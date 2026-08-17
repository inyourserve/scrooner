# Day 3 — Company Facts + Submissions Collectors

## Problem 1: a remote agent's "completed" status was not evidence of completion

A remote/cloud agent was launched to build Day 3 and told to stop and report when done. It stopped twice with `status: completed` and vague, non-terminal language each time ("I've set a background watcher... will resume when it completes"; "Waiting for the background job notification before proceeding further.").

### How it was found

Not by re-reading its report more carefully — by querying the live database directly both times. First check: `raw.sec_companyfacts` had 10 rows (the golden sample) but `raw.sec_submissions` had 0. Second check, after resuming with corrections: real progress (89 submissions rows) but `raw.collector_runs` showed the run still `status='running'`, never marked finished. The agent's own words were not a reliable signal either time; the database was.

### Fix / decision

Resumed the *same* agent (not a fresh one — it keeps context) with the specific gap stated as direct evidence, not a vague "are you done?". Eventually verified success independently: all 10 golden companies covered in both tables, SHA-256 of two freshly-downloaded objects matched their recorded hashes exactly, and the actual Supabase Storage bucket was listed directly (not inferred from DB rows) — e.g. JPM's submissions folder genuinely contains 70 real files totaling ~28.7MB.

### Why it matters going forward

Codified into the `run-collector-day` skill: an agent's self-reported completion is a claim, not evidence, especially for long-running work (multi-GB downloads) where its own turn can end before the work does. Always verify against live state — database rows, storage listings, real checksums — before accepting "done."

## Problem 2: doc 08 promised a schema field that no longer existed

Doc 08 said `exchange` "gets populated during Day 3's bulk `submissions.zip` pass" — but Day 2's fix had already removed the `exchange` column from `raw.company_universe` entirely. The doc was pointing at a column that didn't exist.

### How it was found

The remote agent building Day 3 noticed the inconsistency itself while implementing the submissions collector, and flagged it explicitly instead of either inventing a new column unilaterally or silently ignoring the doc's claim.

### Fix

Corrected doc 08's wording: `exchanges` is stored as part of the verbatim submissions JSON payload (inside `raw.sec_submissions`), not a dedicated column. Extracting it into a structured field is Company Master's job later (doc 06, Part 4) — adding a column at the Collector layer now would mean the Collector deciding how to reconcile a company with multiple exchange values over time, which is interpretation.

### Why it matters going forward

A doc can go stale the moment an earlier fix changes what it was describing, even without anyone touching that doc's text. Cross-check a doc's specific claims against current reality when implementing against it, not just its general intent.

## Problem 3 (design decision, not a bug): SEC paginates large filers' submission history

JPM's submissions data isn't one file — SEC splits it into a base file plus numbered continuation files once history gets long enough. Verified live: JPM has 69 continuation files (`CIK0000019617-submissions-001.json` through `-069.json`) beyond the base. Reddit, by contrast (recent IPO), has none.

### Decision

Store each SEC-published file as its own row/object rather than merging them into one payload. Merging would be interpretation (deciding how multiple files compose into "the" submissions record), which is out of scope for the Collector.

### Why it matters going forward

"One company, one file" was never a safe assumption for any of the bulk SEC data. Storage paths and row cardinality were designed to allow N files per company per fetch from the start, rather than retrofitted after hitting a filer with a long history.

## Problem 4: an interrupted run left `raw.collector_runs` stuck at `status='running'`

One run's row never reached `finished_at`/`status='succeeded'`, despite the underlying data (companyfacts/submissions rows) being verified complete and correct.

### Fix

None yet — deliberately. Flagged rather than patched, because detecting and resolving an abandoned run is explicitly Day 4's scope (retry/failure handling, checkpoint/resume), and this stuck row is now a real, concrete example for Day 4 to actually fix, not a hypothetical to design against.

### Why it matters going forward

Day 4's acceptance test should be checked against this specific row, not just a synthetic "kill it and see" test — a fix that doesn't clean up this exact row isn't actually done.

## Minor: a throwaway inspection script nearly hung the session

An ad hoc script to inspect the structure of the ~986k-entry bulk zip used O(n²) list-membership checks and consumed ~99.8% CPU for 8+ minutes before being killed and rewritten with O(1) set/dict lookups.

### Why it matters going forward

At SEC's actual data volume (hundreds of thousands to millions of entries in bulk files), even a "just a quick check" script needs basic attention to algorithmic complexity — this scale isn't forgiving of accidental O(n²).
