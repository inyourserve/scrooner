"""Apply the per-company full 10-K reads (Verifier, FILING-CHECKED; Dhairya 2026-11-12: note-sourced and template-OUT are
decided only from these reads) on top of the library's tag map.

For a non-PASS read row:
  - printed value + printed tag  -> a 'read_verified' concept row for that tag over the read's FY-1..FY0 dates; any other
    concept/component row of that (company, concept) covering those dates is cut (its cut-out era becomes a reason row);
  - not printed                  -> a read-verified template-OUT row for the company (data point not in its template);
  - otherwise                    -> listed for review (held, N/A, open, or no tag in the read).
Usage: read_overlay.py <tag_map.csv> <read_status.csv> <fy_periods.csv> <concepts.csv> <out_map.csv> <out_template_out.csv> <out_review.csv>
"""
import collections
import csv
import datetime
import re
import sys

tm, rs_path, fy, cc, out_map, out_out, out_rev = sys.argv[1:8]
rows = list(csv.DictReader(open(tm)))
cols = list(rows[0])
cat = {r["name"]: r["statement"] for r in csv.DictReader(open(cc))}
STMT = {"income_statement": "IS", "balance_sheet": "BS", "cash_flow": "CF"}
EXTRA = {"cash_paid_for_interest": "CF", "cash_paid_for_income_taxes": "CF", "weighted_basic_shares": "IS", "weighted_diluted_shares": "IS",
         "net_interest_income": "IS"}
ALIAS = {"revenue": "revenue_sanity"}


def concept_name(dp):
    b = ALIAS.get(dp, dp)
    for n in (b + "_resolved", b):
        if n in cat or n in EXTRA:
            return n
    return None


def day(d, n=0):
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()


fyp = collections.defaultdict(list)
for r in csv.DictReader(open(fy)):
    fyp[r["company_id"]].append(r["period"])
by_co = collections.defaultdict(list)
for r in rows:
    by_co[r["company_id"]].append(r)
