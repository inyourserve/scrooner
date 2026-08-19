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
    facts = [
        (1, 10, Decimal("10"), 101),
        (2, 10, Decimal("99"), 102),
        (2, 11, Decimal("20"), 103),
        (3, 10, Decimal("3"), 104),
        (4, 10, Decimal("4"), 105),
    ]
    monkeypatch.setattr(resolve, "_load_facts", lambda _conn, _company, _mapped: facts)
    conn = WriteConnection()

    stats = resolve.resolve_for_company(conn, 7, mapping_index)
    rows = {(r["canonical_concept_id"], r["period_id"]): r for r in conn.inserted_rows}

    assert stats == {"resolved": 3, "unresolved_concepts": 0}
    assert rows[(100, 10)]["value"] == Decimal("10")
    assert rows[(100, 10)]["source_fact_ids"] == [101]
    assert rows[(100, 11)]["value"] == Decimal("20")
    assert rows[(200, 10)]["value"] == Decimal("7")
    assert rows[(200, 10)]["source_fact_ids"] == [104, 105]
    delete_sql, params = conn.executed[0]
    assert delete_sql == "delete from analytics.canonical_fact where company_id = %s"
    assert params == (7,)

