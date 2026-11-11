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
* **Printed year-to-date columns** (CELL-FORMAT v1.2, release approver 2026-11-10): a 6-month or
  9-month face column (qtrs 2/3, 10-Q forms) is a cell of grain TP under the same winner and check
  rules as Q/FY. A TP cell is output only: never derived, and never an input of the quarter
  derivation above, which keeps reading the store's prints.

Value, accession and source_value_ids of a cell always come from the same fsn.value rows.
"""

from __future__ import annotations

import calendar
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.fsn_store.checks import tol_of

RULE_PRINTED = "fsn.select_printed@1"
RULE_NOTE_Q = "fsn.select_note_quarter@1"
RULE_NOTE_VALUE = "fsn.select_note_value@1"

# concepts that may be served from a NOTE fact (no face line) for approved company x concept pairs only
# (template_company_outs_approval: REJECT_NOTE_SOURCED_VALUE), tags in preference order
NOTE_TAGS = {
    "interest_expense_resolved": (
        "InterestExpense",
        "InterestExpenseNonoperating",
        "InterestExpenseOperating",
        "InterestAndDebtExpense",
    ),
}
# Operating income is NEVER note-sourced (Verifier draw 2026-11-03: a non-dimensional OperatingIncomeLoss
# outside the IS face was a segment-profit total at MOG-A, SHW, SWK and a parent measure at EHC)
# Ritwik 2026-11-03 (PENDING_SOLE_DEBT_INTEREST_RULE rows): InterestExpenseDebt counts as gross for a
# filing only when it is the ONLY interest-expense tag that filing prints and, where it has a face
# label, the label reads as interest expense (the PGR/CVX pattern of the interest card)
SOLE_DEBT_TAG = "InterestExpenseDebt"
INTEREST_FAMILY = (
    "InterestExpense",
    "InterestExpenseNonoperating",
    "InterestExpenseOperating",
    "InterestAndDebtExpense",
    "InterestExpenseDebt",
    "InterestExpenseOther",
    "InterestExpenseBorrowings",
    "InterestExpenseDeposits",
    "InterestExpenseRelatedParty",
    "InterestExpenseShortTermBorrowings",
    "InterestExpenseLongTermDebt",
)
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
# column lengths that become cells: instant, quarter, the printed 6/9-month YTD (grain TP, CELL-FORMAT v1.2), year
CELL_QTRS = (0, 1, 2, 3, 4)
# column lengths (qtrs) a form prints on its statement face
FACE_QTRS = {
    "10-K": {0, 4},
    "10-K/A": {0, 4},
    "10-Q": {0, 1, 2, 3},
    "10-Q/A": {0, 1, 2, 3},
}

# blank reason -> (defect_class, owner) of the cell contract
REASONS = {
    "latest_copy_fails_identity": ("identity", "data_engineer_l2"),
    "conflicting_values_in_filing": ("filer_error", "tag_mapper"),
    "mixed_vintage_inputs": ("period", "period_engineer"),
    "no_basis_witness": ("period", "period_engineer"),
    "no_prior_quarter_end": ("period", "period_engineer"),
    "derived_quarter_fails_residual_guard": ("period", "period_engineer"),
    "predecessor_successor_split": ("period", "period_engineer"),
    "balance_sheet_not_filed": ("filer_error", "data_engineer_l2"),
    "note_values_disagree": ("composition", "standardization_lead"),
    "note_value_not_positive": ("evidence_pending", "verifier"),
    "sole_debt_label_not_interest": ("composition", "standardization_lead"),
    "sign_inconsistent": ("filer_error", "verifier"),
    "perimeter_line_unresolved": ("composition", "tag_mapper"),
    "perimeter_partnership_distribution": (
        "definition_pending",
        "standardization_lead",
    ),
    "ytd_input_only_excluded_other_vintage": ("period", "period_engineer"),
    # a pilot gap key written as a blank (founder 2026-11-09: no fallback, every key of a written pair is the
    # hybrid's value or a visible reason): the filing is not in the store / the hybrid could not resolve it
    "filing_not_in_store": ("ingestion", "data_engineer_l1"),
    "hybrid_gap_unresolved": ("unclassified", "triage"),
    # ruling addendum N2: a written cell that cell_proof disagrees with is re-written as this blank
    "cell_proof_disagree": ("identity", "verifier"),
}
# hybrid_gap_unresolved: (defect_class, owner) by the pilot's gap cause (input_refs.pilot_cause); ruling addendum N1
# (Ritwik 2026-11-09): any other cause is unclassified / triage
GAP_CAUSE_CLASS = {
    "no_mapped_line": ("vocabulary", "tag_mapper"),
    "no_mapped_line_cond": ("vocabulary", "tag_mapper"),
    "no_concept_rule": ("vocabulary", "tag_mapper"),
    "quarter_not_printed_or_derivable": ("period", "period_engineer"),
}
# CELL-FORMAT v1.2 (approver ruling 2026-11-10, item 2): a TP gap key of a MAPPED data point with nothing printed
# on the face is the period engineer's; the same cause on a Q/FY/I key keeps the N1 class (unclassified / triage)
GAP_CAUSE_CLASS_TP = {"no_face_print_for_period": ("period", "period_engineer")}
# blank reason -> cell state for a key outside the template's grains (ruling item 1): a before-image multi-year
# key is written as not_in_template, never as a defect (no class, no owner)
NOT_IN_TEMPLATE_REASONS = {"period_grain_outside_template": "not_in_template"}
# blank reason -> cell state, for blanks that are not defects (no defect class, no owner): the company has no
# public filing for this period (its history window ends before it, or a wrong-entity window was excluded and no
# comparative of the company's own later filings covers the key). Approver note 2026-11-10 (KDP, IBRX quarters).
HORIZON_REASONS = {"no_public_filing_for_period": "history_horizon"}
REASON_TEXT = {
    "period_grain_outside_template": "period grain outside template: multi-year",
    "no_public_filing_for_period": "The company filed no public report for this period (it was not yet a reporting company in this form, or its earlier filings belong to another entity), so no value exists to show.",
    "cell_proof_disagree": "The independent proof of this cell against the filing disagrees with the stored value, so it is not shown until the disagreement is resolved.",
    "filing_not_in_store": "The filing for this period is not in the statement store yet, so no value is shown for it.",
    "hybrid_gap_unresolved": "The filing is stored, but this value could not be read from its statements yet; the cause is recorded with the cell.",
    "latest_copy_fails_identity": "The latest filing that prints this value fails an arithmetic check of its statement column; an older copy is not used instead.",
    "conflicting_values_in_filing": "The filing prints two different values for this line and period.",
    "mixed_vintage_inputs": "The quarter would subtract year-to-date values from filings with a restatement between them.",
    "no_basis_witness": "The later filing re-prints no earlier period of this line, so the two year-to-date values cannot be shown to be on one basis.",
    "no_prior_quarter_end": "The prior year-to-date value needed to compute this quarter is not printed.",
    "derived_quarter_fails_residual_guard": "The computed quarter is negative or larger than its year-to-date total.",
    "predecessor_successor_split": "The period spans the change from predecessor to successor accounting, so its two parts are on different bases and are not added together.",
    "balance_sheet_not_filed": "No balance sheet was filed for this date.",
    "not_filed_separately": "The company reports this figure only for the full year; the fourth quarter is not printed and is never computed.",
    "note_values_disagree": "The notes print two different gross figures for this period (different perimeters), so neither is shown.",
    "note_value_not_positive": "The note prints zero or a negative figure, which is not a gross amount for this line.",
    "sole_debt_label_not_interest": "The only interest line the filing prints is not labelled as interest expense, so it is not taken as the total.",
    "sign_inconsistent": "The filing stores this expense with a negative sign; it is shown only after the sign is checked against the printed page.",
    "line_not_presented_in_filing": "The filing's cash flow statement prints no line for this item for this period.",
    "only_excluded_lines_presented": "The filing's cash flow statement prints only lines that are not this item for this period (for example shares withheld for taxes, or dividends to preferred or noncontrolling holders).",
    "line_presented_combined_with_others": "The filing prints this item only inside a line that combines it with other items, so it is not shown on its own.",
    "perimeter_line_unresolved": "The filing prints a net or unlabelled line for this item, so whether it is this item alone cannot be told from the statement.",
    "perimeter_partnership_distribution": "The filing prints distributions to partnership unitholders; whether they count as dividends paid is a definition still under review.",
    "ytd_input_only_excluded_other_vintage": "The prior year-to-date filing prints only lines that are not this item, in a different filing from the year total, so the quarter is not computed on one basis.",
}

RULE_PERIOD = "fsn.select_period_rule@1"


def load_period_rules(path: str | Path | None, company_id: int) -> list[dict[str, str]]:
    """data-team/47-fsn-store/period_rules.csv rows of one company (basis_split, unfiled_instant)."""
    import csv

    if not path or not Path(path).exists():
        return []
    return [r for r in csv.DictReader(open(path)) if int(r["company_id"]) == company_id]


def apply_period_rules(
    concept: str, cells: list[Cell], rules: list[dict[str, str]], instant: bool
) -> list[Cell]:
    """basis_split: a duration cell whose period spans the split date (start < date <= end) is a
    blank, never a sum of the two sides. unfiled_instant: the instant at that date is a reasoned
    blank (added when no cell exists, replacing one if a stray print exists)."""
    if not rules:
        return cells
    out = []
    for c in cells:
        start = (
            month_end(c.ddate, -3 * c.qtrs) + timedelta(days=1) if c.qtrs else c.ddate
        )
        hit = next(
            (
                r
                for r in rules
                if r["kind"] == "basis_split"
                and c.qtrs > 0
                and start < date.fromisoformat(r["date"]) <= c.ddate
            ),
            None,
        )
        out.append(
            _blank(
                concept,
                (c.ddate, c.qtrs),
                hit["reason_code"],
                None,
                {"rule": hit["note"]},
                RULE_PERIOD,
            )
            if hit
            else c
        )
    if instant:
        for r in rules:
            if r["kind"] != "unfiled_instant":
                continue
            d = month_end(date.fromisoformat(r["date"]), 0)
            out = [c for c in out if not (c.qtrs == 0 and c.ddate == d)]
            out.append(
                _blank(
                    concept,
                    (d, 0),
                    r["reason_code"],
                    None,
                    {"rule": r["note"]},
                    RULE_PERIOD,
                )
            )
    return sorted(out, key=lambda c: (c.ddate, c.qtrs))


@dataclass(frozen=True)
class Filing:
    id: int
    accession: str
    accepted: datetime
    form: str
    period: date | None
    fy: int | None
    fp: str | None
    fye: str | None = None  # sub.fye MMDD of the fiscal year end


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
    state: str  # value | derived | defect | history_horizon | not_presented
    value: Decimal | None = None
    filing_id: int | None = None
    tag: str | None = None
    source_value_ids: list[int] = field(default_factory=list)
    rule_id: str = RULE_PRINTED
    reason_code: str | None = None
    derivation: dict[str, Any] | None = None
    input_refs: dict[str, Any] = field(default_factory=dict)
    # exact true dates, set only on a TP blank built from a before-image key (CELL-FORMAT v1.2); every other
    # cell carries the FSN month-end ddate and is bound by the loader
    start: date | None = None
    end: date | None = None

    @property
    def grain(self) -> str:
        """I, Q, FY; TP for a printed 6- or 9-month year-to-date column (qtrs 2/3) or an exact-dated TP blank."""
        if self.start is not None:
            return "TP"
        return {0: "I", 1: "Q", 4: "FY", 2: "TP", 3: "TP"}[self.qtrs]


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
    to the dimensional and co-registrant values of that tag in that filing (the double-context guard)."""
    prints = [p for p in prints if p.uom == unit]
    members = members or {}
    s = _Series(prints, filings)
    cells: dict[tuple[date, int], Cell] = {}
    winners: dict[tuple[date, int], Print] = {}
    held: dict[
        tuple[date, int], str
    ] = {}  # keys whose latest copy is unusable, with the reason
    for key in sorted(s.by_key):
        ps = s.latest_first(key)
        top = ps[0]
        same_filing = [p for p in ps if p.filing_id == top.filing_id]
        ddate, qtrs = key
        if any(not _same(top, p) for p in same_filing):
            held[key] = "conflicting_values_in_filing"
            if qtrs in CELL_QTRS:
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
            if qtrs in CELL_QTRS:
                cells[key] = _blank(concept, key, "latest_copy_fails_identity", top, {})
            continue
        winners[key] = top
        if qtrs in CELL_QTRS:
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
    if not derive:
        # a never-derived concept (EPS, per-share): Q4 is not printed separately and is not computed
        for (ddate, n), w in sorted(winners.items()):
            if n == 4 and (ddate, 1) not in cells:
                cells[(ddate, 1)] = Cell(
                    concept,
                    ddate,
                    1,
                    "not_presented",
                    filing_id=w.filing_id,
                    rule_id=RULE_BLANK,
                    reason_code="not_filed_separately",
                    input_refs={"fy_value_id": w.value_id},
                )
    if derive:
        notes = _note_quarters(prints)
        for (ddate, n), w in sorted(winners.items()):
            if n < 2 or (ddate, 1) in cells:
                continue
            cell = _note_quarter(concept, ddate, n, w, notes, winners, members)
            if cell is None:
                cell = _ytd_difference(
                    concept, ddate, n, w, s, winners, held, residual_guard
                )
            cells[(ddate, 1)] = cell
        # A quarter whose own year-to-date input (6M / 9M / FY) is held gets that input's reason. Before, it got no
        # cell at all and surfaced as an unexplained gap (cohort dry run 41515845455: Nucor's FY and YTD columns held
        # for the FX identity left every Q2-Q4 key empty). A reason only: no value is computed.
        for (ddate, n), why in sorted(held.items()):
            if n < 2 or (ddate, 1) in cells:
                continue
            top = s.latest_first((ddate, n))[0]
            cells[(ddate, 1)] = _blank(
                concept, (ddate, 1), why, top, {"ytd_qtrs": n, "ytd_input_held": why}
            )
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
        (p.filing_id, p.tag, p.ddate): p for p in prints if p.qtrs == 1 and not p.face
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
        four = [
            p
            for i in range(4)
            if (p := notes.get((w.filing_id, w.tag, month_end(ddate, -3 * i))))
            is not None
        ]
        if len(four) == 4:
            total = sum((p.value for p in four), Decimal(0))
            tol = tol_of([w.dcml, *(p.dcml for p in four)])
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
            concept,
            key,
            held.get(prev_key, "no_prior_quarter_end"),
            w,
            {"needs": str(prev_key)},
        )
    first = s.same_basis(prev.filing_id, w.filing_id)
    pair = (prev, w) if first is None else None
    if pair is None:
        for b in s.latest_first((ddate, n)):
            for a in s.latest_first(prev_key):
                if (
                    a.checks_ok
                    and b.checks_ok
                    and s.same_basis(a.filing_id, b.filing_id) is None
                ):
                    pair = (a, b)
                    break
            if pair:
                break
    zero_pair = False
    if (
        pair is None
        and prev.value == 0
        and w.value == 0
        and prev.checks_ok
        and w.checks_ok
    ):
        # both winning year-to-date copies are printed zeros: 0 - 0 = 0 on every basis, so no basis witness is needed
        # (Dhairya 2026-11-08, Somnigroup Q2/Q3 2020 dividends; flow derivation allowed, founder 2026-11-04)
        pair, zero_pair = (prev, w), True
    if pair is None:
        return _blank(
            concept,
            key,
            first or "mixed_vintage_inputs",
            w,
            {
                "inputs": [
                    s.filings[prev.filing_id].accession,
                    s.filings[w.filing_id].accession,
                ],
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
            "input_accessions": [
                s.filings[b.filing_id].accession,
                s.filings[a.filing_id].accession,
            ],
            "policy": "zero_inputs" if zero_pair else "same_basis",
            "winning_pair": pair == (prev, w),
        },
    )


