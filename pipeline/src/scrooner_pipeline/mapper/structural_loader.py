"""Structural loader: the Tag Expert's structural resolver output (data-team/tags/STRUCTURAL-MAPPING.md,
data-team/tags/line_map/) becomes analytics.company_tag_map rows under ONE generated rule source,
rule_id company_tag_map.structural@1, decided_by structural_resolver, for every company at once. No per-ticker fix files.

INPUT (CSV files; a directory loads every recognised file, a file loads itself). One row per company x data point x
fiscal year (the filing's OWN column; a later filing is never carried back):
  ticker, [cik], data_point, decision (or status), period_end, accession, tags, [stmts|stmt], [r_pages|r_lines|lines],
  [label], [calc_parent], [path], [filing_checks], [era_from], [era_to], [filed], [value], [action]
- decision: mapped | component_sum | combined | not_presented | not_in_template   -> loaded
            derived / derived_not_printed (a computed value is a new perimeter, founder ruling) -> counted, not loaded
            no_role (the resolver found no node: a gap, NOT evidence of absence)  -> counted, not loaded
- tags: '+'/';' separated parts, each `[-][taxonomy:]LocalName`; a leading '-' is the part's sign (the calc weight).
  Without a taxonomy prefix the taxonomy is looked up (the company's SEC tags, then core.concept; us-gaap wins).
  A part with no sign is +1: a resolver that emits weights must write '-' on the -1 parts.
- stmts: per part ('BS+BS+NOTE') or one for all; the r_pages tokens may carry it too ('BS R5:21+BS R5:22+NOTE').
- r_pages: per part 'R5:21' (report 5, line 21) or one token for all parts; NOTE = no R page.
- filing_checks: the filer's own calc arithmetic on the filing ('calc Assets: ok;calc ...: FAIL'). A filing with any
  FAIL is quarantined: none of its rows load (STRUCTURAL-MAPPING.md section 2).
- era: each row covers its own fiscal year (day after the previous year ended .. period_end; 52/53-week neighbours
  close, as docmap fixes do) unless era_from/era_to are given. --open-last leaves each series' last era open-ended.
- three shapes are recognised: the per-filing line_map CSVs (<TICKER>.csv), the per-cell shape above (also the
  structural-fixrows-* files) and the total_debt-* cell files (data point total_debt, columns tags/r_pages/accession).
  Rows whose `action` is review_missing_column_value or no_structural_node are skipped (not a decision).
  A later-dated file corrects an earlier one for the same cell.

PRECEDENCE, per (company, concept, period), kind-merged as docmap-load does (a value competes with values, a
reason with reasons, a combined line with both):
  1. hand fix rows (company_tag_map.docmap_fix@1) win their cells; every structural cell they cover is listed in the
     exceptions report (agreeing or not);
  2. structural clips docmap@1, era_extend@1 and predictor/guard rows around its eras (the other years stay);
  3. library rows follow the docmap merge rule: same decision and tags -> the library row stands; different -> the
     structural row wins (it cites a filing page) and the library row is cut around the era; a library `combined`
     line is the Tag Expert's call (the structural cell is dropped and listed).
Validation: unknown concept, bad tags, every 0122 table rule (company_tag_map_seed.normalize), instant sums, a row is
rejected alone. Idempotent: a rerun replaces the structural rows of the (company, concept) pairs in the input.
Dry run unless apply=True; one transaction per company; a company whose merged map would overlap is skipped whole.
"""

from __future__ import annotations

import csv
import itertools
import re
from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.mapper.company_tag_map import STATEMENT_CODE
from scrooner_pipeline.mapper.company_tag_map_seed import (
    INSERT,
    check_overlaps,
    instant_sum_refused,
    normalize,
)

RULE_ID = "company_tag_map.structural@1"
DECIDED_BY = "structural_resolver"
HAND_FIX_RULE_ID = dl.FIX_RULE_ID
# rows structural overrides outright (machine reads): docmap@1, era_extend@1 (and its predictor/guard rows)
MACHINE_RULES = (dl.RULE_ID, dl.era_extend.EXT_RULE_ID)
SINCE = date(2015, 1, 1)
LOADABLE = {"mapped", "component_sum", "combined", "not_presented", "not_in_template"}
NOT_A_DECISION = {"derived", "derived_not_printed", "no_role"}
SKIP_ACTIONS = {"review_missing_column_value", "no_structural_node"}
ACCN_RE = dl.ACCN_RE
STMT_WORDS = {"BS", "IS", "CF", "CI", "EQ", "CP", "UN", "NOTE"}
LOC_RE = re.compile(
    r"\s*(?:(BS|IS|CF|CI|EQ|CP|UN|NOTE)\b)?\s*(?:R(\d+)(?:\.htm)?(?::(\d+))?)?\s*$"
)
FILE_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})\.csv$")
VALUE_DECISIONS = ("concept", "component")


