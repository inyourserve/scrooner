"""Typer CLI `scrooner-fsn`: the company-wise FSN statement store."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

import typer

app = typer.Typer(help="Company-wise FSN statement store (design 2026-11-01).")
SHARDS_CSV = Path("doc/data-moat/team/top1000/shards.csv")


@app.callback()
def _root() -> None:
    """Subcommands: shard, load, seed-rules, pilot, pilot-prod, done-gate, extract-sec, nightly."""


def _predecessors(spec: str) -> dict[str, str]:
    """'pred=succ,pred=succ' -> {predecessor cik: successor cik} (a registrant reorganised into a
    new holding company keeps its history under the successor's company)."""
    out: dict[str, str] = {}
    for pair in (p for p in spec.split(",") if p.strip()):
        pred, succ = pair.split("=")
        out[pred.strip().zfill(10)] = succ.strip().zfill(10)
    return out


def _db_predecessors(conn) -> dict[str, str]:
    """predecessor cik -> company cik from core.company_history_source (migration 0121), for load."""
    alias, _ = _db_history(conn)
    return {p: v[0][0] for p, v in alias.items()}


def _db_history(conn) -> tuple[dict, dict]:
    """core.company_history_source -> (alias: predecessor cik -> [(company cik, from, to)],
    exclude: company cik -> [(from, to)]), dates as YYYYMMDD (FSN sub.period form)."""
    alias: dict[str, list[tuple[str, str, str]]] = {}
    exclude: dict[str, list[tuple[str, str]]] = {}
    if (
        conn.execute("select to_regclass('core.company_history_source')").fetchone()[0]
        is None
    ):
        return alias, exclude
    rows = conn.execute(
        """select h.source_cik, c.cik, h.relation, to_char(h.valid_from, 'YYYYMMDD'), to_char(h.valid_to, 'YYYYMMDD')
           from core.company_history_source h join core.company c on c.id = h.company_id"""
    ).fetchall()
    for src, cik, rel, f, t in rows:
        if rel == "predecessor":
            alias.setdefault(src, []).append((cik, f, t))
        else:
            exclude.setdefault(src, []).append((f, t))
    return alias, exclude


def _cohort(shards_file: Path) -> list[str]:
    for cand in (shards_file, Path(__file__).resolve().parents[4] / shards_file):
        if cand.exists():
            return sorted(
                {r["cik"] for r in csv.DictReader(cand.open()) if not r.get("excluded")}
            )
    raise FileNotFoundError(shards_file)


@app.command("shard")
def shard_cmd(
    out: str = typer.Option("companies", help="Output root: companies/<cik>/"),
    ciks: str = typer.Option(
        "", help="Comma-separated CIKs (default: the top-1000 cohort)."
    ),
    periods: str = typer.Option(
        "", help="Comma-separated FSN sets (default: every set in the bucket)."
    ),
    cache: str = typer.Option(
        ".cache/fsn-shard", help="Download cache; each period is deleted after use."
    ),
    floor_gb: float = typer.Option(
        4.0, help="Stop cleanly when free disk falls below this."
    ),
    shards_file: Path = typer.Option(SHARDS_CSV),
    predecessor: str = typer.Option(
        "",
        help="pred=succ CIK pairs: also shard the predecessor, under the successor's company.",
    ),
) -> None:
    """Bucket period extracts -> company directories (FORMATS-v1 §1). Read-only on the bucket and the DB."""
    from scrooner_pipeline.db.connection import get_connection
    from scrooner_pipeline.fsn_store import shard

    cik_list = [c.strip().zfill(10) for c in ciks.split(",") if c.strip()] or _cohort(
        shards_file
    )
    with get_connection() as conn:
        alias, exclude = _db_history(conn)
        rows = conn.execute(
            "select cik, id from core.company where cik = any(%s)", (cik_list,)
        ).fetchall()
    for pred, succ in _predecessors(
        predecessor
    ).items():  # flag: whole history, no window
        alias.setdefault(pred, []).append((succ, "00000000", "99999999"))
    ids = dict(rows)
    targets = {c: ids.get(c) for c in cik_list}
    commit = (
        subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
        or None
    )
    res = shard.run(
        Path(out),
        targets,
        [p for p in periods.split(",") if p] or None,
        Path(cache),
        floor_gb=floor_gb,
        shard_commit=commit,
        alias=alias,
        exclude=exclude,
    )
    typer.echo(f"fsn shard: {json.dumps(res)}")


@app.command("load")
def load_cmd(
    companies: str = typer.Option(
        "companies", help="Root of companies/<cik>/ directories."
    ),
    ciks: str = typer.Option(
        "", help="Comma-separated CIKs (default: every directory under the root)."
    ),
    force: bool = typer.Option(
        False, help="Reload even when (input_sha256, loader_commit) already match."
    ),
    report: str = typer.Option(None, help="Write the run summary JSON here."),
    predecessor: str = typer.Option(
        "",
        help="pred=succ CIK pairs: load the predecessor's filings under the successor.",
    ),
    increment: bool = typer.Option(
        False,
        "--increment",
        help="EDGAR-built directories (scrooner-fsn nightly): add or replace those accessions only.",
    ),
) -> None:
    """Company directories -> schema fsn, one transaction per company (design §2). Writes fsn.* only."""
    from scrooner_pipeline.db.connection import get_connection
    from scrooner_pipeline.fsn_store import load

    import psycopg

    from scrooner_pipeline.common.config import settings

    res = None
    try:
        with get_connection() as conn:
            res = load.run(
                conn,
                Path(companies),
                [c for c in ciks.split(",") if c] or None,
                force=force,
                predecessors={**_db_predecessors(conn), **_predecessors(predecessor)},
                # a connection the pooler drops mid-run is replaced (load.run closes it);
                # the shard goes on with the next company instead of dying in rollback()
                connect=lambda: psycopg.connect(settings.database_url),
                increment=increment,
            )
    except psycopg.OperationalError:
        if res is None:
            raise
        typer.echo(
            "fsn load: the first connection was dropped by the pooler; the run completed on a new one"
        )
    if report:
        Path(report).write_text(json.dumps(res, indent=1, default=str))
    typer.echo(f"fsn load: {json.dumps(res, default=str)}")


@app.command("seed-rules")
def seed_rules_cmd(
    files: list[str] = typer.Argument(
        ..., help="concept_rules/<lane>.jsonl files (FORMATS-v1 §2)."
    ),
    apply: bool = typer.Option(
        False, "--apply/--plan", help="Write fsn.concept_rule (default: validate only)."
    ),
) -> None:
    """Validate and load concept_rule seeds; the whole file is refused on the first error."""
    from scrooner_pipeline.db.connection import get_connection
    from scrooner_pipeline.fsn_store import rules

    with get_connection() as conn:
        for f in files:
            res = rules.seed(conn, Path(f), apply=apply)
            typer.echo(
                f"seed-rules {f} [{'apply' if apply else 'plan'}]: {json.dumps(res, default=str)}"
            )


def _ids(conn, ciks: str) -> dict[str, int]:
    cik_list = [c.strip().zfill(10) for c in ciks.split(",") if c.strip()]
    return dict(
        conn.execute(
            "select cik, id from core.company where cik = any(%s)", (cik_list,)
        ).fetchall()
    )


@app.command("pilot")
def pilot_cmd(
    ciks: str = typer.Option(..., help="Comma-separated pilot CIKs (already loaded)."),
    out: str = typer.Option("pilot-out", help="Output directory."),
    calendar: str = typer.Option(
        "data-team/46-canonical-fact-v2/expected_periods_2026-10-31.csv.gz",
        help="Expected-period calendar (CELL-FORMAT §2.3).",
    ),
    period_rules: str = typer.Option(
        "data-team/47-fsn-store/period_rules.csv",
        help="Basis splits and unfiled instants (company period rules).",
    ),
    company_outs: str = typer.Option(
        "data-team/47-fsn-store/template_company_outs_approval_2026-11-03.csv",
        help="Company-level template OUTs with the approver's verdicts (line not printed).",
    ),
    note_sourced: str = typer.Option(
        "data-team/47-fsn-store/template_company_outs_approval_2026-11-03.csv",
        help="Approved company x data point pairs served from a note fact; '' disables.",
    ),
    cleared_keys: str = typer.Option(
        "data-team/47-fsn-store/note_cleared_keys.csv",
        help="Verifier-cleared note keys (stored value pinned) for signs held otherwise.",
    ),
) -> None:
    """Map, check, select and report the pilot companies on the store's database (design §7 step 5).
    Writes fsn.line_map and fsn.filing_check of that database; run it on a scratch copy for a dry run."""
    import gzip

    from scrooner_pipeline.db.connection import get_connection
    from scrooner_pipeline.common.errors import safe_rollback
    from scrooner_pipeline.fsn_store import checks, detectors, mapping, pilot
    from scrooner_pipeline.normalizer.cell_loader import OWNERSHIP

    root = Path(out)
    root.mkdir(parents=True, exist_ok=True)
    reports: list[dict] = []
    families: dict[str, list[dict]] = {}
    library_rows: list[dict] = []
    gap_rows: list[dict] = []
    failed: list[dict] = []
    import psycopg

    finished = False
    try:
        with get_connection() as outer:
            conn = outer
            rules = mapping.load_rules(conn)
            rule_concepts = {
                r[0]
                for r in conn.execute(
                    "select distinct cc.name from fsn.concept_rule r join analytics.canonical_concept cc on cc.id = r.canonical_concept_id"
                ).fetchall()
            }
            for cik, cid in sorted(_ids(conn, ciks).items()):
                try:
                    # the ported lane detectors (capex / D&A: one line per concept per filing, or held)
                    m = mapping.map_company(
                        conn, cid, rules, detectors=detectors.DEFAULT
                    )
                    c = checks.check_company(conn, cid)
                    conn.commit()
                    rep = pilot.report_company(
                        conn,
                        cid,
                        Path(calendar),
                        rule_concepts,
                        Path(period_rules),
                        Path(company_outs),
                        Path(note_sourced) if note_sourced else None,
                        Path(cleared_keys) if cleared_keys else None,
                    )
                    rep["mapping"], rep["checks"] = m, c
                    rep["accessions"] = [
                        r[0]
                        for r in conn.execute(
                            "select accession from fsn.filing where company_id = %s order by accepted",
                            (cid,),
                        ).fetchall()
                    ]
                    for r in rep.pop("_cells"):
                        if r["fsn_end"] < "2014-01-01":
                            continue  # comparatives before the history floor (CELL-FORMAT §2)
                        fam = OWNERSHIP.get(r["data_point_name"], "unowned")
                        families.setdefault(fam, []).append(r)
                    for g in rep.pop("_gaps"):
                        gap_rows.append({"cik": cik, "company_id": cid, **g})
                    for e in rep.pop("_library"):
                        library_rows.append({"cik": cik, "company_id": cid, **e})
                    reports.append(rep)
                except Exception as exc:  # noqa: BLE001  one company must not stop the shard
                    # a dropped connection: rollback() would raise and kill the shard (FSN write run
                    # 42561798991); safe_rollback gives a fresh connection for the next company instead
                    conn = safe_rollback(conn, stage="fsn_pilot", cik=cik)
                    failed.append(
                        {"cik": cik, "company_id": cid, "error": repr(exc)[:300]}
                    )
                    typer.echo(f"pilot {cik}: FAILED {repr(exc)[:200]}")
                else:  # only a company that succeeded has a report to print
                    typer.echo(
                        f"pilot {cik}: template {rep['template_coverage']['valued_pct']}% valued, "
                        f"{rep['template_coverage']['valued_or_reasoned_pct']}% valued or reasoned, "
                        f"library {rep['library']['completeness_pct']}%, gaps {rep['template_coverage']['gaps']}"
                    )
            if conn is not outer:
                conn.close()
            finished = True
    except psycopg.OperationalError:
        # the pooler dropped the FIRST connection while a replacement did the work: its exit commit fails after
        # every company is done; the results below are complete, so only a failure before that is fatal
        if not finished:
            raise
        typer.echo(
            "pilot: the first connection was dropped by the pooler; results are complete"
        )
    for fam, rows in families.items():
        d = root / "cells" / fam
        d.mkdir(parents=True, exist_ok=True)
        with gzip.open(d / "cells.jsonl.gz", "wt") as fh:
            for r in rows:
                fh.write(json.dumps(r, default=str) + "\n")
        (d / "manifest.json").write_text(
            json.dumps(
                {
                    "family": fam,
                    "rule_id": "fsn.select@1",
                    "rows": len(rows),
                    "data_points": sorted({r["data_point_name"] for r in rows}),
                    "period_floor": "2014-01-01",
                }
            )
        )
    for name, rows in (("library", library_rows), ("gaps", gap_rows)):
        if rows:
            with (root / f"{name}.csv").open("w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
    (root / "report.json").write_text(json.dumps(reports, indent=1, default=str))
    (root / "failed.json").write_text(json.dumps(failed, indent=1))
    lines = [
        "| company | template | keys | valued % | valued or reasoned % | gaps | library % | G2-eligible valued/keys | not G2-eligible (BS, debt) valued/keys | bs rule ids serving cells | missing data points (library) |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in reports:
        t, lib = r["template_coverage"], r["library"]
        lines.append(
            f"| {r['name']} ({r['cik']}) | {r['profile']['sector_template']} | {t['keys']} | {t['valued_pct']} | "
            f"{t['valued_or_reasoned_pct']} | {t['gaps']} | {lib['completeness_pct']} | "
            f"{t['g2_eligibility'].get('g2_eligible_valued', 0)}/{t['g2_eligibility'].get('g2_eligible_keys', 0)} | "
            f"{t['g2_eligibility'].get('not_g2_eligible_valued', 0)}/{t['g2_eligibility'].get('not_g2_eligible_keys', 0)} | "
            f"{', '.join(t['bs_rule_ids_serving_cells'])} | {', '.join(x.replace('_resolved', '') for x in lib['missing'])} |"
        )
    causes: dict[str, int] = {}
    for g in gap_rows:
        causes[g["cause"]] = causes.get(g["cause"], 0) + 1
    lines += [
        "",
        "Gap causes (template keys):",
        *[f"- {k}: {v}" for k, v in sorted(causes.items(), key=lambda x: -x[1])],
    ]
    (root / "summary.md").write_text("\n".join(lines) + "\n")
    typer.echo("\n".join(lines))


@app.command("pilot-prod")
def pilot_prod_cmd(
    pilot_out: str = typer.Option("pilot-out", help="The `pilot` output directory."),
) -> None:
    """Production side of the pilot dry run, READ-ONLY: before-image of the pilot companies'
    canonical_fact and reasons, filings missing from the store, then `scrooner-cells load --plan`
    (rolled back) per family file. Writes nothing to production values."""
    import gzip

    from scrooner_pipeline.db.connection import get_connection

    root = Path(pilot_out)
    reports = json.loads((root / "report.json").read_text())
    ids = [r["company_id"] for r in reports]
    with get_connection() as conn:
        conn.execute("set statement_timeout = '10min'")
        for table, cols in (
            ("analytics.canonical_fact", "*"),
            ("analytics.cell_blank_reason", "*"),
            ("analytics.slot_protected_cell", "*"),
        ):
            path = root / "before_image" / f"{table.split('.')[1]}.csv.gz"
            path.parent.mkdir(parents=True, exist_ok=True)
            with (
                gzip.open(path, "wb") as fh,
                conn.cursor().copy(
                    f"copy (select {cols} from {table} where company_id = any(%s) order by 1) to stdout with csv header",
                    (ids,),
                ) as cp,
            ):
                for chunk in cp:
                    fh.write(bytes(chunk))
        missing = {}
        for r in reports:
            have = set(r["accessions"])
            rows = conn.execute(
                """
                select accession_number, form, period_of_report from core.filing
                where company_id = %s and form in ('10-K', '10-Q', '10-K/A', '10-Q/A')
                  and period_of_report >= '2014-01-01'
                order by period_of_report
                """,
                (r["company_id"],),
            ).fetchall()
            missing[r["cik"]] = [
                {"accession": a, "form": f, "period": str(p)}
                for a, f, p in rows
                if a not in have
            ]
        conn.rollback()
    (root / "missing_filings.json").write_text(json.dumps(missing, indent=1))
    typer.echo(
        "filings in core.filing but not in the store: "
        + json.dumps({k: len(v) for k, v in missing.items()})
    )


@app.command("done-gate")
def done_gate_cmd(
    pilot_out: str = typer.Option(
        "pilot-out", help="The `pilot` + `pilot-prod` output directory."
    ),
    data_points: str = typer.Option(
        ..., help="Comma-separated data points the write switches."
    ),
) -> None:
    """Design §5 criteria 1-5 per company (read-only): writes done_companies.txt (company ids that may
    switch) and not_done.json (company id -> failed criteria) into the output directory."""
    from scrooner_pipeline.fsn_store.pilot import done_gate

    root = Path(pilot_out)
    reports = json.loads((root / "report.json").read_text())
    gaps_path = root / "gaps.csv"
    gaps = list(csv.DictReader(gaps_path.open())) if gaps_path.exists() else []
    missing = json.loads((root / "missing_filings.json").read_text())
    res = done_gate(reports, gaps, missing, {s for s in data_points.split(",") if s})
    done = sorted(c for c, f in res.items() if not f)
    (root / "done_companies.txt").write_text("".join(f"{c}\n" for c in done))
    (root / "not_done.json").write_text(
        json.dumps({c: f for c, f in res.items() if f}, indent=1)
    )
    typer.echo(f"done gate: {len(done)} of {len(res)} companies may switch")


@app.command("extract-sec")
def extract_sec_cmd(
    ciks: str = typer.Option(
        "",
        help="CIKs to extract (default: every predecessor in core.company_predecessor).",
    ),
    sets: str = typer.Option(
        "", help="Comma-separated FSN sets (default: every set in the bucket)."
    ),
    work: str = typer.Option(".cache/fsn-extract", help="Scratch directory."),
    apply: bool = typer.Option(
        False,
        "--apply/--plan",
        help="Upload to fsn-notes/predecessors/ (default: extract only).",
    ),
) -> None:
    """SEC FSN sets -> the extra CIKs' rows, byte for byte, into fsn-notes/predecessors/<set>/.
    One request per set to sec.gov with the declared User-Agent; run sets sequentially."""
    import time

    from scrooner_pipeline.common.config import settings
    from scrooner_pipeline.fsn_store import extract_sec, shard

    cik_set = {c.strip().zfill(10) for c in ciks.split(",") if c.strip()}
    if not cik_set:
        from scrooner_pipeline.db.connection import get_connection

        with get_connection() as conn:
            cik_set = set(_db_predecessors(conn))
    if not cik_set:
        raise typer.BadParameter(
            "no CIKs: pass --ciks or fill core.company_predecessor"
        )
    set_list = [s for s in sets.split(",") if s] or shard.list_periods()
    total: dict[str, int] = {}
    for s_ in set_list:
        t0 = time.time()
        counts = extract_sec.run_set(
            s_, cik_set, Path(work), settings.sec_user_agent, apply=apply
        )
        for k, v in counts.items():
            total[k] = total.get(k, 0) + v
        typer.echo(f"extract-sec {s_}: {json.dumps(counts)} in {time.time() - t0:.0f}s")
    typer.echo(
        f"extract-sec total [{'apply' if apply else 'plan'}] {sorted(cik_set)}: {json.dumps(total)}"
    )


if __name__ == "__main__":
    app()


NIGHTLY_COHORT = Path("data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv")


@app.command("nightly")
def nightly_cmd(
    out: str = typer.Option(
        "companies-nightly", help="Output root: companies/<cik>/ increments."
    ),
    cohort: str = typer.Option(str(NIGHTLY_COHORT), help="Cohort CSV (cik column)."),
    ciks: str = typer.Option("", help="Comma-separated CIKs instead of the cohort."),
    lookback_days: int = typer.Option(
        7,
        help="At least the last N days. The window reaches back to the day after the latest SEC FSN"
        " set in the store, so filings since that set (the backfill) and deferred ones are caught up.",
    ),
    since: str = typer.Option(
        "", help="YYYY-MM-DD: start of the window instead (a one-off backfill)."
    ),
    max_minutes: float = typer.Option(
        30.0, help="Wall-clock budget for fetching; the rest is deferred."
    ),
    report: str = typer.Option("nightly-report.json", help="Run report (JSON)."),
) -> None:
    """New periodic filings -> EDGAR-built FSN rows -> increment directories (design note 2026-11-09).
    Reads the database (one indexed query) and sec.gov (<= 4 req/s); writes local files only. Load them
    with `scrooner-fsn load --increment`, then `pilot` / `done-gate` / the protected cell write."""
    import os
    from datetime import date, timedelta

    from scrooner_pipeline.db.connection import get_connection
    from scrooner_pipeline.fsn_store import edgar_fetch, increment

    if ciks:
        cik_list = [c.strip().zfill(10) for c in ciks.split(",") if c.strip()]
    else:
        path = Path(cohort)
        if not path.exists():
            path = Path(__file__).resolve().parents[4] / cohort
        cik_list = sorted({r["cik"].zfill(10) for r in csv.DictReader(path.open())})
    today = date.today()
    with get_connection() as conn:
        start = today - timedelta(days=lookback_days)
        after_set = increment.since_last_set(conn)
        if after_set is not None and after_set < start:
            start = after_set
        if since:
            start = date.fromisoformat(since)
        cands = increment.candidates(conn, cik_list, start)
    client = edgar_fetch.EdgarClient(os.environ.get("SEC_USER_AGENT", ""))
    fsn_set = f"{increment.EDGAR_SET_PREFIX}{today.isoformat()}"
    try:
        res = increment.build(
            cands,
            lambda c: edgar_fetch.fetch_filing(client, c.cik, c.accession, fsn_set),
            max_seconds=max_minutes * 60,
        )
    finally:
        client.close()
    company_ids = {c.cik: c.company_id for c in cands}
    written = increment.write_dirs(Path(out), res.built, company_ids, fsn_set)
    summary = {
        "fsn_set": fsn_set,
        "since": start.isoformat(),
        "candidates": len(cands),
        "built": sum(len(v) for v in res.built.values()),
        "companies": written,
        "failed": res.failed,
        "deferred": res.deferred,
        "seconds": res.requests_seconds,
        "filings": [c.__dict__ for c in cands],
    }
    Path(report).write_text(json.dumps(summary, indent=1))
    Path(out).mkdir(parents=True, exist_ok=True)
    (Path(out) / "ciks.txt").write_text(",".join(written))
    typer.echo(
        f"fsn nightly: {summary['candidates']} new filings, {summary['built']} built for {len(written)} companies,"
        f" {len(res.failed)} failed, {len(res.deferred)} deferred ({res.requests_seconds}s)"
    )
