"""Typer CLI `scrooner-cells`: load family cell files into analytics.canonical_fact
(data-team/46-canonical-fact-v2/CELL-FORMAT-v1.md). `plan` (default) validates,
binds, resolves and reports with every write rolled back; `--apply` writes.
A path under the fsn-notes bucket (`fsn-notes/cells/...`) is downloaded first."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import typer

from scrooner_pipeline.db.connection import get_connection

app = typer.Typer(help="Family cell files -> analytics.canonical_fact.")


def _fetch(path: str, cache: Path) -> Path:
    if not path.startswith("fsn-notes/"):
        return Path(path)
    from scrooner_pipeline.collector.storage import (
        SupabaseStorageClient,
        strip_bucket_prefix,
    )

    target = cache / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with SupabaseStorageClient() as storage:
        for name in (Path(path).name, "manifest.json"):
            obj = str(Path(path).with_name(name))
            try:
                (target.parent / name).write_bytes(
                    storage.download(strip_bucket_prefix(obj))
                )
            except Exception as exc:  # noqa: BLE001
                if name != "manifest.json":
                    raise
                typer.echo(f"no manifest.json next to {path}: {exc!r}")
    return target


@app.command("load")
def load_cmd(
    files: list[str] = typer.Argument(
        ...,
        help="Cell files (.jsonl or .jsonl.gz), local or fsn-notes/... bucket paths; ONE family.",
    ),
    family: str = typer.Option(..., help="Family name (spec section 4)."),
    apply: bool = typer.Option(
        False, "--apply/--plan", help="Write (default: plan, rolled back)."
    ),
    report: str = typer.Option(None, help="Write the load report JSON here."),
    data_points: str = typer.Option(
        "",
        help="Comma-separated delete scope (default: manifest.data_points or the file's).",
    ),
    cache: str = typer.Option(".cache/cells", help="Local cache for bucket downloads."),
    statement_timeout: str = typer.Option(
        "10min", help="Per-statement timeout for this session."
    ),
) -> None:
    from scrooner_pipeline.normalizer import cell_loader

    git_commit = (
        subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
        or None
    )
    paths = [_fetch(f, Path(cache)) for f in files]
    with get_connection() as conn:
        conn.execute(f"set statement_timeout = '{statement_timeout}'")
        rep = cell_loader.load(
            conn,
            family,
            paths,
            apply=apply,
            git_commit=git_commit,
            data_points=[s for s in data_points.split(",") if s] or None,
        )
    d = rep.as_dict()
    if report:
        Path(report).write_text(json.dumps(d, indent=1, default=str))
    summary = {
        k: v
        for k, v in d.items()
        if k not in ("per_company", "reject_samples", "sha256", "files")
    }
    typer.echo(f"cells load {family} [{rep.mode}]: {json.dumps(summary, default=str)}")
    if rep.rejected:
        typer.echo(
            "rejects (first 10): " + json.dumps(rep.reject_samples[:10], default=str)
        )


if __name__ == "__main__":
    app()
