# AgriSense API & Data Contracts

> **Status: PROVISIONAL — Contract amendment reported approved by all three team members on 2026-10-23. Phase 0 baseline approval and guide waiver are recorded in `docs/STATUS.md`; this does not approve new regional-profile fields or any proposed technical decision.**
> **Contract Version:** `0.2.0-draft`  
> **Implementation gate:** Do not implement dependent modules until the full Phase 0 sign-off is recorded. Future schema changes require approval from all three team members (see `docs/TEAM_WORKFLOW.md`).

---

## 1. Contract Overview and Traceability

| Contract ID | Name | Producer Module | Consumer Module | Primary Data Structure |
|:---|:---|:---|:---|:---|
| `CON-01` | Study Area & Boundary Query | Config / UI | `M-DATA` | GeoJSON Geometry and query metadata |
| `CON-02` | Source Observation Query | `M-DATA` | Data provider | Collection-specific query parameters |
| `CON-03` | Multi-source Observation Stack | `M-DATA` | `M-CLASS`, `M-PHENO`, `M-STRESS`, `M-WATER` | Raster time series and provenance manifest |
| `CON-04` | Crop Classification Result | `M-CLASS` | `M-PHENO`, `M-WATER`, `M-DASH` | Class raster, class map, optional probabilities |
| `CON-05` | Phenology / Growth Stage Estimate | `M-PHENO` | `M-STRESS`, `M-WATER`, `M-DASH` | Stage estimate and uncertainty |
| `CON-06` | Candidate Vegetation / Moisture-Stress Indicator | `M-STRESS` | `M-DASH`, optional `M-CANAL` summary | Indicator raster / feature collection |
| `CON-07` | Crop Evapotranspiration Estimate (`ETc`) | `M-WATER` | `M-WATER`, `M-DASH` | Time-indexed depth estimate |
| `CON-08` | Field Water-Balance Estimate | `M-WATER` | `M-CANAL`, `M-DASH` | Period balance terms and assumptions |
| `CON-09` | Canal-Command Zonal Summary | `M-CANAL` | `M-DASH` | Aggregated statistics; release advice is out of scope |

---

## 2. Standard Data Conventions

1. **CRS and resolution:** Exchange vector geometries in EPSG:4326 unless a provider requires otherwise. Record the actual analysis CRS and grid transform in every raster product. A nominal 10 m output grid is a sampling/resampling choice; it does not make Sentinel-2 20 m bands or ERA5-Land genuinely 10 m data. Choose the projected CRS from the approved AOI.
2. **Time:** Use ISO 8601 UTC timestamps and ISO dates. Date intervals are start-inclusive and end-exclusive when querying provider collections. Preserve each source acquisition/valid time; do not imply that observations from different sensors are simultaneous.
3. **Missing and quality data:** Use raster nodata metadata and per-source quality masks/flags. JSON fields that are unavailable or not computed are `null`, with a reason where relevant. Do not use one shared bitmask to conflate optical cloud, SAR validity, and weather-data gaps.
4. **Units:** State units in field names or metadata. Reflectance is unitless and includes its scale factor. SAR backscatter is dB when identified as such. Weather variables retain provider units and conversion history. Evapotranspiration, rainfall, and water-balance terms are depths in mm over a stated interval. Do not express depth as mm/ha. Convert depth to volume only with an explicit area: 1 mm over 1 ha equals 10 m³.
5. **Traceability:** Every derived product records source collection/version, query interval, processing version, formulas/parameters, and quality limitations. Estimates are not direct field measurements.

---

## 3. Individual Contract Specifications

### `CON-01`: Study Area & Boundary Query

- **Purpose:** AOI and requested observation interval.
- **Schema:** Object containing `query_id` (string), `aoi_geometry` (GeoJSON Polygon or MultiPolygon in EPSG:4326), `start_date` and `end_date` (ISO dates, start inclusive/end exclusive), and optional `target_crs` and `buffer_meters`.
- `start_date` must precede `end_date`; geometry must be valid and non-empty. `target_crs` defaults to the documented project configuration, never to an assumed study region.
- The AOI, CRS, date interval, and buffer must be selected for the study; this contract does not prescribe a region or example coordinates.

### `CON-02`: Source Observation Query

- **Purpose:** Query parameters for a named source collection (for example, Sentinel-2 SR Harmonized, Sentinel-1 GRD, or ERA5-Land Daily Aggregates).
- **Required fields:** `collection_id`, `start_date`, `end_date`, and `geometry_geojson`.
- **Optional source-specific fields:** cloud-cover filter for optical data, orbit/pass and polarization for SAR, requested bands/variables, and provider-specific filters. A cloud threshold is a query choice, not a guarantee of clear coverage. No minimum observation count is assumed.
- Query constraints and collection identifiers must be checked against the selected provider before implementation.
- **Parameter types:** `collection_id` (string), dates (ISO date strings), `geometry_geojson` (GeoJSON object); optional cloud threshold (number in percent), orbit/pass (provider enum/string), requested bands (string array), and provider filters (object).

