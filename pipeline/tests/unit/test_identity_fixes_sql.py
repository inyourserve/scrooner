"""identity.cik_name_ticker@1 fix list, durable overrides and the writer hooks on
REAL SQL (isolated test database; scratch schemas s4_c/s4_a; migration 0100
applied verbatim). Stored 'old' values are the ones read from the database on
2026-10-22 (DATA-INFERRED)."""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.company_master import display_name as dn
from scrooner_pipeline.company_master import identity_fixes as fx
from scrooner_pipeline.company_master import identity_overrides as ov
from scrooner_pipeline.company_master import security_type as st
from scrooner_pipeline.company_master import status as status_mod
from scrooner_pipeline.company_master.universe import (
    UniverseCandidate,
    evaluate_candidate,
)
from scrooner_pipeline.mapper import price_metrics as pm

pytestmark = pytest.mark.integration
MIG = (
    Path(__file__).resolve().parents[2]
    / "db"
    / "migrations"
    / "0100_cell_evidence_reason_registrant_audit.sql"
)
A, C = "s4_a", "s4_c"


def _rw(sql):
    return sql.replace("analytics.", f"{A}.").replace("core.", f"{C}.")


class _Cur:
    def __init__(self, c):
        self._c = c

    def __enter__(self):
        self._c.__enter__()
        return self

    def __exit__(self, *a):
        return self._c.__exit__(*a)

    def execute(self, sql, params=None):
        self._c.execute(_rw(sql), params)
        return self

    def executemany(self, sql, params):
        self._c.executemany(_rw(sql), params)

    def fetchone(self):
        return self._c.fetchone()

    def fetchall(self):
        return self._c.fetchall()

    @property
    def rowcount(self):
        return self._c.rowcount


class _Conn:
    def __init__(self, c):
        self._c = c

    def cursor(self):
        return _Cur(self._c.cursor())

    def execute(self, sql, params=None):
        return self.cursor().execute(sql, params)

    def commit(self):
        self._c.commit()

    def rollback(self):
        self._c.rollback()


@pytest.fixture
def db(isolated_database_url):
    with psycopg.connect(isolated_database_url) as raw:
        for s in (A, C):
            raw.execute(f"drop schema if exists {s} cascade")
        raw.execute(f"create schema {A}; create schema {C};")
        raw.execute(
            f"create table {C}.company (id bigint primary key, cik text unique, company_name text, display_name text,"
            " display_name_source text, display_name_updated_at timestamptz, status text, status_as_of date, status_reason text,"
            " primary_ticker text, primary_ticker_status text, primary_ticker_updated_at timestamptz)"
        )
        raw.execute(
            f"create table {C}.listing (id bigint generated always as identity primary key, company_id bigint, ticker text,"
            " exchange text, effective_from date, effective_to date, source text, unique (company_id, ticker))"
        )
        raw.execute(
            MIG.read_text().replace("analytics.", f"{A}.").replace("core.", f"{C}.")
        )
        raw.execute(
            f"insert into {C}.company (id, cik, company_name, display_name, display_name_source, status, status_as_of, status_reason, primary_ticker, primary_ticker_status) values "
            "(1840, '0000906107', 'VIVMARK RESIDENTIAL', 'AvalonBay Communities, Inc.', 'yfinance', 'active', '2026-08-23', 'filed:2026-07-30', 'VMRK', 'resolved'),"
            "(1895, '0000915912', 'AVALONBAY COMMUNITIES INC', 'AvalonBay Communities Inc', 'yfinance', 'active', '2026-08-23', 'filed:2026-07-30', 'AVB', 'resolved'),"
            "(5851, '0001437107', 'Warner Bros. Discovery, Inc.', null, null, 'active', '2026-10-22', 'filed:2026-08-06', 'WBD', 'resolved'),"
            "(4474, '0002041610', 'Paramount Skydance Corp', null, null, 'active', '2026-08-23', 'filed:2026-08-04', 'PSKY', 'resolved'),"
            "(142, '0000007323', 'ENTERGY ARKANSAS, LLC', 'Entergy Arkansas, Inc. 1M BD 4.875%66', 'yfinance', 'active', '2026-08-23', 'filed:2026-07-31', 'EAI', 'resolved')"
        )
        raw.execute(
            f"insert into {C}.listing (company_id, ticker, exchange, source) values (1840, 'VMRK', 'NYSE', 'unknown'), (4474, 'PSKY', 'Nasdaq', 'unknown'), (4474, 'SKYD', 'NYSE', 'unknown')"
        )
        raw.commit()
        yield raw
        raw.rollback()
        for s in (A, C):
            raw.execute(f"drop schema if exists {s} cascade")
        raw.commit()


