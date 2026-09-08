"""Typer CLI for the unified Data Incident layer (2026-09-08) --
built off doc/data-moat/scope/internal-auto-fixer.md, evaluated then
scoped down to a deterministic dashboard + impact-analysis + verifier
(see incidents/dashboard.py's module docstring for what was
deliberately NOT built: 6 separate LLM agents, an autonomous code-
patching Solver, customer-support convergence)."""

import os

import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.incidents.dashboard import summarize, render_markdown as render_dashboard
from scrooner_pipeline.incidents.impact import impact_report, render_markdown as render_impact
from scrooner_pipeline.incidents.verifier import verify_company, render_markdown as render_verify

app = typer.Typer()


@app.command("dashboard")
def dashboard_cmd(github_summary: bool = typer.Option(False, help="Also append to $GITHUB_STEP_SUMMARY, if set.")) -> None:
    """Reads analytics.data_incident (the live view over all 5 checker
    tables) and renders the open-incidents dashboard: totals by
    severity, by source system, worst metrics/concepts, and the top
    offending companies. Read-only, safe to run any time."""
    with get_connection() as conn:
        summary = summarize(conn)
    markdown = render_dashboard(summary)
    typer.echo(markdown)

    if github_summary:
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a") as f:
                f.write(markdown + "\n")


@app.command("impact")
def impact_cmd(concept: str = typer.Argument(..., help="canonical_concept name, e.g. 'revenue' or 'total_debt'.")) -> None:
    """Real blast-radius report for one canonical_concept: which
    metric_definitions read it as a formula input (via the actual
    metric_definition_input table calculate.py itself reads), which
    saved screens reference each of those metrics (a real jsonb query
    against app.saved_screen.query), and how many real companies carry
    data under this concept today."""
    with get_connection() as conn:
        report = impact_report(conn, concept)
    typer.echo(render_impact(report))


@app.command("verify")
def verify_cmd(company_id: int = typer.Argument(..., help="core.company.id to verify.")) -> None:
    """Snapshots analytics.data_incident for one company, reruns the
    two checks that are safe/cheap to rerun on demand (tag_investigator
    resolution + the timeseries self-consistency check), snapshots
    again, and reports what actually resolved/regressed/stayed open.
    Use this right after applying a company_tag_preference fix to
    confirm it actually closed the incident, not just that the write
    succeeded."""
    with get_connection() as conn:
        result = verify_company(conn, company_id)
    typer.echo(render_verify(result))
