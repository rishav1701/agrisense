import fs from "node:fs/promises";
import path from "node:path";
import { createRequire, Module } from "node:module";
import { fileURLToPath } from "node:url";

const nodeModules = "C:/Users/rishav raj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
process.env.NODE_PATH = nodeModules;
Module._initPaths();
const require = createRequire(import.meta.url);
const { SpreadsheetFile, Workbook } = require("@oai/artifact-tool");

const outDir = fileURLToPath(new URL("./", import.meta.url));
const root = path.resolve(outDir, "..", "..");
const auditDir = path.join(root, "data", "audits", "tgrac");

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (quoted && char === '"' && text[i + 1] === '"') {
      field += '"';
      i += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      row.push(field);
      field = "";
    } else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && text[i + 1] === "\n") i += 1;
      row.push(field);
      if (row.some((cell) => cell !== "")) rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (field !== "" || row.length) {
    row.push(field);
    rows.push(row);
  }
  const headers = (rows.shift() ?? []).map((header) => header.replace(/^\uFEFF/, ""));
  return rows.map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""])));
}

async function readCsv(name) {
  return parseCsv(await fs.readFile(path.join(auditDir, "derived", name), "utf8"));
}

const cropCounts = (await readCsv("crop_counts_by_month.csv")).map((row) => ({
  Month: row.month_layer.replace("_2023", "").replace(/^./, (letter) => letter.toUpperCase()),
  Crop: row.crop_label,
  "Count (points)": Number(row.count),
}));
const rawOverlap = await readCsv("overlap_by_source_project_month_crop.csv");
const overlapMap = new Map();
for (const row of rawOverlap) {
  const key = `${row.polygon_source}|${row.polygon_label}`;
  if (!overlapMap.has(key)) {
    overlapMap.set(key, {
      "Boundary source": row.polygon_source === "layer18_candidate" ? "Agriculture2 layer 18" : row.polygon_source === "icad_layer9" ? "I&CAD layer 9" : "I&CAD layer 10",
      "Candidate label": row.polygon_label,
      February: 0,
      March: 0,
      April: 0,
      Total: 0,
      "% of all monthly points": 0,
      "Authority verified?": "No",
    });
  }
  const item = overlapMap.get(key);
  const month = row.month_layer.replace("_2023", "");
  item[month[0].toUpperCase() + month.slice(1)] += Number(row.point_count || 0);
}
const overlap = [...overlapMap.values()].map((item) => {
  item.Total = item.February + item.March + item.April;
  item["% of all monthly points"] = item.Total / 2446;
  return item;
}).sort((a, b) => {
  const sourceOrder = { "I&CAD layer 9": 0, "I&CAD layer 10": 1, "Agriculture2 layer 18": 2 };
  return sourceOrder[a["Boundary source"]] - sourceOrder[b["Boundary source"]] || b.Total - a.Total || a["Candidate label"].localeCompare(b["Candidate label"]);
});

