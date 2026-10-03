"""Period-gap candidate-tag finder (2026-10-03).

Generalizes the manual diagnostic queries used earlier this same day to find
and verify `net_income`'s `NetIncomeLossAvailableToCommonStockholdersBasic`
fallback and `diluted_eps`'s `EarningsPerShareBasicAndDiluted` fallback --
both found by (1) sampling a concept's open `analytics.period_gap` rows for
one cause, (2) checking what currently-UNMAPPED us-gaap tag is actually
present, authoritative, at those exact missing periods, (3) coexistence-
testing the top candidate against the concept's current tag(s).

Read-only. Recommends only -- same hard boundary as
`.github/agents/sec-xbrl-tag-expert.agent.md` and this project's own
tag_candidates.py/tag_investigator.py: a high sample frequency or a high
coexistence agreement is EVIDENCE to review, never grounds to auto-add.
Every real tag this project has ever added was checked by a human against
this exact kind of output first -- this script makes producing that output
fast and repeatable instead of a fresh set of ad hoc queries each time
(the complement of `find_concept_gap_clusters.py`, which asks "what do
companies missing a concept ENTIRELY share" -- this asks "what tag is
present at a concept's specific missing PERIODS").

Usage (pass the _resolved concept name -- that's what period_gap stores):
  uv run python scripts/find_period_gap_candidate_tags.py cfo_resolved
  uv run python scripts/find_period_gap_candidate_tags.py revenue_sanity_resolved --cause no_mapped_tag --sample 500
  uv run python scripts/find_period_gap_candidate_tags.py diluted_eps_resolved --top 3
"""

from collections import Counter
from decimal import Decimal

import psycopg
import typer

from scrooner_pipeline.common.config import settings

app = typer.Typer(add_completion=False)


def _mapped_tags(cur, concept_name: str) -> set[str]:
    cur.execute(
        """
        select co.tag from analytics.concept_mapping m
        join core.concept co on co.id = m.concept_id
        join analytics.canonical_concept cc on cc.id = m.canonical_concept_id
        where cc.name = %s and m.confidence <> 'rejected'
        """,
        (concept_name,),
    )
    return {r[0] for r in cur.fetchall()}


