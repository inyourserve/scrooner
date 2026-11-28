"""Cohort certificate (certification/cohort_cert.py): draw size and bound, stratification, a wrong cell fails the
cohort, the seed reproduces the draw, and the request round-trips. Pure: an evidence bundle is the fact source."""

from __future__ import annotations

import csv
from decimal import Decimal as D
from fractions import Fraction
from math import comb
from pathlib import Path

import pytest

from scrooner_pipeline.certification import cohort_cert as cc
from scrooner_pipeline.certification import display_cert as dc
from scrooner_pipeline.certification import draw_check as dck

HDR = [
    "rank",
    "ticker",
    "company_id",
    "data_point",
    "fiscal_year",
    "period_end",
    "shown_value",
    "accession",
    "r_page",
    "tag",
    "parts",
    "display",
    "badge",
    "sector",
]
ST = {
    "revenue": "income_statement",
    "total_assets": "balance_sheet",
    "operating_cash_flow": "cash_flow",
}


def acc(cid: int, year: int) -> str:
    return f"00000{cid:05d}-{year % 100:02d}-000001"


def write_cov(path: Path, rows: list[list]) -> Path:
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(HDR)
        w.writerows(rows)
    return path


def rev_row(
    rank, ticker, cid, year, value, sector="general", dp="revenue", tag="Revenues"
):
    return [
        rank,
        ticker,
        cid,
        dp,
        str(year),
        f"{year}-12-31",
        value,
        acc(cid, year),
        "R4.htm",
        tag,
        "",
        dc.SHOWN,
        "as_printed",
        sector,
    ]


# ---------------------------------------------------------------- 1. draw size and the bound
def _cdf(k: int, n: int, p: float) -> Fraction:
    pf = Fraction(p)
    return sum(comb(n, i) * pf**i * (1 - pf) ** (n - i) for i in range(k + 1))


def test_draw_size_is_598_and_meets_the_half_percent_target():
    assert cc.COHORT_DRAW_SIZE == 598
    assert dc.clopper_pearson_upper(0, 598) <= 0.005 < dc.clopper_pearson_upper(0, 597)


@pytest.mark.parametrize(
    "k,n,expected",
    [
        (0, 598, 1 - 0.05 ** (1 / 598)),  # closed form at k = 0: 0.4997%
        (0, 199, 1 - 0.05 ** (1 / 199)),  # the per-company draw: 1.494%
        (1, 10, 0.39416),  # exact one-sided 95% upper bound, 1 in 10 (published tables)
        (1, 20, 0.21611),  # 1 in 20
        (2, 598, 0.010510),  # 2 in 598: P(X <= 2 | 598, p) = 0.05
    ],
)
def test_clopper_pearson_known_values(k, n, expected):
    up = dc.clopper_pearson_upper(k, n)
    assert up == pytest.approx(expected, abs=5e-5)
    assert float(_cdf(k, n, up)) == pytest.approx(0.05, abs=1e-6)


def test_cohort_bound_pooled_and_per_stratum(tmp_path):
    co = _cohort(tmp_path, [])
    assert co.upper() == pytest.approx(1 - 0.05 ** (1 / co.n), abs=1e-9)
    for s in co.per_stratum():
        assert s["upper_95"] == pytest.approx(1 - 0.05 ** (1 / s["checked"]), abs=1e-9)


# ---------------------------------------------------------------- 2. stratification covers every stratum
def _companies(tmp_path: Path) -> list[cc.Company]:
    rows = []
    # T0 and T1 share a stratum (general, rank band 1-50): the draw order must not depend on the input order
    spec = [
        (3, "general"),
        (4, "general"),
        (40, "bank"),
        (77, "insurer"),
        (150, "utility"),
        (900, "general"),
        (4200, "bank"),
    ]
    for i, (rank, sector) in enumerate(spec):
        cid = 100 + i
        for dp in ST:
            # skewed pools: general income statements are large, the rest are tiny
            years = 40 if (dp == "revenue" and sector == "general") else 1 + i % 2
            rows += [
                rev_row(rank, f"T{i}", cid, 1980 + y, "100", sector, dp)
                for y in range(years)
            ]
    return cc.load_cohort(write_cov(tmp_path / "cov.csv", rows), tmp_path)