@dataclass(frozen=True)
class Claim:
    ticker: str
    cik: str | None
    data_point: str
    decision: str
    parts: tuple[tuple[int, str | None, str], ...]  # (sign, taxonomy or None, tag)
    stmts: tuple[str, ...]  # per part ('' = the concept's own face)
    locs: tuple[tuple[int | None, int | None], ...]  # per part (R page, line)
    accession: str
    period_end: date
    era_from: date | None = None
    era_to: date | None = None
    label: str = ""
    calc_parent: str = ""
    path: str = ""
    checks: str = ""
    filed: str = ""
    source: str = ""
    file_rank: str = ""
    value: str = (
        ""  # the resolver's value for the cell (checked against the parts' SEC facts)
    )
    node_values: tuple[str, ...] = ()  # per part, when the nodes print them
    grain: str = ""  # FY (duration) or I (instant) of the resolver row; '' for other file shapes


def _split(s: str) -> list[str]:
    return [t.strip() for t in re.split(r"[+;]", s or "") if t.strip()]


def parse_claim_parts(tags: str) -> tuple[tuple[int, str | None, str], ...]:
    out = []
    for t in _split(tags):
        if dl.MEMBER_RE.search(t):
            raise ValueError("member_not_supported")
        sign = -1 if t.startswith("-") else 1
        prefix, sep, local = t.lstrip("-").partition(":")
        tax, tag = (prefix, local) if sep else (None, prefix)
        if not tag or ":" in tag or " " in tag:
            raise ValueError(f"bad tag {t!r}")
        out.append((sign, tax, tag))
    return tuple(out)


def parse_locs(
    r_pages: str, n: int, stmt_col: str, path: str
) -> tuple[tuple[str, ...], tuple[tuple[int | None, int | None], ...]]:
    """Per-part statement codes and (R page, line) from the location tokens, the stmt column and the path text."""
    toks = _split(r_pages)
    locs: list[tuple[str | None, int | None, int | None]] = []
    for t in toks:
        m = LOC_RE.match(t)
        locs.append(
            (
                m.group(1),
                int(m.group(2)) if m and m.group(2) else None,
                int(m.group(3)) if m and m.group(3) else None,
            )
            if m
            else (None, None, None)
        )
    stmt_toks = [
        s.strip().upper() for s in re.split(r"[+;]", stmt_col or "") if s.strip()
    ]
    pm = re.match(r"\s*(BS|IS|CF|CI|EQ)\b", path or "")
    path_stmt = pm.group(1) if pm else ""
    stmts: list[str] = []
    out_locs: list[tuple[int | None, int | None]] = []
    per_loc = len(locs) == n
    for i in range(n):
        lc = locs[i] if per_loc else (locs[0] if locs else (None, None, None))
        s = (
            lc[0]
            or (
                stmt_toks[i]
                if len(stmt_toks) == n
                else (stmt_toks[0] if stmt_toks else "")
            )
            or path_stmt
        )
        stmts.append("UN" if s == "NOTE" else s)
        if per_loc:
            out_locs.append((lc[1], lc[2]))
        else:  # one location for several parts (a single printed line): the page, no per-part line
            out_locs.append((lc[1], lc[2] if n == 1 else None))
    return tuple(stmts), tuple(out_locs)


def _date(v: str) -> date | None:
    v = (v or "").strip()
    if not v:
        return None
    try:
        return date.fromisoformat(v)
    except ValueError:
        return None


NODE_RE = re.compile(
    r"^(?:(?P<tax>[\w.-]+):)?(?P<tag>[A-Za-z0-9_]+)(?:=(?P<val>-?[\d.]+))?\s*(?:\[(?P<loc>[^\]]*)\])?$"
)


def from_resolver(r: dict[str, str], role_stmt: dict[str, str]) -> dict[str, str]:
    """One row of resolver-all110-*.csv (RESOLVER-OUTPUT-FORMAT.md) -> the generic claim dict. `nodes` is
    `Tag[=value] [R4:13 | R4.htm:13 | NOTE | BS R4:18 why]; ... | why: <role and tree path>`."""
    left, _, why = r.get("nodes", "").partition("| why:")
    tags: list[str] = []
    locs: list[str] = []
    vals: list[str] = []
    stmts: list[str] = []
    for node in _split(left.replace("; ", ";")):
        m = NODE_RE.match(node.strip())
        if not m:
            tags.append(node.strip())  # rejected downstream as a bad tag
            locs.append("")
            vals.append("")
            stmts.append("")
            continue
        tags.append((m.group("tax") + ":" if m.group("tax") else "") + m.group("tag"))
        vals.append(m.group("val") or "")
        loc = (m.group("loc") or "").strip()
        lm = LOC_RE_FREE.search(loc)
        sm = re.match(r"(BS|IS|CF|CI|EQ|CP|UN|NOTE)\b", loc)
        stmts.append(sm.group(1) if sm else "")
        locs.append(
            "NOTE"
            if loc.startswith("NOTE")
            else (
                f"R{lm.group(1)}" + (f":{lm.group(2)}" if lm.group(2) else "")
                if lm
                else ""
            )
        )
    out = dict(r)
    out["tags"] = "+".join(tags)
    out["r_pages"] = "+".join(locs)
    out["stmts"] = (
        "+".join(stmts) if any(stmts) else role_stmt.get(r.get("data_point", ""), "")
    )
    out["path"] = why.strip()
    out["filing_checks"] = r.get("calc_check", "")
    out["node_values"] = "+".join(vals)
    return out


