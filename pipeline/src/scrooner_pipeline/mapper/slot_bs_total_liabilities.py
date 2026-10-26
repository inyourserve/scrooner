"""Production write path for release 1 of rule slot.bs_total_liabilities@1
(Data Engineer, 2026-10-26; doc 49 value-changing release procedure, steps 1-7).

WHAT IT DOES. Applies the reviewed release package
(pipeline/scripts/slot_records/results/release_bs_total_liabilities_1/) to
analytics.canonical_fact for concept total_liabilities_resolved:
    slot_differs               the stored value is replaced (before-image archived)
    slot_fills_blank           a row is inserted where none existed (logged 'inserted')
    slot_holds_prod_has_value  the confirmed-wrong stored value is removed
                               (archived) and a guard_hidden blank reason written
Every written cell also gets an append-only cell_evidence row (accession, rule
id, reading, rule, slot-record reference, package digest).

SAFETY CONTRACT (each guard has a mutation test in tests/unit/test_slot_bs_total_liabilities.py):
  * dry-run is the default; it opens a read-only session and writes nothing;
  * apply refuses unless rule_flags says the rule is ON, --confirm equals
    CONFIRM_TOKEN, and the sha256 of the cells file equals BOTH the digest in
    PACKAGE.json and the reviewed digest argument, checked BEFORE any DB access;
  * an unknown CIK, a missing/ambiguous period, or a stored value that is
    neither the package's "production" value nor its "slot" value (drift since
    the package was cut) refuses the WHOLE run before the first write;
  * one transaction per batch of companies: archive + canonical_fact change +
    evidence + blank reasons commit together or not at all; a failure rolls back
    the current batch and stops. Earlier committed batches stay and are listed in
    the report; the run is resumable (--resume-run-id: cells already at the slot
    value are skipped) or fully undone by restore(run_id);
  * restore(run_id) = canonical_archive.restore_run (migration 0098 table
    analytics.canonical_fact_retired) + deletion of that run's blank reasons.
    Evidence rows are append-only and are NOT deleted; the rollback run is
    recorded in rule_run (mode 'rollback').

CAVEATS stated rather than hidden:
  * the package carries no per-cell core.fact ids, so new rows have EMPTY
    source_fact_ids; their provenance is the cell_evidence row (accession,
    locator with the slot-record reference). A consumer that requires non-empty
    lineage will show these cells as lineage-less until the slot record store
    (migration 0101, not applied) feeds fact ids.
  * restore re-inserts replaced rows with NEW canonical_fact ids (same key,
    value, sources, resolved_at); the old ids are in the archive table.
  * the stage-2e / conflict-fill / dedup resolvers rewrite total_liabilities_resolved
    in the nightly; until those honor the slot rule, a nightly of an affected
    company can overwrite the written values. The Release Manager flips the
    default ON (procedure step 8) only together with that wiring; this module
    does NOT register itself in any nightly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from scrooner_pipeline.common import cell_store as cs
from scrooner_pipeline.common.cell_contract import CellKey
from scrooner_pipeline.common.rule_flags import rule_enabled, rule_mode
from scrooner_pipeline.mapper import canonical_archive as ca

RULE_ID = "slot.bs_total_liabilities@1"
CONCEPT_NAME = "total_liabilities_resolved"
DATA_POINT = "total_liabilities"
CONFIRM_TOKEN = "RELEASE-BS-TL-1"
TRAIN = "slot-bs-total-liabilities-release-1"
DEFAULT_BATCH_COMPANIES = 25
PACKAGE_DIR = (
    Path(__file__).resolve().parents[3]
    / "scripts"
    / "slot_records"
    / "results"
    / "release_bs_total_liabilities_1"
)
REASON_REPLACE = "slot_bs_total_liabilities_r1"
REASON_HIDE = "slot_bs_total_liabilities_r1_hide"
# Hidden cells: the slot identity does not tie and production's value was
# confirmed wrong by the Verifier; owner = the family's engineer lane.
HIDE_OWNER = "data_engineer_l1"
HIDE_ROOT_CAUSE = "composition"

STATE_DIFFERS = "slot_differs"
STATE_FILLS = "slot_fills_blank"
STATE_HIDES = "slot_holds_prod_has_value"


class ReleaseRefused(RuntimeError):
    """A guard stopped the run; nothing was written."""


# ------------------------------------------------------------------ package
@dataclass(frozen=True)
class Cell:
    cik: str
    end: date
    state: str
    slot: Decimal | None
    production: Decimal | None
    accession: str
    rule: str
    reading: str
    identity: str
    stratum: str


@dataclass(frozen=True)
class Package:
    cells: tuple[Cell, ...]
    digest: str
    before_image: dict[tuple[str, date], dict[str, Any]]  # (cik, end) -> row


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dec(v: Any) -> Decimal | None:
    return None if v is None else Decimal(str(v))


def load_package(
    package_dir: Path, reviewed_digest: str | None, *, require_digest: bool = True
) -> Package:
    """Read and verify the package. The digest check happens here, before the
    caller opens any database connection."""
    meta = json.loads((package_dir / "PACKAGE.json").read_text())
    r1 = meta["release1"]
    if meta["rule_id"] != RULE_ID:
        raise ReleaseRefused(f"package is for {meta['rule_id']}, not {RULE_ID}")
    cells_path = package_dir / r1["cells_file"]
    actual = file_sha256(cells_path)
    if actual != r1["sha256"]:
        raise ReleaseRefused(
            f"cells file digest {actual} != PACKAGE.json digest {r1['sha256']}"
        )
    if require_digest and (reviewed_digest or "").strip().lower() != actual:
        raise ReleaseRefused(
            f"cells file digest {actual} != the reviewed digest argument "
            f"{reviewed_digest!r}"
        )
    cells: list[Cell] = []
    for line in cells_path.read_text().splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        if d.get("release") != "1":
            raise ReleaseRefused(f"cell outside release 1: {d}")
        cells.append(
            Cell(
                cik=d["cik"],
                end=date.fromisoformat(d["end"]),
                state=d["state"],
                slot=_dec(d.get("slot")),
                production=_dec(d.get("production")),
                accession=d["accession"],
                rule=d["rule"],
                reading=d["reading"],
                identity=d["identity"],
                stratum=d["stratum"],
            )
        )
    if len(cells) != r1["cells"]:
        raise ReleaseRefused(f"{len(cells)} cells, PACKAGE.json says {r1['cells']}")
    counts: dict[str, int] = defaultdict(int)
    for c in cells:
        counts[c.state] += 1
    if dict(counts) != r1["by_state"]:
        raise ReleaseRefused(f"state counts {dict(counts)} != {r1['by_state']}")
    if len({c.cik for c in cells}) != r1["companies"]:
        raise ReleaseRefused("company count differs from PACKAGE.json")
    if len({(c.cik, c.end) for c in cells}) != len(cells):
        raise ReleaseRefused("duplicate (cik, end) cell in the package")
    for c in cells:
        ok = {
            STATE_DIFFERS: c.slot is not None and c.production is not None,
            STATE_FILLS: c.slot is not None and c.production is None,
            STATE_HIDES: c.slot is None and c.production is not None,
        }.get(c.state)
        if not ok:
            raise ReleaseRefused(f"cell {c.cik} {c.end}: state {c.state!r} inconsistent")
    before: dict[tuple[str, date], dict[str, Any]] = {}
    bi_path = package_dir / "bs_release_r1_before_image.jsonl"
    for line in bi_path.read_text().splitlines():
        if line.strip():
            d = json.loads(line)
            before[(d["cik"], date.fromisoformat(d["end"]))] = d
    expected = json.loads((package_dir / "bs_release_r1_plan.json").read_text())[
        "before_image_rows"
    ]
    if len(before) != expected:
        raise ReleaseRefused(f"before-image has {len(before)} rows, plan says {expected}")
    return Package(tuple(cells), actual, before)


# --------------------------------------------------------------------- plan
@dataclass
class PlannedCell:
    cell: Cell
    action: str  # change | fill | hide | already
    company_id: int
    period_id: int
    canonical_fact_id: int | None


def plan(cur, pkg: Package) -> tuple[list[PlannedCell], dict[str, Any]]:
    """Read-only. Resolves ids and checks every cell against the live row.
    Raises ReleaseRefused listing the problems; never writes."""
    problems: list[str] = []
    ciks = sorted({c.cik for c in pkg.cells})
    cur.execute("select cik, id from core.company where cik = any(%s)", (ciks,))
    company_id = dict(cur.fetchall())
    for cik in ciks:
        if cik not in company_id:
            problems.append(f"unknown company cik {cik}")
    cur.execute(
        "select id from analytics.canonical_concept where name = %s", (CONCEPT_NAME,)
    )
    rows = cur.fetchall()
    if len(rows) != 1:
        raise ReleaseRefused(f"canonical_concept {CONCEPT_NAME}: {len(rows)} rows")
    concept_id = rows[0][0]
    for b in pkg.before_image.values():
        if b["canonical_concept_id"] != concept_id:
            raise ReleaseRefused("before-image concept id differs from the live one")
    if problems:
        raise ReleaseRefused("; ".join(problems[:20]))
    cids = sorted(company_id.values())
    cur.execute(
        """
        select cf.id, cf.company_id, cf.period_id, cf.value, p.end_date, p.period_type
        from analytics.canonical_fact cf join core.period p on p.id = cf.period_id
        where cf.canonical_concept_id = %s and cf.company_id = any(%s)
        """,
        (concept_id, cids),
    )
    live = {(r[1], r[4]): r for r in cur.fetchall()}
    cur.execute(
        """
        select company_id, end_date, id from core.period
        where company_id = any(%s) and period_type = 'instant'
        """,
        (cids,),
    )
    periods: dict[tuple[int, date], list[int]] = defaultdict(list)
    for cid, end, pid in cur.fetchall():
        periods[(cid, end)].append(pid)
    planned: list[PlannedCell] = []
    for c in pkg.cells:
        cid = company_id[c.cik]
        row = live.get((cid, c.end))
        b = pkg.before_image.get((c.cik, c.end))
        if row is not None and row[5] != "instant":
            problems.append(f"{c.cik} {c.end}: stored row is not on an instant period")
            continue
        if c.state in (STATE_DIFFERS, STATE_HIDES):
            if b is None:
                problems.append(f"{c.cik} {c.end}: no before-image row")
                continue
            if Decimal(b["value_before"]) != c.production:
                problems.append(f"{c.cik} {c.end}: before-image != package production")
                continue
        if row is None:
            if c.state == STATE_HIDES:
                planned.append(PlannedCell(c, "already", cid, 0, None))
                continue
            if c.state == STATE_DIFFERS:
                problems.append(f"{c.cik} {c.end}: stored row vanished (drift)")
                continue
            pids = periods.get((cid, c.end), [])
            if len(pids) != 1:
                problems.append(f"{c.cik} {c.end}: {len(pids)} instant periods (need 1)")
                continue
            planned.append(PlannedCell(c, "fill", cid, pids[0], None))
            continue
        fid, _, pid, val = row[0], row[1], row[2], row[3]
        if b is not None and b["period_id"] != pid:
            problems.append(f"{c.cik} {c.end}: period id differs from the before-image")
            continue
        if c.state == STATE_DIFFERS:
            if val == c.production:
                planned.append(PlannedCell(c, "change", cid, pid, fid))
            elif val == c.slot:
                planned.append(PlannedCell(c, "already", cid, pid, fid))
            else:
                problems.append(f"{c.cik} {c.end}: stored {val} is neither production nor slot")
        elif c.state == STATE_FILLS:
            if val == c.slot:
                planned.append(PlannedCell(c, "already", cid, pid, fid))
            else:
                problems.append(f"{c.cik} {c.end}: fill cell has stored value {val}")
        else:
            if val == c.production:
                planned.append(PlannedCell(c, "hide", cid, pid, fid))
            else:
                problems.append(f"{c.cik} {c.end}: hide cell stored {val} != production")
    if problems:
        raise ReleaseRefused(
            f"{len(problems)} cell(s) refused, nothing written: " + "; ".join(problems[:20])
        )
    per_company: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for p in planned:
        per_company[p.cell.cik][p.action] += 1
    summary = {
        "concept_id": concept_id,
        "cells": len(planned),
        "changed": sum(p.action == "change" for p in planned),
        "filled": sum(p.action == "fill" for p in planned),
        "hidden": sum(p.action == "hide" for p in planned),
        "already_applied": sum(p.action == "already" for p in planned),
        "companies": len(per_company),
        "per_company": {k: dict(v) for k, v in sorted(per_company.items())},
    }
    return planned, summary


# -------------------------------------------------------------------- apply
def _locator(c: Cell, digest: str) -> str:
    return (
        f"{RULE_ID};release=1;rule={c.rule};reading={c.reading};identity={c.identity};"
        f"slot_record=slot_rows_bs_cohort.jsonl.gz#cik={c.cik},end={c.end},accession={c.accession};"
        f"package_sha256={digest}"
    )


def _import_key(run_id: str, c: Cell) -> str:
    return hashlib.sha256(f"{run_id}|{RULE_ID}|{c.cik}|{c.end}|{c.state}".encode()).hexdigest()


def apply_batch(
    conn, run_id: str, digest: str, batch: list[PlannedCell], concept_id: int
) -> dict[str, int]:
    """ONE transaction: archive + canonical_fact change + evidence + reasons.
    Commits only if everything succeeded; any exception rolls back and re-raises."""
    stats = {"replaced": 0, "inserted": 0, "removed": 0, "evidence": 0, "reasons": 0}
    try:
        with conn.cursor() as cur:
            rows = [
                ca.CanonicalRow(p.company_id, concept_id, p.period_id, p.cell.slot, ())
                for p in batch
                if p.action in ("change", "fill")
            ]
            s = ca.replace_rows(cur, rows, reason_code=REASON_REPLACE, run_id=run_id,
                                basis_version=RULE_ID)
            stats["replaced"], stats["inserted"] = s["replaced"], s["inserted"]
            hide_ids = [p.canonical_fact_id for p in batch if p.action == "hide"]
            stats["removed"] = ca.archive_and_remove(
                cur, hide_ids, reason_code=REASON_HIDE, run_id=run_id, basis_version=RULE_ID
            )
        reasons = []
        for p in batch:
            if p.action not in ("change", "fill", "hide"):
                continue
            c = p.cell
            key = CellKey(p.company_id, DATA_POINT, "I", c.end, c.end)
            cs.append_evidence(
                conn,
                cs.EvidenceRecord(
                    key=key,
                    state_claimed="defect" if p.action == "hide" else "value",
                    rule_id=RULE_ID,
                    evidence_kind="detector_audit",
                    evidence_level="DATA-INFERRED",
                    recorded_by="data_engineer",
                    accession=c.accession,
                    locator=_locator(c, digest),
                    detector_version="1",
                    source_hash=digest,
                ),
                import_key=_import_key(run_id, c),
            )
            stats["evidence"] += 1
            if p.action == "hide":
                reasons.append(
                    cs.guard_hidden(
                        key,
                        RULE_ID,
                        "slot_identity_gap_production_wrong",
                        HIDE_OWNER,
                        root_cause_class=HIDE_ROOT_CAUSE,
                        reason_text="Verifier-confirmed wrong stored total; the filing's "
                        "balance-sheet identity does not tie under the slot rule.",
                        input_refs={"accession": c.accession, "production": str(c.production)},
                    )
                )
        stats["reasons"] = cs.write_blank_reasons(conn, run_id, reasons)
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    return stats


def _touched_report(ciks: list[str]) -> str:
    return ",".join(ciks)


def apply(
    conn,
    pkg: Package,
    *,
    confirm: str,
    environ=None,
    batch_companies: int = DEFAULT_BATCH_COMPANIES,
    git_commit: str | None = None,
    resume_run_id: str | None = None,
) -> dict[str, Any]:
    """Guards first (no DB access before they pass), then plan, then batches."""
    if not rule_enabled(RULE_ID, environ):
        raise ReleaseRefused(f"{RULE_ID} is not ON (mode {rule_mode(RULE_ID, environ)})")
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused(f"--confirm must equal {CONFIRM_TOKEN}")
    if batch_companies < 1:
        raise ReleaseRefused("batch_companies must be >= 1")
    with conn.cursor() as cur:
        planned, summary = plan(cur, pkg)
    conn.rollback()  # end the read transaction
    todo = [p for p in planned if p.action != "already"]
    by_cik: dict[str, list[PlannedCell]] = defaultdict(list)
    for p in todo:
        by_cik[p.cell.cik].append(p)
    ciks = sorted(by_cik)
    if resume_run_id:
        run_id = resume_run_id
        with conn.cursor() as cur:
            cur.execute(
                "select rule_id, mode, finished_at from analytics.rule_run where run_id = %s::uuid",
                (run_id,),
            )
            row = cur.fetchone()
        conn.rollback()
        if row is None or row[0] != RULE_ID or row[1] != "apply" or row[2] is not None:
            raise ReleaseRefused(f"run {run_id} is not an unfinished apply run of {RULE_ID}")
    else:
        run_id = cs.start_rule_run(
            conn, RULE_ID, "apply", "on", ciks, train=TRAIN, git_commit=git_commit,
            before_image_ref=f"analytics.canonical_fact_retired by run_id; package sha256 {pkg.digest}",
        )
        conn.commit()
    totals = {"replaced": 0, "inserted": 0, "removed": 0, "evidence": 0, "reasons": 0}
    committed_batches = 0
    for i in range(0, len(ciks), batch_companies):
        group = ciks[i : i + batch_companies]
        batch = [p for cik in group for p in by_cik[cik]]
        s = apply_batch(conn, run_id, pkg.digest, batch, summary["concept_id"])
        committed_batches += 1
        for k, v in s.items():
            totals[k] += v
    result = {
        "run_id": run_id,
        "rule_id": RULE_ID,
        "batches_committed": committed_batches,
        "touched_ciks": ciks,
        "plan": {k: v for k, v in summary.items() if k != "per_company"},
        **totals,
    }
    cs.finish_rule_run(conn, run_id, {k: v for k, v in result.items() if k != "touched_ciks"})
    conn.commit()
    return result


# ------------------------------------------------------------------ restore
def restore(conn, run_id: str, *, environ=None, confirm: str = "") -> dict[str, Any]:
    """Undo one apply run exactly: deletes the keys it inserted, puts back the
    replaced/removed before-images, deletes its blank reasons. One transaction."""
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused(f"--confirm must equal {CONFIRM_TOKEN}")
    with conn.cursor() as cur:
        cur.execute(
            "select rule_id, mode, ciks from analytics.rule_run where run_id = %s::uuid",
            (run_id,),
        )
        row = cur.fetchone()
    if row is None or row[0] != RULE_ID or row[1] != "apply":
        conn.rollback()
        raise ReleaseRefused(f"{run_id} is not an apply run of {RULE_ID}")
    ciks = list(row[2])
    try:
        with conn.cursor() as cur:
            restored = ca.restore_run(cur, run_id)
        reasons = cs.delete_run_blank_reasons(conn, run_id)
        rb = cs.start_rule_run(conn, RULE_ID, "rollback", "off", ciks, train=TRAIN,
                               before_image_ref=f"restore of {run_id}")
        cs.finish_rule_run(conn, rb, {"restored_archive_rows": restored,
                                      "blank_reasons_deleted": reasons, "of_run": run_id})
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    return {"restored_archive_rows": restored, "blank_reasons_deleted": reasons,
            "rollback_run_id": rb, "touched_ciks": ciks}


# --------------------------------------------------------------- downstream
def downstream_consumers(cur, concept_id: int) -> list[str]:
    """Active metrics whose structured inputs include the concept (read from
    the live definition tables, not from memory)."""
    cur.execute(
        """
        select distinct d.metric_name from analytics.metric_definition_input i
        join analytics.metric_definition d on d.id = i.metric_definition_id
        where i.canonical_concept_id = %s and d.status = 'active' order by 1
        """,
        (concept_id,),
    )
    return [r[0] for r in cur.fetchall()]


def run_downstream(conn, ciks: list[str], concept_id: int) -> dict[str, Any]:
    """Recompute everything that reads total_liabilities_resolved for the touched
    companies: metrics that list it as an input (if any), the balance-sheet
    accounting identity checks, and period completeness. Stages commit in their
    own way; run only in a heavy slot."""
    from scrooner_pipeline.mapper.calculate import calculate
    from scrooner_pipeline.sanity.accounting_identity import run_all as identities
    from scrooner_pipeline.sanity.period_completeness import run as completeness

    out: dict[str, Any] = {}
    with conn.cursor() as cur:
        consumers = downstream_consumers(cur, concept_id)
    conn.rollback()
    out["metric_consumers"] = consumers
    if consumers:
        out["calculate"] = calculate(conn, set(ciks))
    out["accounting_identity"] = identities(conn, ciks=set(ciks))
    out["period_completeness"] = completeness(conn, set(ciks))
    return out


# ---------------------------------------------------------------------- CLI
def _git_commit() -> str | None:
    import subprocess

    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return None


def main(argv: list[str] | None = None, environ=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("dry-run", "apply"):
        sp = sub.add_parser(name)
        sp.add_argument("--package-dir", type=Path, default=PACKAGE_DIR)
        sp.add_argument("--digest", required=True, help="reviewed sha256 of the cells file")
    ap_apply = sub.choices["apply"]
    ap_apply.add_argument("--confirm", default="")
    ap_apply.add_argument("--batch-companies", type=int, default=DEFAULT_BATCH_COMPANIES)
    ap_apply.add_argument("--resume-run-id")
    ap_apply.add_argument("--skip-downstream", action="store_true")
    sp = sub.add_parser("restore")
    sp.add_argument("--run-id", required=True)
    sp.add_argument("--confirm", default="")
    args = ap.parse_args(argv)

    from scrooner_pipeline.db.connection import get_connection

    try:
        if args.cmd == "restore":
            with get_connection() as conn:
                print(json.dumps(restore(conn, args.run_id, confirm=args.confirm), indent=1))
            return 0
        pkg = load_package(args.package_dir, args.digest)  # before any DB access
        if args.cmd == "dry-run":
            with get_connection() as conn:
                conn.read_only = True
                with conn.cursor() as cur:
                    planned, summary = plan(cur, pkg)
                    consumers = downstream_consumers(cur, summary["concept_id"])
            print(f"rule {RULE_ID} mode={rule_mode(RULE_ID, environ)} digest={pkg.digest} DRY RUN, nothing written")
            for k in ("cells", "changed", "filled", "hidden", "already_applied", "companies"):
                print(f"  {k}: {summary[k]}")
            print(f"  metric consumers of {CONCEPT_NAME}: {consumers or 'none in metric_definition_input'}")
            for cik, v in summary["per_company"].items():
                print(f"  {cik} {v}")
            return 0
        with get_connection() as conn:
            res = apply(conn, pkg, confirm=args.confirm, environ=environ,
                        batch_companies=args.batch_companies, git_commit=_git_commit(),
                        resume_run_id=args.resume_run_id)
            print(json.dumps({k: v for k, v in res.items() if k != "touched_ciks"}, indent=1))
            if not args.skip_downstream:
                print(json.dumps(run_downstream(conn, res["touched_ciks"],
                                                res["plan"]["concept_id"]), indent=1, default=str))
            print("touched ciks (certify rerun):", _touched_report(res["touched_ciks"]))
        return 0
    except ReleaseRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
