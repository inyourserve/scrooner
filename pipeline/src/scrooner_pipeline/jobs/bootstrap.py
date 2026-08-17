"""Typer CLI: one-time bulk load. Day 2 wired up company-universe
collection; Day 3 added bulk companyfacts/submissions collection. Day 4
replaces the plain start/finish run bookkeeping with
collector.retry.start_or_resume_run: each command's run is identified by
(job, params), so killing the process mid-run and rerunning the exact same
command resumes the same raw.collector_runs row (same run_id, same
fetched_at) instead of starting a fresh one -- companyfacts.py/
submissions.py then skip everything already checkpointed under that
run_id. See collector/retry.py's module docstring and
doc/learnings/day-04-retry-and-resume.md for the full design.
"""

import json
from datetime import timedelta
from pathlib import Path

import structlog
import typer

from scrooner_pipeline.collector.companyfacts import bootstrap_companyfacts
from scrooner_pipeline.collector.retry import finish_run, reap_stale_runs, start_or_resume_run
from scrooner_pipeline.collector.submissions import bootstrap_submissions
from scrooner_pipeline.collector.universe import collect_company_universe
from scrooner_pipeline.db.connection import get_connection

app = typer.Typer()
logger = structlog.get_logger()

GOLDEN_COMPANIES_PATH = Path(__file__).resolve().parents[3] / "tests" / "golden_companies" / "companies.json"


def _load_golden_ciks() -> set[str]:
    companies = json.loads(GOLDEN_COMPANIES_PATH.read_text())
    return {c["cik"] for c in companies}


def _parse_ciks(ciks: str | None) -> set[str] | None:
    if not ciks:
        return None
    return {c.strip().zfill(10) for c in ciks.split(",") if c.strip()}


def _finish_run_safely(run_id: int, status: str, stats: dict) -> None:
    """finish_run, but on a FRESH connection, not whatever `conn` the caller
    was using. Found the hard way (2026-08-14, see
    doc/learnings/day-04-retry-and-resume.md): a companyfacts run whose
    connection sat idle through a ~30-minute bulk download had gone stale
    by the time SEC's server dropped the transfer and the except block
    tried to record the failure -- OperationalError on the SAME connection
    masked the real error (a RemoteProtocolError from SEC) and left the run
    stuck at status='running' instead of 'failed'. Recording a failure must
    never depend on a connection that's been idle through a long operation.

    If even this fails, log it and swallow it -- never let a
    failed-to-record-the-failure error replace the original exception
    the caller is about to re-raise.
    """
    try:
        with get_connection() as fresh_conn:
            finish_run(fresh_conn, run_id, status, stats)
    except Exception:
        logger.exception("collector_runs.finish_run_failed", run_id=run_id, intended_status=status)


@app.command()
def universe() -> None:
    """Fetch SEC's company_tickers.json and populate raw.company_universe."""
    with get_connection() as conn:
        count = collect_company_universe(conn)
    typer.echo(f"company_universe: upserted {count} (cik, ticker) rows")


@app.command()
def companyfacts(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: full universe)."),
    limit: int = typer.Option(None, help="Stop after N companies stored."),
    fresh: bool = typer.Option(False, help="Ignore any resumable run and start a brand-new one."),
) -> None:
    """Bootstrap raw.sec_companyfacts from the bulk companyfacts.zip archive.
    Rerunning after a kill mid-run resumes the same run automatically
    (same ciks/limit => same job) rather than re-storing companies already
    done -- see collector/retry.py."""
    only_ciks = _parse_ciks(ciks)
    with get_connection() as conn:
        ctx = start_or_resume_run(conn, job="companyfacts", only_ciks=only_ciks, limit=limit, force_fresh=fresh)
        try:
            stats = bootstrap_companyfacts(
                conn, fetched_at=ctx.fetched_at, run_id=ctx.run_id, only_ciks=only_ciks, limit=limit
            )
            finish_run(conn, ctx.run_id, "succeeded", stats)
        except Exception:
            _finish_run_safely(ctx.run_id, "failed", {})
            raise
    typer.echo(f"companyfacts: {stats} (run_id={ctx.run_id}, resumed={ctx.resumed})")


@app.command()
def submissions(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: full universe)."),
    limit: int = typer.Option(None, help="Approximate cap on distinct CIKs stored."),
    fresh: bool = typer.Option(False, help="Ignore any resumable run and start a brand-new one."),
) -> None:
    """Bootstrap raw.sec_submissions from the bulk submissions.zip archive.
    Same resume behavior as `companyfacts`."""
    only_ciks = _parse_ciks(ciks)
    with get_connection() as conn:
        ctx = start_or_resume_run(conn, job="submissions", only_ciks=only_ciks, limit=limit, force_fresh=fresh)
        try:
            stats = bootstrap_submissions(
                conn, fetched_at=ctx.fetched_at, run_id=ctx.run_id, only_ciks=only_ciks, limit=limit
            )
            finish_run(conn, ctx.run_id, "succeeded", stats)
        except Exception:
            _finish_run_safely(ctx.run_id, "failed", {})
            raise
    typer.echo(f"submissions: {stats} (run_id={ctx.run_id}, resumed={ctx.resumed})")


@app.command()
def golden(fresh: bool = typer.Option(False, help="Ignore any resumable run and start a brand-new one.")) -> None:
    """Bootstrap companyfacts + submissions for the fixed golden-company set
    (tests/golden_companies/companies.json) -- doc 08's Day 3 acceptance
    test and doc 05's permanent regression fixture, and Day 4's kill-mid-
    run/resume proving ground. One collector_runs row for the whole
    invocation (job="golden"); resuming after a kill picks the same run_id
    back up and each phase's own checkpoint (by run_id) skips whatever it
    already stored before the kill."""
    golden_ciks = _load_golden_ciks()
    typer.echo(f"golden set: {len(golden_ciks)} companies")
    with get_connection() as conn:
        ctx = start_or_resume_run(conn, job="golden", only_ciks=golden_ciks, limit=None, force_fresh=fresh)
        typer.echo(f"run_id={ctx.run_id} resumed={ctx.resumed}")
        try:
            cf_stats = bootstrap_companyfacts(
                conn, fetched_at=ctx.fetched_at, run_id=ctx.run_id, only_ciks=golden_ciks
            )
            typer.echo(f"companyfacts: {cf_stats}")
            sub_stats = bootstrap_submissions(
                conn, fetched_at=ctx.fetched_at, run_id=ctx.run_id, only_ciks=golden_ciks
            )
            typer.echo(f"submissions: {sub_stats}")
            finish_run(conn, ctx.run_id, "succeeded", {"companyfacts": cf_stats, "submissions": sub_stats})
        except Exception:
            _finish_run_safely(ctx.run_id, "failed", {})
            raise
    typer.echo(f"run_id={ctx.run_id}")


@app.command("reap-stale-runs")
def reap_stale_runs_cmd(
    stale_after_minutes: float = typer.Option(120.0, help="Mark 'running' rows with no heartbeat older than this as failed."),
) -> None:
    """Manual/ops entry point for collector.retry.reap_stale_runs -- also
    runs automatically at the start of every bootstrap command, but exposed
    directly for visibility/testing and for cleaning up abandoned runs
    whose exact params will never be reissued (so auto-resume would never
    reach them)."""
    with get_connection() as conn:
        reaped = reap_stale_runs(conn, stale_after=timedelta(minutes=stale_after_minutes))
    typer.echo(f"reaped: {reaped}")


if __name__ == "__main__":
    app()
