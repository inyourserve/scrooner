"""Stage 2e-b under source.periodic_form_only@1: 8-K, 8-K/A and 6-K can no longer win
a conflict (WTRG: an 8-K furnishing American Water's statements beat WTRG's own 10-K),
the eligible lists are built from common/periodic_forms.py, and winners already stored
from ineligible forms (8-K recasts, the DEF 14A 77 / DEFR14A 5 residue measured
2026-10-22) can be retired with a backup. Real SQL on a scratch schema."""

from datetime import date
from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.common.periodic_forms import PERIODIC_FORMS_ALL
from scrooner_pipeline.normalizer import conflict_latest_filed as m

D = Decimal


# ------------------------------------------------------------------ the lists
@pytest.mark.unit
def test_flag_off_lists_are_the_historical_ones(monkeypatch):
    monkeypatch.delenv(rf.ENV_ENABLED, raising=False)
    fy, q = m.eligible_forms()
    assert fy == m.FY_ELIGIBLE_FORMS and q == m.QUARTER_ELIGIBLE_FORMS
    assert "8-K" in fy and "6-K" in q


@pytest.mark.unit
def test_flag_on_bans_8k_and_6k_and_builds_from_periodic_forms(monkeypatch):
    monkeypatch.setenv(rf.ENV_ENABLED, "source.periodic_form_only@1")
    fy, q = m.eligible_forms()
    for banned in ("8-K", "8-K/A", "6-K", "6-K/A", "DEF 14A", "DEFR14A", "S-1"):
        assert banned not in fy and banned not in q
    assert set(fy) <= PERIODIC_FORMS_ALL and set(q) == PERIODIC_FORMS_ALL
    assert not {"10-Q", "10-Q/A"} & set(fy)  # a 10-Q never wins an annual value


def c(i, v, form, d, auth=False, derived=False):
    return m.Copy(i, D(v), form, date.fromisoformat(d), auth, derived)


@pytest.mark.unit
def test_classify_ban_value_to_blank_changed_same():
    fy, _ = m.eligible_forms(True)
    # WTRG: the 8-K that won is demoted and the 10-K (still an eligible copy) takes over: value changes
    wtrg = [
        c(1, "1010459000", "10-K", "2026-02-26"),
        c(2, "2059000000", "8-K", "2026-03-25", True),
    ]
    assert m.classify_ban(wtrg, fy, 2) == m.BAN_VALUE_CHANGED
    # only ineligible copies disagree (an 8-K and its amendment): nothing eligible to promote -> blank
    only8k = [c(1, "100", "8-K", "2025-01-01"), c(2, "90", "8-K/A", "2025-02-01", True)]
    assert m.classify_ban(only8k, fy, 2) == m.BAN_VALUE_TO_BLANK
    # two disagreeing 10-Ks plus a recast 8-K that won: the latest 10-K takes over, value changes
    three = [
        c(1, "100", "10-K", "2024-02-01"),
        c(2, "90", "10-K", "2025-02-01"),
        c(3, "80", "8-K", "2025-06-01", True),
    ]
    assert m.classify_ban(three, fy, 3) == m.BAN_VALUE_CHANGED
    # the 8-K recast equals the latest 10-K: same value
    same = [
        c(1, "100", "10-K", "2024-02-01"),
        c(2, "90", "10-K", "2025-02-01"),
        c(3, "90", "8-K", "2025-06-01", True),
    ]
    assert m.classify_ban(same, fy, 3) == m.BAN_VALUE_SAME
    # sign-only conflict among the remaining copies is quarantined
    sign = [
        c(1, "-764", "10-K", "2024-02-01"),
        c(2, "764", "10-K", "2025-02-01"),
        c(3, "764", "DEF 14A", "2025-06-01", True),
    ]
    assert m.classify_ban(sign, fy, 3) == m.BAN_VALUE_TO_BLANK
    # derived rows are never competitors
    assert (
        m.new_winner(
            [
                c(1, "1", "10-K", "2024-02-01"),
                c(2, "2", "10-K", "2025-02-01", derived=True),
            ],
            fy,
            99,
        )
        is None
    )


