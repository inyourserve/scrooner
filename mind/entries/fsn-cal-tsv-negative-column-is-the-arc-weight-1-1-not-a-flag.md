---
id: fsn-cal-tsv-negative-column-is-the-arc-weight-1-1-not-a-flag
title: FSN cal.tsv 'negative' column is the arc weight (+1/-1), not a flag; FSN extracts in fsn-notes carry tag/dim/ren/txt too
kind: gotcha
tags: fsn, cal, calc
evidence: DATA-INFERRED
status: active
source: 2015q1_cal.tsv.zst: GrossProfit<-Revenues negative=1, GrossProfit<-CostOfRevenue negative=-1; values -1:29,685 1:109,058; bucket list fsn-notes/2015q1/ has tag,dim,ren,txt,notes.zip
created: 2026-11-01
verified: 2026-11-01
---
Read negative as the calc weight. Local scratch copies often hold only sub/num/pre/cal; ren.tsv (menucat S = statement) and dim.tsv (dimh decode) are in the bucket per period.
