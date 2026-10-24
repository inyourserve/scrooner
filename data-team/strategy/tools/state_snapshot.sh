#!/usr/bin/env bash
# One generated state snapshot (read-only): git, applied schema, coverage build, cohort counts, workflows, DB load.
# Usage: bash data-team/strategy/tools/state_snapshot.sh > data-team/strategy/STATE-SNAPSHOT-$(date +%F).md
# Needs: pipeline/.env (DATABASE_URL), gh, git. One DB connection, 15 s timeout per statement. Writes nothing.
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; cd "$ROOT"
set -a; source pipeline/.env; set +a
q(){ PGCONNECT_TIMEOUT=10 psql "$DATABASE_URL" -X -At -F ' | ' -c "set statement_timeout=15000" -c "$1" 2>&1 | grep -v '^SET$'; }
echo "# State snapshot (GENERATED, not hand-written) $(date '+%F %T %Z')"
echo; echo "## git"; git fetch origin --quiet 2>&1 | tail -1
echo "origin/main head: $(git log origin/main -1 --format='%h %ad %s' --date=short | cut -c1-110)"
echo "local main vs origin (behind ahead): $(git rev-list --left-right --count origin/main...HEAD)"
echo "changed or untracked paths in the shared tree: $(git status --short | wc -l)"
echo "migrations on origin/main (last 3): $(git ls-tree --name-only origin/main pipeline/db/migrations/ | tail -3 | xargs -n1 basename | tr '\n' ' ')"
echo; echo "## applied schema (live DB)"
q "select 'certification_finding='||(to_regclass('analytics.certification_finding') is not null)||', company_certification='||(to_regclass('analytics.company_certification') is not null)||', has_value_any_period='||exists(select 1 from information_schema.columns where table_schema='analytics' and table_name='company_data_point_coverage' and column_name='has_value_any_period')"
echo; echo "## coverage table"
q "select 'built '||max(checked_at)||', rows '||count(*)||', valued '||count(*) filter (where has_value)||', valued any-period (metric rows only) '||count(*) filter (where has_value_any_period) from analytics.company_data_point_coverage"
q "select 'last snapshot '||coalesce(max(snapshot_date)::text,'none') from analytics.coverage_snapshot"
for f in doc/data-moat/team/top1000/shards.csv data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv; do
  [ -f "$f" ] || continue
  if [[ "$f" == *shards.csv ]]; then ids=$(python3 -I -c "import csv;print(','.join(x['company_id'] for x in csv.DictReader(open('$f')) if not x['excluded']))"); lbl="cohort v1 (986)"; else ids=$(python3 -I -c "import csv;print(','.join(x['company_id'] for x in csv.DictReader(open('$f'))))"); lbl="cohort v1.1 (1,000)"; fi
  echo -n "$lbl cells in table / valued / reasonless blanks: "; q "select count(*)||' / '||count(*) filter (where has_value)||' / '||count(*) filter (where not has_value and gap_reason is null) from analytics.company_data_point_coverage where company_id = any(array[$ids]::bigint[])"
done
echo; echo "## workflows (last 2 runs each)"
for w in pipeline-refresh.yml pipeline-sanity.yml pipeline-frames-check.yml workflow-health-check.yml; do echo "$w: $(gh run list --workflow $w --limit 2 --json status,conclusion,createdAt,databaseId --jq '.[]|"\(.createdAt) \(.status) \(.conclusion) \(.databaseId)"' 2>&1 | tr '\n' ';')"; done
echo; echo "## DB load"
q "select coalesce(nullif(application_name,''),'(none)')||' '||state||' '||coalesce(wait_event,'')||' x'||count(*) from pg_stat_activity where backend_type='client backend' and pid<>pg_backend_pid() group by application_name,state,wait_event order by count(*) desc"
q "select 'core.fact live '||n_live_tup||', dead '||n_dead_tup||', last_autovacuum '||coalesce(last_autovacuum::text,'-') from pg_stat_user_tables where schemaname='core' and relname='fact'"
q "select 'shared_buffers '||setting||coalesce(unit,'') from pg_settings where name='shared_buffers'"
