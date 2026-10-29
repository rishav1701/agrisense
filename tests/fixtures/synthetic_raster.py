"""Synthetic raster fixtures for software tests only.

All generated arrays are artificial and must never be presented as satellite
observations, meteorological records, model outputs, or scientific evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Mapping

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float32]
BoolArray = NDArray[np.bool_]

SYNTHETIC_ONLY = "SYNTHETIC SOFTWARE TEST FIXTURE — NOT OBSERVATION OR EVIDENCE"


def _fake_dates(time_steps: int, offset_days: int) -> tuple[str, ...]:
    """Return fabricated ISO dates for one synthetic modality."""
    start = date(2000, 1, 1) + timedelta(days=offset_days)
    return tuple(
        (start + timedelta(days=index)).isoformat() for index in range(time_steps)
    )


@dataclass(frozen=True)
class SyntheticRasterFixture:
    """Independent synthetic sensor arrays with masks and test-only metadata.

    Arrays use ``(time, row, column)`` order. Modality timestamps are stored
    separately to avoid implying that optical, SAR, and weather observations
    are synchronized. No AOI, CRS, source asset identifier, or real acquisition
    time is supplied.
    """

    optical_reflectance: Mapping[str, FloatArray]
    sar_backscatter_db: Mapping[str, FloatArray]
    weather: Mapping[str, FloatArray]
    validity_masks: Mapping[str, BoolArray]
    timestamps: Mapping[str, tuple[str, ...]]
    metadata: Mapping[str, str]
    manifest: Mapping[str, object]


def make_synthetic_raster_fixture(
    *, time_steps: int = 3, height: int = 4, width: int = 5, seed: int = 7
) -> SyntheticRasterFixture:
    """Create deterministic, explicitly synthetic multi-sensor test arrays.

    Args:
        time_steps: Number of fabricated time slices per modality.
        height: Number of fabricated raster rows.
        width: Number of fabricated raster columns.
        seed: Seed for reproducible software-test values.

    Returns:
        A fixture containing separate optical, SAR, and weather arrays, masks,
        fabricated timestamps, and a conspicuous synthetic-only marker.

    Raises:
        ValueError: If a dimension is not a positive integer or the seed is
            negative.
    """
    dimensions = (time_steps, height, width)
    if any(
        not isinstance(value, int) or isinstance(value, bool) for value in dimensions
    ):
        raise ValueError("time_steps, height, and width must be integers")
    if any(value <= 0 for value in dimensions):
        raise ValueError("time_steps, height, and width must be positive")
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("seed must be a non-negative integer")

    rng = np.random.default_rng(seed)
    optical = {
        band: rng.random(dimensions, dtype=np.float32)
        for band in ("B02", "B03", "B04", "B08", "B11")
    }
    sar = {
        polarization: rng.uniform(-30.0, 0.0, dimensions).astype(np.float32)
        for polarization in ("VV", "VH")
    }
    weather = {
        variable: rng.random(dimensions, dtype=np.float32)
        for variable in ("weather_variable_01", "weather_variable_02")
    }

    masks = {
        f"{modality}_valid": rng.random(dimensions) >= 0.15
        for modality in ("optical", "sar", "weather")
    }
    timestamps = {
        "optical": _fake_dates(time_steps, 0),
        "sar": _fake_dates(time_steps, 100),
        "weather": _fake_dates(time_steps, 200),
    }
    interval_dates = tuple(
        timestamp
        for modality_dates in timestamps.values()
        for timestamp in modality_dates
    )

    synthetic_units = {
        "optical": "unitless synthetic reflectance-like test values",
        "sar": "dB synthetic test values",
        "weather": "synthetic; physical unit intentionally unspecified",
    }
    variables = [
        {
            "name": name,
            "units": synthetic_units[modality],
            "scale": None,
            "source_reference": "synthetic_test_fixture",
            "time_support": "fabricated test timestamp",
            "resampling_method": None,
            "mask_reference": f"{modality}_valid",
            "missing_reasons": {
                "scale": "Synthetic test values do not represent a source scale.",
                "resampling_method": "No spatial resampling is performed in this fixture.",
            },
        }
        for modality, bands in (
            ("optical", optical),
            ("sar", sar),
            ("weather", weather),
        )
        for name in bands
    ]
    sources = [
        {
            "source_id": f"synthetic_test_fixture:{modality}",
            "collection_id": None,
            "version": None,
            "timestamps": list(timestamps[modality]),
            "native_grid": None,
            "native_resolution_m": None,
            "quality_mask_reference": f"{modality}_valid",
            "missing_reasons": {
                "collection_id": "Synthetic fixture; no source collection exists.",
                "version": "Synthetic fixture; no source version exists.",
                "native_grid": "Synthetic arrays have no source grid.",
                "native_resolution_m": "Synthetic arrays have no source resolution.",
            },
        }
        for modality in ("optical", "sar", "weather")
    ]

    return SyntheticRasterFixture(
        optical_reflectance=optical,
        sar_backscatter_db=sar,
        weather=weather,
        validity_masks=masks,
        timestamps=timestamps,
        metadata={
            "fixture_status": SYNTHETIC_ONLY,
            "seed": str(seed),
            "array_order": "time,row,column",
            "spatial_reference": "omitted: no AOI or CRS is implied",
            "source_provenance": "fabricated values; no external data source",
        },
        manifest={
            "stack_id": "synthetic-test-only",
            "analysis_crs": None,
            "grid_transform": None,
            "grid_shape": [height, width],
            "aoi_geometry": None,
            "sources": sources,
            "variables": variables,
            "requested_interval": {
                "start": min(interval_dates),
                "end": max(interval_dates),
            },
            "processing_version": "synthetic-fixture-v1",
            "missing_reasons": {
                "analysis_crs": "No real CRS exists in this synthetic fixture.",
                "grid_transform": "Array indices have no real-world coordinates.",
                "aoi_geometry": "No study area is represented.",
            },
            "limitations": [
                SYNTHETIC_ONLY,
                "No real AOI, CRS, asset identifier, acquisition time, or units.",
                "Manifest is a software-test fixture, not production provenance.",
            ],
        },
    )
