# AgriSense Execution Plan (Phases P0 – P6)

> **P0 Status: COMPLETE — approved by the three-member team per project-owner confirmation (2026-10-23); guide sign-off waived by the project owner for the P0 baseline. P1 entry remains blocked by unresolved inputs and decisions.**

> **Scope direction:** India-first multi-region design approved by the project owner (2026-10-23); no pilot AOI selected. P1 setup tasks may proceed independently where their task inputs are satisfied. AOI-dependent acquisition, scientific training/calibration, and validation remain gated by their named inputs. Individual task completion does not close a phase gate.
> **Academic Context:** BACSE291 — Innovative Design Project, VIT Vellore (Fall Semester 2026).
> **Team Structure:** Member A is Peter Livins (weather, water-balance support, geospatial); Member B is Rishav Raj (satellite data, ML, scientific modelling); Member C is Ashwanth C (application, dashboard, integration). The project owner reports unanimous three-member approval of the P0 baseline and waives guide sign-off for P0; sequential, non-overlapping handoffs are approved.
> **Mandatory Rule:** Do not advance between phases without formal gate approval recorded in `docs/STATUS.md`.

---

## 1. Roadmap Overview

**Progress policy:** Task completion, workstream readiness, and phase completion are distinct. A member may complete assigned P1 tasks independently, but P2 cannot start until all P1 deliverables and Gate 1 are complete. In P2, one member owns each sequential stage and can finish it without monitoring another member’s daily progress; the next owner starts only after a documented, reviewed handoff. A phase is complete only when all phase deliverables and its formal exit gate are satisfied and recorded.

```
┌───────┐     ┌───────┐     ┌───────┐     ┌───────┐     ┌───────┐     ┌───────┐     ┌───────┐
│  P0   │ ──► │  P1   │ ──► │  P2   │ ──► │  P3   │ ──► │  P4   │ ──► │  P5   │ ──► │  P6   │
└───────┘     └───────┘     └───────┘     └───────┘     └───────┘     └───────┘     └───────┘
Planning &    Repo Setup    Independent   Integration   Real-Data     Scientific    Demo, Doc
Architecture  & Contracts   Development   & Contracts   End-to-End    Validation    & Review
```

---

## Phase P0: Requirements, Architecture, Risks, and Planning

### Objectives
1. Extract and reconcile all scientific and software requirements from reference materials (`IDP_Review_1_AgriSense (1).pdf` and `mava.pdf`).
2. Establish system architecture, module boundaries, and inter-module contracts.
3. Formulate a realistic task allocation for exactly three members with one primary owner per task and explicit shared-file governance.
4. Document scientific uncertainties, dataset requirements, and collaboration workflows.

### Deliverables
- `AGENTS.md`: Agent behavior rules and scientific integrity constraints.
- `README.md`: Project summary, phase status, navigation.
- `docs/PROJECT_OVERVIEW.md`: Grounded problem statement, objectives (O1–O3), features (F1–F8), gaps (G1–G5).
- `docs/ARCHITECTURE.md`: Proposed scientific backend and responsive browser dashboard architecture, tradeoffs, and pending DEC-01 review.
- `docs/EXECUTION_PLAN.md`: Complete phased roadmap (P0–P6).
- `docs/TASK_ASSIGNMENTS.md`: Work breakdown structure for Members A, B, and C.
- `docs/DATA_REQUIREMENTS.md`: Dataset inventory (S1, S2, ERA5-Land, ground-truth, canal vectors).
- `docs/API_CONTRACTS.md`: Formal data models and schemas (CON-01 to CON-09).
- `docs/TEAM_WORKFLOW.md`: Git branching, PR review, and dispute protocol.
- `docs/DECISIONS.md`: Initial architectural decision records (ADRs).
- `docs/STATUS.md`: Initial checkpoint and blocker inventory.
- `docs/references/README.md`: Documentation of external PDF sources.
- `docs/risks/SCIENTIFIC_RISKS.md`: Comprehensive risk register (RISK-01 to RISK-17).
- `.gitignore` and `.env.example`.

### Roles & Responsibilities
- **Primary Owner:** All members (co-designed with AI architect).
- **Reviewer:** All three human team members. The project owner waived guide sign-off for the P0 baseline.

