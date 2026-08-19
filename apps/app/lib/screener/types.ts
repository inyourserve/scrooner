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

export interface ScreenQueryPayload {
  metric_predicates: MetricPredicatePayload[];
  categorical_predicates: Array<{
    field: "sic_code" | "sic_description";
    operator: "=";
    value: string;
  }>;
  include_inactive: boolean;
  sort_by: string | null;
  sort_desc: boolean;
  limit: number | null;
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
}
