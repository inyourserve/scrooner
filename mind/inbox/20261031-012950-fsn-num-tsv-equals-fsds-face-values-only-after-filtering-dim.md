---
id: fsn-num-tsv-equals-fsds-face-values-only-after-filtering-dim
title: FSN num.tsv equals FSDS face values only after filtering dimn=0, iprx=0, empty coreg
kind: howto
tags: fsn, fsn-notes, fsds, face
paths: pipeline/src/scrooner_pipeline/mapper/quick_ratio_face.py
evidence: CODE-CHECKED
created: 2026-10-31
verified: 2026-10-31
---
FSN num also carries note, dimensional and repeated facts; FSDS num.txt is face-only. quick_ratio_face.fsn_face_num keeps dimn=='0' and iprx=='0' and no coreg, then faces_from_rows reads the same as an FSDS zip: EOG 0000821189-15-000023 gave an identical face from both, and FTAI 0001590364-24-000003 matched at its own date (FSDS also listed 2 stray dates). Lets face reads come from bucket fsn-notes instead of sec.gov (saves the SEC budget). Bucket extracts hold cohort filings only.
