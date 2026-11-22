"""Automated draw checker (founder 2026-11-22: "certify 5,000 companies fast").

The verifier's stratified draw (min(199, shown) cells, display_cert.draw) used to be read against the filing by one
agent per company. This module checks every drawn cell mechanically against the cited filing's own XBRL facts in the
FSN store (fsn.value, fsn.line, fsn.tag, fsn.dim for that accession) and sorts it into one of three outcomes:

- AUTO_MATCH: the filing's fact equals the shown value at the same period end (+-7 days for 52/53-week years), the same
  duration (instant / four quarters), no dimensions (or the part's own dimensions) and the finest decimals the filing
  tags for that figure; per-share plausible; sign per the polarity ruling.
- AUTO_MISMATCH: the filing's fact for the data point exists and differs (value, sign, a rounded duplicate, a part, a
  derivation's sum or shape, an implausible per-share value). Each one may be a wrong shown value.
- NEEDS_READ: no fact to match (text-stated, a stated zero, a custom or dimensioned line outside the checker's own
  element families, a derivation with no known identity): a person or agent reads the filing.

Independence (CERTIFICATION-METHOD-2026-11-16.md, "Automated draw checker"): the checker never reads the resolver
output (data-team/tags/line_map, the standard extract JSON, fsn.line_map) or analytics.canonical_fact. For an
as-printed cell it ignores the export's tag: it finds the data point's fact in the filing through its OWN element
families (FAMILIES below, ordered tiers: the first tier the filing tags at that period decides), so a resolver that
picked the wrong element is caught rather than echoed. Its SQL (FILING_FACT_SQL, FILING_LINE_SQL) is its own and pulls
every fact of the filing at the drawn period ends, not only the cited tag. Combined cells are found by the printed
label in the badge (fsn.line.plabel), derived cells by their registry formula over the filing's facts. Only the sign
convention (common/polarity.py, a Tag Expert ruling of what the page shows) is shared, because it defines the
expected display sign, not a match.
"""

from __future__ import annotations

import csv
import math
import random
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

from scrooner_pipeline.common.polarity import is_fixed_positive

if TYPE_CHECKING:  # import cycle: display_cert imports this module
    from scrooner_pipeline.certification.display_cert import Cell

CHECKER_VERSION = "draw_check@1"
AUTO_MATCH = "AUTO_MATCH"
AUTO_MISMATCH = "AUTO_MISMATCH"
NEEDS_READ = "NEEDS_READ"
OUTCOMES = (AUTO_MATCH, AUTO_MISMATCH, NEEDS_READ)
AUDIT_RATE = 0.05
PER_SHARE = frozenset({"basic_eps", "diluted_eps", "dividends_per_share"})
PER_SHARE_CEILING = Decimal(1000)

