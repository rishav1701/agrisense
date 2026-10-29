"""Validation and serialization tests for CON-01 through CON-09.

Every payload in this module is an artificial software-test object. None is a
real observation, source record, model result, or scientific measurement.
"""

import unittest

from src.contracts.schemas import (
    CanalCommandSummary,
    ClassDefinition,
    ContractModel,
    CropClassificationResult,
    CropEvapotranspirationEstimate,
    FieldWaterBalanceEstimate,
    ObservationStackManifest,
    PhenologyEstimate,
    ProbabilityRaster,
    ProvenanceReference,
    SchemaValidationError,
    SourceMetadata,
    SourceObservationQuery,
    StressIndicator,
    StudyAreaQuery,
    TimeInterval,
    VariableMetadata,
    WaterBalanceTerm,
    deserialize_contract,
    serialize_contract,
)

SYNTHETIC_POLYGON = {
    "type": "Polygon",
    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
}
SYNTHETIC_PROVENANCE = ProvenanceReference(
    reference_id="synthetic-test-reference",
    description="Artificial software-test provenance only.",
    limitations=["Not a real source or study design."],
)


def _contract_samples() -> list[ContractModel]:
    """Return artificial examples of each contract for serialization tests."""
    interval = TimeInterval(start="2020-01-01", end="2020-02-01")
    source = SourceMetadata(
        source_id="synthetic-source",
        collection_id="synthetic-collection",
        version="fixture-v1",
        timestamps=["2020-01-02T00:00:00Z"],
        native_grid="synthetic-grid",
        native_resolution_m=1.0,
        quality_mask_reference="synthetic-mask",
    )
    variable = VariableMetadata(
        name="synthetic-variable",
        units="synthetic-unit",
        scale=1.0,
        source_reference="synthetic-source",
        time_support="fabricated test timestamp",
        resampling_method=None,
        mask_reference="synthetic-mask",
        missing_reasons={"resampling_method": "No resampling occurs in this fixture."},
    )
    class_definition = ClassDefinition(
        class_id=1,
        class_name="synthetic-class",
        label_source_reference="synthetic-test-label-source",
    )
    missing_et = {
        "kc_value": "No crop coefficient is represented in this test.",
        "et0_value": "No meteorological input is represented in this test.",
        "etc_value": "No ETc is calculated in this test.",
        "precipitation_value": "No precipitation input is represented in this test.",
    }
    missing_summary = {
        "statistic_value": "No zonal statistic is calculated in this test.",
        "contributing_area_value": "No real contributing area is represented.",
        "contributing_area_unit": "No area unit is represented.",
        "valid_data_area_value": "No valid-data area is calculated.",
        "valid_data_area_unit": "No valid-data area unit is represented.",
    }
    return [
        StudyAreaQuery(
            query_id="synthetic-query",
            aoi_geometry=SYNTHETIC_POLYGON,
            start_date="2020-01-01",
            end_date="2020-02-01",
        ),
        SourceObservationQuery(
            collection_id="synthetic-collection",
            start_date="2020-01-01",
            end_date="2020-02-01",
            geometry_geojson=SYNTHETIC_POLYGON,
            cloud_cover_percent=50,
            requested_bands=["synthetic-band"],
        ),
        ObservationStackManifest(
            stack_id="synthetic-stack",
            analysis_crs="synthetic-test-crs",
            grid_transform=(1, 0, 0, 0, -1, 0),
            grid_shape=(2, 2),
            aoi_geometry=SYNTHETIC_POLYGON,
            sources=[source],
            variables=[variable],
            requested_interval=interval,
            processing_version="fixture-v1",
            limitations=["Artificial software test only."],
        ),
        CropClassificationResult(
            model_id="synthetic-model",
            model_version="fixture-v1",
            class_raster="synthetic-test-asset",
            class_map=[class_definition],
            nodata_code=-1,
            feature_definition_version="fixture-v1",
            training_label_sources=[SYNTHETIC_PROVENANCE],
            split_design=SYNTHETIC_PROVENANCE,
            evaluation_metrics=None,
            probability_raster=ProbabilityRaster(
                asset_reference="synthetic-probability-asset",
                calibration_status="not calibrated; software fixture only",
                limitations=["Not model output."],
            ),
        ),
        PhenologyEstimate(
            spatial_reference="synthetic-test-cell",
            crop_class_id=None,
            estimate_time="2020-01-15",
            stage_code="unavailable",
            evidence_interval=interval,
            valid_observation_count=None,
            quality_state="insufficient_data",
            method="synthetic test placeholder",
            method_version="fixture-v1",
        ),
        StressIndicator(
            estimate_time="2020-01-15",
            indicator_id="synthetic-indicator",
            value=None,
            unit=None,
            method_reference="synthetic-test-method",
            source_observation_references=[],
            quality_state="insufficient_data",
            limitations=["No stress estimate is generated by this fixture."],
            reference_id="synthetic-test-reference",
            missing_reason="No real observations are present.",
        ),
        CropEvapotranspirationEstimate(
            interval=interval,
            kc_value=None,
            kc_source=None,
            et0_value=None,
            et0_unit=None,
            et0_source=None,
            etc_value=None,
            etc_unit=None,
            method_version="fixture-v1",
            input_quality="insufficient_data",
            limitations=["No ETc estimate is generated by this fixture."],
            precipitation_value=None,
            precipitation_unit=None,
            precipitation_method=None,
            missing_reasons=missing_et,
        ),
        FieldWaterBalanceEstimate(
            spatial_reference="synthetic-test-cell",
            interval=interval,
            terms=[
                WaterBalanceTerm(
                    name="synthetic-term",
                    value=None,
                    unit="mm per test interval",
                    source_or_method_reference="synthetic-test-method",
                    missing_reason="No balance input is present.",
                )
            ],
            method_version="fixture-v1",
            valid_data_coverage=None,
            assumptions=["Artificial test object only."],
            quality_state="insufficient_data",
            limitations=["No field water balance is calculated."],
            missing_reasons={"valid_data_coverage": "No observations are present."},
        ),
        CanalCommandSummary(
            command_id="synthetic-command",
            boundary_source="synthetic-test-boundary",
            interval=interval,
            statistic_name="synthetic-statistic",
            statistic_value=None,
            statistic_unit="synthetic-unit",
            contributing_area_value=None,
            contributing_area_unit=None,
            valid_data_area_value=None,
            valid_data_area_unit=None,
            aggregation_method_version="fixture-v1",
            source_estimate_references=["synthetic-test-estimate"],
            limitations=["No canal result or release advice is produced."],
            missing_reasons=missing_summary,
        ),
    ]


