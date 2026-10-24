"""Regression set, round 4: PRECISION fixes after the Verifier's validation on fresh shards
(data-team/strategy/team/CERTIFY-ROUND3-VALIDATION-2026-10-23.md). The suite is frozen after
this round.

TRAINING cells (named failing cells in that report; the only cells used to design a fix):
  INCY 2024 self-tender, STE Cantel acquisition shares, TER (no event), DOCU IPO preferred
  conversion  -> every inferred split needs restated per-share comparatives
  SPGI gross profit (0/10 right)                       -> newer filing alone reproduces the value
  ILMN redeemable NCI, SWK 2021 assets - equity + NCI  -> liabilities_nci_*
  SWK Q1 2017 revenue (= Q1 2019)                      -> quarter_label_shift
  AZO 1998-2015 cumulative buyback                     -> non-standard windows dropped
  FIX 2017-03-31 total debt (the dip is real)          -> debt_isolated_dip materiality guard
HELD OUT of this round: every other cell of the fresh frames (S025, S044, S058).
"""

from datetime import date
from decimal import Decimal

import pytest
from certification_fixtures import D, add, src

from scrooner_pipeline.certification import (
    composition,
    loader,
    period_integrity,
    source_integrity,
    splits,
    ties,
)
from scrooner_pipeline.certification.model import (
    CompanyData,
    ComponentFact,
    WRONG_VALUE,
)


def empty():
    d = CompanyData(company_id=21, ticker="T", as_of=date(2026, 10, 23))
    d.latest_filed = date(2026, 6, 30)
    return d


def rules(findings, severity=None):
    return {
        f.evidence["rule"]
        for f in findings
        if severity is None or f.severity == severity
    }


def shares(d, series):
    for filed, end, n in series:
        s = src(
            "CommonStockSharesOutstanding", n, unit="shares", filed=filed, form="10-Q"
        )
        add(d, "shares_outstanding", n, end, None, "Q", sources=[s])


def eps_no_restatement(d):
    """EPS cells whose comparatives were never restated: one source each."""
    for filed, end, start, v in (
        (date(2018, 6, 12), date(2018, 4, 30), date(2018, 2, 1), "-0.66"),
        (date(2019, 3, 20), date(2019, 1, 31), date(2018, 2, 1), "-1.10"),
    ):
        s = src(
            "EarningsPerShareBasicAndDiluted",
            D(v),
            unit="usd/shares",
            filed=filed,
            form="10-Q",
        )
        add(d, "diluted_eps", D(v), end, start, "Q", sources=[s])


