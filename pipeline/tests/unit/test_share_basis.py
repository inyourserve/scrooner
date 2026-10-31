"""corporate_actions/share_basis.py: the split re-base pass (rule
split.event_basis@1). Fixtures are SYNTHETIC fact lists that mirror the
cited filings (values and filing dates as in the accession named in each
fixture); they are not read from the database. The regression cells are the
ones wrong on pages on 2026-10-24 (dry-run evidence, FILING-CHECKED where
the accession is cited):

- AAPL FY2018 diluted EPS 11.91 (10-K 0000320193-18-000145) -> 2.98
  (re-presented in 10-K 0000320193-20-000096 after the 2020-08-28 4:1 split)
- GOOG Q2 2022 diluted EPS 1.21 (10-Q 0001652044-22-000071, filed after the
  2022-07-15 20:1 split) stored 0.0605
- TSLA Q1 2015 diluted EPS -1.22 (10-Q 0001564590-15-003789) -> -1.22/15
- ODFL FY2015 diluted EPS 3.57 -> 1.19 (3:2 in 2020 missing from the split
  table, 10-Q 0001564590-20-021054 R16; 2:1 in 2024)
- NVDA 2024 10:1 filed only on duration contexts (0001045810-24-000264 R8)
"""

from __future__ import annotations

import itertools
from datetime import date, timedelta
from decimal import Decimal
from fractions import Fraction

import pytest
from scrooner_pipeline.common.rule_flags import ENV_DRYRUN, ENV_ENABLED
from scrooner_pipeline.corporate_actions import share_basis as sb
from scrooner_pipeline.corporate_actions.share_basis import SourceFact

D = Decimal
EPS_D = "EarningsPerShareDiluted"
EPS_B = "EarningsPerShareBasic"
DPS_DECL = "CommonStockDividendsPerShareDeclared"
DPS_PAID = "CommonStockDividendsPerShareCashPaid"
COVER = "EntityCommonStockSharesOutstanding"
BS_SHARES = "CommonStockSharesOutstanding"
RATIO = "StockholdersEquityNoteStockSplitConversionRatio1"

MAPPED = {
    "diluted_eps": [EPS_D, "EarningsPerShareBasicAndDiluted"],
    "basic_eps": [EPS_B, "EarningsPerShareBasicAndDiluted"],
    "dividends_per_share": [DPS_DECL, DPS_PAID],
    "shares_outstanding": [BS_SHARES, COVER],
}


class Book:
    """Builds SourceFact rows with stable period and filing ids."""

    def __init__(self) -> None:
        self.facts: list[SourceFact] = []
        self._fid = itertools.count(1)
        self._periods: dict[tuple, int] = {}
        self._filings: dict[str, tuple[int, date, str]] = {}

    def filing(self, acc: str, filed: str, form: str = "10-Q") -> str:
        if acc not in self._filings:
            self._filings[acc] = (
                len(self._filings) + 1,
                date.fromisoformat(filed),
                form,
            )
        return acc

    def pid(self, start: str | None, end: str) -> int:
        key = (start, end)
        return self._periods.setdefault(key, len(self._periods) + 1)

    def add(
        self,
        tag: str,
        value: str,
        start: str | None,
        end: str,
        acc: str,
        *,
        derived: bool = False,
        unit: str | None = None,
    ) -> SourceFact:
        filing_id, filed, form = self._filings[acc]
        if unit is None:
            unit = (
                "shares"
                if tag in (COVER, BS_SHARES) or tag.startswith("Weighted")
                else ("pure" if tag == RATIO else "usd/shares")
            )
        f = SourceFact(
            fact_id=next(self._fid),
            tag=tag,
            unit=unit,
            period_id=self.pid(start, end),
            start_date=date.fromisoformat(start) if start else None,
            end_date=date.fromisoformat(end),
            period_type="duration" if start else "instant",
            value=D(value),
            filing_id=filing_id,
            filing_date=filed,
            form=form,
            accession=acc,
            is_derived=derived,
            is_authoritative=False,
        )
        self.facts.append(f)
        return f

    def cell(self, res: sb.CompanyResult, concept: str, start: str | None, end: str):
        pid = self._periods[(start, end)]
        hits = [c for c in res.cells if c.concept == concept and c.period_id == pid]
        assert len(hits) == 1, hits
        return hits[0]


def run(book: Book) -> sb.CompanyResult:
    return sb.compute_company(1, book.facts, MAPPED)


# --------------------------------------------------------------------------
# Fixtures mirroring real filings
# --------------------------------------------------------------------------
def aapl() -> Book:
    """AAPL 4:1 on 2020-08-28 (ratio fact in 10-K 0000320193-20-000096)."""
    b = Book()
    k18 = b.filing("0000320193-18-000145", "2018-11-05", "10-K")
    k19 = b.filing("0000320193-19-000119", "2019-10-31", "10-K")
    q2 = b.filing("0000320193-20-000052", "2020-05-01")
    q3 = b.filing("0000320193-20-000062", "2020-07-31")
    k20 = b.filing("0000320193-20-000096", "2020-10-30", "10-K")
    fy18, fy19 = ("2017-10-01", "2018-09-29"), ("2018-09-30", "2019-09-28")
    for acc, v in ((k18, "11.91"), (k19, "11.91"), (k20, "2.98")):
        b.add(EPS_D, v, *fy18, acc)
    for acc, v in ((k18, "12.01"), (k19, "12.01"), (k20, "3.00")):
        b.add(EPS_B, v, *fy18, acc)
    for acc, v in ((k18, "2.72"), (k19, "2.72"), (k20, "0.68")):
        b.add(DPS_DECL, v, *fy18, acc)
    b.add(EPS_D, "11.89", *fy19, k19)
    b.add(EPS_D, "2.97", *fy19, k20)
    b.add(EPS_D, "2.58", "2020-03-29", "2020-06-27", q3)  # never re-presented
    b.add(BS_SHARES, "4443236000", None, "2019-09-28", k19)
    b.add(BS_SHARES, "17772944000", None, "2019-09-28", k20)
    for acc, d, v in (
        (k18, "2018-10-26", "4754986000"),
        (k19, "2019-10-18", "4443265000"),
        (q2, "2020-04-17", "4334335000"),
        (q3, "2020-07-17", "4275634000"),
        (k20, "2020-10-16", "17001802000"),
    ):
        b.add(COVER, v, None, d, acc)
    b.add(RATIO, "4", None, "2020-08-28", k20)
    return b


def goog() -> Book:
    """GOOG 20:1, disclosed 2022-02-01 (announced) and 2022-07-15 (effective),
    company_stock_split holds both (0001652044-23-000016 R10/R5)."""
    b = Book()
    k20 = b.filing("0001652044-21-000010", "2021-02-03", "10-K")
    k21 = b.filing("0001652044-22-000019", "2022-02-02", "10-K")
    q1 = b.filing("0001652044-22-000029", "2022-04-27")
    q2 = b.filing("0001652044-22-000071", "2022-07-27")
    q3 = b.filing("0001652044-22-000090", "2022-10-26")
    k22 = b.filing("0001652044-23-000016", "2023-02-03", "10-K")
    q2_23 = b.filing("0001652044-23-000070", "2023-07-25")
    b.add(EPS_D, "58.61", "2020-01-01", "2020-12-31", k20)
    b.add(EPS_D, "58.61", "2020-01-01", "2020-12-31", k21)
    b.add(EPS_D, "2.93", "2020-01-01", "2020-12-31", k22)
    b.add(EPS_D, "112.20", "2021-01-01", "2021-12-31", k21)
    b.add(EPS_D, "5.61", "2021-01-01", "2021-12-31", k22)
    b.add(EPS_B, "59.15", "2020-01-01", "2020-12-31", k21)
    b.add(EPS_B, "2.96", "2020-01-01", "2020-12-31", k22)
    b.add(EPS_B, "113.88", "2021-01-01", "2021-12-31", k21)
    b.add(EPS_B, "5.69", "2021-01-01", "2021-12-31", k22)
    b.add(EPS_D, "1.21", "2022-04-01", "2022-06-30", q2)
    b.add(EPS_D, "1.21", "2022-04-01", "2022-06-30", q2_23)
    b.add(BS_SHARES, "662121000", None, "2021-12-31", k21)
    b.add(BS_SHARES, "662121000", None, "2021-12-31", q1)
    b.add(BS_SHARES, "13242000000", None, "2021-12-31", q2)
    b.add(BS_SHARES, "658763000", None, "2022-03-31", q1)
    b.add(BS_SHARES, "13078000000", None, "2022-06-30", q2)
    b.add(BS_SHARES, "12971000000", None, "2022-09-30", q3)
    b.add(BS_SHARES, "12849000000", None, "2022-12-31", k22)
    b.add(RATIO, "20", None, "2022-02-01", q1)
    b.add(RATIO, "20", None, "2022-07-15", q3)
    b.add(RATIO, "20", None, "2022-07-15", k22)
    return b


def tsla() -> Book:
    """TSLA 5:1 (2020-08) and 3:1 (2022-08); Q1 2015 never re-presented."""
    b = Book()
    q15 = b.filing("0001564590-15-003789", "2015-05-11")
    q16 = b.filing("0001564590-16-018886", "2016-05-10")
    k19 = b.filing("0001564590-20-002450", "2020-01-29", "10-K")
    q20 = b.filing("0001564590-20-034648", "2020-07-28")
    q20b = b.filing("0001564590-20-047486", "2020-10-26")
    k20 = b.filing("0001564590-21-004599", "2021-02-08", "10-K")
    k21 = b.filing("0000950170-22-000796", "2022-02-07", "10-K")
    q22 = b.filing("0000950170-22-012843", "2022-07-25")
    q22b = b.filing("0000950170-22-019867", "2022-10-24")
    k22 = b.filing("0000950170-23-001409", "2023-01-31", "10-K")
    b.add(EPS_D, "-1.22", "2015-01-01", "2015-03-31", q15)
    b.add(EPS_D, "-1.22", "2015-01-01", "2015-03-31", q16)
    b.add(EPS_D, "-4.92", "2019-01-01", "2019-12-31", k19)
    b.add(EPS_D, "-0.98", "2019-01-01", "2019-12-31", k20)
    b.add(EPS_D, "4.90", "2021-01-01", "2021-12-31", k21)
    b.add(EPS_D, "1.63", "2021-01-01", "2021-12-31", k22)
    for acc, d, v in (
        (q15, "2015-04-30", "125000000"),
        (q16, "2016-04-29", "133000000"),
        (k19, "2020-01-28", "181000000"),
        (q20, "2020-07-20", "186000000"),
        (q20b, "2020-10-19", "948000000"),
        (k20, "2021-02-01", "960000000"),
        (k21, "2022-01-31", "1033000000"),
        (q22, "2022-07-15", "1040000000"),
        (q22b, "2022-10-19", "3158000000"),
        (k22, "2023-01-25", "3164000000"),
    ):
        b.add(COVER, v, None, d, acc)
    b.add(RATIO, "5", None, "2020-08-10", q20b)
    b.add(RATIO, "3", None, "2022-08-05", q22b)
    return b


def odfl() -> Book:
    """ODFL 3:2 in March 2020 (duration-only ratio fact, 0001564590-20-021054
    R16) and 2:1 in 2024 (instant 2024-02-16)."""
    b = Book()
    k15 = b.filing("0000878927-16-000055", "2016-02-26", "10-K")
    k16 = b.filing("0000878927-17-000005", "2017-02-27", "10-K")
    k17 = b.filing("0000878927-18-000005", "2018-02-28", "10-K")
    k19 = b.filing("0001564590-20-006626", "2020-02-26", "10-K")
    q20 = b.filing("0001564590-20-021054", "2020-05-05")
    k20 = b.filing("0001564590-21-008460", "2021-02-24", "10-K")
    k23 = b.filing("0000950170-24-021165", "2024-02-26", "10-K")
    q24 = b.filing("0000950170-24-054391", "2024-05-07")
    k24 = b.filing("0000950170-25-026661", "2025-02-25", "10-K")
    for acc in (k15, k16, k17):
        b.add(EPS_D, "3.57", "2015-01-01", "2015-12-31", acc)
    b.add(EPS_D, "7.66", "2019-01-01", "2019-12-31", k19)
    b.add(EPS_D, "5.11", "2019-01-01", "2019-12-31", k20)
    b.add(EPS_D, "10.48", "2023-01-01", "2023-12-31", k23)
    b.add(EPS_D, "5.24", "2023-01-01", "2023-12-31", k24)
    for acc, d, v in (
        (k15, "2016-02-19", "83000000"),
        (k19, "2020-02-20", "79500000"),
        (q20, "2020-04-30", "118000000"),
        (k20, "2021-02-19", "118200000"),
        (k23, "2024-02-20", "109000000"),
        (q24, "2024-04-30", "218000000"),
        (k24, "2025-02-20", "213000000"),
    ):
        b.add(COVER, v, None, d, acc)
    b.add(RATIO, "1.5", "2020-01-01", "2020-03-31", q20)
    b.add(RATIO, "2", None, "2024-02-16", q24)
    return b


def nvda_2024() -> Book:
    """NVDA 10:1 in June 2024, ratio fact ONLY on a duration context
    (0001045810-24-000264 R8)."""
    b = Book()
    k24 = b.filing("0001045810-24-000029", "2024-02-21", "10-K")
    q1 = b.filing("0001045810-24-000124", "2024-05-29")
    q2 = b.filing("0001045810-24-000264", "2024-08-28")
    k25 = b.filing("0001045810-25-000023", "2025-02-26", "10-K")
    b.add(EPS_D, "11.93", "2023-01-30", "2024-01-28", k24)
    b.add(EPS_D, "1.19", "2023-01-30", "2024-01-28", k25)
    b.add(COVER, "2464000000", None, "2024-02-16", k24)
    b.add(COVER, "2460000000", None, "2024-05-17", q1)
    b.add(COVER, "24530000000", None, "2024-08-21", q2)
    b.add(COVER, "24490000000", None, "2025-02-19", k25)
    b.add(RATIO, "10", "2024-05-01", "2024-05-31", q2)
    return b


# --------------------------------------------------------------------------
# Named regression cells
# --------------------------------------------------------------------------
def test_aapl_fy2018_rebased_from_the_latest_filed_copy():
    b = aapl()
    res = run(b)
    (ev,) = [e for e in res.events if e.status == "confirmed"]
    assert ev.ratio == 4 and ev.basis_date == date(2020, 10, 30)
    assert set(ev.kinds) == {"ratio_fact", "filed_pair", "share_step"}
    cell = b.cell(res, "diluted_eps_resolved", "2017-10-01", "2018-09-29")
    assert cell.status == sb.SHOWN and cell.value == D("2.98")
    assert cell.chosen.accession == "0000320193-20-000096"
    assert b.cell(res, "basic_eps_resolved", "2017-10-01", "2018-09-29").value == D(
        "3.00"
    )
    assert b.cell(
        res, "dividends_per_share_resolved", "2017-10-01", "2018-09-29"
    ).value == D("0.68")
    assert b.cell(res, "diluted_eps_resolved", "2018-09-30", "2019-09-28").value == D(
        "2.97"
    )


def test_aapl_never_represented_quarter_divided_by_its_filing_factor():
    b = aapl()
    cell = b.cell(run(b), "diluted_eps_resolved", "2020-03-29", "2020-06-27")
    assert cell.value == D("0.645") and cell.factor == 4
    assert 90 not in cell.source_fact_ids  # lineage = own fact + ratio fact ids


def test_aapl_share_counts_are_rebased_too():
    b = aapl()
    res = run(b)
    assert b.cell(res, "shares_outstanding_resolved", None, "2019-09-28").value == D(
        "17772944000"
    )
    cover = b.cell(res, "shares_outstanding_resolved", None, "2018-10-26")
    assert cover.value == D("4754986000") * 4


def test_goog_q2_2022_filed_after_split_is_not_divided_again():
    b = goog()
    res = run(b)
    events = [e for e in res.events if e.status == "confirmed"]
    assert [e.ratio for e in events] == [20]  # two disclosures, one event
    assert len(events[0].disclosures) == 3
    cell = b.cell(res, "diluted_eps_resolved", "2022-04-01", "2022-06-30")
    assert cell.value == D("1.21") and cell.factor == 1
    assert b.cell(res, "diluted_eps_resolved", "2020-01-01", "2020-12-31").value == D(
        "2.93"
    )
    assert res.violations == []


def test_tsla_q1_2015_takes_the_product_of_both_later_splits():
    b = tsla()
    res = run(b)
    assert sorted(e.ratio for e in res.events if e.status == "confirmed") == [3, 5]
    cell = b.cell(res, "diluted_eps_resolved", "2015-01-01", "2015-03-31")
    assert cell.factor == 15
    assert cell.value == D("-0.0813333333")


def test_odfl_three_for_two_from_a_duration_ratio_fact():
    b = odfl()
    res = run(b)
    ratios = sorted(e.ratio for e in res.events if e.status == "confirmed")
    assert ratios == [Fraction(3, 2), 2]
    cell = b.cell(res, "diluted_eps_resolved", "2015-01-01", "2015-12-31")
    assert cell.factor == 3 and cell.value == D("1.19")


def test_nvda_duration_only_ratio_fact_counts_as_evidence():
    b = nvda_2024()
    res = run(b)
    (ev,) = res.events
    assert ev.status == "confirmed" and ev.ratio == 10
    assert set(ev.kinds) == {"ratio_fact", "filed_pair", "share_step"}
    assert b.cell(res, "diluted_eps_resolved", "2023-01-30", "2024-01-28").value == D(
        "1.19"
    )


def test_nvda_2021_two_disclosures_46_days_apart_are_one_event():
    b = Book()
    k21 = b.filing("0001045810-21-000010", "2021-02-26", "10-K")
    q1 = b.filing("0001045810-21-000064", "2021-05-26")
    q2 = b.filing("0001045810-21-000131", "2021-08-20")
    k22 = b.filing("0001045810-22-000036", "2022-03-18", "10-K")
    b.add(EPS_D, "6.90", "2020-01-27", "2021-01-31", k21)
    b.add(EPS_D, "1.73", "2020-01-27", "2021-01-31", k22)
    b.add(COVER, "620000000", None, "2021-02-19", k21)
    b.add(COVER, "623000000", None, "2021-05-20", q1)
    b.add(COVER, "2500000000", None, "2021-08-13", q2)
    b.add(COVER, "2500000000", None, "2022-03-11", k22)
    b.add(RATIO, "4", None, "2021-06-03", q2)
    b.add(RATIO, "4", None, "2021-07-19", k22)
    res = run(b)
    assert [(e.ratio, e.status) for e in res.events] == [(4, "confirmed")]
    assert len(res.events[0].disclosures) == 2
    assert b.cell(res, "diluted_eps_resolved", "2020-01-27", "2021-01-31").value == D(
        "1.73"
    )


