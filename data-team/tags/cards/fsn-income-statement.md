# Card family: FSN income statement, per-share and tax tags (Tag Expert, 2026-11-11)
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Founder order 2026-11-11: "FSN FOR LEARNING - which tag is what. SEC FOR MAPPING." This card says what each of 22 tags is on the top-1,000 faces. It is the seed for `analytics.company_tag_map`. Machine-readable rows: `data-team/tags/library/fsn-income-statement.csv`. It extends `revenue.md`, `operating-income.md`, `net-income-and-shares.md` and `interest.md`. Nothing in those cards is contradicted unless a section says CORRECTS.

## Method and limits (read first)
- **Definitions:** `https://xbrl.fasb.org/us-gaap/2025/elts/us-gaap-doc-2025.xml`, read 2026-11-11. Period type and balance come from `fsn.tag` (us-gaap/2025 rows). Every tag is a duration item. EPS and share tags have no balance.
- **FSN population:** `fsn.filing` holds the 1,001 top-1,000 companies, 42,052 filings with period >= 2015-01-01 (10-K, 10-Q and amendments).
  - Counts = distinct companies with the tag on a face statement (`fsn.line`, which is FSN pre.txt; notes are not in it).
  - Label counts = companies per normalised plabel on stmt IS, non-parenthetical.
  - "Latest 10-K face" = each company's newest 10-K, using its IS report with the most of the 22 tags (1,000 companies).
  - Families come from `core.company.sic_code`: bank = 6021/6022/6029/6035/6036 (41); insurer = 6311-6411 (55); REIT = 6798 (53); utility = 49xx (57); other financial (62); general (729).
- **Calc parents:** `fsn.calc_arc` for the 920 FY2024 10-Ks only. These are all calc groups, so note groups are included (for example the domestic/foreign pretax split in the tax note).
- **Current mapping:** `fsn.line_map` for 10-Ks with period >= 2024-06-30.
- **Filings:** 18 R pages opened on sec.gov in 19 requests (about 1 per second, declared User-Agent): AAPL, AMZN, AVGO, AFG, AIG, CPB, DOC (Healthpeak 2020 10-Q), FCNCA, GPC, HST, INTU, LEN, MRNA, NDAQ, SBUX, UNH, VRSN and WTFC. The first DOC request used the wrong CIK and returned 404. Accessions are in the CSV.
- **Evidence classes:** a claim about a named filing is FILING-CHECKED. Population counts are DATA-INFERRED (FSN store).
- **DB use:** one connection. `pg_stat_activity` showed 16 rows, but 11 were Supabase background or idle system sessions; client sessions were about 5. The run went ahead under the order's explicit DB instruction; this is recorded here as a deviation from the 12-connection rule.

## Structural facts (latest 10-K face, 1,000 companies, DATA-INFERRED)
| Fact | Count |
|---|---|
| Revenues and RCFC both printed on the same face | 70 (RCFC is the lower line only at UNH, where it is a component) |
| Neither Revenues nor RCFC on the face | 107 (29 banks, 48 general that use other tags such as CostOfRevenue-era SalesRevenue, RegulatedAndUnregulated, custom) |
| ProfitLoss and NetIncomeLoss both / NetIncomeLoss only / ProfitLoss only / neither | 411 / 493 / 81 / 15 |
| NCI line printed with no ProfitLoss line | 9 (MAS, STZ, ARMK, MMM, MTCH, LIN, WFC, WMG, MDLN) |
| InterestExpense: below OI / above OI / no OI on the face | 112 / 1 (AFG) / 62 |
| InterestExpenseNonoperating: below OI / no OI | 348 / 31 |
| Equity-method line: above OI / pretax zone / after tax | 25 / 130 / 86 |
| No standard pretax tag on the face | 189 (calc-position rule needed) |
| No EarningsPerShareDiluted on the face | 33 (VRSN, HAL, ABNB on the continuing-ops tag; BRK-A per class; GPC and LEN not printed) |
| NonoperatingIncomeExpense and OtherNonoperatingIncomeExpense on the same face | 188 |
| OperatingIncomeLoss at banks | 0 of 41 |
| GrossProfit outside general companies | 7 |

## Per tag
Format for each tag: meaning (FASB 2025) / FSN labels (companies) / statement and calc parent (FY2024 10-K calc) / decision / exceptions / era / evidence.

### EarningsPerShareDiluted / EarningsPerShareBasic
- **Meaning.** Net income per common share or unit (diluted assumes all dilutive potential shares). Duration, no balance.
- **Labels: 1,599 / 1,576 distinct.**
  - Diluted: "diluted (in dollars per share)" 382, "diluted" 223, "diluted (in usd per share)" 131.
  - Basic: "basic (in dollars per share)" 388, "basic" 224.
  - Class or unit labels: 34 / 35 companies (PLD, BXP, FR, DLR "per share/unit"; APO, GOOG, BKR, ACI "Class A").
  - "basic and diluted" on one tag: 7 / 13 (KYMR, MDB, HALO, LYV, NRG).
- **Statement.** IS 987 / 988 companies; CI 13 (combined statements). Calc children: IncomeLossFromContinuingOperationsPer*Share (90) plus discontinued per-share (69-71). There is no calc parent.
- **Decision.** Map to `diluted_eps_resolved` / `basic_eps_resolved`, as printed and never derived (rule).
- **Exceptions.** These need company-scoped rows, never derivation:
  - VRSN prints "Earnings per Share, Basic/Diluted" 8.83 / 8.81 on `IncomeLossFromContinuingOperationsPerBasicShare/PerDilutedShare` and files no EarningsPerShare* fact (0001014473-26-000006 R5, FILING-CHECKED). The same holds at HAL (0000045012-26-000015 R3 FSN lines 25-26) and ABNB (card).
  - LEN FY2025 10-K prints only "Basic earnings per share" 7.98, with no diluted row (0001628280-26-003870 R5, FILING-CHECKED). Diluted is blank with a reason unless the EPS note prints it.
  - GPC FY2025 10-K prints no EPS on the income statement face (0000040987-26-000003 R5, FILING-CHECKED). Look in the EPS note before calling it not presented.
  - AIG prints continuing-ops and net EPS on separate rows. The net row is EarningsPerShare*, 5.48 / 5.43 (0000005272-26-000023 R5).
- **Era.** All years. The combined BasicAndDiluted tag is era-limited (card).
- **Evidence.** FILING-CHECKED (AAPL 7.49 / 7.46 R3, AMZN 7.29 / 7.17 R4, VRSN, LEN, GPC, AIG).

