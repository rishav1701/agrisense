# AgriSense Task Assignments & Work Breakdown Structure

> **P0 baseline approved by the three-member team per project-owner confirmation (2026-10-23); guide sign-off waived by the project owner for P0. P1 execution remains subject to the listed entry prerequisites and task dependencies.**
> **Team Allocation:** Exactly three human student members. The project owner approved the proposed allocation and sequential handoff plan; this records the approved Phase 0 baseline and role plan, not approval of individual scientific decisions. Member A is Peter Livins (weather, water-balance support, geospatial); Member B is Rishav Raj (satellite data, ML, scientific modelling); Member C is Ashwanth C (application, dashboard, integration).
> **Execution mode:** Sequential, non-overlapping stage handoffs are preferred. A member can work from an accepted handoff package without monitoring another member's day-to-day progress. This does not waive formal phase gates or shared-contract approval.
> **All-work approval and review report (2026-10-31):** The project owner reports that all three members approved proceeding with the remaining work and reviews, and that Members A and B manually reviewed the implementation branch. Record this as owner-reported delegated approval; separate member signatures/review artifacts are not stored here. Member approval does not waive dependencies or scientific/data evidence gates. Any proposed shared-contract amendment still needs its own explicit unanimous approval record.
> **Scope direction:** The project owner approved an India-first multi-region design direction and evidence-led pilot review on 2026-10-23 (`DEC-10`, `DEC-14`). Telangana/TGRAC is currently a lead candidate; SRSP Stage I is not a selected AOI. Existing task IDs, primary owners, reviewers, and file boundaries are retained. Region-dependent scientific work remains gated by sourced AOI/data/method inputs; independent foundation, learning, and source-inventory work may proceed without a pilot.
> **Academic Project:** BACSE291 — Innovative Design Project, VIT Vellore (Fall 2026).
> **Guide:** Dr. Muthuraja S, Assistant Professor Sr. Grade 1.

---

## 1. Team Role Allocation Overview

| Team Member | Primary Domain | Core Responsibilities | File / Directory Ownership |
|:---|:---|:---|:---|
| **Member A — Peter Livins** | **Weather, Water-Balance Support & Geospatial Processing** | ERA5-Land and ET₀ workflow; final cross-source assembly/cache; spatial boundaries and canal aggregation; shared spatial/temporal data QA. | `src/data/gee_auth.py`, `era5land.py`, `observation_assembly.py`, `cache.py`; `src/spatial/`; corresponding tests; `config/study_area.geojson`, `config/kc_coefficients.yaml`, `.env.example` |
| **Member B — Rishav Raj** | **Satellite Data, Machine Learning & Scientific Modelling** | Sentinel-1/2 processing, satellite feature/time-series pipeline, RF classification, phenology, stage-aware stress modelling, evaluation and uncertainty analysis; review water-balance scientific inputs. | `src/data/sentinel1.py`, `sentinel2.py`, `preprocessing.py`; `src/models/classifier.py`, `phenology.py`, `stress.py`; `src/evaluation/`; corresponding tests; `config/crop_calendar.yaml` |
| **Member C — Ashwanth C** | **Application, Responsive Dashboard & Integration** | Browser dashboard, API/backend, visualisation, integration, error handling and deployment preparation; shared-contract coordination without unilateral approval. | `frontend/`, `src/api/`, `src/dashboard/`, `src/contracts/`, `tests/dashboard/`, `tests/integration/`, API boundary documentation |

> **Note on Member Skills & Availability:** Specific personal skillsets and academic schedules are marked as *pending confirmation*. AI coding agents may assist individual team members with code authoring and testing, but AI agents **do not count as team members** and cannot approve scientific decisions, validate results, or modify shared contracts.

---

## 2. File and Directory Ownership Matrix

To prevent merge conflicts, strict file boundaries govern ownership. Work proceeds in approved sequential stages; reviewers provide review at handoff and do not become co-owners.

| Directory / File Pattern | Primary Owner | Secondary Reviewer | Direct Edits Permitted by Others? |
|:---|:---|:---|:---|
| `src/data/sentinel1.py`, `sentinel2.py`, `preprocessing.py`; satellite tests | Member B (Rishav) | Member A (Peter) | **No.** Separate satellite feature work from weather/assembly files. |
| `src/data/gee_auth.py`, `era5land.py`, `observation_assembly.py`, `cache.py`; weather/assembly tests | Member A (Peter) | Member B (Rishav) | **No.** `observation_assembly.py` consumes the completed satellite package. |
| `src/models/classifier.py`, `phenology.py`, `stress.py`; corresponding tests | Member B (Rishav) | Member A (Peter) | **No.** PR/review required. |
| `src/models/water_balance.py`, `config/kc_coefficients.yaml`, water-balance tests | Member A (Peter) | Member B (Rishav) | **No.** Requires approved methods/inputs; Rishav reviews scientific assumptions. |
| `src/evaluation/**` | Member B (Rishav) | Member A (Peter) | **No.** PR with owner review required. |
| `frontend/**`, `src/api/**`, `src/dashboard/**` | Member C (Ashwanth C) | Member B (Rishav) | **No.** DEC-01 and API boundary approval to proceed are reported complete; producer-backed features still require accepted handoffs. |
| `src/spatial/**`, `tests/spatial/**` | Member A (Peter) | Member C (Ashwanth C) | **No.** Ashwanth reviews application integration at handoff. |
| `src/contracts/**` | Member C (Ashwanth C; custodian) | Member A (Peter) & Member B (Rishav) | **No.** Strict unanimous consensus required (all 3 members must approve PR). |
| `tests/contracts/**` | Member C (Ashwanth C) | Member A (Peter) & Member B (Rishav) | **No.** Contract tests must follow the approved shared schemas. |
| Satellite tests for `sentinel1.py`, `sentinel2.py`, `preprocessing.py` | Member B (Rishav) | Member A (Peter) | **No.** |
| Weather/assembly/cache tests | Member A (Peter) | Member B (Rishav) | **No.** |
| Classifier/phenology/stress model tests | Member B (Rishav) | Member A (Peter) | **No.** |
| `tests/models/test_water_balance.py` | Member A (Peter) | Member B (Rishav) | **No.** |
| `tests/dashboard/**` | Member C (Ashwanth C) | Member B (Rishav) | **No.** Owned by Member C. |
| `tests/integration/**` | Member C (Ashwanth C) | Member A (Peter) & Member B (Rishav) | Shared test suite; PR required. |
| `config/study_area.geojson` | Member A (Peter) | Member B & C | PR required. |
| `config/crop_calendar.yaml` | Member B (Rishav) | Member A (Peter) | PR required. |
| `config/kc_coefficients.yaml`| Member A (Peter) | Member B (Rishav) | PR required; source and method approval required. |
| `docs/STATUS.md` | Member C (Ashwanth C; coordinator) | Member A & B | Any member may update their checkpoint by PR; gate state requires evidence and approval. |
| `docs/DECISIONS.md` | All Members | Guide / Lead | PR required for any new decision entry. |
| `docs/data_audit/region_sources.md` | Member A (Peter Livins) | Member B & C | Separate source-inventory file; do not edit the crop-label audit file. |
| `docs/data_audit/crop_catalogue_and_labels.md` | Member B (Rishav Raj) | Member A & C | Separate crop/label source-inventory file; do not edit the regional weather/boundary audit file. |
| `AGENTS.md`, `README.md` | All Members | All Members | Unanimous review required for changes. |

