"""Runs the real PROMOTE_SQL on synthetic rows in an isolated PostgreSQL database.

A Data Verifier check of 47 promoted facts against the original filings
(2026-10-18) found the rule published wrong values: sign-only conflicts (5 of 10
wrong, the latest filing had the flipped sign) and annual values won by proxy
statements or 10-Qs. These tests pin the fixed behavior on real SQL, in a scratch
schema (core. is rewritten to rtest.), so no production table is touched.
"""

from datetime import date

import psycopg
import pytest

from scrooner_pipeline.normalizer import conflict_latest_filed as m

pytestmark = pytest.mark.integration

SCHEMA = """
create schema rtest;
create table rtest.period (id int primary key, period_type text, fiscal_period text, start_date date, end_date date);
create table rtest.filing (id int primary key, filing_date date, form text);
create table rtest.fact (
    id int primary key, company_id int, concept_id int, unit_id int, period_id int, filing_id int,
    value numeric, is_derived boolean default false, is_authoritative boolean default false);
create table rtest.fact_conflict_resolution (
    fact_id int primary key, rule text, group_size int, value_min numeric, value_max numeric,
    resolved_at timestamptz default now());
"""


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute("drop schema if exists rtest cascade")
        c.execute(SCHEMA)
        c.execute(
            "insert into rtest.period values (1,'duration','FY',%s,%s), (2,'duration','Q2',%s,%s)",
            (date(2023, 1, 1), date(2023, 12, 31), date(2023, 4, 1), date(2023, 6, 30)),
        )
        c.execute(
            "insert into rtest.filing values "
            "(1,'2024-02-01','10-K'), (2,'2025-02-01','10-K'), (3,'2025-04-01','DEF 14A'),"
            "(4,'2025-05-01','10-Q'), (5,'2025-06-01','8-K')"
        )
        yield c
        c.rollback()
        c.execute("drop schema if exists rtest cascade")
        c.commit()


def _run(conn, company_ids):
    sql = m.PROMOTE_SQL.replace("core.", "rtest.")
    with conn.cursor() as cur:
        cur.execute(
            sql,
            {
                "company_ids": company_ids,
                "concept_ids": [10],
                "quarter_concept_ids": [10],
                "min_days": m.FULL_YEAR_MIN_DAYS,
                "max_days": m.FULL_YEAR_MAX_DAYS,
                "q_min_days": m.QUARTER_MIN_DAYS,
                "q_max_days": m.QUARTER_MAX_DAYS,
                "rule": m.RULE,
                "rule_quarter": m.RULE_QUARTER,
                "fy_forms": list(m.FY_ELIGIBLE_FORMS),
                "quarter_forms": list(m.QUARTER_ELIGIBLE_FORMS),
            },
        )


def _facts(conn, company, rows, period=1):
    for i, (filing, value) in enumerate(rows):
        conn.execute(
            "insert into rtest.fact (id, company_id, concept_id, unit_id, period_id, filing_id, value) "
            "values (%s, %s, 10, 1, %s, %s, %s)",
            (company * 100 + i, company, period, filing, value),
        )


def _winners(conn, company):
    return sorted(
        r[0]
        for r in conn.execute(
            "select value from rtest.fact where company_id = %s and is_authoritative", (company,)
        ).fetchall()
    )


def test_latest_10k_wins_a_real_restatement(conn):
    _facts(conn, 1, [(1, 100), (2, 90)])  # restated downward in the later 10-K
    _run(conn, [1])
    assert _winners(conn, 1) == [90]


def test_sign_only_conflict_is_quarantined_not_promoted(conn):
    _facts(conn, 2, [(1, -764), (2, 764)])  # the ADT / AEHR / CAPS pattern
    _run(conn, [2])
    assert _winners(conn, 2) == []
    assert conn.execute("select count(*) from rtest.fact_conflict_resolution").fetchone()[0] == 0


def test_proxy_statement_never_wins_an_annual_value(conn):
    _facts(conn, 3, [(2, 30153), (3, 30200)])  # METC: rounded DEF 14A footnote vs the 10-K
    _run(conn, [3])
    assert _winners(conn, 3) == [30153], "the 10-K wins even though only the proxy is later"


def test_ten_q_never_wins_an_annual_value(conn):
    _facts(conn, 4, [(1, 5), (4, 111)])  # OPHC: a 10-Q's AOCI balance read as annual tax
    _run(conn, [4])
    assert _winners(conn, 4) == [5]


def test_recast_in_an_8k_is_eligible(conn):
    _facts(conn, 5, [(1, 4342), (5, 1234)])  # Ford-style recast filed as an 8-K
    _run(conn, [5])
    assert _winners(conn, 5) == [1234]


def test_proxy_sign_flip_quarantines_even_when_a_10k_is_the_only_eligible_copy(conn):
    _facts(conn, 6, [(2, -10700), (3, 10700)])  # METC 2025: 10-K correct, proxy flipped
    _run(conn, [6])
    assert _winners(conn, 6) == []


def test_quarter_values_still_resolve_from_10q_family(conn):
    _facts(conn, 7, [(4, 50), (5, 55)], period=2)
    _run(conn, [7])
    assert _winners(conn, 7) == [55]


def test_an_already_authoritative_group_is_left_alone(conn):
    _facts(conn, 8, [(1, 100), (2, 90)])
    conn.execute("update rtest.fact set is_authoritative = true where id = 800")
    _run(conn, [8])
    assert _winners(conn, 8) == [100]


def test_group_with_only_ineligible_copies_promotes_nothing(conn):
    _facts(conn, 9, [(3, 30200), (4, 111)])  # a proxy and a 10-Q, no annual report copy
    _run(conn, [9])
    assert _winners(conn, 9) == []
