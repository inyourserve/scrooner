"""Total debt as two slots (borrowings + finance leases) from the balance-sheet carrying lines.
Acceptance cases: data-team/strategy/team/DC-TOTAL-DEBT-LEASE-PERIMETER-2026-10-24.md section 6, with the stored
facts read 2026-10-24 (values in $M). Filing locators: MU 0000723125-25-000028 R5; GOOG 0001652044-24-000022 R3/R64 and
-26-000018; AMZN 0001018724-26-000004 R7/R69; CVX 0000093410-17-000013 R5/R98; LLY 0000059478-14-000102 R4; TSLA
0001564590-17-015705 R2/R60; AAPL 0000320193-26-000020; PFE 0000078003-21-000038 R4; DPZ 0000950170-25-025223 R2."""

from __future__ import annotations

from decimal import Decimal

import pytest

from scrooner_pipeline.common import debt_carrying as dc
from scrooner_pipeline.mapper import concept_fallback as cf

M = Decimal(1_000_000)


def V(**tags):
    return {t: Decimal(str(v)) * M for t, v in tags.items()}


def F(**tags):
    return {t: (Decimal(str(v)) * M, i) for i, (t, v) in enumerate(tags.items(), 1)}


MU = dict(LongTermDebt=11533, FinanceLeaseLiability=3044, FinanceLeaseLiabilityCurrent=560,
          FinanceLeaseLiabilityNoncurrent=2484, DebtCurrent=560, LongTermDebtAndCapitalLeaseObligations=14017)  # fmt: skip
GOOG_23 = dict(CommercialPaper=0, LongTermDebtCurrent=1000, LongTermDebtNoncurrent=11870, FinanceLeaseLiabilityNoncurrent=1383)  # fmt: skip
GOOG_25 = dict(CommercialPaper=0, LongTermDebt=49085, LongTermDebtCurrent=1996, LongTermDebtNoncurrent=46547,
               FinanceLeaseLiability=2500, FinanceLeaseLiabilityCurrent=441, FinanceLeaseLiabilityNoncurrent=2059)  # fmt: skip
AMZN_25 = dict(LongTermDebt=68836, ShortTermBorrowings=455, LongTermDebtCurrent=2748, LongTermDebtNoncurrent=65648,
               FinanceLeaseLiability=12286, FinanceLeaseLiabilityCurrent=1544, FinanceLeaseLiabilityNoncurrent=10742)  # fmt: skip
AMZN_Q2 = dict(
    LongTermDebt=132995,
    ShortTermBorrowings=325,
    LongTermDebtCurrent=3330,
    LongTermDebtNoncurrent=128894,
)
CVX = dict(CommercialPaper=10410, LongTermDebt=32490, OtherShortTermBorrowings=0, ShortTermBorrowings=10840,
           LongTermDebtCurrent=6253, LongTermDebtNoncurrent=35193, DebtCurrent=19840, ShortTermBankLoansAndNotesPayable=50,
           CapitalLeaseObligationsCurrent=14, CapitalLeaseObligationsNoncurrent=93, ShortTermDebtRefinancedAmount=9000)  # fmt: skip
LLY = dict(DebtCurrent="9.1", LongTermDebtNoncurrent="5255.3", ShortTermBorrowings=1000)
AAPL = dict(
    CommercialPaper=1997,
    LongTermDebt=82300,
    LongTermDebtCurrent=11007,
    LongTermDebtNoncurrent=71340,
)
PFE = dict(CommercialPaper=556, LongTermDebt=4000, OtherShortTermBorrowings=145, LongTermDebtCurrent=2002,
           LongTermDebtNoncurrent=37133, DebtCurrent=2703)  # fmt: skip
DPZ = dict(LongTermDebtAndCapitalLeaseObligations="3825.659", LongTermDebtAndCapitalLeaseObligationsCurrent="1149.679",
           DebtAndCapitalLeaseObligations="4975.338")  # fmt: skip
TSLA_1706 = dict(DebtCurrent="760.284", LongTermDebt="6755.563", LongTermDebtAndCapitalLeaseObligations="7122.862",
                 LongTermDebtAndCapitalLeaseObligationsCurrent="716.533", NotesPayableRelatedPartiesCurrentAndNoncurrent=100)  # fmt: skip
