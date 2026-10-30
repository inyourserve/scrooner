"""Staleness guard: a value that is far older than the company's own latest
filing is hidden at serve time, with a stated reason.

Decision (Dhairya, delegated by the founder, 2026-10-19; data-team/33 family E,
batch B1(e)). A value is STALE when it is

  * an ANNUAL value (period_label 'FY') more than 1 fiscal year behind the
    company's OWN latest filed period, or
  * a QUARTERLY or TTM value (period_label Q1..Q4 or 'TTM') more than 2
    quarters behind it.

The shown reason is 'not in the latest filing (last reported FY<year>)'
(quarterly/TTM: '... (last reported quarter ended <date>)').

Why relative to the company's own filing and not to today: a company whose
latest filing is itself old (a late filer, a company the SEC feed lags on)
has its latest values compared with ITSELF, so they are never hidden by a
calendar cutoff. Only a value that the company's own newer filings have moved
past is hidden.

How "fiscal year behind" is measured: by period-end DATE gap, not by the
fiscal_year label. Labels are unreliable (one real period is reported under
different fy/fp labels in different filings, core.period comment) and a change
of fiscal-year end would break a label count. A fiscal year is 364..371 days
(Apple FY2023 = 371, ledger 2026-10-18) and a quarter 84..98 days, so:

  * annual: stale when gap > ANNUAL_MAX_GAP_DAYS (400). One fiscal year behind
    is at most ~371 days (kept). Two years behind, when the latest filing is
    at least a quarter into the next year, is at least ~443 days (stale).
  * quarterly/TTM: stale when gap > QUARTERLY_MAX_GAP_DAYS (230). Two quarters
    behind is at most ~196 days (kept, even with 14-week quarters). Three
    quarters behind is at least ~250 days (stale).

Both cut-offs sit in the middle of the empty band between "kept" and "stale"
gaps, so a 52/53-week year, a 14-week quarter or a transition period cannot
flip a decision. A fiscal-year-end change is handled because only dates are
compared (tests cover Dec -> Sep).

What this module never does: change a stored value, create a value, or hide
anything when it cannot PROVE the value is old. No latest filed period known
(no 10-K/10-Q row with a period_of_report), a value with no period end, or a
period label that is neither annual nor quarterly/TTM -> not stale, the value
is left exactly as it was. The guard can only blank; it can never produce a
wrong number.

Evidence label: the rule is a delegated product decision; the gap thresholds
were derived from the filing-checked period lengths in the lessons ledger. The
fixtures in the tests are real stale cells found FILING-CHECKED by the
verifier shards (doc/data-moat/team/top1000/status.md); their dates here are
representative of those cells, not copied from the filings.

One module serves every path (screener resolve + snapshot, company page,
watchlist), exactly as `sector_applicability.py` does for banks, so the
three cannot drift apart. `stale_predicate_sql` renders the same thresholds as
SQL for the one place (the company page peer table) where the decision has to
be made inside the query; a test pins the SQL to these constants.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime, timedelta

from scrooner_pipeline.common.rule_flags import (
    RULE_SHARED_ACCESSION_PRIMARY,
    rule_enabled,
)

ANNUAL_MAX_GAP_DAYS = 400
QUARTERLY_MAX_GAP_DAYS = 230
FUTURE_DATE_GRACE_DAYS = 30  # same buffer as screener/resolve.py

ANNUAL_LABELS = frozenset({"FY"})
QUARTERLY_LABELS = frozenset({"Q1", "Q2", "Q3", "Q4", "TTM"})

# The company's "own latest filed period": the latest period_of_report of its
# periodic reports. Original and amended forms both count (an amendment of an
# old period has an old period_of_report and cannot move the reference ahead).
PERIODIC_FORMS = (
    "10-K",
    "10-K/A",
    "10-KT",
    "10-KT/A",
    "10-Q",
    "10-Q/A",
    "10-QT",
    "10-QT/A",
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
)


def _as_date(value: date | datetime | str | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _reason(label: str, value_end: date, fiscal_year: int | None) -> str:
    if label in ANNUAL_LABELS:
        year = fiscal_year if fiscal_year is not None else value_end.year
        return f"not in the latest filing (last reported FY{year})"
    return f"not in the latest filing (last reported quarter ended {value_end.isoformat()})"


def staleness_reason(
    period_end: date | datetime | str | None,
    period_label: str | None,
    latest_period_end: date | datetime | str | None,
    *,
    fiscal_year: int | None = None,
) -> str | None:
    """The reason to show instead of the value, or None (not stale / cannot
    be shown stale). Pure function of three facts the caller already holds:
    the value's period end and label, and the company's latest filed period.

    `fiscal_year`, when the caller has it (company page statement rows), names
    the year in the reason; otherwise the year of the period end is used."""
    value_end = _as_date(period_end)
    latest = _as_date(latest_period_end)
    if value_end is None or latest is None or period_label is None:
        return None
    gap = (latest - value_end).days
    if period_label in ANNUAL_LABELS:
        limit = ANNUAL_MAX_GAP_DAYS
    elif period_label in QUARTERLY_LABELS:
        limit = QUARTERLY_MAX_GAP_DAYS
    else:
        return None
    if gap > limit:
        return _reason(period_label, value_end, fiscal_year)
    return None


def stale_predicate_sql(label_expr: str, end_expr: str, latest_expr: str) -> str:
    """Boolean SQL expression, true exactly when `staleness_reason` would
    return a reason for the same three inputs (dates compared with day
    arithmetic: end < latest - limit  <=>  gap > limit). Contains no
    parameters. NULL inputs give NULL, which `not (...)` does not turn true,
    so callers must write `not coalesce(<predicate>, false)`."""
    return (
        f"(case when {label_expr} = 'FY' then {end_expr} < {latest_expr} - {ANNUAL_MAX_GAP_DAYS} "
        f"when {label_expr} in ('Q1', 'Q2', 'Q3', 'Q4', 'TTM') "
        f"then {end_expr} < {latest_expr} - {QUARTERLY_MAX_GAP_DAYS} "
        f"else false end)"
    )


def latest_filed_period_sql(company_id_expr: str) -> str:
    """A scalar sub-select: the company's latest filed period end (date), for
    embedding in a query that already has the company id. No parameters."""
    forms = ", ".join(f"'{f}'" for f in PERIODIC_FORMS)
    owner = f"lf.company_id = {company_id_expr}"
    if rule_enabled(RULE_SHARED_ACCESSION_PRIMARY):
        # a registrant (primary or co-registrant) of a combined filing counts it
        owner = (
            f"(lf.company_id = {company_id_expr} or exists (select 1 from "
            "core.filing_registrant fr where fr.accession_number = lf.accession_number "
            f"and fr.company_id = {company_id_expr} and fr.role in ('primary','co_registrant')))"
        )
    return (
        "(select max(lf.period_of_report) from core.filing lf "
        f"where {owner} and lf.form in ({forms}) "
        f"and lf.period_of_report <= current_date + {FUTURE_DATE_GRACE_DAYS})"
    )


def load_latest_filed_periods(
    cur, company_ids: Iterable[int] | None = None, as_of: date | None = None
) -> dict[int, date]:
    """company_id -> latest filed period end. ONE set-based query (grouped by
    company), index-backed when `company_ids` is given, the whole population
    when None. Read-only. A company with no usable filing row is absent from
    the result, and the guard then leaves its values alone."""
    ceiling = (as_of or date.today()) + timedelta(days=FUTURE_DATE_GRACE_DAYS)
    ids = None if company_ids is None else sorted(set(company_ids))
    if ids is not None and not ids:
        return {}
    where = "company_id = any(%s::bigint[]) and " if ids is not None else ""
    params: list = ([ids] if ids is not None else []) + [list(PERIODIC_FORMS), ceiling]
    cur.execute(
        f"select company_id, max(period_of_report) from core.filing "
        f"where {where}form = any(%s) and period_of_report is not null "
        f"and period_of_report <= %s group by company_id",
        params,
    )
    out = {row[0]: row[1] for row in cur.fetchall()}
    if rule_enabled(RULE_SHARED_ACCESSION_PRIMARY):
        reg_where = "r.company_id = any(%s::bigint[]) and " if ids is not None else ""
        cur.execute(
            "select r.company_id, max(f.period_of_report) from core.filing_registrant r "
            "join core.filing f on f.accession_number = r.accession_number "
            f"where {reg_where}r.role in ('primary','co_registrant') and r.company_id is not null "
            "and f.form = any(%s) and f.period_of_report is not null "
            "and f.period_of_report <= %s group by r.company_id",
            params,
        )
        for company_id, latest in cur.fetchall():
            if company_id not in out or latest > out[company_id]:
                out[company_id] = latest
    return out


def apply_to_resolved(
    resolved: dict[tuple[int, int], dict],
    latest_by_company: dict[int, date],
) -> int:
    """In place, for the Screener's most-recent-value map: null every stale
    value and set the reason. Entries without a value are left as they are
    (a bank suppression or a stored null reason is not overwritten). Returns
    how many values were hidden."""
    changed = 0
    for (company_id, _metric_id), entry in resolved.items():
        if entry["value"] is None:
            continue
        reason = staleness_reason(
            entry.get("period_end"),
            entry.get("period_label"),
            latest_by_company.get(company_id),
        )
        if reason is not None:
            entry["value"] = None
            entry["is_null_reason"] = reason
            changed += 1
    return changed


def apply_to_metric_rows(metrics: list[dict], latest_period_end) -> list[dict]:
    """The company page's metric list (metric_name, value, period_label,
    period_end, is_null_reason): returns a new list in which every stale value
    is null with the reason. Entries already null are untouched. Input is not
    mutated. Same order as given."""
    out = []
    for m in metrics:
        reason = (
            staleness_reason(
                m.get("period_end"), m.get("period_label"), latest_period_end
            )
            if m.get("value") is not None
            else None
        )
        if reason is None:
            out.append(m)
        else:
            out.append({**m, "value": None, "is_null_reason": reason})
    return out
