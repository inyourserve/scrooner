"""The FSN done gate per (company, data point): ruling RULING-DONE-GATE-C4-2026-11-09 (Ritwik, 2026-11-09),
conditions C1 (unit = pair, all or nothing, rule (c): an empty pair never passes), C2 (hold guard), C4 (cell_proof
scope), C6/C8 (data points that stay out), and the write filter that keeps only done pairs."""

import csv
import gzip
import json
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from scrooner_pipeline.fsn_store import pilot

ROOT = Path(__file__).resolve().parents[3]
FILTER = ROOT / "pipeline" / "scripts" / "fsn_write_filter.py"
REV, NI, SHR = (
    "revenue_sanity_resolved",
    "net_income_resolved",
    "shares_outstanding_resolved",
)


def rep(cid, cik, per_point, loaded=True, derived=None):
    return {
        "company_id": cid,
        "cik": cik,
        "done_criteria": {
            "1_store_loaded": loaded,
            "5_derived_without_same_basis_by_point": derived or {},
        },
        "template_coverage": {"per_data_point": per_point},
    }


FULL = {"keys": 8, "valued": 6, "reasoned": 2}


@pytest.mark.unit
def test_every_listed_pair_of_a_passing_company_is_written_and_no_pair_keeps_old_rows():
    """No fallback (founder 2026-11-09): a reasonless gap key no longer holds a pair back (it is written as a blank),
    so every in-template data point of the list is written for a company passing criteria 1/2/5; the loader
    replaces each written pair whole, so no old-mapper row of those pairs survives."""
    gate = pilot.done_gate(
        [rep(1, "A", {REV: FULL, NI: {"keys": 8, "valued": 7}, SHR: {"keys": 8}})],
        [{"company_id": "1", "data_point": NI}]
        + [{"company_id": "1", "data_point": SHR}] * 8,
        {},
        {REV, NI, SHR},
    )
    assert pilot.done_pairs(gate) == [(1, NI), (1, REV), (1, SHR)]
    assert gate[1]["gap_blanks"] == {NI: 1, SHR: 8}
    assert pilot.fully_done(gate) == [1]


@pytest.mark.unit
def test_a_pair_with_no_expected_key_is_not_written_and_listed():
    gate = pilot.done_gate(
        [rep(1, "A", {REV: FULL, SHR: {"keys": 0}})], [], {}, {REV, SHR}
    )
    assert pilot.done_pairs(gate) == [(1, REV)]
    assert gate[1]["data_points"][SHR] == ["no_expected_keys"]


@pytest.mark.unit
def test_a_company_failing_criterion_2_writes_nothing():
    gate = pilot.done_gate(
        [rep(1, "A", {REV: FULL, NI: FULL}), rep(2, "B", {REV: FULL, NI: FULL})],
        [],
        {"A": [{"accession": "0000000001-24-000001"}]},
        {REV, NI},
    )
    assert pilot.done_pairs(gate) == [(2, NI), (2, REV)]
    assert gate[1]["company"] == ["2_filings_not_stored:1"]
    assert all(
        f == ["company:2_filings_not_stored:1"] for f in gate[1]["data_points"].values()
    )
    assert pilot.fully_done(gate) == [2]


@pytest.mark.unit
def test_a_point_outside_the_company_template_is_not_written_and_does_not_fail_the_company():
    gate = pilot.done_gate([rep(1, "A", {REV: FULL})], [], {}, {REV, NI})
    assert pilot.done_pairs(gate) == [(1, REV)]
    assert gate[1]["out_of_template"] == [NI]
    assert pilot.fully_done(gate) == [1]


def _filing(fid, period):
    from datetime import datetime

    from scrooner_pipeline.fsn_store import select as sel

    return sel.Filing(
        fid,
        f"0000000001-24-{fid:06d}",
        datetime(2024, 1, 1),
        "10-Q",
        period,
        period.year,
        "Q2",
        "1231",
    )


@pytest.mark.unit
def test_a_reasonless_gap_becomes_a_reasoned_blank_that_passes_the_cell_contract():
    """hybrid_gap_unresolved when the period's filing is stored (cause kept in input_refs, defect class by cause);
    filing_not_in_store when no stored filing has that period. Both pass cell_loader.parse_row."""
    from datetime import date

    from scrooner_pipeline.fsn_store import select as sel
    from scrooner_pipeline.normalizer import cell_loader

    filings = {7: _filing(7, date(2024, 6, 30))}
    stored = pilot.gap_blank(REV, "Q", date(2024, 6, 30), "no_mapped_line", filings)
    assert stored.state == "defect" and stored.reason_code == "hybrid_gap_unresolved"
    assert stored.input_refs["pilot_cause"] == "no_mapped_line"
    missing = pilot.gap_blank(
        REV, "Q", date(2024, 9, 30), "quarter_not_printed_or_derivable", filings
    )
    assert missing.reason_code == "filing_not_in_store"
    # Kroger-style mid-month end: the key carries the FSN month-end date, and the stored filing is recognised
    kroger = {8: _filing(8, date(2015, 7, 31))}
    mid = pilot.gap_blank(
        REV, "Q", date(2015, 8, 15), "no_face_print_for_period", kroger
    )
    assert mid.reason_code == "hybrid_gap_unresolved" and mid.ddate == date(2015, 7, 31)
    for cell, cls in (
        (stored, "vocabulary"),
        (missing, "ingestion"),
        (mid, "unclassified"),
    ):
        row = json.loads(
            json.dumps(sel.to_row(cell, 1, {**filings, **kroger}), default=str)
        )
        assert row["defect_class"] == cls and row["reason_text"]
        parsed = cell_loader.parse_row(1, row, {REV})
        assert not isinstance(parsed, str), (parsed, row)
        assert parsed.state == "defect"