### `CON-03`: Multi-source Observation Stack

- **Purpose:** Spatially referenced, time-indexed source observations and documented derived features. A stack may align data to an analysis grid, but must preserve source timing, native resolution, resampling method, and validity.
- **Format:** GeoTIFF or xarray/raster array with a manifest. Prefer separate variables and source-specific masks over implying one synchronized sensor image.
- **Possible optical variables:** Sentinel-2 surface reflectance bands, including B02/B03/B04/B08 (10 m source bands) and B11 (20 m source band). Record scaling and any resampling. Cloud and shadow screening applies to optical observations only.
- **Derived vegetation features, when approved and computable:**
  - `NDVI = (NIR - RED) / (NIR + RED)`.
  - `EVI = 2.5 × (NIR - RED) / (NIR + 6 × RED - 7.5 × BLUE + 1)`, using documented reflectance scaling.
  - `NDWI_MCF = (GREEN - NIR) / (GREEN + NIR)` is the open-water index associated with McFeeters' convention.
  - `NDWI_GAO = (NIR - SWIR1) / (NIR + SWIR1)` is the vegetation liquid-water index (also called NDMI in some conventions). Record the exact bands and do not use the ambiguous name `NDWI` alone.
  - `VCI` is computed only when the NDVI baseline period, valid observations, and per-pixel minimum/maximum are documented. Otherwise mark it not computed. Do not impose thresholds through this contract.
- **SAR:** Store VV and VH as calibrated backscatter with units and processing metadata. Any ratio is either a linear ratio of linear power or a difference in dB; name and document which. Do not describe SAR as cloud-masked or interpolated to fill optical gaps.
- **Weather:** Store provider variable, units, aggregation interval, source timestamp, and native grid/provenance. ERA5-Land is coarse-resolution meteorological data; resampling it to a finer grid does not add spatial detail. ET0 is included only if a documented method computes it from available inputs.
- **Manifest fields:** `stack_id`, `analysis_crs`, grid transform/shape, AOI, source collection and versions, source timestamps, requested interval, variable/band definitions, scale/units, resampling methods, masks/quality flags, processing version, and limitations. Values are generated from actual processing; this contract supplies no fabricated metadata sample.
- **Manifest field types:** `stack_id` and `analysis_crs` (strings); `grid_transform` (six-number array) and `grid_shape` (two positive integers) when a regular analysis grid exists; `aoi_geometry` (GeoJSON); `sources` and `variables` (arrays of metadata objects); `requested_interval` (start/end ISO dates); `processing_version` (string); `limitations` (string array). Each source record carries its identifier, collection/version, acquisition or valid time, native grid/resolution when known, and quality-mask reference. Each variable record carries its name, units/scale, source reference, time support, resampling method if applied, and mask reference. Missing/unavailable metadata is `null` with a reason.

### `CON-04`: Crop Classification Result

- **Purpose:** Estimated crop class and, when supported, class uncertainty.
- **Format:** Categorical raster plus a class-map manifest. Probability rasters are optional and must identify their calibration or limitations.
- The class IDs and crop names are defined for the approved study using traceable training labels. This contract does not prescribe crop classes or imply that classes have been validated.
- Record model and feature versions, training-label provenance, spatial/temporal split method, class mapping, nodata code, and evaluation data provenance. Report metrics only when computed on an independently held-out evaluation set; identify the metric and sample/support details. Until then, metrics are `null` / not reported, never illustrative numbers.
- **Manifest fields:** `model_id` and `model_version` (strings); `class_raster` (asset reference); `class_map` (array of `class_id` integer, `class_name` string, and label-source reference); `nodata_code` (integer); `feature_definition_version` (string); `training_label_sources` and `split_design` (provenance objects); `evaluation_metrics` (object or `null`, with data-source and support metadata). Probability output, if generated, is a separately referenced asset with its calibration status/limitations.

### `CON-05`: Phenology / Growth Stage Estimate

- **Purpose:** Estimated crop-specific stage from a documented time series, where observation coverage and crop-specific methodology support it.
- **Format:** Stage raster or time-indexed records, with stage vocabulary version, observation support, and uncertainty/quality information.
- Stage names, transitions, planting assumptions, and parameters remain crop- and study-specific decisions. Do not infer flowering solely from peak greenness unless validated for the selected crop and method.
- Each record identifies crop class, estimate time, stage code (including an explicit uncertain/unavailable state), evidence interval, valid-observation support, and method/version. A confidence score is provided only if its calculation is defined. Smoothing error is a fit diagnostic, not automatically a confidence or accuracy metric.
- **Record fields:** spatial reference (string), crop class ID (integer or `null`), estimate time (ISO timestamp/date), stage code (string from the approved vocabulary or an explicit unavailable code), evidence interval (start/end), valid observation count (integer or `null`), quality state (string), method/version (strings), and confidence (number in [0,1] or `null` only when a defined score exists).