new_rows, t_out, review, applied, statuses = [], [], [], 0, 0
for rd in csv.DictReader(open(rs_path)):
    v = rd["verdict"]
    if v.startswith("ERA") or not rd["company_id"]:
        continue
    con = concept_name(rd["data_point"])
    ps = sorted(fyp.get(rd["company_id"], []), reverse=True)[:2]
    has_value = (bool(re.search(r"\d", rd["printed_value"])) and rd["not_printed"] != "True") or bool(
        re.search(r"(?i)prints?\b[^|]*\d[\d,.]*", rd["reason"]) and rd["printed_tag"])
    tag = rd["printed_tag"].split(":")[-1] if rd["printed_tag"] else ""
    if not tag and v == "NEW-FOUND" and "custom incl" not in rd["reason"]:  # the read names the printed tag in its reason: "(CommonStockDividendsPerShareDeclared, ..."
        m = re.findall(r"(?<![A-Za-z:])(?:us-gaap:)?((?:[A-Z][a-z0-9]+){2,}|Goodwill)(?=[ ,)]|$)", rd["reason"])
        tag, has_value = (m[-1], True) if m else ("", has_value)
    not_pr = rd["not_printed"] == "True" or bool(re.search(r"(?i)prints no |no [a-z ]*line on R\d|true not-presented", rd["reason"]))
    status = ("not_presented_read_verified" if not_pr else "held_debt_lane" if (v == "HELD" or rd["reason"].startswith("Held")) and con.startswith("total_debt")
              else "line_presented_combined_with_others" if "combined true" in rd["reason"]
              else "dps_quarterly_only_pending_definition" if re.search(r"(?i)annual DPS not printed", rd["reason"])
              else "equity_printed_only_incl_nci" if re.search(r"(?i)prints only 'Total equity' incl", rd["reason"])
              else "total_costs_incl_cost_of_revenue" if re.search(r"(?i)total including cost of goods", rd["reason"]) else "")
    ps0 = sorted(fyp.get(rd["company_id"], []), reverse=True)[:2]
    if con and status and ps0 and not (has_value and tag and v in ("NEW-FOUND", "FAIL", "FAIL-STATUS", "FAIL-VALUE", "FAIL-GAP")):
        # an FY0/FY-1 status from the full 10-K read: a reason row over the read's dates, never a value
        e = {k: "" for k in cols}
        base0 = by_co[rd["company_id"]][0] if by_co[rd["company_id"]] else {}
        e.update(company_id=rd["company_id"], cik=base0.get("cik", ""), rank=base0.get("rank", ""), taxonomy="scrooner", ticker=rd["ticker"], stmt=STMT.get(cat.get(con, ""), EXTRA.get(con, "IS")), decision="excluded",
                 tag=tag or con, reason_class=status, era_from=min(ps0), era_to=max(ps0), evidence_adsh=rd["evidence_adsh"],
                 reason=f"full 10-K read ({v}) {rd['evidence_adsh']} {rd['r_page']}: {rd['reason'][:160]}", decided_by="read_status", components=con)
        new_rows.append(e)
        statuses += 1
        continue
    if v.startswith("PASS"):
        continue
    open_ok = v == "OPEN" and bool(rd["printed_tag"]) and re.search(r"(?i)printed (in|on|only in) the", rd["reason"]) and not re.search(r"(?i)misuse|sum of|separate line|\+", rd["reason"] + rd["printed_value"])
    if con and has_value and tag and ps and (open_ok or v in ("NEW-FOUND", "FAIL", "FAIL-STATUS", "FAIL-VALUE", "FAIL-GAP")):
        a, b = min(ps), max(ps)
        stmt = STMT.get(cat.get(con, ""), EXTRA.get(con, "IS"))
        for r in by_co[rd["company_id"]]:  # cut the library's rows for this concept over the read's dates
            c = r["canonical_concept"] if r["decision"] == "concept" else r["parent_concept"] if r["decision"] == "component" else ""
            same_tag = r["tag"] == tag and r["stmt"] == stmt and not r.get("_drop")
            if (c == con or same_tag) and not (r["era_to"] < a or b < r["era_from"]):
                cut = dict(r)
                cut.update(decision="excluded", canonical_concept="", parent_concept="", combine_sign="", reason_class="read_override",
                           reason=f"the full 10-K read ({rd['evidence_adsh']} {rd['r_page']}) serves {tag} for these dates", decided_by="read_overlay",
                           era_from=max(r["era_from"], a), era_to=min(r["era_to"], b))
                if not same_tag:  # a same-tag piece would overlap the read row itself; its before/after parts are kept
                    new_rows.append(cut)
                if r["era_from"] < a:
                    keep = dict(r)
                    keep.update(era_to=day(a, -1))
                    new_rows.append(keep)
                if r["era_to"] > b:
                    keep = dict(r)
                    keep.update(era_from=day(b, 1))
                    new_rows.append(keep)
                r["_drop"] = True
        base = {k: v for k, v in by_co[rd["company_id"]][0].items() if k != "_drop"} if by_co[rd["company_id"]] else {k: "" for k in cols}
        base.update({k: "" for k in ("parent_concept", "combine_sign", "components", "reason_class", "evidence_report", "evidence_line", "evidence_cal_parent", "rule_id")})
        lab = rd["printed_label"] + " " + rd["reason"]
        combined = bool(re.search(r"(?i)\band (accrued|other|notes)\b|combined|, net\b", lab)) and con in (
            "accounts_payable", "accounts_receivable", "cf_ap_change", "cf_ar_change", "other_income_expense_net", "interest_expense_resolved", "interest_income")
        base.update(taxonomy=rd["printed_tag"].split(":")[0] if ":" in rd["printed_tag"] else "us-gaap", tag=tag, stmt=stmt,
                    decision="combined" if combined else "concept", components=(con + ";other") if combined else "",
                    reason_class="line_presented_combined_with_others" if combined else "",
                    canonical_concept="" if combined else con, era_from=a, era_to=b, evidence_adsh=rd["evidence_adsh"], evidence_plabel=rd["printed_label"][:120],
                    reason=f"read-verified ({v}): printed {rd['r_page']} in {rd['evidence_adsh']}" + (
                        "; serve note: PP&E includes finance-lease ROU assets (Dhairya ruling 2026-11-12)" if "FinanceLeaseRightOfUse" in tag else ""),
                    decided_by="read_verified", lines="1", filings="1")
        new_rows.append(base)
        applied += 1
    elif con and rd["not_printed"] == "True" and v in ("NEW-FOUND", "FAIL", "FAIL-STATUS", "OPEN"):
        t_out.append({"company_id": rd["company_id"], "ticker": rd["ticker"], "data_point": rd["data_point"], "in_template": "false",
                      "reason": "not_presented_read_verified", "evidence": f"full 10-K read {rd['evidence_adsh']}: {rd['reason'][:160]}"})
    else:
        review.append({"ticker": rd["ticker"], "data_point": rd["data_point"], "verdict": v, "printed_tag": rd["printed_tag"],
                       "printed_value": rd["printed_value"], "our_status": rd["our_status"], "reason": rd["reason"]})