# The checker's own element families: data point -> ordered tiers of standard elements. The first tier with an
# undimensioned fact at the cell's period in the cited filing decides; a value that only equals a later tier's fact is
# not a match (NetIncomeLoss present and different, ProfitLoss equal = the NCI-inclusive line, wrong for net_income).
FAMILIES: dict[str, tuple[tuple[str, ...], ...]] = {
    # One tier: "Revenues" is the total for most filers but a subtotal for some (BLK base fees) and the total with
    # other income for others (CVX "revenues and other income"), so any printed revenue element may hold the figure.
    "revenue": (
        (
            "Revenues",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "RevenueFromContractWithCustomerIncludingAssessedTax",
            "SalesRevenueNet",
            "RevenuesNetOfInterestExpense",
            "RegulatedAndUnregulatedOperatingRevenue",
        ),
    ),
    "cost_of_revenue": (
        (
            "CostOfRevenue",
            "CostOfGoodsAndServicesSold",
            "CostOfGoodsSold",
            "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization",
            "CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization",
        ),
        ("CostOfServices",),
    ),
    "gross_profit": (("GrossProfit",),),
    "operating_income": (("OperatingIncomeLoss",),),
    "operating_expenses": (
        ("OperatingExpenses",),
        ("CostsAndExpenses", "OperatingCostsAndExpenses", "BenefitsLossesAndExpenses"),
    ),
    "sga_expense": (
        ("SellingGeneralAndAdministrativeExpense",),
        ("GeneralAndAdministrativeExpense",),
    ),
    "research_and_development": (
        (
            "ResearchAndDevelopmentExpense",
            "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
        ),
    ),
    "interest_expense": (
        (
            "InterestExpense",
            "InterestExpenseNonoperating",
            "InterestExpenseDebt",
            "InterestExpenseOperating",
            "InterestAndDebtExpense",
        ),
    ),
    # Consolidated interest income (X94): a bank's or broker's total interest income line decides before components.
    "interest_income": (
        ("InterestAndDividendIncomeOperating",),
        (
            "InvestmentIncomeInterest",
            "InterestIncomeOther",
            "InvestmentIncomeInterestAndDividend",
            "InterestIncomeOperating",
            "InterestIncomeNonoperating",
            "InterestAndOtherIncome",
        ),
    ),
    "other_income_expense_net": (
        ("OtherNonoperatingIncomeExpense", "NonoperatingIncomeExpense"),
    ),
    "income_before_tax": (
        (
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
        ),
    ),
    "income_tax_expense": (("IncomeTaxExpenseBenefit",),),
    # Parent net income; a filer with no NetIncomeLoss tags the parent line as available to common (CAT, SCCO)
    # before the NCI-inclusive ProfitLoss.
    "net_income": (
        ("NetIncomeLoss",),
        ("NetIncomeLossAvailableToCommonStockholdersBasic",),
        ("ProfitLoss",),
    ),
    "comprehensive_income": (
        ("ComprehensiveIncomeNetOfTax",),
        (
            "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest",
        ),
    ),
    "basic_eps": (("EarningsPerShareBasic", "EarningsPerShareBasicAndDiluted"),),
    "diluted_eps": (("EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"),),
    "dividends_per_share": (
        (
            "CommonStockDividendsPerShareDeclared",
            "CommonStockDividendsPerShareCashPaid",
        ),
    ),
    "weighted_basic_shares": (
        (
            "WeightedAverageNumberOfSharesOutstandingBasic",
            "WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
        ),
    ),
    "weighted_diluted_shares": (
        (
            "WeightedAverageNumberOfDilutedSharesOutstanding",
            "WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
        ),
    ),
    "total_assets": (("Assets",),),
    "total_liabilities": (("Liabilities",),),
    "current_assets": (("AssetsCurrent",),),
    "current_liabilities": (("LiabilitiesCurrent",),),
    "cash_and_equivalents": (
        ("CashAndCashEquivalentsAtCarryingValue",),
        # registry step 2 (a printed line also holding restricted cash or fed funds: BAC, AXP face totals) and a bank's
        # cash line (JPM "cash and due from banks"): one tier, since the face prints one of them and not a total
        (
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
            "CashCashEquivalentsAndFederalFundsSold",
            "Cash",
            "CashAndDueFromBanks",
        ),
    ),
    "accounts_receivable": (
        ("AccountsReceivableNetCurrent",),
        ("ReceivablesNetCurrent", "AccountsNotesAndLoansReceivableNetCurrent"),
    ),
    "inventory": (("InventoryNet",),),
    "ppe_net": (
        ("PropertyPlantAndEquipmentNet",),
        (
            "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization",
            "PublicUtilitiesPropertyPlantAndEquipmentNet",
        ),
    ),
    "goodwill": (("Goodwill",),),
    "accounts_payable": (("AccountsPayableCurrent",), ("AccountsPayableTradeCurrent",)),
    "stockholders_equity": (("StockholdersEquity",),),
    "shares_outstanding": (("CommonStockSharesOutstanding",),),
    "cfo": (
        ("NetCashProvidedByUsedInOperatingActivities",),
        ("NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",),
    ),
    "cash_flow_investing": (
        ("NetCashProvidedByUsedInInvestingActivities",),
        ("NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",),
    ),
    "cash_flow_financing": (
        ("NetCashProvidedByUsedInFinancingActivities",),
        ("NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",),
    ),
    "capex": (
        ("PaymentsToAcquirePropertyPlantAndEquipment",),
        ("PaymentsToAcquireProductiveAssets",),
    ),
    "depreciation_and_amortization": (
        (
            "DepreciationDepletionAndAmortization",
            "DepreciationAndAmortization",
            "DepreciationAmortizationAndAccretionNet",
        ),
    ),
    "amortization_of_intangibles": (("AmortizationOfIntangibleAssets",),),
    "sbc": (("ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"),),
    "dividends_paid": (("PaymentsOfDividendsCommonStock",), ("PaymentsOfDividends",)),
    "share_buybacks": (
        ("PaymentsForRepurchaseOfCommonStock",),
        ("PaymentsForRepurchaseOfEquity",),
    ),
    "cash_paid_for_interest": (("InterestPaidNet", "InterestPaid"),),
    "cash_paid_for_income_taxes": (("IncomeTaxesPaidNet", "IncomeTaxesPaid"),),
    "cf_ar_change": (
        (
            "IncreaseDecreaseInAccountsReceivable",
            "IncreaseDecreaseInReceivables",
            "IncreaseDecreaseInAccountsAndNotesReceivable",
        ),
    ),
    "cf_inventory_change": (("IncreaseDecreaseInInventories",),),
    "cf_ap_change": (
        ("IncreaseDecreaseInAccountsPayable", "IncreaseDecreaseInAccountsPayableTrade"),
    ),
    "net_interest_income": (("InterestIncomeExpenseNet",),),
    "total_interest_income": (("InterestAndDividendIncomeOperating",),),
    "noninterest_income": (("NoninterestIncome",),),
    "noninterest_expense": (("NoninterestExpense",),),
    "provision_for_credit_losses": (
        (
            "ProvisionForLoanLeaseAndOtherLosses",
            "ProvisionForLoanAndLeaseLosses",
            "ProvisionForCreditLossesNet",
        ),
    ),
    "loans_net": (
        (
            "LoansAndLeasesReceivableNetReportedAmount",
            "FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss",
        ),
    ),
    "deposits": (("Deposits",),),
    "bdc_total_investment_income": (("GrossInvestmentIncomeOperating",),),
}
INSTANT = frozenset(
    {
        "total_assets",
        "total_liabilities",
        "current_assets",
        "current_liabilities",
        "cash_and_equivalents",
        "accounts_receivable",
        "inventory",
        "ppe_net",
        "goodwill",
        "accounts_payable",
        "stockholders_equity",
        "shares_outstanding",
        "total_debt",
        "loans_net",
        "deposits",
    }
)
# Identities for a derived cell with no parts (doc 02 / data_points.csv formulas), over the filing's own facts.
TOTAL_EQUITY = (
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    "StockholdersEquity",
)
TEMP_EQUITY = (
    "TemporaryEquityCarryingAmountAttributableToParent",
    "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterest",
    "RedeemableNoncontrollingInterestEquityCarryingAmount",
)


