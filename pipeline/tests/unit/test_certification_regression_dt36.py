"""Regression set built from the Verifier's filing-checked verdicts (data-team/36,
2026-10-21): every CONFIRMED defect must be caught by the rule that names it, and
every REFUTED finding (value right, coincidence, basis mix between two defensible
readings, lineage only) must NOT fire as `wrong_value`. Fixtures use the filed
numbers of the cases; dates of the filings are the real ones where the verdict
depends on them (vintage = filing date).
"""

from datetime import date
from decimal import Decimal

import pytest
from certification_fixtures import D, QUARTERS, add, clean_company, src

from scrooner_pipeline.certification import (
    composition, period_integrity, scale, source_integrity, splits,
)
from scrooner_pipeline.certification.model import REVIEW, WRONG_VALUE, CompanyData


def by_rule(findings, severity=None):
    out = {}
    for f in findings:
        if severity is None or f.severity == severity:
            out.setdefault(f.evidence["rule"], []).append(f)
    return out


def empty(cid=9):
    d = CompanyData(company_id=cid, ticker="T", as_of=date(2026, 10, 21))
    d.latest_filed = date(2026, 6, 30)
    return d


def fy(year):
    return date(year, 1, 1), date(year, 12, 31)


# ------------------------------------------------ item 1: MSFT restatement basis mix
class TestMsftBasisMix:
    def company(self, fy_filed, q_filed_days=40):
        d = empty()
        fs, fe = date(2015, 7, 1), date(2016, 6, 30)
        add(d, "net_income", 20_539_000_000, fe, fs, "FY", filed=fy_filed, accession="fy-filing")
        qs = [(date(2015, 7, 1), date(2015, 9, 30)), (date(2015, 10, 1), date(2015, 12, 31)),
              (date(2016, 1, 1), date(2016, 3, 31)), (date(2016, 4, 1), date(2016, 6, 30))]
        for (a, b), v in zip(qs, [4_902, 5_018, 3_756, 3_122]):
            add(d, "net_income", v * 1_000_000, b, a, None, form="10-Q", filed=date(b.year, b.month, 28) if q_filed_days else b,
                accession=f"q-{b}")
        return d

    def test_restated_year_vs_original_quarters_is_basis_mix_review(self):
        f = period_integrity.check(self.company(fy_filed=date(2018, 8, 3)))
        r = by_rule(f)
        assert "quarters_vs_year_basis_mix" in r and "quarters_do_not_sum_to_year" not in r
        assert all(x.severity == REVIEW for x in r["quarters_vs_year_basis_mix"])

    def test_same_vintage_year_with_wrong_quarters_stays_wrong_value(self):
        """TSLA FY2017 cost of revenue: FY from the FY2017 10-K, quarters from the 10-Qs, 25% apart."""
        f = period_integrity.check(self.company(fy_filed=date(2016, 8, 1)))
        assert "quarters_do_not_sum_to_year" in by_rule(f, WRONG_VALUE)


# ------------------------------------------------ item 2: JPM / MA proxy net income
class TestProxyNetIncome:
    def cell(self, d, stored, copy):
        proxy = src("NetIncomeLoss", stored, form="DEF 14A", sid=7001, auth=False)
        d.periodic_copies[7001] = [src("NetIncomeLoss", copy, form="10-K", sid=7002)]
        add(d, "net_income_resolved", stored, date(2021, 12, 31), date(2021, 1, 1), "FY", sources=[proxy])

    def test_jpm_rounded_proxy_value_differs_from_the_10k_copy_is_wrong_value(self):
        d = empty()
        self.cell(d, 48_300_000_000, 48_334_000_000)
        assert "non_periodic_form" in by_rule(source_integrity.check(d), WRONG_VALUE)

    def test_ma_proxy_value_identical_to_the_10k_is_lineage_review(self):
        d = empty()
        self.cell(d, 8_687_000_000, 8_687_000_000)
        r = by_rule(source_integrity.check(d))
        assert "non_periodic_form" in r and all(x.severity == REVIEW for x in r["non_periodic_form"])
        assert not by_rule(source_integrity.check(d), WRONG_VALUE).get("non_periodic_form")

    def test_jpm_q4_derived_from_the_proxy_year_differs_from_the_correct_derived_copy(self):
        d = empty()
        derived = src("NetIncomeLoss", 12_977_000_000, form="DEF 14A", derived=True, sid=7011, auth=False)
        d.periodic_copies[7011] = [src("NetIncomeLoss", 13_025_000_000, form="10-K", derived=True, sid=7012)]
        add(d, "net_income", 12_977_000_000, date(2025, 12, 31), date(2025, 10, 1), "Q4", sources=[derived])
        assert "non_periodic_form" in by_rule(source_integrity.check(d), WRONG_VALUE)

    def test_schw_thousands_stored_as_dollars_differs_from_the_10k_copy(self):
        d = empty()
        self.cell(d, 8_852_000, 8_852_000_000)
        assert "non_periodic_form" in by_rule(source_integrity.check(d), WRONG_VALUE)


