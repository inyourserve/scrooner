"""Emit family capex_da_cash_debt cells in the common cell format v1
(data-team/46-canonical-fact-v2/CELL-FORMAT-v1.md, branch work/engineering/canonical-fact-v2 a3b6a8b) for the
1,000 cohort companies, every FY/Q/I cell since 2014-01-01. Founder 2026-11-04: rebuild, not patch.

Sources (all offline, zero SEC requests): cf_da_capex_variants.py cells (capex_resolved, depreciation_and_amortization
_resolved), bs_cash_variants.py cells (cash_and_equivalents_resolved), cohort core.period rows (exact dates).
Grains: FY = a 10-K's annual column; Q = a printed 3-month column, or DERIVED Q2-Q4 as YTD_n - YTD_n-1 (Dhairya
2026-11-04: flows are additive) when both inputs are emitted values from the cash-flow face; inputs whose member
compositions differ are held mixed_vintage_inputs; a negative derived flow is held quarters_do_not_sum_to_ytd.
I = balance-sheet instant. Held cells keep their reason (state, reason_code, defect class/owner).
Release classes (Verifier history): capex publishes single-member cells; multi-member cells hold until a structural
method exists. D&A publishes is_anchor / single_line_* classes. Cash publishes every valued cell (v1 17/17).
usage: emit_capex_da_cash.py <capex_da_cells.jsonl.gz> <cash_cells.jsonl.gz> <cohort.csv> <expected_periods.csv.gz>
                             <git_commit> <out_dir>
"""
import csv
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

capda_path, cash_path, cohort_path, cal_path, git_commit, out = sys.argv[1:7]
out = Path(out)
out.mkdir(parents=True, exist_ok=True)
FAMILY = "capex_da_cash_debt"
DP = {"capex": "capex_resolved", "d_and_a": "depreciation_and_amortization_resolved", "cash": "cash_and_equivalents_resolved"}
RULE = {"capex": f"{FAMILY}.capex_face@21", "d_and_a": f"{FAMILY}.d_and_a_face@21", "cash": f"{FAMILY}.cash_face@2",
        "derived": f"{FAMILY}.flow_q_by_ytd_subtraction@1"}
DA_EMIT = {"is_anchor", "single_line_ties_is", "single_line_clean"}

company = {r["cik"].lstrip("0"): int(r["company_id"]) for r in csv.DictReader(open(cohort_path))}


def month_end(d):
    y, m, dd = int(d[:4]), int(d[5:7]), int(d[8:10])
    if dd < 15:
        return (date(y, m, 1) - timedelta(days=1)).isoformat()
    return (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)).isoformat()


