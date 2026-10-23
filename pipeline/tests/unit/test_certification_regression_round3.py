"""Regression set, round 3: the fixes the Verifier's held-out validation asked for
(data-team/strategy/team/CERTIFY-HELDOUT-VALIDATION-2026-10-22.md, section 5). Every case
is a filing-checked cell named in that report.

TRAINING cases (the author looked at these cells and built the fix for them):
  ODFL 3-for-2, BAX total debt, CMG tax sign, LMT opex, VLO liabilities, DOC REIT subtotal,
  BMY cross-vintage gross profit, MO/MPC/SPGI/DOC identities, MLI public float,
  ODFL Q4 2017 tax, TSLA 2015-2016 diluted EPS, and the derived-Q4 tax-rate / EPS cells.
HELD OUT (never used to design a rule; checked only by the live validation run):
  every other cell of the Verifier's 30-cell frames (AVY, EL, NEM, CBRE, FTNT, TTWO EPS and
  tax rates, GGG, CSL, the K-passed sample, the six NOT-VERIFIED cells...).
"""

from datetime import date
from decimal import Decimal

import pytest
from certification_fixtures import D, add, src

from scrooner_pipeline.certification import (
    composition, currency, period_integrity, sign, source_integrity, splits, ties,
)
from scrooner_pipeline.certification.model import CompanyData, ComponentFact, REVIEW, WRONG_VALUE


def empty(sic="3571"):
    d = CompanyData(company_id=11, ticker="T", sic=sic, as_of=date(2026, 10, 22))
    d.latest_filed = date(2026, 6, 30)
    return d


def rules(findings, severity=None):
    return {f.evidence["rule"] for f in findings if severity is None or f.severity == severity}


def cell(d, concept, value, as_filed, filed, end, *, start=None, fp="Q", tag=None, unit="usd/shares"):
    s = src(tag or concept, as_filed, unit=unit, filed=filed, end=end, form="10-Q")
    return add(d, concept, value, end, start, fp, sources=[s])