# ------------------------------------------------ item 7: 8-K lineage vs mixed vintage
class TestEightKLineage:
    def test_single_input_8k_value_equal_to_the_periodic_copy_is_review_only(self):
        """MSFT FY2015 revenue 93,580M, AVGO FY2017 operating income, LLY 2017 revenue: right as filed."""
        for value in (93_580_000_000, 2_371_000_000, 4_514_900_000):
            d = empty()
            s = src("Revenues", value, form="8-K", sid=7101)
            d.periodic_copies[7101] = [src("Revenues", value, form="10-K", sid=7102)]
            add(d, "revenue_sanity_resolved", value, date(2017, 3, 31), date(2017, 1, 1), "Q1", sources=[s], form="8-K")
            r = by_rule(source_integrity.check(d))
            assert not by_rule(source_integrity.check(d), WRONG_VALUE).get("non_periodic_form"), value
            assert r["non_periodic_form"][0].severity == REVIEW

    def test_lly_gross_profit_from_8k_revenue_minus_original_cogs_is_mixed_vintage(self):
        d = empty()
        add(d, "gross_profit_resolved", 12_657_900_000, date(2016, 12, 31), date(2016, 1, 1), "FY",
            sources=[src("Revenues", 18_312_800_000, form="8-K", sid=7111), src("CostOfRevenue", 5_654_900_000, form="10-K", sid=7112)])
        assert "mixed_vintage" in by_rule(source_integrity.check(d), WRONG_VALUE)

    def test_lly_cell_with_only_8k_inputs_is_not_mixed(self):
        d = empty()
        add(d, "gross_profit_resolved", 14_152_300_000, date(2016, 12, 31), date(2016, 1, 1), "FY",
            sources=[src("Revenues", 18_312_800_000, form="8-K", sid=7121), src("CostOfRevenue", 4_160_500_000, form="8-K", sid=7122)])
        assert "mixed_vintage" not in by_rule(source_integrity.check(d))

    def test_tsla_operating_income_arithmetic_is_not_compared_with_one_input_copy(self):
        d = empty()
        src_ids = [src("Revenues", 11_758_751_000, auth=False, sid=7131), src("CostOfGoodsSold", 6_724_480_000, sid=7132),
                   src("OperatingExpenses", 3_854_573_000, sid=7133)]
        d.authoritative_copies[7131] = [src("Revenues", 11_759_000_000, sid=7134)]
        add(d, "operating_income_resolved", 1_179_271_000, date(2017, 12, 31), date(2017, 1, 1), "FY", sources=src_ids)
        assert "differs_from_authoritative_copy" not in by_rule(source_integrity.check(d))


