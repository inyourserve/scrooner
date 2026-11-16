"""Company x tag x metric library, rebuilt on the NEW system (migration 0128, pending).

The repo files stay the reviewed source; the database is the queryable copy. This job regenerates two tables:

  analytics.tag_library_entry   one row per (taxonomy, tag, stmt, data_point, role): what the tag is, which rule decided
                                it, polarity and family, how many companies map it, and how many cells it proves.
  analytics.resolver_decision   one row per resolver cell (company, data point, period end, grain), the newest
                                data-team/tags/line_map/resolver-all110-*.csv, with the tags its nodes name.

from analytics.company_tag_map (rules docmap@1, docmap_fix@1, structural@1, era_extend, predictor, ...), the resolver
output, analytics.cell_proof, the certificates in data-team/strategy/approvals/, and the Tag Expert's files
(data-team/tags/rules/*.csv, data-team/tags/library/standard-tag-library.csv, rules/polarity.csv). The view
analytics.company_tag_metric (same migration) joins company_tag_map -> resolver decision -> metric inputs.

The old library (analytics.sec_tag_library, company_sec_tag, built on the retired concept_mapping) is left as it is:
build-tag-library deletes and refills sec_tag_library weekly, so columns added there would be wiped.

Dry run by default (reads only). Apply runs only from main (GITHUB_REF) and only when the migration's tables and
columns exist. Writes are batched, Decimal-safe (values stay Decimal, never float) and idempotent: each row carries a
content hash, unchanged rows are not touched, rows no longer produced are deleted, all in one transaction per table.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
LINE_MAP_DIR = REPO_ROOT / "data-team" / "tags" / "line_map"
RULES_DIR = REPO_ROOT / "data-team" / "tags" / "rules"
LIBRARY_DIR = REPO_ROOT / "data-team" / "tags" / "library"
POLARITY_CSV = LINE_MAP_DIR / "rules" / "polarity.csv"
APPROVALS_DIR = REPO_ROOT / "data-team" / "strategy" / "approvals"
# Optional FASB taxonomy ingest (RULEBOOK.md: "goes to data-team/tags/taxonomy/"). Not on main on 2026-11-16, so
# deprecated_by / replaces stay NULL until the file exists. Columns: tag, deprecated_by, replaces.
DEPRECATIONS_CSV = REPO_ROOT / "data-team" / "tags" / "taxonomy" / "deprecations.csv"

BATCH = 2000
READ_TIMEOUT = "10min"
WRITE_TIMEOUT = "15min"

RESOLVER_FILE_RE = re.compile(r"^resolver-all110-(\d{4}-\d{2}-\d{2})\.csv$")
CERT_COMPANY_RE = re.compile(r"company[_ ]id\s+(\d+)", re.I)
DECISION_TO_ROLE = {"map": "concept", "component": "component", "excluded": "excluded"}
CELL_DECISIONS = {
    "mapped",
    "component_sum",
    "derived_not_printed",
    "combined",
    "not_presented",
    "not_in_template",  # out of the company's template (resolver .57); never served, not a gap
    "no_role",
}
NAMESPACE_BY_STMT = {
    "BS": "bs",
    "IS": "is",
    "CF": "cf",
    "EQ": "equity",
    "CI": "is",
    "UN": "notes",
    "CP": "per_share",
}

# Tables and columns the migration creates; the job refuses to run without them.
REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "tag_library_entry": (
        "taxonomy",
        "tag",
        "stmt",
        "data_point",
        "role",
        "concept",
        "rule_ids",
        "library_rule_id",
        "library_decision",
        "reason_class",
        "polarity",
        "family",
        "deprecated_by",
        "replaces",
        "companies_mapped",
        "rows_mapped",
        "proven_cells",
        "certified_cells",
        "disagree_cells",
        "unchecked_cells",
        "known_problems",
        "last_verified",
        "content_hash",
        "built_at",
    ),
    "resolver_decision": (
        "company_id",
        "cik",
        "ticker",
        "data_point",
        "period_end",
        "grain",
        "decision",
        "node_tags",
        "nodes",
        "value",
        "accession",
        "column_kind",
        "calc_check",
        "flags",
        "resolver_version",
        "source_file",
        "content_hash",
        "loaded_at",
    ),
}


class MigrationMissing(RuntimeError):
    """The migration's tables or columns are not in the database."""


