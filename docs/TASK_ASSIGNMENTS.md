# AgriSense Task Assignments & Work Breakdown Structure

> **Status: PROVISIONAL — Subject to team review and guide sign-off**  
> **Team Allocation:** Exactly three human student members (Member A, Member B, Member C), as confirmed by the project owner. The IDP-listed three students form the project team; the additional name in the Mava submission is not a fourth project member.  
> **Academic Project:** BACSE291 — Innovative Design Project, VIT Vellore (Fall 2026).  
> **Guide:** Dr. Muthuraja S, Assistant Professor Sr. Grade 1.

---

## 1. Team Role Allocation Overview

| Team Member | Primary Domain | Core Responsibilities | File / Directory Ownership |
|:---|:---|:---|:---|
| **Member A** | **Data Engineering & Geospatial Processing** | Satellite and ERA5-Land ingestion; spatial alignment, cloud masking, coordinate transformations, data caching, and primary ownership of canal-boundary spatial processing. | `src/data/`, `src/spatial/`, `tests/data/`, `tests/spatial/`, `config/study_area.geojson`, `.env.example` |
| **Member B** | **Scientific Models & Validation** | Random Forest crop classification; SciPy phenological curve smoothing & inflection tracking; stage-aware dynamic VCI stress detection; FAO-56 crop water balance ($ET_c = K_c \times ET_0$); scientific validation & error metrics. | `src/models/`, `src/evaluation/`, `tests/models/`, `tests/evaluation/`, `config/crop_calendar.yaml`, `config/kc_coefficients.yaml` |
| **Member C** | **Backend/API, Responsive Frontend & Integration** | Python API/backend; responsive browser dashboard; map and chart integration (libraries TBD); canal output integration; shared-contract coordination; end-to-end integration. | `frontend/`, `src/api/`, `src/dashboard/`, `src/contracts/`, `tests/dashboard/`, `tests/integration/` |

> **Note on Member Skills & Availability:** Specific personal skillsets and academic schedules are marked as *pending confirmation*. AI coding agents may assist individual team members with code authoring and testing, but AI agents **do not count as team members** and cannot approve scientific decisions, validate results, or modify shared contracts.

---

## 2. File and Directory Ownership Matrix

To prevent merge conflicts and ensure safe parallel development, strict boundaries govern who can edit which directories.

| Directory / File Pattern | Primary Owner | Secondary Reviewer | Direct Edits Permitted by Others? |
|:---|:---|:---|:---|
| `src/data/**` | Member A | Member B | **No.** PR with Member A review required. |
| `src/models/**` | Member B | Member A | **No.** PR with Member B review required. |
| `src/evaluation/**` | Member B | Member C | **No.** PR with Member B review required. |
| `frontend/**`, `src/api/**`, `src/dashboard/**` | Member C | Member A | **No.** PR with Member C review required. Framework and exact structure depend on DEC-01 approval. |
| `src/spatial/**` | Member A | Member C | **No.** Member A owns changes; Member C reviews integration through PR. |
| `src/contracts/**` | Member C (Custodian) | Member A & B | **No.** Strict unanimous consensus required (all 3 members must approve PR). |
| `tests/contracts/**` | Member C | Member A & B | **No.** Contract tests must follow the approved shared schemas. |
| `tests/data/**` | Member A | Member B | **No.** Owned by Member A. |
| `tests/models/**` | Member B | Member A | **No.** Owned by Member B. |
| `tests/dashboard/**` | Member C | Member A | **No.** Owned by Member C. |
| `tests/integration/**` | Member C | Member A & B | Shared test suite; PR required. |
| `config/study_area.geojson` | Member A | Member B & C | PR required. |
| `config/crop_calendar.yaml` | Member B | Member A | PR required. |
| `config/kc_coefficients.yaml`| Member B | Member A | PR required. |
| `docs/STATUS.md` | Member C (Lead) | Member A & B | Any member may update checkpoint sections via PR. |
| `docs/DECISIONS.md` | All Members | Guide / Lead | PR required for any new decision entry. |
| `AGENTS.md`, `README.md` | All Members | All Members | Unanimous review required for changes. |

