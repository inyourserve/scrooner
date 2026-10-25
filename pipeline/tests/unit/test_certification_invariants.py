"""Certification invariant suite (data-team/34 P1): every test is built from a
REAL failure case in doc/data-moat/team/top1000/status.md or the lessons ledger,
starting from a clean fixture and breaking exactly one thing. Each case also
asserts that the repaired fixture is clean (the mutation partner), and each
invariant has a clean-company test."""

from datetime import date
from decimal import Decimal

import pytest
from certification_fixtures import (
    D, QUARTERS, add, clean_company, fact, make_metric, src,
)

from scrooner_pipeline.certification import (
    composition, currency, period_integrity, scale, sector, sign, source_integrity, splits, ties,
)
from scrooner_pipeline.certification.model import REVIEW, WRONG_VALUE, power_of_ten_signature
from scrooner_pipeline.certification.runner import run_checks, served_view


def rules(findings, invariant=None, severity=None):
    return {
        f.evidence["rule"]
        for f in findings
        if (invariant is None or f.invariant == invariant) and (severity is None or f.severity == severity)
    }


def swap_value(data, concept, end, new_value, fp="FY"):
    """Replace one stored cell's value (keeps its source facts)."""
    for i, c in enumerate(data.cells):
        if c.concept == concept and c.end == end and c.fiscal_period == fp and c.days not in (None,) or (
            c.concept == concept and c.end == end and c.period_type == "instant"
        ):
            if c.concept == concept and c.end == end and c.fiscal_period == fp:
                data.cells[i] = type(c)(**{**c.__dict__, "value": D(new_value)})
                return data.cells[i]
    raise AssertionError("cell not found")


# --------------------------------------------------------------- clean company
@pytest.mark.unit
class TestCleanCompany:
    @pytest.mark.parametrize(
        "module",
        [ties, sign, scale, period_integrity, source_integrity, currency, composition, splits, sector],
        ids=lambda m: m.__name__.rsplit(".", 1)[-1],
    )
    def test_each_invariant_module_is_silent_on_a_clean_company(self, module):
        assert module.check(clean_company()) == []

    def test_full_suite_is_silent(self):
        assert run_checks(clean_company()) == []


# ------------------------------------------------------- I4 scale / I6 source
@pytest.mark.unit
class TestMdtNetIncomeScaleAndProxy:
    """MDT net income FY2022 stored as 4,801 dollars (a DEF 14A fact, 64871764)
    instead of 4,801 million: ~1e6x small."""

    def broken(self):
        d = clean_company()
        bad_src = src("NetIncomeLoss", 4801, form="DEF 14A", sid=64871764)
        d.cells[:] = [c for c in d.cells if not (c.concept == "net_income" and c.fiscal_period == "FY")]
        d.cells[:] = [c for c in d.cells if not (c.concept == "revenue" and c.fiscal_period == "FY" and c.end.year == 2023)]
        add(d, "revenue", 32_000_000_000, date(2023, 12, 31), date(2023, 1, 1), "FY")  # MDT sells ~32 billion
        for year in (2022, 2024):  # MDT earns ~4.8 billion a year
            add(d, "net_income", 4_800_000_000, date(year, 12, 31), date(year, 1, 1), "FY")
        add(d, "net_income", 4801, date(2023, 12, 31), date(2023, 1, 1), "FY", sources=[bad_src])
        return d

    def test_scale_error_is_wrong_value(self):
        f = scale.check(self.broken())
        assert "neighbour_magnitude" in rules(f, "I4", WRONG_VALUE)
        assert "cross_concept_scale" in rules(f, "I4", WRONG_VALUE)

    def test_proxy_source_is_wrong_value(self):
        d = self.broken()
        d.periodic_copies[64871764] = [src("NetIncomeLoss", 4_801_000_000, form="10-K", sid=64871765)]
        f = [x for x in source_integrity.check(d) if x.evidence["rule"] == "non_periodic_form"]
        assert f and f[0].severity == WRONG_VALUE and f[0].evidence["differs_from_periodic_copy"] is True
        assert f[0].source_fact_ids == [64871764] and f[0].evidence["form"] == "DEF 14A"

    def test_repaired_fixture_is_clean(self):
        assert run_checks(clean_company()) == []


@pytest.mark.unit
class TestBanrNetIncomeTimes1000:
    def test_thousandfold_high_value(self):
        d = clean_company()
        swap_value(d, "net_income", date(2023, 12, 31), D(120_000_000) * 1000)
        assert "neighbour_magnitude" in rules(scale.check(d), "I4", WRONG_VALUE)

    def test_repaired(self):
        assert "neighbour_magnitude" not in rules(scale.check(clean_company()))


@pytest.mark.unit
class TestSchwBaseNetIncomeThousandfoldSmall:
    """SCHW base net income 8.85M (proxy filed in thousands, stored as dollars)
    next to the resolved layer's 8,417M: the layers disagree ~951x."""

    def test_layer_disagreement_is_wrong_value(self):
        d = clean_company()
        end, start = date(2023, 12, 31), date(2023, 1, 1)
        for c in [c for c in d.cells if c.concept == "net_income" and c.end == end and c.fiscal_period == "FY"]:
            d.cells.remove(c)
        add(d, "net_income", 8_850_000, end, start, "FY")
        add(d, "net_income_resolved", 8_417_000_000, end, start, "FY")
        found = [f for f in scale.check(d) if f.evidence["rule"] == "layer_disagreement"]
        assert found and found[0].severity == WRONG_VALUE and found[0].expected_or_other_value == D(8_417_000_000)

    def test_repaired(self):
        d = clean_company()
        add(d, "net_income_resolved", D(120_000_000), date(2023, 12, 31), date(2023, 1, 1), "FY")
        assert "layer_disagreement" not in rules(scale.check(d))


