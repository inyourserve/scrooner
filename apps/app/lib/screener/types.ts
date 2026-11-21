export type ComparisonOperator = ">" | "<" | ">=" | "<=" | "=" | "!=";
export type RankedOperator = "top_n" | "bottom_n";
export type MetricOperator = ComparisonOperator | "between" | RankedOperator;
export type MetricValueType = "percentage" | "currency" | "multiple" | "number";

export const DEFAULT_COMPARISON_METRICS = [
  "market_cap",
  "trailing_pe",
  "roe",
  "roic",
  "revenue_growth_yoy",
  "eps_growth_yoy",
  "debt_to_equity",
  "fcf_margin",
  "dividend_yield",
] as const;

export interface MetricDefinition {
  metric_name: string;
  display_name: string;
  short_definition: string;
  formula_description: string;
  formula_version: number;
  category: string;
  value_type: MetricValueType;
  operators: MetricOperator[];
}

export interface FilterRow {
  id: string;
  metricName: string;
  operator: MetricOperator;
  value: string;
  highValue: string;
  // Keep companies with no value for this metric (shown as "—" with the
  // reason) instead of excluding them. Not valid on Top N / Bottom N.
  includeMissing?: boolean;
}

export interface CategoryFilter {
  enabled: boolean;
  field: "sic_code" | "sic_description";
  value: string;
}

export interface MetricPredicatePayload {
  metric_name: string;
  operator: MetricOperator;
  value?: string | null;
  value_range?: [string, string] | null;
  n?: number | null;
  include_missing?: boolean;
}

export interface CategoricalPredicatePayload {
  field: "sic_code" | "sic_description" | "sector";
  operator: "=";
  value: string;
}

// A boolean-tree filter node (added 2026-09-11, matches the backend's
// PredicateGroup -- doc/adr/0001-screener-redis-cache-and-boolean-
// logic.md). A leaf is a metric or categorical predicate; `not` always
// has exactly one child.
export interface PredicateGroupPayload {
  op: "and" | "or" | "not";
  predicates: Array<MetricPredicatePayload | CategoricalPredicatePayload | PredicateGroupPayload>;
}

export interface ScreenQueryPayload {
  metric_predicates: MetricPredicatePayload[];
  categorical_predicates: CategoricalPredicatePayload[];
  // Set only for an AND/OR/NOT query (e.g. from the NL parser: "roe above
  // 30% or debt to equity below 0.5"). When present, it -- not the two
  // flat lists above -- is what actually determined the result; the
  // builder UI cannot represent it as editable rows (see
  // queryToBuilderState, which returns null for a query shaped this way).
  where?: PredicateGroupPayload | null;
  include_inactive: boolean;
  sort_by: string | null;
  sort_desc: boolean;
  limit: number | null;
  display_metrics?: string[];
}

function isPredicateGroup(node: MetricPredicatePayload | CategoricalPredicatePayload | PredicateGroupPayload): node is PredicateGroupPayload {
  return "op" in node;
}

/** Every metric name referenced anywhere in a query -- the flat lists,
 * plus a recursive walk of `where` if present. Mirrors the backend's
 * `_collect_metric_names` (screener/query.py) so the results table shows
 * a column for every metric an OR/NOT query actually filtered on, not
 * just the ones that happen to live in the flat lists. */
export function collectPredicateMetricNames(query: ScreenQueryPayload): string[] {
  const names = new Set(query.metric_predicates.map((p) => p.metric_name));
  const walk = (node: MetricPredicatePayload | CategoricalPredicatePayload | PredicateGroupPayload) => {
    if (isPredicateGroup(node)) {
      node.predicates.forEach(walk);
    } else if ("metric_name" in node) {
      names.add(node.metric_name);
    }
  };
  if (query.where) walk(query.where);
  return [...names];
}

export function collectMetricNames(query: ScreenQueryPayload): string[] {
  const names = new Set(collectPredicateMetricNames(query));
  for (const name of query.display_metrics ?? []) names.add(name);
  return [...names];
}

export type MissingReasonBucket =
  | "not_in_template"
  | "history_horizon"
  | "undefined_by_math"
  | "not_presented"
  | "stale"
  | "open_gap";

/** Mirrors pipeline screener/missing_reasons.py BUCKET_LABELS (the backend
 * also sends its labels; these are the fallback and the display order). */
export const MISSING_REASON_LABELS: Record<MissingReasonBucket, string> = {
  not_in_template: "Not applicable to sector",
  history_horizon: "No prior-year filing",
  undefined_by_math: "Undefined (zero or negative base)",
  not_presented: "Not disclosed in filings",
  stale: "Latest value older than latest filing",
  open_gap: "No value yet (our gap)",
};

export interface MissingReason {
  code: string | null;
  bucket: MissingReasonBucket;
  label?: string;
}

export interface ResolvedMetric {
  // null only when a filter kept the company without a value (include_missing).
  value: string | null;
  period_label: string | null;
  period_end: string | null;
  formula_version: number | null;
  missing?: MissingReason;
}

export interface MatchedCompany {
  company_id: number;
  cik: string;
  company_name: string;
  sic_code: string | null;
  sic_description: string | null;
  status: string;
  ticker: string | null;
  metrics: Record<string, ResolvedMetric>;
}

export interface MissingCompany {
  cik: string;
  company_name: string;
  missing_metrics: string[];
  reasons?: Record<string, MissingReason>;
}

/** matched + excluded + not_matched = total_candidates. */
export interface ExclusionSummary {
  total_candidates: number;
  matched: number;
  excluded: number;
  not_matched: number;
  by_bucket: Partial<Record<MissingReasonBucket, number>>;
  by_metric: Record<string, Partial<Record<MissingReasonBucket, number>>>;
  bucket_labels?: Record<string, string>;
}

export interface ScreenResult {
  matched: MatchedCompany[];
  excluded_missing_data: MissingCompany[];
  excluded_inactive: string[];
  exclusion_summary?: ExclusionSummary | null;
}

export interface QueryBuildResult {
  query: ScreenQueryPayload | null;
  errors: Record<string, string>;
}

export interface AmbiguityNote {
  phrase: string;
  candidates: string[];
}

export interface AskResponse {
  explanation: string;
  query: ScreenQueryPayload | null;
  recognized_query: ScreenQueryPayload | null;
  unrecognized: string[];
  ambiguous: AmbiguityNote[];
  result?: ScreenResult;
}
