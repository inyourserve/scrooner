"""Stage select_plan of pipeline-fsn-write.yml (release approver ruling 2026-11-10, item 4): the whole select_write
path against production, with `scrooner-cells load --plan`, so no analytics.canonical_fact, cell_blank_reason or
slot_protected_cell row changes. The workflow is read as text (no YAML library in the pipeline environment) and the
DB test runs the loader with the exact flags the stage's step passes, so flipping the stage to --apply fails both."""

from __future__ import annotations

import gzip
import json
import re
import shlex
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "pipeline-fsn-write.yml"


def _jobs(text: str) -> dict[str, str]:
    body = text.split("\njobs:\n", 1)[1]
    parts = re.split(r"\n  ([a-z_]+):\n", "\n" + body)
    return dict(zip(parts[1::2], parts[2::2]))


def _if(block: str) -> str | None:
    m = re.search(r"^ {4,8}if: (.+)$", block, re.M)
    return m.group(1).strip() if m else None


def _runs(cond: str | None, stage: str) -> bool:
    if cond is None:
        return True
    expr = (
        cond.replace("inputs.stage", repr(stage))
        .replace("||", " or ")
        .replace("&&", " and ")
        .replace("always()", "True")
    )
    return bool(eval(expr, {"__builtins__": {}}, {}))  # noqa: S307  the workflow's own if: expressions


def _steps_run(stage: str) -> list[tuple[str, str]]:
    """(job, step text) of every step that runs for this stage (job-level and step-level if: evaluated)."""
    out = []
    for job, block in _jobs(WORKFLOW.read_text()).items():
        head, _, steps = block.partition("\n    steps:\n")
        if not _runs(_if(head), stage):
            continue
        for step in re.split(r"\n      - ", "\n" + steps)[1:]:
            if _runs(_if(step), stage):
                out.append((job, step))
    return out


def _cells_loads(step: str) -> list[list[str]]:
    """The argument lists of every `scrooner-cells load` command in a step (continuation lines joined)."""
    text = step.replace("\\\n", " ")
    return [
        shlex.split(line.split("scrooner-cells load", 1)[1].split("||", 1)[0])
        for line in text.splitlines()
        if "scrooner-cells load" in line
    ]


def plan_stage_load_flags() -> list[str]:
    """The mode and protect flags the select_plan stage passes to `scrooner-cells load` (exactly one such call)."""
    calls = [a for _j, s in _steps_run("select_plan") for a in _cells_loads(s)]
    assert len(calls) == 1, calls
    return [a for a in calls[0] if a in ("--plan", "--apply", "--protect")]


@pytest.mark.unit
def test_the_select_plan_stage_never_passes_apply_to_the_cell_loader():
    text = WORKFLOW.read_text()
    assert "options: [load_map, select_plan, select_write, proof_blank, restore]" in text
    plan = _steps_run("select_plan")
    names = [s.split("\n", 1)[0] for _j, s in plan]
    # the whole select_write path runs: shard, load, map/pilot, before-image (+ upload), done gate, the plan load
    for want in ("Shard from the fsn-notes bucket", "Load fsn.*", "Map (fsn.line_map)", "Before-image of",
                 "Store the before-image", "Done gate", "Plan the done"):  # fmt: skip
        assert any(want in n for n in names), (want, names)
    assert plan_stage_load_flags() == ["--plan", "--protect"]
    for _j, step in plan:
        assert "scrooner-cells restore" not in step
        for args in _cells_loads(step):
            assert "--apply" not in args, step
        # the only --apply that runs is the fsn.concept_rule seed (the store, under the store-load approval)
        if "--apply" in step:
            assert "scrooner-fsn seed-rules" in step, step
    # the select_write path still applies, and only there
    write = [a for _j, s in _steps_run("select_write") for a in _cells_loads(s)]
    assert len(write) == 1 and "--apply" in write[0] and "--protect" in write[0]
    # what the approver reads after a plan run is uploaded
    upload = next(s for j, s in plan if "name: fsn-write-shard-" in s)
    for f in ("out/valued_to_no_row.tsv", "out/valued_to_blank.json", "out/not_done.json", "out/done_pairs.tsv",
              "out/done_companies.txt", "out/write-*.json"):  # fmt: skip
        assert f in upload, f
    assert any("fsn-write-before-image-" in s for _j, s in plan)


@pytest.fixture
def conn(isolated_database_url):
    import psycopg

    c = psycopg.connect(isolated_database_url)
    if (
        c.execute(
            "select count(*) from information_schema.tables where (table_schema, table_name) in "
            "(('analytics','canonical_fact'), ('analytics','cell_blank_reason'), ('analytics','slot_protected_cell'))"
        ).fetchone()[0]
        != 3
    ):
        c.close()
        pytest.skip("needs the migrated schema")
    yield c
    c.close()


TABLES = (
    "analytics.canonical_fact",
    "analytics.cell_blank_reason",
    "analytics.slot_protected_cell",
    "core.period",
)


def _snapshot(conn) -> dict[str, list[tuple]]:
    return {
        t: conn.execute(f"select * from {t} order by 1, 2, 3").fetchall()
        for t in TABLES
    }


