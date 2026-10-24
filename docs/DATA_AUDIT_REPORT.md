# AgriSense Data Audit Report

> Evidence date: 2026-10-24 (Asia/Kolkata). The ArcGIS feature snapshots were retrieved during the live audit; this report is derived from their saved original JSON. It records evidence suitability, not data-use approval or scientific validation.

## Executive summary

The live TGRAC retrieval completed for all three crop-label layers, I&CAD candidate boundaries, and a point-filtered subset of Agriculture2 layer 18. It retrieved **2,446 georeferenced ground-truth point records** (February 1,397; March 662; April 387), plus **seven polygons each** from I&CAD layers 9 and 10. All downloaded features had usable geometries and no duplicate source object IDs within their final snapshots. The fresh point-in-polygon computation reproduces the historical leading candidate: **SRSP Stage I has 147 point intersections** (84/46/17 by month), the largest among the seven queried I&CAD candidates.

The 147-point result does not make SRSP a verified AOI. The TGRAC services do not state clear reuse terms or establish survey date semantics, source lineage and positional accuracy; I&CAD metadata does not establish boundary authority, vintage, reuse or why layers 9 and 10 are coordinate-identical. The crop-point condition and irrigation-source fields are not measured soil moisture or recommendation outcomes. The project remains blocked for AOI-specific scientific work and advisory validation.

## Source retrieval and geometry

| Source | Geometry / CRS | Records returned | Use and caveat |
|---|---|---:|---|
| TGRAC Agriculture2 layer 10, February 2023 | Point / EPSG:4326 | 1,397 | Crop label points, Rabi 2023 context |
| TGRAC Agriculture2 layer 11, March 2023 | Point / EPSG:4326 | 662 | Crop label points, Rabi 2023 context |
| TGRAC Agriculture2 layer 12, April 2023 | Point / EPSG:4326 | 387 | Crop label points, Rabi 2023 context |
| TGRAC Agriculture2 layer 18, “Irrigation Projects” | Polygon / EPSG:4326 | 10 returned around observed points; service total 1,131,404 | Cadastral/parcel classification, not a command boundary |
| TGRAC I&CAD layer 9, “Command_Boundary” | Polygon / EPSG:4326 | 7 | Candidate named command polygons; lineage/licence not stated |
| TGRAC I&CAD layer 10, “Command_Boundary” | Polygon / EPSG:4326 | 7 | Same named geometries as layer 9, coordinate-identical in prior and current snapshots |

Raw ArcGIS responses, source-coordinate feature snapshots, the run manifest and derived tables are stored separately under Git-ignored `data/audits/tgrac/`. To reproduce derived outputs from those saved source files without a network request:

```powershell
python scripts/agrisense_tgrac_audit.py --outdir data/audits/tgrac --summarize-existing
```

Use the configured Python environment if `python` does not point to the repository environment. Layer 18 retrieval is point-filtered to parcels intersecting source points; the full statewide 1,131,404-feature dataset was not downloaded.

## Crop-label counts

The source fields report crop labels, but do not by themselves establish survey protocols or label accuracy. Exact label counts by month are in [`data/audits/tgrac/derived/crop_counts_by_month.csv`](../data/audits/tgrac/derived/crop_counts_by_month.csv). The total record counts match the service count queries. Administrative distributions, field missingness and all source attributes are retained in the corresponding derived CSV and raw JSON files.

## Fresh I&CAD candidate overlap

The audit uses source CRS EPSG:4326 for point-in-polygon operations, includes points on polygon boundaries (`covers` semantics), and reports crop/month-specific counts in `overlap_by_source_project_month_crop.csv`. The month totals for I&CAD layer 9 are:

| Candidate command name | February | March | April | Total |
|---|---:|---:|---:|---:|
| SRSP STAGE I | 84 | 46 | 17 | **147** |
| NAGARJUNA SAGAR LEFT MAIN CANAL (NSLC) | 23 | 18 | 3 | 44 |
| NIZAMSAGAR PROJECT | 14 | 21 | 5 | 40 |
| Srisailam Left Bank Canal Project (AMRP) | 16 | 0 | 0 | 16 |
| KADDAM | 0 | 7 | 0 | 7 |
| RAJOLI BANDA DIVERSION SCHEME | 0 | 3 | 3 | 6 |
| PRIYADARSHINI JURALA PROJECT | 0 | 1 | 3 | 4 |

Counts sum to 264 across the seven candidate polygons and three month layers. They are descriptive spatial intersections; no polygon's authority, area, licence or role as a current operational command has been verified. The 12 point records with `districtname = Wanaparthy` are outside these seven polygons (the historical DS-09 finding, still consistent with the current counts).

## Agriculture2 layer 18 point-filtered intersection

The service metadata declares EPSG:4326 and polygon geometry; its fields include base survey number, district/mandal/village, irrigation hierarchy and irrigation code. A multipoint filter against all ground-truth observations within the service extent retrieved **10 candidate parcel polygons**. The derived intersection table reports 12 point matches across two attribute labels: “Land Put to Non Agriculture Use” (7 February points) and “Rajiv Bheema LIS” (5 February points). No matches were reported in March/April. This is not evidence that either attribute label is an authoritative command boundary. The point-filtered subset is retained for audit only and does not replace the separate I&CAD candidate layer.

## Other candidate crop sources

