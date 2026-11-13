"""total_debt perimeter, a post-pass of the cell proof (audit R07, founder 2026-11-04 doc 02 item 5).

prove_component proves that the shown value is the sum of the parts the company's map names. It cannot know a part
is missing: MSFT served LongTermDebtCurrent + LongTermDebtNoncurrent in every year and was PROVEN, while the filings
print a face short-term debt line (FY2015-17) and finance lease liabilities in a note (FY2017-26). This pass judges
the PERIMETER: a PROVEN total_debt cell stays PROVEN only if its claim names

  1. every face (BS) short-term / current debt line the filing prints at the cell's column (SHORT_FACE_TAGS), and
  2. the finance-lease liability the filing discloses at that column: FinanceLeaseLiability, or Current +
     Noncurrent (pre-ASC 842: CapitalLeaseObligations, or Current + Noncurrent),
     unless the lease already sits inside a debt line the claim names (double count guard):
       - the filer's location list (FinanceLease{Current,Noncurrent}StatementOfFinancialPositionExtensibleList)
         names a balance-sheet tag the claim carries (MU: DebtCurrent, LongTermDebtAndCapitalLeaseObligations),
         given as `lease_locations` {adsh: {lease tag: (location tags)}}; or
       - the claim carries a LongTermDebtAndCapitalLeaseObligations* line (that tag includes leases); or
       - the lease tag is a calc child of a claim part in the filing.
     The location list is a text fact the FSN num file does not keep, so with no `lease_locations` the last two
     rules are the only guard.

A missing part turns PROVEN into DISAGREE, reason perimeter_incomplete, with checks.perimeter =
{status, missing: [{tag, value, kind}]}. Operating leases are never debt. The pass only ever lowers a verdict.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from scrooner_pipeline.common.tag_aliases import with_aliases
from scrooner_pipeline.proof.fsn import FilingStructure, fsn_ddate
from scrooner_pipeline.proof.prove import (
    DISAGREE,
    PROVEN,
    Proof,
)

REASON = "perimeter_incomplete"

# face short-term / current debt lines (Tag Expert debt rules, data-team/tags/rules/bs.csv debt-lane members)
SHORT_FACE_TAGS = (
    "ShortTermBorrowings",
    "CommercialPaper",
    "DebtCurrent",
    "LongTermDebtCurrent",
    "ShortTermBankLoansAndNotesPayable",
    "OtherShortTermBorrowings",
    "LinesOfCreditCurrent",
    "ConvertibleDebtCurrent",
    "SecuredDebtCurrent",
    "NotesPayableCurrent",
    "LongTermDebtAndCapitalLeaseObligationsCurrent",
)
# (total tag, current tag, noncurrent tag): the total, else the two parts
LEASE_FAMILIES = (
    (
        "FinanceLeaseLiability",
        "FinanceLeaseLiabilityCurrent",
        "FinanceLeaseLiabilityNoncurrent",
    ),
    (
        "CapitalLeaseObligations",
        "CapitalLeaseObligationsCurrent",
        "CapitalLeaseObligationsNoncurrent",
    ),
)
LEASE_IN_DEBT_PREFIX = "LongTermDebtAndCapitalLeaseObligations"


def _names(claim_tags: set[str], tag: str) -> bool:
    """The claim names this tag, or an alias of it."""
    return any(a in claim_tags for a in with_aliases(tag)) or any(
        tag in with_aliases(c) for c in claim_tags
    )


def _value(s: FilingStructure, tag: str, ddate, qtrs: int) -> Decimal | None:
    for alt in with_aliases(tag):
        v = s.value(alt, ddate, qtrs)
        if v is not None and v.value != 0:
            return v.value
    return None


def missing_parts(
    s: FilingStructure,
    claim_tags: set[str],
    ddate,
    lease_locations: dict[str, tuple[str, ...]] | None = None,
) -> list[dict[str, Any]]:
    """Perimeter parts the filing prints at the column that the claim does not name."""
    out: list[dict[str, Any]] = []
    face = {ln.tag for ln in s.lines_on("BS")}
    required: dict[str, Decimal] = {}
    for tag in SHORT_FACE_TAGS:
        if tag not in face:
            continue
        v = _value(s, tag, ddate, 0)
        if v is not None:
            required[tag] = v
    for tag, v in required.items():
        if _names(claim_tags, tag):
            continue
        # a total the claim already carries through its children (DebtCurrent over LongTermDebtCurrent), or a
        # total whose children are themselves required, is not owed twice
        parents = s.calc_parents.get(tag, set())
        children = {c for c, _neg in s.calc_children.get(tag, [])}
        if any(_names(claim_tags, p) for p in parents):
            continue
        if children and any(c in required or _names(claim_tags, c) for c in children):
            continue
        out.append({"tag": tag, "value": str(v), "kind": "face_short_term_debt"})
    in_debt_family = any(c.startswith(LEASE_IN_DEBT_PREFIX) for c in claim_tags)
    for total, cur, noncur in LEASE_FAMILIES:
        owed: list[tuple[str, Decimal]] = []
        tv = _value(s, total, ddate, 0)
        if tv is not None:
            owed = [(total, tv)]
        else:
            for t in (cur, noncur):
                v = _value(s, t, ddate, 0)
                if v is not None:
                    owed.append((t, v))
        if not owed:
            continue
        for t, v in owed:
            if _names(claim_tags, t):
                continue
            locs = (lease_locations or {}).get(t, ())
            if in_debt_family:
                continue
            if locs and any(_names(claim_tags, loc) for loc in locs):
                continue  # the filer's own location list: the lease sits inside a debt line the claim carries
            if any(_names(claim_tags, p) for p in s.calc_parents.get(t, set())):
                continue
            out.append({"tag": t, "value": str(v), "kind": "finance_lease"})
    return out


def apply_perimeter(
    proofs: list[Proof],
    structures: dict[str, FilingStructure],
    lease_locations: dict[str, dict[str, tuple[str, ...]]] | None = None,
) -> int:
    """Post-pass over a company's proofs (in place). Returns the number of cells turned DISAGREE."""
    n = 0
    for p in proofs:
        sh = p.shown
        if sh.data_point_name.removesuffix("_resolved") != "total_debt":
            continue
        if p.verdict != PROVEN or sh.claim is None or sh.period_grain != "I":
            continue
        s = structures.get(p.position_accession or "")
        if s is None:
            continue
        c = sh.claim
        claim_tags = set(c.tags) | {t for _sg, t in c.parts}
        missing = missing_parts(
            s,
            claim_tags,
            fsn_ddate(sh.period_end),
            (lease_locations or {}).get(s.adsh),
        )
        if not missing:
            p.checks["perimeter"] = {"status": "pass"}
            continue
        p.checks["perimeter"] = {"status": "fail", "missing": missing}
        p.verdict, p.reason_code = DISAGREE, REASON
        p.reason_text = (
            "total_debt perimeter incomplete: the filing prints "
            + ", ".join(f"{m['tag']} {m['value']}" for m in missing)
            + " not in the claim"
        )
        n += 1
    return n
