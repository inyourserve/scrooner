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

from scrooner_pipeline.common import instance_facts
from scrooner_pipeline.mapper import era_extend
from scrooner_pipeline.mapper.company_tag_map import EXTRA_STMT, STATEMENT_CODE
from scrooner_pipeline.mapper.company_tag_map_plan import (
    era_shortfall,
    reporting_period_ends,
    unread_tail_concepts,
)
from scrooner_pipeline.proof.fsn import fsn_ddate
from scrooner_pipeline.mapper.company_tag_map_seed import (
    INSERT,
    check_overlaps,
    instant_sum_refused,
    normalize,
)

RULE_ID = "company_tag_map.docmap@1"
DECIDED_BY = "docmap"
FIX_RULE_ID = "company_tag_map.docmap_fix@1"
FIX_DECIDED_BY = "reader_fix"
# rows this loader replaces per company
OWN_RULES = (RULE_ID, era_extend.EXT_RULE_ID, FIX_RULE_ID)
# structural resolver rows (mapper/structural_loader.py) override this loader's docmap/extension/predictor rows: they
# are never replaced here and never compete in the library merge; this loader's own rows are clipped around them
STRUCTURAL_RULE_ID = "company_tag_map.structural@1"
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
COMBINED_CLASS = "line_presented_combined"
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
    # --extend-eras: era_from is the extended start; base_era the read's own (docmap@1 covers base_era onward, the
    # era_extend@1 row base_era-1 back to era_from); ext_note is the audit text on the extension row
    base_era: date | None = None
    ext_note: str = ""
    # closed end of the row's era (None = open-ended); set when an agreeing library row already covers the later years
    era_to: date | None = None
    # reader fix (data-team/companies/reads/fixes): one cell, one fiscal year; serve_note carries the printed value for
    # the Verifier (never served directly)
    is_fix: bool = False
    fix_note: str = ""
    # the era starts at the comparative year of the earliest 10-K that prints the tag (reader convention), and the
    # read names the tag(s) the PRIOR era's 10-K printed (MSFT sbc: the FY2017 10-K prints ShareBasedCompensation
    # for FY2016, the FY2016 10-K and that year's 10-Qs print AllocatedShareBasedCompensationExpense)
    comparative_start: bool = False
    prior_tags: tuple[str, ...] = ()
    # ERA-EXT(absent) per-year evidence: (era_from, era_to, adsh, ((stmt, report), ...)) newest first; each slice cites
    # the filing of its own year (or the nearest later one presenting it), never the docmap read's latest 10-K
    ext_slices: tuple[tuple[date, date, str, tuple[tuple[str, int], ...]], ...] = ()

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


def parse_parts(
    tags: str, instance_of: tuple[str, date] | None = None
) -> tuple[tuple[int, str, str], ...]:
    """Parts as (sign, taxonomy, local tag). A `tag[Axis=Member]` part is accepted ONLY with instance_of = (accession,
    period end) and only when it resolves to a row of the committed instance-facts file for that accession and column
    (common/instance_facts.py); it is stored as the literal `Tag[Axis=Member]` (the instance-sourced part). Otherwise
    member_not_supported: company_tag_map has no axis/member key (Dhairya 2026-11-13)."""
    out = []
    for t in re.split(r"[+;]", tags):
        t = t.strip()
        if not t:
            continue
        if MEMBER_RE.search(t):
            if instance_of is None:
                raise ValueError("member_not_supported")
            try:
                sign, prefix, base, segs = instance_facts.split_instance_part(t)
            except ValueError:
                raise ValueError("member_not_supported") from None
            accn, end = instance_of
            if (
                not prefix
                or instance_facts.lookup(accn, base, segs, fsn_ddate(end)) is None
            ):
                raise ValueError("member_not_supported")
            out.append((sign, prefix, instance_facts.part_tag(base, segs)))
            continue
        if "[" in t or "]" in t:
            raise ValueError(
                f"member_syntax: {t!r}"
            )  # a stray bracket is never part of a tag
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


COMPARATIVE_RE = re.compile(r"10-K's comparative year")
PRIOR_ERA_RE = re.compile(
    r"prior era read in 10-K \S+ \(FY\d{4}\): (?:mapped|combined|component sum) (\S+)"
)


def comparative_era_of(note: str) -> tuple[bool, tuple[str, ...]]:
    """(the era starts at a comparative year, the prior era's tag names) from the read's note. Both or nothing: a
    comparative start without a named prior tag is no evidence to keep the prior era a year longer."""
    if not COMPARATIVE_RE.search(note):
        return False, ()
    m = PRIOR_ERA_RE.search(note)
    if not m:
        return False, ()
    tags = tuple(
        t.split(":", 1)[-1] for t in re.split(r"[+;]", m.group(1)) if t.strip()
    )
    return bool(tags), tags


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


PPE_ROU_TAG_PREFIX = "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAsset"
PPE_ROU_NOTE = (
    "ppe_net ruling (Dhairya 2026-11-14): the face PP&E line that includes finance-lease right-of-use assets "
    "IS ppe_net, mapped, never combined"
)


def ppe_rou_is_ppe_net(
    status: str, data_point: str, parts: tuple[tuple[int, str, str], ...]
) -> str:
    """Rule 4: a 'combined' read of ppe_net on the single face tag PropertyPlantAndEquipmentAndFinanceLeaseRightOfUse
    Asset... (PP&E including finance-lease ROU) is the company's ppe_net line: 'mapped'. Any other status or data
    point, or a multi-tag line, keeps its status."""
    if (
        status == "combined"
        and data_point == "ppe_net"
        and len(parts) == 1
        and parts[0][2].startswith(PPE_ROU_TAG_PREFIX)
    ):
        return "mapped"
    return status


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
        status = ppe_rou_is_ppe_net(status, r["data_point"], parts)
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
        comparative_start, prior_tags = comparative_era_of(r["note"])
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
                comparative_start=comparative_start,
                prior_tags=prior_tags,
            )
        )
    return rows, rejects


