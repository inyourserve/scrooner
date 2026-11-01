"""Release package 1 of rule retire.derived_ratio_cells@1 (Family A: derived effective tax rates).

effective_tax_rate_reported holds PRINTED rates only (the displayed metric effective_tax_rate_gap is reported minus
the rate mapper/tax_reconciliation.py computes from the printed tax and pretax lines, so a computed value in
"reported" would make the gap 0 by construction; Dhairya's ruling 2026-11-03 conditional clause). A quarter built as
FY rate minus 9M rate is wrong by construction (a rate is not additive): it is removed with a reason, or replaced by
a filed rate for the same period. Nothing is recomputed (no metric reads these cells except the gap, which then
goes blank for the period).

The package is the reviewed Family A plan (data-team/strategy/team/results/effective-tax-rate/release-1/): the plan is
RE-BUILT from the live database at apply time and must have exactly the reviewed digest.

  dry-run  read-only: re-plan, report the digest and whether it equals the reviewed one;
  apply    refuses unless the rule is ON, --confirm equals CONFIRM_TOKEN, analytics.fact_authority_retired (migration
           0116) exists, and the re-built digest equals the reviewed digest; then ONE transaction: rule_run (apply) +
           derived_row_retirement.apply_plan (fact before-image + demotion, cell archive + replace / remove);
  restore  derived_row_retirement.restore(run_id), logged as rule_run (rollback).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scrooner_pipeline.common import cell_store as cs
from scrooner_pipeline.common.rule_flags import rule_enabled
from scrooner_pipeline.mapper import derived_row_retirement as rr

CONFIRM_TOKEN = "RELEASE-TAX-RATE-A-1"
TRAIN = "derived-tax-rate-release-1"


class ReleaseRefused(RuntimeError):
    pass


def build_plan(cur: Any, company_ids: list[int], chunk: int = 50) -> rr.Plan:
    """The Family A plan exactly as derived_row_retirement.run_dry_run builds it."""
    cur.execute("select id from core.concept where tag = %s", (rr.TAX_RATE_TAG,))
    cids = [r[0] for r in cur.fetchall()]
    cur.execute(
        "select id from core.unit where unit_name = 'pure' or unit_name like '%%/%%'"
    )
    uids = [r[0] for r in cur.fetchall()]
    cur.execute(rr._q(rr.MAPPED_CONCEPTS_SQL), {"name": rr.TAX_RATE_CANONICAL})
    mapped = {r[0]: r[1] for r in cur.fetchall()}
    plans = [
        rr.plan_ratio_chunk(
            cur,
            company_ids[i : i + chunk],
            cids=cids,
            uids=uids,
            mapped_priority=mapped,
        )
        for i in range(0, len(company_ids), chunk)
    ]
    return rr.merge(plans, "A_ratio_derived", rr.RULE_RATIO)


def _package(package_dir: Path) -> dict[str, Any]:
    return json.loads((package_dir / "PACKAGE.json").read_text())


def _ids(package_dir: Path) -> list[int]:
    return [
        int(x)
        for x in (package_dir / _package(package_dir)["company_ids_file"])
        .read_text()
        .split()
    ]


def dry_run(conn: Any, package_dir: Path) -> dict[str, Any]:
    conn.execute("set default_transaction_read_only = on")
    reviewed = _package(package_dir)["digest"]
    with conn.cursor() as cur:
        plan = build_plan(cur, _ids(package_dir))
    s = rr.summarize(plan)
    return {"reviewed_digest": reviewed, "rebuilt_digest": plan.digest(), "would_apply": plan.digest() == reviewed,
            "cells": s["all_companies"]["cells"], "by_action": s["all_companies"]["by_action"],
            "facts_to_demote": s["facts_to_demote"]}  # fmt: skip


def apply(
    conn: Any, package_dir: Path, reviewed_digest: str, confirm: str, *, environ=None
) -> dict[str, Any]:
    if not rule_enabled(rr.RULE_RATIO, environ):
        raise ReleaseRefused(f"{rr.RULE_RATIO} is not ON; nothing applied")
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused("confirm token mismatch; nothing applied")
    if reviewed_digest != _package(package_dir)["digest"]:
        raise ReleaseRefused(
            "reviewed digest differs from PACKAGE.json; nothing applied"
        )
    with conn.cursor() as cur:
        cur.execute("select to_regclass('analytics.fact_authority_retired')")
        if cur.fetchone()[0] is None:
            raise ReleaseRefused("analytics.fact_authority_retired does not exist (migration 0116 not applied); nothing applied")  # fmt: skip
        plan = build_plan(cur, _ids(package_dir))
    if plan.digest() != reviewed_digest:
        raise ReleaseRefused(f"stale: re-built plan digest {plan.digest()} != reviewed {reviewed_digest}; nothing applied")  # fmt: skip
    with conn.transaction(), conn.cursor() as cur:
        run_id = cs.start_rule_run(conn, rr.RULE_RATIO, "apply", "on", [], train=TRAIN,
                                   before_image_ref=f"canonical_fact_retired + fact_authority_retired run; {reviewed_digest}")  # fmt: skip
        stats = rr.apply_plan(
            cur, plan, run_id=run_id, expected_digest=reviewed_digest, environ=environ
        )
        cs.finish_rule_run(conn, run_id, {**stats, "digest": reviewed_digest})
    conn.commit()
    return {"run_id": run_id, **stats}


def restore(conn: Any, run_id: str, confirm: str) -> dict[str, Any]:
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused("confirm token mismatch; nothing restored")
    with conn.transaction(), conn.cursor() as cur:
        rb = cs.start_rule_run(conn, rr.RULE_RATIO, "rollback", "on", [], train=TRAIN,
                               before_image_ref=f"restore of {run_id}")  # fmt: skip
        out = rr.restore(cur, run_id)
        cs.finish_rule_run(conn, rb, {**out, "of_run": run_id})
    conn.commit()
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
