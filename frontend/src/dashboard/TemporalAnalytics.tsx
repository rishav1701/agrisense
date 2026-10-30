import {
  buildChartModel,
  serializeTemporalCsv,
  validateTemporalView,
} from "./temporalAnalyticsData.mjs";
import type {
  TemporalAnalyticsView,
  TemporalSeries,
} from "./temporalAnalyticsData.mjs";

type Props = {
  view: TemporalAnalyticsView | null;
  loading?: boolean;
  error?: string | null;
};

const CHART_WIDTH = 760;
const CHART_HEIGHT = 220;
const X_PADDING = 36;
const Y_PADDING = 14;

function formatTick(value: number): string {
  return Number(value.toPrecision(3)).toString();
}

function getTransitionX(timestamp: string, interval: TemporalAnalyticsView["interval"]): number {
  const start = Date.parse(`${interval.start}T00:00:00Z`);
  const end = Date.parse(`${interval.end}T00:00:00Z`);
  const current = Date.parse(timestamp);
  return X_PADDING + ((current - start) / (end - start)) * (CHART_WIDTH - X_PADDING * 2);
}

function SeriesChart({ series, view }: { series: TemporalSeries; view: TemporalAnalyticsView }) {
  const model = buildChartModel(series, view.interval, CHART_WIDTH, CHART_HEIGHT);
  const plotBottom = CHART_HEIGHT - Y_PADDING;
  const xEnd = CHART_WIDTH - X_PADDING;

  return (
    <article className="temporal-series-card">
      <header className="temporal-series-heading">
        <div>
          <h3>{series.label}</h3>
          <span className="temporal-series-detail">{series.unit} · {series.timeSupport}</span>
        </div>
        <span className={`temporal-status ${series.status}`}>{series.status}</span>
      </header>
      {model.minimum === null || model.maximum === null ? (
        <div className="temporal-chart-empty" role="status">
          No valid samples are available for this series. Missing times remain in the export.
        </div>
      ) : (
        <svg
          className="temporal-chart"
          viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
          role="img"
          aria-label={`${series.label} over time, measured in ${series.unit}`}
        >
          <line x1={X_PADDING} x2={X_PADDING} y1={Y_PADDING} y2={plotBottom} className="chart-axis" />
          <line x1={X_PADDING} x2={xEnd} y1={plotBottom} y2={plotBottom} className="chart-axis" />
          <line x1={X_PADDING} x2={xEnd} y1={Y_PADDING} y2={Y_PADDING} className="chart-gridline" />
          <text x={X_PADDING - 7} y={Y_PADDING + 4} textAnchor="end" className="chart-tick">
            {formatTick(model.maximum)}
          </text>
          <text x={X_PADDING - 7} y={plotBottom + 3} textAnchor="end" className="chart-tick">
            {formatTick(model.minimum)}
          </text>
          <text x={X_PADDING} y={CHART_HEIGHT - 1} className="chart-tick">{view.interval.start}</text>
          <text x={xEnd} y={CHART_HEIGHT - 1} textAnchor="end" className="chart-tick">{view.interval.end} (exclusive)</text>
          {view.stageTransitions.map((transition) => {
            const x = getTransitionX(transition.timestamp, view.interval);
            return (
              <g key={`${transition.timestamp}-${transition.stageCode}`}>
                <line x1={x} x2={x} y1={Y_PADDING} y2={plotBottom} className="stage-marker" />
                <title>{`${transition.stageCode}: ${transition.method} ${transition.methodVersion}; ${transition.qualityState}`}</title>
              </g>
            );
          })}
          {model.segments.map((segment, index) => (
            <g key={`segment-${index}`}>
              {segment.length > 1 && (
                <polyline
                  points={segment.map((point) => `${point.x},${point.y}`).join(" ")}
                  className="temporal-line"
                />
              )}
              {segment.map((point) => (
                <circle key={point.timestamp} cx={point.x} cy={point.y} r="3.5" className="temporal-point">
                  <title>{`${point.timestamp}: ${point.value} ${series.unit}`}</title>
                </circle>
              ))}
            </g>
          ))}
        </svg>
      )}
      <div className="temporal-series-meta">
        <span>Quality: {series.qualityState}</span>
        <span>Source: {series.sourceReference}</span>
        {model.missingCount > 0 && (
          <span>{model.missingCount} missing sample{model.missingCount === 1 ? "" : "s"}; gaps are not interpolated.</span>
        )}
        {series.limitations.map((limitation) => <span key={limitation}>{limitation}</span>)}
      </div>
    </article>
  );
}

function downloadCsv(view: TemporalAnalyticsView) {
  const blob = new Blob([serializeTemporalCsv(view)], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `agrisense-temporal-${view.interval.start}-${view.interval.end}.csv`;
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
}

/** Display provenance-aware time series and export their available records. */
export function TemporalAnalytics({ view, loading = false, error = null }: Props) {
  if (loading) return <p className="temporal-state" role="status">Loading temporal outputs…</p>;
  if (error) return <p className="temporal-state error" role="alert">{error}</p>;
  if (!view) {
    return (
      <div className="temporal-empty" role="status">
        <span className="section-kicker">TEMPORAL ANALYTICS</span>
        <h2>No temporal product loaded</h2>
        <p>Choose a reviewed producer-projected JSON file above. Structural validation checks its metadata and timestamps, not scientific validity.</p>
      </div>
    );
  }

  try {
    validateTemporalView(view);
  } catch (caught) {
    return (
      <p className="temporal-state error" role="alert">
        Temporal output metadata is invalid: {caught instanceof Error ? caught.message : "unknown validation error"}
      </p>
    );
  }

  if (view.series.length === 0 && view.stageTransitions.length === 0) {
    return (
      <div className="temporal-empty" role="status">
        <span className="section-kicker">TEMPORAL ANALYTICS</span>
        <h2>No temporal records in this product</h2>
        <p>The file contains no series or stage transitions for the requested interval.</p>
      </div>
    );
  }

  const hasRecords = view.series.some((series) => series.samples.length > 0) || view.stageTransitions.length > 0;
  return (
    <section className="temporal-analytics" aria-labelledby="temporal-title">
      <header className="panel-heading temporal-page-heading">
        <div>
          <div className="section-kicker">TEMPORAL ANALYTICS</div>
          <h2 id="temporal-title">Observations and stage transitions</h2>
          <p>{view.interval.start} through {view.interval.end} (end exclusive)</p>
        </div>
        <button className="subtle-button" onClick={() => downloadCsv(view)} disabled={!hasRecords}>
          Download CSV ↓
        </button>
      </header>
      {view.series.map((series) => <SeriesChart key={series.id} series={series} view={view} />)}
      {view.stageTransitions.length > 0 && (
        <section className="stage-transition-list" aria-label="Growth-stage transitions">
          <h3>Growth-stage transitions</h3>
          {view.stageTransitions.map((transition) => (
            <p key={`${transition.timestamp}-${transition.stageCode}`}>
              <b>{transition.timestamp}</b> · {transition.stageCode} · {transition.method} {transition.methodVersion} · {transition.qualityState} · {transition.sourceReference}
            </p>
          ))}
        </section>
      )}
      {view.limitations.length > 0 && (
        <ul className="temporal-limitations" aria-label="Product limitations">
          {view.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}
        </ul>
      )}
      <p className="temporal-footnote">Separate scales are used per series. Missing samples break lines and are not interpolated.</p>
    </section>
  );
}
