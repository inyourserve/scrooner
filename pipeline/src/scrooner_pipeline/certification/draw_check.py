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

@2 (reads 2026-11-24, data-team/strategy/certification/reads-2026-11-24/checker-fixes-2026-11-24.txt): USD facts
only; a dcml -8 mention never proves a mismatch and a finer shown value matches a coarser fact at its decimals; an
unprinted family fact never overrules a printed line (PRECEDENCE_DPS: a read); printed tiers decide or rank with an
unprinted first tier (PRINTED_DECIDES / PRINTED_JOINS); label- and statement-gated family members (LABEL_GATED,
FACE_ONLY); other_income_expense_net by the printed band rule of definition 2026-11-21 (d) (_band), never an element
family; net income as ProfitLoss less the printed NCI share; operating expenses never total costs and expenses;
derived cells exported without a derived: badge rebuilt by their identity.

@3 (2026-11-22): three-source agreement (three_source): each checked cell's deciding FSN fact (AutoCheck.fact, or each
part of a summed cell) against the SEC companyfacts value of that tag, period and accession and the number printed on
the cited R page's line of that tag: AGREE3 (auto-proven), AGREE2 (one source missing), DISAGREE (may be a wrong
shown value), SINGLE (fewer than two sources). The AUTO_* outcomes are unchanged.

@4 (approver, 2026-11-29 cohort reads, data-team/strategy/certification/cohort/top100-cohort-reads-2026-11-29-verifier.md):
three checker false positives fixed. (a) A printed total whose calculation children (fsn.calc_arc) sum to it, with
the data point's own family line among them and no excluded child (CALC_CHILD_EXCLUDE), matches on the total
(C 2021 cash 262,033 = cash and due from banks 27,515 + deposits with banks 234,518; method "calc"). (b) The period
type (instant vs duration) of a data point comes from the registry statement (balance_sheet = instant, is_instant),
for this checker and the certifier's claim check (AXP 2017 Deposits was looked up as a 12-month value). (c) When the
filing tags no fact of the checker's family, the element the cell's claim names (the resolver/FSN structural
mapping, also a filer extension) matches when its undimensioned fact holds the shown value (QCOM 2018/2020
qcom_Interestpaidnetofinterestreceived; method "claim"); a family fact, when present, still decides.

