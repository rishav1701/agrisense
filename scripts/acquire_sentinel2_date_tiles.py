"""Extract separate Sentinel-2 granules for one date without mosaicking."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.data.sentinel_stac_assets import (
    acquire_sentinel2_aoi_date_tiles,
    load_aoi_geometry,
)


def main() -> int:
    """Parse arguments and acquire native-grid tile clips for one date."""
    parser = argparse.ArgumentParser(
        description=(
            "Acquire per-MGRS-tile Sentinel-2 AOI clips for one date. The tool "
            "does not mosaic, reproject, or assess total AOI coverage."
        )
    )
    parser.add_argument(
        "--aoi",
        required=True,
        type=Path,
        help="GeoJSON Polygon/Feature/one-feature collection",
    )
    parser.add_argument("--date", required=True, help="UTC acquisition date YYYY-MM-DD")
    parser.add_argument(
        "--max-cloud-cover",
        required=True,
        type=float,
        help="Explicit scene-level cloud-cover metadata filter (0-100 percent)",
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    manifest = acquire_sentinel2_aoi_date_tiles(
        aoi_geometry=load_aoi_geometry(args.aoi),
        acquisition_date=args.date,
        max_cloud_cover_percent=args.max_cloud_cover,
        output_dir=args.output_dir,
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