def _cell(cid, dp, grain, end, state="value", reason=None):
    return {
        "company_id": cid,
        "data_point_name": dp,
        "period_grain": grain,
        "fsn_end": end,
        "state": state,
        "reason_code": reason,
    }


CONCEPTS = {"10": REV, "11": NI}
PERIODS = {
    "1": {
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "period_type": "duration",
    },
    "2": {
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "period_type": "duration",
    },
    "3": {
        "start_date": "2024-04-01",
        "end_date": "2024-06-30",
        "period_type": "duration",
    },
    "9": {
        "start_date": "2012-01-01",
        "end_date": "2012-12-31",
        "period_type": "duration",
    },
}


@pytest.mark.unit
def test_c2_report_lists_pairs_losing_every_value_and_transitions_by_reason():
    before = [
        {
            "company_id": "1",
            "canonical_concept_id": "10",
            "period_id": "1",
            "value": "100",
        },
        {
            "company_id": "1",
            "canonical_concept_id": "10",
            "period_id": "2",
            "value": "30",
        },
        {
            "company_id": "1",
            "canonical_concept_id": "10",
            "period_id": "3",
            "value": "31",
        },
        {
            "company_id": "1",
            "canonical_concept_id": "11",
            "period_id": "1",
            "value": "7",
        },
        {
            "company_id": "1",
            "canonical_concept_id": "11",
            "period_id": "9",
            "value": "5",
        },  # before the floor
        {
            "company_id": "2",
            "canonical_concept_id": "11",
            "period_id": "9",
            "value": "5",
        },  # only before the floor
    ]
    cells = [
        _cell(1, REV, "FY", "2023-12-31"),
        _cell(
            1,
            REV,
            "Q",
            "2024-03-30",
            state="not_presented",
            reason="not_filed_separately",
        ),
        # Q2 2024 revenue has no new cell: the pair's rows are replaced, so the old value would be lost
        _cell(
            1,
            NI,
            "FY",
            "2023-12-31",
            state="not_presented",
            reason="balance_sheet_not_filed",
        ),
    ]
    held, transitions, no_row = pilot.hold_guard(
        cells, before, CONCEPTS, PERIODS, {REV, NI}
    )
    assert held == {
        (1, NI): "0_new_values_vs_1_before"
    }  # revenue keeps one value: not held
    assert transitions == {
        REV: {"valued": 1, "not_filed_separately": 1, "no_new_cell": 1},
        NI: {"balance_sheet_not_filed": 1},
    }
    assert [(k["company_id"], k["data_point"], k["end"], k["why"]) for k in no_row] == [
        (1, REV, "2024-06-30", "no_new_cell")
    ]


@pytest.mark.unit
def test_a_6_or_9_month_value_is_never_matched_by_the_quarter_ending_that_day():
    # MDT 2026-11-09: the old 9-month and 6-month rows were deleted while the gate counted them as kept
    periods = {
        "q3": {"start_date": "2024-07-01", "end_date": "2024-09-30", "period_type": "duration"},
        "9m": {"start_date": "2024-01-01", "end_date": "2024-09-30", "period_type": "duration"},
        "h1": {"start_date": "2024-01-01", "end_date": "2024-06-30", "period_type": "duration"},
        "3y": {"start_date": "2021-01-01", "end_date": "2023-12-31", "period_type": "duration"},
    }  # fmt: skip
    before = [
        {"company_id": "1", "canonical_concept_id": "10", "period_id": p, "value": "9"}
        for p in periods
    ]
    cells = [
        _cell(1, REV, "Q", "2024-09-30"),
        _cell(1, REV, "Q", "2024-06-30"),
    ]
    held, transitions, no_row = pilot.hold_guard(
        cells, before, CONCEPTS, periods, {REV}
    )
    assert held == {}
    # no TP cell for the 9-month, 6-month and 3-year keys (CELL-FORMAT v1.2): each is valued->no-row
    assert transitions == {REV: {"valued": 1, "no_new_cell": 3}}
    assert sorted(k["period_id"] for k in no_row) == ["3y", "9m", "h1"]
    gate = {1: {"data_points": {REV: [], NI: []}}}
    # founder 2026-11-11 "move to the new system": counted as the old-vs-new diff, never a hold
    assert pilot.count_valued_to_no_row(no_row) == {(1, REV): 3}
    assert gate[1]["data_points"] == {REV: [], NI: []}
    assert pilot.done_pairs(gate) == [(1, NI), (1, REV)]  # both written; the 3 old keys are the diff


