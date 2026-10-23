# AgriSense — Project Overview

> **Document Type:** Phase 0 — Architecture & Planning  
> **Status:** Draft — Awaiting Team Confirmation  
> **Created:** 2026-10-23  
> **Project Title:** AI-Driven Automated Crop Type, Moisture Stress Detection and Irrigation Advisory Across Growth Stages Using Moderate Resolution Spectral Signatures (Optical & Microwave Satellite Data)  
> **Domain:** Remote Sensing & Geospatial AI for Precision Agriculture and Water Resource Management

---

## Table of Contents

1. [Problem Statement and Motivation](#1-problem-statement-and-motivation)
2. [Objectives and Expected Outcomes](#2-objectives-and-expected-outcomes)
3. [Scope and Exclusions](#3-scope-and-exclusions)
4. [Intended Users and Supported Decisions](#4-intended-users-and-supported-decisions)
5. [End-to-End Scientific Workflow](#5-end-to-end-scientific-workflow)
6. [Requirements Extracted from PDFs](#6-requirements-extracted-from-pdfs)
7. [Architect Recommendations](#7-architect-recommendations)
8. [Assumptions Awaiting Confirmation](#8-assumptions-awaiting-confirmation)
9. [Unresolved Questions](#9-unresolved-questions)
10. [Source Traceability](#10-source-traceability)

---

## 1. Problem Statement and Motivation

Canal irrigation systems across India's agricultural belts rely on **district-level averages and fixed schedules** to allocate water. This coarse, one-size-fits-all approach leads to systematic over- and under-watering of individual fields, with cascading consequences:

| Problem | Impact |
|---------|--------|
| District averages replace field-level data | Water allocation ignores crop-specific needs |
| Fixed irrigation schedules | Timing mismatches with actual crop growth stages |
| **Farmer yield loss at critical growth stages** | Flowering, grain-filling stages are most water-sensitive |
| Canal managers lack field-level evidence | No data-driven basis for priority scheduling |
| **Optical remote sensing fails under cloud cover** | Monsoon/post-monsoon monitoring gaps break continuity |
| Source-reported concern: static vegetation-index thresholds may misclassify senescence as stress | This is a motivation to evaluate, not a measured AgriSense result |
| No documented field-level water-depth or canal-boundary summary | Source describes deficits using “mm/ha”; interpret depth as mm and any area-derived volume as m³ with explicit assumptions |
| **No unified pipeline** | Classification, phenology, stress, and advisory are studied in isolation |
| No canal-command aggregation | Pixel-level results never reach the decision boundaries canal officers use |

> **Source:** IDP PDF, page 3 — Problem Statement; pages 15–22 — Research Gaps G1–G5.

**In summary:** Existing tools are fragmented, weather-dependent, stage-unaware, and disconnected from the operational units (canal commands) that actually control water distribution. AgriSense is proposed to investigate the five source-identified research gaps (G1–G5); whether the project addresses them remains to be demonstrated.

---

## 2. Objectives and Expected Outcomes

### 2.1 Main Objective

> Source-stated objective (IDP PDF, p. 23): “To design and implement an automated, all-weather, growth-stage-aware satellite framework that converts Sentinel-1 and Sentinel-2 data into field-level crop maps, moisture stress alerts and canal-wise volumetric irrigation advisories.” The “all-weather” and operational-resolution wording is a source aspiration, not a demonstrated capability.

> **Source:** IDP PDF, page 23.

### 2.2 Sub-Objectives

| ID | Sub-Objective | Description |
|----|---------------|-------------|
| **O1** | SAR–Optical Crop Classification | Source asks for Sentinel-1/2 + ERA5-Land ingestion and Random Forest mapping at a 10 m output grid; effective resolution depends on the source bands and processing. |
| **O2** | Stage-Aware Stress Detection | Source asks for a SciPy phenology tracker and dynamic VCI thresholds to address senescence-related false alarms; this proposed effect requires validation. |
| **O3** | Canal-Level Irrigation Advisory | Source asks for FAO-56-based deficits, canal-command aggregation, and Streamlit delivery. The project owner prefers a responsive browser dashboard; implementation framework is pending DEC-01. Treat “mm/ha” as source terminology; the scientific output unit for depth is mm, and volume requires area and explicit assumptions. |

> **Source:** IDP PDF, page 23 — Objectives O1, O2, O3.

### 2.3 Expected Outcomes

- Crop-type map on the source-requested nominal 10 m output grid, with native/effective resolution documented
- **Growth stage map** showing vegetative, flowering/heading, and senescence phases
- **Candidate vegetation/stress indicator map** using a documented method; stage-aware rules and their value over static baselines require independent validation
- Canal-boundary summary of estimated depth (mm); any area-derived volume (m³) must document valid area and assumptions and is not a gate-release prescription
- Outputs presented in an interactive, responsive browser dashboard; the owner prefers this over Streamlit, with framework choice pending DEC-01 approval

### 2.4 Intended Users (source-proposed; operational suitability unvalidated)

| User Group | Primary Interest |
|------------|-----------------|
| Farmers | Potential field-level indicators for review; no validated operational recommendation is established |
| Canal / Irrigation Officers | Potential canal-boundary summaries for review; operational suitability is unvalidated |
| Agricultural Planners | Regional crop distribution, water demand patterns |

### 2.5 Evaluation Metrics

| Metric Category | Specific Metrics |
|-----------------|-----------------|
| Classification evaluation | Overall Accuracy, Cohen's Kappa, per-class F1-score, only when suitable independent reference labels exist |
| Stress detection reliability | False-alarm rate (senescence vs. real stress) |
| Water-balance evaluation | Deficit RMSE against a sourced reference, if a defensible reference and unit definition are available |
| Monitoring robustness | Evaluate observation availability under cloud; SAR complementarity does not guarantee continuous or equivalent stress observations |

> **Source:** IDP PDF, page 3 — Expected Outcome.

---

## 3. Scope and Exclusions

### 3.1 In Scope

The project intends to address source features **F1–F8** and objectives **O1–O3**, subject to Phase 0 decisions, data availability, and scientific validation. Their appearance in a source document does not establish feasibility or demonstrated capability:

- **F1:** API-Driven Data Ingestion Engine (GEE-based S2, S1, ERA5-Land)
- **F2:** 10 m Pixel Crop Classifier (Random Forest on multi-temporal NDVI/EVI stacks)
- **F3:** Continuous Phenology Tracker (time-series inflection points)
- **F4:** Stage-Aware Stress Intelligence (candidate dynamic thresholds; method and effect require validation)
- **F5:** Sentinel-1 radar features. The source's “all-weather” framing is an aspiration; SAR does not provide optical-equivalent observations or guarantee continuous stress detection.
- **F6:** Mava-proposed FAO-56 water-balance estimate (ETc = Kc × ET₀ against rainfall; method and inputs require definition; source uses “mm/ha”)
- **F7:** Canal Command Boundary Aggregator (pixel → canal polygon summaries)
- **F8:** The 3-Click Field Dashboard (source proposal: Streamlit with map, charts, tables; owner preference: responsive web dashboard, framework pending DEC-01)

### 3.2 Exclusions

> [!IMPORTANT]
> The following items are excluded from the current implementation scope. They are scope choices, including where the source proposes a broader capability; they do not imply that every item is absent from the source documents.

| Exclusion | Rationale |
|-----------|-----------|
| Automated canal-gate control or direct operation | The source mentions canal-gate guidance; this project limits its outputs to estimates and review summaries, not operational commands |
| Real-time sensor integration (IoT/field sensors) | All data comes from satellite and reanalysis sources |
| Yield prediction / crop yield modelling | Out of scope; focus is on stress detection and irrigation deficit |
| Economic or cost-benefit analysis | No financial modelling is planned |
| Multi-year historical analysis | Historical data used only as needed for training/validation, not trend analysis |
| Soil sampling or field instrumentation | No in-situ data collection infrastructure is planned |

---

## 4. Intended Users and Supported Decisions

### 4.1 Farmers

| Information Provided | Decision Supported |
|---------------------|--------------------|
| Candidate vegetation/stress indicators with quality and uncertainty limitations | Review alongside field observations and other evidence |
| Current growth stage of their crop | Understanding crop water sensitivity |
| Irrigation-deficit estimate (depth in mm, if adequately supported) | Decision support subject to documented limitations and human judgment |

### 4.2 Canal / Irrigation Officers

| Information Provided | Decision Supported |
|---------------------|--------------------|
| Canal-boundary summaries of estimated depth and any supported area-derived volume | Review and prioritization only; not a gate-release instruction |
| Spatial candidate-indicator summaries across command area | Reviewing spatial patterns with source and quality limitations |
| Aggregated estimates by available boundary | Descriptive comparison only; no scheduling recommendation without delivery and hydraulic evidence |

### 4.3 Agricultural Planners

| Information Provided | Decision Supported |
|---------------------|--------------------|
| Crop distribution map on a declared analysis grid with effective resolution documented | Seasonal crop planning and land-use assessment |
| Descriptive water-balance estimates across available boundaries | Exploratory review only; not sufficient on their own for infrastructure or capacity decisions |
| Growth stage progression across the region | Macro-level agricultural monitoring |

---

## 5. End-to-End Scientific Workflow

The proposed AgriSense pipeline transforms satellite and meteorological inputs into crop estimates, candidate indicators, and water-balance summaries. Prescriptive irrigation advice is not produced unless an approved method and adequate inputs support it:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AgriSense Scientific Pipeline                       │
│                                                                         │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────────┐     │
│  │ 1. GEE Data  │───▶│ 2. Preprocessing │───▶│ 3. Feature        │     │
│  │   Ingestion  │    │                  │    │    Extraction     │     │
│  │              │    │ • Cloud masking   │    │ • NDVI, EVI      │     │
│  │ • Sentinel-2 │    │ • Compositing    │    │ • named indices │     │
│  │ • Sentinel-1 │    │ • SAR calibration│    │ • SAR VH/VV      │     │
│  │ • ERA5-Land  │    │ • Temporal stack  │    │   ratios         │     │
│  └──────────────┘    └──────────────────┘    └───────┬───────────┘     │
│                                                       │                 │
│                                                       ▼                 │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────────┐     │
│  │ 6. FAO-56    │◀───│ 5. Candidate     │◀───│ 4. Random Forest  │     │
│  │ Water Balance│    │ Indicator        │    │ Crop Classif.    │     │
│  │              │    │                  │    │                   │     │
│  │ ETc=Kc×ET0  │    │ • Candidate      │    │ • Multi-temporal  │     │
│  │ Balance terms│   │   stage-aware    │    │   index stacks   │     │
│  │ per approved │   │   indicators     │    │ • Candidate RF    │     │
│  │ method       │   │ • Validation     │    │   model           │     │
│  └──────┬───────┘    └──────────────────┘    └───────────────────┘     │
│         ▼                                                               │
│  ┌──────────────┐             ┌──────────────────┐                     │
│  │ 7. Canal     │────────────▶│ 8. Responsive    │                     │
│  │              │             │    Dashboard     │                     │
│  │ Boundary     │             │    Dashboard     │                     │
│  │ Aggregation  │             │                  │                     │
│  │              │             │ • Interactive map │                     │
│  │ • GeoPandas  │             │ • Time-series    │                     │
│  │ • Zonal stats│             │ • Deficit tables │                     │
│  └──────────────┘             └──────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### Pipeline Stages

| Stage | Input | Process | Output |
|-------|-------|---------|--------|
| **1. GEE Data Ingestion** | Sentinel-2 L2A, Sentinel-1 GRD, ERA5-Land | Google Earth Engine API queries for AOI and date range | Raw image collections |
| **2. Preprocessing** | Raw image collections | Cloud masking (S2 SCL band), temporal compositing (8-day / monthly), SAR calibration (σ⁰ to dB) | Clean, analysis-ready raster stacks |
| **3. Feature Extraction** | Clean raster stacks | Compute NDVI, EVI, a specifically named `NDWI_MCF` and/or `NDWI_GAO`, and VCI only with a defined baseline; document SAR ratio units | Multi-temporal feature cubes |
| **4. Random Forest Crop Classification** | Feature cubes + sourced training labels | Candidate scikit-learn Random Forest; tree count and features to be approved and evaluated | Map on declared analysis grid, with effective resolution and validation limits |
| **5. Phenology + Stage-Aware Stress Detection** | Classified pixels + temporal NDVI/VCI curves | SciPy signal processing for inflection points → growth stage; dynamic VCI thresholds per stage | Growth stage labels + stress flags |
| **6. Water-Balance Estimate** | Crop stage (→ Kc), meteorology, and any approved soil-water inputs | Compute ETc and a clearly defined balance under a documented method; ETc minus rainfall alone is not automatically a net irrigation requirement | Estimated depth in mm with input provenance and limitations |
| **7. Canal Boundary Aggregation** | Pixel-level deficits + canal boundary shapefiles | GeoPandas zonal statistics: mean/sum deficit per canal command polygon | Canal-wise deficit table |
| **8. Responsive Dashboard** | All approved outputs | Browser frontend and Python API (frameworks and map/chart libraries TBD) | Interactive web application; source documents propose Streamlit |

> **Source:** IDP PDF, page 4 — Key Techniques; mava.pdf, pages 4–6 — Features F1–F8.

---

## 6. Requirements Extracted from PDFs

> The tables below distinguish source-stated requirements from architect recommendations. Statements such as “all-weather,” “10 m,” “real-time,” and claimed false-alarm reduction are source aspirations or claims; they are not verified scientific performance or engineering guarantees.

### 6.1 From IDP_Review_1_AgriSense (1).pdf

**Objectives & Deliverables (REQUIREMENT):**
- **O1:** SAR–Optical crop classification on the source-requested 10 m grid using Random Forest; source resolutions and effective detail must be documented
- **O2:** Source asks for a SciPy phenology tracker with dynamic VCI thresholds; these remain candidate rules until defined and validated.
- **O3:** Canal-Level Irrigation Advisory using FAO-56 deficits aggregated to canal boundaries; the source proposes Streamlit delivery, while the owner prefers a responsive web dashboard (DEC-01 pending)

**Techniques Specified (REQUIREMENT):**
1. SAR-Optical Data Fusion — the source proposes Sentinel-2 indices with Sentinel-1 VH/VV; neither continuous optical coverage nor equivalent stress observations are guaranteed
2. Spectral Vegetation Indices — NDVI, EVI, a specifically named `NDWI_MCF` and/or `NDWI_GAO`, and VCI only when its baseline is defined
3. Random Forest Classification — source requests per-pixel output on a nominal 10 m grid; effective resolution and accuracy require documentation and validation
4. Time-Series Phenology Extraction — Smoothing, inflection points for vegetative/flowering/senescence
5. FAO-56 Water Balance — source requests an ETc/rainfall-based deficit; the project must define the balance and report depth in mm without claiming a complete irrigation requirement unless inputs support it
6. Cloud Geoprocessing & Vector Aggregation — GEE for rasters, GeoPandas for canal polygon summaries

**Evaluation Metrics (REQUIREMENT):**
- Overall Accuracy, Cohen's Kappa, per-class F1-score
- False-alarm rate (senescence misclassified as stress)
- Deficit RMSE in a defined depth unit (mm), if a defensible independent reference exists
- Monitoring continuity under cloud cover

**Research Gaps Addressed (REQUIREMENT):**
- **G1:** Optical dependence — workflows fail under cloud; SAR-optical fusion only for classification
- **G2:** Static, stage-independent thresholds — VCI/NDVI/NDWI stress rules use fixed thresholds
- **G3:** Disconnected pipeline — classification, phenology, stress, water balance studied separately
- **G4:** Source identifies a gap in translating remote-sensing outputs to documented field-level deficit estimates; its “mm/ha” wording requires unit clarification
- **G5:** No canal-command integration — results not aggregated to canal boundaries

**Literature Review (REQUIREMENT):**
- 50 references reviewed across 3 themes:
  - **T1:** Hydrological Deficit & Stress Modelling (22 papers)
  - **T2:** ML Crop Mapping & Phenology (14 papers)
  - **T3:** SAR-Optical Sensing & Platforms (14 papers)

> **Source:** IDP PDF — pages 3 (problem), 4 (techniques), 5–14 (literature review), 15–22 (research gaps), 23 (objectives).

### 6.2 From mava.pdf

**Features (REQUIREMENT):**

| Feature | Name | Description |
|---------|------|-------------|
| **F1** | API-Driven Data Ingestion Engine | GEE-based automated aggregation of Sentinel-2, Sentinel-1, ERA5-Land |
| **F2** | 10 m-grid Pixel Crop Classifier | Random Forest on seasonal multi-temporal NDVI/EVI stacks; grid spacing does not imply uniform 10 m effective resolution |
| **F3** | Continuous Phenology Tracker | Time-series inflection points for Vegetative, Flowering/Heading, Senescence |
| **F4** | Stage-Aware Stress Intelligence | Dynamic thresholds based on crop maturity |
| **F5** | All-Weather Radar Fusion | Sentinel-1 SAR VH/VV backscatter when optical fails |
| **F6** | FAO-56 Water Balance Estimator | Mava proposes ETc = Kc × ET₀ against rainfall; rainfall timing/source and the balance method remain to be defined |
| **F7** | Canal Command Boundary Aggregator | Pixel deficits aggregated to canal command boundaries |
| **F8** | The 3-Click Field Dashboard | Source proposal: Streamlit with interactive map, time-series charts, data tables; project-owner preference: responsive browser UI, framework TBD |

**Technology Stack (REQUIREMENT):**

| Layer | Technologies |
|-------|-------------|
| Cloud Data & Infrastructure | Source-proposed Google Earth Engine, Sentinel-2, Sentinel-1, and ERA5-Land; nominal grid spacing and effective resolution are distinct |
| ML & Processing | Scikit-Learn (Random Forest candidate; Mava's 100-tree setting is a proposal to evaluate), NumPy & Pandas, SciPy (signal processing) |
| Geospatial & Frontend | Source proposal: GeoPandas/Rasterio, Streamlit, Streamlit-Folium, Plotly. Owner prefers a responsive browser frontend with Python API; framework and libraries pending DEC-01. |

**USP Statement (source claim, not independently verified):**
> Mava presents this combination as its unique selling proposition. This is an unverified source claim and is not repeated as a comparative finding.

> **Source:** mava.pdf — pages 4–6 (features), page 9 (technology stack).

---

## 7. Architect Recommendations

> [!NOTE]
> The following are **RECOMMENDATIONS** from the architect based on analysis of both PDFs and the project context. They are not requirements from the PDFs but are advised for successful implementation.

### RECOMMENDATION 1: Prefer a Responsive Browser Dashboard

**Rationale:** The project owner prefers a highly responsive, professional dashboard and does not prefer Streamlit. A separate browser frontend with a Python API is the current owner-preferred direction; React + TypeScript and FastAPI are candidates only. The source PDFs propose Streamlit, and the three-member team's frontend/API capacity is not yet confirmed. DEC-01 requires team and guide review before implementation; preserve a tight scope and avoid adding an unrequested spatial server or database.

### RECOMMENDATION 2: Use GEE for Server-Side Processing to Minimize Local Compute

**Rationale:** Google Earth Engine performs raster processing (compositing, cloud masking, index computation, SAR calibration) on Google's infrastructure. This avoids downloading terabytes of raw Sentinel imagery to local machines. The team should design the pipeline to push as much computation as possible to GEE and only export derived products (feature cubes, classified maps) for local ML training and dashboard serving.

### RECOMMENDATION 3: Start with a Well-Defined Study Area Before Scaling

**Rationale:** Neither PDF specifies a study area. Before writing any code, the team should select a single canal command area (e.g., a minor canal in a known irrigation project) with:
- Known cropping patterns (for ground truth validation)
- Available canal boundary shapefiles
- Reasonable size (a few hundred km²) for initial development and testing

This allows rapid iteration on all pipeline stages before scaling to larger regions.

### RECOMMENDATION 4: Prioritize Ground-Truth Acquisition Early

**Rationale:** Random Forest classification (F2/O1) requires labeled training data. No ground truth dataset, collection method, or existing labeled dataset is mentioned in either PDF. This is the single largest risk to the project timeline. The team should:
- Identify if any existing crop-type ground truth exists for their chosen study area
- Plan field visits or use high-resolution imagery for manual labeling if needed
- Budget sufficient time for this before the classification milestone

---

## 8. Assumptions Awaiting Confirmation

> [!WARNING]
> The following items are **ASSUMPTIONS** that could not be resolved from the two source PDFs alone. Each must be confirmed or clarified by the team and/or project guide before implementation begins.

| # | Assumption | Status | Impact if Unresolved |
|---|-----------|--------|---------------------|
| A1 | **Study area not specified** — No geographic region, state, district, or canal system is named in either PDF | ❓ Unresolved | Cannot begin data ingestion, ground truth, or canal boundary work |
| A2 | **Specific crop types TBD** — Mava's diagram illustrates Wheat, Mustard, and Fallow as proposal examples, not an approved class map | ❓ Unresolved | Affects classifier training, Kc values, crop calendar definitions |
| A3 | **Ground truth collection method undefined** — No labeled dataset, field survey plan, or reference data source specified | ❓ Unresolved | Random Forest (F2) cannot be trained without labels |
| A4 | **Canal boundary shapefile source undefined** — F7/O3 require canal command polygons but no source is identified | ❓ Unresolved | Cannot implement canal aggregation (F7) |
| A5 | **Crop calendar and Kc values source undefined** — FAO-56 (F6) requires stage-specific crop coefficients | ❓ Unresolved | Cannot compute ETc without Kc per growth stage |
| A6 | **Soil parameters not mentioned** — Water balance may need soil water-holding capacity, field capacity, etc. | ❓ Unresolved | Simplified FAO-56 may suffice; needs clarification |
| A7 | **Project team size** — Owner confirms that the project has exactly three members; the additional person listed in the Mava submission is not a project member | Resolved by project owner | Use exactly three roles; assign names based on confirmed skills and availability |
| A8 | **8-day monitoring cycle justification unknown** — mava.pdf F5 mentions 8-day cycle but does not justify this interval | ❓ Unresolved | May be tied to Sentinel-2 revisit time (5 days) or compositing strategy |
| A9 | **ERA5-Land native grid vs. 10 m output grid** — The dataset is approximately 0.1° (Earth Engine's nominal pixel size is about 11.1 km); alignment method not selected | ❓ Unresolved | Preserve source-cell identity and do not imply sub-grid meteorological detail |

---

## 9. Unresolved Questions

> [!IMPORTANT]
> The following questions must be resolved by the team and project guide **before implementation begins**. They are ordered roughly by priority (blocking items first).

### Blocking — Cannot Proceed Without Answers

1. **What is the study area?** Which state, district, and canal irrigation project will be used? Is a specific minor canal command identified?

2. **What crops will be classified?** Is it limited to Wheat and Mustard, or are additional crops (rice, sugarcane, etc.) in scope?

3. **How will ground truth be collected?** Will the team conduct field surveys, use existing labeled datasets (e.g., from agricultural departments), or rely on visual interpretation of high-resolution imagery?

4. **Where will canal boundary shapefiles come from?** Are they available from the Irrigation Department, India-WRIS, or another source?

5. **What are the Kc values and crop calendar dates?** Will they come from FAO Irrigation and Drainage Paper No. 56, local agricultural extension services, or literature?

### Important — Should Be Answered Before Detailed Design

6. **What is the temporal scope?** Which Rabi/Kharif season(s) and year(s) will be targeted?

7. **How will coarse ERA5-Land inputs be aligned with outputs?** Preserve native-grid provenance and avoid implying sub-grid meteorological detail.

8. **Is the “30-hour prototype” from mava.pdf (hackathon context) relevant to the IDP timeline?** Confirm scope and schedule with the team.

9. **What validation strategy will be used?** K-fold cross-validation, spatial hold-out, independent test set?

10. **Will the dashboard be deployed or remain local?** If deployed, what hosting is available (university server, cloud)?

### Clarification — Helpful for Architecture Decisions

11. **What justifies the 8-day reporting interval?** Do not treat it as sensor-revisit guarantee or forecast horizon without evidence.

12. **What water-balance method and inputs are feasible?** Clarify effective rainfall, soil-water terms, and intended meaning of “deficit.”

13. **How many crop classes should the classifier support?** Select only after study-area and label-source decisions.

14. **What evaluation design is feasible?** Do not set a performance target without a user need and independent evidence.

---

## 10. Source Traceability

> [!NOTE]
> Page references are from text extraction of the PDFs and may not exactly match printed page numbers. Extracted text pages may differ from the physical document layout.

| Section | Primary Source | Page Reference |
|---------|---------------|----------------|
| Problem Statement | IDP_Review_1_AgriSense (1).pdf | Page 3 |
| Main Objective & Sub-Objectives (O1–O3) | IDP_Review_1_AgriSense (1).pdf | Page 23 |
| Key Techniques | IDP_Review_1_AgriSense (1).pdf | Page 4 |
| Literature Review (50 references) | IDP_Review_1_AgriSense (1).pdf | Pages 5–14 |
| Research Gaps (G1–G5) | IDP_Review_1_AgriSense (1).pdf | Pages 15–22 |
| Expected Outcomes & Evaluation Metrics | IDP_Review_1_AgriSense (1).pdf | Page 3 |
| Features F1–F8 | mava.pdf | Pages 4–6 |
| Technology Stack | mava.pdf | Page 9 |
| USP Statement | mava.pdf | Pages 4–6 |
| Team Members | Both PDFs | IDP PDF page 1; mava.pdf page 1 |

### Cross-Reference: Requirements → Features → Gaps

| Requirement (IDP) | Feature (mava.pdf) | Gap Addressed |
|-------------------|--------------------|----|
| O1: SAR–Optical Crop Classification | F1 (Ingestion) + F2 (Classifier) + F5 (SAR Fusion) | G1 (Optical dependence) |
| O2: Stage-Aware Stress Detection | F3 (Phenology) + F4 (Stage-Aware Stress) | G2 (Static thresholds), G3 (Disconnected pipeline) |
| O3: Canal-Level Irrigation Advisory | F6 + F7 + F8 | G4 (field-level deficit estimate), G5 (canal-boundary aggregation) |

---

> **Next Steps:** Resolve the blocking assumptions and questions, obtain unanimous approval for shared contracts, then record the Phase 0 gate before implementation.
