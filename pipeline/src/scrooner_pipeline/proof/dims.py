"""Proof of a dimensional cell (company_tag_map rows with dims, 0125): the filing's value of each part tag under the
row's own segments, summed with the row's signs, against the shown value at the filer's stated precision.

A part's value is read ONLY under exactly its segments (FilingStructure.value_dim); the no-dimension total or another
slice is never a stand-in. A part the filing does not print under those segments makes the cell UNCHECKED (unknown,
not a disagreement). The FSN quarter is the SEC's own data set, read by position from the filing (proof/fsn.py)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, fsn_ddate

PROVEN, DISAGREE, UNCHECKED = "PROVEN", "DISAGREE", "UNCHECKED"


_PART_RE = re.compile(r"^(?P<tag>[^\[\]]+)\[(?P<dims>[^\[\]]*=[^\[\]]*)\]$")


def _segment_name(raw: str, suffix: str) -> str:
    """'us-gaap:ProductOrServiceAxis' -> 'ProductOrService' (the FSN store keeps neither prefix nor suffix)."""
    name = raw.strip().rpartition(":")[2]
    return name[: -len(suffix)] if name.endswith(suffix) and name != suffix else name


def normalize_dims(spec: str) -> str:
    """'ProductOrService=Product,BusinessSegments=us-gaap:GamingMember' -> 'BusinessSegments=Gaming;ProductOrService=Product;'
    (axes sorted, as fsn.dim.segments prints them). Raises ValueError on anything that is not axis=member pairs."""
    pairs: dict[str, str] = {}
    for pair in spec.split(","):
        axis, eq, member = pair.partition("=")
        if not eq:
            raise ValueError(f"member_syntax: {pair!r}")
        a, m = _segment_name(axis, "Axis"), _segment_name(member, "Member")
        if (
            not re.fullmatch(r"[A-Za-z0-9_]+", a)
            or not re.fullmatch(r"[A-Za-z0-9_.-]+", m)
            or a in pairs
        ):
            raise ValueError(f"member_syntax: {pair!r}")
        pairs[a] = m
    return "".join(f"{a}={pairs[a]};" for a in sorted(pairs))


def split_part(part: str) -> tuple[str, str]:
    """A claim part 'Tag' -> ('Tag', '') ; 'Tag[Axis=Member,...]' -> ('Tag', segments). '' means no dimension:
    the plain, non-dimensional path. A malformed bracket raises ValueError (never read as a plain tag)."""
    if "[" not in part and "]" not in part:
        return part, ""
    m = _PART_RE.match(part.strip())
    if not m:
        raise ValueError(f"member_syntax: {part!r}")
    return m["tag"].strip(), normalize_dims(m["dims"])


def find_value_dim(
    structure: FilingStructure,
    tag: str,
    ddate: date,
    qtrs: int,
    cls: str,
    segments: str,
) -> NumValue | None:
    """The printed value of tag under EXACTLY these segments, in the unit the class expects (same unit rule as
    prove.find_value). Never the total, never another slice. None = the filing prints nothing there."""
    for v in structure.dim_num.get((tag, ddate, qtrs, segments), []):
        u = v.uom.upper()
        if cls == "shares":
            ok = u.startswith("SHARES")
        elif cls == "per_share":
            ok = u.startswith("USD")
        else:
            ok = u.startswith("USD") and "/" not in u
        if ok:
            return v
    return None


@dataclass(frozen=True)
class DimPart:
    tag: str
    dims: str  # fsn.dim.segments format
    sign: int = 1


def prove_dims_cell(
    structure: FilingStructure,
    parts: list[DimPart],
    shown_value: Decimal,
    period_end: date,
    qtrs: int,
    tol: Decimal,
) -> dict:
    """{verdict, reason_code, position_value, parts: [{tag, dims, value}]}; shown within tol of the signed sum of
    the parts' printed values is PROVEN."""
    ddate = fsn_ddate(period_end)
    total = Decimal(0)
    seen: list[dict] = []
    for part in parts:
        nv = structure.value_dim(part.tag, ddate, qtrs, part.dims)
        if nv is None:
            return {
                "verdict": UNCHECKED,
                "reason_code": "no_value_under_segments",
                "position_value": None,
                "parts": seen,
                "missing": {"tag": part.tag, "dims": part.dims},
            }
        total += part.sign * nv.value
        seen.append({"tag": part.tag, "dims": part.dims, "value": str(nv.value)})
    agree = abs(shown_value - total) <= tol
    return {
        "verdict": PROVEN if agree else DISAGREE,
        "reason_code": None if agree else "shown_differs_from_printed_segments",
        "position_value": total,
        "parts": seen,
    }
