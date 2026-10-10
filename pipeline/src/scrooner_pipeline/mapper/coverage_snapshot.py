"""Coverage-score tracking (doc 41, 2026-09-02). Computes and persists one
daily snapshot of data-point coverage -- per canonical_concept (tag-level,
what the Collector/Normalizer/Mapper's resolve() stage produced) and per
active metric_definition (product-facing, what calculate.py/expanded_metrics.py/
ttm.py/quality_score.py/quality_flags.py etc. actually computed) -- plus two
single aggregate scores meant to be watched trending upward over time, the
same "one documented score, hard denominator" discipline doc/status/
SCORECARD.md already established for a different (execution-quality) score.

avg_metric_coverage_score: simple mean of coverage_pct across every ACTIVE
metric_definition row (both the 18 doc-02-locked V1 metrics and every
expanded metric built since) -- this is the product-facing number, what a
user's screener/company-page results actually cover. Not weighted by
metric importance; a metric with real, low structural coverage (e.g.
piotroski_f_score, which correctly excludes financials) pulls the average
down exactly as much as any other -- deliberately simple (KISS BORING, doc
05) rather than a weighted formula reverse-engineered to look better.

avg_concept_coverage_score: same mean, over the 44 canonical_concept rows
-- a diagnostic/leading indicator (concept coverage moves before metric
coverage does, since a metric needs ALL of its input concepts covered for
the same period) but not the number to optimize directly, since concepts
aren't all equally load-bearing (some feed many metrics, some feed one).

avg_core_v1_metric_coverage_score (added 2026-09-03, doc 42 Part 3):
same mean, restricted to the 20 metric_definition rows doc 02 actually
locked for V1 (CORE_V1_METRIC_NAMES below, sourced directly from
mapper/definitions.py's own METRIC_DEFINITIONS -- not a new, invented
"core metrics" list). Answers a real, flagged-but-undecided product
question: avg_metric_coverage_score's full 64-metric average is
correct and complete, but gets diluted by inherently-rare metrics
(Piotroski's 9-simultaneous-input bar, dividend-only metrics) that most
users never look at -- this second score shows progress on the metrics
doc 02 already decided matter most, without replacing or changing the
first one. Purely additive: computing and storing this changes nothing
about how avg_metric_coverage_score is computed or used.

Never fabricates a coverage number -- every row is a real
`count(distinct company_id) / total_active_companies` query against
canonical_fact/metric_value, same as build_tag_coverage_library.py and
every other coverage query this project has run live."""

from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

import psycopg
import structlog

from scrooner_pipeline.mapper.definitions import (
    METRIC_DEFINITIONS as _V1_METRIC_DEFINITIONS,
)
from scrooner_pipeline.mapper.coverage_matrix import (
    BDC_FAMILY_DATA_POINTS,
    BUYBACK_FAMILY_DATA_POINTS,
    CAPITAL_RETURN_FAMILY_DATA_POINTS,
    DIVIDEND_FAMILY_DATA_POINTS,
    RECONCILIATION_GAP_POPULATION_OVERRIDES,
)

logger = structlog.get_logger()

# Found live 2026-10-03, by direct user report ("why only 82 active
# companies... dividend -> report -> dividend paying stocks"): every item
# here used to divide by the SAME blanket total_active_companies count
# (5,216, raw status='active'), even for data points that structurally
# only apply to a real subset -- dividend_yield showed 22.32% coverage
# against ALL active companies, which looks like a huge gap but is mostly
# just "most companies never pay a dividend," not a data problem. Reuses
# `mapper/coverage_matrix.py`'s already-built, already-verified named
# populations (classify_company_populations(), analytics.company_population)
# instead of inventing a second classification system -- one source of
# truth for "which companies does this data point apply to," same
# constants `build_coverage_matrix()`'s own per-company gap_reason logic
# already uses.
_FAMILY_POPULATION: dict[str, str] = {}
for _name in DIVIDEND_FAMILY_DATA_POINTS:
    _FAMILY_POPULATION[_name] = "dividend_payer"
for _name in BUYBACK_FAMILY_DATA_POINTS:
    _FAMILY_POPULATION[_name] = "buyback_company"
for _name in CAPITAL_RETURN_FAMILY_DATA_POINTS:
    _FAMILY_POPULATION[_name] = "capital_return_company"
for _name in BDC_FAMILY_DATA_POINTS:
    _FAMILY_POPULATION[_name] = "bdc_company"