# ------------------------------------------------------------- I8 composition
@pytest.mark.unit
class TestTotalDebtComposition:
    def debt_company(self, stored, source_tag="ShortTermBorrowings"):
        d = clean_company()
        end, start = date(2024, 12, 31), date(2024, 1, 1)
        add(d, "total_debt_resolved", stored, end, None, "FY", tag=source_tag)
        d.debt_facts += [
            fact("ShortTermBorrowings", 25_200_000_000, None, end),
            fact("LongTermDebt", 207_300_000_000, None, end),
        ]
        return d

    def test_wfc_resolved_equals_short_term_only(self):
        f = [x for x in composition.check(self.debt_company(25_200_000_000)) if x.invariant == "I8"]
        assert f[0].evidence["rule"] == "debt_below_component" and f[0].severity == WRONG_VALUE
        assert f[0].expected_or_other_value == D(207_300_000_000)
        assert f[0].evidence["largest_component_tag"] == "LongTermDebt"

    def test_abbv_zero_with_debt_tags(self):
        f = composition.check(self.debt_company(0))
        assert f[0].evidence["rule"] == "debt_zero_with_components" and f[0].severity == WRONG_VALUE

    def test_repaired_total_is_clean(self):
        assert composition.check(self.debt_company(232_500_000_000, "LongTermDebt")) == []

    def test_double_count_of_overlapping_tags(self):
        d = clean_company()
        cell = add(d, "total_debt", 40, date(2024, 12, 31), None, "FY",
                   sources=[src("LongTermDebt", 30), src("LongTermDebtCurrent", 10)])
        f = composition.check(d)
        assert f and f[0].evidence["rule"] == "debt_double_count" and f[0].data_point_name == cell.concept

    def test_disjoint_tags_are_not_a_double_count(self):
        d = clean_company()
        add(d, "total_debt", 40, date(2024, 12, 31), None, "FY",
            sources=[src("LongTermDebtNoncurrent", 30), src("LongTermDebtCurrent", 10)])
        assert composition.check(d) == []


@pytest.mark.unit
class TestKlacDerivedQ4Eps:
    """KLAC 10-for-1: derived Q4 diluted EPS -22.61, filed 1.04. I8 (EPS by
    subtraction) and I9 (share-basis mix) both fire."""

    def broken(self, q4=D("-22.61")):
        d = clean_company()
        values = [D("0.98"), D("1.02"), D("1.10"), q4]
        for (qs, qe, fp), v in zip(QUARTERS, values):
            add(d, "diluted_eps", v, qe, qs, fp, tag="EarningsPerShareDiluted", unit="usd/shares",
                derived=(fp == "Q4"))
        return d

    def test_subtraction_is_wrong_value(self):
        f = composition.check(self.broken())
        assert any(x.evidence["rule"] == "per_share_derived_by_subtraction" and x.severity == WRONG_VALUE for x in f)

    def test_neighbours_that_average_to_zero_do_not_divide_by_zero(self):
        # CI crashed on certify shards S056/S085 with decimal.DivisionByZero
        d = clean_company()
        values = [D("-0.10"), D("0.10"), D("0"), D("2.00")]
        for (qs, qe, fp), v in zip(QUARTERS, values):
            add(d, "diluted_eps", v, qe, qs, fp, tag="EarningsPerShareDiluted", unit="usd/shares",
                derived=(fp == "Q4"))
        assert splits.check(d) == []

    def test_basis_mix_is_wrong_value(self):
        f = splits.check(self.broken())
        assert f and f[0].evidence["rule"] == "per_share_basis_mix" and f[0].severity == WRONG_VALUE
        assert f[0].evidence["sign_flipped"] is True

    def test_filed_value_is_clean(self):
        d = clean_company()
        for (qs, qe, fp), v in zip(QUARTERS, [D("0.98"), D("1.02"), D("1.10"), D("1.04")]):
            add(d, "diluted_eps", v, qe, qs, fp, tag="EarningsPerShareDiluted", unit="usd/shares")
        assert composition.check(d) == [] and splits.check(d) == []


# ------------------------------------------------------------------ I3 sign
@pytest.mark.unit
class TestSign:
    def test_dis_derived_q4_interest_expense_flipped(self):
        d = clean_company()
        add(d, "interest_expense", -3_200_000_000, date(2024, 12, 31), date(2024, 10, 1), "Q4",
            tag="InterestExpense", derived=True)
        f = sign.check(d)
        assert f[0].severity == WRONG_VALUE and f[0].evidence["derived_source"] is True

    def test_positive_interest_expense_is_clean(self):
        d = clean_company()
        add(d, "interest_expense", 416_000_000, date(2024, 12, 31), date(2024, 10, 1), "Q4", tag="InterestExpense", derived=True)
        assert sign.check(d) == []

    def test_negative_derived_revenue_and_dps(self):
        d = clean_company()
        add(d, "revenue", -50_000_000, date(2023, 12, 31), date(2023, 10, 1), "Q4", tag="Revenues", derived=True)
        add(d, "dividends_per_share", D("-1.18"), date(2024, 12, 31), date(2024, 10, 1), "Q4",
            tag="CommonStockDividendsPerShareDeclared", unit="usd/shares", derived=True)
        got = {f.data_point_name for f in sign.check(d) if f.severity == WRONG_VALUE}
        assert got == {"revenue", "dividends_per_share"}

    def test_filed_negative_is_review_and_value_is_never_changed(self):
        d = clean_company()
        cell = add(d, "revenue", -7, date(2022, 6, 30), date(2022, 4, 1), "Q2", tag="Revenues", form="10-Q")
        f = sign.check(d)
        assert f[0].severity == REVIEW and f[0].stored_value == D(-7) and cell.value == D(-7)

    def test_negative_net_income_is_legitimate(self):
        d = clean_company()
        add(d, "net_income", -5_000_000, date(2022, 6, 30), date(2022, 4, 1), "Q2", tag="NetIncomeLoss", form="10-Q")
        assert sign.check(d) == []


