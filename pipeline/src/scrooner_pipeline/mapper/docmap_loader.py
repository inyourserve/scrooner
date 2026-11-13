"""Docmap loader: the FILING-CHECKED document-first reads (data-team/companies/reads/<TICKER>-docmap-<date>.csv, one row
per data point: data_point, status, tags, stmt, r_page, label, era_from_note, evidence_class, note) become
analytics.company_tag_map rows (decided_by 'docmap', rule company_tag_map.docmap@1, evidence_adsh = the 10-K read,
evidence_report = its R page). Learning reaches the screen with no hand step: load -> tagmap-plan -> cell proof -> guard.

Only verified rows load: evidence_class FILING-CHECKED and no machine-pick marker in the notes (UNVERIFIED_RE);
anything else is rejected as 'unverified'. A fact found only in a note is 'mapped' with stmt NOTE (lands on UN).
Status vocabulary (anything else is rejected and listed, never guessed):
  mapped             -> 'concept' row (the tag IS the data point)
  component_in_note  -> 'concept' row on stmt UN (printed in a note, not on a face)
  component sum      -> one 'component' row per part ('+' or ';' joined; a leading '-' subtracts); instants are never
                        summed except total_debt (company_tag_map_seed.instant_sum_refused)
  combined           -> tagless 'not_in_template' (one printed line spans this and other lines: doc 02 sector
                        templates item 3); the docmap does not name the other spanned concepts
  not_presented      -> tagless 'not_presented'
  OUT                -> tagless 'not_in_template'
Eras: open-ended, starting where the read's era evidence starts (same_tag@<end>, ERA-CHECK, the FY-4 10-K's same tag,
'tag covers last 5 FY'); with no era evidence, the start of the earliest year the read 10-K prints (fy1).

Conflicts with the existing library (rows not written by this loader), per (company, concept): the same decision and
tags -> the library row stands, nothing written; different -> the docmap wins only when it cites a filing page
(r_page): the library rows of that concept still open at the docmap era are cut to end the day before it (or deleted
when they start inside it). A library 'combined' line is never cut here. Every disagreement is listed for the Tag Expert.
Idempotent: each company's docmap rows are replaced in one transaction; library rows are compared, never re-created.
"""

from __future__ import annotations

import csv
import io
import re
from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.mapper.company_tag_map import EXTRA_STMT, STATEMENT_CODE
from scrooner_pipeline.mapper.company_tag_map_seed import (
    INSERT,
    check_overlaps,
    instant_sum_refused,
    normalize,
)

RULE_ID = "company_tag_map.docmap@1"
DECIDED_BY = "docmap"
STATUSES = {
    "mapped",
    "combined",
    "component sum",
    "component_in_note",
    "not_presented",
    "OUT",
}
STATUS_ALIASES = {"component_sum": "component sum"}
TAGLESS_STATUS = {
    "combined": "not_in_template",
    "not_presented": "not_presented",
    "OUT": "not_in_template",
}
FACE_CODES = {"IS", "BS", "CF", "CI", "EQ"}
# docmap data points are catalog names; the screen serves the resolved concept where one exists (the library's names)
SERVED_ALIAS = {"revenue": "revenue_sanity_resolved"}
# a machine pick nobody checked on the filing (Dhairya 2026-11-12): 'auto:' / 'AUTO;' / 'auto)', 'not hand-verified',
# 'no face row matched'. 'auto-reader: manual override' is a hand decision and loads.
UNVERIFIED_RE = re.compile(
    r"\bauto\s*[:;)]|not hand-verified|no face row mat", re.IGNORECASE
)
ACCN_RE = re.compile(r"\d{10}-\d{2}-\d{6}")
DATE_RE = r"\d{4}-\d{2}-\d{2}"


@dataclass(frozen=True)
class DocmapRow:
    ticker: str
    data_point: str
    status: str
    parts: tuple[tuple[int, str, str], ...]  # (sign, taxonomy, local tag)
    stmt_raw: str
    r_page: str
    label: str
    era_from: date
    accession: str
    reason: str
    source: str
    fy0_end: date | None = (
        None  # the read 10-K's fiscal year end (FY0); FY-1 ends a year earlier
    )

    @property
    def cites_page(self) -> bool:
        return bool(self.r_page.strip())

    @property
    def report(self) -> int | None:
        m = re.match(r"R(\d+)", self.r_page.strip())
        return int(m.group(1)) if m else None


