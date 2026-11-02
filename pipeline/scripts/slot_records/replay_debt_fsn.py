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
       replay_debt_fsn.py --company <dir|parent|@list> <records.jsonl> <out.json> [prod_debt.jsonl.gz]
  --company: facts from FSN store company directories (fsn_company_bs.instants, debt vocabulary, the
  same filters as the cohort extract). Without prod_debt production is never read and a publishable
  cell's verdict is 'publishable' (FSN store design: no verdict depends on production).
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
# company-level holds decided by the release owner (Dhairya 2026-11-04: AMZN's custom lease elements unread)
COMPANY_HOLDS = {}  # AMZN released (Verifier debt v3): its custom lease line decomposes; finance leases come from the note


def load_records(rec_path):
    records = defaultdict(list)
    for line in open(rec_path):
        r = json.loads(line)
        # operating-lease members never enter total debt; drop them from the member list entirely so no rule
        # can see them (Verifier debt v3: MSFT OperatingLeaseLiabilityNoncurrent, a label trap)
        r["members"] = [m for m in r["members"] if m["class"] != "operating_lease"]
        records[int(r["cik"])].append(r)
    return records


def month_end(d):
    y, m, dd = int(d[:4]), int(d[5:7]), int(d[8:10])
    if dd < 15:
        return (date(y, m, 1) - timedelta(days=1)).isoformat()
    return (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)).isoformat()


def load_prod(prod_path):
    """production total_debt_resolved, information only; None = production not read (FSN store port)."""
    prod, prod_n = {}, defaultdict(int)
    if prod_path is None:
        return None, prod_n
    for line in gzip.open(prod_path, "rt"):
        cik, name, s, e, v = json.loads(line)
        prod[(cik, month_end(e))] = Decimal(v)
        prod_n[(cik, month_end(e))] += 1
    return prod, prod_n


# filings that print a finance/capital lease liability for an instant (face or note), per (cik, instant):
# a latest copy without one, where an earlier copy has one, is incomplete for the lease-inclusive total
NOTE_LEASE_TAGS = ("FinanceLeaseLiability", "FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent",
                   "CapitalLeaseObligations", "CapitalLeaseObligationsCurrent", "CapitalLeaseObligationsNoncurrent")
NOTE_LEASE = defaultdict(set)
ACCEPTED_OF = {}  # adsh -> (accepted, filed, adsh), the selection order
CELL_FROM = "20150101"
# REPLAY_DEBT_ABLATE=first_filed: the gate's ablation run that isolates the selection change from the other fixes;
# never set in production runs (the pilot/cohort paths do not read it)
import os  # noqa: E402
ABLATE_FIRST_FILED = os.environ.get("REPLAY_DEBT_ABLATE") == "first_filed"  # cells from 2015-01-01 (invariant I11, data-team/34); values are stored from 2014


LEASE_COMPONENT = {"FinanceLeaseLiabilityNoncurrent": ("FinanceLeaseLiability", "FinanceLeaseLiabilityCurrent"),
                   "CapitalLeaseObligationsNoncurrent": ("CapitalLeaseObligations", "CapitalLeaseObligationsCurrent")}
NOTE_DEBT_TAGS = ("LongTermDebt", "LongTermDebtCurrent", "LongTermDebtNoncurrent")


def drop_misdated_lease_components(values, d):
    """Debt Verifier trap META 2018-12-31 (0001326801-20-000013 R47): the FY2019 10-K prints 'Lease liabilities,
    non-current' 418 in the Dec. 31, 2018 context, but 473 = 55 + 418 is the 2019 total. A noncurrent lease
    component at instant d is a filer context error, never a 2018 liability, when the same filing prints the
    lease total and current portion at ANOTHER instant d2 with total - current equal to this value to the unit,
    the component is absent at d2, and neither total nor current is printed at d. Returns {tag} to ignore."""
    drop = set()
    for comp, (total, cur) in LEASE_COMPONENT.items():
        x = values.get(d, {}).get(comp)
        if x in (None, "0", "0.0000") or total in values.get(d, {}) or cur in values.get(d, {}):
            continue
        for d2, v2 in values.items():
            if d2 != d and comp not in v2 and total in v2 and cur in v2 and Decimal(v2[total]) - Decimal(v2[cur]) == Decimal(x):
                drop.add(comp)
    return drop


