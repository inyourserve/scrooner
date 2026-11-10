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
from collections import Counter, defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.common.cell_contract import TP_QTRS, duration_class
from scrooner_pipeline.common.fsn_dates import fsn_end_matches, nearest_month_ends
from scrooner_pipeline.common.history_floor import HISTORY_FLOOR
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


def _row_class(r: dict[str, Any]) -> str | None:
    """The duration class of a cell row: its grain, or for a TP row (CELL-FORMAT v1.2) H1/9M/MULTI from its exact
    dates when it has them, else from its column length (qtrs 2 = H1, 3 = 9M)."""
    if r["period_grain"] != "TP":
        return r["period_grain"]
    if r.get("period_start") and r.get("period_end"):
        return duration_class(
            "duration",
            date.fromisoformat(str(r["period_start"])),
            date.fromisoformat(str(r["period_end"])),
        )
    return TP_QTRS.get(r.get("qtrs"))


def _match(
    rows: list[dict[str, Any]], grain: str, end: date, start: date | None = None
) -> dict[str, Any] | None:
    """The row of this duration class whose FSN end stands for the true period end `end` (within 10 days, or the
    SEC's month-end rounding of it: a mid-month 52/53-week end); the nearest wins. A row with exact dates (a TP
    blank of a before-image key) matches only its own start, when `start` is given."""
    best = None
    for r in rows:
        if _row_class(r) != grain:
            continue
        if (
            start is not None
            and r.get("period_start")
            and date.fromisoformat(str(r["period_start"])) != start
        ):
            continue
        fsn_end = date.fromisoformat(r["fsn_end"])
        if not fsn_end_matches(fsn_end, end):
            continue
        gap = abs((fsn_end - end).days)
        if best is None or gap < best[0]:
            best = (gap, r)
    return best[1] if best else None


RULE_GAP_BLANK = "fsn.hybrid_gap_blank@1"
GRAIN_QTRS = {"FY": 4, "Q": 1, "I": 0, "H1": 2, "9M": 3}
YTD_CLASSES = ("H1", "9M", "MULTI")


