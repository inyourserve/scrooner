# Stage 5 Certify, M3: certificate loads and LLY tag-map, 2026-11-29

Authority quoted: founder, session scrooner-36, 2026-11-28: "everything is approve, dont wait for anything - founder message it is".

1. Certificates (dry run via display_cert_load, FILING-CHECKED vs registry.csv):
   - GILD-fc4df887df61, LRCX-c623fcf8ff31, MO-61b71f5091d2: match registry (PASS, sha). Dry run "would insert 0 rows": already loaded (scrooner-79). Not re-applied.
   - MA-d982df758b46: superseded; registry row is MA-ec326ca1b4a3, which is the one in the DB (506 rows). Not loaded.
   - BMY-1eafcef0c57f: loader refuses (drawn cell accounts_receivable 2020-12-31 result LOCATOR, PASS needs MATCH). Skipped per coordinator; Ritwik to resolve.
   - Status read-back (display_cell_certificate_status): GILD 504 valid/2 invalidated; MA 504/2; LRCX 550/2; MO 475/5; BMY no rows.
2. LLY (company 666) tagmap-authority dry run: demote 0, promote precision 0, restated 0, held 61 -> 61. Expected 18 rounded->precise swaps not present (fix 5e0036679 apparently already applied). NOT applied.
