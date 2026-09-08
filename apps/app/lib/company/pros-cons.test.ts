import { describe, expect, it } from "vitest";
import type { MetricRow } from "./db";
import { buildChecklist } from "./pros-cons";
const metric = (metric_name: string, value: string | null): MetricRow => ({ metric_name, value, period_label: "TTM", period_end: "2026-06-30", is_null_reason: value === null ? "not available" : null });
describe("company checklist", () => {
  it("uses supplied history without extra reads", () => { const items = buildChecklist({ revenue_growth_3y_cagr: metric("revenue_growth_3y_cagr", "0.20"), debt_to_equity: metric("debt_to_equity", "2.50"), interest_coverage_ratio: metric("interest_coverage_ratio", "1.50") }, { roe: ["0.30", "0.25", "0.20"], roic: ["0.20", "0.18", "0.16"], fcf: ["100", "90", "80"] }); expect(items).toHaveLength(6); expect(items.filter((item) => item.kind === "pro")).toHaveLength(4); });
  it("omits unavailable rules", () => { expect(buildChecklist({ revenue_growth_3y_cagr: metric("revenue_growth_3y_cagr", null) }, { roe: [], roic: [], fcf: [] })).toEqual([]); });
});