LOC_RE_FREE = re.compile(r"R(\d+)(?:\.htm)?(?::(\d+))?")


def role_stmts(path: Path) -> dict[str, str]:
    """data_point -> statement from rules/roles.csv next to the resolver output (the roles rows carry no stmt in the
    output). Empty when the file is absent: the concept's own face is used."""
    for cand in (path / "rules" / "roles.csv", path.parent / "rules" / "roles.csv"):
        if cand.is_file():
            with cand.open(newline="") as fh:
                return {
                    x["data_point"]: x["stmt"].strip().upper()
                    for x in csv.DictReader(fh)
                }
    return {}


def read_claims(path: Path) -> tuple[list[Claim], list[dict], dict[str, int]]:
    """Every recognised file under `path` -> claims, rejects, counters. Pure (no DB)."""
    files = [path] if path.is_file() else sorted(path.glob("*.csv"))
    roles = role_stmts(path)
    claims: list[Claim] = []
    rejects: list[dict] = []
    counts: dict[str, int] = defaultdict(int)
    for p in files:
        if p.name.startswith("_") or "held" in p.name:
            counts["files_skipped"] += 1
            continue
        with p.open(newline="") as fh:
            rd = csv.DictReader(fh)
            head = {(h or "").strip() for h in (rd.fieldnames or [])}
            has_dp = "data_point" in head
            resolver = {"nodes", "calc_check", "grain", "accession"} <= head
            if not (
                resolver
                or {"ticker", "tags", "accession", "period_end"} <= head
                and ({"decision", "status"} & head)
                and (has_dp or {"r_pages", "sum"} & head)
            ):
                counts["files_skipped"] += 1
                continue
            counts["files_read"] += 1
            m = FILE_DATE_RE.search(p.name)
            rank = (m.group(1) if m else "0000-00-00") + p.name
            for raw in rd:
                r = {(k or "").strip(): (v or "").strip() for k, v in raw.items()}
                if resolver:
                    r = from_resolver(r, roles)
                dp = r.get("data_point") or "total_debt"
                decision = (r.get("decision") or r.get("status") or "").strip()
                ticker = r.get("ticker", "").upper()

                def reject(why: str) -> None:
                    rejects.append(
                        {
                            "source": p.name,
                            "ticker": ticker,
                            "data_point": dp,
                            "period_end": r.get("period_end", ""),
                            "decision": decision,
                            "why": why,
                        }
                    )

                if r.get("action", "") in SKIP_ACTIONS:
                    counts["skipped_action"] += 1
                    continue
                if decision in NOT_A_DECISION:
                    counts[f"skipped_{decision}"] += 1
                    continue
                if decision not in LOADABLE:
                    reject(f"unknown decision {decision!r}")
                    continue
                pe = _date(r.get("period_end", ""))
                if pe is None:
                    reject("period_end is not a date")
                    continue
                accn = r.get("accession", "")
                if not ACCN_RE.fullmatch(accn):
                    reject("accession is not an SEC accession number")
                    continue
                tagless = decision in ("combined", "not_presented", "not_in_template")
                try:
                    parts = () if tagless else parse_claim_parts(r.get("tags", ""))
                except ValueError as exc:
                    reject(str(exc))
                    continue
                if not tagless:
                    if not parts:
                        reject(f"{decision} row without a tag")
                        continue
                    if len({(t, g) for _, t, g in parts}) < len(parts):
                        reject("a part tag repeats (members are not separable by tag)")
                        continue
                    if decision == "mapped" and len(parts) != 1:
                        reject(f"mapped row with {len(parts)} tags")
                        continue
                stmts, locs = parse_locs(
                    r.get("r_pages") or r.get("r_lines") or r.get("lines", ""),
                    max(len(parts), 1),
                    r.get("stmts") or r.get("stmt", ""),
                    r.get("path", ""),
                )
                claims.append(
                    Claim(
                        ticker=ticker,
                        cik=(r.get("cik") or "").zfill(10) if r.get("cik") else None,
                        data_point=dp,
                        decision=decision,
                        parts=parts,
                        stmts=stmts if not tagless else (stmts[0],),
                        locs=locs if not tagless else (locs[0],),
                        accession=accn,
                        period_end=pe,
                        era_from=_date(r.get("era_from", "")),
                        era_to=_date(r.get("era_to", "")),
                        label=r.get("label", ""),
                        calc_parent=r.get("calc_parent", ""),
                        path=r.get("path") or r.get("nodes") or r.get("note", ""),
                        checks=r.get("filing_checks", ""),
                        filed=r.get("filed", ""),
                        source=p.name,
                        file_rank=rank,
                        value=r.get("value", ""),
                        grain=r.get("grain", ""),
                        node_values=tuple(
                            x.strip() for x in r.get("node_values", "").split("+")
                        )
                        if r.get("node_values")
                        else (),
                    )
                )
    return claims, rejects, dict(counts)


