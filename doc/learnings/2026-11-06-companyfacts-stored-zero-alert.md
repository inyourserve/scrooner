# 2026-11-06: companyfacts `stored: 214 -> 0` was a legitimate zero; the alert re-fired for four nights

Asked by Dhairya (scrooner-df): pipeline freshness refresh run 41901536921 (2026-11-04) failed its
operations gate on `row_count_anomaly:companyfacts:<1,051 CIKs>|limit=None:stored:214->0`. Was it a
legitimate zero or a skipped or broken fetch? Investigation was read-only (GitHub logs and
`raw.collector_runs`); no production writes.

## Verdict: legitimate zero, plus an alert design flaw

1. **The zero is correct.** The two runs being compared are `raw.collector_runs` 308 (2026-10-31) and
   311 (2026-11-02). They have the same `params_key`, which is the same list of 1,051 CIKs.
   - Run 310 (`incremental`, 2026-11-02 21:49) indexed `date=2026-10-30` again. That is the same SEC
     day run 307 had indexed on 2026-10-31: `new 0, already_known 2318`.
   - So companyfacts re-collected the same 1,051 companies. Each payload was byte-identical to what
     was already stored, so run 311 reports `considered 1051, unchanged_skipped 1051, stored 0,
     errors 0, not_in_archive 18`.
   - Unchanged-payload dedupe began with run 308. Every earlier run has no `unchanged_skipped` and
     reports `stored == considered`.
   - Nothing was skipped by mistake and nothing failed; errors were 0.
2. **Why it failed four nights, not one.**
   - `operations.row_count_anomalies` compares the latest two successful runs with the same job and
     scope among the last 50 runs of all jobs.
   - No later companyfacts run shared that CIK list. So the same 308/311 pair was re-evaluated on
     every snapshot.
   - The pair failed the refresh on 2026-11-03 (run 41705247788), 11-04 (41901536921) and 11-05
     (42100457030), each time with this single alert and no other. On 11-02 (run 41531782259) it was
     created that same evening.
   - At about 3 collector runs a night, it would have kept failing until the pair left the 50-run
     window, around mid-November.
3. **The nightly data itself was healthy.** The companyfacts runs that followed were 314 (11-03:
   stored 156 of 922), 317 (11-04: 269 of 1,172) and 320 (11-05: 442 of 1,266), all with 0 errors.

## Fix (branch `claude/laughing-davinci-lcbuhb`, PR inyourserve/scrooner#1)

All changes are in `pipeline/src/scrooner_pipeline/operations.py`.

- A drop in `stored` is not an anomaly when the current run accounts for every considered item:
  `errors == 0` and `stored + unchanged_skipped == considered`. A drop with errors, or with items that
  are neither stored nor unchanged, still alerts.
- Only a pair whose newer run started in the last 24 hours is compared. This is the same window the
  failed-run alert already uses, so one old pair cannot re-alert every night.
- Tests are in `pipeline/tests/unit/test_operations.py`, and each one was checked by mutation.

## Not changed, worth knowing

- **A wrong "unchanged" would also be hidden.** The suppression trusts the collector's unchanged
  check, which compares the payload's sha256 with the latest stored one. If that check ever
  misclassified a changed payload as unchanged, this alert would no longer catch it. Today no
  evidence points that way.
- **Re-indexing the same day after a weekend is expected.** The Monday run indexes the latest
  finalized day, which is still the Friday. A guard that skips companyfacts when `incremental`
  reports `new = 0` would save about 5 minutes of collector time. It is optional and not done here.
