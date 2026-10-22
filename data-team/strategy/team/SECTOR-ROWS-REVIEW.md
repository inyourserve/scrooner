# SECTOR-ROWS-REVIEW: Sector Analyst review of doc 50 (Ritwik's 66 sector rows and visible metric sets), 2026-10-22

Role: Sector Analyst (12). Task: WO-4 item 4 (offline, no database). Reviewed: `data-team/strategy/50-SECTOR-ROWS-AND-VISIBLE-METRIC-SETS-DRAFT-2026-10-22.md`. Everything below is a PROPOSAL for the Standardization Lead, the Tag Expert and the named accountant; nothing is approved.
Evidence labels: **FC** = FILING-CHECKED (balance sheet and income statement R-file rows of the latest 10-K, read by regex "Reader 1" in this run: accession and R-file in `data/group_assignment_v2.csv`, tag coverage in `data/sector_lead_coverage_v2.csv`, per-group tag frequencies in `data/sector_face_tags_v2.csv`); **DI** = DATA-INFERRED; **AS** = ASSUMED. FC here means "the tag is on the face of that filer's own statements", it does not verify a value. Reader 2 (lxml) has not been run on these filings.
Companion files: `data/template_v1_draft.csv` (cell lists over `catalog_version cv-2026.10.22-draft1`), `tools/groups_v2/build_template.py` (rules in code).

## 1. Verdict in six lines
1. The draft is a good first cut: 66 rows, the right families, the right refusal of MD&A-only KPIs. Keep it as the base.
2. **Four groups of the frozen enum have no defining row at all** (non-bank lender, crypto/digital, exchange, insurance broker), so their templates could reach 100% D1 with no sector cell: the same redo the catalog extension exists to prevent. Added below.
3. **At least seven tag leads of the draft are wrong on the filings** (measured on the 986 plus extras): bank interest expense (B3), bank net loans (B10), bank allowance name (B12), BDC net assets (F3, AssetsNet), BDC net investment income (F2, pre- vs after-tax), utility regulatory assets (U2), managed-care premium and medical-cost tags (M1/M2); my own earlier crypto lead (CryptoAssetNoncurrent) was wrong too. Section 3.
4. **Seven draft rows are not new catalog rows** (they already exist as catalog lines or are definition items), and the existing registry metric `net_interest_income` collides with the bank row. Section 2.
5. **Two draft rows are REQ for a whole group but only part of the group files them**: equity-REIT rental revenue (28 of 53) and partners' capital in "MLP / midstream" (6 of 14, the six partnerships).
6. **Asset-manager fee lines, exchange clearing lines and insurance-broker fiduciary lines have no us-gaap tag on the face** (extension tags only): they are extension facts, absent from companyfacts. D1 cells with no capture path are `defect`, not blank; they need the filing-instance route or a `data_limit` label before they count in a template.

## 2. Rules for the catalog (doc 50 section 1): amendments
| # | Draft rule | Finding | Amendment |
|---|---|---|---|
| 1 | "A sector row exists only if it is a face-statement line or an arithmetic combination of face lines" | Contradicted by the draft's own rows: B12 allowance, R4/R5 (Schedule III), F4 NAV per share, F8 and L2 distributions per share come from notes or financial highlights | "face line, or an XBRL-tagged line of the primary statements' notes; never MD&A, press releases or vendors" |
| 2 | ~18 visible metrics per group | Fine; the visible-set sketch lists 18 for banks only by counting REP rows (bank revenue, net margin on bank revenue, efficiency ratio) | Visible sets must mark which items are `definition_pending` so launch does not ship holes (section 6) |
| 3 | Rule codes REQ/REP/COND/NIT | OK. Add the state a COND cell takes when its condition is false (`not_presented`, `evidenced_zero`, `undefined_by_math`) and a `needs_accountant` flag | Both are columns in `template_v1_draft.csv` |
| 4 | "Every sector row is versioned in catalog_version" | Short ids R1..R8, F1..F8, M1.. collide with the report numbers R1-R8 and founder items F-1..F-3 | Namespaced ids `sr.<family>.<name>` (used in the template draft); the Standardization Lead assigns final canonical ids |
| 5 | Rows count about 66, trimmed to about 60 by G+3 | Net effect of this review: 62 sector rows (details in 5) | - |
| 6 | (not in the draft) existing registry rows that share a name | The registry metric `net_interest_income` = `interest_income` - `interest_expense` with `interest_income` mapped to `InvestmentIncomeInterest`, the SECURITIES interest line at banks (FLG 0001104659-25-106961 R4; tag card interest.md) | The bank row needs a new id and a MAJOR definition version; the old metric becomes NIT for bank, lender, mortgage REIT (`template_v1_draft.csv` does this) |

