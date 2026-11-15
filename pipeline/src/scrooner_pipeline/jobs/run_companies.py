"""Per-company, resumable, shardable runner for the top-1000 build steps (docmap-load, tagmap-plan, era-guard,
tagmap-dedupe, proof).

`scrooner-map run-companies --step S --company-ids 1,2 | --ids-file F --workers N --state-dir D [step args...]`

One company at a time per worker, each in its own OS process (own statement_timeout, own wall-clock cap, killed with its
process group on expiry). State under <state-dir>/<step>/:
  <id>.done   written only on success; carries a hash of the step args, so a changed argument list (dry run -> --apply)
              is NOT treated as done
  <id>.lock/  directory made with mkdir (atomic); holds the owner pid; a lock whose pid is dead is reclaimed
  <id>.log    the last attempt's output
  failed.txt  the companies that failed every attempt
A failed company is retried (--retries times after the first attempt); the others go on. The runner pauses new starts
while pg_stat_activity is above --pause-above and never runs more workers than --max-connections allows.
Environment: workers get PATH and the database settings explicitly. The runner refuses to start without a database URL,
and for the proof step without a PATH-resolvable zstd (a job started under xargs without PATH once wrote 172k UNCHECKED).
Step args may use {company_id}, {cik}, {ticker}, {state_dir}, {step_dir} placeholders (e.g. per-company output files).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STEPS = ("docmap-load", "tagmap-plan", "era-guard", "tagmap-dedupe", "proof")
# step -> (python module holding the typer app, command)
STEP_APP = {
    "docmap-load": ("scrooner_pipeline.jobs.map", "docmap-load"),
    "tagmap-plan": ("scrooner_pipeline.jobs.map", "tagmap-plan"),
    "era-guard": ("scrooner_pipeline.jobs.map", "era-guard"),
    "tagmap-dedupe": ("scrooner_pipeline.jobs.normalize", "tagmap-dedupe"),
    "proof": ("scrooner_pipeline.jobs.proof", "run"),
}
WORKER_HEAD = 6  # python, -m, module, --worker, app module, statement_timeout


class PreflightError(RuntimeError):
    """The runner refuses to start (the environment cannot support the step)."""


@dataclass(frozen=True)
class Company:
    company_id: int
    cik: str = ""
    ticker: str = ""


@dataclass
class Outcome:
    company_id: int
    status: str  # done | skipped | failed | locked
    attempts: int = 0
    detail: str = ""


def parse_ids(company_ids: str = "", ids_file: Path | None = None) -> list[int]:
    """Ids from a comma list and/or a file (one or several per line, '#' comments). De-duplicated, order kept."""
    raw: list[str] = [x for x in company_ids.replace(" ", "").split(",") if x]
    if ids_file is not None:
        for line in ids_file.read_text().splitlines():
            line = line.split("#", 1)[0]
            raw += [x for x in line.replace(",", " ").split() if x]
    out: list[int] = []
    for x in raw:
        i = int(x)
        if i not in out:
            out.append(i)
    return out


def command_key(argv: Sequence[str]) -> str:
    """Hash of what the step does (command, selector, args), not of the python path or the timeout."""
    body = argv[WORKER_HEAD:] if "--worker" in argv[:4] else argv
    return hashlib.sha256("\x00".join(body).encode()).hexdigest()[:16]


def preflight(step: str, env: Mapping[str, str]) -> None:
    """Refuse to start when the workers' environment cannot run the step."""
    if step not in STEPS:
        raise PreflightError(f"unknown step {step!r}; one of {', '.join(STEPS)}")
    if not env.get("PATH"):
        raise PreflightError("PATH is empty: workers could not find any tool")
    if not env.get("DATABASE_URL"):
        raise PreflightError(
            "DATABASE_URL is not set (environment or .env): refusing to start"
        )
    if step == "proof" and shutil.which("zstd", path=env["PATH"]) is None:
        raise PreflightError(
            "zstd is not on PATH: the proof would write UNCHECKED for every cell; export PATH and retry"
        )


