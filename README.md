# AgriSense

**AI-Driven Automated Crop Type, Moisture Stress Detection and Irrigation Advisory Across Growth Stages Using Moderate Resolution Spectral Signatures (Optical & Microwave Satellite Data)**

> **Phase 0: COMPLETE — approved by the three-member team; guide sign-off waived by the project owner.**
>
> **Phase 1 has not started.** Project-specific data prerequisites and individual architecture/scientific decisions remain open. No implementation has been performed.

## Project Purpose

AgriSense is an academic project (BACSE291 — Innovative Design Project, VIT Vellore, Fall 2026) that aims to build a satellite-based framework using Sentinel-1 and Sentinel-2 observations to estimate:

1. **Crop-type maps on a nominal 10 m analysis grid** via Random Forest classification (effective spatial resolution varies by sensor and processing).
2. **Candidate growth-stage-aware vegetation-stress indicators** using thresholds selected and validated for the chosen study area
3. **Irrigation-deficit estimates** based on FAO-56 water-balance methods; any area-based volume is derived only when its assumptions and inputs are documented.

The project-owner-approved direction is an India-first, multi-region design with a shared pipeline and region-specific configuration. The pilot AOI is not selected. Regional coverage and model transfer performance are not claims until independently evaluated.

## High-Level Scientific Workflow

```
Sentinel-2 (Optical) ─┐
Sentinel-1 (SAR) ─────┼─→ GEE Ingestion → Preprocessing → Feature Extraction
ERA5-Land (Met) ──────┘                                         │
                                                                 ▼
                                                    Random Forest Classifier
                                                                 │
                                                                 ▼
                                                    Phenology / Growth Stage
                                                                 │
                                                                 ▼
                                                 Stage-Aware Stress Detection
                                                                 │
                                                                 ▼
                                                    FAO-56 Water Balance
                                                                 │
                                                                 ▼
                                                Canal Boundary Aggregation
                                                                 │
                                                                 ▼
                                               Responsive Web Dashboard
```

## Recommended Architecture *(Provisional — Pending Approval)*

**Owner-preferred direction:** a responsive browser dashboard with a Python API/backend; React + TypeScript and FastAPI are candidates, pending their named decision approvals. The source documents propose Streamlit. GEE, scikit-learn, and SciPy remain proposed scientific stack elements. See `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` for the comparison and open decision.

## Project Documentation

| Document | Purpose |
|----------|---------|
| [`AGENTS.md`](AGENTS.md) | Instructions for coding agents |
| [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) | Problem, objectives, scope, requirements |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System architecture and module design |
| [`docs/EXECUTION_PLAN.md`](docs/EXECUTION_PLAN.md) | Phased development roadmap (P0–P6) |
| [`docs/TASK_ASSIGNMENTS.md`](docs/TASK_ASSIGNMENTS.md) | Three-member task allocation |
| [`docs/DATA_REQUIREMENTS.md`](docs/DATA_REQUIREMENTS.md) | Dataset inventory and specifications |
| [`docs/API_CONTRACTS.md`](docs/API_CONTRACTS.md) | Inter-module interface contracts |
| [`docs/TEAM_WORKFLOW.md`](docs/TEAM_WORKFLOW.md) | Git, review, and collaboration process |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Architecture decision log |
| [`docs/STATUS.md`](docs/STATUS.md) | Current progress and checkpoints |
| [`docs/risks/SCIENTIFIC_RISKS.md`](docs/risks/SCIENTIFIC_RISKS.md) | Risk register |
| [`docs/references/README.md`](docs/references/README.md) | Reference document inventory |

## Development Prerequisites

- Python 3.10+
- Google Earth Engine account with API access, if GEE is selected at the Phase 0 gate
- Git

> **Setup status:** Not yet configured. See `docs/STATUS.md`.

## Finding Your Tasks

1. Check `docs/STATUS.md` for the current phase.
2. Find your assignments in `docs/TASK_ASSIGNMENTS.md`.
3. Read the relevant contracts in `docs/API_CONTRACTS.md`.
4. Follow the workflow in `docs/TEAM_WORKFLOW.md`.

## Reference Documents

The two project reference PDFs (`IDP_Review_1_AgriSense (1).pdf` and `mava.pdf`) are maintained **outside the repository** and are not expected to be committed. See `docs/references/README.md` for details.

## License

Academic project — VIT Vellore, BACSE291, Fall Semester 2026.
