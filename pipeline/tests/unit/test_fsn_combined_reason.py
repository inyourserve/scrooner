"""A combined line (MSFT "Depreciation, amortization, and other") is a reason, never a value and never a reasonless gap.

FAMILY-RELEASE-CASE-2026-11-09 §4.1: the capex/D&A detector returned the combined line_map row with no concept, so
the pilot's library never saw the concept and every MSFT D&A key became a `no_mapped_line` gap (done-gate criterion 4
fails the whole company). The row now carries the concept, and the pilot serves `line_presented_combined_with_others`
for each key the combined line prints. Fixture: the real MSFT FY2024 10-K lane filing object
(pipeline/tests/fixtures/fsn_cf_detectors/lane_filings.jsonl.gz, cf_face_extract.py rows of the SEC FSN set)."""

import gzip
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.fsn_store import detectors, pilot
from scrooner_pipeline.fsn_store import select as sel

ROOT = Path(__file__).resolve().parents[3]
FX = ROOT / "pipeline" / "tests" / "fixtures" / "fsn_cf_detectors"
DA, CAPEX = detectors.DA, detectors.CAPEX
COMBINED_TAG = "DepreciationAmortizationAndOther"


def _msft():
    with gzip.open(FX / "lane_filings.jsonl.gz", "rt") as fh:
        for f in map(json.loads, fh):
            if (f["ticker"], f["period"]) == ("MSFT", "20240630"):
                return f
    raise AssertionError("MSFT FY2024 lane filing missing from the fixture")


class _Cur:
    def __init__(self, ids):
        self.ids = ids

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        assert "canonical_concept" in sql

    def fetchall(self):
        return list(self.ids.items())


class _Conn:
    def __init__(self, ids):
        self.ids = ids

    def cursor(self):
        return _Cur(self.ids)


def test_detector_returns_the_msft_combined_line_with_the_da_concept(monkeypatch):
    f = _msft()
    monkeypatch.setattr(detectors, "filing_object", lambda conn, fid: f)
    ids = {CAPEX: 11, DA: 12}
    out = detectors.capex_da_detector(_Conn(ids), 1, [])
    line = next(r for r in f["face"] if r["tag"] == COMBINED_TAG)
    row = next(o for o in out if (o[1], o[2]) == (line["report"], line["line"]))
    assert row[4] == "combined"
    assert row[3] == ids[DA], (
        "the combined row must carry the D&A concept, or the pilot reports a reasonless gap"
    )
    # nothing is MAPPED to D&A in this filing: the combined line is never a value
    assert not [o for o in out if o[3] == ids[DA] and o[4] == "mapped"]
    assert [o for o in out if o[3] == ids[CAPEX] and o[4] == "mapped"]


def _filing(i, acc, accepted, form, period):
    return sel.Filing(
        i,
        acc,
        datetime.fromisoformat(accepted),
        form,
        date.fromisoformat(period),
        2024,
        "FY",
    )


def test_combined_line_cells_reason_every_printed_key_and_keep_existing_cells():
    f = _msft()
    filings = {1: _filing(1, f["adsh"], "2024-07-30T16:00:00", "10-K", "2024-06-30")}
    prints = [
        sel.Print(
            i,
            1,
            COMBINED_TAG,
            date.fromisoformat(k.split("|")[0]),
            int(k.split("|")[1]),
            "USD",
            Decimal(v[COMBINED_TAG]),
            -6,
            "CF",
            True,
        )
        for i, (k, v) in enumerate(sorted(f["values"].items()), start=1)
        if COMBINED_TAG in v
    ]
    assert {p.qtrs for p in prints} == {4} and len(
        prints
    ) == 3  # FY2022-FY2024 columns of the 10-K
    cells = sel.combined_line_cells(DA, prints, filings, set())
    keys = {(c.ddate, c.qtrs) for c in cells}
    assert keys == {
        (p.ddate, q) for p in prints for q in (1, 4)
    }  # each FY and the Q4 inside it
    assert {c.state for c in cells} == {"not_presented"}
    assert {c.reason_code for c in cells} == {"line_presented_combined_with_others"}
    assert all(c.value is None for c in cells)
    row = sel.to_row(cells[0], 4, filings)
    assert (
        row["reason_code"] == "line_presented_combined_with_others"
        and row["reason_text"]
    )
    assert row["value"] is None and row["accession"] == f["adsh"]
    # a key that already has a cell (a value or a defect) keeps it
    top = max(p.ddate for p in prints)
    kept = sel.combined_line_cells(DA, prints, filings, {(top, 4)})
    assert (top, 4) not in {(c.ddate, c.qtrs) for c in kept} and len(kept) == len(
        cells
    ) - 1


