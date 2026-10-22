"""Population DRY-RUN for rule source.periodic_form_only@1 (W3, RF-03) and
dedupe.matching_copies@1 (WO-23, RF-46). READ-ONLY: one connection, set to
default_transaction_read_only, explicit statement_timeout, company-by-company
chunks. It writes only local files under --out-dir. It must not be run until
scrooner-4d gives the heavy-slot go (doc 53); a few named companies are fine as
a light read (--ciks).

What it reports (data-team/strategy/team/WO-REVIEW-data-engineer.md F3, AT-DE-12):

  A. Stage 2e authority changes. For every company it loads the same rows the
     production stage loads and runs the SAME pure planner
     (normalizer/dedupe.plan_authority) three times: legacy, W3, W3 + matching
     copies. Changes are counted by CLASS (groups, cells and companies):
       conflict_cleared                 no authoritative copy -> one (JPM FY / Q4)
       non_periodic_demoted_same_value  proxy/8-K copies leave, value unchanged
       authority_value_changed          the authoritative VALUE differs after
       value_to_none                    a cell loses its only authoritative copy
       periodic_conflict_remains        periodic copies still disagree
       matching_copies_resolved         WO-23 only: copies equal within rounding
     plus the non-periodic form behind each change (DEF 14A, 8-K, S-1, ...).
     "Before" is the stored is_authoritative state, which already includes the
     downstream stages (conflict-latest-filed, restatements, derive): this is
     the effect of Stage 2e alone; those stages re-assert their own decisions
     when they next run.
  B. Stored canonical cells whose source facts include a non-periodic filing
     (mapper/periodic_source_repair.find_non_periodic_sourced_cells): count by
     concept, by form, and by class all_sources_non_periodic / mixed_sources.
     These are the cells that stay wrong after the code fix until purged.
  C. Stage 2e-b winners from non-periodic forms (core.fact_conflict_resolution
     joined to the filing form): promotions the rule does NOT change (the 8-K
     recast question is a policy decision, reported not decided).

Outputs in --out-dir: summary.json, changes_by_class.csv (up to --sample-limit
rows per class), canonical_non_periodic_cells.csv (all of B), named_cases.csv
(--named-ciks: every change row, no cap), manifest.json (git commit, flags,
watermark, argv, counts, timings). Re-run with --resume to continue after a
dropped connection (progress is kept per company id).

  cd pipeline && PYTHONPATH=src python scripts/w3_population_dryrun.py \
      --out-dir ../doc/data-moat/team/w3_dryrun_<date> --ciks 0000019617,0001141391
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import psycopg

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.mapper.periodic_source_repair import find_non_periodic_sourced_cells
from scrooner_pipeline.normalizer.dedupe import _load_fact_rows, plan_authority

NAMED_CIKS = {
    "JPM": "0000019617",
    "MA": "0001141391",
    "SCHW": "0000316709",
    "MDT": "0001613103",
}
MAX_CLIENT_CONNECTIONS = 14


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001 - provenance only
        return "unknown"


def _company_ids(conn: psycopg.Connection, ciks: list[str] | None, only_active: bool) -> list[tuple[int, str]]:
    with conn.cursor() as cur:
        if ciks:
            cur.execute(
                "select id, cik from core.company where cik = any(%s) order by id", (ciks,)
            )
        else:
            cur.execute(
                "select id, cik from core.company "
                + ("where status = 'active' " if only_active else "")
                + "order by id"
            )
        return cur.fetchall()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--ciks", help="comma-separated 10-digit CIKs (default: whole population)")
    ap.add_argument("--only-active", action="store_true", help="restrict to core.company.status = 'active'")
    ap.add_argument("--chunk", type=int, default=50, help="companies per canonical-cell query (max 100)")
    ap.add_argument("--statement-timeout-ms", type=int, default=60000)
    ap.add_argument("--sample-limit", type=int, default=25)
    ap.add_argument("--named-ciks", default=",".join(NAMED_CIKS.values()))
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--max-companies", type=int, default=0, help="stop after N companies (smoke test)")
    args = ap.parse_args(argv)
    if not 1 <= args.chunk <= 100:
        ap.error("--chunk must be between 1 and 100")

    out: Path = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    named = {c for c in args.named_ciks.split(",") if c}
    progress_path = out / "progress.json"

    companies_by_class: dict[str, set[int]] = defaultdict(set)
    forms_by_class: dict[str, Counter] = defaultdict(Counter)
    concepts_by_class: dict[str, Counter] = defaultdict(Counter)
    class_counts: Counter = Counter()
    samples: dict[str, list[list]] = defaultdict(list)
    named_rows: list[list] = []
    stage_totals: Counter = Counter()
    cells_by_concept: Counter = Counter()
    cells_by_form: Counter = Counter()
    cells_by_class: Counter = Counter()
    canonical_companies: set[int] = set()
    cell_rows_written = 0
    state = {"done_up_to": 0, "processed": 0, "errors": []}
    if args.resume and progress_path.exists():
        saved = json.loads(progress_path.read_text())
        state = saved["state"]
        class_counts = Counter(saved["class_counts"])
        stage_totals = Counter(saved["stage_totals"])
        cells_by_concept = Counter(saved["cells_by_concept"])
        cells_by_form = Counter(saved["cells_by_form"])
        cells_by_class = Counter(saved["cells_by_class"])
        for k, v in saved["companies_by_class"].items():
            companies_by_class[k] = set(v)
        for k, v in saved["forms_by_class"].items():
            forms_by_class[k] = Counter(v)
        for k, v in saved["concepts_by_class"].items():
            concepts_by_class[k] = Counter(v)
        canonical_companies = set(saved["canonical_companies"])
        cell_rows_written = saved["cell_rows_written"]

    started = time.time()
    conn = psycopg.connect(settings.database_url, connect_timeout=20)
    try:
        conn.execute("set default_transaction_read_only = on")
        conn.execute(f"set statement_timeout = {int(args.statement_timeout_ms)}")
        n_clients = conn.execute(
            "select count(*) from pg_stat_activity where backend_type = 'client backend'"
        ).fetchone()[0]
        if n_clients > MAX_CLIENT_CONNECTIONS:
            print(f"ABORT: {n_clients} client connections (limit {MAX_CLIENT_CONNECTIONS})", file=sys.stderr)
            return 2
        conn.commit()

        ciks = [c for c in (args.ciks or "").split(",") if c] or None
        companies = [c for c in _company_ids(conn, ciks, args.only_active) if c[0] > state["done_up_to"]]
        if args.max_companies:
            companies = companies[: args.max_companies]
        watermark = conn.execute("select max(filing_date) from core.filing").fetchone()[0]
        conn.commit()

        cells_file = out / "canonical_non_periodic_cells.csv"
        cells_fh = cells_file.open("a" if args.resume else "w", newline="", encoding="utf-8")
        cells_csv = csv.writer(cells_fh)
        if not args.resume:
            cells_csv.writerow(
                ["canonical_fact_id", "company_id", "concept", "period_start", "period_end",
                 "value", "bad_forms", "bad_fact_ids", "periodic_sources", "class"]
            )

        for start in range(0, len(companies), args.chunk):
            chunk = companies[start : start + args.chunk]
            for company_id, cik in chunk:
                try:
                    rows = _load_fact_rows(conn, company_id)
                    legacy = plan_authority(rows)
                    w3 = plan_authority(rows, periodic_only=True, collect_changes=True)
                    both = plan_authority(
                        rows, periodic_only=True, matching_copies=True, collect_changes=True
                    )
                    conn.commit()
                except Exception as exc:  # noqa: BLE001 - report and continue
                    conn.rollback()
                    state["errors"].append({"company_id": company_id, "cik": cik, "error": repr(exc)[:300]})
                    continue
                stage_totals["companies"] += 1
                stage_totals["facts"] += len(rows)
                stage_totals["legacy_writes"] += len(legacy.set_true) + len(legacy.set_false)
                stage_totals["w3_writes"] += len(w3.set_true) + len(w3.set_false)
                stage_totals["w3_matching_writes"] += len(both.set_true) + len(both.set_false)
                stage_totals["non_periodic_demoted"] += w3.stats["non_periodic_demoted"]
                stage_totals["shrunk_group_promoted"] += w3.stats["shrunk_group_promoted"]
                stage_totals["matching_copy_groups"] += both.stats["matching_copy_groups"]
                # W3 changes; WO-23's extra classes come from the combined plan
                w3_keys = {(c[1], c[2], c[3]) for c in w3.changes}
                for ch in w3.changes + [c for c in both.changes if (c[1], c[2], c[3]) not in w3_keys]:
                    klass, concept_id, unit_id, period_id, before, after, forms = ch
                    class_counts[klass] += 1
                    companies_by_class[klass].add(company_id)
                    for f in forms:
                        forms_by_class[klass][f] += 1
                    concepts_by_class[klass][concept_id] += 1
                    row = [klass, cik, company_id, concept_id, unit_id, period_id,
                           ";".join(map(str, before)), ";".join(map(str, after)), ";".join(forms)]
                    if len(samples[klass]) < args.sample_limit:
                        samples[klass].append(row)
                    if cik in named:
                        named_rows.append(row)
            ids = [c[0] for c in chunk]
            try:
                cells = find_non_periodic_sourced_cells(conn, ids)
                conn.commit()
            except Exception as exc:  # noqa: BLE001
                conn.rollback()
                state["errors"].append({"company_ids": ids[:3], "stage": "canonical", "error": repr(exc)[:300]})
                cells = []
            for cell in cells:
                cells_by_concept[cell.concept] += 1
                cells_by_class[cell.klass] += 1
                for f in cell.bad_forms:
                    cells_by_form[f] += 1
                canonical_companies.add(cell.company_id)
                cells_csv.writerow(
                    [cell.canonical_fact_id, cell.company_id, cell.concept, cell.period_start,
                     cell.period_end, cell.value, ";".join(cell.bad_forms),
                     ";".join(map(str, cell.bad_fact_ids)), cell.periodic_sources, cell.klass]
                )
                cell_rows_written += 1
            cells_fh.flush()
            state["done_up_to"] = chunk[-1][0]
            state["processed"] += len(chunk)
            progress_path.write_text(
                json.dumps(
                    {
                        "state": state,
                        "class_counts": class_counts,
                        "stage_totals": stage_totals,
                        "cells_by_concept": cells_by_concept,
                        "cells_by_form": cells_by_form,
                        "cells_by_class": cells_by_class,
                        "companies_by_class": {k: sorted(v) for k, v in companies_by_class.items()},
                        "forms_by_class": {k: dict(v) for k, v in forms_by_class.items()},
                        "concepts_by_class": {k: dict(v) for k, v in concepts_by_class.items()},
                        "canonical_companies": sorted(canonical_companies),
                        "cell_rows_written": cell_rows_written,
                    }
                )
            )
        cells_fh.close()

        # C. Stage 2e-b winners from non-periodic forms (no change by this rule)
        from scrooner_pipeline.common.periodic_forms import PERIODIC_FORMS_ALL_ORDERED

        winners_by_form: Counter = Counter()
        try:
            with conn.cursor() as cur:
                cur.execute("select fact_id from core.fact_conflict_resolution order by fact_id")
                winner_ids = [r[0] for r in cur.fetchall()]
            conn.commit()
            allowed = set(PERIODIC_FORMS_ALL_ORDERED)
            for i in range(0, len(winner_ids), 5000):  # primary-key lookups, chunked
                with conn.cursor() as cur:
                    cur.execute(
                        "select fl.form from core.fact f join core.filing fl on fl.id = f.filing_id "
                        "where f.id = any(%s)",
                        (winner_ids[i : i + 5000],),
                    )
                    for (form,) in cur.fetchall():
                        if form not in allowed:
                            winners_by_form[form] += 1
                conn.commit()
        except Exception as exc:  # noqa: BLE001
            conn.rollback()
            state["errors"].append({"stage": "2e-b winners", "error": repr(exc)[:300]})

        with conn.cursor() as cur:
            cur.execute("select id, tag from core.concept where id = any(%s)",
                        (sorted({cid for c in concepts_by_class.values() for cid in c}),))
            tag_by_id = dict(cur.fetchall())
        conn.commit()
    finally:
        conn.close()

    with (out / "changes_by_class.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["class", "cik", "company_id", "concept_id", "unit_id", "period_id",
                    "before_values", "after_values", "non_periodic_forms"])
        for rows_ in samples.values():
            w.writerows(rows_)
    with (out / "named_cases.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["class", "cik", "company_id", "concept_id", "unit_id", "period_id",
                    "before_values", "after_values", "non_periodic_forms"])
        w.writerows(named_rows)

    summary = {
        "rule_ids": ["source.periodic_form_only@1", "dedupe.matching_copies@1"],
        "evidence_level": "DATA-INFERRED (stored is_authoritative; no filing opened by this script)",
        "stage_2e": {
            "groups_changed_by_class": dict(class_counts),
            "companies_changed_by_class": {k: len(v) for k, v in companies_by_class.items()},
            "non_periodic_forms_by_class": {k: dict(v.most_common()) for k, v in forms_by_class.items()},
            "top_concepts_by_class": {
                k: {tag_by_id.get(cid, str(cid)): n for cid, n in v.most_common(15)}
                for k, v in concepts_by_class.items()
            },
            "totals": dict(stage_totals),
        },
        "canonical_cells_with_non_periodic_source": {
            "cells": cell_rows_written,
            "companies": len(canonical_companies),
            "by_class": dict(cells_by_class),
            "by_form": dict(cells_by_form.most_common()),
            "by_concept_top40": dict(cells_by_concept.most_common(40)),
        },
        "stage_2e_b_winners_from_non_periodic_forms_unchanged_by_rule": dict(winners_by_form.most_common()),
        "errors": state["errors"],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    (out / "manifest.json").write_text(
        json.dumps(
            {
                "git_commit": _git_commit(),
                "argv": sys.argv,
                "watermark_max_filing_date": str(watermark),
                "companies_processed": state["processed"],
                "seconds": round(time.time() - started, 1),
                "writes_to_database": 0,
            },
            indent=2,
        )
    )
    print(json.dumps(summary["stage_2e"]["groups_changed_by_class"], sort_keys=True))
    print(json.dumps(summary["canonical_cells_with_non_periodic_source"], sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