def test_wmt_fy2024_filed_after_split_has_factor_one():
    """WMT 3:1 effective 2024-02-23; FY2024 10-K 0000104169-24-000056 filed
    2024-03-15 already reports post-split EPS 1.91."""
    b = Book()
    k23 = b.filing("0000104169-23-000020", "2023-03-17", "10-K")
    q3 = b.filing("0000104169-23-000110", "2023-12-05")
    k24 = b.filing("0000104169-24-000056", "2024-03-15", "10-K")
    b.add(EPS_D, "4.27", "2022-02-01", "2023-01-31", k23)
    b.add(EPS_D, "1.42", "2022-02-01", "2023-01-31", k24)
    b.add(EPS_D, "1.91", "2023-02-01", "2024-01-31", k24)
    b.add(COVER, "2696000000", None, "2023-03-10", k23)
    b.add(COVER, "2690000000", None, "2023-11-30", q3)
    b.add(COVER, "8060000000", None, "2024-03-08", k24)
    b.add(RATIO, "3", None, "2024-02-23", k24)
    res = run(b)
    cell = b.cell(res, "diluted_eps_resolved", "2023-02-01", "2024-01-31")
    assert cell.factor == 1 and cell.value == D("1.91")
    assert res.basis[cell.chosen.filing_id].factor == 1


# --------------------------------------------------------------------------
# Negative cases and guards
# --------------------------------------------------------------------------
def test_share_step_alone_contradicted_by_filed_comparatives_is_rejected():
    """A merger doubles the share count (clean 2x); EPS comparatives filed on
    both sides agree at ratio 1, so it is not a split (ledger row 113)."""
    b = Book()
    a = b.filing("A-1", "2021-02-01", "10-K")
    c = b.filing("A-2", "2021-05-01")
    d = b.filing("A-3", "2022-02-01", "10-K")
    for acc in (a, d):
        b.add(EPS_D, "1.50", "2020-01-01", "2020-12-31", acc)
        b.add(EPS_B, "1.52", "2020-01-01", "2020-12-31", acc)
    b.add(EPS_D, "0.40", "2021-01-01", "2021-03-31", c)
    b.add(EPS_D, "0.40", "2021-01-01", "2021-03-31", d)
    b.add(COVER, "100000000", None, "2021-01-25", a)
    b.add(COVER, "200000000", None, "2021-04-25", c)
    b.add(COVER, "201000000", None, "2022-01-25", d)
    res = run(b)
    assert [e.status for e in res.events] == ["rejected"]
    cell = b.cell(res, "diluted_eps_resolved", "2020-01-01", "2020-12-31")
    assert cell.status == sb.SHOWN and cell.value == D("1.50") and cell.factor == 1


def test_reverse_split_seen_only_as_a_filed_pair_is_review_and_hides():
    """BURU-like 1-for-40 seen only through a re-presented EPS (ledger row
    35): one evidence kind -> review; cells only in pre-boundary filings are
    hidden, a cell re-presented after it is shown from the later copy."""
    b = Book()
    a = b.filing("B-1", "2026-03-20", "10-K")
    c = b.filing("B-2", "2026-10-01", "10-K/A")
    b.add(EPS_D, "-0.05", "2025-01-01", "2025-12-31", a)
    b.add(EPS_D, "-2.00", "2025-01-01", "2025-12-31", c)
    b.add(EPS_B, "-0.05", "2025-01-01", "2025-12-31", a)
    b.add(EPS_B, "-2.00", "2025-01-01", "2025-12-31", c)
    # a real reverse split re-presents the share counts too
    b.add(
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "40123480",
        "2025-01-01",
        "2025-12-31",
        a,
    )
    b.add(
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "1003087",
        "2025-01-01",
        "2025-12-31",
        c,
    )
    b.add(EPS_D, "-0.07", "2024-01-01", "2024-12-31", a)
    res = run(b)
    (ev,) = res.events
    assert ev.status == "review" and ev.ratio == Fraction(1, 40)
    # Verifier-1000 rule: the period's original filing (pre-boundary, review)
    # must agree, so the later re-presented -2.00 alone is not shown either
    for s, e in (("2025-01-01", "2025-12-31"), ("2024-01-01", "2024-12-31")):
        assert b.cell(res, "diluted_eps_resolved", s, e).status == sb.HIDE_BASIS_REVIEW


def test_double_counted_event_hides_the_company():
    """If a detector bug recorded GOOG's 20:1 twice, filed pairs (ratio 20 on
    two periods between the same filings) contradict factor 400."""
    b = goog()
    facts = b.facts
    pairs = sb.build_filed_pairs(facts)
    series = sb.build_share_series(facts)
    steps = sb.build_share_steps(series)
    filings = sorted(
        {sb.Filing(f.filing_id, f.filing_date, f.form, f.accession) for f in facts},
        key=lambda x: x.filing_date,
    )
    good = sb.detect_events(pairs, steps, sb.build_disclosures(facts), filings)
    twice = good + [
        sb.Event(
            99, Fraction(20), date(2022, 10, 26), date(2023, 1, 1), status="confirmed"
        )
    ]
    basis = sb.compute_filing_basis(filings, twice, series, steps)
    assert sb.invariant_violations(pairs, basis, twice)
    assert not sb.invariant_violations(
        pairs, sb.compute_filing_basis(filings, good, series, steps), good
    )


def test_one_period_context_swap_is_not_a_company_violation():
    """AMZN 10-K 0001193125-13-028520 swaps two quarters' EPS (0.29 <-> 0.44,
    which looks like 3:2 and 2:3). One period per ratio is a context error,
    judged per cell, never a company-wide basis review."""
    b = Book()
    a = b.filing("Z-1", "2012-07-27")
    c = b.filing("Z-2", "2013-01-30", "10-K")
    for tag in (EPS_B, EPS_D):
        b.add(tag, "0.29", "2012-01-01", "2012-03-31", a)
        b.add(tag, "0.44", "2012-01-01", "2012-03-31", c)
        b.add(tag, "0.44", "2011-01-01", "2011-03-31", a)
        b.add(tag, "0.29", "2011-01-01", "2011-03-31", c)
        for s, e, v in (
            ("2011-04-01", "2011-06-30", "0.42"),
            ("2011-07-01", "2011-09-30", "0.14"),
            ("2011-01-01", "2011-12-31", "1.39"),
            ("2011-10-01", "2011-12-31", "0.39"),
        ):
            b.add(tag, v, s, e, a)
            b.add(tag, v, s, e, c)
    res = run(b)
    assert res.violations == []
    assert all(e.status == "rejected" for e in res.events)
    cell = b.cell(res, "basic_eps_resolved", "2012-01-01", "2012-03-31")
    assert cell.status == sb.HIDE_RESTATED


def test_restated_copies_on_one_basis_are_hidden_with_reason():
    """MSFT FY2016 diluted EPS 2.10 (0001193125-16-662209) vs 2.56 after the
    ASC 606 full retrospective (0001564590-18-019062): no split, real
    disagreement -> hidden (design 2.8), not picked by fact id."""
    b = Book()
    a = b.filing("0001193125-16-662209", "2016-07-28", "10-K")
    c = b.filing("0001564590-17-014900", "2017-08-02", "10-K")
    d = b.filing("0001564590-18-019062", "2018-08-03", "10-K")
    for acc, v in ((a, "2.10"), (c, "2.10"), (d, "2.56")):
        b.add(EPS_D, v, "2015-07-01", "2016-06-30", acc)
    res = run(b)
    cell = b.cell(res, "diluted_eps_resolved", "2015-07-01", "2016-06-30")
    assert cell.status == sb.HIDE_RESTATED and cell.value is None
    assert len(cell.candidates) == 3


def test_thousands_scale_copy_is_dropped_from_a_share_cell():
    """AAPL 10-Q 0001193125-14-157311 tags 899,213 shares at 2013-09-28 where
    0001193125-14-024487 tags 899,213,000."""
    b = Book()
    a = b.filing("0001193125-13-416534", "2013-10-30", "10-K")
    c = b.filing("0001193125-14-024487", "2014-01-28")
    d = b.filing("0001193125-14-157311", "2014-04-24")
    for acc, v in ((a, "899213000"), (c, "899213000"), (d, "899213")):
        b.add(BS_SHARES, v, None, "2013-09-28", acc)
    res = run(b)
    assert res.events == [] and res.violations == []
    cell = b.cell(res, "shares_outstanding_resolved", None, "2013-09-28")
    assert cell.status == sb.SHOWN and cell.value == D("899213000")
    assert "units scale" in cell.note


def test_quarter_tagged_with_the_annual_dividend_is_a_label_error():
    """NVDA FY2015 10-K 0001045810-15-000036: CashPaid 0.34 on the Q4
    context while Q1-Q3 declared 0.085 each."""
    b = Book()
    q3 = b.filing("0001045810-14-000188", "2014-11-20")
    k = b.filing("0001045810-15-000036", "2015-03-12", "10-K")
    b.add(DPS_DECL, "0.255", "2014-01-27", "2014-10-26", q3)
    for s_, e_ in (("2013-10-28", "2014-01-26"), ("2014-01-27", "2014-04-27"),
                   ("2014-04-28", "2014-07-27"), ("2014-07-28", "2014-10-26")):  # fmt: skip
        b.add(DPS_DECL, "0.085", s_, e_, q3)
    b.add(DPS_DECL, "0.34", "2014-01-27", "2015-01-25", k)
    b.add(DPS_DECL, "0.085", "2014-10-27", "2015-01-25", k, derived=True)
    b.add(DPS_PAID, "0.34", "2014-10-27", "2015-01-25", k)
    res = run(b)
    # Q4 0.34 is on CashPaid while NVDA's series is Declared: hidden as off
    # the company's basis (before run 5: caught as an annual amount)
    cell = b.cell(res, "dividends_per_share_resolved", "2014-10-27", "2015-01-25")
    assert cell.status == sb.HIDE_DPS_BASIS and cell.value is None


def test_quarter_holding_the_years_only_dividend_is_shown():
    """NVDA FY2013: first dividend paid in Q4 (0.075); 9M paid 0
    (0001045810-13-000109)."""
    b = Book()
    q3 = b.filing("0001045810-13-000109", "2013-11-20")
    k = b.filing("0001045810-13-000008", "2013-03-12", "10-K")
    b.add(DPS_PAID, "0", "2012-01-30", "2012-10-28", q3)
    b.add(DPS_PAID, "0.075", "2012-01-30", "2013-01-27", k)
    b.add(DPS_PAID, "0.075", "2012-10-29", "2013-01-27", k)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2012-10-29", "2013-01-27")
    assert cell.status == sb.SHOWN and cell.value == D("0.075")


def test_derived_and_non_periodic_facts_are_never_candidates():
    b = Book()
    k = b.filing("K-1", "2025-02-01", "10-K")
    e = b.filing("E-1", "2025-03-01", "8-K")
    b.add(EPS_D, "1.84", "2024-10-01", "2024-12-31", k, derived=True)
    b.add(EPS_D, "9.99", "2023-10-01", "2023-12-31", e)
    res = run(b)
    assert (
        b.cell(res, "diluted_eps_resolved", "2024-10-01", "2024-12-31").status
        == sb.HIDE_NO_FILED_SOURCE
    )
    assert (
        b.cell(res, "diluted_eps_resolved", "2023-10-01", "2023-12-31").status
        == sb.HIDE_NO_FILED_SOURCE
    )


def test_unit_mismatch_is_not_a_candidate():
    b = Book()
    k = b.filing("K-1", "2025-02-01", "10-K")
    b.add(EPS_D, "1.00", "2024-01-01", "2024-12-31", k, unit="twd/shares")
    res = run(b)
    assert (
        b.cell(res, "diluted_eps_resolved", "2024-01-01", "2024-12-31").status
        == sb.HIDE_NO_FILED_SOURCE
    )


def test_announced_split_with_no_new_basis_filing_is_pending():
    b = Book()
    k = b.filing("P-1", "2026-02-01", "10-K")
    b.add(EPS_D, "4.00", "2025-01-01", "2025-12-31", k)
    b.add(RATIO, "10", None, "2026-06-01", k)
    res = run(b)
    assert res.events == []  # a ratio fact dated after its own filing is not read
    assert b.cell(res, "diluted_eps_resolved", "2025-01-01", "2025-12-31").value == D(
        "4.00"
    )


# --------------------------------------------------------------------------
# Pure helpers
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "old,new,kind,expected",
    [
        ("11.91", "2.98", sb.PER_SHARE, Fraction(4)),
        ("58.61", "2.93", sb.PER_SHARE, Fraction(20)),
        ("7.66", "5.11", sb.PER_SHARE, Fraction(3, 2)),
        ("-0.05", "-2.00", sb.PER_SHARE, Fraction(1, 40)),
        ("2.34", "2.34", sb.PER_SHARE, sb.ONE),
        ("0.02", "0.01", sb.PER_SHARE, None),  # 1 and 2 both fit: ambiguous
        ("5.48", "6.94", sb.PER_SHARE, None),  # restatement
        ("662121000", "13242000000", sb.SHARES, Fraction(20)),
        ("899213000", "899213", sb.SHARES, None),  # units scale, not 1-for-1000
        ("1.00", "-1.00", sb.PER_SHARE, None),
    ],
)
def test_fit_pair_ratio(old, new, kind, expected):
    assert sb.fit_pair_ratio(D(old), D(new), kind) == expected


def test_share_step_tolerance():
    assert sb.fit_share_step(D("4275634000"), D("17001802000")) == 4
    assert sb.fit_share_step(D("100"), D("117")) is None  # STE-like acquisition
    assert sb.fit_share_step(D("100"), D("430")) is None  # DOCU-like x4.3
    assert sb.fit_share_step(D("100"), D("101")) == sb.ONE


def test_convert_is_exact_and_directional():
    assert sb.convert(D("11.91"), sb.ONE, sb.PER_SHARE) == D("11.91")
    assert sb.convert(D("3.57"), Fraction(3), sb.PER_SHARE) == D("1.19")
    assert sb.convert(D("-1.22"), Fraction(15), sb.PER_SHARE) == D("-0.0813333333")
    assert sb.convert(D("4443236000"), Fraction(4), sb.SHARES) == D("17772944000")
    assert sb.convert(D("100"), Fraction(1, 3), sb.SHARES) == D("33")


def test_half_unit_floors_per_share_at_cents():
    assert sb.half_unit(D("3"), sb.PER_SHARE) == D("0.005")
    assert sb.half_unit(D("2.9775"), sb.PER_SHARE) == D("0.00005")
    assert sb.half_unit(D("13242000000"), sb.SHARES) == D("500000")
    assert sb.half_unit(D("4443236000"), sb.SHARES) == D("500")


def test_classify_change():
    def cell(concept, value, status=sb.SHOWN):
        return sb.CellResult(concept, 1, status, value, (), None, None, ())

    assert (
        sb.classify_change(D("11.91"), cell("diluted_eps_resolved", D("2.98")))
        == sb.WAS_UNADJUSTED
    )
    assert (
        sb.classify_change(D("10.09"), cell("diluted_eps_resolved", D("0.36")))
        == sb.WAS_UNADJUSTED
    )
    assert (
        sb.classify_change(D("0.0605"), cell("diluted_eps_resolved", D("1.21")))
        == sb.WAS_DOUBLE_DIVIDED
    )
    assert (
        sb.classify_change(D("2.97"), cell("diluted_eps_resolved", D("2.97")))
        == sb.UNCHANGED
    )
    assert (
        sb.classify_change(None, cell("diluted_eps_resolved", D("1"))) == sb.NEW_VALUE
    )
    hid = cell("diluted_eps_resolved", None, sb.HIDE_RESTATED)
    assert sb.classify_change(D("2.1"), hid) == sb.NOW_HIDDEN
    der = cell("diluted_eps_resolved", None, sb.HIDE_NO_FILED_SOURCE)
    assert sb.classify_change(D("1.84"), der) == sb.KEPT_DERIVED_ONLY
    assert sb.classify_change(D("1.84"), der, ru1_on=True) == sb.NOW_HIDDEN
    assert (
        sb.classify_change(D("1"), cell("shares_outstanding_resolved", D("4")))
        == sb.SHARE_COUNT_REBASED
    )


def test_cells_to_remove_leaves_derived_only_cells_to_ru1():
    b = Book()
    k = b.filing("K-1", "2025-02-01", "10-K")
    b.add(EPS_D, "1.84", "2024-10-01", "2024-12-31", k, derived=True)
    b.add(EPS_D, "2.10", "2015-07-01", "2016-06-30", k)
    b.add(
        EPS_D, "2.56", "2015-07-01", "2016-06-30", b.filing("K-2", "2026-02-01", "10-K")
    )
    res = run(b)
    current = {
        ("diluted_eps_resolved", b.pid("2024-10-01", "2024-12-31")): (
            501,
            D("1.84"),
            (1,),
        ),
        ("diluted_eps_resolved", b.pid("2015-07-01", "2016-06-30")): (
            502,
            D("2.10"),
            (2,),
        ),
        ("ebit_resolved", 77): (503, D("1"), (9,)),
    }
    assert sb.cells_to_remove(res, current, remove_derived_only=False) == [502]
    assert sorted(sb.cells_to_remove(res, current, remove_derived_only=True)) == [
        501,
        502,
    ]


def test_event_hash_is_stable_and_tracks_the_event_set():
    a, b = run(aapl()), run(aapl())
    assert a.event_hash == b.event_hash
    assert a.event_hash != run(goog()).event_hash


def test_compute_is_deterministic_under_input_order():
    b = aapl()
    r1 = sb.compute_company(1, b.facts, MAPPED)
    r2 = sb.compute_company(1, list(reversed(b.facts)), MAPPED)
    assert [
        (c.concept, c.period_id, c.status, c.value)
        for c in sorted(r1.cells, key=lambda c: (c.concept, c.period_id))
    ] == [
        (c.concept, c.period_id, c.status, c.value)
        for c in sorted(r2.cells, key=lambda c: (c.concept, c.period_id))
    ]


# --------------------------------------------------------------------------
# Flag behavior
# --------------------------------------------------------------------------
class _Boom:
    def execute(self, *a, **k):  # pragma: no cover - must not be called
        raise AssertionError("mode off must not query")


class _Recorder:
    """Fake connection: canned reads, records every statement."""

    def __init__(self, book: Book) -> None:
        self.book = book
        self.sql: list[str] = []

    def execute(self, sql, params=None):
        self.sql.append(" ".join(sql.split()).lower())
        s = self.sql[-1]
        rows: list = []
        if "from analytics.concept_mapping" in s:
            rows = [(n, t) for n, tags in MAPPED.items() for t in tags]
        elif "from core.concept" in s:
            rows = [(1,)]
        elif "from core.fact" in s:
            rows = [
                (f.fact_id, f.tag, f.unit, f.period_id, f.start_date, f.end_date, f.period_type,
                 f.value, f.filing_id, f.filing_date, f.form, f.accession, f.is_derived,
                 f.is_authoritative)
                for f in self.book.facts
            ]  # fmt: skip
        elif "from analytics.canonical_fact" in s:
            rows = []
        return _Rows(rows)

    def transaction(self):  # pragma: no cover - must not be called in dry_run
        raise AssertionError("dry_run must not open a write transaction")


class _Rows:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows


def test_mode_off_issues_no_query():
    assert sb.run_split_rebase(_Boom(), [1], environ={}) == {
        "mode": "off",
        "companies": 0,
    }


def test_dry_run_reads_only_and_returns_results():
    conn = _Recorder(aapl())
    out = sb.run_split_rebase(conn, [1], environ={ENV_DRYRUN: sb.RULE_ID})
    assert out["mode"] == "dry_run" and out["companies"] == 1
    assert all(s.startswith("select") for s in conn.sql)
    res, _current = out["results"][0]
    assert any(c.value == D("2.98") for c in res.cells)


