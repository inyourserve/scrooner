"""Filer XBRL errors: the one reader of data-team/tags/line_map/rules/filer_xbrl_errors.csv.

Rows (ruled by Dhairya and the Tag Expert, 2026-11-14) either CORRECT a filer's wrong XBRL fact (a sign or scale
error: xbrl_value is the stored wrong value, printed_value the filing's printed one) or SUPPLY a fact the filer did not
tag for the current year (xbrl_value empty). Key = (accession, tag, qtrs). The filing check (fsn_store/checks) and the
direct serving / structural load (mapper/structural_*) read it through here; the proof reads it on its own branch.
Money is Decimal. A malformed row raises ValueError (a silently skipped correction would hide a wrong value)."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

CSV_PATH = (
    Path(__file__).resolve().parents[4]
    / "data-team"
    / "tags"
    / "line_map"
    / "rules"
    / "filer_xbrl_errors.csv"
)
ACCESSION_RE = re.compile(r"^\d{10}-\d{2}-\d{6}$")
VALUE_SOURCE = "filer_xbrl_correction"
COLUMNS = ("accession", "tag", "qtrs", "xbrl_value", "printed_value", "evidence")

Key = tuple[str, str, int]


@dataclass(frozen=True)
class Correction:
    accession: str
    tag: str
    qtrs: int
    xbrl_value: (
        Decimal | None
    )  # None: the filer did not tag the fact for this year (SUPPLY)
    printed_value: Decimal
    evidence: str

    @property
    def key(self) -> Key:
        return (self.accession, self.tag, self.qtrs)

    @property
    def supplies(self) -> bool:
        return self.xbrl_value is None

    def note(self) -> str:
        was = "supplied (not tagged)" if self.supplies else f"XBRL {self.xbrl_value}"
        return (
            f"filer_xbrl_correction {self.accession} {self.tag} qtrs {self.qtrs}: "
            f"{was} -> printed {self.printed_value}; evidence: {self.evidence}"
        )

    def as_detail(self) -> dict[str, Any]:
        return {
            "accession": self.accession,
            "tag": self.tag,
            "qtrs": self.qtrs,
            "xbrl_value": None if self.supplies else str(self.xbrl_value),
            "printed_value": str(self.printed_value),
            "evidence": self.evidence,
        }


def _dec(s: str, what: str, line: int) -> Decimal:
    try:
        d = Decimal(s.strip())
    except InvalidOperation as exc:
        raise ValueError(f"filer_xbrl_errors line {line}: bad {what} {s!r}") from exc
    if not d.is_finite():
        raise ValueError(f"filer_xbrl_errors line {line}: {what} {s!r} is not finite")
    return d


def parse(rows: Iterable[dict[str, str]]) -> dict[Key, tuple[Correction, ...]]:
    """Validate and index CSV rows by (accession, tag, qtrs). SEVERAL rows may share that key when their xbrl_value
    differs (STX FY2024 10-K stores the FY2022 and FY2024 DPS both wrong, at different values); the stored value picks
    the row. Raises ValueError on a bad accession, qtrs, number, empty printed value, empty evidence, a correction that
    changes nothing, a duplicate (accession, tag, qtrs, xbrl_value), or a supplying row beside another row of its key
    (a supply has no stored fact to tell the rows apart). Pure."""
    out: dict[Key, list[Correction]] = {}
    for n, r in enumerate(rows, start=2):
        acc, tag = (r.get("accession") or "").strip(), (r.get("tag") or "").strip()
        if not ACCESSION_RE.match(acc):
            raise ValueError(f"filer_xbrl_errors line {n}: bad accession {acc!r}")
        if not tag:
            raise ValueError(f"filer_xbrl_errors line {n}: empty tag")
        try:
            qtrs = int((r.get("qtrs") or "").strip())
        except ValueError as exc:
            raise ValueError(f"filer_xbrl_errors line {n}: bad qtrs") from exc
        if not 0 <= qtrs <= 4:
            raise ValueError(f"filer_xbrl_errors line {n}: qtrs {qtrs} not in 0..4")
        xv_s = (r.get("xbrl_value") or "").strip()
        xv = _dec(xv_s, "xbrl_value", n) if xv_s else None
        pv_s = (r.get("printed_value") or "").strip()
        if not pv_s:
            raise ValueError(f"filer_xbrl_errors line {n}: empty printed_value")
        pv = _dec(pv_s, "printed_value", n)
        ev = (r.get("evidence") or "").strip()
        if not ev:
            raise ValueError(f"filer_xbrl_errors line {n}: empty evidence")
        if xv is not None and xv == pv:
            raise ValueError(
                f"filer_xbrl_errors line {n}: xbrl_value equals printed_value"
            )
        c = Correction(acc, tag, qtrs, xv, pv, ev)
        same = out.setdefault(c.key, [])
        if any(o.xbrl_value == c.xbrl_value for o in same):
            raise ValueError(
                f"filer_xbrl_errors line {n}: duplicate key {c.key} xbrl_value {c.xbrl_value}"
            )
        if same and (c.supplies or any(o.supplies for o in same)):
            raise ValueError(
                f"filer_xbrl_errors line {n}: a supplying row cannot share the key {c.key} with another row"
            )
        same.append(c)
    return {k: tuple(v) for k, v in out.items()}


@lru_cache(maxsize=4)
def _load(path: str) -> dict[Key, tuple[Correction, ...]]:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise ValueError(
                f"filer_xbrl_errors header {reader.fieldnames} != {COLUMNS}"
            )
        return parse(reader)


def load(path: Path | None = None) -> dict[Key, tuple[Correction, ...]]:
    """(accession, tag, qtrs) -> its Corrections from the committed CSV (cached per path)."""
    return _load(str(path or CSV_PATH))


def all_corrections(path: Path | None = None) -> list[Correction]:
    """Every correction row, in file order of key."""
    return [c for cs in load(path).values() for c in cs]


def for_accession(accession: str, path: Path | None = None) -> list[Correction]:
    """The Corrections of one filing, sorted by (tag, qtrs, xbrl_value)."""
    return sorted(
        (c for c in all_corrections(path) if c.accession == accession),
        key=lambda c: (c.tag, c.qtrs, c.xbrl_value if c.xbrl_value is not None else Decimal(0)),
    )


def pick(
    corrections: Iterable[Correction], stored: Decimal | None
) -> Correction | None:
    """The row of one (accession, tag, qtrs) that covers the stored value: the correcting row whose xbrl_value equals
    it; else the supplying row; else, when `stored` is None (unknown) and there is exactly one row, that row; else the
    correcting row whose printed_value is already stored. None when no row fits. Pure."""
    rows = list(corrections)
    for c in rows:
        if c.supplies:
            return c
    if stored is not None:
        for c in rows:
            if c.xbrl_value == stored:
                return c
        for c in rows:
            if c.printed_value == stored:
                return c
        return rows[0] if len(rows) == 1 else None
    return rows[0] if len(rows) == 1 else None


def corrected_value(
    accession: str, tag: str, qtrs: int, value: Decimal, path: Path | None = None
) -> Decimal:
    """The printed value when a correcting row covers this stored fact (same accession, tag, qtrs and the stored wrong
    value), else the value unchanged. A supplying row has no stored fact to replace. Pure."""
    for c in load(path).get((accession, tag, qtrs), ()):
        if not c.supplies and c.xbrl_value == value:
            return c.printed_value
    return value


def stored_problems(c: Correction, stored: Iterable[Decimal]) -> str | None:
    """Why a correction does not fit the stored undimensioned facts of its (accession, tag, qtrs), or None. A correcting
    row needs the stored wrong value among them; a supplying row needs the printed value NOT among them. Pure."""
    vals = set(stored)
    if c.supplies:
        if c.printed_value in vals:
            return f"supplied value {c.printed_value} is already stored"
        return None
    if c.xbrl_value not in vals:
        return (
            f"xbrl_value {c.xbrl_value} is not a stored fact (stored: {sorted(vals)})"
        )
    return None


def validate_against_store(conn, path: Path | None = None) -> list[str]:
    """Read-only: every correction against fsn.value (undimensioned, no coreg). Returns the problems (empty = fits)."""
    problems: list[str] = []
    for c in load(path).values():
        with conn.cursor() as cur:
            cur.execute(
                """select v.value from fsn.value v join fsn.tag t on t.id = v.tag_id
                   join fsn.filing f on f.id = v.filing_id
                   where f.accession = %s and t.tag = %s and v.qtrs = %s
                     and v.dim_id = 0 and v.coreg = '' and v.value is not null""",
                (c.accession, c.tag, c.qtrs),
            )
            stored = [Decimal(v) for (v,) in cur.fetchall()]
        why = stored_problems(c, stored)
        if why:
            problems.append(f"{c.key}: {why}")
    return problems
