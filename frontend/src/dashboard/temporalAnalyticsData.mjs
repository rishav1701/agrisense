const DATE_ONLY = /^\d{4}-\d{2}-\d{2}$/;

function parseDate(value, label) {
  if (typeof value !== "string" || !DATE_ONLY.test(value)) {
    throw new TypeError(`${label} must be an ISO date (YYYY-MM-DD).`);
  }
  const parsed = Date.parse(`${value}T00:00:00Z`);
  if (!Number.isFinite(parsed) || new Date(parsed).toISOString().slice(0, 10) !== value) {
    throw new TypeError(`${label} is not a valid calendar date.`);
  }
  return parsed;
}

function parseTimestamp(value, label) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}T.+Z$/.test(value)) {
    throw new TypeError(`${label} must be an ISO 8601 UTC timestamp.`);
  }
  const parsed = Date.parse(value);
  if (!Number.isFinite(parsed)) {
    throw new TypeError(`${label} must be a valid ISO 8601 timestamp.`);
  }
  parseDate(value.slice(0, 10), label);
  return parsed;
}

function requireText(value, label) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new TypeError(`${label} must be a non-empty string.`);
  }
}

/** Validate temporal chart data projected from the existing output contracts. */
export function validateTemporalView(view) {
  if (!view || typeof view !== "object") {
    throw new TypeError("Temporal analytics data must be an object.");
  }
  const start = parseDate(view.interval?.start, "interval.start");
  const end = parseDate(view.interval?.end, "interval.end");
  if (start >= end) throw new TypeError("The interval end must follow its start.");
  if (!Array.isArray(view.series) || !Array.isArray(view.stageTransitions)) {
    throw new TypeError("series and stageTransitions must be arrays.");
  }
  if (!Array.isArray(view.limitations)) {
    throw new TypeError("limitations must be an array.");
  }

  const identifiers = new Set();
  for (const [seriesIndex, series] of view.series.entries()) {
    const prefix = `series[${seriesIndex}]`;
    for (const field of ["id", "label", "unit", "timeSupport", "sourceReference", "qualityState"]) {
      requireText(series[field], `${prefix}.${field}`);
    }
    if (!["observation", "estimate"].includes(series.status)) {
      throw new TypeError(`${prefix}.status must be observation or estimate.`);
    }
    if (identifiers.has(series.id)) throw new TypeError("Series ids must be unique.");
    identifiers.add(series.id);
    if (!Array.isArray(series.samples) || series.samples.length === 0) {
      throw new TypeError(`${prefix}.samples must contain at least one sample.`);
    }
    let previous = -Infinity;
    for (const [sampleIndex, sample] of series.samples.entries()) {
      const timestamp = parseTimestamp(sample.timestamp, `${prefix}.samples[${sampleIndex}].timestamp`);
      if (timestamp < start || timestamp >= end) {
        throw new TypeError(`${prefix} contains a sample outside the requested interval.`);
      }
      if (timestamp <= previous) {
        throw new TypeError(`${prefix}.samples must be in strictly increasing time order.`);
      }
      previous = timestamp;
      if (sample.value === null) {
        requireText(sample.missingReason, `${prefix}.samples[${sampleIndex}].missingReason`);
      } else if (typeof sample.value !== "number" || !Number.isFinite(sample.value)) {
        throw new TypeError(`${prefix}.samples[${sampleIndex}].value must be finite or null.`);
      }
    }
    if (!Array.isArray(series.limitations)) {
      throw new TypeError(`${prefix}.limitations must be an array.`);
    }
  }

  for (const [index, transition] of view.stageTransitions.entries()) {
    const prefix = `stageTransitions[${index}]`;
    requireText(transition.stageCode, `${prefix}.stageCode`);
    requireText(transition.method, `${prefix}.method`);
    requireText(transition.methodVersion, `${prefix}.methodVersion`);
    requireText(transition.qualityState, `${prefix}.qualityState`);
    requireText(transition.sourceReference, `${prefix}.sourceReference`);
    const timestamp = parseTimestamp(transition.timestamp, `${prefix}.timestamp`);
    if (timestamp < start || timestamp >= end) {
      throw new TypeError(`${prefix} is outside the requested interval.`);
    }
  }
  for (const [index, limitation] of view.limitations.entries()) {
    requireText(limitation, `limitations[${index}]`);
  }
  return view;
}

