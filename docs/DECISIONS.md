# AgriSense Architectural Decision Records (ADRs)

> **Governance Notice:** This log distinguishes project-owner direction from team technical confirmation. The project owner has stated that guide sign-off is unavailable; no guide approval is claimed or used as a blocker. Shared contract changes still require all three human team members' approval. Scientific claims and validation require evidence regardless of decision status.

---

## Decision Index

| Decision ID | Topic | Status | Proposed Date | Approver Role |
|:---|:---|:---|:---|:---|
| **`DEC-01`** | Application Architecture: Streamlit vs. Responsive Web Frontend + Python API | **Owner-selected direction; team technical confirmation open** | 2026-10-23 | Project Owner; team review |
| **`DEC-02`** | Satellite Data Processing Platform: Google Earth Engine vs. Local Downloads | **Owner-preferred: GEE; team review open** | 2026-10-23 | Peter + Rishav; no guide prerequisite recorded |
| **`DEC-03`** | Crop Classification Algorithm: Random Forest vs. Deep Learning (CNN/LSTM) | **Owner-approved baseline: Random Forest; team review open** | 2026-10-23 | All 3 Members; no guide prerequisite recorded |
| **`DEC-04`** | Phenology Estimation: SciPy Curve Inflection vs. Fixed Calendar Rules | **Owner-preferred candidate: evaluate SciPy time-series methods** | 2026-10-23 | Rishav; no guide prerequisite recorded |
| **`DEC-05`** | Stress Detection: Dynamic Stage-Aware Thresholds vs. Static VCI/NDVI | **Owner-preferred research direction; thresholds/method unapproved** | 2026-10-23 | Rishav + Peter review; no guide prerequisite recorded |
| **`DEC-06`** | Agro-Meteorological Data Source: ERA5-Land Reanalysis vs. Station Data | **Owner-preferred: ERA5-Land with native-resolution limits** | 2026-10-23 | Peter + Rishav; no guide prerequisite recorded |
| **`DEC-07`** | Canal Aggregation Strategy: Vector GeoPandas vs. Server-Side GEE Zonal Stats | **Owner-preferred: local vector summary, conditional on valid boundaries** | 2026-10-23 | Peter + Ashwanth C; no guide prerequisite recorded |
| **`DEC-08`** | Intermediate Data Caching: Local GeoTIFF Cache vs. Cloud Object Storage | **Owner-preferred: local ignored cache for initial build** | 2026-10-23 | Peter + Ashwanth C; no guide prerequisite recorded |
| **`DEC-09`** | Software Testing Data Integrity: Pure Synthetic Fixtures vs. Sample Data | **Owner-approved integrity rule: labelled synthetic fixtures for software tests only** | 2026-10-23 | All 3 Members |
| **`DEC-10`** | India-first Multi-Region Scope and Regional Configuration | **Project-owner approved; team implementation review open** | 2026-10-23 | Project Owner; team review for implementation |
| **`DEC-11`** | Initial Multi-Region Candidate AOIs: Punjab and Tamil Nadu | **Initial candidate review; broadened by DEC-14; AOIs open** | 2026-10-23 | Project Owner + all 3 Members |
| **`DEC-12`** | Initial Crop Catalogue and Model Class Scope | **Owner direction; model classes depend on verified labels** | 2026-10-23 | Project Owner; team review |
| **`DEC-13`** | Canal Aggregation Scope | **Deferred from first build; may be reconsidered with licensed boundaries and approved inputs** | 2026-10-29 | Project Owner under delegated member approval |
| **`DEC-14`** | Evidence-Led First Pilot: TGRAC Agriculture2 and I&CAD Command Boundaries | **Owner-approved evidence audit; SRSP Stage I is a lead candidate only; final AOI open** | 2026-10-23 | Project Owner; team review before final AOI/data use |

## Approval Record — 2026-10-29

