"""Sector templates -> per-company template rows (founder ruling 2026-11-01, doc 02).

A field is a cell for a company only if that company's sector template includes it.
This module reads the templates file (markdown tables under fixed headings), resolves
each cohort company to one template (company assignment, else SIC range), applies the
sector defaults, then the company overrides, and writes the full set per company into
analytics.company_data_point_template (migration 0120).

Templates file format (every section is a markdown table under an exact `## ` heading):

    template_version: tv1
    effective_from: 2026-11-01

    ## Sector assignment
    | template | sic_from | sic_to |
    ## Company assignment
    | cik | template | reason |
    ## Sector defaults
    | template | data_point | in_template | reason |
    ## Company overrides
    | cik | data_point | in_template | reason |

Nothing is defaulted silently: a cohort company with no template, overlapping SIC
ranges, a duplicate row, a missing reason or an unknown data point is an error.
The plan is built from files only (the cohort file carries company_id, cik and sic);
the database is read only to validate data-point names and company ids, and written
only by `write_plan`, which the CLI calls behind --apply.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from itertools import pairwise
from pathlib import Path

import psycopg

SECTIONS = {
    "sector assignment": ("template", "sic_from", "sic_to"),
    "company assignment": ("cik", "template", "reason"),
    "sector defaults": ("template", "data_point", "in_template", "reason"),
    "company overrides": ("cik", "data_point", "in_template", "reason"),
}
_REQUIRED_SECTIONS = ("sector assignment", "sector defaults")
_BOOL = {"yes": True, "true": True, "y": True, "no": False, "false": False, "n": False}
_META_RE = re.compile(r"^(template_version|effective_from)\s*:\s*(.+?)\s*$")


class TemplateError(ValueError):
    """The templates file or the cohort cannot produce a complete, unambiguous plan."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__(
            "; ".join(problems[:20]) + (" ..." if len(problems) > 20 else "")
        )


@dataclass(frozen=True)
class Templates:
    template_version: str
    effective_from: date
    sic_ranges: tuple[tuple[str, int, int], ...]
    company_assignment: dict[str, tuple[str, str]]  # cik -> (template, reason)
    defaults: dict[str, dict[str, tuple[bool, str]]]  # template -> dp -> (in, reason)
    overrides: dict[str, dict[str, tuple[bool, str]]]  # cik -> dp -> (in, reason)


@dataclass(frozen=True)
class CohortCompany:
    company_id: int
    cik: str
    sic: int | None


@dataclass(frozen=True)
class TemplateRow:
    company_id: int
    data_point: str
    in_template: bool
    reason: str | None
    effective_from: date
    template: str
    source: str
    template_version: str


def _cik(raw: str) -> str:
    raw = raw.strip()
    if not raw.isdigit():
        raise ValueError(f"cik {raw!r} is not numeric")
    return raw.zfill(10)


def _split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _tables(
    text: str,
) -> tuple[dict[str, str], dict[str, list[dict[str, str]]], list[str]]:
    meta: dict[str, str] = {}
    tables: dict[str, list[dict[str, str]]] = {}
    problems: list[str] = []
    section: str | None = None
    header: list[str] | None = None
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("## "):
            name = s[3:].strip().lower()
            section = name if name in SECTIONS else None
            header = None
            if section is not None:
                if section in tables:
                    problems.append(f"line {n}: section '{name}' appears twice")
                tables.setdefault(section, [])
            continue
        if section is None:
            m = _META_RE.match(s)
            if m and not s.startswith("|"):
                meta[m.group(1)] = m.group(2)
            continue
        if not s.startswith("|"):
            header = None if not s else header
            continue
        cells = _split_row(s)
        if header is None:
            header = [c.lower() for c in cells]
            if tuple(header) != SECTIONS[section]:
                problems.append(
                    f"line {n}: section '{section}' columns {header} != {list(SECTIONS[section])}"
                )
                section = None  # do not read rows under a wrong header
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue  # the |---|---| separator
        if len(cells) != len(header):
            problems.append(f"line {n}: {len(cells)} cells, expected {len(header)}")
            continue
        row = dict(zip(header, cells))
        row["_line"] = str(n)
        tables[section].append(row)
    return meta, tables, problems


