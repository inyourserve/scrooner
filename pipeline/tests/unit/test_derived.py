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
        text = " ".join(sql.split())
        if text.lower().startswith("set local statement_timeout"):
            # Session setting, not a data statement: kept apart so the
            # statement-index assertions below see only reads and writes.
            self.conn.settings.append(text)
            return
        self.conn.statements.append((text, params))


class CaptureConnection:
    def __init__(self):
        self.batches = []
        self.statements = []
        self.settings = []
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


def duration_row(
    fact_id,
    value,
    fiscal_period,
    start,
    end,
    *,
    concept_id=10,
    unit_id=1,
    fiscal_year=2025,
):
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
    monkeypatch.setattr(
        derived, "_load_authoritative_reported_quarters", lambda _conn, _company: {}
    )
    monkeypatch.setattr(derived, "_load_average_concept_ids", lambda _conn: set())
    monkeypatch.setattr(derived, "_load_non_additive", lambda _conn: (set(), set()))


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
    monkeypatch.setattr(
        derived, "_load_quarterly_candidates", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404}
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert stats == {
        "candidate_groups": 1,
        "derived": 1,
        "derived_from_ytd": 0,
        "already_reported": 0,
        "replaced_full_year_q4": 0,
        "incomplete": 0,
        "non_additive_not_derived": 0,
        "demoted_full_year_q4_not_replaced": 0,
    }
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
    monkeypatch.setattr(
        derived, "_load_quarterly_candidates", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404}
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: reported
    )
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
    monkeypatch.setattr(
        derived, "_load_quarterly_candidates", lambda _conn, _company: rows
    )
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _conn, _company: {})
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert stats["derived"] == 0
    assert stats["incomplete"] == 1
    assert conn.fact_rows == []


def _ytd_setup(monkeypatch, rows, ytd, q4_key):
    monkeypatch.setattr(
        derived, "_load_quarterly_candidates", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404}
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
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
    _ytd_setup(
        monkeypatch, rows, {(10, 1, fy_start): [(q3_end, Decimal("-38441"))]}, q4_key
    )
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
    _ytd_setup(
        monkeypatch,
        rows,
        {(10, 1, fy_start): [(date(2025, 6, 28), Decimal("99"))]},
        q4_key,
    )
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
        {
            (10, 1, date(2025, 1, 1)): [
                (date(2025, 9, 30), Decimal("-38441")),
                (date(2025, 9, 30), Decimal("-38000")),
            ]
        },
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
    q1_end, half_end, three_q_end = (
        date(2024, 12, 28),
        date(2025, 3, 29),
        date(2025, 6, 28),
    )
    rows = [
        duration_row(1, "29.935", "Q1", start, q1_end),
        duration_row(2, "53.887", None, start, half_end),
        duration_row(3, "81.754", None, start, three_q_end),
    ]
    q2_key = (date(2024, 12, 29), half_end)
    q3_key = (date(2025, 3, 30), three_q_end)
    monkeypatch.setattr(
        derived, "_load_all_duration_facts", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived,
        "_load_existing_periods",
        lambda _conn, _company: {q2_key: 402, q3_key: 403},
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
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
    monkeypatch.setattr(
        derived, "_load_all_duration_facts", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _conn, _company: {q2_key: 402}
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
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
    monkeypatch.setattr(
        derived, "_load_all_duration_facts", lambda _conn, _company: rows
    )
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _conn, _company: {})
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
    conn = CaptureConnection()

    stats = derived.derive_interim_quarters_for_company(conn, 1)

    assert stats["q2_derived"] == 0
    assert stats["q3_derived"] == 0
    assert stats["incomplete_or_inconsistent"] == 2
    assert conn.fact_rows == []


@pytest.mark.unit
def test_interim_derivation_is_logically_repeatable(monkeypatch):
    start = date(2024, 9, 29)
    q1_end, half_end, three_q_end = (
        date(2024, 12, 28),
        date(2025, 3, 29),
        date(2025, 6, 28),
    )
    rows = [
        duration_row(1, "20", "Q1", start, q1_end),
        duration_row(2, "50", None, start, half_end),
        duration_row(3, "90", None, start, three_q_end),
    ]
    period_lookup = {
        (date(2024, 12, 29), half_end): 402,
        (date(2025, 3, 30), three_q_end): 403,
    }
    monkeypatch.setattr(
        derived, "_load_all_duration_facts", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _conn, _company: period_lookup
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )

    first, second = CaptureConnection(), CaptureConnection()
    first_stats = derived.derive_interim_quarters_for_company(first, 1)
    second_stats = derived.derive_interim_quarters_for_company(second, 1)

    assert second_stats == first_stats
    assert second.fact_rows == first.fact_rows


@pytest.mark.unit
@pytest.mark.parametrize(("reported_value", "replaced"), [("120", True), ("75", False)])
def test_reported_q4_carrying_the_full_year_value_is_replaced(
    monkeypatch, reported_value, replaced
):
    # NiSource-shaped: the 10-K tags the FY total with a Q4 context.
    fy_start, fy_end = date(2025, 1, 1), date(2025, 12, 31)
    rows = [
        duration_row(1, "120", "FY", fy_start, fy_end),
        duration_row(2, "20", "Q1", fy_start, date(2025, 3, 31)),
        duration_row(3, "25", "Q2", date(2025, 4, 1), date(2025, 6, 30)),
        duration_row(4, "30", "Q3", date(2025, 7, 1), date(2025, 9, 30)),
    ]
    q4_key = (date(2025, 10, 1), fy_end)
    monkeypatch.setattr(
        derived, "_load_quarterly_candidates", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404}
    )
    monkeypatch.setattr(
        derived,
        "_load_reported_duration_keys",
        lambda _conn, _company: {(10, 1, *q4_key)},
    )
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
    assert (
        derived._mistagged_full_year_q4([(1, Decimal("5"))], Decimal("5"), Decimal("0"))
        == []
    )


