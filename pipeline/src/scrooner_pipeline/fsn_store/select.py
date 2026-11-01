"""Value selection and quarter derivation over the FSN store (design §4, FSN-STORE-DESIGN-2026-11-01).

For one company and one canonical concept, every key (ddate, qtrs) gets one cell:

* **Candidates** are prints of a line mapped to the concept (fsn.line_map status 'mapped'), in a
  column on the statement face. A column (filing, stmt, ddate, qtrs) is on the face when the
  statement's anchor total has a non-dimensional value for it in the same filing AND the column
  length belongs to the form (a 10-K face is annual or instant; its quarterly note columns are
  not face columns even though the anchor is printed there too: the GE double-context class).
* **Winner** = the print of the latest `accepted` filing. Two different values for the key in the
  winning filing is a defect. If the winner's column fails any fsn.filing_check the cell is a
  blank `latest_copy_fails_identity`; an older vintage is never used instead.
* **Quarter flows without a printed 3-month face column**, in order:
  (a) a 3-month value printed in the same accession as the winning FY/YTD (quarterly note),
      only if it does not duplicate a member (dimensional) value of that tag and period, and
      the filing's note quarters, when all four are printed, sum to the winning FY;
  (b) YTD_n − YTD_(n−1) when SAME_BASIS holds for the pair of filings, the winning pair first,
      then other printed pairs (the restated pair of the N+1 filings).
* SAME_BASIS(A, B) with accepted(A) <= accepted(B): A = B, or no break for the concept lies in
  (accepted(A), accepted(B)] and B re-prints an earlier period of the concept (the witness).
  A filing is a break when any period it prints for the concept differs beyond rounding from
  the latest earlier print of that period.
* EPS and every per-share or share concept is never derived; instants are never derived.
  Revenue-like concepts carry the residual guard: derived Q >= 0 and |Q| <= |YTD_n|.

Value, accession and source_value_ids of a cell always come from the same fsn.value rows.
"""

from __future__ import annotations

import calendar
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable

import psycopg

from scrooner_pipeline.fsn_store.checks import tol_of

RULE_PRINTED = "fsn.select_printed@1"
RULE_NOTE_Q = "fsn.select_note_quarter@1"
RULE_YTD_DIFF = "fsn.select_ytd_difference@1"
RULE_BLANK = "fsn.select_blank@1"

# the statement's anchor total: a column is on the face only where one of these is printed
ANCHOR_TAGS = {
    "IS": (
        "NetIncomeLoss",
        "ProfitLoss",
        "NetIncomeLossAvailableToCommonStockholdersBasic",
        "IncomeLossFromContinuingOperations",
    ),
    "BS": ("Assets", "LiabilitiesAndStockholdersEquity"),
    "CF": (
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    ),
}
# column lengths (qtrs) a form prints on its statement face
FACE_QTRS = {"10-K": {0, 4}, "10-K/A": {0, 4}, "10-Q": {0, 1, 2, 3}, "10-Q/A": {0, 1, 2, 3}}

# blank reason -> (defect_class, owner) of the cell contract
REASONS = {
    "latest_copy_fails_identity": ("identity", "data_engineer_l2"),
    "conflicting_values_in_filing": ("filer_error", "tag_mapper"),
    "mixed_vintage_inputs": ("period", "period_engineer"),
    "no_basis_witness": ("period", "period_engineer"),
    "no_prior_quarter_end": ("period", "period_engineer"),
    "derived_quarter_fails_residual_guard": ("period", "period_engineer"),
}
REASON_TEXT = {
    "latest_copy_fails_identity": "The latest filing that prints this value fails an arithmetic check of its statement column; an older copy is not used instead.",
    "conflicting_values_in_filing": "The filing prints two different values for this line and period.",
    "mixed_vintage_inputs": "The quarter would subtract year-to-date values from filings with a restatement between them.",
    "no_basis_witness": "The later filing re-prints no earlier period of this line, so the two year-to-date values cannot be shown to be on one basis.",
    "no_prior_quarter_end": "The prior year-to-date value needed to compute this quarter is not printed.",
    "derived_quarter_fails_residual_guard": "The computed quarter is negative or larger than its year-to-date total.",
}


@dataclass(frozen=True)
class Filing:
    id: int
    accession: str
    accepted: datetime
    form: str
    period: date | None
    fy: int | None
    fp: str | None


