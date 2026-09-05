import csv
import io
import zipfile
from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.ownership.mutual_fund import (
    _load_fund_series_lookup,
    _load_registrant_lookup,
    _load_submission_lookup,
    _match_holdings,
    _write_matched_rows,
)


def _make_nport_zip(
    submission_rows: list[dict],
    registrant_rows: list[dict],
    fund_info_rows: list[dict],
    holding_rows: list[dict],
) -> zipfile.ZipFile:
    """Builds a real in-memory zip with the 4 real N-PORT tables this
    module reads, using the exact real column names confirmed live
    2026-08-28 against SEC's actual 2026q2_nport.zip -- not a simplified
    schema. Lets _match_holdings/_load_*_lookup run against a real
    zipfile.ZipFile the same way they do against a downloaded one."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, rows, fieldnames in [
            ("SUBMISSION.tsv", submission_rows, ["ACCESSION_NUMBER", "FILING_DATE", "FILE_NUM", "SUB_TYPE", "REPORT_ENDING_PERIOD", "REPORT_DATE", "IS_LAST_FILING"]),
            ("REGISTRANT.tsv", registrant_rows, ["ACCESSION_NUMBER", "CIK", "REGISTRANT_NAME", "FILE_NUM", "LEI", "ADDRESS1", "ADDRESS2", "CITY", "STATE", "COUNTRY", "ZIP", "PHONE"]),
            ("FUND_REPORTED_INFO.tsv", fund_info_rows, ["ACCESSION_NUMBER", "SERIES_NAME", "SERIES_ID"]),
            (
                "FUND_REPORTED_HOLDING.tsv",
                holding_rows,
                [
                    "ACCESSION_NUMBER", "HOLDING_ID", "ISSUER_NAME", "ISSUER_LEI", "ISSUER_TITLE",
                    "ISSUER_CUSIP", "BALANCE", "UNIT", "OTHER_UNIT_DESC", "CURRENCY_CODE",
                    "CURRENCY_VALUE", "EXCHANGE_RATE", "PERCENTAGE", "PAYOFF_PROFILE", "ASSET_CAT",
                    "OTHER_ASSET", "ISSUER_TYPE", "OTHER_ISSUER", "INVESTMENT_COUNTRY",
                    "IS_RESTRICTED_SECURITY", "FAIR_VALUE_LEVEL", "DERIVATIVE_CAT",
                ],
            ),
        ]:
            out = io.StringIO()
            writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            for row in rows:
                writer.writerow({f: row.get(f, "") for f in fieldnames})
            zf.writestr(name, out.getvalue())
    buf.seek(0)
    return zipfile.ZipFile(buf)


AAPL_HOLDING_BASE = {
    "ACCESSION_NUMBER": "0000894189-26-020707",
    "HOLDING_ID": "173355627",
    "ISSUER_NAME": "Apple Inc",
    "ISSUER_LEI": "HWUPKR0MPOU8FGXBT394",
    "ISSUER_TITLE": "Apple Inc",
    "ISSUER_CUSIP": "037833100",
    "BALANCE": "836",
    "UNIT": "NS",
    "CURRENCY_CODE": "USD",
    "CURRENCY_VALUE": "226848.6",
    "PERCENTAGE": "2.009894444",
    "PAYOFF_PROFILE": "Long",
    "ASSET_CAT": "EC",
    "ISSUER_TYPE": "CORP",
    "INVESTMENT_COUNTRY": "US",
    "DERIVATIVE_CAT": "",
}


@pytest.mark.unit
def test_match_holdings_keeps_real_equity_long_position():
    """Real AAPL sample row (ASSET_CAT=EC, PAYOFF_PROFILE=Long, CUSIP
    matches a golden company) -- checked live 2026-08-28 against the real
    2026q2_nport.zip before writing this fixture."""
    zf = _make_nport_zip(
        submission_rows=[{
            "ACCESSION_NUMBER": "0000894189-26-020707", "FILING_DATE": "24-APR-2026",
            "SUB_TYPE": "NPORT-P", "REPORT_ENDING_PERIOD": "31-JAN-2027", "REPORT_DATE": "31-MAY-2026",
        }],
        registrant_rows=[{
            "ACCESSION_NUMBER": "0000894189-26-020707", "CIK": "0000783740",
            "REGISTRANT_NAME": "MFS SERIES TRUST X",
        }],
        fund_info_rows=[{
            "ACCESSION_NUMBER": "0000894189-26-020707",
            "SERIES_NAME": "MFS International Growth Fund", "SERIES_ID": "S000012345",
        }],
        holding_rows=[AAPL_HOLDING_BASE],
    )
    submission_lookup = _load_submission_lookup(zf)
    registrant_lookup = _load_registrant_lookup(zf)
    series_lookup = _load_fund_series_lookup(zf)
    cusip_to_company = {"037833100": 1}

    matched, total_rows = _match_holdings(zf, cusip_to_company, submission_lookup, registrant_lookup, series_lookup, "2026q2")

    assert total_rows == 1
    assert len(matched) == 1
    row = matched[0]
    assert row["company_id"] == 1
    assert row["fund_name"] == "MFS International Growth Fund"  # series name, NOT the trust
    assert row["fund_cik"] == "0000783740"
    assert row["series_id"] == "S000012345"
    assert row["shares"] == Decimal("836")
    assert row["currency_code"] == "USD"
    assert row["value_usd"] == Decimal("226848.6")
    assert row["pct_of_fund_net_assets"] == Decimal("2.009894444")
    assert row["report_period"] == date(2026, 5, 31)
    assert row["filing_date"] == date(2026, 4, 24)
    assert row["is_amendment"] is False
    assert row["source_zip"] == "2026q2"  # tagged per-row from the window arg, not injected at write time


@pytest.mark.unit
def test_match_holdings_excludes_derivative_and_short_and_non_matching_cusip():
    """A real N-PORT bulk window mixes actual share ownership with
    derivatives (ASSET_CAT=DE, DERIVATIVE_CAT populated) and short
    positions (PAYOFF_PROFILE=Short) under the exact same CUSIP as a real
    equity holding -- checked live: of 14,080 raw golden-10 CUSIP matches
    in the real 2026q2 file, only 13,871 were ASSET_CAT=EC/PAYOFF_PROFILE=
    Long. None of these three should ever be written as real ownership."""
    swap_row = {
        **AAPL_HOLDING_BASE,
        "HOLDING_ID": "999000001",
        "ASSET_CAT": "DE",
        "DERIVATIVE_CAT": "SWP",
        "PAYOFF_PROFILE": "N/A",
    }
    short_row = {
        **AAPL_HOLDING_BASE,
        "HOLDING_ID": "999000002",
        "PAYOFF_PROFILE": "Short",
    }
    unmatched_cusip_row = {
        **AAPL_HOLDING_BASE,
        "HOLDING_ID": "999000003",
        "ISSUER_CUSIP": "999999999",  # real filler CUSIP for non-security holdings (e.g. FX futures)
    }
    zf = _make_nport_zip(
        submission_rows=[{
            "ACCESSION_NUMBER": "0000894189-26-020707", "FILING_DATE": "24-APR-2026",
            "SUB_TYPE": "NPORT-P", "REPORT_ENDING_PERIOD": "31-JAN-2027", "REPORT_DATE": "31-MAY-2026",
        }],
        registrant_rows=[{
            "ACCESSION_NUMBER": "0000894189-26-020707", "CIK": "0000783740",
            "REGISTRANT_NAME": "MFS SERIES TRUST X",
        }],
        fund_info_rows=[],
        holding_rows=[AAPL_HOLDING_BASE, swap_row, short_row, unmatched_cusip_row],
    )
    submission_lookup = _load_submission_lookup(zf)
    registrant_lookup = _load_registrant_lookup(zf)
    series_lookup = _load_fund_series_lookup(zf)
    cusip_to_company = {"037833100": 1}

    matched, total_rows = _match_holdings(zf, cusip_to_company, submission_lookup, registrant_lookup, series_lookup, "2026q2")

    assert total_rows == 4
    assert len(matched) == 1
    assert matched[0]["holding_id"] == 173355627


@pytest.mark.unit
def test_match_holdings_falls_back_to_registrant_name_without_series_row():
    """FUND_REPORTED_INFO is missing for this accession (a real, if rare,
    possibility) -- fund_name must fall back to the umbrella trust name
    rather than come back empty."""
    zf = _make_nport_zip(
        submission_rows=[{
            "ACCESSION_NUMBER": "0000894189-26-020707", "FILING_DATE": "24-APR-2026",
            "SUB_TYPE": "NPORT-P", "REPORT_ENDING_PERIOD": "31-JAN-2027", "REPORT_DATE": "31-MAY-2026",
        }],
        registrant_rows=[{
            "ACCESSION_NUMBER": "0000894189-26-020707", "CIK": "0000783740",
            "REGISTRANT_NAME": "MFS SERIES TRUST X",
        }],
        fund_info_rows=[],  # no series row for this accession
        holding_rows=[AAPL_HOLDING_BASE],
    )
    submission_lookup = _load_submission_lookup(zf)
    registrant_lookup = _load_registrant_lookup(zf)
    series_lookup = _load_fund_series_lookup(zf)
    cusip_to_company = {"037833100": 1}

    matched, _ = _match_holdings(zf, cusip_to_company, submission_lookup, registrant_lookup, series_lookup, "2026q2")

    assert matched[0]["fund_name"] == "MFS SERIES TRUST X"


@pytest.mark.unit
def test_match_holdings_treats_literal_na_series_name_as_missing():
    """Real finding (checked live 2026-08-28): 28 of 14,416 real
    FUND_REPORTED_INFO rows in the 2026q2 window carry the literal string
    "N/A" as SERIES_NAME -- single-series unit investment trusts like the
    SPDR S&P 500 ETF Trust, whose one series has no name distinct from
    the trust itself. Writing the literal text "N/A" as fund_name would
    be worse than falling back to the real, recognizable registrant
    name."""
    zf = _make_nport_zip(
        submission_rows=[{
            "ACCESSION_NUMBER": "0001410368-26-055357", "FILING_DATE": "24-APR-2026",
            "SUB_TYPE": "NPORT-P", "REPORT_ENDING_PERIOD": "31-JAN-2027", "REPORT_DATE": "31-MAY-2026",
        }],
        registrant_rows=[{
            "ACCESSION_NUMBER": "0001410368-26-055357", "CIK": "0000884394",
            "REGISTRANT_NAME": "State Street(R) SPDR(R) S&P 500(R) ETF Trust",
        }],
        fund_info_rows=[{
            "ACCESSION_NUMBER": "0001410368-26-055357", "SERIES_NAME": "N/A", "SERIES_ID": "",
        }],
        holding_rows=[{**AAPL_HOLDING_BASE, "ACCESSION_NUMBER": "0001410368-26-055357"}],
    )
    submission_lookup = _load_submission_lookup(zf)
    registrant_lookup = _load_registrant_lookup(zf)
    series_lookup = _load_fund_series_lookup(zf)
    cusip_to_company = {"037833100": 1}

    matched, _ = _match_holdings(zf, cusip_to_company, submission_lookup, registrant_lookup, series_lookup, "2026q2")

    assert matched[0]["fund_name"] == "State Street(R) SPDR(R) S&P 500(R) ETF Trust"
    assert matched[0]["series_id"] is None


@pytest.mark.unit
def test_match_holdings_leaves_value_usd_null_for_non_usd_currency():
    """Real finding (checked live 2026-08-28): ~2% of golden-10 CUSIP
    matches report CURRENCY_VALUE in a non-USD currency (e.g. TWD for
    TSMC's Taiwan-listed ordinary shares), each with an EXCHANGE_RATE
    field whose multiply-vs-divide convention was never independently
    confirmed. value_usd must stay null rather than guess a conversion --
    same "leave null, never guess" discipline as core.fact.is_authoritative
    -- while currency_value/currency_code still carry the raw reported
    figure so nothing is lost."""
    tsmc_row = {
        **AAPL_HOLDING_BASE,
        "ISSUER_CUSIP": "Y84629107",
        "ISSUER_NAME": "TSMC",
        "CURRENCY_CODE": "TWD",
        "CURRENCY_VALUE": "2460311.03",
        "EXCHANGE_RATE": "31.6845",
        "INVESTMENT_COUNTRY": "TW",
    }
    zf = _make_nport_zip(
        submission_rows=[{
            "ACCESSION_NUMBER": "0000894189-26-020707", "FILING_DATE": "24-APR-2026",
            "SUB_TYPE": "NPORT-P", "REPORT_ENDING_PERIOD": "31-JAN-2027", "REPORT_DATE": "31-MAY-2026",
        }],
        registrant_rows=[{
            "ACCESSION_NUMBER": "0000894189-26-020707", "CIK": "0000783740",
            "REGISTRANT_NAME": "MFS SERIES TRUST X",
        }],
        fund_info_rows=[],
        holding_rows=[tsmc_row],
    )
    submission_lookup = _load_submission_lookup(zf)
    registrant_lookup = _load_registrant_lookup(zf)
    series_lookup = _load_fund_series_lookup(zf)
    cusip_to_company = {"Y84629107": 6}

    matched, _ = _match_holdings(zf, cusip_to_company, submission_lookup, registrant_lookup, series_lookup, "2026q2")

    row = matched[0]
    assert row["currency_code"] == "TWD"
    assert row["currency_value"] == Decimal("2460311.03")
    assert row["value_usd"] is None


@pytest.mark.unit
def test_match_holdings_flags_amendment_without_dropping_it():
    """SUB_TYPE ending in "/A" is a real amendment (SEC's own
    NPORT-P/A convention, confirmed live) -- flagged, never filtered out,
    same "never silently drop" discipline as institutional.py's own
    is_amendment handling."""
    zf = _make_nport_zip(
        submission_rows=[{
            "ACCESSION_NUMBER": "0000894189-26-020707", "FILING_DATE": "24-APR-2026",
            "SUB_TYPE": "NPORT-P/A", "REPORT_ENDING_PERIOD": "31-JAN-2027", "REPORT_DATE": "31-MAY-2026",
        }],
        registrant_rows=[{
            "ACCESSION_NUMBER": "0000894189-26-020707", "CIK": "0000783740",
            "REGISTRANT_NAME": "MFS SERIES TRUST X",
        }],
        fund_info_rows=[],
        holding_rows=[AAPL_HOLDING_BASE],
    )
    submission_lookup = _load_submission_lookup(zf)
    registrant_lookup = _load_registrant_lookup(zf)
    series_lookup = _load_fund_series_lookup(zf)
    cusip_to_company = {"037833100": 1}

    matched, _ = _match_holdings(zf, cusip_to_company, submission_lookup, registrant_lookup, series_lookup, "2026q2")

    assert matched[0]["is_amendment"] is True


class FundOwnershipCursor:
    """Hand-rolled fake cursor, same style as test_restatements.py's
    RestatementCursor -- models exactly the two statements
    _write_matched_rows issues (a scoped delete, then a batch insert),
    against an in-memory list standing in for core.fund_ownership."""

    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split())
        if normalized.startswith("delete from core.fund_ownership where company_id = any"):
            (company_ids,) = params
            self.conn.rows = [r for r in self.conn.rows if r["company_id"] not in company_ids]
        else:
            raise AssertionError(f"Unexpected SQL in fund_ownership test: {normalized}")

    def executemany(self, sql, params_list):
        normalized = " ".join(sql.split())
        if not normalized.startswith("insert into core.fund_ownership"):
            raise AssertionError(f"Unexpected executemany SQL in fund_ownership test: {normalized}")
        existing_keys = {(r["accession_number"], r["holding_id"]) for r in self.conn.rows}
        for row in params_list:
            key = (row["accession_number"], row["holding_id"])
            if key in existing_keys:
                continue  # on conflict (accession_number, holding_id) do nothing
            self.conn.rows.append(dict(row))
            existing_keys.add(key)


class FundOwnershipConnection:
    def __init__(self, rows=None):
        self.rows = rows or []

    def cursor(self):
        return FundOwnershipCursor(self)


@pytest.mark.unit
def test_write_matched_rows_replaces_stale_rows_for_touched_companies_only():
    """A company's holdings can shrink between runs (a fund exits a
    position) -- a plain on-conflict-do-nothing upsert would leave that
    stale row behind forever. _write_matched_rows must delete-then-
    reinsert scoped to exactly the companies in this run's matched_rows,
    leaving untouched companies' existing rows alone -- same idempotency
    precedent as institutional.py/Mapper's resolve.py."""
    conn = FundOwnershipConnection(rows=[
        {"company_id": 1, "accession_number": "STALE-ACC", "holding_id": 1, "fund_name": "Old Fund"},
        {"company_id": 2, "accession_number": "OTHER-CO-ACC", "holding_id": 1, "fund_name": "Untouched Fund"},
    ])
    new_rows = [
        {
            "company_id": 1, "accession_number": "NEW-ACC", "holding_id": 1, "fund_name": "New Fund",
            "fund_cik": "1", "series_id": None, "shares": Decimal("100"), "currency_code": "USD",
            "currency_value": Decimal("1000"), "value_usd": Decimal("1000"),
            "pct_of_fund_net_assets": Decimal("1.5"), "report_period": date(2026, 5, 31),
            "filing_date": date(2026, 4, 24), "is_amendment": False, "source_zip": "2026q2",
        },
    ]

    company_ids = _write_matched_rows(conn, new_rows)

    assert company_ids == [1]
    remaining = {(r["company_id"], r["accession_number"]) for r in conn.rows}
    assert (1, "STALE-ACC") not in remaining  # old row for the touched company is gone
    assert (1, "NEW-ACC") in remaining  # new row for it is present
    assert (2, "OTHER-CO-ACC") in remaining  # untouched company's row is left alone