# ------------------------------------------------------------ I5 period / sums
@pytest.mark.unit
class TestPeriodIntegrity:
    def test_amt_one_quarter_far_below_the_others(self):
        """AMT Q2 revenue 211M stored vs 2,749M: the four quarters no longer sum to the year."""
        d = clean_company()
        d.cells[:] = [c for c in d.cells if not (c.concept == "revenue" and c.end.year == 2024)]
        add(d, "revenue", 10_800_000_000, date(2024, 12, 31), date(2024, 1, 1), "FY")
        for (qs, qe, fp), v in zip(QUARTERS, [2_600_000_000, 211_000_000, 2_700_000_000, 2_750_000_000]):
            add(d, "revenue", v, qe, qs, fp, tag="Revenues", form="10-Q")
        f = [x for x in period_integrity.check(d) if x.evidence["rule"] == "quarters_do_not_sum_to_year"]
        assert f and f[0].severity == WRONG_VALUE
        assert f[0].evidence["suspect_quarter_end"] == "2024-06-30"

    def test_ge_quarter_equal_to_longer_window(self):
        """A discrete quarter holding the 6-month figure (label shift)."""
        d = clean_company()
        add(d, "revenue", 552_000_000, date(2024, 6, 30), date(2024, 1, 1), None, tag="Revenues", form="10-Q")
        for c in [c for c in d.cells if c.concept == "revenue" and c.fiscal_period == "Q2"]:
            d.cells.remove(c)
        add(d, "revenue", 552_000_000, date(2024, 6, 30), date(2024, 4, 1), "Q2", tag="Revenues", form="10-Q")
        assert "quarter_equals_longer_window" in rules(period_integrity.check(d), "I5", WRONG_VALUE)

    def test_full_year_value_under_quarter_label(self):
        d = clean_company()
        add(d, "gross_profit", 400_000_000, date(2024, 12, 31), date(2024, 1, 1), "Q4", tag="GrossProfit")
        assert "quarter_label_on_long_period" in rules(period_integrity.check(d), "I5", WRONG_VALUE)

    def test_quarter_value_under_year_label(self):
        d = clean_company()
        add(d, "gross_profit", 100_000_000, date(2024, 12, 31), date(2024, 10, 1), "FY", tag="GrossProfit")
        assert "year_label_on_quarter_period" in rules(period_integrity.check(d), "I5", WRONG_VALUE)

    def test_52_53_week_year_and_14_week_quarter_are_clean(self):
        d = clean_company()
        add(d, "capex", 5_000_000, date(2023, 9, 30), date(2022, 10, 2), "FY", tag="PaymentsToAcquirePropertyPlantAndEquipment")  # 363 days
        add(d, "capex", 1_100_000, date(2023, 1, 1), date(2022, 10, 2), "Q1", tag="PaymentsToAcquirePropertyPlantAndEquipment", form="10-Q")  # 91
        add(d, "capex", 1_300_000, date(2023, 4, 8), date(2023, 1, 2), "Q2", tag="PaymentsToAcquirePropertyPlantAndEquipment", form="10-Q")  # 96
        assert not rules(period_integrity.check(d), "I5", WRONG_VALUE)


# ---------------------------------------------------------------- I7 currency
@pytest.mark.unit
class TestCurrency:
    def test_cme_share_count_from_2010_inside_market_cap(self):
        d = clean_company()
        old = src("CommonStockSharesOutstanding", 66_600_000, unit="shares", end=date(2010, 12, 31), sid=7001)
        d.sources[old.id] = old
        d.metrics.append(make_metric("market_cap", 105_900_000_000, end=date(2026, 10, 20), requires_price=True, source_ids=[7001]))
        d.latest_filed = date(2026, 6, 30)
        f = [x for x in currency.check(d) if x.evidence["rule"] == "stale_metric_input"]
        assert f and f[0].severity == WRONG_VALUE and f[0].evidence["input_age_days"] > 456

    def test_fresh_shares_are_clean(self):
        d = clean_company()
        new = src("CommonStockSharesOutstanding", 359_600_000, unit="shares", end=date(2026, 6, 30), sid=7002)
        d.sources[new.id] = new
        d.metrics.append(make_metric("market_cap", 105_900_000_000, end=date(2026, 10, 20), requires_price=True, source_ids=[7002]))
        d.latest_filed = date(2026, 6, 30)
        assert [x for x in currency.check(d) if x.evidence["rule"] == "stale_metric_input"] == []

    def test_14_months_old_input_is_inside_the_15_month_rule(self):
        d = clean_company()
        ok = src("CommonStockSharesOutstanding", 1, unit="shares", end=date(2025, 8, 20), sid=7003)
        d.sources[ok.id] = ok
        d.metrics.append(make_metric("market_cap", 5, end=date(2026, 10, 20), requires_price=True, source_ids=[7003]))
        assert [x for x in currency.check(d) if x.evidence["rule"] == "stale_metric_input"] == []

    def test_market_cap_without_any_fresh_share_count(self):
        d = clean_company()
        d.metrics.append(make_metric("market_cap", 5, end=date(2026, 10, 20), requires_price=True))
        assert "market_cap_no_fresh_shares" in rules(currency.check(d), "I7", WRONG_VALUE)

    def test_stale_displayed_value_is_review(self):
        d = clean_company()
        add(d, "ppe_net", 5_000_000, date(2012, 12, 31), None, "FY", tag="PropertyPlantAndEquipmentNet")
        d.latest_filed = date(2024, 12, 31)
        f = currency.check(d)
        assert any(x.evidence["rule"] == "stale_displayed_value" and x.severity == REVIEW for x in f)


# ----------------------------------------------------- I4 metrics / I9 splits
@pytest.mark.unit
class TestBkngSplit:
    """BKNG 25-for-1 (2026) missing from the split table: trailing P/E 1.23 vs ~18."""

    def broken(self, with_split=False):
        d = clean_company()
        add(d, "shares_outstanding", 825_000_000, date(2025, 6, 30), None, "Q2", tag="CommonStockSharesOutstanding", unit="shares")
        for c in list(d.cells):
            if c.concept == "shares_outstanding" and c.end == date(2024, 12, 31):
                d.cells.remove(c)
        add(d, "shares_outstanding", 33_000_000, date(2024, 12, 31), None, "FY", tag="CommonStockSharesOutstanding", unit="shares")
        if with_split:
            d.splits.append((date(2025, 3, 1), D(25)))
        d.metrics += [make_metric("trailing_pe", "1.23"), make_metric("market_cap", 150_000_000_000, requires_price=True)]
        return d

    def test_unrecorded_split_is_wrong_value(self):
        f = splits.check(self.broken())
        assert f and f[0].evidence["rule"] == "share_jump_without_split" and f[0].severity == WRONG_VALUE

    def test_recorded_split_is_clean(self):
        # the jump itself is explained by the split on record
        assert "share_jump_without_split" not in rules(splits.check(self.broken(with_split=True)))

    def test_pe_is_implausible(self):
        f = scale.check(self.broken())
        assert {"trailing_pe_below_floor", "trailing_pe_vs_market_cap_over_net_income"} <= rules(f, "I4", REVIEW)

    def test_normal_pe_is_clean(self):
        d = clean_company()
        d.metrics += [make_metric("trailing_pe", "22"), make_metric("market_cap", 2_900_000_000, requires_price=True)]
        assert scale.check(d) == []

    def test_market_cap_impossible(self):
        d = clean_company()
        d.metrics.append(make_metric("market_cap", "1270000000000000", requires_price=True))
        assert "market_cap_above_10T" in rules(scale.check(d), "I4", WRONG_VALUE)


