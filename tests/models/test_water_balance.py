"""Software-only tests for the parameter-driven ETc calculation kernel."""

from __future__ import annotations

import pytest

from src.contracts.schemas import SchemaValidationError, TimeInterval
from src.models.water_balance import estimate_crop_evapotranspiration


def _interval() -> TimeInterval:
    """Return an explicitly synthetic interval for software tests."""
    return TimeInterval(start="2021-01-01", end="2021-01-02")


def _estimate(**overrides):
    """Build a CON-07 result using labelled synthetic fixture inputs."""
    values = {
        "interval": _interval(),
        "kc_value": 1.1,
        "kc_source": "synthetic-test-coefficient",
        "et0_value": 4.0,
        "et0_unit": "mm per test interval",
        "et0_source": "synthetic-test-et0",
        "etc_unit": "mm per test interval",
        "method_version": "test-only",
        "input_quality": "synthetic software fixture",
        "limitations": ["Synthetic software-test values; not project evidence."],
    }
    values.update(overrides)
    return estimate_crop_evapotranspiration(**values)


def test_etc_multiplies_supplied_coefficient_and_interval_et0() -> None:
    estimate = _estimate()

    assert estimate.etc_value == pytest.approx(4.4)
    assert estimate.etc_unit == estimate.et0_unit
    assert estimate.kc_source == "synthetic-test-coefficient"
    assert estimate.et0_source == "synthetic-test-et0"


@pytest.mark.parametrize(
    ("overrides", "missing_key"),
    [
        ({"kc_value": None, "kc_source": None}, "kc_value"),
        ({"et0_value": None, "et0_unit": None, "et0_source": None}, "et0_value"),
    ],
)
def test_missing_inputs_remain_null_with_reasons(overrides, missing_key) -> None:
    estimate = _estimate(**overrides)

    assert estimate.etc_value is None
    assert missing_key in estimate.missing_reasons
    assert "etc_value" in estimate.missing_reasons


def test_missing_input_reason_can_be_supplied_by_caller() -> None:
    estimate = _estimate(
        kc_value=None,
        kc_source=None,
        kc_missing_reason="No locally supported coefficient is available.",
    )

    assert estimate.missing_reasons["kc_value"] == (
        "No locally supported coefficient is available."
    )


def test_output_unit_must_preserve_et0_unit() -> None:
    with pytest.raises(ValueError, match="must match et0_unit"):
        _estimate(etc_unit="m per test interval")


def test_sourced_coefficient_is_required_when_value_is_present() -> None:
    with pytest.raises(SchemaValidationError, match="kc_value requires kc_source"):
        _estimate(kc_source=None)