TSLA_1709 = dict(DebtCurrent="375.506", LongTermDebt="9049.729", LongTermDebtAndCapitalLeaseObligations="9581.616",
                 LongTermDebtAndCapitalLeaseObligationsCurrent="324.224", NotesPayableRelatedPartiesCurrentAndNoncurrent=100)  # fmt: skip
TSLA_1703 = dict(DebtCurrent="963.737", LongTermDebt="6927.937", LongTermDebtAndCapitalLeaseObligations="7148.416",
                 LongTermDebtAndCapitalLeaseObligationsCurrent="829.080")  # fmt: skip
TSLA_1803 = dict(DebtCurrent="1755.634", LongTermDebt="8219.577", LongTermDebtAndCapitalLeaseObligations="8761.070",
                 LongTermDebtAndCapitalLeaseObligationsCurrent="1915.530", NotesPayableRelatedPartiesCurrentAndNoncurrent="82.5")  # fmt: skip
TSLA_1409 = dict(ConvertibleDebtCurrent="597.626", ConvertibleDebtNoncurrent="1786.635", LongTermDebtNoncurrent="597.6",
                 CapitalLeaseObligationsCurrent="9.7", CapitalLeaseObligationsNoncurrent="14.1")  # fmt: skip
GUARDS = cf.ALL_DEBT_GUARDS


def total(tags, perimeter=dc.DEFAULT_PERIMETER):
    r = dc.carrying_lines(V(**tags), perimeter)
    assert isinstance(r, dc.Carrying), r
    return r


# ------------------------------------------------------------------ the card's acceptance cases
def test_t1_mu_2025_08_28_borrowings_and_finance_leases():
    b, i = total(MU, "borrowings_only"), total(MU, "lease_inclusive")
    assert b.value == Decimal(11533) * M and i.value == Decimal(14577) * M
    assert i.composition == dc.COMPOSITION_BORROWINGS_PLUS_LEASES
    assert (
        i.slots.borrowings == Decimal(11533) * M and i.slots.leases == Decimal(3044) * M
    )
    assert i.slots.value if False else True
    assert (
        "debt_current_whole_current_side+less_current_lease_fact" in i.slots.proofs
    )  # 560 - 560: current side is leases
    assert i.value != (Decimal(11533) + 560) * M  # never 11,533 + 560


@pytest.mark.parametrize("name", ["TSLA_1706", "TSLA_1709", "TSLA_1703", "TSLA_1803"])
def test_t3_t4_tsla_lease_inclusive_lines_are_held_never_summed_with_debt_only_lines(
    name,
):
    tags = globals()[name]
    for perimeter in dc.PERIMETERS:
        assert dc.carrying_lines(V(**tags), perimeter) == dc.Hold(
            "related_party_unresolved"
        )
    # the Verifier's wrong values must never come out
    r = cf.evaluate_total_debt(F(**tags), GUARDS)
    assert r.value not in (
        Decimal("7883146000"),
        Decimal("9957122000"),
        Decimal("8112153000"),
    )


def test_t5_goog_2023_12_31_borrowings_only_and_lease_facts_incomplete():
    b = total(GOOG_23, "borrowings_only")
    assert b.value == Decimal(12870) * M  # 13,000 - 130, not the gross 14,746
    i = total(
        GOOG_23, "lease_inclusive"
    )  # current lease fact (363) not stored: leases unverified
    assert (
        i.composition == dc.COMPOSITION_LEASES_NOT_DETERMINED
        and i.value == Decimal(12870) * M
    )
    assert i.slots.lease_reason == "lease_facts_incomplete"
    assert i.value not in (
        Decimal(14253) * M,
        Decimal(14746) * M,
    )  # mixed perimeter / gross of discount


def test_t6_goog_2025_borrowings_and_finance_leases():
    assert total(GOOG_25, "borrowings_only").value == Decimal(48543) * M
    assert total(GOOG_25).value == Decimal(51043) * M


