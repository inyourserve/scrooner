"""Impact analysis (2026-09-08) -- the "blast radius" tool named in
doc/data-moat/scope/internal-auto-fixer.md ("Which companies? Which
periods? Which screener filters? ... Which saved screens? Which users
were exposed?"). Built as real graph traversal over data this project
already has -- analytics.metric_definition_input (concept -> metric,
the exact edge Mapper's calculate.py itself reads) and app.
saved_screen.query (a real JSONB column, so "which saved screens
reference this metric" is a real query, not a guess).

Deliberately scoped to what's actually traceable in this schema.
"Which users were exposed" is answered honestly as "users with a
saved screen referencing an affected metric" (a real, queryable
proxy) -- there is no page-view/session log to trace exposure through
the live screener UI itself, and this module does not invent one."""

import psycopg


def concept_to_metrics(conn: psycopg.Connection, concept_name: str) -> list[dict]:
    """Every metric_definition that reads this canonical_concept as an
    input, via the real metric_definition_input edge -- the same table
    calculate.py's generic engine reads to resolve a metric's formula
    inputs. Empty result is a real, honest signal (concept feeds no
    locked metric formula) not a query failure."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select md.id, md.metric_name, mdi.role
            from analytics.canonical_concept cc
            join analytics.metric_definition_input mdi on mdi.canonical_concept_id = cc.id
            join analytics.metric_definition md on md.id = mdi.metric_definition_id
            where cc.name = %s
            order by md.metric_name
            """,
            (concept_name,),
        )
        return [
            {"metric_definition_id": r[0], "metric_name": r[1], "role": r[2]}
            for r in cur.fetchall()
        ]


def metric_to_saved_screens(conn: psycopg.Connection, metric_name: str) -> list[dict]:
    """Real saved screens whose stored ScreenQuery JSON references this
    metric name -- either as a filter predicate's field or as sort_by.
    A direct jsonb query against app.saved_screen.query, not an
    estimate."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select ss.id, ss.user_id, ss.name
            from app.saved_screen ss
            where ss.query::text like %s
               or ss.query->>'sort_by' = %s
            """,
            (f'%"{metric_name}"%', metric_name),
        )
        return [
            {"saved_screen_id": r[0], "user_id": str(r[1]), "name": r[2]}
            for r in cur.fetchall()
        ]


def concept_affected_companies(conn: psycopg.Connection, concept_name: str) -> dict:
    """How many companies actually have a canonical_fact row for this
    concept -- the real population a bug in this concept's mapping/
    resolution would touch, not an assumption."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select count(distinct cf.company_id)
            from analytics.canonical_concept cc
            join analytics.canonical_fact cf on cf.canonical_concept_id = cc.id
            where cc.name = %s
            """,
            (concept_name,),
        )
        return {"affected_companies": cur.fetchone()[0]}


def impact_report(conn: psycopg.Connection, concept_name: str) -> dict:
    """Full blast-radius report for one canonical_concept: which
    metrics it feeds, which saved screens reference each of those
    metrics, and how many real companies carry data under this concept
    today. This is the concrete, DB-backed version of the scope doc's
    'impact graph' -- Concept -> Metrics -> Saved Screens, each edge a
    real query, not an inferred relationship."""
    metrics = concept_to_metrics(conn, concept_name)
    affected = concept_affected_companies(conn, concept_name)

    metric_impacts = []
    total_screens = 0
    for m in metrics:
        screens = metric_to_saved_screens(conn, m["metric_name"])
        total_screens += len(screens)
        metric_impacts.append({**m, "saved_screens": screens})

    return {
        "concept": concept_name,
        "affected_companies": affected["affected_companies"],
        "metrics_fed": [m["metric_name"] for m in metrics],
        "metric_impacts": metric_impacts,
        "total_saved_screens_touched": total_screens,
    }


def render_markdown(report: dict) -> str:
    lines = [f"# Impact Analysis: `{report['concept']}`", ""]
    lines.append(
        f"- Companies with data under this concept: **{report['affected_companies']:,}**"
    )
    lines.append(
        f"- Metrics fed by this concept: **{len(report['metrics_fed'])}** ({', '.join(report['metrics_fed']) or 'none'})"
    )
    lines.append(
        f"- Saved screens touched (any fed metric referenced): **{report['total_saved_screens_touched']}**"
    )
    lines.append("")

    if not report["metric_impacts"]:
        lines.append(
            "_No metric_definition reads this concept as a formula input -- either it's a statement-display-only concept (never wired into calculate.py) or the concept name doesn't exist._"
        )
        return "\n".join(lines)

    lines.append("## Metrics fed")
    lines.append("")
    lines.append("| Metric | Role | Saved screens |")
    lines.append("|---|---|---|")
    for m in report["metric_impacts"]:
        screen_names = ", ".join(s["name"] for s in m["saved_screens"]) or "-"
        lines.append(f"| {m['metric_name']} | {m['role']} | {screen_names} |")
    lines.append("")
    return "\n".join(lines)
