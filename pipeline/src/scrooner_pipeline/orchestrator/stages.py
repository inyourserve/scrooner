"""Stage runner for the worker: maps PIPELINE.md stages onto the existing commands, unchanged.

  1 ingest   `scrooner-fsn nightly` + `load --increment` for the company's missing filings (new_filing items only);
             SEC at most SCROONER_EDGAR_MAX_RPS = 1 request/second, and only the single ingest worker runs it
  2 know     skipped: the rule store is repo files, already at the code sha this run checked out
  3 resolve  scripts/top100_flow.sh <company_id> c<company_id> (loader, structural load, tagmap plan, era guard)
  4 prove    the same flow's proof --write, display state export and verifier self-check; this stage reads the flow's
             result line and records it (a HELD_CERTIFIED / guard failure line stops stage 5)
  6 serve    skipped while rule serve.shown_cell_path@1 is off (PIPELINE.md M3 hard gate: the shown view has no quarter grain)
  5 certify  read-only: top100_open_shown.py + top100_gate.py on the exported coverage, then FILE a request
             (ops.certify_request + the request md in the publish folder). It never records a verdict, a registry row or a
             certificate: only the approver does (display_cert.record_verdict).

`dry_run` items run no stage that writes: stages 1 and 3 are skipped with the reason, nothing is filed.
Exit codes of top100_flow.sh: 11 docmap-load, 12 structural-load, 21 tagmap-plan (stage 3); 31 proof, 41 era-guard
(stage 4); 2 no worktree, 13 no-filing check, 90 zstd missing (permanent).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from collections.abc import Callable
from pathlib import Path

from . import cohort
from .versions import detector_version
from .worker import Blocked, Item, Permanent, StageResult, Transient

ROOT = Path(__file__).resolve().parents[4]
TRANSIENT = re.compile(
    r"server closed the connection|connection (?:reset|refused|timed out|to server)|could not connect|"
    r"too many clients|remaining connection slots|SSL SYSCALL|terminating connection|"
    r"\b(?:429|500|502|503|504)\b|Too Many Requests|Service Unavailable|Gateway Time-?out|"
    r"ReadTimeout|ConnectTimeout|temporarily unavailable|canceling statement due to statement timeout|"
    r"OperationalError|PoolTimeout",
    re.I,
)
FLOW_STAGE = {11: 3, 12: 3, 21: 3, 31: 4, 41: 4}
FLOW_PERMANENT = {2: "no_worktree", 13: "no_filing_check_failed", 90: "zstd_missing"}


def classify(code: int, tail: str, stage: int) -> Exception:
    """Transient when the log shows a network/pooler/rate-limit signature, else Permanent with the exit code."""
    msg = f"exit {code}: {tail.strip()[-600:]}"
    if code in FLOW_PERMANENT:
        return Permanent(msg, FLOW_PERMANENT[code], stage)
    if TRANSIENT.search(tail):
        return Transient(msg, "transient", stage)
    return Permanent(msg, f"exit_{code}", stage)


def sh(
    cmd: list[str],
    *,
    log: Path,
    env: dict[str, str] | None = None,
    cwd: Path = ROOT,
    timeout: int = 6 * 3600,
) -> tuple[int, str]:
    log.parent.mkdir(parents=True, exist_ok=True)
    try:
        with log.open("wb") as fh:
            p = subprocess.run(
                cmd,
                cwd=cwd,
                env={**os.environ, **(env or {})},
                stdout=fh,
                stderr=subprocess.STDOUT,
                timeout=timeout,
            )
        code = p.returncode
    except subprocess.TimeoutExpired:
        return 124, "command timed out (ReadTimeout)"
    return code, log.read_text(errors="replace")[-4000:]


class FlowRunner:
    def __init__(
        self,
        conn,
        members: dict[str, cohort.Member],
        out: Path,
        *,
        root: Path = ROOT,
        run: Callable[..., tuple[int, str]] = sh,
        fsn_cmd: list[str] | None = None,
        run_url: str = "",
    ):
        self.conn, self.members, self.out, self.root, self.run_cmd = (
            conn,
            members,
            out,
            root,
            run,
        )
        self.fsn = fsn_cmd or ["uv", "run", "--project", "pipeline", "scrooner-fsn"]
        self.run_url = run_url

    def member(self, item: Item) -> cohort.Member:
        m = self.members.get(item.cik)
        if m is None:
            raise Permanent(
                f"cik {item.cik} is not in the cohort of this run", "not_in_cohort"
            )
        return m

    def run(self, stage: int, item: Item) -> StageResult:
        return getattr(self, f"stage{stage}")(item)

    # --- stages -----------------------------------------------------------------------------------------------
    def stage1(self, item: Item) -> StageResult:
        if item.dry_run:
            return StageResult("skipped", {"reason": "dry_run"})
        d = self.out / f"ingest-{item.cik}"
        env = {"SCROONER_EDGAR_MAX_RPS": "1"}
        code, tail = self.run_cmd(
            [
                *self.fsn,
                "nightly",
                "--out",
                str(d / "companies"),
                "--ciks",
                item.cik,
                "--since",
                "2014-01-01",
                "--max-minutes",
                "60",
                "--report",
                str(d / "nightly.json"),
            ],
            log=d / "nightly.log",
            env=env,
            cwd=self.root,
        )
        if code != 0:
            raise classify(code, tail, 1)
        built = d / "companies" / "ciks.txt"
        ciks = built.read_text().strip() if built.exists() else ""
        if not ciks:
            return StageResult("done", {"built": 0})
        code, tail = self.run_cmd(
            [
                *self.fsn,
                "load",
                "--companies",
                str(d / "companies"),
                "--ciks",
                ciks,
                "--increment",
                "--report",
                str(d / "load.json"),
            ],
            log=d / "load.log",
            env=env,
            cwd=self.root,
        )
        if code != 0:
            raise classify(code, tail, 1)
        return StageResult("done", {"built": len(ciks.split(","))})

    def stage2(self, item: Item) -> StageResult:
        return StageResult(
            "skipped",
            {"reason": "rule store is repo files at the checked-out code sha"},
        )

    def stage3(self, item: Item) -> StageResult:
        m = self.member(item)
        if item.dry_run:
            return StageResult(
                "skipped", {"reason": "dry_run: the flow writes production rows"}
            )
        if not cohort.in_rank_source(m.company_id, self.root):
            raise Permanent(
                f"company {m.company_id} ({m.ticker}) rank {m.rank} is not in the rank source top100_coverage reads "
                f"({cohort.SUMMARY}); give the run a universe file (TOP100_RANK_SOURCE) that holds it",
                "cohort_unsupported",
                3,
            )
        if not (
            self.root / f"data-team/tags/line_map/resolver/{m.ticker}.csv"
        ).is_file():
            # not a failure: the resolver-data-refresh batch (dispatched by the plan job, rank order) writes the file
            raise Blocked(
                f"{m.ticker} has no resolver/{m.ticker}.csv yet", "blocked_on_resolver"
            )
        log = self.out / f"flow-{m.company_id}.log"
        code, tail = self.run_cmd(
            ["zsh", "scripts/top100_flow.sh", str(m.company_id), f"c{m.company_id}"],
            log=log,
            env={"TOP100_CI": os.environ.get("TOP100_CI", "1")},
            cwd=self.root,
        )
        if code != 0:
            raise classify(code, tail, FLOW_STAGE.get(code, 3))
        return StageResult("done", {"log": str(log)})

    def _flow_line(self, company_id: int) -> str:
        f = self.root / ".runs/top100_flow/flow_results.tsv"
        if not f.exists():
            return ""
        lines = [
            ln
            for ln in f.read_text().splitlines()
            if ln.split("\t")[1:2] == [str(company_id)]
        ]
        return lines[-1] if lines else ""

    def stage4(self, item: Item) -> StageResult:
        m = self.member(item)
        if item.dry_run:
            return StageResult("skipped", {"reason": "dry_run"})
        line = self._flow_line(m.company_id)
        if not line:
            raise Permanent(
                "the flow exited 0 but wrote no result line", "no_result_line", 4
            )
        held = re.search(
            r"HELD_CERTIFIED|RESTORE_FAILED|REPROOF_FAILED|GUARD_ERROR|NOCSV|NO_RESULT_LINE",
            line,
        )
        return StageResult(
            "done",
            {
                "flow_line": line.split("\t", 2)[-1],
                "held": held.group(0) if held else None,
                "gate_ready": " GATE_READY" in line,
            },
        )

    def stage6(self, item: Item) -> StageResult:
        return StageResult(
            "skipped",
            {
                "reason": "serve.shown_cell_path@1 is off (PIPELINE.md M3 hard gate: quarter grain)"
            },
        )

    def stage5(self, item: Item) -> StageResult:
        m = self.member(item)
        if item.dry_run:
            return StageResult("skipped", {"reason": "dry_run: nothing is filed"})
        s4 = self.conn.execute(
            "select detail from ops.work_item_stage where work_item_id = %s and stage = 4",
            (item.id,),
        ).fetchone()
        d4 = (s4[0] if s4 else {}) or {}
        if d4.get("held"):
            return StageResult(
                "skipped",
                {"reason": f"flow line {d4['held']}: a held company files no request"},
            )
        o = self.root / f".runs/top100_flow/run_c{m.company_id}"
        cv = o / "coverage_held" if (o / "coverage_held").is_dir() else o / "coverage"
        pub = self.root / f".runs/top100_flow/publish_c{m.company_id}"
        pub.mkdir(parents=True, exist_ok=True)
        self.run_cmd(
            [
                "python3",
                "-I",
                "scripts/ci/top100_open_shown.py",
                str(cv),
                str(m.company_id),
                str(pub),
            ],
            log=pub / "open_shown.log",
            cwd=self.root,
        )  # exit 2 = no export: reported by the gate below
        res = self.root / "data-team/tags/line_map/resolver"
        code, tail = self.run_cmd(
            [
                "python3",
                "-I",
                "scripts/ci/top100_gate.py",
                "--coverage-csv",
                str(cv / "top100-coverage.csv"),
                "--company-id",
                str(m.company_id),
                "--out-dir",
                str(pub),
                "--resolver",
                str(res),
            ],
            log=pub / "gate.log",
            cwd=self.root,
        )
        gate = {}
        if (pub / "gate.json").exists():
            gate = json.loads((pub / "gate.json").read_text())
        decision = gate.get("decision", "ERROR")
        if code == 2 or decision == "ERROR":
            raise Permanent(f"gate error: {tail.strip()[-300:]}", "gate_error", 5)
        if decision != "PASS":
            return StageResult(
                "done",
                {
                    "decision": decision,
                    "reason": gate.get("reason", "")[:300],
                    "filed": False,
                },
            )
        csvs = sorted(pub.glob(f"{m.ticker}-coverage-*.csv"))
        reqs = sorted(pub.glob(f"{m.ticker}-request-*.md"))
        if not csvs or not reqs:
            raise Permanent(
                "gate said PASS but wrote no coverage csv / request md",
                "gate_files_missing",
                5,
            )
        sha = hashlib.sha256(csvs[-1].read_bytes()).hexdigest()
        judge = f"{detector_version(self.root)}+gate@1"
        path = f"data-team/strategy/approvals/requests/{reqs[-1].name}"
        cur = self.conn.execute(
            """insert into ops.certify_request (work_item_id, ticker, coverage_sha256, judge_version, request_path)
               values (%s, %s, %s, %s, %s) on conflict (ticker, coverage_sha256, judge_version) do nothing returning id""",
            (item.id, m.ticker, sha, judge, path),
        )
        new = cur.fetchone() is not None
        return StageResult(
            "done",
            {
                "decision": "PASS",
                "filed": new,
                "request_path": path,
                "coverage_sha256": sha,
            },
        )
