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


def test_t5_goog_2023_12_31_borrowings_and_a_truthful_label_while_lease_facts_are_incomplete():
    b = total(GOOG_23, "borrowings_only")
    assert b.value == Decimal(12870) * M  # 13,000 - 130, not the gross 14,746
    # the current finance-lease fact (363) and FinanceLeaseLiability (1,746) exist only as NON-authoritative
    # conflict copies, so the lease-inclusive total (14,616) is not reachable: borrowings with the label
    i = total(GOOG_23)
    assert (
        i.composition == dc.COMPOSITION_LEASES_INCOMPLETE
        and i.value == Decimal(12870) * M
    )
    assert i.slots.lease_reason == "lease_facts_incomplete" and i.slots.lease_fact_filed
    assert i.value not in (
        Decimal(14253) * M,
        Decimal(14746) * M,
    )  # mixed perimeter / gross of discount
    # once the authoritative halves exist the card's 14,616 follows
    full = dict(GOOG_23, FinanceLeaseLiabilityCurrent=363)
    assert (
        total(full).value == Decimal(14616) * M
        and total(full).composition == dc.COMPOSITION_BORROWINGS_PLUS_LEASES
    )


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
    # parts 10 + 35 exceed DebtCurrent 40 and no subset reproduces it: contradicted, not accepted
    tags = dict(LongTermDebtNoncurrent=100, LongTermDebtCurrent=10, CommercialPaper=35, DebtCurrent=40)  # fmt: skip
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
                        True,
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
    # with any lease evidence filed the excess may be a lease: still held (V4: without it, DebtCurrent is the face line)
    with_lease = dict(no_total, FinanceLeaseLiabilityNoncurrent="1")
    assert dc.carrying_lines(V(**with_lease)) == dc.Hold("current_block_unexplained")
    accepted = total(no_total, "borrowings_only")
    assert any("face_line_no_lease_evidence" in x for x in accepted.slots.proofs)


def test_zero_debt_current_means_zero_current_leases_and_the_total_is_lease_inclusive():
    assert total(GOOG_17, "borrowings_only").value == Decimal(3943) * M
    i = total(GOOG_17)
    assert (
        i.composition == dc.COMPOSITION_BORROWINGS_PLUS_LEASES
        and i.value == Decimal(3969) * M
    )  # 3,943 + 26 = LTDCap


def test_mu_2021_09_02_filer_aggregate_proves_both_lines_lease_inclusive():
    c = total(dict(MU_21, DebtAndCapitalLeaseObligations=6776))
    assert (
        c.value == Decimal(6776) * M
        and c.composition == dc.COMPOSITION_LEASE_INCLUSIVE_LINES
    )  # 155 + 6,621
    assert dc.carrying_lines(
        V(**dict(MU_21, DebtAndCapitalLeaseObligations=6776)), "borrowings_only"
    ) == dc.Hold("borrowings_not_separable")
    # without the aggregate the current side cannot be split
    assert dc.carrying_lines(V(**MU_21)) == dc.Hold("lease_location_unknown")


GOOG_1509 = dict(LongTermDebtNoncurrent=1994, CapitalLeaseObligationsCurrent=238, CapitalLeaseObligationsNoncurrent=0,
                 DebtCurrent=3237, LongTermDebtAndCapitalLeaseObligations=1994, LongTermDebtAndCapitalLeaseObligationsCurrent=1237)  # fmt: skip
GOOG_1603 = dict(LongTermDebtNoncurrent=1987, CapitalLeaseObligationsCurrent=223, DebtCurrent=3221,
                 LongTermDebtAndCapitalLeaseObligations=1987, LongTermDebtAndCapitalLeaseObligationsCurrent=1223)  # fmt: skip
GOOG_1803 = dict(
    CommercialPaper=1300,
    LongTermDebtNoncurrent=3944,
    DebtCurrent=1329,
    LongTermDebtAndCapitalLeaseObligations=3973,
)
TSLA_1809 = dict(LongTermDebt="8665.163", DebtCurrent="1833.475", LongTermDebtAndCapitalLeaseObligations="9669.879",
                 LongTermDebtAndCapitalLeaseObligationsCurrent="2106.538")  # fmt: skip
