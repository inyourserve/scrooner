"""Typer CLI for the Data Sanity Layer (2026-09-08) -- an independent
yfinance cross-check of a handful of our own computed values, run
continuously (daily, rotating through the active population) rather than
as a one-off audit. See sanity/yfinance_check.py's module docstring for
the full design and doc/learnings/2026-09-08-data-sanity-layer.md for how
it was scoped."""

import json
from pathlib import Path

import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.sanity.yfinance_check import (
    run_sanity_checks,
    pick_rotation_batch,
)
from scrooner_pipeline.sanity.report import (
    find_regressions,
    load_baseline,
    record_baseline,
    render_markdown,
    summarize,
)
from scrooner_pipeline.sanity.tag_investigator import investigate_open_findings
from scrooner_pipeline.sanity.timeseries_check import run_all as run_timeseries_all
from scrooner_pipeline.sanity.plausibility_check import run_all as run_plausibility_all

app = typer.Typer()

GOLDEN_COMPANIES_PATH = (
    Path(__file__).resolve().parents[3]
    / "tests"
    / "golden_companies"
    / "companies.json"
)


def _load_golden_company_ids(conn) -> list[int]:
    companies = json.loads(GOLDEN_COMPANIES_PATH.read_text())
    ciks = [c["cik"].zfill(10) for c in companies]
    with conn.cursor() as cur:
        cur.execute("select id from core.company where cik = any(%s)", (ciks,))
        return [r[0] for r in cur.fetchall()]


@app.command("run")
def run_cmd(
    limit: int = typer.Option(
        750, help="Max companies to check this run (rotates coldest-checked-first)."
    ),
    golden_only: bool = typer.Option(
        False,
        help="Restrict to the golden-10 set instead of rotating the full active population.",
    ),
) -> None:
    """Runs the 4 checks (market_cap, trailing_pe, shares_outstanding,
    revenue_zero_check) against yfinance for a batch of companies, upserts
    analytics.data_sanity_check. `limit` bounds one run's yfinance load --
    the daily cron (.github/workflows/pipeline-sanity.yml) cycles through
    the whole active population over several days, never all ~5,200 in a
    single run."""
    with get_connection() as conn:
        company_ids = (
            _load_golden_company_ids(conn)
            if golden_only
            else pick_rotation_batch(conn, limit)
        )
        stats = run_sanity_checks(conn, company_ids)
    typer.echo(f"sanity run: {stats}")


@app.command("report")
def report_cmd(
    fail_on_findings: bool = typer.Option(
        False,
        help="Exit 1 if critical/major counts regressed vs. the last passing run's "
        "baseline; a passing run records a new baseline. For CI.",
    ),
    github_summary: bool = typer.Option(
        False, help="Also append the markdown report to $GITHUB_STEP_SUMMARY, if set."
    ),
) -> None:
    """Reads back the current state of analytics.data_sanity_check --
    read-only unless --fail-on-findings, which also records the gate
    baseline on a passing run."""
    with get_connection() as conn:
        summary = summarize(conn)
        markdown = render_markdown(summary)

        regressions: list[str] = []
        if fail_on_findings:
            baseline = load_baseline(conn)
            regressions = find_regressions(summary, baseline)
            if baseline is None:
                gate = "\n## Gate\n\nNo baseline yet -- this run establishes it."
            elif regressions:
                gate = "\n## Gate: REGRESSED\n\n" + "\n".join(
                    f"- {r}" for r in regressions
                )
            else:
                gate = "\n## Gate\n\nNo regression vs. the last passing run's baseline."
            markdown += "\n" + gate
            if not regressions:
                record_baseline(conn, summary)

    typer.echo(markdown)

    if github_summary:
        import os

        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a") as f:
                f.write(markdown + "\n")

    if regressions:
        typer.echo(
            "\nFAILING: sanity findings regressed vs. the last passing run's baseline."
        )
        raise typer.Exit(code=1)


@app.command("investigate")
def investigate_cmd() -> None:
    """For every current critical/major analytics.data_sanity_check
    finding: traces every raw core.fact row under each currently-mapped
    tag for that exact (company, period) -- including rows resolve.py
    marked non-authoritative -- and checks whether any of them reconciles
    against the independent (yfinance) figure, used ONLY to detect and
    match, never as the value that gets stored. A reconciling SEC tag for
    a concept in sanity/tag_investigator.py's FIXABLE_CONCEPTS gets stored
    as a per-company tag PREFERENCE (analytics.company_tag_preference) --
    applying to every period that company has data under the tag, not
    just the one flagged -- merged into a *_sanity_resolved concept
    resolve() never touches. NEVER a write to analytics.concept_mapping
    (see tag_investigator.py's module docstring for why a single
    company's match isn't safe to generalize globally), and the stored
    value is always sourced from core.fact (a real SEC filing), never
    from yfinance itself. Every outcome (fixed, a lead needing human
    review, or genuinely no reconcilable tag found) is recorded in
    analytics.data_sanity_investigation, not just the successes. Wired
    into the daily cron right after `sanity run` (see
    .github/workflows/pipeline-sanity.yml) -- the "wire up a fix" half of
    the Data Sanity Layer, not a separate manual step."""
    with get_connection() as conn:
        stats = investigate_open_findings(conn)
    typer.echo(f"sanity investigate: {stats}")


@app.command("timeseries")
def timeseries_cmd() -> None:
    """Time-series self-consistency check (sanity/timeseries_check.py) --
    zero external API calls, unlike every other check in this CLI.
    Compares each company's own value against its own value for the same
    fiscal_period one year earlier. Covers the WHOLE active population
    in one pass (pure set-based SQL per concept, no rotation/batching
    needed the way the yfinance-based checks require)."""
    with get_connection() as conn:
        stats = run_timeseries_all(conn)
    typer.echo(f"sanity timeseries: {stats}")


@app.command("plausibility")
def plausibility_cmd() -> None:
    """Metric Plausibility Check (sanity/plausibility_check.py,
    doc/reference/47_Scrooner_Metric_Plausibility_Gates.md) -- zero
    external calls, checks each company's most recent value per metric
    against a CRITICAL/WATCH range grounded in the real live distribution
    of that metric. Covers the WHOLE active population in one pass, same
    reasoning as `sanity timeseries`."""
    with get_connection() as conn:
        stats = run_plausibility_all(conn)
    typer.echo(f"sanity plausibility: {stats}")
