"""Runs derived.py's real input-loader SQL on synthetic rows in an isolated
PostgreSQL database (core. is rewritten to rtest.), then feeds the rows the
SQL returns into derive_q4_for_company.

Periodic-form gate (WO-2 RU-1, 2026-10-22): an FY, Q1-Q3 or YTD fact filed
on a proxy (DEF 14A) or an 8-K must never feed a derived quarter, even when
it is the authoritative copy. Cases (FILING-CHECKED in data-team/36 item 2
and ledger 2026-10-22):
- JPM Q4 2025 net income was derived from the DEF 14A pay-versus-performance
  FY (57.0B rounded, 0000019617-26-000096 R2): 57,000 - 44,023 = 12,977M
  (core.fact 182608846). The 10-K FY minus 9M gives 13,025M (fact 340478).
- WTRG's 8-K 0001193125-26-124163 furnishes American Water's statements
  under WTRG's CIK (R1, R7); its FY must not feed WTRG's Q4.
"""

from datetime import date
from decimal import Decimal

import psycopg
import pytest
from scrooner_pipeline.normalizer import derived


@pytest.fixture(autouse=True)
def _release_pair_on(monkeypatch):
    """RU-1 behaviour is flag-gated (default OFF = legacy, proven by the
    *_legacy_off.py copy of this module); these tests exercise it ON."""
    monkeypatch.setenv(
        "SCROONER_RULES_ENABLED",
        "split.event_basis@1,pershare.never_derive@1,derive.periodic_inputs_only@1",
    )
    monkeypatch.delenv("SCROONER_RULES_DRYRUN", raising=False)


pytestmark = pytest.mark.integration

SCHEMA = """
create schema rtest;
create table rtest.period (id int primary key, period_type text, fiscal_year int, fiscal_period text,
                           start_date date, end_date date);
create table rtest.filing (id int primary key, form text);
create table rtest.fact (
    id int primary key, company_id int, concept_id int, unit_id int, period_id int, filing_id int,
    value numeric, raw_object_id int, is_derived boolean default false, is_authoritative boolean default true);
"""

NET_INCOME, USD = 10, 1
FY25 = (date(2025, 1, 1), date(2025, 12, 31))


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute("drop schema if exists rtest cascade")
        c.execute(SCHEMA)
        c.execute(
            "insert into rtest.period values "
            "(1,'duration',2025,'FY',%s,%s), (2,'duration',2025,'Q1',%s,%s),"
            "(3,'duration',2025,'Q2',%s,%s), (4,'duration',2025,'Q3',%s,%s),"
            "(5,'duration',2025,null,%s,%s)",
            (
                *FY25,
                date(2025, 1, 1),
                date(2025, 3, 31),
                date(2025, 4, 1),
                date(2025, 6, 30),
                date(2025, 7, 1),
                date(2025, 9, 30),
                date(2025, 1, 1),
                date(2025, 9, 30),
            ),
        )
        c.execute(
            "insert into rtest.filing values (1,'10-K'), (2,'10-Q'), (3,'DEF 14A'), (4,'8-K'),"
            " (5,'10-K/A'), (6,'10-Q/A'), (7,'S-1')"
        )
        yield c
        c.rollback()
        c.execute("drop schema if exists rtest cascade")
        c.commit()


def _fact(c, fact_id, period_id, filing_id, value, *, company=1, authoritative=True):
    c.execute(
        "insert into rtest.fact (id, company_id, concept_id, unit_id, period_id, filing_id, value,"
        " raw_object_id, is_authoritative) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            fact_id,
            company,
            NET_INCOME,
            USD,
            period_id,
            filing_id,
            value,
            9000 + fact_id,
            authoritative,
        ),
    )


def _run(c, sql, **extra):
    with c.cursor() as cur:
        cur.execute(
            sql.replace("core.", "rtest."),
            {"company_id": 1, "forms": derived.DERIVATION_INPUT_FORMS, **extra},
        )
        return cur.fetchall()


