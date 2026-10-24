# RF-14 operating income sample (2026-10-23)

Read-only measurement. No DB writes. Labels: FILING-CHECKED = I opened the filing R-page and read the figure; DATA-INFERRED = our tables only.

## Headline
- The target of 40 derived-path companies was NOT reached: the frame (350 of 986) held only 19 derived-path companies, so all 19 were taken. Control: 10 of 296.
- Derived path, 19 companies: stored value equals a figure the filing presents in 6 (32%, 95% interval about 15% to 54%); the filing presents no operating income line in the other 13 (68%, about 46% to 85%). PRESENTED-BUT-DIFFERENT: 0. Of the 13, 6 have only a stale old fiscal year stored (no value for the latest FY), so 7 are current-FY wrong-or-derived values.
- Control, single tag OperatingIncomeLoss, 10 companies: 10 of 10 equal a face line (0 of 10 not; upper 95% bound about 28%).
- Hidden-correct risk if a guard hides ALL derived values: 6 of 19 would hide a correct value (about 15% to 54%). By latest-FY value shown: 6 of 13 current-FY derived values are correct (interval about 23% to 71%).
- Named holds: none of the five is on the derived path. All five are single-tag OperatingIncomeLoss values, and none equals a face operating income line (the filings present none). A guard on the two-input derivation alone would not touch them.

## Method, seed, frame
- Seed 20261023 (Python `random`). `random.shuffle` of the 986 non-excluded company_ids of `doc/data-moat/team/top1000/shards.csv` (1014 rows, 28 excluded). Order saved at `/private/tmp/claude-501/scratch-RF14/order.txt`.
- DB budget forbade scanning all 986 (10 ids per query). I took the first 350 of the shuffled order (35 chunks of 10): this is the frame. Frame list = lines 1-350 of order.txt. Chunk 0 (first 10) was fetched in full; chunks 1-34 used the filter below.
- Exact frame query (chunks 1-34; `<10 ids>` = ten consecutive ids of the shuffled list):
  `set statement_timeout=20000; select l.company_id id, to_char(l.latest_period_end,'YYMMDD') pe, l.latest_value v, array_to_string(l.source_tags,'|') t from analytics.company_concept_lineage l join analytics.canonical_concept c on c.id=l.canonical_concept_id where c.name='operating_income_resolved' and l.company_id in (<10 ids>) and (cardinality(l.source_tags)<>1 or l.source_tags[1]<>'us-gaap:OperatingIncomeLoss');`
  Chunk 0 used the same query without the last filter line.
- Frame sizes (350 companies, DATA-INFERRED): derived path (source_tags has more than one tag, always including us-gaap:OperatingExpenses): 19 (5.4%). Of these, 10 are two-input (revenue tag + OperatingExpenses: PRU, EVR, LPLA, BRO, AJG, OXY, AMG, AFL, WDAY, REXR) and 9 three-input (revenue tag + CostOfRevenue or CostOfGoodsAndServicesSold + OperatingExpenses: NVDA, SNOW, RBRK, PATH, IOT, GPC, FCFS, ELAN, WELL). Single tag us-gaap:OperatingIncomeLoss: 296 (by subtraction, assuming every company has a lineage row; any company with no row would be counted here). No value, empty source_tags: 35 (10%). Nothing with a single tag other than OperatingIncomeLoss was seen.
- Extrapolation to the 986: not reliable from this frame; the derived share (5.4%) times 986 would be about 53 companies, interval wide. Prior note says 168 population-wide use exactly the two-input path.
- Sample: all 19 derived (fewer than 40 available) plus 10 controls drawn with `random.seed(20261023); random.sample(<single-path ids in frame>,10)`. Controls: TFX, PEGA, FLS, COO, V, LH, CLH, DINO, RVMD, VST.
- Stored value = `analytics.canonical_fact` `operating_income_resolved` (and `operating_income`) for the latest annual period (end minus start over 300 days) per company. Filing = the company's latest 10-K by filing date from SEC submissions JSON, income statement R-page via FilingSummary/R-page scan. For the named holds I used the latest 10-K (HONA: 10-Q, no 10-K exists).
- The lineage "latest_value" is often a quarter; the comparison here is the latest FISCAL YEAR value.

## Backend breakdown (pooler + app only; sum of Supavisor, Supavisor auth_query, PostgREST)
- Start of resumed run: Supavisor(postgres) 5, Supavisor (auth_query) 1, PostgREST 1 = 7 (excluded: Storage API 3, postgres_exporter 1, supabase_admin 1, mgmt-api 1).
- End: Supavisor 4, auth_query 1, PostgREST 1 = 6 (excluded: mgmt-api 2, postgres_exporter 1, supabase_admin 1).
- Earlier stop: total client backends 18 at one check (before the revised rule). About 40 DB queries in total; none exceeded 20 s.

