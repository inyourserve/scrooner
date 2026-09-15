import { describe, expect, it } from "vitest";
import { queryToBuilderState } from "./interpretation";
import type { MetricDefinition, ScreenQueryPayload } from "./types";

const roe: MetricDefinition = {
  metric_name: "roe",
  display_name: "Return on equity (ROE)",
  short_definition: "Net income relative to stockholders' equity.",
  formula_description: "Net Income / Stockholders' Equity",
  formula_version: 1,
  category: "Returns",
  value_type: "percentage",
  operators: [">", "<", ">=", "<=", "=", "!=", "between", "top_n", "bottom_n"],
};

const base: ScreenQueryPayload = {
  metric_predicates: [],
  categorical_predicates: [],
  include_inactive: false,
  sort_by: null,
  sort_desc: true,
  limit: null,
};

let nextId = 1;
const idFactory = () => `row-${nextId++}`;

describe("queryToBuilderState", () => {
  it("builds editable rows for a plain flat AND query", () => {
    const query: ScreenQueryPayload = {
      ...base,
      metric_predicates: [{ metric_name: "roe", operator: ">", value: "0.3" }],
    };

    const state = queryToBuilderState(query, [roe], idFactory);

    expect(state).not.toBeNull();
    expect(state?.rows).toHaveLength(1);
    expect(state?.rows[0].metricName).toBe("roe");
  });

  it("returns null for a where-tree (AND/OR/NOT) query -- the flat builder can't represent it", () => {
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

    expect(queryToBuilderState(query, [roe], idFactory)).toBeNull();
  });

  it("returns null for a sector-bucket categorical predicate -- the builder has no UI for it", () => {
    const query: ScreenQueryPayload = {
      ...base,
      categorical_predicates: [{ field: "sector", operator: "=", value: "Healthcare" }],
    };

    expect(queryToBuilderState(query, [roe], idFactory)).toBeNull();
  });

  it("still returns null for more than one categorical predicate (pre-existing behavior, unchanged)", () => {
    const query: ScreenQueryPayload = {
      ...base,
      categorical_predicates: [
        { field: "sic_code", operator: "=", value: "7372" },
        { field: "sic_code", operator: "=", value: "2834" },
      ],
    };

    expect(queryToBuilderState(query, [roe], idFactory)).toBeNull();
  });
});
