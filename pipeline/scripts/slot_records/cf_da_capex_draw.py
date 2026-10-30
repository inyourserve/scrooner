"""Seeded, stratified Verifier draw over a cf_da_capex_variants.py cells file.
At most one cell per company per stratum, so a draw cannot be dominated by one filer.
usage: cf_da_capex_draw.py <cells.jsonl.gz> <seed> <out.json>
"""
import gzip
import json
import random
import sys
from collections import defaultdict
from decimal import Decimal


def runit(v, cap=Decimal(1000000)):
    unit = cap
    while unit > 1 and v % unit != 0:
        unit /= 10
    return unit


def differs(a, b):
    """beyond the coarser of the two rounding units (production often carries a rounder copy)"""
    return abs(a - b) > max(runit(a) if a else 1, runit(b) if b else 1)

N = {"da_published_prod_differs": 20, "da_published_prod_blank": 5, "da_2a_tie": 8, "da_combined_other": 5,
     "da_held_unresolved": 6, "capex_published_prod_differs": 20, "capex_leased": 5, "capex_software": 6,
     "capex_discontinued": 4, "capex_unresolved_both": 5}
strata = defaultdict(list)
for line in gzip.open(sys.argv[1], "rt"):
    c = json.loads(line)
    p = Decimal(c["prod_value"]) if c.get("prod_value") else None
    if c["family"] == "d_and_a":
        if c["reason"] is None:
            v = Decimal(c["value"])
            if any(x["nature"] == "other_amort" for x in c["lines"]):
                strata["da_2a_tie"].append(c)
            elif p is None:
                strata["da_published_prod_blank"].append(c)
            elif differs(p, v):
                strata["da_published_prod_differs"].append(c)
        elif c["reason"] == "da_combined_with_other_items":
            strata["da_combined_other"].append(c)
        elif c["reason"] == "perimeter_line_unresolved":
            strata["da_held_unresolved"].append(c)
    else:
        if c["net_sibling"]:
            strata["capex_unresolved_both"].append(c)
        elif c["cases"]:
            strata["capex_" + c["cases"][0]].append(c)
        elif c["interim"] is not None and p is not None and differs(p, Decimal(c["interim"])):
            strata["capex_published_prod_differs"].append(c)
rng = random.Random(int(sys.argv[2]))
draw = {}
for k, n in N.items():
    pool = strata[k][:]
    rng.shuffle(pool)
    seen, pick = set(), []
    for c in pool:
        if c["ticker"] in seen:
            continue
        seen.add(c["ticker"])
        pick.append({x: c.get(x) for x in ("ticker", "cik", "end", "qtrs", "accession", "form", "family", "value", "reason",
                                           "variant_narrow", "variant_ruling", "interim", "interim_reason", "is_intangible_amort",
                                           "prod_value", "lines")})
        if len(pick) == n:
            break
    draw[k] = {"population": len(strata[k]), "drawn": pick}
json.dump({"seed": int(sys.argv[2]), "source": sys.argv[1], "strata": draw}, open(sys.argv[3], "w"), indent=1, default=str)
print({k: (v["population"], len(v["drawn"])) for k, v in draw.items()})
