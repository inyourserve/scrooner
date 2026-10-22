"""Shared library for the Scrooner weekly scoreboard (WO-7, Data Triage).

stdlib only. Every figure the scoreboard prints is a function of a CELL EXTRACT
(a csv or csv.gz of coverage cells), the cohort file (shards.csv), and the metric
dependency graph. Nothing here talks to a database.

Evidence labels used in output: MEASURED (computed from a stored extract),
PROXY (DATA-INFERRED classification), REPORTED (taken from a document, not
recomputed), NOT_COMPUTABLE / NOT_RUN (with the dependency named).
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import re
from collections import Counter, defaultdict
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SB_DIR = SCRIPTS.parent                      # data-team/strategy/scoreboard
REPO = SB_DIR.parents[2]                     # repo root of the worktree
SHARDS = REPO / "doc/data-moat/team/top1000/shards.csv"
GRAPH = REPO / "data-team/strategy/data/metric_dependency_graph.csv"
GROUPS_DRAFT = REPO / "data-team/strategy/data/group_assignment_draft.csv"
EXPORT_GZ = SB_DIR / "cells/2026-10-20.cells.csv.gz"
D0_NAMES_FILE = SB_DIR / "maps/d0_datapoints.txt"
D0E_REMOVED_FILE = SB_DIR / "maps/d0e_removed_30.txt"
REASON_MAP = SB_DIR / "reason_class_map.csv"

# ---- frozen identities (FREEZE-REGISTER-2026-10-22 section 4; doc 44) -------------------
EXPORT_SHA256 = "39df9373c0125f6785d1b5403c1c7b265e6b84b79f94451e9d764934a81df36d"
GRAPH_SHA256 = "e548df612612a68acd3541b327d391acf1679226d29dcded81a47ed158ae4ea0"
SHARDS_SHA256 = "477d879535da826ad76aec566055d0305334e70bab83bccefe37e35e285b2927"
IDS_HASH = "f2da5abbf55d1122"
NAMES_HASH = "9d8434ae4fba7852"
D0_CELLS = 160_718
D0E_CELLS = 131_138

# Frozen enums (freeze register section 1)
CLASSES = ("vocabulary", "composition", "period", "ingestion", "resolver", "identity",
           "evidence_pending", "definition_pending", "guard_hidden", "finding_open",
           "filer_error", "unclassified")
OWNERS = ("data_engineer_l1", "data_engineer_l2", "period_engineer", "tag_mapper",
          "standardization_lead", "accountant", "sector_analyst", "verifier", "triage",
          "company_master")
# When several blockers carry different classes, a cascade cell takes the first that
# appears here: real defects before an unknown, an unknown before a candidate-legitimate.
CLASS_PRECEDENCE = ("identity", "resolver", "ingestion", "vocabulary", "composition",
                    "period", "finding_open", "guard_hidden", "filer_error",
                    "definition_pending", "unclassified", "evidence_pending")

# concept-type rows mean "any canonical_fact at any period" (F2); metric rows mean "latest period".
CONCEPT_KINDS = ("leaf_concept", "resolved_concept", "derived_concept", "external_source")
METRIC_KINDS = ("metric", "price_metric")
KIND_ORDER = ("metric", "leaf_concept", "resolved_concept", "derived_concept", "price_metric",
              "external_source")


# ---- hashing / io ------------------------------------------------------------------------
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_decompressed(p: Path) -> str:
    """sha256 of the file's content; for .gz, of the decompressed bytes."""
    if str(p).endswith(".gz"):
        h = hashlib.sha256()
        with gzip.open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    return sha256_file(p)


def id_list_hash(ids) -> str:
    """first 16 hex of sha256 over comma-joined ids sorted NUMERICALLY (freeze register)."""
    return sha256_bytes(",".join(str(i) for i in sorted(int(x) for x in ids)).encode())[:16]


def name_list_hash(names) -> str:
    return sha256_bytes(",".join(sorted(names)).encode())[:16]


