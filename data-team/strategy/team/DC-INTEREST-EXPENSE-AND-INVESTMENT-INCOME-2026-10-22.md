# Decision card: bank interest expense, vintage ordering, bank metric block, insurer and BDC investment income (Standardization Lead, 2026-10-22)

Status: **PROPOSED** (decision kinds: mapping, definition, release precondition). Not verified, not approved. The Standardization Lead cannot approve its own rule. Next step: Verifier re-read from the filings, then a Data Engineer dry-run (section 8). No code, data, mapping or migration was changed.
Input: `TAG-MAPPER-INTEREST-EXPENSE-AND-BDC-GATE-2026-10-22.md` (the Tag Mapper report) and PLAN.md "Tag Mapper: interest_expense + BDC gate".
Evidence labels: **FC** = FILING-CHECKED (I opened the R-file and/or the XBRL instance myself this run; accession and locator cited). **FC-TM** = filing-checked by the Tag Mapper or Tag Expert, not re-opened by me. **DI** = DATA-INFERRED (our tables). **CR** = CODE-READ. **AS** = ASSUMED.
Method: about 30 SEC requests at about 1 per second with the declared User-Agent (another session was also fetching). R-files parsed for row label plus `defref` tag; instances parsed with context resolution (period, dimensions, decimals). One read-only DB connection, `statement_timeout` 20 s, chunks of 50 companies; a peer's 47-minute query was running, so only one light query was made. Scripts: scratchpad `tools/rrows.py`, `tools/facts.py`, `tools/ixctx.py`, `tools/getinst.sh` (not committed).

## 0. Decisions in one table
| # | Question | Decision (proposed) | Basis |
|---|---|---|---|
| D1 | Stage A bank rows | `InterestExpense` (IE) and `InterestExpenseOperating` (IEO) form **one exact pair** for the bank line "Total interest expense". **`InterestExpenseDebt` (IED) is removed from `interest_expense` for banks**, not moved to p3. Gate = the production bank predicate `common/sector_applicability.bank_predicate_sql`. A negative value is held with a reason, never skipped to the next tag | FC at 5 banks: IED is never the total, and at HWBK it is not interest expense at all |
| D2 | Vintage order when IE and IEO differ for one bank period | **The value from the later periodic filing wins** (2026-10-18 ruling), with the ruling's carve-outs plus four guards. "IE above IEO" is **rejected** for release. If the pair rule is not built for Stage A, the vintage-conflict periods are **held blank with a reason**, not shown with the superseded value | FC: CIVB's later value is an error correction it disclosed; MNSB's is an undisclosed reclassification with net income unchanged |
| D3 | Bank metric block | A block already exists (CR). Release preconditions: the same bank predicate for the mapping gate and the block; certify I10 `bank_shows_suppressed_metric` = 0 on the dry-run. Recommended: also null `net_interest_income` for banks at compute time. A bank NII gets its own concept later (not in Stage A) | CR: commits 5b96ff2 and 153574d |
| D4 | Insurer concepts; concept 205 | New `insurer_net_investment_income` (`NetInvestmentIncome`) and `insurer_gross_investment_income` (`GrossInvestmentIncomeOperating`), insurer-gated. Concept 205 `bdc_total_investment_income`: **restrict to BDCs, do not rename**; retire its insurer and other non-BDC rows; correct its description | FC: CINF, ARCC instances |
| D5 | Accountant | **None of D1-D4 needs the accountant to ship as as-reported values.** Existing cards cover the follow-ons: AC-19 (growth/TTM across a restated or reclassified bank period); AC-11 (whether insurer net investment income enters insurer revenue); AC-15 (Stage B non-bank interest expense) | section 6 |