class ContractRoundTripTests(unittest.TestCase):
    """Ensure each contract round-trips through strict JSON and GeoJSON."""

    def test_all_nine_contracts_round_trip(self):
        self.assertEqual(len(_contract_samples()), 9)
        for model in _contract_samples():
            with self.subTest(contract=type(model).__name__):
                restored = deserialize_contract(type(model), serialize_contract(model))
                self.assertEqual(restored, model)

    def test_geojson_and_nested_models_round_trip(self):
        query = StudyAreaQuery(
            query_id="synthetic-query",
            aoi_geometry=SYNTHETIC_POLYGON,
            start_date="2020-01-01",
            end_date="2020-02-01",
        )
        restored = StudyAreaQuery.from_dict(query.to_dict())
        self.assertEqual(restored.aoi_geometry, SYNTHETIC_POLYGON)

    def test_null_metadata_requires_reason(self):
        with self.assertRaises(SchemaValidationError):
            SourceMetadata(
                source_id="synthetic-source",
                collection_id=None,
                version="fixture-v1",
                timestamps=[],
                native_grid="synthetic-grid",
                native_resolution_m=1,
                quality_mask_reference="synthetic-mask",
            )

    def test_unknown_json_fields_are_rejected(self):
        query = StudyAreaQuery(
            query_id="synthetic-query",
            aoi_geometry=SYNTHETIC_POLYGON,
            start_date="2020-01-01",
            end_date="2020-02-01",
        ).to_dict()
        query["unreviewed_field"] = "must fail"
        with self.assertRaises(SchemaValidationError):
            StudyAreaQuery.from_dict(query)


class ContractValidationTests(unittest.TestCase):
    """Reject malformed intervals, geometries, and unsupported semantics."""

    def test_study_area_requires_ordered_dates_and_closed_polygon(self):
        with self.assertRaises(SchemaValidationError):
            StudyAreaQuery(
                query_id="synthetic-query",
                aoi_geometry=SYNTHETIC_POLYGON,
                start_date="2020-02-01",
                end_date="2020-01-01",
            )
        open_polygon = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1]]],
        }
        with self.assertRaises(SchemaValidationError):
            StudyAreaQuery(
                query_id="synthetic-query",
                aoi_geometry=open_polygon,
                start_date="2020-01-01",
                end_date="2020-02-01",
            )

    def test_source_query_cloud_limit_and_utc_timestamp_are_validated(self):
        with self.assertRaises(SchemaValidationError):
            SourceObservationQuery(
                collection_id="synthetic-collection",
                start_date="2020-01-01",
                end_date="2020-02-01",
                geometry_geojson=SYNTHETIC_POLYGON,
                cloud_cover_percent=101,
            )
        with self.assertRaises(SchemaValidationError):
            TimeInterval(
                start="2020-01-01T00:00:00",
                end="2020-01-02T00:00:00",
            )

    def test_confidence_requires_documented_calculation(self):
        with self.assertRaises(SchemaValidationError):
            PhenologyEstimate(
                spatial_reference="synthetic-test-cell",
                crop_class_id=1,
                estimate_time="2020-01-15",
                stage_code="synthetic-stage",
                evidence_interval=TimeInterval("2020-01-01", "2020-02-01"),
                valid_observation_count=1,
                quality_state="test-only",
                method="synthetic method",
                method_version="fixture-v1",
                confidence=0.5,
            )

    def test_volume_requires_area_basis(self):
        with self.assertRaises(SchemaValidationError):
            FieldWaterBalanceEstimate(
                spatial_reference="synthetic-test-cell",
                interval=TimeInterval("2020-01-01", "2020-02-01"),
                terms=[
                    WaterBalanceTerm(
                        name="synthetic-term",
                        value=None,
                        unit="mm",
                        source_or_method_reference="synthetic-method",
                        missing_reason="No input.",
                    )
                ],
                method_version="fixture-v1",
                valid_data_coverage=0,
                assumptions=[],
                quality_state="insufficient_data",
                limitations=[],
                volume_m3=1,
            )

    def test_canal_valid_area_cannot_exceed_contributing_area(self):
        with self.assertRaises(SchemaValidationError):
            CanalCommandSummary(
                command_id="synthetic-command",
                boundary_source="synthetic-boundary",
                interval=TimeInterval("2020-01-01", "2020-02-01"),
                statistic_name="synthetic-statistic",
                statistic_value=0,
                statistic_unit="synthetic-unit",
                contributing_area_value=2,
                contributing_area_unit="ha",
                valid_data_area_value=3,
                valid_data_area_unit="ha",
                aggregation_method_version="fixture-v1",
                source_estimate_references=[],
                limitations=[],
            )


if __name__ == "__main__":
    unittest.main()
