"""FSN (Financial Statement and Notes data sets) reader for the proof system.

One quarter of the SEC FSN set is kept in the private bucket `fsn-notes` as
<period>/<period>_{sub,pre,cal,num,...}.tsv.zst (uploaded by
scripts/slot_records/fsn_upload.py): quarterly 2014q1-2025q3, monthly 2025m10 onward
(59 periods as of 2026-10-31; a full local copy may be given as fsn_root).
This module loads ONE quarter for a set of accessions and returns, per
accession, the filing's statement STRUCTURE and VALUES:

  pre  the presented lines: (report, line, stmt, inpth, tag, version, plabel,
       negating) -- stmt BS/IS/CF/CI/EQ, inpth 1 = parenthetical (ignored)
  cal  the filer's own calculation arcs: parent tag -> child tag (negative flag)
  num  face-shaped values: (tag, version, ddate, qtrs, uom, value, dcml) with
       dimn = 0, iprx = 0, no co-registrant -- what FSDS num.txt holds

`dcml` is the XBRL decimals attribute (-6 = reported in millions): the proof
uses it as the filer's own stated precision, which core.fact never kept.

Columns checked against the real 2023q4 files on 2026-10-31:
  sub: adsh cik name ... form period fy fp filed ... instance ...
  pre: adsh report line stmt inpth tag version prole plabel negating
  cal: adsh grp arc negative ptag pversion ctag cversion
  num: adsh tag version ddate qtrs uom dimh iprx value footnote footlen dimn coreg durp datp dcml
"""

from __future__ import annotations

import csv
import io
import os
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

import httpx

csv.field_size_limit(1 << 24)

BUCKET = "fsn-notes"
STATEMENTS = ("BS", "IS", "CF", "CI", "EQ")
STD_PREFIXES = ("us-gaap/", "srt/", "dei/", "ifrs/")


MONTHLY_FROM = (
    2025,
    10,
)  # the SEC set is monthly from 2025-10: periods are named YYYYmMM


def fsn_ddate(d: date) -> date:
    """FSN/FSDS `ddate` is the period end rounded to the nearest month end
    (SEC readme): 2025-09-27 -> 2025-09-30, 2024-01-02 -> 2023-12-31."""
    import calendar

    if d.day <= 15:
        first = d.replace(day=1)
        prev = first.fromordinal(first.toordinal() - 1)
        return prev
    return d.replace(day=calendar.monthrange(d.year, d.month)[1])


def quarter_of(filed: date) -> str:
    """FSN period name for a filing date: 2014q1..2025q3, then 2025m10, 2025m11, ..."""
    if (filed.year, filed.month) >= MONTHLY_FROM:
        return f"{filed.year}m{filed.month:02d}"
    return f"{filed.year}q{(filed.month - 1) // 3 + 1}"


@dataclass(frozen=True)
class PreLine:
    report: int
    line: int
    stmt: str
    tag: str
    version: str
    label: str
    negating: bool

    @property
    def custom(self) -> bool:
        return not self.version.startswith(STD_PREFIXES)


@dataclass(frozen=True)
class NumValue:
    tag: str
    version: str
    ddate: date
    qtrs: int
    uom: str
    value: Decimal
    dcml: int | None