## 1. What I verified from the filings (before reading the Tag Mapper's rationale)
| Company | Accession, locator | Face total interest expense (tag) | Where the IED fact sits | IED value | Reading |
|---|---|---|---|---|---|
| RBB | 0001437749-25-008002 R4; instance `rbb20241231_10k_htm.xml` | "Total interest expense" 117,297K (IEO) FY2024; NII 99,364K (`InterestIncomeExpenseNet`) = 216,661K - 117,297K | Long-term-debt note table "Interest Expense: Interest" (FY2024 4,800K, decimals -5; FY2023 7,916K; FY2022 8,199K); dimensioned narrative 1.3M on subordinated debentures | 4,800K | component (debt note) |
| NBBK | 0001104659-26-022367 R4; instance `nbbk-20251231x10k_htm.xml` | "Total interest expense" 138,290K (IEO) = deposits 132,879K + borrowings 5,411K (`InterestExpenseBorrowings`); NII 197,458K | Narrative: "Interest expense on FHLB borrowings approximated $5.4 million" (fact ids `Narr_...`, decimals -5) | 5,400K | component, rounded narrative of the 5,411K face line |
| MYFW | 0001628280-26-012825 R5; instance `myfw-20251231_htm.xml` | "Total interest expense" 84,419K (IEO); NII 75,368K = 159,787K - 84,419K | Narrative: "recorded $2.4 million ... of interest expense related to the collective subordinated notes" (decimals -5) | 2,400K | component (subordinated notes) |
| COLB | FY2024 10-K 0000887343-25-000054 R5; **FY2023 10-K 0000887343-24-000089 R5**; original FY2022 10-K 0000887343-23-000072 R5 | FY2022: 78,001K, on IEO in the FY2024 10-K and on IE in the FY2023 10-K; NII 1,070,016K | **Face row "Interest on borrowings" in the FY2023 10-K** (FY2022 8,920K); the FY2024 10-K files that row on custom `colb_InterestExpenseFHLBFRBAndOtherLongTermDebt` and has **no IED fact** | 8,920K | component (face sub-line) |
| HWBK | 0000893847-24-000016 R4; instance `hwbk-20240630_htm.xml` | "Total interest expense" 18,688K (IEO) for 6 months to 2024-06-30, Q2 9,384K; NII 28,920K = 47,608K - 18,688K | **Face row "Loan expense" under NON-INTEREST EXPENSE**, between "Postage, printing, and supplies" (`SuppliesAndPostageExpense`) and "Other" (`OtherNoninterestExpense`); inside "Total non-interest expense" 24,609K | 389K (6M), 216K (Q2) | **not interest expense at all**: a filer misuse of IED |
| CIVB | 10-K/A 0000950170-23-011581 R4 vs FY2024 10-K 0000950170-25-035961 R4 and main document | FY2022 11,049K (IE, interest income 121,253K) vs 15,951K (IEO, interest income 126,155K); NII 110,204K in both | n/a | n/a | **error correction**: the FY2024 10-K ticks the cover-page box "financial statements ... reflect the correction of an error". Its note: loan participations sold "deemed to not qualify for sales accounting under ASC 860" raised FY2022 interest income and interest expense by 4,902K (and FY2023 interest expense by 3,312K), with no effect on net income |
| MNSB | FY2023 10-K 0001437749-24-008676 R4 vs FY2024 10-K 0001437749-25-007641 R4 and main document | FY2023 48,176K (IE) vs 47,679K (IEO); FY2022 13,836K vs 13,369K | n/a | n/a | **undisclosed reclassification, not a restatement**: the error-correction box is unticked and no note explains it. FY2023 net income is 26,585K in both. Line items move: NII 75,947K to 76,742K, non-interest income 3,638K to 3,340K, non-interest expense 45,119K to 45,616K. Both vintages tie to their own NII |

Also confirmed (FC): COLB FY2023 10-K MD&A says "the Merger was accounted for as a reverse acquisition ... financial results for any periods prior to the Merger Date reflect UHC results only". So COLB's FY2022 78,001K is **Umpqua Holdings' FY2022**. The original 23,645K (0000887343-23-000072 R5, interest income 646,481K) is legacy Columbia's. That is two entities, not a restatement: the same class as ledger row 82 (Vivmark).