### Dependencies
- Access to reference documents and repository setup.

### Acceptance Criteria
- All required Phase 0 documents are present; audit remediation updated their cross-references and recorded unresolved decisions and blockers.
- No application or scientific code has been implemented.
- Neither reference PDF is committed to the Git repository.
- Decisions are labeled `PROPOSED` until approved by team consensus.

### P1 Entry Gate Conditions (Preventing Progression from P0 to P1)
- The Phase 0 baseline is approved by all three members per the project owner’s confirmation; guide sign-off is waived by the project owner for this baseline.
- Role-to-name mapping and the sequential allocation plan are approved as part of the Phase 0 baseline.
- The API contract amendment has unanimous approval from all three members (2026-10-23).
- Study area, crop classes, ground-truth strategy, canal-boundary source, required decision approvals, and GEE access if selected are not yet recorded. P0 may be complete while this P1 entry gate remains open.

---

## Phase P1: Repository Foundation, Shared Contracts, Environments, and Quality Gates

Independent foundation tasks may start when their own inputs are satisfied; pilot AOI and data prerequisites gate AOI-specific acquisition and scientific modelling, not environment setup. Add `T-P1-SH-004` to specify regional profile/provenance handling. Any shared-contract changes still require unanimous approval.

### Objectives
1. Configure local virtual environments, Python dependency definitions (`requirements.txt`), and developer linting/formatting hooks (`black`, `ruff`, `isort`, `pytest`); add frontend tooling after the team confirms the owner-selected DEC-01 stack. This Python setup may begin independently of pilot AOI selection.
2. Implement contract schemas in Python (`src/contracts/schemas.py`) using Pydantic or dataclasses to enforce inter-module interfaces.
3. Establish directory structure and mock data fixtures for unit and interface testing.
4. Set up GEE project credentials and verify cloud connectivity.

### Deliverables
- `requirements.txt` with pinned stable dependencies.
- `pyproject.toml` or configuration files for `black`, `ruff`, and `isort`.
- Provisional directory skeleton for approved backend/scientific modules and tests; frontend/API directories are created after team confirmation of DEC-01.
- Python implementation of data contracts in `src/contracts/schemas.py`.
- Reviewed browser/API boundary specification (`T-P1-SH-003`) after DEC-01 selection.
- Mock fixture generator in `tests/fixtures/` producing synthetic data adhering strictly to `CON-01` through `CON-09`.
- Verified GEE connection script (`scripts/verify_gee.py`).

### Ordered P1 Handoffs
1. Ashwanth C: `T-P1-SH-001` environment/tooling.
2. Ashwanth C: `T-P1-SH-002` schemas, with Peter and Rishav sign-off.
3. Ashwanth C: `T-P1-SH-003` browser/API boundary after team confirmation of DEC-01.
4. Peter: `T-P1-DE-001` GEE setup.
5. Rishav: `T-P1-SC-001` explicitly synthetic software fixtures.
6. Proposed: `T-P1-SH-004` regional profile/provenance specification after team confirms the task and its owner.
7. Peter and Rishav may independently complete `T-P1-DE-002` and `T-P1-SC-002` source inventories in their separate files; these inform but do not finalize AOIs or prove label suitability.

This order is sequential for implementation ownership. A task can be complete while P1 remains open; P2 starts only after the complete P1 deliverables and Gate 1.

### Roles & Responsibilities
- **Lead Owner:** Member C (Application, Environment & Contracts Coordinator).
- **Contributors:** Member A (GEE authentication setup), Member B (Model contract review).
- **Reviewers:** All members must review and sign off on `src/contracts/schemas.py`.

### Dependencies
- Approval of Phase P0 deliverables.

### Testing and Validation Requirements
- CI / test command `pytest tests/` runs and validates mock data against Pydantic contract schemas.
- Linting checks (`ruff check .`, `black --check .`) pass with zero errors.
- Test fixtures verified as purely synthetic (no fabricated scientific data).

### Definition of Done
- Complete repository scaffold exists.
- All three members can successfully clone, install requirements, and execute `pytest` locally.
- GEE authentication verified for members executing data pipelines.