---

## 3. Detailed Work Breakdown Structure by Phase

### Phase P1: Foundation & Contracts

#### `T-P1-SH-001`: Python Environment & Tooling Configuration
- **Objective:** Establish reproducible environment with pinned dependencies, ruff linting, black formatting, and pytest runner.
- **Primary Owner:** Member C
- **Reviewer:** Member A & Member B
- **File Ownership:** `requirements.txt`, `pyproject.toml`, `.gitignore`
- **Inputs:** Architecture specification (`docs/ARCHITECTURE.md`).
- **Outputs:** Functional virtual environment and zero-error test run.
- **Dependencies:** None.
- **Contract Dependencies:** None.
- **Acceptance Criteria:** `pip install -r requirements.txt` succeeds; `pytest` runs without error on Windows and Linux.
- **Testing Requirements:** Test that ruff and black execute cleanly in CI / local terminal.
- **Blockers:** None.

#### `T-P1-SH-002`: Data Contract Schemas Implementation
- **Objective:** Translate abstract contracts (`CON-01` to `CON-09`) into strict Python dataclasses/Pydantic schemas with type enforcement and unit metadata.
- **Primary Owner:** Member C (Coordinator)
- **Reviewer:** Member A & Member B (Mandatory Sign-off)
- **File Ownership:** `src/contracts/schemas.py`, `tests/contracts/test_schemas.py`
- **Inputs:** `docs/API_CONTRACTS.md`.
- **Outputs:** Validated `src/contracts/schemas.py` package.
- **Dependencies:** `T-P1-SH-001`.
- **Contract Dependencies:** `CON-01` through `CON-09`.
- **Acceptance Criteria:** All contract data structures instantiate, validate fields, and serialize/deserialize JSON/GeoJSON cleanly.
- **Testing Requirements:** Schema validation tests with valid and invalid input fixtures.
- **Blockers:** Full Phase 0/guide sign-off is still pending; the contract amendment itself has unanimous approval from all three members (2026-10-23).

#### `T-P1-DE-001`: Google Earth Engine Authentication & Project Initializer
- **Objective:** Set up GEE authentication flow, project binding, and connection verification helper.
- **Primary Owner:** Member A
- **Reviewer:** Member C
- **File Ownership:** `src/data/gee_auth.py`, `scripts/verify_gee.py`, `.env.example`
- **Inputs:** Google Cloud Project with Earth Engine API enabled.
- **Outputs:** Module to initialize Earth Engine securely without hardcoded credentials.
- **Dependencies:** `T-P1-SH-001`.
- **Contract Dependencies:** None.
- **Acceptance Criteria:** `verify_gee.py` connects and retrieves a test Earth Engine metadata object.
- **Testing Requirements:** Mocked auth unit test when offline; live smoke test when online.
- **Blockers:** Team members must have registered GEE developer accounts.

#### `T-P1-SC-001`: Synthetic Benchmark Fixtures & Baseline Verification
- **Objective:** Build synthetic raster arrays and mock time-series data conforming to `CON-03` for testing models without GEE dependency.
- **Primary Owner:** Member B
- **Reviewer:** Member C
- **File Ownership:** `tests/fixtures/synthetic_raster.py`, `tests/fixtures/synthetic_timeseries.py`
- **Inputs:** `docs/API_CONTRACTS.md` schemas.
- **Outputs:** Generator functions producing synthetic S1, S2, and ERA5-Land numpy tensors.
- **Dependencies:** `T-P1-SH-002`.
- **Contract Dependencies:** `CON-03`.
- **Acceptance Criteria:** Synthetic fixtures pass all contract validation checks; explicitly labeled as synthetic.
- **Testing Requirements:** Ensure synthetic fixtures cannot be mistaken for real observations.
- **Blockers:** None.

---

