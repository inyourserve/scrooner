# Decision card: total-debt lease perimeter, overlap rules and metric consequences (Standardization Lead, 2026-10-24)

Status: **PROPOSED** (kinds: definition, composition, release precondition). Not verified, not approved; the Standardization Lead cannot approve its own rule. The perimeter choice itself is **AC-1** (accountant, unanswered). This card fixes everything that does not depend on that answer and states the proposed answer. No code, data or migration changed.
Inputs: `VERIFY-TOTAL-DEBT-CARRYING-2026-10-24.md`; PLAN.md "Verifier sample of root fix #1"; ACCOUNTANT-PACKET AC-1, AC-2, AC-3, AC-4; NA-6 (`NA-DEFINITIONS-AND-FOUNDER-SHEET-2026-10-22.md`); wave1 1.4; ledger rows 21, 48, 53; mind entry `composite-concepts-need-slot-level-perimeter-records-not-tag` (helped).
Labels: **FC** = FILING-CHECKED by me this run (R-file and/or XBRL instance opened; locators below). **FC-V** = filing-checked by the Verifier, not re-opened. **CR** = CODE-READ. **AS** = ASSUMED.

## 0. Decisions
| # | Question | Decision (proposed) |
|---|---|---|
| D1 | Displayed total-debt definition | **Carrying amount of borrowings plus finance (capital) lease liabilities, current + noncurrent. Operating leases never.** Built from two stored slots, `borrowings_carrying` and `finance_lease_liabilities`, each with a perimeter record. That way AC-1 can choose (a) exclude or (b) include without a rebuild. Proposed AC-1 answer: (b), matching the packet's own recommendation |
| D2 | Lease-inclusive line plus a separate lease disclosure | Show the lease-inclusive total, labelled "Total debt (includes finance leases)", with both slots visible. Borrowings-only is shown only where the filing's own arithmetic proves combined = borrowings + leases. Never mix perimeters across the current and noncurrent sides |
| D3 | Related-party notes, mezzanine convertibles, current maturities | Related-party notes and bonds are borrowings when the filer's debt note counts them. The temporary-equity "convertible notes" component is never debt. A current line labelled as including current maturities is the whole current side: pair it with the noncurrent line only |
| D4 | Metrics | One perimeter for every consumer (dependency graph, section 4). The coupled D&A and interest choices (AC-6, AC-15) must ship with AC-1. Until AC-1: rows show the composition label; metrics follow section 4.2 |
| D5 | Accountant | AC-1 (perimeter, C2 subtraction, coupling), AC-2 (short-term block), AC-3 (special liabilities), AC-4 (zero), AC-6 / AC-15 (coupled). No new AC card needed |