# --- fiscal labels and cell rows ------------------------------------------------------------


def _fye_month(fye: str) -> int | None:
    """sub.fye MMDD -> the month-end month FSN rounds the year end to (day <= 15: previous month)."""
    if len(fye) != 4 or not fye.isdigit():
        return None
    month, day = int(fye[:2]), int(fye[2:])
    if not 1 <= month <= 12:
        return None
    return (month - 2) % 12 + 1 if day <= 15 else month


def fiscal_label(
    ddate: date, qtrs: int, filings: Iterable[Filing]
) -> tuple[int | None, str | None]:
    """(fiscal_year, fiscal_period) of a key. With the company's fiscal year end (sub.fye), the
    fiscal year is the year of the year-end month-end that closes the period and the quarter is
    counted back from it, the core.period convention (WMT's year ending 2015-01-31 is 2015; FSN's
    sub.fy calls it 2014). Without fye: the sub row of the filing whose own period is that date,
    else the same quarter one to three years later (comparative columns)."""
    filings = list(filings)
    fyes = Counter(f.fye for f in filings if f.fye).most_common(1)
    m = _fye_month(fyes[0][0]) if fyes else None
    if m is not None:
        ahead = (m - ddate.month) % 12
        if ahead % 3 == 0:
            fy, q = month_end(ddate, ahead).year, 4 - ahead // 3
            if qtrs == 4:
                return fy, "FY"
            if qtrs == 1:
                return fy, f"Q{q}"
            return fy, ("FY" if q == 4 else f"Q{q}")
    by_period: dict[date, Filing] = {}
    for f in sorted(filings, key=lambda f: f.accepted):
        if f.period is not None:
            by_period.setdefault(f.period, f)
    for back in range(4):
        match = by_period.get(month_end(ddate, 12 * back))
        if match is None or match.fy is None:
            continue
        fy = match.fy - back
        if qtrs == 4:
            return fy, "FY"
        if qtrs == 1:
            return fy, (match.fp if match.fp in ("Q1", "Q2", "Q3") else "Q4")
        return fy, (match.fp if match.fp in ("Q1", "Q2", "Q3") else "FY")
    return None, None


