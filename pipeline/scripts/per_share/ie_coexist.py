"""Read-only coexistence check for interest_expense era tags over cohort v1.1 (one connection, chunked).

Per company x period (duration, end >= 2015-01-01, authoritative, non-derived, periodic forms):
values on InterestExpense (IE), InterestExpenseOperating (IEO), InterestExpenseNonoperating (IEN),
InterestExpenseDebt (IED); the stored interest_expense canonical cell. Reports shared-period equality
and cells a period-scoped era rule would fill.
"""

import csv
import json
import subprocess
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _ro import conn  # noqa: E402

TAGS = (
    "InterestExpense",
    "InterestExpenseOperating",
    "InterestExpenseNonoperating",
    "InterestExpenseDebt",
)
FORMS = ["10-K", "10-K/A", "10-Q", "10-Q/A", "10-KT", "10-KT/A"]
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
        "select id from core.company where id = any(%s) and sic_code in ('6021','6022','6029','6035','6036')",
        (ids,),
    )
}
ie_cc = [
    r[0]
    for r in c.execute(
        "select id from analytics.canonical_concept where name in ('interest_expense','interest_expense_resolved')"
    )
]
stats = Counter()
pairs = Counter()
examples: dict[str, list] = {}
for i in range(0, len(ids), 50):
    part = ids[i : i + 50]
    vals: dict[tuple, dict[str, set]] = {}
    for cid, tag, pid, end, months, value, acc in c.execute(
        """select f.company_id, k.tag, f.period_id, p.end_date,
                  round((p.end_date - p.start_date) / 30.4)::int, f.value, fl.accession_number
           from core.fact f join core.concept k on k.id = f.concept_id join core.period p on p.id = f.period_id
           join core.filing fl on fl.id = f.filing_id
           where f.company_id = any(%s) and k.taxonomy = 'us-gaap' and k.tag = any(%s)
             and p.period_type = 'duration' and p.end_date >= '2015-01-01'
             and f.is_authoritative and not f.is_derived and fl.form = any(%s)""",
        (part, list(TAGS), FORMS),
    ):
        vals.setdefault((cid, pid, end, months), {}).setdefault(tag, set()).add(
            Decimal(value)
        )
    stored = {
        (r[0], r[1]): r[2]
        for r in c.execute(
            "select company_id, period_id, value from analytics.canonical_fact where company_id = any(%s) and canonical_concept_id = any(%s)",
            (part, ie_cc),
        )
    }
    for (cid, pid, end, months), by in vals.items():
        kind = "bank" if cid in bank else "nonbank"
        have = stored.get((cid, pid))
        for new in ("InterestExpenseOperating", "InterestExpenseNonoperating"):
            if new not in by:
                continue
            stats[f"{kind}|{new}|periods"] += 1
            if have is None:
                stats[f"{kind}|{new}|no_stored_interest_expense"] += 1
                if "InterestExpense" not in by and "InterestExpenseDebt" not in by:
                    stats[f"{kind}|{new}|fillable_only_source"] += 1
                    examples.setdefault(f"{kind}|{new}|fillable", []).append(
                        (cid, str(end), months, str(min(by[new])))
                    )
            for old in ("InterestExpense", "InterestExpenseDebt"):
                if old in by:
                    eq = bool(by[old] & by[new])
                    pairs[f"{kind}|{new}~{old}|{'equal' if eq else 'differ'}"] += 1
                    if not eq:
                        examples.setdefault(f"{kind}|{new}~{old}|differ", []).append(
                            (
                                cid,
                                str(end),
                                months,
                                [str(v) for v in by[old]],
                                [str(v) for v in by[new]],
                            )
                        )
    print(f"{min(i + 50, len(ids))}/{len(ids)}", flush=True)
out = {
    "stats": dict(sorted(stats.items())),
    "pairs": dict(sorted(pairs.items())),
    "examples": {k: v[:25] for k, v in examples.items()},
    "example_counts": {k: len(v) for k, v in examples.items()},
}
open(sys.argv[2], "w").write(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("stats", "pairs", "example_counts")}, indent=1))
