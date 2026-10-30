"""Software-only checks for Sentinel STAC asset extraction helpers."""

import unittest
from types import SimpleNamespace

from src.data.sentinel1_rtc import _select_latest
from src.data.sentinel_stac_assets import (
    _full_coverage_pixel_window,
    _select_scene,
    _validate_item_id,
    validate_aoi_geometry,
)


class SentinelStacAssetTests(unittest.TestCase):
    """Validate AOI and deterministic scene selection behavior."""

    def test_rejects_non_polygon_aoi(self):
        with self.assertRaisesRegex(ValueError, "Invalid AOI geometry"):
            validate_aoi_geometry({"type": "Point", "coordinates": [79.2, 18.2]})

    def test_selects_least_cloudy_scene_and_newest_on_tie(self):
        items = [
            {
                "id": "older-clear",
                "properties": {
                    "datetime": "2023-02-02T05:00:00Z",
                    "eo:cloud_cover": 2.0,
                },
            },
            {
                "id": "newer-clear",
                "properties": {
                    "datetime": "2023-02-07T05:00:00Z",
                    "eo:cloud_cover": 2.0,
                },
            },
            {
                "id": "cloudy",
                "properties": {
                    "datetime": "2023-02-12T05:00:00Z",
                    "eo:cloud_cover": 25.0,
                },
            },
        ]
        self.assertEqual(_select_scene(items)["id"], "newer-clear")

    def test_missing_cloud_metadata_sorts_after_known_values(self):
        items = [
            {
                "id": "unknown-cloud",
                "properties": {"datetime": "2023-02-12T05:00:00Z"},
            },
            {
                "id": "known-cloud",
                "properties": {
                    "datetime": "2023-02-02T05:00:00Z",
                    "eo:cloud_cover": 40.0,
                },
            },
        ]
        self.assertEqual(_select_scene(items)["id"], "known-cloud")

    def test_sentinel1_selects_latest_scene(self):
        items = [
            {
                "id": "older",
                "properties": {"datetime": "2023-02-08T00:38:56Z"},
            },
            {
                "id": "newer",
                "properties": {"datetime": "2023-02-20T00:38:56Z"},
            },
        ]
        self.assertEqual(_select_latest(items)["id"], "newer")

    def test_pixel_window_rounds_outward_to_cover_aoi(self):
        window = _full_coverage_pixel_window(
            SimpleNamespace(col_off=1.2, row_off=2.7, width=3.1, height=4.2),
            raster_width=10,
            raster_height=10,
            asset_name="B04",
        )
        self.assertEqual(window, (1, 2, 4, 5))

    def test_pixel_window_rejects_partial_source_coverage(self):
        with self.assertRaisesRegex(RuntimeError, "does not fully cover"):
            _full_coverage_pixel_window(
                SimpleNamespace(col_off=-0.5, row_off=0, width=3, height=4),
                raster_width=10,
                raster_height=10,
                asset_name="B04",
            )

    def test_item_id_must_be_safe_as_a_filename(self):
        self.assertEqual(
            _validate_item_id("S2A_44QLF_20230217_L2A"), "S2A_44QLF_20230217_L2A"
        )
        with self.assertRaisesRegex(ValueError, "output filenames"):
            _validate_item_id("../outside")


if __name__ == "__main__":
    unittest.main()
