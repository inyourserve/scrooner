"""Structural loader (company_tag_map.structural@1) against a migrated scratch database: load and clip, hand fix
precedence with the exceptions report, per-year evidence, library merge, validation and idempotence."""

from __future__ import annotations

from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.mapper import structural_loader as sl

DOC = """ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note
ZZT,revenue,mapped,us-gaap:Revenues,IS,R3.htm,Net sales,same_tag@2020-12-31,FILING-CHECKED,
"""
MD = "Latest 10-K opened: 0000000099-26-000001 (period 2025-12-31)"
FIX_HEAD = "data_point,fiscal_year,period_end,decision,tags,stmt,accession,r_page,printed_value,note\n"
REV_FIX = (
    "revenue,2023,2023-12-31,mapped,us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax,IS,"
    "0000000099-24-000002,R4.htm,1234,read it\n"
)
HEAD = "ticker,data_point,decision,period_end,accession,tags,stmts,r_pages,path,filing_checks\n"
CHK = "calc LiabilitiesAndStockholdersEquity: ok"
REV22 = f"ZZT,revenue,mapped,2022-12-31,0000000099-23-000010,us-gaap:SalesRevenueNet,IS,R4:2,IS line 2 top line,{CHK}\n"
REV23 = f"ZZT,revenue,mapped,2023-12-31,0000000099-24-000011,us-gaap:SalesRevenueNet,IS,R5:3,IS line 3 top line,{CHK}\n"


def _setup(conn) -> int:
    cid = conn.execute(
        "insert into core.company (cik, company_name, primary_ticker) values ('0000000099', 'Z', 'ZZT') returning id"
    ).fetchone()[0]
    conn.commit()
    return cid


def _docmap(conn, tmp_path: Path, fixes: str | None = None) -> None:
    d = tmp_path / "reads"
    d.mkdir(exist_ok=True)
    (d / "ZZT-docmap-2026-11-12.csv").write_text(DOC)
    (d / "ZZT-docmap-2026-11-12.md").write_text(MD)
    fdir = None
    if fixes:
        fdir = d / "fixes"
        fdir.mkdir(exist_ok=True)
        (fdir / "ZZT-fixes-2026-11-13.csv").write_text(FIX_HEAD + fixes)
    stats = dl.load(conn, sorted(d.glob("*-docmap-*.csv")), apply=True, fixes=fdir)
    assert stats["blocked"] == {}


def _src(tmp_path: Path, body: str) -> Path:
    d = tmp_path / "structural"
    d.mkdir(exist_ok=True)
    (d / "ZZT.csv").write_text(HEAD + body)
    return d


def _eras(conn, cid, concept="revenue_sanity_resolved"):
    return conn.execute(
        """select m.rule_id, m.tag, m.era_from::text, coalesce(m.era_to::text, ''), m.evidence_adsh,
                  m.evidence_report, m.evidence_line, m.decided_by, m.decision
           from analytics.company_tag_map m join analytics.canonical_concept c
             on c.id = coalesce(m.canonical_concept_id, m.parent_concept_id)
           where m.company_id = %s and c.name = %s order by m.era_from, m.tag""",
        (cid, concept),
    ).fetchall()


def _snapshot(conn, cid):
    return sorted(
        conn.execute(
            """select decision, taxonomy, tag, stmt, sign, canonical_concept_id, parent_concept_id, era_from, era_to,
                      evidence_adsh, evidence_report, evidence_line, reason, decided_by, rule_id
               from analytics.company_tag_map where company_id = %s""",
            (cid,),
        ).fetchall(),
        key=repr,
    )


@pytest.mark.integration
def test_load_clips_machine_rows_around_the_structural_eras(
    isolated_database_url, tmp_path: Path
):
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        _docmap(conn, tmp_path)
        stats = sl.load(conn, _src(tmp_path, REV22 + REV23), apply=True)
        assert stats["blocked"] == {} and stats["rejects"] == []
        got = [(r[0], r[1], r[2], r[3]) for r in _eras(conn, cid)]
        assert got == [
            (dl.RULE_ID, "Revenues", "2020-01-01", "2021-12-31"),
            (sl.RULE_ID, "SalesRevenueNet", "2022-01-01", "2022-12-31"),
            (sl.RULE_ID, "SalesRevenueNet", "2023-01-01", "2023-12-31"),
            (dl.RULE_ID, "Revenues", "2024-01-01", ""),
        ]
        assert {r[7] for r in _eras(conn, cid) if r[0] == sl.RULE_ID} == {
            "structural_resolver"
        }


