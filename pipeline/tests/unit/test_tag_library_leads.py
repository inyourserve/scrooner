"""The tag-library leads stage can no longer hang the weekly job (2026-11-02).

Runs 40251015742 and 41375022141 hit the 3h job limit: the leads stage ran
2h09m with statement_timeout=0 and no log line. These tests pin the new
contract: each concept is replaced in its own savepoint under its own timeout,
a slow concept keeps its previous leads, a wall-clock budget stops scoring,
and a failed reconnect is retried with backoff."""

import psycopg
import pytest

from scrooner_pipeline.mapper import tag_library

# Stand-ins for the real candidate/score SQL, which need a populated
# warehouse. The control flow around them is what is under test.
_CANDIDATES_SQL = """
create temp table lead_candidates on commit drop as
select cc.id as canonical_concept_id, c.id as concept_id, 50 as miss_f
from analytics.canonical_concept cc
cross join core.concept c
where cc.name in ('fast_concept', 'slow_concept') and c.tag = 'NewLeadTag'
"""
_SCORE_SQL = """
insert into analytics.concept_gap_lead
    (canonical_concept_id, concept_id, missing_companies_filing, rank, coexist_pairs, agree_rate)
select c.canonical_concept_id, c.concept_id, c.miss_f, 1, 30, 0.9
from lead_candidates c
join analytics.canonical_concept cc on cc.id = c.canonical_concept_id
cross join lateral (select case when cc.name = 'slow_concept' then pg_sleep(5) end) as s
where c.canonical_concept_id = %(concept)s
"""


@pytest.fixture
def conn(isolated_database_url, monkeypatch):
    monkeypatch.setattr(tag_library, "_LEAD_CANDIDATES_SQL", _CANDIDATES_SQL)
    monkeypatch.setattr(tag_library, "_LEAD_SCORE_SQL", _SCORE_SQL)
    c = psycopg.connect(isolated_database_url)
    with c.cursor() as cur:
        cur.execute(
            """insert into analytics.canonical_concept (name, statement, combination_mode)
               values ('fast_concept', 'income_statement', 'first_match'),
                      ('slow_concept', 'income_statement', 'first_match'),
                      ('dropped_concept', 'income_statement', 'first_match')"""
        )
        cur.execute(
            "insert into core.concept (taxonomy, tag) values ('us-gaap', 'OldLeadTag'), ('us-gaap', 'NewLeadTag')"
        )
        # Every concept starts with one old lead.
        cur.execute(
            """insert into analytics.concept_gap_lead
                   (canonical_concept_id, concept_id, missing_companies_filing, rank, coexist_pairs, agree_rate)
               select cc.id, c.id, 10, 1, 20, 0.5
               from analytics.canonical_concept cc cross join core.concept c
               where c.tag = 'OldLeadTag'"""
        )
    c.commit()
    yield c
    c.close()


def _leads(conn) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute(
            """select cc.name, c.tag from analytics.concept_gap_lead gl
               join analytics.canonical_concept cc on cc.id = gl.canonical_concept_id
               join core.concept c on c.id = gl.concept_id"""
        )
        return dict(cur.fetchall())


@pytest.mark.integration
def test_slow_concept_times_out_and_keeps_its_old_leads_while_others_are_replaced(conn):
    stats = tag_library.build_leads(conn, concept_timeout="300ms")

    assert stats == {
        "concepts": 2,
        "scored": 1,
        "timed_out": 1,
        "not_reached": 0,
        "seconds": stats["seconds"],
    }
    assert stats["seconds"] < 4  # the 5s sleep was cancelled, not waited out
    assert _leads(conn) == {
        "fast_concept": "NewLeadTag",  # rescored
        "slow_concept": "OldLeadTag",  # timed out: previous leads kept
        # dropped_concept had no candidates left: pruned
    }


@pytest.mark.integration
def test_exhausted_budget_stops_scoring_and_keeps_unreached_leads(conn):
    stats = tag_library.build_leads(conn, budget_seconds=0, clock=iter([0, 1, 2, 3, 4, 5]).__next__)

    assert stats["scored"] == 0
    assert stats["not_reached"] == 2
    assert _leads(conn) == {"fast_concept": "OldLeadTag", "slow_concept": "OldLeadTag"}


@pytest.mark.unit
def test_reconnect_retries_a_failed_connect_with_backoff():
    sleeps: list[float] = []
    attempts = iter([psycopg.OperationalError("connection failed"), psycopg.OperationalError("again"), "conn"])

    def connect():
        result = next(attempts)
        if isinstance(result, Exception):
            raise result
        return result

    assert tag_library._reconnect("company_tags", 34, connect=connect, sleep=sleeps.append) == "conn"
    assert sleeps == list(tag_library.RECONNECT_BACKOFF_SECONDS[:2])


@pytest.mark.unit
def test_reconnect_gives_up_after_every_backoff():
    def connect():
        raise psycopg.OperationalError("connection failed")

    with pytest.raises(psycopg.OperationalError):
        tag_library._reconnect("lineage", 1, connect=connect, sleep=lambda _: None)