def _flag(raw: str, where: str, problems: list[str]) -> bool | None:
    v = _BOOL.get(raw.strip().lower())
    if v is None:
        problems.append(f"{where}: in_template {raw!r} is not yes/no")
    return v


def parse_templates(text: str) -> Templates:
    meta, tables, problems = _tables(text)
    for key in ("template_version", "effective_from"):
        if key not in meta:
            problems.append(f"missing '{key}: ...' line")
    effective = date.min
    if "effective_from" in meta:
        try:
            effective = date.fromisoformat(meta["effective_from"])
        except ValueError:
            problems.append(
                f"effective_from {meta['effective_from']!r} is not YYYY-MM-DD"
            )
    for sec in _REQUIRED_SECTIONS:
        if not tables.get(sec):
            problems.append(f"section '## {sec}' is missing or empty")

    defaults: dict[str, dict[str, tuple[bool, str]]] = {}
    for r in tables.get("sector defaults", []):
        where = f"line {r['_line']}"
        t, dp, reason = r["template"], r["data_point"], r["reason"]
        if not t or not dp:
            problems.append(f"{where}: template and data_point are required")
            continue
        flag = _flag(r["in_template"], where, problems)
        if flag is None:
            continue
        if not flag and not reason:
            problems.append(f"{where}: {t}/{dp} is excluded without a reason")
        if dp in defaults.setdefault(t, {}):
            problems.append(f"{where}: duplicate default {t}/{dp}")
        defaults[t][dp] = (flag, reason)

    ranges: list[tuple[str, int, int]] = []
    for r in tables.get("sector assignment", []):
        where = f"line {r['_line']}"
        try:
            lo, hi = int(r["sic_from"]), int(r["sic_to"])
        except ValueError:
            problems.append(f"{where}: sic_from/sic_to must be integers")
            continue
        if lo > hi:
            problems.append(f"{where}: sic_from {lo} > sic_to {hi}")
        if r["template"] not in defaults:
            problems.append(
                f"{where}: template {r['template']!r} has no sector defaults"
            )
        ranges.append((r["template"], lo, hi))
    ordered = sorted(ranges, key=lambda x: (x[1], x[2]))
    for (t1, lo1, hi1), (t2, lo2, hi2) in pairwise(ordered):
        if lo2 <= hi1:
            problems.append(
                f"SIC ranges overlap: {t1} {lo1}-{hi1} and {t2} {lo2}-{hi2}"
            )

    assignment: dict[str, tuple[str, str]] = {}
    for r in tables.get("company assignment", []):
        where = f"line {r['_line']}"
        try:
            cik = _cik(r["cik"])
        except ValueError as exc:
            problems.append(f"{where}: {exc}")
            continue
        if not r["reason"]:
            problems.append(f"{where}: company assignment for {cik} has no reason")
        if r["template"] not in defaults:
            problems.append(
                f"{where}: template {r['template']!r} has no sector defaults"
            )
        if cik in assignment:
            problems.append(f"{where}: duplicate company assignment for {cik}")
        assignment[cik] = (r["template"], r["reason"])

    overrides: dict[str, dict[str, tuple[bool, str]]] = {}
    for r in tables.get("company overrides", []):
        where = f"line {r['_line']}"
        try:
            cik = _cik(r["cik"])
        except ValueError as exc:
            problems.append(f"{where}: {exc}")
            continue
        flag = _flag(r["in_template"], where, problems)
        if flag is None:
            continue
        if not r["reason"]:
            problems.append(f"{where}: override {cik}/{r['data_point']} has no reason")
        if r["data_point"] in overrides.setdefault(cik, {}):
            problems.append(f"{where}: duplicate override {cik}/{r['data_point']}")
        overrides[cik][r["data_point"]] = (flag, r["reason"])

    if problems:
        raise TemplateError(problems)
    return Templates(
        template_version=meta["template_version"],
        effective_from=effective,
        sic_ranges=tuple(ordered),
        company_assignment=assignment,
        defaults=defaults,
        overrides=overrides,
    )


