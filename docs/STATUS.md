# AgriSense Project Status & Progress Checkpoint

> **Last Updated:** 2026-10-29
> **Current Phase:** **Phase P0 complete; P1 foundation work underway — P1/Gate 1 and production entry gates remain open**
> **Phase P0 Status:** **APPROVED BY THE THREE-MEMBER TEAM (per project-owner confirmation, 2026-10-23); GUIDE SIGN-OFF WAIVED BY PROJECT OWNER FOR P0**
> **Implementation Status:** **Contract schemas, synthetic software fixtures, Sentinel-1/2 numerical preprocessing, a local readiness/study-area API, and a responsive dashboard foundation are present. Copernicus STAC metadata discovery is implemented. No source assets were acquired, no pilot AOI was selected, and no scientific models or estimates are available.**

---

## 1. Executive Summary

The project owner approved an India-first multi-region scope direction (`DEC-10`). The initial Punjab/Tamil Nadu evidence-review scope in `DEC-11` has been broadened by `DEC-14`: Telangana/TGRAC is the current lead candidate for evidence review, with the final location still determined by verifiable data suitability. A read-only audit retrieved TGRAC ground-truth points and I&CAD command polygons; SRSP Stage I has the largest observed overlap (147 points), but its boundary provenance/reuse terms and label suitability are unresolved. The 12 points tagged Wanaparthy intersect none of the seven queried commands. No AOI is selected and `DS-09` remains a blocker. See [`docs/DS09_AOI_AUDIT.md`](DS09_AOI_AUDIT.md). The owner selected React + TypeScript and FastAPI (`DEC-01`); the user authorized approval steps on behalf of all members on 2026-10-29, with member-side implementation review still pending. An extensible all-crops catalogue is the product direction, while initial model classes remain limited to verified labels (`DEC-12`). Canal-command summaries are conditional on proper boundaries and inputs (`DEC-13`). P0 is complete and P1 foundation code is underway; evidence-dependent acquisition, modelling, calibration, and validation remain gated.

The Phase 0 documentation baseline is complete and approved by all three team members, as confirmed by the project owner on 2026-10-23. The project owner waived guide sign-off for Phase 0. Audit remediation corrected source overclaims, units, resolution, ownership, unsupported scientific examples, and advisory semantics. This approval closes Phase 0 documentation; it does not approve individual proposed scientific/architecture decisions or satisfy the separate P1 entry prerequisites.

The project has exactly three members. The project owner approved Phase 0 on 2026-10-23 and previously approved this role mapping and sequential handoff plan: Member A — Peter Livins (weather, water-balance support, geospatial); Member B — Rishav Raj (satellite data, ML, scientific modelling); Member C — Ashwanth C (application, dashboard, integration). The project owner reports that all three members approved the Phase 0 baseline; guide sign-off was waived by the owner for this phase. Individual decisions retain their listed approval requirements. The shared API contract amendment has unanimous member approval.

### Phase 0 Approval Record
- **Three-member team:** Approved, per the project owner’s confirmation on 2026-10-23.
- **Project guide:** No approval will be provided; the project owner waived guide sign-off for the Phase 0 documentation baseline.
- **Phase 0 disposition:** **COMPLETE**.
- **P1 entry gate:** **OPEN / NOT SATISFIED** pending the project-specific inputs, decision approvals, and access checks listed below. Implementation remains not started.

---

## 2. Deliverables Inventory (Phase P0)

