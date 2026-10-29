"""Retrieve and summarize TGRAC crop points and candidate project polygons.

All retrieved ArcGIS JSON is retained under the output directory. Derived
summaries are descriptive intersections only; layer 18 is not assumed to be an
authoritative irrigation-command boundary.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

AGRI_ROOT = (
    "https://tgrac.telangana.gov.in/arcgis/rest/services/Agri2/"
    "Agriculture2_CropAnalysis_Layers/MapServer"
)
ICAD_ROOT = (
    "https://tgrac.telangana.gov.in/arcgis/rest/services/"
    "IandCAD_Folder/I_and_CAD/MapServer"
)
LAYERS = (
    ("february_2023", AGRI_ROOT, 10, "ground_truth"),
    ("march_2023", AGRI_ROOT, 11, "ground_truth"),
    ("april_2023", AGRI_ROOT, 12, "ground_truth"),
    ("layer18_candidate", AGRI_ROOT, 18, "candidate_only"),
    ("icad_layer9", ICAD_ROOT, 9, "candidate_only"),
    ("icad_layer10", ICAD_ROOT, 10, "candidate_only"),
)
MONTH_LAYERS = {"february_2023", "march_2023", "april_2023"}
MISSING = "[MISSING]"


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def request_json(url: str, params: dict[str, Any], retries: int = 3) -> dict[str, Any]:
    """Fetch ArcGIS JSON with bounded retries and useful HTTP errors."""
    query = urlencode(params)
    if len(query) > 5000:
        request = Request(
            url,
            data=query.encode("utf-8"),
            headers={
                "User-Agent": "AgriSense-read-only-audit/1.0",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
    else:
        request = Request(
            f"{url}?{query}",
            headers={"User-Agent": "AgriSense-read-only-audit/1.0"},
        )
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(request, timeout=45) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("ArcGIS response was not a JSON object")
            if "error" in payload:
                raise RuntimeError(json.dumps(payload["error"], ensure_ascii=False))
            return payload
        except (
            HTTPError,
            URLError,
            TimeoutError,
            json.JSONDecodeError,
            ValueError,
            RuntimeError,
        ) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(
        f"Request failed after {retries} attempts: {url}: {last_error}"
    ) from last_error


def fetch_layer(
    root: str,
    layer_id: int,
    raw_dir: Path,
    page_size: int | None = None,
    query_params: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    """Fetch metadata and all features for one ArcGIS layer using pagination."""
    layer_url = f"{root}/{layer_id}"
    meta = request_json(layer_url, {"f": "pjson"})
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"layer_{layer_id}_metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    oid_field = next(
        (
            field["name"]
            for field in meta.get("fields", [])
            if field.get("type") == "esriFieldTypeOID"
        ),
        None,
    )
    total_count = request_json(
        f"{layer_url}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    ).get("count")
    count_params = {
        "where": "1=1",
        "returnCountOnly": "true",
        "f": "json",
        **(query_params or {}),
    }
    expected = request_json(f"{layer_url}/query", count_params).get("count")
    limit = int(meta.get("maxRecordCount") or 1000)
    size = max(1, min(page_size or 100, limit))
    all_features: list[dict[str, Any]] = []
    page_number = 0
    id_params = {
        "where": "1=1",
        "returnIdsOnly": "true",
        "returnGeometry": "false",
        "f": "json",
        **(query_params or {}),
    }
    id_response = request_json(f"{layer_url}/query", id_params)
    object_ids = id_response.get("objectIds")
    if object_ids is None:
        if expected == 0:
            object_ids = []
        else:
            raise RuntimeError(
                f"ArcGIS omitted object IDs for layer {layer_id}; expected count={expected}, "
                f"response keys={sorted(id_response)}"
            )
    oid_field = id_response.get("objectIdFieldName") or oid_field
    transfer_limited = False
    for start in range(0, len(object_ids), size):
        batch_ids = object_ids[start : start + size]
        page = request_json(
            f"{layer_url}/query",
            {
                "objectIds": ",".join(str(value) for value in batch_ids),
                "outFields": "*",
                "returnGeometry": "true",
                "f": "json",
            },
        )
        features = page.get("features", [])
        if not isinstance(features, list):
            raise RuntimeError(f"Invalid features response for layer {layer_id}")
        (raw_dir / f"layer_{layer_id}_page_{page_number:05d}.json").write_text(
            json.dumps(page, ensure_ascii=False), encoding="utf-8"
        )
        all_features.extend(features)
        transfer_limited = transfer_limited or bool(page.get("exceededTransferLimit"))
        page_number += 1
        if len(features) < len(batch_ids):
            raise RuntimeError(
                f"Layer {layer_id} returned {len(features)} features for "
                f"{len(batch_ids)} requested object IDs in batch {page_number - 1}"
            )
    ids = (
        [feature.get("attributes", {}).get(oid_field) for feature in all_features]
        if oid_field
        else []
    )
    valid_ids = [value for value in ids if value is not None]
    duplicate_count = len(valid_ids) - len(set(valid_ids))
    stats = {
        "expected_count": expected,
        "service_total_count": total_count,
        "object_ids_returned": len(object_ids),
        "records_received": len(all_features),
        "unique_object_ids": len(set(valid_ids)) if valid_ids else None,
        "duplicate_object_ids": duplicate_count,
        "missing_geometry": sum(
            feature.get("geometry") is None for feature in all_features
        ),
        "malformed_geometry": sum(
            feature.get("geometry") is not None
            and not geometry_is_well_formed(
                feature.get("geometry"), meta.get("geometryType")
            )
            for feature in all_features
        ),
        "page_count": page_number,
        "exceeded_transfer_limit": transfer_limited,
        "object_id_field": oid_field,
        "retrieved_at_utc": utc_now(),
    }
    return meta, all_features, stats


def field_value(feature: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    """Get an attribute using case-insensitive field aliases."""
    attrs = feature.get("attributes") or {}
    by_lower = {str(key).lower(): value for key, value in attrs.items()}
    for name in aliases:
        if name.lower() in by_lower:
            value = by_lower[name.lower()]
            return MISSING if value is None or value == "" else value
    return MISSING


def _ring_area(ring: list[list[float]]) -> float:
    """Return signed planar ring area."""
    return (
        sum(
            ring[index][0] * ring[(index + 1) % len(ring)][1]
            - ring[(index + 1) % len(ring)][0] * ring[index][1]
            for index in range(len(ring))
        )
        / 2
    )


def geometry_is_well_formed(
    geometry: dict[str, Any] | None, geometry_type: str | None
) -> bool:
    """Check whether point or polygon coordinates have a usable basic structure."""
    if not isinstance(geometry, dict):
        return False
    if geometry_type == "esriGeometryPoint":
        try:
            return math.isfinite(float(geometry["x"])) and math.isfinite(
                float(geometry["y"])
            )
        except (KeyError, TypeError, ValueError):
            return False
    if geometry_type == "esriGeometryPolygon":
        rings = geometry.get("rings")
        if not isinstance(rings, list) or not rings:
            return False
        for ring in rings:
            if not isinstance(ring, list) or len(ring) < 4:
                return False
            try:
                coords = [(float(position[0]), float(position[1])) for position in ring]
            except (IndexError, TypeError, ValueError):
                return False
            if not all(math.isfinite(x) and math.isfinite(y) for x, y in coords):
                return False
            if coords[0] != coords[-1]:
                return False
        return True
    return False


def polygon_bounds(
    polygon: dict[str, Any] | None,
) -> tuple[float, float, float, float] | None:
    """Return an Esri polygon's coordinate bounds for a safe overlap prefilter."""
    coordinates = []
    for ring in (polygon or {}).get("rings", []):
        for position in ring:
            try:
                x, y = float(position[0]), float(position[1])
            except (IndexError, TypeError, ValueError):
                continue
            if math.isfinite(x) and math.isfinite(y):
                coordinates.append((x, y))
    if not coordinates:
        return None
    xs, ys = zip(*coordinates)
    return min(xs), min(ys), max(xs), max(ys)