### WeightedAverageNumberOfDilutedSharesOutstanding / ...SharesOutstandingBasic
- **Meaning.** Average shares used in diluted or basic EPS, time-weighted.
- **Labels.** "diluted (in shares)" 470, "diluted" 257; basic 475 / 261. "Basic and diluted" on the basic tag at 15 (UHAL, MDB, ROL, KYMR). Per class or unit at 28-30.
- **Statement.** IS 842 / 838. Calc: Basic is a child of Diluted at 680 FY2024 filers; incremental-share children at 417.
- **Decision.** Excluded: there is no canonical concept (`shares_outstanding` is the BS instant). Proposal: new concepts `weighted_basic_shares` and `weighted_diluted_shares`, mapped as filed.
- **Exceptions.** 204 latest 10-K faces print no diluted share line; the count is in the EPS note.
- **Evidence.** FILING-CHECKED: AAPL 14,948,500K / 15,004,697K; AFG 83.5M / 83.5M; FCNCA 13,002,455.

### NetIncomeLoss
- **Meaning.** Profit or loss net of tax attributable to the parent. Credit.
- **Labels: 1,361 distinct.** "net income" 498, "net income (loss)" 327, "net loss" 198, "net (loss) income" 127, "net earnings" 66.
  - "attributable to common stockholders/shareholders" at 91 companies (PAG, VICI, CPT): still the parent line.
  - "consolidated net income attributable to X" (WMT, AA, SO).
  - Combined "net income and comprehensive income" at 18.
- **Statement.** IS 968, EQ 709, CF 626, CI 559. Calc parents: ComprehensiveIncomeNetOfTax 400, NetCashProvidedByOperating 345, NetIncomeLossAvailableToCommonStockholdersBasic 169. Children: tax (-) 395, ProfitLoss 380, NCI (-) 340, pretax 334.
- **Decision.** Map to `net_income_resolved` from the IS (or combined IS+CI) face only. The CI/EQ/CF copies are start lines.
- **Evidence.** FILING-CHECKED: AAPL 112,010; UNH 12,056; HST 765; LEN 2,078,179K; NDAQ 1,788; SBUX 1,856.4.

### ProfitLoss
- **Meaning.** Consolidated profit or loss including NCI.
- **Labels: 158 distinct.** "net income" 434, "net income (loss)" 314, "consolidated net income" 24, "including noncontrolling interest(s)" variants at 93 companies.
- **Statement. Home is the CF (695 companies)**, then IS 621, CI 535, EQ 519; 99 companies use it only off the IS. Calc parents: CFO 489, comprehensive income incl. NCI 394, NetIncomeLoss 380.
- **Decision.** Map to `net_income_resolved` ONLY in filings whose IS face prints no NetIncomeLoss line and no NCI line. Examples:
  - AVGO 23,126 (0001730168-25-000121 R5), with no NCI row.
  - VRSN 825.7, no NCI.
  - MA, V, TTEK, M, PH, ITW.
  - In all, 81 latest 10-Ks print ProfitLoss without NetIncomeLoss.
- **Exceptions.** Where NetIncomeLoss is printed, ProfitLoss is consolidated and is excluded:
  - UNH 0000731766-26-000062 R5: ProfitLoss "Net earnings" 12,807, NCI (751), NetIncomeLoss 12,056.
  - HST 776 vs 765; LEN; SBUX 1,856.7 vs 1,856.4; NDAQ 1,787 vs 1,788; AIG 3,097 vs 3,096.
  - The CF start line is never the source.
- **Evidence.** FILING-CHECKED.

### NetIncomeLossAttributableToNoncontrollingInterest
- **Meaning.** NCI share of net income. Debit.
- **Labels: 606 distinct.** "net income attributable to noncontrolling interests" 103 and the "less:" variant 103. Redeemable-NCI variants at 31 (EFX, TSLA, GIS). OP-unit variants (GLPI, STAG).
- **Statement.** IS 560. Calc child (-) of NetIncomeLoss at 340.
- **Decision.** Excluded: no concept; it is a detail line of a printed total (agrees with the Mac library).
- **Exceptions.** FE's 2018 10-K labels it "income allocated to preferred stockholders" (0001031296-19-000010 R2, from FSN only, not opened: DATA-INFERRED).
- **Evidence.** FILING-CHECKED: UNH (751), HST (11), NDAQ 1.

### IncomeTaxExpenseBenefit
- **Meaning.** Current plus deferred income tax for continuing operations. Debit.
- **Labels: 494 distinct.** "provision for income taxes" 388, "income tax expense" 380, "income tax expense (benefit)" 253, "income tax benefit" 155. Labels with "(expense) benefit" order at 96+ companies display it negated.
- **Statement.** IS 978. Calc child (-) of NetIncomeLoss 395 and ProfitLoss 355. Children are current and deferred tax plus the rate reconciliation (note groups).
- **Decision.** Map to `income_tax_expense_resolved`, using the fact sign. AMZN's R page shows (19,087) for an expense of 19,087.
- **Exceptions.** Wider perimeters to flag: "income and mining tax" (NEM, CDE, HL, SSRM) and "income and other tax" (VMRK, ADC, SPG 2016). SCCO is a two-line sum (cloud rule 13).
- **Evidence.** FILING-CHECKED: AAPL 20,719; GPC (13,777) benefit; HST 42.

### IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest
- **Meaning.** Continuing-ops income before tax and NCI, *including* equity-method income.
- **Labels: 433 distinct.** "income before income taxes" 484, "income (loss) before income taxes" 307, "loss before income taxes" 167, "income from continuing operations before income taxes" 111.
- **Statement.** IS 887. Calc parents: NetIncomeLoss 334, ProfitLoss 291. Children: OI 567, OtherNonop 293, Nonop 225, InterestExpenseNonoperating (-) 168.
- **Decision.** Map to `income_before_tax_resolved`. Choose the line by calc position beside the tax line (ruling), not by tag.
- **Exceptions.**
  - DOC (Healthpeak) 2020 10-Q 0001628280-20-015363 R4 uses this tag on two face rows: "Income (loss) before income taxes and equity income" (15,927) and "Equity income (loss) from unconsolidated joint ventures" (19,480). FILING-CHECKED. A tag-only pick is ambiguous.
  - Labels "before ... equity in earnings" (BRKR, AMCR, MELI, DKNG, FORM, VMI, EXR) carry a narrower perimeter than the definition.
  - 189 latest 10-Ks print pretax on another tag.
