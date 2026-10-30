import assert from "node:assert/strict";
import test from "node:test";

import {
  buildChartModel,
  filterTemporalView,
  parseTemporalViewJson,
  serializeTemporalCsv,
  validateTemporalView,
} from "../src/dashboard/temporalAnalyticsData.mjs";

// Artificial values exist only to verify browser software behavior.
const softwareFixture = {
  interval: { start: "2023-01-01", end: "2023-01-05" },
  series: [
    {
      id: "fixture-ndvi",
      label: "NDVI",
      unit: "unitless",
      timeSupport: "fabricated test dates",
      sourceReference: "synthetic software fixture",
      status: "observation",
      qualityState: "synthetic_test_only",
      samples: [
        { timestamp: "2023-01-01T00:00:00Z", value: 0.2 },
        {
          timestamp: "2023-01-02T00:00:00Z",
          value: null,
          missingReason: "synthetic gap for software test",
        },
        { timestamp: "2023-01-03T00:00:00Z", value: 0.6 },
      ],
      limitations: ["Artificial test values; not observations."],
    },
  ],
  stageTransitions: [
    {
      timestamp: "2023-01-03T00:00:00Z",
      stageCode: "synthetic_stage",
      method: "synthetic test method",
      methodVersion: "test-only",
      qualityState: "synthetic_test_only",
      sourceReference: "synthetic software fixture",
    },
  ],
  limitations: ["Synthetic software fixture only."],
};

test("validates provenance-aware temporal output and preserves the requested interval", () => {
  assert.equal(validateTemporalView(softwareFixture), softwareFixture);
});

test("parses and validates a temporal product JSON document", () => {
  assert.deepEqual(parseTemporalViewJson(JSON.stringify(softwareFixture)), softwareFixture);
});

test("filters records and stage transitions to a half-open date interval", () => {
  const filtered = filterTemporalView(softwareFixture, {
    start: "2023-01-02",
    end: "2023-01-04",
  });
  assert.deepEqual(filtered.interval, { start: "2023-01-02", end: "2023-01-04" });
  assert.deepEqual(filtered.series[0].samples.map((sample) => sample.timestamp), [
    "2023-01-02T00:00:00Z",
    "2023-01-03T00:00:00Z",
  ]);
  assert.equal(filtered.stageTransitions.length, 1);
  assert.deepEqual(softwareFixture.interval, { start: "2023-01-01", end: "2023-01-05" });
  assert.equal(softwareFixture.series[0].samples.length, 3);
  const csv = serializeTemporalCsv(filtered);
  assert.match(csv, /"2023-01-02","2023-01-04"/);
  assert.doesNotMatch(csv, /2023-01-01T00:00:00Z/);
});

test("date filter rejects empty, invalid, or out-of-product intervals", () => {
  assert.throws(
    () => filterTemporalView(softwareFixture, { start: "2023-01-03", end: "2023-01-03" }),
    /filter end must follow/,
  );
  assert.throws(
    () => filterTemporalView(softwareFixture, { start: "2022-12-31", end: "2023-01-03" }),
    /within the product interval/,
  );
  assert.throws(
    () => filterTemporalView(softwareFixture, { start: "2023-01-02", end: "2023-02-30" }),
    /valid calendar date/,
  );
});

test("rejects malformed JSON and valid JSON without a product interval", () => {
  assert.throws(() => parseTemporalViewJson("{"), /valid JSON/);
  assert.throws(() => parseTemporalViewJson("{}"), /interval.start/);
});

test("chart model leaves a visible break at missing samples", () => {
  const chart = buildChartModel(softwareFixture.series[0], softwareFixture.interval);
  assert.equal(chart.missingCount, 1);
  assert.equal(chart.segments.length, 2);
  assert.deepEqual(chart.segments.map((segment) => segment.length), [1, 1]);
  assert.ok(chart.segments.flat().every((point) => Number.isFinite(point.x) && Number.isFinite(point.y)));
});

test("CSV retains units, quality, provenance, explicit missing reasons, and stage method", () => {
  const csv = serializeTemporalCsv(softwareFixture);
  assert.match(csv, /^"record_type","interval_start","interval_end"/);
  assert.match(csv, /"unitless"/);
  assert.match(csv, /"synthetic software fixture"/);
  assert.match(csv, /"synthetic gap for software test"/);
  assert.match(csv, /"stage_transition"/);
  assert.match(csv, /"synthetic test method"/);
  assert.match(csv, /\r\n$/);
});

test("CSV escapes embedded quotes and neutralizes spreadsheet formulas in text cells", () => {
  const view = structuredClone(softwareFixture);
  view.series[0].sourceReference = "=HYPERLINK(\"bad\")";
  const csv = serializeTemporalCsv(view);
  assert.match(csv, /"'=HYPERLINK\(""bad""\)"/);
});

test("CSV preserves negative numeric observations as numbers", () => {
  const view = structuredClone(softwareFixture);
  view.series[0].samples[0].value = -12.5;
  view.series[0].unit = "dB";
  const csv = serializeTemporalCsv(view);
  assert.match(csv, /"-12\.5","dB"/);
});

test("rejects non-finite values, unordered samples, and samples outside the half-open interval", () => {
  const nonFinite = structuredClone(softwareFixture);
  nonFinite.series[0].samples[0].value = Number.NaN;
  assert.throws(() => validateTemporalView(nonFinite), /finite or null/);

  const unordered = structuredClone(softwareFixture);
  unordered.series[0].samples.reverse();
  assert.throws(() => validateTemporalView(unordered), /strictly increasing/);

  const outOfRange = structuredClone(softwareFixture);
  outOfRange.series[0].samples[2].timestamp = "2023-01-05T00:00:00Z";
  assert.throws(() => validateTemporalView(outOfRange), /outside the requested interval/);
});

test("rejects missing values without an explicit reason", () => {
  const view = structuredClone(softwareFixture);
  delete view.series[0].samples[1].missingReason;
  assert.throws(() => validateTemporalView(view), /missingReason must be a non-empty string/);
});

test("requires UTC timestamps and valid calendar dates", () => {
  const localTime = structuredClone(softwareFixture);
  localTime.series[0].samples[0].timestamp = "2023-01-01T00:00:00";
  assert.throws(() => validateTemporalView(localTime), /ISO 8601 UTC timestamp/);

  const invalidDate = structuredClone(softwareFixture);
  invalidDate.series[0].samples[0].timestamp = "2023-02-30T00:00:00Z";
  assert.throws(() => validateTemporalView(invalidDate), /valid calendar date/);
});
