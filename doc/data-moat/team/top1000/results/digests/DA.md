# Digest DA: shard result files S000 and S001-S019 (block A)

Read-only synthesis of the worker files. Findings only, no fixes. Evidence labels are the workers' own: FILING-CHECKED (FC) = a filing R-page or SEC record was opened and cited; DATA-INFERRED (DI) = our tables only.

## Block

Files read in full: S000.md (ranking audit), S001.md, S002.md, S003.md, S004.md, S005.md, S006.md, S007.md, S008.md, S009.md, S010.md (as instructed, not S010-filing-checked.md), S011.md, S012.md, S013.md, S014.md, S015.md, S016.md, S017.md, S018.md, S019.md. None missing or partial. S000_suspects.csv was not read (brief names only the .md files).

Companies covered: 189 (S001 10, S002 9 because TBLA was excluded and left to S000, S003-S019 10 each).

Evidence level by file (important for how much weight a finding carries):
- Entirely DI, no filing opened: S001, S003, S004, S005, S006, S007, S008, S010, S011. SEC was blocked by network policy or by the permission classifier, or by instruction. Each of these workers called blanks "unknown (suspected not_reported)" instead of `not_reported`. These early files use an older format (no per-company verdict table, blank causes shown as codes).
- Mixed, with real FC findings: S000 (14 SEC requests), S002 (about 38 requests), S009 (57 pages), S012 (39), S013 (39), S014 (37), S015 (43), S016 (about 40), S017 (43), S018 (35), S019 (35).
- No file has its own per-company verdict table. All verdicts below are DERIVED by me (rule in that section).
- All FC reads used one regex R-page reader (`<tr>` rows plus `defref_` tag), footnote cells dropped, no independent cross-check (stated in S002, S009, S012-S019).
- Not read by any worker as a systematic check: FY2015 / FY2018 / FY2021 history spot-checks (see History-window section).

Blank counts per file (cells with `has_value = false`, 163 cells per company): S001 215, S002 360, S003 179, S004 206, S005 292, S006 277, S007 251, S008 270, S009 272, S010 200, S011 361, S012 444, S013 259, S014 277, S015 317, S016 199, S017 332, S018 333, S019 174. Sum 5,218. Four of these are inflated by foreign private issuers with almost no cells filled: BMO 154 (S011), BNS 152 (S012), CNI 151 (S018), AEM 66 (S014) = 523 cells.

---

## T1 Revenue resolves to a partial or sub-line tag

