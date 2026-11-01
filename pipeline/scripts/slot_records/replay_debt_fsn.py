"""Replay the verified total-debt slot records (assemble30.py records; Verifier V5.2 19/19) with
facts from the FSN extracts instead of the database. Same verdict logic as replay30.py, kept
line for line where it decides a value: lease-inclusive perimeter (default), operating leases
excluded, missing member = hard stop unless the filer's printed aggregate ties, custom members
read from FSN (same accession, so no instance reader), the no-current-side rule with the note
reconciliation, face-admission ties, note differences as flags. Differences from replay30.py:
  - facts = the ORIGINAL periodic filing whose period is the instant (else the latest filing
    carrying the instant), all undimensioned USD instants incl. notes (fsn_company_instants.py)
  - cells = every balance-sheet instant 2015+ that a filing prints (Assets / L&E total tagged),
    not a lane-3 list; an instant after the last record era holds (no_covering_record)
  - production's total_debt_resolved is information only (a verdict never depends on it)
Dry run: writes a report, nothing to the database.
usage: replay_debt_fsn.py <records.jsonl> <instants.jsonl.gz> <prod_debt.jsonl.gz> <out.json>
"""
import gzip
import json
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

LEASE_TAGS = {"cur": ["FinanceLeaseLiabilityCurrent", "CapitalLeaseObligationsCurrent"],
              "noncur": ["FinanceLeaseLiabilityNoncurrent", "CapitalLeaseObligationsNoncurrent"]}
AGG_TAGS = ["DebtAndCapitalLeaseObligations", "DebtLongtermAndShorttermCombinedAmount"]
BS_TOTAL = ("Assets", "LiabilitiesAndStockholdersEquity", "LiabilitiesAndPartnersCapital")
rec_path, inst_path, prod_path, out_path = sys.argv[1:5]
# company-level holds decided by the release owner (Dhairya 2026-11-04: AMZN's custom lease elements unread)
COMPANY_HOLDS = {}  # AMZN released (Verifier debt v3): its custom lease line decomposes; finance leases come from the note

records = defaultdict(list)
for line in open(rec_path):
    r = json.loads(line)
    # operating-lease members never enter total debt; drop them from the member list entirely so no rule
    # can see them (Verifier debt v3: MSFT OperatingLeaseLiabilityNoncurrent, a label trap)
    r["members"] = [m for m in r["members"] if m["class"] != "operating_lease"]
    records[int(r["cik"])].append(r)


def month_end(d):
    y, m, dd = int(d[:4]), int(d[5:7]), int(d[8:10])
    if dd < 15:
        return (date(y, m, 1) - timedelta(days=1)).isoformat()
    return (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)).isoformat()


prod, prod_n = {}, defaultdict(int)
for line in gzip.open(prod_path, "rt"):
    cik, name, s, e, v = json.loads(line)
    prod[(cik, month_end(e))] = Decimal(v)
    prod_n[(cik, month_end(e))] += 1

# one filing per (cik, instant): the original whose period is the instant, non-amendment, latest filed
best, filings = {}, {}
for line in gzip.open(inst_path, "rt"):
    f = json.loads(line)
    if f["cik"] not in records:
        continue
    filings[f["adsh"]] = f
    for d, vals in f["values"].items():
        if d < "20140101" or not any(t in vals for t in BS_TOTAL):  # v2 window: since 2014
            continue
        rank = (d == f["period"], not f["form"].endswith("/A"), f["filed"])
        if (f["cik"], d) not in best or rank > best[(f["cik"], d)][0]:
            best[(f["cik"], d)] = (rank, f["adsh"])


def covering_record(cik, period_end):
    ym = period_end[:7]
    for rec in records.get(cik, []):
        if rec["period_from"][:7] <= ym <= rec["period_to"][:7]:
            return rec
    return None


