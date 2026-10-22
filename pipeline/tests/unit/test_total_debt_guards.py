"""Eligible total_debt guards (2026-10-21, data-team/31 section B): R1
containment, R5 zero / floor guards, R4 single-component preference.

Every fixture is a real company-instant from the stored core.fact (values in
$M, taken from the Tag Mapper's top-1000 all-periods read of 2026-10-21;
DATA-INFERRED from our tables, not re-opened in the filings). Where the new
value is NOT claimed to be right (only 'not the old wrong one') the test says
so."""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from scrooner_pipeline.common.cell_blank_reason import InMemoryBlankReasonStore
from scrooner_pipeline.mapper.concept_fallback import (
    ALL_DEBT_GUARDS,
    GUARD_CONTAINMENT,
    GUARD_FLOOR,
    GUARD_PARTIAL,
    GUARD_ZERO,
    REASON_UNDECIDABLE_FLOOR,
    REASON_UNDECIDABLE_ZERO,
    TOTAL_DEBT_LOAD_TAGS,
    compute_total_debt,
    debt_preference_is_applicable,
    evaluate_total_debt,
    resolve_total_debt_components,
)
from scrooner_pipeline.sanity.tag_investigator import resolve_company_tag_preferences


@pytest.fixture(autouse=True)
def _guards_enabled(monkeypatch):
    """The guards ship behind the rules_enabled flag (default OFF); these tests exercise them ON.
    Flag-OFF identity is covered in test_total_debt_flag_and_reasons.py."""
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "debt.total_debt_consistency@1")


def _d(**tags):
    return {t: (Decimal(str(v)), i) for i, (t, v) in enumerate(tags.items(), 1)}


NO_GUARDS = frozenset()


def _without(guard):
    return ALL_DEBT_GUARDS - {guard}


@pytest.mark.unit
class TestR1Containment:
    def test_mar_bare_long_term_debt_below_noncurrent_does_not_outrank_face(self):
        # MAR 2022-12-31: LongTermDebt 92 beside LongTermDebtAndCapitalLeaseObligations
        # 9,380 (stored 92). L < half of it, so L is rejected; the existing
        # incl-current lease tag is used instead.
        facts = _d(
            LongTermDebt=92,
            LongTermDebtAndCapitalLeaseObligations=9380,
            LongTermDebtAndCapitalLeaseObligationsCurrent=684,
            DebtAndCapitalLeaseObligations=10064,
        )
        old = evaluate_total_debt(facts, _without(GUARD_CONTAINMENT))
        new = evaluate_total_debt(facts)
        assert old.value == Decimal("92")
        assert new.value == Decimal("10064")
        assert new.guards_fired == (GUARD_CONTAINMENT,)

    def test_csgp_bare_below_noncurrent(self):
        # CSGP 2025-12-31: LongTermDebt 140 vs LongTermDebtNoncurrent 993.
        facts = _d(LongTermDebt=140, LongTermDebtNoncurrent=993)
        assert evaluate_total_debt(facts, _without(GUARD_CONTAINMENT)).value == 140
        assert evaluate_total_debt(facts).value == Decimal("993")

    def test_algm_bare_below_noncurrent_plus_current(self):
        # ALGM 2025-12-26: L 280.659 < N 286.158. New value = N + C.
        facts = _d(
            LongTermDebt="280.659",
            LongTermDebtCurrent="1.556",
            LongTermDebtNoncurrent="286.158",
        )
        decision = evaluate_total_debt(facts)
        assert decision.value == Decimal("287.714")
        assert decision.path == "noncurrent+current+short_term"

    def test_wtrg_secured_subset_tagged_as_long_term_debt(self):
        # WTRG 2020-12-31: LongTermDebt 3,014.28 (secured subset) < N 5,507.744.
        facts = _d(
            LongTermDebt="3014.28",
            LongTermDebtCurrent="84.353",
            LongTermDebtNoncurrent="5507.744",
        )
        assert evaluate_total_debt(facts).value == Decimal("5592.097")

    def test_tsco_rejected_bare_tag_and_no_value_leaves_blank_not_a_guess(self):
        # TSCO 2018-06-30: L 150 < N 516.41; the fallback path then holds
        # 516.41, which is below UnsecuredDebt 543 by 5%: blank.
        facts = _d(
            LongTermDebt=150,
            LongTermDebtNoncurrent="516.41",
            UnsecuredDebtCurrent=25,
            UnsecuredDebt=543,
        )
        decision = evaluate_total_debt(facts)
        assert decision.value is None
        assert decision.reason == REASON_UNDECIDABLE_FLOOR
        assert decision.guards_fired == (GUARD_CONTAINMENT, GUARD_FLOOR)

    def test_valid_long_term_debt_is_untouched(self):
        # PLD-shaped: a lone LongTermDebt total, and Cheniere-shaped L == N.
        assert compute_total_debt(_d(LongTermDebt=35037))[0] == Decimal("35037")
        facts = _d(
            LongTermDebt=22632,
            LongTermDebtNoncurrent=22632,
            LongTermDebtCurrent=1411,
            DebtCurrent=1411,
        )
        decision = evaluate_total_debt(facts)
        assert decision.value == Decimal("24043")
        assert decision.guards_fired == ()

    def test_l_equal_to_n_plus_c_with_lease_tag_passes(self):
        # JNJ/CSCO shape: L contains the current portion. Lease tag below 2x L.
        facts = _d(
            LongTermDebt=41438,
            LongTermDebtNoncurrent=36000,
            LongTermDebtCurrent=5438,
            LongTermDebtAndCapitalLeaseObligations=36500,
        )
        assert evaluate_total_debt(facts).guards_fired == ()

    def test_exactly_half_of_lease_tag_passes_just_below_fails(self):
        base = {"LongTermDebtAndCapitalLeaseObligations": 1000}
        ok = evaluate_total_debt(_d(LongTermDebt=500, **base))
        bad = evaluate_total_debt(_d(LongTermDebt=499, **base))
        assert ok.guards_fired == ()
        assert GUARD_CONTAINMENT in bad.guards_fired

    def test_rejected_bare_tag_is_never_the_value(self):
        # L 10 < C 50: L is removed; the existing split path would publish the
        # current part only (path 4), never L. With r7 (partial component) the
        # current-only composition is blanked instead; without r7 it is as before.
        facts = _d(LongTermDebt=10, LongTermDebtCurrent=50)
        decision = evaluate_total_debt(facts, _without(GUARD_PARTIAL))
        assert decision.value == Decimal("50")
        assert decision.guards_fired == (GUARD_CONTAINMENT,)
        assert evaluate_total_debt(facts).value is None