---

## 3. Detailed Work Breakdown Structure by Phase

### Phase P1: Foundation & Contracts

#### `T-P1-SH-001`: Python Environment & Tooling Configuration
- **Objective:** Establish reproducible environment with pinned dependencies, ruff linting, black formatting, and pytest runner.
- **Primary Owner:** Member C (Ashwanth C)
- **Reviewer:** Member A (Peter) & Member B (Rishav)
- **File Ownership:** `requirements.txt`, `pyproject.toml`, `.gitignore`
- **Inputs:** Architecture specification (`docs/ARCHITECTURE.md`).
- **Outputs:** Functional virtual environment and zero-error test run.
- **Dependencies:** None.
- **Contract Dependencies:** None.
- **Acceptance Criteria:** `pip install -r requirements.txt` succeeds; `pytest` runs without error on Windows and Linux.
- **Testing Requirements:** Test that ruff and black execute cleanly in CI / local terminal.
- **Blockers:** None.
- **Status (updated 2026-10-31):** Dependency pins and pytest/Black/isort/Ruff configuration are implemented. Python 3.12 environment installation succeeded; 46 tests and 9 subtests passed at the recorded checkpoint. The project owner reports all three members approved proceeding with the work and reviews; no separate review artifacts are stored here.

**Start condition:** This foundation task may start as independent setup; completion does not declare P1 or the project phase complete.

#### `T-P1-SH-002`: Data Contract Schemas Implementation
- **Objective:** Translate abstract contracts (`CON-01` to `CON-09`) into strict Python dataclasses/Pydantic schemas with type enforcement and unit metadata.
- **Primary Owner:** Member C (Ashwanth C; Coordinator)
- **Reviewer:** Member A (Peter) & Member B (Rishav) (Mandatory Sign-off)
- **File Ownership:** `src/contracts/schemas.py`, `tests/contracts/test_schemas.py`
- **Inputs:** `docs/API_CONTRACTS.md`.
- **Outputs:** Validated `src/contracts/schemas.py` package.
- **Dependencies:** `T-P1-SH-001`.
- **Contract Dependencies:** `CON-01` through `CON-09`.
- **Acceptance Criteria:** All contract data structures instantiate, validate fields, and serialize/deserialize JSON/GeoJSON cleanly.
- **Testing Requirements:** Schema validation tests with valid and invalid input fixtures.
- **Blockers:** The contract amendment has unanimous approval from all three members (2026-10-23); implementation remains subject to the P1 entry gate and relevant decisions.

#### `T-P1-SH-003`: Browser/API Boundary Specification
- **Objective:** Document the proposed browser-to-API request/response boundary after DEC-01 selection, reusing approved scientific output contracts and specifying loading, empty, error, provenance, and uncertainty states.
- **Primary Owner:** Member C (Ashwanth C)
- **Reviewer:** Member A (Peter) & Member B (Rishav)
- **File Ownership:** Proposed API boundary section in `docs/ARCHITECTURE.md`; if it changes a shared contract, follow unanimous approval and edit `docs/API_CONTRACTS.md` only after approval.
- **Inputs:** Approved DEC-01 choice and `CON-01` through `CON-09`.
- **Outputs:** Reviewed API boundary specification for `T-P2-AP-002` and `T-P2-AP-003`.
- **Dependencies:** Gate 0; owner-selected DEC-01 with all-member approval to proceed reported 2026-10-31 before framework-specific implementation choices are recorded. The project owner has stated that guide sign-off is unavailable; no guide approval is recorded or assumed.
- **Acceptance Criteria:** Request/response shapes, error/loading/empty/data-quality semantics, provenance, and mapping to approved output contracts are documented; reviewers approve; shared-contract changes have explicit unanimous approval.
- **Status:** The boundary specification is documented in `docs/ARCHITECTURE.md` under `T-P1-SH-003` and was checked against the implemented health/readiness/study-area routes and browser states. The project owner reports all-member approval to proceed and manual A/B review of the implementation branch (2026-10-31); no separate review artifacts are represented here.
- **Blockers:** Product routes remain dependent on real producer modules and handoffs. No shared contract was changed.

#### `T-P1-DE-001`: Google Earth Engine Authentication & Project Initializer
- **Objective:** Set up GEE authentication flow, project binding, and connection verification helper.
- **Primary Owner:** Member A (Peter)
- **Reviewer:** Member C (Ashwanth C)
- **File Ownership:** `src/data/gee_auth.py`, `scripts/verify_gee.py`, `.env.example`
- **Inputs:** Google Cloud Project with Earth Engine API enabled.
- **Outputs:** Module to initialize Earth Engine securely without hardcoded credentials.
- **Dependencies:** `T-P1-SH-001`.
- **Contract Dependencies:** None.
- **Acceptance Criteria:** `verify_gee.py` connects and retrieves a test Earth Engine metadata object.
- **Testing Requirements:** Mocked auth unit test when offline; live smoke test when online.
- **Blockers:** Team members must have registered GEE developer accounts.

