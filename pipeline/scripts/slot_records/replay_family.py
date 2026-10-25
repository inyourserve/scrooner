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
from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).parent))
import common  # noqa: E402

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
PUBLISHABLE = {"G1_printed_line", "G2_composition_ties"}
for cik in sorted(records):
    ticker = records[cik][0]["company"]
    tags = set()
    for rec in records[cik]:
        tags.update(m["tag"] for m in rec["members"] if m["stmt"] == "CF")
        if rec.get("section"):
            tags.add(rec["section"]["total"])
            tags.update(r["tag"] for r in rec["section"]["roots"])
        tags.update(("NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
                     "NetCashProvidedByUsedInInvestingActivities", "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"))
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
    facts = common.fetch_durations(cur, cik, tags)
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
        # Section arithmetic: INFORMATIONAL only since the gate redesign
        # (SLOT-RECORDS-DA-CAPEX-GATE-DESIGN-2026-10-25): its roots include
        # lines the API never carries.
        sec = rec.get("section")
        tie = None
        if sec and sec["total"] in day:
            vals = [(day.get(r["tag"]), Decimal(r["weight"])) for r in sec["roots"]]
            present = [(v, w) for v, w in vals if v is not None]
            if len(present) == len(vals):
                gap = day[sec["total"]] - sum(v * w for v, w in present)
                tie = abs(gap) <= rounding_unit([v for v, _ in present] + [day[sec["total"]]])
        # THE GATE (member level): G1 a single root member in the slot's classes
        # is the filer's printed line; G2 a root that is a calc PARENT of other
        # members publishes only when its printed children tie to it on this
        # accession; children themselves are never summed beside their parent.
        comp = rec.get("composition") or {}
        roots = [t for t in comp.get("roots", []) if any(m["tag"] == t and m["class"] in BROAD for m in cf_members)]
        children_of = comp.get("children_of", {})
        gate = None
        gate_detail = None
        if not comp.get("has_statement_cal"):
            gate = "hold_no_statement_cal"
        elif not roots:
            gate = "hold_no_root_member"
        else:
            g2_ok, g2_fail = [], []
            for rt in roots:
                kids = children_of.get(rt, [])
                if not kids:
                    continue  # a leaf root: G1, the printed line itself
                if rt not in day:
                    g2_fail.append(f"{rt}:parent_value_missing")
                    continue
                kv = [(day.get(k), Decimal(comp["weights"].get(k, "1.0"))) for k in kids]
                if any(v is None for v, _ in kv):
                    g2_fail.append(f"{rt}:child_value_missing")
                    continue
                gap = day[rt] - sum(v * w for v, w in kv)
                (g2_ok if abs(gap) <= rounding_unit([v for v, _ in kv] + [day[rt]]) else g2_fail).append(f"{rt}:{gap}")
            missing_roots = [rt for rt in roots if rt not in day]
            if g2_fail:
                gate = "hold_composition_gap"
                gate_detail = g2_fail
            elif missing_roots:
                gate = "hold_root_value_missing"
                gate_detail = missing_roots
            else:
                gate = "G2_composition_ties" if g2_ok else "G1_printed_line"
                gate_detail = g2_ok or roots

        def roots_total(classes):
            # the slot value: ROOT members only (never a child beside its parent)
            return sum((day[t] for t in roots if t in day and any(m["tag"] == t and m["class"] in classes for m in cf_members)), Decimal(0))

        narrow, broad = roots_total(NARROW), roots_total(BROAD)
        verdict = None
        # FACE COLUMN rule (Verifier D&A V2, KRUS Q3 FY2021: a 3-month figure
        # rounded to 1.2M came from a note; the 10-Q cash flow prints only the
        # year-to-date column). A duration is a face column of this filing only
        # if the filer tagged the cash-flow SECTION TOTAL for the same
        # (start, end) in the same accession; anything else is a note or a
        # derived figure and never a slot value.
        # either spelling of the section total counts (Verifier V3: ContinuingOperations
        # in the record's cal, plain NetCashProvidedByUsedIn... on many filings)
        TOTAL_FAMILY = {"d_and_a": ("NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"),
                        "capex": ("NetCashProvidedByUsedInInvestingActivities", "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations")}[family]
        face_column = bool(sec) and any(t in day for t in TOTAL_FAMILY + (sec["total"],))
        if not day:
            verdict = "no_facts_this_period"
        elif not face_column:
            verdict = "not_a_face_column"
        elif missing_custom and any(m.get("custom") and m["tag"] in roots for m in cf_members):
            verdict = "needs_instance_reader"
        elif gate.startswith("hold"):
            verdict = gate
        elif not any(m["tag"] in roots and m["class"] in NARROW for m in cf_members):
            verdict = "no_narrow_root"  # only broad-class lines on the face (e.g. amortization only)
        else:
            verdict = gate
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
             "gate_detail": gate_detail, "section_tie": tie,
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
