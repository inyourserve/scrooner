"""Pilot report over the FSN store (design §7 step 5, gate G2; THE-PLAN §0 north star).

For each pilot company: the cells fsn_select produces, the sector template coverage over the
expected-period calendar (data-team/46-canonical-fact-v2/expected_periods_*.csv.gz), the metric
library (company × data point × era -> line, tag, label, calc parent, rule, evidence accession),
the company profile and the design §5 done-criteria counts that the store alone can answer.
Every template key that is neither valued nor reasoned is a gap with a cause class.

Templates follow data-team/strategy/SECTOR-TEMPLATES-2026-11-01.md §1-2 (a PROPOSAL: SIC proposes,
the statements decide), restricted to statement data points (metrics recompute from them).
"""

from __future__ import annotations

import csv
import gzip
import re
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.fsn_store import select as sel

FLOOR = date(2015, 1, 1)  # serving window (invariant I11)

INSTANT = {
    "total_assets_resolved",
    "total_liabilities_resolved",
    "stockholders_equity_resolved",
    "cash_and_equivalents_resolved",
    "total_debt_resolved",
    "current_assets_resolved",
    "current_liabilities_resolved",
}
GENERAL = (
    "revenue_sanity_resolved",
    "cost_of_revenue_resolved",
    "gross_profit_resolved",
    "operating_income_resolved",
    "income_before_tax_resolved",
    "income_tax_expense_resolved",
    "net_income_resolved",
    "basic_eps_resolved",
    "diluted_eps_resolved",
    "interest_expense_resolved",
    "total_assets_resolved",
    "total_liabilities_resolved",
    "stockholders_equity_resolved",
    "current_assets_resolved",
    "current_liabilities_resolved",
    "cash_and_equivalents_resolved",
    "total_debt_resolved",
    "cfo_resolved",
    "capex_resolved",
    "depreciation_and_amortization_resolved",
    "dividends_paid_resolved",
    "share_buybacks_resolved",
)
# sector -> data points OUT of the template (doc §2: OUT by evidence or by definition)
OUT = {
    "general": set(),
    # approval §8 (Ritwik 2026-11-01): A and C OUTs approved; B (current assets/liabilities for
    # banks, insurers, REITs) stays IN until the company step removes it per company
    "bank": {
        "cost_of_revenue_resolved",
        "gross_profit_resolved",
        "operating_income_resolved",
        "capex_resolved",
    },
    "insurer": {
        "cost_of_revenue_resolved",
        "gross_profit_resolved",
        "capex_resolved",
    },
    "equity_reit": {
        "gross_profit_resolved",
        "capex_resolved",
    },
    "utility": {"gross_profit_resolved"},
}
# IN only for a company that prints the line (doc §2 COND); a COND gap names that
COND = {
    "general": {"cost_of_revenue_resolved", "gross_profit_resolved"},
    "bank": {"depreciation_and_amortization_resolved"},
    "insurer": {"operating_income_resolved"},
    "equity_reit": {"cost_of_revenue_resolved"},
    "utility": {"cost_of_revenue_resolved"},
}
# sector rows whose definition is pending (doc §2 REP); never valued from the general line
# Dhairya 2026-11-01: bank revenue = the bank's printed total net revenue line (JPM "Total net
# revenue" = NII + noninterest revenue), so no sector row is definition-pending in the pilot
DEFINITION_PENDING: dict[str, set[str]] = {}


# not G2-eligible until the BS lane's port gate can fail (Ritwik/Dhairya 2026-11-01): balance-sheet
# cells (bs.jsonl from b0ac12d) and debt; reported apart, with the bs rule ids serving them
NOT_G2_ELIGIBLE = INSTANT | {"total_debt_resolved"}


def sector_of(sic: str | None) -> str:
    """doc §1: SIC proposes (the statements decide; the profile shows the SIC used)."""
    s = int(sic) if sic and sic.isdigit() else 0
    if s in (6021, 6022):
        return "bank"
    if s in (6311, 6321, 6331, 6351, 6361, 6399):
        return "insurer"
    if s == 6798:
        return "equity_reit"
    if s in (4911, 4922, 4923, 4924, 4931, 4932, 4941):
        return "utility"
    return "general"