@dataclass(frozen=True)
class Print:
    """One non-dimensional fsn.value of a line mapped to the concept in its filing."""

    value_id: int
    filing_id: int
    tag: str
    ddate: date
    qtrs: int
    uom: str
    value: Decimal
    dcml: int | None
    stmt: str
    face: bool
    checks_ok: bool = True


@dataclass
class Cell:
    concept: str
    ddate: date
    qtrs: int
    state: str  # value | derived | defect
    value: Decimal | None = None
    filing_id: int | None = None
    tag: str | None = None
    source_value_ids: list[int] = field(default_factory=list)
    rule_id: str = RULE_PRINTED
    reason_code: str | None = None
    derivation: dict[str, Any] | None = None
    input_refs: dict[str, Any] = field(default_factory=dict)

    @property
    def grain(self) -> str:
        return {0: "I", 1: "Q", 4: "FY"}[self.qtrs]


def month_end(d: date, months: int) -> date:
    """The month-end `months` after (or before) the month of d (FSN ddate is month-end rounded)."""
    m = d.year * 12 + d.month - 1 + months
    y, mo = divmod(m, 12)
    return date(y, mo + 1, calendar.monthrange(y, mo + 1)[1])


def _same(a: Print, b: Print) -> bool:
    return abs(a.value - b.value) <= tol_of([a.dcml, b.dcml])


class _Series:
    """The face prints of one concept, by key and by filing, with the break set."""

    def __init__(self, prints: list[Print], filings: dict[int, Filing]):
        self.filings = filings
        self.by_key: dict[tuple[date, int], list[Print]] = defaultdict(list)
        for p in prints:
            if p.face:
                self.by_key[(p.ddate, p.qtrs)].append(p)
        self.order = sorted(
            {p.filing_id for ps in self.by_key.values() for p in ps},
            key=lambda f: (filings[f].accepted, f),
        )
        self.breaks: set[int] = set()
        self.witness: set[int] = set()
        latest: dict[tuple[date, int], Print] = {}
        for fid in self.order:
            mine = {
                k: next(p for p in ps if p.filing_id == fid)
                for k, ps in self.by_key.items()
                if any(p.filing_id == fid for p in ps)
            }
            for k, p in mine.items():
                prev = latest.get(k)
                if prev is not None:
                    self.witness.add(fid)
                    if not _same(prev, p):
                        self.breaks.add(fid)
            latest.update(mine)

    def same_basis(self, a: int, b: int) -> str | None:
        """None when SAME_BASIS(a, b) holds, else the blank reason."""
        if a == b:
            return None
        if (self.filings[a].accepted, a) > (self.filings[b].accepted, b):
            a, b = b, a
        lo, hi = self.filings[a].accepted, self.filings[b].accepted
        if any(lo < self.filings[f].accepted <= hi for f in self.breaks):
            return "mixed_vintage_inputs"
        if b not in self.witness:
            return "no_basis_witness"
        return None

    def latest_first(self, key: tuple[date, int]) -> list[Print]:
        return sorted(
            self.by_key.get(key, []),
            key=lambda p: (self.filings[p.filing_id].accepted, p.filing_id),
            reverse=True,
        )


def select_concept(
    concept: str,
    prints: list[Print],
    filings: dict[int, Filing],
    *,
    members: dict[tuple[int, str, date, int], set[Decimal]] | None = None,
    unit: str = "USD",
    derive: bool = True,
    residual_guard: bool = False,
) -> list[Cell]:
    """Cells of one concept for one company. `prints` are every non-dimensional value of the
    concept's mapped lines (face and note columns); `members` maps (filing_id, tag, ddate, qtrs)
    to the dimensional values of that tag in that filing (the double-context guard)."""
    prints = [p for p in prints if p.uom == unit]
    members = members or {}
    s = _Series(prints, filings)
    cells: dict[tuple[date, int], Cell] = {}
    winners: dict[tuple[date, int], Print] = {}
    held: dict[tuple[date, int], str] = {}  # keys whose latest copy is unusable, with the reason
    for key in sorted(s.by_key):
        ps = s.latest_first(key)
        top = ps[0]
        same_filing = [p for p in ps if p.filing_id == top.filing_id]
        ddate, qtrs = key
        if any(not _same(top, p) for p in same_filing):
            held[key] = "conflicting_values_in_filing"
            if qtrs in (0, 1, 4):
                cells[key] = _blank(
                    concept,
                    key,
                    "conflicting_values_in_filing",
                    top,
                    {"values": sorted({str(p.value) for p in same_filing})},
                )
            continue
        if not all(p.checks_ok for p in same_filing):
            held[key] = "latest_copy_fails_identity"
            if qtrs in (0, 1, 4):
                cells[key] = _blank(concept, key, "latest_copy_fails_identity", top, {})
            continue
        winners[key] = top
        if qtrs in (0, 1, 4):
            cells[key] = Cell(
                concept,
                ddate,
                qtrs,
                "value",
                top.value,
                top.filing_id,
                top.tag,
                [top.value_id],
                RULE_PRINTED,
                input_refs={"copies": len(ps)},
            )
    if derive:
        notes = _note_quarters(prints)
        for (ddate, n), w in sorted(winners.items()):
            if n < 2 or (ddate, 1) in cells:
                continue
            cell = _note_quarter(concept, ddate, n, w, notes, winners, members)
            if cell is None:
                cell = _ytd_difference(concept, ddate, n, w, s, winners, held, residual_guard)
            cells[(ddate, 1)] = cell
    return [cells[k] for k in sorted(cells)]


