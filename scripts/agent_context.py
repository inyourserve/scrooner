#!/usr/bin/env python3
"""Print a compact, read-only Scrooner context packet for agents."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOARD = "data-team/strategy/TASK-BOARD-TOP1000.md"
GIT = shutil.which("git") or "/usr/bin/git"


def git(*args: str) -> str:
    result = subprocess.run(
        [GIT, *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    return result.stdout.strip()


def board_text() -> str:
    local = ROOT / BOARD
    if local.exists():
        return local.read_text(encoding="utf-8")
    return git("show", f"origin/main:{BOARD}")


def section(text: str, heading: str, next_heading: str, max_lines: int) -> list[str]:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## {re.escape(next_heading)}\n)",
        text,
    )
    if not match:
        return []
    lines = [line.rstrip() for line in match.group(1).strip().splitlines()]
    return lines[:max_lines]


def main() -> int:
    board = board_text()
    print("SCROONER COMPACT CONTEXT")
    print(f"branch: {git('branch', '--show-current') or '(detached)'}")
    print(f"origin/main: {git('log', '-1', '--format=%h %ad %s', '--date=short', 'origin/main')}")
    print(f"local divergence (behind ahead): {git('rev-list', '--left-right', '--count', 'origin/main...HEAD')}")
    print(f"changed paths: {len(git('status', '--porcelain').splitlines())}")

    print("\nSCOREBOARD")
    for line in section(board, "0. The scoreboard (what the user would see today)", "1. Foundations and gates", 32):
        if line.startswith(("**Task count", "** By", "| Certified", "| Companies whose", "| Reasonless", "| Valued", "| Wrong-value", "| Slot-record")):
            print(line)

    print("\nOPEN EXECUTION ROWS")
    rows = [line for line in board.splitlines() if line.startswith("| ")]
    shown = 0
    for line in rows:
        if any(state in line.lower() for state in ("wip", "blocked", "not started", "written")):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 4 and re.fullmatch(r"[FABCR]\d+", cells[0]):
                print(" | ".join(cells[:4]))
                shown += 1
                if shown == 18:
                    break

    print("\nLATEST ORIGIN COMMITS")
    print(git("log", "--oneline", "-5", "origin/main"))
    print("\nRead AGENTS.md for routing. Open only evidence linked by the selected task row.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
