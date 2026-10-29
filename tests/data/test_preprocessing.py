"""Software-only tests for satellite stack assembly using synthetic arrays."""

import unittest

import numpy as np

from src.contracts.schemas import SourceMetadata, TimeInterval, VariableMetadata
from src.data.preprocessing import SatelliteVariableInput, assemble_satellite_stack


def source(source_id: str, timestamps: list[str]) -> SourceMetadata:
    """Create synthetic source metadata for software tests only."""
    return SourceMetadata(
        source_id=source_id,
        collection_id="synthetic-test-fixture",
        version="test-only",
        timestamps=timestamps,
        native_grid="synthetic-test-grid",
        native_resolution_m=10.0,
        quality_mask_reference="synthetic-test-mask",
    )


def variable(name: str, source_id: str, timestamps: tuple[str, ...], values):
    """Create a synthetic variable input for software tests only."""
    return SatelliteVariableInput(
        values=np.asarray(values),
        validity_mask=np.ones(np.shape(values), dtype=np.bool_),
        timestamps=timestamps,
        source_id=source_id,
        metadata=VariableMetadata(
            name=name,
            units="test units",
            scale=1.0,
            source_reference=source_id,
            time_support="synthetic test timestamps",
            resampling_method="none in test fixture",
            mask_reference="synthetic-test-mask",
        ),
    )


class SatelliteStackAssemblyTests(unittest.TestCase):
    """Validate provenance-preserving assembly behavior, not science."""

    def assemble(self, inputs, source_records):
        """Assemble with synthetic software-test metadata."""
        return assemble_satellite_stack(
            stack_id="synthetic-stack-test",
            variables=tuple(inputs),
            sources=tuple(source_records),
            requested_interval=TimeInterval("2023-01-01", "2023-02-01"),
            analysis_crs="EPSG:32644",
            grid_transform=(10.0, 0.0, 100.0, 0.0, -10.0, 200.0),
            aoi_geometry=None,
            processing_version="test-only",
        )

    def test_preserves_sensor_specific_irregular_timestamps_and_missingness(self):
        optical_times = ("2023-01-02T00:00:00Z", "2023-01-20T00:00:00Z")
        radar_times = ("2023-01-04T00:00:00Z",)
        optical_values = np.array([[[1.0, np.nan]], [[2.0, 3.0]]], dtype=np.float64)
        result = self.assemble(
            [
                variable("ndvi", "s2-test", optical_times, optical_values),
                variable("vh_db", "s1-test", radar_times, [[[np.inf, -15.0]]]),
            ],
            [source("s2-test", list(optical_times)), source("s1-test", list(radar_times))],
        )

        self.assertEqual(result.manifest.grid_shape, (1, 2))
        self.assertEqual(result.manifest.sources[0].timestamps, list(optical_times))
        self.assertEqual(result.variables["ndvi"].shape, (2, 1, 2))
        self.assertFalse(result.validity_masks["ndvi"][0, 0, 1])
        self.assertTrue(np.isnan(result.variables["ndvi"][0, 0, 1]))
        self.assertFalse(result.validity_masks["vh_db"][0, 0, 0])
        self.assertTrue(np.isnan(result.variables["vh_db"][0, 0, 0]))
        self.assertEqual(result.valid_data_fraction["ndvi"], 0.75)
        self.assertEqual(result.valid_data_fraction["vh_db"], 0.5)
        self.assertIn("aoi_geometry", result.manifest.missing_reasons)

    def test_rejects_grid_shape_and_time_metadata_mismatch(self):
        times = ("2023-01-02T00:00:00Z",)
        with self.assertRaisesRegex(ValueError, "same declared spatial shape"):
            self.assemble(
                [
                    variable("a", "s1", times, np.ones((1, 2, 2))),
                    variable("b", "s2", times, np.ones((1, 1, 4))),
                ],
                [source("s1", list(times)), source("s2", list(times))],
            )
        with self.assertRaisesRegex(ValueError, "referenced source metadata"):
            self.assemble(
                [variable("a", "s1", times, np.ones((1, 1, 1)))],
                [source("s1", ["2023-01-03T00:00:00Z"])],
            )

    def test_rejects_unsorted_duplicate_and_out_of_window_times(self):
        for timestamps in (
            ("2023-01-20T00:00:00Z", "2023-01-02T00:00:00Z"),
            ("2023-01-02T00:00:00Z", "2023-01-02T00:00:00Z"),
            ("2023-02-01T00:00:00Z",),
        ):
            with self.subTest(timestamps=timestamps), self.assertRaises(ValueError):
                self.assemble(
                    [variable("a", "s1", timestamps, np.ones((len(timestamps), 1, 1)))],
                    [source("s1", list(timestamps))],
                )


if __name__ == "__main__":
    unittest.main()
