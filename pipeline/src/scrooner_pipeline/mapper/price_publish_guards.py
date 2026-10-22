"""Price-metric publish guards: market-cap share basis (RF-15) and reporting currency (RF-19).

Both only HIDE (value None with a visible ``is_null_reason`` on the metric row, which is where
metric_value keeps its reason); neither corrects a value.

``mcap.share_basis_guard@1`` (WO-21, T4). Market cap = shares x USD price. Hidden, with the
four share-dependent ratios, when the share basis is not established:
  * ``shares_scale_conflict``: the chosen share count is 200x or more away from an independent
    observation of the same company's shares (the cover-page count in
    ``core.shares_outstanding_fallback``, the median of its instant share counts, the median of
    its weighted-average counts). RPAY: weighted average 83,285,379,000 chosen over a cover count
    of 85,881,082 (ratio 970); TBLA: 290,505,359,000 against a history near 300M (x1000).
  * ``ads_ratio_unverified``: the company's price is per ADS but its share facts are ordinary
    shares (AKTX 155.8B ordinary shares x an 8.76 ADS price = USD 1.36T). The ADS ratio list is the
    Standardization Lead's input (WO-21); until it exists this is a company-scoped hold with
    label ASSUMED (WO-ADDENDA AT-21.1), not a correction.
``currency.non_usd_price_ratio@1`` (WO-28, E15). A non-USD reporter (no USD-unit fact among its
balance-sheet and income-statement tags in its latest periodic filing) has statement values in
another currency; a ratio of a USD price to them is meaningless. Hidden: P/E, P/S, P/B, dividend
yield, FCF yield. Market cap (shares x USD price) is unaffected. EV multiples live in
``expanded_metrics`` and are NOT covered here (untested scope).

Flags (SCROONER_RULES_ENABLED), default OFF = no-op. ``plan_price_guards`` is the dry run: it reads
the stored latest TTM rows and writes nothing.
"""

from __future__ import annotations

import statistics
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.rule_before_image import PlannedChange
from scrooner_pipeline.common.rules_enabled import is_enabled

logger = structlog.get_logger()

RULE_MCAP = "mcap.share_basis_guard@1"
RULE_CCY = "currency.non_usd_price_ratio@1"
SCALE_FACTOR = Decimal(200)

MARKET_CAP_DEPENDENTS = ("price_to_sales", "price_to_book", "fcf_yield")
CURRENCY_HIDDEN = (
    "trailing_pe",
    "price_to_sales",
    "price_to_book",
    "dividend_yield",
    "fcf_yield",
)

# Company-scoped holds (hide-only). Evidence label ASSUMED: WO-ADDENDA AT-21.1 lists these as
# "ADS ratio or x1000 WASO"; the ADS ratio itself is not in our data. RPAY and TBLA are NOT here:
# the scale test catches them from data.
ADS_HOLDS: dict[str, str] = {
    "0001541157": "AKTX: ADS price against ordinary-share facts (155.8B shares x 8.76)",
    "0001704292": "ZLAB: ADS price against ordinary-share facts",
    "0001611747": "SCNI: ADS price against ordinary-share facts",
    "0001075880": "KZIA: ADS price against ordinary-share facts",
    "0001613780": "DBVT: ADS price against ordinary-share facts",
    "0001888886": "GPCR: ADS price against ordinary-share facts",
    "0000897448": "AMRN: listed in WO-ADDENDA AT-21.1; ratio not verified",
}


def ratio_out_of_bounds(chosen: Decimal, observed: Decimal) -> bool:
    if chosen <= 0 or observed <= 0:
        return False
    ratio = chosen / observed
    return ratio >= SCALE_FACTOR or ratio <= 1 / SCALE_FACTOR


@dataclass(frozen=True)
class ShareObservations:
    cover_fallback: Decimal | None
    instant_median: Decimal | None
    weighted_median: Decimal | None

    def labelled(self) -> list[tuple[str, Decimal]]:
        out = []
        if self.cover_fallback is not None:
            out.append(("cover_page", self.cover_fallback))
        if self.instant_median is not None:
            out.append(("instant_median", self.instant_median))
        if self.weighted_median is not None:
            out.append(("weighted_median", self.weighted_median))
        return out