## 3. Row by row (draft id -> verdict)
Coverage numbers are "members of the group showing the tag on their own face / group size" (FC, Reader 1, latest 10-K or 10-Q), from `data/sector_lead_coverage_v2.csv`. Group sizes are the v2 groups on the 986.
| Draft | Verdict | Correction / name / formula | Group-defining | Tag Expert to confirm |
|---|---|---|---|---|
| B1 NII | keep; shared row `sr.fin.net_interest_income` (bank, lender COND, mortgage REIT) | face line | Y | InterestIncomeExpenseNet + InterestRevenueExpenseNet on 43/44 banks, 2/2 mortgage REITs. Bank-only reading (non-banks print it as net interest EXPENSE: tag card interest.md); id collision with the old metric |
| B2 total interest income | keep `sr.fin.interest_income_total` | face line | Y | InterestAndDividendIncomeOperating or InterestIncomeOperating: 43/44; mortgage REITs use InterestIncomeOperating (2/2). NEVER InvestmentIncomeInterest |
| B3 total interest expense | **lead wrong**: InterestExpenseOperating first | face line | Y | InterestExpenseOperating or InterestExpense: 44/44; InterestExpense alone is on the face of only 2/44 (the draft lead) |
| B4/B5 noninterest income / expense | keep | face line | Y | NoninterestIncome 44/44, NoninterestExpense 44/44; BANR-type mis-tag stays a company-scoped exception |
| B6 provision | keep as REQ but **no single tag** | `sr.fin.provision_credit_losses`, perimeter label (loans only / + unfunded / + securities); accountant | Y | any of 7 us-gaap tags 33/44; the draft's ProvisionForLoanLeaseAndOtherLosses alone 21/44; 11 banks custom or absent; CECL era split |
| B7 bank revenue | keep REP | NII + noninterest income; SFNC-type negative noninterest income needs an NM rule | - | RevenuesNetOfInterestExpense only as cross-check (JPM, WFC) |
| B8 efficiency ratio | keep REP | noninterest expense / B7, "reported basis, not company-adjusted" | - | - |
| B9 deposits | keep | face total, else sum of interest-bearing + noninterest-bearing (composition = calculated) | Y | Deposits 41/44; 3 banks components only |
| B10 loans, net | **lead wrong** | period-scoped tag set, not the pre-CECL tag | Y | post-CECL FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss 33/44; any of 3 tags 40/44; the draft's LoansAndLeasesReceivableNetReportedAmount (pre-CECL) is on 1/44 |
| B11 loans to deposits | keep | net loans / total deposits | - | - |
| B12 allowance | keep COND | face or note | - | post-CECL allowance tag family 35/44; draft name `AllowanceForLoanAndLeaseLosses...` is on the face of 0 of 1,027 filers read: use FinancingReceivableAllowanceForCreditLoss* |
| B13 equity / assets | metric row on existing concepts, keep | state the equity basis (parent common vs total incl. NCI, preferred) | - | - |
| B14 ROA on average assets | **not a bank sector row** | existing `roa` divides by ENDING assets; one general `roa@2` on average assets (MAJOR) or a label, not a bank-only twin | - | - |
| B15 tangible BV/share | keep REP | needs other intangibles and preferred concepts (none exist) | - | goodwill exists; MSR/core-deposit perimeter is an accountant call |
| I1 premiums earned | keep, **shared with managed care** | `sr.ins.premiums_earned` | Y | PremiumsEarnedNet 36/40 insurers, 6/7 managed-care filers (label Premiums) |
| I2 NII (insurer) | keep, **collision** | `sr.ins.net_investment_income` | Y | NetInvestmentIncome 35/40 insurers. The same tag is the PRE-tax BDC line (ARCC 0001287750-26-000006 R5 "NET INVESTMENT INCOME BEFORE INCOME TAXES" 1,458.0M): two concepts, one tag. Likely source of the 24 insurers sitting in `bdc_total_investment_income` (AS: not checked against `concept_mapping`; Tag Expert ask a) |
| I3 total revenues | not a new row | existing `revenue` line; `Revenues` is on the face of 40/40 insurers | - | - |
| I4 losses and LAE | keep, shared with managed care | `sr.ins.benefits_claims_incurred`, label net/gross | Y | PolicyholderBenefitsAndClaimsIncurredNet 33/40; managed care 6/7 labelled "Medical costs" |
| I5 DAC amortization | keep COND | - | - | DeferredPolicyAcquisitionCostAmortizationExpense 19/40 |
| I6 reserves for unpaid losses | **split** | P&C and health: unpaid claims (27/40); life: future policy benefits and policyholder account balances (21/40, row missing in the draft) | Y | LiabilityForClaimsAndClaimsAdjustmentExpense; LiabilityForFuturePolicyBenefits; PolicyholderContractDeposits |
| I7 loss ratio | keep COND, accountant | P&C and health only; combined ratio is MD&A | - | - |
| I8/I9 BVPS, ROE | not new rows | existing catalog lines | - | - |
| M1/M2 managed-care premiums / medical costs | **merge into I1/I4** (same tags, 6/7) | - | - | draft leads (HealthCarePremium..., PolicyholderBenefitsAndClaimsIncurredHealthCare...) are not on any face |
| M3 medical loss ratio | keep COND, rename `sr.mc.medical_care_ratio` | GAAP face basis, not the ACA/regulatory MLR; pharmacy revenue at Cigna/Elevance dilutes the premium base | - | - |
| R1 rental revenue | **REQ -> COND** | REQ for the `property_reit` variant only | Y | rental tag family on 28/53 equity REITs; operating REITs (towers, storage, timber, data centers, hotels) print plain revenue |
| R2 property operating expenses | keep COND | - | - | 25/53; sparse |
| R3 NOI | keep REP, **fix formula** | property revenues INCLUDING tenant reimbursements minus property operating expenses (draft used rental revenue only) | - | - |
| R4 real estate at cost, R5 accumulated depreciation | REQ -> COND | face or Schedule III note | Y (R4) | at cost 26/53, accumulated depreciation 30/53 on the face; add RealEstateInvestmentPropertyNet 36/53 |
| R6 G&A | REQ -> COND | - | - | GeneralAndAdministrativeExpense 47/53 equity REITs, 2/2 mortgage REITs |
| R7 debt to total assets | keep REP | needs the debt perimeter | - | - |
| R8 capex definition | **not a row** | a definition decision on the existing `capex` line for REITs (REP on `capex_resolved`) | - | - |
| MR1-MR3 | keep, shared `sr.fin.*` | interest income, interest expense, NII | Y | InterestIncomeOperating / InterestExpenseOperating / InterestIncomeExpenseNet 2/2 |
| MR4 BVPS, MR6 DPS | not new rows | existing catalog lines | - | - |
| MR5 recourse leverage | keep COND, **rename** | "Repurchase agreements to equity (face basis)", never "economic leverage" | - | repo tags on the face for 1/2 (AGNC/NLY captions differ) |
| (missing) mortgage assets | add `sr.mreit.mortgage_assets` | securities and loans at fair value | Y | custom captions at NLY/AGNC likely |
| F1 total investment income | **not new** | existing catalog leaf `bdc_total_investment_income`; gate it by group (R4) | Y | GrossInvestmentIncomeOperating 2/2 |
| F2 net investment income | **perimeter** | after-tax line `InvestmentIncomeOperatingAfterExpenseAndTax` (ARCC 1,415.0M; BXSL 0001736035-26-000004 R5 739,942K); `NetInvestmentIncome` is the PRE-tax line at both | Y | pre/post-tax choice is a Standardization Lead call |
| F3 net assets | **lead wrong** | StockholdersEquity is the face line (ARCC "Total stockholders' equity" 14,318.0M; BXSL "Total net assets"); AssetsNet is on 0/2 | Y | - |
| F4 NAV/share, F5 investments at FV | keep | - | Y | NetAssetValuePerShare 2/2, InvestmentOwnedAtFairValue 2/2 |
| (missing) net increase in net assets from operations | add | NetIncomeLoss at both ("NET INCREASE IN STOCKHOLDERS' EQUITY RESULTING FROM OPERATIONS" 1,299.0M) | Y | - |
| F6 NII/share, F7 P/NAV | keep derived | BXSL also tags NII per share (InvestmentCompanyInvestmentIncomeLossPerShare) | - | - |
| F8 distributions per share | keep, tag unverified | note / financial highlights | - | not on the face |
| A1 management and advisory fees | keep COND, **capture-path defect** | no common tag: 0/14 show InvestmentAdvisory*/AssetManagement*/ManagementFee* tags; revenue is one RevenueFromContract.../Revenues line (14/14) | N (cannot be) | company-specific fee captions only |
| A2 compensation | keep COND | - | - | LaborAndRelatedExpense 11/14 |
| A3 compensation ratio, A4 operating margin | A3 keep; A4 not new | - | - | - |
| BD1 net revenues | keep REP | - | Y | RevenuesNetOfInterestExpense 7/11, Revenues 8/11 |
| BD2 compensation ratio | keep COND | - | - | - |
| BD3 ROE | not new | - | - | - |
| (missing) broker/customer receivables and payables | add | - | Y | ReceivablesFromBrokersDealersAndClearingOrganizations 7/11; Payables... (srt prefix) 6/11 |
| P1 cash and short-term investments | keep, new concept | composite: cash + short-term investments + current marketable securities (+ non-current marketable securities for runway) | Y | the combined tag CashCashEquivalentsAndShortTermInvestments is on the face of 13 of 1,027 filers read; components are the common case (ShortTermInvestments 133, MarketableSecuritiesCurrent 72) |
| P2 operating cash burn, P5 R&D, P6 dilution | derived/existing, not new | - | - | - |
| P3 runway | keep COND, formula disclosed as ours | - | - | - |
| P4 accumulated deficit | keep, new concept, **not pre-revenue-only** | useful to every corporate (retained earnings is on the 24-gap list) | Y | RetainedEarningsAccumulatedDeficit on the face of 985 of 1,027 filers read |
| P7 equity proceeds | keep COND, new concept | - | - | ProceedsFromIssuanceOfCommonStock family |
| U1 utility plant, net | keep COND | - | - | PublicUtilitiesPropertyPlantAndEquipmentNet 12/32 (others PropertyPlantAndEquipmentNet) |
| U2 regulatory assets | **lead wrong** | RegulatoryAssetsCurrent + RegulatoryAssetsNoncurrent (22/32); plain RegulatoryAssets on 0/32; add regulatory liabilities (22/32) | Y | - |
| U3 capex intensity | not a sector row | existing `capex_pct_revenue` | - | - |
| L1 partners' capital | **REQ -> COND** | legal-form condition; 6/14 midstream filers are partnerships | Y | PartnersCapital family; partnerships print EPS per LP unit (NetIncomeLossPerOutstandingLimitedPartnershipUnit*, 5/14): add to the EPS vocabulary or midstream EPS stays blank |
| L2 distributions per unit | keep COND | name the basis (declared vs paid) | - | ...DeclaredPerUnit vs ...PaidPerUnit |
| L3 distributions / CFO | keep COND derived | - | - | - |