def _blank(
    concept: str,
    key: tuple[date, int],
    reason: str,
    carrier: Print | None,
    refs: dict[str, Any],
    rule_id: str = RULE_BLANK,
) -> Cell:
    return Cell(
        concept,
        key[0],
        key[1],
        "defect",
        filing_id=carrier.filing_id if carrier else None,
        rule_id=rule_id,
        reason_code=reason,
        input_refs=refs,
    )


def _note_quarters(prints: list[Print]) -> dict[tuple[int, str, date], Print]:
    """Non-face 3-month prints by (filing, tag, ddate): the quarterly-data note of a filing."""
    return {
        (p.filing_id, p.tag, p.ddate): p
        for p in prints
        if p.qtrs == 1 and not p.face
    }


def _note_quarter(
    concept: str,
    ddate: date,
    n: int,
    w: Print,
    notes: dict[tuple[int, str, date], Print],
    winners: dict[tuple[date, int], Print],
    members: dict[tuple[int, str, date, int], set[Decimal]],
) -> Cell | None:
    """Rule (a): the 3-month value the winning FY/YTD filing prints in a note, guarded."""
    q = notes.get((w.filing_id, w.tag, ddate))
    if q is None:
        return None
    if q.value in members.get((q.filing_id, q.tag, ddate, 1), set()):
        return None  # an undimensioned copy of a member's figure (GE double context)
    if n == 4:
        four = [notes.get((w.filing_id, w.tag, month_end(ddate, -3 * i))) for i in range(4)]
        if all(four):
            total = sum((p.value for p in four), Decimal(0))  # type: ignore[union-attr]
            tol = tol_of([w.dcml, *(p.dcml for p in four)])  # type: ignore[union-attr]
            if abs(total - w.value) > tol:
                return None  # the note quarters miss the year: not this line's quarters
    return Cell(
        concept,
        ddate,
        1,
        "value",
        q.value,
        q.filing_id,
        q.tag,
        [q.value_id],
        RULE_NOTE_Q,
        input_refs={"source": "note", "ytd_qtrs": n, "ytd_value_id": w.value_id},
    )


def _ytd_difference(
    concept: str,
    ddate: date,
    n: int,
    w: Print,
    s: _Series,
    winners: dict[tuple[date, int], Print],
    held: dict[tuple[date, int], str],
    residual_guard: bool,
) -> Cell:
    """Rule (b): YTD_n − YTD_(n−1) on SAME_BASIS, the winning pair first, then other printed pairs."""
    prev_key = (month_end(ddate, -3), n - 1)
    key = (ddate, 1)
    prev = winners.get(prev_key)
    if prev is None:
        return _blank(
            concept, key, held.get(prev_key, "no_prior_quarter_end"), w, {"needs": str(prev_key)}
        )
    first = s.same_basis(prev.filing_id, w.filing_id)
    pair = (prev, w) if first is None else None
    if pair is None:
        for b in s.latest_first((ddate, n)):
            for a in s.latest_first(prev_key):
                if a.checks_ok and b.checks_ok and s.same_basis(a.filing_id, b.filing_id) is None:
                    pair = (a, b)
                    break
            if pair:
                break
    if pair is None:
        return _blank(
            concept,
            key,
            first or "mixed_vintage_inputs",
            w,
            {
                "inputs": [s.filings[prev.filing_id].accession, s.filings[w.filing_id].accession],
                "breaks": sorted(s.filings[f].accession for f in s.breaks),
            },
        )
    a, b = pair
    value = b.value - a.value
    if residual_guard and (value < 0 or abs(value) > abs(b.value)):
        return _blank(
            concept,
            key,
            "derived_quarter_fails_residual_guard",
            b,
            {"value": str(value), "ytd": str(b.value)},
        )
    return Cell(
        concept,
        ddate,
        1,
        "derived",
        value,
        b.filing_id,
        None,
        [b.value_id, a.value_id],
        RULE_YTD_DIFF,
        derivation={
            "formula": f"YTD{n} - YTD{n - 1}",
            "input_values": [str(b.value), str(a.value)],
            "input_accessions": [s.filings[b.filing_id].accession, s.filings[a.filing_id].accession],
            "policy": "same_basis",
            "winning_pair": pair == (prev, w),
        },
    )


