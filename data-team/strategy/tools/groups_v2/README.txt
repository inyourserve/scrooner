group.assign@2 tooling (Sector Analyst, WO-4, 2026-10-22). stdlib + the repo python only; no database.
  read_batch.py <ciks.txt> <outdir>   SEC reads (latest 10-K, else 10-Q: FilingSummary + BS/IS R-files) through the shared flock limiter, 4 req/s, SEC_USER_AGENT
  groups_v2.py / facelib.py            Signal A (FSDS-flag face shape, R4 rules) and Signal B (SIC bins)
  strict.py / strict_decide.py         Signal A from the filer's own R-file rows (Reader 1) and the reader-phase decision
  hand.py                              human reads (ticker -> group, variant, overlays, note) and exclusions
  build_v2.py / write_v2.py            assignment, review queue, move log, R4 disagreement file, face_features_v2.csv
                                       offline reproduction: SA_SCRATCH=/nonexistent python write_v2.py  (reads data/face_features_v2.csv)
  frames.py [seed] [outdir]            audit sampling frames; the Verifier lane re-draws with its own seed
  build_template.py                    template_v1_draft.csv over catalog_version
  face_tags.py / lead_coverage.py      per-group tag frequencies and lead-tag coverage
  enum_v2.py                           group / overlay / excluded enum and R4 family map
  ../acceptance/wo4.py                 AT-4.1a,b,c,d,e,g,h,l (AT-4.1f,i,j,k are NOT_RUN here)
Paths inside the scripts point at the worktree /Users/vikash/wt-sector-groups/ and a session scratchpad; change REPO / SA_SCRATCH when re-running elsewhere.
