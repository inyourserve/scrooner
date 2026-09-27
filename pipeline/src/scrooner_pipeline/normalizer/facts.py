"""Stage 2d -- Fact extraction (doc 09). Writes every reported XBRL
datapoint from companyfacts into core.fact, linked to core.concept/unit/
period/filing, with full lineage back to raw.sec_companyfacts. Read-only
against `raw`, writes `core.fact` plus (as-encountered) `core.concept`.

Scope, decided by checking the golden-8's real data before writing this
(see doc/learnings/normalizer-day-04-facts.md):

- Only companies NOT in FACT_EXTRACTION_EXCLUDED_CIKS -- TSM (20-F) and ENB
  (40-F) run through Stages 2a/2b/2c for identity/period/unit structure but
  doc 09's Day-7 scope note explicitly excludes them from fact extraction,
  per doc 02's still-open 20-F/40-F decision.
- Only facts whose `accn` resolves to a filing already in core.filing (i.e.
  FORM_ALLOWLIST from identity.py: 10-K/10-Q + amendments, 20-F/40-F).
  Verified live: 424B2/424B5/8-K/DEF14A/S-8/S-3 filings also carry XBRL
  facts for the golden-8 (~9.7K of 178.8K entries, ~5%), but checked which
  CONCEPTS appear *only* via those forms -- fund-fee-table data (`ffd`/`cef`
  taxonomy, from ARCC's 424B2 prospectus supplements) and executive-pay
  disclosures (`ecd`, from DEF 14A proxy filings). None are financial-
  statement line items doc 03's MVP needs; skipping them is real MVP-scope
  discipline, not an accidental gap. A fact whose filing isn't in
  core.filing is skipped and counted, never silently dropped.
- Every value is inserted as Decimal, not float -- JSON's default float
  parsing can lose precision on monetary values, which is exactly what
  core.fact.value's `numeric` (not `double precision`) column type exists
  to prevent (doc 05: correctness before breadth). Verified live: every
  value in the golden-8's data is numeric (no string-valued facts
  encountered), but a non-numeric value is still skipped and counted
  defensively rather than assumed impossible for data not yet seen.
"""

import json
from datetime import date, datetime
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.collector.storage import (
    SupabaseStorageClient,
    strip_bucket_prefix,
)
from scrooner_pipeline.common.errors import log_error
from scrooner_pipeline.normalizer.identity import FORM_ALLOWLIST
from scrooner_pipeline.normalizer.units import canonicalize_unit

logger = structlog.get_logger()

# doc 09's Day-7 scope note: TSM (20-F, ifrs-full) and ENB (40-F) stay
# identity/period/unit-only until doc 02's 20-F/40-F decision closes.
FACT_EXTRACTION_EXCLUDED_CIKS = {"0001046179", "0000895728"}  # TSM, ENB


def _load_json(storage: SupabaseStorageClient, storage_path: str) -> dict:
    raw_bytes = storage.download(strip_bucket_prefix(storage_path))
    return json.loads(raw_bytes, parse_float=Decimal)


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _latest_companyfacts_object(
    conn: psycopg.Connection, cik: str
) -> tuple[int, str] | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id, storage_path from raw.sec_companyfacts where cik = %s order by fetched_at desc limit 1",
            (cik,),
        )
        return cur.fetchone()


def _get_company_id(conn: psycopg.Connection, cik: str) -> int | None:
    with conn.cursor() as cur:
        cur.execute("select id from core.company where cik = %s", (cik,))
        row = cur.fetchone()
        return row[0] if row else None


def _load_filing_lookup(conn: psycopg.Connection, company_id: int) -> dict[str, int]:
    """accession_number -> filing_id, for this company only (filings aren't
    shared across companies, unlike concept/unit)."""
    with conn.cursor() as cur:
        cur.execute(
            "select accession_number, id from core.filing where company_id = %s",
            (company_id,),
        )
        return dict(cur.fetchall())


def _load_period_lookup(conn: psycopg.Connection, company_id: int) -> dict[tuple, int]:
    """(start_date, end_date, period_type) -> period_id, for this company."""
    with conn.cursor() as cur:
        cur.execute(
            "select start_date, end_date, period_type, id from core.period where company_id = %s",
            (company_id,),
        )
        return {(start, end, ptype): pid for start, end, ptype, pid in cur.fetchall()}


def _load_unit_lookup(conn: psycopg.Connection) -> dict[str, int]:
    """unit_name (already canonical/lowercased) -> unit_id. Global, same as core.unit itself."""
    with conn.cursor() as cur:
        cur.execute("select unit_name, id from core.unit")
        return dict(cur.fetchall())


def _load_concept_lookup(conn: psycopg.Connection) -> dict[tuple[str, str], int]:
    """(taxonomy, tag) -> concept_id. Global, same as core.concept itself."""
    with conn.cursor() as cur:
        cur.execute("select taxonomy, tag, id from core.concept")
        return {(taxonomy, tag): cid for taxonomy, tag, cid in cur.fetchall()}


def upsert_concepts(
    conn: psycopg.Connection, pairs: set[tuple[str, str]]
) -> dict[tuple[str, str], int]:
    if pairs:
        with conn.cursor() as cur:
            cur.executemany(
                "insert into core.concept (taxonomy, tag) values (%s, %s) on conflict (taxonomy, tag) do nothing",
                sorted(pairs),
            )
        conn.commit()
    return _load_concept_lookup(conn)


