"""Deterministic, evidence-aware production universe policy.

The source rows come from SEC submissions/ticker metadata plus the existing
OpenFIGI security classification. SEC does not publish a universal corporate
security identifier, so ``core.security`` uses an internal durable identity
and records how it was bootstrapped. Unknown evidence produces ``uncertain``;
absence of evidence is never treated as a negative fact.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from datetime import date
from typing import Iterable

import psycopg
import structlog
from psycopg.types.json import Jsonb

logger = structlog.get_logger()

POLICY_VERSION = "2026-08-18.v1"

ELIGIBLE = "eligible"
EXCLUDED = "excluded"
UNCERTAIN = "uncertain"

# Current SEC exchange labels plus conservative aliases. Only national
# securities exchanges in the locked MVP policy are eligible. OTC is a
# quotation venue and is explicitly outside this universe.
_EXCHANGE_PRIORITY = {
    "nyse": 10,
    "new york stock exchange": 10,
    "nasdaq": 20,
    "nasdaq global select market": 20,
    "nasdaq global market": 20,
    "nasdaq capital market": 20,
    "nyse american": 30,
    "nyse arca": 40,
    "cboe bzx": 50,
    "cboe bzx exchange": 50,
}
_NON_NATIONAL_MARKERS = ("otc", "pink", "grey market")

_DOMESTIC_FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A"}
_FOREIGN_FORMS = {"20-F", "20-F/A"}
_MJDS_FORMS = {"40-F", "40-F/A"}
_REGISTERED_FUND_FORMS = {
    "N-1A",
    "N-2",
    "N-3",
    "N-4",
    "N-6",
    "N-CSR",
    "N-CSRS",
    "N-PORT",
    "S-6",
}


@dataclass(frozen=True)
class UniverseCandidate:
    company_id: int
    filer_id: int
    security_id: int
    listing_id: int
    cik: str
    ticker: str
    exchange: str | None
    security_type: str | None
    company_status: str | None
    sic_code: str | None = None
    filing_forms: tuple[str, ...] = ()
    registered_fund_confirmed: bool = False
    spac_or_shell_confirmed: bool = False
    issuer_kind: str | None = None


@dataclass(frozen=True)
class UniverseDecision:
    company_id: int
    filer_id: int
    security_id: int
    listing_id: int
    cik: str
    ticker: str
    exchange: str | None
    eligibility_status: str
    reason_codes: tuple[str, ...]
    is_primary: bool = False
    decision_order: int = 0


def _normal(value: str | None) -> str:
    return " ".join((value or "").strip().lower().replace("-", " ").split())


def exchange_priority(exchange: str | None) -> int | None:
    return _EXCHANGE_PRIORITY.get(_normal(exchange))


def classify_filing_regime(forms: Iterable[str]) -> str:
    normalized = {form.upper() for form in forms}
    if normalized & _REGISTERED_FUND_FORMS:
        return "registered_fund"
    if normalized & _MJDS_FORMS:
        return "canadian_mjds"
    if normalized & _FOREIGN_FORMS:
        return "foreign_private_issuer"
    if normalized & _DOMESTIC_FORMS:
        return "domestic_reporting_company"
    return "unknown"


def classify_security_type(security_type: str | None) -> str:
    value = _normal(security_type)
    if not value:
        return "unknown"
    if value in {"common stock", "ordinary shares", "reit"}:
        return "common_equity"
    if value in {"adr", "american depositary receipt", "depositary receipt"}:
        return "adr"
    if "preferred" in value or "preference" in value:
        return "preferred"
    if "warrant" in value or value == "right":
        return "warrant_or_right"
    if value == "unit" or value.endswith(" units"):
        return "unit"
    if any(marker in value for marker in ("etp", "etf", "fund", "investment trust")):
        return "registered_or_exchange_traded_fund"
    if any(marker in value for marker in ("bond", "debt", "note", "etn")):
        return "debt"
    if value in {"cdi", "chess depositary interest"}:
        return "foreign_depositary_interest"
    return "other"


def _sector_reason(candidate: UniverseCandidate) -> str | None:
    if candidate.issuer_kind in {"bank", "insurer", "reit", "bdc"}:
        return f"eligible_operating_structure:{candidate.issuer_kind}"
    try:
        sic = int(candidate.sic_code or "")
    except ValueError:
        return None
    if 6000 <= sic <= 6099:
        return "eligible_operating_structure:bank"
    if 6311 <= sic <= 6411:
        return "eligible_operating_structure:insurer"
    if sic == 6798:
        return "eligible_operating_structure:reit"
    return None


def evaluate_candidate(candidate: UniverseCandidate) -> UniverseDecision:
    reasons: list[str] = []
    excluded = False
    uncertain = False

    regime = classify_filing_regime(candidate.filing_forms)
    security_family = classify_security_type(candidate.security_type)
    exchange_name = _normal(candidate.exchange)

    if candidate.company_status == "delisted":
        excluded = True
        reasons.append("excluded_company_delisted")
    elif candidate.company_status in {"stale", "unknown", None}:
        uncertain = True
        reasons.append(
            f"uncertain_company_status:{candidate.company_status or 'missing'}"
        )

    if candidate.registered_fund_confirmed or regime == "registered_fund":
        excluded = True
        reasons.append("excluded_registered_fund")

    if candidate.spac_or_shell_confirmed:
        excluded = True
        reasons.append("excluded_spac_or_shell_confirmed")
    elif candidate.sic_code == "6770":
        uncertain = True
        reasons.append("uncertain_blank_check_sic_requires_confirmation")

    excluded_security_reasons = {
        "preferred": "excluded_preferred_security",
        "warrant_or_right": "excluded_warrant_or_right",
        "unit": "excluded_unit",
        "registered_or_exchange_traded_fund": "excluded_fund_security",
        "debt": "excluded_debt_or_etn",
    }
    if security_family in excluded_security_reasons:
        excluded = True
        reasons.append(excluded_security_reasons[security_family])
    elif security_family == "adr":
        uncertain = True
        reasons.append("uncertain_adr_scope_decision_open")
    elif security_family == "foreign_depositary_interest":
        uncertain = True
        reasons.append("uncertain_foreign_depositary_interest")
    elif security_family in {"unknown", "other"}:
        uncertain = True
        reasons.append(f"uncertain_security_type:{security_family}")
    else:
        reasons.append("eligible_common_equity")

    if exchange_priority(candidate.exchange) is not None:
        reasons.append("eligible_us_national_exchange")
    elif not exchange_name:
        uncertain = True
        reasons.append("uncertain_exchange_missing")
    elif any(marker in exchange_name for marker in _NON_NATIONAL_MARKERS):
        excluded = True
        reasons.append("excluded_non_national_exchange")
    else:
        uncertain = True
        reasons.append("uncertain_exchange_unrecognized")

    if regime in {"foreign_private_issuer", "canadian_mjds"}:
        uncertain = True
        reasons.append(f"uncertain_foreign_filer_scope_open:{regime}")
    elif regime == "unknown":
        uncertain = True
        reasons.append("uncertain_filing_regime")
    elif regime == "domestic_reporting_company":
        reasons.append("eligible_domestic_reporting_company")

    sector_reason = _sector_reason(candidate)
    if sector_reason:
        reasons.append(sector_reason)

    status = EXCLUDED if excluded else UNCERTAIN if uncertain else ELIGIBLE
    return UniverseDecision(
        company_id=candidate.company_id,
        filer_id=candidate.filer_id,
        security_id=candidate.security_id,
        listing_id=candidate.listing_id,
        cik=candidate.cik,
        ticker=candidate.ticker,
        exchange=candidate.exchange,
        eligibility_status=status,
        reason_codes=tuple(dict.fromkeys(reasons)),
    )


def build_snapshot(candidates: Iterable[UniverseCandidate]) -> list[UniverseDecision]:
    decisions = [evaluate_candidate(candidate) for candidate in candidates]
    decisions.sort(key=lambda row: (row.cik, row.ticker, row.listing_id))

    by_company: dict[int, list[int]] = defaultdict(list)
    for index, decision in enumerate(decisions):
        if decision.eligibility_status == ELIGIBLE:
            by_company[decision.company_id].append(index)

    for indexes in by_company.values():
        best_priority = min(
            exchange_priority(decisions[i].exchange) or 999 for i in indexes
        )
        best = [
            i
            for i in indexes
            if exchange_priority(decisions[i].exchange) == best_priority
        ]
        if len(best) == 1:
            primary_index = best[0]
            row = decisions[primary_index]
            decisions[primary_index] = replace(
                row,
                is_primary=True,
                reason_codes=(
                    *row.reason_codes,
                    "primary_selected_by_exchange_priority",
                ),
            )
            for index in indexes:
                if index != primary_index:
                    row = decisions[index]
                    decisions[index] = replace(
                        row,
                        reason_codes=(*row.reason_codes, "eligible_secondary_listing"),
                    )
        else:
            for index in best:
                row = decisions[index]
                decisions[index] = replace(
                    row,
                    reason_codes=(
                        *row.reason_codes,
                        "primary_ambiguous_multiple_share_classes",
                    ),
                )

    return [
        replace(row, decision_order=index + 1) for index, row in enumerate(decisions)
    ]


def ensure_universe_identities(conn: psycopg.Connection) -> None:
    """Backfill new identities for rows created after migration 0016."""
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into core.filer (company_id, cik)
            select id, cik from core.company
            on conflict (cik) do update set company_id = excluded.company_id
            """
        )
        cur.execute(
            """
            insert into core.security
                (company_id, source_key, security_type, classification_source)
            select
                company_id, 'listing:' || id::text, security_type,
                coalesce(security_type_source, 'unclassified')
            from core.listing
            on conflict (source_key) do update
            set security_type = excluded.security_type,
                classification_source = excluded.classification_source
            """
        )
        cur.execute(
            """
            update core.listing l
               set security_id = s.id
              from core.security s
             where s.source_key = 'listing:' || l.id::text
               and l.security_id is distinct from s.id
            """
        )
    conn.commit()