### Phase P2: Independent Module Implementation

#### Workstream A — Member A (Data Engineering)

#### `T-P2-DE-002`: Sentinel-2 Optical Data Ingestion & Cloud Masking
- **Objective:** Query Sentinel-2 L2A Surface Reflectance, apply cloud/shadow masking via documented quality bands, and calculate selected optical indices (NDVI, EVI, `NDWI_MCF` and/or `NDWI_GAO`).
- **Primary Owner:** Member A
- **Reviewer:** Member B
- **File Ownership:** `src/data/sentinel2.py`, `tests/data/test_sentinel2.py`
- **Inputs:** `CON-01` (Study Area & Temporal Window).
- **Outputs:** Multi-spectral image collection with computed index bands.
- **Dependencies:** `T-P1-DE-001`.
- **Contract Dependencies:** `CON-01`, `CON-02`.
- **Acceptance Criteria:** Cloud pixels masked out; invalid values replaced with NaN/mask flags; optical indices match mathematical definitions.
- **Testing Requirements:** Unit tests using mocked GEE responses and synthetic raster arrays.
- **Blockers:** Study area boundaries must be defined in `config/study_area.geojson`.

#### `T-P2-DE-003`: Sentinel-1 SAR GRD Ingestion & Preprocessing
- **Objective:** Ingest Sentinel-1 GRD IW backscatter (VV, VH), filter orbit paths, apply speckle filtering, and compute cross-ratio ($VH/VV$).
- **Primary Owner:** Member A
- **Reviewer:** Member B
- **File Ownership:** `src/data/sentinel1.py`, `tests/data/test_sentinel1.py`
- **Inputs:** `CON-01` (Study Area & Temporal Window).
- **Outputs:** SAR image collection with calibrated backscatter and ratio bands.
- **Dependencies:** `T-P1-DE-001`.
- **Contract Dependencies:** `CON-01`, `CON-02`.
- **Acceptance Criteria:** Correct polarization selection; ratio band properly computed; radar dB values within physical bounds.
- **Testing Requirements:** Unit tests on speckle filter logic and backscatter ratio calculations.
- **Blockers:** Confirm radar orbit preference (ascending vs. descending).

#### `T-P2-DE-004`: ERA5-Land Reanalysis Ingestion & ET0 Derivation
- **Objective:** Query daily ERA5-Land meteorological grids (temperature, solar radiation, dewpoint, wind speed, precipitation) and calculate reference evapotranspiration ($ET_0$) via FAO-56 Penman-Monteith.
- **Primary Owner:** Member A
- **Reviewer:** Member B
- **File Ownership:** `src/data/era5land.py`, `tests/data/test_era5land.py`
- **Inputs:** `CON-01` (Study Area & Temporal Window).
- **Outputs:** Daily meteorological raster grid with $ET_0$ (mm/day) and precipitation (mm).
- **Dependencies:** `T-P1-DE-001`.
- **Contract Dependencies:** `CON-01`, `CON-02`.
- **Acceptance Criteria:** ET0 calculations follow the selected documented method and are checked against appropriate reference examples; native ERA5-Land grid identity is preserved and the collection's grid/temporal support is reported.
- **Testing Requirements:** Compare computed $ET_0$ against standard FAO-56 test example data.
- **Blockers:** None.

#### `T-P2-DE-005`: Multi-Sensor Temporal Compositing & Fusion Engine
- **Objective:** Harmonize Sentinel-1, Sentinel-2, and ERA5-Land into standardized temporal intervals (8-day composite stacks) conforming to `CON-03`.
- **Primary Owner:** Member A
- **Reviewer:** Member B & Member C
- **File Ownership:** `src/data/preprocessing.py`, `src/data/cache.py`, `tests/data/test_preprocessing.py`
- **Inputs:** Outputs of `T-P2-DE-002`, `T-P2-DE-003`, `T-P2-DE-004`.
- **Outputs:** `PreprocessedObservation` objects (`CON-03`) with local caching in `data/cache/`.
- **Dependencies:** `T-P2-DE-002`, `T-P2-DE-003`, `T-P2-DE-004`.
- **Contract Dependencies:** `CON-03`.
- **Acceptance Criteria:** Exported rasters maintain identical common analysis grid with native/effective resolution metadata; SAR observations are retained as a complementary modality and are not treated as equivalent optical replacements; metadata logs valid data fractions.
- **Testing Requirements:** Verify spatial alignment, CRS consistency, and caching read/write integrity.
- **Blockers:** Disk storage limits for local cache.

