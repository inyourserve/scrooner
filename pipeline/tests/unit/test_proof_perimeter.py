"""total_debt perimeter post-pass (proof/perimeter.py, audit R07): a partial sum cannot stay PROVEN."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine
from scrooner_pipeline.proof.perimeter import REASON, apply_perimeter
from scrooner_pipeline.proof.prove import DISAGREE, PROVEN, Claim, Proof, Shown

ADSH = "0001193125-26-323660"
END = date(2025, 6, 30)
B = 1_000_000_000


def struct(face: dict[str, int], notes: dict[str, int], calc=None) -> FilingStructure:
    s = FilingStructure(ADSH, "0000789019", "10-K", date(2025, 7, 30), END)
    for i, tag in enumerate(face):
        s.pre.append(PreLine(4, i, "BS", tag, "us-gaap/2025", tag, False))
    for tag, v in {**face, **notes}.items():
        s.num[(tag, END, 0)].append(
            NumValue(tag, "us-gaap/2025", END, 0, "USD", Decimal(v * B), -6)
        )
    for parent, kids in (calc or {}).items():
        for k in kids:
            s.calc_children[parent].append((k, False))
            s.calc_parents[k].add(parent)
    return s


def proof(parts: list[str], value: int, grain="I") -> Proof:
    claim = Claim("component", "BS", parts=tuple((1, t) for t in parts))
    sh = Shown(
        1,
        "total_debt_resolved",
        grain,
        END,
        END,
        Decimal(value * B),
        tuple(parts),
        ADSH,
        (1,),
        claim=claim,
    )
    return Proof(sh, PROVEN, position_accession=ADSH)


MSFT_FACE = {"LongTermDebtCurrent": 3, "LongTermDebtNoncurrent": 40}
LEASE = {"FinanceLeaseLiability": 46}


def run(parts, value, face, notes, calc=None, locs=None):
    p = proof(parts, value)
    n = apply_perimeter([p], {ADSH: struct(face, notes, calc)}, locs)
    return p, n


@pytest.mark.unit
def test_msft_shape_ltd_only_is_disagree_and_with_leases_is_proven():
    p, n = run(["LongTermDebtCurrent", "LongTermDebtNoncurrent"], 43, MSFT_FACE, LEASE)
    assert (p.verdict, p.reason_code, n) == (DISAGREE, REASON, 1)
    assert p.checks["perimeter"]["missing"] == [
        {"tag": "FinanceLeaseLiability", "value": str(46 * B), "kind": "finance_lease"}
    ]
    p, n = run(
        ["LongTermDebtCurrent", "LongTermDebtNoncurrent", "FinanceLeaseLiability"],
        89,
        MSFT_FACE,
        LEASE,
    )
    assert (p.verdict, n) == (PROVEN, 0)
    assert p.checks["perimeter"]["status"] == "pass"


@pytest.mark.unit
def test_face_short_term_debt_line_missing():
    # MSFT FY2016: 12,904 short-term debt + 0 current LTD + 40,557 LTD noncurrent = 53,461
    face = {"ShortTermBorrowings": 13, "LongTermDebtNoncurrent": 40}
    p, _ = run(["LongTermDebtCurrent", "LongTermDebtNoncurrent"], 40, face, {})
    assert p.reason_code == REASON
    assert p.checks["perimeter"]["missing"][0]["tag"] == "ShortTermBorrowings"
    p, _ = run(["ShortTermBorrowings", "LongTermDebtNoncurrent"], 53, face, {})
    assert p.verdict == PROVEN


@pytest.mark.unit
def test_lease_inside_a_debt_line_is_not_double_counted():
    # LongTermDebtAndCapitalLeaseObligations includes leases (family rule)
    face = {"LongTermDebtAndCapitalLeaseObligations": 50}
    p, _ = run(["LongTermDebtAndCapitalLeaseObligations"], 50, face, LEASE)
    assert p.verdict == PROVEN
    # the lease is a calc child of a claimed debt line
    face = {"DebtCurrent": 5}
    p, _ = run(
        ["DebtCurrent"],
        5,
        face,
        {"FinanceLeaseLiabilityCurrent": 1},
        calc={"DebtCurrent": ["FinanceLeaseLiabilityCurrent"]},
    )
    assert p.verdict == PROVEN


@pytest.mark.unit
def test_pre_842_capital_lease_is_required():
    face = {"LongTermDebtNoncurrent": 10}
    notes = {
        "CapitalLeaseObligationsCurrent": 1,
        "CapitalLeaseObligationsNoncurrent": 2,
    }
    p, _ = run(["LongTermDebtNoncurrent"], 10, face, notes)
    assert [m["tag"] for m in p.checks["perimeter"]["missing"]] == [
        "CapitalLeaseObligationsCurrent",
        "CapitalLeaseObligationsNoncurrent",
    ]
    p, _ = run(
        [
            "LongTermDebtNoncurrent",
            "CapitalLeaseObligationsCurrent",
            "CapitalLeaseObligationsNoncurrent",
        ],
        13,
        face,
        notes,
    )
    assert p.verdict == PROVEN


@pytest.mark.unit
def test_extensible_list_guard_names_a_debt_line_the_claim_carries():
    # MU: the finance lease sits inside DebtCurrent
    face = {"DebtCurrent": 5, "LongTermDebtNoncurrent": 9}
    locs = {ADSH: {"FinanceLeaseLiability": ("DebtCurrent",)}}
    p, _ = run(["DebtCurrent", "LongTermDebtNoncurrent"], 14, face, LEASE, locs=locs)
    assert p.verdict == PROVEN
    # GOOG: the list names a non-debt line, so the lease is owed
    locs = {ADSH: {"FinanceLeaseLiability": ("OtherLiabilitiesNoncurrent",)}}
    p, _ = run(["DebtCurrent", "LongTermDebtNoncurrent"], 14, face, LEASE, locs=locs)
    assert p.reason_code == REASON


@pytest.mark.unit
def test_operating_lease_and_other_cells_untouched():
    p, _ = run(
        ["LongTermDebtNoncurrent"],
        40,
        {"LongTermDebtNoncurrent": 40},
        {"OperatingLeaseLiability": 9},
    )
    assert p.verdict == PROVEN
    q = proof(["LongTermDebtNoncurrent"], 40)
    q.shown = Shown(
        1, "revenue", "I", END, END, Decimal(1), (), ADSH, (1,), claim=q.shown.claim
    )
    assert apply_perimeter([q], {ADSH: struct({}, LEASE)}) == 0


@pytest.mark.unit
def test_lease_total_is_carried_by_its_current_and_noncurrent_parts():
    """WMT FY2016: the claim names CapitalLeaseObligationsCurrent + Noncurrent and the note total is their sum."""
    face = {"ShortTermBorrowings": 3, "LongTermDebtNoncurrent": 40}
    notes = {
        "CapitalLeaseObligations": 7,
        "CapitalLeaseObligationsCurrent": 1,
        "CapitalLeaseObligationsNoncurrent": 6,
    }
    parts = [
        "ShortTermBorrowings",
        "LongTermDebtNoncurrent",
        "CapitalLeaseObligationsCurrent",
        "CapitalLeaseObligationsNoncurrent",
    ]
    p, n = run(parts, 50, face, notes)
    assert (p.verdict, n) == (PROVEN, 0)
    # the parts do not add up to the total (a piece sits elsewhere): still incomplete
    p, n = run(parts, 50, face, {**notes, "CapitalLeaseObligations": 9})
    assert (p.verdict, p.reason_code) == (DISAGREE, REASON)
    # VRTX shape: the claim names only the noncurrent part
    p, n = run(
        ["LongTermDebtNoncurrent", "CapitalLeaseObligationsNoncurrent"],
        46,
        {"LongTermDebtNoncurrent": 40},
        notes,
    )
    assert (p.verdict, p.reason_code) == (DISAGREE, REASON)


@pytest.mark.unit
def test_one_current_debt_line_under_two_tags_is_not_owed_twice():
    """AMAT FY2019: face ShortTermBorrowings 600 and note LongTermDebtCurrent 600 are one line."""
    face = {"ShortTermBorrowings": 6, "LongTermDebtNoncurrent": 47}
    parts = ["LongTermDebtCurrent", "LongTermDebtNoncurrent"]
    p, n = run(parts, 53, face, {"LongTermDebtCurrent": 6})
    assert (p.verdict, n) == (PROVEN, 0)
    # a different amount is a second line
    p, n = run(parts, 53, face, {"LongTermDebtCurrent": 5})
    assert (p.verdict, p.reason_code) == (DISAGREE, REASON)
