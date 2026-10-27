"""Sentinel-1 GRD backscatter math for caller-prepared arrays.

These utilities do not retrieve scenes, choose orbit/polarization subsets,
apply border-noise handling, terrain correction, or speckle filtering.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float32]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class Sentinel1DualPolFeatures:
    """Dual-polarization backscatter with an explicitly defined ratio."""

    vv_db: FloatArray
    vh_db: FloatArray
    vv_linear: FloatArray
    vh_linear: FloatArray
    vh_to_vv_linear_ratio: FloatArray
    valid_mask: BoolArray


def db_to_linear_power(backscatter_db: NDArray[np.floating]) -> FloatArray:
    """Convert calibrated backscatter from dB to linear power.

    Applies ``power = 10 ** (dB / 10)`` elementwise. Non-finite input cells
    are represented as NaN. This conversion does not denoise or calibrate data.

    Args:
        backscatter_db: Calibrated backscatter coefficient in decibels.

    Returns:
        Float32 linear-power array with the same shape.
    """
    values = np.asarray(backscatter_db, dtype=np.float32)
    with np.errstate(over="ignore", invalid="ignore"):
        linear = np.power(np.float32(10.0), values / np.float32(10.0))
    return np.where(
        np.isfinite(values) & np.isfinite(linear), linear, np.nan
    ).astype(np.float32, copy=False)


def compute_dual_pol_features(
    *,
    vv_db: NDArray[np.floating],
    vh_db: NDArray[np.floating],
    validity_mask: BoolArray,
) -> Sentinel1DualPolFeatures:
    """Prepare VV/VH backscatter and compute VH/VV in linear-power space.

    The ratio is ``10 ** ((VH_dB - VV_dB) / 10)``. Dividing VV/VH values in
    dB is not a power ratio. Inputs must already share a grid and represent
    compatible acquisitions; this function does not filter orbit or time.

    Args:
        vv_db: Calibrated VV backscatter in dB.
        vh_db: Calibrated VH backscatter in dB.
        validity_mask: Explicit boolean validity mask on the shared grid.

    Returns:
        Backscatter arrays, their linear-power conversions, the VH/VV linear
        ratio, and the effective valid mask. Invalid cells are NaN.

    Raises:
        ValueError: If arrays are empty, shapes differ, or the mask is invalid.
    """
    vv = np.array(vv_db, dtype=np.float32, copy=True)
    vh = np.array(vh_db, dtype=np.float32, copy=True)
    if not vv.shape or any(size == 0 for size in vv.shape):
        raise ValueError("backscatter arrays must have non-empty dimensions")
    if vv.shape != vh.shape:
        raise ValueError("VV and VH arrays must have the same shape")
    if not isinstance(validity_mask, np.ndarray) or validity_mask.dtype != np.bool_:
        raise ValueError("validity_mask must be a NumPy boolean array")
    if validity_mask.shape != vv.shape:
        raise ValueError("validity_mask must have the same shape as backscatter")

    valid = validity_mask & np.isfinite(vv) & np.isfinite(vh)
    vv_linear = db_to_linear_power(vv)
    vh_linear = db_to_linear_power(vh)
    ratio = db_to_linear_power(vh - vv)
    for array in (vv, vh, vv_linear, vh_linear, ratio):
        array[~valid] = np.nan

    return Sentinel1DualPolFeatures(
        vv_db=vv,
        vh_db=vh,
        vv_linear=vv_linear,
        vh_linear=vh_linear,
        vh_to_vv_linear_ratio=ratio,
        valid_mask=valid,
    )