const inventory = [
  ["GT-TGRAC-2023", "TGRAC Agriculture2 Crop Analysis — Ground Truth Rabi 2023 (layers 10, 11, 12)", "https://tgrac.telangana.gov.in/arcgis/rest/services/Agri2/Agriculture2_CropAnalysis_Layers/MapServer", "Point / EPSG:4326", "Feb–Apr 2023; month-layer dates; field-observation date unconfirmed", "2,446 records. crop, cropvar, typeirrigation, stagecrop, conditioncrop, district/mandal/village, CreationDate", "Candidate crop-classification labels; not measured moisture stress or advisory outcomes", "No clear service licence; obtain custodian terms and attribution", "Retrieved; use rights and quality open", "Complete source JSON: data/audits/tgrac/data/february_2023.json; march_2023.json; april_2023.json. Crop labels and date semantics need provider validation."],
  ["GT-WRMS-ADEX-2022-24", "WRMS ground truth via Telangana ADeX / FAIR Forward; public Zindi mirror", "https://dataexplorer.ts.adex.org.in/dataset/583e8f01-160e-4f51-bde5-31dc7f2a5887; mirror: https://github.com/pranavmyname/zindi_crop_health", "7,888 WKT polygons; source CRS undeclared; no coordinate inference", "Catalogue reports crop cycles 2022–2024", "7,888 rows/20 columns; no nulls/duplicate FarmIDs; categories, crops and seasons in docs/data_audit/crop_catalogue_and_labels.md", "Candidate crop-health labels; not measured moisture stress", "FAIR describes CC BY 4.0; linked Zindi rules permit challenge-data use/share under CC-BY-SA 4.0; preserve attribution/share-alike", "CSV saved under ignored data/audits/external/; SHA-256 recorded in source inventory", "Basic exterior-ring closure/length checks pass; CRS, topology, label protocol, AOI overlap and pixel/date matching remain unresolved. ADeX ID returns 404."],
  ["GT-TG-RABI-2016-19", "DataSuds Telangana Rabi field-survey vectors", "https://doi.org/10.23708/dab0b558-ef5f-4df1-ba7c-714dff15b6ec", "Article describes field polygons; actual file CRS and extent unverified", "March surveys, 2016–2019", "Article describes rice and other crop/land-cover labels; class provenance varies", "Historical crop classification reference if coordinates, source classes and overlap pass inspection", "Data-record licence not verified; article licence is not assumed to cover data", "Candidate; record URL redirected to IRD maintenance page on 2026-10-24", "No original vector file acquired; actual spatial overlap unknown."],
  ["GT-TG-RICE-RASTERS-2016-19", "DataSuds seasonal rice-frequency rasters", "https://doi.org/10.23708/1f7bb3d2-4223-4e1d-a39d-7e432bcbbb34", "Article describes 10 m GeoTIFF; actual CRS/grid unverified", "Rabi 2016–2019", "Values described as number of eight RF runs mapping rice (0–8)", "Rice extent context only; derived product, not independent field labels or stress ground truth", "Data-record licence not verified", "Candidate; record URL redirected to IRD maintenance page on 2026-10-24", "No original raster acquired; associated article: https://pmc.ncbi.nlm.nih.gov/articles/PMC12396292/"],
  ["IRR-TGRAC-L18", "TGRAC Agriculture2 Crop Analysis — Irrigation Projects layer 18", "https://tgrac.telangana.gov.in/arcgis/rest/services/Agri2/Agriculture2_CropAnalysis_Layers/MapServer/18", "Polygon / EPSG:4326", "Layer version/date not established", "Service total 1,131,404; 10 local parcel polygons returned around ground-truth points; cadastral/irrigation hierarchy fields", "Parcel-context join only; not a verified command boundary", "No clear service licence found", "Retrieved point-filtered subset; not AOI boundary", "Fresh spatial summary finds 12 point-to-parcel matches in February; 10 selected parcels are stored in ignored audit data."],
  ["IRR-TGRAC-ICAD-L9-10", "TGRAC I&CAD Command_Boundary layers 9 and 10", "https://tgrac.telangana.gov.in/arcgis/rest/services/IandCAD_Folder/I_and_CAD/MapServer", "Polygon / EPSG:4326", "Layer vintage/date not established", "Seven named polygons per layer; layer 9 and 10 geometries are coordinate-identical", "Candidate command overlap screening; authority and topology need confirmation", "No clear service licence found", "Retrieved candidate geometries; authority/reuse unresolved", "Fresh overlap: 264 point intersections; SRSP Stage I leads with 147. No AOI selected."],
  ["IRR-CWC-NWIC", "CWC / NWIC national Command_Area_GeoJSON", "https://nwdp.nwic.gov.in/en/dataset/water-resource-project/resource/7b1e0abf-ca24-46d2-b0dc-7234021e414d", "GeoJSON; projected coordinate values but source CRS not declared", "Resource last updated 2025-11-17", "1,448 features, including 63 Telangana; named Sriramsagar Stage-I (Pochampad), beneficiary districts Nizamabad/Karimnagar/Warangal/Adilabad; area_ha 880,121.94", "Independent project-name corroboration; not a geometrically verified boundary", "Portal says Other (Open) without specific licence text; obtain terms/attribution", "Full file locally parsed in ignored audit storage", "NWIC area differs from TGRAC 433,249 Ayacut_ha; meanings unreconciled. No CRS means no overlay or AOI selection."],
  ["IMG-GEE-S1-S2-ERA5", "Sentinel-1, Sentinel-2 and ERA5-Land via Google Earth Engine", "https://developers.google.com/earth-engine/datasets", "Collections are gridded imagery/reanalysis; region/grid must be verified", "Date ranges depend on approved study period", "S1/S2 image bands; ERA5-Land meteorological variables", "Candidate feature/weather inputs; catalog access is not evidence of usable AOI pixels", "Check each catalog collection's attribution and terms", "Not authenticated; local EE API and CLI absent", "Complete steps and a three-collection verification script are in docs/GEE_SETUP.md."],
];