# ------------------------------------------------ label shift: coincidence vs same filing
class TestLabelShift:
    def ytd_company(self, q_acc, w_acc, q_value=64_000_000):
        d = empty()
        add(d, "income_tax_expense", 0, date(2020, 1, 26), date(2019, 10, 28), "Q4", tag="IncomeTaxExpenseBenefit", form="10-Q", accession="x0")
        add(d, "income_tax_expense", 5_000_000, date(2020, 7, 26), date(2020, 4, 27), "Q2", tag="IncomeTaxExpenseBenefit", form="10-Q", accession="x1")
        add(d, "income_tax_expense", q_value, date(2020, 4, 26), date(2020, 1, 27), "Q1", tag="IncomeTaxExpenseBenefit", form="10-Q", accession=q_acc)
        add(d, "income_tax_expense", q_value, date(2020, 10, 25), date(2020, 1, 27), None, tag="IncomeTaxExpenseBenefit", form="10-Q", accession=w_acc)
        return d

    def test_nvda_tax_q1_equals_9m_by_coincidence_across_two_filings_is_not_flagged(self):
        f = period_integrity.check(self.ytd_company("10q-q1", "10q-q3"))
        assert "quarter_equals_longer_window" not in by_rule(f)

    def test_same_filing_same_tag_two_contexts_with_equal_value_is_wrong_value(self):
        """AMD Q2 2023 buybacks: the 3-month block of the Q2 10-Q prints the 6-month figure."""
        f = period_integrity.check(self.ytd_company("10q-q2", "10q-q2"))
        assert "quarter_equals_longer_window" in by_rule(f, WRONG_VALUE)


# ------------------------------------------------ item 4: R-RATE-ON-YTD (Visa) and DPS review
def dps_year(d, year, rate, *, fy_value, q4, derived_q4=True, ytd=None):
    fs, fe = date(year, 1, 1), date(year, 12, 31)
    for (a, b, label), v in zip([(date(year, 1, 1), date(year, 3, 31), "Q1"), (date(year, 4, 1), date(year, 6, 30), "Q2"),
                                  (date(year, 7, 1), date(year, 9, 30), "Q3")], [rate] * 3):
        add(d, "dividends_per_share", v, b, a, label, tag="CommonStockDividendsPerShareDeclared", unit="usd/shares", form="10-Q")
    add(d, "dividends_per_share", q4, date(year, 12, 31), date(year, 10, 1), "Q4", tag="CommonStockDividendsPerShareDeclared",
        unit="usd/shares", derived=derived_q4)
    add(d, "dividends_per_share", fy_value, fe, fs, "FY", tag="CommonStockDividendsPerShareDeclared", unit="usd/shares")
    if ytd is not None:
        add(d, "dividends_per_share", ytd, date(year, 9, 30), fs, None, tag="CommonStockDividendsPerShareDeclared", unit="usd/shares", form="10-Q")


class TestRateOnYtd:
    def test_visa_year_holds_the_quarterly_rate_and_the_derived_q4_is_negative(self):
        d = empty()
        dps_year(d, 2025, D("0.59"), fy_value=D("0.59"), q4=D("-1.18"), ytd=D("0.59"))
        flagged = composition.dps_rate_on_ytd(d)
        assert len(flagged) == 3  # FY cell, 9M YTD cell, derived Q4
        rules_ = by_rule(composition.check(d), WRONG_VALUE)
        assert len(rules_["dps_rate_on_ytd"]) == 3 and "per_share_derived_by_subtraction" in rules_

    def test_visa_derived_zero_quarter_is_flagged(self):
        d = empty()
        dps_year(d, 2016, D("0.14"), fy_value=D("0.14"), q4=D("0"))
        assert any(c for c in composition.dps_rate_on_ytd(d).values() if "derived" in c["reason"])

    def test_apple_style_dps_derived_q4_is_review_not_wrong_value(self):
        """Apple Q4 FY2021 0.22: declared dividends add up; FY 0.88 is four times the rate."""
        d = empty()
        dps_year(d, 2021, D("0.22"), fy_value=D("0.88"), q4=D("0.22"))
        assert composition.dps_rate_on_ytd(d) == {}
        f = [x for x in composition.check(d) if x.evidence["rule"] == "per_share_derived_by_subtraction"]
        assert f and all(x.severity == REVIEW for x in f)

    def test_nvda_negative_derived_q4_against_positive_filed_quarters(self):
        d = empty()
        for (a, b, label), v in zip([(date(2015, 2, 1), date(2015, 4, 30), "Q1"), (date(2015, 5, 1), date(2015, 7, 31), "Q2"),
                                      (date(2015, 8, 1), date(2015, 10, 31), "Q3")], [D("0.085"), D("0.0975"), D("0.0975")]):
            add(d, "dividends_per_share", v, b, a, label, tag="CommonStockDividendsPerShareDeclared", unit="usd/shares", form="10-Q")
        add(d, "dividends_per_share", D("-0.165"), date(2016, 1, 31), date(2015, 11, 1), "Q4", tag="CommonStockDividendsPerShareDeclared",
            unit="usd/shares", derived=True)
        add(d, "dividends_per_share", D("0.4"), date(2016, 1, 31), date(2015, 2, 1), "FY", tag="CommonStockDividendsPerShareDeclared", unit="usd/shares")
        assert "dps_rate_on_ytd" in by_rule(composition.check(d), WRONG_VALUE)

    def test_eps_and_tax_rate_by_subtraction_stay_wrong_value_tax_rate_is_labelled_method_policy(self):
        d = empty()
        add(d, "diluted_eps", D("1.23"), date(2021, 9, 25), date(2021, 6, 27), "Q4", tag="EarningsPerShareDiluted", unit="usd/shares", derived=True)
        add(d, "effective_tax_rate_reported", D("-1.464"), date(2018, 6, 30), date(2018, 4, 1), "Q4", tag="EffectiveIncomeTaxRateContinuingOperations", unit="pure", derived=True)
        f = {x.data_point_name: x for x in composition.check(d) if x.evidence["rule"] == "per_share_derived_by_subtraction"}
        assert f["diluted_eps"].severity == WRONG_VALUE and f["diluted_eps"].evidence["method_policy"] is False
        assert f["effective_tax_rate_reported"].severity == WRONG_VALUE and f["effective_tax_rate_reported"].evidence["method_policy"] is True