# ---------------------------------------------------------------- I1 / I2 ties
@pytest.mark.unit
class TestStatementTies:
    def test_balance_sheet_that_does_not_balance(self):
        d = clean_company()
        for c in list(d.cells):
            if c.concept == "total_liabilities" and c.end == date(2024, 12, 31):
                d.cells.remove(c)
        add(d, "total_liabilities", 5_000_000_000, date(2024, 12, 31), None, "FY", tag="Liabilities")
        f = ties.check(d)
        assert any(x.invariant == "I1" and x.severity == WRONG_VALUE for x in f)

    def test_nci_adjustment_makes_a_balance_sheet_pass(self):
        d = clean_company()
        for c in list(d.cells):
            if c.concept == "stockholders_equity" and c.end == date(2024, 12, 31):
                d.cells.remove(c)
                nci = D(60_000_000)
                add(d, "stockholders_equity", c.value - nci, c.end, None, "FY", tag="StockholdersEquity")
                d.adjustment_facts.append(fact("MinorityInterest", nci, None, c.end))
                pid_ = c.period_id
                d.adjustment_facts[-1] = type(d.adjustment_facts[-1])(
                    id=d.adjustment_facts[-1].id, tag="MinorityInterest", value=nci, period_id=pid_, end=c.end)
        assert [x for x in ties.check(d) if x.invariant == "I1"] == []

    def test_net_income_does_not_tie_to_pretax_less_tax(self):
        d = clean_company()
        for c in list(d.cells):
            if c.concept == "net_income" and c.end == date(2024, 12, 31) and c.fiscal_period == "FY":
                d.cells.remove(c)
        add(d, "net_income", 4_801, date(2024, 12, 31), date(2024, 1, 1), "FY", tag="NetIncomeLoss")
        f = [x for x in ties.check(d) if x.invariant == "I2" and x.evidence["rule"] == "identity:net_income"]
        assert f and f[0].severity == WRONG_VALUE

    def test_cash_roll_forward_gap_is_review(self):
        d = clean_company()
        for c in list(d.cells):
            if c.concept == "cash_and_equivalents" and c.end == date(2024, 12, 31):
                d.cells.remove(c)
        add(d, "cash_and_equivalents", 9_000_000_000, date(2024, 12, 31), None, "FY", tag="Cash")
        f = [x for x in ties.check(d) if x.evidence["rule"] == "cash_roll_forward"]
        assert f and f[0].severity == REVIEW


# -------------------------------------------------------------- I6 sources
@pytest.mark.unit
class TestSourceIntegrity:
    def test_wrong_unit_ivda_twd_cash(self):
        d = clean_company()
        add(d, "cash_and_equivalents", 123_000_000, date(2024, 6, 30), None, "Q2", form="10-Q",
            sources=[src("CashAndCashEquivalentsAtCarryingValue", 123_000_000, unit="twd", form="10-Q")])
        f = [x for x in source_integrity.check(d) if x.evidence["rule"] == "wrong_unit_family"]
        assert f and f[0].severity == WRONG_VALUE and f[0].evidence["unit"] == "twd"

    def test_nonauthoritative_with_differing_authoritative_copy(self):
        d = clean_company()
        bad = src("NetIncomeLoss", 4801, auth=False, sid=9001)
        d.authoritative_copies[9001] = [src("NetIncomeLoss", 4_801_000_000, sid=9002)]
        add(d, "net_income", 4801, date(2023, 6, 30), date(2023, 4, 1), "Q2", sources=[bad], form="10-Q")
        assert "differs_from_authoritative_copy" in rules(source_integrity.check(d), "I6", WRONG_VALUE)

    def test_rounded_copy_within_rounding_is_not_a_difference(self):
        """TTWO 3,372,772K vs 3,372.8M: copies equal within rounding are one value."""
        d = clean_company()
        stored = src("Revenues", 3_372_772_000, auth=False, sid=9011)
        d.authoritative_copies[9011] = [src("Revenues", 3_372_800_000, sid=9012)]
        add(d, "revenue", 3_372_772_000, date(2023, 6, 30), date(2023, 4, 1), "Q2", sources=[stored], form="10-Q")
        assert "differs_from_authoritative_copy" not in rules(source_integrity.check(d))

    def conflict_cell(self, stored, copies, *, lone_value=None):
        d = clean_company()
        first = src("Revenues", lone_value if lone_value is not None else copies[0], auth=False, sid=9101, form="10-Q")
        d.conflict_copies[9101] = [src("Revenues", v, auth=False, sid=9102 + i, form="10-Q") for i, v in enumerate(copies[1:])]
        add(d, "revenue", stored, date(2022, 9, 30), date(2022, 7, 1), "Q3", sources=[first], form="10-Q")
        return d

    def na(self, d):
        return [x for x in source_integrity.check(d) if x.evidence["rule"] == "non_authoritative_source"]

    def test_recorded_conflict_fill_is_info_not_review(self):
        """Two non-authoritative copies 4% apart, stored value is one of them (resolver tie-break)."""
        f = self.na(self.conflict_cell(10_400_000, [10_400_000, 10_000_000]))
        assert f and f[0].severity == "info" and f[0].evidence["conflict_filled"] is True and f[0].evidence["copies"] == 2

    def test_lone_non_authoritative_source_stays_review(self):
        f = self.na(self.conflict_cell(10_000_000, [10_000_000]))
        assert f and f[0].severity == REVIEW and f[0].evidence["conflict_filled"] is False

    def test_conflict_copies_more_than_15_percent_apart_stay_review(self):
        f = self.na(self.conflict_cell(10_000_000, [10_000_000, 13_000_000]))
        assert f[0].severity == REVIEW

    def test_stored_value_that_is_none_of_the_copies_stays_review(self):
        f = self.na(self.conflict_cell(10_200_000, [10_400_000, 10_000_000]))
        assert f[0].severity == REVIEW

    def test_value_not_in_sources(self):
        d = clean_company()
        add(d, "revenue", 9_999, date(2022, 9, 30), date(2022, 7, 1), "Q3", sources=[src("Revenues", 10_000_000, form="10-Q")])
        assert "value_not_in_sources" in rules(source_integrity.check(d), "I6", REVIEW)

    def test_sum_concept_must_equal_sum_of_sources(self):
        d = clean_company()
        add(d, "total_debt", 41, date(2024, 12, 31), None, "FY", sources=[src("ShortTermBorrowings", 10), src("LongTermDebtNoncurrent", 30)])
        assert "value_not_sum_of_sources" in rules(source_integrity.check(d))


