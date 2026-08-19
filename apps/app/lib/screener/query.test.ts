import { describe, expect, it } from "vitest";
import { REFERENCE_SCREENS } from "./catalog";
import { buildScreenQuery, fromApiValue, toApiValue } from "./query";
import type { FilterRow, MetricDefinition } from "./types";

const operators: MetricDefinition["operators"] = [">", "<", ">=", "<=", "=", "!=", "between", "top_n", "bottom_n"];

const metrics: MetricDefinition[] = [
  {
    metric_name: "roe",
    display_name: "Return on equity (ROE)",
    short_definition: "Net income relative to equity.",
    formula_description: "Net Income / Equity",
    formula_version: 1,
    category: "Returns",
    value_type: "percentage",
    operators,
  },
  {
    metric_name: "roic",
    display_name: "Return on invested capital (ROIC)",
    short_definition: "After-tax operating return on invested capital.",
    formula_description: "NOPAT / Invested Capital",
    formula_version: 1,
    category: "Returns",
    value_type: "percentage",
    operators,
  },
  {
    metric_name: "debt_to_equity",
    display_name: "Debt to equity",
    short_definition: "Debt relative to equity.",
    formula_description: "Debt / Equity",
    formula_version: 1,
    category: "Financial strength",
    value_type: "multiple",
    operators,
  },
];

function buildReference(index: number) {
  const screen = REFERENCE_SCREENS[index];
  const rows: FilterRow[] = screen.rows.map((row, rowIndex) => ({ ...row, id: `${screen.id}-${rowIndex}` }));
  return buildScreenQuery({
    rows,
    category: screen.category,
    sortBy: screen.sortBy,
    sortDesc: screen.sortDesc,
    limit: screen.limit,
    includeInactive: false,
    metrics,
  });
}

describe("buildScreenQuery", () => {
  it("builds all four verified reference-screen contracts exactly", () => {
    expect(buildReference(0).query).toEqual({
      metric_predicates: [{ metric_name: "roe", operator: ">", value: "0.3" }],
      categorical_predicates: [],
      include_inactive: false,
      sort_by: "roe",
      sort_desc: true,
      limit: 50,
    });

    expect(buildReference(1).query).toEqual({
      metric_predicates: [],
      categorical_predicates: [{ field: "sic_code", operator: "=", value: "7372" }],
      include_inactive: false,
      sort_by: null,
      sort_desc: true,
      limit: 50,
    });

    expect(buildReference(2).query).toEqual({
      metric_predicates: [{ metric_name: "debt_to_equity", operator: "between", value_range: ["0", "1"] }],
      categorical_predicates: [],
      include_inactive: false,
      sort_by: "debt_to_equity",
      sort_desc: false,
      limit: 50,
    });

    expect(buildReference(3).query).toEqual({
      metric_predicates: [{ metric_name: "roic", operator: "top_n", n: 3 }],
      categorical_predicates: [],
      include_inactive: false,
      sort_by: null,
      sort_desc: true,
      limit: 3,
    });
  });

  it("converts display percentages without binary floating-point serialization", () => {
    expect(toApiValue("12.34567890123456789", metrics[0])).toBe("0.1234567890123456789");
    expect(fromApiValue("0.1234567890123456789", metrics[0])).toBe("12.34567890123456789");
  });

  it("compares range endpoints without collapsing high-precision decimals", () => {
    const built = buildScreenQuery({
      rows: [{
        id: "precise-range",
        metricName: "debt_to_equity",
        operator: "between",
        value: "1.0000000000000000000000000001",
        highValue: "1.0000000000000000000000000002",
      }],
      category: { enabled: false, field: "sic_code", value: "" },
      sortBy: "",
      sortDesc: true,
      limit: "50",
      includeInactive: false,
      metrics,
    });

    expect(built.errors).toEqual({});
    expect(built.query?.metric_predicates[0].value_range).toEqual([
      "1.0000000000000000000000000001",
      "1.0000000000000000000000000002",
    ]);
  });

  it("blocks invalid and structurally unsupported input", () => {
    const built = buildScreenQuery({
      rows: [
        { id: "one", metricName: "roe", operator: "top_n", value: "3", highValue: "" },
        { id: "two", metricName: "roic", operator: "bottom_n", value: "3", highValue: "" },
      ],
      category: { enabled: false, field: "sic_code", value: "" },
      sortBy: "",
      sortDesc: true,
      limit: "0",
      includeInactive: false,
      metrics,
    });

    expect(built.query).toBeNull();
    expect(built.errors.form).toMatch(/only one/i);
    expect(built.errors.limit).toMatch(/positive whole number/i);
  });
});
