"""tagmap-plan / apply, the owner guard of 0123, protection and the downstream-stage skip (CI: Postgres 16)."""

from __future__ import annotations

import gzip
from datetime import date
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
        tpl = {co: [("tm_rev", date(2018, 12, 31), "served"), ("tm_rev", date(2020, 12, 31), "served"), ("tm_rev", date(2019, 12, 31), "held C8")]}
        rep = plan.run(conn, [co], tpl, apply=False)
        assert "error" not in rep[co], rep[co]
        assert rep[co]["valued"] == 1 and rep[co]["neither"] == 1 and rep[co]["reasoned_blank"] == 1 and rep[co]["library_status_only"] == 0  # 2020: no value, no reason
        assert _one(conn, "select value from analytics.canonical_fact where company_id = %s", co) == Decimal("1")  # rolled back
        assert _one(conn, "select count(*) from analytics.slot_protected_cell where company_id = %s", co) == 0
        counts = plan.write_before_image(conn, [co], tmp_path / "before")
        assert counts["canonical_fact"] == 1
        assert gzip.open(tmp_path / "before/canonical_fact.csv.gz", "rt").readline().startswith("id,")
        rep = plan.run(conn, [co], tpl, apply=True)
        assert rep[co]["valued"] == 1 and rep[co]["protected_keys"] == 1
        # the library status of the 2019 cell (held C8) is WRITTEN as a reason row: defect, guard_hidden, library rule
        assert conn.execute("select state, defect_class, owner, reason_code, rule_id from analytics.cell_blank_reason where company_id = %s and reason_code = 'held_c8'", (co,)).fetchall() == [("defect", "guard_hidden", "verifier", "held_c8", "tagmap.library_status@1")]
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


@pytest.mark.integration
def test_non_authoritative_only_facts_end_to_end_blank_not_value(isolated_database_url, monkeypatch):
    from scrooner_pipeline.mapper.resolve import resolve

    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
    with psycopg.connect(isolated_database_url) as conn:
        x = _seed(conn)
        co, per, fil, fact = x["company"]("0000001201", True)
        fact("Revenues", "in", "new", "110", auth=False)  # copies disagree across filings: none authoritative
        fact("Revenues", "in", "old", "100", auth=False)
        conn.execute("insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, era_from, decided_by, rule_id) values (%s,'us-gaap','Revenues','IS','concept',%s,'2015-01-01','t','tm.r@1')", (co, x["rev"]))
        conn.commit()
        assert resolve(conn, {"0000001201"})["errored"] == 0
        assert _one(conn, "select count(*) from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s", co, x["rev"]) == 0
        assert _one(conn, "select reason_code from analytics.cell_blank_reason where company_id = %s and data_point_name = 'tm_rev'", co) == "no_authoritative_fact"


@pytest.mark.integration
def test_custom_tag_is_read_from_the_fsn_store_with_value_id_lineage(isolated_database_url, monkeypatch):
    from scrooner_pipeline.mapper.resolve import resolve

    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
    with psycopg.connect(isolated_database_url) as conn:
        x = _seed(conn)
        co, per, fil, fact = x["company"]("0000001301", True)
        fact("Revenues", "in", "new", "100")  # a standard tag: SEC companyfacts
        conn.execute("insert into core.period (company_id, start_date, end_date, period_type) values (%s,'2018-01-01','2018-12-31','duration') on conflict do nothing", (co,))
        fid = _one(conn, "insert into fsn.filing (accession, cik, form, fsn_set, company_id, accepted) values ('0000001301-new','0000001301','10-K','t',%s,'2019-03-01 10:00+00') returning id", co)
        tid = _one(conn, "insert into fsn.tag (tag, version, custom) values ('OpexExclAmort','0000001301-new',true) returning id")
        conn.execute("insert into fsn.line (filing_id, report, line, stmt, tag_id) values (%s,4,9,'IS',%s)", (fid, tid))
        vid = _one(conn, "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg, value) values (%s,%s,%s,'2018-12-31',4,'USD',0,0,'',40) returning id", fid, co, tid)
        opex = x["opex"]
        ins = "insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, era_from, decided_by, rule_id) values (%s,%s,%s,'IS','concept',%s,'2015-01-01','t','tm.r@1')"
        conn.execute(ins, (co, "us-gaap", "Revenues", x["rev"]))
        conn.execute(ins, (co, "custom", "OpexExclAmort", opex))
        conn.commit()
        assert resolve(conn, {"0000001301"})["errored"] == 0
        rows = {r[0]: r[1:] for r in conn.execute("select canonical_concept_id, value, source_fact_ids, source_value_ids, family from analytics.canonical_fact where company_id = %s", (co,))}
        assert rows[opex] == (Decimal("40"), [], [vid], "company_tag_map:fsn_xbrl")  # filing's own XBRL, fsn lineage
        assert rows[x["rev"]][0] == Decimal("100") and rows[x["rev"]][3] == "company_tag_map" and rows[x["rev"]][2] == []


@pytest.mark.integration
def test_coverage_gate_applies_a_full_window_map_and_rolls_back_a_short_one(isolated_database_url, monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
    with psycopg.connect(isolated_database_url) as conn:
        x, co, per = _setup(conn)  # map era from 2015-01-01: covers the data window
        co2, per2, _, fact2 = x["company"]("0000001002", True)
        fact2("Revenues", "out", "new", "55")
        conn.execute("insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, era_from, decided_by, rule_id) values (%s,'us-gaap','Revenues','IS','concept',%s,'2019-01-01','docmap','company_tag_map.docmap@1')", (co2, x["rev"]))
        conn.execute("insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s,%s,%s,%s,'{}')", (co2, x["rev"], per2["in"], Decimal("7")))
        conn.commit()
        tpl = {c: [("tm_rev", date(2018, 12, 31), "served")] for c in (co, co2)}
        rep = plan.run(conn, [co, co2], tpl, apply=True, gate=True)
        assert "error" not in rep[co] and "error" not in rep[co2], rep
        full, short = rep[co]["coverage"], rep[co2]["coverage"]
        assert (full["era_short"], full["values_lost"], full["fy01_before"], full["fy01_after"]) == ({}, 0, 1, 1)
        assert not rep[co].get("gated")
        assert _one(conn, "select value from analytics.canonical_fact where company_id = %s", co) == Decimal("110")
        # the 2018 period ends before the 2019 era: the 2018 value would go, so the company is rolled back
        assert short["era_short"] == {"tm_rev": "2019-01-01"} and short["fy01_after"] < short["fy01_before"]
        assert rep[co2]["gated"] is True
        assert _one(conn, "select value from analytics.canonical_fact where company_id = %s and period_id = %s", co2, per2["in"]) == Decimal("7")
        assert _one(conn, "select count(*) from analytics.company_value_owner where company_id = %s", co2) == 0
