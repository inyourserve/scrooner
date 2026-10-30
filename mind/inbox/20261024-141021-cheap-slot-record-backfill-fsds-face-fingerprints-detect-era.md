---
id: cheap-slot-record-backfill-fsds-face-fingerprints-detect-era
title: Cheap slot-record backfill: FSDS face fingerprints detect eras, fetch cal only at boundaries (~0.3 req/filing vs 2)
kind: howto
tags: slot-records, fsds, era-detection, scaling, total_debt
paths: pipeline/scripts/slot_records/{fsds_debt_pre, era_detect, assemble30, replay30}.py (branch work/scrooner-25/slot-records)
evidence: DATA-INFERRED
created: 2026-10-24
verified: 2026-10-24
---
Proven 2026-10-24 on 33 companies / 1,478 filings: stream the 47 FSDS quarterly zips once (whole-market, ~4.4GB, one at a time + delete), extract face BS presentation rows for the cohort, fingerprint each filing by its ordered debt-family face tags, collapse to eras, then fetch the filer's _cal.xml ONLY for each era's first filing (182 boundaries), re-collapsing adjacent eras whose CAL fingerprints match. Result: 169 era records, ~420 SEC requests total instead of ~3,000. Gotchas baked in: FSDS dates are month-rounded (match on year-month); sub.txt dates are YYYYMMDD; modern filings may need MetaLinks.json (no _cal.xml anywhere); the machinery is family-generic except the tag regexes. Replay vs lane 3 resolved 149 value-to-blank holds and decomposed 194 disagreements into precision (<0.5%), composition (0.5-5%), prod-shows-fragment (>5%, the target class) and one tag-pair question (CVX LongTermDebt vs LongTermDebtNoncurrent, both authoritative, 7.3B apart - filing read required).