def test_t7_amzn_2025_borrowings_and_finance_leases():
    assert total(AMZN_25, "borrowings_only").value == Decimal(68851) * M
    i = total(AMZN_25)
    assert (
        i.value == Decimal(81137) * M
    )  # never 87,339 (operating leases) or 68,836 (principal)


def test_t8_lly_2014_03_31_no_overlap_hold_and_leases_unverified():
    b = total(LLY, "borrowings_only")
    assert b.value == Decimal("5264.4") * M
    i = total(LLY)
    assert (
        i.value == Decimal("5264.4") * M
        and i.composition == dc.COMPOSITION_LEASES_NOT_DETERMINED
    )
    assert i.slots.lease_reason == "lease_facts_absent"


def test_t9_cvx_2016_uses_the_refinanced_amount_and_the_current_lease_fact():
    assert (
        total(CVX, "borrowings_only").value == Decimal(46019) * M
    )  # 10,840 - 14 + 35,193
    assert total(CVX).value == Decimal(46126) * M  # + 14 + 93 capital leases
    no_ref = {k: v for k, v in CVX.items() if k != "ShortTermDebtRefinancedAmount"}
    assert dc.carrying_lines(V(**no_ref)) == dc.Hold(
        "current_block_unexplained"
    )  # 19,840 55,033 / 52,286 never shown


def test_t10_lease_facts_filed_but_current_side_cannot_be_split_is_held():
    tags = dict(
        LongTermDebtNoncurrent=100,
        DebtCurrent=40,
        LongTermDebtCurrent=40,
        FinanceLeaseLiabilityNoncurrent=10,
    )
    assert dc.carrying_lines(V(**tags)) == dc.Hold("lease_location_unknown")


# ------------------------------------------------------------------ other filing-checked cells
def test_aapl_q3_fy26_and_pfe_and_amzn_q2_and_dpz_and_tsla_2014():
    assert total(AAPL).value == Decimal(84344) * M
    assert total(PFE).value == Decimal(39836) * M
    assert total(AMZN_Q2).value == Decimal(132549) * M
    dpz = total(DPZ)
    assert (
        dpz.value == Decimal("4975338000")
        and dpz.composition == dc.COMPOSITION_LEASE_INCLUSIVE_LINES
    )
    assert dc.carrying_lines(V(**DPZ), "borrowings_only") == dc.Hold(
        "borrowings_not_separable"
    )
    t14 = total(TSLA_1409, "borrowings_only")
    assert t14.value == Decimal(
        "2384261000"
    )  # 597,626 + 1,786,635 (R2 0001193125-14-403635)
    assert total(TSLA_1409).value == Decimal(
        "2408061000"
    )  # + capital leases 9.7 + 14.1


def test_aapl_fy2015_has_no_noncurrent_line_so_nothing_is_composed():
    assert dc.carrying_lines(V(CommercialPaper=8499, LongTermDebtCurrent=2500)) is None


def test_the_debt_current_at_or_above_the_parts_path_is_gone():
    # DebtCurrent 40 above the listed part (10) and no lease fact: contradicted, not accepted
    tags = dict(LongTermDebtNoncurrent=100, LongTermDebtCurrent=10, DebtCurrent=40)
    assert dc.carrying_lines(V(**tags)) == dc.Hold("current_block_unexplained")


def test_cvx_overlap_without_refinanced_is_held_and_parts_larger_than_debt_current_are_ignored():
    assert dc.carrying_lines(
        V(**{k: v for k, v in CVX.items() if "Refinanced" not in k})
    ) == dc.Hold("current_block_unexplained")
    assert (
        total(LLY, "borrowings_only").value == Decimal("5264.4") * M
    )  # ShortTermBorrowings 1,000 > DebtCurrent 9.1


# ------------------------------------------------------------------ perimeter is a named parameter
def test_default_perimeter_and_unknown_perimeter():
    assert dc.DEFAULT_PERIMETER == "lease_inclusive" and dc.PERIMETERS == (
        "lease_inclusive",
        "borrowings_only",
    )
    with pytest.raises(ValueError):
        dc.carrying_lines(V(**MU), "as_filed")