def gap_blank(
    concept: str,
    grain: str,
    end: date,
    cause: str,
    filings: dict[int, Any],
    start: date | None = None,
) -> "sel.Cell":
    """A pilot gap key as a reasoned blank, so a written pair carries every expected key (founder 2026-11-09:
    no fallback; a reasonless gap is written as a blank with a visible reason, never skipped).
    filing_not_in_store when no stored filing's period is this period end (FSN's month-end rounding included);
    else hybrid_gap_unresolved, with the pilot's cause in input_refs. The key's date is the FSN month-end form of the
    true end, like every other cell (the loader binds it to the true core.period by fiscal label).
    grain H1/9M/MULTI (CELL-FORMAT v1.2): a year-to-date or multi-year key with nothing printed; `start` is then
    required and the cell is a TP blank carrying the key's exact dates (a YTD period has no fiscal label)."""
    if grain in YTD_CLASSES and start is None:
        raise ValueError(f"a {grain} gap blank needs the key's exact start date")
    stored = sorted(
        (f.accepted, fid)
        for fid, f in filings.items()
        if f.period is not None and fsn_end_matches(f.period, end)
    )
    ends = sorted(nearest_month_ends(end))
    ddate = end if end in ends else ends[-1]
    refs = {"pilot_cause": cause, "expected_end": end.isoformat()}
    if (
        stored
    ):  # N1: the accession of the filing that reports the period (its latest copy)
        refs["accession"] = filings[stored[-1][1]].accession
    ytd_start = start if grain in YTD_CLASSES else None
    if ytd_start is not None:
        refs["expected_start"] = ytd_start.isoformat()
    if grain in GRAIN_QTRS:
        qtrs = GRAIN_QTRS[grain]
    else:  # a multi-year key: its length in quarters (at least 5, so it never reads as a year)
        assert ytd_start is not None
        qtrs = max(5, round(((end - ytd_start).days + 1) / 91.3))
    return sel.Cell(
        concept,
        ddate,
        qtrs,
        "defect",
        filing_id=stored[-1][1] if stored else None,
        rule_id=RULE_GAP_BLANK,
        reason_code="hybrid_gap_unresolved" if stored else "filing_not_in_store",
        input_refs=refs,
        start=ytd_start,
        end=end if ytd_start is not None else None,
    )


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
    for concept, prints in sorted(data["prints"].items()):
        unit = "USD/shares" if "eps" in concept else "USD"
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
                r["qtrs"],
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
    gap_rows: list[
        dict[str, Any]
    ] = []  # each gap key as a reasoned blank (no fallback: founder 2026-11-09)
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
            blank = gap_blank(concept, grain, end, cause, data["filings"])
            gap_rows.append(sel.to_row(blank, company_id, data["filings"]))
            gaps.append(
                {
                    "data_point": concept,
                    "grain": grain,
                    "period_end": end.isoformat(),
                    "cause": cause,
                    "written_as": blank.reason_code,
                }
            )
        per_point[concept] = dict(k)

    cells.extend(gap_rows)
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
            # the same count per data point: the done gate counts only the data points a write switches
            "5_derived_without_same_basis_by_point": dict(
                Counter(
                    r["data_point_name"]
                    for r in cells
                    if r["state"] == "derived"
                    and (r.get("derivation") or {}).get("policy") != "same_basis"
                )
            ),
            "6_proof_disagree": "after the write: cell_proof runs on written cells",
        },
        "cell_states": dict(states),
        # the stored filings, so the done gate can build N1 gap blanks for before-image YTD keys (CELL-FORMAT v1.2)
        "store_filings": [
            {
                "id": f.id,
                "accession": f.accession,
                "accepted": f.accepted.isoformat(),
                "form": f.form,
                "period": f.period.isoformat() if f.period else None,
                "fy": f.fy,
                "fp": f.fp,
                "fye": f.fye,
            }
            for f in data["filings"].values()
        ],
        "_cells": cells,
        "_gaps": gaps,
        "_library": lib,
    }


VALUED_STATES = ("value", "derived")


def done_gate(
    reports: list[dict[str, Any]],
    gaps: list[dict[str, str]],
    missing_filings: dict[str, list[Any]],
    data_points: set[str],
) -> dict[int, dict[str, Any]]:
    """The done gate under the founder's no-fallback decision (2026-11-09: "No fallback. Everything is the hybrid"),
    on Ritwik's per-pair ruling (RULING-DONE-GATE-C4-2026-11-09, C1 atomicity per (company, concept)):
    {company_id: {"company": [failed criteria 1/2/5], "data_points": {dp: [reasons]}, "out_of_template": [dp],
    "gap_blanks": {dp: n}}}.

    Criteria 1, 2 and 5 stay per company: a structural failure writes nothing for that company (every pair carries
    `company:<criterion>`). Otherwise EVERY data point of the list that is in the company's template is written,
    all keys at once: values, reasoned blanks, and each pilot gap key as a reasoned blank (`gap_blank`), so no old
    row of a written pair survives. Criterion 4 no longer holds a pair back; its gap keys are counted under
    "gap_blanks". A pair with no expected key (nothing to write) and a data point outside the template are not
    written and are listed. Criterion 5 counts the derived cells of the switched data points only."""
    gap_keys: Counter[tuple[str, str]] = Counter(
        (str(g["company_id"]), g["data_point"])
        for g in gaps
        if g["data_point"] in data_points
    )
    out: dict[int, dict[str, Any]] = {}
    for r in reports:
        crit = r["done_criteria"]
        cid = r["company_id"]
        company: list[str] = []
        if not crit.get("1_store_loaded"):
            company.append("1_store_not_loaded")
        if missing_filings.get(r["cik"]):
            company.append(f"2_filings_not_stored:{len(missing_filings[r['cik']])}")
        by_point = crit.get("5_derived_without_same_basis_by_point")
        derived = (
            sum(n for dp, n in by_point.items() if dp in data_points)
            if by_point is not None
            else crit.get("5_derived_without_same_basis", 0)
        )
        if derived:
            company.append(f"5_derived_without_same_basis:{derived}")
        per_point = (r.get("template_coverage") or {}).get("per_data_point") or {}
        points: dict[str, list[str]] = {}
        out_of_template: list[str] = []
        blanks: dict[str, int] = {}
        for dp in sorted(data_points):
            if dp not in per_point:
                out_of_template.append(dp)
                continue
            failed = [f"company:{c}" for c in company]
            if not per_point[dp].get("keys", 0):
                failed.append("no_expected_keys")  # nothing to write
            n = gap_keys[(str(cid), dp)]
            if n:
                blanks[dp] = n
            points[dp] = failed
        out[cid] = {
            "company": company,
            "data_points": points,
            "out_of_template": out_of_template,
            "gap_blanks": blanks,
        }
    return out