# ------------------------------------------------ (1) non-integer ratios (ODFL 3-for-2)
class TestOdflThreeForTwo:
    def company(self, restated=True):
        d = empty()
        # cover share counts as filed, by filing date: 82M until the 3-for-2 of March 2020, 123M after;
        # the 2-for-1 of 2024 is recorded in the split table, the 3-for-2 is not
        d.splits = [(date(2024, 3, 28), D(2))]
        for filed, end, n in ((date(2017, 10, 27), date(2017, 9, 30), 82_375_945), (date(2018, 2, 28), date(2017, 12, 31), 82_300_000),
                              (date(2020, 2, 26), date(2019, 12, 31), 82_000_000), (date(2020, 5, 6), date(2020, 3, 31), 123_000_000),
                              (date(2021, 2, 25), date(2020, 12, 31), 123_500_000)):
            cell(d, "shares_outstanding", n, n, filed, end, fp="Q", unit="shares")
        if restated:
            # Q1 2019 diluted EPS: 1.64 in the 2019 10-Q, 1.09 in the 2020 10-Q comparative (restated by 1.5)
            two = [src("EarningsPerShareDiluted", D("1.64"), unit="usd/shares", filed=date(2019, 5, 6), form="10-Q"),
                   src("EarningsPerShareDiluted", D("1.09"), unit="usd/shares", filed=date(2020, 5, 6), form="10-Q")]
            add(d, "diluted_eps", D("1.09"), date(2019, 3, 31), date(2019, 1, 1), "Q1", sources=two)
        return d

    def test_the_split_missing_from_the_table_is_inferred_when_comparatives_were_restated(self):
        events, _ = splits.split_events(self.company())
        assert any(e.kind == "inferred" and e.ratio == D("1.5") for e in events)

    def test_stored_fy2017_eps_divided_by_two_only_is_flagged_with_the_right_expected_value(self):
        d = self.company()
        cell(d, "diluted_eps", D("2.815"), D("5.63"), date(2018, 2, 28), date(2017, 12, 31), start=date(2017, 1, 1), fp="FY")
        got = {x.period_end: x for x in splits.check(d)
               if x.evidence["rule"] == "share_basis_mismatch" and x.data_point_name == "diluted_eps"}
        assert date(2017, 12, 31) in got
        assert abs(got[date(2017, 12, 31)].expected_or_other_value - D("1.8767")) < D("0.01")

    def test_the_share_count_expected_value_includes_both_splits(self):
        f = [x for x in splits.check(self.company()) if x.evidence["rule"] == "share_basis_mismatch" and x.data_point_name == "shares_outstanding"]
        first = min(f, key=lambda x: x.period_end)
        assert first.period_end == date(2017, 9, 30) and abs(first.expected_or_other_value - D(247_127_835)) < D(1)

    def test_an_acquisition_that_steps_only_the_cover_counts_is_not_a_split(self):
        """NEM / Newcrest, DOC / HCP, MPC / Andeavor: cover counts step 1.25-1.5x, no per-share comparative is restated."""
        events, _ = splits.split_events(self.company(restated=False))
        assert not any(e.kind == "inferred" for e in events)

    def test_the_restated_comparative_may_come_a_few_months_after_the_step_but_not_years(self):
        def inferred(restated_filed):
            d = self.company(restated=False)
            two = [src("EarningsPerShareDiluted", D("1.64"), unit="usd/shares", filed=date(2019, 5, 6), form="10-Q"),
                   src("EarningsPerShareDiluted", D("1.09"), unit="usd/shares", filed=restated_filed, form="10-Q")]
            add(d, "diluted_eps", D("1.09"), date(2019, 3, 31), date(2019, 1, 1), "Q1", sources=two)
            return any(e.kind == "inferred" for e in splits.split_events(d)[0])
        assert inferred(date(2020, 8, 4))  # 91 days after the step in the cover counts
        assert not inferred(date(2022, 5, 6))  # two years later: not this step

    def test_comparatives_that_moved_the_other_way_do_not_corroborate_a_share_increase(self):
        d = self.company(restated=False)
        two = [src("EarningsPerShareDiluted", D("1.09"), unit="usd/shares", filed=date(2019, 5, 6), form="10-Q"),
               src("EarningsPerShareDiluted", D("1.64"), unit="usd/shares", filed=date(2020, 5, 6), form="10-Q")]
        add(d, "diluted_eps", D("1.64"), date(2019, 3, 31), date(2019, 1, 1), "Q1", sources=two)  # EPS ROSE 1.5x while shares rose 1.5x
        assert not any(e.kind == "inferred" for e in splits.split_events(d)[0])

    def test_comparatives_are_read_from_other_filings_copies_not_only_from_the_cell_sources(self):
        """The cell lists one source; the restated comparative of the same period lives in another filing (loader: pershare_copies)."""
        d = self.company(restated=False)
        one = src("EarningsPerShareDiluted", D("1.64"), unit="usd/shares", filed=date(2019, 5, 6), form="10-Q", sid=9601)
        d.pershare_copies[9601] = [src("EarningsPerShareDiluted", D("1.09"), unit="usd/shares", filed=date(2020, 5, 6), form="10-Q", sid=9602)]
        add(d, "diluted_eps", D("1.64"), date(2019, 3, 31), date(2019, 1, 1), "Q1", sources=[one])
        assert any(e.kind == "inferred" and e.ratio == D("1.5") for e in splits.split_events(d)[0])

    def test_a_restated_comparative_with_unchanged_cover_counts_is_not_a_split_either(self):
        d = self.company()
        d.cells[:] = [c for c in d.cells if c.concept != "shares_outstanding"]
        for filed, end, n in ((date(2019, 2, 26), date(2018, 12, 31), 82_000_000), (date(2020, 5, 6), date(2020, 3, 31), 82_100_000)):
            cell(d, "shares_outstanding", n, n, filed, end, fp="Q", unit="shares")
        assert not any(e.kind == "inferred" for e in splits.split_events(d)[0])