@5 (approver review data-team/strategy/approvals/draw-check-4-review-2026-11-29.md): (a) a calc total matches only
when EVERY child is a family element or on the data point's allowlist (CALC_CHILD_ALLOW): cash plus
ShortTermInvestments is wider than cash and never matches. (c) a claimed element matches only when the filing
presents it on the cited R page (fsn.line) under a label that passes the data point's gate (CLAIM_LABEL_GATE); a
data point with no gate never matches by claim. The claim is no longer checked against itself (MA FY2025
InterestExpenseDebt, a claimed InterestExpense 722M). fsn.line holds the face statements only, so a claim printed
only in a note (QCOM R63/R57) is NEEDS_READ again.
"""

from __future__ import annotations

import csv
import json
import math
import random
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

from scrooner_pipeline.common.polarity import is_fixed_positive

if TYPE_CHECKING:  # import cycle: display_cert imports this module
    from scrooner_pipeline.certification.display_cert import Cell

CHECKER_VERSION = "draw_check@5"  # @5: calc children all admitted, claim needs a presented gated label; @4: calc totals, registry period type, claimed element (2026-11-29 reads); @3: three-source agreement; @2: fixes from the 2026-11-24 reads
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
            # reads 2026-11-24: CVX 2017 (OilAndGasRevenue), JNJ/KO 2015 (SalesRevenueGoodsNet), SHOP 2015/16
            # (SalesRevenueServicesNet), BLK (RevenuesExcludingInterestAndDividends)
            "OilAndGasRevenue",
            "SalesRevenueGoodsNet",
            "SalesRevenueServicesNet",
            "RevenuesExcludingInterestAndDividends",
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
        ("CostOfServices", "CostOfPurchasedOilAndGas"),
    ),
    "gross_profit": (("GrossProfit",),),
    "operating_income": (("OperatingIncomeLoss",),),
    # CostsAndExpenses includes cost of revenue (BMY 2018, QCOM 2021): registry step 2 is CostsAndExpenses minus
    # cost of revenue, a derivation (_opex_identity), never the family. NoninterestExpense: broker/asset-manager
    # "Total (non-interest) expenses" (SCHW, MS, GS, AXP).
    "operating_expenses": (
        ("OperatingExpenses",),
        (
            "OperatingCostsAndExpenses",
            "BenefitsLossesAndExpenses",
            "NoninterestExpense",
        ),
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
            "InterestExpenseBorrowings",
            "InterestExpenseAggregateExpenses",
        ),
        # by printed label only (LABEL_GATED): V 2015 / VRTX "Interest expense" tagged InterestIncomeExpenseNet,
        # SCCO InterestCostsIncurred, NEM "Interest expense, net of capitalized interest"
        (
            "InterestIncomeExpenseNet",
            "InterestCostsIncurred",
            "InterestIncomeExpenseNonoperatingNet",
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
            "InterestIncome",
        ),
        # by printed label "Interest income" only (LABEL_GATED): MU/FTNT InvestmentIncomeNet, MRVL
        # InvestmentIncomeNonoperating, SHOP/AMD net-interest elements, WELL loan interest
        (
            "InvestmentIncomeNet",
            "InvestmentIncomeNonoperating",
            "InterestIncomeExpenseNonoperatingNet",
            "InterestIncomeExpenseNet",
            "InterestAndFeeIncomeLoansAndLeases",
        ),
    ),
    # No element family: definition 2026-11-21 (d) is the band between operating income and pretax minus the
    # interest lines (_other_income). NonoperatingIncomeExpense is the band total with interest, and
    # OtherNonoperatingIncomeExpense is often only the note's "Other" row (AMGN 2023, BLK 2018/19/23, RTX 2020).
    "other_income_expense_net": (),
    "income_before_tax": (
        (
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxes",
        ),
    ),
    "income_tax_expense": (("IncomeTaxExpenseBenefit",),),
    # Parent net income. Without NetIncomeLoss, registry step 2: ProfitLoss minus
    # NetIncomeLossAttributableToNoncontrollingInterest when the income statement prints the NCI share (Filing.tier;
    # MA prints it only in the equity statement). Available-to-common is after preferred dividends, outside the
    # definition (AVGO 2020: 2,663 available to common, 2,960 net income): only for a filer that tags its net income
    # line with nothing else (TMO "Net Income").
    "net_income": (
        ("NetIncomeLoss",),
        ("ProfitLoss",),
        ("NetIncomeLossAvailableToCommonStockholdersBasic",),
    ),
    "comprehensive_income": (
        ("ComprehensiveIncomeNetOfTax",),
        (
            "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest",
        ),
    ),
    # Continuing-operations EPS is the total only when the filing has no discontinued operations (Filing.tier):
    # ADI 2015/17/18, AXP; never DELL FY2020/21 (a discontinued line exists).
    "basic_eps": (
        ("EarningsPerShareBasic", "EarningsPerShareBasicAndDiluted"),
        ("IncomeLossFromContinuingOperationsPerBasicShare",),
    ),
    "diluted_eps": (
        ("EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"),
        ("IncomeLossFromContinuingOperationsPerDilutedShare",),
    ),
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
        (
            "CashAndCashEquivalentsAtCarryingValue",
            "CashAndEquivalentsExcludingAssetsHeldForSale",
        ),
        # registry step 2 (a printed line also holding restricted cash, fed funds or short-term investments: BAC,
        # AXP face totals, CAT "cash and short-term investments"), a bank's cash line (JPM, MS "cash and due from
        # banks") and a company face tag (CVX): one tier, since the face prints one of them and not a total. The
        # restricted-cash total counts only as a balance-sheet line, never the CF reconciliation total (FACE_ONLY);
        # a CashAndCashEquivalentsAtCarryingValue that is only a CF total does not decide over them (Filing.tier).
        (
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
            "CashCashEquivalentsAndFederalFundsSold",
            "CashCashEquivalentsAndShortTermInvestments",
            "Cash",
            "CashAndDueFromBanks",
            "CashandCashEquivalentsExcludingTimeDepositsatCarryingValue",
            "CashAndCashEquivalentsExcludingTimeDeposits",
        ),
    ),
    # Tier 1 is the note split (X16) and decides over a wider face line even when the face prints the wider one
    # (BMY/CVX/MU/QCOM/VLO/ACN reads 2026-11-24): never in PRINTED_DECIDES.
    "accounts_receivable": (
        ("AccountsReceivableNetCurrent",),
        (
            "ReceivablesNetCurrent",
            "AccountsNotesAndLoansReceivableNetCurrent",
            "AccountsAndOtherReceivablesNetCurrent",
            "AccountsReceivableNet",
        ),
        ("PremiumsReceivableAtCarryingValue",),
    ),
    "inventory": (
        (
            "InventoryNet",
            "InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings",
            "InventoryOtherThanOreStockpilesOnLeachpadsNetOfReserves",
        ),
        ("MaterialsSuppliesAndOther",),
    ),
    # A face line holding finance-lease ROU with PP&E decides over an unprinted PropertyPlantAndEquipmentNet
    # (LRCX 2023/2026, PRINTED_DECIDES); an operating-lease ROU combination is outside the definition (GE).
    "ppe_net": (
        ("PropertyPlantAndEquipmentNet",),
        (
            "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization",
            "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetExcludingLessorAssetUnderOperatingLeaseAfterAccumulatedDepreciationAndAmortization",
            "PublicUtilitiesPropertyPlantAndEquipmentNet",
        ),
        ("RealEstateInvestmentPropertyNet",),
    ),
    "goodwill": (("Goodwill",),),
    "accounts_payable": (
        ("AccountsPayableCurrent",),
        ("AccountsPayableTradeCurrent",),
        ("AccountsPayableCurrentAndNoncurrent",),
    ),
    # Total equity with NCI is parent equity only when the filing has no NCI fact at the period (Filing.tier):
    # AVGO 2024/25, V, JNJ, QCOM.
    "stockholders_equity": (
        ("StockholdersEquity",),
        ("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",),
    ),
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
        (
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "PaymentsToAcquireOtherPropertyPlantAndEquipment",
        ),
        ("PaymentsToAcquireProductiveAssets", "PaymentsToAcquireOtherProductiveAssets"),
    ),
    # DepreciationAndAmortizationIncludingDiscontinuedOperations: the CF add-back, where the segment-note
    # DepreciationAndAmortization is continuing operations only (LMT 2015). Depreciation decides only as a CF line
    # (FACE_ONLY): the sole D&A add-back (UNP, PGR).
    "depreciation_and_amortization": (
        (
            "DepreciationDepletionAndAmortization",
            "DepreciationAndAmortization",
            "DepreciationAmortizationAndAccretionNet",
            "DepreciationAndAmortizationIncludingDiscontinuedOperations",
            "OtherDepreciationAndAmortization",
        ),
        ("Depreciation",),
    ),
    # IS-face lines for acquired-intangible amortization (PFE, BMY company tag); AdjustmentForAmortization and
    # AmortizationAndImpairmentOfIntangibleAssets only by their printed label (LABEL_GATED): WELL "Other
    # amortization expenses" is debt costs, GOOG "Amortization and impairment" holds impairment.
    "amortization_of_intangibles": (
        (
            "AmortizationOfIntangibleAssets",
            "AmortizationOfIntangibleAssetsNotAssociatedWithSingleFunction",
            "AmortizationofAcquiredIntangibleAssets",
            "AdjustmentForAmortization",
            "AmortizationAndImpairmentOfIntangibleAssets",
        ),
    ),
    "sbc": (
        ("ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"),
        ("RestrictedStockExpense",),
    ),
    # A printed CF payment line decides over an unprinted equity-statement element (WELL 2019/2025, PRINTED_DECIDES).
    "dividends_paid": (
        ("PaymentsOfDividendsCommonStock", "PaymentsOfOrdinaryDividends"),
        ("PaymentsOfDividends",),
    ),
    "share_buybacks": (
        ("PaymentsForRepurchaseOfCommonStock",),
        ("PaymentsForRepurchaseOfEquity",),
    ),
    "cash_paid_for_interest": (
        (
            "InterestPaidNet",
            "InterestPaid",
            "InterestPaidOnLongTermDebt",
            "InterestPaidContractualInterest",
        ),
    ),
    # GE's printed CF line (company tag) beside an unprinted ASU 2023-09 note total (GE 2023/2024).
    "cash_paid_for_income_taxes": (
        (
            "IncomeTaxesPaidNet",
            "IncomeTaxesPaid",
            "CashPaidReceivedForIncomeTaxesNetOfDiscontinuedOperations",
        ),
    ),
    "cf_ar_change": (
        (
            "IncreaseDecreaseInAccountsReceivable",
            "IncreaseDecreaseInReceivables",
            "IncreaseDecreaseInAccountsAndNotesReceivable",
            "IncreaseDecreaseInAccountsReceivableExcludingAcquisitionRelated",
        ),
        ("IncreaseDecreaseInAccountsAndOtherReceivables",),
    ),
    "cf_inventory_change": (
        ("IncreaseDecreaseInInventories", "IncreaseDecreaseInRetailRelatedInventories"),
        ("IncreaseDecreaseInMaterialsAndSupplies",),
    ),
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
            "ProvisionForLoanLossesExpensed",
            "FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal",
        ),
    ),
    "loans_net": (
        (
            "LoansAndLeasesReceivableNetReportedAmount",
            "FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss",
        ),
        ("NotesReceivableNet",),
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


@cache
def registry_instant() -> frozenset[str]:
    """Data points whose registry statement is the balance sheet (metrics/registry/data_points.csv): instants."""
    from scrooner_pipeline.metrics.registry import load_data_points

    return frozenset(
        dp
        for (dp, _s), d in load_data_points().items()
        if d.statement == "balance_sheet"
    )


def is_instant(dp: str) -> bool:
    """A balance (instant, qtrs 0) rather than a flow (duration): the registry's statement, or the checker's own list."""
    return dp in INSTANT or dp in registry_instant()


# A calculation child that makes a printed total wider than the data point: the total never matches on it
# (cash excludes restricted cash, Dhairya 2026-11-22; CAT/CVX cash-and-restricted-cash totals stay mismatches).
CALC_CHILD_EXCLUDE: dict[str, re.Pattern] = {
    "cash_and_equivalents": re.compile(r"Restricted"),
}
# The calculation children a printed total may hold beside the family's own elements and still be the data point
# (approver 2026-11-29: every child admitted, else the total is wider). Cash: a bank's cash lines (C 2021) and fed
# funds sold, part of the bank template's cash.
CALC_CHILD_ALLOW: dict[str, frozenset[str]] = {
    "cash_and_equivalents": frozenset(
        {
            "CashAndDueFromBanks",
            "InterestBearingDepositsInBanks",
            "FederalFundsSold",
        }
    ),
}
# A claimed element outside the family matches only when the filing prints it on the cited R page under a label of
# this pattern (normalized, _norm_label): QCOM "Interest paid, net of interest received". No gate, no claim match.
CLAIM_LABEL_GATE: dict[str, str] = {
    "cash_paid_for_interest": r"\binterest paid\b",
}

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


# A tag that holds the data point only when the filing prints it with this label (normalized, _norm_label).
_INTEREST_INCOME_LABEL = r"^interest income( net)?$"
_INTEREST_EXPENSE_LABEL = r"^(interest expense|contractual interest expense|interest expense net of capitalized interest)$"
LABEL_GATED: dict[tuple[str, str], str] = (
    {
        ("interest_income", t): _INTEREST_INCOME_LABEL
        for t in (
            "InvestmentIncomeNet",
            "InvestmentIncomeNonoperating",
            "InterestIncomeExpenseNonoperatingNet",
            "InterestIncomeExpenseNet",
            "InterestAndFeeIncomeLoansAndLeases",
        )
    }
    | {
        ("interest_expense", t): _INTEREST_EXPENSE_LABEL
        for t in (
            "InterestIncomeExpenseNet",
            "InterestCostsIncurred",
            "InterestIncomeExpenseNonoperatingNet",
        )
    }
    | {
        # GILD "Amortization expense", MRK "Amortization"; never WELL "Other amortization expenses" (debt costs)
        ("amortization_of_intangibles", "AdjustmentForAmortization"): (
            r"^(amortization|amortization expense|amortization of (acquired |purchased )?intangible assets?)$"
        ),
        # MRVL "Amortization of acquired intangible assets"; never GOOG "Amortization and impairment of ..."
        (
            "amortization_of_intangibles",
            "AmortizationAndImpairmentOfIntangibleAssets",
        ): (r"^amortization of (acquired |purchased )?intangible assets?$"),
    }
)
_PRETAX_LABEL = re.compile(
    r"^(income|earnings|profit)( loss)?( from continuing operations)?( including noncontrolling interests?)?"
    r" before (provision for )?(income )?tax(es)?$"
)
# Printed-line precedence applies to the data points whose reads proved it (2026-11-24: BMY/PFE/DHR amortization,
# GE cash taxes, KLAC cf_ar, LMT D&A, LRCX ppe, WELL dividends); a note split that decides over a printed face line
# (accounts_receivable X16, SCCO income tax = current-and-royalty + deferred lines) stays a mismatch.
PRECEDENCE_DPS = frozenset(
    {
        "amortization_of_intangibles",
        "cash_paid_for_income_taxes",
        "cf_ar_change",
        "depreciation_and_amortization",
        "ppe_net",
        "dividends_paid",
    }
)
# A tag that holds the data point only as a line of this statement: the restricted-cash total is the CF
# reconciliation total unless the balance sheet prints it (CAT 2019, CVX 2019-2025); Depreciation is the D&A
# add-back only on the cash flow statement (UNP, PGR).
FACE_ONLY: dict[tuple[str, str], str] = {
    (
        "cash_and_equivalents",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    ): "BS",
    ("depreciation_and_amortization", "Depreciation"): "CF",
}
# Data points where a first tier the filing does not print (no fsn.line, or none on this statement when one is
# named) does not decide alone. PRINTED_DECIDES: the first later tier the filing prints decides instead (LRCX ppe
# 2023/2026: the face's PP&E-with-finance-lease-ROU line over an unprinted PropertyPlantAndEquipmentNet).
# PRINTED_JOINS: that printed tier ranks with it, either may hold the figure (WELL dividends 2019/2025 print the CF
# payment while AVGO's printed line also holds preferred dividends; MS 2017 cash and due from banks beside a
# CashAndCashEquivalentsAtCarryingValue that is only the CF total, C 2024 shows that total). accounts_receivable is
# deliberately absent (X16: the note split decides over the wider face line).
PRINTED_DECIDES: dict[str, str] = {"ppe_net": ""}
PRINTED_JOINS: dict[str, str] = {"dividends_paid": "", "cash_and_equivalents": "BS"}
# Dimensions that are the company-level figure of a family element (ruling 9): the common stock member of the
# equity components axis (MA "Cash dividends declared on Class A and Class B common stock, per share").
COMPANY_LEVEL_MEMBERS = frozenset({"EquityComponents=CommonStock"})
# Compared as magnitudes although outside the polarity ruling's fixed-positive list: a filer stores the tax payment
# negative (UNP 2021 IncomeTaxesPaidNet -1,658).
MAGNITUDE = frozenset({"cash_paid_for_income_taxes"})
# A fact rounded to this many decimals or coarser (a note's "$9.9 billion", dcml -8) never proves a mismatch.
ROUNDED_MENTION_DCML = -8


def usd_unit(uom: str) -> bool:
    """A USD (or unit-less, shares, pure) fact: no currency other than USD in the unit (CB tags DPS in USD and CHF)."""
    toks = re.split(r"[^A-Za-z]+", uom or "")
    return not any(len(t) == 3 and t.isupper() and t != "USD" for t in toks)


@dataclass(frozen=True)
class FilingFact:
    accession: str
    tag: str
    ddate: str
    qtrs: int
    dims: str
    value: Decimal
    dcml: int = 32767  # higher is more precise; unknown precision counts as exact
    uom: str = ""  # fsn.value.uom ('USD', 'USD/shares', 'CHF/shares', 'shares'); '' when unknown


@dataclass(frozen=True)
class CalcArc:
    """One calculation arc of the filing (fsn.calc_arc): parent = sum of weight * child within a group."""

    accession: str
    grp: int
    parent: str
    child: str
    weight: int


@dataclass(frozen=True)
class FilingLine:
    accession: str
    tag: str
    report: int
    stmt: str
    plabel: str
    line: int = 0  # position on the statement (fsn.line.line); 0 when unknown
    negating: bool = (
        False  # the filer prints the fact with the opposite sign (a negated label)
    )


# One read of the filing itself: every undimensioned or dimensioned fact (no co-registrant) at the drawn period ends,
# whatever its tag. Deliberately not the certifier's FACT_SQL (which reads only the cited tags).
FILING_FACT_SQL = """
select f.accession, t.tag, v.ddate::text, v.qtrs, coalesce(d.segments, ''), v.value, v.dcml,
       coalesce(v.uom, '')
