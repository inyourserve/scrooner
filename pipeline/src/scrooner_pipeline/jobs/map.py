"""Typer CLI for the Mapper (doc 11). Day 1: `seed-concepts` (Stage 3a)."""

import json
from pathlib import Path

import typer

from scrooner_pipeline.db.connection import (
    get_connection,
    run_tolerating_exit_commit_failure,
)
from scrooner_pipeline.mapper.calculate import calculate
from scrooner_pipeline.mapper.concepts import coverage_report, seed, unmapped_tag_report
from scrooner_pipeline.mapper import definitions as definitions_module
from scrooner_pipeline.mapper.resolve import resolve
from scrooner_pipeline.mapper.concept_fallback import (
    resolve_fallbacks,
    resolve_all_arithmetic_fallbacks,
    resolve_all_balance_sheet_identity_fallbacks,
    resolve_employee_count_fallback,
)
from scrooner_pipeline.mapper.revenue_resolvers import run_all as run_revenue_resolvers
from scrooner_pipeline.mapper.dedup_majority_resolver import resolve_all_safe_concepts
from scrooner_pipeline.mapper.conflict_resolution import resolve_all_conflict_fills
from scrooner_pipeline.mapper.ttm import (
    compute_growth,
    compute_ttm_margins,
    compute_ttm_returns,
)
from scrooner_pipeline.mapper import validate as validate_module
from scrooner_pipeline.statements.classify import seed as seed_statements
from scrooner_pipeline.mapper.price_metrics import calculate_price_metrics
from scrooner_pipeline.mapper import expanded_concepts
from scrooner_pipeline.mapper import expanded_definitions
from scrooner_pipeline.mapper.expanded_metrics import calculate_expanded_metrics
from scrooner_pipeline.mapper.quality_score import calculate_piotroski
from scrooner_pipeline.mapper.quality_flags import calculate_quality_flags
from scrooner_pipeline.mapper.reconciliation import calculate_reconciliation
from scrooner_pipeline.mapper.coverage_matrix import (
    build_registry,
    build_coverage,
    corrected_coverage_report,
)
from scrooner_pipeline.mapper.tag_candidates import build_tag_candidates, report_status
from scrooner_pipeline.mapper.tag_library import (
    build_tag_library,
    gap_report,
    gap_tags,
    record_finding,
    record_verdict,
)
from scrooner_pipeline.mapper.tax_reconciliation import calculate_tax_reconciliation
from scrooner_pipeline.mapper.fcf_growth import calculate_fcf_growth
from scrooner_pipeline.mapper.dividend_streak import calculate_dividend_streak
from scrooner_pipeline.mapper.coverage_groups import write_group_snapshot
from scrooner_pipeline.mapper.coverage_snapshot import write_snapshot
from scrooner_pipeline.mapper.company_coverage_dashboard import (
    render_markdown_company,
    render_markdown_population,
    summarize_company,
    summarize_population,
)
from scrooner_pipeline.parsers.filing_line_evidence import (
    run as run_filing_line_evidence,
)
from scrooner_pipeline.parsers.main_parser import (
    run_parser,
    resolve_parser_results,
    registry_summary,
    PARSER_REGISTRY,
)
from scrooner_pipeline.mapper.main_calculator import (
    METRIC_CALCULATOR_REGISTRY,
    unregistered_metrics,
)

# HYBRID_NEW_PATH: the writer subcommands leave new-path companies out of --ciks (fsn_store/new_path.py)
from scrooner_pipeline.fsn_store.new_path import guarded_group  # noqa: E402

app = typer.Typer(cls=guarded_group("scrooner-map"))

GOLDEN_COMPANIES_PATH = (
    Path(__file__).resolve().parents[3]
    / "tests"
    / "golden_companies"
    / "companies.json"
)


def _load_golden_ciks() -> set[str]:
    companies = json.loads(GOLDEN_COMPANIES_PATH.read_text())
    return {c["cik"] for c in companies}


@app.command("seed-concepts")
def seed_concepts_cmd() -> None:
    """Stage 3a: seed analytics.canonical_concept + analytics.concept_mapping."""
    with get_connection() as conn:
        stats = seed(conn)
    typer.echo(f"seed-concepts: {stats}")


@app.command("coverage")
def coverage_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
    show_unresolved_only: bool = typer.Option(
        True, help="Only print rows that failed to resolve."
    ),
) -> None:
    """Stage 3a coverage report: for every (company, canonical_concept), did
    at least one mapped tag resolve to real authoritative fact data?"""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        rows = coverage_report(conn, target_ciks)
    unresolved = [r for r in rows if not r["resolved"]]
    typer.echo(
        f"{len(rows)} (company, concept) pairs checked; {len(unresolved)} unresolved"
    )
    to_print = unresolved if show_unresolved_only else rows
    for r in to_print:
        typer.echo(f"  {r}")


