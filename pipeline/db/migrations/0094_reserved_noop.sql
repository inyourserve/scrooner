-- Intentionally empty. Number 0094 was left unused when 0095 was committed
-- (2026-10-13, scrooner-2b), which broke scripts/check_migrations.py's
-- contiguity check and turned CI red on every commit. No pending migration
-- needed this number (scrooner-98 confirmed), so it is reserved as a no-op
-- rather than renumbering 0095, which is already applied.
select 1;