YTD_PERIODS = {
    "q2": {"start_date": "2024-04-01", "end_date": "2024-06-30", "period_type": "duration"},
    "h1": {"start_date": "2024-01-01", "end_date": "2024-06-30", "period_type": "duration"},
    "9m": {"start_date": "2024-01-01", "end_date": "2024-09-30", "period_type": "duration"},
    "3y": {"start_date": "2021-10-01", "end_date": "2024-09-30", "period_type": "duration"},
}  # fmt: skip


def _tp(cid, dp, end, qtrs, state="value", reason=None, start=None):
    """A TP cell row the way select.to_row writes it: FSN end + qtrs, or exact dates for a before-image blank."""
    return dict(
        _cell(cid, dp, "TP", end, state, reason),
        qtrs=qtrs,
        period_start=start,
        period_end=end if start else None,
    )


@pytest.mark.unit
def test_hold_guard_counts_a_tp_written_ytd_key_as_valued_to_valued():
    """CELL-FORMAT v1.2: a before-image 9-month (or 6-month) key is matched by the TP cell of its own class and end,
    never by the quarter or the other YTD length ending that day; an exact-dated TP blank matches only its start."""
    before = [
        {"company_id": "1", "canonical_concept_id": "10", "period_id": p, "value": "9"}
        for p in YTD_PERIODS
    ]
    cells = [
        _cell(1, REV, "Q", "2024-06-30"),
        _tp(1, REV, "2024-06-30", 2),
        _tp(1, REV, "2024-09-30", 3),
        # a multi-year blank at the same end but another start must not stand for the 3-year key
        _tp(
            1,
            REV,
            "2024-09-30",
            9,
            "defect",
            "hybrid_gap_unresolved",
            start="2022-07-01",
        ),
    ]
    held, transitions, no_row = pilot.hold_guard(
        cells, before, CONCEPTS, YTD_PERIODS, {REV}
    )
    assert held == {}
    assert transitions == {REV: {"valued": 3, "no_new_cell": 1}}
    assert [k["period_id"] for k in no_row] == ["3y"]
    exact = _tp(
        1, REV, "2024-09-30", 12, "defect", "hybrid_gap_unresolved", start="2021-10-01"
    )
    _held, transitions, no_row = pilot.hold_guard(
        cells + [exact], before, CONCEPTS, YTD_PERIODS, {REV}
    )
    assert (
        transitions == {REV: {"valued": 3, "hybrid_gap_unresolved": 1}} and no_row == []
    )


def _store_report(cid, missing=()):
    return dict(
        rep(cid, "A", {REV: FULL, NI: FULL}),
        library={"missing": list(missing)},
        store_filings=[
            {"id": 7, "accession": "0000000001-24-000007", "accepted": "2024-08-01T12:00:00", "form": "10-Q",
             "period": "2024-06-30", "fy": 2024, "fp": "Q2", "fye": "1231"},
        ],
    )  # fmt: skip


