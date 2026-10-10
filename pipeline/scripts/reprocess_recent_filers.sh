#!/usr/bin/env bash
# bash, not zsh (fixed 2026-09-14) -- unlike pipeline/scripts/backfill_*.sh
# (manual-only, dev-machine-only), THIS script is wired into
# .github/workflows/pipeline-refresh.yml and runs on GitHub's Ubuntu
# runners, which don't have zsh installed by default. `#!/bin/zsh`
# silently broke every single scheduled run since this file landed on
# main -- "cannot execute: required file not found" (exec() failing to
# find the shebang interpreter) -- caught live 2026-09-14 via the exact
# freshness alert this script exists to prevent (`normalizer_backlog`
# going stale, because the thing meant to keep it fresh never actually
# ran). No zsh-specific syntax is used below, so bash runs it unchanged.
# Incremental Normalizer + Mapper reprocessing for recently-filed companies
# (added 2026-09-09). Closes a real, confirmed gap: `scrooner-incremental`
# only ever wrote NEW filing metadata + companyfacts/submissions into `raw`
# -- nothing downstream ever reran the Normalizer's derive-interim-quarters/
# derive-q4 or the Mapper's resolve/calculate chain for those companies, so
# a company's `core`/`analytics` data could silently go stale forever after
# its first full-population pass. Found live investigating a real user
# report (Etsy showing blank quarterly revenue) -- the last full-population
# derive/resolve/calculate run was 2026-08-25; every quarter filed since
# then for any company was invisible past `raw` until this script existed.
#
# Scope: companies with a core.filing row filed in the last N days
# (default 10, matching jobs/incremental.py's own _most_recent_published_
# day lookback convention) -- cheap (usually a few hundred CIKs/day, not
# the full ~5,200-company population) and safe to run daily. Every stage
# below is idempotent (delete-then-reinsert per company, per this
# project's own documented discipline) so a company with nothing new is
# harmless work, not a correctness risk.
#
# Order matters and mirrors jobs/normalize.py's `golden` command plus the
# Mapper stages each module's own docstring says must follow resolve-facts:
# identity -> periods -> units -> facts -> dedupe -> restatements -> conflict-latest-filed ->
# derive-interim-quarters -> derive-q4 -> resolve-facts ->
# resolve-concept-fallbacks -> calculate -> growth -> ttm-returns ->
# calculate-expanded-metrics -> calculate-piotroski -> calculate-quality-flags
# -> calculate-reconciliation -> calculate-tax-reconciliation ->
# calculate-fcf-growth -> calculate-dividend-streak.
# resolve-statement-fallbacks is deliberately excluded -- it's always
# population-wide, set-based SQL (see its own CLI docstring), too heavy to
# run daily for a handful of companies; that one stays on its existing
# manual/periodic cadence.
set -e
export PATH="/opt/homebrew/opt/libxslt/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "$(dirname "$0")/.."

LOOKBACK_DAYS="${1:-10}"

# Status refresh (added 2026-10-02, by direct request -- "manage this list
# daily... because some company status may be changed"). core.company.status
# was computed once and never kept current -- `company_master/status.py`'s
# `update-status` existed but was wired into nothing recurring. This matters
# for more than freshness in the abstract: the $CIKS query just below this
# block ALREADY filters `c.status = 'active'`, so a stale status silently
# changes which companies this whole script (and every population-wide job
# that scopes to status='active', including mapper/ttm.py's TTM returns and
# mapper/revenue_resolvers/) ever sees -- the same root shape as the real,
# already-documented 2026-09-02 incident where 222 active companies sat
# mislabeled `delisted` for days.
#
# Deliberately NARROW, not "any filing in the lookback window" -- an
# unrestricted identity pass over every recent filer is the EXACT shape that
# already blew this script's own 90-minute job timeout once (2026-09-19,
# 2,494 unfiltered CIKs). The real delisting signal, a Form 15/15F-family
# filing, is rare (2 CIKs in a live 10-day check, not thousands) and never a
# 10-K/10-Q, so it would never appear in $CIKS's own form-filtered list below
# -- a company whose last-ever filing is a Form 15 would otherwise never get
# re-checked by anything recurring. `status.py`'s own DEREGISTRATION_FORMS
# constant is reused directly here, not re-derived, so this can never drift
# out of sync with what update-status itself actually checks for.
DELISTING_CIKS=$(LOOKBACK_DAYS="$LOOKBACK_DAYS" uv run python3 - <<'PY'
import os
import psycopg
from scrooner_pipeline.common.config import settings
from scrooner_pipeline.company_master.status import DEREGISTRATION_FORMS
conn = psycopg.connect(settings.database_url)
cur = conn.cursor()
cur.execute(
    """
    select distinct d.cik
    from raw.sec_filing_documents d
    where d.filing_date >= current_date - make_interval(days => %s)
      and d.form = any(%s)
    """,
    (int(os.environ["LOOKBACK_DAYS"]), list(DEREGISTRATION_FORMS)),
)
print(','.join(r[0] for r in cur.fetchall()))
PY
)