/** Parse and validate a producer-projected temporal product JSON document. */
export function parseTemporalViewJson(contents) {
  if (typeof contents !== "string") {
    throw new TypeError("Temporal product content must be text.");
  }
  let parsed;
  try {
    parsed = JSON.parse(contents);
  } catch {
    throw new TypeError("Temporal product must contain valid JSON.");
  }
  return validateTemporalView(parsed);
}

/** Return finite chart coordinates while keeping missing samples as line breaks. */
export function buildChartModel(series, interval, width = 760, height = 220) {
  if (!Number.isFinite(width) || width <= 0 || !Number.isFinite(height) || height <= 0) {
    throw new TypeError("Chart width and height must be positive finite numbers.");
  }
  const start = parseDate(interval.start, "interval.start");
  const end = parseDate(interval.end, "interval.end");
  const values = series.samples.flatMap((sample) => sample.value === null ? [] : [sample.value]);
  if (values.length === 0) {
    return { minimum: null, maximum: null, segments: [], missingCount: series.samples.length };
  }
  let minimum = Math.min(...values);
  let maximum = Math.max(...values);
  if (minimum === maximum) {
    const pad = Math.max(Math.abs(minimum) * 0.05, 0.05);
    minimum -= pad;
    maximum += pad;
  }
  const segments = [];
  let segment = [];
  let missingCount = 0;
  const xPadding = 36;
  const yPadding = 14;
  const plotWidth = Math.max(width - xPadding * 2, 1);
  const plotHeight = Math.max(height - yPadding * 2, 1);
  for (const sample of series.samples) {
    if (sample.value === null) {
      missingCount += 1;
      if (segment.length) segments.push(segment);
      segment = [];
      continue;
    }
    const timestamp = parseTimestamp(sample.timestamp, "sample.timestamp");
    segment.push({
      timestamp: sample.timestamp,
      value: sample.value,
      x: xPadding + ((timestamp - start) / (end - start)) * plotWidth,
      y: yPadding + ((maximum - sample.value) / (maximum - minimum)) * plotHeight,
    });
  }
  if (segment.length) segments.push(segment);
  return { minimum, maximum, segments, missingCount };
}

function csvCell(value, protectFormula = true) {
  let text = value == null ? "" : String(value);
  if (protectFormula && /^[\s\u0000-\u001f]*[=+\-@]/.test(text)) text = `'${text}`;
  return `"${text.replaceAll('"', '""')}"`;
}

/** Serialize observations, missing samples, stage markers, and provenance to CSV. */
export function serializeTemporalCsv(view) {
  validateTemporalView(view);
  const columns = [
    "record_type", "interval_start", "interval_end", "timestamp", "name", "value",
    "unit", "time_support", "source_reference", "status", "quality_state",
    "missing_reason", "method", "method_version", "limitations",
  ];
  const rows = [columns];
  for (const series of view.series) {
    for (const sample of series.samples) {
      rows.push([
        "time_series", view.interval.start, view.interval.end, sample.timestamp,
        series.label, sample.value, series.unit, series.timeSupport,
        series.sourceReference, series.status, series.qualityState,
        sample.value === null ? sample.missingReason : "", "", "",
        [...view.limitations, ...series.limitations].join(" | "),
      ]);
    }
  }
  for (const transition of view.stageTransitions) {
    rows.push([
      "stage_transition", view.interval.start, view.interval.end,
      transition.timestamp, transition.stageCode, "", "", "",
      transition.sourceReference, "estimate", transition.qualityState, "",
      transition.method, transition.methodVersion, view.limitations.join(" | "),
    ]);
  }
  return rows
    .map((row, rowIndex) =>
      row.map((value, columnIndex) =>
        csvCell(value, rowIndex > 0 && columnIndex !== 5 && typeof value === "string"),
      ).join(","),
    )
    .join("\r\n") + "\r\n";
}
