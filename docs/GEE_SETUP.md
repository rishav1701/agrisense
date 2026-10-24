# Google Earth Engine Access Readiness

> These instructions describe what an AgriSense team member must verify. No private account was accessed, and no credentials are stored here.

## Project setup checklist

1. Use a Google account authorized for the team project.
2. Select or create a Google Cloud Project. Register it for Earth Engine noncommercial use (appropriate for eligible academic research) or commercial use as applicable; do not infer eligibility.
3. Enable the Earth Engine API on that project.
4. Ensure the account has permission to use the project. Follow the organization's Cloud IAM policy; project creation/registration may require an administrator.
5. Install the Earth Engine Python API in the project's environment (`pip install earthengine-api`), authenticate locally (`earthengine authenticate` or `ee.Authenticate()`), and initialize using the project ID. Never send credentials or OAuth tokens to the repository or this chat.
6. Run the verification script below from the same environment. Share only the pass/fail output and a redacted project identifier if the team needs to diagnose it.

Google documents that Earth Engine calls route through a Cloud project; it must have the API enabled, be registered for commercial/noncommercial use, and grant appropriate permissions. Python uses `ee.Authenticate()` and `ee.Initialize(project="...")`. See [access](https://developers.google.com/earth-engine/guides/access) and [authentication](https://developers.google.com/earth-engine/guides/auth).

## Verification script

Save as `scripts/verify_gee.py` after Member A's review/ownership handoff. Replace the placeholder with the project's non-secret project ID or set `EE_PROJECT` in the local shell; do not commit a personal identifier.

```python
"""Check authenticated read access to AgriSense Earth Engine collections."""
import os
import ee

project = os.environ.get("EE_PROJECT")
if not project:
    raise SystemExit("Set EE_PROJECT to an Earth Engine-enabled Cloud Project ID.")

ee.Initialize(project=project)
checks = {
    "Sentinel-1 GRD": "COPERNICUS/S1_GRD",
    "Sentinel-2 SR Harmonized": "COPERNICUS/S2_SR_HARMONIZED",
    "ERA5-Land Daily Aggregated": "ECMWF/ERA5_LAND/DAILY_AGGR",
}
for label, asset_id in checks.items():
    collection = ee.ImageCollection(asset_id)
    first = collection.limit(1).size().getInfo()
    print(f"{label}: collection accessible; one-item probe size={first}")
```

Expected: three lines indicating accessible collections. This proves authenticated collection metadata/query access only; it does not prove spatial/temporal coverage, usable imagery, quota suitability or analysis results.

## Troubleshooting

- **API disabled / not used:** enable Earth Engine API on the project passed to `ee.Initialize`.
- **Project not registered / access denied:** complete Earth Engine registration and confirm IAM access for the signed-in account.
- **No project ID:** set `EE_PROJECT` or pass a project ID directly in the local script.
- **Expired or missing credentials:** authenticate locally again. Do not paste tokens into code, `.env.example`, logs, chat or Git.
- **Dataset not found:** check collection ID spelling and current Earth Engine catalog status.
- **Noncommercial eligibility:** follow the current Google verification flow; do not mark access ready until the project is accepted and the script succeeds.

## Current project state

Earth Engine account/project access has not been tested from this workspace. On 2026-10-24, the local check found no `gcloud` executable, no `earthengine` CLI, and no installed Python `earthengine-api` package. Install the package in the project's approved environment and configure a local authentication method before the probe can run. The required team-side input is a successfully configured project and the non-sensitive result of the three collection probes. See task `T-P1-DE-001` in `docs/TASK_ASSIGNMENTS.md` (owned by Member A).
