---
id: top100-coverage-summary-display-certified-is-the-flow-s-mech
title: top100-coverage-summary display_certified is the flow's mechanical gate, NOT the verifier's PASS
kind: gotcha
tags: certification, coverage, verifier
paths: data-team/strategy/top100-coverage-summary.csv, data-team/strategy/approvals/registry.csv
evidence: DOC-CITED
status: active
created: 2026-11-22
verified: 2026-11-22
---
display_certified=yes in top100-coverage-summary.csv means only 0 open, 0 pageless, 0 blank parts (top100_coverage.py). Certification is Ritwik's verdict in data-team/strategy/approvals/registry.csv and approvals/certificates/*.json. 2026-11-22: MA showed yes but FAILED (whole-row hides exported as verified_absent instead of structural_not_presented). Count certified companies from the registry; the column is being renamed gate_ready. Ritwik certifies from request files on main, not from the summary.
