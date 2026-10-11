"""scripts/lib/sharded.sh -- the nightly reprocess runs each stage across parallel
shards. These tests drive the real shell function with a stand-in `uv`, so no
database or network is involved, and pin the properties production depends on.
"""

import os
import stat
import subprocess
from pathlib import Path

import pytest

HELPER = Path(__file__).resolve().parents[2] / "scripts" / "lib" / "sharded.sh"

FAKE_UV = """#!/usr/bin/env bash
# stand-in for: uv run <program> <stage> --ciks <chunk>
echo "START $3 $5" >> "$FAKE_LOG"
sleep 0.15
echo "work for $3 on $5"
if [[ ",$5," == *",FAIL,"* ]]; then echo "END $3 $5 FAILED" >> "$FAKE_LOG"; exit 3; fi
echo "END $3 $5" >> "$FAKE_LOG"
"""


def _run(tmp_path, ciks, stages, shards=4):
    uv = tmp_path / "uv"
    uv.write_text(FAKE_UV)
    uv.chmod(uv.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "calls.log"
    log.write_text("")
    calls = "".join(
        f'run_sharded prog {s} || echo "STAGE-FAILED {s}"\n' for s in stages
    )
    script = f'source "{HELPER}"\nCIKS="{ciks}"\nSHARDS={shards}\n{calls}'
    env = {
        **os.environ,
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "FAKE_LOG": str(log),
    }
    out = subprocess.run(
        ["bash", "-c", script], capture_output=True, text=True, env=env, timeout=60
    )
    return out, log.read_text().splitlines()


@pytest.mark.unit
def test_shards_are_disjoint_and_together_cover_every_company(tmp_path):
    ciks = ",".join(f"{i:010d}" for i in range(1, 11))
    out, lines = _run(tmp_path, ciks, ["facts"])
    chunks = [l.split(" ")[2].split(",") for l in lines if l.startswith("START")]
    flat = [c for chunk in chunks for c in chunk]
    assert len(chunks) == 4
    assert sorted(flat) == sorted(ciks.split(","))  # complete
    assert len(flat) == len(set(flat))  # disjoint: no company processed twice
    assert max(map(len, chunks)) - min(map(len, chunks)) <= 1  # balanced
    assert out.returncode == 0


@pytest.mark.unit
def test_never_more_shards_than_companies(tmp_path):
    out, lines = _run(tmp_path, "0000000001,0000000002", ["facts"], shards=4)
    assert len([l for l in lines if l.startswith("START")]) == 2
    assert "STAGE-FAILED" not in out.stdout


@pytest.mark.unit
def test_each_stage_finishes_on_every_shard_before_the_next_stage_starts(tmp_path):
    """Stage order is a data dependency (dedupe must follow facts, derive-q4 must
    follow derive-interim-quarters): shards may overlap WITHIN a stage, never
    across stages."""
    ciks = ",".join(f"{i:010d}" for i in range(1, 9))
    _, lines = _run(tmp_path, ciks, ["dedupe", "derive-q4"])
    last_end_first = max(i for i, l in enumerate(lines) if l.startswith("END dedupe"))
    first_start_second = min(
        i for i, l in enumerate(lines) if l.startswith("START derive-q4")
    )
    assert last_end_first < first_start_second


@pytest.mark.unit
def test_a_failing_shard_fails_the_stage_but_lets_the_other_shards_finish(tmp_path):
    ciks = "0000000001,0000000002,0000000003,FAIL,0000000005,0000000006"
    out, lines = _run(tmp_path, ciks, ["facts"], shards=3)
    assert "STAGE-FAILED facts" in out.stdout  # caller (set -e) aborts, as before
    ends = [l for l in lines if l.startswith("END")]
    assert len(ends) == 3  # all three shards ran to completion
    assert sum(l.endswith("FAILED") for l in ends) == 1  # only the shard with FAIL


@pytest.mark.unit
def test_output_lines_carry_a_shard_prefix(tmp_path):
    out, _ = _run(tmp_path, "0000000001,0000000002", ["facts"], shards=2)
    prefixed = [l for l in out.stdout.splitlines() if l.startswith("[s")]
    assert {l[:5] for l in prefixed} == {"[s0] ", "[s1] "}