- **Evidence.** FILING-CHECKED: AAPL 132,729; AMZN 97,311; CPB 529; DOC.

### OperatingIncomeLoss
- **Meaning.** Operating revenues less operating expenses.
- **Labels: 111 distinct.** "operating income" 442, "operating income (loss)" 273, "income from operations" 191, "operating profit" 51.
- **Statement.** IS 794: 0 banks, 13 insurers / managed care (UNH, CI, HUM, CNC, MOH, AON, WTW, ERIE, MKL, RYAN, OSCR, MRSH, AFG). Calc parents: pretax 567, the ...MinorityInterest... pretax 72, ProfitLoss 19, NetIncomeLoss 15. Children: GrossProfit 300, CostsAndExpenses (-) 254, RCFC 213, SG&A (-) 199.
- **Decision.** Map to `operating_income_resolved` for non-financial filers and the insurers above that print it.
- **Exceptions.**
  - AFG "Earnings before income taxes" 1,073: interest charges 80 sit above it (0001042046-26-000010 R5, FILING-CHECKED). It is pretax: excluded. ELS likewise (card).
  - EBIT lines: CPB "Earnings before interest and taxes" 852 = 9,744 - 8,892, where total costs include "Other expenses / (income)" 171 on OtherNonoperatingIncomeExpense (0000016732-26-000026 R4, FILING-CHECKED). BALL, TFX, CSL, OC and ATI carry the same label (DATA-INFERRED). Map only with a flag: the line includes non-operating items.
  - BIO "Segment profit (loss)": not opened.
  - SBUX OI 2,936.6 includes "Income from equity investees" 247.8 (R3). That is the company's own presentation.
  - All of these are currently mapped in `fsn.line_map` (rule is.operating_income_line@1).
- **Evidence.** FILING-CHECKED.

### RevenueFromContractWithCustomerExcludingAssessedTax (RCFC)
- **Meaning.** ASC 606 revenue, excluding sales, VAT and excise taxes. The element starts in us-gaap 2017 (no older fsn.tag version).
- **Labels: 293 distinct.** "net sales" 158, "revenue" 153, "revenues" 120, "total revenues" 86, "total revenue" 73.
  - "Noninterest income" (SSB, FCNCA, UMBF).
  - Fee lines at 24 companies (KKR, CG, NTRS, UDR, EXR, CPT).
  - Product/service subsets at 45.
- **Statement.** IS 676. Calc parents: GrossProfit 235, OI 213, Revenues 103, NetIncomeLoss 26, NoninterestIncome 14 (banks).
- **Decision.** Map to `revenue_sanity_resolved` when it is the face top line (AAPL 416,161; AMZN 716,924; AVGO 63,887; GPC 24,300,141K; MRNA 1,944,000K; NDAQ 8,262; HST 6,114).
- **Exceptions.**
  - Excluded where a Revenues total is printed on the same face: 70 companies, for example UNH RCFC "Revenue from Products and Services" 53,380 inside Revenues 447,567 (R5).
  - Excluded at banks and for REIT fee lines. **These lines are mapped to revenue in `fsn.line_map` today: CFR "Service charges on deposit accounts", NTRS "Trust, Investment and Other Servicing Fees", FCNCA and SSB "Noninterest income", WFC "Fee income", BPOP "Net fees", UDR "Joint venture management and other fees".**
  - FCNCA's RCFC appears on the R page only as dimension-member rows (266, 241, ...; 0000798941-26-000015 R5, FILING-CHECKED).
- **Era.** From the ASC 606 year (2018 for most).

### Revenues
- **Meaning.** Revenue from goods, services, premiums or other earning activities; includes interest income *before* interest expense.
- **Labels: 124 distinct.** "total revenues" 213, "revenues" 166, "net sales" 83, "total operating revenues" 33.
  - Labels that add other income at 19 companies (CVX, XOM, RRC, SM, MPLX, WES, DDS).
  - "net of interest expense" at BAC and C.
  - "Total" at L, EOG, CNP.
- **Statement.** IS 620: insurers 51 of 55, REITs 39, utilities 41, banks 5. Calc children: RCFC 103, OtherIncome 57, PremiumsEarnedNet 45, NetInvestmentIncome 40.
- **Decision.** Map to `revenue_sanity_resolved` as the face top line as printed (ruling).
- **Exceptions.**
  - Totals that add other income: take the revenue line above (COP ruling, cloud rule 2).
  - Banks with no printed total: NII + noninterest income (cloud rule 11).
- **Evidence.** FILING-CHECKED: UNH 447,567; INTU 21,448; SBUX 37,184.4; LEN 34,186,934K; AFG 8,174.

### CostOfGoodsAndServicesSold
- **Meaning.** Cost of goods and services sold, excluding financial-services costs.
- **Labels: 308 distinct.** "cost of sales" 182, "cost of goods sold" 77, "cost of goods and services sold" 75, "cost of revenue" 62. "Exclusive of D&A" wording at 42 companies.
  - Opex-like labels at 16: SRE "Operating expenses", HST and DVN "Expenses", WELL "Property operating expenses", RCL "Total cruise operating expenses", DAR, WAT.
- **Statement.** IS 575. Calc parents: GrossProfit (-) 220, CostsAndExpenses 144, OI (-) 48.
- **Decision.** Map to `cost_of_revenue_resolved` for the line directly above gross profit, or the line labelled cost of sales (ruling LMT/BA).
- **Exceptions.**
  - **HST: the tag appears only on dimension-member rows "Expenses" (906, 1,224, 1,466 ...); the face total is CostsAndExpenses 5,259 (0001070750-26-000054 R5, FILING-CHECKED).** The FSN line is mapped to cost_of_revenue today.
  - REIT and utility "operating expenses" lines (SRE, WELL, DOC 2020 "Operating" 314,292, AHR, MAC): excluded (the template has cost of revenue OUT for these sectors).
  - NDAQ "Transaction-based expenses" (3,013): an exchange cost, and a broker-template call.
  - Insurer product costs (UNH 50,655 "Cost of products sold", ELV, CI) are components, not total cost.

### GrossProfit
- **Meaning.** Revenue less cost of goods and services sold.
- **Labels: 26 distinct.** "gross profit" 361, "gross margin" 45.
  - Odd labels: NDAQ "Revenues less transaction-based expenses", CBOE "Revenues less cost of revenues", ICE 2020, SNEX "Operating revenues", FCFS "Net revenue", AES and DPZ "Operating margin", OKE "Net margin", SCI and NYT "Operating profit", NI 2019 "Total Operating Revenues".
