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

    def execute(self, sql, params=None):
        self.conn.statements.append((" ".join(sql.split()), params))


class CaptureConnection:
    def __init__(self):
        self.batches = []
        self.statements = []
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


@pytest.fixture(autouse=True)
def _no_nine_month_ytd_by_default(monkeypatch):
    """Existing chain tests have no 9-month YTD facts; the fallback tests below override this."""
    monkeypatch.setattr(derived, "_load_nine_month_ytd", lambda _conn, _company: {})
    monkeypatch.setattr(derived, "_load_authoritative_reported_quarters", lambda _conn, _company: {})


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

    assert stats == {"candidate_groups": 1, "derived": 1, "derived_from_ytd": 0, "already_reported": 0, "replaced_full_year_q4": 0, "incomplete": 0}
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


def _ytd_setup(monkeypatch, rows, ytd, q4_key):
    monkeypatch.setattr(derived, "_load_quarterly_candidates", lambda _conn, _company: rows)
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404})
    monkeypatch.setattr(derived, "_load_reported_duration_keys", lambda _conn, _company: set())
    monkeypatch.setattr(derived, "_load_nine_month_ytd", lambda _conn, _company: ytd)


@pytest.mark.unit
def test_q4_falls_back_to_fy_minus_nine_month_ytd(monkeypatch):
    # IMA/FCCN shape: FY + discrete Q3 + a 9-month YTD from the Q3 10-Q,
    # but no Q1/Q2 -- the chain can't run, FY - YTD can.
    fy_start, q3_end, fy_end = date(2025, 1, 1), date(2025, 9, 30), date(2025, 12, 31)
    rows = [
        duration_row(1, "-45349", "FY", fy_start, fy_end),
        duration_row(2, "-24779", "Q3", date(2025, 7, 1), q3_end),
    ]
    q4_key = (date(2025, 10, 1), fy_end)
    _ytd_setup(monkeypatch, rows, {(10, 1, fy_start): [(q3_end, Decimal("-38441"))]}, q4_key)
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert stats["derived"] == 1 and stats["derived_from_ytd"] == 1
    assert conn.fact_rows[0]["value"] == Decimal("-6908")
    assert conn.fact_rows[0]["period_id"] == 404


@pytest.mark.unit
def test_complete_chain_wins_over_ytd(monkeypatch):
    fy_start, fy_end = date(2024, 9, 29), date(2025, 9, 27)
    rows = [
        duration_row(1, "120", "FY", fy_start, fy_end),
        duration_row(2, "20", "Q1", fy_start, date(2024, 12, 28)),
        duration_row(3, "25", "Q2", date(2024, 12, 29), date(2025, 3, 29)),
        duration_row(4, "30", "Q3", date(2025, 3, 30), date(2025, 6, 28)),
    ]
    q4_key = (date(2025, 6, 29), fy_end)
    _ytd_setup(monkeypatch, rows, {(10, 1, fy_start): [(date(2025, 6, 28), Decimal("99"))]}, q4_key)
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert stats["derived_from_ytd"] == 0
    assert conn.fact_rows[0]["value"] == Decimal("45")


