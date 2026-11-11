"""One filing's own XBRL on EDGAR -> the rows SEC's Financial Statement and Notes (FSN) set would carry.

Design: data-team/strategy/team/FSN-NIGHTLY-INCREMENTAL-DESIGN-2026-11-09.md. The FSN sets are built by
SEC from the same "as filed" XBRL, weeks after the filing; this module builds the same seven tables
(sub, num, pre, cal, ren, tag, dim) for one accession the night it is filed, so the hybrid build can
load and select it the same way (fsn_store.load / select). It reads, it never repairs: a value is the
instance's own value, rounded to 4 decimals exactly as the FSN readme says.

Inputs (one EDGAR filing directory; sec.gov only, fetched by fsn_store.edgar_fetch):
- the extracted instance `*_htm.xml` (inline filings) or the plain instance (`*.xml`);
- the filing's own schema(s) `*.xsd` with any embedded linkbases, and the separate
  `*_pre.xml` / `*_cal.xml` / `*_lab.xml` when present;
- `FilingSummary.xml` (the renderer's report list: R numbers, menu category, short/long names);
- `MetaLinks.json` (the renderer's element dictionary: data type, balance, period type and every
  label role, standard taxonomy labels included).

Rules (FSN readme 2026-11, `notes-metadata.json`, and calibration against the 2026m10 set; the
equivalence test is tests/test_fsn_xbrl_equivalence.py):
- num: one row per numeric fact (nil included). ddate = end date rounded to the nearest month end,
  datp = ddate - end date in days, qtrs = round(duration days / 91.25) (0 for an instant),
  durp = (qtrs * 91.25 - duration days) / 91.25. uom: the measure's local name; a ratio unit is
  numerator/denominator, except a per-share unit, which is the numerator. dimh = 0x + md5(segments),
  0x00000000 when there is no dimension. segments: '{axis}={member};' sorted by axis, axis without
  a leading 'Statement' and a trailing 'Axis', member without a trailing 'Member' or 'Domain';
  LegalEntityAxis is taken out into coreg. iprx numbers facts that share every key column: 0 for
  the highest decimals, then the closest end date to the month end, then the closest duration.
  dcml: the decimals attribute, INF = 32767, absent = -32768. version: '<taxonomy>/<year>' for a
  standard tag, the accession for a filer's own tag.
- pre: the statements (menu category Statements) and the cover page; lines in depth-first order of
  the presentation tree, the root itself not numbered; plabel = the preferred label role's text.
  stmt: one report per (statement type, parenthetical): the first of each type by report order wins,
  later ones are UN; a parenthetical report takes the type of the statement before it; a lone
  comprehensive-income statement with no income statement is the IS.
- cal: one group per calculation extended link (document order), arcs numbered in document order
  within the group; negative = the arc weight.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

XBRLI = "http://www.xbrl.org/2003/instance"
XBRLDI = "http://xbrl.org/2006/xbrldi"
LINK = "http://www.xbrl.org/2003/linkbase"
XLINK = "http://www.w3.org/1999/xlink"
XSD = "http://www.w3.org/2001/XMLSchema"
XSI_NIL = "{http://www.w3.org/2001/XMLSchema-instance}nil"
NO_DIM = "0x00000000"
QTR_DAYS = Decimal("91.25")
DCML_INF = 32767
DCML_NONE = -32768
NEGATING_PREFIX = "negated"
MENUCAT = {
    "Cover": "C",
    "Statements": "S",
    "Notes": "N",
    "Policies": "P",
    "Tables": "T",
    "Details": "D",
    "Other": "O",
    "Uncategorized": "U",
}
# column order of each table, as the SEC FSN files carry them (the loader reads them by name)
COLUMNS: dict[str, tuple[str, ...]] = {
    "sub": (
        "fsn_set",
        "adsh",
        "cik",
        "name",
        "sic",
        "countryba",
        "stprba",
        "cityba",
        "zipba",
        "bas1",
        "bas2",
        "baph",
        "countryma",
        "stprma",
        "cityma",
        "zipma",
        "mas1",
        "mas2",
        "countryinc",
        "stprinc",
        "ein",
        "former",
        "changed",
        "afs",
        "wksi",
        "fye",
        "form",
        "period",
        "fy",
        "fp",
        "filed",
        "accepted",
        "prevrpt",
        "detail",
        "instance",
        "nciks",
        "aciks",
        "pubfloatusd",
        "floatdate",
        "floataxis",
        "floatmems",
    ),
    "num": (
        "adsh",
        "tag",
        "version",
        "ddate",
        "qtrs",
        "uom",
        "dimh",
        "iprx",
        "value",
        "footnote",
        "footlen",
        "dimn",
        "coreg",
        "durp",
        "datp",
        "dcml",
    ),
    "pre": (
        "adsh",
        "report",
        "line",
        "stmt",
        "inpth",
        "tag",
        "version",
        "prole",
        "plabel",
        "negating",
    ),
    "cal": ("adsh", "grp", "arc", "negative", "ptag", "pversion", "ctag", "cversion"),
    "ren": (
        "adsh",
        "report",
        "rfile",
        "menucat",
        "shortname",
        "longname",
        "roleuri",
        "parentroleuri",
        "parentreport",
        "ultparentrpt",
    ),
    "tag": (
        "tag",
        "version",
        "custom",
        "abstract",
        "datatype",
        "iord",
        "crdr",
        "tlabel",
        "doc",
    ),
    "dim": ("dimhash", "segments", "segt"),
}


def shard_filter(
    tables: dict[str, list[dict[str, str]]],
) -> dict[str, list[dict[str, str]]]:
    """The rows fsn_store.shard keeps of one filing: pre of the statements and the cover, every
    non-dimensional num row and the dimensional num rows of a tag on a statement."""
    from scrooner_pipeline.fsn_store.company_dir import STATEMENT_STMTS

    pre = [r for r in tables.get("pre", []) if r.get("stmt") in STATEMENT_STMTS]
    on_stmt = {(r["tag"], r["version"]) for r in pre}
    num = [
        r
        for r in tables.get("num", [])
        if r["dimh"] == NO_DIM or (r["tag"], r["version"]) in on_stmt
    ]
    return {**tables, "pre": pre, "num": num}


class ConversionError(Exception):
    """The filing cannot be converted (no instance, no FilingSummary, unparsable XML)."""


@dataclass
class FilingFiles:
    """The raw files of one EDGAR filing directory, by file name (bytes, untouched)."""

    adsh: str
    files: dict[str, bytes]
    header: dict[str, Any] = field(default_factory=dict)  # from the EDGAR index headers

    def instance_name(self) -> str:
        names = sorted(self.files)
        inline = [n for n in names if n.endswith("_htm.xml")]
        if inline:
            return inline[0]
        plain = [
            n
            for n in names
            if n.endswith(".xml")
            and n != "FilingSummary.xml"
            and not re.search(r"_(pre|cal|lab|def|ref)\.xml$", n)
        ]
        if not plain:
            raise ConversionError(f"{self.adsh}: no XBRL instance")
        return plain[0]


# ---------------------------------------------------------------- small helpers


def month_end(d: date) -> date:
    nxt = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return nxt - timedelta(days=1)


def round_month_end(d: date) -> date:
    """FSN ddate: day 1-15 rounds back to the previous month end, day 16 on to this month end
    (calibrated: 2026-02-15 -> 2026-01-31 although Feb 28 is nearer; 2024-09-16 -> 2024-09-30)."""
    if d.day <= 15:
        return date(d.year, d.month, 1) - timedelta(days=1)
    return month_end(d)


def _date(s: str) -> date:
    return date.fromisoformat(s.strip()[:10])


def version_of(nsuri: str, adsh: str, custom: set[str]) -> str:
    """'http://fasb.org/us-gaap/2026' -> 'us-gaap/2026'; a filer namespace -> the accession."""
    if nsuri in custom:
        return adsh
    parts = [p for p in re.split(r"[/:]+", nsuri) if p]
    if "ifrs-full" in parts:
        year = next((p[:4] for p in parts if re.match(r"\d{4}", p)), "")
        return f"ifrs/{year}"
    if len(parts) >= 2:
        name, ver = parts[-2], parts[-1]
        if re.match(r"\d{4}-\d{2}-\d{2}$", ver):
            ver = ver[:4]
        return f"{name}/{ver}"[:20]
    return nsuri[:20]


def _ci(pair: tuple[str, str]) -> tuple[str, str]:
    """Axes sort case-insensitively (WFC: 'LoansNotInsured...' before 'LoanToValue')."""
    return pair[0].lower(), pair[1].lower()


def segments_of(dims: list[tuple[str, str, bool]]) -> tuple[str, str, int]:
    """(segments, coreg, dimn) of one context. Explicit axes sorted case-insensitively (WFC), then the
    typed ones, which keep their 'Statement' prefix and their raw value (BAC, KO). coreg only when the
    legal entity is the context's one dimension (NEE: FPL alone -> coreg; an entity with another
    axis -> none), and the entity stays in the segments either way."""
    explicit, typed = [], []
    for axis, member, is_typed in dims:
        if is_typed:
            typed.append((axis[:-4] if axis.endswith("Axis") else axis, member))
        else:
            explicit.append((strip_axis(axis), strip_member(member)))
    coreg = (
        strip_member(dims[0][1])
        if len(dims) == 1 and dims[0][0] == "LegalEntityAxis"
        else ""
    )
    segments = "".join(
        f"{a}={m};" for a, m in sorted(explicit, key=_ci) + sorted(typed, key=_ci)
    )
    return segments, coreg, len(dims)


def strip_axis(local: str) -> str:
    if local.startswith("Statement"):
        local = local[len("Statement") :]
    return local[:-4] if local.endswith("Axis") else local


def strip_member(local: str) -> str:
    for suf in ("Member", "Domain"):
        if local.endswith(suf):
            return local[: -len(suf)]
    return local


def fsn_value(text: str | None) -> str:
    """Rounded to 4 decimals, as the FSN readme states ('' for nil)."""
    if text is None or not text.strip():
        return ""
    try:
        d = Decimal(text.strip())
    except InvalidOperation:
        return ""
    return str(d.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def fsn_text(s: str | None) -> str:
    """FSN text columns drop every character outside ASCII (calibrated: 'Stockholders\u2019 equity' is
    'Stockholders equity' in the 2026m10 set; an en dash leaves its two spaces). A text holding a double
    quote is written CSV-quoted ('"' + doubled quotes + '"'), as the SEC files carry it and as
    fsn_store.shard (QUOTE_NONE) passes it on (IBM footnote, AMZN plabel)."""
    t = (s or "").encode("ascii", "ignore").decode()
    if '"' in t:
        t = '"' + t.replace('"', '""') + '"'
    return t


def fsn_shortname(s: str, menucat: str) -> str:
    """A details report '<note> - <table> (Details)' is listed under its note's name in the FSN ren."""
    if menucat in ("D", "T") and " - " in s:
        return s.split(" - ", 1)[0]
    return s