@app.command("unmapped-tags")
def unmapped_tags_cmd(
    ciks: str = typer.Option(
        None,
        help="Comma-separated CIKs to restrict to (default: every company with facts, not just golden).",
    ),
    limit: int = typer.Option(50, help="Max tags to print."),
) -> None:
    """Coverage-gap discovery (doc 11's proposed, never-built Frames-API
    workflow's SQL half): core.concept tags with real fact volume that have
    NO analytics.concept_mapping row at all -- ranked by fact-row-count, so
    the highest-leverage unmapped tags surface first for curation into
    mapper/concepts.py's CONCEPT_MAPPINGS. Read-only, no writes -- discovery
    only, never auto-maps."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else None
    with get_connection() as conn:
        rows = unmapped_tag_report(conn, target_ciks, limit)
    typer.echo(
        f"{len(rows)} unmapped tag(s) with real fact volume (top {limit} by fact_count)"
    )
    for r in rows:
        typer.echo(f"  {r}")


@app.command("resolve-facts")
def resolve_facts_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Stage 3b: apply concept_mapping to core.fact, populate
    analytics.canonical_fact. Requires Stage 3a (seed-concepts) to have run."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = resolve(conn, target_ciks)
    typer.echo(f"resolve-facts: {stats}")


@app.command("docmap-load")
def docmap_load_cmd(
    reads: Path = typer.Argument(
        ...,
        help="Directory of <TICKER>-docmap-<date>.csv reads (data-team/companies/reads).",
    ),
    conflicts_out: Path = typer.Option(
        ...,
        "--conflicts-out",
        help="CSV of every docmap/library disagreement (for the Tag Expert).",
    ),
    rejects_out: Path = typer.Option(
        None,
        "--rejects-out",
        help="CSV of rejected docmap rows (unknown status, unknown concept, ...).",
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Write (one transaction per company). Default: dry run."
    ),
    extend_eras: bool = typer.Option(
        False,
        "--extend-eras",
        help="Walk each value row back through earlier 10-Ks (FSN: same tag, same line) -> company_tag_map.era_extend@1 rows.",
    ),
    era_log: Path = typer.Option(
        None, "--era-log", help="CSV of every per-filing era check (pass/fail)."
    ),
    predictor_eras: Path = typer.Option(
        None,
        "--predictor-eras",
        help="Directory of the Tag Expert's per-10-K predictions (data-team/tags/exam/eras): the years the extension could not carry become predictor CANDIDATE slices (era_extend@1, decided_by tag_expert_predictor). `era-guard` decides them after the cell proof.",
    ),
    predictor_concepts: str = typer.Option(
        "",
        "--predictor-concepts",
        help="Comma-separated base concept names (e.g. total_debt,interest_expense): reload only these concepts' predictor and guard rows.",
    ),
    no_filing_ciks: str = typer.Option(
        "",
        "--no-filing-ciks",
        help="Comma-separated CIKs with no 10-K before their listing: uncovered years become no_public_filing_for_period reasons.",
    ),
    fixes: Path = typer.Option(
        None,
        "--fixes",
        help="Directory of reader fix files (<TICKER>-fixes-<date>.csv, one row per cell). Default: <reads>/fixes when present. Each row overrides the docmap/era/predictor row of that one data point and fiscal year (rule company_tag_map.docmap_fix@1, decided_by reader_fix); the rows are split around it. printed_value goes to the serve_note for the Verifier, never served.",
    ),
) -> None:
    """Load the FILING-CHECKED docmaps into analytics.company_tag_map (rule company_tag_map.docmap@1). Dry run by
    default: plans, validates and lists conflicts, writes nothing."""
    from scrooner_pipeline.mapper.docmap_loader import load, write_listing

    if fixes is None and (reads / "fixes").is_dir():
        fixes = reads / "fixes"
    with get_connection() as conn:
        stats = load(
            conn,
            sorted(reads.glob("*-docmap-*.csv")),
            apply=apply,
            extend_eras=extend_eras,
            era_log=era_log,
            predictor_eras=predictor_eras,
            predictor_concepts={
                c.strip() for c in predictor_concepts.split(",") if c.strip()
            }
            or None,
            no_filing_ciks={c.strip() for c in no_filing_ciks.split(",") if c.strip()},
            fixes=fixes,
        )
    write_listing(conflicts_out, stats["conflicts"])
    if rejects_out:
        write_listing(rejects_out, stats["rejects"])
    comps = stats["companies"]
    typer.echo(
        f"docmap-load: files={stats['files']} rows={stats['rows']} companies={len(comps)} "
        f"added={sum(c['added'] for c in comps.values())} removed={sum(c['removed'] for c in comps.values())} "
        f"library_cut={sum(c['library_cut'] for c in comps.values())} "
        f"library_deleted={sum(c['library_deleted'] for c in comps.values())} "
        f"conflicts={len(stats['conflicts'])} rejects={len(stats['rejects'])} blocked={len(stats['blocked'])} "
        f"extended={len(stats['extended'])} fix_files={stats.get('fix_files', 0)} "
        f"fix_rows={stats.get('fix_rows', 0)} "
        f"fix_clipped={sum(c.get('fix_clipped', 0) for c in comps.values())} applied={stats['applied']}"
    )
    for key, why in sorted(stats["blocked"].items()):
        typer.echo(f"  blocked {key}: {why}")
    changed = sorted(
        c["company_id"]
        for c in comps.values()
        if c["added"] or c["removed"] or c["library_cut"] or c["library_deleted"]
    )
    typer.echo(f"changed company ids: {','.join(map(str, changed))}")


@app.command("structural-load")
def structural_load_cmd(
    source: Path = typer.Argument(
        ...,
        help="Structural resolver output: a CSV file or a directory of them (data-team/tags/line_map). Format: mapper/structural_loader.py docstring.",
    ),
    company_ids: str = typer.Option(
        "",
        "--company-ids",
        help="Comma-separated core.company ids (default: all in the input).",
    ),
    conflicts_out: Path = typer.Option(
        None, "--conflicts-out", help="CSV of structural/existing-row disagreements."
    ),
    exceptions_out: Path = typer.Option(
        None,
        "--exceptions-out",
        help="CSV of hand-fix (docmap_fix@1) cells that override or disagree with structural cells.",
    ),
    rejects_out: Path = typer.Option(
        None, "--rejects-out", help="CSV of rejected rows."
    ),
    since: str = typer.Option(
        "2015-01-01", "--since", help="Drop eras ending before this date."
    ),
    open_last: bool = typer.Option(
        False, "--open-last", help="Leave each series' last era open-ended."
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Write (one transaction per company). Default: dry run."
    ),
) -> None:
    """Load the structural resolver output as company_tag_map.structural@1 rows (decided_by structural_resolver).
    Hand fixes win their cells (listed as exceptions); structural clips docmap, era_extend and predictor rows."""
    from datetime import date as _date

    from scrooner_pipeline.mapper.docmap_loader import write_listing
    from scrooner_pipeline.mapper.structural_loader import load

    ids = {int(c) for c in company_ids.split(",") if c.strip()} or None
    with get_connection() as conn:
        stats = load(
            conn,
            source,
            apply=apply,
            company_ids=ids,
            since=_date.fromisoformat(since),
            open_last=open_last,
        )
    if conflicts_out:
        write_listing(conflicts_out, stats["conflicts"])
    if exceptions_out:
        write_listing(exceptions_out, stats["exceptions"])
    if rejects_out:
        write_listing(rejects_out, stats["rejects"])
    comps = stats["companies"]
    skipped = {k: v for k, v in stats.items() if k.startswith("skipped_")}
    typer.echo(
        f"structural-load: files_read={stats.get('files_read', 0)} claims={stats['claims']} "
        f"decisions={stats['decisions']} {skipped} companies={len(comps)} "
        f"inserted={sum(c['inserted'] for c in comps.values())} "
        f"library_clipped={sum(c['library_clipped'] for c in comps.values())} "
        f"library_deleted={sum(c['library_deleted'] for c in comps.values())} "
        f"agree={sum(c['agree'] for c in comps.values())} conflicts={len(stats['conflicts'])} "
        f"exceptions={len(stats['exceptions'])} "
        f"exceptions_disagree={sum(1 for e in stats['exceptions'] if e['agrees'] == 'no')} "
        f"rejects={len(stats['rejects'])} blocked={len(stats['blocked'])} applied={stats['applied']}"
    )
    for key, why in sorted(stats["blocked"].items()):
        typer.echo(f"  blocked {key}: {why}")


@app.command("era-guard")
def era_guard_cmd(
    company_ids: str = typer.Option(
        ..., "--company-ids", help="Comma-separated core.company ids."
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Write (one transaction per company). Default: report only.",
    ),
) -> None:
    """Phase 2 of the predictor fallback. After docmap-load --predictor-eras, tagmap-plan --apply and scrooner-proof
    run --write: every predictor slice the cell proof does not back (PROVEN for values, NOT_PRESENTED for reasons) is
    replaced by a not_presented row, reason_class era_unmapped. Re-run tagmap-plan --apply afterwards."""
    from scrooner_pipeline.mapper.era_guard import hold_unproven

    ids = [int(x) for x in company_ids.split(",") if x.strip()]
    with get_connection() as conn:
        rep = hold_unproven(conn, ids, apply=apply)
    typer.echo(
        f"era-guard: slices={rep['slices']} kept={rep['kept']} held={rep['held']} "
        f"companies={rep['companies']} applied={rep.get('applied', False)}"
    )
    for cid, name, a, b, why in rep["held_cells"][:60]:
        typer.echo(f"  held {cid} {name} {a}..{b}: {why}")


@app.command("seed-company-tag-map")
def seed_company_tag_map_cmd(
    path: Path = typer.Argument(
        ..., help="CSV or JSONL of analytics.company_tag_map rows."
    ),
    open_periods: Path = typer.Option(
        None,
        "--open-periods",
        help="open_periods_*.csv: each OPEN period is loaded as a tagless not_presented row (same transaction).",
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Write (one transaction per company, replacing its rows). Default: dry run.",
    ),
    only_rule: str = typer.Option(
        None,
        "--only-rule",
        help="Load and replace only this rule_id's rows (family.rule@N); other writers' rows stay. "
        "A tagless row of the rule that a live row of another rule already decides is dropped (superseded_by_live).",
    ),
) -> None:
    """Load a company's FSN-learned tag map (migration 0122). Dry run by default: validates every row
    against the table's constraints and prints counts, writes nothing."""
    from scrooner_pipeline.mapper.company_tag_map_seed import seed as seed_tag_map

    with get_connection() as conn:
        stats = seed_tag_map(
            conn, path, apply=apply, open_periods=open_periods, only_rule=only_rule
        )
    typer.echo(
        f"seed-company-tag-map: companies={stats['companies']} rows={stats['rows']} "
        f"undecided_skipped={stats['undecided_skipped']} held_verifier_sample_failed={stats['held_verifier_sample_failed']} applied={stats['applied']}"
    )
    for cik, c in sorted(stats["completeness"].items(), key=lambda kv: str(kv[0])):
        typer.echo(
            f"  {cik}: statement tags decided {c['decided']}/{c['statement_tags']} "
            f"(undecided {c['undecided']}) {c['by_decision']}"
        )
    for (company_id, concept, winner, alt), n in sorted(
        stats.get("winner_tag_gaps", {}).items()
    ):
        typer.echo(
            f"  winner-tag gap: company {company_id} {concept} {winner}: {n} period(s) only under {alt}"
        )
    if only_rule:
        typer.echo(
            f"  only rule {only_rule}: superseded_by_live={len(stats['superseded_by_live'])}"
        )
    for w in stats["warnings"]:
        typer.echo(f"  warning: {w}")
    for e in stats["errors"][:50]:
        typer.echo(f"  error: {e}")
    if stats["errors"]:
        raise typer.Exit(1)