from fsn.filing f
join fsn.value v on v.filing_id = f.id
join fsn.tag t on t.id = v.tag_id
join fsn.dim d on d.id = v.dim_id
where f.accession = any(%(acc)s) and v.qtrs in (0, 4) and coalesce(v.coreg, '') = '' and v.value is not null
  and exists (select 1 from unnest(%(pe)s::date[]) p(d) where v.ddate between p.d - 7 and p.d + 7)
"""
FILING_LINE_SQL = """
select f.accession, t.tag, l.report, l.stmt, coalesce(l.plabel, ''), coalesce(l.line, 0), coalesce(l.negating, false)
from fsn.filing f join fsn.line l on l.filing_id = f.id join fsn.tag t on t.id = l.tag_id
where f.accession = any(%(acc)s)
"""


FILING_CALC_SQL = """
select f.accession, a.grp, pt.tag, ct.tag, a.weight
from fsn.filing f join fsn.calc_arc a on a.filing_id = f.id
join fsn.tag pt on pt.id = a.parent_tag_id join fsn.tag ct on ct.id = a.child_tag_id
where f.accession = any(%(acc)s)
"""


def sql_filing_calc(q, accessions: Iterable[str]) -> list[CalcArc]:
    acc = sorted(set(accessions))
    if not acc:
        return []
    return [
        CalcArc(a, int(g), p, ch, int(w))
        for a, g, p, ch, w in q(FILING_CALC_SQL, {"acc": acc})
    ]


def bundle_filing_calc(bundle: dict, accessions: Iterable[str]) -> list[CalcArc]:
    """Offline: bundle['filing_calc'] rows [acc, grp, parent, child, weight]; [] when the bundle has none."""
    acc = set(accessions)
    return [
        CalcArc(r[0], int(r[1]), r[2], r[3], int(r[4]))
        for r in bundle.get("filing_calc", [])
        if r[0] in acc
    ]


def read_calc(source, accessions: Iterable[str]) -> list[CalcArc]:
    """The cited filings' calculation arcs from a source that can read them ([] otherwise: no calc match)."""
    read = getattr(source, "filing_calc", None)
    return list(read(accessions) or []) if read is not None else []


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
            u or "",
        )
        for a, t, d, qt, seg, v, dc, u in q(FILING_FACT_SQL, {"acc": acc, "pe": pe})
    ]
    lines = [
        FilingLine(a, t, int(r), s or "", pl or "", int(n or 0), bool(neg))
        for a, t, r, s, pl, n, neg in q(FILING_LINE_SQL, {"acc": acc})
    ]
    return facts, lines


def bundle_filing_facts(
    bundle: dict, accessions: Iterable[str]
) -> tuple[list[FilingFact], list[FilingLine]] | None:
    """Offline: bundle['filing_facts'] rows [acc, tag, ddate, qtrs, segments, value, dcml, uom] (dcml and uom
    optional) and bundle['filing_lines'] rows [acc, tag, report, stmt, plabel, line, negating] (line and negating
    optional). None when the bundle has no filing
    read (the checker did not run)."""
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
            (r[7] or "") if len(r) > 7 else "",
        )
        for r in bundle["filing_facts"]
        if r[0] in acc and r[5] is not None
    ]
    lines = [
        FilingLine(
            r[0],
            r[1],
            int(r[2]),
            r[3] or "",
            r[4] or "",
            int(r[5] or 0) if len(r) > 5 else 0,
            bool(r[6]) if len(r) > 6 else False,
        )
        for r in bundle.get("filing_lines", [])
        if r[0] in acc
    ]
    return facts, lines


@dataclass(frozen=True)
class AutoCheck:
    data_point: str
    fiscal_year: str
    outcome: str  # AUTO_MATCH | AUTO_MISMATCH | NEEDS_READ
    method: str  # family | label | parts | identity (a formula, or the identity web) | calc | claim | text | per_share | sign | debt | none
    filing_value: Decimal | None
    detail: str
    # the one filing fact that decided a single-element cell (AUTO_MATCH or AUTO_MISMATCH); the three-source
    # check reads that fact's tag in companyfacts and on the printed page. None for parts, identities and reads.
    fact: FilingFact | None = None

    @property
    def key(self) -> tuple[str, str]:
        return (self.data_point, self.fiscal_year)


def _days(a: str, b: str) -> int:
    return abs((date.fromisoformat(a) - date.fromisoformat(b)).days)


def _qtrs(dp: str) -> int:
    """0 for a balance (instant), 4 for an annual flow: the registry's period type (is_instant)."""
    return 0 if is_instant(dp) else 4


