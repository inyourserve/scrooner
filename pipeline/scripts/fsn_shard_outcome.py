"""Fail an FSN write shard that silently did nothing (FSN write run 42561798991: every company failed in the
pilot, the write step found no cells, and only an incidental crash turned the shard red).

usage: python3 pipeline/scripts/fsn_shard_outcome.py <out_dir> <comma-separated CIKs>
  ::error::  and exit 1 when the shard had companies but out/report.json has no company report
  ::warning:: when out/failed.json lists companies, or out/load.json counts load errors
Reads local files only (stdlib).
"""

import json
import sys
from pathlib import Path


def outcome(out: Path, ciks: list[str]) -> tuple[list[str], int]:
    """GitHub workflow annotations and the exit code."""
    lines: list[str] = []
    reports = failed = None
    try:
        reports = json.loads((out / "report.json").read_text())
    except (OSError, ValueError):
        pass
    try:
        failed = json.loads((out / "failed.json").read_text())
    except (OSError, ValueError):
        pass
    try:
        load_errors = int(
            json.loads((out / "load.json").read_text()).get("errors") or 0
        )
    except (OSError, ValueError, AttributeError):
        load_errors = 0
    if failed:
        lines.append(
            f"::warning::{len(failed)} of {len(ciks)} companies failed in the pilot (out/failed.json)"
        )
    if load_errors:
        lines.append(
            f"::warning::{load_errors} companies failed to load (out/load.json errors)"
        )
    if ciks and not reports:
        lines.append(
            f"::error::the shard had {len(ciks)} companies and no company report: nothing can be written"
        )
        return lines, 1
    return lines, 0


if __name__ == "__main__":
    out_dir, ciks_arg = Path(sys.argv[1]), sys.argv[2]
    annotations, code = outcome(out_dir, [c for c in ciks_arg.split(",") if c])
    print("\n".join(annotations) or "shard outcome: ok")
    sys.exit(code)