def share_basis_reason(
    cik: str, chosen: Decimal | None, obs: ShareObservations
) -> str | None:
    """Reason code to hide market cap, or None."""
    if cik in ADS_HOLDS:
        return "ads_ratio_unverified"
    if chosen is None:
        return None
    for label, value in obs.labelled():
        if ratio_out_of_bounds(chosen, value):
            return f"shares_scale_conflict:{label}"
    return None


def median_of(values: Iterable[Decimal]) -> Decimal | None:
    v = sorted(x for x in values if x > 0)
    return Decimal(statistics.median(v)) if v else None


def reporting_currency_from_units(units: Iterable[str]) -> str:
    """'USD' when any USD-unit fact exists, else the first ISO-like currency unit, else 'USD'
    (unknown is not hidden: no evidence of a non-USD reporter)."""
    seen = {u.lower() for u in units}
    if "usd" in seen or not seen:
        return "USD"
    iso = sorted(u for u in seen if len(u) == 3 and u.isalpha())
    return iso[0].upper() if iso else "USD"


# ---------------------------------------------------------------- database layer
_INSTANT_TAGS = ("EntityCommonStockSharesOutstanding", "CommonStockSharesOutstanding")
_WEIGHTED_TAGS = (
    "WeightedAverageNumberOfDilutedSharesOutstanding",
    "WeightedAverageNumberOfSharesOutstandingBasic",
)
_CCY_TAGS = (
    "Assets",
    "Liabilities",
    "StockholdersEquity",
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "NetIncomeLoss",
)
_PERIODIC = ("10-K", "10-K/A", "10-KT", "10-Q", "10-Q/A")


def load_share_observations(
    conn: psycopg.Connection, company_id: int, exclude_fact_ids: Sequence[int] = ()
) -> ShareObservations:
    with conn.cursor() as cur:
        cur.execute(
            "select shares from core.shares_outstanding_fallback where company_id = %s",
            (company_id,),
        )
        row = cur.fetchone()
        cover = row[0] if row else None
        cur.execute(
            """
            select co.tag, f.value
            from core.fact f
            join core.concept co on co.id = f.concept_id
            join core.period p on p.id = f.period_id
            where f.company_id = %s and co.tag = any(%s) and f.value > 0
              and not (f.id = any(%s))
              and p.end_date >= current_date - interval '3 years'
            """,
            (company_id, list(_INSTANT_TAGS + _WEIGHTED_TAGS), list(exclude_fact_ids)),
        )
        inst: list[Decimal] = []
        wavg: list[Decimal] = []
        for tag, value in cur.fetchall():
            (inst if tag in _INSTANT_TAGS else wavg).append(value)
    return ShareObservations(cover, median_of(inst), median_of(wavg))


def load_reporting_currency(conn: psycopg.Connection, company_id: int) -> str:
    """Units of the statement tags in the company's latest periodic filing that has any."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select u.unit_name
            from core.fact f
            join core.concept co on co.id = f.concept_id and co.taxonomy = 'us-gaap' and co.tag = any(%s)
            join core.unit u on u.id = f.unit_id
            join core.filing fl on fl.id = f.filing_id and fl.form = any(%s)
            where f.company_id = %s
              and fl.id = (
                  select fl2.id from core.fact f2
                  join core.concept c2 on c2.id = f2.concept_id and c2.taxonomy = 'us-gaap' and c2.tag = any(%s)
                  join core.filing fl2 on fl2.id = f2.filing_id and fl2.form = any(%s)
                  where f2.company_id = %s
                  order by fl2.filing_date desc, fl2.id desc limit 1)
            """,
            (
                list(_CCY_TAGS),
                list(_PERIODIC),
                company_id,
                list(_CCY_TAGS),
                list(_PERIODIC),
                company_id,
            ),
        )
        return reporting_currency_from_units(r[0] for r in cur.fetchall())


