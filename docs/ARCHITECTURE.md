# Architecture — AgriSense

> **Status: PROVISIONAL** — All recommendations require team approval before implementation.

## 1. Architecture Overview

AgriSense is provisionally a Python scientific backend with a separate, responsive browser dashboard. The project owner selected React + TypeScript with a FastAPI Python API. The user authorized approval steps on behalf of all members on 2026-10-29; individual implementation reviews remain pending. If GEE is selected, supported raster operations may run server-side; the Python backend handles model fitting, phenology analysis, water-balance calculations, and API responses. This proposed division depends on approved data and interface contracts.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Google Earth Engine                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                         │
│  │Sentinel-2│  │Sentinel-1│  │ ERA5-Land│   Server-side filtering, │
│  │  SR/TOA  │  │   GRD    │  │  Daily   │   compositing, masking,  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘   index computation      │
│       └──────────────┼────────────┘                                 │
│                      ▼                                              │
│              Preprocessed exports                                   │
└──────────────────────┬──────────────────────────────────────────────┘
                       │ (GeoTIFF / NumPy arrays / GEE FeatureCollections)
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      Local Python Application                       │
│                                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐          │
│  │ Data Manager│  │ Crop         │  │ Phenology &       │          │
│  │ (GEE I/O,  │─→│ Classifier   │─→│ Growth Stage      │          │
│  │  caching)  │  │ (Random      │  │ Estimator         │          │
│  │            │  │  Forest)     │  │ (SciPy)           │          │
│  └─────────────┘  └──────────────┘  └────────┬──────────┘          │
│                                               │                      │
│                                               ▼                      │
│                                    ┌───────────────────┐            │
│                                    │ Stage-Aware       │            │
│                                    │ Stress Detector   │            │
│                                    └────────┬──────────┘            │
│                                             │                        │
│                                             ▼                        │
│                                  ┌───────────────────────┐          │
│                                  │ FAO-56 Water Balance  │          │
│                                  │ Water-Balance Estimate│          │
│                                  └────────┬──────────────┘          │
│                                           │                          │
│                                           ▼                          │
│                                ┌─────────────────────┐              │
│                                │ Canal Aggregator     │              │
│                                │ (GeoPandas)          │              │
│                                └────────┬────────────┘              │
│                                         │                            │
│                                         ▼                            │
│                              ┌──────────────────────┐               │
│                              │ Responsive Web UI     │               │
│                              │ (framework TBD)       │               │
│                              └──────────────────────┘               │
└──────────────────────────────────────────────────────────────────────┘
```

## 2. Frontend Decision: Streamlit vs a Responsive Web Application

### Multi-Region Design Direction

The project-owner-approved scope direction is India-first and multi-region. Punjab and Tamil Nadu were the initial candidate set; `DEC-14` broadens the evidence review, with Telangana/TGRAC currently a lead candidate and no selected pilot AOI. The first pilot is intended to use one real irrigation-command area and support crop classification and irrigation-advisory research. The retrieved SRSP Stage I polygon has the highest current label overlap, but remains a candidate pending source, licensing, suitability, and validation checks (see [`docs/DS09_AOI_AUDIT.md`](DS09_AOI_AUDIT.md)). Separate shared processing logic from versioned regional profiles. A profile references sourced AOI/boundary data, supported crops and seasons, crop-calendar references, CRS/grid choices, and applicable local scientific parameters. Shared modules must not embed state-specific defaults. Derived products identify their region/profile version, source provenance, and limitations. A profile does not make an unvalidated model transferable; each region and season requires appropriate evaluation.

Regional profile fields that affect `CON-01`–`CON-09` require a proposed schema change and unanimous approval from all three members before implementation.

Maintain an extensible crop catalogue independently from the model's supported class list. The initial classifier includes only classes with verified, traceable labels for its selected AOIs and seasons. Canal-command aggregation is conditional on a sourced command boundary and suitable estimates; otherwise omit/defer that layer. The dashboard direction selected by the owner is React + TypeScript with a FastAPI API, subject to team technical confirmation.

The regional configuration boundary is a configuration/provenance layer consumed by shared acquisition, feature, modelling, water-balance, aggregation, and presentation modules. It selects region-specific references and supported domains; it must not silently tune models, substitute missing labels, or supply unsourced agronomic defaults.

### Option A: Streamlit Monolith *(Source-proposed option)*

| Aspect | Assessment |
|--------|------------|
| **Source alignment** | The source documents propose Streamlit (IDP O3, mava F8) |
| **Implementation choice** | All-Python stack; framework selection remains subject to DEC-01 review |
| **Development speed** | Rapid prototyping; single codebase |
| **Interactivity** | Streamlit-Folium for maps; Plotly for charts; adequate for the use case |
| **Deployment** | Single process; Streamlit Community Cloud or simple server |
| **Limitations** | Less customisable UI; re-runs on interaction; limited multi-page patterns |
| **Suitability** | Fast academic prototype; less suited to the owner's stated preference for a highly responsive, bespoke dashboard |

### Option B: React + TypeScript + Python API *(Owner-preferred candidate)*

| Aspect | Assessment |
|--------|------------|
| **Source alignment** | The source documents propose Streamlit; this option changes that implementation proposal while retaining the dashboard objective |
| **Implementation choice** | Adds frontend tooling and API integration; deployment topology and tooling must be decided |
| **Development speed** | Separate frontend and backend work can proceed against contracts, with added integration and deployment work |
| **Interactivity** | Supports a custom responsive layout and tailored map, chart, and table interactions |
| **Deployment** | Frontend and API hosting must be planned; exact deployment remains undecided |
| **Limitations** | Higher setup and maintenance cost for a three-member academic project |
| **Suitability** | Better fit for the owner's professional and responsive dashboard preference, subject to team technical confirmation |

### Decision

> **DEC-01: Owner-selected direction — responsive React + TypeScript frontend with a FastAPI Python API.** The source documents propose Streamlit; this is a deliberate departure from that implementation proposal while preserving the dashboard objective. Team technical confirmation, mapping/chart libraries, and deployment remain open. No guide approval is recorded or assumed.

## 3. Module Responsibilities

### 3.1 Data Acquisition & GEE Integration (M-DATA)

**Owners:** Member B (satellite ingestion/features), Member A (weather ingestion, assembly/cache).

**Responsibilities:**
- GEE authentication and session management
- Sentinel-2 query, cloud masking (SCL + QA60), temporal compositing
- Sentinel-1 query, orbit filtering, speckle filtering
- ERA5-Land query, variable extraction, ET0 computation
- Study-area and field-boundary management
- Data export (GeoTIFF, NumPy, DataFrame)
- Local caching to avoid repeated GEE calls
- Data provenance metadata

**Key interfaces:**
- Produces: `PreprocessedObservation` (contract CON-03)
- Consumes: `StudyAreaRequest` (contract CON-01)

### 3.2 Crop Classification (M-CLASS)

**Owner:** Member B

**Responsibilities:**
- Feature engineering from preprocessed observations (multi-temporal index stacks)
- Random Forest model training, hyperparameter tuning
- Pixel-level crop-type prediction
- Per-class confidence estimation
- Training/validation/test split with spatial blocking
- Feature importance analysis
- Model persistence (joblib)

**Key interfaces:**
- Consumes: `PreprocessedObservation` (CON-03), ground-truth labels
- Produces: `CropClassificationResult` (CON-04)

### 3.3 Phenology & Growth Stage Estimation (M-PHENO)

**Owner:** Member B

**Responsibilities:**
- Time-series smoothing (Savitzky-Golay or similar via SciPy)
- Inflection-point detection for stage transitions
- Growth-stage assignment: vegetative, flowering/heading, senescence
- Confidence estimation for stage assignments
- Handling temporal gaps and uncertain transitions

**Key interfaces:**
- Consumes: `PreprocessedObservation` (CON-03), `CropClassificationResult` (CON-04)
- Produces: `PhenologyEstimate` (CON-05)

### 3.4 Stage-Aware Stress Detection (M-STRESS)

**Owner:** Member B

**Responsibilities:**
- Candidate stage-conditioned interpretation of VCI and any specifically defined NDWI variant; thresholds require approval and validation
- Stress classification: no-stress, moderate, severe, uncertain
- False-alarm suppression during senescence
- Consider Sentinel-1 as a separate complementary observation only under a validated method; it does not substitute for a missing optical observation
- Confidence and uncertainty flags

**Key interfaces:**
- Consumes: `PreprocessedObservation` (CON-03), `PhenologyEstimate` (CON-05)
- Produces: `StressIndicator` (CON-06)

### 3.5 Water-Balance Estimate (M-WATER)

**Owner:** Member A (Peter); Member B (Rishav) reviews scientific assumptions.

**Responsibilities:**
- FAO-56 ETc = Kc × ET0 computation
- Effective rainfall estimation
- Soil water balance (where soil data available)
- Water-balance depth estimate in mm when the method and required inputs are approved; any area-derived volume is separately reported in m³ with contributing area and assumptions.
- Stage-appropriate Kc selection
- Uncertainty and assumption documentation

**Key interfaces:**
- Consumes: `PhenologyEstimate` (CON-05), meteorological inputs, Kc source, and any approved soil-water inputs
- Produces: `FieldWaterBalanceEstimate` (CON-08) from documented inputs. Outputs must not imply a canal release prescription.

### 3.6 Canal Boundary Aggregation (M-CANAL)

**Primary owner:** Member A (Peter). **Integration reviewer:** Member C (Ashwanth C).

**Responsibilities:**
- Load and validate canal command boundary shapefiles
- Spatial intersection of pixel-level results with canal polygons (GeoPandas)
- Area-weighted aggregation of deficits
- Summary statistics per available boundary; report depths and area-derived volumes with explicit assumptions. Do not recommend gate releases without hydraulic and operational inputs.

**Key interfaces:**
- Consumes: `FieldWaterBalanceEstimate` (CON-08), canal boundary geometries
- Produces: `CanalAggregateReport` (CON-09)

### 3.7 Dashboard & Application (M-DASH)

**Owner:** Member C

**Responsibilities:**
- Responsive browser dashboard with adaptive phone, tablet, and desktop layouts
- Interactive map with togglable layers: crop map, growth stage, candidate indicators, and available water-balance estimates; mapping library TBD
- Time-series charts for per-field/per-pixel analysis; chart library TBD
- Data tables with download capability
- API integration for approved module outputs and explicit loading, empty, error, and data-quality states
- Input controls: study area selection, date range, crop filter

**Key interfaces:**
- Consumes: All output contracts (CON-04 through CON-09)
- Produces: Visual dashboard; any API request/response schemas needed by the browser are defined after DEC-01 and must reuse approved scientific contracts rather than introduce unreviewed scientific fields.

### 3.8 Scientific Evaluation (M-EVAL)

**Owner:** Member B (scientific metric definitions and analysis); Member A reviews data provenance and split design; Member C reviews integration. Independent validation evidence must be sourced and is not replaced by team review.

**Responsibilities:**
- Classification metrics: accuracy, Kappa, F1, per-class precision/recall, confusion matrix
- Stress detection: false-alarm rate analysis
- Water balance: deficit RMSE (if validation data available)
- Monitoring continuity assessment
- Uncertainty analysis and reporting

**Key interfaces:**
- Consumes: All output contracts + ground-truth/validation data
- Produces: Evaluation reports (for documentation, not a runtime contract)

## 4. Storage and Caching

| Data Type | Storage | Format | Notes |
|-----------|---------|--------|-------|
| Raw satellite data | GEE (not local) | GEE ImageCollection | Never downloaded in bulk |
| Preprocessed composites | Local cache | GeoTIFF / NetCDF | Cached to avoid re-querying GEE |
| Classification model | Local | joblib | Versioned with training metadata |
| Classification results | Local | GeoTIFF + GeoJSON | Per-pixel crop map |
| Phenology / stress | Local | GeoTIFF + DataFrame | Time-series per pixel/field |
| Water balance | Local | DataFrame / CSV | Per-pixel or per-field deficit |
| Canal aggregates | Local | GeoJSON + CSV | Per-canal summary |
| Dashboard state | Browser/API session (implementation TBD) | In-memory or approved store | Ephemeral unless a persistence requirement is approved |

**Cache directory:** `data/cache/` (gitignored).
**Output directory:** `data/outputs/` (gitignored).

## 5. Configuration and Secrets

| Item | Mechanism | Committed? |
|------|-----------|-----------|
| GEE project ID | `.env` | No (`.env.example` committed with placeholders) |
| GEE credentials | `earthengine authenticate` | No |
| Study area definition | `config/study_area.geojson` | Yes (small file) |
| Crop calendar | `config/crop_calendar.yaml` | Yes |
| Kc coefficients | `config/kc_coefficients.yaml` | Yes |
| App settings | `config/app_config.yaml` | Yes |

## 6. Logging

- Python `logging` module with configurable levels.
- All GEE queries logged with timestamps and parameters.
- All scientific computations logged with input summaries and assumptions used.
- No sensitive data in logs.

## 7. Deployment *(Provisional)*

For academic demonstration, local development will run the owner-selected browser frontend and Python API after team technical confirmation of DEC-01. Commands, hosting, and service topology remain undecided.

- GEE authenticated per-user

Deployment and containerisation remain provisional; evaluate only after the team confirms the intended users, hosting, and data-access model.

## 8. Technology Stack Summary

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Satellite processing | Google Earth Engine API | Both PDFs specify; scalable server-side processing |
| ML classification | scikit-learn (Random Forest) | Both PDFs specify; interpretable, robust |
| Phenology | SciPy signal processing | IDP PDF specifies SciPy; mava F3 |
| Water balance | NumPy / Pandas | FAO-56 vectorised computation |
| Geospatial | GeoPandas, Rasterio | Both PDFs specify; canal aggregation |
| Dashboard | Responsive React + TypeScript frontend | User-authorized direction; implementation review pending; source documents propose Streamlit |
| API/backend | FastAPI Python API | User-authorized direction; implementation review pending |
| Map visualisation | Library TBD | Source proposes Folium via Streamlit; select after framework and integration review |
| Charts | Library TBD | Source proposes Plotly; confirm compatibility with DEC-01 |
| Testing | pytest | Standard Python testing |
| Formatting | black, ruff, isort | Code quality |

## 9. Proposed Directory Structure

```
agrisense/
├── AGENTS.md
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt            # Pinned dependencies (created in P1)
├── frontend/                   # Responsive browser UI (framework TBD; created after DEC-01 approval)
├── src/api/                    # Python API boundary (framework TBD; created after DEC-01 approval)
├── config/
│   ├── study_area.geojson      # Study area definition
│   ├── crop_calendar.yaml      # Crop phenology calendar
│   ├── kc_coefficients.yaml    # FAO-56 Kc values
│   └── app_config.yaml         # Application settings
├── src/
│   ├── __init__.py
│   ├── data/                   # Satellite files (Member B); auth/weather/assembly/cache (Member A)
│   │   ├── __init__.py
│   │   ├── gee_auth.py
│   │   ├── copernicus_stac.py
│   │   ├── sentinel2.py
│   │   ├── sentinel1.py
│   │   ├── era5land.py
│   │   ├── preprocessing.py
│   │   ├── observation_assembly.py
│   │   └── cache.py (Member A owns cache; Member B owns preprocessing)
│   ├── models/                 # CLASS/PHENO/STRESS (Member B); WATER (Member A)
│   │   ├── __init__.py
│   │   ├── classifier.py
│   │   ├── phenology.py
│   │   ├── stress.py
│   │   └── water_balance.py
│   ├── spatial/                # M-CANAL: Canal aggregation (Member A)
│   │   ├── __init__.py
│   │   └── canal_aggregator.py
│   ├── dashboard/              # M-DASH: Python-side dashboard integration (Member C)
│   │   ├── __init__.py
│   │   ├── pages/
│   │   └── components/
│   ├── contracts/              # Shared data classes / schemas (Member C coordinates)
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── evaluation/             # M-EVAL: Metrics and validation (Member B)
│       ├── __init__.py
│       └── metrics.py
├── tests/
│   ├── data/                   # Tests for M-DATA (Member A)
│   ├── models/                 # Tests for M-CLASS/PHENO/STRESS/WATER (Member B)
│   ├── spatial/                # Tests for M-CANAL
│   ├── dashboard/              # API/UI integration checks (Member C)
│   └── integration/            # Integration tests (Member C + all)
├── scripts/                    # Utility scripts
├── data/                       # Local data (gitignored)
│   ├── cache/
│   ├── outputs/
│   └── ground_truth/
├── docs/                       # Project documentation
│   ├── PROJECT_OVERVIEW.md
│   ├── ARCHITECTURE.md
│   ├── EXECUTION_PLAN.md
│   ├── TASK_ASSIGNMENTS.md
│   ├── DATA_REQUIREMENTS.md
│   ├── API_CONTRACTS.md
│   ├── TEAM_WORKFLOW.md
│   ├── DECISIONS.md
│   ├── STATUS.md
│   ├── references/
│   │   └── README.md
│   └── risks/
│       └── SCIENTIFIC_RISKS.md
└── notebooks/                  # Exploration notebooks (gitignored outputs)
```

> **Note:** This proposed structure remains provisional. The repository currently includes `frontend/`, `src/api/`, contract schemas, and selected satellite utilities; the planned model, weather, assembly, and spatial modules are not all implemented. The user authorized React + TypeScript and FastAPI approval steps on 2026-10-29; this does not mark the application or phase complete.

## 10. Module Dependency Graph

```
StudyArea ──→ M-DATA ──→ M-CLASS ──→ M-PHENO ──→ M-STRESS
                │                       │              │
                │                       ▼              ▼
                └──────────────→ M-WATER ←─────────────┘
                                    │
                                    ▼
                               M-CANAL
                                    │
                                    ▼
                               M-DASH
                                    │
                                    ▼
                               M-EVAL
