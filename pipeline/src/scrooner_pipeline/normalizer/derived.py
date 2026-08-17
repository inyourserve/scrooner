"""Stage 2g -- Q4 derivation (doc 09). Companies file 10-Qs for Q1-Q3 and a
10-K for the full year -- there is normally no standalone Q4 filing, so a
Q4 value has to be derived as FY - Q1 - Q2 - Q3 and explicitly flagged
(is_derived=true), never presented as if it were directly reported.

Only duration facts need this -- an instant (balance-sheet) fact "as of"
fiscal year end already IS the Q4-end snapshot, nothing to derive. Uses
Stage 2b's fiscal_year/fiscal_period labels (robust across non-calendar
FYE companies -- verified Day 2 against AAPL/MSFT/NKE's real fiscal
calendars) to group FY/Q1/Q2/Q3 candidates, and only Stage 2e/2f's
resolved `is_authoritative` facts -- deriving from an unresolved or
superseded input would manufacture a new number nobody should trust,
compounding uncertainty instead of flagging it.

Lineage: a derived fact's filing_id/raw_object_id point at the FY fact's
own filing/raw object (the 10-K that anchors the full-year side of the
subtraction) -- no new schema field for "derived from 4 facts" needed,
since Q1/Q2/Q3's contributing values are always fully reconstructable by
querying the same (company, concept, unit, fiscal_year) with
fiscal_period in ('Q1','Q2','Q3'), same "don't scaffold new schema the
existing structure already answers" pattern as Stage 2e's is_authoritative.

If a company genuinely reports a discrete Q4 value directly somewhere
(rare, but checked for) the real reported fact is left alone -- derivation
never overwrites or duplicates a real value with a guess.

All lookups (existing periods, existing non-derived facts) are loaded
into memory up front and writes are batched, same pattern as
identity.py/periods.py/facts.py -- a first version of this module did a
handful of individual round-trip queries per candidate group instead, and
a large company (JPM, AAPL: thousands of groups) hit repeated
`SSL SYSCALL... Operation timed out` errors from the sheer round-trip
count over one long-lived connection, the same class of problem doc 08's
day-04 learnings entry already flagged for the Collector. Fixed by
batching, not by retrying harder.
"""

from datetime import timedelta

import psycopg
import structlog

logger = structlog.get_logger()

# Same day-length bands periods.py itself uses to classify a duration
# span (see that module's own comment) -- reused here, not
# re-guessed, so "half-year" and "three-quarter" mean exactly the same
# thing in both places.
HALF_YEAR_MIN_DAYS, HALF_YEAR_MAX_DAYS = 170, 200
THREE_QUARTER_MIN_DAYS, THREE_QUARTER_MAX_DAYS = 260, 290


def _load_quarterly_candidates(conn: psycopg.Connection, company_id: int) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.id, f.concept_id, f.unit_id, f.value, f.filing_id, f.raw_object_id,
                   p.fiscal_year, p.fiscal_period, p.start_date, p.end_date
            from core.fact f
            join core.period p on p.id = f.period_id
            where f.company_id = %s
              and f.is_authoritative
              and p.period_type = 'duration'
              and p.fiscal_period in ('FY', 'Q1', 'Q2', 'Q3')
            """,
            (company_id,),
        )
        return cur.fetchall()


def _load_existing_periods(conn: psycopg.Connection, company_id: int) -> dict[tuple, int]:
    """(start_date, end_date) -> period_id, for this company's duration periods."""
    with conn.cursor() as cur:
        cur.execute(
            "select start_date, end_date, id from core.period where company_id = %s and period_type = 'duration'",
            (company_id,),
        )
        return {(start, end): pid for start, end, pid in cur.fetchall()}


def _load_reported_duration_keys(conn: psycopg.Connection, company_id: int) -> set[tuple]:
    """(concept_id, unit_id, start_date, end_date) for every REPORTED
    (not derived) duration fact -- used to skip derivation when a company
    genuinely already reports a discrete Q4 value directly."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.concept_id, f.unit_id, p.start_date, p.end_date
            from core.fact f
            join core.period p on p.id = f.period_id
            where f.company_id = %s and p.period_type = 'duration' and f.is_derived = false
            """,
            (company_id,),
        )
        return set(cur.fetchall())