# ------------------------------------------------ (1) every inferred split needs the proof
class TestInferredSplitsNeedRestatedComparatives:
    def test_docu_ipo_preferred_conversion_four_fold_step_is_not_a_split(self):
        d = empty()
        shares(
            d,
            [
                (date(2018, 3, 12), date(2018, 1, 31), 36_775_658),
                (date(2018, 6, 12), date(2018, 4, 30), 156_600_000),
                (date(2018, 9, 11), date(2018, 7, 31), 158_000_000),
            ],
        )
        eps_no_restatement(d)
        assert not splits.split_events(d)[0]
        assert not [
            x for x in splits.check(d) if x.evidence["rule"] == "share_basis_mismatch"
        ]

    def test_incy_self_tender_that_shrinks_the_cover_count_by_a_fifth_is_not_a_split(
        self,
    ):
        d = empty()
        shares(
            d,
            [
                (date(2024, 4, 25), date(2024, 3, 31), 240_000_000),
                (date(2024, 8, 1), date(2024, 6, 30), 196_300_000),
                (date(2024, 10, 31), date(2024, 9, 30), 196_000_000),
            ],
        )
        eps_no_restatement(d)
        assert not splits.split_events(d)[0]

    def test_ter_two_fold_step_with_no_event_and_ste_acquisition_shares_are_not_splits(
        self,
    ):
        for series in (
            (
                (date(2015, 4, 20), date(2015, 3, 31), 100_000_000),
                (date(2015, 8, 1), date(2015, 6, 30), 200_000_000),
                (date(2015, 11, 1), date(2015, 9, 30), 201_000_000),
            ),
            (
                (date(2021, 1, 20), date(2020, 12, 31), 85_300_000),
                (date(2021, 5, 5), date(2021, 3, 31), 99_800_000),
                (date(2021, 8, 5), date(2021, 6, 30), 100_000_000),
            ),
        ):
            d = empty()
            shares(d, series)
            eps_no_restatement(d)
            assert not splits.split_events(d)[0]

    def test_a_real_integer_split_with_restated_comparatives_is_still_inferred(self):
        d = empty()
        shares(
            d,
            [
                (date(2023, 8, 25), date(2023, 7, 30), 2_470_000_000),
                (date(2024, 8, 28), date(2024, 7, 28), 24_530_000_000),
                (date(2025, 2, 26), date(2025, 1, 26), 24_400_000_000),
            ],
        )
        two = [
            src(
                "EarningsPerShareDiluted",
                D("0.25"),
                unit="usd/shares",
                filed=date(2023, 8, 25),
                form="10-Q",
            ),
            src(
                "EarningsPerShareDiluted",
                D("0.025"),
                unit="usd/shares",
                filed=date(2024, 8, 28),
                form="10-Q",
            ),
        ]
        add(
            d,
            "diluted_eps",
            D("0.025"),
            date(2023, 7, 30),
            date(2023, 5, 1),
            "Q2",
            sources=two,
        )
        assert [(e.kind, e.ratio) for e in splits.split_events(d)[0]] == [
            ("inferred", D(10))
        ]

    def test_unchanged_comparatives_prove_nothing_a_step_of_0_855_with_pairs_at_1_0_is_not_a_split(
        self,
    ):
        """INCY: the cover count fell to 0.855x (self-tender) and every per-share comparative is UNCHANGED (older/newer = 1.0)."""
        d = empty()
        shares(
            d,
            [
                (date(2024, 4, 30), date(2024, 3, 31), 240_000_000),
                (date(2024, 7, 30), date(2024, 6, 30), 205_300_000),
            ],
        )
        for n, (filed, value) in enumerate(
            ((date(2024, 2, 13), "2.55"), (date(2024, 7, 30), "2.55"))
        ):
            s = src(
                "EarningsPerShareBasic",
                D(value),
                unit="usd/shares",
                filed=filed,
                form="10-Q",
                sid=9690 + n,
            )
            if n == 0:
                first = s
        add(
            d,
            "basic_eps",
            D("2.55"),
            date(2023, 12, 31),
            date(2023, 1, 1),
            "FY",
            sources=[
                src(
                    "EarningsPerShareBasic",
                    D("2.55"),
                    unit="usd/shares",
                    filed=date(2024, 2, 13),
                    form="10-K",
                    sid=9691,
                ),
                src(
                    "EarningsPerShareBasic",
                    D("2.55"),
                    unit="usd/shares",
                    filed=date(2024, 7, 30),
                    form="10-Q",
                    sid=9692,
                ),
            ],
        )
        assert not splits.split_events(d)[0]


# ------------------------------------------------ (2) the newer filing alone reproduces the value
class TestSpgiGrossProfit:
    def cell(self, revenue_copy=None):
        d = empty()
        rev = src(
            "Revenues", 3_491_000_000, form="10-Q", sid=9701, filed=date(2024, 4, 30)
        )
        exp = src(
            "CostOfRevenue",
            1_111_000_000,
            form="10-Q",
            sid=9702,
            filed=date(2025, 5, 1),
        )
        d.conflict_copies[9702] = [
            src(
                "CostOfRevenue",
                1_120_000_000,
                form="10-Q",
                sid=9703,
                filed=date(2024, 4, 30),
            )
        ]
        if revenue_copy is not None:
            d.conflict_copies[9701] = [revenue_copy]
        add(
            d,
            "gross_profit_resolved",
            2_380_000_000,
            date(2024, 3, 31),
            date(2024, 1, 1),
            None,
            sources=[rev, exp],
            form="10-Q",
        )
        return d

    def test_revenue_unchanged_between_vintages_so_the_later_10q_alone_gives_the_stored_value(
        self,
    ):
        assert "cross_vintage_arithmetic" not in rules(
            source_integrity.check(self.cell())
        )

    def test_the_same_with_an_explicit_identical_revenue_copy_is_also_silent(self):
        c = src(
            "Revenues", 3_491_000_000, form="10-Q", sid=9704, filed=date(2025, 5, 1)
        )
        assert "cross_vintage_arithmetic" not in rules(
            source_integrity.check(self.cell(c))
        )

    def test_when_revenue_was_recast_too_the_mix_is_still_wrong(self):
        c = src(
            "Revenues", 3_520_000_000, form="10-Q", sid=9705, filed=date(2025, 5, 1)
        )
        assert "cross_vintage_arithmetic" in rules(
            source_integrity.check(self.cell(c)), WRONG_VALUE
        )