@pytest.mark.unit
def test_weighted_average_q4_uses_window_weights_not_subtraction(monkeypatch):
    # Live 2026-10-17: FY - (Q1+Q2+Q3) gave -30.15B for Apple's Q4 diluted
    # shares. Annual average is the mean of the quarterly averages, so
    # Q4 = 4*FY - (Q1+Q2+Q3); validated against yfinance (median error 0.024%).
    fy_start = date(2024, 9, 29)
    q1_end, q2_end, q3_end, fy_end = (
        date(2024, 12, 28),
        date(2025, 3, 29),
        date(2025, 6, 28),
        date(2025, 9, 27),
    )
    avg, flow = 77, 10
    rows = [
        # Apple FY2025 diluted weighted-average shares (thousands)
        duration_row(1, "15004697", "FY", fy_start, fy_end, concept_id=avg),
        duration_row(2, "15150865", "Q1", fy_start, q1_end, concept_id=avg),
        duration_row(3, "15056133", "Q2", date(2024, 12, 29), q2_end, concept_id=avg),
        duration_row(4, "14948179", "Q3", date(2025, 3, 30), q3_end, concept_id=avg),
        duration_row(5, "120", "FY", fy_start, fy_end, concept_id=flow),
        duration_row(6, "20", "Q1", fy_start, q1_end, concept_id=flow),
        duration_row(7, "25", "Q2", date(2024, 12, 29), q2_end, concept_id=flow),
        duration_row(8, "30", "Q3", date(2025, 3, 30), q3_end, concept_id=flow),
    ]
    q4_key = (date(2025, 6, 29), fy_end)
    monkeypatch.setattr(
        derived, "_load_quarterly_candidates", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404}
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
    monkeypatch.setattr(derived, "_load_average_concept_ids", lambda _conn: {avg})
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    values = {r["concept_id"]: r["value"] for r in conn.fact_rows}
    assert stats["derived"] == 2
    assert values[avg] == Decimal("14863611"), "4*FY - (Q1+Q2+Q3)"
    assert values[flow] == Decimal("45"), "additive flows keep FY - (Q1+Q2+Q3)"