def base_name(concept: str | None) -> str:
    """Resolver data point of a canonical concept name ('total_assets_resolved' -> 'total_assets')."""
    return re.sub(r"_resolved$", "", concept or "")


def content_hash(parts: list[Any]) -> str:
    return hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str).encode()
    ).hexdigest()[:32]


# ---------------------------------------------------------------- file readers


def newest_resolver_file(directory: Path = LINE_MAP_DIR) -> Path:
    found = sorted(
        (m.group(1), p)
        for p in directory.iterdir()
        if (m := RESOLVER_FILE_RE.match(p.name))
    )
    if not found:
        raise FileNotFoundError(f"no resolver-all110-<date>.csv in {directory}")
    return found[-1][1]


_NODE_TAG_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_.:\-]*)")


def node_tags(nodes: str) -> list[str]:
    """Tags named by the evidence nodes ('Tag[=value] [R4.htm:13]; Tag2=.. | why: ...'), sorted, unique."""
    head = nodes.split(" | why:", 1)[0]
    tags: set[str] = set()
    for part in head.split("; "):
        m = _NODE_TAG_RE.match(part)
        if m:
            tags.add(m.group(1).split(":")[-1])
    return sorted(tags)


def parse_resolver(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Resolver CSV -> cell rows (value as Decimal) and rejects. Key: (cik, data_point, period_end, grain)."""
    rows: dict[tuple[str, str, date, str], dict[str, Any]] = {}
    rejects: list[str] = []
    with path.open(newline="", encoding="utf-8") as fh:
        for n, r in enumerate(csv.DictReader(fh), start=2):
            try:
                if r["decision"] not in CELL_DECISIONS:
                    raise ValueError(f"unknown decision {r['decision']!r}")
                raw = (r.get("value") or "").strip()
                value = Decimal(raw) if raw else None
                key = (
                    r["cik"].zfill(10),
                    r["data_point"],
                    date.fromisoformat(r["period_end"]),
                    r["grain"],
                )
            except (ValueError, InvalidOperation, KeyError) as exc:
                rejects.append(f"{path.name}:{n}: {exc}")
                continue
            rows[key] = {
                "cik": key[0],
                "ticker": r.get("ticker") or None,
                "data_point": key[1],
                "period_end": key[2],
                "grain": key[3],
                "decision": r["decision"],
                "node_tags": node_tags(r.get("nodes") or ""),
                "nodes": r.get("nodes") or None,
                "value": value,
                "accession": r.get("accession") or None,
                "column_kind": r.get("column") or None,
                "calc_check": r.get("calc_check") or None,
                "flags": r.get("flags") or None,
                "resolver_version": r.get("resolver_version") or None,
                "source_file": path.name,
            }
    return list(rows.values()), rejects


def parse_rules(directory: Path = RULES_DIR) -> dict[tuple[str, str], dict[str, Any]]:
    """Tag Expert `tag` rules, one per (stmt, tag): the lowest `order`, then the latest version."""
    best: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted(directory.glob("*.csv")):
        with path.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("kind") != "tag":
                    continue
                try:
                    when, then = json.loads(r["when"]), json.loads(r["then"])
                except (ValueError, KeyError):
                    continue
                stmt, tag = when.get("stmt"), when.get("tag")
                if not stmt or not tag:
                    continue
                cand = {
                    "rule_id": r["rule_id"],
                    "version": int(r.get("version") or 1),
                    "namespace": r.get("namespace") or "",
                    "data_point": r.get("data_point") or "",
                    "decision": then.get("decision") or "",
                    "concept": then.get("concept") or "",
                    "parent_concept": then.get("parent_concept") or "",
                    "reason_class": then.get("reason_class") or "",
                    "note": (r.get("note") or "").strip(),
                    "order": int(when.get("order") or 0),
                }
                cur = best.get((stmt, tag))
                rank = (int(when.get("order") or 0), -int(r.get("version") or 1))
                if cur is None or rank < cur["rank"]:
                    cand["rank"] = rank
                    best[(stmt, tag)] = cand
    return best


def parse_standard_library(
    path: Path = LIBRARY_DIR / "standard-tag-library.csv",
) -> dict[tuple[str, str], str]:
    """(stmt, tag) -> the library's known-misuse caveat (empty rows dropped)."""
    out: dict[tuple[str, str], str] = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if (r.get("caveat") or "").strip():
                    out[(r["stmt"], r["tag"])] = r["caveat"].strip()
    return out


def parse_polarity(path: Path = POLARITY_CSV) -> dict[str, str]:
    """data point -> 'positive' (sign + and normalised), 'signed' (+/-), or 'raw' (common/polarity.py semantics)."""
    out: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            sign, norm = r["sign"].strip(), r["normalise"].strip().upper()
            if sign == "+" and norm == "Y":
                out[r["data_point"].strip()] = "positive"
            elif sign == "raw":
                out[r["data_point"].strip()] = "raw"
            else:
                out[r["data_point"].strip()] = "signed"
    return out


def parse_deprecations(
    path: Path = DEPRECATIONS_CSV,
) -> dict[str, tuple[str | None, str | None]]:
    out: dict[str, tuple[str | None, str | None]] = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                out[r["tag"]] = (
                    (r.get("deprecated_by") or None),
                    (r.get("replaces") or None),
                )
    return out


def certified_company_ids(directory: Path = APPROVALS_DIR) -> set[int]:
    """Companies with an approver certificate (a *-certificate-*.md naming 'company_id N')."""
    ids: set[int] = set()
    for p in directory.glob("*-certificate-*.md"):
        m = CERT_COMPANY_RE.search(p.read_text(encoding="utf-8"))
        if m:
            ids.add(int(m.group(1)))
    return ids


# ---------------------------------------------------------------- entries


@dataclass
class Sources:
    rules: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)
    caveats: dict[tuple[str, str], str] = field(default_factory=dict)
    polarity: dict[str, str] = field(default_factory=dict)
    deprecations: dict[str, tuple[str | None, str | None]] = field(default_factory=dict)