@dataclass(frozen=True)
class FilingFact:
    accession: str
    tag: str
    ddate: str
    qtrs: int
    dims: str
    value: Decimal
    dcml: int = 32767  # higher is more precise; unknown precision counts as exact


@dataclass(frozen=True)
class FilingLine:
    accession: str
    tag: str
    report: int
    stmt: str
    plabel: str


# One read of the filing itself: every undimensioned or dimensioned fact (no co-registrant) at the drawn period ends,
# whatever its tag. Deliberately not the certifier's FACT_SQL (which reads only the cited tags).
FILING_FACT_SQL = """
select f.accession, t.tag, v.ddate::text, v.qtrs, coalesce(d.segments, ''), v.value, v.dcml
from fsn.filing f
join fsn.value v on v.filing_id = f.id
join fsn.tag t on t.id = v.tag_id
join fsn.dim d on d.id = v.dim_id
where f.accession = any(%(acc)s) and v.qtrs in (0, 4) and coalesce(v.coreg, '') = '' and v.value is not null
  and exists (select 1 from unnest(%(pe)s::date[]) p(d) where v.ddate between p.d - 7 and p.d + 7)
"""
FILING_LINE_SQL = """
select f.accession, t.tag, l.report, l.stmt, coalesce(l.plabel, '')
from fsn.filing f join fsn.line l on l.filing_id = f.id join fsn.tag t on t.id = l.tag_id
where f.accession = any(%(acc)s)
"""


def sql_filing_facts(
    q, accessions: Iterable[str], period_ends: Iterable[str]
) -> tuple[list[FilingFact], list[FilingLine]]:
    """q(sql, params) -> rows (display_cert.SqlFactSource._q: read-only, own statement_timeout)."""
    from scrooner_pipeline.certification.display_cert import norm_dims

    acc = sorted(set(accessions))
    pe = sorted({p for p in period_ends if p})
    if not acc or not pe:
        return [], []
    facts = [
        FilingFact(
            a,
            t,
            str(d)[:10],
            int(qt),
            norm_dims(seg),
            Decimal(str(v)),
            32767 if dc is None else int(dc),
        )
        for a, t, d, qt, seg, v, dc in q(FILING_FACT_SQL, {"acc": acc, "pe": pe})
    ]
    lines = [
        FilingLine(a, t, int(r), s or "", pl or "")
        for a, t, r, s, pl in q(FILING_LINE_SQL, {"acc": acc})
    ]
    return facts, lines


