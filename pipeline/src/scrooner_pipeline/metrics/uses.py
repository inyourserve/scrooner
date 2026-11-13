""" "Which company uses which calculation", generated and read-only.

Two sources, never authored:
  * per value: the cell record (provenance.CellRecord / cell_proof.checks) names the formula
    id@version, each input cell's status and the company_tag_map rule_id and rules_commit behind it;
  * per company: the views in pipeline/db/pending/0126_metric_lineage_view.sql
    (analytics.v_company_metric_inputs, analytics.v_company_metric_status), which exist only once
    that migration is applied. Until then `company_metric_status` fails with a clear message.

Single connection, indexed by company_id, statement_timeout set by the caller.
"""

from __future__ import annotations

from scrooner_pipeline.metrics.applicability import applicability
from scrooner_pipeline.metrics.registry import get_registry

STATUS_SQL = """
select metric_name, formula_version, status, reason, template, period_label, period_end, latest_value
from analytics.v_company_metric_status where company_id = %s order by metric_name
"""
INPUTS_SQL = """
select metric_name, role, input_concept, feed_status, taxonomy, tag, stmt, era_from, era_to, rule_id,
       evidence_adsh, input_proof_verdict
from analytics.v_company_metric_inputs where company_id = %s and metric_name = any(%s)
order by metric_name, input_concept, era_from
"""


def company_metric_status(
    conn, company_id: int, group: str | None = None
) -> list[dict]:
    """One row per metric: the database status, the registry formula ref, and (when `group` is given)
    the registry applicability. A metric whose group applicability is OUT but which has a value is
    reported as `conflict`, never silently kept."""
    reg = get_registry()
    with conn.cursor() as cur:
        cur.execute(STATUS_SQL, (company_id,))
        rows = cur.fetchall()
    out = []
    for name, ver, status, reason, template, label, end, value in rows:
        m = reg.get(name)
        row = {
            "metric": name,
            "db_formula_version": ver,
            "status": status,
            "reason": reason,
            "template": template,
            "period_label": label,
            "period_end": end,
            "latest_value": value,
            "registry_ref": m.formula_ref if m else None,
        }
        if m and group:
            a = applicability(m, group)
            row["applicability"] = a.status
            row["applicability_reason"] = a.reason
            if a.status == "OUT" and status == "COMPUTED":
                row["status"] = "conflict"
        out.append(row)
    return out


def company_metric_inputs(conn, company_id: int, metric_names: list[str]) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(INPUTS_SQL, (company_id, metric_names))
        cols = [d.name for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]