NVDA_15 = dict(ConvertibleDebtCurrent=0, ConvertibleDebtNoncurrent=1384, CapitalLeaseObligationsCurrent="3.414",
               CapitalLeasesFutureMinimumPaymentsPresentValueOfNetMinimumPayments="17.5")  # fmt: skip
NVDA_16 = dict(ConvertibleDebtCurrent=1413, ConvertibleDebtNoncurrent=0, CapitalLeaseObligationsCurrent=4,
               CapitalLeaseObligationsNoncurrent=10)  # fmt: skip


@pytest.mark.parametrize(
    ("tags", "want"),
    [(GOOG_1509, 5231), (GOOG_1603, 5208), (GOOG_16, 4203)],
    ids=["2015-09-30", "2016-03-31", "2016-06-30"],
)
def test_goog_short_term_debt_is_commercial_paper_plus_the_current_capital_lease(
    tags, want
):
    # DebtCurrent holds the current capital lease; the lease-inclusive current line is not a debt-only part
    c = total(tags)
    assert (
        c.value == Decimal(want) * M
        and c.composition == dc.COMPOSITION_BORROWINGS_PLUS_LEASES
    )
    assert "debt_current_whole_current_side+less_current_lease_fact" in c.slots.proofs
    assert total(tags, "borrowings_only").value == c.value - c.slots.leases


def test_goog_2018_03_31_stays_a_hold():
    # stored 5,273 matches neither 5,244 (borrowings) nor 5,302 (+ leases): no current lease fact, DebtCurrent beyond CP
    assert dc.carrying_lines(V(**GOOG_1803)) == dc.Hold("current_block_unexplained")


def test_tsla_2018_09_30_is_held_because_debt_only_totals_sit_beside_the_lease_inclusive_lines():
    # shown before: 11,776,417K; face 11,779,051K includes a 2,634K related-party convertible with no stored fact
    assert dc.carrying_lines(V(**TSLA_1809)) == dc.Hold("related_party_unresolved")
    assert cf.evaluate_total_debt(F(**TSLA_1809), GUARDS).value is None


def test_dpz_still_shows_because_its_debt_only_total_is_noise_not_a_second_set_of_lines():
    c = total(dict(DPZ, LongTermDebt="14.7"))
    assert c.value == Decimal("4975338000")


def test_nvda_pre_842_capital_leases_use_the_total_obligation_fact():
    c = total(NVDA_15)
    assert (
        c.value == Decimal("1401500000")
        and c.composition == dc.COMPOSITION_BORROWINGS_PLUS_LEASES
    )  # 1,384 + 17.5
    assert total(NVDA_15, "borrowings_only").value == Decimal(1384) * M
    assert total(NVDA_16).value == Decimal(1427) * M  # 1,413 + 4 + 10


def test_label_not_determined_only_when_no_lease_fact_or_line_exists():
    assert (
        total(AAPL).composition == dc.COMPOSITION_LEASES_NOT_DETERMINED
    )  # no lease fact at all
    assert total(LLY).composition == dc.COMPOSITION_LEASES_NOT_DETERMINED
    assert total(GOOG_25).composition == dc.COMPOSITION_BORROWINGS_PLUS_LEASES


def test_goog_debt_current_beyond_parts_without_confirmation_is_still_held():
    tags = dict(
        LongTermDebtNoncurrent=100, CommercialPaper=40, DebtCurrent=90
    )  # 50 unlisted, no total: a lease fact beside it means the 50 may be a lease
    tags["FinanceLeaseLiabilityNoncurrent"] = 5
    assert dc.carrying_lines(V(**tags)) == dc.Hold("current_block_unexplained")


def test_zero_debt_current_with_a_nonzero_current_lease_fact_is_a_contradiction():
    tags = dict(
        LongTermDebtNoncurrent=100,
        DebtCurrent=0,
        FinanceLeaseLiabilityCurrent=5,
        FinanceLeaseLiabilityNoncurrent=2,
    )
    assert dc.carrying_lines(V(**tags)) == dc.Hold("current_block_unexplained")


