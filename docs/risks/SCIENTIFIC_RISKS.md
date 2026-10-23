# AgriSense — Scientific & Engineering Risk Register

> **Project:** AI-Driven Automated Crop Type, Moisture Stress Detection and Irrigation Advisory  
> **Phase:** 0 — Foundation & Planning  
> **Last Updated:** 2026-10-23  
> **Status:** All risks Open — initial register

> [!IMPORTANT]
> Two risks are flagged as **BLOCKER** (RISK-01, RISK-16). These must be resolved before meaningful Phase 1 work can begin. The team should treat these as the highest-priority action items in the Phase 0 → Phase 1 gate review.

> **Scope update:** Project owner approved the India-first multi-region design direction on 2026-10-23. The initial AOI is unselected. RISK-09 (transferability), RISK-12 (licensing), RISK-16 (undefined AOI), and RISK-01 (labels) remain open. These blockers gate region-dependent scientific work, not independent documentation, source review, or setup tasks whose inputs are available.

---

## Summary Table

| ID | Title | Category | Likelihood | Impact | Owner | Status |
|----|-------|----------|------------|--------|-------|--------|
| RISK-01 | Missing or Unreliable Ground-Truth Labels | Scientific | High | Critical | All | Open |
| RISK-02 | Class Imbalance and Spatial Leakage | Scientific | Medium | High | Member B | Open |
| RISK-03 | Cloud Contamination and Temporal Gaps | Scientific | High | High | Member B | Open |
| RISK-04 | Resolution Mismatch Between Datasets | Engineering | High | High | Member A + Member B | Open |
| RISK-05 | Uncertainty in Crop Calendars and Phenology | Scientific | Medium | High | Member B | Open |
| RISK-06 | Confounding Factors in Moisture-Stress Indicators | Scientific | Medium | High | Member B | Open |
| RISK-07 | Missing or Uncertain FAO-56 Inputs | Scientific | High | High | Member A + Member B | Open |
| RISK-08 | Uncertainty in Irrigation Recommendations | Scientific | Medium | Critical | Member A + Member B | Open |
| RISK-09 | Geographic Transferability | Scientific | High | High | All | Open |
| RISK-10 | Google Earth Engine Access and Quotas | Engineering | Medium | Medium | Member A | Open |
| RISK-11 | Compute and Storage Constraints | Engineering | Medium | Medium | Member A | Open |
| RISK-12 | Dataset Licensing and Provenance | Operational | Low | Medium | All | Open |
| RISK-13 | Three-Member Scope and Delivery Risk | Operational | High | High | All | Open |
| RISK-14 | Integration and Ownership Conflicts | Operational | Medium | High | All (Member C coordinates) | Open |
| RISK-15 | SAR Data Interpretation Complexity | Scientific | Medium | Medium | Member B | Open |
| RISK-16 | Study Area Not Defined | Scientific | High | Critical | All | Open |
| RISK-17 | Canal Boundary Data Availability | Engineering | High | High | Member A | Open |

---

## Risk Details

---

### RISK-01: Missing or Unreliable Ground-Truth Labels

| Field | Value |
|-------|-------|
| Category | Scientific |
| Cause | No ground-truth label source is identified in either the IDP Review PDF or the Mava hackathon PDF. The project specifies a Random Forest crop classifier (F2) but provides no training labels, reference crop maps, or field survey protocol. |
| Consequence | Without verified labels, the classifier cannot be trained or validated. All downstream outputs — phenology tracking (F3), stage-aware stress detection (F4), and FAO-56 water balance (F6) — depend on correct crop type assignment. An unvalidated classifier invalidates the entire pipeline. |
| Likelihood | High |
| Impact | Critical — **BLOCKER** |
| Mitigation | (1) Prioritize ground-truth acquisition as the first Phase 1 task. (2) Investigate existing crop maps: India LULC, state agriculture department crop statistics, FASAL/CHAMAN project outputs. (3) Visual interpretation of VHR imagery (Google Earth, Bing Maps) as a labeling source with documented protocols. (4) Cross-validation approaches: spatial k-fold, leave-one-block-out. (5) If no ground truth is available, document this as an acknowledged limitation and report only relative (unsupervised) results. |
| Validation Strategy | Verify that a labeling source exists and covers the chosen study area before initiating classifier training. Measure inter-annotator agreement if visual interpretation is used. |
| Owner Role | All |
| Status | Open |