def fsn_float(x: Decimal) -> str:
    """durp / datp as the FSN text shows them: shortest repr of a 4-byte float."""
    import struct

    f = struct.unpack("f", struct.pack("f", float(x)))[0]
    s = f"{f:.8g}"
    if "e" not in s and "." not in s:
        s += ".0"
    return s


# ---------------------------------------------------------------- the instance


@dataclass
class Context:
    start: date | None
    end: date
    dims: list[
        tuple[str, str, bool]
    ]  # (axis local name, member local name or typed value, typed)


def _local(qname: str) -> str:
    return qname.split(":", 1)[-1].strip()


def parse_instance(
    raw: bytes,
) -> tuple[
    dict[str, str], list[ET.Element], dict[str, Context], dict[str, str], ET.Element
]:
    """(prefix->nsuri, fact elements in document order, contexts, unit id -> uom, root)."""
    nsmap: dict[str, str] = {}
    for ev, item in ET.iterparse(io.BytesIO(raw), events=("start-ns",)):
        prefix, uri = item  # type: ignore[misc]
        nsmap.setdefault(prefix, uri)
    root = ET.fromstring(raw)
    contexts: dict[str, Context] = {}
    for c in root.iter(f"{{{XBRLI}}}context"):
        per = c.find(f"{{{XBRLI}}}period")
        if per is None:
            continue
        inst = per.find(f"{{{XBRLI}}}instant")
        st = per.find(f"{{{XBRLI}}}startDate")
        en = per.find(f"{{{XBRLI}}}endDate")
        if inst is not None and inst.text:
            start, end = None, _date(inst.text)
        elif en is not None and en.text and st is not None and st.text:
            start, end = _date(st.text), _date(en.text)
        else:  # 'forever'
            continue
        dims: list[tuple[str, str, bool]] = []
        for holder in (f"{{{XBRLI}}}segment", f"{{{XBRLI}}}scenario"):
            for seg in c.iter(holder):
                for m in seg:
                    if m.tag == f"{{{XBRLDI}}}explicitMember":
                        dims.append(
                            (
                                _local(m.get("dimension", "")),
                                _local(m.text or ""),
                                False,
                            )
                        )
                    elif m.tag == f"{{{XBRLDI}}}typedMember":
                        val = (
                            "".join((ch.text or "").strip() for ch in m)
                            or (m.text or "").strip()
                        )
                        dims.append((_local(m.get("dimension", "")), val, True))
        contexts[c.get("id", "")] = Context(start, end, dims)
    units: dict[str, str] = {}
    for u in root.iter(f"{{{XBRLI}}}unit"):
        div = u.find(f"{{{XBRLI}}}divide")
        if div is not None:
            num = [
                _local(m.text or "")
                for m in div.iter(f"{{{XBRLI}}}unitNumerator")
                for m in m.iter(f"{{{XBRLI}}}measure")
            ]
            den = [
                _local(m.text or "")
                for m in div.iter(f"{{{XBRLI}}}unitDenominator")
                for m in m.iter(f"{{{XBRLI}}}measure")
            ]
            n, d = "*".join(num), "*".join(den)
            units[u.get("id", "")] = n if d.lower() == "shares" else f"{n}/{d}"
        else:
            units[u.get("id", "")] = "*".join(
                _local(m.text or "") for m in u.iter(f"{{{XBRLI}}}measure")
            )
    facts = [el for el in root if el.get("contextRef") and el.get("unitRef")]
    return nsmap, facts, contexts, units, root