#### `T-P1-DE-002`: Candidate-Region Weather, Boundary, and Irrigation Data Inventory
- **Objective:** Identify and compare publicly documented sources for administrative/AOI boundaries, weather, soil, crop calendars, and irrigation/command context in evidence-supported candidate regions. Include the TGRAC candidate review in `DEC-14`; do not assume its boundary vintage, authority, or reuse terms.
- **Primary Owner:** Member A (Peter Livins).
- **Reviewers:** Member B (Rishav Raj) and Member C (Ashwanth C).
- **File Ownership:** `docs/data_audit/region_sources.md`.
- **Dependencies:** None; this is source research and does not require final AOIs.
- **Acceptance Criteria:** Each source records responsible agency, geographic/temporal coverage, spatial support, access status, license/terms, attribution, candidate district/area relevance, and evidence gaps. Administrative boundaries and canal-command boundaries are distinguished. Unknowns remain explicit.
- **Blockers:** None for the inventory; obtaining restricted or missing source data is out of scope until documented.

#### `T-P1-SC-001`: Synthetic Benchmark Fixtures & Baseline Verification
- **Objective:** Build synthetic raster arrays and mock time-series data conforming to `CON-03` for testing models without GEE dependency.
- **Primary Owner:** Member B (Rishav)
- **Reviewer:** Member C (Ashwanth C)
- **File Ownership:** `tests/fixtures/synthetic_raster.py`, `tests/fixtures/synthetic_timeseries.py`
- **Inputs:** `docs/API_CONTRACTS.md` schemas.
- **Outputs:** Generator functions producing synthetic S1, S2, and ERA5-Land numpy tensors.
- **Dependencies:** `T-P1-SH-002`.
- **Contract Dependencies:** `CON-03`.
- **Acceptance Criteria:** Synthetic fixtures pass all contract validation checks; explicitly labeled as synthetic.
- **Testing Requirements:** Ensure synthetic fixtures cannot be mistaken for real observations.
- **Blockers:** None.

**Start condition:** May start after the shared schemas in `T-P1-SH-002` are accepted. Fixtures are software-only and must not be described as region-specific observations or validation.

#### `T-P1-SC-002`: Candidate-Region Crop Catalogue and Label Feasibility Inventory
- **Objective:** Build an extensible crop catalogue from traceable public crop sources and assess whether candidate products provide georeferenced labels suitable for training and independent evaluation. Include the retrieved TGRAC candidate evidence in `DEC-14`, while keeping suitability, label semantics, terms, and study-area selection open.
- **Primary Owner:** Member B (Rishav Raj).
- **Reviewers:** Member A (Peter Livins) and Member C (Ashwanth C).
- **File Ownership:** `docs/data_audit/crop_catalogue_and_labels.md`.
- **Dependencies:** None; use public source research and do not assume a final AOI.
- **Acceptance Criteria:** Record dataset/source, crop names and aliases, spatial and temporal support, reference dates/seasons, label meaning, provenance, access/license/attribution, independence limitations, and whether each product is (a) aggregate crop statistics, (b) mapped crop product, or (c) field-level ground truth. Do not label aggregate statistics as model labels; identify viable gaps.
- **Blockers:** None for research; supervised training remains blocked until suitable verified labels and AOIs are selected.

#### `T-P1-SH-004`: Regional Profile and Provenance Specification
- **Status:** Specification completed in `docs/ARCHITECTURE.md`; it references existing contracts without amending them. The project owner reports all-member approval to proceed with implementation/review (2026-10-31); no individual review artifacts are represented here.
- **Objective:** Specify how AOI, crop/season support, region-specific references, profile versioning, and provenance will be represented without embedding regional assumptions in shared modules.
- **Primary Owner:** Member C (Ashwanth C; contract custodian).
- **Reviewers:** Member A (Peter) and Member B (Rishav); all three members approve any shared-contract change.
- **File Ownership:** Proposed profile section in `docs/ARCHITECTURE.md`; proposed schema amendments in `docs/API_CONTRACTS.md` only after unanimous approval.
- **Dependencies:** `T-P1-SH-002`; `DEC-10` scope direction.
- **Acceptance Criteria:** Profile fields, versioning, missing-input behavior, data provenance, region/season identifiers, and separation of generic versus regional parameters are documented; compatibility with `CON-01`–`CON-09` is reviewed; any contract amendment records unanimous approval.
- **Blockers:** No pilot AOI or region-specific values are selected. Do not create regional values or a boundary file by assumption; any future shared-contract amendment still requires unanimous approval.

---

### Rishav's First Satellite Learning and Prototype Sequence
After formal Gate 0 and Gate 1 approval, Rishav can take the satellite stage without waiting on daily progress from Peter or Ashwanth C. Before those gates, independent reading and method notes are non-implementation work only. The first owned steps are:
1. `T-P2-DE-002`: inspect Sentinel-2 L2A band/quality-band semantics and document chosen cloud/shadow mask behavior and index equations; begin implementation only after AOI and method decisions are approved.
2. `T-P2-DE-003`: inspect Sentinel-1 GRD VV/VH units, orbit metadata, and filtering assumptions; record unresolved orbit/filter choices before committing to a method.
3. `T-P2-DE-005`: build satellite-only feature/time-series assembly and a handoff manifest that reports grid, temporal support, missingness, and source provenance. Software examples are explicitly synthetic; they are not scientific evidence.
4. After Peter accepts the complete `CON-03` assembly handoff, start `T-P2-SC-002` classifier software, then phenology and stress tasks in dependency order. Fit/evaluation claims remain blocked on sourced labels and approved methods.

### Rishav's Build Session Readiness

**Can begin now:** `T-P1-SC-002` crop-catalogue/label feasibility research and Sentinel-1/2 learning notes. This requires no AOI-specific downloads and does not claim any candidate dataset is suitable ground truth.

**First tracked software build task:** `T-P1-SC-001` after Ashwanth completes and hands off `T-P1-SH-002`; use only labelled synthetic fixtures for software behavior.

