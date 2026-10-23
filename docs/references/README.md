# AgriSense — Reference Documents

> This directory documents the reference sources used to derive the AgriSense
> project requirements. It does **not** contain or replace the original PDFs.

---

## 1. Project Reference PDFs

| # | Filename | Description | Pages |
|---|----------|-------------|-------|
| 1 | **IDP_Review_1_AgriSense (1).pdf** | BACSE291 Innovative Design Project, First Review, Fall Semester 2026 | 29 |
| 2 | **mava.pdf** | Team Mava hackathon submission | 10 |

### 1.1 IDP Review PDF

Contains: project title, team details, problem statement, literature review
(50 references across three themes), research gaps (G1–G5), objectives
(O1–O3), and a full reference list (pages 24–29).

### 1.2 Mava Hackathon PDF

The project owner confirms that AgriSense has exactly **three** human team members. The IDP-listed team is authoritative for this project; the additional name in the Mava team list is not a fourth project member.

Contains: team details, opportunity statement, features list (F1–F8), process
flow diagram, architecture diagram, and technology stack. The diagrams on
pages 7–8 were visually inspected. They propose an 8-day revisit trigger,
Wheat/Mustard/Fallow classes, an ETc-minus-precipitation "net irrigation gap"
in mm/ha, and direct canal-gate release metrics. These are source proposals,
not validated methods or project decisions; the interval, classes, water
balance, and operational release claims remain unresolved or out of scope.

### PDF Storage Location

These PDFs are stored externally (in the project owner's local workspace at
the repository root during development). They are **not** tracked by Git and
must **not** be committed to the repository. They serve as the primary source
of project requirements.

---

## 2. Key Requirements Extracted

### From IDP PDF

| Item | Summary |
|------|---------|
| **Problem Statement** (p. 3) | Canal irrigation inefficiency, lack of field-level evidence, optical cloud failure, static thresholds, no mm/ha output |
| **Main Objective** (p. 23) | Automated all-weather growth-stage-aware satellite framework |
| **O1** — SAR-Optical Crop Classification | Source requests a 10 m output grid with Sentinel-1/2, ERA5-Land, and Random Forest; effective resolution is not established by the output grid |
| **O2** — Stage-Aware Stress Detection | Develop a SciPy phenology tracker and dynamic VCI thresholds per growth stage that suppress false alarms during senescence |
| **O3** — Canal-Level Irrigation Advisory | Source requests FAO-56 deficits (“mm/ha” in source), canal-command aggregation, and Streamlit delivery; the unit and operational interpretation require clarification |
| **Research Gap G1** | Optical dependence — workflows fail under cloud; SAR-optical fusion only for classification |
| **Research Gap G2** | Static, stage-independent thresholds — VCI/NDVI/NDWI stress rules use fixed thresholds |
| **Research Gap G3** | Disconnected pipeline — classification, phenology, stress, water balance studied separately |
| **Research Gap G4** | Source identifies a gap in translating indices to field-level deficits; its “mm/ha” terminology is not a valid depth unit |
| **Research Gap G5** | No canal-command integration — results not aggregated to canal boundaries |
| **Key Techniques** (p. 4) | SAR-Optical fusion, spectral indices, Random Forest, phenology extraction, FAO-56, GEE + GeoPandas |
| **Evaluation Metrics** (p. 3) | Accuracy, Kappa, F1; false-alarm rate; deficit RMSE; monitoring continuity under cloud |
| **Literature** | 50 references across 3 themes — T1: Hydrological Deficit (22), T2: ML Crop Mapping (14), T3: SAR-Optical Sensing (14) |

### From Mava PDF