- **WRMS/ADeX and Zindi mirror:** the [FAIR Forward catalogue record](https://fair-forward.github.io/datasets/projects/ui_29-predicting_crop_health_using_opensource_geospatial/) links ADeX ID `583e8f01-160e-4f51-bde5-31dc7f2a5887` (direct access returned 404), the [public GitHub challenge repository](https://github.com/pranavmyname/zindi_crop_health), and the [Zindi challenge](https://zindi.world/competitions/telangana-crop-health-challenge). The full `train.csv` was acquired into Git-ignored `data/audits/external/` on 2026-10-24 (3,489,700 bytes; SHA-256 `92ab358eda4416a7510d174db4925c3599678905f4883a3dccfacb228157b989`). A standard-library audit found 7,888 rows and 20 columns, no nulls or duplicate FarmIDs, 7,888 POLYGON records, and 7,888 exterior rings passing basic closure/length checks. Categories: Healthy 6,506; Diseased 474; Pests 485; Stressed 423. Crops: Paddy 2,268; Cotton 1,692; Maize 1,384; Bengal Gram 938; Groundnut 768; Chillies 614; Red Gram 224. Seasons: Rabi 6,180; Kharif 1,708. All dates parse and harvest dates do not precede sowing dates. Coordinate bounds are x 77.488246–80.296641, y 16.394528–19.911204; the source does not declare a CRS. No polygon topology, AOI intersection, or pixel-date match is verified. FAIR Forward describes the dataset as CC BY 4.0; Zindi's challenge rules explicitly permit challenge-data use and sharing under CC-BY-SA 4.0. The GitHub repository itself has no declared licence. Retain both provenance statements and apply attribution/share-alike conditions to the challenge copy. `Stressed` is not proof of measured soil-moisture stress.
- **DataSuds field survey vectors (2016–19) and rice-frequency rasters:** the associated article describes the products and file/service formats. The DataSuds record URLs currently redirect to an IRD maintenance page; no original file, CRS, extent or record-specific terms were inspected. Rasters are derived rice-frequency products, not independent field labels. [Article and data descriptions](https://pmc.ncbi.nlm.nih.gov/articles/PMC12396292/)
- **CWC/NWIC Water Resource Project:** the [national Command_Area_GeoJSON resource](https://nwdp.nwic.gov.in/en/dataset/water-resource-project/resource/7b1e0abf-ca24-46d2-b0dc-7234021e414d) was downloaded from its direct portal URL and parsed locally (1,448 project features; SHA-256 in ignored `data/audits/external/nwic_audit.json`). It includes 63 Telangana features and a named `Sriramsagar Stage-I (Pochampad)` feature, listing beneficiary districts Nizamabad, Karimnagar, Warangal and Adilabad; its `area_ha` is 880,121.94. TGRAC's candidate feature reports `Ayacut_ha=433,249`; these are unreconciled and may describe different concepts. NWIC coordinates are projected values, but the FeatureCollection does not declare a CRS. No spatial overlay or direct geometric area calculation is made; the recorded area fields remain unreconciled attributes. No AOI is selected. NWIC portal metadata says “Other (Open)” without specific terms text; reuse permission still needs clarification.
- **Boundary provenance / independent source:** TGRAC's [command-area monitoring description](https://tgrac.telangana.gov.in/trac/project-water.php) says boundaries use project-office maps when available and otherwise may be interpreted from crop pattern, terrain, satellite imagery and drainage; it is general program documentation and does not confirm layer 9/10's specific source or version. CWC/NWIC now lists a [Command_Area_GeoJSON resource](https://nwdp.nwic.gov.in/en/dataset/water-resource-project/resource/7b1e0abf-ca24-46d2-b0dc-7234021e414d), with portal metadata “Other (Open),” GeoJSON and last update 2025-11-17. The downloaded resource includes a named Sriramsagar Stage-I feature, but CRS, feature semantics and exact reuse terms remain unresolved.

## Interpretation, AOI status and blockers

1. **Ranked evidence candidate:** SRSP Stage I is first for follow-up because it has the greatest current overlap count and labels in all three monthly layers. The area remains unselected pending authority and licence checks.
2. **Ground truth:** TGRAC labels are potential crop-type references. `CreationDate` is not confirmed as observation date. Labels, survey source, positional accuracy and attribute-domain inconsistencies need provider verification.
3. **Moisture stress / irrigation:** inspected sources do not provide independently measured root-zone moisture, irrigation quantity/timing or recommendation outcomes. Crop-condition categories and irrigation source fields cannot validate those targets.
4. **Imagery and weather:** collection catalog availability is not evidence of valid pixel coverage, field-date matching or low cloud/shadow contamination. Run the GEE access verification and inspect pixel-level imagery only after data terms and AOI are acceptable. ERA5-Land resampling cannot create fine-resolution weather data.
5. **Required approvals / evidence:** written data-use terms and source lineage, authoritative boundary/vintage, confirmed observation dates, a leakage-resistant spatial validation design, and independent field/water-balance evidence remain prerequisites. Team decisions remain governed by `docs/DECISIONS.md` and `docs/TASK_ASSIGNMENTS.md`.

## Verification performed

- TGRAC layers queried using ArcGIS object-ID batches to avoid transfer-limit truncation; layer 18 was queried with small multipoint batches because oversized POST requests returned HTTP 404.
- All features in crop layers and I&CAD layers were retrieved from the live services. No missing or malformed geometry and no duplicate source object IDs appeared in these snapshots.
- The saved-source summarizer regenerated the derived CSV/Markdown report without a network call.
- Eight synthetic software tests passed, Python byte-compilation passed, and `git diff --check` passed after edits. Synthetic fixtures are code tests, not scientific validation.