# ------------------------------------------------------------------ I10 sector
@pytest.mark.unit
class TestSector:
    def bank(self):
        d = clean_company()
        d.sic, d.is_bank = "6022", True
        return d

    def test_bank_showing_a_suppressed_metric(self):
        d = self.bank()
        d.metrics.append(make_metric("gross_margin", "0.4"))
        f = sector.check(d)
        assert f and f[0].evidence["rule"] == "bank_shows_suppressed_metric" and f[0].severity == WRONG_VALUE

    def test_serve_time_suppression_removes_the_metric(self):
        d = self.bank()
        d.metrics += [make_metric("gross_margin", "0.4"), make_metric("roe", "0.1")]
        assert [m.name for m in served_view(d).metrics] == ["roe"]
        assert sector.check(served_view(d)) == []

    def test_non_bank_keeps_every_metric(self):
        d = clean_company()
        d.metrics.append(make_metric("gross_margin", "0.4"))
        assert sector.check(d) == [] and len(served_view(d).metrics) == 1

    def test_bank_sic_without_tag_evidence_is_review(self):
        d = clean_company()
        d.bank_sic_without_evidence = True
        assert rules(sector.check(d), "I10", REVIEW) == {"bank_sic_without_evidence"}


@pytest.mark.unit
def test_power_of_ten_signature_windows():
    assert power_of_ten_signature(Decimal("951"))  # SCHW
    assert power_of_ten_signature(Decimal("1000000"))
    assert power_of_ten_signature(Decimal("0.001"))
    assert not power_of_ten_signature(Decimal("100"))
    assert not power_of_ten_signature(Decimal("5000"))


# ------------------------------------------- guards found on the live S001 dry run
@pytest.mark.unit
class TestGuardsFromLiveDryRun:
    def test_first_dividend_in_q2_is_not_a_label_shift(self):
        """GOOG paid its first dividend in Q2 2024: Q2 equals the 6M window because Q1 is 0."""
        d = clean_company()
        add(d, "dividends_paid", 0, date(2024, 3, 31), date(2024, 1, 1), "Q1", tag="PaymentsOfDividends", form="10-Q")
        add(d, "dividends_paid", 2_466_000_000, date(2024, 6, 30), date(2024, 4, 1), "Q2", tag="PaymentsOfDividends", form="10-Q")
        add(d, "dividends_paid", 2_466_000_000, date(2024, 6, 30), date(2024, 1, 1), None, tag="PaymentsOfDividends", form="10-Q")
        assert "quarter_equals_longer_window" not in rules(period_integrity.check(d))

    def test_split_adjusted_eps_with_ratio_fact_is_clean(self):
        """Apple basic EPS 5.43 / 4 = 1.3575; the ratio fact is unit `pure` and is an adjustment, not a source."""
        d = clean_company()
        add(d, "basic_eps_resolved", D("1.3575"), date(2015, 3, 28), date(2014, 12, 28), "Q1",
            sources=[src("EarningsPerShareBasic", "5.43", unit="usd/shares", form="10-Q"),
                     src("StockholdersEquityNoteStockSplitConversionRatio1", 4, unit="pure", form="10-K")])
        add(d, "basic_eps", D("5.43"), date(2015, 3, 28), date(2014, 12, 28), "Q1",
            sources=[src("EarningsPerShareBasic", "5.43", unit="usd/shares", form="10-Q")])
        assert source_integrity.check(d) == []
        assert "layer_disagreement" not in rules(scale.check(d))

    def test_split_adjusted_value_that_does_not_match_is_flagged(self):
        d = clean_company()
        add(d, "basic_eps_resolved", D("2.0"), date(2015, 3, 28), date(2014, 12, 28), "Q1",
            sources=[src("EarningsPerShareBasic", "5.43", unit="usd/shares", form="10-Q"),
                     src("StockholdersEquityNoteStockSplitConversionRatio1", 4, unit="pure", form="10-K")])
        assert "value_not_in_sources" in rules(source_integrity.check(d), "I6", REVIEW)

    def test_arithmetic_fallback_is_explained_by_its_sources(self):
        d = clean_company()
        add(d, "gross_profit_resolved", 400, date(2022, 9, 30), date(2022, 7, 1), "Q3", form="10-Q",
            sources=[src("Revenues", 1000, form="10-Q"), src("CostOfRevenue", 600, form="10-Q")])
        assert source_integrity.check(d) == []
        add(d, "gross_profit_resolved", 450, date(2022, 12, 31), date(2022, 10, 1), "Q4", form="10-Q",
            sources=[src("Revenues", 1000, form="10-Q"), src("CostOfRevenue", 600, form="10-Q")])
        assert "value_not_in_sources" in rules(source_integrity.check(d))

    def test_nvda_unrecorded_ten_for_one_split_is_wrong_value(self):
        d = clean_company()
        for c in list(d.cells):
            if c.concept == "shares_outstanding" and c.end == date(2024, 12, 31):
                d.cells.remove(c)
        add(d, "shares_outstanding", 2_460_000_000, date(2024, 5, 24), None, "Q1", tag="CommonStockSharesOutstanding", unit="shares")
        add(d, "shares_outstanding", 24_530_000_000, date(2024, 8, 23), None, "Q2", tag="CommonStockSharesOutstanding", unit="shares")
        d.splits.append((date(2021, 7, 19), D(4)))  # only the old split is on record
        assert "share_jump_without_split" in rules(splits.check(d), "I9", WRONG_VALUE)
        d.splits.append((date(2024, 6, 10), D(10)))
        assert "share_jump_without_split" not in rules(splits.check(d))


# ------------------------------------------------------------ I11 history window
from certification_fixtures import add as _add  # noqa: E402
from scrooner_pipeline.certification import history  # noqa: E402
from scrooner_pipeline.certification.model import GapRow, MetricCell  # noqa: E402


