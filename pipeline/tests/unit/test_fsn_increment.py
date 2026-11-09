"""Nightly hybrid incremental (fsn_store.increment + load --increment) on the real schema (0118/0119).

A real filing (META's 2026-09-30 10-Q, tests/fixtures/fsn_xbrl) is built from its EDGAR files, written
as an increment directory, and loaded beside a company's FSN-set history: the increment adds that
accession only; a rerun is a no-op; a full reload that does not carry the accession keeps it; the
FSN set's copy, once it arrives, replaces it (dedupe by accession); an increment never overwrites an
accession the FSN set already holds."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.fsn_store import increment, load, xbrl_fsn
from scrooner_pipeline.fsn_store.increment import Candidate

from test_fsn_store import ACC as FSN_ACC
from test_fsn_store import _company_dir
from test_fsn_xbrl import META, load_fixture

CIK = "0001326801"


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


def _increment_dir(
    tmp_path: Path, company_id: int | None, fsn_set: str = "edgar:2026-11-09"
) -> Path:
    files, _ = load_fixture(META)
    res = increment.build(
        [Candidate(company_id or 0, CIK, META, "10-Q", "2026-10-29", "2026-09-30")],
        lambda c: files,
    )
    assert not res.failed
    root = tmp_path / "nightly"
    assert increment.write_dirs(root, res.built, {CIK: company_id or 0}, fsn_set) == [
        CIK
    ]
    return root / CIK


def test_build_isolates_a_failing_filing_and_defers_over_budget():
    files, _ = load_fixture(META)
    cands = [
        Candidate(1, CIK, "0000000000-26-000001", "10-Q", "2026-10-29", "2026-09-30"),
        Candidate(1, CIK, META, "10-Q", "2026-10-29", "2026-09-30"),
        Candidate(1, CIK, "0000000000-26-000002", "10-Q", "2026-10-29", "2026-09-30"),
    ]

    def fetch(c):
        if c.accession != META:
            raise RuntimeError("HTTP 404")
        return files

    res = increment.build(cands, fetch)
    assert [f["accession"] for f in res.failed] == [
        "0000000000-26-000001",
        "0000000000-26-000002",
    ]
    assert len(res.built[CIK]) == 1
    ticks = iter([0.0, 0.0, 100.0, 100.0])
    res = increment.build(cands, fetch, max_seconds=50, clock=lambda: next(ticks))
    assert [d["accession"] for d in res.deferred] == [META, "0000000000-26-000002"]


def test_increment_dir_is_the_shard_view(tmp_path):
    d = _increment_dir(tmp_path, 7)
    m = json.loads((d / "manifest.json").read_text())
    assert (
        m["increment"]
        and m["accessions"] == [META]
        and m["fsn_sets"] == ["edgar:2026-11-09"]
    )
    from scrooner_pipeline.fsn_store import company_dir

    data = company_dir.read(d)
    files, expected = load_fixture(META)
    view = xbrl_fsn.shard_filter(xbrl_fsn.convert(files))
    assert len(data["num"]) == len(view["num"]) and len(data["pre"]) == len(view["pre"])
    assert (
        data["sub"][0]["fsn_set"] == "edgar:2026-11-09"
        and data["sub"][0]["adsh"] == META
    )
    assert {r["stmt"] for r in data["pre"]} <= set(company_dir.STATEMENT_STMTS)


@pytest.mark.integration
def test_increment_load_dedupes_by_accession(conn, tmp_path):
    cid = _one(
        conn,
        "insert into core.company (cik, company_name) values (%s, 'META TEST') returning id",
        (CIK,),
    )
    conn.commit()
    # the company's FSN-set history (one older filing) is loaded first
    hist = _company_dir(tmp_path / "hist", cik=CIK)
    assert load.load_company(conn, hist, loader_commit="c1")["filings"] == 1
    conn.commit()
    inc = _increment_dir(tmp_path, cid)
    r1 = load.load_company(conn, inc, loader_commit="c1", increment=True)
    conn.commit()
    assert (
        r1["filings"] == 1
        and r1["value"] > 500
        and r1["line"] > 100
        and r1["calc_arc"] > 50
    )
    rows = conn.execute(
        "select accession, fsn_set from fsn.filing where company_id = %s order by accession",
        (cid,),
    ).fetchall()
    assert rows == sorted([(FSN_ACC, "2026m07"), (META, "edgar:2026-11-09")])
    assert (
        _one(
            conn,
            "select loader_commit from fsn.company_load where company_id = %s",
            (cid,),
        )
        == "c1"
    )
    n_values = _one(
        conn, "select count(*) from fsn.value where company_id = %s", (cid,)
    )
    # the same increment again: nothing written
    r2 = load.load_company(conn, inc, loader_commit="c2", increment=True)
    conn.commit()
    assert r2["skipped"] and r2["unchanged"] == 1
    assert (
        _one(conn, "select count(*) from fsn.value where company_id = %s", (cid,))
        == n_values
    )
    # a full reload of the FSN-set history that does not carry the accession keeps the EDGAR build
    r3 = load.load_company(conn, hist, loader_commit="c3")
    conn.commit()
    assert r3["edgar_filings_kept"] == 1
    assert (
        _one(conn, "select fsn_set from fsn.filing where accession = %s", (META,))
        == "edgar:2026-11-09"
    )
    assert (
        _one(conn, "select count(*) from fsn.value where company_id = %s", (cid,))
        == n_values
    )
    # the SEC set arrives with the accession: the full reload replaces the EDGAR build
    arrived = tmp_path / "arrived"
    inc_set = _increment_dir(arrived, cid, fsn_set="2026m10")
    m = json.loads((inc_set / "manifest.json").read_text())
    m.pop("increment")
    (inc_set / "manifest.json").write_text(json.dumps(m))
    load.load_company(conn, inc_set, loader_commit="c4")
    conn.commit()
    assert (
        _one(conn, "select fsn_set from fsn.filing where accession = %s", (META,))
        == "2026m10"
    )
    assert (
        _one(conn, "select count(*) from fsn.filing where accession = %s", (META,)) == 1
    )
    # an increment never overwrites an accession the FSN set holds
    r5 = load.load_company(conn, inc, loader_commit="c5", increment=True)
    conn.commit()
    assert r5["skipped"] and r5["held_from_fsn_set"] == 1
    assert (
        _one(conn, "select fsn_set from fsn.filing where accession = %s", (META,))
        == "2026m10"
    )
    # a night with the held accession and a new one (an amendment): only the new one is written
    files, _ = load_fixture(META)
    amended = "0001326801-26-000099"
    res = increment.build(
        [
            Candidate(cid, CIK, META, "10-Q", "2026-10-29", "2026-09-30"),
            Candidate(cid, CIK, amended, "10-Q/A", "2026-11-05", "2026-09-30"),
        ],
        lambda c: xbrl_fsn.FilingFiles(c.accession, files.files, files.header),
    )
    increment.write_dirs(tmp_path / "night2", res.built, {CIK: cid}, "edgar:2026-11-10")
    r6 = load.load_company(
        conn, tmp_path / "night2" / CIK, loader_commit="c6", increment=True
    )
    conn.commit()
    assert r6["held_from_fsn_set"] == 1 and r6["filings"] == 1 and r6["line"] > 100
    assert (
        _one(conn, "select fsn_set from fsn.filing where accession = %s", (amended,))
        == "edgar:2026-11-10"
    )
    assert (
        _one(
            conn,
            "select count(*) from fsn.line l join fsn.filing f on f.id = l.filing_id where f.accession = %s",
            (META,),
        )
        == r1["line"]
    )


@pytest.mark.integration
def test_increment_refuses_a_non_edgar_directory(conn, tmp_path):
    _one(
        conn,
        "insert into core.company (cik, company_name) values (%s, 'META TEST') returning id",
        (CIK,),
    )
    conn.commit()
    hist = _company_dir(tmp_path / "hist", cik=CIK)
    with pytest.raises(ValueError):
        load.load_company(conn, hist, loader_commit="c1", increment=True)
    conn.rollback()


@pytest.mark.integration
def test_candidates_are_new_periodic_filings_after_the_floor(conn, tmp_path):
    cid = _one(
        conn,
        "insert into core.company (cik, company_name) values (%s, 'META TEST') returning id",
        (CIK,),
    )
    other = _one(
        conn,
        "insert into core.company (cik, company_name) values ('0000000002', 'OTHER') returning id",
    )
    rows = [
        (cid, META, "10-Q", "2026-10-29", "2026-09-30"),  # new: a candidate
        (
            cid,
            "0001326801-26-000002",
            "10-K/A",
            "2026-11-02",
            "2025-12-31",
        ),  # an amendment: a candidate
        (
            cid,
            "0001326801-26-000003",
            "8-K",
            "2026-10-29",
            "2026-10-29",
        ),  # not periodic
        (
            cid,
            "0001326801-26-000004",
            "10-Q",
            "2026-09-01",
            "2026-06-30",
        ),  # filed before the lookback
        (
            cid,
            "0001326801-26-000005",
            "10-K/A",
            "2026-11-03",
            "2013-12-31",
        ),  # before the 2014 floor
        (
            other,
            "0000000002-26-000001",
            "10-Q",
            "2026-10-30",
            "2026-09-30",
        ),  # not in the cohort
    ]
    for c, a, f, fd, p in rows:
        conn.execute(
            "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) values (%s, %s, %s, %s, %s)",
            (c, a, f, fd, p),
        )
    conn.commit()
    got = increment.candidates(conn, [CIK], date(2026, 10, 25))
    assert [(c.accession, c.form) for c in got] == [
        (META, "10-Q"),
        ("0001326801-26-000002", "10-K/A"),
    ]
    # once the store holds an accession it is no longer a candidate
    hist = _company_dir(tmp_path / "hist", cik=CIK)
    load.load_company(conn, hist, loader_commit="c1")
    conn.commit()
    load.load_company(
        conn, _increment_dir(tmp_path, cid), loader_commit="c1", increment=True
    )
    conn.commit()
    assert [
        c.accession for c in increment.candidates(conn, [CIK], date(2026, 10, 25))
    ] == ["0001326801-26-000002"]