| Feature | Summary |
|---------|---------|
| **F1** — Data Ingestion | GEE-based automated aggregation of Sentinel-2, Sentinel-1, ERA5-Land |
| **F2** — Crop Classifier | Random Forest on seasonal multi-temporal NDVI/EVI stacks on the proposed 10 m grid |
| **F3** — Phenology Tracker | Time-series inflection points for Vegetative, Flowering/Heading, Senescence |
| **F4** — Stage-Aware Stress | Dynamic thresholds based on crop maturity |
| **F5** — Radar Fusion | Mava proposes Sentinel-1 VH/VV when optical observations are unavailable; this does not guarantee continuous or equivalent observations |
| **F6** — FAO-56 Water Balance | Mava proposes ETc = Kc × ET0 against “real-time rainfall”; data timing, method, and depth units need definition |
| **F7** — Canal Aggregator | Pixel deficits aggregated to canal command boundaries |
| **F8** — Streamlit Dashboard | Interactive map, time-series charts, data tables |
| **Technology Stack** (p. 9) | Source proposal: GEE, Sentinel-1/2, ERA5-Land, 100-tree Random Forest, NumPy/Pandas, SciPy, GeoPandas/Rasterio, Streamlit, Streamlit-Folium, Plotly; proposal is not a validated design |

> **Implementation preference note:** The project owner prefers a professional responsive browser dashboard over Streamlit. This preference is recorded in proposed decision `DEC-01`; it does not alter the source inventory above and requires team and guide review before implementation.
| **USP** | Mava claims uniqueness, 10 m field-level monitoring, canal-gate guidance, and an 8-day cycle; these are unverified source claims, not verified performance or operational capability |

---

## 3. Technical References Cited in the IDP

The following works are cited in the IDP PDF. Their inclusion here records
source traceability; their full methods and applicability were not independently
reviewed as part of this documentation audit. IDP reference numbers are shown
in square brackets.

| Ref | Citation | Relevance |
|-----|----------|-----------|
| [47] | Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). *FAO Irrigation and Drainage Paper 56* | Standard method for ET₀ and crop coefficients (Kc) |
| [36] | Drusch, M., et al. (2012). Sentinel-2 MSI mission description | 10 m multispectral optical imagery source |
| [37] | Torres, R., et al. (2012). Sentinel-1 C-SAR mission description | Mission background for radar observations; does not validate crop-stress continuity |
| [4]  | Muñoz-Sabater, J., et al. (2021). ERA5-Land description | Daily rainfall and evapotranspiration climate reanalysis |
| [24] | Gorelick, N., et al. (2017). Google Earth Engine platform | Cloud geoprocessing platform |
| [46] | Breiman, L. (2001). Random Forests | Ensemble classifier for crop mapping |
| [49] | Kogan, F. N. (1995). VCI for drought detection | Vegetation Condition Index baseline |
| [43] | Jönsson, P., & Eklundh, L. (2004). TIMESAT phenology extraction | Time-series smoothing and phenology inflection points |
| [48] | Gao, B. (1996). NDWI | Normalised Difference Water Index for moisture stress |

> [!NOTE]
> All 50 literature references from the IDP PDF are listed in the PDF itself
> (pages 24–29) and are **not** reproduced here to avoid duplication. Refer to
> the original PDF for the complete bibliography.

---

## 4. Source-Verification Gaps

The following items could not be fully verified during requirements extraction:

- **Mava diagrams** (pp. 7–8) were visually reviewed, but their technical
  claims are not independently validated. In particular, the flow uses a
  fixed 8-day trigger and equates ETc minus precipitation with a net irrigation
  gap; the architecture labels SAR as cloud-proof and shows direct canal-gate
  release metrics. These claims are not adopted as guaranteed capabilities.
- **Study area, formal crop classes, and ground-truth data sources** are not specified
  in either PDF and must be confirmed by the project team.
- **8-day monitoring cycle** (mentioned in mava.pdf) is not explained or
  justified in either document and must not be described as a forecast without a forecast source.
- **30-hour prototype timeline** (mava.pdf) refers to a hackathon context and
  is not applicable to the IDP project timeline.

---

## 5. Citation Policy

> [!IMPORTANT]
> - Do **not** fabricate source titles, page numbers, quotations, or
>   citations.
> - Page references are from text extraction and may not exactly match printed
>   page numbers.
> - Reference the IDP PDF's own reference numbering (`[1]`–`[50]`) when citing
>   literature.
> - All 50 literature references from the IDP PDF are listed in the PDF itself
>   (pages 24–29) and are not reproduced in project documentation to avoid
>   duplication.

---

## 6. Note on PDF Storage

> [!CAUTION]
> The reference PDFs are maintained externally and **must not** be committed to
> the Git repository. This directory documents references; it does not contain
> or replace the PDFs. See the project [`.gitignore`](../../.gitignore) for
> exclusion rules.
