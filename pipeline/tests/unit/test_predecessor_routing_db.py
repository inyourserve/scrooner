"""Predecessor routing end to end on a migrated scratch database: identity -> periods -> facts, then the
existing selection stages (CI: Postgres 16, every migration replayed).

XOM-shaped: successor S (own CIK) and a predecessor CIK P with no core.company row of its own."""

from __future__ import annotations

import json
from datetime import date

import psycopg
import pytest

from scrooner_pipeline.normalizer import conflict_latest_filed, dedupe, facts, identity, periods

S_CIK, P_CIK = "0002115436", "0000034088"


class _Storage:
    def __init__(self, blobs):
        self.blobs = blobs

    def download(self, path):
        return json.dumps(self.blobs[path]).encode()


def _sub(rows):
    return {
        "name": "X",
        "tickers": [],
        "exchanges": [],
        "fiscalYearEnd": "1231",
        "filings": {
            "recent": {
                "accessionNumber": [r[0] for r in rows],
                "form": ["10-K"] * len(rows),
                "filingDate": [r[1] for r in rows],
                "reportDate": [r[2] for r in rows],
                "items": [""] * len(rows),
            }
        },
    }


def _cf(entries):
    return {"facts": {"us-gaap": {"NetIncomeLoss": {"units": {"USD": [
        {"accn": a, "start": s, "end": e, "val": v} for a, s, e, v in entries]}}}}}


def _raw(conn, table, cik, path):
    return conn.execute(
        f"insert into raw.{table} (cik, source_url, sha256, storage_path, http_status) "
        "values (%s, 'u', 'h', %s, 200) returning id", (cik, path)).fetchone()[0]


@pytest.fixture
def world(isolated_database_url):
    blobs = {
        # predecessor filings: in window (A1), inside the exclude window (A2), outside (A3), no period (A4)
        "sub/p": _sub([("A1", "2015-02-20", "2014-12-31"), ("A2", "2017-02-20", "2016-12-31"),
                       ("A3", "2027-02-20", "2026-12-31"), ("A4", "2015-03-01", "")]),
        "sub/s": _sub([("B1", "2026-02-15", "2025-12-31")]),
        "cf/p": _cf([("A1", "2014-01-01", "2014-12-31", 100), ("A2", "2014-01-01", "2014-06-30", 7),
                     ("A3", "2014-01-01", "2014-09-30", 9), ("A4", "2014-01-01", "2014-12-31", 1),
                     ("A1", "2014-04-26", "2015-04-24", 55)]),  # predecessor's own fiscal calendar
        "cf/s": _cf([("B1", "2014-01-01", "2014-12-31", 105)]),
    }
    with psycopg.connect(isolated_database_url) as conn:
        conn.execute("insert into core.unit (unit_name) values ('usd') on conflict do nothing")
        sid = conn.execute("insert into core.company (cik, company_name, fiscal_year_end) values (%s, 'S', '1231') returning id", (S_CIK,)).fetchone()[0]
        for rel, a, b in (("predecessor", "2014-01-01", "2025-12-31"), ("exclude", "2016-01-01", "2016-12-31")):
            conn.execute(
                "insert into core.company_history_source (company_id, source_cik, relation, source_name, valid_from, valid_to, reason) "
                "values (%s, %s, %s, 'P', %s, %s, 'test')", (sid, P_CIK if rel == "predecessor" else S_CIK, rel, a, b))
        _raw(conn, "sec_submissions", P_CIK, "raw/sub/p"); _raw(conn, "sec_submissions", S_CIK, "raw/sub/s")
        _raw(conn, "sec_companyfacts", P_CIK, "raw/cf/p"); _raw(conn, "sec_companyfacts", S_CIK, "raw/cf/s")
        conn.commit()
        yield conn, sid, _Storage(blobs)


