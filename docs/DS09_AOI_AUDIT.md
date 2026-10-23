# DS-09 Evidence Audit — TGRAC Agriculture2 and Irrigation Commands

> **Audit date:** 2026-10-23  
> **Decision status:** SRSP Stage I is the leading candidate for further verification; no pilot AOI is selected. `DS-09` remains open.  
> **Scope:** Read-only inspection of TGRAC ground-truth and irrigation-command services and the Copernicus Data Space STAC catalog. No application code, model fitting, scientific performance measurement, or raw-data files were added.

## Recommendation

Advance **SRSP Stage I** as the lead candidate for the next suitability check because it has the largest observed overlap with the queried TGRAC ground-truth layers: 147 points, across all three month layers, in seven districts. Treat this as a candidate only. Its command polygon has an attributed ayacut of 433,249 ha, which is large for a first pilot, and the available records do not validate soil-moisture stress or irrigation advice. The candidate also does not validate the Wanaparthy-specific hypothesis: only 12 records are tagged `Wanaparthy`, all in February, and none intersect any of the seven command polygons in either inspected boundary layer.

The current evidence does not support closing `DS-09` or choosing a final pilot. Boundary lineage and reuse terms are not stated in the service metadata; the field survey date is not a dedicated attribute; label quality and field footprint semantics are unverified; and independent moisture-stress/advisory evidence has not been identified.

## Sources and retrieval

