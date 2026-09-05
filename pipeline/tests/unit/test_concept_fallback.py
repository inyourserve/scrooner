import pytest

from scrooner_pipeline.mapper.concept_fallback import resolve_fallback_for_company


class _FakeCursor:
    def __init__(self, facts_by_concept, inserted):
        self._facts_by_concept = facts_by_concept
        self._inserted = inserted
        self._last_select_concept_id = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        if sql.strip().startswith("select period_id"):
            self._last_select_concept_id = params[1]
        elif sql.strip().startswith("delete"):
            pass

    def fetchall(self):
        rows = self._facts_by_concept.get(self._last_select_concept_id, {})
        return [(period_id, value, fact_ids) for period_id, (value, fact_ids) in rows.items()]

    def executemany(self, sql, rows):
        self._inserted.extend(rows)


class _FakeConnection:
    def __init__(self, facts_by_concept):
        self._facts_by_concept = facts_by_concept
        self.inserted = []

    def cursor(self):
        return _FakeCursor(self._facts_by_concept, self.inserted)


@pytest.mark.unit
class TestResolveFallbackForCompany:
    def test_prefers_primary_when_present(self):
        """The exact 2,168-company case that made a naive sum-mode
        widening unsafe: a company reporting BOTH the combined tag and
        the split tags must resolve to the PRIMARY value, not a sum of
        both (which would double-count)."""
        conn = _FakeConnection(
            {
                10: {1: (5000, [100])},  # primary (total_debt): period 1 = 5000
                20: {1: (2500, [101]), 2: (3000, [102])},  # fallback (total_debt_split): period 1 = 2500 (WRONG if used), period 2 = 3000
            }
        )
        count = resolve_fallback_for_company(conn, company_id=1, primary_id=10, fallback_id=20, resolved_id=30)
        assert count == 2
        by_period = {row["period_id"]: row["value"] for row in conn.inserted}
        assert by_period[1] == 5000  # primary wins, not summed with fallback's 2500
        assert by_period[2] == 3000  # only fallback has period 2, used as-is

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
