"""FSN `ddate` is the period end rounded to the nearest month end (SEC FSN data sets). A mid-month 52/53-week or
12/16-week end must still match its FSN date, in the pilot's gap accounting and in the cell loader's period binding.
Real case: Kroger (CIK 56873) Q2 FY2015, 12 weeks ending 2015-08-15, stored in FSN as ddate 2015-07-31 with
SalesRevenueGoodsNet 25,539,000,000 (10-Q 0001104659-15-066444)."""

from datetime import date

import psycopg
import pytest

from scrooner_pipeline.common.fsn_dates import fsn_end_matches, nearest_month_ends
from scrooner_pipeline.fsn_store import pilot
from scrooner_pipeline.normalizer import cell_loader

KROGER_Q2_END, KROGER_Q2_FSN = date(2015, 8, 15), date(2015, 7, 31)


@pytest.mark.unit
def test_nearest_month_ends():
    assert nearest_month_ends(KROGER_Q2_END) == {
        KROGER_Q2_FSN
    }  # 15 days back vs 16 forward
    assert nearest_month_ends(date(2015, 11, 7)) == {
        date(2015, 10, 31)
    }  # Kroger Q3 (40 weeks)
    assert nearest_month_ends(date(2016, 1, 30)) == {date(2016, 1, 31)}
    assert nearest_month_ends(date(2015, 6, 13)) == {
        date(2015, 5, 31)
    }  # PepsiCo-style Q2
    assert nearest_month_ends(date(2015, 6, 15)) == {
        date(2015, 5, 31),
        date(2015, 6, 30),
    }  # a tie: both
    assert nearest_month_ends(date(2016, 2, 14)) == {date(2016, 1, 31)}
    assert nearest_month_ends(date(2016, 12, 31)) == {date(2016, 12, 31)}


@pytest.mark.unit
def test_fsn_end_matches_the_rounding_but_not_a_neighbouring_month():
    assert fsn_end_matches(KROGER_Q2_FSN, KROGER_Q2_END)
    assert fsn_end_matches(date(2015, 4, 3), date(2015, 4, 3))  # within 10 days stays
    assert not fsn_end_matches(
        date(2015, 8, 31), KROGER_Q2_END
    )  # 16 days and not the rounding
    assert not fsn_end_matches(date(2015, 6, 30), KROGER_Q2_END)  # a different month


@pytest.mark.unit
def test_pilot_match_finds_the_month_end_rounded_quarter():
    rows = [
        {"id": 1, "period_grain": "Q", "fsn_end": "2015-07-31"},
        {"id": 2, "period_grain": "FY", "fsn_end": "2015-07-31"},
        {"id": 3, "period_grain": "Q", "fsn_end": "2015-10-31"},
    ]
    assert pilot._match(rows, "Q", KROGER_Q2_END)["id"] == 1
    assert pilot._match(rows, "Q", date(2015, 11, 7))["id"] == 3
    assert pilot._match(rows, "Q", date(2015, 9, 30)) is None


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    yield c
    c.close()


@pytest.mark.integration
def test_loader_binds_a_month_end_rounded_fsn_row_to_the_true_period(conn):
    cid = conn.execute(
        "insert into core.company (cik, company_name) values ('0000056873', 'KR TEST') returning id"
    ).fetchone()[0]
    pid = conn.execute(
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) "
        "values (%s, '2015-05-24', '2015-08-15', 'duration', 2015, 'Q2') returning id",
        (cid,),
    ).fetchone()[0]
    conn.commit()
    row = {
        "company_id": cid,
        "data_point_name": "revenue_sanity_resolved",
        "period_grain": "Q",
        "period_start": None,
        "period_end": None,
        "fiscal_year": 2015,
        "fiscal_period": "Q2",
        "period_type": "duration",
        "fsn_end": "2015-07-31",
        "state": "value",
        "value": "25539000000",
        "unit": "USD",
        "source_fact_ids": [],
        "source_value_ids": [1],
        "accession": "0001104659-15-066444",
        "tag": "SalesRevenueGoodsNet",
        "derivation": None,
        "rule_id": "fsn.select_printed@1",
        "evidence_level": "DATA-INFERRED",
        "input_refs": {},
    }
    parsed = cell_loader.parse_row(1, row, {"revenue_sanity_resolved"})
    assert not isinstance(parsed, str), parsed
    bound, bad, created = cell_loader.bind_periods(conn, cid, [parsed], create=False)
    assert [b.period_id for b in bound] == [pid] and bad == [] and created == 0