**Corrections to the Tag Mapper report** (not a different conclusion, but on record):
- COLB's IED 8,920K comes from 0000887343-24-000089. The cited 0000887343-25-000054 holds no IED fact.
- HWBK's IED is a non-interest expense line ("Loan expense"), not borrowings interest.
- MNSB is a reclassification, not a restatement; CIVB is an error correction, not a reclassification.
- The COLB FY2022 conflict is a reverse-acquisition entity change.

## 2. D1: bank `interest_expense` (concept 10, and `interest_expense_resolved`, concept 250, which the statement row "Interest Expense" displays)
**Is IED really a component at banks? Yes, or worse.** The FASB definition of IED is "cost of borrowed funds accounted for as interest expense for debt" (card interest.md section 1). A bank's total interest expense is dominated by deposit interest, so IED cannot be the total by definition. Filings: it is a debt-note or narrative sub-figure at RBB, NBBK and MYFW, a face sub-line at COLB, and a non-interest expense at HWBK (FC, section 1). Keeping IED at p3 "for a bank that files no total" would still publish a sub-line or a non-interest figure as total interest expense. **Remove it for the bank group.** It stays unchanged for non-banks (Stage B / AC-15).

### 2.1 Concept contract, bank variant of `interest_expense` (stable ID unchanged: 10; 250 follows)
- **Economic definition (bank):** total interest expense on deposits, borrowings and other interest-bearing liabilities for the period, as presented on the face income statement line "Total interest expense" (the subtrahend of net interest income).
- **Statement:** income statement. **Period:** duration. **Unit:** USD only. **Consolidation:** undimensioned, registrant default context (combined filings per ledger row 83).
- **Sign:** as filed, debit-positive. A negative value is held with reason `sign:negative_on_expense_tag` (quarantine; the domain rule is never flip, never fall through). It does not fall through to another tag.
- **Source slot:** `us-gaap:InterestExpense` and `us-gaap:InterestExpenseOperating` are the same line in two tag eras (IE through about 2021-2024, IEO from 2021-09; card interest.md section 2; 98.6% equal in 2,254 shared bank periods, DI). This is an **exact** equivalence at banks only.
- **Excluded at banks:** `InterestExpenseDebt`, `InterestExpenseDeposits`, `InterestExpenseBorrowings` and every other component tag (components); `InterestIncomeExpenseNet` (a net figure; `concepts.py` already excludes it).
- **Selection within the slot:** section 3 (D2).
- **Components only (no IE/IEO fact for the period):** blank with reason `bank:total_interest_expense_not_tagged` (an investigable gap, never structural without the face statement). Summing components is a composition rule this card does **not** approve.
- **Conflict-fill path** (`mapper/conflict_resolution.py` fills `interest_expense_resolved` when all copies conflict, tie-break highest fact_id, CR): for banks it must use the same slot, the same IED exclusion and the D2 vintage rule. Today it is a second route for an IED or superseded value into the displayed row.
- **Gate:** `common/sector_applicability.bank_predicate_sql` (SIC 6020-6036 plus `NoninterestExpense` plus a deposit tag; 322 active banks, DI, read 2026-10-22). It is **the same predicate that already suppresses bank metrics**. Do not use the Tag Mapper's interim 5-SIC proxy or `group_assignment_v2.csv` for this gate. Two bank definitions would let a company get bank interest expense while keeping non-bank metric treatment. AXP, SOFI, SYF and CBC fall outside the predicate and stay in Stage B until the Sector Analyst rules (AXP's face total is IEO 8,234M, FC-TM).
- **Downstream:** `interest_coverage_ratio` (`definitions.py` L163) and `net_interest_income` (`expanded_definitions.py` L337) both read it (CR). Both are suppressed for banks (D3). The income-statement row "Interest Expense" (`statements/classify.py`) is displayed for banks and is **not** suppressed (CR).