def served_concept(data_point: str, names: set[str]) -> str:
    if data_point in SERVED_ALIAS:
        return SERVED_ALIAS[data_point]
    return f"{data_point}_resolved" if f"{data_point}_resolved" in names else data_point


def _years_back(d: date, n: int) -> date:
    try:
        return d.replace(year=d.year - n)
    except ValueError:  # 29 February
        return d.replace(year=d.year - n, day=28)


def _fy_start(end: date, years: int = 1) -> date:
    """First day of the span of `years` fiscal years ending on `end`."""
    return _years_back(end, years) + timedelta(days=1)


MEMBER_RE = re.compile(r"\[[^\]]*=[^\]]*\]")


def parse_parts(tags: str) -> tuple[tuple[int, str, str], ...]:
    out = []
    for t in re.split(r"[+;]", tags):
        t = t.strip()
        if not t:
            continue
        if MEMBER_RE.search(t):
            # tag[Axis=Member]: a dimensional line; company_tag_map has no axis/member key yet (Dhairya 2026-11-13).
            # Stored as a literal tag it would never match a value.
            raise ValueError("member_not_supported")
        sign = -1 if t.startswith("-") else 1
        prefix, _, local = t.lstrip("-").partition(":")
        if not local:
            raise ValueError(f"tag {t!r} has no taxonomy prefix")
        out.append((sign, prefix, local))
    return tuple(out)


def era_from_of(era_note: str, parts, fy0_end: date) -> date:
    """Where the read's evidence says the tag(s) started; fy1 (the earliest year the read 10-K prints) without it."""
    m = re.search(rf"same_tag@({DATE_RE})", era_note)
    if m:
        return _fy_start(date.fromisoformat(m.group(1)))
    m = re.search(rf"ERA-CHECK: chosen tag \['({DATE_RE})'", era_note)
    if m:
        return _fy_start(date.fromisoformat(m.group(1)))
    if "tag covers last 5 FY" in era_note:
        return _fy_start(fy0_end, 5)
    old = set(re.findall(r"SAME_TAG_IN_OLD\([^)]*\):(\S+:\S+)", era_note))
    if parts and old and all(f"{tax}:{tag}" in old for _, tax, tag in parts):
        return _fy_start(fy0_end, 5)  # the FY-4 10-K prints the same tag(s)
    return _fy_start(fy0_end, 2)


def _fy0_end(note: str, md_text: str) -> date | None:
    for pat in (
        rf"period (?:{DATE_RE})?\.\.({DATE_RE})",
        rf"fy0=({DATE_RE})",
        rf"period ({DATE_RE})",
    ):
        m = re.search(pat, note)
        if m:
            return date.fromisoformat(m.group(1))
    m = re.search(rf"(?:period(?: end)?|FY ended) ({DATE_RE})", md_text)
    return date.fromisoformat(m.group(1)) if m else None


def _accession(note: str, md_text: str) -> str | None:
    m = re.search(r"accn (\S+)", note) or re.search(r"@(\d{10}-\d{2}-\d{6})", note)
    if m:
        return m.group(1)
    m = ACCN_RE.search(md_text)
    return m.group(0) if m else None


def _reason(note: str) -> str:
    return re.split(r"\s\|\s(?:accn|api ev|fy0=|API MISSING)", note)[0].strip()