@pytest.mark.integration
def test_per_year_evidence_is_kept_and_not_carried_back(
    isolated_database_url, tmp_path: Path
):
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        sl.load(conn, _src(tmp_path, REV22 + REV23), apply=True)
        rows = [r for r in _eras(conn, cid) if r[0] == sl.RULE_ID]
        assert [(r[2], r[3], r[4], r[5], r[6]) for r in rows] == [
            ("2022-01-01", "2022-12-31", "0000000099-23-000010", 4, 2),
            ("2023-01-01", "2023-12-31", "0000000099-24-000011", 5, 3),
        ]
        reason = conn.execute(
            "select reason from analytics.company_tag_map where rule_id = %s limit 1",
            (sl.RULE_ID,),
        ).fetchone()[0]
        assert "top line" in reason and "LiabilitiesAndStockholdersEquity" in reason


@pytest.mark.integration
def test_hand_fix_wins_its_cell_and_is_reported_as_an_exception(
    isolated_database_url, tmp_path: Path
):
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        _docmap(conn, tmp_path, REV_FIX)
        stats = sl.load(conn, _src(tmp_path, REV22 + REV23), apply=True)
        got = [(r[0], r[1], r[2], r[3]) for r in _eras(conn, cid)]
        assert (
            dl.FIX_RULE_ID,
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "2023-01-01",
            "2023-12-31",
        ) in got
        assert (sl.RULE_ID, "SalesRevenueNet", "2022-01-01", "2022-12-31") in got
        assert not any(g[0] == sl.RULE_ID and g[2] == "2023-01-01" for g in got)
        (exc,) = stats["exceptions"]
        assert (exc["data_point"], exc["agrees"], exc["fix_era_from"]) == (
            "revenue_sanity_resolved",
            "no",
            "2023-01-01",
        )
        assert exc["structural_tags"] == "us-gaap:SalesRevenueNet"


@pytest.mark.integration
def test_rerun_is_idempotent(isolated_database_url, tmp_path: Path):
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        _docmap(conn, tmp_path, REV_FIX)
        src = _src(tmp_path, REV22 + REV23)
        sl.load(conn, src, apply=True)
        once = _snapshot(conn, cid)
        sl.load(conn, src, apply=True)
        assert _snapshot(conn, cid) == once


@pytest.mark.integration
def test_dry_run_writes_nothing(isolated_database_url, tmp_path: Path):
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        _docmap(conn, tmp_path)
        before = _snapshot(conn, cid)
        stats = sl.load(conn, _src(tmp_path, REV22), apply=False)
        assert stats["applied"] is False and stats["decisions"] == {"mapped": 1}
        assert _snapshot(conn, cid) == before


@pytest.mark.integration
def test_bad_rows_are_rejected_alone_and_the_rest_loads(
    isolated_database_url, tmp_path: Path
):
    body = (
        REV22
        + f"ZZT,no_such_point,mapped,2022-12-31,0000000099-23-000010,us-gaap:X,IS,R4:2,p,{CHK}\n"
        + f"ZZT,revenue,mapped,2021-12-31,0000000099-22-000010,SalesRevenueNet,IS,R4:2,unprefixed tag unknown to the SEC feed,{CHK}\n"
        + "ZZT,revenue,mapped,2020-12-31,0000000099-21-000010,us-gaap:SalesRevenueNet,IS,R4:2,p,calc Assets: FAIL\n"
        + f"ZZT,revenue,mapped,2019-12-31,not-an-accession,us-gaap:SalesRevenueNet,IS,R4:2,p,{CHK}\n"
        + f"ZZT,revenue,derived,2018-12-31,0000000099-19-000010,us-gaap:SalesRevenueNet,IS,R4:2,p,{CHK}\n"
        + f"ZZT,revenue,no_role,2017-12-31,0000000099-18-000010,,IS,,p,{CHK}\n"
    )
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        stats = sl.load(conn, _src(tmp_path, body), apply=True)
        why = sorted(r["why"][:28] for r in stats["rejects"])
        assert why == [
            "accession is not an SEC acce",
            "filing quarantined, its own ",
            "invalid row: taxonomy unreso",
            "no canonical concept of that",
        ]
        assert stats["skipped_derived"] == 1 and stats["skipped_no_role"] == 1
        assert [r[2] for r in _eras(conn, cid)] == ["2022-01-01"]


