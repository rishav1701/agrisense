# Proposed Satellite and Weather Processing Conventions

> **Proposal only — pending technical review by the three-member team.** No processing outputs or scientific results are implied. Follow existing contracts and decisions; this document does not amend `docs/API_CONTRACTS.md`.

## Rishav satellite learning notes — source facts, not approved processing choices

These notes support `T-P2-DE-002` and `T-P2-DE-003` research only. AOI-specific ingestion and implementation remain gated by the P1 handoffs, Gate 0/Gate 1, verified study area and period, provider access, and review of the processing choices below.

### Sentinel-2 L2A facts checked against the Earth Engine catalog

- `COPERNICUS/S2_SR_HARMONIZED` surface-reflectance bands use scale `0.0001`. B2/B3/B4/B8 are 10 m; B8A/B11 and `SCL` are 20 m; `QA60` is 60 m. Preserve native scale metadata; using a common grid is a later, explicit resampling decision.
- `SCL` classes identify cloud shadow (3), medium/high probability cloud (8/9), cirrus (10), and other classes; class 7 is low-probability cloud/unclassified. The catalog documents QA60 as masked from 2022-01-25 through 2024-02-28 inclusive. Thus QA60 alone cannot provide a continuous mask across that interval. This does not select an SCL or cloud-probability rule.
- `NDVI=(B8-B4)/(B8+B4)` and `EVI=2.5*(B8-B4)/(B8+6*B4-7.5*B2+1)` are candidate equations on reflectance-scaled bands; EVI's additive constant makes scaling to reflectance important. Exact masks, zero-denominator handling, and aggregation remain to be selected and reviewed.
- “NDWI” is ambiguous: McFeeters' open-water index uses green and NIR, while Gao's vegetation-liquid-water index was defined for approximately 0.86 and 1.24 µm channels. Sentinel-2 B8/B8A and B11 do not exactly reproduce those stated channel centers; a B8A/B11 combination should not be named or interpreted as Gao's exact index without an explicit adaptation rationale. Neither index is a direct field soil-moisture measurement.

### Sentinel-1 GRD facts checked against the Earth Engine catalog and guide

- Earth Engine `COPERNICUS/S1_GRD` values are calibrated backscatter in dB, with preprocessing including orbit-file application, border/thermal-noise handling, radiometric calibration, and terrain correction. The collection is heterogeneous; polarization, instrument mode, pass direction, and resolution metadata support filtering, but the pilot's orbit and relative-orbit strategy remains open.
- If a cross-polarization ratio is retained as a feature, calculate it in linear power: `VH_linear / VV_linear = 10**((VH_dB - VV_dB)/10)`. Dividing the stored dB values is not a physical power ratio. Whether to include this feature, which orbit/pass to use, and whether any additional speckle filtering is justified remain review questions.