The user instructed that their message be treated as universal approval from every member for approval steps needed to continue this work. This grants delegated authorization for implementation and technical choices within the request. It is recorded as user-reported authorization; it is not an individual member's post-implementation verification and does not establish third-party data rights, provider credentials, source provenance, or scientific validity. Those evidence requirements remain open.

---

## Detailed Decision Records

### `DEC-10`: India-First Multi-Region Scope and Regional Configuration

- **Topic:** Project geographic scope and separation of shared pipeline behavior from region-specific inputs.
- **Status:** **APPROVED BY PROJECT OWNER — 2026-10-23; team implementation review and any shared-contract approval remain open.**
- **Decision:** Design AgriSense for an India-first multi-region direction. Punjab and Tamil Nadu were the initial candidate states recorded in `DEC-11`; the candidate review was broadened by `DEC-14`, and no state or AOI is preselected as final. Use region/season-specific configuration and provenance; do not embed state-specific assumptions in shared modules or claim transferability without independent evaluation.
- **Constraints:** This approval does not select an AOI, crop classes, season, dataset, algorithm parameters, or technology stack. Any amendment to shared contracts still requires all three team members' approval.
- **Required next decisions:** Regional profile fields/representation; pilot AOI; crop/season scope; evaluation extent.

### `DEC-11`: Initial AOI Set for Punjab and Tamil Nadu

- **Topic:** Evidence-based selection or deferral of the first pilot region/AOI.
- **Status:** **Initial candidate states for evidence audit; review broadened by `DEC-14`; specific AOIs remain open.**
- **Decision direction:** Assess candidate AOIs in the initial Punjab/Tamil Nadu review set, and extend the search where the evidence warrants it under `DEC-14`. Do not equate a state-level crop statistics table with field-level labels. The OGD Punjab portal lists district/season/crop production and area statistics; Tamil Nadu's portal includes crop area/production and land-use statistics. These help identify crop/season availability, but are not sufficient satellite training labels on their own. See [Punjab crop production statistics](https://punjab.data.gov.in/catalog/district-wise-season-wise-crop-production-statistics-0), [Tamil Nadu principal-crop statistics](https://tn.data.gov.in/resource/area-production-and-productivity-principal-crops-shb-2019), and [Tamil Nadu district land-use statistics](https://tn.data.gov.in/catalog/classification-land-districts-tamil-nadu-scr-2018-19).
- **Decision rule:** Compare concrete AOIs using the same season and criteria: Sentinel-1/2 usable coverage; traceable georeferenced crop labels suitable for training and independent testing; boundary suitability and license; crop/season diversity and calendar references; weather/soil inputs; irrigation evidence and command boundaries if retained; and validation feasibility. Do not finalize AOIs or create boundary files before that review.
- **Required approvers:** Project owner and all three members for selected AOIs; guide approval is not assumed as a prerequisite unless the team later requests it.

### `DEC-12`: Initial Crop Catalogue and Model Class Scope

- **Topic:** Broad crop catalogue versus the supervised classification scope.
- **Status:** **Owner direction recorded; data-supported model class list open.**
- **Decision direction:** Build an extensible crop database/catalogue for crop types represented by the selected source datasets, with names/aliases and region/season provenance. For the initial model, use only classes with verified, traceable labels in the selected AOI(s) and seasons. Do not claim exhaustive all-crop classification or add classes based only on an aggregate crop statistics table.
- **Acceptance rule:** Each modeled class has source, geography, season/date, label semantics, licensing, and enough independent support to define a defensible evaluation split; unsupported classes remain catalogue-only/unavailable for the model.

### `DEC-13`: Canal Aggregation Scope

