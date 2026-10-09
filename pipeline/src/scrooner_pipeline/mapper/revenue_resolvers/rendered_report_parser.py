"""Revenue resolver: rendered-report extraction (doc 42, Parser 3,
`parsers/revenue_parser.py`) for the genuine residual population where
the real value exists in the filing's own rendered income-statement
table, under a company-specific custom tag no mapped-tag list could
enumerate -- the standard Company Facts API strips this kind of
dimensional/custom-label data entirely (doc 22's already-documented
limitation).

Thin wrapper around `parsers/main_parser.py`'s existing orchestration
(`run_parser`/`resolve_parser_results`), given a `run()` entry point
consistent with every other resolver here. Runs LAST and is the only
resolver in this package that does its own SEC fetches (rate-limited,
real cost) -- `run_all(include_parser=True)` opts into it explicitly;
every other resolver is pure local recomputation and always runs."""

import psycopg

from scrooner_pipeline.parsers.main_parser import resolve_parser_results, run_parser


def run(conn: psycopg.Connection, ciks: set[str] | None = None) -> dict:
    parse_result = run_parser(conn, "revenue", ciks)
    merge_stats = resolve_parser_results(conn, "revenue")
    return {
        "considered": parse_result["stats"].get("considered", 0),
        "ok": parse_result["stats"].get("ok", 0),
        "errored": parse_result["stats"].get("errored", 0)
        + merge_stats.get("errored", 0),
        "rows_written": merge_stats.get("applied", 0),
        "no_matching_period": merge_stats.get("no_matching_period", 0),
    }