def _on_segment(point: tuple[float, float], a: list[float], b: list[float]) -> bool:
    """Return whether a point lies on a segment within numeric tolerance."""
    x, y = point
    cross = (x - a[0]) * (b[1] - a[1]) - (y - a[1]) * (b[0] - a[0])
    if abs(cross) > 1e-10:
        return False
    return (
        min(a[0], b[0]) - 1e-10 <= x <= max(a[0], b[0]) + 1e-10
        and min(a[1], b[1]) - 1e-10 <= y <= max(a[1], b[1]) + 1e-10
    )


def _ring_relation(point: tuple[float, float], ring: list[list[float]]) -> int:
    """Return 1 inside, 0 outside, or -1 on a ring boundary."""
    x, y = point
    inside = False
    for index, a in enumerate(ring):
        b = ring[(index + 1) % len(ring)]
        if _on_segment(point, a, b):
            return -1
        if (a[1] > y) != (b[1] > y):
            crossing_x = (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]
            if x < crossing_x:
                inside = not inside
    return 1 if inside else 0


def point_in_arcgis_polygon(
    point_geometry: dict[str, Any] | None, polygon: dict[str, Any] | None
) -> bool:
    """Test an ArcGIS point against an Esri rings polygon, including holes."""
    if (
        not point_geometry
        or not polygon
        or "x" not in point_geometry
        or "y" not in point_geometry
    ):
        return False
    point = (float(point_geometry["x"]), float(point_geometry["y"]))
    rings = polygon.get("rings") or []
    if not rings:
        return False
    outer_rings = [ring for ring in rings if len(ring) >= 4 and _ring_area(ring) < 0]
    hole_rings = [ring for ring in rings if len(ring) >= 4 and _ring_area(ring) > 0]
    # If orientation is absent/nonstandard, fall back to even-odd ring parity.
    if not outer_rings and hole_rings:
        return sum(_ring_relation(point, ring) != 0 for ring in rings) % 2 == 1
    outer = any(_ring_relation(point, ring) != 0 for ring in outer_rings)
    in_hole = any(_ring_relation(point, ring) == 1 for ring in hole_rings)
    return outer and not in_hole


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write rows as UTF-8 CSV, including headers for empty result sets."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = (
        list(rows[0])
        if rows
        else (
            ["source", "error", "retrieved_at_utc"]
            if path.name == "failures.csv"
            else []
        )
    )
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        if fieldnames:
            writer.writeheader()
            writer.writerows(rows)


