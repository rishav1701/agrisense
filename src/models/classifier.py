"""Spatially guarded Random Forest training and raster inference.

This module provides software mechanics only. It does not verify label truth,
source permission, spatial registration, or scientific validity. A model fit is
refused unless the caller supplies an explicit verified-label attestation and
spatially disjoint train/validation/test assignments. No fitted model is
included in the repository or used by the presentation demo.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import numpy as np
from numpy.typing import NDArray

from src.contracts.schemas import ClassDefinition, ProvenanceReference

FloatArray = NDArray[np.float32]
BoolArray = NDArray[np.bool_]
IntArray = NDArray[np.int32]


class ProbabilisticClassifier(Protocol):
    """Minimal estimator interface required by this adapter."""

    classes_: NDArray[Any]

    def fit(
        self, features: NDArray[np.floating], labels: NDArray[np.integer]
    ) -> ProbabilisticClassifier:
        """Fit an estimator to the supplied training samples."""

    def predict_proba(self, features: NDArray[np.floating]) -> NDArray[np.floating]:
        """Return class probabilities in the estimator's ``classes_`` order."""


@dataclass(frozen=True)
class VerifiedTrainingContext:
    """Caller-provided provenance attestation required before model fitting.

    The fields are an auditable declaration, not independent verification by
    this package. A project reviewer must confirm the underlying source and
    terms before setting ``labels_verified`` to true.
    """

    labels_verified: bool
    label_sources: tuple[ProvenanceReference, ...]
    label_protocol: str
    aoi_reference: str
    season_reference: str
    use_terms_reference: str
    split_design: ProvenanceReference


@dataclass(frozen=True)
class FittedCropClassifier:
    """Fitted estimator together with its supported classes and provenance."""

    estimator: ProbabilisticClassifier
    class_map: tuple[ClassDefinition, ...]
    feature_names: tuple[str, ...]
    training_context: VerifiedTrainingContext


@dataclass(frozen=True)
class CropClassifierPrediction:
    """Per-pixel class, model-relative probability, and entropy arrays."""

    class_ids: IntArray
    max_class_probability: FloatArray
    predictive_entropy_nats: FloatArray
    valid_mask: BoolArray
    class_map: tuple[ClassDefinition, ...]
    limitations: tuple[str, ...]


def create_random_forest(
    *,
    n_estimators: int,
    max_features: str | int | float | None,
    min_samples_leaf: int,
    random_state: int,
    n_jobs: int | None,
) -> ProbabilisticClassifier:
    """Create a scikit-learn Random Forest with explicit caller parameters.

    Hyperparameters are required rather than silently selected because the
    project's approved scientific configuration is still data-dependent.

    Args:
        n_estimators: Number of trees to fit.
        max_features: Feature subset rule accepted by scikit-learn.
        min_samples_leaf: Minimum samples per terminal leaf.
        random_state: Reproducibility seed; not a scientific tuning claim.
        n_jobs: Parallel worker count, or ``None`` for the library default.

    Returns:
        An unfitted scikit-learn RandomForestClassifier.

    Raises:
        ImportError: If optional scientific dependencies are not installed.
        ValueError: If required integer parameters are invalid.
    """
    for name, value in (
        ("n_estimators", n_estimators),
        ("min_samples_leaf", min_samples_leaf),
        ("random_state", random_state),
    ):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{name} must be an integer")
    if n_estimators < 1 or min_samples_leaf < 1 or random_state < 0:
        raise ValueError(
            "n_estimators and min_samples_leaf must be positive; "
            "random_state must be non-negative"
        )
    if isinstance(max_features, bool):
        raise ValueError("max_features must be an explicit scikit-learn feature rule")
    if isinstance(max_features, int) and max_features < 1:
        raise ValueError("integer max_features must be positive")
    if isinstance(max_features, float) and not 0 < max_features <= 1:
        raise ValueError("float max_features must be in (0, 1]")
    if isinstance(max_features, str) and max_features not in {"sqrt", "log2"}:
        raise ValueError("string max_features must be 'sqrt' or 'log2'")
    if max_features is not None and not isinstance(max_features, (str, int, float)):
        raise ValueError("max_features must be an explicit scikit-learn feature rule")
    try:
        from sklearn.ensemble import RandomForestClassifier
    except ImportError as exc:
        raise ImportError(
            "Install the optional scientific dependencies from "
            "requirements-science.txt to create a Random Forest"
        ) from exc
    return RandomForestClassifier(
        n_estimators=n_estimators,
        max_features=max_features,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
        n_jobs=n_jobs,
    )


