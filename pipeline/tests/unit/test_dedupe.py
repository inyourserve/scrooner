from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.normalizer.dedupe import resolve_authoritative_for_company


class DedupeCursor:
    def __init__(self, conn):
        self.conn = conn
        self._rows = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split())
        if normalized.startswith("select f.id"):
            company_id = params[0]
            self._rows = list(self.conn.rows_by_company[company_id])
        elif "set is_authoritative = true" in normalized:
            for fact_id in params[0]:
                self.conn.authority[fact_id] = True
        elif "set is_authoritative = false" in normalized:
            for fact_id in params[0]:
                self.conn.authority[fact_id] = False
        else:
            raise AssertionError(f"Unexpected SQL in dedupe test: {normalized}")

    def fetchall(self):
        return self._rows


class DedupeConnection:
    def __init__(self, rows_by_company):
        self.rows_by_company = rows_by_company
        self.authority = {
            row[0]: True
            for rows in rows_by_company.values()
            for row in rows
        }
        self.commits = 0

    def cursor(self):
        return DedupeCursor(self)

    def commit(self):
        self.commits += 1


def fact_row(fact_id, concept_id, value, filing_date, filing_id):
    return (fact_id, concept_id, 1, 100, Decimal(value), filing_date, filing_id)


@pytest.mark.unit
def test_dedupe_earliest_agreement_wins_and_conflicts_remain_unresolved():
    conn = DedupeConnection(
        {
            1: [
                fact_row(1, 10, "100", date(2024, 2, 1), 101),
                fact_row(2, 10, "100", date(2024, 5, 1), 102),
                fact_row(3, 20, "200", date(2024, 2, 1), 101),
                fact_row(4, 20, "201", date(2024, 5, 1), 102),
                fact_row(5, 30, "300", date(2024, 2, 1), 101),
            ]
        }
    )

    stats = resolve_authoritative_for_company(conn, 1)

    assert stats == {
        "duplicate_groups": 2,
        "agreed_duplicate_groups": 1,
        "conflict_groups": 1,
    }
    assert conn.authority == {1: True, 2: False, 3: False, 4: False, 5: True}


@pytest.mark.unit
def test_dedupe_is_repeatable_and_scoped_to_one_company():
    conn = DedupeConnection(
        {
            1: [
                fact_row(1, 10, "100", date(2024, 2, 1), 101),
                fact_row(2, 10, "100", date(2024, 5, 1), 102),
            ],
            2: [
                fact_row(20, 10, "900", date(2024, 2, 1), 201),
                fact_row(21, 10, "901", date(2024, 5, 1), 202),
            ],
        }
    )
    company_two_before = {fact_id: conn.authority[fact_id] for fact_id in (20, 21)}

    first = resolve_authoritative_for_company(conn, 1)
    state_after_first = dict(conn.authority)
    second = resolve_authoritative_for_company(conn, 1)

    assert second == first
    assert conn.authority == state_after_first
    assert {fact_id: conn.authority[fact_id] for fact_id in (20, 21)} == company_two_before

