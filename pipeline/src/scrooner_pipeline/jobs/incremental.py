"""Typer CLI: daily/scheduled catch-up (doc 08 Day 5). Fetches SEC's daily
index for a single date and records genuinely-new filing metadata into
raw.sec_filing_documents. See collector/filings.py's module docstring for
the scope decision (CIKs filtered to raw.company_universe by default) and
the idempotency design (ON CONFLICT DO NOTHING on (cik, accession_number)
is what "genuinely new" means here).

Timing-interpretation decision (doc/learnings/day-05-incremental-updates.md
has the full reasoning): doc 08's "Done when" text says "running it a day
after bootstrap finds only genuinely new filings" -- this session cannot
literally wait a day, so the test is: run once against a real recent PAST
date (index is finalized/immutable once published, unlike "today" which
may still be accumulating filings), confirm the results are plausible
against live EDGAR; run the identical command again for the SAME date and
confirm zero new rows the second time. That's a real, live proxy for "does
not reprocess/duplicate" without needing to wait 24 hours.
"""

from datetime import date, datetime, timedelta

import httpx
import structlog
import typer

from scrooner_pipeline.collector.companyfacts import bootstrap_companyfacts
from scrooner_pipeline.collector.filings import collect_daily_filings
from scrooner_pipeline.collector.identity import get_all_ciks
from scrooner_pipeline.collector.retry import finish_run, start_or_resume_run
from scrooner_pipeline.collector.submissions import bootstrap_submissions
from scrooner_pipeline.db.connection import get_connection

app = typer.Typer()
logger = structlog.get_logger()


def _finish_run_safely(run_id: int, status: str, stats: dict) -> None:
    """Same rationale as jobs/bootstrap.py's _finish_run_safely -- see
    doc/learnings/day-04-retry-and-resume.md. A short-lived incremental run
    is much less likely to hit a stale-connection failure than a 30-minute
    bulk download, but the fix is cheap and this keeps both jobs' failure
    paths consistent rather than one being safe and the other not."""
    try:
        with get_connection() as fresh_conn:
            finish_run(fresh_conn, run_id, status, stats)
    except Exception:
        logger.exception(
            "collector_runs.finish_run_failed", run_id=run_id, intended_status=status
        )


def _parse_ciks(ciks: str | None) -> set[str] | None:
    if not ciks:
        return None
    return {c.strip().zfill(10) for c in ciks.split(",") if c.strip()}


def _parse_date(date_str: str | None) -> date | None:
    if not date_str:
        return None
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def _most_recent_published_date(max_lookback_days: int = 10) -> date:
    """Default target when --date isn't given: the most recent date with a
    published daily index, starting from YESTERDAY (not today -- today's
    index may still be accumulating filings intraday and doc 07 says
    nothing about a partial-day snapshot being safe to treat as final) and
    walking backward. A missing index (weekend/holiday) means SEC
    published nothing for that date -- doc 07 says nothing about EDGAR's
    holiday calendar, so this discovers it live rather than hardcoding one.

    Found live 2026-09-08 (this cron had been crashing daily for 10+ days,
    silently -- GitHub Actions marks it failed but nobody was watching the
    red X): SEC serves a missing daily-index file as 403 Forbidden, not
    404 -- confirmed live against real dates (both weekend days in a row
    returned 403; the preceding real business day returned a clean 200),
    almost certainly an S3-backed "no ListBucket permission" response
    rather than a clean not-found. The original code only treated 404 as
    "not published yet, try an earlier day" and re-raised everything else
    -- so every single lookback hit this on its very first candidate
    (yesterday, always a real business day in this cron's failure history,
    but the SAME 403 pattern) and crashed instead of walking back further.
    Both status codes now treated identically."""
    from scrooner_pipeline.collector.filings import daily_index_url
    from scrooner_pipeline.common.sec_client import SECClient

    NOT_PUBLISHED_STATUS_CODES = (404, 403)

    candidate = date.today() - timedelta(days=1)
    with SECClient() as sec:
        for _ in range(max_lookback_days):
            try:
                sec.get(daily_index_url(candidate))
                return candidate
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code not in NOT_PUBLISHED_STATUS_CODES:
                    raise
                candidate -= timedelta(days=1)
    raise RuntimeError(
        f"no published daily index found in the last {max_lookback_days} days -- "
        "unexpected outside a long SEC outage; check doc 07 section5's URL is still correct"
    )


