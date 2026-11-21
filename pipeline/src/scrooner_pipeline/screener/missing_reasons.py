"""Why a company has no value for a screened metric (v1, 2026-11-22).

A screener must never drop a company silently: every company a filter leaves
out for a missing value carries a reason bucket, and a filter can opt in to
keeping such companies (MetricPredicate.include_missing).

Pure part: `bucket(code)` maps a stored machine reason
(analytics.metric_value.is_null_reason, emitted by mapper/*) to one of six
buckets. The bucket names reuse the frozen reasons/model.py STATES where one
fits; `stale` and `open_gap` are screener-only. An unknown or absent code is
`open_gap` ("no value yet, our gap"): it is never dropped and never dressed
up as a legitimate blank.

DB part: `resolve_reasons(conn, pairs, dataset_version, catalog)` looks up
the reason for many (company_id, metric_name) pairs in two set-based
queries: the snapshot's own period label/end for each pair, then one join
of those pairs to analytics.metric_value (null row at that exact period) and
analytics.company_data_point_template (OUT of the company's template).
Read-only.
"""

from __future__ import annotations

import psycopg
from psycopg import sql

NOT_IN_TEMPLATE = "not_in_template"
HISTORY_HORIZON = "history_horizon"
UNDEFINED_BY_MATH = "undefined_by_math"
NOT_PRESENTED = "not_presented"
STALE = "stale"
OPEN_GAP = "open_gap"

# Display order and labels; the UI mirrors these labels.
BUCKETS: tuple[str, ...] = (
    NOT_IN_TEMPLATE,
    HISTORY_HORIZON,
    UNDEFINED_BY_MATH,
    NOT_PRESENTED,
    STALE,
    OPEN_GAP,
)
BUCKET_LABELS: dict[str, str] = {
    NOT_IN_TEMPLATE: "Not applicable to sector",
    HISTORY_HORIZON: "No prior-year filing",
    UNDEFINED_BY_MATH: "Undefined (zero or negative base)",
    NOT_PRESENTED: "Not disclosed in filings",
    STALE: "Latest value older than latest filing",
    OPEN_GAP: "No value yet (our gap)",
}

# Codes the snapshot or this module itself assigns when metric_value has nothing.
NO_ROW = "no_row"  # no metric_value row in the snapshot window at all
NO_REASON_RECORDED = "no_reason_recorded"  # a null row whose reason column is empty

_UNDEFINED_EXACT = frozenset(
    {
        "zero_denominator",
        "zero_base_value",
        "immaterial_prior_base",
        "undefined_by_math",
        "non_positive_growth_not_meaningful",
    }
)
_NOT_PRESENTED_EXACT = frozenset({"not_presented", "no_dividend_history"})


def bucket(code: str | None) -> str:
    """Map one stored reason code to its bucket. Never raises; unknown -> open_gap."""
    if code is None:
        return OPEN_GAP
    c = code.strip()
    if not c:
        return OPEN_GAP
    if c in (NOT_IN_TEMPLATE, "not_applicable") or c.startswith("not_in_template"):
        return NOT_IN_TEMPLATE
    if c.startswith("missing:prior_period"):
        return HISTORY_HORIZON
    if (
        c in _UNDEFINED_EXACT
        or c.startswith("zero_")
        or c.startswith("negative_ratio_undefined")
    ):
        return UNDEFINED_BY_MATH
    if (
        c in _NOT_PRESENTED_EXACT
        or c.startswith("incomplete:")
        or c.startswith("not filed separately")
    ):
        return NOT_PRESENTED
    if c == STALE or c.startswith("stale"):
        return STALE
    return OPEN_GAP


def reason_entry(code: str | None, bucket_name: str | None = None) -> dict:
    b = bucket_name or bucket(code)
    return {"code": code, "bucket": b, "label": BUCKET_LABELS[b]}


def resolve_reasons(
    conn: psycopg.Connection,
    pairs: list[tuple[int, str]],
    dataset_version: int,
    catalog: dict[str, int],
) -> dict[tuple[int, str], dict]:
    """Reason entry for every (company_id, metric_name) pair, in two queries.

    Precedence: template OUT, then the metric_value null row's own reason at
    the snapshot's period, then open_gap (no_row when the snapshot has no
    period for the pair at all, else no_reason_recorded)."""
    pairs = sorted({p for p in pairs if p[1] in catalog})
    if not pairs:
        return {}
    company_ids = sorted({cid for cid, _ in pairs})
    names = sorted({name for _, name in pairs})
    columns = [sql.Identifier("company_id")]
    for name in names:
        columns += [
            sql.Identifier(f"{name}__period_label"),
            sql.Identifier(f"{name}__period_end"),
        ]
    statement = sql.SQL(
        "select {} from analytics.company_screening_snapshot "
        "where dataset_version = %s and company_id = any(%s::bigint[])"
    ).format(sql.SQL(", ").join(columns))
    with conn.cursor() as cur:
        cur.execute(statement, (dataset_version, company_ids))
        snapshot_rows = cur.fetchall()
    periods: dict[tuple[int, str], tuple] = {}
    for row in snapshot_rows:
        for i, name in enumerate(names):
            periods[(row[0], name)] = (row[1 + 2 * i], row[2 + 2 * i])

    cids, mids, mnames, labels, ends = [], [], [], [], []
    for cid, name in pairs:
        label, end = periods.get((cid, name), (None, None))
        cids.append(cid)
        mids.append(catalog[name])
        mnames.append(name)
        labels.append(label)
        ends.append(end)
    with conn.cursor() as cur:
        cur.execute(
            """
            select t.cid, t.mname, tpl.reason as template_reason,
                   (tpl.company_id is not null) as is_out, mv.is_null_reason
            from unnest(%s::bigint[], %s::bigint[], %s::text[], %s::text[], %s::date[])
                 as t(cid, mid, mname, pl, pe)
            left join lateral (
                select x.company_id, x.reason
                from analytics.company_data_point_template x
                where x.company_id = t.cid and x.data_point = t.mname
                  and x.in_template is false
                  and x.effective_from = (
                      select max(y.effective_from) from analytics.company_data_point_template y
                      where y.company_id = t.cid and y.effective_from <= current_date)
                limit 1
            ) tpl on true
            left join lateral (
                select v.is_null_reason
                from analytics.metric_value v
                where v.company_id = t.cid and v.metric_definition_id = t.mid
                  and v.period_label = t.pl and v.period_end = t.pe
                  and v.value is null and v.is_null_reason is not null
                order by v.is_null_reason
                limit 1
            ) mv on true
            """,
            (cids, mids, mnames, labels, ends),
        )
        found = {(r[0], r[1]): (r[2], r[3], r[4]) for r in cur.fetchall()}

    out: dict[tuple[int, str], dict] = {}
    for cid, name in pairs:
        template_reason, is_out, null_reason = found.get(
            (cid, name), (None, False, None)
        )
        if is_out:
            out[(cid, name)] = reason_entry(
                template_reason or NOT_IN_TEMPLATE, NOT_IN_TEMPLATE
            )
        elif null_reason:
            out[(cid, name)] = reason_entry(null_reason)
        elif periods.get((cid, name), (None, None))[0] is None:
            out[(cid, name)] = reason_entry(NO_ROW, OPEN_GAP)
        else:
            out[(cid, name)] = reason_entry(NO_REASON_RECORDED, OPEN_GAP)
    return out
