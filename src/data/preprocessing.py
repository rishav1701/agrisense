"""Assemble caller-prepared satellite variables into a traceable CON-03 stack.

This module validates array dimensions, timestamps, and declared metadata. It
does not acquire imagery, reproject/resample data, or verify geospatial
registration; those operations must be performed and documented upstream.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from typing import Mapping

import numpy as np
from numpy.typing import NDArray

from src.contracts.schemas import (
    ObservationStackManifest,
    SourceMetadata,
    TimeInterval,
    VariableMetadata,
)

FloatArray = NDArray[np.float32]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class SatelliteVariableInput:
    """One variable's caller-prepared time series and declared metadata.

    ``values`` and ``validity_mask`` have shape ``(time, row, column)``. Each
    variable may have its own acquisition times; no temporal interpolation or
    forced cross-sensor timestamp matching is performed.
    """

    values: NDArray[np.number]
    validity_mask: BoolArray
    timestamps: tuple[str, ...]
    source_id: str
    metadata: VariableMetadata


@dataclass(frozen=True)
class SatelliteFeatureStack:
    """Satellite arrays, effective masks, and their CON-03 manifest."""

    variables: Mapping[str, FloatArray]
    validity_masks: Mapping[str, BoolArray]
    valid_data_fraction: Mapping[str, float]
    manifest: ObservationStackManifest


def _utc_key(value: str) -> datetime:
    """Parse a contract-compatible date or UTC timestamp for interval checks."""
    try:
        if "T" not in value:
            parsed_date = date.fromisoformat(value)
            if parsed_date.isoformat() != value:
                raise ValueError
            return datetime.combine(parsed_date, time.min, tzinfo=timezone.utc)
        candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(f"invalid ISO date/timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(None):
        raise ValueError(f"timestamp must specify UTC: {value!r}")
    return parsed


def assemble_satellite_stack(
    *,
    stack_id: str,
    variables: tuple[SatelliteVariableInput, ...],
    sources: tuple[SourceMetadata, ...],
    requested_interval: TimeInterval,
    analysis_crs: str,
    grid_transform: tuple[float, float, float, float, float, float],
    aoi_geometry: dict | None,
    processing_version: str,
) -> SatelliteFeatureStack:
    """Validate and assemble aligned satellite variables without resampling.

    The declared CRS, transform and AOI are carried through to CON-03. The
    supplied transform is metadata, not independently checked against arrays
    or source files. ``aoi_geometry=None`` is allowed for AOI-independent
    software work and is explicitly recorded as missing in the manifest.

    Args:
        stack_id: Stable identifier for this processing output.
        variables: Non-empty per-variable data, mask, time and metadata inputs.
        sources: Non-empty source records; each input references one source id.
        requested_interval: Start-inclusive, end-exclusive interval.
        analysis_crs: Declared CRS identifier, for example an EPSG code.
        grid_transform: Six affine coefficients for the common spatial grid.
        aoi_geometry: Verified GeoJSON polygon, or ``None`` when unavailable.
        processing_version: Caller-supplied code/configuration version.

    Returns:
        A stack with invalid/non-finite cells represented by NaN and false mask.

    Raises:
        ValueError: If arrays, times, source references, or grids are inconsistent.
        SchemaValidationError: If contract metadata is structurally invalid.
    """
    if not variables or not sources:
        raise ValueError("at least one variable and one source are required")
    source_map = {source.source_id: source for source in sources}
    if len(source_map) != len(sources):
        raise ValueError("source_id values must be unique")
    if len({item.metadata.name for item in variables}) != len(variables):
        raise ValueError("variable names must be unique")

    start, end = _utc_key(requested_interval.start), _utc_key(requested_interval.end)
    output_values: dict[str, FloatArray] = {}
    output_masks: dict[str, BoolArray] = {}
    spatial_shape: tuple[int, int] | None = None
    variable_metadata: list[VariableMetadata] = []
    valid_data_fraction: dict[str, float] = {}
    referenced_sources: set[str] = set()

    for item in variables:
        if item.source_id not in source_map:
            raise ValueError(f"unknown source_id: {item.source_id}")
        referenced_sources.add(item.source_id)
        if item.metadata.source_reference != item.source_id:
            raise ValueError("variable source_reference must match its source_id")
        values = np.asarray(item.values)
        mask = item.validity_mask
        if values.ndim != 3 or any(size == 0 for size in values.shape):
            raise ValueError("each variable must have non-empty (time, row, column) data")
        if not np.issubdtype(values.dtype, np.number) or np.iscomplexobj(values):
            raise ValueError("variable values must be real numeric arrays")
        if not isinstance(mask, np.ndarray) or mask.dtype != np.bool_:
            raise ValueError("validity_mask must be a NumPy boolean array")
        if mask.shape != values.shape:
            raise ValueError("validity_mask must match variable data shape")
        if spatial_shape is None:
            spatial_shape = (values.shape[1], values.shape[2])
        elif (values.shape[1], values.shape[2]) != spatial_shape:
            raise ValueError("all variables must use the same declared spatial shape")
        if len(item.timestamps) != values.shape[0]:
            raise ValueError("timestamps count must match the variable time axis")
        if tuple(item.timestamps) != tuple(source_map[item.source_id].timestamps):
            raise ValueError("timestamps must match the referenced source metadata")
        parsed_times = [_utc_key(timestamp) for timestamp in item.timestamps]
        if parsed_times != sorted(parsed_times) or len(set(parsed_times)) != len(parsed_times):
            raise ValueError("timestamps must be unique and sorted chronologically")
        if any(timestamp < start or timestamp >= end for timestamp in parsed_times):
            raise ValueError("timestamps must fall within the requested interval")

        with np.errstate(over="ignore", invalid="ignore"):
            copied = values.astype(np.float32, copy=True)
        effective_mask = mask.copy() & np.isfinite(copied)
        copied[~effective_mask] = np.nan
        output_values[item.metadata.name] = copied
        output_masks[item.metadata.name] = effective_mask
        valid_data_fraction[item.metadata.name] = float(np.mean(effective_mask))
        variable_metadata.append(item.metadata)

    assert spatial_shape is not None
    if referenced_sources != set(source_map):
        raise ValueError("each declared source must be referenced by a variable")
    manifest = ObservationStackManifest(
        stack_id=stack_id,
        analysis_crs=analysis_crs,
        grid_transform=grid_transform,
        grid_shape=spatial_shape,
        aoi_geometry=aoi_geometry,
        sources=list(sources),
        variables=variable_metadata,
        requested_interval=requested_interval,
        processing_version=processing_version,
        limitations=[
            "Assembly validates declared metadata and array shapes; it does not independently verify geospatial registration.",
            "No acquisition, reprojection, resampling, temporal interpolation, or gap filling is performed.",
            "Native/effective resolution and upstream processing must be truthfully supplied in source metadata.",
        ],
        missing_reasons=(
            {"aoi_geometry": "No verified AOI geometry was supplied."}
            if aoi_geometry is None
            else {}
        ),
    )
    return SatelliteFeatureStack(
        output_values, output_masks, valid_data_fraction, manifest
    )