def _run_all(conn, st):
    identity.normalize_identity_for_cik(st, conn, S_CIK)
    periods.normalize_periods_for_cik(st, conn, S_CIK)
    facts.normalize_facts_for_cik(st, conn, S_CIK)
    r = identity.normalize_identity_for_cik(st, conn, P_CIK)
    # an earlier unwindowed load left the out-of-window / excluded predecessor filings in core.filing:
    # their facts must still not be routed (the fact dates themselves are inside the window)
    conn.execute(
        """insert into core.filing (company_id, accession_number, form, filing_date, period_of_report, raw_submission_id)
           select c.id, a.accn, '10-K', a.fd, a.pd, (select id from raw.sec_submissions where cik = %s)
           from core.company c, (values ('A2', date '2017-02-20', date '2016-12-31'),
                                        ('A3', date '2027-02-20', date '2026-12-31')) as a(accn, fd, pd)
           where c.cik = %s""", (P_CIK, S_CIK))
    conn.commit()
    periods.normalize_periods_for_cik(st, conn, P_CIK)
    facts.normalize_facts_for_cik(st, conn, P_CIK)
    return r


@pytest.mark.integration
def test_identity_periods_facts_route_in_window_only_with_predecessor_provenance(world):
    conn, sid, st = world
    r = _run_all(conn, st)
    assert r["predecessor_filings"] == 1  # A1 only: A2 excluded, A3 outside, A4 has no period
    assert conn.execute("select count(*) from core.company where cik = %s", (P_CIK,)).fetchone()[0] == 0
    assert r["predecessor_filings"] == 1 and "A4" not in {x[0] for x in conn.execute("select accession_number from core.filing")}
    # provenance: the routed filing and fact lead back to the predecessor's CIK and accession
    row = conn.execute(
        """select f.accession_number, s.cik, rc.cik from core.fact x
           join core.filing f on f.id = x.filing_id
           join raw.sec_submissions s on s.id = f.raw_submission_id
           join raw.sec_companyfacts rc on rc.id = x.raw_object_id
           where x.company_id = %s and f.accession_number = 'A1' order by x.id""", (sid,)).fetchall()
    assert row and all(t == ("A1", P_CIK, P_CIK) for t in row)
    ends = {x[0] for x in conn.execute(
        "select p.end_date from core.fact x join core.period p on p.id=x.period_id join core.filing f on f.id=x.filing_id where f.accession_number in ('A1','A2','A3','A4')")}
    assert ends == {date(2014, 12, 31), date(2015, 4, 24)}
    assert conn.execute("select count(*) from core.fact x join core.filing f on f.id=x.filing_id where f.accession_number in ('A2','A3','A4')").fetchone()[0] == 0


@pytest.mark.integration
def test_periods_never_relabelled_and_keyed_on_dates(world):
    conn, sid, st = world
    identity.normalize_identity_for_cik(st, conn, S_CIK)
    periods.normalize_periods_for_cik(st, conn, S_CIK)
    conn.execute("update core.period set fiscal_year = 2099, fiscal_period = 'Q2' where company_id=%s and end_date='2014-12-31'", (sid,))
    conn.commit()
    identity.normalize_identity_for_cik(st, conn, P_CIK)
    periods.normalize_periods_for_cik(st, conn, P_CIK)
    got = {(a, b): (fy, fp) for a, b, fy, fp in conn.execute(
        "select start_date, end_date, fiscal_year, fiscal_period from core.period where company_id=%s", (sid,))}
    assert got[(date(2014, 1, 1), date(2014, 12, 31))] == (2099, "Q2")  # successor's label survives
    # the predecessor's own-calendar period (Apr 24 year end) is a separate row, keyed on its dates
    assert (date(2014, 4, 26), date(2015, 4, 24)) in got


@pytest.mark.integration
def test_later_successor_comparative_beats_predecessor_original(world):
    conn, sid, st = world
    _run_all(conn, st)
    n = conn.execute("""select count(*) from core.fact x join core.period p on p.id=x.period_id
        where x.company_id=%s and p.start_date='2014-01-01' and p.end_date='2014-12-31'""", (sid,)).fetchone()[0]
    assert n == 2  # predecessor original (A1, 100) and successor comparative (B1, 105) coexist
    dedupe.resolve_authoritative(conn, {S_CIK})
    conflict_latest_filed.resolve_latest_filed(conn, {S_CIK})
    conn.commit()
    auth = conn.execute("""select f.accession_number, x.value from core.fact x join core.filing f on f.id=x.filing_id
        join core.period p on p.id=x.period_id where x.company_id=%s and x.is_authoritative
        and p.start_date='2014-01-01' and p.end_date='2014-12-31'""", (sid,)).fetchall()
    assert [(a, int(v)) for a, v in auth] == [("B1", 105)]
