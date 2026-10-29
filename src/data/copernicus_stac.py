"""Search the public Copernicus Data Space STAC catalogue.

This module discovers Sentinel-2 L2A item metadata only. It does not download
assets, run atmospheric/cloud processing, or claim that a returned footprint
contains usable pixels.
"""

from __future__ import annotations

import json
import math
from datetime import date, datetime, time, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

from src.contracts.schemas import SchemaValidationError, StudyAreaQuery

DEFAULT_STAC_URL = "https://stac.dataspace.copernicus.eu/v1"
SENTINEL2_L2A_COLLECTION = "sentinel-2-l2a"


class STACCatalogError(RuntimeError):
    """Raised when the catalogue response or pagination is invalid."""


def _utc_datetime(value: str, *, field_name: str) -> datetime:
    """Parse an RFC 3339 timestamp and require an explicit UTC offset."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise STACCatalogError(f"STAC item has an invalid {field_name}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise STACCatalogError(f"STAC item {field_name} must specify UTC")
    return parsed.astimezone(timezone.utc)


def _request_json(
    *, url: str, method: str, body: dict[str, Any] | None, timeout_seconds: float
) -> dict[str, Any]:
    """Request a JSON document from the STAC endpoint."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(
        url,
        data=data,
        headers={"Accept": "application/geo+json, application/json"},
        method=method,
    )
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read())
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise STACCatalogError(f"Copernicus STAC request failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise STACCatalogError("Copernicus STAC response must be a JSON object")
    return payload


def search_sentinel2_l2a(
    *,
    aoi_geometry: dict[str, Any],
    start_date: str,
    end_date: str,
    max_cloud_cover_percent: float | None = None,
    page_size: int = 100,
    max_items: int = 1000,
    timeout_seconds: float = 30.0,
    stac_url: str = DEFAULT_STAC_URL,
) -> list[dict[str, Any]]:
    """Return Sentinel-2 L2A STAC items intersecting a CON-01 query.

    The requested interval follows CON-01's start-inclusive/end-exclusive
    date convention. STAC search is issued with UTC day boundaries; returned
    item timestamps are filtered locally to enforce the exclusive end date.
    Items are metadata records, not proof of clear coverage or usable pixels.

    Args:
        aoi_geometry: GeoJSON Polygon or MultiPolygon in longitude/latitude.
        start_date: Inclusive ISO date in ``YYYY-MM-DD`` form.
        end_date: Exclusive ISO date in ``YYYY-MM-DD`` form.
        max_cloud_cover_percent: Optional scene-level cloud filter in [0, 100].
        page_size: Requested page size; must be between 1 and 500.
        max_items: Maximum number of item records to return; must be positive.
        timeout_seconds: Per-request timeout in seconds.
        stac_url: Copernicus STAC API root; HTTPS is required.

    Returns:
        STAC Item dictionaries ordered as returned by the catalogue, with
        items at or after the exclusive end date removed.

    Raises:
        ValueError: If query parameters violate their declared constraints.
        STACCatalogError: If the service returns invalid metadata or pagination.
    """
    try:
        StudyAreaQuery(
            query_id="copernicus-stac-search",
            aoi_geometry=aoi_geometry,
            start_date=start_date,
            end_date=end_date,
        )
    except SchemaValidationError as exc:
        raise ValueError(str(exc)) from exc
    if max_cloud_cover_percent is not None and (
        isinstance(max_cloud_cover_percent, bool)
        or not isinstance(max_cloud_cover_percent, (int, float))
        or not 0 <= max_cloud_cover_percent <= 100
    ):
        raise ValueError("max_cloud_cover_percent must be between 0 and 100")
    if (
        isinstance(page_size, bool)
        or not isinstance(page_size, int)
        or not 1 <= page_size <= 500
    ):
        raise ValueError("page_size must be an integer between 1 and 500")
    if isinstance(max_items, bool) or not isinstance(max_items, int) or max_items < 1:
        raise ValueError("max_items must be a positive integer")
    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, (int, float))
        or not math.isfinite(timeout_seconds)
        or timeout_seconds <= 0
    ):
        raise ValueError("timeout_seconds must be positive")

    endpoint = stac_url.rstrip("/")
    endpoint_parts = urlsplit(endpoint)
    if endpoint_parts.scheme != "https" or not endpoint_parts.netloc:
        raise ValueError("stac_url must be an absolute HTTPS URL")

    start = datetime.combine(date.fromisoformat(start_date), time.min, timezone.utc)
    end = datetime.combine(date.fromisoformat(end_date), time.min, timezone.utc)
    search_body: dict[str, Any] = {
        "collections": [SENTINEL2_L2A_COLLECTION],
        "intersects": aoi_geometry,
        "datetime": f"{start.isoformat().replace('+00:00', 'Z')}/"
        f"{end.isoformat().replace('+00:00', 'Z')}",
        "limit": min(page_size, max_items),
    }
    if max_cloud_cover_percent is not None:
        search_body["query"] = {
            "eo:cloud_cover": {"lte": float(max_cloud_cover_percent)}
        }

    current_url = f"{endpoint}/search"
    current_method = "POST"
    current_body: dict[str, Any] | None = search_body
    found: list[dict[str, Any]] = []
    seen_item_ids: set[str] = set()
    seen_page_urls: set[str] = set()
    while current_url and len(found) < max_items:
        page_parts = urlsplit(current_url)
        if (page_parts.scheme, page_parts.netloc) != (
            endpoint_parts.scheme,
            endpoint_parts.netloc,
        ):
            raise STACCatalogError("STAC pagination link changed the endpoint origin")
        if current_url in seen_page_urls:
            raise STACCatalogError("STAC pagination repeated a page link")
        seen_page_urls.add(current_url)

        page = _request_json(
            url=current_url,
            method=current_method,
            body=current_body,
            timeout_seconds=float(timeout_seconds),
        )
        features = page.get("features")
        if not isinstance(features, list):
            raise STACCatalogError("STAC search response is missing its features array")
        links = page.get("links", [])
        if not isinstance(links, list):
            raise STACCatalogError("STAC response links must be an array")
        for item in features:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("id"), str)
                or not item["id"].strip()
                or not isinstance(item.get("properties"), dict)
            ):
                raise STACCatalogError("STAC search response contains a malformed item")
            item_time = item["properties"].get("datetime")
            if item_time is None:
                raise STACCatalogError("STAC item is missing its acquisition datetime")
            acquisition_time = _utc_datetime(item_time, field_name="datetime")
            if start <= acquisition_time < end and item["id"] not in seen_item_ids:
                seen_item_ids.add(item["id"])
                found.append(item)
                if len(found) >= max_items:
                    break

        next_link = next(
            (
                link
                for link in links
                if isinstance(link, dict) and link.get("rel") == "next"
            ),
            None,
        )
        if not next_link:
            break
        href = next_link.get("href")
        if not isinstance(href, str):
            raise STACCatalogError("STAC next link has no href")
        href = urljoin(current_url, href)
        current_url = href
        current_method = str(next_link.get("method", "GET")).upper()
        if current_method not in {"GET", "POST"}:
            raise STACCatalogError("STAC next link uses an unsupported HTTP method")
        next_body = next_link.get("body")
        if current_method == "POST" and not isinstance(next_body, dict):
            raise STACCatalogError("STAC POST next link is missing its request body")
        current_body = next_body if current_method == "POST" else None

    return found[:max_items]
