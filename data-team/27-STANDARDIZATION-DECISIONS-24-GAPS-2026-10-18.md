# Standardization decisions on the 24 filing-checked gap blanks (2026-10-18)

Role: Standardization Lead (11). Objective: decide policy for the five rule families the Verifier's file 26 raised. Scope: the 24 OUR_GAP rows (13 companies) in `26-VERIFIER-24-GAP-BLANKS-2026-10-18.md`, read together with `24-STUDY-STANDARDIZATION-RESEARCH-AND-CASES.md`. Authorized: read-only research, code reading, writing this file. **No database use; nothing was mapped, coded, seeded or run against the database.** No accounting reviewer is named, so every decision that changes a perimeter, adds a formula or combines tags is **PROPOSAL-ONLY**. Only a single clean standard tag that is an exact match to the definition can be **ELIGIBLE**, under the release tier in `doc/data-moat/team/PLAN.md` ("Auto-eligible after checks"). ELIGIBLE means "may go to the Tag Mapper's checks". It is not approval and not publication. I cannot approve my own rule; the Verifier reviews this file next.

Evidence labels: **FILING-CHECKED** = original SEC filing content with locator (either opened by me, marked "me", or by the Verifier in file 26, marked "V26"). **CODE-READ** = what our code does today (not financial evidence). **DATA-INFERRED** = from our tables or docs, no filing opened. **ASSUMED** = reasoning without evidence.

New filing evidence opened for this file (me; cached R-file bytes the Verifier fetched in this session, rendered by SEC; content sha256 prefix in brackets):
- CDNL 10-K 0001193125-26-120014 **R60** "Summary of Notes payable" [c4d8f57a7aceeefd] and R63 [c0ddde40068b7845]; CDNL 10-Q 0001193125-26-345109 R4 [c0614d86bdb89f8c]; HTZ 10-K 0001657853-26-000008 R7 [7678caf0c16d2a83]; UNIT 10-K 0001628280-26-013196 R84 [3d1bae11301fb6b6]; FRD 10-Q 0001437749-26-026305 R2 [0296f5afcb8876bc]; EG 10-Q 0001095073-26-000032 R2 [b8688bf22f423e1f]. The us-gaap element definitions quoted below were read from the `defref_us-gaap_*` definition blocks embedded in these R-files.
- 17 CFR 210.5-03 (Reg S-X income-statement captions), read at https://www.law.cornell.edu/cfr/text/17/210.5-03 (eCFR redirected to a bot check).

---

## Decision 1. Operating income where the income statement has no operating subtotal (CVX, AJG, HTZ)

**Decision: leave `operating_income` blank for these issuer-periods, with the reason "Operating income is not reported as a subtotal by this company (single-step income statement)". Do not derive it. Status: PROPOSAL-ONLY** (a new reason assignment and a refusal to derive; no number is published). Reason code: `NOT_SEPARATELY_DISCLOSED`; no new code needed.

