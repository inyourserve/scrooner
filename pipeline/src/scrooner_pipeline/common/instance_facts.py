"""Instance-sourced facts: dimensioned facts that exist only in a filing's XBRL instance (the FSN load drops facts that
carry only a BalanceSheetLocationAxis member, so neither fsn.value nor core.fact has them). The evidence source is a
committed file read from sec.gov instances (FILING-CHECKED): data-team/tags/line_map/_lease-locations-pre842-
2026-11-14.csv (cik, adsh, instance, ddate, tag, balance_sheet_location_member, value, decimals).

A map part names such a fact as `Tag[Axis=Member]` (stored in company_tag_map.tag as `Tag[Axis=Member]`, axes sorted,
no namespace prefix and no Axis/Member suffix: no ':' because the table forbids it). It resolves ONLY to a row of this
file for the filing and column; anything else is rejected (loader), held (mapper) or unchecked (proof). Facts are
instants (qtrs 0), USD. Pure: no DB, no network."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from scrooner_pipeline.proof.dims import normalize_dims
from scrooner_pipeline.proof.fsn import NumValue

REPO = Path(__file__).resolve().parents[4]
FACTS_PATH = REPO / "data-team/tags/line_map/_lease-locations-pre842-2026-11-14.csv"
LOCATION_AXIS = "BalanceSheetLocation"
VERSION = "instance"

_SPEC_RE = re.compile(r"^(?P<neg>-?)(?P<tag>[^\[\]]+)\[(?P<dims>[^\[\]]*=[^\[\]]*)\]$")


@dataclass(frozen=True)
class InstanceFact:
    adsh: str
    instance: str
    ddate: date
    tag: str  # local tag, no prefix
    segs: str  # normalized segments, as fsn.dim.segments prints them
    member: str
    value: Decimal
    decimals: int | None
    r_page: str = ""  # 'R102.htm' of the filing's R page that prints the fact (FILING-CHECKED), '' unknown

    @property
    def part_tag(self) -> str:
        return part_tag(self.tag, self.segs)

    def num_value(self) -> NumValue:
        return NumValue(
            self.tag, VERSION, self.ddate, 0, "USD", self.value, self.decimals
        )


Key = tuple[str, str, str, date]  # adsh, tag, segs, ddate


def part_tag(base: str, segs: str) -> str:
    """('CapitalLeaseObligationsCurrent', 'BalanceSheetLocation=OtherCurrentLiabilities;') ->
    'CapitalLeaseObligationsCurrent[BalanceSheetLocation=OtherCurrentLiabilities]'."""
    pairs = ",".join(p for p in segs.split(";") if p)
    return f"{base}[{pairs}]" if pairs else base


def is_instance_part(tag: str | None) -> bool:
    return tag is not None and "[" in tag


def split_instance_part(spec: str) -> tuple[int, str, str, str]:
    """'-us-gaap:Tag[Axis=Member]' or stored 'Tag[Axis=Member]' -> (sign, prefix or '', base tag, segments).
    ValueError (member_syntax) for anything else."""
    m = _SPEC_RE.match(spec.strip())
    if not m:
        raise ValueError(f"member_syntax: {spec!r}")
    prefix, _, local = m["tag"].strip().rpartition(":")
    if not local:
        raise ValueError(f"member_syntax: {spec!r}")
    return -1 if m["neg"] else 1, prefix, local, normalize_dims(m["dims"])


def _member_segs(member: str) -> str:
    name = member.strip().rpartition(":")[2]
    name = (
        name[: -len("Member")] if name.endswith("Member") and name != "Member" else name
    )
    return f"{LOCATION_AXIS}={name};"


_cache: dict[Path, dict[Key, InstanceFact]] = {}


def load(path: Path | None = None) -> dict[Key, InstanceFact]:
    """The file's located facts (member present) keyed (adsh, tag, segs, ddate). Rows without a member are not
    dimensioned facts and are not served from here. A key with two different values is dropped (ambiguous)."""
    p = path or FACTS_PATH
    if p in _cache:
        return _cache[p]
    out: dict[Key, InstanceFact] = {}
    bad: set[Key] = set()
    if p.exists():
        with p.open(newline="") as fh:
            for r in csv.DictReader(fh):
                member = (r.get("balance_sheet_location_member") or "").strip()
                if not member:
                    continue
                dec = (r.get("decimals") or "").strip()
                f = InstanceFact(
                    r["adsh"].strip(),
                    r["instance"].strip(),
                    date.fromisoformat(r["ddate"].strip()),
                    r["tag"].strip(),
                    _member_segs(member),
                    member,
                    Decimal(r["value"].strip()),
                    int(dec) if dec not in ("", "INF") else None,
                    (r.get("r_page") or "").strip(),
                )
                k = (f.adsh, f.tag, f.segs, f.ddate)
                if k in out and out[k].value != f.value:
                    bad.add(k)
                out[k] = f
    for k in bad:
        del out[k]
    _cache[p] = out
    return out


def lookup(
    adsh: str,
    base: str,
    segs: str,
    ddate: date,
    facts: dict[Key, InstanceFact] | None = None,
) -> InstanceFact | None:
    return (facts if facts is not None else load()).get((adsh, base, segs, ddate))


def at_column(
    adsh: str, ddate: date, facts: dict[Key, InstanceFact] | None = None
) -> list[InstanceFact]:
    """Every located fact of one filing at one column (the perimeter's evidence)."""
    return [
        f
        for f in (facts if facts is not None else load()).values()
        if f.adsh == adsh and f.ddate == ddate
    ]