@app.command()
def daily(
    date_str: str = typer.Option(
        None,
        "--date",
        help="YYYY-MM-DD to fetch. Default: most recent date with a published index.",
    ),
    ciks: str = typer.Option(
        None,
        help="Comma-separated CIKs to restrict to (default: all of raw.company_universe).",
    ),
    fresh: bool = typer.Option(
        False, help="Ignore any resumable run and start a brand-new one."
    ),
) -> None:
    """Fetch one day's SEC daily index and record genuinely-new filing
    metadata into raw.sec_filing_documents. Rerunning for the SAME date is
    idempotent -- see collector/filings.py's ON CONFLICT DO NOTHING design;
    that's what makes this safe to run daily on a schedule without
    duplicating anything, and what today's verification actually tests.

    Also refreshes raw.sec_companyfacts/raw.sec_submissions for whichever
    CIKs actually filed something on target_date (added 2026-09-08, found
    live: this command's own docstring only ever promised the filing
    INDEX, so companyfacts/submissions for existing companies were never
    refreshed by anything, ever -- scrooner-operations's freshness gate
    for both had been alerting every single day with no way to clear,
    because nothing kept its promise current). Reuses the same bulk-
    archive bootstrap functions jobs/bootstrap.py's own commands call,
    scoped via only_ciks to just today's filers rather than the whole
    ~5,200-company population -- correct, since a company that didn't
    file anything today has nothing new to refresh.

    Measured live 2026-09-08 against a real 25-CIK/66-file sample: ~85s
    of real work, extrapolating to up to ~45min for a typical ~800-filer
    day (submissions files include every historical continuation page
    for a company with a long filing history, e.g. JPMorgan alone has
    70+) -- the cron's own job timeout was raised to 90min for headroom.
    Known, accepted gap, not yet solved: if a day's run times out
    partway through submissions, the CIKs it didn't reach are NOT
    retried tomorrow (tomorrow's only_ciks is a different day's filers,
    not a backlog queue) -- that company's submissions just stay stale
    until it files something else. Acceptable for now (an actively-
    reporting company files again within a quarter, well inside the
    7-day alert target's own slack), but a real backlog/retry queue
    would close it properly if this proves to matter in practice."""
    target_date = _parse_date(date_str) or _most_recent_published_date()
    explicit_ciks = _parse_ciks(ciks)

    with get_connection() as conn:
        only_ciks = (
            explicit_ciks if explicit_ciks is not None else set(get_all_ciks(conn))
        )
        typer.echo(
            f"target_date={target_date.isoformat()} scope={'explicit ciks' if explicit_ciks is not None else f'company_universe ({len(only_ciks)} ciks)'}"
        )

        ctx = start_or_resume_run(
            conn,
            job="incremental",
            only_ciks=explicit_ciks,  # params_key reflects the CALLER's scope, not the resolved company_universe set (which changes over time and shouldn't affect resumability)
            limit=None,
            force_fresh=fresh,
            run_type="incremental",
            extra_params=f"date={target_date.isoformat()}",
        )
        typer.echo(f"run_id={ctx.run_id} resumed={ctx.resumed}")
        try:
            stats = collect_daily_filings(
                conn, for_date=target_date, run_id=ctx.run_id, only_ciks=only_ciks
            )
            finish_run(conn, ctx.run_id, "succeeded", stats)
        except Exception:
            _finish_run_safely(ctx.run_id, "failed", {})
            raise
    typer.echo(f"filings: {stats} (run_id={ctx.run_id}, resumed={ctx.resumed})")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select distinct cik from raw.sec_filing_documents where filing_date = %s",
                (target_date,),
            )
            todays_filer_ciks = {row[0] for row in cur.fetchall()}
        typer.echo(f"todays_filers={len(todays_filer_ciks)}")
        if not todays_filer_ciks:
            return

        cf_ctx = start_or_resume_run(
            conn,
            job="companyfacts",
            only_ciks=todays_filer_ciks,
            limit=None,
            force_fresh=fresh,
        )
        try:
            cf_stats = bootstrap_companyfacts(
                conn,
                fetched_at=cf_ctx.fetched_at,
                run_id=cf_ctx.run_id,
                only_ciks=todays_filer_ciks,
            )
            finish_run(conn, cf_ctx.run_id, "succeeded", cf_stats)
        except Exception:
            _finish_run_safely(cf_ctx.run_id, "failed", {})
            raise
        typer.echo(f"companyfacts: {cf_stats} (run_id={cf_ctx.run_id})")

        sub_ctx = start_or_resume_run(
            conn,
            job="submissions",
            only_ciks=todays_filer_ciks,
            limit=None,
            force_fresh=fresh,
        )
        try:
            sub_stats = bootstrap_submissions(
                conn,
                fetched_at=sub_ctx.fetched_at,
                run_id=sub_ctx.run_id,
                only_ciks=todays_filer_ciks,
            )
            finish_run(conn, sub_ctx.run_id, "succeeded", sub_stats)
        except Exception:
            _finish_run_safely(sub_ctx.run_id, "failed", {})
            raise
        typer.echo(f"submissions: {sub_stats} (run_id={sub_ctx.run_id})")


if __name__ == "__main__":
    app()
