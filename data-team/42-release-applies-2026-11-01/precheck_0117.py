"""Read-only pre-checks for migration 0117 (canonical_fact provenance). Writes nothing."""
import os
import sys

import psycopg

url = os.environ["DATABASE_URL"]
Q = {
    "read_only_db": "show default_transaction_read_only",
    "connections": "select count(*) from pg_stat_activity",
    "cols_present": """select column_name, data_type from information_schema.columns
        where table_schema='analytics' and table_name='canonical_fact'
          and column_name in ('rule_run_id','family','source_value_ids')""",
    "rule_run_pk": """select a.attname, format_type(a.atttypid,a.atttypmod), c.contype
        from pg_constraint c join pg_attribute a on a.attrelid=c.conrelid and a.attnum=any(c.conkey)
        where c.conrelid='analytics.rule_run'::regclass and c.contype in ('p','u')""",
    "rule_run_rows": "select reltuples::bigint from pg_class where oid='analytics.rule_run'::regclass",
    "cf_size": """select reltuples::bigint as est_rows,
        pg_size_pretty(pg_relation_size('analytics.canonical_fact')) heap,
        pg_size_pretty(pg_total_relation_size('analytics.canonical_fact')) total""",
    "idx_name_taken": "select indexname from pg_indexes where indexname='idx_canonical_fact_family_company'",
    "cf_triggers": """select tgname, tgenabled from pg_trigger
        where tgrelid='analytics.canonical_fact'::regclass and not tgisinternal""",
    "cf_locks_now": """select l.mode, l.granted, a.pid, a.state, now()-a.xact_start xact_age, left(a.query,80)
        from pg_locks l join pg_stat_activity a using (pid)
        where l.relation='analytics.canonical_fact'::regclass and a.pid<>pg_backend_pid()""",
    "long_xacts": """select pid, state, now()-xact_start age, left(query,80) from pg_stat_activity
        where xact_start < now()-interval '5 min' and pid<>pg_backend_pid() order by xact_start""",
    "disk_db": "select pg_size_pretty(pg_database_size(current_database()))",
}
with psycopg.connect(url, autocommit=False, connect_timeout=20) as conn:
    conn.execute("set transaction read only")
    conn.execute("set local statement_timeout='60s'")
    conn.execute("set local lock_timeout='2s'")
    for k, q in Q.items():
        try:
            print(f"{k}: {conn.execute(q).fetchall()}")
        except Exception as e:  # report and continue on a fresh savepoint-less txn
            print(f"{k}: ERROR {type(e).__name__}: {e}".splitlines()[0])
            conn.rollback()
            conn.execute("set transaction read only")
            conn.execute("set local statement_timeout='60s'")
    conn.rollback()
sys.exit(0)
