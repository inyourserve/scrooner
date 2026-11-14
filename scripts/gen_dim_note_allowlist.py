#!/usr/bin/env python3
"""Write (or --check) pipeline/src/scrooner_pipeline/fsn_store/dim_note_rules.json.

Rerun whenever the resolver or a concept-library rule adds a member part. `--check` exits 1 when the file is stale.
Run from anywhere: the repo root is this file's parent's parent.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline" / "src"))

from scrooner_pipeline.fsn_store import dim_note_allowlist as al  # noqa: E402


def main(argv: list[str]) -> int:
    want = al.render(al.build(ROOT))
    have = al.RULES_FILE.read_text(encoding="utf-8") if al.RULES_FILE.exists() else ""
    if "--check" in argv:
        if want != have:
            print("dim_note_rules.json is stale: run python3 scripts/gen_dim_note_allowlist.py")
            return 1
        print(f"dim_note_rules.json is current ({len(json.loads(want))} rules)")
        return 0
    al.RULES_FILE.write_text(want, encoding="utf-8")
    print(f"wrote {al.RULES_FILE} ({len(json.loads(want))} rules)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
