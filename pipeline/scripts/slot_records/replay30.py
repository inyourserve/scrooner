"""Replay the 30-company-set slot records against lane 3's before-images.

For every lane 3 total_debt row (cik, period_end, before/after/hold) in the
2015+ data window, compute the slot values from stored facts:
  lease_inclusive = borrowing + combined + finance_lease members
  borrowings_only = lease_inclusive - finance-lease content (explicit members,
                    plus the same-side lease fact inside 'combined' members)
Operating-lease members are excluded from both variants (standardization card).
Values prefer authoritative facts; a non-authoritative fallback is flagged.

Read-only: one DB connection, SELECTs only.
usage: DATABASE_URL=... replay30.py <records.jsonl> <lane3_dir> <out_report.json>
"""
import json
import re
import os
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import psycopg

LEASE_TAGS = {
    "cur": ["FinanceLeaseLiabilityCurrent", "CapitalLeaseObligationsCurrent"],
    "noncur": ["FinanceLeaseLiabilityNoncurrent", "CapitalLeaseObligationsNoncurrent"],
}
# The filer's own printed debt aggregates confirm a missing member is a
# face blank (zero), not a data gap (Verifier V2 fix 6: ABBV 2015-06-30).
AGG_TAGS = ["DebtAndCapitalLeaseObligations", "DebtLongtermAndShorttermCombinedAmount"]

records = defaultdict(list)
for line in open(sys.argv[1]):
    r = json.loads(line)
    records[r["cik"]].append(r)

lane3 = []
for fn in Path(sys.argv[2]).glob("debt_v4_MORE*"):
    for line in open(fn):
        r = json.loads(line)
        lane3.append(r)
# one row per (cik, period, variant-file) -> dedupe to (cik, period): keep both variants' before
by_cell = {}
for r in lane3:
    key = (r["cik"], r["period_end"])
    by_cell.setdefault(key, []).append(r)
# Verifier value anchors are evaluated even when lane 3 has no row there.
anchor_keys: set = set()
anchors_path = Path(sys.argv[1]).parent / "results" / "expected_values.json"
if not anchors_path.exists():
    anchors_path = Path(sys.argv[1]).parent / "expected_values.json"
if anchors_path.exists():
    tick2cik = {}
    for recs in records.values():
        for r in recs:
            tick2cik[r["company"]] = r["cik"]
    anchor_keys = set()
    for a in json.loads(anchors_path.read_text())["anchors"]:
        cik = tick2cik.get(a["ticker"])
        if cik:
            by_cell.setdefault((cik, a["period_end"]), [])
            anchor_keys.add((cik, a["period_end"]))

def covering_record(cik, period_end):
    ym = period_end[:7]
    for rec in records.get(cik, []):
        if rec["period_from"][:7] <= ym <= rec["period_to"][:7]:
            return rec
    return None

def fetch_facts(cur, cik, tags):
    # Verifier D2: restrict facts to PERIODIC filings - the non-authoritative
    # fallback once took an 8-K recast copy (GE 2021-12-31: 35,114M from an
    # 8-K vs the 10-K face 35,185M).
    cur.execute(
        """
        select distinct on (co.tag, p.end_date) co.tag, p.end_date::text, f.value::numeric, f.is_authoritative
        from core.fact f
        join core.concept co on co.id = f.concept_id
        join core.period p on p.id = f.period_id
        join core.unit u on u.id = f.unit_id
        join core.company c on c.id = f.company_id
        join core.filing fi on fi.id = f.filing_id
        where c.cik = %s and p.period_type = 'instant' and co.taxonomy = 'us-gaap'
          and u.unit_name = 'usd' and co.tag = any(%s)
          and fi.form in ('10-K','10-Q','10-K/A','10-Q/A')
        order by co.tag, p.end_date, (fi.period_of_report = p.end_date) desc, f.is_authoritative desc, f.id desc
        """,
        (cik, list(tags)),
    )
    facts = defaultdict(dict)
    for tag, end_date, value, is_auth in cur.fetchall():
        facts[end_date][tag] = (value, is_auth)
    # custom-tag values from the filing's OWN instance (instance_reader.py),
    # same accession as the instant's original periodic filing only
    if instance_evidence:
        cur.execute(
            """select fi.accession_number, fi.period_of_report::text from core.filing fi
               join core.company c on c.id = fi.company_id
               where c.cik = %s and fi.form in ('10-K','10-Q') and fi.period_of_report >= '2015-01-01'""",
            (cik,),
        )
        for acc, por in cur.fetchall():
            for tag, v in instance_evidence.get((acc, por), {}).items():
                if tag in tags and tag not in facts[por]:
                    facts[por][tag] = (v, True)
                    facts[por].setdefault("__instance_filled__", ([], True))[0].append(tag)
    return facts