# ------------------------------------------------ (3) BAX / CMG / LMT / VLO / DOC / BMY gates
class TestGates:
    def debt_company(self, stored, extra_tag, extra_value):
        d = empty()
        end = date(2020, 6, 30)
        add(d, "total_debt_resolved", stored, end, None, "Q2", tag="DebtCurrent", form="10-Q")
        d.debt_facts = [ComponentFact(1, "DebtCurrent", D(319_000_000), 99, end), ComponentFact(2, extra_tag, D(extra_value), 99, end)]
        for c in list(d.cells):
            pass
        d.cells[-1] = type(d.cells[-1])(**{**d.cells[-1].__dict__, "period_id": 99})
        return d

    def test_bax_total_debt_319m_against_6_055m_of_long_term_debt_and_finance_leases(self):
        d = self.debt_company(319_000_000, "LongTermDebtAndCapitalLeaseObligations", 6_055_000_000)
        f = [x for x in composition.check(d) if x.evidence["rule"] == "debt_below_component"]
        assert f and f[0].severity == WRONG_VALUE and f[0].evidence["largest_component_tag"] == "LongTermDebtAndCapitalLeaseObligations"

    def test_kr_borrowings_only_total_against_a_lease_inclusive_line_is_a_perimeter_not_an_error(self):
        d = self.debt_company(15_909_000_000, "LongTermDebtAndCapitalLeaseObligations", 17_633_000_000)
        assert "debt_below_component" not in rules(composition.check(d))

    def test_cmg_income_tax_sign_flipped_by_a_retagged_comparative(self):
        d = empty()
        s = src("IncomeTaxExpenseBenefit", -91_883_000, form="10-K", auth=False, sid=9001, accession="fy2020")
        d.conflict_copies[9001] = [src("IncomeTaxExpenseBenefit", 91_883_000, form="10-K", auth=False, sid=9002, accession="fy2018"),
                                   src("IncomeTaxExpenseBenefit", 91_883_000, form="10-K", auth=False, sid=9003, accession="fy2019")]
        add(d, "income_tax_expense", -91_883_000, date(2018, 12, 31), date(2018, 1, 1), "FY", sources=[s])
        f = [x for x in source_integrity.check(d) if x.evidence["rule"] == "sign_flip_between_copies"]
        assert f and f[0].severity == WRONG_VALUE and f[0].evidence["opposite_sign_copies"] == 2

    def test_a_stored_sign_that_the_majority_of_copies_share_is_not_flagged(self):
        d = empty()
        s = src("IncomeTaxExpenseBenefit", 91_883_000, form="10-K", auth=False, sid=9011)
        d.conflict_copies[9011] = [src("IncomeTaxExpenseBenefit", 91_883_000, form="10-K", auth=False, sid=9012),
                                   src("IncomeTaxExpenseBenefit", -91_883_000, form="10-K", auth=False, sid=9013)]
        add(d, "income_tax_expense", 91_883_000, date(2018, 12, 31), date(2018, 1, 1), "FY", sources=[s])
        assert "sign_flip_between_copies" not in rules(source_integrity.check(d))

    def test_lmt_negative_opex_calculated_as_gross_profit_minus_operating_income(self):
        d = empty()
        add(d, "operating_expenses", -62_000_000, date(2021, 12, 31), date(2021, 1, 1), "FY",
            sources=[src("GrossProfit", 9_061_000_000, sid=9101), src("OperatingIncomeLoss", 9_123_000_000, sid=9102)])
        f = sign.check(d)
        assert f and f[0].severity == WRONG_VALUE and f[0].evidence["calculated_from_inputs"] is True

    def test_a_single_filed_negative_stays_review(self):
        d = empty()
        add(d, "revenue", -7_000_000, date(2021, 12, 31), date(2021, 1, 1), "FY", tag="Revenues")
        assert sign.check(d)[0].severity == REVIEW

    def test_vlo_total_liabilities_that_leaves_the_noncontrolling_interest_inside(self):
        d = empty()
        add(d, "total_liabilities_resolved", 33_814_000_000, date(2020, 12, 31), None, "FY",
            sources=[src("Assets", 51_774_000_000, sid=9201), src("StockholdersEquity", 17_960_000_000, sid=9202),
                     src("MinorityInterest", 1_682_000_000, sid=9203)])
        f = [x for x in ties.check(d) if x.evidence["rule"] == "liabilities_nci_treatment"]
        assert f and f[0].severity == WRONG_VALUE and abs(f[0].expected_or_other_value - D(32_132_000_000)) < D(1)

    def test_total_liabilities_that_subtracts_the_nci_is_clean(self):
        d = empty()
        add(d, "total_liabilities_resolved", 32_132_000_000, date(2020, 12, 31), None, "FY",
            sources=[src("Assets", 51_774_000_000, sid=9211), src("StockholdersEquity", 17_960_000_000, sid=9212),
                     src("MinorityInterest", 1_682_000_000, sid=9213)])
        assert "liabilities_nci_treatment" not in rules(ties.check(d))

    def test_doc_reit_operating_income_built_from_revenue_minus_a_property_expense_line(self):
        for sic, expect in (("6798", True), ("3571", False)):
            d = empty(sic)
            add(d, "operating_income_resolved", 359_252_000, date(2016, 6, 30), date(2016, 4, 1), "Q2", form="10-Q",
                sources=[src("Revenues", 538_332_000, form="10-Q", sid=9301 + int(expect)), src("CostDirectOperatingCosts", 179_080_000, form="10-Q", sid=9303 + int(expect))])
            assert ("reit_calculated_subtotal" in rules(source_integrity.check(d), WRONG_VALUE)) is expect

    def test_bmy_gross_profit_from_a_2017_revenue_and_a_2018_recast_cost_of_sales(self):
        d = empty()
        rev = src("Revenues", 10_073_000_000, form="10-Q", sid=9401, filed=date(2017, 8, 1))
        cogs = src("CostOfGoodsAndServicesSold", 2_834_000_000, form="10-Q", sid=9402, filed=date(2018, 8, 1))
        d.conflict_copies[9402] = [src("CostOfGoodsAndServicesSold", 2_821_000_000, form="10-Q", sid=9403, filed=date(2017, 8, 1))]
        add(d, "gross_profit_resolved", 7_239_000_000, date(2017, 6, 30), date(2017, 1, 1), None, sources=[rev, cogs], form="10-Q")
        assert "cross_vintage_arithmetic" in rules(source_integrity.check(d), WRONG_VALUE)

    def test_inputs_that_did_not_change_between_the_two_filings_are_not_flagged(self):
        d = empty()
        rev = src("Revenues", 10_073_000_000, form="10-Q", sid=9411, filed=date(2017, 8, 1))
        cogs = src("CostOfGoodsAndServicesSold", 2_821_000_000, form="10-Q", sid=9412, filed=date(2018, 8, 1))
        d.conflict_copies[9412] = [src("CostOfGoodsAndServicesSold", 2_821_000_000, form="10-Q", sid=9413, filed=date(2017, 8, 1))]
        add(d, "gross_profit_resolved", 7_252_000_000, date(2017, 6, 30), date(2017, 1, 1), None, sources=[rev, cogs], form="10-Q")
        assert "cross_vintage_arithmetic" not in rules(source_integrity.check(d))


    def test_alle_gross_profit_whose_inputs_are_one_filings_own_versions_is_single_vintage(self):
        """Revenue 2,408.2 first filed in the FY2018 10-K, cost 1,335.3 first filed in the FY2019 10-K; the FY2019 10-K
        holds BOTH at the values that give the stored 1,072.9 (the newest version of every input)."""
        d = empty()
        rev = src("Revenues", 2_408_200_000, form="10-K", sid=9501, filed=date(2019, 2, 20))
        cogs = src("CostOfRevenue", 1_335_300_000, form="10-K", sid=9502, filed=date(2020, 2, 20))
        d.conflict_copies[9501] = [src("Revenues", 2_238_000_000, form="10-K", sid=9503, filed=date(2018, 2, 20)),
                                   src("Revenues", 2_408_200_000, form="10-K", sid=9505, filed=date(2020, 2, 20))]
        add(d, "gross_profit", 1_072_900_000, date(2017, 12, 31), date(2017, 1, 1), "FY", sources=[rev, cogs])
        assert "cross_vintage_arithmetic" not in rules(source_integrity.check(d))

    def test_inputs_restated_but_filed_less_than_200_days_apart_are_not_flagged(self):
        d = empty()
        rev = src("Revenues", 10_073_000_000, form="10-Q", sid=9511, filed=date(2017, 8, 1))
        cogs = src("CostOfGoodsAndServicesSold", 2_834_000_000, form="10-Q", sid=9512, filed=date(2017, 11, 1))
        d.conflict_copies[9512] = [src("CostOfGoodsAndServicesSold", 2_821_000_000, form="10-Q", sid=9513, filed=date(2017, 8, 1))]
        add(d, "gross_profit_resolved", 7_239_000_000, date(2017, 6, 30), date(2017, 1, 1), None, sources=[rev, cogs], form="10-Q")
        assert "cross_vintage_arithmetic" not in rules(source_integrity.check(d))

    def test_bax_total_debt_that_dips_to_a_twentieth_of_both_neighbouring_quarters(self):
        d = empty()
        for end, v in ((date(2020, 3, 31), 6_400_000_000), (date(2020, 6, 30), 319_000_000), (date(2020, 9, 30), 6_350_000_000)):
            add(d, "total_debt_resolved", v, end, None, "Q", tag="LongTermDebt", form="10-Q")
        f = [x for x in composition.check(d) if x.evidence["rule"] == "debt_isolated_dip"]
        assert [x.period_end for x in f] == [date(2020, 6, 30)] and f[0].severity == WRONG_VALUE

    def test_bax_erratic_series_only_the_value_with_a_big_balance_sheet_either_side_is_a_dip(self):
        """2019-12 5,350M; 2020-03 536M; 2020-06 319M; 2020-09 727M; 2020-12 6,233M: 2020-06 has 5.35B within two
        quarters before and 6.2B within two after. 2020-03 has no high value after it within two; 2020-09 none before."""
        d = empty()
        for end, v in ((date(2019, 12, 31), 5_350_000_000), (date(2020, 3, 31), 536_000_000), (date(2020, 6, 30), 319_000_000),
                       (date(2020, 9, 30), 727_000_000), (date(2020, 12, 31), 6_233_000_000)):
            add(d, "total_debt_resolved", v, end, None, "Q", tag="LongTermDebt", form="10-Q")
        f = [x for x in composition.check(d) if x.evidence["rule"] == "debt_isolated_dip"]
        assert [x.period_end for x in f] == [date(2020, 6, 30)]

    def test_bmy_unproven_when_no_filing_holds_both_inputs(self):
        d = empty()
        rev = src("Revenues", 10_073_000_000, form="10-Q", sid=9421, filed=date(2017, 8, 1))
        cogs = src("CostOfGoodsAndServicesSold", 2_834_000_000, form="10-Q", sid=9422, filed=date(2018, 8, 1))
        add(d, "gross_profit_resolved", 7_239_000_000, date(2017, 6, 30), date(2017, 1, 1), None, sources=[rev, cogs], form="10-Q")
        assert "cross_vintage_arithmetic" not in rules(source_integrity.check(d))

    def test_a_gap_of_more_than_five_percent_between_vintages_is_a_different_problem(self):
        d = empty()
        rev = src("Revenues", 10_073_000_000, form="10-Q", sid=9431, filed=date(2017, 8, 1))
        cogs = src("CostOfGoodsAndServicesSold", 2_000_000_000, form="10-Q", sid=9432, filed=date(2018, 8, 1))
        d.conflict_copies[9432] = [src("CostOfGoodsAndServicesSold", 2_821_000_000, form="10-Q", sid=9433, filed=date(2017, 8, 1))]
        add(d, "gross_profit_resolved", 8_073_000_000, date(2017, 6, 30), date(2017, 1, 1), None, sources=[rev, cogs], form="10-Q")
        assert "cross_vintage_arithmetic" not in rules(source_integrity.check(d))

    def test_a_repayment_that_stays_repaid_is_not_a_dip(self):
        d = empty()
        for end, v in ((date(2020, 3, 31), 6_400_000_000), (date(2020, 6, 30), 319_000_000), (date(2020, 9, 30), 300_000_000)):
            add(d, "total_debt_resolved", v, end, None, "Q", tag="LongTermDebt", form="10-Q")
        assert "debt_isolated_dip" not in rules(composition.check(d))


