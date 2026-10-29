# AgriSense

**AI-Driven Automated Crop Type, Moisture Stress Detection and Irrigation Advisory Across Growth Stages Using Moderate Resolution Spectral Signatures (Optical & Microwave Satellite Data)**

> **Phase 0: COMPLETE — approved by the three-member team; guide sign-off waived by the project owner.**
>
> **P1 foundation work is underway.** Contract schemas, synthetic software fixtures, selected Sentinel-1/2 preprocessing, a local API/dashboard foundation, and metadata-only Sentinel-2 catalogue discovery are implemented. The pilot AOI, source-use approvals, real data connections, and scientific outputs remain unresolved.

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

**User-authorized direction:** a responsive React + TypeScript browser dashboard with a FastAPI Python API. The project owner directed that required member approvals be treated as complete for implementation; individual review records were not collected in this workspace. The source documents propose Streamlit. GEE, scikit-learn, and SciPy remain proposed scientific stack elements. See `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` for current decisions.

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
| [`docs/DS09_AOI_AUDIT.md`](docs/DS09_AOI_AUDIT.md) | TGRAC command-area and ground-truth evidence audit; AOI remains unselected |
| [`docs/STATUS.md`](docs/STATUS.md) | Current progress and checkpoints |
| [`docs/risks/SCIENTIFIC_RISKS.md`](docs/risks/SCIENTIFIC_RISKS.md) | Risk register |
| [`docs/references/README.md`](docs/references/README.md) | Reference document inventory |

## Development Prerequisites

- Python 3.10+
- Node.js with npm for the React dashboard
- Google Earth Engine account with API access, if GEE is selected at the Phase 0 gate
- Git

> **Setup:** Use the pinned root dependency set in `requirements.txt`. See `docs/STATUS.md` for toolchain and data-readiness checkpoints.

Create a local environment and install the application and development tools:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check src tests
.\.venv\Scripts\python -m black --check src tests
.\.venv\Scripts\python -m isort --check-only src tests
```

On Linux/macOS, use `python3 -m venv .venv` and `.venv/bin/python` in place of the Windows commands.

## Run the Local Foundation Demo

The current demo shows the responsive research workspace, API/data readiness, local GeoJSON preview, and structural study-request validation. It does **not** load satellite/weather observations or generate crop, stress, growth-stage, or irrigation estimates. Bring a boundary file you are authorized to use; the repository does not bundle a synthetic or unverified AOI.

From the repository root, install the frontend dependencies and build the browser app:

```powershell
cd frontend
npm ci
npm run build
cd ..
```

Start the local API, which serves the built frontend when `frontend/dist` exists:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). To demonstrate the supported flow, upload an authorized GeoJSON `Polygon` or `MultiPolygon` in longitude/latitude order, choose an inclusive start and exclusive end date, and select **Validate study request**. The response confirms request structure only; it does not select an AOI, query a provider, or acquire data. The interactive API schema is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

For frontend hot reload during development, run `npm run dev` from `frontend` and start the API in a second terminal with the command above. Vite proxies `/api` requests to the local API.

## Finding Your Tasks

1. Check `docs/STATUS.md` for the current phase.
2. Find your assignments in `docs/TASK_ASSIGNMENTS.md`.
3. Read the relevant contracts in `docs/API_CONTRACTS.md`.
4. Follow the workflow in `docs/TEAM_WORKFLOW.md`.

## Reference Documents

The two project reference PDFs (`IDP_Review_1_AgriSense (1).pdf` and `mava.pdf`) are maintained **outside the repository** and are not expected to be committed. See `docs/references/README.md` for details.

## License

Academic project — VIT Vellore, BACSE291, Fall Semester 2026.