## 4. Rows the draft does not have (added in the template draft)
| Group | Rows | Why |
|---|---|---|
| non-bank lender (4) | shares `sr.fin.*`: interest income, interest expense, provision, net loans, allowance; NII COND | provision tag ProvisionForLoanLossesExpensed 3/4, loans NotesReceivableNet 3/4 (FC) |
| crypto / digital (8) | `sr.crypto.digital_assets`, `sr.crypto.digital_asset_gains_losses` | CryptoAssetFairValue* 6/8; CryptoAssetRealizedGainLossOperating / ...AndUnrealized... 5/8 (FC). My earlier lead CryptoAssetNoncurrent is on no face |
| exchange (6) | clearing assets (performance bonds, guaranty funds, margin deposits), transaction and clearing revenue | extension tags at CME, ICE, CBOE (prefix cme/ice/cboe; 0 of 6 show a us-gaap margin-deposit tag): custom, not in companyfacts |
| insurance broker (7) | fiduciary assets (COND), commissions and fees (COND) | fiduciary lines on 3/7 but under EXTENSION tags (aon, ajg, bro prefixes; 0/7 us-gaap); 7/7 show ONE revenue line |
| life insurer | future policy benefits and policyholder account balances | I6 covered P&C only |
| BDC | net increase in net assets from operations | the BDC earnings line |
| broker-dealer | receivables from / payables to brokers, dealers, customers | defines the shape |
| energy | oil and gas properties, net (E&P) | optional |
| overlays | pre_revenue (5 rows), captive_finance, lending_operations (PROPOSED), insurance_operations, managed_care_operations, conglomerate_insurer, deposit_taking_operations (PROPOSED), crypto_holdings, royalty_land | `OVERLAYS` in `build_template.py`; triggers are text in the CSV |

