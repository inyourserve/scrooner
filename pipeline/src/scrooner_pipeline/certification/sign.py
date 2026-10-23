"""I3 sign policy.

Never flips a sign: a violation is reported, the value stays as stored.

Concept list. The DQC_0015 element list (6,396 elements that must not be
negative) is not stored in this repo, so the check works at the CANONICAL level
with the concepts that cannot be negative by definition (a quantity of things or
an amount owed/held/earned from customers) and the tags behind them are not
enumerated. `EXTRA_NONNEGATIVE_TAGS` is the hook for the DQC list: any source
fact whose tag is in it and whose value is negative is reported the same way.

Concepts deliberately NOT here because a negative is legitimate: net income,
operating income, gross profit, income before tax, income tax expense (benefit),
cash flows (cfo, investing, financing), EPS, equity, comprehensive income,
other income/expense, interest_income (can be net), working-capital changes.

Severity: a DERIVED source (Q4 = FY - 9M, the pipeline's own arithmetic) that
produces a sign-impossible value is `wrong_value` (the filed inputs are
positive, so the arithmetic or a filing's sign broke); a FILED negative is
`review` (DQC_0015: a tagging-error candidate to quarantine, not to flip) - real
cases exist (an insurer with negative revenue after investment losses).
"""

from __future__ import annotations

from .model import REVIEW, WRONG_VALUE, CompanyData, Finding, finding

NONNEGATIVE_CONCEPTS = frozenset(
    {
        "revenue",
        "cost_of_revenue",
        "operating_expenses",
        "sga_expense",
        "research_and_development",
        "interest_expense",
        "sbc",
        "depreciation_and_amortization",
        "amortization_of_intangibles",
        "total_assets",
        "total_liabilities",
        "current_assets",
        "current_liabilities",
        "cash_and_equivalents",
        "total_debt",
        "total_debt_split",
        "inventory",
        "ppe_net",
        "goodwill",
        "accounts_receivable",
        "accounts_payable",
        "shares_outstanding",
        "public_float",
        "employee_count",
        "dividends_per_share",
        "dividends_paid",
        "share_buybacks",
        "capex",
    }
)

# Hook for the DQC_0015 element list (tag local names). Empty until the list is
# loaded from the study material; see module docstring.
EXTRA_NONNEGATIVE_TAGS: frozenset[str] = frozenset()


def check(data: CompanyData) -> list[Finding]:
    findings: list[Finding] = []
    for cell in data.cells:
        sources = data.source_facts(cell)
        derived = [s for s in sources if s.derived]
        # A CALCULATED cell (two or more input facts, e.g. opex = gross profit - operating
        # income) cannot legitimately come out negative on a concept that is an amount of
        # expense or an asset: the negative is another line (LMT: other income +62M shown
        # as opex -62M). A single filed fact can (an insurer's revenue after losses).
        calculated = len({s.id for s in sources if not s.derived}) >= 2
        if cell.base in NONNEGATIVE_CONCEPTS and cell.value < 0:
            findings.append(
                finding(
                    data,
                    "I3",
                    WRONG_VALUE if derived or calculated else REVIEW,
                    "negative_on_nonnegative_concept",
                    cell,
                    other=None,
                    derived_source=bool(derived),
                    calculated_from_inputs=calculated,
                    tags=sorted({s.tag for s in sources}),
                    forms=sorted({s.form or "?" for s in sources}),
                    policy="quarantine, never flip",
                )
            )
        if EXTRA_NONNEGATIVE_TAGS:
            for s in sources:
                if (
                    s.tag in EXTRA_NONNEGATIVE_TAGS
                    and s.value < 0
                    and cell.base not in NONNEGATIVE_CONCEPTS
                ):
                    findings.append(
                        finding(
                            data,
                            "I3",
                            REVIEW,
                            "negative_on_dqc0015_tag",
                            cell,
                            tag=s.tag,
                            source_ids=[s.id],
                        )
                    )
    return findings