@pytest.mark.unit
def test_an_unprinted_ytd_key_becomes_a_hybrid_gap_defect_blank_with_exact_dates():
    from datetime import date

    from scrooner_pipeline.fsn_store import select as sel

    """CELL-FORMAT v1.2: a before-image 6/9-month key with no TP cell is a defect blank under the gap_blank
    conventions (N1): hybrid_gap_unresolved when the period's filing is stored (accession in input_refs), else
    filing_not_in_store; a mapped point's unprinted key is period / period_engineer and an unmapped one vocabulary /
    tag_mapper (ruling 2026-11-10 item 2). A multi-year key is not_in_template with no class or owner (item 1).
    Exact dates; every row passes the loader's row check."""
    from scrooner_pipeline.normalizer import cell_loader

    before = [
        {"company_id": "1", "canonical_concept_id": cc, "period_id": p, "value": "9"}
        for cc in ("10", "11")
        for p in ("h1", "9m", "3y")
    ]
    cells = [
        _tp(1, REV, "2024-09-30", 3)
    ]  # revenue's 9 months is printed; nothing else is
    rows, skipped = pilot.ytd_gap_blanks(
        cells,
        before,
        CONCEPTS,
        YTD_PERIODS,
        {REV, NI},
        [_store_report(1, missing=[NI])],
    )
    assert skipped == []
    got = {(r["data_point_name"], r["period_start"], r["period_end"]): r for r in rows}
    assert set(got) == {
        (REV, "2024-01-01", "2024-06-30"),
        (REV, "2021-10-01", "2024-09-30"),
        (NI, "2024-01-01", "2024-06-30"),
        (NI, "2024-01-01", "2024-09-30"),
        (NI, "2021-10-01", "2024-09-30"),
    }
    h1 = got[(REV, "2024-01-01", "2024-06-30")]
    assert (h1["period_grain"], h1["qtrs"], h1["state"], h1["reason_code"]) == (
        "TP",
        2,
        "defect",
        "hybrid_gap_unresolved",
    )
    assert (h1["defect_class"], h1["owner"]) == ("period", "period_engineer")
    assert h1["input_refs"]["accession"] == h1["accession"] == "0000000001-24-000007"
    assert (
        h1["input_refs"]["pilot_cause"] == "no_face_print_for_period"
        and h1["value"] is None
    )
    ni = got[(NI, "2024-01-01", "2024-06-30")]
    assert (ni["defect_class"], ni["owner"]) == (
        "vocabulary",
        "tag_mapper",
    )  # no mapped line
    # the v1 grains keep their column length: an instant gap is qtrs 0 (CI 42783704321 caught qtrs 0 read as "none")
    from datetime import date

    inst = pilot.gap_blank(
        "total_assets_resolved", "I", date(2024, 6, 30), "no_face_print_for_period",
        {7: _filing(7, date(2024, 6, 30))},
    )  # fmt: skip
    assert (inst.qtrs, inst.grain, inst.start) == (0, "I", None)
    # the same cause on a Q key keeps the N1 class
    q = sel.to_row(
        pilot.gap_blank(REV, "Q", date(2024, 6, 30), "no_face_print_for_period", {7: _filing(7, date(2024, 6, 30))}),
        1, {7: _filing(7, date(2024, 6, 30))},
    )  # fmt: skip
    assert (q["defect_class"], q["owner"]) == ("unclassified", "triage")
    multi = got[(REV, "2021-10-01", "2024-09-30")]
    assert (multi["period_grain"], multi["state"], multi["reason_code"], multi["reason_text"]) == (
        "TP", "not_in_template", "period_grain_outside_template", "period grain outside template: multi-year",
    )  # fmt: skip
    assert multi["qtrs"] >= 5 and "defect_class" not in multi and "owner" not in multi
    assert got[(NI, "2024-01-01", "2024-09-30")]["reason_code"] == "filing_not_in_store"
    for r in rows:
        parsed = cell_loader.parse_row(
            1, json.loads(json.dumps(r, default=str)), {REV, NI}
        )
        assert not isinstance(parsed, str), (parsed, r)
        assert parsed.exact_dates and parsed.key.period_grain == "TP"
    # with the blanks the guard sees every YTD key as reasoned: nothing is valued->no-row
    _held, transitions, no_row = pilot.hold_guard(
        cells + rows, before, CONCEPTS, YTD_PERIODS, {REV, NI}
    )
    listed: list = []
    _held, transitions, no_row = pilot.hold_guard(
        cells + rows, before, CONCEPTS, YTD_PERIODS, {REV, NI}, listed
    )
    assert no_row == [] and transitions[REV] == {
        "valued": 1,
        "hybrid_gap_unresolved": 1,
        "period_grain_outside_template": 1,
    }
    assert sorted((k["data_point"], k["period_id"]) for k in listed) == [
        (NI, "3y"),
        (REV, "3y"),
    ]
    # a YTD key inside an excluded wrong-entity window with no stored filing: the history horizon blank (main)
    hist = dict(
        _store_report(1),
        history_windows={"exclude": [["2024-07-01", "2024-12-31"]], "predecessor": []},
    )
    hrows, _ = pilot.ytd_gap_blanks(
        [], before[:3], CONCEPTS, YTD_PERIODS, {REV}, [hist]
    )
    nine = next(
        r
        for r in hrows
        if r["period_start"] == "2024-01-01" and r["period_end"] == "2024-09-30"
    )
    assert (nine["state"], nine["reason_code"]) == (
        "history_horizon",
        "no_public_filing_for_period",
    )
    # idempotent: a second pass finds the blanks and adds nothing; no stored filings in the report -> no blank
    assert pilot.ytd_gap_blanks(
        cells + rows, before, CONCEPTS, YTD_PERIODS, {REV, NI}, [_store_report(1)]
    ) == ([], [])
    none, skipped = pilot.ytd_gap_blanks(
        cells, before, CONCEPTS, YTD_PERIODS, {REV}, [rep(1, "A", {REV: FULL})]
    )
    assert none == [] and {k["why"] for k in skipped} == {"no_store_filings_in_report"}


@pytest.mark.unit
def test_done_gate_command_writes_unprinted_ytd_keys_as_blanks_and_writes_the_pair(
    tmp_path,
):
    from scrooner_pipeline.jobs import fsn as fsn_job

    before = [
        {"company_id": "1", "canonical_concept_id": "10", "period_id": p, "value": "9"}
        for p in ("q2", "h1", "3y")
    ]
    cells = [
        _cell(1, REV, "Q", "2024-06-30"),
        _cell(1, NI, "Q", "2024-06-30"),
        _tp(1, NI, "2024-09-30", 3),  # binds to the 9-month period
        _tp(
            1, NI, "2023-06-30", 2
        ),  # no 6-month period ends there: the loader will reject it (item 3)
    ]
    out = _out_dir(tmp_path, [_store_report(1)], cells, before, periods=YTD_PERIODS)
    args = ["done-gate", "--pilot-out", str(out), "--data-points", f"{REV},{NI}"]
    res = CliRunner().invoke(fsn_job.app, args)
    assert res.exit_code == 0, res.output + repr(res.exception)
    assert (
        "2 before-image year-to-date keys with nothing printed added as TP blanks"
        in res.output
    )
    assert "valued->no-row in written pairs: 0" in res.output
    assert (out / "done_pairs.tsv").read_text().splitlines()[1:] == [
        f"1\t{NI}",
        f"1\t{REV}",
    ]
    with gzip.open(out / "cells" / "is_core" / "cells.jsonl.gz", "rt") as fh:
        added = [json.loads(line) for line in fh]
    assert [
        (r["period_grain"], r["period_start"], r["period_end"], r["reason_code"])
        for r in added
    ] == [
        ("TP", "2024-01-01", "2024-06-30", "hybrid_gap_unresolved"),
        ("TP", "2021-10-01", "2024-09-30", "period_grain_outside_template"),
    ]
    report = json.loads((out / "valued_to_blank.json").read_text())
    # item 1: the multi-year key in its own column; item 3: TP prints the loader will reject, per company
    assert report["valued_to_not_in_template_by_data_point"] == {REV: 1}
    assert report["valued_to_not_in_template_by_pair"] == [
        {"company_id": 1, "data_point": REV, "keys": 1}
    ]
    assert report["tp_rejected_by_company"] == {
        "1": {"tp_prints": 2, "period_unresolvable": 1, "rejected": 1, "share": 0.5}
    }
    assert report["tp_rejected_share"] == 0.5
    assert (
        "TP prints the loader will reject: 1 of 2; 1 companies above 0.5%" in res.output
    )
    assert report["ytd_keys_written_as_blanks_by_data_point"] == {REV: 2}
    assert report["valued_to_no_row_by_pair"] == []
    # a second run adds nothing
    res = CliRunner().invoke(fsn_job.app, args)
    assert "0 before-image year-to-date keys" in res.output