def parse_docmap(
    csv_text: str, md_text: str, source: str
) -> tuple[list[DocmapRow], list[dict]]:
    """One docmap file -> rows, rejects ({source, ticker, data_point, status, why}). Pure."""
    rows: list[DocmapRow] = []
    rejects: list[dict] = []
    seen: set[str] = set()
    for r in csv.DictReader(io.StringIO(csv_text)):
        r = {k: (v or "").strip() for k, v in r.items()}
        status = STATUS_ALIASES.get(r["status"], r["status"])

        def reject(why: str, r: dict = r) -> None:
            rejects.append(
                {
                    "source": source,
                    "ticker": r["ticker"],
                    "data_point": r["data_point"],
                    "status": r["status"],
                    "why": why,
                }
            )

        if status not in STATUSES:
            reject(f"unknown status {r['status']!r}")
            continue
        if not r.get("evidence_class", "").startswith(
            "FILING-CHECKED"
        ) or UNVERIFIED_RE.search(
            " ".join(r.get(k, "") for k in ("note", "era_from_note", "evidence_class"))
        ):
            reject("unverified")
            continue
        if r["data_point"] in seen:
            reject("duplicate data_point in file")
            continue
        seen.add(r["data_point"])
        try:
            parts = parse_parts(r["tags"])
        except ValueError as exc:
            reject(str(exc))
            continue
        if status in TAGLESS_STATUS:
            parts = parts if status == "combined" else ()
        elif not parts:
            reject(f"{status} row without a tag")
            continue
        elif len({(tax, tag) for _, tax, tag in parts}) < len(parts):
            reject("a part tag repeats (dimensional members are not separable by tag)")
            continue
        elif status != "component sum" and len(parts) > 1:
            reject(f"{status} row with {len(parts)} tags")
            continue
        fy0 = _fy0_end(r["note"], md_text)
        accn = _accession(r["note"], md_text)
        if fy0 is None or accn is None:
            reject("no 10-K period or accession in the row or the read's header")
            continue
        era = (
            era_from_of(r["era_from_note"], parts, fy0)
            if status not in TAGLESS_STATUS
            else _fy_start(fy0, 2)
        )
        rows.append(
            DocmapRow(
                r["ticker"],
                r["data_point"],
                status,
                parts,
                r["stmt"],
                r["r_page"],
                r["label"],
                era,
                accn,
                _reason(r["note"]),
                source,
                fy0,
            )
        )
    return rows, rejects


def stmt_code(
    raw: str, concept_name: str, concept_statement: str, *, value_row: bool
) -> str:
    """FSN statement code for a docmap row. Value rows land on a face the concept may be fed from, else UN (a note,
    the cover, a parenthetical); tagless rows sit on the concept's own face."""
    home = STATEMENT_CODE.get(concept_statement, "UN")
    allowed = {home} | EXTRA_STMT.get(concept_name, set())
    t = raw.upper()
    code: str | None = t if t in FACE_CODES else None
    if code is None and t.startswith("CONSOLIDATED"):
        for pat, c in (
            (r"BALANCE|OF FIN", "BS"),
            (r"OF CAS|CASH", "CF"),
            (r"OF COM", "CI"),
            (r"OF OPE|OF INC|OF EAR", "IS"),
            (r"OF EQU|OF CHA|OF STO|OF SHA", "EQ"),
        ):
            if re.search(pat, t):
                code = c
                break
    if code is not None and code in allowed:
        return code
    return home if not value_row else "UN"


def table_rows(
    d: DocmapRow, company_id: int, cik: str, concept_statement: dict[str, str]
) -> list[dict]:
    """Seeder-shaped rows (company_tag_map_seed.normalize input) for one docmap row."""
    base: dict[str, Any] = {
        "company_id": company_id,
        "cik": cik,
        "era_from": d.era_from,
        "era_to": None,
        "evidence_adsh": d.accession,
        "evidence_report": d.report,
        "evidence_plabel": d.label or None,
        "decided_by": DECIDED_BY,
        "rule_id": RULE_ID,
    }
    st = concept_statement[d.data_point]
    if d.status in TAGLESS_STATUS:
        reason = d.reason or "not printed in the latest 10-K"
        if d.status == "combined":
            tags = "+".join(f"{tax}:{tag}" for _, tax, tag in d.parts)
            reason = f"combined line '{d.label}' ({tags}): {reason}"
        return [
            {
                **base,
                "decision": TAGLESS_STATUS[d.status],
                "canonical_concept": d.data_point,
                "stmt": stmt_code(d.stmt_raw, d.data_point, st, value_row=False),
                "reason": reason,
                "reason_class": f"docmap_{d.status.replace(' ', '_').lower()}",
            }
        ]
    stmt = (
        "UN"
        if d.status == "component_in_note"
        else stmt_code(d.stmt_raw, d.data_point, st, value_row=True)
    )
    if d.status == "component sum":
        return [
            {
                **base,
                "decision": "component",
                "parent_concept": d.data_point,
                "taxonomy": tax,
                "tag": tag,
                "sign": sign,
                "stmt": stmt,
            }
            for sign, tax, tag in d.parts
        ]
    ((sign, tax, tag),) = d.parts
    return [
        {
            **base,
            "decision": "concept",
            "canonical_concept": d.data_point,
            "taxonomy": tax,
            "tag": tag,
            "sign": sign,
            "stmt": stmt,
        }
    ]


