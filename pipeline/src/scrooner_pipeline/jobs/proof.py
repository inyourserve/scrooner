"""scrooner-proof: the cell proof system (rule proof.cell_proof@1, migration 0114)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.proof.runner import run

app = typer.Typer(
    help="One proof row per displayed cell: shown value vs structure-selected printed line."
)


@app.callback()
def _main() -> None:
    """scrooner-proof <command>: run."""


def _parse_ciks(ciks: str) -> set[str]:
    return {c.strip().zfill(10) for c in ciks.split(",") if c.strip()}


@app.command("run")
def run_cmd(
    ciks: str = typer.Option(..., help="Comma-separated CIKs."),
    fsn_root: str = typer.Option(
        ".cache/fsn",
        help="Local cache of FSN quarters (downloaded from the fsn-notes bucket on first use).",
    ),
    report: str = typer.Option(None, help="JSONL report, one row per cell."),
    write: bool = typer.Option(
        False,
        "--write",
        help="Upsert into analytics.cell_proof (needs migration 0114 applied).",
    ),
    statement_timeout: str = typer.Option("10min"),
    floor: str = typer.Option(
        None,
        help="Only cells with period_end >= this date (YYYY-MM-DD); default 2015-01-01.",
    ),
) -> None:
    """Dry run by default (report only). --write stores the proofs; the website
    reads them only behind proof.serve_proven_only@1 (OFF)."""
    with get_connection() as conn:
        conn.execute(f"set statement_timeout = '{statement_timeout}'")
        totals = run(
            conn,
            _parse_ciks(ciks),
            fsn_root=Path(fsn_root),
            report_path=Path(report) if report else None,
            write=write,
            floor=date.fromisoformat(floor) if floor else None,
        )
    per_company = totals.pop("per_company")
    typer.echo(f"cell-proof: {json.dumps(totals, default=str)}")
    for cik, v in sorted(per_company.items()):
        typer.echo(f"  {cik}: {v}")