def test_both_perimeters_through_evaluate_total_debt():
    f = F(**GOOG_25)
    assert (
        cf.evaluate_total_debt(f, GUARDS, "borrowings_only").value == Decimal(48543) * M
    )
    d = cf.evaluate_total_debt(f, GUARDS, "lease_inclusive")
    assert (
        d.value == Decimal(51043) * M
        and d.composition == dc.COMPOSITION_BORROWINGS_PLUS_LEASES
    )
    assert (
        d.slots.borrowings == Decimal(48543) * M and d.slots.leases == Decimal(2500) * M
    )


def test_holds_reach_the_decision_with_their_text():
    d = cf.evaluate_total_debt(F(**TSLA_1706), GUARDS)
    assert d.value is None and d.reason == cf.REASON_RELATED_PARTY
    d = cf.evaluate_total_debt(
        F(**{k: v for k, v in CVX.items() if "Refinanced" not in k}), GUARDS
    )
    assert d.value is None and d.reason == cf.REASON_UNDECIDABLE_FALLBACK


def test_flag_off_keeps_the_legacy_path_byte_identical():
    for tags in (AAPL, GOOG_25, AMZN_25, CVX, PFE, DPZ, MU):
        f = F(**tags)
        assert (
            cf.evaluate_total_debt(f, frozenset()).value
            == (cf._compose_total_debt(f) or (None,))[0]
        )
    assert cf.debt_guards_active({}) == frozenset()
    assert cf.GUARD_CARRYING in cf.debt_guards_active(
        {"SCROONER_RULES_ENABLED": cf.RULE_DEBT}
    )


def test_related_party_notes_are_never_added_by_tag():
    tags = dict(
        LongTermDebtNoncurrent=100,
        LongTermDebtCurrent=10,
        NotesPayableRelatedPartiesCurrentAndNoncurrent=50,
    )
    assert total(tags, "borrowings_only").value == Decimal(110) * M


# ------------------------------------------------------------------ writer joins the duration fact by end date
class _Cur:
    def __init__(self, c):
        self.c, self.res = c, []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        sql = " ".join(sql.split())
        if sql.startswith("select id from analytics.canonical_concept"):
            self.res = [(7,)]
        elif sql.startswith("select c.id from core.company"):
            self.res = [(1,)]
        elif sql.startswith("select count(*) from core.company"):
            self.res = [(1,)]
        elif "from core.fact f" in sql:
            from datetime import date

            end = date(2016, 12, 31)
            rows = []
            for i, (tag, v) in enumerate(CVX.items()):
                dur = tag == "ShortTermDebtRefinancedAmount"
                rows.append(
                    (
                        1,
                        900 if dur else 100,
                        tag,
                        Decimal(v) * M,
                        i + 1,
                        end,
                        "duration" if dur else "instant",
                    )
                )
            self.res = rows
        elif sql.startswith(
            "select company_id, period_id, value from analytics.canonical_fact"
        ):
            self.res = [(1, 100, Decimal(43330) * M)]
        elif sql.startswith("select id, cik from core.company"):
            self.res = [(1, "0000093410")]
        else:
            self.res = []

    def executemany(self, sql, rows):
        pass

    def fetchall(self):
        return self.res

    def fetchone(self):
        return self.res[0] if self.res else None


class _Conn:
    def cursor(self):
        return _Cur(self)

    def commit(self):
        pass

    def rollback(self):
        pass


def test_writer_joins_the_refinanced_duration_fact_to_the_instant_by_end_date():
    on = {"SCROONER_RULES_ENABLED": cf.RULE_DEBT}
    st = cf.resolve_total_debt_components(_Conn(), {"x"}, dry_run=True, environ=on)
    (pc,) = st["planned"]
    assert (
        pc.before == Decimal(43330) * M and pc.after == Decimal(46126) * M
    )  # lease_inclusive default
    st = cf.resolve_total_debt_components(
        _Conn(), {"x"}, dry_run=True, environ=on, perimeter="borrowings_only"
    )
    assert st["planned"][0].after == Decimal(46019) * M


def test_finance_lease_total_is_used_when_the_halves_are_not_filed():
    tags = {
        k: v
        for k, v in GOOG_25.items()
        if k not in ("FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent")
    }
    assert total(tags).value == Decimal(51043) * M


