"""Proof v22: era parts of a filing's own column (TMO total_debt Dec-2020), split parts against the combined face line.
Each test fails without its rule (mutation-checked)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.proof.shown import component_sum_authority_by_era

D = Decimal
OWN = ((1, "DebtCurrent"), (1, "LongTermDebtNoncurrent"))
ERA2021 = ((1, "DebtCurrent"), (1, "LongTermDebtAndCapitalLeaseObligations"))


def test_a_later_filings_era_part_it_does_not_print_never_counts_as_zero():
    # TMO Dec-2020: the FY2020 10-K prints both parts; the Q2-2021 10-Q (era 2021 names LTD&CL) prints the Dec-2020
    # column under LongTermDebtNoncurrent, so its era part is absent. zero_ok would make it 0 and the sum 2,628M.
    copies = [
        ("K20", D("2628"), "DebtCurrent"),
        ("K20", D("19107"), "LongTermDebtNoncurrent"),
        ("Q221", D("2628"), "DebtCurrent"),
        ("Q221", D("19107"), "LongTermDebtNoncurrent"),
    ]
    filed = {"K20": date(2021, 2, 25), "Q221": date(2021, 8, 6)}
    win = component_sum_authority_by_era(
        copies,
        OWN,
        {"K20": OWN, "Q221": ERA2021},
        filed,
        None,
        zero_ok=lambda a, t: True,
    )
    assert win == ("Q221", D("21735"))  # the latest filing, read with the cell's own complete part set


def _split_cells(dep, amort):
    from scrooner_pipeline.proof.prove import PROVEN, Proof, Shown

    split = (("DepreciationDepletionAndAmortization", ("depreciation_and_amortization", "amortization_of_intangibles")),)

    def mk(name, v):
        s = Shown(1, name, "FY", date(2019, 1, 1), date(2019, 12, 31), D(v), (), "A-1", (1,), combined_splits=split)
        return Proof(shown=s, verdict=PROVEN)

    return [mk("depreciation_and_amortization_resolved", dep), mk("amortization_of_intangibles", amort)]


def _structure_with_line(value):
    from scrooner_pipeline.proof.fsn import FilingStructure, NumValue

    st = FilingStructure("A-1", "1", "10-K", date(2020, 2, 1), date(2019, 12, 31))
    tag = "DepreciationDepletionAndAmortization"
    st.num[(tag, date(2019, 12, 31), 4)].append(NumValue(tag, "us-gaap/2019", date(2019, 12, 31), 4, "USD", D(value), -6))
    return st


def test_split_parts_must_sum_to_the_combined_face_line():
    from scrooner_pipeline.proof.identities import SPLIT_REASON, apply_identities
    from scrooner_pipeline.proof.prove import DISAGREE, PROVEN

    st = {"A-1": _structure_with_line("199700000")}
    ok = _split_cells("156700000", "43000000")  # 156.7 + 43.0 = 199.7
    apply_identities(ok, structures=st)
    assert [p.verdict for p in ok] == [PROVEN, PROVEN]
    assert ok[0].checks["split_parts"]["status"] == "pass"
    bad = _split_cells("156700000", "30100000")  # 186.8 vs 199.7
    counts = apply_identities(bad, structures=st)
    assert [p.verdict for p in bad] == [DISAGREE, DISAGREE]
    assert {p.reason_code for p in bad} == {SPLIT_REASON}
    assert counts == {"split:DepreciationDepletionAndAmortization": 1}
    # the combined line is not printed in the filing: not judged here
    none = _split_cells("156700000", "30100000")
    apply_identities(none, structures={"A-1": _structure_with_line("199700000").__class__("A-1", "1", "10-K", None, None)})
    assert [p.verdict for p in none] == [PROVEN, PROVEN]


def test_a_later_filing_that_prints_its_era_parts_keeps_them():
    # MO: the later filing prints the column under its own era tags (COGS + OtherCost): still read with them
    own = ((1, "COGS"), (1, "Excise"))
    era = ((1, "COGS"), (1, "OtherCost"))
    copies = [
        ("A", D("10"), "COGS"),
        ("A", D("2"), "Excise"),
        ("B", D("10"), "COGS"),
        ("B", D("3"), "OtherCost"),
    ]
    filed = {"A": date(2019, 1, 1), "B": date(2021, 1, 1)}
    win = component_sum_authority_by_era(copies, own, {"A": own, "B": era}, filed)
    assert win == ("B", D("13"))
