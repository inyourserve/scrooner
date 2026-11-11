"""Ritwik G2 (REVIEW-DONE-GATE-PAIRS-2026-11-10) under the founder's "No fallback": a listed pair the done gate
does not write must not keep old-mapper values silently.
  (a) an out-of-template pair with old values -> `not_in_template` reason rows at the before-image keys;
  (b) an in-template `no_expected_keys` pair with old values -> `hybrid_gap_unresolved` defect blanks
      (cause `no_calendar_key`, unclassified / triage) at the before-image keys;
  a pair with a key no v1 cell grain can hold (6/9-month YTD) is held and listed instead (G3)."""

import csv
import gzip
import json

import pytest
from typer.testing import CliRunner

from scrooner_pipeline.fsn_store import pilot

GP, REV, NI = "gross_profit_resolved", "revenue_sanity_resolved", "net_income_resolved"
CONCEPTS = {"10": GP, "11": NI, "12": REV}
PERIODS = {
    "1": {"start_date": "2023-01-01", "end_date": "2023-12-31", "period_type": "duration"},  # FY
    "2": {"start_date": "2024-01-01", "end_date": "2024-03-31", "period_type": "duration"},  # Q
    "3": {"start_date": "2024-03-31", "end_date": "2024-03-31", "period_type": "instant"},  # I
    "4": {"start_date": "2024-01-01", "end_date": "2024-06-30", "period_type": "duration"},  # H1 YTD
    "5": {"start_date": "2012-01-01", "end_date": "2012-12-31", "period_type": "duration"},  # before the floor
}
FULL = {"keys": 8, "valued": 6, "reasoned": 2}


def rep(cid, per_point, loaded=True):
    return {
        "company_id": cid,
        "cik": f"C{cid}",
        "done_criteria": {"1_store_loaded": loaded, "5_derived_without_same_basis_by_point": {}},
        "template_coverage": {"per_data_point": per_point},
    }


def old(cid, concept_id, period_id, value="5"):
    return {"company_id": str(cid), "canonical_concept_id": concept_id, "period_id": period_id, "value": value}


def _run(reports, before, points=(GP, REV, NI), missing=None, cells=()):
    gate = pilot.done_gate(reports, [], missing or {}, set(points))
    rows, covered, held = pilot.no_fallback_rows(gate, before, CONCEPTS, PERIODS, set(points), list(cells))
    return gate, rows, covered, held


@pytest.mark.unit
def test_a_out_of_template_pair_with_old_values_is_written_as_not_in_template_rows():
    # company 1: gross profit is not in its template (a bank), but the old mapper holds FY and Q values
    gate, rows, covered, held = _run([rep(1, {REV: FULL})], [old(1, "10", "1"), old(1, "10", "2")])
    assert covered == [(1, GP)] and held == []
    assert {(r["period_grain"], r["period_start"], r["period_end"]) for r in rows} == {
        ("FY", "2023-01-01", "2023-12-31"), ("Q", "2024-01-01", "2024-03-31")}  # fmt: skip
    assert {(r["state"], r["reason_code"], r["value"]) for r in rows} == {("not_in_template", "not_in_template", None)}
    assert (1, GP) in pilot.done_pairs(gate)  # the pair is now written, replacing the old rows
    assert gate[1]["out_of_template"] == [GP, NI]  # still listed (NI: out of template, no old value: not written)


@pytest.mark.unit
def test_b_no_expected_keys_pair_with_old_values_is_written_as_gap_defects():
    gate, rows, covered, _ = _run([rep(1, {REV: FULL, NI: {"keys": 0}})], [old(1, "11", "3")])
    assert covered == [(1, NI)]
    (r,) = rows
    assert (r["state"], r["reason_code"], r["defect_class"], r["owner"]) == (
        "defect", "hybrid_gap_unresolved", "unclassified", "triage")  # fmt: skip
    assert r["input_refs"]["pilot_cause"] == "no_calendar_key" and "no_calendar_key" in r["reason_text"]
    assert (r["period_grain"], r["period_type"], r["fsn_end"]) == ("I", "instant", "2024-03-31")
    assert gate[1]["data_points"][NI] == [] and (1, NI) in pilot.done_pairs(gate)


@pytest.mark.unit
def test_rows_pass_the_cell_contract():
    from scrooner_pipeline.normalizer import cell_loader

    _, rows_a, _, _ = _run([rep(1, {REV: FULL})], [old(1, "10", "1")])
    _, rows_b, _, _ = _run([rep(1, {REV: FULL, NI: {"keys": 0}})], [old(1, "11", "2")])
    for r in rows_a + rows_b:
        got = cell_loader.parse_row(1, r, {GP, NI})
        assert not isinstance(got, str), got
        assert (got.key.period_start.isoformat(), got.key.period_end.isoformat()) == (r["period_start"], r["period_end"])


@pytest.mark.unit
def test_a_ytd_key_holds_the_pair_and_lists_it():
    gate, rows, covered, held = _run(
        [rep(1, {REV: FULL, NI: {"keys": 0}})], [old(1, "10", "1"), old(1, "10", "4"), old(1, "11", "4")]
    )
    assert rows == [] and covered == []
    assert held == [
        {"company_id": 1, "data_point": GP, "case": "a", "no_cell_grain_keys": 1},
        {"company_id": 1, "data_point": NI, "case": "b", "no_cell_grain_keys": 1},
    ]
    assert gate[1]["data_points"][NI] == ["no_expected_keys", "G2_no_cell_grain:1"]
    assert (1, GP) not in pilot.done_pairs(gate)