# --- fiscal labels and cell rows ------------------------------------------------------------


def fiscal_label(ddate: date, qtrs: int, filings: Iterable[Filing]) -> tuple[int | None, str | None]:
    """(fiscal_year, fiscal_period) of a key from the sub row of the filing whose own period is
    that date, else the same quarter one to three years later (comparative columns)."""
    by_period: dict[date, Filing] = {}
    for f in sorted(filings, key=lambda f: f.accepted):
        if f.period is not None:
            by_period.setdefault(f.period, f)
    for back in range(4):
        f = by_period.get(month_end(ddate, 12 * back))
        if f is None or f.fy is None:
            continue
        fy = f.fy - back
        if qtrs == 4:
            return fy, "FY"
        if qtrs == 1:
            return fy, (f.fp if f.fp in ("Q1", "Q2", "Q3") else "Q4")
        return fy, (f.fp if f.fp in ("Q1", "Q2", "Q3") else "FY")
    return None, None


def to_row(
    cell: Cell, company_id: int, filings: dict[int, Filing], *, unit: str = "USD"
) -> dict[str, Any]:
    """The cell as a CELL-FORMAT v1.1 row, bound by fiscal label (the loader binds within 10 days)."""
    fy, fp = fiscal_label(cell.ddate, cell.qtrs, filings.values())
    f = filings.get(cell.filing_id) if cell.filing_id else None
    row: dict[str, Any] = {
        "company_id": company_id,
        "data_point_name": cell.concept,
        "period_grain": cell.grain,
        "period_start": None,
        "period_end": None,
        "fiscal_year": fy,
        "fiscal_period": fp,
        "period_type": "instant" if cell.qtrs == 0 else "duration",
        "fsn_end": cell.ddate.isoformat(),
        "basis": "latest",
        "state": cell.state,
        "value": str(cell.value) if cell.value is not None else None,
        "unit": unit if cell.value is not None else None,
        "source_fact_ids": [],
        "source_value_ids": cell.source_value_ids,
        "accession": f.accession if f else None,
        "tag": cell.tag,
        "derivation": cell.derivation,
        "rule_id": cell.rule_id,
        "evidence_level": "DATA-INFERRED",
        "input_refs": cell.input_refs,
    }
    if cell.state == "defect":
        cls, owner = REASONS[cell.reason_code or ""]
        row.update(
            reason_code=cell.reason_code,
            reason_text=REASON_TEXT[cell.reason_code or ""],
            defect_class=cls,
            owner=owner,
            root_cause_class=cls,
        )
    return row


# --- the database side ----------------------------------------------------------------------