def footnotes(root: ET.Element) -> dict[str, str]:
    """fact id -> footnote text (instance footnoteLinks)."""
    out: dict[str, str] = {}
    for fl in root.iter(f"{{{LINK}}}footnoteLink"):
        loc = {
            l.get(f"{{{XLINK}}}label"): (l.get(f"{{{XLINK}}}href") or "").split("#")[-1]
            for l in fl.iter(f"{{{LINK}}}loc")
        }
        notes = {
            n.get(f"{{{XLINK}}}label"): " ".join("".join(n.itertext()).split())
            for n in fl.iter(f"{{{LINK}}}footnote")
        }
        for arc in fl.iter(f"{{{LINK}}}footnoteArc"):
            fid = loc.get(arc.get(f"{{{XLINK}}}from"))
            txt = notes.get(arc.get(f"{{{XLINK}}}to"))
            if fid and txt:
                out[fid] = (
                    (out[fid] + " | " + txt) if fid in out else txt
                )  # IBM: two notes on one value
    return out


# ---------------------------------------------------------------- the DTS (local schemas, linkbases, MetaLinks)


@dataclass
class Element:
    nsuri: str
    local: str


class Dts:
    """What the converter needs from the filing's own schema, linkbases and MetaLinks."""

    def __init__(self, files: FilingFiles, nsmap: dict[str, str]):
        self.custom_ns: set[str] = set()
        self.by_id: dict[str, Element] = {}
        self.local_abstract: dict[tuple[str, str], bool] = {}
        self.local_meta: dict[tuple[str, str], dict[str, str]] = {}
        self.linkbases: list[ET.Element] = []
        for name, raw in sorted(files.files.items()):
            if name.endswith(".xsd"):
                root = ET.fromstring(raw)
                tns = root.get("targetNamespace", "")
                self.custom_ns.add(tns)
                for el in root.iter(f"{{{XSD}}}element"):
                    if el.get("name"):
                        e = Element(tns, el.get("name", ""))
                        if el.get("id"):
                            self.by_id[el.get("id", "")] = e
                        self.local_abstract[(tns, e.local)] = (
                            el.get("abstract") == "true"
                        )
                        self.local_meta[(tns, e.local)] = {
                            "type": el.get("type", ""),
                            "periodType": el.get(f"{{{XBRLI}}}periodType", ""),
                            "balance": el.get(f"{{{XBRLI}}}balance", ""),
                        }
                self.linkbases.extend(root.iter(f"{{{LINK}}}linkbase"))
            elif re.search(r"_(pre|cal|lab)\.xml$", name):
                self.linkbases.append(ET.fromstring(raw))
        self.nsmap = nsmap
        self.meta: dict[tuple[str, str], dict[str, Any]] = {}
        ml = files.files.get("MetaLinks.json")
        if ml:
            inst = json.loads(ml)["instance"]
            for body in inst.values():
                for key, t in body.get("tag", {}).items():
                    k = (t.get("nsuri", ""), t.get("localname", ""))
                    self.meta[k] = t
                    self.by_id.setdefault(key, Element(*k))
        # filer label linkbase: (nsuri, local) -> role -> text
        self.labels: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
        for lb in self.linkbases:
            for ll in lb.iter(f"{{{LINK}}}labelLink"):
                locs = {
                    l.get(f"{{{XLINK}}}label"): self.element(
                        l.get(f"{{{XLINK}}}href", "")
                    )
                    for l in ll.iter(f"{{{LINK}}}loc")
                }
                labs: dict[str, list[tuple[str, str]]] = defaultdict(list)
                for lab in ll.iter(f"{{{LINK}}}label"):
                    labs[lab.get(f"{{{XLINK}}}label", "")].append(
                        (
                            (lab.get(f"{{{XLINK}}}role") or "").rsplit("/", 1)[-1],
                            " ".join("".join(lab.itertext()).split()),
                        )
                    )
                for arc in ll.iter(f"{{{LINK}}}labelArc"):
                    owner = locs.get(arc.get(f"{{{XLINK}}}from", ""))
                    if owner is None:
                        continue
                    for role, text in labs.get(arc.get(f"{{{XLINK}}}to", ""), []):
                        self.labels[(owner.nsuri, owner.local)][role] = text

    def element(self, href: str) -> Element | None:
        frag = href.split("#", 1)[-1]
        if frag in self.by_id:
            return self.by_id[frag]
        if "_" in frag:
            prefix, local = frag.split("_", 1)
            uri = self.nsmap.get(prefix)
            if uri:
                return Element(uri, local)
        return None

    def label(self, e: Element, role: str) -> str | None:
        k = (e.nsuri, e.local)
        mine = self.labels.get(k, {})
        if role in mine:
            return mine[role]
        ml = (
            ((self.meta.get(k) or {}).get("lang") or {})
            .get("en-us", {})
            .get("role", {})
        )
        return ml.get(role)