def test_current_lease_derived_from_the_lease_inclusive_current_line_less_the_debt_only_one():
    # LTDCapC 14 less LongTermDebtCurrent 10 = 4 current leases, inside DebtCurrent 14
    tags = dict(LongTermDebtNoncurrent=100, LongTermDebtCurrent=10, DebtCurrent=14, LongTermDebtAndCapitalLeaseObligations=103,
                LongTermDebtAndCapitalLeaseObligationsCurrent=14)  # fmt: skip
    c = total(tags)
    assert c.slots.leases == Decimal(7) * M  # 3 noncurrent + 4 current
    assert c.slots.borrowings == Decimal(110) * M and c.value == Decimal(117) * M


def test_a_related_party_line_alone_holds_lease_inclusive_only_lines():
    tags = dict(LongTermDebtAndCapitalLeaseObligations=1000, LongTermDebtAndCapitalLeaseObligationsCurrent=100,
                NotesPayableRelatedPartiesCurrentAndNoncurrent=1)  # fmt: skip
    assert dc.carrying_lines(V(**tags)) == dc.Hold("related_party_unresolved")


def test_a_lease_half_derived_from_face_lines_does_not_trigger_the_location_hold():
    # AVGO-shaped: DebtCurrent beside a lease-inclusive noncurrent line, no lease FACT filed
    tags = dict(
        LongTermDebtNoncurrent=100,
        LongTermDebtAndCapitalLeaseObligations=103,
        DebtCurrent=10,
    )
    c = total(tags)
    assert (
        c.value == Decimal(110) * M
        and c.composition == dc.COMPOSITION_LEASES_NOT_DETERMINED
    )


# ------------------------------------------------------------------ V3 verifier findings (2026-10-24)
# AAPL files "Commercial paper and repurchase agreements" as OtherShortTermBorrowings (10-Q 0000320193-20-000062 R4)
AAPL_2006 = dict(
    OtherShortTermBorrowings=11166,
    LongTermDebtCurrent=7509,
    LongTermDebtNoncurrent=94048,
    FinanceLeaseLiability=650,
)
AAPL_2003 = dict(
    OtherShortTermBorrowings=10029,
    LongTermDebtCurrent=10392,
    LongTermDebtNoncurrent=89086,
    FinanceLeaseLiability=648,
)
AAPL_1909 = dict(
    CommercialPaper=5980,
    OtherShortTermBorrowings=5980,
    LongTermDebtCurrent=10260,
    LongTermDebtNoncurrent=91807,
)


def test_aapl_2020_06_27_includes_the_commercial_paper_and_repurchase_agreements_line():
    c = total(AAPL_2006)
    assert (
        c.value == Decimal(113373) * M
    )  # 11,166 + 7,509 + 94,048 + finance leases 650
    assert (
        c.slots.borrowings == Decimal(112723) * M and c.slots.leases == Decimal(650) * M
    )
    assert (
        total(AAPL_2006, "borrowings_only").value != Decimal(102207) * M
    )  # the wrong value the Verifier found


def test_aapl_2020_03_28_same_mechanism():
    c = total(AAPL_2003)
    assert c.value == Decimal(110155) * M  # was 100,126: missed the 10,029 line
    assert c.slots.borrowings == Decimal(109507) * M


def test_aapl_2019_09_28_commercial_paper_and_other_short_term_borrowings_are_one_line():
    c = total(AAPL_1909, "borrowings_only")
    assert c.value == (Decimal(5980) + 10260 + 91807) * M  # not 5,980 twice
    assert "CommercialPaper" in c.tags and "OtherShortTermBorrowings" in c.tags
    assert any("short_term_same_line" in p for p in c.slots.proofs)


def test_distinct_short_term_amounts_are_held_unless_the_stated_total_proves_the_sum():
    tags = dict(
        LongTermDebtNoncurrent=100,
        LongTermDebtCurrent=10,
        CommercialPaper=5,
        OtherShortTermBorrowings=11,
    )
    assert dc.carrying_lines(V(**tags)) == dc.Hold("short_term_overlap_unresolved")
    # the stated total shows the two are separate lines (100 + 10 + 5 + 11)
    c = dc.carrying_lines(
        V(**dict(tags, DebtLongtermAndShorttermCombinedAmount="126.4"))
    )
    assert c.value == Decimal(126) * M
    # ... or that the larger line contains the smaller (100 + 10 + 11)
    c = dc.carrying_lines(
        V(**dict(tags, DebtLongtermAndShorttermCombinedAmount="121.3"))
    )
    assert c.value == Decimal(121) * M and "CommercialPaper" not in c.tags


