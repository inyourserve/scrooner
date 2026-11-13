"""Reader fixes (data-team/companies/reads/fixes/<TICKER>-fixes-<date>.csv) against a migrated scratch database:
one cell (data point x fiscal year) overrides the docmap row of that year only; the other years stay."""

from __future__ import annotations

from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.mapper import docmap_loader as dl

FIX_HEAD = "data_point,fiscal_year,period_end,decision,tags,stmt,accession,r_page,printed_value,note\n"
DOC = """ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note
ZZT,revenue,mapped,us-gaap:Revenues,IS,R3.htm,Net sales,same_tag@2020-12-31,FILING-CHECKED,
ZZT,total_debt,component sum,us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent,BS,R4.htm+R4.htm,Debt,same_tag@2020-12-31,FILING-CHECKED,
"""
MD = "Latest 10-K opened: 0000000099-26-000001 (period 2025-12-31)"
REV_FIX = (
    "revenue,2023,2023-12-31,mapped,us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax,IS,"
    "0000000099-24-000002,R4.htm,1234,read it\n"
)


def _setup(conn) -> int:
    cid = conn.execute(
        "insert into core.company (cik, company_name, primary_ticker) values ('0000000099', 'Z', 'ZZT') returning id"
    ).fetchone()[0]
    conn.commit()
    return cid


def _write(tmp_path: Path, fix_rows: str):
    (tmp_path / "ZZT-docmap-2026-11-12.csv").write_text(DOC)
    (tmp_path / "ZZT-docmap-2026-11-12.md").write_text(MD)
    fixes = tmp_path / "fixes"
    fixes.mkdir(exist_ok=True)
    (fixes / "ZZT-fixes-2026-11-13.csv").write_text(FIX_HEAD + fix_rows)
    return sorted(tmp_path.glob("*-docmap-*.csv")), fixes


def _eras(conn, cid, concept):
    return conn.execute(
        """select m.rule_id, m.decided_by, m.tag, m.era_from::text, coalesce(m.era_to::text, ''), m.evidence_adsh,
                  m.evidence_report, m.serve_note
           from analytics.company_tag_map m join analytics.canonical_concept c
             on c.id = coalesce(m.canonical_concept_id, m.parent_concept_id)
           where m.company_id = %s and c.name = %s order by m.era_from, m.tag""",
        (cid, concept),
    ).fetchall()


def _snapshot(conn, cid):
    return sorted(
        conn.execute(
            """select decision, taxonomy, tag, stmt, sign, canonical_concept_id, parent_concept_id, era_from, era_to,
                      evidence_adsh, evidence_report, serve_note, decided_by, rule_id
               from analytics.company_tag_map where company_id = %s""",
            (cid,),
        ).fetchall(),
        key=repr,
    )


@pytest.mark.integration
def test_fix_clips_the_docmap_row_into_before_and_after_pieces(
    isolated_database_url, tmp_path: Path
):
    paths, fixes = _write(tmp_path, REV_FIX)
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        stats = dl.load(conn, paths, apply=True, fixes=fixes)
        assert (
            stats["blocked"] == {}
            and stats["fix_files"] == 1
            and stats["fix_rows"] == 1
        )
        rows = _eras(conn, cid, "revenue_sanity_resolved")
        assert [(r[0], r[1], r[3], r[4]) for r in rows] == [
            (dl.RULE_ID, "docmap", "2020-01-01", "2022-12-31"),
            (dl.FIX_RULE_ID, "reader_fix", "2023-01-01", "2023-12-31"),
            (dl.RULE_ID, "docmap", "2024-01-01", ""),
        ]
        fix = rows[1]
        assert fix[2] == "RevenueFromContractWithCustomerExcludingAssessedTax"
        assert (fix[5], fix[6]) == ("0000000099-24-000002", 4)
        assert "1234" in fix[7] and "never served" in fix[7]


@pytest.mark.integration
def test_fix_rerun_is_idempotent(isolated_database_url, tmp_path: Path):
    paths, fixes = _write(tmp_path, REV_FIX)
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        dl.load(conn, paths, apply=True, fixes=fixes)
        once = _snapshot(conn, cid)
        second = dl.load(conn, paths, apply=True, fixes=fixes)
        assert _snapshot(conn, cid) == once
        c = second["companies"]["0000000099"]
        assert (c["added"], c["removed"]) == (0, 0)


@pytest.mark.integration
def test_fix_with_unknown_decision_is_rejected_alone(
    isolated_database_url, tmp_path: Path
):
    bad = "revenue,2022,2022-12-31,guessed,us-gaap:Revenues,IS,0000000099-23-000001,R4.htm,1,x\n"
    paths, fixes = _write(tmp_path, REV_FIX + bad)
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        stats = dl.load(conn, paths, apply=True, fixes=fixes)
        assert [(r["data_point"], r["why"][:27]) for r in stats["rejects"]] == [
            ("revenue", "fix: unknown decision 'gues")
        ]
        assert stats["blocked"] == {}
        eras = [(r[0], r[3], r[4]) for r in _eras(conn, cid, "revenue_sanity_resolved")]
        assert (
            dl.FIX_RULE_ID,
            "2023-01-01",
            "2023-12-31",
        ) in eras  # the good fix still landed
        assert (
            dl.RULE_ID,
            "2020-01-01",
            "2022-12-31",
        ) in eras  # the rejected year keeps the docmap row


@pytest.mark.integration
def test_component_sum_fix_clips_and_writes_one_row_per_part(
    isolated_database_url, tmp_path: Path
):
    paths, fixes = _write(
        tmp_path,
        "total_debt,2022,2022-12-31,component sum,us-gaap:LongTermDebtCurrent+us-gaap:SecuredDebt,BS,"
        "0000000099-23-000001,R2.htm,900,sum\n",
    )
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        stats = dl.load(conn, paths, apply=True, fixes=fixes)
        assert stats["blocked"] == {} and stats["rejects"] == []
        got = [
            (r[0], r[2], r[3], r[4]) for r in _eras(conn, cid, "total_debt_resolved")
        ]
        assert sorted(got) == sorted(
            [
                (dl.FIX_RULE_ID, "LongTermDebtCurrent", "2022-01-01", "2022-12-31"),
                (dl.FIX_RULE_ID, "SecuredDebt", "2022-01-01", "2022-12-31"),
                (dl.RULE_ID, "LongTermDebtCurrent", "2020-01-01", "2021-12-31"),
                (dl.RULE_ID, "LongTermDebtNoncurrent", "2020-01-01", "2021-12-31"),
                (dl.RULE_ID, "LongTermDebtCurrent", "2023-01-01", ""),
                (dl.RULE_ID, "LongTermDebtNoncurrent", "2023-01-01", ""),
            ]
        )
