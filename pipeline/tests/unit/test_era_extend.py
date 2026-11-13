"""Era back-extension of docmap rows (mapper/era_extend.py): pure walk logic, and the loader against fsn rows."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.mapper import era_extend as ee

TAG = "Revenues"
REF = "0000000077-25-000001"


def L(stmt="IS", prole="terseLabel", label="net sales", parents=("GrossProfit",)):
    return ee.Line(stmt, prole, label, frozenset(parents))


def data(years: dict, lines: dict, mapped=None):
    """years: fiscal year -> accession (period = Dec 31); lines: accession -> {tag: [Line]}."""
    return ee.FsnData(
        {date(y, 12, 31): [a] for y, a in years.items()}, lines, mapped or {}
    )


def acc(y):
    return f"0000000077-{y % 100:02d}-000001"


YEARS = {y: acc(y) for y in range(2015, 2026)}
BASE = date(2024, 1, 1)  # the read (FY2025 10-K) printed FY2025 and FY2024


def lines_for(years, **kw):
    return {acc(y): {TAG: [L(**kw)]} for y in years}


def run(d):
    return ee.extend([TAG], set(), BASE, acc(2025), d)


def test_extends_back_across_continuous_years():
    era, adsh, log = run(data(YEARS, lines_for(YEARS)))
    # the FY2023 10-K prints FY2023 and FY2022 ... the FY2015 10-K prints FY2015 and FY2014; floor 2015-01-01
    assert era == date(2015, 1, 1)
    assert adsh == acc(2016) or adsh == acc(2015)
    assert all(r["check"] == "pass" for r in log)
    assert [r["adsh"] for r in log][0] == acc(2024)


def test_stops_at_a_tag_switch():
    ls = lines_for(YEARS)
    for y in (2020, 2019, 2018, 2017, 2016, 2015):
        ls[acc(y)] = {"SalesRevenueNet": [L()]}  # the company printed another tag before 2021
    era, adsh, log = run(data(YEARS, ls))
    assert era == date(2020, 1, 1)  # the FY2021 10-K prints FY2021 and FY2020
    assert adsh == acc(2021)
    assert log[-1]["check"] == "fail" and "not printed" in log[-1]["detail"]


def test_stops_at_a_changed_line():
    ls = lines_for(YEARS)
    ls[acc(2020)] = {TAG: [L(stmt="CF", label="other", prole="x")]}
    era, adsh, _ = run(data(YEARS, ls))
    assert (era, adsh) == (date(2020, 1, 1), acc(2021))
    ls[acc(2020)] = {TAG: [L(parents=("Other",))]}
    assert run(data(YEARS, ls))[0] == date(2020, 1, 1)  # calc parent changed


def test_stops_at_a_gap_and_never_bridges():
    years = {y: a for y, a in YEARS.items() if y != 2019}  # no FY2019 filing in the store
    era, adsh, log = run(data(years, lines_for(years)))
    assert era == date(2019, 1, 1) and adsh == acc(2020)
    assert log[-1]["check"] == "fail" and log[-1]["detail"].startswith("gap")


def test_other_tag_mapped_to_the_concept_stops():
    ls = lines_for(YEARS)
    mp = {acc(2019): {7: {"SalesRevenueNet"}}}
    era, _, _ = ee.extend([TAG], {7}, BASE, acc(2025), data(YEARS, ls, mp))
    assert era == date(2019, 1, 1)


def test_unknown_reference_extends_nothing():
    d = data(YEARS, {})
    era, adsh, log = run(d)
    assert (era, adsh) == (BASE, None) and log[0]["check"] == "fail"


# ---- loader, DB-backed -------------------------------------------------------------------------------------------

CSV = """ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note
ZZE,revenue,mapped,us-gaap:Revenues,IS,R3.htm,Net sales,,FILING-CHECKED,
"""
MD = f"Latest 10-K opened: {REF} (period 2025-12-31)"


def _seed(conn, years_with_tag):
    cid = conn.execute(
        "insert into core.company (cik, company_name, primary_ticker) values ('0000000077', 'Z', 'ZZE') returning id"
    ).fetchone()[0]
    tid = conn.execute(
        "insert into fsn.tag (tag, version) values ('Revenues', 'us-gaap/2024') returning id"
    ).fetchone()[0]
    other = conn.execute(
        "insert into fsn.tag (tag, version) values ('SalesRevenueNet', 'us-gaap/2024') returning id"
    ).fetchone()[0]
    for y in range(2015, 2026):
        fid = conn.execute(
            "insert into fsn.filing (accession, company_id, cik, form, period, fsn_set) "
            "values (%s, %s, '0000000077', '10-K', %s, 'x') returning id",
            (acc(y), cid, date(y, 12, 31)),
        ).fetchone()[0]
        if y in years_with_tag:
            conn.execute(
                "insert into fsn.line (filing_id, report, line, stmt, tag_id, prole, plabel) "
                "values (%s, 2, 1, 'IS', %s, 'terseLabel', 'Net sales')",
                (fid, tid),
            )
        else:
            conn.execute(
                "insert into fsn.line (filing_id, report, line, stmt, tag_id, prole, plabel) "
                "values (%s, 2, 1, 'IS', %s, 'terseLabel', 'Net sales')",
                (fid, other),
            )
    return cid


@pytest.mark.integration
def test_loader_extends_and_records_evidence(isolated_database_url, tmp_path: Path):
    (tmp_path / "ZZE-docmap-2026-11-12.csv").write_text(CSV)
    (tmp_path / "ZZE-docmap-2026-11-12.md").write_text(MD)
    paths = sorted(tmp_path.glob("*-docmap-*.csv"))
    log = tmp_path / "era.csv"
    with psycopg.connect(isolated_database_url) as conn:
        cid = _seed(conn, set(range(2019, 2026)))  # same tag FY2019-2025, another tag before
        conn.commit()
        plain = dl.load(conn, paths)
        assert plain["extended"] == []
        stats = dl.load(conn, paths, apply=True, extend_eras=True, era_log=log)
        assert len(stats["extended"]) == 1
        rows = conn.execute(
            """select rule_id, era_from::text, era_to::text, evidence_adsh, serve_note, decided_by
               from analytics.company_tag_map where company_id = %s order by era_from""",
            (cid,),
        ).fetchall()
        assert [(r[0], r[1], r[2]) for r in rows] == [
            (ee.EXT_RULE_ID, "2018-01-01", "2023-12-31"),  # FY2019 10-K prints FY2019 and FY2018
            (dl.RULE_ID, "2024-01-01", None),
        ]
        assert rows[0][3] == REF and rows[0][4].startswith(ee.EXT_MARK) and acc(2019) in rows[0][4]
        # idempotent: a second apply replaces both rules' rows
        dl.load(conn, paths, apply=True, extend_eras=True)
        assert conn.execute(
            "select count(*) from analytics.company_tag_map where company_id = %s", (cid,)
        ).fetchone()[0] == 2
    assert "pass" in log.read_text() and "fail" in log.read_text()