report = {"cells": [], "summary": defaultdict(int), "per_company": defaultdict(lambda: defaultdict(int))}
for (cik, d), (_r, adsh) in sorted(best.items()):
    f = filings[adsh]
    period_end = f"{d[:4]}-{d[4:6]}-{d[6:]}"
    ticker = records[cik][0]["company"]
    day = {t: (Decimal(v), True) for t, v in f["values"][d].items()}
    rec = covering_record(cik, period_end)
    pv = prod.get((cik, period_end)) if prod_n.get((cik, period_end)) == 1 else None
    if rec is None:
        verdict = "no_covering_record"
        report["summary"][verdict] += 1
        report["per_company"][ticker][verdict] += 1
        report["cells"].append({"ticker": ticker, "cik": cik, "period_end": period_end, "accession": adsh, "verdict": verdict,
                                "slot_lease_inclusive": None, "prod_value": str(pv) if pv is not None else None})
        continue
    # ---- value logic: replay30.py, unchanged ----
    lease_incl = Decimal(0)
    missing, missing_custom = [], []
    combined_sides = set()
    for m in rec["members"]:
        if m["class"] == "operating_lease":
            continue
        if m["class"] == "combined":
            combined_sides.add("cur" if m["side"] == "current" else "noncur")
        if m["tag"] in day:
            lease_incl += day[m["tag"]][0]
        elif m.get("custom"):
            missing_custom.append(m["tag"])
        else:
            missing.append(m["tag"])
    lease_content = Decimal(0)
    for m in rec["members"]:
        if m["class"] == "finance_lease" and m["tag"] in day:
            lease_content += day[m["tag"]][0]
    for side in combined_sides:
        for lt in LEASE_TAGS[side]:
            if lt in day:
                lease_content += day[lt][0]
                break
    borrowings = lease_incl - lease_content
    note_current_added, current_unverified, note_flag = None, False, None
    has_current_side = any(m["side"] == "current" and m["class"] != "operating_lease" for m in rec["members"])
    ltd_note = day.get("LongTermDebt")
    noncur_ltd = sum((day[m["tag"]][0] for m in rec["members"]
                      if m["side"] == "noncurrent" and m["tag"] in day and re.search(r"LongTermDebt", m["tag"])), Decimal(0))
    if not has_current_side and noncur_ltd > 0:
        ltd_cur = day.get("LongTermDebtCurrent")
        next12 = day.get("LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths")
        if ltd_note is not None and abs(ltd_note[0] - noncur_ltd) <= 1:
            pass
        elif (ltd_cur is not None and ltd_cur[0] == 0) or (next12 is not None and next12[0] == 0):
            pass
        elif ltd_cur is not None and ltd_note is not None and abs(noncur_ltd + ltd_cur[0] - ltd_note[0]) <= 1:
            lease_incl += ltd_cur[0]
            borrowings += ltd_cur[0]
            note_current_added = ltd_cur[0]
        elif ltd_cur is not None and ltd_cur[0] > 0:
            lease_incl += ltd_cur[0]
            borrowings += ltd_cur[0]
            note_current_added = ltd_cur[0]
            note_flag = f"current_portion_from_note_unreconciled:{ltd_cur[0]}"
        else:
            current_unverified = True
    if ltd_note is not None:
        ltd_face = sum((day[m["tag"]][0] for m in rec["members"]
                        if m["tag"] in day and re.search(r"Debt|Borrow|CommercialPaper|NotesPayable", m["tag"])
                        and m["class"] not in ("operating_lease", "finance_lease")), Decimal(0)) + (note_current_added or Decimal(0))
        if abs(ltd_note[0] - ltd_face) > 1:
            note_flag = (note_flag + ";" if note_flag else "") + f"face_vs_note_LongTermDebt:{ltd_face - ltd_note[0]}"
    filer_agg = next((day[t][0] for t in AGG_TAGS if t in day), None)
    agg_unit = Decimal(0)
    if filer_agg is not None:
        agg_unit = Decimal(100000000)
        while agg_unit > 1 and filer_agg != 0 and filer_agg % agg_unit != 0:
            agg_unit /= 10
    tie_pending = []
    for m in rec["members"]:
        tie = m.get("tie")
        if not tie or m["tag"] not in day:
            continue
        if not tie.get("computable") or tie.get("total") not in day:
            tie_pending.append(f"{m['tag']}:no_printed_total")
            continue
        vals = [day[t][0] for t in tie["roots"] if t in day]
        if len(vals) != len(tie["roots"]):
            tie_pending.append(f"{m['tag']}:root_values_missing")
            continue
        less = tie.get("less") or []
        less = [less] if isinstance(less, str) else less
        if any(t not in day for t in less):
            tie_pending.append(f"{m['tag']}:less_values_missing")
            continue
        target = day[tie["total"]][0] - sum((day[t][0] for t in less), Decimal(0))
        unit = Decimal(1000000)
        for v in vals + [target]:
            while unit > 1 and v != 0 and v % unit != 0:
                unit /= 10
        if abs(sum(vals) - target) > unit:
            tie_pending.append(f"{m['tag']}:gap={sum(vals) - target}")
    # a lease-liability line printed on the balance sheet that the record does not carry (custom lease
    # elements, AMZN 'Long-term lease liabilities') leaves the lease-inclusive perimeter unproven
    member_tags = {m["tag"] for m in rec["members"]}
    lease_unread = sorted({r["tag"] for r in f["bs"] if r["tag"] in day and r["tag"] not in member_tags
                           and re.search(r"lease", r["plabel"], re.I) and re.search(r"liabilit|obligation", r["plabel"], re.I)
                           and not re.search(r"operating", r["plabel"] + r["tag"], re.I) and not r["tag"].startswith("OperatingLease")})
    # a face lease line that the filer's own facts decompose into operating + finance leases is proven
    # (AMZN 'Long-term lease liabilities' 77,297 = operating 67,220 + finance 10,077); its finance part
    # then comes from the note (option b), never from the combined line
    decomposed = []
    for t in lease_unread:
        v = day[t][0]
        for op, fi in (("OperatingLeaseLiabilityNoncurrent", "FinanceLeaseLiabilityNoncurrent"),
                       ("OperatingLeaseLiabilityCurrent", "FinanceLeaseLiabilityCurrent"),
                       ("OperatingLeaseLiability", "FinanceLeaseLiability")):
            if op in day and fi in day and abs(day[op][0] + day[fi][0] - v) <= 1:
                decomposed.append(t)
                break
    lease_unread = [t for t in lease_unread if t not in decomposed]
    # ... or a finance/capital lease fact in the filing (often in the notes) that no member carries and no
    # combined (debt-and-lease) member can contain (AMZN 2015-2018 capital lease obligations)
    lease_in_notes = []
    if not combined_sides:
        lease_in_notes = sorted(t for t, (v, _a) in day.items() if v and t not in member_tags and re.fullmatch(
            r"(FinanceLeaseLiability|CapitalLeaseObligations)(Current|Noncurrent)?|FinanceLeaseLiabilityCurrentAndNoncurrent|"
            r"CapitalLeaseObligationsIncurred?", t) and not t.endswith("Incurred"))
    lease_in_notes = [t for t in lease_in_notes if t not in lease_unread]
    note_lease_added = None
    if lease_in_notes:
        # OPTION (b), founder ruling 2026-11-04 (relayed by Dhairya): finance leases that sit only in the
        # notes, outside every member, are added to the lease-inclusive total from the SAME accession
        # (MSFT, META, AAPL, GOOG, NVDA). Total element first, else current + noncurrent; capital-lease
        # elements (pre-ASC 842) the same way. Borrowings-only is unchanged.
        def pick(total, cur_, noncur):
            if total in day:
                return day[total][0], total
            parts = [t for t in (cur_, noncur) if t in day]
            return (sum((day[t][0] for t in parts), Decimal(0)), "+".join(parts)) if parts else (None, None)
        v, src = pick("FinanceLeaseLiability", "FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent")
        if v is None:
            v, src = pick("CapitalLeaseObligations", "CapitalLeaseObligationsCurrent", "CapitalLeaseObligationsNoncurrent")
        if v:
            lease_incl += v
            note_lease_added = str(v)
            note_flag = (note_flag + ";" if note_flag else "") + f"note_finance_lease_added:{src}={v}"
    verdict = None
    if ticker in COMPANY_HOLDS:
        verdict = COMPANY_HOLDS[ticker]
    elif lease_unread:
        verdict = "debt_lease_member_unverified"
    elif not rec.get("coverage_clean", True):
        verdict = "not_computable_uncovered_candidates"
    elif missing_custom:
        verdict = "custom_member_missing_in_filing"  # FSN carries custom tags: absent means not filed here
    elif tie_pending:
        verdict = "face_admission_tie_pending"
    elif missing and filer_agg is not None and abs(lease_incl - filer_agg) <= 1:
        pass
    elif missing:
        verdict = "not_computable_missing_member"
    elif current_unverified:
        verdict = "current_maturities_unverified"
    elif filer_agg is not None and abs(lease_incl - filer_agg) > max(Decimal(1), agg_unit):
        note_flag = (note_flag + ";" if note_flag else "") + f"face_vs_note_aggregate:{lease_incl - filer_agg}"
    publishable = verdict is None
    if publishable:
        verdict = ("prod_blank" if pv is None else "prod_agrees" if abs(pv - lease_incl) <= 1 else "prod_differs")
    report["summary"][verdict] += 1
    report["per_company"][ticker][verdict] += 1
    report["cells"].append({
        "ticker": ticker, "cik": cik, "period_end": period_end, "accession": adsh, "verdict": verdict,
        "record_filing_from": rec["filing_from"], "members": [(m["tag"], m["class"], m["side"]) for m in rec["members"]],
        "slot_lease_inclusive": str(lease_incl) if publishable else None,
        "slot_borrowings": str(borrowings) if publishable else None,
        "prod_value": str(pv) if pv is not None else None,
        "lease_lines_not_in_record": lease_unread, "missing_members": missing, "missing_custom_members": missing_custom, "face_admission_tie_pending": tie_pending,
        "note_current_portion_added": str(note_current_added) if note_current_added is not None else None,
        "note_finance_lease_added": note_lease_added, "note_flag": note_flag})
report["summary"] = dict(report["summary"])
report["per_company"] = {k: dict(v) for k, v in report["per_company"].items()}
json.dump(report, open(out_path, "w"), indent=1)
print(json.dumps(report["summary"], indent=1))
for t in sorted(report["per_company"]):
    print(t, dict(report["per_company"][t]))