def template(sector: str) -> list[str]:
    return [c for c in GENERAL if c not in OUT[sector]]


def store_keys(filings: list[sel.Filing], concept: str) -> list[tuple[str, date]]:
    """Expected keys from the stored filings themselves, for a company the calendar barely knows
    (XOM: its 2015-2025 history is under predecessor CIK 0000034088, not in core.period)."""
    keys: set[tuple[str, date]] = set()
    for f in filings:
        if f.period is None or f.period < FLOOR:
            continue
        if concept in INSTANT:
            keys.add(("I", f.period))
            continue
        keys.add(("Q", f.period))
        if f.form.startswith("10-K"):
            keys.add(("FY", f.period))
    return sorted(keys)


def _company_outs(path: Path | None) -> list[dict[str, str]]:
    if not path or not path.exists():
        return []
    with path.open() as fh:
        return list(csv.DictReader(fh))


def calendar_keys(path: Path, company_id: int, concept: str) -> list[tuple[str, date]]:
    """(grain, period_end) keys of one data point: FY/Q durations or instants, end >= FLOOR."""
    want = "instant" if concept in INSTANT else "duration"
    keys: set[tuple[str, date]] = set()
    with gzip.open(path, "rt") as fh:
        for r in csv.DictReader(fh):
            if int(r["company_id"]) != company_id or r["period_type"] != want:
                continue
            end = date.fromisoformat(r["period_end"])
            if end < FLOOR:
                continue
            grain = (
                "I"
                if want == "instant"
                else ("FY" if r["fiscal_period"] == "FY" else "Q")
            )
            keys.add((grain, end))
    return sorted(keys)


def _match(rows: list[dict[str, Any]], grain: str, end: date) -> dict[str, Any] | None:
    best = None
    for r in rows:
        if r["period_grain"] != grain:
            continue
        gap = abs((date.fromisoformat(r["fsn_end"]) - end).days)
        if gap <= 10 and (best is None or gap < best[0]):
            best = (gap, r)
    return best[1] if best else None


def library(conn: psycopg.Connection, company_id: int) -> list[dict[str, Any]]:
    """Company × data point × era: runs of filings (in period order) whose line for the data
    point has the same status, tag and label. Evidence = first and last accession of the run."""
    rows = conn.execute(
        """
        select cc.name, lm.status, lm.rule_id, l.stmt, l.report, l.line, t.tag, t.custom, l.plabel,
               f.accession, f.period, f.form,
               (select string_agg(distinct p.tag || case when a.weight < 0 then '(-)' else '' end, ',')
                  from fsn.calc_arc a join fsn.tag p on p.id = a.parent_tag_id
                 where a.filing_id = f.id and a.child_tag_id = l.tag_id) as calc_parent
        from fsn.line_map lm
        join fsn.line l using (filing_id, report, line)
        join fsn.tag t on t.id = l.tag_id
        join fsn.filing f on f.id = lm.filing_id
        left join analytics.canonical_concept cc on cc.id = lm.canonical_concept_id
        where f.company_id = %s and lm.status in ('mapped', 'combined', 'excluded') and cc.name is not null
        order by cc.name, f.period, f.accepted, l.report, l.line
        """,
        (company_id,),
    ).fetchall()
    eras: list[dict[str, Any]] = []
    for (
        name,
        status,
        rule_id,
        stmt,
        report,
        line,
        tag,
        custom,
        plabel,
        acc,
        period,
        form,
        parent,
    ) in rows:
        last = eras[-1] if eras else None
        sig = (name, status, tag, plabel)
        if last and last["_sig"] == sig:
            last["era_to"] = period
            last["evidence_last"] = acc
            last["filings"] += 1
            continue
        eras.append(
            {
                "_sig": sig,
                "data_point": name,
                "status": status,
                "stmt": stmt,
                "line": line,
                "tag": tag,
                "custom": custom,
                "plabel": plabel,
                "calc_parent": parent,
                "rule_id": rule_id,
                "era_from": period,
                "era_to": period,
                "evidence_first": acc,
                "evidence_last": acc,
                "filings": 1,
            }
        )
    for e in eras:
        e.pop("_sig")
    return eras