---

#### Workstream B — Member B (Scientific Modeling)

#### `T-P2-SC-002`: Random Forest Multi-Temporal Crop Classifier
- **Objective:** Implement the approved Random Forest configuration using sourced labels and seasonal features to generate crop maps on the declared analysis grid and uncertainty outputs.
- **Primary Owner:** Member B
- **Reviewer:** Member A
- **File Ownership:** `src/models/classifier.py`, `tests/models/test_classifier.py`
- **Inputs:** `CON-03` (Preprocessed multi-temporal observation stacks) and Ground-Truth Labels (`DS-04`).
- **Outputs:** `CropClassificationResult` (`CON-04`) with class predictions and uncertainty layers.
- **Dependencies:** `T-P1-SC-001`.
- **Contract Dependencies:** `CON-03`, `CON-04`.
- **Acceptance Criteria:** Train/val/test splits strictly segregated by spatial blocks; produces per-pixel class ID and entropy/confidence score.
- **Testing Requirements:** Unit test on synthetic arrays; verify model persistence (`joblib`) and inference reproducibility.
- **Blockers:** Sourcing ground-truth labels (`DS-04`) for study area.

#### `T-P2-SC-003`: Time-Series Phenology Tracker & Inflection Extractor
- **Objective:** Evaluate a documented time-series smoothing and transition-detection method against available crop-specific references. Inflection dates are estimates; do not equate a greenness peak directly with flowering without validation.
- **Primary Owner:** Member B
- **Reviewer:** Member C
- **File Ownership:** `src/models/phenology.py`, `config/crop_calendar.yaml`, `tests/models/test_phenology.py`
- **Inputs:** `CON-03` (NDVI/EVI time series) and `CON-04` (Crop Type).
- **Outputs:** `PhenologyEstimate` (`CON-05`) with growth stage ID, transition dates, and fit confidence.
- **Dependencies:** `T-P1-SC-001`.
- **Contract Dependencies:** `CON-03`, `CON-04`, `CON-05`.
- **Acceptance Criteria:** Handles irregular observations and gaps; reports uncertainty when observations are sparse; any crop-stage interpretation is validated against a documented crop calendar or independent reference.
- **Testing Requirements:** Unit tests against ideal synthetic double-logistic curves and noisy time series.
- **Blockers:** Region-specific crop calendar calibration (`DS-06`).

#### `T-P2-SC-004`: Growth-Stage-Aware Moisture-Stress Detector
- **Objective:** Evaluate dynamic, growth-stage-conditioned VCI/NDWI rules as candidate indicators; distinguish vegetation anomalies from confirmed crop-water stress.
- **Primary Owner:** Member B
- **Reviewer:** Member A
- **File Ownership:** `src/models/stress.py`, `tests/models/test_stress.py`
- **Inputs:** `CON-03` (VCI when its baseline exists, selected and named optical index variants, and documented SAR features where available), `CON-05` (Estimated Growth Stage).
- **Outputs:** Candidate `StressIndicator` (`CON-06`) values with an explicit uncertain/insufficient-data state; categories and thresholds depend on the approved method.
- **Dependencies:** `T-P2-SC-003`.
- **Contract Dependencies:** `CON-03`, `CON-05`, `CON-06`.
- **Acceptance Criteria:** Implements only a documented, approved candidate rule; reports uncertain cases and does not present vegetation-index anomalies as confirmed moisture stress without independent evidence.
- **Testing Requirements:** Synthetic scenario tests comparing static VCI vs. dynamic VCI on flowering vs. senescing pixels.
- **Blockers:** None.