def one(db, sql, *p):
    return db.execute(sql, p).fetchone()


@pytest.mark.integration
def test_plan_is_read_only_and_lists_every_item(db):
    plans = fx.plan_fixes(_Conn(db))
    by = {(p.fix.cik, p.fix.audit_field): p for p in plans}
    assert by[("0000906107", "display_name")].old_value == "AvalonBay Communities, Inc."
    assert by[("0000906107", "listing_end:EQR")].old_value == "absent"
    assert by[("0000915912", "status")].action == "apply"
    assert (
        by[("0000041091", "pseudo_ticker")].action == "no_company"
    )  # not in this scratch DB
    assert (
        one(db, f"select display_name from {C}.company where id=1840")[0]
        == "AvalonBay Communities, Inc."
    )
    assert one(db, f"select count(*) from {C}.company_identity_audit")[0] == 0


@pytest.mark.integration
def test_apply_edits_audits_and_is_idempotent(db):
    conn = _Conn(db)
    stats = fx.apply_fixes(conn, fx.plan_fixes(conn))
    db.commit()
    assert (
        stats["applied"] == len(fx.FIX_LIST) - 3
    )  # three companies (GPJA, CMS-PB, PNMXO) are not in the scratch DB
    # id 1840 is NOT renamed; ticker unchanged; display name fixed; EQR history added
    assert one(
        db,
        f"select company_name, primary_ticker, display_name, display_name_source from {C}.company where id=1840",
    ) == ("VIVMARK RESIDENTIAL", "VMRK", "VIVMARK RESIDENTIAL", "sec_submissions")
    assert one(
        db,
        f"select effective_to from {C}.listing where company_id=1840 and ticker='EQR'",
    )[0] == date(2026, 8, 17)
    assert (
        one(db, f"select status, status_reason from {C}.company where id=1895")[0]
        == "delisted"
    )
    assert one(db, f"select status from {C}.company where id=5851")[0] == "delisted"
    assert one(
        db, f"select company_name, primary_ticker from {C}.company where id=4474"
    ) == ("Skydance Corp", "SKYD")
    audits = db.execute(
        f"select field, old_value, new_value, accession, evidence_level from {C}.company_identity_audit order by id"
    ).fetchall()
    assert len(audits) == stats["applied"] and all(
        a[3] for a in audits if a[4] == "FILING-CHECKED"
    )
    assert (
        "display_name",
        "AvalonBay Communities, Inc.",
        "VIVMARK RESIDENTIAL",
        "0001140361-26-033377",
        "FILING-CHECKED",
    ) in audits
    # second plan: nothing left to do
    again = fx.plan_fixes(conn)
    assert {p.action for p in again if p.company_id} == {"already_applied"}
    assert fx.apply_fixes(conn, again)["applied"] == 0