const actions = [
  ["T-P1-SH-001", "Member C — Ashwanth C", "Create the project Python environment and pin dependencies; configure pytest, Ruff, Black and isort.", "Open", "Repo currently has no requirements/pyproject/environment manifest and no tools installed.", "Clean environment setup and project checks pass."],
  ["T-P1-DE-001", "Member A — Peter", "Install Earth Engine API in the approved environment; configure a registered Cloud Project and authenticate locally.", "Open", "No gcloud, Earth Engine CLI or earthengine-api is present; no private account was accessed.", "All three collection probes in docs/GEE_SETUP.md succeed."],
  ["DS-04 / TGRAC", "Project owner + data custodian", "Obtain survey lineage/protocol, field-observation date semantics, point positional quality, crop/condition dictionaries and reuse/redistribution terms.", "Open", "TGRAC candidate points retrieved; service terms and survey QA are absent from inspected metadata.", "Written source response or authoritative metadata, with terms recorded."],
  ["DS-05 / boundary", "Member A + irrigation authority", "Confirm I&CAD layer/version provenance, topology and terms; obtain the NWIC CRS, feature semantics and reuse terms, then verify any matched boundary.", "Open", "NWIC includes same-named Sriramsagar Stage-I project but declares no CRS; its area_ha differs from TGRAC Ayacut_ha and “Other (Open)” is nonspecific.", "Authoritative boundary/version, CRS, area semantics and applicable reuse terms documented."],
  ["DS-09 / AOI", "Project owner + all three members", "Review ranked evidence and select or defer the pilot; decide whether SRSP Stage I or Wanaparthy focus matches project intent.", "Open", "SRSP has the largest overlap (147); 12 Wanaparthy-tagged points miss the seven queried commands.", "AOI/study period and required team approvals recorded; do not call SRSP verified yet."],
  ["Alternative labels", "Member B + WRMS/Zindi", "Obtain CRS and survey/label protocol; assess pixel/date matching and spatial validation feasibility; confirm intended project use follows CC-BY-SA attribution/share-alike.", "Open", "Full CSV acquired and counted (SHA-256 recorded); ADeX returns 404; CRS, topology and label protocol remain unverified.", "Source metadata/protocol and CRS documented, with accepted spatial/date design and reuse conditions."],
  ["DS-06 / DS-07", "Member B + Member A", "Review ICAR Telangana Kharif advisory and generic FAO-56 Kc table against approved target crops/season; identify a suitable Rabi calendar and any local Kc calibration.", "Open", "Initial references identified; ICAR is not a pilot-specific Rabi calendar and FAO-56 values are generic.", "Crop/season-appropriate calendar and supported Kc inputs selected under the member review process."],
  ["Stress / advisory validation", "Project team + field partners", "Obtain independent soil/root-zone moisture reference, irrigation event date/quantity and recommendation outcomes, or narrow the validated claim.", "Open", "No inspected source provides those independent target observations.", "Traceable validation source and accepted methodology documented."],
  ["Proposed conventions / contracts", "All three members", "Review processing conventions and module interface proposal; resolve open choices without changing approved contracts unilaterally.", "Open", "Documents are proposals, not shared approval or implemented code.", "Member review recorded; shared contract changes follow unanimous rules."],
];

const wb = Workbook.create();
const summary = wb.worksheets.add("Overview");
const inventorySheet = wb.worksheets.add("Dataset Inventory");
const cropSheet = wb.worksheets.add("Crop Counts");
const overlapSheet = wb.worksheets.add("Spatial Overlap");
const actionSheet = wb.worksheets.add("Next Actions");
for (const sheet of [summary, inventorySheet, cropSheet, overlapSheet, actionSheet]) sheet.showGridLines = false;

const navy = "#163A52";
const blue = "#DCEAF2";
const amber = "#FFF2CC";
const lightGray = "#F2F5F7";
const white = "#FFFFFF";
const dark = "#21313C";

