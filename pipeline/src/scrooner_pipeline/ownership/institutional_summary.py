"""Institutional Ownership QoQ summary (product spec
doc/scoping/insider_info.md's "Institutional Ownership" subsection).
Consumes core.institutional_ownership's now-two-window data
(ownership/institutional.py) and computes, per company, the comparison
between its two most recent report_periods: total institutional
ownership %, QoQ change, total holders, increased/decreased/new/exited
counts, and the Top 10 holders table with per-holder status.

Lives in ownership/, not mapper/ -- this is ownership-identity-adjacent
presentation data for the Ownership page (a Top Holders table, holder
counts), not a financial-statement-derived ratio, same reasoning doc 19
already used to keep insider/beneficial_ownership/institutional out of
`analytics`. Writes to a new core table (core.institutional_ownership_summary,
0024 migration), never to `analytics` -- this module's output is not one
of doc 02's locked metrics and was never meant to be.

Total institutional ownership % reuses the exact dedup-by-filer
precedence (prefer amendment over original, else latest filing_date)
that mapper/expanded_metrics.py's _institutional_ownership_shares and
apps/site's getTopInstitutionalHolders already use, scoped additionally
to one report_period at a time (that existing helper intentionally looks
across ALL stored rows for "current" ownership; this module needs each
of the two specific quarters separately to compute a QoQ change) -- so
this module's aggregate % and Mapper's analytics.metric_value
institutional_ownership_pct can disagree only in which single snapshot
each is reporting (this: the latest of two known quarters; Mapper: all
rows on file), never in the dedup logic itself.

Shares outstanding is resolved via the exact same
_latest_instant_fact / _load_shares_outstanding_fallback building blocks
price_metrics.py and expanded_metrics.py already use for the identical
concept -- not a second source of truth. Deliberately uses ONE current
shares-outstanding value as the denominator for BOTH quarters' percentage
(this pipeline doesn't resolve historical point-in-time shares
outstanding as of an arbitrary past quarter) -- this isolates the QoQ
change to genuine institutional-holding movement rather than mixing in
share-count drift, and is called out here explicitly as a deliberate
simplification, not an oversight.

QoQ increased/decreased/new/exited matching is by filer_cik, not
filer_name, per the product spec's own instruction ("match by filer_cik,
since the same manager should file consistently") -- a manager's display
name can vary slightly release to release; its CIK doesn't. A holder row
with no resolvable filer_cik (a rare submission-lookup miss, see
institutional.py's own docstring on amendments) falls back to its
filer_name as the match key, flagged in the row itself, rather than being
silently excluded from the comparison.
"""

import json
from datetime import date
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import safe_rollback
from scrooner_pipeline.mapper.price_metrics import (
    _latest_instant_fact,
    _load_concept_ids,
    _load_shares_outstanding_fallback,
)

logger = structlog.get_logger()

TOP_HOLDERS_LIMIT = 10


