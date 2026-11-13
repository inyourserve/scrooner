"""pipeline/scripts/fsn_nightly_incremental.sh as the refresh workflow runs it, with stand-in `uv` and `psql`
(no database, no network, no GNU `timeout`): the stages stop where FSN_NIGHTLY_STAGE says, and `write` hands only the night's
companies that have a company_tag_map to the tag-map writer (rule company_tag_map.select@1), with the rule
enabled for that call alone. The script never fails the night."""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SCRIPT = "pipeline/scripts/fsn_nightly_incremental.sh"

FAKE_UV = """#!/usr/bin/env bash
# uv run --project pipeline <prog> <cmd> ...
shift 3
prog="$1"; cmd="$2"; shift 2
echo "$prog $cmd $* RULES=${SCROONER_RULES_ENABLED:-}" >> "$FAKE_LOG"
if [ "$prog $cmd" = "scrooner-fsn nightly" ]; then
  out=""; report=""
  while [ $# -gt 0 ]; do case "$1" in --out) out="$2"; shift;; --report) report="$2"; shift;; esac; shift; done
  mkdir -p "$out"; printf '%s' "$FAKE_CIKS" > "$out/ciks.txt"
  python3 -c 'import json,sys; print(json.dumps({"filings": [{"company_id": int(c)} for c in sys.argv[1].split(",") if c]}))' "$FAKE_IDS" > "$report"
fi
if [ "$prog $cmd" = "scrooner-map tagmap-plan" ]; then echo "tagmap-plan [apply]"; exit "${FAKE_TAGMAP_RC:-0}"; fi
exit 0
"""

FAKE_PSQL = """#!/usr/bin/env bash
q="${@: -1}"
echo "PSQL $q" >> "$FAKE_LOG"
case "$q" in
  *pg_stat_activity*) echo 10 ;;
  *company_tag_map*) echo "$FAKE_MAPPED" ;;
esac
"""

# macOS has no `timeout` (GNU coreutils), so the script's first `timeout ... scrooner-fsn nightly` failed there,
# the script warned and exited 0, and no scrooner- call was logged (6 tests failed on the Mac with IndexError).
# The stand-in drops the duration and runs the command, like the real one does on a call that finishes in time.
FAKE_TIMEOUT = """#!/usr/bin/env bash
shift
exec "$@"
"""


def run(tmp_path: Path, **env_extra: str) -> tuple[subprocess.CompletedProcess, list[str]]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    for name, body in (("uv", FAKE_UV), ("psql", FAKE_PSQL), ("timeout", FAKE_TIMEOUT)):
        p = bin_dir / name
        p.write_text(body)
        p.chmod(p.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "calls.log"
    log.write_text("")
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "FAKE_LOG": str(log),
        "FSN_NIGHTLY_OUT": str(tmp_path / "out"),
        "DATABASE_URL": "postgresql://fake",
        "FAKE_CIKS": "0000000001,0000000002",
        "FAKE_IDS": "11,12",
        "FAKE_MAPPED": "12",
        **env_extra,
    }
    env.pop("SCROONER_RULES_ENABLED", None)
    out = subprocess.run(["bash", SCRIPT], cwd=REPO, capture_output=True, text=True, env=env, timeout=120)
    return out, log.read_text().splitlines()


@pytest.mark.unit
@pytest.mark.parametrize(
    "stage,last",
    [("build", "scrooner-fsn nightly"), ("load", "scrooner-fsn pilot"), ("write", "scrooner-map tagmap-plan")],
)
def test_each_stage_stops_where_it_says(tmp_path, stage, last):
    out, calls = run(tmp_path, FSN_NIGHTLY_STAGE=stage)
    assert out.returncode == 0, out.stderr
    progs = [c for c in calls if c.startswith("scrooner-")]
    assert progs[-1].startswith(last)
    if stage != "write":
        assert not any("tagmap-plan" in c for c in calls)


@pytest.mark.unit
def test_write_hands_only_tag_mapped_companies_to_the_tag_map_writer(tmp_path):
    out, calls = run(tmp_path, FSN_NIGHTLY_STAGE="write")
    assert out.returncode == 0, out.stderr
    tagmap = [c for c in calls if c.startswith("scrooner-map tagmap-plan")]
    assert len(tagmap) == 1
    assert "--company-ids 12 --apply --before-image-dir" in tagmap[0]
    assert tagmap[0].endswith("RULES=company_tag_map.select@1")
    # the rule is enabled for that call alone
    assert all(c.endswith("RULES=") for c in calls if c.startswith("scrooner-fsn"))
    assert not any("cells load" in c or "pilot-prod" in c or "done-gate" in c for c in calls)
    assert any("company_tag_map" in c and "{11,12}" in c for c in calls if c.startswith("PSQL"))


@pytest.mark.unit
def test_write_skips_when_no_company_has_a_tag_map(tmp_path):
    out, calls = run(tmp_path, FSN_NIGHTLY_STAGE="write", FAKE_MAPPED="")
    assert out.returncode == 0
    assert "nothing written" in out.stdout
    assert not any("tagmap-plan" in c for c in calls)


@pytest.mark.unit
def test_a_failed_tag_map_write_warns_and_never_fails_the_night(tmp_path):
    out, _ = run(tmp_path, FSN_NIGHTLY_STAGE="write", FAKE_TAGMAP_RC="1")
    assert out.returncode == 0
    assert "::warning::fsn nightly: tag-map write failed" in out.stdout


@pytest.mark.unit
def test_off_runs_nothing(tmp_path):
    out, calls = run(tmp_path)
    assert out.returncode == 0 and calls == []