@pytest.mark.unit
def test_weighted_average_q4_from_nine_month_ytd_uses_three_times_ytd(monkeypatch):
    fy_start = date(2024, 9, 29)
    fy_end, ytd_end = date(2025, 9, 27), date(2025, 6, 28)
    avg = 77
    rows = [duration_row(1, "100", "FY", fy_start, fy_end, concept_id=avg)]
    q4_key = (date(2025, 6, 29), fy_end)
    monkeypatch.setattr(
        derived, "_load_quarterly_candidates", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived,
        "_load_nine_month_ytd",
        lambda _conn, _company: {(avg, 1, fy_start): [(ytd_end, Decimal("102"))]},
    )
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404}
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
    monkeypatch.setattr(derived, "_load_average_concept_ids", lambda _conn: {avg})
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert stats["derived_from_ytd"] == 1
    assert conn.fact_rows[0]["value"] == Decimal("94"), "4*100 - 3*102"


@pytest.mark.unit
def test_weighted_average_q4_is_not_stored_when_result_is_non_positive(monkeypatch):
    fy_start = date(2024, 9, 29)
    q1_end, q2_end, q3_end, fy_end = (
        date(2024, 12, 28),
        date(2025, 3, 29),
        date(2025, 6, 28),
        date(2025, 9, 27),
    )
    avg = 77
    # quarters far above the annual average -> 4*100 - 3*200 < 0: inconsistent inputs
    rows = [
        duration_row(1, "100", "FY", fy_start, fy_end, concept_id=avg),
        duration_row(2, "200", "Q1", fy_start, q1_end, concept_id=avg),
        duration_row(3, "200", "Q2", date(2024, 12, 29), q2_end, concept_id=avg),
        duration_row(4, "200", "Q3", date(2025, 3, 30), q3_end, concept_id=avg),
    ]
    monkeypatch.setattr(
        derived, "_load_quarterly_candidates", lambda _conn, _company: rows
    )
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _conn, _company: {})
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
    monkeypatch.setattr(derived, "_load_average_concept_ids", lambda _conn: {avg})
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert stats["derived"] == 0 and stats["incomplete"] == 1
    assert conn.fact_rows == []


@pytest.mark.unit
def test_weighted_average_interim_quarters_use_window_weights(monkeypatch):
    start = date(2024, 9, 29)
    q1_end, half_end, three_q_end = (
        date(2024, 12, 28),
        date(2025, 3, 29),
        date(2025, 6, 28),
    )
    avg = 77
    rows = [
        duration_row(1, "100", "Q1", start, q1_end, concept_id=avg),
        duration_row(2, "98", None, start, half_end, concept_id=avg),  # H1 average
        duration_row(3, "97", None, start, three_q_end, concept_id=avg),  # 9M average
    ]
    q2_key = (date(2024, 12, 29), half_end)
    q3_key = (date(2025, 3, 30), three_q_end)
    monkeypatch.setattr(
        derived, "_load_all_duration_facts", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived,
        "_load_existing_periods",
        lambda _conn, _company: {q2_key: 402, q3_key: 403},
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
    monkeypatch.setattr(derived, "_load_average_concept_ids", lambda _conn: {avg})
    conn = CaptureConnection()

    stats = derived.derive_interim_quarters_for_company(conn, 1)
    values = {r["period_id"]: r["value"] for r in conn.fact_rows}

    assert stats["q2_derived"] == 1 and stats["q3_derived"] == 1
    assert values == {402: Decimal("96"), 403: Decimal("95")}, "2*98-100 and 3*97-2*98"


@pytest.mark.unit
def test_stale_derived_share_row_is_retired_when_the_method_declines(monkeypatch):
    # After the rollout 2,203 old negative derived share rows remained: the new
    # method correctly refuses to store a non-positive average, but nothing
    # retired the previous FY - sum(quarters) row, still authoritative.
    fy_start = date(2024, 9, 29)
    q1_end, q2_end, q3_end, fy_end = (
        date(2024, 12, 28),
        date(2025, 3, 29),
        date(2025, 6, 28),
        date(2025, 9, 27),
    )
    avg = 77
    rows = [
        duration_row(1, "100", "FY", fy_start, fy_end, concept_id=avg),
        duration_row(2, "200", "Q1", fy_start, q1_end, concept_id=avg),
        duration_row(3, "200", "Q2", date(2024, 12, 29), q2_end, concept_id=avg),
        duration_row(4, "200", "Q3", date(2025, 3, 30), q3_end, concept_id=avg),
    ]
    q4_key = (date(2025, 6, 29), fy_end)
    monkeypatch.setattr(
        derived, "_load_quarterly_candidates", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404}
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
    monkeypatch.setattr(derived, "_load_average_concept_ids", lambda _conn: {avg})
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 7)

    assert stats["derived"] == 0 and stats["incomplete"] == 1
    retire = [b for b in conn.batches if "set is_authoritative = false" in b[0]]
    assert len(retire) == 1
    assert "and is_derived and is_authoritative" in retire[0][0], (
        "only derived rows may be touched"
    )
    assert conn.fact_rows == []