def _signature_doc(d: DocmapRow) -> frozenset:
    if d.status in TAGLESS_STATUS:
        return frozenset(
            {
                (
                    TAGLESS_STATUS[d.status] if d.status != "combined" else "combined",
                    None,
                    None,
                    1,
                )
            }
        )
    kind = "component" if d.status == "component sum" else "concept"
    return frozenset((kind, tax, tag, sign) for sign, tax, tag in d.parts)


def _signature_lib(rows: list[dict]) -> frozenset:
    return frozenset(
        (
            r["decision"],
            r["taxonomy"],
            r["tag"],
            r["sign"] if r["decision"] in ("concept", "component") else 1,
        )
        for r in rows
    )


@dataclass
class CompanyPlan:
    insert: list[DocmapRow] = field(default_factory=list)
    cut: list[tuple[int, date]] = field(
        default_factory=list
    )  # (library row id, new era_to)
    delete: list[int] = field(default_factory=list)  # library row ids
    conflicts: list[dict] = field(default_factory=list)
    agree: int = 0


REASON_DECISIONS = {"not_presented", "not_in_template"}


def _conflict(
    d: DocmapRow, winner: str, why: str, library: list[dict], names_by_id: dict
) -> dict:
    return {
        "ticker": d.ticker,
        "data_point": d.data_point,
        "winner": winner,
        "why": why,
        "docmap_status": d.status,
        "docmap_tags": "+".join(
            f"{'-' if s < 0 else ''}{t}:{g}" for s, t, g in d.parts
        ),
        "docmap_era_from": d.era_from.isoformat(),
        "docmap_accession": d.accession,
        "library": "; ".join(
            sorted(
                f"{r['decision']} {r['taxonomy'] or ''}:{r['tag'] or ''} {r['era_from']}..{r['era_to'] or ''} "
                f"({names_by_id.get(r['canonical_concept_id'] or r['parent_concept_id'], '')})"
                for r in library
            )
        ),
        "source": d.source,
    }


def plan_company(
    existing: list[dict], docrows: list[DocmapRow], concept_ids: dict[str, int]
) -> CompanyPlan:
    """existing: the company's company_tag_map rows NOT written by this loader (id, decision, taxonomy, tag, sign,
    canonical_concept_id, parent_concept_id, components, era_from, era_to). Pure."""
    plan = CompanyPlan()
    names_by_id = {i: n for n, i in concept_ids.items()}
    for d in docrows:
        cid = concept_ids.get(d.data_point)
        current = [
            r
            for r in existing
            if (r["era_to"] is None or r["era_to"] >= d.era_from)
            and (
                cid in (r["canonical_concept_id"], r["parent_concept_id"])
                or (
                    r["decision"] == "combined"
                    and d.data_point in (r["components"] or [])
                )
            )
            and r["decision"] != "excluded"
        ]
        # merge by kind (Dhairya 2026-11-13): a docmap VALUE row competes only with library value rows, a docmap
        # REASON row only with library reasons. A per-period library reason (open_period, fy_status ...) is never
        # removed by a value row: a value row is no reason for a period that has no fact.
        reasons = [r for r in current if r["decision"] in REASON_DECISIONS]
        values = [r for r in current if r["decision"] not in REASON_DECISIONS]
        if d.status in TAGLESS_STATUS and d.status != "combined":
            if values:
                plan.conflicts.append(
                    _conflict(
                        d,
                        "coexist",
                        "docmap reason beside a library value: the value is served where printed",
                        values,
                        names_by_id,
                    )
                )
            current = reasons
        elif (
            d.status != "combined"
        ):  # a combined line is a reason that also displaces values: it meets both
            current = values
        if not current:
            plan.insert.append(d)
            continue
        if _signature_lib(current) == _signature_doc(d):
            plan.agree += 1
            continue
        has_combined = any(r["decision"] == "combined" for r in current)
        winner = "docmap" if d.cites_page and not has_combined else "library"
        why = (
            ("docmap cites " + d.r_page)
            if winner == "docmap"
            else (
                "library combined line: Tag Expert decides"
                if has_combined
                else "docmap cites no filing page"
            )
        )
        plan.conflicts.append(_conflict(d, winner, why, current, names_by_id))
        if winner == "library":
            continue
        for r in current:
            if r["era_from"] < d.era_from:
                plan.cut.append((r["id"], d.era_from - timedelta(days=1)))
            else:
                plan.delete.append(r["id"])
        plan.insert.append(d)
    return plan


