# Expanding the pilot from golden-10 to a real 174-candidate pool — what actually happened

The Supabase plan was upgraded to Pro (2026-08-21), clearing the capacity blocker `doc/consultant/15_Blocker_Remediation_Execution_Evidence.md` had named as the last externally-blocked item for the 100-company pilot. This is the real, live-executed record of what ran, what broke, and what the evidence actually says — not a re-assertion of the plan.

## Scope, stated plainly

This ran `--ciks` explicitly against one specific, pre-existing 174-CIK candidate pool (companies that already had `raw.sec_companyfacts` collected from earlier work) — never the full 10,396-row `raw.company_universe` seed table, and never a step toward the full universe. Worth stating directly because the natural next question ("does this run for all 10k tickers?") came up mid-pilot, and the answer is no — this was, and remains, a 174→100 pilot only.

## What ran, in order, with real timing

1. **`scrooner-bootstrap submissions --ciks <174>`** — failed on the first attempt. The 1.559 GB SEC bulk `submissions.zip` downloaded completely (confirmed by exact byte count match), but the database connection dropped mid-store with `OperationalError: ... Can't assign requested address` — the same class of intermittent Supabase-pooler connection issue already documented in `pipeline/CLAUDE.md` from Normalizer Day 7, now confirmed recurring under a different specific error message. 110 of 174 CIKs had already been stored before the crash (partial progress preserved, not lost). Re-running the identical command succeeded cleanly and fast, because the 1.5 GB zip was now cached locally (`.cache/bulk-zips/`) — the retry only had to redo the DB-store phase, not the download. **Lesson: a long-running bulk-download-then-store job should be re-run as-is on a transient connection failure before assuming anything is wrong with the data or the approach — the cache made the retry cheap.**

2. **`scrooner-normalize identity --ciks <174>`** and **`scrooner-company-master update-history --ciks <174>`** both exceeded the default 2-minute foreground timeout partway through (each landed in the 15-27 companies/minute range) and had to be resumed as backgrounded jobs. Both completed cleanly for all 174 on the backgrounded rerun — same command, no special resume flag needed, confirming these stages are naturally idempotent/re-runnable the same way every other pipeline stage in this project already is.

3. **`update-identity`** and **`update-status`** both completed inside 2 minutes — pure re-parsing of already-stored `raw.sec_submissions`, no new fetches, fast by design.

4. **`update-security-types`** (OpenFIGI classification) took the longest of any single stage — expected, since it's the one step that's genuinely rate-limited against an external API (~1.5s/request, 255 real listings). 175 of 255 classified, 80 no-match (expected: OTC/pink-sheet variants and other non-primary listing types that OpenFIGI doesn't carry).

5. **`build-universe`** found **138 eligible primary companies** out of 255 candidate listings on the first real run — comfortably past the 100-company pilot target, using the same reason-coded eligibility policy already proven at golden-10 scale (`policy_version=2026-08-18.v1`).

## The `preflight` gate has a real, permanent wiring gap — found live, not assumed

`scrooner-pilot preflight` kept reporting `"representative_mapping_coverage_not_measured"` as a blocker even after running `scrooner-pilot mapping-preflight` and getting a real, complete coverage report. Traced this to `pilot.py`'s `read_inventory()`, which hardcodes `mapping_coverage=None` unconditionally — there is no code path, table, or file that ever writes a real number into the field `evaluate_readiness()` checks. **This blocker cannot be auto-cleared by any sequence of CLI commands as currently wired.**

This looks deliberate, not broken: `mapped_tag_presence()`'s own docstring says "the report deliberately avoids a single pass/fail percentage that could overstate what this check proves." The tool is built to hand a human evidence, not to self-certify. Worth recording plainly so a future session doesn't spend time hunting for a command that "should" clear this gate — there isn't one, by design.

## The cohort you measure against matters — checked both, they disagree usefully

`mapping-preflight`'s default cohort is `cik_ordered_inventory` — literally "the first N CIKs in storage order," not the actual pilot manifest. Running it that way first, then re-running with `--eligible-sample` (the real deterministic cohort `sample --target 100` would actually select), gave meaningfully different — and more informative — results:

| Concept | Default (arbitrary) cohort | Real eligible cohort |
|---|---:|---:|
| Cash, CFO, net income, stockholders' equity | 93% | **100%** |
| Revenue | 91% | **99%** |
| Diluted EPS | 89% | **98%** |
| Gross profit | 60% | 55% |

The real cohort is *better* on every core metric — sensible in hindsight, since the eligibility filter itself already screens out the messiest candidates (non-primary listings, thin identity data) before a company ever reaches the sample. But it's *worse* on gross profit and current-asset/liability concepts specifically, which matches an already-known structural pattern (banks/BDCs like JPM/ARCC in the golden-10 don't report a classified balance sheet or a gross-profit line at all) rather than revealing anything new. **Lesson: always measure the tool's own default/convenience cohort against the real target cohort before trusting a coverage number — they can diverge in both directions, and the direction itself is diagnostic** (here, "the eligible cohort is cleaner" confirms the eligibility policy is doing real filtering work, not just checking a box).

## Where things stand

Every automatable blocker is cleared: capacity (~1.1 GB projected against an 8 GB limit), eligible primaries (138, above the 100 target), submissions/companyfacts payloads (174, above target), zero unresolved Normalizer/Mapper errors. The one remaining item — representative mapping coverage — is a human judgment call by the tool's own design, and the evidence for that call (above) supports proceeding: core decision-relevant metrics are at 96-100% in the real cohort, and the two weak spots are the same already-understood, structurally-honest gaps as the golden-10, not new surprises.

Not yet done: the actual `sample --target 100` manifest generation and the full Normalizer→Mapper run against that manifest (currently only 16 of 174 companies have gone through fact extraction/mapping at all — the rest have identity/listing/status only). That's the next real step, not implied complete by anything above.
