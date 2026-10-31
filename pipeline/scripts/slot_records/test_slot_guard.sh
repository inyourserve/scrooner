#!/usr/bin/env bash
# Test migration 0113 (resolver guard) on a THROWAWAY local Postgres cluster
# (never the shared database): minimal core/analytics tables, the migration,
# then the resolver write shapes found in the pipeline (delete-then-insert,
# update, upsert, insert of a protected fill) with and without protection,
# and the release writer's bypass. Exits non-zero on the first failed check.
# usage: test_slot_guard.sh [work_dir]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MIG="$HERE/../../db/migrations/0113_slot_protected_cell.sql"
WORK="${1:-$(mktemp -d)}"
PORT="${PGTEST_PORT:-55433}"
BIN="$(dirname "$(command -v pg_ctl)")"
SOCK="$(mktemp -d /tmp/sg.XXXX)"  # unix socket paths are limited to 103 bytes
rm -rf "$WORK/pg"; "$BIN/initdb" -D "$WORK/pg" -U t -A trust >/dev/null
"$BIN/pg_ctl" -D "$WORK/pg" -o "-p $PORT -k $SOCK -c listen_addresses=''" -l "$WORK/pg.log" -w start >/dev/null
trap '"$BIN/pg_ctl" -D "$WORK/pg" -m immediate stop >/dev/null 2>&1 || true; rm -rf "$SOCK"' EXIT
q() { "$BIN/psql" -h "$SOCK" -p "$PORT" -U t -d postgres -v ON_ERROR_STOP=1 -qtAX "$@"; }
q -c "
create schema core; create schema analytics;
create table core.company (id bigint primary key);
create table core.period (id bigint primary key);
create table analytics.canonical_concept (id bigint primary key, name text);
create table analytics.canonical_fact (
  id bigint generated always as identity primary key,
  company_id bigint not null references core.company (id),
  canonical_concept_id bigint not null references analytics.canonical_concept (id),
  period_id bigint not null references core.period (id),
  value numeric not null, source_fact_ids bigint[] not null,
  resolved_at timestamptz not null default now(),
  unique (company_id, canonical_concept_id, period_id));
insert into core.company values (1),(2); insert into core.period values (10),(11),(12);
insert into analytics.canonical_concept values (5,'net_income_resolved'),(6,'revenue_sanity_resolved');"
q -f "$MIG"
fail=0
check() { # name, sql, expected
  got="$(q -c "$2")"
  if [[ "$got" == "$3" ]]; then echo "ok   $1"; else echo "FAIL $1: got [$got] want [$3]"; fail=1; fi
}
# 0. empty protection table: resolvers behave exactly as before
q -c "insert into analytics.canonical_fact (company_id,canonical_concept_id,period_id,value,source_fact_ids) values (1,5,10,100,'{1}'),(1,5,11,200,'{2}'),(2,5,10,300,'{3}');"
q -c "update analytics.canonical_fact set value = 301 where company_id = 2;"
check "unprotected update applies" "select value from analytics.canonical_fact where company_id=2 and period_id=10" "301"
# 1. the release writer (bypass) writes the slot value and protects the cell
q -c "begin; set local scrooner.slot_writer = 'on';
      update analytics.canonical_fact set value = 111, source_fact_ids = '{}' where company_id=1 and canonical_concept_id=5 and period_id=10;
      insert into analytics.canonical_fact (company_id,canonical_concept_id,period_id,value,source_fact_ids) values (1,5,12,333,'{}');
      insert into analytics.slot_protected_cell values (1,5,10,'slot.is_net_income@1',111,'run1','sha'),(1,5,12,'slot.is_net_income@1',333,'run1','sha');
      commit;"
check "bypass write landed" "select value from analytics.canonical_fact where company_id=1 and period_id=10" "111"
# 2. resolver shape: delete the company's concept, re-insert its own values (concept_fallback, resolve.py)
q -c "begin; delete from analytics.canonical_fact where company_id = 1 and canonical_concept_id = 5;
      insert into analytics.canonical_fact (company_id,canonical_concept_id,period_id,value,source_fact_ids) values (1,5,10,999,'{9}'),(1,5,11,222,'{8}'),(1,5,12,777,'{7}');
      commit;"
