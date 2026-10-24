"""Balance-sheet identity fallback, corrected (rule ``balance.identity_equity_basis@1``).

The legacy SQL in ``concept_fallback.resolve_balance_sheet_identity_fallback`` computed

    total_liabilities = Assets - StockholdersEquity + (MinorityInterest + temporary equity)

but the identity is  Assets = Liabilities + total equity (parent + NCI) + temporary equity, so the adjustments
must be SUBTRACTED. Two defects (found by the derivation catalog, 2026-10-24):
  1. sign: the adjustment was added (WMT 2026-07-31 stored 202,237M, filing 189,115M, 0000104169-26-000154 R4);
  2. double count: ``stockholders_equity`` priority 2 is the NCI-inclusive tag; when the equity input is that
     tag the NCI is already inside it (AT&T 2026-06-30 stored 319,920M, filing 299,920M, 0000732717-26-000297 R5).

Rule here (pure, ``identity_amount``):
  * total equity including NCI: the equity input when it came from the NCI-inclusive tag, else the filed
    NCI-inclusive total for the same instant when there is one, else parent equity + ``MinorityInterest``;
  * temporary equity: ``TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterest`` when
    filed (it already holds the redeemable NCI), else ``...AttributableToParent`` + ``RedeemableNoncontrollingInterest...``;
  * liabilities = Assets - total equity - temporary equity.
  * parent equity (the other direction) = Assets - Liabilities - NCI - temporary equity, same adjustment terms.
Redeemable common of a SPAC sits in temporary equity, so it is correctly outside liabilities; the per-share exit
(DC-SHARE-COUNT-DATE section 5) is a book-value-per-share rule and is not touched here.

The planner records which equity tag was the input. It replaces only rows that THIS fallback wrote (their
``source_fact_ids`` contain every source fact of the assets row and of the other term) and fills still-empty
cells; a value from a real Liabilities / StockholdersEquity tag is never touched.
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
    "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterest"
)
TEMP_REDEEMABLE_NCI = "RedeemableNoncontrollingInterestEquityCarryingAmount"
ADJUSTMENT_TAGS = (NCI, TEMP_PARENT, TEMP_INCL, TEMP_REDEEMABLE_NCI)
LOAD_TAGS = (*ADJUSTMENT_TAGS, NCI_INCLUSIVE_EQUITY)

LIABILITIES = "total_liabilities_resolved"
EQUITY = "stockholders_equity_resolved"
ASSETS = "total_assets_resolved"


@dataclass(frozen=True)
class Amount:
    value: Decimal
    basis: str  # what total equity / adjustments were used, e.g. "equity_nci_inclusive+temp_incl"
    equity_tag: str | None


def temporary_equity(adj: dict[str, Decimal]) -> tuple[Decimal, str]:
    if TEMP_INCL in adj:
        return adj[TEMP_INCL], "temp_incl"
    parts = [adj[t] for t in (TEMP_PARENT, TEMP_REDEEMABLE_NCI) if t in adj]
    if not parts:
        return Decimal(0), ""
    return sum(parts, Decimal(0)), "temp_parent+redeemable_nci" if len(
        parts
    ) == 2 else "temp_one_line"


def identity_amount(
    target: str,
    assets: Decimal,
    other: Decimal,
    other_tag: str | None,
    adj: dict[str, Decimal],
) -> Amount:
    """``target`` is LIABILITIES (other = the equity input, ``other_tag`` its tag) or EQUITY (other = liabilities)."""
    temp, temp_basis = temporary_equity(adj)
    tail = f"+{temp_basis}" if temp_basis else ""
    if target == LIABILITIES:
        if other_tag == NCI_INCLUSIVE_EQUITY:
            total_equity, basis = other, "equity_nci_inclusive"
        elif NCI_INCLUSIVE_EQUITY in adj:
            total_equity, basis = adj[NCI_INCLUSIVE_EQUITY], "filed_nci_inclusive_total"
        elif NCI in adj:
            total_equity, basis = other + adj[NCI], "parent_equity+nci"
        else:
            total_equity, basis = other, "parent_equity_no_nci_filed"
        return Amount(assets - total_equity - temp, basis + tail, other_tag)
    nci = adj.get(NCI, Decimal(0))
    basis = "less_nci" if NCI in adj else "no_nci_filed"
    return Amount(assets - other - nci - temp, basis + tail, other_tag)


@dataclass
class PlannedChange:
    company_id: int
    cik: str
    period_end: str
    concept: str
    before: str | None
    after: str
    basis: str
    equity_tag: str | None
    legacy_adjustment: str  # the adjustment the legacy SQL added
    kind: str  # replace | fill
    period_id: int = 0
    source_fact_ids: tuple[int, ...] = ()

    def rel_change(self) -> Decimal | None:
        if self.before is None or Decimal(self.before) == 0:
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
    what is stored. ``replace`` = a row this fallback wrote whose value differs; ``fill`` = an empty cell."""
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
            cur.execute(
                """select distinct on (f.company_id, f.period_id, f.concept_id)
                          f.company_id, f.period_id, f.concept_id, f.value, f.id from core.fact f
                   where f.company_id = any(%s) and f.concept_id = any(%s) and f.is_authoritative
                   order by f.company_id, f.period_id, f.concept_id, f.id desc""",
                (part, list(tag_id.values())),
            )
            name_of = {v: k for k, v in tag_id.items()}
            adjs: dict[tuple[int, int], dict[str, Decimal]] = {}
            adj_ids: dict[tuple[int, int], dict[str, int]] = {}
            for cid, pid, con, val, fid in cur.fetchall():
                adjs.setdefault((cid, pid), {})[name_of[con]] = (
                    val  # one fact per tag (latest authoritative)
                )
                adj_ids.setdefault((cid, pid), {})[name_of[con]] = fid
            need = {
                s for c in cells.values() for _, (_, src, _) in c.items() for s in src
            }
            tag_of_fact: dict[int, str] = {}
            if need:
                cur.execute(
                    "select f.id, k.tag from core.fact f join core.concept k on k.id = f.concept_id where f.id = any(%s)",
                    (sorted(need),),
                )
                tag_of_fact = dict(cur.fetchall())
        for (cid, pid), c in cells.items():
            if ids[ASSETS] not in c:
                continue
            a_val, a_src, end = c[ids[ASSETS]]
            adj = adjs.get((cid, pid), {})
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
                other_tag = None
                if target == LIABILITIES:
                    tags = {tag_of_fact.get(s) for s in o_src}
                    other_tag = (
                        NCI_INCLUSIVE_EQUITY
                        if NCI_INCLUSIVE_EQUITY in tags
                        else next(iter(sorted(t for t in tags if t)), None)
                    )
                amt = identity_amount(target, a_val, o_val, other_tag, adj)
                legacy_adj = sum(
                    (adj.get(t, Decimal(0)) for t in ADJUSTMENT_TAGS), Decimal(0)
                )
                if stored is not None and stored[0] == amt.value:
                    continue
                plan.append(
                    PlannedChange(
                        cid,
                        cik_of[cid],
                        str(end),
                        target,
                        None if stored is None else str(stored[0]),
                        str(amt.value),
                        amt.basis,
                        amt.equity_tag,
                        str(legacy_adj),
                        "fill" if stored is None else "replace",
                        pid,
                        tuple(a_src)
                        + tuple(o_src)
                        + tuple(sorted(adj_ids.get((cid, pid), {}).values())),
                    )
                )
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
