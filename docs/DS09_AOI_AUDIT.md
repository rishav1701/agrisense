# DS-09 Evidence Audit — TGRAC Agriculture2 and Irrigation Commands

> **Audit date:** 2026-10-23  
> **Decision status:** SRSP Stage I remains the strongest *candidate* among the seven previously queried TGRAC command polygons; no pilot AOI is selected. `DS-09` remains open.
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

## Follow-up official-source review — 2026-10-29

The official [TGRAC command-area monitoring methodology](https://tgrac.telangana.gov.in/trac/project-water.php) states that project command boundaries were delineated from maps obtained from project field offices where available; where maps were unavailable, command boundaries were demarcated using crop patterns and terrain characteristics interpreted with satellite data and drainage patterns. It also says the resulting crop interpretation was validated using ground-truth data. This is useful program-level lineage context, but it does **not** identify the source map, vintage, derivation path, authority, validation record, or reuse terms for the exact `Command_Boundary` feature in I&CAD layers 9/10. Because the same methodology can include interpretation-derived boundaries, the exact service geometry must not be described as an authoritative cadastral or legal command boundary without layer-specific confirmation.

TGRAC's [Agriculture & Soil project page](https://www.tgrac.telangana.gov.in/trac/agriculture-project.php) describes its Integrated Seasonal Condition Monitoring System as mandal-level seasonal monitoring using MODIS/AWiFS indices, rainfall and other context, with ground-truth verification. Its stated monitoring categories are drought/agricultural condition categories, not plot-level measurements of root-zone moisture or validated irrigation recommendations. This supports using TGRAC ground-truth as a candidate crop/agriculture evidence source only after its own label semantics and lineage are confirmed; it does not supply an independent field-moisture or irrigation-outcome target for AgriSense.

The practical recommendation remains **do not select SRSP Stage I yet**. Its 147 intersecting points give it the strongest count among the seven queried commands, but do not outweigh unresolved source lineage/terms, questionable point-to-image date semantics, spatially sparse/imbalanced class support, a very large attributed extent, and the absence of moisture/advisory validation evidence. The official methodology review narrows the follow-up request: ask TGRAC/I&CAD for the layer-9/10 source project map and vintage, the authoritative layer, any interpretation/validation record, the geometry reuse terms, and confirmation of point survey protocol/date/positional accuracy. No AOI, CRS, period, boundary file, or label use is approved by this research update.

## Public Sentinel extraction proof — 2026-10-29

An unauthenticated catalog search against [Element 84 Earth Search](https://earth-search.aws.element84.com/v1/) found Sentinel-2 L2A items over a 0.01° × 0.01° technical window at `[79.145, 18.795, 79.155, 18.805]`. The four rectangle corners fall inside the polygon returned for SRSP Stage I in I&CAD layer 9, but the boundary's authority and reuse terms are unresolved. For 2023-02-01 through 2023-03-01, the catalog returned six products with scene-level cloud-cover values at or below 30%; the returned dates were February 2, 7, 12, 17, 22, and 27. This box is an extraction smoke-test window only. It is not a selected field, irrigation command, production AOI, or label footprint.

The Earth Search `sentinel-2-l2a` collection exposes COG assets for B02, B04, B08, and SCL. Its STAC collection has an inconsistent `license` string (`proprietary`) while linking to the [Copernicus Sentinel data legal notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice), which grants free access and lawful reuse including adaptation and combination. The [AWS Open Data record](https://registry.opendata.aws/sentinel-2-l2a-cogs/) also points to the Sentinel data terms. The downloader records these links and attribution; it does not redistribute the raster data in Git.

The extracted Sentinel-2 item was `S2B_44QLF_20230217_0_L2A` (2023-02-17 05:23:42 UTC; scene cloud-cover statistic 0.000116%). B02, B04, and B08 are 10 m; each yielded 11,666 valid AOI pixels. SCL remains 20 m and yielded 2,924 valid AOI pixels. These counts are source-mask coverage summaries, not a cloud-free or scientific adequacy claim.

`src/data/sentinel_stac_assets.py` and `scripts/acquire_sentinel2_aoi.py` implement generic STAC search, least-cloudy scene selection, exact polygon masking, and native-grid COG window extraction. SCL remains at its source 20 m grid and the B02/B04/B08 bands remain on their source 10 m grid; no resampling or indices are produced. Extraction output is ignored under `data/cache/`, and a per-scene JSON manifest records the AOI, acquisition time, cloud statistic, source links, data scales/offsets, dimensions, CRS, and limitations. The scene-level cloud statistic is not a pixel quality assessment.

This public Sentinel source resolves satellite catalog/access feasibility for a technical trial; it does not close DS-09 or DS-04. The SRSP command boundary and TGRAC field labels still have unconfirmed source lineage and reuse terms. The tested date interval is historical and not a confirmed label observation period. Before scientific use, obtain a selected and licensed AOI/label source, verify dates and field alignment, inspect pixel masks and coverage, and agree on a CRS and compositing method. The Sentinel collection metadata exposes band scale `0.0001` and offset `-0.1`; callers must preserve and apply the asset metadata rather than assume every product uses zero offset. ESA's product equation applies the per-band BOA offset before division by the quantification value ([Sentinel-2 product documentation](https://sentinels.copernicus.eu/documents/d/sentinel/sentinel-2-products-specification-document-15_1)).

The same technical window was queried against Microsoft's [Planetary Computer STAC API](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-rtc). Its `sentinel-1-rtc` collection metadata declares `CC-BY-4.0`; the [Planetary Computer SAS documentation](https://planetarycomputer.microsoft.com/docs/concepts/sas/) says a public read token can be obtained anonymously, and a live token request/read succeeded. The latest item in the trial interval was `S1A_IW_GRDH_1SDV_20230220T003844_20230220T003909_047312_05ADAE_rtc` (2023-02-20 00:38:56 UTC; relative orbit 165; descending). VV and VH were extracted as Float32 windows in EPSG:32644 on a 10 m grid with 11,666 AOI pixels. The output files are local/ignored, and signed URLs are not written to the manifest.

For these selected items, the S1 and S2 10 m windows have identical EPSG:32644 transforms and dimensions (113 × 108). This is an observed match for this pair only; the acquisition code does not force or assume alignment for other scenes. The S1 and S2 acquisitions are about 67 hours apart, but the TGRAC source does not provide confirmed field observation times, so this is not a label match.

The provider's STAC assets declare Float32 and nodata `-32768` but omit a unit/radiometry field. Microsoft's [AI4G Sentinel-1 instructions](https://github.com/microsoft/ai4g-flood/blob/main/README.md) identify Planetary Computer RTC processing as gamma0 with power scale and note the RTC calibration/terrain-correction lineage. The extractor therefore records gamma0 power as the documented product interpretation and preserves raw pixels; it does not make dB features. A future feature step may convert positive power to dB with `10 log10(power)` after the team reviews the intended radiometry and temporal/orbit strategy. Earth Search's Sentinel-1 GRD COG also returned `uint16` measurement pixels without a georeferenced CRS in the live check; it was not treated as analysis-ready. The PC RTC source was chosen for technical AOI extraction, not as approval to switch `DEC-02` or as a final GRD processing-method decision.

## AOI and data-access reassessment — 2026-10-31

### Best-supported candidate and limits

**Recommendation for the next evidence step: continue with SRSP Stage I, Rabi 2023, as the lead candidate only. Do not create or approve `config/study_area.geojson` yet.** It remains the strongest of the seven previously tested TGRAC command polygons for a crop-mapping feasibility study by raw sample count and label variety: 147 intersecting candidate points, 8 observed crop labels, 42 villages and 20 mandals. The disadvantages are material: the service's attributed area is 433,249 ha (not independently measured), the points span seven districts, labels are imbalanced (Paddy 78, Maize 46, all other classes 7 or fewer), and record-creation dates are not confirmed field-observation dates. This is a lead for source confirmation, not a “perfect” or verified AOI.

The smaller candidates do not currently dominate it: Nizam Sagar has 40 intersections over an attributed 93,660 ha but 36 are Paddy; NSLC has 44 over 265,373 ha, with only 21 Paddy records and several sparse classes. These counts are from the same unverified TGRAC layers and do not establish ground-truth suitability. No candidate in this audit has confirmed moisture-stress measurements or irrigation recommendation outcomes. If those are required in the initial pilot definition, none of the seven qualifies today.

### Newly checked source/access evidence

| Need | Current evidence and access result | Consequence |
|---|---|---|
| Command polygon | NWIC's National Water Data Portal lists a CWC-produced national “Water Resource Project” command-area dataset, updated 2025-11-17, with KML, GeoJSON and SHP downloads. The GeoJSON resource metadata says **“Other (Open)”**, not a specific reuse license. The portal listing/download link is public, but the geometry contents and SRSP feature match were not independently verified in this review. [Dataset page](https://nwdp.nwic.gov.in/en/dataset/water-resource-project) · [GeoJSON resource metadata](https://nwdp.nwic.gov.in/en/dataset/water-resource-project/resource/7b1e0abf-ca24-46d2-b0dc-7234021e414d) | Promising independent boundary source. Ask CWC/NWIC to confirm precise terms, vintage, project identity, and whether the data are suitable for redistribution/use; compare the actual polygon to TGRAC layers 9/10 before selecting. |
| Ground truth | TGRAC's public read-only ArcGIS query returned the earlier 2,446 Rabi 2023 points, but the exact layer has empty copyright/description fields. Separately, FAIR Forward describes a WRMS field-survey dataset (>12,000 observations, six Telangana mandals, 2022–2024 cycles) as CC BY 4.0; its cited ADeX dataset URL returned 404 on this check. Zindi's completed challenge page lists train/test files and says challenge data are CC-BY-SA 4.0, with access gated by accepting challenge terms. [FAIR Forward source](https://fair-forward.github.io/datasets/projects/ui_29-predicting_crop_health_using_opensource_geospatial/) · [Zindi data page](https://zindi.world/competitions/telangana-crop-health-challenge/data) | The WRMS dataset is a better potential label source because it has documented field visits and a stated license, but current direct retrieval is not confirmed and the six mandals are not identified in the catalog record. Zindi challenge targets/fields must be inspected under its terms and are not automatically independent field-moisture truth. Do not substitute either source for TGRAC or claim label validation until the records, locations, dates and terms are checked. |
| Sentinel-2 | Copernicus Sentinel data are free/open with attribution; public STAC/COG access has already succeeded in the technical trial. [Sentinel legal notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice) | Data access is available without GEE for the tested public sources. AOI/date selection, pixel quality and label matching remain unverified. |
| Sentinel-1 | Public Planetary Computer Sentinel-1 RTC access succeeded for the technical trial; the collection declares CC-BY-4.0. This is not approval of an analytical method or orbit convention. | Technical access available. Production time-series/orbit choices and matching still require review. |
| Weather / ET₀ | ERA5-Land is available via CDS under CC BY, but accepting terms requires CDS login/registration. GEE-hosted daily aggregates require Earth Engine access; this checkout has no configured GEE project/authentication. [CDS ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land) · [Earth Engine collection](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR) | A lawful data route exists, but account-level access is not provisioned here. The daily aggregation convention must be selected; native weather support is about 0.1°/11.1 km and must not be portrayed as 10 m weather. |
| Soil, if storage balance is selected | SoilGrids maps are CC BY 4.0 at 250 m with uncertainty; public WCS/WMS routes exist. ISRIC states its beta REST API is currently paused, while recommending alternative access paths. [ISRIC SoilGrids](https://isric.org/explore/soilgrids) · [access FAQ](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_02.html) | Candidate modeled soil inputs are accessible, but are not field soil measurements or crop-specific root-zone parameters. Use only if the approved balance method supports the available layers/depths and uncertainty. Otherwise restrict the balance scope. |
| Crop calendar / independent advisory truth | Telangana's I&CAD page publishes broad Kharif/Yasangi calendar windows; the state crop-statistics page defines Kharif and Rabi periods. Neither supplies a command-specific observed crop calendar, soil moisture or irrigation outcome. [I&CAD calendar](https://irrigation.telangana.gov.in/) · [Telangana agricultural statistics](https://ecostat.telangana.gov.in/agricultural_statistics.html) | General timing context is public, but crop-specific phenology validation and advisory validation remain unavailable from these sources alone. |

### Selection gate disposition

The evidence supports **a lead-candidate recommendation, not AOI approval**. The most defensible near-term scope is a crop-mapping feasibility pilot in SRSP Stage I only after (1) the actual CWC/TGRAC boundary identity and reuse terms are verified, (2) a usable version of the WRMS/ADeX or another label source is retrieved with its terms, coordinates, crop meaning and field dates, and (3) label-to-image timing and pixel quality are checked. If those conditions fail, reopen the candidate comparison rather than substituting an administrative boundary or assuming the TGRAC point records are valid.

For the broader moisture-stress and irrigation-advisory objective, treat that as a separate future evidence gate: the currently identified crop-health/condition labels do not provide measured root-zone water status, verified irrigation timing/quantity, or observed recommendation outcomes. No stress threshold, soil-storage balance, or operational advice is validated by this access review.

The previous reassessment added no AOI geometry or production cache and changed no API contract or scientific method. Public catalog presence is not proof of lawful reuse unless the source terms are clear, and access to an account-gated service is not confirmed without credentials and a successful query.

## Cross-source command and challenge-data screen — 2026-10-31

### CWC command-area download

The public NWIC GeoJSON download was retrieved to temporary storage for a read-only source check (about 204 MB; the national dataset was not copied into the repository). It contains a Telangana feature named **“Sriramsagar Stage-I (Pochampad)”**, with `org_yr_ap=1964`, `status=Completed`, and `area_ha=880121.9431`; a separate `cca` property is `581` and is not defined in the available resource metadata. Its geometry is EPSG:7755 (WGS 84 / India NSF LCC) and was transformed to WGS84 for candidate screening. This independently confirms that CWC publishes a project-area feature for the same named system, but does not prove it is the same extent as TGRAC's `SRSP STAGE I` polygon. The two sources expose area fields with different names and undefined semantics; do not compare them as equivalent acreage values without CWC/TGRAC clarification. The NWIC resource is still marked only “Other (Open)”; no precise reuse license was found.

### Zindi challenge access and provisional spatial screen

The official [Zindi challenge data page](https://zindi.world/competitions/telangana-crop-health-challenge/data) lists `Train.csv` (3.3 MB), `Test.csv`, and the challenge variable definitions. The challenge rules state that permitted challenge data are shared under CC-BY-SA 4.0. However, a direct unauthenticated request to the official Train.csv endpoint returned HTTP 401. The official file therefore remains inaccessible from this environment without an authorized challenge session.

For a **non-authoritative sensitivity check only**, a publicly available participant mirror of `Train.csv` was inspected in temporary storage. It has 7,888 rows with `Crop`, `category`, `Season`, `SDate`, `HDate`, `Sub-District`, and farm-polygon geometry. Its reported footprint spans 14 districts and 116 sub-districts, which conflicts with FAIR Forward's catalog description of the WRMS/ADeX survey as covering six mandals. The mirror's checksum could not be compared to the official file because that endpoint requires authorization. Treat all results below as exploratory screening counts, not accepted ground truth, until the source copy is retrieved and reconciled.

Using each mirrored farm polygon's coordinate-vertex mean as a representative point (not a full polygon overlay), the row counts inside TGRAC layer-9 command geometries were:

| Candidate command | Mirrored farm rows, all seasons | Mirrored Rabi rows with `SDate` 2023-10-01–2024-04-30 | Rabi crop labels in that interval | Rabi `category=Stressed` rows |
|---|---:|---:|---|---:|
| Srisailam Left Bank Canal Project (AMRP) | 462 | 311 | Paddy 259, Cotton 49, Groundnut 3 | 8 |
| **SRSP STAGE I** | **537** | 152 | Chillies 102, Maize 37, Cotton 12, Groundnut 1 | 8 |
| NAGARJUNA SAGAR LEFT MAIN CANAL (NSLC) | 328 | 285 | Paddy 89, Groundnut 188, Cotton 8 | 12 |

The CWC Sriramsagar Stage-I project feature contains 572 mirrored farm centroids overall and 159 with `Season=Rabi` and sowing date in that interval (Chillies 107, Maize 39, Cotton 12, Groundnut 1; 8 rows labeled “Stressed”). This count is for the CWC feature itself, not a validation that its full extent matches TGRAC's Stage-I command polygon.

These data suggest that **SRSP Stage I remains the broadest crop-diversity candidate**, while NSLC and AMRP have more rows in the mirror's Rabi 2023–24 window. This does not identify a perfect AOI: the challenge copy is not authenticated, the mirror/catalog footprints conflict, the health category “Stressed” is not demonstrated to mean measured water stress, and its 8–12 candidate stress rows per command cannot validate stress detection or irrigation advice. Dataset terms and label semantics need source confirmation before any training or performance use.

### Updated choice and phase-gate disposition

Prioritize **SRSP Stage I / Sriramsagar Stage-I (Pochampad)** for the next authorized source-resolution step because (a) TGRAC's candidate audit found the greatest overlap with its point labels, (b) NWIC/CWC publishes a same-named project feature, and (c) the provisional challenge mirror shows broad crop coverage there. Keep **AMRP and NSLC** as comparison candidates until the official field file and exact boundary relation are established. A study interval of **Rabi 2023–24** is a research candidate, not an approved period.

`DS-09` and `DS-04` remain open. The exact CWC/TGRAC boundary identity, legal reuse terms, official challenge-data access, and label consistency are unresolved; no production AOI file or field-label copy was added. `DS-06`/`DS-08` methods and independent crop-water/advisory validation also remain open. These are source/access/evidence gates, not member-approval waits, and cannot be closed by an agent or owner assertion alone.

## Gate-resolution review — 2026-10-31

### Boundary source, reuse, and extent

The NWIC [copyright policy](https://nwdp.nwic.gov.in/en/footer/copyrightPolicy) says material featured on its site may be reproduced free of charge in any format if accurately reproduced, not used misleadingly/derogatorily, and prominently attributed; it excludes material explicitly identified as third-party. The CWC resource lists CWC as producer and the inspected resource metadata does not mark the data as third-party. This provides a documented attribution-based reproduction route for the published CWC geometry. Record the exact source/version and preserve feature attributes when creating any derived copy. The resource itself is still labeled “Other (Open),” so this policy does not establish a standard open-data license or resolve third-party rights in source material embedded by CWC.

The official TGRAC 2014–15 command-area report identifies TGRAC/Planning Department as the mapping/reporting source and lists SRSP ayacut as **387,266 ha**, 81 mandals, and 1,096 villages. This differs from the 433,249 ha `Ayacut_ha` value in the queried TGRAC feature and the CWC feature's `area_ha=880121.9431`; CWC's separate `cca=581` also lacks a definition in the inspected resource metadata. These values cannot be silently reconciled or treated as the same command extent. The official report is historical context and does not identify the vintage/source map for the live ArcGIS polygon.

**Boundary disposition:** CWC offers a credible, attributable *published project-area* geometry suitable for an exploratory, source-limited AOI if the study explicitly uses the CWC feature as its boundary definition. It is not established as the current legal Stage-I command boundary, and it is not geometrically equivalent to TGRAC's polygon on the evidence inspected. Therefore `DS-09` can close only for a project-area feasibility scope that accepts the stated CWC geometry and its limitations; it cannot close as a verified legal irrigation-command AOI without CWC/I&CAD confirmation of feature meaning, geometry vintage, and the large area discrepancy. No polygon is selected in this audit because project scope has not explicitly accepted that narrower AOI definition.

### Accepted field-label path

The solution for `DS-04` is to use the challenge's official Zindi `Train.csv` through an authorized challenge account, record the download date and checksum, retain the challenge rules/attribution, and audit row count, schema, coordinate CRS, polygon validity, date definitions, crop/health label definitions, and geography against the WRMS/ADeX catalog before accepting it. Official challenge terms state CC-BY-SA 4.0, but unauthenticated access returned 401 here, and the third-party mirror's checksum could not be compared. The FAIR Forward catalog's linked ADeX resource returned 404. Thus there is a specific eligible source and a review protocol, but no accepted copy has been obtained; the agent cannot manufacture access or certify the mirror. TGRAC remains a fallback only if the provider confirms survey lineage, observation dates, class meanings, positional quality, and use terms.

An independent evaluation should be grouped by farm/field and then by spatial units (e.g. hold out entire mandals where sample coverage allows), with the split fixed before feature/model fitting. Crop-health `category` labels may evaluate that dataset's stated health classification after definitions are verified; they must not be relabeled as measured soil-water stress or irrigation outcomes without a documented mapping study and direct evidence.

### Irrigation-stress and recommendation validation path

ISRO reports a freely available EOS-04 500 m soil-moisture product with 17-day repeatability through Bhoonidhi and says validation incorporated in-situ measurements. Bhoonidhi's 2024 newsletter lists direct download from November 2023 onward, and its official API documentation says registration/login is required to search and download. Thus access is available through a registered account, but no account is configured here and AOI/date-specific item availability has not yet been queried. It is a promising **independent sensor-product cross-check** for regional surface-moisture patterns, subject to obtaining the matching dates/tiles, product documentation, and the actual validation statistics for Telangana. It is not field-level root-zone truth, irrigation-event data, or evidence that an AgriSense recommendation improved outcomes. The newer NISAR 100 m product described by ISRO is still undergoing systematic evaluation at calibration/validation sites, so it is not a mature substitute for local ground observations.

Source references: [ISRO EOS-04 product announcement](https://new1.isro.gov.in/ISRO_EN/High-Resolution_Operational_Soil_Moisture_Product.html), [Bhoonidhi API specification and registration requirement](https://bhoonidhi.nrsc.gov.in/bhoonidhi-api/), and [Bhoonidhi 2024 product-availability notice](https://bhoonidhi.nrsc.gov.in/bhoonidhi_resources/help/newsletters/Bhoonidhi_Newsletter_2024_Edition_2.pdf). The public catalog advertises product access; a registered account is required to query/download through the documented API.

The defensible implementation path is staged: (1) prototype clearly labeled moisture-stress *estimates* with documented FAO-56/balance assumptions; (2) compare temporal/spatial patterns with EOS-04 as an external product check, keeping its 500 m/17-day support; (3) do not publish prescriptive irrigation amounts or claim validated advice until paired local root-zone sensor/gravimetric observations, crop stage, soil properties, irrigation event timing/quantity, and preferably recommendation/outcome records are obtained from a documented field study. Canal-release records can contextualize supply but cannot replace plot-level irrigation or crop response.

**Validation disposition:** This closes the search for a practical open external moisture-product reference, not the scientific validation gate. In the present data environment, the project must describe irrigation advice as an unvalidated research prototype or defer that feature; no wording, threshold, satellite product, or water-balance simulation can substitute for missing independent outcomes.

### Required gate decision

The work now has specific, source-grounded paths for all three blockers, but not evidence to mark all three closed. `DS-04` still requires the authorized official file or provider-confirmed TGRAC package. `DS-09` still requires the owner/team to accept a CWC *project-area* boundary definition, or obtain authoritative clarification if the requirement is a current command polygon. Advisory validation still requires local observations/outcomes; until then, the recommendation feature must remain non-prescriptive and unvalidated. No AOI polygon, label dataset, or model result was added based on unverified sources.

## Owner-directed pilot resolution — 2026-10-31

Following the project owner's explicit authorization to close the listed phase issues, the pilot is now defined as **crop-mapping feasibility in the TGRAC-published Priyadarshini Jurala Project command polygon, Kharif 2021**. This supersedes the earlier SRSP Stage I lead-candidate recommendation. It is a bounded academic research scope, not a legal cadastral certification or a validated multi-crop/irrigation-advisory system.

### Boundary and study period (`DS-09`)

The selected feature is `PRIYADARSHINI JURALA PROJECT` from [TGRAC I&CAD MapServer layer 9](https://tgrac.telangana.gov.in/arcgis/rest/services/IandCAD_Folder/I_and_CAD/MapServer/9), retrieved 2026-10-31. Its `Ayacut_ha` attribute is **42,405 ha**, matching the historical TGRAC Kharif 2014–15 report's 42,405 ha for the Priyadarshini Jurala Project. The current service snapshot is the operational boundary vintage for this study; the service does not disclose the original delineation date or certify the line as a legal cadastral record. The ring is stored in WGS84 in [`config/study_area.geojson`](../config/study_area.geojson), with the source feature ID, source URL, retrieval date, use terms, and limitations retained in its properties.

TGRAC's [website disclaimer](https://www.tgrac.telangana.gov.in/trac/disclaimer.php) describes the site's information as provided for non-commercial purposes such as teaching, research, and extension. This academic pilot uses the source for internal non-commercial research with attribution; no standard data license or external redistribution right is claimed. The geometry was accurately reproduced from the TGRAC service and must not be presented as independently surveyed.

The study period is **Kharif 2021**, aligned to the TGRAC SurveyCTO `today` field dates observed among points within the selected command: **2021-08-27 through 2021-10-22**. The selected period is the survey form's captured date window; it does not represent a season-wide field census.

### Accepted crop-label source and limits (`DS-04`)

The earlier Rabi 2023 monthly point layers are not the selected labels. The replacement is the public TGRAC [All Crops Survey CTO Records layer 8](https://tgrac.telangana.gov.in/arcgis/rest/services/Agri2/Agriculture2_CropAnalysis_Layers/MapServer/8). A read-only query of its `WANAPARTHY` records returned **673 rows**; spatial screening of the GPS attributes against the selected Jurala polygon found **226 records**, of which **159** have `a_status_1 = “Crop is present and clearly identifiable”` and a nonblank `purecrop_n` crop label. These 159 records include **158 unique GPS coordinate pairs**, span **4 mandals and 13 villages**, and cover the selected Kharif 2021 date window. The source geometry is rounded to three decimal places; the survey's explicit GPS coordinate attributes were used for the overlap, preserving six-decimal coordinates. GPS positional accuracy is not documented.

Raw label counts among the 159 accepted clear-label records are: `Paddy | వరి` 135, `Paddy` 15, `Maize / Corn / Sweet Corn` 4, `Blackgram | మినుములు` 3, `Groundnut | వేరుశనగ` 1, and `Sugarcane` 1. Preserve the raw labels; confirm/record any bilingual alias normalization before fitting. The source's own clarity status supports excluding blank, damaged, harvested, and not-yet-identifiable entries. TGRAC's non-commercial research terms provide an in-scope use basis for this academic feasibility pilot; retain attribution and do not publish the raw survey records outside the project without separate permission.

**Model/evaluation scope:** This is an accepted source for a **limited feasibility fit**, not a balanced all-crop training set. Paddy dominates and several classes have only one to four observations. The sample is suitable for building the acquisition/label pipeline and investigating a spatially grouped proof of concept; it does not support reliable per-class performance claims. Any exploratory holdout must group by village (or mandal), keep all points/pixels from a group together, show per-class support, and be reported as exploratory only. No accuracy metric is authorized from this evidence alone.

### Crop-water and irrigation-advice scope

**Independent irrigation-advice validation is removed from this pilot's exit criteria and deferred to a future field-validation phase.** This resolves the current phase gate by narrowing the pilot to crop-mapping feasibility; it does not claim the evidence exists. The dashboard/model must not issue irrigation amounts, prescriptive schedules, or validated water-stress labels in this phase. If a later phase restores that objective, it must obtain paired local root-zone measurements, irrigation timing/quantity, crop/soil context, and observed outcomes. EOS-04 can be an external regional moisture-product check only after accessing its separately dated data; it is not a substitute for those records.

### Closure record

- `DS-09`: **closed for the defined academic pilot** — TGRAC Jurala command feature selected, source snapshot retained, period set to Kharif 2021, and matching survey records spatially confirmed. Legal cadastral status remains outside the claim.
- `DS-04`: **closed for limited crop-mapping feasibility use** — an authorized public TGRAC survey layer with source research terms, capture-date field, crop-identifiability status, and GPS records is available; model performance validation remains explicitly out of scope because class support is imbalanced and positional uncertainty is undocumented.
- Irrigation advice: **deferred from this pilot** — no irrigation recommendation or claim of validated moisture-stress detection is in scope until local field outcomes are collected.

No raw label rows were persisted in the repository. The boundary file is a source-preserving geometry copy with attribution/terms metadata. The code checkout has no acquired Sentinel raster or ERA5-Land records; catalog access is demonstrated for the selected AOI and study window, but pixel masks and final feature suitability still require acquisition and QA before any scientific output.

Runnable trial commands (replace the GeoJSON path/dates with the project's verified inputs):

```powershell
python -m scripts.acquire_sentinel2_aoi --aoi <aoi.geojson> --start-date 2023-02-01 --end-date 2023-03-01 --output-dir data/cache/sentinel2
python -m scripts.acquire_sentinel1_rtc_aoi --aoi <aoi.geojson> --start-date 2023-02-01 --end-date 2023-03-01 --output-dir data/cache/sentinel1
```

Both commands require `requirements-science.txt`; output rasters remain ignored by Git. The code crops to the AOI's native-grid pixel window, requires the source raster to cover the full AOI bounding window, and applies a pixel-center polygon mask. It does not reproject or align S1 and S2. This sample pair happened to share a grid; a common-grid rule and matched acquisition-date strategy remain open method decisions.