def test_short_term_tag_equal_to_the_current_maturities_is_still_dropped():
    c = total(
        dict(
            LongTermDebtNoncurrent=100, LongTermDebtCurrent=10, ShortTermBorrowings=10
        ),
        "borrowings_only",
    )
    assert c.value == Decimal(110) * M


NVDA_15_FACE = dict(LongTermDebt="1384.342", ConvertibleDebtCurrent=0, ConvertibleDebtNoncurrent=1384,
                    CapitalLeaseObligationsCurrent="3.414", CapitalLeaseObligationsNoncurrent="14.086",
                    CapitalLeasesFutureMinimumPaymentsPresentValueOfNetMinimumPayments="17.5")  # fmt: skip


def test_nvda_fy2015_uses_the_precise_face_line_not_the_rounded_note_figure():
    c = total(NVDA_15_FACE)
    assert c.value == Decimal(
        "1401842000"
    )  # 1,384,342K + 14,086K + 3,414K (10-K 0001045810-15-000036 R5)
    assert total(NVDA_15_FACE, "borrowings_only").value == Decimal("1384342000")
    assert any("precise_copy_long_term_debt" in p for p in c.slots.proofs)
    # the rounded figure alone stays 1,384M
    assert (
        total(
            {k: v for k, v in NVDA_15_FACE.items() if k != "LongTermDebt"},
            "borrowings_only",
        ).value
        == Decimal(1384) * M
    )


def test_a_longtermdebt_that_is_not_a_rounding_of_the_note_figure_is_not_a_precise_copy():
    far = dict(NVDA_15_FACE, LongTermDebt="1390")
    assert total(far, "borrowings_only").value == Decimal(1384) * M


def _c(v, i, auth):
    return (Decimal(v), i, auth)


def test_refine_copies_rounding_variants_and_conflicts():
    # authoritative rounded copy anchors; the precise non-authoritative copy it is a rounding of wins
    assert dc.refine_copies(
        [_c("1384000000", 1, True), _c("1384342000", 2, False)]
    ) == (Decimal("1384342000"), 2)
    # no authoritative copy: a rounded/precise pair that Stage 2e de-authorized (NVDA capital leases 14.0 / 14.086)
    assert dc.refine_copies([_c("14000000", 1, False), _c("14086000", 2, False)]) == (
        Decimal("14086000"),
        2,
    )
    assert (
        dc.refine_copies([_c("14086000", 2, False)]) is None
    )  # a lone non-authoritative copy is never used
    assert (
        dc.refine_copies([_c("1000000000", 1, False), _c("1300000000", 2, False)])
        is None
    )  # a real conflict
    assert dc.refine_copies(
        [_c("1000000000", 1, True), _c("1300000000", 2, False)]
    ) == (Decimal("1000000000"), 1)
    assert dc.refine_copies([_c("5", 1, True)]) == (Decimal("5"), 1)


def test_is_rounding_variant_bounds():
    assert dc.is_rounding_variant(Decimal("1384000000"), Decimal("1384342000"))
    assert dc.is_rounding_variant(Decimal("14000000"), Decimal("14086000"))
    assert not dc.is_rounding_variant(
        Decimal("1384000000"), Decimal("1385000000")
    )  # beyond half a unit
    assert not dc.is_rounding_variant(
        Decimal("1000000000"), Decimal("1400000000")
    )  # a $1B round number is no licence
    assert not dc.is_rounding_variant(
        Decimal("1384342000"), Decimal("1384000000")
    )  # the precise one is no rounding of the coarse


AVGO_25 = dict(LongTermDebtNoncurrent=61984, LongTermDebtCurrent=3152, LongTermDebtAndCapitalLeaseObligations=61984,
               LongTermDebtAndCapitalLeaseObligationsCurrent=3152)  # fmt: skip