FIX_FILE_RE = re.compile(r"(.+?)-fixes-(?:v\d+-)?(\d{4}-\d{2}-\d{2})\.csv$")
DEFAULT_FIXES_DIR = Path("data-team/companies/reads/fixes")


def fix_files(directory: Path | None) -> list[Path]:
    """Reader fix files (<TICKER>-fixes-<date>.csv) of a directory, oldest date first (a newer file wins a cell)."""
    if directory is None or not directory.is_dir():
        return []
    found = []
    for p in directory.glob("*.csv"):
        m = FIX_FILE_RE.match(p.name)
        if m:
            found.append((m.group(2), p.name, p))
    return [p for _, _, p in sorted(found)]


def parse_fixes(csv_text: str, source: str) -> tuple[list[DocmapRow], list[dict]]:
    """One reader fix file -> rows (one per cell: data point x fiscal-year period), rejects. Pure. Columns: data_point,
    fiscal_year, period_end, decision, tags (or tag), stmt, accession, r_page, printed_value, note. The decision
    vocabulary is the docmap's statuses. The era is that fiscal year only: from the day after the year before ended
    (see assign_fix_eras for 52/53-week neighbors) to period_end."""
    m = FIX_FILE_RE.match(source)
    ticker = (m.group(1) if m else source).upper()
    rows: list[DocmapRow] = []
    rejects: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for raw in csv.DictReader(io.StringIO(csv_text)):
        r = {(k or "").strip(): (v or "").strip() for k, v in raw.items()}
        status = STATUS_ALIASES.get(r.get("decision", ""), r.get("decision", ""))

        def reject(why: str, r: dict = r) -> None:
            rejects.append(
                {
                    "source": source,
                    "ticker": ticker,
                    "data_point": r.get("data_point", ""),
                    "status": r.get("decision", ""),
                    "why": f"fix: {why} (period_end {r.get('period_end', '')})",
                }
            )

        if status not in STATUSES:
            reject(f"unknown decision {r.get('decision', '')!r}")
            continue
        try:
            end = date.fromisoformat(r.get("period_end", ""))
        except ValueError:
            reject("period_end is not a date")
            continue
        accn = r.get("accession", "")
        if not ACCN_RE.fullmatch(accn):
            reject("accession is not an SEC accession number")
            continue
        key = (r.get("data_point", ""), end.isoformat())
        if key in seen:
            reject("duplicate cell in file")
            continue
        seen.add(key)
        try:
            parts = parse_parts(r.get("tags", r.get("tag", "")), (accn, end))
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
        was = status
        status = ppe_rou_is_ppe_net(status, r.get("data_point", ""), parts)
        note = r.get("note", "")
        if status != was:
            note = f"{note} [{PPE_ROU_NOTE}]".strip()
        printed = r.get("printed_value", "")
        rows.append(
            DocmapRow(
                ticker,
                r["data_point"],
                status,
                parts,
                r.get("stmt", ""),
                r.get("r_page", ""),
                "",
                _fy_start(end),
                accn,
                note,
                source,
                end,
                era_to=end,
                is_fix=True,
                fix_note=(
                    f"reader fix (company_tag_map.docmap_fix@1), FY ending {end}: printed value {printed or 'n/a'} in "
                    f"{accn} {r.get('r_page', '')}; for the Verifier, never served directly. {note}"
                ).strip(),
            )
        )
    return rows, rejects


GAP_CLOSE_DAYS = 10


def assign_fix_eras(rows: list[DocmapRow]) -> list[DocmapRow]:
    """A fix's era must not overlap its neighbor's of the same data point (52/53-week years end 364 days apart, so
    the nominal start of one year is the previous period end)."""
    out: list[DocmapRow] = []
    last: dict[str, date] = {}
    for d in sorted(rows, key=lambda d: (d.data_point, d.era_to or date.max)):
        prev = last.get(d.data_point)
        # overlap, or a small gap (53-week year starting days after the previous 52-week end, JNJ FY2019/FY2020): no
        # gap, or the rounded month-end of the gap days would let a guard row hold the earlier year
        if prev is not None and (
            d.era_from <= prev or (d.era_from - prev).days <= GAP_CLOSE_DAYS
        ):
            d = replace(d, era_from=prev + timedelta(days=1))
        last[d.data_point] = d.era_to or date.max
        out.append(d)
    return out


def _key(r: dict) -> int | None:
    return r["canonical_concept_id"] or r["parent_concept_id"]