if [ -n "$DELISTING_CIKS" ]; then
  N_DELISTING=$(echo "$DELISTING_CIKS" | tr ',' '\n' | wc -l | tr -d ' ')
  echo "reprocess_recent_filers: ${N_DELISTING} companies with a Form 15-family filing in the last ${LOOKBACK_DAYS} days -- ensuring it's normalized before the status check"
  uv run scrooner-normalize identity --ciks "$DELISTING_CIKS"
fi

# Sourced from raw.sec_filing_documents, NOT core.filing -- core.filing only
# exists once the Normalizer's identity stage has already run for a CIK, so
# scoping off of it would silently exclude exactly the companies this
# script exists to catch up (confirmed live 2026-09-09: core.filing's own
# max filing_date lagged raw's by ~1 week, and 2,660 active CIKs had a raw
# filing in the last 10 days with zero core.filing awareness of it yet).
#
# form IN (10-K/10-K/A/10-Q/10-Q/A) -- added 2026-09-19, closing a real,
# confirmed scoping bug: an unfiltered version pulled EVERY CIK with ANY
# raw filing in the window (2,494 on 2026-09-18), but every stage this
# script runs (Normalizer identity/periods/facts/derive-quarters, Mapper
# resolve/calculate) only ever consumes companyfacts/XBRL data, which only
# 10-K/10-Q filings carry -- Form 4/144/3/8-K (97% of that 2,494) file no
# new XBRL fact at all and gained nothing from being reprocessed. Checked
# live before narrowing: the same 10-day window has only 146 real 10-K/
# 10-K/A/10-Q/10-Q/A filers, matching this script's own docstring
# assumption ("usually a few hundred CIKs/day") that the unfiltered
# version had silently broken.
# Consequence of the unfiltered scope: "normalize identity" alone took 63
# minutes for 2,494 CIKs, blowing the whole 90-minute job timeout before
# ever reaching a Mapper stage -- meaning new quarterly filings had NOT
# been reprocessed into core/analytics for 5+ consecutive days (2026-09-15
# through 09-19, all "cancelled" on the job timeout annotation), which is
# why the company page was showing recent quarters as blank cells.
#
# The Python below is fed through a quoted heredoc ('PY'), never an inline
# `python3 -c "..."` string: a double quote inside a comment in that string
# ('("usually a few hundred CIKs/day")') silently ended the bash string early,
# so python only ever received the code up to that comment -- it connected,
# never ran the query, exited 0, and this script reported "no companies" on
# every scheduled run from 2026-09-19 until 2026-09-27.
CIKS=$(LOOKBACK_DAYS="$LOOKBACK_DAYS" uv run python3 - <<'PY'
import os
import psycopg
from scrooner_pipeline.common.config import settings
conn = psycopg.connect(settings.database_url)
cur = conn.cursor()
cur.execute(
    """
    select distinct d.cik
    from raw.sec_filing_documents d
    join core.company c on c.cik = d.cik
    where d.filing_date >= current_date - make_interval(days => %s)
      and c.status = 'active'
      and d.form in ('10-K', '10-K/A', '10-Q', '10-Q/A')
    union
    -- Backlog (added 2026-09-27): a company whose latest 10-K/10-Q has
    -- no core.fact rows yet, although a companyfacts payload fetched
    -- after it is already in raw. The lookback above only sees the last
    -- N days, so any cron outage longer than that lost filings for good:
    -- 348 companies (Abbott, NextEra, S&P Global, Cintas' FY2026 10-K)
    -- sat at Q1 2026 after the 09-15..09-26 outages. Capped per run so
    -- a large backlog drains over a few days instead of blowing the
    -- job timeout.
    select cik from (
      select lf.cik
      from (
        select distinct on (f.company_id) f.company_id, c.cik, f.id as filing_id, f.filing_date
        from core.filing f
        join core.company c on c.id = f.company_id
        where c.status = 'active'
          and f.form in ('10-K', '10-K/A', '10-Q', '10-Q/A')
          and f.filing_date >= current_date - 150
        order by f.company_id, f.filing_date desc
      ) lf
      where not exists (select 1 from core.fact x where x.filing_id = lf.filing_id)
        and (select max(r.fetched_at)::date from raw.sec_companyfacts r where r.cik = lf.cik) > lf.filing_date
      order by lf.filing_date desc
      limit %s
    ) backlog
    """,
    (int(os.environ["LOOKBACK_DAYS"]), int(os.environ.get("BACKLOG_LIMIT", "150"))),
)
print(','.join(r[0] for r in cur.fetchall()))
PY
)