# ---------------------------------------------------------------- statement classification


PAREN = re.compile(r"parenthetical", re.I)


def statement_kind(shortname: str) -> str:
    t = PAREN.sub("", (shortname or "").lower())
    if "cash flow" in t:
        return "CF"
    if re.search(
        r"balance sheet|financial position|financial condition|statements? of condition|assets and liabilities|net assets(?! available)",
        t,
    ):
        return "BS"
    if re.search(
        r"equity|stockholder|shareholder|deficit|partners|members|changes in capital|statements? of capital",
        t,
    ) and not re.search(
        r"comprehensive (income|loss|earnings)",
        t.split("equity")[0] if "equity" in t else "",
    ):
        return "EQ"
    rest = (
        t.replace("comprehensive income", "")
        .replace("comprehensive earnings", "")
        .replace("comprehensive loss", "")
    )
    if "comprehensive" in t and not re.search(
        r"operations|income statement|statements? of (consolidated )?(income|earnings|loss)|net income|earnings and",
        rest,
    ):
        return "CI"
    if re.search(r"operations|income|earnings|loss|revenue", t):
        return "IS"
    return "UN"


def classify_reports(
    reports: list[tuple[int, str, str, str]],
) -> dict[int, tuple[str, int]]:
    """reports: (report, menucat, shortname, longname) in report order -> {report: (stmt, inpth)}
    for the cover page and the statements (other reports carry no pre rows in the FSN sets)."""
    stm = [
        (rep, short, bool(PAREN.search(f"{short} {long}")))
        for rep, menucat, short, long in reports
        if menucat == "S"
    ]
    kinds = {rep: (None if p else statement_kind(short)) for rep, short, p in stm}
    if "IS" not in kinds.values():
        for rep, k in kinds.items():
            if k == "CI":
                kinds[rep] = "IS"
                break
    # only the first cover report is the CP (MU's 'Audit Information' cover report has no stmt), and only
    # when the filing has statements: a cover-only amendment's cover has no stmt (TECH 10-K/A; 2026m10:
    # 996 of 997 filings with statements have a CP cover, 16 of 16 without have none)
    covers = [rep for rep, menucat, _, _ in reports if menucat == "C"]
    has_statements = any(menucat == "S" for _, menucat, _, _ in reports)
    out: dict[int, tuple[str, int]] = (
        {covers[0]: ("CP", 0)} if covers and has_statements else {}
    )
    used: set[tuple[str, int]] = set()
    prev = "UN"
    for rep, _short, p in stm:
        k = prev if p else (kinds[rep] or "UN")
        inp = 1 if p else 0
        if k != "UN" and (k, inp) in used:
            if p:  # CB: a second parenthetical of a typed statement gets no stmt (no pre rows in FSN);
                continue  # the parenthetical of a UN statement stays UN (AEP's co-registrant pages)
            k = "UN"
        if not p:
            prev = k
        used.add((k, inp))
        out[rep] = (k, inp)
    return out