@pytest.mark.unit
@pytest.mark.parametrize(
    "ytd",
    [
        # YTD starts on a different date than the fiscal year
        {(10, 1, date(2025, 2, 1)): [(date(2025, 9, 30), Decimal("-38441"))]},
        # remainder is not quarter-length (YTD ends a month early)
        {(10, 1, date(2025, 1, 1)): [(date(2025, 8, 31), Decimal("-38441"))]},
        # two authoritative YTD values disagree
        {(10, 1, date(2025, 1, 1)): [(date(2025, 9, 30), Decimal("-38441")), (date(2025, 9, 30), Decimal("-38000"))]},
    ],
    ids=["wrong_start", "not_quarter_length", "disagreeing_values"],
)
def test_ytd_fallback_refuses_unsafe_inputs(monkeypatch, ytd):
    fy_start, fy_end = date(2025, 1, 1), date(2025, 12, 31)
    rows = [duration_row(1, "-45349", "FY", fy_start, fy_end)]
    _ytd_setup(monkeypatch, rows, ytd, (date(2025, 10, 1), fy_end))
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert stats["derived"] == 0 and stats["incomplete"] == 1
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
def test_q2_derives_when_q1_has_an_unusual_unlabeled_duration(monkeypatch):
    """Real bug, found live 2026-10-03 tracing Albertsons' FY2026 Q2 cfo
    gap: its real first quarter spans 111 days (a 52/53-week-calendar
    grocery retailer's irregular Q1), outside periods.py's normal
    80-100-day quarter band, so it's stored with fiscal_period=None --
    exactly like the HALF/THREE_Q buckets already handle. The original
    code only ever looked for an EXPLICITLY 'Q1'-labeled fact, so Q2
    (and every later quarter for that fiscal year, since Q3 needs HALF
    which is fine, but any company whose Q1 is unlabeled this way never
    gets a Q2) silently never derived -- correct, present HALF data sat
    unused. Must derive from structural nesting (same start as HALF,
    ends before it), not require the label."""
    start = date(2025, 2, 23)
    q1_end = date(2025, 6, 14)  # 111 days -- outside the normal quarter band
    half_end = date(2025, 9, 6)
    rows = [
        duration_row(1, "754400000", None, start, q1_end),
        duration_row(2, "1282000000", None, start, half_end),
    ]
    q2_key = (date(2025, 6, 15), half_end)
    monkeypatch.setattr(derived, "_load_all_duration_facts", lambda _conn, _company: rows)
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _conn, _company: {q2_key: 402})
    monkeypatch.setattr(derived, "_load_reported_duration_keys", lambda _conn, _company: set())
    conn = CaptureConnection()

    stats = derived.derive_interim_quarters_for_company(conn, 1)
    values = {row["period_id"]: row["value"] for row in conn.fact_rows}

    assert stats["q2_derived"] == 1
    assert values == {402: Decimal("527600000")}


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


@pytest.mark.unit
@pytest.mark.parametrize(("reported_value", "replaced"), [("120", True), ("75", False)])
def test_reported_q4_carrying_the_full_year_value_is_replaced(monkeypatch, reported_value, replaced):
    # NiSource-shaped: the 10-K tags the FY total with a Q4 context.
    fy_start, fy_end = date(2025, 1, 1), date(2025, 12, 31)
    rows = [
        duration_row(1, "120", "FY", fy_start, fy_end),
        duration_row(2, "20", "Q1", fy_start, date(2025, 3, 31)),
        duration_row(3, "25", "Q2", date(2025, 4, 1), date(2025, 6, 30)),
        duration_row(4, "30", "Q3", date(2025, 7, 1), date(2025, 9, 30)),
    ]
    q4_key = (date(2025, 10, 1), fy_end)
    monkeypatch.setattr(derived, "_load_quarterly_candidates", lambda _conn, _company: rows)
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404})
    monkeypatch.setattr(derived, "_load_reported_duration_keys", lambda _conn, _company: {(10, 1, *q4_key)})
    monkeypatch.setattr(
        derived,
        "_load_authoritative_reported_quarters",
        lambda _conn, _company: {(10, 1, *q4_key): [(99, Decimal(reported_value))]},
    )
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    if replaced:
        assert stats["replaced_full_year_q4"] == 1 and stats["already_reported"] == 0
        assert conn.statements[0][1] == ([99],)
        assert conn.fact_rows[0]["value"] == Decimal("45")
    else:
        assert stats["already_reported"] == 1
        assert conn.statements == [] and conn.fact_rows == []


@pytest.mark.unit
def test_full_year_q4_is_kept_when_first_three_quarters_are_zero():
    assert derived._mistagged_full_year_q4([(1, Decimal("5"))], Decimal("5"), Decimal("0")) == []
