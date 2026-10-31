"""Release package 1 of rule quick_ratio.inventory_evidence@1: hide the planned quick_ratio cells (plan v7).

WHAT IT DOES. Sets ``value = null``, ``is_null_reason = <plan reason>``, ``source_fact_ids = null`` on the
analytics.metric_value rows listed in the package (``build`` cuts it from plan v7 and a read-only read of the live
rows). Nothing else is touched; the keep-list names every cohort quick_ratio cell the plan leaves alone.

SAFETY CONTRACT (each guard has a test in tests/unit/test_quick_ratio_release.py):
  * ``dry-run`` is the default and runs in a read-only session;
  * ``apply`` refuses unless the rule is ON, --confirm equals CONFIRM_TOKEN and the sha256 of cells.jsonl equals
    BOTH PACKAGE.json's digest and the reviewed digest argument, checked before any DB access;
  * STALE CELLS REFUSE THE WHOLE RUN before the first write: a missing row, or a live value / reason / sources
    that differ from the before-image (the nightly recomputed it since the package was cut). Each UPDATE also
    re-checks the before value, so a row changed between the check and the write rolls its batch back;
  * one transaction per batch of companies, recorded in analytics.rule_run (mode apply); restore(run_id) puts
    every hidden row of that run back from the before-image (rule_run mode rollback), refusing rows that are no
    longer in the hidden state this package wrote.

CAVEAT stated rather than hidden: the nightly Mapper recomputes metric_value. With the rule OFF it writes the
legacy values back; with it ON it needs the face evidence (SCROONER_QR_FACE_FILE = qr_face_v7.jsonl from
fsn-notes) or it falls back to "no readable statement" and keeps values. The Release Manager switches the
runtime rule ON together with the face wiring; this module registers nothing in any nightly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from scrooner_pipeline.common import cell_store as cs
from scrooner_pipeline.common.rule_flags import rule_enabled
from scrooner_pipeline.mapper import quick_ratio_evidence as qe

RULE_ID = qe.RULE_ID
CONFIRM_TOKEN = "RELEASE-QUICK-RATIO-1"
TRAIN = "quick-ratio-inventory-evidence-release-1"
BATCH_COMPANIES = 25
ROW_SQL = """select id, company_id, period_end, period_label, value, is_null_reason, source_fact_ids
             from analytics.metric_value where id = any(%s)"""


class ReleaseRefused(RuntimeError):
    pass


@dataclass(frozen=True)
class Cell:
    metric_value_id: int
    company_id: int
    cik: str
    period_end: str
    period_label: str
    reason: str
    before_value: str | None
    before_reason: str | None
    before_sources: tuple[int, ...] | None


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _row_state(row: tuple) -> tuple[str | None, str | None, tuple[int, ...] | None]:
    _id, _cid, _end, _label, value, reason, sources = row
    return (
        None if value is None else str(Decimal(value)),
        reason,
        None if sources is None else tuple(sources),
    )


# ------------------------------------------------------------------ build (read-only)
def build(
    conn: Any, plan_cells: list[dict], cohort_ids: list[int], out_dir: Path
) -> dict[str, Any]:
    """Cut the package from the plan and the live rows (read-only). A planned cell whose live row no longer stores
    the planned value is left out and listed (stale at build time), never guessed."""
    conn.execute("set default_transaction_read_only = on")
    planned = {
        (c["company_id"], c["period_end"], c["period_label"]): c for c in plan_cells
    }
    rows = conn.execute(
        """select mv.id, mv.company_id, mv.period_end, mv.period_label, mv.value, mv.is_null_reason,
                  mv.source_fact_ids, c.cik
           from analytics.metric_value mv join analytics.metric_definition md on md.id = mv.metric_definition_id
           join core.company c on c.id = mv.company_id
           where md.metric_name = 'quick_ratio' and mv.company_id = any(%s) and mv.period_label <> 'TTM'""",
        (cohort_ids,),
    ).fetchall()
    cells, keep, stale = [], [], []
    seen = set()
    for r in rows:
        key = (r[1], str(r[2]), r[3])
        value, reason, sources = _row_state(r[:7])
        p = planned.get(key)
        if p is None:
            keep.append({"metric_value_id": r[0], "company_id": r[1], "cik": r[7], "period_end": key[1],
                         "period_label": r[3], "value": value})  # fmt: skip
            continue
        seen.add(key)
        if value is None or Decimal(value) != Decimal(p["stored"]):
            stale.append({**p, "live_value": value})
            continue
        cells.append(
            Cell(r[0], r[1], r[7], key[1], r[3], p["reason"], value, reason, sources)
        )
    stale += [
        {**p, "live_value": "row missing"} for k, p in planned.items() if k not in seen
    ]
    cells.sort(key=lambda c: c.metric_value_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    cells_path = out_dir / "cells.jsonl"
    cells_path.write_text("".join(json.dumps(
        {"metric_value_id": c.metric_value_id, "company_id": c.company_id, "cik": c.cik,
         "period_end": c.period_end, "period_label": c.period_label, "reason": c.reason}) + "\n" for c in cells))  # fmt: skip
    (out_dir / "before_image.jsonl").write_text("".join(json.dumps(
        {"metric_value_id": c.metric_value_id, "value": c.before_value, "is_null_reason": c.before_reason,
         "source_fact_ids": None if c.before_sources is None else list(c.before_sources)}) + "\n" for c in cells))  # fmt: skip
    (out_dir / "keep_list.jsonl").write_text(
        "".join(json.dumps(k) + "\n" for k in keep)
    )
    (out_dir / "stale_at_build.jsonl").write_text(
        "".join(json.dumps(s, default=str) + "\n" for s in stale)
    )
    (out_dir / "touched_ciks.txt").write_text(
        "".join(f"{cik}\n" for cik in sorted({c.cik for c in cells}))
    )
    manifest = {
        "rule_id": RULE_ID, "train": TRAIN, "confirm_token": CONFIRM_TOKEN,
        "digest": file_sha256(cells_path), "cells": len(cells), "companies": len({c.company_id for c in cells}),
        "keep_cells": len(keep), "stale_at_build": len(stale),
        "before_image_sha256": file_sha256(out_dir / "before_image.jsonl"),
        "by_reason": {r: sum(1 for c in cells if c.reason == r) for r in sorted({c.reason for c in cells})},
    }  # fmt: skip
    (out_dir / "PACKAGE.json").write_text(json.dumps(manifest, indent=1))
    return manifest


# ------------------------------------------------------------------ load / check
def load_package(
    package_dir: Path, reviewed_digest: str | None, *, require_digest: bool = True
) -> list[Cell]:
    manifest = json.loads((package_dir / "PACKAGE.json").read_text())
    actual = file_sha256(package_dir / "cells.jsonl")
    if actual != manifest["digest"]:
        raise ReleaseRefused(
            f"cells.jsonl digest {actual} != PACKAGE.json digest {manifest['digest']}"
        )
    if require_digest and (reviewed_digest or "").strip().lower() != actual:
        raise ReleaseRefused(
            f"cells.jsonl digest {actual} != the reviewed digest {reviewed_digest!r}"
        )
    if (
        file_sha256(package_dir / "before_image.jsonl")
        != manifest["before_image_sha256"]
    ):
        raise ReleaseRefused("before_image.jsonl digest differs from PACKAGE.json")
    before = {}
    for line in (package_dir / "before_image.jsonl").read_text().splitlines():
        b = json.loads(line)
        before[b["metric_value_id"]] = b
    cells = []
    for line in (package_dir / "cells.jsonl").read_text().splitlines():
        d = json.loads(line)
        b = before.get(d["metric_value_id"])
        if b is None:
            raise ReleaseRefused(
                f"metric_value {d['metric_value_id']}: no before-image row"
            )
        cells.append(Cell(d["metric_value_id"], d["company_id"], d["cik"], d["period_end"], d["period_label"],
                          d["reason"], b["value"], b["is_null_reason"],
                          None if b["source_fact_ids"] is None else tuple(b["source_fact_ids"])))  # fmt: skip
    if len(cells) != manifest["cells"] or len(before) != len(cells):
        raise ReleaseRefused("package row counts differ from PACKAGE.json")
    return cells


def stale_cells(cur: Any, cells: list[Cell]) -> list[str]:
    """Every cell whose live row is missing or differs from its before-image (empty list: nothing is stale)."""
    cur.execute(ROW_SQL, ([c.metric_value_id for c in cells],))
    live = {r[0]: _row_state(r) for r in cur.fetchall()}
    problems = []
    for c in cells:
        state = live.get(c.metric_value_id)
        if state is None:
            problems.append(f"{c.metric_value_id} {c.cik} {c.period_end}: row missing")
        elif state != (c.before_value, c.before_reason, c.before_sources):
            problems.append(
                f"{c.metric_value_id} {c.cik} {c.period_end}: live {state} != before-image"
            )
    return problems


def dry_run(conn: Any, cells: list[Cell]) -> dict[str, Any]:
    conn.execute("set default_transaction_read_only = on")
    with conn.cursor() as cur:
        problems = stale_cells(cur, cells)
    return {"cells": len(cells), "stale": len(problems), "stale_examples": problems[:20],
            "would_apply": not problems}  # fmt: skip


# ------------------------------------------------------------------ apply / restore
def apply(
    conn: Any, package_dir: Path, reviewed_digest: str, confirm: str, *, environ=None
) -> dict[str, Any]:
    if not rule_enabled(RULE_ID, environ):
        raise ReleaseRefused(f"{RULE_ID} is not ON; nothing applied")
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused("confirm token mismatch; nothing applied")
    cells = load_package(package_dir, reviewed_digest)
    with conn.cursor() as cur:
        problems = stale_cells(cur, cells)
    if problems:
        raise ReleaseRefused(
            f"{len(problems)} stale cells, e.g. {problems[:3]}; nothing applied"
        )
    run_id = cs.start_rule_run(conn, RULE_ID, "apply", "on", [c.cik for c in cells], train=TRAIN,
                               before_image_ref=f"{package_dir}/before_image.jsonl sha {reviewed_digest}")  # fmt: skip
    conn.commit()
    by_company: dict[int, list[Cell]] = {}
    for c in cells:
        by_company.setdefault(c.company_id, []).append(c)
    companies = sorted(by_company)
    hidden = 0
    for i in range(0, len(companies), BATCH_COMPANIES):
        batch = [
            c for cid in companies[i : i + BATCH_COMPANIES] for c in by_company[cid]
        ]
        with conn.transaction(), conn.cursor() as cur:
            for c in batch:
                cur.execute(
                    """update analytics.metric_value set value = null, is_null_reason = %s, source_fact_ids = null
                       where id = %s and value = %s::numeric""",
                    (c.reason, c.metric_value_id, c.before_value),
                )
                if cur.rowcount != 1:
                    raise ReleaseRefused(
                        f"{c.metric_value_id}: changed since the check; batch rolled back"
                    )
        hidden += len(batch)
    cs.finish_rule_run(conn, run_id, {"hidden": hidden, "digest": reviewed_digest})
    conn.commit()
    return {"run_id": run_id, "hidden": hidden}


def restore(conn: Any, package_dir: Path, run_id: str, confirm: str) -> dict[str, Any]:
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused("confirm token mismatch; nothing restored")
    cells = load_package(package_dir, None, require_digest=False)
    rb = cs.start_rule_run(conn, RULE_ID, "rollback", "on", [c.cik for c in cells], train=TRAIN,
                           before_image_ref=f"restore of {run_id}")  # fmt: skip
    restored, skipped = 0, []
    with conn.transaction(), conn.cursor() as cur:
        for c in cells:
            cur.execute(
                """update analytics.metric_value set value = %s::numeric, is_null_reason = %s, source_fact_ids = %s
                   where id = %s and value is null and is_null_reason = %s""",
                (c.before_value, c.before_reason, None if c.before_sources is None else list(c.before_sources),
                 c.metric_value_id, c.reason),
            )  # fmt: skip
            if cur.rowcount == 1:
                restored += 1
            else:
                skipped.append(c.metric_value_id)
    cs.finish_rule_run(
        conn, rb, {"restored": restored, "skipped": len(skipped), "of_run": run_id}
    )
    conn.commit()
    return {"rollback_run_id": rb, "restored": restored, "skipped": skipped}


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
    # dry-run: autocommit, so the read-only default covers every statement it issues
    with psycopg.connect(
        settings.database_url, autocommit=args.cmd == "dry-run"
    ) as conn:
        conn.execute("set statement_timeout = '120s'")
        if args.cmd == "dry-run":
            out = dry_run(
                conn,
                load_package(
                    args.package_dir, args.digest, require_digest=bool(args.digest)
                ),
            )
        elif args.cmd == "apply":
            out = apply(conn, args.package_dir, args.digest, args.confirm)
        else:
            out = restore(conn, args.package_dir, args.run_id, args.confirm)
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
