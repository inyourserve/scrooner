# Tag Mapper: InterestExpenseOperating alternate and the bdc_total_investment_income group gate (2026-10-22)

Role: Tag Mapper. Status: COMPLETE for both read-only investigations; every row below is a PROPOSAL (nothing approved, no `concept_mapping` edit, no DB write, no migration). Reviewer chain: Standardization Lead (definitions) -> Verifier -> Data Engineer (group-scoped mapping capability).
Sources read first: data-team 20, 21, 22, 13; cards interest.md, investment-income-and-funds.md; PLAN.md "Tag Expert sector tag run" (item 2 and item 1).
Evidence labels: FILING-CHECKED = original filing R-file opened (SEC, declared User-Agent, <=2 req/s, 20 requests); DATA-INFERRED = our tables only.

## 0. Method and limits
- One read-only connection (`set default_transaction_read_only=on`, `statement_timeout=20s`), 10 client backends at every check (limit 12-14), no peer heavy job observed in `pg_stat_activity`. Chunks of 100 companies. Population read 2026-10-22; counts are of that moment.
- Facts: `core.fact.is_authoritative` only, duration periods, `period.end_date >= 2015-01-01`, undimensioned by construction of core.fact. "Existing value" = `analytics.canonical_fact` row for concept 10 `interest_expense` on the same `period_id`. "Same" = within 0.5%. Resolution is `first_match` per period (mapper/resolve.py), so a lower-priority tag only fills a period no higher tag has an authoritative fact for.
- Cohort: `doc/data-moat/team/top1000/shards.csv` (1,014 company_ids, 28 flagged `excluded`; all 1,014 kept here, flagged where it matters). Groups: `data-team/strategy/data/group_assignment_v2.csv` on branch work/sector-analyst/groups (worktree /Users/vikash/wt-sector-groups, 1,032 rows, ~top-1000 only). Outside that file no group exists, so the proxy is SIC 6021/6022/6029/6035/6036 = bank (DATA-INFERRED; the file itself disagrees with that SIC proxy for AXP, SOFI, SYF (group bank, SIC 6199) and CBC (group bank, null SIC)).
- Scripts (scratchpad, not committed): /private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/t1.py (pull), a1.py/a4.py/a6.py (classify), t5.py/t6.py/a7.py (BDC). Core query shape, parameterised by company-id chunk: authoritative `core.fact` concept 535 (IEO) joined to same-period authoritative 529 (InterestExpense), 1645 (InterestExpenseDebt) and `analytics.canonical_fact` concept 10.

## 1. Task 1: us-gaap:InterestExpenseOperating (core.concept 535) as an alternate for `interest_expense` (concept 10)

### 1.1 Current mapping (read)
concept_mapping for concept 10: InterestExpense (529) p1 approved; InterestExpenseDebt (1645) p2 approved ("Alternative label, same semantics"). Downstream inputs of concept 10: `interest_coverage_ratio` (operating_income / interest_expense) and `net_interest_income` (interest_income - interest_expense, with interest_income = `InvestmentIncomeInterest`, the securities-only line at banks per interest.md). No other metric reads it.

### 1.2 Reach (DATA-INFERRED, measured)
545 companies (538 active, 7 delisted) have >=1 authoritative IEO duration fact since 2015-01-01: 10,528 company-periods (quarters, YTDs, years).
| Population | IEO company-periods | GAIN (no existing value) | SAME as existing | CONFLICT: existing from InterestExpense | CONFLICT: existing from InterestExpenseDebt |
|---|---|---|---|---|---|
| All, bank (group bank, else the 5 bank SICs) | 6,849 / 318 cos | 4,497 / 312 cos | 2,292 / 290 | 32 / 7 | 28 / 6 |
| All, non-bank | 3,679 / 227 cos | 2,115 / 192 | 1,274 / 166 | 85 / 28 | 205 / 24 |
| Top-1000 cohort, bank | 917 / 43 | 597 / 42 | 317 / 41 | 2 / 1 | 1 / 1 |
| Top-1000 cohort, non-bank | 772 / 45 | 438 / 39 | 270 / 38 | 24 / 5 | 40 / 3 |
Companies that gain at least one period: 504 of 545 all; 81 of 88 in the cohort. 68 companies (5 in cohort) have every IEO period unfilled today. Fiscal-year view, all banks: gain 594 FY values / 296 banks; conflict 11 / 8 (IE or IED source).
Latest-year blank (the user-visible defect): of 306 banks with an FY IEO fact, 299 have NO `interest_expense` for their latest fiscal year (258 of 265 outside the cohort, 41 of 41 in it). Non-banks: 150 of 190 with an FY IEO fact have the latest year blank.
- "Would change a value": 0 under an IEO-after-IE placement for IE-sourced periods. The only changed values are periods whose current value comes from InterestExpenseDebt (bank 28 periods / 6 banks; non-bank 205 / 24; cohort 1 + 40) because IEO sits before IED.
- Downstream exposure of the gains (bank group): 95 gained periods / 10 banks also have `operating_income` (they would newly compute `interest_coverage_ratio`); 55 periods / 6 banks also have `interest_income` (they would compute `net_interest_income` from a securities-only numerator and a total-expense denominator, a wrong mixed-perimeter number). Both metrics need a bank block before or with this change.