def history_company():
    """Window 2015-2016: two 10-Ks and two 10-Qs; consumed = revenue (flow) + total_assets (instant)."""
    from certification_fixtures import CompanyData
    d = CompanyData(company_id=2, ticker="HST", as_of=date(2017, 3, 1))
    d.latest_filed = date(2016, 12, 31)
    d.window_start = date(2015, 1, 1)
    d.first_filing_period = date(2014, 3, 31)
    d.consumed = {"revenue_sanity_resolved": "income_statement", "total_assets_resolved": "balance_sheet"}
    d.filings = [(date(2015, 12, 31), "10-K"), (date(2016, 3, 31), "10-Q"), (date(2016, 12, 31), "10-K")]
    for fy, qs, qe in ((2015, None, None), (2016, date(2016, 1, 1), date(2016, 3, 31))):
        _add(d, "revenue_sanity_resolved", 1000, date(fy, 12, 31), date(fy, 1, 1), "FY", tag="Revenues")
        _add(d, "total_assets_resolved", 5000, date(fy, 12, 31), None, "FY", tag="Assets")
    _add(d, "revenue_sanity_resolved", 240, date(2016, 3, 31), date(2016, 1, 1), "Q1", tag="Revenues", form="10-Q")
    _add(d, "total_assets_resolved", 5000, date(2016, 3, 31), None, "Q1", tag="Assets", form="10-Q")
    return d


@pytest.mark.unit
class TestHistoryCompleteness:
    def test_complete_history_has_no_missing_cell(self):
        d = history_company()
        # Q4 of both years is missing in the fixture: give it
        _add(d, "revenue_sanity_resolved", 250, date(2015, 12, 31), date(2015, 10, 1), "Q4", tag="Revenues")
        _add(d, "revenue_sanity_resolved", 250, date(2016, 12, 31), date(2016, 10, 1), "Q4", tag="Revenues")
        assert history.check(d) == []

    def test_missing_cells_are_classified_by_period_gap(self):
        d = history_company()
        d.period_gaps = [GapRow("revenue_sanity_resolved", "Q4", date(2015, 12, 31), "q4_not_derived"),
                         GapRow("revenue_sanity_resolved", "Q4", date(2016, 12, 31), "q4_not_derived")]
        f = history.check(d)
        assert [x.evidence["rule"] for x in f] == ["missing_cell:q4_not_derived"]
        assert f[0].evidence["count"] == 2 and f[0].evidence["classified"] is True and f[0].severity == REVIEW

    def test_missing_cell_without_a_gap_row_is_unclassified(self):
        d = history_company()
        f = history.check(d)
        assert f and f[0].evidence["rule"] == "missing_cell:unclassified" and f[0].evidence["classified"] is False

    def test_expected_set_comes_from_filings_and_respects_window_and_first_filing(self):
        d = history_company()
        d.filings.append((date(2014, 12, 31), "10-K"))  # before the window
        exp = history.expected_periods(d)
        assert ("FY", date(2014, 12, 31)) not in exp
        assert {("FY", date(2015, 12, 31)), ("Q4", date(2016, 12, 31)), ("Q", date(2016, 3, 31)), ("I", date(2016, 3, 31))} <= exp
        d.first_filing_period = date(2016, 1, 1)  # late registrant: the 2015 periods are not expected
        assert ("FY", date(2015, 12, 31)) not in history.expected_periods(d)

    def test_late_registrant_gets_a_history_starts_after_window_finding(self):
        d = history_company()
        d.first_filing_period = date(2016, 3, 31)
        f = [x for x in history.check(d) if x.evidence["rule"] == "history_starts_after_window"]
        assert f and f[0].evidence["classified"] is False  # blocks checks_clean until a link is recorded

    def test_company_without_any_periodic_filing_in_window_blocks(self):
        d = history_company()
        d.filings = []
        f = history.check(d)
        assert [x.evidence["rule"] for x in f if x.evidence["classified"] is False] == ["no_periodic_filing_in_window"]

    def test_balance_sheet_concept_is_expected_as_instants_only(self):
        d = history_company()
        m = history.history_matrix(d)
        assert m["concepts"][(2015, "I", "expected")] == 1  # one fiscal-year-end instant; revenue contributes none
        assert m["concepts"][(2016, "I", "expected")] == 2  # Q1 10-Q and FY end
        assert m["concepts"][(2015, "FY", "expected")] == 1

    def test_metric_with_a_stated_reason_is_classified(self):
        d = history_company()
        d.metric_history = [
            MetricCell("net_margin", "FY", date(2015, 12, 31), D("0.1"), None),
            MetricCell("net_margin", "FY", date(2016, 12, 31), None, "bank revenue definition pending"),
        ]
        f = [x for x in history.check(d) if x.data_point_name == "net_margin"]
        assert [x.evidence["rule"] for x in f] == ["missing_metric:bank revenue definition pending"]
        assert f[0].evidence["classified"] is True

    def test_full_suite_includes_i11(self):
        d = history_company()
        assert any(f.invariant == "I11" for f in run_checks(d))


@pytest.mark.unit
class TestRefinementsFromLiveDryRun:
    def test_jnj_discontinued_ops_gain_is_review_not_wrong_value(self):
        """JNJ 2023: net income 31.1B vs pretax - tax 9.2B (Kenvue exchange gain in discontinued ops)."""
        d = clean_company()
        for c in list(d.cells):
            if c.concept == "net_income" and c.end == date(2024, 12, 31) and c.fiscal_period == "FY":
                d.cells.remove(c)
        add(d, "net_income", 410_000_000, date(2024, 12, 31), date(2024, 1, 1), "FY", tag="NetIncomeLoss")  # 2.6x expected 165M? pretax-tax
        f = [x for x in ties.check(d) if x.evidence["rule"] == "identity:net_income"]
        assert f and f[0].severity == "info"  # round 3: identities that cannot see NCI / discontinued ops are not stored

    def test_flat_dividends_in_adjacent_quarters_are_not_a_finding(self):
        """NVDA pays 99M a quarter for years: equal adjacent quarters are normal for dividends."""
        d = clean_company()
        for (qs, qe, fp) in QUARTERS[:3]:
            add(d, "dividends_paid", 99_000_000, qe, qs, fp, tag="PaymentsOfDividends", form="10-Q")
        assert period_integrity.check(d) == []

    def test_equal_adjacent_quarter_revenue_is_review(self):
        d = clean_company()
        for c in [c for c in d.cells if c.concept == "revenue" and c.fiscal_period in ("Q2", "Q3")]:
            d.cells.remove(c)
        for (qs, qe, fp) in QUARTERS[1:3]:
            add(d, "revenue", 300_000_000, qe, qs, fp, tag="Revenues", form="10-Q")
        assert "quarter_equals_adjacent_quarter" in rules(period_integrity.check(d), "I5", REVIEW)

    def test_weak_quarter_with_the_same_sign_is_not_a_basis_mix(self):
        """AMZN Q4 2022 EPS 0.02 against 0.30 neighbours: derived, but not a split basis mix."""
        d = clean_company()
        for (qs, qe, fp), v in zip(QUARTERS, [D("0.30"), D("0.28"), D("0.31"), D("0.02")]):
            add(d, "diluted_eps", v, qe, qs, fp, tag="EarningsPerShareDiluted", unit="usd/shares", derived=(fp == "Q4"))
        assert "per_share_basis_mix" not in rules(splits.check(d))


