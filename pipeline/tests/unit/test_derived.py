from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.normalizer import derived


class CaptureCursor:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def executemany(self, sql, rows):
        self.conn.batches.append((" ".join(sql.split()), [dict(row) for row in rows]))


class CaptureConnection:
    def __init__(self):
        self.batches = []
        self.commits = 0

    def cursor(self):
        return CaptureCursor(self)

    def commit(self):
        self.commits += 1

    @property
    def fact_rows(self):
        rows = []
        for sql, batch in self.batches:
            if "insert into core.fact" in sql:
                rows.extend(batch)
        return rows


def duration_row(fact_id, value, fiscal_period, start, end, *, concept_id=10, unit_id=1, fiscal_year=2025):
    return (
        fact_id,
        concept_id,
        unit_id,
        Decimal(value),
        1000 + fact_id,
        2000 + fact_id,
        fiscal_year,
        fiscal_period,
        start,
        end,
    )


@pytest.mark.unit
def test_q4_is_derived_exactly_from_complete_discrete_quarters(monkeypatch):
    fy_start = date(2024, 9, 29)
    q1_end, q2_end, q3_end, fy_end = (
        date(2024, 12, 28),
        date(2025, 3, 29),
        date(2025, 6, 28),
        date(2025, 9, 27),
    )
    rows = [
        duration_row(1, "120", "FY", fy_start, fy_end),
        duration_row(2, "20", "Q1", fy_start, q1_end),
        duration_row(3, "25", "Q2", date(2024, 12, 29), q2_end),
        duration_row(4, "30", "Q3", date(2025, 3, 30), q3_end),
    ]
    q4_key = (date(2025, 6, 29), fy_end)
    monkeypatch.setattr(derived, "_load_quarterly_candidates", lambda _conn, _company: rows)
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404})
    monkeypatch.setattr(derived, "_load_reported_duration_keys", lambda _conn, _company: set())
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert stats == {"candidate_groups": 1, "derived": 1, "already_reported": 0, "incomplete": 0}
    assert conn.fact_rows[0]["period_id"] == 404
    assert conn.fact_rows[0]["value"] == Decimal("45")
    assert conn.fact_rows[0]["filing_id"] == 1001


@pytest.mark.unit
@pytest.mark.parametrize("case", ["reported", "incomplete"])
def test_q4_is_not_derived_over_reported_or_incomplete_data(monkeypatch, case):
    fy_start, fy_end = date(2024, 9, 29), date(2025, 9, 27)
    q1_end, q2_end, q3_end = date(2024, 12, 28), date(2025, 3, 29), date(2025, 6, 28)
    rows = [
        duration_row(1, "120", "FY", fy_start, fy_end),
        duration_row(2, "20", "Q1", fy_start, q1_end),
        duration_row(3, "25", "Q2", date(2024, 12, 29), q2_end),
    ]
    if case == "reported":
        rows.append(duration_row(4, "30", "Q3", date(2025, 3, 30), q3_end))
    q4_key = (date(2025, 6, 29), fy_end)
    reported = {(10, 1, *q4_key)} if case == "reported" else set()
    monkeypatch.setattr(derived, "_load_quarterly_candidates", lambda _conn, _company: rows)
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404})
    monkeypatch.setattr(derived, "_load_reported_duration_keys", lambda _conn, _company: reported)
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert conn.fact_rows == []
    if case == "reported":
        assert stats["already_reported"] == 1
    else:
        assert stats["incomplete"] == 1