# --- Per-share values and ratios are never derived (fix register item 12) ---
# Real cases, FILING-CHECKED in data-team/35 and top1000 status.md. Input
# values are the stored core.fact values (fact ids in each comment); the
# expected outcome is "no derived row", whatever the arithmetic would give.

_REAL_LOAD_NON_ADDITIVE = (
    derived._load_non_additive
)  # captured before the autouse fixture patches it
EPS_UNIT, USD_UNIT, PURE_UNIT = 13, 16, 24  # core.unit ids: usd/shares, usd, pure
EPS_DILUTED, DPS_DECLARED, REVENUE, TAX_RATE, EPS_USD_TAG = 101, 102, 103, 104, 105


def _non_additive(
    monkeypatch,
    *,
    units=(EPS_UNIT, PURE_UNIT),
    concepts=(EPS_DILUTED, DPS_DECLARED, EPS_USD_TAG),
):
    monkeypatch.setattr(
        derived, "_load_non_additive", lambda _conn: (set(units), set(concepts))
    )


def _q4_ytd_case(monkeypatch, fy_start, ytd_end, fy_end, cells):
    """cells: [(concept_id, unit_id, fy_value, ytd_value)] -> runs derive_q4."""
    rows = [
        duration_row(i + 1, fy_value, "FY", fy_start, fy_end, concept_id=c, unit_id=u)
        for i, (c, u, fy_value, _ytd) in enumerate(cells)
    ]
    ytd = {(c, u, fy_start): [(ytd_end, Decimal(y))] for c, u, _fy, y in cells}
    q4_key = (ytd_end + (date(2000, 1, 2) - date(2000, 1, 1)), fy_end)
    _ytd_setup(monkeypatch, rows, ytd, q4_key)
    conn = CaptureConnection()
    return derived.derive_q4_for_company(conn, 1), conn


@pytest.mark.unit
def test_v_quarterly_dividend_on_full_year_context_is_not_derived(monkeypatch):
    # V FY2025: the 10-K tags the $0.59 QUARTERLY dividend with the full-year
    # context (0001403161-25-000089 R8); the 9M YTD is 1.77. Old behaviour
    # stored Q4 DPS = 0.59 - 1.77 = -1.18 (yield 0.19% vs ~0.63%).
    _non_additive(monkeypatch)
    stats, conn = _q4_ytd_case(
        monkeypatch,
        date(2024, 10, 1),
        date(2025, 6, 30),
        date(2025, 9, 30),
        [(DPS_DECLARED, EPS_UNIT, "0.59", "1.77")],
    )
    assert conn.fact_rows == []
    assert stats["derived"] == 0 and stats["non_additive_not_derived"] == 1


@pytest.mark.unit
def test_additive_flow_in_same_company_is_still_derived(monkeypatch):
    # The guard is per (concept, unit): revenue next to a blocked EPS cell keeps FY - 9M.
    _non_additive(monkeypatch)
    stats, conn = _q4_ytd_case(
        monkeypatch,
        date(2025, 1, 1),
        date(2025, 9, 30),
        date(2025, 12, 31),
        [(REVENUE, USD_UNIT, "1000", "700"), (DPS_DECLARED, EPS_UNIT, "0.59", "1.77")],
    )
    assert [(r["concept_id"], r["value"]) for r in conn.fact_rows] == [
        (REVENUE, Decimal("300"))
    ]
    assert stats["derived"] == 1 and stats["non_additive_not_derived"] == 1


