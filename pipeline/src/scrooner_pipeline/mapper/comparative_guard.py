"""Comparative-column guard for no-filing reasons (Ritwik, GEV final draw 2026-11-15).

A reason `no_public_filing_for_period` / `no_10k_presents_period` says no periodic filing shows the period. That is
false when ANY accepted annual filing of the company (its own year's 10-K or a later one) prints a column for the
period on a statement: fsn.value rows (undimensioned, in a statement line, not a parenthetical) with that period end
and duration. GEV's FY2024 10-K prints IS and CF for 2024/2023/2022 and the BS at Dec 31 2024 and 2023, so every
2022-23 IS/CF cell and the 2023 balance-sheet cells are presented even though the company's first 10-K is FY2024.

The guard is statement-level on purpose (the resolver decides the line from the column): a refused reason leaves the
cell open (UNCHECKED, never served as a reason) for the resolver to fill from that comparative column.

Two codes, one meaning each:
  no_10k_presents_period       no annual filing presents the period; a registration statement (Form 10, S-1) may have.
  no_public_filing_for_period  nothing at all was public for the period (an excluded wrong-entity window, a company not
                               yet public). Never produced for a company that registered; core.filing holds no Form
                               10 or S-1 (checked 2026-11-16: only 10-K/10-Q/20-F/40F, 424B5), so the structural
                               loader cannot prove "nothing at all" and always writes no_10k_presents_period.

Read-only. Pure helpers are unit-tested; the one DB read is `read_columns`.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

from scrooner_pipeline.common.fsn_dates import fsn_end_matches

NO_FILING_REASON = "no_public_filing_for_period"
NO_10K_REASON = "no_10k_presents_period"
# every code that claims no filing presents the period; the guard applies to all of them
NO_FILING_CODES = frozenset({NO_FILING_REASON, NO_10K_REASON})

ANNUAL_FORMS = (
    "10-K",
    "10-K/A",
    "10-KT",
    "10-KT/A",
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
)
FACE_STMTS = ("IS", "BS", "CF", "CI", "EQ")
# A column is PRINTED when at least this share of the statement's valued tags carry a value at that date. A tag that
# sits on both the balance sheet and the equity roll-forward or cash-flow opening balance has a stray value at an
# earlier date (GEV Dec 31 2022 on the FY2024 10-K): a handful of tags, not a column. Found 2026-11-16 (GEV BS 2022).
MIN_COLUMN_SHARE = 0.5
# fsn qtrs of a fiscal-year duration column (a 52/53-week year is 4 as well); an instant has 0
ANNUAL_QTRS = 4


@dataclass(frozen=True)
class Column:
    """One column a filing prints on a statement: (accession, form, statement, FSN end date, qtrs, lowest report)."""

    accession: str
    form: str
    stmt: str
    ddate: date
    qtrs: int
    report: int | None = None
    n_tags: int = 0  # statement tags with a value in this column
    total_tags: int = (
        0  # statement tags with a value in any column of the filing's statement
    )


def presenting(
    columns: Iterable[Column],
    period_end: date,
    instant: bool,
    stmts: Iterable[str] | None = None,
) -> list[Column]:
    """The columns that present the fiscal period ending `period_end`: same end (FSN month-end rounding included),
    duration 4 quarters (annual) or 0 (instant), on one of `stmts` (any face statement when None). Pure."""
    want = ANNUAL_QTRS if not instant else 0
    allowed = set(stmts) if stmts else set(FACE_STMTS)
    return sorted(
        (
            c
            for c in columns
            if c.qtrs == want
            and c.stmt in allowed
            and (c.total_tags == 0 or c.n_tags >= MIN_COLUMN_SHARE * c.total_tags)
            and fsn_end_matches(c.ddate, period_end)
        ),
        key=lambda c: (c.accession, FACE_STMTS.index(c.stmt), c.report or 0),
    )


def refuse_no_filing_reason(
    columns: Iterable[Column],
    period_end: date,
    instant: bool,
    stmts: Iterable[str] | None = None,
) -> str | None:
    """None when no filing presents the period (the no-filing reason may stand); else why it is refused. Pure."""
    hit = presenting(columns, period_end, instant, stmts)
    if not hit:
        return None
    h = hit[0]
    return (
        f"filing {h.accession} ({h.form}) presents a {h.stmt} column for the period"
        + (f" on R{h.report}" if h.report else "")
        + f" ({len(hit)} such column(s)); the cell stays open for the resolver"
    )


def read_columns(conn: Any, company_ids: list[int]) -> dict[int, list[Column]]:
    """company id -> every statement column its stored annual filings print (read-only, one query)."""
    out: dict[int, list[Column]] = defaultdict(list)
    if not company_ids:
        return out
    for cid, acc, form, stmt, ddate, qtrs, rep, n, total in conn.execute(
        """with base as (
             select f.id fid, f.company_id, f.accession, f.form, l.stmt, l.report, v.tag_id, v.ddate, v.qtrs
             from fsn.filing f
             join fsn.line l on l.filing_id = f.id and l.stmt = any(%s) and not l.inpth
             join fsn.value v on v.filing_id = f.id and v.tag_id = l.tag_id and v.dim_id = 0
                              and v.iprx = 0 and v.coreg = '' and v.value is not null
             where f.company_id = any(%s) and f.form = any(%s) and v.qtrs in (0, %s)),
           tot as (select fid, stmt, count(distinct tag_id) n from base group by fid, stmt)
           select b.company_id, b.accession, b.form, b.stmt, b.ddate, b.qtrs, min(b.report),
                  count(distinct b.tag_id), t.n
           from base b join tot t on t.fid = b.fid and t.stmt = b.stmt
           group by b.company_id, b.accession, b.form, b.stmt, b.ddate, b.qtrs, t.n""",
        (list(FACE_STMTS), company_ids, list(ANNUAL_FORMS), ANNUAL_QTRS),
    ).fetchall():
        out[cid].append(
            Column(acc, form, stmt, ddate, int(qtrs), rep, int(n), int(total))
        )
    return out