def load_cohort(path: Path) -> list[CohortCompany]:
    """The top-1000 cohort file (doc/data-moat/team/top1000/shards.csv); excluded rows are skipped."""
    out: list[CohortCompany] = []
    with path.open(newline="") as fh:
        for r in csv.DictReader(fh):
            if (r.get("excluded") or "").strip():
                continue
            sic = (r.get("sic") or "").strip()
            out.append(
                CohortCompany(
                    company_id=int(r["company_id"]),
                    cik=_cik(r["cik"]),
                    sic=int(sic) if sic.isdigit() else None,
                )
            )
    return out


def cohort_has_sic(path: Path) -> bool:
    with path.open(newline="") as fh:
        return "sic" in (csv.DictReader(fh).fieldnames or [])


def fill_sic_from_db(
    conn: psycopg.Connection, cohort: list[CohortCompany]
) -> list[CohortCompany]:
    """For a cohort file without a sic column (e.g. cohort_v1_1_proposal_2026-10-24.csv):
    read core.company.sic_code by id, one indexed read. A cik that disagrees with
    core.company is an error, never silently trusted."""
    with conn.cursor() as cur:
        cur.execute(
            "select id, cik, sic_code from core.company where id = any(%s)",
            ([c.company_id for c in cohort],),
        )
        found = {int(i): (cik, sic) for i, cik, sic in cur.fetchall()}
    problems = []
    out = []
    for c in cohort:
        if c.company_id not in found:
            problems.append(f"company id {c.company_id} not in core.company")
            continue
        cik, sic = found[c.company_id]
        if _cik(cik) != c.cik:
            problems.append(
                f"company id {c.company_id}: cohort cik {c.cik} != core.company {cik}"
            )
        sic_s = (sic or "").strip()
        out.append(
            CohortCompany(c.company_id, c.cik, int(sic_s) if sic_s.isdigit() else None)
        )
    if problems:
        raise TemplateError(problems)
    return out


def resolve_template(t: Templates, c: CohortCompany) -> str | None:
    if c.cik in t.company_assignment:
        return t.company_assignment[c.cik][0]
    if c.sic is not None:
        for name, lo, hi in t.sic_ranges:
            if lo <= c.sic <= hi:
                return name
    return None


def build_plan(t: Templates, cohort: list[CohortCompany]) -> list[TemplateRow]:
    """Every cohort company's full template: sector defaults, then company overrides."""
    problems: list[str] = []
    dup = [cik for cik, n in Counter(c.cik for c in cohort).items() if n > 1]
    if dup:
        problems.append(f"cohort lists CIKs more than once: {sorted(dup)[:10]}")
    cohort_ciks = {c.cik for c in cohort}
    for cik in sorted(set(t.overrides) | set(t.company_assignment)):
        if cik not in cohort_ciks:
            problems.append(f"cik {cik} is overridden/assigned but not in the cohort")
    rows: list[TemplateRow] = []
    for c in sorted(cohort, key=lambda x: x.company_id):
        name = resolve_template(t, c)
        if name is None:
            problems.append(f"cik {c.cik} (sic {c.sic}) matches no template")
            continue
        cells: dict[str, tuple[bool, str | None, str]] = {
            dp: (flag, reason or None, "sector_default")
            for dp, (flag, reason) in t.defaults[name].items()
        }
        for dp, (o_flag, o_reason) in t.overrides.get(c.cik, {}).items():
            cells[dp] = (o_flag, o_reason, "company_override")
        for dp in sorted(cells):
            in_t, why, source = cells[dp]
            rows.append(
                TemplateRow(
                    company_id=c.company_id,
                    data_point=dp,
                    in_template=in_t,
                    reason=why,
                    effective_from=t.effective_from,
                    template=name,
                    source=source,
                    template_version=t.template_version,
                )
            )
    if problems:
        raise TemplateError(problems)
    return rows