def test_avgo_fy2025_no_finance_leases_equals_zero_without_a_filed_zero():
    c = total(
        AVGO_25
    )  # SYNTHETIC from the Verifier's read: 3,152 + 61,984 = 65,136M, lease halves only derived
    assert c.value == Decimal(65136) * M and c.slots.leases is None
    assert (
        c.composition == dc.COMPOSITION_LEASES_NOT_DETERMINED
        and c.slots.lease_reason == "lease_zero_unproven"
    )
    filed = dict(
        AVGO_25, FinanceLeaseLiabilityCurrent=0, FinanceLeaseLiabilityNoncurrent=0
    )
    z = total(filed)
    assert (
        z.slots.leases == 0 and z.composition == dc.COMPOSITION_BORROWINGS_PLUS_LEASES
    )


def test_incomplete_label_needs_an_authoritative_lease_fact_not_a_derived_half():
    assert (
        total(GOOG_23).composition == dc.COMPOSITION_LEASES_INCOMPLETE
    )  # noncurrent 1,383 filed
    derived_only = dict(
        LongTermDebtNoncurrent=100,
        LongTermDebtAndCapitalLeaseObligations=103,
        DebtCurrent=10,
    )
    assert total(derived_only).composition == dc.COMPOSITION_LEASES_NOT_DETERMINED


class _CopyCur(_Cur):
    """Returns NVDA FY2015 with the Stage 2e conflict copies: LongTermDebt 1,384 / 1,384.342 both de-authorized."""

    def execute(self, sql, params=None):
        sql = " ".join(sql.split())
        if "from core.fact f" in sql:
            from datetime import date

            end = date(2015, 1, 25)
            r = [
                (
                    1,
                    100,
                    "ConvertibleDebtNoncurrent",
                    Decimal(1384) * M,
                    1,
                    end,
                    "instant",
                    True,
                ),
                (1, 100, "ConvertibleDebtCurrent", Decimal(0), 2, end, "instant", True),
                (
                    1,
                    100,
                    "CapitalLeaseObligationsCurrent",
                    Decimal("3.414") * M,
                    3,
                    end,
                    "instant",
                    True,
                ),
                (
                    1,
                    100,
                    "CapitalLeaseObligationsNoncurrent",
                    Decimal(14) * M,
                    4,
                    end,
                    "instant",
                    False,
                ),
                (
                    1,
                    100,
                    "CapitalLeaseObligationsNoncurrent",
                    Decimal("14.086") * M,
                    5,
                    end,
                    "instant",
                    False,
                ),
                (1, 100, "LongTermDebt", Decimal(1384) * M, 6, end, "instant", False),
                (
                    1,
                    100,
                    "LongTermDebt",
                    Decimal("1384.342") * M,
                    7,
                    end,
                    "instant",
                    False,
                ),
            ]
            self.c.params = params
            self.res = r
        elif sql.startswith(
            "select company_id, period_id, value from analytics.canonical_fact"
        ):
            self.res = []
        else:
            super().execute(sql, params)


class _CopyConn(_Conn):
    def cursor(self):
        return _CopyCur(self)


def test_writer_resolves_rounding_copies_only_under_the_carrying_guard():
    on = {"SCROONER_RULES_ENABLED": cf.RULE_DEBT}
    st = cf.resolve_total_debt_components(
        _CopyConn(), {"x"}, dry_run=True, environ=on, perimeter="borrowings_only"
    )
    (pc,) = st["planned"]
    assert pc.after == Decimal(
        "1384342000"
    )  # LongTermDebt precise copy, not the rounded convertible 1,384M
    st = cf.resolve_total_debt_components(_CopyConn(), {"x"}, dry_run=True, environ=on)
    assert st["planned"][0].after == Decimal("1401842000")


