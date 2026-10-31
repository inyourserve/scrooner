"""Cash and cash equivalents per cohort balance-sheet cell, from the balance-sheet FACE (FSN pre
rows + same-accession instant values; zero SEC requests). Dry run: writes a cells file and a
summary, nothing to the database. Production's value is information only.

Cells: one per (company, instant) where the filer tagged its balance-sheet total (Assets or
LiabilitiesAndStockholdersEquity) for that instant in that filing (face-column rule); the
original 10-K/10-Q whose period is the instant wins, comparatives only when no original.
Members: the printed cash-type lines of the assets section (before the current-assets total,
else before total assets), each classed by its face label/element:
  pure            "Cash and cash equivalents" / "Cash" / "Cash and equivalents" (one line)
  restricted      a separate restricted-cash line (excluded from cash and equivalents)
  with_restricted one line that includes restricted cash        -> hold
  with_investments one line that includes investments/securities -> hold
  bank            cash and due from banks / interest-bearing deposits / fed funds sold
Outcome: one pure line -> its value. Bank layouts publish the sum of the bank components only when
it equals the filer's own cash-flow ending cash and cash equivalents for that instant (the filer's
definition); otherwise hold. Anchor check everywhere: where the cash-flow statement ends on the
pure cash element (CashAndCashEquivalentsAtCarryingValue, pre-restricted-cash presentation), the
published value must equal it, else hold.
usage: bs_cash_variants.py <bs_face.jsonl.gz> <prod_cash.jsonl.gz> <out_dir>
"""
import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

face_path, prod_path, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
out_dir.mkdir(parents=True, exist_ok=True)
BS_TOTAL = ("Assets", "LiabilitiesAndStockholdersEquity", "LiabilitiesAndPartnersCapital")
PURE_TAG = re.compile(r"^(CashAndCashEquivalentsAtCarryingValue|Cash|CashEquivalentsAtCarryingValue|CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations)$")
BANK = re.compile(r"due from banks|interest.bearing (deposits|balances)|deposits (with|in|at) (other )?(banks|federal reserve)|federal funds sold|"
                  r"cash and balances (due|with)|reverse repurchase|securities purchased under", re.I)
CASH_WORD = re.compile(r"\bcash\b|due from banks|interest.bearing deposits|federal funds sold", re.I)


def dec(x):
    try:
        return Decimal(x)
    except Exception:
        return None


def runit(values, cap=Decimal(1000000)):
    unit = cap
    for v in values:
        if v is None or v == 0:
            continue
        while unit > 1 and v % unit != 0:
            unit /= 10
    return unit


def nature(tag, label):
    if BANK.search(label) or tag in ("CashAndDueFromBanks", "InterestBearingDepositsInBanks", "FederalFundsSold",
                                     "FederalFundsSoldAndSecuritiesPurchasedUnderAgreementsToResell"):
        return "bank"
    if re.search(r"restricted", label + tag, re.I):
        if re.search(r"^\s*restricted|^RestrictedCash", label + "|" + tag, re.I) and not re.search(r"cash and cash equivalents,? and restricted|equivalents and restricted", label, re.I):
            return "restricted"
        return "with_restricted"
    if re.search(r"investment|securities|marketable|short.term", label, re.I):
        return "with_investments"
    if PURE_TAG.match(tag) or re.match(r"\s*cash(,| and)? ?(cash )?(and )?(equivalents)?\s*(\(note.*\))?\s*$", label, re.I) \
            or re.match(r"\s*cash and cash equivalents\b", label, re.I):
        return "pure"
    return "other_cash"


def month_end(d):
    """FSN ddate is the instant rounded to the NEAREST month end; round production's true date the same way."""
    from datetime import date, timedelta
    y, m, dd = int(d[:4]), int(d[5:7]), int(d[8:10])
    if dd < 15:
        return (date(y, m, 1) - timedelta(days=1)).isoformat()
    return (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)).isoformat()


prod, prod_n = {}, Counter()
for line in gzip.open(prod_path, "rt"):
    cik, name, s, e, v = json.loads(line)
    prod[(cik, month_end(e))] = Decimal(v)
    prod_n[(cik, month_end(e))] += 1


best = {}
for line in gzip.open(face_path, "rt"):
    f = json.loads(line)
    for col, vals in f["values"].items():
        ddate, q = col.split("|")
        if q != "0" or ddate < "20141231" or not any(t in vals for t in BS_TOTAL):
            continue
        rank = (ddate == f["period"], not f["form"].endswith("/A"), f["filed"])
        key = (f["cik"], ddate)
        if key not in best or rank > best[key][0]:
            best[key] = (rank, f["adsh"])