# ------------------------------------------------ items 3 and 8: share basis runs
def eps_series(d, years, ni, shares_by_year, *, dps_by_year=None):
    for y in years:
        fs, fe = fy(y)
        add(d, "net_income", ni[y], fe, fs, "FY", tag="NetIncomeLoss")
        add(d, "diluted_eps", D(ni[y]) / shares_by_year[y], fe, fs, "FY", tag="EarningsPerShareDiluted", unit="usd/shares")
        add(d, "basic_eps", D(ni[y]) / shares_by_year[y] * D("1.01"), fe, fs, "FY", tag="EarningsPerShareBasic", unit="usd/shares")
        if dps_by_year:
            add(d, "dividends_per_share", dps_by_year[y], fe, fs, "FY", tag="CommonStockDividendsPerShareDeclared", unit="usd/shares")
        add(d, "shares_outstanding", shares_by_year[y], fe, None, "FY", tag="CommonStockSharesOutstanding", unit="shares")


class TestShareBasis:
    def nvda(self):
        d = empty()
        years = list(range(2016, 2026))
        ni = {y: 1_000_000_000 * (y - 2014) for y in years}
        old = D(2_500_000_000)
        shares = {y: (old if y <= 2023 else old * 10) for y in years}  # the 10-for-1 of 2024 never applied to the older run
        eps_series(d, years, ni, shares, dps_by_year={y: D("0.16") if y <= 2023 else D("0.016") for y in years})
        return d

    def test_nvda_every_cell_before_the_missing_split_is_flagged(self):
        d = self.nvda()
        f = [x for x in splits.check(d) if x.evidence["rule"] == "share_basis_mismatch"]
        flagged = {(x.data_point_name, x.period_end.year) for x in f}
        for y in range(2016, 2024):
            for name in ("diluted_eps", "basic_eps", "shares_outstanding", "dividends_per_share"):
                assert (name, y) in flagged, (name, y)
        assert all(y >= 2016 and y <= 2023 for _n, y in flagged)  # the current-basis run is untouched
        assert all(x.severity == WRONG_VALUE and x.evidence["clean_ratio"] == 10 for x in f)

    def test_repaired_series_on_one_basis_is_clean(self):
        d = empty()
        years = list(range(2016, 2026))
        ni = {y: 1_000_000_000 * (y - 2014) for y in years}
        eps_series(d, years, ni, {y: D(25_000_000_000) for y in years})
        assert [x for x in splits.check(d) if x.evidence["rule"] == "share_basis_mismatch"] == []

    def test_aapl_fy2018_eps_11_91_is_an_isolated_run_on_the_old_basis(self):
        d = empty()
        years = list(range(2015, 2022))
        ni = {2015: 53_394e6, 2016: 45_687e6, 2017: 48_351e6, 2018: 59_531e6, 2019: 55_256e6, 2020: 57_411e6, 2021: 94_680e6}
        sh = {2015: 22.3e9, 2016: 21.4e9, 2017: 20.5e9, 2018: 20.0e9, 2019: 18.6e9, 2020: 17.5e9, 2021: 16.9e9}
        eps_series(d, years, {y: D(int(v)) for y, v in ni.items()}, {y: D(int(v)) for y, v in sh.items()})
        # FY2018 diluted EPS was never adjusted for the 2020 4-for-1: 11.91 instead of 2.98
        for c in list(d.cells):
            if c.concept == "diluted_eps" and c.end.year == 2018:
                d.cells.remove(c)
        add(d, "diluted_eps", D("11.91"), date(2018, 12, 31), date(2018, 1, 1), "FY", tag="EarningsPerShareDiluted", unit="usd/shares")
        f = [x for x in splits.check(d) if x.evidence["rule"] == "share_basis_mismatch"]
        assert {(x.data_point_name, x.period_end.year) for x in f} == {("diluted_eps", 2018), ("basic_eps", 2018)}

    def test_aapl_share_counts_before_the_2020_split_are_flagged(self):
        d = empty()
        for i, y in enumerate(range(2015, 2024)):
            end = date(y, 9, 26)
            value = D(5_578_753_000) if y <= 2019 else D(16_976_763_000)
            add(d, "shares_outstanding", value * (1 if y <= 2019 else 1) - D(i * 10_000_000) , end, None, "FY", tag="CommonStockSharesOutstanding", unit="shares")
        f = [x for x in splits.check(d) if x.evidence["rule"] == "share_basis_mismatch"]
        assert {x.period_end.year for x in f} == {2015, 2016, 2017, 2018, 2019}

    def test_split_counted_twice_in_the_table(self):
        d = empty()
        d.splits = [(date(2021, 6, 3), D(4)), (date(2021, 7, 19), D(4))]  # NVDA: the same split 46 days apart
        assert "split_ratio_counted_twice" in by_rule(splits.check(d), REVIEW)
        d.splits = [(date(2021, 6, 3), D(4)), (date(2022, 7, 19), D(4))]
        assert "split_ratio_counted_twice" not in by_rule(splits.check(d))

    def test_wmt_sign_flip_to_a_smaller_loss_is_not_a_basis_mix(self):
        d = empty()
        for (a, b, label), v in zip(QUARTERS, [D("0.55"), D("0.50"), D("0.47"), D("-0.2467")]):
            add(d, "basic_eps", v, b, a, label, tag="EarningsPerShareBasic", unit="usd/shares", derived=(label == "Q4"))
        assert "per_share_basis_mix" not in by_rule(splits.check(d))


