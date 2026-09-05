"""Research tool (doc 42, built 2026-09-04) -- NOT part of the production
pipeline (not imported by any job, no CLI wiring). Answers a real question
raised mid-session: for the companies still missing a given canonical
concept, is there a real SHARED tag among a large subset of them -- a
sector cluster worth its own concept, the same shape as the
`bdc_total_investment_income` fix this script's own investigation found
-- rather than 700 individual one-off gaps?

Complements, doesn't replace, `build_tag_coverage_library.py`. That script
starts from a KNOWN canonical concept and hand-curated keywords, then
finds candidate ALTERNATE tags for that same concept (the `revenue`-tag
widening shape, e.g. adding `RevenueFromContractWithCustomerIncludingAssessedTax`).
This script starts from nothing -- no keyword guessing -- and asks "of the
companies missing concept X entirely, what tags do THEY actually share
with EACH OTHER?" The answer isn't always another `revenue`-shaped tag:
BDCs don't have a revenue-shaped tag at all, they share
`GrossInvestmentIncomeOperating`, an entirely different vocabulary a
keyword search for "revenue" would never surface. A cluster this script
finds might need a brand-new sector-specific concept (BDCs), a genuine
alternate tag for the SAME concept (a Parser-1 widening), or turn out to
be noise (many small, unrelated clusters of 1-2 companies each -- the
real Parser-3-shaped population, which this script correctly can't
cluster, since by definition those companies don't share a tag with
anyone).

How to read the output: a HIGH company-count cluster (dozens+) sharing an
otherwise-unmapped tag is the strong signal -- likely a real sector concept
worth its own canonical_concept row, the same discipline that already
shipped `bdc_total_investment_income` (118 companies, `GrossInvestmentIncomeOperating`).
A LOW company-count cluster (1-3) is much weaker evidence -- could be a
real but narrow alternate tag (verify like any other candidate, don't
batch-adopt), or just coincidental vocabulary overlap between unrelated
companies (this project's own repeated lesson: same-vocabulary tags are
often a DIFFERENT concept that happens to share words, see doc 40's
research_and_development/goodwill/comprehensive_income false positives).
Every cluster surfaced here is a LEAD to investigate on real company data
(read the rendered statement, confirm the tag really means what the
concept means), never an approval to auto-map.

Usage: uv run python scripts/find_concept_gap_clusters.py <concept_name> [--min-cluster 3] [--limit 25]
Example: uv run python scripts/find_concept_gap_clusters.py revenue
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scrooner_pipeline.db.connection import get_connection  # noqa: E402

# Taxonomies deliberately excluded from clustering -- these are either
# out of scope (ifrs-full: foreign filers already decided excluded from
# V1, see doc 02) or not concept-bearing (dei/srt/country/currency/exch/
# stpr are cover-page/dimension-metadata taxonomies, never a real line
# item a canonical_concept would map to).
EXCLUDED_TAXONOMIES = ("ifrs-full", "dei", "srt", "country", "currency", "exch", "stpr", "invest")

# SIC-description substrings for populations already confirmed, live,
# to be legitimately-absent (not a tag/parsing gap) for `revenue`
# specifically -- doc 42 Part 1's own root-cause table. Excluding them
# from clustering is what actually makes this script useful: run
# unfiltered against `revenue`, and 280 SPACs + ~250 pre-revenue
# biotech/pharma companies dominate every result with tags related to
# their shared "pre-revenue capital-raising" business stage (stock
# issuance, IPO proceeds, related-party debt) -- real correlation, zero
# revenue signal. Excluding them surfaces the much smaller, harder
# population clustering actually helps with. Not a universal exclusion
# list for every concept -- pass --no-sic-filter to disable for a
# concept where these categories aren't the dominant noise source.
DEFAULT_SIC_EXCLUDE_PATTERNS = (
    "blank check",
    "pharmaceutical",
    "biological",
    "commodity contracts",
    "gold and silver",
    "metal mining",
    "crude petroleum",
)


def find_clusters(
    conn,
    concept_name: str,
    min_cluster: int = 3,
    limit: int = 25,
    period_type: str = "duration",
    sic_exclude: bool = True,
) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("select id from analytics.canonical_concept where name = %s", (concept_name,))
        row = cur.fetchone()
        if row is None:
            raise SystemExit(f"Unknown canonical concept: {concept_name!r}")
        canonical_id = row[0]

        # The population missing this concept -- same "active + no
        # canonical_fact row" definition used throughout doc 41/42's own
        # live investigations this session. Optionally excludes SIC
        # categories already confirmed to be legitimate-absence noise
        # (see DEFAULT_SIC_EXCLUDE_PATTERNS above).
        sic_clause = ""
        params: list = [canonical_id]
        if sic_exclude:
            sic_clause = " and (c.sic_description is null or not (" + " or ".join(
                "c.sic_description ilike %s" for _ in DEFAULT_SIC_EXCLUDE_PATTERNS
            ) + "))"
            params.extend(f"%{p}%" for p in DEFAULT_SIC_EXCLUDE_PATTERNS)
        cur.execute(
            f"""
            select c.id
            from core.company c
            where c.status = 'active'
              and not exists (
                  select 1 from analytics.canonical_fact cf
                  where cf.company_id = c.id and cf.canonical_concept_id = %s
              )
              {sic_clause}
            """,
            params,
        )
        missing_company_ids = [r[0] for r in cur.fetchall()]
        if not missing_company_ids:
            return []

        # Pass 1: which tags does the MISSING population share -- restricted
        # to core.fact rows for exactly these companies (a small slice),
        # so this stays cheap even though core.fact itself is huge
        # (~67M rows full-population, see pipeline/CLAUDE.md). No
        # correlated subquery here on purpose -- that's what timed out
        # the first version of this script against the real database.
        #
        # unit='usd' + period_type='duration' is a deliberate, real
        # filter, not just a performance shortcut -- found live
        # 2026-09-04 running this script unfiltered against `revenue`:
        # the top "shared tags" were RetainedEarningsAccumulatedDeficit,
        # AdditionalPaidInCapital, PreferredStockSharesAuthorized, etc.
        # -- real signal that the missing population (mostly SPACs/
        # shells) shares a generic simple-balance-sheet SHAPE, not any
        # revenue-relevant tag. Revenue-shaped concepts are always a
        # monetary FLOW (duration period, USD unit) -- restricting to
        # that combination removes instant/balance-sheet tags and
        # non-monetary tags (share counts, ratios, ISO segment counts)
        # from consideration entirely, which is what actually
        # distinguishes "a real income-statement line item" from
        # "any tag this company happens to report."
        placeholders = tuple(EXCLUDED_TAXONOMIES)
        cur.execute(
            """
            select cn.id, cn.taxonomy, cn.tag,
                   count(distinct f.company_id) as missing_pop_company_count
            from core.fact f
            join core.concept cn on cn.id = f.concept_id
            join core.unit u on u.id = f.unit_id
            join core.period p on p.id = f.period_id
            where f.company_id = any(%s)
              and f.is_authoritative = true
              and cn.taxonomy != all(%s)
              and u.unit_name = 'usd'
              and p.period_type = %s
              and not exists (
                  select 1 from analytics.concept_mapping cm where cm.concept_id = cn.id
              )
            group by cn.id, cn.taxonomy, cn.tag
            having count(distinct f.company_id) >= %s
            order by missing_pop_company_count desc
            limit %s
            """,
            (missing_company_ids, list(placeholders), period_type, min_cluster, limit),
        )
        top_tags = cur.fetchall()

        # Pass 2: for just these top candidates, how common is each tag
        # ACROSS THE WHOLE ACTIVE POPULATION (not just the missing
        # subset) -- one narrow query per tag (core.concept.id is
        # indexed, core.fact's own company_id/concept_id lookups are
        # cheap at this per-tag scale), never a full-table correlated
        # subquery.
        clusters = []
        for concept_id, taxonomy, tag, missing_n in top_tags:
            cur.execute(
                "select count(distinct company_id) from core.fact where concept_id = %s and is_authoritative = true",
                (concept_id,),
            )
            full_n = cur.fetchone()[0]
            clusters.append(
                {
                    "taxonomy": taxonomy,
                    "tag": tag,
                    "missing_population_companies": missing_n,
                    "full_population_companies": full_n,
                }
            )

    return [
        {"total_missing_population": len(missing_company_ids), "clusters": clusters}
    ][0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("concept_name", help="canonical_concept.name to analyze, e.g. 'revenue'")
    parser.add_argument("--min-cluster", type=int, default=3, help="minimum company count to report a tag")
    parser.add_argument("--limit", type=int, default=25, help="max tags to print")
    parser.add_argument(
        "--period-type",
        choices=["duration", "instant"],
        default="duration",
        help="'duration' for income-statement/cash-flow-shaped concepts (revenue, operating_income), "
        "'instant' for balance-sheet-shaped concepts (current_assets, total_debt)",
    )
    parser.add_argument(
        "--no-sic-filter", action="store_true", help="don't exclude SPAC/pharma/biotech/mining SIC categories"
    )
    args = parser.parse_args()

    with get_connection() as conn:
        result = find_clusters(
            conn, args.concept_name, args.min_cluster, args.limit, args.period_type, not args.no_sic_filter
        )

    print(f"Concept: {args.concept_name}")
    print(f"Total active companies missing this concept: {result['total_missing_population']}")
    print(f"Top unmapped tags shared among them (min cluster size {args.min_cluster}):\n")
    for c in result["clusters"]:
        pct_of_missing = c["missing_population_companies"] / result["total_missing_population"] * 100
        print(
            f"  {c['taxonomy']}:{c['tag']:<55} "
            f"missing-pop={c['missing_population_companies']:>4} ({pct_of_missing:5.1f}% of gap)  "
            f"full-pop={c['full_population_companies']:>4}"
        )
    if not result["clusters"]:
        print("  (no shared unmapped tag found at this cluster size -- remaining gap is likely "
              "either structural (no tag exists at all) or scattered custom-extension tags, "
              "one company at a time -- the genuine Parser 3 shape.)")


if __name__ == "__main__":
    main()
