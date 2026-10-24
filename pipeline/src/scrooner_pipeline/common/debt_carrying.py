"""Total debt as TWO slots from the balance-sheet carrying lines (pure; no settings, no database).

Decision card DC-TOTAL-DEBT-LEASE-PERIMETER-2026-10-24 (Standardization Lead, adopted by the coordinator):

    total debt = borrowings (carrying) + finance (capital) lease liabilities, current + noncurrent.
    Operating leases never. Two slots, each with the lines it came from (``DebtSlots``), so the
    accountant's answer to AC-1 (include or exclude finance leases) needs no rebuild.

The perimeter is a NAMED PARAMETER (``perimeter``), not a policy guess:
* ``lease_inclusive`` (default, the card's proposed AC-1 answer): borrowings + finance leases. Where the
  finance leases cannot be established the borrowings are returned with the composition label
  ``finance_leases_not_determined`` (card 2: "Total debt (finance leases not determined)", interim only,
  never enters a cross-company screen); they are never added blind;
* ``borrowings_only``: borrowings alone; a lease-inclusive-only filer whose borrowings cannot be
  separated is HELD.

Never sum a lease-inclusive line with a debt-only line (the TSLA 2017 error: debt-only ``DebtCurrent`` +
lease-inclusive noncurrent). The "DebtCurrent at or above the parts is accepted" path is gone.

How the slots are built from STORED numeric facts (the ASC 842 location lists are text facts and are not
stored, so the location is proven by the filing's own arithmetic, else held):
* leases L = ``FinanceLeaseLiability``, else current + noncurrent (FinanceLease... or the pre-842
  CapitalLeaseObligations...); exactly one half filed = incomplete, unverified;
* noncurrent borrowings: ``LongTermDebtNoncurrent`` (tag: debt only), or ``ConvertibleDebtNoncurrent``,
  or the lease-inclusive line ``LongTermDebtAndCapitalLeaseObligations`` less the noncurrent lease fact
  (MU: 14,017 - 2,484 = 11,533 = ``LongTermDebt``);
* current borrowings: a filed ``DebtCurrent`` is the whole current side (it includes current
  maturities and, by its definition, current capital leases): with a current lease fact the borrowings
  part is DebtCurrent less it (MU 560 - 560 = 0); a filed ``ShortTermDebtRefinancedAmount`` is removed
  first (CVX 19,840 - 9,000 = 10,840, NA-6 rule 3.4). Otherwise ``LongTermDebtCurrent`` plus short-term
  borrowings. A DebtCurrent contradicted by the parts filed beside it is HELD; parts larger than it are not
  inside it (LLY 2014-03-31: ``ShortTermBorrowings`` 1,000 beside DebtCurrent 9.1 is ignored). A DebtCurrent
  with lease facts filed but no current lease fact cannot be split: HELD ``lease_location_unknown``;
* a lease-inclusive-only filer with no lease facts (DPZ, TSLA) has only the lease-inclusive face total.
  It is used (lease-inclusive perimeter only) when no debt-only line or related-party line sits beside
  it; TSLA is HELD (``related_party_unresolved``): its debt-only DebtCurrent exceeds the lease-inclusive
  current line, or a related-party notes line is filed, so face lines would be dropped or double counted;
* related-party notes are never added by tag; they count only inside a filer line.
Known residual (not detectable from stored tags): a related-party convertible noncurrent line that is not
among the stored facts (TSLA 2018-09-30, 2.6M, 0.02%).
Authoritative facts only: the caller passes them.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from itertools import combinations

PLAIN_NONCURRENT = "LongTermDebtNoncurrent"
PLAIN_CURRENT = "LongTermDebtCurrent"
CONVERTIBLE_NONCURRENT = "ConvertibleDebtNoncurrent"
CONVERTIBLE_CURRENT = "ConvertibleDebtCurrent"
LEASE_INCL_NONCURRENT = "LongTermDebtAndCapitalLeaseObligations"
LEASE_INCL_CURRENT = "LongTermDebtAndCapitalLeaseObligationsCurrent"
LEASE_NONCURRENT = (
    "FinanceLeaseLiabilityNoncurrent",
    "CapitalLeaseObligationsNoncurrent",
)
LEASE_CURRENT = ("FinanceLeaseLiabilityCurrent", "CapitalLeaseObligationsCurrent")
LEASE_TOTAL = "FinanceLeaseLiability"
REFINANCED = "ShortTermDebtRefinancedAmount"  # a duration fact; the caller keys it by the instant's end date
RELATED_PARTY = "NotesPayableRelatedPartiesCurrentAndNoncurrent"
SHORT_TERM = ("ShortTermBorrowings", "CommercialPaper")
CURRENT_PART_TAGS = (
    "ShortTermBorrowings",
    "CommercialPaper",
    "OtherShortTermBorrowings",
    "ShortTermBankLoansAndNotesPayable",
    "LinesOfCreditCurrent",
    "NotesPayableCurrent",
    "ConvertibleNotesPayableCurrent",
    PLAIN_CURRENT,
    LEASE_INCL_CURRENT,
)
CARRYING_TAGS = tuple(
    dict.fromkeys(
        [
            PLAIN_NONCURRENT,
            PLAIN_CURRENT,
            CONVERTIBLE_NONCURRENT,
            CONVERTIBLE_CURRENT,
            LEASE_INCL_NONCURRENT,
            LEASE_INCL_CURRENT,
            LEASE_TOTAL,
            REFINANCED,
            RELATED_PARTY,
            "DebtCurrent",
            "LongTermDebt",
            "DebtLongtermAndShorttermCombinedAmount",
        ]
        + list(SHORT_TERM)
        + list(CURRENT_PART_TAGS)
        + list(LEASE_NONCURRENT)
        + list(LEASE_CURRENT)
    )
)
EXPLAIN_TOLERANCE = Decimal("0.02")
AGREEMENT_TOLERANCE = Decimal("0.10")
PERIMETERS = ("lease_inclusive", "borrowings_only")
DEFAULT_PERIMETER = "lease_inclusive"

COMPOSITION_BORROWINGS_PLUS_LEASES = "borrowings_plus_finance_leases"
COMPOSITION_LEASES_NOT_DETERMINED = "finance_leases_not_determined"
COMPOSITION_LEASE_INCLUSIVE_LINES = "lease_inclusive_face_lines"
COMPOSITION_BORROWINGS_ONLY = "borrowings_only"


@dataclass(frozen=True)
class Hold:
    # current_block_unexplained | lease_location_unknown | borrowings_not_separable
    # | related_party_unresolved | negative_component
    reason: str


@dataclass(frozen=True)
class DebtSlots:
    """The perimeter record of one company-instant (the two slots and where they came from)."""

    borrowings: (
        Decimal | None
    )  # None: lease-inclusive face lines only, borrowings not separable
    leases: Decimal | None  # None: unverified (see lease_reason)
    lease_inclusive_total: Decimal | None  # set only when borrowings is None
    tags: tuple[str, ...]
    proofs: tuple[str, ...]
    path: str
    lease_reason: str | None = (
        None  # lease_facts_absent | lease_facts_incomplete when leases is None
    )


@dataclass(frozen=True)
class Carrying:
    value: Decimal
    tags: tuple[str, ...]
    path: str
    perimeter: str  # the perimeter requested
    composition: str  # what value is: see COMPOSITION_*
    slots: DebtSlots


def _first(vals: Mapping[str, Decimal], tags: tuple[str, ...]) -> str | None:
    return next((t for t in tags if t in vals), None)


def _lease_slot(
    vals: Mapping[str, Decimal],
) -> tuple[Decimal | None, Decimal | None, Decimal | None, str | None, list[str]]:
    """(L total, L current, L noncurrent, reason when unverified, tags)."""
    ct, nt = _first(vals, LEASE_CURRENT), _first(vals, LEASE_NONCURRENT)
    lc = vals[ct] if ct else None
    ln = vals[nt] if nt else None
    tags = [t for t in (ct, nt) if t]
    if LEASE_TOTAL in vals:
        return vals[LEASE_TOTAL], lc, ln, None, [LEASE_TOTAL, *tags]
    if lc is not None and ln is not None:
        return lc + ln, lc, ln, None, tags
    if lc is None and ln is None:
        return None, None, None, "lease_facts_absent", []
    return None, lc, ln, "lease_facts_incomplete", tags


def _subset_matches(parts: list[Decimal], target: Decimal) -> bool:
    tol = target * EXPLAIN_TOLERANCE
    return any(
        abs(sum(c) - target) <= tol
        for n in range(1, len(parts) + 1)
        for c in combinations(parts, n)
    )


CORROBORATION_TOLERANCE = Decimal("0.005")


def _corroborated(
    vals: Mapping[str, Decimal], bn: Decimal, dc: Decimal, parts_short: Decimal
) -> bool:
    """A DebtCurrent that exceeds the listed parts (unlisted components, LLY: commercial paper plus current
    maturities with no current-maturities tag) is accepted only when the filing's own arithmetic confirms it:
    the company-stated total equals noncurrent + DebtCurrent, or ``LongTermDebt`` (which includes current
    maturities) equals noncurrent + DebtCurrent less the short-term parts."""
    all_in = vals.get("DebtLongtermAndShorttermCombinedAmount")
    if all_in and abs(all_in - (bn + dc)) <= CORROBORATION_TOLERANCE * all_in:
        return True
    lt = vals.get("LongTermDebt")
    return bool(
        lt and abs(lt - (bn + dc - parts_short)) <= CORROBORATION_TOLERANCE * lt
    )


def _current_borrowings(
    vals: Mapping[str, Decimal], lc: Decimal | None, any_lease_fact: bool, bn: Decimal
) -> tuple[Decimal | None, list[str], str, str | None]:
    """(current borrowings, tags, proof, hold reason)."""
    if "DebtCurrent" in vals:
        dc = vals["DebtCurrent"]
        tags = ["DebtCurrent"]
        proof = "debt_current_whole_current_side"
        if REFINANCED in vals and vals[REFINANCED] > 0:
            dc -= vals[REFINANCED]  # the pre-reclassification subtotal (CVX 2016)
            tags.append(REFINANCED)
            proof += "+less_refinanced"
        if dc < 0:
            return None, tags, proof, "negative_component"
        if dc == 0:
            return Decimal(0), tags, proof + "+zero", None
        tol = dc * EXPLAIN_TOLERANCE
        parts = [
            vals[t] for t in CURRENT_PART_TAGS if t in vals and 0 < vals[t] <= dc + tol
        ]
        if parts and not _subset_matches(parts, dc):
            # DebtCurrent also holds current capital leases by definition: a subset of the parts plus
            # the current lease fact may reproduce it; otherwise the parts contradict it
            short = sum(
                (
                    vals[t]
                    for t in CURRENT_PART_TAGS
                    if t in vals and t != PLAIN_CURRENT and 0 < vals[t] <= dc + tol
                ),
                Decimal(0),
            )
            if lc is None or not _subset_matches(parts, dc - lc):
                if not (dc > sum(parts) - tol and _corroborated(vals, bn, dc, short)):
                    return None, tags, proof, "current_block_unexplained"
                proof += "+corroborated_by_stated_total"
        if lc is not None:
            if lc > dc + tol:
                return None, tags, proof, "current_block_unexplained"
            return (
                max(dc - lc, Decimal(0)),
                tags,
                proof + "+less_current_lease_fact",
                None,
            )
        if any_lease_fact:
            return (
                None,
                tags,
                proof,
                "lease_location_unknown",
            )  # leases filed, cannot split the current side
        return dc, tags, proof + "+current_lease_unverified", None
    if PLAIN_CURRENT in vals:
        c = vals[PLAIN_CURRENT]
        tags = [PLAIN_CURRENT]
        s = _first(vals, SHORT_TERM)
        if s is not None and vals[s] != c:
            tags.append(s)
            return c + vals[s], tags, "current_maturities_plus_short_term", None
        return c, tags, "current_maturities", None
    if CONVERTIBLE_CURRENT in vals:
        return (
            vals[CONVERTIBLE_CURRENT],
            [CONVERTIBLE_CURRENT],
            "convertible_current",
            None,
        )
    return None, [], "", None


def _lease_inclusive_only(vals: Mapping[str, Decimal]) -> DebtSlots | Hold | None:
    """Lease-inclusive face lines and no lease facts to separate them (DPZ, TSLA)."""
    if LEASE_INCL_CURRENT not in vals:
        return None
    n, c = vals[LEASE_INCL_NONCURRENT], vals[LEASE_INCL_CURRENT]
    dc = vals.get("DebtCurrent")
    if RELATED_PARTY in vals or (dc is not None and dc > c * (1 + EXPLAIN_TOLERANCE)):
        return Hold("related_party_unresolved")
    return DebtSlots(
        borrowings=None,
        leases=None,
        lease_inclusive_total=n + c,
        tags=(LEASE_INCL_NONCURRENT, LEASE_INCL_CURRENT),
        proofs=("lease_inclusive_face_lines_same_perimeter",),
        path="carrying_lease_inclusive_lines",
        lease_reason="lease_facts_absent",
    )


def debt_slots(vals: Mapping[str, Decimal]) -> DebtSlots | Hold | None:
    """Build the two slots; None when the carrying lines are not applicable (no noncurrent or no current line)."""
    L, lc, ln, lease_reason, lease_tags = _lease_slot(vals)
    any_lease_fact = bool(lease_tags)
    tags: list[str] = []
    proofs: list[str] = []
    plain_complete = PLAIN_NONCURRENT in vals and (
        "DebtCurrent" in vals or PLAIN_CURRENT in vals
    )
    convertible_complete = (
        CONVERTIBLE_NONCURRENT in vals and CONVERTIBLE_CURRENT in vals
    )
    if convertible_complete and not plain_complete:
        # the debt is the convertible pair (TSLA 2014: LongTermDebtNoncurrent 593.6 is a stray mis-tag)
        bn, ntag, nproof = (
            vals[CONVERTIBLE_NONCURRENT],
            CONVERTIBLE_NONCURRENT,
            "convertible_noncurrent",
        )
    elif PLAIN_NONCURRENT in vals:
        bn, ntag, nproof = (
            vals[PLAIN_NONCURRENT],
            PLAIN_NONCURRENT,
            "noncurrent_tag_is_debt_only",
        )
    elif CONVERTIBLE_NONCURRENT in vals:
        bn, ntag, nproof = (
            vals[CONVERTIBLE_NONCURRENT],
            CONVERTIBLE_NONCURRENT,
            "convertible_noncurrent",
        )
    elif LEASE_INCL_NONCURRENT in vals and ln is not None:
        bn = vals[LEASE_INCL_NONCURRENT] - ln
        ntag, nproof = (
            LEASE_INCL_NONCURRENT,
            "lease_inclusive_line_less_noncurrent_lease_fact",
        )
        if bn < 0:
            return Hold("negative_component")
    elif LEASE_INCL_NONCURRENT in vals:
        return _lease_inclusive_only(vals)
    else:
        return None
    tags.append(ntag)
    proofs.append(nproof)
    bc, ctags, cproof, hold = _current_borrowings(vals, lc, any_lease_fact, bn)
    if hold:
        return Hold(hold)
    if bc is None:
        return None
    tags.extend(ctags)
    proofs.append(cproof)
    borrowings = bn + bc
    lt = vals.get("LongTermDebt")
    # LongTermDebt holds the long-term debt including current maturities but not the short-term borrowings
    short_inside = sum(
        (
            vals[t]
            for t in SHORT_TERM
            + ("OtherShortTermBorrowings", "ShortTermBankLoansAndNotesPayable")
            if t in vals and 0 < vals[t] <= bc * (1 + EXPLAIN_TOLERANCE)
        ),
        Decimal(0),
    )
    if (
        lt is not None
        and lt > 0
        and PLAIN_NONCURRENT in vals
        and lt
        >= bn  # a LongTermDebt below the noncurrent line is partial (r1 containment's case), not a total
        and abs(lt - (borrowings - short_inside)) > AGREEMENT_TOLERANCE * lt
    ):
        return None  # LongTermDebt describes other lines (partial / other basis)
    all_in = vals.get("DebtLongtermAndShorttermCombinedAmount")
    if (
        all_in is not None
        and all_in > 0
        and abs(all_in - borrowings) > AGREEMENT_TOLERANCE * all_in
    ):
        return None
    tags.extend(t for t in lease_tags if t not in tags)
    return DebtSlots(
        borrowings=borrowings,
        leases=L,
        lease_inclusive_total=None,
        tags=tuple(tags),
        proofs=tuple(proofs),
        path="carrying_slots",
        lease_reason=None if L is not None else lease_reason,
    )


def carrying_lines(
    vals: Mapping[str, Decimal], perimeter: str = DEFAULT_PERIMETER
) -> Carrying | Hold | None:
    if perimeter not in PERIMETERS:
        raise ValueError(f"perimeter {perimeter!r} not in {PERIMETERS}")
    slots = debt_slots(vals)
    if slots is None or isinstance(slots, Hold):
        return slots
    if slots.borrowings is None:  # lease-inclusive face lines only
        if perimeter == "borrowings_only":
            return Hold("borrowings_not_separable")
        assert slots.lease_inclusive_total is not None
        return Carrying(
            slots.lease_inclusive_total,
            slots.tags,
            slots.path,
            perimeter,
            COMPOSITION_LEASE_INCLUSIVE_LINES,
            slots,
        )
    if perimeter == "borrowings_only":
        return Carrying(
            slots.borrowings,
            slots.tags,
            slots.path,
            perimeter,
            COMPOSITION_BORROWINGS_ONLY,
            slots,
        )
    if slots.leases is None:
        return Carrying(
            slots.borrowings,
            slots.tags,
            slots.path,
            perimeter,
            COMPOSITION_LEASES_NOT_DETERMINED,
            slots,
        )
    return Carrying(
        slots.borrowings + slots.leases,
        slots.tags,
        slots.path,
        perimeter,
        COMPOSITION_BORROWINGS_PLUS_LEASES,
        slots,
    )
