"""Guarded command-line entry point for auditable dead-letter resolution."""

import json

import typer

from scrooner_pipeline.common.reconcile import parse_error_ids, resolve_dead_letters
from scrooner_pipeline.db.connection import get_connection

app = typer.Typer()


@app.command()
def resolve(
    layer: str = typer.Option(
        ..., help="Pipeline layer: collector, normalizer, or mapper."
    ),
    ids: str = typer.Option(..., help="Comma-separated exact dead-letter IDs."),
    note: str = typer.Option(
        ..., help="Evidence explaining why these exact rows are resolved."
    ),
    confirm: bool = typer.Option(
        False, "--confirm", help="Required write confirmation."
    ),
) -> None:
    """Resolve only the explicitly supplied dead-letter IDs."""
    if not confirm:
        typer.echo(
            "refusing write: pass --confirm after reviewing the exact IDs and evidence note",
            err=True,
        )
        raise typer.Exit(2)
    try:
        error_ids = parse_error_ids(ids)
        with get_connection() as conn:
            result = resolve_dead_letters(
                conn, layer=layer, error_ids=error_ids, note=note
            )
    except ValueError as exc:
        typer.echo(f"refusing write: {exc}", err=True)
        raise typer.Exit(2) from exc
    typer.echo(json.dumps(result, indent=2))


if __name__ == "__main__":
    app()