**Sources:** [Earth Engine Sentinel-2 SR Harmonized catalog](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED), [Earth Engine Sentinel-1 guide](https://developers.google.com/earth-engine/guides/sentinel1), [Earth Engine Sentinel-1 GRD catalog](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD), [McFeeters (1996)](https://doi.org/10.1080/01431169608948714), [Gao (1996)](https://doi.org/10.1016/S0034-4257(96)00067-3).

## Sentinel-2 optical data

- Candidate source: `COPERNICUS/S2_SR_HARMONIZED`; record collection, product IDs, processing baseline and retrieval window.
- Mask clouds and shadows using scene classification and/or cloud probability with a documented, tested rule; preserve mask provenance and per-pixel valid-observation counts. Do not choose a cloud-probability threshold until it is assessed for the pilot and validated against inspection.
- Apply the catalog's reflectance scaling/offset convention consistently before computing indices; store units and scaling in metadata. Do not mix scaled and integer reflectance silently.
- Compute indices only from documented bands and retain source bands. Vegetation-index values alone are not ground truth for moisture stress.

### Catalogue discovery implementation

- `src/data/copernicus_stac.py` searches the Copernicus Data Space STAC API's `sentinel-2-l2a` collection by a caller-supplied GeoJSON geometry and date interval. It returns catalogue item metadata only; it does not download assets, establish clear-pixel coverage, or replace a verified AOI.
- The client applies the CON-01 start-inclusive/end-exclusive date rule after the catalogue search and only follows pagination links on the configured HTTPS origin. An optional scene-level cloud percentage is a catalogue filter, not a pixel-level cloud mask or a guarantee of clear observations.
- This is a discovery fallback alongside the owner-preferred GEE direction in `DEC-02`; it does not change the provider decision or establish access to any restricted product. No AOI-specific STAC search or asset download has been run.
- Official provider documentation lists the `/v1/` STAC endpoint, Sentinel-2 L2A collection, geometry/time search, and query extensions. Check the live catalogue and product access terms when a study area is approved.

**Sources:** [Copernicus Data Space STAC API documentation](https://documentation.dataspace.copernicus.eu/APIs/STAC.html), [Copernicus Data Space quotas and limitations](https://documentation.dataspace.copernicus.eu/Quotas.html), [GeoJSON RFC 7946](https://datatracker.ietf.org/doc/html/rfc7946).

## Sentinel-1 radar data

- Candidate source: `COPERNICUS/S1_GRD`; record product IDs, acquisition time, relative orbit, pass direction, instrument mode, resolution and polarisation.
- Restrict comparisons to compatible acquisition geometry/polarisation where feasible; document any orbit/pass harmonisation. Keep VV/VH availability explicit.
- Use the catalog's calibrated backscatter representation and document whether values are linear or dB before ratios/differences. Do not assume a generic despeckle step improves field-scale truth; evaluate filtering/resolution effects before adoption.
- Aggregate temporally with a declared window and robust statistic; retain observation count, date range and quality flags.

## ERA5-Land and water balance

- Preserve native grid/time resolution and source units. Convert accumulated quantities using documented interval semantics and unit conversions before water-balance use.
- Aggregate to a declared local-day convention/time zone and document missing hours/days. Preserve provenance, band names and conversion code.
- ERA5-Land is a coarse meteorological/reanalysis input (approximately 0.1° grid); resampling to a 10 m display grid does not create 10 m weather information. Do not present a simplified balance as direct soil-moisture measurement.

## Spatial grid and study area

- Keep original source CRS and coordinates in raw data. Reproject vectors to a suitable local projected CRS for area/distance calculations; never calculate area in geographic degrees.
- Fix a target raster CRS, origin, pixel size and alignment for each approved AOI. Use nearest-neighbour for categorical labels; choose continuous-data interpolation only with sensor and scale justification. Record any resampling.
- Clip to a verified AOI with a documented boundary source/version. Do not use TGRAC layer 18 as a command boundary; its metadata describes a large parcel dataset.

## Time windows, phenology and missingness

- Derive temporal windows from confirmed planting/observation dates and regional crop calendars, not from database creation timestamps unless their meaning is confirmed.
- Represent growth-stage features as estimates with their method, window and uncertainty. Keep crop classification labels and stress labels as distinct targets.
- Expose missing-data masks, valid observation counts and quality flags. Do not silently fill missing imagery/weather or label imputed values as observations.

## Validation and reproducibility

- Prevent leakage by grouping spatially by field/village/mandal as appropriate and keeping temporal tests separate when independent dates/seasons exist. Check class support in each partition before fitting.
- Report class counts and appropriate metrics/confusion matrices only after labels and a split are accepted. Record baselines and uncertainty; do not invent targets or results.
- Keep source IDs, download dates, processing code version, configuration, units, QA rules and output hashes with each derived product. Configuration must be explicit and version-controlled; secrets stay local.
- Irrigation output is an advisory estimate with documented assumptions, uncertainty, area and units—not an operational instruction or guaranteed field condition.
