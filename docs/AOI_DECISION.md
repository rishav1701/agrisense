# Area of Interest Decision Record — Owner-Directed Pilot

> Updated 2026-10-31. This record documents the project owner's selection for the bounded academic feasibility pilot. It does not certify legal boundary status or scientific model validity.

## Selected scope

- **AOI:** Priyadarshini Jurala Project command polygon from the current TGRAC I&CAD MapServer layer 9 snapshot, stored in `config/study_area.geojson`.
- **Period:** Kharif 2021, using the date range represented in matched TGRAC crop-survey records (2021-08-27 through 2021-10-22).
- **Purpose:** Crop-mapping feasibility only. This small, heavily Paddy-dominated label sample does not support dependable multiclass performance claims.
- **Irrigation advice and validated moisture stress:** Deferred from this pilot because independent local root-zone moisture, irrigation event, and recommendation-outcome data were not identified. Do not produce prescriptive schedules or amounts.

## Evidence and limitations

The TGRAC published polygon reports an ayacut of 42,405 ha, matching the area named for Priyadarshini Jurala in TGRAC's historical Kharif 2014–15 report. This cross-check supports feature identity, but does not establish legal cadastral authority, creation date, or boundary vintage. The selected geometry is the source-preserving current service snapshot; future updates must be versioned and rechecked.

A spatial join of the TGRAC All Crops Survey CTO Records layer 8 records against the polygon found 226 points, of which 159 were marked clear and had nonblank labels. They cover 13 villages across Atmakur, Chinnambavi, Pebbair, and Srirangapur. Of the 159 labels, 150 are Paddy (including source spelling variants), and only nine records represent other crops. The source does not document positional accuracy, independent label verification, or establish that the `today` field is an exact field-observation date. These labels are accepted only for a limited feasibility fit, with provenance, class counts, and uncertainty reported; no robust accuracy claim is authorized by this evidence.

The TGRAC disclaimer describes site information as available for noncommercial purposes including teaching and research. Use is limited to internal academic research with attribution; no standard license or right to redistribute the raw survey rows is asserted. Boundary source, survey query, terms, and limitations are documented in [`DS09_AOI_AUDIT.md`](DS09_AOI_AUDIT.md).

Sentinel-1/2 catalog screening found products intersecting the AOI bounding box during the study period. This is only a discovery result: exact polygon coverage, cloud/quality masks, temporal matching, and usable-pixel counts still require inspection before scientific feature work.

## Gate disposition

- **DS-09:** Closed for the owner-directed AOI and period. Boundary identity is supported for this bounded internal pilot; legal authority and broader reuse remain unclaimed.
- **DS-04:** Accepted for limited feasibility use only. Broad multiclass evaluation remains unsupported; independent, spatially grouped validation and adequate class coverage are future needs.
- **Irrigation advice:** Deferred from this pilot. Reopen only when suitable independent moisture, irrigation-event, and outcome evidence is available.
- **DS-05 canal aggregation:** Deferred; do not infer command-level delivery or irrigated area from this pilot boundary.

This scope decision does not amend shared API contracts. The historical SRSP Stage I evidence remains in `DATA_AUDIT_REPORT.md` as an earlier candidate screen and is superseded for the current pilot.