### 2.2 Proposed rows (supersede the Tag Mapper's Stage A table)
| canonical concept | tag | role at banks | at non-banks |
|---|---|---|---|
| interest_expense | us-gaap:InterestExpense | bank slot member (D2 selection) | p1, unchanged |
| interest_expense | us-gaap:InterestExpenseOperating | bank slot member (D2 selection); candidate until Verifier | not mapped (Stage B) |
| interest_expense | us-gaap:InterestExpenseDebt | **excluded** | p2, unchanged (AC-15 owns its fate) |

**Mechanism (recommendation to the Data Engineer, not a design):** first_match priority rows cannot express a two-tag latest-filing selection or a group-only exclusion. The repo idiom that fits is a post-resolve bank step (`mapper/concept_fallback.py` pattern, CR), with a migration and a dry-run first. Choosing the mechanism is the Data Engineer's call; the semantics above are the requirement.

### 2.3 Live defect today (DI, sized this run)
Under the production bank predicate, `interest_expense` has **56 rows at 8 banks** whose first source fact is IED, and `interest_expense_resolved` has **64 rows at 10 banks** (since 2015-01-01; query: `canonical_fact.source_fact_ids[1]` joined to `core.fact.concept_id`, chunked). By D1 every one of them shows a component or a non-interest line as "Interest Expense" on a bank's income statement. **Interim until Stage A ships:** hide those cells at serve time with the reason "bank interest expense mapping pending" (the 2026-10-19 serve-time pattern), rather than leave known-wrong values displayed. This is a product action for the Data Chief / Dhairya to authorize.

## 3. D2: vintage ordering when IE and IEO differ for the same bank period
**The ruling it must agree with** (`doc/data-moat/decisions.md`, 2026-10-18): for a period a later filing restated, the stored value is the latest-filed figure, and the original stays as a non-authoritative copy with lineage. The reason given is that a time series is comparable only on one basis. Carve-outs: a later value that is a labelling error does not win, and a rounded copy never beats a precise one.

**Decision.** Treat IE and IEO at a bank as one slot. When both have authoritative facts for the period and differ beyond rounding (decimals-interval overlap, domain 8.4), **take the fact from the later periodic filing** (10-K, 10-Q, 10-KT and amendments; ordered by filing date, then acceptance time). Guards; if any fires, hold with reason `vintage:unresolved` and keep both facts as lineage:
1. **Periodic forms only** (ledger row 77): 8-K and DEF 14A facts never compete.
2. **Label-error signal** (ledger row 33): the later value equals the same company's IE/IEO value for a different period.
3. **Same-filing tie:** the later fact's interest income minus interest expense must equal that filing's NII (`InterestIncomeExpenseNet`) within rounding. Both CIVB and MNSB vintages pass, so this is a sanity guard, not a tie-breaker.
4. **Entity change:** an 8-K Item 2.01 reverse acquisition between the two filings (COLB/Umpqua 2023, FC). The later basis is the accounting acquirer's and is the series that continues, so it wins for the periods the later filing presents. Earlier periods that only legacy-registrant filings cover are a different entity. Route that history to Gate A identity (ledger row 82); this card does not decide it.

**Outcomes on the filing-checked cases.**
- CIVB FY2022: **15,951K** (an error correction the filer disclosed under ASC 860; the original is a known-corrected figure).
- MNSB: FY2023 **47,679K**, FY2022 **13,369K**. This is the filer's current presentation, and the definition (face total interest expense) is unchanged across vintages.
- COLB FY2022: **78,001K**. Under D1 this is already the only authoritative candidate once IED is excluded. The IE copies conflict (23,645K vs 78,001K, both non-authoritative), so it arrives from the single authoritative IEO fact in 0000887343-25-000054.