def open_text(p: Path):
    if str(p).endswith(".gz"):
        return io.TextIOWrapper(gzip.open(p, "rb"), encoding="utf-8", newline="")
    return open(p, newline="", encoding="utf-8")


def write_gz_deterministic(rows_text: str, dest: Path) -> None:
    """gzip with mtime=0 and no filename so the same text always gives the same bytes."""
    raw = rows_text.encode("utf-8")
    with open(dest, "wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0, compresslevel=9) as gz:
            gz.write(raw)


def pct(num: int, den: int) -> str:
    """percentage to 2 decimals, half-up; '' when the denominator is 0 (never a fake 0)."""
    if den == 0:
        return ""
    q = (Decimal(num) * 100 / Decimal(den)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return format(q, "f")


# ---- cohort / grid ---------------------------------------------------------------------
def load_cohort(shards: Path = SHARDS):
    """-> (ids list sorted numeric, {id: row}) for the non-excluded rows."""
    rows = list(csv.DictReader(open(shards, newline="", encoding="utf-8")))
    keep = {int(r["company_id"]): r for r in rows if not (r.get("excluded") or "").strip()}
    return sorted(keep), keep


def load_graph(path: Path = GRAPH):
    """-> {data_point: {'kind':..., 'inputs': [(node, role), ...]}}"""
    g = {}
    for r in csv.DictReader(open(path, newline="", encoding="utf-8")):
        ins = []
        raw = (r.get("direct_inputs(node:role)") or "").strip()
        if raw:
            for part in raw.split(";"):
                node, _, role = part.partition(":")
                ins.append((node.strip(), role.strip()))
        g[r["data_point"]] = {"kind": r["kind"], "inputs": ins}
    return g


def read_lines(p: Path):
    return [x.strip() for x in open(p, encoding="utf-8").read().splitlines() if x.strip()]


class Extract:
    """A cell extract. Cells are keyed (company_id:int, data_point_name:str).

    Accepts the committed export (company_id,data_point_name,has_value,gap_reason) and the
    live format (adds data_point_type, has_value_any_period, latest_period_end, latest_label,
    absent_from_table). has_value is 't'/'f'/'true'/'false'/'1'/'0'.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.cells: dict[tuple[int, str], dict] = {}
        self.dups = 0
        with open_text(self.path) as fh:
            for r in csv.DictReader(fh):
                key = (int(r["company_id"]), r["data_point_name"])
                if key in self.cells:
                    self.dups += 1
                hv = (r.get("has_value") or "").strip().lower() in ("t", "true", "1")
                absent = (r.get("absent_from_table") or "").strip().lower() in ("t", "true", "1")
                self.cells[key] = {
                    "has_value": hv and not absent,
                    "reason": (r.get("gap_reason") or ""),
                    "absent": absent,
                    "type": (r.get("data_point_type") or ""),
                    "any_period": (r.get("has_value_any_period") or ""),
                    "latest_end": (r.get("latest_period_end") or ""),
                    "latest_label": (r.get("latest_label") or ""),
                }
        self.company_ids = sorted({k[0] for k in self.cells})
        self.names = sorted({k[1] for k in self.cells})

    def __len__(self):
        return len(self.cells)


# ---- reason patterns ----------------------------------------------------------------------
_PAREN = re.compile(r"\([^)]*\)")


def reason_pattern(reason: str) -> str:
    """Strip '(...)' parameters (years, periods). '' stays ''."""
    return _PAREN.sub("(...)", reason)


def reason_tokens(reason: str):
    """Tokens of a cascade reason: 'missing:a(2025),b(2024)...' -> ['a', 'b'];
    returns (kind_prefix, tokens, truncated)."""
    prefix, _, body = reason.partition(":")
    truncated = body.endswith("...")
    body = body[:-3] if truncated else body
    body = _PAREN.sub("", body)
    toks = [t.strip() for t in body.split(",") if t.strip()]
    return prefix, toks, truncated


def load_reason_map(path: Path = REASON_MAP):
    m = {}
    for r in csv.DictReader(open(path, newline="", encoding="utf-8")):
        m[r["pattern_key"]] = r
    return m


# ---- token -> data-point resolution (walk) -----------------------------------------------
TOKEN_ALIASES = {
    "share_count_1y_ago": ["shares_outstanding"],
    "total_debt_or_cash": ["total_debt_resolved", "cash_and_equivalents"],
}


def resolve_token(token: str, dp: str, graph: dict) -> list[str]:
    """Map a name inside a cascade reason to data-point names. [] when it names no data point
    (the caller then falls back, never guesses)."""
    if token in TOKEN_ALIASES:
        return list(TOKEN_ALIASES[token])
    if token in graph:
        return [token]
    if token.endswith("_ttm"):
        base = token[:-4]
        if base in graph:
            return [base]
    if token.startswith("ttm_"):
        base = token[4:]
        for cand in (base, base + "_resolved"):
            if cand in graph:
                return [cand]
    # a role name: inputs of this data point carrying that role (exact or '_'-suffix match)
    ins = graph.get(dp, {}).get("inputs", [])
    hit = [n for n, role in ins if role == token or role.endswith("_" + token)]
    seen, out = set(), []
    for n in hit:
        if n not in seen and n in graph:
            seen.add(n)
            out.append(n)
    return out


class Classifier:
    """Proxy classifier: (company, data point) -> (class, owner, rf_id, note).

    Uses the FROZEN reason_class_map.csv for terminal reasons and for the fallback class of a
    cascade reason. A cascade cell inherits the class of its blocking input cells for the same
    company, walking the dependency graph. Never defaults an unmapped reason: it raises
    UnmappedReason so the caller can list it (must be 0 before the register is published).
    """

    def __init__(self, extract: Extract, graph: dict, reason_map: dict):
        self.x = extract
        self.g = graph
        self.m = reason_map
        self.memo: dict[tuple[int, str], tuple] = {}
        self.unmapped: Counter = Counter()

    def classify(self, cid: int, dp: str, _depth: int = 0):
        key = (cid, dp)
        if key in self.memo:
            return self.memo[key]
        cell = self.x.cells.get(key)
        if cell is None:
            res = ("unclassified", "triage", "", "absent_from_extract")
        elif cell["absent"]:
            res = ("unclassified", "triage", "", "absent_from_table")
        elif cell["has_value"] and not cell["reason"]:
            res = ("", "", "", "valued")
        else:
            res = self._classify_reason(cid, dp, cell, _depth)
        self.memo[key] = res
        return res

    def _classify_reason(self, cid, dp, cell, depth):
        reason = cell["reason"]
        if reason == "":
            return ("unclassified", "triage", "", "null_reason")
        pat = reason_pattern(reason)
        row = self.m.get(pat)
        if row is None:
            self.unmapped[pat] += 1
            return ("unclassified", "triage", "", f"UNMAPPED_REASON:{pat}")
        if row["mode"] == "terminal" or depth > 8:
            return (row["class"], row["owner"], row["rf_id"], f"reason:{pat}")
        # walk
        _, toks, truncated = reason_tokens(reason)
        blockers, notes = [], []
        for t in toks:
            for n in resolve_token(t, dp, self.g):
                c = self.x.cells.get((cid, n))
                if c is None or (c["has_value"] and not c["reason"]):
                    notes.append(f"{n}:valued_latest")
                    continue
                if c["has_value"]:           # valued but carries a reason
                    notes.append(f"{n}:valued_latest")
                    continue
                sub = self.classify(cid, n, depth + 1)
                blockers.append((sub, n))
        if truncated:
            notes.append("reason_list_truncated_in_source")
        if blockers:
            blockers.sort(key=lambda b: CLASS_PRECEDENCE.index(b[0][0]) if b[0][0] in CLASS_PRECEDENCE else 99)
            (cls, owner, rf, _n), name = blockers[0]
            return (cls, owner, rf, f"via:{name}|" + ";".join(notes))
        return (row["class"], row["owner"], row["rf_id"], f"walk_no_blank_input|{pat}|" + ";".join(notes))


# ---- diff of two extracts (RT-2 / M rows) ------------------------------------------------
def diff_extracts(prev: Extract, cur: Extract):
    """cell-level outer join on (company, data point). Returns list of (key, change, prev, cur)
    for every cell whose (has_value, reason) differs or that exists on one side only.
    change in value_appeared, value_disappeared, reason_changed, company_absent_from_table,
    cell_new."""
    out = []
    for key, p in prev.cells.items():
        c = cur.cells.get(key)
        if c is None or c["absent"]:
            out.append((key, "company_absent_from_table", p, c))
            continue
        if p["has_value"] == c["has_value"] and p["reason"] == c["reason"]:
            continue
        if not p["has_value"] and c["has_value"]:
            out.append((key, "value_appeared", p, c))
        elif p["has_value"] and not c["has_value"]:
            out.append((key, "value_disappeared", p, c))
        else:
            out.append((key, "reason_changed", p, c))
    for key, c in cur.cells.items():
        if key not in prev.cells:
            out.append((key, "cell_new", None, c))
    return out


def tally(ext: Extract, graph: dict, names=None):
    """Core counts used by every KPI. names restricts to a subset of data points (D0e)."""
    n = valued = blank = reasonless = vwr = 0
    by_kind = defaultdict(Counter)
    reasons = Counter()
    for (cid, dp), c in ext.cells.items():
        if names is not None and dp not in names:
            continue
        kind = graph.get(dp, {}).get("kind", "?")
        n += 1
        by_kind[kind]["cells"] += 1
        if c["has_value"]:
            valued += 1
            by_kind[kind]["valued"] += 1
            if c["reason"]:
                vwr += 1
                by_kind[kind]["valued_with_reason"] += 1
        else:
            blank += 1
            by_kind[kind]["blank"] += 1
            if not c["reason"]:
                reasonless += 1
                by_kind[kind]["reasonless"] += 1
            reasons[c["reason"]] += 1
    return {"cells": n, "valued": valued, "blank": blank, "reasonless": reasonless,
            "valued_with_reason": vwr, "by_kind": by_kind, "reasons": reasons}


# ---- staleness thresholds read from the product module, never retyped (AT-7.12) ------------
STALENESS_MODULE = REPO / "pipeline/src/scrooner_pipeline/common/staleness.py"


def staleness_thresholds(path: Path = STALENESS_MODULE):
    """-> (annual_max_gap_days, quarterly_max_gap_days) parsed from the module's constants."""
    import ast
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("ANNUAL_MAX_GAP_DAYS", "QUARTERLY_MAX_GAP_DAYS"):
                found[node.targets[0].id] = ast.literal_eval(node.value)
    if set(found) != {"ANNUAL_MAX_GAP_DAYS", "QUARTERLY_MAX_GAP_DAYS"}:
        raise RuntimeError(f"staleness thresholds not found in {path}")
    return found["ANNUAL_MAX_GAP_DAYS"], found["QUARTERLY_MAX_GAP_DAYS"]


def is_stale(label: str, latest_end: str, ref_end: str, annual: int, quarterly: int) -> bool:
    """Mirror of common/staleness.py: stale only when it can be PROVEN old. Dates are ISO strings.
    Missing ref_end / latest_end / unknown label -> not stale."""
    from datetime import date
    if not latest_end or not ref_end or not label:
        return False
    gap = (date.fromisoformat(ref_end[:10]) - date.fromisoformat(latest_end[:10])).days
    if label == "FY":
        return gap > annual
    if label in ("Q1", "Q2", "Q3", "Q4", "TTM"):
        return gap > quarterly
    return False
