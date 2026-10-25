---
id: the-achievable-definition-of-100-coverage-100-correct-for-to
title: The achievable definition of '100% coverage / 100% correct' for top-1000
kind: decision
tags: strategy, coverage, top-1000, correctness
evidence: ASSUMED
created: 2026-10-24
verified: 2026-10-24
---
Context: founder asked how 100%/100% is possible when Yahoo etc. seem to have it. Key facts: Yahoo licenses fundamentals from vendors (S&P Capital IQ/FactSet/Refinitiv class), who achieve correctness via thousands of human analysts manually keying+double-reviewing filings plus decades of exception rules - not parsing. Even so they are not at 100%: vendors disagree with each other on standardized numbers (EBITDA, total debt), Yahoo shows wrong market caps/stale shares routinely, and vendor contracts promise an error-correction process, not accuracy. Therefore the Scrooner target should be stated as: (1) 100% coverage = every applicable data point for top-1000 since 2015 is populated OR carries a verified reason (line_not_presented_in_filing / sector not-applicable) - zero UNEXPLAINED blanks; (2) 100% correct = every displayed value traces to an original filing, passed certification I1-I11, filing-verified (never Frames-verified, see 2026-10-18 lesson), with a measured defect-escape rate. This is finite (~1000 x ~30 concepts x ~44 quarters ~ 1.3M cells) and agent-verifiers are our equivalent of the vendors' analyst army. Industry claims are from general knowledge (ASSUMED); repo-internal facts (circular coverage, 64% unmapped facts, cert suite) are DOC-CITED in their own entries.