@pytest.mark.integration
def test_reverse_restores_every_old_value_exactly(db):
    conn = _Conn(db)
    snap = lambda: (  # noqa: E731
        db.execute(
            f"select id, company_name, display_name, display_name_source, status, status_reason, primary_ticker from {C}.company order by id"
        ).fetchall(),
        db.execute(
            f"select company_id, ticker, effective_to from {C}.listing order by company_id, ticker"
        ).fetchall(),
    )
    before = snap()
    stats = fx.apply_fixes(conn, fx.plan_fixes(conn))
    db.commit()
    assert snap() != before
    assert fx.reverse_run(conn, stats["run_id"]) == stats["applied"]
    db.commit()
    after = snap()
    # status_as_of is stamped by an apply; everything else is back byte for byte
    assert after == before
    assert (
        one(
            db,
            f"select count(*) from {C}.company_identity_audit where reversed_at is null",
        )[0]
        == 0
    )
    assert ov.load_overrides(conn, "status") == {}


@pytest.mark.integration
def test_overrides_are_read_back_and_reversed_rows_are_ignored(db):
    conn = _Conn(db)
    stats = fx.apply_fixes(conn, fx.plan_fixes(conn))
    db.commit()
    assert json.loads(ov.load_overrides(conn, "status")[1895])["status"] == "delisted"
    assert ov.load_overrides(conn, "primary_ticker", [4474]) == {4474: "SKYD"}
    assert ov.load_overrides(conn, "primary_ticker", [1840]) == {}
    hold = ov.load_market_cap_hold(conn, 1840)
    assert hold.event_date == date(2026, 8, 17)
    assert (
        ov.load_market_cap_hold(conn, 142).event_date is None
    )  # pseudo ticker: always blocked
    with pytest.raises(ValueError):
        ov.load_overrides(conn, "company_name")
    fx.reverse_run(conn, stats["run_id"])
    assert ov.load_market_cap_hold(conn, 1840) is None


@pytest.mark.integration
def test_overrides_are_a_noop_before_migration_0100(db):
    db.execute(f"drop table {C}.company_identity_audit")
    db.commit()
    conn = _Conn(db)
    assert (
        ov.load_overrides(conn, "status") == {}
        and ov.load_market_cap_hold(conn, 1840) is None
    )


@pytest.mark.unit
def test_hold_semantics():
    ev = ov.MarketCapHold(date(2026, 8, 17), "merger")
    assert (
        ov.hold_blocks_share_count(ev, date(2026, 7, 24)) == "hold:merger"
    )  # pre-merger cover count
    assert ov.hold_blocks_share_count(ev, None) == "hold:merger"
    assert ov.hold_blocks_share_count(ev, date(2026, 11, 5)) is None  # Q3 10-Q cover
    assert (
        ov.hold_blocks_share_count(ov.MarketCapHold(None, "pseudo"), date(2030, 1, 1))
        == "hold:pseudo"
    )


# ------------------------------------------------------------------ writer hooks
@pytest.mark.integration
def test_nightly_status_recompute_does_not_undo_the_audited_status(db, monkeypatch):
    conn = _Conn(db)
    fx.apply_fixes(conn, fx.plan_fixes(conn))
    db.commit()
    recent = date.today()
    monkeypatch.setattr(
        status_mod, "_load_latest_filing_dates", lambda c, ids: {i: recent for i in ids}
    )
    monkeypatch.setattr(status_mod, "_load_latest_form15_dates", lambda c, ids: {})
    monkeypatch.setattr(
        status_mod, "_load_candidate_deregistrations", lambda c, ids: []
    )
    monkeypatch.setattr(
        status_mod, "_confirm_deregistered_company_ids", lambda sec, cands: set()
    )

    class Sec:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(status_mod, "SECClient", Sec)
    stats = status_mod.update_status(conn, {"0000915912", "0001437107", "0000906107"})
    assert (
        one(db, f"select status from {C}.company where id=1895")[0] == "delisted"
    )  # recency says active; override wins
    assert one(db, f"select status from {C}.company where id=5851")[0] == "delisted"
    assert one(db, f"select status from {C}.company where id=1840")[0] == "active"
    assert stats["identity_override"] == 2