def assign_eras(
    claims: list[Claim], *, since: date = SINCE, open_last: bool = False
) -> tuple[list[tuple[Claim, date, date | None]], list[dict]]:
    """Claims -> (claim, era_from, era_to): one cell per company x data point x fiscal year. A later file (or later
    filing for the same period) corrects an earlier one; a row whose era ends before `since` is dropped. Pure."""
    log: list[dict] = []
    cells: dict[tuple, Claim] = {}
    for c in claims:
        k = (c.cik or c.ticker, c.data_point, c.period_end)
        old = cells.get(k)
        if old is None or (c.file_rank, c.filed, c.accession) >= (
            old.file_rank,
            old.filed,
            old.accession,
        ):
            if old is not None:
                log.append(
                    {
                        "ticker": c.ticker,
                        "data_point": c.data_point,
                        "period_end": c.period_end.isoformat(),
                        "why": f"superseded: {old.source} {old.accession} by {c.source} {c.accession}",
                    }
                )
            cells[k] = c
        else:
            log.append(
                {
                    "ticker": c.ticker,
                    "data_point": c.data_point,
                    "period_end": c.period_end.isoformat(),
                    "why": f"superseded: {c.source} {c.accession} by {old.source} {old.accession}",
                }
            )
    series: dict[tuple, list[Claim]] = defaultdict(list)
    for k, c in cells.items():
        series[(k[0], k[1])].append(c)
    out: list[tuple[Claim, date, date | None]] = []
    for _, cs in series.items():
        cs.sort(key=lambda c: c.period_end)
        prev_to: date | None = None
        for i, c in enumerate(cs):
            a = c.era_from or dl._fy_start(c.period_end)
            b: date | None = c.era_to or c.period_end
            if c.era_from is None and prev_to is not None:
                if a <= prev_to or (a - prev_to).days <= dl.GAP_CLOSE_DAYS:
                    a = prev_to + timedelta(days=1)
            if open_last and i == len(cs) - 1 and c.era_to is None:
                b = None
            if b is not None and a > b:
                log.append(
                    {
                        "ticker": c.ticker,
                        "data_point": c.data_point,
                        "period_end": c.period_end.isoformat(),
                        "why": "era empty after closing against the previous year",
                    }
                )
                continue
            prev_to = b or date.max
            if b is not None and b < since:
                continue
            out.append((c, a, b))
    return out, log


def quarantined(c: Claim) -> str | None:
    bad = [x.strip() for x in c.checks.split(";") if re.search(r"\bFAIL\b", x)]
    return "; ".join(bad) if bad else None


def evidence_text(c: Claim) -> str:
    bits = [f"structural resolver: {c.path}" if c.path else "structural resolver"]
    if c.checks:
        bits.append(f"filing checks: {c.checks}")
    return "; ".join(bits)


def build_rows(
    c: Claim,
    era_from: date,
    era_to: date | None,
    company_id: int,
    cik: str,
    concept_name: str,
    concept_statement: dict[str, str],
    taxonomy_of: dict[str, str],
) -> list[dict]:
    """Seeder-shaped rows for one cell. Raises ValueError/KeyError on anything the table would refuse. Pure."""
    home = STATEMENT_CODE.get(concept_statement[concept_name], "UN")
    base: dict[str, Any] = {
        "company_id": company_id,
        "cik": cik,
        "era_from": era_from,
        "era_to": era_to,
        "evidence_adsh": c.accession,
        "evidence_plabel": c.label or None,
        "evidence_cal_parent": c.calc_parent or None,
        "decided_by": DECIDED_BY,
        "rule_id": RULE_ID,
    }
    if c.decision in ("combined", "not_presented", "not_in_template"):
        rep, line = c.locs[0]
        reason = c.path or "not printed in this filing"
        if c.decision == "combined":
            reason = f"combined line: {reason}"
        return [
            {
                **base,
                "evidence_report": rep,
                "evidence_line": line,
                "decision": "not_in_template"
                if c.decision == "combined"
                else c.decision,
                "canonical_concept": concept_name,
                "stmt": dl.stmt_code(
                    c.stmts[0] or home,
                    concept_name,
                    concept_statement[concept_name],
                    value_row=False,
                ),
                "reason": f"{reason}; filing checks: {c.checks}"
                if c.checks
                else reason,
                "reason_class": dl.COMBINED_CLASS
                if c.decision == "combined"
                else f"structural_{c.decision}",
            }
        ]
    rows = []
    for i, (sign, tax, tag) in enumerate(c.parts):
        taxonomy = tax or taxonomy_of.get(tag)
        if not taxonomy:
            raise ValueError(f"taxonomy unresolved for tag {tag}")
        rep, line = c.locs[i]
        raw = c.stmts[i] or home
        stmt = dl.stmt_code(
            raw, concept_name, concept_statement[concept_name], value_row=True
        )
        rows.append(
            {
                **base,
                "evidence_report": rep,
                "evidence_line": line,
                "decision": "concept" if c.decision == "mapped" else "component",
                "canonical_concept"
                if c.decision == "mapped"
                else "parent_concept": concept_name,
                "taxonomy": taxonomy,
                "tag": tag,
                "sign": sign,
                "stmt": stmt,
                "reason": evidence_text(c),
                "reason_class": f"structural_{c.decision}",
            }
        )
    return rows