def load_company(conn: psycopg.Connection, company_id: int) -> dict[str, Any]:
    """Filings, per-concept prints and member values of one stored company (five indexed reads)."""
    with conn.cursor() as cur:
        cur.execute(
            "select id, accession, accepted, form, period, fy, fp from fsn.filing where company_id = %s",
            (company_id,),
        )
        filings = {r[0]: Filing(*r) for r in cur.fetchall()}
        cur.execute(
            """
            select lm.filing_id, l.stmt, l.tag_id, t.tag, cc.name
            from fsn.line_map lm
            join fsn.line l using (filing_id, report, line)
            join fsn.tag t on t.id = l.tag_id
            join analytics.canonical_concept cc on cc.id = lm.canonical_concept_id
            join fsn.filing f on f.id = lm.filing_id
            where f.company_id = %s and lm.status = 'mapped' and not l.inpth
            """,
            (company_id,),
        )
        mapped = cur.fetchall()
        anchors = [t for ts in ANCHOR_TAGS.values() for t in ts]
        cur.execute(
            """
            select distinct v.filing_id, l.stmt, v.ddate, v.qtrs
            from fsn.value v
            join fsn.line l on l.filing_id = v.filing_id and l.tag_id = v.tag_id and not l.inpth
            join fsn.tag t on t.id = v.tag_id and not t.custom
            where v.company_id = %s and v.dim_id = 0 and v.iprx = 0 and v.coreg = ''
              and v.value is not null and t.tag = any(%s)
            """,
            (company_id, anchors),
        )
        anchor_cols = {(f, s, d, q) for f, s, d, q in cur.fetchall() if q in (0, 1, 2, 3, 4)}
        anchor_cols = {
            (f, s, d, q)
            for f, s, d, q in anchor_cols
            if s in ANCHOR_TAGS and _form_prints(filings[f].form, q)
        }
        tag_ids = sorted({r[2] for r in mapped})
        cur.execute(
            """
            select id, filing_id, tag_id, ddate, qtrs, uom, value, dcml, dim_id
            from fsn.value
            where company_id = %s and tag_id = any(%s) and iprx = 0 and coreg = '' and value is not null
            """,
            (company_id, tag_ids),
        )
        values = cur.fetchall()
        cur.execute(
            """
            select distinct fc.filing_id, fc.stmt, fc.ddate, fc.qtrs
            from fsn.filing_check fc join fsn.filing f on f.id = fc.filing_id
            where f.company_id = %s and not fc.ok
            """,
            (company_id,),
        )
        failed = set(cur.fetchall())
    return build(filings, mapped, anchor_cols, values, failed)


def _form_prints(form: str, qtrs: int) -> bool:
    allowed = FACE_QTRS.get(form)
    return allowed is None or qtrs in allowed  # transition reports (10-KT, 10-QT): any length


def build(
    filings: dict[int, Filing],
    mapped: list[tuple[int, str, int, str, str]],
    anchor_cols: set[tuple[int, str, date, int]],
    values: list[tuple],
    failed: set[tuple[int, str, date, int]],
) -> dict[str, Any]:
    """Pure assembly of select_concept inputs (shared by load_company and the fixtures)."""
    lines: dict[tuple[int, int], list[tuple[str, str, str]]] = defaultdict(list)
    for filing_id, stmt, tag_id, tag, concept in mapped:
        lines[(filing_id, tag_id)].append((stmt, tag, concept))
    prints: dict[str, dict[int, Print]] = defaultdict(dict)
    members: dict[tuple[int, str, date, int], set[Decimal]] = defaultdict(set)
    for vid, filing_id, tag_id, ddate, qtrs, uom, value, dcml, dim_id in values:
        for stmt, tag, concept in lines.get((filing_id, tag_id), []):
            if dim_id != 0:
                members[(filing_id, tag, ddate, qtrs)].add(Decimal(value))
                continue
            col = (filing_id, stmt, ddate, qtrs)
            prints[concept].setdefault(
                vid,
                Print(
                    vid,
                    filing_id,
                    tag,
                    ddate,
                    qtrs,
                    uom,
                    Decimal(value),
                    dcml,
                    stmt,
                    col in anchor_cols,
                    col not in failed,
                ),
            )
    return {
        "filings": filings,
        "prints": {c: list(ps.values()) for c, ps in prints.items()},
        "members": dict(members),
    }


NEVER_DERIVED_UNITS = ("USD/shares", "shares", "pure")


def select_company(
    conn: psycopg.Connection,
    company_id: int,
    units: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Every mapped concept of one company as CELL-FORMAT rows. units: concept -> unit (default USD)."""
    data = load_company(conn, company_id)
    units = units or {}
    rows: list[dict[str, Any]] = []
    for concept, prints in sorted(data["prints"].items()):
        unit = units.get(concept, "USD")
        cells = select_concept(
            concept,
            prints,
            data["filings"],
            members=data["members"],
            unit=unit,
            derive=unit not in NEVER_DERIVED_UNITS and "eps" not in concept,
            residual_guard="revenue" in concept,
        )
        rows.extend(to_row(c, company_id, data["filings"], unit=unit) for c in cells)
    return rows