| Source | Inspected content | Verified metadata |
|---|---|---|
| [TGRAC Agriculture2 CropAnalysis MapServer](https://tgrac.telangana.gov.in/arcgis/rest/services/Agri2/Agriculture2_CropAnalysis_Layers/MapServer) | Ground Truth - Rabi Season 2023, child layers 10 February, 11 March, 12 April | Point features; EPSG:4326; current ArcGIS Server version 10.22; layer attributes include district, mandal, village, crop, irrigation type, crop stage, crop condition, `CreationDate`, and edit metadata. `copyrightText` and layer descriptions are empty. The service has attachments. |
| [TGRAC I&CAD MapServer](https://tgrac.telangana.gov.in/arcgis/rest/services/IandCAD_Folder/I_and_CAD/MapServer) | Layers 9 and 10, both named `Command_Boundary` | Polygon features; EPSG:4326; each layer returns the same seven named command/project polygons with coordinate-identical geometries. The metadata does not explain the duplicate layers or specify boundary vintage, lineage, or reuse terms. |
| [Copernicus Data Space STAC API](https://stac.dataspace.copernicus.eu/v1/) | `sentinel-2-l2a` and `sentinel-1-grd` products in the SRSP Stage I bounding box, February–April 2023 | Product-footprint and acquisition-datetime searches. These establish catalog availability, not usable clear pixels or extracted values. |

All 2,446 ground-truth point features and the 14 boundary features were retrieved from the live ArcGIS query endpoints for this audit. No source data were persisted in the repository. The feature-service records do not identify a dataset release/version; `currentVersion: 10.22` is the ArcGIS Server version, not a source-data version. Layer names, service metadata, and retrieval date are the available provenance; independent source lineage remains to be obtained.

### Reproduction

For ground-truth layer IDs 10, 11, and 12, query the layer count with:

```text
<layer-url>/query?where=1%3D1&returnCountOnly=true&f=pjson
```

Retrieve features and geometry in pages to respect the service's 1,000-record limit, for example:

```text
<layer-url>/query?where=1%3D1&outFields=*&returnGeometry=true&resultOffset=0&resultRecordCount=400&f=pjson
```

Repeat with offsets until the returned page is empty. Retrieve candidate command geometries from I&CAD layers 9 and 10 with `where=1=1`, `outFields=*`, `returnGeometry=true`, and `f=pjson`. Both services report WGS84 coordinates, so point-in-polygon checks were made without reprojection. The checks used each returned polygon ring and each returned point coordinate. The reported counts are intersections of the retrieved features; they do not independently validate the accuracy or legal status of either source.

## Ground-truth coverage

The queried monthly layers contain **2,446 points**: February 1,397; March 662; April 387. Their parent is labelled **Ground Truth - Rabi Season 2023**. There is no separate survey/observation-date field in the layer schema. `CreationDate` is database record metadata and is not assumed to be the observation date.

All-service crop-label counts (these points span Telangana districts and are not limited to the named Wanaparthy service context):

| Crop label | Points |
|---|---:|
| Paddy | 1,447 |
| Chillies | 317 |
| Maize | 241 |
| Cotton | 140 |
| Others | 117 |
| Mango | 93 |
| Jowar | 21 |
| Plantation | 21 |
| Ground Nut | 14 |
| Black Gram | 9 |
| Mixed Crop | 8 |
| Bengal Gram | 8 |
| Castor | 8 |
| Red Gram | 2 |
| **Total** | **2,446** |

`Mixed Crop` and `Plantation` occur in returned records but are absent from the inspected crop coded-value domain. Irrigation values also include `tank`, `dripirrigation`, and `sprinkler` in records despite not appearing in the inspected irrigation domain (which lists Canal, Rainfed, Dugwell, and Tubewell). Normalize neither class nor value until this discrepancy is resolved with the provider.

For the SRSP Stage I candidate, the Rabi 2023 month-layer crop counts are:

| Crop label | February layer | March layer | April layer | Total |
|---|---:|---:|---:|---:|
| Paddy | 40 | 28 | 10 | 78 |
| Maize | 26 | 14 | 6 | 46 |
| Cotton | 7 | 0 | 0 | 7 |
| Chillies | 3 | 2 | 1 | 6 |
| Others | 2 | 2 | 0 | 4 |
| Mango | 3 | 0 | 0 | 3 |
| Ground Nut | 2 | 0 | 0 | 2 |
| Jowar | 1 | 0 | 0 | 1 |
| **Total** | **84** | **46** | **17** | **147** |

The candidate point-record `CreationDate` day counts are February 2 (4), 3 (10), 6 (6), 7 (16), 8 (3), 12 (5), 15 (20), 21 (1), 22 (2), and 23 (17); March 10 (11), 13 (1), 17 (4), 18 (9), 21 (15), 23 (1), and 29 (5); April 4 (2), 6 (1), and 21 (14). These are database record-creation dates, not confirmed field-observation dates. The source's month-layer names establish month/season placement only; exact observation dates require provider confirmation.

Only **12** records have `districtname = Wanaparthy`; all are in the February layer and are labelled Paddy (7), Others (4), or Mango (1). All 12 report Dugwell or Tubewell irrigation. None intersects any of the seven command polygons in either layer 9 or layer 10.

## Command-boundary intersections

Each of the seven named polygons in layer 9 was tested against all three monthly point layers. The named polygon geometries in layer 10 were checked and are coordinate-identical to those in layer 9; both layers produced the same per-command counts. There were 264 distinct intersecting points; no point intersected more than one of the seven polygons.

| I&CAD command/project name | `Ayacut_ha` attribute | Feb | Mar | Apr | Total | Crop-label summary | `typeirrigation` summary |
|---|---:|---:|---:|---:|---:|---|---|
| NIZAMSAGAR PROJECT | 93,660 | 14 | 21 | 5 | 40 | Paddy 36, Jowar 3, Others 1 | Tubewell 34, Tank 4, Dugwell 1, Canal 1 |
| Srisailam Left Bank Canal Project (AMRP) | 92,152 | 16 | 0 | 0 | 16 | Paddy 9, Cotton 4, Others 3 | Tubewell 10, Rainfed 4, Canal 2 |
| PRIYADARSHINI JURALA PROJECT | 42,405 | 0 | 1 | 3 | 4 | Paddy 3, Chillies 1 | Canal 4 |
| RAJOLI BANDA DIVERSION SCHEME | 35,425 | 0 | 3 | 3 | 6 | Chillies 2, Jowar 2, Cotton 1, Mixed Crop 1 | Canal 6 |
| KADDAM | 27,530 | 0 | 7 | 0 | 7 | Paddy 4, Mango 1, Mixed Crop 2 | Tubewell 7 |
| **SRSP STAGE I** | **433,249** | **84** | **46** | **17** | **147** | Paddy 78, Maize 46, Cotton 7, Chillies 6, Others 4, Mango 3, Ground Nut 2, Jowar 1 | Tubewell 77, Dugwell 39, Canal 21, Rainfed 5, Drip Irrigation 4, Tank 1 |
| NAGARJUNA SAGAR LEFT MAIN CANAL (NSLC) | 265,373 | 23 | 18 | 3 | 44 | Paddy 21, Others 8, Chillies 6, Maize 4, Cotton 4, Ground Nut 1 | Canal 21, Tubewell 16, Rainfed 6, Dugwell 1 |

The `Ayacut_ha` values are copied from the service attributes; they are not independently verified area calculations. `SRSP STAGE I` has the highest sample count, but the points cover seven districts, 20 mandals, and 42 villages. Class support is uneven: only two Ground Nut points and one Jowar point occur in this command. The 147 points have 147 unique coordinates, but village/mandal grouping remains necessary to avoid spatial leakage.

SRSP Stage I records have crop-condition labels Good 140 and Moderately Damaged 7, with no Severely Damaged records. The service has no measured soil moisture, irrigation amount/timing, or outcome label. These condition labels cannot validate water stress or irrigation recommendations.

## Sentinel acquisition availability and temporal matching

For SRSP Stage I, a bounding-box search against the Copernicus Data Space catalog returned 284 Sentinel-2 L2A products (92 February, 96 March, 96 April; 35 distinct acquisition dates) and 30 Sentinel-1 GRD products (10 per month; 15 distinct acquisition dates). Returned product footprints were then intersected with each of the 147 point coordinates. Temporal proximity was measured to the record's `CreationDate` solely as an explicit proxy because the source has no documented observation-date field.

The Sentinel-2 acquisition dates were February 2, 5, 7, 10, 12, 15, 17, 20, 22, 25, and 27; March 2, 4, 7, 9, 12, 14, 17, 19, 22, 24, 27, and 29; and April 1, 3, 6, 8, 11, 13, 16, 18, 21, 23, 26, and 28. Sentinel-1 dates were February 3, 8, 15, 20, and 27; March 4, 11, 16, 23, and 28; and April 4, 9, 16, 21, and 28. Multiple product tiles can share a date.

| Sensor / collection | Points with a product footprint on the same UTC date as `CreationDate` | Within 24 hours | Within 72 hours |
|---|---:|---:|---:|
| Sentinel-2 L2A | 32 / 147 | 49 / 147 | 147 / 147 |
| Sentinel-1 GRD | 20 / 147 | 25 / 147 | 64 / 147 |

For Sentinel-2, the within-72-hour counts are February 84/84, March 46/46, and April 17/17. For Sentinel-1 they are February 15/84, March 32/46, and April 17/17. This is catalog/footprint availability only. It does not check pixel-level cloud/shadow validity, radiometric processing choices, orbit consistency, image-to-field positional error, or whether `CreationDate` is a field-observation time. A provider-confirmed observation date is required before treating this as a true label-to-image match.

## Training and evaluation suitability

- **Potential training candidates:** The 147 SRSP Stage I points are candidate crop labels only, pending verification of survey provenance, label definitions, positional accuracy, and code-domain inconsistencies. Current support is concentrated in Paddy and Maize; rare labels should not be presented as supported model classes without more evidence.
- **Potential independent spatial evaluation:** 20 mandals and 42 villages permit a group-based holdout to be investigated. Split by geographic groups (and inspect class support in each split); do not randomly split points or pixels. The report does not select a split or claim a validation result.
- **Independent temporal evaluation:** Not established. The layers belong to one Rabi 2023 season; monthly layer placement alone does not create an independent temporal test set, and survey dates are unconfirmed.
- **Irrigation advisory evaluation:** Not supported by the returned fields. The `typeirrigation` field describes source category, while `conditioncrop` is a qualitative crop-condition category. Neither is measured root-zone moisture or an observed irrigation recommendation/outcome.

Evidence still needed for the first pilot's irrigation-advisory objective includes independently sourced field/root-zone moisture observations or a defensible water-balance reference, verified irrigation event timing and quantity where recommendations are evaluated, local soil and crop-stage inputs required by the selected method, and suitable weather observations/reanalysis checks. Canal release records alone would not validate field demand or delivery.

## Unresolved checks before `DS-09` can close

1. Obtain TGRAC confirmation of dataset lineage, source-survey protocol, field-point meaning/positional accuracy, observation date semantics, data update/version history, and reuse/redistribution terms for both services.
2. Determine why two `Command_Boundary` layers (9 and 10) publish coordinate-identical polygons, which layer/vintage is authoritative, and validate topology and `Ayacut_ha` attributes against the responsible irrigation authority.
3. Decide whether the pilot should prioritize the highest-overlap SRSP Stage I evidence or the requested Wanaparthy candidate geography. Wanaparthy records do not intersect these seven boundaries; a matching command or a different usable ground-truth source is needed for a Wanaparthy pilot.
4. Assess whether SRSP Stage I's 433,249 ha extent is workable or whether a sourced, official sub-command polygon can support a smaller pilot without changing its identity.
5. Confirm actual reference dates and rerun point-to-footprint matching using those dates; retrieve and screen pixel data for cloud/shadow and SAR orbit suitability.
6. Establish an independent spatial holdout and identify real moisture-stress/advisory validation evidence before any scientific performance claim.

Until these checks are documented, this report is a source audit, not AOI verification, model validation, or authorization to use the data beyond read-only inspection.