def done_pairs(gate: dict[int, dict[str, Any]]) -> list[tuple[int, str]]:
    """The (company_id, data point) pairs that may be written."""
    return sorted(
        (cid, dp)
        for cid, g in gate.items()
        for dp, failed in g["data_points"].items()
        if not failed
    )


def fully_done(gate: dict[int, dict[str, Any]]) -> list[int]:
    """Companies whose every listed (in-template) pair passes, with at least one such pair."""
    return sorted(
        cid
        for cid, g in gate.items()
        if g["data_points"] and not any(g["data_points"].values())
    )


def _grain(period_type: str, start: date, end: date) -> str:
    """The duration class of a stored period: I, Q (about 3 months), H1 (6-month YTD), 9M (9-month YTD), FY, or
    MULTI (longer than a year). A 6/9-month row must never be counted as matched by the Q cell that ends on the
    same day (MDT 2026-11-09: 170 YTD values deleted unseen); since CELL-FORMAT v1.2 it is matched by a TP cell of
    its own class."""
    return duration_class(period_type, start, end)


CELL_GRAINS = ("Q", "FY", "I", "H1", "9M", "MULTI")


def hold_guard(
    cells: list[dict[str, Any]],
    before: list[dict[str, str]],
    concept_names: dict[str, str],
    periods: dict[str, dict[str, str]],
    data_points: set[str],
) -> tuple[
    dict[tuple[int, str], str],
    dict[str, dict[str, int]],
    list[dict[str, Any]],
]:
    """C2 (Ritwik 2026-11-10): the expected keys of a written pair are its calendar keys AND every key the
    before-image held a value for. Returns (pairs losing every value, valued->X transitions per data point,
    the valued->no-row keys).

    before: the before-image canonical_fact rows (company_id, canonical_concept_id, period_id, value);
    concept_names: canonical_concept id -> name; periods: core.period id -> its row (start_date, end_date,
    period_type). For every before-image valued key the new cell is matched by duration class and an end within
    10 days: a 6-month, 9-month or multi-year key by a TP cell of its class (CELL-FORMAT v1.2; an exact-dated TP
    blank only at its own start). A blank new cell counts under its reason_code. A key with no new cell is
    valued->no-row: the loader replaces the pair's rows whole, so that value would vanish with no cell and no
    reason. Every such key is listed; the gate holds its pair."""
    new_valued: Counter[tuple[int, str]] = Counter()
    by_pair: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for r in cells:
        if r["data_point_name"] not in data_points:
            continue
        key = (int(r["company_id"]), r["data_point_name"])
        by_pair[key].append(r)
        if r["state"] in VALUED_STATES:
            new_valued[key] += 1
    old_valued: Counter[tuple[int, str]] = Counter()
    transitions: dict[str, Counter[str]] = defaultdict(Counter)
    no_row: list[dict[str, Any]] = []
    for b in before:
        dp = concept_names.get(str(b["canonical_concept_id"]))
        if dp not in data_points or b.get("value") in (None, ""):
            continue
        key = (int(b["company_id"]), dp)
        p = periods.get(str(b["period_id"]))
        if p is None:
            old_valued[key] += 1
            transitions[dp]["period_unknown"] += 1
            no_row.append(
                {"company_id": key[0], "data_point": dp, "period_id": b["period_id"],
                 "grain": None, "start": None, "end": None, "before_value": b["value"], "why": "period_unknown"}
            )  # fmt: skip
            continue
        start, end = (
            date.fromisoformat(p["start_date"]),
            date.fromisoformat(p["end_date"]),
        )
        if (
            end < HISTORY_FLOOR
        ):  # the write does not reach keys before the history floor (CELL-FORMAT §2)
            continue
        old_valued[key] += 1
        grain = _grain(p["period_type"], start, end)
        row = _match(
            by_pair.get(key, []), grain, end, start if grain in YTD_CLASSES else None
        )
        if row is None:
            why = "no_new_cell"
            transitions[dp][why] += 1
            no_row.append(
                {"company_id": key[0], "data_point": dp, "period_id": b["period_id"], "grain": grain,
                 "start": start.isoformat(), "end": end.isoformat(), "before_value": b["value"], "why": why}
            )  # fmt: skip
        elif row["state"] not in VALUED_STATES:
            transitions[dp][row.get("reason_code") or row["state"]] += 1
        else:
            transitions[dp]["valued"] += 1
    held = {
        key: f"0_new_values_vs_{n}_before"
        for key, n in old_valued.items()
        if n and not new_valued[key]
    }
    return held, {dp: dict(c) for dp, c in transitions.items()}, no_row


