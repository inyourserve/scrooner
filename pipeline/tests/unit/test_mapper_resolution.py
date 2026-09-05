from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import resolve


class WriteCursor:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        self.conn.executed.append((" ".join(sql.split()), params))

    def executemany(self, sql, rows):
        self.conn.batches.append((" ".join(sql.split()), [dict(row) for row in rows]))


class WriteConnection:
    def __init__(self):
        self.executed = []
        self.batches = []
        self.commits = 0

    def cursor(self):
        return WriteCursor(self)

    def commit(self):
        self.commits += 1

    @property
    def inserted_rows(self):
        return [row for sql, rows in self.batches if "insert into analytics.canonical_fact" in sql for row in rows]


@pytest.mark.unit
def test_resolution_honors_tag_priority_sum_mode_and_source_lineage(monkeypatch):
    mapping_index = {
        100: {"combination_mode": "first_match", "mappings": [(1, 1), (2, 2)]},
        200: {"combination_mode": "sum", "mappings": [(3, 1), (4, 2)]},
    }
    managed_concept_ids = {100, 200}
    facts = [
        (1, 10, Decimal("10"), 101),
        (2, 10, Decimal("99"), 102),
        (2, 11, Decimal("20"), 103),
        (3, 10, Decimal("3"), 104),
        (4, 10, Decimal("4"), 105),
    ]
    monkeypatch.setattr(resolve, "_load_facts", lambda _conn, _company, _mapped: facts)
    conn = WriteConnection()

    stats = resolve.resolve_for_company(conn, 7, mapping_index, managed_concept_ids)
    rows = {(r["canonical_concept_id"], r["period_id"]): r for r in conn.inserted_rows}

    assert stats == {"resolved": 3, "unresolved_concepts": 0}
    assert rows[(100, 10)]["value"] == Decimal("10")
    assert rows[(100, 10)]["source_fact_ids"] == [101]
    assert rows[(100, 11)]["value"] == Decimal("20")
    assert rows[(200, 10)]["value"] == Decimal("7")
    assert rows[(200, 10)]["source_fact_ids"] == [104, 105]
    delete_sql, params = conn.executed[0]
    assert delete_sql == "delete from analytics.canonical_fact where company_id = %s and canonical_concept_id = any(%s)"
    assert params[0] == 7
    assert set(params[1]) == managed_concept_ids


@pytest.mark.unit
def test_delete_never_touches_a_zero_mapping_concept(monkeypatch):
    """The real 2026-09-02 bug: total_debt_resolved has zero concept_mapping
    rows by design (populated only by mapper/concept_fallback.py, never by
    resolve()) -- a resolve-facts run must never delete its rows, even
    though it appears in mapping_index with an empty mappings list (every
    canonical_concept does, mapped or not)."""
    mapping_index = {
        100: {"combination_mode": "first_match", "mappings": [(1, 1)]},
        999: {"combination_mode": "first_match", "mappings": []},  # total_debt_resolved-shaped: zero mappings
    }
    managed_concept_ids = {100}  # 999 deliberately excluded -- it has no concept_mapping rows at all
    monkeypatch.setattr(resolve, "_load_facts", lambda _conn, _company, _mapped: [(1, 10, Decimal("5"), 101)])
    conn = WriteConnection()

    resolve.resolve_for_company(conn, 7, mapping_index, managed_concept_ids)

    delete_sql, params = conn.executed[0]
    assert "canonical_concept_id = any(%s)" in delete_sql
    assert 999 not in params[1]
    assert set(params[1]) == {100}