def _cell(cid, **over):
    row = {
        "company_id": cid,
        "data_point_name": "capex_resolved",
        "period_grain": "Q",
        "period_start": "2024-01-01",
        "period_end": "2024-04-02",
        "basis": "latest",
        "state": "value",
        "value": "100",
        "unit": "USD",
        "source_fact_ids": [],
        "accession": "0000000001-24-000001",
        "tag": "PaymentsToAcquirePropertyPlantAndEquipment",
        "rule_id": "fsn.select_printed@1",
        "evidence_level": "DATA-INFERRED",
    }
    row.update(over)
    return row


def _file(tmp_path: Path, name: str, rows: list[dict]) -> Path:
    d = tmp_path / name
    d.mkdir()
    p = d / "cells.jsonl.gz"
    p.write_bytes(gzip.compress("\n".join(json.dumps(r) for r in rows).encode()))
    return p


@pytest.mark.integration
def test_the_plan_stage_load_leaves_canonical_fact_reasons_and_protection_unchanged(
    conn, isolated_database_url, tmp_path, monkeypatch
):
    from typer.testing import CliRunner

    from scrooner_pipeline.common.config import settings
    from scrooner_pipeline.jobs import cells as cells_job
    from scrooner_pipeline.normalizer import cell_loader as cl

    one = lambda sql, p=(): conn.execute(sql, p).fetchone()[0]  # noqa: E731
    cid = one(
        "insert into core.company (cik, company_name) values ('0000000001', 'PLAN TEST') returning id"
    )
    conn.execute(
        "insert into core.unit (unit_name) values ('usd') on conflict do nothing"
    )
    uid = one("select id from core.unit where unit_name = 'usd'")
    conn.execute(
        "insert into analytics.canonical_concept (name, statement, combination_mode) "
        "values ('capex_resolved', 'cash_flow', 'first_match') on conflict (name) do nothing"
    )
    pid = one(
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) "
        "values (%s, '2024-01-01', '2024-04-02', 'duration', 2024, 'Q1') returning id",
        (cid,),
    )
    fid = one(
        "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) "
        "values (%s, '0000000001-24-000001', '10-Q', '2024-05-01', '2024-04-02') returning id",
        (cid,),
    )
    conn.execute(
        "insert into core.concept (taxonomy, tag) values ('us-gaap', 'PaymentsToAcquirePropertyPlantAndEquipment') "
        "on conflict do nothing"
    )
    coid = one(
        "select id from core.concept where tag = 'PaymentsToAcquirePropertyPlantAndEquipment'"
    )
    raw = one(
        "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status, fetched_at) "
        "values ('0000000001', 'test://x', 'abc', 'test/x', 200, now()) returning id"
    )
    conn.execute(
        "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_derived, "
        "is_authoritative, raw_object_id) values (%s, %s, %s, %s, %s, 100, false, true, %s)",
        (cid, coid, uid, pid, fid, raw),
    )
    conn.commit()
    blank = {"state": "defect", "value": None, "unit": None, "accession": None, "tag": None,
             "reason_code": "hybrid_gap_unresolved", "reason_text": "not printed", "defect_class": "period",
             "owner": "period_engineer"}  # fmt: skip
    # an earlier applied, protected write: rows in all three tables
    first = _file(tmp_path, "first", [
        _cell(cid),
        _cell(cid, period_start="2024-04-03", period_end="2024-07-02", **blank),
    ])  # fmt: skip
    cl.load(conn, "capex_da_cash_debt", [first], apply=True, protect=True)
    before = _snapshot(conn)
    assert all(before[t] for t in TABLES[:3]), before
    # the plan: a changed value, a new valued key with a new period, a new TP blank, the old blank now valued
    second = _file(tmp_path, "second", [
        _cell(cid, value="250"),
        _cell(cid, period_start="2024-04-03", period_end="2024-07-02", value="7", source_fact_ids=[]),
        _cell(cid, period_start="2023-10-01", period_end="2023-12-31", value="5"),
        _cell(cid, period_grain="TP", period_start="2024-01-01", period_end="2024-07-02", **blank),
    ])  # fmt: skip
    conn.commit()
    monkeypatch.setattr(settings, "database_url", isolated_database_url)
    monkeypatch.delenv("SCROONER_LOAD_DATABASE_URL", raising=False)
    flags = plan_stage_load_flags()  # exactly what the select_plan step passes
    res = CliRunner().invoke(
        cells_job.app,
        [
            "load",
            str(second),
            "--family",
            "capex_da_cash_debt",
            *flags,
            "--statement-timeout",
            "10min",
            "--report",
            str(tmp_path / "write-capex_da_cash_debt.json"),
        ],  # fmt: skip
    )
    assert res.exit_code == 0, res.output + repr(res.exception)
    report = json.loads((tmp_path / "write-capex_da_cash_debt.json").read_text())
    assert (
        report["companies"] == 1
    )  # the company was planned (bound, resolved, written, rolled back)
    conn.rollback()
    assert _snapshot(conn) == before