#### `T-P2-SC-005`: Crop Evapotranspiration and Water-Balance Engine
- **Objective:** Calculate daily crop evapotranspiration ($ET_c = K_c \times ET_0$) and, only after the water-balance method and inputs are approved, estimate a clearly defined depth balance in mm. Do not label this alone as a field-verified irrigation requirement or canal volume.
- **Primary Owner:** Member B
- **Reviewer:** Member C
- **File Ownership:** `src/models/water_balance.py`, `config/kc_coefficients.yaml`, `tests/models/test_water_balance.py`
- **Inputs:** `CON-03` (ERA5-Land $ET_0$ and Precipitation), `CON-04` (Crop Type), `CON-05` (Growth Stage).
- **Outputs:** `CropEvapotranspirationEstimate` (`CON-07`) and, only when the method and required inputs are approved, `FieldWaterBalanceEstimate` (`CON-08`).
- **Dependencies:** `T-P2-SC-003` and approved meteorological inputs from `T-P2-DE-004`.
- **Contract Dependencies:** `CON-03`, `CON-04`, `CON-05`, `CON-07`, `CON-08`.
- **Acceptance Criteria:** The selected Kc source and stage mapping are traceable; depth units, assumptions, time window, missing inputs, and limitations are explicit. Quantify uncertainty only with a documented method. Scientific validation is reported separately from software tests.
- **Testing Requirements:** Validate water-balance numerical outputs against FAO-56 manual calculation examples.
- **Blockers:** A sourced and approved water-balance method and required soil/initial-storage inputs (`DS-08`); no regional default is assumed.

---

#### Workstream C — Member C (Backend/API, Responsive Frontend & Integration)

#### `T-P2-AP-001`: Canal Command Spatial Polygon Aggregator
- **Objective:** Ingest available canal-command boundary data, compute spatial overlays with approved depth estimates, and summarize zonal depth and area. Do not infer operational release volumes without the required delivery assumptions.
- **Primary Owner:** Member A
- **Reviewer:** Member C
- **File Ownership:** `src/spatial/canal_aggregator.py`, `tests/spatial/test_canal_aggregator.py`
- **Inputs:** Approved field water-balance estimates (`CON-08`) in mm and canal-command polygons (`DS-05`), if available.
- **Outputs:** Approved zonal summary with mapped area and mean depth; area-derived volume may be reported only with explicit assumptions and must not be presented as a gate-release prescription.
- **Dependencies:** `T-P1-SH-002`; execute only after shared contract approval.
- **Contract Dependencies:** `CON-08`, `CON-09`.
- **Acceptance Criteria:** Correct zonal aggregation and unit conversion, with valid-area accounting and documented coverage. Operational releases remain out of scope unless hydraulic and delivery data are available and approved.
- **Testing Requirements:** Spatial geometry tests using synthetic mock polygons and uniform deficit grids.
- **Blockers:** Acquiring or digitizing canal boundary shapefiles (`DS-05`).

