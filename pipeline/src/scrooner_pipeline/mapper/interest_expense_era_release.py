"""Release package 1 of rule interest_expense.era_tag_fill@1: fill blank interest_expense cells from the 2024+
taxonomy tags (InterestExpenseNonoperating for non-banks, InterestExpenseOperating for banks).

WHAT IT DOES. For every package cell, inserts analytics.canonical_fact rows for interest_expense AND
interest_expense_resolved at the cell's period, value = the filed fact's value, source_fact_ids = (that core.fact id),
through canonical_archive.replace_rows (each key logged 'inserted'), and appends one cell_evidence row (accession,
tag, label, plan digest). Only the plan's ``fill`` cells are in the package (pipeline/scripts/per_share/ie_plan.py,
ie_label_check.py): the period has no InterestExpense fact and no stored value, the new tag's label on the income
statement is gross, the value is positive, and the company's new tag equals InterestExpense in every shared period.

SAFETY CONTRACT (each guard has a test in tests/unit/test_interest_expense_era_release.py):
  * ``dry-run`` is the default and runs in a read-only session;
  * ``apply`` refuses unless the rule is ON, --confirm equals CONFIRM_TOKEN and the sha256 of cells.jsonl equals
    BOTH PACKAGE.json's digest and the reviewed digest argument, checked before any DB access;
  * STALE CELLS REFUSE THE WHOLE RUN before the first write: a stored interest_expense / interest_expense_resolved
    row now exists at the key, or the source fact is gone, demoted, derived or has another value;
  * one transaction per batch of companies, recorded in analytics.rule_run, with scrooner.slot_writer = 'on': the
    inserted rows, their analytics.slot_protected_cell rows (migration 0113: the nightly resolvers cannot overwrite
    or delete a protected cell) and the evidence commit together; apply refuses when 0113 is absent;
  * every held cell (keep_list.jsonl) gets an analytics.cell_blank_reason row, defect / guard_hidden, reason code =
    its hold code (owner tag_mapper); a held key that has a stored value by now is stale too;
  * restore(run_id): canonical_archive.restore_run + the run's protection rows and blank reasons deleted, one
    transaction. Evidence rows are append-only.
Ritwik's approval conditions (APPROVAL-INTEREST-EXPENSE-ERA-2026-10-31): (2) protection, (3) hold reasons, (4) the
package (cells.jsonl and keep_list.jsonl digests) is frozen at the Verifier's commit.

The nightly rebuild does not map these tags; the slot_protected_cell guard keeps the written rows. This module
registers nothing in any nightly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from scrooner_pipeline.common import cell_store as cs
from scrooner_pipeline.common.cell_contract import CellKey
from scrooner_pipeline.common.rule_flags import rule_enabled
from scrooner_pipeline.mapper import canonical_archive as ca

RULE_ID = "interest_expense.era_tag_fill@1"
CONFIRM_TOKEN = "RELEASE-INTEREST-EXPENSE-ERA-1"
TRAIN = "interest-expense-era-tag-fill-release-1"
CONCEPTS = ("interest_expense", "interest_expense_resolved")
BATCH_COMPANIES = 25
OWNER = "tag_mapper"
# hold code -> (root cause class, what the reader is told)
HOLD_REASONS = {
    "hold_net_label": ("composition", "Filed only on a net interest line (interest expense net of income); not shown."),
    "hold_no_overlap": ("evidence_pending", "The 2024 taxonomy tag has no period shared with the earlier tag and no plain face line to prove it is the same total; not shown."),
    "hold_nonbank_ieo": ("composition", "Only operating interest expense is tagged (a component, not the total); not shown."),
    "hold_not_on_face": ("composition", "The tagged amount is not on the income statement face; not shown."),
    "hold_label_unread": ("ingestion", "The filing's statement layout is not in our data set yet; not shown until it is read."),
    "hold_perimeter": ("composition", "The 2024 taxonomy tag differs from the earlier total in a shared period; not shown."),
    "hold_sign": ("filer_error", "The tagged amount has the wrong sign for an expense; not shown."),
}  # fmt: skip


class ReleaseRefused(RuntimeError):
    pass


@dataclass(frozen=True)
class Cell:
    company_id: int
    cik: str
    period_id: int
    start: str
    end: str
    months: int
    tag: str
    fact_id: int
    value: str
    accession: str
    label: str


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ------------------------------------------------------------------ build (file-only)
def build(plan_rows: list[dict[str, str]], out_dir: Path) -> dict[str, Any]:
    """Cut the package from the labelled plan (ie_label_check.py output): cells.jsonl = the fill rows; every other
    outcome goes to keep_list.jsonl with its reason (nothing is written for them)."""
    cells = sorted(
        (Cell(int(r["company_id"]), r["cik"], int(r["period_id"]), r["start"], r["end"], int(r["months"]), r["tag"],
              int(r["fact_id"]), r["value"], r["accession"], r["label"])
         for r in plan_rows if r["outcome"] == "fill"),
        key=lambda c: (c.company_id, c.period_id),
    )  # fmt: skip
    keep = [r for r in plan_rows if r["outcome"] != "fill"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "cells.jsonl"
    path.write_text("".join(json.dumps(c.__dict__) + "\n" for c in cells))
    (out_dir / "keep_list.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in keep)
    )
    (out_dir / "touched_ciks.txt").write_text(
        "".join(f"{k}\n" for k in sorted({c.cik for c in cells}))
    )
    manifest = {
        "rule_id": RULE_ID, "train": TRAIN, "confirm_token": CONFIRM_TOKEN, "digest": file_sha256(path),
        "cells": len(cells), "companies": len({c.company_id for c in cells}), "rows_to_insert": 2 * len(cells),
        "keep_cells": len(keep), "keep_by_outcome": {o: sum(1 for r in keep if r["outcome"] == o)
                                                     for o in sorted({r["outcome"] for r in keep})},
        "by_tag": {t: sum(1 for c in cells if c.tag == t) for t in sorted({c.tag for c in cells})},
        "before_image": "every key absent in interest_expense and interest_expense_resolved (checked by dry-run)",
    }  # fmt: skip
    manifest["keep_list_sha256"] = file_sha256(out_dir / "keep_list.jsonl")
    (out_dir / "PACKAGE.json").write_text(json.dumps(manifest, indent=1))
    return manifest


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
    cells = [
        Cell(**json.loads(line))
        for line in (package_dir / "cells.jsonl").read_text().splitlines()
    ]
    if len(cells) != manifest["cells"]:
        raise ReleaseRefused("package row count differs from PACKAGE.json")
    if file_sha256(package_dir / "keep_list.jsonl") != manifest.get("keep_list_sha256"):
        raise ReleaseRefused("keep_list.jsonl differs from PACKAGE.json")
    return cells


def load_holds(package_dir: Path) -> list[dict[str, str]]:
    holds = [
        json.loads(line)
        for line in (package_dir / "keep_list.jsonl").read_text().splitlines()
    ]
    unknown = {h["outcome"] for h in holds} - set(HOLD_REASONS)
    if unknown:
        raise ReleaseRefused(f"hold codes without a reason: {sorted(unknown)}")
    return holds


def _concept_ids(cur: Any) -> dict[str, int]:
    cur.execute(
        "select name, id from analytics.canonical_concept where name = any(%s)",
        (list(CONCEPTS),),
    )
    got = dict(cur.fetchall())
    if set(got) != set(CONCEPTS):
        raise ReleaseRefused(f"canonical concepts missing: {set(CONCEPTS) - set(got)}")
    return got


def stale_cells(
    cur: Any,
    cells: list[Cell],
    holds: Sequence[dict[str, str]] = (),
) -> list[str]:
    """Every cell that is no longer exactly as planned (empty: nothing is stale): a fill key or a held key that has a
    stored row now, or a fill's source fact gone / demoted / derived / changed."""
    ids = _concept_ids(cur)
    keys = {(c.company_id, c.period_id) for c in cells} | {
        (int(h["company_id"]), int(h["period_id"])) for h in holds
    }
    cur.execute(
        """select company_id, period_id from analytics.canonical_fact
           where canonical_concept_id = any(%s) and company_id = any(%s) and period_id = any(%s)""",
        (list(ids.values()), sorted({k[0] for k in keys}), sorted({k[1] for k in keys})),
    )  # fmt: skip
    taken = {(r[0], r[1]) for r in cur.fetchall()}
    cur.execute(
        "select id, value, is_authoritative, is_derived from core.fact where id = any(%s)",
        ([c.fact_id for c in cells],),
    )
    facts = {r[0]: (Decimal(r[1]), bool(r[2]), bool(r[3])) for r in cur.fetchall()}
    problems = [
        f"{h['cik']} {h['end']}: held cell has a stored interest_expense row now"
        for h in holds
        if (int(h["company_id"]), int(h["period_id"])) in taken
    ]
    for c in cells:
        if (c.company_id, c.period_id) in taken:
            problems.append(
                f"{c.cik} {c.end}: a stored interest_expense row exists now"
            )
        f = facts.get(c.fact_id)
        if f is None or not f[1] or f[2] or f[0] != Decimal(c.value):
            problems.append(
                f"{c.cik} {c.end}: source fact {c.fact_id} gone, demoted, derived or changed"
            )
    return problems