---

### RISK-02: Class Imbalance and Spatial Leakage

| Field | Value |
|-------|-------|
| Category | Scientific |
| Cause | In most agricultural landscapes, one or two dominant crops (e.g., rice or wheat) cover the majority of area, while minor crops (pulses, oilseeds, vegetables) occupy small, scattered patches. If training samples are drawn randomly, dominant classes will be over-represented. Additionally, adjacent pixels are spatially autocorrelated — drawing train and test samples from the same field or neighbourhood inflates accuracy metrics without reflecting genuine generalization. |
| Consequence | (1) Classifier biased toward dominant classes; minority crops under-detected. (2) Reported accuracy (OA, Kappa) overstates real-world performance due to spatial leakage. (3) Downstream stress and irrigation advisories systematically miss minor-crop fields. |
| Likelihood | Medium |
| Impact | High |
| Mitigation | (1) Stratified sampling: ensure minimum sample count per crop class, oversample rare classes or undersample dominant ones. (2) Spatial blocking: assign entire fields or spatial blocks (not individual pixels) to train vs. test sets to prevent leakage. (3) Report per-class precision, recall, and F1 alongside overall accuracy and Kappa. (4) Use confusion matrices to expose systematic misclassifications. |
| Validation Strategy | Compare spatially-blocked cross-validation accuracy with random-split accuracy; a large gap indicates leakage. Inspect per-class F1 scores for minority classes. |
| Owner Role | Member B |
| Status | Open |

---

### RISK-03: Cloud Contamination and Temporal Gaps

| Field | Value |
|-------|-------|
| Category | Scientific |
| Cause | Sentinel-2 optical imagery is subject to cloud, haze, and cloud-shadow contamination. The IDP Review PDF explicitly notes: *"Optical tools fail under cloud."* India's monsoon season (June–September) coincides with critical crop growth stages (Kharif sowing and vegetative growth), creating systematic temporal gaps in optical time series. |
| Consequence | Missing observations during critical growth stages degrades phenology extraction (F3), prevents timely stress detection (F4), and introduces gaps in NDVI/EVI time series that confound VCI computation. Cloud residuals not caught by masking introduce noise. |
| Likelihood | High |
| Impact | High |
| Mitigation | (1) Treat Sentinel-1 VH/VV as complementary radar observations with their own acquisition times, masks, and uncertainty; do not use radar values as optical observations or claim they fill cloudy optical gaps. (2) Select temporal compositing windows for the study and report observation support. (3) Any interpolation across optical gaps must be separately justified, labelled as an estimate, and must preserve missing-data flags and original observations. (4) Apply documented Sentinel-2 cloud/shadow quality screening. (5) Report valid observation counts and coverage as data-quality measures. |
| Validation Strategy | Map cloud-free observation count per pixel; flag regions with fewer than a defined minimum (e.g., < 5 clear observations in a season) as low-confidence zones. Compare interpolated vs. actual values where overlap exists. |
| Owner Role | Member A |
| Status | Open |

---

### RISK-04: Resolution Mismatch Between Datasets

