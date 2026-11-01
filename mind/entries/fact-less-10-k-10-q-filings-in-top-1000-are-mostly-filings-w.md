---
id: fact-less-10-k-10-q-filings-in-top-1000-are-mostly-filings-w
title: Fact-less 10-K/10-Q filings in top-1000 are mostly filings with no XBRL at all (isXBRL=0), not extraction gaps
kind: lesson
evidence: DATA-INFERRED
status: active
created: 2026-10-31
verified: 2026-10-31
---
B9 cohort dry run 2026-10-31: 549 fact-less filings, 426 absent from FSN; EDGAR submissions JSON isXBRL=0 for 419 of them (ARCC 36, BDCs/pre-mandate filers); only 7 XBRL filings missing from FSN. Before calling a filing's blanks an extraction gap, check submissions JSON isXBRL for the accession; no instance means no fallback source and the blank reason is filing_has_no_xbrl. Only 123 fact-less filings are fillable from FSN (70 FY2013 10-Ks, 42 filed 2026). System python 3.14 fails SSL to sec.gov; use the pipeline venv python (httpx). See data-team/44-b9-instance-fallback/COHORT-SIZING-2026-10-31.md
