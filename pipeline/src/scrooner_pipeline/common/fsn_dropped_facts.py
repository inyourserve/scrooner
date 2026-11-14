"""FSN dropped facts: the one reader of data-team/tags/line_map/rules/fsn_dropped_facts.csv.

A fact the filing prints (an R page of the filing's own XBRL rendering) that our FSN ingest did not store (PM FY2022 10-K
R60: amortization of intangibles by income-statement location, 58 + 101 = 159). The row supplies it: key
(accession, tag, qtrs, segment), value in dollars, evidence = the R page and line. `segment` is the fsn.dim.segments
text ('Axis=Member;'), empty for an undimensioned fact. Used by member_facts (direct serving and structural load read
the same rows), the filing check, and (proof branch) the proof. Money is Decimal. A malformed row raises ValueError."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from scrooner_pipeline.common.filer_xbrl_errors import ACCESSION_RE

CSV_PATH = (
    Path(__file__).resolve().parents[4]
    / "data-team"
    / "tags"
    / "line_map"
    / "rules"
    / "fsn_dropped_facts.csv"
)
VALUE_SOURCE = "fsn_dropped_fact"
COLUMNS = ("accession", "tag", "qtrs", "segment", "value", "evidence")

Key = tuple[str, str, int, str]


def norm_segment(seg: str) -> str:
    """'A=B,C=D' / 'A=B;C=D' -> 'A=B;C=D;' (the fsn.dim.segments shape); empty stays empty."""
    parts = [p.strip() for p in seg.replace(",", ";").split(";") if p.strip()]
    return "".join(p + ";" for p in parts)


@dataclass(frozen=True)
class DroppedFact:
    accession: str
    tag: str
    qtrs: int
    segment: str
    value: Decimal
    evidence: str

    @property
    def key(self) -> Key:
        return (self.accession, self.tag, self.qtrs, self.segment)

    def note(self) -> str:
        seg = f"[{self.segment}]" if self.segment else ""
        return (
            f"fsn_dropped_fact {self.accession} {self.tag}{seg} qtrs {self.qtrs} = {self.value}: "
            f"printed by the filing, not stored by the FSN ingest; evidence: {self.evidence}"
        )

    def as_detail(self) -> dict[str, str | int]:
        return {
            "accession": self.accession,
            "tag": self.tag,
            "qtrs": self.qtrs,
            "segment": self.segment,
            "value": str(self.value),
            "evidence": self.evidence,
        }


def parse(rows: Iterable[dict[str, str]]) -> dict[Key, DroppedFact]:
    """Validate and index CSV rows (bad accession, tag, qtrs, value, empty evidence, duplicate key -> ValueError). Pure."""
    out: dict[Key, DroppedFact] = {}
    for n, r in enumerate(rows, start=2):
        acc, tag = (r.get("accession") or "").strip(), (r.get("tag") or "").strip()
        if not ACCESSION_RE.match(acc):
            raise ValueError(f"fsn_dropped_facts line {n}: bad accession {acc!r}")
        if not tag:
            raise ValueError(f"fsn_dropped_facts line {n}: empty tag")
        try:
            qtrs = int((r.get("qtrs") or "").strip())
        except ValueError as exc:
            raise ValueError(f"fsn_dropped_facts line {n}: bad qtrs") from exc
        if not 0 <= qtrs <= 4:
            raise ValueError(f"fsn_dropped_facts line {n}: qtrs {qtrs} not in 0..4")
        try:
            value = Decimal((r.get("value") or "").strip())
        except InvalidOperation as exc:
            raise ValueError(f"fsn_dropped_facts line {n}: bad value") from exc
        if not value.is_finite():
            raise ValueError(f"fsn_dropped_facts line {n}: value is not finite")
        ev = (r.get("evidence") or "").strip()
        if not ev:
            raise ValueError(f"fsn_dropped_facts line {n}: empty evidence")
        f = DroppedFact(acc, tag, qtrs, norm_segment(r.get("segment") or ""), value, ev)
        if f.key in out:
            raise ValueError(f"fsn_dropped_facts line {n}: duplicate key {f.key}")
        out[f.key] = f
    return out


@lru_cache(maxsize=4)
def _load(path: str) -> dict[Key, DroppedFact]:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise ValueError(
                f"fsn_dropped_facts header {reader.fieldnames} != {COLUMNS}"
            )
        return parse(reader)


def load(path: Path | None = None) -> dict[Key, DroppedFact]:
    return _load(str(path or CSV_PATH))


def for_accession(accession: str, path: Path | None = None) -> list[DroppedFact]:
    return sorted(
        (f for f in load(path).values() if f.accession == accession),
        key=lambda f: f.key,
    )


def stored_problems(f: DroppedFact, stored: Iterable[Decimal]) -> str | None:
    """A dropped fact must not be stored with a DIFFERENT value (the CSV would then contradict the store); the same
    value already stored is harmless (the store caught up). Pure."""
    other = sorted({v for v in stored if v != f.value})
    return f"a different value is stored for the same fact: {other}" if other else None


def validate_against_store(conn, path: Path | None = None) -> list[str]:
    """Read-only: each row against fsn.value of the same accession, tag, qtrs and segments, in the filing's own column
    (the ddate within 16 days of its period: other columns of the filing are other years)."""
    problems: list[str] = []
    for f in load(path).values():
        with conn.cursor() as cur:
            cur.execute(
                """select v.value from fsn.value v join fsn.tag t on t.id = v.tag_id
                   join fsn.filing fl on fl.id = v.filing_id join fsn.dim d on d.id = v.dim_id
                   where fl.accession = %s and t.tag = %s and v.qtrs = %s and coalesce(d.segments, '') = %s
                     and v.coreg = '' and v.iprx = 0 and v.value is not null
                     and fl.period is not null and abs(v.ddate - fl.period) <= 16""",
                (f.accession, f.tag, f.qtrs, f.segment),
            )
            stored = [Decimal(v) for (v,) in cur.fetchall()]
        why = stored_problems(f, stored)
        if why:
            problems.append(f"{f.key}: {why}")
    return problems