def worker_env(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Environment handed to every worker: the caller's, with PATH and the database settings made explicit (the .env
    file is read once here, so a worker sees the same settings whatever its cwd)."""
    env = dict(os.environ if base is None else base)
    env.setdefault("PATH", os.defpath)
    if base is None:
        try:
            from scrooner_pipeline.common.config import settings

            env.setdefault("DATABASE_URL", settings.database_url)
            env.setdefault("SUPABASE_URL", settings.supabase_url)
            env.setdefault(
                "SUPABASE_SERVICE_ROLE_KEY", settings.supabase_service_role_key
            )
            env.setdefault("SEC_USER_AGENT", settings.sec_user_agent)
        except Exception:  # noqa: BLE001 - preflight reports the missing DATABASE_URL
            pass
    return env


def step_argv(
    step: str,
    company: Company,
    step_args: Sequence[str],
    state_dir: Path,
    python: str = sys.executable,
    statement_timeout: str = "10min",
) -> list[str]:
    """The worker command for one company. The worker bootstrap (this module's __main__) sets the session
    statement_timeout on every connection the step opens, then runs the step's typer app."""
    module, command = STEP_APP[step]
    if step == "proof":
        if not company.cik:
            raise PreflightError(f"company {company.company_id} has no cik for proof")
        selector = ["--ciks", company.cik]
    else:
        selector = ["--company-ids", str(company.company_id)]
    subst = {
        "company_id": str(company.company_id),
        "cik": company.cik,
        "ticker": company.ticker,
        "state_dir": str(state_dir),
        "step_dir": str(state_dir / step),
    }
    args = [a.format(**subst) for a in step_args]
    return [
        python,
        "-m",
        "scrooner_pipeline.jobs.run_companies",
        "--worker",
        module,
        statement_timeout,
        command,
        *selector,
        *args,
    ]


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def acquire_lock(lock: Path) -> bool:
    """mkdir is atomic: exactly one runner takes a company. A lock whose owner pid is dead is reclaimed."""
    for _ in range(2):
        try:
            lock.mkdir()
        except FileExistsError:
            try:
                pid = int((lock / "pid").read_text().strip())
            except (OSError, ValueError):
                return False  # just created by a live runner (pid not written yet)
            if _pid_alive(pid):
                return False
            shutil.rmtree(lock, ignore_errors=True)
            continue
        (lock / "pid").write_text(str(os.getpid()))
        return True
    return False


def release_lock(lock: Path) -> None:
    shutil.rmtree(lock, ignore_errors=True)


def run_one(
    argv: list[str], env: Mapping[str, str], log: Path, wall_clock: float
) -> tuple[bool, str]:
    """One attempt in its own process group; killed at the wall-clock cap. (ok, detail)."""
    with log.open("w") as fh:
        proc = subprocess.Popen(
            argv,
            env=dict(env),
            stdout=fh,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            rc = proc.wait(timeout=wall_clock)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                proc.kill()
            proc.wait()
            return False, f"wall-clock cap {wall_clock:g}s exceeded"
    return (rc == 0), f"exit {rc}"


def process_company(
    company: Company,
    step: str,
    argv: list[str],
    env: Mapping[str, str],
    state_dir: Path,
    *,
    retries: int,
    wall_clock: float,
    retry_wait: float,
    wait_for_db: Callable[[], None],
) -> Outcome:
    step_dir = state_dir / step
    cid = company.company_id
    done = step_dir / f"{cid}.done"
    key = command_key(argv)
    if done.exists():
        try:
            if json.loads(done.read_text()).get("args_hash") == key:
                return Outcome(cid, "skipped", 0, "done marker")
        except (OSError, ValueError):
            pass
    lock = step_dir / f"{cid}.lock"
    if not acquire_lock(lock):
        return Outcome(cid, "locked", 0, "another runner holds the lock")
    try:
        detail = ""
        for attempt in range(1, retries + 2):
            wait_for_db()
            ok, detail = run_one(argv, env, step_dir / f"{cid}.log", wall_clock)
            if ok:
                done.write_text(
                    json.dumps(
                        {
                            "company_id": cid,
                            "step": step,
                            "args_hash": key,
                            "attempts": attempt,
                            "at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                )
                return Outcome(cid, "done", attempt, detail)
            if attempt <= retries:
                time.sleep(retry_wait)
        return Outcome(cid, "failed", retries + 1, detail)
    finally:
        release_lock(lock)


def db_gate(
    count_connections: Callable[[], int], pause_above: int, poll: float = 15.0
) -> Callable[[], None]:
    """Blocks while the database holds more than `pause_above` connections. A failing probe also waits."""

    def wait() -> None:
        while True:
            try:
                n = count_connections()
            except Exception:  # noqa: BLE001 - a hung/failed probe is a reason to wait, not to run
                n = pause_above + 1
            if n <= pause_above:
                return
            time.sleep(poll)

    return wait


def effective_workers(workers: int, max_connections: int, per_worker: int = 1) -> int:
    """Each worker holds `per_worker` connections; the total stays within max_connections."""
    return max(1, min(workers, max_connections // max(1, per_worker)))


@dataclass
class RunReport:
    outcomes: list[Outcome] = field(default_factory=list)

    def of(self, status: str) -> list[int]:
        return [o.company_id for o in self.outcomes if o.status == status]


def run_companies(
    companies: Sequence[Company],
    step: str,
    step_args: Sequence[str],
    state_dir: Path,
    *,
    workers: int = 1,
    max_connections: int = 8,
    retries: int = 3,
    wall_clock: float = 3600.0,
    statement_timeout: str = "10min",
    retry_wait: float = 5.0,
    wait_for_db: Callable[[], None] = lambda: None,
    env: Mapping[str, str] | None = None,
    argv_for: Callable[[Company], list[str]] | None = None,
) -> RunReport:
    env = worker_env() if env is None else dict(env)
    preflight(step, env)
    (state_dir / step).mkdir(parents=True, exist_ok=True)
    n = effective_workers(workers, max_connections)
    build = argv_for or (
        lambda c: step_argv(
            step, c, step_args, state_dir, statement_timeout=statement_timeout
        )
    )
    report = RunReport()
    mu = threading.Lock()

    def job(c: Company) -> None:
        o = process_company(
            c,
            step,
            build(c),
            env,
            state_dir,
            retries=retries,
            wall_clock=wall_clock,
            retry_wait=retry_wait,
            wait_for_db=wait_for_db,
        )
        with mu:
            report.outcomes.append(o)

    with ThreadPoolExecutor(max_workers=n) as pool:
        list(pool.map(job, companies))
    failed = sorted(report.of("failed"))
    failed_file = state_dir / step / "failed.txt"
    if failed:
        failed_file.write_text("\n".join(map(str, failed)) + "\n")
    elif failed_file.exists():
        failed_file.unlink()
    return report


def _worker(argv: list[str]) -> None:
    """`python -m scrooner_pipeline.jobs.run_companies --worker <app module> <statement_timeout> <command...>`:
    every connection the step opens gets its own statement_timeout, then the step's typer app runs."""
    import importlib

    import psycopg

    module, timeout, *rest = argv
    real = psycopg.connect

    def connect(*a: Any, **kw: Any) -> Any:
        conn = real(*a, **kw)
        conn.execute(f"set statement_timeout = '{timeout}'")
        conn.commit()  # a later rollback (dry run) must not undo the session setting
        return conn

    psycopg.connect = connect  # type: ignore[assignment]
    importlib.import_module(module).app(rest, standalone_mode=True)


def count_pg_connections() -> int:
    import psycopg

    from scrooner_pipeline.common.config import settings

    with psycopg.connect(settings.database_url, connect_timeout=20) as conn:
        conn.execute("set statement_timeout = '20s'")
        row = conn.execute("select count(*) from pg_stat_activity").fetchone()
        return int(row[0]) if row else 0


def lookup_companies(ids: Sequence[int]) -> list[Company]:
    """id -> (cik, ticker), read-only, one indexed query."""
    import psycopg

    from scrooner_pipeline.common.config import settings

    with psycopg.connect(settings.database_url) as conn:
        conn.execute("set statement_timeout = '60s'")
        conn.execute("set transaction read only")
        rows = conn.execute(
            "select id, cik, coalesce(primary_ticker, '') from core.company where id = any(%s)",
            (list(ids),),
        ).fetchall()
    by_id = {r[0]: Company(r[0], r[1], r[2]) for r in rows}
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise PreflightError(f"no core.company row for ids {missing}")
    return [by_id[i] for i in ids]


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--worker":
        _worker(sys.argv[2:])
    else:
        sys.exit("usage: --worker <app module> <statement_timeout> <command...>")