# ------------------------------------------------ (2) derived Q4: wrong number vs unsourced
class TestDerivedQ4Status:
    def etr(self, stored):
        d = empty()
        e, s = date(2023, 12, 31), date(2023, 10, 1)
        add(d, "income_tax_expense", 515_600_000, e, s, "Q4", tag="IncomeTaxExpenseBenefit")
        add(d, "income_before_tax", 2_503_400_000, e, s, "Q4", tag="IncomeLossBeforeIncomeTaxes")
        add(d, "effective_tax_rate_reported", stored, e, s, "Q4", tag="EffectiveIncomeTaxRate", unit="pure", derived=True)
        return d

    def test_pgr_derived_q4_tax_rate_minus_40_percent_is_a_wrong_number(self):
        f = [x for x in composition.check(self.etr(D("-0.404"))) if x.evidence["rule"] == "per_share_derived_by_subtraction"]
        assert f and f[0].severity == WRONG_VALUE and f[0].evidence["value_status"] == "differs_from_recompute"

    def test_a_derived_q4_tax_rate_that_matches_the_recompute_stays_gating_but_is_unsourced(self):
        f = [x for x in composition.check(self.etr(D("0.2060"))) if x.evidence["rule"] == "per_share_derived_by_subtraction"]
        assert f and f[0].severity == WRONG_VALUE and f[0].evidence["value_status"] == "consistent_with_recompute"

    def eps(self, stored):
        d = empty()
        for i, (a, b, e) in enumerate(((date(2022, 1, 1), date(2022, 3, 31), "0.50"), (date(2022, 4, 1), date(2022, 6, 30), "0.52"), (date(2022, 7, 1), date(2022, 9, 30), "0.54"))):
            add(d, "net_income", 100_000_000 + i * 4_000_000, b, a, f"Q{i + 1}", tag="NetIncomeLoss")
            add(d, "diluted_eps", D(e), b, a, f"Q{i + 1}", tag="EarningsPerShareDiluted", unit="usd/shares", form="10-Q")
        add(d, "net_income", 112_000_000, date(2022, 12, 31), date(2022, 10, 1), "Q4", tag="NetIncomeLoss")
        add(d, "diluted_eps", stored, date(2022, 12, 31), date(2022, 10, 1), "Q4", tag="EarningsPerShareDiluted", unit="usd/shares", derived=True)
        return d

    def test_a_derived_q4_eps_far_from_net_income_over_implied_shares_is_a_wrong_number(self):
        f = [x for x in composition.check(self.eps(D("0.31"))) if x.evidence["rule"] == "per_share_derived_by_subtraction" and x.data_point_name == "diluted_eps"]
        assert f and f[0].evidence["value_status"] == "differs_from_recompute"

    def test_a_derived_q4_eps_that_matches_stays_gating_as_unsourced(self):
        f = [x for x in composition.check(self.eps(D("0.56"))) if x.evidence["rule"] == "per_share_derived_by_subtraction" and x.data_point_name == "diluted_eps"]
        assert f and f[0].severity == WRONG_VALUE and f[0].evidence["value_status"] == "consistent_with_recompute"