def to_row(
    cell: Cell, company_id: int, filings: dict[int, Filing], *, unit: str = "USD"
) -> dict[str, Any]:
    """The cell as a CELL-FORMAT row, bound by fiscal label (the loader binds within 10 days). A TP row
    (v1.2) carries no fiscal period: year-to-date periods have none in core.period, so the loader binds it by
    its FSN end and duration class (qtrs), or by the exact dates an exact-dated TP blank carries."""
    fy, fp = fiscal_label(cell.ddate, cell.qtrs, filings.values())
    f = filings.get(cell.filing_id) if cell.filing_id else None
    grain = cell.grain
    if grain == "TP":
        fp = None
    row: dict[str, Any] = {
        "company_id": company_id,
        "data_point_name": cell.concept,
        "period_grain": grain,
        "qtrs": cell.qtrs,
        "period_start": cell.start.isoformat() if cell.start else None,
        "period_end": cell.end.isoformat() if cell.end else None,
        "fiscal_year": fy,
        "fiscal_period": fp,
        "period_type": "instant" if cell.qtrs == 0 else "duration",
        "fsn_end": cell.ddate.isoformat(),
        "basis": "latest",
        "state": cell.state,
        "value": format(cell.value.normalize(), "f")
        if cell.value is not None
        else None,
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
    if cell.state == "not_presented":
        row.update(
            reason_code=cell.reason_code,
            reason_text=REASON_TEXT[cell.reason_code or ""],
        )
    if cell.state == "history_horizon":
        if HORIZON_REASONS.get(cell.reason_code or "") != "history_horizon":
            raise ValueError(
                f"history_horizon needs a horizon reason, got {cell.reason_code!r}"
            )
        row.update(
            reason_code=cell.reason_code,
            reason_text=REASON_TEXT[cell.reason_code or ""],
        )
    if cell.state == "not_in_template":
        if NOT_IN_TEMPLATE_REASONS.get(cell.reason_code or "") != "not_in_template":
            raise ValueError(
                f"not_in_template needs a template reason, got {cell.reason_code!r}"
            )
        row.update(
            reason_code=cell.reason_code,
            reason_text=REASON_TEXT[cell.reason_code or ""],
        )
    if cell.state == "defect":
        cls, owner = REASONS[cell.reason_code or ""]
        if cell.reason_code == "hybrid_gap_unresolved":
            cause = str(cell.input_refs.get("pilot_cause"))
            classes = (
                {**GAP_CAUSE_CLASS, **GAP_CAUSE_CLASS_TP}
                if grain == "TP"
                else GAP_CAUSE_CLASS
            )
            cls, owner = classes.get(cause, (cls, owner))
        text = REASON_TEXT[cell.reason_code or ""]
        if cell.input_refs.get(
            "pilot_cause"
        ):  # N1: the reason text carries the pilot cause
            text += f" Pilot cause: {cell.input_refs['pilot_cause']}."
        row.update(
            reason_code=cell.reason_code,
            reason_text=text,
            defect_class=cls,
            owner=owner,
            root_cause_class=cls,
        )
    return row


# --- the database side ----------------------------------------------------------------------


# Every value (members and co-registrant copies included, so no dim_id filter) of the mapped tags of ONE company.
# filing_id leads the (filing_id, tag_id, ...) unique key: without `filing_id = any(...)` this read cannot use the
# partial series index (dim_id = 0) and walked EVERY company's rows for the mapped tags; once fsn.value held ~900
# companies it hit the pooler's statement timeout for every company (FSN write run 42561798991, 2026-11-09).
MEMBER_VALUES_SQL = """
    select id, filing_id, tag_id, ddate, qtrs, uom, value, dcml, dim_id, coreg
    from fsn.value
    where company_id = %s and filing_id = any(%s) and tag_id = any(%s) and iprx = 0 and value is not null
"""


def load_company(conn: psycopg.Connection, company_id: int) -> dict[str, Any]:
    """Filings, per-concept prints and member values of one stored company (five indexed reads)."""
    with conn.cursor() as cur:
        cur.execute(
            "select id, accession, accepted, form, period, fy, fp, fye from fsn.filing where company_id = %s",
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
        anchor_cols = face_columns(filings, cur.fetchall())
        tag_ids = sorted({r[2] for r in mapped})
        cur.execute(MEMBER_VALUES_SQL, (company_id, sorted(filings), tag_ids))
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


def face_columns(
    filings: dict[int, Filing], anchor_prints: Iterable[tuple[int, str, date, int]]
) -> set[tuple[int, str, date, int]]:
    """Face columns (filing, stmt, ddate, qtrs): an anchor total is printed there, on a statement
    the store selects from, with a column length the form prints on its face."""
    return {
        (f, s, d, q)
        for f, s, d, q in anchor_prints
        if s in ANCHOR_TAGS
        and q in (0, 1, 2, 3, 4)
        and _form_prints(filings[f].form, q)
    }


def _form_prints(form: str, qtrs: int) -> bool:
    allowed = FACE_QTRS.get(form)
    return (
        allowed is None or qtrs in allowed
    )  # transition reports (10-KT, 10-QT): any length


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
    for vid, filing_id, tag_id, ddate, qtrs, uom, value, dcml, dim_id, coreg in values:
        for stmt, tag, concept in lines.get((filing_id, tag_id), []):
            # a member value: dimensional, or a co-registrant/legal-entity copy (FSN puts
            # LegalEntityAxis members in coreg, not in dimh: GE's SubsidiariesGecc)
            if dim_id != 0 or coreg:
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
    mapped_filings: dict[str, set[int]] = defaultdict(set)
    for filing_id, _stmt, _tag_id, _tag, concept in mapped:
        mapped_filings[concept].add(filing_id)
    return {
        "filings": filings,
        "prints": {c: list(ps.values()) for c, ps in prints.items()},
        "members": dict(members),
        "face_cols": anchor_cols,
        "mapped_filings": dict(mapped_filings),
    }


RULE_ABSENT = "fsn.absent_line@1"


def explain_excluded_inputs(
    cells: list[Cell], excluded: dict[tuple[str, date, int], list[int]]
) -> list[Cell]:
    """A quarter blanked `no_prior_quarter_end` whose prior year-to-date period IS printed, but only as excluded lines
    (pilot.definitional_exclusions), gets the true reason: the year total and that YTD are different filings, so 0 - 0
    is not taken on one basis (Dhairya 2026-11-08, Brixmor Q4 2015 / Q4 2016 buybacks: FY 0 in the FY2017/FY2018
    10-Ks, the 9M copies print only the equity-award line)."""
    ex_periods = {(d, q) for (_t, d, q) in excluded}
    out = []
    for c in cells:
        if (
            c.qtrs == 1
            and c.state == "defect"
            and c.reason_code == "no_prior_quarter_end"
        ):
            prev = month_end(c.ddate, -3)
            if any((prev, q) in ex_periods for q in (1, 2, 3)):
                c = Cell(
                    c.concept,
                    c.ddate,
                    c.qtrs,
                    "defect",
                    filing_id=c.filing_id,
                    rule_id=RULE_ABSENT,
                    reason_code="ytd_input_only_excluded_other_vintage",
                    input_refs={
                        **c.input_refs,
                        "prior_ytd_excluded_by_label": prev.isoformat(),
                    },
                )
        out.append(c)
    return out


def excluded_period_cells(
    concept: str,
    cells: list[Cell],
    excluded: dict[tuple[str, date, int], list[int]],
    filings: dict[int, Filing],
) -> list[Cell]:
    """not_presented `only_excluded_lines_presented` cells for the periods a filing excludes by its label
    (pilot.definitional_exclusions): FY and Q4 for an annual column, the quarter for a 3-month or year-to-date
    column. Never replaces a cell select already decided."""
    have = {(c.ddate, c.qtrs) for c in cells}
    targets: dict[tuple[date, int], set[int]] = defaultdict(set)
    for (_tag, ddate, qtrs), fids in excluded.items():
        for key in [(ddate, 4), (ddate, 1)] if qtrs == 4 else [(ddate, 1)]:
            targets[key].update(fids)
    out = []
    for (ddate, qtrs), fid_set in sorted(targets.items()):
        if (ddate, qtrs) in have:
            continue
        order = sorted(fid_set, key=lambda f: (filings[f].accepted, f))
        out.append(
            Cell(
                concept,
                ddate,
                qtrs,
                "not_presented",
                filing_id=order[-1],
                rule_id=RULE_ABSENT,
                reason_code="only_excluded_lines_presented",
                input_refs={
                    "accessions": [filings[f].accession for f in order],
                    "excluded_by_label": True,
                },
            )
        )
    return out


def absent_line_cell(
    concept: str,
    grain: str,
    end: date,
    data: dict[str, Any],
    line_classes: dict[int, list[str]],
) -> Cell | None:
    """An evidenced blank for a cash-flow key with no cell, or None (the key stays a gap).

    The filings that print the statement's cash-flow face column ending at `end` (FY: the annual column; Q: any
    duration column, a 10-Q prints year-to-date) are the evidence. When none of them maps a line to the concept,
    `line_classes[filing_id]` (the lane's classes of that filing's cash-flow lines for this concept, from the line
    tag and label only, never from values) decides:
      no family line at all             not_presented  line_not_presented_in_filing
      only lines the lane excludes      not_presented  only_excluded_lines_presented (tax withholding, NCI, ...)
      a combined line                   not_presented  line_presented_combined_with_others
      partnership-unit distributions    defect         perimeter_partnership_distribution (a definition call)
      a net / unresolved line           defect         perimeter_line_unresolved
      a common line (any tag) or a      None: a line exists that may be the concept, so nothing is claimed
      share purchase the lane's repurchase test does not name (unclassified_share_line)
    """
    cols = [
        (f, d, q)
        for (f, st, d, q) in data["face_cols"]
        if st == "CF"
        and abs((d - end).days) <= 10
        and (q == 4 if grain == "FY" else q >= 1)
    ]
    if not cols:
        return None
    fids = sorted(
        {f for f, _d, _q in cols}, key=lambda f: (data["filings"][f].accepted, f)
    )
    if set(fids) & data["mapped_filings"].get(concept, set()):
        return None
    every = {c for f in fids for c in line_classes.get(f, [])}
    if {"common", "unclassified_share_line", "no_financing_section"} & every:
        return None  # a line in ANY filing that prints the column may be the concept: nothing is claimed
    # the evidence carrier is the filing whose own period is this date (it prints the column on its face), an original
    # before an amendment; a later filing only re-prints it and may print a longer column (Verifier 2026-11-08,
    # Brixmor Q1 2025, Kraft Heinz 10-Q vs 10-Q/A). The reason is read from the carrier's own lines: another filing's
    # unrelated line never changes it (Sunoco FY2023, Clearway Q4 2021)
    own = [
        f
        for f in fids
        if data["filings"][f].period is not None
        and abs((data["filings"][f].period - end).days) <= 10
    ]
    pool = [f for f in own if not data["filings"][f].form.endswith("/A")] or own or fids
    latest = pool[-1]
    classes = sorted(line_classes.get(latest, []))
    if not classes:
        state, reason = "not_presented", "line_not_presented_in_filing"
    elif "perimeter_partnership_distribution" in classes:
        state, reason = "defect", "perimeter_partnership_distribution"
    elif any(c in ("net", "unresolved") for c in classes):
        state, reason = "defect", "perimeter_line_unresolved"
    elif "combined" in classes:
        state, reason = "not_presented", "line_presented_combined_with_others"
    else:
        state, reason = "not_presented", "only_excluded_lines_presented"
    ddate = next(d for f, d, _q in cols if f == latest)
    return Cell(
        concept,
        ddate,
        4 if grain == "FY" else 1,
        state,
        filing_id=latest,
        rule_id=RULE_ABSENT,
        reason_code=reason,
        input_refs={
            "accessions": [data["filings"][f].accession for f in fids],
            "line_classes": classes,
        },
    )


NEVER_DERIVED_UNITS = ("USD/shares", "shares", "pure")
# FSN (like FSDS) files per-share values with uom "USD", not "USD/shares": filter prints by this
FSN_UOM = {"USD/shares": "USD"}


def select_company(
    conn: psycopg.Connection,
    company_id: int,
    units: dict[str, str] | None = None,
    period_rules: str | Path | None = None,
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
            unit=FSN_UOM.get(unit, unit),
            derive=unit not in NEVER_DERIVED_UNITS and "eps" not in concept,
            residual_guard="revenue" in concept,
        )
        cells = apply_period_rules(
            concept,
            cells,
            load_period_rules(period_rules, company_id),
            instant=bool(prints) and all(p.qtrs == 0 for p in prints),
        )
        rows.extend(to_row(c, company_id, data["filings"], unit=unit) for c in cells)
    return rows


# --- note-sourced values (approved company x concept pairs) ------------------------------------


@dataclass(frozen=True)
class NoteFact:
    value_id: int
    filing_id: int
    tag: str
    ddate: date
    qtrs: int
    value: Decimal
    dcml: int | None
    label: str | None = None  # the face plabel when the tag sits on a statement line


def select_note_values(
    concept: str,
    facts: list[NoteFact],
    filings: dict[int, Filing],
    taken: set[tuple[date, int]],
    *,
    sole_debt: bool = False,
    label_verified: bool = False,
    cleared: dict[tuple[str, date, int], tuple[Decimal, Decimal]] | None = None,
) -> list[Cell]:
    """Cells from non-dimensional NOTE facts for keys (FY/Q) that have no face cell. The latest
    filing printing the key wins; within it the first tag in NOTE_TAGS order. Two tags with
    different values in that filing (two perimeters: International Paper) or a value <= 0 hold
    the key with a reason. Every cell is marked source=note for its own Verifier stratum."""
    order = {t: i for i, t in enumerate(NOTE_TAGS.get(concept, ()))}
    # interest-family tags each filing prints (any date): the sole-debt test is per filing
    family: dict[int, set[str]] = defaultdict(set)
    for f in facts:
        family[f.filing_id].add(f.tag)
    sole = sole_debt and concept == "interest_expense_resolved"
    if sole:
        order = {**order, SOLE_DEBT_TAG: len(order)}
    by_key: dict[tuple[date, int], list[NoteFact]] = defaultdict(list)
    for f in facts:
        if f.qtrs in (1, 4) and f.tag in order and (f.ddate, f.qtrs) not in taken:
            if f.tag == SOLE_DEBT_TAG and family[f.filing_id] != {SOLE_DEBT_TAG}:
                continue  # Debt is a component wherever another interest tag is printed
            by_key[(f.ddate, f.qtrs)].append(f)
    out: list[Cell] = []
    for key, fs in sorted(by_key.items()):
        latest = max(fs, key=lambda f: (filings[f.filing_id].accepted, f.filing_id))
        mine = sorted(
            (f for f in fs if f.filing_id == latest.filing_id),
            key=lambda f: order[f.tag],
        )
        top = mine[0]
        refs: dict[str, Any] = {
            "source": "note",
            "tag": top.tag,
            "tags": sorted({f.tag for f in mine}),
        }
        if top.tag == SOLE_DEBT_TAG:
            refs.update(
                sole_debt=True,
                label=top.label,
                label_unverified=top.label is None and not label_verified,
            )
            if top.label is not None and "interest" not in top.label.lower():
                out.append(
                    Cell(
                        concept,
                        key[0],
                        key[1],
                        "defect",
                        filing_id=top.filing_id,
                        rule_id=RULE_NOTE_VALUE,
                        reason_code="sole_debt_label_not_interest",
                        input_refs=refs,
                    )
                )
                continue
        if any(abs(f.value - top.value) > tol_of([f.dcml, top.dcml]) for f in mine):
            out.append(
                Cell(
                    concept,
                    key[0],
                    key[1],
                    "defect",
                    filing_id=top.filing_id,
                    rule_id=RULE_NOTE_VALUE,
                    reason_code="note_values_disagree",
                    input_refs={**refs, "values": sorted({str(f.value) for f in mine})},
                )
            )
            continue
        acc = filings[top.filing_id].accession
        pin = (cleared or {}).get((acc, key[0], key[1]))
        if (
            pin is not None and top.value == pin[0]
        ):  # a Verifier-cleared key, stored value pinned
            refs.update(cleared_from=str(top.value))
            out.append(
                Cell(
                    concept,
                    key[0],
                    key[1],
                    "value",
                    pin[1],
                    top.filing_id,
                    top.tag,
                    [top.value_id],
                    RULE_NOTE_VALUE,
                    input_refs=refs,
                )
            )
            continue
        if top.value < 0:
            out.append(
                Cell(
                    concept,
                    key[0],
                    key[1],
                    "defect",
                    filing_id=top.filing_id,
                    rule_id=RULE_NOTE_VALUE,
                    reason_code="sign_inconsistent",
                    input_refs={**refs, "value": str(top.value)},
                )
            )
            continue
        # a printed zero is the filer's value (Toll Brothers FY2015-2019: interest fully capitalised);
        # served as note-sourced like any other gross figure (Ritwik 2026-11-03)
        out.append(
            Cell(
                concept,
                key[0],
                key[1],
                "value",
                top.value,
                top.filing_id,
                top.tag,
                [top.value_id],
                RULE_NOTE_VALUE,
                input_refs=refs,
            )
        )
    return out


def load_note_values(
    conn: psycopg.Connection, company_id: int, concept: str, *, sole_debt: bool = False
) -> list[NoteFact]:
    """Non-dimensional USD facts of the concept's NOTE_TAGS for one stored company (one read);
    with sole_debt, every interest-family tag and the face label where the tag is on a line."""
    tags = list(NOTE_TAGS.get(concept, ()))
    if sole_debt and concept == "interest_expense_resolved":
        tags = list(INTEREST_FAMILY)
    if not tags:
        return []
    rows = conn.execute(
        """
        select v.id, v.filing_id, t.tag, v.ddate, v.qtrs, v.value, v.dcml,
               (select l.plabel from fsn.line l where l.filing_id = v.filing_id and l.tag_id = v.tag_id
                 order by l.report, l.line limit 1)
        from fsn.value v join fsn.tag t on t.id = v.tag_id and not t.custom
        where v.company_id = %s and v.dim_id = 0 and v.iprx = 0 and v.coreg = ''
          and v.uom = 'USD' and v.value is not null and t.tag = any(%s)
        """,
        (company_id, tags),
    ).fetchall()
    return [
        NoteFact(r[0], r[1], r[2], r[3], r[4], Decimal(r[5]), r[6], r[7]) for r in rows
    ]
