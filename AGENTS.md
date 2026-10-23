# AGENTS.md — AgriSense Repository Instructions for Coding Agents

## Project Purpose

AgriSense is an academic project for automated crop-type classification, growth-stage-aware moisture-stress detection, and irrigation advisory using Sentinel-1/2 satellite data, ERA5-Land meteorological data, and FAO-56 water-balance methodology. See `docs/PROJECT_OVERVIEW.md` for full context.

## Before You Start

1. Read `docs/STATUS.md` for current phase and blockers.
2. Read your assigned task in `docs/TASK_ASSIGNMENTS.md`.
3. Read relevant contracts in `docs/API_CONTRACTS.md`.
4. Read relevant decisions in `docs/DECISIONS.md`.
5. Do **not** read unrelated files or modules unless a dependency requires it.

## Scientific Integrity — Mandatory

- **Never fabricate** satellite observations, meteorological records, crop labels, field measurements, model results, or validation metrics.
- **Never hardcode** scientific outputs and present them as model predictions.
- **Never invent** ground-truth data, accuracy numbers, or performance targets.
- Synthetic data is permitted **only** in explicitly labelled software tests — never as evidence of scientific performance.
- Distinguish software tests from scientific validation.
- All scientific claims require traceability to source data and methodology.
- Label all model outputs as estimates with documented assumptions and limitations.
- Do not describe simplified water-balance estimates as direct soil-moisture measurements.
- Do not claim that resampling ERA5-Land's approximately 0.1° native grid to 10 m creates genuine fine-resolution meteorological data.

## Coding Standards

- Python 3.10+; type hints on all public functions.
- Docstrings (Google style) on all public modules, classes, and functions.
- Format with `black`; lint with `ruff`; sort imports with `isort`.
- Unit tests for all non-trivial functions; use `pytest`.
- No credentials, API keys, or secrets in code or commits.
- Follow the file-ownership boundaries in `docs/TASK_ASSIGNMENTS.md`.

## Git Rules

- Work on feature branches: `feat/<task-id>-description`.
- Small, focused commits with conventional messages: `type(scope): description`.
- Reference your task ID in commits and PRs.
- Never force-push to `main`. Never rewrite shared history.
- Never commit: reference PDFs, satellite datasets, large rasters, credentials, model artifacts.
- Do not delete or overwrite files you do not own without approval.

## Task Discipline

- Work only on your assigned task. Do not broaden scope without approval.
- Respect file-ownership boundaries (see `docs/TASK_ASSIGNMENTS.md`).
- Changes to shared contracts require approval from all team members.
- Update `docs/STATUS.md` at meaningful checkpoints.
- Record decisions and open questions in `docs/DECISIONS.md`.

## Blocker Protocol

- If you encounter a blocker (missing data, unclear requirement, inaccessible resource), **stop and report it**.
- Do not silently guess, invent data, or work around the blocker.
- Do not approve your own scientific decisions or shared contract changes.

## Context Efficiency

- Read only the files relevant to your current task.
- Use targeted file inspection rather than reading entire modules.
- Prefer small, focused diffs over rewriting whole files.
- Reference task IDs and contract IDs rather than duplicating content.

## Reference Documents

The two project reference PDFs (`IDP_Review_1_AgriSense (1).pdf` and `mava.pdf`) are maintained outside the repository. See `docs/references/README.md` for details. Do not copy them into the repository.