# ------------------------------------------------ (4) identities demoted, annual-only staleness
class TestDemotions:
    def gp(self, gp, revenue=10_000_000_000, cost=6_000_000_000):
        d = empty()
        e, s = date(2020, 6, 30), date(2020, 4, 1)
        add(d, "revenue", revenue, e, s, "Q2", tag="Revenues", form="10-Q")
        add(d, "cost_of_revenue", cost, e, s, "Q2", tag="CostOfRevenue", form="10-Q")
        add(d, "gross_profit", gp, e, s, "Q2", tag="GrossProfit", form="10-Q")
        return d

    def test_mo_gross_profit_gap_from_excise_taxes_in_revenue_is_info(self):
        f = [x for x in ties.check(self.gp(3_287_000_000, 6_800_000_000, 3_100_000_000)) if x.evidence["rule"] == "identity:gross_profit"]
        assert f and all(x.severity == "info" for x in f)

    def test_a_gross_profit_that_is_a_unit_scale_error_is_still_wrong_value(self):
        f = [x for x in ties.check(self.gp(4_000_000)) if x.evidence["rule"] == "identity:gross_profit"]
        assert f and f[0].severity == WRONG_VALUE

    def test_mpc_net_income_gap_from_noncontrolling_interest_is_info(self):
        d = empty()
        e, s = date(2022, 6, 30), date(2022, 1, 1)
        add(d, "income_before_tax", 9_000_000_000, e, s, None, tag="IncomeLossBeforeIncomeTaxes", form="10-Q")
        add(d, "income_tax_expense", 1_650_000_000, e, s, None, tag="IncomeTaxExpenseBenefit", form="10-Q")
        add(d, "net_income", 6_718_000_000, e, s, None, tag="NetIncomeLoss", form="10-Q")
        f = [x for x in ties.check(d) if x.evidence["rule"] == "identity:net_income"]
        assert f and all(x.severity == "info" for x in f)

    def test_mli_public_float_of_a_june_date_is_not_stale_against_a_later_quarterly_filing(self):
        d = empty()
        d.latest_filed = date(2026, 9, 26)  # a 10-Q 456 days after the float date: the next float arrives in the next 10-K
        add(d, "public_float", 8_641_564_012, date(2025, 6, 27), None, "Q2", tag="EntityPublicFloat")
        assert not [x for x in currency.check(d) if x.data_point_name == "public_float"]
        add(d, "public_float", 5_000_000_000, date(2023, 6, 30), None, "Q2", tag="EntityPublicFloat")  # 3 years old: truly stale
        d.cells[:] = [c for c in d.cells if c.end != date(2025, 6, 27)]
        assert [x for x in currency.check(d) if x.data_point_name == "public_float"]

    def test_a_quarterly_item_of_the_same_age_is_still_stale(self):
        d = empty()
        d.latest_filed = date(2026, 3, 28)
        add(d, "ppe_net", 5_000_000, date(2025, 6, 27), None, "Q2", tag="PropertyPlantAndEquipmentNet")
        assert [x for x in currency.check(d) if x.data_point_name == "ppe_net"]


