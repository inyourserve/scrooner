"""0125 value path: a map row with dims reads the fsn.value printed under exactly those segments; dims = '' keeps the
no-dimension fact (CI: Postgres 16; applies the migration file itself until it lands contiguously)."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.mapper import company_tag_map as ctm
from scrooner_pipeline.mapper.resolve import resolve
from tests.unit.test_company_tag_map_db import _one, _seed

MIGRATION = Path(__file__).resolve().parents[2] / "db/migrations/0125_company_tag_map_dims.sql"
INS = (
    "insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id,"
    " parent_concept_id, era_from, decided_by, rule_id, dims) values (%s,'us-gaap',%s,'IS',%s,%s,%s,'2015-01-01','t',"
    "'tm.r@1',%s)"
)


def _ensure_dims_column(conn):
    if not ctm.has_dims_column(conn):
        conn.execute(MIGRATION.read_text())


def _fsn_world(conn, x, cik):
    """A company with one 10-K in the FSN store; returns (company, period ids, value(tag, segments, value))."""
    co, per, _, _ = x["company"](cik, True)
    fid = _one(conn, "insert into fsn.filing (accession, cik, form, fsn_set, company_id, accepted) values (%s,%s,'10-K','t',%s,'2019-03-01 10:00+00') returning id", f"{cik}-fsn", cik, co)
    tags: dict[str, int] = {}

    def value(tag, segments, v):
        if tag not in tags:
            tags[tag] = _one(conn, "insert into fsn.tag (tag, version) values (%s,'2018') returning id", tag)
            conn.execute("insert into fsn.line (filing_id, report, line, stmt, tag_id) values (%s,4,%s,'IS',%s)", (fid, len(tags), tags[tag]))
        dim = 0
        if segments:
            dim = _one(conn, "insert into fsn.dim (dimh, segments, segt) values (%s,%s,false) on conflict (dimh) do update set segments = excluded.segments returning id", f"0x{segments}", segments)
        return _one(conn, "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg, value) values (%s,%s,%s,'2018-12-31',4,'USD',%s,0,'',%s) returning id", fid, co, tags[tag], dim, Decimal(v))

    return co, per, value


@pytest.mark.integration
def test_dimensional_components_sum_only_their_own_segments(isolated_database_url, monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
    with psycopg.connect(isolated_database_url) as conn:
        _ensure_dims_column(conn)
        x = _seed(conn)
        co, per, value = _fsn_world(conn, x, "0000001401")
        vp = value("CostOfGoodsAndServicesSold", "ProductOrService=Product;", "30")
        vs = value("CostOfGoodsAndServicesSold", "ProductOrService=Service;", "12")
        value("CostOfGoodsAndServicesSold", "ProductOrService=Other;", "99")  # a slice the map does not name
        value("CostOfGoodsAndServicesSold", "", "141")  # the consolidated total is never a part
        for dims in ("ProductOrService=Product;", "ProductOrService=Service;"):
            conn.execute(INS, (co, "CostOfGoodsAndServicesSold", "component", None, x["opex"], dims))
        conn.commit()
        assert resolve(conn, {"0000001401"})["errored"] == 0
        row = conn.execute("select value, source_fact_ids, source_value_ids, family from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s", (co, x["opex"])).fetchone()
        assert row[0] == Decimal("42") and row[1] == [] and sorted(row[2]) == sorted([vp, vs])
        assert row[3] == "company_tag_map:fsn_xbrl"


@pytest.mark.integration
def test_a_class_of_stock_concept_row_reads_that_member_not_the_total_or_another_class(isolated_database_url, monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
    with psycopg.connect(isolated_database_url) as conn:
        _ensure_dims_column(conn)
        x = _seed(conn)
        co, per, value = _fsn_world(conn, x, "0000001402")
        va = value("WeightedAverageNumberOfDilutedSharesOutstanding", "ClassOfStock=CommonClassA;", "7")
        value("WeightedAverageNumberOfDilutedSharesOutstanding", "ClassOfStock=CommonClassB;", "8")
        value("WeightedAverageNumberOfDilutedSharesOutstanding", "", "15")
        conn.execute(INS, (co, "WeightedAverageNumberOfDilutedSharesOutstanding", "concept", x["rev"], None, "ClassOfStock=CommonClassA;"))
        conn.commit()
        assert resolve(conn, {"0000001402"})["errored"] == 0
        row = conn.execute("select value, source_value_ids from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s", (co, x["rev"])).fetchone()
        assert row == (Decimal("7"), [va])


@pytest.mark.integration
def test_no_dims_reads_the_no_dimension_fact_and_a_dims_key_never_reads_it(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        _ensure_dims_column(conn)
        x = _seed(conn)
        co, per, value = _fsn_world(conn, x, "0000001403")
        value("CostOfGoodsAndServicesSold", "ProductOrService=Product;", "30")
        v_total = value("CostOfGoodsAndServicesSold", "", "141")
        periods = ctm._load_periods(conn, co)
        plain = ("us-gaap", "CostOfGoodsAndServicesSold")
        sliced = ctm.dim_key("us-gaap", "CostOfGoodsAndServicesSold", "ProductOrService=Product;")
        missing = ctm.dim_key("us-gaap", "CostOfGoodsAndServicesSold", "ProductOrService=Service;")
        got = ctm._load_fsn_vintages(conn, co, {plain}, periods)
        assert [f.fact_id for f in got[plain][per["in"]]] == [v_total] and set(got) == {plain}
        got = ctm._load_fsn_vintages(conn, co, {plain, sliced, missing}, periods)
        assert got[plain][per["in"]][0].fact_id == v_total and got[plain][per["in"]][0].value == Decimal("141")
        assert got[sliced][per["in"]][0].value == Decimal("30")
        assert missing not in got  # no fact under those segments: nothing, never the total
        # two keys of different tags: a tag's slice is never read for the other tag's key, and the plain key stays plain
        value("OtherTag", "ProductOrService=Service;", "5")
        value("OtherTag", "", "9")
        other_sliced = ctm.dim_key("us-gaap", "OtherTag", "ProductOrService=Product;")
        got = ctm._load_fsn_vintages(conn, co, {plain, other_sliced}, periods)
        assert set(got) == {plain}  # OtherTag has no fact under Product; its Service slice and total are not read