# ---------------------------------------------------------------- the converter


def _reports(files: FilingFiles) -> list[dict[str, Any]]:
    raw = files.files.get("FilingSummary.xml")
    if not raw:
        raise ConversionError(f"{files.adsh}: no FilingSummary.xml")
    root = ET.fromstring(raw)
    out = []
    for r in root.iter("Report"):
        html = (r.findtext("HtmlFileName") or r.findtext("XmlFileName") or "").strip()
        m = re.match(r"R(\d+)\.(htm|xml)$", html)
        if not m:
            continue
        out.append(
            {
                "report": int(m.group(1)),
                "rfile": "H" if m.group(2) == "htm" else "X",
                "menucat": MENUCAT.get((r.findtext("MenuCategory") or "").strip(), ""),
                "shortname": " ".join((r.findtext("ShortName") or "").split()),
                "longname": " ".join((r.findtext("LongName") or "").split()),
                "roleuri": (r.findtext("Role") or "").strip(),
                "parentroleuri": (r.findtext("ParentRole") or "").strip(),
            }
        )
    out.sort(key=lambda x: x["report"])
    return out


def convert(files: FilingFiles) -> dict[str, list[dict[str, str]]]:
    """The seven FSN tables for one filing, as lists of {column: text} rows (FSN text forms)."""
    adsh = files.adsh
    try:
        nsmap, facts, contexts, units, root = parse_instance(
            files.files[files.instance_name()]
        )
    except ET.ParseError as exc:
        raise ConversionError(f"{adsh}: instance does not parse: {exc}") from exc
    dts = Dts(files, nsmap)
    notes = footnotes(root)
    tags: dict[tuple[str, str], Element] = {}
    dims: dict[str, str] = {NO_DIM: ""}

    def tag_row(e: Element) -> tuple[str, str]:
        v = version_of(e.nsuri, adsh, dts.custom_ns)
        tags.setdefault((e.local, v), e)
        return e.local, v

    # ---- num
    keyed: dict[tuple, list[tuple]] = defaultdict(list)
    for pos, el in enumerate(facts):
        ctx = contexts.get(el.get("contextRef", ""))
        if ctx is None:
            continue
        nsuri, local = el.tag[1:].split("}", 1)
        tag, ver = tag_row(Element(nsuri, local))
        segments, coreg, ndims = segments_of(ctx.dims)
        dimh = "0x" + hashlib.md5(segments.encode()).hexdigest() if segments else NO_DIM
        if segments:
            dims[dimh] = segments
        ddate = round_month_end(ctx.end)
        datp = Decimal((ddate - ctx.end).days)
        if ctx.start is None:
            qtrs, durp = 0, Decimal(0)
        else:
            days = Decimal((ctx.end - ctx.start).days)
            qtrs = int((days / QTR_DAYS).quantize(Decimal(1), rounding=ROUND_HALF_UP))
            durp = (qtrs * QTR_DAYS - days) / QTR_DAYS
        dec = el.get("decimals")
        dcml = (
            DCML_INF
            if dec == "INF"
            else (int(dec) if dec not in (None, "") else DCML_NONE)
        )
        value = "" if el.get(XSI_NIL) == "true" else fsn_value(el.text)
        uom = units.get(el.get("unitRef", ""), "")[:20]
        note = notes.get(el.get("id", ""), "")
        key = (tag, ver, ddate.strftime("%Y%m%d"), str(qtrs), uom, dimh, coreg)
        keyed[key].append(
            (-dcml, abs(datp), abs(durp), pos, value, note, ndims, durp, datp, dcml)
        )
    num_rows: list[dict[str, str]] = []
    for key, cands in keyed.items():
        for iprx, c in enumerate(sorted(cands, key=lambda x: x[:4])):
            tag, ver, dd, q, uom, dimh, coreg = key
            note = fsn_text(c[5])[:512]
            num_rows.append(
                {
                    "adsh": adsh,
                    "tag": tag,
                    "version": ver,
                    "ddate": dd,
                    "qtrs": q,
                    "uom": uom,
                    "dimh": dimh,
                    "iprx": str(iprx),
                    "value": c[4],
                    "footnote": note,
                    "footlen": str(len(c[5].encode())),
                    "dimn": str(c[6]),
                    "coreg": coreg,
                    "durp": fsn_float(c[7]),
                    "datp": fsn_float(c[8]),
                    "dcml": str(c[9]),
                }
            )
    # ---- ren and pre
    reports = _reports(files)
    by_role = {r["roleuri"]: r for r in reports}
    ren_rows = []
    for r in reports:
        parent = by_role.get(r["parentroleuri"]) if r["parentroleuri"] else None
        ult = parent
        seen = set()
        while ult is not None and ult["parentroleuri"] and ult["roleuri"] not in seen:
            seen.add(ult["roleuri"])
            nxt = by_role.get(ult["parentroleuri"])
            if nxt is None:
                break
            ult = nxt
        ren_rows.append(
            {
                "adsh": adsh,
                "report": str(r["report"]),
                "rfile": r["rfile"],
                "menucat": r["menucat"],
                "shortname": fsn_text(
                    " ".join(
                        fsn_shortname(r["shortname"], r["menucat"])
                        .encode("ascii", "ignore")
                        .decode()
                        .split()
                    )
                )[:255],
                "longname": fsn_text(
                    " ".join(r["longname"].encode("ascii", "ignore").decode().split())
                )[:255],
                "roleuri": r["roleuri"][:255],
                "parentroleuri": r["parentroleuri"][:255],
                "parentreport": str(parent["report"]) if parent else "",
                "ultparentrpt": str(ult["report"])
                if ult
                else (str(r["report"]) if r["menucat"] == "N" else ""),
            }
        )
    stmts = classify_reports(
        [(r["report"], r["menucat"], r["shortname"], r["longname"]) for r in reports]
    )
    pres = _presentation(dts)
    used_members = _used_members(root, contexts)
    concrete = {el.tag.split("}", 1)[-1] for el in root if el.get("contextRef")}
    pre_rows = []
    for r in reports:
        if r["report"] not in stmts:
            continue
        stmt, inpth = stmts[r["report"]]
        lines = pres.get(r["roleuri"], [])
        rfile = files.files.get(f"R{r['report']}.htm")
        if rfile is not None:
            lines = _rendered(
                lines, rendered_elements(rfile, dts), used_members, concrete
            )
        for line, (e, prole, _axis, _depth) in enumerate(lines, start=1):
            tag, ver = tag_row(e)
            plabel = dts.label(e, prole) or dts.label(e, "label") or ""
            pre_rows.append(
                {
                    "adsh": adsh,
                    "report": str(r["report"]),
                    "line": str(line),
                    "stmt": stmt,
                    "inpth": str(inpth),
                    "tag": tag,
                    "version": ver,
                    "prole": prole[:50],
                    "plabel": fsn_text(plabel)[:512],
                    "negating": "1" if prole.startswith(NEGATING_PREFIX) else "0",
                }
            )
    # ---- cal
    cal_rows = []
    grp = 0
    for lb in dts.linkbases:
        for cl in lb.iter(f"{{{LINK}}}calculationLink"):
            locs = {
                l.get(f"{{{XLINK}}}label"): dts.element(l.get(f"{{{XLINK}}}href", ""))
                for l in cl.iter(f"{{{LINK}}}loc")
            }
            arcs = [
                a
                for a in cl.iter(f"{{{LINK}}}calculationArc")
                if a.get("use") != "prohibited"
            ]
            if not arcs:
                continue
            grp += 1
            n = 0
            for a in arcs:
                p_el = locs.get(a.get(f"{{{XLINK}}}from", ""))
                c_el = locs.get(a.get(f"{{{XLINK}}}to", ""))
                if p_el is None or c_el is None or c_el.local not in concrete:
                    continue  # CB: FSN carries no arc to a child the filing reports no fact for
                n += 1
                pt, pv = tag_row(p_el)
                ct, cv = tag_row(c_el)
                w = Decimal(a.get("weight") or "1")
                cal_rows.append(
                    {
                        "adsh": adsh,
                        "grp": str(grp),
                        "arc": str(n),
                        "negative": "-1" if w < 0 else "1",
                        "ptag": pt,
                        "pversion": pv,
                        "ctag": ct,
                        "cversion": cv,
                    }
                )
    # ---- tag and dim (iord from the facts when MetaLinks carries no period type)
    period_kind: dict[str, str] = {}
    for el in root:
        ctx = contexts.get(el.get("contextRef", ""))
        if ctx is not None:
            local = el.tag.split("}", 1)[-1]
            period_kind[local] = "I" if ctx.start is None else "D"
    tag_rows = []
    for (t, v), e in sorted(tags.items()):
        meta = dts.meta.get((e.nsuri, e.local)) or {}
        lm = dts.local_meta.get((e.nsuri, e.local)) or {}
        xtype = meta.get("xbrltype") or lm.get("type", "").split(":")[-1]
        abstract = dts.local_abstract.get(
            (e.nsuri, e.local),
            xtype == "domainItemType"
            or e.local.endswith(
                ("Abstract", "Axis", "Domain", "Member", "Table", "LineItems")
            ),
        )
        datatype = (
            {"domain": "member"}.get(x := re.sub(r"ItemType$", "", xtype), x)
            if xtype
            else ""
        )
        crdr = (meta.get("crdr") or lm.get("balance") or "")[:1].upper()
        iord = {"instant": "I", "duration": "D"}.get(
            meta.get("periodType") or lm.get("periodType") or "", ""
        ) or period_kind.get(e.local, "")
        tag_rows.append(
            {
                "tag": t,
                "version": v,
                "custom": "1" if v == adsh else "0",
                "abstract": "1" if abstract else "0",
                "datatype": datatype
                if (not abstract or xtype == "domainItemType")
                else "",
                "iord": "" if abstract else iord,
                "crdr": crdr,
                "tlabel": fsn_text(dts.label(e, "label"))[:512],
                "doc": fsn_text(dts.label(e, "documentation")),
            }
        )
    dim_rows = [
        {"dimhash": h, "segments": s[:1024], "segt": "1" if len(s) > 1024 else "0"}
        for h, s in sorted(dims.items())
    ]
    return {
        "sub": [sub_row(files, root, nsmap, contexts)],
        "num": num_rows,
        "pre": pre_rows,
        "cal": cal_rows,
        "ren": ren_rows,
        "tag": tag_rows,
        "dim": dim_rows,
    }