class Filing:
    """The cited filing's facts, indexed for the checker: one fact per (tag, dims) at a period end, the closest date
    then the finest decimals (a filer can tag a face figure and a rounded note duplicate: WMT FY2023 372M / 400M).
    Only USD facts are kept (a fact in another currency is never the shown figure: CB DPS 2024 in CHF)."""

    def __init__(
        self,
        facts: list[FilingFact],
        lines: list[FilingLine],
        calc: Iterable[CalcArc] = (),
    ):
        self.facts = [f for f in facts if usd_unit(f.uom)]
        self.lines = lines
        self._printed: dict[tuple[str, str], list[FilingLine]] = {}
        for ln in lines:
            self._printed.setdefault((ln.accession, ln.tag), []).append(ln)
        self._calc: dict[tuple[str, str], dict[int, list[CalcArc]]] = {}
        for a in calc:
            self._calc.setdefault((a.accession, a.parent), {}).setdefault(
                a.grp, []
            ).append(a)

    def calc_total(
        self, acc: str, dp: str, tag: str, period_end: str
    ) -> tuple[FilingFact, list[tuple[int, FilingFact]]] | None:
        """(total, [(weight, child fact)]) when the filing's calculation of `tag` holds at the period: every child
        has an undimensioned fact, their weighted sum equals the total's fact, one child is an element of the data
        point's family (the data point's own line is inside the total), every child is a family element or on the
        data point's allowlist (CALC_CHILD_ALLOW) and no child is excluded (CALC_CHILD_EXCLUDE). None otherwise."""
        q = _qtrs(dp)
        total = self.fact(acc, tag, period_end, q)
        if total is None:
            return None
        family = {t for tags in FAMILIES.get(dp, ()) for t in tags}
        excl = CALC_CHILD_EXCLUDE.get(dp)
        admitted = family | CALC_CHILD_ALLOW.get(dp, frozenset())
        for _g, arcs in sorted(self._calc.get((acc, tag), {}).items()):
            found = [(a.weight, self.fact(acc, a.child, period_end, q)) for a in arcs]
            kids = [(w, f) for w, f in found if f is not None]
            if len(kids) != len(found):
                continue
            if not any(a.child in family for a in arcs):
                continue
            if not all(a.child in admitted for a in arcs):
                continue
            if excl is not None and any(excl.search(a.child) for a in arcs):
                continue
            if sum((w * f.value for w, f in kids), Decimal(0)) == total.value:
                return total, kids
        return None

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

    def printed(self, acc: str, tag: str, stmt: str = "") -> list[FilingLine]:
        """The filing's printed lines (fsn.line) of a tag, on one statement when stmt is given."""
        return [
            ln
            for ln in self._printed.get((acc, tag), ())
            if not stmt or ln.stmt == stmt
        ]

    def _admit(self, acc: str, dp: str, f: FilingFact, period_end: str) -> bool:
        """A family fact counts only when its gate holds: a printed label (LABEL_GATED), a statement
        (FACE_ONLY), no NCI (total equity as parent equity) or no discontinued operations (continuing EPS)."""
        rx = LABEL_GATED.get((dp, f.tag))
        if rx is not None and not any(
            re.search(rx, _norm_label(ln.plabel)) for ln in self.printed(acc, f.tag)
        ):
            return False
        st = FACE_ONLY.get((dp, f.tag))
        if st is not None and not self.printed(acc, f.tag, st):
            return False
        if (
            dp == "stockholders_equity"
            and f.tag
            == "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
        ):
            return self.fact(acc, "MinorityInterest", period_end, 0) is None
        if f.tag.startswith("IncomeLossFromContinuingOperationsPer"):
            return not any(
                g.accession == acc
                and g.tag.startswith("IncomeLossFromDiscontinuedOperations")
                and g.dims == ""
                and g.value != 0
                for g in self.facts
            )
        return True

    def _tier_facts(
        self, acc: str, dp: str, tags: Iterable[str], period_end: str
    ) -> list[FilingFact]:
        got = [
            f
            for t in tags
            if (f := self.fact(acc, t, period_end, _qtrs(dp))) is not None
            and self._admit(acc, dp, f, period_end)
        ]
        if dp == "net_income" and got and got[0].tag == "ProfitLoss":
            # registry step 2: ProfitLoss minus the NCI share the income statement prints
            nci = self.fact(
                acc, "NetIncomeLossAttributableToNoncontrollingInterest", period_end, 4
            )
            if nci is not None and self.printed(
                acc, "NetIncomeLossAttributableToNoncontrollingInterest", "IS"
            ):
                p = got[0]
                got = [
                    FilingFact(
                        acc,
                        "ProfitLoss-NetIncomeLossAttributableToNoncontrollingInterest",
                        p.ddate,
                        p.qtrs,
                        "",
                        p.value - nci.value,
                        min(p.dcml, nci.dcml),
                        p.uom,
                    )
                ]
        if dp == "revenue" and len(got) > 1:
            # "Total revenues and other income" (CVX) is not revenue while a narrower revenue line is printed
            narrow = [
                f
                for f in got
                if not any(
                    "other income" in _norm_label(ln.plabel)
                    for ln in self.printed(acc, f.tag)
                )
            ]
            if narrow and any(self.printed(acc, f.tag, "IS") for f in narrow):
                got = narrow
        if dp == "share_buybacks" and any(
            "and other" in _norm_label(ln.plabel)
            for f in got
            for ln in self.printed(acc, f.tag, "CF")
        ):
            # AXP 2023: the CF line "repurchase of shares and other" is wider; the equity statement's repurchase
            # of common shares is the data point
            if (
                t := self.fact(
                    acc, "TreasuryStockValueAcquiredCostMethod", period_end, 4
                )
            ) is not None:
                got = [*got, t]
        return got

    def tier(self, acc: str, dp: str, period_end: str) -> tuple[int, list[FilingFact]]:
        """(tier index, facts) of the first family tier the filing tags at the period; (-1, []) when none. For a
        PRINTED_DECIDES data point a tier the filing does not print yields to a later tier it prints."""
        tiers = [
            (i, g)
            for i, tags in enumerate(FAMILIES.get(dp, ()))
            if (g := self._tier_facts(acc, dp, tags, period_end))
        ]
        if not tiers and dp == "income_before_tax":
            # a custom pretax element on the income statement, by its printed label (ORCL, PG, SHOP)
            got = [
                f
                for ln in self.lines
                if ln.accession == acc
                and ln.stmt == "IS"
                and _PRETAX_LABEL.search(_norm_label(ln.plabel))
                and (f := self.fact(acc, ln.tag, period_end, 4)) is not None
            ]
            if got:
                tiers = [(len(FAMILIES[dp]), got[:1])]
        if not tiers:
            return -1, []
        rule = PRINTED_DECIDES if dp in PRINTED_DECIDES else PRINTED_JOINS
        if dp in rule and not any(
            self.printed(acc, f.tag, rule[dp]) for f in tiers[0][1]
        ):
            later = next(
                (
                    (i, g)
                    for i, g in tiers[1:]
                    if any(self.printed(acc, f.tag, rule[dp]) for f in g)
                ),
                None,
            )
            if later is not None:
                return (
                    later
                    if rule is PRINTED_DECIDES
                    else (tiers[0][0], tiers[0][1] + later[1])
                )
        return tiers[0]

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
    if is_fixed_positive(dp) or dp in MAGNITUDE:
        return abs(shown) == abs(filed), "value differs"
    if shown == filed:
        return True, ""
    if shown == -filed and filed != 0:
        return False, "sign: shown with the opposite sign of the filing's fact"
    return False, "value differs"


