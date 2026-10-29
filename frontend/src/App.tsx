import { useEffect, useMemo, useState } from "react";

type Geometry = {
  type: "Polygon" | "MultiPolygon";
  coordinates: number[][][] | number[][][][];
};

type ValidationResult = {
  query_id: string;
  valid: boolean;
  message: string;
  accepted_for_acquisition: boolean;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isPosition(value: unknown): value is number[] {
  return (
    Array.isArray(value) &&
    value.length >= 2 &&
    value.every((coordinate) => typeof coordinate === "number" && Number.isFinite(coordinate)) &&
    value[0] >= -180 && value[0] <= 180 &&
    value[1] >= -90 && value[1] <= 90
  );
}

function isRing(value: unknown): value is number[][] {
  return (
    Array.isArray(value) &&
    value.length >= 4 &&
    value.every(isPosition) &&
    value[0].length === value[value.length - 1].length &&
    value[0].every((coordinate, index) => coordinate === value[value.length - 1][index])
  );
}

function isPolygonCoordinates(value: unknown): value is number[][][] {
  return Array.isArray(value) && value.length > 0 && value.every(isRing);
}

function parseGeometry(value: unknown): Geometry {
  if (!isRecord(value) || !Array.isArray(value.coordinates)) {
    throw new Error("Choose a GeoJSON Polygon or MultiPolygon with coordinates.");
  }
  if (value.type === "Polygon" && isPolygonCoordinates(value.coordinates)) {
    return value as Geometry;
  }
  if (
    value.type === "MultiPolygon" &&
    value.coordinates.length > 0 &&
    value.coordinates.every(isPolygonCoordinates)
  ) {
    return value as Geometry;
  }
  throw new Error("The boundary must contain closed Polygon or MultiPolygon rings in longitude/latitude order.");
}

function parseBoundaryDocument(value: unknown): Geometry {
  if (!isRecord(value)) throw new Error("Choose a valid GeoJSON boundary file.");
  if (value.type === "FeatureCollection") {
    if (!Array.isArray(value.features) || value.features.length !== 1) {
      throw new Error("Choose a FeatureCollection containing exactly one boundary feature.");
    }
    value = value.features[0];
  }
  if (isRecord(value) && value.type === "Feature") {
    if (!value.geometry) throw new Error("The GeoJSON feature has no geometry.");
    return parseGeometry(value.geometry);
  }
  return parseGeometry(value);
}

function getPositions(geometry: Geometry): number[][] {
  const polygons = geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates;
  return (polygons as number[][][][]).flat(2);
}

function geometryPath(geometry: Geometry): string {
  const positions = getPositions(geometry);
  const longitudes = positions.map((point) => point[0]);
  const latitudes = positions.map((point) => point[1]);
  const minX = Math.min(...longitudes);
  const maxX = Math.max(...longitudes);
  const minY = Math.min(...latitudes);
  const maxY = Math.max(...latitudes);
  const spanX = Math.max(maxX - minX, 0.0001);
  const spanY = Math.max(maxY - minY, 0.0001);
  const project = (point: number[]) => {
    const x = 30 + ((point[0] - minX) / spanX) * 340;
    const y = 210 - ((point[1] - minY) / spanY) * 180;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  };
  const polygons = geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates;
  return (polygons as number[][][][])
    .map((polygon) =>
      polygon
        .map((ring) => `${ring.map(project).join(" ")} Z`)
        .join(" "),
    )
    .join(" ");
}

function App() {
  const [active, setActive] = useState("Overview");
  const [geometry, setGeometry] = useState<Geometry | null>(null);
  const [areaName, setAreaName] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [noticeVisible, setNoticeVisible] = useState(true);
  const path = useMemo(() => (geometry ? geometryPath(geometry) : ""), [geometry]);

  useEffect(() => {
    void checkApi();
  }, []);

  async function checkApi() {
    try {
      const response = await fetch(`${API_BASE}/api/health`);
      setApiOnline(response.ok);
    } catch {
      setApiOnline(false);
    }
  }

  async function handleFile(file?: File) {
    setError("");
    setMessage("");
    if (!file) return;
    try {
      const candidate = parseBoundaryDocument(JSON.parse(await file.text()) as unknown);
      setGeometry(candidate);
      setAreaName(file.name.replace(/\.geojson$|\.json$/i, ""));
    } catch (caught) {
      setGeometry(null);
      setError(caught instanceof Error ? caught.message : "Could not read this GeoJSON file.");
    }
  }

  async function validateRequest() {
    setError("");
    setMessage("");
    if (!geometry || !startDate || !endDate) {
      setError("Add a Polygon/MultiPolygon GeoJSON and choose a complete date interval.");
      return;
    }
    if (startDate >= endDate) {
      setError("The end date must be later than the start date.");
      return;
    }
    setBusy(true);
    try {
      const response = await fetch(`${API_BASE}/api/study-area/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ aoi_geometry: geometry, start_date: startDate, end_date: endDate }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "The API rejected this request.");
      const result = body as ValidationResult;
      setMessage(`${result.message} Request ${result.query_id}.`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not reach the AgriSense API.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview" onClick={() => setActive("Overview")}>
          <span className="brand-mark"><LeafIcon /></span>
          <span><strong>AgriSense</strong><small>FIELD INTELLIGENCE</small></span>
        </a>
        <div className="workspace-switch"><span className="workspace-dot">A</span><span><b>Research workspace</b><small>Academic project</small></span><span className="chevron">⌄</span></div>
        <div className="nav-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {["Overview", "Field setup", "Observations", "Crop insights", "Water balance"].map((item, index) => (
            <button className={`nav-item ${active === item ? "selected" : ""}`} key={item} onClick={() => setActive(item)}>
              <span className="nav-icon">{[<GridIcon />, <PinIcon />, <SatelliteIcon />, <SproutIcon />, <DropIcon />][index]}</span>
              {item}
              {index > 1 && <span className="nav-lock">·</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="data-status"><span className="status-pulse" /><div><b>Data connections</b><small>{apiOnline === null ? "Checking local API" : apiOnline ? "API online · sources not connected" : "API offline"}</small></div><span className="more">···</span></div>
          <button className="profile"><span className="avatar">RR</span><span><b>Research team</b><small>Local environment</small></span><span className="chevron">⌄</span></button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> <b>{active}</b></div>
          <div className="top-actions"><span className="environment"><i /> DEVELOPMENT</span><button className="icon-button" aria-label="Check API status" onClick={checkApi}><RefreshIcon /></button><button className="help-button">Help <span>↗</span></button></div>
        </header>

        <div className="page-wrap">
          <section className="welcome-row">
            <div><div className="eyebrow"><span className="eyebrow-line" /> CROP MONITORING PLATFORM</div><h1>{active === "Overview" ? "Field intelligence,\nwith evidence." : active}</h1><p>Explore satellite observations and crop conditions for your study area.</p></div>
            <button className="primary-button" onClick={() => setActive("Field setup")}><span>＋</span> Configure study area</button>
          </section>

          {noticeVisible && <section className="notice" role="status"><span className="notice-icon">i</span><div><b>Research workspace is being configured</b><p>No pilot area or live data sources are connected yet. Add a GeoJSON boundary to preview and validate a study request.</p></div><button className="notice-close" aria-label="Dismiss notice" onClick={() => setNoticeVisible(false)}>×</button></section>}

          <section className="metrics-grid" aria-label="Project readiness">
            <article className="metric-card"><div className="metric-top"><span>STUDY AREAS</span><span className="metric-glyph pale-green"><PinIcon /></span></div><div className="metric-value">—</div><div className="metric-caption"><span className="tiny-dot gray" />No verified area selected</div></article>
            <article className="metric-card"><div className="metric-top"><span>OBSERVATIONS</span><span className="metric-glyph pale-blue"><SatelliteIcon /></span></div><div className="metric-value">—</div><div className="metric-caption"><span className="tiny-dot gray" />No source data connected</div></article>
            <article className="metric-card"><div className="metric-top"><span>CROP ESTIMATES</span><span className="metric-glyph pale-gold"><SproutIcon /></span></div><div className="metric-value">—</div><div className="metric-caption"><span className="tiny-dot gray" />No model outputs available</div></article>
            <article className="metric-card"><div className="metric-top"><span>WATER BALANCE</span><span className="metric-glyph pale-aqua"><DropIcon /></span></div><div className="metric-value">—</div><div className="metric-caption"><span className="tiny-dot gray" />Inputs and method not configured</div></article>
          </section>

          <section className="content-grid">
            <article className="panel map-panel">
              <div className="panel-heading"><div><div className="section-kicker">STUDY AREA</div><h2>Spatial workspace</h2></div><button className="subtle-button" onClick={() => setActive("Field setup")}>Set up area <span>→</span></button></div>
              <div className={`map-canvas ${geometry ? "has-geometry" : ""}`}>
                <div className="map-grid" />
                <div className="map-controls"><button aria-label="Zoom in">＋</button><button aria-label="Zoom out">−</button><button aria-label="Reset view">⌖</button></div>
                {geometry ? <svg className="aoi-preview" viewBox="0 0 400 240" role="img" aria-label="Uploaded AOI geometry preview"><path d={path} /></svg> : <div className="map-empty"><span className="map-empty-icon"><MapIcon /></span><b>Your study area will appear here</b><span>Upload a GeoJSON boundary to preview its shape</span><button className="map-upload" onClick={() => setActive("Field setup")}>Add boundary <span>→</span></button></div>}
                <div className="map-attribution">AOI preview only · EPSG:4326 coordinates</div>
              </div>
              <div className="map-footer"><span><i className="legend-aoi" />Study boundary</span><span className="map-footer-note">No basemap or satellite layer loaded</span></div>
            </article>

            <article className="panel setup-panel">
              <div className="panel-heading"><div><div className="section-kicker">GET STARTED</div><h2>Set up a study</h2></div><span className="step-badge">01 / 03</span></div>
              <label className="field-label">Study area boundary</label>
              <label className="upload-box" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); void handleFile(event.dataTransfer.files[0]); }}>
                <input type="file" accept=".geojson,.json,application/geo+json,application/json" onChange={(event) => void handleFile(event.target.files?.[0])} />
                <span className="upload-icon"><UploadIcon /></span><span><b>{areaName || "Choose a GeoJSON file"}</b><small>{geometry ? "Boundary loaded for local preview" : "Polygon or MultiPolygon · EPSG:4326"}</small></span><span className="browse-label">Browse</span>
              </label>
              <div className="date-row"><label><span className="field-label">Start date</span><input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></label><label><span className="field-label">End date <small>(exclusive)</small></span><input type="date" value={endDate} min={startDate || undefined} onChange={(event) => setEndDate(event.target.value)} /></label></div>
              {error && <div className="form-message error" role="alert">{error}</div>}
              {message && <div className="form-message success" role="status">{message}</div>}
              <button className="submit-button" disabled={busy} onClick={() => void validateRequest()}>{busy ? "Validating…" : "Validate study request"}<span>→</span></button>
              <p className="form-footnote">Validation checks request structure only. It does not acquire data or approve the selected area.</p>
            </article>
          </section>

          <section className="bottom-grid">
            <article className="panel source-panel"><div className="panel-heading"><div><div className="section-kicker">PIPELINE STATUS</div><h2>Data sources</h2></div><button className="text-link" onClick={checkApi}>Refresh <RefreshIcon /></button></div><div className="source-list">{[["Sentinel-2", "Optical imagery", "SatelliteIcon"], ["Sentinel-1", "Radar observations", "RadarIcon"], ["ERA5-Land", "Weather reanalysis", "CloudIcon"]].map(([name, detail, icon]) => <div className="source-row" key={name}><span className="source-symbol">{icon === "SatelliteIcon" ? <SatelliteIcon /> : icon === "RadarIcon" ? <RadarIcon /> : <CloudIcon />}</span><span className="source-name"><b>{name}</b><small>{detail}</small></span><span className="source-pill"><i />Not connected</span><span className="row-chevron">›</span></div>)}</div></article>
            <article className="panel outputs-panel"><div className="panel-heading"><div><div className="section-kicker">ANALYSIS</div><h2>Latest insights</h2></div><span className="empty-badge">No outputs</span></div><div className="outputs-empty"><span className="insight-icon"><ChartIcon /></span><b>Insights will show up here</b><p>Connect source data and complete a study setup before analysis products are available.</p></div></article>
          </section>

          <footer className="page-footer"><span>AgriSense <span>·</span> Research preview</span><span>Estimates require traceable data and documented methods</span></footer>
        </div>
      </main>
    </div>
  );
}

function LeafIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19.7 3.2C11.1 3.3 5.2 5.5 4.1 11.2c-.7 3.5 1.5 5.9 4.5 5.6 5.8-.5 8.8-6.1 11.1-13.6ZM3 21c2.2-5.2 6.2-8.7 11.8-11.7" /></svg>; }
function GridIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/></svg>; }
function PinIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></svg>; }
function SatelliteIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8.2 9.3 6.5 6.5M10 7.5l-3.6-3.6-3.2 3.2 3.6 3.6m5.7 5.7 3.6 3.6 3.2-3.2-3.6-3.6M14 10a5.7 5.7 0 0 1 0-8m3 11a10 10 0 0 0 0-14M10 14a5.7 5.7 0 0 1 0 8M7 11a10 10 0 0 0 0 14"/></svg>; }
function SproutIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21v-9m0 4c-4.8 0-7-2.2-7-7 4.8 0 7 2.2 7 7Zm0-5c0-4.8 2.2-7 7-7 0 4.8-2.2 7-7 7Z"/></svg>; }
function DropIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3s7 7.2 7 12a7 7 0 0 1-14 0c0-4.8 7-12 7-12Z"/><path d="M9 16a3 3 0 0 0 3 3"/></svg>; }
function MapIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z"/><path d="M9 3v15m6-12v15"/></svg>; }
function UploadIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 16V4m-4 4 4-4 4 4M4 15v5h16v-5"/></svg>; }
function RefreshIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 7v5h-5M4 17v-5h5"/><path d="M6.1 9A7 7 0 0 1 18 6l2 6M4 12l2 6a7 7 0 0 0 11.9-3"/></svg>; }
function RadarIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 12 20 4M12 3v2m9 7h-2m-7 9v-2m-9-7h2"/><path d="M12 12h.01M5.6 5.6a9 9 0 1 0 12.8 0"/></svg>; }
function CloudIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 18h10a4 4 0 0 0 .5-8A6 6 0 0 0 6 9a4.5 4.5 0 0 0 1 9Z"/><path d="m9 21 1-2m4 2 1-2"/></svg>; }
function ChartIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19V5m0 14h16M7 15l4-4 3 2 5-6"/><circle cx="7" cy="15" r="1"/><circle cx="11" cy="11" r="1"/><circle cx="14" cy="13" r="1"/><circle cx="19" cy="7" r="1"/></svg>; }

export default App;