## Sample table: derived path (19), all FILING-CHECKED for the filing side, DATA-INFERRED for the stored side
Class: M = PRESENTED-AND-MATCHES, N = NOT-PRESENTED. No PRESENTED-BUT-DIFFERENT. Accession is the latest 10-K; locator = R-page of the income statement.

| Co (id) | Stored FY value (unit as filed) | Accession | R | Class | Face figures |
|---|---|---|---|---|---|
| NVDA (2733) | FY26 130,387 | 0001045810-26-000021 | R3 | M | Operating income 130,387 |
| SNOW (3982) | FY26 (1,435,165) | 0001640147-26-000008 | R5 | M | Operating loss (1,435,165) |
| RBRK (3733) | FY26 (345,416) | 0001943896-26-000013 | R5 | M | Loss from operations (345,416) |
| PATH (5149) | FY26 56,760 | 0001734722-26-000012 | R5 | M | Operating income 56,760 |
| WDAY (5069) | FY26 721 | 0001327811-26-000014 | R5 | M | Operating income 721 |
| IOT (4017) | FY26 (52,576) | 0001628280-26-018167 | R5 | M | Loss from operations (52,576) |
| PRU (3882) | FY25 25,225 | 0001137774-26-000048 | R5 | N | No operating line; total revenues less total benefits and expenses is pretax; stored matches neither |
| EVR (5393) | FY25 814,206 | 0001628280-26-010273 | R5 | N | Total Revenues 3,880,084 less Total Expenses 3,065,878 = 814,206, but the face shows Net Revenues less expenses = 789,942 and pretax 793,814; no operating line |
| GPC (612) | FY25 960,651 | 0000040987-26-000003 | R5 | N | Gross profit 8,940,698 less total operating expenses 7,980,047 = 960,651; the face has no operating income line (pretax 52,168 after 741,967 pension charge) |
| FCFS (1608) | FY25 1,259,851 | 0000840489-26-000032 | R5 | N | Total revenue 3,661,043, net revenue 1,840,607, pretax 447,563; stored equals none; no operating line |
| AJG (1233) | FY25 11,684 ($M) | 0001628280-26-008662 | R3 | N | Total revenues 13,942, total expenses 12,071, pretax 1,871; no operating line |
| AMG (2152) | FY25 269.0 ($M) | 0001628280-26-008665 | R3 | N | Revenue 2,074.4 less total consolidated expenses 1,805.4 = 269.0; face has no operating line (expenses include interest; pretax 1,186.3) |
| AFL (109) | FY25 11,826 ($M) | 0001628280-26-011402 | R3 | N | Revenues 17,164 less "total acquisition and operating expenses" 5,338 = 11,826; the face shows total benefits and expenses 12,631 and pretax 4,533; no operating line |
| LPLA (5683) | stale FY20 731,838; no FY25 value | 0001628280-26-010705 | R3 | N | No operating line (pretax 1,149,507) |
| BRO (1036) | stale FY23 1,146 | 0001193125-26-046984 | R2 | N | No operating line (total revenues 5,902, total expenses 4,531, pretax 1,371) |
| OXY (1492) | stale FY15 11,210 | 0001628280-26-009059 | R5 | N | No operating line (pretax and other items 3,052) |
| ELAN (5212) | stale FY20 56.7M | 0001739104-26-000012 | R3 | N | No operating line (pretax (224)M) |
| REXR (3070) | stale FY19 (192,057) | 0001571283-26-000006 | R5 | N | No operating line (total operating expenses 622,500, total expenses 800,014) |
| WELL (1421) | stale FY18 (2,009,527) | 0000766704-26-000010 | R4 | N | No operating line (income before taxes and other items (480,025)) |

Notes:
- Stale rows: the latest stored annual value is an old year (stored column shows its year). Nothing is stored for the latest FY, so the stored-versus-face comparison for the latest FY is "no value shown; filing presents none". These 6 are class N on the filing side only; whether an old-year value is also not presented was not opened.
- By input count: 5 of 9 three-input and 1 of 10 two-input derivations match a face line; 4 of 9 three-input and 9 of 10 two-input are not presented. Matches occur only where the company presents a face operating line.
- Six matched rows are all technology/software issuers with a face "operating income/loss" line. All 7 current-FY N rows are insurers, brokers, asset managers, retail finance or distributors without that line (PRU, AFL, AJG, EVR, AMG, FCFS, GPC).

