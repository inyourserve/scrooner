"""Predictor candidates (mapper/era_predictor.py), the loader's predictor / no-filing paths and the proof guard
(mapper/era_guard.py): pure logic and DB-backed (CI: Postgres 16)."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.mapper import era_extend as ee
from scrooner_pipeline.mapper import era_guard as eg
from scrooner_pipeline.mapper import era_predictor as ep

COLS = "ticker,rank,data_point,status,tags,stmt,sign,scale,era_break,prior_tag,value_source,acc,r_page,label,fy0_value,rule,rule_ids,fy0_api,evidence_class,period,rules_commit".split(",")
CONCEPTS = {"revenue_sanity_resolved": 1, "gross_profit": 2}
STATEMENT = {"revenue_sanity_resolved": "income_statement", "gross_profit": "income_statement"}


def pred(period, dp="revenue", status="mapped", tags="us-gaap:SalesRevenueNet", acc=None, stmt="IS"):
    acc = acc or f"0000000077-{period.year % 100:02d}-000001"
    return {"ticker": "ZZE", "rank": "1", "data_point": dp, "status": status, "tags": tags, "stmt": stmt, "sign": "+",
            "scale": "", "era_break": "", "prior_tag": "", "value_source": "sec_api", "acc": acc, "r_page": "R4", "label": "Net sales",
            "fy0_value": "1", "rule": "library map", "rule_ids": "lib.is.SalesRevenueNet", "fy0_api": "1",
            "evidence_class": "PREDICTED (predict.py v7-x)", "period": period.isoformat(), "rules_commit": "d79b53a0"}


def docrow(era_from=date(2022, 1, 1), dp="revenue_sanity_resolved", status="mapped", tags="us-gaap:Revenues"):
    return dl.DocmapRow("ZZE", dp, status, dl.parse_parts(tags) if tags else (), "IS", "R4", "Net sales", era_from,
                        "0000000077-26-000001", "r", "f.csv", date(2025, 12, 31))


def cand(preds, docrows, **kw):
    by = {}
    for p in preds:
        by.setdefault(date.fromisoformat(p["period"]), []).append(p)
    return ep.candidates("ZZE", by, docrows, CONCEPTS, STATEMENT, 7, "0000000077", **kw)


def test_one_slice_per_earlier_filing_contiguous_and_clipped_before_the_boundary():
    rows, rej = cand([pred(date(y, 12, 31)) for y in (2019, 2020, 2021, 2022)], [docrow()])
    assert rej == []
    assert [(r["era_from"].isoformat(), r["era_to"].isoformat()) for r in rows] == [
        ("2019-01-01", "2019-12-31"), ("2020-01-01", "2020-12-31"), ("2021-01-01", "2021-12-31")]  # FY2022 is the extension's
    assert {(r["rule_id"], r["decided_by"], r["tag"], r["decision"]) for r in rows} == {
        (ee.EXT_RULE_ID, ep.PREDICTOR_BY, "SalesRevenueNet", "concept")}
    assert all(r["serve_note"].startswith(ep.MARK) and "d79b53a0" in r["serve_note"] for r in rows)


def test_a_data_point_already_covered_to_the_window_gets_none_and_concepts_filter():
    assert cand([pred(date(2019, 12, 31))], [docrow(era_from=date(2015, 1, 1))])[0] == []
    preds = [pred(date(2020, 12, 31)), pred(date(2020, 12, 31), dp="gross_profit")]
    both = [docrow(), docrow(dp="gross_profit", tags="us-gaap:GrossProfit")]
    assert {r["canonical_concept"] for r in cand(preds, both)[0]} == {"revenue_sanity_resolved", "gross_profit"}
    assert {r["canonical_concept"] for r in cand(preds, both, concepts={"gross_profit"})[0]} == {"gross_profit"}


def test_reason_rows_and_rejects():
    rows, rej = cand([pred(date(2020, 12, 31), status="not_presented", tags=""),
                      pred(date(2021, 12, 31), tags="us-gaap:Revenues[ProductMember=x]")], [docrow()])
    assert [(r["decision"], r["tag"] if "tag" in r else None, r["reason_class"]) for r in rows] == [
        ("not_presented", None, "predictor_candidate")]
    assert [x["why"] for x in rej] == ["member_not_supported"]


def test_no_filing_rows():
    (row,) = ep.no_filing_rows([docrow()], STATEMENT, 7, "0000000077")
    assert (row["decision"], row["reason_class"], row["era_from"], row["era_to"]) == (
        "not_presented", ep.NO_FILING_REASON, date(2015, 1, 1), date(2021, 12, 31))
    assert ep.no_filing_rows([docrow(era_from=date(2015, 1, 1))], STATEMENT, 7, "0000000077") == []


def test_guard_verdict_rule():
    assert eg.verdict_backs(True, ["PROVEN", "PROVEN"])
    assert not eg.verdict_backs(True, ["PROVEN", "DISAGREE"]) and not eg.verdict_backs(True, []) and not eg.verdict_backs(True, ["NOT_PRESENTED"])
    assert eg.verdict_backs(False, ["NOT_PRESENTED"]) and not eg.verdict_backs(False, ["PROVEN"])


CSV = """ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note
ZZE,revenue,mapped,us-gaap:Revenues,IS,R3.htm,Net sales,,FILING-CHECKED,
ZZE,gross_profit,mapped,us-gaap:GrossProfit,IS,R3.htm,Gross profit,,FILING-CHECKED,
"""
MD = "Latest 10-K opened: 0000000077-25-000001 (period 2025-12-31)"


def write_preds(d: Path, tag="SalesRevenueNet"):
    d.mkdir(exist_ok=True)
    for y in (2021, 2022, 2023):
        rows = [pred(date(y, 12, 31), tags=f"us-gaap:{tag}"), pred(date(y, 12, 31), dp="gross_profit", tags="us-gaap:GrossProfit")]
        with (d / f"ZZE-0000000077-{y % 100:02d}-000001-prediction.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS)
            w.writeheader()
            w.writerows(rows)


def snap(conn, cid):
    return conn.execute("select decided_by, tag, era_from::text, era_to::text, decision, reason_class from analytics.company_tag_map "
                        "where company_id = %s order by era_from, tag", (cid,)).fetchall()


@pytest.mark.integration
def test_a_candidate_never_overlaps_a_row_that_already_covers_its_years(isolated_database_url, tmp_path: Path):
    (tmp_path / "ZZE-docmap-2026-11-12.csv").write_text(CSV)
    (tmp_path / "ZZE-docmap-2026-11-12.md").write_text(MD)
    eras = tmp_path / "eras"
    write_preds(eras)
    with psycopg.connect(isolated_database_url) as conn:
        cid = conn.execute("insert into core.company (cik, company_name, primary_ticker) values ('0000000077', 'Z', 'ZZE') returning id").fetchone()[0]
        gp = conn.execute("select id from analytics.canonical_concept where name = 'gross_profit_resolved'").fetchone()[0]
        conn.execute("insert into analytics.company_tag_map (company_id, cik, taxonomy, tag, stmt, decision, canonical_concept_id, era_from, era_to, "
                     "decided_by, rule_id) values (%s, '0000000077', 'us-gaap', 'GrossProfit', 'IS', 'concept', %s, '2021-01-01', '2021-12-31', 'structure', "
                     "'company_tag_map.library@1')", (cid, gp))
        conn.commit()
        stats = dl.load(conn, sorted(tmp_path.glob("*-docmap-*.csv")), apply=True, predictor_eras=eras)
        assert stats["blocked"] == {}
        gps = [r for r in snap(conn, cid) if r[1] == "GrossProfit"]
        assert [(r[0], r[2]) for r in gps] == [("structure", "2021-01-01"), (ep.PREDICTOR_BY, "2022-01-01"), (ep.PREDICTOR_BY, "2023-01-01"), ("docmap", "2024-01-01")]


@pytest.mark.integration
def test_loader_predictor_slices_reload_by_concept_and_the_guard(isolated_database_url, tmp_path: Path):
    (tmp_path / "ZZE-docmap-2026-11-12.csv").write_text(CSV)
    (tmp_path / "ZZE-docmap-2026-11-12.md").write_text(MD)
    paths = sorted(tmp_path.glob("*-docmap-*.csv"))
    eras = tmp_path / "eras"
    write_preds(eras)
    with psycopg.connect(isolated_database_url) as conn:
        cid = conn.execute("insert into core.company (cik, company_name, primary_ticker) values ('0000000077', 'Z', 'ZZE') returning id").fetchone()[0]
        conn.commit()
        dry = dl.load(conn, paths, predictor_eras=eras)
        assert dry["companies"]["0000000077"]["predictor_rows"] == 6 and not dry["applied"]
        assert snap(conn, cid) == []  # a dry run writes nothing
        stats = dl.load(conn, paths, apply=True, predictor_eras=eras)
        assert stats["blocked"] == {}
        rows = snap(conn, cid)
        assert [r[0] for r in rows].count(ep.PREDICTOR_BY) == 6 and [r[0] for r in rows].count("docmap") == 2
        assert ("tag_expert_predictor", "SalesRevenueNet", "2021-01-01", "2021-12-31", "concept", None) in rows
        # a load without the predictor flag leaves the predictor rows alone
        dl.load(conn, paths, apply=True)
        assert snap(conn, cid) == rows
        # reloading one concept replaces only its predictor rows
        write_preds(eras, tag="Revenues2")
        dl.load(conn, paths, apply=True, predictor_eras=eras, predictor_concepts={"revenue"})
        after = snap(conn, cid)
        assert {r[1] for r in after if r[0] == ep.PREDICTOR_BY} == {"Revenues2", "GrossProfit"}
        assert [r for r in after if r[1] == "GrossProfit"] == [r for r in rows if r[1] == "GrossProfit"]

        # the guard: FY2021 proven, FY2022 disagrees, FY2023 has no proof
        conn.execute(
            "insert into analytics.cell_proof (company_id, data_point_name, period_grain, period_start, period_end, shown_value, "
            "position_value, position_is_expected_line, verdict, detector_version) values (%s, 'revenue_sanity_resolved', 'FY', "
            "'2021-01-01', '2021-12-31', 1, 1, true, 'PROVEN', 't')", (cid,))
        conn.execute(
            "insert into analytics.cell_proof (company_id, data_point_name, period_grain, period_start, period_end, "
            "verdict, reason_code, detector_version) values (%s, 'revenue_sanity_resolved', 'FY', '2022-01-01', '2022-12-31', "
            "'DISAGREE', 'value_mismatch', 't')", (cid,))
        conn.commit()
        rep = eg.hold_unproven(conn, [cid])
        assert (rep["slices"], rep["kept"], rep["held"]) == (6, 1, 5)  # gross_profit has no proof at all: held too
        assert snap(conn, cid) == after  # report only
        rep = eg.hold_unproven(conn, [cid], apply=True)
        final = snap(conn, cid)
        assert ("tag_expert_predictor", "Revenues2", "2021-01-01", "2021-12-31", "concept", None) in final
        held = [r for r in final if r[0] == eg.GUARD_BY]
        assert len(held) == 5 and {r[4:] for r in held} == {("not_presented", "era_unmapped")}
        assert not [r for r in final if r[0] == ep.PREDICTOR_BY and r[2] != "2021-01-01" and r[1] == "Revenues2"]
        # reloading the revenue predictor rows removes its guard rows too (the guard runs again afterwards)
        dl.load(conn, paths, apply=True, predictor_eras=eras, predictor_concepts={"revenue"})
        again = snap(conn, cid)
        assert [r for r in again if r[0] == eg.GUARD_BY and r[1] is None]  # gross_profit's holds stay
        assert len([r for r in again if r[0] == ep.PREDICTOR_BY and r[1] == "Revenues2"]) == 3
        # no-filing company: reasoned blanks before the listing
        dl.load(conn, paths, apply=True, no_filing_ciks={"77"})
        nf = [r for r in snap(conn, cid) if r[5] == ep.NO_FILING_REASON]
        assert nf and nf[0][2] == "2015-01-01"