def _primary_tag(cur, concept_name: str) -> str | None:
    cur.execute(
        """
        select co.tag from analytics.concept_mapping m
        join core.concept co on co.id = m.concept_id
        join analytics.canonical_concept cc on cc.id = m.canonical_concept_id
        where cc.name = %s and m.confidence <> 'rejected'
        order by m.priority limit 1
        """,
        (concept_name,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def _sample_gap_periods(cur, concept_name: str, cause: str, sample: int) -> list[tuple]:
    cur.execute(
        """
        select g.company_id, g.period_end
        from analytics.period_gap g
        join analytics.canonical_concept cc on cc.id = g.canonical_concept_id
        where cc.name = %s and g.gap_cause = %s
        order by random() limit %s
        """,
        (concept_name, cause, sample),
    )
    return cur.fetchall()


def _candidate_frequency(
    cur, gaps: list[tuple], mapped_tags: set[str]
) -> Counter:
    counter: Counter = Counter()
    for company_id, period_end in gaps:
        cur.execute(
            """
            select distinct co.tag
            from core.fact f
            join core.concept co on co.id = f.concept_id
            join core.period p on p.id = f.period_id
            where f.company_id = %s and p.end_date = %s
              and f.is_authoritative = true and co.taxonomy = 'us-gaap'
            """,
            (company_id, period_end),
        )
        for (tag,) in cur.fetchall():
            if tag not in mapped_tags:
                counter[tag] += 1
    return counter


def _coexistence(cur, candidate_tag: str, primary_tag: str) -> dict:
    cur.execute(
        """
        with a as (
            select f.company_id, f.period_id, f.value
            from core.fact f join core.concept co on co.id = f.concept_id
            where co.taxonomy = 'us-gaap' and co.tag = %(candidate)s
              and f.is_authoritative = true
        ), b as (
            select f.company_id, f.period_id, f.value
            from core.fact f join core.concept co on co.id = f.concept_id
            where co.taxonomy = 'us-gaap' and co.tag = %(primary)s
              and f.is_authoritative = true
        )
        select count(*),
               count(*) filter (where abs(a.value - b.value) <= 0.01 * greatest(abs(a.value), abs(b.value), 0.01)),
               count(*) filter (where abs(a.value - b.value) > 0.01 * greatest(abs(a.value), abs(b.value), 0.01))
        from a join b on a.company_id = b.company_id and a.period_id = b.period_id
        """,
        {"candidate": candidate_tag, "primary": primary_tag},
    )
    total, agree, disagree = cur.fetchone()
    return {
        "coexisting_pairs": total,
        "agree_within_1pct": agree,
        "disagree": disagree,
        "agreement_pct": round(100 * agree / total, 1) if total else None,
    }


def _bounded_gap_fill(cur, candidate_tag: str, mapped_tags: set[str]) -> int:
    cur.execute(
        """
        with candidate as (
            select distinct f.company_id, f.period_id
            from core.fact f join core.concept co on co.id = f.concept_id
            where co.taxonomy = 'us-gaap' and co.tag = %(candidate)s
              and f.is_authoritative = true
        ),
        has_primary as (
            select distinct f.company_id, f.period_id
            from core.fact f join core.concept co on co.id = f.concept_id
            where co.taxonomy = 'us-gaap' and co.tag = any(%(mapped)s)
              and f.is_authoritative = true
        )
        select count(*) from candidate c
        where not exists (
            select 1 from has_primary h
            where h.company_id = c.company_id and h.period_id = c.period_id
        )
        """,
        {"candidate": candidate_tag, "mapped": list(mapped_tags)},
    )
    return cur.fetchone()[0]


@app.command()
def main(
    concept_name: str = typer.Argument(
        ...,
        help=(
            "Canonical concept name as it appears in period_gap, e.g. "
            "cfo_resolved, diluted_eps_resolved, revenue_sanity_resolved. "
            "period_completeness.py's CHECK_CONCEPTS always checks a "
            "_resolved display concept, not the raw base concept."
        ),
    ),
    base: str = typer.Option(
        None,
        help=(
            "The base concept whose concept_mapping rows are the tag "
            "source (default: concept_name with a trailing '_resolved' "
            "stripped, matching period_completeness.py's own CHECK_CONCEPTS "
            "mapping, e.g. cfo_resolved -> cfo)."
        ),
    ),
    cause: str = typer.Option("no_mapped_tag", help="period_gap.gap_cause to sample from"),
    sample: int = typer.Option(400, help="How many gap periods to sample"),
    top: int = typer.Option(5, help="How many top candidates to coexistence-test and report"),
) -> None:
    base_name = base or (
        concept_name[: -len("_resolved")]
        if concept_name.endswith("_resolved")
        else concept_name
    )
    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            mapped_tags = _mapped_tags(cur, base_name)
            primary_tag = _primary_tag(cur, base_name)
            if not mapped_tags:
                typer.echo(f"No concept_mapping rows found for base concept '{base_name}' -- pass --base explicitly.")
                raise typer.Exit(1)
            typer.echo(f"Gap concept: {concept_name} | base concept: {base_name} | currently mapped tags: {sorted(mapped_tags)}")

            gaps = _sample_gap_periods(cur, concept_name, cause, sample)
            typer.echo(f"Sampled {len(gaps)} gap periods (cause={cause})")
            if not gaps:
                typer.echo("No gap periods found for this (concept, cause) -- nothing to investigate.")
                return

            counter = _candidate_frequency(cur, gaps, mapped_tags)
            if not counter:
                typer.echo(
                    "No unmapped tag found at ANY sampled gap period -- this cluster's "
                    "cause is likely structural (genuinely missing in the filing), not a "
                    "missing-mapping problem. A tag addition will not help here."
                )
                return

            typer.echo(f"\nTop {top} unmapped tags present at these gap periods (lead only, NOT verified):")
            for tag, count in counter.most_common(top):
                typer.echo(f"  {tag}: {count}/{len(gaps)} sampled gaps")

            typer.echo("\n--- Coexistence verification against the primary mapped tag ---")
            typer.echo(f"(primary tag: {primary_tag})")
            for tag, count in counter.most_common(top):
                coex = _coexistence(cur, tag, primary_tag)
                bounded = _bounded_gap_fill(cur, tag, mapped_tags)
                typer.echo(f"\n  Candidate: {tag}")
                typer.echo(f"    sampled frequency: {count}/{len(gaps)}")
                if coex["coexisting_pairs"]:
                    typer.echo(
                        f"    coexistence with {primary_tag}: {coex['coexisting_pairs']} pairs, "
                        f"{coex['agreement_pct']}% agree within 1% "
                        f"({coex['agree_within_1pct']} agree / {coex['disagree']} disagree)"
                    )
                else:
                    typer.echo(f"    coexistence with {primary_tag}: never coexists in this data (0 pairs)")
                typer.echo(f"    bounded activation surface if added as a fallback: {bounded} periods")
                if coex["agreement_pct"] is not None and coex["agreement_pct"] >= 70:
                    typer.echo("    -> looks like a real same-concept variant, worth human review")
                elif coex["coexisting_pairs"] == 0 and bounded > 0:
                    typer.echo(
                        "    -> never coexists with the primary tag -- could be a real "
                        "same-concept fallback OR a different concept sharing vocabulary. "
                        "Verify semantic equivalence by reading 2-3 real filings before adding."
                    )
                else:
                    typer.echo(
                        "    -> high disagreement rate -- likely a DIFFERENT concept sharing "
                        "vocabulary (this project's own repeated trap). Do not add without "
                        "checking 2-3 real filings by hand."
                    )

            typer.echo(
                "\nThis output is a lead, never an approval. Every real tag this project has "
                "added was checked against 2-3 real filings by a human before being added to "
                "concepts.py -- do the same here before touching concept_mapping."
            )


if __name__ == "__main__":
    app()
