"""Typer CLI `scrooner-fsn`: the company-wise FSN statement store."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import typer

app = typer.Typer(help="Company-wise FSN statement store (design 2026-11-01).")
SHARDS_CSV = Path("doc/data-moat/team/top1000/shards.csv")


@app.callback()
def _root() -> None:
    """Subcommands: shard, load, seed-rules, pilot, pilot-prod."""


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
    input_sha: str = typer.Option(
        "", help="sha256 of the dispatched CIK list, recorded in the rule_run stats."
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
                input_sha=input_sha or None,
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
        for table, cols, where in (
            ("analytics.canonical_fact", "*", "company_id = any(%s)"),
            ("analytics.cell_blank_reason", "*", "company_id = any(%s)"),
            ("analytics.slot_protected_cell", "*", "company_id = any(%s)"),
            # the done gate's hold guard (ruling C2) reads concept names and period dates with the image
            ("analytics.canonical_concept", "id, name", "%s::bigint[] is not null"),
            (
                "core.period",
                "id, company_id, start_date, end_date, period_type, fiscal_year, fiscal_period",
                "company_id = any(%s)",
            ),
        ):
            path = root / "before_image" / f"{table.split('.')[1]}.csv.gz"
            path.parent.mkdir(parents=True, exist_ok=True)
            with (
                gzip.open(path, "wb") as fh,
                conn.cursor().copy(
                    f"copy (select {cols} from {table} where {where} order by 1) to stdout with csv header",
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


# Data points the FSN write never switches until the approver clears them (ruling RULING-DONE-GATE-C4-2026-11-09)
HELD_OUT = {
    "dividends_per_share_resolved": "C6: the Q4 FY-9M route must check the same share basis first",
    "total_debt_resolved": "C8: seed defect, release case §2/§3a",
    "total_liabilities_resolved": "C8: seed defect, release case §2/§3a",
    "shares_outstanding_resolved": "R2 (Ritwik 2026-11-10): not in the template, so the gate cannot cover it",
}


@app.command("done-gate")
def done_gate_cmd(
    pilot_out: str = typer.Option(
        "pilot-out", help="The `pilot` + `pilot-prod` output directory."
    ),
    data_points: str = typer.Option(
        ..., help="Comma-separated data points the write switches."
    ),
) -> None:
    """The done gate (founder 2026-11-09 "No fallback. Everything is the hybrid", on ruling
    RULING-DONE-GATE-C4-2026-11-09), read-only. Every in-template pair of a company passing criteria 1/2/5 is
    written whole (gap keys as reasoned blanks). Writes into the output directory:
      done_pairs.tsv         company_id, data_point: the pairs to write
      done_companies.txt     companies whose every listed pair is written
      written_companies.txt  companies with at least one pair to write: the cell_proof scope (C4)
      not_done.json          company id -> {"company": failed criteria 1/2/5, "data_points": {dp: reasons}, ...}
      valued_to_blank.json   C2 as a report: valued->blank transitions per data point by reason class, and the
                             pairs whose new cells hold no value where the before-image had values
    A before-image 6-month, 9-month or multi-year key with no printed TP cell (CELL-FORMAT v1.2) is added to its
    family's cells file (out/cells/<family>/cells.jsonl.gz) as an exact-dated hybrid gap blank before the C2 check,
    so the write carries a visible reason for it; a second run finds the blank and adds nothing.
    The before-image (pilot-prod) is required, so the C2 report is never skipped."""
    import gzip

    from scrooner_pipeline.fsn_store.pilot import (
        done_gate,
        done_pairs,
        fully_done,
        hold_guard,
        count_valued_to_no_row,
        ytd_gap_blanks,
    )
    from scrooner_pipeline.normalizer.cell_loader import (
        OWNERSHIP,
        bind_tp,
        ytd_periods_by_class,
    )

    root = Path(pilot_out)
    points = {s for s in data_points.split(",") if s}
    refused = sorted(points & set(HELD_OUT))
    if refused:
        raise typer.BadParameter(
            "; ".join(f"{dp} stays out ({HELD_OUT[dp]})" for dp in refused)
        )
    reports = json.loads((root / "report.json").read_text())
    gaps_path = root / "gaps.csv"
    gaps = list(csv.DictReader(gaps_path.open())) if gaps_path.exists() else []
    missing = json.loads((root / "missing_filings.json").read_text())
    image = root / "before_image"
    for name in ("canonical_fact", "canonical_concept", "period"):
        if not (image / f"{name}.csv.gz").exists():
            raise typer.BadParameter(
                f"{image}/{name}.csv.gz is missing: run pilot-prod first (C2 hold guard)"
            )

    def rows(name):
        with gzip.open(image / f"{name}.csv.gz", "rt") as fh:
            return list(csv.DictReader(fh))

    cells: list[dict] = []
    for path in sorted(root.glob("cells/*/cells.jsonl.gz")):
        with gzip.open(path, "rt") as fh:
            cells.extend(json.loads(line) for line in fh if line.strip())
    before = rows("canonical_fact")
    names = {r["id"]: r["name"] for r in rows("canonical_concept")}
    periods = {r["id"]: r for r in rows("period")}
    # CELL-FORMAT v1.2: before-image YTD / multi-year keys with nothing printed become reasoned TP blanks
    ytd_rows, ytd_skipped = ytd_gap_blanks(
        cells, before, names, periods, points, reports
    )
    by_family: dict[str, list[dict]] = {}
    for r in ytd_rows:
        by_family.setdefault(OWNERSHIP.get(r["data_point_name"], "unowned"), []).append(
            r
        )
    for fam, add in sorted(by_family.items()):
        d = root / "cells" / fam
        d.mkdir(parents=True, exist_ok=True)
        path = d / "cells.jsonl.gz"
        old = []
        if path.exists():
            with gzip.open(path, "rt") as fh:
                old = [json.loads(line) for line in fh if line.strip()]
        with gzip.open(path, "wt") as fh:
            for r in old + add:
                fh.write(json.dumps(r, default=str) + "\n")
        manifest = d / "manifest.json"
        if manifest.exists():
            m = json.loads(manifest.read_text())
            m["rows"] = len(old) + len(add)
            m["data_points"] = sorted(
                set(m.get("data_points") or []) | {r["data_point_name"] for r in add}
            )
            manifest.write_text(json.dumps(m))
    cells.extend(ytd_rows)
    not_in_template: list[dict] = []
    emptied, transitions, no_row = hold_guard(
        cells, before, names, periods, points, not_in_template
    )
    # approver ruling 2026-11-10, item 3: a TP print the loader will reject (no YTD period of its class at its end,
    # or two at the same nearest end) is not written and gets no reason row; count it per company with the share
    # of the company's TP prints, by the loader's own binding rule (bind_tp) over the before-image core.period
    by_company_periods: dict[int, list] = {}
    for pid, p in periods.items():
        if p.get("company_id"):
            by_company_periods.setdefault(int(p["company_id"]), []).append(
                (
                    pid,
                    date.fromisoformat(p["start_date"]),
                    date.fromisoformat(p["end_date"]),
                    p["period_type"],
                )
            )
    ytd_by_company = {
        c: ytd_periods_by_class(ps) for c, ps in by_company_periods.items()
    }
    tp_stats: dict[int, Counter] = {}
    for r in cells:
        if (
            r.get("period_grain") != "TP"
            or r["data_point_name"] not in points
            or r.get("period_start")
            or r.get("qtrs") not in (2, 3)
        ):
            continue
        cid = int(r["company_id"])
        st = tp_stats.setdefault(cid, Counter())
        st["tp_prints"] += 1
        _pid, why = bind_tp(
            ytd_by_company.get(cid, {}), date.fromisoformat(r["fsn_end"]), r["qtrs"]
        )
        if why:
            st[why] += 1
            st["rejected"] += 1
    tp_rejected_by_company = {
        str(c): {
            **dict(st),
            "share": round(st["rejected"] / st["tp_prints"], 6),
        }
        for c, st in sorted(tp_stats.items())
    }
    tp_total = sum(st["tp_prints"] for st in tp_stats.values())
    tp_rej = sum(st["rejected"] for st in tp_stats.values())
    gate = done_gate(reports, gaps, missing, points)
    # C2 is the old-vs-new diff, a report (founder 2026-11-11 "move to the new system"; approver's C2 amendment)
    no_row_by_pair = count_valued_to_no_row(no_row)
    with (root / "valued_to_no_row.tsv").open("w") as fh:
        cols = [
            "company_id",
            "data_point",
            "period_id",
            "grain",
            "start",
            "end",
            "before_value",
            "why",
        ]
        fh.write("\t".join(cols) + "\n")
        for k in no_row:
            fh.write("\t".join("" if k[c] is None else str(k[c]) for c in cols) + "\n")
    pairs = done_pairs(gate)
    written_no_row = sum(no_row_by_pair.get(p, 0) for p in pairs)
    full = fully_done(gate)
    written = sorted({cid for cid, _dp in pairs})
    listed = sum(len(g["data_points"]) for g in gate.values())
    (root / "done_pairs.tsv").write_text(
        "company_id\tdata_point\n" + "".join(f"{c}\t{dp}\n" for c, dp in pairs)
    )
    (root / "done_companies.txt").write_text("".join(f"{c}\n" for c in full))
    (root / "written_companies.txt").write_text("".join(f"{c}\n" for c in written))
    not_done = {
        cid: {
            "company": g["company"],
            "data_points": {dp: f for dp, f in g["data_points"].items() if f},
            "out_of_template": g["out_of_template"],
            "gap_blanks": g["gap_blanks"],
        }
        for cid, g in gate.items()
        if g["company"] or any(g["data_points"].values())
    }
    (root / "not_done.json").write_text(json.dumps(not_done, indent=1))
    gap_blanks: dict[str, int] = {}
    for g in gate.values():
        for dp, n in g["gap_blanks"].items():
            gap_blanks[dp] = gap_blanks.get(dp, 0) + n
    (root / "valued_to_blank.json").write_text(
        json.dumps(
            {
                # C2 as a report (founder 2026-11-09: no hold); the approver reviews it before dispatch
                "valued_to_blank_by_data_point": transitions,
                # must be 0 in every written pair (Ritwik 2026-11-10); the keys are in valued_to_no_row.tsv
                "valued_to_no_row_by_pair": [
                    {"company_id": c, "data_point": dp, "keys": n}
                    for (c, dp), n in sorted(no_row_by_pair.items())
                ],
                "valued_to_no_row_in_written_pairs": written_no_row,
                "pairs_with_no_new_value_but_old_values": [
                    {"company_id": c, "data_point": dp, "why": w}
                    for (c, dp), w in sorted(emptied.items())
                ],
                "gap_keys_written_as_blanks_by_data_point": dict(
                    sorted(gap_blanks.items())
                ),
                # CELL-FORMAT v1.2: before-image YTD / multi-year keys with nothing printed, added as TP blanks
                "ytd_keys_written_as_blanks_by_data_point": dict(
                    sorted(Counter(r["data_point_name"] for r in ytd_rows).items())
                ),
                "ytd_keys_not_blanked": ytd_skipped,
                # approver ruling 2026-11-10, item 1: before-image multi-year keys written as not_in_template
                "valued_to_not_in_template_by_data_point": dict(
                    sorted(Counter(k["data_point"] for k in not_in_template).items())
                ),
                "valued_to_not_in_template_by_pair": [
                    {"company_id": c, "data_point": dp, "keys": n}
                    for (c, dp), n in sorted(
                        Counter(
                            (k["company_id"], k["data_point"]) for k in not_in_template
                        ).items()
                    )
                ],
                "valued_to_not_in_template_keys": not_in_template,
                # item 3: TP prints the loader will reject (ambiguous or no YTD period), per company and in total
                "tp_rejected_by_company": tp_rejected_by_company,
                "tp_rejected_share": round(tp_rej / tp_total, 6) if tp_total else 0.0,
            },
            indent=1,
        )
    )
    per_point: dict[str, int] = {}
    for _c, dp in pairs:
        per_point[dp] = per_point.get(dp, 0) + 1
    typer.echo(
        f"done gate: {len(pairs)} pairs of {listed}; {len(full)} companies fully done"
    )
    typer.echo(
        f"done gate: pairs passing per data point {json.dumps(dict(sorted(per_point.items())))}"
    )
    typer.echo(
        f"done gate: {sum(gap_blanks.values())} gap keys written as reasoned blanks; "
        f"{len(emptied)} pairs lose every value (valued_to_blank.json, C2 report)"
    )
    over = sum(1 for v in tp_rejected_by_company.values() if v["share"] > 0.005)
    typer.echo(
        f"done gate: TP prints the loader will reject: {tp_rej} of {tp_total}; "
        f"{over} companies above 0.5%; {len(not_in_template)} multi-year keys written as not_in_template"
    )
    typer.echo(
        f"done gate: {len(ytd_rows)} before-image year-to-date keys with nothing printed added as TP blanks; "
        f"{len(ytd_skipped)} not blanked (no stored filings in the report)"
    )
    typer.echo(
        f"done gate: {len(no_row)} before-image values would have no row; "
        f"{len(no_row_by_pair)} pairs carry such keys (diff report, not a hold); valued->no-row in written pairs: {written_no_row}"
    )


@app.command("proof-blank")
def proof_blank_cmd(
    write_dir: str = typer.Option(
        "out/write",
        help="The select_write run's written cells: <dir>/<family>/cells.jsonl.gz.",
    ),
    out: str = typer.Option("out/proof_blank", help="Output directory (same layout)."),
) -> None:
    """Ruling addendum N2 (no fallback), READ-ONLY on production: the written cells that analytics.cell_proof
    DISAGREEs with become defect blanks (identity / verifier, cell_proof_disagree) instead of being restored to
    old values. Writes <out>/<family>/cells.jsonl.gz holding every row of each pair with a DISAGREE (the loader
    replaces a pair whole) and <out>/summary.json. Loading it is a production write: `scrooner-cells load ... --apply`
    on the founder's words. The before-image restore stays an emergency rollback only."""
    import gzip

    from scrooner_pipeline.db.connection import get_connection
    from scrooner_pipeline.fsn_store.pilot import blank_disagreements

    families: dict[str, list[dict]] = {}
    for path in sorted(Path(write_dir).glob("*/cells.jsonl.gz")):
        with gzip.open(path, "rt") as fh:
            families[path.parent.name] = [
                json.loads(line) for line in fh if line.strip()
            ]
    ids = sorted({int(r["company_id"]) for rows in families.values() for r in rows})
    if not ids:
        raise typer.BadParameter(f"no written cells under {write_dir}")
    with get_connection() as conn:
        conn.execute("set statement_timeout = '5min'")
        cur = conn.execute(
            """select id, company_id, data_point_name, period_grain, period_start, period_end, shown_value,
                      position_value, reason_code, rule_id
               from analytics.cell_proof where verdict = 'DISAGREE' and company_id = any(%s)""",
            (ids,),
        )
        cols = [c.name for c in cur.description]
        disagrees = [dict(zip(cols, r)) for r in cur.fetchall()]
        conn.rollback()
    root = Path(out)
    summary: dict[str, Any] = {
        "companies": len(ids),
        "disagree_rows": len(disagrees),
        "families": {},
    }
    matched_ids: set = set()
    for fam, rows in sorted(families.items()):
        points = {r["data_point_name"] for r in rows}
        mine = [d for d in disagrees if d["data_point_name"] in points]
        blanked, unmatched = blank_disagreements(rows, mine)
        matched_ids |= {d["id"] for d in mine} - {d["id"] for d in unmatched}
        if not blanked:
            continue
        d = root / fam
        d.mkdir(parents=True, exist_ok=True)
        with gzip.open(d / "cells.jsonl.gz", "wt") as fh:
            for r in blanked:
                fh.write(json.dumps(r, default=str) + "\n")
        n = sum(1 for r in blanked if r.get("reason_code") == "cell_proof_disagree")
        (d / "manifest.json").write_text(
            json.dumps(
                {
                    "family": fam,
                    "rule_id": "fsn.cell_proof_blank@1",
                    "rows": len(blanked),
                    "blanked": n,
                }
            )
        )
        summary["families"][fam] = {"rows_reloaded": len(blanked), "cells_blanked": n}
    unmatched_all = [d for d in disagrees if d["id"] not in matched_ids]
    summary["disagree_not_in_written_cells"] = len(unmatched_all)
    root.mkdir(parents=True, exist_ok=True)
    (root / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    typer.echo(f"proof-blank: {json.dumps(summary, default=str)}")


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
