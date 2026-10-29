"""Software tests for Copernicus STAC catalogue discovery."""

from __future__ import annotations

import unittest
import unittest.mock
from unittest.mock import patch

from src.data.copernicus_stac import (
    DEFAULT_STAC_URL,
    PLANETARY_COMPUTER_STAC_URL,
    SENTINEL1_RTC_COLLECTION,
    SENTINEL2_L2A_COLLECTION,
    STACCatalogError,
    _request_json,
    search_sentinel1_rtc,
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

    @patch("src.data.copernicus_stac.urlopen")
    def test_request_reports_non_json_gateway_response(self, urlopen) -> None:
        response = unittest.mock.MagicMock()
        response.read.return_value = b"<html>Request Rejected</html>"
        response.headers.get.return_value = "text/html; charset=utf-8"
        urlopen.return_value.__enter__.return_value = response

        with self.assertRaisesRegex(STACCatalogError, "non-JSON response"):
            _request_json(
                url="https://stac.example/search",
                method="POST",
                body={"limit": 1},
                timeout_seconds=1,
            )

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
    def test_post_pagination_uses_body_cursor_on_same_url(self, request_json) -> None:
        request_json.side_effect = [
            {
                "features": [item("one", "2023-02-02T00:00:00Z")],
                "links": [
                    {
                        "rel": "next",
                        "href": "/v1/search",
                        "method": "POST",
                        "body": {"token": "page-2"},
                    }
                ],
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
            request_json.call_args_list[1].kwargs["url"], f"{DEFAULT_STAC_URL}/search"
        )
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "POST")
        self.assertEqual(
            request_json.call_args_list[1].kwargs["body"], {"token": "page-2"}
        )

    @patch("src.data.copernicus_stac._request_json")
    def test_post_pagination_rejects_repeated_cursor(self, request_json) -> None:
        repeated_next = {
            "rel": "next",
            "href": "/v1/search",
            "method": "POST",
            "body": {"token": "page-2"},
        }
        request_json.side_effect = [
            {
                "features": [item("one", "2023-02-02T00:00:00Z")],
                "links": [repeated_next],
            },
            {
                "features": [item("two", "2023-03-02T00:00:00Z")],
                "links": [repeated_next],
            },
        ]

        with self.assertRaisesRegex(STACCatalogError, "repeated a page link"):
            search_sentinel2_l2a(
                aoi_geometry=GEOMETRY,
                start_date="2023-02-01",
                end_date="2023-04-01",
            )
        self.assertEqual(request_json.call_count, 2)

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

    @patch("src.data.copernicus_stac._request_json")
    def test_sentinel1_rtc_uses_public_planetary_computer_collection(
        self, request_json
    ) -> None:
        request_json.return_value = {
            "features": [item("rtc-one", "2023-02-02T00:00:00Z")],
            "links": [],
        }

        result = search_sentinel1_rtc(
            aoi_geometry=GEOMETRY,
            start_date="2023-02-01",
            end_date="2023-03-01",
        )

        self.assertEqual([record["id"] for record in result], ["rtc-one"])
        request = request_json.call_args.kwargs
        self.assertEqual(
            request["url"], f"{PLANETARY_COMPUTER_STAC_URL}/search"
        )
        self.assertEqual(request["body"]["collections"], [SENTINEL1_RTC_COLLECTION])

    @patch("src.data.copernicus_stac._request_json")
    def test_sentinel2_can_use_compatible_alternative_stac_endpoint(
        self, request_json
    ) -> None:
        request_json.return_value = {"features": [], "links": []}

        search_sentinel2_l2a(
            aoi_geometry=GEOMETRY,
            start_date="2023-02-01",
            end_date="2023-03-01",
            stac_url=PLANETARY_COMPUTER_STAC_URL,
        )

        request = request_json.call_args.kwargs
        self.assertEqual(
            request["url"], f"{PLANETARY_COMPUTER_STAC_URL}/search"
        )
        self.assertEqual(request["body"]["collections"], [SENTINEL2_L2A_COLLECTION])


if __name__ == "__main__":
    unittest.main()