### Gate Conditions (Preventing Progression to P2)
- Any member cannot run the agreed software checks.
- Required P1 task handoffs, including the DEC-01/API boundary, are incomplete or unreviewed.
- Shared contracts have not been unanimously approved.
- DEC-01 and the frontend/API toolchain have not yet received team technical confirmation. Guide sign-off is unavailable per project-owner statement and is not recorded as obtained.
- Study area and target crop classes remain undefined.
- Ground-truth and canal-boundary acquisition strategies remain unassessed. Coding against synthetic fixtures may proceed only for software behavior, not scientific performance.

---

## Phase P2: Sequential Implementation Workstreams

### Objectives
1. Implement isolated modules in sequential, non-overlapping stages with formal handoff packages; do not use another member’s daily progress as a prerequisite.
2. Member B (Rishav) completes Sentinel-1/2 and satellite feature/time-series preparation (`T-P2-DE-002`, `003`, `005`); Member A (Peter) then completes ERA5-Land and cross-source assembly (`T-P2-DE-004`, `006`).
3. Member B (Rishav) implements the scientific models sequentially after the accepted complete `CON-03` data handoff: classifier, phenology, then stress model, respecting sourced-label and method blockers. Synthetic fixtures support software tests only; scientific claims and calibration require sourced evidence.
4. Member A (Peter) completes water-balance and canal-geospatial outputs (`T-P2-SC-005`, `T-P2-AP-001`); Member C (Ashwanth C) begins API/dashboard work only after reviewed output handoffs and DEC-01/API boundary approval.

### Deliverables
- **Stage 1 — Member B (Rishav):** `T-P2-DE-002`, `T-P2-DE-003`, `T-P2-DE-005` — satellite package.
- **Stage 2 — Member A (Peter):** `T-P2-DE-004`, `T-P2-DE-006` — ERA5-Land and complete `CON-03` assembly.
  - Satellite tests in the task-owned `tests/data/` files.
- **Stage 3 — Member B (Rishav):** `T-P2-SC-002`, `003`, `004` — classification, phenology, stress.
- **Stage 4 — Member A (Peter):** `T-P2-SC-005`, `T-P2-AP-001` — approved water-balance method and canal aggregation.
  - Task-owned model tests in `tests/models/`; synthetic inputs are software fixtures only.
- **Stage 5 — Member C (Ashwanth C):** `T-P2-AP-002`, `003` — responsive dashboard and charts/exports, after `T-P1-SH-003` boundary approval.
- API/browser boundary must be documented and approved before API implementation; `T-P3-IN-001` follows all accepted P2 handoffs.

### Roles & Responsibilities
- The primary owner and independent reviewer for every task are listed in `docs/TASK_ASSIGNMENTS.md`; sequential stage handoffs are required before the next owner starts dependent work.

### Dependencies
- Successful completion of Phase P1, approved DEC-01/API boundary, and frozen `src/contracts/schemas.py`.

### Testing and Validation Requirements
- Every non-trivial module needs unit tests for its defined behavior; software coverage is not scientific validation.
- No cross-module imports during P2 except through `src/contracts/schemas.py`. No downstream stage begins before its named inputs are handed off and reviewed.
- Offline software tests should not require live GEE/network access; data acquisition checks are separate smoke tests.

### Definition of Done
- Each task owner’s branch passes its defined acceptance criteria and tests, with the designated reviewer’s handoff recorded. Individual task completion does not complete a phase.
- Each module consumes and produces valid contract objects.

### Gate Conditions (Preventing Progression to P3)
- Every required P2 task and sequential handoff has met its acceptance criteria and is reviewed.
- Unit tests failing on any individual workstream.
- Unapproved alterations made to shared contract files.
- Persistent blocker on ground-truth label acquisition or study area definition.

---

## Phase P3: Integration and Contract Verification

### Objectives
1. Connect module outputs to downstream module inputs on feature integration branches.
2. Verify that accepted data outputs from Member A feed Member B's models.
3. Verify that Member B's scientific outputs feed into Member C's spatial aggregator, Python API, and responsive browser dashboard.
4. Resolve edge cases, coordinate transformations, missing pixel handling, and NaN propagation.

### Deliverables
- Integration test suite in `tests/integration/` validating end-to-end data pipelines on sample AOIs.
- Integrated `src/` modules functioning together on local runtime.
- Working prototype dashboard displaying sample/cached pipeline runs.
- Integration verification report in `docs/STATUS.md`.

