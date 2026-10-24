"""Replay BS-totals records: anchors + the accounting identity as cross-check.

For each company: compute total_liabilities per its record rule (printed total
or face-sum of skeleton members), equity_parent, nci, mezzanine, at every
instant; identity check |Assets - (L + mezz + equity_incl_nci)| <= tolerance.
Rules inherited: periodic-only facts, authoritative-first, missing member =
hard stop (custom -> needs_instance_reader), no production-derived verdicts.
usage: DATABASE_URL=... bs_replay.py <bs_records.jsonl> <anchors.json> <out.json>
"""
import json
import os
import sys
from collections import defaultdict
from decimal import Decimal

import psycopg

records = defaultdict(list)
for line in open(sys.argv[1]):
    r = json.loads(line)
    records[r["cik"]].append(r)
anchors = json.loads(open(sys.argv[2]).read())["anchors"]

conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
report = {"anchor_results": [], "identity": defaultdict(int), "per_company": {}}

EXTRA = ["Assets", "Liabilities", "StockholdersEquity", "MinorityInterest",
         "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
         "PartnersCapital", "TemporaryEquityCarryingAmountAttributableToParent",
         "RedeemableNoncontrollingInterestEquityCarryingAmount", "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests"]


def fetch(cik, tags):
    cur.execute(
        """
        select distinct on (co.tag, p.end_date) co.tag, p.end_date::text, f.value::numeric, f.is_authoritative
        from core.fact f
        join core.concept co on co.id=f.concept_id
        join core.period p on p.id=f.period_id
        join core.unit u on u.id=f.unit_id
        join core.company c on c.id=f.company_id
        join core.filing fi on fi.id=f.filing_id
        where c.cik=%s and p.period_type='instant' and co.taxonomy='us-gaap'
          and u.unit_name='usd' and co.tag = any(%s)
          and fi.form in ('10-K','10-Q','10-K/A','10-Q/A')
        order by co.tag, p.end_date, f.is_authoritative desc, f.id desc
        """,
        (cik, list(tags)),
    )
    facts = defaultdict(dict)
    for tag, e, v, auth in cur.fetchall():
        facts[e][tag] = v
    return facts


def covering(cik, end):
    ym = end[:7]
    return next((r for r in records[cik] if r["period_from"][:7] <= ym <= r["period_to"][:7]), None)


def liab_value(rec, day):
    members = rec["total_liabilities_members"]
    if rec["total_liabilities_rule"] == "printed_total":
        v = day.get("Liabilities")
        return (v, [], []) if v is not None else (None, ["Liabilities"], [])
    tot, miss, miss_custom = Decimal(0), [], []
    for m in members:
        v = day.get(m["tag"])
        if v is not None:
            tot += v
        elif m.get("custom"):
            miss_custom.append(m["tag"])
        else:
            miss.append(m["tag"])
    return tot, miss, miss_custom


for cik in sorted(records):
    ticker = records[cik][0]["company"]
    tags = set(EXTRA)
    for r in records[cik]:
        tags.update(m["tag"] for m in r["total_liabilities_members"])
        tags.update(m["tag"] for m in r["mezzanine_face"])
        if r["equity_parent_tag"]:
            tags.add(r["equity_parent_tag"])
    facts = fetch(cik, tags)
    stats = defaultdict(int)
    for end, day in sorted(facts.items()):
        if end < "2015-01-01":
            continue
        rec = covering(cik, end)
        if rec is None or "Assets" not in day:
            continue
        liab, miss, miss_custom = liab_value(rec, day)
        if miss_custom:
            stats["needs_instance_reader"] += 1
            continue
        if liab is None or miss:
            stats["not_computable"] += 1
            continue
        eq_incl = day.get("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest")
        if eq_incl is None:
            eq_p = day.get(rec["equity_parent_tag"] or "StockholdersEquity") or Decimal(0)
            nci = day.get("MinorityInterest") or Decimal(0)
            eq_incl = eq_p + nci
        mezz = sum((day.get(m["tag"]) or Decimal(0)) for m in rec["mezzanine_face"])
        for t in ("TemporaryEquityCarryingAmountAttributableToParent",
                  "RedeemableNoncontrollingInterestEquityCarryingAmount",
                  "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests"):
            if not rec["mezzanine_face"] and day.get(t) is not None:
                mezz = day[t]
                break
        gap = day["Assets"] - (liab + mezz + eq_incl)
        rel = abs(gap) / day["Assets"] if day["Assets"] else Decimal(0)
        if rel <= Decimal("0.0005"):
            stats["identity_ties"] += 1
        else:
            stats["identity_gap"] += 1
        report["identity"]["ties" if rel <= Decimal("0.0005") else "gaps"] += 1
    report["per_company"][ticker] = dict(stats)
    for a in anchors:
        if a["ticker"] != ticker:
            continue
        end = a["period_end"]
        day = facts.get(end, {})
        rec = covering(cik, end)
        if rec is None:
            report["anchor_results"].append({**a, "result": "no_record"})
            continue
        liab, miss, miss_custom = liab_value(rec, day)
        got = str(liab) if liab is not None else None
        ok = ("expected" in a and got == a["expected"])
        report["anchor_results"].append(
            {**a, "got": got, "missing": miss, "missing_custom": miss_custom,
             "result": "PASS" if ok else "CHECK"}
        )
conn.close()
report["identity"] = dict(report["identity"])
json.dump(report, open(sys.argv[3], "w"), indent=1, default=str)
print(json.dumps(report["identity"]))
for t, s in sorted(report["per_company"].items()):
    print(t, dict(s))
print("--- anchors:")
for a in report["anchor_results"]:
    print(a["ticker"], a["period_end"], a.get("expected"), "->", a.get("got"), a["result"])