def _recent_report_periods(
    conn: psycopg.Connection, company_id: int, limit: int = 2
) -> list[date]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select distinct report_period
            from core.institutional_ownership
            where company_id = %s and report_period is not null
            order by report_period desc
            limit %s
            """,
            (company_id, limit),
        )
        return [row[0] for row in cur.fetchall()]


def _period_holders(
    conn: psycopg.Connection, company_id: int, report_period: date
) -> list[dict]:
    """One row per distinct filer (by filer_cik) for a single
    report_period: picks the single authoritative FILING per filer
    (prefers an amendment's accession_number over the original, else
    latest filing_date), then SUMS every row within that one filing --
    a single Form 13F can legitimately report the same security across
    multiple separate INFOTABLE lines for one filer (different
    investment-discretion/managed-account categories), which is a real,
    additive position, not a duplicate to dedupe away.

    Fixed 2026-09-05: the original `distinct on (filer_name)` kept only
    ONE raw row per filer, silently discarding every other real
    position line for any filer with more than one -- confirmed live
    for AAPL, "BlackRock, Inc." reports 25 separate rows (all under one
    accession_number, all is_amendment=false) summing to ~$1.1B, of
    which the old query kept only the single largest ($423.9M). This
    was the dominant cause of institutional_ownership_pct reading ~36%
    for AAPL against a real-world figure of ~60-65%. See
    mapper/expanded_metrics.py's _institutional_ownership_shares (fixed
    the same way, same day) for the full diagnosis."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select max(io.filer_name) as filer_name, io.filer_cik, sum(io.shares) as shares, sum(io.value_usd) as value_usd
            from core.institutional_ownership io
            join (
                select distinct on (filer_cik) filer_cik, accession_number
                from core.institutional_ownership
                where company_id = %s and report_period = %s
                order by filer_cik, is_amendment desc, filing_date desc nulls last
            ) chosen_filing
              on chosen_filing.filer_cik = io.filer_cik
             and chosen_filing.accession_number = io.accession_number
            where io.company_id = %s and io.report_period = %s
            group by io.filer_cik
            """,
            (company_id, report_period, company_id, report_period),
        )
        return [
            {"filer_name": r[0], "filer_cik": r[1], "shares": r[2], "value_usd": r[3]}
            for r in cur.fetchall()
        ]


def _match_key(holder: dict) -> str:
    """filer_cik when resolvable, else a name-prefixed fallback so it can
    never collide with a real CIK string -- see module docstring."""
    return (
        holder["filer_cik"] if holder["filer_cik"] else f"name:{holder['filer_name']}"
    )


def _shares_outstanding_current(
    conn: psycopg.Connection, company_id: int, concept_ids: dict[str, int]
) -> Decimal | None:
    if "shares_outstanding" not in concept_ids:
        return None
    hit = _latest_instant_fact(conn, company_id, concept_ids["shares_outstanding"])
    if hit is not None:
        return hit[0]
    fallback = _load_shares_outstanding_fallback(conn, company_id)
    return fallback[0] if fallback else None


def build_institutional_summary(
    company_id: int,
    report_period_latest: date,
    report_period_prior: date,
    latest_holders: list[dict],
    prior_holders: list[dict],
    shares_out: Decimal | None,
) -> dict:
    """Pure comparison logic, no DB access -- takes already-fetched
    per-period holder lists (each a list of {filer_name, filer_cik,
    shares, value_usd} dicts, e.g. from _period_holders) and a resolved
    shares-outstanding value, and returns the full summary dict. Split out
    from compute_institutional_summary_for_company (below) so the QoQ
    comparison/Top-10/status logic is unit-testable without a live
    connection -- same pure-function-vs-DB-wrapper split
    insider_summary.py's compute_ownership_pct already established."""
    prior_by_key = {_match_key(h): h for h in prior_holders}

    total_shares_latest = sum((h["shares"] or Decimal(0)) for h in latest_holders)
    total_shares_prior = sum((h["shares"] or Decimal(0)) for h in prior_holders)

    if shares_out is None or shares_out == 0:
        total_institutional_pct = None
        total_institutional_pct_prior = None
        qoq_change_pct = None
    elif total_shares_latest > shares_out or total_shares_prior > shares_out:
        # Institutional ownership can never exceed 100% -- a result over
        # that means shares_out (this pipeline's single "current" shares
        # outstanding value, deliberately reused for both quarters -- see
        # this module's own docstring) is wrong for this company, not
        # that real ownership is implausibly high. Found live 2026-09-05
        # (NIKE): shares_outstanding has had no real authoritative
        # EntityCommonStockSharesOutstanding fact since 2015 (likely the
        # same dimensional/multi-class-share stripping already documented
        # for Block/Reddit), producing a stale, too-small denominator.
        # Null rather than show an impossible >100% figure -- see
        # mapper/expanded_metrics.py's own institutional_ownership_pct
        # guard, added the same day for the same reason.
        total_institutional_pct = None
        total_institutional_pct_prior = None
        qoq_change_pct = None
    else:
        total_institutional_pct = total_shares_latest / shares_out
        total_institutional_pct_prior = total_shares_prior / shares_out
        qoq_change_pct = total_institutional_pct - total_institutional_pct_prior

    holders_increased = holders_decreased = new_positions = 0
    for h in latest_holders:
        key = _match_key(h)
        prior = prior_by_key.get(key)
        if prior is None:
            new_positions += 1
        else:
            latest_shares, prior_shares = (
                h["shares"] or Decimal(0),
                prior["shares"] or Decimal(0),
            )
            if latest_shares > prior_shares:
                holders_increased += 1
            elif latest_shares < prior_shares:
                holders_decreased += 1
    latest_keys = {_match_key(h) for h in latest_holders}
    exited_positions = sum(1 for h in prior_holders if _match_key(h) not in latest_keys)

    top_holders = []
    for h in sorted(
        latest_holders, key=lambda h: h["shares"] or Decimal(0), reverse=True
    )[:TOP_HOLDERS_LIMIT]:
        prior = prior_by_key.get(_match_key(h))
        shares = h["shares"] or Decimal(0)
        prior_shares = prior["shares"] if prior else None
        if prior is None:
            status, share_change, pct_change = "new", None, None
        else:
            prior_shares_val = prior_shares or Decimal(0)
            share_change = shares - prior_shares_val
            pct_change = (share_change / prior_shares_val) if prior_shares_val else None
            if share_change > 0:
                status = "increased"
            elif share_change < 0:
                status = "decreased"
            else:
                status = "unchanged"
        top_holders.append(
            {
                "filer_name": h["filer_name"],
                "filer_cik": h["filer_cik"],
                "shares": str(shares),
                "value_usd": str(h["value_usd"])
                if h["value_usd"] is not None
                else None,
                "ownership_pct": str(shares / shares_out) if shares_out else None,
                "share_change": str(share_change) if prior is not None else None,
                "pct_change": str(pct_change) if pct_change is not None else None,
                "status": status,
                "report_period": report_period_latest.isoformat(),
            }
        )
    # A holder present in the prior period but not the latest one at all
    # never appears in latest_holders, so the loop above can't emit an
    # "exited" row for it -- add those explicitly so the Top 10 table can
    # show a real exited position rather than silently dropping it.
    exited_in_prior_top = [h for h in prior_holders if _match_key(h) not in latest_keys]
    for h in sorted(
        exited_in_prior_top, key=lambda h: h["shares"] or Decimal(0), reverse=True
    ):
        if len(top_holders) >= TOP_HOLDERS_LIMIT:
            break
        top_holders.append(
            {
                "filer_name": h["filer_name"],
                "filer_cik": h["filer_cik"],
                "shares": "0",
                "value_usd": "0",
                "ownership_pct": "0",
                "share_change": str(-(h["shares"] or Decimal(0))),
                "pct_change": "-1",
                "status": "exited",
                "report_period": report_period_latest.isoformat(),
            }
        )

    return {
        "company_id": company_id,
        "report_period_latest": report_period_latest,
        "report_period_prior": report_period_prior,
        "total_institutional_pct": total_institutional_pct,
        "total_institutional_pct_prior": total_institutional_pct_prior,
        "qoq_change_pct": qoq_change_pct,
        "total_holders": len(latest_holders),
        "holders_increased": holders_increased,
        "holders_decreased": holders_decreased,
        "new_positions": new_positions,
        "exited_positions": exited_positions,
        "top_holders": top_holders,
    }