def _key(r: dict) -> int | None:
    return r["canonical_concept_id"] or r["parent_concept_id"]


def _sig(rows: list[dict]) -> frozenset:
    return frozenset(
        (
            r["decision"],
            r["taxonomy"],
            r["tag"],
            r["sign"] if r["decision"] in VALUE_DECISIONS else 1,
        )
        for r in rows
    )


def _kind(r: dict) -> str:
    return "value" if r["decision"] in VALUE_DECISIONS else "reason"


def _overlap(a: date, b: date | None, c: date, d: date | None) -> bool:
    return a <= (d or date.max) and c <= (b or date.max)


def _subtract(
    pieces: list[tuple[date, date | None]], cuts: list[tuple[date, date | None]]
) -> list[tuple[date, date | None]]:
    for ca, cb in cuts:
        nxt: list[tuple[date, date | None]] = []
        for lo, hi in pieces:
            if not _overlap(lo, hi, ca, cb):
                nxt.append((lo, hi))
                continue
            if lo < ca:
                nxt.append((lo, ca - timedelta(days=1)))
            if cb is not None and (hi is None or hi > cb):
                nxt.append((cb + timedelta(days=1), hi))
        pieces = nxt
    return pieces


def _groups(rows: list[dict]) -> list[list[dict]]:
    g: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        g[(r["rule_id"], r["decided_by"], r["era_from"], r["era_to"], _kind(r))].append(
            r
        )
    return list(g.values())


def _tags_of(rows: list[dict]) -> str:
    return "+".join(
        sorted(
            f"{'-' if r['sign'] < 0 else ''}{r['taxonomy']}:{r['tag']}"
            if r["tag"]
            else r["decision"]
            for r in rows
        )
    )


@dataclass
class Plan:
    own_delete: list[int] = field(default_factory=list)
    updates: list[tuple[int, date, date | None]] = field(default_factory=list)
    deletes: list[int] = field(default_factory=list)
    inserts: list[dict] = field(
        default_factory=list
    )  # new structural rows and clip pieces
    conflicts: list[dict] = field(default_factory=list)
    exceptions: list[dict] = field(default_factory=list)
    agree: int = 0
    dropped: int = 0
    value_cells: int = (
        0  # structural value cells (company x data point x period) this load writes
    )
    reason_cells: int = 0
    merged: list[dict] = field(default_factory=list)  # the company's map after the load