# Actual status refresh -- merges the 10-K/10-Q filers already selected
# above (covers "resumed real filing activity," e.g. a stale/unknown company
# going active again) with $DELISTING_CIKS (covers the Form 15 signal
# $CIKS's own form filter can never see). Runs before the early-exit below
# so a day with zero 10-K/10-Q filings but a real Form 15 filing still gets
# its status checked.
STATUS_CIKS=$(printf '%s,%s' "$CIKS" "$DELISTING_CIKS" | tr ',' '\n' | awk 'NF' | sort -u | paste -sd, -)
if [ -n "$STATUS_CIKS" ]; then
  N_STATUS=$(echo "$STATUS_CIKS" | tr ',' '\n' | wc -l | tr -d ' ')
  echo "reprocess_recent_filers: refreshing status for ${N_STATUS} companies"
  uv run scrooner-company-master update-status --ciks "$STATUS_CIKS"
fi

if [ -z "$CIKS" ]; then
  echo "reprocess_recent_filers: no companies filed in the last ${LOOKBACK_DAYS} days -- nothing to do"
  exit 0
fi

N=$(echo "$CIKS" | tr ',' '\n' | wc -l | tr -d ' ')
echo "reprocess_recent_filers: ${N} companies (filed in the last ${LOOKBACK_DAYS} days, or latest 10-K/10-Q not yet normalized)"

# conflict-latest-filed must follow dedupe: dedupe resets the disagreeing-filings
# groups it promotes, so skipping it silently reverts them (and re-blocks Q4).
for stage in identity periods units facts dedupe restatements conflict-latest-filed derive-interim-quarters derive-q4; do
  echo "--- normalize $stage ---"
  uv run scrooner-normalize "$stage" --ciks "$CIKS"
done

for stage in resolve-facts resolve-concept-fallbacks calculate growth ttm-returns ttm-margins calculate-expanded-metrics calculate-piotroski calculate-quality-flags calculate-reconciliation calculate-tax-reconciliation calculate-fcf-growth calculate-dividend-streak; do
  echo "--- map $stage ---"
  uv run scrooner-map "$stage" --ciks "$CIKS"
done

# Keep the SEC Tag Library current (founder direction 2026-09-29: it is the
# source of truth for data gaps and must never be stale). Refreshes the
# company x tag rows and concept lineage for just these companies, then the
# population-wide tag summary, verdict sync and gap leads.
echo "--- map build-tag-library ---"
uv run scrooner-map build-tag-library --ciks "$CIKS"

echo "reprocess_recent_filers: done"