# Found live 2026-10-10 (doc 50 Phase 4): this file builds its own
# _FAMILY_POPULATION independently of coverage_matrix.py's
# build_registry() (which already picked up RECONCILIATION_GAP_
# POPULATION_OVERRIDES) -- the two must stay in sync, same reasoning as
# every other family dict above being imported rather than re-derived.
_FAMILY_POPULATION.update(RECONCILIATION_GAP_POPULATION_OVERRIDES)

# Default for everything NOT in a named family above: real_operating_company
# (~4,818), not raw status='active' (5,216) -- the corrected denominator
# this project already adopted for revenue on 2026-09-12 (SPACs/trusts/
# passthrough vehicles structurally can't have most fundamentals either),
# generalized here to every concept/metric rather than re-deriving it.
_DEFAULT_POPULATION = "real_operating_company"

# The 20 metric_definition rows doc 02 actually locked for V1 (18
# product-facing metrics; revenue/EPS growth each split into YoY and
# 3Y-CAGR rows -- see mapper/definitions.py's own module docstring).
# Sourced directly from that module, never duplicated by hand, so this
# list can never silently drift from what's actually locked.
CORE_V1_METRIC_NAMES = frozenset(name for name, *_rest in _V1_METRIC_DEFINITIONS)


def _pct(covered: int, total: int) -> Decimal:
    if total == 0:
        return Decimal("0.00")
    return (Decimal(covered) / Decimal(total) * 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def _load_total_active_companies(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("select count(*) from core.company where status = 'active'")
        return cur.fetchone()[0]


def _load_population_counts(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(
            "select population_name, count(*) from analytics.company_population group by population_name"
        )
        return dict(cur.fetchall())


def _denominator_for(item_name: str, population_counts: dict[str, int], total_active: int) -> int:
    """The semantically-correct denominator for one concept/metric --
    its named family's population if it has one, else real_operating_
    company, falling back to raw total_active only if that population
    is somehow missing (classify_company_populations() never run)."""
    population_name = _FAMILY_POPULATION.get(item_name, _DEFAULT_POPULATION)
    return population_counts.get(population_name) or total_active


def _load_concept_coverage(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select cc.name, count(distinct cf.company_id)
            from analytics.canonical_concept cc
            left join analytics.canonical_fact cf on cf.canonical_concept_id = cc.id
            group by cc.name
            """
        )
        return dict(cur.fetchall())


def _load_metric_coverage(conn: psycopg.Connection) -> dict[str, int]:
    """`analytics.metric_value` stores an explicit row with `is_null_reason`
    set even when a metric couldn't be computed for a company (the same
    traceability discipline as `excluded_missing_data` elsewhere in this
    project) -- `value is not null` is required here, or every metric
    would silently show 100% coverage regardless of how many of its rows
    are real. Found live 2026-09-02 building this module's first real
    snapshot: market_cap showed 5,216/5,216 companies before this filter,
    3,131/5,216 after -- the true number."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select md.metric_name, count(distinct mv.company_id) filter (where mv.value is not null)
            from analytics.metric_definition md
            left join analytics.metric_value mv on mv.metric_definition_id = md.id
            where md.status = 'active'
            group by md.metric_name
            """
        )
        return dict(cur.fetchall())


def compute_snapshot(conn: psycopg.Connection, as_of: date | None = None) -> dict:
    """Pure-ish computation (no writes) -- returns the rows a snapshot would
    contain, for testing and for the write path below to share."""
    as_of = as_of or date.today()
    total_active = _load_total_active_companies(conn)
    population_counts = _load_population_counts(conn)
    concept_coverage = _load_concept_coverage(conn)
    metric_coverage = _load_metric_coverage(conn)

    rows = []
    for name, covered in sorted(concept_coverage.items()):
        denom = _denominator_for(name, population_counts, total_active)
        rows.append(
            {
                "snapshot_date": as_of,
                "item_type": "concept",
                "item_name": name,
                "companies_covered": covered,
                "total_active_companies": denom,
                "coverage_pct": _pct(covered, denom),
            }
        )
    for name, covered in sorted(metric_coverage.items()):
        denom = _denominator_for(name, population_counts, total_active)
        rows.append(
            {
                "snapshot_date": as_of,
                "item_type": "metric",
                "item_name": name,
                "companies_covered": covered,
                "total_active_companies": denom,
                "coverage_pct": _pct(covered, denom),
            }
        )

    concept_pcts = [r["coverage_pct"] for r in rows if r["item_type"] == "concept"]
    metric_pcts = [r["coverage_pct"] for r in rows if r["item_type"] == "metric"]
    core_v1_pcts = [
        r["coverage_pct"]
        for r in rows
        if r["item_type"] == "metric" and r["item_name"] in CORE_V1_METRIC_NAMES
    ]
    avg_concept = (
        (sum(concept_pcts) / len(concept_pcts)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if concept_pcts
        else Decimal("0.00")
    )
    avg_metric = (
        (sum(metric_pcts) / len(metric_pcts)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if metric_pcts
        else Decimal("0.00")
    )
    avg_core_v1 = (
        (sum(core_v1_pcts) / len(core_v1_pcts)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if core_v1_pcts
        else Decimal("0.00")
    )

    # Found live 2026-10-03, direct user report: these 3 "score" rows used
    # to set BOTH companies_covered AND total_active_companies to the same
    # len(pcts) value (e.g. 82 for avg_metric_coverage_score, the metric
    # COUNT, not a company count) -- always reading as a meaningless 100%
    # on those 2 columns and, read out of context, looking like "only 82
    # active companies" exist. companies_covered now means what it always
    # meant for a score row (how many items were averaged); total_active_
    # companies is the REAL active-company count for honest context, not
    # a copy of companies_covered.
    rows.append(
        {
            "snapshot_date": as_of,
            "item_type": "score",
            "item_name": "avg_concept_coverage_score",
            "companies_covered": len(concept_pcts),
            "total_active_companies": total_active,
            "coverage_pct": avg_concept,
        }
    )
    rows.append(
        {
            "snapshot_date": as_of,
            "item_type": "score",
            "item_name": "avg_metric_coverage_score",
            "companies_covered": len(metric_pcts),
            "total_active_companies": total_active,
            "coverage_pct": avg_metric,
        }
    )
    rows.append(
        {
            "snapshot_date": as_of,
            "item_type": "score",
            "item_name": "avg_core_v1_metric_coverage_score",
            "companies_covered": len(core_v1_pcts),
            "total_active_companies": total_active,
            "coverage_pct": avg_core_v1,
        }
    )
    return {
        "rows": rows,
        "avg_concept_coverage_score": avg_concept,
        "avg_metric_coverage_score": avg_metric,
        "avg_core_v1_metric_coverage_score": avg_core_v1,
        "total_active_companies": total_active,
    }


def write_snapshot(conn: psycopg.Connection, as_of: date | None = None) -> dict:
    # UTC, not local date.today() -- found live 2026-09-04: the Postgres
    # server runs UTC while a local dev machine can run a different zone
    # (this project's own machine is IST, UTC+5:30), so a snapshot
    # written locally just after UTC midnight lands under tomorrow's
    # date by local-clock reckoning while the DB's own current_date
    # still reads today -- any same-day verification query using SQL's
    # current_date then silently reads yesterday's real row and looks
    # like data corruption. That's the actual root cause of the
    # previously-unexplained "coverage_snapshot insert anomaly"
    # (doc/learnings/2026-09-03-coverage-snapshot-insert-anomaly.md) --
    # not a write bug at all. UTC keeps every environment (a GitHub
    # Actions runner, which is also UTC, and any local machine)
    # agreeing on the same snapshot_date for "today."
    as_of = as_of or datetime.now(timezone.utc).date()
    result = compute_snapshot(conn, as_of)
    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.coverage_snapshot where snapshot_date = %s", (as_of,)
        )
        cur.executemany(
            """
            insert into analytics.coverage_snapshot
                (snapshot_date, item_type, item_name, companies_covered, total_active_companies, coverage_pct)
            values (%(snapshot_date)s, %(item_type)s, %(item_name)s, %(companies_covered)s, %(total_active_companies)s, %(coverage_pct)s)
            """,
            result["rows"],
        )
    conn.commit()
    stats = {
        "snapshot_date": as_of.isoformat(),
        "rows_written": len(result["rows"]),
        "avg_concept_coverage_score": str(result["avg_concept_coverage_score"]),
        "avg_metric_coverage_score": str(result["avg_metric_coverage_score"]),
        "avg_core_v1_metric_coverage_score": str(
            result["avg_core_v1_metric_coverage_score"]
        ),
        "total_active_companies": result["total_active_companies"],
    }
    logger.info("coverage_snapshot.written", **stats)
    return stats
