# AgriSense Architectural Decision Records (ADRs)

> **Governance Notice:** Decisions documented here govern the architectural direction of the AgriSense project. In accordance with Phase P0 standards, **all decisions are initially labeled `PROPOSED`** and require formal human team and guide approval before implementation. No decision may be marked `APPROVED` without recorded consensus.

---

## Decision Index

| Decision ID | Topic | Status | Proposed Date | Approver Role |
|:---|:---|:---|:---|:---|
| **`DEC-01`** | Application Architecture: Streamlit vs. Responsive Web Frontend + Python API | **PROPOSED** | 2026-10-23 | All 3 Team Members + Guide |
| **`DEC-02`** | Satellite Data Processing Platform: Google Earth Engine vs. Local Downloads | **PROPOSED** | 2026-10-23 | Member A & B |
| **`DEC-03`** | Crop Classification Algorithm: Random Forest vs. Deep Learning (CNN/LSTM) | **PROPOSED** | 2026-10-23 | Member B & Guide |
| **`DEC-04`** | Phenology Estimation: SciPy Curve Inflection vs. Fixed Calendar Rules | **PROPOSED** | 2026-10-23 | Member B |
| **`DEC-05`** | Stress Detection: Dynamic Stage-Aware Thresholds vs. Static VCI/NDVI | **PROPOSED** | 2026-10-23 | Member B & Guide |
| **`DEC-06`** | Agro-Meteorological Data Source: ERA5-Land Reanalysis vs. Station Data | **PROPOSED** | 2026-10-23 | Member A & B |
| **`DEC-07`** | Canal Aggregation Strategy: Vector GeoPandas vs. Server-Side GEE Zonal Stats | **PROPOSED** | 2026-10-23 | Member A & C |
| **`DEC-08`** | Intermediate Data Caching: Local GeoTIFF Cache vs. Cloud Object Storage | **PROPOSED** | 2026-10-23 | Member A & C |
| **`DEC-09`** | Software Testing Data Integrity: Pure Synthetic Fixtures vs. Sample Data | **PROPOSED** | 2026-10-23 | All 3 Team Members |

---

## Detailed Decision Records

### `DEC-01`: Application Architecture & Technology Stack

- **Topic:** High-level web application and backend architecture.
- **Status:** **PROPOSED**
- **Context:** The source documents request an interactive GIS-enabled dashboard with nominal 10 m crop outputs, growth stage estimates, stress indicators, and canal-boundary summaries. Two architectural options were evaluated:
  1. *Streamlit Monolith (Python-only):* Single-process Python application utilizing `streamlit-folium` for interactive maps and `plotly` for temporal graphs; this is the source documents' implementation proposal.
  2. *Responsive Web Frontend + Python API:* React + TypeScript and FastAPI are candidate technologies. No PostGIS/GeoServer requirement has been established.
- **Alternatives Considered:**
  - *Option 1 (Streamlit Monolith):* Native Python, fast iteration, minimal boilerplate, and directly proposed in reference documents.
  - *Option 2 (Responsive Web Frontend + Python API):* Supports a custom responsive interface and separates UI from scientific services, but introduces frontend tooling, API integration, and deployment coordination.
- **Recommendation:** The project owner prefers **Option 2**, a highly responsive and professional browser dashboard, and does not prefer Streamlit. React + TypeScript and FastAPI are provisional candidates only; team and guide approval and a three-member capacity check are still required.
- **Rationale:**
  - The reference documents propose Streamlit (IDP PDF Sub-Objective O3, page 23; `mava.pdf` Feature F8 and Tech Stack, page 9); they do not prevent the team from selecting another implementation for the same dashboard objective.
  - The owner prioritizes a polished, adaptive dashboard experience. The three-person constraint makes scope control and a capacity review essential; individual skills and availability remain unconfirmed.
- **Consequences & Trade-offs:**
  - *Potential benefits:* Custom responsive layouts and clear separation between browser presentation and Python scientific processing.
  - *Costs and open questions:* Frontend/API integration, separate tooling, deployment topology, mapping/chart library choices, and Member C workload must be assessed before implementation.
- **Evidence / Source:** `IDP_Review_1_AgriSense (1).pdf` p. 23; `mava.pdf` p. 9.
- **Required Approver Role:** All 3 Team Members and Project Guide.

---

### `DEC-02`: Satellite Data Processing Platform

