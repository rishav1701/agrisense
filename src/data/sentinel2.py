"""Sentinel-2 spectral-index calculations for caller-prepared reflectance.

These functions do not acquire imagery, apply cloud masks, resample bands, or
infer scale factors. Callers must provide reflectance-scaled arrays and an
explicit validity mask, then record upstream processing in the CON-03 manifest.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatRaster = NDArray[np.float32]
BoolRaster = NDArray[np.bool_]


@dataclass(frozen=True)
class VegetationIndices:
    """Vegetation index rasters and their independent valid-pixel masks.

    ``ndvi_valid`` and ``evi_valid`` include the caller-provided validity mask,
    finite input checks, and each equation's non-zero-denominator check.
    Invalid output pixels are represented by NaN.
    """

    ndvi: FloatRaster
    evi: FloatRaster
    ndvi_valid: BoolRaster
    evi_valid: BoolRaster


def compute_vegetation_indices(
    *,
    blue: NDArray[np.floating],
    red: NDArray[np.floating],
    nir: NDArray[np.floating],
    validity_mask: BoolRaster,
) -> VegetationIndices:
    """Calculate NDVI and EVI from reflectance-scaled Sentinel-2 bands.

    Uses ``NDVI = (NIR - RED) / (NIR + RED)`` and
    ``EVI = 2.5 * (NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1)``. The EVI
    additive constant assumes the inputs are scaled to unitless reflectance.
    This function deliberately requires an explicit validity mask and does
    not apply a cloud/shadow policy or infer a source scale factor.

    Args:
        blue: Reflectance-scaled Sentinel-2 B02 array.
        red: Reflectance-scaled Sentinel-2 B04 array.
        nir: Reflectance-scaled Sentinel-2 B08 array.
        validity_mask: Boolean mask selected by the caller. True means the
            input pixel is eligible for calculation.

    Returns:
        NDVI and EVI arrays (float32), with separate boolean validity masks.
        Invalid values are NaN; no imputation is performed.

    Raises:
        ValueError: If arrays are empty, shapes differ, or the validity mask
            is not boolean with the same shape.
    """
    bands = {
        "blue": np.asarray(blue, dtype=np.float32),
        "red": np.asarray(red, dtype=np.float32),
        "nir": np.asarray(nir, dtype=np.float32),
    }
    shape = bands["blue"].shape
    if not shape or any(size == 0 for size in shape):
        raise ValueError("reflectance arrays must have non-empty dimensions")
    if any(band.shape != shape for band in bands.values()):
        raise ValueError("blue, red, and nir arrays must have the same shape")
    if not isinstance(validity_mask, np.ndarray) or validity_mask.dtype != np.bool_:
        raise ValueError("validity_mask must be a NumPy boolean array")
    if validity_mask.shape != shape:
        raise ValueError("validity_mask must have the same shape as the bands")

    blue_array = bands["blue"]
    red_array = bands["red"]
    nir_array = bands["nir"]
    finite_inputs = (
        np.isfinite(blue_array) & np.isfinite(red_array) & np.isfinite(nir_array)
    )
    numerator = nir_array - red_array

    ndvi_denominator = nir_array + red_array
    ndvi_valid = validity_mask & finite_inputs & (ndvi_denominator != 0)
    ndvi = np.full(shape, np.nan, dtype=np.float32)
    np.divide(numerator, ndvi_denominator, out=ndvi, where=ndvi_valid)

    evi_denominator = nir_array + 6.0 * red_array - 7.5 * blue_array + 1.0
    evi_valid = validity_mask & finite_inputs & (evi_denominator != 0)
    evi = np.full(shape, np.nan, dtype=np.float32)
    np.divide(
        2.5 * numerator,
        evi_denominator,
        out=evi,
        where=evi_valid,
    )
    return VegetationIndices(
        ndvi=ndvi,
        evi=evi,
        ndvi_valid=ndvi_valid,
        evi_valid=evi_valid,
    )