```

Sequential dependencies:
1. M-DATA must produce preprocessed observations before any other module can run.
2. M-CLASS requires M-DATA outputs.
3. M-PHENO requires M-DATA outputs and M-CLASS outputs (crop type determines phenology model).
4. M-STRESS requires M-PHENO (growth stage determines threshold).
5. M-WATER requires M-PHENO (Kc depends on stage) and meteorological data from M-DATA.
6. M-CANAL requires M-WATER outputs and canal boundary data.
7. Sequential stages use explicit reviewed handoffs; downstream modules wait for complete required inputs.
8. M-EVAL runs after all modules produce outputs.

Approved work order: Member B completes satellite processing; Member A completes weather ingestion and final assembly; Member B completes scientific models; Member A completes water-balance/canal outputs; Member C completes dashboard/API after DEC-01 and API boundary approval. Each handoff is reviewed. Synthetic fixtures are for labeled software tests only.

## 11. Browser/API Boundary — `T-P1-SH-003`

The browser calls the same-origin `/api` routes in deployment. During local development, Vite proxies `/api` to the FastAPI service. The browser may preview a user-selected GeoJSON boundary locally; this preview is not saved or treated as an approved study AOI.

### Implemented foundation routes

| Route | Request | Response and meaning |
|---|---|---|
| `GET /api/health` | None | Process liveness only: `{status, service}`. It does not imply provider connectivity. |
| `GET /api/readiness` | None | Capability flags, null product references, and current limitations. `null` means no product is available. |
| `POST /api/study-area/validate` | `CON-01` fields: `aoi_geometry`, `start_date`, `end_date`, optional `target_crs`, optional `buffer_meters` | Structural validation result with `query_id`, `valid`, `message`, and `accepted_for_acquisition: false`. No persistence, data query, licensing check, AOI approval, or scientific processing occurs. |

Malformed JSON or invalid fields return HTTP 422 with a validation detail. The browser displays the error and retains no success state. Network failures display an API connection error. A structurally valid request displays the returned `query_id` and the explicit no-acquisition message.

### Product and data-quality states

- Until actual source data and a valid processing task produce products, all estimate/product references remain `null`; the dashboard uses empty states and does not draw fictional crop, stage, stress, water-balance, or zonal layers.
- Future responses map to `CON-03` through `CON-09` and must include their contract provenance, units, time support, quality state, limitations, and unavailable-value reasons. An absent product is an empty state, not a zero or a failed estimate.
- Loading is a transient browser state while a request is pending. A failed request is an error state; low coverage or missing observations are product quality states supplied by real processing metadata. These states must not be conflated.
- The current browser boundary supports only health, readiness, and `CON-01` structural validation. It has no product, layer, chart, or CSV endpoint yet. Such interfaces require actual producer modules and response contracts before they can be completed honestly.

### Access and deployment

The current CORS allowlist is limited to local development origins and the API has no authentication. Keep it bound to local development until deployment security, access control, data policy, and rate limits are selected. Do not expose the foundation API publicly as an authenticated product service.