def clip_rows(
    rows: list[dict], spans: list[tuple[Any, date, date]]
) -> tuple[list[dict], list[tuple[int, date, date | None]], list[int], list[dict]]:
    """Cut the fix eras out of every row of the same concept (value or reason; 'combined' and 'excluded' rows carry no
    concept key and stay). A row that spans a fix era is split into a before and an after piece; the other years are
    never removed. Rows with an id are DB rows: the first remaining piece is an update of that row, further pieces
    are inserts. Returns (rows in memory, updates (id, era_from, era_to), deleted ids, new piece rows). Pure."""
    kept: list[dict] = []
    updates: list[tuple[int, date, date | None]] = []
    deletes: list[int] = []
    extras: list[dict] = []
    for r in rows:
        k = _key(r)
        mine = sorted((a, b) for c, a, b in spans if k is not None and c == k)
        pieces: list[tuple[date, date | None]] = [(r["era_from"], r["era_to"])]
        for a, b in mine:
            nxt: list[tuple[date, date | None]] = []
            for lo, hi in pieces:
                if (hi is not None and hi < a) or lo > b:
                    nxt.append((lo, hi))
                    continue
                if lo < a:
                    nxt.append((lo, a - timedelta(days=1)))
                if hi is None or hi > b:
                    nxt.append((b + timedelta(days=1), hi))
            pieces = nxt
        if pieces == [(r["era_from"], r["era_to"])]:
            kept.append(r)
            continue
        if r.get("id") is not None:
            if not pieces:
                deletes.append(r["id"])
                continue
            lo, hi = pieces[0]
            updates.append((r["id"], lo, hi))
            kept.append({**r, "era_from": lo, "era_to": hi})
            for lo, hi in pieces[1:]:
                extras.append({**r, "id": None, "era_from": lo, "era_to": hi})
        else:
            for lo, hi in pieces:
                kept.append({**r, "era_from": lo, "era_to": hi})
    return kept, updates, deletes, extras


