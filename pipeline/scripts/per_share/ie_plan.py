"""Read-only dry-run plan for an interest_expense era rule over cohort v1.1 (one connection, chunked).

Cells: company x 3- or 12-month duration ending >= 2015-01-01 with NO stored interest_expense canonical value, where the
2024+ taxonomy tag carries an authoritative, non-derived 10-K/10-Q fact: InterestExpenseNonoperating (IEN, non-banks) or
InterestExpenseOperating (IEO, banks SIC 6021/6022/6029/6035/6036). Outcome per cell:
  fill               value > 0 and the company passes the perimeter check
  hold_sign          value <= 0 (a net figure stored credit-positive, or income: the tag card's ANDE/BBW trap)
  hold_perimeter     in some shared period the new tag and InterestExpense differ by more than rounding (component or
                     different perimeter: e.g. company 646 IEO ~60% of InterestExpense)
  hold_nonbank_ieo   IEO at a non-bank: operating interest only, a component unless proven the total (HTZ is total)
  hold_no_overlap    no shared period with InterestExpense to prove the perimeter (the company switched cleanly)
Rounding: |a - b| <= max(0.5% of the larger, one unit of the coarser printed scale).
"""

import csv
import json
import subprocess
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _ro import conn  # noqa: E402

FORMS = ["10-K", "10-K/A", "10-Q", "10-Q/A", "10-KT", "10-KT/A"]
TAGS = ("InterestExpense", "InterestExpenseOperating", "InterestExpenseNonoperating")
BANK_SIC = ("6021", "6022", "6029", "6035", "6036")


def unit(v: Decimal) -> Decimal:
    n, u = abs(v), Decimal(1)
    while n and u < Decimal(10) ** 6 and n % (u * 10) == 0:
        u *= 10
    return u


def same(a: Decimal, b: Decimal) -> bool:
    return abs(a - b) <= max(
        Decimal("0.005") * max(abs(a), abs(b)), max(unit(a), unit(b))
    )


txt = subprocess.run(
    [
        "git",
        "-C",
        "/Users/vikash/scrooner",
        "show",
        "origin/main:data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv",
    ],
    capture_output=True,
    text=True,
    check=True,
).stdout
ids = sorted(int(r["company_id"]) for r in csv.DictReader(txt.splitlines()))
c = conn()
c.execute("set statement_timeout = '120s'")
bank = {
    r[0]
    for r in c.execute(
        "select id from core.company where id = any(%s) and sic_code = any(%s)",
        (ids, list(BANK_SIC)),
    )
}
cik = dict(
    c.execute("select id, cik from core.company where id = any(%s)", (ids,)).fetchall()
)
ie_cc = [
    r[0]
    for r in c.execute(
        "select id from analytics.canonical_concept where name in ('interest_expense','interest_expense_resolved')"
    )
]
cells, stats = [], Counter()
for i in range(0, len(ids), 50):
    part = ids[i : i + 50]
    facts = defaultdict(
        lambda: defaultdict(list)
    )  # (cid, pid) -> tag -> [(value, accession)]
    meta = {}
    for cid, tag, pid, start, end, months, value, acc in c.execute(
        """select f.company_id, k.tag, f.period_id, p.start_date, p.end_date,
                  round((p.end_date - p.start_date) / 30.4)::int, f.value, fl.accession_number
           from core.fact f join core.concept k on k.id = f.concept_id join core.period p on p.id = f.period_id
           join core.filing fl on fl.id = f.filing_id
           where f.company_id = any(%s) and k.taxonomy = 'us-gaap' and k.tag = any(%s)
             and p.period_type = 'duration' and p.end_date >= '2015-01-01'
             and f.is_authoritative and not f.is_derived and fl.form = any(%s)""",
        (part, list(TAGS), FORMS),
    ):
        facts[(cid, pid)][tag].append((Decimal(value), acc))
        meta[(cid, pid)] = (str(start), str(end), months)
    stored = {
        (r[0], r[1])
        for r in c.execute(
            "select company_id, period_id from analytics.canonical_fact where company_id = any(%s) and canonical_concept_id = any(%s)",
            (part, ie_cc),
        )
    }
    # perimeter verdict per company and new tag: every shared period must agree within rounding
    verdict: dict[tuple[int, str], str] = {}
    for (cid, pid), by in facts.items():
        for new in ("InterestExpenseOperating", "InterestExpenseNonoperating"):
            if new in by and "InterestExpense" in by:
                ok = any(
                    same(a, b) for a, _ in by[new] for b, _ in by["InterestExpense"]
                )
                key = (cid, new)
                verdict[key] = (
                    "differ" if (not ok or verdict.get(key) == "differ") else "agree"
                )
    for (cid, pid), by in facts.items():
        start, end, months = meta[(cid, pid)]
        if months not in (3, 12) or (cid, pid) in stored or "InterestExpense" in by:
            continue
        new = (
            "InterestExpenseOperating" if cid in bank else "InterestExpenseNonoperating"
        )
        if new not in by:
            if cid not in bank and "InterestExpenseOperating" in by:
                outcome, new = "hold_nonbank_ieo", "InterestExpenseOperating"
            else:
                continue
        else:
            vals = {v for v, _ in by[new]}
            v = max(vals)
            if len(vals) > 1 and not all(same(a, v) for a in vals):
                outcome = "hold_copies_disagree"
            elif v <= 0:
                outcome = "hold_sign"
            elif verdict.get((cid, new)) == "differ":
                outcome = "hold_perimeter"
            elif verdict.get((cid, new)) is None:
                outcome = "hold_no_overlap"
            else:
                outcome = "fill"
        v, acc = max(by[new])
        stats[outcome] += 1
        cells.append(
            {
                "company_id": cid,
                "cik": cik[cid],
                "bank": cid in bank,
                "period_id": pid,
                "start": start,
                "end": end,
                "months": months,
                "tag": new,
                "value": str(v),
                "accession": acc,
                "outcome": outcome,
            }
        )
    print(f"{min(i + 50, len(ids))}/{len(ids)}", flush=True)
out = sys.argv[2]
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(cells[0]))
    w.writeheader()
    w.writerows(cells)
by_tag = Counter(
    (x["outcome"], x["tag"], "bank" if x["bank"] else "nonbank") for x in cells
)
print(
    json.dumps(
        {
            "cells": len(cells),
            "companies": len({x["company_id"] for x in cells}),
            "by_outcome": dict(stats),
            "by_outcome_tag": {"|".join(k): n for k, n in sorted(by_tag.items())},
            "fill_companies": len(
                {x["company_id"] for x in cells if x["outcome"] == "fill"}
            ),
        },
        indent=1,
    )
)