def apply_price_publish_guards(
    conn: psycopg.Connection,
    company_id: int,
    cik: str | None,
    rows: list[dict[str, Any]],
    metric_names: Mapping[int, str],
    shares_hit: tuple[Decimal, list[int]] | None,
    *,
    environ: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Live hook (called by price_metrics before it writes). No-op, zero queries, when both
    flags are off. ``rows`` are the metric_value dicts; hidden rows keep their identity and get
    value None plus a ``guard:`` reason."""
    mcap_on = is_enabled(RULE_MCAP, environ)
    ccy_on = is_enabled(RULE_CCY, environ)
    if not (mcap_on or ccy_on):
        return rows
    by_name = {metric_names[r["metric_definition_id"]]: r for r in rows}
    hide: dict[str, str] = {}
    if cik is None:
        with conn.cursor() as cur:
            cur.execute("select cik from core.company where id = %s", (company_id,))
            row = cur.fetchone()
            cik = row[0] if row else ""
    if (
        mcap_on
        and "market_cap" in by_name
        and by_name["market_cap"]["value"] is not None
    ):
        chosen = shares_hit[0] if shares_hit else None
        obs = load_share_observations(
            conn, company_id, shares_hit[1] if shares_hit else ()
        )
        why = share_basis_reason(cik, chosen, obs)
        if why:
            mc_fids = set(by_name["market_cap"]["source_fact_ids"] or [])
            hide["market_cap"] = f"guard:{why}"
            for m in MARKET_CAP_DEPENDENTS:
                if m in by_name:
                    hide[m] = f"guard:{why}"
            pe = by_name.get("trailing_pe")
            if pe is not None and mc_fids & set(pe["source_fact_ids"] or []):
                hide["trailing_pe"] = f"guard:{why}"
    if ccy_on:
        ccy = load_reporting_currency(conn, company_id)
        if ccy != "USD":
            for m in CURRENCY_HIDDEN:
                if m in by_name and m not in hide:
                    hide[m] = f"guard:non_usd_reporter:{ccy}"
    for name, reason in hide.items():
        by_name[name]["value"] = None
        by_name[name]["is_null_reason"] = reason
    return rows


def plan_price_guards(conn: psycopg.Connection, ciks: set[str]) -> list[PlannedChange]:
    """Dry run over the STORED latest TTM rows; evaluates both rules as ON, writes nothing."""
    out: list[PlannedChange] = []
    with conn.cursor() as cur:
        cur.execute(
            "select id, cik from core.company where cik = any(%s)", (sorted(ciks),)
        )
        companies = cur.fetchall()
    for company_id, cik in companies:
        with conn.cursor() as cur:
            cur.execute(
                """
                select distinct on (md.metric_name) md.metric_name, mv.value, mv.period_end, mv.source_fact_ids
                from analytics.metric_value mv
                join analytics.metric_definition md on md.id = mv.metric_definition_id
                where mv.company_id = %s and mv.period_label = 'TTM'
                  and md.metric_name = any(%s)
                order by md.metric_name, mv.period_end desc
                """,
                (
                    company_id,
                    [
                        "market_cap",
                        *MARKET_CAP_DEPENDENTS,
                        "trailing_pe",
                        "dividend_yield",
                    ],
                ),
            )
            stored = {n: (v, e, s) for n, v, e, s in cur.fetchall()}
            share_fact = None
            mc = stored.get("market_cap")
            if mc and mc[2]:
                cur.execute("select value from core.fact where id = %s", (mc[2][0],))
                r = cur.fetchone()
                share_fact = (r[0], list(mc[2])) if r else None
        if mc and mc[0] is not None:
            obs = load_share_observations(
                conn, company_id, share_fact[1] if share_fact else ()
            )
            why = share_basis_reason(cik, share_fact[0] if share_fact else None, obs)
            if why:
                for name in ("market_cap", *MARKET_CAP_DEPENDENTS):
                    if name in stored and stored[name][0] is not None:
                        out.append(
                            _change(cik, company_id, name, stored[name], RULE_MCAP, why)
                        )
        ccy = load_reporting_currency(conn, company_id)
        if ccy != "USD":
            for name in CURRENCY_HIDDEN:
                if name in stored and stored[name][0] is not None:
                    out.append(
                        _change(
                            cik,
                            company_id,
                            name,
                            stored[name],
                            RULE_CCY,
                            f"non_usd_reporter:{ccy}",
                        )
                    )
    return out


def _change(
    cik: str,
    company_id: int,
    name: str,
    stored: tuple[Decimal, date, Any],
    rule: str,
    why: str,
) -> PlannedChange:
    return PlannedChange(
        rule, cik, company_id, name, stored[1], stored[0], None, f"guard:{why}"
    )