def _quarters(c):
    _fact(c, 11, 2, 2, Decimal("14643"))  # Q1 10-Q
    _fact(c, 12, 3, 2, Decimal("14987"))  # Q2 10-Q
    _fact(c, 13, 4, 2, Decimal("14393"))  # Q3 10-Q (9M = 44,023)


def _derive(monkeypatch, rows):
    q4_key = (date(2025, 10, 1), FY25[1])
    monkeypatch.setattr(derived, "_load_quarterly_candidates", lambda _c, _co: rows)
    monkeypatch.setattr(derived, "_load_nine_month_ytd", lambda _c, _co: {})
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _c, _co: {q4_key: 404}
    )
    monkeypatch.setattr(derived, "_load_reported_duration_keys", lambda _c, _co: set())
    monkeypatch.setattr(
        derived, "_load_authoritative_reported_quarters", lambda _c, _co: {}
    )
    monkeypatch.setattr(derived, "_load_average_concept_ids", lambda _c: set())
    monkeypatch.setattr(derived, "_load_non_additive", lambda _c: (set(), set()))
    captured = []

    class Cur:
        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

        def executemany(self, sql, batch):
            if "insert into core.fact" in sql:
                captured.extend(dict(r) for r in batch)

        def execute(self, *_a):
            pass

    class Conn:
        def cursor(self):
            return Cur()

        def commit(self):
            pass

    stats = derived.derive_q4_for_company(Conn(), 1)
    return stats, captured


def test_jpm_proxy_fy_never_feeds_a_derived_q4(conn, monkeypatch):
    _fact(conn, 1, 1, 3, Decimal("57000"))  # DEF 14A FY, the lone authoritative copy
    _quarters(conn)
    rows = _run(conn, derived.QUARTERLY_CANDIDATES_SQL)
    assert {r[0] for r in rows} == {11, 12, 13}, "the proxy FY must not be loaded"
    stats, inserted = _derive(monkeypatch, rows)
    assert inserted == [] and stats["derived"] == 0


def test_jpm_10k_fy_still_derives_the_correct_q4(conn, monkeypatch):
    _fact(conn, 1, 1, 3, Decimal("57000"), authoritative=False)  # proxy copy
    _fact(conn, 2, 1, 1, Decimal("57048"))  # 10-K copy
    _quarters(conn)
    rows = _run(conn, derived.QUARTERLY_CANDIDATES_SQL)
    stats, inserted = _derive(monkeypatch, rows)
    assert [r["value"] for r in inserted] == [Decimal("13025")]
    assert inserted[0]["filing_id"] == 1


def test_wtrg_8k_fy_and_ytd_are_excluded(conn):
    _fact(conn, 1, 1, 4, Decimal("2059"))  # 8-K FY (another entity's statements)
    _fact(conn, 5, 5, 4, Decimal("1500"))  # 8-K 9M YTD
    _fact(conn, 6, 5, 2, Decimal("1400"))  # 10-Q 9M YTD
    assert _run(conn, derived.QUARTERLY_CANDIDATES_SQL) == []
    ytd = _run(
        conn,
        derived.NINE_MONTH_YTD_SQL,
        min_days=derived.THREE_QUARTER_MIN_DAYS,
        max_days=derived.THREE_QUARTER_MAX_DAYS,
    )
    assert [r[4] for r in ytd] == [Decimal("1400")]
    all_rows = _run(conn, derived.ALL_DURATION_FACTS_SQL)
    assert sorted(r[0] for r in all_rows) == [6]


def test_amendments_count_as_periodic_and_other_forms_do_not(conn):
    _fact(conn, 1, 1, 5, Decimal("100"))  # 10-K/A
    _fact(conn, 2, 2, 6, Decimal("20"))  # 10-Q/A
    _fact(conn, 3, 3, 7, Decimal("30"))  # S-1
    assert sorted(r[0] for r in _run(conn, derived.QUARTERLY_CANDIDATES_SQL)) == [1, 2]


def test_non_authoritative_and_other_company_rows_stay_out(conn):
    _fact(conn, 1, 1, 1, Decimal("100"), authoritative=False)
    _fact(conn, 2, 2, 2, Decimal("20"), company=2)
    assert _run(conn, derived.QUARTERLY_CANDIDATES_SQL) == []