def plan_company(
    existing: list[dict],
    cells: list[tuple[Claim, date, date | None, list[dict]]],
    names_by_id: dict[int, str],
) -> Plan:
    """existing: every analytics.company_tag_map row of the company. cells: (claim, era_from, era_to, normalized rows).
    Pure: returns the rows to insert/clip/delete and the reports."""
    plan = Plan()
    keys = {_key(rows[0]) for _, _, _, rows in cells}
    own = [r for r in existing if r["rule_id"] == RULE_ID]
    plan.own_delete = [r["id"] for r in own if _key(r) in keys]
    rest = [r for r in existing if r["rule_id"] != RULE_ID or _key(r) not in keys]
    fixes = [r for r in rest if r["rule_id"] == HAND_FIX_RULE_ID]
    machine = [r for r in rest if r["rule_id"] in MACHINE_RULES]
    library = [
        r
        for r in rest
        if r["rule_id"] not in MACHINE_RULES + (HAND_FIX_RULE_ID, RULE_ID)
    ]
    spans: dict[str, list[tuple[Any, date, date]]] = {"value": [], "reason": []}
    new_rows: list[dict] = []
    for claim, a, b, rows in sorted(cells, key=lambda x: (_key(x[3][0]), x[1])):
        k = _key(rows[0])
        dp_name = names_by_id.get(k or 0, "")
        sig = _sig(rows)
        combined = claim.decision == "combined"
        kind = "value" if rows[0]["decision"] in VALUE_DECISIONS else "reason"

        def compatible(r: dict) -> bool:
            return combined or _kind(r) == kind

        def info(extra: dict, rows: list[dict] = rows, claim: Claim = claim) -> dict:
            return {
                "ticker": claim.ticker,
                "data_point": dp_name,
                "era_from": a.isoformat(),
                "era_to": b.isoformat() if b else "",
                "structural_decision": claim.decision,
                "structural_tags": _tags_of(rows),
                "structural_accession": claim.accession,
                "structural_source": claim.source,
                **extra,
            }

        pieces: list[tuple[date, date | None]] = [(a, b)]
        # 1. hand fixes win their cells and are logged as exceptions
        fix_hit = [
            g
            for g in _groups([r for r in fixes if _key(r) == k])
            if _overlap(a, b, g[0]["era_from"], g[0]["era_to"])
        ]
        for g in fix_hit:
            plan.exceptions.append(
                info(
                    {
                        "agrees": "yes" if _sig(g) == sig else "no",
                        "fix_decision": g[0]["decision"],
                        "fix_tags": _tags_of(g),
                        "fix_era_from": g[0]["era_from"].isoformat(),
                        "fix_era_to": g[0]["era_to"].isoformat()
                        if g[0]["era_to"]
                        else "",
                        "fix_accession": g[0]["evidence_adsh"],
                    }
                )
            )
        pieces = _subtract(
            pieces, [(g[0]["era_from"], g[0]["era_to"]) for g in fix_hit]
        )
        if not pieces:
            plan.dropped += 1
            continue
        # 3. library rows (merge rule of docmap-load)
        lib = [
            r
            for r in library
            if _key(r) == k
            or (r["decision"] == "combined" and dp_name in (r["components"] or []))
        ]
        lib = [r for r in lib if r["decision"] != "excluded"]
        if any(
            r["decision"] == "combined" and _overlap(a, b, r["era_from"], r["era_to"])
            for r in lib
        ):
            plan.conflicts.append(
                info(
                    {
                        "winner": "library",
                        "why": "library combined line: Tag Expert decides",
                        "existing": "",
                    }
                )
            )
            plan.dropped += 1
            continue
        agree_spans: list[tuple[date, date | None]] = []
        for g in _groups([r for r in lib if compatible(r) and _key(r) == k]):
            if not _overlap(a, b, g[0]["era_from"], g[0]["era_to"]):
                continue
            existing_txt = f"{g[0]['rule_id']} {_tags_of(g)} {g[0]['era_from']}..{g[0]['era_to'] or ''}"
            if _sig(g) == sig:
                plan.agree += 1
                agree_spans.append((g[0]["era_from"], g[0]["era_to"]))
            else:
                plan.conflicts.append(
                    info(
                        {
                            "winner": "structural",
                            "why": "structural cites its filing page",
                            "existing": existing_txt,
                        }
                    )
                )
        pieces = _subtract(pieces, agree_spans)
        # 2. machine rows (docmap, era_extend, predictor): overridden, listed when they disagree
        for g in _groups([r for r in machine if _key(r) == k and compatible(r)]):
            if _overlap(a, b, g[0]["era_from"], g[0]["era_to"]) and _sig(g) != sig:
                plan.conflicts.append(
                    info(
                        {
                            "winner": "structural",
                            "why": "structural overrides the machine read",
                            "existing": f"{g[0]['rule_id']} {_tags_of(g)} {g[0]['era_from']}..{g[0]['era_to'] or ''}",
                        }
                    )
                )
        # value beside an existing reason (or the reverse) coexists: the value is served where printed
        for p_a, p_b in pieces:
            for r in rest:
                if (
                    _key(r) == k
                    and not compatible(r)
                    and r["decision"] != "excluded"
                    and _overlap(p_a, p_b, r["era_from"], r["era_to"])
                ):
                    plan.conflicts.append(
                        info(
                            {
                                "winner": "coexist",
                                "why": f"structural {kind} beside an existing {_kind(r)}: both kept",
                                "existing": f"{r['rule_id']} {r['decision']} {r['era_from']}..{r['era_to'] or ''}",
                            }
                        )
                    )
                    break
        for p_a, p_b in pieces:
            if kind == "value":
                plan.value_cells += 1
            else:
                plan.reason_cells += 1
            for r in rows:
                new_rows.append({**r, "era_from": p_a, "era_to": p_b})
            if combined:
                spans["value"].append((k, p_a, p_b or date.max))
                spans["reason"].append((k, p_a, p_b or date.max))
            else:
                spans[kind].append((k, p_a, p_b or date.max))
    # clip the machine and disagreeing library rows around the final structural eras (never delete other years)
    clippable = machine + [r for r in library if _key(r) is not None]
    kept_other = [r for r in rest if r not in clippable]
    out_rows: list[dict] = []
    for knd in ("value", "reason"):
        sub = [r for r in clippable if _kind(r) == knd]
        ks, ups, dels, extras = dl.clip_rows(sub, spans[knd])  # type: ignore[arg-type]
        plan.updates += ups
        plan.deletes += dels
        plan.inserts += extras
        out_rows += ks + extras
    plan.inserts += new_rows
    plan.merged = kept_other + out_rows + new_rows
    plan.merged = [r for r in plan.merged if r.get("id") not in set(plan.deletes)]
    return plan


# ---------------------------------------------------------------------------------------------------------------------


