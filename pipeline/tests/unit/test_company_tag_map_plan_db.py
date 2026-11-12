"""tagmap-plan / apply, the owner guard of 0123, protection and the downstream-stage skip (CI: Postgres 16)."""

from __future__ import annotations

import gzip
from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.mapper import company_tag_map_plan as plan
from tests.unit.test_company_tag_map_db import _one, _seed


def _setup(conn):
    x = _seed(conn)
    co, per, fil, fact = x["company"]("0000001001", True)
    fact("Revenues", "in", "new", "110")
    conn.execute("insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, era_from, decided_by, rule_id) values (%s,'us-gaap','Revenues','IS','concept',%s,'2015-01-01','t','tm.r@1')", (co, x["rev"]))
    # a pre-existing wrong value and a slot-protected cell of the OLD path: the tag-map write replaces them
    conn.execute("insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s,%s,%s,%s,'{}')", (co, x["rev"], per["in"], Decimal("1")))
    conn.commit()
    return x, co, per


@pytest.mark.integration
def test_plan_rolls_back_and_apply_writes_protects_owns_and_blocks_other_writers(isolated_database_url, tmp_path):
    with psycopg.connect(isolated_database_url) as conn:
        x, co, per = _setup(conn)
        tpl = {co: {"tm_rev"}}
        rep = plan.run(conn, [co], tpl, apply=False)
        assert rep[co]["valued"] == 1 and rep[co]["neither"] == 1  # the 2020 period has no value and no reason
        assert _one(conn, "select value from analytics.canonical_fact where company_id = %s", co) == Decimal("1")  # rolled back
        assert _one(conn, "select count(*) from analytics.slot_protected_cell where company_id = %s", co) == 0
        counts = plan.write_before_image(conn, [co], tmp_path / "before")
        assert counts["canonical_fact"] == 1
        assert gzip.open(tmp_path / "before/canonical_fact.csv.gz", "rt").readline().startswith("id,")
        rep = plan.run(conn, [co], tpl, apply=True)
        assert rep[co]["valued"] == 1 and rep[co]["protected_keys"] == 1
        assert _one(conn, "select value from analytics.canonical_fact where company_id = %s", co) == Decimal("110")
        assert _one(conn, "select value from analytics.slot_protected_cell where company_id = %s", co) == Decimal("110")
        assert _one(conn, "select owner from analytics.company_value_owner where company_id = %s", co) == "company_tag_map"
        # any other writer is skipped for an owned company (0123 keeps the guard) and logged
        conn.execute("delete from analytics.canonical_fact where company_id = %s", (co,))
        conn.commit()
        assert _one(conn, "select value from analytics.canonical_fact where company_id = %s", co) == Decimal("110")
        assert _one(conn, "select count(*) from analytics.owned_write_skipped where company_id = %s", co) >= 1
        # the tag-map writer itself is let through
        conn.execute("set local scrooner.writer = 'company_tag_map'")
        conn.execute("set local scrooner.slot_writer = 'on'")  # the cell is also protected (0113): the write path sets both
        conn.execute("update analytics.canonical_fact set value = 111 where company_id = %s", (co,))
        conn.commit()
        assert _one(conn, "select value from analytics.canonical_fact where company_id = %s", co) == Decimal("111")


@pytest.mark.integration
def test_downstream_stage_skips_tag_map_companies_only_when_the_flag_is_on(isolated_database_url, monkeypatch):
    from scrooner_pipeline.mapper.concept_fallback import resolve_employee_count_fallback

    with psycopg.connect(isolated_database_url) as conn:
        x, co, per = _setup(conn)
        co2, *_ = x["company"]("0000001002", False)  # no tag-map rows
        for n in ("employee_count", "employee_count_resolved"):
            conn.execute("insert into analytics.canonical_concept (name, statement, combination_mode) values (%s,'balance_sheet','first_match') on conflict (name) do nothing", (n,))
        conn.commit()
        monkeypatch.delenv("SCROONER_RULES_ENABLED", raising=False)
        off = resolve_employee_count_fallback(conn, {"0000001001", "0000001002"})
        monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
        on = resolve_employee_count_fallback(conn, {"0000001001", "0000001002"})
        assert off["considered"] == 2 and on["considered"] == 1  # the tag-map company is skipped only with the flag ON
