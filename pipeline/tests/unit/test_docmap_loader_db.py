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


DIMS_CSV = """ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note
ZZD,cost_of_revenue,component sum,us-gaap:CostOfGoodsAndServicesSold[ProductOrService=Product]+us-gaap:CostOfGoodsAndServicesSold[ProductOrService=Service],IS,R4.htm+R4.htm,Cost of sales,same_tag@2020-12-31,FILING-CHECKED,
ZZD,weighted_diluted_shares,mapped,us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding[ClassOfStock=us-gaap:CommonClassAMember],IS,R4.htm,Diluted Class A,same_tag@2020-12-31,FILING-CHECKED,
ZZD,revenue,mapped,us-gaap:Revenues[ProductOrService=Product],IS,R4.htm,Revenues,same_tag@2020-12-31,FILING-CHECKED,
"""
MIGRATION_0125 = Path(__file__).resolve().parents[2] / "db/migrations/0125_company_tag_map_dims.sql"


@pytest.mark.integration
def test_dimensional_rows_load_with_their_segments_and_a_refusable_one_is_rejected_alone(isolated_database_url, tmp_path: Path):
    (tmp_path / "ZZD-docmap-2026-11-13.csv").write_text(DIMS_CSV)
    (tmp_path / "ZZD-docmap-2026-11-13.md").write_text(MD)
    paths = sorted(tmp_path.glob("*-docmap-*.csv"))
    with psycopg.connect(isolated_database_url) as conn:
        if not conn.execute("select 1 from information_schema.columns where table_name = 'company_tag_map' and column_name = 'dims'").fetchone():
            conn.execute(MIGRATION_0125.read_text())  # until it lands contiguously (CI applies it with the rest)
        cid = conn.execute("insert into core.company (cik, company_name, primary_ticker) values ('0000000098', 'Z', 'ZZD') returning id").fetchone()[0]
        conn.commit()
        first = dl.load(conn, paths, apply=True)
        assert first["blocked"] == {}
        assert [(r["data_point"], r["why"][:12]) for r in first["rejects"]] == [("revenue_sanity_resolved", "invalid row:")]  # a slice is no data point
        got = conn.execute(
            """select decision, tag, dims from analytics.company_tag_map where company_id = %s and rule_id = %s order by dims""",
            (cid, dl.RULE_ID),
        ).fetchall()
        assert got == [
            ("concept", "WeightedAverageNumberOfDilutedSharesOutstanding", "ClassOfStock=CommonClassA;"),
            ("component", "CostOfGoodsAndServicesSold", "ProductOrService=Product;"),
            ("component", "CostOfGoodsAndServicesSold", "ProductOrService=Service;"),
        ]
        second = dl.load(conn, paths, apply=True)
        c = second["companies"]["0000000098"]
        assert (c["added"], c["removed"]) == (0, 0)  # idempotent: dims are part of the row's content
        # a library row of the same tag WITHOUT dims is a different line: the docmap's dimensional parts conflict with it
        cost = conn.execute("select id from analytics.canonical_concept where name = 'cost_of_revenue_resolved'").fetchone()[0]
        conn.execute(
            """insert into analytics.company_tag_map (company_id, cik, taxonomy, tag, stmt, decision, canonical_concept_id,
                   era_from, decided_by, rule_id) values (%s, '0000000098', 'us-gaap', 'CostOfGoodsAndServicesSold', 'IS', 'concept', %s,
                   '2015-01-01', 'structure', 'company_tag_map.library@1')""", (cid, cost))
        conn.commit()
        third = dl.load(conn, paths, apply=False)
        assert [(x["data_point"], x["winner"]) for x in third["conflicts"]] == [("cost_of_revenue_resolved", "docmap")]