# ------------------------------------------------ R-STATEMENT-ROLE: EMR, NTAP, JNJ
def revenue_history(d, values, base_values=None):
    for y, v in values.items():
        fs, fe = fy(y)
        add(d, "revenue_sanity_resolved", v, fe, fs, "FY", tag="Revenues")
        add(d, "revenue", (base_values or values)[y], fe, fs, "FY", tag="RevenueFromContractWithCustomerExcludingAssessedTax")


class TestStatementRole:
    def test_emr_fy2022_acquiree_revenue_is_wrong_value(self):
        d = empty()
        vals = {2018: 17.4e9, 2019: 18.4e9, 2020: 16.8e9, 2021: 12.7e9, 2022: 13.8e9, 2023: 15.2e9, 2024: 17.5e9}
        base = {y: D(int(v)) for y, v in vals.items()}
        res = dict(base)
        res[2022] = D(1_660_000_000)
        revenue_history(d, res, base)
        add(d, "net_income", D(2_000_000_000), date(2022, 12, 31), date(2022, 1, 1), "FY", tag="NetIncomeLoss")
        f = [x for x in scale.check(d) if x.evidence["rule"] == "statement_role_suspect"]
        assert len(f) == 1 and f[0].severity == WRONG_VALUE and f[0].period_end.year == 2022
        assert {"neighbours", "layer", "margins"} <= set(f[0].evidence["signals"])

    def test_ntap_segment_total_on_the_consolidated_tag_is_review(self):
        d = empty()
        base = {2022: D(6_318_000_000), 2023: D(6_362_000_000), 2024: D(6_268_000_000), 2025: D(6_572_000_000), 2026: D(6_925_000_000)}
        res = {2022: base[2022], 2023: base[2023], 2024: D(5_657_000_000), 2025: D(5_907_000_000), 2026: D(6_237_000_000)}
        revenue_history(d, res, base)
        f = [x for x in scale.check(d) if x.evidence["rule"] == "statement_role_suspect"]
        assert {x.period_end.year for x in f} == {2024, 2025, 2026} and all(x.severity == REVIEW for x in f)

    def test_clean_revenue_history_is_silent(self):
        d = empty()
        vals = {y: D(int(10e9 + 1e9 * (y - 2018))) for y in range(2018, 2025)}
        revenue_history(d, vals)
        assert [x for x in scale.check(d) if x.evidence["rule"] == "statement_role_suspect"] == []

    def test_jnj_rd_is_the_cash_flow_addback_for_fy2021_to_fy2025(self):
        d = empty()
        years = list(range(2015, 2026))
        rev = {y: D(int(70e9 + 1.5e9 * (y - 2015))) for y in years}
        for y in years:
            fs, fe = fy(y)
            add(d, "revenue", rev[y], fe, fs, "FY", tag="RevenueFromContractWithCustomerExcludingAssessedTax")
        rd = {2015: 9.0e9, 2016: 9.1e9, 2017: 10.8e9, 2018: 10.6e9, 2019: 11.4e9, 2020: 12.2e9, 2021: 0, 2022: 0, 2023: 483e6, 2024: 1841e6, 2025: 109e6}
        for y, v in rd.items():
            fs, fe = fy(y)
            add(d, "research_and_development", D(int(v)), fe, fs, "FY", tag="ResearchAndDevelopmentExpense")
        f = [x for x in scale.check(d) if x.evidence["rule"] == "statement_role_suspect" and x.severity == WRONG_VALUE]
        assert {x.period_end.year for x in f} >= {2021, 2022, 2025}
        assert not {x.period_end.year for x in f} & {2015, 2016, 2017, 2018}  # the real R&D years stay silent