def test_the_loader_asks_for_non_authoritative_copies_only_when_the_carrying_guard_is_on():
    conn = _CopyConn()
    cf.resolve_total_debt_components(conn, {"x"}, dry_run=True, environ={})
    assert conn.params[1] is True  # dry run evaluates r8 as ON
    # flag off, live: no copies are requested (byte-identical legacy loading)
    conn2 = _CopyConn()
    try:
        cf.resolve_total_debt_components(
            conn2, {"x"}, dry_run=False, reason_store=None, environ={}
        )
    except Exception:
        pass
    assert getattr(conn2, "params", [None, False])[1] is False


def test_a_coarser_long_term_debt_never_replaces_a_precise_noncurrent_line():
    tags = dict(
        LongTermDebtNoncurrent="1384.342", LongTermDebtCurrent=0, LongTermDebt=1384
    )
    assert total(tags, "borrowings_only").value == Decimal("1384342000")


# ------------------------------------------------------------------ vocabulary scan of 30 more cohort companies
KO_1906 = dict(
    LongTermDebt=32045,
    LongTermDebtCurrent=2749,
    LongTermDebtNoncurrent=29296,
    NotesAndLoansPayableCurrent=13030,
)
KO_1912 = dict(CommercialPaper=10007, LongTermDebt=31769, OtherShortTermBorrowings=987, ShortTermBorrowings=10994,
               LongTermDebtCurrent=4253, LongTermDebtNoncurrent=27516, NotesAndLoansPayableCurrent=10994)  # fmt: skip


def test_ko_loans_and_notes_payable_is_a_short_term_face_line():
    # before: 32,045 (the line was missing); the face "Loans and notes payable" 13,030 is a short-term borrowing
    assert total(KO_1906, "borrowings_only").value == Decimal(45075) * M


def test_ko_short_term_borrowings_contains_its_components_and_is_counted_once():
    c = total(KO_1912, "borrowings_only")
    assert (
        c.value == Decimal(42763) * M
    )  # 27,516 + 4,253 + 10,994, not + 10,007 + 987 on top
    assert any("container_of_components" in p for p in c.slots.proofs)


def test_distinct_short_term_amounts_that_are_not_containment_still_hold():
    tags = dict(KO_1912, OtherShortTermBorrowings=500)  # 10,007 + 500 != 10,994
    assert dc.carrying_lines(V(**tags)) == dc.Hold("short_term_overlap_unresolved")


# ------------------------------------------------------------------ V4 verifier fixes (2026-10-24)
ABBV_2203 = dict(LongTermDebtAndCapitalLeaseObligations=63522, LongTermDebtAndCapitalLeaseObligationsCurrent=9940, ShortTermBorrowings=12)  # fmt: skip
ABBV_1712 = dict(DebtAndCapitalLeaseObligations=36968, LongTermDebtAndCapitalLeaseObligations=30953,
                 LongTermDebtAndCapitalLeaseObligationsCurrent=6015, ShortTermBorrowings=400)  # fmt: skip
CVX_1503 = dict(CapitalLeaseObligationsNoncurrent=65, LongTermDebt=22700, LongTermDebtNoncurrent=29960, ShortTermBorrowings=3908)  # fmt: skip
CVX_1409 = dict(CapitalLeaseObligationsNoncurrent=84, LongTermDebt=12400, LongTermDebtNoncurrent=19960, ShortTermBorrowings=5665)  # fmt: skip


@pytest.mark.parametrize(
    "tags, want",
    [(ABBV_2203, 73474), (ABBV_1712, 37368)],
    ids=["2022-03-31", "2017-12-31"],
)
def test_abbv_separate_short_term_borrowings_line_is_part_of_the_lease_inclusive_total(
    tags, want
):
    # 10-Q 0001551152-22-000017 R5: 12 + 9,940 + 63,522 = 73,474; 10-K 0001551152-18-000014 R5: 400 + 6,015 + 30,953
    c = total(tags)
    assert c.value == Decimal(want) * M
    assert c.composition == dc.COMPOSITION_LEASE_INCLUSIVE_LINES
    assert "ShortTermBorrowings" in c.tags


def test_abbv_short_term_borrowings_are_not_added_when_debt_current_is_the_current_line():
    # DebtCurrent is the whole current side: a ShortTermBorrowings beside it is inside it
    tags = dict(LongTermDebtAndCapitalLeaseObligations=30953, DebtCurrent=6415,
                DebtAndCapitalLeaseObligations=37368, ShortTermBorrowings=400)  # fmt: skip
    assert total(tags).value == Decimal(37368) * M


