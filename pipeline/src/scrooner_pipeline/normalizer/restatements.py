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

logger = structlog.get_logger()


def link_amendments_for_company(conn: psycopg.Connection, company_id: int) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "select id, accession_number, form, period_of_report, filing_date "
            "from core.filing where company_id = %s and is_amendment",
            (company_id,),
        )
        amendments = cur.fetchall()

    linked = 0
    unmatched = 0
    with conn.cursor() as cur:
        for amend_id, accession_number, form, period_of_report, filing_date in amendments:
            base_form = form.replace("/A", "")
            cur.execute(
                """
                select id from core.filing
                where company_id = %s
                  and form in (%s, %s)
                  and period_of_report = %s
                  and filing_date < %s
                order by filing_date desc
                limit 1
                """,
                (company_id, base_form, f"{base_form}/A", period_of_report, filing_date),
            )
            row = cur.fetchone()
            if row is None:
                unmatched += 1
                logger.warning(
                    "restatements.amendment_unmatched",
                    company_id=company_id,
                    accession_number=accession_number,
                    form=form,
                    period_of_report=period_of_report,
                )
                continue
            cur.execute("update core.filing set amends_filing_id = %s where id = %s", (row[0], amend_id))
            linked += 1
    conn.commit()
    return {"linked": linked, "unmatched": unmatched}


def supersede_facts_for_company(conn: psycopg.Connection, company_id: int) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "select id, amends_filing_id from core.filing where company_id = %s and amends_filing_id is not null",
            (company_id,),
        )
        pairs = cur.fetchall()

    superseded_pairs = 0
    with conn.cursor() as cur:
        for amend_filing_id, original_filing_id in pairs:
            cur.execute(
                """
                select af.id, of.id
                from core.fact af
                join core.fact "of"
                    on of.company_id = af.company_id
                   and of.concept_id = af.concept_id
                   and of.unit_id   = af.unit_id
                   and of.period_id = af.period_id
                   and of.filing_id = %s
                where af.filing_id = %s
                """,
                (original_filing_id, amend_filing_id),
            )
            matches = cur.fetchall()
            for amend_fact_id, orig_fact_id in matches:
                cur.execute(
                    "update core.fact set is_authoritative = true, supersedes_fact_id = %s where id = %s",
                    (orig_fact_id, amend_fact_id),
                )
                cur.execute("update core.fact set is_authoritative = false where id = %s", (orig_fact_id,))
                superseded_pairs += 1
    conn.commit()
    return {"superseded_pairs": superseded_pairs}


def resolve_restatements(conn: psycopg.Connection, ciks: set[str]) -> dict:
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = dict(cur.fetchall())

    totals = {"considered": 0, "ok": 0, "no_company": 0, "linked": 0, "unmatched": 0, "superseded_pairs": 0}
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        link_stats = link_amendments_for_company(conn, company_id)
        supersede_stats = supersede_facts_for_company(conn, company_id)
        totals["ok"] += 1
        totals["linked"] += link_stats["linked"]
        totals["unmatched"] += link_stats["unmatched"]
        totals["superseded_pairs"] += supersede_stats["superseded_pairs"]
        logger.info("restatements.resolved", cik=cik, company_id=company_id, **link_stats, **supersede_stats)

    logger.info("restatements.resolve.done", **totals)
    return totals