# reason -> (state, reason_code, reason_text, defect_class, owner)
HOLD = {
    # capex
    "perimeter_line_unresolved": ("defect", "line_presented_combined_with_others", "A capex line on the cash-flow statement mixes items that cannot be split from the face.", "composition", "standardization_lead"),
    "capex_sign_unresolved": ("defect", "sign_conflict", "The direction of a capex line cannot be read from the filer's own investing section.", "composition", "standardization_lead"),
    "capex_line_names_no_asset": ("defect", "line_presented_combined_with_others", "A capex member's label names no property, plant or equipment asset.", "composition", "standardization_lead"),
    "other_capex_lines_outside_ruling": ("defect", "definition_outside_ruling", "Real-estate acquisition or development lines are outside the ruled capex definition.", "definition_pending", "accountant"),
    "no_continuing_capex_line": ("not_presented", "line_not_presented_in_filing", "The cash-flow statement prints no capital-expenditure line for this period.", None, None),
    "multi_member_composition_unverified": ("defect", "held_pending_verifier", "Capex is the sum of several printed lines; the structural method that proves the sum is not built yet.", "composition", "standardization_lead"),
    # D&A
    "da_combined_with_other_items": ("not_presented", "line_presented_combined_with_others", "The cash-flow statement prints depreciation and amortization combined with other items.", None, None),
    "da_definition_question": ("defect", "definition_outside_ruling", "The D&A line includes lessor-equipment depreciation or lease-incentive amortization, a definition question.", "definition_pending", "accountant"),
    "no_da_line": ("not_presented", "line_not_presented_in_filing", "The cash-flow statement prints no depreciation or amortization line for this period.", None, None),
    "no_depreciation_line_on_cf": ("defect", "line_presented_combined_with_others", "The cash-flow statement prints amortization but no depreciation line, and no income-statement total ties.", "composition", "standardization_lead"),
    "da_net_line_below_intangible_amortization": ("defect", "shown_differs_from_printed_line", "The D&A line is printed net and is below the filing's own intangible amortization.", "composition", "standardization_lead"),
    "da_multi_member_unverified": ("defect", "held_pending_verifier", "D&A is the sum of several printed lines without an income-statement tie; the structural method is not built yet.", "composition", "standardization_lead"),
    # cash
    "cash_includes_restricted": ("not_presented", "line_presented_combined_with_others", "The balance sheet prints cash together with restricted cash in one line.", None, None),
    "cash_combined_with_investments": ("not_presented", "line_presented_combined_with_others", "The balance sheet prints cash together with investments in one line.", None, None),
    "bank_cash_definition": ("defect", "definition_outside_ruling", "Bank cash components do not tie to the bank's own cash-flow cash definition.", "evidence_pending", "sector_analyst"),
    "two_cash_lines": ("defect", "line_presented_combined_with_others", "The balance sheet prints two cash lines and the cash-equivalents line cannot be chosen from the face.", "composition", "standardization_lead"),
    "no_cash_line": ("not_presented", "line_not_presented_in_filing", "The balance sheet prints no cash line for this date.", None, None),
    "cash_flow_anchor_differs": ("defect", "shown_differs_from_printed_line", "The balance-sheet cash line differs from the filer's own cash-flow ending cash.", "identity", "data_engineer_l1"),
    # derived quarters
    "mixed_vintage_inputs": ("defect", "mixed_vintage_inputs", "The two year-to-date inputs of this quarter have different member compositions.", "period", "period_engineer"),
    "quarters_do_not_sum_to_ytd": ("defect", "quarters_do_not_sum_to_ytd", "Subtracting the year-to-date inputs gives a negative flow for this quarter.", "period", "period_engineer"),
}
NEW_CODES = {"definition_outside_ruling": "the line falls outside a ruled definition (owner decides)"}

rows, stats, unbound = [], Counter(), Counter()


def emit(fam, cid, cik, grain, start, end, state, value, accession, members, fsn_stmt, rule_id, evidence, reason=None, refs=None,
         derivation=None, fiscal=None):
    r = {"company_id": cid, "cik": f"{int(cik):010d}", "data_point_name": DP[fam], "period_grain": grain,
         "period_start": start, "period_end": end, "basis": "latest", "state": state,
         "value": value, "unit": "USD" if value is not None else None, "decimals": None,
         "source_fact_ids": [], "accession": accession, "tag": (members[0]["tag"] if members and len(members) == 1 else None),
         "members": members or None, "fsn_set": None, "fsn_stmt": fsn_stmt, "fsn_line": None, "derivation": derivation,
         "rule_id": rule_id, "rule_run_id": None, "evidence_level": evidence,
         "reason_code": None, "reason_text": None, "defect_class": None, "owner": None, "root_cause_class": None,
         "input_refs": refs or {}}
    if fiscal:
        r.update(fiscal)
    if reason:
        st, code, text, dcls, owner = HOLD[reason]
        r.update({"state": st, "value": None, "unit": None, "reason_code": code, "reason_text": text})
        r["input_refs"]["engine_reason"] = reason
        if st == "defect":
            r.update({"defect_class": dcls, "owner": owner, "root_cause_class": dcls if dcls not in ("guard_hidden", "finding_open") else None})
    rows.append(r)
    stats[(fam, grain, r["state"])] += 1


def mem(lines, accession):
    return [{"tag": x["tag"], "value": str(x["value"]), "accession": accession, "label": x["label"]} for x in lines]