Why no rule is defensible:
- Reg S-X 5-03 has no "operating income" caption. Its order is 1 net sales, 2 cost of sales, 3 other operating costs, 4 SG&A, 5 provision for doubtful accounts, 6 other general expenses, 7 non-operating income, 8 interest and amortization of debt discount, 9 non-operating expenses, 10 income before income tax (FILING-CHECKED rule text, me). A single-step statement that totals 2-9 as "costs and expenses" is permitted, so the subtotal does not exist in these filings.
- Revenues - CostsAndExpenses = pretax income for all three (FILING-CHECKED, V26: CVX 19,743; AJG 1,871; HTZ -830 $M). Rejected, as the Verifier found.
- Adding interest back is still a choice we would be making for the filer. On V26's filing numbers: CVX 189,031 - (169,288 - 1,217) = 20,960, but CVX's Revenues also contain equity-affiliate income 3,000 and `cvx_NonoperatingIncome` 1,599, and yfinance's component sum is 16,674. AJG 13,942 - (12,071 - 639) = 2,510 vs 2,556. HTZ 8,504 - (9,334 - 1,077) = 247 vs 14; HTZ's costs also contain gains on asset sales, a legal settlement, a bankruptcy litigation reserve and warrant fair-value changes, and 608 of its 1,077 interest is vehicle interest, which is arguably operating for a rental company (HTZ tags it `InterestExpenseOperating`, R7, me). Every candidate formula needs a line-by-line operating/non-operating classification the filer did not make. That is accounting judgement: there is no deterministic answer to verify.
- A component sum (yfinance's method) needs the same per-line classification, and some lines carry custom tags.

When the reason may be displayed (evidence required): only when, for that filing, the rendered income statement shows no operating-income caption: either `analytics.company_filing_line_evidence` = `line_not_presented_in_filing` for that accession or a Verifier R-file check. Our not having an `OperatingIncomeLoss` fact is not enough (a custom-tag subtotal is possible; "not in the XBRL is not not in the filing", 21 §6). Without that evidence, the cell shows the generic "not available in our data" reason.

Downstream: `operating_margin`, the TTM OI numerator of `roic` and the numerator of `interest_coverage` stay blank with the same reason for these issuer-periods (rows 2, 3, 7, 10, 11, 14, 17).

Optional separate proposal (not a fix to `operating_income`; PROPOSAL-ONLY; do not build without a reviewer): a distinct concept `ebit_pretax_plus_interest` = `income_before_tax` + `interest_expense` (gross, expensed, approved tags only), labelled "derived: pretax income plus interest expense". It would feed only an explicitly separate "interest coverage (EBIT basis)" metric. It is never written into `operating_income_resolved` and never mixed into `operating_margin`. It must not apply to:
- banks, thrifts and other credit institutions (SIC 6000-6199), broker-dealers (62xx), or insurers and insurance brokers (63xx-64xx), where interest is an operating item;
- any issuer-period that files `InterestExpenseOperating` (rental, leasing and captive-finance shapes such as HTZ);
- any issuer-period whose pretax income is not under an approved `income_before_tax` tag. HTZ tags pretax as `IncomeLossAttributableToParent` (V26 note 6), so HTZ is out until that is resolved.
It would still include gains, settlements and other non-operating items, which is why it gets its own name.

Reject outright: any rule built on CostsAndExpenses, for OI or for opex. The 2026-09-08 learnings note (`doc/learnings/2026-09-08-yfinance-financials-system.md` line 45) recommends "CostsAndExpenses - cost_of_revenue" as an `operating_expenses` recovery for 682 companies. CVX, AJG and HTZ show that this would put interest (and other non-operating items) into opex. **Do not build it.** (DATA-INFERRED that the note is still open; FILING-CHECKED that the formula is wrong for these three.)

## Decision 2. Is SG&A an operating expense in the existing OI derivation (DHI, BBW)?

**Decision: yes, SG&A is an operating expense. But SG&A must not be fed into `operating_expenses_resolved`, because SG&A is a component of operating expenses, not the total. The only defensible use is a separately gated formula, OI = revenue - cost_of_revenue - SG&A, used only when SG&A is the only operating-expense line presented. Status: PROPOSAL-ONLY** (a new formula and a statement-shape condition).

Evidence:
- FILING-CHECKED (V26): DHI statement of operations (R4), 10-K FY ending 2025-09-30 (balance sheet acc 0000882184-25-000081): no OI line and no CostsAndExpenses; 34,250.4 - 26,134.2 - 3,692.0 = 4,424.2 $M. BBW statement of operations (R4), original 10-K acc 0001437749-26-012501 (the 10-K/A 0001437749-26-012597 has no financial R-files): 529,832 - 234,203 - 229,203 = 66,426 $K, then net interest **income** 801 gives pretax 67,227.
- FILING-CHECKED rule text (me): Reg S-X 5-03 item 4 (SG&A) sits inside the operating block (items 1-6) and before non-operating items 7-9. So SG&A is operating. Captions 3, 5 and 6 are also operating, which is why the formula is only valid when they are absent.
- CODE-READ: `resolve_operating_income_arithmetic_fallback` (`mapper/conflict_resolution.py` line 676) needs `operating_expenses_resolved`. That concept comes from `operating_expenses` (CostsAndExpenses rejected, concept_mapping id 272, 2026-09-08) or from gross_profit - operating_income (`concept_fallback.py` ARITHMETIC_FALLBACKS), which cannot fire when OI is the missing value. So DHI and BBW get nothing today.

Why not just map SG&A into opex: for any company that also has R&D, D&A, impairments, restructuring or other operating lines, but no OperatingExpenses total, opex would be understated and OI overstated. That is the "component as total" error the role spec forbids.

Proposed rule `oi_from_sga_only_statement` (for review):
- Fires only when all of these hold for the company-period: no `OperatingIncomeLoss` fact (authoritative or not); no `OperatingExpenses` or `CostsAndExpenses`; `revenue_sanity_resolved` > 0; `cost_of_revenue_resolved` present (or a reviewed confirmation that the statement has no cost-of-sales line); `sga_expense` present; and no authoritative undimensioned fact for any operating-expense-family tag other than SG&A. The Tag Mapper enumerates that family from `sec_tag_library`; at minimum R&D, D&A, amortization of intangibles, impairment, restructuring, `OtherOperatingIncomeExpenseNet`, `OtherCostAndExpenseOperating`, gain/loss on asset sales, provision for doubtful accounts, and the separate selling and G&A components.
- XBRL absence of other lines is not proof (custom tags). The latest filing must also show `company_filing_line_evidence` with no other operating line, or pass a Verifier face check. Periods older than the filing-line evidence stay blank until checked.
- Excluded: SIC 6000-6199, 62xx, 63xx-64xx, 6798, and any period that files `InterestExpenseOperating`.
- Control-group acceptance (query Q-D2 below): on companies that DO tag `OperatingIncomeLoss` and meet the same shape conditions, the formula must equal the filed OI exactly (difference no larger than the filed rounding). Every mismatch must be explained by a face line and turned into an exclusion condition; otherwise the rule is rejected. A percentage-within-tolerance figure is not acceptance.

**Defect routed (DATA-INFERRED from the code's own docstring, measured 2026-09-13, not remeasured):** the existing arithmetic fallback reports that only 90.3% (with cost of revenue) and 85.5% (without) of control-group periods land within 2% of the filer's real OI. Its rationale is that "an imperfect ~10-15% of fills still replace an empty cell". Under the 2026-10-18 correctness standard, a value that is up to 15% likely to be materially off is a wrong-value class, not an acceptable fill. It also excludes only SIC 602/603/606, not other credit institutions, insurers or broker-dealers (HOOD 6211 was its motivating case). **Route to the Data Chief and the Verifier:** re-measure the control group, find the conditions that separate exact from inexact fills, and suppress inexact shapes. Do not extend this fallback with SG&A until that is done. The SG&A rule above should be a separate code path with its own exactness gate.

## Decision 3. Zero borrowings (CATO, ATEX) and the lease perimeter of `total_debt`

**Decision: distinguish three evidence states. Only the first two may display 0. Status: PROPOSAL-ONLY** for E2 and E3. E1 is existing behaviour (a reported numeric zero is preserved) and needs no new approval, but it needs an audit, listed below.

| State | Filing evidence required (per balance-sheet date, never carried to another date) | Display |
|---|---|---|
| E1 reported zero | An authoritative, undimensioned fact on a **total** debt tag (`DebtLongtermAndShorttermCombinedAmount`) equal to 0, or zeros on every debt-family tag present with no nonzero debt-family fact at that instant | `total_debt` = 0, value_status reported |
| E2 filing states none | The filing's text for that date says no borrowings are outstanding (CATO: Note 8, R15, "There were no borrowings outstanding"; R58 `LineOfCredit` = 0 under the ABL Credit Agreement member; acc 0001562762-26-000041, FY ending 2026-01-31; FILING-CHECKED V26), **and** the face balance sheet (R3) has no borrowing line. Recorded as a `company_data_finding` with accession and locator | `total_debt` = 0 with provenance "filing states no borrowings outstanding" (proposal) |
| E3 nothing shown | No debt line on the face and no debt note (ATEX: BS R3, acc 0001304492-26-000027, FY ending 2026-03-31; FILING-CHECKED V26) | **Blank** with the reason "No borrowings reported in the filing". Never 0 by default |

Points for the reviewer:
- A zero on an instrument tag (for example an undrawn revolver, `LineOfCredit` = 0) does not prove total debt is zero; the company can have a term loan under another tag. That is why E1 requires a total tag or zeros on every family tag present, and why CATO needs E2 (its zero is dimensional, under the ABL member, and is not in companyfacts anyway).
- E3 could become a zero rule only with a stricter face test: the face liability lines sum to total liabilities, none is a borrowing, none is a catch-all ("other liabilities", "accrued and other") that could hold debt, and there is no debt note. ATEX has not been checked for catch-all lines, so it stays E3.
- With `total_debt` = 0: D/E = 0, and ROIC invested capital = equity. `interest_coverage` with zero interest expense must show "not meaningful (no interest expense)", never infinity or a huge ratio. Check the existing materiality floor on `interest_expense` covers this.
- **E1 audit (CODE-READ):** `compute_total_debt` sums whichever component tags exist, so a filer with `LongTermDebt` = 0 and short-term debt under an unmapped or custom tag gets a wrong 0 through path `ltd_incl_current+short_term`. The Verifier should sample `total_debt_resolved` = 0 rows by path (query Q-D3b).

**Lease perimeter, today (CODE-READ, `mapper/concept_fallback.py` lines 58-103 and 310-403):**
- **Operating lease liabilities are not counted as debt.** No `OperatingLease*` tag is in `TOTAL_DEBT_TAGS`. This matches the Wave 1 proposal ("Lease liabilities are NOT debt under any current metric", `doc/data-moat/wave1-canonical-definitions.md` §1.3-1.4). It is also why yfinance "Total Debt" disagrees for CATO (150,448K = op-lease current 53,507 + noncurrent 96,941) and ATEX (4,419K) (FILING-CHECKED V26). yfinance total-debt comparisons for lessees are therefore systematically non-comparable, and must not be read as our gaps.
- **Finance leases are counted inconsistently.** They are included when the filer combines them with debt in one tag (`DebtAndCapitalLeaseObligations`, and the `LongTermDebtAndCapitalLeaseObligations*` alternates). They are excluded when reported separately (`FinanceLeaseLiability*` is not in the list; CDNL's 3,349,359 + 4,974,309 is excluded). The same economic item is in or out depending on tagging. **Open perimeter question for the accountant.** Options: (A) exclude everywhere, which requires subtracting a component from a combined line and is blocked without composition evidence; (B) include everywhere, adding separate `FinanceLeaseLiability*` only when not already inside a combined tag, which carries double-count risk; (C, interim proposal) keep today's behaviour but store and show each value's composition path ("includes finance leases" when a lease-combined tag was used). The `path` is computed in `compute_total_debt` but only counted in logs, not stored. Recommended interim: C.
- Custom combined lease tags (FRD `frd_OperatingAndFinanceLeaseLiabilitiesNoncurrent` 4,097) must never enter debt (FILING-CHECKED V26).

## Decision 4. Net-interest-only filers (VVX, UNIT): can interest coverage use a net interest tag?

**Decision: No, not as a global mapping. Status: the "no" keeps today's approved behaviour (`concepts.py` lines 258-259 exclude net tags), so it needs no new approval. A company-scoped exception is PROPOSAL-ONLY.**
- Definition (FILING-CHECKED, me, UNIT R84 defref): `InterestIncomeExpenseNonoperatingNet` = "Amount of interest income (expense) classified as nonoperating". It is net by definition and its sign flips between filers.
- Counterexample (FILING-CHECKED, V26): BBW uses the same tag for net interest **income** of 801 $K (added to OI to reach pretax). Mapped globally, it would give BBW a meaningless or negative interest coverage, and it would overstate coverage for every filer that nets real interest income.
- UNIT: R84 builds "Total interest expense, net" 602.8 $M only from expense-side items (per-instrument interest, amortization 14.3, accretion 1.7, capitalized interest (9.7), other 2.4), with no interest-income component shown. That holds for FY2025 only. VVX: no composition is shown; R68's `InterestExpense` facts are per-instrument, not a total (V26).
- Consequence of "no": VVX and UNIT `interest_coverage` stays blank with the reason "Only net interest is reported; gross interest expense is not separately disclosed" (`NOT_SEPARATELY_DISCLOSED`). The same applies to every net-only filer.
- Possible company-scoped exception (PROPOSAL-ONLY): a per-company, per-period `company_tag_preference` for UNIT. It needs, for each period, an R-file showing that the net figure has no interest-income component, plus a sign check (expense must be stored as the expense magnitude). VVX is not eligible without such a note. The preference expires when a later filing changes the composition.
- Related (not in the five, FILING-CHECKED V26): DHI capitalizes interest (incurred 241.7 $M, 158.1 charged to cost of sales). `InterestCostsIncurred` is not interest expense and must not be mapped to `interest_expense`, the same hard rule as `InterestPaidNet`. DHI coverage stays blank: "interest is capitalized into inventory; no interest expense is presented".

## Decision 5. Candidate tags: concept, status, required checks, withdrawal

Element definitions (FILING-CHECKED, me, from the defref blocks in the R-files listed at the top):
- `NotesPayable`: "Including the current and noncurrent portions, aggregate carrying amount of all types of notes payable ... with initial maturities beyond one year".
- `NotesPayableCurrent`: "portions of long-term notes payable due within one year".
- `LongTermNotesPayable`: "notes payable (with maturities initially due after one year ...), **excluding current portion**".
- `LongTermLineOfCredit`: "the **noncurrent portion** of long-term obligations drawn from a line of credit".
- `SeniorNotes` and `SubordinatedDebt`: "Including the current and noncurrent portions".
- `AdvancesFromFederalHomeLoanBanks`: "borrowings ... from the Federal Home Loan Bank".
- `InterestExpenseNonoperating`: "interest expense classified as nonoperating" (companion: `InterestExpenseOperating`, "classified as operating").
- `Cash`: "currency on hand as well as demand deposits ...", which excludes cash equivalents.

**New filing-checked counterexample (me, CDNL 10-K 0001193125-26-120014 R60, 2025-12-31):** undimensioned `NotesPayable` "Total Notes Payable" 121,178,878 coexists with its own components: `NotesPayableCurrent` 6,128,674, `UnamortizedDebtIssuanceExpense` 1,897,340 and `LongTermNotesPayable` 113,152,864 (121,178,878 - 6,128,674 - 1,897,340 = 113,152,864 exactly). So `NotesPayable` can be a **gross note-schedule total** while the split pair is the **net face carrying value**. Adding all three would double count. Taking `NotesPayable` over the pair would overstate the face value by the issuance costs. Precedence must be: face split pair > `NotesPayable`. R63 also shows `NotesPayable` per instrument under dimension members; those facts are not in companyfacts, but they confirm the tag is used at both total and instrument level.

`total_debt` tags are not `concept_mapping` rows. They are hard-coded role tuples in `compute_total_debt` (CODE-READ). Adding one is a code change plus a total-debt reprocess, with a dry-run diff reviewed before the live write. `interest_expense` and `cash_and_equivalents` changes are `concept_mapping` rows via a committed migration.

**Two rule families for debt.** (F1) **Sole-instrument last resort**: a candidate tag supplies `total_debt_resolved` only when it is the only debt-family fact at that instant, and only for instrument tags whose definition includes both current and noncurrent portions (`NotesPayable`, `SeniorNotes`, `SubordinatedDebt`). It is reached only after every existing path returns None, the same structure as the `ConvertibleLongTermNotesPayable` last resort (dc9fa96). It never adds to or replaces an existing value. Noncurrent-only tags (`LongTermLineOfCredit`, `LongTermNotesPayable`) are excluded from F1: when one stands alone the current portion may simply sit under a tag we do not see. (F2) **Multi-component sums**: any total built by adding two or more candidate tags.

I read F1 as "single clean standard tag, exact definitional match within the existing perimeter". If the Chief reads PLAN's "fallbacks across tags" as covering F1, every ELIGIBLE debt row below reverts to PROPOSAL-ONLY. That reading is the Chief's call, not mine.

| Tag | Concept / role | Status | Cells it would fill | Why |
|---|---|---|---|---|
| `NotesPayable` (DHI) | `total_debt_resolved`, F1 | **ELIGIBLE (F1 only)** | DHI D/E (row 22) for the latest dates; DHI ROIC stays blank for OI (Decision 2) | Includes current and noncurrent; DHI's single face debt line (5,965.5 at 2025-09-30, R2 acc 0000882184-25-000081; 7,112.6 at 2026-06-30, acc 0000882184-26-000096) (V26). The CDNL R60 case shows it is excluded from F1 whenever its components are present |
| `NotesPayableCurrent` (CDNL) | `total_debt_resolved`, current portion of long-term notes (alternate in `DEBT_LTD_CURRENT`) | **PROPOSAL-ONLY** (F2 pair) | CDNL D/E and ROIC debt input (rows 5, 23) only together with the next tag | Needs a two-tag sum and a precedence rule over `NotesPayable` (gross vs net basis) |
| `LongTermNotesPayable` (CDNL, FRD) | `total_debt_resolved`, noncurrent notes (alternate in `DEBT_LTD_NONCURRENT`) | **PROPOSAL-ONLY** (F2) | CDNL with `NotesPayableCurrent`; FRD with `LongTermLineOfCredit` | Noncurrent only; it is a total only when summed |
| `LongTermLineOfCredit` (FRD) | `total_debt_resolved`, noncurrent line-of-credit draws | **PROPOSAL-ONLY** (F2) | FRD D/E (row 19): 92,564 + 3,489 at 2026-03-31; 91,488 + 3,489 at 2026-06-30 | Noncurrent only, and FRD needs the sum with `LongTermNotesPayable` |
| `SeniorNotes` (EG) | `total_debt_resolved`, F1 or F2 | F1 ELIGIBLE; **EG fill PROPOSAL-ONLY** | EG needs the F2 sum | EG face: 2,352 + 218 + 1,019 = 3,589 $M (V26; R2 of 10-Q 0001095073-26-000032, me) |
| `SubordinatedDebt` (EG) | `total_debt_resolved`, F1 or F2 | F1 ELIGIBLE; **EG fill PROPOSAL-ONLY** | as above | EG labels this line "Long-term notes" (me, R2): label and tag diverge, so the Verifier must check the note |
| `AdvancesFromFederalHomeLoanBanks` (EG) | `total_debt_resolved` candidate | **PROPOSAL-ONLY** (perimeter) | EG D/E (row 21) | Whether FHLB funding counts as debt for an insurer is a perimeter decision; it must never apply to banks or thrifts (SIC 6000-6199), where FHLB advances are funding |
| `InterestExpenseNonoperating` (CDNL) | `interest_expense`, priority 3 after `InterestExpense` and `InterestExpenseDebt` | **ELIGIBLE**, conditional on check I-2 = 0 | CDNL interest coverage (row 13), only after the CDNL "net" label is resolved (below) | Expense-side standard tag, a strict part of `InterestExpense`. If a filer reports operating and nonoperating parts without the total, first_match would understate, so I-2 must find none |
| `Cash` (CDNL) | `cash_and_equivalents` | **PROPOSAL-ONLY** (component) | CDNL ROIC cash input (row 5) | Excludes cash equivalents by definition, so it is a component, not an exact match. EG (insurer) also tags `Cash` 1,117 within "Total investments and cash" (me, R2): an insurer's cash-equivalent perimeter differs |

CDNL caution (FILING-CHECKED, me and V26): CDNL labels `InterestExpenseNonoperating` "Interest expense, net" (10-K R4; 10-Q R4: (3,466,263) for the quarter, (5,712,139) for the six months). If "net" means interest income was netted in, the expense tag carries a net figure. The mapping may be ELIGIBLE globally while CDNL's own cell is not verified: the Verifier must open CDNL's interest note. If income is netted, record a CDNL finding and suppress that cell with the Decision 4 reason.

### Read-only query designs for the Tag Mapper (NOT RUN)

Run discipline for every query: `ListAgents` first; wait if a peer reprocess or recompute is running; one connection; `begin read only; set local statement_timeout = '5min';` per chunk; chunk by `company_id` range (about 250 companies per chunk), `commit` between chunks; no writes; results go to a scratch file, not a table. Before running, confirm each candidate tag exists in `analytics.sec_tag_library` (taxonomy `us-gaap`) and record its `active_company_count`. Split every count into end_date >= 2015-01-01 (display window, doc 38) and earlier. Break every count down by SIC 2-digit.

**Shared base for debt and cash (Q-BASE):** one row per (company, instant period) with a jsonb of authoritative undimensioned us-gaap values for the family list. The tie-break matches `resolve_total_debt_components` (`distinct on (company_id, period_id, tag) ... order by f.id desc`).
```sql
with fam(tag, role) as (values
  -- existing TOTAL_DEBT_TAGS (concept_fallback.py) ...
  ('DebtLongtermAndShorttermCombinedAmount','x_all_in'), ('DebtAndCapitalLeaseObligations','x_all_in_lease'),
  ('LongTermDebt','x_incl'), ('LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities','x_incl'),
  ('LongTermDebtNoncurrent','x_nc'), ('LongTermDebtAndCapitalLeaseObligations','x_nc'),
  ('LongTermDebtCurrent','x_cur'), ('LongTermDebtAndCapitalLeaseObligationsCurrent','x_cur'),
  ('DebtCurrent','x_debt_cur'), ('ShortTermBorrowings','x_st'), ('CommercialPaper','x_st'),
  ('ConvertibleLongTermNotesPayable','x_conv'), ('DebtInstrumentCarryingAmount','aux_carrying'),
  -- candidates
  ('NotesPayable','c_np'), ('NotesPayableCurrent','c_np_cur'), ('LongTermNotesPayable','c_np_nc'),
  ('LongTermLineOfCredit','c_loc_nc'), ('LineOfCredit','c_loc'), ('SeniorNotes','c_senior'),
  ('SubordinatedDebt','c_sub'), ('AdvancesFromFederalHomeLoanBanks','c_fhlb'),
  -- context
  ('UnamortizedDebtIssuanceExpense','aux_dic'), ('Liabilities','aux_liab'),
  ('OperatingLeaseLiability','aux_oplease'), ('FinanceLeaseLiability','aux_finlease')
  -- Tag Mapper: extend with every other borrowing tag in sec_tag_library whose definition is a borrowing
  -- (secured/unsecured debt, other long-term debt, bank loans, other borrowings); list them in the report
),
f as (
  select distinct on (f.company_id, f.period_id, c.tag)
         f.company_id, f.period_id, p.end_date, c.tag, fam.role, f.value, f.id as fact_id, f.filing_id
  from core.fact f
  join core.concept c on c.id = f.concept_id and c.taxonomy = 'us-gaap'
  join fam on fam.tag = c.tag
  join core.period p on p.id = f.period_id and p.period_type = 'instant'
  where f.is_authoritative and f.company_id >= %(lo)s and f.company_id < %(hi)s
  order by f.company_id, f.period_id, c.tag, f.id desc)
select f.company_id, co.sic_code, f.period_id, f.end_date,
       jsonb_object_agg(f.tag, f.value) as v,
       array_agg(f.tag order by f.tag) filter (where f.role like 'x\_%%' or f.role like 'c\_%%') as debt_tags,
       (select cf.value from analytics.canonical_fact cf
         join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id and cc.name = 'total_debt_resolved'
         where cf.company_id = f.company_id and cf.period_id = f.period_id) as current_total_debt
from f join core.company co on co.id = f.company_id
group by f.company_id, co.sic_code, f.period_id, f.end_date;
```

Required outputs, per candidate tag:
- **D-1 standalone:** periods where `debt_tags` = {tag} exactly (the F1 fill population), with distinct companies, how many already have `current_total_debt` (must be 0 for F1; nonzero means a tag-preference or parser row exists, so stop and report), values < 0 (must be 0), value > `Liabilities` (must be 0).
- **D-2 coexistence with each existing aggregate** (`x_all_in`, `x_incl`, `x_nc`, `x_debt_cur`): counts where candidate = aggregate (same debt tagged twice), candidate < aggregate (component), candidate > aggregate (red flag; list every case). Coexistence is not equivalence; this only sizes double-count risk.
- **D-3 notes trio:** for periods with `NotesPayable` and both `NotesPayableCurrent` and `LongTermNotesPayable`, classify `NotesPayable` - (pair) as 0, = `UnamortizedDebtIssuanceExpense` (CDNL shape), or other. List the "other" cases.
- **D-4 F2 sums** (CDNL pair; FRD `LongTermLineOfCredit` + `LongTermNotesPayable`; EG three-tag set): count periods with exactly that set and no aggregate; compare the sum to `DebtInstrumentCarryingAmount` where present (equal or not); list companies.
- **D-5 lease contamination:** periods where a candidate equals `OperatingLeaseLiability` or `FinanceLeaseLiability` (possible mis-tag; list).
- **D-6 sector:** all of the above by SIC; F1 counts inside SIC 6000-6199 are reported separately and excluded from any fill.

**Q-D3b (E1 audit):** from the same base, rows where `current_total_debt` = 0, grouped by which tags produced it and whether any candidate tag is nonzero at the same instant (a nonzero candidate means the stored 0 is wrong: list every one).

**Q-I (interest):** the same pattern on duration periods, with family `InterestExpense`, `InterestExpenseDebt`, `InterestExpenseNonoperating`, `InterestExpenseOperating`, `InterestIncomeExpenseNonoperatingNet`, `InterestIncomeExpenseNet`, `InterestCostsIncurred`, `InterestPaidNet`. Group on (company, period start, period end) and keep `end_date - start_date` so quarter, YTD and annual are never compared across lengths.
- I-1: `InterestExpenseNonoperating` alone (no `InterestExpense` or `InterestExpenseDebt`) = the fill population. Report values < 0 (must be 0 or explained), and periods where the value is greater than `InterestCostsIncurred`.
- I-2: `InterestExpenseNonoperating` and `InterestExpenseOperating` both present without `InterestExpense` = **must be 0 for ELIGIBLE**. If nonzero, the mapping becomes PROPOSAL-ONLY (it needs a sum rule).
- I-3: where `InterestExpense` coexists, classify Nonoperating = / < / > `InterestExpense`.
- I-4: Nonoperating = `InterestIncomeExpenseNonoperatingNet` in absolute value (the filer is putting a net figure in the expense tag; list these for the Verifier).
- I-5: SIC breakdown; 6000-6199, 62xx and 63xx are excluded from `interest_coverage` fills.

**Q-C (cash):** instants with `Cash`, `CashAndCashEquivalentsAtCarryingValue`, `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents`, `CashEquivalentsAtCarryingValue`, `RestrictedCash`. C-1: `Cash` with neither priority-1 nor priority-2 present (the fill population), and inside it the count that also has `CashEquivalentsAtCarryingValue` (each one would be understated). C-2: where priority 1 coexists, `Cash` = / < / > CCE. C-3: SIC breakdown (63xx insurers and 60xx banks separately). This informs the reviewer; Cash stays PROPOSAL-ONLY regardless.

**Q-D2 (SG&A control group, Decision 2):** duration periods with an authoritative `OperatingIncomeLoss`, `revenue_sanity_resolved` > 0, `cost_of_revenue_resolved`, `sga_expense`, and none of the operating-expense family other than SG&A. Output `OperatingIncomeLoss - (revenue - cost_of_revenue - sga)` per row: the count exactly 0 (within filed rounding) and every non-zero row listed with company and accession, for the Verifier to explain from the face.

### Verifier sample and withdrawal criteria

- Sample size: 30 cases per ELIGIBLE tag (total_debt and interest_expense feed locked metrics; PLAN tier), stratified per study 24 item 9: small caps, custom-tag-heavy filers, non-December and 52/53-week years, amended filings, and every SIC division in the fill population. Each case is checked against the face statement and the debt or interest note of the filing behind the fact. 0 failures are required to proceed. A clean sample only means "none found in this sample".
- **Withdraw an F1 debt tag** (revert the code path and replay) if any of these occurs: a sampled or later-reported standalone value differs from the filing's total borrowings at that date (a borrowing line omitted, the tag used for a sub-schedule, or a segment value); D-1 shows any period where it would override an existing value; any negative value or value > `Liabilities`; or a D-5 lease match is confirmed. Re-admission requires a deterministic exclusion condition that removes the failing class. No error tolerance applies.
- **Withdraw `InterestExpenseNonoperating`** if I-2 > 0 at any time (including after new filings: rerun I-2 on every nightly tag-library refresh), or any sampled value includes netted interest income or excludes operating interest the filer also reports. A single company's netting found later becomes a recorded finding plus a suppression of that company's cells; if the class cannot be excluded deterministically, the mapping is withdrawn.
- PROPOSAL-ONLY items have no withdrawal criterion because they are not to be applied.

## Source-based tests to draft (with any later implementation; not written)
- `compute_total_debt({'NotesPayable': 5965.5})` gives 5965.5 via path `sole_instrument_notes` (DHI 2025-09-30 shape).
- The CDNL R60 trio `{'NotesPayable': 121178878, 'NotesPayableCurrent': 6128674, 'LongTermNotesPayable': 113152864}` never returns 121178878 and never 240M+. Until F2 is approved it returns None.
- `{'NotesPayable': X, 'LongTermDebt': Y}` returns the existing path's value; F1 is never reached.
- `{'LongTermLineOfCredit': 92564}` alone returns None (noncurrent only, not F1).
- Operating lease tags alone (CATO and ATEX shapes) return None; `total_debt` is never 0 from leases.
- `InterestIncomeExpenseNonoperatingNet` never resolves into `interest_expense` (BBW +801 shape).
- OI fallback: the CVX, AJG and HTZ shapes (no OI, CostsAndExpenses only) produce no `operating_income_resolved`.

## Proposed ledger rows (not appended: this task restricts writes to this file)
| 2026-10-18 | CDNL: `NotesPayable` 121,178,878 is the gross note-schedule total; `NotesPayableCurrent` 6,128,674 + `LongTermNotesPayable` 113,152,864 are the net face values (issuance costs 1,897,340) | A total tag and its components can coexist undimensioned; never sum them, and prefer face-basis components over a schedule total | CDNL 0001193125-26-120014 R60 |
| 2026-10-18 | BBW tags net interest income (+801K) with `InterestIncomeExpenseNonoperatingNet`, the same tag UNIT uses for net expense 602.8M | A net interest tag cannot be an interest-expense measure without per-company composition evidence | BBW 0001437749-26-012501 R4; UNIT 0001628280-26-013196 R84 |
| 2026-10-18 | Reg S-X 5-03 has no operating-income caption; single-step statements are permitted | A missing OI subtotal can be structural; show "not reported as a subtotal" only after a face check | 17 CFR 210.5-03 |

## Status
Task: **COMPLETE** as a policy pass. Per decision: D1 PROPOSAL-ONLY; D2 PROPOSAL-ONLY (plus a routed defect in the existing fallback); D3 E2 and E3 PROPOSAL-ONLY, E1 existing behaviour plus an audit query, lease policy confirmed for operating leases with finance-lease perimeter OPEN; D4 "no" keeps current behaviour, UNIT exception PROPOSAL-ONLY; D5 ELIGIBLE: `NotesPayable` (F1), `InterestExpenseNonoperating` (conditional on I-2), `SeniorNotes` and `SubordinatedDebt` (F1 only, no named cell filled); PROPOSAL-ONLY: `NotesPayableCurrent`, `LongTermNotesPayable`, `LongTermLineOfCredit`, `AdvancesFromFederalHomeLoanBanks`, `Cash`, and the EG, FRD and CDNL sums. All checks: NOT_RUN.

Commands actually run: read data-team 20, 21, 22, 11, 03, 24, 26, `doc/data-moat/decisions.md`, `wave1-canonical-definitions.md` (grep), `team/PLAN.md` (grep); read `mapper/concept_fallback.py`, `mapper/conflict_resolution.py` (lines 560-749), `mapper/concepts.py` and `expanded_concepts.py` (grep), migrations 0003, 0004, 0036 and 0058 (grep); `git log` on the mapper modules; `git diff --stat` (another session's uncommitted `conflict_resolution.py` stale-fill change, unrelated, not touched). Extracted defref definitions and the CDNL R60 rows from cached R-files with scratch scripts `/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/scripts/defs.py` and inline `python3 -I`; mapped cache hashes to accessions; computed sha256. One web read (Reg S-X 5-03, Cornell LII). No SEC fetches, no database connection.

Untested scope: every query above; whether our stored values for these cells match the filings; earlier TTM quarters; sign of the net-interest and nonoperating-interest facts as stored in `core.fact`; CDNL's interest note ("net"); ATEX's face for catch-all lines; DHI R50 dimension context (Verifier assumption); finance-lease composition of existing combined-tag values; whether `interest_coverage` already excludes banks; the existing OI fallback's current exactness.

Next actions: (1) Verifier reviews this file, Decision 5 and the CDNL R60 counterexample first. (2) Tag Mapper runs Q-BASE/D-1..D-6, Q-D3b, Q-I and Q-C under the run discipline above, after `ListAgents`, and reports. (3) Data Chief decides whether F1 counts as "single clean tag" under PLAN, and routes the existing OI-fallback exactness defect. (4) Founder names an accounting reviewer for D1 (EBIT variant), D2, D3 E2 and E3, the finance-lease perimeter, FHLB, the F2 sums and Cash.