// Summary / decision view
summary.getRange("A1:J1").values = [["AgriSense — Data & AOI Readiness", null, null, null, null, null, null, null, null, null]];
summary.getRange("A1:J1").format.font = { name: "Arial", size: 15, bold: true, color: navy };
summary.getRange("A2:J2").values = [["Evidence checkpoint: 24 Oct 2026 | Zindi CSV and NWIC project inventory locally audited; CRS, label permissions, AOI authority and advisory validation remain open.", null, null, null, null, null, null, null, null, null]];
summary.getRange("A2:J2").format.font = { name: "Arial", size: 10, italic: true, color: dark };
summary.getRange("A2:J2").format.wrapText = false;
summary.getRange("A4:B4").values = [["Readiness indicator", "Verified value"]];
summary.getRange("A4:B4").format = { fill: navy, font: { name: "Arial", size: 10, bold: true, color: white }, horizontalAlignment: "center", verticalAlignment: "center" };
summary.getRange("A5:A8").values = [["TGRAC crop points downloaded"], ["I&CAD layer 9 candidate intersections"], ["Dataset candidates inventoried"], ["Open prerequisite actions"]];
summary.getRange("B5:B8").formulas = [
  [`=SUM('Crop Counts'!C2:C${cropCounts.length + 1})`],
  [`=SUMIF('Spatial Overlap'!A2:A${overlap.length + 1},"I&CAD layer 9",'Spatial Overlap'!F2:F${overlap.length + 1})`],
  [`=COUNTA('Dataset Inventory'!A2:A${inventory.length + 1})`],
  [`=COUNTIF('Next Actions'!D2:D${actions.length + 1},"Open")`],
];
summary.getRange("A5:B8").format.borders = { preset: "inside", style: "thin", color: "#D9E1E6" };
summary.getRange("B5:B8").format.numberFormat = "#,##0";
summary.getRange("B5:B8").format.font = { name: "Arial", size: 11, bold: true, color: navy };
summary.getRange("A10:F10").values = [["AOI evidence ranking", "Feb points", "Mar points", "Apr points", "Total", "Decision state"]];
summary.getRange("A10:F10").format = { fill: navy, font: { name: "Arial", size: 10, bold: true, color: white }, horizontalAlignment: "center", verticalAlignment: "center" };
const iCAD9 = overlap.filter((row) => row["Boundary source"] === "I&CAD layer 9").sort((a, b) => b.Total - a.Total);
summary.getRange(`A11:F${10 + iCAD9.length}`).values = iCAD9.map((row) => [row["Candidate label"], row.February, row.March, row.April, row.Total, row.Total === 147 ? "Lead for review only" : "Candidate only"]);
summary.getRange(`B11:E${10 + iCAD9.length}`).format.numberFormat = "#,##0";
summary.getRange(`A11:F${10 + iCAD9.length}`).format.borders = { preset: "inside", style: "thin", color: "#D9E1E6" };
summary.getRange("A20:J20").values = [["Readiness decision", null, null, null, null, null, null, null, null, null]];
summary.getRange("A20:J20").format = { fill: blue, font: { name: "Arial", size: 10, bold: true, color: navy } };
summary.getRange("A21:J24").values = [
  ["SRSP Stage I ranks first by current point overlap (147), but it is not a selected or verified AOI. Boundary source authority, vintage, terms and ground-truth quality still need verification.", null, null, null, null, null, null, null, null, null],
  ["Layer 18 is a 1,131,404-parcel cadastral dataset. Only 10 parcels around the source points were retrieved; it is not a command boundary.", null, null, null, null, null, null, null, null, null],
  ["NWIC independently lists Sriramsagar Stage-I (Pochampad), but its GeoJSON has no CRS declaration and its area field differs from TGRAC; no spatial match is established.", null, null, null, null, null, null, null, null, null],
  ["The Zindi CSV is saved and counted, but its CRS/topology/label protocol remain open. No source validates measured moisture stress or irrigation-advisory outcomes.", null, null, null, null, null, null, null, null, null],
];
summary.getRange("A21:J24").format.wrapText = false;
summary.getRange("A21:J24").format.rowHeight = 33;
summary.getRange("A21:J24").format.font = { name: "Arial", size: 9, color: dark };
summary.getRange("A25:F25").values = [["Immediate inputs required", null, null, null, null, null]];
summary.getRange("A25:F25").format = { fill: amber, font: { name: "Arial", size: 10, bold: true, color: dark } };
summary.getRange("A26:F31").values = [
  ["1. Team/owner: confirm target geography and record AOI/study-period approval." , null, null, null, null, null],
  ["2. Providers: obtain TGRAC survey/reuse details and I&CAD/NWIC boundary authority, CRS and applicable reuse terms." , null, null, null, null, null],
  ["3. Member B + WRMS/Zindi: obtain crop-health file CRS and label protocol; assess spatial/date fit and follow CC-BY-SA attribution/share-alike." , null, null, null, null, null],
  ["4. Member B + Member A: review ICAR calendar and generic FAO-56 Kc references against selected crops/season." , null, null, null, null, null],
  ["5. Member A: configure Earth Engine project locally; never share credentials." , null, null, null, null, null],
  ["6. Team/field partners: supply independent moisture and irrigation-event/outcome evidence, or narrow the scientific claim." , null, null, null, null, null],
];
summary.getRange("A26:F31").format.wrapText = false;
summary.getRange("A26:F31").format.rowHeight = 30;
summary.getRange("A1:J30").format.font = { name: "Arial", size: 10, color: dark };
summary.getRange("A1:J1").format.font = { name: "Arial", size: 15, bold: true, color: navy };
summary.getRange("A4:B4").format.font = { name: "Arial", size: 10, bold: true, color: white };
summary.getRange("A10:F10").format.font = { name: "Arial", size: 10, bold: true, color: white };
summary.getRange("A20:J20").format.font = { name: "Arial", size: 10, bold: true, color: navy };
summary.getRange("A25:F25").format.font = { name: "Arial", size: 10, bold: true, color: dark };
summary.getRange("A1:J29").format.verticalAlignment = "center";
summary.getRange("A1:A29").format.columnWidth = 42;
summary.getRange("B1:B29").format.columnWidth = 18;
summary.getRange("C1:F29").format.columnWidth = 22;
summary.getRange("G1:J29").format.columnWidth = 14;
summary.getRange("A11:F17").format.wrapText = true;
summary.getRange("F11:F17").format.fill = amber;

