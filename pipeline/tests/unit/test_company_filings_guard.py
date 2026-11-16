"""Guard for the ONE shared rule of which filings belong to a company (common/company_filings.py, ONE-PATH step 2).

No module that decides a company's filing set may filter fsn.filing / core.filing on a raw cik column: a filing
under a predecessor CIK (XOM 0000034088, AVGO 0001441634, DIS 0001001039, MRVL 0001058057 ...) is the company's
and a raw `cik = <company cik>` filter silently drops it. Callers go through company_filings (Python) or embed
fsn_filings_cte / core_filings_cte (SQL). Legitimate cik uses (SEC fetch by CIK, identity) are listed in ALLOWED."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from scrooner_pipeline.common.company_filings import fsn_filings_cte

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "pipeline" / "src" / "scrooner_pipeline"

PY_MODULES = [
    PKG / "mapper" / "structural_loader.py",
    PKG / "mapper" / "structural_direct.py",
    PKG / "mapper" / "docmap_loader.py",
    PKG / "mapper" / "company_tag_map.py",
    PKG / "mapper" / "company_tag_map_plan.py",
    PKG / "mapper" / "top100_coverage.py",
    PKG / "proof" / "fsn_db.py",
    PKG / "proof" / "shown.py",
    PKG / "common" / "instance_facts.py",
    PKG / "jobs" / "fsn.py",
    PKG / "fsn_store" / "increment.py",
    PKG / "fsn_store" / "dim_note.py",
    ROOT / "scripts" / "build_note_report_lookup.py",
]
SQL_DIR = ROOT / "data-team" / "tags" / "line_map" / "tools"
SQL_FILES = sorted(SQL_DIR.glob("*.sql"))
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("pipeline-fsn*.yml"))

_FILING = re.compile(r"\b(fsn|core)\.filing\b(?!_)")
_CIK_FILTER = re.compile(
    r"\b(?:\w+\.)?cik\s*(?:=|<>|!=|in\s*\(|::\s*bigint|\bany\b)", re.I
)

# (file name, a fragment of the SQL string) -> why a cik comparison next to fsn.filing / core.filing is fine
ALLOWED: dict[tuple[str, str], str] = {
    (
        "company_tag_map.py",
        "from core.company_history_source h",
    ): "_merge_predecessor_facts: the predecessor-window fact read itself (joins the source CIK to its core.company "
    "row); the window rule it applies is the one company_filings states",
    (
        "build_note_report_lookup.py",
        "select accession, cik from fsn.filing where accession = any",
    ): "reads the FILER cik of a known accession to build the SEC archive path (a fetch by CIK, not a filing-set filter)",
    (
        "fsn.py",
        "select h.source_cik, c.cik, h.relation",
    ): "_db_history: the loader's alias table (predecessor cik -> company cik) read from core.company_history_source",
}


def _sql_strings(path: Path) -> list[str]:
    out: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append(node.value)
    return out


def _allowed(name: str, text: str) -> bool:
    return any(n == name and frag in text for (n, frag) in ALLOWED)


def raw_cik_filter_offences(name: str, text: str) -> list[str]:
    """The SQL strings that touch fsn.filing / core.filing and compare a cik column."""
    if not _FILING.search(text) or not _CIK_FILTER.search(text):
        return []
    if _allowed(name, text):
        return []
    return [" ".join(text.split())[:140]]


@pytest.mark.parametrize("path", PY_MODULES, ids=lambda p: p.name)
def test_python_modules_do_not_filter_filings_on_a_raw_cik(path: Path):
    assert path.exists(), path
    bad = [
        o
        for s in _sql_strings(path)
        for o in raw_cik_filter_offences(path.name, s)
    ]
    assert not bad, (
        f"{path.name} filters filings on a raw cik column; use company_filings / fsn_filings_cte / "
        f"core_filings_cte (common/company_filings.py) or add an ALLOWED entry with a reason: {bad}"
    )


def _sql_text_without_canonical(text: str) -> str:
    for tok in ("__CIKS__", "/* CIKs */"):
        text = text.replace(fsn_filings_cte(f"co.cik::bigint in ({tok})"), "")
    return text


@pytest.mark.parametrize("path", SQL_FILES + WORKFLOWS, ids=lambda p: p.name)
def test_sql_and_workflow_files_do_not_filter_filings_on_a_raw_cik(path: Path):
    text = _sql_text_without_canonical(path.read_text(encoding="utf-8"))
    # statement-level scan: split on ; and on the CTE comma-newline boundary is overkill; a whole-file scan is
    # enough because the canonical CTE (the only legitimate cik comparison on fsn.filing) was removed above
    bad = []
    for stmt in re.split(r";\s*\n", text):
        # the cik comparison must sit on the same select as fsn.filing / core.filing: scan each "from ... where" piece
        for m in re.finditer(
            r"\b(?:fsn|core)\.filing\b(?!_)[^;]{0,240}", stmt, flags=re.I
        ):
            if _CIK_FILTER.search(m.group(0)) and not re.search(
                r"core\.company_history_source", m.group(0)
            ):
                bad.append(" ".join(m.group(0).split())[:140])
    assert not bad, f"{path.name}: raw cik filter on a filing table: {bad}"


@pytest.mark.parametrize(
    "name", ["extract.sql", "extract_bs.sql", "resolve_cf_extract.sql"]
)
def test_standard_extracts_embed_the_canonical_cte_verbatim(name: str):
    text = (SQL_DIR / name).read_text(encoding="utf-8")
    assert fsn_filings_cte("co.cik::bigint in (__CIKS__)") in text


@pytest.mark.parametrize("name", ["extract_notefacts.sql", "extract_facelines.sql"])
def test_notefacts_extracts_embed_the_canonical_cte_verbatim(name: str):
    text = (SQL_DIR / name).read_text(encoding="utf-8")
    assert fsn_filings_cte("co.cik::bigint in (/* CIKs */)") in text


def test_guard_detects_a_raw_cik_filter():
    bad = "select id from fsn.filing where cik::bigint in (1,2) and form = 'x'"
    assert raw_cik_filter_offences("x.py", bad)
    assert raw_cik_filter_offences(
        "x.py", "select id from core.filing where company_id = any(%s)"
    ) == []
    assert raw_cik_filter_offences("x.py", "select cik from core.company where cik = any(%s)") == []