Two overlays are my additions to the plan's list: `deposit_taking_operations` (GS, MS, SCHW, RJF, SF carry deposits + loans + provision + NII on the face) and `lending_operations` (XYZ, FCFS). Standardization Lead to accept or fold them into `captive_finance`.

## 5. Group-defining rows (a template that lacks them can pass D1 with no sector content)
Bank: NII, total interest income, total interest expense, noninterest income, noninterest expense, provision, deposits, net loans (8). Lender: interest income, interest expense, provision, net loans. Insurer: premiums earned, net investment income, benefits and claims, unpaid claims (P&C) or future policy benefits (life). Managed care: premiums, medical costs (shared). Equity REIT: rental revenue (property variant), real estate net / at cost. Mortgage REIT: NII, interest income, interest expense, mortgage assets, repurchase agreements. BDC: total investment income, NII after tax, net assets, NAV per share, investments at fair value, net increase in net assets. Broker-dealer: net revenues, broker/customer receivables. Crypto: digital assets. Utility: regulatory assets. Midstream partnerships: partners' capital. Asset manager, exchange and insurance broker: no defining row has a us-gaap tag usable by companyfacts (section 1 line 6). 32 of the 62 rows are marked `group_defining=Y` in the CSV.

## 6. Visible metric sets (doc 50 section 3): findings
1. Bank: three of the 18 (bank revenue, net margin on bank revenue, efficiency ratio) depend on B7, which is `definition_pending` until the accountant rules. Until then the visible set is 15 with three marked pending, not 18.
2. Missing from section 3: non-bank lender, crypto/digital, insurance broker, midstream (partnership distributions). They need a set before the template is frozen.
3. Equity REIT: NOI (COND) and debt to total assets (REP) are not available at launch for most; rental revenue is on 28/53 only. A visible set that shows them for all REITs would show holes.
4. Insurer: "reserves" must be split P&C vs life (I6).
5. The core cells line says "P/E trailing, only on positive earnings": consistent with the NM state; fine.
6. Mortgage REIT list shows ROE; E-M reasoning for coverage ratios is consistent with the template draft (interest coverage NIT).