def _store_filings(report: dict[str, Any]) -> dict[int, sel.Filing] | None:
    rows = report.get("store_filings")
    if rows is None:
        return None
    return {
        int(f["id"]): sel.Filing(
            int(f["id"]),
            f["accession"],
            datetime.fromisoformat(f["accepted"]),
            f["form"],
            date.fromisoformat(f["period"]) if f.get("period") else None,
            f.get("fy"),
            f.get("fp"),
            f.get("fye"),
        )
        for f in rows
    }


def ytd_gap_blanks(
    cells: list[dict[str, Any]],
    before: list[dict[str, str]],
    concept_names: dict[str, str],
    periods: dict[str, dict[str, str]],
    data_points: set[str],
    reports: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """CELL-FORMAT v1.2 (release approver 2026-11-10): a before-image valued key of a 6-month, 9-month or multi-year
    period (no calendar row expects one) with no TP cell, because nothing is printed on the face for it, becomes a
    defect blank under the pilot.gap_blank conventions (N1): hybrid_gap_unresolved when a stored filing reports the
    period end (its accession in input_refs), else filing_not_in_store; the cause is no_mapped_line when the
    company's library has no line for the data point, else no_face_print_for_period. The blank carries the key's
    exact dates. Returns (blank rows, skipped keys): a company whose report lacks its stored filings gets no blank
    (its keys stay valued->no-row and the gate holds the pair)."""
    by_pair: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for r in cells:
        by_pair[(int(r["company_id"]), r["data_point_name"])].append(r)
    by_company = {int(r["company_id"]): r for r in reports}
    out: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    seen: set[tuple[int, str, date, date]] = set()
    filings_of: dict[int, dict[int, sel.Filing] | None] = {}
    for b in before:
        dp = concept_names.get(str(b["canonical_concept_id"]))
        if dp not in data_points or b.get("value") in (None, ""):
            continue
        p = periods.get(str(b["period_id"]))
        if p is None:
            continue
        start, end = (
            date.fromisoformat(p["start_date"]),
            date.fromisoformat(p["end_date"]),
        )
        grain = _grain(p["period_type"], start, end)
        cid = int(b["company_id"])
        if end < HISTORY_FLOOR or grain not in YTD_CLASSES:
            continue
        if (cid, dp, start, end) in seen or _match(
            by_pair.get((cid, dp), []), grain, end, start
        ):
            continue
        seen.add((cid, dp, start, end))
        report = by_company.get(cid)
        if cid not in filings_of:
            filings_of[cid] = _store_filings(report) if report else None
        filings = filings_of[cid]
        if report is None or filings is None:
            skipped.append(
                {"company_id": cid, "data_point": dp, "start": start.isoformat(), "end": end.isoformat(),
                 "why": "no_store_filings_in_report"}
            )  # fmt: skip
            continue
        missing = set((report.get("library") or {}).get("missing") or [])
        cause = "no_mapped_line" if dp in missing else "no_face_print_for_period"
        blank = gap_blank(dp, grain, end, cause, filings, start=start)
        row = sel.to_row(blank, cid, filings)
        by_pair[(cid, dp)].append(row)
        out.append(row)
    return out, skipped


def hold_valued_to_no_row(
    gate: dict[int, dict[str, Any]], no_row: list[dict[str, Any]]
) -> dict[tuple[int, str], int]:
    """Hold every pair with a valued->no-row key (it must be 0 for a written pair); returns the count per pair."""
    counts: Counter[tuple[int, str]] = Counter(
        (int(k["company_id"]), k["data_point"]) for k in no_row
    )
    for (cid, dp), n in counts.items():
        g = gate.get(cid)
        if g is not None and dp in g["data_points"]:
            g["data_points"][dp].append(f"C2_valued_to_no_row:{n}")
    return dict(counts)


RULE_PROOF_BLANK = "fsn.cell_proof_blank@1"


def blank_disagreements(
    rows: list[dict[str, Any]], disagrees: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Ruling addendum N2 (no fallback): a written cell that cell_proof DISAGREEs with becomes a defect blank
    (identity / verifier, reason cell_proof_disagree, the proof evidence in input_refs) instead of being restored
    to its old value. Returns (rows to load, unmatched DISAGREE rows).

    The loader replaces a written (company, data point) pair WHOLE, so the result holds EVERY row of each pair with
    at least one DISAGREE key, with only those keys replaced; pairs without a DISAGREE are not reloaded. A DISAGREE
    row matches a written cell by company, data point, grain and end (FSN month-end rounding included)."""
    by_pair: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_pair[(int(r["company_id"]), r["data_point_name"])].append(r)
    hits: dict[int, dict[str, Any]] = {}  # id(row) -> the DISAGREE it matched
    unmatched = []
    for d in disagrees:
        pair = (int(d["company_id"]), d["data_point_name"])
        end = (
            d["period_end"]
            if isinstance(d["period_end"], date)
            else date.fromisoformat(str(d["period_end"]))
        )
        cands = [
            r
            for r in by_pair.get(pair, [])
            if r["period_grain"] == d["period_grain"]
            and fsn_end_matches(date.fromisoformat(r["fsn_end"]), end)
        ]
        if not cands:
            unmatched.append(d)
            continue
        best = min(
            cands, key=lambda r: abs((date.fromisoformat(r["fsn_end"]) - end).days)
        )
        hits[id(best)] = d
    out = []
    for pair, prs in sorted(by_pair.items()):
        if not any(id(r) in hits for r in prs):
            continue
        for r in prs:
            d = hits.get(id(r))
            if d is None:
                out.append(r)
                continue
            out.append(
                dict(
                    r,
                    state="defect",
                    value=None,
                    unit=None,
                    derivation=None,
                    source_fact_ids=[],
                    source_value_ids=[],
                    rule_id=RULE_PROOF_BLANK,
                    reason_code="cell_proof_disagree",
                    reason_text=sel.REASON_TEXT["cell_proof_disagree"],
                    defect_class="identity",
                    owner="verifier",
                    root_cause_class=None,
                    input_refs={
                        "cell_proof_id": d.get("id"),
                        "proof_reason_code": d.get("reason_code"),
                        "proof_rule_id": d.get("rule_id"),
                        "shown_value": None
                        if d.get("shown_value") is None
                        else str(d["shown_value"]),
                        "position_value": None
                        if d.get("position_value") is None
                        else str(d["position_value"]),
                        "replaced_value": r.get("value"),
                        "replaced_rule_id": r.get("rule_id"),
                        "replaced_state": r.get("state"),
                    },
                )
            )
    return out, unmatched