#### `T-P2-AP-002`: Responsive Web Dashboard Base
- **Objective:** Build a professional responsive browser dashboard with an interactive map and toggleable Base Map, Crop Classification, Growth Stage, candidate Indicator, and available Water-Balance / Zonal Summary layers. Frontend framework, mapping library, Python API framework, and chart library require DEC-01 approval.
- **Primary Owner:** Member C
- **Reviewer:** Member B
- **File Ownership:** `frontend/`, `src/api/`, `src/dashboard/`, `tests/dashboard/` (exact paths follow approved DEC-01 architecture)
- **Inputs:** `CON-04`, `CON-05`, `CON-06`, `CON-09` (Mock or cached).
- **Outputs:** Responsive interactive web dashboard; local development URLs are set by the approved frontend/API tooling.
- **Dependencies:** `T-P1-SH-001`, `T-P1-SH-002`.
- **Contract Dependencies:** `CON-04`, `CON-05`, `CON-06`, `CON-09`.
- **Acceptance Criteria:** Adaptive layouts work across phone, tablet, and desktop viewport sizes; map layers and date filters operate through the approved API; loading, empty, error, and data-quality states are clear; displayed estimates include provenance/limitations; no scientific output is fabricated.
- **Testing Requirements:** Browser/component and API integration checks appropriate to the approved stack; exact tools TBD in DEC-01. Use only explicitly labeled synthetic fixtures for software testing.
- **Blockers:** DEC-01 approval and framework/tooling selection, including a capacity check for Member C's combined backend/API, frontend, contracts, and integration responsibilities; can otherwise use contract-conforming synthetic fixtures during software development.

#### `T-P2-AP-003`: Temporal Analytics Charts & Tabular Export Module
- **Objective:** Implement field analytics displaying available NDVI/EVI/SAR trajectories, estimated growth-stage transition markers, and downloadable CSV summary tables. Chart library and browser interaction patterns follow approved DEC-01 architecture.
- **Primary Owner:** Member C
- **Reviewer:** Member A
- **File Ownership:** `frontend/`, `src/dashboard/`, `tests/dashboard/` (exact paths follow approved DEC-01 architecture)
- **Inputs:** `CON-03`, `CON-05`, `CON-08`, `CON-09`.
- **Outputs:** Chart widgets and CSV export buttons.
- **Dependencies:** `T-P2-AP-002`.
- **Contract Dependencies:** `CON-03`, `CON-05`, `CON-08`, `CON-09`.
- **Acceptance Criteria:** Charts expose units, time support, missing-data gaps, and estimate status; table downloads include valid headers, units, and provenance metadata where applicable.
- **Testing Requirements:** Check CSV generation and chart serialization using tools selected with the approved frontend.
- **Blockers:** None.

---

### Phase P3: System Integration & Verification

#### `T-P3-IN-001`: End-to-End Pipeline Wiring & Contract Validation
- **Objective:** Connect Member A data pipeline directly to Member B scientific models and Member C spatial aggregator on a staging branch.
- **Primary Owner:** Member C (Coordinator)
- **Reviewer:** Member A & Member B
- **File Ownership:** `src/pipeline.py`, `tests/integration/test_end_to_end.py`
- **Inputs:** Real or sample GEE outputs.
- **Outputs:** Single-command execution script executing complete AgriSense workflow.
- **Dependencies:** All P2 tasks completed and shared contracts approved.
- **Contract Dependencies:** `CON-01` through `CON-09`.
- **Acceptance Criteria:** Pipeline runs without type errors or schema violations from raw query to dashboard data bindings.
- **Testing Requirements:** Integration test covering data ingestion -> classification -> phenology -> stress -> water balance -> canal aggregation.
- **Blockers:** Module interface mismatches must be resolved via contract amendments.

---

### Phase P4: Real-Data Campaign Execution

#### `T-P4-DE-006`: Seasonal Observation Acquisition for Study Area
- **Objective:** Ingest and cache complete seasonal Sentinel-1, Sentinel-2, and ERA5-Land records for the designated study area.
- **Primary Owner:** Member A
- **Reviewer:** Member B
- **File Ownership:** `data/cache/` (Gitignored), `scripts/download_season.py`
- **Inputs:** Finalized `config/study_area.geojson` and confirmed date range.
- **Outputs:** Cached composite rasters ready for model inference.
- **Dependencies:** `T-P3-IN-001`.
- **Contract Dependencies:** `CON-03`.
- **Acceptance Criteria:** Complete temporal coverage with all cloud masking applied and SAR ratio calculated.
- **Testing Requirements:** Integrity check on cached GeoTIFF bounds, CRS, and non-null pixel ratios.
- **Blockers:** GEE export task limits or network timeouts.