@pytest.mark.integration
def test_display_name_and_primary_ticker_writers_skip_pinned_companies(db, monkeypatch):
    conn = _Conn(db)
    fx.apply_fixes(conn, fx.plan_fixes(conn))
    db.commit()
    seen = []
    monkeypatch.setattr(dn, "resolve_primary_tickers", lambda c, ciks: {})
    monkeypatch.setattr(
        dn,
        "resolve_display_name",
        lambda t, n, paced=True: seen.append(n) or ("X " + n, "yfinance"),
    )
    dn.update_display_names(conn, {"0000906107", "0000915912"}, paced=False, force=True)
    assert seen == ["AVALONBAY COMMUNITIES INC"]  # 1840 is pinned
    assert (
        one(db, f"select display_name from {C}.company where id=1840")[0]
        == "VIVMARK RESIDENTIAL"
    )
    monkeypatch.setattr(
        st,
        "resolve_primary_tickers",
        lambda c, ciks, fallback_ticker_by_cik=None: {k: "PSKY" for k in ciks},
    )
    st.persist_primary_tickers(conn, {"0002041610", "0000007323"})
    assert (
        one(db, f"select primary_ticker from {C}.company where id=4474")[0] == "SKYD"
    )  # pinned
    assert (
        one(db, f"select primary_ticker from {C}.company where id=142")[0] == "PSKY"
    )  # not pinned: normal path


@pytest.mark.unit
def test_universe_excludes_a_pseudo_ticker():
    base = dict(
        company_id=1,
        filer_id=1,
        security_id=1,
        listing_id=1,
        cik="0000007323",
        ticker="EAI",
        exchange="NYSE",
        security_type="Common Stock",
        company_status="active",
        filing_forms=("10-K", "10-Q"),
    )
    assert (
        evaluate_candidate(UniverseCandidate(**base)).eligibility_status == "eligible"
    )
    d = evaluate_candidate(UniverseCandidate(**base, pseudo_ticker_confirmed=True))
    assert (
        d.eligibility_status == "excluded"
        and "excluded_pseudo_ticker_not_common_equity" in d.reason_codes
    )


@pytest.mark.integration
def test_market_cap_is_withheld_for_a_hold_but_not_otherwise(db, monkeypatch):
    conn = _Conn(db)
    fx.apply_fixes(conn, fx.plan_fixes(conn))
    db.commit()
    written = []

    class Cur:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, sql, params=None):
            return self

        def executemany(self, sql, rows):
            written.extend(rows)

    class FakeConn:
        def cursor(self):
            return Cur()

        def commit(self):
            pass

    holds = ov.load_market_cap_holds(conn, [1840, 1895])
    monkeypatch.setattr(
        pm, "_load_latest_price", lambda c, cid: (Decimal("62.165"), date.today())
    )
    monkeypatch.setattr(pm, "_load_quarterly_facts", lambda c, cid, con: {})
    monkeypatch.setattr(
        pm,
        "_latest_instant_fact",
        lambda c, cid, con: (Decimal("374944409"), [21881820], date(2026, 7, 24)),
    )
    monkeypatch.setattr(pm, "_load_latest_diluted_weighted_shares", lambda c, cid: None)
    monkeypatch.setattr(pm, "_load_shares_outstanding_fallback", lambda c, cid: None)
    names = (
        "market_cap",
        "trailing_pe",
        "price_to_sales",
        "price_to_book",
        "dividend_yield",
        "fcf_yield",
    )
    ids = {n: i for i, n in enumerate(names, 1)}
    concepts = {"shares_outstanding": 1, "stockholders_equity": 2}
    pm.calculate_price_metrics_for_company(FakeConn(), 1840, ids, concepts, holds)
    mc = next(r for r in written if r["metric_definition_id"] == 1)
    assert mc["value"] is None and mc["is_null_reason"].startswith(
        "hold:share_count_predates_merger"
    )
    written.clear()
    pm.calculate_price_metrics_for_company(
        FakeConn(), 1895, ids, concepts, holds
    )  # no hold
    mc = next(r for r in written if r["metric_definition_id"] == 1)
    assert mc["value"] == Decimal("374944409") * Decimal("62.165")