def bundle_filing_facts(
    bundle: dict, accessions: Iterable[str]
) -> tuple[list[FilingFact], list[FilingLine]] | None:
    """Offline: bundle['filing_facts'] rows [acc, tag, ddate, qtrs, segments, value, dcml] and bundle['filing_lines']
    rows [acc, tag, report, stmt, plabel]. None when the bundle has no filing read (the checker did not run)."""
    from scrooner_pipeline.certification.display_cert import norm_dims

    if "filing_facts" not in bundle:
        return None
    acc = set(accessions)
    facts = [
        FilingFact(
            r[0],
            r[1],
            str(r[2])[:10],
            int(r[3]),
            norm_dims(r[4] or ""),
            Decimal(str(r[5])),
            32767 if len(r) < 7 or r[6] is None else int(r[6]),
        )
        for r in bundle["filing_facts"]
        if r[0] in acc and r[5] is not None
    ]
    lines = [
        FilingLine(r[0], r[1], int(r[2]), r[3] or "", r[4] or "")
        for r in bundle.get("filing_lines", [])
        if r[0] in acc
    ]
    return facts, lines


@dataclass(frozen=True)
class AutoCheck:
    data_point: str
    fiscal_year: str
    outcome: str  # AUTO_MATCH | AUTO_MISMATCH | NEEDS_READ
    method: (
        str  # family | label | parts | identity | text | per_share | sign | debt | none
    )
    filing_value: Decimal | None
    detail: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.data_point, self.fiscal_year)


def _days(a: str, b: str) -> int:
    return abs((date.fromisoformat(a) - date.fromisoformat(b)).days)


def _qtrs(dp: str) -> int:
    """0 for a balance (instant), 4 for an annual flow: the checker's own grain list (INSTANT)."""
    return 0 if dp in INSTANT else 4


class Filing:
    """The cited filing's facts, indexed for the checker: one fact per (tag, dims) at a period end, the closest date
    then the finest decimals (a filer can tag a face figure and a rounded note duplicate: WMT FY2023 372M / 400M)."""

    def __init__(self, facts: list[FilingFact], lines: list[FilingLine]):
        self.facts = facts
        self.lines = lines

    def fact(
        self, acc: str, tag: str, period_end: str, qtrs: int, dims: str = ""
    ) -> FilingFact | None:
        cand = [
            f
            for f in self.facts
            if f.accession == acc
            and f.tag == tag
            and f.dims == dims
            and f.qtrs == qtrs
            and period_end
            and _days(f.ddate, period_end) <= 7
        ]
        cand.sort(key=lambda f: (_days(f.ddate, period_end), -f.dcml))
        return cand[0] if cand else None

    def tier(self, acc: str, dp: str, period_end: str) -> tuple[int, list[FilingFact]]:
        """(tier index, facts) of the first family tier the filing tags at the period; (-1, []) when none."""
        for i, tags in enumerate(FAMILIES.get(dp, ())):
            got = [
                f
                for t in tags
                if (f := self.fact(acc, t, period_end, _qtrs(dp))) is not None
            ]
            if got:
                return i, got
        return -1, []

    def labelled(self, acc: str, label: str) -> list[str]:
        """Tags of the printed lines in the filing whose label is the badge's label (case, punctuation and an
        optional leading 'total' ignored)."""
        want = _norm_label(label)
        if not want:
            return []
        return sorted(
            {
                ln.tag
                for ln in self.lines
                if ln.accession == acc
                and (lab := _norm_label(ln.plabel))
                and (lab == want or (len(want) >= 12 and want in lab))
            }
        )


def _norm_label(s: str) -> str:
    s = re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower())
    s = re.sub(r"\s+", " ", s).strip()
    return s.removeprefix("total ").strip()