def build_entries(
    tag_map: list[dict[str, Any]], proof: list[dict[str, Any]], src: Sources
) -> list[dict[str, Any]]:
    """Library rows.

    tag_map: one dict per (taxonomy, tag, stmt, role, concept) with companies, rows, rule_ids (sorted list).
    proof:   one dict per (tag, stmt, data_point) with proven, certified, disagree, unchecked, last_proved (date|None).
    Library-only entries (a Tag Expert rule no company maps) are added with zero counts under us-gaap.
    """
    entries: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for t in tag_map:
        dp = base_name(t["concept"])
        key = (t["taxonomy"], t["tag"], t["stmt"], dp, t["role"])
        e = entries.setdefault(
            key,
            {
                "taxonomy": t["taxonomy"],
                "tag": t["tag"],
                "stmt": t["stmt"],
                "data_point": dp,
                "role": t["role"],
                "concept": t["concept"] or "",
                "rule_ids": set(),
                "companies_mapped": 0,
                "rows_mapped": 0,
            },
        )
        e["rule_ids"] |= set(t["rule_ids"])
        e["companies_mapped"] += t["companies"]
        e["rows_mapped"] += t["rows"]
        e["reason_class"] = t.get("reason_class") or ""
    for (stmt, tag), r in src.rules.items():
        role = DECISION_TO_ROLE.get(r["decision"])
        if role is None or any(k[1] == tag and k[2] == stmt for k in entries):
            continue
        dp = base_name(r["concept"]) or r["data_point"]
        key = ("us-gaap", tag, stmt, dp if role != "excluded" else "", role)
        entries.setdefault(
            key,
            {
                "taxonomy": "us-gaap",
                "tag": tag,
                "stmt": stmt,
                "data_point": key[3],
                "role": role,
                "concept": r["concept"],
                "rule_ids": set(),
                "companies_mapped": 0,
                "rows_mapped": 0,
                "reason_class": r["reason_class"],
            },
        )
    by_tag_stmt = defaultdict(list)
    for k in entries:
        by_tag_stmt[(k[1], k[2])].append(k)
    by_tag_dp = defaultdict(list)
    for k in entries:
        by_tag_dp[(k[1], k[3])].append(k)

    counts: dict[tuple, dict[str, Any]] = {
        k: {"proven": 0, "certified": 0, "disagree": 0, "unchecked": 0, "last": None}
        for k in entries
    }
    for p in proof:
        dp = base_name(p["data_point"])
        if p.get("stmt"):
            targets = [
                k for k in by_tag_stmt.get((p["tag"], p["stmt"]), []) if k[3] == dp
            ] or by_tag_stmt.get((p["tag"], p["stmt"]), [])
        else:
            targets = by_tag_dp.get((p["tag"], dp), [])
        # a cell belongs to exactly one entry: the one with the most companies, ties by key (never double counted)
        targets = [
            k for k in targets if entries[k]["role"] in ("concept", "component")
        ] or targets
        if not targets:
            continue
        k = sorted(targets, key=lambda x: (-entries[x]["companies_mapped"], x))[0]
        c = counts[k]
        c["proven"] += p["proven"]
        c["certified"] += p["certified"]
        c["disagree"] += p["disagree"]
        c["unchecked"] += p["unchecked"]
        if p.get("last_proved") and (c["last"] is None or p["last_proved"] > c["last"]):
            c["last"] = p["last_proved"]

    out: list[dict[str, Any]] = []
    for k, e in sorted(entries.items()):
        rule = src.rules.get((e["stmt"], e["tag"]))
        c = counts[k]
        problems: list[str] = []
        caveat = src.caveats.get((e["stmt"], e["tag"]))
        if caveat:
            problems.append(f"library caveat: {caveat}")
        if rule and rule["note"]:
            problems.append(f"rule note ({rule['rule_id']}): {rule['note']}")
        if (
            rule
            and e["companies_mapped"]
            and DECISION_TO_ROLE.get(rule["decision"]) not in (None, e["role"])
        ):
            problems.append(
                f"library rule {rule['rule_id']} says {rule['decision']}; company_tag_map holds it as {e['role']} for {e['companies_mapped']} companies"
            )
        if c["disagree"]:
            problems.append(f"{c['disagree']} cell_proof DISAGREE cells")
        dep, rep = src.deprecations.get(e["tag"], (None, None))
        dp = e["data_point"]
        row = {
            "taxonomy": e["taxonomy"],
            "tag": e["tag"],
            "stmt": e["stmt"],
            "data_point": dp,
            "role": e["role"],
            "concept": e["concept"],
            "rule_ids": sorted(e["rule_ids"]),
            "library_rule_id": rule["rule_id"] if rule else None,
            "library_decision": rule["decision"] if rule else None,
            "reason_class": e.get("reason_class") or None,
            "polarity": src.polarity.get(dp),
            "family": (
                rule["namespace"]
                if rule and rule["namespace"]
                else NAMESPACE_BY_STMT.get(e["stmt"])
            ),
            "deprecated_by": dep,
            "replaces": rep,
            "companies_mapped": e["companies_mapped"],
            "rows_mapped": e["rows_mapped"],
            "proven_cells": c["proven"],
            "certified_cells": c["certified"],
            "disagree_cells": c["disagree"],
            "unchecked_cells": c["unchecked"],
            "known_problems": sorted(problems),
            "last_verified": c["last"],
        }
        row["content_hash"] = content_hash([row[f] for f in sorted(row)])
        out.append(row)
    return out