**Before real satellite processing (`T-P2-DE-002`, `003`, `005`):**
1. Accepted P1 handoffs and approved shared observation contracts.
2. One sourced real irrigation-command pilot AOI selected through `DEC-14`, with verified geometry source, reuse terms, CRS, boundary vintage, and study period. Additional regions are included only if selected for a separate evidence-backed evaluation.
3. Crop/season inventory with source citations; candidate DS-04 labels with geometry/coordinates, label semantics, observation date/season, license, provenance, and an independent spatial/temporal holdout plan. District aggregate tables are insufficient by themselves.
4. Team confirmation of the selected provider (GEE or a documented alternative), working account/access if GEE is selected, and confirmation of data export/storage limits.
5. Reviewed decisions for optical collection/quality masking, SAR orbit/polarization/filtering, temporal compositing, analysis grid/CRS, index definitions, missing-observation handling, and feature-stack metadata. Keep source acquisition times, native resolution, masks and resampling explicit.

**Before supervised Random Forest fitting (`T-P2-SC-002`):** accepted `CON-03` handoff, supported crop-class map backed by verified labels, spatially/temporally isolated training-validation-test design, and approved feature/model configuration. If labels are not available for a candidate state, it cannot contribute supervised training or accuracy claims; report it as a data gap.

### Phase P2: Sequential Module Implementation and Handoffs

**Region-dependent gate:** A specific AOI, season, supported crop set, and relevant source/method approvals are required before AOI-specific acquisition, scientific calibration, training, or performance claims. Shared contract/schema changes require unanimous approval. Unblocked setup and literature/source review do not satisfy these gates.

#### Stage 1 — Member B (Rishav): Satellite Processing

#### `T-P2-DE-002`: Sentinel-2 Optical Data Ingestion & Cloud Masking
- **Objective:** Query Sentinel-2 L2A Surface Reflectance, apply cloud/shadow masking via documented quality bands, and calculate selected optical indices (NDVI, EVI, `NDWI_MCF` and/or `NDWI_GAO`).
- **Primary Owner:** Member B (Rishav)
- **Reviewer:** Member A (Peter)
- **File Ownership:** `src/data/sentinel2.py`, `tests/data/test_sentinel2.py`
- **Inputs:** `CON-01` (Study Area & Temporal Window).
- **Outputs:** Multi-spectral image collection with computed index bands.
- **Dependencies:** `T-P1-DE-001`, after Gate 0 and the shared P1 foundation; AOI and relevant method decisions must be approved.
- **Contract Dependencies:** `CON-01`, `CON-02`.
- **Acceptance Criteria:** Cloud pixels masked out; invalid values replaced with NaN/mask flags; optical indices match mathematical definitions.
- **Testing Requirements:** Unit tests using mocked GEE responses and synthetic raster arrays.
- **Blockers:** Study area boundaries must be defined in `config/study_area.geojson`.

#### `T-P2-DE-003`: Sentinel-1 SAR GRD Ingestion & Preprocessing
- **Objective:** Ingest Sentinel-1 GRD IW backscatter (VV, VH), filter orbit paths, apply speckle filtering, and compute cross-ratio ($VH/VV$).
- **Primary Owner:** Member B (Rishav)
- **Reviewer:** Member A (Peter)
- **File Ownership:** `src/data/sentinel1.py`, `tests/data/test_sentinel1.py`
- **Inputs:** `CON-01` (Study Area & Temporal Window).
- **Outputs:** SAR image collection with calibrated backscatter and ratio bands.
- **Dependencies:** `T-P1-DE-001`, after Gate 0 and the shared P1 foundation; AOI and relevant method decisions must be approved.
- **Contract Dependencies:** `CON-01`, `CON-02`.
- **Acceptance Criteria:** Correct polarization selection; ratio band properly computed; radar dB values within physical bounds.
- **Testing Requirements:** Unit tests on speckle filter logic and backscatter ratio calculations.
- **Blockers:** Confirm radar orbit preference (ascending vs. descending).

#### `T-P2-DE-005`: Satellite Feature and Time-Series Stack
- **Objective:** Prepare Sentinel-1 and Sentinel-2 features/time series on the approved grid and temporal convention, preserving modality provenance.
- **Primary Owner:** Member B (Rishav)
- **Reviewer:** Member A (Peter) & Member C (Ashwanth C)
- **File Ownership:** `src/data/preprocessing.py` and satellite preprocessing tests
- **Inputs:** Outputs of `T-P2-DE-002` and `T-P2-DE-003`.
- **Outputs:** Satellite portion of `CON-03`, ready for weather/assembly handoff.
- **Dependencies:** `T-P2-DE-002`, `T-P2-DE-003`.
- **Contract Dependencies:** `CON-03`.
- **Acceptance Criteria:** Features preserve common-grid metadata and native/effective resolution; SAR remains complementary to optical; valid-data fractions and provenance are recorded. No 8-day interval is assumed until approved.
- **Testing Requirements:** Verify spatial alignment, CRS consistency, feature calculations, missing-data handling, and temporal metadata.
- **Blockers:** Approved grid/temporal conventions and the pending AOI/orbit decisions.
- **Status (2026-10-29):** Generic `CON-03` satellite-array assembly and software-only checks are implemented on `feat/T-P2-SC-002-scientific-foundation`. It preserves per-variable timestamps and provenance and rejects shape/time mismatches; it does not acquire or align real imagery. Full task acceptance and handoff remain blocked on upstream Sentinel-1/2 outputs and approved AOI/grid/time conventions.
- **Member C review (2026-10-30):** Software boundary review found the generic assembler preserves source references, per-variable timestamps, masks, valid-data fractions, and declared shared-grid metadata. Focused tests pass. It does not independently verify source CRS/transform registration or perform alignment; full producer handoff remains unaccepted pending real imagery and approved grid/time/orbit conventions.

---


#### Stage 2 — Member A (Peter): Weather and Assembly

