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

from scrooner_pipeline.collector.filings import collect_daily_filings
from scrooner_pipeline.collector.identity import get_all_ciks
from scrooner_pipeline.collector.retry import finish_run, start_or_resume_run
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
        logger.exception("collector_runs.finish_run_failed", run_id=run_id, intended_status=status)


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
    walking backward. A 404 means SEC published no index for that date
    (weekend/holiday) -- doc 07 says nothing about EDGAR's holiday
    calendar, so this discovers it live rather than hardcoding one.
    """
    from scrooner_pipeline.collector.filings import daily_index_url
    from scrooner_pipeline.common.sec_client import SECClient

    candidate = date.today() - timedelta(days=1)
    with SECClient() as sec:
        for _ in range(max_lookback_days):
            try:
                sec.get(daily_index_url(candidate))
                return candidate
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code != 404:
                    raise
                candidate -= timedelta(days=1)
    raise RuntimeError(
        f"no published daily index found in the last {max_lookback_days} days -- "
        "unexpected outside a long SEC outage; check doc 07 section5's URL is still correct"
    )


@app.command()
def daily(
    date_str: str = typer.Option(
        None, "--date", help="YYYY-MM-DD to fetch. Default: most recent date with a published index."
    ),
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: all of raw.company_universe)."
    ),
    fresh: bool = typer.Option(False, help="Ignore any resumable run and start a brand-new one."),
) -> None:
    """Fetch one day's SEC daily index and record genuinely-new filing
    metadata into raw.sec_filing_documents. Rerunning for the SAME date is
    idempotent -- see collector/filings.py's ON CONFLICT DO NOTHING design;
    that's what makes this safe to run daily on a schedule without
    duplicating anything, and what today's verification actually tests."""
    target_date = _parse_date(date_str) or _most_recent_published_date()
    explicit_ciks = _parse_ciks(ciks)

    with get_connection() as conn:
        only_ciks = explicit_ciks if explicit_ciks is not None else set(get_all_ciks(conn))
        typer.echo(f"target_date={target_date.isoformat()} scope={'explicit ciks' if explicit_ciks is not None else f'company_universe ({len(only_ciks)} ciks)'}")

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
            stats = collect_daily_filings(conn, for_date=target_date, run_id=ctx.run_id, only_ciks=only_ciks)
            finish_run(conn, ctx.run_id, "succeeded", stats)
        except Exception:
            _finish_run_safely(ctx.run_id, "failed", {})
            raise
    typer.echo(f"filings: {stats} (run_id={ctx.run_id}, resumed={ctx.resumed})")


if __name__ == "__main__":
    app()