- **Topic:** Cloud geoprocessing platform vs. local raw satellite raster downloads.
- **Status:** **PROPOSED**
- **Context:** Multi-temporal satellite processing can impose substantial storage and compute costs. The actual data volume and local capacity have not been measured for a study area.
- **Alternatives Considered:**
  - *Option 1 (Google Earth Engine API):* Server-side filtering, cloud masking, band math, and compositing, exporting only clipped 10 m analytical tiles to local disk.
  - *Option 2 (Local Processing via Copernicus Open Access Hub / Planetary Computer):* Download raw SAFE files and process using ESA SNAP and GDAL locally.
- **Recommendation:** Adopt **Option 1: Google Earth Engine Python API**.
- **Rationale:**
  - GEE provides instant access to petabyte-scale pre-calibrated archives (`COPERNICUS/S2_SR_HARMONIZED`, `COPERNICUS/S1_GRD`, `ECMWF/ERA5_LAND`).
  - Heavy raster calculations (cloud masking, temporal compositing, index generation) execute server-side on Google infrastructure with zero local download latency.
- **Consequences & Trade-offs:**
  - *Pros:* Massive reduction in local compute and bandwidth requirements; automated reproducibility across team members.
  - *Cons:* Requires project access and is subject to platform limits; the appropriate export scale and temporal interval remain to be assessed.
- **Evidence / Source:** `mava.pdf` Feature F1, p. 4; Gorelick et al. (2017) [Ref 24].
- **Required Approver Role:** Member A (Data Engineering) & Member B (Scientific Models).

---

### `DEC-03`: Crop Classification Algorithm

- **Topic:** Selection of supervised classification model for 10 m pixel crop mapping.
- **Status:** **PROPOSED**
- **Context:** The source asks for crop-type classification but does not define the study area or final class list. “Wheat vs. Mustard” appears as an example in Mava.
- **Alternatives Considered:**
  - *Option 1 (Random Forest):* Candidate ensemble classifier trained via Scikit-Learn on multi-temporal features; Mava names a 100-tree model, which remains a proposal to evaluate.
  - *Option 2 (Deep Learning - 1D-CNN / TempCNN / LSTM):* Temporal neural networks operating on raw reflectance sequences.
  - *Option 3 (Support Vector Machines - SVM):* Kernel-based margin classifier.
- **Recommendation:** Use Random Forest as the source-aligned candidate; confirm features, tree count, classes, and evaluation design before fixing a model configuration.
- **Rationale:**
  - Explicitly specified in both reference documents (IDP PDF Objective O1, page 23; `mava.pdf` Feature F2 & Tech Stack, page 9).
  - Random Forest handles high-dimensional multi-sensor feature spaces with resilience to noise and small sample sizes (Belgiu & Drăguţ, 2016 [Ref 28]).
  - Provides native feature importance metrics, requires minimal hyperparameter tuning, and executes inference in seconds on standard CPUs without GPU dependencies.
- **Consequences & Trade-offs:**
  - *Pros:* Fast training, explainable feature importances, low computational barrier.
  - *Cons:* Susceptible to spatial autocorrelation and training label noise if ground-truth samples are clustered (mitigated by spatial k-fold cross-validation).
- **Evidence / Source:** `IDP_Review_1_AgriSense (1).pdf` p. 4, 23; Breiman (2001) [Ref 46].
- **Required Approver Role:** Member B & Project Guide.

---

### `DEC-04`: Phenology Estimation Methodology

- **Topic:** Algorithm for growth stage transition detection from irregular satellite time series.
- **Status:** **PROPOSED**
- **Context:** Crop water demand ($K_c$) and moisture stress sensitivity vary radically by growth stage. Static calendar dates fail due to variable planting dates and weather anomalies.
- **Alternatives Considered:**
  - *Option 1 (SciPy Signal Processing):* Evaluate smoothing and transition-detection approaches on NDVI/EVI time series. Savitzky-Golay and derivative rules are candidate methods, not source-approved parameters.
  - *Option 2 (Fixed Calendar Thresholds):* Assuming standard day-count milestones from sowing date.
  - *Option 3 (TIMESAT Fortran/C Binary Wrapper):* External tool integration.
