# Verify: Retirement Family B plan B15 (work/dhairya/family-b-csgp 11cdebb), 2026-10-31

Seed 20261031. Files: dryrun_B15/B_proxy_form_scale_check.csv, B_proxy_form_cells.csv; report data-team/strategy/team/FAMILY-B-B15-2026-10-30.md. Claimed counts: new scale candidates=30 (27 exact, 1 rounded unchanged, 1 rounded changed, 1 hidden); B14b to B15 changed cells=2. Evidence class: FILING-CHECKED (each input filing's own income-statement R page). Verifier 2 (scrooner-bc).

## Result
**Ready for apply review: YES.** GATE (zero wrong shown values) PASSES: 11 of 11 shown cells right, 0 wrong (CSGP Q4 2023 plus 10 seeded draws from the new candidates). The one hidden cell (LNG Q4 2025) is an avoidable hold, not a wrong value: the filing supports 2,302M exactly, and hiding it removes production's wrong 3,766M.

## Method
For each derived quarter, Q4 = FY (12-month column of the claimed 10-K accession) minus 9M YTD (9-month column of the claimed 10-Q accession). Both read from the filing's own income statement (`filing_kit.select_income_statement` + `parse_rpage`), columns by date and duration, scale from the page header, rounding unit = scale x 10^-printed decimals. Shown value is right when it equals the face derivation at the coarsest printed unit of its inputs. Production's value and the builder's code path were not used as evidence.

## Sample
The 2 changed cells named in the brief, plus 10 of the 27 remaining new candidates (the 30 new = B15 scale_check rows not in B14b's), `random.seed(20261031); random.sample(pool sorted by canonical_fact_id, 10)`.

## Cell table
| Company (CIK) | Quarter end | FY accession / 9M accession (IS R page) | FY face | 9M face | Face Q4 (unit) | Shown | Verdict |
|---|---|---|---|---|---|---|---|
| CSGP (1057352) | 2023-12-31 | 0001057352-25-000016 / 0001057352-23-000127 | 374.7M ($M, 1 dp) | 278,225K | 96.475M -> 96.5M (100K) | 96,500,000 | right |
| LNG (3570) | 2025-12-31 | 0000003570-26-000005 R3 / 0000003570-25-000107 R2 | 5,330M attrib. | 3,028M attrib. | 2,302M (1M) | hidden (derived_scale_unverified) | avoidable hold |
| CHE (19584) | 2024-12-31 | 0001562762-26-000020 / 0001562762-24-000248 | 301,999K | 211,680K | 90,319K | 90,319,000 (net_income_resolved) | right |
| CHE (19584) | 2024-12-31 | same | same | same | 90,319K | 90,319,000 (net_income) | right |
| CHE (19584) | 2021-12-31 | 0001562762-24-000045 / 0001562762-21-000385 | 268,550K | 193,925K | 74,625K | 74,625,000 | right |
| IT (749251) | 2021-12-31 | 0000749251-24-000006 / 0000749251-21-000038 | 793,560K | 584,201K | 209,359K | 209,359,000 | right |
| KMX (1170010) | 2023-02-28 | 0001170010-25-000024 / 0001170010-23-000006 | 484,762K | 415,750K (9M to 2022-11-30) | 69,012K | 69,012,000 | right |
| EXEL (939767) | 2026-01-02 | 0000939767-26-000021 / 0000939767-25-000128 | 782,570K | 538,042K (9M to 2025-10-03) | 244,528K | 244,528,000 | right |
| ST (1477294) | 2021-12-31 | 0001477294-24-000020 / 0001477294-21-000151 | 363,580K | 251,608K | 111,972K | 111,972,000 | right |
| DT (1773383) | 2025-03-31 | 0001773383-26-000019 / 0001773383-25-000009 | 483,684,000 ($1) | 444,380K | 39,304K (1K) | 39,304,000 | right |
| VRSN (1014473) | 2021-12-31 | 0001014473-22-000007 / 0001014473-21-000027 | 784,830K | 454,748K | 330,082K | 330,082,000 | right |
| KYMR (1815442) | 2025-12-31 | 0001193125-26-073395 / 0001193125-25-263550 | -311,351K | -224,370K | -86,981K | -86,981,000 | right |

## Withheld cells (avoidable holds)
- **LNG (company 101) Q4 2025 net income attributable to Cheniere: 2,302M is right as printed.** FY 2025 "Net income attributable to Cheniere" 5,330 (10-K 0000003570-26-000005, R3, "$ in Millions") minus 9M 2025 3,028 (10-Q 0000003570-25-000107, R2, "$ in Millions"). Both inputs printed in millions with 0 decimals: unit 1M, the derived value is exact. (Consolidated would be 6,794 - 3,861 = 2,933M; the cell is the attributable concept, consistent with the plan's FY replacement 6,794M -> 5,330M.) Production currently shows 3,766M = 6,794 consolidated FY minus 3,028 attributable 9M, a mixed-basis wrong value, so hiding is still a strict improvement.
- **Why the scale reader failed:** the scale WAS readable ("$ in Millions" in the R2 title). `filing_kit.parse_rpage` drops the duration of every column on this page: the header row "3 Months Ended" / "9 Months Ended" each have colspan=3 because the "Sep. 30, 2024" date cells carry colspan=2 (a footnote spacer column), so `spans` has 6 entries against 4 date columns, the length check fails and `months` becomes all None. `FilingFace.printed_unit` then calls `page.column(2025-09-30, 9)` (KeyError: no column with months=9) and falls back to `page.column(2025-09-30)`, which raises AmbiguousColumn (two Sep 30 columns, a KeyError subclass), so it returns None and the cell is hidden. A kit defect, not a filing gap.

## False holds
None found.

## Findings for the builder
1. Fix `filing_kit.parse_rpage` duration spans: expand the duration header by date-cell position (each date header cell's own colspan), not by raw colspan count, so footnote spacer columns do not desync `months`. Fixture: LNG 0000003570-25-000107 R2 (expect months [3, 3, 9, 9]). After the fix, re-run B15 and re-verify LNG Q4 2025 shows 2,302,000,000; check whether other pages in the candidate set were silently relying on the fallback.
2. Optional: in `FilingFace.printed_unit`, when the page's months are all None, say so in the hold reason ("duration header unread") so this class is countable separately from truly unreadable scales.
3. CSGP precision fix (`_scale_suspect` trailing-power-of-ten selection): confirmed on the filing; no change requested.

## Requests and disk
SEC requests: 51 (44 for the 12 cells, 6 for the LNG pair re-read, 1 raw R2 header). Downloads held in memory only; scratch scripts deleted. Free disk on /private/tmp: about 14 GB.

## Untested scope
17 of the 27 exact-or-unchanged new candidates were not drawn; the 9 old candidates were not re-read (B14b to B15 report says unchanged). Only the scale-candidate subset of B15 was verified, not the 657 replacements / 142 removals as a whole (covered by the B14 verdict and its delta). The Pinnacle W3/Family B restore-order caveat in the B15 report was not exercised.