#### `T-P2-DE-004`: ERA5-Land Reanalysis Ingestion & ET0 Derivation
- **Objective:** Query daily ERA5-Land meteorological grids (temperature, solar radiation, dewpoint, wind speed, precipitation) and calculate reference evapotranspiration ($ET_0$) via FAO-56 Penman-Monteith.
- **Primary Owner:** Member A (Peter)
- **Reviewer:** Member B (Rishav)
- **File Ownership:** `src/data/era5land.py`, `tests/data/test_era5land.py`
- **Inputs:** `CON-01` (Study Area & Temporal Window).
- **Outputs:** Daily meteorological raster grid with $ET_0$ (mm/day) and precipitation (mm).
- **Dependencies:** `T-P1-DE-001`.
- **Contract Dependencies:** `CON-01`, `CON-02`.
- **Acceptance Criteria:** ET0 calculations follow the selected documented method and are checked against appropriate reference examples; native ERA5-Land grid identity is preserved and the collection's grid/temporal support is reported.
- **Testing Requirements:** Compare computed $ET_0$ against standard FAO-56 test example data.
- **Blockers:** ERA5-Land query/extraction and a daily gridded output require an approved study AOI/time interval, source-band mapping, and local-day/grid conventions. The pure ET0 calculation kernel is implemented and reference-tested; ingestion and product handoff remain open.


#### `T-P2-DE-006`: ERA5-to-Satellite Assembly and Cache
- **Objective:** Assemble the completed satellite package with ERA5-Land into approved `CON-03` and implement caching.
- **Primary Owner:** Member A (Peter)
- **Reviewer:** Member B (Rishav) & Member C (Ashwanth C)
- **File Ownership:** `src/data/observation_assembly.py`, `src/data/cache.py`, assembly/cache tests.
- **Inputs:** `T-P2-DE-005` satellite handoff and `T-P2-DE-004` weather outputs.
- **Outputs:** Complete validated `PreprocessedObservation` (`CON-03`) handoff.
- **Dependencies:** `T-P2-DE-004`, `T-P2-DE-005`, approved `CON-03` and temporal/grid decisions.
- **Acceptance Criteria:** ERA5-Land native grid/temporal support remains explicit; alignment is documented; no claim of genuine fine-resolution weather; cache preserves provenance and missingness.
- **Blockers:** Temporal convention, analysis-grid decisions, and storage availability.

#### Stage 3 — Member B (Rishav): Scientific Modelling

#### `T-P2-SC-002`: Random Forest Multi-Temporal Crop Classifier
- **Objective:** Implement the approved Random Forest configuration using sourced labels and seasonal features to generate crop maps on the declared analysis grid and uncertainty outputs.
- **Primary Owner:** Member B (Rishav)
- **Reviewer:** Member A (Peter)
- **File Ownership:** `src/models/classifier.py`, `tests/models/test_classifier.py`
- **Inputs:** `CON-03` (Preprocessed multi-temporal observation stacks) and Ground-Truth Labels (`DS-04`).
- **Outputs:** `CropClassificationResult` (`CON-04`) with class predictions and uncertainty layers.
- **Dependencies:** `T-P1-SC-001`, complete data handoff `T-P2-DE-006`.
- **Contract Dependencies:** `CON-03`, `CON-04`.
- **Acceptance Criteria:** Train/val/test splits strictly segregated by spatial blocks; produces per-pixel class ID and entropy/confidence score.
- **Class scope:** The crop catalogue may be broad, but this classifier supports only classes with verified, traceable labels for its AOIs and seasons; unavailable classes are not emitted as predictions.
- **Testing Requirements:** Unit test on synthetic arrays; verify model persistence (`joblib`) and inference reproducibility.
- **Blockers:** Sourcing ground-truth labels (`DS-04`) for study area.
- **Status (2026-10-29; review updated 2026-10-31):** Added the gated model adapter and optional scientific dependency set on `feat/T-P2-SC-002-scientific-foundation`. It requires declared label provenance, verified-label attestation, exact train/validation/test partition coverage with spatial groups isolated, and stable feature order. Synthetic-only software checks cover fitting, nodata, uncertainty semantics, and persistence. The project owner reports member approval to proceed with the software work and reviews. No study labels were used; production fit, scientific validation, and `CON-03` handoff remain open.

#### `T-P2-SC-003`: Time-Series Phenology Tracker & Inflection Extractor
- **Objective:** Evaluate a documented time-series smoothing and transition-detection method against available crop-specific references. Inflection dates are estimates; do not equate a greenness peak directly with flowering without validation.
- **Primary Owner:** Member B (Rishav)
- **Reviewer:** Member A (Peter)
- **File Ownership:** `src/models/phenology.py`, `config/crop_calendar.yaml`, `tests/models/test_phenology.py`
- **Inputs:** `CON-03` (NDVI/EVI time series) and `CON-04` (Crop Type).
- **Outputs:** `PhenologyEstimate` (`CON-05`) with growth stage ID, transition dates, and fit confidence.
- **Dependencies:** `T-P1-SC-001`, complete data handoff `T-P2-DE-006`, and `T-P2-SC-002` crop output.
- **Contract Dependencies:** `CON-03`, `CON-04`, `CON-05`.
- **Acceptance Criteria:** Handles irregular observations and gaps; reports uncertainty when observations are sparse; any crop-stage interpretation is validated against a documented crop calendar or independent reference.
- **Testing Requirements:** Unit tests against ideal synthetic double-logistic curves and noisy time series.
- **Blockers:** Region-specific crop calendar calibration (`DS-06`).

#### `T-P2-SC-004`: Growth-Stage-Aware Moisture-Stress Detector
- **Objective:** Evaluate dynamic, growth-stage-conditioned VCI/NDWI rules as candidate indicators; distinguish vegetation anomalies from confirmed crop-water stress.
- **Primary Owner:** Member B (Rishav)
- **Reviewer:** Member A (Peter)
- **File Ownership:** `src/models/stress.py`, `tests/models/test_stress.py`
- **Inputs:** `CON-03` (VCI when its baseline exists, selected and named optical index variants, and documented SAR features where available), `CON-05` (Estimated Growth Stage).
- **Outputs:** Candidate `StressIndicator` (`CON-06`) values with an explicit uncertain/insufficient-data state; categories and thresholds depend on the approved method.
- **Dependencies:** `T-P2-SC-003`, complete data handoff `T-P2-DE-006`.
- **Contract Dependencies:** `CON-03`, `CON-05`, `CON-06`.
- **Acceptance Criteria:** Implements only a documented, approved candidate rule; reports uncertain cases and does not present vegetation-index anomalies as confirmed moisture stress without independent evidence.
- **Testing Requirements:** Synthetic scenario tests comparing static VCI vs. dynamic VCI on flowering vs. senescing pixels.
- **Blockers:** None.

