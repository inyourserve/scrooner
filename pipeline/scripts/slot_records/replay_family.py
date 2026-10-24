"""Replay D&A / capex slot records against production canonical values.

Duration facts: periods match on exact (start_date, end_date). Two slot
variants per family, mirroring the standardization cards:
  d_and_a: narrow = asset_da members; broad = narrow + other_amort
           (financing_amort, investment_amort and IS sub-lines excluded)
  capex:   ppe_only = ppe_capex (+net_capex); plus_software = + software/intangible
Verdicts vs production (<family>_resolved): agrees_<variant>, DISAGREES,
prod_blank_slot_has_value (the holds-equivalent), not_computable.
Read-only, one connection. usage:
  DATABASE_URL=... replay_family.py <family> <records.jsonl> <out.json>
"""
import json
import os
import sys
from collections import defaultdict
from decimal import Decimal

import psycopg

family = sys.argv[1]
PROD_CONCEPT = {"d_and_a": "depreciation_and_amortization_resolved", "capex": "capex_resolved"}[family]
NARROW = {"d_and_a": {"asset_da"}, "capex": {"ppe_capex", "net_capex"}}[family]
BROAD = {"d_and_a": {"asset_da", "other_amort"},
         "capex": {"ppe_capex", "net_capex", "software_capex", "intangible_capex"}}[family]

records = defaultdict(list)
for line in open(sys.argv[2]):
    r = json.loads(line)
    records[r["cik"]].append(r)

conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
report = {"cells": [], "summary": defaultdict(int), "per_company": defaultdict(lambda: defaultdict(int))}
for cik in sorted(records):
    ticker = records[cik][0]["company"]
    tags = sorted({m["tag"] for rec in records[cik] for m in rec["members"] if m["stmt"] == "CF"})
    cur.execute(
        """
        select p.start_date::text, p.end_date::text, cf.value::numeric
        from analytics.canonical_fact cf
        join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
        join core.period p on p.id = cf.period_id
        join core.company c on c.id = cf.company_id
        where c.cik = %s and cc.name = %s and p.end_date >= '2015-01-01'
        """,
        (cik, PROD_CONCEPT),
    )
    prod = {(s, e): v for s, e, v in cur.fetchall()}
    cur.execute(
        """
        select distinct on (co.tag, p.start_date, p.end_date)
               co.tag, p.start_date::text, p.end_date::text, f.value::numeric, f.is_authoritative
        from core.fact f
        join core.concept co on co.id = f.concept_id
        join core.period p on p.id = f.period_id
        join core.unit u on u.id = f.unit_id
        join core.company c on c.id = f.company_id
        where c.cik = %s and p.period_type = 'duration' and co.taxonomy = 'us-gaap'
          and u.unit_name = 'usd' and co.tag = any(%s) and p.end_date >= '2015-01-01'
        order by co.tag, p.start_date, p.end_date, f.is_authoritative desc, f.id desc
        """,
        (cik, tags),
    )
    facts = defaultdict(dict)
    for tag, s, e, v, auth in cur.fetchall():
        facts[(s, e)][tag] = (v, auth)
    # production blanks: periods where member facts exist but prod has no value
    all_periods = set(prod) | set(facts)
    for (s, e) in sorted(all_periods):
        ym = e[:7]
        rec = next(
            (r for r in records[cik] if r["period_from"][:7] <= ym <= r["period_to"][:7]), None
        )
        if rec is None:
            continue
        day = facts.get((s, e), {})
        cf_members = [m for m in rec["members"] if m["stmt"] == "CF"]
        missing_custom = [m["tag"] for m in cf_members if m.get("custom") and m["tag"] not in day]

        def total(classes):
            tot, missing = Decimal(0), []
            for m in cf_members:
                if m["class"] not in classes:
                    continue
                if m["tag"] in day:
                    tot += day[m["tag"]][0]
                else:
                    missing.append(m["tag"])
            return tot, missing

        narrow, miss_n = total(NARROW)
        broad, miss_b = total(BROAD)
        pv = prod.get((s, e))
        if pv is None:
            if narrow > 0 and not miss_n:
                verdict = "prod_blank_slot_has_value"
            else:
                continue  # neither side has a complete value
        elif abs(narrow - pv) <= 1 and not miss_n:
            verdict = "agrees_narrow"
        elif abs(broad - pv) <= 1 and not miss_b:
            verdict = "agrees_broad"
        elif missing_custom:
            verdict = "not_computable_custom_member"
        elif miss_n:
            verdict = "not_computable_missing_member"
        else:
            verdict = "DISAGREES_with_prod"
        report["summary"][verdict] += 1
        report["per_company"][ticker][verdict] += 1
        if verdict in ("DISAGREES_with_prod", "prod_blank_slot_has_value"):
            report["cells"].append(
                {"ticker": ticker, "start": s, "end": e, "verdict": verdict,
                 "slot_narrow": str(narrow), "slot_broad": str(broad),
                 "prod": str(pv) if pv is not None else None,
                 "missing": miss_n, "missing_custom": missing_custom}
            )
conn.close()
report["summary"] = dict(report["summary"])
report["per_company"] = {k: dict(v) for k, v in report["per_company"].items()}
json.dump(report, open(sys.argv[3], "w"), indent=1)
print(family, json.dumps(report["summary"], indent=1))