def _rounds_to(shown: Decimal, f: FilingFact) -> bool:
    """The shown value, finer than the fact, rounded to the fact's decimals equals the fact (magnitudes). A fact that
    is not a whole number of its own unit (or zero) proves nothing at that precision."""
    if f.dcml >= 32767 or f.value == 0:
        return False
    unit = Decimal(1).scaleb(-f.dcml)
    if f.value % unit != 0 or shown % unit == 0:
        return False
    return abs(shown).quantize(unit, rounding="ROUND_HALF_UP") == abs(f.value).quantize(
        unit
    )


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
            if (
                dp == "other_income_expense_net"
                and f.value == -p.value
                and (band := _band(fl, c.accession, c.period_end)) is not None
                and band.value == shown
            ):
                # the part's XBRL sign contradicts the printed total identity, which proves the shown value
                # (T 2019 IncomeLossFromEquityMethodInvestments tagged -6, the printed band proves +6)
                return AutoCheck(
                    dp,
                    fy,
                    AUTO_MATCH,
                    "identity",
                    shown,
                    f"part {p.tag} tagged {f.value}, claimed {p.value}; the band proves the shown value: {band.evidence}",
                )
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
        # total costs and expenses - cost of revenue is evaluated from the filing's facts, not from the cited
        # parts list (QCOM 2021 cites R&D + SG&A)
        if dp == "operating_expenses" and (ox := _opex_identity(c, fl, shown)):
            return ox
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
    "stockholders_equity": "total_equity-noncontrolling_interest",
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
    if dp == "other_income_expense_net" and formula.startswith("sum("):
        # a sum of the printed nonoperating lines given as one figure: the band rule rebuilds it (VZ, KO)
        return _other_income(c, fl, shown)
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
        bd = _band(fl, acc, pe)
        if bd is not None and bd.complete and not bd.coarse:
            val, ev = bd.value, "band: " + bd.evidence
    elif dp == "stockholders_equity":
        # CAT 2016: badge total_equity-noncontrolling_interest, value = the total with NCI (NCI 76 printed)
        t = fl.fact(acc, TOTAL_EQUITY[0], pe, 0)
        n = fl.fact(acc, "MinorityInterest", pe, 0)
        if t and n:
            val, ev = t.value - n.value, f"{_fmt(t)} - {_fmt(n)}"
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
                    dp,
                    fy,
                    AUTO_MATCH,
                    "label",
                    f.value,
                    f"line {label!r}: {_fmt(f)}",
                    f,
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
            got[0],
        )
    if not c.tag and not c.parts:
        if dp in IDENTITY_FORMULAS:
            # a derived cell exported without its derived: badge (GILD gross profit, total liabilities): its
            # registry identity over the filing's facts settles it when they complete it and agree
            r = _derived_no_parts(c, fl, shown)
            if r.outcome != AUTO_MATCH:
                r = _identity(c, fl, shown)
            if r.outcome == AUTO_MATCH:
                return r
        return AutoCheck(
            dp,
            fy,
            NEEDS_READ,
            "text",
            None,
            f"text-stated value (no tagged fact): read the quote at {c.r_page or '?'} of {c.accession}",
        )
    if dp == "other_income_expense_net":
        return _other_income(c, fl, shown)
    tier, got = fl.tier(c.accession, dp, c.period_end)
    if not got:
        if dp == "operating_expenses" and (ox := _opex_identity(c, fl, shown)):
            return ox
        if len(c.parts) == 1 and c.parts[0].dims in COMPANY_LEVEL_MEMBERS:
            # the company-level member of a family element (ruling 9: MA DPS 2020/21 on
            # EquityComponents=CommonStock, the Class A and B common stock line)
            p = c.parts[0]
            f = fl.fact(c.accession, p.tag, c.period_end, _qtrs(dp), p.dims)
            if f is not None and any(p.tag in tags for tags in FAMILIES.get(dp, ())):
                ok = _shown_matches(dp, shown, f.value)[0]
                return AutoCheck(
                    dp,
                    fy,
                    AUTO_MATCH if ok else AUTO_MISMATCH,
                    "family",
                    f.value,
                    ("" if ok else f"value differs, shown {shown}: ")
                    + f"company-level member {_fmt(f)}",
                    f,
                )
        if (cl := _claimed_element(c, fl, shown)) is not None:
            return cl
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
                dp, fy, AUTO_MATCH, "family", f.value, f"tier {tier + 1}: {_fmt(f)}", f
            )
    # Coarser decimals: the shown figure (from a finer face line) rounds to the family fact at the fact's own
    # decimals (DHR 2016 amortization 583.1 vs the note's 583, dcml -6). A rounded mention is never a match.
    for f in got:
        if ROUNDED_MENTION_DCML < f.dcml < 32767 and _rounds_to(shown, f):
            if is_fixed_positive(dp) or dp in MAGNITUDE or (shown < 0) == (f.value < 0):
                return AutoCheck(
                    dp,
                    fy,
                    AUTO_MATCH,
                    "family",
                    f.value,
                    f"tier {tier + 1}: {_fmt(f)}, shown {shown} rounds to it at the fact's decimals",
                    f,
                )
    if (ct := _calc_total(c, fl, shown)) is not None:
        return ct
    if dp == "operating_expenses" and (ox := _opex_identity(c, fl, shown)):
        return ox
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
    elif all(f.dcml <= ROUNDED_MENTION_DCML for f in got):
        # The only family fact is a rounded mention (a note's "$9.9 billion", dcml -8): it can never prove the exact
        # shown figure wrong (MRK amortization 2,793 vs 2,800; BMY 2020 9,688 vs 9.9 billion; CVX 2020 receivables).
        return AutoCheck(
            dp,
            fy,
            NEEDS_READ,
            "family",
            got[0].value,
            f"the filing's only {dp} fact is rounded ({_fmt(got[0])}), shown {shown}: read the line",
        )
    if (pr := _printed_elsewhere(c, fl, shown, got)) is not None:
        return pr
    return AutoCheck(
        dp,
        fy,
        AUTO_MISMATCH,
        "family",
        got[0].value,
        f"{why}: tier {tier + 1} "
        + "; ".join(_fmt(f) for f in got)
        + f", shown {shown}",
        got[0],
    )


def _cited_tag(c: Cell) -> str:
    """The export's tag for a single-element cell (its tag column, or its one part)."""
    t = c.tag or (c.parts[0].tag if len(c.parts) == 1 else "")
    return t.strip().split(":")[-1]


def _calc_total(c: Cell, fl: Filing, shown: Decimal) -> AutoCheck | None:
    """A printed total the cell cites whose calculation children sum to the shown value (Filing.calc_total) matches on
    the total, not on the one family child it contains (C 2021: cash, due from banks and deposits with banks 262,033 =
    CashAndDueFromBanks 27,515 + InterestBearingDepositsInBanks 234,518)."""
    t = _cited_tag(c)
    if not t or not fl.printed(c.accession, t):
        return None
    got = fl.calc_total(c.accession, c.data_point, t, c.period_end)
    if got is None or not _shown_matches(c.data_point, shown, got[0].value)[0]:
        return None
    total, kids = got
    return AutoCheck(
        c.data_point,
        c.fiscal_year,
        AUTO_MATCH,
        "calc",
        total.value,
        f"printed total {_fmt(total)} = "
        + " ".join(("-" if w < 0 else "+") + _fmt(f) for w, f in kids),
        total,
    )


def _claimed_element(c: Cell, fl: Filing, shown: Decimal) -> AutoCheck | None:
    """No family fact: the element the cell's claim names (the resolver/FSN structural mapping, a filer extension
    such as qcom_Interestpaidnetofinterestreceived) matches when its undimensioned fact at the period holds the shown
    value. Only reached when the filing tags no admitted fact of the family, so a family fact still decides when
    present; a family element its gate refused (LABEL_GATED, FACE_ONLY, continuing EPS) is never readmitted here.
    The element must be presented on the cited R page (fsn.line) under a label passing CLAIM_LABEL_GATE, so the claim
    is never checked against itself (@5)."""
    t = _cited_tag(c)
    gate = CLAIM_LABEL_GATE.get(c.data_point)
    rp = (c.r_page or "").removeprefix("R")
    if not t or gate is None or not rp.isdigit():
        return None
    family = {x for tags in FAMILIES.get(c.data_point, ()) for x in tags}
    names = [t] + ([t.split("_", 1)[1]] if "_" in t else [])
    for name in names:
        if name in family:
            continue
        shown_on = [
            ln
            for ln in fl.printed(c.accession, name)
            if ln.report == int(rp) and re.search(gate, _norm_label(ln.plabel))
        ]
        if not shown_on:
            continue
        f = fl.fact(c.accession, name, c.period_end, _qtrs(c.data_point))
        if f is not None and _shown_matches(c.data_point, shown, f.value)[0]:
            return AutoCheck(
                c.data_point,
                c.fiscal_year,
                AUTO_MATCH,
                "claim",
                f.value,
                f"no {c.data_point} family fact; the claimed element {_fmt(f)}, printed on {c.r_page} as "
                f"{shown_on[0].plabel!r}, holds the shown value",
                f,
            )
    return None