# optional 4th arg: instance-reader evidence JSONL -> (adsh, end) -> tag -> Decimal
instance_evidence = defaultdict(dict)
if len(sys.argv) > 4 and os.path.exists(sys.argv[4]):
    for line in open(sys.argv[4]):
        r = json.loads(line)
        if r.get("period_type") != "instant" or r.get("value") in (None, "") or (r.get("unit") or "USD") != "USD":
            continue
        try:
            instance_evidence[(r["adsh"], r["end"])].setdefault(r["tag"], Decimal(r["value"]))
        except Exception:  # noqa: BLE001
            continue

report = {"cells": [], "summary": defaultdict(int), "per_company": defaultdict(lambda: defaultdict(int))}
conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
for cik in sorted(records):
    tags = set()
    for rec in records[cik]:
        tags.update(m["tag"] for m in rec["members"])
        for m in rec["members"]:
            tie = m.get("tie") or {}
            tags.update(tie.get("roots", []))
            less = tie.get("less") or []
            tags.update([less] if isinstance(less, str) else less)
            if tie.get("total"):
                tags.add(tie["total"])
    tags.update(t for side in LEASE_TAGS.values() for t in side)
    tags.update(AGG_TAGS)
    tags.update(("LongTermDebt", "LongTermDebtCurrent"))  # debt-note carrying total + current portion (COST rule)
    facts = fetch_facts(cur, cik, tags)
    cells = [(k, v) for k, v in by_cell.items() if k[0] == cik]
    for (cik_, period_end), rows in sorted(cells):
        ticker = records[cik][0]["company"]
        if period_end < "2015-01-01" and (cik_, period_end) not in anchor_keys:
            verdict = "out_of_window_pre2015"
            report["summary"][verdict] += 1
            report["per_company"][ticker][verdict] += 1
            continue
        rec = covering_record(cik, period_end)
        if rec is None:
            verdict = "no_covering_record"
            report["summary"][verdict] += 1
            report["per_company"][ticker][verdict] += 1
            continue
        day = facts.get(period_end, {})
        lease_incl = Decimal(0)
        missing, missing_custom, nonauth = [], [], []
        combined_sides = set()
        for m in rec["members"]:
            if m["class"] == "operating_lease":
                continue
            if m["class"] == "combined":
                combined_sides.add("cur" if m["side"] == "current" else "noncur")
            if m["tag"] in day:
                v, auth = day[m["tag"]]
                lease_incl += v
                if not auth:
                    nonauth.append(m["tag"])
            elif m.get("custom"):
                # custom tags never reach the API: not a blank, a data gap that
                # only the filing instance can fill (Verifier V3: GE non-recourse
                # 3,083M, RPAY long-term debt 240.96M)
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
        # CURRENT MATURITIES IN A COMBINED LINE (Verifier V5, COST 2018-09-02:
        # face shows only LongTermDebtNoncurrent 6,487M; the debt note carries
        # 6,577M with a 90M current portion inside 'other current liabilities').
        # A record with NO current-maturities member never publishes the
        # noncurrent face figure as total debt: if the filer's own note total
        # (LongTermDebt) reconciles as noncurrent face + note current portion,
        # the current portion is added from the note (same accession, periodic
        # form); otherwise the cell holds as face_note_gap_review.
        note_current_added = None
        note_gap = False
        current_unverified = False
        has_current_ltd = any(
            m["side"] == "current" and re.search(r"LongTermDebt|DebtCurrent|CurrentPortion|Maturit", m["tag"])
            for m in rec["members"]
        )
        ltd_note = day.get("LongTermDebt")
        if not has_current_ltd and ltd_note is not None:
            noncur_ltd = sum(
                (day[m["tag"]][0] for m in rec["members"]
                 if m["side"] == "noncurrent" and m["tag"] in day and re.search(r"LongTermDebt", m["tag"])),
                Decimal(0),
            )
            ltd_cur = day.get("LongTermDebtCurrent")
            if abs(ltd_note[0] - noncur_ltd) <= 1:
                pass  # no current portion exists
            elif ltd_cur is not None and abs(noncur_ltd + ltd_cur[0] - ltd_note[0]) <= 1:
                lease_incl += ltd_cur[0]
                borrowings += ltd_cur[0]
                note_current_added = ltd_cur[0]
            else:
                note_gap = True
        elif has_current_ltd and ltd_note is not None:
            # both sides on the face: the long-term-debt members must still tie
            # to the filer's note carrying total (COST 2019-02-17: face 1,698 +
            # 4,794 = 6,492M vs note 6,525M); a gap goes to review, never shown
            ltd_face = sum(
                (day[m["tag"]][0] for m in rec["members"]
                 if m["tag"] in day and re.search(r"LongTermDebt", m["tag"]) and m["class"] != "operating_lease"),
                Decimal(0),
            )
            if abs(ltd_note[0] - ltd_face) > 1:
                note_gap = True
        elif not has_current_ltd and any(
            m["side"] == "noncurrent" and m["tag"] in day and re.search(r"LongTermDebt", m["tag"]) for m in rec["members"]
        ):
            # noncurrent long-term debt on the face, no current-maturities line,
            # and no note carrying total at this instant to prove there is no
            # current portion (COST 10-Qs): never publish the noncurrent figure
            # as total debt; hold for the Verifier / instance reader.
            current_unverified = True
        before_vals = {Decimal(r["before"]) for r in rows if r.get("before")}
        is_hold = any("hold" in (r.get("reason") or "") and not r.get("after") for r in rows)
        # Verifier: a missing member is a HARD STOP, never a silent zero
        # (it hid KO's custom 2014-18 line). Borrowings-only verdicts dropped:
        # the variant does not remove current finance leases inside non-combined
        # short-term lines (CVX 2022, LRCX) - it stays informational only.
        filer_agg = next((day[t][0] for t in AGG_TAGS if t in day), None)
        # FACE-ADMISSION VALUE TIE (Verifier V4 guard iv): a member admitted
        # from the face (not in the statement-role cal) is used only when its
        # zone roots sum to the filer's printed side total on this instant;
        # otherwise the cell holds. Rounding unit = the filer's (bs_replay rule).
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
        verdict = None
        # A verdict must NEVER depend on production's value: production is the
        # thing being replaced (Verifier V3 defect 1). A blank is accepted only
        # from the filing itself: the filer's own printed total ties.
        if not rec.get("coverage_clean", True):
            verdict = "not_computable_uncovered_candidates"
        elif missing_custom:
            verdict = "needs_instance_reader"
        elif tie_pending:
            verdict = "face_admission_tie_pending"
        elif missing and filer_agg is not None and abs(lease_incl - filer_agg) <= 1:
            pass  # the filer's own printed total confirms the blanks are zero
        elif missing:
            verdict = "not_computable_missing_member"
        elif not day:
            verdict = "not_computable_no_facts"
        elif note_gap:
            verdict = "face_note_gap_review"
        elif current_unverified:
            verdict = "current_maturities_unverified"
        elif filer_agg is not None and abs(lease_incl - filer_agg) > 1:
            # NOTE-TIE CHECK (Verifier V4: COST 2018-09-02 - a 90M current
            # portion folded into another face line is invisible to a
            # face-built record; only the debt note's carrying total shows
            # it). A gap between the era sum and the filer's own note
            # carrying total goes to review, never published either way.
            verdict = "face_note_gap_review"
        if verdict is None:
            if before_vals and any(abs(lease_incl - b) <= 1 for b in before_vals):
                verdict = "agrees_lease_inclusive"
            elif before_vals:
                verdict = "DISAGREES_with_lane3"
            else:
                verdict = "lane3_blank_slot_has_value"
        if is_hold and verdict in ("agrees_lease_inclusive", "DISAGREES_with_lane3", "lane3_blank_slot_has_value"):
            report["summary"]["holds_resolved_by_slot"] += 1
            report["per_company"][ticker]["holds_resolved_by_slot"] += 1
        report["summary"][verdict] += 1
        report["per_company"][ticker][verdict] += 1
        publishable = verdict not in (
            "needs_instance_reader", "not_computable_missing_member",
            "not_computable_no_facts", "not_computable_uncovered_candidates",
            "face_note_gap_review", "face_admission_tie_pending", "current_maturities_unverified",
        )
        report["cells"].append(
            {"ticker": ticker, "cik": cik, "period_end": period_end, "verdict": verdict,
             # a partial sum must be NULL on any non-publishable verdict:
             # nothing downstream may carry GE's 194,519M or RPAY's 5.5M
             "slot_lease_inclusive": str(lease_incl) if publishable else None,
             "slot_borrowings": str(borrowings) if publishable else None,
             "lane3_before": sorted(str(b) for b in before_vals), "hold": is_hold,
             "missing_members": missing, "missing_custom_members": missing_custom,
             "nonauth_members": nonauth, "face_admission_tie_pending": tie_pending,
             "note_current_portion_added": str(note_current_added) if note_current_added is not None else None}
        )
conn.close()
report["summary"] = dict(report["summary"])
report["per_company"] = {k: dict(v) for k, v in report["per_company"].items()}
json.dump(report, open(sys.argv[3], "w"), indent=1)
print(json.dumps(report["summary"], indent=1))
for t in sorted(report["per_company"]):
    print(t, dict(report["per_company"][t]))
