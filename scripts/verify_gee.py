"""Verify authenticated metadata access to the configured Earth Engine project."""

from __future__ import annotations

from src.data.gee_auth import initialize_earth_engine


COLLECTIONS = {
    "Sentinel-1 GRD": "COPERNICUS/S1_GRD",
    "Sentinel-2 SR Harmonized": "COPERNICUS/S2_SR_HARMONIZED",
    "ERA5-Land Daily Aggregated": "ECMWF/ERA5_LAND/DAILY_AGGR",
}


def main() -> int:
    """Probe collection metadata access for the configured Earth Engine project."""
    ee = initialize_earth_engine()
    for label, asset_id in COLLECTIONS.items():
        collection = ee.ImageCollection(asset_id)
        size = collection.limit(1).size().getInfo()
        print(f"{label}: accessible; one-item probe size={size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
