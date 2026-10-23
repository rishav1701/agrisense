# AgriSense Project Status & Progress Checkpoint

> **Last Updated:** 2026-10-23  
> **Current Phase:** **Phase P0 — Requirements, Architecture, Risks, and Planning**  
> **Phase P0 Status:** **DRAFTED — NOT APPROVED; remediation and human review remain**  
> **Implementation Status:** **NOT STARTED** (In strict compliance with Phase 0 scope, zero application or algorithmic code has been implemented).

---

## 1. Executive Summary

Phase 0 documentation has been drafted from the two project references and includes known assumptions and gaps. Audit remediation has corrected source overclaims, units, resolution, ownership, unsupported scientific examples, and advisory semantics across the project documentation. All three team members approved the API contract amendment on 2026-10-23. The full document set remains provisional pending guide review and formal Phase 0 sign-off, and is not yet an implementation baseline.

The project team has exactly three members, as confirmed by the project owner. The IDP PDF lists three students; the Mava PDF lists an additional person, which is not part of this project team. Role-to-name mapping, architecture decisions, and the Phase 0 gate still require the approvals recorded below. The shared API contract amendment has unanimous member approval; final guide and Phase 0 approval remain pending.

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
| **API & Data Contracts** | [`docs/API_CONTRACTS.md`](API_CONTRACTS.md) | **Amended; member approval recorded; guide review pending** | `CON-01` to `CON-09` revised to remove fabricated examples and unsupported thresholds, clarify units and provenance, and bound water-balance/canal outputs. |
| **Team Workflow** | [`docs/TEAM_WORKFLOW.md`](TEAM_WORKFLOW.md) | **Drafted; audit remediation applied; provisional** | Branching, conventional commits, unanimous contract review protocol, and session recovery steps. |
| **Architectural Decisions** | [`docs/DECISIONS.md`](DECISIONS.md) | **Drafted; audit remediation applied; provisional** | 9 decision records (`DEC-01` to `DEC-09`) covering architecture, modeling, and caching; all remain `PROPOSED`. |
| **Reference Documentation** | [`docs/references/README.md`](references/README.md) | **Drafted; audit remediation applied; provisional** | Source traceability, visually reviewed Mava diagrams, and unresolved technical claims. |
| **Scientific Risk Register** | [`docs/risks/SCIENTIFIC_RISKS.md`](risks/SCIENTIFIC_RISKS.md) | **Drafted; audit remediation applied; provisional** | Scientific and operational risks with mitigation strategies. |
| **Repository Configuration** | [`.gitignore`](../.gitignore), [`.env.example`](../.env.example) | **Complete** | Configured to exclude PDFs, large rasters, cache files, and private credentials. |

---

## 3. Decisions Log Summary

| Decision ID | Summary | Proposed Recommendation | Status |
|:---|:---|:---|:---|
| **`DEC-01`** | Web Application Architecture | Responsive browser frontend + Python API candidate; framework TBD | `PROPOSED` |
| **`DEC-02`** | Satellite Geoprocessing Engine | Google Earth Engine Python API (Server-Side) | `PROPOSED` |
| **`DEC-03`** | Crop Classification Algorithm | Random Forest candidate; classes/features/tree count to be evaluated | `PROPOSED` |
| **`DEC-04`** | Phenology Curve Tracking | Candidate SciPy smoothing and transition method; parameters unselected | `PROPOSED` |
| **`DEC-05`** | Moisture-Stress Detection | Dynamic Growth-Stage-Aware VCI Thresholding | `PROPOSED` |
| **`DEC-06`** | Agro-Meteorological Forcing | ECMWF ERA5-Land Daily Reanalysis via GEE | `PROPOSED` |
| **`DEC-07`** | Canal Aggregation Method | Vector Zonal Overlay via GeoPandas & Rasterio | `PROPOSED` |
| **`DEC-08`** | Intermediate Data Caching | Local Filesystem Cache (`data/cache/` ignored) | `PROPOSED` |
| **`DEC-09`** | Software Testing Fixtures | Pure Synthetic Mock Arrays (Strictly Labeled) | `PROPOSED` |

