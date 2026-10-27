"""FastAPI endpoints for readiness and study-area request validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from fastapi.staticfiles import StaticFiles

from src.contracts.schemas import SchemaValidationError, StudyAreaQuery


class StudyAreaRequest(BaseModel):
    """Browser request matching the approved CON-01 fields."""

    model_config = ConfigDict(extra="forbid")

    aoi_geometry: dict[str, Any]
    start_date: str = Field(min_length=10, max_length=10)
    end_date: str = Field(min_length=10, max_length=10)
    target_crs: str | None = None
    buffer_meters: float | None = Field(default=None, ge=0)


class ValidationResponse(BaseModel):
    """Result of structural validation; no observations are acquired."""

    query_id: str
    valid: bool
    message: str
    accepted_for_acquisition: bool = False


app = FastAPI(
    title="AgriSense API",
    version="0.1.0",
    description=(
        "AgriSense foundation API. Study-area validation checks request shape; "
        "it does not select an AOI, acquire observations, or produce estimates."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Report that the local API process is responding."""
    return {"status": "ok", "service": "agrisense-api"}


@app.get("/api/readiness")
def readiness() -> dict[str, Any]:
    """Report available implementation capabilities without implying data."""
    return {
        "status": "foundation",
        "capabilities": {
            "study_area_validation": True,
            "sentinel2_indices": True,
            "sentinel2_preprocessing": True,
            "sentinel1_backscatter_features": True,
            "sentinel1_ingestion": False,
            "weather_ingestion": False,
            "crop_classification": False,
            "phenology_estimates": False,
            "stress_estimates": False,
            "water_balance": False,
        },
        "products": {
            "crop_map": None,
            "growth_stage": None,
            "stress_indicator": None,
            "water_balance": None,
        },
        "limitations": [
            "No pilot AOI or study interval is configured.",
            "No real satellite, weather, or verified label data is connected.",
            "No scientific estimates or validation metrics are available.",
        ],
    }


@app.post("/api/study-area/validate", response_model=ValidationResponse)
def validate_study_area(payload: StudyAreaRequest) -> ValidationResponse:
    """Validate a CON-01 request shape without persisting or querying it."""
    query_id = f"query-{uuid4()}"
    try:
        StudyAreaQuery(
            query_id=query_id,
            aoi_geometry=payload.aoi_geometry,
            start_date=payload.start_date,
            end_date=payload.end_date,
            target_crs=payload.target_crs,
            buffer_meters=payload.buffer_meters,
        )
    except SchemaValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ValidationResponse(
        query_id=query_id,
        valid=True,
        message=(
            "AOI request structure is valid. No data was queried or saved; "
            "a verified study configuration is still required for acquisition."
        ),
    )


frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=frontend_dist, html=True),
        name="frontend",
    )