class TestAnnualDividendIsNotARate:
    def test_wmt_annual_dividend_declared_once_equals_the_year_value_and_is_not_flagged(self):
        """WMT declares one annual dividend: Q1 = 6M = 9M = FY = 0.68 and derived quarters are 0.
        DPS x (net income / EPS) over dividends paid is about 1, so it is a full-year total."""
        d = empty()
        fs, fe = date(2017, 2, 1), date(2018, 1, 31)
        add(d, "net_income", D(10_000_000_000), fe, fs, "FY", tag="NetIncomeLoss")
        add(d, "diluted_eps", D("3.3"), fe, fs, "FY", tag="EarningsPerShareDiluted", unit="usd/shares")
        add(d, "dividends_paid", D(2_060_000_000), fe, fs, "FY", tag="PaymentsOfDividends")  # 0.68 x ~3.03B shares
        add(d, "dividends_per_share", D("0.68"), fe, fs, "FY", tag="CommonStockDividendsPerShareDeclared", unit="usd/shares")
        add(d, "dividends_per_share", D("0.68"), date(2017, 4, 30), fs, "Q1", tag="CommonStockDividendsPerShareDeclared", unit="usd/shares", form="10-Q")
        add(d, "dividends_per_share", D("0.68"), date(2017, 7, 31), fs, None, tag="CommonStockDividendsPerShareDeclared", unit="usd/shares", form="10-Q")
        add(d, "dividends_per_share", D("0.68"), date(2017, 10, 31), fs, None, tag="CommonStockDividendsPerShareDeclared", unit="usd/shares", form="10-Q")
        assert composition.dps_rate_on_ytd(d) == {}

    def test_the_same_shape_with_dividends_paid_four_times_larger_is_a_rate(self):
        d = empty()
        fs, fe = date(2017, 2, 1), date(2018, 1, 31)
        add(d, "net_income", D(10_000_000_000), fe, fs, "FY", tag="NetIncomeLoss")
        add(d, "diluted_eps", D("3.3"), fe, fs, "FY", tag="EarningsPerShareDiluted", unit="usd/shares")
        add(d, "dividends_paid", D(8_240_000_000), fe, fs, "FY", tag="PaymentsOfDividends")
        add(d, "dividends_per_share", D("0.68"), fe, fs, "FY", tag="CommonStockDividendsPerShareDeclared", unit="usd/shares")
        add(d, "dividends_per_share", D("0.68"), date(2017, 4, 30), fs, "Q1", tag="CommonStockDividendsPerShareDeclared", unit="usd/shares", form="10-Q")
        add(d, "dividends_per_share", D("0.68"), date(2017, 7, 31), fs, None, tag="CommonStockDividendsPerShareDeclared", unit="usd/shares", form="10-Q")
        assert len(composition.dps_rate_on_ytd(d)) == 2  # the FY cell and the 6M YTD cell