*No decision has been marked `APPROVED` pending human review.*

DEC-01 records the project owner's preference for a responsive browser dashboard with a Python API; React + TypeScript and FastAPI remain candidates. The source documents propose Streamlit. The three-member team and project guide must review the architecture and Member C's capacity before implementation.

---

## 4. Current Blockers & Unresolved Questions

### Critical Blockers (must be resolved before dependent implementation or scientific claims)
1. **`BLOCKER-01`: Specific Study Area Undefined**
   - *Impact:* Neither PDF specifies the geographic boundary or administrative district for the project. Satellite queries, coordinate reference systems, crop calendars, and canal boundary acquisitions cannot proceed without a defined Area of Interest (AOI).
   - *Action Required:* Team must confirm the study area (e.g., specific district in Punjab, Haryana, or Karnataka) and save boundary geometry to `config/study_area.geojson`.
2. **`BLOCKER-02`: Ground-Truth Crop Training Labels Unidentified**
   - *Impact:* Supervised Random Forest classification requires suitable, sourced, georeferenced crop labels (points or polygons). No ground-truth source is identified in the project documents.
   - *Action Required:* Determine source of ground-truth data (e.g., state remote sensing centre datasets, ICAR survey data, or high-resolution visual digitization).
3. **`BLOCKER-03`: Canal Command Boundary Vector Data Availability**
   - *Impact:* Canal-boundary aggregation (`F7`, `O3`) requires boundary data; any area-derived volume also needs documented valid-area and method assumptions.
   - *Action Required:* Acquire and verify official canal-command boundaries. If unavailable, defer canal-command summaries or report summaries for another sourced boundary under its correct name; administrative areas are not canal commands.

### Open Questions Awaiting Confirmation
- **`Q-01` Role Mapping:** The project has exactly three members. The task plan uses Member A/B/C roles; the team must approve the mapping from the three IDP-listed students to those roles. The additional name in the Mava team list is not part of this project team.
- **`Q-02` 8-Day Monitoring Window:** `mava.pdf` mentions an 8-day monitoring cycle without justification. Treat it as a proposed reporting interval only; do not call it a forecast or guaranteed sensor cadence.
- **`Q-03` Target Crop Classes:** Mava's diagram illustrates Wheat, Mustard, and Fallow; these are proposal examples, not an approved class map. Confirm the formal classes and traceable labels for the selected study area.

---

## 5. Conditions Required Before Phase P1 Begins (Gate 0)

To transition from Phase P0 to Phase P1, the following conditions must be met:
1. [ ] Team members review and formally approve `docs/TASK_ASSIGNMENTS.md` and role distribution.
2. [ ] All three members review and approve the proposed architecture decisions (`DEC-01` through `DEC-09`); the guide reviews decisions requiring guide approval.
3. [ ] Team selects the target study area (`BLOCKER-01`) and confirms the target crop classes.
4. [ ] Team records a feasible ground-truth strategy and verifies whether independent labels can be obtained before classifier implementation.
5. [ ] Team records a source and fallback decision for canal boundaries before claiming canal-level outputs.
6. [ ] Each team member verifies their Google Earth Engine access if GEE remains selected.
7. [ ] All three members and the project guide review the corrected Phase 0 deliverables and record Gate 0 approval.

---

## 6. Next Recommended Action

The project lead (Rishav Raj) should convene a team sync with Ashwanth C and Peter Livins to:
1. Review the corrected provisional documents in `docs/` and confirm that the team consists of the three students listed in the IDP review.
2. Assign those three members to **Member A**, **Member B**, and **Member C** roles based on their actual skills and availability.
3. Resolve `BLOCKER-01` and agree the crop classes, ground-truth strategy, and canal-boundary plan.
4. Confirm that the unanimously approved API contract amendment is reflected in the implementation plan; keep implementation gated on Phase 0 approval.
5. Ask Dr. Muthuraja S to review the revised Phase 0 baseline and record Gate 0 approval.
