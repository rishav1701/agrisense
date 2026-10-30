# Proposed Team Module Interfaces

> **Proposal only; no team approval or implementation is implied.** This file does not change `docs/API_CONTRACTS.md`; changes to shared contracts still require the unanimous approval recorded in project instructions.

## Proposed ownership

- **Rishav:** Sentinel-1/2 processing, crop classification, growth-stage features, model validation and uncertainty.
- **Peter:** ERA5-Land/weather, geospatial assembly, water balance and irrigation-advisory calculations.
- **Ashwaanth:** Browser dashboard, visualisation and application integration. The repository's task assignment spells the name “Ashwanth C”; confirm the preferred spelling with the team.

Follow the authoritative ownership matrix in `docs/TASK_ASSIGNMENTS.md`. The bullets above are a collaboration proposal, not a reallocation of owned files.

## Proposed exchange envelope

All module inputs/outputs should carry a shared provenance envelope consistent with `CON-01`–`CON-09`:

```json
{
  "schema_version": "pending-contract-version",
  "region_id": "configured-region-key",
  "aoi_id": "verified-aoi-key",
  "source_ids": [],
  "generated_at_utc": "ISO-8601 timestamp",
  "period_start": "YYYY-MM-DD",
  "period_end": "YYYY-MM-DD",
  "crs": "explicit CRS identifier",
  "quality_flags": [],
  "assumptions": [],
  "uncertainty": {}
}
```

This is a proposed interface sketch, not a deployed endpoint, approved schema or example scientific output. Use explicit numeric units, UTC timestamps for source instants, and local-day rules only when documented. Geometry coordinates must declare their CRS; raster outputs must include grid transform, pixel size and nodata.

## Module handoffs (proposed)

| Module | Proposed input | Proposed output | Interface boundary |
|---|---|---|---|
| Satellite features / crop model (Rishav) | Verified label set, approved AOI, S1/S2 observation references, configuration | Crop-class estimate, model/version identifier, class probabilities or confidence summary, valid-data flags, temporal feature provenance | Python module output package; no endpoint assumed |
| Weather / water balance (Peter) | ERA5-Land inputs, verified soil/crop parameters, AOI geometry, date convention | Water-balance/advisory estimate with units, forcing provenance, assumptions, quality flags and uncertainty | Python service/module package; no endpoint assumed |
| App / integration (Ashwanth) | Versioned outputs from above and approved contracts | Map/chart views that expose period, units, missing data, provenance and advisory nature | DEC-01 approval to proceed is reported complete; producer handoffs and exact technical interfaces remain open |

## Required semantics

- Crop class and moisture-stress are separate targets with separate label provenance and evaluation.
- Values include units where applicable; dates distinguish observation time from record creation/update time.
- Missing values are represented explicitly and accompanied by quality flags; never encode missing as zero unless the variable definition permits it.
- Model outputs are estimates, include model/configuration identifiers and uncertainty, and are not ground truth.
- Water depth-to-volume conversions require verified area, explicit unit conversions and consistent interval aggregation.
- Configuration is passed explicitly and recorded in provenance; secrets and account tokens are not part of the schema.
- Any API path, request/response schema, status behavior or shared contract change requires Ashwanth's coordination and the existing approval process.

## Open technical design items

The project owner reports all three members approved proceeding with remaining work and reviews (2026-10-31); this is owner-reported and no separate member signatures are stored here. Remaining items are technical/interface decisions, not pending member-approval requests: confirm module handoff formats, schema versioning, geometry serialization, error/empty-state semantics, uncertainty representation, and whether specific contract amendments are needed. No fictional endpoints or unimplemented modules are claimed here.