// Candidate source inventory
const inventoryHeaders = ["ID", "Dataset / source", "Source URL", "Geometry / CRS", "Dates / season", "Known attributes / evidence", "Potential use", "Licence / reuse", "Status", "Evidence / caveat"];
inventorySheet.getRangeByIndexes(0, 0, 1, inventoryHeaders.length).values = [inventoryHeaders];
inventorySheet.getRangeByIndexes(1, 0, inventory.length, inventoryHeaders.length).values = inventory;
inventorySheet.tables.add(`A1:J${inventory.length + 1}`, true, "DatasetInventory");
inventorySheet.getRange(`A1:J1`).format = { fill: navy, font: { name: "Arial", size: 10, bold: true, color: white }, horizontalAlignment: "center", verticalAlignment: "center", wrapText: true };
inventorySheet.getRange(`A2:J${inventory.length + 1}`).format.font = { name: "Arial", size: 9, color: dark };
inventorySheet.getRange(`A2:J${inventory.length + 1}`).format.wrapText = true;
inventorySheet.getRange(`A2:J${inventory.length + 1}`).format.verticalAlignment = "center";
inventorySheet.getRange(`A2:J${inventory.length + 1}`).format.rowHeight = 78;
for (const [col, width] of [["A", 24], ["B", 40], ["C", 55], ["D", 32], ["E", 40], ["F", 54], ["G", 48], ["H", 48], ["I", 38], ["J", 68]]) inventorySheet.getRange(`${col}1:${col}${inventory.length + 1}`).format.columnWidth = width;
inventorySheet.freezePanes.freezeRows(1);

// Crop counts by month, retained as typed records
cropSheet.getRange("A1:C1").values = [["Month", "Crop label (source field)", "Count (points)"]];
cropSheet.getRangeByIndexes(1, 0, cropCounts.length, 3).values = cropCounts.map((row) => [row.Month, row.Crop, row["Count (points)"]]);
cropSheet.tables.add(`A1:C${cropCounts.length + 1}`, true, "CropCounts");
cropSheet.getRange("A1:C1").format = { fill: navy, font: { name: "Arial", size: 10, bold: true, color: white }, horizontalAlignment: "center", verticalAlignment: "center" };
cropSheet.getRange(`A2:C${cropCounts.length + 1}`).format.font = { name: "Arial", size: 10, color: dark };
cropSheet.getRange(`C2:C${cropCounts.length + 1}`).format.numberFormat = "#,##0";
cropSheet.getRange("A1:A100").format.columnWidth = 20;
cropSheet.getRange("B1:B100").format.columnWidth = 30;
cropSheet.getRange("C1:C100").format.columnWidth = 20;
cropSheet.freezePanes.freezeRows(1);