## 7. Answers to the five open questions of doc 50
1. **Hybrid precedence**: confirmed as "the group owns the largest face revenue caption; the second business is an overlay when its signature (at least two face lines) is on the face". Measured: CVS premiums 134,751M of 402,067M (33%) -> corporate + managed_care_operations; L premiums 10,900M of 18,454M and MKL premiums 8,715,667K of 15,513,233K -> insurer + conglomerate_insurer; CAT, F, GM, DE, PCAR, KMX, SNA, TXT carry finance receivables -> corporate + captive_finance. **Open**: KKR (net premiums + net investment income 11,062M of 19,464M total revenues) and APO (Athene) are asset_manager + insurance_operations as the plan says, but by caption size an insurer reading is arguable; BRK-A is provisional (rule 4 says corporate, the plan says insurer + conglomerate_insurer).
2. **$1M floor**: I could not test it (no database). The face disjunct alone selects PCVX and SMMT in the 986 (and AKTX outside it): an income statement with no revenue line and an R&D line (FC). Keep both disjuncts; the floor value is the Standardization Lead's call.
3. **New concepts**: confirm cash and short-term investments (composite), accumulated deficit, equity proceeds, partners' capital (COND). Add: digital assets, fiduciary assets, regulatory assets and liabilities (current / noncurrent), net increase in net assets from operations, future policy benefits / policyholder account balances.
4. **REP rows needing the accountant**: B6 (provision perimeter), B7, B8, B15, R3, R7, BD1, I-row net vs gross, F2 (pre/post tax), MR5 label, A1 (custom fee captions).
5. **Tag Expert asks**: section 8.

