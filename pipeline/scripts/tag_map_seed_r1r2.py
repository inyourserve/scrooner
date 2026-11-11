#!/usr/bin/env python3
"""ONE loader for every tag-decision source -> per-company analytics.company_tag_map rows (migration 0122). CSV only.

Founder order 2026-11-11: "FSN for learning (which tag is what), SEC for mapping" and "no mapping without reading
first". Nothing here decides what a tag means; it reads decisions written by Tag Experts / Ritwik and applies them.
Sources, precedence high to low (a company row overrides a tag-level row for the same (company, tag, stmt, era)):
  1 COMPANY rows  data-team/47-fsn-store/company_tag_map/ranks_*.csv (contract columns; blank decision = undecided)
      and data-team/tags/decisions/companies-*-exceptions-*.csv
      company_id, ticker, stmt, tag (empty = concept-level), decision map|exclude|not_presented|not_in_template|
      combined|review, concept, era_from, era_to (YYMM or ISO), n_filings, reason.   rule_id tagmap.company@1
  2 TAG-level     data-team/tags/decisions/std-tags-rank-*.csv
      rank, tag 'us-gaap:X', statements 'BS/CF', decision map|exclude|component|combined|review, concept, reason
      data-team/tags/library/fsn-*.csv  (tag, home_stmt, decision, concept key, sign, applies_to, exceptions, era,
      evidence; header spelling tolerant).   rule_id tagmap.library@1
  Tag-level rows apply to each company on the statements where it actually uses the tag (FSN, period >= 2014-01-01,
  IS/BS/CF), restricted to the listed statements, applies_to (all | sector template | company ids), exceptions, era.
Mapping: map -> concept; exclude -> excluded; review -> not loaded (undecided; a company review row also blocks the
tag-level row for that key/era). component/combined are loaded only when the source gives what the contract needs
(component: parent concept and sign; combined: member tags); otherwise listed as needs_detail, never guessed.
Concept-level company rows (no tag) go to OUT.concept_level.csv (not part of company_tag_map: the table needs a tag).
A concept name that is not in analytics.canonical_concept is not loaded and is listed (unknown_concept).
decided_by = source file name. Reads production with one connection, statement_timeout 120s; no writes.
Usage: tag_map_seed_r1r2.py OUT.csv [--decisions DIR_GLOB ...] [--batch N]
Evidence label: DATA-INFERRED structure + the source's own evidence; not a filing-checked value.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import glob
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COHORT_CSV = REPO / "data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv"
DEFAULT_GLOBS = [
    str(REPO / "data-team/47-fsn-store/company_tag_map/ranks_*.csv"),
    str(REPO / "data-team/tags/decisions/companies-*-exceptions-*.csv"),
    str(REPO / "data-team/tags/decisions/std-tags-rank-*.csv"),
    str(REPO / "data-team/tags/library/fsn-*.csv"),
]

RULE_LIBRARY = "tagmap.library@1"
RULE_COMPANY = "tagmap.company@1"
FLOOR = date(2014, 1, 1)
SEED_STMTS = ("IS", "BS", "CF", "CI")
STD_TAXONOMIES = ("us-gaap", "srt", "dei", "ifrs-full")
DECISION_MAP = {"map": "concept", "concept": "concept", "exclude": "excluded", "excluded": "excluded",
                "component": "component", "combined": "combined"}
CONCEPT_LEVEL = ("not_presented", "not_in_template")
FID, PLABEL = 5, 14  # positions in an appearance tuple (see APPEAR_SQL)
CONDITIONS_CSV = Path(__file__).with_name("tag_map_conditions.csv")
# Sign rulings (Dhairya / founder 2026-11-11, NEE, VZ, TMUS): a blank-sign company component row is additive (+1)
# when its own reason says it is a sum / an include. Anything else without a sign stays needs_detail.
PLUS_REASON = re.compile(r"\bsum\b|component sum|capex =|INCLUDE in capex", re.I)

COLUMNS = [
    "company_id", "cik", "taxonomy", "tag", "stmt", "decision", "canonical_concept", "parent_concept",
    "combine_sign", "components", "reason_class", "reason", "era_from", "era_to", "evidence_adsh",
    "evidence_report", "evidence_line", "evidence_plabel", "evidence_cal_parent", "decided_by", "rule_id",
]


# ---------------------------------------------------------------- pure logic (unit tested)

def _hk(h: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", h.strip().lower()).strip("_")


def _split(v: str) -> list[str]:
    return [x.strip() for x in re.split(r"[;,|]", v or "") if x.strip()]


def parse_range(text: str) -> tuple[date | None, date | None]:
    """'2019-01-01..2021-12-31', '2019-01-01..', '..2021-12-31' or '' -> (from, to), None = open."""
    text = (text or "").strip()
    if not text or text.lower() in ("all", "any", "*"):
        return None, None
    a, _, b = text.partition("..")
    return (date.fromisoformat(a.strip()) if a.strip() else None,
            date.fromisoformat(b.strip()) if b.strip() else None)


def parse_period(text: str, end: bool) -> date | None:
    """ISO date, or YYMM (a period month, as in the company-exception files): first / last day of that month."""
    text = (text or "").strip()
    if not text:
        return None
    if re.fullmatch(r"\d{4}", text) and int(text[2:]) > 12:  # a plain year (tag cards: '2015'), not YYMM
        return date(int(text), 12, 31) if end else date(int(text), 1, 1)
    if re.fullmatch(r"\d{4}", text):
        y, m = 2000 + int(text[:2]), int(text[2:])
        return date(y, m, calendar.monthrange(y, m)[1] if end else 1)
    if re.fullmatch(r"\d{4}-\d{2}", text):  # 'YYYY-MM' (tag cards)
        y, m = int(text[:4]), int(text[5:])
        return date(y, m, calendar.monthrange(y, m)[1] if end else 1)
    return date.fromisoformat(text)


def _tag(raw: str) -> tuple[str | None, str]:
    if ":" in raw:
        tx, tag = raw.split(":", 1)
        return (tx if tx in STD_TAXONOMIES else None), tag
    return None, raw


def _entry(**kw) -> dict:
    base = {"taxonomy": None, "company": None, "decision": "", "concept": "", "sign": "", "components": [],
            "applies_to": "", "era": (None, None), "reason": "", "exceptions": [], "source": "", "rule_id": RULE_LIBRARY,
            "home_stmts": [], "kind": "tag", "cond": [], "else_reason": "", "reason_class": "", "raw": None, "prio": 2, "detail_note": "", "exceptions_text": ""}
    base.update(kw)
    return base


def parse_company_rows(rows: list[dict], source: str) -> list[dict]:
    out = []
    for raw in rows:
        r = {_hk(k): (v or "").strip() for k, v in raw.items() if k}
        if not r.get("company_id"):
            continue
        dec = r.get("decision", "").lower()
        stmt = r.get("stmt", "").upper()
        reason = r.get("reason", "")
        sign = r.get("sign", "")
        if DECISION_MAP.get(dec) == "component" and not sign and PLUS_REASON.search(reason):
            sign = "+1"
        for raw_tag in [t.strip() for t in r.get("tag", "").split(" + ")] or [""]:  # 'A + B' = two component rows
            tx, tag = _tag(raw_tag)
            out.append(_entry(
                taxonomy=tx, company=int(r["company_id"]), decision=dec, concept=r.get("concept", ""),
                reason=reason, sign=sign, home_stmts=[stmt],
                era=(parse_period(r.get("era_from", ""), False), parse_period(r.get("era_to", ""), True)),
                source=source, rule_id=RULE_COMPANY, prio=0, kind="company_tag" if tag else "company_concept")
                | {"tag": tag})
    return out


def parse_tag_rows(rows: list[dict], source: str) -> list[dict]:
    """Three tag-level shapes, header spelling tolerant of case, spaces, underscores:
    tag cards data-team/tags/library/fsn-*.csv (canonical_concept_key, sign_rule, applies_to, exceptions, era_from,
    era_to, evidence; decided_by 'tag-card', prio 1), std-tags-rank files (statements, concept, reason; prio 2),
    and the older library shape (home_stmt, concept key, sign, era)."""
    out = []
    for raw in rows:
        r = {_hk(k): (v or "").strip() for k, v in raw.items() if k}
        if not r.get("tag"):
            continue
        card = "canonical_concept_key" in r
        tx, tag = _tag(r["tag"])
        homes_txt = r.get("statements") or r.get("home_stmt", "")
        if re.search(r"parenthetical", homes_txt, re.I):  # 'BS parenthetical' lines are FSN stmt CP, not seeded
            homes_txt = "CP"
        stmts = [x.upper() for x in re.split(r"[/;,| ]+", homes_txt) if x]
        lo, hi = parse_range(r.get("era", ""))
        if r.get("era_from") or r.get("era_to"):
            lo, hi = parse_period(r.get("era_from", ""), False), parse_period(r.get("era_to", ""), True)
        exc_txt = r.get("exceptions", "")
        try:
            if exc_txt and not re.fullmatch(r"[\d@.\-;,| ]+", exc_txt):
                raise ValueError
            exc, exc_free = parse_exceptions(exc_txt), ""
        except ValueError:
            exc, exc_free = [], exc_txt  # free-text exceptions are not machine-evaluated; carried as a note
        out.append(_entry(
            taxonomy=tx, tag=tag, home_stmts=stmts, decision=r.get("decision", "").lower(),
            concept=r.get("canonical_concept_key") or r.get("concept_key") or r.get("concept", ""),
            sign=r.get("sign", "") if not card else "",
            applies_to=r.get("applies_to", ""), era=(lo, hi), reason=r.get("evidence") or r.get("reason", ""),
            components=_split(r.get("components", "")), exceptions=exc, exceptions_text=exc_free,
            source="tag-card" if card else source, prio=1 if card else 2))
    return out


def parse_ranks_rows(rows: list[dict], source: str) -> list[dict]:
    """Ritwik's per-company map (company_tag_map/ranks_1_50.csv), already in the contract columns. A blank decision is
    an undecided row ('review': loads nothing, blocks tag-level rows). Company-specific, so it wins."""
    out = []
    for r in rows:
        if not r.get("company_id") or not r.get("tag"):
            continue
        dec = r["decision"].strip().lower() or "review"
        sign = r.get("combine_sign", "").strip()
        out.append(_entry(
            taxonomy=r["taxonomy"] if r["taxonomy"] in STD_TAXONOMIES else None, tag=r["tag"],
            company=int(r["company_id"]), decision=dec,
            concept=r["parent_concept"] if DECISION_MAP.get(dec) == "component" else r["canonical_concept"],
            sign=sign, components=_split(r.get("components", "")), reason=r.get("reason", ""),
            home_stmts=[r["stmt"].upper()], source=f"{source}:{r.get('decided_by', '')}", rule_id=RULE_COMPANY,
            era=(parse_period(r.get("era_from", ""), False), parse_period(r.get("era_to", ""), True)),
            kind="company_tag", prio=0, reason_class=r.get("reason_class", ""), raw=r))
    return out


def parse_source(name: str, rows: list[dict]) -> list[dict]:
    head = {_hk(k) for k in (rows[0] if rows else {})}
    if "company_id" in head and "evidence_adsh" in head:
        ents = parse_ranks_rows(rows, name)
    else:
        ents = parse_company_rows(rows, name) if "company_id" in head else parse_tag_rows(rows, name)
    for e in ents:
        e["decision"] = DECISION_MAP.get(e["decision"], e["decision"])
    return ents


def parse_exceptions(text: str) -> list[tuple[int | None, tuple[date | None, date | None]]]:
    """Tokens separated by ; or ,|: '123' (company, all eras), '123@2019-01-01..2020-12-31' (company, era),
    '2019-01-01..2020-12-31' (era, all companies). Returns [(company_id or None, (from, to))]."""
    out = []
    for tok in _split(text):
        if "@" in tok:
            c, _, e = tok.partition("@")
            out.append((int(c), parse_range(e)))
        elif tok.isdigit():
            out.append((int(tok), (None, None)))
        elif ".." in tok:
            out.append((None, parse_range(tok)))
        else:
            raise ValueError(f"unparseable exception token {tok!r}")
    return out


def applies(entry: dict, company_id: int, templates: set[str]) -> bool:
    """Company rows: only that company. Tag rows: explicit numeric company ids or 'sector:'/'template:' names restrict;
    empty, 'all...' and any other descriptive text (tag cards: 'classified balance sheets (828 cos)') applies to all."""
    if entry["company"] is not None:
        return entry["company"] == company_id
    toks = _split(entry["applies_to"])
    ids = {int(t) for t in toks if t.isdigit()}
    names = {re.sub(r"^(sector|template|sector_template)\s*:\s*", "", t, flags=re.I).strip().lower()
             for t in toks if re.match(r"(sector|template|sector_template)\s*:", t, re.I)}
    if not ids and not names:
        return True
    return company_id in ids or bool(names & {x.lower() for x in templates})


def _lo(d):  # None = -inf
    return date.min if d is None else d


def _hi(d):  # None = +inf
    return date.max if d is None else d


def clip(era: tuple[date, date | None], include: tuple, excludes: list[tuple]) -> list[tuple[date, date | None]]:
    """Intersect the company era with the entry era, then cut out the excluded ranges. Open end stays None."""
    lo, hi = max(era[0], _lo(include[0])), min(_hi(era[1]), _hi(include[1]))
    pieces = [(lo, hi)] if lo <= hi else []
    for ex_lo, ex_hi in excludes:
        el, eh = _lo(ex_lo), _hi(ex_hi)
        nxt = []
        for a, b in pieces:
            if eh < a or el > b:
                nxt.append((a, b))
                continue
            if el > a:
                nxt.append((a, date.fromordinal(el.toordinal() - 1)))
            if eh < b:
                nxt.append((date.fromordinal(eh.toordinal() + 1), b))
        pieces = nxt
    return [(a, None if b == date.max else b) for a, b in pieces]


def build_index(entries: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """(tag, stmt) -> entries; company rows first, then tag-level rows in source order. Concept-level rows excluded."""
    idx: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for e in sorted((x for x in entries if x["kind"] != "company_concept"), key=lambda x: x["prio"]):
        for stmt in e["home_stmts"]:
            idx[(e["tag"], stmt)].append(e)
    return idx


def missing_detail(e: dict) -> str | None:
    """What the contract needs but the source does not give, for component/combined; None when complete."""
    if e["decision"] == "component":
        miss = [n for n, v in (("parent concept", e["concept"]), ("sign", e["sign"])) if not v]
        if e["sign"] and e["sign"] not in ("+", "+1", "1", "-", "-1"):
            miss.append("sign unreadable")
        return ", ".join(miss) or None
    if e["decision"] == "combined":
        return None if e["components"] and e["concept"] else "member tags / concept"
    return None


def parse_condition(text: str) -> list[tuple[str, str]]:
    """'copresent:Tag and label!~regex and near~regex' -> [(kind, arg)]. Per-filing, from fsn.line only.
    near~ is an ambiguity guard for label!~: FSN plabels can be shifted one row (tag and value right), so a demotion
    on the label is only made when no neighbouring row label looks like the line the tag is wanted for."""
    out = []
    for tok in [t.strip() for t in re.split(r"\s+and\s+", text or "") if t.strip()]:
        m = re.match(r"(copresent:|absent:|label!~|label~|near~)(.+)$", tok)
        if not m:
            raise ValueError(f"unsupported condition {tok!r}")
        out.append((m.group(1), m.group(2).strip()))
    return out


def load_conditions(path: Path = CONDITIONS_CSV) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return [{_hk(k): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


def attach_conditions(entries: list[dict], overlay: list[dict]) -> None:
    """The overlay adds a per-filing condition to decisions that already exist in a source; it never creates one."""
    for o in overlay:
        for e in entries:
            if e["kind"] == "company_concept" or e["tag"] != o["tag"] or o["stmt"].upper() not in e["home_stmts"]:
                continue
            if o.get("company_id") and (e["company"] is None or e["company"] != int(o["company_id"])):
                continue
            if o.get("decision") and e["decision"] != o["decision"]:
                continue
            if o.get("concept") and e["concept"] != o["concept"]:
                continue
            e["cond"] = e["cond"] + parse_condition(o["condition"])
            e["else_reason"] = o.get("else_reason", "") or e["else_reason"]
            e["reason"] = o.get("reason", "") or e["reason"]


def is_nondim(row: tuple) -> bool:
    return row[16] if len(row) > 16 else True


def cond_ok(cond: list[tuple[str, str]], row: tuple, printed: dict) -> str:
    """One filing: 'ok', 'bad' (condition clearly fails) or 'amb' (a label demotion that a neighbouring row label
    contradicts, or no label to judge by). printed[(filing, stmt)] = tags printed on that statement."""
    tags = printed.get((row[FID], row[3]), set())
    lab = row[PLABEL] or ""
    near = [x for x in (row[17] if len(row) > 17 else None, row[18] if len(row) > 18 else None) if x]
    state = "ok"
    for kind, arg in cond:
        if kind == "copresent:" and arg not in tags:
            return "bad"
        if kind == "absent:" and arg in tags:
            return "bad"
        if kind == "label~" and not re.search(arg, lab, re.I):
            return "bad"
        if kind == "label!~":
            if not lab:
                state = "amb"
            elif re.search(arg, lab, re.I):
                guards = [a for k, a in cond if k == "near~"]
                state = "amb" if any(re.search(g, n, re.I) for g in guards for n in near) else "bad"
                if state == "bad":
                    return "bad"
    return state


def expand_company(company_id: int, templates: set[str], groups: dict, annual: list[date], index: dict) -> dict:
    """groups: (taxonomy, tag, stmt) -> {period: appearance tuple}. Returns key -> result dict
    {'rows': [(entry, era_from, era_to, row)], 'review': bool, 'needs_detail': [entry], 'override': bool}.
    Per-filing conditions (copresent/absent/label) and 'a printed total beats its components' split eras, so every
    emitted row is unconditional. Phase 1 places everything except components and records which concepts a filing
    prints as a total; phase 2 emits a component only for filings where its parent concept has no total row."""
    printed: dict[tuple, set] = defaultdict(set)
    for (tx, tag, stmt), appear in groups.items():
        for r in appear.values():
            printed[(r[FID], stmt)].add(tag)
    totals: dict[int, set[str]] = defaultdict(set)  # filing id -> concepts printed as a concept/combined total
    res = {k: {"rows": [], "review": False, "needs_detail": [], "override": False} for k in groups}
    for phase in (1, 2):
        for (tx, tag, stmt), appear in groups.items():
            _expand_key(company_id, templates, tx, tag, stmt, appear, annual, index, printed, totals, phase,
                        res[(tx, tag, stmt)])
    return res


def _expand_key(company_id, templates, taxonomy, tag, stmt, appear, annual, index, printed, totals, phase, res):
    all_eras = build_eras(appear, annual)
    for e_idx, era in enumerate([(a, b) for a, b, _ in all_eras]):
        company_taken: list[tuple] = []
        taken: list[tuple] = []  # tag-level pieces already claimed
        for e in index.get((tag, stmt), []):
            if (e["decision"] == "component") != (phase == 2) and e["decision"] != "review":
                continue
            if e["decision"] == "review" and phase == 2:
                continue
            if e["taxonomy"] and e["taxonomy"] != taxonomy:
                continue
            if not applies(e, company_id, templates):
                continue
            ex = [rng for cid, rng in e["exceptions"] if cid is None or cid == company_id]
            is_company = e["company"] is not None
            # filings of this era where the entry's per-filing conditions hold
            in_era = {p: r for p, r in appear.items() if era[0] <= p and (era[1] is None or p <= era[1])}
            states = {p: cond_ok(e["cond"], r, printed) for p, r in in_era.items()}
            ok = {p: r for p, r in in_era.items() if states[p] == "ok"
                  and (e["decision"] == "excluded" or is_nondim(r))  # concepts only from non-dimensional face lines
                  and not (e["decision"] == "component" and e["concept"] in totals[r[FID]])}
            bad = {p: r for p, r in in_era.items() if states[p] == "bad"}
            if any(v == "amb" for v in states.values()):
                res["needs_detail"].append(dict(e, detail_note="label demotion ambiguous: a neighbouring row label "
                                                "looks like the wanted line, or no label (FSN plabels can shift one row)"))
            variants = [(e, ok)]
            if e["else_reason"] and bad:
                variants.append((dict(e, decision="excluded", reason=e["else_reason"], concept="", kind="condition"),
                                 bad))
            for ent, sub in variants:
                sub_eras = build_eras(sub, annual)
                if sub_eras and sub_eras[-1][1] is None and max(in_era) > max(sub):
                    # the last eligible span ends where a later filing of this era no longer qualifies
                    sub_eras[-1] = (sub_eras[-1][0], max(sub), sub_eras[-1][2])
                for a, b, rr in sub_eras:
                    for pa, pb in clip((a, b), ent["era"], ex + company_taken + taken):
                        if not is_company and clip((a, b), ent["era"], ex + taken) != clip(
                                (a, b), ent["era"], ex + company_taken + taken):
                            res["override"] = True
                        (company_taken if is_company else taken).append((pa, pb))
                        dec = ent["decision"]
                        if dec == "review":
                            res["review"] = True
                        elif missing_detail(ent):
                            res["needs_detail"].append(ent)
                        elif dec in ("concept", "excluded", "component", "combined"):
                            res["rows"].append((ent, pa, pb, rr))
                            if dec in ("concept", "combined") and phase == 1:
                                for p, r in sub.items():
                                    if pa <= p and (pb is None or p <= pb):
                                        totals[r[FID]].add(ent["concept"])
                        else:  # e.g. not_presented / not_in_template on a tagged row
                            res["needs_detail"].append(ent)


def library_row(e: dict) -> dict:
    """Contract fields (without company/evidence) for one decision entry."""
    dec = e["decision"]
    sign = e["sign"].strip()
    row = {"decision": dec, "canonical_concept": "", "parent_concept": "", "combine_sign": "",
           "components": "", "reason_class": "", "reason": e["reason"]}
    if dec in ("concept", "combined"):
        row["canonical_concept"] = e["concept"]
        if dec == "combined":
            row["components"] = "{" + ",".join(e["components"]) + "}"
    elif dec == "component":
        row["parent_concept"] = e["concept"]
        row["combine_sign"] = {"+": "1", "+1": "1", "1": "1", "-": "-1", "-1": "-1"}[sign]
    elif dec == "excluded":
        row["reason_class"] = e["reason_class"] or ("company_exclude" if e["company"] is not None else "tag_exclude")
    return row


def relabel_ci(rows: list[tuple]) -> list[tuple]:
    """Rows are appearance tuples (filing id at [5], stmt at [3]). A filing with CI lines but no IS lines
    (e.g. CB 10-Qs 2014-2017) has its CI report as the income statement: its CI rows become IS so IS entries apply."""
    has_is = {r[5] for r in rows if r[3] == "IS"}
    return [(*r[:3], "IS", *r[4:]) if r[3] == "CI" and r[5] not in has_is else r for r in rows]


def build_eras(appear: dict[date, object], annual_periods: list[date]) -> list[tuple[date, date | None, object]]:
    """appear: period -> payload. Returns [(era_from, era_to, payload of the era's last filing)].
    Eras split only where the tag is absent from an annual (10-K) filing strictly between two appearances
    (it left and returned). The last era is open (era_to None). Only periods >= FLOOR count."""
    periods = sorted(p for p in appear if p >= FLOOR)
    if not periods:
        return []
    annual = sorted(set(annual_periods))
    spans: list[tuple[date, date]] = []
    start = prev = periods[0]
    for p in periods[1:]:
        if any(prev < k < p and k not in appear for k in annual):
            spans.append((start, prev))
            start = p
        prev = p
    spans.append((start, prev))
    return [(a, None if i == len(spans) - 1 else b, appear[b]) for i, (a, b) in enumerate(spans)]


# ---------------------------------------------------------------- DB helpers

def connect():
    import psycopg
    url = os.environ.get("DATABASE_URL")
    if not url:
        for line in (REPO / "pipeline/.env").read_text().splitlines():
            if line.startswith("DATABASE_URL="):
                url = line.split("=", 1)[1].strip().strip("\"'")
    conn = psycopg.connect(url, autocommit=True)
    conn.execute("set statement_timeout='120s'")
    return conn


# ---------------------------------------------------------------- seed

APPEAR_SQL = """
with fl as (
    select l.*, lag(l.plabel) over w as prev_label, lead(l.plabel) over w as next_label
      from fsn.line l join fsn.filing f2 on f2.id = l.filing_id
     where f2.company_id = any(%s) and f2.period >= %s
    window w as (partition by l.filing_id, l.report order by l.line)),
nd as (select distinct v.filing_id, v.tag_id from fsn.value v
        where v.dim_id = 0 and v.filing_id in (select id from fsn.filing where company_id = any(%s) and period >= %s))
select distinct on (f.company_id, split_part(t.version, '/', 1), t.custom, t.tag, l.stmt, f.id)
       f.company_id, case when t.custom then 'custom' else split_part(t.version, '/', 1) end as taxonomy,
       t.tag, l.stmt, t.abstract, f.id, f.accession, f.period, f.form, f.amendment, f.fy, f.accepted,
       l.report, l.line, l.plabel, t.id as tag_id, (nd.tag_id is not null) as nondim, l.prev_label, l.next_label
  from fl l
  join fsn.filing f on f.id = l.filing_id
  join fsn.tag t on t.id = l.tag_id
  left join nd on nd.filing_id = f.id and nd.tag_id = t.id
 where l.stmt = any(%s)
 order by f.company_id, split_part(t.version, '/', 1), t.custom, t.tag, l.stmt, f.id, l.report, l.line
"""

PARENT_SQL = """
select a.filing_id, a.child_tag_id, min(p.tag)
  from fsn.calc_arc a join fsn.tag p on p.id = a.parent_tag_id
 where (a.filing_id, a.child_tag_id) in (select * from unnest(%s::bigint[], %s::bigint[]))
 group by 1, 2
"""

TEMPLATE_SQL = """
select company_id, template from analytics.company_data_point_template t
 where company_id = any(%s)
   and effective_from = (select max(effective_from) from analytics.company_data_point_template x
                          where x.company_id = t.company_id)
 group by 1, 2
"""

CATEGORIES = {
    "total_debt": r"Debt|Borrowings|NotesPayable|LineOfCredit|ConvertibleNotes|SeniorNotes|LoansPayable|CommercialPaper",
    "depreciation_and_amortization": r"Depreciation|Amortization",
    "total_liabilities": r"Liabilit",
    "interest": r"Interest",
    "dividends_paid": r"Dividend",
    "current_assets_liabilities": r"Current",
}


def load_sources(patterns: list[str]) -> tuple[list[dict], list[str]]:
    entries, files = [], sorted({p for g in patterns for p in glob.glob(g)})
    for path in files:
        with open(path, newline="") as f:
            entries += parse_source(Path(path).name, list(csv.DictReader(f)))
    return entries, [Path(p).name for p in files]


def seed_company_rows(cid, cik, rows, templates, index, valid_concepts, conn, stats):
    """rows: appearance tuples of one company. Returns (csv rows, key info)."""
    rows = relabel_ci(rows)  # amendments without any IS/BS/CF/CI line have no rows at all, so they never count
    annual = [r[7] for r in rows if r[8] == "10-K" and not r[9]]
    groups: dict[tuple, dict[date, tuple]] = defaultdict(dict)
    fy23: dict[tuple, bool] = defaultdict(bool)
    for r in rows:
        key = (r[1], r[2], r[3])
        if r[10] is not None and r[10] >= 2023:
            fy23[key] = True
        prev = groups[key].get(r[7])
        if prev is None or (r[11], r[5]) > (prev[11], prev[5]):  # latest accepted filing of the period
            groups[key][r[7]] = r
    out, keyinfo, need = [], [], []
    results = expand_company(cid, templates, groups, annual, index)
    for key, res in results.items():
        stats["overrides"] += res["override"]
        stats["review_keys"] += res["review"]
        for e in res["needs_detail"]:
            stats["needs_detail"][(e["source"], e["tag"], "/".join(e["home_stmts"]), e["decision"], e["concept"],
                                   e["detail_note"] or missing_detail(e) or "decision not loadable on a tagged row")].add(cid)
        good = []
        for e, a, b, rr in res["rows"]:
            if valid_concepts is not None and e["decision"] != "excluded" and e["concept"] and \
                    e["concept"] not in valid_concepts:
                stats["unknown_concept"][(e["source"], e["concept"])].add(cid)
                continue
            good.append((e, a, b, rr))
        keyinfo.append((key, fy23[key], bool(good)))
        for e, a, b, rr in good:
            need.append((rr[5], rr[15]))
            out.append((key, e, a, b, rr))
    parents = {}
    if need:
        fids, tids = zip(*set(need))
        for fid, tid, ptag in conn.execute(PARENT_SQL, (list(fids), list(tids))).fetchall():
            parents[(fid, tid)] = ptag
    csv_rows = []
    for (tx, tag, stmt), e, a, b, rr in out:
        row = {
            "company_id": cid, "cik": cik, "taxonomy": tx, "tag": tag, "stmt": stmt,
            "era_from": a.isoformat(), "era_to": b.isoformat() if b else "", "evidence_adsh": rr[6],
            "evidence_report": rr[12], "evidence_line": rr[13], "evidence_plabel": rr[14] or "",
            "evidence_cal_parent": parents.get((rr[5], rr[15]), ""), "decided_by": e["source"],
            "rule_id": e["rule_id"],
        }
        row.update(library_row(e))
        if e["kind"] == "condition":
            row["reason_class"] = "filing_condition"
        csv_rows.append(row)
    return csv_rows, keyinfo


def cmd_seed(args) -> None:
    entries, files = load_sources(args.decisions or DEFAULT_GLOBS)
    attach_conditions(entries, load_conditions())
    index = build_index(entries)
    free_exc = sorted({(e["source"], e["tag"]) for e in entries if e["exceptions_text"]})
    with open(COHORT_CSV, newline="") as f:
        cohort = {int(r["company_id"]): r["cik"] for r in csv.DictReader(f)}
    ids = sorted(cohort)
    conn = connect()
    valid = {r[0] for r in conn.execute("select name from analytics.canonical_concept").fetchall()}
    valid |= {v.removesuffix("_resolved") for v in valid}
    out_path = Path(args.out)
    stats = {"overrides": 0, "review_keys": 0, "needs_detail": defaultdict(set), "unknown_concept": defaultdict(set)}
    by_decision: dict[str, int] = defaultdict(int)
    by_source: dict[str, int] = defaultdict(int)
    per_company, undecided = {}, defaultdict(int)
    n_rows = 0
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, COLUMNS)
        w.writeheader()
        for i in range(0, len(ids), args.batch):
            batch = ids[i:i + args.batch]
            tmpl: dict[int, set[str]] = defaultdict(set)
            for cid, t in conn.execute(TEMPLATE_SQL, (batch,)).fetchall():
                tmpl[cid].add(t)
            by_co: dict[int, list] = defaultdict(list)
            for r in conn.execute(APPEAR_SQL, (batch, FLOOR, batch, FLOOR, list(SEED_STMTS))).fetchall():
                by_co[r[0]].append(r)
            for cid, rows in by_co.items():
                csv_rows, keyinfo = seed_company_rows(cid, cohort[cid], rows, tmpl[cid], index, valid, conn, stats)
                w.writerows(csv_rows)
                n_rows += len(csv_rows)
                for r in csv_rows:
                    by_decision[r["decision"]] += 1
                    by_source[r["decided_by"]] += 1
                tot = dec = 0
                for key, is23, decided in keyinfo:
                    if not is23:
                        continue
                    tot += 1
                    if decided:
                        dec += 1
                    else:
                        undecided[key] += 1
                per_company[cid] = {"cik": cohort[cid], "fy2023_statement_tags": tot, "decided": dec,
                                    "undecided": tot - dec}
            print(f"batch {i // args.batch + 1}/{-(-len(ids) // args.batch)} rows so far {n_rows}", file=sys.stderr)
    # ranks_1_50 rows on statements the FSN query does not expand (EQ, CP, UN): Ritwik's decided rows pass through
    passthrough = 0
    with open(out_path, "a", newline="") as f:
        w = csv.DictWriter(f, COLUMNS, extrasaction="ignore")
        for e in entries:
            if (e["raw"] is not None and e["home_stmts"][0] not in SEED_STMTS and e["company"] in cohort
                    and e["decision"] in ("concept", "excluded") and (e["concept"] or e["decision"] == "excluded")):
                row = dict(e["raw"])
                row["decided_by"], row["rule_id"] = e["source"], RULE_COMPANY
                w.writerow(row)
                passthrough += 1
                by_decision[e["decision"]] += 1
                n_rows += 1
    # concept-level company rows (not company_tag_map rows)
    cl = [e for e in entries if e["kind"] == "company_concept"]
    with open(out_path.with_suffix(".concept_level.csv"), "w", newline="") as f:
        cw = csv.writer(f)
        cw.writerow(["company_id", "stmt", "decision", "canonical_concept", "reason", "era_from", "era_to", "decided_by"])
        for e in cl:
            cw.writerow([e["company"], "/".join(e["home_stmts"]), e["decision"], e["concept"], e["reason"],
                         e["era"][0] or "", e["era"][1] or "", e["source"]])
    with open(out_path.with_suffix(".needs_detail.csv"), "w", newline="") as f:
        nw = csv.writer(f)
        nw.writerow(["source", "tag", "stmt", "decision", "concept", "missing", "companies_affected"])
        for k, cs in sorted(stats["needs_detail"].items(), key=lambda kv: -len(kv[1])):
            nw.writerow([*k, len(cs)])
    ranked = sorted(undecided.items(), key=lambda kv: -kv[1])
    total = sum(c["fy2023_statement_tags"] for c in per_company.values())
    dec_total = sum(c["decided"] for c in per_company.values())
    complete = sum(1 for c in per_company.values() if c["fy2023_statement_tags"] and c["undecided"] == 0)
    summary = {
        "source_files": files, "entries": len(entries), "entries_with_free_text_exceptions_not_evaluated": len(free_exc), "concept_level_company_rows": len(cl),
        "companies_in_cohort": len(ids), "companies_with_fsn_rows": len(per_company), "csv_rows": n_rows,
        "rows_by_decision": dict(by_decision), "passthrough_rows_eq_cp_un": passthrough, "rows_by_source": dict(by_source),
        "keys_where_company_row_overrode_tag_row": stats["overrides"],
        "keys_blocked_or_left_by_review": stats["review_keys"],
        "needs_detail_entries": len(stats["needs_detail"]),
        "unknown_concept": {f"{k[0]}|{k[1]}": len(v) for k, v in stats["unknown_concept"].items()},
        "pairs_fy2023_company_taxonomy_tag_stmt": total, "pairs_decided": dec_total,
        "pairs_undecided": total - dec_total,
        "companies_with_every_fy2023_is_bs_cf_tag_decided": complete,
        "top_undecided": [{"taxonomy": k[0], "tag": k[1], "stmt": k[2], "companies": n} for k, n in ranked[:60]],
        "undecided_by_group": {
            g: [{"taxonomy": k[0], "tag": k[1], "stmt": k[2], "companies": n}
                for k, n in ranked if re.search(rx, k[1])][:25] for g, rx in CATEGORIES.items()},
        "per_company": per_company,
    }
    out_path.with_suffix(".summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps({k: v for k, v in summary.items() if k not in ("per_company", "undecided_by_group")},
                     indent=1, default=str))
    for g, lst in summary["undecided_by_group"].items():
        print(g, [(x["tag"], x["stmt"], x["companies"]) for x in lst[:10]])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("out", help="path of the CSV to write")
    ap.add_argument("--decisions", action="append", help="glob of decision CSVs (repeatable); default: the repo dirs")
    ap.add_argument("--batch", type=int, default=10, help="companies per query")
    cmd_seed(ap.parse_args())


if __name__ == "__main__":
    main()