- **Statement.** IS 409, of which 373 general. Calc parent: OI 300.
- **Decision.** Map to `gross_profit_resolved` where the label is gross profit or gross margin.
- **Exceptions.** Exchange and broker net revenue on this tag is excluded (broker template GP OUT). NDAQ 5,249 is FILING-CHECKED (R5). NDAQ, SNEX, CBOE and AES are mapped today.
- **Evidence.** FILING-CHECKED: AAPL 195,201; GPC 8,940,698K; AVGO 43,294.

### CostsAndExpenses
- **Meaning.** Total costs of sales and operating expenses.
- **Labels: 62 distinct.** "total operating expenses" 134, "total costs and expenses" 102, "total expenses" 54. "Total costs and other deductions" (CVX, XOM). "Total benefits and expenses" (AMP).
- **Statement.** IS 366. Calc parent: OI (-) 254.
- **Decision.** Excluded. Never `operating_expenses` and never used to derive OI. Under the "total operating expenses" label it includes cost of sales:
  - AMZN 636,949 includes cost of sales 356,414 (R4).
  - MRNA 5,018,000K includes COGS 868,000K (R5).
  - CPB 8,892 includes other expenses / (income) 171.
  - Interest is inside at CVX, XOM, GE and AJG (card).
- **Evidence.** FILING-CHECKED. Agrees with the Mac library (total_costs_incl_cost_of_revenue).

### SellingGeneralAndAdministrativeExpense
- **Labels: 231 distinct.** SG&A wordings at 487; marketing/administrative variants (JNJ, LLY, INTC, STX).
- **Statement.** IS 521. Calc parents: OI (-) 199, CostsAndExpenses 138, OperatingExpenses 73, BenefitsLossesAndExpenses 11 (insurers).
- **Decision.** Map to `sga_expense` for non-financial filers.
- **Exceptions.** Insurers use the tag for broader lines; excluded for the insurer template:
  - UNH "Operating costs" 59,592 (R5).
  - AIG "General operating and other expenses" 5,053 (R5).
  - AFG "Commissions and other underwriting expenses" 2,059 (R5).
  - AFL "Insurance and other expenses".
  - All FILING-CHECKED except AFL.

### GeneralAndAdministrativeExpense
- **Labels: 133 distinct.** "general and administrative" 249. The full SG&A label sits on this tag at 9 companies: MRNA "Selling, general and administrative" 1,018,000K (R5, FILING-CHECKED), INSM, IOVA, CELH, DINO, JEF.
- **Statement.** IS 360, REITs 47. Calc parents: CostsAndExpenses 125, OperatingExpenses 108.
- **Decision.** Excluded as a component (agrees with the Mac library). Map to `sga_expense` only where the label is SG&A and no SG&A line exists. A REIT's G&A as its SG&A row is a sector call.

### InterestExpense
- **Meaning.** Interest expense, operating and nonoperating.
- **Labels: 278 distinct.** "interest expense" 542, "interest expense, net" 88, "total interest expense" 43 (banks).
  - Net of interest income: PBF, JLL, RMD, VRT, DDS, ZETA, TDY, CASY "Interest, net".
  - Net of capitalized interest: 11+.
- **Statement.** IS 695. Calc parents: pretax (-) 105, CostsAndExpenses 25, BenefitsLossesAndExpenses 18.
- **Decision.** Map to `interest_expense_resolved` as the gross expensed amount. Bank "Total interest expense" (WTFC 1,503,981, R5, FILING-CHECKED) is the bank row.
- **Exceptions.**
  - Net-of-interest-income labels: combined.
  - "Net of capitalized interest": map (SCCO ruling).
  - AFG puts it above its pretax-labelled OI.
- **Era.** Many companies move to InterestExpenseNonoperating or InterestExpenseOperating in 2024+ schemas (interest card).

### InterestExpenseNonoperating
- **Meaning.** Interest expense classified as nonoperating. **The element exists only in fsn.tag versions us-gaap/2024-2026**, which confirms the interest card.
- **Labels: 58 distinct.** "interest expense" 329, "interest expense, net" 56.
- **Statement.** IS 423, below OI in every latest 10-K that has OI (348). Calc parents: pretax (-) 168, NonoperatingIncomeExpense (-) 127.
- **Decision.** Map to `interest_expense_resolved` (2024+). Examples: AMZN 2,274; AVGO 3,210; NDAQ 367 beside a separate interest income 39; HST 235.
- **Exceptions.** "Interest expense, net" is combined unless the note shows it is gross. GPC 163,506K has no interest income line on its face (R5, FILING-CHECKED), so the net includes interest income. EQT, AAL, MP, CHDN and LIN carry the same label.

### OtherNonoperatingIncomeExpense
- **Meaning.** Nonoperating income (expense) classified as other.
- **Labels: 451 distinct.** "other income, net" 279, "other income (expense), net" 259, "other expense, net" 209. "Interest and other income, net" at INTU, VIAV, CMG, AMAT and PCAR.
- **Statement.** IS 674. Calc parents: pretax 293, NonoperatingIncomeExpense 201.
- **Decision.** Map to `other_income_expense_net` as the printed "other" line. Examples: AMZN 15,229; AVGO 455; GPC 3,010; NDAQ (27).
- **Exceptions.**
  - CPB puts it *inside* operating costs, above EBIT (R4): excluded.
  - "Interest and other" lines: combined (INTU 389 includes interest income, R3).

### NonoperatingIncomeExpense
- **Meaning.** Aggregate income or expense from ancillary activities.
- **Labels: 349 distinct.** "total other income (expense)" 69, "other income (expense), net" 64, "total other income (expense), net" 61. "Interest and other ..." at 49 companies (HPQ, META, NFLX, HD, CSCO, ISRG, GM).
- **Statement.** IS 389. Calc parent: pretax 225. Children: OtherNonop 201, InterestExpenseNonoperating (-) 127, InvestmentIncomeInterest 61, equity method 46.
- **Decision.** Combined. It fills `other_income_expense_net` only when it is the single non-operating line with no separate interest line (AAPL "Other income/(expense), net" (321), R3).
- **Exceptions.** Where it totals printed interest and other lines, it is total non-operating, and serving it as "other income" would double-count interest:
  - AMZN 17,336 includes interest expense (2,274) (R4).
  - GPC 908,483K includes interest 163,506K and a pension settlement 741,967K (R5).

