"""Debt family, zero-cal re-measure over the cohort (database reads only, no
SEC requests). Dhairya's condition before any debt cal fetch (2026-10-25).

Members per era: STANDARD face lines of the balance sheet that read as debt
(build_debt_slots.DEBT_RX, not EXCLUDE_RX / EXCLUDE_CLASSES), printed in the
liabilities zone (face_admission.liabilities_zone), never an Abstract or a
debit-balance element. Taxonomy total elements are never summed beside their
components: LongTermDebt beside LongTermDebtCurrent/Noncurrent, DebtCurrent
beside ShortTermBorrowings/LongTermDebtCurrent, LongTermDebtAndCapitalLease
Obligations beside its Current/Noncurrent parts. Custom debt lines make the
cell needs_instance_reader (values come from the instance / FSDS num rows).

Gate (no calc graph proves the structure, so the filer's own debt note does):
the face sum is published only when, on the same accession, one of the
filer's note totals ties within its rounding unit:
  sum(LTD family) = LongTermDebt                                  (carrying)
  sum(all borrowing members) = DebtLongtermAndShorttermCombinedAmount
  sum(all members incl. leases) = DebtAndCapitalLeaseObligations
Otherwise the cell holds (hold_no_note_tie). Lease-only lines are never a
borrowings value by themselves.
usage: DATABASE_URL=... debt_zero_cal.py <debt_eras_all.json> <cohort_bs_rows.jsonl> <out_report.json> [max_companies]
"""
import json
import os
import re
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).parent))
import build_debt_slots as b  # noqa: E402
import face_admission as fa  # noqa: E402
import taxonomy_attrs as ta  # noqa: E402

eras = json.load(open(sys.argv[1]))
limit = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
# ordered BS face rows per boundary filing
boundary = {e["first"] for el in eras.values() for e in el}
tmp = defaultdict(list)
for line in open(sys.argv[2]):
    r = json.loads(line)
    if r["adsh"] in boundary:
        tmp[r["adsh"]].append((r["report"], r["line"], {"tag": r["tag"], "custom": r["custom"], "label": r.get("label") or ""}))
face_rows = {a: [d for _, _, d in sorted(v, key=lambda x: (x[0], x[1]))] for a, v in tmp.items()}

LTD_FAMILY_RX = re.compile(r"LongTermDebt|SeniorNotes|NotesPayable|ConvertibleNotes|ConvertibleDebt|UnsecuredDebt|SecuredDebt|SubordinatedDebt|Debentures")
LEASE_RX = re.compile(r"Lease")
TOTALS = {
    "LongTermDebt": {"LongTermDebtCurrent", "LongTermDebtNoncurrent"},
    "DebtCurrent": {"ShortTermBorrowings", "LongTermDebtCurrent", "CommercialPaper", "LongTermDebtAndCapitalLeaseObligationsCurrent"},
    "LongTermDebtAndCapitalLeaseObligations": {"LongTermDebtAndCapitalLeaseObligationsCurrent", "LongTermDebtNoncurrent", "LongTermDebtCurrent"},
    "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities": {"LongTermDebtAndCapitalLeaseObligations", "LongTermDebtAndCapitalLeaseObligationsCurrent"},
    "DebtAndCapitalLeaseObligations": {"DebtCurrent", "LongTermDebtNoncurrent", "LongTermDebtCurrent", "ShortTermBorrowings"},
}
NOTE_TAGS = ("LongTermDebt", "DebtLongtermAndShorttermCombinedAmount", "DebtAndCapitalLeaseObligations", "LongTermDebtCurrent")


def members_for(era):
    face = face_rows.get(era["first"], [])
    zone, known = fa.liabilities_zone(face)
    ztags = {r["tag"] for r in zone}
    mem, custom, rejected = [], [], []
    for c in era["candidates"]:
        t = c["tag"]
        if not b.DEBT_RX.search(t) or b.EXCLUDE_RX.search(t) or any(rx.search(t) for rx, _ in b.EXCLUDE_CLASSES):
            continue
        if c["custom"]:
            custom.append(t)
            continue
        if fa.ABSTRACT_RX.search(t) or ta.is_abstract(t):
            rejected.append((t, "abstract"))
            continue
        if ta.balance(t) == "debit":
            rejected.append((t, "debit_balance"))
            continue
        if known and t not in ztags:
            rejected.append((t, "outside_liabilities_zone"))
            continue
        mem.append(t)
    # taxonomy totals never summed beside their components
    ms = set(mem)
    for total, parts in TOTALS.items():
        if total in ms and ms & parts:
            mem = [t for t in mem if t != total]
            rejected.append((total, "total_of_members:" + ",".join(sorted(ms & parts))))
    return mem, custom, rejected, known


