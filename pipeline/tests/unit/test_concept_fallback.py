from datetime import date
from unittest.mock import MagicMock

import pytest

from scrooner_pipeline.mapper.concept_fallback import (
    _find_or_create_instant_period,
    resolve_arithmetic_fallback,
    resolve_fallback_for_company,
)


class _FakeCursor:
    def __init__(self, facts_by_concept, overlap_periods, inserted):
        self._facts_by_concept = facts_by_concept
        self._overlap_periods = overlap_periods
        self._inserted = inserted
        self._last_select_concept_id = None
        self._last_result = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        sql = sql.strip()
        if sql.startswith("select period_id"):
            self._last_select_concept_id = params[1]
            self._last_result = None
        elif sql.startswith("select distinct f.period_id"):
            # The overlap_tag guard query (core.fact/core.concept) -- real
            # column names don't matter here, only which periods it returns.
            self._last_result = [(pid,) for pid in self._overlap_periods]
        elif sql.startswith("delete"):
            pass

    def fetchall(self):
        if self._last_result is not None:
            return self._last_result
        rows = self._facts_by_concept.get(self._last_select_concept_id, {})
        return [(period_id, value, fact_ids) for period_id, (value, fact_ids) in rows.items()]

    def executemany(self, sql, rows):
        self._inserted.extend(rows)


class _FakeConnection:
    def __init__(self, facts_by_concept, overlap_periods=()):
        self._facts_by_concept = facts_by_concept
        self._overlap_periods = overlap_periods
        self.inserted = []

    def cursor(self):
        return _FakeCursor(self._facts_by_concept, self._overlap_periods, self.inserted)


@pytest.mark.unit
class TestResolveFallbackForCompany:
    def test_prefers_primary_on_genuine_overlap(self):
        """The exact 2,168-company case that made a naive sum-mode
        widening unsafe: a company reporting BOTH the combined tag and
        the split tags for the SAME period, with overlap_tag present for
        that period, must resolve to the PRIMARY value alone, not a sum
        of both (which would double-count)."""
        conn = _FakeConnection(
            {
                10: {1: (5000, [100])},  # primary (total_debt): period 1 = 5000
                20: {1: (2500, [101]), 2: (3000, [102])},  # fallback (total_debt_split): period 1 = 2500 (WRONG if summed), period 2 = 3000
            },
            overlap_periods=[1],  # period 1's primary value is confirmed to include the overlap tag
        )
        count = resolve_fallback_for_company(conn, company_id=1, primary_id=10, fallback_id=20, resolved_id=30, overlap_tag="LongTermDebt")
        assert count == 2
        by_period = {row["period_id"]: row["value"] for row in conn.inserted}
        assert by_period[1] == 5000  # genuine overlap: primary wins, not summed with fallback's 2500
        assert by_period[2] == 3000  # only fallback has period 2, used as-is

    def test_sums_primary_and_fallback_when_no_overlap_tag_present(self):
        """The real bug found live 2026-09-13 (OGE Energy: $492M shown vs
        a real $5.86B): a company can report SOME debt under total_debt's
        own tags (e.g. ShortTermBorrowings) and ALL of its long-term debt
        only under the split convention, with no combined LongTermDebt tag
        at all -- in that case both values are real and distinct pieces of
        the same total, and must be ADDED, not one preferred over the
        other."""
        conn = _FakeConnection(
            {
                10: {1: (492, [100])},  # primary: period 1 = 492 (short-term only, no LongTermDebt tag)
                20: {1: (5370, [101])},  # fallback (split): period 1 = 5370 (the real long-term piece)
            },
            overlap_periods=[],  # LongTermDebt tag never present for this company/period
        )
        count = resolve_fallback_for_company(conn, company_id=1, primary_id=10, fallback_id=20, resolved_id=30, overlap_tag="LongTermDebt")
        assert count == 1
        assert conn.inserted[0]["value"] == 5862  # summed, not one or the other

    def test_falls_back_when_primary_absent(self):
        """The real 360-company case this module exists for: only the
        split tags are reported."""
        conn = _FakeConnection(
            {
                10: {},  # primary: nothing
                20: {1: (7500, [200])},  # fallback: period 1 = 7500
            }
        )
        count = resolve_fallback_for_company(conn, company_id=2, primary_id=10, fallback_id=20, resolved_id=30)
        assert count == 1
        assert conn.inserted[0]["value"] == 7500

    def test_no_row_when_neither_source_has_data(self):
        conn = _FakeConnection({10: {}, 20: {}})
        count = resolve_fallback_for_company(conn, company_id=3, primary_id=10, fallback_id=20, resolved_id=30)
        assert count == 0
        assert conn.inserted == []

    def test_disjoint_periods_from_both_sources_all_kept(self):
        conn = _FakeConnection(
            {
                10: {1: (100, [1])},
                20: {2: (200, [2])},
            }
        )
        count = resolve_fallback_for_company(conn, company_id=4, primary_id=10, fallback_id=20, resolved_id=30)
        assert count == 2
        periods = {row["period_id"] for row in conn.inserted}
        assert periods == {1, 2}

    def test_no_overlap_tag_configured_means_always_sum(self):
        """overlap_tag=None (the default) means primary and fallback can
        never legitimately represent the same real figure -- always sum
        where both exist, no guard query needed at all."""
        conn = _FakeConnection({10: {1: (100, [1])}, 20: {1: (200, [2])}})
        count = resolve_fallback_for_company(conn, company_id=5, primary_id=10, fallback_id=20, resolved_id=30)
        assert count == 1
        assert conn.inserted[0]["value"] == 300