VALUE_STATUSES = {"mapped", "component sum", "component_in_note"}


def expected_cells(
    paths: list[Path], names: set[str]
) -> dict[str, list[tuple[str, date, str]]]:
    """Ticker -> the docmap template's FY0/FY-1 cells (served data point, period end, status): 'served' for a
    value-bearing status, else the status (a reasoned blank is expected). The tagmap-plan coverage check reads it."""
    out: dict[str, list[tuple[str, date, str]]] = {}
    for p in latest_docmaps(paths):
        md = p.with_suffix(".md")
        rows, _ = parse_docmap(
            p.read_text(), md.read_text() if md.exists() else "", p.name
        )
        ticker = p.name.split("-docmap-")[0].upper()
        cells = out.setdefault(ticker, [])
        for d in rows:
            if d.fy0_end is None:
                continue
            status = "served" if d.status in VALUE_STATUSES else d.status
            for end in (d.fy0_end, _years_back(d.fy0_end, 1)):
                cells.append((served_concept(d.data_point, names), end, status))
    return out


def latest_docmaps(paths: list[Path]) -> list[Path]:
    """The newest docmap per ticker (file names <TICKER>-docmap-<YYYY-MM-DD>.csv)."""
    best: dict[str, Path] = {}
    for p in sorted(paths, key=lambda p: p.name):
        m = re.match(r"(.+)-docmap-(\d{4}-\d{2}-\d{2})\.csv$", p.name)
        if m:
            best[m.group(1)] = p
    return [best[t] for t in sorted(best)]


EXISTING_SQL = """
select id, company_id, decision, taxonomy, tag, sign, canonical_concept_id, parent_concept_id, components, era_from,
       era_to, stmt, rule_id
from analytics.company_tag_map where company_id = any(%s)
"""


def companies_by_ticker(conn: psycopg.Connection) -> dict[str, set[tuple[int, str]]]:
    """Upper-case ticker -> {(company id, cik)} from the primary ticker and every listing."""
    by_ticker: dict[str, set[tuple[int, str]]] = defaultdict(set)
    with conn.cursor() as cur:
        cur.execute(
            """select upper(t), c.id, c.cik from core.company c
               join lateral (select c.primary_ticker union select l.ticker from core.listing l where l.company_id = c.id) x(t)
                 on x.t is not null"""
        )
        for t, cid, cik in cur.fetchall():
            by_ticker[t].add((cid, cik))
    return by_ticker


