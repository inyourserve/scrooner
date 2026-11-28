#!/usr/bin/env python3
"""Publish the files the orchestrator's workers produced (the publish job of pipeline-orchestrator.yml).

Workers hold the DB secret but no write permission to the repo; this job holds contents: write and no DB secret. For every
company folder in the downloaded artifacts it applies exactly what top100-flow's publish job applies, as ONE commit:
  - data-team/strategy/open-shown/<TICKER>.csv  (written when open > 0, removed when 0 and the file exists)
  - the company's row in data-team/strategy/top100-coverage-summary.csv (scripts/ci/top100_coverage_merge.py --summary-only)
  - on a gate PASS: data-team/strategy/certification/<T>-coverage-*.csv and approvals/requests/<T>-request-*.md
    (the certify REQUEST; the verdict, registry row and certificate are recorded only by the approver)
Only these named paths are added. Push retry loop: fetch, reset to origin/main, re-apply (idempotent), commit, push.

usage: orchestrator_publish.py PARTS_DIR [--repo .] [--run-url URL] [--retries 30] [--no-push]
"""

import argparse
import json
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path


def git(repo, *a, check=True):
    r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(a)}: {r.stderr.strip()[:300]}")
    return r


def companies(parts: Path):
    """(company_id, publish dir, coverage dir or None) for every flow folder in the artifacts."""
    seen = {}
    for pub in sorted(parts.rglob("publish_c*")):
        if pub.is_dir() and pub.name[len("publish_c"):].isdigit():
            cid = pub.name[len("publish_c"):]
            cv = None
            for name in ("coverage_held", "coverage"):
                c = next((d for d in parts.rglob(f"run_c{cid}/{name}") if d.is_dir()), None)
                if c is not None and (c / "top100-coverage-summary.csv").is_file():
                    cv = c
                    break
            seen[cid] = (pub, cv)
    return [(cid, *v) for cid, v in sorted(seen.items(), key=lambda kv: int(kv[0]))]


def apply(repo: Path, parts: Path) -> list[str]:
    """Copy the files into the checkout; return the named paths to add."""
    paths: list[str] = []
    for cid, pub, cv in companies(parts):
        js = pub / "open-shown.json"
        if js.is_file():
            d = json.loads(js.read_text())
            tk, n = d["ticker"], int(d["open"])
            if not tk or any(ch not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-" for ch in tk):
                raise ValueError(f"bad ticker {tk!r}")
            f = repo / "data-team/strategy/open-shown" / f"{tk}.csv"
            if n > 0:
                f.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(pub / "open-shown.csv", f)
                paths.append(str(f.relative_to(repo)))
            elif f.exists():
                f.unlink()
                paths.append(str(f.relative_to(repo)))
        if cv is not None:
            r = subprocess.run([sys.executable, "-I", "scripts/ci/top100_coverage_merge.py", "--from", str(cv), "--into",
                                "data-team/strategy", "--company-ids", cid, "--summary-only"], cwd=repo, capture_output=True, text=True)
            if r.returncode:
                raise RuntimeError(f"coverage merge for {cid}: {r.stderr.strip()[:300]}")
            paths.append("data-team/strategy/top100-coverage-summary.csv")
        g = pub / "gate.json"
        if g.is_file() and json.loads(g.read_text()).get("decision") == "PASS":
            for src, dst in (("*-coverage-*.csv", "data-team/strategy/certification"),
                             ("*-request-*.md", "data-team/strategy/approvals/requests")):
                for f in sorted(pub.glob(src)):
                    (repo / dst).mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(f, repo / dst / f.name)
                    paths.append(f"{dst}/{f.name}")
    return list(dict.fromkeys(paths))


def publish(repo: Path, parts: Path, run_url: str = "", retries: int = 30, push: bool = True, sleep=time.sleep) -> str:
    last = ""
    for _ in range(retries):
        try:
            if push:
                git(repo, "fetch", "-q", "origin", "main")
                git(repo, "reset", "-q", "--hard", "origin/main")
            paths = apply(repo, parts)
            if not paths:
                return "nothing to publish"
            git(repo, "add", "--", *paths)
            if git(repo, "diff", "--cached", "--quiet", check=False).returncode == 0:
                return "unchanged"
            n = len(companies(parts))
            git(repo, "commit", "-q", "-m", f"Orchestrator: files for {n} companies ({run_url or 'local'})")
            if not push:
                return "committed (no push)"
            git(repo, "push", "-q", "origin", "HEAD:main")
            return "pushed"
        except RuntimeError as e:
            last = str(e)
            sleep(random.randint(3, 20))
    raise SystemExit(f"publish failed after {retries} tries: {last}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("parts")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--run-url", default="")
    ap.add_argument("--retries", type=int, default=30)
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    print(publish(Path(a.repo).resolve(), Path(a.parts), a.run_url, a.retries, not a.no_push))
    return 0


if __name__ == "__main__":
    sys.exit(main())