def rounding_unit(values):
    unit = Decimal(100000000)
    for v in values:
        if v is None or v == 0:
            continue
        while unit > 1 and v % unit != 0:
            unit /= 10
    return unit


conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("set statement_timeout = '60s'")
report = {"per_company": {}, "summary": defaultdict(int), "cells": []}
n = 0
for cik, era_list in sorted(eras.items()):
    if n >= limit:
        break
    n += 1
    recs = []
    for e in era_list:
        mem, custom, rejected, known = members_for(e)
        recs.append({"first": e["first"], "from": e["period_from"], "to": e["period_to"], "members": mem, "custom": custom, "rejected": rejected, "zone_known": known})
    tags = set(NOTE_TAGS)
    for r in recs:
        tags.update(r["members"])
    if not tags:
        continue
    cur.execute(
        """
        select co.tag, p.end_date::text, f.value::numeric, fi.accession_number, fi.period_of_report::text
        from core.fact f
        join core.concept co on co.id = f.concept_id
        join core.period p on p.id = f.period_id
        join core.unit u on u.id = f.unit_id
        join core.company c on c.id = f.company_id
        join core.filing fi on fi.id = f.filing_id
        where c.cik = %s and p.period_type = 'instant' and co.taxonomy = 'us-gaap' and u.unit_name = 'usd'
          and co.tag = any(%s) and fi.form in ('10-K','10-Q','10-K/A','10-Q/A') and p.end_date >= '2015-01-01'
        order by co.tag, p.end_date, f.is_authoritative desc, f.id desc
        """,
        (cik, sorted(tags)),
    )
    by_acc = defaultdict(lambda: defaultdict(dict))
    original = {}
    for tag, e, v, acc, por in cur.fetchall():
        by_acc[e][acc].setdefault(tag, v)
        if por == e:
            original.setdefault(e, acc)
    stats = defaultdict(int)
    for end, accs in sorted(by_acc.items()):
        acc = original.get(end) or max(accs, key=lambda a: len(accs[a]))
        day = accs[acc]
        rec = next((r for r in recs if r["from"][:7] <= end[:7] <= r["to"][:7]), None)
        if rec is None:
            continue
        if not rec["members"] and not rec["custom"]:
            stats["no_debt_line"] += 1
            continue
        if rec["custom"]:
            stats["needs_instance_reader"] += 1
            continue
        missing = [t for t in rec["members"] if t not in day]
        if missing:
            stats["member_value_missing"] += 1
            continue
        vals = {t: day[t] for t in rec["members"]}
        borrow = sum((v for t, v in vals.items() if not LEASE_RX.search(t)), Decimal(0))
        ltd = sum((v for t, v in vals.items() if LTD_FAMILY_RX.search(t) and not LEASE_RX.search(t)), Decimal(0))
        total = sum(vals.values(), Decimal(0))
        unit = rounding_unit(list(vals.values()) + [day.get(t) for t in NOTE_TAGS if t in day])
        tie = None
        if "LongTermDebt" in day and abs(day["LongTermDebt"] - ltd) <= unit:
            tie = "LongTermDebt"
        elif "DebtLongtermAndShorttermCombinedAmount" in day and abs(day["DebtLongtermAndShorttermCombinedAmount"] - borrow) <= unit:
            tie = "DebtLongtermAndShorttermCombinedAmount"
        elif "DebtAndCapitalLeaseObligations" in day and abs(day["DebtAndCapitalLeaseObligations"] - total) <= unit:
            tie = "DebtAndCapitalLeaseObligations"
        if tie:
            stats["note_tie_published"] += 1
        elif not any(t in day for t in NOTE_TAGS[:3]):
            stats["hold_no_note_total"] += 1
        else:
            stats["hold_note_gap"] += 1
        report["cells"].append({"cik": cik, "end": end, "accession": acc, "era_first": rec["first"], "members": rec["members"],
                                "value": str(total) if tie else None, "borrowings": str(borrow) if tie else None, "tie": tie,
                                "note_LongTermDebt": str(day.get("LongTermDebt")), "ltd_face": str(ltd)})
    report["per_company"][cik] = dict(stats)
    for k, v in stats.items():
        report["summary"][k] += v
conn.close()
report["summary"] = dict(report["summary"])
json.dump(report, open(sys.argv[3], "w"), indent=1)
print(json.dumps(report["summary"], indent=1))
print("companies", len(report["per_company"]))