def test_dry_run_needs_an_explicit_company_list():
    with pytest.raises(ValueError):
        sb.run_split_rebase(_Recorder(aapl()), [], environ={ENV_DRYRUN: sb.RULE_ID})


def test_mode_on_needs_a_run_id():
    with pytest.raises(ValueError):
        sb.run_split_rebase(_Recorder(aapl()), [1], environ={ENV_ENABLED: sb.RULE_ID})


def test_rule_is_registered_with_a_dry_run_path():
    from scrooner_pipeline.common import rule_flags

    assert rule_flags.RULES[sb.RULE_ID].dry_run is True
    assert rule_flags.rule_mode(sb.RULE_ID, {}) == rule_flags.OFF


def test_comparatives_not_rebased_across_a_confirmed_split_hide_the_company():
    """Ratio fact and share step confirm a 2:1, but the post-split filing
    repeats two prior periods at the pre-split value (ratio 1): our factor
    would divide them, the filing says they are already current, so the
    whole company goes to basis review rather than show either guess."""
    b = Book()
    a = b.filing("C-1", "2023-02-01", "10-K")
    q = b.filing("C-2", "2023-05-01")
    c = b.filing("C-3", "2024-02-01", "10-K")
    for s, e, v in (
        ("2022-01-01", "2022-12-31", "4.00"),
        ("2021-01-01", "2021-12-31", "3.00"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, v, s, e, a)
            b.add(tag, v, s, e, c)
    b.add(EPS_D, "1.10", "2023-01-01", "2023-03-31", q)
    b.add(COVER, "100000000", None, "2023-01-25", a)
    b.add(COVER, "100500000", None, "2023-04-25", q)
    b.add(COVER, "201000000", None, "2024-01-25", c)
    b.add(RATIO, "2", None, "2023-09-01", c)
    res = run(b)
    assert [(e.ratio, e.status) for e in res.events] == [(2, "confirmed")]
    assert res.violations
    assert {c.status for c in res.cells} == {sb.HIDE_COMPANY_INVARIANT}


def test_representation_rounding_of_summed_quarters_is_not_a_conflict():
    """AAPL FY2013 DPS 11.40 (10-K 0001193125-13-416534) is 1.6286 after the
    7:1 split; the FY2014 10-K 0001193125-14-383437 re-presents 1.64
    (0.38+0.38+0.44+0.44)."""
    b = Book()
    k13 = b.filing("0001193125-13-416534", "2013-10-30", "10-K")
    q = b.filing("0001193125-14-157311", "2014-04-24")
    k14 = b.filing("0001193125-14-383437", "2014-10-27", "10-K")
    b.add(DPS_DECL, "11.40", "2012-09-30", "2013-09-28", k13)
    b.add(DPS_DECL, "1.64", "2012-09-30", "2013-09-28", k14)
    for acc in (k13, k14):
        b.add(EPS_D, "39.75" if acc == k13 else "5.68", "2012-09-30", "2013-09-28", acc)
        b.add(EPS_B, "40.03" if acc == k13 else "5.72", "2012-09-30", "2013-09-28", acc)
    b.add(COVER, "899738000", None, "2013-10-18", k13)
    b.add(COVER, "861745000", None, "2014-04-11", q)
    b.add(COVER, "5987867000", None, "2014-10-10", k14)
    b.add(RATIO, "7", None, "2014-06-06", k14)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2012-09-30", "2013-09-28")
    assert cell.status == sb.SHOWN and cell.value == D("1.64")


def test_pair_spanning_two_confirmed_splits_is_not_a_third_event():
    """A TSLA FY2017 copy filed before the 5:1 and one filed after the 3:1
    differ by 15 (SYNTHETIC pairing: -11.83 / 15 = -0.79): explained by the
    product of the two confirmed events, so no review event hides history."""
    b = tsla()
    old = b.filing("0001564590-18-002956", "2018-02-23", "10-K")
    b.add(EPS_D, "-11.83", "2017-01-01", "2017-12-31", old)
    b.add(EPS_D, "-0.79", "2017-01-01", "2017-12-31", "0000950170-23-001409")
    b.add(EPS_B, "-11.83", "2017-01-01", "2017-12-31", old)
    b.add(EPS_B, "-0.79", "2017-01-01", "2017-12-31", "0000950170-23-001409")
    res = run(b)
    assert {e.status for e in res.events} <= {"confirmed", "rejected"}
    assert (
        b.cell(res, "diluted_eps_resolved", "2015-01-01", "2015-03-31").status
        == sb.SHOWN
    )
    assert b.cell(res, "diluted_eps_resolved", "2017-01-01", "2017-12-31").value == D(
        "-0.79"
    )


# --------------------------------------------------------------------------
# Rules from the 1,000-company cohort dry-run (2026-10-24), SYNTHETIC
# fixtures shaped like the named companies' facts (DATA-INFERRED cases).
# --------------------------------------------------------------------------
def _two_to_one(b: Book, pre: str, post: str, *, cover: bool = True) -> None:
    """A real 2:1 between filings `pre` and `post`: EPS basic and diluted on
    two periods re-presented / 2, plus cover counts doubling."""
    for s, e, v in (
        ("2012-01-01", "2012-12-31", "3.02"),
        ("2011-01-01", "2011-12-31", "2.50"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, v, s, e, pre)
            b.add(tag, str(D(v) / 2), s, e, post)
    if cover:
        b.add(COVER, "48000000", None, "2013-04-20", pre)
        b.add(COVER, "96200000", None, "2013-07-20", post)


def test_redisclosed_old_split_does_not_confirm_a_later_one_pair_cluster():
    """WAB: the 2013 2:1 is re-disclosed in later 10-Ks; a single DPS copy
    pair at ratio 2 a year later must not become a second confirmed 2:1."""
    b = Book()
    pre = b.filing("W-1", "2013-05-02")
    post = b.filing("W-2", "2013-07-26")
    q16 = b.filing("W-3", "2015-11-01")
    k16 = b.filing("W-4", "2016-02-19", "10-K")
    _two_to_one(b, pre, post)
    b.add(RATIO, "2", None, "2013-05-14", post)
    b.add(RATIO, "2", None, "2013-05-14", k16)  # re-disclosure, >400 days later
    for tag in (DPS_PAID, DPS_DECL):
        b.add(tag, "0.10", "2015-07-01", "2015-09-30", q16)
        b.add(tag, "0.05", "2015-07-01", "2015-09-30", k16)
    res = run(b)
    assert [(e.ratio, e.status) for e in res.events if e.status == "confirmed"] == [
        (2, "confirmed")
    ]
    assert {e.status for e in res.events} == {"confirmed", "rejected"}
    assert res.violations == []


def test_inverted_ratio_fact_attaches_to_the_observed_split():
    """TTD files its 2021 10:1 as 0.1: attach it to the ratio-10 event, never
    leave it as a loose review candidate that hides all earlier filings."""
    b = Book()
    pre = b.filing("T-1", "2021-05-10")
    post = b.filing("T-2", "2021-08-10")
    for s, e, v in (
        ("2020-01-01", "2020-12-31", "4.80"),
        ("2019-01-01", "2019-12-31", "2.60"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, v, s, e, pre)
            b.add(tag, str(D(v) / 10), s, e, post)
    b.add(RATIO, "0.1", None, "2021-06-16", post)
    res = run(b)
    assert [(e.ratio, e.status) for e in res.events] == [(10, "confirmed")]
    assert "ratio_fact" in res.events[0].kinds


def test_non_clean_ratio_fact_is_an_exchange_ratio_not_a_split():
    """DUK 0.8708 / WTW 0.3775 style values: rejected, nothing hidden."""
    b = Book()
    a = b.filing("D-1", "2012-02-01", "10-K")
    c = b.filing("D-2", "2013-02-01", "10-K")
    b.add(EPS_D, "4.00", "2011-01-01", "2011-12-31", a)
    b.add(EPS_D, "4.20", "2012-01-01", "2012-12-31", c)
    b.add(RATIO, "0.8708", None, "2012-06-30", c)
    res = run(b)
    assert [e.status for e in res.events] == ["rejected"]
    assert (
        b.cell(res, "diluted_eps_resolved", "2011-01-01", "2011-12-31").status
        == sb.SHOWN
    )


def test_restated_share_counts_count_as_share_evidence():
    """MA/CSX/CME: no undimensioned cover series, but EPS basic and diluted
    / 10 and weighted shares x 10 on two periods in the later filing."""
    b = Book()
    pre = b.filing("M-1", "2013-11-01")
    post = b.filing("M-2", "2014-02-14", "10-K")
    for s, e, v, w in (
        ("2012-01-01", "2012-12-31", "22.73", "122000000"),
        ("2011-01-01", "2011-12-31", "14.85", "127000000"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, v, s, e, pre)
            b.add(tag, str((D(v) / 10).quantize(D("0.01"))), s, e, post)
        b.add("WeightedAverageNumberOfDilutedSharesOutstanding", w, s, e, pre)
        b.add(
            "WeightedAverageNumberOfDilutedSharesOutstanding",
            str(D(w) * 10),
            s,
            e,
            post,
        )
    res = run(b)
    (ev,) = res.events
    assert ev.status == "confirmed" and ev.ratio == 10
    assert set(ev.kinds) == {"filed_pair", "share_step"}
    assert ev.evidence_json()["share_step_from"] == "restated_share_counts"


def test_single_tag_dps_move_is_not_an_event_or_a_company_violation():
    """TER/AIG: DPS on two periods moves x4 between filings (rate vs annual
    context), EPS does not. Judged per cell; the company is not hidden."""
    b = Book()
    a = b.filing("R-1", "2021-02-24", "10-K")
    c = b.filing("R-2", "2022-02-24", "10-K")
    for s, e, v in (
        ("2020-01-01", "2020-12-31", "0.10"),
        ("2019-01-01", "2019-12-31", "0.09"),
    ):
        b.add(DPS_PAID, v, s, e, a)
        b.add(DPS_PAID, str(D(v) * 4), s, e, c)
        b.add(EPS_D, "3.00", s, e, a)
        b.add(EPS_D, "3.00", s, e, c)
    res = run(b)
    assert all(e.status == "rejected" for e in res.events)
    assert res.violations == []
    cell = b.cell(res, "diluted_eps_resolved", "2020-01-01", "2020-12-31")
    assert cell.status == sb.SHOWN
    dps = b.cell(res, "dividends_per_share_resolved", "2020-01-01", "2020-12-31")
    # dividends are not restated: the original 10-K's quarterly 0.10 stands
    assert dps.status == sb.SHOWN and dps.value == D("0.10")


def test_per_share_power_of_ten_without_share_counts_is_a_units_error():
    """HALO/RGA: basic and diluted EPS x1000 in one filing, share counts
    unchanged: not a 1-for-1000 reverse split; cells judged per copy."""
    b = Book()
    a = b.filing("H-1", "2018-02-20", "10-K")
    c = b.filing("H-2", "2019-02-20", "10-K")
    for s, e, v in (
        ("2017-01-01", "2017-12-31", "0.87"),
        ("2016-01-01", "2016-12-31", "0.42"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, v, s, e, a)
            b.add(tag, str(D(v) * 1000), s, e, c)
    res = run(b)
    assert all(e.status == "rejected" for e in res.events)
    assert res.violations == []


def test_same_ratio_confirmed_twice_keeps_one_and_reviews_the_gap():
    """KR: a 2:1 seen at two boundaries 6 months apart is one event; the
    filing between them cannot be placed and is basis review."""
    b = Book()
    f1 = b.filing("K-1", "2014-12-16")
    f2 = b.filing("K-2", "2015-03-31", "10-K")
    f3 = b.filing("K-3", "2015-06-30")
    f4 = b.filing("K-4", "2015-09-22")
    _two_to_one(b, f1, f2)
    for s, e, v in (
        ("2013-01-01", "2013-12-31", "1.90"),
        ("2014-01-01", "2014-03-31", "0.80"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, v, s, e, f3)
            b.add(tag, str(D(v) / 2), s, e, f4)
    b.add(COVER, "48100000", None, "2015-06-20", f3)  # KR: back on the old basis
    b.add(COVER, "96000000", None, "2015-09-15", f4)
    b.add(RATIO, "2", None, "2015-06-25", f4)
    res = run(b)
    assert [e.status for e in res.events].count("confirmed") == 1
    assert "review" not in [e.status for e in res.events]
    filing_ids = {f.accession: f.filing_id for f in b.facts}
    assert res.basis[filing_ids["K-2"]].status == "review"
    assert "same-ratio" in res.basis[filing_ids["K-2"]].note


def test_one_eps_tag_moving_alone_is_not_an_event():
    """A context or entry error in one EPS tag (diluted 2x in the later
    filing, basic unchanged) is judged per cell, not a split candidate that
    hides every earlier filing."""
    b = Book()
    a = b.filing("O-1", "2020-02-01", "10-K")
    c = b.filing("O-2", "2021-02-01", "10-K")
    for s, e in (("2019-01-01", "2019-12-31"), ("2018-01-01", "2018-12-31")):
        b.add(EPS_D, "2.40", s, e, a)
        b.add(EPS_D, "1.20", s, e, c)
    b.add(EPS_D, "2.00", "2017-01-01", "2017-12-31", a)
    res = run(b)
    assert [e.status for e in res.events] == ["rejected"]
    assert (
        b.cell(res, "diluted_eps_resolved", "2017-01-01", "2017-12-31").status
        == sb.SHOWN
    )


def test_mixed_dividend_basis_in_one_series_is_hidden_pending_ac24():
    """LLY: interim DPS cells would come from Declared for most quarters and
    CashPaid (0.5625) for Q3 2018; one series, two bases -> hidden."""
    b = Book()
    q = b.filing("L-1", "2018-11-01")
    k = b.filing("0000059478-20-000057", "2020-02-19", "10-K")
    b.add(DPS_DECL, "1.125", "2018-01-01", "2018-06-30", q)
    b.add(DPS_DECL, "0.5625", "2018-01-01", "2018-03-31", q)
    b.add(DPS_PAID, "0.5625", "2018-07-01", "2018-09-30", k)
    b.add(DPS_DECL, "2.25", "2018-01-01", "2018-12-31", k)
    res = run(b)
    q3 = b.cell(res, "dividends_per_share_resolved", "2018-07-01", "2018-09-30")
    q1 = b.cell(res, "dividends_per_share_resolved", "2018-01-01", "2018-03-31")
    # default: the series is shown on the declared basis; the paid-only Q3 is hidden
    assert q3.status == sb.HIDE_DPS_BASIS
    assert q1.status == sb.SHOWN and q1.chosen.tag == DPS_DECL
    fy = b.cell(res, "dividends_per_share_resolved", "2018-01-01", "2018-12-31")
    assert fy.status == sb.SHOWN  # the annual series is on one tag


def test_label_shifted_copy_is_dropped_not_read_as_a_restatement():
    """NVDA FY2018 10-K puts the Q2 value 0.98 on the 6-month context while
    two 10-Qs give 1.83 (Verifier false hold, 2026-10-24)."""
    b = Book()
    q2 = b.filing("0001045810-17-000123", "2017-08-23")
    q3 = b.filing("0001045810-17-000176", "2017-11-21")
    k = b.filing("0001045810-18-000010", "2018-02-28", "10-K")
    for tag, six, q in ((EPS_B, "1.83", "0.98"), (EPS_D, "1.71", "0.92")):
        b.add(tag, six, "2017-01-30", "2017-07-30", q2)
        b.add(tag, six, "2017-01-30", "2017-07-30", q3)
        b.add(tag, q, "2017-01-30", "2017-07-30", k)  # shifted
        b.add(tag, q, "2017-05-01", "2017-07-30", k)  # its own Q2 in the same filing
        b.add(tag, q, "2017-05-01", "2017-07-30", q2)
    res = run(b)
    cell = b.cell(res, "basic_eps_resolved", "2017-01-30", "2017-07-30")
    assert cell.status == sb.SHOWN and cell.value == D("1.83")
    # run 7: a 6M copy in a 10-K is also an unpresented column
    assert "label-shifted" in cell.note or "does not present" in cell.note


def test_two_vintage_restatement_is_still_hidden():
    """MSFT ASC 606: the restated copy does not equal any other period's
    value in its filing, so the hold stays."""
    b = Book()
    a = b.filing("0001564590-17-014900", "2017-08-02", "10-K")
    c = b.filing("0001564590-18-019062", "2018-08-03", "10-K")
    b.add(EPS_D, "2.71", "2016-07-01", "2017-06-30", a)
    b.add(EPS_D, "3.25", "2016-07-01", "2017-06-30", c)
    b.add(EPS_D, "2.13", "2017-07-01", "2018-06-30", c)
    res = run(b)
    assert (
        b.cell(res, "diluted_eps_resolved", "2016-07-01", "2017-06-30").status
        == sb.HIDE_RESTATED
    )


def _mixed_basis_book(declared_quarters: int, paid_quarters: int) -> Book:
    b = Book()
    k = 0
    for year in (2016, 2017, 2018):
        for qs, qe, fd in (("01-01", "03-31", "05-01"), ("04-01", "06-30", "08-01"),
                           ("07-01", "09-30", "11-01")):  # fmt: skip
            f = b.filing(f"Q-{year}-{qs}", f"{year}-{fd}")
            if k < declared_quarters:
                b.add(DPS_DECL, "0.50", f"{year}-{qs}", f"{year}-{qe}", f)
            elif k < declared_quarters + paid_quarters:
                b.add(DPS_PAID, "0.48", f"{year}-{qs}", f"{year}-{qe}", f)
            k += 1
    return b


def test_one_dividend_basis_per_company_hides_the_other_tag():
    """AES/AMT/CVI/CWEN/LMT (Verifier run 5): a company's shown DPS never mix
    declared and paid. More Declared quarters: the CashPaid ones are hidden."""
    b = _mixed_basis_book(5, 4)
    res = run(b)
    shown = [c for c in res.cells if c.status == sb.SHOWN]
    assert {c.chosen.tag for c in shown} == {DPS_DECL} and len(shown) == 5
    hidden = [c for c in res.cells if c.status == sb.HIDE_DPS_BASIS]
    assert len(hidden) == 4 and all(DPS_DECL in c.note for c in hidden)


def test_one_dividend_basis_goes_to_cash_paid_when_it_has_more_quarters():
    b = _mixed_basis_book(4, 5)
    res = run(b)
    shown = [c for c in res.cells if c.status == sb.SHOWN]
    assert {c.chosen.tag for c in shown} == {DPS_PAID} and len(shown) == 5


def test_one_dividend_basis_tie_goes_to_declared():
    b = _mixed_basis_book(4, 4)
    res = run(b)
    shown = [c for c in res.cells if c.status == sb.SHOWN]
    assert {c.chosen.tag for c in shown} == {DPS_DECL} and len(shown) == 4


def test_off_basis_cell_takes_the_basis_tags_own_vintage_value():
    """AMT Q4 2023: shown 1.62 paid while the declared 1.70 is filed."""
    b = _mixed_basis_book(5, 0)
    k = b.filing("AMT-K", "2024-02-27", "10-K")
    q = b.filing("AMT-Q", "2024-01-30")
    b.add(DPS_PAID, "1.62", "2023-10-01", "2023-12-31", q)
    b.add(DPS_DECL, "1.70", "2023-10-01", "2023-12-31", k)
    b.add(DPS_PAID, "1.62", "2023-10-01", "2023-12-31", k)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2023-10-01", "2023-12-31")
    assert cell.status == sb.SHOWN and cell.value == D("1.70")
    assert cell.chosen.tag == DPS_DECL


def test_zero_declared_beside_cash_paid_in_the_same_filing_is_dropped():
    """AFL Q1 2026 (0001628280-26-030923): Declared 0 next to CashPaid 0.61;
    AFL's series is on the paid basis."""
    b = _mixed_basis_book(0, 6)
    q = b.filing("AFL-Q1", "2026-05-06")
    q2 = b.filing("AFL-Q2", "2026-08-07")
    b.add(DPS_PAID, "0.61", "2026-01-01", "2026-03-31", q)
    b.add(DPS_DECL, "0", "2026-01-01", "2026-03-31", q)
    b.add(DPS_DECL, "0", "2026-01-01", "2026-03-31", q2)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2026-01-01", "2026-03-31")
    assert cell.status == sb.SHOWN and cell.value == D("0.61")


def test_generic_dividends_paid_below_a_cent_is_not_common_dividend_evidence():
    """BPOP Q1 2015 (0001193125-15-182220): Declared 0 beside a generic
    PaymentsOfDividends of 620K, which is preferred (~0.006 a share); the
    first common dividend came in Q2 2015."""
    b = Book()
    q = b.filing("BPOP-Q1", "2015-05-11")
    b.add(DPS_DECL, "0", "2015-01-01", "2015-03-31", q)
    b.add("PaymentsOfDividends", "620000", "2015-01-01", "2015-03-31", q, unit="USD")
    b.add(
        "EntityCommonStockSharesOutstanding",
        "103000000",
        "2015-04-30",
        "2015-04-30",
        q,
        unit="shares",
    )
    b.add(
        DPS_DECL, "0.15", "2015-07-01", "2015-09-30", b.filing("BPOP-Q3", "2015-11-06")
    )
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2015-01-01", "2015-03-31")
    assert cell.status == sb.SHOWN and cell.value == D("0")


def test_generic_dividends_paid_at_a_real_rate_still_contradicts_a_zero():
    b = Book()
    q = b.filing("X-Q1", "2015-05-11")
    b.add(DPS_DECL, "0", "2015-01-01", "2015-03-31", q)
    b.add("PaymentsOfDividends", "30000000", "2015-01-01", "2015-03-31", q, unit="USD")
    b.add(
        "EntityCommonStockSharesOutstanding",
        "100000000",
        "2015-04-30",
        "2015-04-30",
        q,
        unit="shares",
    )
    b.add(DPS_DECL, "0.30", "2015-07-01", "2015-09-30", b.filing("X-Q3", "2015-11-06"))
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2015-01-01", "2015-03-31")
    assert cell.status == sb.HIDE_DPS_INVALID


def test_restatement_fitting_an_unrelated_clean_ratio_is_not_a_company_violation():
    """CRM-like: a confirmed 4:1 exists, and a later 10-K restates two small
    quarters roughly 3x (0.09 -> 0.28, 0.10 -> 0.31): restatement, judged per
    cell, never a company-wide hide."""
    b = aapl()
    a = b.filing("C-9", "2018-03-09", "10-K")
    c = b.filing("C-10", "2019-03-08", "10-K")
    for s, e, old, new in (
        ("2017-02-01", "2017-04-30", "0.09", "0.28"),
        ("2017-05-01", "2017-07-31", "0.10", "0.31"),
    ):
        for tag in (EPS_B, EPS_D):
            b.add(tag, old, s, e, a)
            b.add(tag, new, s, e, c)
    # ... while the other comparatives in the same two filings are unchanged
    for s, e, v in (
        ("2016-02-01", "2016-04-30", "1.10"),
        ("2016-05-01", "2016-07-31", "1.20"),
        ("2016-08-01", "2016-10-31", "1.30"),
        ("2016-02-01", "2017-01-31", "4.80"),
    ):
        for tag in (EPS_B, EPS_D):
            b.add(tag, v, s, e, a)
            b.add(tag, v, s, e, c)
    res = run(b)
    assert res.violations == []
    assert all(e.status in ("confirmed", "rejected") for e in res.events)
    cell = b.cell(res, "basic_eps_resolved", "2017-02-01", "2017-04-30")
    assert cell.status == sb.HIDE_RESTATED


def _with_confirmed_two_for_one(b: Book) -> tuple[str, str]:
    """A company with a filed 2:1 (ratio fact + pairs + share step) in 2013,
    plus two later 10-Ks for the cases below."""
    pre = b.filing("X-1", "2013-05-02")
    post = b.filing("X-2", "2013-07-26")
    _two_to_one(b, pre, post)
    b.add(RATIO, "2", None, "2013-05-14", post)
    return b.filing("X-3", "2016-02-20", "10-K"), b.filing("X-4", "2017-02-20", "10-K")


def test_dps_only_move_by_the_companys_own_ratio_is_not_a_violation():
    """A DPS rate/annual context error that happens to equal the company's
    own split ratio (2x on two periods, Declared and CashPaid) while EPS is
    unchanged: judged per cell, the company is not hidden."""
    b = Book()
    a, c = _with_confirmed_two_for_one(b)
    for s, e in (("2015-01-01", "2015-03-31"), ("2015-04-01", "2015-06-30")):
        for tag in (DPS_DECL, DPS_PAID):
            b.add(tag, "0.20", s, e, a)
            b.add(tag, "0.40", s, e, c)
        b.add(EPS_D, "1.00", s, e, a)
        b.add(EPS_D, "1.00", s, e, c)
    res = run(b)
    assert res.violations == []
    assert (
        b.cell(res, "diluted_eps_resolved", "2015-01-01", "2015-03-31").status
        == sb.SHOWN
    )


def test_one_period_move_by_the_companys_own_ratio_is_not_a_violation():
    """One period (basic and diluted) moving 2x between two later 10-Ks is a
    context error at that period, not a missed split."""
    b = Book()
    a, c = _with_confirmed_two_for_one(b)
    for tag in (EPS_B, EPS_D):
        b.add(tag, "0.80", "2015-01-01", "2015-03-31", a)
        b.add(tag, "0.40", "2015-01-01", "2015-03-31", c)
    for s, e, v in (
        ("2015-04-01", "2015-06-30", "0.90"),
        ("2015-07-01", "2015-09-30", "0.95"),
        ("2015-01-01", "2015-12-31", "3.50"),
        ("2014-01-01", "2014-12-31", "3.10"),
    ):
        for tag in (EPS_B, EPS_D):
            b.add(tag, v, s, e, a)
            b.add(tag, v, s, e, c)
    res = run(b)
    assert res.violations == []
    assert (
        b.cell(res, "diluted_eps_resolved", "2015-04-01", "2015-06-30").status
        == sb.SHOWN
    )


def test_share_copy_off_by_a_million_vs_its_own_filing_is_dropped():
    """PCG 10-Q 0001004980-13-000025: CommonStockSharesOutstanding
    430,718,293,000,000 beside cover 442,173,394 and basic WASO 434M."""
    b = Book()
    q = b.filing("0001004980-13-000025", "2013-05-01")
    b.add(BS_SHARES, "430718293000000", None, "2012-12-31", q)
    b.add(COVER, "442173394", None, "2013-04-23", q)
    b.add(
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "434000000",
        "2013-01-01",
        "2013-03-31",
        q,
    )
    res = run(b)
    assert (
        b.cell(res, "shares_outstanding_resolved", None, "2012-12-31").status
        == sb.HIDE_UNITS_SCALE
    )
    assert b.cell(res, "shares_outstanding_resolved", None, "2013-04-23").value == D(
        "442173394"
    )


def test_two_share_copies_off_by_scale_with_no_majority_are_hidden():
    b = Book()
    a = b.filing("S-1", "2014-01-28")
    c = b.filing("S-2", "2014-04-24")
    b.add(BS_SHARES, "899213000", None, "2013-09-28", a)
    b.add(BS_SHARES, "899213", None, "2013-09-28", c)
    res = run(b)
    assert (
        b.cell(res, "shares_outstanding_resolved", None, "2013-09-28").status
        == sb.HIDE_UNITS_SCALE
    )


def test_zero_filed_share_count_is_hidden():
    b = Book()
    k = b.filing("0000908937-25-000005", "2025-01-30", "10-K")
    b.add(BS_SHARES, "0", None, "2023-12-31", k)
    res = run(b)
    assert (
        b.cell(res, "shares_outstanding_resolved", None, "2023-12-31").status
        == sb.HIDE_ZERO_SHARES
    )


def test_dps_off_by_a_units_scale_vs_the_company_median_is_hidden():
    """VICI 10-Q 0001705696-18-000086 files Q2 2018 DPS as 262,500."""
    b = Book()
    for i, (s, e, v) in enumerate(
        (
            ("2018-01-01", "2018-03-31", "0.16"),
            ("2018-04-01", "2018-06-30", "262500"),
            ("2018-07-01", "2018-09-30", "0.2625"),
            ("2018-10-01", "2018-12-31", "0.2875"),
            ("2019-01-01", "2019-03-31", "0.2875"),
        )
    ):
        b.add(DPS_DECL, v, s, e, b.filing(f"V-{i}", f"20{19 + i // 4}-0{1 + i % 4}-15"))
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2018-04-01", "2018-06-30").status
        == sb.HIDE_UNITS_SCALE
    )
    assert (
        b.cell(res, "dividends_per_share_resolved", "2018-07-01", "2018-09-30").status
        == sb.SHOWN
    )


def test_dps_guard_needs_enough_other_values_and_a_large_gap():
    b = Book()
    for i, (s, e, v) in enumerate(
        (
            ("2018-01-01", "2018-03-31", "0.10"),
            ("2018-04-01", "2018-06-30", "4.10"),  # a special dividend, 41x
            ("2018-07-01", "2018-09-30", "0.10"),
            ("2018-10-01", "2018-12-31", "0.11"),
        )
    ):
        b.add(DPS_DECL, v, s, e, b.filing(f"W-{i}", f"2019-0{1 + i}-15"))
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2018-04-01", "2018-06-30").status
        == sb.SHOWN
    )


def test_share_count_far_off_the_company_median_is_hidden():
    """DLTR 10-K 0000935703-11-000058 files a share count of 123.5 (in
    millions) with no other share count in that filing."""
    b = Book()
    for i, (d, v) in enumerate(
        (
            ("2010-01-30", "123000000"),
            ("2011-01-29", "123.5"),
            ("2012-01-28", "117000000"),
            ("2013-02-02", "221000000"),
            ("2014-02-01", "207000000"),
        )
    ):
        b.add(BS_SHARES, v, None, d, b.filing(f"D-{i}", f"201{i}-03-20", "10-K"))
    res = run(b)
    assert (
        b.cell(res, "shares_outstanding_resolved", None, "2011-01-29").status
        == sb.HIDE_UNITS_SCALE
    )
    assert (
        b.cell(res, "shares_outstanding_resolved", None, "2013-02-02").status
        == sb.SHOWN
    )


def test_real_repeated_splits_months_apart_are_both_kept():
    """CPRT 2:1 in Nov 2022 and again in Sep 2023 (no reversal between):
    both confirmed, the 4x pairs across both are their product."""
    b = Book()
    f1 = b.filing("P-1", "2022-09-01", "10-K")
    f2 = b.filing("P-2", "2022-11-20")
    f3 = b.filing("P-3", "2023-08-01")
    f4 = b.filing("P-4", "2023-09-30", "10-K")
    _two_to_one(b, f1, f2)
    for s, e, v in (
        ("2021-08-01", "2022-07-31", "4.40"),
        ("2020-08-01", "2021-07-31", "3.90"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, str(D(v) / 2), s, e, f3)
            b.add(tag, str(D(v) / 4), s, e, f4)
    b.add(COVER, "96500000", None, "2023-07-20", f3)
    b.add(COVER, "193000000", None, "2023-09-20", f4)
    b.add(RATIO, "2", None, "2023-08-20", f4)
    res = run(b)
    assert sorted(str(e.basis_date) for e in res.events if e.status == "confirmed") == [
        "2022-11-20",
        "2023-09-30",
    ]
    assert res.violations == []


def test_review_candidate_on_a_confirmed_boundary_is_rejected():
    """PRAX: a 1:15 reverse split with a concurrent offering moves the share
    count only 1:10; that step is the confirmed split plus issuance."""
    b = Book()
    pre = b.filing("X-1", "2024-02-01", "10-K")
    post = b.filing("X-2", "2024-03-10")
    for s, e, v in (
        ("2023-01-01", "2023-09-30", "-1.20"),
        ("2022-01-01", "2022-12-31", "-2.10"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, v, s, e, pre)
            b.add(tag, str(D(v) * 15), s, e, post)
    b.add(COVER, "90000000", None, "2024-01-25", pre)
    b.add(COVER, "9000000", None, "2024-03-05", post)
    b.add(RATIO, "0.0667", None, "2024-03-05", post)
    res = run(b)
    assert [e.status for e in res.events if e.ratio == Fraction(1, 15)] == ["confirmed"]
    assert all(e.status != "review" for e in res.events)


def test_dps_same_filing_checks():
    """OHI negative DPS; BWA zero DPS while dividends were paid; WTRG annual
    DPS below its quarters; OGE an annual rate on a quarter."""
    b = Book()
    k = b.filing("K-1", "2020-02-20", "10-K")
    b.add(DPS_DECL, "-0.66", "2019-01-01", "2019-03-31", b.filing("Q-1", "2019-05-01"))
    b.add(DPS_DECL, "0", "2019-01-01", "2019-12-31", k)
    b.add(
        "PaymentsOfDividendsCommonStock",
        "140000000",
        "2019-01-01",
        "2019-12-31",
        k,
        unit="usd",
    )
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2019-01-01", "2019-03-31").status
        == sb.HIDE_DPS_INVALID
    )
    assert (
        b.cell(res, "dividends_per_share_resolved", "2019-01-01", "2019-12-31").status
        == sb.HIDE_DPS_INVALID
    )

    b = Book()
    for i, (s, e, v) in enumerate(
        (
            ("2024-01-01", "2024-03-31", "0.3255"),
            ("2024-04-01", "2024-06-30", "0.3255"),
            ("2024-07-01", "2024-09-30", "0.3255"),
            ("2024-10-01", "2024-12-31", "0.3255"),
            ("2024-01-01", "2024-12-31", "0.3255"),  # WTRG: the rate on the year
            ("2019-01-01", "2019-03-31", "0.365"),
            ("2019-04-01", "2019-06-30", "0.365"),
            ("2019-07-01", "2019-09-30", "0.3875"),
            ("2019-10-01", "2019-12-31", "0.3875"),
            ("2020-01-01", "2020-03-31", "1.505"),  # OGE: the 2019 total on Q1 2020
            ("2020-04-01", "2020-06-30", "0.3875"),
            ("2020-07-01", "2020-09-30", "0.3875"),
            ("2020-10-01", "2020-12-31", "0.3875"),
        )
    ):
        b.add(DPS_DECL, v, s, e, b.filing(f"W-{i}", f"2025-{1 + i % 12:02d}-15"))
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2024-01-01", "2024-12-31").status
        == sb.HIDE_DPS_INVALID
    )
    assert (
        b.cell(res, "dividends_per_share_resolved", "2020-01-01", "2020-03-31").status
        == sb.HIDE_DPS_INVALID
    )
    assert (
        b.cell(res, "dividends_per_share_resolved", "2020-04-01", "2020-06-30").status
        == sb.SHOWN
    )


def test_original_filing_must_agree_with_the_later_copy():
    """XYL Q3 2019: the original 10-Q gives 0.24; a later 10-K puts the next
    year's rate 0.26 on that quarter (and 0.26 is also that later filing's own
    Q3 2020 value). The original is never dropped as shifted; the later copy is."""
    b = Book()
    q = b.filing("XYL-1", "2019-10-31")
    k = b.filing("XYL-2", "2021-02-20", "10-K")
    b.add(DPS_DECL, "0.24", "2019-07-01", "2019-09-30", q)
    b.add(DPS_DECL, "0.24", "2019-04-01", "2019-06-30", q)  # same rate, normal
    b.add(DPS_DECL, "0.26", "2019-07-01", "2019-09-30", k)  # shifted comparative
    b.add(DPS_DECL, "0.26", "2020-07-01", "2020-09-30", k)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2019-07-01", "2019-09-30")
    # one later copy against the original: dividends are not restated, the
    # original 0.24 stands (never the later 0.26)
    assert cell.status == sb.SHOWN and cell.value == D("0.24")


def test_rate_on_a_longer_context_in_the_original_is_dropped():
    """LEA 9M 2014: the original 10-Q puts the quarterly 0.20 on the 9-month
    context; later filings give 0.60 (Verifier false hold)."""
    b = Book()
    q = b.filing("0000842162-14-000002", "2014-10-24")
    k = b.filing("0000842162-15-000013", "2015-04-24")
    b.add(DPS_DECL, "0.20", "2014-01-01", "2014-09-27", q)
    b.add(DPS_DECL, "0.20", "2014-06-29", "2014-09-27", q)
    b.add(DPS_DECL, "0.60", "2014-01-01", "2014-09-27", k)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2014-01-01", "2014-09-27")
    assert cell.status == sb.SHOWN and cell.value == D("0.60")


def test_share_copies_in_thousands_next_to_waso_are_not_flagged():
    """SAIA/EXEL file weighted averages in thousands: the correct count must
    not be hidden by the same-filing scale check when its own series agrees."""
    b = Book()
    for i, (d, v) in enumerate(
        (("2010-12-31", "15900245"), ("2011-06-30", "15927231"), ("2011-09-30", "15937821"),
         ("2011-12-31", "15937821"), ("2012-03-31", "15993881"))
    ):  # fmt: skip
        f = b.filing(f"S-{i}", (date.fromisoformat(d) + timedelta(days=40)).isoformat())
        b.add(BS_SHARES, v, None, d, f)
        b.add(
            "WeightedAverageNumberOfSharesOutstandingBasic",
            str(int(v) // 1000),
            "2011-01-01",
            d,
            f,
        )
    res = run(b)
    assert (
        b.cell(res, "shares_outstanding_resolved", None, "2011-06-30").status
        == sb.SHOWN
    )


def test_phase_one_keeps_the_stored_value_for_other_changed_cells():
    b = aapl()
    res = run(b)
    fy18 = b.pid("2017-10-01", "2018-09-29")
    fy19 = b.pid("2018-09-30", "2019-09-28")
    current = {
        ("diluted_eps_resolved", fy18): (
            1,
            D("11.91"),
            (),
        ),  # was unadjusted -> written
        ("diluted_eps_resolved", fy19): (2, D("-2.97"), ()),  # other_changed -> kept
    }
    p1 = {(c.concept, c.period_id) for c in sb.cells_to_write(res, current, phase=1)}
    p2 = {(c.concept, c.period_id) for c in sb.cells_to_write(res, current, phase=2)}
    assert ("diluted_eps_resolved", fy18) in p1 and ("diluted_eps_resolved", fy18) in p2
    assert ("diluted_eps_resolved", fy19) not in p1 and (
        "diluted_eps_resolved",
        fy19,
    ) in p2
    assert sb.WRITE_PHASE == 1


def test_lone_outlier_does_not_beat_a_majority_of_later_copies():
    """TEX Q2 2020 DPS: the original 10-Q 0.12, two later 10-Ks 0; TSCO
    2023-02-08: six copies 1.03, one later 0.22."""
    b = Book()
    q = b.filing("0000097216-20-000259", "2020-10-28")
    k1 = b.filing("0000097216-22-000013", "2022-02-11", "10-K")
    k2 = b.filing("0000097216-23-000012", "2023-02-10", "10-K")
    b.add(DPS_DECL, "0.12", "2020-04-01", "2020-06-30", q)
    b.add(DPS_DECL, "0", "2020-04-01", "2020-06-30", k1)
    b.add(DPS_DECL, "0", "2020-04-01", "2020-06-30", k2)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2020-04-01", "2020-06-30")
    assert cell.status == sb.SHOWN and cell.value == D("0")

    b = Book()
    accs = [
        b.filing(f"T-{i}", f"202{3 + i // 4}-0{1 + (i % 4) * 2}-20") for i in range(7)
    ]
    for acc in accs[:6]:
        b.add(DPS_DECL, "1.03", None, "2023-02-08", acc)
    b.add(DPS_DECL, "0.22", None, "2023-02-08", accs[6])
    res = run(b)
    assert b.cell(res, "dividends_per_share_resolved", None, "2023-02-08").value == D(
        "1.03"
    )


def test_future_dated_context_is_not_a_reported_value():
    """PPL 10-Q 0000922224-13-000025 (filed Aug 2013) tags the November 2013
    dividend 0.36; the later filing reports 0.3675."""
    b = Book()
    q = b.filing("0000922224-13-000025", "2013-08-05")
    k = b.filing("K-14", "2014-02-20", "10-K")
    b.add(DPS_DECL, "0.36", "2013-11-01", "2013-11-30", q)
    b.add(DPS_DECL, "0.3675", "2013-11-01", "2013-11-30", k)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2013-11-01", "2013-11-30")
    assert cell.status == sb.SHOWN and cell.value == D("0.3675")


def test_recurring_stock_dividends_hold_earlier_filings():
    """VLY-like 5% stock dividend: EPS basic and diluted re-presented / 1.05
    on two periods -> review, earlier filings held; CBSH tags
    StockIssuedDuringPeriodValueStockDividend."""
    b = Book()
    a = b.filing("V-1", "2010-02-25", "10-K")
    c = b.filing("V-2", "2011-02-25", "10-K")
    for s_, e, v in (
        ("2009-01-01", "2009-12-31", "0.73"),
        ("2008-01-01", "2008-12-31", "0.84"),
    ):
        for tag in (EPS_B, EPS_D):
            b.add(tag, v, s_, e, a)
            b.add(tag, str((D(v) / D("1.05")).quantize(D("0.01"))), s_, e, c)
    d = b.filing("V-3", "2012-02-25", "10-K")  # the next year's 5% (VLY 2011, 2012)
    for s_, e, v in (
        ("2010-01-01", "2010-12-31", "0.62"),
        ("2009-01-01", "2009-12-31", "0.70"),
    ):
        for tag in (EPS_B, EPS_D):
            b.add(tag, v, s_, e, c)
            b.add(tag, str((D(v) / D("1.05")).quantize(D("0.01"))), s_, e, d)
    b.add(EPS_D, "0.61", "2007-01-01", "2007-12-31", a)
    res = run(b)
    assert [e.status for e in res.events] == ["review", "review"]
    assert (
        b.cell(res, "diluted_eps_resolved", "2007-01-01", "2007-12-31").status
        == sb.HIDE_BASIS_REVIEW
    )

    # the stock-dividend value tag alone is not split evidence (EQIX, IRM REIT
    # special distributions): nothing is held on it
    b = Book()
    a = b.filing("C-1", "2018-02-25", "10-K")
    k = b.filing("C-2", "2019-02-25", "10-K")
    b.add(EPS_D, "3.20", "2017-01-01", "2017-12-31", a)
    b.add(
        "StockIssuedDuringPeriodValueStockDividend",
        "886000",
        "2018-01-01",
        "2018-12-31",
        k,
        unit="usd",
    )
    res = run(b)
    assert (
        b.cell(res, "diluted_eps_resolved", "2017-01-01", "2017-12-31").status
        == sb.SHOWN
    )


def test_confirmed_event_contradicted_by_comparatives_is_rejected():
    """ANF 2013: a ratio fact and one tag pair, no share-count step, while many
    comparatives span the boundary unchanged: not a split."""
    b = Book()
    a = b.filing("A-1", "2012-03-30", "10-K")
    c = b.filing("A-2", "2013-04-02", "10-K")
    for s_, e, v in (
        ("2011-01-30", "2012-01-28", "1.55"),
        ("2010-01-31", "2011-01-29", "1.73"),
        ("2011-10-30", "2012-01-28", "0.42"),
        ("2011-07-31", "2011-10-29", "0.18"),
    ):
        for tag in (EPS_B, EPS_D):
            b.add(tag, v, s_, e, a)
            b.add(tag, v, s_, e, c)
    for tag in (DPS_DECL, DPS_PAID):
        b.add(tag, "0.70", "2011-01-30", "2012-01-28", a)
        b.add(tag, "0.35", "2011-01-30", "2012-01-28", c)
    b.add(RATIO, "2", None, "2013-03-01", c)
    res = run(b)
    assert "confirmed" not in [e.status for e in res.events]
    assert res.violations == []


def test_no_representation_slack_on_a_quarter_or_instant():
    """TSCO 2023-02-08 DPS: six copies 1.03 on the pre-5:1 basis (0.206) and a
    2025 filing's 0.22 (the 2024 rate on a 2023 date) are not one value."""
    b = tsco_like = Book()
    pre = [b.filing(f"P-{i}", f"2023-0{3 + i}-01") for i in range(3)]
    post = b.filing("0000916365-25-000089", "2025-02-25", "10-K")
    for acc in pre:
        b.add(DPS_DECL, "1.03", None, "2023-02-08", acc)
    b.add(DPS_DECL, "0.22", None, "2023-02-08", post)
    for acc, v in ((pre[2], "1.03"), (post, "0.206")):
        for tag in (EPS_B, EPS_D):
            b.add(tag, str(D(v) * 9), "2022-01-01", "2022-12-31", acc)
            b.add(tag, str(D(v) * 4), "2021-01-01", "2021-12-31", acc)
    b.add(COVER, "110000000", None, "2023-05-01", pre[2])
    b.add(COVER, "535000000", None, "2025-02-10", post)
    b.add(RATIO, "5", None, "2024-12-20", post)
    res = run(tsco_like)
    cell = b.cell(res, "dividends_per_share_resolved", None, "2023-02-08")
    assert cell.status == sb.SHOWN and cell.value == D("0.206")


def test_confirmed_product_across_two_splits_is_not_a_third_event():
    """CPRT: 2:1 in Nov 2022 and 2:1 in Sep 2023; per-share and share counts
    re-presented 4x between a pre-2022 and a post-2023 filing (filed pair +
    restated shares, no ratio fact) are the product, not a 4:1 split."""
    b = Book()
    f0 = b.filing("P-0", "2022-03-01")
    f1 = b.filing("P-1", "2022-09-01", "10-K")
    f2 = b.filing("P-2", "2022-11-20")
    f3 = b.filing("P-3", "2023-08-01")
    f4 = b.filing("P-4", "2023-09-30", "10-K")
    _two_to_one(b, f1, f2)
    for s_, e, v in (
        ("2021-08-01", "2022-07-31", "4.40"),
        ("2020-08-01", "2021-07-31", "3.90"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, str(D(v) / 2), s_, e, f3)
            b.add(tag, str(D(v) / 4), s_, e, f4)
    for s_, e, v, w in (
        ("2019-08-01", "2020-07-31", "3.20", "47512345"),
        ("2018-08-01", "2019-07-31", "2.80", "47834567"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, v, s_, e, f0)
            b.add(tag, str(D(v) / 4), s_, e, f4)
        b.add("WeightedAverageNumberOfSharesOutstandingBasic", w, s_, e, f0)
        b.add(
            "WeightedAverageNumberOfSharesOutstandingBasic", str(int(w) * 4), s_, e, f4
        )
    b.add(COVER, "96500000", None, "2023-07-20", f3)
    b.add(COVER, "193000000", None, "2023-09-20", f4)
    b.add(RATIO, "2", None, "2023-08-20", f4)
    res = run(b)
    assert [e.ratio for e in res.events if e.status == "confirmed"] == [2, 2]
    assert res.violations == []
    assert b.cell(res, "diluted_eps_resolved", "2019-08-01", "2020-07-31").value == D(
        "0.8"
    )


def test_q4_equal_to_a_rate_tagged_year_is_shown():
    """BPOP FY2016: a later filing puts the quarterly 0.15 on the year while
    the 9M YTD is 0.45: the year is the rate error, the Q4 0.15 is right."""
    b = Book()
    q = b.filing("B-1", "2016-11-05")
    k = b.filing("B-2", "2017-03-01", "10-K")
    b.add(DPS_DECL, "0.45", "2016-01-01", "2016-09-30", q)
    b.add(DPS_DECL, "0.15", "2016-10-01", "2016-12-31", k)
    b.add(DPS_DECL, "0.15", "2016-01-01", "2016-12-31", k)
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2016-10-01", "2016-12-31").status
        == sb.SHOWN
    )


def test_scale_guard_compares_within_a_local_window():
    """C 2012 quarterly DPS 0.01 vs 0.51+ five years later: real dividend
    growth, not a units error."""
    b = Book()
    vals = [("2011-01-01", "2011-03-31", "0.01"), ("2011-04-01", "2011-06-30", "0.01"),
            ("2011-07-01", "2011-09-30", "0.01"), ("2012-01-01", "2012-03-31", "0.01"),
            ("2017-01-01", "2017-03-31", "0.60"), ("2017-04-01", "2017-06-30", "0.60"),
            ("2017-07-01", "2017-09-30", "0.60"), ("2017-10-01", "2017-12-31", "0.60"),
            ("2018-01-01", "2018-03-31", "0.60")]  # fmt: skip
    for i, (s_, e, v) in enumerate(vals):
        b.add(
            DPS_DECL,
            v,
            s_,
            e,
            b.filing(
                f"C-{i}", (date.fromisoformat(e) + timedelta(days=35)).isoformat()
            ),
        )
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2012-01-01", "2012-03-31").status
        == sb.SHOWN
    )


def test_eps_original_is_never_dropped_as_a_label_shift():
    """The original 10-Q's Q1 0.40 equals its prior-year comparative 0.40 (a
    normal coincidence); a later 10-K copies Q2's 0.45 onto Q1."""
    b = Book()
    q = b.filing("E-1", "2019-05-01")
    k = b.filing("E-2", "2020-02-20", "10-K")
    b.add(EPS_D, "0.40", "2019-01-01", "2019-03-31", q)
    b.add(EPS_D, "0.40", "2018-01-01", "2018-03-31", q)
    b.add(EPS_D, "0.45", "2019-01-01", "2019-03-31", k)
    b.add(EPS_D, "0.45", "2019-04-01", "2019-06-30", k)
    res = run(b)
    cell = b.cell(res, "diluted_eps_resolved", "2019-01-01", "2019-03-31")
    assert cell.status == sb.SHOWN and cell.value == D("0.40")


def test_rate_on_longer_context_is_found_across_dividend_tags():
    """LEA's original 10-Q: 9M Declared 0.20 while its 3-month value is filed
    on CashPaid 0.20."""
    b = Book()
    q = b.filing("0000842162-14-000002", "2014-10-24")
    k = b.filing("0000842162-15-000013", "2015-04-24")
    b.add(DPS_DECL, "0.20", "2014-01-01", "2014-09-27", q)
    b.add(DPS_PAID, "0.20", "2014-06-29", "2014-09-27", q)
    b.add(DPS_DECL, "0.60", "2014-01-01", "2014-09-27", k)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2014-01-01", "2014-09-27")
    assert cell.status == sb.SHOWN and cell.value == D("0.60")


def test_one_off_five_percent_restatement_is_not_a_stock_dividend():
    """BAC/PAYX/CCI-like: copies ~5% apart on two tags once, no stock-dividend
    tag and no repeat a year later: not held (Verifier run 3)."""
    b = Book()
    a = b.filing("R-1", "2017-02-25", "10-K")
    c = b.filing("R-2", "2018-02-25", "10-K")
    for s_, e, v in (
        ("2016-01-01", "2016-12-31", "1.47"),
        ("2015-01-01", "2015-12-31", "1.31"),
    ):
        for tag in (EPS_B, EPS_D):
            b.add(tag, v, s_, e, a)
            b.add(tag, str((D(v) / D("1.05")).quantize(D("0.01"))), s_, e, c)
    b.add(EPS_D, "1.12", "2014-01-01", "2014-12-31", a)
    res = run(b)
    assert all(e.status == "rejected" for e in res.events)
    assert (
        b.cell(res, "diluted_eps_resolved", "2014-01-01", "2014-12-31").status
        == sb.SHOWN
    )


def test_shifted_later_majority_does_not_beat_two_originals():
    """PPL 2022-06 one-month DPS: originals 0000922224-22-000042/-000049 say
    0.225; three 2023 10-Qs put the 2023 rate 0.24 on the comparative (and file
    2023-06 = 0.24 beside it)."""
    b = Book()
    o1 = b.filing("0000922224-22-000042", "2022-08-01")
    o2 = b.filing("0000922224-22-000049", "2022-11-01")
    later = [
        b.filing(f"0000922224-23-0000{n}", f"2023-0{m}-01")
        for n, m in ((31, 7), (45, 8), (49, 9))
    ]
    for acc in (o1, o2):
        b.add(DPS_DECL, "0.225", "2022-06-01", "2022-06-30", acc)
    for acc in later:
        b.add(DPS_DECL, "0.24", "2022-06-01", "2022-06-30", acc)
        b.add(DPS_DECL, "0.24", "2023-06-01", "2023-06-30", acc)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2022-06-01", "2022-06-30")
    assert cell.status == sb.SHOWN and cell.value == D("0.225")


def test_three_eps_vintages_are_held():
    """Dominion Q1 2024 EPS: 0.78 / 0.50 / 0.46 in three vintages."""
    b = Book()
    for i, v in enumerate(("0.78", "0.50", "0.50", "0.46")):
        b.add(
            EPS_D,
            v,
            "2024-01-01",
            "2024-03-31",
            b.filing(f"D-{i}", f"202{4 + i // 2}-0{2 + i}-01"),
        )
    res = run(b)
    assert (
        b.cell(res, "diluted_eps_resolved", "2024-01-01", "2024-03-31").status
        == sb.HIDE_RESTATED
    )


def test_mixed_dividend_tags_with_equal_values_are_one_basis():
    """NSC/AMGN/SSNC: Declared and CashPaid equal on every common period."""
    b = Book()
    for i, (s_, e_) in enumerate((("2019-01-01", "2019-03-31"), ("2019-04-01", "2019-06-30"),
                                  ("2019-07-01", "2019-09-30"))):  # fmt: skip
        f = b.filing(f"N-{i}", f"2019-{4 + 3 * i:02d}-25")
        b.add(DPS_DECL, "0.86", s_, e_, f)
        b.add(DPS_PAID, "0.86", s_, e_, f)
    k = b.filing("N-9", "2020-02-05", "10-K")
    b.add(DPS_PAID, "0.94", "2019-10-01", "2019-12-31", k)  # only on CashPaid
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2019-10-01", "2019-12-31").status
        == sb.SHOWN
    )


def test_annual_total_check_uses_true_quarters_only():
    """AMGN FY2023 DPS 8.64 = 2.13 x 3 + 2.25; one-month and instant contexts
    (Oct 2.13, Dec 2.25) must not be counted as extra quarters."""
    b = Book()
    k = b.filing("A-1", "2024-02-15", "10-K")
    for s_, e_, v in (("2023-01-01", "2023-03-31", "2.13"), ("2023-04-01", "2023-06-30", "2.13"),
                      ("2023-07-01", "2023-09-30", "2.13"), ("2023-10-01", "2023-12-31", "2.25"),
                      ("2023-10-01", "2023-10-31", "2.13"), ("2023-12-01", "2023-12-31", "2.25")):  # fmt: skip
        b.add(DPS_DECL, v, s_, e_, k)
    b.add(DPS_DECL, "8.64", "2023-01-01", "2023-12-31", k)
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2023-01-01", "2023-12-31").status
        == sb.SHOWN
    )


def test_per_share_move_without_share_counts_is_not_a_split():
    """IONS 2021: EPS basic and diluted re-presented 5:4 on several periods,
    no share count moved: a restatement, not a split candidate."""
    b = Book()
    a = b.filing("I-1", "2021-02-25", "10-K")
    c = b.filing("I-2", "2021-05-05")
    for s_, e, v in (
        ("2020-01-01", "2020-12-31", "2.50"),
        ("2019-01-01", "2019-12-31", "1.75"),
    ):
        for tag in (EPS_B, EPS_D):
            b.add(tag, v, s_, e, a)
            b.add(tag, str(D(v) * 4 / 5), s_, e, c)
    b.add(EPS_D, "1.10", "2018-01-01", "2018-12-31", a)
    res = run(b)
    assert all(e.status == "rejected" for e in res.events)
    assert (
        b.cell(res, "diluted_eps_resolved", "2018-01-01", "2018-12-31").status
        == sb.SHOWN
    )


def test_disclosure_beside_a_confirmed_split_is_not_a_second_candidate():
    """GSAT 2025: 0.6667 ratio fact disclosed beside its confirmed 1:15."""
    b = Book()
    pre = b.filing("G-1", "2025-02-01", "10-K")
    post = b.filing("G-2", "2025-03-10")
    for s_, e, v, w in (
        ("2024-01-01", "2024-09-30", "-0.42", "1812345678"),
        ("2023-01-01", "2023-12-31", "-0.37", "1790123456"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, v, s_, e, pre)
            b.add(tag, str(D(v) * 15), s_, e, post)
        b.add("WeightedAverageNumberOfSharesOutstandingBasic", w, s_, e, pre)
        b.add(
            "WeightedAverageNumberOfSharesOutstandingBasic",
            str(int(w) // 15),
            s_,
            e,
            post,
        )
    b.add(RATIO, "0.6667", None, "2025-02-10", post)
    res = run(b)
    assert "review" not in [e.status for e in res.events]


def test_later_comparatives_without_own_vintage_are_shown_as_filed():
    """PPL 2022-06 one-month DPS exists only as 2023 comparatives, each equal
    to the 2023-06 value in the same filing (0.24); the originals report the
    quarter (0.225) on another context."""
    b = Book()
    for n, m in ((31, 5), (45, 8), (49, 9)):
        acc = b.filing(f"0000922224-23-0000{n}", f"2023-0{m}-01")
        b.add(DPS_DECL, "0.24", "2022-06-01", "2022-06-30", acc)
        if m > 6:  # the May 10-Q cannot hold June 2023
            b.add(DPS_DECL, "0.24", "2023-06-01", "2023-06-30", acc)
    res = run(b)
    # rule withdrawn (Verifier run 4: constant dividend rates made every later
    # comparative "equal next year's value"; FNB, WAL, EWBC, MSM, MS, AM, NEM)
    cell = b.cell(res, "dividends_per_share_resolved", "2022-06-01", "2022-06-30")
    assert cell.status == sb.SHOWN


def test_first_dividend_quarter_is_not_an_annual_amount():
    """MSI Q3 2011: first dividend 0.22 after three zero quarters."""
    b = Book()
    for i, (s_, e, v) in enumerate((("2010-10-03", "2011-01-01", "0"), ("2011-01-02", "2011-04-02", "0"),
                                    ("2011-04-03", "2011-07-02", "0"), ("2011-07-03", "2011-10-01", "0.22"),
                                    ("2011-10-02", "2011-12-31", "0.22"))):  # fmt: skip
        b.add(
            DPS_DECL,
            v,
            s_,
            e,
            b.filing(
                f"M-{i}", (date.fromisoformat(e) + timedelta(days=35)).isoformat()
            ),
        )
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2011-07-03", "2011-10-01").status
        == sb.SHOWN
    )


def test_later_comparative_with_constant_rate_and_an_original_is_shown():
    """A later 10-K repeats a constant 0.30 dividend on last year's quarter
    (equal to this year's): the period's own 10-Q also files 0.30, so it is
    shown, not held."""
    b = Book()
    q = b.filing("K-1", "2021-08-01")
    k = b.filing("K-2", "2022-08-01")
    b.add(DPS_DECL, "0.30", "2021-04-01", "2021-06-30", q)
    b.add(DPS_DECL, "0.30", "2021-04-01", "2021-06-30", k)
    b.add(DPS_DECL, "0.30", "2022-04-01", "2022-06-30", k)
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2021-04-01", "2021-06-30").status
        == sb.SHOWN
    )


def test_two_own_vintage_dividend_copies_beat_a_later_majority():
    """PPL 2022-06 one-month DPS as filed: 0.225 in the Aug and Nov 2022
    10-Qs; 0.24 in three 2023 10-Qs (the 2023 quarterly rate)."""
    b = Book()
    for acc, filed, v in (
        ("0000922224-22-000042", "2022-08-03", "0.225"),
        ("0000922224-22-000049", "2022-11-04", "0.225"),
        ("0000922224-23-000031", "2023-05-04", "0.24"),
        ("0000922224-23-000045", "2023-08-04", "0.24"),
        ("0000922224-23-000049", "2023-11-02", "0.24"),
    ):
        b.add(DPS_DECL, v, "2022-06-01", "2022-06-30", b.filing(acc, filed))
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2022-06-01", "2022-06-30")
    assert cell.status == sb.SHOWN and cell.value == D("0.225")


def test_year_totals_choose_the_filed_quarter_values():
    """COST FY2013: Q2 own-vintage 10-Q 0.275 (regular only) vs 10-K 7.275
    (with the $7 special); FY 8.17 in 0000909832-14-000021."""
    b = Book()
    q2 = b.filing("COST-Q2", "2013-03-10")
    k = b.filing("0000909832-14-000021", "2014-10-15", "10-K")
    q3 = b.filing("COST-Q3", "2013-06-05")
    vals = (("2012-09-03", "2012-11-25", "0.275"), ("2012-11-26", "2013-02-17", None),
            ("2013-02-18", "2013-05-12", "0.31"), ("2013-05-13", "2013-09-01", "0.31"))  # fmt: skip
    for s_, e_, v in vals:
        if v:
            b.add(DPS_DECL, v, s_, e_, k)
    b.add(DPS_DECL, "0.275", "2012-11-26", "2013-02-17", q2)
    b.add(DPS_DECL, "0.275", "2012-11-26", "2013-02-17", q3)
    b.add(DPS_DECL, "7.275", "2012-11-26", "2013-02-17", k)
    b.add(DPS_DECL, "8.17", "2012-09-03", "2013-09-01", k)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2012-11-26", "2013-02-17")
    assert cell.status == sb.SHOWN and cell.value == D("7.275")


def test_year_totals_fix_two_shifted_quarters_together():
    """OKE 2014: FY 2.125 = 0.40 + 0.56 + 0.575 + 0.59; the own-vintage Q2
    and Q3 copies carry the next quarter's rate (0.575, 0.59)."""
    b = Book()
    k = b.filing("OKE-K", "2015-02-24", "10-K")
    q2 = b.filing("OKE-Q2", "2014-08-05")
    q3 = b.filing("OKE-Q3", "2014-11-04")
    b.add(DPS_DECL, "0.40", "2014-01-01", "2014-03-31", k)
    for acc, v2, v3 in ((q2, "0.575", None), (q3, None, "0.59"), (k, "0.56", "0.575")):
        if v2:
            b.add(DPS_DECL, v2, "2014-04-01", "2014-06-30", acc)
        if v3:
            b.add(DPS_DECL, v3, "2014-07-01", "2014-09-30", acc)
    b.add(
        DPS_DECL, "0.575", "2014-04-01", "2014-06-30", b.filing("OKE-Q2b", "2014-09-01")
    )
    b.add(
        DPS_DECL, "0.59", "2014-07-01", "2014-09-30", b.filing("OKE-Q3b", "2014-12-01")
    )
    b.add(DPS_DECL, "0.59", "2014-10-01", "2014-12-31", k)
    b.add(DPS_DECL, "2.125", "2014-01-01", "2014-12-31", k)
    res = run(b)
    assert b.cell(
        res, "dividends_per_share_resolved", "2014-04-01", "2014-06-30"
    ).value == D("0.56")
    assert b.cell(
        res, "dividends_per_share_resolved", "2014-07-01", "2014-09-30"
    ).value == D("0.575")


def test_year_solve_leaves_an_ambiguous_year_alone():
    b = Book()
    k = b.filing("A-K", "2021-02-20", "10-K")
    q = b.filing("A-Q", "2020-08-01")
    for s_, e_ in (("2020-01-01", "2020-03-31"), ("2020-04-01", "2020-06-30"),
                   ("2020-07-01", "2020-09-30"), ("2020-10-01", "2020-12-31")):  # fmt: skip
        b.add(DPS_DECL, "0.50", s_, e_, k)
    b.add(DPS_DECL, "0.50", "2020-04-01", "2020-06-30", q)
    b.add(DPS_DECL, "2.00", "2020-01-01", "2020-12-31", k)
    res = run(b)
    assert b.cell(
        res, "dividends_per_share_resolved", "2020-04-01", "2020-06-30"
    ).value == D("0.50")


def test_forward_split_seen_through_weighted_average_shares():
    """CVNA 2026 5-for-1: no cover or balance-sheet count, basic weighted
    shares 137.6M (FY2025 10-K) -> 717.7M (Q2 2026 10-Q), ratio fact 0.2 (the
    filer's inverted convention); FY2021 filed -1.63 becomes -0.326."""
    b = Book()
    k21 = b.filing("CV-21", "2022-02-24", "10-K")
    k25 = b.filing("CV-25", "2026-02-18", "10-K")
    q26 = b.filing("0001690820-26-000055", "2026-07-29")
    b.add(EPS_D, "-1.63", "2021-01-01", "2021-12-31", k21)
    b.add(
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "135412000",
        "2021-01-01",
        "2021-12-31",
        k21,
    )
    b.add(
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "137634000",
        "2025-01-01",
        "2025-12-31",
        k25,
    )
    b.add(
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "717691000",
        "2026-04-01",
        "2026-06-30",
        q26,
    )
    b.add(RATIO, "0.2", None, "2026-05-08", q26)
    res = run(b)
    assert [(e.ratio, e.status) for e in res.events if e.status == "confirmed"] == [
        (5, "confirmed")
    ]
    assert b.cell(res, "diluted_eps_resolved", "2021-01-01", "2021-12-31").value == D(
        "-0.326"
    )


def test_invariant_hides_only_cells_filed_up_to_the_last_contradiction():
    """CBSH: cells re-filed after the last contradicting filing are shown."""
    b = Book()
    a = b.filing("C-1", "2023-02-01", "10-K")
    q = b.filing("C-2", "2023-05-01")
    c = b.filing("C-3", "2024-02-01", "10-K")
    late = b.filing("C-4", "2026-02-20", "10-K")
    for s_, e, v in (
        ("2022-01-01", "2022-12-31", "4.00"),
        ("2021-01-01", "2021-12-31", "3.00"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, v, s_, e, a)
            b.add(tag, v, s_, e, c)
    b.add(EPS_D, "1.10", "2023-01-01", "2023-03-31", q)
    b.add(EPS_D, "4.20", "2025-01-01", "2025-12-31", late)
    b.add(COVER, "100000000", None, "2023-01-25", a)
    b.add(COVER, "100500000", None, "2023-04-25", q)
    b.add(COVER, "201000000", None, "2024-01-25", c)
    b.add(COVER, "202000000", None, "2026-02-10", late)
    b.add(RATIO, "2", None, "2023-09-01", c)
    res = run(b)
    assert res.violations
    assert (
        b.cell(res, "diluted_eps_resolved", "2022-01-01", "2022-12-31").status
        == sb.HIDE_COMPANY_INVARIANT
    )
    assert (
        b.cell(res, "diluted_eps_resolved", "2025-01-01", "2025-12-31").status
        == sb.SHOWN
    )


def test_amendment_share_counts_are_not_series_points():
    b = Book()
    a = b.filing("S-1", "2024-02-01", "10-K")
    amend = b.filing("S-2", "2024-09-01", "10-Q/A")
    b.add(COVER, "100000000", None, "2024-01-25", a)
    b.add(COVER, "20000000", None, "2024-08-25", amend)
    series = sb.build_share_series(b.facts)
    assert [f.accession for f in series] == ["S-1"]


def test_year_solve_uses_the_nine_month_total_without_a_filed_q4():
    """COP 2021 as filed: Q4 dividend only derived; the "declared" tag
    disagrees with itself (9M 0.46 and 1.75; Q3 0.46 and 0.89 = two
    declarations), CashPaid gives 9M 1.29 and Q3 0.43 (Verifier run 4: right
    Q3 is 0.43, FY 1.75 = 0.43 x 3 + 0.46)."""
    b = Book()
    q1 = b.filing("COP-Q1", "2021-05-06")
    q2 = b.filing("COP-Q2", "2021-08-05")
    q3 = b.filing("COP-Q3", "2021-11-04")
    k = b.filing("COP-K", "2022-02-17", "10-K")
    q3b = b.filing("COP-Q3b", "2022-11-03")
    # COP's quarters are filed on CashPaid (its dividend basis)
    for s_, e_, fd in (("2020-01-01", "2020-03-31", "2020-05-05"),
                       ("2020-04-01", "2020-06-30", "2020-08-04"),
                       ("2020-07-01", "2020-09-30", "2020-11-03")):  # fmt: skip
        b.add(DPS_PAID, "0.42", s_, e_, b.filing(f"COP-{s_}", fd))
    b.add(DPS_PAID, "0.43", "2021-01-01", "2021-03-31", q1)
    b.add(
        DPS_DECL, "0.43", "2021-01-01", "2021-03-31", b.filing("COP-Q1b", "2022-05-05")
    )
    b.add(DPS_PAID, "0.43", "2021-04-01", "2021-06-30", q2)
    b.add(
        DPS_DECL, "0.43", "2021-04-01", "2021-06-30", b.filing("COP-Q2b", "2022-08-04")
    )
    b.add(DPS_PAID, "0.86", "2021-01-01", "2021-06-30", q2)
    b.add(DPS_PAID, "0.43", "2021-07-01", "2021-09-30", q3)
    b.add(DPS_DECL, "0.46", "2021-07-01", "2021-09-30", q3)
    b.add(DPS_DECL, "0.89", "2021-07-01", "2021-09-30", q3b)
    b.add(DPS_PAID, "1.29", "2021-01-01", "2021-09-30", q3)
    b.add(DPS_DECL, "0.46", "2021-01-01", "2021-09-30", q3)
    b.add(DPS_DECL, "1.75", "2021-01-01", "2021-09-30", q3b)
    b.add(DPS_DECL, "1.75", "2021-01-01", "2021-12-31", k)
    res = run(b)
    cell = b.cell(res, "dividends_per_share_resolved", "2021-07-01", "2021-09-30")
    assert cell.status == sb.SHOWN and cell.value == D("0.43")
    nine = b.cell(res, "dividends_per_share_resolved", "2021-01-01", "2021-09-30")
    assert nine.status == sb.SHOWN and nine.value == D("1.29")


def test_year_solve_hides_a_nine_month_cell_no_filed_copy_adds_up():
    """A 9M dividend whose filed copies disagree (0.46 / 1.75) and none
    equals the solved quarters' sum (0.43 x 3) is hidden, not shown."""
    b = Book()
    q1 = b.filing("X-Q1", "2021-05-06")
    q2 = b.filing("X-Q2", "2021-08-05")
    q3 = b.filing("X-Q3", "2021-11-04")
    k = b.filing("X-K", "2022-02-17", "10-K")
    q3b = b.filing("X-Q3b", "2022-11-03")
    q3c = b.filing("X-Q3c", "2023-11-02")
    b.add(DPS_DECL, "0.43", "2021-01-01", "2021-03-31", q1)
    b.add(DPS_DECL, "0.43", "2021-04-01", "2021-06-30", q2)
    b.add(DPS_DECL, "0.43", "2021-07-01", "2021-09-30", q3)
    b.add(DPS_DECL, "0.47", "2021-07-01", "2021-09-30", q3b)
    b.add(DPS_DECL, "0.46", "2021-10-01", "2021-12-31", k)
    b.add(DPS_DECL, "0.46", "2021-01-01", "2021-09-30", q3)
    b.add(DPS_DECL, "1.75", "2021-01-01", "2021-09-30", q3b)
    b.add(DPS_DECL, "1.75", "2021-01-01", "2021-09-30", q3c)
    b.add(DPS_DECL, "1.75", "2021-01-01", "2021-12-31", k)
    res = run(b)
    nine = b.cell(res, "dividends_per_share_resolved", "2021-01-01", "2021-09-30")
    assert nine.status == sb.HIDE_DPS_INVALID


# --------------------------------------------------------------------------
# Verifier run 5 (VERIFY-SPLIT-RUN5-2026-10-26.md)
# --------------------------------------------------------------------------
def _after(end: str, days: int = 40) -> str:
    return (date.fromisoformat(end) + timedelta(days=days)).isoformat()


def test_eps_copy_off_by_a_units_scale_loses_to_the_majority():
    """NPO Q3 2022 diluted: 1.29 in two 10-Qs, 1,290,000 in the 10-K."""
    b = Book()
    q = b.filing("NPO-Q", "2022-11-07")
    k = b.filing("NPO-K", "2023-03-01", "10-K")
    q2 = b.filing("NPO-Q2", "2023-10-31")
    for acc, v in ((q, "1.29"), (k, "1290000"), (q2, "1.29")):
        b.add(EPS_D, v, "2022-07-01", "2022-09-30", acc)
    cell = b.cell(run(b), "diluted_eps_resolved", "2022-07-01", "2022-09-30")
    assert cell.status == sb.SHOWN and cell.value == D("1.29")


def test_eps_units_scale_tie_is_decided_by_the_local_magnitude():
    """BE Q3 2025 diluted: -100 in the original 10-Q, -0.10 a year later;
    BE's other quarters are cents."""
    b = Book()
    q = b.filing("BE-Q", "2025-10-28")
    q2 = b.filing("BE-Q2", "2026-10-22")
    b.add(EPS_D, "-100", "2025-07-01", "2025-09-30", q)
    b.add(EPS_D, "-0.1", "2025-07-01", "2025-09-30", q2)
    for i, (s_, e_, v) in enumerate((("2025-01-01", "2025-03-31", "-0.1"),
                                     ("2025-04-01", "2025-06-30", "0.03"),
                                     ("2024-10-01", "2024-12-31", "0.2"))):  # fmt: skip
        b.add(EPS_D, v, s_, e_, b.filing(f"BE-{i}", _after(e_)))
    cell = b.cell(run(b), "diluted_eps_resolved", "2025-07-01", "2025-09-30")
    assert cell.status == sb.SHOWN and cell.value == D("-0.1")


def test_eps_units_scale_tie_without_local_history_is_hidden():
    b = Book()
    b.add(EPS_D, "-100", "2025-07-01", "2025-09-30", b.filing("X-Q", "2025-10-28"))
    b.add(EPS_D, "-0.1", "2025-07-01", "2025-09-30", b.filing("X-Q2", "2026-10-22"))
    cell = b.cell(run(b), "diluted_eps_resolved", "2025-07-01", "2025-09-30")
    assert cell.status == sb.HIDE_UNITS_SCALE


def test_share_count_units_scale_original_does_not_block_the_cell():
    """AM 2019-12-31: the 10-K files 484,042; four later filings 484,042,000."""
    b = Book()
    k = b.filing("AM-K", "2020-02-12", "10-K")
    b.add(BS_SHARES, "484042", None, "2019-12-31", k)
    for i, fd in enumerate(("2020-04-29", "2020-07-29", "2020-10-28")):
        b.add(BS_SHARES, "484042000", None, "2019-12-31", b.filing(f"AM-{i}", fd))
    cell = b.cell(run(b), "shares_outstanding_resolved", None, "2019-12-31")
    assert cell.status == sb.SHOWN and cell.value == D("484042000")


def test_share_count_corrected_by_a_prompt_amendment():
    """ANF cover 2017-06-01: 10-Q 86,016,786, 10-Q/A next day 68,016,186."""
    b = Book()
    b.add(COVER, "86016786", None, "2017-06-01", b.filing("ANF-Q", "2017-06-05"))
    b.add(
        COVER,
        "68016186",
        None,
        "2017-06-01",
        b.filing("ANF-QA", "2017-06-06", "10-Q/A"),
    )
    cell = b.cell(run(b), "shares_outstanding_resolved", None, "2017-06-01")
    assert cell.status == sb.SHOWN and cell.value == D("68016186")


def test_amended_original_count_is_not_a_share_step():
    """SNDK: 10-Q cover 114,863,251 corrected by the 10-Q/A to 144,863,251;
    the typo must not read as a 5:4 step."""
    b = Book()
    b.add(COVER, "144000000", None, "2024-11-01", b.filing("S-1", "2024-11-08"))
    b.add(COVER, "114863251", None, "2025-02-27", b.filing("S-2", "2025-03-07"))
    b.add(
        COVER, "144863251", None, "2025-02-27", b.filing("S-2A", "2025-03-17", "10-Q/A")
    )
    b.add(COVER, "145100000", None, "2025-05-01", b.filing("S-3", "2025-05-12"))
    res = run(b)
    assert all(e.status == "rejected" for e in res.events)


def test_lone_later_share_count_does_not_beat_the_original():
    """TTEK 2019-06-30: 54,714,000 in its own 10-Q, 54,728,000 in one later
    10-Q's comparative."""
    b = Book()
    b.add(BS_SHARES, "54714000", None, "2019-06-30", b.filing("T-Q", "2019-08-02"))
    b.add(BS_SHARES, "54728000", None, "2019-06-30", b.filing("T-Q2", "2020-01-31"))
    cell = b.cell(run(b), "shares_outstanding_resolved", None, "2019-06-30")
    assert cell.status == sb.SHOWN and cell.value == D("54714000")


def test_offering_sized_share_step_alone_is_not_a_split_candidate():
    """SYRE 2025: cover 60.4M -> 77.6M (+28%) with no per-share or ratio
    evidence: not a 5:4 review that hides every earlier filing."""
    b = Book()
    b.add(COVER, "60400960", None, "2025-07-31", b.filing("Y-1", "2025-08-05"))
    b.add(COVER, "77592130", None, "2025-10-29", b.filing("Y-2", "2025-11-04"))
    b.add(EPS_D, "-0.5", "2025-04-01", "2025-06-30", "Y-1")
    res = run(b)
    assert all(e.status == "rejected" for e in res.events)
    assert (
        b.cell(res, "diluted_eps_resolved", "2025-04-01", "2025-06-30").status
        == sb.SHOWN
    )


def test_stale_balance_sheet_count_is_not_the_filings_current_count():
    """LYFT 10-K 2020-02-28 carries CommonStockSharesOutstanding at
    2018-12-31 only; against a 2021 weighted average it read as a 15x step."""
    b = Book()
    k = b.filing("L-K", "2020-02-28", "10-K")
    q = b.filing("L-Q", "2021-05-06")
    b.add(BS_SHARES, "22438472", None, "2018-12-31", k)
    b.add(
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "326165000",
        "2021-01-01",
        "2021-03-31",
        q,
        unit="shares",
    )
    b.add(EPS_D, "-2.23", "2019-04-01", "2019-06-30", k)
    res = run(b)
    assert all(e.status == "rejected" for e in res.events)
    assert (
        b.cell(res, "diluted_eps_resolved", "2019-04-01", "2019-06-30").status
        == sb.SHOWN
    )


def test_zero_per_share_is_shown_whatever_the_basis():
    """QXO Q2 2018 EPS 0 in a filing before an unconfirmed 1:30 candidate
    (filed pairs only; 1:5 here)."""
    b = Book()
    q = b.filing("Q-1", "2018-08-10")
    q2 = b.filing("Q-2", "2018-11-10")
    b.add(EPS_D, "0", "2018-04-01", "2018-06-30", q)
    for tag, v in ((EPS_D, "0.10"), (EPS_B, "0.10")):
        b.add(tag, v, "2017-01-01", "2017-12-31", q)
        b.add(tag, str(D(v) * 5), "2017-01-01", "2017-12-31", q2)
    for v, acc in (("30000000", q), ("6000000", q2)):
        b.add(
            "WeightedAverageNumberOfSharesOutstandingBasic",
            v,
            "2017-01-01",
            "2017-12-31",
            acc,
            unit="shares",
        )
    res = run(b)
    assert any(e.status == "review" for e in res.events), res.events
    cell = b.cell(res, "diluted_eps_resolved", "2018-04-01", "2018-06-30")
    assert cell.status == sb.SHOWN and cell.value == D("0")


def test_confirmed_split_inside_an_issuance_step_places_earlier_filings():
    """NLY 1:4 in 2022 with offerings: cover 1.46B -> 0.42B (no clean ratio);
    earlier filings are on the old basis, not a conflict."""
    b = Book()
    a = b.filing("N-1", "2022-08-01")
    c = b.filing("N-2", "2022-11-03")
    b.add(COVER, "1460000000", None, "2022-07-29", a)
    b.add(COVER, "420000000", None, "2022-10-31", c)
    b.add(RATIO, "0.25", None, "2022-09-23", c)
    for s_, e_, v in (
        ("2021-07-01", "2021-09-30", "0.55"),
        ("2022-04-01", "2022-06-30", "0.40"),
    ):
        for tag in (EPS_D, EPS_B):
            b.add(tag, v, s_, e_, a)
            b.add(tag, str(D(v) * 4), s_, e_, c)
    res = run(b)
    assert [e.status for e in res.events if e.ratio == Fraction(1, 4)] == ["confirmed"]
    fid = {f.accession: f.filing_id for f in b.facts}
    assert res.basis[fid["N-1"]].status == "consistent"


def test_annual_on_quarter_check_yields_to_the_filings_own_dividends_paid():
    """WY Q1 2022 1.63 (base 0.18 + variable 1.45): 1,218M paid over ~733M
    shares; it also equals four earlier quarters' sum by coincidence."""
    b = Book()
    for i, (s_, e_, v) in enumerate((("2021-01-01", "2021-03-31", "0.17"),
                                     ("2021-04-01", "2021-06-30", "0.17"),
                                     ("2021-07-01", "2021-09-30", "0.17"),
                                     ("2021-10-01", "2021-12-31", "1.12"))):  # fmt: skip
        b.add(DPS_PAID, v, s_, e_, b.filing(f"W-{i}", _after(e_)))
    q = b.filing("W-Q1", "2022-04-29")
    b.add(DPS_PAID, "1.63", "2022-01-01", "2022-03-31", q)
    b.add(
        "PaymentsOfDividendsCommonStock",
        "1218000000",
        "2022-01-01",
        "2022-03-31",
        q,
        unit="USD",
    )
    b.add(COVER, "733000000", None, "2022-04-22", q)
    cell = b.cell(run(b), "dividends_per_share_resolved", "2022-01-01", "2022-03-31")
    assert cell.status == sb.SHOWN and cell.value == D("1.63")


def test_annual_on_quarter_check_yields_to_two_own_vintage_copies():
    """HL-like sub-cent rates: 0.01125 filed twice (own 10-Q and the next
    year's comparative) equals four quarters' sum by coincidence."""
    b = Book()
    for i, (s_, e_, v) in enumerate((("2020-07-01", "2020-09-30", "0.0025"),
                                     ("2020-10-01", "2020-12-31", "0.0025"),
                                     ("2021-01-01", "2021-03-31", "0.0025"),
                                     ("2021-04-01", "2021-06-30", "0.00375"))):  # fmt: skip
        b.add(DPS_DECL, v, s_, e_, b.filing(f"H-{i}", _after(e_)))
    b.add(
        DPS_DECL, "0.01125", "2021-07-01", "2021-09-30", b.filing("H-Q3", "2021-11-05")
    )
    b.add(
        DPS_DECL, "0.01125", "2021-07-01", "2021-09-30", b.filing("H-Q3b", "2022-11-09")
    )
    cell = b.cell(run(b), "dividends_per_share_resolved", "2021-07-01", "2021-09-30")
    assert cell.status == sb.SHOWN and cell.value == D("0.01125")


def test_annual_amount_on_a_quarter_is_still_caught():
    """OGE Q1 2020 1.505 = the 2019 total, one filing, no paid amount."""
    b = Book()
    for i, (s_, e_, v) in enumerate((("2019-01-01", "2019-03-31", "0.365"),
                                     ("2019-04-01", "2019-06-30", "0.365"),
                                     ("2019-07-01", "2019-09-30", "0.3875"),
                                     ("2019-10-01", "2019-12-31", "0.3875"))):  # fmt: skip
        b.add(DPS_DECL, v, s_, e_, b.filing(f"O-{i}", _after(e_)))
    b.add(DPS_DECL, "1.505", "2020-01-01", "2020-03-31", b.filing("O-Q1", "2020-05-07"))
    cell = b.cell(run(b), "dividends_per_share_resolved", "2020-01-01", "2020-03-31")
    assert cell.status == sb.HIDE_DPS_INVALID


def test_annual_vs_quarters_counts_one_quarter_per_end_date():
    """BX FY2014 1.92 = 0.58 + 0.35 + 0.55 + 0.44; a second Q2 context
    (04-08 to 06-30, 0.35) must not be added twice."""
    b = Book()
    for i, (s_, e_, v) in enumerate((("2014-01-01", "2014-03-31", "0.58"),
                                     ("2014-04-01", "2014-06-30", "0.35"),
                                     ("2014-04-08", "2014-06-30", "0.35"),
                                     ("2014-07-01", "2014-09-30", "0.55"),
                                     ("2014-10-01", "2014-12-31", "0.44"))):  # fmt: skip
        b.add(
            DPS_DECL,
            v,
            s_,
            e_,
            b.filing(f"B-{i}", "2015-02-27", "10-K")
            if i == 4
            else b.filing(f"B-{i}", _after(e_)),
        )
    b.add(DPS_DECL, "1.92", "2014-01-01", "2014-12-31", "B-4")
    cell = b.cell(run(b), "dividends_per_share_resolved", "2014-01-01", "2014-12-31")
    assert cell.status == sb.SHOWN and cell.value == D("1.92")


def test_off_basis_annual_equal_to_its_basis_quarters_is_shown():
    """FE FY2016 Declared 1.44 = CashPaid 0.36 x 4 (FE's basis is CashPaid)."""
    b = Book()
    for i, (s_, e_) in enumerate((("2016-01-01", "2016-03-31"), ("2016-04-01", "2016-06-30"),
                                  ("2016-07-01", "2016-09-30"), ("2016-10-01", "2016-12-31"))):  # fmt: skip
        b.add(
            DPS_PAID,
            "0.36",
            s_,
            e_,
            b.filing(f"F-{i}", _after(e_))
            if i < 3
            else b.filing("F-K", "2017-02-21", "10-K"),
        )
    b.add(DPS_DECL, "1.44", "2016-01-01", "2016-12-31", "F-K")
    cell = b.cell(run(b), "dividends_per_share_resolved", "2016-01-01", "2016-12-31")
    assert cell.status == sb.SHOWN and cell.value == D("1.44")


def test_amended_typo_count_does_not_create_a_split_candidate():
    """An original cover count halved by a typo and corrected by a 10-Q/A
    within 60 days must not read as a 1:2 step (SNDK pattern)."""
    b = Book()
    b.add(COVER, "144000000", None, "2024-11-01", b.filing("S-1", "2024-11-08"))
    b.add(COVER, "72431625", None, "2025-02-27", b.filing("S-2", "2025-03-07"))
    b.add(
        COVER, "144863251", None, "2025-02-27", b.filing("S-2A", "2025-03-17", "10-Q/A")
    )
    b.add(COVER, "145100000", None, "2025-05-01", b.filing("S-3", "2025-05-12"))
    b.add(EPS_D, "0.50", "2024-07-01", "2024-09-30", "S-1")
    res = run(b)
    assert not [e for e in res.events if e.status in ("review", "confirmed")]
    assert (
        b.cell(res, "diluted_eps_resolved", "2024-07-01", "2024-09-30").status
        == sb.SHOWN
    )


def test_zero_declared_original_beside_cash_paid_gives_way_to_the_later_copy():
    """AES Q2 2020 pattern: the original 10-Q files Declared 0 next to
    CashPaid 0.1433; a later filing files Declared 0.1433. The zero is a
    contradicted original, not the value (Verifier run 5 fix 1)."""
    b = Book()
    for i, (s_, e_) in enumerate((("2019-01-01", "2019-03-31"), ("2019-04-01", "2019-06-30"),
                                  ("2019-07-01", "2019-09-30"), ("2019-10-01", "2019-12-31"),
                                  ("2020-01-01", "2020-03-31"))):  # fmt: skip
        b.add(DPS_DECL, "0.1433", s_, e_, b.filing(f"A-{i}", _after(e_)))
    a = b.filing("A-Q2", "2020-08-06")
    b.add(DPS_DECL, "0", "2020-04-01", "2020-06-30", a)
    b.add(DPS_PAID, "0.1433", "2020-04-01", "2020-06-30", a)
    b.add(
        DPS_DECL, "0.1433", "2020-04-01", "2020-06-30", b.filing("A-Q2b", "2021-08-06")
    )
    # a lone later copy on another rate does not beat the kept original
    b.add(
        DPS_DECL, "0.1505", "2020-04-01", "2020-06-30", b.filing("A-Q2c", "2022-08-06")
    )
    cell = b.cell(run(b), "dividends_per_share_resolved", "2020-04-01", "2020-06-30")
    assert cell.status == sb.SHOWN and cell.value == D("0.1433")


# --------------------------------------------------------------------------
# Run 7 (Verifier run 6): spans agree with their parts, quarter = YTD context,
# same-quarter declare-and-pay releases
# --------------------------------------------------------------------------
def _amt_book(
    fy_declared: str, fy_paid: str, year: int, decl: list[tuple[str, str]]
) -> Book:
    """AMT: Declared basis (declared 3-month quarters outnumber paid ones),
    dated declaration facts, and a 10-K whose full-year tags are swapped."""
    b = Book()
    for y in (2016, 2017, 2018, 2019):
        for qs, qe, fd in (("01-01", "03-31", "04-30"), ("04-01", "06-30", "07-30"),
                           ("07-01", "09-30", "10-30")):  # fmt: skip
            b.add(
                DPS_DECL,
                "1.00",
                f"{y}-{qs}",
                f"{y}-{qe}",
                b.filing(f"Q-{y}-{qs}", f"{y}-{fd}"),
            )
    q = b.filing(f"AMT-Q-{year}", f"{year}-10-26")
    for day, v in decl[:3]:
        b.add(DPS_DECL, v, day, day, q)
    k = b.filing(f"AMT-K-{year}", f"{year + 1}-02-27", "10-K")
    b.add(DPS_DECL, decl[3][1], decl[3][0], decl[3][0], k)
    late = b.filing(f"AMT-K-{year + 2}", f"{year + 3}-02-25", "10-K")
    b.add(DPS_DECL, fy_declared, f"{year}-01-01", f"{year}-12-31", late)
    b.add(DPS_PAID, fy_paid, f"{year}-01-01", f"{year}-12-31", late)
    return b


def test_full_year_dividend_takes_the_filed_copy_that_equals_its_declarations():
    """AMT FY2022 (0001053507-25-000025): Declared FY 4.30 counts three
    declarations; the four 2022 declarations sum to 5.86, filed as CashPaid."""
    b = _amt_book(
        "4.30",
        "5.86",
        2022,
        [
            ("2022-03-10", "1.40"),
            ("2022-05-18", "1.43"),
            ("2022-09-21", "1.47"),
            ("2022-12-07", "1.56"),
        ],
    )
    cell = b.cell(run(b), "dividends_per_share_resolved", "2022-01-01", "2022-12-31")
    assert cell.status == sb.SHOWN and cell.value == D("5.86")
    assert "dated facts" in cell.note


def test_full_year_dividend_swapped_tags_amt_2023():
    """AMT FY2023: Declared 6.31 is the paid sum; declarations 1.56 + 1.57 +
    1.62 + 1.70 = 6.45, filed as CashPaid."""
    b = _amt_book(
        "6.31",
        "6.45",
        2023,
        [
            ("2023-03-08", "1.56"),
            ("2023-05-24", "1.57"),
            ("2023-09-20", "1.62"),
            ("2023-12-13", "1.70"),
        ],
    )
    cell = b.cell(run(b), "dividends_per_share_resolved", "2023-01-01", "2023-12-31")
    assert cell.status == sb.SHOWN and cell.value == D("6.45")


def test_dated_facts_never_hide_when_no_filed_copy_equals_them():
    """Dated facts can be announcements that shift a dividend between
    quarters (JPM 6M 2018 1.12, run 7.2): they only choose between filed
    copies, so with no matching copy the filed value stays."""
    b = _amt_book(
        "4.30",
        "4.30",
        2022,
        [
            ("2022-03-10", "1.40"),
            ("2022-05-18", "1.43"),
            ("2022-09-21", "1.47"),
            ("2022-12-07", "1.56"),
        ],
    )
    cell = b.cell(run(b), "dividends_per_share_resolved", "2022-01-01", "2022-12-31")
    assert cell.status == sb.SHOWN and cell.value == D("4.30")


def test_full_year_dividend_left_alone_when_declarations_miss_a_quarter():
    """Three dated declarations cannot check a four-quarter year."""
    b = _amt_book(
        "4.30",
        "5.86",
        2022,
        [
            ("2022-03-10", "1.40"),
            ("2022-05-18", "1.43"),
            ("2022-06-21", "1.47"),
            ("2022-12-07", "1.56"),
        ],
    )
    cell = b.cell(run(b), "dividends_per_share_resolved", "2022-01-01", "2022-12-31")
    # Q3 has no declaration date: no evidence, the filed basis value stays
    assert cell.status == sb.SHOWN and cell.value == D("4.30")


def test_quarter_carrying_the_ytd_value_is_hidden_logi():
    """LOGI Q3 FY22 10-Q 0001032975-22-000006: Apr-Dec 0.95 and Oct-Dec 0.95
    while Jul-Sep was 0.95 (annual dividend paid in September)."""
    b = Book()
    q2 = b.filing("0001032975-21-000045", "2021-10-28")
    q3 = b.filing("0001032975-22-000006", "2022-01-27")
    b.add(DPS_PAID, "0.95", "2021-07-01", "2021-09-30", q2)
    b.add(DPS_PAID, "0.95", "2021-04-01", "2021-09-30", q2)
    b.add(DPS_PAID, "0.95", "2021-04-01", "2021-12-31", q3)
    b.add(DPS_PAID, "0.95", "2021-10-01", "2021-12-31", q3)
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2021-10-01", "2021-12-31").status
        == sb.HIDE_QTR_YTD
    )
    assert b.cell(
        res, "dividends_per_share_resolved", "2021-07-01", "2021-09-30"
    ).value == D("0.95")
    assert b.cell(
        res, "dividends_per_share_resolved", "2021-04-01", "2021-12-31"
    ).value == D("0.95")


def test_quarter_equal_to_ytd_stays_when_earlier_quarters_paid_nothing():
    """An annual dividend paid in the last quarter of the YTD: Q = YTD is right."""
    b = Book()
    q2 = b.filing("A-Q2", "2021-10-28")
    q3 = b.filing("A-Q3", "2022-01-27")
    b.add(DPS_PAID, "0", "2021-07-01", "2021-09-30", q2)
    b.add(DPS_PAID, "0.95", "2021-04-01", "2021-12-31", q3)
    b.add(DPS_PAID, "0.95", "2021-10-01", "2021-12-31", q3)
    cell = b.cell(run(b), "dividends_per_share_resolved", "2021-10-01", "2021-12-31")
    assert cell.status == sb.SHOWN and cell.value == D("0.95")


def _together_book(agree: bool) -> Book:
    """Declared basis; four quarters with both tags (equal unless agree is
    False); one later quarter filed on CashPaid only."""
    b = Book()
    for i, (qs, qe, fd) in enumerate((("2016-01-01", "2016-03-31", "2016-05-01"), ("2016-04-01", "2016-06-30", "2016-08-01"),
                                      ("2016-07-01", "2016-09-30", "2016-11-01"), ("2017-01-01", "2017-03-31", "2017-05-01"),
                                      ("2017-04-01", "2017-06-30", "2017-08-01"))):  # fmt: skip
        f = b.filing(f"T-{i}", fd)
        b.add(DPS_DECL, "0.50", qs, qe, f)
        b.add(DPS_PAID, "0.50" if agree or i else "0.48", qs, qe, f)
    for i, (qs, qe, fd) in enumerate(
        (
            ("2018-01-01", "2018-03-31", "2018-05-01"),
            ("2018-04-01", "2018-06-30", "2018-08-01"),
        )
    ):
        b.add(
            DPS_DECL, "0.50", qs, qe, b.filing(f"T-decl-{i}", fd)
        )  # Declared stays the basis
    f = b.filing("T-paid-only", "2017-11-01")
    b.add(DPS_PAID, "0.50", "2017-07-01", "2017-09-30", f)
    return b


def test_off_basis_quarter_released_when_company_declares_and_pays_together():
    """Verifier run 6: ~25 dividend_basis_pending holds (CMI, NSC, LIN, EXC,
    BAC ...) where the off-basis value is the same number on both bases."""
    b = _together_book(agree=True)
    cell = b.cell(run(b), "dividends_per_share_resolved", "2017-07-01", "2017-09-30")
    assert cell.status == sb.SHOWN and cell.value == D("0.50")
    assert "same quarter" in cell.note


def test_off_basis_quarter_stays_hidden_when_one_quarter_differs():
    """HWM Q1 2019 declared 0.08 vs paid 0.06: a real timing difference."""
    b = _together_book(agree=False)
    cell = b.cell(run(b), "dividends_per_share_resolved", "2017-07-01", "2017-09-30")
    assert cell.status == sb.HIDE_DPS_BASIS


def test_copy_from_a_10k_that_does_not_present_the_quarter_is_dropped_swk():
    """SWK Q4 2017 basic EPS 1.88 (two copies) vs -0.72 in the FY2019 10-K
    0000093556-20-000006, which presents 2019 and 2018 quarters only."""
    b = Book()
    k17 = b.filing("0000093556-18-000008", "2018-02-22", "10-K")
    k18 = b.filing("0000093556-19-000011", "2019-02-26", "10-K")
    k19 = b.filing("0000093556-20-000006", "2020-02-21", "10-K")
    b.add(EPS_B, "1.88", "2017-10-01", "2017-12-30", k17)
    b.add(EPS_B, "1.88", "2017-10-01", "2017-12-30", k18)
    b.add(EPS_B, "-0.72", "2017-10-01", "2017-12-30", k19)
    cell = b.cell(run(b), "basic_eps_resolved", "2017-10-01", "2017-12-30")
    assert cell.status == sb.SHOWN and cell.value == D("1.88")
    assert "does not present" in cell.note


def test_nine_month_copy_in_a_10k_is_dropped_form():
    """FORM 9M 2017 basic EPS 0.49 vs 0.03 in a 10-K (no 9M column)."""
    b = Book()
    q = b.filing("0001039399-17-000078", "2017-11-01")
    q18 = b.filing("0001039399-18-000085", "2018-10-31")
    k = b.filing("0001039399-19-000024", "2019-02-26", "10-K")
    b.add(EPS_B, "0.49", "2017-01-01", "2017-09-30", q)
    b.add(EPS_B, "0.49", "2017-01-01", "2017-09-30", q18)
    b.add(EPS_B, "0.03", "2017-01-01", "2017-09-30", k)
    cell = b.cell(run(b), "basic_eps_resolved", "2017-01-01", "2017-09-30")
    assert cell.status == sb.SHOWN and cell.value == D("0.49")


def test_swapped_quarter_pair_in_one_filing_is_dropped_nwsa():
    """NWSA FY2016 10-K 0001193125-16-679975 tags Jul-Sep 2014 0.30 and
    Jul-Sep 2015 0.11: each is the other quarter's consensus."""
    b = Book()
    q15 = b.filing("0001193125-14-399701", "2014-11-07")
    k15 = b.filing("0001193125-15-288946", "2015-08-13", "10-K")
    q16 = b.filing("0001193125-15-370000", "2015-11-06")
    k16 = b.filing("0001193125-16-679975", "2016-08-12", "10-K")
    q17 = b.filing("0001193125-16-760000", "2016-11-08")
    b.add(EPS_D, "0.11", "2014-07-01", "2014-09-30", q15)
    b.add(EPS_D, "0.11", "2014-07-01", "2014-09-30", k15)
    b.add(EPS_D, "0.11", "2014-07-01", "2014-09-30", q16)
    b.add(EPS_D, "0.30", "2014-07-01", "2014-09-30", k16)  # swapped
    b.add(EPS_D, "0.30", "2015-07-01", "2015-09-30", q16)
    b.add(EPS_D, "0.30", "2015-07-01", "2015-09-30", q17)
    b.add(EPS_D, "0.11", "2015-07-01", "2015-09-30", k16)  # swapped
    res = run(b)
    assert b.cell(res, "diluted_eps_resolved", "2014-07-01", "2014-09-30").value == D(
        "0.11"
    )
    assert b.cell(res, "diluted_eps_resolved", "2015-07-01", "2015-09-30").value == D(
        "0.30"
    )


def test_restated_prior_year_quarter_in_the_next_10q_is_still_hidden():
    """A real restatement often has ONE later copy (the next year's 10-Q
    comparative): it is presented and not a swap, so the hold stays."""
    b = Book()
    q = b.filing("R-Q1-2016", "2016-05-01")
    q2 = b.filing("R-Q1-2017", "2017-05-01")
    b.add(EPS_D, "0.40", "2016-01-01", "2016-03-31", q)
    b.add(EPS_D, "0.33", "2016-01-01", "2016-03-31", q2)
    b.add(EPS_D, "0.52", "2017-01-01", "2017-03-31", q2)
    cell = b.cell(run(b), "diluted_eps_resolved", "2016-01-01", "2016-03-31")
    assert cell.status == sb.HIDE_RESTATED


def test_10q_copy_of_a_quarter_two_years_back_is_dropped():
    """A 10-Q compares with the prior year only; a quarter two years back in
    it is an unpresented column."""
    b = Book()
    q = b.filing("A-Q3-2015", "2015-11-01")
    q2 = b.filing("A-Q3-2016", "2016-11-01")
    q3 = b.filing("A-Q3-2017", "2017-11-01")
    b.add(EPS_D, "0.40", "2015-07-01", "2015-09-30", q)
    b.add(EPS_D, "0.40", "2015-07-01", "2015-09-30", q2)
    b.add(EPS_D, "0.61", "2015-07-01", "2015-09-30", q3)
    cell = b.cell(run(b), "diluted_eps_resolved", "2015-07-01", "2015-09-30")
    assert cell.status == sb.SHOWN and cell.value == D("0.40")


def test_quarter_kept_when_the_ytd_contexts_carry_the_quarterly_rate_visa():
    """V FY2022 (0001403161-23-000031/-000072): every YTD context carries the
    quarterly rate 0.375; the quarters are right, the YTDs are not."""
    b = Book()
    q1 = b.filing("V-Q1", "2022-01-27")
    q2 = b.filing("V-Q2", "2022-04-27")
    q3 = b.filing("V-Q3", "2022-07-27")
    b.add(DPS_DECL, "0.375", "2021-10-01", "2021-12-31", q1)
    b.add(DPS_DECL, "0.375", "2022-01-01", "2022-03-31", q2)
    b.add(DPS_DECL, "0.375", "2021-10-01", "2022-03-31", q2)
    b.add(DPS_DECL, "0.375", "2022-04-01", "2022-06-30", q3)
    b.add(DPS_DECL, "0.375", "2021-10-01", "2022-06-30", q3)
    res = run(b)
    assert b.cell(
        res, "dividends_per_share_resolved", "2022-04-01", "2022-06-30"
    ).value == D("0.375")
    assert (
        b.cell(res, "dividends_per_share_resolved", "2021-10-01", "2022-06-30").status
        == sb.HIDE_DPS_INVALID
    )


def test_two_dated_facts_in_one_quarter_are_no_evidence_bac():
    """BAC 2016: five dated declaration/announcement facts (two in Q2); the
    filed FY 0.25 stays."""
    b = Book()
    k = b.filing("BAC-K", "2017-02-23", "10-K")
    for day, v in (
        ("2016-01-21", "0.05"),
        ("2016-04-27", "0.05"),
        ("2016-06-29", "0.075"),
        ("2016-07-27", "0.075"),
        ("2016-10-27", "0.075"),
    ):
        b.add(DPS_DECL, v, day, day, k)
    b.add(DPS_DECL, "0.25", "2016-01-01", "2016-12-31", k)
    cell = b.cell(run(b), "dividends_per_share_resolved", "2016-01-01", "2016-12-31")
    assert cell.status == sb.SHOWN and cell.value == D("0.25")


def test_one_copy_quarter_hidden_when_year_totals_agree_lfus():
    """LFUS FY2023 2.5 in three 10-Ks vs a one-copy Q4 0.6 (0.6+0.6+0.65+0.6 =
    2.45): the year stays, the one-copy quarter is hidden."""
    b = Book()
    qs = (
        ("2023-01-01", "2023-04-01", "0.6"),
        ("2023-04-02", "2023-07-01", "0.6"),
        ("2023-07-02", "2023-09-30", "0.65"),
    )
    for i, (s, e, v) in enumerate(qs):
        b.add(DPS_PAID, v, s, e, b.filing(f"L-Q{i}", f"2023-{4 + 3 * i:02d}-28"))
        b.add(DPS_PAID, v, s, e, b.filing(f"L-Q{i}-next", f"2024-{4 + 3 * i:02d}-28"))
    b.add(DPS_PAID, "0.6", "2023-10-01", "2023-12-30", b.filing("L-24Q", "2024-10-30"))
    for i, fd in enumerate(("2024-02-20", "2025-02-20", "2026-02-20")):
        b.add(
            DPS_PAID, "2.5", "2023-01-01", "2023-12-30", b.filing(f"L-K{i}", fd, "10-K")
        )
    res = run(b)
    assert b.cell(
        res, "dividends_per_share_resolved", "2023-01-01", "2023-12-30"
    ).value == D("2.5")
    assert (
        b.cell(res, "dividends_per_share_resolved", "2023-10-01", "2023-12-30").status
        == sb.HIDE_DPS_INVALID
    )


def test_swapped_pair_released_when_the_swapped_copy_is_the_earliest_nwsa():
    """NWSA Jul-Sep 2015 has two copies: 0.11 in the FY2016 10-K (swapped,
    the earliest) and 0.30 in the FY2017 10-K; Jul-Sep 2014 is 0.11 in two
    other filings and 0.30 in that same FY2016 10-K."""
    b = Book()
    q15 = b.filing("0001193125-14-399701", "2014-11-07")
    k15 = b.filing("0001193125-15-288946", "2015-08-13", "10-K")
    k16 = b.filing("0001193125-16-679975", "2016-08-12", "10-K")
    k17 = b.filing("0001193125-17-257248", "2017-08-11", "10-K")
    b.add(EPS_D, "0.11", "2014-07-01", "2014-09-30", q15)
    b.add(EPS_D, "0.11", "2014-07-01", "2014-09-30", k15)
    b.add(EPS_D, "0.30", "2014-07-01", "2014-09-30", k16)
    b.add(EPS_D, "0.11", "2015-07-01", "2015-09-30", k16)
    b.add(EPS_D, "0.30", "2015-07-01", "2015-09-30", k17)
    res = run(b)
    assert b.cell(res, "diluted_eps_resolved", "2014-07-01", "2014-09-30").value == D(
        "0.11"
    )
    cell = b.cell(res, "diluted_eps_resolved", "2015-07-01", "2015-09-30")
    assert cell.status == sb.SHOWN and cell.value == D("0.30")


def _fact(fid: int, filed: str) -> SourceFact:
    return SourceFact(
        fid,
        EPS_D,
        "usd/shares",
        1,
        date(2023, 1, 1),
        date(2023, 12, 31),
        "duration",
        D("-1.63"),
        fid,
        date.fromisoformat(filed),
        "10-K",
        f"A-{fid}",
        False,
        True,
    )


def test_post_event_copies_need_two_filings_after_every_live_event():
    """QXO FY2023: the 2024 and 2025 10-Ks, filed after the confirmed 1:8 of
    2024-08-14, re-present the year on the current basis."""
    ev = sb.Event(
        1, Fraction(1, 8), date(2024, 5, 1), date(2024, 8, 14), status="confirmed"
    )
    dead = sb.Event(
        2, Fraction(5, 4), date(2025, 5, 1), date(2025, 8, 14), status="rejected"
    )
    conv = [
        (_fact(1, "2024-03-01"), Fraction(1, 8), D("-0.20")),
        (_fact(2, "2025-02-20"), Fraction(1), D("-1.63")),
        (_fact(3, "2026-02-20"), Fraction(1), D("-1.63")),
    ]
    post = sb.post_event_copies(conv, [ev, dead])
    assert [x[0].fact_id for x in post] == [2, 3]
    assert (
        sb.post_event_copies(conv[:2], [ev, dead]) is None
    )  # one later copy never decides
    pending = sb.Event(
        3, Fraction(2), date(2025, 9, 1), date(2026, 3, 1), status="review"
    )
    assert (
        sb.post_event_copies(conv, [ev, pending]) is None
    )  # a live candidate after them


def test_logi_prior_ytd_with_two_values_still_hides_the_quarter():
    """LOGI files CHF and USD amounts on the same contexts (0.87 and 0.95);
    the prior YTD Apr-Sep holds both, the current Apr-Dec too."""
    b = Book()
    q2 = b.filing("0001032975-21-000045", "2021-10-28")
    q3 = b.filing("0001032975-22-000006", "2022-01-27")
    for v in ("0.95", "0.87"):
        b.add(DPS_PAID, v, "2021-07-01", "2021-09-30", q2)
        b.add(DPS_PAID, v, "2021-04-01", "2021-09-30", q2)
        b.add(DPS_PAID, v, "2021-04-01", "2021-12-31", q3)
        b.add(DPS_PAID, v, "2021-10-01", "2021-12-31", q3)
    cell = b.cell(run(b), "dividends_per_share_resolved", "2021-10-01", "2021-12-31")
    assert cell.status != sb.SHOWN


def test_second_quarter_kept_when_prior_period_is_only_q1_visa():
    """Visa Jan-Mar 2022 0.375 with the 6M context also 0.375: Q1 alone is not
    a prior year-to-date, so the quarter stays."""
    b = Book()
    q1 = b.filing("V-Q1", "2022-01-27")
    q2 = b.filing("V-Q2", "2022-04-27")
    b.add(DPS_DECL, "0.375", "2021-10-01", "2021-12-31", q1)
    b.add(DPS_DECL, "0.375", "2022-01-01", "2022-03-31", q2)
    b.add(DPS_DECL, "0.375", "2021-10-01", "2022-03-31", q2)
    cell = b.cell(run(b), "dividends_per_share_resolved", "2022-01-01", "2022-03-31")
    assert cell.status == sb.SHOWN and cell.value == D("0.375")


def test_year_below_its_quarters_is_hidden_even_with_many_copies_visa():
    """Visa FY 0.375 in three 10-Ks against four 0.375 quarters: the year
    carries the quarterly rate; it is hidden and the quarters stay."""
    b = Book()
    for i, (s_, e_) in enumerate(
        (
            ("2021-10-01", "2021-12-31"),
            ("2022-01-01", "2022-03-31"),
            ("2022-04-01", "2022-06-30"),
            ("2022-07-01", "2022-09-30"),
        )
    ):
        b.add(
            DPS_DECL,
            "0.375",
            s_,
            e_,
            b.filing(
                f"VQ{i}",
                f"2022-{2 + 3 * i:02d}-27" if i < 3 else "2022-11-15",
                "10-Q" if i < 3 else "10-K",
            ),
        )
    for i, fd in enumerate(("2022-11-16", "2023-11-15", "2024-11-14")):
        b.add(
            DPS_DECL,
            "0.375",
            "2021-10-01",
            "2022-09-30",
            b.filing(f"VK{i}", fd, "10-K"),
        )
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2021-10-01", "2022-09-30").status
        == sb.HIDE_DPS_INVALID
    )
    assert b.cell(
        res, "dividends_per_share_resolved", "2022-04-01", "2022-06-30"
    ).value == D("0.375")


@pytest.mark.parametrize(
    "basic, diluted, same_filing, hidden",
    [
        ("-0.04", "0.30", False, True),  # NWSA Jul-Sep 2015: two filings mixed
        ("0.50", "0.55", False, True),
        (
            "0.07",
            "0.09",
            True,
            False,
        ),  # NTNX 6M FY2024: printed pair, preferred add-back
        ("0.51", "0.62", True, False),  # ZWS FY2018
        ("-0.02", "17600000", True, True),  # ASTS: a share count on the EPS tag
        ("-0.02", "-17600000", True, True),  # a units scale apart, same sign
        ("0.08", "-0.08", False, False),  # warrant gain removed from diluted (CG, GSAT)
        ("0.50", "0.49", False, False),
        ("-0.30", "-0.30", True, False),
    ],
)
def test_basic_and_diluted_eps_pair_check(basic, diluted, same_filing, hidden):
    b = Book()
    f = b.filing("P-Q3", "2015-11-06")
    g = f if same_filing else b.filing("P-K", "2016-02-20", "10-K")
    b.add(EPS_B, basic, "2015-07-01", "2015-09-30", f)
    b.add(EPS_D, diluted, "2015-07-01", "2015-09-30", g)
    res = run(b)
    for concept in ("basic_eps_resolved", "diluted_eps_resolved"):
        cell = b.cell(res, concept, "2015-07-01", "2015-09-30")
        assert (cell.status == sb.HIDE_EPS_PAIR) is hidden


def _pkg_book():
    b = Book()
    f = b.filing("PK-1", "2016-05-01")
    b.add(EPS_D, "0.40", "2016-01-01", "2016-03-31", f)
    b.add(EPS_D, "0.52", "2016-04-01", "2016-06-30", b.filing("PK-2", "2016-08-01"))
    res = run(b)
    q1 = b.cell(res, "diluted_eps_resolved", "2016-01-01", "2016-03-31")
    q2 = b.cell(res, "diluted_eps_resolved", "2016-04-01", "2016-06-30")
    return res, q1, q2


def _pc(c, old):
    return sb.PackageCell(c.concept, c.period_id, old, c.value, c.status)


def test_release_package_matches_when_nothing_moved():
    res, q1, q2 = _pkg_book()
    current = {
        (q1.concept, q1.period_id): (11, D("4.00"), ()),
        (q2.concept, q2.period_id): (12, D("0.52"), ()),
    }
    pkg = {
        (q1.concept, q1.period_id): _pc(q1, D("4.00"))
    }  # q1 changes 4.00 -> 0.40; q2 is a no-op
    assert sb.package_mismatches(res, current, pkg, remove_derived_only=True) == []


def test_release_package_refuses_a_cell_production_rewrote():
    res, q1, q2 = _pkg_book()
    current = {
        (q1.concept, q1.period_id): (11, D("3.90"), ()),
        (q2.concept, q2.period_id): (12, D("0.52"), ()),
    }
    pkg = {(q1.concept, q1.period_id): _pc(q1, D("4.00"))}
    why = sb.package_mismatches(res, current, pkg, remove_derived_only=True)
    assert len(why) == 1 and "production now 3.90" in why[0]


def test_release_package_refuses_a_changed_recompute_and_writes_outside_it():
    res, q1, q2 = _pkg_book()
    current = {
        (q1.concept, q1.period_id): (11, D("4.00"), ())
    }  # q2 would be a new, unpackaged value
    stale = sb.PackageCell(q1.concept, q1.period_id, D("4.00"), D("0.41"), sb.SHOWN)
    why = sb.package_mismatches(
        res, current, {(q1.concept, q1.period_id): stale}, remove_derived_only=True
    )
    assert any("recomputed" in w for w in why)
    assert any(
        "outside the package" in w for w in why
    )  # q2's new 0.52 was not packaged