def rendered_elements(raw: bytes, dts: Dts) -> set[tuple[str, str]]:
    """The elements the renderer shows on one R page: its `defref_<prefix>_<name>` row and axis links."""
    out = set()
    for ref in re.findall(rb"defref_([A-Za-z0-9_.-]+)", raw):
        e = dts.element(ref.decode())
        if e is not None:
            out.add((e.nsuri, e.local))
    return out


def _used_members(
    root: ET.Element, contexts: dict[str, Context]
) -> dict[tuple[str, str], set[str]]:
    """(concept local name, axis local name) -> members used with it in any fact's context (text too)."""
    out: dict[tuple[str, str], set[str]] = defaultdict(set)
    for el in root:
        if not el.get("contextRef"):
            continue
        ctx = contexts.get(el.get("contextRef", ""))
        if ctx is None:
            continue
        local = el.tag.split("}", 1)[-1]
        for axis, member, typed in ctx.dims:
            if not typed:
                out[(local, axis)].add(member)
    return out


def node_kind(e: Element, axis: Element | None = None) -> str:
    """table / axis / lineitems / member (anything under an axis: IBM's exchange members are 'XNYS') / item."""
    n = e.local
    if n.endswith("Axis"):
        return "axis"
    if axis is not None or n.endswith(("Member", "Domain")):
        return "member"
    if n.endswith("Table"):
        return "table"
    if n.endswith("LineItems"):
        return "lineitems"
    return "item"


