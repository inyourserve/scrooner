"""Day 7 stratified-pilot selection and fail-closed readiness checks.

This module is intentionally read-only. It decides whether a 100-company
write-heavy pipeline run is safe and builds a deterministic sample manifest
from an already-approved Day 6 universe. It never bypasses universe,
coverage, dead-letter, or database-capacity gates.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Iterable

import psycopg

from scrooner_pipeline.company_master.universe import classify_filing_regime
from scrooner_pipeline.mapper.concepts import CONCEPT_MAPPINGS

DEFAULT_DATABASE_LIMIT_BYTES = 500 * 1024 * 1024
MAPPING_COVERAGE_GATE = Decimal("0.95")

FAILURE_CATEGORIES = {
    "code_defect",
    "mapping_gap",
    "unavailable_filing_data",
    "universe_error",
    "expected_structural_null",
    "upstream_source_failure",
    "unreviewed",
}


@dataclass(frozen=True)
class PilotCandidate:
    cik: str
    sector: str
    market_cap_band: str
    fiscal_calendar: str
    filing_regime: str
    issuer_kind: str
    multi_class: bool
    has_amendment: bool

    def strata(self) -> tuple[tuple[str, str], ...]:
        return (
            ("sector", self.sector),
            ("market_cap_band", self.market_cap_band),
            ("fiscal_calendar", self.fiscal_calendar),
            ("filing_regime", self.filing_regime),
            ("issuer_kind", self.issuer_kind),
            ("multi_class", str(self.multi_class).lower()),
            ("has_amendment", str(self.has_amendment).lower()),
        )


@dataclass(frozen=True)
class PilotInventory:
    universe_schema_present: bool
    eligible_primary_count: int
    raw_companyfacts_ciks: int
    raw_submissions_ciks: int
    normalized_company_count: int
    unresolved_normalizer_errors: int
    unresolved_mapper_errors: int
    database_size_bytes: int
    scalable_table_bytes: int
    mapping_coverage: Decimal | None = None

    @property
    def bytes_per_normalized_company(self) -> int:
        if self.normalized_company_count <= 0:
            return 0
        return self.scalable_table_bytes // self.normalized_company_count

    def projected_database_size(self, target: int) -> int:
        additional = max(0, target - self.normalized_company_count)
        return self.database_size_bytes + additional * self.bytes_per_normalized_company


@dataclass(frozen=True)
class PilotReadiness:
    ready: bool
    blockers: tuple[str, ...]
    projected_database_size_bytes: int
    database_limit_bytes: int


def select_stratified_sample(
    candidates: Iterable[PilotCandidate], target: int = 100
) -> list[PilotCandidate]:
    if target < 1:
        raise ValueError("pilot target must be positive")

    by_cik = {candidate.cik: candidate for candidate in candidates}
    pool = sorted(by_cik.values(), key=lambda candidate: candidate.cik)
    if len(pool) < target:
        raise ValueError(
            f"need {target} distinct eligible companies, found {len(pool)}"
        )

    populations = Counter(token for candidate in pool for token in candidate.strata())
    selected: list[PilotCandidate] = []
    selected_ciks: set[str] = set()
    represented = Counter()

    # Cover every available stratum once, rare strata first. One selected
    # company can satisfy several strata, keeping this a compact set-cover
    # pass rather than one company per label.
    for token in sorted(populations, key=lambda item: (populations[item], item)):
        if represented[token]:
            continue
        choices = [
            row
            for row in pool
            if row.cik not in selected_ciks and token in row.strata()
        ]
        if not choices:
            continue
        chosen = choices[0]
        selected.append(chosen)
        selected_ciks.add(chosen.cik)
        represented.update(chosen.strata())
        if len(selected) == target:
            return sorted(selected, key=lambda row: row.cik)

    # Fill remaining seats by favoring the currently least-represented
    # strata. Fraction avoids float/tie instability across Python builds.
    while len(selected) < target:
        remaining = [row for row in pool if row.cik not in selected_ciks]

        def balance_score(row: PilotCandidate) -> Fraction:
            return sum(
                (Fraction(1, represented[token] + 1) for token in row.strata()),
                start=Fraction(0, 1),
            )

        chosen = min(remaining, key=lambda row: (-balance_score(row), row.cik))
        selected.append(chosen)
        selected_ciks.add(chosen.cik)
        represented.update(chosen.strata())

    return sorted(selected, key=lambda row: row.cik)


def evaluate_readiness(
    inventory: PilotInventory,
    target: int = 100,
    database_limit_bytes: int = DEFAULT_DATABASE_LIMIT_BYTES,
) -> PilotReadiness:
    blockers: list[str] = []
    if not inventory.universe_schema_present:
        blockers.append("day6_universe_migration_not_deployed")
    if inventory.eligible_primary_count < target:
        blockers.append(
            f"insufficient_eligible_primary_companies:{inventory.eligible_primary_count}/{target}"
        )
    if inventory.raw_companyfacts_ciks < target:
        blockers.append(
            f"insufficient_companyfacts_payloads:{inventory.raw_companyfacts_ciks}/{target}"
        )
    if inventory.raw_submissions_ciks < target:
        blockers.append(
            f"insufficient_submissions_payloads:{inventory.raw_submissions_ciks}/{target}"
        )
    if inventory.unresolved_normalizer_errors:
        blockers.append(
            f"unresolved_normalizer_errors:{inventory.unresolved_normalizer_errors}"
        )
    if inventory.unresolved_mapper_errors:
        blockers.append(
            f"unresolved_mapper_errors:{inventory.unresolved_mapper_errors}"
        )
    if inventory.mapping_coverage is None:
        blockers.append("representative_mapping_coverage_not_measured")
    elif inventory.mapping_coverage < MAPPING_COVERAGE_GATE:
        blockers.append(
            f"mapping_coverage_below_gate:{inventory.mapping_coverage:.2%}/{MAPPING_COVERAGE_GATE:.0%}"
        )

    projected = inventory.projected_database_size(target)
    if projected > database_limit_bytes:
        blockers.append(
            f"projected_database_capacity_exceeded:{projected}/{database_limit_bytes}"
        )

    return PilotReadiness(
        ready=not blockers,
        blockers=tuple(blockers),
        projected_database_size_bytes=projected,
        database_limit_bytes=database_limit_bytes,
    )


def sector_group(sic_code: str | None) -> str:
    try:
        sic = int(sic_code or "")
    except ValueError:
        return "unknown"
    if 100 <= sic <= 999:
        return "agriculture"
    if 1000 <= sic <= 1499:
        return "mining"
    if 1500 <= sic <= 1799:
        return "construction"
    if 2000 <= sic <= 3999:
        return "manufacturing"
    if 4000 <= sic <= 4999:
        return "transport_communications_utilities"
    if 5000 <= sic <= 5199:
        return "wholesale"
    if 5200 <= sic <= 5999:
        return "retail"
    if 6000 <= sic <= 6799:
        return "finance_insurance_real_estate"
    if 7000 <= sic <= 8999:
        return "services"
    if 9000 <= sic <= 9999:
        return "public_administration"
    return "unknown"


def market_cap_band(value: Decimal | None) -> str:
    if value is None:
        return "unknown"
    if value < Decimal("300000000"):
        return "micro"
    if value < Decimal("2000000000"):
        return "small"
    if value < Decimal("10000000000"):
        return "mid"
    if value < Decimal("200000000000"):
        return "large"
    return "mega"


def issuer_kind(sic_code: str | None) -> str:
    try:
        sic = int(sic_code or "")
    except ValueError:
        return "general"
    if 6000 <= sic <= 6099:
        return "bank"
    if 6311 <= sic <= 6411:
        return "insurer"
    if sic == 6798:
        return "reit"
    if sic == 6770:
        return "blank_check_candidate"
    return "general"


def classify_failure(stage: str, error_type: str, message: str) -> str:
    text = f"{error_type} {message}".lower()
    if error_type in {"KeyError", "AssertionError", "TypeError", "NotNullViolation"}:
        return "code_defect"
    if "mapping" in stage or "unmapped" in text or "concept" in text:
        return "mapping_gap"
    if "notinbulkarchive" in text or "no filing" in text or "missing payload" in text:
        return "unavailable_filing_data"
    if "cik" in text and ("mismatch" in text or "identity" in text):
        return "universe_error"
    if "structural" in text or "not applicable" in text:
        return "expected_structural_null"
    if any(
        marker in text for marker in ("timeout", "429", "http", "connection", "storage")
    ):
        return "upstream_source_failure"
    return "unreviewed"


def mapped_tag_presence(payloads: dict[str, dict]) -> dict:
    """Cheap mapping preflight over raw Company Facts JSON.

    Presence is not semantic reconciliation: it proves that at least one
    curated non-rejected tag exists in the payload, not that every period,
    unit, context, or formula will resolve. The report deliberately avoids a
    single pass/fail percentage that could overstate what this check proves.
    """
    mappings: dict[str, set[tuple[str, str]]] = {}
    for canonical, taxonomy, tag, _priority, confidence, _notes in CONCEPT_MAPPINGS:
        if confidence != "rejected":
            mappings.setdefault(canonical, set()).add((taxonomy, tag))

    resolved = Counter()
    taxonomy_counts = Counter()
    for payload in payloads.values():
        facts = payload.get("facts") or {}
        taxonomy_counts.update(facts.keys())
        for canonical, tags in mappings.items():
            if any(
                tag in facts.get(taxonomy, {})
                and bool((facts[taxonomy][tag] or {}).get("units"))
                for taxonomy, tag in tags
            ):
                resolved[canonical] += 1

    count = len(payloads)
    return {
        "companies": count,
        "taxonomy_company_counts": dict(sorted(taxonomy_counts.items())),
        "concepts": {
            canonical: {
                "present": resolved[canonical],
                "missing": count - resolved[canonical],
                "presence_rate": str(
                    (Decimal(resolved[canonical]) / Decimal(count)).quantize(
                        Decimal("0.0001")
                    )
                    if count
                    else Decimal("0")
                ),
            }
            for canonical in sorted(mappings)
        },
    }


def read_inventory(conn: psycopg.Connection) -> PilotInventory:
    with conn.cursor() as cur:
        cur.execute("select to_regclass('core.universe_member') is not null")
        universe_present = cur.fetchone()[0]
        eligible_primary_count = 0
        if universe_present:
            cur.execute(
                """
                select count(distinct company_id)
                from core.universe_member
                where snapshot_id = (select id from core.universe_snapshot order by as_of desc, id desc limit 1)
                  and eligibility_status = 'eligible' and is_primary
                """
            )
            eligible_primary_count = cur.fetchone()[0]

        cur.execute("select count(distinct cik) from raw.sec_companyfacts")
        companyfacts_ciks = cur.fetchone()[0]
        cur.execute("select count(distinct cik) from raw.sec_submissions")
        submissions_ciks = cur.fetchone()[0]
        cur.execute("select count(distinct company_id) from core.fact")
        normalized_companies = cur.fetchone()[0]
        cur.execute("select count(*) from core.normalizer_error where not resolved")
        normalizer_errors = cur.fetchone()[0]
        cur.execute("select count(*) from analytics.mapper_error where not resolved")
        mapper_errors = cur.fetchone()[0]
        cur.execute("select pg_database_size(current_database())")
        database_bytes = cur.fetchone()[0]
        cur.execute(
            """
            select sum(pg_total_relation_size(name::regclass))
            from unnest(array[
                'core.fact', 'core.period', 'core.filing',
                'analytics.canonical_fact', 'analytics.metric_value'
            ]) as name
            """
        )
        scalable_bytes = int(cur.fetchone()[0] or 0)

    return PilotInventory(
        universe_schema_present=universe_present,
        eligible_primary_count=eligible_primary_count,
        raw_companyfacts_ciks=companyfacts_ciks,
        raw_submissions_ciks=submissions_ciks,
        normalized_company_count=normalized_companies,
        unresolved_normalizer_errors=normalizer_errors,
        unresolved_mapper_errors=mapper_errors,
        database_size_bytes=database_bytes,
        scalable_table_bytes=scalable_bytes,
        mapping_coverage=None,
    )


def load_eligible_candidates(conn: psycopg.Connection) -> list[PilotCandidate]:
    """Load the latest Day 6 approved primary universe for sample selection."""
    with conn.cursor() as cur:
        cur.execute(
            """
            with latest_snapshot as (
                select id from core.universe_snapshot order by as_of desc, id desc limit 1
            ), forms as (
                select company_id,
                       array_agg(distinct form) as filing_forms,
                       bool_or(form like '%/A') as has_amendment
                from core.filing group by company_id
            ), caps as (
                select distinct on (mv.company_id) mv.company_id, mv.value
                from analytics.metric_value mv
                join analytics.metric_definition md on md.id = mv.metric_definition_id
                where md.metric_name = 'market_cap' and mv.value is not null
                order by mv.company_id, mv.period_end desc
            ), classes as (
                select company_id, count(*) as eligible_classes
                from core.universe_member
                where snapshot_id = (select id from latest_snapshot)
                  and eligibility_status = 'eligible'
                group by company_id
            )
            select c.cik, c.sic_code, c.fiscal_year_end, caps.value,
                   coalesce(forms.filing_forms, '{}'), coalesce(forms.has_amendment, false),
                   coalesce(classes.eligible_classes, 0) > 1
            from core.universe_member um
            join latest_snapshot ls on ls.id = um.snapshot_id
            join core.company c on c.id = um.company_id
            left join forms on forms.company_id = c.id
            left join caps on caps.company_id = c.id
            left join classes on classes.company_id = c.id
            where um.eligibility_status = 'eligible' and um.is_primary
            order by c.cik
            """
        )
        rows = cur.fetchall()

    return [
        PilotCandidate(
            cik=cik,
            sector=sector_group(sic),
            market_cap_band=market_cap_band(cap),
            fiscal_calendar=(
                "calendar"
                if fiscal_year_end == "1231"
                else "non_calendar"
                if fiscal_year_end
                else "unknown"
            ),
            filing_regime=classify_filing_regime(forms),
            issuer_kind=issuer_kind(sic),
            multi_class=multi_class,
            has_amendment=has_amendment,
        )
        for cik, sic, fiscal_year_end, cap, forms, has_amendment, multi_class in rows
    ]
