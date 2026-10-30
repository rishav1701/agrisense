"""Acquire native-grid Sentinel-1 RTC windows from Planetary Computer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.data.sentinel1_rtc import acquire_sentinel1_rtc_aoi
from src.data.sentinel_stac_assets import load_aoi_geometry


def main() -> int:
    """Parse command-line options and extract one Sentinel-1 RTC scene."""
    parser = argparse.ArgumentParser(
        description=(
            "Search public Planetary Computer STAC metadata and extract native-grid "
            "Sentinel-1 VV/VH RTC GeoTIFF windows."
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
    args = parser.parse_args()
    manifest = acquire_sentinel1_rtc_aoi(
        aoi_geometry=load_aoi_geometry(args.aoi),
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=args.output_dir,
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