- **Topic:** Canal-command summaries in the initial deliverable.
- **Status:** **Deferred from the first build on 2026-10-29 under the user's delegated approval on behalf of all members.**
- **Decision direction:** Retain descriptive canal-command aggregation only when authoritative, licensed command boundaries and suitable estimates exist. Defer it for any AOI lacking those inputs. Administrative or district boundaries must never be relabeled as canal commands. No operational release, gate-control, or irrigation schedule recommendation is implied.
- **Effect:** DS-05 is no longer an entry blocker for the first build because the canal-aggregation deliverable is out of the first-build scope. It remains a prerequisite before any later canal-command aggregation. This decision does not authorize use or redistribution of any TGRAC or NWIC geometry.
- **Required approvers:** User's 2026-10-29 delegated approval covers member approval for this scope decision; guide approval is not assumed as a prerequisite unless the team later requests it.

### `DEC-14`: Evidence-Led First Pilot: TGRAC Agriculture2 and I&CAD Command Boundaries

- **Topic:** Evidence-based selection of one real irrigation-command area for an initial pilot that supports both crop classification and irrigation-advisory research.
- **Status:** **OWNER-APPROVED EVIDENCE AUDIT; no final AOI or dataset-use approval. `DS-09` remains open.** This broadens the initial candidate-state review recorded in `DEC-11`; it does not cancel the India-first, multi-region scope in `DEC-10` or select a state by preference alone.
- **Approved review direction:** Inspect the TGRAC Agriculture2 CropAnalysis ground-truth layers for February, March, and April 2023 and TGRAC I&CAD project/command boundaries. Compare candidate commands using verifiable label coverage, spatial overlap, acquisition availability, boundary provenance, reuse terms, study period, crop/season support, and the evidence available for irrigation-advisory validation. Select the strongest verifiable public-data combination; do not infer an AOI from a service title or administrative geography.
- **Evidence checkpoint (2026-10-23):** The read-only audit retrieved 2,446 point records from TGRAC layers 10–12 and seven polygons each from I&CAD layers 9 and 10. The named polygons in layers 9 and 10 have coordinate-identical geometries. `SRSP STAGE I` has the largest observed intersection (147 points: 84 February, 46 March, 17 April), making it the lead candidate for additional verification. Its `Ayacut_ha` attribute is 433,249; this extent is not independently verified. The 12 records tagged Wanaparthy do not intersect any of the seven returned command polygons. See [DS-09 AOI evidence audit](DS09_AOI_AUDIT.md) for methods, candidate counts, Sentinel catalog matches, and limitations.
- **Recommendation:** Advance SRSP Stage I as the next candidate for suitability review because it has the greatest point overlap and records in all three month layers. Do not treat it as a selected/verified AOI: the boundary source vintage/authority and reuse terms are absent from layer metadata; record `CreationDate` is not confirmed as the field-observation date; labels/domains need provider review; and the returned data do not contain measured moisture stress, irrigation quantity/timing, or recommendation outcomes. The large attributed command area and rare-class support also need assessment.
- **Sentinel evidence limit:** Copernicus Data Space STAC products intersecting SRSP point footprints were found in the February–April 2023 window. Temporal proximity was checked against `CreationDate` as an explicitly unverified proxy, not as confirmed observation-date matching. Catalog presence does not prove cloud-free usable pixels or a valid scientific feature stack.
- **Required before final selection / closing `DS-09`:** Confirm source lineage/version and reuse terms for labels and boundaries; establish the authoritative I&CAD layer/vintage and verify topology/area; confirm survey date semantics, point meaning/positional quality, crop-label validity, and a non-leaking spatial holdout; inspect usable pixel coverage; identify independent field evidence for moisture-stress and irrigation-advisory validation; and document the selected study period. If the Wanaparthy focus is retained, identify a matching real command and adequate labels because its 12 tagged points are outside these seven polygons.
- **Scope controls:** Keep one real command-area pilot as the first target and maintain multi-region capability. This decision changes no task ID, primary owner, file-ownership boundary, architecture, or shared API contract. It does not mark `DS-04`, `DS-05`, or `DS-09` complete and does not authorize model fitting, accuracy claims, or operational irrigation advice.
- **Required approvers:** The project owner approved this evidence-based planning direction. Final AOI selection and use of a data source remain subject to the project’s existing member-review rules; no guide approval is asserted.

