"""Typer CLI for the SEC Frames self-consistency checker (doc 45 follow-on,
2026-09-08). See frames/compare.py's module docstring for why this is a
fundamentally different check than the yfinance-based ones: both sides
read the SAME SEC filing, so a mismatch is direct evidence of a bug in
our OWN pipeline, not a third-party disagreement."""

import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.common.sec_client import SECClient
from scrooner_pipeline.frames.fetch import fetch_frame
from scrooner_pipeline.frames.compare import compare_frame

app = typer.Typer()

# (canonical_concept_name, taxonomy, tag, is_instant) -- the highest-value
# concepts first: doc 02's locked V1 metrics' own underlying facts.
# Deliberately a SMALL, named list, not "every concept" -- same "measure
# before building broadly" discipline as every other rollout this project
# has done; widen only once this first pass proves the pattern.
CONCEPTS_TO_CHECK: list[tuple[str, str, str, bool]] = [
    ("revenue", "us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax", False),
    ("net_income", "us-gaap", "NetIncomeLoss", False),
    ("cfo", "us-gaap", "NetCashProvidedByUsedInOperatingActivities", False),
    ("operating_income", "us-gaap", "OperatingIncomeLoss", False),
    ("total_assets", "us-gaap", "Assets", True),
    ("cash_and_equivalents", "us-gaap", "CashAndCashEquivalentsAtCarryingValue", True),
    ("stockholders_equity", "us-gaap", "StockholdersEquity", True),
]


def _canonical_concept_id(conn, name: str) -> int:
    with conn.cursor() as cur:
        cur.execute("select id from analytics.canonical_concept where name = %s", (name,))
        return cur.fetchone()[0]


@app.command("run")
def run_cmd(
    year: int = typer.Option(..., help="Calendar year, e.g. 2026"),
    quarter: int = typer.Option(..., help="Calendar quarter, 1-4"),
) -> None:
    """Fetches SEC's own bulk Frames data for CONCEPTS_TO_CHECK at the
    given (year, quarter) and compares it against our own core.fact for
    every matched company. One SEC request per concept (not per company)
    -- 7 requests total for the current list, covering the whole active
    population in each."""
    client = SECClient()
    totals = {"considered": 0, "matched_company": 0, "ok": 0, "mismatch": 0, "missing_ours": 0}
    with get_connection() as conn:
        for concept_name, taxonomy, tag, is_instant in CONCEPTS_TO_CHECK:
            concept_id = _canonical_concept_id(conn, concept_name)
            rows = fetch_frame(client, taxonomy, tag, "USD", year, quarter, is_instant)
            typer.echo(f"{concept_name} ({taxonomy}:{tag}): fetched {len(rows)} SEC-wide rows")
            stats = compare_frame(conn, concept_id, taxonomy, tag, rows)
            typer.echo(f"  {stats}")
            for key in totals:
                totals[key] += stats.get(key, 0)
    typer.echo(f"TOTAL: {totals}")


@app.command("report")
def report_cmd() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select cc.name, f.severity, count(*)
                from analytics.frames_consistency_check f
                join analytics.canonical_concept cc on cc.id = f.canonical_concept_id
                group by cc.name, f.severity
                order by cc.name, f.severity
                """
            )
            typer.echo("Concept | Severity | Count")
            for name, severity, count in cur.fetchall():
                typer.echo(f"{name} | {severity} | {count}")

            cur.execute(
                """
                select c.company_name, l.ticker, cc.name, f.tag, f.period_end,
                       f.our_value, f.frames_value, f.pct_diff, f.accession
                from analytics.frames_consistency_check f
                join core.company c on c.id = f.company_id
                join analytics.canonical_concept cc on cc.id = f.canonical_concept_id
                left join core.listing l on l.company_id = c.id and l.effective_to is null and l.security_type = 'Common Stock'
                where f.severity = 'mismatch'
                order by f.pct_diff desc
                limit 40
                """
            )
            typer.echo("\n=== Worst mismatches (SEC's own data vs. ours) ===")
            for row in cur.fetchall():
                typer.echo(str(row))
