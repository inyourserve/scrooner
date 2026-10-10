"""Revenue sub-mapper registry (2026-10-02, by direct request: "why
fallback concept? in mapper create lots of submapper for revenue, and
group companies with common tag, and then make it scalable").

Before this package, each newly-discovered company-shape for revenue
(a sector-specific tag, a resolve() priority bug, a dimensionally-
stripped filing) got wired in as one more bespoke function inside
`mapper/concept_fallback.py`, plus one more entry in `sanity/
tag_investigator.py`'s `FIXABLE_CONCEPTS` dict -- a human had to
remember where to plug in a new case, and "why is company X's revenue
what it is" meant grepping across 3 files. This package is the same
"sub-tree node per calculation" fix `mapper/calculate_shapes/` already
applied to formula shapes (2026-09-28) and `mapper/main_calculator.py`/
`parsers/main_parser.py` applied to metrics/parsers (doc 42,
2026-09-05) -- applied one more time, to revenue resolution strategies.

Each registered resolver module is a company-grouping strategy: it
knows which companies it applies to and how to merge its own tag(s)
into `revenue_sanity_resolved` for them. A module exports exactly one
function, `run(conn) -> dict`, with the same stats-dict shape every
other resolver here returns (`considered`/`ok`/`errored`/
`rows_written`, plus whatever else is useful to that strategy). Adding
a new strategy for a newly-discovered company-shape is: one new file
here + one line in RESOLVER_REGISTRY below -- `run_all()` and the CLI
wiring (`jobs/map.py`'s `resolve-revenue` command) never need to
change.

**Discovery, not just resolution**: a new resolver candidate should be
found the same way root causes 2/3 of this package's first version
were found -- cluster the still-unexplained zero-revenue population by
shared tag (`pipeline/scripts/find_concept_gap_clusters.py`, built
2026-09-04 for exactly this), then run the standard coexistence test
against real company data (does the candidate tag ever coexist with
the primary revenue tag for the same period, and if so do the values
agree or represent a genuinely separate stream) before trusting it
enough to become a new sub-mapper file. This file is the registry a
cluster graduates INTO once verified -- not a replacement for that
verification step.

Resolvers run in the order below. Earlier resolvers narrow the
candidate pool for later ones via `_companies_owned_by_other_revenue_
writer()` (shared.py) -- a company one resolver already fully owns
(every period) is never touched by a later one, the same single-writer
discipline `concept_fallback.py`'s original `ARITHMETIC_FALLBACKS`
already established for the gross_profit/cost_of_revenue family.
"""

import psycopg
import structlog

from scrooner_pipeline.mapper.revenue_resolvers import (
    collaborative_arrangement,
    net_lease_income,
    rendered_report_parser,
    spurious_zero_tag_preference,
)

logger = structlog.get_logger()

# name -> (module, one-line description of the company-grouping it targets)
RESOLVER_REGISTRY: dict[str, tuple] = {
    # Strategy 1: a company whose priority-1 revenue tag is a real,
    # authoritative-but-spurious $0 (Stage 2e dedupe correctly rejecting
    # a trivial cross-filing rounding disagreement, then resolve()
    # falling through to nothing) -- fixed by discovering which of the
    # company's OWN already-mapped tags actually reconciles, stored as a
    # per-company preference. Runs first: it's the narrowest, most
    # surgical override, and other resolvers' "owned by another writer"
    # exclusion needs its result in place before they run.
    "spurious_zero_tag_preference": (
        spurious_zero_tag_preference,
        "resolve()'s authoritative-$0 bug -- per-company tag preference override",
    ),
    # Strategy 2: a genuinely unmapped tag representing a SECOND revenue
    # stream (biotech/pharma collaboration-arrangement income on top of
    # product/contract revenue) -- additive, never a substitute.
    "collaborative_arrangement": (
        collaborative_arrangement,
        "biotech/pharma collaboration-arrangement revenue (additive)",
    ),
    # Strategy 3: a genuinely unmapped tag that IS a sector's real
    # top-line, substituted only where the primary is missing/zero and
    # the company is evidence-gated to the right sector (equity/net-lease
    # REITs, explicitly excluding mortgage REITs/banks).
    "net_lease_income": (
        net_lease_income,
        "equity/net-lease REIT lease income (substitute, REIT-SIC-gated)",
    ),
    # Strategy 4: a real value exists but only inside the filing's own
    # rendered statement (dimensional/segment XBRL the Company Facts API
    # strips entirely) -- delegates to parsers/revenue_parser.py's
    # already-built rendered-report extraction + concept_parser_result,
    # merged in last since it's the most expensive (does its own SEC
    # fetches) and narrowest (only companies nothing else resolved).
    "rendered_report_parser": (
        rendered_report_parser,
        "rendered-report extraction for dimensionally-stripped filers",
    ),
}


def run_all(conn: psycopg.Connection, *, include_parser: bool = False) -> dict:
    """Runs every registered resolver in order, returns {resolver_name:
    stats}. `include_parser` defaults False since rendered_report_parser
    does its own SEC fetches (a real, rate-limited cost) -- the other 3
    resolvers are pure local recomputation over already-fetched data and
    always run."""
    results: dict[str, dict] = {}
    for name, (module, _description) in RESOLVER_REGISTRY.items():
        if name == "rendered_report_parser" and not include_parser:
            logger.info(
                "revenue_resolvers.skipped",
                resolver=name,
                reason="include_parser=False",
            )
            continue
        logger.info("revenue_resolvers.starting", resolver=name)
        stats = module.run(conn)
        logger.info("revenue_resolvers.done", resolver=name, **stats)
        results[name] = stats
    return results


def registry_summary() -> list[dict]:
    """What a human checks first: which strategies exist and what each
    targets, without reading 4 files."""
    return [
        {"name": name, "module": module.__name__, "targets": description}
        for name, (module, description) in RESOLVER_REGISTRY.items()
    ]