## 8. Tags the Tag Expert should confirm (population-wide, with the coexistence check) and cards to open
1. Bank: InterestIncomeExpenseNet vs InterestRevenueExpenseNet (the one bank without either), InterestExpenseOperating vs InterestExpense, the 7-tag provision set per CECL era, Deposits composite, net loans three-tag set, allowance family. Reuse the clean set in data-team/32 s4; the 44-bank numbers above replace its 30-bank numbers.
2. Insurer: NetInvestmentIncome vs InvestmentIncomeNet; query `concept_mapping` for the tag behind `bdc_total_investment_income` (hypothesis: NetInvestmentIncome); PolicyholderBenefitsAndClaimsIncurredNet net vs gross; LiabilityForClaims... vs LiabilityForFuturePolicyBenefits by variant.
3. BDC: NetInvestmentIncome (pre-tax) vs InvestmentIncomeOperatingAfterExpenseAndTax; StockholdersEquity as net assets; only two BDCs here, so the full BDC population needs its own check.
4. Crypto: CryptoAssetFairValue / ...Noncurrent / ...Current and the gain/loss tags across the 8, plus TSLA, XYZ, GME, FIG, SPCX (one balance-sheet line each).
5. Utility: RegulatoryAssets/Liability current + noncurrent; PublicUtilitiesPropertyPlantAndEquipmentNet vs PropertyPlantAndEquipmentNet.
6. Midstream: PartnersCapital family and EPS per LP unit tags; the EPS vocabulary for partnerships.
7. Equity REIT: rental revenue family vs plain Revenues for the operating variant; real estate gross/at cost/net.
8. Custom-tag groups (asset manager fees, exchange clearing lines, MRSH fiduciary lines): confirm there is no common tag, then route to the filing-instance capture path (ledger rule: custom extension facts are absent from companyfacts).
9. Mortgage REIT repurchase agreements and mortgage assets (custom captions at NLY/AGNC likely).

## 9. Commands actually run, untested scope
Run: reads of local repo files and data; SEC reads through the shared flock limiter (see the task report for counts); python (repo venv, stdlib only) for the classifier, the template builder and the coverage tables. No database query, no write outside the worktree, nothing applied.
Untested: tag coverage uses Reader 1 (regex on R-file rows) on the latest 10-K or 10-Q of each filer, one fiscal year; custom tags appear as extension prefixes and were not mapped; BDC, mortgage REIT, lender and crypto counts rest on 2, 2, 4 and 8 filers; the template draft's REQ/COND bands come from R4 presence rates (DI) plus 986-run presence for the proxied groups; no accountant ruling is assumed anywhere.