@pytest.mark.unit
@pytest.mark.parametrize(
    ("concept_id", "unit_id"),
    [(TAX_RATE, PURE_UNIT), (EPS_USD_TAG, USD_UNIT)],
    ids=["pure_ratio_unit", "per_share_tag_filed_in_usd"],
)
def test_ratio_unit_and_per_share_tag_each_block_derivation(
    monkeypatch, concept_id, unit_id
):
    _non_additive(monkeypatch)
    stats, conn = _q4_ytd_case(
        monkeypatch,
        date(2025, 1, 1),
        date(2025, 9, 30),
        date(2025, 12, 31),
        [(concept_id, unit_id, "0.21", "0.20")],
    )
    assert conn.fact_rows == [] and stats["non_additive_not_derived"] == 1


@pytest.mark.unit
def test_per_share_blocked_on_quarter_chain_too_and_full_year_q4_is_demoted_not_replaced(
    monkeypatch,
):
    # Chain path (FY - Q1 - Q2 - Q3), plus a filed "Q4" that is really the
    # full-year EPS (UP/RTB pattern, ledger 2026-10-18): it is demoted as
    # before, but no derived EPS replaces it.
    _non_additive(monkeypatch)
    fy_start, fy_end = date(2025, 1, 1), date(2025, 12, 31)
    rows = [
        duration_row(
            1, "4.00", "FY", fy_start, fy_end, concept_id=EPS_DILUTED, unit_id=EPS_UNIT
        ),
        duration_row(
            2,
            "0.90",
            "Q1",
            fy_start,
            date(2025, 3, 31),
            concept_id=EPS_DILUTED,
            unit_id=EPS_UNIT,
        ),
        duration_row(
            3,
            "1.00",
            "Q2",
            date(2025, 4, 1),
            date(2025, 6, 30),
            concept_id=EPS_DILUTED,
            unit_id=EPS_UNIT,
        ),
        duration_row(
            4,
            "1.05",
            "Q3",
            date(2025, 7, 1),
            date(2025, 9, 30),
            concept_id=EPS_DILUTED,
            unit_id=EPS_UNIT,
        ),
    ]
    q4_key = (date(2025, 10, 1), fy_end)
    cell = (EPS_DILUTED, EPS_UNIT, *q4_key)
    monkeypatch.setattr(
        derived, "_load_quarterly_candidates", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404}
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: {cell}
    )
    monkeypatch.setattr(
        derived,
        "_load_authoritative_reported_quarters",
        lambda _conn, _company: {cell: [(99, Decimal("4.00"))]},
    )
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert conn.fact_rows == []
    assert (
        stats["demoted_full_year_q4_not_replaced"] == 1
        and stats["replaced_full_year_q4"] == 0
    )
    assert conn.statements[-1][1] == ([99],)


@pytest.mark.unit
def test_filed_discrete_q4_per_share_is_left_alone(monkeypatch):
    # A 10-K quarterly table can file Q4 EPS itself: it stays authoritative.
    _non_additive(monkeypatch)
    fy_start, fy_end = date(2025, 1, 1), date(2025, 12, 31)
    rows = [
        duration_row(
            1, "4.00", "FY", fy_start, fy_end, concept_id=EPS_DILUTED, unit_id=EPS_UNIT
        )
    ]
    q4_key = (date(2025, 10, 1), fy_end)
    cell = (EPS_DILUTED, EPS_UNIT, *q4_key)
    _ytd_setup(
        monkeypatch,
        rows,
        {(EPS_DILUTED, EPS_UNIT, fy_start): [(date(2025, 9, 30), Decimal("2.95"))]},
        q4_key,
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: {cell}
    )
    monkeypatch.setattr(
        derived,
        "_load_authoritative_reported_quarters",
        lambda _conn, _company: {cell: [(99, Decimal("1.06"))]},
    )
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert conn.fact_rows == [] and conn.statements == [] and conn.batches == []
    assert stats["non_additive_not_derived"] == 1