@app.command("tagmap-plan")
def tagmap_plan_cmd(
    company_ids: str = typer.Option(
        ..., "--company-ids", help="Comma-separated core.company ids."
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Commit (default: plan, every company's transaction is rolled back).",
    ),
    before_image_dir: Path = typer.Option(
        None,
        "--before-image-dir",
        help="Required with --apply: before-image csv.gz directory.",
    ),
    fy_check: Path = typer.Option(
        Path("data-team/47-fsn-store/company_tag_map/fy_check_ranks_1_50.csv"),
        "--fy-check",
        help="CSV company_id,ticker,data_point,fy,period,status: the tag library's expected cells (FY0/FY-1).",
    ),
    docmap_reads: Path = typer.Option(
        None,
        "--docmap-reads",
        help="Directory of docmap reads: the expected FY0/FY-1 cells come from each company's docmap instead of --fy-check.",
    ),
    coverage_gate: bool = typer.Option(
        False,
        "--coverage-gate",
        help="With --apply: commit a company only when its eras cover the data window, it loses no FY0/FY-1 value and no value disappears without a reason.",
    ),
    coverage_gate_scope: str = typer.Option(
        "company",
        "--coverage-gate-scope",
        help="Default: new-only serving, every served cell of a tag-map company comes from the new system (value, derived value or reason); old rows are deleted, uncovered periods become era_unmapped blanks. company (with --coverage-gate): legacy, the gate rolls a whole company back.",
    ),
    dqc_report: Path = typer.Option(
        None,
        "--dqc-report",
        help="Run the DQC checks (data-team/tags/validations/dqc-checks.csv) on each company's served cells of this run and write the hits here (report only).",
    ),
    dqc_hold: bool = typer.Option(
        False,
        "--dqc-hold",
        help="With the DQC checks: a hit whose on_fail is 'hold the cell' removes that served cell and writes a visible defect reason instead.",
    ),
    statement_timeout: str = typer.Option("300s", help="Per-statement cap."),
) -> None:
    """Rule company_tag_map.select@1 for these companies: tag-map resolve, protection of every written key,
    ownership. Plan by default (rolled back); prints template cells vs valued / reasoned blank / NEITHER."""
    from scrooner_pipeline.mapper import company_tag_map_plan as plan

    ids = [int(x) for x in company_ids.split(",") if x.strip()]
    if apply and before_image_dir is None:
        typer.echo("ERROR --apply needs --before-image-dir", err=True)
        raise typer.Exit(2)
    with get_connection() as conn:
        conn.execute(f"set statement_timeout = '{statement_timeout}'")
        if docmap_reads is not None:
            from scrooner_pipeline.mapper import docmap_loader

            names = {
                n
                for (n,) in conn.execute(
                    "select name from analytics.canonical_concept"
                ).fetchall()
            }
            by_ticker = docmap_loader.companies_by_ticker(conn)
            tpl = {}
            for ticker, cells in docmap_loader.expected_cells(
                sorted(docmap_reads.glob("*-docmap-*.csv")), names
            ).items():
                for cid, _ in by_ticker.get(ticker, set()):
                    if cid in ids and len(by_ticker[ticker]) == 1:
                        tpl[cid] = cells
        else:
            tpl = plan.expected_cells_from_fy_check(fy_check, ids)
        if apply:
            typer.echo(
                f"before-image: {plan.write_before_image(conn, ids, before_image_dir)} -> {before_image_dir}"
            )
        from scrooner_pipeline.mapper import dqc_checks

        checks = dqc_checks.load_checks() if (dqc_report or dqc_hold) else None
        rep = plan.run(
            conn,
            ids,
            tpl,
            apply=apply,
            gate=coverage_gate,
            gate_scope=coverage_gate_scope,
            dqc_checks=checks,
            dqc_hold=dqc_hold,
        )
    if checks:
        all_hits = [h for r in rep.values() for h in r.get("dqc_hits", [])]
        if dqc_report:
            dqc_checks.write_report(all_hits, dqc_report)
        typer.echo(
            f"dqc: hits {dqc_checks.hits_by_check(all_hits)} held {sum(r.get('dqc_held', 0) for r in rep.values())}"
            f"{f' -> {dqc_report}' if dqc_report else ''}"
        )
    typer.echo(f"tagmap-plan [{'apply' if apply else 'plan'}]")
    for cid, r in rep.items():
        if "error" in r:
            typer.echo(f"  {cid}: ERROR {r['error']}")
            continue
        typer.echo(
            f"  {cid}: expected {r['template_cells']} valued {r['valued']} blank {r['reasoned_blank']} "
            f"library-status {r['library_status_only']} NEITHER {r['neither']} combined_lines {r['combined_lines']} "
            f"holds {r['holds']} conflicts {r['conflict_cells']} protected {r['protected_keys']} "
            f"neither_top {dict(list(r['neither_by_data_point'].items())[:6])}"
        )
        cov = r["coverage"]
        typer.echo(
            f"    coverage: era_from_min {cov['era_from_min']} era_short {len(cov['era_short'])} "
            f"values_lost {cov['values_lost']} held_with_reason {cov['values_held_with_reason']} "
            f"fy01 {cov['fy01_before']}->{cov['fy01_after']}/{cov['fy01_expected']}"
            f"{' GATED (rolled back)' if r.get('gated') else ''}"
        )
        if cov.get("skipped_concepts") is not None:
            typer.echo(
                f"      concept gate: rewritten {cov['rewritten_concepts']} skipped {len(cov['skipped_concepts'])} "
                f"(left as served): {dict(list(cov['skipped_concepts'].items())[:40])}"
            )
        if cov["era_short"]:
            typer.echo(f"      era_short {dict(list(cov['era_short'].items())[:8])}")
        for dp, period in r["neither_cells"][:40]:
            typer.echo(f"      NEITHER {dp} {period}")
    bad = {c: r["neither"] for c, r in rep.items() if r.get("neither")}
    if bad:
        typer.echo(f"expected cells with neither value nor reason: {bad}")


@app.command("dqc-check")
def dqc_check_cmd(
    company_ids: str = typer.Option(
        ..., "--company-ids", help="Comma-separated core.company ids."
    ),
    report: Path = typer.Option(
        ...,
        "--report",
        help="CSV of the hits (check_id, company, data point, period, values, on_fail, hold).",
    ),
    checks_csv: Path = typer.Option(
        None, "--checks", help="Default: data-team/tags/validations/dqc-checks.csv."
    ),
    statement_timeout: str = typer.Option("120s", help="Per-statement cap."),
) -> None:
    """DQC checks over the SERVED cells (analytics.canonical_fact) of these companies. Read only: a read-only
    transaction, nothing is written or held. Prints hits per check_id and per company, and the unsupported checks."""
    from scrooner_pipeline.mapper import dqc_checks

    ids = [int(x) for x in company_ids.split(",") if x.strip()]
    checks = dqc_checks.load_checks(checks_csv)
    impl, unsupported = dqc_checks.split_checks(checks)
    hits: list[dqc_checks.Hit] = []
    with get_connection() as conn:
        conn.read_only = True
        conn.execute(f"set statement_timeout = '{statement_timeout}'")
        for cid in ids:
            hits += dqc_checks.check_company(conn, cid, checks)
        conn.rollback()
    dqc_checks.write_report(hits, report)
    typer.echo(
        f"dqc-check: checks {len(checks)} implemented {len(impl)} unsupported {len(unsupported)}"
    )
    for cid_, reason in unsupported.items():
        typer.echo(f"  unsupported {cid_}: {reason}")
    typer.echo(f"  hits by check: {dqc_checks.hits_by_check(hits)}")
    for cid in ids:
        mine = [h for h in hits if h.company_id == cid]
        typer.echo(f"  {cid}: {len(mine)} hits {dqc_checks.hits_by_check(mine)}")
    typer.echo(f"  report -> {report}")


@app.command("split-rebase")
def split_rebase_cmd(
    ciks: str = typer.Option(
        ..., help="Comma-separated CIKs (always explicit: cohort / recent filers)."
    ),
    statement_timeout: str = typer.Option("120s", help="Per-statement cap."),
) -> None:
    """WO-22 SB-8: re-base per-share values and share counts onto the current
    share basis by source filing date (corporate_actions/share_basis.py).
    Rule split.event_basis@1: off (default) = no query, no write; dry_run =
    compute and print counts only; on = write through the archive (needs
    pershare.never_derive@1 on too, migrations 0098/0099 applied). Runs after
    resolve-facts and before conflict fills and the metric stages. Prints the
    run id: `scrooner-map split-rebase-restore --run-id <id>` undoes it."""
    import os
    import time

    from scrooner_pipeline.common import rule_flags
    from scrooner_pipeline.corporate_actions import share_basis

    mode = rule_flags.rule_mode(share_basis.RULE_ID)
    if mode == rule_flags.OFF:
        typer.echo("split-rebase: rule split.event_basis@1 is off; nothing done")
        return
    target = sorted({c.strip().zfill(10) for c in ciks.split(",") if c.strip()})
    run_id = (
        f"split-rebase-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{os.getpid()}"
    )
    with get_connection() as conn:
        conn.execute(f"set statement_timeout = '{statement_timeout}'")
        ids = [
            r[0]
            for r in conn.execute(
                "select id from core.company where cik = any(%s) order by id", (target,)
            ).fetchall()
        ]
        conn.commit()
        out = share_basis.run_split_rebase(conn, ids, run_id=run_id)
    counts: dict[str, int] = {}
    for res, _current in out.get("results", []):
        for c in res.cells:
            counts[c.status] = counts.get(c.status, 0) + 1
    typer.echo(
        f"split-rebase: mode={out['mode']} run_id={run_id if mode == rule_flags.ON else '-'} "
        f"companies={out['companies']} cells={counts}"
    )


@app.command("split-rebase-restore")
def split_rebase_restore_cmd(
    run_id: str = typer.Option(..., help="Run id printed by split-rebase."),
) -> None:
    """Undo one split-rebase run from analytics.canonical_fact_retired."""
    from scrooner_pipeline.mapper import canonical_archive

    with get_connection() as conn:
        with conn.transaction():
            n = canonical_archive.restore_run(conn.cursor(), run_id)
    typer.echo(f"split-rebase-restore: {run_id} restored {n} archive rows")


@app.command("resolve-concept-fallbacks")
def resolve_concept_fallbacks_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Doc 40: prefer-A-else-B merge for concepts needing a safe fallback
    resolve.py's sum/first_match modes can't express (today: total_debt,
    see mapper/concept_fallback.py's own module docstring). Run AFTER
    resolve-facts (reads its output), BEFORE calculate/calculate-piotroski
    (they should consume the *_resolved concept, not the original)."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    # run_tolerating_exit_commit_failure: same shape as ownership.py's
    # update_beneficial_ownership_cmd fix (2026-09-16) -- the outer conn
    # can sit idle long enough for the Supabase pooler to drop it,
    # surfacing only when the `with` block exits and psycopg's implicit
    # commit/close hits a dead socket, well after stats is already correct
    # and every company's own work already committed. Don't let that
    # crash a fully-successful run.
    stats = run_tolerating_exit_commit_failure(
        "resolve_concept_fallbacks_cmd",
        lambda conn: resolve_fallbacks(conn, target_ciks),
    )
    typer.echo(f"resolve-concept-fallbacks: {stats}")


@app.command("resolve-statement-fallbacks")
def resolve_statement_fallbacks_cmd() -> None:
    """Migration 0047 / 2026-09-07: gross_profit_resolved,
    cost_of_revenue_resolved, operating_expenses_resolved -- derives a
    missing Income Statement line from two other already-resolved concepts
    (e.g. Revenue - Cost of Revenue) when the primary tag is absent. Always
    population-wide (set-based SQL, no per-CIK scoping -- see
    concept_fallback.py's resolve_arithmetic_fallback docstring for why a
    loop-per-company shape was deliberately avoided). Run AFTER
    resolve-facts, BEFORE seed-statements' consumers render the company
    page (statements/classify.py's STATEMENT_LINES already points at the
    *_resolved concepts)."""
    with get_connection() as conn:
        stats = resolve_all_arithmetic_fallbacks(conn)
    typer.echo(f"resolve-statement-fallbacks: {stats}")


@app.command("resolve-balance-sheet-fallback")
def resolve_balance_sheet_fallback_cmd() -> None:
    """2026-10-05: total_liabilities_resolved/stockholders_equity_resolved
    from Assets = Liabilities + StockholdersEquity (+ NCI/temporary
    equity), doc 49's "low-risk first move" recommendation. Own CLI
    command, not folded into resolve-statement-fallbacks above -- this
    query joins analytics.canonical_fact against itself at full-population
    scale and was found live to risk the Supabase pooler's hard 2-minute
    statement_timeout under contention (confirmed: it ran cleanly in under
    2 minutes once optimized to look up the adjustment tags by concept_id
    first, but hit the cap when a prior run's stuck connection was still
    holding a lock on the same rows). If this command times out, run the
    same SQL directly via `psql "$DATABASE_URL" -f <script starting with
    SET statement_timeout = 0;>`, detached (nohup + disown) -- the
    documented pattern for any long admin DDL/DML against this project's
    pooled connection (pipeline/CLAUDE.md's 2026-09-21 entry). Purely
    additive (ON CONFLICT DO NOTHING) -- safe to run any time after
    resolve-facts, in any order relative to resolve-statement-fallbacks/
    resolve-conflict-fills/resolve-dedup-holes, since it can only fill a
    still-empty cell, never overwrite another writer's value."""
    with get_connection() as conn:
        stats = resolve_all_balance_sheet_identity_fallbacks(conn)
    typer.echo(f"resolve-balance-sheet-fallback: {stats}")


@app.command("balance-identity-dry-run")
def balance_identity_dry_run_cmd(
    ciks: str = typer.Option(
        "", help="Comma-separated CIKs; empty = every company with total assets."
    ),
    out: Path = typer.Option(
        Path("balance_identity_plan.jsonl"), help="Before-image / plan file (JSONL)."
    ),
) -> None:
    """Read-only: print the corrected balance-sheet identity values (rule balance.identity_equity_basis@1)
    next to what is stored. Writes nothing to the database."""
    from scrooner_pipeline.mapper import balance_identity

    with get_connection() as conn:
        conn.execute("set statement_timeout = 20000")
        with conn.cursor() as cur:
            if ciks.strip():
                cur.execute(
                    "select id from core.company where cik = any(%s) order by id",
                    ([c.strip() for c in ciks.split(",")],),
                )
            else:
                cur.execute(
                    "select distinct cf.company_id from analytics.canonical_fact cf join analytics.canonical_concept cc "
                    "on cc.id = cf.canonical_concept_id where cc.name = %s order by 1",
                    (balance_identity.ASSETS,),
                )
            ids = [r[0] for r in cur.fetchall()]
        plan = balance_identity.plan_identity(conn, ids)
        conn.rollback()
    balance_identity.write_before_image(out, plan)
    typer.echo(
        f"balance-identity-dry-run: {len(plan)} cells planned for {len(ids)} companies -> {out}"
    )


@app.command("resolve-revenue")
def resolve_revenue_cmd(
    include_parser: bool = typer.Option(
        False,
        "--include-parser",
        help="Also run the rendered-report parser resolver (does its own SEC fetches).",
    ),
) -> None:
    """Runs every registered resolver in mapper/revenue_resolvers/
    (2026-10-02) against revenue_sanity_resolved, in registry order:
    the resolve()-authoritative-$0 tag-preference sweep, collaboration-
    arrangement revenue (additive, biotech/pharma), net-lease REIT
    income (substitute, evidence-gated), and -- only with
    --include-parser -- the rendered-report parser for dimensionally-
    stripped filers. Run AFTER resolve-facts (the collaborative/
    net-lease concepts need their own canonical_fact rows to exist
    first). Replaces the old resolve-revenue-root-cause-fixes command --
    see mapper/revenue_resolvers/__init__.py for why this is a registry
    now, not one bespoke function per discovered company-shape."""
    with get_connection() as conn:
        results = run_revenue_resolvers(conn, include_parser=include_parser)
    for name, stats in results.items():
        typer.echo(f"resolve-revenue: {name}={stats}")


@app.command("resolve-dedup-holes")
def resolve_dedup_holes_cmd() -> None:
    """mapper/dedup_majority_resolver.py (2026-10-03): population-wide fix
    for the Stage 2e "all-non-authoritative" dedup-hole bug, generalized
    beyond revenue to the 8 balance-sheet/instant concepts a live sample
    confirmed safe for majority-vote (88-97% clean agreement among
    disagreeing raw facts): total_assets, current_assets,
    current_liabilities, total_liabilities, stockholders_equity,
    shares_outstanding, basic_eps, diluted_eps. Income-statement/cash-flow
    concepts (revenue, net_income, cfo, gross_profit, operating_income,
    etc.) were deliberately NOT included -- only 68-75% clean agreement,
    confirmed on Abbott Labs FY2012 operating_income (3 raw rows, 3
    genuinely different values, no safe majority) -- needs its own,
    more careful mechanism, not blind majority vote. Safe to rerun
    (delete-free upsert, idempotent)."""
    with get_connection() as conn:
        results = resolve_all_safe_concepts(conn)
    for name, stats in results.items():
        typer.echo(f"resolve-dedup-holes: {name}={stats}")


@app.command("resolve-employee-count-fallback")
def resolve_employee_count_fallback_cmd(
    ciks: str = typer.Option(
        ..., help="Comma-separated CIKs to restrict to -- no default, always explicit."
    ),
) -> None:
    """2026-09-12: employee_count_resolved -- prefers XBRL
    dei:EntityNumberOfEmployees, else core.employee_headcount_disclosure
    (10-K prose extraction), else core.company.y_employee_count
    (yfinance). See concept_fallback.py's own comment above this
    function for why this is company-level, not period-level, unlike
    every other fallback in that module."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")}
    with get_connection() as conn:
        stats = resolve_employee_count_fallback(conn, target_ciks)
    typer.echo(f"resolve-employee-count-fallback: {stats}")


@app.command("resolve-conflict-fills")
def resolve_conflict_fills_cmd() -> None:
    """Migration 0059 / 2026-09-09: fills a statement-table cell that's
    null specifically because dedupe.py correctly flagged 2+ disagreeing
    filings as an unresolved conflict (never guessed at before now),
    for all 24 statement-table concepts. Purely additive (INSERT ... ON
    CONFLICT DO NOTHING, never a delete) -- run AFTER resolve-facts and
    resolve-statement-fallbacks (this fills gaps those leave, and being
    additive-only it can't be undone by anything that runs after it,
    only by something that runs after it and re-DELETEs its own resolved
    concept, which none of the 24 targets' other writers do at this
    point in the pipeline). Always population-wide, set-based SQL."""
    with get_connection() as conn:
        stats = resolve_all_conflict_fills(conn)
    typer.echo(f"resolve-conflict-fills: {stats}")


@app.command("seed-definitions")
def seed_definitions_cmd() -> None:
    """Stage 3c: seed analytics.metric_definition + metric_definition_input for doc 02's 18 locked metrics."""
    with get_connection() as conn:
        stats = definitions_module.seed(conn)
    typer.echo(f"seed-definitions: {stats}")


@app.command("calculate")
def calculate_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Stage 3d: compute analytics.metric_value for the 10 EDGAR-only,
    non-growth metrics. Requires Stages 3a/3b/3c to have already run."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = calculate(conn, target_ciks)
    typer.echo(f"calculate: {stats}")


@app.command("growth")
def growth_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Stage 3e (part 1): compute revenue/EPS growth (YoY + 3Y CAGR)."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = compute_growth(conn, target_ciks)
    typer.echo(f"growth: {stats}")


@app.command("ttm-returns")
def ttm_returns_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Stage 3e (part 2): compute TTM ROIC/ROE for quarterly periods."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = compute_ttm_returns(conn, target_ciks)
    typer.echo(f"ttm-returns: {stats}")


@app.command("ttm-margins")
def ttm_margins_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """2026-09-13: compute TTM gross/operating/net margin for quarterly
    periods -- found live that these 3 locked V1 metrics were never
    computed as TTM at all (only a raw single-quarter ratio), the same bug
    class already fixed once for roic/roe (see ttm-returns above), just
    never applied here. Screener/resolve.py's own TTM-preferred rule picks
    these up automatically once they exist, no screener code change
    needed. See mapper/ttm.py's MARGIN_CONCEPTS docstring for the full
    finding and verification."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = compute_ttm_margins(conn, target_ciks)
    typer.echo(f"ttm-margins: {stats}")


@app.command("seed-statements")
def seed_statements_cmd() -> None:
    """Doc 17 Sec 4 / doc 23 Stage B: seed statement-display-only canonical
    concepts (cost_of_revenue, public_float, etc.) additively, alongside
    Mapper's frozen 17. Run resolve-facts after this to populate values."""
    with get_connection() as conn:
        stats = seed_statements(conn)
    typer.echo(f"seed-statements: {stats}")


@app.command("calculate-price-metrics")
def calculate_price_metrics_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Stage 3h (doc 25 follow-on): compute the 6 price-dependent metrics
    (Market Cap, Trailing P/E, Price/Sales, Price/Book, Dividend Yield,
    FCF Yield) from core.market_price_alpaca's real price + TTM
    fundamentals. Requires update-market-price to have run first."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = calculate_price_metrics(conn, target_ciks)
    typer.echo(f"calculate-price-metrics: {stats}")


@app.command("seed-expanded-concepts")
def seed_expanded_concepts_cmd() -> None:
    """Doc 18 Tier A / doc 26 (2026-08-18): seed inventory/sbc/
    depreciation_and_amortization additively, alongside Mapper's frozen
    17 and doc 17's statement concepts. Run resolve-facts after this."""
    with get_connection() as conn:
        stats = expanded_concepts.seed(conn)
    typer.echo(f"seed-expanded-concepts: {stats}")


@app.command("seed-expanded-definitions")
def seed_expanded_definitions_cmd() -> None:
    """Doc 18 Tier A / doc 26 (2026-08-18): seed roa/quick_ratio/
    sbc_pct_revenue/ebitda (real calculate.py-engine inputs) plus
    documentation-only rows for the 6 EBITDA/price-based ratios computed
    in expanded_metrics.py. Run calculate after this."""
    with get_connection() as conn:
        stats = expanded_definitions.seed(conn)
    typer.echo(f"seed-expanded-definitions: {stats}")


@app.command("calculate-expanded-metrics")
def calculate_expanded_metrics_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Doc 18 Tier A / doc 26 (2026-08-18): Net Debt/EBITDA, EV/EBITDA,
    EV/Sales, PEG, Buyback Yield, Total Shareholder Yield. Requires
    calculate (for ebitda) and calculate-price-metrics (for market_cap/
    trailing_pe/dividend_yield) to have already run."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = calculate_expanded_metrics(conn, target_ciks)
    typer.echo(f"calculate-expanded-metrics: {stats}")


@app.command("calculate-piotroski")
def calculate_piotroski_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Doc 26 Sec 2 (2026-08-19): standard 9-test Piotroski F-Score (0-9),
    FY vs prior FY. Requires seed-expanded-definitions (for the metric_
    definition row) and resolve-facts (for the 9 raw concepts) to have
    already run. Correctly null for financial institutions -- see
    mapper/quality_score.py's module docstring."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = calculate_piotroski(conn, target_ciks)
    typer.echo(f"calculate-piotroski: {stats}")


@app.command("calculate-quality-flags")
def calculate_quality_flags_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Doc 26 Sec 2.9 (2026-08-19): fcf_gt_net_income, zero_debt,
    profitable_streak_years, margin_expanding_3yr. Requires
    seed-expanded-definitions and resolve-facts to have already run."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = calculate_quality_flags(conn, target_ciks)
    typer.echo(f"calculate-quality-flags: {stats}")


@app.command("calculate-reconciliation")
def calculate_reconciliation_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Core-fact-utilization-study.md #2 (2026-08-21): AR/Inventory/AP
    cash-flow-vs-balance-sheet reconciliation gaps, a quality-of-earnings
    cross-check, FY-only. Requires seed-expanded-concepts,
    seed-expanded-definitions, and resolve-facts to have already run."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = calculate_reconciliation(conn, target_ciks)
    typer.echo(f"calculate-reconciliation: {stats}")


@app.command("calculate-tax-reconciliation")
def calculate_tax_reconciliation_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Utilization-study ranked #5 (2026-08-22): effective_tax_rate_gap,
    a cross-check between the reported effective tax rate and ROIC's own
    internally-derived rate. Requires seed-expanded-concepts,
    seed-expanded-definitions, and resolve-facts to have already run."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = calculate_tax_reconciliation(conn, target_ciks)
    typer.echo(f"calculate-tax-reconciliation: {stats}")


@app.command("calculate-fcf-growth")
def calculate_fcf_growth_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Doc 18 Tier A (2026-08-22): fcf_growth_3y_cagr/5y_cagr. Requires
    calculate (for fcf) to have already run."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = calculate_fcf_growth(conn, target_ciks)
    typer.echo(f"calculate-fcf-growth: {stats}")


@app.command("calculate-dividend-streak")
def calculate_dividend_streak_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Doc 26 (2026-08-22): dividend_growth_streak_years. Requires
    seed-expanded-definitions and resolve-facts to have already run."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = calculate_dividend_streak(conn, target_ciks)
    typer.echo(f"calculate-dividend-streak: {stats}")


@app.command("snapshot-coverage")
def snapshot_coverage_cmd() -> None:
    """Doc 41 (2026-09-02): compute and persist today's data-point
    coverage (per canonical_concept, per active metric_definition, plus
    the two aggregate avg_*_coverage_score rows) to
    analytics.coverage_snapshot. Whole-population, no --ciks scoping --
    run once per day after the day's calculate-family stages finish."""
    with get_connection() as conn:
        stats = write_snapshot(conn)
        group_stats = write_group_snapshot(conn)
    typer.echo(f"snapshot-coverage: {stats}")
    typer.echo(f"snapshot-coverage groups: {group_stats}")


@app.command("seed-sector-templates")
def seed_sector_templates_cmd(
    templates: Path = typer.Option(
        Path("data-team/strategy/SECTOR-TEMPLATES-2026-11-01.md"),
        help="Templates file (sector defaults plus company overrides).",
    ),
    cohort: Path = typer.Option(
        Path("doc/data-moat/team/top1000/shards.csv"),
        help="Cohort file with company_id, cik, sic; excluded rows are skipped.",
    ),
    plan_out: Path = typer.Option(
        Path("pipeline/scripts/results/sector_templates_plan.csv"),
        help="Where the dry-run plan CSV is written.",
    ),
    validate_db: bool = typer.Option(
        False,
        help="Also check data-point names and company ids against the database (read-only).",
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Write analytics.company_data_point_template. Needs the founder's words.",
    ),
    confirm_version: str = typer.Option(
        "", help="With --apply: must equal the file's template_version."
    ),
) -> None:
    """Doc 02 ruling 2026-11-01: seed each cohort company's sector template (migration
    0120). Dry run by default: builds the plan from files only and writes a CSV."""
    from scrooner_pipeline.mapper import sector_templates as st

    for path in (templates, cohort):
        if not path.exists():
            typer.echo(f"ERROR file not found: {path}", err=True)
            raise typer.Exit(2)
    try:
        parsed = st.parse_templates(templates.read_text(encoding="utf-8"))
        companies = st.load_cohort(cohort)
        if not st.cohort_has_sic(cohort):
            # e.g. data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv: one read
            with get_connection() as conn:
                companies = st.fill_sic_from_db(conn, companies)
        rows = st.build_plan(parsed, companies)
    except st.TemplateError as exc:
        for problem in exc.problems:
            typer.echo(f"ERROR {problem}", err=True)
        raise typer.Exit(2) from exc
    st.write_plan_csv(rows, plan_out)
    typer.echo(
        f"seed-sector-templates plan: {json.dumps(st.summarize(rows))} -> {plan_out}"
    )
    if not (validate_db or apply):
        return
    if apply and confirm_version != parsed.template_version:
        typer.echo(
            f"ERROR --apply needs --confirm-version {parsed.template_version}", err=True
        )
        raise typer.Exit(2)
    with get_connection() as conn:
        try:
            st.validate_against_db(conn, rows)
        except st.TemplateError as exc:
            for problem in exc.problems:
                typer.echo(f"ERROR {problem}", err=True)
            raise typer.Exit(2) from exc
        typer.echo("seed-sector-templates: data points and company ids valid")
        if apply:
            typer.echo(f"seed-sector-templates applied: {st.write_plan(conn, rows)}")


@app.command("seed-templates-from-catalog")
def seed_templates_from_catalog_cmd(
    catalog: Path = typer.Option(
        Path("data-team/47-fsn-store/company_tag_map/concepts_catalog.csv"),
        help="Concept list (column name).",
    ),
    cohort: Path = typer.Option(
        Path("doc/data-moat/team/top1000/shards.csv"),
        help="Cohort file with rank, company_id, cik, ticker, sic, excluded.",
    ),
    top_n: int = typer.Option(110, help="Ranks 1..N only."),
    plan_out: Path = typer.Option(
        Path("pipeline/scripts/results/catalog_template_plan.csv"),
        help="Plan CSV (always written).",
    ),
    before_out: Path = typer.Option(
        Path("pipeline/scripts/results/catalog_template_before_image.csv"),
        help="Before-image CSV of existing rows (written with --validate-db or --apply).",
    ),
    validate_db: bool = typer.Option(
        False, help="Read-only DB validation and before-image."
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Write the rows (founder-approved)."
    ),
    confirm_version: str = typer.Option(
        "", help="With --apply: must equal the catalog version."
    ),
) -> None:
    """Seed analytics.company_data_point_template from the concept catalog and each
    company's SIC group, for ranks 1..N. Dry run by default; idempotent when applied."""
    from scrooner_pipeline.mapper import sector_templates as st

    try:
        concepts = st.load_catalog(catalog)
        companies, excluded = st.load_ranked_cohort(cohort, top_n)
        rows = st.build_catalog_plan(concepts, companies)
    except (st.TemplateError, OSError) as exc:
        typer.echo(f"ERROR {exc}", err=True)
        raise typer.Exit(2) from exc
    st.write_plan_csv(rows, plan_out)
    per_group = st.rows_per_company_group(rows)
    typer.echo(
        f"catalog {len(concepts)} concepts; {len(companies)} companies; {len(rows)} rows"
    )
    typer.echo(f"per group: {json.dumps(per_group)}")
    counts: dict[int, tuple[str, str, int]] = {}
    tick = {c.company_id: c.ticker for c in companies}
    for r in rows:
        g, t, n = counts.get(r.company_id, (r.template, tick[r.company_id], 0))
        counts[r.company_id] = (g, t, n + (1 if r.in_template else 0))
    for cid, (g, t, n) in sorted(counts.items(), key=lambda kv: kv[1][1]):
        typer.echo(f"  {t:6} {g:12} in_template={n}")
    for rank, ticker, why in excluded:
        typer.echo(f"EXCLUDED (no template) rank {rank} {ticker}: {why}")
    if not (validate_db or apply):
        return
    if apply and confirm_version != st.CATALOG_VERSION:
        typer.echo(
            f"ERROR --apply needs --confirm-version {st.CATALOG_VERSION}", err=True
        )
        raise typer.Exit(2)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from pg_stat_activity")
            active = cur.fetchone()[0]  # type: ignore[index]
        typer.echo(f"pg_stat_activity count: {active}")
        if active > 60:
            typer.echo("ERROR pg_stat_activity > 60; pausing", err=True)
            raise typer.Exit(3)
        try:
            st.validate_against_db(conn, rows)
        except st.TemplateError as exc:
            typer.echo(f"ERROR {exc}", err=True)
            raise typer.Exit(2) from exc
        n_before = st.write_before_image(
            conn, sorted({r.company_id for r in rows}), before_out
        )
        typer.echo(f"before-image: {n_before} existing rows -> {before_out}")
        if apply:
            typer.echo(f"applied: {st.write_plan(conn, rows)}")


@app.command()
def errors(
    stage: str = typer.Option(
        None,
        help="Restrict to one stage (resolve, calculate, growth, ttm_returns, price_metrics).",
    ),
    unresolved_only: bool = typer.Option(
        True, help="Only print rows with resolved=false."
    ),
    limit: int = typer.Option(50, help="Max rows to print."),
) -> None:
    """Dead-letter report over analytics.mapper_error (Phase 1 scaling
    foundation) -- read-only, no writes. One row per company whose mapping/
    calculation failed with an unhandled exception; the batch itself keeps
    going past a single company's failure."""
    conditions, params = [], []
    if stage:
        conditions.append("stage = %s")
        params.append(stage)
    if unresolved_only:
        conditions.append("not resolved")
    where = f"where {' and '.join(conditions)}" if conditions else ""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"select id, cik, stage, error_type, message, occurred_at, resolved "
                f"from analytics.mapper_error {where} order by occurred_at desc limit %s",
                (*params, limit),
            )
            rows = cur.fetchall()
    typer.echo(f"{len(rows)} row(s)")
    for row in rows:
        typer.echo(f"  {row}")


@app.command("validate")
def validate_cmd() -> None:
    """Stage 3f: confidence-state distribution, non-authoritative-leak check,
    and source_fact_ids lineage integrity across the whole analytics schema
    (not scoped to a CIK set -- these are global invariants)."""
    with get_connection() as conn:
        result = validate_module.run(conn)
    typer.echo(f"validate: {result}")
    if not result["clean"]:
        raise typer.Exit(1)


@app.command("run-parser")
def run_parser_cmd(
    concept_name: str = typer.Argument(
        ..., help=f"Registered: {sorted(PARSER_REGISTRY)}"
    ),
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: full gap population)."
    ),
) -> None:
    """Doc 42 Parser 3 architecture: run the dedicated rendered-report
    parser registered for one canonical concept (see parsers/main_parser.py's
    own module docstring for the 3-tier resolution order this fits into).
    Automatically skips companies already resolved via XBRL tag matching
    and companies this parser has already attempted before (see
    analytics.concept_parser_attempt) -- safe and efficient to rerun."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else None
    with get_connection() as conn:
        result = run_parser(conn, concept_name, target_ciks)
    typer.echo(f"run-parser {concept_name}: {result['stats']}")


@app.command("resolve-parser-results")
def resolve_parser_results_cmd(
    concept_name: str = typer.Argument(
        ..., help="Concept whose analytics.concept_parser_result rows to merge."
    ),
) -> None:
    """Merges run-parser's output into the concept's *_sanity_resolved
    display concept (doc 42's Tier 3) -- run-parser alone only writes to
    analytics.concept_parser_result, which nothing else reads; this is
    the step that makes a parsed value actually reach the company page/
    screener. Always run right after run-parser for the same concept."""
    with get_connection() as conn:
        stats = resolve_parser_results(conn, concept_name)
    typer.echo(f"resolve-parser-results {concept_name}: {stats}")


@app.command("parser-registry-summary")
def parser_registry_summary_cmd() -> None:
    """Read-only: for every (concept, parser) pair ever attempted, real
    counts of matched/no_report/no_row_matched/errored -- the 'which
    parser resolved this' view doc 42's routing table exists for."""
    with get_connection() as conn:
        rows = registry_summary(conn)
    for row in rows:
        typer.echo(f"  {row}")


@app.command("probe-filing-lines")
def probe_filing_lines_cmd(
    ciks: str = typer.Option(
        None,
        help="Comma-separated CIKs to restrict to (default: every active company whose evidence is missing or stale).",
    ),
    limit: int = typer.Option(None, help="Stop after this many companies."),
    max_minutes: float = typer.Option(
        None,
        help="Stop starting new companies after this many minutes (the rest are picked up next run).",
    ),
    force: bool = typer.Option(
        False, help="Re-read companies whose evidence is already current."
    ),
) -> None:
    """Per-company filing-line evidence (parsers/filing_line_evidence.py, migration
    0093): does each concept's line appear on the face of the company's latest
    10-K/10-Q balance sheet or income statement? Incremental -- only companies whose
    latest filing changed are re-read (3 SEC requests each, shared rate limiter).
    Run build-coverage-matrix afterwards: it turns the evidence into gap reasons, and
    snapshot-coverage then uses them for denominators."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else None
    stats = run_tolerating_exit_commit_failure(
        "probe_filing_lines",
        lambda conn: run_filing_line_evidence(
            conn,
            target_ciks,
            limit=limit,
            max_seconds=max_minutes * 60 if max_minutes else None,
            force=force,
        ),
    )
    typer.echo(f"probe-filing-lines: {stats}")


@app.command("build-coverage-matrix")
def build_coverage_matrix_cmd() -> None:
    """2026-09-05: the two-table coverage system (registry + per-company
    yes/no). Rebuilds both from scratch each run -- never hand-edited,
    can't drift from concept_mapping/metric_definition_input/
    canonical_fact/metric_value/the ownership tables. build_coverage()
    already internally chains classify_concept_gaps() and classify_
    company_populations() (confirmed by reading it 2026-10-03, not
    assumed) -- this single command is the complete rebuild, no
    additional step needed."""
    with get_connection() as conn:
        registry_stats = build_registry(conn)
        coverage_stats = build_coverage(conn)
    typer.echo(f"registry: {registry_stats}")
    typer.echo(f"coverage: {coverage_stats}")


@app.command("company-coverage")
def company_coverage_cmd(
    company_id: int = typer.Option(..., "--company-id", help="core.company.id"),
) -> None:
    """2026-10-03, by direct request: company-wise coverage, not metric-
    wise -- "for Visa, what does it have and why is anything missing."
    3-state classification (present / not applicable / genuine gap),
    every absence given a human-readable note. Run build-coverage-matrix
    first so company_data_point_coverage/company_population are fresh."""
    with get_connection() as conn:
        summary = summarize_company(conn, company_id)
    typer.echo(render_markdown_company(summary))


@app.command("company-coverage-report")
def company_coverage_report_cmd(
    limit: int = typer.Option(50, "--limit"),
    best: bool = typer.Option(
        False, "--best", help="Rank best-covered first instead of worst."
    ),
) -> None:
    """2026-10-03: population-wide ranking of the same 3-state coverage
    used by company-coverage, one row per active company. Worst-first by
    default -- the real-gap worklist."""
    with get_connection() as conn:
        rows = summarize_population(conn)
    typer.echo(render_markdown_population(rows, limit=limit, worst_first=not best))


@app.command("corrected-coverage-report")
def corrected_coverage_report_cmd() -> None:
    """2026-09-12: reports every registry data point's coverage against
    its real applicable_population (real_operating_company/dividend_payer/
    buyback_company/capital_return_company/bdc_company), not against all
    active companies -- see coverage_matrix.py's own module comment and
    doc/data-moat/learnings/2026-09-12-corrected-coverage-denominator-methodology.md.
    Run build-coverage-matrix first."""
    with get_connection() as conn:
        rows = corrected_coverage_report(conn)
    for row in rows:
        pct = (
            100 * row["has_value"] / row["population_size"]
            if row["population_size"]
            else 0.0
        )
        typer.echo(
            f"{row['data_point_type']:8s} {row['data_point_name']:40s} "
            f"{row['has_value']:>5}/{row['population_size']:<5} ({pct:5.1f}%)  pop={row['applicable_population']}"
        )


@app.command("build-tag-candidates")
def build_tag_candidates_cmd() -> None:
    """2026-09-08: retires reference/xbrl_tag_coverage_library.json
    (doc 40) into analytics.concept_tag_candidate -- the DB-native
    record of candidate UNMAPPED XBRL tags per canonical concept, ranked
    by real company count. The one thing the JSON library had that the
    coverage matrix didn't; now the single DB source of truth for both.
    Every candidate is still a LEAD to investigate, never an approval --
    see tag_candidates.py's module docstring."""
    with get_connection() as conn:
        stats = build_tag_candidates(conn)
    typer.echo(f"tag-candidates: {stats}")


@app.command("tag-candidate-report")
def tag_candidate_report_cmd() -> None:
    """Reads back the current concept-by-concept status
    (well_covered / gap_safe_candidate_found / gap_needs_fallback_resolver
    / gap_no_safe_candidate) computed live from analytics.canonical_fact
    coverage + analytics.concept_tag_candidate -- read-only, safe any time."""
    with get_connection() as conn:
        rows = report_status(conn)
    for row in rows:
        top = (
            f"{row['top_candidate'][0]} ({row['top_candidate'][1]} cos)"
            if row["top_candidate"]
            else "-"
        )
        typer.echo(
            f"{row['concept']:<32} {row['coverage_pct']:>5}%  {row['status']:<28} top candidate: {top}"
        )


@app.command("build-tag-library")
def build_tag_library_cmd(
    ciks: str = typer.Option(
        None,
        help="Comma-separated CIKs to restrict to (default: every company with facts).",
    ),
    stages: str = typer.Option(
        None,
        help="Comma-separated subset of company_tags,library,lineage,leads (default: all).",
    ),
    leads_budget_minutes: float = typer.Option(
        40,
        help="Wall-clock budget for scoring leads; concepts not reached keep their previous leads.",
    ),
) -> None:
    """2026-09-27: the SEC Tag Library (migration 0077) -- every tag x every
    company (analytics.company_sec_tag), tag -> concepts/metrics
    (analytics.sec_tag_library), and company x concept -> the source tag
    behind our value (analytics.company_concept_lineage). See
    mapper/tag_library.py. Run after resolve-facts/build-coverage-matrix/
    build-tag-candidates so lineage reflects the current values."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else None
    target_stages = {s.strip() for s in stages.split(",")} if stages else None
    with get_connection() as conn:
        stats = build_tag_library(
            conn,
            target_ciks,
            target_stages,
            leads_budget_seconds=leads_budget_minutes * 60,
        )
    typer.echo(f"tag-library: {stats}")


@app.command("gap-tags")
def gap_tags_cmd(
    concept: str = typer.Argument(
        ..., help="Canonical concept name, e.g. total_debt_resolved."
    ),
    limit: int = typer.Option(25, help="Max tags to print."),
) -> None:
    """Lift-ranked tag leads for active companies MISSING `concept`
    (analytics.concept_gap_lead). Leads only: coexistence-check each one,
    then record the outcome with `record-verdict`."""
    with get_connection() as conn:
        rows = gap_tags(conn, concept, limit=limit)
    if rows:
        typer.echo(f"{rows[0]['missing_total']} active companies missing {concept}")
    for r in rows:
        typer.echo(
            f"  #{r['rank']:<3} {r['missing_companies_filing']:>5} of missing file it  "
            f"{r['tag']:<70} agrees {float(r['agree_rate']):.0%} on {r['coexist_pairs']} overlapping periods"
        )


@app.command("gap-report")
def gap_report_cmd(
    limit: int = typer.Option(15, help="Rows per section."),
) -> None:
    """The fix queue from the data truth layer (migration 0080): concepts by
    unexplained missing market cap, metrics by unexplained gaps, and the
    largest companies missing core data. Explained = a recorded gap_reason
    or a company_data_finding. Rebuild the tag library first if stale."""
    with get_connection() as conn:
        report = gap_report(conn, limit=limit)
    typer.echo("CONCEPTS (by unexplained missing market cap)")
    for c, cov, miss, expl, unexpl, mcap, lead, lead_n, agree in report["concepts"]:
        mcap_b = f"${float(mcap) / 1e9:,.0f}B" if mcap else "-"
        lead_s = f"{lead} ({lead_n} cos, {float(agree):.0%} agree)" if lead else "-"
        typer.echo(
            f"  {c:<34} {cov or 0:>5}%  missing {miss:>5} (explained {expl:>5}, unexplained {unexpl:>5}, {mcap_b:>8})  lead: {lead_s}"
        )
    typer.echo("METRICS (by unexplained missing companies)")
    for m, cov, miss, unexpl, inputs in report["metrics"]:
        typer.echo(
            f"  {m:<34} {cov or 0:>5}%  missing {miss:>5} (unexplained {unexpl:>5})  inputs: {inputs or '-'}"
        )
    typer.echo("COMPANIES (largest with unexplained core gaps)")
    for t, name, mcap, miss, unexpl, concepts, findings in report["companies"]:
        mcap_b = f"${float(mcap) / 1e9:,.1f}B" if mcap else "-"
        typer.echo(
            f"  {t or '?':<7} {name[:30]:<30} {mcap_b:>9}  missing {miss} ({unexpl} unexplained): {concepts}  findings={findings}"
        )


@app.command("record-verdict")
def record_verdict_cmd(
    tag: str = typer.Argument(..., help="XBRL tag, e.g. NotesPayable."),
    concept: str = typer.Argument(..., help="Canonical concept, e.g. total_debt."),
    verdict: str = typer.Argument(
        ...,
        help="approved | needs_review | rejected | different_concept | partial_component",
    ),
    reason: str = typer.Argument(..., help="One sentence: what the evidence showed."),
    taxonomy: str = typer.Option("us-gaap"),
) -> None:
    """Record an investigation's conclusion about a (tag, concept) pair in
    analytics.tag_concept_verdict, so the gap leads never re-propose it."""
    with get_connection() as conn:
        record_verdict(conn, tag, concept, verdict, reason, taxonomy=taxonomy)
    typer.echo(f"recorded: {taxonomy}:{tag} -> {concept} = {verdict}")


@app.command("record-finding")
def record_finding_cmd(
    ticker: str = typer.Argument(...),
    finding_type: str = typer.Argument(
        ..., help="pipeline_bug | filer_error | legitimate_absence | data_limit"
    ),
    summary: str = typer.Argument(...),
    concept: str = typer.Option(None, help="Canonical concept, if concept-specific."),
    status: str = typer.Option("open", help="open | fixed | wont_fix"),
) -> None:
    """Record a per-company finding in analytics.company_data_finding."""
    with get_connection() as conn:
        record_finding(
            conn, ticker, finding_type, summary, concept_name=concept, status=status
        )
    typer.echo(f"recorded: {ticker} {finding_type} ({status})")


@app.command("calculator-registry")
def calculator_registry_cmd() -> None:
    """Doc 42: for every real metric_definition, which module computes
    it and via which CLI command. Also flags any metric this registry
    doesn't yet know about (should be empty -- a non-empty result means
    a new metric was seeded without updating mapper/main_calculator.py
    in the same pass)."""
    with get_connection() as conn:
        missing = unregistered_metrics(conn)
    for name in sorted(METRIC_CALCULATOR_REGISTRY):
        entry = METRIC_CALCULATOR_REGISTRY[name]
        typer.echo(f"  {name:<38} -> {entry['module']:<38} ({entry['cli_command']})")
    if missing:
        typer.echo(f"\nUNREGISTERED (fix main_calculator.py): {missing}")


if __name__ == "__main__":
    app()
