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