def test_stratification_covers_every_stratum(tmp_path):
    companies = _companies(tmp_path)
    expected = {cc.stratum(c, co.rank, ST) for co in companies for c in co.cells}
    bands = {k.split("|")[2] for k in expected}
    assert bands == {
        "r0001-0050",
        "r0051-0100",
        "r0101-0500",
        "r0501-1000",
        "r2001-5000",
    }
    drawn, strata = cc.draw_cohort(companies, "seed", n=30, statements=ST)
    assert set(strata) == expected
    got = {d.stratum for d in drawn}
    assert got == expected  # every non-empty stratum has at least one drawn cell
    assert len(drawn) == 30 and all(0 < a <= m for m, a in strata.values())
    assert all(d.stratum == cc.stratum(d.cell, d.rank, ST) for d in drawn)
    # a pool smaller than n is drawn in full (a census)
    full, st_full = cc.draw_cohort(companies, "seed", n=10_000, statements=ST)
    assert (
        len(full)
        == sum(m for m, _ in st_full.values())
        == sum(len(co.cells) for co in companies)
    )


def test_rank_band_edges():
    assert [cc.rank_band(r) for r in (1, 50, 51, 100, 101, 5000, 5001)] == [
        "r0001-0050",
        "r0001-0050",
        "r0051-0100",
        "r0051-0100",
        "r0101-0500",
        "r2001-5000",
        "r5001+",
    ]


# ---------------------------------------------------------------- 4. a seed reproduces the draw
def test_seed_reproduces_the_draw(tmp_path):
    companies = _companies(tmp_path)
    a, _ = cc.draw_cohort(companies, "top100-x-abc", n=25, statements=ST)
    b, _ = cc.draw_cohort(
        list(reversed(companies)), "top100-x-abc", n=25, statements=ST
    )
    assert [d.key for d in a] == [
        d.key for d in b
    ]  # input order never changes the draw
    c, _ = cc.draw_cohort(companies, "top100-x-abd", n=25, statements=ST)
    assert [d.key for d in a] != [d.key for d in c]


# ---------------------------------------------------------------- 3. a single wrong cell fails the cohort
def _bundle(rows: list[list]) -> dict:
    """The filing facts that make every row's value the filed value (Revenues 100 per cited filing)."""
    facts, ffacts, lines, company = [], [], [], []
    for r in rows:
        a, pe = r[7], r[5]
        facts.append([a, "Revenues", pe, 4, "", "100", ["R4"]])
        ffacts.append([a, "Revenues", pe, 4, "", "100", -6, "USD"])
        lines.append([a, "Revenues", 4, "IS", "Revenues", 1, False])
        company.append([a, "Assets", pe, 0, "", "1", ["R2"]])
    return {
        "facts": facts,
        "filing_facts": ffacts,
        "filing_lines": lines,
        "company_facts": company,
        "year_ends": {r[7]: [r[5]] for r in rows},
    }


def _cohort(tmp_path: Path, wrong: list[tuple[str, int]]):
    rows = [
        rev_row(rank, t, cid, y, "99" if (t, y) in wrong else "100")
        for rank, t, cid in ((1, "AAA", 11), (60, "BBB", 12))
        for y in (2020, 2021, 2022)
    ]
    cov = write_cov(tmp_path / "cohort.csv", rows)
    src = dc.BundleFactSource(_bundle(rows))
    return cc.judge("t", cov, src, lambda cid: cid, statements=ST)


def test_clean_cohort_is_ready_for_the_approver(tmp_path):
    co = _cohort(tmp_path, [])
    assert co.n == 6 and co.errors == 0 and not co.census_fail
    assert {c.outcome for c in co.cells} == {cc.PASS}, [c.detail for c in co.cells]
    assert co.status == cc.STATUS_READY
    assert co.key == f"{co.cohort_id}|{co.coverage_sha256}|{cc.JUDGE_VERSION}"


def test_a_single_wrong_cell_fails_the_cohort(tmp_path):
    co = _cohort(tmp_path, [("BBB", 2021)])
    assert co.errors == 1 and co.status == cc.STATUS_FAIL
    bad = [c for c in co.cells if c.outcome == cc.FAIL]
    assert [(c.drawn.ticker, c.drawn.cell.fiscal_year) for c in bad] == [
        ("BBB", "2021")
    ]
    assert co.upper() > dc.clopper_pearson_upper(0, co.n)
    ex = cc.exception_rows(co, "draw.csv")
    fails = [r for r in ex if r.kind == "SAMPLE_FAIL"]
    assert (
        len(fails) == 1
        and fails[0].root_cause_family == "income_statement.revenue:claim_mismatch"
    )
    assert fails[0].idempotency_key.startswith(f"SAMPLE_FAIL|{co.key}|")
    assert fails[0].cells_affected == 1 and fails[0].judge_version == cc.JUDGE_VERSION