ABSENT_LINE_CONCEPTS = ("share_buybacks_resolved", "dividends_paid_resolved")
SHARE_PURCHASE_RX = re.compile(r"(purchas|acqui)\w*\b.*\b(shares?|stock)\b", re.I)


SHAPE_TAG = ("Abstract", "Table", "Axis", "Domain", "Member", "LineItems")
INV_TOTALS = (
    "NetCashProvidedByUsedInInvestingActivities",
    "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
)


def financing_rows(face_rows: list[tuple], lane: Any) -> list[tuple[str, str]] | None:
    """(tag, label) of the financing-section rows of ONE filing's primary cash-flow statement: the rows after the
    investing total up to the financing total, in printed line order (run 7's primary_face picks the report).
    None when the section cannot be located: then nothing is claimed about the filing. Section headers and
    table/axis rows are dropped; supplemental and non-cash rows sit after the financing total and never count."""
    face = {"f": list(face_rows)}
    lane.primary_face(face)
    rows = face["f"]  # (line, tag, label, custom, negating), primary report only
    inv = [i for i, r in enumerate(rows) if r[1] in INV_TOTALS]
    if not inv:
        return None
    fin = next(
        (i for i in range(inv[-1] + 1, len(rows)) if rows[i][1] in lane.FIN_TOTALS),
        None,
    )
    if fin is None:
        return None
    return [
        (t, lab)
        for _ln, t, lab, _cu, _ng in rows[inv[-1] + 1 : fin]
        if not t.endswith(SHAPE_TAG)
    ]


