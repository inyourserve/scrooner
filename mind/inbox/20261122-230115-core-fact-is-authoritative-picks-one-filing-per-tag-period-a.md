---
id: core-fact-is-authoritative-picks-one-filing-per-tag-period-a
title: core.fact is_authoritative picks one filing per (tag, period); a one-filing derivation must see equal-valued copies in other filings
kind: gotcha
tags: derived_cells, is_authoritative, one-filing-rule, GILD, recert
paths: pipeline/src/scrooner_pipeline/mapper/derived_cells.py, scripts/ci/recert_token.py
evidence: CODE-CHECKED
source: flow run 45038935707; fix ff6d74fa2
created: 2026-11-22
verified: 2026-11-22
---
GILD total_liabilities FY2015 (certified 32,601M) fell BLANK: authoritative Assets/L&SE sat in the FY2016 10-K, authoritative equity/NCI/temp equity in the FY2015 10-K (same numbers printed in both), so with authoritative-only reads no filing printed every C2 operand. Rule now (derived_cells.operand_filings_from_rows): a non-authoritative fact counts for its filing only when it equals the authoritative value; no non-authoritative value enters a derivation. Same run: a recert token written the same day as the certificate it supersedes was read as consumed; tokens naming the superseded certificate are now judged against it (recert_token.py).