# ------------------------------------------------ (5) the suspect quarter is the finding cell
class TestSuspectQuarter:
    def test_odfl_q4_2017_tax_benefit_tagged_as_a_provision_is_the_named_cell(self):
        d = empty()
        fs, fe = date(2017, 1, 1), date(2017, 12, 31)
        add(d, "income_tax_expense", 112_058_000, fe, fs, "FY", tag="IncomeTaxExpenseBenefit")
        for (a, b, fp), v in zip(((date(2017, 1, 1), date(2017, 3, 31), "Q1"), (date(2017, 4, 1), date(2017, 6, 30), "Q2"),
                                  (date(2017, 7, 1), date(2017, 9, 30), "Q3"), (date(2017, 10, 1), date(2017, 12, 31), "Q4")),
                                 (40_000_000, 45_000_000, 44_000_000, 104_900_000)):
            add(d, "income_tax_expense", v, b, a, fp, tag="IncomeTaxExpenseBenefit", form="10-Q")
        f = [x for x in period_integrity.check(d) if x.evidence["rule"] == "quarters_do_not_sum_to_year"]
        assert f and f[0].period_end == date(2017, 12, 31) and f[0].stored_value == D(104_900_000)
        assert f[0].evidence["year_value"] == "112058000" and f[0].evidence["implied_quarter_value"] == "-16942000"

    def test_a_year_on_a_component_tag_stays_the_named_cell(self):
        """TSLA cost of revenue FY2017 rests on CostOfGoodsSold (priority 3, a component): the YEAR is wrong."""
        d = empty()
        d.tag_roles = {("cost_of_revenue", "CostOfRevenue"): (2, "approved"), ("cost_of_revenue", "CostOfGoodsSold"): (3, "provisional")}
        add(d, "cost_of_revenue", 6_724_480_000, date(2017, 12, 31), date(2017, 1, 1), "FY", tag="CostOfGoodsSold", filed=date(2018, 2, 20))
        for (a, b, fp), v in zip(((date(2017, 1, 1), date(2017, 3, 31), "Q1"), (date(2017, 4, 1), date(2017, 6, 30), "Q2"),
                                  (date(2017, 7, 1), date(2017, 9, 30), "Q3"), (date(2017, 10, 1), date(2017, 12, 31), "Q4")),
                                 (2_028_324_000, 2_122_942_000, 2_535_535_000, 2_849_463_000)):
            add(d, "cost_of_revenue", v, b, a, fp, tag="CostOfRevenue", form="10-Q", filed=date(b.year, b.month, 28))
        f = [x for x in period_integrity.check(d) if x.evidence["rule"] == "quarters_do_not_sum_to_year"]
        assert f and f[0].stored_value == D(6_724_480_000)

    def test_a_basis_mix_still_names_the_year(self):
        d = empty()
        fs, fe = date(2015, 7, 1), date(2016, 6, 30)
        add(d, "net_income", 20_539_000_000, fe, fs, "FY", filed=date(2018, 8, 3), accession="fy")
        for (a, b), v in zip(((date(2015, 7, 1), date(2015, 9, 30)), (date(2015, 10, 1), date(2015, 12, 31)), (date(2016, 1, 1), date(2016, 3, 31)),
                              (date(2016, 4, 1), date(2016, 6, 30))), (4_902, 5_018, 3_756, 3_122)):
            add(d, "net_income", v * 1_000_000, b, a, None, form="10-Q", filed=date(b.year, b.month, 28), accession=f"q{b}")
        f = [x for x in period_integrity.check(d) if x.evidence["rule"] == "quarters_vs_year_basis_mix"]
        assert f and f[0].period_end == fe and f[0].stored_value == D(20_539_000_000)