def fill_lease_from_earlier_copy(cik, d, adsh, day, rec, filings):
    """Debt Verifier traps NVDA 2017-01-29 and META 2025-12-31 (Ritwik items 3 and 6). The latest accepted print
    decides every value; but a latest copy that does not repeat a finance/capital lease figure (NVDA's FY2018
    10-K folds the 6 noncurrent capital lease into other liabilities; META's later 10-Q has no lease note) cannot
    be read as 'no lease'. When the debt lines of the latest copy and of the latest EARLIER-accepted copy that
    prints the lease figures are EQUAL (the record's debt members tag by tag, absent = absent, and the note LongTermDebt where both print it), the two copies print the same debt and only the lease detail differs: lease tags the latest copy
    lacks are taken from that earlier copy. Debt lines that differ -> nothing is filled (the caller then holds
    with latest_copy_lacks_note_finance_lease). Returns the tags filled, with their source accession."""
    cands = sorted((a for a in NOTE_LEASE.get((cik, d), set()) - {adsh} if ACCEPTED_OF.get(a, "") < ACCEPTED_OF.get(adsh, "")),
                   key=lambda a: ACCEPTED_OF[a], reverse=True)
    missing_any = [t for t in NOTE_LEASE_TAGS if t not in day]
    if not cands or not missing_any:
        return None
    src = cands[0]
    sv = {t: Decimal(v) for t, v in filings[src]["values"][d].items()}
    members = {m["tag"] for m in rec["members"] if m["class"] not in ("operating_lease", "finance_lease")}
    if any((day[t][0] if t in day else None) != sv.get(t) for t in members):
        return None
    # the note's LongTermDebt is compared only where both copies print it (a later copy may drop the note line)
    if any(t in day and t in sv and day[t][0] != sv[t] for t in NOTE_DEBT_TAGS):
        return None
    # a missing TOTAL is filled only when the latest copy prints nothing of that lease family: a latest copy that
    # prints current + noncurrent has the present value, and an earlier copy's total may be the GROSS minimum
    # payments (AMZN 2016: CapitalLeaseObligations 9,406 gross vs 4,000 + 5,080 present value; Verifier R51)
    fam = lambda t: "FinanceLease" if t.startswith("FinanceLease") else "CapitalLease"
    present = {fam(t) for t in NOTE_LEASE_TAGS if t in day}
    filled = {t: sv[t] for t in missing_any if t in sv and sv[t] not in (0,)
              and (t.endswith(("Current", "Noncurrent")) or fam(t) not in present)}
    for t, v in filled.items():
        day[t] = (v, True)
    return (src, sorted(filled)) if filled else None


def select_cells(filing_iter, records):
    """one filing per (cik, instant): the LATEST ACCEPTED filing that prints the instant on its balance-sheet
    face (FSN-STORE-DESIGN section 4: winner = latest accepted; an older vintage is never preferred).
    accepted = sub.accepted (FSN); filings without it fall back to filed, then accession, for a total order."""
    best, filings = {}, {}
    NOTE_LEASE.clear()
    ACCEPTED_OF.clear()
    for f in filing_iter:
        if f["cik"] not in records:
            continue
        filings[f["adsh"]] = f
        ACCEPTED_OF[f["adsh"]] = (f.get("accepted") or "", f["filed"], f["adsh"])
        # a FACE column only (design section 4): the balance sheet's own closing total is valued at the date.
        # Assets alone is not enough: a later 10-K's segment note prints total assets for earlier years.
        face_tags = {r["tag"] for r in f["bs"]}
        closing = [t for t in ("LiabilitiesAndStockholdersEquity", "LiabilitiesAndPartnersCapital") if t in face_tags] or ["Assets"]
        for d, vals in f["values"].items():
            if any(vals.get(t) not in (None, "0", "0.0000") for t in NOTE_LEASE_TAGS):
                NOTE_LEASE[(f["cik"], d)].add(f["adsh"])
            if d < CELL_FROM or not any(t in vals for t in closing):
                continue
            rank = (f.get("accepted") or "", f["filed"], f["adsh"])
            if ABLATE_FIRST_FILED:  # regression-gate ablation only (bs_port_gate.sh): the pre-review selection
                rank = (d == f["period"], not f["form"].endswith("/A"), f["filed"])
            if (f["cik"], d) not in best or rank > best[(f["cik"], d)][0]:
                best[(f["cik"], d)] = (rank, f["adsh"])
    return best, filings


def covering_record(records, cik, period_end):
    ym = period_end[:7]
    for rec in records.get(cik, []):
        if rec["period_from"][:7] <= ym <= rec["period_to"][:7]:
            return rec
    return None


