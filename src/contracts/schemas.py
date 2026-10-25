"""Dataclass schemas and JSON serialization for AgriSense CON-01–CON-09.

The schemas enforce structural and provenance requirements from
``docs/API_CONTRACTS.md``. They do not approve scientific methods, validate
source truth, or replace full GIS topology checks.
"""

from __future__ import annotations

import json
import math
import types
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, TypeVar, Union, get_args, get_origin, get_type_hints


class SchemaValidationError(ValueError):
    """Raised when a contract payload violates its declared structure."""


TContract = TypeVar("TContract", bound="ContractModel")


def _require_text(name: str, value: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise SchemaValidationError(f"{name} must be a non-empty string")


def _require_number(name: str, value: float, *, minimum: float | None = None) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SchemaValidationError(f"{name} must be a number")
    if not math.isfinite(float(value)):
        raise SchemaValidationError(f"{name} must be finite")
    if minimum is not None and value < minimum:
        raise SchemaValidationError(f"{name} must be at least {minimum}")


def _require_int(name: str, value: int, *, minimum: int | None = None) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SchemaValidationError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise SchemaValidationError(f"{name} must be at least {minimum}")


def _require_string_list(name: str, values: list[str]) -> None:
    if not isinstance(values, list):
        raise SchemaValidationError(f"{name} must be a list of strings")
    for index, value in enumerate(values):
        _require_text(f"{name}[{index}]", value)


def _require_instance(
    name: str, value: Any, expected: type, *, optional: bool = False
) -> None:
    if optional and value is None:
        return
    if not isinstance(value, expected):
        raise SchemaValidationError(f"{name} must be a {expected.__name__}")


def _require_model_list(
    name: str, values: Any, expected: type, *, allow_empty: bool = True
) -> None:
    if not isinstance(values, list):
        raise SchemaValidationError(f"{name} must be a list")
    if not allow_empty and not values:
        raise SchemaValidationError(f"{name} must not be empty")
    for index, value in enumerate(values):
        _require_instance(f"{name}[{index}]", value, expected)


def _parse_date(name: str, value: str) -> date:
    _require_text(name, value)
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise SchemaValidationError(f"{name} must be an ISO date (YYYY-MM-DD)") from exc
    if parsed.isoformat() != value:
        raise SchemaValidationError(f"{name} must use YYYY-MM-DD format")
    return parsed


def _time_key(name: str, value: str) -> datetime:
    _require_text(name, value)
    if "T" not in value:
        parsed_date = _parse_date(name, value)
        return datetime.combine(parsed_date, datetime.min.time(), tzinfo=timezone.utc)
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise SchemaValidationError(f"{name} must be an ISO date or timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise SchemaValidationError(f"{name} timestamp must specify UTC")
    return parsed


def _validate_interval(start: str, end: str, *, name: str = "interval") -> None:
    if _time_key(f"{name}.start", start) >= _time_key(f"{name}.end", end):
        raise SchemaValidationError(f"{name}.start must precede {name}.end")


def _validate_position(position: Any, name: str) -> None:
    if not isinstance(position, (list, tuple)) or len(position) < 2:
        raise SchemaValidationError(f"{name} must contain longitude and latitude")
    longitude, latitude = position[:2]
    _require_number(f"{name}.longitude", longitude)
    _require_number(f"{name}.latitude", latitude)
    if not -180 <= longitude <= 180 or not -90 <= latitude <= 90:
        raise SchemaValidationError(f"{name} is outside EPSG:4326 coordinate bounds")


def _validate_ring(ring: Any, name: str) -> None:
    if not isinstance(ring, (list, tuple)) or len(ring) < 4:
        raise SchemaValidationError(f"{name} must have at least four positions")
    for index, position in enumerate(ring):
        _validate_position(position, f"{name}[{index}]")
    if list(ring[0]) != list(ring[-1]):
        raise SchemaValidationError(f"{name} must be closed")


def _validate_geojson_geometry(
    geometry: dict[str, Any], *, polygon_only: bool = False
) -> None:
    if not isinstance(geometry, dict):
        raise SchemaValidationError("geometry must be a GeoJSON object")
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates")
    allowed = {"Polygon", "MultiPolygon"} if polygon_only else {
        "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon",
        "MultiPolygon", "GeometryCollection",
    }
    if kind not in allowed:
        raise SchemaValidationError(f"geometry.type must be one of {sorted(allowed)}")
    if kind == "GeometryCollection":
        geometries = geometry.get("geometries")
        if not isinstance(geometries, (list, tuple)) or not geometries:
            raise SchemaValidationError(
                "GeometryCollection.geometries must be non-empty"
            )
        for index, member in enumerate(geometries):
            try:
                _validate_geojson_geometry(member)
            except SchemaValidationError as exc:
                raise SchemaValidationError(
                    f"invalid GeometryCollection member {index}: {exc}"
                ) from exc
        return
    if not isinstance(coordinates, (list, tuple)) or not coordinates:
        raise SchemaValidationError("geometry.coordinates must be non-empty")
    if kind == "Point":
        _validate_position(coordinates, "geometry.coordinates")
    elif kind == "MultiPoint":
        for index, point in enumerate(coordinates):
            _validate_position(point, f"geometry.coordinates[{index}]")
    elif kind == "LineString":
        if len(coordinates) < 2:
            raise SchemaValidationError("LineString needs at least two positions")
        for index, point in enumerate(coordinates):
            _validate_position(point, f"geometry.coordinates[{index}]")
    elif kind == "MultiLineString":
        if any(
            not isinstance(line, (list, tuple)) or len(line) < 2
            for line in coordinates
        ):
            raise SchemaValidationError(
                "each MultiLineString member needs two positions"
            )
        for line_index, line in enumerate(coordinates):
            for point_index, point in enumerate(line):
                _validate_position(
                    point, f"geometry.coordinates[{line_index}][{point_index}]"
                )
    elif kind == "Polygon":
        for index, ring in enumerate(coordinates):
            _validate_ring(ring, f"geometry.coordinates[{index}]")
    else:
        for polygon_index, polygon in enumerate(coordinates):
            if not isinstance(polygon, (list, tuple)) or not polygon:
                raise SchemaValidationError("each MultiPolygon member needs a ring")
            for ring_index, ring in enumerate(polygon):
                _validate_ring(
                    ring, f"geometry.coordinates[{polygon_index}][{ring_index}]"
                )


def _validate_missing_reasons(
    name: str, value: Any, reasons: dict[str, str], reason_key: str | None = None
) -> None:
    _validate_reason_map(reasons)
    if value is None:
        key = reason_key or name
        reason = reasons.get(key)
        if reason is None:
            raise SchemaValidationError(f"{name} is null without a missing-data reason")
        _require_text(f"missing_reasons[{key}]", reason)


def _validate_reason_map(reasons: Any) -> None:
    if not isinstance(reasons, dict):
        raise SchemaValidationError("missing_reasons must be an object")
    for key, reason in reasons.items():
        _require_text("missing_reasons key", key)
        _require_text(f"missing_reasons[{key}]", reason)


def _to_primitive(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {
            item.name: _to_primitive(getattr(value, item.name))
            for item in fields(value)
        }
    if isinstance(value, dict):
        return {str(key): _to_primitive(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_primitive(item) for item in value]
    return value


def _coerce(annotation: Any, value: Any, field_name: str) -> Any:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in (Union, types.UnionType):
        if value is None and type(None) in args:
            return None
        errors: list[str] = []
        for option in args:
            if option is type(None):
                continue
            try:
                return _coerce(option, value, field_name)
            except (SchemaValidationError, TypeError, ValueError) as exc:
                errors.append(str(exc))
        raise SchemaValidationError(f"{field_name} does not match any allowed type")
    if origin is list:
        if not isinstance(value, list):
            raise SchemaValidationError(f"{field_name} must be a list")
        return [
            _coerce(args[0], item, f"{field_name}[{index}]")
            for index, item in enumerate(value)
        ]
    if origin is tuple:
        if not isinstance(value, (list, tuple)):
            raise SchemaValidationError(f"{field_name} must be an array")
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(_coerce(args[0], item, field_name) for item in value)
        if len(value) != len(args):
            raise SchemaValidationError(f"{field_name} has the wrong number of items")
        return tuple(
            _coerce(item_type, item, field_name)
            for item_type, item in zip(args, value)
        )
    if origin is dict:
        if not isinstance(value, dict):
            raise SchemaValidationError(f"{field_name} must be an object")
        return {
            _coerce(args[0], key, f"{field_name}.key"): _coerce(
                args[1], item, f"{field_name}.{key}"
            )
            for key, item in value.items()
        }
    if isinstance(annotation, type) and issubclass(annotation, ContractModel):
        if isinstance(value, annotation):
            return value
        if not isinstance(value, dict):
            raise SchemaValidationError(f"{field_name} must be an object")
        return annotation.from_dict(value)
    if annotation is Any:
        return value
    if annotation is float and isinstance(value, int) and not isinstance(value, bool):
        return float(value)
    if annotation is not Any and not isinstance(value, annotation):
        raise SchemaValidationError(f"{field_name} has the wrong type")
    return value


def _build_model(model_type: type[TContract], payload: dict[str, Any]) -> TContract:
    if not isinstance(payload, dict):
        raise SchemaValidationError(f"{model_type.__name__} payload must be an object")
    model_fields = {item.name: item for item in fields(model_type)}
    unexpected = set(payload) - set(model_fields)
    if unexpected:
        raise SchemaValidationError(
            f"unexpected fields: {', '.join(sorted(unexpected))}"
        )
    hints = get_type_hints(model_type)
    values: dict[str, Any] = {}
    for name, item in model_fields.items():
        if name not in payload:
            if item.default is MISSING and item.default_factory is MISSING:
                raise SchemaValidationError(f"missing required field: {name}")
            continue
        values[name] = _coerce(hints[name], payload[name], name)
    return model_type(**values)


@dataclass
class ContractModel:
    """Base class for validated, JSON-compatible contract dataclasses."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize this contract model to a JSON-compatible dictionary."""
        return _to_primitive(self)

    def to_json(self) -> str:
        """Serialize this contract model to strict JSON."""
        return json.dumps(self.to_dict(), allow_nan=False, sort_keys=True)

    @classmethod
    def from_dict(cls: type[TContract], payload: dict[str, Any]) -> TContract:
        """Validate and construct this model from a dictionary."""
        return _build_model(cls, payload)

    @classmethod
    def from_json(cls: type[TContract], payload: str) -> TContract:
        """Parse strict JSON and validate it as this model."""
        try:
            decoded = json.loads(payload, parse_constant=_reject_json_constant)
        except (json.JSONDecodeError, TypeError) as exc:
            raise SchemaValidationError("payload is not valid JSON") from exc
        if not isinstance(decoded, dict):
            raise SchemaValidationError("contract JSON must contain an object")
        return _build_model(cls, decoded)


def _reject_json_constant(value: str) -> None:
    raise SchemaValidationError(f"non-standard JSON constant is not allowed: {value}")


def serialize_contract(model: ContractModel) -> str:
    """Serialize any AgriSense contract model as strict JSON."""
    if not isinstance(model, ContractModel):
        raise SchemaValidationError("model must inherit ContractModel")
    return model.to_json()


def deserialize_contract(model_type: type[TContract], payload: str) -> TContract:
    """Deserialize strict JSON into the requested AgriSense contract model."""
    if not isinstance(model_type, type) or not issubclass(model_type, ContractModel):
        raise SchemaValidationError("model_type must inherit ContractModel")
    return model_type.from_json(payload)


@dataclass
class TimeInterval(ContractModel):
    """ISO date or UTC timestamp interval with exclusive end semantics."""

    start: str
    end: str

    def __post_init__(self) -> None:
        _validate_interval(self.start, self.end)


@dataclass
class StudyAreaQuery(ContractModel):
    """CON-01 study area geometry and requested date interval."""

    query_id: str
    aoi_geometry: dict[str, Any]
    start_date: str
    end_date: str
    target_crs: str | None = None
    buffer_meters: float | None = None

    def __post_init__(self) -> None:
        _require_text("query_id", self.query_id)
        _validate_geojson_geometry(self.aoi_geometry, polygon_only=True)
        start = _parse_date("start_date", self.start_date)
        end = _parse_date("end_date", self.end_date)
        if start >= end:
            raise SchemaValidationError("start_date must precede end_date")
        if self.target_crs is not None:
            _require_text("target_crs", self.target_crs)
        if self.buffer_meters is not None:
            _require_number("buffer_meters", self.buffer_meters, minimum=0)


@dataclass
class SourceObservationQuery(ContractModel):
    """CON-02 collection query with provider-specific filters."""

    collection_id: str
    start_date: str
    end_date: str
    geometry_geojson: dict[str, Any]
    cloud_cover_percent: float | None = None
    orbit_pass: str | None = None
    polarization: list[str] = field(default_factory=list)
    requested_bands: list[str] = field(default_factory=list)
    provider_filters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_text("collection_id", self.collection_id)
        if _parse_date("start_date", self.start_date) >= _parse_date(
            "end_date", self.end_date
        ):
            raise SchemaValidationError("start_date must precede end_date")
        _validate_geojson_geometry(self.geometry_geojson, polygon_only=True)
        if self.cloud_cover_percent is not None:
            _require_number("cloud_cover_percent", self.cloud_cover_percent, minimum=0)
            if self.cloud_cover_percent > 100:
                raise SchemaValidationError("cloud_cover_percent must not exceed 100")
        if self.orbit_pass is not None:
            _require_text("orbit_pass", self.orbit_pass)
        _require_string_list("polarization", self.polarization)
        _require_string_list("requested_bands", self.requested_bands)
        if not isinstance(self.provider_filters, dict):
            raise SchemaValidationError("provider_filters must be an object")


@dataclass
class SourceMetadata(ContractModel):
    """CON-03 source identity, time support, and known native-grid metadata."""

    source_id: str
    collection_id: str | None
    version: str | None
    timestamps: list[str]
    native_grid: str | None
    native_resolution_m: float | None
    quality_mask_reference: str | None
    missing_reasons: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_text("source_id", self.source_id)
        for name in (
            "collection_id", "version", "native_grid", "quality_mask_reference"
        ):
            value = getattr(self, name)
            if value is not None:
                _require_text(name, value)
            else:
                _validate_missing_reasons(name, value, self.missing_reasons)
        if self.native_resolution_m is not None:
            _require_number("native_resolution_m", self.native_resolution_m, minimum=0)
        else:
            _validate_missing_reasons("native_resolution_m", None, self.missing_reasons)
        _require_string_list("timestamps", self.timestamps)
        for timestamp in self.timestamps:
            _time_key("timestamp", timestamp)
        _validate_reason_map(self.missing_reasons)


@dataclass
class VariableMetadata(ContractModel):
    """CON-03 variable units, scaling, source, time, and quality metadata."""

    name: str
    units: str | None
    scale: float | None
    source_reference: str
    time_support: str
    resampling_method: str | None
    mask_reference: str | None
    missing_reasons: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("name", "source_reference", "time_support"):
            _require_text(name, getattr(self, name))
        for name in ("units", "resampling_method", "mask_reference"):
            value = getattr(self, name)
            if value is None:
                _validate_missing_reasons(name, value, self.missing_reasons)
            else:
                _require_text(name, value)
        if self.scale is not None:
            _require_number("scale", self.scale)
        else:
            _validate_missing_reasons("scale", None, self.missing_reasons)
        _validate_reason_map(self.missing_reasons)


@dataclass
class ObservationStackManifest(ContractModel):
    """CON-03 observation stack manifest with modality-specific provenance."""

    stack_id: str
    analysis_crs: str | None
    grid_transform: tuple[float, float, float, float, float, float] | None
    grid_shape: tuple[int, int] | None
    aoi_geometry: dict[str, Any] | None
    sources: list[SourceMetadata]
    variables: list[VariableMetadata]
    requested_interval: TimeInterval
    processing_version: str
    limitations: list[str]
    missing_reasons: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_text("stack_id", self.stack_id)
        _require_text("processing_version", self.processing_version)
        _require_string_list("limitations", self.limitations)
        _require_model_list("sources", self.sources, SourceMetadata, allow_empty=False)
        _require_model_list(
            "variables", self.variables, VariableMetadata, allow_empty=False
        )
        _require_instance("requested_interval", self.requested_interval, TimeInterval)
        _validate_reason_map(self.missing_reasons)
        if self.analysis_crs is None:
            _validate_missing_reasons("analysis_crs", None, self.missing_reasons)
        else:
            _require_text("analysis_crs", self.analysis_crs)
        if self.grid_transform is None:
            _validate_missing_reasons("grid_transform", None, self.missing_reasons)
        else:
            if len(self.grid_transform) != 6:
                raise SchemaValidationError("grid_transform must have six numbers")
            for item in self.grid_transform:
                _require_number("grid_transform item", item)
        if self.grid_shape is None:
            _validate_missing_reasons("grid_shape", None, self.missing_reasons)
        else:
            if len(self.grid_shape) != 2:
                raise SchemaValidationError(
                    "grid_shape must have two positive integers"
                )
            for item in self.grid_shape:
                _require_int("grid_shape item", item, minimum=1)
        if self.aoi_geometry is None:
            _validate_missing_reasons("aoi_geometry", None, self.missing_reasons)
        else:
            _validate_geojson_geometry(self.aoi_geometry, polygon_only=True)
        if self.grid_transform is not None and self.grid_shape is None:
            raise SchemaValidationError("grid_transform requires grid_shape")


@dataclass
class ProvenanceReference(ContractModel):
    """Traceable source, method, label, or split-design reference."""

    reference_id: str
    description: str
    uri: str | None = None
    attribution: str | None = None
    terms: str | None = None
    limitations: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _require_text("reference_id", self.reference_id)
        _require_text("description", self.description)
        for name in ("uri", "attribution", "terms"):
            value = getattr(self, name)
            if value is not None:
                _require_text(name, value)
        _require_string_list("limitations", self.limitations)


@dataclass
class ClassDefinition(ContractModel):
    """Traceable crop class in a study-specific classifier codebook."""

    class_id: int
    class_name: str
    label_source_reference: str

    def __post_init__(self) -> None:
        _require_int("class_id", self.class_id)
        _require_text("class_name", self.class_name)
        _require_text("label_source_reference", self.label_source_reference)


@dataclass
class EvaluationMetric(ContractModel):
    """Computed metric with held-out source and sample-support provenance."""

    metric_name: str
    value: float
    data_source_reference: str
    support_count: int
    split_reference: str

    def __post_init__(self) -> None:
        _require_text("metric_name", self.metric_name)
        _require_number("value", self.value)
        _require_text("data_source_reference", self.data_source_reference)
        _require_int("support_count", self.support_count, minimum=1)
        _require_text("split_reference", self.split_reference)


@dataclass
class ProbabilityRaster(ContractModel):
    """Optional probability asset with calibration state and caveats."""

    asset_reference: str
    calibration_status: str
    limitations: list[str]

    def __post_init__(self) -> None:
        _require_text("asset_reference", self.asset_reference)
        _require_text("calibration_status", self.calibration_status)
        _require_string_list("limitations", self.limitations)


@dataclass
class CropClassificationResult(ContractModel):
    """CON-04 crop raster and model, class, split, and evaluation provenance."""

    model_id: str
    model_version: str
    class_raster: str
    class_map: list[ClassDefinition]
    nodata_code: int
    feature_definition_version: str
    training_label_sources: list[ProvenanceReference]
    split_design: ProvenanceReference
    evaluation_metrics: list[EvaluationMetric] | None = None
    probability_raster: ProbabilityRaster | None = None

    def __post_init__(self) -> None:
        for name in (
            "model_id", "model_version", "class_raster", "feature_definition_version"
        ):
            _require_text(name, getattr(self, name))
        _require_int("nodata_code", self.nodata_code)
        if not self.class_map:
            raise SchemaValidationError("class_map must contain supported classes")
        class_ids = [item.class_id for item in self.class_map]
        if len(class_ids) != len(set(class_ids)):
            raise SchemaValidationError("class_map class_id values must be unique")
        class_names = [item.class_name.casefold() for item in self.class_map]
        if len(class_names) != len(set(class_names)):
            raise SchemaValidationError("class_map class_name values must be unique")
        if not self.training_label_sources:
            raise SchemaValidationError("training_label_sources must not be empty")
        _require_model_list(
            "class_map", self.class_map, ClassDefinition, allow_empty=False
        )
        _require_model_list(
            "training_label_sources", self.training_label_sources, ProvenanceReference,
            allow_empty=False,
        )
        _require_instance("split_design", self.split_design, ProvenanceReference)
        if self.evaluation_metrics is not None:
            _require_model_list(
                "evaluation_metrics", self.evaluation_metrics, EvaluationMetric
            )
        _require_instance(
            "probability_raster", self.probability_raster,
            ProbabilityRaster, optional=True,
        )


@dataclass
class PhenologyEstimate(ContractModel):
    """CON-05 crop-specific stage estimate with evidence and quality state."""

    spatial_reference: str
    crop_class_id: int | None
    estimate_time: str
    stage_code: str
    evidence_interval: TimeInterval
    valid_observation_count: int | None
    quality_state: str
    method: str
    method_version: str
    confidence: float | None = None
    confidence_method: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "spatial_reference", "stage_code", "quality_state", "method",
            "method_version",
        ):
            _require_text(name, getattr(self, name))
        _time_key("estimate_time", self.estimate_time)
        _require_instance("evidence_interval", self.evidence_interval, TimeInterval)
        if self.crop_class_id is not None:
            _require_int("crop_class_id", self.crop_class_id)
        if self.valid_observation_count is not None:
            _require_int(
                "valid_observation_count", self.valid_observation_count, minimum=0
            )
        if self.confidence is not None:
            _require_number("confidence", self.confidence, minimum=0)
            if self.confidence > 1:
                raise SchemaValidationError("confidence must be at most 1")
            if self.confidence_method is None:
                raise SchemaValidationError(
                    "confidence requires a defined confidence_method"
                )
        if self.confidence_method is not None:
            _require_text("confidence_method", self.confidence_method)


@dataclass
class StressIndicator(ContractModel):
    """CON-06 candidate indicator with explicit uncertainty and limitations."""

    estimate_time: str
    indicator_id: str
    value: float | None
    unit: str | None
    method_reference: str
    source_observation_references: list[str]
    quality_state: str
    limitations: list[str]
    spatial_reference: str | None = None
    geometry: dict[str, Any] | None = None
    reference_id: str | None = None
    crop_class_id: int | None = None
    stage_code: str | None = None
    baseline_reference: str | None = None
    missing_reason: str | None = None

    def __post_init__(self) -> None:
        _time_key("estimate_time", self.estimate_time)
        for name in ("indicator_id", "method_reference", "quality_state"):
            _require_text(name, getattr(self, name))
        if not any((self.spatial_reference, self.geometry, self.reference_id)):
            raise SchemaValidationError(
                "a spatial reference, geometry, or reference_id is required"
            )
        if self.geometry is not None:
            _validate_geojson_geometry(self.geometry)
        for name in (
            "unit", "spatial_reference", "reference_id", "stage_code",
            "baseline_reference",
        ):
            value = getattr(self, name)
            if value is not None:
                _require_text(name, value)
        if self.value is None:
            _require_text("missing_reason", self.missing_reason or "")
        else:
            _require_number("value", self.value)
            if self.missing_reason is not None:
                raise SchemaValidationError(
                    "missing_reason is only valid when value is null"
                )
        if self.crop_class_id is not None:
            _require_int("crop_class_id", self.crop_class_id)
        _require_string_list(
            "source_observation_references", self.source_observation_references
        )
        _require_string_list("limitations", self.limitations)
        if self.value is not None and not self.source_observation_references:
            raise SchemaValidationError(
                "a computed indicator requires source observation references"
            )


@dataclass
class CropEvapotranspirationEstimate(ContractModel):
    """CON-07 interval ETc estimate and the provenance of its inputs."""

    interval: TimeInterval
    kc_value: float | None
    kc_source: str | None
    et0_value: float | None
    et0_unit: str | None
    et0_source: str | None
    etc_value: float | None
    etc_unit: str | None
    method_version: str
    input_quality: str
    limitations: list[str]
    crop_reference: str | None = None
    stage_reference: str | None = None
    precipitation_value: float | None = None
    precipitation_unit: str | None = None
    precipitation_method: str | None = None
    missing_reasons: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("method_version", "input_quality"):
            _require_text(name, getattr(self, name))
        _require_string_list("limitations", self.limitations)
        _require_instance("interval", self.interval, TimeInterval)
        _validate_reason_map(self.missing_reasons)
        for name in ("crop_reference", "stage_reference"):
            value = getattr(self, name)
            if value is not None:
                _require_text(name, value)
        for name in ("kc_value", "et0_value", "etc_value", "precipitation_value"):
            value = getattr(self, name)
            if value is None:
                _validate_missing_reasons(name, None, self.missing_reasons)
            else:
                _require_number(name, value)
        for name in (
            "kc_source", "et0_unit", "et0_source", "etc_unit",
            "precipitation_unit", "precipitation_method",
        ):
            value = getattr(self, name)
            if value is not None:
                _require_text(name, value)
        if self.kc_value is not None and self.kc_source is None:
            raise SchemaValidationError("kc_value requires kc_source")
        if self.et0_value is not None and (
            self.et0_unit is None or self.et0_source is None
        ):
            raise SchemaValidationError("et0_value requires et0_unit and et0_source")
        if self.etc_value is not None and self.etc_unit is None:
            raise SchemaValidationError("etc_value requires etc_unit")
        if self.precipitation_value is not None and (
            self.precipitation_unit is None or self.precipitation_method is None
        ):
            raise SchemaValidationError(
                "precipitation requires unit and method provenance"
            )


@dataclass
class WaterBalanceTerm(ContractModel):
    """Named water-balance term with a value or an explicit missing reason."""

    name: str
    value: float | None
    unit: str
    source_or_method_reference: str
    missing_reason: str | None = None

    def __post_init__(self) -> None:
        for name in ("name", "unit", "source_or_method_reference"):
            _require_text(name, getattr(self, name))
        if self.value is None:
            _require_text("missing_reason", self.missing_reason or "")
        else:
            _require_number("value", self.value)
            if self.missing_reason is not None:
                raise SchemaValidationError(
                    "missing_reason is only valid when value is null"
                )


@dataclass
class AreaBasis(ContractModel):
    """Explicit area and conversion basis for an area-derived volume."""

    area_value: float
    area_unit: str
    conversion_method: str

    def __post_init__(self) -> None:
        _require_number("area_value", self.area_value, minimum=0)
        _require_text("area_unit", self.area_unit)
        _require_text("conversion_method", self.conversion_method)


@dataclass
class FieldWaterBalanceEstimate(ContractModel):
    """CON-08 bounded depth balance with explicit assumptions and quality."""

    spatial_reference: str
    interval: TimeInterval
    terms: list[WaterBalanceTerm]
    method_version: str
    valid_data_coverage: float | None
    assumptions: list[str]
    quality_state: str
    limitations: list[str]
    volume_m3: float | None = None
    area_basis: AreaBasis | None = None
    missing_reasons: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("spatial_reference", "method_version", "quality_state"):
            _require_text(name, getattr(self, name))
        if not self.terms:
            raise SchemaValidationError("terms must contain at least one balance term")
        _require_instance("interval", self.interval, TimeInterval)
        _require_model_list("terms", self.terms, WaterBalanceTerm, allow_empty=False)
        _require_string_list("assumptions", self.assumptions)
        _require_string_list("limitations", self.limitations)
        _validate_reason_map(self.missing_reasons)
        if self.valid_data_coverage is None:
            _validate_missing_reasons("valid_data_coverage", None, self.missing_reasons)
        else:
            _require_number("valid_data_coverage", self.valid_data_coverage, minimum=0)
            if self.valid_data_coverage > 1:
                raise SchemaValidationError("valid_data_coverage must not exceed 1")
        if self.volume_m3 is not None:
            _require_number("volume_m3", self.volume_m3, minimum=0)
            if self.area_basis is None:
                raise SchemaValidationError("volume_m3 requires an explicit area_basis")
            _require_instance("area_basis", self.area_basis, AreaBasis)
        elif self.area_basis is not None:
                raise SchemaValidationError(
                    "area_basis is only used when volume_m3 is provided"
                )


@dataclass
class CanalCommandSummary(ContractModel):
    """CON-09 descriptive zonal summary; contains no operational release advice."""

    command_id: str
    boundary_source: str
    interval: TimeInterval
    statistic_name: str
    statistic_value: float | None
    statistic_unit: str
    contributing_area_value: float | None
    contributing_area_unit: str | None
    valid_data_area_value: float | None
    valid_data_area_unit: str | None
    aggregation_method_version: str
    source_estimate_references: list[str]
    limitations: list[str]
    missing_reasons: dict[str, str] = field(default_factory=dict)
    volume_m3: float | None = None
    volume_area_basis: AreaBasis | None = None

    def __post_init__(self) -> None:
        for name in (
            "command_id", "boundary_source", "statistic_name", "statistic_unit",
            "aggregation_method_version",
        ):
            _require_text(name, getattr(self, name))
        _require_string_list(
            "source_estimate_references", self.source_estimate_references
        )
        _require_string_list("limitations", self.limitations)
        _require_instance("interval", self.interval, TimeInterval)
        _validate_reason_map(self.missing_reasons)
        _require_model_list(
            "source_estimate_references", self.source_estimate_references,
            str, allow_empty=True,
        )
        for name in (
            "statistic_value", "contributing_area_value", "valid_data_area_value"
        ):
            value = getattr(self, name)
            if value is None:
                _validate_missing_reasons(name, None, self.missing_reasons)
            else:
                _require_number(
                    name, value, minimum=0 if name != "statistic_value" else None
                )
        for name in ("contributing_area_unit", "valid_data_area_unit"):
            value = getattr(self, name)
            if value is None:
                _validate_missing_reasons(name, None, self.missing_reasons)
            else:
                _require_text(name, value)
        if (
            self.valid_data_area_value is not None
            and self.contributing_area_value is not None
        ):
            if self.valid_data_area_unit != self.contributing_area_unit:
                raise SchemaValidationError(
                    "area values must use the same unit for comparison"
                )
            if self.valid_data_area_value > self.contributing_area_value:
                raise SchemaValidationError(
                    "valid_data_area_value cannot exceed contributing area"
                )
        if self.volume_m3 is not None:
            _require_number("volume_m3", self.volume_m3, minimum=0)
            if self.volume_area_basis is None:
                raise SchemaValidationError("volume_m3 requires an explicit area basis")
            _require_instance("volume_area_basis", self.volume_area_basis, AreaBasis)
        elif self.volume_area_basis is not None:
            raise SchemaValidationError("volume_area_basis requires volume_m3")


__all__ = [
    "AreaBasis",
    "CanalCommandSummary",
    "ClassDefinition",
    "ContractModel",
    "CropClassificationResult",
    "CropEvapotranspirationEstimate",
    "EvaluationMetric",
    "FieldWaterBalanceEstimate",
    "ObservationStackManifest",
    "PhenologyEstimate",
    "ProbabilityRaster",
    "ProvenanceReference",
    "SchemaValidationError",
    "SourceMetadata",
    "SourceObservationQuery",
    "StressIndicator",
    "StudyAreaQuery",
    "TimeInterval",
    "VariableMetadata",
    "WaterBalanceTerm",
    "deserialize_contract",
    "serialize_contract",
]
