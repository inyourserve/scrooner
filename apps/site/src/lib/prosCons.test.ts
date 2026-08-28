import assert from "node:assert/strict";
import test from "node:test";

import { buildChecklist } from "./prosCons.ts";
import type { MetricRow } from "./db.ts";

function metric(metricName: string, value: string | null): MetricRow {
  return {
    metric_name: metricName,
    value,
    period_label: "TTM",
    period_end: "2026-06-30",
    is_null_reason: value === null ? "not available" : null,
  };
}

test("buildChecklist uses supplied history without fetching more data", () => {
  const latest = {
    revenue_growth_3y_cagr: metric("revenue_growth_3y_cagr", "0.20"),
    debt_to_equity: metric("debt_to_equity", "2.50"),
    interest_coverage_ratio: metric("interest_coverage_ratio", "1.50"),
  };

  const items = buildChecklist(latest, {
    roe: ["0.30", "0.25", "0.20"],
    roic: ["0.20", "0.18", "0.16"],
    fcf: ["100", "90", "80"],
  });

  assert.equal(items.length, 6);
  assert.equal(items.filter((item) => item.kind === "pro").length, 4);
  assert.equal(items.filter((item) => item.kind === "con").length, 2);
  assert.ok(items.some((item) => item.text.includes("positive free cash flow")));
});

test("buildChecklist omits rules whose required values are unavailable", () => {
  const items = buildChecklist(
    {
      revenue_growth_3y_cagr: metric("revenue_growth_3y_cagr", null),
      debt_to_equity: metric("debt_to_equity", null),
      interest_coverage_ratio: metric("interest_coverage_ratio", null),
    },
    { roe: [], roic: [], fcf: [] },
  );

  assert.deepEqual(items, []);
});

test("buildChecklist preserves low-return and declining-revenue risks", () => {
  const items = buildChecklist(
    { revenue_growth_3y_cagr: metric("revenue_growth_3y_cagr", "-0.04") },
    { roe: ["0.08", "0.07", "0.06"] },
  );

  assert.equal(items.length, 2);
  assert.ok(items.every((item) => item.kind === "con"));
});