#### Stage 4 — Member A (Peter): Water Balance and Canal Geospatial Outputs

#### `T-P2-SC-005`: Crop Evapotranspiration and Water-Balance Engine
- **Objective:** Calculate daily crop evapotranspiration ($ET_c = K_c \times ET_0$) and, only after the water-balance method and inputs are approved, estimate a clearly defined depth balance in mm. Do not label this alone as a field-verified irrigation requirement or canal volume.
- **Primary Owner:** Member A (Peter)
- **Reviewer:** Member B (Rishav)
- **File Ownership:** `src/models/water_balance.py`, `config/kc_coefficients.yaml`, `tests/models/test_water_balance.py`
- **Inputs:** `CON-03` (ERA5-Land $ET_0$ and Precipitation), `CON-04` (Crop Type), `CON-05` (Growth Stage).
- **Outputs:** `CropEvapotranspirationEstimate` (`CON-07`) and, only when the method and required inputs are approved, `FieldWaterBalanceEstimate` (`CON-08`).
- **Dependencies:** `T-P2-SC-002`, `T-P2-SC-003`, `T-P2-DE-006`, and approved meteorological inputs/methods.
- **Contract Dependencies:** `CON-03`, `CON-04`, `CON-05`, `CON-07`, `CON-08`.
- **Acceptance Criteria:** The selected Kc source and stage mapping are traceable; depth units, assumptions, time window, missing inputs, and limitations are explicit. Quantify uncertainty only with a documented method. Scientific validation is reported separately from software tests.
- **Testing Requirements:** Validate water-balance numerical outputs against FAO-56 manual calculation examples.
- **Blockers:** A sourced and approved water-balance method and required soil/initial-storage inputs (`DS-08`); no regional default is assumed.

---

#### `T-P2-AP-001`: Canal Command Spatial Polygon Aggregator
- **Objective:** Ingest available canal-command boundary data, compute spatial overlays with approved depth estimates, and summarize zonal depth and area. Do not infer operational release volumes without the required delivery assumptions.
- **Primary Owner:** Member A (Peter)
- **Reviewer:** Member C (Ashwanth C)
- **File Ownership:** `src/spatial/canal_aggregator.py`, `tests/spatial/test_canal_aggregator.py`
- **Inputs:** Approved field water-balance estimates (`CON-08`) in mm and canal-command polygons (`DS-05`), if available.
- **Outputs:** Approved zonal summary with mapped area and mean depth; area-derived volume may be reported only with explicit assumptions and must not be presented as a gate-release prescription.
- **Dependencies:** `T-P2-SC-005`, sourced canal boundaries (`DS-05`), and approved shared contracts; execute in Stage 4.
- **Contract Dependencies:** `CON-08`, `CON-09`.
- **Acceptance Criteria:** Correct zonal aggregation and unit conversion, with valid-area accounting and documented coverage. Operational releases remain out of scope unless hydraulic and delivery data are available and approved.
- **Testing Requirements:** Spatial geometry tests using synthetic mock polygons and uniform deficit grids.
- **Status:** Deferred from the first build under `DEC-13` (2026-10-29 delegated member approval). Do not acquire or digitize a command boundary for this task until the scope is reopened and `DS-05` is resolved.
- **Blockers:** `DS-05` remains a blocker only if this task is reactivated for a later canal phase.

#### Stage 5 — Member C (Ashwanth C): API and Dashboard

#### `T-P2-AP-002`: Responsive Web Dashboard Base
- **Objective:** Build a professional responsive browser dashboard with an interactive map and toggleable Base Map, Crop Classification, Growth Stage, candidate Indicator, and available Water-Balance / Zonal Summary layers. Frontend framework, mapping library, Python API framework, and chart library require DEC-01 approval.
- **Primary Owner:** Member C (Ashwanth C)
- **Reviewer:** Member B (Rishav)
- **File Ownership:** `frontend/`, `src/api/`, `src/dashboard/`, `tests/dashboard/` (exact paths follow approved DEC-01 architecture)
- **Inputs:** `CON-04`, `CON-05`, `CON-06`, `CON-09` (Mock or cached).
- **Outputs:** Responsive interactive web dashboard; local development URLs are set by the approved frontend/API tooling.
- **Dependencies:** `T-P1-SH-003`, approved DEC-01, plus reviewed preceding-stage outputs.
- **Contract Dependencies:** `CON-04`, `CON-05`, `CON-06`, `CON-09`.
- **Acceptance Criteria:** Adaptive layouts work across phone, tablet, and desktop viewport sizes; map layers and date filters operate through the approved API; loading, empty, error, and data-quality states are clear; displayed estimates include provenance/limitations; no scientific output is fabricated.
- **Testing Requirements:** Browser/component and API integration checks appropriate to the approved stack; exact tools TBD in DEC-01. Use only explicitly labeled synthetic fixtures for software testing.
- **Blockers:** The owner has directed that member approvals be treated as complete for this work. Product-layer, date-filter, chart, and export behavior still depends on real producer outputs and accepted handoffs. Do not populate these interfaces with fabricated estimates.
- **Status (2026-10-29):** A foundation-level local demo now includes API-backed capability status, an AOI GeoJSON preview, and structural date/geometry request validation. This is not completion of interactive scientific map layers or a data-connected dashboard; those remain dependent on real, reviewed producer outputs.
- **Status (2026-10-31):** Added functional zoom-in, zoom-out, and fit-to-boundary controls for the locally uploaded AOI preview. This remains a geometry preview; basemap and producer-backed scientific layers are not connected.

