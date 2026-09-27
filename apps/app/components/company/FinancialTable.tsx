"use client";

import { useState } from "react";
import { EmptyState } from "@/components/scrooner/EmptyState";
import type { Statement } from "@/lib/company/db";

// Scaling/precision here must match lib/company/format.ts's fmtNum() --
// same page, same kind of number, and they used to disagree (2 decimals
// for "T" but only 1 for "B"/"M" here, while fmtNum uses 2 throughout,
// producing visibly different precision between this table and the
// Investor Snapshot panel above it). Kept as a separate function rather
// than switching to fmtNum directly because financial statements need the
// parens-for-negative convention fmtNum doesn't have.
function amount(value: string | null) {
  if (value === null) return "—";
  const number = Number(value);
  if (!Number.isFinite(number)) return "—";
  const absolute = Math.abs(number);
  const scaled = absolute >= 1e12 ? `${(absolute / 1e12).toFixed(2)}T` : absolute >= 1e9 ? `${(absolute / 1e9).toFixed(2)}B` : absolute >= 1e6 ? `${(absolute / 1e6).toFixed(2)}M` : absolute.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  return number < 0 ? `(${scaled})` : scaled;
}

// Historical note (removed 2026-09-08): this table used to split into an
// "Investor view" (regex-filtered) vs. "All lines" toggle. Found live,
// via a direct user report ("why not showing PAT, EBITDA etc in table?"),
// that the regex was silently hiding 6 of the statement's 25 real lines
// by default -- Operating Expenses, Interest Expense, Income Before Tax,
// Income Tax Expense, Property/Plant & Equipment, Share Buybacks -- none
// of them optional for a serious equity researcher (you can't verify
// Operating Income = Gross Profit - Operating Expenses, or Net Income =
// Income Before Tax - Income Tax Expense, if the intermediate lines are
// hidden -- directly undermines this project's own traceability
// principle, doc 05). And "All lines" never actually showed anything
// beyond that SAME small, already-curated set (analytics.statement_line
// only ever has 6-11 rows per statement, curated upstream by Mapper/doc
// 17) -- both toggle states read the identical `statement.lines` array,
// so the split was pure UI friction hiding real signal for zero benefit.
// Removed: the full statement (already a deliberately small, curated
// walk-down, not a raw XBRL tag dump) always renders in full.
export function FinancialTable({ title, companyName, statement, periods = 10 }: { title: string; companyName: string; statement: Statement; periods?: number }) {
  const [periodCount, setPeriodCount] = useState(periods);
  const start = Math.max(0, statement.periods.length - periodCount);
  const visiblePeriods = statement.periods.slice(start);
  const visibleLines = statement.lines;
  if (!visiblePeriods.length || !statement.lines.length) return <EmptyState description={`No comparable ${title.toLowerCase()} periods are available.`} />;
  return <div className="financial-statement"><div className="financial-statement__controls"><div className="segmented-control" role="group" aria-label={`${title} history`}>{[periods, Math.min(statement.periods.length, periods + 5)].filter((value, index, list) => list.indexOf(value) === index).map((value) => <button type="button" aria-pressed={periodCount === value} onClick={() => setPeriodCount(value)} key={value}>{value} periods</button>)}{statement.periods.length > periods + 5 && <button type="button" aria-pressed={periodCount === statement.periods.length} onClick={() => setPeriodCount(statement.periods.length)}>Max</button>}</div></div><p className="table-reading-cue">Previous periods <span aria-hidden="true">→</span> latest</p><div className="statement-scroll" tabIndex={0} role="group" aria-label={`${title}; previous periods lead to latest`}><table className="financial-table"><caption className="sr-only">{title} for {companyName}, previous periods to latest.</caption><thead><tr><th scope="col">Metric</th>{visiblePeriods.map((period, index) => <th scope="col" className={index === visiblePeriods.length - 1 ? "hl" : undefined} key={`${period.fiscal_period}-${period.period_end}`}><span>{period.fiscal_period} {period.fiscal_year}</span><small>{period.period_end}</small></th>)}</tr></thead><tbody>{visibleLines.map((line) => <tr key={line.label}><th scope="row">{line.label}</th>{line.values.slice(start).map((entry, index) => <td className={index === visiblePeriods.length - 1 ? "hl" : undefined} key={index}>{amount(entry)}</td>)}</tr>)}</tbody></table></div></div>;
}