def summarize(rows: list[TemplateRow]) -> dict[str, object]:
    companies = {r.company_id for r in rows}
    by_template = Counter(t for t, _cid in {(r.template, r.company_id) for r in rows})
    return {
        "companies": len(companies),
        "rows": len(rows),
        "template_cells": sum(1 for r in rows if r.in_template),
        "excluded_cells": sum(1 for r in rows if not r.in_template),
        "overrides": sum(1 for r in rows if r.source == "company_override"),
        "companies_per_template": dict(sorted(by_template.items())),
    }


def write_plan_csv(rows: list[TemplateRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "company_id",
                "data_point",
                "in_template",
                "reason",
                "effective_from",
                "template",
                "source",
                "template_version",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r.company_id,
                    r.data_point,
                    "yes" if r.in_template else "no",
                    r.reason or "",
                    r.effective_from.isoformat(),
                    r.template,
                    r.source,
                    r.template_version,
                ]
            )


def validate_against_db(conn: psycopg.Connection, rows: list[TemplateRow]) -> None:
    """Every data point must be a canonical concept or an active metric, and every
    company id must exist with the cohort's CIK. Read-only, two indexed queries."""
    names = sorted({r.data_point for r in rows})
    ids = sorted({r.company_id for r in rows})
    with conn.cursor() as cur:
        cur.execute("set statement_timeout = '2min'")
        cur.execute(
            """
            select n from unnest(%s::text[]) as n
            where not exists (select 1 from analytics.canonical_concept c where c.name = n)
              and not exists (select 1 from analytics.metric_definition d
                              where d.metric_name = n and d.status = 'active')
            """,
            (names,),
        )
        unknown = [r[0] for r in cur.fetchall()]
        cur.execute("select id from core.company where id = any(%s)", (ids,))
        missing = sorted(set(ids) - {r[0] for r in cur.fetchall()})
    problems = []
    if unknown:
        problems.append(
            f"data points unknown to canonical_concept/metric_definition: {unknown}"
        )
    if missing:
        problems.append(f"company ids not in core.company: {missing[:20]}")
    if problems:
        raise TemplateError(problems)


WRITE_CHUNK = 5000

_INSERT_SQL = """
    insert into analytics.company_data_point_template
        (company_id, data_point, in_template, reason, effective_from, template, source, template_version)
    values (%s, %s, %s, %s, %s, %s, %s, %s)
"""


def write_plan(conn: psycopg.Connection, rows: list[TemplateRow]) -> dict[str, int]:
    """Replace each planned company's rows at this effective_from, in ONE transaction,
    with batched statements (no per-row round trip). Rerunning is idempotent."""
    if not rows:
        return {"companies": 0, "deleted": 0, "inserted": 0}
    effective = {r.effective_from for r in rows}
    if len(effective) != 1:
        raise TemplateError([f"one effective_from per seed, got {sorted(effective)}"])
    ids = sorted({r.company_id for r in rows})
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local statement_timeout = '5min'")
            cur.execute(
                "delete from analytics.company_data_point_template"
                " where company_id = any(%s) and effective_from = %s",
                (ids, next(iter(effective))),
            )
            deleted = cur.rowcount
            params = [
                (
                    r.company_id,
                    r.data_point,
                    r.in_template,
                    r.reason,
                    r.effective_from,
                    r.template,
                    r.source,
                    r.template_version,
                )
                for r in rows
            ]
            for i in range(
                0, len(params), WRITE_CHUNK
            ):  # pipeline/CLAUDE.md: chunk bulk writes
                cur.executemany(_INSERT_SQL, params[i : i + WRITE_CHUNK])
    # On a non-autocommit connection conn.transaction() is a savepoint inside the
    # open transaction; commit so the seed is durable as one unit.
    conn.commit()
    return {"companies": len(ids), "deleted": deleted, "inserted": len(rows)}