- **Companies affected: 19.**
  - FILING-CHECKED (11): USB(S014), BNY(S013), WMT(S002), FCX(S013), CEG(S013), DUK(S013), KMI(S018), CP(S018), AMT(S016), WMB(S016, subset LARGER than face total), ICE(S014, perimeter question: gross revenue vs filer's net revenue under custom tag).
  - DATA-INFERRED (8): BAC(S004), WFC(S005), GS(S005), MS(S005), AXP(S006, ASC 606 component), COF(S011, ASC 606 component), CVX(S003, "a definition choice, not an error", 67,199 vs Revenues 70,055), GE(S004, quarterly revenue = GE Capital only, cited from a known family, not re-derived).
  - Cleared as correct (FC): JPM(S002), SCHW(S009), PNC(S015), HOOD(S015), C(S006, arithmetic).
- **Cells:** wrong values shown, not blanks. Each wrong revenue also feeds revenue growth, net margin, P/S, EV/S, and sometimes TTM. Sizes the workers give: AXP Q2 -43%, AMT Q2 -92%, CEG Q2 -22% and Q1 -32%, KMI Q2 -8.5%, DUK -2.0%, FCX -1.6% (Q2) and -2.8% (FY), WMT Q2 -1.0%, CP -0.65%, USB FY +8.5% overstated, WMB base row +10.7% (Q2) and +55.7% (Q1). Per-company cell counts: not stated.
- **FC exemplars:**
  - AMT 10-Q 0001053507-26-000133 R4: stored Q2 revenue_sanity 211.1M (6M 427.2M, tag `RevenueFromContractWithCustomerExcludingAssessedTax`), filed "Total operating revenues" `Revenues` 2,749.1M (6M 5,486.6M). TTM net margin shows 41.8%, about 32% correct.
  - WMT 10-Q 0000104169-26-000154 R2: stored Q2 FY27 186,100 (net sales), filed total revenues 187,937 (adds membership income 1,837). Every earlier WMT period resolves to `Revenues`.
  - USB 10-Q 0000036104-26-000044 R4: stored Q2 7,598 (`InterestAndDividendIncomeOperating`, gross interest income), filed NII 4,361 + noninterest income 3,325 = 7,686. FY2025 (10-K 0000036104-26-000011 R4) stored 30,970 vs filed 28,540.
- **Mechanism (workers' wording):** for banks, the priority-4 provisional tag (gross interest income) outranks `RevenuesNetOfInterestExpense` (S005 F2). For non-banks, the "Revenue-row fix is pinned per period; new quarters fall back to the ASC 606 tag" (S016 NEW-A), and "the later (incremental) resolve chose a different tag than the full resolve" (WMT resolved_at 2026-09-27 vs 2026-09-08, S002 NEW-4). S016 NEW-B: a "606 is a subset" rule fails in the other direction at WMB.

## T2 Operating income derived or taken from a non-face line

- **Companies affected: 17 with a wrong or stale operating-income value shown.**
  - FILING-CHECKED (10): ELV(S014, 1,763M looks like a segment "operating gain" total), ETN(S009), JCI(S014), ADP(S012), SHW(S017), TRV(S017), BX(S017, derived), SLB(S019), HOOD(S015, base blank but `operating_income_resolved` derived 574M), JNJ(S002, 2015 value, face has no subtotal).
  - DATA-INFERRED (7): WELL(S008, derived -1,650M, double subtraction), DE(S008, 9,039M FY2024, suspected segment note), TJX(S008, FY2019 value), GE(S004, FY2012 22,887M and Q2 2014), BMY(S010, Q1 2012), KLAC(S006, 2015), AXP(S006, 2010). LLY(S001) shows operating_margin 0.2594 from FY2019.
  - Correctly blank, no subtotal presented (cascade to EBITDA, ROIC, interest coverage): CVX(S003), LLY(S001), MRK(S004), PFE(S008), XOM(S002), COP(S007), PSX(S011), HCA(S013), EMR(S015), IBM(S006), NEM(S010), PGR(S010), MPC, BMY, KLAC. Cascade sizes quoted: CVX 10, COP 12, PSX 12, HCA 21 + 6, MRK 8+.
- **Cells:** wrong or stale values counted as filled (operating_income, `_resolved`, operating_margin, ROIC, interest coverage). Exact cell totals not stated.
- **FC exemplars:**
  - ETN 10-K 0001551182-26-000007 R3 and 10-Q 0001551182-26-000030 R2: stored FY2019 3,675M and latest quarter Q4 2013 767M; filed income statement has no operating-income subtotal.
  - ELV 10-Q 0001156039-26-000060 R4: stored Q2 `operating_income_resolved` 1,763M; filed R4 goes from total expenses to income before tax 1,937 with no such line. 1,763 = operating revenue 49,826 - benefit 37,024 - products 5,492 - operating expense 5,547.
  - ADP 10-K 0000008670-26-000030 R3: stored 424.3M at 2014-09-30 (revenue minus `OperatingExpenses`); filed has no subtotal.
- **Mechanism:** "Known no-subtotal plus stale family (#3, GE)" and "segment-note value mapped as consolidated (#7)" (S014 W4, S012 W11). WELL: "the derived operating income subtracts cost of revenue AND an `OperatingExpenses` total that already includes it" (S008 NEW-3).

## T3 Latest 10-Q or 10-K has 0 facts in core.fact (or filing absent)

- **Companies affected: 15 with a periodic filing in `core.filing` and 0 facts, plus 1 missing filing.**
  - FILING-CHECKED that the filing has XBRL (0 facts is DI in all): CB(S009), HCA(S013), DUK(S013), GD(S014), JCI(S014), CDNS(S015), MDLZ(S016).
  - DATA-INFERRED: KO(S003), V(S002), C(S006, two 10-Qs), ABT(S007), NEE(S008), WELL(S008), SPGI(S010), PLD(S011).
  - Possibly missing filing (DI): DE(S008, no Q3 FY2026 10-Q in `core.filing`; companyfacts last fetched 2026-08-22).
  - Checked and absent: S017, S018, S019 (none). TRV(S017) `_resolved` rows lag one filing, "a one-day timing lag, not a family".
- **Cells:** every latest-quarter value and every TTM at the company is one quarter stale. Per-cell counts not stated.
- **FC exemplars:**
  - CB 10-Q 0000896159-26-000017 (filing id 814522): R2/R4/R6 show revenue 15,816, NI 2,854, diluted EPS 7.30; 0 rows in `core.fact`.
  - HCA 10-Q 0001193125-26-321077 (filing id 743296): revenue 20,230, NI 1,699, EPS 7.62.
  - GD 10-Q 0000040533-26-000032 (filing id 268741): revenue 14,094, NI 1,160, EPS 4.24.
- **Mechanism:** "The VERIFY-W2 #3 family: companyfacts lacks the accession" (S015 W6); S006 N4 "Ingestion or normalization gap". Counter-evidence worth noting: for SPGI companyfacts was refetched 2026-10-06 and for NEE 2026-10-15, after the 10-Q dates, so a stale payload is not the whole story.

## T4 shares_outstanding blank, stale or wrong; market cap on the wrong share basis; per-share cascade

- **Companies affected: about 33.**
  - FILING-CHECKED wrong market cap (S000, 10): AKTX, ZLAB, SCNI, KZIA, AMRN, GPCR, DBVT (ADS ratio), TBLA, RPAY (filer scale x1000 on diluted WASO), SPCX (multi-class cover not summed, understated). 7 are inside the top-1000 list (6 overstated, 1 understated).
  - FILING-CHECKED wrong share count shown: ACN(S009, 2010), CME(S012, 2010), UPS(S016, 2010), REGN(S016, 2012), CMCSA(S017, 2009), MA(S002, 2010), HOOD(S015, 0 at 2021), DDOG(S015, 0 at 2019), USB(S014, rounded narrative 1.6B vs 1,555M). DASH(S017), ABNB(S012), NET(S012), SPCX(S002) have cover shares only per class (blank cells).
  - DATA-INFERRED: SHOP(S006, shares 0 at 2015), META(S001, no undimensioned count, market cap with NULL `source_fact_ids`), V(S002, 2010), DELL/QCOM/NEE/SPGI (S005, S007, S008, S010, count rounded to millions, market cap = rounded shares x price).
  - Cover-date share alignment (no share count on a balance-sheet date, so BVPS, net cash/share, Piotroski blank): appears at about 40 companies across S003-S019 (for example KO, CVX, ABBV, MRK, TXN, CRWD, LIN, ABT, PEP, COP, PFE, SCCO, MPC, BMY, VLO, PH, MCK, PSX, SYK, GLW, FCX, TT, WMB, MCO, EOG, MDLZ, RCL, NOC, HPE, ORLY, RSG, TGT, HLT, MSI, CP, ROST, KMI, KKR, GM). Exact count not stated.
- **Cells:** META 10 per-share cells blank, V 8, ACN 8, CME 8, UPS 7, HOOD 5, DDOG 5, SHOP 2, SPCX 6, RPAY 6. S000: market cap wrong in 10 rows out of 1,300 checked.
- **FC exemplars:**
  - AKTX 10-Q 0001493152-26-037730: stored 155,758,529,533 ordinary shares (`dei:EntityCommonStockSharesOutstanding`), market cap $1,274.1B; ADS = 80,000 ordinary shares, so 1,946,982 ADS-equivalents, corrected $0.016B.
  - TBLA 10-Q 0001840502-26-000012: stored diluted WASO 290,505,359,000 (YTD), $999.3B; cover 252,115,754 + 18,039,644 = 270,155,398, corrected $0.93B.
  - ACN 10-K 0001467373-26-000049 R1: stored 637,016,143 at 2010-03-19; cover Class A 668,722,814 + Class X 300,673 (dimensioned only).
- **Mechanism (S000 wording):** "There is no ADS or depositary ratio anywhere" (`price_metrics.py` line 362); "WASO fallback with no plausibility check"; multi-class covers are dimensioned and stripped by companyfacts; WASO tie between discrete quarter and YTD row (SPCX); "a rounded narrative fact wins the FY shares cell" (S014 NEW-3).

## T5 Stale series counted as filled

- **Companies affected: effectively all 189.** Every file with filing access found stale "latest" values; the coverage definition counts any past period as filled.
  - FILING-CHECKED stale-as-current examples (non-exhaustive): ETN, JCI, ADP, SHW, TRV, BX, SLB, HPE, GLW, LOW, SBUX, SNOW, NET, ABNB, SNPS, MRSH, CDNS, HWM, EMR, APP, HOOD, NSC, RSG, TGT, LITE, MAR, FCX, EQIX, DUK, TT, APH, MELI, WM, CSX, PWR, T, SCHW, STX, NOW, ACN, BA, CB, KKR, KMI, GM, ITW, CL, NOC, RCL, CI, EPD, CMCSA, WBD, ECL, MU, WMT, AMD, JNJ, MA, V, JPM.
  - DATA-INFERRED: remaining S003-S008, S010, S011 companies (e.g. VRTX, NEM, PGR, FTNT, MPC, VLO, BMY, DE, TJX, PFE, TMUS, KLAC, TMO, RTX, PANW, MS, WFC).
  - Hidden-blank counts from the coverage code (S014 NEW-1): `has_value` is true if ANY period had a value while `gap_reason` is read from the latest period. Workers counted: S014 79 cells (JCI 16, GD 14, AEM 13, MELI 9, ELV 8, ICE 5, PWR 4, CSX 4, USB 3, WM 3), S018 65 (KKR 17, GM 13, KMI 12, ITW 6, HLT 6, CP 3, CL 3, ROST 3, MSI 2, CNI 0), S019 69 (SLB 16, LITE 12, RCL 8, NOC 6, RSG 6, TGT 6, HPE 6, CMI 4, ORLY 3, NSC 2). Total 213 hidden blanks in 30 companies. Other shards not counted.
- **Cells:** wrong-as-current values (measurement problem, not coverage gap) plus the 213 hidden blanks above. Worst ages quoted: AEM whole page FY2009-2013 (S014 W6), CDNS gross margin 94.47% from 2012, INTU gross margin 82.27% from 2020, VRTX total_debt 105.0M from 2011, LOW interest expense 86M from 2011, MRSH accounts_receivable 5M from 2011, TRV operating income from 2015, AXP operating margin 91.4% from 2010.
- **FC exemplars:**
  - SNPS 10-Q 0000883241-26-000025 R4: stored interest_expense 1.324M at 2024-01-31, coverage 266.3x; filed Q3 133.2M (`InterestExpenseNonoperating`), coverage about 2.7x.
  - MRSH 10-Q 0000062709-26-000258 R4: stored accounts_receivable 5M at 2011-06-30; filed "Net receivables" 8,548M (`ReceivablesNetCurrent`).
  - CDNS 10-Q 0000813672-26-000092 R3: stored gross margin 94.47% (2012); filed cost of sales 239.3M, gross margin 84.9%.
- **Mechanism:** S014 NEW-1, code read of `coverage_matrix.py` around L740-750: `bool_or(value is not null)` across all periods. The 80.86% baseline is "overstated by about 0.5 point per company in this shard" (S014). Population-wide count not run (55 s MCP cap).

## T6 True zero shown as blank, and total_debt unmapped, wrong or stale

- **Companies affected: about 90 with a total_debt problem; about 12 with a true-zero problem.**
  - True zero or debt-free shown blank or stale: FILING-CHECKED ISRG(S009, 16 cells, no debt line on the face); DI VRTX(S010, 2011 value stands), PLTR(S003), ANET(S006), SHOP(S006, 11 cells), GEV(S005), AKTX(S001), WM and CMI and AMT (buyback absent quarters block TTM, S014/S019/S016), TSLA(S001), DDOG buybacks(S015), PLD(S011). No-dividend cells for non-payers with no reason: VRTX, FTNT(S010), SNOW, ABNB, NET(S012), LITE(S019), ORLY(S019), AMD, NOW, UBER, DASH.
  - total_debt wrong, FILING-CHECKED: MU, WMT(S002); SCHW, UBER, BA, STX(S009); MAR, ADBE, BNY, EQIX(S013); CME, NET(S012); CDNS(S015); CMI, SLB, LITE(S019); GM, KKR, CL(S018); GD(S014); BX, CTAS(S017/S016); LLY(S001, base row), DASH/HOOD/DDOG/SNOW convertibles unmapped.
  - total_debt DI: ABBV, INTC, CVX, UNH, PG, ORCL, CSCO(S003); DELL, TMO, RTX, GEV, WFC, PANW(S005); IBM, CRWD(S006); ADI, PEP, VZ, COP, GILD, QCOM(S007); PFE, TMUS, NEE, TJX, DHR, SCCO, UNP(S008); MPC, VLO, SPGI, BMY, LMT, PGR, FTNT, VRTX(S010); CVS, MDT, PSX, PH, BKNG, COF(S011).
  - Hit counts the workers give: S003 7/10, S005 6/10, S007 6/10, S008 7/10, S009 5/10, S010 8/10, S011 6/10, S013 8/10, S015 6/10, S016 8/10 (base row only; resolved correct at 10/10).
- **Cells:** mostly the base `total_debt` row is wrong while `total_debt_resolved` is right (S003, S013, S016); in 20+ cases the resolved row is itself wrong (omits short-term borrowings, current portion, or an unmapped tag). Blank cascade when debt is missing: debt_to_equity, net_cash, net_cash_per_share, ROIC, Piotroski, zero_debt, debt_to_ebitda, net_debt_ebitda (8-11 cells per company).
- **FC exemplars:**
  - MAR 10-Q 0001048286-26-000035 R5: stored total_debt 23M (`LongTermDebt`); filed 460 + 16,455 = 16,915M. Understated about 735x; net_cash +439M should be about -16.5B.
  - CME 10-Q 0001156375-26-000047 R2: stored base total_debt 0 (`ShortTermBorrowings`); filed long-term debt 3,424.2M (`UnsecuredLongTermDebt`, unmapped).
  - ADBE 10-Q 0000796343-26-000156 R2: stored total_debt_resolved 4,766 (`LongTermDebt` = noncurrent only); filed current 1,597 + 4,766 = 6,363.
  - UBER 10-Q 0001543151-26-000032 R2: stored 14,720M; filed 12,723M (`LongTermDebt` already includes the 1,997 short-term; double count).
- **Mechanism:** "`total_debt` sums whichever of {LongTermDebt, ShortTermBorrowings, DebtCurrent, SecuredDebtCurrent} is present; in 10-Qs only ShortTermBorrowings = 0 is tagged, so the sum is 0" (S003 W1); `DebtCurrent` + `LongTermDebt` double count (S003 F1, DELL, TMO, UBER); unmapped tags `UnsecuredLongTermDebt`, `ConvertibleDebtNoncurrent`, `ConvertibleLongTermNotesPayable`, `LongTermDebtAndCapitalLeaseObligations*`, `LoansPayable`, `ShortTermBankLoansAndNotesPayable`, plus custom current-debt tags (SLB). A zero-borrowings ruling (E3) keeps debt-free cases blank.

## T7 Wrong or missing blank reasons

- **Companies affected: about 45 with a wrong reason; the 4 universal unexplained cells at all 189.**
  - False `pre_revenue_biotech_pharma`: LLY(S001), JNJ(S002), ABBV(S003), MRK(S004), AMGN(S005), GILD, ABT(S007), PFE(S008), VRTX, BMY(S010), MRNA, REGN(S016). All DI except GILD/ABT (DI too; revenue figures from stored facts).
  - False `pre_revenue_mining_exploration`: SCCO(S008 DI), NEM(S010 DI), FCX(S013 FC, 7.0B quarterly revenue).
  - False `financial_institution_interest_income_not_revenue`: MO(S010 DI), PGR(S010), GD(S014 FC), HPE and ORLY(S019 FC), KKR and TRV(S018/S017 wrong text for an asset manager and an insurer).
  - Mortgage-REIT reason on equity REITs: WELL(S008 DI), PLD(S011 DI), AMT(S016 FC).
  - `no_dividend_history` at dividend payers: XOM(S002), C(S006), DHR(S008), GD(S014), REGN(S016), VRT(S017 FC), EPD(S017 FC).
  - `line_not_presented_in_filing` / `line_in_filing_not_extracted` contradicted by the face: SCHW(S009 FC), HCA, TRV, EOG, HOOD, and the CostsAndExpenses cases (T16).
  - Dividend-family cells with no reason at non-payers while the streak cell has one (NEW-6 S012, NEW-C S010).
  - Universal cells: bdc_total_investment_income (non-BDCs), collaborative_arrangement_revenue, employee_count, net_lease_revenue: counted unexplained at essentially every company (S001 F12: 40 cells for 10 companies). `dei:EntityNumberOfEmployees` is tagged by only 177 companies (S003); T, ETN and CSX do tag it.
- **Cells:** reasons shown to users would be false; counts per reason: PFE 5 cells, MO 1, WELL 9, PGR 12, EPD false no-dividend plus 25 unmapped cells.
- **FC exemplars:**
  - SCHW 10-Q 0000316709-26-000031 R2: stored interest_income reason `line_not_presented_in_filing`; filed "Interest revenue" 4,146 (`InterestIncomeOperating`) on the face.
  - VRT 10-Q 0001628280-26-050609 R6: stored `no_dividend_history`; filed dividends paid 47.8M (6M 2026), 28.4M (6M 2025).
  - FCX 10-Q 0000831259-26-000036: stored `pre_revenue_mining_exploration`; revenue 7.0B for the quarter.
  - HPE 10-Q 0001645590-26-000080 R2: stored `financial_institution_interest_income_not_revenue` on gross_profit and operating_expenses; HPE is IT hardware (financing income 192).
- **Mechanism (S010 NEW-E):** `mapper/coverage_matrix.py` `classify_concept_gaps`: "the `exists (... co2.tag = any(_FINANCIAL_INCOME_TAGS))` test has no period, size or SIC limit"; the pharma reason "seems to be assigned by SIC 2834 alone" (S001 W4). Population gate: `bdc_total_investment_income` carries `applicable_population = bdc_company` but is still in the matrix for non-BDCs (S003 F9).

## T8 Negative or meaningless ratios shown as numbers

- **Companies affected: about 24.**
  - Negative equity (ratio arithmetically right but meaningless): ABBV(S003, D/E -11.9, P/B -85.4, ROE -106%), DELL(S005, D/E -24.15, ROE -797%), PM(S004, D/E -5.72, ROE -1.27), MCD(S008, D/E -38.97, ROE -859%), MO(S010, D/E -9.21, P/B -46.94, ROE -298.8%), MCK(S011, ROIC 1,640%), BKNG(S011), HCA(S013), MAR(S013, ROIC -63.7%), LOW(S012, D/E -5.05, P/B -14.9, ROE -89%), SBUX(S012), HLT(S018), ORLY(S019, D/E -3.82, P/B -39.3, ROE -144%).
  - Near-zero or thin positive equity: CL(S018, P/B 319.2, ROE 864%), MA(S002, ROE 290%, P/B 97), STX(S009, ROE 146.9%), BA(S009, ROE 39.9%), APP(S015, ROE 139%, ROIC 123%), SHW (ROE 69.7%), MMM (101.5%).
  - ROIC on zero or negative invested capital: FTNT(S010, -222.6%), GEV(S005, 128.9%), ABNB(S012, 63.4%, customer funds).
  - YoY growth on a negative base: COF(S011, eps_growth_yoy -155%, net_income_growth_yoy -171%, a loss turning into profit).
  - All DI except LOW, SBUX, HCA, MAR, HLT, ORLY, CL, STX, BA (equity read from the face, FC).
- **Cells:** shown values: D/E, P/B, ROE, ROIC, net_cash; counts per company 2-4. Not blanks.
- **FC exemplars:**
  - LOW 10-Q 0000060667-26-000117 R2: stored D/E -5.05, P/B -14.9, ROE -89%; filed equity -7,437M.
  - ORLY 10-Q 0000898173-26-000045 R2: stored D/E -3.82, P/B -39.3, ROE -144%; filed deficit -1,835.7M.
  - CL 10-Q 0000021665-26-000042 R4: stored P/B 319.2, ROE 8.64, D/E 33.1; filed Colgate equity 236M (total incl. NCI 566M).
- **Mechanism:** no "not meaningful" rule; "the CAGR metrics already null this case; YoY does not" (S011 N2); ROIC "divides positive NOPAT by negative invested capital" (S010 NEW-A).

## T9 fiscal_year / fiscal_period label wrong

- **Companies affected: 3 with a stated label problem, 4 more counted without a check.**
  - DATA-INFERRED: PG(S003 W6: 2025-06-30 labeled fiscal_year 2025 / Q3, 2024-12-31 labeled 2025 / Q1; Piotroski reports missing total_assets(2025)), ADP(S012 NEW-4: `core.period` labels Jul-Sep Q1, Oct-Dec Q2, Jan-Mar Q1, Apr-Jun Q2 every year, so fiscal Q3 never exists).
  - Counted only, not re-derived: TT(S013), CB(S009), SPGI(S010; "known re-presentation (#5)").
  - TTM fails on 12/12/12/16-week or 13-week calendars (blank, not mislabel): COST(S003, 10 cells), PEP(S007, 4 cells), TJX(S008, suspected), GD(S014, dividend_yield, suspected).
  - Handled correctly: TGT and LITE (S019, 53-week years), MU 53-week not checked, STX 53-week TTM not checked.
- **Cells:** ADP 15 price-based TTM cells blank plus Piotroski and zero_debt; PG 1 (Piotroski); COST 10.
- **FC exemplars:** none. No worker opened a filing to check a period label.
- **Mechanism:** "fy/fp placement for a June-year-end filer; breaks domain rule 8.1" (S003 W6); "derive fiscal_period from the company's fiscal year end and start/end dates, not from the filing's fp" (S012 NEW-4). COST: "the TTM builder appears to reject the 111-day Q4" (S003).

## T10 Recast, restated, spun-off, predecessor comparatives; missing quarters inside the last 8

- **Companies affected: about 40.**
  - Re-presentation basis break: MMM(S016, FC), GE(S004 DI, 8-K recast 0000040545-23-000137 mixed into 2021-22 quarters).
  - Rounding-scale duplicates treated as conflicts, no authoritative fact (S006 N1: 82 tag-periods, ANET 30, MRVL 24, CRM 13, SHOP 8, C 3, KLAC 2, AXP 1, IBM 1; also PGR 2024 quarters S010 W11, LLY precision duplicates S001 F1, GOOG buybacks 28,706M vs 28,306M S001 F11). ANET FC on the cause (facts read), others DI.
  - Stock split not in split table or mixed basis: KLAC(S006 DI, 10-for-1, Q4 EPS -22.61), BKNG(S011 DI, 25-for-1, trailing_pe 1.23 should be about 18); ORLY 15-for-1 not checked.
  - Predecessor registrant or successor CIK cuts history: XOM(S002, predecessor CIK 34088 not in `core.company`), BLK, DIS(S007), AVGO(S001), MRVL, LIN, SHOP(S006), CI(S017), HWM(S015, Alcoa history shown as current), plus spin-offs GEV(S005), SNDK(S007), CEG(S013), MDLZ n/a, and IPO-limited history at about 25 companies (PLTR, UBER, SNOW, ABNB, NET, DASH, HOOD, APP, DDOG, CRWD, MRNA, VRT, ...).
  - Missing quarters inside last 8: LLY (2025 Q2/Q3, FY2024 balance sheet missing), GOOG (2025 Q2/Q3 buybacks), AMT (Q3/Q4 2025 buybacks), CEG (Q1 2026 buybacks), WM, CMI, ORLY (absent-component TTM), DE (Q3 FY26 filing missing).
- **Cells:** LLY 6 blanks plus Piotroski and 2 per-share cells; ANET whole 2024-12-31 balance sheet; MRVL FY2022 quarters; MMM revenue 5y -6.2% and 10y -1.6% CAGR wrong; KLAC Q4 EPS wrong and EPS CAGR 3y/5y/10y wrong; BKNG trailing_pe and EPS CAGR wrong.
- **FC exemplars:**
  - MMM 10-K 0000066740-25-000006 R3: FY2022 net sales re-presented as 26,161 and operating income 4,369 (continuing basis); stored FY2021 35,355 (original, 10-K 0000066740-22-000010) sits next to it.
  - ANET: 10-K 0001596532-25-000028 reports Assets 14,043,921,000; four later filings (for example 0001596532-26-000013) report 14,043,900,000; all five copies `is_authoritative=false`, no canonical value for 2024-12-31 (DI on the resolver; facts FC by stored values only).
  - XOM 10-Q 0000034088-26-000093 R1: combined two-registrant filing (Exxon Mobil Corporation and ExxonMobil Holdings Corporation); CIK 0000034088 absent from `core.company`, 46 period_gap cells.
- **Mechanism:** "A rounding-scale change is treated as a conflict, and the period is not conflict-filled although the gap is 0.00015%" (S006 W9); "latest filed wins re-presents only the periods inside the later filings' comparative window" (S016 NEW-D); split missing from `company_stock_split` (S011 W2).

## T11 Net income basis inconsistent (ProfitLoss / consolidated vs attributable; proxy copies; equity incl. NCI)

- **Companies affected: about 20.**
  - FILING-CHECKED wrong: SCHW(S009, DEF 14A copy in $ thousands read as dollars, resolver then falls back to available-to-common), FCX(S013, ProfitLoss incl. NCI, 23 rows since 2022), AMT(S016, +2.3%), CMI(S019, +3.9%), T(S009, equity 126,434 includes NCI 15,990; ROE and P/B skewed), MRSH(S015), HOOD(S015), CSX(S014, immaterial 0.04%).
  - DATA-INFERRED wrong: MDT(S011, FY2022-26 net income about 10^6 too small, 5 derived Q4 negative -2.6B to -3.6B, ROE 0.86% vs about 10.4%), NFLX, HD(S004, DEF 14A $1M or $10M rounding wins over authoritative 10-K), MRK(S004, FY2021 12,345M vs 13,049M, 5.4%), FTNT(S010, 0.002%, provenance only), ProfitLoss rows also at APH, CEG, EQIX, BNY (S013, small NCI, not checked).
  - Provenance-only (values equal 10-K): CAT(S004), BKNG and PH(S011), APH, FCX FY2021-25 (sole source DEF 14A).
- **Cells:** net_income (base and `_resolved`) for FY2021-25 plus derived Q4s (5 per company at NFLX, HD, MDT); downstream ROE, net margin, payout ratio, P/E. FCX TTM NI about 4,183M vs about 2,945M attributable.
- **FC exemplars:**
  - FCX 10-Q 0000831259-26-000036 R3 (and 10-K 0000831259-26-000012 R3): stored Q1 2026 net_income_resolved 1,387M (`ProfitLoss`); attributable = 6M 1,865 - Q2 984 = 881M.
  - SCHW 10-K 0000316709-26-000009 R3: stored FY2025 / FY2024 / FY2023 8,417 / 5,478 / 4,649M (`NetIncomeLossAvailableToCommonStockholdersBasic`); filed 8,852 / 5,942 / 5,067. Base row holds DEF 14A 0001193125-26-142826 R2 value 8,852,000 (unscaled "000s", 1000x too small).
  - CMI 10-Q 0000026172-26-000029 R2: stored Q2 968M (`ProfitLoss`); filed attributable 932M.
- **Mechanism:** "Proxy (DEF 14A) and 8-K values win over authoritative 10-K copies" (S004 family 1); MDT "breaks the hard rule 'is_authoritative=false is a hard filter'" (S011 N3); "when a filing does not tag `NetIncomeLoss`, the resolver falls back to `ProfitLoss`" (S013 NEW-1).

## T12 Capex, D&A, interest expense, receivables tags unmapped, stale or split

- **Companies affected: about 150 company-hits (workers' own counts, not de-duplicated by me).**
  - Interest expense, `InterestExpenseNonoperating` / net tags not mapped, value stuck at 2024 or earlier: summed worker hit counts about 99 (S002 7, S005 6, S006 6, S007 6, S008 5, S009 5, S010 6, S011 7, S012 5, S013 6, S014 8, S015 7, S016 5, S017 5, S018 8, S019 7), plus 7 interest_coverage blanks in S004. Other tags: BA/NOC/TXN/CME `InterestAndDebtExpense`, MS/WFC/PNC/USB `InterestExpenseOperating`, SCCO `InterestCostsIncurred`.
  - D&A filed as `Depreciation` + `AmortizationOfIntangibleAssets` (no combined tag), custom tags, or `Depreciation` only: about 30 (GOOG, MSFT, AVGO, ABBV, ORCL, TXN, GEV, IBM, GILD, ADI, ABT, UNP, DHR, PGR, PH, PWR, SHW, INTU, ITW, USB, SYK, GLW, CEG, ISRG, ACN, SCHW, MAR, LITE, EPD, CSCO suspect W7). 5 EBITDA cells blank per company.
  - Capex tag drift, custom or absent: VZ, COP, PSX, NEE, VLO, GLW, ADP, EQIX, FCX (segment-only), CI (custom), EOG (13 cells, never stored), WELL, PLD, HOOD, DDOG, LLY, NVDA, MS, ABNB, APP, TRV and insurers/banks (no capex line, FCF chain not applicable).
  - Receivables: `IncreaseDecreaseInReceivables` unmapped (CAT, PM, HD, IBM, KLAC? no; DIS, QCOM, MU, DE, MCD, LMT, MO, BMY, T, NOW, EMR, HWM, MRSH, ELV, CL, ITW, EOG, MDLZ, SHOP, SLB, ADBE, CEG, DUK, MCK, PSX, ...), `ReceivablesNetCurrent` unmapped (LMT, MO, ETN, LOW, XOM, CDNS, MRSH, WMB, CI, ITW, ROST, SLB, MCK, GEV, COST, TT).
- **Cells:** interest_expense, `_resolved`, interest_coverage_ratio, net_interest_income per company 3-5; D&A + 5 EBITDA cells 7 per company; EOG capex chain 13; PSX 13; NEE 17; cf_ar_change + reconciliation 2 per company.
- **FC exemplars:**
  - GLW 10-Q 0000024741-26-000255 R6: stored capex 986M at 2020-09-30 (`PaymentsToAcquireProductiveAssets`); filed "Capital expenditures" 754M (6M, `PaymentsForCapitalImprovements`). Blocks 8 FCF cells.
  - EOG 10-Q 0000821189-26-000149 R7: stored capex none; filed additions to oil and gas properties 3,129 (`PaymentsToAcquireOilAndGasPropertyAndEquipment`) + other PP&E 297 (6M).
  - LOW 10-Q 0000060667-26-000117 R2: stored interest_expense 86M at 2011-01-28; filed only "Interest - net" 374M.
- **Mechanism:** tag vocabulary frozen at an older generation of tags ("period-scoped tag sets", S005 F4); "A capex tag drift leaves capex and FCF 6+ years stale" (S007 N4); custom extensions are absent from companyfacts (domain rule 8.9), so some cases (CI `ci_PaymentsForProceedsFromPropertyPlantAndEquipment`, SLB `slb_ShortTermBorrowingsAndLongTermDebtCurrent`, MSFT D&A) cannot be fixed from companyfacts.

---

## T13+ Other themes found

### T13 Sector templates: bank, broker, insurer, asset manager, exchange, MLP, REIT, captive-finance
- Companies (FC and DI mixed): JPM, BAC, MS, GS, WFC, C, AXP, COF, USB, PNC, BNY, SCHW, HOOD, KKR, BX, BLK, CB, TRV, PGR, CI, ELV, UNH, MRSH, CME, ICE, ADP, EPD, WELL, PLD, AMT, EQIX, GM (captive finance), DE.
- Cells: bank rows `not_applicable` about 42-63 per bank (155 for WFC+GS+MS); bank metrics still shown: D/E (WFC 0.14, GS 3.57, MS 3.37, C 1.73, AXP 1.72, USB 1.42, PNC 1.34), net_cash, fcf_yield, ev_sales. Banks' net interest income and interest income unmapped while `InterestIncomeExpenseNet` and `InterestAndDividendIncomeOperating` are on the face (WFC, MS, USB, PNC, C, AXP, GS wrong NII -59,217M). NA cells need the X2 face-line check before showing a reason (S005, S006, S007, S008, S013). MLP template: EPD 25 cells (`PartnersCapital`, LP distributions, per-unit tags unmapped; reach 101, 49, 60, 36, 39 active companies). Customer-fund balance sheets make current ratio and ROA meaningless: CME (performance bonds 158.1B of 194.7B assets), ADP (43.96B of 63.2B), ICE (122B), MRSH, INTU, HOOD. Insurer cash flow has no capex, so 13 FCF cells blank (TRV). BDC cell filled at an insurer: TRV 4,012M (S017 W9 FC).
- FC exemplar: CME 10-Q 0001156375-26-000047 R2/R6; EPD 10-Q 0001061219-26-000021 R2/R6; GM 10-Q 0001467858-26-000051 R4 (debt only on `gm_BusinessGroupAxis` members).
- Mechanism: "industrial template applied to a non-industrial statement"; fix-register #1 / #1a.

### T14 Population: foreign private issuers, trusts, acquired companies
- Companies: BMO(S011, 154 blanks, rank 105), BNS(S012, 152 blanks, "10-Ks" are covered-bond ABS, 0 facts, 0001140361-21-002628), AEM(S014, never filed a 10-K, 66 blanks, rank 132), CNI(S018, never filed a 10-K, 151 blanks), IAU and SLV (S000, SIC 6221 trusts, ranks 211 and 367), WBD (S017 FC: acquired 2026-10-06, Form 25 and Form 15-12G, still `active`, market cap $77,782M at a 2026-10-05 price, 8-K 0001193125-26-415055, 15-12G 0001193125-26-423513). SLB (S019) correctly a domestic filer.
- S000 listed 8 large companies missing from the ranking because market_cap is null: BRK-A, FWONA, BAM, PLNT, UHAL, SUN, ENB, TSM.
- Mechanism: population is `status='active'` minus SPAC and trust reasons with no form check (S014); "classify by the latest annual form (40-F/20-F)" (S011 N1).

### T15 Gross profit from a partial cost line, member-only cost lines, and CostsAndExpenses
- Partial cost line gross margin shown: UNH 88.6%, CVX 43.6%, ELV 89.1%, WM 40.9%, EPD 25.6% (about 12.5% correct), CI 20.6%, COP 50.9%, RCL 49.1%, RSG 42.0%, KMI 48.9% stale, CVS 44.5%, VZ stale, MPC 12.5%, BMY 70.2%. Mostly FC (ELV, WM, EPD, RCL, RSG, KMI).
- Cost of sales filed only on Product/Service members, so gross profit stale or blank: GD, CDNS, INTU, SLB, NOC, HPE, GM, REGN (FC).
- `CostsAndExpenses` is opex at some filers (ORCL, CME, MRVL, HLT, V, CEG, DUK, EOG, UPS, AMT, WMB, CMCSA) and includes COGS or interest at others (STX, ACN, UBER, HCA, GE, CVX, ABBV, UNH, AMGN, TMO, SBUX, ELV, DASH): 33 cells across S003-S019 carry one gap reason for both cases (S013 NEW-7).

### T16 Dividend and DPS derivation
- V(S002 NEW-1 FC): FY DPS 0.59 is the quarterly rate; derived Q4 -1.18; TTM DPS 0.75 vs 2.52; dividend_yield 0.187% vs about 0.63%. 10-K 0001403161-25-000089 R8.
- WMT(S002 NEW-3 FC): payout_ratio 0.0000 for Q2 (annual dividend declared once, in Q1); 10-Q 0000104169-26-000154 R6.
- PGR(S010 W12): variable annual dividend inflates TTM yield 6.36%. Q4 DPS not derived, yield blank: SHW, TRV, MAR, AMGN, PH, GD, DHR, NEM, BKNG, DIS, PEP, ADP, GLW.
- Wrong or missing `PaymentsOfOrdinaryDividends` mapping: GE, PFE, DUK, CL, HWM, EOG, GLW, JNJ, ACN (blank dividends_paid at payers).

### T17 EPS only per share class or only continuing operations
- V(S002 FC, 11 cells), KKR(S018 FC, 3 cells), ABNB(S012 FC, 10 cells, `IncomeLossFromContinuingOperationsPerDilutedShare` 1.37), GD(S014 FC, no quarterly diluted EPS since Q4 2019).

### T18 Currency basis
- CP(S018 NEW-1 FC): statements in CAD, USD market cap divided by CAD values; P/B 76.7B / 46,626M = 1.645 exactly; P/E, P/S, P/B understated about 28%, yields overstated about 39%. 10-Q 0000016875-26-000026.

### T19 Market cap without lineage, and definition questions
- Market cap with `source_fact_ids` NULL: META(S001 W5), ABNB, NET, CME(S012), DDOG(S015), V(S002).
- Definition questions (not called wrong): BX market cap excludes Holdings units (S017), ACN cover count vs WASO (S009), MRNA price $215.80 from a single Alpaca row, unverified (S016).
- EntityPublicFloat scale errors (S000 1d): ONTO $4,817B, TTMI $4,166B, SKY $4,136B, OLED $6,792B, NOVT $3,497B, ENVA $2,670B, CBT $4.4e15, WTTR $837B, CRD-A $240B, RPAY $399.7B; too small: ARES $0.33B, LB $0.002B, PTCT $0.003B. Latent WASO scale errors: WAT 98.2B, NTNX 0.29M, CYTK 0.13M, LOAR 0.10M, IOVA 0.45M, MCD about 0.

### T20 Derived Q4 across mixed signs and impossible derived signs
- DIS(S007 N1): FY interest_expense -1,812M (10-K sign flipped, FY2021-25) vs positive in 10-Qs; derived Q4 -3,208M, -3,608M, -3,445M. SEC companyconcept (live) confirms the filer's own sign. RPAY derived Q2 2025 capex -69,000 (S004). COP sga_expense Q1 2020 -3M (S007).

### T21 Provenance and traceability
- Derived Q4 fact attributed to DEF 14A and marked authoritative: FTNT fact 183100851 (S010 NEW-H). CAT, BKNG, PH, APH, FCX show a proxy filing as only source. TRV/PGR `_resolved` rows lag one filing.

---

## Per-company verdicts

No file has its own verdict table, so every line is **DERIVED** by me. Rule: NOT CLEAN = at least one wrong, stale-as-current, or wrongly-reasoned value found for the company; CLEAN = none found (it does not mean zero blanks; the four universal cells and other explained blanks may remain). Columns: TICKER | shard | rank-or-mcap if in file | wrong values (worker ids) | blanks (total; unexplained split only where the file gives it, S017 only) | verdict. "Rank" appears only where S000 or S011/S014 state it. Evidence for S001, S003-S008, S010, S011 is DATA-INFERRED; a CLEAN verdict there means only "no problem seen in our tables".

NVDA | S001 | not stated | W2 total_debt vs resolved disagree (possible double count) | 5 | NOT CLEAN
AAPL | S001 | not stated | none found | 6 | CLEAN (DI)
GOOG | S001 | not stated | none found as wrong value; open conflict F11 (buybacks 28,706M vs 28,306M) | 20 | CLEAN (DI, open conflict)
MSFT | S001 | not stated | none found | 13 | CLEAN (DI)
AMZN | S001 | not stated | none found (P3 plausibility flag only) | 18 | CLEAN (DI)
META | S001 | not stated | W5 market_cap with NULL lineage | 24 | NOT CLEAN
AVGO | S001 | not stated | W2 total_debt 61,671 vs 61,079 | 15 | NOT CLEAN
TSLA | S001 | not stated | W2 total_debt double-count pattern | 22 | NOT CLEAN
AKTX | S001 | S000 shard rank 9 | W6, market cap $1,274.1B (true $0.016B), P/B 68,519, EPS 0.00 | 62 | NOT CLEAN
LLY | S001 | not stated | W1 base total_debt, W3 stale 2019 operating margin, W4 false pre_revenue reason | 30 | NOT CLEAN
MU | S002 | not stated | W5 total_debt_resolved, W9 stale | 13 | NOT CLEAN
WMT | S002 | not stated | W2 payout 0%, W3 revenue perimeter, W6 total_debt, W9 D&A | 16 | NOT CLEAN
JPM | S002 | not stated | W10 known bank values | 63 | NOT CLEAN
AMD | S002 | not stated | W9 stale (D&A 2023, public_float 2023) | 16 | NOT CLEAN
XOM | S002 | not stated | NEW-5 history lost, false no_dividend_history | 88 | NOT CLEAN
V | S002 | not stated | W1 DPS, W4 no EPS, W7 shares 2010, W8 0-fact 10-Q | 42 | NOT CLEAN
SPCX | S002 | S000 shard rank 18 (true about 6) | market cap $709.8B vs true about $1,917.6B | 82 | NOT CLEAN
JNJ | S002 | not stated | W9 operating income 2015, false pre_revenue reason | 16 | NOT CLEAN
MA | S002 | not stated | W7 shares 2010, thin-equity ratios | 24 | NOT CLEAN
TBLA | S000 | S000 shard rank 11 | market cap $999.3B (true $0.93B) | not in S002 | NOT CLEAN
ABBV | S003 | not stated | W1 total_debt 0, W5 false reason, negative-equity ratios | 18 | NOT CLEAN
INTC | S003 | not stated | W1, W2 total_debt | 6 | NOT CLEAN
CVX | S003 | not stated | W1 debt, W4 partial gross margin | 29 | NOT CLEAN
PLTR | S003 | not stated | none found; population bug (dividend_family_ever_reported) | 28 | CLEAN (DI)
COST | S003 | not stated | none found; TTM fails on 52/53-week (10 blanks) | 27 | CLEAN (DI)
CSCO | S003 | not stated | W2, W3 total_debt, W7 D&A 700M suspect | 9 | NOT CLEAN
KO | S003 | not stated | Q2 2026 10-Q has 0 facts | 18 | NOT CLEAN
ORCL | S003 | not stated | W1 total_debt 7,199 vs 129,541 | 16 | NOT CLEAN
PG | S003 | not stated | W1 debt, W6 period labels | 9 | NOT CLEAN
UNH | S003 | not stated | W1 debt, W4 gross profit 88.6% | 19 | NOT CLEAN
MRK | S004 | not stated | W3 FY2021 net income, W10 false reason | 23 | NOT CLEAN
BAC | S004 | not stated | W5 revenue = gross interest income | 62 | NOT CLEAN
RPAY | S004 | S000 shard rank 33 | W8 scale error, market cap $340.6B (true $0.37B) | 33 | NOT CLEAN
CAT | S004 | not stated | none found (W4 provenance only) | 13 | CLEAN (DI)
LRCX | S004 | not stated | none found | 4 | CLEAN (DI)
GE | S004 | not stated | W6 operating income 2012, W7 recast | 13 | NOT CLEAN
AMAT | S004 | not stated | none found (W12 interest-coverage latest blank) | 7 | CLEAN (DI)
PM | S004 | not stated | W9 negative-equity ratios | 8 | NOT CLEAN
HD | S004 | not stated | W2 proxy net income | 14 | NOT CLEAN
NFLX | S004 | not stated | W1 proxy net income FY2021-25 | 29 | NOT CLEAN
DELL | S005 | not stated | W2 total_debt, W8 negative equity, W10 rounded shares | 5 | NOT CLEAN
MS | S005 | not stated | W1 revenue, W6 bank metrics, W7 stale | 59 | NOT CLEAN
PANW | S005 | not stated | W7 debt metrics FY2023, W8 coverage 414x | 23 | NOT CLEAN
RTX | S005 | not stated | W3 total_debt 229M, W7 stale | 17 | NOT CLEAN
GS | S005 | not stated | W1 revenue, W5 NII, W6 | 47 | NOT CLEAN
TMO | S005 | not stated | W2 total_debt, W7 stale | 9 | NOT CLEAN
WFC | S005 | not stated | W1 revenue, W4 total_debt_resolved, W6 | 60 | NOT CLEAN
TXN | S005 | not stated | none found beyond blanks | 20 | CLEAN (DI)
GEV | S005 | not stated | W3 total_debt 63M, W8 ROIC 129% | 44 | NOT CLEAN
AMGN | S005 | not stated | W9 false pre_revenue reason | 8 | NOT CLEAN
CRWD | S006 | not stated | W6 stale interest coverage | 35 | NOT CLEAN
LIN | S006 | not stated | none found | 23 | CLEAN (DI)
ANET | S006 | not stated | W6 stale 2014, W9 FY2024 balance sheet dropped | 20 | NOT CLEAN
SHOP | S006 | not stated | W4 shares 0, W6 stale | 50 | NOT CLEAN
KLAC | S006 | not stated | W3 Q4 EPS -22.61, W6 stale | 7 | NOT CLEAN
IBM | S006 | not stated | W5 total_debt 5.8B vs 67.8B | 23 | NOT CLEAN
C | S006 | not stated | W2 2026 10-Qs 0 facts, W6, W7, W8 | 49 | NOT CLEAN
AXP | S006 | not stated | W1 revenue 11.2B vs 19.6B, W6, W7 | 44 | NOT CLEAN
MRVL | S006 | not stated | W9 FY2022 quarters dropped | 14 | NOT CLEAN
CRM | S006 | not stated | W9 13 rounding-dropped tag-periods | 12 | NOT CLEAN
GILD | S007 | not stated | W5, W6, W9 | 17 | NOT CLEAN
ADI | S007 | not stated | W5, W6 | 16 | NOT CLEAN
DIS | S007 | not stated | W1 interest-expense sign | 32 | NOT CLEAN
SNDK | S007 | not stated | none found as wrong value (P3 plausibility unverified) | 39 | CLEAN (DI)
VZ | S007 | not stated | W3 capex/FCF 2019, W4, W5, W6 | 20 | NOT CLEAN
ABT | S007 | not stated | W2 Q2 10-Q 0 facts, W6, W9 | 22 | NOT CLEAN
QCOM | S007 | not stated | W5, W8 rounded shares | 12 | NOT CLEAN
PEP | S007 | not stated | W5, W10 | 19 | NOT CLEAN
COP | S007 | not stated | W3 capex/FCF 2022, W5, W7, W11 | 25 | NOT CLEAN
BLK | S007 | not stated | none found as wrong value; N2 predecessor history cut | 49 | CLEAN (DI)
DE | S008 | not stated | W2 operating income, W8 Q3 filing missing, W11 | 23 | NOT CLEAN
UNP | S008 | not stated | W4, W5 | 35 | NOT CLEAN
MCD | S008 | not stated | W6 negative-equity ratios | 28 | NOT CLEAN
TMUS | S008 | not stated | W4 total_debt 6.1B vs 91.4B, W5, W11 | 15 | NOT CLEAN
PFE | S008 | not stated | W4 total_debt 2.7B vs 63.2B, W9 | 25 | NOT CLEAN
SCCO | S008 | not stated | W4, W9 | 21 | NOT CLEAN
NEE | S008 | not stated | W4, W7 Q2 10-Q 0 facts, W10 | 38 | NOT CLEAN
WELL | S008 | not stated | W3 operating income -1.65B, W5, W7, W9 | 54 | NOT CLEAN
TJX | S008 | not stated | W1 operating income FY2019, W4 | 10 | NOT CLEAN
DHR | S008 | not stated | W4, W5, W9 | 21 | NOT CLEAN
T | S009 | not stated | W6 equity incl. NCI, W8 stale | 16 | NOT CLEAN
SCHW | S009 | not stated | W1 net income FY21-25, W2 total_debt, W8, W10 | 52 | NOT CLEAN
ETN | S009 | not stated | W4 operating income from 2019 | 13 | NOT CLEAN
BA | S009 | not stated | W8 stale, W9 total_debt small, thin-equity ratios | 17 | NOT CLEAN
ISRG | S009 | not stated | NEW-B debt chain blank, should be 0 (16 cells) | 32 | NOT CLEAN
NOW | S009 | not stated | W8 interest income 2015 | 22 | NOT CLEAN
STX | S009 | not stated | W9 small, ROE 147% | 7 | NOT CLEAN
UBER | S009 | not stated | W3 total_debt double count | 29 | NOT CLEAN
ACN | S009 | not stated | W5 shares 2010 | 23 | NOT CLEAN
CB | S009 | not stated | W7 Q2 10-Q 0 facts | 61 | NOT CLEAN
MPC | S010 | not stated | W4 stale ppe, W5 total_debt 2.1B vs 32.8B, W13 | 11 | NOT CLEAN
VLO | S010 | not stated | W4, W5, W8 capex stops at 9M-2025 | 16 | NOT CLEAN
LMT | S010 | not stated | W4 stale interest, W5 | 14 | NOT CLEAN
VRTX | S010 | not stated | W3 total_debt 2011 value, W4, W9 | 22 | NOT CLEAN
PGR | S010 | not stated | W5, W11, W12 | 51 | NOT CLEAN
SPGI | S010 | not stated | W6 Q2 10-Q 0 facts, W5, W10 | 17 | NOT CLEAN
MO | S010 | not stated | W7 negative equity, W9 false reason, W4 | 15 | NOT CLEAN
NEM | S010 | not stated | W4, W9 | 24 | NOT CLEAN
FTNT | S010 | not stated | W1 proxy NI, W2 ROIC -222.6% | 16 | NOT CLEAN
BMY | S010 | not stated | W4 operating income Q1 2012, W9, W13 | 14 | NOT CLEAN
COF | S011 | not stated | W3 revenue, W4 YoY sign inversion, W5, W13 | 51 | NOT CLEAN
BKNG | S011 | not stated | W2 split (trailing_pe 1.23), W7, W14 | 19 | NOT CLEAN
PH | S011 | not stated | W8, W14 | 16 | NOT CLEAN
MDT | S011 | not stated | W1 net income x10^-6, derived Q4s, ROE 0.86% | 7 | NOT CLEAN
BMO | S011 | S000 rank 105, mcap $118.21B | W12 FPI in population | 154 | NOT CLEAN
CVS | S011 | not stated | W6, W8, W14 | 8 | NOT CLEAN
WDC | S011 | not stated | W8 stale; P1 plausibility unverified | 5 | NOT CLEAN
PLD | S011 | not stated | W10 Q2 10-Q 0 facts, W11 false reason | 55 | NOT CLEAN
MCK | S011 | not stated | W7 ROIC 1,640%, W8 | 12 | NOT CLEAN
PSX | S011 | not stated | W8, W9 | 34 | NOT CLEAN
ADP | S012 | not stated | W6 stale operating income, W13, NEW-4 labels | 41 | NOT CLEAN
BNS | S012 | mcap $113.2B | W14 FPI in population | 152 | NOT CLEAN
SYK | S012 | not stated | W11 D&A, W12 interest | 11 | NOT CLEAN
GLW | S012 | not stated | W4 capex 2020, W5 dividends 2014 | 31 | NOT CLEAN
LOW | S012 | not stated | W7 interest 2011, negative equity | 14 | NOT CLEAN
SBUX | S012 | not stated | W10 stale, negative equity | 12 | NOT CLEAN
SNOW | S012 | not stated | W9 stale interest income | 40 | NOT CLEAN
ABNB | S012 | not stated | W8 stale, NEW-2 EPS, ROIC 63% | 60 | NOT CLEAN
CME | S012 | not stated | W1 total_debt 0, W2 shares 2010 | 45 | NOT CLEAN
NET | S012 | not stated | W3 total_debt 0 at 2019, W8 | 38 | NOT CLEAN
HCA | S013 | not stated | W8 Q2 10-Q 0 facts, W11, negative equity | 36 | NOT CLEAN
TT | S013 | not stated | stale cash (NEW-9) | 14 | NOT CLEAN
MAR | S013 | not stated | W1 total_debt 23M vs 16,915M | 29 | NOT CLEAN
FCX | S013 | not stated | W2 net income incl. NCI, W3 revenue subset | 19 | NOT CLEAN
BNY | S013 | not stated | W7 revenue and debt | 50 | NOT CLEAN
EQIX | S013 | not stated | W9, W10 stale | 16 | NOT CLEAN
APH | S013 | not stated | stale interest_income 2017, base debt 2018; proxy NI rounding | 7 | NOT CLEAN
CEG | S013 | not stated | W4 revenue 5,843 vs 7,504, W12 | 41 | NOT CLEAN
ADBE | S013 | not stated | W6 total_debt omits 1,597M | 26 | NOT CLEAN
DUK | S013 | not stated | W5 revenue subset, W8 Q2 10-Q 0 facts | 21 | NOT CLEAN
PWR | S014 | not stated | W11 stale interest expense, PP&E | 23 | NOT CLEAN
AEM | S014 | S000 rank 132, mcap $94.3B | W6 whole page FY2009-2013 | 66 | NOT CLEAN
GD | S014 | not stated | W7 Q2 10-Q 0 facts, W9 gross margin 2019 | 12 | NOT CLEAN
MELI | S014 | not stated | W11 stale AP 2012, coverage -5.9 (2018) | 12 | NOT CLEAN
ELV | S014 | not stated | W3 gross margin 89.1%, W4 operating income | 27 | NOT CLEAN
USB | S014 | not stated | W1 revenue = gross interest income, W2 shares 1.6B | 65 | NOT CLEAN
ICE | S014 | not stated | W10 revenue perimeter | 19 | NOT CLEAN
WM | S014 | not stated | W5 gross margin 40.9%, W11 | 21 | NOT CLEAN
CSX | S014 | not stated | W11, W13 | 23 | NOT CLEAN
JCI | S014 | not stated | W7 Q3 10-Q 0 facts, W8 operating income 2016 | 9 | NOT CLEAN
EMR | S015 | not stated | W13 stale interest, base debt | 20 | NOT CLEAN
HOOD | S015 | not stated | W14 shares 0, capex, W18 | 62 | NOT CLEAN
MRSH | S015 | not stated | W8, W9, W10, W18 | 28 | NOT CLEAN
APP | S015 | not stated | W16 stale capex/interest/PP&E | 29 | NOT CLEAN
HWM | S015 | not stated | W11, W12 pre-separation history | 14 | NOT CLEAN
CDNS | S015 | not stated | W3, W4, W5, W6 Q2 10-Q 0 facts | 27 | NOT CLEAN
SNPS | S015 | not stated | W1 interest, W2 interest income | 17 | NOT CLEAN
INTU | S015 | not stated | W7 gross margin 2020 | 21 | NOT CLEAN
PNC | S015 | not stated | W17 stale interest, bank D/E shown | 63 | NOT CLEAN
DDOG | S015 | not stated | W15 shares 0, interest | 36 | NOT CLEAN
AMT | S016 | not stated | W1 revenue 211.1 vs 2,749.1, W2 | 17 | NOT CLEAN
MRNA | S016 | not stated | false pre-revenue reason; implied price $215.80 unverified | 29 | NOT CLEAN
WMB | S016 | not stated | W3 base revenue +11% to +56% | 18 | NOT CLEAN
MMM | S016 | not stated | W4 growth across Solventum re-presentation | 6 | NOT CLEAN
CTAS | S016 | not stated | base total_debt noncurrent only, stale interest | 8 | NOT CLEAN
MCO | S016 | not stated | opex 2020, R&D 2018 shown as current | 18 | NOT CLEAN
REGN | S016 | not stated | W5 shares 2012, false reasons | 19 | NOT CLEAN
EOG | S016 | not stated | capex never stored, W7 dividends 2009 | 41 | NOT CLEAN
UPS | S016 | not stated | W6 shares 2010 | 33 | NOT CLEAN
MDLZ | S016 | not stated | W8 Q2 10-Q 0 facts | 10 | NOT CLEAN
DASH | S017 | not stated | stale interest_expense (W10), false reasons | 51 (24 unexplained) | NOT CLEAN
SHW | S017 | not stated | W3 stale operating income | 19 (9 unexplained) | NOT CLEAN
ECL | S017 | not stated | stale D&A 2012 (W10) | 6 (3 unexplained) | NOT CLEAN
BX | S017 | not stated | W5 stale derived OI, W8 debt +0.9% | 43 (22 unexplained) | NOT CLEAN
TRV | S017 | not stated | W4 OI 2015, W9 BDC cell filled | 59 (26 unexplained) | NOT CLEAN
CI | S017 | not stated | W11 capex 2019, partial-cost gross margin | 24 (9 unexplained) | NOT CLEAN
EPD | S017 | not stated | W7 gross margin 25.6% vs about 12.5%, W12 | 38 (17 unexplained) | NOT CLEAN
VRT | S017 | not stated | false no_dividend_history | 20 (9 unexplained) | NOT CLEAN
CMCSA | S017 | not stated | W2 fcf_per_share 9.91 vs about 5.77 | 34 (12 unexplained) | NOT CLEAN
WBD | S017 | not stated; mcap $77,782M | W1 acquired and delisted, W6 stale | 38 (17 unexplained) | NOT CLEAN
HLT | S018 | not stated | W8 interest 2024, W10 negative equity | 22 | NOT CLEAN
ITW | S018 | not stated | W7 pretax stuck at FY2023, W8 | 22 | NOT CLEAN
KKR | S018 | not stated | W5 debt 2021, EPS 2018, FCF 2019 shown | 54 | NOT CLEAN
MSI | S018 | not stated | none found | 10 | CLEAN (FC for headline and debt; interest current)
CP | S018 | not stated | W2 revenue, W3 CAD/USD mix, W8 | 26 | NOT CLEAN
ROST | S018 | not stated | W8 interest 2020 | 19 | NOT CLEAN
CL | S018 | not stated | W6 near-zero equity ratios, debt -0.4%, W8 | 14 | NOT CLEAN
KMI | S018 | not stated | W1 revenue -8.5%, W8, W9 | 7 | NOT CLEAN
CNI | S018 | not stated | W11 FPI never filed a 10-K | 151 | NOT CLEAN
GM | S018 | not stated | W4 debt by business group, W9 gross margin 2021 | 8 | NOT CLEAN
RCL | S019 | not stated | W8 ppe, W9 interest, W10 gross margin 49.1% | 19 | NOT CLEAN
NOC | S019 | not stated | W9 no interest expense, W11 gross profit 2018 | 13 | NOT CLEAN
LITE | S019 | not stated | W1 debt FY2025 10.6M vs 2,573.2M, W6, W7, W8, W9 | 24 | NOT CLEAN
SLB | S019 | not stated | W2 debt, W3 cash 2015, W11, W12 | 24 | NOT CLEAN
NSC | S019 | not stated | W9 interest 2024, W13 opex 2019 | 29 | NOT CLEAN
CMI | S019 | not stated | W4 net income incl. NCI, W5 debt | 10 | NOT CLEAN
HPE | S019 | not stated | W11 gross profit 2020, W14 total liabilities 2018, W15 false reason | 7 | NOT CLEAN
ORLY | S019 | not stated | W15 false reason, W16 negative equity | 21 | NOT CLEAN
RSG | S019 | not stated | W8 ppe 2020, W9, W10 gross margin 42.0% | 13 | NOT CLEAN
TGT | S019 | not stated | W8 ppe 2024, W9 interest 2024 | 14 | NOT CLEAN

Also named in S000 (not in a block A shard list above): ZLAB (shard rank 387, mcap $26.0B vs true $2.60B), SCNI (688, $10.6B vs $0.003B), KZIA (933, $6.2B vs $0.012B), AMRN (about 1100, $4.75B vs $0.24B), GPCR (about 1130, $4.58B vs $1.53B), DBVT (about 1460, $2.68B vs $0.54B), IAU (211, trust), SLV (367, trust). All FILING-CHECKED (market cap) or DATA-INFERRED (trusts). CRWD (rank 51) and KLAC (rank 55) flagged by S000's automatic checks and cleared as real splits (FC). Verdict for the S000 names: NOT CLEAN.

Tally of my derived verdicts for the 189 block A companies: CLEAN 14 (AAPL, GOOG, MSFT, AMZN, PLTR, COST, CAT, LRCX, AMAT, TXN, LIN, SNDK, BLK, MSI), NOT CLEAN 175. Of the 14 CLEAN, 13 are DATA-INFERRED only; MSI is FC.

---

## History-window items

No worker ran a systematic first-period-held versus filing-history check or a FY2015 / FY2018 / FY2021 spot-check. What the files do say:

- **First period held versus filing history (share and balance sheet cells, stale base series):**
  - V shares_outstanding 469,280,842 at 2010-01-27; MA 122,530,193 at 2010-10-27 (S002, FC cover for MA); ACN 2010-03-19 (S009 FC); CME 2010-02-17 (S012 FC); UPS 2010-02-17 (S016 FC); CMCSA 2009-12-31; REGN 2012-09-30; HOOD 0 at 2021-12-31; DDOG 0 at 2019-12-31; SHOP 0 at 2015-12-31; JCI FY shares 2009; RPAY 6,468,750 at 2018-06-18 (SPAC era).
  - AEM: whole page from FY2009 (revenue) and FY2013 (NI, equity, assets, debt) (S014 W6 FC, SEC submissions: 40-F x13, 20-F x12, 6-K x489, no 10-K).
  - XOM: history starts Q2 2026 because predecessor CIK 34088 is not in `core.company`; SPCX: one 10-Q only after the 2026 IPO (S002).
  - VRTX total_debt 105.0M at 2011-09-30 stands as latest for a debt-free company (S010 W3).
  - KO: quarterly revenue 2015 to Q1 2016 filed only under unmapped `SalesRevenueGoodsNet` (authoritative, Q1 2016 10,282M, Q4 2015 10,000M), so 2015 canonical revenue is empty and the 2016_Q1 TTM base is missing (S003 F13, DI).
  - NVDA fcf_growth_5y: FY2021 (to 2021-01-31) capex missing in 0001045810-21-000010, -22-000036, -23-000017 (S001, DI).
- **10-year CAGR blanks because the 2016 base is missing:** AVGO (2016_Q3, predecessor CIK 1730168 dates from 2018 redomicile), VLO, WDC (2016 Q4), GLW (2016 Q2), PWR (2016_Q2), HCA (2016_Q1), APH (2016_Q2), PLD (2016 Q1), MRVL (2017_Q2; new CIK 1835632 in 2021), LIN (2016_Q2; Linde plc since 2018), SHOP (40-F era), BLK, DIS (predecessor CIKs, S007 N2), CI (2018 registrant), HWM (Alcoa), GEV (10 cells; spin-off April 2024), SNDK (9 cells; spin-off Feb 2025), CEG (4 cells; no pre-2022 base), PLTR (S-1 from 2018), UBER (post-2019), SNOW, ABNB, NET, DASH, HOOD, APP, DDOG, CRWD, MRNA (Dec 2018 IPO), VRT (2018), KKR (2018 conversion), TMUS (dividend initiated late 2023), CRM (dividends 2024), GOOG/META (dividends 2024), REGN (dividend 2025). Several are legitimate "history not available" cases, not data bugs (S009 NEW-H, S005 F10); the workers want the reason shown instead of a blank.
- **Missing quarter inside the last 8:**
  - LLY: 2025 Q2/Q3 discrete values never derived (H1-2025 duplicates 1,665.6M vs 1,666M, 4,752.5M vs 4,753M, 1,892.2M vs 1,892M marked non-authoritative); FY2024 balance sheet absent from `canonical_fact` (total assets, AR, AP, cash, current assets at 2024-12-31) (S001, DI).
  - GOOG: H1-2025 repurchases 28,706M (0001652044-25-000062) vs 28,306M (0001652044-26-000071), both non-authoritative, so discrete Q2/Q3 2025 missing (S001, DI).
  - ANET: whole 2024-12-31 balance sheet (30 tag-periods) and MRVL FY2022 quarters dropped (S006 N1).
  - AMT: Q3/Q4 2025 buybacks (no 9M 2025 fact); CEG: Q1 2026 buybacks, so the Q2 value equals the 6M value; WM: 2025 buyback quarters absent (treated as no data, not zero); CMI: 0 in 2025.
  - MAR and TT: Q4 2025 capex not derived (fcf_yield blank); SHW, TRV, MAR, PH, GD, NEM, BKNG: Q4 2025 DPS not derived.
  - KO, ABT, C (two quarters), NEE, WELL, SPGI, CB, HCA, DUK, GD, JCI, CDNS, MDLZ, PLD, V: latest quarter has 0 facts; DE: Q3 FY26 10-Q not in `core.filing`.
  - MMM: break between FY2021 and FY2022 (annual) and Q2 2022 / Q2 2023 (quarterly) because only periods inside the later filings' comparative window were re-presented (S016 NEW-D, FC).
  - MU FY2026 is a 53-week year; TTM construction not checked. TGT FY2023 (53 weeks, 371 days) derived Q4 of 98 days checked and correct (S019 FC).
- **FY2015 / FY2018 / FY2021 spot-check:** not performed as a labeled check by any of S000-S019.

---

## Population counts quoted

Query = the worker ran a count against the database or SEC; estimate = inferred or extrapolated. "Query?" is my reading of the file; where the file does not say, I mark "not stated".

| Shard | Count quoted | Query or estimate |
|---|---|---|
| S000 | 1,300 largest active market_cap rows checked (overall rank 1,300; shard rank 1000 = TFX = overall 1009) | query |
| S000 | 4,351 non-null and 866 null market_cap rows in total | query |
| S000 | 45 rows flagged by the automatic checks | query |
| S000 | 10 wrong market caps confirmed against filings: 7 inside the top-1000 (6 overstated, 1 understated), 3 below it | query + FC filings |
| S000 | 2 flags cleared as correct (CRWD, KLAC splits); 2 non-operating trusts in the list (IAU, SLV); 8 large companies missing from the ranking; 1 more ADS suspect (SLN, mcap/float 6.0, unchecked) | query |
| S000 | 10 EntityPublicFloat scale errors too large, 3 too small; 6 latent WASO scale errors (WAT, NTNX, CYTK, LOAR, IOVA, MCD) | query |
| S000 | proposed drop of 8 companies and backfill of 8 (SNDR, ASB, MBGL, BGC, ORA, NIQ, INSW, WFRD, then APLD, IMVT, FTDR, BCPC) | estimate (DATA-INFERRED, not filing-checked) |
| S000 | 14 SEC requests; 1,301-4,351 only covered by the foreign-issuer and null-cap passes | stated scope |
| S001 | 215 blank cells (1,630 - 1,415 filled); 93 with `gap_reason` NULL; 40 universal cells (10 x 4) | query (matches shards.csv) |
| S002 | 360 blank cells; 95 of 102 period_gap cells are XOM (46) and SPCX (49); 9 of 9 employee_count not tagged | query |
| S003 | 179 blanks (85 unexplained = shards.csv baseline); `EntityNumberOfEmployees` tagged by only 177 companies; `Depreciation` unmapped at 3,572 active companies; `ReceivablesNetCurrent` 739; `SalesRevenueGoodsNet` 745; `IncreaseDecreaseInAccountsAndNotesReceivable` 152; `InvestmentIncomeInterestAndDividend` 300 | blanks query; tag reach from `analytics.company_sec_tag` (query) |
| S004 | 206 blank cells (109 not_applicable, 40 unknown likely not_reported, 20 unknown other, 25 mapping_gap) | query |
| S005 | 292 blank cells (176 not_applicable); 53 cells suspected not_reported / custom; 155 bank cells | query |
| S006 | 277 blank cells; N1 82 tag-periods with all copies non-authoritative across 8 of 10 companies; 102 cells suspected / custom tag | query |
| S007 | 251 blank cells | query |
| S008 | 270 blank cells; total_debt composition hits 7 of 10 | query |
| S009 | 272 blank cells (matches shards.csv); 57 SEC pages read | query + FC |
| S010 | 200 blank cells; 62 SNR cells | query |
| S011 | 361 blank cells vs shards.csv baseline 224 unexplained (baseline predates the 2026-10-17 coverage rebuild); 154 BMO cells all FPI; "25 40-F and 5 40-F/A filings" for BMO | query |
| S012 | 444 blank cells (matches shards.csv); BNS "seven 10-K filings, 0 facts"; 152 FPI cells | query + FC |
| S013 | 259 blank cells (matches shards.csv); FCX 23 net_income_resolved rows since 2022 sourced from `ProfitLoss`; APH 4, CEG 3, EQIX 7, BNY 7 ProfitLoss-sourced rows | query |
| S014 | 277 blank cells (1,630 - 1,353 filled); 79 hidden blanks (real count about 356); AEM 1,607 us-gaap facts from 2006-2013, 2,754 `ifrs-full` facts; baseline 80.86% overstated by about 0.5 point per company in this shard | query; population-wide NEW-1 count not run (55 s cap) |
| S015 | 317 blank cells (matches shards.csv); 43 SEC requests | query + FC |
| S016 | 199 blank cells (163 x 10 - 1,431 filled); tag reach `PaymentsToAcquireOilAndGasPropertyAndEquipment` 60 and `PaymentsToAcquireOilAndGasProperty` 72 active companies; PP&E-incl-finance-lease tag candidate 647 companies | query (`sec_tag_library`) |
| S017 | 332 blank cells, 148 unexplained (reconciles to shards.csv); `PartnersCapital` 101, `PartnersCapitalIncluding...NCI` 49, `DistributionMadeToLimitedPartnerCashDistributionsPaid` 60, per-unit tags 36 and 39 active companies; `ConvertibleLongTermNotesPayable` 512; `InvestmentIncomeNet` 566; `CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization` 285; `PaymentsForRepurchaseOfEquity` 426; `LoansPayable` 462 | query (`sec_tag_library`), "not coexistence-checked" |
| S018 | 333 blank cells (1,630 - 1,297 filled); 65 hidden (real about 398) | query |
| S019 | 174 blank cells (1,630 - 1,456 filled); 69 hidden (10 correct reasoned, 59 real; real about 233) | query |
| S006/S008/S014 | 0-fact latest-filing family: S006 "2 of 20 with S003's KO", S008 "3 companies", S014 "at least 10 companies across S003-S014" | running tally by the workers; my own count of named companies is 15 |
| S014/S018/S019 | hidden blanks: 79 + 65 + 69 = 213 across 30 companies; population-wide count not run | query (shard level), estimate beyond |
| S014 | 1 FPI with no 10-K ever (AEM); S018 CNI "40-F x25 (2002-2026), 6-K x572"; S014 AEM "40-F x13, 20-F x12, 6-K x489" | query (SEC submissions JSON, FC) |
| various | "employee_count not tagged" 10/10 in S003-S010 and S013, S015-S016, S019; 9 of 10 in S002, S009 (T and ETN tag it), S014 (CSX tags it), S012, S018, S011 | query |
| various | "bdc cell counted at non-BDCs" 9-10 of 10 in every shard (KKR, TRV fill it) | query |
| Fix-register / status quoted | "15 banks with a wrong net_interest_income value" (S004), BAC not one of them | quoted from another doc, not a query here |
| S005 F13 | 20 population-mislabel cells (PANW dividend family 10 + bdc 10) | estimate from the shard |
| S000 | "full-population reach" of every proposed rule (MCAP-SHARES, R1-R5): not run; "re-run on all 4,351 rows" proposed | not run |

Reach counts that no worker ran against the full population (all NEW-n families): stated "not counted beyond this shard" in S002, S009, S012, S013, S014, S015, S016, S017, S018, S019. No worker gives a top-1000-wide number for any family except S000's market-cap pass (1,300 rows).
