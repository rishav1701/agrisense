"""Synthetic software tests for the TGRAC audit helpers.

These fixtures verify code behavior only and are not scientific observations.
"""

import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from scripts.agrisense_tgrac_audit import (
    build_summaries,
    point_in_arcgis_polygon,
    fetch_layer,
    deduplicate_features,
    geometry_is_well_formed,
    polygon_bounds,
)


class GeometryTests(unittest.TestCase):
    """Exercise point-in-polygon behavior on synthetic Esri rings."""

    def test_point_inside_and_outside_polygon(self):
        polygon = {"rings": [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]}
        self.assertTrue(point_in_arcgis_polygon({"x": 5, "y": 5}, polygon))
        self.assertFalse(point_in_arcgis_polygon({"x": 11, "y": 5}, polygon))

    def test_polygon_hole_excludes_interior_and_includes_boundary(self):
        polygon = {
            "rings": [
                [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
                [[3, 3], [7, 3], [7, 7], [3, 7], [3, 3]],
            ]
        }
        self.assertFalse(point_in_arcgis_polygon({"x": 5, "y": 5}, polygon))
        self.assertTrue(point_in_arcgis_polygon({"x": 3, "y": 5}, polygon))
        self.assertTrue(point_in_arcgis_polygon({"x": 2, "y": 2}, polygon))

    def test_missing_geometry_does_not_match(self):
        self.assertFalse(point_in_arcgis_polygon(None, {"rings": []}))

    def test_polygon_bounds(self):
        polygon = {"rings": [[[2, 1], [2, 8], [9, 8], [9, 1], [2, 1]]]}
        self.assertEqual(polygon_bounds(polygon), (2.0, 1.0, 9.0, 8.0))
        self.assertIsNone(polygon_bounds({"rings": []}))

    def test_malformed_point_and_polygon_are_flagged(self):
        self.assertFalse(
            geometry_is_well_formed(
                {"x": float("nan"), "y": 2}, "esriGeometryPoint"
            )
        )
        self.assertFalse(
            geometry_is_well_formed(
                {"rings": [[[0, 0], [1, 1]]]}, "esriGeometryPolygon"
            )
        )


class SummaryTests(unittest.TestCase):
    """Verify synthetic summary rows and candidate-boundary labeling."""

    def test_overlap_is_candidate_and_keeps_missing_geometry_count(self):
        meta = {
            "id": 10,
            "name": "month",
            "geometryType": "esriGeometryPoint",
            "extent": {"spatialReference": {"wkid": 4326}},
        }
        points = [
            {"geometry": {"x": 5, "y": 5}, "attributes": {"crop": "Rice", "districtname": "D1"}},
            {"geometry": None, "attributes": {"crop": None, "districtname": None}},
        ]
        polygon_meta = {
            "id": 18,
            "name": "candidate",
            "geometryType": "esriGeometryPolygon",
            "extent": {"spatialReference": {"wkid": 4326}},
        }
        polygon = {
            "geometry": {"rings": [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]},
            "attributes": {"Irrigation_L_3": "candidate"},
        }
        data = {
            "february_2023": (meta, points, {"missing_geometry": 1, "records_received": 2}),
            "layer18_candidate": (polygon_meta, [polygon], {"missing_geometry": 0, "records_received": 1}),
        }
        result = build_summaries(data)
        self.assertEqual(result["feature_counts.csv"][0]["missing_geometry"], 1)
        overlap = result["overlap_by_source_project_month_crop.csv"]
        rice = next(row for row in overlap if row["crop_label"] == "Rice")
        self.assertEqual(rice["point_count"], 1)
        self.assertFalse(rice["authoritative_command_verified"])

    def test_fetch_layer_paginates_and_counts_duplicate_ids(self):
        replies = [
            {"id": 10, "name": "synthetic", "maxRecordCount": 2,
             "fields": [{"name": "OBJECTID", "type": "esriFieldTypeOID"}]},
            {"count": 3},
            {"count": 3},
            {"objectIdFieldName": "OBJECTID", "objectIds": [1, 2, 3]},
            {"features": [
                {"attributes": {"OBJECTID": 1}, "geometry": {"x": 1, "y": 1}},
                {"attributes": {"OBJECTID": 2}, "geometry": None},
            ]},
            {"features": [
                {"attributes": {"OBJECTID": 2}, "geometry": {"x": 2, "y": 2}},
            ]},
        ]

        class FakeResponse:
            def __init__(self, payload):
                self.payload = payload

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return json.dumps(self.payload).encode("utf-8")

        with tempfile.TemporaryDirectory(
            dir=Path(__file__).resolve().parents[1] / "tests"
        ) as folder:
            with patch(
                "scripts.agrisense_tgrac_audit.urlopen",
                side_effect=[FakeResponse(item) for item in replies],
            ) as mocked:
                _meta, features, stats = fetch_layer(
                    "https://example.invalid/MapServer", 10, Path(folder), page_size=2
                )
        self.assertEqual(len(features), 3)
        self.assertEqual(stats["expected_count"], 3)
        self.assertEqual(stats["duplicate_object_ids"], 1)
        self.assertEqual(stats["missing_geometry"], 1)
        self.assertEqual(mocked.call_count, 6)

    def test_duplicate_source_ids_are_deduplicated_for_summaries(self):
        features = [
            {"attributes": {"OBJECTID": 7, "crop": "Rice"}},
            {"attributes": {"OBJECTID": 7, "crop": "Rice"}},
            {"attributes": {"crop": "Unknown ID"}},
        ]
        unique = deduplicate_features(features, "OBJECTID")
        self.assertEqual(len(unique), 2)


if __name__ == "__main__":
    unittest.main()
