# AgriSense Local User Guide

This guide covers the current local research preview. It does not describe a production data service.

## Start the application

From the repository root, install frontend dependencies and build the browser app:

```powershell
cd frontend
npm ci
npm run build
cd ..
```

Start the API and served frontend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. For frontend hot reload, run `npm run dev` from `frontend` and the API in a second terminal. Vite proxies `/api` calls to the local API.

## Validate a study-area request

1. Upload a GeoJSON `Polygon` or `MultiPolygon` boundary you are authorized to use. Coordinates must be longitude/latitude in EPSG:4326 order and rings must be closed. The preview supports zoom in, zoom out, and fit-to-boundary controls; it is not a basemap or a scientific map layer.
2. Choose the requested start date and exclusive end date.
3. Select **Validate study request**.

The API validates request structure only. It does not select or approve the AOI, check source permissions, query a provider, or acquire observations. The geometry preview stays in the browser.

## Load temporal analytics

1. Open **Temporal analytics**.
2. Choose a JSON product view produced from a reviewed data handoff.
3. Optionally set a start date and exclusive end date within the product interval to filter the displayed records and stage transitions.
4. Review units, time support, quality, source references, missing-value reasons, and limitations before interpreting the chart or exporting CSV. The CSV contains the selected interval only.

The browser reads the file locally. It is not uploaded or persisted. The importer checks structural metadata and timestamp ordering; it does not verify source authenticity, scientific validity, AOI approval, or method approval. Use only traceable producer outputs for research interpretation.

The JSON object has these fields:

| Field | Required contents |
|---|---|
| `interval` | `start` and `end` calendar dates (`YYYY-MM-DD`); start is inclusive and end is exclusive. |
| `series` | Array of time series. Each series has a unique `id`, `label`, `unit`, `timeSupport`, `sourceReference`, `status` (`observation` or `estimate`), `qualityState`, `samples`, and `limitations`. |
| `series[].samples` | Non-empty, chronologically ordered UTC timestamps inside the interval. `value` is a finite number or `null`; a null value requires a non-empty `missingReason`. |
| `stageTransitions` | Array of optional transition records, each with a UTC `timestamp`, `stageCode`, `method`, `methodVersion`, `qualityState`, and `sourceReference`. |
| `limitations` | Array of non-empty strings describing product-level limitations. |

Each series must include provenance and quality metadata. The importer preserves separate series scales and visible gaps; it does not interpolate missing values. Date filtering uses a half-open interval (start inclusive, end exclusive) and leaves the loaded product unchanged. CSV export includes the selected interval, timestamps, values, units, missing reasons, quality, method, provenance references, and limitations.

## Current limits

- No producer-backed product API or automated product ingestion is connected.
- No pilot AOI, validated crop/stage/stress product, or irrigation estimate is bundled.
- A structurally valid temporal JSON file is not proof of scientific correctness or permission to reuse its underlying data.