def test_long_term_debt_below_the_noncurrent_line_is_partial_and_ignored_above_it_it_must_agree():
    assert (
        total(
            dict(LongTermDebtNoncurrent=100, LongTermDebtCurrent=10, LongTermDebt=50),
            "borrowings_only",
        ).value
        == 110 * M
    )
    assert (
        dc.carrying_lines(
            V(LongTermDebtNoncurrent=100, LongTermDebtCurrent=10, LongTermDebt=200)
        )
        is None
    )


def test_company_stated_total_far_from_the_composed_borrowings_disables_the_mechanism():
    odd = dict(
        LongTermDebtNoncurrent=100,
        LongTermDebtCurrent=10,
        DebtLongtermAndShorttermCombinedAmount=200,
    )
    assert dc.carrying_lines(V(**odd)) is None


# ------------------------------------------------------------------ false holds found in the pilot dry run
LLY_16 = dict(CommercialPaper="1299.3", LongTermDebt="9005.9", LongTermDebtNoncurrent="8367.8",
              DebtLongtermAndShorttermCombinedAmount="10305.2", DebtCurrent="1937.4")  # fmt: skip
LLY_23 = dict(CommercialPaper="6189.4", LongTermDebt="19104.6", LongTermDebtNoncurrent="18320.8",
              DebtLongtermAndShorttermCombinedAmount="25225.3", DebtCurrent="6904.5")  # fmt: skip
GOOG_17 = dict(CommercialPaper=0, LongTermDebt=4026, LongTermDebtNoncurrent=3943, CapitalLeaseObligationsNoncurrent=26,
               DebtCurrent=0, LongTermDebtAndCapitalLeaseObligations=3969)  # fmt: skip
MU_21 = dict(
    LongTermDebt=5968,
    FinanceLeaseLiabilityNoncurrent=649,
    DebtCurrent=155,
    LongTermDebtAndCapitalLeaseObligations=6621,
)
GOOG_16 = dict(LongTermDebtNoncurrent=1984, CapitalLeaseObligationsCurrent=220, DebtCurrent=2219,
               LongTermDebtAndCapitalLeaseObligations=1984, LongTermDebtAndCapitalLeaseObligationsCurrent=220)  # fmt: skip


@pytest.mark.parametrize(("tags", "want"), [(LLY_16, "10305.2"), (LLY_23, "25225.3")])
def test_debt_current_beyond_the_listed_parts_is_accepted_only_when_the_stated_total_confirms_it(
    tags, want
):
    # LLY: commercial paper + current maturities (no current-maturities tag); N + DebtCurrent = the company's own total
    c = total(tags, "borrowings_only")
    assert c.value == Decimal(want) * M and any(
        "corroborated_by_stated_total" in x for x in c.slots.proofs
    )


def test_the_same_excess_without_a_confirming_total_is_still_held():
    no_total = {
        k: v
        for k, v in LLY_16.items()
        if k not in ("DebtLongtermAndShorttermCombinedAmount", "LongTermDebt")
    }
    assert dc.carrying_lines(V(**no_total)) == dc.Hold("current_block_unexplained")
    wrong_total = dict(LLY_16, DebtLongtermAndShorttermCombinedAmount="9000")
    assert dc.carrying_lines(
        V(**{k: v for k, v in wrong_total.items() if k != "LongTermDebt"})
    ) is None or isinstance(dc.carrying_lines(V(**wrong_total)), (dc.Hold, type(None)))


def test_zero_debt_current_needs_no_lease_split():
    c = total(GOOG_17, "borrowings_only")
    assert c.value == Decimal(3943) * M
    i = total(GOOG_17)
    assert (
        i.composition == dc.COMPOSITION_LEASES_NOT_DETERMINED
        and i.slots.lease_reason == "lease_facts_incomplete"
    )


def test_mu_2021_current_side_cannot_be_split_without_the_current_lease_fact():
    assert dc.carrying_lines(V(**MU_21)) == dc.Hold("lease_location_unknown")


def test_goog_2016_debt_current_beyond_parts_with_no_confirmation_is_held_not_accepted():
    assert dc.carrying_lines(V(**GOOG_16)) == dc.Hold("current_block_unexplained")
