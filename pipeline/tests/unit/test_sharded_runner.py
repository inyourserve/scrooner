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


@pytest.mark.unit
def test_the_real_reprocess_script_finds_its_helper_when_invoked_the_way_ci_does():
    """CI runs `pipeline/scripts/reprocess_recent_filers.sh` as a RELATIVE path
    from the repo root. The script cd's into pipeline/ first, so a helper path
    derived from a relative $0 after the cd does not resolve -- that broke the
    entire nightly refresh on 2026-10-12 (3 minutes in), and the stand-in-uv
    tests above could not see it because they source the helper by absolute
    path. This runs the real script, from the repo root, by the relative path."""
    repo_root = HELPER.parents[3]
    out = subprocess.run(
        ["bash", "pipeline/scripts/reprocess_recent_filers.sh"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env={**os.environ, "REPROCESS_SOURCE_CHECK": "1"},
        timeout=60,
    )
    assert "No such file" not in out.stderr, out.stderr
    assert "SOURCED_OK" in out.stdout, (out.stdout, out.stderr)
    assert out.returncode == 0


@pytest.mark.unit
def test_hung_shard_is_killed_at_the_stage_cap_and_later_stages_still_run(tmp_path):
    """A shard that never exits must not hold the barrier forever: it is killed at
    STAGE_TIMEOUT_SECS, the stage is reported failed, and the next stage runs."""
    uv = tmp_path / "uv"
    uv.write_text(
        '#!/usr/bin/env bash\necho "START $3" >> "$FAKE_LOG"\n'
        '[ "$3" = "hang" ] && sleep 300\necho "END $3" >> "$FAKE_LOG"\n'
    )
    uv.chmod(uv.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "calls.log"
    log.write_text("")
    script = (
        f'source "{HELPER}"\nCIKS="0000000001,0000000002"\nSHARDS=2\n'
        "export STAGE_TIMEOUT_SECS=3\n"
        'run_sharded prog hang || echo "STAGE-FAILED hang"\n'
        'run_sharded prog after || echo "STAGE-FAILED after"\n'
    )
    env = {**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}", "FAKE_LOG": str(log)}
    out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, env=env, timeout=40)
    assert "STAGE-FAILED hang" in out.stdout
    assert "STAGE-FAILED after" not in out.stdout
    assert "exceeded 3s" in out.stderr
    assert "END after" in log.read_text()


# --- overall budget + tag-library cap (2026-10-19) -------------------------
# These run the REAL script by the relative path CI uses, from the repo root and
# from pipeline/, with a stand-in `uv` injected via REPROCESS_PATH_PREFIX (no DB).

SCRIPT_REL = "scripts/reprocess_recent_filers.sh"
REPO_ROOT = HELPER.parents[3]

FAKE_UV_FULL = """#!/usr/bin/env bash
# uv run python3 -  -> the two SQL heredocs; uv run <prog> <stage> [--ciks X]
if [ "$2" = "python3" ]; then
  if grep -q DEREGISTRATION_FORMS; then echo ""; else echo "0000000001,0000000002,0000000003"; fi
  exit 0
fi
prog="$2"; stage="$3"
echo "RUN $prog $stage" >> "$FAKE_LOG"
if [ "$stage" = "build-tag-library" ] && [ -n "$FAKE_TAG_HANG" ]; then sleep 300; fi
sleep "${FAKE_STAGE_SLEEP:-0}"
[ "$stage" = "$FAKE_FAIL_STAGE" ] && exit 4
exit 0
"""


def _run_script(tmp_path, cwd, script_path, **env_extra):
    uv = tmp_path / "uv"
    uv.write_text(FAKE_UV_FULL)
    uv.chmod(uv.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "calls.log"
    log.write_text("")
    env = {
        **os.environ,
        "REPROCESS_PATH_PREFIX": str(tmp_path),
        "FAKE_LOG": str(log),
        "REPROCESS_SHARDS": "1",
        **env_extra,
    }
    out = subprocess.run(
        ["bash", script_path], cwd=cwd, capture_output=True, text=True, env=env, timeout=120
    )
    return out, log.read_text().splitlines()


@pytest.mark.unit
@pytest.mark.parametrize("cwd,path", [(REPO_ROOT, "pipeline/" + SCRIPT_REL), (REPO_ROOT / "pipeline", SCRIPT_REL)])
def test_full_run_without_budget_pressure_runs_all_23_stages_and_exits_zero(tmp_path, cwd, path):
    out, calls = _run_script(tmp_path, cwd, path)
    assert out.returncode == 0, (out.stdout, out.stderr)
    stages_run = [c.split()[2] for c in calls if c.startswith("RUN scrooner-") and "update-status" not in c]
    assert len(stages_run) == 23
    assert stages_run[-1] == "build-tag-library"
    assert out.stdout.count("took ") == 23  # one "took Ns" line per stage
    assert "budget exhausted" not in out.stderr


@pytest.mark.unit
@pytest.mark.parametrize("cwd,path", [(REPO_ROOT, "pipeline/" + SCRIPT_REL), (REPO_ROOT / "pipeline", SCRIPT_REL)])
def test_budget_exhaustion_skips_remaining_stages_names_them_once_and_exits_nonzero(tmp_path, cwd, path):
    out, calls = _run_script(
        tmp_path, cwd, path, REPROCESS_BUDGET_SECS="2", FAKE_STAGE_SLEEP="1.2"
    )
    assert out.returncode != 0
    assert out.stderr.count("budget exhausted") == 1
    line = next(l for l in out.stderr.splitlines() if "budget exhausted" in l)
    ran = {c.split()[2] for c in calls if "scrooner-normalize" in c or "scrooner-map" in c}
    skipped_names = line.split("skipped: ")[1].split()
    assert skipped_names and skipped_names[-1] == "map:build-tag-library"
    assert not ({s.split(":")[1] for s in skipped_names} & ran)  # skipped means never run
    # a "took" line for every stage: ran + skipped = all 23
    assert out.stdout.count("took ") == 23
    assert "FAILED stages" in out.stderr and "budget-skipped" in out.stderr


@pytest.mark.unit
def test_a_failed_stage_does_not_hide_and_later_stages_still_run(tmp_path):
    out, calls = _run_script(
        tmp_path, REPO_ROOT, "pipeline/" + SCRIPT_REL, FAKE_FAIL_STAGE="facts"
    )
    assert out.returncode == 1
    assert "normalize:facts" in out.stderr
    assert any(c.endswith("build-tag-library") for c in calls)


@pytest.mark.unit
def test_tag_library_is_killed_at_its_cap_and_reported(tmp_path):
    out, _ = _run_script(
        tmp_path, REPO_ROOT, "pipeline/" + SCRIPT_REL,
        FAKE_TAG_HANG="1", TAG_LIBRARY_TIMEOUT_SECS="2",
    )
    assert out.returncode == 1
    assert "exceeded 2s" in out.stderr
    assert "map:build-tag-library" in out.stderr