@pytest.mark.unit
def test_write_matched_rows_on_conflict_do_nothing_for_same_accession_and_holding():
    """(accession_number, holding_id) is the real primary key N-PORT
    itself guarantees uniqueness on (per nport_readme.htm's own
    field-layout table: HOLDING_ID is "Key for each holding in the
    schedule of portfolio investments") -- a rerun inserting the exact
    same row twice within one write must not duplicate it."""
    conn = FundOwnershipConnection(rows=[])
    row = {
        "company_id": 1, "accession_number": "ACC-1", "holding_id": 1, "fund_name": "Fund A",
        "fund_cik": "1", "series_id": None, "shares": Decimal("100"), "currency_code": "USD",
        "currency_value": Decimal("1000"), "value_usd": Decimal("1000"),
        "pct_of_fund_net_assets": Decimal("1.5"), "report_period": date(2026, 5, 31),
        "filing_date": date(2026, 4, 24), "is_amendment": False, "source_zip": "2026q2",
    }

    _write_matched_rows(conn, [row, dict(row)])

    assert len(conn.rows) == 1


@pytest.mark.unit
def test_write_matched_rows_merges_both_windows_in_one_pass_without_clobbering():
    """The real bug this design avoids: if _write_matched_rows were called
    once per window (delete-then-reinsert scoped by company_id only, no
    window dimension), the second window's write would silently delete
    the first window's already-written rows for any company matched in
    both -- both share the same company_id, and a company_id-only delete
    has no way to tell them apart. update_mutual_fund_ownership avoids
    this by merging both windows' matched_rows into ONE list before ever
    calling _write_matched_rows -- proven here directly: one call with
    rows from two different report_periods/source_zips for the same
    company must leave both intact."""
    conn = FundOwnershipConnection(rows=[])
    q2_row = {
        "company_id": 1, "accession_number": "ACC-Q2", "holding_id": 1, "fund_name": "Fund A",
        "fund_cik": "1", "series_id": "S1", "shares": Decimal("100"), "currency_code": "USD",
        "currency_value": Decimal("1000"), "value_usd": Decimal("1000"),
        "pct_of_fund_net_assets": Decimal("1.5"), "report_period": date(2026, 5, 31),
        "filing_date": date(2026, 4, 24), "is_amendment": False, "source_zip": "2026q2",
    }
    q1_row = {
        **q2_row,
        "accession_number": "ACC-Q1", "shares": Decimal("90"),
        "report_period": date(2026, 2, 28), "filing_date": date(2026, 1, 24),
        "source_zip": "2026q1",
    }

    company_ids = _write_matched_rows(conn, [q2_row, q1_row])

    assert company_ids == [1]
    windows_present = {r["source_zip"] for r in conn.rows if r["company_id"] == 1}
    assert windows_present == {"2026q2", "2026q1"}
    assert len(conn.rows) == 2