| Field | Value |
|-------|-------|
| Category | Engineering |
| Cause | ERA5-Land is on an approximately 0.1° grid (Earth Engine's nominal pixel size is about 11.1 km), while Sentinel-2 has mixed native band resolutions and Sentinel-1 GRD can have 10 m pixel spacing despite coarser effective IW ground resolution. Sentinel-2 itself has mixed resolutions: 10 m (B2, B3, B4, B8), 20 m (B5, B6, B7, B8A, B11, B12), and 60 m (B1, B9, B10). |
| Consequence | When ERA5-Land values (temperature, rainfall, ET0) are resampled to 10 m pixels, the result does NOT represent genuine fine-resolution meteorological variation. Reprojecting or resampling does not create sub-grid weather information; retain the native cell identity and report the method used to align coarse meteorology with analysis outputs. This creates a false impression of spatial precision in the FAO-56 water balance (F6) and irrigation advisory (F7). |
| Likelihood | High |
| Impact | High |
| Mitigation | (1) Clearly document this resolution mismatch in all outputs and metadata. (2) Do NOT claim fine-resolution weather data; preserve the approximately 0.1° source-cell identity for meteorological inputs and any ET0 derived from them. (3) Preserve ERA5-Land provenance; if alignment resampling is necessary, choose and document a method that does not imply genuine fine-scale weather variation. (4) Record how Sentinel-2 20 m bands are aligned to the analysis grid. (5) Do not interpret aligned raster cell size as the effective spatial support of a water-balance estimate. |
| Validation Strategy | Verify that documentation explicitly states the resolution of each input dataset and that no output claims sub-grid meteorological variation. |
| Owner Role | Member A |
| Status | Open |

---

### RISK-05: Uncertainty in Crop Calendars and Phenology

| Field | Value |
|-------|-------|
| Category | Scientific |
| Cause | Crop calendars vary by region, crop variety, sowing date, and farmer practice. The project's phenology tracker (F3) detects growth stages from time-series inflection points, but this approach has inherent uncertainty: smoothing parameters affect inflection detection, mixed pixels blur stage transitions, and abnormal seasons shift calendars unpredictably. |
| Consequence | Incorrect growth stage assignment leads to wrong Kc coefficient selection → wrong ETc estimation → wrong deficit calculation → wrong irrigation advisory. Stage-aware stress thresholds (F4) applied at the wrong stage produce false alarms or missed detections. |
| Likelihood | Medium |
| Impact | High |
| Mitigation | (1) Use flexible, data-driven phenology detection rather than fixed calendar dates. (2) Validate detected phenology against known crop calendars from state agriculture departments or ICAR publications. (3) Report phenology confidence (e.g., sharpness of inflection) alongside stage assignment. (4) Allow manual override or adjustment of detected stages. (5) Test sensitivity of downstream outputs (Kc, deficit) to ±1 stage assignment errors. |
| Validation Strategy | Compare estimated phenology dates against an appropriate, sourced crop-stage reference if available; report method and limitations. |
| Owner Role | Member B |
| Status | Open |

---

### RISK-06: Confounding Factors in Moisture-Stress Indicators

| Field | Value |
|-------|-------|
| Category | Scientific |
| Cause | NDVI, VCI, and the specifically identified optical index variants can change for reasons beyond crop-water stress: natural senescence, residual cloud contamination, mixed pixels, pest or disease damage, fertilizer differences, and soil background. A stage-aware approach is only a candidate response to the source's research gap G2; its effect and all other confounders require evaluation. |
| Consequence | False-positive stress alerts (senescence interpreted as stress) or false-negative alerts (actual stress masked by confounders). Unreliable stress maps erode trust in irrigation advisories. |
| Likelihood | Medium |
| Impact | High |
| Mitigation | (1) Evaluate stage-conditioned rules only after the stages, index definitions, and thresholds are sourced and approved. (2) Treat agreement among optical indices and SAR as corroborating features to evaluate, not proof that stress is genuine. (3) Report confidence only when a method defines it. (4) Document that the system detects candidate vegetation anomalies, not definitive moisture stress. (5) Do not describe VH/VV as direct soil-moisture measurement or independent ground truth. |
| Validation Strategy | Evaluate false-alarm rate (FAR) against known non-stress events (harvest, fallow). If ground truth is available, measure stress detection precision and recall separately for each growth stage. |
| Owner Role | Member B |
| Status | Open |

---

### RISK-07: Missing or Uncertain FAO-56 Inputs

| Field | Value |
|-------|-------|
| Category | Scientific |
| Cause | A defensible FAO-56-based water balance needs an approved ET0 method/source, Kc source and crop/stage mapping, effective-rainfall method, and any soil/storage terms required by the selected balance. These choices and data sources are not specified in the PDFs; generic coefficients or reanalysis inputs may not be locally representative. ET0 is derived from meteorological variables using a selected method; it is not presumed to be a native ERA5-Land field. |
| Consequence | Water balance accuracy is fundamentally limited by input quality. A simple ETc-minus-effective-rainfall balance omits other soil-water and management terms unless explicitly included. Any estimated depth (mm) inherits input and method uncertainty and is not an operational prescription. |
| Likelihood | High |
| Impact | High |
| Mitigation | (1) Document the ET0 method/source, Kc provenance and mapping, effective-rainfall method, and soil/storage inputs actually used. (2) Conduct sensitivity analysis only over ranges supported by data or cited sources; do not imply unsupported precision. (3) Evaluate station comparisons if suitable, sourced station records are available. (4) Verify any soil map's provenance, native resolution, depth support, and license before selection; if required storage inputs are unavailable, do not substitute an unverified default. (5) Quantify uncertainty only with a defensible method; otherwise state that it is not quantified. |
| Validation Strategy | Compare derived ET0 with suitable independent station data if available. Validate a complete water balance against appropriate independent field water-balance/soil-water observations if available; irrigation-release records alone do not validate crop demand without delivery, timing, and field-level accounting. |
| Owner Role | Member B |
| Status | Open |

---

### RISK-08: Uncertainty in Irrigation Recommendations

| Field | Value |
|-------|-------|
| Category | Scientific |
| Cause | The project proposes irrigation-deficit estimates, but depth units should be mm. These are model estimates, not verified prescriptions calibrated against field measurements. Area-times-depth can estimate a gross volume in m³ under stated spatial-coverage assumptions; estimating an operational release additionally requires delivery efficiency, hydraulic, and scheduling information. |
| Consequence | If recommendations are interpreted as operational commands rather than advisory estimates, there is a risk of over-irrigation (waterlogging, nutrient leaching) or under-irrigation (yield loss). This has direct consequences for farmers and canal managers who are identified as target users. |
| Likelihood | Medium |
| Impact | Critical |
| Mitigation | (1) Label ALL irrigation outputs as **"advisory estimates"** — never as prescriptions or commands. (2) Quantify uncertainty where a defensible method and inputs exist; otherwise report that uncertainty is not quantified rather than inventing confidence values. (3) Require explicit human review (irrigation officer) before any operational action. (4) Add a disclaimer on the dashboard: "These values are model estimates for decision support. They should not replace professional irrigation management judgment." (5) Distinguish area-derived gross volume from operational canal release; do not recommend gate operations without delivery and hydraulic data. |
| Validation Strategy | Review all dashboard text and output labels to confirm "advisory" framing. Verify that uncertainty bounds are displayed alongside deficit values. |
| Owner Role | Member B |
| Status | Open |

---

### RISK-09: Geographic Transferability

| Field | Value |
|-------|-------|
| Category | Scientific |
| Cause | The model will be trained and validated in a single study area with specific crop types, growing seasons, soil types, climate patterns, and irrigation infrastructure. Crop spectral signatures, phenology patterns, and stress thresholds are all region-specific. |
| Consequence | Claims of generalizability to other regions are unsupported without separate validation. Deploying the model in a different agro-climatic zone without re-training could produce unreliable results. |
| Likelihood | Medium |
| Impact | Medium |
| Mitigation | (1) Document the study area, its agro-climatic characteristics, and the specific crops covered. (2) Do NOT claim generalization beyond the study area without explicit validation evidence. (3) If time permits, test on a second area to characterize transferability. (4) Design the pipeline to be parameterizable (crop list, Kc table, calendar) so it can be adapted to new regions with appropriate inputs. |
| Validation Strategy | If a second study area is tested, compare accuracy metrics between regions. Document which pipeline components are region-specific vs. generic. |
| Owner Role | All |
| Status | Open |

---

### RISK-10: Google Earth Engine Access and Quotas

| Field | Value |
|-------|-------|
| Category | Engineering |
| Cause | Google Earth Engine (GEE) is the primary data ingestion and processing platform (F1). GEE has usage quotas (concurrent computations, memory limits, export size limits), requires a Google account with Earth Engine access, and its API may change or be deprecated. Large-area, high-resolution (10 m) processing over multi-year time series can exceed free-tier limits. |
| Consequence | Processing delays, failed exports, or quota exhaustion during critical project phases. If GEE access is disrupted, the entire data pipeline stalls. |
| Likelihood | Medium |
| Impact | Medium |
| Mitigation | (1) Test with small spatial extents first before scaling to the full study area. (2) Implement efficient GEE code: server-side filtering, lazy evaluation, avoid `getInfo()` in loops. (3) Cache intermediate results (composites, index stacks) as GEE assets or Cloud Storage exports. (4) Document GEE quota limits encountered and workarounds. (5) Identify fallback data access (Copernicus Open Access Hub, Microsoft Planetary Computer) for critical datasets. |
| Validation Strategy | Run the full pipeline for a small test area (e.g., 10 km × 10 km) and log computation time, memory usage, and export sizes. Extrapolate to full study area. |
| Owner Role | Member A |
| Status | Open |

---

### RISK-11: Compute and Storage Constraints

| Field | Value |
|-------|-------|
| Category | Engineering |
| Cause | 10 m resolution Sentinel data for a meaningful study area generates large datasets. A single Sentinel-2 tile (100 km × 100 km) at 10 m has ~100 million pixels; multi-temporal stacks with multiple bands multiply this further. Local processing (downloading to laptop) may be infeasible for training and inference at scale. |
| Consequence | Slow processing, insufficient local storage, or inability to run the full pipeline if GEE server-side processing is not maximized. |
| Likelihood | Medium |
| Impact | Medium |
| Mitigation | (1) Maximize GEE server-side processing: perform all filtering, compositing, and index computation on GEE before exporting. (2) Export only the final products needed (classified maps, index composites), not raw imagery. (3) Process tiles or sub-regions incrementally rather than the entire area at once. (4) Use efficient data formats (GeoTIFF with LZW compression, Cloud Optimized GeoTIFF). (5) For ML training, extract point samples (not full rasters) from GEE. |
| Validation Strategy | Estimate total data volume for the full pipeline before starting Phase 1. Confirm that local storage and GEE quotas are sufficient. |
| Owner Role | Member A |
| Status | Open |

---

### RISK-12: Dataset Licensing and Provenance

| Field | Value |
|-------|-------|
| Category | Operational |
| Cause | The project uses multiple datasets with different licenses: Copernicus Sentinel data (free, open, with attribution requirements), ERA5-Land (Copernicus Climate Data Store license), and canal boundary shapefiles (source unknown, potentially restricted government data). Each dataset has specific terms of use, attribution requirements, and redistribution constraints. |
| Consequence | License violations could prevent publication or sharing of results. Inability to redistribute input data could hinder reproducibility. |
| Likelihood | Low |
| Impact | Medium |
| Mitigation | (1) Verify and document the license for every dataset used. (2) Include proper attribution in all outputs, publications, and the dashboard. (3) For potentially restricted datasets (canal boundaries), confirm permissions before use. (4) Maintain a data provenance table: dataset name, source URL, license type, access date, version. |
| Validation Strategy | Review the data provenance table at each phase gate. Confirm all attributions are present in deliverables. |
| Owner Role | All |
| Status | Open |

---

### RISK-13: Three-Member Scope and Delivery Risk

| Field | Value |
|-------|-------|
| Category | Operational |
| Cause | The project scope spans data engineering, machine learning, scientific modelling, geospatial processing, and web application development. Dependencies and unresolved data sources can affect delivery even with explicit owners and sequential handoffs. |
| Consequence | Risk of incomplete features, insufficient validation, or shallow implementation across too many modules. Time pressure may lead to cutting corners on documentation, testing, or scientific rigour. |
| Likelihood | High |
| Impact | High |
| Mitigation | (1) Prioritize the core pipeline (data → classification → stress → deficit) over advanced features. (2) Define clear task ownership per member to avoid duplication and gaps. (3) Set realistic milestones with explicit "minimum viable deliverable" for each phase. (4) Identify which features can be descoped if time runs short (e.g., canal aggregation could use administrative boundaries instead of actual canal commands). (5) Automate repetitive tasks (testing, data processing) early. |
| Validation Strategy | Review scope and blockers at formal phase gates. Preserve primary ownership; do not silently transfer tasks or weaken scientific acceptance criteria. |
| Owner Role | All |
| Status | Open |

---

### RISK-14: Integration and Ownership Conflicts

| Field | Value |
|-------|-------|
| Category | Operational |
| Cause | Sequentially developed modules (satellite data, weather/assembly, modelling, geospatial outputs, dashboard) must integrate into one pipeline. Interfaces may diverge if handoff artifacts, schema versions, provenance, and acceptance evidence are not recorded. |
| Consequence | Integration failures at assembly time. Incompatible data formats between modules. Duplicated or contradictory logic. Merge conflicts and rework. |
| Likelihood | Medium |
| Impact | High |
| Mitigation | (1) Define interface contracts (data schemas, file formats, function signatures) BEFORE implementation begins. (2) Designate a contract owner responsible for maintaining interface definitions. (3) Use the named task handoff and reviewer acceptance as integration checkpoints; formal phase gates remain separate. (4) Use version control (Git) with pull request reviews for all code changes. (5) Create integration tests that verify module interfaces. |
| Validation Strategy | Run end-to-end integration tests at each checkpoint. Verify that module outputs conform to agreed schemas. |
| Owner Role | All (Member C coordinates) |
| Status | Open |

---

### RISK-15: SAR Data Interpretation Complexity

| Field | Value |
|-------|-------|
| Category | Scientific |
| Cause | Sentinel-1 C-band SAR backscatter (VH, VV) is influenced simultaneously by: soil moisture, vegetation structure and biomass, surface roughness, crop geometry, and viewing geometry (incidence angle). Disentangling these contributions is a well-known challenge. Using VH/VV ratio or temporal VH changes for moisture stress detection is less established in the literature compared to optical indices. |
| Consequence | SAR-derived indicators are ambiguous: backscatter change can reflect crop growth, soil moisture, or surface roughness. Over-reliance on SAR for stress detection without understanding these confounders could produce unreliable results. |
| Likelihood | Medium |
| Impact | Medium |
| Mitigation | (1) Use SAR as a complementary observation; do not assume it can replace optical stress indicators or guarantee continuity. (2) When optical data is available, use optical indices as the primary stress signal and SAR as complementary. (3) Document the limitations of SAR-based stress detection clearly. (4) If SAR-only stress detection is attempted, validate against periods with concurrent clear optical data. (5) Consider using SAR primarily for crop classification (where multi-temporal SAR signatures are better established) rather than stress detection. |
| Validation Strategy | During cloud-free periods, compare SAR-derived stress indicators against optical-derived indicators. Measure agreement rate. |
| Owner Role | Member A + Member B |
| Status | Open |

---

### RISK-16: Study Area Not Defined

| Field | Value |
|-------|-------|
| Category | Scientific |
| Cause | Neither the IDP Review PDF nor the Mava hackathon PDF specifies a study area. The project mentions "canal irrigation" and "Wheat vs. Mustard" as example crops, but no geographic extent, state, district, or canal command area is named. |
| Consequence | All data acquisition, ground-truth labeling, crop calendar selection, Kc table selection, and ERA5-Land extraction depend on knowing the study area. This is a **BLOCKER** — no Phase 1 data engineering work can begin without a defined study area. |
| Likelihood | High |
| Impact | Critical — **BLOCKER** |
| Mitigation | (1) The team MUST define the study area before Phase 1 begins. (2) Selection criteria: availability of canal command boundaries, presence of target crops, data availability (cloud-free optical windows), accessibility for potential field validation. (3) Recommended approach: choose a well-studied canal command area in a Rabi-season wheat-growing region (e.g., parts of Haryana, Punjab, Rajasthan, or Uttar Pradesh) where reference data may be available. (4) Document the rationale for the choice. |
| Validation Strategy | Confirm that the chosen study area has: (a) Sentinel-2 coverage, (b) identifiable canal infrastructure, (c) known crop types, and (d) available crop calendar information. |
| Owner Role | All |
| Status | Open |

---

### RISK-17: Canal Boundary Data Availability

| Field | Value |
|-------|-------|
| Category | Engineering |
| Cause | Feature F7 (Canal Command Boundary Aggregator) and Sub-Objective O3 require canal command boundary shapefiles to aggregate pixel-level deficits to canal-level advisories. However, no data source for these boundaries is identified in either PDF. Canal command area boundaries are typically maintained by state irrigation departments and may not be publicly available in digital (shapefile) format. |
| Consequence | Without canal boundaries, the aggregation step (F7) cannot be implemented, and the canal-level irrigation advisory (O3) — a key differentiator of this project — is blocked. |
| Likelihood | High |
| Impact | High |
| Mitigation | (1) Contact the local irrigation department or state water resources department for the chosen study area. (2) Check India-WRIS (Water Resources Information System) for digitized canal network data. (3) Check OpenStreetMap for canal network features. (4) As a fallback, use administrative boundaries (village, block, or district) instead of canal commands — this reduces the project's novelty but maintains the aggregation functionality. (5) As a last resort, manually digitize canal commands from satellite imagery if the area is small. |
| Validation Strategy | Confirm that boundary data exists in usable format (shapefile, GeoJSON) before Phase 1 milestone for F7. |
| Owner Role | Member A |
| Status | Open |

---

## Risk Review Schedule

The risk register is a living document. Risks should be reviewed, updated, and re-scored at each project phase gate:

| Review Point | Timing | Focus |
|-------------|--------|-------|
| **Phase 0 → Phase 1 Gate** | Before data acquisition begins | Resolve BLOCKERS (RISK-01, RISK-16, RISK-17). Confirm study area, ground-truth strategy, and canal boundary source. |
| **Phase 1 Mid-Point** | After initial data ingestion | Reassess RISK-03 (cloud coverage for chosen area/season), RISK-04 (resolution handling), RISK-10/11 (GEE quotas and compute). |
| **Phase 1 → Phase 2 Gate** | Before ML training begins | Confirm ground-truth quality (RISK-01), assess class balance (RISK-02), validate phenology assumptions (RISK-05). |
| **Phase 2 Mid-Point** | After initial model results | Reassess RISK-06 (confounders), RISK-07 (FAO-56 input quality), RISK-15 (SAR interpretation). |
| **Phase 2 → Phase 3 Gate** | Before dashboard integration | Review RISK-08 (advisory framing), RISK-14 (integration), RISK-13 (scope and delivery). |
| **Phase 3 Final Review** | Before submission | Full risk register review. Document which risks materialized, which were mitigated, and which remain as known limitations. Update RISK-09 (transferability) and RISK-12 (licensing) for final deliverable. |

> [!TIP]
> At each review, ask three questions for every risk:
> 1. Has the likelihood or impact changed based on new evidence?
> 2. Have the mitigations been implemented and are they effective?
> 3. Are there new risks that should be added to the register?

---

*Document generated as part of AgriSense Phase 0 — Foundation & Planning.*
