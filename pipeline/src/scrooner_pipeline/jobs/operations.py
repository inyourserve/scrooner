"""Operational status CLI for pipeline freshness, runs, and dead letters."""

import json

import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.operations import load_operational_snapshot, snapshot_as_dict

app = typer.Typer()


@app.command()
def status(
    fail_on_alert: bool = typer.Option(
        False, help="Exit 1 when any operational alert is active."
    ),
    fsn_freshness_alert: bool = typer.Option(
        False,
        envvar="FSN_FRESHNESS_ALERT",
        help="Alert when cohort companies' newest fsn.filing lags core.filing. Default report-only: the FSN nightly stage is still off.",
    ),
) -> None:
    """Print one machine-readable operational snapshot; performs no writes."""
    with get_connection() as conn:
        conn.execute("set transaction read only")
        report = snapshot_as_dict(
            load_operational_snapshot(conn, fsn_alert_enabled=fsn_freshness_alert)
        )
    typer.echo(json.dumps(report, indent=2, default=str))
    if fail_on_alert and report["alerts"]:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