// Candidate spatial overlaps aggregated from crop-specific source calculations
const overlapHeaders = Object.keys(overlap[0]);
overlapSheet.getRangeByIndexes(0, 0, 1, overlapHeaders.length).values = [overlapHeaders];
overlapSheet.getRangeByIndexes(1, 0, overlap.length, overlapHeaders.length).values = overlap.map((row) => overlapHeaders.map((header) => row[header]));
overlapSheet.tables.add(`A1:H${overlap.length + 1}`, true, "SpatialOverlap");
overlapSheet.getRange(`A1:H1`).format = { fill: navy, font: { name: "Arial", size: 10, bold: true, color: white }, horizontalAlignment: "center", verticalAlignment: "center", wrapText: true };
overlapSheet.getRange(`A2:H${overlap.length + 1}`).format.font = { name: "Arial", size: 9, color: dark };
overlapSheet.getRange(`B2:H${overlap.length + 1}`).format.wrapText = true;
overlapSheet.getRange(`C2:F${overlap.length + 1}`).format.numberFormat = "#,##0";
overlapSheet.getRange(`G2:G${overlap.length + 1}`).format.numberFormat = "0.0%";
overlapSheet.getRange(`H2:H${overlap.length + 1}`).format.fill = amber;
overlapSheet.getRange(`A2:H${overlap.length + 1}`).format.rowHeight = 30;
for (const [col, width] of [["A", 28], ["B", 45], ["C", 14], ["D", 14], ["E", 14], ["F", 14], ["G", 23], ["H", 23]]) overlapSheet.getRange(`${col}1:${col}${overlap.length + 1}`).format.columnWidth = width;
overlapSheet.freezePanes.freezeRows(1);

// Action tracker; all statuses remain open until evidence/approval is supplied
const actionHeaders = ["Task / gate", "Owner / provider", "Required action", "Status", "Current blocker / evidence", "Close condition"];
actionSheet.getRangeByIndexes(0, 0, 1, actionHeaders.length).values = [actionHeaders];
actionSheet.getRangeByIndexes(1, 0, actions.length, actionHeaders.length).values = actions;
actionSheet.tables.add(`A1:F${actions.length + 1}`, true, "PrerequisiteActions");
actionSheet.getRange(`A1:F1`).format = { fill: navy, font: { name: "Arial", size: 10, bold: true, color: white }, horizontalAlignment: "center", verticalAlignment: "center", wrapText: true };
actionSheet.getRange(`A2:F${actions.length + 1}`).format.font = { name: "Arial", size: 9, color: dark };
actionSheet.getRange(`A2:F${actions.length + 1}`).format.wrapText = true;
actionSheet.getRange(`A2:F${actions.length + 1}`).format.verticalAlignment = "center";
actionSheet.getRange(`A2:F${actions.length + 1}`).format.rowHeight = 54;
actionSheet.getRange(`D2:D${actions.length + 1}`).format.fill = amber;
actionSheet.getRange(`D2:D${actions.length + 1}`).dataValidation = { rule: { type: "list", values: ["Open", "In Progress", "Complete"] } };
for (const [col, width] of [["A", 24], ["B", 32], ["C", 70], ["D", 18], ["E", 72], ["F", 62]]) actionSheet.getRange(`${col}1:${col}${actions.length + 1}`).format.columnWidth = width;
actionSheet.freezePanes.freezeRows(1);

wb.recalculate();
const summaryCheck = await wb.inspect({ kind: "region", sheetId: "Overview", range: "A4:F17", maxChars: 5000 });
const errorCheck = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 100 }, summary: "inventory formula error scan" });
if (/#(?:REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|NULL!|SPILL!|CALC!)/.test(errorCheck.ndjson)) {
  throw new Error(`Formula error detected: ${errorCheck.ndjson}`);
}
const previews = [];
for (const sheetName of ["Overview", "Dataset Inventory", "Crop Counts", "Spatial Overlap", "Next Actions"]) {
  const preview = await wb.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(path.join(outDir, `${sheetName.replaceAll(" ", "_")}.png`), new Uint8Array(await preview.arrayBuffer()));
  previews.push(sheetName);
}
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(outDir, "AgriSense_Data_AOI_Inventory.xlsx"));
const verify = await wb.inspect({ kind: "workbook,sheet,table", maxChars: 5000, tableMaxRows: 4, tableMaxCols: 8 });
console.log(JSON.stringify({ output: path.join(outDir, "AgriSense_Data_AOI_Inventory.xlsx"), summary: summaryCheck.ndjson, formulaErrors: errorCheck.ndjson, sheetsRendered: previews, workbook: verify.ndjson }, null, 2));