# --------------------------------------------------------------------- real SQL
SCHEMA = """
create schema rtest;
create table rtest.period (id int primary key, period_type text, fiscal_period text, start_date date, end_date date);
create table rtest.filing (id int primary key, filing_date date, form text);
create table rtest.fact (
    id int primary key, company_id int, concept_id int, unit_id int, period_id int, filing_id int,
    value numeric, is_derived boolean default false, is_authoritative boolean default false);
create table rtest.fact_conflict_resolution (
    fact_id int primary key references rtest.fact(id) on delete cascade, rule text, group_size int,
    value_min numeric, value_max numeric, resolved_at timestamptz default now());
"""


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute("drop schema if exists rtest cascade")
        c.execute(SCHEMA)
        c.execute(
            "insert into rtest.period values (1,'duration','FY','2023-01-01','2023-12-31')"
        )
        c.execute(
            "insert into rtest.filing values (1,'2024-02-01','10-K'), (2,'2025-02-01','10-K'), "
            "(3,'2025-04-01','DEF 14A'), (5,'2025-06-01','8-K'), (6,'2025-06-02','DEFR14A')"
        )
        yield c
        c.rollback()
        c.execute("drop schema if exists rtest cascade")
        c.commit()


def _run(conn, company_ids, fy, q):
    with conn.cursor() as cur:
        cur.execute(
            m.PROMOTE_SQL.replace("core.", "rtest."),
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
                "fy_forms": list(fy),
                "quarter_forms": list(q),
            },
        )


def _facts(conn, company, rows):
    for i, (filing, value) in enumerate(rows):
        conn.execute(
            "insert into rtest.fact (id, company_id, concept_id, unit_id, period_id, filing_id, value) values (%s,%s,10,1,1,%s,%s)",
            (company * 100 + i, company, filing, value),
        )


def _winners(conn, company):
    return sorted(
        r[0]
        for r in conn.execute(
            "select value from rtest.fact where company_id=%s and is_authoritative",
            (company,),
        ).fetchall()
    )


@pytest.mark.integration
def test_8k_recast_wins_with_the_historical_list_and_loses_with_the_ban(conn):
    _facts(conn, 1, [(1, 100), (2, 90), (5, 80)])
    _run(conn, [1], m.FY_ELIGIBLE_FORMS, m.QUARTER_ELIGIBLE_FORMS)
    assert _winners(conn, 1) == [80]
    conn.execute(
        "update rtest.fact set is_authoritative = false; delete from rtest.fact_conflict_resolution"
    )
    _run(conn, [1], *m.eligible_forms(True))
    assert _winners(conn, 1) == [90]


@pytest.mark.integration
def test_find_and_retire_ineligible_winners_needs_the_backup(conn, tmp_path):
    # stored state before the ban: an 8-K recast and a DEFR14A residue promoted as winners
    _facts(conn, 2, [(1, 100), (2, 90), (5, 80)])
    _facts(conn, 3, [(1, 100), (6, 100000)])
    conn.execute("update rtest.fact set is_authoritative = true where id in (204, 301)")
    conn.execute(
        "insert into rtest.fact_conflict_resolution (fact_id, rule, group_size, value_min, value_max) values "
        f"(202, '{m.RULE}', 3, 80, 100), (301, '{m.RULE}', 2, 100, 100000), (200, '{m.RULE}', 3, 80, 100)"
    )
    conn.execute("update rtest.fact set is_authoritative = true where id = 200")
    winners = m.find_ineligible_winners(_CurRw(conn), [2, 3])
    assert sorted(w[0] for w in winners) == [202, 301] and {w[2] for w in winners} == {
        "8-K",
        "DEFR14A",
    }
    with pytest.raises(FileNotFoundError):
        m.retire_ineligible_winners(_CurRw(conn), winners, tmp_path / "none.jsonl")
    bk = tmp_path / "bk.jsonl"
    assert m.write_winner_backup(_CurRw(conn), winners, bk) == 2
    partial = tmp_path / "partial.jsonl"
    partial.write_text(bk.read_text().splitlines()[0] + "\n")
    with pytest.raises(ValueError):
        m.retire_ineligible_winners(_CurRw(conn), winners, partial)
    assert m.retire_ineligible_winners(_CurRw(conn), winners, bk) == {
        "demoted": 1,
        "audit_rows_deleted": 2,
    }
    assert conn.execute(
        "select id from rtest.fact where is_authoritative order by id"
    ).fetchall() == [(200,)]  # the 10-K winner stays
    assert [
        r[0]
        for r in conn.execute(
            "select fact_id from rtest.fact_conflict_resolution"
        ).fetchall()
    ] == [200]


class _CurRw:
    """cell wrapper: rewrite core. -> rtest. for the module's own SQL."""

    def __init__(self, conn):
        self._c = conn

    def cursor(self):
        outer = self._c.cursor()

        class W:
            def __enter__(s):
                outer.__enter__()
                return s

            def __exit__(s, *a):
                return outer.__exit__(*a)

            def execute(s, sql, params=None):
                outer.execute(sql.replace("core.", "rtest."), params)

            def fetchone(s):
                return outer.fetchone()

            def fetchall(s):
                return outer.fetchall()

            @property
            def rowcount(s):
                return outer.rowcount

            @property
            def description(s):
                return outer.description

        return W()