def derive_q4_for_company(conn: psycopg.Connection, company_id: int) -> dict:
    rows = _load_quarterly_candidates(conn, company_id)
    groups: dict[tuple, dict] = {}
    for fact_id, concept_id, unit_id, value, filing_id, raw_object_id, fiscal_year, fiscal_period, start_date, end_date in rows:
        key = (concept_id, unit_id, fiscal_year)
        groups.setdefault(key, {})[fiscal_period] = {
            "fact_id": fact_id,
            "value": value,
            "filing_id": filing_id,
            "raw_object_id": raw_object_id,
            "start_date": start_date,
            "end_date": end_date,
        }

    existing_periods = _load_existing_periods(conn, company_id)
    reported_keys = _load_reported_duration_keys(conn, company_id)

    stats = {"candidate_groups": len(groups), "derived": 0, "already_reported": 0, "incomplete": 0}
    new_periods: list[tuple] = []  # (start, end, fiscal_year) -- may contain duplicates across concepts, deduped below
    to_derive: list[dict] = []

    for (concept_id, unit_id, fiscal_year), by_period in groups.items():
        if not all(k in by_period for k in ("FY", "Q1", "Q2", "Q3")):
            stats["incomplete"] += 1
            continue

        fy, q1, q2, q3 = by_period["FY"], by_period["Q1"], by_period["Q2"], by_period["Q3"]
        q4_start = q3["end_date"] + timedelta(days=1)
        q4_end = fy["end_date"]

        if (concept_id, unit_id, q4_start, q4_end) in reported_keys:
            stats["already_reported"] += 1
            continue

        if (q4_start, q4_end) not in existing_periods:
            new_periods.append((q4_start, q4_end, fiscal_year))

        to_derive.append(
            {
                "concept_id": concept_id,
                "unit_id": unit_id,
                "start": q4_start,
                "end": q4_end,
                "value": fy["value"] - q1["value"] - q2["value"] - q3["value"],
                "filing_id": fy["filing_id"],
                "raw_object_id": fy["raw_object_id"],
            }
        )

    # Insert any new Q4 periods first (deduped -- several concepts share the
    # same company-wide Q4 span), one round trip, then fold the new ids into
    # the same lookup dict used for the fact rows below.
    distinct_new_periods = {(s, e): fy for s, e, fy in new_periods}
    if distinct_new_periods:
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period)
                values (%(company_id)s, %(start)s, %(end)s, 'duration', %(fiscal_year)s, 'Q4')
                on conflict (company_id, start_date, end_date, period_type) do nothing
                """,
                [{"company_id": company_id, "start": s, "end": e, "fiscal_year": fy} for (s, e), fy in distinct_new_periods.items()],
            )
        conn.commit()
        existing_periods = _load_existing_periods(conn, company_id)

    if to_derive:
        rows_to_insert = [
            {
                "company_id": company_id,
                "concept_id": d["concept_id"],
                "unit_id": d["unit_id"],
                "period_id": existing_periods[(d["start"], d["end"])],
                "filing_id": d["filing_id"],
                "value": d["value"],
                "raw_object_id": d["raw_object_id"],
            }
            for d in to_derive
        ]
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into core.fact
                    (company_id, concept_id, unit_id, period_id, filing_id, value, is_derived, is_authoritative, raw_object_id)
                values
                    (%(company_id)s, %(concept_id)s, %(unit_id)s, %(period_id)s, %(filing_id)s, %(value)s, true, true, %(raw_object_id)s)
                on conflict (company_id, concept_id, unit_id, period_id, filing_id) do update
                    set value = excluded.value, is_derived = true
                """,
                rows_to_insert,
            )
        conn.commit()
        stats["derived"] = len(rows_to_insert)

    logger.info("derived.q4_resolved", company_id=company_id, **stats)
    return stats


def derive_q4(conn: psycopg.Connection, ciks: set[str]) -> dict:
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = dict(cur.fetchall())

    totals = {"considered": 0, "ok": 0, "no_company": 0, "candidate_groups": 0, "derived": 0, "already_reported": 0, "incomplete": 0}
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        stats = derive_q4_for_company(conn, company_id)
        totals["ok"] += 1
        for k in ("candidate_groups", "derived", "already_reported", "incomplete"):
            totals[k] += stats[k]

    logger.info("derived.q4.done", **totals)
    return totals


