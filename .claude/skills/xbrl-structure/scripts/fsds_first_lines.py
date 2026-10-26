"""Read-only FSDS check: which filings show no vocabulary tag in the first
income-statement lines. Usage: python3 -I fsds_first_lines.py DIR [--form 10-K]
[--vocab A,B,C] [--top 6] [--show 12]. DIR holds sub.txt and pre.txt."""
import argparse
import collections
import csv
import os

DEFAULT_VOCAB = (
    "RevenueFromContractWithCustomerExcludingAssessedTax,"
    "RevenueFromContractWithCustomerIncludingAssessedTax,Revenues,SalesRevenueNet"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--form", default="10-K")
    ap.add_argument("--vocab", default=DEFAULT_VOCAB)
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--show", type=int, default=12)
    a = ap.parse_args()
    vocab = set(a.vocab.split(","))
    with open(os.path.join(a.dir, "sub.txt"), newline="") as f:
        sub = {r["adsh"]: r for r in csv.DictReader(f, delimiter="\t") if r["form"] == a.form}
    rows = collections.defaultdict(list)
    with open(os.path.join(a.dir, "pre.txt"), newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["adsh"] in sub and r["stmt"] == "IS":
                rows[r["adsh"]].append(r)
    miss, shown = 0, 0
    for adsh, rs in rows.items():
        first = min(int(r["report"]) for r in rs)
        lines = sorted((r for r in rs if int(r["report"]) == first), key=lambda r: int(r["line"]))
        if any(r["tag"] in vocab for r in lines[: a.top]):
            continue
        miss += 1
        if shown < a.show:
            shown += 1
            head = [(r["tag"], r["version"][:8], r["plabel"][:30]) for r in lines[:2]]
            print(adsh, sub[adsh]["name"][:28], "sic", sub[adsh]["sic"], head)
    n = len(rows)
    print(f"filings with IS: {n}; no vocab tag in first {a.top} lines: {miss} ({100 * miss / max(n, 1):.1f}%)")


if __name__ == "__main__":
    main()
