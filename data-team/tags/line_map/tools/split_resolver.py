#!/usr/bin/env python3
"""Split a single-file resolver output into data-team/tags/line_map/resolver/<TICKER>.csv (one file per company).

usage: split_resolver.py <resolver-all110-or-resolver.csv> [out_dir]      (out_dir default: ../resolver next to this tool)

Run it after resolve_all.py; commit the directory, never the single file (no tracked file over 5 MB, Dhairya 2026-11-21;
GitHub refuses 100 MB, reached at about 370 companies). Every reader (pipeline, flow, gate, auto-trigger, tools) reads the
directory through scrooner_pipeline.mapper.resolver_files. Rows are sorted by key inside each file, so re-splitting the
same rows changes nothing in git.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "pipeline" / "src"))

from scrooner_pipeline.mapper.resolver_files import split_all110  # noqa: E402


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    src = Path(argv[0])
    out = Path(argv[1]) if len(argv) > 1 else HERE.parent / "resolver"
    counts = split_all110(src, out)
    print(
        f"{len(counts)} companies, {sum(counts.values())} rows -> {os.path.relpath(out)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
