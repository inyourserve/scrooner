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
every other coverage query this project has run live.

Template coverage (founder ruling 2026-11-01, doc 02, migration 0120): once
analytics.company_data_point_template holds rows, coverage = valued cells /
template cells. A cell is (company, data point) where the company's CURRENT
template (its rows at the latest effective_from <= as_of) has in_template = true.
Each concept/metric row then counts template companies (denominator) and those of
them with a value (numerator); a data point in no template is not a cell and gets
no row. The score row template_cell_coverage_score is the sum of valued template
cells over the sum of template cells (its companies_covered / total_active_companies
columns hold those two cell counts). A template data point that no concept or
metric produces still counts as template cells with 0 valued, so it shows as a gap.
Until 0120 is applied and seeded the snapshot keeps the population denominators
below and logs coverage_snapshot.template_mode_off (reporting only; no value is
ever taken from anywhere else)."""

from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.mapper.definitions import (
    METRIC_DEFINITIONS as _V1_METRIC_DEFINITIONS,
)
from scrooner_pipeline.mapper.coverage_matrix import (
    FILING_LINE_STRUCTURAL_REASONS,
    BDC_FAMILY_DATA_POINTS,
    BUYBACK_FAMILY_DATA_POINTS,
    CAPITAL_RETURN_FAMILY_DATA_POINTS,
    DIVIDEND_CONCEPT_DATA_POINTS,
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
# 2026-10-11: see coverage_matrix.py's own comment on
# DIVIDEND_CONCEPT_DATA_POINTS/dividend_family_ever_reported -- the raw
# concepts themselves need a broader, "ever reported" population, not
# dividend_payer's deliberately current-state-only one.
for _name in DIVIDEND_CONCEPT_DATA_POINTS:
    _FAMILY_POPULATION[_name] = "dividend_family_ever_reported"
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


def _load_filing_line_na_counts(conn: psycopg.Connection) -> dict[str, int]:
    """Per data point: how many companies in the default population have NO value
    and whose own latest filing shows the standalone line is not presented
    (coverage_matrix.apply_filing_line_evidence). The line does not exist for them
    on the statements, so they are not part of what a "complete" count should reach.
    Only ever the two structural filing-line reasons -- a line that IS in the filing
    but not extracted stays in the denominator as the real gap it is."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select cov.data_point_name, count(*)
            from analytics.company_data_point_coverage cov
            join analytics.company_population p
              on p.company_id = cov.company_id and p.population_name = %s
            where cov.has_value = false and cov.gap_reason = any(%s)
            group by cov.data_point_name
            """,
            (_DEFAULT_POPULATION, list(FILING_LINE_STRUCTURAL_REASONS)),
        )
        return dict(cur.fetchall())


def _denominator_for(
    item_name: str, population_counts: dict[str, int], total_active: int
) -> int:
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


METRIC_COVERAGE_SQL = """
    select md.metric_name,
           count(distinct mv.company_id) filter (
               where mv.value is not null
                 and (not (coalesce(m.population_name, %(default)s) = any(%(restricted)s::text[]))
                      or p.company_id is not null)
           ) as covered_in_population,
           count(distinct mv.company_id) filter (where mv.value is not null) as covered_any
    from analytics.metric_definition md
    left join unnest(%(names)s::text[], %(pops)s::text[]) as m(metric_name, population_name)
      on m.metric_name = md.metric_name
    left join analytics.metric_value mv on mv.metric_definition_id = md.id
    left join analytics.company_population p
      on p.company_id = mv.company_id
     and p.population_name = coalesce(m.population_name, %(default)s)
    where md.status = 'active'
    group by md.metric_name