def _printed_elsewhere(
    c: Cell, fl: Filing, shown: Decimal, got: list[FilingFact]
) -> AutoCheck | None:
    """Printed-line precedence: a family fact the filing does not print (a note mention, no fsn.line) never
    overrules a printed statement line holding the shown value under a tag outside the family (BMY 2017 amortization
    bmy:AmortizationofAcquiredIntangibleAssets 97 vs the note's 190; GE 2023 cash taxes). The checker cannot tell
    from the facts which of the two is the data point: a read. A cited tag that is itself a lower family tier is
    ranked by the family (accounts_receivable: the note split decides over the wider face line, X16)."""
    dp = c.data_point
    t = _cited_tag(c)
    if dp not in PRECEDENCE_DPS:
        return None
    if not t or any(fl.printed(c.accession, f.tag) for f in got):
        return None
    if any(t in tags for tags in FAMILIES.get(dp, ())):
        return None
    f = fl.fact(c.accession, t, c.period_end, _qtrs(dp))
    if (
        f is None
        or not fl.printed(c.accession, t)
        or not _shown_matches(dp, shown, f.value)[0]
    ):
        return None
    return AutoCheck(
        dp,
        c.fiscal_year,
        NEEDS_READ,
        "family",
        got[0].value,
        f"the family fact {_fmt(got[0])} is not printed; the printed line {t} holds the shown {shown}: read which "
        "one is the data point",
    )


def _one(facts: list[FilingFact]) -> FilingFact | None:
    """The tier's figure when its facts agree (one value), else None."""
    return facts[0] if facts and len({f.value for f in facts}) == 1 else None


def _opex_identity(c: Cell, fl: Filing, shown: Decimal) -> AutoCheck | None:
    """Registry step 2 for operating_expenses: total costs and expenses minus cost of revenue, from the filing's own
    facts (QCOM 2021, BMY 2018). None when the filing does not tag both or the result differs."""
    acc, pe = c.accession, c.period_end
    tot = fl.fact(acc, "CostsAndExpenses", pe, 4)
    if tot is None:
        return None
    _, cors = fl.tier(acc, "cost_of_revenue", pe)
    cor = _one(cors)
    if cors and cor is None:
        return None
    if cor is None and fl.fact(acc, "GrossProfit", pe, 4) is not None:
        return None  # a cost of revenue the family cannot see sits inside the total
    val = abs(tot.value) - (abs(cor.value) if cor else 0)
    if abs(shown) != val:
        return None
    return AutoCheck(
        c.data_point,
        c.fiscal_year,
        AUTO_MATCH,
        "identity",
        val,
        f"total costs and expenses - cost of revenue: {_fmt(tot)}"
        + (f" - {_fmt(cor)}" if cor else " (the filing tags no cost of revenue)"),
    )


# A printed label that puts income in parentheses (expense-positive presentation: "Other (income) and expense").
_EXPENSE_POSITIVE_LABEL = re.compile(r"\(income\)")


def _interest_effect(label: str, v: Decimal) -> Decimal | None:
    """The effect on pretax of a printed interest line in the nonoperating band, from its label; None for a line
    that combines interest with other items ("Interest and other income, net"): the band cannot be split there."""
    lab = _norm_label(label)
    if re.search(
        r"\b(other|investment|gains?|losses?)\b", lab
    ):  # "interest and dividend income" is interest (BLK)
        return None
    exp, inc = "expense" in lab, "income" in lab
    if exp and not inc:
        return -abs(v)
    if inc and not exp:
        return abs(v)
    return v  # "interest income (expense), net": a credit-signed net element


_NET_INTEREST_LABEL = re.compile(
    r"^(net interest|total interest|interest( expense| income)?( income| expense)? net)"
)


def _half_unit(f: FilingFact) -> Decimal:
    return Decimal(0) if f.dcml >= 32767 else Decimal(5).scaleb(-f.dcml - 1)


@dataclass(frozen=True)
class Band:
    value: Decimal
    evidence: str
    complete: bool  # False: a band line combines interest with other items, or an interest line has no fact
    tolerance: Decimal  # half a unit of each input's decimals, summed
    coarse: bool  # an input is a rounded mention (dcml -8 or coarser)
    # the band with unprinted interest income also taken out, when a printed "interest ..., net" line may or may not
    # already hold it (PM, LIN: inside the net line; AMGN: inside "Other income, net")
    alt: tuple[Decimal, Decimal, bool, str] | None = (
        None  # (value, tolerance, coarse, evidence)
    )
    combined: tuple[
        FilingFact, ...
    ] = ()  # band lines that combine interest with other items


def _band(fl: Filing, acc: str, pe: str) -> Band | None:
    """Definition 2026-11-21 (d): the printed income-statement lines between operating income and pretax, without
    the interest lines, as pretax - operating income - the interest lines' effect (no line weights needed). An
    interest block's printed net subtotal ("Interest, net", WMT) stands for the lines above it. Interest income the
    band does not print (a note fact: PANW, AMGN) sits inside an "other income" line and is taken out; one printed
    above operating income (UNH "Investment and other income" in revenues) is not in the band. None when the filing
    does not print operating income and pretax on one statement."""
    pt = _one(fl.tier(acc, "income_before_tax", pe)[1])
    oi = _one(fl.tier(acc, "operating_income", pe)[1])
    if pt is None or oi is None:
        return None
    pair = next(
        (
            (o, p)
            for o in fl.printed(acc, oi.tag, "IS")
            for p in fl.printed(acc, pt.tag, "IS")
            if o.report == p.report and 0 < o.line < p.line
        ),
        None,
    )
    if pair is None:
        return None
    o, p = pair
    band = sorted(
        (
            ln
            for ln in fl.lines
            if ln.accession == acc
            and ln.report == o.report
            and o.line < ln.line < p.line
            and re.search(
                r"interest|investment (and other )?income", _norm_label(ln.plabel)
            )
        ),
        key=lambda ln: ln.line,
    )
    nets = [
        ln
        for i, ln in enumerate(band)
        if i > 0 and _NET_INTEREST_LABEL.search(_norm_label(ln.plabel))
    ]
    if nets:
        band = [ln for ln in band if ln.line >= nets[0].line]
    val = pt.value - oi.value
    tol, coarse = (
        _half_unit(pt) + _half_unit(oi),
        min(pt.dcml, oi.dcml) <= ROUNDED_MENTION_DCML,
    )
    ev, complete, printed_income, net_line = (
        [f"{_fmt(pt)} - {_fmt(oi)}"],
        True,
        False,
        False,
    )
    combined: list[FilingFact] = []
    for ln in band:
        lab = _norm_label(ln.plabel)
        f = fl.fact(acc, ln.tag, pe, 4)
        eff = None if f is None else _interest_effect(ln.plabel, f.value)
        if f is None or eff is None:
            complete = False
            if f is not None:
                combined.append(f)
            ev.append(f"unsplit {ln.plabel!r}" + (f" {_fmt(f)}" if f else " (no fact)"))
            continue
        printed_income |= eff > 0 or "income" in lab
        net_line |= bool(re.search(r"\bnet\b", lab))
        val -= eff
        tol += _half_unit(f)
        coarse |= f.dcml <= ROUNDED_MENTION_DCML
        ev.append(f"{'+' if eff < 0 else '-'} {ln.plabel!r} {_fmt(f)}")
    out = Band(val, " ".join(ev), complete, tol, coarse, None, tuple(combined))
    if not printed_income:
        ii = _one(fl.tier(acc, "interest_income", pe)[1])
        if ii is not None and not fl.printed(acc, ii.tag, "IS"):
            v2, t2 = val - abs(ii.value), tol + _half_unit(ii)
            c2 = coarse or ii.dcml <= ROUNDED_MENTION_DCML
            e2 = out.evidence + f" - interest income inside the band {_fmt(ii)}"
            if net_line:
                out = Band(
                    val,
                    out.evidence,
                    complete,
                    tol,
                    coarse,
                    (v2, t2, c2, e2),
                    tuple(combined),
                )
            else:
                out = Band(v2, e2, complete, t2, c2, None, tuple(combined))
    return out


