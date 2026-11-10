---
id: fsn-pilot-cause-quarter-not-printed-or-derivable-also-covers
title: FSN pilot cause quarter_not_printed_or_derivable also covers calendar keys whose filing is not in the FSN store (bucket ends 2026m09)
kind: gotcha
tags: fsn, cohort, gaps, done-gate
paths: pipeline/src/scrooner_pipeline/fsn_store/pilot.py
evidence: DATA-INFERRED
status: active
source: cohort run 41708119011 gaps.csv; FSN-STORE-DESIGN-2026-11-01.md l.6 and l.170
created: 2026-11-09
verified: 2026-11-09
---
pilot.py assigns quarter_not_printed_or_derivable to any Q key with no cell once the concept is mapped anywhere; expected keys come from the company calendar (expected_periods csv), not the store. In run 41708119011, 319 companies have the latest quarter (mostly 2026-09-30) missing on >=10 of the 13 write data points at once: the 10-Q is newer than the bucket's last set 2026m09. That alone blocks ~1,744 IS (company, data point) pairs of the per-pair done gate. Split this class (filing_not_in_store vs not derivable) before ranking fixes; do not blank it with a reason when the old table holds a value (the per-(company, concept) delete would turn it valued->blank).
