"""Replay D&A / capex slot records; the verdict comes from the FILING, never
from production (standing rule: production is the thing being replaced).

Duration facts match on exact (start_date, end_date); inputs come from ONE
accession per period (the original filing whose period_of_report is the end
date, else the accession carrying the most of the needed tags). Gate: the
filer's own cash-flow SECTION arithmetic on that accession
(sum of signed section roots = section total, within the filer's rounding
unit). A member value is published only when the section ties and every
member is present (custom member missing -> needs_instance_reader).

Two slot variants per family, mirroring the standardization cards:
  d_and_a: narrow = asset_da members; broad = narrow + other_amort
           (financing_amort, investment_amort and IS sub-lines excluded)
  capex:   ppe_only = ppe_capex (+net_capex); plus_software = + software/intangible
Production's value is carried as information (prod_value, differs_from_prod)
and never decides a verdict. Read-only, one connection.
usage: DATABASE_URL=... replay_family.py <family> <records.jsonl> <out.json>
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


def rounding_unit(values):
    unit = Decimal(1000000)
    for v in values:
        if v is None or v == 0:
            continue
        while unit > 1 and v % unit != 0:
            unit /= 10
    return unit


conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("set statement_timeout = '60s'")
report = {"cells": [], "summary": defaultdict(int), "per_company": defaultdict(lambda: defaultdict(int))}
PUBLISHABLE = {"section_ties", "section_ties_narrow_only"}
for cik in sorted(records):
    ticker = records[cik][0]["company"]
    tags = set()
    for rec in records[cik]:
        tags.update(m["tag"] for m in rec["members"] if m["stmt"] == "CF")
        if rec.get("section"):
            tags.add(rec["section"]["total"])
            tags.update(r["tag"] for r in rec["section"]["roots"])
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
        select co.tag, p.start_date::text, p.end_date::text, f.value::numeric, f.is_authoritative,
               fi.accession_number, fi.period_of_report::text
        from core.fact f
        join core.concept co on co.id = f.concept_id
        join core.period p on p.id = f.period_id
        join core.unit u on u.id = f.unit_id
        join core.company c on c.id = f.company_id
        join core.filing fi on fi.id = f.filing_id
        where c.cik = %s and p.period_type = 'duration' and co.taxonomy = 'us-gaap'
          and u.unit_name = 'usd' and co.tag = any(%s) and p.end_date >= '2015-01-01'
          and fi.form in ('10-K','10-Q','10-K/A','10-Q/A')
        order by co.tag, p.start_date, p.end_date, f.is_authoritative desc, f.id desc
        """,
        (cik, sorted(tags)),
    )
    by_acc = defaultdict(lambda: defaultdict(dict))
    original = {}
    for tag, s, e, v, auth, acc, por in cur.fetchall():
        by_acc[(s, e)][acc].setdefault(tag, v)
        if por == e:
            original.setdefault((s, e), acc)
    facts = {}
    for key, accs in by_acc.items():
        acc = original.get(key) or max(accs, key=lambda a: len(accs[a]))
        facts[key] = (acc, accs[acc])
    for (s, e) in sorted(set(prod) | set(facts)):
        ym = e[:7]
        rec = next((r for r in records[cik] if r["period_from"][:7] <= ym <= r["period_to"][:7]), None)
        if rec is None:
            continue
        acc, day = facts.get((s, e), (None, {}))
        cf_members = [m for m in rec["members"] if m["stmt"] == "CF"]
        if not cf_members:
            continue
        missing_custom = [m["tag"] for m in cf_members if m.get("custom") and m["tag"] not in day]
        missing_std = [m["tag"] for m in cf_members if not m.get("custom") and m["tag"] not in day]

        def total(classes):
            return sum((day[m["tag"]] for m in cf_members if m["class"] in classes and m["tag"] in day), Decimal(0))

        narrow, broad = total(NARROW), total(BROAD)
        # THE GATE: the filer's own section arithmetic on this accession
        sec = rec.get("section")
        tie = None
        if sec and sec["total"] in day:
            vals = [(day.get(r["tag"]), Decimal(r["weight"])) for r in sec["roots"]]
            present = [(v, w) for v, w in vals if v is not None]
            if len(present) == len(vals):
                gap = day[sec["total"]] - sum(v * w for v, w in present)
                tie = abs(gap) <= rounding_unit([v for v, _ in present] + [day[sec["total"]]])
            else:
                tie = None  # a root value is missing: cannot prove the section
        verdict = None
        if not day:
            verdict = "no_facts_this_period"
        elif missing_custom:
            verdict = "needs_instance_reader"
        elif missing_std and not any(m["class"] in NARROW for m in cf_members if m["tag"] in day):
            verdict = "not_computable_missing_member"
        elif sec is None:
            verdict = "hold_no_section_cal"
        elif sec["total"] not in day:
            verdict = "hold_section_total_missing"
        elif tie is None:
            verdict = "hold_section_root_missing"
        elif not tie:
            verdict = "hold_section_gap"
        elif missing_std:
            verdict = "section_ties_narrow_only"  # broad variant incomplete
        else:
            verdict = "section_ties"
        pv = prod.get((s, e))
        publishable = verdict in PUBLISHABLE
        report["summary"][verdict] += 1
        report["per_company"][ticker][verdict] += 1
        if publishable and pv is not None:
            k = "prod_agrees" if (abs(narrow - pv) <= 1 or abs(broad - pv) <= 1) else "prod_differs"
            report["summary"][k] += 1
        elif publishable and pv is None:
            report["summary"]["prod_blank_slot_has_value"] += 1
        report["cells"].append(
            {"ticker": ticker, "start": s, "end": e, "accession": acc, "verdict": verdict,
             "slot_narrow": str(narrow) if publishable else None,
             "slot_broad": str(broad) if publishable and not missing_std else None,
             "prod_value": str(pv) if pv is not None else None,
             "differs_from_prod": (pv is not None and publishable and abs(narrow - pv) > 1 and abs(broad - pv) > 1),
             "missing": missing_std, "missing_custom": missing_custom}
        )
conn.close()
report["summary"] = dict(report["summary"])
report["per_company"] = {k: dict(v) for k, v in report["per_company"].items()}
json.dump(report, open(sys.argv[3], "w"), indent=1)
print(family, json.dumps(report["summary"], indent=1))