# Dhairya's rulings on the read gaps, 2026-11-12. Durations may be summed from printed lines; operating-lease ROU is not PP&E.
#   (ticker, data point) -> rows over the read's FY-1..FY0 dates unless an era is given
RULINGS = {
    ("AMD", "depreciation_and_amortization"): [("CF", "us-gaap", "OtherDepreciationAndAmortization", "component", "depreciation_and_amortization_resolved", None),
                                               ("CF", "us-gaap", "AdjustmentForAmortization", "component", "depreciation_and_amortization_resolved", None)],
    ("AVGO", "amortization_of_intangibles"): [("IS", "avgo", "Amortizationofacquisitionrelatedintangibleassetscostofproductssold", "component", "amortization_of_intangibles", ("2018-07-31", "2026-07-31")),
                                              ("IS", "avgo", "Amortizationofacquisitionrelatedintangibleassetsoperatingexpenses", "component", "amortization_of_intangibles", ("2018-07-31", "2026-07-31"))],
    ("AMD", "interest_income"): [("IS", "us-gaap", "InterestIncomeExpenseNet", "concept", "interest_income", None)],  # gross interest income under the NET tag (filer misuse; the read confirmed the line)
    ("AMD", "operating_expenses"): [("IS", "us-gaap", "OperatingExpenses", "concept", "operating_expenses_resolved", None)],  # read tag = mapped tag
    ("CAT", "sbc"): [("EQ", "us-gaap", "AllocatedShareBasedCompensationExpense", "concept", "sbc", None)],  # read tag = mapped tag, value in the SBC note
    ("GE", "ppe_net"): [("BS", "ge", "PropertyPlantAndEquipmentAndOperatingLeaseRightOfUseAsset", "combined", "ppe_net;operating_lease_rou_asset", None)],
}
ROU_NOT_PPE = {("JPM", "ppe_net")}  # custom premises line incl. operating-lease ROU: shown as the company line, feeds no PP&E
co_by_tick = {r["ticker"]: r["company_id"] for r in rows}
ruled = 0
for (tk, dp), specs in RULINGS.items():
    c = co_by_tick.get(tk)
    if not c:
        continue
    ps = sorted(fyp.get(c, []), reverse=True)[:2]
    for st, tax, tag, dec, con, era in specs:
        a, b = era or (min(ps), max(ps))
        for r in by_co[c] + new_rows:  # the ruled tag/concept owns these dates
            cc = r["canonical_concept"] if r["decision"] == "concept" else r["parent_concept"] if r["decision"] == "component" else ""
            hit = (dec != "combined" and cc == con and r["decision"] == dec == "concept") or (r["tag"] == tag and r["stmt"] == st)
            if hit and r.get("company_id") == c and not r.get("_drop") and not (r["era_to"] < a or b < r["era_from"]):
                if r["era_from"] < a:
                    new_rows.append({**r, "era_to": day(a, -1), "_drop": False})
                if r["era_to"] > b:
                    new_rows.append({**r, "era_from": day(b, 1), "_drop": False})
                r["_drop"] = True
        e = {k: v for k, v in by_co[c][0].items() if k != "_drop"}
        e.update({k: "" for k in ("canonical_concept", "parent_concept", "combine_sign", "components", "reason_class", "evidence_report", "evidence_line", "evidence_cal_parent", "rule_id", "evidence_plabel")})
        e.update(taxonomy=tax, tag=tag, stmt=st, decision=dec, era_from=a, era_to=b, decided_by="ruling", lines="1", filings="1",
                 reason=f"Dhairya ruling 2026-11-12 on the full 10-K read ({tk} {dp})")
        if dec == "concept":
            e["canonical_concept"] = con
        elif dec == "component":
            e.update(parent_concept=con, combine_sign="1")
        else:
            e.update(components=con, reason_class="line_presented_combined_with_others")
        new_rows.append(e)
        ruled += 1
