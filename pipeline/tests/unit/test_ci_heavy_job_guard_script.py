"""scripts/ci/heavy_job_guard.sh against a stub `gh` (the workflows run it on ubuntu-latest with the real gh).

The stub answers `gh run list --workflow W --status S` from a per-call script: each call pops the next line of
<state>/<W>.<S> files ("rows" of "<id> <status> <url>", or the word FAIL for an API error)."""

import os
import stat
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GUARD = ROOT / "scripts" / "ci" / "heavy_job_guard.sh"

STUB = r"""#!/usr/bin/env bash
# gh run list --repo R --workflow W --status S --limit N --json ... --jq ...
wf=""; st=""
while [ $# -gt 0 ]; do
  case "$1" in --workflow) wf=$2; shift;; --status) st=$2; shift;; esac; shift
done
echo "$wf $st" >> "$STATE/calls"
seq_file="$STATE/$wf.$st.seq"
if [ -f "$seq_file" ]; then
  n=$(cat "$STATE/$wf.$st.n" 2>/dev/null || echo 0)
  line=$(sed -n "$((n + 1))p" "$seq_file"); [ -z "$line" ] && line=$(tail -n 1 "$seq_file")
  echo $((n + 1)) > "$STATE/$wf.$st.n"
  [ "$line" = FAIL ] && { echo "HTTP 502" >&2; exit 1; }
  [ "$line" = NONE ] || echo "$line"
fi
exit 0
"""


def guard(tmp_path, *args, seqs=None):
    state = tmp_path / "state"
    state.mkdir(parents=True, exist_ok=True)
    for (wf, status), lines in (seqs or {}).items():
        (state / f"{wf}.{status}.seq").write_text("\n".join(lines) + "\n")
    bindir = tmp_path / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    gh = bindir / "gh"
    gh.write_text(STUB)
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    env = dict(os.environ, PATH=f"{bindir}:{os.environ['PATH']}", STATE=str(state), GITHUB_REPOSITORY="o/r",
               HEAVY_GUARD_POLL_SECONDS="0")
    return subprocess.run(["bash", str(GUARD), *args], capture_output=True, text=True, env=env, timeout=60)


RUN = "123 in_progress https://github.com/o/r/actions/runs/123"


def test_refuse_if_heavy_passes_when_nothing_runs(tmp_path):
    r = guard(tmp_path, "refuse-if-heavy")
    assert r.returncode == 0, r.stdout + r.stderr


def test_refuse_if_heavy_refuses_a_running_or_queued_heavy_job(tmp_path):
    assert guard(tmp_path, "refuse-if-heavy", seqs={("pipeline-refresh.yml", "in_progress"): [RUN]}).returncode == 1
    queued = "9 queued https://x"
    assert guard(tmp_path / "q", "refuse-if-heavy", seqs={("pipeline-sanity.yml", "queued"): [queued]}).returncode == 1


def test_refuse_if_heavy_fails_closed_on_an_api_error(tmp_path):
    r = guard(tmp_path, "refuse-if-heavy", seqs={("pipeline-recompute.yml", "pending"): ["FAIL"]})
    assert r.returncode == 1 and "could not list" in r.stdout


def test_wait_for_write_passes_without_a_write(tmp_path):
    assert guard(tmp_path, "wait-for-write", "5").returncode == 0


def test_wait_for_write_waits_until_the_write_ends(tmp_path):
    r = guard(tmp_path, "wait-for-write", "5",
              seqs={("pipeline-fsn-write.yml", "in_progress"): [RUN, RUN, "NONE"]})
    assert r.returncode == 0, r.stdout
    assert r.stdout.count("waiting for the FSN production write") == 2


def test_wait_for_write_is_bounded_when_the_write_hangs(tmp_path):
    r = guard(tmp_path, "wait-for-write", "0", seqs={("pipeline-fsn-write.yml", "in_progress"): [RUN]})
    assert r.returncode == 1 and "still in progress" in r.stdout


def test_wait_for_write_never_reads_an_api_error_as_no_write(tmp_path):
    """Fail closed: an error is 'unknown' and the job keeps waiting (here: until the API answers 'no write')."""
    r = guard(tmp_path, "wait-for-write", "5",
              seqs={("pipeline-fsn-write.yml", "in_progress"): ["FAIL", "FAIL", "NONE"]})
    assert r.returncode == 0
    assert r.stdout.count("::warning::could not list") >= 2
    hung = guard(tmp_path / "h", "wait-for-write", "0", seqs={("pipeline-fsn-write.yml", "in_progress"): ["FAIL"]})
    assert hung.returncode == 1 and "unknown" in hung.stdout


def test_a_queued_write_does_not_block_the_nightly(tmp_path):
    """Only a write in progress blocks: a queued write starts later and then refuses beside the running nightly."""
    r = guard(tmp_path, "wait-for-write", "5", seqs={("pipeline-fsn-write.yml", "queued"): ["7 queued https://x"]})
    assert r.returncode == 0


def _jobs(text: str) -> dict[str, str]:
    """Top-level jobs of a workflow file -> their text (no YAML parser in the locked dependencies)."""
    body = text.split("\njobs:\n", 1)[1]
    out, name = {}, None
    for line in body.splitlines():
        if line.startswith("  ") and not line.startswith("   ") and line.rstrip().endswith(":") and not line.strip().startswith("#"):
            name = line.strip()[:-1]
            out[name] = ""
        elif name:
            out[name] += line + "\n"
    return out


def test_every_heavy_workflow_waits_for_the_write_before_any_other_job():
    """The two directions stay symmetric: each workflow the write refuses to start beside also waits for the write,
    and no job of it starts before that wait (a job without `needs` would start at once)."""
    heavy = GUARD.read_text().split("HEAVY_WORKFLOWS=(", 1)[1].split(")", 1)[0].split()
    wf_dir = ROOT / ".github" / "workflows"
    for name in heavy:
        text = (wf_dir / name).read_text()
        if "\n  workflow_call:" in text and "\n  workflow_dispatch:" not in text and "\n  schedule:" not in text:
            continue  # a reusable stage runs inside its caller, which waits
        assert "\n  actions: read\n" in text.split("\njobs:\n", 1)[0], name
        jobs = _jobs(text)
        assert "wait-for-fsn-write" in jobs, name
        roots = [j for j, b in jobs.items() if j != "wait-for-fsn-write" and "\n    needs:" not in "\n" + b]
        assert not roots, (name, roots)