#### `T-P2-AP-003`: Temporal Analytics Charts & Tabular Export Module
- **Objective:** Implement field analytics displaying available NDVI/EVI/SAR trajectories, estimated growth-stage transition markers, and downloadable CSV summary tables. Chart library and browser interaction patterns follow approved DEC-01 architecture.
- **Primary Owner:** Member C (Ashwanth C)
- **Reviewer:** Member A (Peter)
- **File Ownership:** `frontend/`, `src/dashboard/`, `tests/dashboard/` (exact paths follow approved DEC-01 architecture)
- **Inputs:** `CON-03`, `CON-05`, `CON-08`, `CON-09`.
- **Outputs:** Chart widgets and CSV export buttons.
- **Dependencies:** `T-P2-AP-002`, `T-P1-SH-003`.
- **Contract Dependencies:** `CON-03`, `CON-05`, `CON-08`, `CON-09`.
- **Acceptance Criteria:** Charts expose units, time support, missing-data gaps, and estimate status; table downloads include valid headers, units, and provenance metadata where applicable.
- **Testing Requirements:** Check CSV generation and chart serialization using tools selected with the approved frontend.
- **Blockers:** No producer endpoint or accepted data handoff is connected yet; chart/export integration with real outputs remains gated on upstream products and reviewed handoffs. The current reusable component and empty state satisfy the UI foundation only.
- **Status (2026-10-31):** A provenance-aware chart/export component, empty state, local JSON import, and half-open date-range filtering are implemented. The selected interval filters series, stage transitions, and CSV export. Imported views stay in browser memory; no producer endpoint is connected, no scientific validity is inferred, and no product is bundled. Software tests use explicitly synthetic test-only fixtures.

---

### Phase P3: System Integration & Verification

#### `T-P3-IN-001`: End-to-End Pipeline Wiring & Contract Validation
- **Objective:** Connect Member A data pipeline directly to Member B scientific models and Member C spatial aggregator on a staging branch.
- **Primary Owner:** Member C (Ashwanth C; Coordinator)
- **Reviewer:** Member A (Peter) & Member B (Rishav)
- **File Ownership:** `src/pipeline.py`, `tests/integration/test_end_to_end.py`
- **Inputs:** Real or sample GEE outputs.
- **Outputs:** Single-command execution script executing complete AgriSense workflow.
- **Dependencies:** All P2 tasks completed and shared contracts approved.
- **Contract Dependencies:** `CON-01` through `CON-09`.
- **Acceptance Criteria:** Pipeline runs without type errors or schema violations from raw query to dashboard data bindings.
- **Testing Requirements:** Integration test covering data ingestion -> classification -> phenology -> stress -> water balance -> canal aggregation.
- **Blockers:** The required upstream P2 producer modules and accepted CON-03–CON-09 handoffs are not available in this workspace. Implementing an end-to-end runner now would require placeholder behavior or invented outputs. Resolve real module interfaces first; any shared-contract amendment requires unanimous approval.

---

### Phase P4: Real-Data Campaign Execution

#### `T-P4-DE-006`: Seasonal Observation Acquisition for Study Area
- **Objective:** Ingest and cache seasonal Sentinel-1, Sentinel-2, and ERA5-Land records for the accepted pilot command area, and any additional AOIs explicitly selected for an evidence-backed evaluation; identify coverage gaps by AOI/source.
- **Primary Owner:** Member B (Rishav)
- **Reviewer:** Member A (Peter)
- **File Ownership:** `data/cache/` (Gitignored), `scripts/download_season.py`
- **Inputs:** Finalized `config/study_area.geojson` and confirmed date range.
- **Outputs:** Cached composite rasters ready for model inference.
- **Dependencies:** `T-P3-IN-001`.
- **Contract Dependencies:** `CON-03`.
- **Acceptance Criteria:** Report actual coverage and gaps separately for each AOI/source; apply approved cloud masking and SAR feature definitions; do not describe incomplete coverage as complete.
- **Testing Requirements:** Integrity check on cached GeoTIFF bounds, CRS, and non-null pixel ratios.
- **Blockers:** GEE export task limits or network timeouts.

#### `T-P4-SC-006`: Real-Data Model Inference & Advisory Generation
- **Objective:** Run Random Forest classifier, phenology extractor, stress detector, and FAO-56 balance across the real seasonal dataset.
- **Primary Owner:** Member B (Rishav)
- **Reviewer:** Member C (Ashwanth C)
- **File Ownership:** `data/outputs/` (Gitignored), `scripts/run_inference.py`
- **Inputs:** Cached seasonal rasters from `T-P4-DE-006`.
- **Outputs:** Real-data crop map on the declared analysis grid, stage estimates, candidate stress indicators, and depth-balance outputs with resolution, provenance, and limitations.
- **Dependencies:** `T-P4-DE-006`.
- **Contract Dependencies:** `CON-04`, `CON-05`, `CON-06`, `CON-07`, `CON-08`.
- **Acceptance Criteria:** Model completes inference without out-of-memory errors; predictions fall within valid physical bounds.
- **Testing Requirements:** Check outputs against bounds justified by the approved method and sourced parameters; do not use unverified numeric ranges as scientific acceptance criteria.
- **Blockers:** Requires cached real seasonal inputs, accepted upstream model implementations, calibrated/sourced parameters, and verified provenance. Member C's review cannot proceed until Member B supplies actual inference artifacts.

---

### Phase P5: Scientific Validation & Evaluation

#### `T-P5-SC-007`: Classification Metrics, Confusion Matrix & Spatial Hold-Out Evaluation
- **Objective:** Compute agreed classification metrics using spatially segregated held-out ground-truth folds; where data support it, separately evaluate held-out seasons and transfer to an unseen region.
- **Primary Owner:** Member B (Rishav)
- **Reviewer:** Member A (Peter) and the Guide; the held-out labels and evaluation design must be independent of model fitting.
- **File Ownership:** `src/evaluation/metrics.py`, `docs/VALIDATION_REPORT.md`
- **Inputs:** `CON-04` real classification outputs and independently sourced, held-out ground truth.
- **Outputs:** Numerical evaluation tables and published validation report.
- **Dependencies:** `T-P4-SC-006`.
- **Contract Dependencies:** `CON-04`.
- **Acceptance Criteria:** Strictly honest metrics; zero spatial leakage; temporal and cross-region splits are explicitly identified and isolated from fitting/tuning. Report transfer failure or insufficient evidence without substituting in-region scores. Do not require every split where verified independent labels are unavailable; document that limitation.
- **Testing Requirements:** Unit tests verifying accuracy calculation mathematics.
- **Blockers:** Size and quality of independent test label dataset.

