// Shared display formatters for company-page metrics (doc 17 -> doc 26 ->
// design framework Sec 12.2/13.5). Shared by the stock-page components so
// the metric grid, statement tables, and any future page can share one
// formatting contract instead of re-deriving it -- see design framework
// Sec 20.2 ("shared financial formatting utilities").
//
// All inputs are Decimal-as-string from Postgres (never parsed to float
// upstream, per doc 04's correctness controls); these functions format
// for DISPLAY only -- the exact string value stays available separately
// wherever full precision matters (title/aria attributes).

export function fmtPct(value: string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return (Number(value) * 100).toFixed(1) + "%";
}

export function fmtNum(value: string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  const n = Number(value);
  if (Math.abs(n) >= 1e12) return (n / 1e12).toFixed(2) + "T";
  if (Math.abs(n) >= 1e9) return (n / 1e9).toFixed(2) + "B";
  if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(2) + "M";
  return n.toFixed(2);
}

export function fmtMultiple(value: string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return Number(value).toFixed(2) + "x";
}

export function fmtDays(value: string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return Number(value).toFixed(1) + "d";
}

export function fmtScore(value: string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return Number(value).toFixed(0) + "/9";
}

export function fmtBool(value: string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return Number(value) === 1 ? "Yes" : "No";
}

export function fmtYears(value: string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  const n = Number(value);
  return n.toFixed(0) + (n === 1 ? " yr" : " yrs");
}

// Share counts are whole numbers (Form 4 shares/shares_owned_following) --
// deliberately separate from fmtNum so statement-table dollar formatting
// is never accidentally touched by a share-count-specific change.
export function fmtShares(value: string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  const n = Number(value);
  if (Math.abs(n) >= 1e9) return (n / 1e9).toFixed(2) + "B";
  if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(2) + "M";
  return n.toLocaleString("en-US");
}
