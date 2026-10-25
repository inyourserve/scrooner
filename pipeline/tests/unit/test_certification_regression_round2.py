"""Regression set, round 2 (data-team/36, "precision of the tuned suite"): the six
measuring fixes asked by the Verifier. Confirmed defects must be caught; the
refuted and mislocated cases must not fire as `wrong_value`.

(1)(2) share basis by SOURCE FILING DATE, split recorded twice by ratio and event
(3) recast 8-K lineage            (4) stale quarter, not the year
(5) mixed vintage only when inputs differ   (6) perimeter mix on face-line tags
and the misses: Visa DPS without quarters, JNJ FY2023 R&D.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from certification_fixtures import D, add, src

from scrooner_pipeline.certification import composition, period_integrity, scale, source_integrity, splits
from scrooner_pipeline.certification.model import REVIEW, WRONG_VALUE, CompanyData


def empty():
    d = CompanyData(company_id=7, ticker="T", as_of=date(2026, 10, 21))
    d.latest_filed = date(2026, 6, 30)
    return d


def rules(findings, severity=None):
    return {f.evidence["rule"] for f in findings if severity is None or f.severity == severity}


def cell(d, concept, value, as_filed, filed, end, *, start=None, fp="Q", tag=None, unit="usd/shares"):
    """A display cell holding `value` whose single source is the as-filed fact `as_filed` filed on `filed`."""
    s = src(tag or concept, as_filed, unit=unit, filed=filed, end=end, form="10-Q")
    return add(d, concept, value, end, start, fp, sources=[s])


def flagged(d):
    return {(f.data_point_name, f.period_end) for f in splits.check(d) if f.evidence["rule"] == "share_basis_mismatch"}


# ------------------------------------------------ (1) filing-date basis
class TestShareBasisByFilingDate:
    def test_tsla_q3_2019_adjusted_by_5_not_15_is_flagged_and_the_correct_cells_are_not(self):
        d = empty()
        d.splits = [(date(2020, 8, 31), D(5)), (date(2022, 8, 25), D(3))]
        # raw 0.80 filed 2019-10-24: should be 0.80 / 15 = 0.0533, stored 0.16 (= /5 only)
        cell(d, "basic_eps", D("0.16"), D("0.80"), date(2019, 10, 24), date(2019, 9, 30), start=date(2019, 7, 1))
        # Q3 2017: raw -3.70 filed 2017-10-25, stored -0.2467 = /15: correct
        cell(d, "basic_eps", D("-0.2467"), D("-3.70"), date(2017, 10, 25), date(2017, 9, 30), start=date(2017, 7, 1))
        # a value filed between the two splits, adjusted by the 3-for-1 only
        cell(d, "basic_eps", D("0.107"), D("0.32"), date(2020, 10, 22), date(2020, 9, 30), start=date(2020, 7, 1))
        got = flagged(d)
        assert ("basic_eps", date(2019, 9, 30)) in got
        assert ("basic_eps", date(2017, 9, 30)) not in got
        assert ("basic_eps", date(2020, 9, 30)) not in got  # filed after the 5-for-1, /3 is right

    def test_tsla_partly_adjusted_q1_2020_is_flagged(self):
        d = empty()
        d.splits = [(date(2020, 8, 31), D(5)), (date(2022, 8, 25), D(3))]
        cell(d, "diluted_eps", D("0.02"), D("0.06"), date(2020, 4, 29), date(2020, 3, 31), start=date(2020, 1, 1))  # /3 only
        assert ("diluted_eps", date(2020, 3, 31)) in flagged(d)

    def test_wmt_value_filed_after_the_split_and_divided_again_is_flagged(self):
        d = empty()
        d.splits = [(date(2024, 2, 23), D(3))]
        cell(d, "basic_eps", D("0.64"), D("1.92"), date(2024, 3, 15), date(2024, 1, 31), start=date(2023, 2, 1), fp="FY")
        cell(d, "basic_eps", D("1.63"), D("4.90"), date(2022, 3, 15), date(2022, 1, 31), start=date(2021, 2, 1), fp="FY")  # /3: right
        f = [x for x in splits.check(d) if x.evidence["rule"] == "share_basis_mismatch"]
        assert [x.period_end for x in f] == [date(2024, 1, 31)]
        assert f[0].evidence["adjusted_though_filed_after_split"] is True

    def test_goog_value_filed_before_the_split_and_not_divided_is_flagged(self):
        d = empty()
        d.splits = [(date(2022, 7, 15), D(20))]
        cell(d, "basic_eps", D("59.15"), D("59.15"), date(2021, 2, 3), date(2020, 12, 31), start=date(2020, 1, 1), fp="FY")
        cell(d, "basic_eps", D("2.96"), D("59.15"), date(2021, 2, 3), date(2019, 12, 31), start=date(2019, 1, 1), fp="FY")
        assert flagged(d) == {("basic_eps", date(2020, 12, 31))}

    def test_every_share_count_filed_before_a_split_is_flagged_and_later_ones_are_not(self):
        d = empty()
        d.splits = [(date(2020, 8, 28), D(4))]
        for y, filed in ((2018, date(2018, 11, 5)), (2019, date(2019, 10, 31)), (2021, date(2021, 10, 29))):
            cell(d, "shares_outstanding", D(5_000_000_000) * (4 if y == 2021 else 1), D(5_000_000_000) * (4 if y == 2021 else 1),
                 filed, date(y, 9, 28), fp="FY", unit="shares")
        assert flagged(d) == {("shares_outstanding", date(2018, 9, 28)), ("shares_outstanding", date(2019, 9, 28))}

    def test_a_split_missing_from_the_table_is_inferred_from_the_filing_dated_share_series(self):
        """NVDA: the 10-for-1 of 2024 has no row. Filings up to 2024-05 report 2.46B, from 2024-08 24.53B."""
        d = empty()
        for fy_end, filed, shares in ((date(2023, 1, 29), date(2023, 2, 24), 2_470_000_000), (date(2024, 1, 28), date(2024, 2, 21), 2_460_000_000),
                                      (date(2024, 7, 28), date(2024, 8, 28), 24_530_000_000), (date(2025, 1, 26), date(2025, 2, 26), 24_400_000_000)):
            cell(d, "shares_outstanding", shares, shares, filed, fy_end, fp="FY", unit="shares")
        cell(d, "diluted_eps", D("1.74"), D("1.74"), date(2023, 2, 24), date(2023, 1, 29), start=date(2022, 1, 31), fp="FY")
        cell(d, "diluted_eps", D("2.94"), D("2.94"), date(2025, 2, 26), date(2025, 1, 26), start=date(2024, 1, 29), fp="FY")
        events, _ = splits.split_events(d)
        assert [(e.kind, e.ratio) for e in events] == [("inferred", D(10))]
        assert flagged(d) == {("shares_outstanding", date(2023, 1, 29)), ("shares_outstanding", date(2024, 1, 28)),
                              ("diluted_eps", date(2023, 1, 29))}

    def test_values_that_follow_the_filing_date_rule_are_clean(self):
        d = empty()
        d.splits = [(date(2020, 8, 28), D(4))]
        cell(d, "diluted_eps", D("2.98"), D("11.91"), date(2018, 11, 5), date(2018, 9, 29), start=date(2017, 10, 1), fp="FY")
        cell(d, "diluted_eps", D("3.28"), D("3.28"), date(2020, 10, 30), date(2020, 9, 26), start=date(2019, 9, 29), fp="FY")
        assert flagged(d) == set()

    def test_aapl_fy2018_eps_never_adjusted_is_flagged(self):
        d = empty()
        d.splits = [(date(2020, 8, 28), D(4))]
        cell(d, "diluted_eps", D("11.91"), D("11.91"), date(2018, 11, 5), date(2018, 9, 29), start=date(2017, 10, 1), fp="FY")
        assert flagged(d) == {("diluted_eps", date(2018, 9, 29))}


    def test_a_cell_listing_the_same_fact_from_two_filings_uses_the_newest_copy(self):
        """AAPL FY2018 diluted EPS 11.91 is the source of two 10-Ks (2018, 2019), both before the 2020 split."""
        d = empty()
        d.splits = [(date(2020, 8, 28), D(4))]
        two = [src("EarningsPerShareDiluted", D("11.91"), unit="usd/shares", filed=date(2018, 11, 5), form="10-K"),
               src("EarningsPerShareDiluted", D("11.91"), unit="usd/shares", filed=date(2019, 10, 31), form="10-K")]
        add(d, "diluted_eps_resolved", D("11.91"), date(2018, 9, 29), date(2017, 10, 1), "FY", sources=two)
        assert flagged(d) == {("diluted_eps_resolved", date(2018, 9, 29))}

    def test_tsla_q3_2019_the_re_presented_copy_was_only_divided_by_5(self):
        """Sources: 0.80 (10-Q 2019-10-29) and 0.16 (10-Q 2020-10-26, adjusted for the 5-for-1 only); the 3-for-1 of 2022 is still missing."""
        d = empty()
        d.splits = [(date(2020, 8, 10), D(5)), (date(2022, 8, 5), D(3))]
        two = [src("EarningsPerShareBasic", D("0.80"), unit="usd/shares", filed=date(2019, 10, 29), form="10-Q"),
               src("EarningsPerShareBasic", D("0.16"), unit="usd/shares", filed=date(2020, 10, 26), form="10-Q")]
        add(d, "basic_eps_resolved", D("0.16"), date(2019, 9, 30), date(2019, 7, 1), "Q3", sources=two)
        ok = [src("EarningsPerShareBasic", D("-3.70"), unit="usd/shares", filed=date(2017, 11, 3), form="10-Q"),
              src("StockholdersEquityNoteStockSplitConversionRatio1", D(5), unit="pure", filed=date(2020, 10, 26), form="10-Q"),
              src("StockholdersEquityNoteStockSplitConversionRatio1", D(3), unit="pure", filed=date(2022, 10, 24), form="10-Q")]
        add(d, "basic_eps_resolved", D("-0.246667"), date(2017, 9, 30), date(2017, 7, 1), "Q3", sources=ok)
        assert flagged(d) == {("basic_eps_resolved", date(2019, 9, 30))}


# ------------------------------------------------ (2) split recorded twice
class TestSplitRecordedTwice:
    def series(self, d, steps):
        """Share counts as filed: (filing date, shares)."""
        for i, (filed, shares) in enumerate(steps):
            cell(d, "shares_outstanding", shares, shares, filed, filed - timedelta(days=40), fp="FY", unit="shares")

    def test_goog_announcement_and_effective_date_164_days_apart_are_one_event(self):
        d = empty()
        d.splits = [(date(2022, 2, 1), D(20)), (date(2022, 7, 15), D(20))]
        self.series(d, [(date(2021, 2, 3), 680_000_000), (date(2022, 2, 2), 670_000_000), (date(2022, 8, 2), 13_100_000_000), (date(2023, 2, 1), 12_800_000_000)])
        events, dups = splits.split_events(d)
        assert [(e.date, e.ratio) for e in events] == [(date(2022, 7, 15), D(20))] and len(dups) == 1
        f = [x for x in splits.check(d) if x.evidence["rule"] == "split_ratio_counted_twice"]
        assert f and f[0].severity == WRONG_VALUE and f[0].evidence["days_apart"] == 164

    def test_goog_eps_divided_by_400_is_flagged_against_the_deduplicated_table(self):
        d = empty()
        d.splits = [(date(2022, 2, 1), D(20)), (date(2022, 7, 15), D(20))]
        cell(d, "basic_eps", D("0.0129"), D("5.16"), date(2015, 4, 24), date(2015, 3, 31), start=date(2015, 1, 1))  # 5.16 / 400
        cell(d, "basic_eps", D("0.258"), D("5.16"), date(2015, 4, 24), date(2014, 12, 31), start=date(2014, 10, 1))  # 5.16 / 20: right
        assert flagged(d) == {("basic_eps", date(2015, 3, 31))}

    def test_nvda_rows_46_days_apart_are_one_event(self):
        d = empty()
        d.splits = [(date(2021, 6, 3), D(4)), (date(2021, 7, 19), D(4))]
        self.series(d, [(date(2021, 5, 26), 620_000_000), (date(2021, 8, 18), 2_490_000_000)])
        assert len(splits.split_events(d)[1]) == 1

    def test_two_real_splits_of_one_ratio_a_year_and_a_half_apart_are_not_duplicates(self):
        d = empty()
        d.splits = [(date(2010, 6, 1), D(2)), (date(2011, 12, 1), D(2))]
        self.series(d, [(date(2010, 3, 1), 100_000_000), (date(2010, 9, 1), 200_000_000), (date(2011, 9, 1), 205_000_000), (date(2012, 3, 1), 410_000_000)])
        assert splits.split_events(d)[1] == []


    def test_two_same_ratio_rows_with_two_steps_in_the_share_series_are_two_real_splits(self):
        d = empty()
        d.splits = [(date(2010, 6, 1), D(2)), (date(2010, 12, 20), D(2))]  # 202 days apart, two doublings
        TestSplitRecordedTwice.series(self, d, [(date(2010, 3, 1), 100_000_000), (date(2010, 9, 1), 200_000_000), (date(2011, 3, 1), 400_000_000)])
        assert splits.split_events(d)[1] == []


# ------------------------------------------------ (3) recast 8-K lineage
class TestRecast8K:
    def tax(self, form, facts, stored=D("170300000"), original=D("172000000")):
        d = empty()
        d.filing_fact_counts = {"acc-8k": facts}
        s = src("IncomeTaxExpenseBenefit", stored, form=form, sid=8301, accession="acc-8k")
        d.periodic_copies[8301] = [src("IncomeTaxExpenseBenefit", original, form="10-Q", sid=8302)]
        add(d, "income_tax_expense_resolved", stored, date(2017, 3, 31), date(2017, 1, 1), "Q1", sources=[s], form=form)
        return d

    def test_lly_8k_with_full_restated_statements_is_a_lineage_note(self):
        f = source_integrity.check(self.tax("8-K", 1200))
        assert "recast_8k_lineage" in rules(f, REVIEW) and "non_periodic_form" not in rules(f)

    def test_the_same_numbers_from_an_8k_without_statements_stay_a_possible_rounding_error(self):
        f = source_integrity.check(self.tax("8-K", 6, stored=D("170300000"), original=D("170100000")))
        assert "non_periodic_form" in rules(f, WRONG_VALUE)

    def test_a_proxy_is_never_a_recast(self):
        f = source_integrity.check(self.tax("DEF 14A", 5000, stored=D("48300000000"), original=D("48334000000")))
        assert "recast_8k_lineage" not in rules(f) and "non_periodic_form" in rules(f, WRONG_VALUE)


# ------------------------------------------------ (4) stale quarter rather than the year
class TestStaleQuarter:
    def company(self, q2_filed):
        d = empty()
        fs, fe = date(2023, 1, 2), date(2023, 12, 31)
        add(d, "interest_expense", 772_000_000, fe, fs, "FY", filed=date(2024, 2, 20), accession="fy")
        add(d, "interest_expense", 621_000_000, date(2023, 10, 1), fs, None, form="10-Q", filed=date(2023, 10, 31), accession="q3")
        add(d, "interest_expense", 212_000_000, date(2023, 4, 2), fs, "Q1", form="10-Q", filed=date(2024, 4, 30), accession="q1b")
        add(d, "interest_expense", 346_000_000, date(2023, 7, 2), date(2023, 4, 3), "Q2", form="10-Q", filed=q2_filed, accession="q2")
        add(d, "interest_expense", 148_000_000, date(2023, 10, 1), date(2023, 7, 3), "Q3", form="10-Q", filed=date(2023, 10, 31), accession="q3")
        add(d, "interest_expense", 151_000_000, fe, date(2023, 10, 2), "Q4", derived=True, filed=date(2024, 2, 20), accession="fy")
        return d

    def test_jnj_the_never_represented_quarter_is_flagged_not_the_year(self):
        f = period_integrity.check(self.company(date(2023, 8, 1)))
        assert not {"quarters_do_not_sum_to_year", "quarters_vs_year_basis_mix"} & rules(f)
        stale = [x for x in f if x.evidence["rule"] == "stale_quarter_basis"]
        assert len(stale) == 1 and stale[0].period_end == date(2023, 7, 2) and stale[0].severity == WRONG_VALUE


    def test_a_year_that_is_not_its_own_9m_plus_q4_keeps_the_year_finding(self):
        d = self.company(date(2023, 8, 1))
        for c in list(d.cells):  # make the derived Q4 disagree with FY - 9M
            if c.fiscal_period == "Q4":
                d.cells.remove(c)
        add(d, "interest_expense", 40_000_000, date(2023, 12, 31), date(2023, 10, 2), "Q4", derived=True, filed=date(2024, 2, 20), accession="fy")
        f = period_integrity.check(d)
        assert "stale_quarter_basis" not in rules(f) and rules(f) & {"quarters_do_not_sum_to_year", "quarters_vs_year_basis_mix"}


# ------------------------------------------------ (5) mixed vintage only when the inputs differ
class TestMixedVintageNeedsDifferingInputs:
    def cell(self, copy_value):
        d = empty()
        eight_k = src("GrossProfit", 8_509_000_000, form="8-K", sid=8401)
        d.periodic_copies[8401] = [src("GrossProfit", copy_value, form="10-K", sid=8402)]
        add(d, "operating_expenses_resolved", 6_138_000_000, date(2017, 10, 29), date(2016, 11, 1), "FY",
            sources=[eight_k, src("OperatingIncomeLoss", 2_371_000_000, form="10-K", sid=8403)])
        return d

    def test_avgo_both_versions_agree_on_gross_profit_is_not_flagged(self):
        assert "mixed_vintage" not in rules(source_integrity.check(self.cell(8_509_000_000)))

    def test_lly_inputs_that_differ_between_versions_are_flagged(self):
        assert "mixed_vintage" in rules(source_integrity.check(self.cell(9_900_000_000)), WRONG_VALUE)

    def test_no_periodic_copy_to_compare_with_is_not_flagged(self):
        d = self.cell(1)
        d.periodic_copies.clear()
        assert "mixed_vintage" not in rules(source_integrity.check(d))


# ------------------------------------------------ (6) face-line perimeter
class TestPerimeterMix:
    ROLES = {("income_before_tax", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"): (1, "approved"),
             ("income_before_tax", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"): (2, "approved"),
             ("cost_of_revenue", "CostOfRevenue"): (2, "approved"), ("cost_of_revenue", "CostOfGoodsSold"): (3, "provisional")}

    def build(self, concept, fy_tag, q_tag, fy_value, q_values):
        d = empty()
        d.tag_roles = dict(self.ROLES)
        add(d, concept, fy_value, date(2017, 12, 30), date(2016, 12, 31), "FY", tag=fy_tag, filed=date(2018, 2, 20))
        ends = [(date(2016, 12, 31), date(2017, 4, 1)), (date(2017, 4, 2), date(2017, 7, 1)), (date(2017, 7, 2), date(2017, 9, 30)), (date(2017, 10, 1), date(2017, 12, 30))]
        for (a, b), v in zip(ends, q_values):
            add(d, concept, v, b, a, None, tag=q_tag, form="10-Q", filed=b + timedelta(days=30))
        return d

    def test_amd_pretax_on_two_approved_face_tags_is_a_perimeter_mix_review(self):
        d = self.build("income_before_tax", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                       "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
                       -15_000_000, [-26_000_000, -36_000_000, 8_000_000, 46_000_000])
        f = period_integrity.check(d)
        assert "quarters_vs_year_perimeter_mix" in rules(f, REVIEW) and not rules(f, WRONG_VALUE)

    def test_tsla_cost_of_revenue_on_a_component_tag_stays_wrong_value(self):
        d = self.build("cost_of_revenue", "CostOfGoodsSold", "CostOfRevenue", 6_724_480_000, [2_028_324_000, 2_122_942_000, 2_535_535_000, 2_849_463_000])
        f = period_integrity.check(d)
        assert "quarters_do_not_sum_to_year" in rules(f, WRONG_VALUE)


# ------------------------------------------------ misses
class TestMisses:
    def test_visa_fy2021_dps_without_quarters_is_caught_by_the_cash_dividends(self):
        d = empty()
        fs, fe = date(2020, 10, 1), date(2021, 9, 30)
        add(d, "net_income", D(10_866_000_000), fe, fs, "FY", tag="NetIncomeLoss")
        add(d, "diluted_eps", D("4.99"), fe, fs, "FY", tag="EarningsPerShareDiluted", unit="usd/shares")
        add(d, "dividends_paid", D(2_800_000_000), fe, fs, "FY", tag="PaymentsOfDividends")
        add(d, "dividends_per_share", D("0.32"), fe, fs, "FY", tag="CommonStockDividendsPerShareDeclared", unit="usd/shares")
        assert len(composition.dps_rate_on_ytd(d)) == 1

    def test_a_fully_paid_year_without_quarters_is_not_flagged(self):
        d = empty()
        fs, fe = date(2020, 10, 1), date(2021, 9, 30)
        add(d, "net_income", D(10_866_000_000), fe, fs, "FY", tag="NetIncomeLoss")
        add(d, "diluted_eps", D("4.99"), fe, fs, "FY", tag="EarningsPerShareDiluted", unit="usd/shares")
        add(d, "dividends_paid", D(700_000_000), fe, fs, "FY", tag="PaymentsOfDividends")
        add(d, "dividends_per_share", D("0.32"), fe, fs, "FY", tag="CommonStockDividendsPerShareDeclared", unit="usd/shares")
        assert composition.dps_rate_on_ytd(d) == {}

    def test_jnj_fy2023_rd_483m_is_caught_by_the_history_of_the_other_years(self):
        d = empty()
        for y in range(2015, 2026):
            fs, fe = date(y, 1, 1), date(y, 12, 31)
            add(d, "revenue", D(int(70e9 + 1.5e9 * (y - 2015))), fe, fs, "FY", tag="Revenues")
            rd = {2015: 9.0e9, 2016: 9.1e9, 2017: 10.8e9, 2018: 10.6e9, 2019: 11.4e9, 2020: 12.2e9, 2021: 14.3e9, 2022: 14.1e9, 2023: 483e6, 2024: 17.2e9, 2025: 14.7e9}[y]
            add(d, "research_and_development", D(int(rd)), fe, fs, "FY", tag="ResearchAndDevelopmentExpense")
        f = [x for x in scale.check(d) if x.evidence["rule"] == "statement_role_suspect"]
        assert [x.period_end.year for x in f] == [2023] and f[0].severity == WRONG_VALUE and "history" in f[0].evidence["signals"]
