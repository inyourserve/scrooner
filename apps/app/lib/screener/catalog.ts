import type { CategoryFilter, FilterRow, MetricDefinition, MetricOperator } from "./types";

export const OPERATOR_LABELS: Record<MetricOperator, string> = {
  ">": "Greater than",
  "<": "Less than",
  ">=": "At least",
  "<=": "At most",
  "=": "Equal to",
  "!=": "Not equal to",
  between: "Between",
  top_n: "Top N",
  bottom_n: "Bottom N",
};

export const SIC_OPTIONS = [
  { value: "6021", label: "Banks" },
  { value: "7372", label: "Software" },
  { value: "3674", label: "Semiconductors" },
  { value: "3021", label: "Footwear" },
  { value: "4610", label: "Pipelines" },
  { value: "3571", label: "Computer hardware" },
];

export interface ReferenceScreen {
  id: string;
  label: string;
  description: string;
  rows: Omit<FilterRow, "id">[];
  category: CategoryFilter;
  sortBy: string;
  sortDesc: boolean;
  limit: string;
}

const noCategory: CategoryFilter = { enabled: false, field: "sic_code", value: "" };

export const REFERENCE_SCREENS: ReferenceScreen[] = [
  {
    id: "high-roe",
    label: "ROE above 30%",
    description: "Companies with latest return on equity above 30%.",
    rows: [{ metricName: "roe", operator: ">", value: "30", highValue: "" }],
    category: noCategory,
    sortBy: "roe",
    sortDesc: true,
    limit: "50",
  },
  {
    id: "software",
    label: "Software companies",
    description: "Active companies classified under SIC 7372.",
    rows: [],
    category: { enabled: true, field: "sic_code", value: "7372" },
    sortBy: "",
    sortDesc: true,
    limit: "50",
  },
  {
    id: "low-leverage",
    label: "Debt/equity 0–1x",
    description: "Companies with debt to equity between zero and one.",
    rows: [{ metricName: "debt_to_equity", operator: "between", value: "0", highValue: "1" }],
    category: noCategory,
    sortBy: "debt_to_equity",
    sortDesc: false,
    limit: "50",
  },
  {
    id: "top-roic",
    label: "Top 3 by ROIC",
    description: "The three highest latest return-on-invested-capital values.",
    rows: [{ metricName: "roic", operator: "top_n", value: "3", highValue: "" }],
    category: noCategory,
    sortBy: "",
    sortDesc: true,
    limit: "3",
  },
];

export function metricByName(metrics: MetricDefinition[], metricName: string) {
  return metrics.find((metric) => metric.metric_name === metricName);
}
