export interface TemporalSample {
  timestamp: string;
  value: number | null;
  missingReason?: string;
}

export interface TemporalSeries {
  id: string;
  label: string;
  unit: string;
  timeSupport: string;
  sourceReference: string;
  status: "observation" | "estimate";
  qualityState: string;
  samples: TemporalSample[];
  limitations: string[];
}

export interface StageTransition {
  timestamp: string;
  stageCode: string;
  method: string;
  methodVersion: string;
  qualityState: string;
  sourceReference: string;
}

export interface TemporalAnalyticsView {
  interval: { start: string; end: string };
  series: TemporalSeries[];
  stageTransitions: StageTransition[];
  limitations: string[];
}

export interface ChartPoint {
  timestamp: string;
  value: number;
  x: number;
  y: number;
}

export interface ChartModel {
  minimum: number | null;
  maximum: number | null;
  segments: ChartPoint[][];
  missingCount: number;
}

export function validateTemporalView(view: TemporalAnalyticsView): TemporalAnalyticsView;
export function buildChartModel(
  series: TemporalSeries,
  interval: TemporalAnalyticsView["interval"],
  width?: number,
  height?: number,
): ChartModel;
export function serializeTemporalCsv(view: TemporalAnalyticsView): string;
