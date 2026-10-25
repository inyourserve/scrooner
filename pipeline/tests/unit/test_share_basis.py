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
    b.add(DPS_DECL, "0.085", "2014-07-28", "2014-10-26", q3)
    b.add(DPS_DECL, "0.34", "2014-01-27", "2015-01-25", k)
    b.add(DPS_DECL, "0.085", "2014-10-27", "2015-01-25", k, derived=True)
    b.add(DPS_PAID, "0.34", "2014-10-27", "2015-01-25", k)
    res = run(b)
    assert (
        b.cell(res, "dividends_per_share_resolved", "2014-10-27", "2015-01-25").status
        == sb.HIDE_LABEL_ERROR
    )


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
        b.add("WeightedAverageNumberOfSharesOutstandingBasic", w, s, e, pre)
        b.add(
            "WeightedAverageNumberOfSharesOutstandingBasic", str(D(w) * 10), s, e, post
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
    assert dps.status == sb.HIDE_RESTATED


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
    assert "label-shifted" in cell.note


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


def test_hide_series_policy_hides_the_whole_mixed_series(monkeypatch):
    monkeypatch.setattr(sb, "DPS_MIXED_POLICY", "hide_series")
    b = Book()
    q = b.filing("L-1", "2018-11-01")
    k = b.filing("L-2", "2020-02-19", "10-K")
    b.add(DPS_DECL, "0.5625", "2018-01-01", "2018-03-31", q)
    b.add(DPS_PAID, "0.5625", "2018-07-01", "2018-09-30", k)
    res = run(b)
    q1 = b.cell(res, "dividends_per_share_resolved", "2018-01-01", "2018-03-31")
    assert q1.status == sb.HIDE_DPS_BASIS


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
            ("2020-01-01", "2020-03-31", "1.505"),  # OGE-like annual on a quarter
            ("2020-04-01", "2020-06-30", "0.3875"),
            ("2020-07-01", "2020-09-30", "0.3875"),
            ("2020-10-01", "2020-12-31", "0.3875"),
        )
    ):
        b.add(DPS_DECL, v, s, e, b.filing(f"W-{i}", f"2025-0{1 + i % 9}-15"))
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
    # one later copy against the original: unresolved, held (never the later 0.26)
    assert cell.status == sb.HIDE_RESTATED


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
    b.add(EPS_D, "0.61", "2007-01-01", "2007-12-31", a)
    res = run(b)
    assert [e.status for e in res.events] == ["review"]
    assert (
        b.cell(res, "diluted_eps_resolved", "2007-01-01", "2007-12-31").status
        == sb.HIDE_BASIS_REVIEW
    )

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
        == sb.HIDE_BASIS_REVIEW
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
        ("2019-08-01", "2020-07-31", "3.20", "230000000"),
        ("2018-08-01", "2019-07-31", "2.80", "232000000"),
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
