"""Total debt on the FSN store: the Verifier-passed debt lane, run unchanged, as the store's only debt source.

Total debt is a SUM (face borrowing lines, CommercialPaper, current maturities from the note where the face has no
current side, and finance leases from the notes: founder 2026-11-04 item 5), so it cannot come from fsn_store.select,
which takes ONE mapped line per concept. The calc_position seeds that tried (bs.debt_*) mapped any custom child of
current liabilities as total debt (FAMILY-RELEASE-CASE-2026-11-09 §2: 7,335 lines in 5,441 filings, accounts payable
among them) and are no longer exported.

The lane is the one the gate and the tests run, in company mode on the shard's company directories, never retyped:
  era_detect.py --company -> assemble_fsn.py --company -> replay_debt_fsn.py --company
(pipeline/scripts/slot_records; Verifier debt v3 14/14, VERIFY-DEBT-RELEASE1-AMZN 3/3, the BS port gate). Its cells
become CELL-FORMAT cells here:
  * verdict 'publishable' -> a value: the lease-inclusive total, from the lane's chosen accession (the latest
    accepted filing printing the instant on its balance-sheet face), with the fsn.value ids of every summed fact;
  * any other verdict -> a defect blank carrying the lane's own reason.
Nothing is read from production; the database is read only for fsn.value lineage."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.fsn_store import select as sel

CONCEPT = "total_debt_resolved"
RULE_VALUE = "fsn.debt_lane@1"
RULE_HOLD = "fsn.debt_lane_hold@1"
LANE_DIR = Path(__file__).resolve().parents[3] / "scripts" / "slot_records"
CHAIN = ("era_detect.py", "assemble_fsn.py", "replay_debt_fsn.py")

# the lane's hold verdicts (replay_debt_fsn.replay) -> (defect_class, owner) and the text a user sees
HOLDS: dict[str, tuple[str, str, str]] = {
    "no_covering_record": (
        "composition",
        "tag_mapper",
        "No checked description of this company's debt lines covers this filing yet, so total debt is not added up.",
    ),
    "debt_lease_member_unverified": (
        "composition",
        "standardization_lead",
        "The balance sheet prints a lease liability line whose debt and non-debt parts are not proven, so total debt is not shown.",
    ),
    "note_finance_lease_below_face_members": (
        "composition",
        "verifier",
        "The notes give a finance-lease total below the lease lines on the balance sheet, so the two cannot be reconciled.",
    ),
    "latest_copy_lacks_note_finance_lease": (
        "definition_pending",
        "standardization_lead",
        "The latest filing for this date does not repeat the finance-lease figure an earlier filing gives; an older copy is not used instead.",
    ),
    "not_computable_uncovered_candidates": (
        "composition",
        "tag_mapper",
        "The balance sheet prints a debt-like line that is not yet classified, so total debt is not added up.",
    ),
    "custom_member_missing_in_filing": (
        "composition",
        "tag_mapper",
        "A debt line the company prints in other filings is missing from this one, so total debt is not added up.",
    ),
    "face_admission_tie_pending": (
        "evidence_pending",
        "verifier",
        "A debt line's amount does not yet tie to the printed totals, so total debt is not shown.",
    ),
    "not_computable_missing_member": (
        "composition",
        "tag_mapper",
        "A debt line is missing from this filing, so total debt is not added up.",
    ),
    "current_maturities_unverified": (
        "evidence_pending",
        "verifier",
        "The balance sheet has no current portion of debt, and the notes do not confirm whether one exists.",
    ),
}
# sectors whose total-debt perimeter is not defined yet: every key is a reasoned blank, never a partial sum.
# Banks (Tag Expert 2026-11-09, debt.md): ZION's lane total 548M left out "Federal funds and other short-term
# borrowings" 3,104M; EWBC stored 35.6M vs 3,035.6M (FHLB advances); AX, GABC, WFC, BAC, BNY perimeter errors.
# Deposits are never debt; FHLB advances, fed funds / repos and other borrowings await the Standardization Lead.
SECTOR_HOLDS: dict[str, str] = {"bank": "bank_debt_perimeter_pending"}
RULE_SECTOR_HOLD = "fsn.debt_sector_hold@1"
HOLDS["bank_debt_perimeter_pending"] = (
    "definition_pending",
    "standardization_lead",
    (
        "Total debt for banks is not shown until the bank definition is decided (FHLB advances, fed funds and repos, "
        "other borrowings); deposits are never debt."
    ),
)
for _code, (_cls, _owner, _text) in HOLDS.items():
    sel.REASONS.setdefault(_code, (_cls, _owner))
    sel.REASON_TEXT.setdefault(_code, _text)

_LEASE_SRC = re.compile(r"note_finance_lease_added:([A-Za-z+\-]+)=")
_EARLIER = re.compile(r"lease_tags_from_earlier_copy:([0-9-]+):([A-Za-z+]+)")


def run_lane(companies: Path, work: Path) -> Path:
    """Run the lane chain over every company directory under `companies` (company mode, python -I, the way the gate
    and the tests run it). Returns the replay report path; raises if any step fails."""
    work.mkdir(parents=True, exist_ok=True)
    dirs = sorted(
        p for p in Path(companies).iterdir() if (p / "manifest.json").exists()
    )
    (work / "dirs.txt").write_text("".join(f"{d}\n" for d in dirs))
    # assemble_fsn needs a cik,ticker map; the store has no ticker, so the CIK stands in (labels only)
    (work / "cohort.csv").write_text(
        "cik,ticker\n" + "".join(f"{int(d.name)},{int(d.name)}\n" for d in dirs)
    )
    src = f"@{work / 'dirs.txt'}"
    steps = (
        (
            "era_detect.py",
            "--company",
            src,
            work / "eras.json",
            work / "boundaries.txt",
        ),
        (
            "assemble_fsn.py",
            "--company",
            src,
            work / "eras.json",
            work / "cohort.csv",
            work / "records.jsonl",
        ),
        (
            "replay_debt_fsn.py",
            "--company",
            src,
            work / "records.jsonl",
            work / "replay.json",
        ),
    )
    for script, *args in steps:
        p = subprocess.run(
            [sys.executable, "-I", str(LANE_DIR / script), *map(str, args)],
            capture_output=True,
            text=True,
            check=False,
        )
        if p.returncode != 0:
            raise RuntimeError(f"{script} failed: {p.stderr[-2000:]}")
    return work / "replay.json"


def load_replay(path: Path | None) -> dict[int, list[dict[str, Any]]]:
    """Lane cells by integer CIK ({} without a report)."""
    if not path or not Path(path).exists():
        return {}
    out: dict[int, list[dict[str, Any]]] = {}
    for c in json.loads(Path(path).read_text())["cells"]:
        out.setdefault(int(c["cik"]), []).append(c)
    return out


def summed_tags(c: dict[str, Any]) -> tuple[set[str], dict[str, set[str]]]:
    """(tags read in the cell's own accession, {earlier accession: tags}) for every fact the lane summed."""
    own = {m[0] for m in c.get("members") or [] if m[1] != "operating_lease"}
    flag = c.get("note_flag") or ""
    if c.get("note_current_portion_added") is not None:
        own.add("LongTermDebtCurrent")
    m = _LEASE_SRC.search(flag)
    if m:
        own |= {t for t in re.split(r"[+\-]", m.group(1)) if t and "(" not in t}
    earlier: dict[str, set[str]] = {}
    for acc, tags in _EARLIER.findall(flag):
        earlier.setdefault(acc, set()).update(tags.split("+"))
        own -= set(tags.split("+"))
    return own, earlier


LINEAGE_SQL = """
    select v.id from fsn.value v join fsn.tag t on t.id = v.tag_id
    where v.filing_id = %s and v.ddate = %s and v.qtrs = 0 and v.uom = 'USD' and v.dim_id = 0 and v.iprx = 0
      and v.coreg = '' and v.value is not null and t.tag = any(%s)
"""


def debt_cells(
    conn: psycopg.Connection | None,
    lane: list[dict[str, Any]],
    filings: dict[int, sel.Filing],
    sector: str = "general",
) -> list[sel.Cell]:
    """The lane's cells of one company as store cells. A lane cell whose accession is not stored for the company is
    skipped (the store cannot cite it). In a sector of SECTOR_HOLDS every key is that sector's reasoned blank."""
    if sector in SECTOR_HOLDS:
        reason = SECTOR_HOLDS[sector]
        by_acc = {f.accession: f.id for f in filings.values()}
        return [
            sel.Cell(
                CONCEPT,
                date.fromisoformat(c["period_end"]),
                0,
                "defect",
                filing_id=by_acc[c["accession"]],
                rule_id=RULE_SECTOR_HOLD,
                reason_code=reason,
                input_refs={"sector": sector, "lane_verdict": c["verdict"]},
            )
            for c in lane
            if c["accession"] in by_acc
        ]
    by_acc = {f.accession: f.id for f in filings.values()}
    out: list[sel.Cell] = []
    for c in lane:
        fid = by_acc.get(c["accession"])
        if fid is None:
            continue
        d = date.fromisoformat(c["period_end"])
        refs = {
            k: c.get(k)
            for k in (
                "verdict",
                "record_filing_from",
                "members",
                "slot_borrowings",
                "note_current_portion_added",
                "note_finance_lease_added",
                "note_flag",
                "lease_lines_not_in_record",
                "missing_members",
                "missing_custom_members",
                "face_admission_tie_pending",
            )
            if c.get(k) not in (None, [], "")
        }
        if c["verdict"] == "publishable":
            ids: list[int] = []
            if conn is not None:
                own, earlier = summed_tags(c)
                with conn.cursor() as cur:
                    cur.execute(LINEAGE_SQL, (fid, d, sorted(own)))
                    ids += [r[0] for r in cur.fetchall()]
                    for acc, tags in earlier.items():
                        if acc in by_acc:
                            cur.execute(LINEAGE_SQL, (by_acc[acc], d, sorted(tags)))
                            ids += [r[0] for r in cur.fetchall()]
            out.append(
                sel.Cell(
                    CONCEPT,
                    d,
                    0,
                    "value",
                    Decimal(c["slot_lease_inclusive"]),
                    fid,
                    source_value_ids=sorted(ids),
                    rule_id=RULE_VALUE,
                    input_refs=refs,
                )
            )
        elif c["verdict"] in HOLDS:
            out.append(
                sel.Cell(
                    CONCEPT,
                    d,
                    0,
                    "defect",
                    filing_id=fid,
                    rule_id=RULE_HOLD,
                    reason_code=c["verdict"],
                    input_refs=refs,
                )
            )
        else:
            raise ValueError(
                f"unknown debt lane verdict {c['verdict']!r} ({c['cik']} {c['period_end']})"
            )
    return out
