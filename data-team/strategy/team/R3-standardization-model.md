# R3. Standardization model: comparable numbers when companies compose a line differently

Role: Standardization Lead (data-team/11), for the tag-non-uniformity investigation (BRIEF.md, Ritwik, 2026-10-21).
Objective: design the model that makes composite numbers (D&A, capex, total debt, interest expense, operating income, revenue, net income attributable, FCF inputs) comparable across companies, so an engineer can build it.
Status of every accounting definition below: **PROPOSED**. Nothing here is approved. Perimeter choices need the accounting reviewer the founder has not yet named (data-team/33 decision 2; strategy/37 D3). I cannot approve my own rule; the Verifier reviews this next.

Evidence labels: **FILING-CHECKED** (original SEC filing or official FASB taxonomy file opened; accession and locator given), **CODE-READ** (what our repository does today; not financial evidence), **DATA-INFERRED** (SEC Financial Statement Data Sets 2025q4 or our docs; no filing opened), **ASSUMED** (reasoning only).

Database: **not queried.** `select count(*) from pg_stat_activity` returned 17 (brief limit 14). Every count below comes from FSDS 2025q4 or repo files, never from our tables.

---

## 0. Findings in one page

1. **The non-uniformity that costs us is the perimeter of a line, not its tag name.** In FSDS 2025q4 (5,631 10-K and 10-Q filings, 5,468 companies; 4,271 non-financial filings), our current single-tag recipes match the face statement exactly as "the only line" in only part of the population (DATA-INFERRED, `ours.py` below):
   | Concept (non-financial filings with the statement section) | Our recipe finds the only face line | Our recipe finds a line but other component lines also appear | Our recipe finds nothing, but component lines exist | No such line |
   |---|---|---|---|---|
   | D&A (cash-flow operating section, 4,262) | 2,256 | 219 | **1,202** | 585 |
   | Capex (investing section, 3,846) | 2,084 | **577** | **676** | 509 |
   | Interest expense (income statement, 4,270) | 719 | 28 | **1,667** other gross tags; 800 net-only | 1,056 |
   Caveat: companyfacts can carry a tag in a note that is not on the face, so "finds nothing" overstates our blanks; it is the face composition that matters for comparability, and that is what these columns measure.
2. **Five composition defects in our code today (CODE-READ, confirmed against the official FASB 2025 calculation linkbase, FILING-CHECKED):**
   - `compute_total_debt` treats `LongTermDebtNoncurrent` and `LongTermDebtAndCapitalLeaseObligations` as alternative spellings of one role (`concept_fallback.py` lines 66-73). The FASB 2025 calc tree says `LongTermDebtAndCapitalLeaseObligations` = `LongTermDebtNoncurrent` + `FinanceLeaseLiabilityNoncurrent`, and `DebtCurrent` = `ShortTermBorrowings` + `LongTermDebtCurrent` + `FinanceLeaseLiabilityCurrent` (`us-gaap-stm-sfp-cls-cal-2025.xml`). So finance leases are in total debt for filers that use combined tags (CVX) and out for filers that report them separately (Walmart). Same concept, two perimeters, and the `path` that would tell them apart is computed but not stored.
   - `fcf`, `fcf_margin` (`definitions.py` lines 130-141) and `fcf_yield` (`price_metrics.py` lines 57-58, 425-426) read raw `capex`, while the statements show `capex_resolved`, which adds `PaymentsToAcquireSoftware` (`concept_fallback.py` lines 697-731). The displayed capex row and the FCF that uses it can have different perimeters for the same company-period.
   - `depreciation_and_amortization_resolved` takes the larger of `DepreciationAndAmortization` and `DepreciationDepletionAndAmortization` (`concept_fallback.py` 639-677), a rule fitted to yfinance (64.1% -> 80.1% within 5%). It picks whichever perimeter is bigger, not the defined one, and cannot see composed D&A (AMD, Aptiv, Gilead, ArcBest below).
   - `net_income` is one first_match chain over `NetIncomeLoss` -> `ProfitLoss` -> `NetIncomeLossAvailableToCommonStockholdersBasic` (`concepts.py` 150-176): three attributions (parent, consolidated incl. NCI, common after preferred) under one name.
   - `revenue` puts `RevenueFromContractWithCustomerExcludingAssessedTax` (RCFC) ahead of `Revenues` (`concepts.py` 103-118). At Walmart that shows net sales 177,769M instead of total revenues 179,496M; at ITC it shows 515M against a face total of 454M (RCFC is larger). Already known as fix-plan family G (data-team/33); the model below fixes it structurally.
