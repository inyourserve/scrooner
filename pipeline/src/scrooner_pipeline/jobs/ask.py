"""Typer CLI for the AI Query Engine (doc 15). Takes English text, prints
the interpretation (and, with --run, executes it through the real
Screener) -- through llm_interpreter.interpret, which is the rule-based
interpreter (6b) unless an LLM client is configured (none ships, doc 15);
see ai_query/rules.py's module docstring for its documented scope limits.
"""

import json
from decimal import Decimal

import structlog
import typer

from scrooner_pipeline.ai_query.llm_interpreter import interpret
from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.screener.query import run_query

app = typer.Typer()
logger = structlog.get_logger()


def _default(o):
    if isinstance(o, Decimal):
        return str(o)
    return str(o)


@app.command("ask")
def ask_cmd(
    text: str = typer.Argument(..., help="Plain-English screening request."),
    run: bool = typer.Option(
        False, help="Also execute the interpreted query through the Screener."
    ),
) -> None:
    result = interpret(text)
    typer.echo(f"Explanation: {result.explanation}")
    if result.unrecognized:
        typer.echo(f"Unrecognized: {result.unrecognized}")
    if result.ambiguous:
        typer.echo(f"Ambiguous: {[(a.phrase, a.candidates) for a in result.ambiguous]}")
    if result.query is None:
        typer.echo("No query produced.")
        return
    typer.echo(f"ScreenQuery: {result.query.model_dump_json()}")
    if run:
        with get_connection() as conn:
            screen_result = run_query(conn, result.query)
        typer.echo(json.dumps(screen_result, default=_default, indent=2))


if __name__ == "__main__":
    app()