check "delete+insert keeps protected value" "select value from analytics.canonical_fact where company_id=1 and period_id=10" "111"
check "delete+insert keeps protected fill" "select value from analytics.canonical_fact where company_id=1 and period_id=12" "333"
check "delete+insert still rewrites unprotected cell" "select value from analytics.canonical_fact where company_id=1 and period_id=11" "222"
check "no duplicate rows" "select count(*) from analytics.canonical_fact where company_id=1" "3"
# 3. resolver shape: update in place (conflict_resolution, balance_identity)
q -c "update analytics.canonical_fact set value = 555 where company_id=1 and canonical_concept_id=5;"
check "update skips protected" "select value from analytics.canonical_fact where company_id=1 and period_id=10" "111"
check "update applies to unprotected" "select value from analytics.canonical_fact where company_id=1 and period_id=11" "555"
# 4. resolver shape: upsert
q -c "insert into analytics.canonical_fact (company_id,canonical_concept_id,period_id,value,source_fact_ids) values (1,5,10,4242,'{4}')
      on conflict (company_id,canonical_concept_id,period_id) do update set value = excluded.value;"
check "upsert skips protected" "select value from analytics.canonical_fact where company_id=1 and period_id=10" "111"
# 5. update that MOVES a row onto a protected key
q -c "update analytics.canonical_fact set period_id = 10 where company_id=2 and period_id=10 and canonical_concept_id=5;" # same key, unprotected company 2
q -c "update analytics.canonical_fact set company_id = 1 where company_id=2 and period_id=10;" 2>/dev/null || true
check "row cannot be moved onto a protected key" "select value from analytics.canonical_fact where company_id=1 and period_id=10" "111"
# 6. other concepts of the same company are untouched by the guard
q -c "insert into analytics.canonical_fact (company_id,canonical_concept_id,period_id,value,source_fact_ids) values (1,6,10,50,'{5}');
      update analytics.canonical_fact set value = 51 where company_id=1 and canonical_concept_id=6;"
check "other concept unaffected" "select value from analytics.canonical_fact where company_id=1 and canonical_concept_id=6" "51"
# 7. every skipped write is logged
check "skips logged" "select count(*) > 0 from analytics.slot_protected_write_skipped where company_id=1 and canonical_concept_id=5" "t"
# 8. rollback of the run (bypass): restore the before-image and drop protection; resolvers work again
q -c "begin; set local scrooner.slot_writer = 'on';
      update analytics.canonical_fact set value = 100, source_fact_ids = '{1}' where company_id=1 and canonical_concept_id=5 and period_id=10;
      delete from analytics.canonical_fact where company_id=1 and canonical_concept_id=5 and period_id=12;
      delete from analytics.slot_protected_cell where run_id = 'run1';
      commit;"
q -c "update analytics.canonical_fact set value = 101 where company_id=1 and canonical_concept_id=5 and period_id=10;"
check "after rollback the resolver writes again" "select value from analytics.canonical_fact where company_id=1 and canonical_concept_id=5 and period_id=10" "101"
check "rolled-back fill removed" "select count(*) from analytics.canonical_fact where company_id=1 and canonical_concept_id=5 and period_id=12" "0"
# 9. the bypass is per transaction (set local) and does not leak to the next statement
q -c "begin; set local scrooner.slot_writer = 'on'; insert into analytics.slot_protected_cell values (1,5,11,'r',555,'run2','sha'); commit;"
q -c "update analytics.canonical_fact set value = 1 where company_id=1 and period_id=11 and canonical_concept_id=5;"
check "bypass does not leak" "select value from analytics.canonical_fact where company_id=1 and period_id=11 and canonical_concept_id=5" "555"
exit $fail
