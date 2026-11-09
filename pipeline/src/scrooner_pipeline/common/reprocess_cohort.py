"""The nightly reprocess cohort (pipeline/scripts/reprocess_recent_filers.sh), as a testable function.

Two branches, as before:

* **recent filers**: active companies with a 10-K / 10-K/A / 10-Q / 10-Q/A in raw.sec_filing_documents in the last
  `lookback_days`, now **capped at `filer_limit`, newest filing first**;
* **backlog** (unchanged, 2026-09-27): a company whose latest 10-K/10-Q of the last 150 days has no core.fact rows
  although a companyfacts payload fetched after it is in raw, newest first, capped at `backlog_limit`.

Why the cap (2026-11-09). The work is ~10 s per company across the 23 stages at 4 shards (31 Oct: 669 companies,
~7,000 s, the whole budget). In 10-Q season the 4-day window holds 1,366-1,635 companies (6-8 Nov), partly because a
filer is reselected on each of the 4 nights. `normalize:facts` then hit its 1,800 s stage cap (killed, ~7 s per
company per shard) and the job crossed its 7,000 s budget before the map stages, so growth, TTM, expanded metrics,
Piotroski, quality flags, reconciliations, FCF growth, dividend streak and the tag library were skipped for every
company, every night from 2026-11-02. Newest first means the repeats of filings already processed on an earlier
night are the ones deferred; a deferred filing whose facts never landed is still caught by the backlog branch.
"""

from __future__ import annotations

from typing import Any

import psycopg

FILER_LIMIT = (
    450  # + BACKLOG_LIMIT 150 = at most 600 companies, ~6,250 s at the measured rate
)
BACKLOG_LIMIT = 150

RECENT_SQL = """
    select d.cik, max(d.filing_date) as last_filed
    from raw.sec_filing_documents d
    join core.company c on c.cik = d.cik
    where d.filing_date >= current_date - make_interval(days => %s)
      and c.status = 'active'
      and d.form in ('10-K', '10-K/A', '10-Q', '10-Q/A')
    group by d.cik
    order by last_filed desc, d.cik
"""

BACKLOG_SQL = """
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
"""


def reprocess_cohort(
    conn: psycopg.Connection,
    lookback_days: int,
    filer_limit: int = FILER_LIMIT,
    backlog_limit: int = BACKLOG_LIMIT,
) -> tuple[list[str], dict[str, Any]]:
    """(sorted CIKs, counts). filer_limit <= 0 means no cap (the old behaviour)."""
    recent = [r[0] for r in conn.execute(RECENT_SQL, (lookback_days,)).fetchall()]
    chosen = recent[:filer_limit] if filer_limit > 0 else recent
    backlog = [r[0] for r in conn.execute(BACKLOG_SQL, (backlog_limit,)).fetchall()]
    ciks = sorted(set(chosen) | set(backlog))
    return ciks, {
        "recent_filers": len(recent),
        "recent_selected": len(chosen),
        "recent_deferred": len(recent) - len(chosen),
        "backlog": len(backlog),
        "total": len(ciks),
    }