@pytest.mark.unit
def test_reason_family_collapses_parameterised_null_reasons():
    assert history.reason_family("missing:prior_period(2005_FY)") == "missing:prior_period"
    assert history.reason_family("missing:fcf(2015),cfo(2014),total_assets(2015)...") == "missing:fcf"
    assert history.reason_family("incomplete:add") == "incomplete:add"
    assert history.reason_family("bank revenue definition pending") == "bank revenue definition pending"


# ----------------------------------- I11 cause inference beyond the 15 period_gap concepts
@pytest.mark.unit
class TestInferCause:
    def company(self):
        d = history_company()
        d.mapped_tag_count = {"revenue": 2, "total_assets": 1, "cfo": 1}
        d.consumed = {"revenue_sanity_resolved": "income_statement", "total_assets_resolved": "balance_sheet",
                      "cfo": "cash_flow"}
        return d

    def cause(self, d, base, kind, end):
        return history.infer_cause(d, base, kind, end)

    def test_period_gap_row_wins(self):
        d = self.company()
        d.period_gaps = [GapRow("cfo", "FY", date(2015, 12, 31), "not_in_sec_feed")]
        d.mapped_facts = {"cfo": [(date(2015, 1, 1), date(2015, 12, 31))]}
        f = [x for x in history.check(d) if x.data_point_name == "cfo" and x.evidence["kind"] == "FY"]
        causes = {x.evidence["cause"]: x.evidence["period_ends"] for x in f}
        assert causes["not_in_sec_feed"] == ["2015-12-31"]  # the gap row beat the "fact exists" inference
        assert "fact_exists_not_resolved" not in causes or "2015-12-31" not in causes["fact_exists_not_resolved"]

    def test_fact_on_the_period_under_a_mapped_tag_is_fact_exists_not_resolved(self):
        d = self.company()
        d.mapped_facts = {"cfo": [(date(2015, 1, 1), date(2015, 12, 31))]}
        assert self.cause(d, "cfo", "FY", date(2015, 12, 31)) == "fact_exists_not_resolved"

    def test_no_fact_under_any_mapped_tag_but_period_loaded_is_no_mapped_tag(self):
        d = self.company()  # revenue/total_assets cells exist at 2015-12-31, so the period is loaded
        assert self.cause(d, "cfo", "FY", date(2015, 12, 31)) == "no_mapped_tag"

    def test_period_with_no_data_at_all_stays_unclassified(self):
        d = self.company()
        assert self.cause(d, "cfo", "FY", date(2019, 12, 31)) == "unclassified"

    def test_concept_with_no_mapped_tag_in_the_registry_is_unclassified(self):
        d = self.company()
        d.mapped_tag_count = {}
        assert self.cause(d, "cfo", "FY", date(2015, 12, 31)) == "unclassified"

    def test_q4_with_only_the_year_fact_is_q4_not_derived(self):
        d = self.company()
        d.mapped_facts = {"cfo": [(date(2015, 1, 1), date(2015, 12, 31))]}
        assert self.cause(d, "cfo", "Q4", date(2015, 12, 31)) == "q4_not_derived"

    def test_quarter_with_only_a_ytd_fact_is_quarter_not_derived(self):
        d = self.company()
        d.mapped_facts = {"cfo": [(date(2016, 1, 1), date(2016, 6, 30))]}  # 6M YTD ending the quarter
        assert self.cause(d, "cfo", "Q", date(2016, 6, 30)) == "quarter_not_derived"

    def test_instant_fact_matches_instant_not_duration(self):
        d = self.company()
        d.mapped_facts = {"total_assets": [(date(2015, 12, 31), date(2015, 12, 31))]}
        assert self.cause(d, "total_assets", "I", date(2015, 12, 31)) == "fact_exists_not_resolved"
        d.mapped_facts = {"total_assets": [(date(2015, 1, 1), date(2015, 12, 31))]}
        assert self.cause(d, "total_assets", "I", date(2015, 12, 31)) != "fact_exists_not_resolved"


# ----------------------------------------- metric cells with no stored row: the four buckets
from scrooner_pipeline.certification.model import MetricSpec  # noqa: E402


def metric_company(specs, rows, *, first=date(2010, 1, 1)):
    d = history_company()
    d.metric_specs = {s.name: s for s in specs}
    d.metric_history = rows
    d.first_data_period = first
    d.mapped_tag_count = {"revenue": 1, "total_assets": 1}
    return d


FY15, FY16 = date(2015, 12, 31), date(2016, 12, 31)


def buckets(d):
    return history.history_matrix(d)["metric_buckets"]


def metric_findings(d, name):
    return {x.evidence["rule"]: x for x in history.check(d) if x.data_point_name == name}