@pytest.mark.unit
class TestR5Zero:
    def test_now_zero_current_ltd_does_not_select_path(self):
        # NOW 2022-06-30: LongTermDebtCurrent 0 selected the split path (sum
        # 0, stored 0) although ConvertibleLongTermNotesPayable is 1,485M.
        facts = _d(LongTermDebtCurrent=0, ConvertibleLongTermNotesPayable=1485)
        old = evaluate_total_debt(facts, NO_GUARDS)
        new = evaluate_total_debt(facts)
        assert old.value == 0
        assert new.value == Decimal("1485")
        assert new.path == "convertible_notes_fallback"
        assert new.guards_fired == (GUARD_ZERO,)

    def test_ddog_zero_plus_instrument_only_is_blank_with_reason(self):
        # DDOG 2024-09-30: ConvertibleLongTermNotesPayable 0 and
        # ConvertibleNotesPayableCurrent 744.858M. The instrument tag is NOT
        # summed (R3 is proposal-only): blank, not 0, not a fill.
        facts = _d(
            ConvertibleLongTermNotesPayable=0,
            ConvertibleNotesPayableCurrent="744.858",
        )
        old = evaluate_total_debt(facts, NO_GUARDS)
        new = evaluate_total_debt(facts)
        assert old.value == 0
        assert new.value is None
        assert new.reason == REASON_UNDECIDABLE_ZERO
        assert new.guards_fired == (GUARD_ZERO,)

    def test_crm_zero_with_secured_and_convertible_instruments(self):
        # CRM 2017-10-31.
        facts = _d(
            LineOfCredit=0,
            LongTermLineOfCredit=0,
            SecuredLongTermDebt="198.471",
            ConvertibleNotesPayableCurrent="1137.954",
            ConvertibleLongTermNotesPayable=0,
        )
        assert evaluate_total_debt(facts, NO_GUARDS).value == 0
        assert evaluate_total_debt(facts).value is None

    def test_ilmn_zero_current_tags_with_nonzero_instruments(self):
        # ILMN 2022-01-02.
        facts = _d(
            LongTermDebtCurrent=0,
            LongTermNotesPayable=993,
            OtherLongTermDebtNoncurrent=993,
            NotesPayableCurrent=0,
            ConvertibleDebtNoncurrent=702,
        )
        assert evaluate_total_debt(facts, NO_GUARDS).value == 0
        assert evaluate_total_debt(facts).value is None

    def test_adi_zero_debt_current_beside_unsecured_long_term_debt(self):
        # ADI 2016-07-30: DebtCurrent 0, UnsecuredLongTermDebt 1,731.758M.
        facts = _d(DebtCurrent=0, UnsecuredLongTermDebt="1731.758")
        assert evaluate_total_debt(facts, NO_GUARDS).value == 0
        assert evaluate_total_debt(facts).value is None

    def test_zero_role_tag_loses_to_a_nonzero_role_path(self):
        # LongTermDebt 0 selected the incl path (sum 0) although the company
        # also filed a nonzero lease-combined incl-current tag (ARMK shape).
        facts = _d(
            LongTermDebt=0,
            LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities=6682,
        )
        decision = evaluate_total_debt(facts, frozenset({GUARD_ZERO}))
        assert decision.value == Decimal("6682")
        assert decision.guards_fired == (GUARD_ZERO,)

    def test_genuine_zero_stays_zero(self):
        # No nonzero debt tag anywhere: a real zero is published.
        facts = _d(LongTermDebt=0, ShortTermBorrowings=0, NotesPayable=0)
        decision = evaluate_total_debt(facts)
        assert decision.value == 0
        assert decision.guards_fired == ()

    def test_carrying_amount_alone_does_not_block_a_real_zero(self):
        facts = _d(LongTermDebt=0, DebtInstrumentCarryingAmount=500)
        assert evaluate_total_debt(facts).value == 0