- **Recommendation:** Evaluate a SciPy-based approach; select smoothing and transition rules only after data-gap and crop-stage validation.
- **Rationale:**
  - IDP Sub-Objective O2 names a SciPy tracker and Mava Feature F3 proposes time-series inflection points; neither specifies Savitzky-Golay parameters or validates stage inference.
  - Keeps the entire pipeline within Python without external C/Fortran binary dependencies.
- **Consequences & Trade-offs:**
  - *Pros:* Tracks per-pixel seasonal shifts dynamically; robust against mild noise; purely Python-based.
  - *Risks:* Cloud gaps and sparse temporal observations can distort curve fitting; SAR backscatter is not a direct substitute for optical indices.
- **Evidence / Source:** `IDP_Review_1_AgriSense (1).pdf` p. 4, 23; Zeng et al. (2020) [Ref 11].
- **Required Approver Role:** Member B.

---

### `DEC-05`: Moisture-Stress Detection Strategy

- **Topic:** Dynamic stage-conditioned thresholding vs. static vegetation index thresholds.
- **Status:** **PROPOSED**
- **Context:** The project source motivates stage-aware indicators to reduce senescence-related false alarms. It does not establish a validated universal VCI cutoff or prove that a threshold-based indicator identifies crop-water stress.
- **Alternatives Considered:**
  - *Option 1 (Stage-Conditioned Candidate Indicator):* Evaluate how candidate vegetation indicators vary by estimated stage; label outputs as uncertain indicators unless independently validated.
  - *Option 2 (Static Thresholding):* Standard Kogan (1995) VCI thresholds applied universally across all dates.
- **Recommendation:** Evaluate Option 1 as a hypothesis; do not encode fixed thresholds or claim false-alarm reduction until supported by local independent evidence.
- **Rationale:**
  - Directly resolves Research Gap G2 identified in literature review (IDP PDF page 15).
  - Matches Core Innovation / Opportunity claimed in `mava.pdf` (page 3, 5): "recognises that moisture drops during flowering are critical, while the same drop during senescence is normal."
- **Consequences & Trade-offs:**
  - *Potential benefit to evaluate:* May reduce senescence-related false alarms if stage estimates and thresholds are appropriate and independently validated.
  - *Risks:* Depends on accurate phenology estimation; stage or indicator errors can create missed alerts or false positives.
- **Evidence / Source:** `IDP_Review_1_AgriSense (1).pdf` p. 15, 23; `mava.pdf` p. 3, 5.
- **Required Approver Role:** Member B & Project Guide.

---

### `DEC-06`: Agro-Meteorological Data Source

- **Topic:** Source for reference evapotranspiration ($ET_0$) and precipitation forcing.
- **Status:** **PROPOSED**
- **Context:** Calculating FAO-56 crop water balance ($ET_c = K_c \times ET_0$) requires daily temperature, solar radiation, wind speed, vapor pressure, and rainfall. Ground weather stations are sparse across rural command areas.
- **Alternatives Considered:**
  - *Option 1 (ECMWF ERA5-Land Reanalysis via GEE):* Gridded global land-surface reanalysis on an approximately 0.1° grid (Earth Engine reports a nominal 11,132 m pixel size); the selected collection's actual temporal support must be recorded.
  - *Option 2 (IMD Automated Weather Stations):* High point accuracy but sparse network and restricted automated API access.
  - *Option 3 (CHIRPS Precipitation + Generic Penman):* Multi-source blend.
- **Recommendation:** Adopt **Option 1: ECMWF ERA5-Land via Google Earth Engine**.
- **Rationale:**
  - Explicitly specified in both reference documents (IDP PDF page 3, 23; `mava.pdf` page 4, 9).
  - Readily accessible in GEE (`ECMWF/ERA5_LAND/DAILY_AGGR`) without separate licensing or external API scrapers.
- **Consequences & Trade-offs:**
  - *Pros:* Continuous, consistent global coverage with all necessary energy-balance parameters.
  - *Cons:* Coarse native grid. **Mandatory constraint:** Resampling ERA5-Land to a 10 m analysis grid must be explicitly labeled as spatial alignment; the project will not claim that it creates genuine fine-scale weather variations (Scientific Integrity Rule 4.1).
- **Evidence / Source:** Muñoz-Sabater et al. (2021) [Ref 4]; Hersbach et al. (2020) [Ref 13].
- **Required Approver Role:** Member A & Member B.

---

### `DEC-07`: Canal Command Aggregation Framework

