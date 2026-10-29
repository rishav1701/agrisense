"""Search and extract native-grid Sentinel-1 RTC COGs from Planetary Computer.

The acquisition preserves provider pixel values. It does not infer dB units,
select a multi-date orbit strategy, resample, despeckle, or estimate moisture.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from src.data.copernicus_stac import search_sentinel1_rtc
from src.data.sentinel_stac_assets import (
    SENTINEL_ATTRIBUTION,
    _full_coverage_pixel_window,
    _validate_item_id,
    validate_aoi_geometry,
)

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
SIGN_URL = "https://planetarycomputer.microsoft.com/api/sas/v1/sign"
SENTINEL1_COLLECTION = "sentinel-1-rtc"
ASSET_KEYS = {"VV": "vv", "VH": "vh"}
COPERNICUS_TERMS = (
    "https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice"
)
DATASET_LICENSE = "https://creativecommons.org/licenses/by/4.0/"


def _acquisition_time(item: dict[str, Any]) -> datetime:
    """Get a STAC item's UTC acquisition time."""
    try:
        timestamp = str(item["properties"]["datetime"]).replace("Z", "+00:00")
        value = datetime.fromisoformat(timestamp)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("STAC item has no valid acquisition datetime") from exc
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError("STAC acquisition datetime must specify UTC")
    return value.astimezone(timezone.utc)


def search_sentinel1_rtc_items(
    *,
    aoi_geometry: dict[str, Any],
    start_date: str,
    end_date: str,
    max_items: int = 500,
) -> list[dict[str, Any]]:
    """Search public Sentinel-1 RTC metadata for a polygon and date interval."""
    validate_aoi_geometry(aoi_geometry)
    return search_sentinel1_rtc(
        aoi_geometry=aoi_geometry,
        start_date=start_date,
        end_date=end_date,
        max_items=max_items,
        stac_url=STAC_URL,
    )