@pytest.mark.unit
class TestMetricNoRowBuckets:
    def test_a_fy_only_metric_is_not_defined_on_quarters(self):
        spec = MetricSpec("debtor_days", "(Accounts Receivable / Revenue) x 365, FY only", False, ("accounts_receivable",), ("balance_sheet",))
        d = metric_company([spec], [MetricCell("debtor_days", "FY", FY15, D(40), None), MetricCell("debtor_days", "FY", FY16, D(41), None)])
        assert buckets(d)["not_defined_for_period_kind"] == 3  # Q1 2016 10-Q, Q4 2015, Q4 2016
        assert "missing_metric:not_defined_for_period_kind" not in metric_findings(d, "debtor_days")

    def test_a_ttm_price_metric_has_no_fy_or_quarter_cell(self):
        spec = MetricSpec("market_cap", "Shares Outstanding x Price", True, ("shares_outstanding",), ("balance_sheet",))
        d = metric_company([spec], [])
        assert buckets(d)["not_defined_for_period_kind"] > 0 and metric_findings(d, "market_cap") == {}

    def test_a_kind_written_for_any_company_of_the_chunk_is_defined(self):
        spec = MetricSpec("debtor_days", "(Accounts Receivable / Revenue) x 365, FY only", False, ("accounts_receivable",), ("balance_sheet",))
        d = metric_company([spec], [MetricCell("debtor_days", "FY", FY15, D(40), None)])
        d.metric_kinds_seen = {"debtor_days": {"FY", "Q"}}  # another company has quarterly rows
        assert buckets(d)["not_defined_for_period_kind"] == 0

    def test_observed_kinds_beat_the_registry_text(self):
        """ROE-style: the text names no period kind, only FY rows exist anywhere -> quarters are not defined."""
        spec = MetricSpec("roa", "Net Income / Total Assets", False, ("net_income",), ("income_statement",))
        d = metric_company([spec], [MetricCell("roa", "FY", FY15, D(1), None), MetricCell("roa", "FY", FY16, D(1), None)])
        d.metric_kinds_seen = {"roa": {"FY"}}
        assert buckets(d)["not_defined_for_period_kind"] > 0 and buckets(d)["no_row_inputs_present"] == 0

    def test_a_composite_metric_without_registry_inputs_is_counted_apart(self):
        spec = MetricSpec("peg_ratio", "Trailing P/E / EPS Growth Rate, FY only", False, (), ())
        d = metric_company([spec], [MetricCell("peg_ratio", "FY", FY15, D(1), None)])
        b = buckets(d)
        assert b["no_row_inputs_present"] == 1 and b["no_row_inputs_present:metric_has_no_registry_inputs"] == 1

    def test_b_cagr_that_looks_back_before_the_first_period_is_insufficient_history(self):
        spec = MetricSpec("revenue_growth_10y_cagr", "(Revenue[t] / Revenue[t-10]) ^ (1/10) - 1, same fiscal_period.", False, ("revenue",), ("income_statement",))
        d = metric_company([spec], [MetricCell(spec.name, "FY", FY15, D(1), None)], first=date(2012, 6, 30))
        f = metric_findings(d, spec.name)
        assert list(f) == ["missing_metric:insufficient_history"] and f["missing_metric:insufficient_history"].evidence["classified"] is True

    def test_b_the_same_cagr_with_enough_history_is_not_insufficient(self):
        spec = MetricSpec("revenue_growth_10y_cagr", "(Revenue[t] / Revenue[t-10]) ^ (1/10) - 1, same fiscal_period.", False, ("revenue",), ("income_statement",))
        d = metric_company([spec], [MetricCell(spec.name, "FY", FY15, D(1), None)], first=date(2001, 1, 1))
        assert "missing_metric:insufficient_history" not in metric_findings(d, spec.name)

    def test_lookback_is_read_from_the_registry_text(self):
        def lb(text):
            return history.lookback_days(MetricSpec("m", text))
        assert lb("(Revenue[t] / Revenue[t-3]) ^ (1/3) - 1") == int(3 * 365.25)
        assert lb("same fiscal_period year over year") == int(365.25)
        assert lb("1 if gross margin increased across the 3 most recent CONSECUTIVE FY years") == int(2 * 365.25)
        assert lb("Gross Profit / Revenue") == 0

    def test_c_an_input_that_is_a_classified_missing_cell_carries_its_cause(self):
        spec = MetricSpec("net_margin", "Net Income / Revenue, FY only", False, ("revenue",), ("income_statement",))
        d = metric_company([spec], [MetricCell("net_margin", "FY", FY15, D(1), None)])
        d.cells = [c for c in d.cells if not (c.base == "revenue" and c.end == FY16 and c.fiscal_period == "FY")]
        d.period_gaps = [GapRow("revenue_sanity_resolved", "FY", FY16, "no_mapped_tag")]
        f = metric_findings(d, "net_margin")
        assert list(f) == ["missing_metric:input_gap"] and f["missing_metric:input_gap"].evidence["classified"] is True
        assert history.history_matrix(d)["metric_input_causes"]["no_mapped_tag"] == 1

    def test_c_an_input_gap_whose_own_cause_is_unclassified_still_blocks(self):
        spec = MetricSpec("net_margin", "Net Income / Revenue, FY only", False, ("revenue",), ("income_statement",))
        d = metric_company([spec], [MetricCell("net_margin", "FY", FY15, D(1), None)])
        d.cells = [c for c in d.cells if not (c.base == "revenue" and c.end == FY16 and c.fiscal_period == "FY")]
        d.mapped_tag_count = {}  # no period_gap row and no mapped tag: the input cell is `unclassified`
        f = metric_findings(d, "net_margin")
        assert list(f) == ["missing_metric:input_gap:unclassified"]
        assert f["missing_metric:input_gap:unclassified"].evidence["classified"] is False

    def test_d_all_inputs_present_but_no_row_is_a_blocking_gap(self):
        spec = MetricSpec("net_margin", "Net Income / Revenue, FY only", False, ("revenue",), ("income_statement",))
        d = metric_company([spec], [MetricCell("net_margin", "FY", FY15, D(1), None)])
        f = metric_findings(d, "net_margin")  # revenue FY2016 exists, the metric row for FY2016 does not
        assert list(f) == ["missing_metric:no_row_inputs_present"]
        assert f["missing_metric:no_row_inputs_present"].evidence["classified"] is False

    def test_balance_sheet_metric_at_fiscal_year_end_is_present_under_the_fy_label(self):
        spec = MetricSpec("current_ratio", "Current Assets / Current Liabilities", False, ("current_assets",), ("balance_sheet",))
        rows = [MetricCell("current_ratio", "FY", FY15, D(1), None), MetricCell("current_ratio", "FY", FY16, D(1), None),
                MetricCell("current_ratio", "Q1", date(2016, 3, 31), D(1), None)]
        d = metric_company([spec], rows)
        assert history.history_matrix(d)["metric_buckets"]["no_row_inputs_present"] == 0

    def test_a_row_with_a_stated_reason_keeps_its_reason_not_a_bucket(self):
        spec = MetricSpec("net_margin", "Net Income / Revenue", False, ("revenue",), ("income_statement",))
        d = metric_company([spec], [MetricCell("net_margin", "FY", FY15, D(1), None),
                                    MetricCell("net_margin", "FY", FY16, None, "incomplete:numerator")])
        assert "missing_metric:incomplete:numerator" in metric_findings(d, "net_margin")