def _shown_matches(dp: str, shown: Decimal, filed: Decimal) -> tuple[bool, str]:
    """(match, why-not). Fixed-positive data points (polarity ruling: expenses, CF payments, DPS) show the magnitude;
    every other data point shows the filing's own sign. A negative fixed-positive cell never reaches here (check_cell
    fails it on sign first)."""
    if is_fixed_positive(dp):
        return abs(shown) == abs(filed), "value differs"
    if shown == filed:
        return True, ""
    if shown == -filed and filed != 0:
        return False, "sign: shown with the opposite sign of the filing's fact"
    return False, "value differs"


def _rounds_to(shown: Decimal, f: FilingFact) -> bool:
    """The shown value rounded to the fact's decimals equals the fact (magnitudes)."""
    if f.dcml >= 32767:
        return False
    q = Decimal(1).scaleb(-f.dcml)
    return abs(shown).quantize(q, rounding="ROUND_HALF_UP") == abs(f.value).quantize(q)


def _fmt(f: FilingFact) -> str:
    return f"{f.tag}{'[' + f.dims + ']' if f.dims else ''}={f.value} (dcml {f.dcml}, {f.ddate}, qtrs {f.qtrs})"


def _formula_shape(badge: str, signs: list[int]) -> str:
    """A derived badge's registry formula against the parts' signs: a named sum (a+b) has no subtracted part, a formula
    with a minus term has at least one. A sum of printed lines (sum(...)) keeps each line's calculation weight, so an
    income line inside an expense band is subtracted (AMZN, MU OtherOperatingIncomeExpenseNet): no shape rule. ''
    when consistent."""
    formula = badge.removeprefix("derived:")
    if formula.startswith(("zero_balance:", "sum(")):
        return ""
    minus = "-" in re.sub(r"\(.*?\)", "", formula)
    if not minus and any(s < 0 for s in signs):
        return f"formula {formula!r} subtracts nothing, but a part is subtracted"
    if minus and len(signs) > 1 and not any(s < 0 for s in signs):
        return f"formula {formula!r} subtracts a term, but no part is subtracted"
    return ""


def _check_parts(c: Cell, fl: Filing, shown: Decimal) -> AutoCheck:
    dp, fy = c.key
    q = _qtrs(dp)
    accs = {p.accession for p in c.parts}
    badge = c.badge or ""
    if badge.startswith("derived:") and len(accs | ({c.accession} - {""})) > 1:
        return AutoCheck(
            dp,
            fy,
            AUTO_MISMATCH,
            "parts",
            None,
            f"derivation uses more than one filing {sorted(accs)}",
        )
    total, ev = Decimal(0), []
    for p in c.parts:
        f = fl.fact(p.accession, p.tag, c.period_end, q, p.dims)
        if f is None:
            return AutoCheck(
                dp,
                fy,
                NEEDS_READ,
                "parts",
                None,
                f"no fact {p.tag}[{p.dims}] qtrs={q} near {c.period_end} in {p.accession}",
            )
        if f.value != p.value:
            return AutoCheck(
                dp,
                fy,
                AUTO_MISMATCH,
                "parts",
                f.value,
                f"part {p.tag}[{p.dims}] claimed {p.value}, the filing tags {_fmt(f)}",
            )
        total += p.sign * f.value
        ev.append(("-" if p.sign < 0 else "+") + _fmt(f))
    if badge.startswith("derived:") and (
        why := _formula_shape(badge, [p.sign for p in c.parts])
    ):
        return AutoCheck(dp, fy, AUTO_MISMATCH, "parts", total, why)
    if total != shown:
        return AutoCheck(
            dp,
            fy,
            AUTO_MISMATCH,
            "parts",
            total,
            f"parts sum to {total}, shown {shown}: " + " ".join(ev),
        )
    return AutoCheck(
        dp, fy, AUTO_MATCH, "parts", total, f"{len(c.parts)} parts: " + " ".join(ev)
    )


def _first(fl: Filing, acc: str, tags: Iterable[str], pe: str, q: int):
    return next((f for t in tags if (f := fl.fact(acc, t, pe, q)) is not None), None)


# A derived badge whose formula is one of the identities _identity computes; any other formula without parts (a
# sum of printed lines given as one tag) cannot be rebuilt from the facts alone.
IDENTITY_FORMULAS = {
    "total_liabilities": "liabilities_and_equity-total_equity-temporary_equity",
    "shares_outstanding": "shares_issued-treasury_shares",
    "gross_profit": "revenue-cost_of_revenue",
    "other_income_expense_net": "income_before_tax-operating_income+interest_expense-interest_income",
}