def dry_run(
    conn: Any,
    cells: list[Cell],
    holds: Sequence[dict[str, str]] = (),
) -> dict[str, Any]:
    conn.execute("set default_transaction_read_only = on")
    with conn.cursor() as cur:
        problems = stale_cells(cur, cells, holds)
    return {
        "cells": len(cells),
        "stale": len(problems),
        "stale_examples": problems[:20],
        "would_apply": not problems,
    }


def apply(
    conn: Any, package_dir: Path, reviewed_digest: str, confirm: str, *, environ=None
) -> dict[str, Any]:
    if not rule_enabled(RULE_ID, environ):
        raise ReleaseRefused(f"{RULE_ID} is not ON; nothing applied")
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused("confirm token mismatch; nothing applied")
    cells = load_package(package_dir, reviewed_digest)
    holds = load_holds(package_dir)
    with conn.cursor() as cur:
        cur.execute("select to_regclass('analytics.slot_protected_cell') is not null")
        if not cur.fetchone()[0]:
            raise ReleaseRefused(
                "migration 0113 (analytics.slot_protected_cell) is not applied; nothing applied"
            )
        problems = stale_cells(cur, cells, holds)
        ids = _concept_ids(cur)
    if problems:
        raise ReleaseRefused(
            f"{len(problems)} stale cells, e.g. {problems[:3]}; nothing applied"
        )
    run_id = cs.start_rule_run(conn, RULE_ID, "apply", "on", [c.cik for c in cells], train=TRAIN,
                               before_image_ref=f"keys absent; archive rows 'inserted' of this run; {reviewed_digest}")  # fmt: skip
    conn.commit()
    companies = sorted({c.company_id for c in cells})
    inserted = protected = reasons = 0
    for i in range(0, len(companies), BATCH_COMPANIES):
        part = set(companies[i : i + BATCH_COMPANIES])
        batch = [c for c in cells if c.company_id in part]
        with conn.transaction(), conn.cursor() as cur:
            cur.execute("set local scrooner.slot_writer = 'on'")
            rows = [ca.CanonicalRow(c.company_id, ids[name], c.period_id, Decimal(c.value), (c.fact_id,))
                    for c in batch for name in CONCEPTS]  # fmt: skip
            s = ca.replace_rows(
                cur,
                rows,
                reason_code=f"{RULE_ID}:fill",
                run_id=run_id,
                basis_version=RULE_ID,
            )
            if s["inserted"] != len(rows):
                raise ReleaseRefused(
                    f"batch would replace stored rows ({s}); rolled back"
                )
            inserted += s["inserted"]
            cur.executemany(
                """insert into analytics.slot_protected_cell
                       (company_id, canonical_concept_id, period_id, rule_id, value, run_id, package_sha256)
                   values (%s, %s, %s, %s, %s, %s, %s)""",
                [(r.company_id, r.canonical_concept_id, r.period_id, RULE_ID, r.value, run_id, reviewed_digest) for r in rows],
            )  # fmt: skip
            protected += len(rows)
            for c in batch:
                cs.append_evidence(
                    conn,
                    cs.EvidenceRecord(
                        key=CellKey(c.company_id, "interest_expense", "FY" if c.months == 12 else "Q",
                                    _date(c.start), _date(c.end)),
                        state_claimed="value", rule_id=RULE_ID, evidence_kind="detector_audit",
                        evidence_level="DATA-INFERRED", recorded_by="data_engineer", accession=c.accession,
                        locator=f"core.fact {c.fact_id};tag={c.tag};label={c.label};plan_sha256={reviewed_digest}",
                        detector_version="1", source_hash=reviewed_digest,
                    ),
                    import_key=hashlib.sha256(f"{run_id}|{c.company_id}|{c.period_id}".encode()).hexdigest(),
                )  # fmt: skip
    for i in range(0, len(holds), 500):
        with conn.transaction():
            reasons += cs.write_blank_reasons(conn, run_id, [
                cs.guard_hidden(
                    CellKey(int(h["company_id"]), "interest_expense", "FY" if h["months"] == "12" else "Q",
                            _date(h["start"]), _date(h["end"])),
                    RULE_ID, h["outcome"], OWNER, root_cause_class=HOLD_REASONS[h["outcome"]][0],
                    reason_text=HOLD_REASONS[h["outcome"]][1],
                    input_refs={"tag": h["tag"], "accession": h["accession"], "fact_id": h["fact_id"],
                                "label": h.get("label", ""), "package_digest": reviewed_digest},
                )
                for h in holds[i : i + 500]
            ])  # fmt: skip
    stats = {
        "inserted": inserted,
        "protected": protected,
        "hold_reasons": reasons,
        "cells": len(cells),
    }
    cs.finish_rule_run(conn, run_id, {**stats, "digest": reviewed_digest})
    conn.commit()
    return {"run_id": run_id, **stats}