def _out_dir(tmp_path, reports, cells, before, gaps=(), periods=None):
    out = tmp_path / "out"
    (out / "before_image").mkdir(parents=True)
    (out / "report.json").write_text(json.dumps(reports))
    (out / "missing_filings.json").write_text(json.dumps({}))
    with (out / "gaps.csv").open("w", newline="") as fh:
        w = csv.DictWriter(
            fh, ["cik", "company_id", "data_point", "grain", "period_end", "cause"]
        )
        w.writeheader()
        w.writerows(gaps)

    def gz(name, header, rows):
        with gzip.open(out / "before_image" / f"{name}.csv.gz", "wt", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)

    gz(
        "canonical_fact",
        ["company_id", "canonical_concept_id", "period_id", "value"],
        [
            [b["company_id"], b["canonical_concept_id"], b["period_id"], b["value"]]
            for b in before
        ],
    )
    gz("canonical_concept", ["id", "name"], [[k, v] for k, v in CONCEPTS.items()])
    gz(
        "period",
        ["id", "company_id", "start_date", "end_date", "period_type"],
        [
            [
                k,
                v.get("company_id", "1"),
                v["start_date"],
                v["end_date"],
                v["period_type"],
            ]
            for k, v in (periods or PERIODS).items()
        ],
    )
    (out / "cells" / "income").mkdir(parents=True)
    with gzip.open(out / "cells" / "income" / "cells.jsonl.gz", "wt") as fh:
        for c in cells:
            fh.write(json.dumps(c) + "\n")
    return out


@pytest.mark.unit
def test_done_gate_command_writes_pairs_proof_scope_and_the_c2_report(tmp_path):
    from scrooner_pipeline.jobs import fsn as fsn_job

    reports = [
        rep(1, "A", {REV: FULL, NI: FULL}),
        rep(2, "B", {REV: FULL, NI: FULL}),
        rep(3, "C", {REV: FULL, NI: FULL}, loaded=False),
    ]
    before = [
        {
            "company_id": "2",
            "canonical_concept_id": "11",
            "period_id": "1",
            "value": "7",
        }
    ]
    cells = [
        _cell(c, dp, "FY", "2023-12-31")
        for c in (1, 2, 3)
        for dp in (REV, NI)
        if (c, dp) != (2, NI)
    ]
    out = _out_dir(tmp_path, reports, cells, before)
    res = CliRunner().invoke(
        fsn_job.app,
        ["done-gate", "--pilot-out", str(out), "--data-points", f"{REV},{NI}"],
    )
    assert res.exit_code == 0, res.output + repr(res.exception)
    # companies 1 and 2: both pairs. Company 2's net income drops its old FY 2023 value with no new row: since
    # the founder's 2026-11-11 "move to the new system" that is the old-vs-new diff (reported), not a hold.
    # Company 3: criterion 1 fails
    assert "4 pairs of 6; 2 companies fully done" in res.output
    assert "valued->no-row in written pairs: 1" in res.output
    pairs = (out / "done_pairs.tsv").read_text().splitlines()
    assert pairs == [
        "company_id\tdata_point",
        f"1\t{NI}",
        f"1\t{REV}",
        f"2\t{NI}",
        f"2\t{REV}",
    ]
    assert (out / "done_companies.txt").read_text().split() == ["1", "2"]
    assert (out / "written_companies.txt").read_text().split() == [
        "1",
        "2",
    ]  # C4: cell_proof scope
    report = json.loads((out / "valued_to_blank.json").read_text())
    # C2 is a report: company 2's net income had a value and has no new cell; it is listed, not held
    assert report["pairs_with_no_new_value_but_old_values"] == [
        {"company_id": 2, "data_point": NI, "why": "0_new_values_vs_1_before"}
    ]
    assert report["valued_to_blank_by_data_point"] == {NI: {"no_new_cell": 1}}
    assert report["valued_to_no_row_by_pair"] == [
        {"company_id": 2, "data_point": NI, "keys": 1}
    ]
    assert report["valued_to_no_row_in_written_pairs"] == 1
    rows = (out / "valued_to_no_row.tsv").read_text().splitlines()
    assert rows[1].split("\t")[:4] == ["2", NI, "1", "FY"]
    not_done = json.loads((out / "not_done.json").read_text())
    assert set(not_done) == {"3"}


