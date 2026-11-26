"""Method-neutral vegetation-curve transition candidates.

This module provides software mechanics for exploring irregular time series.
It does not map curve features to crop growth stages, fill observation gaps, or
claim phenological accuracy. Every analysis parameter must be supplied by the
caller; field calibration and crop-specific interpretation remain external.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Literal, Sequence

import numpy as np
from numpy.typing import NDArray

TransitionKind = Literal[
    "positive_slope_peak", "vegetation_index_peak", "negative_slope_peak"
]


def _is_finite_real(value: object) -> bool:
    """Return whether value is a finite real number rather than a boolean."""
    return (
        not isinstance(value, (bool, np.bool_))
        and isinstance(value, (int, float, np.integer, np.floating))
        and bool(np.isfinite(value))
    )


@dataclass(frozen=True)
class TransitionCandidate:
    """A curve-shape feature, not a crop-stage estimate."""

    timestamp: str
    kind: TransitionKind
    smoothed_value: float
    slope_per_day: float
    observations_used: int


@dataclass(frozen=True)
class PhenologySegment:
    """Candidate features extracted from a contiguous observation segment."""

    start_timestamp: str
    end_timestamp: str
    observation_count: int
    quality_state: Literal["candidate_only", "insufficient_support"]
    candidates: tuple[TransitionCandidate, ...]
    limitations: tuple[str, ...]


def _timestamp_day(value: str) -> tuple[datetime, float]:
    """Parse a calendar date or explicit UTC timestamp to an epoch day."""
    if not isinstance(value, str):
        raise ValueError("timestamps must be ISO date strings")
    try:
        if len(value) == 10:
            parsed = datetime.combine(date.fromisoformat(value), datetime.min.time())
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(
                parsed
            ):
                raise ValueError("timestamps must specify UTC")
            parsed = parsed.astimezone(timezone.utc)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "timestamps must be valid ISO dates or UTC timestamps"
        ) from exc
    return parsed, parsed.timestamp() / 86400.0


def _local_polynomial(
    days: NDArray[np.float64],
    values: NDArray[np.float64],
    *,
    window_days: float,
    polynomial_order: int,
    minimum_observations: int,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.int32]]:
    """Fit local polynomials at observed times without temporal interpolation."""
    smoothed = np.full(values.shape, np.nan, dtype=np.float64)
    slopes = np.full(values.shape, np.nan, dtype=np.float64)
    support = np.zeros(values.shape, dtype=np.int32)
    half_window = window_days / 2.0
    for index, center in enumerate(days):
        selected = np.abs(days - center) <= half_window
        count = int(np.count_nonzero(selected))
        support[index] = count
        if count < minimum_observations:
            continue
        scaled_days = (days[selected] - center) / half_window
        design = np.vander(scaled_days, N=polynomial_order + 1, increasing=True)
        coefficients, _, rank, _ = np.linalg.lstsq(design, values[selected], rcond=None)
        if rank != polynomial_order + 1:
            continue
        smoothed[index] = coefficients[0]
        slopes[index] = coefficients[1] / half_window
    return smoothed, slopes, support


def _analyze_segment(
    timestamps: Sequence[str],
    days: NDArray[np.float64],
    values: NDArray[np.float64],
    *,
    window_days: float,
    polynomial_order: int,
    minimum_observations: int,
    minimum_abs_slope_per_day: float,
) -> PhenologySegment:
    """Analyze one contiguous series segment."""
    smoothed, slopes, support = _local_polynomial(
        days,
        values,
        window_days=window_days,
        polynomial_order=polynomial_order,
        minimum_observations=minimum_observations,
    )
    usable = np.flatnonzero(np.isfinite(smoothed) & np.isfinite(slopes))
    limitations = (
        "Curve features are candidates only and are not crop growth-stage labels.",
        "Smoothing settings and slope threshold were supplied by the caller; no local calibration is implied.",
        "No gap filling, confidence score, or field validation is performed.",
    )
    if len(usable) < 3:
        return PhenologySegment(
            timestamps[0],
            timestamps[-1],
            len(values),
            "insufficient_support",
            (),
            limitations,
        )

    peak_index = int(usable[np.argmax(smoothed[usable])])
    candidates: list[TransitionCandidate] = [
        TransitionCandidate(
            timestamp=timestamps[peak_index],
            kind="vegetation_index_peak",
            smoothed_value=float(smoothed[peak_index]),
            slope_per_day=float(slopes[peak_index]),
            observations_used=int(support[peak_index]),
        )
    ]
    rising = usable[usable < peak_index]
    if len(rising):
        rising_index = int(rising[np.argmax(slopes[rising])])
        rising_slope = float(slopes[rising_index])
        if rising_slope >= minimum_abs_slope_per_day:
            candidates.append(
                TransitionCandidate(
                    timestamp=timestamps[rising_index],
                    kind="positive_slope_peak",
                    smoothed_value=float(smoothed[rising_index]),
                    slope_per_day=rising_slope,
                    observations_used=int(support[rising_index]),
                )
            )
    falling = usable[usable > peak_index]
    if len(falling):
        falling_index = int(falling[np.argmin(slopes[falling])])
        falling_slope = float(slopes[falling_index])
        if falling_slope <= -minimum_abs_slope_per_day:
            candidates.append(
                TransitionCandidate(
                    timestamp=timestamps[falling_index],
                    kind="negative_slope_peak",
                    smoothed_value=float(smoothed[falling_index]),
                    slope_per_day=falling_slope,
                    observations_used=int(support[falling_index]),
                )
            )
    candidates.sort(key=lambda candidate: candidate.timestamp)
    return PhenologySegment(
        timestamps[0],
        timestamps[-1],
        len(values),
        "candidate_only",
        tuple(candidates),
        limitations,
    )


def detect_transition_candidates(
    *,
    timestamps: Sequence[str],
    vegetation_index: Sequence[float | None],
    window_days: float,
    polynomial_order: int,
    minimum_observations: int,
    maximum_gap_days: float,
    minimum_abs_slope_per_day: float,
) -> tuple[PhenologySegment, ...]:
    """Extract generic curve-shape candidates from an irregular time series.

    Consecutive observations are separated into segments at missing values or
    gaps larger than ``maximum_gap_days``. A local polynomial is fit in a
    caller-defined day window around each observation. The function reports
    the vegetation-index maximum and, when the explicit slope threshold is
    met, the strongest positive and negative slopes around it. It never names
    those events as crop-specific growth stages.

    Args:
        timestamps: Strictly increasing ISO dates or explicit UTC timestamps.
        vegetation_index: Finite index values or ``None`` for missing records.
        window_days: Explicit local regression window, in days.
        polynomial_order: Explicit local polynomial degree, at least one.
        minimum_observations: Required local support, greater than polynomial order.
        maximum_gap_days: Explicit maximum interval before starting a new segment.
        minimum_abs_slope_per_day: Caller-supplied slope floor for rise/decline
            candidates. This is not a project-approved crop threshold.

    Returns:
        Ordered contiguous segments with generic transition candidates and
        limitations. Segments with insufficient local support have no candidates.

    Raises:
        ValueError: If timestamps, observations, or required parameters are invalid.
    """
    if len(timestamps) != len(vegetation_index) or len(timestamps) == 0:
        raise ValueError(
            "timestamps and vegetation_index must have equal non-zero length"
        )
    if not _is_finite_real(window_days) or window_days <= 0:
        raise ValueError("window_days must be positive and finite")
    if (
        not isinstance(polynomial_order, int)
        or isinstance(polynomial_order, bool)
        or polynomial_order < 1
    ):
        raise ValueError("polynomial_order must be a positive integer")
    if (
        not isinstance(minimum_observations, int)
        or isinstance(minimum_observations, bool)
        or minimum_observations <= polynomial_order
    ):
        raise ValueError("minimum_observations must exceed polynomial_order")
    if not _is_finite_real(maximum_gap_days) or maximum_gap_days <= 0:
        raise ValueError("maximum_gap_days must be positive and finite")
    if not _is_finite_real(minimum_abs_slope_per_day) or minimum_abs_slope_per_day < 0:
        raise ValueError("minimum_abs_slope_per_day must be finite and non-negative")

    parsed = [_timestamp_day(timestamp) for timestamp in timestamps]
    day_values = np.asarray([item[1] for item in parsed], dtype=np.float64)
    if np.any(np.diff(day_values) <= 0):
        raise ValueError("timestamps must be strictly increasing")
    for index, value in enumerate(vegetation_index):
        if value is not None and not _is_finite_real(value):
            raise ValueError(f"vegetation_index[{index}] must be finite or null")

    segments: list[PhenologySegment] = []
    start = 0
    for index in range(len(timestamps)):
        is_break = vegetation_index[index] is None
        if (
            index > start
            and day_values[index] - day_values[index - 1] > maximum_gap_days
        ):
            segments.append((start, index))
            start = index
        if is_break:
            if start < index:
                segments.append((start, index))
            start = index + 1
    if start < len(timestamps):
        segments.append((start, len(timestamps)))

    results: list[PhenologySegment] = []
    for left, right in segments:
        if right <= left:
            continue
        segment_values = np.asarray(vegetation_index[left:right], dtype=np.float64)
        results.append(
            _analyze_segment(
                timestamps[left:right],
                day_values[left:right],
                segment_values,
                window_days=window_days,
                polynomial_order=polynomial_order,
                minimum_observations=minimum_observations,
                minimum_abs_slope_per_day=minimum_abs_slope_per_day,
            )
        )
    return tuple(results)