@pytest.mark.unit
class TestFindOrCreateInstantPeriod:
    def test_returns_existing_period_id_without_inserting(self):
        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value = (42,)

        result = _find_or_create_instant_period(conn, company_id=1, as_of=date(2025, 12, 31))

        assert result == 42
        # Only the initial select ran -- no insert attempted once a real
        # period already exists for this company/date.
        assert cur.execute.call_count == 1

    def test_creates_a_new_period_when_none_exists(self):
        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        # First select: no existing row. Insert...returning: new id 99.
        cur.fetchone.side_effect = [None, (99,)]

        result = _find_or_create_instant_period(conn, company_id=2, as_of=date(2025, 6, 30))

        assert result == 99
        assert cur.execute.call_count == 2
        insert_sql, insert_params = cur.execute.call_args_list[1].args
        assert "insert into core.period" in insert_sql
        assert insert_params == (2, date(2025, 6, 30), date(2025, 6, 30), 2025)

    def test_reselects_on_a_lost_insert_race(self):
        # A concurrent insert for the same company/date won the race --
        # ON CONFLICT DO NOTHING means our own insert returns no row, so
        # this must re-select rather than crash on an empty fetchone().
        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.side_effect = [None, None, (7,)]

        result = _find_or_create_instant_period(conn, company_id=3, as_of=date(2024, 1, 1))

        assert result == 7
        assert cur.execute.call_count == 3


@pytest.mark.unit
class TestResolveArithmeticFallbackParserExclusion:
    """Found live 2026-09-21 (Hyatt Hotels): resolve_arithmetic_fallback's
    blanket delete-then-reinsert of a *_resolved concept silently wiped a
    value parsers/cost_of_revenue_parser.py had just written into the
    SAME resolved concept via resolve_parser_results() -- neither writer
    knew about the other, the same shared-table scoping bug class already
    hit for roic/roe (Mapper Day 6) and expanded_metrics.py's delete
    scope. These tests assert the fix's actual mechanism (an explicit
    concept_parser_result exclusion in both the DELETE and both INSERT
    branches) stays in place, rather than re-verifying the whole SQL
    round trip against a real database."""

    def _run_and_capture_sql(self):
        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value = (3,)
        resolve_arithmetic_fallback(
            conn, resolved_id=1, primary_id=2, minuend_id=3, subtrahend_id=4, guard_min_value=None,
        )
        return [call.args[0] for call in cur.execute.call_args_list]

    def test_delete_excludes_parser_owned_companies(self):
        statements = self._run_and_capture_sql()
        delete_sql = statements[0]
        assert "delete from analytics.canonical_fact" in delete_sql
        assert "concept_parser_result" in delete_sql

    def test_baseline_passthrough_insert_excludes_parser_owned_companies(self):
        statements = self._run_and_capture_sql()
        insert_sql = statements[1]
        assert insert_sql.count("concept_parser_result") >= 2  # baseline branch + derived branch

    def test_commits_after_write(self):
        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value = (5,)
        count = resolve_arithmetic_fallback(conn, resolved_id=1, primary_id=2, minuend_id=3, subtrahend_id=4, guard_min_value=0)
        assert count == 5
        conn.commit.assert_called_once()
