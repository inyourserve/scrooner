---
id: fsn-notes-bucket-reads-use-pipeline-venv-python-system-3-14-
title: FSN-notes bucket reads: use pipeline/.venv python (system 3.14 has no CA bundle); num ddate is month-end rounded; cal 'negative' is the weight
kind: gotcha
tags: fsn, fsn-notes, supabase-storage, slot-records
paths: pipeline/scripts/slot_records/cf_face_extract.py
evidence: CODE-CHECKED
created: 2026-10-31
verified: 2026-10-31
---
(1) /Library/Frameworks python3 3.14 fails TLS to Supabase Storage with CERTIFICATE_VERIFY_FAILED; run storage reads with pipeline/.venv/bin/python after 'set -a; . pipeline/.env'. (2) zsh does not word-split unquoted $VAR in for-loops: a bulk loop over a list silently does one iteration; do bulk downloads in Python. (3) FSN num.tsv ddate is the period end rounded to the nearest month end, so match core.period end_date after rounding it the same way (day<15 -> previous month end). (4) FSN cal.tsv column 'negative' holds the arc weight itself (1 or -1), not a boolean. Bucket fsn-notes holds 59 period folders (2014q1-2025q3 + 2025m10-2026m09); sub/pre/num/cal for all = 1.6 GB.