# ------------------------------------------------ (3) liabilities and noncontrolling interests
class TestLiabilitiesNci:
    def test_ilmn_redeemable_nci_comes_from_the_period_facts_not_only_the_cell_sources(
        self,
    ):
        d = empty()
        end = date(2016, 7, 3)
        add(
            d,
            "total_liabilities_resolved",
            2_013_460_000,
            end,
            None,
            "Q2",
            sources=[
                src("Assets", 3_985_090_000, sid=9801),
                src("StockholdersEquity", 2_139_912_000, sid=9802),
            ],
        )
        cell = d.cells[-1]
        d.adjustment_facts = [
            ComponentFact(
                1,
                "RedeemableNoncontrollingInterestEquityCarryingAmount",
                D(33_733_000),
                cell.period_id,
                end,
            )
        ]
        f = [
            x
            for x in ties.check(d)
            if x.invariant == "I1" and x.evidence["rule"].startswith("liabilities_nci")
        ]
        assert (
            f
            and f[0].severity == WRONG_VALUE
            and f[0].expected_or_other_value == D(1_811_445_000)
        )

    def test_the_plural_temporary_equity_tag_ilmn_files_is_a_claim_too(self):
        from scrooner_pipeline.certification.model import NCI_CLAIM_TAGS

        assert (
            "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests"
            in NCI_CLAIM_TAGS
        )

    def test_ilmn_with_the_minority_interest_and_the_temporary_equity_both_subtracted(
        self,
    ):
        d = empty()
        end = date(2016, 7, 3)
        add(
            d,
            "total_liabilities_resolved",
            2_013_460_000,
            end,
            None,
            "Q2",
            sources=[
                src("Assets", 3_985_090_000, sid=9803),
                src("StockholdersEquity", 2_055_771_000, sid=9804),
                src("MinorityInterest", 84_141_000, sid=9805),
            ],
        )
        cell = d.cells[-1]
        d.adjustment_facts = [
            ComponentFact(
                2,
                "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests",
                D(33_733_000),
                cell.period_id,
                end,
            )
        ]
        f = [
            x for x in ties.check(d) if x.evidence["rule"].startswith("liabilities_nci")
        ]
        assert f and f[0].expected_or_other_value == D(
            1_811_445_000
        )  # 3,985,090 - 2,055,771 - 84,141 - 33,733

    def test_swk_2021_assets_minus_equity_plus_nci_at_a_size_of_0_05_percent(self):
        d = empty()
        add(
            d,
            "total_liabilities_resolved",
            12_477_200_000,
            date(2021, 4, 3),
            None,
            "Q1",
            sources=[
                src("Assets", 23_876_000_000, sid=9811),
                src("StockholdersEquity", 11_401_800_000, sid=9812),
                src("MinorityInterest", 3_000_000, sid=9813),
            ],
        )
        f = [x for x in ties.check(d) if x.evidence["rule"] == "liabilities_nci_added"]
        assert (
            f
            and f[0].severity == WRONG_VALUE
            and f[0].expected_or_other_value == D(12_471_200_000)
        )

    def test_the_right_value_is_silent_even_at_that_size(self):
        d = empty()
        add(
            d,
            "total_liabilities_resolved",
            12_471_200_000,
            date(2021, 4, 3),
            None,
            "Q1",
            sources=[
                src("Assets", 23_876_000_000, sid=9821),
                src("StockholdersEquity", 11_401_800_000, sid=9822),
                src("MinorityInterest", 3_000_000, sid=9823),
            ],
        )
        assert not [
            x for x in ties.check(d) if x.evidence["rule"].startswith("liabilities_nci")
        ]


