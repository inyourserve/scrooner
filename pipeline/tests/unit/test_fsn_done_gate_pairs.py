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
    held, transitions = pilot.hold_guard(cells, before, CONCEPTS, PERIODS, {REV, NI})
    assert held == {
        (1, NI): "0_new_values_vs_1_before"
    }  # revenue keeps one value: not held
    assert transitions == {
        REV: {"not_filed_separately": 1, "no_new_cell": 1},
        NI: {"balance_sheet_not_filed": 1},
    }


def _out_dir(tmp_path, reports, cells, before, gaps=()):
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
        ["id", "start_date", "end_date", "period_type"],
        [
            [k, v["start_date"], v["end_date"], v["period_type"]]
            for k, v in PERIODS.items()
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
    # company 1 and 2: both pairs (no hold, founder 2026-11-09); company 3: criterion 1 fails, nothing written
    assert "4 pairs of 6; 2 companies fully done" in res.output
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
