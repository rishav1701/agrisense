# AgriSense Work Status — Data Readiness

> Updated: 2026-10-31 (Asia/Kolkata)
> Scope: prerequisite/data audit requested by the project owner. This is not project phase or task completion approval.

> **Current disposition (2026-10-31):** The owner directed a bounded Priyadarshini Jurala/Kharif 2021 crop-mapping feasibility pilot. DS-09 is closed for that scope and DS-04 is accepted for limited feasibility use. Irrigation advice is deferred for lack of independent local outcome data. The remainder of this file records the earlier 2026-10-24 evidence checkpoint and is superseded where it conflicts with this disposition; see [`AOI_DECISION.md`](AOI_DECISION.md) and [`DS09_AOI_AUDIT.md`](DS09_AOI_AUDIT.md).

## Completed with evidence

- Inspected the repository, existing TGRAC audit records, task/ownership instructions, API contracts, and decisions. No inventory workbook (`.xlsx`) existed, so created a canonical evidence workbook at `../outputs/agrisense-data-readiness-2026-10-24/AgriSense_Data_AOI_Inventory.xlsx` with five sheets: overview, dataset inventory, crop counts, spatial overlap and next actions.
- Added a reproducible standard-library TGRAC ArcGIS audit and eight synthetic software tests. The tests validate parsing, pagination/deduplication, missing geometry, geometry bounds and point-in-polygon behavior; fixtures are not scientific evidence.
- Completed a fresh read-only TGRAC retrieval on 2026-10-24: Agriculture2 layers 10/11/12 returned 1,397/662/387 point records (2,446 total); I&CAD layers 9/10 each returned seven polygons. All downloaded geometries are present and well-formed, and source object IDs are unique in each snapshot.
- Verified Agriculture2 layer 18 has 1,131,404 polygon records and parcel/cadastral attributes (`Base_Survey_No`, district/mandal/village, `Irrigation_L_1`–`L_4`, `Irrigation_Code`). Treat it as a parcel-classification layer, not an irrigation command boundary.
- Fresh I&CAD overlaps reproduce 264 candidate intersections; SRSP Stage I has 147 (84/46/17), the largest. No AOI is selected.
- Retrieved 10 layer 18 candidate parcels around source points (service-wide count 1,131,404); the layer is not a command boundary. The point-filtered join finds 12 point matches (7 February for `Land Put to Non Agriculture Use`, 5 February for `Rajiv Bheema LIS`, none in March/April).
- Re-ran local checks on 2026-10-24: 8/8 audit unit tests pass, script byte-compilation and `git diff --check` pass. Rebuilt derived tables and report from saved source JSON; the manifest has no required-layer failures.
- The available Python runtime is 3.12.14. The repository has no `requirements*.txt`, `pyproject.toml` or `environment.yml`; `pytest`, `ruff`, `black` and `isort` are not installed. The audit used `unittest` and `py_compile`; project environment/tooling setup remains Member C's P1 task.
- Reviewed official Earth Engine setup/access requirements and prepared GEE verification guidance below.
- Identified official planning references for DS-06/DS-07 in the crop-label inventory: ICAR Telangana Kharif agro-advisories and FAO-56 Table 12. The references do not resolve the Rabi 2023 calendar, target classes, or local Kc calibration; no scientific parameter was selected.
- Acquired the FAIR-linked Zindi `train.csv` to ignored audit storage (3,489,700 bytes; SHA-256 `92ab358eda4416a7510d174db4925c3599678905f4883a3dccfacb228157b989`). Full standard-library audit: 7,888 rows, 20 columns, no nulls/duplicate FarmIDs, 7,888 POLYGON geometries whose exterior rings pass basic closure/length checks; all dates parse and harvest does not precede sowing. Category/crop/season/district counts are recorded in the crop-label inventory and ignored JSON audit. The source CRS and polygon topology are unknown; no spatial overlap is claimed. FAIR Forward describes source data as CC BY 4.0; the linked Zindi rules explicitly permit challenge-data use/share under CC-BY-SA 4.0. Preserve both provenance statements and apply challenge-copy attribution/share-alike obligations.
- Strengthened boundary-source evidence: TGRAC's program page says command boundaries are taken from project-office maps when available and otherwise may use crop-pattern, terrain, satellite and drainage interpretation; it does not establish the lineage/version of service layers 9/10. CWC/NWIC lists a nationwide command-area GeoJSON resource (GeoJSON, “Other (Open),” last updated 2025-11-17). The full file was downloaded and parsed as documented below.
- Downloaded and parsed NWIC's 204,264,802-byte command-area GeoJSON (1,448 features; checksum/summary in ignored `data/audits/external/nwic_audit.json`). It has 63 features labelled Telangana, including `Sriramsagar Stage-I (Pochampad)` with four beneficiary districts. The project area field is 880,121.94 ha versus TGRAC's 433,249 ha, an unreconciled difference. GeoJSON has projected coordinate values but no CRS declaration, so no cross-source overlay is claimed. The portal's “Other (Open)” metadata is not a specific licence text; obtain terms before use/redistribution.

