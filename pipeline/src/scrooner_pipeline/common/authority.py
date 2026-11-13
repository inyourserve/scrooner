"""Which copy of a fact may be the authoritative one: the face-column eligibility rule (Dhairya 2026-11-13,
tagmap-authority v2). ONE definition; the normalizer (conflict_latest_filed) and the proof (R13) both import it.

Why: a filing carries a period as a copy for many reasons. HD Goodwill at 2015-02-01 is 1,353M in seven filings
(FY2014 10-K, 10-Qs, FY2015 and FY2017 10-Ks); the FY2018 10-K printed 2,102M for that date from a note rollforward
context and won as "latest filed". A filing speaks for a period only when it PRINTS that period as a face column,
which its own period_of_report bounds:

  instant   10-K / 10-Q (and amendments): period_of_report - end_date <= 400 days (current and prior year-end)
  duration  10-K family: <= 2 years + 10 days (the income statement and cash flow print three fiscal years)
            10-Q family: <= 400 days
  The original filing (period_of_report within 10 days of the end date) is always eligible, so every period keeps
  an eligible copy. An amendment takes the same windows on its own period_of_report. Forms that are not periodic
  reports are never eligible. An unknown period_of_report cannot be judged and is treated as eligible (no evidence
  it is a far-later filing); the form test still applies.

Eligible copies compete (latest filed wins, ties to the lower accession); an ineligible copy is history only.

Statement coherence (Dhairya 2026-11-13, tag expert identity triage: 257 real breaks, mostly vintage mixes; JPM total
assets came from a summary table of the next year's 10-Q):
  1. A copy is face-eligible only if that filing's FACE statement prints that tag for that column (fsn.line of
     BS/IS/CF/CI/EQ plus a non-dimensional fsn.value in the column), not a summary table or a note: FaceIndex.eligible.
     Exception: tags the map claims as NOTE (stmt NOTE/UN, reason_class component_in_note) follow their own note rule.
     A filing the FSN store does not hold (no face line) cannot be judged and keeps the window rule above only.
  2. For one company, statement and period, every served member comes from ONE filing: the latest face-eligible filing
     that prints the column (FaceIndex.statement_filing / statement_filing()). The mapper's selection, tagmap-authority
     v2 (core.fact is_authoritative) and the proof's authority all call it. A member the statement filing does not
     print keeps its own latest eligible copy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, TypeVar

from scrooner_pipeline.common.fsn_dates import fsn_end_matches
from scrooner_pipeline.common.periodic_forms import (
    ANNUAL_FORMS_ALL,
    PERIODIC_FORMS_ALL,
)

K = TypeVar("K", int, str)

ORIGINAL_WINDOW_DAYS = 10
INSTANT_WINDOW_DAYS = 400
QUARTERLY_DURATION_WINDOW_DAYS = 400
ANNUAL_DURATION_WINDOW_DAYS = 2 * 365 + 10


def face_column_eligible(
    form: str,
    period_of_report: date | None,
    end_date: date,
    period_type: str,
) -> bool:
    """True when `form`'s filing (period_of_report) prints the period ending end_date as a face column."""
    if form not in PERIODIC_FORMS_ALL:
        return False
    if period_of_report is None:
        return True
    days = (period_of_report - end_date).days
    if days <= ORIGINAL_WINDOW_DAYS:
        return True
    if period_type == "instant":
        return days <= INSTANT_WINDOW_DAYS
    if form in ANNUAL_FORMS_ALL:
        return days <= ANNUAL_DURATION_WINDOW_DAYS
    return days <= QUARTERLY_DURATION_WINDOW_DAYS


def latest_complete_filing(
    prints_by_part: list[dict[K, date | None]], prefer: K | None = None
) -> K | None:
    """The filing a component sum (SG&A = S&M + G&A, opex = R&D + ...) is read from: among the filings that print
    EVERY part, the latest filed, ties to the higher key. ONE definition: the mapper (_one_filing_parts, keys are
    filing ids) and the proof (shown.py, keys are accessions) both call it, so what is shown and what the proof
    treats as authoritative cannot drift. Each element maps filing key -> filing date (None sorts first); the caller
    passes only face-column-eligible prints (face_column_eligible). None when no filing prints every part."""
    if not prints_by_part:
        return None
    common = set.intersection(*(set(p) for p in prints_by_part))
    if not common:
        return None
    if prefer is not None and prefer in common:
        return prefer  # the statement filing (FaceIndex.statement_filing) when it prints every part
    return max(common, key=lambda k: (prints_by_part[0][k] or date.min, k))