def feature_collection(
    features: list[dict[str, Any]], spatial_reference: Any
) -> dict[str, Any]:
    """Build a GeoJSON-like collection while preserving ArcGIS source CRS metadata."""
    return {
        "type": "FeatureCollection",
        "source_spatial_reference": spatial_reference,
        "features": [
            {
                "type": "Feature",
                "geometry": feature.get("geometry"),
                "properties": feature.get("attributes") or {},
            }
            for feature in features
        ],
    }


def deduplicate_features(
    features: list[dict[str, Any]], object_id_field: str | None
) -> list[dict[str, Any]]:
    """Keep the first record per source object ID for derived summaries."""
    if not object_id_field:
        return list(features)
    seen = set()
    unique = []
    for feature in features:
        object_id = (feature.get("attributes") or {}).get(object_id_field)
        if object_id is None or object_id not in seen:
            unique.append(feature)
            if object_id is not None:
                seen.add(object_id)
    return unique


def crop_field(features: list[dict[str, Any]]) -> str | None:
    """Find the crop label field present in a feature list."""
    aliases = ("crop", "Crop", "CROP", "purecrop_n", "purecrop_1")
    for feature in features:
        attrs = feature.get("attributes") or {}
        match = next(
            (key for key in attrs if key.lower() in {a.lower() for a in aliases}), None
        )
        if match:
            return match
    return None