"""


def _load_metric_coverage(
    conn: psycopg.Connection, population_counts: dict[str, int]
) -> dict[str, tuple[int, int]]:
    """metric_name -> (companies with a value INSIDE the metric's denominator
    population, companies with a value anywhere).

    `analytics.metric_value` stores an explicit row with `is_null_reason`
    set even when a metric couldn't be computed for a company (the same
    traceability discipline as `excluded_missing_data` elsewhere in this
    project) -- `value is not null` is required here, or every metric
    would silently show 100% coverage regardless of how many of its rows
    are real. Found live 2026-09-02 building this module's first real
    snapshot: market_cap showed 5,216/5,216 companies before this filter,
    3,131/5,216 after -- the true number.

    Found 2026-10-18 (ROE 4,818 of 4,815 = 100.06%): the denominator is a named
    population (real_operating_company, ...) but the numerator used to count a
    company with a value from ANYWHERE, including companies outside that population
    (reclassified out since their metric rows were written; metric_value rows are
    never deleted when a company leaves a population). The numerator is now
    restricted to the same population as the denominator. A population with no rows
    (classify_company_populations never run) is not restricted -- the denominator
    falls back to total_active in that case, see _denominator_for."""
    names = sorted(_FAMILY_POPULATION)
    params = {
        "names": names,
        "pops": [_FAMILY_POPULATION[n] for n in names],
        "default": _DEFAULT_POPULATION,
        "restricted": [p for p, n in population_counts.items() if n],
    }
    with conn.cursor() as cur:
        cur.execute(METRIC_COVERAGE_SQL, params)
        return {name: (int(a), int(b)) for name, a, b in cur.fetchall()}


TEMPLATE_TABLE = "analytics.company_data_point_template"

TEMPLATE_PRESENT_SQL = "select to_regclass(%s) is not null as template_table_present"

TEMPLATE_COVERAGE_SQL = """
    with latest as (
        select company_id, max(effective_from) as effective_from
        from analytics.company_data_point_template
        where effective_from <= %(as_of)s
        group by company_id
    ), cells as (
        select t.company_id, t.data_point
        from analytics.company_data_point_template t
        join latest l on l.company_id = t.company_id and l.effective_from = t.effective_from
        where t.in_template
    )
    select c.data_point,
           count(*) as template_cells,
           count(*) filter (where exists (
               select 1
               from analytics.canonical_fact cf
               join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
               where cf.company_id = c.company_id and cc.name = c.data_point
           )) as concept_valued,
           count(*) filter (where exists (
               select 1
               from analytics.metric_value mv
               join analytics.metric_definition md on md.id = mv.metric_definition_id
               where mv.company_id = c.company_id and md.metric_name = c.data_point
                 and md.status = 'active' and mv.value is not null
           )) as metric_valued
    from cells c
    group by c.data_point
"""

PRODUCER_NAMES_SQL = """
    select 'concept' as kind, name from analytics.canonical_concept
    union all
    select 'metric', metric_name from analytics.metric_definition where status = 'active'