### `DEC-01`: Application Architecture & Technology Stack

- **Topic:** High-level web application and backend architecture.
- **Status:** **React + TypeScript / FastAPI implementation direction approved per the project owner's 2026-10-29 instruction to treat member approvals as complete; no individual review records were collected in this workspace.**
- **Context:** The source documents request an interactive GIS-enabled dashboard with nominal 10 m crop outputs, growth stage estimates, stress indicators, and canal-boundary summaries. Two architectural options were evaluated:
  1. *Streamlit Monolith (Python-only):* Single-process Python application utilizing `streamlit-folium` for interactive maps and `plotly` for temporal graphs; this is the source documents' implementation proposal.
  2. *Responsive Web Frontend + Python API:* React + TypeScript and FastAPI are candidate technologies. No PostGIS/GeoServer requirement has been established.
- **Alternatives Considered:**
  - *Option 1 (Streamlit Monolith):* Native Python, fast iteration, minimal boilerplate, and directly proposed in reference documents.
  - *Option 2 (Responsive Web Frontend + Python API):* Supports a custom responsive interface and separates UI from scientific services, but introduces frontend tooling, API integration, and deployment coordination.
- **Recommendation:** Use **Option 2: React + TypeScript responsive browser frontend with a FastAPI Python API**. The user has explicitly authorized approval steps on behalf of all members for this work. Reviewers still need to verify the implementation and deployment fit; no guide response is recorded.
- **Rationale:**
  - The reference documents propose Streamlit (IDP PDF Sub-Objective O3, page 23; `mava.pdf` Feature F8 and Tech Stack, page 9); they do not prevent the team from selecting another implementation for the same dashboard objective.
  - The owner prioritizes a polished, adaptive dashboard experience. The selected stack direction remains subject to team technical confirmation; deployment and libraries remain open.
- **Consequences & Trade-offs:**
  - *Potential benefits:* Custom responsive layouts and clear separation between browser presentation and Python scientific processing.
  - *Costs and open questions:* Frontend/API integration, separate tooling, deployment topology, and mapping/chart library choices must be decided before implementation.
- **Evidence / Source:** `IDP_Review_1_AgriSense (1).pdf` p. 23; `mava.pdf` p. 9.
- **Required Approver Role:** Project owner and all three members. The owner directed that approval from the other members be considered complete for implementation. This is recorded as owner-reported delegated authorization, not as individual member review artifacts. No guide approval is assumed or recorded.

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
- **Required Approver Role:** Peter and Rishav confirm provider choice and access; no guide approval is assumed.

---

### `DEC-03`: Crop Classification Algorithm

- **Topic:** Selection of supervised classification model for 10 m pixel crop mapping.
- **Status:** **OWNER-APPROVED BASELINE — team confirmation open; model configuration unapproved**
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
- **Required Approver Role:** All three members confirm the baseline; class list, parameters, and scientific validity remain data-dependent.

---

### `DEC-04`: Phenology Estimation Methodology

- **Topic:** Algorithm for growth stage transition detection from irregular satellite time series.
- **Status:** **OWNER-PREFERRED CANDIDATE — method and parameters require evidence-based selection**
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
- **Status:** **OWNER-PREFERRED RESEARCH DIRECTION — no threshold or validated method approved**
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
- **Required Approver Role:** Rishav proposes method/parameters; Peter reviews crop-calendar and water-balance implications. No guide approval is assumed.

---

### `DEC-06`: Agro-Meteorological Data Source

- **Topic:** Source for reference evapotranspiration ($ET_0$) and precipitation forcing.
- **Status:** **OWNER-PREFERRED SOURCE — Peter/Rishav access and method review open**
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
- **Status:** **OWNER-PREFERRED CONDITIONAL METHOD — member review and boundary availability open**
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
- **Status:** **OWNER-PREFERRED INITIAL APPROACH — member review open**
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
- **Status:** **OWNER-APPROVED INTEGRITY RULE — team review recorded through the Phase 0 baseline**
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