## Control: single-tag OperatingIncomeLoss (10), all FILING-CHECKED
| Co (id) | Stored FY | Accession | R | Class | Face line |
|---|---|---|---|---|---|
| TFX (1100) | FY25 118,373 | 0000096943-26-000019 | R3 | M (caveat) | "Income from continuing operations before interest and taxes" 118,373; the company labels no line "operating income" |
| PEGA (2271) | FY25 263,100 | 0001013857-26-000017 | R5 | M | Income from operations 263,100 |
| FLS (353) | FY25 399,924 | 0000030625-26-000003 | R5 | M | Operating income 399,924 |
| COO (1274) | FY25 682,900 | 0001628280-25-055615 | R3 | M | Operating income 682,900 |
| V (5718) | FY25 23,994 ($M) | 0001403161-25-000089 | R5 | M | Operating income 23,994 |
| LH (1913) | FY25 1,384.7 ($M) | 0000920148-26-000111 | R5 | M | Operating income 1,384.7 |
| CLH (1565) | FY25 673,372 | 0000822818-26-000009 | R5 | M | Income from operations 673,372 |
| DINO (3600) | FY25 927 ($M) | 0001915657-26-000016 | R5 | M | Income from operations 927 |
| RVMD (3831) | FY25 (1,182,369) | 0001193125-26-071563 | R4 | M | Loss from operations (1,182,369) |
| VST (4655) | FY25 1,906 ($M) | 0001692819-26-000006 | R3 | M | Operating income 1,906 |

Result: 10 of 10 match (interval about 72% to 100%). Not-presented 0 of 10 (upper bound about 28%).

## Named holds (all FILING-CHECKED unless stated)
All five have lineage source_tags = us-gaap:OperatingIncomeLoss (single tag, not the derived path; DATA-INFERRED). The tag is filed by the company but the number is not a face line.
- AFG (2668), 10-K 0001042046-26-000010, R5: stored FY25 1,073 ($M). The face shows total revenues 8,174, total costs and expenses 7,101, "Earnings before income taxes" 1,073. No operating income line. Class N: the stored value equals pretax earnings.
- ELS (1805), 10-K 0001628280-26-008722, R5: stored FY25 391,349. The face shows total revenues 1,531,382, total expenses 1,140,033, "Income before taxes and other items" 391,349. No operating income line. Class N: the stored value equals that pretax-type line.
- MOG-A (705): stored FY25 (period end 2025-09-27) 449,606; Moog 0001628280-25-054103 R3 is already FILING-CHECKED (cited as instructed). My read of the same R3: face has gross profit, R&D, SG&A, interest, "Earnings before income taxes"; no operating income line. Class N.
- MET (3459), 10-K 0001099219-26-000013, R5: stored FY25 6,137 ($M). The face shows total revenues 77,084, total expenses 72,423, "Income (loss) before provision for income tax" 4,661. No operating income line; 6,137 appears nowhere on the face. Class N. Where 6,137 comes from was not traced.
- HONA (5063): no 10-K exists (Form 10-12B 0001628280-26-013549 filed 2026-03-03 and 10-Q 0002089271-26-000021 only). No annual value is stored (DATA-INFERRED). Stored quarter 995 (period 2026-06-27). 10-Q R2 face shows net sales 4,522, total costs, expenses and other 4,144, income before taxes 378; no operating income line, and 995 is not on the face. Class N for the quarter; the 10-K comparison is not possible.

Count among named holds: 5 of 5 class N, none on the derived path. These are chosen cases, not a random sample, so no rate is claimed.

## Limits
- Frame is 350 of 986 (35.5%), a random subset, not the whole top-1000 (budget of about 100 queries and 10 ids per query). Only 19 derived-path companies were found, so the sample is a census of the frame's derived companies, not a sample of 40. The frame-based shares have wide intervals; do not scale to 986 without more chunks.
- Stored values are the latest stored annual period (period length over 300 days), not the latest quarter. For 6 derived companies the latest annual stored value is years old, so the latest-FY comparison there is only "filing presents no operating line"; the old stored year was not opened against its own 10-K.
- "Equal to a presented figure" was tested only against the latest 10-K income statement page; segment notes, MD&A and non-GAAP tables were not searched, so a stored number could be presented elsewhere (MET's 6,137 might be; not checked). The face-line test is the strict one the task asked for.
- No 10-K R-page scan covered a company whose income statement is outside R2-R9 (none were missed here; NVDA needed R3 refetched after an empty cached page).
- HONA has no 10-K; no 10-K check is possible.
- Class M for TFX relies on treating "Income from continuing operations before interest and taxes" as its operating-level line.
- Derived equality with an arithmetic subtotal (EVR, GPC, AMG, AFL) was found by recomputing from face lines; the formula was inferred (DATA-INFERRED), the inputs are FILING-CHECKED.
- No fixes are proposed here.
