"""Balance-sheet identity fallback, corrected (rule ``balance.identity_equity_basis@1``).

The legacy SQL in ``concept_fallback.resolve_balance_sheet_identity_fallback`` computed

    total_liabilities = Assets - StockholdersEquity + (MinorityInterest + temporary equity)

but the identity is  Assets = Liabilities + total equity (parent + NCI) + temporary equity, so the adjustments
must be SUBTRACTED. Defects found by the derivation catalog and the Verifier (2026-10-24):
  1. sign: the adjustment was added (WMT 2026-07-31 stored 202,237M, filing 189,115M, 0000104169-26-000154 R4);
  2. double count: ``stockholders_equity`` priority 2 is the NCI-inclusive tag; when the equity input is that
     tag the NCI is already inside it (AT&T 2026-06-30 stored 319,920M, filing 299,920M, 0000732717-26-000297 R5);
  3. V1 of this fix misspelled the including-NCI temporary-equity element (``...Interests``, core.concept 32640)
     and read only part of the redeemable-NCI family (AMRX, MCK, IPG, ETP);
  4. terms from different filings were mixed (IRM: original 10-K assets with restated equity);
  5. the equity direction ignored NCI carried on unmapped partnership tags (BX, KKR).

Rule (pure, ``identity_amount``); every term comes from ONE filing, else no value (``planned hold``):
  * base: ``LiabilitiesAndStockholdersEquity`` of that filing when filed (the right side of the identity), else Assets;
  * total equity including NCI: the equity input when it is the NCI-inclusive tag, else the filed NCI-inclusive total,
    else parent equity + ``MinorityInterest``;
  * temporary equity: the including-NCI element when filed (it holds the redeemable NCI), else the parent line
    (``...AttributableToParent``, or the generic ``TemporaryEquityCarryingAmount`` when alone) + the redeemable NCI
    carrying amount (the total element, else the sum of its Common / Preferred / Other carrying components).
    Only CARRYING-AMOUNT elements are read: a carrying amount is a balance-sheet measure by definition. A redeemable
    NCI that appears only on FairValue / RedemptionValue elements (IPG) may or may not be the face line, so the cell
    is HELD, never guessed;
  * liabilities = base - total equity - temporary equity; parent equity (other direction) = base - liabilities - NCI
    - temporary equity, HELD unless ``MinorityInterest`` is filed in the same filing;
  * NCI carried on unmapped partnership elements (``PartnersCapital...NoncontrollingInterest``) holds both
    directions when no NCI total is read (BX, KKR).
Redeemable common of a SPAC sits in temporary equity, so it is outside liabilities; the per-share exit
(DC-SHARE-COUNT-DATE section 5) is a book-value-per-share rule and is not touched here.

The planner records which equity tag was the input. It replaces only rows that THIS fallback wrote (their
``source_fact_ids`` contain every source fact of the assets row and of the other term) and fills still-empty
cells; a value from a real Liabilities / StockholdersEquity tag is never touched. A held cell keeps its stored
value in this module (blanking needs the reason store, migration 0100) and is listed in the plan as ``hold``.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

RULE_ID = "balance.identity_equity_basis@1"
NCI_INCLUSIVE_EQUITY = (
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
)
NCI = "MinorityInterest"
TEMP_PARENT = "TemporaryEquityCarryingAmountAttributableToParent"
TEMP_INCL = (
    "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests"
)
TEMP_GENERIC = "TemporaryEquityCarryingAmount"
TEMP_REDEEMABLE_NCI = "RedeemableNoncontrollingInterestEquityCarryingAmount"
# components of the redeemable NCI when the total element is not filed (MCK: common; ETP: other)
TEMP_REDEEMABLE_PARTS = (
    "RedeemableNoncontrollingInterestEquityCommonCarryingAmount",
    "RedeemableNoncontrollingInterestEquityPreferredCarryingAmount",
    "RedeemableNoncontrollingInterestEquityOtherCarryingAmount",
)
# measurement-only elements: not read; alone they hold the cell (IPG: the face line is tagged FairValue)
TEMP_MEASURE_ONLY = (
    "RedeemableNoncontrollingInterestEquityFairValue",
    "RedeemableNoncontrollingInterestEquityCommonFairValue",
    "RedeemableNoncontrollingInterestEquityRedemptionValue",
    "RedeemableNoncontrollingInterestEquityCommonRedemptionValue",
    "RedeemableNoncontrollingInterestEquityPreferredRedemptionValue",
)
# NCI carried on partnership elements that are deliberately not mapped (BX, KKR): hold, do not map
NCI_UNREAD = (
    "PartnersCapitalAttributableToNoncontrollingInterest",
    "PartnersCapitalIncludingPortionAttributableToNoncontrollingInterest",
)
LSE = "LiabilitiesAndStockholdersEquity"
PARENT_EQUITY = "StockholdersEquity"
LIABILITIES_TAG = "Liabilities"
ASSETS_TAG = "Assets"
ADJUSTMENT_TAGS = (
    NCI,
    TEMP_PARENT,
    TEMP_INCL,
    TEMP_GENERIC,
    TEMP_REDEEMABLE_NCI,
    *TEMP_REDEEMABLE_PARTS,
)
LOAD_TAGS = (
    *ADJUSTMENT_TAGS,
    *TEMP_MEASURE_ONLY,
    *NCI_UNREAD,
    NCI_INCLUSIVE_EQUITY,
    LSE,
    PARENT_EQUITY,
    LIABILITIES_TAG,
)

LIABILITIES = "total_liabilities_resolved"
EQUITY = "stockholders_equity_resolved"
ASSETS = "total_assets_resolved"


@dataclass(frozen=True)
class Amount:
    value: Decimal
    basis: str  # what total equity / adjustments were used, e.g. "equity_nci_inclusive+temp_incl"
    equity_tag: str | None


@dataclass(frozen=True)
class Held:
    reason: str


def temporary_equity(adj: dict[str, Decimal]) -> tuple[Decimal, str] | Held:
    """Temporary equity (mezzanine) from carrying-amount elements of ONE filing; see the module doc."""
    if TEMP_INCL in adj:
        return adj[TEMP_INCL], "temp_incl"
    redeemable_parts = [adj[t] for t in TEMP_REDEEMABLE_PARTS if t in adj]
    if TEMP_REDEEMABLE_NCI in adj:
        rnci: Decimal | None = adj[TEMP_REDEEMABLE_NCI]
    elif redeemable_parts:
        rnci = sum(redeemable_parts, Decimal(0))
    else:
        rnci = None
    if rnci is None and any(adj.get(t) for t in TEMP_MEASURE_ONLY):
        return Held("redeemable_nci_measurement_only")
    parent = adj.get(TEMP_PARENT)
    if parent is None and TEMP_GENERIC in adj:
        if rnci is not None:
            return Held("temporary_equity_generic_overlaps_redeemable_nci")
        parent = adj[TEMP_GENERIC]
    if parent is None and rnci is None:
        return Decimal(0), ""
    if parent is not None and rnci is not None:
        return parent + rnci, "temp_parent+redeemable_nci"
    return (parent if parent is not None else rnci or Decimal(0)), "temp_one_line"


def identity_amount(
    target: str,
    base: Decimal,
    other: Decimal,
    other_tag: str | None,
    adj: dict[str, Decimal],
) -> Amount | Held:
    """``target`` is LIABILITIES (other = the equity input, ``other_tag`` its tag) or EQUITY (other = liabilities).
    ``base`` is the left side of the identity (L&SE when filed, else Assets)."""
    temp = temporary_equity(adj)
    if isinstance(temp, Held):
        return temp
    temp_value, temp_basis = temp
    tail = f"+{temp_basis}" if temp_basis else ""
    nci_unread = any(adj.get(t) for t in NCI_UNREAD)
    if target == LIABILITIES:
        if other_tag == NCI_INCLUSIVE_EQUITY:
            total_equity, basis = other, "equity_nci_inclusive"
        elif NCI_INCLUSIVE_EQUITY in adj:
            total_equity, basis = adj[NCI_INCLUSIVE_EQUITY], "filed_nci_inclusive_total"
        elif NCI in adj:
            total_equity, basis = other + adj[NCI], "parent_equity+nci"
        elif nci_unread:
            return Held("nci_on_unmapped_partnership_elements")
        else:
            total_equity, basis = other, "parent_equity_no_nci_filed"
        return Amount(base - total_equity - temp_value, basis + tail, other_tag)
    if NCI not in adj:
        return Held(
            "nci_on_unmapped_partnership_elements" if nci_unread else "nci_not_read"
        )
    return Amount(base - other - adj[NCI] - temp_value, "less_nci" + tail, other_tag)


@dataclass
class PlannedChange:
    company_id: int
    cik: str
    period_end: str
    concept: str
    before: str | None
    after: str | None  # None for a hold
    basis: str  # the equity/temporary-equity basis, or the hold reason
    equity_tag: str | None
    legacy_adjustment: str  # the adjustment the legacy SQL added
    kind: str  # replace | fill | hold
    period_id: int = 0
    source_fact_ids: tuple[int, ...] = ()
    filing_id: int | None = None

    def rel_change(self) -> Decimal | None:
        if self.before is None or self.after is None or Decimal(self.before) == 0:
            return None
        return abs(Decimal(self.after) - Decimal(self.before)) / abs(
            Decimal(self.before)
        )


def before_image_path() -> Path:
    """Where a run writes its before-image: SCROONER_BEFORE_IMAGE_DIR (default: the working directory)."""
    import os
    from datetime import UTC, datetime

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return (
        Path(os.environ.get("SCROONER_BEFORE_IMAGE_DIR", "."))
        / f"balance_identity_{stamp}.jsonl"
    )


def write_before_image(path: Path, plan: list[PlannedChange]) -> None:
    with path.open("w") as f:
        for p in plan:
            f.write(json.dumps(asdict(p), sort_keys=True) + "\n")


def _concept_ids(cur: Any, names: tuple[str, ...]) -> dict[str, int]:
    cur.execute(
        "select name, id from analytics.canonical_concept where name = any(%s)",
        (list(names),),
    )
    return {n: i for n, i in cur.fetchall()}


def plan_identity(
    conn: Any, company_ids: list[int], chunk: int = 100
) -> list[PlannedChange]:
    """Read-only. For each (company, instant) where the identity can be solved, the corrected value next to
    what is stored. ``replace`` = a row this fallback wrote whose value differs; ``fill`` = an empty cell;
    ``hold`` = the identity cannot be solved from one filing (reason in ``basis``); the stored value stays."""
    plan: list[PlannedChange] = []
    with conn.cursor() as cur:
        ids = _concept_ids(cur, (ASSETS, LIABILITIES, EQUITY))
        cur.execute(
            "select id, tag from core.concept where tag = any(%s)", (list(LOAD_TAGS),)
        )
        tag_id = {t: i for i, t in cur.fetchall()}
        cur.execute(
            "select id, cik from core.company where id = any(%s)", (company_ids,)
        )
        cik_of = dict(cur.fetchall())
    name_of = {v: k for k, v in tag_id.items()}
    for i in range(0, len(company_ids), chunk):
        part = company_ids[i : i + chunk]
        with conn.cursor() as cur:
            cur.execute(
                """select cf.company_id, cf.period_id, cf.canonical_concept_id, cf.value, cf.source_fact_ids, p.end_date
                   from analytics.canonical_fact cf join core.period p on p.id = cf.period_id
                   where cf.company_id = any(%s) and cf.canonical_concept_id = any(%s)""",
                (part, list(ids.values())),
            )
            cells: dict[tuple[int, int], dict[int, tuple[Decimal, list[int], Any]]] = {}
            for cid, pid, con, val, src, end in cur.fetchall():
                cells.setdefault((cid, pid), {})[con] = (val, list(src or []), end)
            # every filing's own copy of the adjustment / base elements (one value per filing, tag, instant)
            cur.execute(
                """select distinct on (f.company_id, f.period_id, f.filing_id, f.concept_id)
                          f.company_id, f.period_id, f.filing_id, f.concept_id, f.value, f.id
                   from core.fact f
                   where f.company_id = any(%s) and f.concept_id = any(%s)
                   order by f.company_id, f.period_id, f.filing_id, f.concept_id, f.id desc""",
                (part, list(tag_id.values())),
            )
            by_filing: dict[tuple[int, int, int], dict[str, tuple[Decimal, int]]] = {}
            for cid, pid, fil, con, val, fid in cur.fetchall():
                by_filing.setdefault((cid, pid, fil), {})[name_of[con]] = (val, fid)
            need = {
                s for c in cells.values() for _, (_, src, _) in c.items() for s in src
            }
            fact_info: dict[int, tuple[str, int]] = {}
            if need:
                cur.execute(
                    "select f.id, k.tag, f.filing_id from core.fact f join core.concept k on k.id = f.concept_id where f.id = any(%s)",
                    (sorted(need),),
                )
                fact_info = {fid: (tag, fil) for fid, tag, fil in cur.fetchall()}
        for (cid, pid), c in cells.items():
            if ids[ASSETS] not in c:
                continue
            a_val, a_src, end = c[ids[ASSETS]]
            for target, other in ((LIABILITIES, EQUITY), (EQUITY, LIABILITIES)):
                if ids[other] not in c:
                    continue
                o_val, o_src, _ = c[ids[other]]
                stored = c.get(ids[target])
                derived_row = (
                    stored is not None
                    and set(a_src) <= set(stored[1])
                    and set(o_src) <= set(stored[1])
                )
                if stored is not None and not derived_row:
                    continue  # a real tag-based value
                before = None if stored is None else str(stored[0])
                kind = "fill" if stored is None else "replace"
                filings = {fact_info[s][1] for s in a_src + o_src if s in fact_info}
                other_tag = None
                if target == LIABILITIES:
                    tags = {fact_info[s][0] for s in o_src if s in fact_info}
                    other_tag = (
                        NCI_INCLUSIVE_EQUITY
                        if NCI_INCLUSIVE_EQUITY in tags
                        else next(iter(sorted(tags)), None)
                    )

                def held(reason: str, fil: int | None = None) -> PlannedChange:
                    return PlannedChange(
                        cid, cik_of[cid], str(end), target, before, None, reason,
                        other_tag, "0", "hold", pid, tuple(a_src) + tuple(o_src), fil,
                    )  # fmt: skip

                if not filings:
                    plan.append(held("no_source_filing"))
                    continue
                if len(filings) > 1:
                    # mixed vintage (IRM: original 10-K assets, restated equity). The cell is solved inside the
                    # assets filing from that filing's OWN copy of the other term, else it is held.
                    a_filings = {fact_info[s][1] for s in a_src if s in fact_info}
                    if len(a_filings) != 1:
                        plan.append(held("mixed_vintage"))
                        continue
                    (fil,) = a_filings
                    own = by_filing.get((cid, pid, fil), {})
                    wanted = (
                        (PARENT_EQUITY, NCI_INCLUSIVE_EQUITY)
                        if target == LIABILITIES
                        else (LIABILITIES_TAG,)
                    )
                    found_tag = next((t for t in wanted if t in own), None)
                    if found_tag is None:
                        plan.append(held("mixed_vintage", fil))
                        continue
                    o_val, o_src = own[found_tag][0], [own[found_tag][1]]
                    other_tag = found_tag if target == LIABILITIES else None
                else:
                    (fil,) = filings
                same = by_filing.get((cid, pid, fil), {})
                adj = {t: v for t, (v, _) in same.items()}
                base = adj[LSE] if LSE in adj else a_val
                base_name = "lse" if LSE in adj else "assets"
                amt = identity_amount(target, base, o_val, other_tag, adj)
                if isinstance(amt, Held):
                    plan.append(held(amt.reason, fil))
                    continue
                legacy_adj = sum((adj.get(t, Decimal(0)) for t in (NCI, TEMP_PARENT, TEMP_INCL, TEMP_REDEEMABLE_NCI)), Decimal(0))  # fmt: skip
                if stored is not None and stored[0] == amt.value:
                    continue
                adj_fact_ids = sorted(fid for t, (_, fid) in same.items() if t in ADJUSTMENT_TAGS or t in (NCI_INCLUSIVE_EQUITY, LSE))  # fmt: skip
                plan.append(
                    PlannedChange(
                        cid, cik_of[cid], str(end), target, before, str(amt.value),
                        f"{amt.basis}+base_{base_name}", amt.equity_tag, str(legacy_adj), kind, pid,
                        tuple(a_src) + tuple(o_src) + tuple(adj_fact_ids), fil,
                    )
                )  # fmt: skip
    return plan


def apply_identity(conn: Any, plan: list[PlannedChange], before_image: Path) -> int:
    """Write the plan (rule on only): update the rows this fallback wrote, insert the empty cells. One
    transaction; the before-image is written first. Delete scope: none."""
    write_before_image(before_image, plan)
    if not plan:
        return 0
    n = 0
    with conn.cursor() as cur:
        ids = _concept_ids(cur, (ASSETS, LIABILITIES, EQUITY))
        for p in plan:
            if p.kind == "hold":
                continue  # the stored value stays; blanking needs the reason store
            if p.kind == "replace":
                cur.execute(
                    """update analytics.canonical_fact set value = %s, source_fact_ids = %s
                       where company_id = %s and canonical_concept_id = %s and period_id = %s""",
                    (
                        p.after,
                        list(p.source_fact_ids),
                        p.company_id,
                        ids[p.concept],
                        p.period_id,
                    ),
                )
            else:
                cur.execute(
                    """insert into analytics.canonical_fact
                           (company_id, canonical_concept_id, period_id, value, source_fact_ids)
                       values (%s, %s, %s, %s, %s)
                       on conflict (company_id, canonical_concept_id, period_id) do nothing""",
                    (
                        p.company_id,
                        ids[p.concept],
                        p.period_id,
                        p.after,
                        list(p.source_fact_ids),
                    ),
                )
            n += cur.rowcount
    conn.commit()
    return n