## 1. What the filings show (FC unless marked)
| Case | Accession, locator | Face lines (tag) | Lease facts | Borrowings carrying | Incl. finance leases |
|---|---|---|---|---|---|
| MU 2025-08-28 | 10-K 0000723125-25-000028 R5; instance `mu-20250828_htm.xml` | "Current debt" 560 (`DebtCurrent`); "Long-term debt" 14,017 (`LongTermDebtAndCapitalLeaseObligations`) | `FinanceLeaseLiabilityCurrent` 560, `...Noncurrent` 2,484 (total 3,044). The ASC 842 location list puts them inside `DebtCurrent` and `LongTermDebtAndCapitalLeaseObligations` | **11,533M** (`LongTermDebt`; the current side is all leases: 560 = 560) | **14,577M** |
| TSLA 2017-06-30 | 10-Q 0001564590-17-015705 R2, R60, instance `tsla-20170630.xml` | current "debt and capital leases" 716,533 (`LongTermDebtAndCapitalLeaseObligationsCurrent`); current related-party "solar bonds and promissory notes" 100,000 (`DueToRelatedPartiesCurrent`); noncurrent "debt and capital leases" 7,122,862; "Convertible senior notes issued to related parties" 2,444 (custom); mezzanine "Convertible senior notes" 1,688 (`TemporaryEquityCarryingAmountAttributableToParent`) | none tagged; leases are implied by difference | **7,515,847K** = R60 "Net Carrying Value" current 760,284 (includes the 100,000 related-party note) + long-term 6,755,563 | **7,941,839K** (face sum, FC-V and FC); capital leases = 425,992K by difference (arithmetic from the filing; the lease note itself was not opened) |
| TSLA 2017-09-30 | 10-Q 0001564590-17-021343 R2 | 324,224 + 100,000 + 9,581,616 + 2,481 | - | not opened (R60 of this filing still to read) | **10,008,321K** |
| GOOG 2023-12-31 | 10-K 0001652044-24-000022 R3, **R64** | "Long-term debt" 13,253 (`LongTermDebtAndCapitalLeaseObligations`); current notes and current leases inside "Accrued expenses and other current liabilities" | R64: notes 13,000 + "Future finance lease payments, net and other" 1,746 (`FinanceLeaseLiability`) = filer's **"Total debt" 14,746, before** unamortized discount (130); less current notes 1,000 and current leases 363 gives 13,253 | **12,870M** (13,000 - 130) | **14,616M** |
| GOOG 2025-12-31 | 10-K 0001652044-26-000018 R3; instance | "Long-term debt" 46,547 (`LongTermDebtNoncurrent`); current 1,996 (`LongTermDebtCurrent`, inside accrued) | `FinanceLeaseLiability` 2,500 = 441 (in accrued) + 2,059 (in `OtherLiabilitiesNoncurrent`), per the location list | **48,543M** (FC-V; facts FC) | **51,043M** |
| AMZN 2025-12-31 | 10-K 0001018724-26-000004 R7; instance | "Long-term debt" 65,648 (`LongTermDebtNoncurrent`); current 2,748 and short-term 455 inside accrued (facts); "Long-term lease liabilities" 87,339 (custom `amzn_LeaseLiabilityNoncurrent`) = operating 76,597 + finance 10,742 | `FinanceLeaseLiability` 12,286 = 1,544 (accrued) + 10,742 (the custom lease line) | **68,851M** | **81,137M** |
| LLY 2014-03-31 | 10-Q 0000059478-14-000102 R4 | "Short-term borrowings and current maturities of long-term debt" 9.1 (`DebtCurrent`); "Long-term debt" 5,255.3 (`LongTermDebtNoncurrent`) | lease perimeter not checked (AS: pre-ASC 842; the note was not opened) | **5,264.4M** | unknown (perimeter `unverified`) |
| CVX 2016-12-31 | 10-K 0000093410-17-000013 R5, R98, R100 | "Short-term debt" 10,840 (`ShortTermBorrowings`; R98: subtotal `DebtCurrent` 19,840, which includes current maturities 6,253 and current capital leases 14, less 9,000 reclassified to long-term); "Long-term debt" 35,193 (`LongTermDebtNoncurrent`; R100 includes the 9,000); "Capital lease obligations" 93 (`CapitalLeaseObligationsNoncurrent`) | 14 current (inside short-term debt) + 93 noncurrent | **46,019M** (10,840 + 35,193 - 14) | **46,126M** |

Values that are **not** total debt, though they look like it:
- GOOG "Total debt" 14,746 (gross of discount; it was the stored before-value).
- GOOG `LongTermDebt` 49,085 and AMZN `LongTermDebt` 68,836 (principal / face value, ledger row 48).
- TSLA `DebtInstrumentCarryingAmount` 8,104,869, which TSLA labels "Unpaid Principal Balance".
- AMZN's lease line 87,339 (includes operating leases).
- CVX `DebtCurrent` 19,840 (before the refinancing reclass; NA-6 already records the 55,033M overcount).

## 2. D1 and D2: definition and construction
**Concept contract `total_debt_resolved` (ID unchanged, version bump MINOR under DEFINITION-VERSIONING-SPEC)**
- **Economic definition:** obligations for borrowed money at the balance-sheet instant, at carrying amount (net of unamortized discount, premium and issuance costs): bonds, notes (including related-party notes, and the liability component of convertibles), loans, commercial paper, other short-term borrowings, current maturities. Plus finance (capital) lease liabilities.
- **Excluded:**
  - operating lease liabilities (wave1 1.4);
  - temporary-equity components of convertibles;
  - accrued interest;
  - trade and other payables;
  - deposits (banks: not in template; `BANK_BORROWINGS_PENDING`, CR);
  - AC-3 items until ruled.
- **Statement:** balance sheet, instant, undimensioned (member-summed only per ledger row 60), USD only.
- **Sign:** non-negative; a negative value is held.

**Slots, each with a perimeter record per company-instant (accession, lines used, rule id)**
1. `borrowings_carrying`.
2. `finance_lease_liabilities`.

Total = 1 + 2. Each slot is filled only by addition of filed lines or facts; no slot is filled by subtraction except under rule C2 below.

**Construction by filer shape**
- **A. Lease-inclusive face lines (MU, TSLA 2017, GOOG 2023 noncurrent):**
  - Total = the sum of the face debt lines on one perimeter.
  - Slot 2 = the lease facts the location list or note places inside those lines.
  - Slot 1 = total - slot 2 only where the filing's own arithmetic shows it: GOOG R64 roll, MU 14,017 = 11,533 + 2,484, TSLA R60 note totals. That is AC-1's sub-question **C2**, proposed "yes, only if the filing shows the identity".