| Deliverable | File Path | Status | Verification Summary |
|:---|:---|:---|:---|
| **Coding Agent Instructions** | [`AGENTS.md`](../AGENTS.md) | **Drafted; audit remediation applied; provisional** | Mandatory scientific integrity rules, file ownership boundaries, and blocker protocols established. |
| **Repository README** | [`README.md`](../README.md) | **Drafted; audit remediation applied; provisional** | Project scope, provisional architecture, document map, and phase warning displayed. |
| **Project Overview** | [`docs/PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) | **Drafted; audit remediation applied; provisional** | Source-grounded problem statement, objectives (O1–O3), features (F1–F8), literature gaps (G1–G5), and scope boundaries. |
| **System Architecture** | [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) | **Drafted; audit remediation applied; provisional** | Provisional architecture, module boundaries, tradeoffs, and directory structure. |
| **Execution Plan** | [`docs/EXECUTION_PLAN.md`](EXECUTION_PLAN.md) | **Drafted; audit remediation applied; provisional** | Phased roadmap (P0–P6), gate criteria, definitions of done, and owner/reviewer roles. |
| **Task Allocation Plan** | [`docs/TASK_ASSIGNMENTS.md`](TASK_ASSIGNMENTS.md) | **Drafted; audit remediation applied; provisional** | Work breakdown for exactly three members (A, B, C), dependency graph, and file ownership matrix. |
| **Data Requirements** | [`docs/DATA_REQUIREMENTS.md`](DATA_REQUIREMENTS.md) | **Drafted; audit remediation applied; provisional** | Data inventory for Sentinel-1, Sentinel-2, ERA5-Land, ground truth, canal vectors, and access checks. |
| **API & Data Contracts** | [`docs/API_CONTRACTS.md`](API_CONTRACTS.md) | **Amended; unanimous member approval recorded** | `CON-01` to `CON-09` revised to remove fabricated examples and unsupported thresholds, clarify units and provenance, and bound water-balance/canal outputs. |
| **Team Workflow** | [`docs/TEAM_WORKFLOW.md`](TEAM_WORKFLOW.md) | **Drafted; audit remediation applied; provisional** | Branching, conventional commits, unanimous contract review protocol, and session recovery steps. |
| **Architectural Decisions** | [`docs/DECISIONS.md`](DECISIONS.md) | **Updated with owner directions and open team decisions** | `DEC-01`–`DEC-13` cover architecture, scope, crop inventory, pilot evidence and conditional canal outputs. |
| **DS-09 AOI Evidence Audit** | [`docs/DS09_AOI_AUDIT.md`](DS09_AOI_AUDIT.md) | **Candidate evidence recorded; AOI not selected** | Live TGRAC point/polygon intersections and Copernicus product-footprint availability; open provenance, license, label, date, and advisory validation checks. |
| **Reference Documentation** | [`docs/references/README.md`](references/README.md) | **Drafted; audit remediation applied; provisional** | Source traceability, visually reviewed Mava diagrams, and unresolved technical claims. |
| **Scientific Risk Register** | [`docs/risks/SCIENTIFIC_RISKS.md`](risks/SCIENTIFIC_RISKS.md) | **Drafted; audit remediation applied; provisional** | Scientific and operational risks with mitigation strategies. |
| **Repository Configuration** | [`.gitignore`](../.gitignore), [`.env.example`](../.env.example) | **Complete** | Configured to exclude PDFs, large rasters, cache files, and private credentials. |

---

## 3. Decisions Log Summary

| Decision ID | Summary | Proposed Recommendation | Status |
|:---|:---|:---|:---|
| **`DEC-01`** | Web Application Architecture | Responsive React + TypeScript frontend and FastAPI candidate stack | **User-authorized on behalf of all members; implementation review pending** |
| **`DEC-02`** | Satellite Geoprocessing Engine | Google Earth Engine Python API (Server-Side) | **Owner-preferred; Peter/Rishav review open** |
| **`DEC-03`** | Crop Classification Algorithm | Random Forest baseline; classes/features remain data-dependent | **Owner-approved baseline; team review open** |
| **`DEC-04`** | Phenology Curve Tracking | Evaluate documented SciPy time-series methods; parameters unselected | **Owner-preferred candidate** |
| **`DEC-05`** | Moisture-Stress Detection | Evaluate stage-aware indicators; thresholds unapproved | **Owner-preferred direction; method open** |
| **`DEC-06`** | Agro-Meteorological Forcing | ERA5-Land with native-grid/temporal limits preserved | **Owner-preferred; Peter/Rishav review open** |
| **`DEC-07`** | Canal Aggregation Method | Conditional local vector descriptive summary | **Owner-preferred conditional method** |
| **`DEC-08`** | Intermediate Data Caching | Local ignored cache for initial build | **Owner-preferred** |
| **`DEC-09`** | Software Testing Fixtures | Clearly labelled synthetic software fixtures only | **Owner-approved integrity rule** |
| **`DEC-10`** | India-first multi-region scope and regional configuration | Shared pipeline with region-specific profiles; no transferability claims without evaluation | **Approved by project owner; implementation/schema review remains open** |
| **`DEC-11`** | Initial multi-region AOIs | Initial Punjab/Tamil Nadu evidence comparison, broadened by `DEC-14`; exact AOI unset | **Initial candidate review; AOI evidence review open** |
| **`DEC-12`** | Crop catalogue and model class scope | Broad catalogue; initial model limited to verified labels | **Owner direction; evidence review open** |
| **`DEC-13`** | Canal aggregation scope | Conditional descriptive aggregation only with sourced command boundaries | **Owner-approved conditional scope** |
| **`DEC-14`** | Evidence-led first pilot | TGRAC/Telangana is a leading candidate; SRSP Stage I has the strongest queried overlap, not a verified AOI | **Owner-approved audit direction; final AOI open** |

*The 2026-10-29 user message authorizes approval steps on behalf of all members; direct member-side implementation reviews are not recorded. `DEC-11` records the initial candidate-state scope; `DEC-14` expands the evidence review. No specific AOI is selected.*

The source documents propose Streamlit; this repository already contains the owner-selected React + TypeScript and FastAPI direction. On 2026-10-29, the user instructed that their message be treated as universal approval from every member for approval steps. Record that as user-reported delegated authorization; individual member-side review signatures are not independently available in this workspace.

---

## 4. Current Blockers & Unresolved Questions

### Critical Blockers (must be resolved before dependent implementation or scientific claims)
1. **`BLOCKER-01`: Pilot AOI Not Verified (`DS-09`)**
   - *Impact:* No candidate boundary has passed source-lineage, vintage, reuse, spatial suitability, study-period, and irrigation-advisory validation checks. AOI-specific acquisition and scientific processing remain gated.
   - *Action Required:* Continue the `DEC-14` review. Resolve whether evidence supports SRSP Stage I or a different command; address the mismatch between 12 Wanaparthy-tagged points and the inspected commands; select and document one verified command polygon and study period.
2. **`BLOCKER-02`: Ground-Truth Suitability Unverified (`DS-04`)**
   - *Impact:* TGRAC layers provide candidate georeferenced point labels (2,446 across February–April 2023), but survey lineage, date semantics, positional accuracy, class validity, domain inconsistencies, reuse terms, and independent evaluation suitability are unconfirmed.
   - *Action Required:* Obtain source metadata/terms and quality details; define a spatially grouped evaluation design. Do not fit or report accuracy until labels and data-use conditions are accepted.
3. **`BLOCKER-03`: Command-Boundary Authority and Reuse Unverified (`DS-05`)**
   - *Impact:* TGRAC I&CAD layers 9 and 10 each return the same seven command polygons with coordinate-identical geometries, but metadata does not explain the duplicate layers or identify vintage, responsible authority, or reuse terms.
   - *Action Required:* Confirm the authoritative layer/version, topology, area attributes, source lineage, and permission. Keep command aggregation gated until verified.

### Open Questions Awaiting Confirmation
- **`Q-01` Role Mapping:** Member assignments were approved with the Phase 0 baseline, per project-owner confirmation.
- **`Q-02` 8-Day Monitoring Window:** `mava.pdf` mentions an 8-day monitoring cycle without justification. Treat it as a proposed reporting interval only; do not call it a forecast or guaranteed sensor cadence.
- **`Q-03` Target Crop Classes:** Maintain a broad, extensible crop catalogue, but confirm each initial model class against traceable labels for the selected AOIs and seasons. Mava's Wheat/Mustard/Fallow diagram remains an example, not an approved class map.

---

## 5. P1 Startup and Region-Dependent Gates

Phase 0 is complete. P1 foundation tasks may begin when their own dependencies are satisfied. This does not close P1 or authorize AOI-specific scientific work. The following remain prerequisites for the dependent activities shown:
1. [x] All three members approved the Phase 0 baseline (reported by the project owner, 2026-10-23); guide sign-off waived by the owner for P0.
2. [ ] Before AOI-specific acquisition: select one pilot command and study period through `DEC-14`, verify its sourced boundary (`DS-09`), and confirm provider access and reuse terms.
3. [ ] Before supervised training/evaluation: confirm supported crop classes and a feasible ground-truth source/strategy; acquire/verify independent labels (`DS-04`).
4. [ ] Before canal aggregation: record a licensed canal-boundary source (`DS-05`) or explicitly defer canal aggregation.
5. [x] User authorization for the React + TypeScript/FastAPI direction (`DEC-01`) was provided on 2026-10-29. Implementation review remains pending; other source and scientific method choices must still be supported by their inputs and documented evidence.
6. [ ] Verify required GEE account access if the team selects GEE; do not share credentials.
7. [x] Initial references identified for later review: ICAR Telangana Kharif agro-advisories for DS-06 and FAO-56 Table 12 for generic DS-07 Kc values. These do not resolve a pilot-specific Rabi calendar, target-class coverage, local calibration, or method approval; those remain gates before the corresponding scientific implementation. Soil parameters (`DS-08`) are required only for a method that models soil storage; otherwise document the supported balance scope and limitations.

### AOI-independent P1 work and current handoffs

- `T-P1-SH-001` — Ashwanth C: environment/tooling foundation remains assigned.
- `T-P1-SH-002` — `CON-01`–`CON-09` schemas are implemented; Member A reviewed them. Member B review and Member C acceptance remain to be recorded. No regional fields were added.
- `T-P1-SH-003` — browser/API boundary specification is now documented; delegated authorization is recorded. Member-side implementation review remains pending.
- `T-P1-SC-001` — Rishav's synthetic fixture implementation and schema integration pass software validation; Member C review remains pending.
- `T-P1-SC-002` — Rishav's source-feasibility inventory is complete; Member A reviewed it and Member C review remains pending.
- `T-P1-DE-002` — Member A's regional-source inventory is complete as desk research; Member B/C reviews remain pending.
- `T-P1-DE-001` — GEE setup remains assigned to Peter and requires the selected provider plus account/project access; no authentication was attempted.
- AOI-free satellite catalog discovery is implemented as a tested metadata utility; this does not complete Sentinel asset ingestion or AOI-specific work.

---

## 6. Next Recommended Action

Continue P1 foundation and evidence tasks. Keep asset acquisition, AOI-specific processing, model fitting, stress/advisory validation, and canal aggregation gated until the evidence and access items in Section 4 are resolved. A user approval can authorize technical choices; it cannot establish third-party data reuse rights, source lineage, credentials, or scientific validity.

---

## 7. Data-readiness checkpoint — 2026-10-24

- Added a source/licence register, AOI evidence recommendation, GEE access guide, proposed satellite/weather conventions, proposed team interface sketch, and a detailed work status. These documents do not record team approval, final AOI selection, or task/phase completion.
- A fresh authorized read-only retrieval completed for TGRAC crop layers 10–12 and I&CAD candidate command layers 9–10: all records returned without missing or malformed geometries (2,446 crop points; seven polygons in each I&CAD layer). Derived CSVs and source-preserving JSON are in Git-ignored `data/audits/tgrac/`.
- The fresh I&CAD overlap results reproduce the DS-09 leading candidate: SRSP Stage I 84/46/17 points (147 total). Layer 18 metadata confirms 1,131,404 cadastral polygons; the point-filtered join retrieved 10 parcels with 12 point matches, and the layer is not a command boundary.
- Alternative-data access: official ADeX linked dataset URL returned HTTP 404; DataSuds catalogue currently redirects to an IRD maintenance page. No actual file was acquired from these sources. A separate public Zindi challenge mirror was identified in the follow-up audit; see the new evidence below.
- Follow-up source check: FAIR Forward's linked ADeX ID `583e8f01-160e-4f51-bde5-31dc7f2a5887` returned 404. Its linked Zindi raw `train.csv` is now acquired to Git-ignored `data/audits/external/` (SHA-256 `92ab358eda4416a7510d174db4925c3599678905f4883a3dccfacb228157b989`) and fully counted: 7,888 rows, 20 columns, no nulls or duplicate FarmIDs, basic polygon-ring closure/length checks passed, and crop/category/season/district counts are in `docs/data_audit/crop_catalogue_and_labels.md`. Its CRS, polygon topology, label protocol, AOI overlap and pixel/date match remain open. FAIR Forward describes source data as CC BY 4.0; Zindi challenge rules permit challenge-data use/share under CC-BY-SA 4.0. Retain both provenance statements, attribute the challenge copy, and meet share-alike conditions. `Stressed` is not verified moisture stress.
- The data-readiness workbook was updated with the acquired Zindi audit, NWIC project record and remaining prerequisite actions. It has five rendered sheets and its formula-error scan found none; it marks unresolved items open.
- TGRAC's command-area monitoring page gives program-level boundary methods, but not layer-9/10-specific lineage/version. The downloaded NWIC Command_Area_GeoJSON contains 1,448 features, including 63 marked Telangana and a same-named `Sriramsagar Stage-I (Pochampad)` project feature. NWIC lists `area_ha=880,121.94`, versus TGRAC's `Ayacut_ha=433,249`; the figures are unreconciled. The GeoJSON has projected coordinate values but no declared CRS, so no overlay or AOI selection is made. Portal metadata says “Other (Open)” without specific licence text; authority, CRS and reuse remain open.
- DS-06/DS-07 source identification is now complete for planning: ICAR's Telangana Kharif agro-advisory and FAO-56 Table 12 are recorded in the crop-label inventory. The ICAR reference is not a pilot-specific Rabi calendar, and the FAO values are generic rather than locally calibrated; target-class and method review remain open.
- Software audit tests pass (8/8) and script byte-compilation passes. No Earth Engine account/project authentication was attempted.
- P1 status remains unchanged. AOI, reuse, source QA, team-review and independent moisture/advisory validation gates remain open.
- Rishav started the non-implementation research portion of the first satellite task (`T-P2-DE-002`): Sentinel-2 SR Harmonized scaling/resolution, SCL/QA60 coverage caveats and candidate index definitions are documented in `docs/PROCESSING_CONVENTIONS.md`, alongside Sentinel-1 source facts relevant to the next step. No collection was queried and no AOI-specific processing or implementation began. The `T-P1-SH-002` schema handoff and the documented P1/Gate 0/Gate 1, AOI/access/method prerequisites remain unsatisfied, so satellite build tasks remain gated.
- On the project owner's instruction to start Rishav's software build, added `T-P1-SC-001` synthetic raster/time-series fixture generators under `tests/fixtures/`. These are explicitly test-only and provide no real source IDs, AOI, CRS, observations, model outputs, or validation evidence. This 2026-10-24 note is superseded by the 2026-10-25 schema implementation checkpoint below.
- Rishav workstream status at the 2026-10-24 checkpoint: `T-P1-SC-002` source-inventory research was complete as a feasibility deliverable, pending Member A/C review; fixture implementation awaited schema validation. The later checkpoint below records the schema and test integration. `T-P2-DE-002`, `T-P2-DE-003`, `T-P2-DE-005`, `T-P2-SC-002` through `T-P2-SC-004`, and downstream `T-P4`/`T-P5` work remain gated on the AOI, provider access, accepted data handoffs, source suitability, and scientific method approvals described above.

## 8. Schema implementation checkpoint — 2026-10-25

- Implemented Python dataclasses and JSON serialization/deserialization for the already-approved `CON-01`–`CON-09` contracts in `src/contracts/schemas.py`. The contract document was not amended and no regional fields were added.
- Added software validation coverage for all nine contracts and strict checks for dates/times, GeoJSON structure and coordinate ranges, units/metadata, ranges, null-with-reason cases, and provenance requirements.
- Updated the synthetic `CON-03` raster manifest to match the schema and added direct schema validation. Fixture values remain artificial software-test inputs only.
- Full test discovery passes: 26 tests; byte-compilation and `git diff --check` pass. This is software validation, not scientific validation. Member C review of `T-P1-SC-001` and reviewer handoff of `T-P1-SH-002` remain pending.
- P1 entry/exit gates and Gate 1 remain open. No pilot AOI, study period, production data access, accepted source/label handoffs, or scientific method approvals were established here. P2 production acquisition/modelling remains gated.

## 9. Rishav Sentinel-2 software checkpoint — 2026-10-25

- Added `src/data/sentinel2.py` with reusable NDVI/EVI raster calculations using the equations documented in `docs/API_CONTRACTS.md` and `docs/PROCESSING_CONVENTIONS.md`.
- The caller must pass reflectance-scaled B02/B04/B08 arrays and an explicit boolean validity mask. The helper does not infer scale, make cloud/shadow decisions, resample bands, download imagery, or impute invalid pixels; zero-denominator and non-finite inputs remain invalid (`NaN`).
- Added four software-only tests. Full discovery passes 30 tests; byte-compilation and `git diff --check` pass. Test arrays are artificial and are not scientific validation.
- This is a general numerical helper, not completion of `T-P2-DE-002`. AOI-specific ingestion, cloud masking, resampling, acquisition, and satellite feature handoff remain gated by the unresolved study area, period, provider access, and processing choices.

## 10. Member A source-inventory checkpoint — 2026-10-27

- Added `docs/data_audit/region_sources.md` for `T-P1-DE-002`, covering weather, administrative boundaries, soil, crop-calendar/advisory, and irrigation/command sources across the Telangana lead candidate and the initial Punjab/Tamil Nadu evidence-review regions.
- Recorded current official source documentation and access/reuse constraints, including IMD data access, ERA5-Land grid/attribution, Survey of India administrative boundaries, TNGIS sharing terms, Soil Health Card limitations, and unresolved TGRAC/NWIC command-boundary provenance/CRS/licensing.
- Inventory is a desk-research deliverable, not source acquisition, AOI approval, or scientific validation. Review by Members B and C remains pending; region-dependent acquisition and water-balance implementation remain gated.

See [`docs/WORK_STATUS.md`](WORK_STATUS.md), [`docs/AOI_DECISION.md`](AOI_DECISION.md), and [`docs/DATA_SOURCES_AND_LICENCES.md`](DATA_SOURCES_AND_LICENCES.md) for details. The AOI evidence and reuse blockers remain open.

## 11. Member A review checkpoint — 2026-10-28

- Refreshed the `T-P1-DE-002` candidate-region source inventory with official-source details on ERA5-Land daily-band semantics and known accumulated-variable issues, IMD data-supply conditions, SoI boundary product scale, Soil Health Card scope, TGRAC/NWIC command-source limitations, TNGIS terms, and Earth Engine project requirements.
- Member A reviewed `T-P1-SH-002`: no blocking mismatch was found between the implemented schemas and approved `CON-01`–`CON-09` meanings. This is not final handoff acceptance; Member B review and Member C acceptance remain pending. Schema checks do not validate source truth, topology, reuse rights or scientific methods.
- Member A reviewed Rishav's `T-P1-SC-002` crop/label feasibility inventory: no blocking omission for the research deliverable. Candidate labels and products remain unapproved for training or validation; provider terms/lineage, CRS/topology, AOI/time match and independent evaluation suitability remain open. Member C review remains pending.
- GEE remains owner-preferred under `DEC-02`; delegated approval to proceed does not supply a registered project or account. No authentication was attempted. Preserve local-only credentials and defer `T-P1-DE-001` verification until the required project/account access is available.
- `T-P1-DE-002` is complete as a desk-research inventory and Member A review checkpoint only. The task's Member B/C reviews, pilot AOI selection, boundary authority/reuse verification, study period and P1 gates remain open.

## 12. Owner-authorized foundation work — 2026-10-29

- The user authorized approval steps on behalf of all members and requested implementation plus verification. This is recorded as delegated authorization, not as direct member-side acceptance. No shared API contract was changed.
- Completed the previously open `T-P1-SH-001` tooling setup: pinned runtime/development dependencies, added pytest/Black/isort/Ruff configuration, and documented virtual environment setup in the README. The ignored `.venv` was installed successfully using Python 3.12; NumPy is pinned to 2.2.6 to retain Python 3.10 compatibility.
- Tightened the FastAPI study-area request so dates remain strings and a boolean cannot be coerced into `buffer_meters`. Added five API software checks covering readiness semantics, valid structural requests, invalid date order, unclosed rings, and strict numeric handling.
- Hardened browser-side GeoJSON intake: Polygon/MultiPolygon and single-feature FeatureCollection inputs are checked for closed rings, finite longitude/latitude bounds, and coordinate shape before preview. Multiple-feature collections are rejected because the UI does not silently combine unrelated geometries. Date intervals are checked before submission.
- Researched current Copernicus Data Space STAC documentation and implemented `src/data/copernicus_stac.py` as metadata-only Sentinel-2 L2A discovery. It validates CON-01 geometry/date inputs, enforces the exclusive end date locally, follows same-origin pagination only, supports the documented scene cloud-cover query, and does not download imagery or claim clear-pixel coverage. The official catalog currently documents the `/v1/` endpoint and `sentinel-2-l2a` collection. See [`docs/PROCESSING_CONVENTIONS.md`](PROCESSING_CONVENTIONS.md).
- Added five explicitly mocked STAC software tests. Full Python software discovery passes: 46 tests (plus 9 subtests); Ruff, isort, per-file Black checks, frontend `npm run build` (TypeScript and Vite production build), and `git diff --check` all pass. A local HTTP smoke test could not reach loopback sockets under the execution sandbox, so route behavior was verified by direct unit calls rather than a live browser/API session.
- Scope remains foundation/prototype work. No STAC query was made for a study AOI, no imagery was downloaded, and no scientific output or validation evidence was created. `T-P2-DE-002` is not complete; AOI, source QA, reuse, GEE account/access, cloud-mask method, and team review gates remain open.
- Member-side verification: not independently performed by other team members in this session. Automated software checks are reported separately and do not substitute for reviewer acceptance.