def taxonomies(
    conn: psycopg.Connection, company_ids: set[int], tags: set[str]
) -> tuple[dict[int, dict[str, str]], list[dict]]:
    """company id -> tag -> taxonomy for tags written without a prefix. The company's own SEC tags first, then
    core.concept; us-gaap wins; an ambiguous or unknown tag is left out (the row is rejected alone)."""
    out: dict[int, dict[str, str]] = {c: {} for c in company_ids}
    if not tags:
        return out, []
    with conn.cursor() as cur:
        cur.execute(
            """select s.company_id, c.tag, array_agg(distinct c.taxonomy)
               from analytics.company_sec_tag s join core.concept c on c.id = s.concept_id
               where s.company_id = any(%s) and c.tag = any(%s) group by 1, 2""",
            (sorted(company_ids), sorted(tags)),
        )
        for cid, tag, taxes in cur.fetchall():
            pick = (
                "us-gaap"
                if "us-gaap" in taxes
                else (taxes[0] if len(taxes) == 1 else None)
            )
            if pick:
                out[cid][tag] = pick
        cur.execute(
            "select tag, array_agg(distinct taxonomy) from core.concept where tag = any(%s) group by 1",
            (sorted(tags),),
        )
        glob = {
            t: ("us-gaap" if "us-gaap" in x else (x[0] if len(x) == 1 else None))
            for t, x in cur.fetchall()
        }
    for cid in company_ids:
        for t, p in glob.items():
            if p and t not in out[cid]:
                out[cid][t] = p
    return out, []


def solve_signs(
    claim: Claim, options: list[set[Decimal]]
) -> tuple[tuple[int, ...] | None, str]:
    """The part signs under which the parts sum to the claim's value. `options` = each part's candidate values (the
    node's printed value, else its SEC facts at the period). The declared signs (+1 when none) are tried first, then
    fewest minus signs. Returns (signs, "") or (None, why). Pure."""
    target = Decimal(claim.value)
    n = len(claim.parts)
    if any(not o for o in options):
        miss = [claim.parts[i][2] for i, o in enumerate(options) if not o]
        return None, f"no value to check the sum for part(s) {','.join(miss)}"
    if n > 10:
        return None, "too many parts to check"
    declared = tuple(sg for sg, _, _ in claim.parts)
    combos = sorted(
        itertools.product((1, -1), repeat=n),
        key=lambda sg: (sg != declared, sg.count(-1)),
    )
    for sg in combos:
        for vals in itertools.product(*[sorted(o) for o in options]):
            if sum(sg[i] * vals[i] for i in range(n)) == target:
                return sg, ""
    return None, "the parts do not sum to the resolver value under any sign pattern"


def fact_options(
    conn: psycopg.Connection, items: list[tuple[int, str, date]]
) -> dict[tuple[int, str, date], set[Decimal]]:
    """(company id, tag, period end) -> authoritative SEC fact values: instants, and durations of about a year."""
    out: dict[tuple[int, str, date], set[Decimal]] = defaultdict(set)
    if not items:
        return out
    cids = sorted({i[0] for i in items})
    tags = sorted({i[1] for i in items})
    ends = sorted({i[2] for i in items})
    with conn.cursor() as cur:
        cur.execute(
            """select f.company_id, c.tag, p.end_date, f.value
               from core.fact f join core.concept c on c.id = f.concept_id
                 join core.period p on p.id = f.period_id
               where f.company_id = any(%s) and c.tag = any(%s) and p.end_date = any(%s) and f.is_authoritative
                 and (p.period_type = 'instant' or p.start_date <= p.end_date - 330)""",
            (cids, tags, ends),
        )
        for cid, tag, end, v in cur.fetchall():
            out[(cid, tag, end)].add(Decimal(v))
    return out