@pytest.mark.unit
def test_interim_q2_q3_per_share_not_derived_but_flows_are(monkeypatch):
    _non_additive(monkeypatch)
    start = date(2024, 9, 29)
    q1_end, half_end, three_q_end = (
        date(2024, 12, 28),
        date(2025, 3, 29),
        date(2025, 6, 28),
    )
    rows = [
        duration_row(
            1, "2.40", "Q1", start, q1_end, concept_id=EPS_DILUTED, unit_id=EPS_UNIT
        ),
        duration_row(
            2, "4.05", None, start, half_end, concept_id=EPS_DILUTED, unit_id=EPS_UNIT
        ),
        duration_row(
            3,
            "5.62",
            None,
            start,
            three_q_end,
            concept_id=EPS_DILUTED,
            unit_id=EPS_UNIT,
        ),
        duration_row(
            4, "29.935", "Q1", start, q1_end, concept_id=REVENUE, unit_id=USD_UNIT
        ),
        duration_row(
            5, "53.887", None, start, half_end, concept_id=REVENUE, unit_id=USD_UNIT
        ),
        duration_row(
            6, "81.754", None, start, three_q_end, concept_id=REVENUE, unit_id=USD_UNIT
        ),
    ]
    q2_key, q3_key = (date(2024, 12, 29), half_end), (date(2025, 3, 30), three_q_end)
    monkeypatch.setattr(
        derived, "_load_all_duration_facts", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived,
        "_load_existing_periods",
        lambda _conn, _company: {q2_key: 402, q3_key: 403},
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )
    conn = CaptureConnection()

    stats = derived.derive_interim_quarters_for_company(conn, 1)

    assert {r["concept_id"] for r in conn.fact_rows} == {REVENUE}
    assert stats["non_additive_not_derived"] == 1
    assert stats["q2_derived"] == 1 and stats["q3_derived"] == 1


@pytest.mark.unit
@pytest.mark.parametrize(
    ("unit", "expected"),
    [
        ("usd/shares", True),
        ("USD/shares", True),
        ("cad/shares", True),
        ("usd/bbl", True),
        ("cad/usd", True),
        ("pure", True),
        ("usd", False),
        ("shares", False),
        ("eur", False),
    ],
)
def test_is_ratio_unit(unit, expected):
    assert derived.is_ratio_unit(unit) is expected


@pytest.mark.unit
@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        ("EarningsPerShareDiluted", True),
        ("EarningsPerShareBasicAndDiluted", True),
        (
            "IncomeLossFromContinuingOperationsPerBasicShare",
            True,
        ),  # ANDE FY2025 face EPS
        ("IncomeLossFromContinuingOperationsPerDilutedShare", True),
        ("NetIncomeLossNetOfTaxPerOutstandingLimitedPartnershipUnitDiluted", True),
        ("CommonStockDividendsPerShareDeclared", True),
        ("CommonStockDividendsPerShareCashPaid", True),
        ("DistributionMadeToLimitedPartnerDistributionsPaidPerUnit", True),
        ("Revenues", False),
        ("NetIncomeLoss", False),
        (
            "WeightedAverageNumberOfDilutedSharesOutstanding",
            False,
        ),  # own window-weight method
        ("PaymentsOfDividendsCommonStock", False),
        ("StockRepurchasedDuringPeriodShares", False),
    ],
)
def test_is_per_share_tag(tag, expected):
    assert derived.is_per_share_tag(tag) is expected


class _RowsCursor(CaptureCursor):
    def __init__(self, conn):
        super().__init__(conn)
        self._rows = []

    def execute(self, sql, params=None):
        super().execute(sql, params)
        self._rows = self.conn.results.pop(0)

    def fetchall(self):
        return self._rows


@pytest.mark.unit
def test_load_non_additive_classifies_units_in_python_and_tags_by_regex():
    conn = CaptureConnection()
    conn.results = [
        [
            (13, "usd/shares"),
            (16, "usd"),
            (24, "pure"),
            (27, "shares"),
            (521, "usd/bbl"),
        ],
        [(101,), (102,)],
    ]
    conn.cursor = lambda: _RowsCursor(conn)

    units, concepts = _REAL_LOAD_NON_ADDITIVE(conn)

    assert units == {13, 24, 521} and concepts == {101, 102}
    assert conn.statements[1][1] == (derived.PER_SHARE_TAG_REGEX,)


