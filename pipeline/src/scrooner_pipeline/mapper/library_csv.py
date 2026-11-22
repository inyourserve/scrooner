"""Thin reader of the one tag library, data-team/tags/library/library.csv (built by build_library.py).

The library is the single source of what an element is: data points, polarity, deprecations, caveats, known problems,
metrics (SYSTEMS.md #6, founder 2026-11-22: one tag library). The two DB loaders read it through this module and
never re-derive that knowledge from the raw rule files:

  mapper/tag_library_rebuild.py   analytics.tag_library_entry (polarity, deprecated_by/replaces, caveats, problems)
  mapper/tag_library.py           analytics.sec_tag_library, library stage (mapping status, data points, metrics)

Read-only, no DB, no network. Lists inside a cell are `;`-separated; deprecation items carry `@<year>`.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
LIBRARY_DIR = REPO_ROOT / "data-team" / "tags" / "library"
LIBRARY_CSV = LIBRARY_DIR / "library.csv"
COVERAGE_JSON = LIBRARY_DIR / "coverage.json"
POLARITY_CLASSES = ("positive", "signed", "raw")

csv.field_size_limit(10**8)


def items(cell: str | None) -> list[str]:
    """';'-separated cell -> list, empty items dropped, order kept."""
    return [x.strip() for x in (cell or "").split(";") if x.strip()]


def _element(item: str) -> str:
    """'RevenueFromContract@2018' -> 'RevenueFromContract'."""
    return item.split("@", 1)[0].strip()


def library_path() -> Path | None:
    """The current library.csv: the repo file, or the storage-manifest version once it is out of git (>5 MB rule,
    common/repo_archive.py: verified download cached under .runs/). None when neither is available."""
    from scrooner_pipeline.common import repo_archive

    return repo_archive.resolve("data-team/tags/library/library.csv")


def load(path: Path | None = None) -> dict[str, dict[str, str]]:
    """element -> library row (default: library_path()). Raises FileNotFoundError when the library is not available."""
    path = path or library_path()
    if path is None:
        raise FileNotFoundError(
            "library.csv is neither in the repo nor fetchable from the storage manifest"
        )
    with path.open(newline="", encoding="utf-8") as fh:
        return {r["element"]: r for r in csv.DictReader(fh) if r.get("element")}


def built_for(path: Path = COVERAGE_JSON) -> str:
    """The resolver version the committed library was built from (coverage.json, written with library.csv)."""
    return json.loads(path.read_text(encoding="utf-8")).get("resolver_version") or ""


@dataclass(frozen=True)
class Knowledge:
    """What the DB loaders take from the library, keyed the way they join."""

    polarity: dict[str, str]  # data point -> positive | signed | raw
    deprecations: dict[
        str, tuple[str | None, str | None]
    ]  # element -> (deprecated_by, replaces)
    caveats: dict[
        str, str
    ]  # element -> legacy library caveat (known misuse to check per company)
    problems: dict[
        str, list[str]
    ]  # element -> known problems (filer XBRL errors, FSN dropped facts)


def knowledge(rows: dict[str, dict[str, str]]) -> Knowledge:
    polarity: dict[str, str] = {}
    deprecations: dict[str, tuple[str | None, str | None]] = {}
    caveats: dict[str, str] = {}
    problems: dict[str, list[str]] = {}
    for el, r in rows.items():
        for item in items(r.get("polarity")):
            dp, _, cls = item.rpartition(":")
            if dp and cls in POLARITY_CLASSES:
                polarity[dp] = cls
        by = (
            ";".join(dict.fromkeys(_element(x) for x in items(r.get("deprecated_by"))))
            or None
        )
        rep = ";".join(sorted({_element(x) for x in items(r.get("replaces"))})) or None
        if by or rep:
            deprecations[el] = (by, rep)
        if (r.get("legacy_caveat") or "").strip():
            caveats[el] = "; ".join(items(r["legacy_caveat"]))
        if items(r.get("known_problems")):
            problems[el] = items(r["known_problems"])
    return Knowledge(polarity, deprecations, caveats, problems)


def mapping_status(r: dict[str, str]) -> str:
    """The sec_tag_library status of one library row (0077 vocabulary, now decided by the new system):
    approved = full row (data point, ruling, served, proven or certified); provisional = served or proven for a data point;
    candidate = a resolver alternative never served yet; company_preference = only a company override;
    rejected = only a legacy `excluded` decision; unmapped = none of these."""
    if r.get("full_row") == "yes":
        return "approved"
    dps = items(r.get("data_point"))
    used = any(
        (r.get(k) or "0") not in ("", "0")
        for k in ("served_cells", "proven_cells", "certified_cells")
    )
    if dps and used:
        return "provisional"
    if dps:
        return "candidate"
    if items(r.get("company_overrides")):
        return "company_preference"
    if "excluded" in items(r.get("legacy_decision")):
        return "rejected"
    return "unmapped"


def sec_tag_library_rows(
    rows: dict[str, dict[str, str]],
) -> list[tuple[str, str, str, list[str], list[str], list[str]]]:
    """(taxonomy, element, mapping_status, mapped_concepts, candidate_for_concepts, feeds_metrics) per library row with
    any knowledge. taxonomy is 'us-gaap' for taxonomy elements, else '*' (a company extension: joined by tag name to
    every non-us-gaap core.concept). Concepts are the library's data points."""
    out = []
    for el, r in rows.items():
        status = mapping_status(r)
        metrics = items(r.get("metrics"))
        if status == "unmapped" and not metrics:
            continue
        dps = items(r.get("data_point"))
        mapped = dps if status in ("approved", "provisional") else []
        cand = dps if status == "candidate" else []
        tax = "us-gaap" if r.get("taxonomy") == "us-gaap" else "*"
        out.append((tax, el, status, mapped, cand, metrics))
    return out