def restore(conn: Any, run_id: str, confirm: str) -> dict[str, Any]:
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused("confirm token mismatch; nothing restored")
    rb = cs.start_rule_run(
        conn,
        RULE_ID,
        "rollback",
        "on",
        [],
        train=TRAIN,
        before_image_ref=f"restore of {run_id}",
    )
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("set local scrooner.slot_writer = 'on'")
        restored = ca.restore_run(cur, run_id)
        cur.execute(
            "delete from analytics.slot_protected_cell where run_id = %s and rule_id = %s",
            (run_id, RULE_ID),
        )
        unprotected = cur.rowcount
        reasons = cs.delete_run_blank_reasons(conn, run_id)
    out = {
        "restored_archive_rows": restored,
        "unprotected": unprotected,
        "hold_reasons_deleted": reasons,
    }
    cs.finish_rule_run(conn, rb, {**out, "of_run": run_id})
    conn.commit()
    return {"rollback_run_id": rb, **out}


def _date(s: str):
    from datetime import date

    return date.fromisoformat(s)


def main(argv: list[str] | None = None) -> int:
    import csv

    import psycopg

    from scrooner_pipeline.common.config import settings

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["build", "dry-run", "apply", "restore"])
    ap.add_argument("package_dir", type=Path)
    ap.add_argument("--plan", type=Path, help="build: ie_label_check.py output CSV")
    ap.add_argument("--digest", default="")
    ap.add_argument("--confirm", default="")
    ap.add_argument("--run-id", default="")
    args = ap.parse_args(argv)
    if args.cmd == "build":
        with args.plan.open(newline="") as fh:
            print(
                json.dumps(build(list(csv.DictReader(fh)), args.package_dir), indent=1)
            )
        return 0
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
                load_holds(args.package_dir),
            )
        elif args.cmd == "apply":
            out = apply(conn, args.package_dir, args.digest, args.confirm)
        else:
            out = restore(conn, args.run_id, args.confirm)
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
