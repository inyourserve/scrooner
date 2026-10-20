"""In-memory fixtures for the certification suite. A company is a
`CompanyData` built from `Cell` / `Source` rows; nothing here touches a database.

`clean_company()` is a small, internally consistent company (three fiscal years,
quarters that tile each year, a balanced balance sheet, a cash roll that closes,
10-K / 10-Q sources) that must produce ZERO findings from every invariant.
Each real failure case starts from it and breaks exactly one thing.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.certification.model import (
    Cell, CompanyData, ComponentFact, Metric, Source,
)

D = Decimal
_period_ids: dict[tuple, int] = {}
_next_source = [1_000]


def pid(start: date | None, end: date) -> int:
    return _period_ids.setdefault((start, end), len(_period_ids) + 1)


def src(tag: str, value, *, form="10-K", unit="usd", auth=True, derived=False, end=None, sid=None,
        accession="0000000000-26-000001") -> Source:
    if sid is None:
        _next_source[0] += 1
        sid = _next_source[0]
    return Source(id=sid, tag=tag, value=D(value), authoritative=auth, derived=derived, form=form,
                  unit=unit, accession=accession, filing_date=date(2026, 2, 1), end=end)


def add(data: CompanyData, concept: str, value, end: date, start: date | None = None, fp: str | None = None,
        *, sources: list[Source] | None = None, tag: str | None = None, form="10-K", unit="usd",
        derived=False, auth=True) -> Cell:
    """Add one canonical cell plus (unless `sources` is given) one clean source fact."""
    value = D(value)
    ptype = "instant" if start is None else "duration"
    if sources is None:
        sources = [src(tag or concept, value, form=form, unit=unit, derived=derived, auth=auth, end=end)]
    cell = Cell(
        concept=concept, value=value, period_id=pid(start, end), start=start, end=end, period_type=ptype,
        fiscal_year=end.year, fiscal_period=fp, source_ids=tuple(s.id for s in sources),
    )
    data.cells.append(cell)
    for s in sources:
        data.sources[s.id] = s
    return cell


QUARTERS = [
    (date(2024, 1, 1), date(2024, 3, 31), "Q1"),
    (date(2024, 4, 1), date(2024, 6, 30), "Q2"),
    (date(2024, 7, 1), date(2024, 9, 30), "Q3"),
    (date(2024, 10, 1), date(2024, 12, 31), "Q4"),
]


def clean_company(company_id: int = 1) -> CompanyData:
    d = CompanyData(company_id=company_id, cik="0000000001", ticker="CLN", sic="3571",
                    as_of=date(2025, 1, 15))
    d.latest_filed = date(2024, 12, 31)
    d.concept_modes = {"total_debt": "sum", "total_debt_resolved": "first_match"}
    years = [(2022, D(1000), D(100)), (2023, D(1100), D(120)), (2024, D(1210), D(135))]
    prev_cash = D(500_000_000)
    add(d, "cash_and_equivalents", prev_cash, date(2021, 12, 31), None, "FY", tag="Cash")
    for year, rev_m, ni_m in years:
        fy_start, fy_end = date(year, 1, 1), date(year, 12, 31)
        rev, cost, ni = rev_m * 1_000_000, rev_m * 600_000, ni_m * 1_000_000
        tax = D(30_000_000)
        add(d, "revenue", rev, fy_end, fy_start, "FY", tag="Revenues")
        add(d, "cost_of_revenue", cost, fy_end, fy_start, "FY", tag="CostOfRevenue")
        add(d, "gross_profit", rev - cost, fy_end, fy_start, "FY", tag="GrossProfit")
        add(d, "income_before_tax", ni + tax, fy_end, fy_start, "FY", tag="IncomeLossBeforeIncomeTaxes")
        add(d, "income_tax_expense", tax, fy_end, fy_start, "FY", tag="IncomeTaxExpenseBenefit")
        add(d, "net_income", ni, fy_end, fy_start, "FY", tag="NetIncomeLoss")
        add(d, "diluted_eps", ni / D(100_000_000), fy_end, fy_start, "FY", tag="EarningsPerShareDiluted",
            unit="usd/shares")
        cfo, cfi, cff = ni + D(20_000_000), D(-60_000_000), D(-30_000_000)
        add(d, "cfo", cfo, fy_end, fy_start, "FY", tag="NetCashProvidedByOperatingActivities")
        add(d, "cash_flow_investing", cfi, fy_end, fy_start, "FY", tag="NetCashProvidedByInvestingActivities")
        add(d, "cash_flow_financing", cff, fy_end, fy_start, "FY", tag="NetCashProvidedByFinancingActivities")
        cash = prev_cash + cfo + cfi + cff
        add(d, "cash_and_equivalents", cash, fy_end, None, "FY", tag="Cash")
        prev_cash = cash
        assets, liab = D(2_000_000_000) + rev_m * 1_000_000, D(900_000_000) + rev_m * 400_000
        add(d, "total_assets", assets, fy_end, None, "FY", tag="Assets")
        add(d, "total_liabilities", liab, fy_end, None, "FY", tag="Liabilities")
        add(d, "stockholders_equity", assets - liab, fy_end, None, "FY", tag="StockholdersEquity")
        add(d, "shares_outstanding", D(100_000_000), fy_end, None, "FY", tag="CommonStockSharesOutstanding",
            unit="shares")
    # four quarters per year that tile it, summing exactly to the year (2024 only, enough for I5)
    for fy in (2024,):
        rev_year = D(1210) * 1_000_000
        shares = [D("0.22"), D("0.25"), D("0.26"), D("0.27")]
        for (qs, qe, fp), w in zip(QUARTERS, shares):
            add(d, "revenue", rev_year * w, qe, qs, fp, tag="Revenues", form="10-Q")
            add(d, "net_income", D(135_000_000) * w, qe, qs, fp, tag="NetIncomeLoss", form="10-Q")
    return d


def make_metric(name, value, label="TTM", end=date(2025, 1, 14), requires_price=False, source_ids=()) -> Metric:
    return Metric(name=name, label=label, period_end=end, value=D(value), requires_price=requires_price,
                  source_ids=tuple(source_ids))


def fact(tag, value, period_start, period_end, fid=None) -> ComponentFact:
    _next_source[0] += 1
    return ComponentFact(id=fid or _next_source[0], tag=tag, value=D(value), period_id=pid(period_start, period_end),
                         end=period_end)
