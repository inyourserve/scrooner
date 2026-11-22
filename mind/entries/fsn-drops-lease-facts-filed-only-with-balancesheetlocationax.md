---
id: fsn-drops-lease-facts-filed-only-with-balancesheetlocationax
title: FSN drops lease facts filed only with BalanceSheetLocationAxis; pre-842 capital leases need the sec.gov instance
kind: gotcha
tags: total_debt, leases, fsn
paths: data-team/tags/line_map/total_debt-pre842-2026-11-14.csv, pipeline/src/scrooner_pipeline/proof/perimeter.py
evidence: FILING-CHECKED
status: active
created: 2026-11-14
verified: 2026-11-14
---
MSFT FY2016 total_debt missed 786M: CapitalLeaseObligationsCurrent 25 [OtherCurrentLiabilitiesMember] + Noncurrent 761 [OtherNoncurrentLiabilitiesMember] exist only dimensioned (0001564590-17-014900, note R102); fsn.value has no row, so structural total_debt and proof v9 perimeter missed it. Correct 54,247M. Scan of 494 top-110 2015-2019 10-Ks: only MSFT locates capital leases by member (CSV _lease-locations-pre842-2026-11-14.csv). Rule (perimeter.py item 3): non-debt location member -> add; debt member -> inside; no member -> add only via calc arc to a non-debt line, else reader.
