"""Typer CLI: human-readable reporting over what the Collector has already
recorded (doc 08 Day 6) -- collector/logs.py (Module 10, run summaries)
and collector/integrity.py (Module 11, checksum reconciliation). Same
pattern as jobs/bootstrap.py / jobs/incremental.py: this file is just the
CLI wiring, the actual logic lives in collector/*.py.
"""

import typer

from scrooner_pipeline.collector import integrity, logs
from scrooner_pipeline.db.connection import get_connection

app = typer.Typer()


@app.command()
def runs(
    limit: int = typer.Option(20, help="How many recent runs to show."),
    job: str = typer.Option(
        None, help="Restrict to one job (e.g. 'companyfacts', 'incremental')."
    ),
) -> None:
    """Human-readable summary of recent raw.collector_runs rows."""
    with get_connection() as conn:
        rows = logs.get_recent_runs(conn, limit=limit, job=job)
    typer.echo(logs.format_recent_runs(rows))


@app.command()
def run(run_id: int) -> None:
    """Full detail for one run: its raw.collector_runs row plus every
    raw.collector_errors row tied to it."""
    with get_connection() as conn:
        detail = logs.get_run_detail(conn, run_id)
    if detail is None:
        typer.echo(f"no such run_id={run_id}")
        raise typer.Exit(1)
    typer.echo(logs.format_run_detail(detail))


@app.command()
def reconcile(
    hash_sample_rate: float = typer.Option(
        1.0,
        help=(
            "Fraction (0.0-1.0) of existing objects to re-download and re-hash. "
            "Existence checking is ALWAYS exhaustive regardless of this value -- "
            "see collector/integrity.py's module docstring for the reasoning. "
            "Default 1.0 (exhaustive) matches the current data volume (a few "
            "hundred objects); lower this once volume/size make exhaustive "
            "re-download impractical."
        ),
    ),
    seed: int = typer.Option(
        None, help="Random seed for reproducible sampling (irrelevant at rate=1.0)."
    ),
    table: str = typer.Option(
        None,
        help="Restrict to one raw.* table (e.g. 'raw.sec_companyfacts'). Default: check all tables with a storage_path column.",
    ),
) -> None:
    """Checksum reconciliation report (doc 08 Day 6, Module 11): for every
    DB row with a storage_path, confirm a real Supabase Storage object
    exists there, and (per hash_sample_rate) that its content still hashes
    to the recorded sha256. Exits 1 if any unexplained delta is found, so
    this is safe to wire into a cron/CI check later without extra
    plumbing."""
    tables = [table] if table else None
    with get_connection() as conn:
        report = integrity.reconcile(
            conn, hash_sample_rate=hash_sample_rate, seed=seed, tables=tables
        )
    typer.echo(integrity.render_report(report))
    if not report.clean:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
