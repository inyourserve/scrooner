export type ComparisonOperator = ">" | "<" | ">=" | "<=" | "=" | "!=";
export type RankedOperator = "top_n" | "bottom_n";
export type MetricOperator = ComparisonOperator | "between" | RankedOperator;
export type MetricValueType = "percentage" | "currency" | "multiple" | "number";

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
export function collectMetricNames(query: ScreenQueryPayload): string[] {
  const names = new Set(query.metric_predicates.map((p) => p.metric_name));
  const walk = (node: MetricPredicatePayload | CategoricalPredicatePayload | PredicateGroupPayload) => {
    if (isPredicateGroup(node)) {
      node.predicates.forEach(walk);
    } else if ("metric_name" in node) {
      names.add(node.metric_name);
    }
  };
  if (query.where) walk(query.where);
  for (const name of query.display_metrics ?? []) names.add(name);
  return [...names];
}

export interface ResolvedMetric {
  value: string;
  period_label: string;
  period_end: string;
  formula_version: number;
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
}

export interface ScreenResult {
  matched: MatchedCompany[];
  excluded_missing_data: MissingCompany[];
  excluded_inactive: string[];
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