def _rendered(
    lines: list[tuple[Element, str, Element | None, int]],
    shown: set[tuple[str, str]],
    used: dict[tuple[str, str], set[str]],
    concrete: set[str],
) -> list[tuple[Element, str, Element | None, int]]:
    """Keep what the renderer shows (FSN pre mirrors the R page):
    - a concrete line item only when the R page has its row (COST: an empty 'Commitments and
      contingencies' row the renderer dropped; MSFT kept its);
    - an abstract only when the R page links it or a line under it is kept;
    - a member only when a fact of a line item shown on the page uses it on that axis (WFC);
      an axis and its domain only when one of its members is kept (KO, CB: an unused scenario axis);
    - tables and [Line Items] always."""
    kinds = [node_kind(e, axis) for e, _p, axis, _d in lines]
    items = {
        e.local
        for (e, _p, _a, _d), k in zip(lines, kinds)
        if k == "item" and ((e.nsuri, e.local) in shown or e.local in concrete)
    }
    keep = [False] * len(lines)
    for i, (e, _prole, axis, _d) in enumerate(lines):
        kind = kinds[i]
        if kind == "item":
            # a row on the R page, or a concept with a fact (ACN, CB: a per-share parenthetical value
            # FSN lists though its R page renders it without a row link)
            keep[i] = (e.nsuri, e.local) in shown or e.local in concrete
        elif kind == "member" and axis is not None:
            keep[i] = any(e.local in used.get((it, axis.local), ()) for it in items)
        elif kind == "axis":
            keep[i] = (e.nsuri, e.local) in shown
        elif kind in ("table", "lineitems"):
            keep[i] = True
    # bottom-up: an abstract item, an axis or a domain stays when something under it stays
    for i in range(len(lines) - 1, -1, -1):
        e, _prole, _axis, depth = lines[i]
        kind = kinds[i]
        if keep[i] or kind in ("table", "lineitems"):
            continue
        if kind == "item" and e.local in concrete:
            continue
        j = i + 1
        while j < len(lines) and lines[j][3] > depth:
            if keep[j] and kinds[j] in ("item", "member"):
                keep[i] = True
                break
            j += 1
    # a domain goes with its axis (KO: an equity-components axis the R page links, no member used)
    for i, (e, _prole, axis, depth) in enumerate(lines):
        if kinds[i] == "axis" and keep[i]:
            j = i + 1
            while j < len(lines) and lines[j][3] > depth:
                if lines[j][3] == depth + 1:
                    keep[j] = True
                j += 1
    return [ln for ln, k in zip(lines, keep) if k]


