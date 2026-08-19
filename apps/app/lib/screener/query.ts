import type {
  CategoryFilter,
  FilterRow,
  MetricDefinition,
  MetricPredicatePayload,
  QueryBuildResult,
  ScreenQueryPayload,
} from "./types";

const DECIMAL_PATTERN = /^-?(?:\d+\.?\d*|\.\d+)$/;

function normalizeDecimal(raw: string): string | null {
  const value = raw.trim().replaceAll(",", "");
  if (!DECIMAL_PATTERN.test(value)) return null;
  const negative = value.startsWith("-");
  const unsigned = negative ? value.slice(1) : value;
  const [wholeRaw, fractionRaw = ""] = unsigned.split(".");
  const whole = (wholeRaw || "0").replace(/^0+(?=\d)/, "");
  const fraction = fractionRaw.replace(/0+$/, "");
  const normalized = fraction ? `${whole}.${fraction}` : whole;
  if (/^0(?:\.0*)?$/.test(normalized)) return "0";
  return negative ? `-${normalized}` : normalized;
}

function shiftDecimalLeft(value: string, places: number): string {
  const negative = value.startsWith("-");
  const unsigned = negative ? value.slice(1) : value;
  const digits = unsigned.replace(".", "");
  const decimalIndex = (unsigned.includes(".") ? unsigned.indexOf(".") : unsigned.length) - places;
  let shifted: string;
  if (decimalIndex <= 0) {
    shifted = `0.${"0".repeat(Math.abs(decimalIndex))}${digits}`;
  } else if (decimalIndex >= digits.length) {
    shifted = `${digits}${"0".repeat(decimalIndex - digits.length)}`;
  } else {
    shifted = `${digits.slice(0, decimalIndex)}.${digits.slice(decimalIndex)}`;
  }
  const normalized = normalizeDecimal(`${negative ? "-" : ""}${shifted}`);
  return normalized ?? "0";
}

function shiftDecimalRight(value: string, places: number): string {
  const negative = value.startsWith("-");
  const unsigned = negative ? value.slice(1) : value;
  const digits = unsigned.replace(".", "");
  const decimalIndex = (unsigned.includes(".") ? unsigned.indexOf(".") : unsigned.length) + places;
  const shifted = decimalIndex >= digits.length
    ? `${digits}${"0".repeat(decimalIndex - digits.length)}`
    : `${digits.slice(0, decimalIndex)}.${digits.slice(decimalIndex)}`;
  return normalizeDecimal(`${negative ? "-" : ""}${shifted}`) ?? "0";
}

function compareNormalizedDecimals(left: string, right: string): number {
  const leftNegative = left.startsWith("-");
  const rightNegative = right.startsWith("-");
  if (leftNegative !== rightNegative) return leftNegative ? -1 : 1;

  const [leftWhole, leftFraction = ""] = (leftNegative ? left.slice(1) : left).split(".");
  const [rightWhole, rightFraction = ""] = (rightNegative ? right.slice(1) : right).split(".");
  let magnitude = leftWhole.length - rightWhole.length;
  if (magnitude === 0) magnitude = leftWhole.localeCompare(rightWhole);
  if (magnitude === 0) {
    const width = Math.max(leftFraction.length, rightFraction.length);
    magnitude = leftFraction.padEnd(width, "0").localeCompare(rightFraction.padEnd(width, "0"));
  }
  return leftNegative ? -magnitude : magnitude;
}

export function toApiValue(raw: string, metric: MetricDefinition): string | null {
  const normalized = normalizeDecimal(raw);
  if (normalized === null) return null;
  return metric.value_type === "percentage" ? shiftDecimalLeft(normalized, 2) : normalized;
}

export function fromApiValue(raw: string, metric: MetricDefinition): string {
  const normalized = normalizeDecimal(raw);
  if (normalized === null) return raw;
  return metric.value_type === "percentage" ? shiftDecimalRight(normalized, 2) : normalized;
}

interface BuildOptions {
  rows: FilterRow[];
  category: CategoryFilter;
  sortBy: string;
  sortDesc: boolean;
  limit: string;
  includeInactive: boolean;
  metrics: MetricDefinition[];
}

export function buildScreenQuery(options: BuildOptions): QueryBuildResult {
  const { rows, category, sortBy, sortDesc, limit, includeInactive, metrics } = options;
  const errors: Record<string, string> = {};
  const definitions = new Map(metrics.map((metric) => [metric.metric_name, metric]));
  const rankedRows = rows.filter((row) => row.operator === "top_n" || row.operator === "bottom_n");

  if (rankedRows.length > 1) {
    errors.form = "Use only one Top N or Bottom N condition in a screen.";
  }
  if (rows.length === 0 && !(category.enabled && category.value)) {
    errors.form = "Add at least one metric or company classification.";
  }

  const metricPredicates = rows.flatMap<MetricPredicatePayload>((row): MetricPredicatePayload[] => {
    const metric = definitions.get(row.metricName);
    if (!metric) {
      errors[row.id] = "Choose a supported metric.";
      return [];
    }
    if (!metric.operators.includes(row.operator)) {
      errors[row.id] = "Choose an operator supported by this metric.";
      return [];
    }

    if (row.operator === "top_n" || row.operator === "bottom_n") {
      const n = Number(row.value);
      if (!/^\d+$/.test(row.value.trim()) || !Number.isSafeInteger(n) || n < 1) {
        errors[row.id] = "Enter a positive whole number for N.";
        return [];
      }
      return [{ metric_name: row.metricName, operator: row.operator, n }];
    }

    const low = toApiValue(row.value, metric);
    if (low === null) {
      errors[row.id] = "Enter a valid numeric value.";
      return [];
    }

    if (row.operator === "between") {
      const high = toApiValue(row.highValue, metric);
      if (high === null) {
        errors[row.id] = "Enter both ends of the range.";
        return [];
      }
      if (compareNormalizedDecimals(low, high) >= 0) {
        errors[row.id] = "The first value must be lower than the second.";
        return [];
      }
      return [{ metric_name: row.metricName, operator: row.operator, value_range: [low, high] as [string, string] }];
    }

    return [{ metric_name: row.metricName, operator: row.operator, value: low }];
  });

  if (category.enabled && !category.value) {
    errors.category = "Choose a company classification.";
  }

  let parsedLimit: number | null = null;
  if (limit.trim()) {
    parsedLimit = Number(limit);
    if (!/^\d+$/.test(limit.trim()) || !Number.isSafeInteger(parsedLimit) || parsedLimit < 1) {
      errors.limit = "Limit must be a positive whole number.";
    }
  }

  if (sortBy && !definitions.has(sortBy)) {
    errors.sort = "Choose a supported sort metric.";
  }

  if (Object.keys(errors).length > 0) return { query: null, errors };

  const query: ScreenQueryPayload = {
    metric_predicates: metricPredicates,
    categorical_predicates: category.enabled
      ? [{ field: category.field, operator: "=", value: category.value }]
      : [],
    include_inactive: includeInactive,
    sort_by: sortBy || null,
    sort_desc: sortDesc,
    limit: parsedLimit,
  };
  return { query, errors: {} };
}
