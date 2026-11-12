"""0125 company_tag_map.dims on a migrated scratch database (applies the file itself until it lands contiguously)."""

from __future__ import annotations

from pathlib import Path

import psycopg
import pytest

MIGRATION = Path(__file__).resolve().parents[2] / "db/migrations/0125_company_tag_map_dims.sql"
INSERT = (
    "insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id,"
    " parent_concept_id, era_from, decided_by, rule_id, dims) values (%s, 'us-gaap', %s, 'IS', %s, %s, %s,"
    " '2015-01-01', 't', 'a.b@1', %s)"
)


def _setup(conn):
    if not conn.execute(
        "select 1 from information_schema.columns where table_schema = 'analytics' and table_name = 'company_tag_map' and column_name = 'dims'"
    ).fetchone():
        conn.execute(MIGRATION.read_text())
    co = conn.execute("insert into core.company (cik, company_name) values ('0000009991', 'D') returning id").fetchone()[0]
    cc = conn.execute(
        "insert into analytics.canonical_concept (name, statement, combination_mode) values ('tm_dims', 'income_statement', 'first_match') returning id"
    ).fetchone()[0]
    return co, cc


@pytest.mark.integration
def test_two_members_of_one_tag_are_parts_of_one_sum(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        co, cc = _setup(conn)
        for dims in ("ProductOrService=Product;", "ProductOrService=Service;"):
            conn.execute(INSERT, (co, "CostOfGoodsAndServicesSold", "component", None, cc, dims))
        assert conn.execute("select count(*) from analytics.company_tag_map where company_id = %s", (co,)).fetchone()[0] == 2


@pytest.mark.integration
def test_a_single_class_of_stock_member_may_be_the_data_point(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        co, cc = _setup(conn)
        conn.execute(INSERT, (co, "WeightedAverageNumberOfDilutedSharesOutstanding", "concept", cc, None, "ClassOfStock=CommonClassA;"))


@pytest.mark.integration
@pytest.mark.parametrize("dims", ["ProductOrService=Product;", "ClassOfStock=CommonClassA;ProductOrService=Product;"])
def test_any_other_slice_is_never_a_data_point(isolated_database_url, dims):
    with psycopg.connect(isolated_database_url) as conn:
        co, cc = _setup(conn)
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute(INSERT, (co, "CostOfGoodsAndServicesSold", "concept", cc, None, dims))
