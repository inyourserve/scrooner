#!/usr/bin/env python3
"""Validate local Markdown links without network access."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", "node_modules", "dist", ".astro", ".cache", "worktrees"}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def markdown_files():
    for path in ROOT.rglob("*.md"):
        if not SKIP_PARTS.intersection(path.relative_to(ROOT).parts):
            yield path


def local_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    # Drop an optional Markdown title after a whitespace separator.
    target = target.split(maxsplit=1)[0]
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:")):
        return None
    return unquote(target.split("#", 1)[0])


def main() -> int:
    failures: list[str] = []
    checked = 0
    for document in markdown_files():
        text = document.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = local_target(match.group(1))
            if target is None:
                continue
            checked += 1
            resolved = (ROOT / target.lstrip("/")) if target.startswith("/") else (document.parent / target)
            if not resolved.resolve().exists():
                line = text.count("\n", 0, match.start()) + 1
                failures.append(f"{document.relative_to(ROOT)}:{line}: missing local target {target!r}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        print(f"documentation links: {len(failures)} failure(s), {checked} checked", file=sys.stderr)
        return 1
    print(f"documentation links: {checked} local target(s) checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