def _other_income(c: Cell, fl: Filing, shown: Decimal) -> AutoCheck:
    """other_income_expense_net, as printed or combined, by the band rule (definition 2026-11-21 d) instead of an
    element family (NonoperatingIncomeExpense is the band total with interest, OtherNonoperatingIncomeExpense often
    only the note's "Other" row: AMGN 2023, BLK 2018/19/23, RTX 2020). Matched by the band, or by the interest split
    (the combined nonoperating line minus its interest income). A cited custom line printed expense-positive and not
    negated ("Other (income) and expense", ibm:OtherIncomeAndExpense) must be shown flipped (IBM 2020-2025)."""
    dp, fy = c.key
    acc, pe = c.accession, c.period_end
    t = _cited_tag(c)
    cited = fl.fact(acc, t, pe, 4) if t else None
    if cited is not None and cited.value != 0 and shown == cited.value:
        lines = fl.printed(acc, t, "IS")
        if lines and all(
            _EXPENSE_POSITIVE_LABEL.search(ln.plabel.lower()) and not ln.negating
            for ln in lines
        ):
            return AutoCheck(
                dp,
                fy,
                AUTO_MISMATCH,
                "sign",
                -cited.value,
                f"sign: the printed line {t} ({lines[0].plabel!r}) is expense-positive and not negated; other "
                f"income is {-cited.value}, shown {shown}",
            )
    bd = _band(fl, acc, pe)
    # (value, tolerance, coarse, evidence) candidates
    cands: list[tuple[Decimal, Decimal, bool, str]] = []
    if bd is not None and bd.complete:
        cands.append((bd.value, bd.tolerance, bd.coarse, "band: " + bd.evidence))
        if bd.alt is not None:
            cands.append((bd.alt[0], bd.alt[1], bd.alt[2], "band: " + bd.alt[3]))
    comb = fl.fact(acc, "NonoperatingIncomeExpense", pe, 4)
    if comb is not None:
        for it in ("InterestIncomeOther", "InvestmentIncomeInterest"):
            if (i := fl.fact(acc, it, pe, 4)) is not None:
                cands.append(
                    (
                        comb.value - abs(i.value),
                        _half_unit(comb) + _half_unit(i),
                        min(comb.dcml, i.dcml) <= ROUNDED_MENTION_DCML,
                        f"interest split: {_fmt(comb)} - {_fmt(i)}",
                    )
                )
    if bd is not None and not bd.complete:
        # a printed band line combining interest with other items ("Investment and other income, net", V, QCOM):
        # the shown value is that printed line (the badge should say combined)
        for f in bd.combined:
            if f.value == shown:
                return AutoCheck(
                    dp,
                    fy,
                    AUTO_MATCH,
                    "label",
                    f.value,
                    f"printed combined band line: {_fmt(f)}",
                )
    if bd is None:
        # no printed operating income line (insurers, banks, conglomerates): the face's own other-income line,
        # never a note row
        onf = fl.fact(acc, "OtherNonoperatingIncomeExpense", pe, 4)
        if onf is not None and onf.value == shown and fl.printed(acc, onf.tag, "IS"):
            return AutoCheck(
                dp,
                fy,
                AUTO_MATCH,
                "family",
                onf.value,
                f"printed income-statement line: {_fmt(onf)}",
            )
    for v, _, _, why in cands:
        if v == shown:
            return AutoCheck(dp, fy, AUTO_MATCH, "identity", v, why)
    near = [x for x in cands if abs(x[0] - shown) <= x[1]]
    if any(not x[2] for x in near):
        v, tol, _, why = next(x for x in near if not x[2])
        return AutoCheck(
            dp,
            fy,
            AUTO_MATCH,
            "identity",
            v,
            f"{v} equals the shown {shown} within its inputs' rounding ({tol}): {why}",
        )
    if bd is not None and bd.complete and not near and not any(x[2] for x in cands):
        return AutoCheck(
            dp,
            fy,
            AUTO_MISMATCH,
            "identity",
            bd.value,
            f"the printed band without its interest lines gives "
            + " or ".join(str(x[0]) for x in cands)
            + f", shown {shown}: {bd.evidence}",
        )
    return AutoCheck(
        dp,
        fy,
        NEEDS_READ,
        "identity",
        bd.value if bd else None,
        f"the band at {pe} in {acc} does not settle it "
        f"({bd.evidence if bd else 'no printed operating income and pretax lines'}): read the printed nonoperating lines",
    )


def check_draw(
    sample: list[Cell],
    facts: list[FilingFact],
    lines: list[FilingLine],
    calc: Iterable[CalcArc] = (),
) -> list[AutoCheck]:
    fl = Filing(facts, lines, calc)
    return [check_cell(c, fl) for c in sample]


def corroborate(
    checks: list[AutoCheck], corroborated: dict[tuple[str, str], str]
) -> list[AutoCheck]:
    """A drawn NEEDS_READ cell an exact accounting identity corroborates (proof/identity_web.web_corroborated: the
    identity holds over the shown cells and the filing's own operands, and every other member is AUTO_MATCH) is
    AUTO_MATCH by method 'identity'. An AUTO_MISMATCH is never overturned."""
    return [
        AutoCheck(
            a.data_point,
            a.fiscal_year,
            AUTO_MATCH,
            "identity",
            None,
            corroborated[a.key],
        )
        if a.outcome == NEEDS_READ and a.key in corroborated
        else a
        for a in checks
    ]


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


# ---------------------------------------------------------------- three-source agreement (@3, 2026-11-22)
# Each shown cell is compared across three renderings of the cited filing: (1) the FSN filing fact the checker
# decided the cell by (AutoCheck.fact; per part for a summed cell), (2) the SEC companyfacts API value of that tag at
# the same period end and accession, (3) the number printed on the cited R page's line of that tag. Never the
# resolver's output or the value tables: the tag is the checker's own fact's tag (a part's tag for a summed cell).
AGREE3 = "AGREE3"  # all three sources present and equal to the shown value: auto-proven, no draw needed
AGREE2 = "AGREE2"  # one source missing (custom tag not in companyfacts, no printed line); the two present agree
DISAGREE = "DISAGREE"  # a present source differs from the shown value: may be a wrong shown value
SINGLE = "SINGLE"  # fewer than two sources (a read, a dimensioned part, an identity): never proven by agreement
AGREEMENT = (AGREE3, AGREE2, DISAGREE, SINGLE)
SOURCES = ("fsn", "companyfacts", "rpage")
CF_TOLERANCE_DAYS = 7  # the checker's own period window (52/53-week years)


@dataclass(frozen=True)
class CfFact:
    tag: str
    accession: str
    start: str  # "" for an instant
    end: str
    value: Decimal
    uom: str


class CompanyFacts:
    """One companyfacts JSON (data.sec.gov/api/xbrl/companyfacts), indexed by (tag local name, accession)."""

    def __init__(self, doc: dict):
        self._by: dict[tuple[str, str], list[CfFact]] = {}
        for tax in (doc.get("facts") or {}).values():
            for tag, body in tax.items():
                for uom, rows in (body.get("units") or {}).items():
                    for r in rows:
                        if r.get("val") is None or not r.get("accn"):
                            continue
                        f = CfFact(
                            tag,
                            r["accn"],
                            r.get("start") or "",
                            r["end"],
                            Decimal(str(r["val"])),
                            uom,
                        )
                        self._by.setdefault((tag, f.accession), []).append(f)

    def values(
        self, tag: str, accession: str, period_end: str, qtrs: int
    ) -> list[CfFact]:
        """The undimensioned USD (or share, per-share) facts of a tag the accession reported at the period end: an
        instant (no start) for qtrs 0, a 350-380 day duration for qtrs 4."""
        out = []
        for f in self._by.get((tag, accession), ()):
            if not usd_unit(f.uom) or _days(f.end, period_end) > CF_TOLERANCE_DAYS:
                continue
            if qtrs == 0 and f.start:
                continue
            if qtrs == 4 and not (f.start and 350 <= _days(f.end, f.start) <= 380):
                continue
            out.append(f)
        return out


class SourceStore:
    """Companyfacts JSON and R pages under one cache directory (cf/CIK##########.json, r/<accession>/R<n>.htm).
    fetch=True fetches a missing file through the machine-wide SEC budget (common/sec_rate.py, sec.gov only);
    fetch=False reads the cache only and a missing file is a missing source."""

    def __init__(self, cache: Path, fetch: bool = False):
        self.cache, self.fetch = Path(cache), fetch
        self._cf: dict[str, CompanyFacts | None] = {}
        self._pages: dict[tuple[str, str], object] = {}

    def _file(self, url: str, out: Path) -> Path | None:
        if not (out.exists() and out.stat().st_size > 0) and self.fetch:
            from scrooner_pipeline.common import sec_rate

            try:
                sec_rate.fetch_to(url, out)
            except Exception:  # noqa: BLE001 - an unreachable page is a missing source, never a match
                return None
        return out if out.exists() and out.stat().st_size > 0 else None

    def companyfacts(self, cik: str) -> CompanyFacts | None:
        cik = str(cik).lstrip("0").zfill(10)
        if cik not in self._cf:
            if len(self._cf) > 2:  # one company at a time; the JSON is large
                self._cf.clear()
            p = self._file(
                f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                self.cache / "cf" / f"CIK{cik}.json",
            )
            try:
                self._cf[cik] = CompanyFacts(json.loads(p.read_text())) if p else None
            except ValueError:
                self._cf[cik] = None
        return self._cf[cik]

    def rpage(self, cik: str, accession: str, r_page: str):
        """The parsed R page (verification/filing_kit.parse_rpage), None when absent or unparseable."""
        from scrooner_pipeline.verification.filing_kit import parse_rpage

        r = re.sub(r"\.htm$", "", (r_page or "").strip())
        if not re.fullmatch(r"R\d+", r) or not accession:
            return None
        k = (accession, r)
        if k not in self._pages:
            if len(self._pages) > 512:
                self._pages.clear()
            p = self._file(
                f"https://www.sec.gov/Archives/edgar/data/{str(cik).lstrip('0')}/"
                f"{accession.replace('-', '')}/{r}.htm",
                self.cache / "r" / accession / f"{r}.htm",
            )
            try:
                self._pages[k] = (
                    parse_rpage(p.read_text(errors="replace")) if p else None
                )
            except (ValueError, KeyError, IndexError):
                self._pages[k] = None
        return self._pages[k]


