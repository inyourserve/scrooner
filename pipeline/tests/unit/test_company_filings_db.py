"""company_filings on a migrated scratch database (CI: Postgres 16, every migration replayed).

Shapes: S has a predecessor P (window 2014-01-01..2018-12-29) and an own CIK; E has an exclude window on its own CIK
(a legal acquirer's pre-merger filings); N has neither (the no-behaviour-change case)."""

from __future__ import annotations

from datetime import date

import psycopg
import pytest

from scrooner_pipeline.common.company_filings import (
    company_filing_accessions,
    company_filings,
    core_filings_cte,
    fsn_filings_cte,
)

S, P, E, N = "0001744489", "0001001039", "0001111111", "0002222222"


def _fsn(conn, acc, cik, form, period, company_id=None):
    conn.execute(
        "insert into fsn.filing (accession, company_id, cik, form, period, fsn_set) values (%s,%s,%s,%s,%s,'t')",
        (acc, company_id, cik, form, period),
    )


def _core(conn, company_id, acc, form, period, sub_cik):
    sid = conn.execute(
        "insert into raw.sec_submissions (cik, source_url, sha256, storage_path, http_status) "
        "values (%s,'u','h',%s,200) returning id",
        (sub_cik, "p/" + acc),
    ).fetchone()[0]
    conn.execute(
        "insert into core.filing (company_id, accession_number, form, period_of_report, filing_date, raw_submission_id) "
        "values (%s,%s,%s,%s,%s,%s)",
        (company_id, acc, form, period, period, sid),
    )


@pytest.fixture
def world(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        ids = {
            k: conn.execute(
                "insert into core.company (cik, company_name, fiscal_year_end) values (%s,%s,'1231') returning id",
                (cik, k),
            ).fetchone()[0]
            for k, cik in (("S", S), ("E", E), ("N", N))
        }
        conn.execute(
            "insert into core.company_history_source (company_id,source_cik,relation,source_name,valid_from,valid_to,reason) "
            "values (%s,%s,'predecessor','P','2014-01-01','2018-12-29','t')",
            (ids["S"], P),
        )
        conn.execute(
            "insert into core.company_history_source (company_id,source_cik,relation,source_name,valid_from,valid_to,reason) "
            "values (%s,%s,'exclude','E','2014-01-01','2016-12-31','t')",
            (ids["E"], E),
        )
        # S: own filings, predecessor filings in / out of the window, a shared period (successor wins)
        _fsn(conn, "S-20", S, "10-K", date(2020, 9, 30), ids["S"])
        _fsn(conn, "S-18", S, "10-K", date(2018, 9, 30), ids["S"])  # shared period with P-18
        _fsn(conn, "P-16", P, "10-K", date(2016, 9, 30), ids["S"])
        _fsn(conn, "P-17A", P, "10-K/A", date(2017, 9, 30), ids["S"])
        _fsn(conn, "P-18", P, "10-K", date(2018, 9, 30), ids["S"])  # dropped: S filed the same period
        _fsn(conn, "P-19", P, "10-K", date(2019, 9, 30), None)  # outside the window
        # E: own filing in its exclude window is another entity's
        _fsn(conn, "E-15", E, "10-K", date(2015, 12, 31), ids["E"])
        _fsn(conn, "E-20", E, "10-K", date(2020, 12, 31), ids["E"])
        # N: nothing special; a stranger's filing must not leak in
        _fsn(conn, "N-19", N, "10-K", date(2019, 12, 31), ids["N"])
        _fsn(conn, "N-20", N, "10-K", date(2020, 12, 31), ids["N"])
        # core.filing, owned by the successor like the normalizer does (raw submission cik = who filed it)
        _core(conn, ids["S"], "S-20", "10-K", date(2020, 9, 30), S)
        _core(conn, ids["S"], "S-18", "10-K", date(2018, 9, 30), S)
        _core(conn, ids["S"], "P-16", "10-K", date(2016, 9, 30), P)
        _core(conn, ids["S"], "P-17A", "10-K/A", date(2017, 9, 30), P)
        _core(conn, ids["S"], "P-18", "10-K", date(2018, 9, 30), P)
        _core(conn, ids["S"], "P-19", "10-K", date(2019, 9, 30), P)
        _core(conn, ids["E"], "E-15", "10-K", date(2015, 12, 31), E)
        _core(conn, ids["E"], "E-20", "10-K", date(2020, 12, 31), E)
        _core(conn, ids["N"], "N-19", "10-K", date(2019, 12, 31), N)
        _core(conn, ids["N"], "N-20", "10-K", date(2020, 12, 31), N)
        conn.commit()
        yield conn, ids


def _acc(conn, cid, source):
    return {f.accession for f in company_filings(conn, cid, source=source)}


def test_successor_gets_own_plus_predecessor_window_and_wins_shared_periods(world):
    conn, ids = world
    expect = {"S-20", "S-18", "P-16", "P-17A"}  # P-18 dropped (shared period), P-19 outside the window
    assert _acc(conn, ids["S"], "fsn") == expect
    assert _acc(conn, ids["S"], "core") == expect
    via = {f.accession: f.via for f in company_filings(conn, ids["S"], source="fsn")}
    assert via == {"S-20": "own", "S-18": "own", "P-16": "predecessor", "P-17A": "predecessor"}
    filer = {f.accession: f.filer_cik for f in company_filings(conn, ids["S"], source="fsn")}
    assert filer["P-16"] == P and filer["S-20"] == S
    # the company's cik is the key, never the filer's
    assert {f.cik for f in company_filings(conn, ids["S"])} == {S}


def test_exclude_window_removes_the_own_filing(world):
    conn, ids = world
    assert _acc(conn, ids["E"], "fsn") == {"E-20"}
    assert _acc(conn, ids["E"], "core") == {"E-20"}


def test_company_without_history_equals_the_raw_cik_set(world):
    conn, ids = world
    raw_fsn = {r[0] for r in conn.execute("select accession from fsn.filing where cik = %s", (N,))}
    raw_core = {
        r[0]
        for r in conn.execute(
            "select accession_number from core.filing where company_id = %s", (ids["N"],)
        )
    }
    assert _acc(conn, ids["N"], "fsn") == raw_fsn == {"N-19", "N-20"}
    assert _acc(conn, ids["N"], "core") == raw_core


def test_forms_period_filters_and_many_companies(world):
    conn, ids = world
    got = company_filings(
        conn, ids["S"], source="fsn", forms=["10-K"], min_period=date(2017, 1, 1)
    )
    assert {f.accession for f in got} == {"S-20", "S-18"}
    many = company_filing_accessions(conn, [ids["S"], ids["N"]], source="fsn")
    assert many == {"S-20", "S-18", "P-16", "P-17A", "N-19", "N-20"}


def test_the_embedded_sql_text_is_the_same_rule(world):
    conn, ids = world
    rows = conn.execute(
        "with " + fsn_filings_cte("co.cik::bigint in (%s)") + " select accession from company_filings",
        (int(S),),
    ).fetchall()
    assert {r[0] for r in rows} == _acc(conn, ids["S"], "fsn")
    rows = conn.execute(
        "with " + core_filings_cte("co.cik::bigint in (%s)") + " select accession from company_core_filings",
        (int(S),),
    ).fetchall()
    assert {r[0] for r in rows} == _acc(conn, ids["S"], "core")