@pytest.mark.unit
class TestR5Floor:
    def test_ewbc_total_is_only_the_lease_tag_while_fhlb_is_3000(self):
        # EWBC 2025-12-31: stored 35.645M, FHLB advances 3,000M.
        facts = _d(
            AdvancesFromFederalHomeLoanBanks=3000,
            LongTermDebtAndCapitalLeaseObligations="35.645",
        )
        old = evaluate_total_debt(facts, _without(GUARD_FLOOR))
        new = evaluate_total_debt(facts)
        assert old.value == Decimal("35.645")
        assert new.value is None and new.reason == REASON_UNDECIDABLE_FLOOR

    def test_teva_total_below_senior_notes(self):
        # TEVA 2020-09-30: DebtCurrent path 2,106 vs SeniorNotes 25,078.
        facts = _d(
            LongTermDebtCurrent=1474,
            DebtCurrent=2106,
            SeniorNotes=25078,
            LongTermNotesAndLoans=23515,
        )
        assert evaluate_total_debt(facts, _without(GUARD_FLOOR)).value == 2106
        assert evaluate_total_debt(facts).value is None

    def test_phm_bare_long_term_debt_below_notes_payable(self):
        # PHM 2022-12-31: stored 77.3 vs NotesPayable 2,045.527 / SeniorNotes 1,990.3.
        facts = _d(
            LongTermDebt="77.3",
            NotesPayable="2045.527",
            SeniorNotes="1990.299",
            OtherNotesPayable="55.228",
        )
        assert evaluate_total_debt(facts).value is None

    def test_smci_own_total_below_convertible_notes(self):
        # SMCI 2025-06-30: DebtLongtermAndShorttermCombinedAmount 112.475 vs
        # ConvertibleLongTermNotesPayable 4,645.178.
        facts = _d(
            DebtLongtermAndShorttermCombinedAmount="112.475",
            ConvertibleLongTermNotesPayable="4645.178",
        )
        assert evaluate_total_debt(facts, _without(GUARD_FLOOR)).value == Decimal(
            "112.475"
        )
        assert evaluate_total_debt(facts).value is None

    def test_wmt_all_in_total_just_over_two_percent_below_unsecured_debt(self):
        # WMT 2024-01-31: 39,579 vs UnsecuredDebt 40,405 (2.04%). The
        # company's own total is blanked under the stated 2% rule.
        facts = _d(
            DebtLongtermAndShorttermCombinedAmount=39579,
            LongTermDebt=39579,
            UnsecuredDebt=40405,
        )
        assert evaluate_total_debt(facts).value is None

    def test_two_percent_boundary(self):
        # part 1000: total 980 is exactly 2% below (kept), 979 is not.
        keep = evaluate_total_debt(
            _d(DebtLongtermAndShorttermCombinedAmount=980, SeniorNotes=1000)
        )
        drop = evaluate_total_debt(
            _d(DebtLongtermAndShorttermCombinedAmount=979, SeniorNotes=1000)
        )
        assert keep.value == Decimal("980")
        assert drop.value is None

    def test_total_equal_or_above_instrument_tags_unchanged(self):
        # CDNL-like: instrument tag smaller than the total is nested, fine.
        facts = _d(LongTermDebt=22632, NotesPayable=5000, SeniorNotes=8000)
        decision = evaluate_total_debt(facts)
        assert decision.value == Decimal("22632")
        assert decision.guards_fired == ()

    def test_negative_instrument_tag_is_ignored(self):
        facts = _d(LongTermDebt=100, NotesPayable=-500)
        assert evaluate_total_debt(facts).value == 100

    def test_convertible_fallback_equal_to_its_own_instrument_is_kept(self):
        facts = _d(ConvertibleLongTermNotesPayable=1549)
        assert evaluate_total_debt(facts).value == Decimal("1549")