def _derived_no_parts(c: Cell, fl: Filing, shown: Decimal) -> AutoCheck:
    """A derived cell with no parts. When the filing itself prints the figure on a family line it is matched there
    (NVDA FY2016 prints total liabilities 2,814 beside a custom temporary-equity line the identity cannot see);
    otherwise its badge's identity is rebuilt from the filing's facts; any other formula goes to a read."""
    dp, fy = c.key
    _, got = fl.tier(c.accession, dp, c.period_end)
    hit = next((f for f in got if _shown_matches(dp, shown, f.value)[0]), None)
    if hit is not None:
        return AutoCheck(
            dp, fy, AUTO_MATCH, "family", hit.value, f"printed: {_fmt(hit)}"
        )
    formula = (c.badge or "").removeprefix("derived:")
    if dp in IDENTITY_FORMULAS and (not c.badge or formula == IDENTITY_FORMULAS[dp]):
        return _identity(c, fl, shown)
    return AutoCheck(
        dp,
        fy,
        NEEDS_READ,
        "identity",
        None,
        f"derived {c.badge or '(no badge)'} with no parts: the formula is not an identity the facts rebuild",
    )


def _identity(c: Cell, fl: Filing, shown: Decimal) -> AutoCheck:
    """A derived cell with no parts: its registry identity over the filing's own facts (never the shown cells)."""
    dp, fy = c.key
    acc, pe = c.accession, c.period_end
    val: Decimal | None = None
    ev = ""
    if dp == "total_liabilities":
        a = _first(fl, acc, ("Assets", "LiabilitiesAndStockholdersEquity"), pe, 0)
        e = _first(fl, acc, TOTAL_EQUITY, pe, 0)
        if a and e:
            temp = sum(
                (f.value for t in TEMP_EQUITY if (f := fl.fact(acc, t, pe, 0))),
                Decimal(0),
            )
            val, ev = (
                a.value - e.value - temp,
                f"{_fmt(a)} - {_fmt(e)} - temporary equity {temp}",
            )
    elif dp == "shares_outstanding":
        i = fl.fact(acc, "CommonStockSharesIssued", pe, 0)
        t = _first(fl, acc, ("TreasuryStockCommonShares", "TreasuryStockShares"), pe, 0)
        if i and t:
            val, ev = i.value - t.value, f"{_fmt(i)} - {_fmt(t)}"
    elif dp == "gross_profit":
        _, rev = fl.tier(acc, "revenue", pe)
        _, cor = fl.tier(acc, "cost_of_revenue", pe)
        if len(rev) == 1 and len(cor) == 1:
            val, ev = (
                rev[0].value - abs(cor[0].value),
                f"{_fmt(rev[0])} - {_fmt(cor[0])}",
            )
    elif dp == "other_income_expense_net":
        got = [
            fl.tier(acc, k, pe)[1]
            for k in (
                "income_before_tax",
                "operating_income",
                "interest_expense",
                "interest_income",
            )
        ]
        if all(len(g) == 1 for g in got):
            pt, oi, ie, ii = (g[0] for g in got)
            val = pt.value - oi.value + abs(ie.value) - abs(ii.value)
            ev = f"{_fmt(pt)} - {_fmt(oi)} + {_fmt(ie)} - {_fmt(ii)}"
    if val is None:
        return AutoCheck(
            dp,
            fy,
            NEEDS_READ,
            "identity",
            None,
            f"derived {c.badge or '(no badge)'}: no parts and no identity the filing's facts complete",
        )
    ok = val == shown
    return AutoCheck(
        dp,
        fy,
        AUTO_MATCH if ok else AUTO_MISMATCH,
        "identity",
        val,
        ("" if ok else f"identity gives {val}, shown {shown}: ") + ev,
    )


