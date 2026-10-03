import type { MetricDefinition, ResolvedMetric } from "./types";

function withCommas(value: number, maximumFractionDigits: number) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits }).format(value);
}

export function formatMetricValue(raw: string, metric?: MetricDefinition): string {
  const value = Number(raw);
  if (!Number.isFinite(value)) return raw;
  switch (metric?.value_type) {
    case "percentage":
      return `${withCommas(value * 100, 1)}%`;
    case "currency": {
      const absolute = Math.abs(value);
      if (absolute >= 1_000_000_000) return `$${withCommas(value / 1_000_000_000, 2)}B`;
      if (absolute >= 1_000_000) return `$${withCommas(value / 1_000_000, 2)}M`;
      return `$${withCommas(value, 2)}`;
    }
    case "multiple":
      return `${withCommas(value, 2)}x`;
    default:
      return withCommas(value, 2);
  }
}

export function metricPeriod(metric: ResolvedMetric): string {
  return `${metric.period_label} · ${metric.period_end}`;
}

const RESULT_COLUMN_LABELS: Record<string, string> = {
  market_cap: "Market cap",
  trailing_pe: "P/E",
  roe: "ROE",
  roic: "ROIC",
  revenue_growth_yoy: "Revenue growth",
  eps_growth_yoy: "EPS growth",
  fcf_margin: "FCF margin",
  dividend_yield: "Dividend yield",
  debt_to_equity: "Debt / equity",
};

export function resultColumnLabel(metricName: string, definition?: MetricDefinition) {
  return RESULT_COLUMN_LABELS[metricName] ?? definition?.display_name ?? metricName.replaceAll("_", " ");
}

export function resultColumnUnit(definition?: MetricDefinition) {
  if (definition?.value_type === "percentage") return "%";
  if (definition?.value_type === "currency") return "USD";
  if (definition?.value_type === "multiple") return "×";
  return "Value";
}
