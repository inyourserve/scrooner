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
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.collector.storage import (
    SupabaseStorageClient,
    strip_bucket_prefix,
)
from scrooner_pipeline.common.errors import log_error, safe_rollback
from scrooner_pipeline.common.history_floor import HISTORY_FLOOR
from scrooner_pipeline.common.rule_flags import (
    RULE_SHARED_ACCESSION_PRIMARY,
    rule_enabled,
)
from scrooner_pipeline.normalizer.identity import FORM_ALLOWLIST
from scrooner_pipeline.normalizer.predecessors import Route, predecessor_routes
from scrooner_pipeline.normalizer.units import canonicalize_unit

logger = structlog.get_logger()

# doc 09's Day-7 scope note: TSM (20-F, ifrs-full) and ENB (40-F) stay
# identity/period/unit-only until doc 02's 20-F/40-F decision closes.
FACT_EXTRACTION_EXCLUDED_CIKS = {"0001046179", "0000895728"}  # TSM, ENB

# Founder decision 2026-10-25 (revised: floor moved 2015 -> 2014-01-01 to keep prior-year inputs): no fact whose period ends before
# 2014-01-01 is stored. The pre-2015 purge deletes them; without this floor every
# reprocess of a company would re-insert them from its raw companyfacts payload.
FACT_HISTORY_FLOOR = HISTORY_FLOOR  # 2014-01-01, single source: common/history_floor.py (founder 2026-10-25: keep calendar 2014)


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
        lookup = dict(cur.fetchall())
        if rule_enabled(RULE_SHARED_ACCESSION_PRIMARY):
            # entity.shared_accession_primary_filer@1: a combined filing's row may be
            # owned by a co-registrant (first claimant under the legacy upsert) while
            # THIS company is its primary; its own companyfacts carry the facts.
            cur.execute(
                """
                select f.accession_number, f.id
                from core.filing_registrant r
                join core.filing f on f.accession_number = r.accession_number
                where r.company_id = %s and r.role = 'primary'
                """,
                (company_id,),
            )
            lookup.update(dict(cur.fetchall()))
        return lookup


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
    conn: psycopg.Connection,
    pairs: set[tuple[str, str]],
    cache: dict[tuple[str, str], int] | None = None,
) -> dict[tuple[str, str], int]:
    """Insert any missing (taxonomy, tag) pairs and return the pair -> id lookup.

    With `cache` (the run-wide lookup loaded once by normalize_facts) only the pairs
    the cache does not hold are inserted, and only those are re-queried; the cache is
    updated in place and returned. Without it the whole table is re-read (old path)."""
    if cache is not None:
        missing = sorted(p for p in pairs if p not in cache)
        if missing:
            found: list[tuple[str, str, int]] = []
            with conn.cursor() as cur:
                cur.executemany(
                    "insert into core.concept (taxonomy, tag) values (%s, %s) on conflict (taxonomy, tag) do nothing",
                    missing,
                )
                cur.execute(
                    "select c.taxonomy, c.tag, c.id from core.concept c "
                    "join unnest(%s::text[], %s::text[]) as n(taxonomy, tag) "
                    "on c.taxonomy = n.taxonomy and c.tag = n.tag",
                    ([m[0] for m in missing], [m[1] for m in missing]),
                )
                found = cur.fetchall()
            conn.commit()
            # only after the commit: a rolled-back insert must never leave a phantom id in the cache
            for taxonomy, tag, cid in found:
                cache[(taxonomy, tag)] = cid
        return cache
    if pairs:
        with conn.cursor() as cur:
            cur.executemany(
                "insert into core.concept (taxonomy, tag) values (%s, %s) on conflict (taxonomy, tag) do nothing",
                sorted(pairs),
            )
        conn.commit()
    return _load_concept_lookup(conn)


_FACT_KEY = "company_id, concept_id, unit_id, period_id, filing_id"
_FACT_STAGE_COLS = (
    "company_id", "concept_id", "unit_id", "period_id", "filing_id", "value", "raw_object_id",
)


