"""FSN store: shard writer + loader round trip on the real schema (migrations 0118/0119), seed validation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.fsn_store import company_dir, load, rules, shard

ACC = "0000789019-26-000001"


def _zst(path: Path, header: list[str], rows: list[list[str]]) -> None:
    body = "\n".join(["\t".join(header), *("\t".join(r) for r in rows)]) + "\n"
    path.write_bytes(
        subprocess.run(
            ["zstd", "-q", "-c"], input=body.encode(), capture_output=True, check=True
        ).stdout
    )


def _company_dir(tmp_path: Path, cik: str = "0000789019") -> Path:
    d = tmp_path / "companies" / cik
    d.mkdir(parents=True)
    _zst(
        d / "sub.tsv.zst",
        [
            "fsn_set",
            "adsh",
            "cik",
            "form",
            "period",
            "fy",
            "fp",
            "fye",
            "filed",
            "accepted",
            "prevrpt",
            "aciks",
        ],
        [
            [
                "2026m07",
                ACC,
                cik.lstrip("0"),
                "10-K",
                "20260630",
                "2026",
                "FY",
                "0630",
                "20260729",
                "2026-07-29 16:05:00.0",
                "0",
                "",
            ]
        ],
    )
    _zst(
        d / "pre.tsv.zst",
        [
            "adsh",
            "report",
            "line",
            "stmt",
            "inpth",
            "tag",
            "version",
            "prole",
            "plabel",
            "negating",
        ],
        [
            [
                ACC,
                "4",
                "1",
                "IS",
                "0",
                "Revenues",
                "us-gaap/2025",
                "terseLabel",
                "Revenue",
                "0",
            ],
            [
                ACC,
                "4",
                "2",
                "IS",
                "0",
                "CostOfRevenue",
                "us-gaap/2025",
                "terseLabel",
                "Cost of revenue",
                "0",
            ],
            [
                ACC,
                "4",
                "3",
                "IS",
                "0",
                "GrossProfit",
                "us-gaap/2025",
                "totalLabel",
                "Gross margin",
                "0",
            ],
        ],
    )
    _zst(
        d / "num.tsv.zst",
        [
            "adsh",
            "tag",
            "version",
            "ddate",
            "qtrs",
            "uom",
            "dimh",
            "iprx",
            "value",
            "footnote",
            "footlen",
            "dimn",
            "coreg",
            "durp",
            "datp",
            "dcml",
        ],
        [
            [
                ACC,
                "Revenues",
                "us-gaap/2025",
                "20260630",
                "4",
                "USD",
                "0x00000000",
                "0",
                "281724000000",
                "",
                "0",
                "0",
                "",
                "1.0",
                "0.0",
                "-6",
            ],
            [
                ACC,
                "Revenues",
                "us-gaap/2025",
                "20250630",
                "4",
                "USD",
                "0x00000000",
                "0",
                "245122000000",
                "",
                "0",
                "0",
                "",
                "1.0",
                "0.0",
                "-6",
            ],
            [
                ACC,
                "CostOfRevenue",
                "us-gaap/2025",
                "20260630",
                "4",
                "USD",
                "0x00000000",
                "0",
                "88000000000",
                "",
                "0",
                "0",
                "",
                "1.0",
                "0.0",
                "-6",
            ],
            [
                ACC,
                "GrossProfit",
                "us-gaap/2025",
                "20260630",
                "4",
                "USD",
                "0x00000000",
                "0",
                "193724000000",
                "",
                "0",
                "0",
                "",
                "1.0",
                "0.0",
                "-6",
            ],
            [
                ACC,
                "Revenues",
                "us-gaap/2025",
                "20260630",
                "4",
                "USD",
                "0xabc",
                "0",
                "100",
                "",
                "0",
                "1",
                "",
                "1.0",
                "0.0",
                "-6",
            ],
        ],
    )
    _zst(
        d / "cal.tsv.zst",
        ["adsh", "grp", "arc", "negative", "ptag", "pversion", "ctag", "cversion"],
        [
            [
                ACC,
                "1",
                "1",
                "1",
                "GrossProfit",
                "us-gaap/2025",
                "Revenues",
                "us-gaap/2025",
            ],
            [
                ACC,
                "1",
                "2",
                "-1",
                "GrossProfit",
                "us-gaap/2025",
                "CostOfRevenue",
                "us-gaap/2025",
            ],
        ],
    )
    _zst(
        d / "ren.tsv.zst",
        [
            "adsh",
            "report",
            "rfile",
            "menucat",
            "shortname",
            "longname",
            "roleuri",
            "parentroleuri",
            "parentreport",
            "ultparentrpt",
        ],
        [
            [
                ACC,
                "4",
                "H",
                "S",
                "INCOME STATEMENTS",
                "0000004 - Statement - INCOME STATEMENTS",
                "http://x/role/IS",
                "",
                "",
                "",
            ]
        ],
    )
    _zst(
        d / "tag.tsv.zst",
        [
            "tag",
            "version",
            "custom",
            "abstract",
            "datatype",
            "iord",
            "crdr",
            "tlabel",
            "doc",
        ],
        [
            [
                "Revenues",
                "us-gaap/2025",
                "0",
                "0",
                "monetary",
                "D",
                "C",
                "Revenues",
                "",
            ],
            [
                "CostOfRevenue",
                "us-gaap/2025",
                "0",
                "0",
                "monetary",
                "D",
                "D",
                "Cost of Revenue",
                "",
            ],
            [
                "GrossProfit",
                "us-gaap/2025",
                "0",
                "0",
                "monetary",
                "D",
                "C",
                "Gross Profit",
                "",
            ],
        ],
    )
    _zst(
        d / "dim.tsv.zst",
        ["dimhash", "segments", "segt"],
        [["0xabc", "ProductOrServiceAxis=ServiceMember;", "0"]],
    )
    shard.finalize(tmp_path / "companies", cik, None, ["2026m07"], "test")
    return d


@pytest.mark.unit
def test_company_dir_reader_and_manifest(tmp_path):
    d = _company_dir(tmp_path)
    data = company_dir.read(d)
    m = data["manifest"]
    assert m["row_counts"] == {
        "sub": 1,
        "pre": 3,
        "num": 5,
        "cal": 2,
        "ren": 1,
        "tag": 3,
        "dim": 1,
    }
    assert (
        m["accessions"] == [ACC]
        and m["fsn_sets"] == ["2026m07"]
        and len(m["input_sha256"]) == 64
    )
    assert data["num"][0]["value"] == "281724000000"  # SEC strings untouched


@pytest.mark.unit
def test_seed_validation_names_every_error():
    ids = {"revenue_sanity_resolved": 1, "cost_of_revenue_resolved": 2}
    good = {
        "canonical_concept": "revenue_sanity_resolved",
        "stmt": "IS",
        "match_kind": "std_tag",
        "tag": "us-gaap:Revenues",
        "position": None,
        "components": None,
        "priority": 10,
        "era_from": None,
        "era_to": None,
        "rule_id": "is.revenue_total@1",
        "source_commit": "78ca35e",
        "evidence": "tag card",
    }
    assert rules.validate([good], ids) == []
    bad = [
        dict(good, canonical_concept="x"),
        dict(good, tag="Revenues"),
        dict(good, match_kind="calc_position", tag=None),
        dict(good, rule_id="revenue"),
        dict(good, priority="10"),
        good,
        good,
    ]
    errs = rules.validate(bad, ids)
    assert len(errs) == 7 and sum("duplicate" in e for e in errs) == 2


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if (
        _one(
            c,
            "select count(*) from information_schema.tables where table_schema = 'fsn' and table_name in ('filing', 'value', 'company_load')",
        )
        != 3
    ):
        c.close()
        pytest.skip("needs migrations 0118/0119")
    yield c
    c.close()


@pytest.mark.integration
def test_load_company_is_atomic_idempotent_and_keeps_every_print(conn, tmp_path):
    cid = _one(
        conn,
        "insert into core.company (cik, company_name) values ('0000789019', 'MSFT TEST') returning id",
    )
    conn.commit()
    d = _company_dir(tmp_path)
    r1 = load.load_company(conn, d, loader_commit="c1")
    conn.commit()
    assert (
        r1["filings"] == 1
        and r1["line"] == 3
        and r1["value"] == 5
        and r1["calc_arc"] == 2
        and r1["report"] == 1
    )
    assert (
        _one(
            conn,
            "select count(*) from fsn.value v join fsn.filing f on f.id = v.filing_id where f.company_id = %s and v.dim_id = 0",
            (cid,),
        )
        == 4
    )
    assert (
        _one(
            conn,
            "select weight from fsn.calc_arc a join fsn.tag t on t.id = a.child_tag_id where t.tag = 'CostOfRevenue'",
        )
        == -1
    )
    assert _one(
        conn, "select accepted::text from fsn.filing where accession = %s", (ACC,)
    ).startswith("2026-07-29 16:05")
    # same input + same commit -> skipped; forced reload -> same counts, no duplicates
    assert load.load_company(conn, d, loader_commit="c1")["skipped"] is True
    r3 = load.load_company(conn, d, loader_commit="c2")
    conn.commit()
    assert r3["skipped"] is False and r3["filings_deleted"] == 1 and r3["value"] == 5
    assert (
        _one(conn, "select count(*) from fsn.filing where company_id = %s", (cid,)) == 1
    )
    assert (
        _one(
            conn,
            "select loader_commit from fsn.company_load where company_id = %s",
            (cid,),
        )
        == "c2"
    )
    # 0119 guard: a canonical_fact write for an owned company is skipped unless the session is the fsn writer
    conn.execute(
        "insert into analytics.company_value_owner (company_id, owner) values (%s, 'fsn_cells')",
        (cid,),
    )
    ccid = _one(
        conn,
        "insert into analytics.canonical_concept (name, statement, combination_mode) values ('fsn_test_concept', 'income_statement', 'first_match') returning id",
    )
    pid = _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) values (%s, '2025-07-01', '2026-06-30', 'duration', 2026, 'FY') returning id",
        (cid,),
    )
    conn.execute(
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s, %s, %s, 1, '{}')",
        (cid, ccid, pid),
    )
    assert (
        _one(
            conn,
            "select count(*) from analytics.canonical_fact where company_id = %s",
            (cid,),
        )
        == 0
    )
    assert (
        _one(
            conn,
            "select count(*) from analytics.owned_write_skipped where company_id = %s",
            (cid,),
        )
        == 1
    )
    conn.execute("set local scrooner.writer = 'fsn_cells'")
    conn.execute(
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s, %s, %s, 1, '{}')",
        (cid, ccid, pid),
    )
    assert (
        _one(
            conn,
            "select count(*) from analytics.canonical_fact where company_id = %s",
            (cid,),
        )
        == 1
    )
    conn.rollback()


@pytest.mark.integration
def test_seed_apply_writes_every_rule_including_demote_patterns(conn, tmp_path):
    # the v1.1 tag_pattern column was in the insert but not in the parameters (pilot run 41311864687)
    conn.execute(
        "insert into analytics.canonical_concept (name, statement, combination_mode) "
        "values ('revenue_sanity_resolved', 'income_statement', 'first_match') on conflict (name) do nothing"
    )
    conn.commit()
    base = {"canonical_concept": "revenue_sanity_resolved", "stmt": "IS", "position": None, "components": None,
            "priority": 10, "era_from": None, "era_to": None, "rule_id": "is.revenue_total@1",
            "source_commit": "abc1234", "evidence": "test"}
    rows = [
        {**base, "match_kind": "std_tag", "tag": "us-gaap:Revenues", "tag_pattern": None},
        {**base, "match_kind": "demote", "tag": None, "tag_pattern": "^[0-9-]+:.*Interest.*$", "priority": 20,
         "rule_id": "is.revenue_demote@1"},
    ]
    p = tmp_path / "is.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    res = rules.seed(conn, p, apply=True)
    assert res["written"] == 2 and res["errors"] == []
    got = conn.execute("select match_kind, tag, tag_pattern from fsn.concept_rule order by priority").fetchall()
    assert got == [("std_tag", "us-gaap:Revenues", None), ("demote", None, "^[0-9-]+:.*Interest.*$")]


@pytest.mark.integration
def test_predecessor_filings_load_under_the_successor_company(conn, tmp_path):
    # XOM: history filed as 0000034088, the company master holds only the successor 0002115436
    succ = _one(
        conn,
        "insert into core.company (cik, company_name) values ('0002115436', 'SUCCESSOR TEST') returning id",
    )
    conn.commit()
    d = _company_dir(tmp_path, cik="0000034088")
    with pytest.raises(LookupError):
        load.load_company(conn, d, loader_commit="c1")
    conn.rollback()
    r = load.load_company(
        conn, d, loader_commit="c1", predecessors={"0000034088": "0002115436"}
    )
    conn.commit()
    assert r["filings"] == 1
    assert conn.execute("select company_id, cik from fsn.filing").fetchall() == [(succ, "0000034088")]
    assert conn.execute("select count(distinct company_id) from fsn.value").fetchone()[0] == 1
    assert conn.execute("select company_id from fsn.value limit 1").fetchone()[0] == succ


@pytest.mark.unit
def test_owners_follow_history_windows_and_exclusions():
    # core.company_history_source: Dow Chemical serves Dow Inc to 2018-12-31 and DowDuPont to 2017-06-30;
    # Johnson Controls' own CIK holds Tyco's filings to 2016-06-30 (excluded)
    targets = {"0001751788", "0001666700", "0000833444"}
    alias = {"0000029915": [("0001751788", "20140101", "20181231"), ("0001666700", "20140101", "20170630")]}
    exclude = {"0000833444": [("20140101", "20160630")]}

    def own(cik, period, aciks=""):
        return shard.owners_of({"cik": cik.lstrip("0"), "period": period, "aciks": aciks}, targets, alias, exclude)

    assert own("0000029915", "20161231") == ["0001666700", "0001751788"]  # both windows
    assert own("0000029915", "20180930") == ["0001751788"]  # DowDuPont's window closed
    assert own("0000029915", "20190331") == []  # after both
    assert own("0000833444", "20160331") == []  # Tyco under JCI's CIK: wrong entity
    assert own("0000833444", "20160930") == ["0000833444"]  # JCI's own history from the merger
    assert own("0001751788", "20190331", aciks="29915") == ["0001751788"]  # co-filing, once
