#!/usr/bin/env bash
# bash, not zsh -- same reason as reprocess_recent_filers.sh: this runs on
# GitHub's Ubuntu runners, which don't have zsh by default.
#
# Keeps core.listing.security_type classification (OpenFIGI, see
# company_master/security_type.py's own module docstring) from silently
# going stale. Added 2026-09-20, closing a real, confirmed gap: this
# classification job (`scrooner-company-master update-security-types`)
# had NEVER been wired into any scheduled cron -- it only ran once,
# manually, on 2026-09-06. A single-listing company never needs
# classification at all (resolve_primary_tickers() falls back to its one
# listing directly), but a company that only later GAINS a second listing
# (a SPAC merger completing, a new preferred-share/warrant registration)
# silently drops into "multiple listings, none classified" and stays
# there forever with no ticker resolvable for ANY downstream consumer
# (yfinance sector/industry, the Data Sanity Layer, yfinance-financials,
# market-price ingestion) until this job happens to run again by hand.
#
# Found live 2026-09-20 investigating a direct report that "lots of
# companies don't have a ticker" in the daily cron logs: real, substantial
# operating companies -- Webster Financial, Athene Holding, Equitable
# Holdings, CHS Inc, Triton International, Liberty Broadband, Aspen
# Insurance Holdings among them -- were sitting permanently unclassified
# for exactly this reason, not because the classification mechanism
# itself is broken (it resolves >98.8% of the active population fine).
#
# Cheap and safe to run daily: update_security_types() is resumable and
# skips already-classified listings by default (no --force here), so this
# only ever spends real OpenFIGI requests on whatever is newly
# unclassified since the last run -- typically a handful of companies,
# not the ~900 with multiple listings overall.
set -e
export PATH="/opt/homebrew/opt/libxslt/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "$(dirname "$0")/.."

CIKS=$(uv run python3 -c "
import psycopg
from scrooner_pipeline.common.config import settings
conn = psycopg.connect(settings.database_url)
cur = conn.cursor()
# Scoped to companies with NO resolvable primary ticker yet -- NOT every
# multi-listing company. First version of this script scoped broadly
# ('any company with >1 listing'), which pulled in 940 unclassified
# listing ROWS (2026-09-20 measurement) because most multi-listing
# companies already have their PRIMARY ticker classified and only their
# SECONDARY listings (preferred shares, warrants, notes) sit unclassified
# -- update_security_types() has no way to know those don't matter for
# resolve_primary_tickers()'s purposes, so it would spend real OpenFIGI
# budget (~40 minutes at the 2.5s/request pace) reclassifying securities
# nothing downstream needs. Scoping to companies where NO current listing
# is already a PRIMARY_SECURITY_TYPES match cuts this to the ~50-90
# companies actually blocked -- a few minutes, not tens of minutes.
PRIMARY_TYPES = ('Common Stock', 'ADR', 'REIT', 'MLP', 'Tracking Stk', 'Ltd Part')
cur.execute('''
    select c.cik
    from core.company c
    join core.listing l on l.company_id = c.id and l.effective_to is null
    where c.status = 'active'
    group by c.cik
    having count(*) > 1
       and count(*) filter (where l.security_type = any(%s)) = 0
''', (list(PRIMARY_TYPES),))
print(','.join(r[0] for r in cur.fetchall()))
")

if [ -z "$CIKS" ]; then
  echo "classify_multi_listing_companies: no multi-listing active companies -- nothing to do"
  exit 0
fi

N=$(echo "$CIKS" | tr ',' '\n' | wc -l | tr -d ' ')
echo "classify_multi_listing_companies: ${N} multi-listing active companies considered (already-classified listings are skipped automatically)"

uv run scrooner-company-master update-security-types --ciks "$CIKS"

echo "classify_multi_listing_companies: done"