new_rows = [r for r in new_rows if not r.pop("_drop", False) and not (r["decided_by"] == "read_verified" and (r["ticker"], next(
    (d for (t, d) in RULINGS if t == r["ticker"] and r["canonical_concept"] and r["canonical_concept"].startswith(d)), "")) in RULINGS)]
for tk, dp in ROU_NOT_PPE:
    c = co_by_tick.get(tk)
    ps = sorted(fyp.get(c, []), reverse=True)[:2]
    if c and ps:
        e = {k: "" for k in cols}
        e.update(company_id=c, cik=by_co[c][0]["cik"], rank=by_co[c][0]["rank"], ticker=tk, taxonomy="scrooner", tag="ppe_net_resolved", stmt="BS",
                 decision="excluded", reason_class="ppe_incl_operating_lease_rou", components="ppe_net_resolved", era_from=min(ps), era_to=max(ps), decided_by="read_status",
                 reason="Dhairya ruling 2026-11-12: the printed premises line includes operating-lease ROU, a separate GAAP asset: not PP&E")
        new_rows.append(e)
        ruled += 1
print("ruled rows", ruled)
kept = [r for r in rows if not r.pop("_drop", False)]
# same tag, same concept: two non-excluded rows never overlap (0122); the earlier row ends the day before the later one starts
by_tag = collections.defaultdict(list)
for r in kept + new_rows:
    if r["decision"] != "excluded":
        by_tag[(r["company_id"], r["taxonomy"], r["tag"], r["stmt"], r["canonical_concept"] or r["parent_concept"])].append(r)
trimmed, gone = 0, set()
for grp in by_tag.values():
    grp.sort(key=lambda r: (r["era_from"], r["decided_by"] != "read_verified"))
    for x, y in zip(grp, grp[1:]):
        if x["era_to"] >= y["era_from"]:
            x["era_to"] = day(y["era_from"], -1)
            trimmed += 1
            if x["era_to"] < x["era_from"]:
                gone.add(id(x))
kept = [r for r in kept if id(r) not in gone]
new_rows = [r for r in new_rows if id(r) not in gone]
print("same-tag overlaps trimmed", trimmed, "| emptied", len(gone))
with open(out_map, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(kept + new_rows)
for path, data in ((out_out, t_out), (out_rev, review)):
    with open(path, "w", newline="") as fh:
        if data:
            w = csv.DictWriter(fh, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
print("read rows applied", applied, "| read statuses", statuses, "| template-OUT read-verified", len(t_out), "| for review", len(review))
