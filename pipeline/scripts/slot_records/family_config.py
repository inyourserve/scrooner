"""Family definitions for slot-record detection beyond debt (stdlib).

Each family: which FSDS statements its face lines live on, which tags belong,
and how members classify. Classes are descriptive, never a mapping decision:
'is_subline' marks the Kura trap (an income-statement D&A sub-line must never
be mapped as the cash-flow D&A total); 'financing_amort' marks debt-cost
amortization that most D&A definitions exclude; 'net_capex' marks a
purchases-net-of-proceeds line whose perimeter differs from gross capex.
"""
import re

FAMILIES = {
    "d_and_a": {
        "stmts": {"CF", "IS"},
        "match": re.compile(r"Depreciation|Amortization|Depletion|Accretion"),
        "exclude": re.compile(
            r"AccumulatedDepreciation|RightOfUseAsset|"
            r"AmortizedCost|AvailableForSale"  # investment-schedule lines
        ),
        "classes": [
            (re.compile(r"AmortizationOfDebtDiscount|DebtIssuanceCost|AmortizationOfFinancingCosts"), "financing_amort"),
            (re.compile(r"AccretionAmortizationOfDiscountsAndPremiums"), "investment_amort"),
            (re.compile(r"DepreciationDepletionAndAmortization|DepreciationAmortizationAndAccretionNet|DepreciationAndAmortization$|^Depreciation$|DepreciationNonproduction|AmortizationOfIntangibleAssets|CapitalizedComputerSoftwareAmortization"), "asset_da"),
            (re.compile(r"."), "other_amort"),
        ],
    },
    "capex": {
        "stmts": {"CF"},
        "match": re.compile(
            r"PaymentsToAcquireProductiveAssets|PaymentsToAcquirePropertyPlantAndEquipment|"
            r"PaymentsToAcquireOtherPropertyPlantAndEquipment|PaymentsForCapitalImprovements|"
            r"PaymentsToAcquireMachineryAndEquipment|PaymentsForProceedsFromProductiveAssets|"
            r"PaymentsToDevelopSoftware|PaymentsForSoftware|PaymentsToAcquireSoftware|"
            r"PaymentsToAcquireIntangibleAssets"
        ),
        "exclude": re.compile(r"Businesses|Investments"),
        "classes": [
            (re.compile(r"PaymentsForProceedsFrom"), "net_capex"),
            (re.compile(r"Software"), "software_capex"),
            (re.compile(r"IntangibleAssets"), "intangible_capex"),
            (re.compile(r"."), "ppe_capex"),
        ],
    },
}


def classify(family: str, tag: str, stmt: str) -> str:
    if family == "d_and_a" and stmt == "IS":
        return "is_subline"
    for rx, cls in FAMILIES[family]["classes"]:
        if rx.search(tag):
            return cls
    return "other"
