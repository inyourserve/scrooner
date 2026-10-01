"""Stage 2f -- Restatement handling (doc 09). Two steps:

1. Populate core.filing.amends_filing_id for every amendment (form ending
   in "/A"), left null by Stage 2a.
2. For every linked (amendment, original) filing pair, supersede matching
   core.fact rows: the amendment's fact becomes authoritative and points
   back at the original's fact via supersedes_fact_id; the original's fact
   becomes non-authoritative -- never deleted, never overwritten, always
   queryable (doc 04's lineage principle).

Linking rule, verified live 2026-08-15 against all 42 amendments across
the golden-10 (not just ARCC's, though ARCC's 5 10-K/As are the named
acceptance case): an amendment's original is the most recent PRIOR filing
for the same company, same base form family (form with "/A" stripped --
matching either the bare base form or an earlier amendment of it, so a
hypothetical amendment-of-an-amendment chain links to its immediate
predecessor, not always the very first filing), with the SAME
period_of_report. Held for 39 of 42; the other 3 companies' 7 unmatched
cases are all pre-2002 filings (several carrying SEC's `9999999997`
dummy-CIK prefix used for old paper filings) where the original genuinely
isn't in our captured submissions history -- left with amends_filing_id
null and counted, not guessed at.

Formal amendments are a STRONGER signal than Stage 2e's generic duplicate
resolution -- 2e only ever infers "earliest wins" from filing dates; 2f
knows, from SEC's own form-type data, that this filing IS a correction of
that one. So 2f's fact-level updates deliberately override whatever 2e
already set on the specific (concept, unit, period) pairs an amendment
actually touches, leaving everything else 2e resolved untouched.
"""

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error, safe_rollback

logger = structlog.get_logger()


def link_amendments_for_company(conn: psycopg.Connection, company_id: int) -> dict:
    """Batched (2026-08-26): the original version issued one correlated
    SELECT plus one UPDATE PER amendment -- found live to be the real
    remaining cost driver for heavy companies (company_id=2864, 43
    amendments, ~10+ minutes; a same-day peer with FAR more superseded fact
    pairs but only 6 amendments finished in under a minute once
    supersede_facts_for_company was batched, isolating amendment COUNT, not
    pair count, as the actual bottleneck here). Same matching rule (most
    recent prior filing, same base form family, same period_of_report),
    now evaluated for every amendment in one query via DISTINCT ON, applied
    with one bulk UPDATE.
    """
    with conn.cursor() as cur:
        cur.execute(
            "select id, accession_number, form, period_of_report, filing_date "
            "from core.filing where company_id = %s and is_amendment",
            (company_id,),
        )
        amendments = cur.fetchall()

    if not amendments:
        return {"linked": 0, "unmatched": 0}

    amend_ids = [a[0] for a in amendments]
    base_forms = [a[2].replace("/A", "") for a in amendments]
    alt_forms = [f"{bf}/A" for bf in base_forms]
    periods = [a[3] for a in amendments]
    filing_dates = [a[4] for a in amendments]

    with conn.cursor() as cur:
        cur.execute(
            """
            select distinct on (a.amend_id) a.amend_id, f.id
            from unnest(%s::bigint[], %s::text[], %s::text[], %s::date[], %s::date[])
                as a(amend_id, base_form, alt_form, period_of_report, filing_date)
            join core.filing f
                on f.company_id = %s
               and f.form in (a.base_form, a.alt_form)
               and f.period_of_report = a.period_of_report
               and f.filing_date < a.filing_date
            order by a.amend_id, f.filing_date desc
            """,
            (amend_ids, base_forms, alt_forms, periods, filing_dates, company_id),
        )
        matches = dict(cur.fetchall())

    linked = 0
    unmatched = 0
    matched_amend_ids = []
    matched_original_ids = []
    for amend_id, accession_number, form, period_of_report, _filing_date in amendments:
        original_id = matches.get(amend_id)
        if original_id is None:
            unmatched += 1
            logger.warning(
                "restatements.amendment_unmatched",
                company_id=company_id,
                accession_number=accession_number,
                form=form,
                period_of_report=period_of_report,
            )
            continue
        matched_amend_ids.append(amend_id)
        matched_original_ids.append(original_id)
        linked += 1

    if matched_amend_ids:
        with conn.cursor() as cur:
            cur.execute(
                """
                update core.filing set amends_filing_id = v.original_id
                from unnest(%s::bigint[], %s::bigint[]) as v(amend_id, original_id)
                where core.filing.id = v.amend_id
                """,
                (matched_amend_ids, matched_original_ids),
            )
    conn.commit()
    return {"linked": linked, "unmatched": unmatched}