def latest_eligible(filed_by_key: dict[K, date | None]) -> K | None:
    """The authoritative copy among face-column-eligible copies of one cell: the latest filed, ties to the lower key
    (the normalizer's conflict_latest_filed rule). ONE definition: the proof (shown.py) picks the cell's authoritative
    filing with it instead of reading per-tag is_authoritative flags, which say nothing across tags (JNJ cash 2022:
    the restricted-cash tag's FY2022 copy was authoritative for ITS tag and was taken for the cell's authority).
    Each element maps filing key -> filing date (None sorts first); the caller passes only eligible copies."""
    if not filed_by_key:
        return None
    best = max(d or date.min for d in filed_by_key.values())
    return min(k for k, d in filed_by_key.items() if (d or date.min) == best)


# statements whose lines are the face of a filing; the comprehensive-income statement folds into IS (a combined
# statement of operations and comprehensive income is filed as either)
FACE_STMTS = ("BS", "IS", "CF", "CI", "EQ")
_STMT_FOLD = {"CI": "IS"}
NOTE_STMTS = (
    "NOTE",
    "UN",
    "CP",
)  # UN/CP = note only, no face (Claim docstring); NOTE kept for the ruling wording


def column_matches(
    ddate: date, qtrs: int, start: date | None, end: date, period_type: str
) -> bool:
    """An FSN value column (ddate rounded to a month end, qtrs) stands for the core period (start, end, type)."""
    if not fsn_end_matches(ddate, end):
        return False
    if period_type == "instant":
        return qtrs == 0
    if qtrs <= 0 or start is None:
        return False
    return qtrs * 91 - 20 <= (end - start).days <= qtrs * 91 + 20


@dataclass
class FaceIndex:
    """What each filing of ONE company prints on its face statements (fsn.line + fsn.value), read once per company.
    filings: accession -> (form, period_of_report, order key (filed, accepted epoch)); only filings with a face line.
    prints: (accession, tag) -> [(stmt, ddate, qtrs)] of the non-dimensional values on those lines.
    note_tags: tags the map claims as NOTE (exempt from the face check)."""

    filings: dict[str, tuple[str, date | None, tuple[date, float]]] = field(
        default_factory=dict
    )
    prints: dict[tuple[str, str], list[tuple[str, date, int]]] = field(
        default_factory=dict
    )
    note_tags: frozenset[str] = frozenset()

    def judged(self, accession: str) -> bool:
        return accession in self.filings

    def prints_column(
        self,
        accession: str,
        tag: str,
        start: date | None,
        end: date,
        period_type: str,
    ) -> bool:
        return any(
            column_matches(d, q, start, end, period_type)
            for _s, d, q in self.prints.get((accession, tag), ())
        )

    def printed_ok(
        self,
        accession: str,
        tag: str,
        start: date | None,
        end: date,
        period_type: str,
    ) -> bool:
        """The face-print half of eligible() alone: True when the filing is not judged (not in the FSN store) or
        the tag is note-claimed, else the filing's face statement prints the tag for the column."""
        if tag in self.note_tags or not self.judged(accession):
            return True
        return self.prints_column(accession, tag, start, end, period_type)

    def eligible(
        self,
        form: str,
        period_of_report: date | None,
        accession: str,
        tag: str,
        start: date | None,
        end: date,
        period_type: str,
    ) -> bool:
        """face_column_eligible AND the filing's face statement prints the tag for the column (rule 1)."""
        if not face_column_eligible(form, period_of_report, end, period_type):
            return False
        return self.printed_ok(accession, tag, start, end, period_type)

    def stmt_of(
        self, accession: str, tag: str, end: date, period_type: str, start=None
    ) -> str | None:
        """The statement (BS/IS/CF) a tag's column is printed on in that filing (BS, IS, CF in that order)."""
        got = {
            _STMT_FOLD.get(s, s)
            for s, d, q in self.prints.get((accession, tag), ())
            if column_matches(d, q, start, end, period_type)
        }
        return next((s for s in ("BS", "IS", "CF", "EQ") if s in got), None)

    def statement_filing(
        self, stmt: str, start: date | None, end: date, period_type: str
    ) -> str | None:
        """THE filing every member of `stmt` is served from for the column: the latest face-eligible filing whose
        face statement `stmt` prints it (latest filed, then accepted; ties to the lower accession). None when no
        judged filing prints the column (the caller keeps per-tag selection)."""
        best: tuple[tuple[date, float], str] | None = None
        for (acc, _tag), cols in self.prints.items():
            meta = self.filings.get(acc)
            if meta is None:
                continue
            if not any(
                _STMT_FOLD.get(s, s) == stmt
                and column_matches(d, q, start, end, period_type)
                for s, d, q in cols
            ):
                continue
            if not face_column_eligible(meta[0], meta[1], end, period_type):
                continue
            if best is None or (meta[2], _neg(acc)) > (best[0], _neg(best[1])):
                best = (meta[2], acc)
        return best[1] if best else None


