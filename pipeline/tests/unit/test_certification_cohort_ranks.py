"""certify on cohort v1.1 ranks (the FSN write's cohort; shards.csv lacks ranks 981-1000)."""

from __future__ import annotations

import csv
import re

import pytest
from typer.testing import CliRunner

from scrooner_pipeline.certification.runner import (
    COHORT_V11_CSV,
    SHARDS_CSV,
    load_cohort_company_ids,
    parse_ranks,
)
from scrooner_pipeline.jobs.certify import app


def _v11():
    with open(COHORT_V11_CSV, newline="") as fh:
        return list(csv.DictReader(fh))


@pytest.mark.unit
def test_parse_ranks():
    assert parse_ranks("1-100") == [(1, 100)]
    assert parse_ranks("1-10, 981-1000") == [(1, 10), (981, 1000)]
    assert parse_ranks("7") == [(7, 7)]
    for bad in ("", "0-5", "10-2", "a-b"):
        with pytest.raises(ValueError):
            parse_ranks(bad)


@pytest.mark.unit
def test_top_100_is_the_first_100_rows_in_rank_order():
    rows = _v11()
    ids = load_cohort_company_ids("1-100")
    assert ids == [int(r["company_id"]) for r in rows[:100]]
    assert rows[0]["ticker"] == "NVDA" and len(ids) == 100


@pytest.mark.unit
def test_tail_ranks_absent_from_shards_are_reachable():
    with open(SHARDS_CSV, newline="") as fh:
        sharded = {int(r["company_id"]) for r in csv.DictReader(fh) if not (r.get("excluded") or "").strip()}
    tail = load_cohort_company_ids("981-1000")
    assert len(tail) == 20 and not set(tail) & sharded  # exactly the 20 with no campaign shard
    by_id = {int(r["company_id"]): r["ticker"] for r in _v11()}
    assert {"BRK-A", "SO", "TXNM"} <= {by_id[i] for i in tail}


@pytest.mark.unit
def test_overlapping_ranges_are_deduplicated_and_beyond_cohort_refused():
    assert load_cohort_company_ids("1-3,2-4") == load_cohort_company_ids("1-4")
    with pytest.raises(ValueError, match="beyond"):
        load_cohort_company_ids("990-1001")


def _plain(text: str) -> str:
    """CI renders typer help through rich with ANSI styling that splits option names."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


@pytest.mark.unit
def test_cli_accepts_cohort_ranks_and_still_requires_a_selection():
    runner = CliRunner(env={"NO_COLOR": "1", "TERM": "dumb", "COLUMNS": "200"})
    assert "--cohort-ranks" in _plain(runner.invoke(app, ["--help"]).output)
    res = runner.invoke(app, [])
    assert res.exit_code != 0 and "--cohort-ranks" in _plain(res.output)
