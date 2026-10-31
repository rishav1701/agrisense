"""Software checks for the local readiness and study-area API."""

from __future__ import annotations

import unittest

from fastapi import HTTPException
from pydantic import ValidationError

from src.api.main import (
    StudyAreaRequest,
    health,
    readiness,
    validate_study_area,
)

VALID_POLYGON = {
    "type": "Polygon",
    "coordinates": [[[76.0, 17.0], [76.1, 17.0], [76.1, 17.1], [76.0, 17.0]]],
}


class StudyAreaApiTests(unittest.TestCase):
    """Check API structure validation without starting a server or querying data."""

    def test_health_and_readiness_do_not_claim_data_products(self) -> None:
        self.assertEqual(health(), {"status": "ok", "service": "agrisense-api"})
        response = readiness()
        self.assertEqual(response["status"], "foundation")
        self.assertIsNone(response["products"]["crop_map"])
        self.assertFalse(response["capabilities"]["crop_classification"])
        self.assertTrue(
            any("config/study_area.geojson" in item for item in response["limitations"])
        )

    def test_valid_geometry_returns_structural_validation_only(self) -> None:
        payload = StudyAreaRequest(
            aoi_geometry=VALID_POLYGON,
            start_date="2023-02-01",
            end_date="2023-05-01",
        )

        response = validate_study_area(payload)

        self.assertTrue(response.valid)
        self.assertFalse(response.accepted_for_acquisition)
        self.assertIn("No data was queried or saved", response.message)

    def test_invalid_date_interval_is_rejected(self) -> None:
        payload = StudyAreaRequest(
            aoi_geometry=VALID_POLYGON,
            start_date="2023-05-01",
            end_date="2023-02-01",
        )

        with self.assertRaises(HTTPException) as raised:
            validate_study_area(payload)

        self.assertEqual(raised.exception.status_code, 422)
        self.assertIn("start_date must precede end_date", raised.exception.detail)

    def test_unclosed_polygon_ring_is_rejected(self) -> None:
        payload = StudyAreaRequest(
            aoi_geometry={
                "type": "Polygon",
                "coordinates": [
                    [[76.0, 17.0], [76.1, 17.0], [76.1, 17.1], [76.0, 17.1]]
                ],
            },
            start_date="2023-02-01",
            end_date="2023-05-01",
        )

        with self.assertRaises(HTTPException) as raised:
            validate_study_area(payload)

        self.assertEqual(raised.exception.status_code, 422)
        self.assertIn("must be closed", raised.exception.detail)

    def test_boolean_buffer_is_not_accepted_as_a_number(self) -> None:
        with self.assertRaises(ValidationError):
            StudyAreaRequest.model_validate(
                {
                    "aoi_geometry": VALID_POLYGON,
                    "start_date": "2023-02-01",
                    "end_date": "2023-05-01",
                    "buffer_meters": True,
                }
            )


if __name__ == "__main__":
    unittest.main()
