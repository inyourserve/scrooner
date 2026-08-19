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
  if (query.categorical_predicates.length > 1) return null;

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

  const categoryPredicate = query.categorical_predicates[0];
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
