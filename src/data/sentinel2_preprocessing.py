"""Preprocess aligned Sentinel-2 SR bands using an explicit SCL policy.

Inputs are arrays already extracted from a source product and aligned to one
grid. This module does not download data, apply a geospatial warp, or resample
the 20 m Scene Classification Layer (SCL) to 10 m reflectance bands.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from src.data.sentinel2 import VegetationIndices, compute_vegetation_indices

FloatArray = NDArray[np.float32]
BoolArray = NDArray[np.bool_]
IntArray = NDArray[np.integer]

SENTINEL2_SR_SCALE = 0.0001
DEFAULT_EXCLUDED_SCL_CLASSES = frozenset({0, 1, 3, 7, 8, 9, 10, 11})


@dataclass(frozen=True)
class Sentinel2Scene:
    """Scaled reflectance, SCL validity mask, and spectral indices."""

    blue_reflectance: FloatArray
    red_reflectance: FloatArray
    nir_reflectance: FloatArray
    validity_mask: BoolArray
    indices: VegetationIndices
    scale_factor: float
    excluded_scl_classes: frozenset[int]


def preprocess_sentinel2_scene(
    *,
    blue_dn: NDArray[np.number],
    red_dn: NDArray[np.number],
    nir_dn: NDArray[np.number],
    scl: IntArray,
    source_valid_mask: BoolArray,
    scale_factor: float = SENTINEL2_SR_SCALE,
    excluded_scl_classes: frozenset[int] = DEFAULT_EXCLUDED_SCL_CLASSES,
) -> Sentinel2Scene:
    """Scale aligned Sentinel-2 SR bands, mask SCL classes, and derive indices.

    Args:
        blue_dn: B02 stored digital-number array.
        red_dn: B04 stored digital-number array.
        nir_dn: B08 stored digital-number array.
        scl: SCL class array already aligned to the reflectance grid. This
            function will reject a different shape instead of resampling it.
        source_valid_mask: Boolean mask combining the source's band masks and
            any upstream validity conditions. True means valid source pixels.
        scale_factor: Reflectance scale for the provided product. The default
            ``0.0001`` is for Sentinel-2 SR Harmonized stored band values.
        excluded_scl_classes: SCL codes excluded from the output mask. The
            default excludes no-data, defective, cloud-shadow, unclassified,
            cloud, cirrus, and snow/ice classes. Water and dark-area classes
            remain eligible; callers may supply another documented policy.

    Returns:
        Scaled float32 B02/B04/B08 reflectance, a boolean valid mask, and
        NDVI/EVI arrays whose invalid cells are NaN.

    Raises:
        ValueError: If band/SCL/mask shapes differ, inputs are empty, the SCL
            dtype is not integer, the validity mask is not boolean, or the
            scale/policy is invalid.
    """
    bands = {
        "blue_dn": np.asarray(blue_dn),
        "red_dn": np.asarray(red_dn),
        "nir_dn": np.asarray(nir_dn),
    }
    shape = bands["blue_dn"].shape
    if not shape or any(size == 0 for size in shape):
        raise ValueError("reflectance arrays must have non-empty dimensions")
    if any(array.shape != shape for array in bands.values()):
        raise ValueError("B02, B04, and B08 arrays must have the same shape")
    if any(not np.issubdtype(array.dtype, np.number) for array in bands.values()):
        raise ValueError("reflectance bands must be numeric arrays")

    scl_array = np.asarray(scl)
    if scl_array.shape != shape:
        raise ValueError(
            "SCL must already be aligned to the reflectance grid; "
            "resample it explicitly before preprocessing"
        )
    if not np.issubdtype(scl_array.dtype, np.integer):
        raise ValueError("SCL must contain integer class codes")
    if np.any((scl_array < 0) | (scl_array > 11)):
        raise ValueError("SCL class codes must be between 0 and 11")
    if not isinstance(source_valid_mask, np.ndarray):
        raise ValueError("source_valid_mask must be a NumPy boolean array")
    if source_valid_mask.dtype != np.bool_ or source_valid_mask.shape != shape:
        raise ValueError(
            "source_valid_mask must be boolean and match the reflectance shape"
        )
    if (
        isinstance(scale_factor, bool)
        or not isinstance(scale_factor, (int, float))
        or not np.isfinite(scale_factor)
        or scale_factor <= 0
    ):
        raise ValueError("scale_factor must be a positive finite number")
    if not isinstance(excluded_scl_classes, frozenset):
        raise ValueError("excluded_scl_classes must be a frozenset of integers")
    if any(
        isinstance(class_code, bool) or not isinstance(class_code, int)
        for class_code in excluded_scl_classes
    ):
        raise ValueError("excluded_scl_classes must contain only integers")

    reflectance = {
        name: (array.astype(np.float32, copy=False) * np.float32(scale_factor))
        for name, array in bands.items()
    }
    scl_valid = ~np.isin(scl_array, tuple(excluded_scl_classes))
    finite_reflectance = np.logical_and.reduce(
        [np.isfinite(array) for array in reflectance.values()]
    )
    valid = source_valid_mask & scl_valid & finite_reflectance
    for array in reflectance.values():
        array[~valid] = np.nan

    indices = compute_vegetation_indices(
        blue=reflectance["blue_dn"],
        red=reflectance["red_dn"],
        nir=reflectance["nir_dn"],
        validity_mask=valid,
    )
    return Sentinel2Scene(
        blue_reflectance=reflectance["blue_dn"],
        red_reflectance=reflectance["red_dn"],
        nir_reflectance=reflectance["nir_dn"],
        validity_mask=valid,
        indices=indices,
        scale_factor=float(scale_factor),
        excluded_scl_classes=excluded_scl_classes,
    )
