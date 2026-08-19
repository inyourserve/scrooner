"""Operational status CLI for pipeline freshness, runs, and dead letters."""

import json

import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.operations import load_operational_snapshot, snapshot_as_dict

app = typer.Typer()


@app.command()
def status(
    fail_on_alert: bool = typer.Option(False, help="Exit 1 when any operational alert is active."),
) -> None:
    """Print one machine-readable operational snapshot; performs no writes."""
    with get_connection() as conn:
        conn.execute("set transaction read only")
        report = snapshot_as_dict(load_operational_snapshot(conn))
    typer.echo(json.dumps(report, indent=2, default=str))
    if fail_on_alert and report["alerts"]:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