def replay(records, best, filings, prod, prod_n):
    report = {"cells": [], "summary": defaultdict(int), "per_company": defaultdict(lambda: defaultdict(int))}
    for (cik, d), (_r, adsh) in sorted(best.items()):
        f = filings[adsh]
        period_end = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        ticker = records[cik][0]["company"]
        ignore = drop_misdated_lease_components(f["values"], d)
        day = {t: (Decimal(v), True) for t, v in f["values"][d].items() if t not in ignore}
        # the record covering the chosen filing's own period: that filing's face is the one the members name
        # (a later comparative column is printed under the later era's tags)
        own = f"{f['period'][:4]}-{f['period'][4:6]}-{f['period'][6:]}"
        rec = covering_record(records, cik, own)
        pv = (prod.get((cik, period_end)) if prod_n.get((cik, period_end)) == 1 else None) if prod is not None else None
        if rec is None:
            verdict = "no_covering_record"
            report["summary"][verdict] += 1
            report["per_company"][ticker][verdict] += 1
            report["cells"].append({"ticker": ticker, "cik": cik, "period_end": period_end, "accession": adsh, "verdict": verdict,
                                    "slot_lease_inclusive": None, "prod_value": str(pv) if pv is not None else None})
            continue
        filled_from = fill_lease_from_earlier_copy(cik, d, adsh, day, rec, filings)
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
        if filled_from:
            note_flag = f"lease_tags_from_earlier_copy:{filled_from[0]}:{'+'.join(filled_from[1])}"
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
        note_lease_negative = None
        if lease_in_notes:
            # OPTION (b), founder ruling 2026-11-04 (relayed by Dhairya): finance leases that sit only in the
            # notes, outside every member, are added to the lease-inclusive total from the SAME accession
            # (MSFT, META, AAPL, GOOG, NVDA). Total element first, else current + noncurrent; capital-lease
            # elements (pre-ASC 842) the same way. Borrowings-only is unchanged.
            # Only the part NO member already carries is added (review 2026-11-01: a face member
            # FinanceLeaseLiabilityNoncurrent 40 beside a note total FinanceLeaseLiability 55 adds 15, never 55).
            def pick(total, cur_, noncur):
                on_face = sum((day[t][0] for t in (cur_, noncur) if t in member_tags and t in day), Decimal(0))
                if total in member_tags:
                    # the TOTAL is itself a face member (review 2026-11-01: face FinanceLeaseLiability 45 + note
                    # current 5 must not add 45 again): the member already carries every finance lease
                    return Decimal(0), f"{total}(face member)"
                if total in day:
                    face_src = "+".join(t for t in (cur_, noncur) if t in member_tags and t in day)
                    return day[total][0] - on_face, total + (f"-{face_src}" if face_src else "")
                parts = [t for t in (cur_, noncur) if t in day and t not in member_tags]
                return (sum((day[t][0] for t in parts), Decimal(0)), "+".join(parts)) if parts else (None, None)
            v, src = pick("FinanceLeaseLiability", "FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent")
            if v is None:
                v, src = pick("CapitalLeaseObligations", "CapitalLeaseObligationsCurrent", "CapitalLeaseObligationsNoncurrent")
            if v is not None and v < -1:
                note_lease_negative = f"{src}={v}"  # the note total is below the face lease members: never subtract
            elif v and v > 1:
                lease_incl += v
                note_lease_added = str(v)
                note_flag = (note_flag + ";" if note_flag else "") + f"note_finance_lease_added:{src}={v}"
        verdict = None
        if ticker in COMPANY_HOLDS:
            verdict = COMPANY_HOLDS[ticker]
        elif lease_unread:
            verdict = "debt_lease_member_unverified"
        elif note_lease_negative:
            verdict = "note_finance_lease_below_face_members"
        elif (not any(t in day for t in NOTE_LEASE_TAGS) and not combined_sides
              and any(ACCEPTED_OF.get(a, "") < ACCEPTED_OF.get(adsh, "") for a in NOTE_LEASE.get((cik, d), set()) - {adsh})):
            # design section 4: the latest copy decides and is never replaced by an older one; a latest copy that
            # lacks the finance-lease figure an EARLIER-accepted copy of the same date prints cannot give the
            # lease-inclusive total (AAPL 2025-09-30: the 2026 10-Q comparative has no lease note, 1,230M)
            verdict = "latest_copy_lacks_note_finance_lease"
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
            verdict = ("publishable" if prod is None else
                       "prod_blank" if pv is None else "prod_agrees" if abs(pv - lease_incl) <= 1 else "prod_differs")
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
            "note_finance_lease_added": note_lease_added, "note_flag": note_flag,
            "note_finance_lease_negative": note_lease_negative})
    report["summary"] = dict(report["summary"])
    report["per_company"] = {k: dict(v) for k, v in report["per_company"].items()}
    return report


def write_report(report, out_path):
    json.dump(report, open(out_path, "w"), indent=1)
    print(json.dumps(report["summary"], indent=1))
    for t in sorted(report["per_company"]):
        print(t, dict(report["per_company"][t]))


def main(argv):
    if argv[1] == "--company":
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))  # -I drops the script directory
        # replay_debt_fsn.py --company <dir|parent|@list> <records.jsonl> <out.json> [prod_debt.jsonl.gz]
        import fsn_company_bs as fc
        records = load_records(argv[3])
        prod, prod_n = load_prod(argv[5] if len(argv) > 5 else None)
        best, filings = select_cells((f for d in fc.company_dir_list(argv[2]) for f in fc.instants(d, debt_only=True)), records)
        write_report(replay(records, best, filings, prod, prod_n), argv[4])
        return
    rec_path, inst_path, prod_path, out_path = argv[1:5]
    records = load_records(rec_path)
    prod, prod_n = load_prod(prod_path)
    best, filings = select_cells((json.loads(line) for line in gzip.open(inst_path, "rt")), records)
    write_report(replay(records, best, filings, prod, prod_n), out_path)


if __name__ == "__main__":
    main(sys.argv)
