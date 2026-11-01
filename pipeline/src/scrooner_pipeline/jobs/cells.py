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


@app.callback()
def _root() -> None:
    """Keeps `load` a subcommand (a single-command Typer app would swallow it)."""


def _fetch(path: str, cache: Path) -> Path:
    """A `fsn-notes/...` path is downloaded (with its manifest.json) into the
    cache through the storage HTTP API, the way proof/fsn.py reads FSN sets."""
    if not path.startswith("fsn-notes/"):
        return Path(path)
    import os

    import httpx

    base = os.environ["SUPABASE_URL"].rstrip("/") + "/storage/v1/object/"
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"Authorization": f"Bearer {key}", "apikey": key}
    target = cache / path
    target.parent.mkdir(parents=True, exist_ok=True)
    for name in (Path(path).name, "manifest.json"):
        obj = str(Path(path).with_name(name))
        local = target.parent / name
        if local.exists():
            continue
        resp = httpx.get(base + obj, headers=headers, timeout=900)
        if resp.status_code != 200:
            if name == "manifest.json":
                typer.echo(f"no manifest.json next to {path}: HTTP {resp.status_code}")
                continue
            raise FileNotFoundError(f"{obj}: HTTP {resp.status_code}")
        local.write_bytes(resp.content)
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
    defect_keys: str = typer.Option(
        None,
        help="JSONL of cell keys to load as defect blanks instead of their value (a lane's suspect list).",
    ),
    defect_reason: str = typer.Option(
        "mixed_vintage_inputs", help="reason_code for --defect-keys rows."
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

    def connect():
        import psycopg

        from scrooner_pipeline.common.config import settings

        c = psycopg.connect(settings.database_url, connect_timeout=30)
        c.execute(f"set statement_timeout = '{statement_timeout}'")
        c.commit()
        return c

    with get_connection() as conn:
        conn.execute(f"set statement_timeout = '{statement_timeout}'")
        rep = cell_loader.load(
            conn,
            family,
            paths,
            apply=apply,
            git_commit=git_commit,
            data_points=[s for s in data_points.split(",") if s] or None,
            defect_overrides=[
                json.loads(line)
                for line in Path(defect_keys).read_text().splitlines()
                if line.strip()
            ]
            if defect_keys
            else None,
            defect_reason=defect_reason,
            connect=connect,
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