### 1.3 Findings that shape the rule
1. **The existing p2 `InterestExpenseDebt` is a live wrong-value source for banks, not just a gap.** At 6 banks the canonical value is a debt component while the same filing's face total is on IEO (table 1.4). The IED fact wins today because nothing sits above it. Putting IEO after IED (p3) would leave those wrong values in place; IEO must sit above IED.
2. **IEO coexists with IE and IED in the same filing as a total vs component, never as a synonym of IED.** RBB 0001437749-25-008002 R4: face "Total interest expense" 117,297K is IEO; IED is 4,800K.
3. **Vintage differences IE vs IEO (32 bank periods / 7 banks; 85 / 28 non-bank) are reclassifications or restatements in a later filing, not tag-meaning differences.** CIVB FY2022: 11,049K in the 10-K/A 0000950170-23-011581 R4 (interest income 121,253K) vs 15,951K in the FY2024 10-K 0000950170-25-035961 R4 (interest income 126,155K); both tie to NII 110,204K. MNSB: FY2023 48,176K (0001437749-24-008676 R4) restated to 47,679K and FY2022 13,836K to 13,369K in 0001437749-25-007641 R4 (FILING-CHECKED, both internally consistent: 124,421K-47,679K = 76,742K). MS FY2023: IE 42,051K (10-K 0000895421-24-000300, value from the DB; filing not opened) vs 37,619K in 0000895421-25-000304 R3 (opened). Which vintage is "current" is a policy decision (section 1.6), not a mapping fact.
4. **Non-banks do file IEO with different meanings (the card's "banks only" scope must stay).** (a) Label "net": MTZ 0000015615-26-000020 R3 "Interest expense, net" 172,985K on IEO (FILING-CHECKED); HTZ "Interest expense, net" 1,077M on IEO incl. 608M vehicle interest (card, FILING-CHECKED earlier). (b) IP 0000051434-26-000055 R3: the face "Interest expense, net" 372M is tagged `InterestIncomeExpenseNet` (FILING-CHECKED) while the DB holds an IEO fact of 372M beside InterestExpense 551M (IEO equal to the net line: DATA-INFERRED; location of the IEO fact not opened). (c) Wrong sign: 21 IEO periods at 7 non-banks are negative (SSRM 15, in the cohort); SSRM's face interest expense in 0000921638-26-000035 R3 is on `InterestExpenseNonoperating` shown in parentheses, so its IEO facts are not the face line (FILING-CHECKED for the face, location of the IEO fact not opened). No bank has a negative IEO value. (d) Where IEO is the face total and IED a component, IEO is correct and the current IED value is wrong: CMC 0000022444-26-000041 R2 9M FY2026 "Interest expense" 105,981K (canonical 14,900K from IED), TPG 0001880661-26-000011 R5 FY2025 112,111K (canonical 102,300K), AFL 0001628280-26-011402 R3 FY2025 220M (canonical 217M), AXP 0000004962-26-000080 R3 FY2025 "Total interest expense" 8,234M (a gain). So for non-banks IEO is right in the cases checked, but "net" labels and the SSRM/IP cases mean it cannot be released population-wide without a per-group check.

### 1.4 Opened filings, changed or gained values (FILING-CHECKED; 11 values: 1 named gain, 5 bank IED corrections, 3 non-bank IED corrections, 2 vintage cases)
| Company | Accession, locator | Period | Value today (tag) | Value after (IEO) | Filing check |
|---|---|---|---|---|---|
| EFSC (named case) | 0001025835-26-000058 R5 "Interest Expense, Total" | FY2025 | none (gain) | 261,672K | row tagged InterestExpenseOperating; FY2024 282,955K and FY2023 202,327K on the same row already match our FY2024 value |
| RBB | 0001437749-25-008002 R4 | FY2024 | 4,800K (IED) | 117,297K | face "Total interest expense" 117,297K; 216,661K interest income less 117,297K = NII 99,364K on the face |
| NBBK | 0001104659-26-022367 R4 | FY2025 | 5,400K (IED) | 138,290K | deposits 132,879K + borrowings 5,411K = 138,290K; NII 197,458K |
| MYFW | 0001628280-26-012825 R5 | FY2025 | 2,400K (IED) | 84,419K | 159,787K - 84,419K = NII 75,368K |
| COLB | 0000887343-25-000054 R5 | FY2022 | 8,920K (IED, from a conflict: both InterestExpense copies are non-authoritative, 23,645K in the original 10-K vs 78,001K in the FY2023 10-K) | 78,001K | components 48,195K + 997K + 8,920K + 19,889K = 78,001K; 8,920K is only the borrowings line |
| HWBK | 0000893847-24-000016 R4 | 6 months to 2024-06-30 (and Q2 9,384K vs 216K) | 389K (IED) | 18,688K | face "Total interest expense"; 47,608K - 18,688K = NII 28,920K |
| CMC | 0000022444-26-000041 R2 | 9 months to 2026-05-31 | 14,900K (IED) | 105,981K | face "Interest expense" |
| TPG | 0001880661-26-000011 R5 | FY2025 | 102,300K (IED) | 112,111K | face "Interest expense" |
| AFL | 0001628280-26-011402 R3 | FY2025 | 217M (IED) | 220M | face "Interest expense" |
| CIVB | 0000950170-25-035961 R4 vs 0000950170-23-011581 R4 | FY2022 | 11,049K (IE, original) | 15,951K only if IEO is ranked above IE | vintage case, section 1.6 |
| MNSB | 0001437749-25-007641 R4 vs 0001437749-24-008676 R4 | FY2023 | 48,176K (IE) | 47,679K only if IEO above IE | vintage case, restatement |

### 1.5 PROPOSED mapping rows (not approved)
Stage A (recommended, bank group only; EFSC and 311 other banks gain, 6 banks stop showing a debt component as total interest expense):
| canonical concept | taxonomy:tag | priority | group gate | confidence | positive condition | negative condition |
|---|---|---|---|---|---|---|
| interest_expense | us-gaap:InterestExpense | 1 (unchanged) | all | approved (unchanged) | | |
| interest_expense | us-gaap:InterestExpenseOperating | 2 (new) | bank only (group_assignment_v2 `bank`; interim proxy SIC 6021/6022/6029/6035/6036 for companies outside the file) | candidate -> approved only after Verifier | undimensioned duration fact on the face "Total interest expense" | value < 0 (21 periods, none at a bank); a bank that files only a component without a total |
| interest_expense | us-gaap:InterestExpenseDebt | 3 (was 2) for the bank group; unchanged for other groups | all | approved (unchanged) | | |
Stage B (queue, do not release yet): the same IEO p2 for broker-dealers, asset managers, insurers, mortgage REITs, BDCs and corporates, only after the Sector Analyst assigns each group an interest-expense definition. Open issues: "net" labels (MTZ, HTZ, IP), negative values (SSRM), and that corporate `interest_expense` is described as "interest expense on debt" while IEO there is the face total. Cohort scale of Stage B: 39 non-bank cohort companies gain 438 periods and 3 (AFL, CMC, TPG) swap 40 periods from IED to the face total.
Engineering note for the Data Engineer: `analytics.concept_mapping` has no group column and `mapper/resolve.py` has no group-scoped priority. The gate needs a new capability (group-scoped mapping column or a post-resolve step like `concept_fallback.py`), a migration, and a dry-run of the proposed canonical_fact writes first. Not designed or written here.
Required alongside Stage A: block `interest_coverage_ratio` and `net_interest_income` for the bank group with a visible reason (or give banks their own NII definition on `InterestIncomeExpenseNet`), otherwise 95 and 55 bank-periods start showing meaningless or wrong ratios.

### 1.6 Open decisions (not mine to make)
1. Vintage ordering for banks: keep IE above IEO (no existing value changes; 32 bank periods / 7 banks keep the earlier, since-restated or reclassified figure) or put IEO above IE (those 32 periods move to the later presentation, which in the two banks opened, CIVB and MNSB, is the one that ties to its own statement; HTB, TFC, MS and the rest not opened). Recommendation: first release with IE above IEO (pure gain and IED correction), take the 32-period vintage question to the Standardization Lead and Verifier as a separate item, because "latest filing wins" cannot be validated by Frames (root CLAUDE.md, 2026-10-18).
2. Whether IED stays as an alternate for banks at all: it is a component at banks (RBB, NBBK, MYFW, COLB, HWBK), kept at p3 here only for a bank that files no total.

### 1.7 Withdraw the proposal if
- a bank is found whose IEO face total is not total interest expense (for example a segment-only total) in a filing sample drawn beyond the six banks above; or
- the Verifier opens >=1 bank period where IEO differs from the face total with no restatement explanation; or
- the group file's bank assignment is revised so that IEO filers placed in the bank group are not deposit-takers (AXP, SOFI, SYF, CBC are group `bank` but SIC 6199 or null: check their face lines before including them; AXP is FILING-CHECKED above).

## 2. Task 2: concept 205 `bdc_total_investment_income` group gate

### 2.1 State (DATA-INFERRED, measured 2026-10-22)
One mapping: GrossInvestmentIncomeOperating (core.concept 2551) p1 approved, first_match. No metric uses concept 205 (metric_definition_input has zero rows). Referenced by `mapper/coverage_matrix.py` (bdc_company population and gap reason), `mapper/expanded_concepts.py`, `sanity/yfinance_check.py`, `sanity/plausibility_check.py`, `parsers/revenue_parser.py` (comment).
canonical_fact rows: 3,648 over 118 companies (all active).
| Family (SIC) | Companies | canonical rows | In cohort |
|---|---|---|---|
| Null SIC (BDCs / closed-end funds; every one also files NetInvestmentIncome or InvestmentIncomeOperatingAfterExpenseAndTax or InvestmentIncomeInvestmentExpense) | 42 | 1,361 | 2 (ARCC, BXSL, group `bdc`) |
| Insurers SIC 63xx | 47 | 1,940 | 24 (group insurer; plus OSCR managed_care) |
| Insurance agents/brokers SIC 6411 (ACT, ARX, BWIN, WTW) | 4 | 100 | 2 (ACT, WTW) |
| Staking/commodity ETPs SIC 62xx incl. KKR | 12 | 76 | 1 (KKR, asset_manager) |
| Banks/credit 60-61 (FGNX, NEWT, SNFCA, SUIG) | 4 | 81 | 0 |
| Other (SPAC trust, BLZE, NXTT, VATE, VNOV, AFCG, HASI, CMRF, HHH) | 9 | 90 | 0 |
The group file assigns `bdc` to only 2 of the 42 BDCs (it covers the ~top-1000). The other 40 have no group, so a gate by `group = bdc` alone would drop 40 real BDCs from concept 205 until the Sector Analyst extends the file.

### 2.2 PROPOSED gate (not approved)
| canonical concept | taxonomy:tag | priority | group gate | note |
|---|---|---|---|---|
| bdc_total_investment_income | us-gaap:GrossInvestmentIncomeOperating | 1 (unchanged) | group = `bdc` ONLY; interim for companies without a group assignment: `core.company.sic_code is null` AND files at least one BDC marker tag (InvestmentIncomeOperatingAfterExpenseAndTax or NetInvestmentIncome) | FILING-CHECKED meaning for BDCs: ARCC 0001287750-26-000006 "Total investment income" top line |
Effect if gated (counts are exact for the current table, DATA-INFERRED):
- 42 BDCs keep 1,361 rows; 76 non-BDCs lose 2,287 rows (insurers 1,940, 6411 100, bank/credit 81, other 90, ETP/KKR 76). Cohort: 29 companies in the concept today, 27 lose it (24 insurers, OSCR, WTW and ACT among them, KKR), ARCC and BXSL keep it.
- `bdc_company` coverage population (coverage_matrix.py L344, L421: "has any value for this concept") falls from 118 to 42; that code needs to follow (Data Engineer / lane B). No metric loses an input.
- 9 BDCs that file no gross tag at all stay without a value (card; unchanged, by design: a net figure must not stand in for a gross concept).
Withdraw if: a BDC outside the null-SIC set files the gross tag as its top line, or a null-SIC filer in the 42 is not an investment company (spot-check: names are BDCs or closed-end funds; only ARCC opened, so the other 41 are DATA-INFERRED).

### 2.3 What insurers should map instead (PROPOSED new concepts; names are the Standardization Lead's call; they follow the Sector Analyst id `sr.ins.net_investment_income`)
| proposed concept | tag | priority | gate | meaning | evidence |
|---|---|---|---|---|---|
| insurer_net_investment_income | us-gaap:NetInvestmentIncome | 1 | group insurer (and 6411 mortgage-insurance filers such as ACT after group review) | face revenue line "Net investment income" (after investment expense) | CINF 0000020286-26-000008, TRV 0000086312-26-000065, PRU 0001137774-26-000048 face rows (card, FILING-CHECKED) |
| insurer_gross_investment_income | us-gaap:GrossInvestmentIncomeOperating | 1 | group insurer | gross note line before investment expense; identity gross = net + `InvestmentIncomeInvestmentExpense` | same three filings; population identity holds in 1,571 of 1,726 shared periods with all three tags (91%, DATA-INFERRED this run) |
Do NOT map: `InvestmentIncomeNet` (includes realized gains at PGR; differs from NetInvestmentIncome in 252 of 778 shared periods); `NetInvestmentIncome` for BDCs (pre-tax result; BDC after-tax NII is `InvestmentIncomeOperatingAfterExpenseAndTax`, a separate BDC concept for the Standardization Lead). PGR caveat: its face "Investment income" 3,583M is tagged `InterestAndDividendIncomeOperating`; the stored gross and net tags sit in the notes, so the face-versus-note location differs for that company (card).
Measured insurer reach (103 active companies: SIC 63xx or group insurer; authoritative duration facts since 2015):
- `NetInvestmentIncome`: 5,531 company-periods at 89 companies (cohort-id companies 2,775 / 43; others 2,756 / 46). Periods with the net tag but NO gross tag: 3,764 at 76 companies, so the net concept would fill about 3,764 periods the BDC concept never showed. Today only 1,983 insurer periods carry any value (the gross, mislabelled as BDC).
- `GrossInvestmentIncomeOperating`: 1,833 company-periods at 47 insurers (the 103-company insurer universe also holds 1,983 canonical concept-205 rows, which include conflict-filled and non-duration-filtered periods; the two counts are not reconciled, DATA-INFERRED).
- Gross equals net in only 40 of 1,767 periods where both exist (so the two are not interchangeable; magnitude of the gap was not measured beyond the three named filings, where gross exceeds net by investment expense: CINF 17M, TRV 53M, PRU 1,475M).
- Values are DATA-INFERRED beyond the three filings named; no new insurer filing was opened this run.
Withdraw if: an insurer's face "Net investment income" is found on a tag other than NetInvestmentIncome in a sample beyond CINF/TRV/PRU (PGR already shows face and note tags differ), or the Verifier finds an insurer whose undimensioned NetInvestmentIncome fact is a segment subtotal.

## 3. Handoffs and unresolved
- Standardization Lead: Stage A rows, the vintage ordering (1.6), the insurer concept names and definitions, bank block for interest_coverage_ratio and net_interest_income.
- Verifier: independent check of Stage A on banks not named here (draw 10 from the 312 gaining banks incl. the 41 cohort banks), the 5 non-opened vintage banks (HTB, TFC, SMBC, BYFC, QNTO), and the NBBK/MYFW/RBB-style IED swaps.
- Sector Analyst: extend `bdc` group assignment to the other 40 BDCs; bank vs card-lender (AXP, SOFI, SYF, CBC) decision for interest expense.
- Data Engineer / lane B: group-scoped mapping capability; redefine `bdc_company`; dry-run of canonical_fact writes (swap counts above are the expected diff: 4,497 inserts and 28 replacements for Stage A all-population; -2,287 rows for the BDC gate).
- NOT tested: Stage B groups; non-bank IEO facts' filing locations (IP, SSRM); pre-2021-09 banks (IEO does not exist there); whether conflict-fill rows (migration 0059) alter any counted "existing" value; all insurer values beyond CINF/TRV/PRU.