# ---- my cells, keyed by (rounded month-end, length in quarters) ----
flows = defaultdict(dict)  # (fam, cid) -> {(end, q): (value or None, reason, accession, members, tagset, refs, cik)}
for line in gzip.open(capda_path, "rt"):
    c = json.loads(line)
    fam = c["family"]
    cid = company.get(str(c["cik"]))
    if cid is None:
        continue
    if fam == "capex":
        lines = c["lines"]
        val, reason = c["interim"], c["interim_reason"]
        if val is not None and len(lines) != 1:
            val, reason = None, "multi_member_composition_unverified"
        refs = {"exclusion_note": c.get("exclusion_note")} if c.get("exclusion_note") else {}
    else:
        lines = [x for x in c["lines"] if x["nature"] == "asset_da"]
        val, reason = c["value"], c["reason"]
        if val is not None and c.get("da_class") not in DA_EMIT:
            val, reason = None, "da_multi_member_unverified"
        refs = {"da_class": c.get("da_class")}
        if c.get("is_da_tie"):
            refs["is_da_tie"], refs["is_da_total"] = c["is_da_tie"], c.get("is_da_total")
    flows[(fam, cid)][(c["end"], c["qtrs"])] = (val, reason, c["accession"], mem(lines, c["accession"]),
                                                frozenset(x["tag"] for x in lines), refs, c["cik"])
cash = {}
for line in gzip.open(cash_path, "rt"):
    c = json.loads(line)
    cid = company.get(str(c["cik"]))
    if cid is not None:
        cash[(cid, c["end"])] = c

# ---- the shared expected-cell calendar drives the rows: every expected key gets a row ----
NOT_CAPTURED = ("defect", "not_captured", "No filing column for this period was captured from the filer's statements.", "unclassified", "triage")
YTD_ONLY = ("not_presented", "cash_flow_prints_ytd_only", "The 10-Q prints year-to-date flows only and a year-to-date input for this quarter is missing.", None, None)
HOLD["__not_captured__"], HOLD["__ytd_only__"] = NOT_CAPTURED, YTD_ONLY
QN = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
cal_cik = {}
seen_inst = set()
for r in csv.DictReader(gzip.open(cal_path, "rt")):
    cid, start, end = int(r["company_id"]), r["period_start"], r["period_end"]
    cal_cik[cid] = r["cik"]
    if end < "2014-01-01":
        continue
    me = month_end(end)
    if r["period_type"] == "instant":
        if (cid, end) in seen_inst:
            continue  # FY and Q4 instants share the date: one I row
        seen_inst.add((cid, end))
        c = cash.get((cid, me))
        if c is None:
            emit("cash", cid, r["cik"], "I", end, end, "value", None, None, None, "BS", RULE["cash"], "DATA-INFERRED", "__not_captured__", {})
            continue
        members = [{"tag": m["tag"], "value": m["value"], "accession": c["accession"], "label": m["label"]}
                   for m in c["members"] if m["nature"] in ("pure", "bank")]
        emit("cash", cid, r["cik"], "I", end, end, "value", c["value"], c["accession"], members, "BS", RULE["cash"], "FILING-CHECKED",
             c["reason"], {"cf_ending": c["cf_ending"]} if c["cf_ending"] else {})
        continue
    grain = "FY" if r["fiscal_period"] == "FY" else "Q"
    for fam in ("capex", "d_and_a"):
        cells = flows.get((fam, cid), {})
        if grain == "FY":
            hit = cells.get((me, 4))
            if hit is None:
                emit(fam, cid, r["cik"], "FY", start, end, "value", None, None, None, "CF", RULE[fam], "DATA-INFERRED", "__not_captured__", {})
            else:
                val, reason, acc, members, _t, refs, _k = hit
                emit(fam, cid, r["cik"], "FY", start, end, "value", val, acc, members, "CF", RULE[fam], "FILING-CHECKED", reason, dict(refs))
            continue
        n = QN[r["fiscal_period"]]
        printed = cells.get((me, 1))
        if printed is not None and (n == 1 or printed[0] is not None):
            val, reason, acc, members, _t, refs, _k = printed
            emit(fam, cid, r["cik"], "Q", start, end, "value", val, acc, members, "CF", RULE[fam], "FILING-CHECKED", reason, dict(refs))
            continue
        if n == 1:
            emit(fam, cid, r["cik"], "Q", start, end, "value", None, None, None, "CF", RULE[fam], "DATA-INFERRED", "__not_captured__", {})
            continue
        # derived: YTD_n - YTD_(n-1); Q4 = FY - 9M
        cur = cells.get((me, n))
        prev_end = month_end((date.fromisoformat(me).replace(day=1) - timedelta(days=80)).isoformat()[:8] + "28")
        prev = cells.get((prev_end, n - 1))
        lbl = {2: "6M_YTD", 3: "9M_YTD", 4: "FY"}[n]
        plbl = {2: "Q1", 3: "6M_YTD", 4: "9M_YTD"}[n]
        if cur is None or prev is None:
            emit(fam, cid, r["cik"], "Q", start, end, "derived", None, None, None, "CF", RULE["derived"], "DATA-INFERRED", "__ytd_only__",
                 {"missing_input": lbl if cur is None else plbl})
            continue
        val, reason, acc, _m, tags, _r, _k = cur
        pv, preason, pacc, _pm, ptags, _pr, _ = prev
        derivation = {"formula": f"{lbl} - {plbl}", "input_values": [val, pv], "input_accessions": [acc, pacc], "policy": "same_vintage"}
        if val is None or pv is None:
            held = reason if val is None else preason
            emit(fam, cid, r["cik"], "Q", start, end, "derived", None, None, None, "CF", RULE["derived"], "DATA-INFERRED", held,
                 {"held_input": lbl if val is None else plbl}, derivation)
            continue
        if tags != ptags:
            emit(fam, cid, r["cik"], "Q", start, end, "derived", None, acc, None, "CF", RULE["derived"], "DATA-INFERRED", "mixed_vintage_inputs",
                 {"input_members": [sorted(tags), sorted(ptags)]}, derivation)
            continue
        dv = Decimal(val) - Decimal(pv)
        if dv < 0:
            emit(fam, cid, r["cik"], "Q", start, end, "derived", None, acc, None, "CF", RULE["derived"], "DATA-INFERRED", "quarters_do_not_sum_to_ytd",
                 {"ytd": val, "prior": pv}, derivation)
            continue
        emit(fam, cid, r["cik"], "Q", start, end, "derived", str(dv), acc, None, "CF", RULE["derived"], "DATA-INFERRED", None, {}, derivation)