3. **How others do it (section 1):** the FASB taxonomy, XBRL US / Hoffman's Fundamental Accounting Concepts (FAC) and edgartools all show the same thing from different angles. Totals are compositions; filers pick different reporting styles; a tag-to-label table alone mixes perimeters (edgartools maps `InterestIncomeExpenseNonoperatingNet` and `FinanceLeaseLiabilityNoncurrent` to "Interest Expense" and "Long-Term Debt"). Compustat re-standardizes history repeatedly (Lyle, Siano and Yohn 2024: datapoints updated about 6 times, re-standardization cycle about 2 years), which is the failure mode to design against.
4. **Recommendation:** add a composition layer in Mapper. Each composite concept becomes a versioned definition made of named component slots with include/exclude flags. For every company-period we store a **perimeter record** (which slots the company's reported line contains, which it reports separately, which are unknown, with evidence), a **reported value** (the face line as filed) and a **standardized value** (computed from the slots by the definition). Screens and cross-company ratios use only standardized values whose perimeter is complete; anything else is a reasoned blank for screening, and the reported line is still shown with its own label.

---

## 1. How it is done elsewhere (with sources)

| Source | What it does | What we take | Evidence |
|---|---|---|---|
| FASB US GAAP taxonomy 2025 calculation linkbases | Defines totals as sums of children. `DepreciationDepletionAndAmortization` = `Depreciation` + `Depletion` + `AdjustmentForAmortization` + `OtherDepreciationAndAmortization`; `AdjustmentForAmortization` includes `AmortizationOfIntangibleAssets`, `FinanceLeaseRightOfUseAssetAmortization`, **`AmortizationOfFinancingCostsAndDiscounts`**, DAC and MSR amortization, `AccretionAmortizationOfDiscountsAndPremiumsInvestments` (weight -1) and 16 more. `PaymentsToAcquireProductiveAssets` = PP&E + `PaymentsForSoftware` + `PaymentsToAcquireIntangibleAssets` + crypto, mineral rights, equipment on lease. `PaymentsForProceedsFromProductiveAssets` = purchases - proceeds. `InterestExpenseNonoperating` = `InterestExpenseDebt` + `FinanceLeaseInterestExpense` + commitment fees + customer-deposit interest. `InterestAndDebtExpense` includes gains/losses on debt extinguishment. `Revenues` children include `OtherIncome`, `GainsLossesOnSalesOfAssets`, `RealizedInvestmentGainsLosses`. `OperatingIncomeLoss` = `GrossProfit` - `OperatingExpenses` + `OtherOperatingIncomeExpenseNet` + government assistance. `NetIncomeLoss` = `ProfitLoss` - NCI; `NetIncomeLossAvailableToCommonStockholdersBasic` = `NetIncomeLoss` - preferred - participating | The slot lists below. The taxonomy totals are wider than an analyst's definition (D&A includes debt-cost amortization; "Revenues" can include gains), so a total tag can never be the canonical number by name alone | FILING-CHECKED (official files): https://xbrl.fasb.org/us-gaap/2025/stm/us-gaap-stm-scf-indir-cal-2025.xml, .../us-gaap-stm-soi-cal-2025.xml, .../us-gaap-stm-sfp-cls-cal-2025.xml (HTTP 200, read 2026-10-21) |
| XBRL US / Charles Hoffman, Fundamental Accounting Concepts v3 | About 10 "reporting styles" cover about 90% of SEC filers; each style is a network with (a) a mapping table from a fundamental concept to US GAAP tags with a **try order**, (b) **impute rules** executed in order (forward chaining), (c) **consistency rules** (identities). Keeps `NetIncomeLoss` (consolidated, mapped to `ProfitLoss`), `NetIncomeLossAttributableToParent` and `NetIncomeLossAvailableToCommonStockholdersBasic` separate; IS-Impute-10: parent = net income - NCI; IS-Impute-02: parent = available-to-common only when preferred adjustments are zero. Its documentation is titled "Comparability is NOT Uniformity" | Reporting style per company-period (our "statement shape"), ordered imputes, identities as gates, three separate net-income concepts. Do NOT copy: its rules test `= 0` to mean "missing", which conflates a reported zero with absence, and its revenue try-list mixes totals with components (`InterestIncomeExpenseNet` at try order 9) | FILING-CHECKED (pages read 2026-10-21): http://xbrl.squarespace.com/fundamental-accounting-concept/ ; http://www.xbrlsite.com/2016/fac/v3/Documentation/ ; http://www.xbrlsite.com/2016/fac/v3/Rules_Impute/IncomeStatement3Step-impute.html ; .../Rules_Mapping/IncomeStatement3Step-mapping.html ; .../Rules_Mapping/BalanceSheetClassified-mapping.html |
| edgartools 5.49.0 (installed in `pipeline/.venv`) | `gaap_mappings.json` (2,924 tags) and `concept_mappings.json` relabel a tag to a display concept. `Depreciation`, `DepreciationAndAmortization`, `DepreciationDepletionAndAmortization`, `OtherDepreciationAndAmortization` all -> "Depreciation Expense"; `InterestExpense`, `InterestExpenseNonoperating`, **`InterestIncomeExpenseNonoperatingNet`**, `FinanceLeaseInterestExpense` all -> "Interest Expense"; **`FinanceLeaseLiabilityNoncurrent`** -> "Long-Term Debt"; `PaymentsToDevelopSoftware` -> "Purchase of Intangible Assets" (confidence 0.319). Docs: priority P1 core, P2 company, P4 prefix boost; over 200 ambiguous tags resolved by "statement context and sign convention"; composites (D&A, capex, debt, interest, FCF) not addressed | It is a labeler, not a composer: the same display label carries different perimeters (net vs gross interest, debt with or without leases). Our model must not be a relabeling table | FILING-CHECKED (local package files `edgar/xbrl/standardization/gaap_mappings.json`, `concept_mappings.json`); docs https://edgartools.readthedocs.io/en/latest/advanced/customizing-standardization/ |
| Compustat (via Lyle, Siano, Yohn, "Re-Standardized Financial Statement Data", Yale working paper, July 2024) | Compustat updates each datapoint about 6 times (8.5M datapoints, 40,000 firms, 1986-2023), re-standardization cycle about 685 days; numeric-to-numeric changes in Dpq (depreciation), Oiadp, Dlttq (long-term debt), Saleq, Niq typically 20% to 130% of the original; a Boeing FY2016 example shows Oiadp 17% off the as-filed figure | Store `definition_version` on every standardized value and never overwrite history silently; keep the reported value beside the standardized one | FILING-CHECKED (PDF text read): https://som.yale.edu/sites/default/files/2024-07/Re-Standardized%20Financial%20Statement%20Data.pdf , pages 9-10 and the Snapshot statistics section |
| Du, Huddart, Jiang (JAE 2023); Chychyla and Kogan | Standardized databases differ from as-filed data, more for complex reporters | Keep as-reported beside standardized | Second-hand via data-team/24 section 1.3 (not re-read) |
| FactSet, Calcbench, Morningstar, S&P item definitions | Not confirmed this run: Calcbench help article HTTP 403; search engines blocked; FactSet four-template practice is second-hand via data-team/24 | Nothing claimed beyond data-team/24 | Could not confirm |

Common pattern (DATA-INFERRED from the above): every serious approach separates (a) what the filer reported, (b) a defined target, (c) the rule that maps one to the other, and checks identities. The approaches that fail comparability are the ones that only relabel (edgartools) or that re-standardize without versioning (Compustat per LSY).

---

## 2. Filing evidence for composition (FILING-CHECKED)

R-files fetched from sec.gov with the declared User-Agent, about 2 requests per second; sha256 prefix in brackets. Values in the filing's own scale.

| Company, filing | Locator | What the face shows | Why it matters |
|---|---|---|---|
| AMD 10-Q, 9M to 2025-09-27, 0000002488-25-000166 | R6 [2a7d677624598f60] | "Depreciation and amortization" 556 tagged `OtherDepreciationAndAmortization`; "Amortization of acquisition-related intangibles" 1,697 tagged `AmortizationOfIntangibleAssets`; capex 752 `PaymentsToAcquirePropertyPlantAndEquipment`; CFO total 5,109 includes 920 from discontinued operations | D&A for EBITDA is 2,253, composed of two lines, neither of which our D&A tags read. A single-tag D&A is either blank or 75% short |
| ArcBest 10-Q, 9M to 2025-09-30, 0001104659-25-106816 | R8 [fd3dac31646a200b] | "Depreciation and amortization" 115,690K tagged **`Depreciation`**; "Amortization of intangibles" 9,600K; "Purchases of property, plant and equipment, **net of financings**" 107,005K; "Capitalization of internally developed software" 9,958K `PaymentsToDevelopSoftware`; proceeds from sale of PP&E 32,518K | Label and tag disagree on perimeter; capex is net of financed purchases; software capex sits on a tag our `capex_resolved` does not read (it reads `PaymentsToAcquireSoftware`) |
| Aptiv 10-Q, 9M to 2025-09-30, 0001521332-25-000051 | R6 [b9d52f2e915be88a] | Depreciation 585 `Depreciation`; Amortization 156 `AmortizationOfIntangibleAssets`; "Amortization of deferred debt issuance costs" 7 `AmortizationOfFinancingCosts`; "Capital expenditures" 489 on **`PaymentsToAcquireProductiveAssets`** | D&A = 741 (debt-cost amortization 7 is interest, excluded). Capex is on a tag our mapping does not read, so FCF is blank or wrong |
| Gilead 10-Q, 9M to 2025-09-30, 0000882095-25-000047 | R8 [81c7b10d0e2ee27e] | "Depreciation expense" 280 `Depreciation`; "Amortization expense" 1,793 **`AdjustmentForAmortization`** | `AdjustmentForAmortization` is a taxonomy aggregate that can include debt-cost amortization; its slots are unknown from the face, so the standardized D&A needs the note (status unknown, not a guess) |
| Jabil 10-K FY to 2025-08-31, 0001628280-25-045293 | R5 [c4fa66daeedd537e], R8 [e2692751291fb795] | Income statement "Amortization of intangibles" 62 `AmortizationOfIntangibleAssets`; cash flow "Depreciation and amortization" 674 `DepreciationDepletionAndAmortization` | An income-statement D&A line is often only a component. In FSDS, 30 of 72 10-Ks with both lines differ (DATA-INFERRED). Source D&A from the cash-flow statement |
| Walmart 10-Q, Q3 to 2025-10-31, 0000104169-25-000191 | R2 [b4262cae77e43587], R4 [4d7ea177cf23001e] | Net sales 177,769 RCFC; Membership and other income 1,727 `OtherIncome`; Total revenues 179,496 `Revenues`. Interest: Debt 563 `InterestExpenseDebt`; Finance lease 121 `FinanceLeaseInterestExpense`; interest income (93); "Interest, net" 591. Consolidated net income 6,088 `ProfitLoss`; NCI 55; attributable to Walmart 6,143 `NetIncomeLoss`. Balance sheet: short-term borrowings 8,401; LTD due within one year 3,523; LTD 34,445; finance lease obligations 842 + 5,916; operating lease obligations 1,592 + 13,705 | Revenue precedence; gross vs net interest; finance-lease interest vs debt interest; three net-income attributions; borrowings 46,369 vs with finance leases 53,127 |
| ITC Holdings 10-Q, Q3 to 2025-09-30, 0001317630-25-000018 | R4 [89d7be5ba25f9aae] | "Transmission and other services" 515 RCFC; "Formula Rate true-up" (61) custom `itc_FormulaRateTrueUpRevenue`; "Total operating revenues" 454 `Revenues` | RCFC is not a lower bound of total revenue; the face total must win |
| Carried from the ledger (data-team/22) | CVX 0000093410-26-000078 R3/R5; PLD 0001193125-26-051453 R4; AMZN/GOOG/AAPL LTD face value | CVX "Long-term debt" = `LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities` (leases inside); PLD operating income includes about 943.6M disposition gains; `LongTermDebt` is face value at AMZN and GOOG | Perimeters differ under the same tag |

Element definitions read from the defref blocks of those R-files (FILING-CHECKED): `OtherDepreciationAndAmortization` "...tangible and intangible assets ... classified as other"; `Depreciation` "...tangible assets ... Includes production and non-production related depreciation"; `DepreciationDepletionAndAmortization` "...tangible assets, intangible assets, or depleting assets"; `PaymentsToAcquirePropertyPlantAndEquipment` "...long-lived, physical assets ... includes cash outflows to pay for construction of self-constructed assets"; `PaymentsToDevelopSoftware` "...software ... for internal use ... that qualify for capitalization"; `Revenues` "...Includes, but is not limited to, investment and interest income before deduction of interest expense when recognized as a component of revenue, and sales and trading gain (loss)"; `ProfitLoss` "consolidated ... including the portion attributable to the noncontrolling interest"; `NetIncomeLoss` "...attributable to the parent"; `FinanceLeaseInterestExpense` "interest expense on finance lease liability".

## 3. Composition census (DATA-INFERRED, FSDS 2025q4)

Method: `pre.txt` face statements (BS, IS, CF; parenthetical rows dropped), `num.txt` values for the filing's own period end, undimensioned, USD. 10-K uses the 4-quarter value; 10-Q uses the quarter for IS and the longest YTD for CF. Cash-flow operating section = lines before the CFO total; investing section = lines between CFO and CFI totals. "Financial" = SIC 60-64, 67xx, 6798, excluded from these counts. Tag families are my lists (in the scripts). Scope: one quarter's filings (mostly calendar Q3 10-Qs plus non-December 10-Ks), not our active population, no value check against our tables.

- D&A shapes on the cash-flow face (non-financial, core lines only): one combined line 2,286; `Depreciation` only 427; separate depreciation + intangible amortization 286; combined line + separate intangible amortization 76; custom-tag D&A 222 alone and 439 alongside standard lines; none 537 (of 4,262 non-financial filings with a CFO line). Separate amortization lines that are not depreciation of operating assets also sit in the same section: debt-cost amortization in 1,439 filings, right-of-use or lease amortization (operating or finance, my tag list) in 823.
- Capex shapes: PP&E line only 2,514; PP&E + intangibles 321 (+16 more with two PP&E lines); PP&E + software 146 (+23 with intangibles); two or three PP&E-family lines 137; intangibles or software only 71; custom only 53. A disposal-proceeds line appears in 991 of 3,846.
- Interest (income statement): gross only 1,349; gross + separate interest income 867; net only 763 (+25 custom); income only 330; none 604; filings with two different gross tags 33.
- Operating income: face `OperatingIncomeLoss` in 3,783; above that line, the face shows an impairment line in 684, restructuring 513, other operating income 393, gain/loss on disposal 328, equity-method income 55. No operating-income line 398; `CostsAndExpenses` with no OI 89.
- Net income: `NetIncomeLoss` only 2,679; `NetIncomeLoss` + `ProfitLoss` + NCI 744; `ProfitLoss` with no `NetIncomeLoss` 259; available-to-common lines in 523.
- Revenue: RCFC as the only revenue tag 1,953; `Revenues` only 1,134; RCFC-including-tax 280; both RCFC and `Revenues` on the face 131 (RCFC < Revenues 75, equal 15, RCFC > Revenues 3); excise line 79; none 751.
- Debt (balance sheet): lease-combined debt tag on the face (`LongTermDebtAndCapitalLeaseObligations*`, `DebtAndCapitalLeaseObligations`, `DebtCurrent`) 516; separate finance-lease liability line 443; both 18; operating-lease liability line 2,675.

---

## 4. Deliverable 1: the data model

### 4.1 Principles
1. A composite concept is a **definition**: an ordered set of named component slots, each with a default `include` / `exclude` / `separate_concept` flag and a reason. It is versioned and has an approval status.
2. For each company, concept and period we record what the company actually did: the **perimeter record**. It is evidence about the filing, not a choice we make.
3. Two numbers are kept and never confused: **reported** (the face line as filed, its label, tag and accession) and **standardized** (computed from slots per the definition version). They are equal when the reported perimeter already matches the definition.
4. A standardized value exists only when every included slot is known (reported separately with a value, known to be inside the anchor, or shown as not present) and no excluded slot is trapped inside the anchor. Otherwise it is a reasoned blank. No estimates, no "close enough".
5. Nothing changes `core`. The layer lives in `analytics`, written by Mapper from `core.fact` plus statement-structure evidence (presentation and calculation relationships). Existing `concept_mapping` and `canonical_fact` stay; this sits beside them.

### 4.2 Tables (proposal; a migration only after review; numbers claimed in doc 53 at that time)

```sql
-- versioned definition of a composite concept
analytics.composite_definition (
  id bigint pk, concept_name text,            -- e.g. 'da_ebitda', 'capex_std'
  version int, status text check (status in ('proposed','verified','approved','retired')),
  statement text, period_type text,           -- 'cash_flow','duration'
  unit text default 'USD', sign_policy text,  -- 'positive_magnitude' | 'economic_sign'
  attribution text,                           -- 'consolidated' | 'parent' | 'common'
  template text,                              -- 'commercial' | 'bank' | 'insurer' | 'reit' | 'bdc' | 'utility' ...
  effective_from date, approved_by text null, approved_at timestamptz null,
  supersedes_id bigint null, notes text,
  unique (concept_name, version, template)
);

-- slots of a definition
analytics.composite_slot (
  definition_id bigint fk, slot_code text,    -- 'DA.DEPRECIATION', 'DA.AMORT_DEBT_COST'
  ordinal int, inclusion text check (inclusion in ('include','exclude','separate_concept')),
  arithmetic_sign smallint check (arithmetic_sign in (1,-1)),
  reason text, accountant_required boolean,
  primary key (definition_id, slot_code)
);

-- which tags can carry a slot, or a total that spans several slots
analytics.composite_tag_role (
  definition_id bigint fk, taxonomy text, tag text,
  role text check (role in ('slot','anchor_total','combined')),
  covers_slots text[] not null,               -- slots this tag's amount contains by its definition
  may_cover_slots text[] not null default '{}', -- slots the taxonomy calc tree allows inside it (needs filer evidence)
  evidence text not null,                     -- taxonomy doc label / calc linkbase / tag card
  primary key (definition_id, taxonomy, tag)
);

-- the perimeter record: one row per company, concept, period and source filing
analytics.company_perimeter (
  id bigint pk, company_id bigint, definition_id bigint, period_id bigint, filing_id bigint,
  reporting_style text,                       -- e.g. 'IS_multistep_with_OI', 'CF_indirect', 'BS_classified'
  anchor_fact_ids bigint[], anchor_tag text, anchor_label text, anchor_locator text, -- 'R6 row 4'
  reported_value numeric null,                -- the face line(s) as filed, after unit check, sign as stored
  standardized_value numeric null,
  status text check (status in ('complete','partial','unavailable','not_applicable')),
  reason_code text null,                      -- reuse data-team/03 codes: COMBINED_LINE_ONLY, NOT_SEPARATELY_DISCLOSED, ...
  method text,                                -- 'face_structure' | 'filer_calc' | 'note' | 'verifier_manual'
  definition_version int, built_at timestamptz, reviewed_by text null,
  unique (company_id, definition_id, period_id, filing_id)
);

-- slot state inside each perimeter record
analytics.company_perimeter_slot (
  perimeter_id bigint fk, slot_code text,
  state text check (state in (
    'inside_anchor',          -- filer evidence (calc arc, label, note) shows the anchor contains it
    'reported_separately',    -- its own fact in the same filing and context; value below
    'not_present',            -- filing evidence that the company has none (face plus calc, or note)
    'combined_inseparable',   -- inside a combined line and no separate value to remove or add
    'unknown')),              -- no evidence either way
  value numeric null, fact_ids bigint[] null, evidence jsonb not null,
  primary key (perimeter_id, slot_code)
);
```
`canonical_fact` gets the standardized value under a new `<concept>_std` canonical concept (zero `concept_mapping` rows, the `_resolved` idiom, delete scope excluding it), with `source_fact_ids` = anchor + added slot facts. The reported value keeps living in today's concept (`capex`, `revenue`, ...). Downstream metrics switch to `_std` one family at a time.

### 4.3 Algorithm (per company, concept, period, filing)
1. **Select the filing and context**: latest periodic filing that presents the period (10-K/10-Q, never DEF 14A), undimensioned context, unit USD, period length checked from dates (data-team/21 section 8).
2. **Find the anchor** on the face statement from presentation evidence (FSDS `pre`, or `company_filing_line_evidence`, or the rendered R-file): the line a reader would call this concept (for capex, every investing line that is a purchase of a productive asset). Reporting style is recorded.
3. **Classify slots for the anchor**: use `composite_tag_role.covers_slots`; for every slot in `may_cover_slots`, require filer evidence: the filer's own calculation linkbase children (FSN `cal`, data-team/22 CVX row), the line label, or the note. Without evidence the slot is `unknown`.
4. **Collect separately reported slots** from the same filing and context (sibling face lines first, then notes).
5. **Compute**: standardized = anchor + sum(include slots reported separately) - sum(exclude slots shown inside the anchor with a separate value). Status:
   - `complete`: every include slot is `inside_anchor`, `reported_separately` or `not_present`, and every exclude slot is `reported_separately` (not inside), `not_present`, or inside with a separate value we can subtract **only where the accountant approved subtraction for that slot**.
   - `partial`: some include slot is `unknown` or `combined_inseparable` with no removal path; the value is not published as standardized.
   - `unavailable`: no anchor and no slots; `not_applicable` for a template where the concept does not exist (bank capex is not a gap, it is a template question).
6. **Gates** (any failure sets status `partial` with a finding): no double counting (a slot cannot be both inside the anchor and added); arithmetic ties where the filer gives a total (sum of slots equals the filer total within filed rounding); sign policy per slot; unit USD; same period dates for every input; standardized >= every included slot magnitude where the concept is a sum of non-negative parts.
7. **Write** the perimeter rows, slot rows and the `_std` canonical fact in one transaction per company chunk, idempotent, delete-then-insert scoped to (definition, company).

### 4.4 Quarters, TTM and history
- Q4 and discrete quarters are derived per slot (FY minus 9M YTD of that slot) only when the same slot state holds in both filings; then the standardized value is recombined. Never subtract a standardized FY from a standardized 9M built under different slot states.
- TTM of a standardized flow needs four quarters with status `complete` and the same definition version.
- Each value carries `definition_version`. A new version writes new rows and a diff report; old rows are retired, not overwritten, so a past screen can be reproduced (the LSY re-standardization lesson).

---

## 5. Deliverable 2: proposed definitions for the eight composite concepts

Notation: IN = include, OUT = exclude, SEP = its own concept, AC = needs the named accounting reviewer. Commercial template unless stated. All PROPOSED.

### 5.1 `da_ebitda`: depreciation, depletion and amortization, EBITDA basis
Duration, USD, positive magnitude, consolidated, continuing operations. **Source statement: cash flow (operating adjustments)**, because the income statement often shows only a component (Jabil 62 vs 674; 30 of 72 FSDS 10-Ks with both lines differ).
| Slot | In/out | Reason | Tags (role) |
|---|---|---|---|
| DA.DEPRECIATION (incl. production depreciation in cost of sales) | IN | core | `Depreciation`, `DepreciationNonproduction` (slot); inside `DepreciationDepletionAndAmortization`, `DepreciationAndAmortization`, `OtherDepreciationAndAmortization` |
| DA.DEPLETION | IN (AC) | E&P and mining depletion is the same economics | `Depletion`, `DepletionOfOilAndGasProperties`, `DepreciationAndDepletion` |
| DA.AMORT_INTANGIBLES (acquired) | IN | standard EBITDA practice; AMD's largest D&A line | `AmortizationOfIntangibleAssets` |
| DA.AMORT_SOFTWARE (capitalized internal-use) | IN (AC) | must match capex including software (5.2) | `CapitalizedComputerSoftwareAmortization1` |
| DA.AMORT_FINANCE_LEASE_ROU | IN only if finance leases are in the debt perimeter (AC, coupled decision C1) | finance-lease cost is amortization + interest; adding it back without counting the lease as debt flatters leverage | `FinanceLeaseRightOfUseAssetAmortization` |
| DA.OPERATING_LEASE_ROU | OUT | operating-lease cost is rent, an operating expense | `OperatingLeaseRightOfUseAssetAmortizationExpense`, `NoncashOrPartNoncashLeaseExpense` |
| DA.AMORT_DEBT_COST | OUT | interest; Aptiv shows it separately (7) | `AmortizationOfFinancingCosts`, `AmortizationOfDebtIssuanceCosts`, `AmortizationOfDebtDiscountPremium`, `AmortizationOfFinancingCostsAndDiscounts` |
| DA.AMORT_OTHER_OPERATING (contract costs, DAC, VOBA, MSR, content/film, regulatory assets) | OUT by default (AC for content producers and utilities) | operating costs or sector items | the `AdjustmentForAmortization` children |
| DA.ACCRETION (ARO, investment premium/discount) | OUT (AC) | not depreciation | `AccretionExpense`... ; inside `DepreciationAmortizationAndAccretionNet` (combined) |
| DA.IMPAIRMENT | OUT | not periodic allocation | impairment tags |
Combined tags: `AdjustmentForAmortization` (Gilead) and `DepreciationAmortizationAndAccretionNet` may hold excluded slots: status `unknown` until the note or filer calc shows the parts. `DepreciationDepletionAndAmortization` may include debt-cost amortization by the taxonomy calc tree; accept as covering only DEPRECIATION + DEPLETION + AMORT_INTANGIBLES when no separate debt-cost line exists and the filer calc shows no debt-cost child (filer evidence rule). Replace the current max-of-two-tags rule.
Fixtures (FILING-CHECKED): AMD 9M 2025 = 556 + 1,697 = **2,253**; Aptiv 9M 2025 = 585 + 156 = **741** (7 excluded); Jabil FY2025 = **674**; ArcBest 9M 2025 = 115,690K + 9,600K = **125,290K** (anchor tag `Depreciation` but label "D&A": AC to accept a label as evidence that unspecified amortization is inside); Gilead 9M 2025 = **partial** (1,793 on `AdjustmentForAmortization`, composition unknown).
Downstream: `ebitda`, `ebitda_margin`, `net_debt_ebitda`, `debt_to_ebitda`, `ev_ebitda`.

### 5.2 `capex_std`: capital expenditures (cash)
Duration, USD, positive magnitude (outflow), consolidated, continuing operations.
| Slot | In/out | Reason | Tags |
|---|---|---|---|
| CX.PPE (incl. construction in progress, E&P development, self-constructed) | IN | core | `PaymentsToAcquirePropertyPlantAndEquipment` and its FASB children; `PaymentsForCapitalImprovements`, `PaymentsForConstructionInProcess`, `PaymentsToExploreAndDevelopOilAndGasProperties` |
| CX.SOFTWARE (capitalized internal-use) | IN (AC) | economic capex; DDOG/HOOD/INTU FCF overstated without it (data-team/33 B3) | `PaymentsToAcquireSoftware`, `PaymentsToDevelopSoftware`, `PaymentsForSoftware` |
| CX.INTANGIBLES_OTHER (licences, spectrum, patents) | OUT by default, SEP concept `intangible_purchases` (AC) | different asset class; keeps FCF comparable between filers that buy and filers that build | `PaymentsToAcquireIntangibleAssets` |
| CX.DISPOSAL_PROCEEDS | OUT (gross capex) | proceeds are lumpy; a net figure is a separate concept `capex_net` | `ProceedsFromSaleOfPropertyPlantAndEquipment`, `ProceedsFromSaleOfProductiveAssets` |
| CX.ACQUISITIONS | OUT | M&A, not capex | `PaymentsToAcquireBusinessesNetOfCashAcquired` |
| CX.NONCASH (accrued, financed purchases, finance-lease additions) | OUT | not cash | `CapitalExpendituresIncurredButNotYetPaid`, ArcBest "net of financings" |
| CX.RENTAL_FLEET / equipment on lease | AC | operating asset for rental and leasing companies (HTZ) | `PaymentsToAcquireEquipmentOnLease` |
| CX.REAL_ESTATE_ACQ (REITs) | template `reit` (Sector Analyst + AC) | acquisitions vs development vs maintenance | `PaymentsToAcquireRealEstate`, `PaymentsToDevelopRealEstateAssets` |
Combined tags: `PaymentsToAcquireProductiveAssets` (Aptiv "Capital expenditures") may include intangibles and software by the FASB calc: accept with CX.INTANGIBLES_OTHER `unknown` -> status `partial` unless the filer shows no intangibles purchase (AC: whether "Capital expenditures" labelled `PaymentsToAcquireProductiveAssets` with no separate intangible line may be treated as PP&E + software). `PaymentsForProceedsFromProductiveAssets` is net: anchor perimeter net, CX.DISPOSAL_PROCEEDS inside -> standardized only if proceeds are reported separately.
Fixtures: AMD 9M **752**; ArcBest 9M = 107,005K + 9,958K = **116,963K**, flagged "PP&E net of financed purchases" (AC); Aptiv 9M **489** partial pending the intangible ruling; Gilead 9M **358**.
Code fix bound to this: one capex concept feeds the statement row and FCF/FCF yield/capex-to-revenue.

### 5.3 `total_debt_std`: borrowings, and `total_debt_incl_fl_std`
Instant, USD, positive, consolidated, carrying amount.
| Slot | `total_debt_std` | `_incl_fl` | Reason | Tags |
|---|---|---|---|---|
| TD.SHORT_TERM (bank loans, CP, notes, revolver draws) | IN | IN | borrowing | `ShortTermBorrowings`, `CommercialPaper`, `LinesOfCreditCurrent`, `NotesPayableCurrent` (short-term notes only; see card) |
| TD.LTD_CURRENT | IN | IN | | `LongTermDebtCurrent` |
| TD.LTD_NONCURRENT | IN | IN | | `LongTermDebtNoncurrent` and its FASB children |
| TD.FINANCE_LEASE (current + noncurrent) | OUT | IN | lease policy (wave1: leases are not debt unless a separate policy is approved); C1 | `FinanceLeaseLiability*`; inside `LongTermDebtAndCapitalLeaseObligations*`, `DebtCurrent`, `DebtAndCapitalLeaseObligations` |
| TD.OPERATING_LEASE | OUT | OUT | not borrowing (CATO, ATEX ledger rows) | `OperatingLeaseLiability*` |
| TD.FHLB / bank funding | template | template | banks: funding, not debt; insurers AC | `AdvancesFromFederalHomeLoanBanks` |
| TD.MANDATORILY_REDEEMABLE_PREFERRED | OUT (AC) | OUT (AC) | equity-like instrument classified as liability | |
| TD.FACE_VALUE figures | never anchor | never | carrying amount only (AMZN, GOOG ledger row) | `DebtInstrumentFaceAmount`, `LongTermDebt` where it equals face value in the note |
Anchor rules: `DebtLongtermAndShorttermCombinedAmount` (filer's own total, PGR) covers TD.SHORT_TERM + LTD with TD.FINANCE_LEASE `unknown` unless the face or note says. `LongTermDebt` covers LTD_CURRENT + LTD_NONCURRENT (CSCO, TMO) and never sums with them. Combined lease tags cover TD.FINANCE_LEASE: `total_debt_std` is `complete` only when `FinanceLeaseLiability*` is filed for the same instant so it can be subtracted (AC must approve subtraction), else `partial` with reason COMBINED_LINE_ONLY ("long-term debt includes finance leases"), while `_incl_fl` is `complete`.
Fixtures: Walmart 2025-10-31: `total_debt_std` = 8,401 + 3,523 + 34,445 = **46,369**; `_incl_fl` = 46,369 + 842 + 5,916 = **53,127**; operating leases 15,297 never included. CVX: `_incl_fl` complete, `total_debt_std` partial unless the finance-lease amount is filed.
Code bound to this: split `DEBT_LTD_NONCURRENT`/`DEBT_LTD_CURRENT`/`DEBT_CURRENT_ALL` into lease-exclusive and lease-inclusive roles; store `path` and slot states.

### 5.4 `interest_expense_std`: gross interest expense recognized in profit or loss
Duration, USD, positive magnitude, consolidated.
| Slot | In/out | Reason | Tags |
|---|---|---|---|
| IE.DEBT (incl. amortization of discount and issuance cost) | IN | | `InterestExpenseDebt`; inside `InterestExpense`, `InterestExpenseNonoperating` |
| IE.FINANCE_LEASE | coupled C1: IN iff `total_debt_incl_fl` is the leverage denominator | consistency of coverage and leverage | `FinanceLeaseInterestExpense`; inside `InterestExpenseNonoperating` per FASB calc |
| IE.FEES (commitment, debt-related) | IN | cost of borrowing | `DebtRelatedCommitmentFeesAndDebtIssuanceCosts` |
| IE.INTEREST_INCOME | OUT, SEP `interest_income` | never net | net tags `InterestIncomeExpenseNet`, `InterestIncomeExpenseNonoperatingNet`, `InterestRevenueExpenseNet` are role `combined`: never this concept |
| IE.CAPITALIZED | OUT | not expensed (DHI ledger) | `InterestCostsIncurred`, `InterestCostsCapitalized` |
| IE.EXTINGUISHMENT | OUT | not interest | inside `InterestAndDebtExpense` (combined) |
| IE.OPERATING (rental fleet, captive finance, HTZ) | AC | operating for these models | `InterestExpenseOperating` |
| IE.CASH_PAID | never | cash vs expense (wave1 1.5) | `InterestPaidNet` |
Fixture: Walmart Q3: IE.DEBT 563, IE.FINANCE_LEASE 121; `interest_expense_std` = **563** or **684** depending on C1; "Interest, net" 591 is a different concept. Net-only filers: blank with NOT_SEPARATELY_DISCLOSED (data-team/27 D4 stays).

### 5.5 `operating_income`: reported, with perimeter flags (no standardized re-cut)
Duration, USD, economic sign, consolidated. **Proposal: do not compute a standardized operating income that removes gains, impairments or restructuring.** That is an "adjusted" (non-GAAP-style) number requiring line-by-line judgement (data-team/27 D1). Instead the perimeter record lists what the reported subtotal contains:
| Slot (flag) | Default | Census (FSDS, above the OI line) |
|---|---|---|
| OI.GAIN_LOSS_DISPOSAL | inside, flagged | 328 filings; PLD about 943.6M |
| OI.IMPAIRMENT | inside, flagged | 684 |
| OI.RESTRUCTURING | inside, flagged | 513 |
| OI.OTHER_OPERATING_INCOME | inside, flagged | 393 |
| OI.EQUITY_METHOD_INCOME | inside, flagged (AC: whether to treat as non-comparable) | 55 |
| OI.DA | inside (expected) | 1,419 show a D&A line above OI |
Anchor: `OperatingIncomeLoss` only where it is the face subtotal labelled operating income/loss; never for banks (BANR, PEBO); none for single-step statements (CVX, AJG, HTZ, GE; 89 + 398 filings). The arithmetic fallback (85-90% exact, data-team/27 D2) stays suppressed until its exactness gate exists. Screens can filter on flags ("operating income includes disposal gains").
EBITDA = reported operating income + `da_ebitda`, `complete` only when `da_ebitda` is complete and the D&A was deducted inside operating income (OI.DA not `not_present`); label "EBITDA (operating income + D&A)".

### 5.6 `revenue_std`: total revenues as presented
Duration, USD, positive, consolidated.
| Slot | In/out | Reason | Tags |
|---|---|---|---|
| RV.CONTRACT (ASC 606) | IN | | RCFC (slot, not anchor when a face total exists) |
| RV.LEASE | IN | lessors (AMT) | `OperatingLeaseLeaseIncome`, sales-type lease revenue |
| RV.OTHER_OPERATING (membership fees, franchise, regulatory true-ups / alternative revenue programs) | IN as presented inside the filer's total | Walmart 1,727; ITC (61) | `OtherIncome` when inside the revenue total, custom |
| RV.EXCISE_TAXES | AC (default OUT when presented as a deduction) | gross vs net of excise | `RevenueFromContractWithCustomerIncludingAssessedTax`, `ExciseAndSalesTaxes` |
| RV.NONOP_INSIDE_TOTAL (equity-method income, gains, interest income inside "Total revenues and other income") | OUT, subtract only with face values | CVX shape | `IncomeLossFromEquityMethodInvestments`, `GainsLossesOnSalesOfAssets`, `OtherNonoperatingIncome` |
Anchor rule replaces RCFC-first: the face line that is the revenue total wins; RCFC or `Revenues` is the anchor only by presentation. Fixtures: Walmart Q3 **179,496** (not 177,769); ITC Q3 **454** (not 515). Banks, BDCs, insurers: template definitions (`bank_revenue` = NII + noninterest income; BDC total investment income), never this concept.

### 5.7 Net income: three concepts, never one chain
| Concept | Definition | Anchor | Derivation allowed |
|---|---|---|---|
| `net_income_consolidated` | incl. NCI | `ProfitLoss` | parent + NCI when both reported |
| `net_income_parent` (feeds net margin, ROE, P/E checks) | attributable to parent | `NetIncomeLoss` | consolidated - NCI (FASB calc; FAC IS-Impute-10) when NCI is reported; never from available-to-common unless preferred and participating adjustments are reported as numeric zero (FAC IS-Impute-02, without its zero-means-missing flaw) |
| `net_income_common` (feeds EPS checks) | after preferred and participating | `NetIncomeLossAvailableToCommonStockholdersBasic` | parent - preferred - participating when reported |
Fixture: Walmart Q3: consolidated **6,088**, NCI +55, parent **6,143**. Census: 259 filings have `ProfitLoss` with no `NetIncomeLoss` on the face; today they flow into `net_income` as if parent. Never DEF 14A values (AEMD, JPM ledger rows). Not a standardization of perimeter: these are distinct attributions, so no AC needed for the split itself; AC only for the 259-type derivation when NCI is absent (is "no NCI line" evidence of zero NCI?).

### 5.8 Free cash flow inputs
`fcf_std` = `cfo_std` - `capex_std`, same company, period, filing and continuing-operations basis.
| Input decision | Proposal | AC? |
|---|---|---|
| CFO perimeter | continuing operations when the filer reports discontinued CFO separately (AMD 5,109 total includes 920 discontinued), else total; capex on the same basis | AC |
| Capex | `capex_std` (5.2), the same concept the statement row shows | via 5.2 |
| Finance-lease principal payments | `fcf_std` excludes them; variant `fcf_after_lease_principal_std` subtracts `FinanceLeasePrincipalPayments` only under C1 | AC (C1) |
| Interest paid, taxes paid | as classified under US GAAP (operating); no adjustment | no |
| SBC, working capital, acquisitions | no adjustment; acquisitions are not capex | no |
| Quarters | derive per input from YTD (allowlist, same slot states), then subtract | no (existing additive rule) |

### 5.9 Decisions that need the named accounting reviewer
| ID | Decision | My proposed default |
|---|---|---|
| C1 | Finance leases in leverage: is the screen's debt `total_debt_std` or `_incl_fl`? Coupled: finance-lease ROU amortization in D&A, finance-lease interest in interest expense, lease principal in FCF | `_incl_fl` for EV, net debt and debt/EBITDA with ROU amortization and lease interest included; `total_debt_std` shown as "borrowings" |
| C2 | Subtracting a separately filed finance-lease amount from a combined lease-inclusive debt tag | allowed only when the filer's own note or calc shows the combined line equals debt + that amount |
| C3 | Depletion in D&A | IN |
| C4 | Capitalized software in capex and its amortization in D&A | IN both |
| C5 | Intangible purchases: in capex or separate | separate |
| C6 | `PaymentsToAcquireProductiveAssets` "Capital expenditures" with no separate intangibles line | accept as PP&E + software, flagged |
| C7 | Label "D&A" on a `Depreciation` tag as evidence that amortization is inside | accept when only intangibles are shown separately |
| C8 | Rental-fleet purchases and operating interest for rental/captive-finance | separate template |
| C9 | Excise taxes in revenue | net of excise where presented as a deduction |
| C10 | Equity-method income inside revenue or operating income | subtract from revenue when on the face; flag in OI |
| C11 | Content, regulatory, contract-cost amortization | OUT |
| C12 | ARO accretion | OUT |
| C13 | Continuing vs total CFO for FCF | continuing when separable |
| C14 | Treating a missing NCI line as zero NCI | no; status partial |
| C15 | Mandatorily redeemable preferred, FHLB advances for insurers | OUT; insurers case by case |

---

## 6. Deliverable 3: reported vs standardized, perimeter display, screens

**Which number where**
| Surface | Shows | Rule |
|---|---|---|
| Statement tables ("as filed" view) | reported value with the filer's own label and accession | always, whatever the standardized status |
| Key metrics, ratios, screens, rankings, peer comparisons | standardized value only | status must be `complete` for every input |
| Standardized equals reported | one number, chip "matches standard definition" | |
| Standardized differs | standardized number, chip "standardized"; tooltip lists each slot added or removed with its value, tag, label and R-file locator; link to the reported line | e.g. AMD: "Company line 556 (Depreciation and amortization) + 1,697 amortization of acquisition-related intangibles, R6 = 2,253" |
| Status `partial` | blank in ratios and screens with the reason ("Capex may include intangible purchases (not separately disclosed)"); reported line still visible in statements | never a fallback to the reported number in a ratio |
| Template not applicable | "Not reported by banks" style reason | `not_applicable`, out of the denominator only with filing evidence (data-team/11 policy) |

**Exposing the perimeter**
- Every standardized value links to its perimeter record: slot table (state, value, evidence), definition version, approval status, reviewer.
- Perimeter flags become screen fields (`oi_includes_disposal_gains`, `debt_includes_finance_leases`, `capex_net_of_disposals`), so a user can include or exclude them explicitly.
- Methodology page: one block per definition with its slots and reasons, generated from `composite_definition`/`composite_slot`, never hand-written prose that can drift.

**How this protects screens**
1. A screen compares numbers built from the same slot set, so "EV/EBITDA < 10" means the same thing for AMD (with intangible amortization) and Jabil.
2. Companies whose perimeter is incomplete fall into the existing visible `excluded_missing_data` list with the slot reason (doc 14), instead of passing or failing on a non-comparable number.
3. Coupled decisions are enforced in code: a metric whose numerator and denominator depend on C1 reads both from the same C1 variant; a mixed read is a test failure.
4. Time series use one definition version; a tag switch between years no longer changes the meaning (the slot is the same even if the tag changes).
5. A change of definition version re-runs dependents and publishes a diff, never a silent overwrite.

---

## 7. Deliverable 4: edge cases

- **Banks and thrifts:** `revenue_std`, `capex_std`, `da_ebitda`, EBITDA, `total_debt_std` and `interest_expense_std` are `not_applicable` under the commercial template; bank template concepts instead (NII, noninterest income/expense, provision, deposits, borrowings incl. FHLB). Detect banks by filing evidence (deposits + `NoninterestExpense`), not SIC alone (crypto miners sit in 6000-6199; tag inbox).
- **Insurers:** no gross profit or operating income; `PGR` uses `InterestAndDividendIncomeOperating` for investment income; interest expense inside `BenefitsLossesAndExpenses`; DAC amortization is never D&A (C11). Separate template.
- **REITs:** D&A is large and real-estate depreciation is the business; EBITDA allowed but FFO is non-GAAP and not built; capex splits into acquisitions, development and recurring improvements (C template); `OperatingIncomeLoss` can include disposition gains (PLD), flagged.
- **BDCs and funds:** no revenue, capex, D&A; total investment income concept exists (`bdc_total_investment_income`).
- **Utilities:** regulatory asset amortization and alternative revenue programs (ITC true-up); custom capex tags are common (NEE, data-team/33); D&A often includes nuclear fuel amortization (C11).
- **Finance leases:** ASC 842 (2019+ for most; later for emerging growth companies, data-team/22) changes tags; pre-842 "capital lease" tags map to the same TD.FINANCE_LEASE slot. Coupled decision C1 governs four concepts at once.
- **Capitalized software:** both capex (CX.SOFTWARE) and D&A (DA.AMORT_SOFTWARE), three tags for the outflow (`PaymentsToAcquireSoftware`, `PaymentsToDevelopSoftware`, `PaymentsForSoftware`).
- **Sign conventions:** store the fact sign as filed; slots carry an arithmetic sign in the definition; capex and interest are stored as positive magnitudes of outflows/expenses only after checking the tag's balance type; a negative where the element should not be negative (DQC_0015) is a quarantine, never a flip. R-file negated labels (ANDE, BBW) mean a rendered number is compared through the row's negation.
- **Discontinued operations:** continuing-ops slots; total-tag cash-flow values used for a continuing subtotal (MGNC, LRDC) are detected by the presence of discontinued-ops lines.
- **Dimensions and context errors:** only undimensioned facts can be anchors or slots; a quarterly value that duplicates a member value (GE FY2016) is a context error.
- **52/53-week years, transition periods:** slot derivations check period lengths from dates.
- **Restatements:** the perimeter is built from the filing that supplies the value; a later filing that re-presents the period produces a new perimeter row, and the latest-filed policy picks between them.
- **Custom tags:** a custom line enters a slot only through presentation plus filer calc evidence (it rolls into a standard parent) or a reviewed company-scoped rule; never globally.

## 8. Deliverable 5: what not to standardize
1. Per-share data and share counts (EPS, weighted shares, DPS): take as filed, never compose or subtract.
2. Non-GAAP adjustments: no "adjusted EBITDA", no operating income stripped of impairments or one-offs, no FFO/AFFO computed by us.
3. Net lines into gross: never gross up "interest, net" or "payable and accrued" by estimating the missing part.
4. Cash into accrual or back: interest paid is not interest expense; taxes paid are not tax expense.
5. Operating leases into debt.
6. Financial-company statements into the commercial template (banks, insurers, BDCs, broker-dealers).
7. Segment or dimensional figures into consolidated totals.
8. Principal-vs-agent (gross vs net) revenue presentation: accept as reported.
9. Restated and as-filed values merged into one series without a basis label.
10. Any slot whose state is unknown: no inference from tag name, frequency, vendor values (yfinance) or a "close enough" tie.
11. Zero from absence: a missing slot is `unknown`, a reported zero is zero.

---

## 9. Build plan, tests and acceptance (for the engineer)

Order (each step dry-run first, Verifier sample with zero wrong rows, then live; no step publishes a perimeter-changing value before the accountant rules on its C-items):
1. **Schema and definitions** (`composite_definition`, `composite_slot`, `composite_tag_role`, `company_perimeter`, `company_perimeter_slot`), seeded with the eight definitions at status `proposed`. Migration number claimed in doc 53 at that time.
2. **Structure input**: face presentation and filer calculation relationships per filing for the top 1,000 (FSDS `pre`/`num`, FSN `cal`, streamed and deleted per quarter; doc 39 step 2). Without `cal`, slots in `may_cover_slots` stay `unknown`, which is safe.
3. **Composer** `mapper/composition/` with a registry per concept (`compose_da`, `compose_capex`, `compose_debt`, `compose_interest`, `compose_revenue`, `compose_net_income`, `flag_operating_income`), pure functions over an in-memory filing bundle, set-based loads, batched writes (pipeline/CLAUDE.md conventions).
4. **Immediate code fixes that need no new definition** (reported to the owners; not done here): FCF metrics read the same capex concept the statement shows; store `compute_total_debt` path; split lease-inclusive tags out of the lease-exclusive debt roles; stop the max-of-two D&A rule from publishing into ratios until `da_ebitda` exists.
5. **Switch metrics** family by family to `_std` inputs, with a before/after diff per company.

Tests (fixtures from section 2; synthetic only where marked):
- `compose_da(AMD R6 9M)` -> 2,253, status complete; Aptiv -> 741 and the 7 debt-cost amortization never included; Gilead -> partial (`AdjustmentForAmortization` unknown); Jabil -> 674 from CF, never the IS 62.
- `compose_capex(ArcBest)` -> 116,963K with flag `net_of_financings`; Aptiv -> partial until C6; AMD -> 752.
- `compose_debt(Walmart 2025-10-31)` -> 46,369 and `_incl_fl` 53,127; operating leases never enter; CVX -> `_incl_fl` complete, `total_debt_std` partial.
- `compose_interest(Walmart Q3)` -> 563 / 684 by C1; `InterestIncomeExpenseNonoperatingNet` never resolves into it.
- `compose_revenue(Walmart Q3)` -> 179,496; ITC -> 454.
- net income Walmart -> consolidated 6,088, parent 6,143; a `ProfitLoss`-only synthetic case with no NCI line -> parent partial.
- Coupling test: any metric reading debt and EBITDA/interest uses the same C1 variant.
- Determinism: same inputs and definition version -> byte-identical outputs.

Acceptance: the Verifier's stratified sample (data-team/24 item 9) on 10 companies x 3 concepts first (doc 39 step 3), then 30 per concept; zero wrong standardized values; every `partial` has a reason a user can read. Stop rule from doc 39 applies: if filer calc evidence explains fewer than half of the "values differ" cases, stop and report.

Impact query plan (NOT_RUN; database unavailable at 17 connections): per concept, count company-periods by today's recipe outcome vs the composer's status, split by template and by the display window (>= 2015-01-01), and list every company whose screen membership changes for the existing screen templates.

---

## 10. Commands run, evidence, limits

Commands actually run (all read-only):
- Read: BRIEF.md; data-team 20, 21, 22, 11, 03, 24, 27, 33 (grep), 34 (grep), strategy 37 (grep), 38, 39; tags/00-README, INDEX, cards (debt, interest, operating-income, revenue, net-income-and-shares, cash), company-quirks, feedback-inbox; `doc/data-moat/decisions.md` and `wave1-canonical-definitions.md` (grep); `mapper/concepts.py`, `expanded_concepts.py`, `concept_fallback.py`, `definitions.py`, `expanded_definitions.py` (part), `conflict_resolution.py` (lines 80-105), grep of `ttm.py`, `price_metrics.py`, `calculate.py`; migrations 0004 and 0080 (grep); `git log` on the three mapper modules; `mind search`.
- FSDS 2025q4 (brief's extracted copy): scratch scripts `extract.py`, `compose.py`, `ours.py` under `/private/tmp/claude-501/-Users-vikash-scrooner/99c20ae4-2938-4dd5-8ec6-924194f63d67/scratchpad/r3/` run with `python3 -I`.
- sec.gov: 9 R-files (AMD R6, Walmart R2/R4, ArcBest R8, Jabil R5/R8, ITC R4, Aptiv R6, Gilead R8) with the declared User-Agent, about 2 per second.
- Web: FASB 2025 calc linkbases (3 files, 0.8 MB); XBRL US / Hoffman FAC pages (5); edgartools docs; Lyle-Siano-Yohn PDF (text extracted); Calcbench (403); search engines (blocked).
- DB: one `select count(*) from pg_stat_activity` = 17, so no queries.
- Downloads deleted after use (R-files, FAC pages, FASB linkbases, PDF text); total well under 300 MB.

Untested scope: our stored values for these companies (database not queried); quarters other than 2025q4 and pre-2018 eras; FSN `cal` evidence (not downloaded); the top-1000 subset; whether companyfacts carries note-level D&A/capex tags for the face-composed filers; Compustat/FactSet/Morningstar item definitions (not confirmed); how many screens change.

## 11. Next actions
1. Verifier: review sections 4-5 against original filings before reading my rationale; start with AMD, Aptiv, Walmart, ArcBest.
2. Founder: name the accounting reviewer; C1 (lease coupling) is the highest-impact single ruling.
3. Data Engineer: FSN `cal` loader pilot for the top 1,000 (doc 39 step 2), which turns `unknown` slots into evidence.
4. Owners of `definitions.py` / `price_metrics.py` / `concept_fallback.py`: the four no-definition fixes in 9.4 (FCF capex mismatch first; it is a wrong-value class today).
5. Tag Mapper: coexistence checks for `PaymentsToAcquireProductiveAssets`, `PaymentsToDevelopSoftware`, `PaymentsForSoftware`, `OtherDepreciationAndAmortization`, `InterestExpenseNonoperating` as slot carriers (not as global concept mappings).