@pytest.mark.unit
def test_done_gate_command_refuses_held_out_points_and_a_missing_before_image(tmp_path):
    from scrooner_pipeline.jobs import fsn as fsn_job

    out = _out_dir(
        tmp_path, [rep(1, "A", {REV: FULL})], [_cell(1, REV, "FY", "2023-12-31")], []
    )
    for dp in (
        "dividends_per_share_resolved",
        "total_debt_resolved",
        "total_liabilities_resolved",
        "shares_outstanding_resolved",
    ):
        res = CliRunner().invoke(
            fsn_job.app,
            ["done-gate", "--pilot-out", str(out), "--data-points", f"{REV},{dp}"],
        )
        assert res.exit_code != 0 and "stays out" in res.output, dp
    (out / "before_image" / "period.csv.gz").unlink()
    res = CliRunner().invoke(
        fsn_job.app, ["done-gate", "--pilot-out", str(out), "--data-points", REV]
    )
    assert res.exit_code != 0 and "pilot-prod" in res.output


@pytest.mark.unit
def test_write_filter_keeps_only_done_pairs(tmp_path):
    """Run the way the workflow runs it. Every row of a done pair is kept (all or nothing), none of another pair."""
    src = tmp_path / "cells" / "income" / "cells.jsonl.gz"
    src.parent.mkdir(parents=True)
    rows = [
        _cell(1, REV, "FY", "2023-12-31"),
        _cell(1, REV, "Q", "2024-03-31", state="not_presented", reason="x"),
        _cell(1, NI, "FY", "2023-12-31"),  # company 1 net income: not a done pair
        _cell(2, NI, "FY", "2023-12-31"),
        _cell(
            2, "dividends_per_share_resolved", "FY", "2023-12-31"
        ),  # not in the dispatched list
        dict(
            _cell(2, "operating_income_resolved", "FY", "2023-12-31"),
            input_refs={"source": "note"},
        ),
    ]
    with gzip.open(src, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    pairs = tmp_path / "done_pairs.tsv"
    pairs.write_text(
        f"company_id\tdata_point\n1\t{REV}\n2\t{NI}\n2\tdividends_per_share_resolved\n2\toperating_income_resolved\n"
    )
    dst = tmp_path / "write" / "income" / "cells.jsonl.gz"
    dst.parent.mkdir(parents=True)
    r = subprocess.run(
        [
            sys.executable,
            str(FILTER),
            str(src),
            str(dst),
            f"{REV},{NI},operating_income_resolved",
            str(pairs),
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert r.returncode == 0, r.stderr
    kept = [json.loads(line) for line in gzip.open(dst, "rt")]
    assert sorted(
        (k["company_id"], k["data_point_name"], k["period_grain"]) for k in kept
    ) == [(1, REV, "FY"), (1, REV, "Q"), (2, NI, "FY")]
    manifest = json.loads((dst.parent / "manifest.json").read_text())
    assert manifest["rows"] == 3 and manifest["pairs"] == 2


@pytest.mark.unit
def test_the_workflow_filters_by_done_pairs_and_keeps_the_held_out_points_out_of_its_default():
    wf = (ROOT / ".github" / "workflows" / "pipeline-fsn-write.yml").read_text()
    assert "fsn_write_filter.py" in wf and "out/done_pairs.tsv" in wf
    default = wf.split("data_points:", 1)[1].split("default:", 1)[1].split("\n", 1)[0]
    for dp in (
        "dividends_per_share_resolved",
        "total_debt_resolved",
        "total_liabilities_resolved",
    ):
        assert dp not in default, dp
    for f in (
        "out/done_pairs.tsv",
        "out/written_companies.txt",
        "out/valued_to_blank.json",
    ):
        assert f in wf, f


@pytest.fixture
def conn(isolated_database_url):
    import psycopg

    c = psycopg.connect(isolated_database_url)
    yield c
    c.close()


@pytest.mark.integration
def test_report_company_writes_every_gap_key_as_a_reasoned_blank(conn, tmp_path):
    """JPM's FY2023 10-K alone in the store, against a calendar asking for FY2016-FY2023: the years no stored filing
    reports become filing_not_in_store blanks; a stored year the hybrid cannot fill becomes hybrid_gap_unresolved.
    Every gap key is in _cells, so a written pair carries all its keys and no old row survives."""
    from datetime import date

    from scrooner_pipeline.fsn_store import load, mapping, rules
    from scrooner_pipeline.normalizer import cell_loader

    fx = ROOT / "pipeline" / "tests" / "fixtures" / "fsn_cf_detectors" / "0000019617"
    seeds = sorted(
        p
        for p in (ROOT / "data-team" / "47-fsn-store" / "concept_rules").glob("*.jsonl")
        if not p.name.startswith("_")
    )
    stmt = {"BS": "balance_sheet", "IS": "income_statement", "CF": "cash_flow"}
    for p in seeds:
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                for c in [
                    r["canonical_concept"],
                    *(r.get("components") or []),
                    (r.get("position") or {}).get("anchor_concept"),
                ]:
                    if c:
                        conn.execute(
                            "insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, %s, 'first_match') on conflict (name) do nothing",
                            (c, stmt[r["stmt"]]),
                        )
    cid = conn.execute(
        "insert into core.company (cik, company_name, sic_code) values ('0000019617', 'JPM TEST', '6021') returning id"
    ).fetchone()[0]
    conn.commit()
    for p in seeds:
        assert not rules.seed(conn, p, apply=True)["errors"]
    load.load_company(conn, fx, loader_commit="test")
    conn.commit()
    mapping.map_company(conn, cid, mapping.load_rules(conn))
    from scrooner_pipeline.fsn_store import checks

    checks.check_company(conn, cid)
    conn.commit()
    cal = tmp_path / "cal.csv.gz"
    with gzip.open(cal, "wt", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "company_id",
                "cik",
                "fiscal_year",
                "fiscal_period",
                "period_type",
                "period_start",
                "period_end",
            ]
        )
        for y in range(2016, 2024):
            w.writerow(
                [cid, "0000019617", y, "FY", "duration", f"{y}-01-01", f"{y}-12-31"]
            )
            w.writerow(
                [cid, "0000019617", y, "FY", "instant", f"{y}-12-31", f"{y}-12-31"]
            )
    rule_concepts = {
        r[0]
        for r in conn.execute(
            "select distinct cc.name from fsn.concept_rule r join analytics.canonical_concept cc on cc.id = r.canonical_concept_id"
        )
    }
    rep = pilot.report_company(conn, cid, cal, rule_concepts)
    gaps = rep["_gaps"]
    assert gaps, "the calendar asks for years the store does not hold"
    blanks = {
        (
            c["data_point_name"],
            c["period_grain"],
            c["input_refs"].get("expected_end"),
        ): c
        for c in rep["_cells"]
        if c.get("rule_id") == pilot.RULE_GAP_BLANK
    }
    for g in gaps:  # every gap key is written as a reasoned blank
        c = blanks[(g["data_point"], g["grain"], g["period_end"])]
        assert c["state"] == "defect" and c["reason_code"] == g["written_as"]
        assert c["input_refs"]["pilot_cause"] == g["cause"]
        assert not isinstance(
            cell_loader.parse_row(
                1, json.loads(json.dumps(c, default=str)), {c["data_point_name"]}
            ),
            str,
        )
    reasons = {g["written_as"] for g in gaps}
    assert (
        "filing_not_in_store" in reasons
    )  # FY2016-FY2020: no stored filing reports those years
    assert all(
        g["written_as"] == "filing_not_in_store"
        for g in gaps
        if date.fromisoformat(g["period_end"]) < date(2021, 1, 1)
    )


@pytest.mark.unit
def test_n1_each_pilot_cause_maps_to_a_valid_defect_and_a_defect_without_class_is_refused():
    """Ruling addendum N1: state defect (never not_presented), filing_not_in_store -> ingestion /
    data_engineer_l1, hybrid_gap_unresolved -> the class of its pilot cause (period / period_engineer,
    vocabulary / tag_mapper, otherwise unclassified / triage), reason_text carries the cause, input_refs the
    accession where one exists."""
    from datetime import date

    from scrooner_pipeline.common.cell_contract import validate_defect
    from scrooner_pipeline.fsn_store import select as sel
    from scrooner_pipeline.normalizer import cell_loader

    filings = {7: _filing(7, date(2024, 6, 30))}
    want = {
        "no_mapped_line": ("vocabulary", "tag_mapper"),
        "no_mapped_line_cond": ("vocabulary", "tag_mapper"),
        "no_concept_rule": ("vocabulary", "tag_mapper"),
        "quarter_not_printed_or_derivable": ("period", "period_engineer"),
        "no_face_print_for_period": ("unclassified", "triage"),
        "sector_row_definition_pending": ("unclassified", "triage"),
    }
    for cause, (cls, owner) in want.items():
        row = sel.to_row(
            pilot.gap_blank(REV, "Q", date(2024, 6, 30), cause, filings), 1, filings
        )
        assert (row["state"], row["defect_class"], row["owner"]) == (
            "defect",
            cls,
            owner,
        ), cause
        validate_defect(
            row["state"], row["defect_class"], row["owner"], row["root_cause_class"]
        )
        assert (
            cause in row["reason_text"]
            and row["input_refs"]["accession"]
            == row["accession"]
            == filings[7].accession
        )
    missing = sel.to_row(
        pilot.gap_blank(REV, "Q", date(2024, 9, 30), "no_mapped_line", filings),
        1,
        filings,
    )
    assert (missing["reason_code"], missing["defect_class"], missing["owner"]) == (
        "filing_not_in_store",
        "ingestion",
        "data_engineer_l1",
    )
    assert "accession" not in missing["input_refs"] and missing["accession"] is None
    bare = json.loads(
        json.dumps(
            dict(missing, defect_class=None, owner=None, root_cause_class=None),
            default=str,
        )
    )
    assert cell_loader.parse_row(1, bare, {REV}) == "defect_fields_inconsistent"


def _w(cid, dp, grain, end, value="10", state="value"):
    return {
        "company_id": cid,
        "data_point_name": dp,
        "period_grain": grain,
        "fsn_end": end,
        "state": state,
        "value": value,
        "unit": "USD",
        "rule_id": "fsn.select_printed@1",
        "source_value_ids": [1],
    }


@pytest.mark.unit
def test_n2_a_disagree_cell_becomes_a_blank_and_its_pair_is_reloaded_whole():
    """Ruling addendum N2: never the old value back. The DISAGREE key is a defect blank (identity / verifier,
    cell_proof_disagree); every other row of the same pair is reloaded unchanged (the loader replaces a pair
    whole); a pair without a DISAGREE is not touched; a DISAGREE matching no written cell is reported."""
    from datetime import date

    rows = [
        _w(1, REV, "FY", "2023-12-31", "100"),
        _w(
            1, REV, "Q", "2015-07-31", "25539"
        ),  # Kroger-style: the proof row has the true end 2015-08-15
        _w(1, NI, "FY", "2023-12-31", "7"),
        _w(2, REV, "FY", "2023-12-31", "9"),
    ]
    disagrees = [
        {
            "id": 41,
            "company_id": 1,
            "data_point_name": REV,
            "period_grain": "Q",
            "period_start": date(2015, 5, 24),
            "period_end": date(2015, 8, 15),
            "shown_value": 25539,
            "position_value": 25540,
            "reason_code": "position_differs",
            "rule_id": "proof.cell_proof@1",
        },
        {
            "id": 42,
            "company_id": 3,
            "data_point_name": REV,
            "period_grain": "FY",
            "period_start": date(2023, 1, 1),
            "period_end": date(2023, 12, 31),
            "shown_value": 1,
            "position_value": 2,
            "reason_code": "x",
            "rule_id": "proof.cell_proof@1",
        },
    ]
    out, unmatched = pilot.blank_disagreements(rows, disagrees)
    assert [
        (r["company_id"], r["data_point_name"], r["period_grain"]) for r in out
    ] == [(1, REV, "FY"), (1, REV, "Q")]
    fy, q = out
    assert (
        fy["state"] == "value" and fy["value"] == "100"
    )  # the rest of the pair, unchanged
    assert (
        q["state"],
        q["value"],
        q["defect_class"],
        q["owner"],
        q["reason_code"],
    ) == ("defect", None, "identity", "verifier", "cell_proof_disagree")
    assert (
        q["input_refs"]["cell_proof_id"] == 41
        and q["input_refs"]["replaced_value"] == "25539"
    )
    assert [d["id"] for d in unmatched] == [42]


@pytest.mark.integration
def test_proof_blank_command_reads_cell_proof_and_writes_whole_pairs(
    isolated_database_url, tmp_path, monkeypatch
):
    import psycopg

    from scrooner_pipeline.common.config import settings
    from scrooner_pipeline.jobs import fsn as fsn_job
    from scrooner_pipeline.normalizer import cell_loader

    with psycopg.connect(isolated_database_url) as c:
        cid = c.execute(
            "insert into core.company (cik, company_name) values ('0000000001', 'A') returning id"
        ).fetchone()[0]
        c.execute(
            """insert into analytics.cell_proof (company_id, data_point_name, period_grain, period_start, period_end,
                   shown_value, position_value, verdict, reason_code, detector_version)
               values (%s, %s, 'FY', '2023-01-01', '2023-12-31', 100, 90, 'DISAGREE', 'position_differs', 't'),
                      (%s, %s, 'FY', '2022-01-01', '2022-12-31', 80, 80, 'UNCHECKED', null, 't')""",
            (cid, REV, cid, REV),
        )
    monkeypatch.setattr(settings, "database_url", isolated_database_url)
    w = tmp_path / "write" / "income"
    w.mkdir(parents=True)
    rows = [
        dict(
            _w(cid, REV, "FY", "2023-12-31", "100"),
            fiscal_year=2023,
            fiscal_period="FY",
            period_type="duration",
            period_start=None,
            period_end=None,
            evidence_level="DATA-INFERRED",
            input_refs={},
        ),
        dict(
            _w(cid, REV, "FY", "2022-12-31", "80"),
            fiscal_year=2022,
            fiscal_period="FY",
            period_type="duration",
            period_start=None,
            period_end=None,
            evidence_level="DATA-INFERRED",
            input_refs={},
        ),
    ]
    with gzip.open(w / "cells.jsonl.gz", "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    out = tmp_path / "proof_blank"
    res = CliRunner().invoke(
        fsn_job.app,
        ["proof-blank", "--write-dir", str(tmp_path / "write"), "--out", str(out)],
    )
    assert res.exit_code == 0, res.output + repr(res.exception)
    got = [
        json.loads(line) for line in gzip.open(out / "income" / "cells.jsonl.gz", "rt")
    ]
    assert [(r["fsn_end"], r["state"]) for r in got] == [
        ("2023-12-31", "defect"),
        ("2022-12-31", "value"),
    ]
    assert json.loads((out / "summary.json").read_text())["families"]["income"] == {
        "rows_reloaded": 2,
        "cells_blanked": 1,
    }
    for r in got:  # both rows load
        assert not isinstance(cell_loader.parse_row(1, r, {REV}), str)