@pytest.mark.unit
def test_per_share_cell_without_inputs_counts_as_policy_block_not_incomplete(
    monkeypatch,
):
    # The reason shown for a blank Q4 EPS is the policy, never "inputs missing".
    _non_additive(monkeypatch)
    fy_start, fy_end = date(2025, 1, 1), date(2025, 12, 31)
    rows = [
        duration_row(
            1, "4.00", "FY", fy_start, fy_end, concept_id=EPS_DILUTED, unit_id=EPS_UNIT
        )
    ]
    _ytd_setup(monkeypatch, rows, {}, (date(2025, 10, 1), fy_end))
    conn = CaptureConnection()

    stats = derived.derive_q4_for_company(conn, 1)

    assert stats["non_additive_not_derived"] == 1 and stats["incomplete"] == 0
    assert conn.fact_rows == []


# Real stored inputs (core.fact ids) behind derived rows found by the
# 2026-10-21 census; every one produced a wrong authoritative derived value.
REAL_PER_SHARE_CASES = [
    # MSFT FY26 diluted EPS: 17.95 - (3.72+5.16+4.27) = 4.80, filed 4.81 (8-K 0001193125-26-323632 Ex. 99.1); derived 341935
    (
        "MSFT_eps",
        EPS_DILUTED,
        "17.95",
        ("3.72", "5.16", "4.27"),
        (
            date(2025, 7, 1),
            date(2025, 9, 30),
            date(2025, 12, 31),
            date(2026, 3, 31),
            date(2026, 6, 30),
        ),
        "4.80",
    ),
    # AAPL FY25 diluted EPS: 7.46 - (2.40+1.65+1.57) = 1.84, filed 1.85 (8-K 0000320193-25-000077 Ex. 99.1); derived 341384
    (
        "AAPL_eps",
        EPS_DILUTED,
        "7.46",
        ("2.4", "1.65", "1.57"),
        (
            date(2024, 9, 29),
            date(2024, 12, 28),
            date(2025, 3, 29),
            date(2025, 6, 28),
            date(2025, 9, 27),
        ),
        "1.84",
    ),
    # KLAC FY26: post-split FY EPS 3.66 minus pre-split quarters = -22.61, filed 1.04 (8-K 0000319201-26-000024); derived 77564004
    (
        "KLAC_eps_split_mix",
        EPS_DILUTED,
        "3.66",
        ("8.47", "8.68", "9.12"),
        (
            date(2025, 7, 1),
            date(2025, 9, 30),
            date(2025, 12, 31),
            date(2026, 3, 31),
            date(2026, 6, 30),
        ),
        "-22.61",
    ),
    # KLAC FY26 DPS: 0.8 - 3 x 1.9 = -4.9 (same split mix); derived 77563969
    (
        "KLAC_dps_split_mix",
        DPS_DECLARED,
        "0.8",
        ("1.9", "1.9", "1.9"),
        (
            date(2025, 7, 1),
            date(2025, 9, 30),
            date(2025, 12, 31),
            date(2026, 3, 31),
            date(2026, 6, 30),
        ),
        "-4.9",
    ),
    # V FY25 DPS: quarterly 0.59 on the FY context (0001403161-25-000089 R8) -> -1.18; derived 78616210
    (
        "V_dps_fy_context",
        DPS_DECLARED,
        "0.59",
        ("0.59", "0.59", "0.59"),
        (
            date(2024, 10, 1),
            date(2024, 12, 31),
            date(2025, 3, 31),
            date(2025, 6, 30),
            date(2025, 9, 30),
        ),
        "-1.18",
    ),
    # LEA FY25 DPS: quarterly 0.77 on the FY context (0000842162-26-000011) -> -1.54; derived 77999241
    (
        "LEA_dps_fy_context",
        DPS_DECLARED,
        "0.77",
        ("0.77", "0.77", "0.77"),
        (
            date(2025, 1, 1),
            date(2025, 3, 29),
            date(2025, 6, 28),
            date(2025, 9, 27),
            date(2025, 12, 31),
        ),
        "-1.54",
    ),
]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("case", "concept_id", "fy", "quarters", "ends", "old_value"),
    REAL_PER_SHARE_CASES,
    ids=[c[0] for c in REAL_PER_SHARE_CASES],
)
def test_real_per_share_cases_are_not_derived(
    monkeypatch, case, concept_id, fy, quarters, ends, old_value
):
    fy_start, q1_end, q2_end, q3_end, fy_end = ends
    one = date(2000, 1, 2) - date(2000, 1, 1)
    rows = [
        duration_row(
            1, fy, "FY", fy_start, fy_end, concept_id=concept_id, unit_id=EPS_UNIT
        ),
        duration_row(
            2,
            quarters[0],
            "Q1",
            fy_start,
            q1_end,
            concept_id=concept_id,
            unit_id=EPS_UNIT,
        ),
        duration_row(
            3,
            quarters[1],
            "Q2",
            q1_end + one,
            q2_end,
            concept_id=concept_id,
            unit_id=EPS_UNIT,
        ),
        duration_row(
            4,
            quarters[2],
            "Q3",
            q2_end + one,
            q3_end,
            concept_id=concept_id,
            unit_id=EPS_UNIT,
        ),
    ]
    q4_key = (q3_end + one, fy_end)
    monkeypatch.setattr(
        derived, "_load_quarterly_candidates", lambda _conn, _company: rows
    )
    monkeypatch.setattr(
        derived, "_load_existing_periods", lambda _conn, _company: {q4_key: 404}
    )
    monkeypatch.setattr(
        derived, "_load_reported_duration_keys", lambda _conn, _company: set()
    )

    # Without the guard the arithmetic reproduces the wrong stored value exactly.
    monkeypatch.setattr(derived, "_load_non_additive", lambda _conn: (set(), set()))
    unguarded = CaptureConnection()
    derived.derive_q4_for_company(unguarded, 1)
    assert unguarded.fact_rows[0]["value"] == Decimal(old_value)

    _non_additive(monkeypatch)
    conn = CaptureConnection()
    stats = derived.derive_q4_for_company(conn, 1)
    assert conn.fact_rows == [] and stats["non_additive_not_derived"] == 1