def test_combined_line_cells_skip_note_prints():
    filings = {1: _filing(1, "a", "2024-07-30T16:00:00", "10-K", "2024-06-30")}
    note = sel.Print(
        1, 1, COMBINED_TAG, date(2024, 6, 30), 4, "USD", Decimal(1), -6, "CF", False
    )
    assert sel.combined_line_cells(DA, [note], filings, set()) == []


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if (
        _one(
            c,
            "select count(*) from information_schema.tables where table_schema = 'fsn' and table_name = 'line_map'",
        )
        != 1
    ):
        c.close()
        pytest.skip("needs migration 0118")
    yield c
    c.close()


@pytest.mark.integration
def test_load_company_reads_combined_lines_apart_from_mapped_ones(conn, tmp_path):
    """The store side: a combined line_map row with a concept is read into combined_prints, never into prints."""
    for name in (DA, "cfo_resolved"):
        conn.execute(
            "insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, 'cash_flow', "
            "'first_match') on conflict (name) do nothing",
            (name,),
        )
    da_id = _one(
        conn, "select id from analytics.canonical_concept where name = %s", (DA,)
    )
    cfo_id = _one(
        conn, "select id from analytics.canonical_concept where name = 'cfo_resolved'"
    )
    cid = _one(
        conn,
        "insert into core.company (cik, company_name) values ('0000789019', 'MSFT TEST') returning id",
    )
    fid = _one(
        conn,
        "insert into fsn.filing (accession, company_id, cik, form, period, fy, fp, accepted, fsn_set) values "
        "('0000950170-24-087843', %s, '0000789019', '10-K', '2024-06-30', 2024, 'FY', '2024-07-30 16:00+00', "
        "'2024m07') returning id",
        (cid,),
    )
    tags = {}
    for t in (COMBINED_TAG, "NetCashProvidedByUsedInOperatingActivities"):
        custom = t == COMBINED_TAG
        tags[t] = _one(
            conn,
            "insert into fsn.tag (tag, version, custom) values (%s, %s, %s) returning id",
            (t, "0000950170-24-087843" if custom else "us-gaap/2024", custom),
        )
    conn.execute(
        "insert into fsn.report (filing_id, report, menucat) values (%s, 6, 'S')",
        (fid,),
    )
    for ln, t in (
        (4, COMBINED_TAG),
        (20, "NetCashProvidedByUsedInOperatingActivities"),
    ):
        conn.execute(
            "insert into fsn.line (filing_id, report, line, stmt, tag_id, plabel) values (%s, 6, %s, 'CF', %s, %s)",
            (fid, ln, tags[t], t),
        )
    for t, v in (
        (COMBINED_TAG, 22287),
        ("NetCashProvidedByUsedInOperatingActivities", 118548),
    ):
        conn.execute(
            "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, value, dcml) "
            "values (%s, %s, %s, '2024-06-30', 4, 'USD', 0, %s, -6)",
            (fid, cid, tags[t], v * 1_000_000),
        )
    conn.execute(
        "insert into fsn.line_map (filing_id, report, line, canonical_concept_id, status, rule_id) values "
        "(%s, 6, 4, %s, 'combined', 'cf.capex_da_held@1'), (%s, 6, 20, %s, 'mapped', 'cf.cfo@1')",
        (fid, da_id, fid, cfo_id),
    )
    conn.commit()
    data = sel.load_company(conn, cid)
    assert DA not in data["prints"], "a combined line must never be a value candidate"
    assert [p.value for p in data["combined_prints"][DA]] == [Decimal(22287_000_000)]
    assert data["combined_prints"][DA][
        0
    ].face  # the CF anchor is printed in that column
    got = sel.combined_line_cells(
        DA, data["combined_prints"][DA], data["filings"], set()
    )
    assert {(c.ddate, c.qtrs, c.reason_code) for c in got} == {
        (date(2024, 6, 30), 1, "line_presented_combined_with_others"),
        (date(2024, 6, 30), 4, "line_presented_combined_with_others"),
    }
    # the pilot's library sees the concept on the combined row (no `no_mapped_line` gap)
    lib = pilot.library(conn, cid)
    assert any(e["data_point"] == DA and e["status"] == "combined" for e in lib)
    # end to end: the pilot report serves the reason and has no reasonless D&A key (done-gate criterion 4)
    cal = tmp_path / "calendar.csv.gz"
    with gzip.open(cal, "wt") as fh:
        fh.write(
            "company_id,cik,fiscal_year,fiscal_period,period_type,period_start,period_end\n"
        )
    rep = pilot.report_company(conn, cid, cal, {DA, "cfo_resolved"})
    assert not [g for g in rep["_gaps"] if g["data_point"] == DA]
    da = [r for r in rep["_cells"] if r["data_point_name"] == DA]
    assert {(r["period_grain"], r["state"], r["reason_code"]) for r in da} == {
        ("FY", "not_presented", "line_presented_combined_with_others"),
        ("Q", "not_presented", "line_presented_combined_with_others"),
    }
