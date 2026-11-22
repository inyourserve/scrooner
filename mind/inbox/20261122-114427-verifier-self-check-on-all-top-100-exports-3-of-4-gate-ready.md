---
id: verifier-self-check-on-all-top-100-exports-3-of-4-gate-ready
title: Verifier self-check on all top-100 exports: 3 of 4 gate_ready companies fail; verified_absent on whole hidden rows is the top class
kind: gotcha
tags: verifier, certify_display, top100, patterns
paths: pipeline/scripts/certify_display.py, data-team/tags/library/pattern_detectors.py
evidence: DATA-INFERRED
source: 2026-11-22 run of certify() over origin/main 0732d5d8 top100-coverage.csv
created: 2026-11-22
verified: 2026-11-22
---
certify() over the 95 company exports on main 2026-11-22: 79 companies have a FAIL besides OPEN cells. The top class: 586 cells at 42 companies where the export writes hide_class verified_absent on a HIDDEN_ROW (the verifier allows it only on a year). Next: 469 shown cells with no accession or R page, and about 300 parts with no page. JNJ and MA (gate_ready) fail only that class; WMT fails hidden_year shares FY2024 (a 10-Q comparative). resolve_cik fails for multi-CIK companies (AVGO BLK DIS GOOG LIN MRVL XOM): pass core.company.cik. The flow now runs certify_display.py --self-check-dir before gate_ready.
