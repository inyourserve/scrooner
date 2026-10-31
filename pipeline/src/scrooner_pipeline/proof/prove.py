"""Verdict logic of the cell proof system (rule proof.cell_proof@1). Pure.

A displayed cell is PROVEN only when
  (a) the value production shows (analytics.canonical_fact, with its source tag
      and accession) equals, at the filer's own precision (FSN dcml, else the
      company's presentation scale),
  (b) the value at the statement position the STRUCTURE selects in that same
      filing: the line on the expected statement whose tag is one of the
      concept's tags, preferring a line that is a calculation PARENT (a printed
      total) over one that is only a component; for total-type concepts the
      chosen line must not itself be a component of another candidate, and
  (c) every applicable check passes:
      identity_tie     balance sheet: Assets = LiabilitiesAndStockholdersEquity
                       at the same date (what the filer printed, both sides)
      components_sum   the line's calc children, with their signs, sum to it
      period_length    the FSN duration (qtrs) matches the cell's grain
      unit_scale       USD (USD/shares for per-share) and the same magnitude
Anything else is DISAGREE (a reason, never a value), NOT_PRESENTED (the filing
presents no such line on that statement) or UNCHECKED (no structure available:
the FSN quarter is not in the bucket, a derived cell, a cell without source).

Why not compare companyfacts to FSN num: both are the same XBRL instance and
agree by construction (the trap of validating against SEC Frames, root
CLAUDE.md 2026-10-18). The independence here is POSITION, the identity tie,
the components sum and the printed-page sample, never two numeric feeds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine

RULE_ID = "proof.cell_proof@1"
DETECTOR_VERSION = "cell_proof_v1_2026-10-31"
PROVEN, DISAGREE, NOT_PRESENTED, UNCHECKED = (
    "PROVEN",
    "DISAGREE",
    "NOT_PRESENTED",
    "UNCHECKED",
)

GRAIN_QTRS = {"I": 0, "Q": 1, "FY": 4}
UNITS_SLACK = Decimal("1.5")

# (canonical data point -> FSN statement, candidate tags in priority order, is the
# line a printed total that must not be a component of another candidate).
# Tags mirror analytics.statement_line / concept_mapping as of 2026-10-31.
EXPECTED: dict[str, tuple[str, tuple[str, ...], bool]] = {
    "revenue_sanity_resolved": (
        "IS",
        (
            "Revenues",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "SalesRevenueNet",
            "RevenueFromContractWithCustomerIncludingAssessedTax",
            "InterestAndDividendIncomeOperating",
        ),
        True,
    ),
    "cost_of_revenue_resolved": (
        "IS",
        ("CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"),
        False,
    ),
    "gross_profit_resolved": ("IS", ("GrossProfit",), True),
    "operating_expenses_resolved": (
        "IS",
        ("OperatingExpenses", "CostsAndExpenses"),
        True,
    ),
    "operating_income_resolved": ("IS", ("OperatingIncomeLoss",), True),
    "interest_expense_resolved": (
        "IS",
        ("InterestExpense", "InterestExpenseDebt", "InterestExpenseNonoperating"),
        False,
    ),
    "income_before_tax_resolved": (
        "IS",
        (
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
        ),
        True,
    ),
    "income_tax_expense_resolved": ("IS", ("IncomeTaxExpenseBenefit",), False),
    "net_income_resolved": (
        "IS",
        (
            "NetIncomeLoss",
            "ProfitLoss",
            "NetIncomeLossAvailableToCommonStockholdersBasic",
        ),
        True,
    ),
    "diluted_eps_resolved": (
        "IS",
        ("EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"),
        False,
    ),
    "cash_and_equivalents_resolved": (
        "BS",
        (
            "CashAndCashEquivalentsAtCarryingValue",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        ),
        False,
    ),
    "current_assets_resolved": ("BS", ("AssetsCurrent",), True),
    "ppe_net_resolved": ("BS", ("PropertyPlantAndEquipmentNet",), False),
    "total_assets_resolved": ("BS", ("Assets",), True),
    "current_liabilities_resolved": ("BS", ("LiabilitiesCurrent",), True),
    "total_liabilities_resolved": ("BS", ("Liabilities",), True),
    "stockholders_equity_resolved": (
        "BS",
        (
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ),
        True,
    ),
    "cfo_resolved": (
        "CF",
        (
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ),
        True,
    ),
    "capex_resolved": (
        "CF",
        (
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "PaymentsToAcquireProductiveAssets",
        ),
        False,
    ),
    "cash_flow_investing_resolved": (
        "CF",
        (
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ),
        True,
    ),
    "cash_flow_financing_resolved": (
        "CF",
        (
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ),
        True,
    ),
    "dividends_paid_resolved": (
        "CF",
        ("PaymentsOfDividends", "PaymentsOfDividendsCommonStock"),
        False,
    ),
    "share_buybacks_resolved": ("CF", ("PaymentsForRepurchaseOfCommonStock",), False),
}
PER_SHARE = {"diluted_eps_resolved"}
# total_debt_resolved is a composition (several lines), proven by the slot-record
# producer, not by a single printed line: UNCHECKED here until that producer lands.


@dataclass(frozen=True)
class Shown:
    """Source (a): the cell as production shows it."""

    company_id: int
    data_point_name: str
    period_grain: str
    period_start: date
    period_end: date
    value: Decimal
    tags: tuple[str, ...]
    accession: str | None
    source_fact_ids: tuple[int, ...]
    is_derived: bool = False
    presentation_scale: int = 6


@dataclass
class Proof:
    shown: Shown
    verdict: str
    reason_code: str | None = None
    reason_text: str | None = None
    position_value: Decimal | None = None
    position_tag: str | None = None
    position_accession: str | None = None
    position_source: str | None = None
    fsn_set: str | None = None
    fsn_stmt: str | None = None
    fsn_line: int | None = None
    fsn_label: str | None = None
    fsn_calc_parent: str | None = None
    position_is_expected_line: bool | None = None
    checks: dict[str, Any] = field(default_factory=dict)

    def row(self) -> dict[str, Any]:
        s = self.shown
        return {
            "company_id": s.company_id,
            "data_point_name": s.data_point_name,
            "period_grain": s.period_grain,
            "period_start": s.period_start,
            "period_end": s.period_end,
            "basis": "latest",
            "shown_value": s.value,
            "shown_tag": ",".join(s.tags) or None,
            "shown_accession": s.accession,
            "shown_source_fact_ids": list(s.source_fact_ids),
            "position_value": self.position_value,
            "position_tag": self.position_tag,
            "position_accession": self.position_accession,
            "position_source": self.position_source,
            "fsn_set": self.fsn_set,
            "fsn_stmt": self.fsn_stmt,
            "fsn_line": self.fsn_line,
            "fsn_label": self.fsn_label,
            "fsn_calc_parent": self.fsn_calc_parent,
            "position_is_expected_line": self.position_is_expected_line,
            "checks": self.checks,
            "verdict": self.verdict,
            "reason_code": self.reason_code,
            "reason_text": self.reason_text,
            "rule_id": RULE_ID,
            "detector_version": DETECTOR_VERSION,
        }


def slack(dcml: int | None, presentation_scale: int) -> Decimal:
    """1.5 units of the filer's stated precision (XBRL decimals: -6 = millions,
    2 = cents), else of the company's presentation scale."""
    exp = -dcml if dcml is not None else presentation_scale
    return UNITS_SLACK * (Decimal(10) ** exp)