@pytest.mark.integration
def test_library_rows_follow_the_merge_rule(isolated_database_url, tmp_path: Path):
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        conn.execute(
            """insert into analytics.company_tag_map (company_id, cik, taxonomy, tag, stmt, decision,
                   canonical_concept_id, era_from, decided_by, rule_id)
               select %s, '0000000099', 'us-gaap', 'SalesRevenueNet', 'IS', 'concept', id, date '2020-01-01',
                      'tag_expert', 'company_tag_map.library@1'
               from analytics.canonical_concept where name = 'revenue_sanity_resolved'""",
            (cid,),
        )
        conn.commit()
        other = REV23.replace("SalesRevenueNet", "Revenues")
        stats = sl.load(conn, _src(tmp_path, REV22 + other), apply=True)
        got = [(r[0], r[1], r[2], r[3]) for r in _eras(conn, cid)]
        # FY2022 agrees: the library row stands there; FY2023 differs: structural wins and the library row is cut around it
        assert got == [
            (
                "company_tag_map.library@1",
                "SalesRevenueNet",
                "2020-01-01",
                "2022-12-31",
            ),
            (sl.RULE_ID, "Revenues", "2023-01-01", "2023-12-31"),
            ("company_tag_map.library@1", "SalesRevenueNet", "2024-01-01", ""),
        ]
        assert sum(c["agree"] for c in stats["companies"].values()) == 1
        assert [c["winner"] for c in stats["conflicts"]] == ["structural"]


RHEAD = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,resolver_version\n"


def _rsrc(tmp_path: Path, body: str) -> Path:
    d = tmp_path / "resolver"
    d.mkdir(exist_ok=True)
    (d / "resolver-all110-2026-11-14.csv").write_text(RHEAD + body)
    return d / "resolver-all110-2026-11-14.csv"


def _rrow(dp, pe, decision, nodes, value, accn, chk=CHK, grain="I"):
    return f'0000000099,ZZT,{dp},{pe},{grain},{decision},"{nodes}",{value},{accn},own,{chk},total_debt,resolver-2026-11-14.2\n'


@pytest.mark.integration
def test_resolver_output_format_loads_with_checked_signs_and_per_node_evidence(
    isolated_database_url, tmp_path: Path
):
    body = (
        _rrow(
            "total_debt",
            "2022-12-31",
            "component_sum",
            "ShortTermBorrowings=100 [BS R4:18 debt-role tag]; LongTermDebtNoncurrent=50 [BS R4:21 debt-role tag] | why: total_debt rule",
            150,
            "0000000099-23-000010",
        )
        + _rrow(
            "total_debt",
            "2023-12-31",
            "component_sum",
            "ShortTermBorrowings=100 [BS R4:18 debt-role tag]; LongTermDebtNoncurrent=30 [BS R4:21 debt-role tag] | why: w",
            70,
            "0000000099-24-000010",
        )
        + _rrow(
            "total_debt",
            "2021-12-31",
            "component_sum",
            "ShortTermBorrowings=100 [BS R4:18 debt-role tag]; LongTermDebtNoncurrent=30 [BS R4:21 debt-role tag] | why: w",
            999,
            "0000000099-22-000010",
        )
        + _rrow(
            "revenue",
            "2022-12-31",
            "not_presented",
            " | why: no revenue line",
            "",
            "0000000099-23-000010",
            grain="FY",
        )
        + _rrow(
            "revenue",
            "2023-12-31",
            "mapped",
            "Revenues [R4.htm:2] | why: IS line 2",
            5,
            "0000000099-24-000010",
            chk="calc Assets: FAIL",
            grain="FY",
        )
    )
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        for tag in ("ShortTermBorrowings", "LongTermDebtNoncurrent", "Revenues"):
            conn.execute(
                "insert into core.concept (taxonomy, tag) values ('us-gaap', %s)",
                (tag,),
            )
        conn.commit()
        stats = sl.load(conn, _rsrc(tmp_path, body), apply=True)
        assert stats["blocked"] == {}
        assert sorted(r["why"][:31] for r in stats["rejects"]) == [
            "component sum not verified: the",
            "filing quarantined, its own cal",
        ]
        debt = [
            (r[1], r[2], r[3], r[5], r[6])
            for r in _eras(conn, cid, "total_debt_resolved")
        ]
        assert debt == [
            ("LongTermDebtNoncurrent", "2022-01-01", "2022-12-31", 4, 21),
            ("ShortTermBorrowings", "2022-01-01", "2022-12-31", 4, 18),
            ("LongTermDebtNoncurrent", "2023-01-01", "2023-12-31", 4, 21),
            ("ShortTermBorrowings", "2023-01-01", "2023-12-31", 4, 18),
        ]
        signs = conn.execute(
            "select era_from::text, tag, sign, stmt, taxonomy from analytics.company_tag_map where rule_id = %s and parent_concept_id is not null order by 1, 2",
            (sl.RULE_ID,),
        ).fetchall()
        assert [(s[0][:4], s[1], s[2], s[3], s[4]) for s in signs] == [
            ("2022", "LongTermDebtNoncurrent", 1, "BS", "us-gaap"),
            ("2022", "ShortTermBorrowings", 1, "BS", "us-gaap"),
            ("2023", "LongTermDebtNoncurrent", -1, "BS", "us-gaap"),
            ("2023", "ShortTermBorrowings", 1, "BS", "us-gaap"),
        ]
        rev = _eras(conn, cid)
        assert [(r[8], r[2]) for r in rev] == [("not_presented", "2022-01-01")]


