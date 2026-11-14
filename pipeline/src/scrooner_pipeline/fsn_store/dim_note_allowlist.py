"""The dimensional-note allowlist (Dhairya decisions 2026-11-14, option B; source = the resolver's own member extract).

The shard keeps a dimensional num row only when its (adsh, tag, version) sits on a statement pre row
(FSN-STORE-DESIGN §2). A concept the library reads from a dimensional NOTE fact (PM FY2022 R60: amortization by
income-statement location, 58 + 101) was therefore never stored. The allowlist is a list of rules
{tag_re, seg_re, qtrs}: a dimensional fact is kept when its tag matches tag_re, its dimension segments match seg_re
(and, when given, its qtrs equals qtrs).

The rules are BUILT FROM CODE, never copied, so they cannot drift from what the resolver reads:
  1. the `mem` CTE of data-team/tags/line_map/tools/extract_notefacts.sql, parsed after the placeholders are filled by
     tools/standard_inputs.build_sql (the element-family regex of rules/roles.csv + extract_families.txt): each
     `[t.tag =|~ '..' and] [v.qtrs = N and] d.segments ~ '..'` disjunct becomes a rule; a disjunct without a tag
     condition applies to the `tgm` tag domain (families + AP/AR + revenue names); extract_legalentity.sql's
     LegalEntity segments pattern applies to the same domain;
  2. every `Tag[Axis=Member]` node the structural resolver prints (data-team/tags/line_map/resolver-*.csv), grouped
     by axis: tag in the printed tags, segments = exactly that axis with any single member;
  3. the concept library's member / class-sum rules (data-team/tags/rules/*.csv): the tags they name, single-dimension.
The CTE's "a statement line exists" condition is dropped on purpose: that condition is the very gap being closed.

The rules are rebuilt at run time by `current()` on every run of the shard and of `scrooner-fsn add-dim-notes`;
dim_note_rules.json is only a REPORT of what the generator (`python3 scripts/gen_dim_note_allowlist.py`) built.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

RULES_FILE = Path(__file__).with_name("dim_note_rules.json")
LEGALENTITY_SQL = "data-team/tags/line_map/tools/extract_legalentity.sql"
STANDARD_INPUTS = "data-team/tags/line_map/tools/standard_inputs.py"
SINGLE_DIM = r"^[A-Za-z][A-Za-z0-9_]*=[^;=]+;$"
_NODE_RE = re.compile(
    r"(?:^|[ ;|])([A-Za-z][A-Za-z0-9_:]*)\[([A-Za-z][A-Za-z0-9_]*)=[^\]]*\]"
)
_MEMBER_RULE_RE = re.compile(r"member|multi_class|class_sum", re.I)
_DISJUNCT_RE = re.compile(
    r"(?:t\.tag\s*(=|~)\s*'([^']*)'\s*and\s*)?(?:v\.qtrs\s*=\s*(\d+)\s*and\s*)?d\.segments\s*~\s*'([^']*)'"
)


def _standard_inputs(root: Path) -> Any:
    spec = importlib.util.spec_from_file_location(
        "standard_inputs", root / STANDARD_INPUTS
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _cte(sql: str, name: str, nxt: str) -> str:
    i = sql.index(f"\n{name} as (")
    return sql[i : sql.index(f"\n{nxt} as (", i)]


def cte_rules(root: Path, sql: str | None = None) -> list[dict[str, Any]]:
    sql = sql or _standard_inputs(root).build_sql([1])
    rx = re.search(r"with rx as \(select '([^']*)'::text r\)", sql).group(1)  # type: ignore[union-attr]
    tgm = _cte(sql, "tgm", "own")
    domain = [
        rx if lit is None else lit
        for lit in (
            m.group(1)
            for m in re.finditer(r"tag ~ (?:\(select r from rx\)|'([^']*)')", tgm)
        )
    ]
    domain_re = "|".join(f"(?:{d})" for d in domain)
    out: list[dict[str, Any]] = []
    for m in _DISJUNCT_RE.finditer(_cte(sql, "mem", "cmp")):
        op, tag, qtrs, seg = m.groups()
        tag_re = (
            domain_re if op is None else (f"^{re.escape(tag)}$" if op == "=" else tag)
        )
        out.append(
            {
                "source": "extract_notefacts.mem",
                "tag_re": tag_re,
                "seg_re": seg,
                "qtrs": int(qtrs) if qtrs else None,
            }
        )
    if not out:
        raise ValueError(
            "no member disjunct parsed from the mem CTE: the extract changed shape"
        )
    le = (root / LEGALENTITY_SQL).read_text(encoding="utf-8")
    for m in re.finditer(r"d\.segments\s*~\s*'([^']*)'", le):
        out.append(
            {
                "source": "extract_legalentity",
                "tag_re": domain_re,
                "seg_re": m.group(1),
                "qtrs": None,
            }
        )
    return out


def resolver_rules(line_map_dir: Path) -> list[dict[str, Any]]:
    axes: dict[str, set[str]] = {}
    csv.field_size_limit(1 << 24)
    for f in sorted(line_map_dir.glob("resolver-*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                for m in _NODE_RE.finditer(
                    (row.get("nodes") or "").split(" | why:")[0]
                ):
                    axes.setdefault(m.group(2), set()).add(m.group(1).split(":")[-1])
    return [
        {
            "source": "resolver_parts",
            "tag_re": "^(" + "|".join(sorted(tags)) + ")$",
            "seg_re": f"^{axis}=[^;=]+;$",
            "qtrs": None,
        }
        for axis, tags in sorted(axes.items())
    ]


def _tags_in(obj: object) -> set[str]:
    if isinstance(obj, str):
        return {obj}
    if isinstance(obj, list):
        return {t for x in obj for t in _tags_in(x)}
    if isinstance(obj, dict):
        return {t for v in obj.values() for t in _tags_in(v)}
    return set()


def library_rules(rules_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, str]] = []
    for f in sorted(rules_dir.glob("*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            rows.extend(csv.DictReader(fh))
    tag_rows: dict[str, set[str]] = {}
    for r in rows:
        if r.get("kind") == "tag":
            try:
                t = json.loads(r["when"]).get("tag")
            except (ValueError, AttributeError):
                continue
            if t:
                tag_rows.setdefault(r["data_point"], set()).add(t)
    tags: set[str] = set()
    for r in rows:
        if r.get("kind") != "procedure" or not _MEMBER_RULE_RE.search(r["rule_id"]):
            continue
        try:
            when = json.loads(r["when"])
        except ValueError:
            continue
        dps: set[str] = set()
        if isinstance(when, dict):
            for key in ("tags", "tag"):
                if key in when:
                    tags |= _tags_in(when[key])
            dps = set(_tags_in(when.get("data_points", [])))
        if re.search(r"multi_class|class_sum", r["rule_id"]):
            dps.add(
                r["data_point"]
            )  # a class-sum rule reads the data point's own tags by member
        for dp in dps:
            tags |= tag_rows.get(dp, set())
    if not tags:
        return []
    return [
        {
            "source": "rules_library",
            "tag_re": "^(" + "|".join(sorted(tags)) + ")$",
            "seg_re": SINGLE_DIM,
            "qtrs": None,
        }
    ]


def build(root: Path) -> list[dict[str, Any]]:
    rules = (
        cte_rules(root)
        + resolver_rules(root / "data-team/tags/line_map")
        + library_rules(root / "data-team/tags/rules")
    )
    for r in rules:
        re.compile(r["tag_re"])
        re.compile(r["seg_re"])
    return rules


def render(rules: list[dict[str, Any]]) -> str:
    return json.dumps(rules, indent=1, sort_keys=True) + "\n"


class Rules:
    def __init__(self, rules: list[dict[str, Any]]):
        self.spec = rules
        self.rules = [
            (re.compile(r["tag_re"]), re.compile(r["seg_re"]), r.get("qtrs"))
            for r in rules
        ]

    def any_segments(self, segments: str) -> bool:
        """True when some rule could match these segments (lets a caller keep only the useful dimension rows)."""
        return any(s.search(segments) is not None for _, s, _ in self.rules)

    def matches(self, tag: str, segments: str, qtrs: int) -> bool:
        return any(
            (q is None or q == qtrs)
            and t.search(tag) is not None
            and s.search(segments) is not None
            for t, s, q in self.rules
        )


REPO_ROOT = Path(__file__).resolve().parents[4]


@lru_cache(maxsize=1)
def current(root: Path | None = None) -> Rules:
    """The rules, REBUILT from the current extract_notefacts.sql / resolver / library at run time (once per process).
    There is no committed snapshot to lag: dim_note_rules.json is only a report written by the generator."""
    root = root or REPO_ROOT
    if not (root / STANDARD_INPUTS).exists():
        raise FileNotFoundError(
            f"{root / STANDARD_INPUTS}: run from a repo checkout (the allowlist is built from it)"
        )
    return Rules(build(root))


load = current  # the name the shard and the insert-only load use


def keep_dimensional(
    adsh: str,
    tag: str,
    version: str,
    segments: str,
    qtrs: int,
    on_stmt: set[tuple[str, str, str]],
    rules: Rules | None = None,
) -> bool:
    """A dimensional num row is kept when its tag has a statement pre row in the filing, or an allowlist rule matches
    its tag, dimension segments and qtrs."""
    return (adsh, tag, version) in on_stmt or (rules or current()).matches(
        tag, segments, qtrs
    )
