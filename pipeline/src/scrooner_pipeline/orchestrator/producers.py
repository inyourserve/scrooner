"""Event producers (PIPELINE.md section 3): each turns something that changed into rows of ops.pipeline_event.

  new_filing       core.filing periodic filings of a cohort company that fsn.filing does not hold yet (stage 1 first)
  rule_version     a git range's resolver/rules changes, per company, through scripts/ci/top100_changed.py (the same diff
                   rule the auto trigger uses: resolver_version ignored); shared rules carry no company key, so they go in
                   as a '*' event the planner scopes through the rule usage index (unscoped, nothing queued, when none)
  rank_change      cohort members with no served versions yet (they just entered the rank set)
  template_change  a template seed version for a set of companies (explicit, from the template seeding job)

Every producer is idempotent (events are unique on cik, cause, versions) and returns how many events were NEW.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import psycopg

from .store import emit_event

ROOT = Path(__file__).resolve().parents[4]
PERIODIC = (
    "10-K",
    "10-K/A",
    "10-KT",
    "10-Q",
    "10-Q/A",
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
)
SINCE = "2014-01-01"
SHARED_RULES = re.compile(r"^data-team/tags/line_map/rules/([^/]+)$")


def new_filings(conn: psycopg.Connection, members, since: str = SINCE) -> int:
    """One new_filing event per company with periodic filings in core.filing and not in fsn.filing."""
    conn.execute("set statement_timeout = '120s'")
    ciks = [m.cik for m in members]
    rows = conn.execute(
        """select c.cik, array_agg(f.accession_number order by f.accession_number)
           from core.filing f join core.company c on c.id = f.company_id
           where c.cik = any(%s) and f.form = any(%s) and f.period_of_report >= %s
             and not exists (select 1 from fsn.filing x where x.accession = f.accession_number)
           group by c.cik""",
        (ciks, list(PERIODIC), since),
    ).fetchall()
    new = 0
    with conn.transaction():
        for cik, accs in rows:
            new += emit_event(
                conn,
                cik=cik,
                cause="new_filing",
                versions={"accessions": list(accs), "from_stage": 1},
                source="collector",
            )
    return new


def rule_changes(
    conn: psycopg.Connection, members, base: str, head: str, root: Path = ROOT
) -> dict[str, int]:
    """rule_version events for the companies whose resolver rows changed between two git shas (read-only git)."""
    out = subprocess.run(
        [sys.executable, "-I", "scripts/ci/top100_changed.py", "companies", base, head],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if out.returncode not in (0,):
        raise RuntimeError(
            f"top100_changed.py exit {out.returncode}: {out.stderr.strip()[:300]}"
        )
    ids = {int(x) for x in out.stdout.strip().split(",") if x}
    by_id = {m.company_id: m for m in members}
    per_company = 0
    with conn.transaction():
        for cid in sorted(ids & set(by_id)):
            per_company += emit_event(
                conn,
                cik=by_id[cid].cik,
                cause="rule_version",
                versions={
                    "rule": f"resolver:{by_id[cid].ticker}",
                    "range": f"{base[:12]}..{head[:12]}",
                    "from_stage": 3,
                },
                source="git",
            )
        shared = 0
        names = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                base,
                head,
                "--",
                "data-team/tags/line_map/rules",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        ).stdout.split()
        for n in names:
            m = SHARED_RULES.match(n)
            if m:
                shared += emit_event(
                    conn,
                    cik="*",
                    cause="rule_version",
                    versions={"rule": m.group(1), "range": head[:12]},
                    source="git",
                )
    return {
        "company_events": per_company,
        "shared_events": shared,
        "outside_cohort": len(ids - set(by_id)),
    }


def rank_changes(conn: psycopg.Connection, members, rank_set: str) -> int:
    """Members that have never been served (they entered the rank set) get a rank_change event."""
    served = {
        r[0]
        for r in conn.execute("select cik from ops.company_served_version").fetchall()
    }
    new = 0
    with conn.transaction():
        for m in members:
            if m.cik not in served:
                new += emit_event(
                    conn,
                    cik=m.cik,
                    cause="rank_change",
                    versions={"rank_set": rank_set},
                    source="rank_job",
                )
    return new


def seed_templates(
    conn: psycopg.Connection, members, root: Path = ROOT, *, write: bool = True
) -> dict[str, Any]:
    """Seed the sector_default template (mapper/sector_templates.py, the catalog plan) for cohort members that have no
    analytics.company_data_point_template row, then emit one template_change event each. A company with no template cannot
    be proved or gated (scrooner-36, M6-PREP: ranks 1,001-5,000 are unseeded). One transaction, batched (write_plan); a
    company whose sector group has no template definition is reported in `failed` and gets no event. write=False (dry run)
    only reports who would be seeded."""
    from scrooner_pipeline.mapper import sector_templates as st

    have = {
        r[0]
        for r in conn.execute(
            "select distinct company_id from analytics.company_data_point_template"
        )
    }
    todo = [m for m in members if m.company_id not in have]
    sics = dict(
        conn.execute(
            "select id, sic_code from core.company where id = any(%s)",
            ([m.company_id for m in todo],),
        ).fetchall()
    )
    concepts = st.load_catalog(root / st.CATALOG_PATH)
    plan, failed, ok = [], {}, []
    for m in todo:
        sic = sics.get(m.company_id)
        rc = st.RankedCompany(
            m.rank,
            m.company_id,
            m.cik,
            m.ticker,
            int(sic) if sic and str(sic).isdigit() else None,
        )
        try:
            plan += st.build_catalog_plan(concepts, [rc])
            ok.append(m)
        except st.TemplateError as e:
            failed[m.ticker] = str(e)[:200]
    out: dict[str, Any] = {
        "missing": len(todo),
        "seeded": 0,
        "failed": failed,
        "events": 0,
    }
    if write and plan:
        st.write_plan(conn, plan)
        out["seeded"] = len(ok)
        out["events"] = template_change(conn, [m.cik for m in ok], st.CATALOG_VERSION)
    return out


def template_change(
    conn: psycopg.Connection,
    ciks: list[str],
    template: str,
    extra: dict[str, Any] | None = None,
) -> int:
    new = 0
    with conn.transaction():
        for cik in ciks:
            new += emit_event(
                conn,
                cik=cik,
                cause="template_change",
                versions={"template": template, **(extra or {})},
                source="template_seed",
            )
    return new