@pytest.mark.integration
def test_docmap_reload_leaves_structural_rows_and_clips_around_them(
    isolated_database_url, tmp_path: Path
):
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        _docmap(conn, tmp_path)
        sl.load(conn, _src(tmp_path, REV22 + REV23), apply=True)
        once = _snapshot(conn, cid)
        _docmap(conn, tmp_path)  # docmap-load again, after the structural load
        assert _snapshot(conn, cid) == once


MEMBER_TAG = "RevenueFromContractWithCustomerExcludingAssessedTax"
MEM23 = (
    f"ZZT,revenue,component_sum,2023-12-31,0000000099-24-000011,"
    f"us-gaap:{MEMBER_TAG}[Product]+us-gaap:{MEMBER_TAG}[Service],IS,R5:3,members sum,{CHK}\n"
)


def _fsn_member_facts(conn, cid: int, products: dict[str, str]) -> None:
    fid = conn.execute(
        "insert into fsn.filing (accession, cik, form, fsn_set, accepted, period) values "
        "('0000000099-24-000011','0000000099','10-K','t','2024-02-01','2023-12-31') returning id"
    ).fetchone()[0]
    tid = conn.execute(
        "insert into fsn.tag (tag, version, custom) values (%s,'2023',false) returning id",
        (MEMBER_TAG,),
    ).fetchone()[0]
    for segs, value in products.items():
        did = conn.execute(
            "insert into fsn.dim (dimh, segments, segt) values (%s,%s,false) returning id",
            (segs, segs),
        ).fetchone()[0]
        conn.execute(
            "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg, value) "
            "values (%s,%s,%s,'2023-12-31',4,'USD',%s,0,'',%s)",
            (fid, cid, tid, did, value),
        )
    conn.commit()


@pytest.mark.integration
def test_member_claim_is_written_with_the_resolved_axis(
    isolated_database_url, tmp_path: Path
):
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        _fsn_member_facts(
            conn,
            cid,
            {"ProductOrService=Product;": "60", "ProductOrService=Service;": "40"},
        )
        stats = sl.load(conn, _src(tmp_path, MEM23), apply=True)
        assert stats["rejects"] == [] and stats["blocked"] == {}
        rows = conn.execute(
            "select decision, taxonomy, tag from analytics.company_tag_map where rule_id = %s order by tag",
            (sl.RULE_ID,),
        ).fetchall()
        assert rows == [
            ("component", "us-gaap", f"{MEMBER_TAG}[ProductOrService=Product]"),
            ("component", "us-gaap", f"{MEMBER_TAG}[ProductOrService=Service]"),
        ]


@pytest.mark.integration
def test_member_claim_without_a_stored_member_fact_is_rejected_and_writes_nothing(
    isolated_database_url, tmp_path: Path
):
    with psycopg.connect(isolated_database_url) as conn:
        cid = _setup(conn)
        _fsn_member_facts(conn, cid, {"ProductOrService=Product;": "60"})  # no Service
        stats = sl.load(conn, _src(tmp_path, MEM23), apply=True)
        assert (
            len(stats["rejects"]) == 1
            and "no stored dimensioned fact" in stats["rejects"][0]["why"]
        )
        assert (
            conn.execute(
                "select count(*) from analytics.company_tag_map where rule_id = %s",
                (sl.RULE_ID,),
            ).fetchone()[0]
            == 0
        )
