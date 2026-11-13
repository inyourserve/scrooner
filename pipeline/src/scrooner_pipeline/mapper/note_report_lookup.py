"""Note R page per (accession, tag): the cached lookup the coverage export uses for note-only facts.

The FSN store (fsn_store/shard.py) keeps only the statement rows of the SEC FSN pre.tsv (stmt in BS/IS/CF/CI/EQ/...),
so a fact that is on no statement line (cash paid for interest, a tax note line, the cover-page share count) has no
report in fsn.line. The SEC pre.tsv itself lists every presentation line, notes included, with its report number
(the R<n>.htm page of the filing). This module reads that pre.tsv from the local quarter cache for exactly the
(accession, tag) pairs asked for and keeps them in a small committed CSV. No database write, no migration.

FILING-CHECKED source: SEC Financial Statement and Notes pre.tsv (the filing's own presentation linkbase).
"""

from __future__ import annotations

import csv
import io
import re
import subprocess
from collections import defaultdict
from pathlib import Path

COLUMNS = ["accession", "tag", "report", "n_reports", "line", "plabel"]
DEFAULT_PATH = (
    Path(__file__).resolve().parents[4]
    / "data-team"
    / "47-fsn-store"
    / "note_report_lookup.csv"
)


def load_lookup(path: Path | None = None) -> dict[tuple[str, str], int]:
    """(accession, tag) -> report number of the lowest-numbered report that presents the tag. Empty if no file."""
    p = path or DEFAULT_PATH
    if not p.exists():
        return {}
    with p.open(newline="") as fh:
        return {
            (r["accession"], r["tag"]): int(r["report"])
            for r in csv.DictReader(fh)
            if r["report"]
        }


def scan_pre(
    pre_path: Path, wanted: set[tuple[str, str]]
) -> dict[tuple[str, str], list[tuple[int, int, str]]]:
    """(adsh, tag) -> [(report, line, plabel)] for the wanted pairs found in one pre.tsv.zst (streamed)."""
    found: dict[tuple[str, str], list[tuple[int, int, str]]] = defaultdict(list)
    wanted_adsh = {a for a, _t in wanted}
    proc = subprocess.Popen(["zstd", "-dc", str(pre_path)], stdout=subprocess.PIPE)
    assert proc.stdout is not None
    fh = io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace", newline="")
    for r in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
        a = r["adsh"]
        if a in wanted_adsh and (a, r["tag"]) in wanted:
            try:
                found[(a, r["tag"])].append(
                    (int(r["report"]), int(r["line"]), r.get("plabel") or "")
                )
            except ValueError:
                continue
    proc.wait()
    return found


def build_rows(
    cache_dir: Path, wanted: set[tuple[str, str]]
) -> tuple[list[dict[str, object]], set[tuple[str, str]]]:
    """Scan every cached quarter's pre.tsv.zst; return (csv rows, wanted pairs not found in any quarter)."""
    hits: dict[tuple[str, str], list[tuple[int, int, str]]] = defaultdict(list)
    for pre in sorted(cache_dir.glob("*/*_pre.tsv.zst")):
        todo = {k for k in wanted if k not in hits}
        if not todo:
            break
        for k, v in scan_pre(pre, todo).items():
            hits[k].extend(v)
    rows = []
    for (acc, tag), v in sorted(hits.items()):
        reps = sorted(set(v))
        rep, line, label = reps[0]
        rows.append(
            {
                "accession": acc,
                "tag": tag,
                "report": rep,
                "n_reports": len({x[0] for x in reps}),
                "line": line,
                "plabel": label,
            }
        )
    return rows, wanted - set(hits)


DEFREF = re.compile(r"defref_[A-Za-z0-9\-]+_([A-Za-z0-9]+)'")


def scan_edgar(
    client: object, cik: str | int, adsh: str, tags: set[str]
) -> dict[str, tuple[int, int]]:
    """Option B, for a filing newer than the published SEC FSN data sets: sec.gov FilingSummary.xml, then each
    R page of the filing; a tag is on a page when the page links its definition (defref_<prefix>_<Tag>).
    Returns tag -> (lowest report number, number of reports). `client` is fsn_store.edgar_fetch.EdgarClient."""
    import xml.etree.ElementTree as ET

    from scrooner_pipeline.fsn_store.edgar_fetch import filing_base

    base = filing_base(cik, adsh)
    summary = client.get(f"{base}/FilingSummary.xml").content  # type: ignore[attr-defined]
    pages = []
    for r in ET.fromstring(summary).iter("Report"):
        m = re.match(r"R(\d+)\.htm$", (r.findtext("HtmlFileName") or "").strip())
        if m:
            pages.append(int(m.group(1)))
    seen: dict[str, list[int]] = defaultdict(list)
    for n in sorted(set(pages)):
        html = client.get(f"{base}/R{n}.htm").text  # type: ignore[attr-defined]
        for t in set(DEFREF.findall(html)) & tags:
            seen[t].append(n)
    return {t: (min(v), len(v)) for t, v in seen.items()}