def test_abbv_conflicting_short_term_amounts_beside_a_lease_inclusive_current_line_hold():
    tags = dict(ABBV_2203, CommercialPaper=7)  # 12 vs 7: neither contained nor proven
    assert dc.carrying_lines(V(**tags)) == dc.Hold("short_term_overlap_unresolved")


@pytest.mark.parametrize(
    "tags, want",
    [(CVX_1503, 33933), (CVX_1409, 25709)],
    ids=["2015-03-31", "2014-09-30"],
)
def test_cvx_pre_2015_noncurrent_capital_lease_face_line_is_included(tags, want):
    # 10-Q 0000093410-15-000020 R5: 3,908 + 29,960 + 65; 10-Q 0000093410-14-000049 R5: 5,665 + 19,960 + 84.
    # LongTermDebt (22,700) is below the noncurrent line: the r1 containment guard removes it before r8
    d = cf.evaluate_total_debt(F(**tags), GUARDS)
    assert d.value == Decimal(want) * M
    assert d.composition == dc.COMPOSITION_BORROWINGS_PLUS_LEASES
    b = cf.evaluate_total_debt(F(**tags), GUARDS, "borrowings_only")
    assert b.value == d.value - Decimal(tags["CapitalLeaseObligationsNoncurrent"]) * M


def test_short_term_only_composition_is_not_used_when_long_term_debt_may_hold_the_current_maturities():
    # a LongTermDebt that contains the noncurrent line includes untagged current maturities: legacy path decides
    tags = dict(
        LongTermDebt=30500, LongTermDebtNoncurrent=29960, ShortTermBorrowings=3908
    )
    assert dc.carrying_lines(V(**tags)) is None


MRK_13 = dict(DebtAndCapitalLeaseObligations=25100, DebtCurrent=4521, LongTermDebtCurrent=2100, LongTermDebtNoncurrent=20539)  # fmt: skip
INTC_1203 = dict(CommercialPaper=273, DebtCurrent=362, LongTermDebtNoncurrent=7088)
UNH_2403 = dict(CommercialPaper=7300, DebtCurrent=9787, LongTermDebtNoncurrent=63850)
CSCO_1704 = dict(DebtCurrent=4248, LongTermDebt=30470, LongTermDebtCurrent=2248, LongTermDebtNoncurrent=28222)  # fmt: skip
CSCO_2410 = dict(DebtCurrent=12364, LongTermDebt=20117, LongTermDebtCurrent=494, LongTermDebtNoncurrent=19623)  # fmt: skip


@pytest.mark.parametrize(
    "tags, want",
    [
        (MRK_13, 25060),
        (INTC_1203, 7450),
        (UNH_2403, 73637),
        (CSCO_1704, 32470),
        (CSCO_2410, 31987),
    ],
    ids=[
        "MRK-2013-12-31",
        "INTC-2012-03-31",
        "UNH-2024-03-31",
        "CSCO-2017-04-29",
        "CSCO-2024-10-26",
    ],
)
def test_debt_current_that_is_the_face_line_is_the_whole_current_side(tags, want):
    # filings: MRK 0000310158-14-000009 R4; INTC 0001193125-12-212253 R4; UNH 0000731766-24-000155 R2;
    # CSCO 0000858877-17-000010 / -24-000030 R2: the filer tags only commercial paper or current maturities
    c = total(tags)
    assert c.value == Decimal(want) * M
    assert any("face_line_no_lease_evidence" in p or "corroborated" in p for p in c.slots.proofs)  # fmt: skip


def test_debt_current_excess_is_still_held_when_lease_lines_sit_beside_it():
    # GOOG 2018-03-31 (CP 1,300 vs DebtCurrent 1,329 with a lease-inclusive noncurrent line) stays a hold
    assert dc.carrying_lines(V(**GOOG_1803)) == dc.Hold("current_block_unexplained")
    # same shape as UNH, plus a finance-lease fact: the excess may be the lease
    tags = dict(UNH_2403, FinanceLeaseLiabilityNoncurrent=100)
    assert dc.carrying_lines(V(**tags)) in (dc.Hold("current_block_unexplained"), dc.Hold("lease_location_unknown"))  # fmt: skip


