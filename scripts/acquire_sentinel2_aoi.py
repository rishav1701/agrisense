"""Acquire a small Sentinel-2 L2A AOI window from Earth Search."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.data.sentinel_stac_assets import acquire_sentinel2_aoi, load_aoi_geometry


def main() -> int:
    """Parse command-line options and extract one Sentinel-2 scene."""
    parser = argparse.ArgumentParser(
        description=(
            "Search public Earth Search STAC metadata and extract native-grid "
            "Sentinel-2 B02/B04/B08/SCL GeoTIFF windows."
        )
    )
    parser.add_argument(
        "--aoi", required=True, type=Path, help="GeoJSON Polygon or Feature"
    )
    parser.add_argument("--start-date", required=True, help="Inclusive YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="Exclusive YYYY-MM-DD")
    parser.add_argument(
        "--output-dir", required=True, type=Path, help="Directory for extracted assets"
    )
    parser.add_argument(
        "--max-cloud-cover",
        type=float,
        default=30,
        help="Maximum scene-level cloud cover percentage (default: 30)",
    )
    args = parser.parse_args()
    manifest = acquire_sentinel2_aoi(
        aoi_geometry=load_aoi_geometry(args.aoi),
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=args.output_dir,
        max_cloud_cover_percent=args.max_cloud_cover,
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