#### `T-P5-SC-008`: False-Alarm Comparison & Uncertainty Analysis
- **Objective:** Compare candidate stage-aware indicators with a documented static baseline within the supported region/season and, only where independent evidence exists, assess stability across regions/seasons; report measured false-alarm changes only when the evaluation design supports them.
- **Primary Owner:** Member B (Rishav)
- **Reviewer:** Member C (Ashwanth C) & Guide
- **File Ownership:** `docs/VALIDATION_REPORT.md`, `src/evaluation/uncertainty.py`
- **Inputs:** `CON-06` stress outputs vs. baseline static threshold outputs.
- **Outputs:** Comparative false-alarm results (direction and magnitude only if supported) and uncertainty narrative.
- **Dependencies:** `T-P4-SC-006`.
- **Contract Dependencies:** `CON-06`.
- **Acceptance Criteria:** Explicitly documents uncertain/ambiguous conditions, regional/season limits, and whether cross-region evidence exists. Classification metrics do not stand in for stress or advisory validation.
- **Testing Requirements:** Select an evaluation method appropriate to the available independent reference data and sample size; do not require significance testing without a defensible design.
- **Blockers:** Depends on actual stage-aware and baseline stress outputs plus independent reference evidence and an accepted evaluation design. Member C's review cannot proceed until the comparison and uncertainty report exist.

---

### Phase P6: Documentation, Demonstration & Academic Presentation

#### `T-P6-AP-004`: Final Dashboard Polishing & Demonstration Packaging
- **Objective:** Polish UI styling, optimize map rendering speed, package demonstration sample data, and verify clean-clone execution.
- **Primary Owner:** Member C (Ashwanth C)
- **Reviewer:** Member A (Peter) & Member B (Rishav)
- **File Ownership:** `frontend/`, `src/api/`, `docs/USER_GUIDE.md` (React + TypeScript and FastAPI implementation selected under DEC-01).
- **Inputs:** Final integrated system and validation findings.
- **Outputs:** Fully functional, reliable demonstration web application.
- **Dependencies:** Phase P5 completion.
- **Contract Dependencies:** All.
- **Acceptance Criteria:** Dashboard starts from cached inputs and presents only implemented, traceable outputs; measure performance rather than assuming a target.
- **Testing Requirements:** Fresh clone test in an isolated Python virtual environment.
- **Blockers:** Depends on completed integration and Phase P5 validation findings; no final producer-backed outputs or validation report are available yet.

#### `T-P6-SH-003`: Final Academic Slide Deck & IDP Presentation Delivery
- **Objective:** Synthesize project results, literature gap resolution (G1–G5), architecture, and validation metrics into final IDP review presentation.
- **Primary Owner:** Member C (Ashwanth C; Coordinator)
- **Supporting Contributors:** Member A and Member B provide their owned deliverables and participate in the defense.
- **Reviewer:** Dr. Muthuraja S (Project Guide)
- **File Ownership:** Presentation slides (external to repo) & final documentation review.
- **Inputs:** All Phase P0–P5 artifacts and evaluation findings.
- **Outputs:** Successful final project defense and university portal submission.
- **Dependencies:** `T-P6-AP-004`, `T-P5-SC-007`.
- **Contract Dependencies:** None.
- **Acceptance Criteria:** Formal approval from Dr. Muthuraja S.
- **Testing Requirements:** Rehearsal demonstration.
- **Blockers:** Depends on the final dashboard and accepted validation results; formal guide approval and university submission cannot be completed from this repository workspace.

---

## 4. Task Dependency Graph

```text
Gate 0 approval
      │
      ▼
P1 foundation: T-P1-SH-001 → T-P1-SH-002 → T-P1-SC-001
      ├─ T-P1-DE-001 (GEE setup)
      └─ T-P1-SH-003 (DEC-01/API boundary; unanimous approval for shared contract changes)
      │
      ▼
Stage 1 — Rishav: T-P2-DE-002 + T-P2-DE-003 → T-P2-DE-005 (satellite handoff)
      │
      ▼
Stage 2 — Peter: T-P2-DE-004 + accepted T-P2-DE-005 → T-P2-DE-006 (complete CON-03)
      │
      ▼
Stage 3 — Rishav: T-P2-SC-002 → T-P2-SC-003 → T-P2-SC-004
                      (classifier fitting/validation waits for sourced DS-04)
      │
      ▼
Stage 4 — Peter: T-P2-SC-005 (after CON-04/05 handoff) → T-P2-AP-001 (approved methods + DS-05)
      │
      ▼
Stage 5 — Ashwanth C: T-P2-AP-002 → T-P2-AP-003
      │
      ▼
T-P3-IN-001 → T-P4-DE-006 → T-P4-SC-006 → T-P5-SC-007 / T-P5-SC-008
      → T-P6-AP-004 / T-P6-SH-003
```

---

## 5. Summary of Shared Responsibilities

1. **Architecture & Contract Reviews:** All three members must sign off on any contract change in `src/contracts/`.
2. **Scientific Decision Log:** Any change to scientific assumptions in `docs/DECISIONS.md` requires agreement between Member A and Member B, with Member C informed.
3. **Progress policy:** Task completion is individual; a workstream handoff requires the task acceptance criteria and reviewer acceptance; phase completion requires every phase deliverable and formal exit gate. P1 completion by one member does not allow P2 to begin before Gate 1. Once Rishav starts his approved P2 satellite stage, he can complete it without monitoring Peter’s or Ashwanth C’s day-to-day progress; Peter starts the dependent assembly stage only after the satellite handoff is accepted.
4. **Status updates:** Update `docs/STATUS.md` at meaningful checkpoints and when blockers or formal gate decisions change. No daily cross-member status monitoring is required.
5. **Academic Guide Sync:** Bi-weekly status demonstrations presented to Dr. Muthuraja S to confirm project alignment.
