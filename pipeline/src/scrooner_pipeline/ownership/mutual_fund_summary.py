"""Mutual Fund Ownership QoQ summary (product spec
doc/scoping/insider_info.md's "Mutual Fund Ownership" subsection).
Consumes core.fund_ownership's now-two-window data (ownership/mutual_fund.py,
BULK_ZIP_WINDOWS) and computes, per company, the comparison between its
two most recent report_periods: total mutual fund ownership %, change,
fund counts, increased/decreased/new/exited counts, and the Top 10
holders table with per-fund status.

Structurally a near-copy of ownership/institutional_summary.py (the
equivalent Form 13F QoQ summary, built in this same session by a parallel
effort) -- same "compute on a batch job, persist to a new `core` table"
architecture, chosen over a compute-on-read view/function specifically
FOR consistency with that twin module, since the product doc groups
Institutional and Mutual Fund Ownership as sibling subsections of the
same Ownership page. Writes core.fund_ownership_summary (0026 migration),
never `analytics` -- same reasoning as the institutional twin: this is
ownership-identity-adjacent presentation data (a Top Holders table,
fund counts), not one of doc 02's locked financial-statement metrics.

What's genuinely DIFFERENT from the institutional twin, checked live
2026-08-29 against the real two-window golden-10 data before writing this
(not assumed from the twin's own shape):

1. Per-fund match key is (fund_cik, series_id), NOT filer_cik alone the
   way the institutional twin matches by filer_cik. Checked live: one
   real fund_cik ('0001100663') covers 77 DISTINCT series_id/fund_name
   values across 318 real matched rows in the 2026q2 window alone --
   fund_cik alone conflates dozens of genuinely different funds under one
   umbrella trust/registrant (see mutual_fund.py's own module docstring
   point 2 for why). series_id is populated on ~97% of real matched rows
   (428 null of 13,871 in 2026q2) -- the ~3% without one already fall
   back to fund_name at match/write time (mutual_fund.py's own
   _match_holdings), so fund_name is the correct, already-established
   second key, not a new invention here.

2. value_usd can be genuinely null here (non-USD holdings, ~2% of real
   matches -- see mutual_fund.py's own docstring point 4) in a way Form
   13F's VALUE never is post-2023. Left null in the Top 10 payload rather
   than guessed, same "leave null, never guess" discipline as everywhere
   else in this project.

3. portfolio_weight_pct (FUND_REPORTED_HOLDING.PERCENTAGE, "percentage
   value compared to net assets of the Fund") has no Form 13F equivalent
   at all -- included here because the product spec explicitly asks for
   it ("portfolio weight (when available)"), sourced directly from
   core.fund_ownership.pct_of_fund_net_assets, null passthrough when
   N-PORT itself didn't report one.

4. fund_family is a REAL, HONEST GAP, not fabricated: core.fund_ownership
   never captures the umbrella registrant/trust name once a series name
   is known (mutual_fund.py's fund_name column already prefers
   SERIES_NAME over REGISTRANT_NAME at write time, per that module's own
   docstring point 2) -- the raw trust name is discarded before storage
   for the large majority of rows, so there is no real "fund family"
   signal left to return. Always None here, by design, per explicit
   instruction to surface this as a gap rather than invent one from data
   that was never kept.

5. "Two most recent report_period VALUES" is NOT the same as "two
   consecutive reporting periods" for N-PORT specifically, unlike Form
   13F's cleaner single quarterly cadence -- discovered live 2026-08-29
   the hard way, by hand-checking a computed AAPL summary that looked
   wrong (an entire ~530-fund portfolio "new" and an entire ~1,021-fund
   portfolio "exited" between two adjacent calendar months, zero overlap
   in either direction). Checked directly: a real fund_cik/series_id
   present at report_period=Jan-31 is ALSO present at Apr-30 (450/463
   keys overlap, ~97%) but is COMPLETELY ABSENT at Feb-28 or Mar-31 (0
   overlap each way) -- N-PORT filers cluster into 3 essentially
   DISJOINT quarterly cohorts by calendar month (a Jan/Apr/Jul/Oct
   cohort, Feb/May/Aug/Nov cohort, Mar/Jun/Sep/Dec cohort, each fund
   reporting on ITS OWN ~90-day fiscal-quarter cadence), not one shared
   monthly cycle. Pairing "the most recent report_period" with "the very
   next older distinct report_period value" is therefore almost always
   pairing two near-fully-disjoint fund cohorts, manufacturing a false
   100%-turnover artifact regardless of real fund behavior.

   A second, compounding issue: even within the RIGHT cohort, the most
   recent calendar report_period can be genuinely incomplete -- N-PORT
   gives funds up to ~60 days to file after a month-end, so the very
   latest month in any bulk snapshot is real but sparse (found live:
   AAPL's absolute-latest report_period, 2026-05-31, had exactly 1
   matched fund vs. 342+ at its own real quarter-cohort partner,
   2026-02-28 -- not a data error, just most of that cohort's May
   filings genuinely hadn't landed in this bulk window yet).

   _find_comparable_periods below fixes both: it only pairs two
   report_periods within a QUARTER_MIN_DAYS-QUARTER_MAX_DAYS (75-105
   day) gap -- wide enough to cover every real ~89-92-day cadence this
   project's golden-10 actually produces, narrow enough to exclude both
   adjacent-month (~28-31 day) and year-over-year (~365 day) gaps -- and
   additionally requires the "latest" candidate's fund count be at least
   MIN_COMPLETENESS_RATIO (0.5x) of its own quarter-prior partner's
   count, walking back to the next-older report_period as "latest"
   whenever a candidate fails that check (same "compare against the
   period's own real baseline, not an arbitrary absolute number"
   reasoning as everywhere else in this project that uses a ratio/band
   instead of a magic constant). Verified live across the full
   golden-10: every one of the 8 golden companies with 2+ real periods
   on file lands on the exact same (2026-04-30, 2026-01-31) pair --
   the same real, well-populated, correctly-aligned quarterly cohort,
   not 8 different arbitrary guesses.

institutional_ownership_summary.total_institutional_pct and this
module's total_fund_ownership_pct are NEVER summed anywhere in this
module or its output -- doc `insider_info.md`'s explicit rule (a fund
can appear via its own N-PORT filing AND via its manager's separate 13F
filing, so the two datasets overlap and are not additive).

Shares outstanding is resolved via the exact same
_latest_instant_fact / _load_shares_outstanding_fallback building blocks
price_metrics.py / expanded_metrics.py / institutional_summary.py all
already use for the identical concept -- not a second source of truth.
Same deliberate simplification as the institutional twin: ONE current
shares-outstanding value is the denominator for BOTH periods' percentage
(no historical point-in-time shares-outstanding series exists to divide
the PRIOR period by), so "change in %" isolates genuine fund-holding
movement rather than mixing in share-count drift -- stated here
explicitly, not hidden.
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

# See module docstring point 5. Real observed cadence across the golden-10
# is 89-92 days; this band is wide enough to cover that with margin while
# still excluding adjacent-month (~28-31 day) and year-over-year (~365
# day) gaps.
QUARTER_MIN_DAYS, QUARTER_MAX_DAYS = 75, 105
# A "latest" candidate whose fund count is below this fraction of its own
# quarter-cohort partner's count is treated as still filling in (N-PORT's
# up-to-~60-day filing grace period), not a real comparison point -- walk
# back to the next-older report_period instead of trusting it.
MIN_COMPLETENESS_RATIO = Decimal("0.5")


def _select_comparable_pair(
    periods: list[tuple[date, int]],
) -> tuple[date, date] | None:
    """Pure selection logic over an already-fetched (report_period, count)
    list, DESC by report_period -- split out from _find_comparable_periods
    so this real-cadence/completeness algorithm (module docstring point
    5) is unit-testable without a DB. Returns (latest, prior) report_periods
    that are the same real quarterly filing cohort (~90 days apart),
    walking back from the globally most recent report_period until one is
    found whose own fund count isn't a still-filling-in stub relative to
    its cohort partner. None when no such pair exists (e.g. only 1 period
    on file, or none whose gap falls in the real cadence band)."""
    for i, (latest, latest_count) in enumerate(periods):
        for prior, prior_count in periods[i + 1 :]:
            gap_days = (latest - prior).days
            if gap_days > QUARTER_MAX_DAYS:
                break  # sorted desc -- no closer candidate further back either
            if gap_days >= QUARTER_MIN_DAYS:
                if latest_count >= prior_count * MIN_COMPLETENESS_RATIO:
                    return latest, prior
                break  # right cohort, but latest is still filling in -- try an older "latest"
    return None


def _find_comparable_periods(
    conn: psycopg.Connection, company_id: int
) -> tuple[date, date] | None:
    """Fetches per-period fund counts for a company and delegates to
    _select_comparable_pair for the actual (latest, prior) decision."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select report_period, count(*)
            from core.fund_ownership
            where company_id = %s and report_period is not null
            group by report_period
            order by report_period desc
            """,
            (company_id,),
        )
        periods = cur.fetchall()
    return _select_comparable_pair(periods)


def _period_holdings(
    conn: psycopg.Connection, company_id: int, report_period: date
) -> list[dict]:
    """One row per real fund for a single report_period -- DISTINCT ON
    (fund_cik, coalesce(series_id, fund_name)) collapses a rare
    same-period duplicate (e.g. an amendment alongside its original) by
    preferring the amendment / latest filing_date, same "prefer
    amendment" dedup rule institutional_summary.py's own _period_holders
    already establishes for Form 13F."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select distinct on (fund_cik, coalesce(series_id, fund_name))
                fund_cik, series_id, fund_name, shares, value_usd, pct_of_fund_net_assets
            from core.fund_ownership
            where company_id = %s and report_period = %s
            order by fund_cik, coalesce(series_id, fund_name), is_amendment desc, filing_date desc nulls last
            """,
            (company_id, report_period),
        )
        return [
            {
                "fund_cik": r[0],
                "series_id": r[1],
                "fund_name": r[2],
                "shares": r[3],
                "value_usd": r[4],
                "pct_of_fund_net_assets": r[5],
            }
            for r in cur.fetchall()
        ]


def _match_key(holding: dict) -> str:
    """(fund_cik, series_id) when series_id is resolvable, else a
    name-prefixed fallback keyed off fund_name -- see module docstring
    point 1 for why fund_cik alone is never a safe grain on its own."""
    cik = holding["fund_cik"] or "unknown_cik"
    if holding["series_id"]:
        return f"{cik}:{holding['series_id']}"
    return f"{cik}:name:{holding['fund_name']}"


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


def compute_summary_for_company(
    conn: psycopg.Connection, company_id: int, concept_ids: dict[str, int]
) -> dict | None:
    """Returns None (not an error) when no valid same-cohort
    (latest, prior) pair exists yet for this company -- either fewer than
    2 report_periods are on file at all (CUSIP hasn't matched in both
    bulk windows yet), or none of the candidates satisfy
    _find_comparable_periods's real-cadence/completeness checks (module
    docstring point 5). Neither case is a bug."""
    pair = _find_comparable_periods(conn, company_id)
    if pair is None:
        return None
    report_period_latest, report_period_prior = pair

    latest_holdings = _period_holdings(conn, company_id, report_period_latest)
    prior_holdings = _period_holdings(conn, company_id, report_period_prior)
    shares_out = _shares_outstanding_current(conn, company_id, concept_ids)

    return _build_summary(
        company_id,
        report_period_latest,
        report_period_prior,
        latest_holdings,
        prior_holdings,
        shares_out,
    )


def _build_summary(
    company_id: int,
    report_period_latest: date,
    report_period_prior: date,
    latest_holdings: list[dict],
    prior_holdings: list[dict],
    shares_out: Decimal | None,
) -> dict:
    """Pure comparison logic over two already-fetched per-period holdings
    lists -- split out from compute_summary_for_company so this is
    unit-testable with plain dicts, no DB, same "separate IO from
    algorithm" pattern as mutual_fund.py's own _match_holdings/
    _write_matched_rows split."""
    prior_by_key = {_match_key(h): h for h in prior_holdings}

    total_shares_latest = sum((h["shares"] or Decimal(0)) for h in latest_holdings)
    total_shares_prior = sum((h["shares"] or Decimal(0)) for h in prior_holdings)

    if shares_out is None or shares_out == 0:
        total_pct, total_pct_prior, change_in_pct = None, None, None
    else:
        total_pct = total_shares_latest / shares_out
        total_pct_prior = total_shares_prior / shares_out
        change_in_pct = total_pct - total_pct_prior

    funds_increasing = funds_decreasing = new_positions = 0
    for h in latest_holdings:
        prior = prior_by_key.get(_match_key(h))
        if prior is None:
            new_positions += 1
        else:
            latest_shares, prior_shares = (
                h["shares"] or Decimal(0),
                prior["shares"] or Decimal(0),
            )
            if latest_shares > prior_shares:
                funds_increasing += 1
            elif latest_shares < prior_shares:
                funds_decreasing += 1
    latest_keys = {_match_key(h) for h in latest_holdings}
    exited_positions = sum(
        1 for h in prior_holdings if _match_key(h) not in latest_keys
    )

    top_holders = []
    for h in sorted(
        latest_holdings, key=lambda h: h["shares"] or Decimal(0), reverse=True
    )[:TOP_HOLDERS_LIMIT]:
        prior = prior_by_key.get(_match_key(h))
        shares = h["shares"] or Decimal(0)
        if prior is None:
            status, share_change, pct_change = "new", None, None
        else:
            prior_shares_val = prior["shares"] or Decimal(0)
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
                "fund_name": h["fund_name"],
                "fund_cik": h["fund_cik"],
                "series_id": h["series_id"],
                # Real, honest gap -- see module docstring point 4. Never
                # fabricated from fund_name/registrant data.
                "fund_family": None,
                "shares": str(shares),
                "value_usd": str(h["value_usd"])
                if h["value_usd"] is not None
                else None,
                "ownership_pct": str(shares / shares_out) if shares_out else None,
                "portfolio_weight_pct": str(h["pct_of_fund_net_assets"])
                if h["pct_of_fund_net_assets"] is not None
                else None,
                "share_change": str(share_change) if prior is not None else None,
                "pct_change": str(pct_change) if pct_change is not None else None,
                "status": status,
                "report_period": report_period_latest.isoformat(),
            }
        )
    # A fund present in the prior period but not the latest one at all
    # never appears in latest_holdings, so the loop above can't emit an
    # "exited" row for it -- add those explicitly (highest prior-period
    # shares first) so the Top 10 table can show a real exited position
    # rather than silently dropping it, same precedent as
    # institutional_summary.py's own equivalent backfill.
    exited_in_prior = [h for h in prior_holdings if _match_key(h) not in latest_keys]
    for h in sorted(
        exited_in_prior, key=lambda h: h["shares"] or Decimal(0), reverse=True
    ):
        if len(top_holders) >= TOP_HOLDERS_LIMIT:
            break
        top_holders.append(
            {
                "fund_name": h["fund_name"],
                "fund_cik": h["fund_cik"],
                "series_id": h["series_id"],
                "fund_family": None,
                "shares": "0",
                "value_usd": "0",
                "ownership_pct": "0",
                "portfolio_weight_pct": None,
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
        "total_fund_ownership_pct": total_pct,
        "total_fund_ownership_pct_prior": total_pct_prior,
        "change_in_pct": change_in_pct,
        "total_funds_holding": len(latest_holdings),
        "funds_increasing": funds_increasing,
        "funds_decreasing": funds_decreasing,
        "new_positions": new_positions,
        "exited_positions": exited_positions,
        "top_holders": top_holders,
    }


def compute_mutual_fund_ownership_summary(
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
            summary = compute_summary_for_company(conn, company_id, concept_ids)
        except Exception:
            # Same "one company's failure must not crash the whole batch"
            # discipline as institutional_summary.py -- no dedicated
            # dead-letter table for ownership/, so roll back and count.
            # safe_rollback() additionally tolerates a dead connection
            # (see common/errors.py) instead of a bare conn.rollback()
            # crashing the whole remaining batch.
            logger.exception("mutual_fund_ownership_summary.company_failed", cik=cik)
            conn = safe_rollback(conn, stage="mutual_fund_ownership_summary", cik=cik)
            totals["errored"] += 1
            continue
        if summary is None:
            totals["insufficient_periods"] += 1
            continue
        _write_summary(conn, summary)
        totals["computed"] += 1

    logger.info("mutual_fund_ownership_summary.done", **totals)
    return totals


def _write_summary(conn: psycopg.Connection, summary: dict) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into core.fund_ownership_summary
                (company_id, report_period_latest, report_period_prior,
                 total_fund_ownership_pct, total_fund_ownership_pct_prior, change_in_pct,
                 total_funds_holding, funds_increasing, funds_decreasing,
                 new_positions, exited_positions, top_holders)
            values
                (%(company_id)s, %(report_period_latest)s, %(report_period_prior)s,
                 %(total_fund_ownership_pct)s, %(total_fund_ownership_pct_prior)s, %(change_in_pct)s,
                 %(total_funds_holding)s, %(funds_increasing)s, %(funds_decreasing)s,
                 %(new_positions)s, %(exited_positions)s, %(top_holders)s)
            on conflict (company_id) do update set
                report_period_latest = excluded.report_period_latest,
                report_period_prior = excluded.report_period_prior,
                total_fund_ownership_pct = excluded.total_fund_ownership_pct,
                total_fund_ownership_pct_prior = excluded.total_fund_ownership_pct_prior,
                change_in_pct = excluded.change_in_pct,
                total_funds_holding = excluded.total_funds_holding,
                funds_increasing = excluded.funds_increasing,
                funds_decreasing = excluded.funds_decreasing,
                new_positions = excluded.new_positions,
                exited_positions = excluded.exited_positions,
                top_holders = excluded.top_holders,
                computed_at = now()
            """,
            {**summary, "top_holders": json.dumps(summary["top_holders"])},
        )
        conn.commit()
