import type { MetricRow } from "@/lib/company/db";
import { fmtBool, fmtDays, fmtMultiple, fmtNum, fmtPct, fmtScore, fmtYears } from "@/lib/company/format";
import { Tooltip } from "@/components/ui/Tooltip";

export type MetricKind = "pct" | "dollar" | "multiple" | "raw" | "days" | "score" | "bool" | "years";
export interface MetricItem { label: string; row?: MetricRow; kind: MetricKind; raw?: string; nullReason?: string }

function value(item: MetricItem) {
  const raw = item.kind === "raw" ? item.raw : item.row?.value;
  if (item.kind === "dollar") return raw ? `$${fmtNum(raw)}` : "—";
  if (item.kind === "multiple") return fmtMultiple(raw);
  if (item.kind === "days") return fmtDays(raw);
  if (item.kind === "score") return fmtScore(raw);
  if (item.kind === "bool") return fmtBool(raw);
  if (item.kind === "years") return fmtYears(raw);
  if (item.kind === "raw") return raw ?? "—";
  return fmtPct(raw);
}

export function MetricGrid({ items, dense = false }: { items: MetricItem[]; dense?: boolean }) {
  return <div className={`metric-grid${dense ? " metric-grid-dense" : ""}`}>{items.map((item) => {
    const missing = item.kind === "raw" ? !item.raw : item.row?.value == null;
    const reason = item.nullReason ?? item.row?.is_null_reason?.replaceAll("_", " ") ?? "Not yet available for this company";
    const period = item.row && !missing ? `${item.row.period_label} · ${item.row.period_end}` : undefined;
    return <div className="metric-cell" key={item.label}><span className="metric-label">{item.label}{missing && <Tooltip label={item.label}>{reason}</Tooltip>}</span><span className={`metric-value${missing ? " metric-blocked" : ""}`} aria-label={missing ? `${item.label}: not available. ${reason}` : undefined}>{value(item)}</span>{!dense && period && <span className="metric-period">{period}</span>}</div>;
  })}</div>;
}