## Current blockers / missing evidence

1. **Licensing and provenance:** TGRAC metadata has no clear reuse terms, field-survey lineage, positional accuracy, or confirmed observation-date semantics. Obtain written clarification from data custodians before reuse/redistribution.
2. **AOI verification:** TGRAC provides program-level boundary-method documentation but no layer-9/10-specific lineage, vintage, duplicate-layer explanation or reuse terms. NWIC independently lists Sriramsagar Stage-I, but its GeoJSON lacks CRS metadata, and its listed area differs materially from TGRAC's. No geometric match, authoritative boundary or final AOI is verified/selected.
3. **Remaining alternative-data checks:** The linked ADeX endpoint returns 404 and DataSuds records are unavailable. Zindi `train.csv` is acquired and reproducibly counted, but CRS, topology, AOI overlap and label protocol remain unresolved. Zindi challenge rules allow use/share under CC-BY-SA 4.0; maintain attribution/share-alike. FAIR Forward's separate CC BY 4.0 description is retained as source provenance.
4. **Moisture-stress/advisory validation:** no source inspected here provides independently measured soil/root-zone moisture, irrigation timing/quantity, or recommendation outcomes.
5. **Earth Engine execution access:** no private Google account was inspected; the local `gcloud`, `earthengine` CLI and Python `earthengine-api` are absent. Member A must set up the approved environment, authenticate a registered Cloud project locally, and run the verification script in `GEE_SETUP.md`.
6. **Team decisions:** AOI, dataset reuse, scientific methods and proposed conventions require the member approvals already defined in project records. Documentation here cannot supply those approvals.
7. **P1 developer environment:** no dependency manifest or lint/test toolchain is present; Ashwanth C's `T-P1-SH-001` remains the assigned setup task. This is separate from the data evidence blockers.
8. **Crop-calendar and Kc application:** source identification is complete for planning, but the calendar does not match the candidate Rabi 2023 evidence period and generic FAO-56 Kc values need class/assumption review. Do not use them in scientific outputs until the target crop, season, and method are approved.

## Exact next action for project owner

Next, obtain NWIC CRS/feature semantics and exact terms, and check whether a valid matched boundary can be established. Obtain TGRAC survey/reuse details and layer-specific I&CAD boundary authority/terms. Have Member C complete P1 Python tooling and Member A configure and verify Earth Engine locally. The project owner/team must record AOI/method approvals and provide independent moisture/irrigation validation evidence or formally narrow that objective. No credentials need to be shared with this agent.

## Evidence files

- [TGRAC script](../scripts/agrisense_tgrac_audit.py), [software tests](../tests/test_agrisense_tgrac_audit.py)
- [Existing DS-09 AOI audit](DS09_AOI_AUDIT.md)
- [Crop label inventory](data_audit/crop_catalogue_and_labels.md)
- [Source and licence register](DATA_SOURCES_AND_LICENCES.md)
- Raw/reproducible output target: ignored `data/audits/tgrac/` (not versioned)

