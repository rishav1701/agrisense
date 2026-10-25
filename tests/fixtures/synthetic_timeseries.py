"""Synthetic time-series fixtures for software tests only.

Generated values and timestamps are artificial. They are not crop labels,
field measurements, sensor records, phenology, stress observations, or
scientific validation data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float32]
BoolArray = NDArray[np.bool_]

SYNTHETIC_ONLY = "SYNTHETIC SOFTWARE TEST FIXTURE — NOT OBSERVATION OR EVIDENCE"


@dataclass(frozen=True)
class SyntheticTimeSeriesFixture:
    """Artificial feature sequences with missingness represented explicitly.

    ``values`` and ``valid_mask`` have shape ``(entity, time, feature)``.
    Entity identifiers and feature names are test placeholders with no link to
    real fields, crops, sensors, or locations.
    """

    values: FloatArray
    valid_mask: BoolArray
    timestamps: tuple[str, ...]
    entity_ids: tuple[str, ...]
    feature_names: tuple[str, ...]
    metadata: str


def make_synthetic_timeseries_fixture(
    *, entities: int = 3, time_steps: int = 6, features: int = 4, seed: int = 11
) -> SyntheticTimeSeriesFixture:
    """Create deterministic artificial sequences for pipeline software tests.

    Args:
        entities: Number of placeholder entities.
        time_steps: Number of fabricated timestamps per entity.
        features: Number of generic feature channels.
        seed: Seed for reproducible software-test values.

    Returns:
        Artificial values, a matching validity mask, placeholder identifiers,
        fabricated timestamps, and a synthetic-only disclaimer.

    Raises:
        ValueError: If a dimension is not a positive integer or the seed is
            negative.
    """
    dimensions = (entities, time_steps, features)
    if any(
        not isinstance(value, int) or isinstance(value, bool)
        for value in dimensions
    ):
        raise ValueError("entities, time_steps, and features must be integers")
    if any(value <= 0 for value in dimensions):
        raise ValueError("entities, time_steps, and features must be positive")
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("seed must be a non-negative integer")

    rng = np.random.default_rng(seed)
    values = rng.random(dimensions, dtype=np.float32)
    valid_mask = rng.random(dimensions) >= 0.15
    start = date(2000, 1, 1)

    return SyntheticTimeSeriesFixture(
        values=values,
        valid_mask=valid_mask,
        timestamps=tuple(
            (start + timedelta(days=index)).isoformat() for index in range(time_steps)
        ),
        entity_ids=tuple(f"synthetic_entity_{index:03d}" for index in range(entities)),
        feature_names=tuple(
            f"synthetic_feature_{index:03d}" for index in range(features)
        ),
        metadata=SYNTHETIC_ONLY,
    )