### Roles & Responsibilities
- **Lead Owner:** Member C (Application & Integration).
- **Contributors:** Member A and Member B.
- **Reviewers:** Full team joint review.

### Dependencies
- Completion of all P2 workstreams.

### Testing and Validation Requirements
- End-to-end pipeline execution from cached sample input rasters to final canal-aggregated tables and Folium map layers.
- Contract validation on every inter-module data exchange.
- Zero silent failure or uncaught NaN / divide-by-zero errors in scientific calculations.

### Definition of Done
- All individual workstreams merged into `main` via approved PRs.
- `pytest tests/integration/` passes consistently across all three member environments.

### Gate Conditions (Preventing Progression to P4)
- Schema mismatch between module interfaces.
- Memory overflow or timeout when processing multi-temporal sample tiles.

---

## Phase P4: Real-Data End-to-End Processing

### Objectives
1. Execute the integrated pipeline on actual satellite and weather observations for the designated study area.
2. Ingest real Sentinel-1, Sentinel-2, and ERA5-Land observations across an active crop season.
3. Execute Random Forest classification and generate a map on the approved analysis grid, documenting effective sensor resolution and validation limits.
4. Execute temporal phenology extraction, candidate stage-aware indicator analysis, and FAO-56 ETc / water-balance estimates under the approved method.
5. Ingest official or digitized canal boundaries if available and produce zonal summaries of estimated depth; report area-derived volume only with explicit assumptions, never as an unsupported gate-release prescription.

### Deliverables
- Preprocessed real-data composites stored in local cache or GEE assets.
- Real-data crop classification map GeoTIFF with analysis-grid spacing and effective-resolution caveats.
- Multi-temporal phenological inflection rasters and growth stage classifications.
- Candidate vegetation/stress indicator maps with quality states and documented senescence handling.
- Canal-boundary summaries of estimated depth (mm) and, if approved and supported, area-derived volume with assumptions; no gate-release prescription.
- Responsive browser dashboard displaying available observations, estimates, candidate indicators, and their limitations; framework selection remains gated by DEC-01.

### Roles & Responsibilities
- **Satellite & Met Processing:** Member A.
- **Scientific Model Execution:** Member B.
- **Dashboard Data Binding & Display:** Member C.
- **Reviewers:** All members.

### Dependencies
- Confirmed study area boundary (`config/study_area.geojson`).
- Confirmed ground-truth training set for target crops.
- Acquired canal boundary shapefile (`data/canals/`).

### Testing and Validation Requirements
- Verification of spatial alignment (CRS, pixel grid, bounds) across S1, S2, and ERA5-Land.
- Verification that cloud masking correctly flags invalid optical pixels.
- Verification of available Sentinel-1 acquisitions and quality flags across the study interval; report SAR gaps separately from optical cloud gaps.

### Definition of Done
- Complete end-to-end pipeline run executed without crashes on real seasonal data.
- Outputs rendered in the approved browser dashboard with functional map layer toggling and clear data-quality states.

### Gate Conditions (Preventing Progression to P5)
- Complete failure of GEE export quotas or inability to acquire imagery for target season.
- Inability to acquire ground-truth training data (triggering RISK-01 mitigation protocols).

---

## Phase P5: Scientific Validation, Uncertainty Analysis, and Evaluation

### Objectives
1. Rigorously evaluate model outputs against empirical ground data and scientific benchmarks.
2. Compute classification metrics: Overall Accuracy, Cohen's Kappa, Macro-F1, and per-class Confusion Matrices with spatial cross-validation.
3. Compare the stage-aware candidate indicator with a documented static baseline where independent evidence supports evaluation; report whether false alarms decrease, increase, or remain uncertain.
4. Perform sensitivity and uncertainty analysis on FAO-56 irrigation deficit estimates ($ET_c = K_c \times ET_0$).
5. Document all assumptions, biases, and methodological limitations.
6. Where suitable independent labels exist, separately evaluate transfer to unseen regions and across seasons. A single-area spatial holdout is not evidence of cross-region transfer. If evidence is unavailable, report the gap rather than inventing or substituting metrics.

