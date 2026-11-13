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
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from scrooner_pipeline.proof.dims import find_value_dim, split_part
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine, fsn_ddate

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
        ("OperatingExpenses",),
        True,
    ),  # CostsAndExpenses includes cost of revenue
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
    "depreciation_and_amortization_resolved": (
        "CF",
        (
            "DepreciationDepletionAndAmortization",
            "DepreciationAmortizationAndAccretionNet",
            "DepreciationAndAmortization",
            "Depreciation",
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
PER_SHARE = {
    "diluted_eps_resolved",
    "basic_eps_resolved",
    "dividends_per_share_resolved",
}
SHARE_COUNTS = {
    "weighted_basic_shares",
    "weighted_diluted_shares",
    "shares_outstanding_resolved",
}
# claim statements with no printed face statement: a note (UN) or the cover/parenthetical (CP)
NOTE_STMTS = frozenset({"UN", "CP", "NOTE"})
# dei cover facts: dated after the balance sheet, never the balance-sheet-date shares outstanding
# (Dhairya shares ruling 2026-11-12; audit R12)
DEI_COVER_TAGS = frozenset({"EntityCommonStockSharesOutstanding"})


def unit_class(data_point: str) -> str:
    """money | per_share | shares: the units and decimals the proof expects."""
    if data_point in SHARE_COUNTS:
        return "shares"
    if data_point in PER_SHARE:
        return "per_share"
    return "money"


def find_value(
    structure: FilingStructure, tag: str, ddate: date, qtrs: int, cls: str
) -> NumValue | None:
    """The filing's value of the tag at (ddate, qtrs) in the unit the class expects:
    shares -> 'shares'; per_share -> 'USD/shares' (FSN may also carry plain 'USD', INTC EPS);
    money -> 'USD' without a per-unit denominator."""
    for v in structure.num.get((tag, ddate, qtrs), []):
        u = v.uom.upper()
        if cls == "shares":
            ok = u.startswith("SHARES")
        elif cls == "per_share":
            ok = u.startswith("USD")
        else:
            ok = u.startswith("USD") and "/" not in u
        if ok:
            return v
    return None


def uom_matches(uom: str, cls: str) -> bool:
    u = uom.upper()
    if cls == "shares":
        return u.startswith("SHARES")
    if cls == "per_share":
        return u.startswith("USD")
    return u.startswith("USD") and "/" not in u


@dataclass(frozen=True)
class Claim:
    """The company's own company_tag_map decision for one cell (the map is the claim, the filing
    FSN/XBRL is the check). kind 'concept': the tag(s) ARE the data point, printed on `stmt`
    (UN/CP = note only, no face). kind 'component': the data point is the signed sum of `parts`."""

    kind: str
    stmt: str
    tags: tuple[str, ...] = ()
    parts: tuple[tuple[int, str], ...] = ()  # (sign, tag)
    sign: int = 1


# A printed total is itself a component of the next subtotal up (gross profit
# sits under operating income, liabilities under liabilities-and-equity), so
# "component" must mean: a calc child of something OTHER than the standard
# parents of that line. Anything else (a custom total, another aggregation)
# makes the chosen line a component of a line we do not recognise.
STANDARD_PARENTS: dict[str, frozenset[str]] = {
    "revenue_sanity_resolved": frozenset(
        {
            "Revenues",
            "GrossProfit",
            "OperatingIncomeLoss",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
            "CostsAndExpenses",
        }
    ),
    "gross_profit_resolved": frozenset(
        {
            "OperatingIncomeLoss",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
        }
    ),
    "operating_expenses_resolved": frozenset(
        {
            "OperatingIncomeLoss",
            "CostsAndExpenses",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
        }
    ),
    "operating_income_resolved": frozenset(
        {
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
            "NetIncomeLoss",
            "ProfitLoss",
        }
    ),
    "income_before_tax_resolved": frozenset(
        {
            "NetIncomeLoss",
            "ProfitLoss",
            "IncomeLossFromContinuingOperations",
            "IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest",
        }
    ),
    "net_income_resolved": frozenset(
        {
            "ProfitLoss",
            "NetIncomeLossAvailableToCommonStockholdersBasic",
            "ComprehensiveIncomeNetOfTax",
            "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest",
            "NetIncomeLoss",
        }
    ),
    "current_assets_resolved": frozenset({"Assets"}),
    "total_assets_resolved": frozenset(),
    "current_liabilities_resolved": frozenset(
        {"Liabilities", "LiabilitiesAndStockholdersEquity"}
    ),
    "total_liabilities_resolved": frozenset({"LiabilitiesAndStockholdersEquity"}),
    "stockholders_equity_resolved": frozenset(
        {
            "LiabilitiesAndStockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        }
    ),
    "cfo_resolved": frozenset(
        {
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
            "CashAndCashEquivalentsPeriodIncreaseDecrease",
            "NetCashProvidedByUsedInOperatingActivities",
        }
    ),
    "cash_flow_investing_resolved": frozenset(
        {
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
            "CashAndCashEquivalentsPeriodIncreaseDecrease",
            "NetCashProvidedByUsedInInvestingActivities",
        }
    ),
    "cash_flow_financing_resolved": frozenset(
        {
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
            "CashAndCashEquivalentsPeriodIncreaseDecrease",
            "NetCashProvidedByUsedInFinancingActivities",
        }
    ),
}
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
    copies_disagree: tuple[tuple[str, str], ...] | None = (
        None  # periodic copies (accession, value) outside precision
    )
    copies: int = 0
    claim: Claim | None = None


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


def slack_for(cls: str, dcml: int | None, presentation_scale: int) -> Decimal:
    """Money: the filer's decimals, else the company's presentation scale. Share counts and
    per-share values never take the money scale (1.5M of slack on a share count would prove anything):
    decimals, else whole shares / cents."""
    if cls == "money":
        return slack(dcml, presentation_scale)
    exp = -dcml if dcml is not None else (0 if cls == "shares" else -2)
    return UNITS_SLACK * (Decimal(10) ** exp)


def same(a: Decimal, b: Decimal, tol: Decimal) -> bool:
    return abs(a - b) <= tol


def select_position(
    structure: FilingStructure, data_point: str, claim: Claim | None = None
) -> tuple[PreLine | None, str | None]:
    """The line the structure selects for the data point on its expected
    statement: the highest-priority candidate tag that is presented. For a
    total-type data point the line must be a printed total or subtotal, i.e.
    not a calculation child of a line OUTSIDE the candidate set (a candidate
    may be a child of another candidate: StockholdersEquity sits under the
    total including NCI). Returns (None, 'not_presented' | 'component_only')."""
    if claim is not None:
        # the company's own map names the tag(s) and the statement (custom tags allowed: it is the claim)
        stmt, tags = claim.stmt, claim.tags
        must_be_total = EXPECTED[data_point][2] if data_point in EXPECTED else False
    else:
        stmt, tags, must_be_total = EXPECTED[data_point]
    lines = structure.lines_on(stmt)
    candidates = [
        p for p in lines if p.tag in tags and (claim is not None or not p.custom)
    ]
    if not candidates:
        return None, "not_presented"
    candidate_tags = {p.tag for p in candidates}
    candidates.sort(key=lambda p: (tags.index(p.tag), p.report, p.line))
    chosen = candidates[0]
    if must_be_total:
        # A us-gaap parent of a us-gaap total is a higher aggregate by construction
        # (gross profit under operating income, operating income under the many
        # income-before-tax variants). A line is a COMPONENT only when its parent is
        # a filer extension: a custom "total revenues" with the standard revenue tag
        # beneath it means the printed total is not the standard line.
        custom = structure.custom_parents.get(chosen.tag, set()) - candidate_tags
        # a line that is itself a calc parent is a printed total, whatever a filer
        # rolls it up into (AMZN cash from operations under a custom cash roll-up,
        # PG operating income under a custom pre-tax line): never a component
        if custom and not structure.calc_children.get(chosen.tag):
            return None, "component_only"
    return chosen, None


def on_statement_face(
    structure: FilingStructure, stmt: str, nv: NumValue
) -> tuple[bool, str]:
    """Does the statement print a column for this value? FSN num holds every
    fact of the filing, notes and MD&A included (the quarterly-data note of a
    10-K, 3-month cash-flow figures where the statement prints 6 or 9 months).
    Form-based rule, conservative: a 10-K statement prints annual columns only
    (qtrs 4); a 10-Q income statement prints the 3-month and the year-to-date
    columns, its cash-flow statement the year-to-date only; a balance sheet
    prints the dates at which the filing values total assets."""
    form = (structure.form or "").upper()
    if stmt == "BS":
        dates = {d for (tag, d, q) in structure.num if tag == "Assets" and q == 0}
        if not dates:
            dates = {
                d
                for (tag, d, q) in structure.num
                if tag == "LiabilitiesAndStockholdersEquity" and q == 0
            }
        if nv.ddate in dates or not dates:
            return True, "balance sheet date"
        return False, f"the balance sheet prints no column dated {nv.ddate}"
    if form.startswith("10-K"):
        if nv.qtrs == 4:
            return True, "annual column of a 10-K"
        return (
            False,
            f"a 10-K {stmt} prints annual columns; a {nv.qtrs}-quarter value comes from a note",
        )
    if form.startswith("10-Q"):
        ytd = max(
            (q for (tag, d, q) in structure.num if tag == nv.tag and d == nv.ddate),
            default=nv.qtrs,
        )
        if stmt == "CF":
            if nv.qtrs == ytd:
                return True, "year-to-date column of a 10-Q cash-flow statement"
            return (
                False,
                f"the cash-flow statement prints the {ytd}-quarter year-to-date column, not a {nv.qtrs}-quarter one",
            )
        if nv.qtrs in (1, ytd):
            return True, "3-month or year-to-date column of a 10-Q"
        return (
            False,
            f"a 10-Q {stmt} prints the 3-month and {ytd}-quarter columns, not {nv.qtrs}",
        )
    return True, f"form {form}: no column rule"


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
    """The line's calc children sum to it, evaluated PER CALC GROUP: a statement
    line can be totalled in several roles (income before tax = operating income
    + non-operating on the face, and = domestic + foreign in the tax note);
    merging the groups double-counts. Pass when any complete group ties; fail
    only when every complete group misses; n/a when no group is complete."""
    groups = structure.calc_groups.get(line.tag)
    if not groups and structure.calc_children.get(line.tag):
        groups = {"all": structure.calc_children[line.tag]}
    if not groups:
        return {"status": "n/a", "why": "no calculation children for this line"}
    complete: list[dict[str, Any]] = []
    incomplete = 0
    for grp, children in groups.items():
        if len(children) < 2:
            continue  # a single arc is a reclassification, not a decomposition
        total = Decimal(0)
        missing = []
        for ctag, negative in children:
            cv = structure.value(ctag, nv.ddate, nv.qtrs)
            if cv is None:
                missing.append(ctag)
                continue
            total += -cv.value if negative else cv.value
        if missing:
            incomplete += 1
            continue
        # a sum of n rounded children can miss the rounded total by n/2 units
        unit = tol / UNITS_SLACK
        ok = same(total, nv.value, max(tol, unit * Decimal(len(children)) / 2))
        if ok:
            return {
                "status": "pass",
                "group": grp,
                "children": len(children),
                "children_sum": str(total),
                "printed": str(nv.value),
            }
        complete.append(
            {"group": grp, "children": len(children), "children_sum": str(total)}
        )
    if not complete:
        return {
            "status": "n/a",
            "why": f"{incomplete} calc group(s), none with every child valued at this date",
        }
    return {"status": "fail", "printed": str(nv.value), "groups": complete}


def locate(
    structure: FilingStructure, shown: Shown
) -> tuple[PreLine | None, str | None, str, Claim | None]:
    """(line, why, statement, claim used). The company's claim first; the hand EXPECTED map is the
    fallback where the claim's line is not on the claimed statement (or there is no claim)."""
    dp = shown.data_point_name
    claim = shown.claim
    if claim is not None and claim.kind == "concept" and claim.stmt not in NOTE_STMTS:
        line, why = select_position(structure, dp, claim)
        if line is not None or dp not in EXPECTED:
            return line, why, claim.stmt, claim
    if dp in EXPECTED:
        line, why = select_position(structure, dp)
        return line, why, EXPECTED[dp][0], None
    return None, "not_presented", claim.stmt if claim else "", claim


def _claim_check(claim: Claim | None) -> dict[str, Any]:
    if claim is None:
        return {"source": "expected_map"}
    return {
        "source": "company_tag_map",
        "kind": claim.kind,
        "stmt": claim.stmt,
        "tags": list(claim.tags) or [t for _s, t in claim.parts],
    }


def _note_only(shown: Shown) -> bool:
    c = shown.claim
    return (
        c is not None
        and c.kind == "concept"
        and (
            c.stmt in NOTE_STMTS
            # the parenthetical share line of a balance sheet is not in FSN pre (inpth 1)
            or shown.data_point_name == "shares_outstanding_resolved"
        )
    )


def _finish(
    p: Proof,
    shown: Shown,
    cls: str,
    printed: Decimal,
    uom: str,
    dcml: int | None,
    sign: int,
    label: str,
) -> Proof:
    """unit_scale + value comparison -> verdict (shared by every proof path)."""
    tol = slack_for(cls, dcml, shown.presentation_scale)
    expect = sign * printed
    p.position_value = expect
    mag_ok = (
        shown.value == 0
        or expect == 0
        or (Decimal("0.5") <= abs(shown.value / expect) <= Decimal(2))
    )
    p.checks["unit_scale"] = {
        "status": "pass" if (uom_matches(uom, cls) and mag_ok) else "fail",
        "uom": uom,
        "dcml": dcml,
        "class": cls,
    }
    failed = [k for k, v in p.checks.items() if v.get("status") == "fail"]
    if same(shown.value, expect, tol) and not failed:
        p.verdict = PROVEN
        return p
    p.verdict = DISAGREE
    if not same(shown.value, expect, tol):
        p.reason_code = "shown_differs_from_printed_line"
        p.reason_text = (
            f"production shows {shown.value} ({','.join(shown.tags)}), {label} "
            f"reads {expect} (slack {tol})"
        )
    else:
        p.reason_code = "check_failed:" + ",".join(failed)
        p.reason_text = f"value matches {label} but {', '.join(failed)} failed"
    return p


def _column(shown: Shown) -> tuple[date, int | None]:
    return fsn_ddate(shown.period_end), GRAIN_QTRS.get(shown.period_grain)


def prove_note(shown: Shown, structure: FilingStructure, p: Proof) -> Proof:
    """A line printed only in a note or the cover (interest paid, taxes paid, the parenthetical
    share count): there is no face statement; the claim's tag is read as the filing's own fact at
    the cell's column, in the right unit."""
    claim = shown.claim
    assert claim is not None
    cls = unit_class(shown.data_point_name)
    p.fsn_stmt = claim.stmt
    p.position_accession = structure.adsh
    p.position_source = "fsn_pre_calc"
    p.position_is_expected_line = True
    p.checks["claim"] = _claim_check(claim)
    ddate, qtrs = _column(shown)
    if qtrs is None:
        p.reason_text = f"grain {shown.period_grain} has no FSN duration"
        return p
    nv = None
    for t in claim.tags:
        nv = find_value(structure, t, ddate, qtrs, cls)
        if nv is not None:
            break
    if nv is None:
        alt = sorted(
            {
                v.qtrs
                for t in claim.tags
                for (tg, d, _q), vs in structure.num.items()
                if tg == t and d == ddate
                for v in vs
                if uom_matches(v.uom, cls)
            }
        )
        if alt:
            p.verdict, p.reason_code = DISAGREE, "period_length_mismatch"
            p.checks["period_length"] = {
                "status": "fail",
                "expected_qtrs": qtrs,
                "found_qtrs": alt,
            }
            p.reason_text = (
                f"the note fact {claim.tags} at {shown.period_end} covers {alt} "
                f"quarter(s), the cell needs {qtrs}"
            )
        else:
            p.verdict, p.reason_code = NOT_PRESENTED, "no_value_for_this_column"
            p.reason_text = (
                f"{structure.adsh} carries no {','.join(claim.tags)} fact for the "
                f"column ending {shown.period_end}"
            )
        return p
    p.position_tag = nv.tag
    p.checks["period_length"] = {"status": "pass", "qtrs": qtrs}
    p.checks["statement_face"] = {
        "status": "n/a",
        "why": "note-only line: proven against the note fact of this filing, no face statement",
    }
    p.checks["identity_tie"] = {"status": "n/a"}
    p.checks["components_sum"] = {"status": "n/a", "why": "note fact"}
    return _finish(
        p, shown, cls, nv.value, nv.uom, nv.dcml, claim.sign, f"the note fact {nv.tag}"
    )


def prove_component(shown: Shown, structure: FilingStructure, p: Proof) -> Proof:
    """A component sum (total debt): the shown value is the signed sum of the parts the company's
    map names, each part matched in this filing at the cell's column and on the claimed statement.
    A part the filing does not carry leaves the cell UNCHECKED (never a guessed zero)."""
    claim = shown.claim
    assert claim is not None
    cls = unit_class(shown.data_point_name)
    p.fsn_stmt = claim.stmt
    p.position_accession = structure.adsh
    p.position_source = "fsn_pre_calc"
    p.position_is_expected_line = True
    ddate, qtrs = _column(shown)
    if qtrs is None:
        p.reason_text = f"grain {shown.period_grain} has no FSN duration"
        return p
    face = {ln.tag for ln in structure.lines_on(claim.stmt)}
    total = Decimal(0)
    found: list[dict[str, Any]] = []
    missing: list[str] = []
    off_face: list[str] = []
    dcmls: list[int | None] = []
    for sign, tag in claim.parts:
        try:
            base, segs = split_part(tag)
        except (
            ValueError
        ):  # a malformed member claim is unknown, never read as a plain tag
            missing.append(tag)
            continue
        if segs:  # member claim: ONLY the value under exactly these members, never the total (proof/dims.py)
            nv = find_value_dim(structure, base, ddate, qtrs, cls, segs)
        else:  # plain claim: the non-dimensional value only
            nv = find_value(structure, tag, ddate, qtrs, cls)
        if nv is None:
            missing.append(tag)
            continue
        if not segs and claim.stmt not in NOTE_STMTS and tag not in face:
            off_face.append(tag)
            continue
        total += sign * nv.value
        dcmls.append(nv.dcml)
        found.append({"tag": tag, "sign": sign, "value": str(nv.value)})
    p.checks["claim"] = _claim_check(claim)
    p.checks["component_parts"] = {
        "status": "n/a" if (missing or off_face) else "pass",
        "found": found,
        "missing": missing,
        "not_on_statement": off_face,
    }
    if missing or off_face:
        p.reason_text = (
            f"component sum not provable: part(s) {missing + off_face} not on the "
            f"{claim.stmt} of {structure.adsh} at {shown.period_end}"
        )
        return p
    p.position_tag = "+".join(t for _s, t in claim.parts)
    p.checks["period_length"] = {"status": "pass", "qtrs": qtrs}
    p.checks["identity_tie"] = {"status": "n/a"}
    p.checks["components_sum"] = {
        "status": "n/a",
        "why": "the cell is itself the sum of parts",
    }
    known = [d for d in dcmls if d is not None]
    dcml = min(known) if known else None  # the coarsest filer precision among the parts
    return _finish(
        p,
        shown,
        cls,
        total,
        "shares" if cls == "shares" else "USD",  # a share-count sum is in shares (R11)
        dcml,
        claim.sign,
        "the sum of " + ",".join(t for _s, t in claim.parts),
    )


def prove_cell(
    shown: Shown,
    structure: FilingStructure | None,
    fsn_set: str | None,
    prior_structure: FilingStructure | None = None,
) -> Proof:
    p = Proof(shown=shown, verdict=UNCHECKED, fsn_set=fsn_set)
    if shown.data_point_name not in EXPECTED and shown.claim is None:
        p.reason_text = (
            "no company_tag_map claim for this cell and no hand expectation: "
            "nothing to prove it against"
        )
        return p
    if shown.data_point_name == "shares_outstanding_resolved":
        cover = sorted(
            DEI_COVER_TAGS
            & {*shown.tags, *(shown.claim.tags if shown.claim else ())}
        )
        if cover:
            p.verdict, p.reason_code = DISAGREE, "dei_cover_count_is_not_shares_outstanding"
            p.reason_text = (
                f"shares outstanding rests on the dei cover fact {cover}; the cover count is dated "
                "after the balance sheet and is never the balance-sheet-date shares outstanding"
            )
            return p
    if shown.copies_disagree:
        p.verdict, p.reason_code = DISAGREE, "restated_copies_disagree"
        others = "; ".join(f"{v} in {acc}" for acc, v in shown.copies_disagree[:4])
        p.reason_text = (
            f"production shows {shown.value} ({shown.accession}) but another periodic copy of this cell reads {others}; "
            "restated copies that disagree are hidden (founder ruling); 'show the latest recast' is a founder decision"
        )
        return p
    if shown.is_derived:
        return prove_derived(shown, structure, prior_structure, fsn_set)
    if structure is None:
        p.reason_text = "no FSN structure for the shown accession (quarter not in bucket, or filing absent from the set)"
        return p
    claim = shown.claim
    if claim is not None and claim.kind == "component":
        return prove_component(shown, structure, p)
    if _note_only(shown):
        return prove_note(shown, structure, p)
    cls = unit_class(shown.data_point_name)
    line, why, stmt, used = locate(structure, shown)
    sign = used.sign if used is not None else 1
    p.fsn_stmt = stmt
    p.position_accession = structure.adsh
    p.checks["claim"] = _claim_check(used)
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
    ddate, qtrs = _column(shown)
    if qtrs is None:
        p.reason_text = f"grain {shown.period_grain} has no FSN duration"
        return p
    nv = find_value(structure, line.tag, ddate, qtrs, cls)
    if nv is None:
        # the line exists but not for this column: a different duration or date
        alt = [
            v
            for (t, d, q), vs in structure.num.items()
            if t == line.tag and d == ddate
            for v in vs
            if uom_matches(v.uom, cls)
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
    p.position_value = sign * nv.value
    face, why_face = on_statement_face(structure, stmt, nv)
    p.checks["statement_face"] = {"status": "pass" if face else "fail", "why": why_face}
    if not face:
        p.verdict, p.reason_code = NOT_PRESENTED, "value_in_note_not_on_statement_face"
        p.reason_text = f"{line.tag} = {nv.value} exists in {structure.adsh} but {why_face}; the statement face proves nothing here"
        return p
    p.checks["period_length"] = {"status": "pass", "qtrs": qtrs}
    tol = slack_for(cls, nv.dcml, shown.presentation_scale)
    if stmt == "BS":
        p.checks["identity_tie"] = _check_identity_tie(structure, ddate, tol)
    else:
        p.checks["identity_tie"] = {"status": "n/a"}
    p.checks["components_sum"] = _check_components_sum(structure, line, nv, tol)
    return _finish(
        p,
        shown,
        cls,
        nv.value,
        nv.uom,
        nv.dcml,
        sign,
        f"the printed {line.tag} line",
    )


# ---- derived cells (Q4 and interim quarters built by subtraction) --------------


def prove_derived(
    shown: Shown,
    structure: FilingStructure | None,
    prior_structure: FilingStructure | None,
    fsn_set: str | None,
) -> Proof:
    """A derived quarter has no printed line. It is PROVEN when its two
    inputs are printed lines of the filings they come from and the arithmetic
    reproduces the shown value at the filer's precision:
        Q_n = YTD_n (the derived fact's own filing: the 10-K for Q4, the 10-Q
              for an interim quarter) - YTD_(n-1) (the prior quarter's filing;
              Q1 counts as YTD_1)
    where each YTD is the structure-selected line's value at that period end
    with the matching duration (qtrs). A missing prior filing or YTD leaves
    the cell UNCHECKED with that reason; a mismatch is DISAGREE (the
    same-vintage hold's territory: a recast FY against an original 9M)."""
    p = Proof(shown=shown, verdict=UNCHECKED, fsn_set=fsn_set)
    if shown.data_point_name not in EXPECTED and shown.claim is None:
        p.reason_text = "no company_tag_map claim for this cell and no hand expectation: nothing to prove it against"
        return p
    if unit_class(shown.data_point_name) == "shares" or (
        shown.data_point_name not in EXPECTED
        and unit_class(shown.data_point_name) == "per_share"
    ):
        p.reason_text = "a share count or per-share value is never derived by subtraction; nothing to prove"
        return p
    if shown.data_point_name not in EXPECTED and (
        shown.claim is None or shown.claim.kind != "concept" or _note_only(shown)
    ):
        p.reason_text = "derived component sum or note-only line: no printed year-to-date line to subtract"
        return p
    if shown.period_grain != "Q":
        p.reason_text = f"derived {shown.period_grain} cell: only derived quarters are proven through inputs"
        return p
    if structure is None:
        p.reason_text = "no FSN structure for the derived fact's filing (quarter not in bucket, or filing absent)"
        return p
    line, why, stmt, used = locate(structure, shown)
    sign = used.sign if used is not None else 1
    p.checks["claim"] = _claim_check(used)
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
            p.reason_text = "the standard line sits under a filer-extension total"
        return p
    p.position_tag, p.fsn_line, p.fsn_label = line.tag, line.line, line.label
    # 0114 allows slot_record / fsn_pre_calc / face_total: the inputs' line is located through the
    # filing's pre/calc structure; the derivation itself is recorded in checks["derivation"]
    p.position_source = "fsn_pre_calc"
    p.checks["derivation"] = {"status": "n/a", "source": "derived_inputs"}
    p.position_is_expected_line = True
    end_dd = fsn_ddate(shown.period_end)
    ytd_n = None
    for n in (4, 3, 2):
        ytd_n = structure.value(line.tag, end_dd, n, "USD")
        if ytd_n is not None:
            break
    if ytd_n is None:
        p.verdict, p.reason_code = NOT_PRESENTED, "no_year_to_date_value_in_own_filing"
        p.reason_text = f"{line.tag} has no year-to-date value ending {shown.period_end} in {structure.adsh}"
        return p
    prior_end = shown.period_start - timedelta(days=1)
    prior_dd = fsn_ddate(prior_end)
    sources = [s for s in (prior_structure, structure) if s is not None]
    ytd_prev = None
    for s in sources:
        ytd_prev = s.value(line.tag, prior_dd, ytd_n.qtrs - 1, "USD")
        if ytd_prev is not None:
            prev_adsh = s.adsh
            break
    if ytd_prev is None:
        p.reason_text = (
            f"no {ytd_n.qtrs - 1}-quarter year-to-date value of {line.tag} ending {prior_end} "
            f"in the prior quarter's filing{'' if prior_structure else ' (prior filing not loaded)'}"
        )
        return p
    q = sign * (ytd_n.value - ytd_prev.value)
    tol = slack(ytd_n.dcml, shown.presentation_scale)
    p.position_value = q
    p.checks["period_length"] = {
        "status": "pass",
        "ytd_qtrs": ytd_n.qtrs,
        "prior_qtrs": ytd_prev.qtrs,
    }
    uom_ok = ytd_n.uom.upper().startswith("USD") and ytd_prev.uom.upper().startswith(
        "USD"
    )
    mag_ok = (
        shown.value == 0
        or q == 0
        or (Decimal("0.5") <= abs(shown.value / q) <= Decimal(2))
    )
    p.checks["unit_scale"] = {
        "status": "pass" if (uom_ok and mag_ok) else "fail",
        "uom": ytd_n.uom,
        "dcml": ytd_n.dcml,
    }
    p.checks["identity_tie"] = {"status": "n/a"}
    p.checks["components_sum"] = {
        "status": "n/a",
        "why": "derived by subtraction of two printed year-to-date lines",
        "inputs": {
            "ytd": str(ytd_n.value),
            "ytd_accession": structure.adsh,
            "prior": str(ytd_prev.value),
            "prior_accession": prev_adsh,
        },
    }
    if same(shown.value, q, tol) and p.checks["unit_scale"]["status"] == "pass":
        p.verdict = PROVEN
        return p
    p.verdict = DISAGREE
    p.reason_code = "derived_quarter_differs_from_inputs"
    p.reason_text = (
        f"production shows {shown.value}; the printed {line.tag} year-to-date {ytd_n.value} ({structure.adsh}) "
        f"minus the prior year-to-date {ytd_prev.value} ({prev_adsh}) gives {q} (slack {tol})"
    )
    return p
