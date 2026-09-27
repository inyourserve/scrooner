"""Stage 2c -- Unit normalization (doc 09). Resolves every distinct unit
string referenced anywhere in companyfacts payloads into core.unit. Read-only
against `raw`, writes only `core` -- no new SEC network calls.

core.unit is a GLOBAL lookup, not scoped per company -- units like "USD" or
"shares" mean the same thing for every filer, unlike core.period/core.fact.

Canonicalization is case-fold only (lower + strip), nothing fuzzier.
Verified live 2026-08-15 across the golden-10 companyfacts payloads: XBRL's
registered units (USD, CAD, TWD, EUR -- ISO 4217 codes; shares, pure -- the
standard non-currency units) are consistently cased already, by spec. But
FILER-INVENTED units for count-type facts (e.g. "how many reportable
segments") have no such registry, and really do collide across filers --
found "segment" (141 datapoints, 5 companies) and "Segment" (13 datapoints,
2 companies) both used for us-gaap:NumberOfReportableSegments-style
concepts; same for "Year"/"years". Case-folding these together is
standardization (doc 04's Normalizer "can do" column explicitly allows it),
not interpretation -- it doesn't decide what any concept MEANS, just that
"Segment" and "segment" are the same literal unit of measurement.

Deliberately NOT attempted: merging semantically-similar-but-textually-
distinct custom units (e.g. "Store" counts vs "Job" counts vs
"operating_segment" counts) into fewer buckets. Those are genuinely
different real-world units that happen to share the structural shape "a
plain count" -- collapsing them would be a Mapper-level judgment call about
what they mean, not Normalizer-level string standardization.
"""

import json

import psycopg
import structlog

from scrooner_pipeline.collector.storage import (
    SupabaseStorageClient,
    strip_bucket_prefix,
)
from scrooner_pipeline.common.errors import log_error

logger = structlog.get_logger()


def _load_json(storage: SupabaseStorageClient, storage_path: str) -> dict:
    raw_bytes = storage.download(strip_bucket_prefix(storage_path))
    return json.loads(raw_bytes)


def _latest_companyfacts_object(
    conn: psycopg.Connection, cik: str
) -> tuple[int, str] | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id, storage_path from raw.sec_companyfacts where cik = %s order by fetched_at desc limit 1",
            (cik,),
        )
        return cur.fetchone()


def canonicalize_unit(raw_unit: str) -> str:
    """The only standardization applied: fold case and trim whitespace.
    See module docstring for why nothing fuzzier (plural-stemming,
    semantic-grouping) is attempted here."""
    return raw_unit.strip().lower()


def extract_distinct_units(payload: dict) -> set[str]:
    """Every distinct (raw, as-reported) unit string referenced anywhere in
    a companyfacts payload, across every taxonomy/concept."""
    units: set[str] = set()
    for _taxonomy, concepts in payload.get("facts", {}).items():
        for _concept, cdata in concepts.items():
            units.update(cdata.get("units", {}).keys())
    return units


def upsert_units(conn: psycopg.Connection, canonical_unit_names: set[str]) -> int:
    if not canonical_unit_names:
        return 0
    with conn.cursor() as cur:
        cur.executemany(
            "insert into core.unit (unit_name) values (%s) on conflict (unit_name) do nothing",
            [(name,) for name in canonical_unit_names],
        )
    conn.commit()
    return len(canonical_unit_names)


def normalize_units_for_cik(
    storage: SupabaseStorageClient, conn: psycopg.Connection, cik: str
) -> dict:
    cf_row = _latest_companyfacts_object(conn, cik)
    if cf_row is None:
        logger.warning("units.no_companyfacts_for_cik", cik=cik)
        return {"cik": cik, "status": "no_companyfacts", "raw_units": set()}
    _raw_id, storage_path = cf_row
    payload = _load_json(storage, storage_path)
    raw_units = extract_distinct_units(payload)
    logger.info("units.scanned", cik=cik, raw_units=len(raw_units))
    return {"cik": cik, "status": "ok", "raw_units": raw_units}


def normalize_units(conn: psycopg.Connection, ciks: set[str]) -> dict:
    """Unlike identity/periods, this accumulates ONE shared set of canonical
    unit names across every requested company before writing -- core.unit
    is a global lookup, so there's no per-company upsert step."""
    stats = {"considered": 0, "ok": 0, "no_companyfacts": 0, "errored": 0}
    all_canonical: set[str] = set()
    raw_to_canonical: dict[str, set[str]] = {}
    with SupabaseStorageClient() as storage:
        for cik in sorted(ciks):
            stats["considered"] += 1
            try:
                result = normalize_units_for_cik(storage, conn, cik)
            except Exception as exc:
                stats["errored"] += 1
                log_error(conn, "core.normalizer_error", cik, "units", exc)
                continue
            stats[result["status"]] += 1
            for raw_unit in result["raw_units"]:
                canonical = canonicalize_unit(raw_unit)
                all_canonical.add(canonical)
                raw_to_canonical.setdefault(canonical, set()).add(raw_unit)

    written = upsert_units(conn, all_canonical)
    collisions = {
        c: variants for c, variants in raw_to_canonical.items() if len(variants) > 1
    }
    logger.info(
        "units.normalize.done",
        **stats,
        distinct_canonical_units=written,
        case_collisions=len(collisions),
    )
    if collisions:
        logger.info("units.case_collisions_detail", collisions=collisions)
    return {**stats, "distinct_canonical_units": written, "case_collisions": collisions}