def _sign_asset_href(href: str, *, timeout_seconds: float = 20) -> str:
    """Request a temporary anonymous read URL from Planetary Computer."""
    if urlsplit(href).scheme != "https":
        raise ValueError("Sentinel-1 RTC asset must use HTTPS")
    request = Request(
        f"{SIGN_URL}?{urlencode({'href': href})}",
        headers={"Accept": "application/json"},
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        document = json.loads(response.read())
    signed_href = document.get("href")
    if (
        not isinstance(signed_href, str)
        or urlsplit(signed_href).scheme != "https"
        or not urlsplit(signed_href).netloc
    ):
        raise ValueError("Planetary Computer returned an invalid signed asset URL")
    return signed_href


def _select_latest(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Select the latest matching scene for a single-date technical sample."""
    if not items:
        raise ValueError("No Sentinel-1 RTC items intersect the AOI and dates")
    return max(items, key=_acquisition_time)


def extract_sentinel1_rtc_assets(
    *, item: dict[str, Any], aoi_geometry: dict[str, Any], output_dir: Path
) -> dict[str, Any]:
    """Read and save VV and VH COG windows masked to an explicit AOI polygon."""
    try:
        import rasterio
    except ImportError as exc:
        raise ImportError("Sentinel extraction requires rasterio") from exc

    from rasterio.features import bounds, geometry_mask
    from rasterio.warp import transform_geom
    from rasterio.windows import Window, from_bounds

    validate_aoi_geometry(aoi_geometry)
    item_id = _validate_item_id(item.get("id"))
    assets = item.get("assets")
    if not isinstance(assets, dict):
        raise ValueError("STAC item must include assets")
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted: dict[str, Any] = {}
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tiff",
    ):
        for polarization, asset_key in ASSET_KEYS.items():
            asset = assets.get(asset_key)
            href = asset.get("href") if isinstance(asset, dict) else None
            if (
                not isinstance(href, str)
                or urlsplit(href).scheme != "https"
                or not urlsplit(href).netloc
            ):
                raise ValueError(f"Sentinel-1 item has no HTTPS {polarization} asset")
            signed_href = _sign_asset_href(href)
            with rasterio.open(signed_href) as source:
                projected_geometry = transform_geom(
                    "EPSG:4326", source.crs, aoi_geometry, precision=8
                )
                requested = from_bounds(
                    *bounds(projected_geometry), transform=source.transform
                )
                window = Window(
                    *_full_coverage_pixel_window(
                        requested,
                        raster_width=source.width,
                        raster_height=source.height,
                        asset_name=polarization,
                    )
                )
                if window.width <= 0 or window.height <= 0:
                    raise RuntimeError(f"{polarization} asset does not overlap the AOI")
                values = source.read(1, window=window)
                transform = source.window_transform(window)
                inside_aoi = geometry_mask(
                    [projected_geometry],
                    out_shape=values.shape,
                    transform=transform,
                    invert=True,
                    all_touched=False,
                )
                valid_mask = inside_aoi & (source.read_masks(1, window=window) > 0)
                profile = source.profile.copy()
                profile.update(
                    driver="GTiff",
                    width=values.shape[1],
                    height=values.shape[0],
                    transform=transform,
                    compress="deflate",
                    tiled=True,
                )
                output_path = output_dir / f"{item_id}_{polarization}.tif"
                with rasterio.open(output_path, "w", **profile) as destination:
                    destination.write(values, 1)
                    destination.write_mask(valid_mask.astype("uint8") * 255)
                    destination.scales = source.scales
                    destination.offsets = source.offsets
                    destination.update_tags(
                        source_item_id=item_id,
                        source_asset_href=href,
                        polarization=polarization,
                        radiometry="gamma0",
                        value_scale="linear power",
                        aoi_geometry_crs="EPSG:4326",
                        extraction="AOI pixel-center mask; native source grid",
                    )
                extracted[polarization] = {
                    "path": output_path.name,
                    "source_asset": href,
                    "crs": source.crs.to_string(),
                    "shape": [int(values.shape[0]), int(values.shape[1])],
                    "resolution_native_units": [
                        abs(float(source.transform.a)),
                        abs(float(source.transform.e)),
                    ],
                    "scale": list(source.scales),
                    "offset": list(source.offsets),
                    "valid_pixels_inside_aoi": int(valid_mask.sum()),
                    "nodata": source.nodata,
                }

    properties = item.get("properties", {})
    manifest = {
        "item_id": item_id,
        "collection": item.get("collection", SENTINEL1_COLLECTION),
        "acquired_utc": properties.get("datetime"),
        "aoi_geometry": aoi_geometry,
        "aoi_crs": "EPSG:4326",
        "relative_orbit": properties.get("sat:relative_orbit"),
        "orbit_state": properties.get("sat:orbit_state"),
        "instrument_mode": properties.get("sar:instrument_mode"),
        "radiometry": "gamma0",
        "value_scale": "linear power",
        "value_semantics_source": "https://github.com/microsoft/ai4g-flood/blob/main/README.md",
        "assets": extracted,
        "provider": "Microsoft Planetary Computer Sentinel-1 RTC",
        "source_terms": COPERNICUS_TERMS,
        "dataset_license": DATASET_LICENSE,
        "attribution": (
            f"{SENTINEL_ATTRIBUTION} {_acquisition_time(item).year}; "
            "processed by Microsoft Planetary Computer"
        ),
        "limitations": [
            "Technical acquisition only; AOI and field-label suitability are not validated.",
            "Microsoft's AI4G Sentinel-1 RTC instructions identify the product as gamma0 radiometry in power scale; the STAC assets themselves omit a unit field.",
            "Raw gamma0 power pixels are preserved without conversion; no dB features are generated by this extractor.",
            "No temporal orbit matching, speckle filtering, resampling, compositing, or scientific inference is performed.",
        ],
    }
    (output_dir / f"{item_id}_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def acquire_sentinel1_rtc_aoi(
    *, aoi_geometry: dict[str, Any], start_date: str, end_date: str, output_dir: Path
) -> dict[str, Any]:
    """Search for and extract the latest matching Sentinel-1 RTC scene."""
    item = _select_latest(
        search_sentinel1_rtc_items(
            aoi_geometry=aoi_geometry, start_date=start_date, end_date=end_date
        )
    )
    return extract_sentinel1_rtc_assets(
        item=item, aoi_geometry=aoi_geometry, output_dir=output_dir
    )
