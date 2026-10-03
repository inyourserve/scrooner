import { describe, expect, it } from "vitest";
import { collectMetricNames, collectPredicateMetricNames, type ScreenQueryPayload } from "./types";

const base: ScreenQueryPayload = {
  metric_predicates: [],
  categorical_predicates: [],
  include_inactive: false,
  sort_by: null,
  sort_desc: true,
  limit: null,
};

describe("collectMetricNames", () => {
  it("collects names from the flat metric_predicates list", () => {
    const query: ScreenQueryPayload = {
      ...base,
      metric_predicates: [{ metric_name: "roe", operator: ">", value: "0.3" }],
    };

    expect(collectMetricNames(query)).toEqual(["roe"]);
  });

  it("recursively collects names from an OR where-tree", () => {
    const query: ScreenQueryPayload = {
      ...base,
      where: {
        op: "or",
        predicates: [
          { metric_name: "roe", operator: ">", value: "0.3" },
          { metric_name: "debt_to_equity", operator: "<", value: "0.5" },
        ],
      },
    };

    expect(new Set(collectMetricNames(query))).toEqual(new Set(["roe", "debt_to_equity"]));
  });

  it("collects the ranked predicate's name alongside a NOT-wrapped where tree", () => {
    const query: ScreenQueryPayload = {
      ...base,
      metric_predicates: [{ metric_name: "roic", operator: "top_n", n: 5 }],
      where: {
        op: "not",
        predicates: [{ field: "sector", operator: "=", value: "Financials" }],
      },
    };

    // The excluded sector isn't a metric, so it never appears; the
    // ranked predicate's name does, since it's the whole point of the query.
    expect(collectMetricNames(query)).toEqual(["roic"]);
  });

  it("de-duplicates a name that appears in both the flat list and the tree", () => {
    const query: ScreenQueryPayload = {
      ...base,
      metric_predicates: [{ metric_name: "roe", operator: "top_n", n: 3 }],
      where: {
        op: "and",
        predicates: [
          { metric_name: "roe", operator: ">", value: "0" },
          { field: "sic_code", operator: "=", value: "7372" },
        ],
      },
    };

    expect(collectMetricNames(query)).toEqual(["roe"]);
  });

  it("keeps display-only columns out of match reasons", () => {
    const query: ScreenQueryPayload = {
      ...base,
      metric_predicates: [{ metric_name: "debt_to_equity", operator: "between", value_range: ["0", "1"] }],
      display_metrics: ["market_cap", "roe"],
    };

    expect(collectPredicateMetricNames(query)).toEqual(["debt_to_equity"]);
    expect(collectMetricNames(query)).toEqual(["debt_to_equity", "market_cap", "roe"]);
  });
});
