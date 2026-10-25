# Existing readers: reuse, do not duplicate

| Need | Use | Where |
|---|---|---|
| R page -> labelled rows with column dates, face liabilities, seeded sample, verdict skeleton | `filing_kit.py` | `pipeline/src/scrooner_pipeline/verification/` (on main) |
| Rate-limited sec.gov client (`SEC_USER_AGENT`, 4/s, disk floor, request count), calculation-linkbase loader, same-accession instant/duration fetch, rounding unit, FSDS face rows | `pipeline/scripts/slot_records/common.py` | branch `work/scrooner-25/slot-records` (not yet on main); README there lists each function |
| Custom-tag and dimensioned mezzanine values from the filing instance | `instance_reader.py` | same slot-records folder |
| One calc file per boundary filing | `fetch_boundary_cal.py` | same slot-records folder |
| Quick R-page dump for one accession (prints rows, not parsed) | `sec_rpages.py` | `doc/data-moat/team/top1000/tools/` (hard-codes a UA; prefer `SecClient` + `fetch_statements`) |
| Balance-sheet gate logic (readings A/B, L&E tie) | `bs_replay.py`, `bs_assemble.py` | slot-records folder |
| Past verdicts to mirror | `VERIFY-BS-BATCH2-2026-10-25.md` | `data-team/strategy/team/` |

`filing_kit.fetch_statements(client, folder_url)` takes any object with `get(url) -> bytes`; pass `SecClient()` from slot-records `common.py` (`client.folder(cik, adsh)` gives the folder URL).
