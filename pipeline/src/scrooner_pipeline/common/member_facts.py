"""Dimensioned (member) parts of a structural resolver claim, read from the stored FSN facts (fsn.value, dim_id <> 0).

core.fact holds the SEC API's undimensioned facts only (it has no dimension column), so a dimensioned value exists in
the store only as fsn.value x fsn.dim.segments ('ClassOfStock=CommonClassA;'). A claim part written `Tag[Member]` (the
resolver prints the member without its axis) or `Tag[Axis=Member]` (face facts with an EquityComponents member) resolves
to exactly ONE stored fact of the claim's own accession and period:

  * the fact carries exactly that member as its only segment (never a fact with extra axes, never the undimensioned
    total, never another member);
  * a member-only part must find that member under ONE axis for the tag in that filing and column; two axes holding the
    member make the part ambiguous and it is rejected (no pick);
  * a part with two stored values (a restated copy, shares and USD) resolves only by the value the resolver node
    printed; otherwise it is rejected.

Used by both structural-load (the claim row stores the resolved `Tag[Axis=Member]`) and direct serving (the value), so
claims and serving agree. Pure parts (split/resolve) are unit-testable; read_member_rows is one indexed read by filing.
The value is the stored fact's own; the resolver node value is only a cross-check by the caller."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import psycopg

from scrooner_pipeline.common.fsn_dates import fsn_end_matches
from scrooner_pipeline.proof.dims import _segment_name, normalize_dims

_PART_RE = re.compile(r"^(?P<neg>-?)(?P<tag>[^\[\]]+)\[(?P<body>[^\[\]]+)\]$")


@dataclass(frozen=True)
class MemberSpec:
    prefix: str  # taxonomy prefix as written ('' when none)
    base: str  # tag name
    segs: str | None  # normalised segments when the axis is named ('Axis=Member;'), else None
    member: str | None  # the member (no 'Member' suffix) when only the member is named
    sign: int = 1

    def text(self) -> str:
        """The part as a claim tag (no prefix, no ':'): `Tag[Member]` or `Tag[Axis=Member,...]`."""
        return part_text(self.base, self.segs, self.member)


def part_text(base: str, segs: str | None, member: str | None) -> str:
    if segs is not None:
        return f"{base}[{','.join(p for p in segs.split(';') if p)}]"
    return f"{base}[{member}]"


def is_member_part(tag: str | None) -> bool:
    return tag is not None and ("[" in tag or "]" in tag)


def split_member_part(part: str) -> MemberSpec:
    """'-us-gaap:Tag[CommonClassA]' / 'Tag[EquityComponents=RetainedEarnings]' -> MemberSpec. ValueError(member_syntax)
    for anything else (a stray bracket is never part of a tag)."""
    m = _PART_RE.match(part.strip())
    if not m:
        raise ValueError(f"member_syntax: {part!r}")
    prefix, _, base = m["tag"].strip().rpartition(":")
    if not base or " " in base or ":" in prefix:
        raise ValueError(f"member_syntax: {part!r}")
    sign = -1 if m["neg"] else 1
    body = m["body"].strip()
    if "=" in body:
        return MemberSpec(prefix, base, normalize_dims(body), None, sign)
    member = _segment_name(body, "Member")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", member):
        raise ValueError(f"member_syntax: {part!r}")
    return MemberSpec(prefix, base, None, member, sign)


# the axis family a resolver rule flag names (RESOLVER-OUTPUT-FORMAT: class_sum = 'class sum over ClassOfStock members',
# ap/ar_related_sum = RelatedPartyTransactionsByRelatedPartyAxis, cor_member_sum = ProductOrServiceAxis)
AXIS_BY_FLAG = {
    "class_sum": "ClassOfStock",
    "ap_related_sum": "RelatedPartyTransactionsByRelatedParty",
    "ar_related_sum": "RelatedPartyTransactionsByRelatedParty",
    "cor_member_sum": "ProductOrService",
}


def axis_hint_of(flags: str) -> str | None:
    fl = {f.strip() for f in flags.replace(",", ";").split(";")}
    axes = {a for f, a in AXIS_BY_FLAG.items() if f in fl}
    return next(iter(axes)) if len(axes) == 1 else None


@dataclass(frozen=True)
class MemberRow:
    ddate: date
    qtrs: int
    uom: str
    segments: str
    value: Decimal
    value_id: int


@dataclass(frozen=True)
class MemberHit:
    value: Decimal
    ids: tuple[int, ...]
    segments: str
    part_tag: str  # the resolved `Tag[Axis=Member]`


def read_member_rows(
    conn: psycopg.Connection,
    company_id: int,
    accessions: set[str],
    bases: set[str],
) -> dict[tuple[str, str], list[MemberRow]]:
    """(accession, tag) -> stored dimensioned numeric facts of exactly those filings (no coreg, iprx 0)."""
    out: dict[tuple[str, str], list[MemberRow]] = {}
    if not accessions or not bases:
        return out
    with conn.cursor() as cur:
        cur.execute(
            """select f.accession, t.tag, v.ddate, v.qtrs, v.uom, d.segments, v.value, v.id
               from fsn.filing f
               join fsn.value v on v.filing_id = f.id
               join fsn.tag t on t.id = v.tag_id
               join fsn.dim d on d.id = v.dim_id
               where f.accession = any(%s) and t.tag = any(%s) and v.company_id = %s
                 and v.dim_id <> 0 and v.coreg = '' and v.iprx = 0 and v.value is not null""",
            (sorted(accessions), sorted(bases), company_id),
        )
        for acc, tag, ddate, qtrs, uom, segs, value, vid in cur.fetchall():
            out.setdefault((acc, tag), []).append(
                MemberRow(ddate, qtrs, uom, segs or "", Decimal(value), vid)
            )
    return out


def _pairs(segments: str) -> list[str]:
    return [p for p in segments.split(";") if p]


def resolve_member_part(
    rows: list[MemberRow],
    spec: MemberSpec,
    end: date,
    want: Decimal | None,
    axis_hint: str | None = None,
) -> MemberHit | str:
    """The ONE stored fact for the part at the period `end`, or the reason there is none. Instants (qtrs 0) and yearly
    columns (3..5 quarters) only. No fallback to another member, another axis or the undimensioned total."""
    here = [
        r
        for r in rows
        if fsn_end_matches(r.ddate, end) and (r.qtrs == 0 or 3 <= r.qtrs <= 5)
    ]
    if spec.segs is not None:
        hit = [r for r in here if r.segments == spec.segs]
    else:
        hit = [
            r
            for r in here
            if len(_pairs(r.segments)) == 1
            and _pairs(r.segments)[0].partition("=")[2] == spec.member
        ]
    if not hit:
        return "no stored dimensioned fact for the member in that filing and column"
    axes = sorted({r.segments for r in hit})
    if len(axes) > 1 and axis_hint and spec.segs is None:
        # the resolver's own rule names the axis family (class sum: ClassOfStock); narrow only, never widen
        hit = [r for r in hit if r.segments.startswith(f"{axis_hint}=")]
        axes = sorted({r.segments for r in hit})
    if len(axes) > 1:
        return f"member is ambiguous: stored under {', '.join(axes)}"
    values: dict[Decimal, set[int]] = {}
    for r in hit:
        values.setdefault(r.value, set()).add(r.value_id)
    if len(values) > 1 and want is not None and want in values:
        values = {want: values[want]}
    if len(values) > 1:
        return "two stored values for the member in that filing (units or a restated copy)"
    ((v, ids),) = values.items()
    segs = axes[0]
    return MemberHit(v, tuple(sorted(ids)), segs, part_text(spec.base, segs, None))