def printed_values(
    page, tag: str, period_end: str, qtrs: int, uom: str
) -> list[tuple[Decimal, Decimal]]:
    """The numbers printed on the page's line(s) of `tag` in the column ending at the period end (+-7 days; a
    12-month column for a flow when the page has several durations), scaled by the page's printed unit: money by
    the money unit, shares by the share unit, per-share figures unscaled. Returns (value, printed unit) per line:
    the unit is the scale times the printed decimals (1,234.5 in millions: 100,000). Signs are printed (a negated
    label prints the fact's opposite), so callers compare magnitudes."""
    if page is None or not tag:
        return []
    cols = [
        i
        for i, d in enumerate(page.columns)
        if abs((d - date.fromisoformat(period_end)).days) <= 7
    ]
    if qtrs == 4 and len(cols) > 1:
        twelve = [i for i in cols if page.months[i] == 12]
        cols = twelve or cols
    if len(cols) != 1:
        return []  # no column, or an ambiguous one (several durations or columns): a missing source
    i = cols[0]
    if "/" in uom:
        mult = 1
    elif "share" in uom.lower():
        mult = page.share_multiplier
    else:
        mult = page.multiplier
    out = []
    for row in page.rows:
        if row.tag != tag or i >= len(row.values) or row.values[i] is None:
            continue
        dec = row.decimals[i] if i < len(row.decimals) else None
        out.append((row.values[i] * mult, Decimal(mult).scaleb(-(dec or 0))))
    return out


@dataclass(frozen=True)
class Leg:
    """One filed figure behind a shown cell: the whole cell (single element) or one part of a summed cell."""

    tag: str
    dims: str
    accession: str
    r_page: str
    expected: Decimal  # what the sources must equal: the shown value (single) or the part as filed
    fact: FilingFact | None  # the FSN fact (source 1); None = FSN missing
    single: bool  # True: compared by the polarity rule against the shown value; False: a part as filed


@dataclass(frozen=True)
class SourceCheck:
    data_point: str
    fiscal_year: str
    outcome: str  # AGREE3 | AGREE2 | DISAGREE | SINGLE
    legs: tuple[dict, ...]
    detail: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.data_point, self.fiscal_year)

    def as_json(self) -> dict:
        return {
            "outcome": self.outcome,
            "legs": list(self.legs),
            "detail": self.detail,
        }


def _agrees(dp: str, leg: Leg, v: Decimal, dcml: int) -> bool:
    if leg.single:
        if _shown_matches(dp, leg.expected, v)[0]:
            return True
        probe = FilingFact("", "", "", 0, "", v, dcml)
        return (
            ROUNDED_MENTION_DCML < dcml < 32767
            and _rounds_to(leg.expected, probe)
            and (
                is_fixed_positive(dp)
                or dp in MAGNITUDE
                or (leg.expected < 0) == (v < 0)
            )
        )
    return v == leg.expected


def _printed_agrees(leg: Leg, printed: Decimal, unit: Decimal) -> bool:
    """Magnitudes (the printed sign follows the label) within half the printed unit: a page in millions prints
    293 for 293,223,000 only to the million it shows, so the unit bounds the difference, never more."""
    return abs(abs(printed) - abs(leg.expected)) * 2 <= unit


def _legs(c: Cell, a: AutoCheck, fl: Filing) -> list[Leg]:
    dp = c.data_point
    shown = c.value if c.value is not None else Decimal(0)
    if a.fact is not None and len(c.parts) <= 1:
        if a.fact.dcml <= ROUNDED_MENTION_DCML:
            return []  # a rounded mention proves nothing either way
        return [
            Leg(a.fact.tag, a.fact.dims, c.accession, c.r_page, shown, a.fact, True)
        ]
    if len(c.parts) > 1 and a.outcome == AUTO_MATCH:
        # a summed cell the checker matched (the parts sum to the shown value): each part across the sources
        return [
            Leg(
                p.tag.split(":")[-1],
                p.dims,
                p.accession,
                p.r_page,
                p.value,
                fl.fact(
                    p.accession, p.tag.split(":")[-1], c.period_end, _qtrs(dp), p.dims
                ),
                False,
            )
            for p in c.parts
        ]
    return []


def three_source_cell(
    c: Cell, a: AutoCheck, fl: Filing, store: SourceStore, cik: str
) -> SourceCheck:
    """Three-source agreement of one shown cell. A cell the checker found AUTO_MISMATCH is DISAGREE (its FSN source
    differs from the shown value) whatever the other two say."""
    dp, fy = c.key
    q = _qtrs(dp)
    legs = _legs(c, a, fl)
    out, n_present, bad = [], [], []
    for leg in legs:
        got: dict[str, Decimal | None] = dict.fromkeys(SOURCES)
        ok: dict[str, bool | None] = dict.fromkeys(SOURCES)
        # the unit decides the printed scale: companyfacts' own unit first (FSN tags EPS in 'USD'), per-share by the
        # data point, else the FSN fact's
        uom = "USD/shares" if dp in PER_SHARE else (leg.fact.uom if leg.fact else "")
        dcml = leg.fact.dcml if leg.fact else 32767
        if leg.fact is not None:
            got["fsn"] = leg.fact.value
            ok["fsn"] = _agrees(dp, leg, leg.fact.value, dcml)
        if not leg.dims:  # companyfacts and the statement line carry no dimensions
            cf = store.companyfacts(cik)
            vals = cf.values(leg.tag, leg.accession, c.period_end, q) if cf else []
            if vals:
                hit = [f for f in vals if _agrees(dp, leg, f.value, dcml)]
                got["companyfacts"] = (hit or vals)[0].value
                ok["companyfacts"] = bool(hit)
                uom = vals[0].uom
            page = store.rpage(cik, leg.accession, leg.r_page)
            pv = printed_values(page, leg.tag, c.period_end, q, uom or "USD")
            if pv:
                printed = [v for v, u in pv if _printed_agrees(leg, v, u)]
                got["rpage"] = (printed or [v for v, _ in pv])[0]
                ok["rpage"] = bool(printed)
        present = [s for s in SOURCES if ok[s] is not None]
        n_present.append(len(present))
        bad += [
            f"{leg.tag} {s} {got[s]} vs {leg.expected}" for s in present if not ok[s]
        ]
        out.append(
            {
                "tag": leg.tag,
                "dims": leg.dims,
                "accession": leg.accession,
                "r_page": leg.r_page,
                "expected": str(leg.expected),
                **{s: None if got[s] is None else str(got[s]) for s in SOURCES},
                "agree": ok,
            }
        )
    if a.outcome == AUTO_MISMATCH:
        outcome = DISAGREE
        bad = bad or [f"fsn: {a.detail}"]
    elif bad:
        outcome = DISAGREE
    elif not legs or min(n_present) < 2:
        outcome = SINGLE
    elif min(n_present) == 3:
        outcome = AGREE3
    else:
        outcome = AGREE2
    detail = (
        "; ".join(bad)
        if bad
        else (
            "no filed figure the three sources can share"
            if not legs
            else f"{len(legs)} leg(s), sources present per leg {n_present}"
        )
    )
    return SourceCheck(dp, fy, outcome, tuple(out), detail)


def three_source(
    sample: list[Cell],
    checks: list[AutoCheck],
    facts: list[FilingFact],
    lines: list[FilingLine],
    store: SourceStore,
    cik: str,
) -> list[SourceCheck]:
    fl = Filing(facts, lines)
    by = {a.key: a for a in checks}
    return [
        three_source_cell(c, by[c.key], fl, store, cik) for c in sample if c.key in by
    ]


def agreement_counts(checks: Iterable[SourceCheck]) -> dict[str, int]:
    out = dict.fromkeys(AGREEMENT, 0)
    for s in checks:
        out[s.outcome] += 1
    return out