# one row per key
keys = Counter((r["company_id"], r["data_point_name"], r["period_grain"], r["period_start"], r["period_end"]) for r in rows)
dups = {k for k, n in keys.items() if n > 1}
if dups:  # a printed Q column and a derived quarter on the same key: the printed one wins
    keep, seen = [], set()
    for r in sorted(rows, key=lambda r: r["state"] == "derived"):
        k = (r["company_id"], r["data_point_name"], r["period_grain"], r["period_start"], r["period_end"])
        if k in seen:
            stats["duplicate_dropped"] += 1
            continue
        seen.add(k)
        keep.append(r)
    rows = keep
data = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows).encode()
with gzip.open(out / "cells.jsonl.gz", "wb") as fo:
    fo.write(data)
manifest = {"family": FAMILY, "rule_id": RULE, "git_commit": git_commit, "produced_at": date.today().isoformat(),
            "rows": len(rows), "sha256": hashlib.sha256(open(out / "cells.jsonl.gz", "rb").read()).hexdigest(),
            "companies": len({r["company_id"] for r in rows}), "data_points": sorted(DP.values()), "period_floor": "2014-01-01",
            "new_reason_codes": NEW_CODES,
            "note": "total_debt_resolved is NOT in this file (cohort debt build in progress); data_points lists only what this file carries",
            "calendar": "data-team/46-canonical-fact-v2/expected_periods_2026-10-31.csv.gz (every expected key gets a row)"}
json.dump(manifest, open(out / "manifest.json", "w"), indent=1)
print(json.dumps({(":".join(k) if isinstance(k, tuple) else k): n for k, n in sorted(stats.items(), key=str)} | {"rows": len(rows)}, indent=1))
