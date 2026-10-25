"""Software-only tests for deterministic synthetic input fixtures."""

import unittest

import numpy as np

from src.contracts.schemas import ObservationStackManifest

from tests.fixtures.synthetic_raster import (
    SYNTHETIC_ONLY as RASTER_SYNTHETIC_ONLY,
    make_synthetic_raster_fixture,
)
from tests.fixtures.synthetic_timeseries import (
    SYNTHETIC_ONLY as TIMESERIES_SYNTHETIC_ONLY,
    make_synthetic_timeseries_fixture,
)


class SyntheticRasterFixtureTests(unittest.TestCase):
    """Check raster fixture shape, reproducibility, and synthetic provenance."""

    def test_shapes_masks_and_manifest_are_explicitly_synthetic(self):
        fixture = make_synthetic_raster_fixture(
            time_steps=2, height=3, width=4, seed=19
        )
        expected_shape = (2, 3, 4)

        self.assertEqual(fixture.optical_reflectance["B08"].shape, expected_shape)
        self.assertEqual(fixture.sar_backscatter_db["VV"].shape, expected_shape)
        self.assertEqual(fixture.weather["weather_variable_01"].shape, expected_shape)
        self.assertTrue(
            all(
                mask.shape == expected_shape
                for mask in fixture.validity_masks.values()
            )
        )
        self.assertTrue(
            all(
                mask.dtype == np.bool_
                for mask in fixture.validity_masks.values()
            )
        )
        self.assertEqual(fixture.metadata["fixture_status"], RASTER_SYNTHETIC_ONLY)
        self.assertEqual(fixture.manifest["limitations"][0], RASTER_SYNTHETIC_ONLY)
        self.assertIsNone(fixture.manifest["analysis_crs"])
        self.assertIsNone(fixture.manifest["aoi_geometry"])
        self.assertTrue(
            all(source["source_id"].startswith("synthetic_test_fixture:") for source in fixture.manifest["sources"])
        )

    def test_modalities_use_separate_fabricated_time_support(self):
        fixture = make_synthetic_raster_fixture(time_steps=3, seed=3)
        self.assertNotEqual(fixture.timestamps["optical"], fixture.timestamps["sar"])
        self.assertNotEqual(fixture.timestamps["sar"], fixture.timestamps["weather"])

    def test_manifest_carries_contract_fields_and_missing_reasons(self):
        manifest = make_synthetic_raster_fixture().manifest
        required_fields = {
            "stack_id",
            "analysis_crs",
            "grid_transform",
            "grid_shape",
            "aoi_geometry",
            "sources",
            "variables",
            "requested_interval",
            "processing_version",
            "limitations",
        }
        self.assertTrue(required_fields.issubset(manifest))
        self.assertTrue(
            {"analysis_crs", "grid_transform", "aoi_geometry"}.issubset(
                manifest["missing_reasons"]
            )
        )

    def test_manifest_validates_against_con03_schema(self):
        manifest = ObservationStackManifest.from_dict(
            make_synthetic_raster_fixture().manifest
        )
        self.assertEqual(manifest.stack_id, "synthetic-test-only")
        self.assertEqual(len(manifest.sources), 3)
        self.assertTrue(all("synthetic_test_fixture" in source.source_id for source in manifest.sources))

    def test_seed_reproduces_values(self):
        left = make_synthetic_raster_fixture(seed=23)
        right = make_synthetic_raster_fixture(seed=23)
        np.testing.assert_array_equal(
            left.optical_reflectance["B04"], right.optical_reflectance["B04"]
        )
        np.testing.assert_array_equal(
            left.validity_masks["sar_valid"], right.validity_masks["sar_valid"]
        )

    def test_invalid_dimensions_and_seed_fail_clearly(self):
        with self.assertRaises(ValueError):
            make_synthetic_raster_fixture(height=0)
        with self.assertRaises(ValueError):
            make_synthetic_raster_fixture(time_steps=1.5)
        with self.assertRaises(ValueError):
            make_synthetic_raster_fixture(seed=-1)


class SyntheticTimeSeriesFixtureTests(unittest.TestCase):
    """Check mock sequence dimensions, missingness, and reproducibility."""

    def test_dimensions_masks_and_synthetic_marker(self):
        fixture = make_synthetic_timeseries_fixture(
            entities=2, time_steps=5, features=3, seed=29
        )
        self.assertEqual(fixture.values.shape, (2, 5, 3))
        self.assertEqual(fixture.valid_mask.shape, (2, 5, 3))
        self.assertEqual(fixture.valid_mask.dtype, np.bool_)
        self.assertEqual(len(fixture.timestamps), 5)
        self.assertEqual(len(fixture.entity_ids), 2)
        self.assertEqual(len(fixture.feature_names), 3)
        self.assertEqual(fixture.metadata, TIMESERIES_SYNTHETIC_ONLY)

    def test_seed_reproduces_values_and_masks(self):
        left = make_synthetic_timeseries_fixture(seed=31)
        right = make_synthetic_timeseries_fixture(seed=31)
        np.testing.assert_array_equal(left.values, right.values)
        np.testing.assert_array_equal(left.valid_mask, right.valid_mask)

    def test_invalid_dimensions_and_seed_fail_clearly(self):
        with self.assertRaises(ValueError):
            make_synthetic_timeseries_fixture(entities=0)
        with self.assertRaises(ValueError):
            make_synthetic_timeseries_fixture(features=True)
        with self.assertRaises(ValueError):
            make_synthetic_timeseries_fixture(seed=-5)


if __name__ == "__main__":
    unittest.main()