def _neg(acc: str) -> tuple[int, ...]:
    """Sort key reversed so that max() prefers the lower accession."""
    return tuple(-ord(c) for c in acc)


def load_face_indexes(conn: Any, company_ids: list[int]) -> dict[int, FaceIndex]:
    """company_id -> FaceIndex, two indexed reads (fsn.line/fsn.value of the companies; the map's NOTE claims).
    A company with no FSN filing has an empty index (nothing is judged)."""
    out: dict[int, FaceIndex] = {c: FaceIndex() for c in company_ids}
    if not company_ids:
        return out
    if conn.execute("select to_regclass('fsn.line')").fetchone()[0] is not None:
        rows = conn.execute(
            """
            select f.company_id, f.accession, f.form, f.period, f.filed, f.accepted, t.tag, l.stmt,
                   v.ddate, v.qtrs
            from fsn.filing f
            join fsn.line l on l.filing_id = f.id and l.stmt = any(%s)
            join fsn.tag t on t.id = l.tag_id
            left join fsn.value v on v.filing_id = f.id and v.tag_id = l.tag_id and v.dim_id = 0
                                  and v.coreg = '' and v.iprx = 0 and v.value is not null
            where f.company_id = any(%s)
            """,
            (list(FACE_STMTS), company_ids),
        ).fetchall()
        seen: set[tuple[int, str, str, str, date, int]] = set()
        for cid, acc, form, por, filed, accepted, tag, stmt, ddate, qtrs in rows:
            ix = out[cid]
            ix.filings.setdefault(
                acc,
                (
                    form,
                    por,
                    (filed or date.min, accepted.timestamp() if accepted else 0.0),
                ),
            )
            if ddate is None:
                continue
            k = (cid, acc, tag, stmt, ddate, qtrs)
            if k in seen:
                continue
            seen.add(k)
            ix.prints.setdefault((acc, tag), []).append((stmt, ddate, qtrs))
    if conn.execute("select to_regclass('analytics.company_tag_map')").fetchone()[0]:
        notes: dict[int, set[str]] = {}
        for cid, tag in conn.execute(
            """
            select company_id, tag from analytics.company_tag_map
            where company_id = any(%s) and tag is not null
              and (stmt = any(%s) or reason_class = 'component_in_note')
            """,
            (company_ids, list(NOTE_STMTS)),
        ).fetchall():
            notes.setdefault(cid, set()).add(tag)
        for cid, tags in notes.items():
            out[cid].note_tags = frozenset(tags)
    return out


def statement_filing(
    conn: Any,
    company_id: int,
    stmt: str,
    start: date | None,
    end: date,
    period_type: str,
) -> str | None:
    """Accession of the filing a company's statement `stmt` ('BS'/'IS'/'CF') is served from for the period."""
    return load_face_indexes(conn, [company_id])[company_id].statement_filing(
        stmt, start, end, period_type
    )