@dataclass
class FilingStructure:
    adsh: str
    cik: str
    form: str
    filed: date | None
    period: date | None
    pre: list[PreLine] = field(default_factory=list)
    calc_children: dict[str, list[tuple[str, bool]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    calc_parents: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    custom_parents: dict[str, set[str]] = field(
        default_factory=lambda: defaultdict(set)
    )  # parents that are filer extensions
    calc_groups: dict[str, dict[str, list[tuple[str, bool]]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list))
    )  # parent -> cal group (role) -> children: one line can be totalled differently per role
    num: dict[tuple[str, date, int], list[NumValue]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def lines_on(self, stmt: str) -> list[PreLine]:
        return sorted(
            (p for p in self.pre if p.stmt == stmt), key=lambda p: (p.report, p.line)
        )

    def value(
        self, tag: str, ddate: date, qtrs: int, uom_prefix: str = "USD"
    ) -> NumValue | None:
        vals = [
            v
            for v in self.num.get((tag, ddate, qtrs), [])
            if v.uom.upper().startswith(uom_prefix)
        ]
        return vals[0] if vals else None


def _zst_rows(path: Path):
    proc = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
    assert proc.stdout is not None
    fh = io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace", newline="")
    yield from csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
    proc.wait()


def _d8(s: str) -> date | None:
    try:
        return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    except (ValueError, TypeError):
        return None


def ensure_quarter(
    fsn_root: Path, period: str, files=("sub", "pre", "cal", "num")
) -> Path:
    """Download the quarter's files from the bucket into fsn_root/<period> if
    absent (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY from the environment)."""
    d = fsn_root / period
    d.mkdir(parents=True, exist_ok=True)
    missing = [f for f in files if not (d / f"{period}_{f}.tsv.zst").exists()]
    if not missing:
        return d
    base = os.environ["SUPABASE_URL"].rstrip("/") + "/storage/v1"
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"Authorization": f"Bearer {key}", "apikey": key}
    for f in missing:
        name = f"{period}_{f}.tsv.zst"
        tmp = d / (name + ".part")
        with httpx.stream(
            "GET",
            f"{base}/object/{BUCKET}/{period}/{name}",
            headers=headers,
            timeout=900,
        ) as resp:
            if resp.status_code != 200:
                # 404 (absent) or 400 (a period the SEC has not published yet): not in the bucket
                raise FileNotFoundError(
                    f"{BUCKET}/{period}/{name}: HTTP {resp.status_code}"
                )
            with tmp.open("wb") as fh:
                for chunk in resp.iter_bytes():
                    fh.write(chunk)
        tmp.rename(d / name)
    return d


def load_quarter(
    fsn_root: Path, period: str, accessions: set[str]
) -> dict[str, FilingStructure]:
    """Structures for the given accessions found in one FSN quarter."""
    d = ensure_quarter(fsn_root, period)
    out: dict[str, FilingStructure] = {}
    for r in _zst_rows(d / f"{period}_sub.tsv.zst"):
        if r["adsh"] in accessions:
            out[r["adsh"]] = FilingStructure(
                r["adsh"],
                r["cik"].zfill(10),
                r["form"],
                _d8(r.get("filed", "")),
                _d8(r.get("period", "")),
            )
    if not out:
        return out
    for r in _zst_rows(d / f"{period}_pre.tsv.zst"):
        s = out.get(r["adsh"])
        if s is None or r["stmt"] not in STATEMENTS or r.get("inpth", "0") != "0":
            continue
        s.pre.append(
            PreLine(
                int(r["report"] or 0),
                int(r["line"] or 0),
                r["stmt"],
                r["tag"],
                r["version"],
                r.get("plabel", ""),
                r.get("negating", "0") == "1",
            )
        )
    for r in _zst_rows(d / f"{period}_cal.tsv.zst"):
        s = out.get(r["adsh"])
        if s is None:
            continue
        # cal.tsv `negative` is the arc weight sign: 1 or -1 (checked on INTC 2023q1, not a 0/1 flag)
        arc = (r["ctag"], r.get("negative", "1").strip() == "-1")
        # the same arc appears once per role (statement, parenthetical, note): keep one
        if arc not in s.calc_children[r["ptag"]]:
            s.calc_children[r["ptag"]].append(arc)
        s.calc_groups[r["ptag"]][r.get("grp", "0")].append(arc)
        s.calc_parents[r["ctag"]].add(r["ptag"])
        if not r.get("pversion", "").startswith(STD_PREFIXES):
            s.custom_parents[r["ctag"]].add(r["ptag"])
    for r in _zst_rows(d / f"{period}_num.tsv.zst"):
        s = out.get(r["adsh"])
        if (
            s is None
            or r.get("dimn", "0") != "0"
            or r.get("iprx", "0") != "0"
            or r.get("coreg")
        ):
            continue
        dd = _d8(r["ddate"])
        if dd is None:
            continue
        try:
            value = Decimal(r["value"])
        except (InvalidOperation, TypeError):
            continue
        dcml = None
        try:
            dcml = int(r["dcml"]) if r.get("dcml") not in (None, "", "INF") else None
        except ValueError:
            dcml = None
        qtrs = int(r["qtrs"] or 0)
        s.num[(r["tag"], dd, qtrs)].append(
            NumValue(r["tag"], r["version"], dd, qtrs, r["uom"], value, dcml)
        )
    return out
