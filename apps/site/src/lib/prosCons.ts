// Pros/Cons checklist (doc 17 Sec 5) -- deterministic, from already-
// verified metric_value data only, never AI-generated prose. Mirrors
// Screener.in's own real copy ("machine generated... based on a
// checklist") but built from Scrooner's own locked metrics. A rule whose
// required metric is null produces no bullet, never a guessed one -- same
// "null over guess" discipline as everywhere else in this project.

import { getLatestMetrics, getMetricHistory, type MetricRow } from "./db";

export interface ChecklistItem {
  text: string;
  kind: "pro" | "con";
}

function avg(values: (string | null)[]): number | null {
  const nums = values.filter((v): v is string => v !== null).map(Number);
  if (nums.length === 0) return null;
  return nums.reduce((a, b) => a + b, 0) / nums.length;
}

export async function buildChecklist(companyId: number, latest: Record<string, MetricRow>): Promise<ChecklistItem[]> {
  const items: ChecklistItem[] = [];

  const roe3y = avg(await getMetricHistory(companyId, "roe", 3));
  if (roe3y !== null) {
    if (roe3y > 0.2) items.push({ text: `Company has a high return on equity of ${(roe3y * 100).toFixed(1)}% over the last 3 years.`, kind: "pro" });
    if (roe3y < 0.1) items.push({ text: `Company has a low return on equity of ${(roe3y * 100).toFixed(1)}% over the last 3 years.`, kind: "con" });
  }

  const roic3y = avg(await getMetricHistory(companyId, "roic", 3));
  if (roic3y !== null && roic3y > 0.15) {
    items.push({ text: `Company has a strong return on invested capital of ${(roic3y * 100).toFixed(1)}% over the last 3 years.`, kind: "pro" });
  }

  const revGrowth3y = latest["revenue_growth_3y_cagr"]?.value;
  if (revGrowth3y !== null && revGrowth3y !== undefined) {
    const v = Number(revGrowth3y);
    if (v > 0.15) items.push({ text: `Revenue has grown at a 3-year CAGR of ${(v * 100).toFixed(1)}%.`, kind: "pro" });
    if (v < 0) items.push({ text: `Revenue has declined over the last 3 years (CAGR ${(v * 100).toFixed(1)}%).`, kind: "con" });
  }

  const fcfHistory = await getMetricHistory(companyId, "fcf", 3);
  if (fcfHistory.length === 3 && fcfHistory.every((v) => v !== null && Number(v) > 0)) {
    items.push({ text: "Company has generated positive free cash flow in each of the last 3 years.", kind: "pro" });
  }

  const de = latest["debt_to_equity"]?.value;
  if (de !== null && de !== undefined && Number(de) > 2) {
    items.push({ text: `Company has a high debt-to-equity ratio of ${Number(de).toFixed(2)}.`, kind: "con" });
  }

  const icr = latest["interest_coverage_ratio"]?.value;
  if (icr !== null && icr !== undefined && Number(icr) < 2) {
    items.push({ text: `Company has low interest coverage of ${Number(icr).toFixed(2)}x.`, kind: "con" });
  }

  return items;
}
