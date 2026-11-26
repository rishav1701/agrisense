"""Software-only tests for generic phenology candidate extraction."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from src.models.phenology import detect_transition_candidates


def _synthetic_curve() -> tuple[list[str], list[float]]:
    """Return an explicitly synthetic double-logistic software fixture."""
    offsets = np.arange(0, 181, 10, dtype=float)
    values = (
        0.15
        + 0.72 / (1 + np.exp(-(offsets - 45) / 9))
        - 0.62 / (1 + np.exp(-(offsets - 135) / 10))
    )
    timestamps = [
        (date(2021, 1, 1) + timedelta(days=int(offset))).isoformat()
        for offset in offsets
    ]
    return timestamps, values.tolist()


def _detect(timestamps: list[str], values: list[float | None]):
    """Call the candidate extractor with explicit software-test settings."""
    return detect_transition_candidates(
        timestamps=timestamps,
        vegetation_index=values,
        window_days=50,
        polynomial_order=2,
        minimum_observations=4,
        maximum_gap_days=20,
        minimum_abs_slope_per_day=0.001,
    )


def test_candidate_curve_reports_generic_features_without_stage_labels() -> None:
    timestamps, values = _synthetic_curve()

    [segment] = _detect(timestamps, values)

    assert segment.quality_state == "candidate_only"
    assert {candidate.kind for candidate in segment.candidates} == {
        "positive_slope_peak",
        "vegetation_index_peak",
        "negative_slope_peak",
    }
    assert all(
        "crop growth-stage labels" in limitation
        for limitation in segment.limitations[:1]
    )
    assert all(candidate.observations_used >= 4 for candidate in segment.candidates)


def test_numpy_series_values_are_supported() -> None:
    timestamps, values = _synthetic_curve()

    [segment] = _detect(timestamps, np.asarray(values, dtype=np.float32).tolist())

    assert segment.quality_state == "candidate_only"


def test_missing_observation_splits_series_without_gap_filling() -> None:
    timestamps, values = _synthetic_curve()
    values[9] = None

    segments = _detect(timestamps, values)

    assert len(segments) == 2
    assert segments[0].end_timestamp == timestamps[8]
    assert segments[1].start_timestamp == timestamps[10]


def test_large_temporal_gap_splits_series() -> None:
    timestamps, values = _synthetic_curve()
    timestamps[9:] = [
        (date.fromisoformat(stamp) + timedelta(days=40)).isoformat()
        for stamp in timestamps[9:]
    ]

    segments = _detect(timestamps, values)

    assert len(segments) == 2


def test_sparse_segment_returns_explicit_insufficient_support() -> None:
    [segment] = _detect(
        ["2021-01-01", "2021-01-10", "2021-01-20"],
        [0.1, 0.5, 0.2],
    )

    assert segment.quality_state == "insufficient_support"
    assert segment.candidates == ()


@pytest.mark.parametrize(
    ("timestamps", "values", "message"),
    [
        (["2021-01-01", "2021-01-01"], [0.1, 0.2], "strictly increasing"),
        (["2021-02-30"], [0.1], "valid ISO"),
        (["2021-01-01", "2021-01-02"], [0.1], "equal non-zero length"),
        (["2021-01-01"], [float("nan")], "finite or null"),
        (["2021-01-01"], [True], "finite or null"),
    ],
)
def test_invalid_series_are_rejected(
    timestamps: list[str], values: list[float | None], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        _detect(timestamps, values)


def test_parameters_are_required_and_checked() -> None:
    with pytest.raises(ValueError, match="minimum_observations"):
        detect_transition_candidates(
            timestamps=["2021-01-01"],
            vegetation_index=[0.1],
            window_days=20,
            polynomial_order=2,
            minimum_observations=2,
            maximum_gap_days=10,
            minimum_abs_slope_per_day=0,
        )