def fit_crop_classifier(
    *,
    estimator: ProbabilisticClassifier,
    features: NDArray[np.number],
    labels: NDArray[np.integer],
    spatial_groups: NDArray[Any],
    partitions: NDArray[Any],
    class_map: tuple[ClassDefinition, ...],
    feature_names: tuple[str, ...],
    training_context: VerifiedTrainingContext,
) -> FittedCropClassifier:
    """Fit using training partition only after structural gate checks.

    All samples sharing a spatial group must belong to the same partition.
    Validation and test rows are never passed to ``estimator.fit``. This
    function does not choose hyperparameters or report evaluation metrics.

    Args:
        estimator: An unfitted classifier implementing ``fit`` and
            ``predict_proba``; normally created with :func:`create_random_forest`.
        features: Real-valued feature matrix shaped ``(samples, features)``.
        labels: Integer class IDs for each sample.
        spatial_groups: Geographic block/field/village group ID per sample.
        partitions: ``train``, ``validation``, or ``test`` label per sample.
        class_map: Traceable supported classes and label-source references.
        feature_names: Ordered feature identifiers preserved at inference.
        training_context: Caller attestation and provenance for this dataset.

    Returns:
        Fitted estimator with class and training-source provenance.

    Raises:
        ValueError: If arrays, class IDs, gates, or split isolation are invalid.
    """
    if training_context.labels_verified is not True:
        raise ValueError("classifier fit requires verified labels")
    if not training_context.label_sources or not all(
        isinstance(source, ProvenanceReference)
        for source in training_context.label_sources
    ):
        raise ValueError("verified training context requires label source references")
    if not isinstance(training_context.split_design, ProvenanceReference):
        raise ValueError("verified training context requires a split-design reference")
    for name in (
        "label_protocol",
        "aoi_reference",
        "season_reference",
        "use_terms_reference",
    ):
        value = getattr(training_context, name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"training context requires {name}")
    if not class_map or not all(isinstance(item, ClassDefinition) for item in class_map):
        raise ValueError("class_map must contain supported verified classes")
    if (
        len(feature_names) == 0
        or len(feature_names) != len(set(feature_names))
        or any(not name.strip() for name in feature_names)
    ):
        raise ValueError("feature_names must be unique, non-empty identifiers")

    x = np.asarray(features)
    y = np.asarray(labels)
    groups = np.asarray(spatial_groups)
    split = np.asarray(partitions)
    if x.ndim != 2 or x.shape[0] == 0 or x.shape[1] == 0:
        raise ValueError("features must have non-empty (samples, features) shape")
    if x.shape[1] != len(feature_names):
        raise ValueError("feature_names count must match the feature matrix width")
    if not np.issubdtype(x.dtype, np.number) or np.iscomplexobj(x):
        raise ValueError("features must be real numeric values")
    if y.ndim != 1 or not np.issubdtype(y.dtype, np.integer):
        raise ValueError("labels must be a one-dimensional integer array")
    if any(array.ndim != 1 for array in (groups, split)):
        raise ValueError("spatial_groups and partitions must be one-dimensional")
    if any(array.shape[0] != x.shape[0] for array in (y, groups, split)):
        raise ValueError("features, labels, groups, and partitions must align")
    if not np.all(np.isfinite(x)):
        raise ValueError("training samples must not contain non-finite features")
    if any(
        item is None
        or str(item).strip() == ""
        or (isinstance(item, (float, np.floating)) and not np.isfinite(item))
        for item in groups
    ):
        raise ValueError("every sample requires a spatial group")
    if set(split.tolist()) != {"train", "validation", "test"}:
        raise ValueError("partitions must include train, validation, and test")
    if np.any(y < 0):
        raise ValueError("class IDs must be non-negative")

    group_partitions: dict[str, str] = {}
    for group, partition in zip(groups, split, strict=True):
        group_key = str(group)
        partition_key = str(partition)
        previous = group_partitions.setdefault(group_key, partition_key)
        if previous != partition_key:
            raise ValueError("spatial groups must not cross data partitions")

    class_ids = {item.class_id for item in class_map}
    if len(class_ids) != len(class_map):
        raise ValueError("class_map class IDs must be unique")
    class_names = [item.class_name.casefold() for item in class_map]
    if len(class_names) != len(set(class_names)):
        raise ValueError("class_map class names must be unique")
    label_source_ids = {
        source.reference_id for source in training_context.label_sources
    }
    if any(item.label_source_reference not in label_source_ids for item in class_map):
        raise ValueError("each class must reference a declared label source")
    train = split == "train"
    training_ids = set(int(value) for value in np.unique(y[train]))
    if not training_ids or training_ids != class_ids:
        raise ValueError("class_map must exactly match classes present in training data")
    if set(int(value) for value in np.unique(y)) - class_ids:
        raise ValueError("labels contain class IDs absent from class_map")

    estimator.fit(x[train], y[train])
    estimator_classes = tuple(int(value) for value in estimator.classes_)
    if set(estimator_classes) != class_ids:
        raise ValueError("fitted estimator classes do not match the declared class_map")
    return FittedCropClassifier(estimator, class_map, feature_names, training_context)


