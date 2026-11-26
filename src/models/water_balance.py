"""Parameter-driven FAO-56 crop evapotranspiration kernel.

The function in this module performs only the documented coefficient
multiplication for a caller-supplied interval. It does not select crop
coefficients, infer growth stages, derive ET0, or calculate field water balance.
"""

from __future__ import annotations

from src.contracts.schemas import CropEvapotranspirationEstimate, TimeInterval


def estimate_crop_evapotranspiration(
    *,
    interval: TimeInterval,
    kc_value: float | None,
    kc_source: str | None,
    et0_value: float | None,
    et0_unit: str | None,
    et0_source: str | None,
    etc_unit: str | None,
    method_version: str,
    input_quality: str,
    limitations: list[str],
    crop_reference: str | None = None,
    stage_reference: str | None = None,
    kc_missing_reason: str | None = None,
    et0_missing_reason: str | None = None,
) -> CropEvapotranspirationEstimate:
    """Compute interval ETc only when sourced Kc and ET0 are both available.

    The result uses ``ETc = Kc × ET0``. Since Kc is dimensionless, ETc retains
    ET0's unit and interval. All scientific inputs and provenance are supplied
    by the caller; this function does not select coefficients or impute values.

    Args:
        interval: Start-inclusive/end-exclusive interval for all depth inputs.
        kc_value: Sourced crop coefficient, or ``None`` when unavailable.
        kc_source: Reference for the supplied crop coefficient.
        et0_value: Reference ET0 depth for the interval, or ``None``.
        et0_unit: Unit/time support of ET0, such as depth over this interval.
        et0_source: Source/method reference for ET0.
        etc_unit: Output unit; when ET0 is present it must match ``et0_unit``.
        method_version: Identifier for this calculation implementation.
        input_quality: Caller-provided quality state for the supplied inputs.
        limitations: Explicit product limitations.
        crop_reference: Optional crop identifier/reference.
        stage_reference: Optional stage estimate/reference used to choose Kc.
        kc_missing_reason: Required when ``kc_value`` is unavailable.
        et0_missing_reason: Required when ``et0_value`` is unavailable.

    Returns:
        A validated CON-07 estimate. ``etc_value`` remains null with a reason
        unless both inputs are present.

    Raises:
        ValueError: If available ET0 and ETc units differ.
        SchemaValidationError: If values, provenance, or missing reasons fail
            the CON-07 contract.
    """
    missing_reasons: dict[str, str] = {}
    if kc_value is None:
        missing_reasons["kc_value"] = kc_missing_reason or "Kc input is unavailable."
    if et0_value is None:
        missing_reasons["et0_value"] = et0_missing_reason or "ET0 input is unavailable."
    missing_reasons["precipitation_value"] = (
        "Precipitation is outside this ETc kernel and was not supplied."
    )

    if kc_value is None or et0_value is None:
        etc_value = None
        missing_reasons["etc_value"] = (
            "ETc requires both a sourced Kc value and an ET0 value for this interval."
        )
    else:
        if etc_unit != et0_unit:
            raise ValueError(
                "etc_unit must match et0_unit; no unit conversion is applied"
            )
        etc_value = kc_value * et0_value

    return CropEvapotranspirationEstimate(
        interval=interval,
        kc_value=kc_value,
        kc_source=kc_source,
        et0_value=et0_value,
        et0_unit=et0_unit,
        et0_source=et0_source,
        etc_value=etc_value,
        etc_unit=etc_unit,
        method_version=method_version,
        input_quality=input_quality,
        limitations=list(limitations),
        crop_reference=crop_reference,
        stage_reference=stage_reference,
        missing_reasons=missing_reasons,
    )
