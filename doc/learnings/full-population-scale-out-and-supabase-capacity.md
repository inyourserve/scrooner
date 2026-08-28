# Full-population scale-out and Supabase capacity planning (2026-08-23)

## What happened

Scaled the pipeline from the 174-company pilot pool to the full 5,258-company
eligible universe in one overnight session. Two significant findings came out
of it, both corrected a wrong assumption formed the night before.

## Finding 1: the ~15-connection "ceiling" was never a hard platform limit

The previous session found `pg_stat_activity` topping out around 15
concurrent connections during a 4-shard collector run, and treated that as
the project's hard connection ceiling for the rest of the night — every
sharding decision was made around staying under ~15.

Checked live this session: raw Postgres `max_connections` is **60** (the
Micro compute tier's actual setting), and Micro tier's Supavisor pooler
supports up to **200** client connections. The ~15 figure was a *configured*
pool-size setting on the project's pooler, not a platform maximum — it can
simply be raised in the Supabase dashboard, independent of upgrading compute
tier at all.

Separately, the performance advisor flagged that Supabase's own Auth service
reserves up to 10 connections for itself by default (an absolute count, not
percentage-based) — a real, previously-unknown contributor to why the
project's usable headroom felt so tight.

**Lesson:** an empirically-observed ceiling from one incident is a data point
about that incident's configuration, not necessarily the platform's actual
capacity. Re-verify against the platform's own documented limits before
architecting around a number found via observation alone.

## Finding 2: per-company writes are safe to shard across a stage, cross-stage sharding is not

Verified live (`grep` across every remaining Company Master / Normalizer /
Mapper module) that every `delete from` / `update` in those stages is scoped
by `company_id = %s` — genuinely disjoint per company, no shared-table
writes. This made it safe to re-introduce parallelism, but in a different
shape than the previous night's abandoned 4-shard attempt:

- **Safe (what we did):** N shards running the *same* stage simultaneously
  against disjoint company subsets, never starting stage N+1 until every
  shard of stage N finishes.
- **Unsafe (what failed the night before):** shards each running the *entire
  pipeline* independently, so different shards were on different stages at
  the same time against overlapping companies — this is what caused the
  earlier deadlocks/races, not parallelism itself.

Result: ~8x throughput improvement (3.8 companies/min sequential → ~32.7
companies/min with 3 shards) on the Normalizer identity stage, with zero
correctness issues, at a stable 12/15 connections (well under the — now
known to be soft — ceiling).

## Real Supabase specs (verified 2026-08-23, for future capacity decisions)

- Plan: Pro, compute add-on: Micro (1GB RAM, 60 max connections, 200 pooler
  connections, ~$10/mo)
- DB size: 1.49GB (pre-full-population; will grow once Normalizer
  facts/Mapper metrics run for the ~5,000 newly-added companies)
- For a future 1,000-concurrent-user target: Medium tier (4GB RAM, 600 pooler
  connections, ~$60/mo) is the reasoned recommendation, not Large — this
  product is read-heavy and CDN-cacheable on its public pages, and
  transaction-mode pooling means concurrent users don't map 1:1 to concurrent
  connections. Not load-tested; treat as a starting point, not a guarantee.

## Finding 3: the local bulk-zip cache had no rotation, and it took the whole run down

`SECClient.get_cached_bulk_zip` (`common/sec_client.py`) caches SEC's daily
`submissions.zip`/`companyfacts.zip` locally, date-keyed
(`{name}-{date}.zip`), specifically so a multi-batch run doesn't re-download
~1.5GB per batch. Correct call — moving this to Supabase Storage would trade
an instant local read for a network round-trip on every one of 27+ batch
reads, and would burn paid storage quota on a file with zero long-term value
(SEC lets you re-fetch it free, any time).

The gap: nothing ever deleted a *previous* day's copy. Across this session
(which spanned parts of three calendar days), that meant up to 3 full
generations of both zips sitting on disk simultaneously — by the time the
full-population run reached 6-way parallel shards, the disk was down to
206MB free on a 228GB volume, and all 6 shards crashed identically with
`OSError: [Errno 28] No space left on device`. Freeing ~5.9GB of stale zips
fixed it immediately, and shard throughput measured cleanly right after
(~106 companies/min at 6 shards, vs. 32.7/min at 3 shards, vs. 3.8/min
sequential).

Fixed in `get_cached_bulk_zip`: after a fresh download completes, prune
every other `{cache_name}-*.zip` in the same directory. Safe unconditionally
— these are pure bandwidth cache, never a source of truth.

**Lesson:** a cache with no eviction policy is a slow leak, not a
performance win — and a leak that only manifests after several real-world
days of a cache directory quietly growing is exactly the kind of bug that's
invisible in short-lived test/dev usage and only surfaces once something
runs long enough (an overnight full-population job, in this case) to
actually hit it.

## Generalizable lesson

Before scaling any part of this pipeline again: re-check the *actual*
documented platform limits (compute tier specs, pooler config) rather than
reusing a ceiling discovered under one specific failure condition — and when
parallelizing, shard by an entity whose writes are provably disjoint
(verified via the actual `WHERE`/`delete from` clauses, not assumed from the
schema), one stage at a time.