### Deliverables
- `docs/VALIDATION_REPORT.md`: Comprehensive evaluation findings.
- Confusion matrices, error tables, and metric summaries.
- Comparative analysis of static and stage-aware indicators, including false-alarm results only when the evaluation labels and design support them.
- Uncertainty bounds report documenting ERA5-Land downscaling limitations and $K_c$ parameter sensitivity.
- Evaluator scripts in `src/evaluation/metrics.py`.

### Roles & Responsibilities
- **Lead Owner:** Member B (Scientific Models & Validation).
- **Contributors:** Member A (Spatial data integrity), Member C (Visualization of evaluation charts).
- **Reviewers:** Project Guide (Dr. Muthuraja S).

### Dependencies
- Successful completion of Phase P4 real-data execution.
- Independent ground-truth test partition (spatially segregated).

### Testing and Validation Requirements
- Quantitative validation must use held-out test data strictly isolated from training folds (no spatial data leakage).
- Cross-region and cross-season results must use data held out from fitting, feature selection, and tuning; report each evaluation domain separately.
- All scientific claims must cite source data and methodology.
- Software tests must remain strictly separated from scientific validation analyses.

### Definition of Done
- All performance metrics calculated honestly from verified data without fabrication.
- Comprehensive validation report finalized and reviewed by the project guide.

### Gate Conditions (Preventing Progression to P6)
- Scientific claims contradicted by evaluation data.
- Unsubstantiated claims of high accuracy or "measured soil moisture" present in project text.

---

## Phase P6: Deployment, Documentation, Demonstration, and Academic Presentation

### Objectives
1. Finalize the responsive browser dashboard for academic presentation and guide review, using the framework approved in DEC-01.
2. Complete all technical documentation, user guides, and reproducibility instructions.
3. Prepare presentation slide deck and demonstration script highlighting the 3-in-1 pipeline USP.
4. Conduct final code audit, dependency cleanup, and repository archiving.

### Deliverables
- Polished responsive web dashboard with intuitive UI controls, field-level drilldown, and canal summary exports.
- `docs/USER_GUIDE.md`: Step-by-step instructions for operating the dashboard.
- Final academic presentation slide deck (PDF/PPT) covering IDP Review requirements.
- Final project report linking literature gaps (G1–G5) to implemented features (F1–F8).
- Demonstration video or walkthrough script.
- Clean Git history on `main` with all release tags applied.

### Roles & Responsibilities
- **Lead Owner:** Member C (Dashboard, Presentation & Demonstration).
- **Contributors:** Member A (Data engineering documentation), Member B (Scientific methodology documentation).
- **Reviewers:** Project Guide & External Review Panel.

### Dependencies
- Completion of Phase P5 scientific validation.

### Testing and Validation Requirements
- Clean-clone check: A fresh clone can run the dashboard using the documented setup steps; record setup issues without imposing an unsupported time target.
- All dashboard interactive widgets (date sliders, layer selectors, export buttons) function without unhandled exceptions.

### Definition of Done
- System successfully demonstrated to Project Guide (Dr. Muthuraja S).
- Final review deliverables submitted and approved on university portal (VTOP).

---

## Phase Gate Summary Matrix

| Gate | Target Milestone | Approvers | Blocker Criteria |
|:---|:---|:---|:---|
| **Gate 0** | Phase P0 -> P1 | All 3 Members | P0 baseline approval and ownership are recorded; phase remains open until the P1 deliverables are accepted. Independent P1 tasks may begin when their own dependencies are satisfied. |
| **Gate 1** | Phase P1 -> P2 | All 3 Members | Unstable environment, broken tests, unapproved contract schemas |
| **Gate 2** | Phase P2 -> P3 | Member A, B, C | Unit test failures, contract violations, unmerged rogue code |
| **Gate 3** | Phase P3 -> P4 | All 3 Members | Broken pipeline integration, coordinate misalignment, memory exhaustion |
| **Gate 4** | Phase P4 -> P5 | Project Guide & Team | Inability to run on real data, missing study area or ground-truth |
| **Gate 5** | Phase P5 -> P6 | Project Guide & Team | Unsupported claims, missing independent validation, unresolved uncertainty, or unaddressed false alarms |
| **Gate 6** | Final Submission | Guide & Review Panel| Broken demonstration, missing documentation, non-reproducible code |