#### `T-P4-SC-006`: Real-Data Model Inference & Advisory Generation
- **Objective:** Run Random Forest classifier, phenology extractor, stress detector, and FAO-56 balance across the real seasonal dataset.
- **Primary Owner:** Member B
- **Reviewer:** Member C
- **File Ownership:** `data/outputs/` (Gitignored), `scripts/run_inference.py`
- **Inputs:** Cached seasonal rasters from `T-P4-DE-006`.
- **Outputs:** Real-data crop map on the declared analysis grid, stage estimates, candidate stress indicators, and depth-balance outputs with resolution, provenance, and limitations.
- **Dependencies:** `T-P4-DE-006`.
- **Contract Dependencies:** `CON-04`, `CON-05`, `CON-06`, `CON-07`, `CON-08`.
- **Acceptance Criteria:** Model completes inference without out-of-memory errors; predictions fall within valid physical bounds.
- **Testing Requirements:** Check outputs against bounds justified by the approved method and sourced parameters; do not use unverified numeric ranges as scientific acceptance criteria.
- **Blockers:** Uncalibrated model producing nonsensical classifications.

---

### Phase P5: Scientific Validation & Evaluation

#### `T-P5-SC-007`: Classification Metrics, Confusion Matrix & Spatial Hold-Out Evaluation
- **Objective:** Compute Overall Accuracy, Cohen's Kappa, Macro-F1, and per-class error matrices using spatially segregated ground-truth test folds.
- **Primary Owner:** Member B
- **Reviewer:** Member A and the Guide; the held-out labels and evaluation design must be independent of model fitting.
- **File Ownership:** `src/evaluation/metrics.py`, `docs/VALIDATION_REPORT.md`
- **Inputs:** `CON-04` real classification outputs and independently sourced, held-out ground truth.
- **Outputs:** Numerical evaluation tables and published validation report.
- **Dependencies:** `T-P4-SC-006`.
- **Contract Dependencies:** `CON-04`.
- **Acceptance Criteria:** Strictly honest, uninflated metrics; zero spatial leakage between train and test sets.
- **Testing Requirements:** Unit tests verifying accuracy calculation mathematics.
- **Blockers:** Size and quality of independent test label dataset.

#### `T-P5-SC-008`: False-Alarm Comparison & Uncertainty Analysis
- **Objective:** Compare candidate stage-aware indicators with a documented static baseline and report any measured false-alarm change only when independent labels and the evaluation design support that conclusion; document ERA5-Land resolution limitations.
- **Primary Owner:** Member B
- **Reviewer:** Member C & Guide
- **File Ownership:** `docs/VALIDATION_REPORT.md`, `src/evaluation/uncertainty.py`
- **Inputs:** `CON-06` stress outputs vs. baseline static threshold outputs.
- **Outputs:** Comparative false-alarm results (direction and magnitude only if supported) and uncertainty narrative.
- **Dependencies:** `T-P4-SC-006`.
- **Contract Dependencies:** `CON-06`.
- **Acceptance Criteria:** Explicitly documents conditions where stress detection is uncertain or ambiguous.
- **Testing Requirements:** Select an evaluation method appropriate to the available independent reference data and sample size; do not require significance testing without a defensible design.
- **Blockers:** None.

---

### Phase P6: Documentation, Demonstration & Academic Presentation

#### `T-P6-AP-004`: Final Dashboard Polishing & Demonstration Packaging
- **Objective:** Polish UI styling, optimize map rendering speed, package demonstration sample data, and verify clean-clone execution.
- **Primary Owner:** Member C
- **Reviewer:** Member A & Member B
- **File Ownership:** `app.py`, `docs/USER_GUIDE.md`
- **Inputs:** Final integrated system and validation findings.
- **Outputs:** Fully functional, reliable demonstration web application.
- **Dependencies:** Phase P5 completion.
- **Contract Dependencies:** All.
- **Acceptance Criteria:** Dashboard starts from cached inputs and presents only implemented, traceable outputs; measure performance rather than assuming a target.
- **Testing Requirements:** Fresh clone test in an isolated Python virtual environment.
- **Blockers:** None.