### IncomeLossFromEquityMethodInvestments
- **Meaning.** Share of equity investees' income.
- **Labels: 840 distinct**, the most spread of the group. "income (loss) from equity method investments" 22, "equity in earnings of unconsolidated affiliates" 18. "Net of tax" at 39 companies (AMZN, BWA, IP, BALL).
- **Statement.** IS 332. CF-only at 64 companies. Calc parents: CFO (-) 150, pretax 66, ProfitLoss 64, Nonop 46, OI 20.
- **Decision.** Excluded: no concept.
- **Exceptions.** The position differs, and it decides what OI and pretax contain:
  - Above OI 25: SBUX 247.8.
  - Pretax zone 130: HST 18, NDAQ 83.
  - After tax 86: AMZN (554).
  - LEN prints a custom combined `len_IncomeLossFromEquityMethodInvestmentsAndOtherNonoperatingIncomeExpense`.

## Disagreements with the library
Sources: Mac Ritwik `origin/work/tag-library/ranks-1-50` @ aea0cf4 (`data-team/47-fsn-store/company_tag_map/ranks_1_50.csv`), and cloud Ritwik `origin/work/ritwik-cloud/tag-decisions-2026-11-11` @ 83bc4988 (card notes and the company exceptions CSV). The rulings listed in the order are followed and not disputed.

1. **Mac: UNH and CRWD `ProfitLoss` -> net_income_resolved (UNH 2015-06 to 2026-06; CRWD 2021-01 to 2026-07).**
   - UNH prints NetIncomeLoss in all 45 of its IS filings in FSN.
   - The FY2025 10-K (0000731766-26-000062 R5, FILING-CHECKED) shows ProfitLoss 12,807 = NetIncomeLoss 12,056 + NCI 751.
   - CRWD has an NCI line in 22 IS filings.
   - If ProfitLoss ever wins a filing, net income is overstated by the NCI share. ProfitLoss should be eligible only where no NetIncomeLoss and no NCI line is printed.
   - V and MA (ProfitLoss only, no NCI line) agree with this card.
2. **Mac: `NonoperatingIncomeExpense` -> other_income_expense_net, including printed totals.**
   - Affected: AMZN "Total non-operating income (expense)", V, MA "Total other income (expense)", RTX, SHOP; and "interest and other" lines at META, INTC, CSCO, HD, NFLX, DELL.
   - The AMZN total (R4, 17,336) contains the interest expense (2,274) that the same map serves as interest_expense. GPC's total contains interest and a 742M pension charge.
   - This card: the OtherNonop line, or Nonop only when it is the single line. The perimeter of `other_income_expense_net` is a definition call for the Standardization Lead. Its catalogue text describes a broad "other non-operating" bucket.
3. **Mac vs cloud (inconsistent with each other): "Interest expense, net".**
   - Mac maps RTX InterestExpense "Interest expense, net" (2015-2024) and LIN InterestExpenseNonoperating "Interest expense - net" to interest_expense.
   - Cloud calls "interest expense, net" combined at DIS and TMUS.
   - This card sides with cloud (combined unless the face or note shows it is gross or only net of capitalized interest). RTX and LIN were not opened: ASSUMED pending a filing check.
4. **Mac: WFC RCFC "Fee income" -> revenue_sanity_resolved (2021-09 to 2026-09).** It is a fee component (FSN label, WFC 0000072971-26-000133 R3 line 27; not opened: DATA-INFERRED). WFC's top line is RevenuesNetOfInterestExpense (Mac commit message). RCFC must never serve WFC revenue.
5. **Mac: UNH SG&A "Operating costs" (59,592) -> sga_expense.** For a managed-care insurer this line is all non-medical operating cost; it is not SG&A in the corporate sense. This card excludes it for the insurer template; it is a sector call. FILING-CHECKED R5.
6. **Mac: UNH CostOfGoodsAndServicesSold "Cost of products sold" -> cost_of_revenue_resolved (2018-2026).** It is 50,655 of 428,603 total operating costs; medical costs of 313,995 are a separate line. It is a component, so cost of revenue for UNH should be not-in-template (insurer).
7. **Cloud IBM `ProfitLoss` -> net_income ("Tag Expert to confirm no NCI line"): confirmed.** IBM has ProfitLoss in 8 IS filings and NetIncomeLoss in 39, and no NCI line on any IBM IS face in FSN (DATA-INFERRED; not opened).
8. **Cloud continuing-ops EPS tags -> basic/diluted EPS (AXP, ADI, COP): agree.** VRSN (FILING-CHECKED) and HAL show the same pattern. The live `fsn.concept_rule` (per_share.eps_fsn_tags) has no such rule, so they go blank today. This is a gap in the rule, not a library disagreement.
9. **Current `fsn.line_map` (rules, not either library) maps known-wrong lines.** Mac rows were not found for these companies, since most are outside ranks 1-50.
   - RCFC bank fee lines to revenue: CFR, NTRS, FCNCA, SSB, BPOP; WFC also in Mac.
   - UDR fee line to revenue.
   - GrossProfit net-revenue lines at NDAQ, SNEX, CBOE and AES.
   - COGS at HST (member rows only), SRE and WELL.
   - OperatingIncomeLoss pretax at AFG and ELS; EBIT at CPB and TFX.

## Untested scope
- 10-Q faces were counted but no 10-Q R page was opened.
- Pre-2018 filings: only DOC 2020 was opened.
- Labels named only from FSN (BALL, TFX, BIO, FE, AFL, EQT, RTX, LIN, WFC, CBOE, SNEX, AES, SRE, WELL) are DATA-INFERRED.
- Values were not compared with companyfacts. That is the mapping step ("SEC FOR MAPPING").

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.92). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.92. 32 elements named in this card have library knowledge; the 30 most served are below. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `IncomeTaxExpenseBenefit`
- **Meaning:** Income Tax Expense (Benefit) (us-gaap, duration, debit). Amount of current income tax expense (benefit) and deferred income tax expense (benefit) pertaining to continuing operations.
- **Data point definition:** income_tax_expense: Income tax expense (benefit) for the period, as printed;  a benefit is a real negative.
- **Data point:** income_tax_expense; polarity income_tax_expense:signed; role income_tax_expense:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1302 served, 44905 proven, 117 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces IncomeTaxExpenseBenefitContinuingOperations@2013; RestatementOfPriorYearIncomeTaxEffects@2020