**Why "IE above IEO" (the Tag Mapper's first-release recommendation) is rejected.** It would knowingly keep the pre-correction CIVB figure and the superseded MNSB figures in 32 bank periods at 7 banks (DI). That contradicts a ruling already in force. The Tag Mapper's worry is valid: Frames cannot validate "latest wins", because it agrees with it by construction (root CLAUDE.md 2026-10-18). The answer is guards 1-4 plus the Verifier opening every one of the 32 periods (section 8), not keeping the superseded value. **Fallback if the slot rule is not built in Stage A: hold the 32 periods blank** with `vintage:unresolved`.

**Out of scope here; for the Period Engineer.** A derived Q4 must not take IE-era 9M facts and an IEO-era FY fact, because derivation is per tag (CR) and a mixed pair is mixed-vintage (RF-04). Count it in the dry-run (section 8, item 6). Growth or TTM across a reclassified period such as MNSB's NII change is **AC-19**.

## 4. D3: the bank metric block (`interest_coverage_ratio`, `net_interest_income`)
**What exists (CR, git log read):** `common/sector_applicability.py`, commits 5b96ff2 and 153574d (decision of 2026-10-19). `interest_coverage_ratio` gets "not applicable to banks" and `net_interest_income` gets "bank net interest income mapping pending". The suppression is applied at serve time in `screener/resolve.py`, `screener/query.py`, `apps/backend/company_page.py` (including peers) and the watchlist router. `metric_value` keeps the stored number. The stock page reads through `apps/backend` (CR). `apps/app/lib/company/db.ts::getLatestMetrics` reads `metric_value` directly but has no caller (CR). `certification/sector.py` checks for leaks (I10).

**Decision.**
1. Stage A is releasable only if (a) the mapping gate and the suppression use the **same** `bank_predicate_sql`, and (b) certify I10 `bank_shows_suppressed_metric` reports 0 on the dry-run output. The Tag Mapper counts 95 newly computable bank coverage-ratio periods at 10 banks and 55 NII periods at 6 banks (DI).
2. **Recommended, not required:** also null `net_interest_income` for banks at compute time, with the same reason. Its bank value is wrong by construction: `InvestmentIncomeInterest`, a securities-only line at FLG, CCB, SFNC and CARV (card), minus total interest expense. A stored wrong number is a trap for any future direct reader, unlike an inapplicable ratio. This changes the 2026-10-19 "metric_value left as written" design, so the Data Chief must agree.
3. **Bank NII definition (later card):** a separate bank-gated concept, provisionally `bank_net_interest_income`, on `us-gaap:InterestIncomeExpenseNet`, the face "Net interest income" (29 of 30 cohort banks FC-TM; RBB, NBBK, MYFW, COLB, HWBK, CIVB and MNSB all file it on the face, FC this run). `InterestRevenueExpenseNet` only per company (ACNB). Not part of Stage A. The non-bank `net_interest_income` formula is never reused for banks.
4. `interest_coverage_ratio` stays "not applicable to banks". There is no bank definition to wait for; a bank has no operating-income line.

## 5. D4: insurer investment income concepts and concept 205
### 5.1 `insurer_net_investment_income` (new; Sector Analyst id `sr.ins.net_investment_income`)
- **Economic definition:** income earned on the insurer's invested assets (debt and equity securities, mortgage loans, real estate, policy loans, cash), **after investment expenses**, **excluding** realized and unrealized investment gains and losses, before income tax. This is the FASB definition of `NetInvestmentIncome`.
- **Tag:** `us-gaap:NetInvestmentIncome`, p1, only tag. **Statement:** income statement (face revenue line at CINF, TRV and PRU; FC-TM; CINF instance fact 1,165M, FC). **Period:** duration. **Unit:** USD only. **Consolidation:** undimensioned. **Sign:** as filed; a negative value is held for review (AS: none seen).
- **Never mapped here:** `InvestmentIncomeNet` (includes realized gains at PGR; differs in 252 of 778 shared periods, DI); `InvestmentIncomeInterest`; `InterestAndDividendIncomeOperating` (PGR's face "Investment income" 3,583M is gross; FC-TM); and `NetInvestmentIncome` at BDCs, where it is a pre-tax operating result (ARCC 1,458M, FC).
- **Gate:** group `insurer`. The interim proxy outside the group file is the Sector Analyst's call. Suggestion (AS): SIC 6311, 6321, 6331, 6351, 6361, 6399 plus an insurer evidence tag such as `PremiumsEarnedNet`, mirroring the bank predicate, **excluding** 6324 managed care and 6411 brokers and agents until the Sector Analyst rules (OSCR, ACT, WTW).
- **Allowed derivations:** none at this level. Q4 = FY - 9M only via the Period Engineer's additive allowlist with same-vintage inputs. Never derived as gross minus expense.
- **Downstream:** none in v1. Whether it enters insurer revenue is AC-11.

### 5.2 `insurer_gross_investment_income` (new)
- **Definition:** the same perimeter as 5.1, **before investment expenses** (FASB `GrossInvestmentIncomeOperating`), usually a note line, not the face.
- **Tag:** `us-gaap:GrossInvestmentIncomeOperating`, p1. Same gate, unit, period and sign policy as 5.1.
- **Relationship:** calculated parent of 5.1: gross = net + `InvestmentIncomeInvestmentExpense` (CINF 1,182M = 1,165M + 17M, FC). This identity is a **check, not a derivation**. It holds in 91% of shared insurer periods (DI); a failing period is flagged for review, and no value is changed.
- **Display:** secondary (note figure); the face figure is 5.1.

### 5.3 Concept 205 `bdc_total_investment_income`: restrict, do not rename
- **The name is right for what it should hold:** ARCC's face "Total investment income" 3,052M is `GrossInvestmentIncomeOperating` (FC, instance f-188). What is wrong is the population: 76 of 118 filers are not BDCs (DI).
- **Why not rename:** a rename would (a) relabel insurer rows instead of retiring them, (b) break `mapper/coverage_matrix.py` (L207, L344, L421, L495 `BDC_FAMILY_DATA_POINTS`), `sanity/plausibility_check.py`, `sanity/yfinance_check.py` and the registry rows (CR), and (c) violate the never-overwrite rule of the definition-versioning spec (doc 49, 0.3).
- **Action:** gate it to group `bdc`, with the Tag Mapper's interim proxy (null SIC plus a BDC marker tag). Only ARCC is FC; the other 41 are DI, so the Sector Analyst must extend the group file. Retire the 2,287 non-BDC rows with lineage; do not move them into 5.2. Re-derive 5.2 from `core.fact` under its own gate, because the insurer gate includes insurers the BDC concept never held.
- **Coverage population:** the `bdc_company` population (118 to 42) must use the same predicate as the gate.
- **Description (PATCH):** correct the text in `mapper/expanded_concepts.py` (~L228 and L418: "118 real companies ... other closed-end funds"); 47 are insurers.
- **New confusable (FC):** ARCC tags its total fund expenses 1,594M with `InvestmentIncomeInvestmentExpense`, so gross - "investment expense" = NII holds at a BDC too, but there it means all expenses including interest and management fees. A BDC's pre-tax NII 1,458M, less tax 43M, gives after-tax 1,415M (`InvestmentIncomeOperatingAfterExpenseAndTax`). A future `bdc_net_investment_income` concept would use the after-tax tag first; the pre-2020 era is open (card section 5). Not defined here.

## 6. D5: what needs the accountant
| Item | Accountant? | Why |
|---|---|---|
| D1 bank total interest expense = face line on IE/IEO; IED excluded | No | Presentation identity (interest income - expense = NII on the same face) and explicit FASB definitions; no judgment about measurement |
| D2 latest-filed for display | No | Already decided 2026-10-18 under delegated authority. CIVB is the filer's own disclosed correction; MNSB keeps the same definition |
| D2 follow-on: growth or TTM spanning a restated or reclassified bank period | **Yes: AC-19** (already on the packet) | Basis mixing in derived figures |
| D2 COLB pre-merger history | No (identity, Gate A) | Entity question, not accounting |
| D3 block | No | Product applicability, delegated 2026-10-19 |
| D3 later bank NII concept | No for the as-presented face line; yes for any NIM or tax-equivalent variant | — |
| D4 insurer net and gross investment income as reported | No | FASB element definitions; FC tie-outs |
| D4 insurer NII inside insurer revenue | **Yes: AC-11** | Revenue composition |
| Stage B non-bank IEO (HTZ operating interest, "net" labels) | **Yes: AC-15** | Interest composition |
No new AC card is needed.

## 7. Acceptance tests (FC inputs; expected outputs after the change)
| # | Case | Source | Expected |
|---|---|---|---|
| T1 | RBB FY2024 | 0001437749-25-008002 R4 | `interest_expense` = **117,297K** from IEO; never 4,800K (IED) |
| T2 | NBBK FY2025 | 0001104659-26-022367 R4 | **138,290K**; never 5,400K |
| T3 | MYFW FY2025 | 0001628280-26-012825 R5 | **84,419K**; never 2,400K |
| T4 | HWBK 6 months to 2024-06-30 and Q2 2024 | 0000893847-24-000016 R4 | **18,688K** and **9,384K**; the 389K / 216K "Loan expense" never appears in interest expense |
| T5 | COLB FY2022 | 0000887343-25-000054 R5 (IEO); 0000887343-24-000089 R5 | **78,001K**; never 8,920K; never 23,645K (legacy Columbia, a different entity) |
| T6 | CIVB FY2022 (vintage) | 0000950170-25-035961 R4 vs 0000950170-23-011581 R4 | **15,951K** (later, error-corrected); 11,049K kept as a non-authoritative lineage copy; or, under the fallback, held with `vintage:unresolved`, **never 11,049K displayed** |
| T7 | MNSB FY2023 and FY2022 (vintage) | 0001437749-25-007641 R4 vs 0001437749-24-008676 R4 | **47,679K** and **13,369K**; same fallback rule |
| T8 | EFSC FY2025 (gain) | 0001025835-26-000058 R5 (FC-TM) | **261,672K**; FY2024 282,955K unchanged |
| T9 | Non-bank invariance | e.g. CMC 0000022444-26-000041, TPG 0001880661-26-000011, AFL 0001628280-26-011402 | **unchanged by Stage A** (they keep today's IED values until Stage B / AC-15; the known non-bank IED defects stay on the Stage B list, they are not silently fixed here) |
| T10 | Bank metric leak | dry-run output | certify I10 `bank_shows_suppressed_metric` = 0; RBB, NBBK, MYFW, HWBK, CIVB show "not applicable to banks" / "bank net interest income mapping pending" |
| T11 | Negative guard (synthetic) | - | a bank IEO fact < 0 gives a held cell with `sign:negative_on_expense_tag`; no fall-through to another tag |
| T12 | Components only (synthetic) | - | a bank with only `InterestExpenseDeposits` and `InterestExpenseBorrowings` gives a blank with `bank:total_interest_expense_not_tagged`, never their sum |
| T13 | CINF FY2025 | 0000020286-26-000008 instance f-141 / f-683 / f-686 | `insurer_net_investment_income` **1,165M**; `insurer_gross_investment_income` **1,182M**; identity 1,182 = 1,165 + 17 passes; `bdc_total_investment_income` **no row** |
| T14 | ARCC FY2025 | 0001287750-26-000006 instance f-188 | `bdc_total_investment_income` **3,052M** kept; no insurer concept row; 1,458M (`NetInvestmentIncome`) appears in no insurer concept |
| T15 | PGR | 0000080661-26-000086 R3 (FC-TM) | `insurer_net_investment_income` = its `NetInvestmentIncome` fact (3,549M, note); never `InvestmentIncomeNet` 4,276M (includes gains) |
| T16 | Negative near-match | any insurer filing `InvestmentIncomeNet` but not `NetInvestmentIncome` | no `insurer_net_investment_income` row |

## 8. Dry-run counts the Data Engineer must produce before any release
All read-only, chunked by company, `statement_timeout` set explicitly, after `ListAgents`. Periods >= 2015-01-01. Split each count into FY, quarter and YTD, and into cohort (shards.csv) vs other.

**Population**
1. Bank population under `bank_predicate_sql`: count, plus a list of companies in the Tag Mapper's 5-SIC proxy or the group file but not in the predicate, and the reverse.

**interest_expense (concepts 10 and 250), banks**
2. Diff for both concepts by type, with companies and periods:
   - insert (IEO gain);
   - replace IED with IE/IEO;
   - delete IED with nothing else (becomes blank with reason): **expected about 56 / 64 rows at 8 / 10 banks today, DI**;
   - vintage pair resolved to the later filing;
   - vintage held;
   - negative held;
   - unchanged.
3. For every vintage pair (expected 32 periods at 7 banks, DI): company, period, both values, both accessions, forms, filing dates, which guard fired. **The Verifier opens all of them**, not a sample, before release.
4. **Non-bank invariance:** 0 changed rows in concepts 10 and 250 for companies outside the predicate.
5. Conflict-fill interaction: bank periods where `interest_expense_resolved` is a conflict fill today, and what it becomes.
6. Derived Q4 interest expense at banks whose FY and 9M inputs come from different tags or filing vintages (must be 0 or held; Period Engineer).
7. Bank `interest_expense` facts < 0 on IE or IEO (expected 0 for IEO).

**Downstream metrics**
8. `metric_value` diff for `interest_coverage_ratio` and `net_interest_income` at banks, plus certify I10 on the post-change state (must be 0). Also `metric_definition_input` proof that no other metric reads concept 10 or 250.
9. Company-page "Interest Expense" cells that change for the 41 cohort banks: before and after, with the source accession.

**Concept 205 and the new insurer concepts**
10. Concept 205: rows removed by SIC family (expected 2,287 at 76 companies) and kept (1,361 at 42); the named list of the 42 for the Sector Analyst.
11. `bdc_company` population before and after (118 to 42), and the coverage_snapshot effect.
12. New insurer concepts: rows and companies per concept, FY vs quarter; identity pass, fail and not-applicable counts; negative values; non-USD units (must be 0 or held); companies in both the BDC and insurer gates (must be 0).

**Replay**
13. Idempotency: a second run gives an empty diff.

## 9. Not tested, open, withdraw conditions
- **Not tested by me:**
  - EFSC, AXP, PGR, TRV and PRU (FC-TM only);
  - the other 5 vintage banks (HTB, TFC, SMBC, BYFC, QNTO) and MS;
  - any bank that files only components;
  - insurers beyond CINF;
  - BDCs beyond ARCC;
  - pre-2021 bank IE values (assumed to be the total from the card's 30-bank check, FC-TM);
  - quarterly vintage pairs (both FC vintage cases are FY);
  - the conflict-fill rows behind the 64 vs 56 difference.
- **Count caveat:** the DI counts in 2.3 use the first source fact only; a multi-source row could be misattributed.
- **Withdraw D1** if a filing shows a bank whose face "Total interest expense" is on IED.
- **Withdraw D2's later-wins default for a period** if the Verifier finds a later IE/IEO bank value that is a context or label error, not a correction or a reclassification. The fallback (hold) then applies to that period. The general ruling is revisited only under its own revisit clause.
- **Withdraw 5.1** if an insurer's undimensioned `NetInvestmentIncome` is a segment subtotal, or if its face NII sits on another tag.

## 10. Routing
- **Verifier:** re-derive T1-T16 from the filings, all vintage periods (section 8 item 3), and 10 gaining banks drawn from the predicate population.
- **Data Engineer:** the mechanism (2.2), the conflict-fill path, the dry-run (section 8), the USD-only gate.
- **Data Chief / Dhairya:**
  - authorize the interim serve-time hide of IED-sourced bank interest-expense cells (2.3);
  - decide the compute-time NII null (D3.2).
- **Sector Analyst:**
  - BDC group extension (40 BDCs);
  - insurer interim predicate;
  - AXP, SOFI, SYF and CBC;
  - managed care and brokers.
- **Period Engineer:** mixed-tag Q4 (section 8 item 6).
- **Gate A identity:** COLB / Umpqua pre-merger history (reverse acquisition closed in Q1 2023; the FY2023 10-K MD&A cites February 28, 2023 for the reverse-merger accounting step; exact close date not read).