def extract_fact_rows(payload: dict) -> list[dict]:
    """Every (taxonomy, concept, unit, entry) tuple in the payload, flattened
    into one dict per reported datapoint -- the raw material this stage
    resolves into core.fact rows. No filtering by form/filing here; that
    happens in normalize_facts_for_cik, which has the company's actual
    filing lookup to check against."""
    rows = []
    for taxonomy, concepts in payload.get("facts", {}).items():
        for tag, cdata in concepts.items():
            for raw_unit, entries in cdata.get("units", {}).items():
                for e in entries:
                    rows.append(
                        {
                            "taxonomy": taxonomy,
                            "tag": tag,
                            "raw_unit": raw_unit,
                            "accn": e.get("accn"),
                            "start": e.get("start"),
                            "end": e.get("end"),
                            "val": e.get("val"),
                        }
                    )
    return rows


def normalize_facts_for_cik(
    storage: SupabaseStorageClient, conn: psycopg.Connection, cik: str
) -> dict:
    company_id = _get_company_id(conn, cik)
    if company_id is None:
        logger.warning("facts.no_company_for_cik", cik=cik)
        return {"cik": cik, "status": "no_company"}

    cf_row = _latest_companyfacts_object(conn, cik)
    if cf_row is None:
        logger.warning("facts.no_companyfacts_for_cik", cik=cik)
        return {"cik": cik, "status": "no_companyfacts"}
    raw_object_id, storage_path = cf_row
    payload = _load_json(storage, storage_path)

    filing_by_accn = _load_filing_lookup(conn, company_id)
    period_by_key = _load_period_lookup(conn, company_id)
    unit_by_name = _load_unit_lookup(conn)

    raw_rows = extract_fact_rows(payload)
    concept_pairs = {(r["taxonomy"], r["tag"]) for r in raw_rows}
    concept_by_pair = upsert_concepts(conn, concept_pairs)

    stats = {
        "considered": len(raw_rows),
        "written": 0,
        "skipped_no_filing": 0,
        "skipped_no_end": 0,
        "skipped_non_numeric": 0,
        "skipped_unmapped_unit": 0,
        "skipped_period_not_found": 0,
    }
    insert_rows = []
    for r in raw_rows:
        filing_id = filing_by_accn.get(r["accn"])
        if filing_id is None:
            stats["skipped_no_filing"] += 1
            continue
        if not r["end"]:
            stats["skipped_no_end"] += 1
            continue
        if not isinstance(r["val"], (int, Decimal)) or isinstance(r["val"], bool):
            stats["skipped_non_numeric"] += 1
            continue

        end_date = _parse_date(r["end"])
        if r["start"]:
            start_date = _parse_date(r["start"])
            period_type = "duration"
        else:
            start_date = end_date
            period_type = "instant"
        period_id = period_by_key.get((start_date, end_date, period_type))
        if period_id is None:
            # Shouldn't happen -- Stage 2b scans the same payload's periods
            # exhaustively -- but never silently drop a fact over it.
            stats["skipped_period_not_found"] += 1
            logger.warning(
                "facts.period_not_found",
                cik=cik,
                tag=r["tag"],
                start=r["start"],
                end=r["end"],
                type=period_type,
            )
            continue

        unit_id = unit_by_name.get(canonicalize_unit(r["raw_unit"]))
        if unit_id is None:
            stats["skipped_unmapped_unit"] += 1
            logger.warning("facts.unit_not_found", cik=cik, raw_unit=r["raw_unit"])
            continue

        concept_id = concept_by_pair[(r["taxonomy"], r["tag"])]

        insert_rows.append(
            {
                "company_id": company_id,
                "concept_id": concept_id,
                "unit_id": unit_id,
                "period_id": period_id,
                "filing_id": filing_id,
                "value": r["val"],
                "raw_object_id": raw_object_id,
            }
        )

    if insert_rows:
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into core.fact
                    (company_id, concept_id, unit_id, period_id, filing_id, value, raw_object_id)
                values
                    (%(company_id)s, %(concept_id)s, %(unit_id)s, %(period_id)s, %(filing_id)s,
                     %(value)s, %(raw_object_id)s)
                on conflict (company_id, concept_id, unit_id, period_id, filing_id) do update
                    set value = excluded.value
                """,
                insert_rows,
            )
        conn.commit()
    stats["written"] = len(insert_rows)

    logger.info("facts.normalized", cik=cik, company_id=company_id, **stats)
    return {"cik": cik, "status": "ok", **stats}


def normalize_facts(conn: psycopg.Connection, ciks: set[str]) -> dict:
    target_ciks = ciks - FACT_EXTRACTION_EXCLUDED_CIKS
    excluded_requested = ciks & FACT_EXTRACTION_EXCLUDED_CIKS
    if excluded_requested:
        logger.info("facts.excluded_by_scope", ciks=sorted(excluded_requested))

    totals = {
        "considered": 0,
        "written": 0,
        "skipped_no_filing": 0,
        "skipped_no_end": 0,
        "skipped_non_numeric": 0,
        "skipped_unmapped_unit": 0,
        "skipped_period_not_found": 0,
    }
    errored: list[str] = []
    per_cik = {}
    with SupabaseStorageClient() as storage:
        for cik in sorted(target_ciks):
            try:
                result = normalize_facts_for_cik(storage, conn, cik)
            except Exception as exc:
                errored.append(cik)
                log_error(conn, "core.normalizer_error", cik, "facts", exc)
                continue
            per_cik[cik] = result
            if result["status"] == "ok":
                for k in totals:
                    totals[k] += result[k]

    logger.info(
        "facts.normalize.done",
        excluded=sorted(excluded_requested),
        errored=errored,
        **totals,
    )
    return {
        "excluded": sorted(excluded_requested),
        "errored": errored,
        "totals": totals,
        "per_cik": per_cik,
    }
