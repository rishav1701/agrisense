"""Software checks for the FAO-56 ET0 calculation kernel."""

import math

import pytest

from src.data.era5land import calculate_fao56_reference_et0


def test_fao56_penman_monteith_matches_fao_example_17() -> None:
    """Reproduce the documented FAO-56 Bangkok April worked example."""
    et0 = calculate_fao56_reference_et0(
        t_max_c=34.8,
        t_min_c=25.6,
        actual_vapor_pressure_kpa=2.85,
        net_radiation_mj_m2_day=14.33,
        soil_heat_flux_mj_m2_day=0.14,
        wind_speed_2m_m_s=2.0,
        air_pressure_kpa=101.3,
    )

    assert et0 == pytest.approx(5.72, abs=0.02)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"t_min_c": 31.0}, "t_min_c"),
        ({"wind_speed_2m_m_s": -0.1}, "wind_speed_2m_m_s"),
        ({"air_pressure_kpa": 0.0}, "air_pressure_kpa"),
        ({"actual_vapor_pressure_kpa": -0.1}, "actual_vapor_pressure_kpa"),
        ({"t_max_c": math.inf}, "t_max_c"),
        ({"wind_speed_2m_m_s": True}, "wind_speed_2m_m_s"),
    ],
)
def test_invalid_meteorological_inputs_are_rejected(
    overrides: dict[str, float], message: str
) -> None:
    inputs = {
        "t_max_c": 30.0,
        "t_min_c": 20.0,
        "actual_vapor_pressure_kpa": 1.5,
        "net_radiation_mj_m2_day": 10.0,
        "wind_speed_2m_m_s": 2.0,
        "air_pressure_kpa": 100.0,
    }
    inputs.update(overrides)

    with pytest.raises(ValueError, match=message):
        calculate_fao56_reference_et0(**inputs)
