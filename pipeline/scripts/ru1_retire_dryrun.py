"""RU-1 retirement DRY-RUN (WO-2, 2026-10-22). READ-ONLY: writes CSV files only.

Lists, for the reviewed dry-run before any live retirement:
  1. core.fact rows to DEMOTE (is_authoritative -> false, never deleted):
     derived facts (is_derived) that are per-share or ratio values -- unit
     contains '/' or is 'pure', or the tag matches derived.PER_SHARE_TAG_REGEX.
     Also derived facts whose own filing is not a 10-K/10-Q-family form (the
     deriver anchored them on a DEF 14A / 8-K FY: JPM core.fact 182608846).
  2. analytics.canonical_fact rows to ARCHIVE then remove (into
     analytics.canonical_fact_retired, migration 0098): rows whose
     source_fact_ids include a row of list 1.
  3. analytics.metric_value rows whose source_fact_ids include a row of list 1
     (they are recomputed, not retired).
No date cut (the 2026-10-21 census stopped at 2015-01-01). Heavy: about 40
minutes over the population on one connection (census.log 2026-10-21). Run
it only in the heavy-db slot (doc 53, ListAgents first), never beside
another heavy job.

Usage (from pipeline/):
  uv run python scripts/ru1_retire_dryrun.py OUT_DIR [--ciks 0000789019,...]
"""

import argparse
import csv
import time

import psycopg

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.derivation_policy import PERIODIC_FORMS_DOMESTIC
from scrooner_pipeline.normalizer.derived import PER_SHARE_TAG_REGEX

CHUNK = 100

FACTS_SQL = """
select f.id, f.company_id, c.tag, u.unit_name, p.fiscal_period, p.start_date, p.end_date,
       f.value, f.is_authoritative, fl.form,
       case when f.concept_id = any(%(cids)s) or f.unit_id = any(%(uids)s)
            then 'per_share_or_ratio' else 'non_periodic_input' end as reason
from core.fact f
join core.unit u on u.id = f.unit_id
join core.concept c on c.id = f.concept_id
join core.period p on p.id = f.period_id
join core.filing fl on fl.id = f.filing_id
where f.company_id = any(%(ids)s) and f.is_derived and f.is_authoritative
  and (f.concept_id = any(%(cids)s) or f.unit_id = any(%(uids)s)
       or not (fl.form = any(%(forms)s)))
"""

CANON_SQL = """
select cf.id, cf.company_id, cc.name, p.fiscal_period, p.end_date, cf.value, cf.source_fact_ids
from analytics.canonical_fact cf
join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
join core.period p on p.id = cf.period_id
where cf.company_id = any(%(ids)s) and cf.source_fact_ids && %(fids)s::bigint[]
"""

METRIC_SQL = """
select mv.id, mv.company_id, md.metric_name, mv.period_label, mv.period_end, mv.value
from analytics.metric_value mv
join analytics.metric_definition md on md.id = mv.metric_definition_id
where mv.company_id = any(%(ids)s) and mv.source_fact_ids && %(fids)s::bigint[]
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--ciks", default=None)
    ap.add_argument("--statement-timeout", default="60s")
    args = ap.parse_args()
    t0 = time.time()
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        cur = conn.cursor()
        cur.execute(
            "select set_config(%s, %s, false)",
            ("statement_timeout", args.statement_timeout),
        )
        cur.execute("set default_transaction_read_only = on")
        cur.execute(
            "select id from core.concept where tag ~ %s", (PER_SHARE_TAG_REGEX,)
        )
        cids = [r[0] for r in cur.fetchall()]
        cur.execute(
            "select id from core.unit where unit_name like '%%/%%' or unit_name = 'pure'"
        )
        uids = [r[0] for r in cur.fetchall()]
        if args.ciks:
            cur.execute(
                "select id from core.company where cik = any(%s) order by id",
                ([c.strip().zfill(10) for c in args.ciks.split(",")],),
            )
        else:
            cur.execute("select id from core.company order by id")
        ids = [r[0] for r in cur.fetchall()]
        files = {
            name: open(f"{args.out_dir}/ru1_{name}.csv", "w", newline="")
            for name in (
                "demote_core_fact",
                "archive_canonical_fact",
                "recompute_metric_value",
            )
        }
        writers = {name: csv.writer(fh) for name, fh in files.items()}
        writers["demote_core_fact"].writerow(
            [
                "fact_id",
                "company_id",
                "tag",
                "unit",
                "fiscal_period",
                "start_date",
                "end_date",
                "value",
                "is_authoritative",
                "form",
                "reason",
            ]
        )
        writers["archive_canonical_fact"].writerow(
            [
                "canonical_fact_id",
                "company_id",
                "concept",
                "fiscal_period",
                "end_date",
                "value",
                "source_fact_ids",
            ]
        )
        writers["recompute_metric_value"].writerow(
            [
                "metric_value_id",
                "company_id",
                "metric",
                "period_label",
                "period_end",
                "value",
            ]
        )
        counts = {name: 0 for name in files}
        for i in range(0, len(ids), CHUNK):
            chunk = ids[i : i + CHUNK]
            cur.execute(
                FACTS_SQL,
                {
                    "ids": chunk,
                    "cids": cids,
                    "uids": uids,
                    "forms": sorted(PERIODIC_FORMS_DOMESTIC),
                },
            )
            rows = cur.fetchall()
            fids = [r[0] for r in rows]
            for r in rows:
                writers["demote_core_fact"].writerow(r)
            counts["demote_core_fact"] += len(rows)
            if fids:
                cur.execute(CANON_SQL, {"ids": chunk, "fids": fids})
                for r in cur.fetchall():
                    writers["archive_canonical_fact"].writerow(r)
                    counts["archive_canonical_fact"] += 1
                cur.execute(METRIC_SQL, {"ids": chunk, "fids": fids})
                for r in cur.fetchall():
                    writers["recompute_metric_value"].writerow(r)
                    counts["recompute_metric_value"] += 1
            print(
                f"companies {i + len(chunk)}/{len(ids)} {counts} {time.time() - t0:.0f}s",
                flush=True,
            )
        for fh in files.values():
            fh.close()
    print("done", counts)


if __name__ == "__main__":
    main()