# --- Interim-quarter derivation (Stage 2g follow-on, doc 24/25 --
# closing a real gap found live 2026-08-17 while building
# mapper/price_metrics.py's FCF Yield: several companies' quarterly
# cash-flow-statement facts are tagged cumulative-year-to-date (a normal
# GAAP presentation choice, most common on cash-flow lines -- income-
# statement lines are usually reported discretely per quarter instead),
# which classify_period() above correctly leaves unclassified rather
# than mislabel as a single quarter. Confirmed live against AAPL's real
# CFO facts before writing this: Q1 $29.935B (discrete), a 6-month span
# $53.887B, a 9-month span $81.754B, FY $111.482B -- every one of these
# was already sitting in core.fact, just never decomposed into discrete
# quarters. Implied Q2 = $23.952B, Q3 = $27.867B, Q4 = $29.728B, all
# positive and reasonable, summing back to the real FY figure exactly by
# construction.
#
# Purely additive: does not modify derive_q4_for_company above. Derives
# Q2/Q3 as new is_derived=true/is_authoritative=true facts; derive_q4
# (already-existing logic, unchanged) then picks them up automatically
# on its own next run, the same way it already would for any other
# authoritative Q1-Q3 set -- no code path in derive_q4_for_company knows
# or needs to know these particular Q2/Q3 facts were derived rather than
# directly reported.
def _load_all_duration_facts(conn: psycopg.Connection, company_id: int) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.id, f.concept_id, f.unit_id, f.value, f.filing_id, f.raw_object_id,
                   p.fiscal_year, p.fiscal_period, p.start_date, p.end_date
            from core.fact f
            join core.period p on p.id = f.period_id
            where f.company_id = %s
              and f.is_authoritative
              and p.period_type = 'duration'
            """,
            (company_id,),
        )
        return cur.fetchall()


def derive_interim_quarters_for_company(conn: psycopg.Connection, company_id: int) -> dict:
    rows = _load_all_duration_facts(conn, company_id)
    groups: dict[tuple, dict] = {}
    for fact_id, concept_id, unit_id, value, filing_id, raw_object_id, fiscal_year, fiscal_period, start_date, end_date in rows:
        if fiscal_year is None:
            continue
        key = (concept_id, unit_id, fiscal_year)
        entry = {
            "fact_id": fact_id, "value": value, "filing_id": filing_id, "raw_object_id": raw_object_id,
            "start_date": start_date, "end_date": end_date,
        }
        duration_days = (end_date - start_date).days
        if fiscal_period == "Q1":
            groups.setdefault(key, {})["Q1"] = entry
        elif fiscal_period == "FY":
            groups.setdefault(key, {})["FY"] = entry
        elif fiscal_period is None and HALF_YEAR_MIN_DAYS <= duration_days <= HALF_YEAR_MAX_DAYS:
            groups.setdefault(key, {})["HALF"] = entry
        elif fiscal_period is None and THREE_QUARTER_MIN_DAYS <= duration_days <= THREE_QUARTER_MAX_DAYS:
            groups.setdefault(key, {})["THREE_Q"] = entry
        # Q2/Q3/Q4/other non-standard spans: not this derivation's
        # concern -- Q2/Q3 already discrete means nothing to derive;
        # anything else falls outside the clean day-length bands and is
        # correctly left alone rather than forced.

    existing_periods = _load_existing_periods(conn, company_id)
    reported_keys = _load_reported_duration_keys(conn, company_id)

    stats = {"candidate_groups": len(groups), "q2_derived": 0, "q3_derived": 0, "already_reported": 0, "incomplete_or_inconsistent": 0}
    new_periods: dict[tuple, dict] = {}  # (start, end) -> {"fiscal_year": ..., "fiscal_period": "Q2"|"Q3"}
    to_derive: list[dict] = []

    for (concept_id, unit_id, fiscal_year), by_span in groups.items():
        q1, half, three_q = by_span.get("Q1"), by_span.get("HALF"), by_span.get("THREE_Q")

        # Q2 = HALF - Q1, only when both share the same start (the true
        # fiscal-year start) -- never subtract spans that don't actually
        # nest inside one another.
        if q1 is not None and half is not None and q1["start_date"] == half["start_date"]:
            q2_start, q2_end = q1["end_date"] + timedelta(days=1), half["end_date"]
            if (concept_id, unit_id, q2_start, q2_end) not in reported_keys:
                if (q2_start, q2_end) not in existing_periods:
                    new_periods[(q2_start, q2_end)] = {"fiscal_year": fiscal_year, "fiscal_period": "Q2"}
                to_derive.append({
                    "concept_id": concept_id, "unit_id": unit_id, "start": q2_start, "end": q2_end,
                    "value": half["value"] - q1["value"], "filing_id": half["filing_id"], "raw_object_id": half["raw_object_id"],
                    "metric": "q2_derived",
                })
            else:
                stats["already_reported"] += 1
        else:
            stats["incomplete_or_inconsistent"] += 1

        # Q3 = THREE_Q - HALF, same nesting requirement.
        if half is not None and three_q is not None and half["start_date"] == three_q["start_date"]:
            q3_start, q3_end = half["end_date"] + timedelta(days=1), three_q["end_date"]
            if (concept_id, unit_id, q3_start, q3_end) not in reported_keys:
                if (q3_start, q3_end) not in existing_periods:
                    new_periods[(q3_start, q3_end)] = {"fiscal_year": fiscal_year, "fiscal_period": "Q3"}
                to_derive.append({
                    "concept_id": concept_id, "unit_id": unit_id, "start": q3_start, "end": q3_end,
                    "value": three_q["value"] - half["value"], "filing_id": three_q["filing_id"], "raw_object_id": three_q["raw_object_id"],
                    "metric": "q3_derived",
                })
            else:
                stats["already_reported"] += 1
        else:
            stats["incomplete_or_inconsistent"] += 1

    if new_periods:
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period)
                values (%(company_id)s, %(start)s, %(end)s, 'duration', %(fiscal_year)s, %(fiscal_period)s)
                on conflict (company_id, start_date, end_date, period_type) do update
                    set fiscal_period = excluded.fiscal_period
                """,
                [
                    {"company_id": company_id, "start": s, "end": e, **info}
                    for (s, e), info in new_periods.items()
                ],
            )
        conn.commit()
        existing_periods = _load_existing_periods(conn, company_id)

    if to_derive:
        rows_to_insert = [
            {
                "company_id": company_id, "concept_id": d["concept_id"], "unit_id": d["unit_id"],
                "period_id": existing_periods[(d["start"], d["end"])], "filing_id": d["filing_id"],
                "value": d["value"], "raw_object_id": d["raw_object_id"],
            }
            for d in to_derive
        ]
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into core.fact
                    (company_id, concept_id, unit_id, period_id, filing_id, value, is_derived, is_authoritative, raw_object_id)
                values
                    (%(company_id)s, %(concept_id)s, %(unit_id)s, %(period_id)s, %(filing_id)s, %(value)s, true, true, %(raw_object_id)s)
                on conflict (company_id, concept_id, unit_id, period_id, filing_id) do update
                    set value = excluded.value, is_derived = true
                """,
                rows_to_insert,
            )
        conn.commit()
        for d in to_derive:
            stats[d["metric"]] += 1

    logger.info("derived.interim_quarters_resolved", company_id=company_id, **stats)
    return stats


def derive_interim_quarters(conn: psycopg.Connection, ciks: set[str]) -> dict:
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = dict(cur.fetchall())

    totals = {"considered": 0, "ok": 0, "no_company": 0, "candidate_groups": 0, "q2_derived": 0, "q3_derived": 0, "already_reported": 0, "incomplete_or_inconsistent": 0}
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        stats = derive_interim_quarters_for_company(conn, company_id)
        totals["ok"] += 1
        for k in ("candidate_groups", "q2_derived", "q3_derived", "already_reported", "incomplete_or_inconsistent"):
            totals[k] += stats[k]

    logger.info("derived.interim_quarters.done", **totals)
    return totals
