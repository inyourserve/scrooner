"""I8 composition.

total debt (display layer = `total_debt_resolved` else `total_debt`):

  debt_below_component   the stored total is smaller than a single authoritative
                         debt component recorded for the same period. A total
                         can never be below one of its parts. Covers ABBV (0
                         while debt tags exist), WFC (resolved = short-term only,
                         25.2B vs 207.3B) and every "resolved equals one tag"
                         failure. Components are read from the registry
                         (analytics.concept_mapping rows of total_debt and
                         total_debt_split, minus 'rejected'), not assumed.
  debt_zero_with_components
                         subtype of the above, reported under its own rule name
                         when the stored total is 0.
  debt_double_count      the sources of the stored total include two tags where
                         one by definition contains the other (OVERLAPPING_TAGS,
                         from the us-gaap element definitions: DATA-INFERRED).

per-share by subtraction:

  per_share_derived      a per-share or share-count value whose source is a
                         DERIVED fact (Q4 = FY - 9M). Never valid: EPS and
                         weighted shares are not additive (KLAC Q4 EPS -22.61,
                         filed 1.04).
"""

from __future__ import annotations

from decimal import Decimal

from .model import NON_ADDITIVE_DERIVED, REVIEW, WRONG_VALUE, CompanyData, Finding, finding

TOTAL_TOLERANCE = Decimal("0.98")  # stored may be 2% under a component (rounding / FX)

# (container tag, contained tag): the first by its taxonomy definition includes
# the second, so summing both counts the second twice.
OVERLAPPING_TAGS = (
    ("LongTermDebt", "LongTermDebtCurrent"),
    ("LongTermDebt", "LongTermDebtNoncurrent"),
    ("DebtCurrent", "ShortTermBorrowings"),
    ("DebtCurrent", "LongTermDebtCurrent"),
    ("DebtCurrent", "SecuredDebtCurrent"),
)
# Partial overlap (LongTermDebt includes current maturities that DebtCurrent
# also holds): a review, not a certain double count.
PARTIAL_OVERLAPS = (("LongTermDebt", "DebtCurrent"),)


def _debt_cells(data: CompanyData):
    return [c for c in data.display_cells() if c.base == "total_debt"]


def _debt_below_component(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    by_period: dict[int, list] = {}
    for f in data.debt_facts:
        by_period.setdefault(f.period_id, []).append(f)
    for cell in _debt_cells(data):
        facts = by_period.get(cell.period_id, [])
        positives = [f for f in facts if f.value > 0]
        if not positives:
            continue
        biggest = max(positives, key=lambda f: f.value)
        if cell.value >= biggest.value * TOTAL_TOLERANCE:
            continue
        rule = "debt_zero_with_components" if cell.value == 0 else "debt_below_component"
        out.append(
            finding(
                data, "I8", WRONG_VALUE, rule, cell, other=biggest.value,
                largest_component_tag=biggest.tag, largest_component_id=biggest.id,
                components=[{"id": f.id, "tag": f.tag, "value": str(f.value)} for f in positives],
                source_ids=sorted(set(cell.source_ids) | {biggest.id}),
            )
        )
    return out


def _debt_double_count(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    for cell in _debt_cells(data):
        tags = {s.tag for s in data.source_facts(cell)}
        for container, contained in OVERLAPPING_TAGS:
            if container in tags and contained in tags:
                out.append(
                    finding(data, "I8", WRONG_VALUE, "debt_double_count", cell,
                            container=container, contained=contained, tags=sorted(tags))
                )
        for a, b in PARTIAL_OVERLAPS:
            if a in tags and b in tags:
                out.append(
                    finding(data, "I8", REVIEW, "debt_partial_overlap", cell,
                            tags=sorted(tags), note=f"{a} includes current maturities also held in {b}")
                )
    return out


def _per_share_derived(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    for cell in data.display_cells():  # displayed layer only; base+resolved would double-count
        if cell.base not in NON_ADDITIVE_DERIVED:
            continue
        derived = [s for s in data.source_facts(cell) if s.derived]
        if derived:
            out.append(
                finding(data, "I8", WRONG_VALUE, "per_share_derived_by_subtraction", cell,
                        derived_fact_ids=[s.id for s in derived], tags=sorted({s.tag for s in derived}),
                        policy="never derive EPS, weighted shares or ratios by subtraction",
                        value_checked=False,
                        note="policy violation; the value was not compared with a filed Q4 figure")
            )
    return out


def check(data: CompanyData) -> list[Finding]:
    return _debt_below_component(data) + _debt_double_count(data) + _per_share_derived(data)
