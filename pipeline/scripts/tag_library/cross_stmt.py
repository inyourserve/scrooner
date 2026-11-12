"""One statement per concept per period: where two 'concept' rows of one (company, concept) on different statements
cover the same period, the higher-priority statement serves and the other row is cut to the periods outside it (the cut
part becomes an excluded alternate row). 0122 checks overlap per (company, stmt, concept) only; the mapper sees both and
holds the cell as conflicting_values_in_filing (META sbc: IS AllocatedShareBasedCompensationExpense vs CF
ShareBasedCompensation; NVDA DPS: IS Declared vs EQ CashPaid on the wrong context; Engineering 2026-11-12).
Usage: cross_stmt.py <tag_map.csv> <out.csv>"""
import collections
import csv
import datetime
import sys

PRIORITY = {"sbc": ("CF", "IS", "EQ"),  # the cash-flow add-back is the sbc line
            "dividends_per_share_resolved": ("IS", "EQ", "CF"),  # the per-share line on the face first
            "cash_and_equivalents_resolved": ("BS", "CF")}


def day(d, n):
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()


def apply(rows):
    groups = collections.defaultdict(list)
    for i, r in enumerate(rows):
        if r["decision"] == "concept" and r["canonical_concept"] in PRIORITY:
            groups[(r["company_id"], r["canonical_concept"])].append(i)
    drop, new, cut = set(), [], 0
    for (c, con), idx in groups.items():
        order = PRIORITY[con]
        rank = lambda r: order.index(r["stmt"]) if r["stmt"] in order else len(order)
        for i in idx:
            r = rows[i]
            higher = sorted((rows[j]["era_from"], rows[j]["era_to"]) for j in idx if rank(rows[j]) < rank(r)
                            and not (rows[j]["era_to"] < r["era_from"] or r["era_to"] < rows[j]["era_from"]))
            if not higher:
                continue
            drop.add(i)
            cut += 1
            cur = r["era_from"]
            for a, b in higher:
                if a > cur:
                    new.append({**r, "era_from": cur, "era_to": min(day(a, -1), r["era_to"])})
                lo, hi = max(a, cur), min(b, r["era_to"])
                if lo <= hi:
                    new.append({**r, "decision": "excluded", "canonical_concept": "", "reason_class": "alternate_tag_overlapping", "era_from": lo,
                                "era_to": hi, "decided_by": "cross_stmt", "value_source": "",
                                "reason": f"same concept {con} on a higher-priority statement for these periods ({' > '.join(order)})"})
                cur = max(cur, day(b, 1))
            if cur <= r["era_to"]:
                new.append({**r, "era_from": cur, "era_to": r["era_to"]})
    return [r for i, r in enumerate(rows) if i not in drop] + new, cut


if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    rows = list(csv.DictReader(open(src)))
    out, cut = apply(rows)
    with open(dst, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(out)
    print("rows", len(rows), "->", len(out), "| cross-statement rows cut", cut)