- **Topic:** Method for aggregating pixel-level deficits into administrative canal polygons.
- **Status:** **PROPOSED**
- **Context:** Pixel or field depth estimates may be summarized across canal boundaries if inputs and geometry are available. A gross operational release volume requires additional area, delivery, and hydraulic assumptions.
- **Alternatives Considered:**
  - *Option 1 (Local Vector Processing via GeoPandas & Rasterio):* Export clipped raster arrays and perform zonal overlay and volume integration locally.
  - *Option 2 (Server-Side GEE Zonal Statistics):* Compute `reduceRegions` inside Google Earth Engine and export tabular results.
- **Recommendation:** Adopt **Option 1: Local GeoPandas + Rasterio Vector Aggregation**.
- **Rationale:**
  - IDP PDF page 4 and `mava.pdf` page 9 identify GeoPandas/Rasterio for spatial aggregation.
  - Decouples proprietary canal boundary shapefiles from Google Cloud storage; allows local interactive filtering without roundtrip cloud latency.
- **Consequences & Trade-offs:**
  - *Pros:* Fully open-source; runs locally in Python memory; facilitates flexible tabular aggregation.
  - *Cons:* Requires local memory allocation proportional to the number of pixels within the canal command polygon.
- **Evidence / Source:** `IDP_Review_1_AgriSense (1).pdf` p. 4; `mava.pdf` p. 9.
- **Required Approver Role:** Member A & Member C.

---

### `DEC-08`: Intermediate Data Caching Strategy

- **Topic:** Mechanism for caching preprocessed satellite composites and intermediate model outputs.
- **Status:** **PROPOSED**
- **Context:** To support responsive dashboard queries and permit offline model development, intermediate raster stacks must be persisted locally without exceeding Git or disk constraints.
- **Alternatives Considered:**
  - *Option 1 (Local Filesystem Cache in `data/cache/`):* Standard GeoTIFF / NumPy `.npy` files ignored by Git via `.gitignore`.
  - *Option 2 (Cloud Object Storage - AWS S3 / GCS Bucket):* Remote storage of all tiles.
  - *Option 3 (Relational Database with PostGIS Raster):* Storing raster tiles as database BLOBs.
- **Recommendation:** Adopt **Option 1: Local Filesystem Cache in `data/cache/` (Gitignored)**.
- **Rationale:**
  - Simple, robust, and zero-cost for a student project.
  - Avoids cloud hosting fees or database server configuration.
- **Consequences & Trade-offs:**
  - *Pros:* Zero external infrastructure; works seamlessly with Rasterio and GDAL; fast local I/O.
  - *Cons:* Requires each team member to generate or locally share sample cache tiles; strict `.gitignore` rules required to prevent accidental large binary commits.
- **Evidence / Source:** Project Architecture Guidelines (`docs/ARCHITECTURE.md`).
- **Required Approver Role:** Member A & Member C.

---

### `DEC-09`: Software Testing Data Integrity

- **Topic:** Policy on test fixtures and synthetic data.
- **Status:** **PROPOSED**
- **Context:** Coding agents and automated CI runners require test fixtures to verify module logic before live satellite data is acquired.
- **Alternatives Considered:**
  - *Option 1 (Pure Synthetic Mock Fixtures):* Mathematically generated NumPy arrays (random seeds, ideal curves) explicitly labeled as synthetic software tests.
  - *Option 2 (Sample Real Subsets):* Small real cropped satellite GeoTIFFs committed to repository.
  - *Option 3 (Hardcoded Simulated Outputs):* Plausible-looking static arrays presented as model predictions.
- **Recommendation:** Adopt **Option 1: Pure Synthetic Mock Fixtures (Strictly Labeled)**.
- **Rationale:**
  - Complies with Mandatory Scientific Integrity Rule: "Synthetic data is permitted only in explicitly labelled software tests — never as evidence of scientific performance."
  - Keeps repository size small (under 10 MB); ensures tests verify code logic without confusing software tests with scientific validation.
- **Consequences & Trade-offs:**
  - *Pros:* Rapid CI execution; total compliance with scientific integrity constraints; zero risk of data leakage.
  - *Cons:* Synthetic fixtures do not capture real-world sensor noise or cloud artifacts (real-world validation reserved for Phase P5).
- **Evidence / Source:** `AGENTS.md` Scientific Integrity Standards.
- **Required Approver Role:** All 3 Team Members.