def same(a: Decimal, b: Decimal, tol: Decimal) -> bool:
    return abs(a - b) <= tol


def select_position(
    structure: FilingStructure, data_point: str
) -> tuple[PreLine | None, str | None]:
    """The line the structure selects for the data point on its expected
    statement, and why no line when None: 'not_presented' or 'component_only'."""
    stmt, tags, must_be_total = EXPECTED[data_point]
    lines = structure.lines_on(stmt)
    candidates = [p for p in lines if p.tag in tags and not p.custom]
    if not candidates:
        return None, "not_presented"
    candidate_tags = {p.tag for p in candidates}

    def is_component_of_candidate(p: PreLine) -> bool:
        return bool(structure.calc_parents.get(p.tag, set()) & candidate_tags)

    totals = [
        p
        for p in candidates
        if structure.calc_children.get(p.tag) and not is_component_of_candidate(p)
    ]
    pool = (
        totals
        or [p for p in candidates if not is_component_of_candidate(p)]
        or candidates
    )
    if must_be_total and all(is_component_of_candidate(p) for p in candidates):
        return None, "component_only"
    pool.sort(key=lambda p: (tags.index(p.tag), p.report, p.line))
    return pool[0], None


def _check_identity_tie(
    structure: FilingStructure, ddate: date, tol: Decimal
) -> dict[str, Any]:
    a = structure.value("Assets", ddate, 0)
    le = structure.value("LiabilitiesAndStockholdersEquity", ddate, 0)
    if a is None or le is None:
        return {
            "status": "n/a",
            "why": "Assets or LiabilitiesAndStockholdersEquity not in the filing at this date",
        }
    ok = same(a.value, le.value, tol)
    return {
        "status": "pass" if ok else "fail",
        "assets": str(a.value),
        "liabilities_and_equity": str(le.value),
    }