def compute_institutional_summary_for_company(
    conn: psycopg.Connection, company_id: int, concept_ids: dict[str, int]
) -> dict | None:
    """Thin DB-fetching wrapper around build_institutional_summary.
    Returns None (not an error) when fewer than 2 report_periods are on
    file yet for this company -- expected for any golden company whose
    CUSIP hasn't matched in both bulk windows, not a bug."""
    periods = _recent_report_periods(conn, company_id, limit=2)
    if len(periods) < 2:
        return None
    report_period_latest, report_period_prior = periods[0], periods[1]

    latest_holders = _period_holders(conn, company_id, report_period_latest)
    prior_holders = _period_holders(conn, company_id, report_period_prior)
    shares_out = _shares_outstanding_current(conn, company_id, concept_ids)

    return build_institutional_summary(
        company_id,
        report_period_latest,
        report_period_prior,
        latest_holders,
        prior_holders,
        shares_out,
    )


def compute_institutional_ownership_summary(
    conn: psycopg.Connection, ciks: set[str]
) -> dict:
    concept_ids = _load_concept_ids(conn, {"shares_outstanding"})
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())

    totals = {
        "considered": 0,
        "no_company": 0,
        "insufficient_periods": 0,
        "errored": 0,
        "computed": 0,
    }
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            summary = compute_institutional_summary_for_company(
                conn, company_id, concept_ids
            )
        except Exception:
            # Same "one company's failure must not crash the whole batch"
            # discipline as beneficial_ownership.py/insider.py -- no
            # dedicated dead-letter table for ownership/ (unlike
            # core.normalizer_error/analytics.mapper_error), so roll back
            # and count, matching that existing local convention.
            # safe_rollback() additionally tolerates a dead connection
            # (see common/errors.py) instead of a bare conn.rollback()
            # crashing the whole remaining batch.
            logger.exception("institutional_ownership_summary.company_failed", cik=cik)
            conn = safe_rollback(conn, stage="institutional_ownership_summary", cik=cik)
            totals["errored"] += 1
            continue
        if summary is None:
            totals["insufficient_periods"] += 1
            continue
        _write_summary(conn, summary)
        totals["computed"] += 1

    logger.info("institutional_ownership_summary.done", **totals)
    return totals


def _write_summary(conn: psycopg.Connection, summary: dict) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into core.institutional_ownership_summary
                (company_id, report_period_latest, report_period_prior,
                 total_institutional_pct, total_institutional_pct_prior, qoq_change_pct,
                 total_holders, holders_increased, holders_decreased,
                 new_positions, exited_positions, top_holders)
            values
                (%(company_id)s, %(report_period_latest)s, %(report_period_prior)s,
                 %(total_institutional_pct)s, %(total_institutional_pct_prior)s, %(qoq_change_pct)s,
                 %(total_holders)s, %(holders_increased)s, %(holders_decreased)s,
                 %(new_positions)s, %(exited_positions)s, %(top_holders)s)
            on conflict (company_id) do update set
                report_period_latest = excluded.report_period_latest,
                report_period_prior = excluded.report_period_prior,
                total_institutional_pct = excluded.total_institutional_pct,
                total_institutional_pct_prior = excluded.total_institutional_pct_prior,
                qoq_change_pct = excluded.qoq_change_pct,
                total_holders = excluded.total_holders,
                holders_increased = excluded.holders_increased,
                holders_decreased = excluded.holders_decreased,
                new_positions = excluded.new_positions,
                exited_positions = excluded.exited_positions,
                top_holders = excluded.top_holders,
                computed_at = now()
            """,
            {**summary, "top_holders": json.dumps(summary["top_holders"])},
        )
        conn.commit()