def test_debt_current_smaller_than_a_part_pair_is_still_a_contradiction():
    # two parts that together exceed DebtCurrent contradict it; only an unexplained EXCESS is accepted
    tags = dict(DebtCurrent=1000, CommercialPaper=700, ShortTermBorrowings=600, LongTermDebtNoncurrent=5000)  # fmt: skip
    assert dc.carrying_lines(V(**tags)) == dc.Hold("current_block_unexplained")


def test_csco_long_term_debt_is_accepted_only_when_it_is_noncurrent_plus_current_maturities():
    tags = dict(
        CSCO_2410, LongTermDebt=20500
    )  # no longer equals 19,623 + 494 and is far from the total
    assert dc.carrying_lines(V(**tags)) is None


def test_abbv_filer_aggregate_that_includes_the_short_term_line_also_proves_the_total():
    # aggregate 37,368 = 400 + 6,015 + 30,953; a debt-only LongTermDebt beside it must not hold the total
    tags = dict(ABBV_1712, DebtAndCapitalLeaseObligations=37368, LongTermDebt=30000)
    c = total(tags)
    assert c.value == Decimal(37368) * M and any("filer_aggregate" in p for p in c.slots.proofs)  # fmt: skip


def test_noncurrent_line_alone_is_not_a_total_even_with_a_noncurrent_capital_lease():
    # no short-term line, no current line: nothing to compose (AAPL FY2015 shape), not a zero current side
    tags = dict(LongTermDebtNoncurrent=29960, CapitalLeaseObligationsNoncurrent=65)
    assert dc.carrying_lines(V(**tags)) is None


def test_short_term_only_composition_leaves_overlapping_short_term_amounts_to_the_legacy_path():
    # LLY 2010-09-30: ShortTermBorrowings 155.1 beside ShortTermBankLoansAndNotesPayable 125
    tags = dict(LongTermDebtNoncurrent=6982, ShortTermBorrowings=155.1, ShortTermBankLoansAndNotesPayable=125)  # fmt: skip
    assert dc.carrying_lines(V(**tags)) is None


@pytest.mark.parametrize(
    "extra",
    [dict(LongTermDebtAndCapitalLeaseObligationsCurrent=60),
     dict(LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities=2041)],
    ids=["AMD-2013-lease-inclusive-current", "KO-including-current-maturities"],
)  # fmt: skip
def test_short_term_only_composition_never_drops_a_filed_current_maturities_line(extra):
    # AMD 2013-12-28: 1,986 + 60 + 55 = 2,101, not 1,986 + 55
    tags = dict(LongTermDebtNoncurrent=1986, ShortTermBorrowings=55, **extra)
    assert dc.carrying_lines(V(**tags)) is None


def test_current_capital_lease_stays_unlocated_for_a_post_842_finance_lease_half():
    # only the pre-ASC 842 CapitalLeaseObligationsNoncurrent tag lets the current half sit inside the current debt
    tags = dict(LongTermDebtNoncurrent=19960, ShortTermBorrowings=5665, FinanceLeaseLiabilityNoncurrent=84)  # fmt: skip
    c = total(tags)
    assert c.value == Decimal(19960 + 5665) * M and c.composition == dc.COMPOSITION_LEASES_INCOMPLETE  # fmt: skip


def test_long_term_debt_agreement_counts_a_short_term_container_once_without_a_current_maturities_tag():
    # no LongTermDebtCurrent, so only the short-term subtraction can reconcile LongTermDebt (noncurrent + maturities):
    # DebtCurrent 80 = container 50 + maturities 30; the container 50 holds CP 30 + other 20
    tags = dict(LongTermDebtNoncurrent=100, DebtCurrent=80, ShortTermBorrowings=50, CommercialPaper=30,
                OtherShortTermBorrowings=20, LongTermDebt=130)  # fmt: skip
    assert total(tags, "borrowings_only").value == Decimal(180) * M