# --- Periodic-form gate on derivation inputs (WO-2 RU-1, 2026-10-22) ---
# JPM Q4 2025 net income was derived from a DEF 14A FY (core.fact 182608846)
# and WTRG Q4 from an 8-K carrying another entity's statements. The real-SQL
# behaviour is pinned in test_derived_form_gate_sql.py; this checks, without a
# database, that every input loader passes the gate and the gate's contents.


@pytest.mark.unit
def test_derivation_input_forms_are_the_domestic_periodic_family_only():
    assert set(derived.DERIVATION_INPUT_FORMS) == {
        "10-K",
        "10-K/A",
        "10-KT",
        "10-KT/A",
        "10-Q",
        "10-Q/A",
        "10-QT",
        "10-QT/A",
    }
    for excluded in ("DEF 14A", "8-K", "8-K/A", "S-1", "424B4", "20-F", "40-F", "6-K"):
        assert excluded not in derived.DERIVATION_INPUT_FORMS


class _ParamCursor(CaptureCursor):
    def fetchall(self):
        return []


# Captured at import, before the autouse fixture stubs _load_nine_month_ytd.
_REAL_INPUT_LOADERS = {
    name: getattr(derived, name)
    for name in (
        "_load_quarterly_candidates",
        "_load_nine_month_ytd",
        "_load_all_duration_facts",
    )
}


@pytest.mark.unit
@pytest.mark.parametrize(
    "loader",
    ["_load_quarterly_candidates", "_load_nine_month_ytd", "_load_all_duration_facts"],
)
def test_every_input_loader_filters_on_periodic_forms(monkeypatch, loader):
    real = _REAL_INPUT_LOADERS[loader]
    conn = CaptureConnection()
    conn.cursor = lambda: _ParamCursor(conn)

    real(conn, 7)

    sql, params = conn.statements[0]
    assert "join core.filing fl on fl.id = f.filing_id" in sql
    assert "fl.form = any(%(forms)s)" in sql
    assert (
        params["forms"] == derived.DERIVATION_INPUT_FORMS and params["company_id"] == 7
    )