def predict_crop_raster(
    *,
    model: FittedCropClassifier,
    features: NDArray[np.number],
    validity_mask: BoolArray,
    feature_names: tuple[str, ...],
) -> CropClassifierPrediction:
    """Predict classes for valid raster pixels and compute model-relative uncertainty.

    Probabilities are not calibrated unless separately assessed. Predictive
    entropy is measured in natural-log units (nats). Invalid pixels receive
    class ID -1 and NaN probability/entropy values.

    Args:
        model: Fitted classifier with a declared class map.
        features: Real-valued array shaped ``(rows, columns, features)``.
        validity_mask: Boolean validity mask shaped ``(rows, columns)``.
        feature_names: Ordered feature identifiers; must match training order.

    Returns:
        Class IDs, maximum class probabilities, entropy, and effective mask.

    Raises:
        ValueError: If grid, mask, feature count, or probabilities are invalid.
    """
    values = np.asarray(features)
    mask = validity_mask
    if values.ndim != 3 or any(length == 0 for length in values.shape):
        raise ValueError("features must have non-empty (rows, columns, features) shape")
    if not isinstance(mask, np.ndarray) or mask.dtype != np.bool_:
        raise ValueError("validity_mask must be a NumPy boolean array")
    if mask.shape != values.shape[:2]:
        raise ValueError("validity_mask must match raster rows and columns")
    if not np.issubdtype(values.dtype, np.number) or np.iscomplexobj(values):
        raise ValueError("features must be real numeric values")
    if feature_names != model.feature_names or len(feature_names) != values.shape[2]:
        raise ValueError("inference feature names/order must match the fitted model")
    effective_mask = mask & np.all(np.isfinite(values), axis=2)
    rows, columns, feature_count = values.shape
    classes = tuple(int(value) for value in model.estimator.classes_)
    expected_classes = {item.class_id for item in model.class_map}
    if set(classes) != expected_classes:
        raise ValueError("estimator classes do not match the model class_map")
    class_raster = np.full((rows, columns), -1, dtype=np.int32)
    max_probability = np.full((rows, columns), np.nan, dtype=np.float32)
    entropy = np.full((rows, columns), np.nan, dtype=np.float32)
    if np.any(effective_mask):
        samples = values[effective_mask].reshape(-1, feature_count)
        probabilities = np.asarray(model.estimator.predict_proba(samples), dtype=np.float64)
        if probabilities.shape != (samples.shape[0], len(classes)):
            raise ValueError("predict_proba returned an incompatible shape")
        if (
            not np.all(np.isfinite(probabilities))
            or np.any(probabilities < 0)
            or not np.allclose(probabilities.sum(axis=1), 1.0, rtol=1e-5, atol=1e-7)
        ):
            raise ValueError("predict_proba must return finite normalized probabilities")
        class_order = np.asarray(classes, dtype=np.int32)
        predictions = class_order[np.argmax(probabilities, axis=1)]
        max_probability[effective_mask] = np.max(probabilities, axis=1).astype(np.float32)
        safe_probabilities = np.where(probabilities > 0, probabilities, 1.0)
        pixel_entropy = -np.sum(
            np.where(probabilities > 0, probabilities * np.log(safe_probabilities), 0.0),
            axis=1,
        )
        entropy[effective_mask] = pixel_entropy.astype(np.float32)
        class_raster[effective_mask] = predictions

    return CropClassifierPrediction(
        class_ids=class_raster,
        max_class_probability=max_probability,
        predictive_entropy_nats=entropy,
        valid_mask=effective_mask,
        class_map=model.class_map,
        limitations=(
            "This prediction is an estimate; field-level scientific validity is unestablished until independently evaluated.",
            "Maximum class probability is model-relative and is not a calibrated confidence score.",
            "Predictive entropy is model-relative uncertainty in nats and is not a validation metric.",
            "Spatial georeferencing, feature scaling, class-domain completeness, and source permissions are not checked here.",
        ),
    )


def save_crop_classifier(*, model: FittedCropClassifier, path: str | Path) -> None:
    """Persist a fitted model and its provenance with optional joblib.

    Args:
        model: Fitted model object produced by :func:`fit_crop_classifier`.
        path: Destination file path outside the source repository.

    Raises:
        ImportError: If optional scientific dependencies are not installed.
        ValueError: If the model object is not a fitted crop classifier.
    """
    if not isinstance(model, FittedCropClassifier):
        raise ValueError("model must be a FittedCropClassifier")
    try:
        import joblib
    except ImportError as exc:
        raise ImportError(
            "Install the optional scientific dependencies from "
            "requirements-science.txt to persist a model"
        ) from exc
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, target, compress=3)


def load_crop_classifier(*, path: str | Path) -> FittedCropClassifier:
    """Load a fitted model from a trusted local artifact only.

    Joblib uses pickle serialization. Loading an untrusted or user-uploaded
    artifact can execute arbitrary code; only load artifacts created and
    controlled by the project team.

    Args:
        path: Trusted model artifact path.

    Returns:
        The fitted crop classifier and its stored class/provenance metadata.

    Raises:
        ImportError: If optional scientific dependencies are not installed.
        ValueError: If the artifact is not a ``FittedCropClassifier``.
    """
    try:
        import joblib
    except ImportError as exc:
        raise ImportError(
            "Install the optional scientific dependencies from "
            "requirements-science.txt to load a model"
        ) from exc
    loaded = joblib.load(Path(path))
    if not isinstance(loaded, FittedCropClassifier):
        raise ValueError("artifact does not contain a FittedCropClassifier")
    return loaded
