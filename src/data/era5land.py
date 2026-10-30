"""FAO-56 reference evapotranspiration calculation from normalized inputs.

This module implements the daily Penman-Monteith calculation only. It does
not retrieve ERA5-Land data, decode provider bands, derive net radiation,
convert wind height, aggregate UTC records into local days, or resample grids.
Those operations require explicit source and study-area conventions.
"""

from __future__ import annotations

import math


def calculate_fao56_reference_et0(
    *,
    t_max_c: float,
    t_min_c: float,
    actual_vapor_pressure_kpa: float,
    net_radiation_mj_m2_day: float,
    wind_speed_2m_m_s: float,
    air_pressure_kpa: float,
    soil_heat_flux_mj_m2_day: float = 0.0,
) -> float:
    """Calculate reference ET0 using the daily FAO-56 Penman-Monteith equation.

    All meteorological inputs must already represent a consistent daily
    interval. Wind speed must be at 2 m; radiation is net radiation at the
    reference surface. The result is an estimate in mm/day for the hypothetical
    FAO grass reference crop, not crop ET, soil moisture, or irrigation demand.

    Args:
        t_max_c: Daily maximum air temperature in degrees Celsius.
        t_min_c: Daily minimum air temperature in degrees Celsius.
        actual_vapor_pressure_kpa: Actual vapor pressure in kPa.
        net_radiation_mj_m2_day: Daily net radiation in MJ m-2 day-1.
        wind_speed_2m_m_s: Daily mean wind speed at 2 m in m s-1.
        air_pressure_kpa: Daily atmospheric pressure in kPa.
        soil_heat_flux_mj_m2_day: Soil heat flux in MJ m-2 day-1. The FAO-56
            daily convention commonly treats this as zero; provide a sourced
            value for other periods or conditions.

    Returns:
        Reference evapotranspiration in mm/day. The equation result is not
        clipped, so callers can inspect unusual inputs or negative estimates.

    Raises:
        ValueError: If an input is non-finite or outside its physical domain.
    """
    values = {
        "t_max_c": t_max_c,
        "t_min_c": t_min_c,
        "actual_vapor_pressure_kpa": actual_vapor_pressure_kpa,
        "net_radiation_mj_m2_day": net_radiation_mj_m2_day,
        "wind_speed_2m_m_s": wind_speed_2m_m_s,
        "air_pressure_kpa": air_pressure_kpa,
        "soil_heat_flux_mj_m2_day": soil_heat_flux_mj_m2_day,
    }
    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a finite number")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")

    if t_min_c > t_max_c:
        raise ValueError("t_min_c must not exceed t_max_c")
    if actual_vapor_pressure_kpa < 0:
        raise ValueError("actual_vapor_pressure_kpa must be non-negative")
    if wind_speed_2m_m_s < 0:
        raise ValueError("wind_speed_2m_m_s must be non-negative")
    if air_pressure_kpa <= 0:
        raise ValueError("air_pressure_kpa must be positive")

    t_mean_c = (t_max_c + t_min_c) / 2.0
    if t_mean_c <= -273.0:
        raise ValueError("mean temperature must be above absolute zero")

    e_t_max = 0.6108 * math.exp(17.27 * t_max_c / (t_max_c + 237.3))
    e_t_min = 0.6108 * math.exp(17.27 * t_min_c / (t_min_c + 237.3))
    saturation_vapor_pressure_kpa = (e_t_max + e_t_min) / 2.0
    delta = (
        4098.0
        * (0.6108 * math.exp(17.27 * t_mean_c / (t_mean_c + 237.3)))
        / (t_mean_c + 237.3) ** 2
    )
    psychrometric_constant = 0.000665 * air_pressure_kpa

    numerator = 0.408 * delta * (
        net_radiation_mj_m2_day - soil_heat_flux_mj_m2_day
    ) + psychrometric_constant * (900.0 / (t_mean_c + 273.0)) * wind_speed_2m_m_s * (
        saturation_vapor_pressure_kpa - actual_vapor_pressure_kpa
    )
    denominator = delta + psychrometric_constant * (1.0 + 0.34 * wind_speed_2m_m_s)
    return numerator / denominator