### `EarningsPerShareBasic`
- **Meaning:** Earnings Per Share, Basic (us-gaap, duration). The amount of net income (loss) for the period per each share of common stock or unit outstanding during the reporting period.
- **Data point definition:** basic_eps: Basic EPS per common share as printed (latest print = split-adjusted history, X92).
- **Data point:** basic_eps; role basic_eps:primary#1
- **Rules:** none
- **Evidence:** 109 companies, 1236 served, 4644 proven, 116 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAdjustmentAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemPreviouslyReportedAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemRestatedAmount@2012; EarningsPerShareBasicAndDiluted@2022 (+5 more)

### `WeightedAverageNumberOfDilutedSharesOutstanding`
- **Meaning:** Weighted Average Number of Shares Outstanding, Diluted (us-gaap, duration). The average number of shares or units issued and outstanding that are used in calculating diluted EPS or earnings per unit (EPU), determined based on the timing of issuance of shares or units in the period.
- **Data point definition:** weighted_diluted_shares: Weighted average diluted common shares as printed.
- **Data point:** weighted_diluted_shares; role weighted_diluted_shares:primary#1
- **Rules:** none
- **Evidence:** 108 companies, 1234 served, 4539 proven, 116 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000063908-24-000072: MCD FY2023 10-K consolidated statement of income ($ in millions, shares in millions): weighted-average diluted shares 732.3;  the XBRL fact is 732.3 shares (scal; filer XBRL error 0000063908-25-000012: MCD FY2024 10-K consolidated statement of income ($ in millions, shares in millions): weighted-average diluted shares 721.9;  the XBRL fact is 721.9 shares (scal (+4 more)
- **Pattern hits:** P03 (5); P04 (3)
- **Deprecation:** replaces WeightedAverageNumberOfShareOutstandingBasicAndDiluted@2022

### `EarningsPerShareDiluted`
- **Meaning:** Earnings Per Share, Diluted (us-gaap, duration). The amount of net income (loss) for the period available to each share of common stock or common unit outstanding during the reporting period and to each share or unit that would have been outstanding assuming the issuance of common shares ...
- **Data point definition:** diluted_eps: Diluted EPS per common share as printed (latest print, X92).
- **Data point:** diluted_eps; role diluted_eps:primary#1
- **Rules:** none
- **Evidence:** 109 companies, 1233 served, 39141 proven, 116 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAdjustmentAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemPreviouslyReportedAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemRestatedAmount@2012; EarningsPerShareBasicAndDiluted@2022 (+5 more)

### `NetIncomeLoss`
- **Meaning:** Net Income (Loss) Attributable to Parent (us-gaap, duration, credit). The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
- **Data point definition:** net_income: Net income attributable to the parent (common and preferred holders) as printed.
- **Data point:** net_income; role net_income:primary#1
- **Rules:** X77; C29; resolver functions resolve
- **Evidence:** 105 companies, 1212 served, 28185 proven, 106 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces InvestmentCompanyNetAssetsFromOperationsIncreaseDecrease@2023; RestatementOfPriorYearIncomeNetOfTax@2020

### `ComprehensiveIncomeNetOfTax`
- **Meaning:** Comprehensive Income (Loss), Net of Tax, Attributable to Parent (us-gaap, duration, credit). Amount after tax of increase (decrease) in equity from transactions and other events and circumstances from net income and other comprehensive income, attributable to parent entity. Excludes changes in equity resulting from investments by o...
- **Data point definition:** comprehensive_income: Comprehensive income attributable to the parent as printed.
- **Data point:** comprehensive_income; role comprehensive_income:primary#1
- **Rules:** X43; X67; X76; I38; I39; I40; I41; I42; resolver functions COMBINED_YIELDS_TO; comparative_fill; DERIVED_YIELDS_TO; fill_printed_zero_and_comparative; resolve_ci
- **Evidence:** 108 companies, 1206 served, 4365 proven, 76 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `SellingGeneralAndAdministrativeExpense`
- **Meaning:** Selling, General and Administrative Expense (us-gaap, duration, debit). The aggregate total costs related to selling a firm's product and services, as well as all other general and administrative expenses. Direct selling expenses (for example, credit, warranty, and advertising) are expenses that can be directly...
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]; sga_expense: Selling, general and administrative expense for the period.
- **Data point:** sga_expense; operating_expenses; polarity sga_expense:positive; role sga_expense:primary#1
- **Rules:** I15; I16; I17; I18; family resolve_all.NARROW[sga_expense]
- **Evidence:** 66 companies, 1140 served, 3623 proven, 73 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces RelatedPartyTransactionSellingGeneralAndAdministrativeExpensesFromTransactionsWithRelatedParty@2023

### `CostOfGoodsAndServicesSold`
- **Meaning:** Cost of Product and Service Sold (us-gaap, duration, debit). The aggregate costs related to goods produced and sold and services rendered by an entity during the reporting period. This excludes costs incurred during the reporting period related to financial services rendered and other revenue generat...
- **Data point definition:** cost_of_revenue: Cost of goods sold / cost of revenue for the period: the costs the filer matches to revenue above gross profit. [not applicable: bank,insurer,bdc]; gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc] (+1 more)
- **Data point:** cost_of_revenue; gross_profit; operating_expenses; polarity cost_of_revenue:positive; role cost_of_revenue:primary#2
- **Rules:** I02; I03; I04
- **Evidence:** 65 companies, 955 served, 16174 proven, 62 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AdvertisingRevenueCost@2018; AssetManagementCosts@2018; CasinoExpenses@2018; ConcessionsCosts@2018 (+62 more)

