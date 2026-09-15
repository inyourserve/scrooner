import { OPERATOR_LABELS, SIC_OPTIONS, metricByName } from "./catalog";
import { formatMetricValue } from "./format";
import { fromApiValue } from "./query";
import type {
  CategoryFilter,
  FilterRow,
  MetricDefinition,
  MetricPredicatePayload,
  ScreenQueryPayload,
} from "./types";

export const NATURAL_QUERY_EXAMPLES = [
  "companies with ROE above 30%",
  "software companies",
  "debt to equity between 0 and 1",
  "top 3 by ROIC",
  "revenue growth 3Y CAGR above 15%",
];

const PARSER_PHRASES: Record<string, string> = {
  revenue_growth_yoy: "revenue growth yoy",
  revenue_growth_3y_cagr: "revenue growth 3y cagr",
  eps_growth_yoy: "eps growth yoy",
  eps_growth_3y_cagr: "eps growth 3y cagr",
};

export function parserPhraseForMetric(metricName: string): string {
  return PARSER_PHRASES[metricName] ?? metricName.replaceAll("_", " ");
}

export function predicateValueLabel(predicate: MetricPredicatePayload, metric?: MetricDefinition): string {
  if (predicate.operator === "top_n" || predicate.operator === "bottom_n") return String(predicate.n ?? "—");
  if (predicate.operator === "between" && predicate.value_range) {
    return `${formatMetricValue(predicate.value_range[0], metric)} – ${formatMetricValue(predicate.value_range[1], metric)}`;
  }
  return predicate.value != null ? formatMetricValue(predicate.value, metric) : "—";
}

export function predicateSummary(predicate: MetricPredicatePayload, metrics: MetricDefinition[]) {
  const metric = metricByName(metrics, predicate.metric_name);
  return {
    metric: metric?.display_name ?? predicate.metric_name,
    operator: OPERATOR_LABELS[predicate.operator],
    value: predicateValueLabel(predicate, metric),
  };
}

export function categorySummary(query: ScreenQueryPayload): string[] {
  return query.categorical_predicates.map((predicate) => {
    const known = SIC_OPTIONS.find((option) => option.value === predicate.value);
    return `${known?.label ?? predicate.field} · SIC ${predicate.value}`;
  });
}

export interface BuilderState {
  rows: FilterRow[];
  category: CategoryFilter;
  sortBy: string;
  sortDesc: boolean;
  limit: string;
  includeInactive: boolean;
}

export function queryToBuilderState(
  query: ScreenQueryPayload,
  metrics: MetricDefinition[],
  idFactory: () => string,
): BuilderState | null {
  // The flat "Exact filters" builder can only ever represent an AND-of-
  // predicates -- an AND/OR/NOT query (from the NL parser) has no honest
  // row-by-row representation, so this returns null rather than a
  // builder state seeded from the (near-empty) flat lists, which would
  // silently show 0-1 rows and imply that's the whole query. Real
  // results still render regardless -- ScreenerClient.applyRunPage only
  // uses this for the optional, editable-filters panel, never to gate
  // whether a match is displayed.
  if (query.where) return null;
  if (query.categorical_predicates.length > 1) return null;
  // The builder's own classification dropdown only ever offers SIC
  // codes/descriptions (SIC_OPTIONS) -- it has no UI for a sector-bucket
  // predicate (`field: "sector"`, doc 28's broader "healthcare
  // companies"-style phrases), even though the NL parser and backend
  // have supported that field since 2026-08-21. Surfaced by widening
  // CategoricalPredicatePayload's type to match the backend accurately
  // (2026-09-11) -- this case existed before that, just silently,
  // because the old narrower type let TypeScript wave it through.
  if (query.categorical_predicates.some((p) => p.field === "sector")) return null;

  const rows = query.metric_predicates.map((predicate) => {
    const metric = metricByName(metrics, predicate.metric_name);
    const value = predicate.operator === "top_n" || predicate.operator === "bottom_n"
      ? String(predicate.n ?? "")
      : predicate.value != null && metric
        ? fromApiValue(predicate.value, metric)
        : predicate.value ?? "";
    const highValue = predicate.operator === "between" && predicate.value_range
      ? metric
        ? fromApiValue(predicate.value_range[1], metric)
        : predicate.value_range[1]
      : "";
    const lowValue = predicate.operator === "between" && predicate.value_range
      ? metric
        ? fromApiValue(predicate.value_range[0], metric)
        : predicate.value_range[0]
      : value;
    return {
      id: idFactory(),
      metricName: predicate.metric_name,
      operator: predicate.operator,
      value: lowValue,
      highValue,
    };
  });

  // The guard above already ruled out "sector" -- only sic_code/
  // sic_description can reach here, but a .some() check upstream doesn't
  // narrow this array access for TypeScript.
  const categoryPredicate = query.categorical_predicates[0] as
    | { field: "sic_code" | "sic_description"; value: string }
    | undefined;
  return {
    rows,
    category: categoryPredicate
      ? { enabled: true, field: categoryPredicate.field, value: categoryPredicate.value }
      : { enabled: false, field: "sic_code", value: "" },
    sortBy: query.sort_by ?? "",
    sortDesc: query.sort_desc,
    limit: query.limit == null ? "" : String(query.limit),
    includeInactive: query.include_inactive,
  };
}
