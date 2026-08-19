#!/usr/bin/env bash
set -euo pipefail

# This script creates and destroys one uniquely named restore database. It is
# intentionally fail-closed so it cannot be pointed at a production database
# by accident. The source must be an explicitly non-production database and
# the caller must acknowledge the ephemeral restore operation.
if [[ "${SCROONER_ALLOW_EPHEMERAL_RESTORE:-}" != "1" ]]; then
  echo "backup restore: refused; set SCROONER_ALLOW_EPHEMERAL_RESTORE=1 for an isolated non-production database" >&2
  exit 2
fi

source_database="${PGDATABASE:-}"
case "$source_database" in
  *test*|*dev*|*local*|*staging*) ;;
  *)
    echo "backup restore: refused; PGDATABASE must identify a test/dev/local/staging database" >&2
    exit 2
    ;;
esac

for command_name in pg_dump pg_restore createdb dropdb psql; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "backup restore: missing required command: $command_name" >&2
    exit 2
  fi
done

restore_database="scrooner_restore_verify_$$"
archive_path="$(mktemp /tmp/scrooner-backup-restore.XXXXXX)"
restore_created=0
canary_created=0

cleanup() {
  if [[ "$canary_created" == "1" ]]; then
    psql --dbname "$source_database" --set ON_ERROR_STOP=1 \
      --command "drop table if exists public.scrooner_restore_canary" >/dev/null || true
  fi
  if [[ "$restore_created" == "1" ]]; then
    dropdb --if-exists "$restore_database" >/dev/null || true
  fi
  rm -f -- "$archive_path"
}
trap cleanup EXIT

psql --dbname "$source_database" --set ON_ERROR_STOP=1 <<'SQL' >/dev/null
create table public.scrooner_restore_canary (
    canary_key text primary key,
    canary_value text not null
);
insert into public.scrooner_restore_canary (canary_key, canary_value)
values ('day10', 'backup-restore-round-trip');
SQL
canary_created=1

source_table_count="$(psql --dbname "$source_database" --tuples-only --no-align --set ON_ERROR_STOP=1 --command \
  "select count(*) from information_schema.tables where table_schema in ('raw','core','analytics','app','auth','public')")"

pg_dump --dbname "$source_database" --format custom --no-owner --no-acl --file "$archive_path"
createdb "$restore_database"
restore_created=1
pg_restore --dbname "$restore_database" --no-owner --no-acl --exit-on-error "$archive_path"

restored_table_count="$(psql --dbname "$restore_database" --tuples-only --no-align --set ON_ERROR_STOP=1 --command \
  "select count(*) from information_schema.tables where table_schema in ('raw','core','analytics','app','auth','public')")"
restored_canary="$(psql --dbname "$restore_database" --tuples-only --no-align --set ON_ERROR_STOP=1 --command \
  "select canary_value from public.scrooner_restore_canary where canary_key = 'day10'")"

if [[ "$source_table_count" != "$restored_table_count" ]]; then
  echo "backup restore: FAIL table count source=$source_table_count restored=$restored_table_count" >&2
  exit 1
fi
if [[ "$restored_canary" != "backup-restore-round-trip" ]]; then
  echo "backup restore: FAIL canary mismatch" >&2
  exit 1
fi

echo "backup restore: PASS"
echo "source_table_count=$source_table_count"
echo "restored_table_count=$restored_table_count"
echo "canary=backup-restore-round-trip"