def check_cell(c: Cell, fl: Filing) -> AutoCheck:
    """One drawn SHOWN cell against the cited filing's facts. See the module docstring for the outcomes."""
    dp, fy = c.key
    shown = c.value if c.value is not None else Decimal(0)
    badge = c.badge or ""
    if dp in PER_SHARE and abs(shown) > PER_SHARE_CEILING:
        return AutoCheck(
            dp,
            fy,
            AUTO_MISMATCH,
            "per_share",
            None,
            f"implausible per-share value {shown} (> {PER_SHARE_CEILING})",
        )
    if is_fixed_positive(dp) and shown < 0 and not c.parts:
        return AutoCheck(
            dp,
            fy,
            AUTO_MISMATCH,
            "sign",
            None,
            f"sign: {dp} is fixed positive (polarity ruling) but shown {shown}",
        )
    if len(c.parts) > 1 or badge.startswith("derived:"):
        if c.parts:
            return _check_parts(c, fl, shown)
        return _derived_no_parts(c, fl, shown)
    if not c.accession or not c.period_end:
        return AutoCheck(
            dp, fy, NEEDS_READ, "none", None, "no filing or period to check"
        )
    if badge.startswith("combined:"):
        label = badge.removeprefix("combined:")
        tags = fl.labelled(c.accession, label)
        got = [
            f for t in tags if (f := fl.fact(c.accession, t, c.period_end, _qtrs(dp)))
        ]
        if not got:
            return AutoCheck(
                dp,
                fy,
                NEEDS_READ,
                "label",
                None,
                f"no printed line labelled {label!r} with a fact at {c.period_end} in {c.accession}",
            )
        for f in got:
            if _shown_matches(dp, shown, f.value)[0]:
                return AutoCheck(
                    dp, fy, AUTO_MATCH, "label", f.value, f"line {label!r}: {_fmt(f)}"
                )
        return AutoCheck(
            dp,
            fy,
            AUTO_MISMATCH,
            "label",
            got[0].value,
            f"line {label!r} holds "
            + "; ".join(_fmt(f) for f in got)
            + f", shown {shown}",
        )
    if not c.tag and not c.parts:
        return AutoCheck(
            dp,
            fy,
            NEEDS_READ,
            "text",
            None,
            f"text-stated value (no tagged fact): read the quote at {c.r_page or '?'} of {c.accession}",
        )
    tier, got = fl.tier(c.accession, dp, c.period_end)
    if not got:
        return AutoCheck(
            dp,
            fy,
            NEEDS_READ,
            "family",
            None,
            f"no fact of the checker's {dp} family at {c.period_end} in {c.accession} "
            "(custom, dimensioned or note-only line): read the filing",
        )
    why = ""
    for f in got:
        ok, why = _shown_matches(dp, shown, f.value)
        if ok:
            return AutoCheck(
                dp, fy, AUTO_MATCH, "family", f.value, f"tier {tier + 1}: {_fmt(f)}"
            )
    # Precision: the shown value equals a coarser duplicate of the same figure, not the finest one.
    coarse = [
        f
        for f in fl.facts
        if f.accession == c.accession
        and f.tag in {g.tag for g in got}
        and f.dims == ""
        and f.qtrs == _qtrs(dp)
        and _days(f.ddate, c.period_end) <= 7
        and _shown_matches(dp, shown, f.value)[0]
    ]
    if coarse:
        why = f"equals a rounded duplicate {_fmt(coarse[0])}, not the finest-decimals fact"
    elif all(f.dcml <= -7 and _rounds_to(shown, f) for f in got):
        # The only family fact is a rounded mention (a note's "$2.8 billion", dcml -8) that the exact shown figure
        # rounds to (MRK amortization 2,793 vs 2,800): consistent, not contradicted, but not proved either.
        return AutoCheck(
            dp,
            fy,
            NEEDS_READ,
            "family",
            got[0].value,
            f"the filing's only {dp} fact is rounded ({_fmt(got[0])}) and the shown {shown} rounds to it: read the line",
        )
    return AutoCheck(
        dp,
        fy,
        AUTO_MISMATCH,
        "family",
        got[0].value,
        f"{why}: tier {tier + 1} "
        + "; ".join(_fmt(f) for f in got)
        + f", shown {shown}",
    )


def check_draw(
    sample: list[Cell], facts: list[FilingFact], lines: list[FilingLine]
) -> list[AutoCheck]:
    fl = Filing(facts, lines)
    return [check_cell(c, fl) for c in sample]


def needs(sample: list[Cell]) -> tuple[set[str], set[str]]:
    """(accessions, period ends) the checker reads for a draw."""
    acc = {c.accession for c in sample if c.accession} | {
        p.accession for c in sample for p in c.parts
    }
    return acc, {c.period_end for c in sample if c.period_end}


def counts(checks: Iterable[AutoCheck]) -> dict[str, int]:
    out = dict.fromkeys(OUTCOMES, 0)
    for a in checks:
        out[a.outcome] += 1
    return out