wanted = defaultdict(list)
for key, (_r, adsh) in best.items():
    wanted[adsh].append(key)
del best

cells, summ, per_company = [], Counter(), defaultdict(Counter)
for line in gzip.open(face_path, "rt"):
    f = json.loads(line)
    for (cik, ddate) in wanted.get(f["adsh"], ()):
        vals = f["values"][f"{ddate}|0"]
        bs = [r for r in f["face"] if r["stmt"] == "BS"]
        reps = Counter(r["report"] for r in bs if r["tag"] in BS_TOTAL)
        if not reps:
            continue
        rows = [r for r in bs if r["report"] == reps.most_common(1)[0][0]]
        stop = next((i for i, r in enumerate(rows) if r["tag"] == "AssetsCurrent"), None)
        if stop is None:
            stop = next((i for i, r in enumerate(rows) if r["tag"] == "Assets"), len(rows))
        members, seen = [], set()
        for r in rows[:stop]:
            t, lab = r["tag"], r["plabel"]
            if t in seen or t not in vals or not (CASH_WORD.search(lab) or PURE_TAG.match(t) or "Cash" in t):
                continue
            if re.search(r"Abstract$", t) or re.search(r"pledged|segregated|held in trust|customer", lab, re.I):
                continue
            v = dec(vals[t])
            if v is None:
                continue
            seen.add(t)
            members.append({"tag": t, "label": lab, "nature": nature(t, lab), "value": str(v)})
        # the filer's own cash definition: the cash-flow statement's ending balance, same instant
        cf_end = None
        cf_tags = {r["tag"] for r in f["face"] if r["stmt"] == "CF"}
        for t in ("CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                  "CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations"):
            if t in cf_tags and t in vals:
                cf_end = (t, dec(vals[t]))
                break
        pure = [m for m in members if m["nature"] == "pure"]
        bank = [m for m in members if m["nature"] == "bank"]
        mixed = [m for m in members if m["nature"] in ("with_restricted", "with_investments", "other_cash")]
        value, reason = None, None
        if bank:
            sm = sum((Decimal(m["value"]) for m in bank + pure), Decimal(0))
            if cf_end and cf_end[0] == "CashAndCashEquivalentsAtCarryingValue" and abs(sm - cf_end[1]) <= runit([sm, cf_end[1]]):
                value = sm  # the filer's own cash-flow cash definition ties to the bank components
            else:
                reason = "bank_cash_definition"
        elif mixed and not pure:
            reason = {"with_restricted": "cash_includes_restricted", "with_investments": "cash_combined_with_investments"}.get(
                mixed[0]["nature"], "cash_line_unclear")
        elif len(pure) == 1:
            value = Decimal(pure[0]["value"])
        elif len(pure) > 1:
            reason = "two_cash_lines"
        else:
            reason = "no_cash_line"
        if value is not None and cf_end and cf_end[0] == "CashAndCashEquivalentsAtCarryingValue" \
                and abs(value - cf_end[1]) > runit([value, cf_end[1]]):
            value, reason = None, "cash_flow_anchor_differs"  # the BS line disagrees with the filer's own CF cash
        end = f"{ddate[:4]}-{ddate[4:6]}-{ddate[6:]}"
        pv = prod.get((cik, end)) if prod_n[(cik, end)] == 1 else None  # two production instants in one month: no comparison
        c = {"family": "cash", "ticker": f["ticker"], "cik": cik, "end": end, "accession": f["adsh"], "form": f["form"],
             "members": members, "cf_ending": [cf_end[0], str(cf_end[1])] if cf_end else None,
             "value": str(value) if value is not None else None, "reason": reason, "prod_value": str(pv) if pv is not None else None}
        cells.append(c)
        k = reason or ("published_bank_tie" if bank else "published")
        summ[f"cash_{k}"] += 1
        per_company[f["ticker"]][k] += 1
        if value is not None:
            if pv is None:
                summ["cash_published_prod_blank"] += 1
            else:
                summ["cash_published_prod_agrees" if abs(pv - value) <= max(runit([value]), runit([pv])) else "cash_published_prod_differs"] += 1
        elif pv is not None:
            summ["cash_hidden_prod_shows_value"] += 1
with gzip.open(out_dir / "cells.jsonl.gz", "wt") as fo:
    for c in cells:
        fo.write(json.dumps(c) + "\n")
json.dump({"summary": dict(sorted(summ.items())), "companies": {k: dict(v) for k, v in sorted(per_company.items())}},
          open(out_dir / "summary.json", "w"), indent=1)
print(json.dumps(dict(sorted(summ.items())), indent=1))
