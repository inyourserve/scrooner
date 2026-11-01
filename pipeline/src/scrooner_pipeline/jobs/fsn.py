"""Typer CLI `scrooner-fsn`: the company-wise FSN statement store."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

import typer

app = typer.Typer(help="Company-wise FSN statement store (design 2026-11-01).")
SHARDS_CSV = Path("doc/data-moat/team/top1000/shards.csv")


@app.callback()
def _root() -> None:
    """Subcommands: shard."""


def _cohort(shards_file: Path) -> list[str]:
    for cand in (shards_file, Path(__file__).resolve().parents[4] / shards_file):
        if cand.exists():
            return sorted(
                {r["cik"] for r in csv.DictReader(cand.open()) if not r.get("excluded")}
            )
    raise FileNotFoundError(shards_file)


@app.command("shard")
def shard_cmd(
    out: str = typer.Option("companies", help="Output root: companies/<cik>/"),
    ciks: str = typer.Option(
        "", help="Comma-separated CIKs (default: the top-1000 cohort)."
    ),
    periods: str = typer.Option(
        "", help="Comma-separated FSN sets (default: every set in the bucket)."
    ),
    cache: str = typer.Option(
        ".cache/fsn-shard", help="Download cache; each period is deleted after use."
    ),
    floor_gb: float = typer.Option(
        4.0, help="Stop cleanly when free disk falls below this."
    ),
    shards_file: Path = typer.Option(SHARDS_CSV),
) -> None:
    """Bucket period extracts -> company directories (FORMATS-v1 §1). Read-only on the bucket and the DB."""
    from scrooner_pipeline.db.connection import get_connection
    from scrooner_pipeline.fsn_store import shard

    cik_list = [c.strip().zfill(10) for c in ciks.split(",") if c.strip()] or _cohort(
        shards_file
    )
    with get_connection() as conn:
        rows = conn.execute(
            "select cik, id from core.company where cik = any(%s)", (cik_list,)
        ).fetchall()
    ids = dict(rows)
    targets = {c: ids.get(c) for c in cik_list}
    commit = (
        subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
        or None
    )
    res = shard.run(
        Path(out),
        targets,
        [p for p in periods.split(",") if p] or None,
        Path(cache),
        floor_gb=floor_gb,
        shard_commit=commit,
    )
    typer.echo(f"fsn shard: {json.dumps(res)}")


if __name__ == "__main__":
    app()