### `OperatingIncomeLoss`
- **Meaning:** Operating Income (Loss) (us-gaap, duration, credit). The net result for the period of deducting operating expenses from operating revenues.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]; operating_income: Operating income: revenue minus all operating costs (COR, opex, restructuring and impairment), before interest, other non-operating items, equity-method income and tax. [not applicable: bank]
- **Data point:** operating_income; operating_expenses
- **Rules:** C13; resolver functions resolve
- **Evidence:** 80 companies, 948 served, 34797 proven, 106 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestExpense`
- **Meaning:** Interest Expense, Operating and Nonoperating (us-gaap, duration, debit). Amount of interest expense classified as operating and nonoperating. Includes, but is not limited to, cost of borrowing accounted for as interest expense.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+2 more)
- **Data point:** interest_expense; other_income_expense_net; operating_expenses; interest_income; polarity interest_expense:positive; role interest_expense:primary#1
- **Rules:** X115; I21; I20; I22; I23; I24; resolver functions resolve_band; family resolve_all.NARROW[interest_expense]
- **Evidence:** 88 companies, 938 served, 24594 proven, 51 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 2 open hit(s) at 1 companies, e.g. META interest_expense 2021-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P05 (2)
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToInterestExpenseNet@2013; CashFlowHedgeGainReclassifiedToInterestExpense@2013; CashFlowHedgeLossReclassifiedToInterestExpense@2013; InterestExpenseRelatedParty@2023

### `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest`
- **Meaning:** Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest (us-gaap, duration, credit). Amount of income (loss) from continuing operations, including income (loss) from equity method investments, before deduction of income tax expense (benefit), and income (loss) attributable to noncontrolling interest.
- **Data point definition:** income_before_tax: Income from continuing operations before income taxes, as printed (incl. equity-method income where the filer places it above tax).
- **Data point:** income_before_tax; role income_before_tax:primary#1
- **Rules:** I36; I37
- **Evidence:** 95 companies, 815 served, 32500 proven, 81 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAdjustmentAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemPreviouslyReportedAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemRestatedAmount@2012; RetrospectiveEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAmountAfterApplication@2012 (+2 more)

### `Revenues`
- **Meaning:** Revenues (us-gaap, duration, credit). Amount of revenue recognized from goods sold, services rendered, insurance premiums, or other activities that constitute an earning process. Includes, but is not limited to, investment and interest income before deduction of interest expens...
- **Data point definition:** gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc]; revenue: Total revenues (net sales) for the period as printed: the top line of the income statement, after returns and allowances (+1 more)
- **Data point:** revenue; gross_profit
- **Rules:** X123
- **Evidence:** 69 companies, 708 served, 12391 proven, 34 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToRevenueNet@2013; CashFlowHedgeGainReclassifiedToRevenue@2013; CashFlowHedgeLossReclassifiedToRevenue@2013; DevelopmentStageEnterpriseCumulativeRevenue@2012 (+10 more)

### `RevenueFromContractWithCustomerExcludingAssessedTax`
- **Meaning:** Revenue from Contract with Customer, Excluding Assessed Tax (us-gaap, duration, credit). Amount, excluding tax collected from customer, of revenue from satisfaction of performance obligation by transferring promised good or service to customer. Tax collected from customer is tax assessed by governmental authority that is both i...
- **Data point definition:** gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc]; revenue: Total revenues (net sales) for the period as printed: the top line of the income statement, after returns and allowances (+1 more)
- **Data point:** revenue; gross_profit
- **Rules:** none
- **Evidence:** 64 companies, 650 served, 16994 proven, 75 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces InitialFranchiseFees@2026; PropertyManagementFeeRevenue@2026; RevenueRecognitionMilestoneMethodRevenueRecognized@2026

### `InvestmentIncomeInterest`
- **Meaning:** Investment Income, Interest (us-gaap, duration, credit). Amount before accretion (amortization) of purchase discount (premium) of interest income on nonoperating securities.
- **Data point definition:** interest_income: Consolidated interest income for the period (X94).; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** interest_income; other_income_expense_net; polarity interest_income:signed; role interest_income:primary#2
- **Rules:** I26; I27; family resolve_all.NARROW[interest_income]
- **Evidence:** 50 companies, 616 served, 1444 proven, 48 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 4 open hit(s) at 3 companies, e.g. AMGN interest_income 2021-12-31 (export) (pattern_hits.csv); pattern P06 own_10k_year_hidden: 5 open hit(s) at 1 companies, e.g. CRM interest_income 2015-01-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (5); P05 (4)

### `OtherNonoperatingIncomeExpense`
- **Meaning:** Other Nonoperating Income (Expense) (us-gaap, duration, credit). Amount of income (expense) related to nonoperating activities, classified as other.
- **Data point definition:** interest_income: Consolidated interest income for the period (X94).; operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank] (+1 more)
- **Data point:** other_income_expense_net; interest_income; operating_expenses; polarity other_income_expense_net:signed; role other_income_expense_net:primary#2
- **Rules:** X59; I28; I29; I30; I31; I32; I33; I34; I35; resolver functions COMBINED_YIELDS_TO
- **Evidence:** 67 companies, 607 served, 1993 proven, 46 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `GrossProfit`
- **Meaning:** Gross Profit (us-gaap, duration, credit). Aggregate revenue less cost of goods and services sold or operating expenses directly attributable to the revenue generation activity.
- **Data point definition:** gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc]; operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]
- **Data point:** gross_profit; operating_expenses
- **Rules:** X36; X56; X80; C10; I08; resolver functions apply_absent_in_own_filing; resolve; derive_gross_profit
- **Evidence:** 44 companies, 499 served, 17157 proven, 71 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationGrossProfitLoss@2020

### `CostOfRevenue`
- **Meaning:** Cost of Revenue (us-gaap, duration, debit). The aggregate cost of goods produced and sold and services rendered during the reporting period.
- **Data point definition:** cost_of_revenue: Cost of goods sold / cost of revenue for the period: the costs the filer matches to revenue above gross profit. [not applicable: bank,insurer,bdc]; gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc] (+1 more)
- **Data point:** cost_of_revenue; gross_profit; operating_expenses; polarity cost_of_revenue:positive; role cost_of_revenue:primary#1
- **Rules:** I02; I03; I04
- **Evidence:** 32 companies, 429 served, 7811 proven, 27 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationCostOfSales@2020; RelatedPartyCosts@2023

### `GeneralAndAdministrativeExpense`
- **Meaning:** General and Administrative Expense (us-gaap, duration, debit). The aggregate total of expenses of managing and administering the affairs of an entity, including affiliates of the reporting entity, which are not directly or indirectly associated with the manufacture, sale or creation of a product or pro...
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]; sga_expense: Selling, general and administrative expense for the period.
- **Data point:** sga_expense; operating_expenses; polarity sga_expense:positive; role sga_expense:primary-part#2; sga_expense:primary-part#4; sga_expense:primary-part#5; sga_expense:primary-part#6 (+1 more)
- **Rules:** I17; I15; I16; I18; resolver functions role
- **Evidence:** 26 companies, 419 served, 394 proven, 13 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 1 open hit(s) at 1 companies, e.g. PM sga_expense 2015-12-31 (export) (pattern_hits.csv); pattern P06 own_10k_year_hidden: 2 open hit(s) at 1 companies, e.g. PM sga_expense 2016-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (2); P05 (1)

### `OperatingExpenses`
- **Meaning:** Operating Expenses (us-gaap, duration, debit). Generally recurring costs associated with normal operations except for the portion of these expenses which can be clearly related to production and included in cost of sales or services. Includes selling, general and administrative expense.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]
- **Data point:** operating_expenses; polarity operating_expenses:positive; role operating_expenses:primary#1
- **Rules:** I14; I09; I10; I11; I12; I13; family resolve_all.NARROW[operating_expenses]
- **Evidence:** 36 companies, 352 served, 11930 proven, 11 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `NonoperatingIncomeExpense`
- **Meaning:** Nonoperating Income (Expense) (us-gaap, duration, credit). The aggregate amount of income or expense from ancillary business-related activities (that is to say, excluding major activities considered part of the normal operations of the business).
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+2 more)
- **Data point:** other_income_expense_net; interest_income; interest_expense; operating_expenses; polarity other_income_expense_net:signed; role other_income_expense_net:primary#1
- **Rules:** I29; I28; I30; I31; I32; I33; I34; I35; resolver functions resolve_band
- **Evidence:** 28 companies, 184 served, 242 proven, 14 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestExpenseNonoperating`
- **Meaning:** Interest Expense, Nonoperating (us-gaap, duration, debit). Amount of interest expense classified as nonoperating.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+1 more)
- **Data point:** interest_expense; other_income_expense_net; interest_income; polarity interest_expense:positive; role interest_expense:primary#2
- **Rules:** I20; I21; I22; I23; I24; family resolve_all.NARROW[interest_expense]
- **Evidence:** 55 companies, 132 served, 744 proven, 28 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `NoninterestIncome`
- **Meaning:** Noninterest Income (us-gaap, duration, credit). The total amount of noninterest income which may be derived from: (1) fees and commissions; (2) premiums earned; (3) insurance policy charges; (4) the sale or disposal of assets; and (5) other sources not otherwise specified.
- **Data point definition:** noninterest_income: Total noninterest income as printed. [not applicable: general,lender,broker_am,insurer,equity_reit,utility,bdc]; revenue: Total revenues (net sales) for the period as printed: the top line of the income statement, after returns and allowances (+1 more)
- **Data point:** noninterest_income; revenue; role noninterest_income:primary#1
- **Rules:** none
- **Evidence:** 8 companies, 114 served, 375 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `CostsAndExpenses`
- **Meaning:** Costs and Expenses (us-gaap, duration, debit). Total costs of sales and operating expenses for the period.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]
- **Data point:** operating_expenses
- **Rules:** X117; I09; resolver functions apply_cost_and_opex
- **Evidence:** 21 companies, 95 served, 190 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces DevelopmentStageEnterpriseCumulativeExpense@2012