# ------------------------------------------------ (4) quarter label shift
class TestQuarterLabelShift:
    def company(self, twins=True):
        d = empty()
        a = src(
            "SalesRevenueNet",
            3_209_300_000,
            form="10-K",
            sid=9901,
            filed=date(2020, 2, 21),
            accession="0000093556-20-000006",
        )
        add(
            d,
            "revenue",
            3_209_300_000,
            date(2017, 4, 1),
            date(2017, 1, 1),
            "Q1",
            sources=[a],
        )
        if twins:  # loader: the same company, concept, unit and value on the quarter ending 2019-03-30
            d.label_twins[9901] = [(date(2019, 3, 30), 77001)]
        return d

    def test_swk_q1_2017_equal_to_a_fact_on_q1_2019_in_the_same_10k_is_a_label_shift(
        self,
    ):
        f = [
            x
            for x in period_integrity.check(self.company())
            if x.evidence["rule"] == "quarter_label_shift"
        ]
        assert (
            f and f[0].period_end == date(2017, 4, 1) and f[0].severity == WRONG_VALUE
        )
        assert f[0].evidence["equals_fact_on_quarter_ending"] == "2019-03-30"

    def test_no_twin_no_finding(self):
        assert "quarter_label_shift" not in rules(
            period_integrity.check(self.company(twins=False))
        )

    def test_a_year_cell_is_never_a_label_shift_quarter(self):
        d = empty()
        a = src(
            "SalesRevenueNet",
            9_000_000_000,
            form="10-K",
            sid=9911,
            filed=date(2020, 2, 21),
        )
        add(
            d,
            "revenue",
            9_000_000_000,
            date(2017, 12, 31),
            date(2017, 1, 1),
            "FY",
            sources=[a],
        )
        d.label_twins[9911] = [(date(2019, 12, 31), 77002)]
        assert "quarter_label_shift" not in rules(period_integrity.check(d))

    def test_the_loader_asks_only_about_quarters_filed_more_than_800_days_late_and_stores_the_twin(
        self,
    ):
        from test_certification_runner import FakeCursor

        end, start = date(2017, 4, 1), date(2017, 1, 1)
        routes = [
            (
                "p1.end_date + 340 and p1.end_date + 1130",
                [(5, date(2019, 3, 30), 77003)],
            ),
            ("group by cf.company_id", []),
            (
                "from analytics.canonical_fact cf",
                [
                    (
                        7,
                        "revenue",
                        D(3_209_300_000),
                        [5],
                        100,
                        start,
                        end,
                        "duration",
                        2017,
                        "Q1",
                    )
                ],
            ),
            (
                "where f.id = any",
                [
                    (
                        5,
                        "SalesRevenueNet",
                        D(3_209_300_000),
                        True,
                        False,
                        "10-K",
                        "usd",
                        "acc",
                        date(2020, 2, 21),
                        start,
                        end,
                    )
                ],
            ),
            ("from core.company where id", [(7, "0000000007", "T", "3571")]),
        ]
        cur = FakeCursor(routes, [])
        data = loader.load_chunk(cur, [7], loader.Registry(), timeout_s=5)[7]
        assert data.label_twins == {5: [(date(2019, 3, 30), 77003)]}


# ------------------------------------------------ (5) non-standard windows are not loaded
class TestWindowGuard:
    def test_the_canonical_cell_query_drops_durations_longer_than_the_limit(self):
        from test_certification_runner import FakeCursor

        log = []
        cur = FakeCursor([], log)
        loader.load_chunk(cur, [1], loader.Registry(), timeout_s=5)
        q = next(
            e
            for e in log
            if e[0] == "execute"
            and "from analytics.canonical_fact cf" in e[1]
            and "canonical_concept cc" in e[1]
        )
        assert "p.end_date - p.start_date <=" in q[1] and q[2][-1] == 400

    def test_azo_cumulative_window_is_longer_than_the_limit(self):
        assert (
            (date(2015, 5, 9) - date(1998, 1, 1)).days
            > 400
            > (date(2014, 9, 6) - date(2013, 9, 1)).days
        )


# ------------------------------------------------ (6) a real small debt is not a dip
class TestDebtDipMateriality:
    def series(self, values, assets):
        d = empty()
        for end, v in zip(
            (date(2016, 12, 31), date(2017, 3, 31), date(2017, 6, 30)), values
        ):
            add(
                d,
                "total_debt_resolved",
                v,
                end,
                None,
                "Q",
                tag="LongTermDebt",
                form="10-Q",
            )
            add(d, "total_assets", assets, end, None, "Q", tag="Assets", form="10-Q")
        return d

    def test_fix_debt_of_1_8m_between_neighbours_of_9m_on_a_1b_balance_sheet_is_real(
        self,
    ):
        d = self.series((12_000_000, 1_805_000, 12_100_000), 1_000_000_000)
        assert "debt_isolated_dip" not in rules(composition.check(d))

    def test_bax_319m_between_6_4b_neighbours_on_a_30b_balance_sheet_is_still_a_dip(
        self,
    ):
        d = self.series((6_400_000_000, 319_000_000, 6_350_000_000), 30_000_000_000)
        assert "debt_isolated_dip" in rules(composition.check(d), WRONG_VALUE)