def test_a_wrong_read_fails_the_cohort_and_a_matching_read_settles(tmp_path):
    rows = [rev_row(1, "AAA", 11, 2022, "100")]
    cov = write_cov(tmp_path / "cohort.csv", rows)
    b = _bundle(rows)
    b["filing_facts"], b["filing_lines"] = (
        [[rows[0][7], "Assets", "2022-12-31", 0, "", "1", -6, "USD"]],
        [],
    )
    src = dc.BundleFactSource(b)
    co = cc.judge("t", cov, src, lambda cid: cid, statements=ST)
    assert [c.outcome for c in co.cells] == [
        cc.NEEDS_READ
    ] and co.status == cc.STATUS_READS
    assert [r.kind for r in cc.exception_rows(co, "d.csv")] == ["NEEDS_READ"]
    read = {
        "AAA": {
            ("revenue", "2022"): dck.Read(
                "revenue", "2022", "MISMATCH", "verifier", "R4 says 90"
            )
        }
    }
    co2 = cc.judge("t", cov, src, lambda cid: cid, reads=read, statements=ST)
    assert co2.errors == 1 and co2.status == cc.STATUS_FAIL
    ok = {
        "AAA": {
            ("revenue", "2022"): dck.Read(
                "revenue", "2022", "MATCH", "verifier", "R4 prints 100"
            )
        }
    }
    assert (
        cc.judge("t", cov, src, lambda cid: cid, reads=ok, statements=ST).status
        == cc.STATUS_READY
    )


def test_a_census_fail_fails_the_cohort_and_opens_an_item(tmp_path):
    rows = [rev_row(1, "AAA", 11, y, "100") for y in (2021, 2022)]
    rows.append(
        [
            1,
            "AAA",
            11,
            "basic_eps",
            "2022",
            "2022-12-31",
            "2770000",
            acc(11, 2022),
            "R4.htm",
            "EarningsPerShareBasic",
            "",
            dc.SHOWN,
            "as_printed",
            "general",
        ]
    )
    cov = write_cov(tmp_path / "cohort.csv", rows)
    co = cc.judge(
        "t",
        cov,
        dc.BundleFactSource(_bundle(rows)),
        lambda cid: cid,
        n=1,
        statements=ST,
    )
    assert co.census_fail and co.status == cc.STATUS_FAIL
    items = [r for r in cc.exception_rows(co, "d.csv") if r.kind == "CENSUS_FAIL"]
    assert items and all(r.root_cause_family.startswith("census:gate:") for r in items)


# ---------------------------------------------------------------- the request the approver reads
def test_request_round_trips_and_states_no_verdict(tmp_path):
    co = _cohort(tmp_path, [("AAA", 2020)])
    md = tmp_path / "req.md"
    md.write_text(
        cc.render_request(
            co, "2026-11-29", "abc123", {"drawn cells": "d.csv"}, "preparer"
        )
    )
    req = cc.read_request(md)
    assert (req.cohort_id, req.sha256, req.judge, req.seed, req.n) == (
        co.cohort_id,
        co.coverage_sha256,
        cc.JUDGE_VERSION,
        co.seed,
        co.n,
    )
    text = md.read_text()
    assert "machine status: `FAIL`" in text and "verdict:" not in text.lower().replace(
        "nothing below is a verdict", ""
    )
    md.write_text(text.replace(co.coverage_sha256, "0" * 64, 1))
    with pytest.raises(ValueError):
        cc.read_request(md)


def test_reads_file_needs_ticker_reader_and_evidence(tmp_path):
    p = tmp_path / "r.csv"
    p.write_text(
        "ticker,data_point,fiscal_year,verdict,reader,evidence\nAAA,revenue,2022,MATCH,v,R4 100\n"
    )
    assert cc.load_cohort_reads(p)["AAA"][("revenue", "2022")].verdict == "MATCH"
    p.write_text(
        "ticker,data_point,fiscal_year,verdict,reader,evidence\nAAA,revenue,2022,MATCH,,\n"
    )
    with pytest.raises(ValueError):
        cc.load_cohort_reads(p)


def test_certify_refuses_a_cell_not_in_the_coverage(tmp_path):
    rows = [rev_row(1, "AAA", 11, 2022, "100")]
    cov = write_cov(tmp_path / "c.csv", rows)
    alien = dc.Cell(
        "revenue", "1999", "1999-12-31", dc.SHOWN, D(1), "x", "R4", "Revenues"
    )
    with pytest.raises(ValueError):
        dc.certify("AAA", "11", cov, dc.BundleFactSource(_bundle(rows)), sample=[alien])