def with_company_ids(
    cells: list[dict[str, Any]], cik_to_id: dict[str, int | None]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Attach company_id; unknown or ambiguous CIKs are dropped and counted, never guessed."""
    out, stats = [], {"unknown_cik": 0, "ambiguous_cik": 0}
    for c in cells:
        if c["cik"] not in cik_to_id:
            stats["unknown_cik"] += 1
        elif cik_to_id[c["cik"]] is None:
            stats["ambiguous_cik"] += 1
        else:
            row = {**c, "company_id": cik_to_id[c["cik"]]}
            row["content_hash"] = content_hash(
                [row[f] for f in sorted(row) if f != "content_hash"]
            )
            out.append(row)
    return out, stats


def plan(existing: dict[tuple, str], new: dict[tuple, str]) -> dict[str, int]:
    """Counts of what an apply would do, from key -> content_hash maps."""
    return {
        "insert": sum(1 for k in new if k not in existing),
        "update": sum(1 for k, h in new.items() if k in existing and existing[k] != h),
        "unchanged": sum(1 for k, h in new.items() if existing.get(k) == h),
        "delete": sum(1 for k in existing if k not in new),
    }


# ---------------------------------------------------------------- database


def check_migration(cur: Any) -> None:
    missing: list[str] = []
    for table, cols in REQUIRED_COLUMNS.items():
        cur.execute(
            "select column_name from information_schema.columns where table_schema = 'analytics' and table_name = %s",
            (table,),
        )
        have = {r[0] for r in cur.fetchall()}
        if not have:
            missing.append(f"analytics.{table} (table)")
        else:
            missing += [f"analytics.{table}.{c}" for c in cols if c not in have]
    if missing:
        raise MigrationMissing(
            "migration 0128 (company x tag x metric library) is not applied: missing "
            + ", ".join(missing)
            + ". It needs the founder's typed go; nothing was read or written."
        )


_TAG_MAP_SQL = """
select coalesce(tm.taxonomy, 'us-gaap') as taxonomy, tm.tag, tm.stmt, tm.decision as role,
       coalesce(cc.name, pc.name, '') as concept, count(*) as rows, count(distinct tm.company_id) as companies,
       array_agg(distinct tm.rule_id order by tm.rule_id) as rule_ids, max(tm.reason_class) as reason_class
from analytics.company_tag_map tm
left join analytics.canonical_concept cc on cc.id = tm.canonical_concept_id
left join analytics.canonical_concept pc on pc.id = tm.parent_concept_id
where tm.tag is not null
group by 1, 2, 3, 4, 5
"""

# latest verdict per cell (basis latest), counted by the structure-selected tag (position_tag) and statement
_PROOF_SQL = """
with latest as (
    select distinct on (company_id, data_point_name, period_grain, period_start, period_end)
           company_id, data_point_name, position_tag, fsn_stmt, verdict, proved_at
    from analytics.cell_proof
    where basis = 'latest' and position_tag is not null
    order by company_id, data_point_name, period_grain, period_start, period_end, proved_at desc
)
select position_tag as tag, fsn_stmt as stmt, data_point_name as data_point,
       count(*) filter (where verdict = 'PROVEN') as proven,
       count(*) filter (where verdict = 'PROVEN' and company_id = any(%s)) as certified,
       count(*) filter (where verdict = 'DISAGREE') as disagree,
       count(*) filter (where verdict = 'UNCHECKED') as unchecked,
       (max(proved_at) filter (where verdict = 'PROVEN'))::date as last_proved
from latest group by 1, 2, 3
"""

_ENTRY_COLS = [c for c in REQUIRED_COLUMNS["tag_library_entry"] if c != "built_at"]
_ENTRY_KEY = ("taxonomy", "tag", "stmt", "data_point", "role")
_RES_COLS = [c for c in REQUIRED_COLUMNS["resolver_decision"] if c != "loaded_at"]
_RES_KEY = ("company_id", "data_point", "period_end", "grain")


def _chunks(seq: list[Any], n: int = BATCH):
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def read_inputs(
    cur: Any, certified: set[int]
) -> tuple[list[dict], list[dict], dict[str, int | None]]:
    cur.execute(f"set local statement_timeout = '{READ_TIMEOUT}'")
    cur.execute(_TAG_MAP_SQL)
    names = [d.name for d in cur.description]
    tag_map = [dict(zip(names, r, strict=True)) for r in cur.fetchall()]
    cur.execute(_PROOF_SQL, (sorted(certified),))
    names = [d.name for d in cur.description]
    proof = [dict(zip(names, r, strict=True)) for r in cur.fetchall()]
    cur.execute("select cik, id from core.company where cik is not null")
    cik_to_id: dict[str, int | None] = {}
    for cik, cid in cur.fetchall():
        cik_to_id[cik.zfill(10)] = None if cik.zfill(10) in cik_to_id else cid
    return tag_map, proof, cik_to_id


def existing_hashes(cur: Any, table: str, key: tuple[str, ...]) -> dict[tuple, str]:
    cur.execute(f"select {', '.join(key)}, content_hash from analytics.{table}")
    return {tuple(r[:-1]): r[-1] for r in cur.fetchall()}


def write_table(
    cur: Any,
    table: str,
    cols: list[str],
    key: tuple[str, ...],
    rows: list[dict[str, Any]],
    ts_col: str,
) -> dict[str, int]:
    """Stage, upsert only changed rows (content hash), delete rows no longer produced. One transaction."""
    cur.execute(f"set local statement_timeout = '{WRITE_TIMEOUT}'")
    cur.execute(
        f"create temporary table _stage (like analytics.{table} including defaults) on commit drop"
    )
    ph = ", ".join(["%s"] * len(cols))
    sql = f"insert into _stage ({', '.join(cols)}) values ({ph})"
    for chunk in _chunks(rows):
        cur.executemany(sql, [[r[c] for c in cols] for r in chunk])
    set_list = (
        ", ".join(f"{c} = excluded.{c}" for c in cols if c not in key)
        + f", {ts_col} = now()"
    )
    on = " and ".join(f"t.{k} = s.{k}" for k in key)
    cur.execute(
        f"insert into analytics.{table} ({', '.join(cols)}) select {', '.join(cols)} from _stage "
        f"on conflict ({', '.join(key)}) do update set {set_list} "
        f"where analytics.{table}.content_hash is distinct from excluded.content_hash"
    )
    upserted = cur.rowcount
    cur.execute(
        f"delete from analytics.{table} t where not exists (select 1 from _stage s where {on})"
    )
    return {"upserted": upserted, "deleted": cur.rowcount}


def rebuild(conn: Any, *, apply: bool, github_ref: str | None = None) -> dict[str, Any]:
    """Dry run (default): reads only, returns the plan. Apply: only from refs/heads/main."""
    if (
        apply
        and (github_ref if github_ref is not None else os.environ.get("GITHUB_REF"))
        != "refs/heads/main"
    ):
        raise PermissionError(
            "apply runs only from main (GITHUB_REF=refs/heads/main); this is a dry run context"
        )
    resolver_path = newest_resolver_file()
    cells, rejects = parse_resolver(resolver_path)
    src = Sources(
        parse_rules(), parse_standard_library(), parse_polarity(), parse_deprecations()
    )
    certified = certified_company_ids()
    with conn.cursor() as cur:
        cur.execute("set transaction read only") if not apply else None
        check_migration(cur)
        tag_map, proof, cik_to_id = read_inputs(cur, certified)
        entries = build_entries(tag_map, proof, src)
        res_rows, cik_stats = with_company_ids(cells, cik_to_id)
        ex_e = existing_hashes(cur, "tag_library_entry", _ENTRY_KEY)
        ex_r = existing_hashes(cur, "resolver_decision", _RES_KEY)
        result = {
            "resolver_file": resolver_path.name,
            "resolver_rejects": rejects,
            "cik_stats": cik_stats,
            "certified_companies": len(certified),
            "deprecation_file": DEPRECATIONS_CSV.exists(),
            "tag_library_entry": plan(
                ex_e,
                {tuple(e[k] for k in _ENTRY_KEY): e["content_hash"] for e in entries},
            ),
            "resolver_decision": plan(
                ex_r,
                {tuple(r[k] for k in _RES_KEY): r["content_hash"] for r in res_rows},
            ),
            "entry_rows": len(entries),
            "resolver_rows": len(res_rows),
        }
        if apply:
            result["written_entry"] = write_table(
                cur, "tag_library_entry", _ENTRY_COLS, _ENTRY_KEY, entries, "built_at"
            )
            result["written_resolver"] = write_table(
                cur, "resolver_decision", _RES_COLS, _RES_KEY, res_rows, "loaded_at"
            )
    if apply:
        conn.commit()
    else:
        conn.rollback()
    return result