def load_current_candidates(conn: psycopg.Connection) -> list[UniverseCandidate]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select
                c.id, fi.id, s.id, l.id, c.cik, l.ticker, l.exchange,
                coalesce(s.security_type, l.security_type), c.status, c.sic_code,
                coalesce(array_agg(distinct f.form) filter (where f.form is not null), '{}')
            from core.company c
            join core.filer fi on fi.company_id = c.id
            join core.listing l on l.company_id = c.id and l.effective_to is null
            join core.security s on s.id = l.security_id
            left join core.filing f on f.company_id = c.id
            group by c.id, fi.id, s.id, l.id
            order by c.cik, l.ticker, l.id
            """
        )
        return [
            UniverseCandidate(
                company_id=row[0],
                filer_id=row[1],
                security_id=row[2],
                listing_id=row[3],
                cik=row[4],
                ticker=row[5],
                exchange=row[6],
                security_type=row[7],
                company_status=row[8],
                sic_code=row[9],
                filing_forms=tuple(sorted(row[10])),
            )
            for row in cur.fetchall()
        ]


def persist_snapshot(
    conn: psycopg.Connection, as_of: date, decisions: list[UniverseDecision]
) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into core.universe_snapshot (as_of, policy_version)
            values (%s, %s)
            on conflict (as_of, policy_version) do update set created_at = now()
            returning id
            """,
            (as_of, POLICY_VERSION),
        )
        snapshot_id = cur.fetchone()[0]
        cur.execute(
            "delete from core.universe_member where snapshot_id = %s", (snapshot_id,)
        )
        if decisions:
            cur.executemany(
                """
                insert into core.universe_member
                    (snapshot_id, company_id, filer_id, security_id, listing_id,
                     eligibility_status, reason_codes, is_primary, decision_order)
                values
                    (%(snapshot_id)s, %(company_id)s, %(filer_id)s, %(security_id)s,
                     %(listing_id)s, %(eligibility_status)s, %(reason_codes)s,
                     %(is_primary)s, %(decision_order)s)
                """,
                [
                    {
                        "snapshot_id": snapshot_id,
                        "company_id": row.company_id,
                        "filer_id": row.filer_id,
                        "security_id": row.security_id,
                        "listing_id": row.listing_id,
                        "eligibility_status": row.eligibility_status,
                        "reason_codes": Jsonb(row.reason_codes),
                        "is_primary": row.is_primary,
                        "decision_order": row.decision_order,
                    }
                    for row in decisions
                ],
            )
    conn.commit()
    return snapshot_id


def build_current_universe(conn: psycopg.Connection, as_of: date | None = None) -> dict:
    as_of = as_of or date.today()
    if as_of != date.today():
        raise ValueError(
            "current universe snapshots can only be built for today; "
            "use an already-persisted snapshot for historical screening"
        )
    ensure_universe_identities(conn)
    decisions = build_snapshot(load_current_candidates(conn))
    snapshot_id = persist_snapshot(conn, as_of, decisions)
    counts = Counter(row.eligibility_status for row in decisions)
    stats = {
        "snapshot_id": snapshot_id,
        "as_of": as_of.isoformat(),
        "policy_version": POLICY_VERSION,
        "candidates": len(decisions),
        "eligible": counts[ELIGIBLE],
        "excluded": counts[EXCLUDED],
        "uncertain": counts[UNCERTAIN],
        "primary": sum(row.is_primary for row in decisions),
    }
    logger.info("company_universe.snapshot_built", **stats)
    return stats