### `CON-06`: Candidate Vegetation / Moisture-Stress Indicator

- **Purpose:** Screen for candidate vegetation condition or possible moisture stress using documented indicators and quality checks. Satellite indices alone do not establish root-zone moisture or diagnose cause.
- **Format:** Raster or GeoJSON features linked to the underlying observations, method, and quality flags.
- Categories, thresholds, stage adjustments, and alert rules are unset until supported by traceable agronomic sources and approved for the study. The output must support an uncertain/insufficient-data state; senescence and other causes of vegetation change must not be silently treated as irrigation need.
- Fields may include geometry/reference ID, estimate time, crop/stage estimates if available, indicator name/value, method/baseline, source observations, quality state, and limitations. Do not include prescriptive actions or fabricated example measurements.
- **Feature fields:** spatial reference/geometry; estimate time; indicator ID and numeric value with units if applicable; crop/stage references when available; method/baseline reference; source-observation references; quality state; and limitations. Category codebooks and threshold values are versioned separately after approval.

### `CON-07`: Crop Evapotranspiration Estimate (`ETc`)

- **Purpose:** Estimate crop evapotranspiration for a stated interval using a documented reference evapotranspiration (`ET0`) and crop coefficient (`Kc`) method.
- **Relationship:** `ETc = Kc × ET0` when the FAO-56 coefficient method and inputs apply. State coefficient source, crop, stage, adjustment method, ET0 method/source, units, interval, and missing-data treatment.
- **Fields:** date/interval; crop and stage references if available; `Kc` and provenance; `ET0` and provenance; `ETc` in mm per interval; precipitation and effective-rainfall terms only when separately computed by a documented method.
- FAO-56 is a methodology reference, not proof that local coefficients or ET0 inputs have been validated. Do not attach invented sample values.
- **Record fields:** interval start/end; crop/stage references when available; `kc_value`, `kc_source`; `et0_value`, `et0_unit`, `et0_source`; `etc_value`, `etc_unit`; method/version; input quality; and limitations. Store ET0 and ETc as depths for their stated intervals. Precipitation is a distinct input, not an ETc subfield.

### `CON-08`: Field Water-Balance Estimate

- **Purpose:** Report the computed terms of a field/area water-balance estimate over a configured period. The period is not inherently an 8-day forecast or irrigation rotation.
- **Units:** Depth terms in mm over the stated period. An area-derived volume may be reported in m³ only when the contributing area and conversion are explicit.
- **Required provenance:** period, area/geometry reference, available ETc and precipitation inputs, effective-rainfall method if used, soil/initial-storage assumptions if used, computation method/version, valid-data coverage, and limitations.
- The water-balance method, soil storage inputs, effective rainfall method, and irrigation efficiency are not fixed by this schema. A missing input must remain missing or be handled by a documented method; do not silently insert a regional soil-water default.
- **Output semantics:** A calculated balance is an estimate, not direct soil-moisture measurement. Do not call it a recommended irrigation depth, urgency, or forecast unless a separately approved and sufficiently supported decision method produces that output. Keep unavailable terms `null` with a reason.
- **Record fields:** spatial/area reference; interval start/end; computed balance terms (name, value, unit, source/method reference); optional area-derived volume and area basis; method/version; valid-data coverage; assumptions; quality state; and limitations. Terms and the reported balance direction must be defined by the selected method. A result value is `null` when the method's required inputs are unavailable.

### `CON-09`: Canal-Command Zonal Summary

- **Purpose:** Aggregate available field estimates within approved command-area boundaries for descriptive analysis.
- **Possible fields:** command-area identifier/source, period, contributing area, valid-data area/coverage, aggregation method, summary statistic and unit, source estimate versions, and limitations. Report depth (mm) and, where justified, area-derived volume (m³) as distinct quantities.
- Aggregation must document how partial coverage, overlaps, missing fields, and area weighting are handled. Do not infer canal delivery, discharge, release schedules, priority, or operational actions from field estimates alone. Those require additional hydraulic and operational data and a separately approved method.
- Command boundaries, names, and identifiers come from project sources; no example location or value is implied by this contract.
- **Summary fields:** `command_id` and source-boundary reference; period start/end; statistic name and value/unit; contributing and valid-data areas with units; aggregation method/version; contributing estimate references; and limitations. Volume is optional and requires an explicit area and conversion. A release recommendation, priority, or schedule is not a field in this contract.

---

## 4. Contract Versioning and Change Governance

1. **Semantic versioning:** Contracts follow `MAJOR.MINOR.PATCH`. A breaking schema or meaning change increments MAJOR; backward-compatible optional additions increment MINOR; annotation-only changes increment PATCH.
2. **Amendment protocol:** Document schema changes in this file. All three team members must approve dependent contract changes before implementation. Approval of this amendment does not constitute final guide or Phase 0 approval.
3. **Synthetic fixtures:** Synthetic examples may be used only in explicitly labelled software tests. They must not be presented as scientific observations, model outputs, validation results, or project evidence.