#### `T-P6-SH-003`: Final Academic Slide Deck & IDP Presentation Delivery
- **Objective:** Synthesize project results, literature gap resolution (G1–G5), architecture, and validation metrics into final IDP review presentation.
- **Primary Owner:** Member C (Coordinator)
- **Supporting Contributors:** Member A and Member B provide their owned deliverables and participate in the defense.
- **Reviewer:** Dr. Muthuraja S (Project Guide)
- **File Ownership:** Presentation slides (external to repo) & final documentation review.
- **Inputs:** All Phase P0–P5 artifacts and evaluation findings.
- **Outputs:** Successful final project defense and university portal submission.
- **Dependencies:** `T-P6-AP-004`, `T-P5-SC-007`.
- **Contract Dependencies:** None.
- **Acceptance Criteria:** Formal approval from Dr. Muthuraja S.
- **Testing Requirements:** Rehearsal demonstration.
- **Blockers:** None.

---

## 4. Task Dependency Graph

```
[T-P1-SH-001] (Environment & Linting)
      │
      ├──► [T-P1-SH-002] (Data Contract Schemas)
      │          │
      │          ├──► [T-P1-SC-001] (Synthetic Fixtures)
      │          │          │
      │          │          ├──► [T-P2-SC-002] (RF Crop Classifier)
      │          │          ├──► [T-P2-SC-003] (Phenology Tracker)
      │          │          │          │
      │          │          │          ├──► [T-P2-SC-004] (Stage-Aware Stress)
      │          │          │          └──► [T-P2-SC-005] (FAO-56 Water Balance)
      │          │          │                     │
      │          ├──► [T-P2-AP-001] (Canal Aggregator)
      │          │          │
      │          └──► [T-P2-AP-002] (Responsive Dashboard Base)
      │                     │
      │                     └──► [T-P2-AP-003] (Analytics & Charts)
      │
      └──► [T-P1-DE-001] (GEE Authentication)
                 │
                 ├──► [T-P2-DE-002] (Sentinel-2 Ingestion)
                 ├──► [T-P2-DE-003] (Sentinel-1 Ingestion)
                 └──► [T-P2-DE-004] (ERA5-Land Ingestion)
                            │
                            ▼
                      [T-P2-DE-005] (Compositing & Fusion)
                            │
                            ▼
      ┌──────────────────────────────────────────────┐
      │  [T-P3-IN-001] System Integration Pipeline   │
      └─────────────────────┬────────────────────────┘
                            │
                            ▼
      ┌──────────────────────────────────────────────┐
      │  [T-P4-DE-006] Seasonal Data Ingestion       │
      │  [T-P4-SC-006] Real-Data Model Inference     │
      └─────────────────────┬────────────────────────┘
                            │
                            ▼
      ┌──────────────────────────────────────────────┐
      │  [T-P5-SC-007] Accuracy & Cross-Validation   │
      │  [T-P5-SC-008] False-Alarm & Uncertainty     │
      └─────────────────────┬────────────────────────┘
                            │
                            ▼
      ┌──────────────────────────────────────────────┐
      │  [T-P6-AP-004] Dashboard Demo Polishing      │
      │  [T-P6-SH-003] Final Defense Presentation    │
      └──────────────────────────────────────────────┘
```

---

## 5. Summary of Shared Responsibilities

1. **Architecture & Contract Reviews:** All three members must sign off on any contract change in `src/contracts/`.
2. **Scientific Decision Log:** Any change to scientific assumptions in `docs/DECISIONS.md` requires agreement between Member A and Member B, with Member C informed.
3. **Weekly Progress Checkpoints:** Every Friday, all three members update their task statuses in `docs/STATUS.md` and report active blockers.
4. **Academic Guide Sync:** Bi-weekly status demonstrations presented to Dr. Muthuraja S to confirm project alignment.
