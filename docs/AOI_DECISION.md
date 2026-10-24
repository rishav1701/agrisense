# Area of Interest Decision Record — Evidence State

> Updated 2026-10-24. This is a recommendation state, not a final selection or data-use approval.

## Recommendation

Keep **SRSP Stage I** as the first-ranked candidate for further verification, not as the selected AOI. Existing DS-09 results report the highest overlap among seven TGRAC I&CAD candidate polygons: 147 unique points (84 Feb, 46 Mar, 17 Apr 2023), versus 44 for NSLC, 40 for Nizamsagar and fewer for the remaining four. This ranking is a coverage screen only.

Do not begin AOI-dependent scientific training or advisory validation until boundary authority/terms and label provenance/terms are confirmed. The 147 points are spread over 20 mandals and 42 villages, class support is imbalanced, and two labels have only one/two points. TGRAC layer 18 is a 1,131,404-feature parcel classification layer, not a substitute command polygon. The 12 records tagged Wanaparthy do not fall within any of the seven inspected I&CAD polygons; if Wanaparthy is the required target, the team must identify a matching command and label source.

## Evidence status by criterion

| Criterion | Evidence now available | Status |
|---|---|---|
| Georeferenced crop labels | TGRAC Feb–Apr 2023 points plus locally acquired Zindi `train.csv` (7,888 WKT polygons, seven crop labels, four health categories). Zindi source CRS, polygon topology, label protocol, pixel/date match and TGRAC provenance/positional accuracy/date semantics remain unresolved | Partial |
| Candidate area overlap | Fresh TGRAC snapshots reproduce 264 intersections. Zindi and NWIC files are locally acquired, but their source CRSs are undeclared, so no cross-source spatial overlap is claimed. NWIC supports SRSP by project name and district metadata only. | Partial |
| Boundary authority / licence | TGRAC's [program page](https://tgrac.telangana.gov.in/trac/project-water.php) describes project-office maps and, where absent, interpretation using crop pattern/terrain/satellite/drainage, but does not tie provenance/version to I&CAD layers 9/10. The downloaded NWIC file lists Sriramsagar Stage-I with an area field that differs from TGRAC's; its CRS is undeclared and licence text is nonspecific (“Other (Open)”). | Partial |
| Crop-label reuse / quality | TGRAC has no explicit terms or survey QA. FAIR Forward describes the source as CC BY 4.0; the linked Zindi challenge rules permit challenge-copy use/share under CC-BY-SA 4.0; the GitHub repo declares no licence. Preserve both provenance statements, attribute and follow share-alike for the challenge copy; label protocol/quality still unverified. | Partial |
| Temporal suitability | Rabi 2023 layers; CreationDate not confirmed as observation time; imagery footprints historically found but not pixel-screened | Partial |
| Sentinel-1/2 actual data quality | Catalog-level products historically found; cloud, shadows, usable pixels and field-point match unverified | Partial |
| Weather/water-balance inputs | ERA5-Land is an available candidate collection; user project access and local soil/crop inputs are unverified | Partial |
| Independent stress/advisory validation | No measured moisture, irrigation quantity/timing or recommendation outcomes inspected | Blocked |

### NWIC independent-project inventory (2026-10-24)

The NWIC national `Command_Area_GeoJSON` file was acquired to Git-ignored audit storage and parsed as a 1,448-feature FeatureCollection. It includes 63 features whose state attribute is Telangana, including a feature named **“Sriramsagar Stage-I (Pochampad)”** with the listed beneficiary districts Nizamabad, Karimnagar, Warangal and Adilabad. This independently corroborates that SRSP Stage I is a named project candidate in the national project inventory. Its `area_ha` attribute is 880,121.94, compared with 433,249 in the inspected TGRAC SRSP Stage I polygon; the figures may refer to different boundary/area concepts and are not reconciled. The NWIC GeoJSON has no declared CRS, although its coordinates are projected metre-like values outside geographic longitude/latitude ranges. No cross-source geometry overlay or direct geometry-area calculation is valid until NWIC confirms the CRS and field meaning; the two area attributes are recorded only for review. Portal metadata says “Other (Open)” but provides no specific licence text in the inspected resource record. The GeoJSON is not yet an accepted command boundary and does not close DS-05/DS-09.

## Decision gate

Rank SRSP Stage I first for evidence follow-up. Do not designate it a verified AOI, create a final `config/study_area.geojson`, claim model readiness, or assert irrigation-advisory validity. Re-evaluate the shortlist when original data terms, survey documentation and official boundary evidence are available. Final AOI choice remains a project-owner/team decision under the existing approvals in `docs/DECISIONS.md` and `docs/TASK_ASSIGNMENTS.md`.

## Required evidence to close

1. Provider source lineage, observation date definition, positional accuracy, class dictionary and reuse terms for TGRAC points; Zindi source CRS, survey/label protocol and spatial/date suitability. Preserve FAIR Forward and Zindi provenance statements, attribute the challenge copy and comply with CC-BY-SA 4.0 share-alike conditions.
2. I&CAD/NWIC authority confirmation of the specific boundary's provenance, vintage, authoritative status, CRS, topology/area semantics and reuse terms. The NWIC feature now confirms a same-named SRSP project record but does not yet provide a usable CRS or a geometrically matched command boundary.
3. Clean reproducible source download and overlap report; inspect point distribution and class support by spatial groups.
4. Confirmed dates, pixel-level Sentinel quality, and a leakage-resistant spatial holdout.
5. Independent soil/root-zone moisture or defensible water-balance reference plus irrigation events/outcomes for advisory validation.