- **B. Leases on separate lines (GOOG 2025, AMZN, CVX 2016 noncurrent):**
  - Slot 1 = face debt lines plus filed current-debt facts.
  - Slot 2 = `FinanceLeaseLiability` current + noncurrent (or pre-842 capital-lease lines), added **only** when the ASC 842 location list (`FinanceLeaseLiability{Current,Noncurrent}StatementOfFinancialPositionExtensibleList`) or the face shows they are outside the debt lines used. If the location is unknown, slot 2 = `unverified` and the total is held (`debt:lease_location_unknown`); it is never added blind.
- **C. Mixed perimeter on one side** (TSLA's debt-only `DebtCurrent` plus a lease-inclusive noncurrent line; GOOG 2023 noncurrent with leases next to a current-notes-only fact): **never sum across perimeters.** This is the Verifier's TSLA 2017 failure. Retire the "DebtCurrent at or above the parts is accepted" path.
- **Display wording:**
  - "Total debt (includes finance leases)", with a details line "Borrowings $X; finance leases $Y (source accession)".
  - If slot 2 is `unverified` (pre-842 filers with no lease fact, e.g. LLY 2014): "Total debt (finance leases not determined)". This is shown only under the interim of 4.2, and never enters a cross-company screen.
- **Series:** build by slots every period, never by copying a face line. GOOG's face perimeter changed between FY2023 and FY2025; its slot series does not.

## 3. D3: related-party, convertible and overlap rules
1. **Related-party borrowings are borrowings.** Include a related-party line only when the filer's debt note counts it in its debt totals (TSLA R60: the 100,000 "Related Party Promissory Notes" are inside `DebtCurrent` 760,284; the 2,444 related-party convertibles are a face noncurrent debt line). Never include by tag alone: `DueToRelatedPartiesCurrent` is a generic payables tag.
2. **Convertible notes:** the liability component is debt. A temporary-equity "convertible senior notes" amount (TSLA 1,688K) is equity and is excluded.
3. **Current maturities:** a current line whose label or note says it includes current maturities is the whole current side. LLY "Short-term borrowings and current maturities"; CVX "Short-term debt" per R98, which includes 6,253 of current maturities and 14 of current capital leases.
   - Pair it with the **noncurrent** line (`LongTermDebtNoncurrent` or a lease-combined noncurrent line), never with a `LongTermDebt` total that may include current maturities.
   - Never add `LongTermDebtCurrent` on top.
4. **Refinancing reclass:** if `ShortTermDebtRefinancedAmount` is filed, use the face current line, never the pre-reclass `DebtCurrent` subtotal (CVX; NA-6 sub-rule 5).
5. **LLY 2014-03-31 false hold:** `DebtCurrent` + `LongTermDebtNoncurrent` from the same face are disjoint by label. The overlap test must not fire; expected 5,264.4M.

## 4. D4: consequences for consuming metrics
### 4.1 Dependency graph
Source: `data-team/strategy/tools/s1_cascade/graph_def.py`, CR. `total_debt_resolved` feeds `debt_to_equity` (L45), `net_cash` (L61), `net_cash_per_share` (L62), `net_debt_ebitda` (L80), `debt_to_ebitda` (L81), `ev_ebitda` (L89), `ev_sales` (L90), `roic` invested capital (L42), `piotroski_f_score` (L103) and `zero_debt` (L105), plus the statement row "Total Debt" (suppressed for banks, CR).

| Metric | Effect of including finance leases | Coupling that must ship with AC-1 |
|---|---|---|
| debt_to_equity, net_cash, net_cash_per_share, roic (invested capital) | higher debt, lower net cash; MU +26% vs borrowings-only, GOOG 2025 +5%, AMZN +18%, TSLA 2017 +6% (FC numbers above) | none beyond one perimeter for every company |
| ev_sales | higher EV | none |
| ev_ebitda, net_debt_ebitda, debt_to_ebitda | lease debt in the numerator | **AC-6:** finance-lease right-of-use amortization must be inside the D&A slot of EBITDA (otherwise lease cost is deducted from EBITDA and the lease is also counted as debt). The D&A slot record must state it per company (AS: not measured) |
| interest coverage (not a consumer of total debt, but on the same perimeter) | - | **AC-15:** finance-lease interest in interest expense |
| FCF family | - | **AC-5 / AC-20:** whether lease principal payments reduce FCF |
| zero_debt | a company with finance leases only is not zero-debt | **AC-4:** zero only with filing evidence; under (b) a company with leases only is never "zero debt" |
| piotroski_f_score (leverage change) | needs the same perimeter in t and t-1 | slot build guarantees it |

### 4.2 Until AC-1 is answered
- **Rows:** the "Total Debt" statement row may show the corrected carrying build with its composition label (as AC-1 itself recommends: "show the composition path"). This is sourced presentation, not a definition.
- **Metrics:** the ten metrics above need one cross-company perimeter, and plan 49 lists them as blocked on AC-1.
  - The stored values are wrong today in 37 of 37 checked cells (FC-V), so leaving them up is not an option under the correctness standard.
  - Proposal to Dhairya (release-policy owner, delegated): either (i) publish on the lease-inclusive perimeter with the label "definition pending accountant review", or (ii) hide with that reason.
  - Mixing perimeters by company (today's AC-1 option (c)) is rejected for metrics.

## 5. D5: accountant
| Part | Card | Needed? |
|---|---|---|
| Include vs exclude finance leases; C2 subtraction; coupled interest, D&A and FCF | **AC-1** (with AC-5, AC-6 in the same sitting; AC-15 for interest) | yes |
| Short-term block, current maturities, building from parts | **AC-2** (rules 3.3-3.5 are AC-2's option (a) and tie to filed totals; rule 3.4 is already NA-6) | yes for AC-2 itself; 3.3-3.5 are filing arithmetic |
| Related-party notes in debt; temporary-equity convertibles out | none: liabilities for borrowed money vs equity classification as presented | no |
| Mandatorily redeemable preferred, vehicle and captive-finance debt | **AC-3** | yes (unchanged) |
| When debt is zero | **AC-4** | yes (unchanged) |
| Operating leases never | already decided (wave1 1.4; AC-1 states it under every option) | no |
| Carrying vs face value | none (ledger row 48; filer arithmetic) | no |

## 6. Acceptance tests (FC inputs)
| # | Case | Expected borrowings | Expected incl. finance leases | Must never show |
|---|---|---|---|---|
| T1 | MU 2025-08-28, 0000723125-25-000028 | 11,533M | **14,577M** (both lines carry leases; the location list proves it) | 11,533 + 560 (the current side is leases) |
| T2 | MU other 19 instants (FC-V sums) | from slots | = face current + noncurrent (e.g. 2026-09-03: 491 + 4,688) | - |
| T3 | TSLA 2017-06-30, 0001564590-17-015705 | **7,515,847K** (R60) | **7,941,839K** | 7,883,146K (the mixed-perimeter new value); any figure without the 2,444 related-party line; 1,688 mezzanine |
| T4 | TSLA 2017-09-30, 0001564590-17-021343 | read from that filing's R60 before release (NOT CHECKED) | **10,008,321K** | 9,957,122K |
| T5 | GOOG 2023-12-31, 0001652044-24-000022 R64 | **12,870M** | **14,616M** | 14,746 (gross of discount); 14,253 (13,253 + 1,000: mixed perimeter) |
| T6 | GOOG 2025-12-31, 0001652044-26-000018 | **48,543M** | **51,043M** (2,500 from accrued and other noncurrent liabilities per the location list) | 49,085 (principal) |
| T7 | AMZN 2025-12-31, 0001018724-26-000004 | **68,851M** | **81,137M** | 87,339 or any figure including operating leases; 68,836 (principal) |
| T8 | LLY 2014-03-31, 0000059478-14-000102 R4 | **5,264.4M**; no overlap hold | held as `unverified` until the lease note is read | blank with "composition undecidable" |
| T9 | CVX 2016-12-31, 0000093410-17-000013 R5/R98/R100 | **46,019M** | **46,126M** | 55,033 (`DebtCurrent` + LTD noncurrent); 52,286 (+ `LongTermDebtCurrent` 6,253 on top of short-term debt) |
| T10 | Synthetic | a filer with finance-lease facts but no location list and no face line gives the total held `debt:lease_location_unknown` | | |
| T11 | Bank (any in `bank_predicate_sql`) | row and metrics stay suppressed | | |

## 7. Required before release (Data Engineer, lane 3; dry-run first)
1. Rebuild with the two slots and rules 2A-2C and 3.1-3.5. Remove the "DebtCurrent at or above the parts" path. Re-run the Verifier's 46 cells plus T1-T9.
2. **Dry-run counts:** instants by filer shape (A/B/C); slot-2 location source (location list / face / note / unverified); C2 subtractions used; holds by reason; cohort companies whose total changes by more than 5% between perimeters.
3. Persist the perimeter record and the hold reason to the cell (NA-6 release condition: today `resolve_total_debt_components` drops it, CR via NA-6).
4. A lease-perimeter stratum in the Verifier's fresh sample.

## 8. Not tested
- LLY's and TSLA 2017-09-30's lease amounts.
- Pre-2019 filers' capital-lease locations in general.
- How often the ASC 842 location list is filed (population not measured).
- Whether each company's D&A slot includes finance-lease amortization (AC-6 coupling).
- AMZN and GOOG interim instants.
- Combined or segment-only debt presenters (ledger row 60).
- Any non-USD filer.