def definitional_exclusions(
    conn: psycopg.Connection, company_id: int
) -> dict[str, dict[tuple[str, date, int], list[int]]]:
    """concept -> (tag, ddate, qtrs) -> filing ids whose cash-flow detector held that tag's line because every
    family line of the filing is excluded by definition (`excluded_only:*`: tax withholding, SBC-plan purchases,
    NCI or preferred dividends). Verifier 2026-11-08: Brixmor's FY2015/FY2016 10-Ks label PaymentsForRepurchaseOf
    CommonStock "Repurchase of common shares in conjunction with equity award plans" (excluded); its FY2017 10-K
    reprints the same periods under the same tag as "Repurchase of common shares". The more specific label wins."""
    rows = conn.execute(
        """
        select lm.evidence->>'concept', t.tag, v.ddate, v.qtrs, lm.filing_id
        from fsn.line_map lm
        join fsn.line l using (filing_id, report, line)
        join fsn.tag t on t.id = l.tag_id
        join fsn.value v on v.filing_id = lm.filing_id and v.tag_id = l.tag_id
        join fsn.filing f on f.id = lm.filing_id
        where f.company_id = %s and lm.rule_id = 'cf.buybacks_dividends_held@1'
          and v.dim_id = 0 and v.coreg = '' and v.iprx = 0 and v.qtrs > 0 and v.value is not null
          and jsonb_array_length(lm.evidence->'held') > 0
          and not exists (
            select 1 from jsonb_array_elements_text(lm.evidence->'held') h where h not like 'excluded_only:%%'
          )
        """,
        (company_id,),
    ).fetchall()
    out: dict[str, dict[tuple[str, date, int], list[int]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for concept, tag, ddate, qtrs, fid in rows:
        out[concept][(tag, ddate, int(qtrs))].append(fid)
    return out


def classify_filing(face_rows: list[tuple], lane: Any) -> dict[str, list[str]]:
    """concept -> the lane classes of ONE filing's financing-section lines (pure; see cf_line_classes)."""
    out: dict[str, list[str]] = {c: [] for c in ABSENT_LINE_CONCEPTS}
    fin = financing_rows(face_rows, lane)
    if fin is None:
        return {c: ["no_financing_section"] for c in ABSENT_LINE_CONCEPTS}
    for tag, label in fin:
        d = lane.dividend_class(tag, label)
        if d and d != "excluded_noncash":
            out["dividends_paid_resolved"].append(d)
        if (
            lane.REPURCHASE_RX.search(label)
            or "Repurchase" in tag
            or "TreasuryStock" in tag
        ):
            b = lane.buyback_class(tag, label)
            if b:
                out["share_buybacks_resolved"].append(b)
        elif SHARE_PURCHASE_RX.search(label) and not re.match(
            r"\s*(proceeds|issuance|issue)\b", label, re.I
        ):
            # a purchase of shares the lane's repurchase test does not name ("Purchase of CP Common Shares"
            # under a custom tag): never evidence that no buyback line is printed, so no claim is made
            out["share_buybacks_resolved"].append("unclassified_share_line")
    return out


def cf_line_classes(
    conn: psycopg.Connection, company_id: int
) -> dict[str, dict[int, list[str]]]:
    """concept -> filing_id -> the run 7 lane classes of the financing-section lines of that filing's primary
    cash-flow statement (tag and label only; the lane's buyback_class / dividend_class, imported).
    Verifier 2026-11-08 (VERIFY-CF-GAPS-2026-11-08): section headers (Kraft Heinz), rows of other pages (Erie's
    related-party table), operating inflows ("Dividends received", Somnigroup) and supplemental non-cash items
    (BXP "declared but not paid") are never lines of the concept. A filing whose financing section cannot be
    located gets the marker `no_financing_section`: nothing is claimed. A buyback line counts only when the lane's
    repurchase test hits it; an unnamed share purchase blocks any claim (`unclassified_share_line`)."""
    from scrooner_pipeline.fsn_store.cf_detector import _lane  # noqa: PLC0415

    lane = _lane()
    rows = conn.execute(
        """select l.filing_id, l.report, l.line, t.tag, coalesce(l.plabel, ''), t.custom, l.negating
           from fsn.line l join fsn.tag t on t.id = l.tag_id
           join fsn.filing f on f.id = l.filing_id
           where f.company_id = %s and l.stmt = 'CF' and not l.inpth""",
        (company_id,),
    ).fetchall()
    by_filing: dict[int, list[tuple]] = defaultdict(list)
    for fid, rep, ln, tag, label, cu, ng in rows:
        by_filing[fid].append((rep, ln, tag, label, bool(cu), bool(ng)))
    out: dict[str, dict[int, list[str]]] = {
        c: defaultdict(list) for c in ABSENT_LINE_CONCEPTS
    }
    for fid, face_rows in by_filing.items():
        for c, classes in classify_filing(face_rows, lane).items():
            out[c][fid].extend(classes)
    return out


def report_company(
    conn: psycopg.Connection,
    company_id: int,
    calendar: Path,
    rule_concepts: set[str],
    period_rules: Path | None = None,
    company_outs: Path | None = None,
    note_sourced: Path | None = None,
    cleared_keys: Path | None = None,
) -> dict[str, Any]:
    cik, name, sic = conn.execute(
        "select cik, company_name, sic_code from core.company where id = %s",
        (company_id,),
    ).fetchone()
    sector = sector_of(sic)
    tmpl = template(sector)
    data = sel.load_company(conn, company_id)
    cells: list[dict[str, Any]] = []
    breaks: dict[str, list[str]] = {}
    excluded = definitional_exclusions(conn, company_id)
    for concept, prints in sorted(data["prints"].items()):
        unit = "USD/shares" if "eps" in concept else "USD"
        ex = excluded.get(concept, {})
        if ex:  # a period one filing excludes by its label is never filled by a relabelled copy of the same tag
            prints = [p for p in prints if (p.tag, p.ddate, p.qtrs) not in ex]
        cs = sel.select_concept(
            concept,
            prints,
            data["filings"],
            members=data["members"],
            unit=sel.FSN_UOM.get(unit, unit),
            derive=unit == "USD",
            residual_guard="revenue" in concept,
        )
        cs = sel.apply_period_rules(
            concept,
            cs,
            sel.load_period_rules(period_rules, company_id),
            instant=concept in INSTANT,
        )
        if ex:
            cs = cs + sel.excluded_period_cells(concept, cs, ex, data["filings"])
        cells.extend(sel.to_row(c, company_id, data["filings"], unit=unit) for c in cs)
        s = sel._Series(
            [p for p in prints if p.uom == sel.FSN_UOM.get(unit, unit)], data["filings"]
        )
        if s.breaks:
            breaks[concept] = sorted(data["filings"][f].accession for f in s.breaks)
    # approved company x concept pairs served from a NOTE fact where the face prints no line
    # (approval CSV: REJECT_NOTE_SOURCED_VALUE); keys that already have a face cell are kept
    # sole-debt: pending rows, and rows the Verifier passed as gross (label verified)
    note_pairs: dict[str, tuple[bool, bool]] = {}
    for r in _company_outs(note_sourced):
        if int(r["company_id"]) != company_id or r.get("approver_verdict") not in (
            "REJECT_NOTE_SOURCED_VALUE",
            "PENDING_SOLE_DEBT_INTEREST_RULE",
        ):
            continue
        passed = "PASS_AS_GROSS" in (r.get("approver_evidence") or "")
        pending = r.get("approver_verdict") == "PENDING_SOLE_DEBT_INTEREST_RULE"
        note_pairs[r["data_point"]] = (pending or passed, passed)
    cleared = {
        (r["accession"], date.fromisoformat(r["ddate"]), int(r["qtrs"])): (
            Decimal(r["stored_value"]),
            Decimal(r["cleared_value"]),
        )
        for r in _company_outs(cleared_keys)
        if int(r["company_id"]) == company_id
    }
    note_cells = 0
    for concept in sorted(note_pairs):
        taken = {
            (
                date.fromisoformat(r["fsn_end"]),
                {"FY": 4, "Q": 1, "I": 0}[r["period_grain"]],
            )
            for r in cells
            if r["data_point_name"] == concept
        }
        sole, verified = note_pairs[concept]
        got = sel.select_note_values(
            concept,
            sel.load_note_values(conn, company_id, concept, sole_debt=sole),
            data["filings"],
            taken,
            sole_debt=sole,
            label_verified=verified,
            cleared=cleared,
        )
        note_cells += sum(1 for c in got if c.state == "value")
        cells.extend(sel.to_row(c, company_id, data["filings"]) for c in got)
    line_classes = cf_line_classes(conn, company_id)
    lib = library(conn, company_id)
    mapped_points = {
        e["data_point"]
        for e in lib
        if e["status"] in ("mapped", "combined", "excluded")
    }
    by_point: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in cells:
        by_point[r["data_point_name"]].append(r)

    keys = valued = reasoned = 0
    gaps: list[dict[str, Any]] = []
    per_point: dict[str, dict[str, int]] = {}
    # SECTOR-TEMPLATES §4 step 2: a COND data point the company's statements do not print (no line
    # mapped, combined or excluded in any stored filing) is OUT of that company's template, with that
    # reason; it leaves the denominator and is listed, never silently dropped
    cond_out = [c for c in tmpl if c in COND[sector] and c not in mapped_points]
    # company-level OUT from evidence that the statements print no such line
    # (data-team/47-fsn-store/template_company_outs.csv: no operating-income line, net interest only)
    # approval CSV: APPROVE_OUT -> out; APPROVE_OUT_FROM -> keys after out_effective_after are out;
    # REJECT_NOTE_SOURCED_VALUE -> stays IN (served from the note); a file without verdicts = all OUT
    company_out: dict[str, str] = {}
    out_after: dict[str, date] = {}
    for r in _company_outs(company_outs):
        if int(r["company_id"]) != company_id or r["data_point"] not in tmpl:
            continue
        verdict = r.get("approver_verdict") or "APPROVE_OUT"
        if verdict == "APPROVE_OUT":
            company_out[r["data_point"]] = r["reason"]
        elif verdict == "APPROVE_OUT_FROM" and r.get("out_effective_after"):
            out_after[r["data_point"]] = date.fromisoformat(r["out_effective_after"])
    tmpl = [c for c in tmpl if c not in cond_out and c not in company_out]
    for concept in tmpl:
        k: Counter[str] = Counter()
        expected = calendar_keys(calendar, company_id, concept)
        if len(expected) < 8:
            expected = store_keys(list(data["filings"].values()), concept)
        if concept in out_after:  # the line stopped being printed: later keys are out
            expected = [(g, e) for g, e in expected if e <= out_after[concept]]
        for grain, end in expected:
            keys += 1
            k["keys"] += 1
            row = _match(by_point.get(concept, []), grain, end)
            if row is None and concept in line_classes and grain in ("FY", "Q"):
                c = sel.absent_line_cell(
                    concept, grain, end, data, line_classes[concept]
                )
                if c is not None:
                    row = sel.to_row(c, company_id, data["filings"])
                    cells.append(row)
                    by_point[concept].append(row)
            if row and row["state"] in ("value", "derived"):
                valued += 1
                k["valued"] += 1
                continue
            if row:
                reasoned += 1
                k["reasoned"] += 1
                continue
            if concept in DEFINITION_PENDING.get(sector, set()):
                cause = "sector_row_definition_pending"
            elif concept not in rule_concepts:
                cause = "no_concept_rule"
            elif concept not in mapped_points:
                cause = "no_mapped_line" + ("_cond" if concept in COND[sector] else "")
            elif grain == "Q" and concept not in INSTANT:
                cause = "quarter_not_printed_or_derivable"
            else:
                cause = "no_face_print_for_period"
            k[cause] += 1
            gaps.append(
                {
                    "data_point": concept,
                    "grain": grain,
                    "period_end": end.isoformat(),
                    "cause": cause,
                }
            )
        per_point[concept] = dict(k)

    filings = data["filings"].values()
    latest = max(filings, key=lambda f: f.accepted) if filings else None
    combined = conn.execute(
        """
        select distinct t.tag, l.plabel from fsn.line_map lm join fsn.line l using (filing_id, report, line)
        join fsn.tag t on t.id = l.tag_id join fsn.filing f on f.id = lm.filing_id
        where f.company_id = %s and lm.status = 'combined'
        """,
        (company_id,),
    ).fetchall()
    coreg = conn.execute(
        "select distinct unnest(aciks) from fsn.filing where company_id = %s",
        (company_id,),
    ).fetchall()
    fye = conn.execute(
        "select fye from fsn.filing where company_id = %s order by accepted desc limit 1",
        (company_id,),
    ).fetchone()
    load_row = conn.execute(
        "select input_sha256, row_counts from fsn.company_load where company_id = %s",
        (company_id,),
    ).fetchone()
    lib_points = [c for c in tmpl if c in mapped_points]
    valued_points = {
        r["data_point_name"] for r in cells if r["state"] in ("value", "derived")
    }
    bs_rules_serving = sorted(
        {
            e["rule_id"]
            for e in lib
            if e["status"] == "mapped"
            and e["rule_id"]
            and e["rule_id"].startswith("bs.")
            and e["data_point"] in valued_points
        }
    )
    eligible: Counter[str] = Counter()
    for concept, counts in per_point.items():
        tag = "not_g2_eligible" if concept in NOT_G2_ELIGIBLE else "g2_eligible"
        eligible[tag + "_keys"] += counts.get("keys", 0)
        eligible[tag + "_valued"] += counts.get("valued", 0)
    states = Counter(r["state"] for r in cells)
    return {
        "company_id": company_id,
        "cik": cik,
        "name": name,
        "profile": {
            "sic": sic,
            "sector_template": sector,
            "template_points": len(tmpl),
            "template_out_cond_not_printed": cond_out,
            "template_out_by_company_evidence": company_out,
            "template_out_after": {k: v.isoformat() for k, v in out_after.items()},
            "note_sourced_points": sorted(note_pairs),
            "note_sourced_cells": note_cells,
            "fye": fye[0] if fye else None,
            "co_registrants": sorted(c[0] for c in coreg if c[0]),
            "filings_stored": len(data["filings"]),
            "latest_filing": latest.accession if latest else None,
            "restatement_breaks": {k: len(v) for k, v in breaks.items()},
            "restatement_break_accessions": breaks,
            "combined_lines": [{"tag": t, "label": lbl} for t, lbl in combined],
        },
        "template_coverage": {
            "keys": keys,
            "valued": valued,
            "reasoned": reasoned,
            "gaps": len(gaps),
            "valued_pct": round(100 * valued / keys, 1) if keys else None,
            "valued_or_reasoned_pct": round(100 * (valued + reasoned) / keys, 1)
            if keys
            else None,
            "per_data_point": per_point,
            "g2_eligibility": dict(eligible),
            "not_g2_eligible_points": sorted(c for c in tmpl if c in NOT_G2_ELIGIBLE),
            "bs_rule_ids_serving_cells": bs_rules_serving,
        },
        "library": {
            "template_points": len(tmpl),
            "with_line": len(lib_points),
            "completeness_pct": round(100 * len(lib_points) / len(tmpl), 1)
            if tmpl
            else None,
            "missing": [c for c in tmpl if c not in mapped_points],
            "eras": len(lib),
        },
        "done_criteria": {
            "1_store_loaded": bool(load_row),
            "1_row_counts": load_row[1] if load_row else None,
            "3_served_from_passing_columns": sum(
                1 for r in cells if r["state"] in ("value", "derived")
            ),
            "3_blanked_latest_copy_fails_identity": sum(
                1 for r in cells if r.get("reason_code") == "latest_copy_fails_identity"
            ),
            "4_reasonless_template_keys": len(gaps),
            "5_derived_without_same_basis": sum(
                1
                for r in cells
                if r["state"] == "derived"
                and (r.get("derivation") or {}).get("policy") != "same_basis"
            ),
            "6_proof_disagree": "after the write: cell_proof runs on written cells",
        },
        "cell_states": dict(states),
        "_cells": cells,
        "_gaps": gaps,
        "_library": lib,
    }


def done_gate(
    reports: list[dict[str, Any]],
    gaps: list[dict[str, str]],
    missing_filings: dict[str, list[Any]],
    data_points: set[str],
) -> dict[int, list[str]]:
    """Design §5 done criteria 1-5 per company, for the data points a write switches: {company_id: failed
    criteria}; an empty list means the company may switch. Criterion 3 holds by construction (select serves
    only passing columns; a failing latest copy is a reasoned blank). Criterion 6 (zero served cell_proof
    DISAGREE) needs the written cells: checked after the write, and a failing company is restored from its
    before-image (`scrooner-cells restore`), so it keeps its earlier rows (§7.6)."""
    reasonless: Counter[str] = Counter(
        str(g["company_id"]) for g in gaps if g["data_point"] in data_points
    )
    out: dict[int, list[str]] = {}
    for r in reports:
        crit = r["done_criteria"]
        failed = []
        if not crit.get("1_store_loaded"):
            failed.append("1_store_not_loaded")
        if missing_filings.get(r["cik"]):
            failed.append(f"2_filings_not_stored:{len(missing_filings[r['cik']])}")
        if reasonless[str(r["company_id"])]:
            failed.append(f"4_reasonless_keys:{reasonless[str(r['company_id'])]}")
        if crit.get("5_derived_without_same_basis"):
            failed.append(
                f"5_derived_without_same_basis:{crit['5_derived_without_same_basis']}"
            )
        out[r["company_id"]] = failed
    return out