def load(
    conn: psycopg.Connection,
    path: Path,
    *,
    apply: bool = False,
    check_values: bool = True,
    company_ids: set[int] | None = None,
    since: date = SINCE,
    open_last: bool = False,
) -> dict:
    claims, rejects, counts = read_claims(path)
    stats: dict[str, Any] = {
        **counts,
        "claims": len(claims),
        "rejects": rejects,
        "conflicts": [],
        "exceptions": [],
        "blocked": {},
        "companies": {},
        "era_log": [],
        "decisions": defaultdict(int),
        "applied": False,
    }
    cells, stats["era_log"] = assign_eras(claims, since=since, open_last=open_last)
    with conn.cursor() as cur:
        cur.execute("select name, id, statement from analytics.canonical_concept")
        cc = cur.fetchall()
    concept_ids = {n: i for n, i, _ in cc}
    names_by_id = {i: n for n, i in concept_ids.items()}
    concept_statement = {n: s for n, _, s in cc}
    by_ticker = dl.companies_by_ticker(conn)
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik is not null")
        by_cik = {c: i for c, i in cur.fetchall()}
    # resolve companies
    resolved: list[tuple[Claim, date, date | None, int, str]] = []
    for c, a, b in cells:
        if c.cik and c.cik in by_cik:
            cid, cik = by_cik[c.cik], c.cik
        else:
            hits = by_ticker.get(c.ticker, set())
            if len(hits) != 1:
                stats["blocked"][c.ticker] = (
                    f"ticker {c.ticker} resolves to {len(hits)} companies"
                )
                continue
            ((cid, cik),) = hits
        if company_ids is not None and cid not in company_ids:
            continue
        resolved.append((c, a, b, cid, cik))
    need_tax: dict[int, set[str]] = {cid: set() for cid in {r[3] for r in resolved}}
    for c, _, _, cid, _ in resolved:
        need_tax[cid] |= {tag for _, tax, tag in c.parts if tax is None}
    all_tags = set().union(*need_tax.values()) if need_tax else set()
    tax_of, _ = taxonomies(conn, set(need_tax), all_tags)
    by_company: dict[
        int, tuple[str, list[tuple[Claim, date, date | None, list[dict]]]]
    ] = {}
    facts: dict[tuple[int, str, date], set[Decimal]] = {}
    if check_values:
        facts = fact_options(
            conn,
            [
                (cid, tag, c.period_end)
                for c, _, _, cid, _ in resolved
                if c.decision == "component_sum" and c.value and not c.node_values
                for _, _, tag in c.parts
            ],
        )
    for c, a, b, cid, cik in resolved:

        def reject(why: str, c: Claim = c) -> None:
            stats["rejects"].append(
                {
                    "source": c.source,
                    "ticker": c.ticker,
                    "data_point": c.data_point,
                    "period_end": c.period_end.isoformat(),
                    "decision": c.decision,
                    "why": why,
                }
            )

        q = quarantined(c)
        if q:
            reject(f"filing quarantined, its own calc check failed: {q}")
            continue
        if check_values and c.decision == "component_sum" and c.value:
            if (
                c.node_values
                and len(c.node_values) == len(c.parts)
                and all(c.node_values)
            ):
                opts = [{Decimal(v)} for v in c.node_values]
            else:
                opts = [
                    facts.get((cid, tag, c.period_end), set()) for _, _, tag in c.parts
                ]
            try:
                sg, why = solve_signs(c, opts)
            except (ArithmeticError, ValueError) as exc:
                sg, why = None, f"bad value: {exc}"
            if sg is None:
                reject(f"component sum not verified: {why}")
                continue
            c = replace(
                c, parts=tuple((sg[i], t, g) for i, (_, t, g) in enumerate(c.parts))
            )
        name = dl.served_concept(c.data_point, set(concept_ids))
        if name not in concept_ids:
            reject("no canonical concept of that name")
            continue
        if c.decision == "component_sum" and instant_sum_refused(
            name, concept_statement[name]
        ):
            reject("instant component sum refused (only total_debt)")
            continue
        try:
            rows = [
                normalize(t, {}, concept_ids, RULE_ID, [])
                for t in build_rows(
                    c, a, b, cid, cik, name, concept_statement, tax_of[cid]
                )
            ]
        except (ValueError, TypeError, KeyError) as exc:
            reject(f"invalid row: {exc}")
            continue
        stats["decisions"][c.decision] += 1
        by_company.setdefault(cid, (cik, []))[1].append((c, a, b, rows))
    with conn.cursor() as cur:
        cur.execute(
            "select * from analytics.company_tag_map where company_id = any(%s)",
            (sorted(by_company),),
        )
        cols = [x.name for x in cur.description]
        existing: dict[int, list[dict]] = defaultdict(list)
        for row in cur.fetchall():
            rec = dict(zip(cols, row))
            existing[rec["company_id"]].append(rec)
    writes = []
    for cid, (cik, cs) in sorted(by_company.items()):
        plan = plan_company(existing[cid], cs, names_by_id)
        errors = check_overlaps(plan.merged)
        if errors:
            stats["blocked"][cik] = "; ".join(errors[:3])
            continue
        stats["conflicts"] += plan.conflicts
        stats["exceptions"] += plan.exceptions
        before = [r for r in existing[cid] if r["rule_id"] == RULE_ID]
        stats["companies"][cik] = {
            "company_id": cid,
            "cells": len(cs),
            "inserted": len([r for r in plan.inserts if r.get("rule_id") == RULE_ID]),
            "previously_structural": len(plan.own_delete),
            "library_clipped": len(plan.updates),
            "library_deleted": len(plan.deletes),
            "agree": plan.agree,
            "value_cells": plan.value_cells,
            "reason_cells": plan.reason_cells,
            "dropped": plan.dropped,
            "conflicts": len(plan.conflicts),
            "exceptions": len(plan.exceptions),
            "unchanged_structural": len(before) - len(plan.own_delete),
        }
        writes.append((cid, plan))
    stats["decisions"] = dict(stats["decisions"])
    if not apply:
        return stats
    for cid, plan in writes:
        with conn.transaction():
            doomed = plan.own_delete + plan.deletes
            if doomed:
                conn.execute(
                    "delete from analytics.company_tag_map where id = any(%s)",
                    (doomed,),
                )
            with conn.cursor() as cur:
                if plan.updates:
                    cur.executemany(
                        "update analytics.company_tag_map set era_from = %s, era_to = %s where id = %s",
                        [(a, b, rid) for rid, a, b in plan.updates],
                    )
                cur.executemany(INSERT, plan.inserts)
    stats["applied"] = True
    return stats


def spans_of(rows: list[dict]) -> list[tuple[Any, date, date]]:
    """(concept key, era_from, era_to) of structural rows: the cells docmap-load must not overwrite."""
    return sorted(
        {
            (_key(r), r["era_from"], r["era_to"] or date.max)
            for r in rows
            if r["rule_id"] == RULE_ID and _key(r) is not None
        },
        key=repr,
    )