class TestProxyRoundingVersusRecast:
    def test_lly_recast_revenue_differs_from_the_original_copy_by_7_percent_is_review(self):
        d = empty()
        s = src("Revenues", 4_514_900_000, form="8-K", sid=7201)
        d.periodic_copies[7201] = [src("Revenues", 4_865_100_000, form="10-Q", sid=7202)]
        add(d, "revenue_sanity_resolved", 4_514_900_000, date(2017, 3, 31), date(2017, 1, 1), "Q1", sources=[s], form="8-K")
        f = [x for x in source_integrity.check(d) if x.evidence["rule"] == "non_periodic_form"]
        assert f and all(x.severity == REVIEW for x in f)

    def test_the_base_layer_of_a_proxy_cell_is_checked_too(self):
        """JPM: both net_income and net_income_resolved hold the rounded proxy value."""
        d = empty()
        for name in ("net_income", "net_income_resolved"):
            s = src("NetIncomeLoss", 48_300_000_000, form="DEF 14A", sid=7211 if name == "net_income" else 7213)
            d.periodic_copies[s.id] = [src("NetIncomeLoss", 48_334_000_000, form="10-K", sid=s.id + 1)]
            add(d, name, 48_300_000_000, date(2021, 12, 31), date(2021, 1, 1), "FY", sources=[s])
        f = [x for x in source_integrity.check(d) if x.evidence["rule"] == "non_periodic_form" and x.severity == WRONG_VALUE]
        assert {x.data_point_name for x in f} == {"net_income", "net_income_resolved"}


class TestLayerSignAndJump:
    def test_tsla_resolved_operating_income_positive_against_a_negative_base(self):
        d = empty()
        add(d, "operating_income", -1_632_086_000, date(2017, 12, 31), date(2017, 1, 1), "FY", tag="OperatingIncomeLoss")
        add(d, "operating_income_resolved", 1_179_271_000, date(2017, 12, 31), date(2017, 1, 1), "FY", tag="Revenues")
        f = [x for x in scale.check(d) if x.evidence["rule"] == "layer_sign_conflict"]
        assert f and f[0].severity == WRONG_VALUE and f[0].data_point_name == "operating_income_resolved"

    def test_share_jump_points_at_the_older_cell(self):
        """NVDA: 24.53B on 2024-08-23 is right; 2.46B on 2024-05-24 is on the old basis."""
        d = empty()
        add(d, "shares_outstanding", 2_460_000_000, date(2024, 5, 24), None, "Q1", tag="CommonStockSharesOutstanding", unit="shares")
        add(d, "shares_outstanding", 24_530_000_000, date(2024, 8, 23), None, "Q2", tag="CommonStockSharesOutstanding", unit="shares")
        f = [x for x in splits.check(d) if x.evidence["rule"] == "share_jump_without_split"]
        assert f and f[0].period_end == date(2024, 5, 24) and f[0].evidence["newer_period_end"] == "2024-08-23"