def build_summaries(
    datasets: dict[str, tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    """Create feature, missing-value, crop, district, mandal and overlap summaries."""
    feature_rows = []
    missing_rows = []
    crop_rows = []
    admin_rows = []
    point_sets = {}
    point_wkids = {}
    point_denominators: dict[str, int] = {}
    for name, (meta, features, stats) in datasets.items():
        sr = meta.get("extent", {}).get("spatialReference") or meta.get(
            "sourceSpatialReference"
        )
        wkid = (sr or {}).get("latestWkid") or (sr or {}).get("wkid")
        feature_rows.append(
            {
                "dataset": name,
                "layer_id": meta.get("id"),
                "layer_name": meta.get("name"),
                "geometry_type": meta.get("geometryType"),
                "wkid": wkid,
                **stats,
            }
        )
        keys = sorted(
            {key for feature in features for key in (feature.get("attributes") or {})}
        )
        for key in keys:
            missing = sum(
                (feature.get("attributes") or {}).get(key) in (None, "")
                for feature in features
            )
            missing_rows.append(
                {
                    "dataset": name,
                    "field": key,
                    "missing_count": missing,
                    "record_count": len(features),
                }
            )
        if name in MONTH_LAYERS:
            point_sets[name] = features
            point_wkids[name] = wkid
            point_denominators[name] = len(features)
            cfield = crop_field(features)
            if cfield:
                counts = Counter(
                    (
                        MISSING
                        if feature.get("attributes", {}).get(cfield) in (None, "")
                        else str(feature["attributes"][cfield])
                    )
                    for feature in features
                )
                crop_rows.extend(
                    {
                        "month_layer": name,
                        "crop_field": cfield,
                        "crop_label": label,
                        "count": count,
                    }
                    for label, count in sorted(counts.items())
                )
            for dimension, aliases in (
                ("district", ("districtname", "district")),
                ("mandal", ("mandalname", "mandal")),
            ):
                counts = Counter(
                    str(field_value(feature, aliases)) for feature in features
                )
                admin_rows.extend(
                    {
                        "month_layer": name,
                        "admin_level": dimension,
                        "name": label,
                        "count": count,
                    }
                    for label, count in sorted(counts.items())
                )

    overlap_rows = []
    polygons = [
        (name, features)
        for name, (_, features, _) in datasets.items()
        if name.endswith("candidate") or name in {"icad_layer9", "icad_layer10"}
    ]
    for polygon_source, poly_features in polygons:
        for polygon_index, polygon_feature in enumerate(poly_features):
            polygon = polygon_feature.get("geometry")
            bounds = polygon_bounds(polygon)
            label = field_value(
                polygon_feature,
                (
                    "Irrigation_L_3",
                    "Irrigation_L_2",
                    "D_Name",
                    "M_Name",
                    "V_Name",
                    "name",
                ),
            )
            if label == MISSING:
                label = str(
                    polygon_feature.get("attributes", {}).get("OBJECTID", polygon_index)
                )
            for month, points in point_sets.items():
                polygon_meta = datasets[polygon_source][0]
                polygon_sr = (
                    polygon_meta.get("extent", {}).get("spatialReference")
                    or polygon_meta.get("sourceSpatialReference")
                    or {}
                )
                polygon_wkid = polygon_sr.get("latestWkid") or polygon_sr.get("wkid")
                if (
                    not polygon_wkid
                    or not point_wkids[month]
                    or str(polygon_wkid) != str(point_wkids[month])
                ):
                    overlap_rows.append(
                        {
                            "polygon_source": polygon_source,
                            "polygon_label": label,
                            "month_layer": month,
                            "crop_label": MISSING,
                            "point_count": "",
                            "percent_of_month_points": "",
                            "percent_of_month_crop": "",
                            "authoritative_command_verified": False,
                            "overlap_status": f"Skipped: CRS mismatch or unknown ({point_wkids[month]} vs {polygon_wkid})",
                        }
                    )
                    continue
                matched = []
                if bounds:
                    xmin, ymin, xmax, ymax = bounds
                    for point in points:
                        point_geometry = point.get("geometry")
                        if not point_geometry:
                            continue
                        x, y = point_geometry.get("x"), point_geometry.get("y")
                        if (
                            isinstance(x, (int, float))
                            and isinstance(y, (int, float))
                            and xmin <= x <= xmax
                            and ymin <= y <= ymax
                            and point_in_arcgis_polygon(point_geometry, polygon)
                        ):
                            matched.append(point)
                crop_counts = Counter(
                    str(field_value(point, ("crop", "purecrop_n", "purecrop_1")))
                    for point in matched
                )
                if not matched:
                    overlap_rows.append(
                        {
                            "polygon_source": polygon_source,
                            "polygon_label": label,
                            "month_layer": month,
                            "crop_label": MISSING,
                            "point_count": 0,
                            "percent_of_month_points": 0.0,
                            "percent_of_month_crop": "",
                            "authoritative_command_verified": False,
                            "overlap_status": "Computed; descriptive candidate intersection",
                        }
                    )
                for crop, count in sorted(crop_counts.items()):
                    all_crop = sum(
                        str(field_value(point, ("crop", "purecrop_n", "purecrop_1")))
                        == crop
                        for point in points
                    )
                    overlap_rows.append(
                        {
                            "polygon_source": polygon_source,
                            "polygon_label": label,
                            "month_layer": month,
                            "crop_label": crop,
                            "point_count": count,
                            "percent_of_month_points": (
                                round(100 * count / point_denominators[month], 6)
                                if point_denominators[month]
                                else 0.0
                            ),
                            "percent_of_month_crop": (
                                round(100 * count / all_crop, 6) if all_crop else 0.0
                            ),
                            "authoritative_command_verified": False,
                            "overlap_status": "Computed; descriptive candidate intersection",
                        }
                    )
    return {
        "feature_counts.csv": feature_rows,
        "missing_values.csv": missing_rows,
        "crop_counts_by_month.csv": crop_rows,
        "district_mandal_counts.csv": admin_rows,
        "overlap_by_source_project_month_crop.csv": overlap_rows,
    }


def run_audit(outdir: Path, page_size: int | None = None) -> int:
    """Retrieve configured sources and write raw data plus reproducible summaries."""
    outdir.mkdir(parents=True, exist_ok=True)
    datasets = {}
    failures = []
    service_roots = sorted({root for _, root, _, _ in LAYERS})
    for root in service_roots:
        try:
            metadata = request_json(root, {"f": "pjson"})
            path = outdir / "raw" / "services"
            path.mkdir(parents=True, exist_ok=True)
            (
                path / f"{'agri2' if root == AGRI_ROOT else 'icad'}_service.json"
            ).write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as exc:
            failures.append(
                {"source": root, "error": str(exc), "retrieved_at_utc": utc_now()}
            )
            print(f"ERROR service metadata {root}: {exc}", file=sys.stderr)
    layer_catalogues = {}
    for root in service_roots:
        catalogue_file = (
            outdir
            / "raw"
            / "services"
            / f"{'agri2' if root == AGRI_ROOT else 'icad'}_service.json"
        )
        if catalogue_file.exists():
            layer_catalogues[root] = json.loads(
                catalogue_file.read_text(encoding="utf-8")
            )
    for name, root, layer_id, role in LAYERS:
        print(f"Fetching {name} ({root}/{layer_id}; role={role})")
        try:
            published_ids = {
                int(layer.get("id"))
                for layer in layer_catalogues.get(root, {}).get("layers", [])
                if layer.get("id") is not None
            }
            if published_ids and layer_id not in published_ids:
                raise RuntimeError(
                    f"Configured layer {layer_id} is absent from live service metadata; "
                    f"published IDs: {sorted(published_ids)}"
                )
            query_params = None
            if name == "layer18_candidate":
                candidate_meta = request_json(f"{root}/{layer_id}", {"f": "pjson"})
                extent = candidate_meta.get("extent") or {}
                spatial_reference = extent.get("spatialReference") or {}
                wkid = spatial_reference.get("latestWkid") or spatial_reference.get(
                    "wkid"
                )
                if str(wkid) != "4326":
                    raise RuntimeError(
                        f"Candidate layer 18 CRS is {wkid}; point-filtered query currently requires EPSG:4326."
                    )
                xmin, ymin = extent["xmin"], extent["ymin"]
                xmax, ymax = extent["xmax"], extent["ymax"]
                ground_truth = [
                    feature
                    for month in MONTH_LAYERS
                    for feature in datasets.get(month, (None, [], None))[1]
                    if feature.get("geometry")
                    and geometry_is_well_formed(
                        feature.get("geometry"), "esriGeometryPoint"
                    )
                    and xmin <= feature["geometry"]["x"] <= xmax
                    and ymin <= feature["geometry"]["y"] <= ymax
                ]
                if not ground_truth:
                    print(
                        "No ground-truth points fall inside the live layer 18 extent."
                    )
                # Keep each encoded multipoint query short enough for ArcGIS GET.
                # This host returns 404 for long POST queries, although small GET
                # multipoint queries work. Union IDs across batches before storing.
                candidate_parts = []
                for start in range(0, len(ground_truth), 5):
                    point_batch = ground_truth[start : start + 5]
                    query_params = {
                        "geometry": json.dumps(
                            {
                                "points": [
                                    [feature["geometry"]["x"], feature["geometry"]["y"]]
                                    for feature in point_batch
                                ],
                                "spatialReference": {"wkid": 4326},
                            },
                            separators=(",", ":"),
                        ),
                        "geometryType": "esriGeometryMultipoint",
                        "inSR": "4326",
                        "spatialRel": "esriSpatialRelIntersects",
                    }
                    candidate_parts.append(
                        fetch_layer(
                            root,
                            layer_id,
                            outdir / "raw" / name / f"point_filter_{start:05d}",
                            page_size,
                            query_params,
                        )
                    )
                if candidate_parts:
                    meta = candidate_parts[0][0]
                    oid_name = candidate_parts[0][2].get("object_id_field")
                    by_id = {}
                    for _, part_features, part_stats in candidate_parts:
                        for feature in part_features:
                            oid = (feature.get("attributes") or {}).get(oid_name)
                            by_id[
                                (
                                    oid
                                    if oid is not None
                                    else (
                                        len(by_id),
                                        json.dumps(feature, sort_keys=True),
                                    )
                                )
                            ] = feature
                    features = list(by_id.values())
                    stats = dict(candidate_parts[0][2])
                    stats.update(
                        expected_count=None,
                        object_ids_returned=len(features),
                        records_received=len(features),
                        unique_object_ids=len(features) if oid_name else None,
                        duplicate_object_ids=sum(
                            part[2].get("records_received", 0)
                            for part in candidate_parts
                        )
                        - len(features),
                        page_count=sum(
                            part[2].get("page_count", 0) for part in candidate_parts
                        ),
                        point_filter_batches=len(candidate_parts),
                        retrieved_at_utc=utc_now(),
                    )
                else:
                    meta = candidate_meta
                    features = []
                    stats = {
                        "expected_count": 0,
                        "service_total_count": None,
                        "object_ids_returned": 0,
                        "records_received": 0,
                        "unique_object_ids": 0,
                        "duplicate_object_ids": 0,
                        "missing_geometry": 0,
                        "malformed_geometry": 0,
                        "page_count": 0,
                        "exceeded_transfer_limit": False,
                        "object_id_field": None,
                        "point_filter_batches": 0,
                        "retrieved_at_utc": utc_now(),
                    }
            else:
                meta, features, stats = fetch_layer(
                    root, layer_id, outdir / "raw" / name, page_size, None
                )
            (outdir / "raw" / name / f"layer_{layer_id}_features.json").write_text(
                json.dumps({"features": features}, ensure_ascii=False), encoding="utf-8"
            )
            spatial_reference = meta.get("extent", {}).get("spatialReference")
            data_path = outdir / "data"
            data_path.mkdir(parents=True, exist_ok=True)
            (data_path / f"{name}.json").write_text(
                json.dumps(
                    feature_collection(features, spatial_reference), ensure_ascii=False
                ),
                encoding="utf-8",
            )
            summary_features = deduplicate_features(features, stats["object_id_field"])
            stats["records_used_for_summaries"] = len(summary_features)
            datasets[name] = (meta, summary_features, stats)
        except Exception as exc:
            failures.append(
                {
                    "source": f"{root}/{layer_id}",
                    "error": str(exc),
                    "retrieved_at_utc": utc_now(),
                }
            )
            print(f"ERROR layer {name}: {exc}", file=sys.stderr)
    if datasets:
        summaries = build_summaries(datasets)
        for filename, rows in summaries.items():
            write_csv(outdir / "derived" / filename, rows)
        report_lines = [
            "# TGRAC Crop and Candidate-Polygon Audit",
            "",
            f"> Generated: {utc_now()}",
            ">",
            "> This is a descriptive source audit. Layer 18 and I&CAD polygons remain candidate geometries; no authority, licence, label validity, or AOI selection is asserted.",
            "",
            "## Retrieval summary",
            "",
            "| Source | Layer | Name | Records expected | Records received | CRS | Missing geometry | Malformed geometry | Duplicate object IDs |",
            "|---|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
        for row in summaries["feature_counts.csv"]:
            report_lines.append(
                f"| {row['dataset']} | {row['layer_id']} | {row['layer_name']} | "
                f"{row['expected_count']} / {row['service_total_count']} | {row['records_received']} | {row['wkid']} | "
                f"{row['missing_geometry']} | {row['malformed_geometry']} | {row['duplicate_object_ids']} |"
            )
        report_lines.extend(["", "## Crop counts by month", ""])
        crop_rows = summaries["crop_counts_by_month.csv"]
        if crop_rows:
            report_lines.extend(
                ["| Month layer | Crop label | Count |", "|---|---|---:|"]
            )
            report_lines.extend(
                f"| {row['month_layer']} | {row['crop_label']} | {row['count']} |"
                for row in crop_rows
            )
        else:
            report_lines.append(
                "No crop-count rows were available; inspect retrieval failures and source schemas."
            )
        report_lines.extend(
            [
                "",
                "## Overlap",
                "",
                "See derived/overlap_by_source_project_month_crop.csv for project, month, crop, and percentage details. Boundary points are included (covers semantics). Percentages are relative to all points in that month and to that month’s same crop label. Cross-layer duplicate points are not deduplicated in these source-specific summaries.",
                "",
                "## Failures and caveats",
                "",
                f"Failed service/layer requests: {len(failures)}. See failures.csv and manifest.json for the exact errors. Raw ArcGIS metadata and pages are retained under raw/; source-coordinate feature collections are under data/.",
            ]
        )
        (outdir / "DATA_AUDIT_REPORT.md").write_text(
            "\n".join(report_lines) + "\n", encoding="utf-8"
        )
    else:
        failure_lines = [
            "# TGRAC Crop and Candidate-Polygon Audit",
            "",
            f"> Attempted: {utc_now()}",
            "",
            "No service metadata or feature records were retrieved. No crop counts or overlap results were computed.",
            "",
            "## Exact failures",
            "",
            "| Source | Error |",
            "|---|---|",
        ]
        failure_lines.extend(
            f"| {row['source']} | {row['error']} |" for row in failures
        )
        failure_lines.extend(
            [
                "",
                "Do not interpret missing output tables as zero observations or zero overlap. "
                "Retry after DNS/network access is available. Layer 18 and I&CAD layers 9/10 "
                "remain candidate polygons, not verified command boundaries.",
            ]
        )
        (outdir / "DATA_AUDIT_REPORT.md").write_text(
            "\n".join(failure_lines) + "\n", encoding="utf-8"
        )
    write_csv(outdir / "failures.csv", failures)
    manifest = {
        "created_at_utc": utc_now(),
        "source_layers": [
            {"name": name, "url": f"{root}/{layer_id}", "role": role}
            for name, root, layer_id, role in LAYERS
        ],
        "failures": failures,
        "limitation": (
            "All project polygons are candidates only. No boundary authority, licence, "
            "label validity, or AOI selection is asserted by this audit."
        ),
    }
    (outdir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 1 if failures else 0


def summarize_existing_sources(outdir: Path) -> int:
    """Rebuild derived audit outputs from previously downloaded ArcGIS JSON."""
    datasets = {}
    snapshots = []
    for name, root, layer_id, _ in LAYERS:
        raw_dir = outdir / "raw" / name
        meta_path = raw_dir / f"layer_{layer_id}_metadata.json"
        features_path = raw_dir / f"layer_{layer_id}_features.json"
        if not meta_path.exists() or not features_path.exists():
            raise FileNotFoundError(
                f"Required saved source files missing for {name}: {raw_dir}"
            )
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        features = json.loads(features_path.read_text(encoding="utf-8")).get(
            "features", []
        )
        digest = hashlib.sha256(features_path.read_bytes()).hexdigest()
        oid_field = next(
            (
                field["name"]
                for field in meta.get("fields", [])
                if field.get("type") == "esriFieldTypeOID"
            ),
            None,
        )
        received_features = features
        page_count = None
        if name == "layer18_candidate":
            batch_features = []
            batch_pages = []
            for batch_dir in raw_dir.glob("point_filter_*"):
                batch_file = batch_dir / f"layer_{layer_id}_features.json"
                if batch_file.exists():
                    batch_features.extend(
                        json.loads(batch_file.read_text(encoding="utf-8")).get(
                            "features", []
                        )
                    )
                batch_pages.extend(batch_dir.glob(f"layer_{layer_id}_page_*.json"))
            received_features = batch_features or features
            page_count = len(batch_pages)
        received_ids = [
            (feature.get("attributes") or {}).get(oid_field)
            for feature in received_features
            if oid_field
            and (feature.get("attributes") or {}).get(oid_field) is not None
        ]
        summary_features = deduplicate_features(features, oid_field)
        stats = {
            "expected_count": len(features),
            "service_total_count": (
                1131404 if name == "layer18_candidate" else len(features)
            ),
            "object_ids_returned": len(features),
            "records_received": len(received_features),
            "unique_object_ids": len(set(received_ids)) if received_ids else None,
            "duplicate_object_ids": len(received_ids) - len(set(received_ids)),
            "missing_geometry": sum(
                feature.get("geometry") is None for feature in features
            ),
            "malformed_geometry": sum(
                feature.get("geometry") is not None
                and not geometry_is_well_formed(
                    feature.get("geometry"), meta.get("geometryType")
                )
                for feature in features
            ),
            # This is intentionally unknown: interrupted earlier runs may leave
            # old page files beside the latest consolidated feature snapshot.
            "page_count": page_count,
            "exceeded_transfer_limit": False,
            "object_id_field": oid_field,
            "retrieved_at_utc": datetime.fromtimestamp(
                features_path.stat().st_mtime, timezone.utc
            ).isoformat(),
            "records_used_for_summaries": len(summary_features),
        }
        if name == "layer18_candidate":
            stats["point_filter_batches"] = len(list(raw_dir.glob("point_filter_*")))
        datasets[name] = (meta, summary_features, stats)
        snapshots.append(
            {
                "name": name,
                "source_url": f"{root}/{layer_id}",
                "feature_snapshot": str(features_path),
                "feature_snapshot_sha256": digest,
                "record_count_in_snapshot": len(features),
                "snapshot_mtime_utc": stats["retrieved_at_utc"],
            }
        )
        spatial_reference = meta.get("extent", {}).get("spatialReference")
        data_dir = outdir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / f"{name}.json").write_text(
            json.dumps(
                feature_collection(features, spatial_reference), ensure_ascii=False
            ),
            encoding="utf-8",
        )
    summaries = build_summaries(datasets)
    for filename, rows in summaries.items():
        write_csv(outdir / "derived" / filename, rows)
    failed = []
    write_csv(outdir / "failures.csv", failed)
    manifest = {
        "created_at_utc": utc_now(),
        "source_layers": [
            {"name": name, "url": f"{root}/{layer_id}", "role": role}
            for name, root, layer_id, role in LAYERS
        ],
        "source_snapshots": snapshots,
        "failures": failed,
        "summary_mode": "recomputed from saved original ArcGIS JSON; no network calls",
        "limitation": (
            "Layer 18 features are the point-filtered subset around ground-truth points, not the full 1,131,404 parcels. "
            "All project polygons are candidate geometries only; no boundary authority, licence, label validity, or AOI selection is asserted."
        ),
    }
    (outdir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = [
        "# TGRAC Crop and Candidate-Polygon Audit",
        "",
        f"> Generated from saved source files: {utc_now()}",
        "",
        "> This is a descriptive source audit. Layer 18 and I&CAD polygons remain candidate geometries; no authority, licence, label validity, or AOI selection is asserted.",
        "",
        "## Retrieval summary",
        "",
        "| Source | Layer | Name | Records in saved source | CRS | Missing geometry | Malformed geometry | Duplicate object IDs |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in summaries["feature_counts.csv"]:
        report.append(
            f"| {row['dataset']} | {row['layer_id']} | {row['layer_name']} | {row['records_received']} | "
            f"{row['wkid']} | {row['missing_geometry']} | {row['malformed_geometry']} | {row['duplicate_object_ids']} |"
        )
    report.extend(
        [
            "",
            "## Crop counts by month",
            "",
            "| Month layer | Crop label | Count |",
            "|---|---|---:|",
        ]
    )
    report.extend(
        f"| {row['month_layer']} | {row['crop_label']} | {row['count']} |"
        for row in summaries["crop_counts_by_month.csv"]
    )
    report.extend(
        [
            "",
            "## Overlap",
            "",
            "See derived/overlap_by_source_project_month_crop.csv for source, project, month, crop and percentage details. "
            "Points on polygon boundaries are included. Percentages use the original monthly source-layer denominator; "
            "the same source points are not deduplicated across month layers.",
            "",
            "## Failures and caveats",
            "",
            "All configured source records needed for these summaries were present in the saved downloads. Layer 18 is only the subset of parcel polygons intersecting a point-filter batch; it is not an irrigation-command boundary. "
            "Service terms, boundary provenance, label validity and AOI suitability remain unresolved.",
        ]
    )
    (outdir / "DATA_AUDIT_REPORT.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )
    return 0


def main() -> int:
    """Parse CLI options and run or recompute the ArcGIS audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=Path("data/audits/tgrac"))
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument(
        "--summarize-existing",
        action="store_true",
        help="Rebuild summaries from saved original JSON without making network requests.",
    )
    args = parser.parse_args()
    if args.summarize_existing:
        return summarize_existing_sources(args.outdir)
    return run_audit(args.outdir, args.page_size)


if __name__ == "__main__":
    raise SystemExit(main())