def write_fact_rows(conn: psycopg.Connection, rows: list[dict]) -> None:
    """COPY `rows` into a temp staging table, then one set-based insert into core.fact.

    Same result as the old per-row `executemany` (insert ... on conflict (key) do update
    set value = excluded.value): a key repeated inside `rows` keeps its first insertion
    position and ends with the LAST value (row-by-row semantics; a single set-based
    ON CONFLICT would otherwise raise "cannot affect row a second time"). Values go to
    COPY as Decimal/int, i.e. their exact text, never float. The caller commits; the
    staging table is emptied at commit (`on commit delete rows`) and reused per session."""
    with conn.cursor() as cur:
        cur.execute(
            """
            create temp table if not exists _fact_stage (
                seq bigint generated always as identity,
                company_id bigint, concept_id bigint, unit_id bigint, period_id bigint,
                filing_id bigint, value numeric, raw_object_id bigint
            ) on commit delete rows
            """
        )
        with cur.copy(
            f"copy _fact_stage ({', '.join(_FACT_STAGE_COLS)}) from stdin"
        ) as copy:
            for r in rows:
                copy.write_row([r[c] for c in _FACT_STAGE_COLS])
        cur.execute(
            f"""
            insert into core.fact
                (company_id, concept_id, unit_id, period_id, filing_id, value, raw_object_id)
            select company_id, concept_id, unit_id, period_id, filing_id,
                   (array_agg(value order by seq desc))[1],
                   (array_agg(raw_object_id order by seq desc))[1]
            from _fact_stage
            group by {_FACT_KEY}
            order by min(seq)
            on conflict ({_FACT_KEY}) do update
                set value = excluded.value
            """
        )


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
    storage: SupabaseStorageClient,
    conn: psycopg.Connection,
    cik: str,
    concept_by_pair: dict[tuple[str, str], int] | None = None,
    unit_by_name: dict[str, int] | None = None,
) -> dict:
    company_id = _get_company_id(conn, cik)
    routes = predecessor_routes(conn, cik)
    if company_id is None and not routes:
        logger.warning("facts.no_company_for_cik", cik=cik)
        return {"cik": cik, "status": "no_company"}

    cf_row = _latest_companyfacts_object(conn, cik)
    if cf_row is None:
        logger.warning("facts.no_companyfacts_for_cik", cik=cik)
        return {"cik": cik, "status": "no_companyfacts"}
    raw_object_id, storage_path = cf_row
    payload = _load_json(storage, storage_path)
    result: dict[str, Any] = {"cik": cik, "status": "ok"}
    if company_id is not None:
        result = normalize_payload(
            conn, company_id, cik, payload, raw_object_id,
            concept_by_pair=concept_by_pair, unit_by_name=unit_by_name,
        )
    # Predecessor windows: the same payload, attributed to each successor company.
    result["predecessor_routes"] = [
        normalize_payload(
            conn, r.company_id, cik, payload, raw_object_id, window=r,
            concept_by_pair=concept_by_pair, unit_by_name=unit_by_name,
        )
        for r in routes
    ]
    return result


def normalize_payload(
    conn: psycopg.Connection,
    company_id: int,
    cik: str,
    payload: dict,
    raw_object_id: int,
    window: Route | None = None,
    concept_by_pair: dict[tuple[str, str], int] | None = None,
    unit_by_name: dict[str, int] | None = None,
) -> dict:
    """`concept_by_pair` / `unit_by_name`: run-wide lookups loaded once by normalize_facts (the
    concept cache is extended in place with newly upserted tags); None loads them here.

    `window` (predecessor routing, see normalizer/predecessors.py): only facts whose period END
    lies inside the window are written, to `company_id` (the successor).

    The ONE write path for facts: a companyfacts-shaped payload into
    core.fact with `raw_object_id` as lineage. Called with the SEC companyfacts
    payload by normalize_facts_for_cik, and by the B9 instance fallback with a
    payload built from the filing's own XBRL (FSN set or instance) for a
    periodic filing the companyfacts API never carried (2026-10-31)."""
    filing_by_accn = {} if window is not None else _load_filing_lookup(conn, company_id)
    if window is not None:
        # Only filings that came from THIS source CIK (raw_submission_id -> raw.sec_submissions.cik,
        # or the source's own core.company) and whose period is inside the window and outside the
        # excludes. The successor's own filings are never matched: they carry their own accessions.
        filing_by_accn = {
            accn: fid
            for accn, fid, period in conn.execute(
                """select f.accession_number, f.id, f.period_of_report
                   from core.filing f
                   left join raw.sec_submissions s on s.id = f.raw_submission_id
                   where s.cik = %s
                      or f.company_id in (select id from core.company where cik = %s)""",
                (cik, cik),
            ).fetchall()
            if window.contains(period)
        }
    period_by_key = _load_period_lookup(conn, company_id)
    if unit_by_name is None:
        unit_by_name = _load_unit_lookup(conn)

    raw_rows = extract_fact_rows(payload)
    concept_pairs = {(r["taxonomy"], r["tag"]) for r in raw_rows}
    if concept_by_pair is None:
        concept_by_pair = upsert_concepts(conn, concept_pairs)
    else:
        upsert_concepts(conn, concept_pairs, cache=concept_by_pair)

    stats = {
        "considered": len(raw_rows),
        "written": 0,
        "skipped_no_filing": 0,
        "skipped_no_end": 0,
        "skipped_non_numeric": 0,
        "skipped_unmapped_unit": 0,
        "skipped_period_not_found": 0,
        "skipped_before_history_floor": 0,
        "skipped_outside_window": 0,
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
        if window is not None and not window.contains(end_date):
            stats["skipped_outside_window"] += 1
            continue
        if end_date < FACT_HISTORY_FLOOR:
            stats["skipped_before_history_floor"] += 1
            continue
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
        write_fact_rows(conn, insert_rows)
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
        "skipped_before_history_floor": 0,
    }
    errored: list[str] = []
    per_cik = {}
    # Lookups are global and nearly static: load once per run, not once per CIK (live
    # pg_stat_statements: 14,421 full core.concept scans). Concepts first seen during the run
    # are added to concept_by_pair in place by upsert_concepts(cache=...).
    unit_by_name = _load_unit_lookup(conn) if target_ciks else {}
    concept_by_pair = _load_concept_lookup(conn) if target_ciks else {}
    with SupabaseStorageClient() as storage:
        for cik in sorted(target_ciks):
            try:
                result = normalize_facts_for_cik(
                    storage, conn, cik,
                    concept_by_pair=concept_by_pair, unit_by_name=unit_by_name,
                )
            except Exception as exc:
                errored.append(cik)
                log_error(conn, "core.normalizer_error", cik, "facts", exc)
                conn = safe_rollback(conn, stage="facts", cik=cik)
                continue
            per_cik[cik] = result
            if result["status"] == "ok":
                # a predecessor CIK (no company of its own) returns only its predecessor routes, no counts
                for k in totals:
                    totals[k] += result.get(k, 0)

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
