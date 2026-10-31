"""Release package 1 of rule retire.derived_per_share_cells@1 (Family C, derived EPS quarters), with rule
pershare.never_derive_ttm@1 switched on in the same step as the metric recompute.

The package is the reviewed Family C plan (data-team/strategy/team/results/family-c-eps/release-1/): its digest is the
plan digest of derived_row_retirement.Plan (dry run v3, Verifier verify/eps-family-c-v3-2026-11-02, 15/15). Nothing is
stored as a separate cell file to apply from: the plan is RE-BUILT from the live database at apply time and must have
exactly the reviewed digest, so any drift (a cell, a fact or an FSN outcome changed) refuses the run.

  dry-run  read-only: re-plan, report the digest and whether it equals the reviewed one;
  apply    refuses unless BOTH rules are ON, --confirm equals CONFIRM_TOKEN, analytics.fact_authority_retired exists
           (its migration is not applied yet) and analytics.slot_protected_cell (0113) exist, and the re-built digest
           equals the reviewed digest; then ONE
           transaction: rule_run (apply) + derived_row_retirement.apply_plan (fact before-image + demotion, cell
           archive + replace / remove, FSN cell_evidence) + slot_protected_cell rows for the FSN-sourced cells
           (scrooner.slot_writer = 'on') + rule_run stats; writes touched_company_ids.txt for the
           recompute (calculate, ttm-returns/margins, growth, calculate-price-metrics) that must run with
           pershare.never_derive_ttm@1 ON;
  restore  derived_row_retirement.restore(run_id): cells from canonical_fact_retired, facts from
           fact_authority_retired; logged as rule_run (rollback).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scrooner_pipeline.common import cell_store as cs
from scrooner_pipeline.common.rule_flags import rule_enabled
from scrooner_pipeline.mapper import derived_row_retirement as rr
from scrooner_pipeline.mapper.ttm import RULE_PER_SHARE_TTM

CONFIRM_TOKEN = "RELEASE-PER-SHARE-C-1"
TRAIN = "per-share-derived-eps-release-1"
REQUIRED_RULES = (rr.RULE_PER_SHARE, RULE_PER_SHARE_TTM)


class ReleaseRefused(RuntimeError):
    pass


def build_plan(
    cur: Any, company_ids: list[int], fsn: dict[int, dict[str, Any]], chunk: int = 50
) -> rr.Plan:
    """The Family C plan exactly as the dry run builds it (same queries, same planner, same merge)."""
    cur.execute(
        "select id from core.unit where unit_name = 'pure' or unit_name like '%%/%%'"
    )
    uids = [r[0] for r in cur.fetchall()]
    priority: dict[str, dict[int, int]] = {}
    for name in rr.EPS_CANONICAL:
        cur.execute(rr._q(rr.MAPPED_CONCEPTS_SQL), {"name": name})
        priority[name] = {r[0]: r[1] for r in cur.fetchall()}
    plans = [
        rr.plan_per_share_chunk(
            cur,
            company_ids[i : i + chunk],
            uids=uids,
            priority_by_name=priority,
            fsn=fsn,
        )
        for i in range(0, len(company_ids), chunk)
    ]
    return rr.merge(plans, "C_per_share_derived", rr.RULE_PER_SHARE)


def _package(package_dir: Path) -> dict[str, Any]:
    return json.loads((package_dir / "PACKAGE.json").read_text())


def _ids_and_fsn(package_dir: Path) -> tuple[list[int], dict[int, dict[str, Any]]]:
    m = _package(package_dir)
    ids = [int(x) for x in (package_dir / m["company_ids_file"]).read_text().split()]
    return ids, rr.load_fsn_outcomes(package_dir / m["fsn_outcomes_file"])


def dry_run(conn: Any, package_dir: Path) -> dict[str, Any]:
    conn.execute("set default_transaction_read_only = on")
    ids, fsn = _ids_and_fsn(package_dir)
    reviewed = _package(package_dir)["digest"]
    with conn.cursor() as cur:
        plan = build_plan(cur, ids, fsn)
    summary = rr.summarize(plan)
    return {"reviewed_digest": reviewed, "rebuilt_digest": plan.digest(), "would_apply": plan.digest() == reviewed,
            "cells": summary["all_companies"]["cells"], "by_action": summary["all_companies"]["by_action"],
            "facts_to_demote": summary["facts_to_demote"]}  # fmt: skip


def apply(
    conn: Any, package_dir: Path, reviewed_digest: str, confirm: str, *, environ=None
) -> dict[str, Any]:
    missing = [r for r in REQUIRED_RULES if not rule_enabled(r, environ)]
    if missing:
        raise ReleaseRefused(f"rules not ON: {missing}; nothing applied")
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused("confirm token mismatch; nothing applied")
    if reviewed_digest != _package(package_dir)["digest"]:
        raise ReleaseRefused(
            "reviewed digest differs from PACKAGE.json; nothing applied"
        )
    with conn.cursor() as cur:
        for table, why in (("fact_authority_retired", "its migration is not written/applied"),
                           ("slot_protected_cell", "migration 0113, the resolver guard")):  # fmt: skip
            cur.execute("select to_regclass(%s)", (f"analytics.{table}",))
            if cur.fetchone()[0] is None:
                raise ReleaseRefused(
                    f"analytics.{table} does not exist ({why}); nothing applied"
                )
        ids, fsn = _ids_and_fsn(package_dir)
        plan = build_plan(cur, ids, fsn)
    if plan.digest() != reviewed_digest:
        raise ReleaseRefused(
            f"stale: re-built plan digest {plan.digest()} != reviewed {reviewed_digest}; nothing applied"
        )
    conn.rollback()  # end the planning transaction; the write is one fresh transaction
    with conn.transaction(), conn.cursor() as cur:
        run_id = cs.start_rule_run(conn, rr.RULE_PER_SHARE, "apply", "on", [], train=TRAIN,
                                   before_image_ref=f"canonical_fact_retired + fact_authority_retired run; {reviewed_digest}")  # fmt: skip
        cur.execute("set local scrooner.slot_writer = 'on'")
        stats = rr.apply_plan(
            cur, plan, run_id=run_id, expected_digest=reviewed_digest, environ=environ
        )
        # FSN-sourced values have no core.fact behind them: the nightly rebuild would delete them, so they are
        # protected (migration 0113) in the same transaction; restore removes the protection with the cells
        fsn_cells = [c for c in plan.cells if c.action == rr.ACT_REPLACE_FSN]
        cur.executemany(
            """insert into analytics.slot_protected_cell
                   (company_id, canonical_concept_id, period_id, rule_id, value, run_id, package_sha256)
               values (%s, %s, %s, %s, %s, %s, %s)""",
            [(c.company_id, c.canonical_concept_id, c.period_id, rr.RULE_PER_SHARE, c.replacement_value, run_id,
              reviewed_digest) for c in fsn_cells],
        )  # fmt: skip
        stats["protected"] = len(fsn_cells)
        cs.finish_rule_run(conn, run_id, {**stats, "digest": reviewed_digest})
    touched = sorted({c.company_id for c in plan.cells if c.action != rr.ACT_REVIEW})
    (package_dir / f"touched_company_ids_{run_id}.txt").write_text(
        "".join(f"{i}\n" for i in touched)
    )
    return {"run_id": run_id, **stats, "companies_to_recompute": len(touched)}


def restore(conn: Any, run_id: str, confirm: str) -> dict[str, Any]:
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused("confirm token mismatch; nothing restored")
    with conn.transaction(), conn.cursor() as cur:
        rb = cs.start_rule_run(conn, rr.RULE_PER_SHARE, "rollback", "on", [], train=TRAIN,
                               before_image_ref=f"restore of {run_id}")  # fmt: skip
        cur.execute("set local scrooner.slot_writer = 'on'")
        out = rr.restore(cur, run_id)
        cur.execute(
            "delete from analytics.slot_protected_cell where run_id = %s and rule_id = %s",
            (run_id, rr.RULE_PER_SHARE),
        )
        out["unprotected"] = cur.rowcount
        cs.finish_rule_run(conn, rb, {**out, "of_run": run_id})
    return {"rollback_run_id": rb, **out}


def main(argv: list[str] | None = None) -> int:
    import psycopg

    from scrooner_pipeline.common.config import settings

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["dry-run", "apply", "restore"])
    ap.add_argument("package_dir", type=Path)
    ap.add_argument("--digest", default="")
    ap.add_argument("--confirm", default="")
    ap.add_argument("--run-id", default="")
    args = ap.parse_args(argv)
    with psycopg.connect(
        settings.database_url, autocommit=args.cmd == "dry-run"
    ) as conn:
        conn.execute("set statement_timeout = '120s'")
        if args.cmd == "dry-run":
            out = dry_run(conn, args.package_dir)
        elif args.cmd == "apply":
            out = apply(conn, args.package_dir, args.digest, args.confirm)
        else:
            out = restore(conn, args.run_id, args.confirm)
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
