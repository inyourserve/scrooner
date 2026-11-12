"""Docmap loader against a migrated scratch database (CI: Postgres 16): idempotent, and the cited docmap cuts the
disagreeing library row."""

from __future__ import annotations

from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.mapper import docmap_loader as dl

CSV = """ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note
ZZT,revenue,mapped,us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax,IS,R3.htm,Net sales,same_tag@2020-12-31,FILING-CHECKED,
ZZT,gross_profit,not_presented,,IS,R3.htm,,,FILING-CHECKED,no gross profit line
ZZT,total_debt,component sum,us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent,BS,R4.htm+R4.htm,Debt,,FILING-CHECKED,
ZZT,cash_paid_for_interest,component_in_note,us-gaap:InterestPaidNet,Debt - Narrative ,R60,Interest paid,,FILING-CHECKED,
ZZT,dividends_per_share,not_located,,,,,,ASSUMED,no fact
ZZT,operating_expenses,mapped,us-gaap:Opex:Bad,IS,R3.htm,Opex,,FILING-CHECKED,
"""
MD = "Latest 10-K opened: 0000000099-26-000001 (period 2025-12-31)"


def _snapshot(conn, cid):
    return sorted(conn.execute(
        """select decision, taxonomy, tag, stmt, sign, canonical_concept_id, parent_concept_id, era_from, era_to,
                  evidence_adsh, evidence_report, reason, decided_by, rule_id
           from analytics.company_tag_map where company_id = %s""", (cid,)).fetchall(), key=repr)


@pytest.mark.integration
def test_load_is_idempotent_and_the_cited_docmap_cuts_the_library(isolated_database_url, tmp_path: Path):
    (tmp_path / "ZZT-docmap-2026-11-12.csv").write_text(CSV)
    (tmp_path / "ZZT-docmap-2026-11-12.md").write_text(MD)
    paths = sorted(tmp_path.glob("*-docmap-*.csv"))
    with psycopg.connect(isolated_database_url) as conn:
        cid = conn.execute("insert into core.company (cik, company_name, primary_ticker) values ('0000000099', 'Z', 'ZZT') returning id").fetchone()[0]
        rev = conn.execute("select id from analytics.canonical_concept where name = 'revenue_sanity_resolved'").fetchone()[0]
        lib = conn.execute(
            """insert into analytics.company_tag_map (company_id, cik, taxonomy, tag, stmt, decision, canonical_concept_id,
                   era_from, decided_by, rule_id) values (%s, '0000000099', 'us-gaap', 'Revenues', 'IS', 'concept', %s,
                   '2015-01-01', 'structure', 'company_tag_map.library@1') returning id""", (cid, rev)).fetchone()[0]
        conn.commit()

        first = dl.load(conn, paths, apply=True)
        once = _snapshot(conn, cid)
        assert first["companies"]["0000000099"]["added"] == 5  # revenue, gross profit, 2 debt parts, interest paid
        assert [(r["data_point"], r["why"][:12]) for r in first["rejects"]] == [
            ("dividends_per_share", "unknown stat"), ("operating_expenses_resolved", "invalid row:")]
        assert first["blocked"] == {}  # an invalid row is rejected alone, never the company
        assert [(c["data_point"], c["winner"]) for c in first["conflicts"]] == [("revenue_sanity_resolved", "docmap")]
        assert conn.execute("select era_to::text from analytics.company_tag_map where id = %s", (lib,)).fetchone()[0] == "2019-12-31"
        assert {r[13] for r in once if r[12] == "docmap"} == {dl.RULE_ID}

        second = dl.load(conn, paths, apply=True)
        assert _snapshot(conn, cid) == once
        c = second["companies"]["0000000099"]
        assert (c["added"], c["removed"], c["library_cut"], c["library_deleted"]) == (0, 0, 0, 0)