# ------------------------------------------------ (6) TSLA 2015-2016 diluted EPS never adjusted
class TestTslaEarlyEps:
    CASES = (  # (end, start, stored = as filed, right value on today's basis)
        (date(2015, 3, 31), date(2015, 1, 1), "-1.22", "-0.0813"), (date(2015, 6, 30), date(2015, 4, 1), "-1.45", "-0.0967"),
        (date(2015, 6, 30), date(2015, 1, 1), "-2.68", "-0.1787"), (date(2016, 3, 31), date(2016, 1, 1), "-2.13", "-0.142"),
        (date(2016, 6, 30), date(2016, 4, 1), "-2.09", "-0.1393"), (date(2016, 6, 30), date(2016, 1, 1), "-4.22", "-0.2813"),
    )

    def test_each_cell_is_flagged_and_reports_the_right_expected_value(self):
        d = empty()
        d.splits = [(date(2020, 8, 31), D(5)), (date(2022, 8, 25), D(3))]
        for end, start, v, _right in self.CASES:
            cell(d, "diluted_eps_resolved", D(v), D(v), end + (date(2015, 5, 11) - date(2015, 3, 31)), end, start=start)
        f = [x for x in splits.check(d) if x.evidence["rule"] == "share_basis_mismatch"]
        assert len(f) == 6 and all(x.severity == WRONG_VALUE for x in f)
        for x, (_e, _s, _v, right) in zip(sorted(f, key=lambda x: (x.period_end, x.stored_value)), sorted(self.CASES, key=lambda c: (c[0], D(c[2])))):
            assert abs(x.expected_or_other_value - D(right)) < D("0.001"), (x.period_end, x.expected_or_other_value, right)