@pytest.mark.unit
def test_q4_refuses_non_contiguous_or_non_nested_quarters(monkeypatch):
    fy_start, fy_end = date(2024, 9, 29), date(2025, 9, 27)
    rows = [
        duration_row(1, "120", "FY", fy_start, fy_end),
        duration_row(2, "20", "Q1", fy_start, date(2024, 12, 28)),
        # This gap means the labelled Q2 is not comparable to the Q1 span.
        duration_row(3, "25", "Q2", date(2025, 1, 5), date(2025, 3, 29)),
        duration_row(4, "30", "Q3", date(2025, 3, 30), date(2025, 6, 28)),
    ]
    monkeypatch.setattr(derived, "_load_quarterly_candidates", lambda _conn, _company: rows)
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _conn, _company: {})
    monkeypatch.setattr(derived, "_load_reported_duration_keys", lambda _conn, _company: set())
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert stats["derived"] == 0
    assert stats["incomplete"] == 1
    assert conn.fact_rows == []


@pytest.mark.unit
def test_cumulative_ytd_values_become_discrete_q2_and_q3(monkeypatch):
    start = date(2024, 9, 29)
    q1_end, half_end, three_q_end = date(2024, 12, 28), date(2025, 3, 29), date(2025, 6, 28)
    rows = [
        duration_row(1, "29.935", "Q1", start, q1_end),
        duration_row(2, "53.887", None, start, half_end),
        duration_row(3, "81.754", None, start, three_q_end),
    ]
    q2_key = (date(2024, 12, 29), half_end)
    q3_key = (date(2025, 3, 30), three_q_end)
    monkeypatch.setattr(derived, "_load_all_duration_facts", lambda _conn, _company: rows)
    monkeypatch.setattr(
        derived,
        "_load_existing_periods",
        lambda _conn, _company: {q2_key: 402, q3_key: 403},
    )
    monkeypatch.setattr(derived, "_load_reported_duration_keys", lambda _conn, _company: set())
    conn = CaptureConnection()

    stats = derived.derive_interim_quarters_for_company(conn, 1)
    values = {row["period_id"]: row["value"] for row in conn.fact_rows}

    assert stats["q2_derived"] == 1
    assert stats["q3_derived"] == 1
    assert values == {402: Decimal("23.952"), 403: Decimal("27.867")}


@pytest.mark.unit
def test_interim_derivation_refuses_non_nested_spans(monkeypatch):
    q1_start = date(2024, 9, 29)
    other_start = date(2024, 10, 1)
    rows = [
        duration_row(1, "20", "Q1", q1_start, date(2024, 12, 28)),
        duration_row(2, "50", None, other_start, date(2025, 3, 29)),
        duration_row(3, "80", None, date(2024, 10, 2), date(2025, 6, 28)),
    ]
    monkeypatch.setattr(derived, "_load_all_duration_facts", lambda _conn, _company: rows)
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _conn, _company: {})
    monkeypatch.setattr(derived, "_load_reported_duration_keys", lambda _conn, _company: set())
    conn = CaptureConnection()

    stats = derived.derive_interim_quarters_for_company(conn, 1)

    assert stats["q2_derived"] == 0
    assert stats["q3_derived"] == 0
    assert stats["incomplete_or_inconsistent"] == 2
    assert conn.fact_rows == []


@pytest.mark.unit
def test_interim_derivation_is_logically_repeatable(monkeypatch):
    start = date(2024, 9, 29)
    q1_end, half_end, three_q_end = date(2024, 12, 28), date(2025, 3, 29), date(2025, 6, 28)
    rows = [
        duration_row(1, "20", "Q1", start, q1_end),
        duration_row(2, "50", None, start, half_end),
        duration_row(3, "90", None, start, three_q_end),
    ]
    period_lookup = {
        (date(2024, 12, 29), half_end): 402,
        (date(2025, 3, 30), three_q_end): 403,
    }
    monkeypatch.setattr(derived, "_load_all_duration_facts", lambda _conn, _company: rows)
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _conn, _company: period_lookup)
    monkeypatch.setattr(derived, "_load_reported_duration_keys", lambda _conn, _company: set())

    first, second = CaptureConnection(), CaptureConnection()
    first_stats = derived.derive_interim_quarters_for_company(first, 1)
    second_stats = derived.derive_interim_quarters_for_company(second, 1)

    assert second_stats == first_stats
    assert second.fact_rows == first.fact_rows
