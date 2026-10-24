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
# pre-ASC 842 total capital-lease obligation (current + noncurrent), used when FinanceLeaseLiability is absent
LEASE_TOTAL_PRE842 = (
    "CapitalLeasesFutureMinimumPaymentsPresentValueOfNetMinimumPayments"
)
LEASE_AGGREGATE = "DebtAndCapitalLeaseObligations"
REFINANCED = "ShortTermDebtRefinancedAmount"  # a duration fact; the caller keys it by the instant's end date
RELATED_PARTY = "NotesPayableRelatedPartiesCurrentAndNoncurrent"
# short-term borrowing face tags. AAPL prints "Commercial paper and repurchase agreements" as
# OtherShortTermBorrowings (11,166M at 2020-06-27 against a CommercialPaper note figure): the slot must include it.
SHORT_TERM = (
    "ShortTermBorrowings",
    "CommercialPaper",
    "OtherShortTermBorrowings",
    "ShortTermBankLoansAndNotesPayable",
    # KO prints "Loans and notes payable" (13,030M at 2019-06-28) under this tag
    "NotesAndLoansPayableCurrent",
)
CURRENT_PART_TAGS = (
    "ShortTermBorrowings",
    "CommercialPaper",
    "OtherShortTermBorrowings",
    "ShortTermBankLoansAndNotesPayable",
    "LinesOfCreditCurrent",
    "NotesPayableCurrent",
    "ConvertibleNotesPayableCurrent",
    PLAIN_CURRENT,
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
            LEASE_TOTAL_PRE842,
            LEASE_AGGREGATE,
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
# any of these filed beside DebtCurrent means part of it may be a lease, so its excess over the filed parts is
# not accepted without corroboration
LEASE_EVIDENCE_TAGS = (
    *LEASE_NONCURRENT,
    *LEASE_CURRENT,
    LEASE_TOTAL,
    LEASE_TOTAL_PRE842,
    LEASE_INCL_NONCURRENT,
    LEASE_INCL_CURRENT,
)
EXPLAIN_TOLERANCE = Decimal("0.02")
AGREEMENT_TOLERANCE = Decimal("0.10")
PERIMETERS = ("lease_inclusive", "borrowings_only")
DEFAULT_PERIMETER = "lease_inclusive"

COMPOSITION_BORROWINGS_PLUS_LEASES = "borrowings_plus_finance_leases"
COMPOSITION_LEASES_NOT_DETERMINED = "finance_leases_not_determined"
COMPOSITION_LEASES_INCOMPLETE = "finance_leases_incomplete"  # some lease fact is authoritative, the other half is not
COMPOSITION_LEASE_INCLUSIVE_LINES = "lease_inclusive_face_lines"
COMPOSITION_BORROWINGS_ONLY = "borrowings_only"


@dataclass(frozen=True)
class Hold:
    # current_block_unexplained | lease_location_unknown | short_term_overlap_unresolved | borrowings_not_separable
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
    # lease_facts_absent | lease_facts_incomplete | lease_zero_unproven when leases is None
    lease_reason: str | None = None
    # an actual lease FACT (not a half derived from face lines) is authoritative
    lease_fact_filed: bool = False


@dataclass(frozen=True)
class Carrying:
    value: Decimal
    tags: tuple[str, ...]
    path: str
    perimeter: str  # the perimeter requested
    composition: str  # what value is: see COMPOSITION_*
    slots: DebtSlots


def trailing_unit(x: Decimal) -> Decimal:
    """The power of ten a whole-dollar amount is rounded to (1,384,000,000 -> 1,000,000); 1 for any amount
    that is not a round number. Capped at 1e9."""
    n = abs(x)
    if n != n.to_integral_value() or n == 0:
        return Decimal(1)
    unit = Decimal(1)
    while unit < Decimal(10) ** 9 and n % (unit * 10) == 0:
        unit *= 10
    return unit


def is_rounding_variant(coarse: Decimal, precise: Decimal) -> bool:
    """``coarse`` is ``precise`` rounded to its own trailing-zero unit, at most to the million (filers round to
    thousands or millions): NVDA 1,384,000,000 vs 1,384,342,000; 14,000,000 vs 14,086,000. Within half the unit."""
    if coarse == precise:
        return True
    unit = min(trailing_unit(coarse), Decimal(10) ** 6)
    return unit > 1 and abs(coarse - precise) <= unit / 2


def refine_copies(
    copies: list[tuple[Decimal, int, bool]],
) -> tuple[Decimal, int] | None:
    """Pick the value of ONE line from its copies (value, fact id, authoritative): the most precise copy that
    the anchor is a rounded form of ("a rounded copy never replaces a precise one", ledger).
    With an authoritative copy it anchors the choice; without one, at least two copies must all be rounding
    variants of the most precise (Stage 2e de-authorized a rounded/precise pair as a conflict; WO-23's case).
    A genuine conflict, or a lone non-authoritative copy, returns None."""
    if not copies:
        return None
    auth = [c for c in copies if c[2]]
    if auth:
        anchor = max(auth, key=lambda c: c[1])
        pool = [c for c in copies if is_rounding_variant(anchor[0], c[0])]
    else:
        if len(copies) < 2:
            return None
        pool = copies
    best = min(pool, key=lambda c: (trailing_unit(c[0]), -c[1]))
    if not auth and not all(is_rounding_variant(c[0], best[0]) for c in copies):
        return None
    return best[0], best[1]


def _first(vals: Mapping[str, Decimal], tags: tuple[str, ...]) -> str | None:
    return next((t for t in tags if t in vals), None)


def _lease_slot(
    vals: Mapping[str, Decimal],
) -> tuple[Decimal | None, Decimal | None, Decimal | None, str | None, list[str]]:
    """(L total, L current, L noncurrent, reason when unverified, tags).

    A missing half is derived from the lease-inclusive face line less the debt-only line when both are filed
    (GOOG 2016-06-30: lease-inclusive noncurrent 1,984 less LongTermDebtNoncurrent 1,984 = 0)."""
    ct, nt = _first(vals, LEASE_CURRENT), _first(vals, LEASE_NONCURRENT)
    lc = vals[ct] if ct else None
    ln = vals[nt] if nt else None
    filed_zero_proof = (
        bool(ct and nt) or LEASE_TOTAL in vals or LEASE_TOTAL_PRE842 in vals
    )
    tags = [t for t in (ct, nt) if t]
    if ln is None and LEASE_INCL_NONCURRENT in vals and PLAIN_NONCURRENT in vals:
        ln = max(vals[LEASE_INCL_NONCURRENT] - vals[PLAIN_NONCURRENT], Decimal(0))
        tags += [LEASE_INCL_NONCURRENT, PLAIN_NONCURRENT]
    if lc is None and LEASE_INCL_CURRENT in vals and PLAIN_CURRENT in vals:
        lc = max(vals[LEASE_INCL_CURRENT] - vals[PLAIN_CURRENT], Decimal(0))
        tags += [LEASE_INCL_CURRENT, PLAIN_CURRENT]
    if lc is None and vals.get("DebtCurrent") == 0:
        lc = Decimal(
            0
        )  # DebtCurrent includes current capital leases by definition: zero means none
        tags.append("DebtCurrent")
    for total_tag in (LEASE_TOTAL, LEASE_TOTAL_PRE842):
        if total_tag in vals:
            return vals[total_tag], lc, ln, None, [total_tag, *tags]
    if lc is not None and ln is not None:
        if lc + ln == 0 and not filed_zero_proof:
            # zeros derived from face-line differences are not a filed zero (AVGO FY2025)
            return None, lc, ln, "lease_zero_unproven", tags
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


def _short_amount(vals: Mapping[str, Decimal], limit: Decimal) -> Decimal:
    """The short-term borrowings inside a current side (for the LongTermDebt agreement): distinct amounts; a
    container counts once."""
    distinct = sorted(
        {vals[t] for t in SHORT_TERM if t in vals and 0 < vals[t] <= limit}
    )
    if len(distinct) <= 1:
        return sum(distinct, Decimal(0))
    top, rest = distinct[-1], distinct[:-1]
    for n in range(1, len(rest) + 1):
        for combo in combinations(rest, n):
            if abs(sum(combo) - top) <= CORROBORATION_TOLERANCE * top:
                return top
    return sum(distinct, Decimal(0))


def _short_term(
    vals: Mapping[str, Decimal], current_maturities: Decimal, bn: Decimal
) -> tuple[Decimal, list[str], str, str | None]:
    """The short-term borrowings slot: (value, tags, proof, hold reason).

    Tags holding the same amount are one line (AAPL 2019-09-28: CommercialPaper = OtherShortTermBorrowings =
    5,980); a value equal to the current maturities is the same debt tagged twice and is dropped. Distinct
    amounts may overlap (a note figure inside the face line) or be separate lines: they are summed only when the
    company-stated total proves the sum, else HELD (``short_term_overlap_unresolved``)."""
    present = {
        t: vals[t]
        for t in SHORT_TERM
        if t in vals and vals[t] > 0 and vals[t] != current_maturities
    }
    if not present:
        return Decimal(0), [], "", None
    distinct = sorted(set(present.values()))
    if len(distinct) == 1:
        tags = [t for t in SHORT_TERM if t in present]
        return (
            distinct[0],
            tags,
            "+short_term" + ("_same_line" if len(tags) > 1 else ""),
            None,
        )
    # one amount equal to the sum of the others is the line that CONTAINS them (KO 2019-12-31: short-term
    # borrowings 10,994 = commercial paper 10,007 + other 987): the container is the slot
    top, rest = distinct[-1], distinct[:-1]
    for n in range(1, len(rest) + 1):
        for combo in combinations(rest, n):
            if abs(sum(combo) - top) <= CORROBORATION_TOLERANCE * top:
                tags = [t for t in SHORT_TERM if t in present and present[t] == top]
                return top, tags, "+short_term_container_of_components", None
    all_in = vals.get("DebtLongtermAndShorttermCombinedAmount")
    if all_in:
        for n in range(len(distinct), 0, -1):
            for combo in combinations(distinct, n):
                if (
                    abs(bn + current_maturities + sum(combo) - all_in)
                    <= CORROBORATION_TOLERANCE * all_in
                ):
                    tags = [
                        t for t in SHORT_TERM if t in present and present[t] in combo
                    ]
                    return (
                        sum(combo, Decimal(0)),
                        tags,
                        "+short_term_confirmed_by_stated_total",
                        None,
                    )
    return Decimal(0), [], "", "short_term_overlap_unresolved"


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
        if dc == 0 and (lc is None or lc == 0):
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
                uncontradicted = dc > sum(parts) - tol
                if uncontradicted and _corroborated(vals, bn, dc, short):
                    proof += "+corroborated_by_stated_total"
                elif uncontradicted and not any(t in vals for t in LEASE_EVIDENCE_TAGS):
                    # DebtCurrent is itself the face line ("Short-term debt", "Loans payable and current
                    # portion of long-term debt"): the filer tags only some of it (commercial paper, or
                    # nothing). No filed part exceeds it and no lease line sits beside it that could be
                    # inside it, so it is the whole current side (MRK, INTC, UNH, CSCO). With any lease
                    # evidence filed the excess may be a lease: HELD (GOOG 2018-03-31, TSLA).
                    proof += "+face_line_no_lease_evidence"
                else:
                    return None, tags, proof, "current_block_unexplained"
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
        st, st_tags, st_proof, st_hold = _short_term(vals, c, bn)
        if st_hold:
            return None, tags, "", st_hold
        tags += st_tags
        return c + st, tags, "current_maturities" + st_proof, None
    if CONVERTIBLE_CURRENT in vals:
        return (
            vals[CONVERTIBLE_CURRENT],
            [CONVERTIBLE_CURRENT],
            "convertible_current",
            None,
        )
    return None, [], "", None


OTHER_DEBT_LINE_SHARE = Decimal("0.05")


def _lease_inclusive_only(vals: Mapping[str, Decimal]) -> DebtSlots | Hold | None:
    """Lease-inclusive face lines and no lease facts to separate them (DPZ, MU 2021, TSLA).

    The total of the two lease-inclusive lines is used only when nothing else says other debt face lines
    exist: a related-party notes line, or a debt-only subtotal (DebtCurrent / LongTermDebt) of a size that
    belongs to the same debt. TSLA files both beside its lease-inclusive lines and some of its face lines
    (related-party convertibles, 2.4-2.6M) have no stored fact, so the total would silently miss them:
    HELD. The filer's own aggregate DebtAndCapitalLeaseObligations equal to DebtCurrent + the noncurrent line
    proves both lines are lease-inclusive and complete (MU 2021: 155 + 6,621 = 6,776)."""
    n = vals[LEASE_INCL_NONCURRENT]
    agg = vals.get(LEASE_AGGREGATE)
    dc = vals.get("DebtCurrent")
    if LEASE_INCL_CURRENT in vals:
        c = vals[LEASE_INCL_CURRENT]
    elif (
        dc is not None
        and agg is not None
        and abs(agg - (dc + n)) <= CORROBORATION_TOLERANCE * agg
    ):
        c = dc  # DebtCurrent is the lease-inclusive current line, proved by the filer's own aggregate
    else:
        return None
    st, st_tags, st_proof = Decimal(0), [], ""
    if LEASE_INCL_CURRENT in vals:
        # a separate short-term borrowings face line sits beside the lease-inclusive current line (ABBV: 12M in
        # 2022-03-31, 400M in 2017-12-31); with DebtCurrent as the current line it already holds them
        st, st_tags, st_proof, st_hold = _short_term(vals, c, n)
        if st_hold:
            return Hold(st_hold)
    total = n + c + st
    proven = agg is not None and any(
        abs(agg - x) <= CORROBORATION_TOLERANCE * agg for x in (n + c, total)
    )
    if not proven:
        other = [vals[t] for t in (RELATED_PARTY, "LongTermDebt") if t in vals]
        if dc is not None and LEASE_INCL_CURRENT in vals:
            other.append(dc)
        if RELATED_PARTY in vals or any(
            v >= OTHER_DEBT_LINE_SHARE * total for v in other
        ):
            return Hold("related_party_unresolved")
    return DebtSlots(
        borrowings=None,
        leases=None,
        lease_inclusive_total=total,
        tags=tuple(
            t
            for t in (
                LEASE_INCL_NONCURRENT,
                LEASE_INCL_CURRENT if LEASE_INCL_CURRENT in vals else "DebtCurrent",
                *st_tags,
            )
            if t
        ),
        proofs=(
            "lease_inclusive_face_lines_same_perimeter"
            + ("+filer_aggregate" if proven else "")
            + st_proof,
        ),
        path="carrying_lease_inclusive_lines",
        lease_reason="lease_facts_absent",
    )


_SHORT_ONLY_TAGS = frozenset(
    {
        PLAIN_NONCURRENT,
        *SHORT_TERM,
        *LEASE_NONCURRENT,
        *LEASE_CURRENT,
        LEASE_TOTAL,
        LEASE_TOTAL_PRE842,
        REFINANCED,
    }
)


def _may_hold_current_maturities(tag: str) -> bool:
    """A filed debt line other than the noncurrent line, the short-term lines and the lease facts could be the
    current maturities (AMD: the lease-inclusive current line; KO: the including-current-maturities total), so a
    short-term-only composition would drop it."""
    return tag not in _SHORT_ONLY_TAGS and (
        tag in CARRYING_TAGS or "CurrentMaturities" in tag
    )


def debt_slots(vals: Mapping[str, Decimal]) -> DebtSlots | Hold | None:
    """Build the two slots; None when the carrying lines are not applicable (no noncurrent or no current line)."""
    L, lc, ln, lease_reason, lease_tags = _lease_slot(vals)
    nt_tag = _first(vals, LEASE_NONCURRENT)
    # only filed lease FACTS count here; a half derived from the face lines does not locate the current leases
    any_lease_fact = any(
        t in vals
        for t in (LEASE_TOTAL, LEASE_TOTAL_PRE842, *LEASE_CURRENT, *LEASE_NONCURRENT)
    )
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
    lt_precise = vals.get("LongTermDebt")
    if (
        lt_precise is not None
        and ntag in (PLAIN_NONCURRENT, CONVERTIBLE_NONCURRENT)
        and lt_precise != bn
        and is_rounding_variant(bn, lt_precise)
    ):
        # the face "Long-term debt" is the precise copy of the rounded note figure (NVDA FY2015)
        bn = lt_precise
        nproof += "+precise_copy_long_term_debt"
        tags.append(ntag)
        ntag = "LongTermDebt"
    tags.append(ntag)
    proofs.append(nproof)
    bc, ctags, cproof, hold = _current_borrowings(vals, lc, any_lease_fact, bn)
    if (
        bc is None
        and hold is None
        and ntag == PLAIN_NONCURRENT
        and not any(_may_hold_current_maturities(t) for t in vals)
    ):
        # only a short-term borrowings line is filed beside the noncurrent line (CVX 2014-2015: "Short-term
        # debt" 3,908 + "Long-term debt" 29,960 + "Capital lease obligations" 65): the legacy path's composition,
        # now with the noncurrent capital-lease face line
        st, st_tags, st_proof, st_hold = _short_term(vals, Decimal(0), bn)
        # an overlap among the short-term amounts is not decided here: the legacy path keeps deciding (LLY 2010)
        if not st_hold and st > 0:
            bc, ctags, cproof = (
                st,
                st_tags,
                "short_term_only_no_current_maturities_tagged" + st_proof,
            )
            if (
                lc is None
                and ln is not None
                and nt_tag == "CapitalLeaseObligationsNoncurrent"
            ):
                # pre-ASC 842: the current capital lease is inside the current debt lines, only the noncurrent
                # one is a face line of its own
                L, lease_reason = ln, None
    if hold == "lease_location_unknown" and LEASE_INCL_NONCURRENT in vals:
        # the current side cannot be split, but the filer's own aggregate may prove both lines lease-inclusive
        alt = _lease_inclusive_only(vals)
        if isinstance(alt, DebtSlots):
            return alt
    if hold:
        return Hold(hold)
    if bc is None:
        return None
    tags.extend(ctags)
    proofs.append(cproof)
    borrowings = bn + bc
    lt = vals.get("LongTermDebt")
    # LongTermDebt holds the long-term debt including current maturities but not the short-term borrowings
    short_inside = _short_amount(vals, bc * (1 + EXPLAIN_TOLERANCE))
    if (
        lt is not None
        and lt > 0
        and PLAIN_NONCURRENT in vals
        and lt
        >= bn  # a LongTermDebt below the noncurrent line is partial (r1 containment's case), not a total
        and abs(lt - (borrowings - short_inside)) > AGREEMENT_TOLERANCE * lt
        # LongTermDebt that is exactly the noncurrent line plus the current maturities agrees (CSCO: the
        # rest of DebtCurrent is untagged short-term debt that LongTermDebt never holds)
        and not (
            PLAIN_CURRENT in vals
            and abs(lt - (bn + vals[PLAIN_CURRENT])) <= CORROBORATION_TOLERANCE * lt
        )
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
        lease_fact_filed=any_lease_fact,
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
            COMPOSITION_LEASES_INCOMPLETE
            if slots.lease_reason == "lease_facts_incomplete" and slots.lease_fact_filed
            else COMPOSITION_LEASES_NOT_DETERMINED,
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
