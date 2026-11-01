"""The approved sector-template seed (SECTOR-TEMPLATES-2026-11-01.md section 8, Ritwik):
the committed seeder input is exactly what the generator builds, the seeder's dry run
accepts it on cohort v1.1, and the section-8 points hold. On REAL SQL (opt-in via
SCROONER_TEST_DATABASE_URL) the whole plan validates and loads under migration 0120."""

from __future__ import annotations

import collections
import csv
import importlib.util
from pathlib import Path

import pytest

from scrooner_pipeline.mapper import sector_templates as st

ROOT = Path(__file__).resolve().parents[3]
SEED = ROOT / "data-team/strategy/SECTOR-TEMPLATES-SEED-2026-11-01.md"
COHORT = ROOT / "data-team/strategy/data/cohort_v1_1_sic_2026-11-01.csv"
GENERATOR = ROOT / "data-team/strategy/tools/build_sector_template_seed.py"
CATALOG = ROOT / "data-team/strategy/data/cohort_cells.csv"

CIK = {"ARCC": "0001287750", "BXSL": "0001736035", "CBC": "0002065601", "JPM": "0000019617",
       "AXP": "0000004962", "MSTR": "0001050446", "NLY": "0001043219", "WY": "0000106535"}  # fmt: skip


def _generator():
    spec = importlib.util.spec_from_file_location(
        "build_sector_template_seed", GENERATOR
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def plan():
    cohort = st.load_cohort(COHORT)
    by_cik = {c.cik: c.company_id for c in cohort}
    rows = st.build_plan(st.parse_templates(SEED.read_text()), cohort)
    return rows, by_cik


def _cell(rows, company_id, dp):
    (hit,) = [r for r in rows if r.company_id == company_id and r.data_point == dp]
    return hit


@pytest.mark.unit
def test_committed_seed_is_what_the_generator_builds():
    seed, cohort = _generator().build()
    assert SEED.read_text() == seed, (
        "rerun data-team/strategy/tools/build_sector_template_seed.py"
    )
    assert COHORT.read_text() == cohort


@pytest.mark.unit
def test_cohort_is_v1_1_with_1000_companies_and_sic():
    rows = list(csv.DictReader(COHORT.open()))
    v11 = list(
        csv.DictReader(
            (
                ROOT / "data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv"
            ).open()
        )
    )
    assert len(rows) == 1000
    assert [r["company_id"] for r in rows] == [r["company_id"] for r in v11]
    no_sic = {r["ticker"] for r in rows if not r["sic"]}
    assert no_sic == {"ARCC", "BXSL", "CBC"}  # all three by company assignment


@pytest.mark.unit
def test_dry_run_plan_and_section_8_sum_check(plan):
    rows, _ = plan
    s = st.summarize(rows)
    assert s["companies"] == 1000
    catalog = {r["data_point_name"] for r in csv.DictReader(CATALOG.open())}
    assert len(catalog) == 163
    per_company = collections.Counter(r.company_id for r in rows)
    assert set(per_company.values()) == {163}  # every company carries the full catalog
    assert {r.data_point for r in rows} == catalog
    # §8.6: §1's sum check with ARCC, BXSL and CBC moved (712 + 60 pharma - 3 = 769)
    assert s["companies_per_template"] == {
        "general": 769, "bank": 42, "lender": 7, "broker_am": 37, "insurer": 39,
        "reit_equity": 51, "reit_mortgage": 2, "utility": 51, "bdc": 2,
    }  # fmt: skip


@pytest.mark.unit
def test_section_8_assignments(plan):
    rows, by_cik = plan
    tmpl = {r.company_id: r.template for r in rows}
    assert tmpl[by_cik[CIK["CBC"]]] == "bank"  # §8.5
    assert tmpl[by_cik[CIK["ARCC"]]] == tmpl[by_cik[CIK["BXSL"]]] == "bdc"  # §8.4
    assert tmpl[by_cik[CIK["AXP"]]] == "lender"  # 6199 minus crypto
    assert tmpl[by_cik[CIK["MSTR"]]] == "general"  # crypto miner
    assert tmpl[by_cik[CIK["NLY"]]] == "reit_mortgage"


@pytest.mark.unit
def test_category_b_stays_in_and_bdc_rules(plan):
    rows, by_cik = plan
    current = (
        "current_assets",
        "current_liabilities",
        "current_ratio",
        "working_capital",
    )
    for r in rows:
        if r.data_point in current and r.template != "bdc":
            assert r.in_template, (r.template, r.data_point)  # §8.3
    arcc = by_cik[CIK["ARCC"]]
    assert not _cell(
        rows, arcc, "current_ratio"
    ).in_template  # §8.4 current ratio family
    assert not _cell(rows, arcc, "ebitda").in_template
    assert not _cell(rows, arcc, "fcf").in_template
    assert _cell(rows, arcc, "debt_to_equity").in_template
    assert _cell(rows, arcc, "bdc_total_investment_income").in_template
    rev = _cell(rows, arcc, "revenue")
    assert (
        rev.in_template and "total investment income" in rev.reason
    )  # REP, a defect until served
    # founder ruling 2026-11-01 (relayed): revenue = TII, earnings line = NII, as printed
    assert "RULED" in rev.reason and "pending" not in rev.reason
    assert "net investment income" in _cell(rows, arcc, "net_income").reason
    assert not any("pending" in (r.reason or "") for r in rows if r.template == "bdc")


@pytest.mark.unit
def test_category_c_out_for_banks_and_defaults_full_for_general(plan):
    rows, by_cik = plan
    jpm = by_cik[CIK["JPM"]]
    for dp in ("ebitda", "fcf", "capex", "roic", "interest_coverage_ratio", "debt_to_equity",
               "operating_margin", "gross_margin", "inventory"):  # fmt: skip
        assert not _cell(rows, jpm, dp).in_template, dp
    assert "REP" in _cell(rows, jpm, "revenue").reason
    # dependent metrics leave with their required input (§6 "+ dependent metrics")
    dep = _cell(rows, jpm, "dividends_pct_fcf")
    assert not dep.in_template and "requires fcf" in dep.reason
    assert _cell(rows, jpm, "quick_ratio").in_template  # inventory is optional for it
    general_out = {
        r.data_point for r in rows if r.template == "general" and not r.in_template
    }
    assert general_out == {"bdc_total_investment_income"}


@pytest.mark.unit
def test_section_3_company_overrides(plan):
    rows, by_cik = plan
    overrides = [r for r in rows if r.source == "company_override"]
    assert (
        len(overrides) == 17
    )  # the 19 line instances, one row per company x data point
    assert all(r.in_template and r.reason for r in overrides)
    assert _cell(rows, by_cik[CIK["JPM"]], "accounts_receivable").in_template
    wy = by_cik[CIK["WY"]]
    assert _cell(rows, wy, "gross_profit").source == "company_override"
    assert not _cell(
        rows, wy, "gross_margin"
    ).in_template  # only the named line is overridden


@pytest.mark.unit
def test_every_exclusion_carries_a_reason(plan):
    rows, _ = plan
    assert all(r.reason for r in rows if not r.in_template)


# --------------------------------------------------------------------------- real SQL


@pytest.mark.integration
def test_whole_seed_validates_and_loads_under_0120(isolated_database_url, plan):
    psycopg = pytest.importorskip("psycopg")
    rows, _ = plan
    with psycopg.connect(isolated_database_url) as conn:
        if not conn.execute(
            "select to_regclass('analytics.company_data_point_template') is not null"
        ).fetchone()[0]:
            pytest.skip("needs the migrated schema with migration 0120")
        cohort = list(csv.DictReader(COHORT.open()))
        with conn.cursor() as cur:
            cur.executemany(
                "insert into core.company (id, cik, company_name) overriding system value"
                " values (%s, %s, %s) on conflict do nothing",
                [(int(r["company_id"]), r["cik"], r["ticker"]) for r in cohort],
            )
            cur.executemany(
                "insert into analytics.data_point_registry (data_point_name, data_point_type)"
                " values (%s, 'concept') on conflict do nothing",
                [(dp,) for dp in sorted({r.data_point for r in rows})],
            )
        st.validate_against_db(conn, rows)
        out = st.write_plan(conn, rows)
        assert (out["companies"], out["inserted"]) == (1000, 163_000)
        n_out = conn.execute(
            "select count(*) from analytics.company_data_point_template where not in_template"
        ).fetchone()[0]
        assert n_out == sum(1 for r in rows if not r.in_template)