def _check_components_sum(
    structure: FilingStructure, line: PreLine, nv: NumValue, tol: Decimal
) -> dict[str, Any]:
    children = structure.calc_children.get(line.tag, [])
    if not children:
        return {"status": "n/a", "why": "no calculation children for this line"}
    total = Decimal(0)
    missing = []
    for ctag, negative in children:
        cv = structure.value(ctag, nv.ddate, nv.qtrs)
        if cv is None:
            missing.append(ctag)
            continue
        total += -cv.value if negative else cv.value
    if missing:
        return {
            "status": "n/a",
            "why": f"{len(missing)} of {len(children)} children have no value at this date",
            "missing": missing[:5],
        }
    ok = same(total, nv.value, tol)
    return {
        "status": "pass" if ok else "fail",
        "children_sum": str(total),
        "printed": str(nv.value),
        "children": len(children),
    }


def prove_cell(
    shown: Shown, structure: FilingStructure | None, fsn_set: str | None
) -> Proof:
    p = Proof(shown=shown, verdict=UNCHECKED, fsn_set=fsn_set)
    if shown.data_point_name not in EXPECTED:
        p.reason_text = "no single printed line for this data point (composition); proven by its producer"
        return p
    if shown.is_derived:
        p.reason_text = "derived cell (Q4 / TTM): no printed line; proven through its inputs (not in v1)"
        return p
    if structure is None:
        p.reason_text = "no FSN structure for the shown accession (quarter not in bucket, or filing absent from the set)"
        return p
    stmt, _tags, _must = EXPECTED[shown.data_point_name]
    line, why = select_position(structure, shown.data_point_name)
    p.fsn_stmt = stmt
    p.position_accession = structure.adsh
    if line is None:
        if why == "not_presented":
            p.verdict, p.reason_code = NOT_PRESENTED, "line_not_presented_on_statement"
            p.reason_text = (
                f"the filing presents no {shown.data_point_name} line on its {stmt}"
            )
        else:
            p.verdict, p.reason_code = DISAGREE, "only_a_component_line_presented"
            p.reason_text = f"every candidate {shown.data_point_name} line on the {stmt} is a component of another candidate"
        return p
    p.position_tag, p.fsn_line, p.fsn_label = line.tag, line.line, line.label
    parents = structure.calc_parents.get(line.tag, set())
    p.fsn_calc_parent = ",".join(sorted(parents)) or None
    p.position_source = "fsn_pre_calc"
    p.position_is_expected_line = True
    qtrs = GRAIN_QTRS.get(shown.period_grain)
    if qtrs is None:
        p.reason_text = f"grain {shown.period_grain} has no FSN duration"
        return p
    nv = structure.value(line.tag, shown.period_end, qtrs, "USD")
    if nv is None:
        # the line exists but not for this column: a different duration or date
        alt = [
            v
            for (t, d, q), vs in structure.num.items()
            if t == line.tag and d == shown.period_end
            for v in vs
        ]
        if alt:
            p.verdict, p.reason_code = DISAGREE, "period_length_mismatch"
            p.checks["period_length"] = {
                "status": "fail",
                "expected_qtrs": qtrs,
                "found_qtrs": sorted({v.qtrs for v in alt}),
            }
            p.reason_text = f"the printed {line.tag} at {shown.period_end} covers {sorted({v.qtrs for v in alt})} quarter(s), the cell needs {qtrs}"
        else:
            p.verdict, p.reason_code = NOT_PRESENTED, "no_value_for_this_column"
            p.reason_text = f"{line.tag} is presented but carries no value for the column ending {shown.period_end}"
        return p
    p.position_value = nv.value
    tol = slack(nv.dcml, shown.presentation_scale)
    p.checks["period_length"] = {"status": "pass", "qtrs": qtrs}
    want_uom = "USD/" if shown.data_point_name in PER_SHARE else "USD"
    uom_ok = nv.uom.upper().startswith(want_uom) and (
        want_uom != "USD" or "/" not in nv.uom
    )
    mag_ok = (
        shown.value == 0
        or nv.value == 0
        or (Decimal("0.5") <= abs(shown.value / nv.value) <= Decimal("2"))
    )
    p.checks["unit_scale"] = {
        "status": "pass" if (uom_ok and mag_ok) else "fail",
        "uom": nv.uom,
        "dcml": nv.dcml,
    }
    if stmt == "BS":
        p.checks["identity_tie"] = _check_identity_tie(structure, shown.period_end, tol)
    else:
        p.checks["identity_tie"] = {"status": "n/a"}
    p.checks["components_sum"] = _check_components_sum(structure, line, nv, tol)
    values_agree = same(shown.value, nv.value, tol)
    failed = [k for k, v in p.checks.items() if v.get("status") == "fail"]
    if values_agree and not failed:
        p.verdict = PROVEN
        return p
    p.verdict = DISAGREE
    if not values_agree:
        p.reason_code = "shown_differs_from_printed_line"
        p.reason_text = (
            f"production shows {shown.value} ({','.join(shown.tags)}), the printed {line.tag} line "
            f"reads {nv.value} (slack {tol})"
        )
    else:
        p.reason_code = "check_failed:" + ",".join(failed)
        p.reason_text = f"value matches the printed line but {', '.join(failed)} failed"
    return p
