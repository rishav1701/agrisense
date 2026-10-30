"""Software-only classifier tests using explicitly synthetic samples."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from src.contracts.schemas import ClassDefinition, ProvenanceReference
from src.models.classifier import (
    VerifiedTrainingContext,
    create_random_forest,
    fit_crop_classifier,
    load_crop_classifier,
    predict_crop_raster,
    save_crop_classifier,
)


class SyntheticProbabilisticClassifier:
    """Tiny deterministic estimator stub for software tests, not a model."""

    def fit(self, features, labels):
        """Record the training rows to check split isolation."""
        self.fitted_features = np.array(features, copy=True)
        self.fitted_labels = np.array(labels, copy=True)
        self.classes_ = np.unique(labels)
        return self

    def predict_proba(self, features):
        """Return synthetic probabilities for software-path tests only."""
        probabilities = np.zeros((len(features), len(self.classes_)), dtype=np.float64)
        for row, feature in enumerate(features):
            preferred = int(feature[0] > 0.5)
            probabilities[row, preferred] = 0.8
            probabilities[row, 1 - preferred] = 0.2
        return probabilities


def training_context(*, labels_verified=True):
    """Return synthetic software-test provenance, never field evidence."""
    return VerifiedTrainingContext(
        labels_verified=labels_verified,
        label_sources=(
            ProvenanceReference(
                reference_id="synthetic-test-labels",
                description="Synthetic software-test labels only",
                limitations=["Not field observations or scientific evidence"],
            ),
        ),
        label_protocol="synthetic test fixture",
        aoi_reference="synthetic test coordinates only",
        season_reference="synthetic test interval only",
        use_terms_reference="test-only synthetic data",
        split_design=ProvenanceReference(
            reference_id="synthetic-group-split",
            description="Synthetic software-test group split",
            limitations=["Not an evaluation design for scientific claims"],
        ),
    )


def class_map():
    """Return explicitly synthetic software-test class definitions."""
    return (
        ClassDefinition(
            class_id=0,
            class_name="Synthetic A",
            label_source_reference="synthetic-test-labels",
        ),
        ClassDefinition(
            class_id=1,
            class_name="Synthetic B",
            label_source_reference="synthetic-test-labels",
        ),
    )


def fit_test_model(*, estimator=None, context=None, groups=None):
    """Fit the stub with explicitly synthetic software-test arrays."""
    features = np.array(
        [[0.1, 1.0], [0.9, 1.1], [0.2, 0.9], [0.8, 1.2], [0.3, 1.0], [0.7, 1.0]],
        dtype=np.float32,
    )
    labels = np.array([0, 1, 0, 1, 0, 1], dtype=np.int32)
    group_values = np.array(groups or ["a", "b", "c", "d", "e", "f"])
    partitions = np.array(["train", "train", "train", "train", "validation", "test"])
    model = estimator if estimator is not None else SyntheticProbabilisticClassifier()
    return fit_crop_classifier(
        estimator=model,
        features=features,
        labels=labels,
        spatial_groups=group_values,
        partitions=partitions,
        class_map=class_map(),
        feature_names=("synthetic_ndvi", "synthetic_vh"),
        training_context=context or training_context(),
    )


class CropClassifierTests(unittest.TestCase):
    """Check software guardrails, not model quality or scientific results."""

    def test_fit_uses_only_train_groups_and_prediction_marks_missing_pixels(self):
        estimator = SyntheticProbabilisticClassifier()
        model = fit_test_model(estimator=estimator)
        self.assertEqual(estimator.fitted_features.shape, (4, 2))
        self.assertTrue(np.all(np.isin(estimator.fitted_labels, [0, 1])))

        raster_features = np.array(
            [[[0.1, 1.0], [0.9, 1.0]], [[np.nan, 1.0], [0.2, 1.0]]],
            dtype=np.float32,
        )
        result = predict_crop_raster(
            model=model,
            features=raster_features,
            validity_mask=np.ones((2, 2), dtype=np.bool_),
            feature_names=("synthetic_ndvi", "synthetic_vh"),
        )

        np.testing.assert_array_equal(result.class_ids, [[0, 1], [-1, 0]])
        self.assertFalse(result.valid_mask[1, 0])
        self.assertTrue(np.isnan(result.predictive_entropy_nats[1, 0]))
        self.assertIn("not a calibrated confidence", result.limitations[1])

    def test_fit_rejects_unverified_labels_and_spatial_leakage(self):
        with self.assertRaisesRegex(ValueError, "requires verified labels"):
            fit_test_model(context=training_context(labels_verified=False))
        with self.assertRaisesRegex(ValueError, "must not cross data partitions"):
            fit_test_model(groups=["a", "b", "c", "d", "a", "f"])

    def test_inference_rejects_changed_feature_order(self):
        model = fit_test_model()
        with self.assertRaisesRegex(ValueError, "feature names/order"):
            predict_crop_raster(
                model=model,
                features=np.ones((1, 1, 2), dtype=np.float32),
                validity_mask=np.ones((1, 1), dtype=np.bool_),
                feature_names=("synthetic_vh", "synthetic_ndvi"),
            )

    def test_random_forest_persistence_preserves_synthetic_inference(self):
        estimator = create_random_forest(
            n_estimators=5,
            max_features=2,
            min_samples_leaf=1,
            random_state=17,
            n_jobs=1,
        )
        model = fit_test_model(estimator=estimator)
        sample_features = np.array(
            [[[0.1, 1.0], [0.9, 1.0]]], dtype=np.float32
        )
        mask = np.ones((1, 2), dtype=np.bool_)
        before = predict_crop_raster(
            model=model,
            features=sample_features,
            validity_mask=mask,
            feature_names=("synthetic_ndvi", "synthetic_vh"),
        )

        with TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            model_path = Path(directory) / "synthetic-test-model.joblib"
            save_crop_classifier(model=model, path=model_path)
            restored = load_crop_classifier(path=model_path)

        after = predict_crop_raster(
            model=restored,
            features=sample_features,
            validity_mask=mask,
            feature_names=("synthetic_ndvi", "synthetic_vh"),
        )
        np.testing.assert_array_equal(after.class_ids, before.class_ids)
        np.testing.assert_allclose(
            after.max_class_probability, before.max_class_probability
        )


if __name__ == "__main__":
    unittest.main()