def _presentation(
    dts: Dts,
) -> dict[str, list[tuple[Element, str, Element | None, int]]]:
    """role -> [(element, preferred label role, the axis it sits under, depth)] in depth-first order,
    the root(s) not numbered."""
    out: dict[str, list[tuple[Element, str, Element | None, int]]] = {}
    for lb in dts.linkbases:
        for pl in lb.iter(f"{{{LINK}}}presentationLink"):
            role = pl.get(f"{{{XLINK}}}role", "")
            locs = {
                l.get(f"{{{XLINK}}}label", ""): dts.element(
                    l.get(f"{{{XLINK}}}href", "")
                )
                for l in pl.iter(f"{{{LINK}}}loc")
            }
            kids: dict[str, list[tuple[Decimal, int, str, str]]] = defaultdict(list)
            has_parent: set[str] = set()
            order_seen: list[str] = []
            for i, a in enumerate(pl.iter(f"{{{LINK}}}presentationArc")):
                if a.get("use") == "prohibited":
                    continue
                f, t = a.get(f"{{{XLINK}}}from", ""), a.get(f"{{{XLINK}}}to", "")
                kids[f].append(
                    (
                        Decimal(a.get("order") or "1"),
                        i,
                        t,
                        (a.get("preferredLabel") or "label").rsplit("/", 1)[-1],
                    )
                )
                has_parent.add(t)
                order_seen.extend([f, t])
            roots = []
            for x in order_seen:
                if x not in has_parent and x not in roots:
                    roots.append(x)
            seq: list[tuple[Element, str, Element | None, int]] = []

            def walk(node: str, axis: Element | None, stack: set[str]) -> None:
                for _o, _i, child, prole in sorted(kids.get(node, [])):
                    e = locs.get(child)
                    if e is not None:
                        seq.append((e, prole, axis, len(stack)))
                    under = e if e is not None and e.local.endswith("Axis") else axis
                    if child not in stack:
                        walk(child, under, stack | {child})

            for r in roots:
                walk(r, None, {r})
            out.setdefault(role, []).extend(seq)
    return out


def sub_row(
    files: FilingFiles,
    root: ET.Element,
    nsmap: dict[str, str],
    contexts: dict[str, Context],
) -> dict[str, str]:
    """The sub row from the dei cover facts plus the EDGAR index header (filed, accepted, co-registrants)."""
    dei: dict[str, str] = {}
    for el in root:
        ns, _, local = el.tag[1:].partition("}")
        if "/dei/" in ns and local not in dei and el.text:
            ctx = contexts.get(el.get("contextRef", ""))
            if ctx is not None and not ctx.dims:
                dei[local] = el.text.strip()
    h = files.header
    period = h.get("period") or dei.get("DocumentPeriodEndDate", "")
    try:
        pdate = round_month_end(_date(period)) if period else None
    except ValueError:
        pdate = None
    fye = ""
    m = re.search(r"(\d{2})-(\d{2})$", dei.get("CurrentFiscalYearEndDate") or "")
    if m:  # rounded like every FSN date (MU --09-03 -> 0831, JNJ --01-03 -> 1231); 2000 is a leap year
        try:
            fye = round_month_end(
                date(2000, int(m.group(1)), int(m.group(2)))
            ).strftime("%m%d")
        except ValueError:
            fye = ""
    row = {c: "" for c in COLUMNS["sub"]}
    row.update(
        {
            "fsn_set": h.get("fsn_set", "edgar"),
            "adsh": files.adsh,
            "cik": str(int(h.get("cik") or dei.get("EntityCentralIndexKey") or 0)),
            "name": (h.get("name") or dei.get("EntityRegistrantName") or "").upper()[
                :150
            ],
            "form": h.get("form") or dei.get("DocumentType", ""),
            "period": pdate.strftime("%Y%m%d") if pdate else "",
            "fy": dei.get("DocumentFiscalYearFocus", "")[:4],
            "fp": dei.get("DocumentFiscalPeriodFocus", ""),
            "fye": fye,
            "filed": h.get("filed", ""),
            "accepted": h.get("accepted", ""),
            "prevrpt": "0",
            "detail": "1",
            "instance": files.instance_name(),
            "nciks": str(1 + len(h.get("aciks", []))),
            "aciks": " ".join(str(int(c)) for c in h.get("aciks", [])),
        }
    )
    return row