def supersede_facts_for_company(conn: psycopg.Connection, company_id: int) -> dict:
    """Batched (2026-08-26): the original version issued one SELECT plus two
    round-trip UPDATEs PER superseded fact pair -- fine for most companies,
    but a real bug for the ones with hundreds/thousands of pairs (found
    live: company_id=2864, 1,088 pairs, ~11 minutes every single run,
    purely from network round-trip count, not query cost -- the exact
    N+1-in-a-loop shape this project's own pipeline/CLAUDE.md already
    documents as forbidden). Same semantics, same per-pair join condition,
    now evaluated for ALL of a company's amendment/original filing pairs in
    one query (via unnest over the filing-id pairs), then applied with
    exactly two bulk UPDATEs regardless of how many pairs matched.
    """
    with conn.cursor() as cur:
        cur.execute(
            "select id, amends_filing_id from core.filing where company_id = %s and amends_filing_id is not null",
            (company_id,),
        )
        pairs = cur.fetchall()

    if not pairs:
        return {"superseded_pairs": 0}

    amend_filing_ids = [p[0] for p in pairs]
    original_filing_ids = [p[1] for p in pairs]

    with conn.cursor() as cur:
        cur.execute(
            """
            select af.id, of.id
            from unnest(%s::bigint[], %s::bigint[]) as pair(amend_filing_id, original_filing_id)
            join core.fact af on af.filing_id = pair.amend_filing_id
            join core.fact "of"
                on of.filing_id = pair.original_filing_id
               and of.company_id = af.company_id
               and of.concept_id = af.concept_id
               and of.unit_id   = af.unit_id
               and of.period_id = af.period_id
            """,
            (amend_filing_ids, original_filing_ids),
        )
        matches = cur.fetchall()

    if not matches:
        conn.commit()
        return {"superseded_pairs": 0}

    amend_fact_ids = [m[0] for m in matches]
    orig_fact_ids = [m[1] for m in matches]

    with conn.cursor() as cur:
        cur.execute(
            """
            update core.fact set is_authoritative = true, supersedes_fact_id = v.orig_id
            from unnest(%s::bigint[], %s::bigint[]) as v(fact_id, orig_id)
            where core.fact.id = v.fact_id
            """,
            (amend_fact_ids, orig_fact_ids),
        )
        cur.execute(
            "update core.fact set is_authoritative = false where id = any(%s::bigint[])",
            (orig_fact_ids,),
        )
    conn.commit()
    return {"superseded_pairs": len(matches)}


def resolve_restatements(conn: psycopg.Connection, ciks: set[str]) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())

    totals = {
        "considered": 0,
        "ok": 0,
        "no_company": 0,
        "errored": 0,
        "linked": 0,
        "unmatched": 0,
        "superseded_pairs": 0,
    }
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            link_stats = link_amendments_for_company(conn, company_id)
            supersede_stats = supersede_facts_for_company(conn, company_id)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "core.normalizer_error", cik, "restatements", exc)
            conn = safe_rollback(conn, stage="restatements", cik=cik)
            continue
        totals["ok"] += 1
        totals["linked"] += link_stats["linked"]
        totals["unmatched"] += link_stats["unmatched"]
        totals["superseded_pairs"] += supersede_stats["superseded_pairs"]
        logger.info(
            "restatements.resolved",
            cik=cik,
            company_id=company_id,
            **link_stats,
            **supersede_stats,
        )

    logger.info("restatements.resolve.done", **totals)
    return totals