# ---------------------------------------------------------------- filing reads (people or agents)
READ_VERDICTS = ("MATCH", "MISMATCH")


@dataclass(frozen=True)
class Read:
    data_point: str
    fiscal_year: str
    verdict: str  # MATCH | MISMATCH
    reader: str
    evidence: str


def load_reads(path: Path | None) -> dict[tuple[str, str], Read]:
    """A filing-read file (CSV: data_point, fiscal_year, verdict MATCH|MISMATCH, reader, evidence) for the drawn cells
    the machine could not settle. A row without a reader or evidence is refused: a read names who read what."""
    if path is None:
        return {}
    out: dict[tuple[str, str], Read] = {}
    with open(path, newline="") as fh:
        for i, r in enumerate(csv.DictReader(fh), start=2):
            v = (r.get("verdict") or "").strip().upper()
            reader = (r.get("reader") or "").strip()
            ev = (r.get("evidence") or "").strip()
            if v not in READ_VERDICTS or not reader or not ev:
                raise ValueError(
                    f"{path}:{i}: a read needs verdict MATCH|MISMATCH, a reader and evidence"
                )
            k = (r["data_point"].strip(), str(r["fiscal_year"]).strip())
            out[k] = Read(*k, v, reader, ev)
    return out


def verified_by(a: AutoCheck, reads: dict[tuple[str, str], Read]) -> str:
    """Who verified a drawn cell: 'machine' (AUTO_MATCH), 'read:<reader>' (a person or agent read the filing), or
    'pending_read' (NEEDS_READ / AUTO_MISMATCH with no read yet)."""
    if a.outcome == AUTO_MATCH:
        return "machine"
    r = reads.get(a.key)
    return f"read:{r.reader}" if r else "pending_read"


def read_queue(checks: Iterable[AutoCheck]) -> list[AutoCheck]:
    """The only drawn cells a person or agent reads: AUTO_MISMATCH first (each may be a wrong shown value)."""
    return sorted(
        (a for a in checks if a.outcome != AUTO_MATCH),
        key=lambda a: (a.outcome != AUTO_MISMATCH, a.key),
    )


# ---------------------------------------------------------------- audit of the checker itself (verifier samples it)
def audit_sample(
    checks: Iterable[AutoCheck], seed: str, rate: float = AUDIT_RATE
) -> list[AutoCheck]:
    """A seeded random ceil(rate x AUTO_MATCH) of the machine-matched cells (at least one when any), re-checked by
    an agent filing read so the checker's own error rate is measured, not assumed."""
    pool = sorted((a for a in checks if a.outcome == AUTO_MATCH), key=lambda a: a.key)
    if not pool:
        return []
    k = min(len(pool), max(1, math.ceil(rate * len(pool))))
    return sorted(random.Random(f"audit-{seed}").sample(pool, k), key=lambda a: a.key)


def audit_agreement(
    sample: list[AutoCheck], reads: dict[tuple[str, str], Read]
) -> dict:
    """Agreement of the agent's reads with the machine on the audit sample: agree = read MATCH on an AUTO_MATCH cell.
    A sampled cell without a read is 'unread' (the audit is incomplete, never counted as agreement)."""
    agree = sum(1 for a in sample if (r := reads.get(a.key)) and r.verdict == "MATCH")
    disagree = [
        a.key for a in sample if (r := reads.get(a.key)) and r.verdict != "MATCH"
    ]
    unread = [a.key for a in sample if a.key not in reads]
    done = agree + len(disagree)
    return {
        "sampled": len(sample),
        "read": done,
        "agree": agree,
        "disagree": [list(k) for k in disagree],
        "unread": [list(k) for k in unread],
        "agreement": None if not done else f"{agree / done:.4f}",
        "complete": not unread,
    }


AUDIT_COLUMNS = [
    "data_point",
    "fiscal_year",
    "machine",
    "filing_value",
    "machine_evidence",
    "verdict",
    "reader",
    "evidence",
]


def write_audit_request(path: Path, sample: list[AutoCheck]) -> None:
    """The audit sheet for the agent read: the reader fills verdict, reader and evidence (load_reads reads it)."""
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(AUDIT_COLUMNS)
        for a in sample:
            w.writerow(
                [
                    a.data_point,
                    a.fiscal_year,
                    a.outcome,
                    a.filing_value,
                    a.detail,
                    "",
                    "",
                    "",
                ]
            )