def load(conn: psycopg.Connection, paths: list[Path], *, apply: bool = False) -> dict:
    """Plan (and with apply, write) every docmap in `paths`. One transaction per company; a company whose rows fail
    validation or era overlap is skipped whole and listed."""
    files = latest_docmaps(paths)
    with conn.cursor() as cur:
        cur.execute("select name, id, statement from analytics.canonical_concept")
        cc = cur.fetchall()
    by_ticker = companies_by_ticker(conn)
    concept_ids = {n: i for n, i, _ in cc}
    concept_statement = {n: s for n, _, s in cc}
    stats: dict[str, Any] = {
        "files": len(files),
        "rows": 0,
        "rejects": [],
        "conflicts": [],
        "blocked": {},
        "companies": {},
        "applied": False,
    }
    docs: dict[int, tuple[str, list[DocmapRow]]] = {}
    for p in files:
        md = p.with_suffix(".md")
        rows, rejects = parse_docmap(
            p.read_text(), md.read_text() if md.exists() else "", p.name
        )
        stats["rejects"] += rejects
        ticker = p.name.split("-docmap-")[0].upper()
        hits = by_ticker.get(ticker, set())
        if len(hits) != 1:
            stats["blocked"][p.name] = (
                f"ticker {ticker} resolves to {len(hits)} companies"
            )
            continue
        ((cid, cik),) = hits
        ok = []
        for d in (
            replace(d, data_point=served_concept(d.data_point, set(concept_ids)))
            for d in rows
        ):
            if d.data_point not in concept_ids:
                stats["rejects"].append(
                    {
                        "source": d.source,
                        "ticker": d.ticker,
                        "data_point": d.data_point,
                        "status": d.status,
                        "why": "no canonical concept of that name",
                    }
                )
            elif d.status == "component sum" and instant_sum_refused(
                d.data_point, concept_statement[d.data_point]
            ):
                stats["rejects"].append(
                    {
                        "source": d.source,
                        "ticker": d.ticker,
                        "data_point": d.data_point,
                        "status": d.status,
                        "why": "instant component sum refused (only total_debt)",
                    }
                )
            else:
                # validate before planning: a row the table would refuse is rejected alone, and no library row is
                # cut or deleted for it (a bad row never blocks its company)
                try:
                    for t in table_rows(d, cid, cik, concept_statement):
                        normalize(t, {}, concept_ids, RULE_ID, [])
                except (ValueError, TypeError) as exc:
                    stats["rejects"].append(
                        {
                            "source": d.source,
                            "ticker": d.ticker,
                            "data_point": d.data_point,
                            "status": d.status,
                            "why": f"invalid row: {exc}",
                        }
                    )
                    continue
                ok.append(d)
        stats["rows"] += len(ok)
        docs[cid] = (cik, ok)
    with conn.cursor() as cur:
        cur.execute(EXISTING_SQL, (sorted(docs),))
        cols = [c.name for c in cur.description]
        existing: dict[int, list[dict]] = defaultdict(list)
        for row in cur.fetchall():
            rec = dict(zip(cols, row))
            existing[rec["company_id"]].append(rec)
    names = {i: n for n, i in concept_ids.items()}
    writes = []
    for cid, (cik, rows) in sorted(docs.items()):
        mine = [r for r in existing[cid] if r["rule_id"] == RULE_ID]
        library = [r for r in existing[cid] if r["rule_id"] != RULE_ID]
        plan = plan_company(library, rows, concept_ids)
        stats["conflicts"] += plan.conflicts
        warnings: list[str] = []
        try:
            new = [
                normalize(t, {}, concept_ids, RULE_ID, warnings)
                for d in plan.insert
                for t in table_rows(d, cid, cik, concept_statement)
            ]
        except (ValueError, TypeError) as exc:
            stats["blocked"][cik] = str(exc)
            continue
        cut = dict(plan.cut)
        kept = [
            {**r, "era_to": cut.get(r["id"], r["era_to"])}
            for r in library
            if r["id"] not in plan.delete
        ]
        errors = check_overlaps(kept + new)
        if errors:
            stats["blocked"][cik] = "; ".join(errors[:3])
            continue
        before = {_content(r, names) for r in mine}
        after = {_content(r, names) for r in new}
        stats["companies"][cik] = {
            "company_id": cid,
            "docmap_rows": len(new),
            "added": len(after - before),
            "removed": len(before - after),
            "library_cut": len(plan.cut),
            "library_deleted": len(plan.delete),
            "agree": plan.agree,
            "conflicts": len(plan.conflicts),
        }
        writes.append((cid, new, plan))
    if not apply:
        return stats
    for cid, new, plan in writes:
        with conn.transaction():
            conn.execute(
                "delete from analytics.company_tag_map where company_id = %s and rule_id = %s",
                (cid, RULE_ID),
            )
            if plan.delete:
                conn.execute(
                    "delete from analytics.company_tag_map where id = any(%s)",
                    (plan.delete,),
                )
            with conn.cursor() as cur:
                if plan.cut:
                    cur.executemany(
                        "update analytics.company_tag_map set era_to = %s where id = %s",
                        [(to, rid) for rid, to in plan.cut],
                    )
                cur.executemany(INSERT, new)
    stats["applied"] = True
    return stats


def _content(r: dict, names: dict[int, str]) -> tuple:
    return (
        r["decision"],
        r["taxonomy"],
        r["tag"],
        r["stmt"],
        r["sign"],
        names.get(r["canonical_concept_id"]),
        names.get(r["parent_concept_id"]),
        r["era_from"],
        r["era_to"],
    )


def write_listing(path: Path, rows: list[dict]) -> None:
    """Conflicts or rejects as CSV for the Tag Expert."""
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({k for r in rows for k in r}) or ["none"]
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