### `IncomeLossFromEquityMethodInvestments`
- **Meaning:** Income (Loss) from Equity Method Investments (us-gaap, duration, credit). Amount of income (loss) for proportionate share of equity method investee's income (loss).
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** operating_expenses; other_income_expense_net
- **Rules:** none
- **Evidence:** 13 companies, 82 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** filer XBRL error 0001562762-20-000064: T FY2019 10-K t-20191231.htm consolidated statements of income: Equity in net income (loss) of affiliates 6 (2018: (48));  the XBRL fact is -6 and the printed to
- **Pattern hits:** none
- **Deprecation:** replaces IncomeLossFromEquityMethodInvestmentsMember@2013; MinorityInterestAndEarningsLossesEquityInvestmentsMember@2013

### `NetIncomeLossAvailableToCommonStockholdersBasic`
- **Meaning:** Net Income (Loss) Available to Common Stockholders, Basic (us-gaap, duration, credit). Amount, after deduction of tax, noncontrolling interests, dividends on preferred stock and participating securities; of income (loss) available to common shareholders.
- **Data point definition:** net_income: Net income attributable to the parent (common and preferred holders) as printed.
- **Data point:** net_income; role net_income:primary#2
- **Rules:** none
- **Evidence:** 11 companies, 75 served, 383 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `RevenuesNetOfInterestExpense`
- **Meaning:** Revenues, Net of Interest Expense (us-gaap, duration, credit). Amount of revenue recognized from goods sold, services rendered, insurance premiums, or other activities that constitute an earning process. Includes, but is not limited to, investment and interest income after deduction of interest expense...
- **Data point definition:** revenue: Total revenues (net sales) for the period as printed: the top line of the income statement, after returns and allowances;  excise follows the filer's own presentation (X56).
- **Data point:** revenue
- **Rules:** none
- **Evidence:** 5 companies, 49 served, 245 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `MinorityInterest`
- **Meaning:** Equity, Attributable to Noncontrolling Interest (us-gaap, instant, credit). Amount of equity (deficit) attributable to noncontrolling interest. Excludes temporary equity.
- **Data point definition:** stockholders_equity: Equity attributable to the parent at period end.
- **Data point:** stockholders_equity
- **Rules:** none
- **Evidence:** 4 companies, 47 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationMinorityInterest@2020; NoncontrollingInterestBalanceSheetLocation@2016

### `BenefitsLossesAndExpenses`
- **Meaning:** Benefits, Losses and Expenses (us-gaap, duration, debit). The total amount of expense recognized during the period for future policy benefits, claims and claims adjustment costs, and for selling, general and administrative costs.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]
- **Data point:** operating_expenses; polarity operating_expenses:positive; role operating_expenses:primary#2
- **Rules:** I14; I09; I10; I11; I12; I13
- **Evidence:** 2 companies, 24 served, 101 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestExpenseOperating`
- **Meaning:** Interest Expense, Operating (us-gaap, duration, debit). Amount of interest expense classified as operating.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).
- **Data point:** interest_expense; polarity interest_expense:positive; role interest_expense:primary#5
- **Rules:** I20; I21; I22; I23; I24
- **Evidence:** 11 companies, 20 served, 142 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `IncomeLossFromContinuingOperationsPerBasicShare`
- **Meaning:** Income (Loss) from Continuing Operations, Per Basic Share (us-gaap, duration). The amount of net income (loss) from continuing operations per each share of common stock or unit outstanding during the reporting period.
- **Data point definition:** basic_eps: Basic EPS per common share as printed (latest print = split-adjusted history, X92).
- **Data point:** basic_eps; role basic_eps:primary#3
- **Rules:** none
- **Evidence:** 5 companies, 20 served, 23 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces IncomeLossFromContinuingOperationsPerBasicAndDilutedShare@2022; NewAccountingPronouncementOrChangeInAccountingPrincipleEffectOfChangeOnBasicEarningsPerShare@2020
<!-- END GENERATED: tag library rows -->
