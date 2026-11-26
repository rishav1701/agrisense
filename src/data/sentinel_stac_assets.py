"""Extract bounded Sentinel-2 asset windows from public STAC items.

The helper reads cloud-optimized GeoTIFF ranges and writes only the requested
AOI window. It preserves each source band's native grid and values; it does not
resample, calculate indices, or establish that an AOI is scientifically valid.
"""

from __future__ import annotations

import json
import math
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from src.contracts.schemas import SchemaValidationError, StudyAreaQuery
from src.data.copernicus_stac import search_sentinel2_l2a

STAC_URL = "https://earth-search.aws.element84.com/v1"
SENTINEL_ATTRIBUTION = "Contains modified Copernicus Sentinel data"
SENTINEL_TERMS_URL = (
    "https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice"
)
ASSET_KEYS = {"B02": "blue", "B04": "red", "B08": "nir", "SCL": "scl"}


def _full_coverage_pixel_window(
    requested: Any,
    *,
    raster_width: int,
    raster_height: int,
    asset_name: str,
) -> tuple[int, int, int, int]:
    """Round an AOI window outward and reject incomplete source coverage."""
    try:
        col_start = math.floor(float(requested.col_off))
        row_start = math.floor(float(requested.row_off))
        col_stop = math.ceil(float(requested.col_off + requested.width))
        row_stop = math.ceil(float(requested.row_off + requested.height))
    except (AttributeError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{asset_name} AOI pixel window is invalid") from exc
    if col_stop <= col_start or row_stop <= row_start:
        raise ValueError(f"{asset_name} AOI pixel window is empty")
    if (
        col_start < 0
        or row_start < 0
        or col_stop > raster_width
        or row_stop > raster_height
    ):
        raise RuntimeError(f"{asset_name} asset does not fully cover the requested AOI")
    return col_start, row_start, col_stop - col_start, row_stop - row_start


def _clipped_pixel_window(
    requested: Any,
    *,
    raster_width: int,
    raster_height: int,
    asset_name: str,
) -> tuple[tuple[int, int, int, int], bool]:
    """Clip an AOI window to one granule and report whether it covers all bounds."""
    try:
        col_start = math.floor(float(requested.col_off))
        row_start = math.floor(float(requested.row_off))
        col_stop = math.ceil(float(requested.col_off + requested.width))
        row_stop = math.ceil(float(requested.row_off + requested.height))
    except (AttributeError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{asset_name} AOI pixel window is invalid") from exc
    if col_stop <= col_start or row_stop <= row_start:
        raise ValueError(f"{asset_name} AOI pixel window is empty")
    clipped_start = max(col_start, 0)
    clipped_row_start = max(row_start, 0)
    clipped_stop = min(col_stop, raster_width)
    clipped_row_stop = min(row_stop, raster_height)
    if clipped_stop <= clipped_start or clipped_row_stop <= clipped_row_start:
        raise RuntimeError(f"{asset_name} granule does not overlap the AOI")
    fully_covered = (
        col_start >= 0
        and row_start >= 0
        and col_stop <= raster_width
        and row_stop <= raster_height
    )
    return (
        (
            clipped_start,
            clipped_row_start,
            clipped_stop - clipped_start,
            clipped_row_stop - clipped_row_start,
        ),
        fully_covered,
    )


def _validate_item_id(item_id: Any) -> str:
    """Require an item identifier safe for use in output filenames."""
    if (
        not isinstance(item_id, str)
        or not item_id.strip()
        or Path(item_id).name != item_id
        or any(ord(character) < 32 for character in item_id)
    ):
        raise ValueError("STAC item id is invalid for output filenames")
    return item_id


def validate_aoi_geometry(geometry: dict[str, Any]) -> None:
    """Validate an AOI polygon using the project's CON-01 GeoJSON rules.

    Args:
        geometry: GeoJSON Polygon or MultiPolygon in longitude/latitude.

    Raises:
        ValueError: If the geometry is invalid or outside WGS84 longitude/latitude.
    """
    try:
        StudyAreaQuery(
            query_id="sentinel-asset-extraction",
            aoi_geometry=geometry,
            start_date="2000-01-01",
            end_date="2000-01-02",
        )
    except SchemaValidationError as exc:
        raise ValueError(f"Invalid AOI geometry: {exc}") from exc


def load_aoi_geometry(path: Path) -> dict[str, Any]:
    """Read one GeoJSON geometry, Feature, or single-feature collection.

    Args:
        path: GeoJSON file path.

    Returns:
        The polygon geometry in longitude/latitude.

    Raises:
        ValueError: If the file is malformed or does not contain exactly one polygon.
    """
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read AOI GeoJSON: {exc}") from exc
    if isinstance(document, dict) and document.get("type") == "FeatureCollection":
        features = document.get("features")
        if not isinstance(features, list) or len(features) != 1:
            raise ValueError("AOI FeatureCollection must contain exactly one feature")
        document = features[0]
    if isinstance(document, dict) and document.get("type") == "Feature":
        geometry = document.get("geometry")
    else:
        geometry = document
    if not isinstance(geometry, dict):
        raise ValueError("AOI GeoJSON must contain a single geometry or Feature")
    validate_aoi_geometry(geometry)
    return geometry


def _select_scene(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Choose the least cloudy scene, breaking ties by newest acquisition."""
    if not items:
        raise ValueError("No Sentinel-2 L2A scenes intersect the AOI and dates")

    def rank(item: dict[str, Any]) -> tuple[float, float]:
        properties = item.get("properties", {})
        cloud = properties.get("eo:cloud_cover")
        try:
            cloud_value = float(cloud)
        except (TypeError, ValueError):
            cloud_value = math.inf
        try:
            acquired = datetime.fromisoformat(
                str(properties["datetime"]).replace("Z", "+00:00")
            ).astimezone(timezone.utc)
        except (KeyError, ValueError) as exc:
            raise ValueError(
                "STAC scene has no valid UTC acquisition datetime"
            ) from exc
        return cloud_value, -acquired.timestamp()

    return min(items, key=rank)


def select_sentinel2_granules_by_tile(
    items: list[dict[str, Any]], *, acquisition_date: str
) -> dict[str, dict[str, Any]]:
    """Select the least-cloudy item for each MGRS tile on one UTC date.

    Args:
        items: STAC items returned for the target AOI and single-day interval.
        acquisition_date: Required UTC calendar date in ``YYYY-MM-DD`` form.

    Returns:
        A tile-keyed mapping of selected STAC items. Tile products remain
        separate; this function does not assert a common timestamp or grid.

    Raises:
        ValueError: If the date or any item's acquisition date/tile is invalid,
            or no matching items are present.
    """
    try:
        requested_date = date.fromisoformat(acquisition_date)
    except (TypeError, ValueError) as exc:
        raise ValueError("acquisition_date must be a valid ISO date") from exc
    if requested_date.isoformat() != acquisition_date:
        raise ValueError("acquisition_date must use YYYY-MM-DD format")
    if not items:
        raise ValueError("No Sentinel-2 items were found for the requested date")

    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        properties = item.get("properties")
        if not isinstance(properties, dict):
            raise ValueError("Sentinel-2 STAC item has no properties object")
        tile = properties.get("s2:mgrs_tile")
        if not isinstance(tile, str) or not tile.strip():
            # Earth Search's observed Sentinel-2 L2A IDs encode the MGRS tile
            # as the second underscore-delimited field. Keep this fallback
            # strict so unrelated provider ID formats are never guessed.
            item_id = item.get("id")
            match = (
                re.fullmatch(r"S2[AB]_(\d{2}[A-Z]{3})_\d{8}_\d+_L2A", item_id)
                if isinstance(item_id, str)
                else None
            )
            tile = match.group(1) if match else None
        if not isinstance(tile, str) or not tile.strip():
            raise ValueError(
                "Sentinel-2 STAC item has no MGRS tile property or recognized Earth Search ID"
            )
        try:
            acquired = datetime.fromisoformat(
                str(properties["datetime"]).replace("Z", "+00:00")
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                "Sentinel-2 item has no valid acquisition datetime"
            ) from exc
        if acquired.tzinfo is None or acquired.utcoffset() != timezone.utc.utcoffset(
            acquired
        ):
            raise ValueError("Sentinel-2 acquisition datetime must specify UTC")
        if acquired.date() != requested_date:
            raise ValueError("STAC items must match the requested acquisition date")
        grouped.setdefault(tile, []).append(item)
    return {tile: _select_scene(group) for tile, group in sorted(grouped.items())}


def search_and_select_sentinel2(
    *,
    aoi_geometry: dict[str, Any],
    start_date: str,
    end_date: str,
    max_cloud_cover_percent: float = 30,
    max_items: int = 500,
) -> dict[str, Any]:
    """Find and select a public Sentinel-2 L2A item for an explicit AOI.

    Args:
        aoi_geometry: Polygon or MultiPolygon in WGS84 longitude/latitude.
        start_date: Inclusive ``YYYY-MM-DD`` date.
        end_date: Exclusive ``YYYY-MM-DD`` date.
        max_cloud_cover_percent: Scene-level cloud-cover filter.
        max_items: Maximum number of catalog records to inspect.

    Returns:
        The least-cloudy matching STAC Item, preferring the latest date on ties.
    """
    validate_aoi_geometry(aoi_geometry)
    items = search_sentinel2_l2a(
        aoi_geometry=aoi_geometry,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover_percent=max_cloud_cover_percent,
        max_items=max_items,
        stac_url=STAC_URL,
    )
    return _select_scene(items)


def extract_sentinel2_assets(
    *,
    item: dict[str, Any],
    aoi_geometry: dict[str, Any],
    output_dir: Path,
    allow_partial_coverage: bool = False,
) -> dict[str, Any]:
    """Read and save B02, B04, B08, and SCL clipped to one AOI polygon.

    Each output retains the source band's native CRS, pixel size, integer
    values, scale/offset metadata, and resolution. The 20 m SCL layer is never
    resampled onto the 10 m reflectance grids.

    Args:
        item: STAC Item with Earth Search COG assets.
        aoi_geometry: AOI polygon in WGS84 longitude/latitude.
        output_dir: Directory for four GeoTIFF assets and a provenance manifest.
        allow_partial_coverage: Permit this granule's clipped output to cover
            only part of the AOI. The manifest records per-band coverage; this
            option does not mosaic neighboring granules or establish total AOI
            coverage.

    Returns:
        A provenance manifest describing the extracted source windows.

    Raises:
        ImportError: If optional rasterio dependency is missing.
        ValueError: If item assets are missing or do not safely resolve to HTTPS.
        RuntimeError: If a source asset does not overlap the requested AOI.
    """
    try:
        import rasterio
        from rasterio.features import geometry_mask
        from rasterio.warp import transform_geom
        from rasterio.windows import Window, from_bounds
    except ImportError as exc:
        raise ImportError(
            "Sentinel asset extraction requires rasterio; install requirements-science.txt"
        ) from exc

    validate_aoi_geometry(aoi_geometry)
    assets = item.get("assets")
    if not isinstance(assets, dict):
        raise ValueError("STAC item is missing its assets object")
    output_dir.mkdir(parents=True, exist_ok=True)
    item_id = _validate_item_id(item.get("id"))

    extracted: dict[str, Any] = {}
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
    ):
        for band_name, asset_key in ASSET_KEYS.items():
            asset = assets.get(asset_key)
            href = asset.get("href") if isinstance(asset, dict) else None
            if (
                not isinstance(href, str)
                or urlsplit(href).scheme != "https"
                or not urlsplit(href).netloc
            ):
                raise ValueError(f"STAC item has no HTTPS {band_name} asset")
            with rasterio.open(href) as source:
                raster_metadata = asset.get("raster:bands", [])
                band_metadata = (
                    raster_metadata[0]
                    if isinstance(raster_metadata, list)
                    and raster_metadata
                    and isinstance(raster_metadata[0], dict)
                    else {}
                )
                source_scales = source.scales
                source_offsets = source.offsets
                if band_metadata.get("scale") is not None:
                    source_scales = (float(band_metadata["scale"]),)
                if band_metadata.get("offset") is not None:
                    source_offsets = (float(band_metadata["offset"]),)
                if any(
                    not math.isfinite(float(value))
                    for value in (*source_scales, *source_offsets)
                ):
                    raise ValueError(
                        f"{band_name} asset has invalid scale/offset metadata"
                    )
                projected_geometry = transform_geom(
                    "EPSG:4326", source.crs, aoi_geometry, precision=8
                )
                bounds = rasterio.features.bounds(projected_geometry)
                requested = from_bounds(*bounds, transform=source.transform)
                if allow_partial_coverage:
                    window_values, covers_full_aoi = _clipped_pixel_window(
                        requested,
                        raster_width=source.width,
                        raster_height=source.height,
                        asset_name=band_name,
                    )
                else:
                    window_values = _full_coverage_pixel_window(
                        requested,
                        raster_width=source.width,
                        raster_height=source.height,
                        asset_name=band_name,
                    )
                    covers_full_aoi = True
                window = Window(*window_values)
                if window.width <= 0 or window.height <= 0:
                    raise RuntimeError(f"{band_name} asset does not overlap the AOI")

                values = source.read(1, window=window)
                transform = source.window_transform(window)
                inside_aoi = geometry_mask(
                    [projected_geometry],
                    out_shape=values.shape,
                    transform=transform,
                    invert=True,
                    all_touched=False,
                )
                source_mask = source.read_masks(1, window=window) > 0
                valid_mask = inside_aoi & source_mask
                profile = source.profile.copy()
                profile.update(
                    driver="GTiff",
                    width=values.shape[1],
                    height=values.shape[0],
                    transform=transform,
                    compress="deflate",
                    tiled=True,
                )
                output_path = output_dir / f"{item_id}_{band_name}.tif"
                with rasterio.open(output_path, "w", **profile) as destination:
                    destination.write(values, 1)
                    destination.write_mask(valid_mask.astype("uint8") * 255)
                    destination.scales = source_scales
                    destination.offsets = source_offsets
                    destination.update_tags(
                        source_item_id=item_id,
                        source_asset_href=href,
                        source_asset_key=asset_key,
                        aoi_geometry_crs="EPSG:4326",
                        extraction="AOI pixel-center mask; native source grid",
                    )
                extracted[band_name] = {
                    "path": output_path.name,
                    "source_asset": href,
                    "crs": source.crs.to_string(),
                    "shape": [int(values.shape[0]), int(values.shape[1])],
                    "resolution_native_units": [
                        abs(float(source.transform.a)),
                        abs(float(source.transform.e)),
                    ],
                    "scale": list(source_scales),
                    "offset": list(source_offsets),
                    "valid_pixels_inside_aoi": int(valid_mask.sum()),
                    "granule_covers_full_aoi_bounds": covers_full_aoi,
                    "nodata": source.nodata,
                }

    properties = item.get("properties", {})
    acquired_utc = properties.get("datetime")
    if not isinstance(acquired_utc, str):
        raise ValueError("STAC item has no acquisition datetime for attribution")
    try:
        acquired_year = datetime.fromisoformat(acquired_utc.replace("Z", "+00:00")).year
    except ValueError as exc:
        raise ValueError("STAC acquisition datetime is invalid") from exc
    manifest = {
        "item_id": item_id,
        "collection": item.get("collection", "sentinel-2-l2a"),
        "acquired_utc": acquired_utc,
        "scene_cloud_cover_percent": properties.get("eo:cloud_cover"),
        "aoi_geometry": aoi_geometry,
        "aoi_crs": "EPSG:4326",
        "assets": extracted,
        "granule_covers_full_aoi_bounds": all(
            item["granule_covers_full_aoi_bounds"] for item in extracted.values()
        ),
        "provider": "Element 84 Earth Search on AWS Open Data",
        "source_terms": SENTINEL_TERMS_URL,
        "attribution": f"{SENTINEL_ATTRIBUTION} {acquired_year}",
        "limitations": [
            "This is a technical raster extraction; AOI and field-label suitability are not validated.",
            "Scene cloud cover is a product-level statistic, not an AOI pixel-quality assessment.",
            "B02/B04/B08 retain their source 10 m grid; SCL retains its source 20 m grid.",
            "No resampling, atmospheric correction, index calculation, or scientific inference is performed.",
        ],
    }
    if not manifest["granule_covers_full_aoi_bounds"]:
        manifest["limitations"].append(
            "This granule covers only part of the AOI; neighboring granules and a coverage assessment are required before area-wide analysis."
        )
    (output_dir / f"{item_id}_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def acquire_sentinel2_aoi(
    *,
    aoi_geometry: dict[str, Any],
    start_date: str,
    end_date: str,
    output_dir: Path,
    max_cloud_cover_percent: float = 30,
) -> dict[str, Any]:
    """Search Earth Search and extract one least-cloudy Sentinel-2 scene."""
    item = search_and_select_sentinel2(
        aoi_geometry=aoi_geometry,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover_percent=max_cloud_cover_percent,
    )
    return extract_sentinel2_assets(
        item=item, aoi_geometry=aoi_geometry, output_dir=output_dir
    )


def acquire_sentinel2_aoi_date_tiles(
    *,
    aoi_geometry: dict[str, Any],
    acquisition_date: str,
    max_cloud_cover_percent: float,
    output_dir: Path,
) -> dict[str, Any]:
    """Extract separate native-grid Sentinel-2 granules for one UTC date.

    Every intersecting MGRS tile is selected independently and clipped to the
    AOI. Outputs are intentionally not mosaicked or reprojected. The resulting
    manifest preserves tile-specific acquisition times and states that total
    AOI coverage has not been assessed.

    Args:
        aoi_geometry: Polygon or MultiPolygon in longitude/latitude.
        acquisition_date: UTC date in ``YYYY-MM-DD`` format.
        max_cloud_cover_percent: Explicit product-level catalog filter.
        output_dir: Directory for per-tile rasters and the summary manifest.

    Returns:
        A summary manifest linking independently extracted tile products.

    Raises:
        ValueError: If no matching granules are found or the date is invalid.
        ImportError: If Rasterio is not installed.
        RuntimeError: If a selected tile does not overlap the AOI.
    """
    try:
        parsed_date = date.fromisoformat(acquisition_date)
    except (TypeError, ValueError) as exc:
        raise ValueError("acquisition_date must be a valid ISO date") from exc
    if parsed_date.isoformat() != acquisition_date:
        raise ValueError("acquisition_date must use YYYY-MM-DD format")
    end_date = (parsed_date + timedelta(days=1)).isoformat()
    items = search_sentinel2_l2a(
        aoi_geometry=aoi_geometry,
        start_date=acquisition_date,
        end_date=end_date,
        max_cloud_cover_percent=max_cloud_cover_percent,
        max_items=500,
        stac_url=STAC_URL,
    )
    granules = select_sentinel2_granules_by_tile(
        items, acquisition_date=acquisition_date
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    tile_manifests: dict[str, Any] = {}
    for tile, item in granules.items():
        tile_manifests[tile] = extract_sentinel2_assets(
            item=item,
            aoi_geometry=aoi_geometry,
            output_dir=output_dir / tile,
            allow_partial_coverage=True,
        )
    manifest = {
        "acquisition_date_requested": acquisition_date,
        "granules": tile_manifests,
        "aoi_coverage_state": "not_assessed",
        "mosaic_created": False,
        "limitations": [
            "Granules are retained separately on their native grids; no reprojection, resampling, or mosaic is performed.",
            "Per-granule masks do not establish complete AOI coverage when combined.",
            "Tile acquisition timestamps are retained individually and are not assumed simultaneous.",
            "Scene cloud percentages do not replace pixel-level quality review.",
        ],
    }
    (output_dir / f"sentinel2_{acquisition_date}_granules_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest
