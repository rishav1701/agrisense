"""Software tests for Copernicus STAC catalogue discovery."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from src.data.copernicus_stac import (
    DEFAULT_STAC_URL,
    SENTINEL2_L2A_COLLECTION,
    STACCatalogError,
    search_sentinel2_l2a,
)

GEOMETRY = {
    "type": "Polygon",
    "coordinates": [[[76.0, 17.0], [76.1, 17.0], [76.1, 17.1], [76.0, 17.0]]],
}


def item(item_id: str, acquisition_time: str) -> dict[str, object]:
    """Create explicitly synthetic catalogue metadata for software tests."""
    return {"id": item_id, "properties": {"datetime": acquisition_time}}


class CopernicusStacTests(unittest.TestCase):
    """Verify query construction, time semantics, and pagination controls."""

    @patch("src.data.copernicus_stac._request_json")
    def test_search_uses_public_collection_and_exclusive_end_date(
        self, request_json
    ) -> None:
        request_json.return_value = {
            "features": [
                item("inside", "2023-04-30T23:59:59Z"),
                item("at-end", "2023-05-01T00:00:00Z"),
            ],
            "links": [],
        }

        result = search_sentinel2_l2a(
            aoi_geometry=GEOMETRY,
            start_date="2023-02-01",
            end_date="2023-05-01",
            max_cloud_cover_percent=35,
        )

        self.assertEqual([record["id"] for record in result], ["inside"])
        request = request_json.call_args.kwargs
        self.assertEqual(request["url"], f"{DEFAULT_STAC_URL}/search")
        self.assertEqual(request["body"]["collections"], [SENTINEL2_L2A_COLLECTION])
        self.assertEqual(
            request["body"]["datetime"],
            "2023-02-01T00:00:00Z/2023-05-01T00:00:00Z",
        )
        self.assertEqual(request["body"]["query"]["eo:cloud_cover"]["lte"], 35.0)

    @patch("src.data.copernicus_stac._request_json")
    def test_search_follows_same_origin_next_page(self, request_json) -> None:
        request_json.side_effect = [
            {
                "features": [item("one", "2023-02-02T00:00:00Z")],
                "links": [{"rel": "next", "href": "/v1/search?page=2"}],
            },
            {"features": [item("two", "2023-03-02T00:00:00Z")], "links": []},
        ]

        result = search_sentinel2_l2a(
            aoi_geometry=GEOMETRY,
            start_date="2023-02-01",
            end_date="2023-04-01",
        )

        self.assertEqual([record["id"] for record in result], ["one", "two"])
        self.assertEqual(
            [entry.kwargs["url"] for entry in request_json.call_args_list],
            [f"{DEFAULT_STAC_URL}/search", f"{DEFAULT_STAC_URL}/search?page=2"],
        )
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")

    @patch("src.data.copernicus_stac._request_json")
    def test_search_rejects_cross_origin_pagination(self, request_json) -> None:
        request_json.return_value = {
            "features": [],
            "links": [{"rel": "next", "href": "https://untrusted.example/search"}],
        }

        with self.assertRaisesRegex(STACCatalogError, "changed the endpoint origin"):
            search_sentinel2_l2a(
                aoi_geometry=GEOMETRY,
                start_date="2023-02-01",
                end_date="2023-04-01",
            )

    @patch("src.data.copernicus_stac._request_json")
    def test_invalid_query_does_not_call_catalogue(self, request_json) -> None:
        with self.assertRaisesRegex(ValueError, "start_date must precede end_date"):
            search_sentinel2_l2a(
                aoi_geometry=GEOMETRY,
                start_date="2023-04-01",
                end_date="2023-02-01",
            )
        request_json.assert_not_called()

    def test_cloud_cover_rejects_boolean(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 0 and 100"):
            search_sentinel2_l2a(
                aoi_geometry=GEOMETRY,
                start_date="2023-02-01",
                end_date="2023-04-01",
                max_cloud_cover_percent=True,
            )


if __name__ == "__main__":
    unittest.main()
