"""Catalog-driven template seeding (founder approval 2026-11-13): the concept list comes
from concepts_catalog.csv, the group from SIC, the OUT sets from GROUP_OUT; ranks 1..N of
the cohort file, excluded rows skipped, idempotent batched write."""

from __future__ import annotations

from pathlib import Path

import pytest
from scrooner_pipeline.mapper import sector_templates as st

CATALOG = "name,statement,combination_mode\n" + "".join(
    f"{n},income_statement,first_match\n"
    for n in (
        "revenue",
        "revenue_sanity_resolved",
        "gross_profit",
        "gross_profit_resolved",
        "inventory",
        "capex",
        "comprehensive_income",
        "net_income",
        "bdc_total_investment_income",
        "net_interest_income",
    )
)
COHORT = (
    "shard,rank,company_id,cik,ticker,name,sic,mcap_bn,cells,filled,unexplained_blank,excluded\n"
    "S1,1,11,0000000011,GEN,Gen Co,3674,1,1,1,0,\n"
    "S1,2,12,0000000012,BNK,Bank Co,6021,1,1,1,0,\n"
    "S1,3,13,0000000013,BAD,Bad Co,2834,1,1,1,0,wrong mcap: ADS ratio\n"
    "S1,4,14,0000000014,KEP,Keep Co,7370,1,1,1,0,keep: mcap understated\n"
    "S1,5,15,0000000015,FAR,Far Co,3674,1,1,1,0,\n"
    "S101,,16,0000000016,BKF,Backfill,6022,,,,,added by re-rank\n"
)


def _files(tmp_path: Path) -> tuple[Path, Path]:
    c = tmp_path / "catalog.csv"
    c.write_text(CATALOG)
    s = tmp_path / "shards.csv"
    s.write_text(COHORT)
    return c, s


def test_catalog_plan_groups_outs_and_excluded_rows(tmp_path: Path):
    c, s = _files(tmp_path)
    concepts = st.load_catalog(c)
    companies, excluded = st.load_ranked_cohort(s, 4)
    assert [e[1] for e in excluded] == ["BAD"]
    assert [x.ticker for x in companies] == [
        "GEN",
        "BNK",
        "KEP",
    ]  # keep-note kept, rank 5 cut
    rows = st.build_catalog_plan(concepts, companies)
    assert len(rows) == 3 * len(concepts)
    by = {(r.company_id, r.data_point): r for r in rows}
    assert by[(11, "gross_profit")].in_template
    assert not by[(12, "gross_profit")].in_template  # bank
    assert not by[(12, "gross_profit_resolved")].in_template  # _resolved follows base
    assert not by[(12, "capex")].in_template
    assert by[(12, "comprehensive_income")].in_template  # founder ruling
    assert by[(11, "revenue_sanity_resolved")].in_template
    assert not by[(11, "bdc_total_investment_income")].in_template  # BDC-only
    assert not by[(11, "net_interest_income")].in_template  # bank-only
    assert by[(12, "net_interest_income")].in_template
    assert all(r.reason for r in rows if not r.in_template)
    assert {r.template for r in rows if r.company_id == 12} == {"bank"}
    summ = st.rows_per_company_group(rows)
    assert summ["bank"] == {"companies": 1, "in_rows": 5, "out_rows": 5, "rows": 10}


def test_unknown_group_and_duplicate_catalog_are_errors(tmp_path: Path):
    bdc = st.RankedCompany(1, 1, "0001287750", "ARCC", 6726)
    with pytest.raises(st.TemplateError):
        st.build_catalog_plan(["revenue"], [bdc])
    dup = tmp_path / "d.csv"
    dup.write_text("name\nrevenue\nrevenue\n")
    with pytest.raises(st.TemplateError):
        st.load_catalog(dup)


def test_real_catalog_and_cohort_give_enough_rows_for_top_110():
    root = Path(__file__).resolve().parents[3]
    concepts = st.load_catalog(root / st.CATALOG_PATH)
    companies, excluded = st.load_ranked_cohort(
        root / "doc/data-moat/team/top1000/shards.csv", 110
    )
    rows = st.build_catalog_plan(concepts, companies)
    per = {}
    for r in rows:
        per[r.company_id] = per.get(r.company_id, 0) + (1 if r.in_template else 0)
    assert min(per.values()) >= 40
    assert "comprehensive_income" in {r.data_point for r in rows if r.in_template}
    assert len(excluded) == 4


@pytest.fixture
def db(isolated_database_url):
    psycopg = pytest.importorskip("psycopg")
    conn = psycopg.connect(isolated_database_url)
    present = conn.execute(
        "select to_regclass('analytics.company_data_point_template') is not null"
    ).fetchone()[0]
    if not present:
        conn.close()
        pytest.skip("needs the migrated schema with migration 0120")
    yield conn
    conn.rollback()
    conn.close()


@pytest.mark.integration
def test_catalog_write_is_idempotent_batched_and_scoped(
    db, tmp_path: Path, monkeypatch
):
    c, _s = _files(tmp_path)
    concepts = st.load_catalog(c)
    for name in concepts:
        db.execute(
            "insert into analytics.canonical_concept (name, statement, combination_mode)"
            " values (%s, 'income_statement', 'first_match') on conflict (name) do nothing",
            (name,),
        )
    ids = {}
    for t in (11, 12, 14, 99):
        ids[t] = db.execute(
            "insert into core.company (cik, company_name) values (%s, %s) returning id",
            (f"{t:010d}", f"CO {t}"),
        ).fetchone()[0]
    db.commit()
    companies = [
        st.RankedCompany(1, ids[11], "0000000011", "GEN", 3674),
        st.RankedCompany(2, ids[12], "0000000012", "BNK", 6021),
    ]
    rows = st.build_catalog_plan(concepts, companies)
    st.validate_against_db(db, rows)
    # an untouched company's row must survive the write
    db.execute(
        "insert into analytics.company_data_point_template (company_id, data_point, in_template,"
        " effective_from, template, source, template_version)"
        " values (%s, 'revenue', true, '2026-11-13', 'general', 'sector_default', 'x')",
        (ids[99],),
    )
    db.commit()
    before = tmp_path / "before.csv"
    assert st.write_before_image(db, [ids[11], ids[12]], before) == 0
    assert before.read_text().startswith("company_id,data_point")
    monkeypatch.setattr(st, "WRITE_CHUNK", 7)  # force several batches
    first = st.write_plan(db, rows)
    again = st.write_plan(db, rows)
    n = 2 * len(concepts)
    assert (first["inserted"], first["deleted"]) == (n, 0)
    assert (again["inserted"], again["deleted"]) == (n, n)
    count = "select count(*) from analytics.company_data_point_template where company_id = any(%s)"
    assert db.execute(count, ([ids[11], ids[12]],)).fetchone()[0] == n
    assert db.execute(count, ([ids[99]],)).fetchone()[0] == 1
    out = db.execute(
        "select in_template from analytics.company_data_point_template"
        " where company_id = %s and data_point = 'gross_profit'",
        (ids[12],),
    ).fetchone()[0]
    assert out is False
