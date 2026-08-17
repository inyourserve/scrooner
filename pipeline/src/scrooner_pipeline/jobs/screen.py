"""Typer CLI for the Screener (doc 14). Accepts a query as a JSON string
for manual/golden-set testing -- no HTTP exposure (doc 02's FastAPI gate
isn't cleared), just a way to run a real ScreenQuery against the live
database and inspect the result directly.
"""

import json
from decimal import Decimal

import structlog
import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.screener.query import run_query
from scrooner_pipeline.screener.schema import ScreenQuery

app = typer.Typer()
logger = structlog.get_logger()


def _default(o):
    if isinstance(o, Decimal):
        return str(o)
    return str(o)


@app.command("run")
def run_cmd(query_json: str = typer.Argument(..., help="ScreenQuery as a JSON string.")) -> None:
    """Run a screen query (JSON) against the live database and print the result."""
    query = ScreenQuery.model_validate_json(query_json)
    with get_connection() as conn:
        result = run_query(conn, query)
    typer.echo(json.dumps(result, default=_default, indent=2))


if __name__ == "__main__":
    app()
