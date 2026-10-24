"""Typer CLI `scrooner-certify`: the top-1000 certification invariant suite
(data-team/34, P1). DEFAULT IS DRY-RUN: findings are printed, nothing is
written. --apply writes only analytics.certification_finding and
analytics.company_certification (migration 0097), delete-then-insert per
company, one transaction per chunk of at most 25 companies."""

from __future__ import annotations

from pathlib import Path

import psycopg
import typer

from scrooner_pipeline.certification.loader import HISTORY_FLOOR, resolve_company_ids
from scrooner_pipeline.certification.runner import (
    DEFAULT_TIMEOUT_S,
    MAX_CHUNK,
    SHARDS_CSV,
    MigrationNotAppliedError,
    certify,
    dump_json,
    load_shard_company_ids,
    render_text,
)
from scrooner_pipeline.common.config import settings

app = typer.Typer(help=__doc__)


@app.command("run")
def run_cmd(
    ciks: str = typer.Option("", help="Comma-separated CIKs."),
    top1000_shard: str = typer.Option(
        "", "--top1000-shard", help="Campaign shard id, e.g. S001."
    ),
    limit: int = typer.Option(
        0, help="Check at most this many companies (0 = all selected)."
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--apply",
        help="Dry run (default): print findings, write nothing. --apply writes the two certification tables.",
    ),
    chunk_size: int = typer.Option(
        MAX_CHUNK, help=f"Companies per chunk (capped at {MAX_CHUNK})."
    ),
    statement_timeout: int = typer.Option(
        DEFAULT_TIMEOUT_S, help="Seconds, set before every query."
    ),
    since: str = typer.Option(
        HISTORY_FLOOR.isoformat(),
        help="Earliest period end checked (history gate, doc 38).",
    ),
    show: int = typer.Option(0, help="Also print the first N findings."),
    summary_only: bool = typer.Option(
        False, help="Print only the SUMMARY block (states, wrong_value, I11 causes)."
    ),
    json_out: Path = typer.Option(None, help="Write all findings to this JSON file."),
    shards_file: Path = typer.Option(SHARDS_CSV, help="shards.csv path."),
) -> None:
    """Run invariants I1-I10 for the selected companies."""
    from datetime import date

    if not ciks and not top1000_shard:
        raise typer.BadParameter("give --ciks or --top1000-shard")
    since_date = date.fromisoformat(since) if since else None
    conn = psycopg.connect(settings.database_url)
    try:
        conn.read_only = dry_run
        ids: list[int] = []
        if top1000_shard:
            ids += load_shard_company_ids(top1000_shard, shards_file)
        if ciks:
            with conn.cursor() as cur:
                ids += resolve_company_ids(cur, ciks.split(","), statement_timeout)
            conn.rollback()
        ids = list(dict.fromkeys(ids))
        if limit:
            ids = ids[:limit]
        typer.echo(
            f"mode: {'DRY RUN (nothing written)' if dry_run else 'APPLY'}; companies: {len(ids)}"
        )
        try:
            result = certify(
                conn,
                ids,
                chunk_size=chunk_size,
                timeout_s=statement_timeout,
                since=since_date,
                apply=not dry_run,
                progress=typer.echo,
            )
        except MigrationNotAppliedError as exc:
            typer.echo(f"REFUSED: {exc}")
            raise typer.Exit(code=2)
        typer.echo(render_text(result, show=show, summary_only=summary_only))
        if json_out:
            dump_json(result, json_out)
            typer.echo(f"findings written to {json_out}")
        if not dry_run:
            typer.echo(
                f"rows written to analytics.certification_finding: {result.written}"
            )
        typer.echo(
            f"elapsed: {sum(result.chunk_seconds):.1f}s over {len(result.chunk_seconds)} chunk(s)"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    app()