def clip_around_structural(
    rows: list[dict], struct_rows: list[dict]
) -> tuple[list[dict], list[tuple[int, date, date | None]], list[int], list[dict]]:
    """clip_rows around the structural eras, kind-merged: a structural value cell clips value rows, a structural
    reason cell clips reason rows (a value beside a reason coexists, as in docmap-load's merge). Pure."""
    kept: list[dict] = []
    ups: list[tuple[int, date, date | None]] = []
    dels: list[int] = []
    extras: list[dict] = []
    for is_value in (True, False):
        sub = [
            r for r in rows if (r["decision"] in ("concept", "component")) == is_value
        ]
        spans = sorted(
            {
                (_key(x), x["era_from"], x["era_to"] or date.max)
                for x in struct_rows
                if _key(x) is not None
                and (x["decision"] in ("concept", "component")) == is_value
            },
            key=repr,
        )
        k, u, d, e = clip_rows(sub, spans)
        kept += k
        ups += u
        dels += d
        extras += e
    return kept, ups, dels, extras


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
        "era_to": d.era_to,
        "evidence_adsh": d.accession,
        "evidence_report": d.report,
        "evidence_plabel": d.label or None,
        "decided_by": FIX_DECIDED_BY if d.is_fix else DECIDED_BY,
        "rule_id": FIX_RULE_ID if d.is_fix else RULE_ID,
    }
    if d.is_fix:
        base["serve_note"] = d.fix_note
    if d.base_era is not None and d.base_era > d.era_from:
        main = (
            table_rows(
                replace(d, era_from=d.base_era, base_era=None, ext_note=""),
                company_id,
                cik,
                concept_statement,
            )
            if d.era_to is None or d.base_era <= d.era_to
            else []
        )
        ext_to = d.base_era - timedelta(days=1)
        if d.era_to is not None:
            ext_to = min(ext_to, d.era_to)
        ref = main or table_rows(
            replace(d, base_era=None, ext_note=""),
            company_id,
            cik,
            concept_statement,
        )
        ext = [
            {
                **r,
                "era_from": d.era_from,
                "era_to": ext_to,
                "rule_id": era_extend.EXT_RULE_ID,
                "decided_by": "era_extend",
                "serve_note": d.ext_note,
            }
            for r in ref
        ]
        if d.ext_slices and d.status in TAGLESS_STATUS:
            ext = []
            for sf, st_, adsh, reps in d.ext_slices:
                lo, hi = max(sf, d.era_from), min(st_, ext_to)
                if lo > hi:
                    continue
                for r in ref:
                    ext.append(
                        {
                            **r,
                            "era_from": lo,
                            "era_to": hi,
                            "rule_id": era_extend.EXT_RULE_ID,
                            "decided_by": "era_extend",
                            "serve_note": d.ext_note,
                            "evidence_adsh": adsh,
                            "evidence_report": dict(reps).get(r["stmt"]),
                        }
                    )
        return main + ext
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
                # a combined line keeps the decision value (the table's 'combined' needs tags and components) but
                # its class says what the filing says; the row carries accession, printed label and R page
                "reason_class": COMBINED_CLASS
                if d.status == "combined"
                else f"docmap_{d.status.replace(' ', '_').lower()}"
                if not d.is_fix
                else f"docmap_fix_{d.status.replace(' ', '_').lower()}",
            }
        ]
    stmt = (
        "UN"
        if d.status == "component_in_note"
        else stmt_code(d.stmt_raw, d.data_point, st, value_row=True)
    )
    if d.status == "component sum":
        # a mixed claim keeps each part's own statement ('BS+BS+NOTE': face debt lines plus a note finance-lease
        # total, audit R06); one value, or a count that is not the part count, applies to every part as before
        raws = [x.strip() for x in d.stmt_raw.split("+")]
        per = raws if len(raws) == len(d.parts) and len(set(raws)) > 1 else None
        pages = [x.strip() for x in d.r_page.split("+")]
        per_page = pages if len(pages) == len(d.parts) else None
        return [
            {
                **base,
                "decision": "component",
                "parent_concept": d.data_point,
                "taxonomy": tax,
                "tag": tag,
                "sign": sign,
                "stmt": stmt_code(per[i], d.data_point, st, value_row=True)
                if per
                else stmt,
                # each part keeps its own R page when the row lists one per part ('R4.htm+R4.htm+R102.htm')
                **(
                    {"evidence_report": int(m.group(1))}
                    if per_page and (m := re.match(r"R(\d+)", per_page[i]))
                    else {}
                ),
            }
            for i, (sign, tax, tag) in enumerate(d.parts)
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
    cut: list[tuple[int, date | None]] = field(
        default_factory=list
    )  # (library row id, new era_to; None = open)
    edits: list[tuple[int, date, date | None]] = field(
        default_factory=list
    )  # reader fixes: (row id, new era_from, new era_to)
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
        if d.comparative_start and d.prior_tags:
            # The read's era starts at the comparative year: the next 10-K prints the new tag for it, but that year's
            # own 10-K and its 10-Qs (the quarters, and the Q4 derived from that 10-K) print the prior tag, and those
            # cells exist only under it. The prior era (the library row carrying the tag the read names) is kept
            # through that first year; the new tag starts one year later (MSFT sbc FY2016 quarters were lost).
            new_from = _years_back(d.era_from, -1)
            for r in existing:
                if (
                    r["decision"] not in REASON_DECISIONS | {"excluded", "combined"}
                    and cid in (r["canonical_concept_id"], r["parent_concept_id"])
                    and r["tag"] in d.prior_tags
                    and r["era_to"] is not None
                    and d.era_from - timedelta(days=1)
                    <= r["era_to"]
                    < new_from - timedelta(days=1)
                ):
                    # a row this loader cut at the comparative year before: open it to the first year's end
                    plan.cut.append((r["id"], new_from - timedelta(days=1)))
            d = replace(d, era_from=new_from)
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
            # same decision and tags: the library row stands, but the docmap's earlier era is not lost; the docmap
            # row is written for the years before the library row starts
            lib_from = min(r["era_from"] for r in current)
            if d.era_from < lib_from:
                plan.insert.append(replace(d, era_to=lib_from - timedelta(days=1)))
            # ... and its later era is not lost either: the docmap reads the same tags through the present (open
            # era), the agreeing library row was cut at the FY the Tag Expert read (MSFT cash_paid_*: era_to
            # 2026-06-30), which left the 2026-09-30 10-Q period uncovered, so the tagmap-plan concept gate skipped
            # the whole concept and FY2015-FY2024 never served. The last library row is opened to the docmap's end.
            if d.era_to is None:
                last = max(current, key=lambda r: r["era_to"] or date.max)
                if last["era_to"] is not None:
                    plan.cut.append((last["id"], None))
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
select * from analytics.company_tag_map where company_id = any(%s)
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


def _base(name: str) -> str:
    return {"revenue_sanity_resolved": "revenue"}.get(
        name, name.removesuffix("_resolved")
    )


def global_candidates(conn: psycopg.Connection) -> dict[str, set[str]]:
    """Base concept name -> every tag the map serves it with, for any company (the candidate set an absence check
    must rule out; same idea as fy_era_status.candidates)."""
    out: dict[str, set[str]] = defaultdict(set)
    with conn.cursor() as cur:
        cur.execute(
            """select coalesce(cc.name, pc.name), m.tag
               from analytics.company_tag_map m
               left join analytics.canonical_concept cc on cc.id = m.canonical_concept_id
               left join analytics.canonical_concept pc on pc.id = m.parent_concept_id
               where m.decision in ('concept', 'component') and m.tag is not null
               group by 1, 2"""
        )
        for name, tag in cur.fetchall():
            if name:
                out[_base(name)].add(tag)
    return out


def extend_company(
    conn: psycopg.Connection,
    cid: int,
    rows: list[DocmapRow],
    concept_ids: dict[str, int],
    log: list[dict],
    global_cands: dict[str, set[str]] | None = None,
) -> list[DocmapRow]:
    """--extend-eras: each row's era walked back through the company's earlier 10-Ks. Value rows: same tag, same
    line or value (era_extend.extend). Reason rows (not_presented, combined, OUT): while no candidate tag of the concept
    is on a statement line or in the filing's facts (era_extend.extend_absent)."""
    global_cands = global_cands or {}
    value_rows = [d for d in rows if d.status in VALUE_STATUSES]
    reason_rows = [d for d in rows if d.status in TAGLESS_STATUS]
    if not value_rows and not reason_rows:
        return rows

    def ids_of(d: DocmapRow) -> set[int]:
        return {
            concept_ids[n]
            for n in (d.data_point, d.data_point.removesuffix("_resolved"))
            if n in concept_ids
        }

    own: dict[str, set[str]] = defaultdict(
        set
    )  # the docmap's own value tags per base concept
    for d in value_rows:
        own[_base(d.data_point)] |= {tag for _, _, tag in d.parts}
    tags = {tag for d in value_rows for _, _, tag in d.parts}
    cids = {c for d in value_rows + reason_rows for c in ids_of(d)}
    cand_tags: set[str] = set()
    for d in reason_rows:
        cand_tags |= (
            global_cands.get(_base(d.data_point), set()) | own[_base(d.data_point)]
        )
        cand_tags |= {tag for _, _, tag in d.parts}
    data = era_extend.fetch(conn, cid, tags | cand_tags, cids)
    with_facts, present = (
        era_extend.fetch_facts(conn, cid, cand_tags) if reason_rows else (set(), {})
    )
    out = []
    for d in rows:
        if d.status in VALUE_STATUSES:
            era, adsh, rlog, by_value = era_extend.extend(
                [tag for _, _, tag in d.parts], ids_of(d), d.era_from, d.accession, data
            )
            if by_value:
                note = (
                    f"{era_extend.EXT_MARK_VALUE}: same tag carried non-dimensionally, same period type and unit "
                    f"class, no other tag mapped to the concept, in each 10-K back to {adsh} (FY from {era}); "
                    f"docmap read {d.accession}"
                )
            else:
                note = (
                    f"{era_extend.EXT_MARK}: same tag on the same line (stmt, role/label, calc parent) in each "
                    f"10-K back to {adsh} (FY from {era}); docmap read {d.accession}"
                )
        elif d.status in TAGLESS_STATUS:
            cands = (
                global_cands.get(_base(d.data_point), set())
                | own[_base(d.data_point)]
                | {
                    t
                    for c in ids_of(d)
                    for acc_map in data.mapped.values()
                    for t in acc_map.get(c, ())
                }
            )
            era, adsh, rlog = era_extend.extend_absent(
                cands,
                [tag for _, _, tag in d.parts] if d.status == "combined" else [],
                d.era_from,
                data,
                with_facts,
                present,
            )
            slices = era_extend.absent_slices(rlog, d.era_from)
            era = slices[-1][0] if slices else d.era_from
            adsh = slices[-1][2] if slices else None
            reps = era_extend.face_reports(conn, {x[2] for x in slices})
            ext_slices = tuple(
                (a_, b_, c_, tuple(sorted(reps.get(c_, {}).items())))
                for a_, b_, c_ in slices
            )
            note = (
                f"{era_extend.EXT_MARK_ABSENT}: in each 10-K back to {adsh} (FY from {era}) no candidate tag of the "
                f"concept on a statement line or in the facts"
                + (
                    "; the combined line still printed"
                    if d.status == "combined"
                    else ""
                )
                + f"; docmap read {d.accession}"
            )
        else:
            out.append(d)
            continue
        for r in rlog:
            log.append(
                {
                    "ticker": d.ticker,
                    "data_point": d.data_point,
                    "kind": d.status,
                    "read_adsh": d.accession,
                    **r,
                }
            )
        if adsh is not None and era < d.era_from:
            d = replace(
                d,
                era_from=era,
                base_era=d.era_from,
                ext_note=note,
                ext_slices=ext_slices if d.status in TAGLESS_STATUS else (),
            )
        out.append(d)
    return out


def load(
    conn: psycopg.Connection,
    paths: list[Path],
    *,
    apply: bool = False,
    extend_eras: bool = False,
    era_log: Path | None = None,
    predictor_eras: Path | None = None,
    predictor_concepts: set[str] | None = None,
    no_filing_ciks: set[str] | None = None,
    fixes: Path | None = None,
) -> dict:
    """Plan (and with apply, write) every docmap in `paths`. One transaction per company; a company whose rows fail
    validation or era overlap is skipped whole and listed.
    predictor_eras: directory of the Tag Expert's per-10-K predictions; the years the FSN extension could not carry
    become era_extend@1 / tag_expert_predictor CANDIDATE slices (era_guard.hold_unproven decides them after the cell
    proof). predictor_concepts (base names, e.g. total_debt, interest_expense) reloads only those concepts: only their
    predictor and guard rows are replaced. no_filing_ciks: companies with no 10-K before their listing: the uncovered
    years are reasoned blanks no_public_filing_for_period.
    fixes: directory of reader fix files (<TICKER>-fixes-<date>.csv, one row per cell): each overrides the docmap, era
    extension, predictor and library rows of that one data point for that one fiscal year (the rows are split around it,
    the other years stay); rule company_tag_map.docmap_fix@1, decided_by reader_fix."""
    from scrooner_pipeline.mapper import era_predictor

    preds = era_predictor.read_predictions(predictor_eras) if predictor_eras else {}
    no_filing = {c.zfill(10) for c in (no_filing_ciks or set())}
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
    era_log_rows: list[dict] = []
    global_cands = global_candidates(conn) if extend_eras else {}
    stats["extended"] = []
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
        if extend_eras:
            ok = extend_company(conn, cid, ok, concept_ids, era_log_rows, global_cands)
            stats["extended"] += [
                {
                    "ticker": d.ticker,
                    "data_point": d.data_point,
                    "kind": d.status,
                    "era_from": d.era_from,
                    "base_era": d.base_era,
                }
                for d in ok
                if d.base_era is not None
            ]
        stats["rows"] += len(ok)
        docs[cid] = (cik, ok)
    fixes_by_cid: dict[int, list[DocmapRow]] = {}
    fix_cells: dict[tuple[str, str, date], DocmapRow] = {}
    stats["fix_files"] = 0
    for p in fix_files(fixes):
        stats["fix_files"] += 1
        frows, frejects = parse_fixes(p.read_text(), p.name)
        stats["rejects"] += frejects
        for d in frows:  # a newer file corrects an older one for the same cell
            fix_cells[(d.ticker, d.data_point, d.era_to or date.max)] = d
    fix_by_ticker: dict[str, list[DocmapRow]] = defaultdict(list)
    for d in fix_cells.values():
        fix_by_ticker[d.ticker].append(d)
    for ticker, frows in sorted(fix_by_ticker.items()):
        hits = by_ticker.get(ticker, set())
        if len(hits) != 1:
            stats["blocked"][f"{ticker} fixes"] = (
                f"ticker {ticker} resolves to {len(hits)} companies"
            )
            continue
        ((cid, cik),) = hits
        if cid not in docs:
            stats["blocked"][f"{ticker} fixes"] = (
                "no docmap file loaded for the company: a fix overrides docmap rows, it is not a docmap"
            )
            continue
        good: list[DocmapRow] = []
        for d in (
            replace(d, data_point=served_concept(d.data_point, set(concept_ids)))
            for d in assign_fix_eras(frows)
        ):
            why = None
            if d.data_point not in concept_ids:
                why = "no canonical concept of that name"
            elif d.status == "component sum" and instant_sum_refused(
                d.data_point, concept_statement[d.data_point]
            ):
                why = "instant component sum refused (only total_debt)"
            else:
                try:
                    for t in table_rows(d, cid, cik, concept_statement):
                        normalize(t, {}, concept_ids, FIX_RULE_ID, [])
                except (ValueError, TypeError) as exc:
                    why = f"invalid row: {exc}"
            if why:
                stats["rejects"].append(
                    {
                        "source": d.source,
                        "ticker": d.ticker,
                        "data_point": d.data_point,
                        "status": d.status,
                        "why": f"fix: {why} (period_end {d.era_to})",
                    }
                )
            else:
                good.append(d)
        fixes_by_cid[cid] = good
        stats["fix_rows"] = stats.get("fix_rows", 0) + len(good)
    with conn.cursor() as cur:
        cur.execute(EXISTING_SQL, (sorted(docs),))
        cols = [c.name for c in cur.description]
        existing: dict[int, list[dict]] = defaultdict(list)
        for row in cur.fetchall():
            rec = dict(zip(cols, row))
            existing[rec["company_id"]].append(rec)
    names = {i: n for n, i in concept_ids.items()}
    period_ends: dict[int, list[date]] = {
        pc: reporting_period_ends(conn, pc) for pc in sorted(docs)
    }
    writes = []
    for cid, (cik, rows) in sorted(docs.items()):
        own = [r for r in existing[cid] if r["rule_id"] in OWN_RULES]
        mine = [r for r in own if r["decided_by"] not in era_predictor.PRED_BY]
        pred_old = [r for r in own if r["decided_by"] in era_predictor.PRED_BY]
        struct_rows = [r for r in existing[cid] if r["rule_id"] == STRUCTURAL_RULE_ID]
        library = [
            r
            for r in existing[cid]
            if r["rule_id"] not in OWN_RULES and r["rule_id"] != STRUCTURAL_RULE_ID
        ]
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
        ] + struct_rows
        # comparative-column extension: a year no row covers takes the next 10-K's prior-year column when that 10-K
        # prints the same tag(s) as the nearest covered year (predictor/guard rows are not evidence and do not cover)
        comp: list[dict] = []
        if extend_eras and cik not in no_filing:
            comp = comparative_rows(
                conn,
                cid,
                cik,
                kept + new,
                concept_ids,
                stats.setdefault("comparative_log", []),
                global_cands,
            )
            stats.setdefault("comparative", []).extend(
                {
                    "cik": cik,
                    "concept": names.get(
                        r["canonical_concept_id"] or r["parent_concept_id"]
                    ),
                    "tag": r["tag"],
                    "era_from": r["era_from"],
                    "era_to": r["era_to"],
                    "adsh": r["evidence_adsh"],
                }
                for r in comp
            )
            new = new + comp
        # predictor candidates / no-public-filing reasons for the years still uncovered; the predictor and guard rows
        # of the reloaded concepts are replaced, the others stay unless a new row now covers their years
        pnew: list[dict] = []
        pred_delete: list[int] = []
        if preds or cik in no_filing:
            ticker = rows[0].ticker if rows else ""
            try:
                if cik in no_filing:
                    raw = era_predictor.no_filing_rows(
                        rows, concept_statement, cid, cik
                    )
                else:
                    raw, prejects = era_predictor.candidates(
                        ticker,
                        preds.get(ticker, {}),
                        rows,
                        concept_ids,
                        concept_statement,
                        cid,
                        cik,
                        concepts=predictor_concepts,
                    )
                    stats["rejects"] += prejects
                pnew = [normalize(t, {}, concept_ids, RULE_ID, warnings) for t in raw]
            except (ValueError, TypeError) as exc:
                stats["blocked"][cik] = str(exc)
                continue
        scope_ids = (
            {
                concept_ids[n]
                for c in predictor_concepts
                for n in (c, served_concept(c, set(concept_ids)))
                if n in concept_ids
            }
            if predictor_concepts is not None
            else None
        )

        def key(r):
            return r["canonical_concept_id"] or r["parent_concept_id"]

        def overlaps(a, b):
            return (
                key(a) == key(b)
                and a["era_from"] <= (b["era_to"] or date.max)
                and b["era_from"] <= (a["era_to"] or date.max)
            )

        if preds or cik in no_filing:
            pred_delete = [
                r["id"]
                for r in pred_old
                if (scope_ids is None or key(r) in scope_ids)
                or any(overlaps(r, n) for n in new)
            ]
        if comp:  # filing evidence beats a predictor candidate for the same years
            pred_delete += [
                r["id"]
                for r in pred_old
                if r["id"] not in set(pred_delete) and any(overlaps(r, n) for n in comp)
            ]
        keep_pred = [r for r in pred_old if r["id"] not in set(pred_delete)]
        # a candidate never overlaps a row that already covers its years (library, docmap, extension, kept predictor)
        pnew = [
            n for n in pnew if not any(overlaps(n, k) for k in kept + new + keep_pred)
        ]
        if (
            struct_rows
        ):  # structural cells beat this loader's docmap / extension / predictor rows
            new, _, _, _ = clip_around_structural(new, struct_rows)
            pnew, _, _, _ = clip_around_structural(pnew, struct_rows)
            keep_pred, ed3, de3, x3 = clip_around_structural(keep_pred, struct_rows)
            plan.edits += ed3
            pred_delete += de3
            new = new + x3
        fix_rows = fixes_by_cid.get(cid, [])
        if fix_rows:
            try:
                fnew = [
                    normalize(t, {}, concept_ids, FIX_RULE_ID, warnings)
                    for d in fix_rows
                    for t in table_rows(d, cid, cik, concept_statement)
                ]
            except (ValueError, TypeError) as exc:
                stats["blocked"][cik] = str(exc)
                continue
            spans = sorted({(_key(r), r["era_from"], r["era_to"]) for r in fnew})
            kept, ed1, de1, x1 = clip_rows(kept, spans)
            keep_pred, ed2, de2, x2 = clip_rows(keep_pred, spans)
            new, _, _, _ = clip_rows(new, spans)
            pnew, _, _, _ = clip_rows(pnew, spans)
            plan.edits += ed1 + ed2
            plan.delete += de1
            pred_delete += de2
            new = new + fnew + x1 + x2
        errors = check_overlaps(kept + keep_pred + new + pnew)
        if errors:
            stats["blocked"][cik] = "; ".join(errors[:3])
            continue
        new_all = new + pnew
        before = {_content(r, names) for r in mine}
        after = {_content(r, names) for r in new}
        # the era half of tagmap-plan's coverage gate, on the merged map (library kept + new rows)
        short = era_shortfall(
            [
                (
                    r["canonical_concept_id"] or r["parent_concept_id"],
                    r["era_from"],
                    r["era_to"],
                )
                for r in kept + keep_pred + new_all
            ],
            period_ends.get(cid, []),
            unread_tail_concepts(
                [
                    (
                        r["canonical_concept_id"] or r["parent_concept_id"],
                        r["era_from"],
                        r["era_to"],
                        r.get("rule_id"),
                    )
                    for r in kept + keep_pred + new_all
                ]
            ),
        )
        era_report = {
            "era_short": len(short),
            "era_from_min": min(
                (r["era_from"] for r in kept + keep_pred + new_all), default=None
            ),
        }
        stats["companies"][cik] = {
            **era_report,
            "map_rows": [  # the merged map after this load: (concept, tag, decision, era_from, era_to)
                (
                    names.get(r["canonical_concept_id"] or r["parent_concept_id"]),
                    r["tag"],
                    r["decision"],
                    r["era_from"],
                    r["era_to"],
                )
                for r in kept + keep_pred + new_all
            ],
            "predictor_rows": len(pnew),
            "company_id": cid,
            "docmap_rows": len(new),
            "fix_rows": len(fix_rows),
            "fix_clipped": len(plan.edits),
            "added": len(after - before),
            "removed": len(before - after),
            "library_cut": len(plan.cut),
            "library_deleted": len(plan.delete),
            "agree": plan.agree,
            "conflicts": len(plan.conflicts),
        }
        writes.append((cid, new_all, plan, pred_delete))
    if era_log is not None:
        write_listing(era_log, era_log_rows)
    if not apply:
        return stats
    for cid, new, plan, pred_delete in writes:
        with conn.transaction():
            conn.execute(
                "delete from analytics.company_tag_map where company_id = %s and rule_id = any(%s) "
                "and decided_by <> all(%s)",
                (cid, list(OWN_RULES), list(era_predictor.PRED_BY)),
            )
            if pred_delete:
                conn.execute(
                    "delete from analytics.company_tag_map where id = any(%s)",
                    (pred_delete,),
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
                if plan.edits:
                    cur.executemany(
                        "update analytics.company_tag_map set era_from = %s, era_to = %s where id = %s",
                        [(a, b, rid) for rid, a, b in plan.edits],
                    )
                cur.executemany(INSERT, new)
    stats["applied"] = True
    return stats


def comparative_groups(rows: list[dict]) -> dict:
    """Map rows -> {concept key: [era_extend.Covered]}: one group per (era_from, era_to) of value rows (concept /
    component; payload = those rows), a reason group for every other row. Predictor and guard rows are no evidence:
    they neither cover nor serve as a neighbor."""
    by: dict = defaultdict(lambda: defaultdict(list))
    for r in rows:
        k = r["canonical_concept_id"] or r["parent_concept_id"]
        if k is None or r.get("decided_by") in era_predictor_by():
            continue
        by[k][(r["era_from"], r["era_to"])].append(r)
    out: dict = {}
    for k, eras in by.items():
        gs = []
        for (a, b), rs in eras.items():
            vals = [r for r in rs if r["decision"] in ("concept", "component")]
            gs.append(
                era_extend.Covered(
                    a, b, frozenset(r["tag"] for r in vals) if vals else None, vals
                )
            )
        out[k] = gs
    return out


def era_predictor_by() -> tuple[str, ...]:
    from scrooner_pipeline.mapper import era_predictor

    return era_predictor.PRED_BY


def comparative_rows(
    conn: psycopg.Connection,
    cid: int,
    cik: str,
    rows: list[dict],
    concept_ids: dict[str, int],
    log: list[dict],
    global_cands: dict[str, set[str]] | None = None,
) -> list[dict]:
    """The comparative-column extension rows (era_extend@1, decided_by era_comparative) for one company's merged map.
    Evidence: the next 10-K's accession (the year is its prior-year column)."""
    groups = comparative_groups(rows)
    tags = {t for gs in groups.values() for g in gs if g.tags for t in g.tags}
    if not tags:
        return []
    ids = set(groups)
    base_ids: dict[int, set[int]] = {}
    names = {i: n for n, i in concept_ids.items()}
    for k in ids:
        nm = names.get(k, "")
        base = {k}
        for alias in (nm.removesuffix("_resolved"), nm + "_resolved"):
            if alias in concept_ids:
                base.add(concept_ids[alias])
        base_ids[k] = base
    filings, printed, own, mapped = era_extend.fetch_printed(
        conn, cid, tags, {i for s in base_ids.values() for i in s}
    )

    def other(acc: str, key: int) -> set[str]:
        return {t for i in base_ids[key] for t in mapped.get(acc, {}).get(i, ())}

    slices, clog = era_extend.comparative_slices(groups, filings, printed, own, other)
    log.extend({"cik": cik, **x} for x in clog)
    out = []
    # rule 3: the year's own quarters keep the tag their own 10-Qs print (candidates: every value row of the concept,
    # predictor rows included, grouped by era and tag set); the comparative slice then covers the fiscal-year cell only
    by_era: dict[int, dict[tuple, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        k = r["canonical_concept_id"] or r["parent_concept_id"]
        if k in groups and r["decision"] in ("concept", "component") and r["tag"]:
            by_era[k][(r["era_from"], r["era_to"])].append(r)
    cand_rows: dict[int, dict[frozenset, list[dict]]] = defaultdict(dict)
    for k, eras in by_era.items():
        for rs in eras.values():
            cand_rows[k].setdefault(frozenset(r["tag"] for r in rs), rs)
    # the tags the year's own 10-Qs print on a face line mapped to the concept (fsn.line_map): candidates too, cloned
    # from the comparative row with the 10-Q line's taxonomy, tag and statement
    qmapped = era_extend.fetch_quarter_mapped(
        conn, cid, {i for s in base_ids.values() for i in s}
    )
    glob = {k: (global_cands or {}).get(_base(names.get(k, "")), set()) for k in groups}
    q_tags = (
        {t for k in cand_rows for g in cand_rows[k] for t in g}
        | {t for ts in glob.values() for t in ts}
        | {
            full.rsplit(":", 1)[-1]
            for per in qmapped.values()
            for tags in per.values()
            for full in tags
        }
    )
    tenqs, qprinted = (
        era_extend.fetch_quarter_prints(conn, cid, q_tags) if q_tags else ({}, {})
    )
    qface = era_extend.fetch_quarter_face(conn, cid, q_tags)
    split_slices = []
    for s in slices:
        cands = dict(cand_rows.get(s.key, {}))
        extra: dict[frozenset, tuple[str, str]] = {}
        year_q = [
            a for a, p in tenqs.items() if s.era_from <= p < s.era_to and a in qmapped
        ]
        mapped_sets = [
            qmapped[a].get(k) or {}
            for a in year_q
            for k in base_ids.get(s.key, {s.key})
            if qmapped[a].get(k)
        ]
        if year_q and len(mapped_sets) == len(year_q):
            common = set.intersection(*(set(m) for m in mapped_sets))
            for full in sorted(common):
                local = full.rsplit(":", 1)[-1]
                fs = frozenset({local})
                if (
                    fs != s.tags
                    and fs not in cands
                    and mapped_sets[0][full] in FACE_CODES
                    and s.source.payload
                    and s.source.payload[0]["decision"] == "concept"
                ):
                    cands[fs] = []
                    extra[fs] = (full, mapped_sets[0][full])
        if s.source.payload and s.source.payload[0]["decision"] == "concept":
            for local in sorted(glob.get(s.key, set())):
                fs = frozenset({local})
                if fs != s.tags and fs not in cands and local in qface:
                    cands[fs] = []
                    extra[fs] = qface[local]
        sp = era_extend.quarter_split(
            s.era_from, s.era_to, s.tags, list(cands), tenqs, qprinted
        )
        if sp is None or sp.last_quarter_end >= s.era_to:
            split_slices.append(s)
            continue
        split_slices.append(
            replace(s, era_from=sp.last_quarter_end + timedelta(days=1))
        )
        qnote = (
            f"{era_extend.COMP_MARK}: the quarters of the year keep the tag(s) {'+'.join(sorted(sp.tags))} their own "
            f"10-Qs print (last {sp.adsh}); the next 10-K's comparative tag(s) {'+'.join(sorted(s.tags))} "
            f"cover the fiscal-year cell only"
        )
        if (
            sp.tags in extra
        ):  # a tag only the 10-Qs' mapped face lines name: the comparative row, retagged
            full, st = extra[sp.tags]
            tax = full.rsplit(":", 1)[0] if ":" in full else "us-gaap"
            q_rows = [
                {
                    **r,
                    "taxonomy": tax,
                    "tag": full.rsplit(":", 1)[-1],
                    "stmt": st,
                    "decision": "concept",
                    "components": None,
                }
                for r in s.source.payload[:1]
            ]
        else:
            q_rows = cand_rows[s.key][sp.tags]
        for r in q_rows:
            n = {
                **r,
                "company_id": cid,
                "cik": cik,
                "era_from": s.era_from,
                "era_to": sp.last_quarter_end,
                "evidence_adsh": sp.adsh,
                "evidence_report": None,
                "evidence_line": None,
                "evidence_plabel": None,
                "evidence_cal_parent": None,
                "rule_id": era_extend.EXT_RULE_ID,
                "decided_by": era_extend.COMP_BY,
                "serve_note": qnote,
            }
            out.append(normalize(n, {}, concept_ids, era_extend.EXT_RULE_ID, []))
    slices = split_slices
    for s in slices:
        note = (
            f"{era_extend.COMP_MARK}: the 10-K {s.adsh} prints the year as its prior-year column with the same "
            f"tag(s) {'+'.join(sorted(s.tags))} as the nearest covered year"
        )
        for r in s.source.payload:
            n = {
                **r,
                "company_id": cid,
                "cik": cik,
                "era_from": s.era_from,
                "era_to": s.era_to,
                "evidence_adsh": s.adsh,
                "evidence_report": None,
                "evidence_line": None,
                "evidence_plabel": None,
                "evidence_cal_parent": None,
                "rule_id": era_extend.EXT_RULE_ID,
                "decided_by": era_extend.COMP_BY,
                "serve_note": note,
            }
            out.append(normalize(n, {}, concept_ids, era_extend.EXT_RULE_ID, []))
    return out


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