@pytest.mark.unit
def test_nothing_for_a_failing_company_a_pair_without_old_values_or_keys_before_the_floor():
    gate, rows, covered, _ = _run(
        [rep(1, {REV: FULL}), rep(2, {REV: FULL})],
        [old(1, "10", "1"), old(2, "10", "5")],  # company 2: only a 2012 value (before the history floor)
        missing={"C1": [{"accession": "x"}]},
    )
    assert rows == [] and covered == []
    gate, rows, covered, _ = _run([rep(3, {REV: FULL})], [old(3, "10", "1", value="")])  # no value
    assert rows == [] and covered == []


@pytest.mark.unit
def test_b_skips_keys_select_already_writes():
    cell = {"company_id": 1, "data_point_name": NI, "period_grain": "FY", "fsn_end": "2023-12-31", "state": "value"}
    _, rows, covered, _ = _run(
        [rep(1, {REV: FULL, NI: {"keys": 0}})], [old(1, "11", "1"), old(1, "11", "2")], cells=[cell]
    )
    assert [(r["period_grain"]) for r in rows] == ["Q"] and covered == [(1, NI)]


# --------------------------------------------------------------------------- the done-gate command


def _out(tmp_path, reports, before, cells):
    out = tmp_path / "out"
    (out / "before_image").mkdir(parents=True)
    (out / "report.json").write_text(json.dumps(reports))
    (out / "missing_filings.json").write_text("{}")
    (out / "gaps.csv").write_text("cik,company_id,data_point,grain,period_end,cause\n")

    def gz(name, header, rows):
        with gzip.open(out / "before_image" / f"{name}.csv.gz", "wt", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)

    gz("canonical_fact", ["company_id", "canonical_concept_id", "period_id", "value"],
       [[b["company_id"], b["canonical_concept_id"], b["period_id"], b["value"]] for b in before])  # fmt: skip
    gz("canonical_concept", ["id", "name"], [[k, v] for k, v in CONCEPTS.items()])
    gz("period", ["id", "start_date", "end_date", "period_type"],
       [[k, v["start_date"], v["end_date"], v["period_type"]] for k, v in PERIODS.items()])  # fmt: skip
    (out / "cells" / "is_core").mkdir(parents=True)
    with gzip.open(out / "cells" / "is_core" / "cells.jsonl.gz", "wt") as fh:
        for c in cells:
            fh.write(json.dumps(c) + "\n")
    return out


def _cell(cid, dp, grain, end):
    return {"company_id": cid, "data_point_name": dp, "period_grain": grain, "fsn_end": end, "state": "value",
            "value": "1", "rule_id": "fsn.select@1", "input_refs": {}}  # fmt: skip


@pytest.mark.unit
def test_done_gate_command_writes_g2_rows_into_the_cells_the_write_reads(tmp_path):
    from scrooner_pipeline.jobs import fsn as fsn_job

    # select also emitted a gross-profit value for company 1 (out of template): the whole pair is replaced
    cells = [_cell(1, REV, "FY", "2023-12-31"), _cell(1, GP, "FY", "2023-12-31")]
    out = _out(tmp_path, [rep(1, {REV: FULL})], [old(1, "10", "1"), old(1, "10", "2"), old(1, "12", "1")], cells)
    res = CliRunner().invoke(fsn_job.app, ["done-gate", "--pilot-out", str(out), "--data-points", f"{REV},{GP}"])
    assert res.exit_code == 0, res.output + repr(res.exception)
    assert "G2 1 pairs written as reason rows (2 rows); 0 pairs keep old rows" in res.output
    assert "valued->no-row in written pairs: 0" in res.output
    pairs = (out / "done_pairs.tsv").read_text().splitlines()[1:]
    assert pairs == [f"1\t{GP}", f"1\t{REV}"]
    with gzip.open(out / "cells" / "is_core" / "cells.jsonl.gz", "rt") as fh:
        got = [json.loads(line) for line in fh]
    gp = [r for r in got if r["data_point_name"] == GP]
    assert [r["state"] for r in gp] == ["not_in_template", "not_in_template"]  # the select value is gone
    assert [r for r in got if r["data_point_name"] == REV][0]["state"] == "value"
    report = json.loads((out / "no_fallback.json").read_text())
    assert report["pairs_written_as_reasons"] == [{"company_id": 1, "data_point": GP}]
    assert report["pairs_held_keeping_old_rows"] == []


@pytest.mark.unit
def test_done_gate_command_without_g2_leaves_the_cells_untouched(tmp_path):
    from scrooner_pipeline.jobs import fsn as fsn_job

    cells = [_cell(1, REV, "FY", "2023-12-31")]
    out = _out(tmp_path, [rep(1, {REV: FULL})], [old(1, "12", "1")], cells)
    src = out / "cells" / "is_core" / "cells.jsonl.gz"
    before = src.read_bytes()
    res = CliRunner().invoke(fsn_job.app, ["done-gate", "--pilot-out", str(out), "--data-points", f"{REV},{GP}"])
    assert res.exit_code == 0, res.output + repr(res.exception)
    assert src.read_bytes() == before
    assert json.loads((out / "no_fallback.json").read_text())["rows"] == 0
