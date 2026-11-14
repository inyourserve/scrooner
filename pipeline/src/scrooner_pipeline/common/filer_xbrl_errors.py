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


def parse(rows: Iterable[dict[str, str]]) -> dict[Key, Correction]:
    """Validate and index CSV rows. Raises ValueError on a bad accession, qtrs, number, empty printed value, empty
    evidence, a correction that changes nothing, or a duplicate key. Pure."""
    out: dict[Key, Correction] = {}
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
        if c.key in out:
            raise ValueError(f"filer_xbrl_errors line {n}: duplicate key {c.key}")
        out[c.key] = c
    return out


@lru_cache(maxsize=4)
def _load(path: str) -> dict[Key, Correction]:
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


def load(path: Path | None = None) -> dict[Key, Correction]:
    """(accession, tag, qtrs) -> Correction from the committed CSV (cached per path)."""
    return _load(str(path or CSV_PATH))


def for_accession(
    accession: str, path: Path | None = None
) -> dict[tuple[str, int], Correction]:
    """(tag, qtrs) -> Correction of one filing."""
    return {(c.tag, c.qtrs): c for c in load(path).values() if c.accession == accession}


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