@pytest.mark.unit
class TestEvaluateContract:
    def test_compute_total_debt_wrapper_returns_none_when_blocked(self):
        facts = _d(
            AdvancesFromFederalHomeLoanBanks=3000,
            LongTermDebtAndCapitalLeaseObligations=36,
        )
        assert compute_total_debt(facts) is None

    def test_extra_instrument_tags_never_enter_a_path_sum(self):
        facts = _d(LongTermDebt=1000, NotesPayable=400, LineOfCredit=100)
        value, ids, _path = compute_total_debt(facts)
        assert value == Decimal("1000")
        assert ids == [1]

    def test_loader_requests_instrument_tags(self):
        assert "NotesPayable" in TOTAL_DEBT_LOAD_TAGS
        assert "LongTermDebt" in TOTAL_DEBT_LOAD_TAGS
        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.side_effect = [(1,), (2,), (1,)]
        cur.fetchall.side_effect = [[(7,)], [], []]
        resolve_total_debt_components(
            conn, {"0000000001"}, reason_store=InMemoryBlankReasonStore()
        )
        fact_query = next(
            c for c in cur.execute.call_args_list if "from core.fact f" in c.args[0]
        )
        assert "NotesPayable" in fact_query.args[1][1]
        assert "LongTermDebt" in fact_query.args[1][1]

    def test_negative_total_is_not_blocked_by_a_negative_instrument_tag(self):
        facts = _d(LongTermDebt=-600, NotesPayable=-500)
        assert evaluate_total_debt(facts).value == Decimal("-600")


@pytest.mark.unit
class TestR4Preference:
    def test_only_total_tags_are_applicable(self):
        assert not debt_preference_is_applicable(
            "us-gaap", "ShortTermBorrowings"
        )  # WFC, LITE
        assert not debt_preference_is_applicable(
            "us-gaap", "OtherLongTermDebtNoncurrent"
        )  # DTE
        assert not debt_preference_is_applicable("us-gaap", "LongTermDebt")  # TAP
        assert not debt_preference_is_applicable("us-gaap", "DebtCurrent")
        assert not debt_preference_is_applicable("us-gaap", "SecuredDebtCurrent")
        assert debt_preference_is_applicable(
            "us-gaap", "DebtLongtermAndShorttermCombinedAmount"
        )
        assert not debt_preference_is_applicable(
            "custom", "DebtAndCapitalLeaseObligations"
        )

    def test_resolver_skip_query_only_skips_total_tag_preferences(self):
        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.side_effect = [(1,), (2,), (10,)]
        cur.fetchall.return_value = []
        resolve_total_debt_components(
            conn, {"0000000001"}, reason_store=InMemoryBlankReasonStore()
        )
        sql, params = next(
            (c.args[0], c.args[1])
            for c in cur.execute.call_args_list
            if "company_tag_preference" in c.args[0]
        )
        assert "p.tag = any(%s)" in sql
        assert "DebtLongtermAndShorttermCombinedAmount" in params[2]
        assert "ShortTermBorrowings" not in params[2]

    def test_investigator_does_not_apply_single_component_total_debt_preference(self):
        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.side_effect = [(5,), (6,)]
        # WFC (ShortTermBorrowings) is not applied; a total-tag row would be.
        cur.fetchall.return_value = [
            (101, "us-gaap", "ShortTermBorrowings"),
            (102, "us-gaap", "DebtLongtermAndShorttermCombinedAmount"),
        ]
        cur.fetchone.side_effect = [(5,), (6,), (0,)]
        resolve_company_tag_preferences(conn, "total_debt", "total_debt_resolved")
        deletes = [
            c.args[1]
            for c in cur.execute.call_args_list
            if c.args[0].lstrip().startswith("delete from analytics.canonical_fact")
        ]
        assert deletes[0]["preferred_ids"] == [102]