"""


def _load_template_coverage(
    conn: psycopg.Connection, as_of: date
) -> dict[str, tuple[int, int, int]] | None:
    """data_point -> (template cells, cells valued as a concept, cells valued as a
    metric). None when the template table does not exist yet (0120 not applied)."""
    with conn.cursor() as cur:
        cur.execute(TEMPLATE_PRESENT_SQL, (TEMPLATE_TABLE,))
        row = cur.fetchone()
        if not row or not row[0]:
            return None
        cur.execute(TEMPLATE_COVERAGE_SQL, {"as_of": as_of})
        return {dp: (int(n), int(cv), int(mv)) for dp, n, cv, mv in cur.fetchall()}


def _load_producer_names(conn: psycopg.Connection) -> tuple[set[str], set[str]]:
    with conn.cursor() as cur:
        cur.execute(PRODUCER_NAMES_SQL)
        pairs = cur.fetchall()
    return (
        {name for kind, name in pairs if kind == "concept"},
        {name for kind, name in pairs if kind == "metric"},
    )


def _template_rows(
    template: dict[str, tuple[int, int, int]],
    concepts: set[str],
    metrics: set[str],
    as_of: date,
) -> tuple[list[dict[str, Any]], int, int]:
    """Concept/metric rows over template cells, plus (valued cells, template cells)."""
    rows: list[dict[str, Any]] = []
    valued_cells = 0
    template_cells = 0
    for dp, (cells, concept_valued, metric_valued) in sorted(template.items()):
        template_cells += cells
        if dp in metrics:
            valued_cells += metric_valued
        elif dp in concepts:
            valued_cells += concept_valued
        else:
            logger.warning(
                "coverage_snapshot.template_data_point_without_producer",
                data_point=dp,
                template_cells=cells,
            )
        for item_type, known, valued in (
            ("concept", dp in concepts, concept_valued),
            ("metric", dp in metrics, metric_valued),
        ):
            if known:
                rows.append(
                    {
                        "snapshot_date": as_of,
                        "item_type": item_type,
                        "item_name": dp,
                        "companies_covered": valued,
                        "total_active_companies": cells,
                        "coverage_pct": _pct(valued, cells),
                    }
                )
    return rows, valued_cells, template_cells


def compute_snapshot(conn: psycopg.Connection, as_of: date | None = None) -> dict:
    """Pure-ish computation (no writes) -- returns the rows a snapshot would
    contain, for testing and for the write path below to share."""
    as_of = as_of or date.today()
    # The concept/metric coverage aggregates scan canonical_fact / metric_value
    # and exceeded the pooler's 2-minute default in the 2026-10-16 nightly
    # (snapshot-coverage failed after ~2 min, leaving no snapshot for 3 days).
    with conn.cursor() as cur:
        cur.execute("set statement_timeout = '15min'")
    total_active = _load_total_active_companies(conn)
    template = _load_template_coverage(conn, as_of)
    template_mode = bool(template)
    template_cells_valued = template_cells_total = 0
    rows: list[dict[str, Any]] = []
    if template_mode:
        assert template is not None
        concepts, metrics = _load_producer_names(conn)
        rows, template_cells_valued, template_cells_total = _template_rows(
            template, concepts, metrics, as_of
        )
        concept_coverage: dict[str, int] = {}
        metric_coverage: dict[str, tuple[int, int]] = {}
        population_counts: dict[str, int] = {}
        filing_line_na: dict[str, int] = {}
    else:
        logger.warning(
            "coverage_snapshot.template_mode_off",
            reason="template table absent" if template is None else "no template rows",
        )
        population_counts = _load_population_counts(conn)
        concept_coverage = _load_concept_coverage(conn)
        metric_coverage = _load_metric_coverage(conn, population_counts)
        filing_line_na = _load_filing_line_na_counts(conn)

    for name, covered in sorted(concept_coverage.items()):
        denom = _denominator_for(name, population_counts, total_active)
        # Companies whose own filing shows the line is not presented are not "missing"
        # it. Never below what we actually covered.
        denom = max(denom - filing_line_na.get(name, 0), covered)
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
    for name, (covered, covered_any) in sorted(metric_coverage.items()):
        denom = _denominator_for(name, population_counts, total_active)
        if covered_any > covered:
            logger.info(
                "coverage_snapshot.metric_values_outside_population",
                metric=name,
                outside=covered_any - covered,
            )
        if covered > denom:
            # Only reachable when the population fell back to total_active, or the
            # population table changed between the two reads. Never publish >100%.
            logger.warning(
                "coverage_snapshot.covered_exceeds_denominator",
                metric=name,
                covered=covered,
                denominator=denom,
            )
            denom = covered
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
    template_score = _pct(template_cells_valued, template_cells_total)
    if template_mode:
        # companies_covered / total_active_companies hold CELL counts on this row:
        # valued template cells / template cells (doc 02 ruling 2026-11-01).
        rows.append(
            {
                "snapshot_date": as_of,
                "item_type": "score",
                "item_name": "template_cell_coverage_score",
                "companies_covered": template_cells_valued,
                "total_active_companies": template_cells_total,
                "coverage_pct": template_score,
            }
        )
    return {
        "rows": rows,
        "template_mode": template_mode,
        "template_cells": template_cells_total,
        "template_cells_valued": template_cells_valued,
        "template_cell_coverage_score": template_score if template_mode else None,
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
        "template_mode": result["template_mode"],
        "template_cells": result["template_cells"],
        "template_cells_valued": result["template_cells_valued"],
        "template_cell_coverage_score": (
            str(result["template_cell_coverage_score"])
            if result["template_mode"]
            else None
        ),
    }
    logger.info("coverage_snapshot.written", **stats)
    return stats
