"""Committed, hash-pinned inputs and the evidence containers.

Every pinned file input is verified against its sha256 before use, so a silent
edit of the template or the group assignment changes the dry-run loudly instead
of changing which cells get a reason."""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from scrooner_pipeline.reasons.model import BaselineCell, CellKey

REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = REPO_ROOT / "data-team" / "strategy" / "data"
SCOREBOARD_DIR = REPO_ROOT / "data-team" / "strategy" / "scoreboard"

GROUP_ASSIGNMENT_PATH = DATA_DIR / "group_assignment_v2.csv"
TEMPLATE_PATH = DATA_DIR / "template_v1_draft.csv"
DEPENDENCY_GRAPH_PATH = DATA_DIR / "metric_dependency_graph.csv"
BASELINE_DEFECTS_PATH = (
    SCOREBOARD_DIR / "defects" / "2026-10-20.defects.map-v2.1.csv.gz"
)
F1_REMOVED_PATH = SCOREBOARD_DIR / "maps" / "d0e_removed_30.txt"

# Pinned: origin/work/sector-analyst/groups @ 43ba4df (WO-4 group.assign@2, template v1 draft).
PINNED_SHA256 = {
    "group_assignment_v2.csv": "30faa345ba320d60b5e9ee006938081619cf60865f6fd805b73690472d87c446",
    "template_v1_draft.csv": "5c8226716fd483a3172d6c21802ff26419306c773b48a25a7ff7c7d6950767e0",
}
TEMPLATE_VERSION = "tv1-draft-2026.10.22"


class InputHashError(RuntimeError):
    pass


def _read_bytes_checked(path: Path, verify: bool = True) -> bytes:
    raw = path.read_bytes()
    want = PINNED_SHA256.get(path.name)
    if verify and want is not None:
        got = hashlib.sha256(raw).hexdigest()
        if got != want:
            raise InputHashError(f"{path.name}: sha256 {got} != pinned {want}")
    return raw


def _rows(raw: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))


# --- baseline ----------------------------------------------------------------
def load_baseline(path: Path = BASELINE_DEFECTS_PATH) -> dict[CellKey, BaselineCell]:
    """The 2026-10-20 scoreboard defect register (map v2.1): every blank cell of
    the 986 x 163 cohort plus the 116 valued-with-reason cells."""
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out: dict[CellKey, BaselineCell] = {}
    for r in rows:
        cell = BaselineCell(
            company_id=int(r["company_id"]),
            ticker=r["ticker"],
            data_point=r["data_point_name"],
            kind=r["kind"],
            valued=r["proxy_state"] != "blank",
            gap_reason=r["gap_reason"],
            defect_class=r["defect_class"],
            owner=r["owner"],
            candidate_state=r["candidate_state"],
            root_cause_class=r["root_cause_class"],
        )
        out[cell.key] = cell
    return out


# --- groups and template ----------------------------------------------------
@dataclass(frozen=True)
class GroupRow:
    company_id: int
    group: str
    overlays: tuple[str, ...]
    basis: str
    evidence_accession: str
    evidence_form: str
    evidence_period_end: str
    review_flags: str
    cohort_status: str
    rule_path: str


def load_groups(
    path: Path = GROUP_ASSIGNMENT_PATH, verify: bool = True
) -> dict[int, GroupRow]:
    out: dict[int, GroupRow] = {}
    for r in _rows(_read_bytes_checked(path, verify)):
        if r["cohort_status"] != "cohort_file_v1":
            continue
        out[int(r["company_id"])] = GroupRow(
            company_id=int(r["company_id"]),
            group=r["group"],
            overlays=tuple(o for o in r["overlays"].split(";") if o),
            basis=r["assignment_basis"],
            evidence_accession=r["evidence_accession"],
            evidence_form=r["evidence_form"],
            evidence_period_end=r["evidence_period_end"],
            review_flags=r["review_flags"],
            cohort_status=r["cohort_status"],
            rule_path=r["rule_path"],
        )
    return out


@dataclass(frozen=True)
class TemplateRow:
    scope: str  # group | overlay
    name: str
    data_point: str
    rule: str  # REQ | COND | NIT | REP | n/a
    state_if_false: str
    template_version: str


def load_template(
    path: Path = TEMPLATE_PATH, verify: bool = True
) -> dict[tuple[str, str, str], TemplateRow]:
    out: dict[tuple[str, str, str], TemplateRow] = {}
    for r in _rows(_read_bytes_checked(path, verify)):
        row = TemplateRow(
            scope=r["scope"],
            name=r["group_or_overlay"],
            data_point=r["data_point"],
            rule=r["rule"],
            state_if_false=r["state_if_condition_false"],
            template_version=r["template_version"],
        )
        out[(row.scope, row.name, row.data_point)] = row
    return out


# --- dependency graph -------------------------------------------------------
@dataclass(frozen=True)
class GraphNode:
    data_point: str
    kind: str
    inputs: tuple[tuple[str, str], ...]  # (input data point, role)


def load_graph(path: Path = DEPENDENCY_GRAPH_PATH) -> dict[str, GraphNode]:
    out: dict[str, GraphNode] = {}
    for r in _rows(path.read_bytes()):
        ins = tuple(
            (a, b)
            for a, _, b in (
                p.partition(":") for p in r["direct_inputs(node:role)"].split(";") if p
            )
        )
        out[r["data_point"]] = GraphNode(r["data_point"], r["kind"], ins)
    return out


def load_f1_removed(path: Path = F1_REMOVED_PATH) -> tuple[str, ...]:
    return tuple(x for x in path.read_text().split() if x)


# --- evidence containers (filled by db_evidence.py, or by tests) -------------
@dataclass(frozen=True)
class LineEvidence:
    """One row of analytics.company_filing_line_evidence (migration 0093)."""

    statement: str
    line_present: bool | None
    combined: bool
    matched_label: str | None
    accession_number: str
    form: str


@dataclass(frozen=True)
class TagPresence:
    """Tag-agnostic facts about everything a company ever filed
    (analytics.company_sec_tag): how many distinct tags, and which activity
    families have at least one signal tag among them."""

    tag_count: int
    families: frozenset[str]


@dataclass
class Evidence:
    """Everything the evidence rules read. A `None` section was not loaded: its
    rule reports NOT_RUN. An empty mapping means loaded and nothing found."""

    line: Mapping[CellKey, LineEvidence] | None = None
    tags: Mapping[int, TagPresence] | None = None
    source: str = "none"
