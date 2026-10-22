# Digest DC (shards S039-S059, 210 companies)

Read-only synthesis of the 21 result files. No DB, no SEC, no code. Evidence labels are the workers' own: FC = FILING-CHECKED, DI = DATA-INFERRED. Accessions copied as written in the files. "Stale Q2" means the Q2 2026 10-Q is not in core.fact, so the page stops at Q1.

## Block

Read in full: S039, S040, S041, S042, S043, S044, S045, S046, S047, S048, S049, S050, S051, S052, S053, S054, S055, S056, S057, S058, S059. None missing or partial.

Caveats that apply to the whole block:
- Almost every worker checked only the latest 10-Q (or the latest 10-K) against the filing. FY2015/2018/2021 spot-checks were done only in S058 and S059, and mostly from memory (marked DI).
- Market-cap bands per shard, as stated: S040 24.8-26.0B; S043 22.4-23.6B; S044 21.2-23.2B; S045 21.2-22.5B; S046 20.5-22.2B; S047 19.4-20.7B; S053 15.9-17.1B (ranks 521-530); S054 15.0-16.1B; S055 14.5-15.7B; S059 13.2-13.8B. Other shards do not state a band. CRS is rank 479 (S048).
- All 210 companies carry the 4 "universal" unexplained blank cells (`bdc_total_investment_income`, `collaborative_arrangement_revenue`, `net_lease_revenue`, `employee_count`), except where a worker notes the cell is real (ARCC a BDC, VICI/REG/MAA lessors). Under a strict rule that alone makes every company NOT CLEAN.
- Theme ids T13 onward are additions (listed after T12).

---

## T1 revenue resolves to a partial / sub-line tag (or gross interest) instead of the statement total

Companies affected: 19 with a wrong stored value, 3 related.
- FC (stored vs filed read on the statement): AFRM(S041), L(S043), CRCL(S044), NRG(S044), KEY(S045), RF(S042), EWBC(S051), ESS(S051), BG(S047), SBAC(S047), SOFI(S049), TPG(S053), INVH(S053), CNH(S057), OHI(S058), OVV(S048), BURL(S053, 0.15%), DLTR(S042, 0.1%, definition ruling only), ZLAB(S039, excluded company).
- FC, stale/empty rather than partial: EQR(S043, revenue frozen at 2020 because `OperatingLeaseLeaseIncome` is unmapped), APA(S051, `revenue` empty, only `revenue_sanity_resolved` filled).
- DI only: none stated. Not wrong per the workers: FCNCA(S041), MKL(S043), GPN etc.

Cells: wrong values shown. Revenue cell itself plus every dependent ratio. Not stated as a count of cells, but each worker names the cascade (P/S, margins, growth, EV/sales, piotroski). Impossible displayed ratios: ESS Q2 net margin 28.87 and operating margin 47.18 (2,887% / 4,718%); OHI operating margin 2,365.9%; SBAC operating margin 685%; BG revenue below cost of revenue. Measurement problem: APA, where the base concept is blank and 14+ ratio cells read the empty base.

Exemplars (FC):
- AFRM: stored FY2026 revenue 1,443,922K vs Total revenue, net 4,261,082K (accession 0001628280-26-059279, R5); stored is the first sub-line "Revenue" only. P/S 17.2 vs about 5.8.
- CRCL: stored Q2 33,582K vs "Total revenue and reserve income" 701,315K (R4); source tag is the 606 tag while `Revenues` is also filed. P/S 163.2.
- BG: stored Q1 2026 4,660M vs Net sales 21,861M (Q1 10-Q R2); cost of goods sold stored 21,095M. Other FC cases in the same pattern: SBAC 51,389K vs 715,274K, OHI 13,987K vs 328,246K, ESS 2,318K vs 489,049K, TPG 704,969K vs 1,841,424K (0001880661-26-000049), INVH 49,460K vs 747,550K (0001687229-26-000045), SOFI 153,577K vs 1,218,676K, L 828 vs 4,734.
- Bank variants: EWBC 1,080,823K (Total interest and dividend income, `InterestAndDividendIncomeOperating`) vs net interest income + noninterest income 791,143K; RF 1,748 vs about 1,907; KEY 449M from `RevenueFromContractWithCustomer...` vs a face with no revenue line.

Mechanism (workers' words): "`RevenueFromContractWithCustomerExcludingAssessedTax` (a partial slice) wins over `Revenues`" (S047); "Revenue mapped to `InterestAndDividendIncomeOperating`, i.e. interest income, not bank total revenue" (S042); "Note-disclosure subset tag used as headline revenue for a bank" (S045). OVV: derivative gains and sublease revenue excluded from the stored line (needs a standardization ruling, same as DVN).

---

## T2 operating income derived or taken from a non-face line where the filer presents none (or a different figure)

Companies affected: about 31.
- FC, wrong value shown: CASY(S040), EQR(S043), TPG(S053), OHI(S058), MAA(S059), REG(S059), APA(S051), RF(S042, stray 53M `OperatingIncomeLoss`).
- FC that no line exists, stored value stale (shown as the latest in the series): NWSA(S053, 2019), WPC(S055, FY2015), CNH(S057, 2017), SWK(S058, 2024-09-28), BALL(S052, 2024-03), FTAI(S052, 2021-12-31).
- DI, stale: LPLA(S040, 2020-12-31), BRO(S043, 317 at 2024-09-30), INVH(S053, 2018).
- FC, no operating income line and the blank has no reason (blank right, explanation missing): BG(S047), Q(S041), BURL(S053), H(S053), WWD(S048), IP(S049), LEN(S049), SOFI(S049), GPC(S049), DD(S050), NI(S047, not stated either way), PHM(S045, DI), NVR(S054, wrong reason), FOX(S042, wrong reason), L(S043).

Cells: wrong values shown in 8 companies (above); the rest are stale or blank-without-reason. Dependent: operating_margin, roic, interest_coverage.

Exemplars (FC):
- CASY: stored 4,924,225K (FY26 14,723,675K on revenue 17,561,101K, an 87% margin) vs about 369,089K computed from the statement; derived as `Revenues - OperatingExpenses` where the filed `OperatingExpenses` (754,111) excludes cost of goods sold and D&A. The worker reproduced 5,678,336 - 754,111 = 4,924,225.
- EQR: stored 520.0 / 513.2 vs 218.9; filed `OperatingExpenses` 265.0 is property and maintenance plus real estate taxes only.
- TPG: stored Q2 -792,369K on a profitable firm (partial revenue 705.0M minus 1,497.3M); income before tax is 356,014K. MAA: 348,153K (62.9% margin) from `Revenues - OperatingExpenses` where `OperatingExpenses` excludes D&A and G&A (accession for MAA Q1 not given).

Mechanism: "Derivation valid only when `OperatingExpenses` is the statement's own cost subtotal (the DVN-class W3 family)" (S059); "resolver trusts the tag rather than the statement" (REG, OHI, APA take a filed `OperatingIncomeLoss` that is not on the face).

---

## T3 latest 10-Q/10-K has 0 facts in core.fact, or the filing is absent from core.filing

Companies affected: 23. All FC (filing read on SEC; zero-fact count itself DI in most files).
- 0 facts (21): PPL(S039, 0000922224-26-000044), VRSK(S040, 0001437749-26-024749), VLTO(S040, 0001967680-26-000044), HUBB(S041, 0001628280-26-050405), PPG(S042, 0000079879-26-000252), PFG(S042, 0001104659-26-088071), OMC(S043, 0000029989-26-000019), INCY(S044, 0000879169-26-000056), DOW(S045, 0001751788-26-000147), RS(S046, 0001104659-26-087528), BG(S047, 0001628280-26-050540), EVRG(S048, 0001711269-26-000100), WES(S049, 0001423902-26-000093), LNT(S050, 0000352541-26-000043), FTV(S050, 0001659166-26-000034), CLH(S052, 0000822818-26-000034), MAS(S056, 0000062996-26-000027), SUI(S056, 0000912593-26-000234), TRU(S057, 0001552033-26-000047), REG(S059, 0001193125-26-330021), MAA(S059, 0001193125-26-326153).
- Filing absent from core.filing (2): HEI(S052; SEC lists a 10-Q filed 2026-08-27, accession 0000046619-26-000020; no core.filing row for any 10-Q after 0000046619-26-000016), SJM(S059; Q1 FY27 10-Q 0000091419-26-000080 filed 2026-08-26; core.filing holds nothing after 2026-06-09, not even Form 4s).
- SEC companyfacts also lacks the accession for PPG, PFG, INCY, RS, BG, VRSK, VLTO, MAS, SUI (checked live by the workers). Not stated for the rest.

Cells: coverage/measurement. Every TTM, growth and market-cap-ratio cell for the company is one quarter stale (a full quarter or more for HEI and SJM). Wrong values shown: stale values presented as latest, e.g. VRSK equity -1,167.7M stored vs -1,189.0 filed; HUBB stored assets 8,417.7M vs 11,846.2M filed; OMC trailing_pe -219.4; BG trailing P/E 23.9 and P/B 1.24 on stale TTM; SUI Q1 view (assets 12.4B, trailing_pe 10.7) vs filed Q2 with net loss -1,024.9M incl. discontinued operations (EPS -8.08).

Exemplars (FC): PPL Q2 filed NI 230, EPS 0.30, assets 46,301 vs stored Q1 452 / 46,304; INCY Q2 revenue 1,674,039K, EPS 2.81 not stored; OMC Q2 revenue 6,562.5, EPS 2.08 not stored.

Mechanism: "filing ingested but XBRL facts not loaded" (S059); "Fix path as PLAYBOOK: parse the filing's own XBRL instance" (S047, S050). Several filers share agent prefix 0001193125 (S059). Population count was not run anywhere (timeouts).

---

## T4 shares_outstanding blank / stale / wrong, market cap on the wrong share basis, per-share cascade

Companies affected: about 40.
- FC, multi-class cover counts not summed (blank or stale/zero): CPNG(S039, DI), AFRM(S041, DI; latest 2020-12-31), ECHO(S041, DI; 2020-09-30), FCNCA(S041, none), FOX(S042, FC; stored 1 on 2019-03-18 vs 199,401,385 + 220,248,764), IOT(S042, FC; 380,273,036 + 205,332,173), ROKU(S043, DI), RL(S043, DI), STZ(S044, FC; EPS and shares also on class axis), RBRK(S044), CRCL(S044), ARXS(S044), TOST(S048, stored zero 2021), CBRS(S048, 112,247,109 + 111,601,424 + 13,715,508), WMG(S053; 2020), H(S053), TPG(S053), TSN(S055, FC; 281,792,507 + 70,009,005), LAMR(S055), PINS(S056, FC cover), CHTR(S057, FC), BF-A(S059, FC; stored 2025-04-30 472,669,000 vs 458,864,265 now), HEI(S052, stale 2025-10-31), ULS(S055, stale 2025-12-31), FDXF(S052, flat 149,505,248 by construction).
- FC, issued shares tagged as outstanding: IP(S049; 627,000,000 vs 529.6M), EG(S055; 74.5M vs about 38.7M), TYL(S056; 48,147,969 vs about 40.95M).
- FC, market cap on wrong basis: QSR(S039; 349.2M common vs diluted 460M incl. about 110M exchangeable units, market cap understated about 30%), PINS(S056; stored 15.32B vs about 13.05B, 665.1M stale shares vs about 566.3M).
- D1 per-share pairing (cover-date shares never meet the balance-sheet-date equity): `book_value_per_share` incomplete at essentially every company in the block (workers: 8 of 10 in S039; 10 of 10 in S040, S046, S047, S050, S051; 9 of 10 in S049, S052, S055; 8 of 10 in S054, S058). Equity is present and matches the filing where checked (FC). Also `net_cash_per_share`, piotroski `missing:shares_outstanding(2025)`.

Cells: coverage blanks plus some wrong values (PINS/QSR market cap, P/B, P/S, P/E affected; IP/EG/TYL per-share). Per-company cascade is about 6-10 cells (book value, net cash, fcf per share, dilution trend, total shareholder yield, piotroski, institutional ownership).

Exemplars (FC): FOX stored shares 1 vs 419.65M cover total; PINS (see above, cover 492,198,008 Class A + 74,115,019 Class B); IP stored 627M at 2026-03-31 and 2026-06-30 vs cover 529,516,974 / 529,569,895.

Mechanism: "per-class cover shares not summed into shares_outstanding" (S059); "filer reports issued shares under the outstanding tag" (S049). Population quoted: 497 companies with blank `shares_outstanding` (S044, S055).

---

## T5 stale series counted as filled (latest period years old, coverage says has_value)

Companies affected: about 28.
- FC (statement opened, current value exists): WMG(S053, EPS and shares 2020), KIM(S055, EPS 2020, capex ends at 0), WPC(S055, EPS 2018, capex 2018, op income 2015), HST(S053, capex 2019), INVH(S053, capex 2018), PAA(S050, equity 2017-09-30 -753M, diluted EPS 2016-12-31), NLY(S059, total_debt 2020 429,650,000, capex 2018), BR(S047, income_before_tax 2020-03-31), WY/JLL(S057, capex 2019), CNH(S057, capex 2016, op income 2017), TPL(S042, capex stops 2023-09-30, DI), SYM(S042, capex stops 2024-12-28), REG(S059, interest_expense FY2023), DD? (no).
- DI: TROW(S045, gross_profit_resolved 2012), DT(S051, total_debt 0 at 2023-03-31), MEDP(S051, total_debt_resolved 0 at 2019-12-31), ZBRA/IEX/APG/ESS(S051, interest_expense 2021-12 / 2024-06 / 2024-03 / 2024-06), GME(S059, interest_expense 2022), GDDY(S059, 2024-Q1), RL(S043, capex missing Q4 FY26), BEN(S054), GH(S046, accounts_payable stops 2021), LPLA, BRO, NWSA, BALL, FTAI, SWK (operating income, see T2).
- Anomaly not resolved (S056): UNM and RNR show no `operating_income_resolved` row after 2025-12-01 yet are not in the blank list.

Cells: wrong values shown or wrongly counted filled. Downstream wrong ratios: PAA price_to_book -23.84 (17.95B / -753M, the 2017 equity); NLY stale debt displays as current.

Mechanism: "old tag stopped being filed, stale value remains the latest with no flag" (S052); "the stale-latest rule is not catching these" (S050). Suggested detection by workers: latest period more than about 400 days behind the company's newest filing.

---

## T6 true zero shown as blank; total_debt unmapped / wrong / stale; reported zero not stored

Companies affected: about 40.
- FC, no debt on the statement but total_debt blank: LOGI(S055), TOST(S048), MEDP(S051), DOCU(S058), NBIX(S058), INCY(S044, finance leases only), CRCL(S044, convertible reported 0 at Jun 30 2026), TROW(S045, DI).
- DI, probably true zero, balance sheet debt lines not opened: CPRT, ZLAB(S039), EXPD, FFIV, ULTA(S040), TPL, IOT, SYM(S042), UTHR, ROKU(S043), ROIV(S041), DT(S051), EXEL(S054), SITM(S057), LSCC(S055), EG(S055).
- FC, real debt exists but not in total_debt: RBRK convertible 1,132,895K(S044), U 557,173K + 1,680,229K(S050), PINS 981,128K (`ConvertibleDebtNoncurrent` is in core.fact)(S056), GWRE 678,094K(S058), NTNX 1,348,711K(S049), YUMC short-term borrowings 66(S054), CDW (S048; `LongTermDebtCurrent` 1,008.9M + `LongTermDebtNoncurrent` 4,808.1M filed), MAA unsecured 5,331,445K + secured 360,456K(S059), GME 4,167.8M(S059, stale 10-K value), NLY (repos 86,895,874K etc.), LEN senior notes 4,297,251K(S049). EVRG (S048, DI values), SUI (S056 DI).
- Reported explicit zero not turned into zero: SMCI `share_buybacks` (Stock repurchases 0, FC) and PR (`PaymentsForRepurchaseOfEquity` = 0, DI) (S046).

Cells: coverage/measurement; each case blocks about 6-10 cells (zero_debt, debt_to_equity, net_cash, roic, piotroski, net_debt_ebitda, debt_to_ebitda). Population quoted: 1,698 companies have total_debt blank with no reason (S044, a query-like figure, method not stated).

Mechanism: "Reported zero is not turned into 0" (S044); "debt composite is built for some companies only" (S048: SNA yes, CDW/EVRG no).

---

## T7 wrong or missing blank reasons

Companies affected: all 210 in some form. Main sub-families:
- Financial-institution / REIT / pre-revenue reason on a wrong sector (FC): DGX(S039), ZLAB(S039, pre-revenue with 106M quarterly revenue), CHD(S041), FOX(S042, media), UTHR(S043, pre-revenue with revenue 783.3), JBHT(S045), SBAC(S047, `reit_net_interest_income_not_revenue`), CRS(S048), ITT(S050), CLH(S052), BALL(S052), HST(S053), TPG(S053), NVR(S054), NBIX(S058, pre-revenue with 959.0M quarterly revenue), JAZZ(S059, pre-revenue with revenue 4.6B in 6M), WY(S057), KIM/WPC/LAMR(S055), EQR(S043, reit label on rental REIT), BRO AR(S043, line exists), RGLD AR(S047, "Royalty receivables 131,708" exists).
- Insurer/bank/REIT/unclassified-balance-sheet cells with no reason (current_assets, current_ratio, quick_ratio, working_capital, inventory_days, payables_days, sga, cf_* changes): CINF, VICI(S039), LPLA(S040), FCNCA(S041), SYF, PFG, RF(S042), MKL, L, EQR(S043), KEY, GPN, PHM, TROW(S045), RGA, EWBC, ESS(S051), EG, WPC, KIM(S055), UNM, RNR, EQH, SUI(S056), PNFP, CNH(S057), AIZ(S058), NLY, MAA, REG(S059), CRBG, NVR(S054), LEN, SOFI(S049), PS(S050), OHI(S058), ARCC(S059).
- Non-dividend payer / no-buyback cells showing NO REASON or `missing:` instead of "pays no dividend" (only `dividend_growth_streak_years` has `no_dividend_history`): CPAY, CPRT, CPNG, ZLAB, SN(S039), FISV, FFIV, ULTA, ATI(S040), AFRM, ECHO, ROIV(S041), IOT, SYM, DLTR(S042), MKL, UTHR, ROKU(S043), RBRK, INCY, CRCL, ARXS, USFD(S044), THC(S045), GH, INSM, PTC, SMCI(S046), MTSI(S047), CBRS, TOST(S048), FSLR, NTNX, SOFI(S049), U(S050), DT, ZBRA, APG, MEDP(S051), RIVN, CLH, WCC, TLN, FICO(S052), BURL(S053), RBC, NVR, EXEL, PFGC(S054), MTZ, LSCC, ULS(S055), TYL, SOLV, PINS(S056), CRL, SITM(S057), DOCU, TRMB, GWRE, NBIX, HALO(S058), JAZZ, CACI, GDDY, GME(S059).
- False `no_dividend_history` on dividend payers (FC/DI): LPLA, VRSK, VLTO(S040), STZ(S044, DI), WES(S049), PAA(S050), SBAC(S047), CDE(S054, newly initiated dividend of 20,645K, FC).
- Missing "line not presented" explanations where operating income is truly absent: see T2. Contradictory reasons: GDDY(S059).
- The 4 universal cells.

Cells: reason text wrong or absent (blank itself is often right). Population quoted: see "Population counts quoted" (203, 328, 1,470, 189/789, 3,433, 142).

Mechanism: "reason labels are assigned by a rule that does not look at the statement" (S043); "sector label (SIC 2834) mapped to a pre-revenue reason without checking revenue" (S059).

---

## T8 negative or meaningless ratios shown as numbers

Companies affected: about 40.
- Negative trailing P/E shown (DI arithmetic; loss FC where noted): CPNG -32.5(S039), ZLAB -138.97, ECHO -3.43, ROIV -74.49(S041), OMC -219.38(S043), RBRK -90.44(S044), DOW -7.6125, GPN -28.43 (FC EPS -6.58 H1), VTRS -46.15(S045), LYB -56.28, GH -46.28, INSM -23.17(S046), IP -5.20(S049), GIS -20.12, U -29.43(S050), APG -66.44(S051), RIVN -4.84, TLN -87.32(S052), EQH -16.28(S056), CRL -65.53(S057), SJM -99.27(S059; becomes about +229.5 TTM once the stale Q1 FY27 is loaded).
- Negative/near-zero equity: GH roe +2.03, price_to_book -97.5, debt_to_equity -6.74, roic -2.07 (S046); SBAC P/B -4.18, ROE -21.4%(S047, FC deficit -4,629,854K); MAS P/B -62.17, ROE -345.9%(S056, FC equity -118/-242); EQH P/B -18.79; PAA P/B -23.84 (stale equity); GDDY P/B 2,064.7, ROE 13,587%, D/E 563.3 on equity 6.7M(S059); LVS P/B 42.3(S041); NTNX ROE 214%(S049); MEDP ROE 113%(S051); TPR ROE 221%(S042); HAS 108.7%, HALO 288.1%(S058); FICO book value should be negative(S052).
- Extreme positive: TPL 345.24 (wrong, T17), SYM 2,916, IOT 265(S042), SITM 848(S057), GPC 484.8(S049), H 211.7(S053); CPNG ROIC +154% with operating loss(S039, DI); LPLA trailing_pe exactly 25.9 (suspicious, S040).
- Impossible margins: see T1 (ESS, OHI, SBAC).
- PAA trailing_pe 6.49 inflated by 1,649 of 1,830 Q2 net income from discontinued operations (S050, FC split); DD trailing_pe 155.7 on mixed-basis TTM.

Cells: wrong values shown (display/guard problem, not a data error in most). Workers: PEG has the guard `non_positive_growth_not_meaningful`, trailing_pe/price_to_book/roe do not.

---

## T9 fiscal_year / period label wrong

Companies affected: 11 plus label drift on cover dates.
- FC vs SEC companyfacts `fy`: ULTA(S040; stored 2027 Q2 vs SEC 2026 Q2; FY ended 2026-01-31 stored 2026 FY vs SEC 2025 FY, accession 0001104659-26-035243), ROIV(S041; FY ended 2026-03-31 stored 2026 vs SEC fy=2025, 0001635088-26-000061), DLTR(S042; stored FY2027 Q2 vs `fy=2026`), EXEL(S054; Q4 ended 2026-01-02 stored 2026 Q4 vs SEC fy=2025, 10-K 0000939767-26-000021), SWK and TRMB(S058; Q4 ending 2026-01-03/02 labeled 2026).
- DI: LDOS(S054; same Jan-2026 pattern), NTNX(S049; cover count dated 2026-08-31 labeled FY2027, fp null), CRS(S048; cover 2026-08-07 labeled 2027), SMCI(S046; cover count fiscal_year 2027 null fp; CAGR lookups `prior_period(2016_Q4)` fail), BR and AMCR(S047; cover-date counts fiscal_year 2027, null fp, cosmetic), GEN(S057; possible quarter-label shift, DI), ARMK(S056; `prior_period(2023_Q3)`, DI), PS(S050; reorganization stub periods in core.period).
- Effect: TTM chain breaks. EXEL and LDOS lose trailing_pe, price_to_sales, ev_sales, ebitda_margin, fcf_yield; SWK/TRMB lose revenue_ttm, diluted_eps_ttm, cfo_ttm, ebitda_margin, ev_sales, price_to_sales, trailing_pe, fcf_yield, peg (all four quarters exist in canonical_fact, DI). Labels correct per workers: STZ, RBRK, STE, USFD, DT, BBY, RL.

Cells: label wrong (values align, per ULTA worker growth math unaffected) but TTM cells blank where the label breaks the window. Population: 38 companies have a Q4 ending 2026-01-01..09 labeled fiscal_year 2026 (a query, S054); 43 have the FY labeled 2025; 244 have any period ending in that window.

Mechanism: "fiscal year is taken from the calendar year of the period end date" (S040); "derived Q4 gets the calendar year of its end date" (S058).

---

## T10 recast / restated / spun-off / predecessor comparatives; missing quarters inside the last 8

Companies affected: about 13.
- FC: IFF(S043; stored Q1 2,741 vs recast 1,906, stored 6M 3,860 is not Q1+Q2; Q2 2025 row absent), AMRZ(S046; Q1 recast 2,181 vs original 2,178, CFO (893) vs (896), capex 275 vs 272; original facts `is_authoritative=false`, recast not promoted so no Q1 row; 2025 Q1/Q2 also missing), DD(S050; 9M 2025 8,720M old basis vs FY2025 6,849M recast, no standalone Q3 2025), FTV(S050; fcf_growth base restated for Ralliant spin), JAZZ(S059; 2025-Q1 897,841K and 2025-Q2 1,045,712K present in core.fact only as `is_authoritative=false`), PAG(S058; 2024Q3, 2025Q1-Q3 revenue missing, only 4 of the last 8 quarters, non-authoritative), SUI(S056; discontinued-operations reclassification, stale view differs materially).
- DI/structural: SN(S039; 20-F to 10-K, no standalone Q3/Q4 2025, TTM blank for revenue, cfo, EPS plus 15 cells, but FY - prior YTD + current YTD gives 6,909,956K), JHX(S055; 20-F to 10-K, price metrics blank), PNFP(S057; new registrant CIK, Q3-Q4 2025 and FY2025 revenue/EPS/assets absent; stored FY2025 equity 6,013 common-only vs 7,044 total), FDXF(S052; first 10-K only, TTM blank for a $16.4B company), PS(S050; reorg stub periods, first 10-Q 2026-06-04), CBRS/ARXS(IPO history), AMRZ spin history, QNTY (Q, S041 spin).
- Inside the last 8 quarters: PAG (4 of 8), JAZZ (2025-Q1, Q2 missing), AMRZ, IFF.

Cells: coverage/measurement (TTM, growth, P/S, EV/sales, fcf_yield blank) plus mixed-basis values (IFF, DD). Mechanism (S043): when a later filing recasts an earlier quarter the stored one stays; caution from root CLAUDE.md that "latest wins" cannot be validated against Frames, validate on statement arithmetic (IFF 3,860 - 1,954 = 1,906).

---

## T11 net income basis inconsistent (consolidated vs attributable), equity incl. NCI

Companies affected: 9.
- FC: QSR(S039; stored 445 / 665 / 1,110 vs attributable 507 / 845 for Q2 / 6M; ROE 0.442 overstated about 22%), CF(S049; 869 / 1,545 consolidated vs 727 / 1,342 attributable), FTAI(S052; `ProfitLoss` 125,094K / 262,993K vs attributable 117,585K after preferred dividends and redemption loss), BALL(S052; 223M vs 221M), LYB(S046; 559 / 684 vs 558 / 681), ECHO(S041; 6M stored 8,315,245K total vs attributable 8,315,487K, Q2 stored attributable), GIS(S050; two coexisting values -85.0 and -85.3M vs filed -85.3 incl. NCI, -87.6 attributable), CACI(S059; rounded 535,800,000 vs 535,808K).
- DI: ARXS equity tag `LimitedLiabilityCompanyLlcMembersEquity...` unmapped (S044, FC value 4,467,558K) is an equity-mapping gap, listed in T15.

Cells: wrong values shown (small to about 22%). Mechanism: "ProfitLoss (consolidated) is the source tag; EPS is on the attributable figure" (S052). Other companies in the block store attributable (RS, PR, AMRZ, FIS, LEN, RIVN, WCC).

---

## T12 capex (and D&A, interest expense, receivables) tags unmapped, stale or split; FCF/EBITDA cascades

Companies affected: about 75.
- Capex unmapped/stale/net-of-disposal (FC line exists unless noted): VICI(S039), PFG(S042, "Net purchases of property and equipment (101.4)"), SYM(S042, 62,753K combined line), TPL(S042, DI), EQR(S043, "Capital expenditures to real estate" 160.3), INCY(S044, "Capital expenditures" 22,613), PR(S046; `PaymentsToExploreAndDevelopOilAndGasProperties` 987,664K and `PaymentsToAcquireOilAndGasProperty` 534,304K), SNA(S048; `PaymentsForCapitalImprovements` 44.3M stored but unmapped, 13 FCF cells), ESS(S051; 51,326K), APA(S051; 1,111), HST(S053; 140 + 103), INVH(S053; 111,304K), TPG(S053), KIM(S055; "Improvements to operating real estate" 173,625K), WPC(S055; 71,233K), WY/JLL/CNH(S057), WES(S049, DI), PS(S050, DI), LNT(S050, DI), MAA(S059; `PaymentsForCapitalImprovements` unmapped), REG(S059, DI), RBC(S054, DI), RL(S043; Q4 FY26 missing), HEI(S052; YTD only), CRBG/RNR/EQH insurers (SNR), RGLD(S047; acquisitions of interests, standardization ruling needed). LEN(S049): Q3 capex derived by YTD difference goes negative (-8,019K vs filed 9M 40,829K).
- Banks/insurers with no capex line (NR-F, reason absent): SYF, RF(S042), EG(S055).
- Cascade: each missing capex blocks about 7-13 cells (fcf, fcf_margin, fcf_yield, fcf_per_share, fcf_gt_net_income, capex_pct_revenue, fcf_growth_*, dividends_pct_fcf, share_repurchases_pct_fcf). Counts named: SNA 13, PFG about 12, EQR 9, PR 17+, VICI 7, SYM about 10, TPL about 10.
- D&A unmapped or split in two lines: PPL, VICI(S039), NVT, BRO ("Amortization" 110 + "Depreciation" 18), EQR, CHTR(S057), MEDP, APG(S051), SJM ("Depreciation" 346.4 + "Amortization" 210.6)(S059), SBAC(S047), PAG(S058), SW(S045), PR (custom extension `pr:DepreciationDepletionAmortizationAndAssetRetirementObligationAccretionExpense`, FC line 1,026,448K)(S046). YTD-only D&A causes `ebitda missing:4_consecutive_quarters` plus 4-5 EBITDA ratios at many companies (e.g. CHD, XYL, HUBB, WWD, FISV, LAMR, CNH, TRU, MAS, RS, INCY).
- Interest expense unmapped/stale: Q (`InterestAndDebtExpense`, FC 61 / 122), PKG (net line), DD (FC "Interest expense" 41 / 81), ULS (FC 5 / 13), DLTR (DI), QSR (FC 124 / 247), NTNX, CHRW, ZBRA/IEX/APG/ESS stale, REG stale.
- Receivables/payables/inventory unmapped: NVT, BRO, RGLD, BBY (FC "Receivables, net 922"), J (FC 3,760,646K), CHRW (FC 3,055,149K), ARMK (FC 2,582,676K), MEDP, LUV inventory (FC 917), DLTR inventory, ULTA inventory, CDW AP (FC `AccountsPayableTradeCurrent` 5,117.4M), PFGC AP, ROL, GPC, HUBB, ITT, GIS, FTV and more. NVR: nested segment blocks.

Cells: coverage blanks; no wrong values except the LEN derived negative capex. Mechanism (S053): `ReceivablesNetCurrent` filed but not mapped (known row: LMT, MO).

---

## T13 dividends: payers with no DPS / YTD-only DPS or distributions unmapped; non-payers shown as gaps (additional)

Companies affected: about 28 payers.
- Payer, `dividends_per_share` or TTM missing, yield blank: CASY, EXPD, VLTO(S040), TPL, FOX(S042), STZ(S044), JBHT (DPS Q4 2025 stored -0.88, yield 0.20% instead of about 0.8%)(S045), EXE(S045; Q2 DPS missing though dividends_paid 138M), WWD(S048; "Cash dividends paid (54,902)" 9M, `dividends_paid` blank), SNA, PR, AMRZ(S046), LEN, CF, CW, GPC, WES (distributions per unit)(S049), PAA(S050), SBAC(S047), IEX(S051), TSN(S055), HEI(S052; `zero_base_value` for a semi-annual payer), CNH, PNFP, JLL(S057), SWK(S058), BF-A(S059; DPS annual only), NWSA(S053), RNR, EQH(S056).
- Sign/period error: JBHT DPS -0.88 (DI).
Cells: coverage blanks plus one wrong value (JBHT yield). Mechanism: "YTD-only per-share dividend tag" (AME family from S023); MLP distributions tags unmapped (S050).

## T14 institutional_ownership_pct blank `implausible:institutional_shares_exceed_shares_outstanding` (additional)

Companies affected: about 40 across the block: LPLA, FFIV, ULTA(S040), AFRM, ECHO(S041), SYF, DLTR, IOT, FOX(S042), IFF, OMC(S043), INCY, USFD, XPO(S044), GPN, THC(S045), ENTG 172.7M 13F vs 152.8M (113%), GH 144.0M vs 132.6M (109%), PTC 125.0M vs 115.5M (108%)(S046), EFX, CDW(S048), ZBH, FTV, DD(S050), ZBRA, IEX(S051), RVTY, HEI, WCC(S052), CHRW, HST, TPG, INVH, WMG, BURL(S053), EXEL, CRBG, PFGC(S054), LSCC(S055), RNR, ARMK, EQH, SUI, MKSI(S056), TRU, CRL(S057), GWRE, HALO(S058), JAZZ, GDDY(S059). DI. The blank is honest; cause not investigated by any worker (13F double counting or stale/coarse share base). Only S046 gives holder sums (DI).

## T15 unmapped face lines / derivable values hidden (additional)

- Pretax income unmapped: LH ("Earnings from operations before income taxes" 386.4 / 706.1, FC), NI (`IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic` 47,100,000), BR (`IncomeLossAttributableToParent` 1,445,800,000; stuck at 2020-03-31), CRL (`IncomeLossIncludingPortionAttributableToNoncontrollingInterest`, 53,170 / 23,228), AMCR, TPG, PFG, PHM, INVH, ARCC.
- Equity/EPS tags unmapped: ARXS equity 4,467,558K, WES "Total partners' capital" 4,258,306K and basic EPS 0.99, PAA partners' capital and per-unit EPS 2.51, RNR `EarningsPerShareDilutedUndistributed` (Q2 15.48, 6M 21.94, FC), STE (latest diluted EPS 2.04 under a continuing-ops per-share tag; latest stored diluted_eps is FY2026 7.93), STZ (class-axis EPS 3.32), KIM/WPC/WMG stale EPS.
- Gross profit / cost of revenue derivable but blank with "not presented": GH, PINS (FC revenue 1,179,654K, cost of revenue 257,354K), SOLV, ARMK, ULS (FC 399 / 394), DD, EFX (cost of services 773.7 / 1,540.7, `CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization`), MTZ, RVTY, WCC, BALL, RS, ROL.
- Operating expenses total on the statement not captured: DGX, QSR, CPNG (S039), AFRM, FCNCA, LVS, DRI (S041), MKL ("Total Operating Expenses" 3,625.6), WES, EFX, ROL ("Total operating expenses" 877,217K), BURL ("Total costs and expenses" 2,713,792K), H, PINS, FICO, CLH, NVR and others.
- Cash tag `us-gaap:Cash` unmapped (FDXF cash 251M), interest income lines (SOFI, FCNCA, KEY, EWBC), BDC investment income (ARCC: Total investment income 768.0 / 1,531.0; `bdc_total_investment_income` blank).
- `total_liabilities` blank where the balance sheet prints no total line (derivable): ENTG, PKG, LYB, BG, NI, SBAC, BBY, GPC, IP, CF, FOX, LNT, FTV, NDSN, TSN, CHTR, XPO, CDW, LUV, DGX, EXPD (about 25).
- `net_interest_income` blank on every non-financial with `incomplete:add/subtract` (10 of 10 in S047), while blank at banks that present it (RF, FCNCA, KEY).

## T16 TTM construction rules (additional)

- Four standalone quarters required: SN, JHX (20-F to 10-K switchers; FY + current YTD - prior YTD is exact, S039/S055), FDXF (only an annual period), PNFP, ARXS, PS.
- LSCC(S055): price/revenue/EBITDA TTM valid through 2026-09-29, `missing:revenue_ttm` since 2026-10-03 after Q2 (Jul 4 2026); worker hypothesis (untested): TTM window of 371 days (53-week FY2025) is rejected by a 365/366-day span guard.
- Cumulative-YTD-only cash flow: BEN (capex 9M 15.0M), RBC, ARMK (9M CFO -264,755K, fiscal quarter near Jul 3), and the YTD D&A EBITDA family in T12.

## T17 split adjustment / sign errors in derived quarters (additional)

- TPL(S042): derived Q4 2025 EPS -8.59 (FY 6.97 post-split minus 9M 15.56 pre-split), so TTM EPS 0.98 and trailing_pe 345.24 vs about 40 (comparative FC; mixing DI).
- AMCR(S047): 1-for-5 reverse split; Q1 FY26 EPS 0.113 pre-split vs adjusted Q2/Q3; Q4 derived 1.287 vs FY 2.38 - 9M 1.55 = 0.83 (FC).
- LEN: Q3 capex derived negative (see T12). JBHT DPS -0.88 (T13).

## T18 identity and ingestion defects (additional)

- EQR(S043, FC cover R1): `company_name` "VIVMARK RESIDENTIAL", `display_name` "AvalonBay Communities, Inc.", `primary_ticker` "VMRK"; the filing says EQUITY RESIDENTIAL, CIK 0000906107, symbol EQR. Three identities on one row.
- DD: duplicate FY2026 periods (start 2025-05-26 and 2025-06-01) at DRI, duplicate FY rows at AIZ 2009-2011 (benign, S041/S058).
- History gaps inside the XBRL era: SWK FY2010-2014, PAG FY2009-2014 (S058, DI).

---

## Per-company verdicts

Format: TICKER | shard | rank-or-mcap (shard band, see Block) | wrong values | unexplained blanks (or total blanks if that is all the file gives) | verdict. None of these files has its own per-company verdict table except S058 and S059 (quoted as given, marked FILE); all others DERIVED: NOT CLEAN where any wrong value, stale value, wrong reason or unexplained blank exists. By the workers' own universal-cell finding, every company here is NOT CLEAN.

S039
PPL | S039 | not stated | stale Q2 (0 facts); Q1 values only | 12 unexplained (32 blank) | NOT CLEAN DERIVED
SN | S039 | not stated | none shown (TTM chain blank, DI) | 8 (52) | NOT CLEAN DERIVED
CPAY | S039 | not stated | none | 15 (30) | NOT CLEAN DERIVED
CPNG | S039 | not stated | trailing_pe -32.5; roic +154% | 18 (33) | NOT CLEAN DERIVED
CINF | S039 | not stated | fcf_yield 12.9% meaningless | 24 (53) | NOT CLEAN DERIVED
QSR | S039 | not stated | net income incl. NCI; market cap share basis | 8 (21) | NOT CLEAN DERIVED
ZLAB | S039 | not stated (excluded, ADS) | revenue partial; market cap 28.08B vs about 2.6-2.8B; PE -138.97 | 16 (34) | NOT CLEAN DERIVED
VICI | S039 | not stated | none shown (capex blank) | 23 (52) | NOT CLEAN DERIVED
DGX | S039 | not stated | none (false financial-institution reason) | 9 (24) | NOT CLEAN DERIVED
CPRT | S039 | not stated | none (true-zero debt blank) | 11 (24) | NOT CLEAN DERIVED
S040
LH | S040 | 24.8-26.0B | none | not stated (17 blank) | NOT CLEAN DERIVED
CASY | S040 | band | operating_income_resolved 4,924,225K vs about 369,089K | not stated (25 blank) | NOT CLEAN DERIVED
EXPD | S040 | band | none (total_debt blank, DPS missing) | not stated (41 blank) | NOT CLEAN DERIVED
ULTA | S040 | band | fiscal_year labels +1 | not stated (31 blank) | NOT CLEAN DERIVED
ATI | S040 | band | none | not stated (21 blank) | NOT CLEAN DERIVED
FISV | S040 | band | none | not stated (38 blank) | NOT CLEAN DERIVED
LPLA | S040 | band | stale OI 2020; trailing_pe 25.9 suspicious; false no_dividend_history | not stated (55 blank) | NOT CLEAN DERIVED
FFIV | S040 | band | none (buyback line unmapped) | not stated (38 blank) | NOT CLEAN DERIVED
VRSK | S040 | band | stale Q2 (0 facts) | not stated (37 blank) | NOT CLEAN DERIVED
VLTO | S040 | band | stale Q2 (0 facts) | not stated (40 blank) | NOT CLEAN DERIVED
S041
CHD | S041 | not stated | none | 5 (22) | NOT CLEAN DERIVED
AFRM | S041 | 24.5-24.9B | revenue 1,443,922K vs 4,261,082K; shares stale | 23 (64) | NOT CLEAN DERIVED
ECHO | S041 | 24.5-24.9B | NI 6M basis; trailing_pe -3.43; shares stale | 11 (42) | NOT CLEAN DERIVED
LVS | S041 | band | P/B 42.3 | 8 (27) | NOT CLEAN DERIVED
DRI | S041 | band | none (duplicate FY2026 period rows) | 7 (16) | NOT CLEAN DERIVED
FCNCA | S041 | band | none; shares missing | 25 (61) | NOT CLEAN DERIVED
XYL | S041 | band | none | 5 (17) | NOT CLEAN DERIVED
HUBB | S041 | band | stale Q2 (0 facts) | 4 (30) | NOT CLEAN DERIVED
ROIV | S041 | band | fiscal_year label; PE -74.49; P/S 3,357 | 18 (47) | NOT CLEAN DERIVED
Q | S041 | band | none (OI blank no reason; interest expense unmapped) | 17 (55) | NOT CLEAN DERIVED
S042
TPR | S042 | not stated | ROE 221% (plausible) | 4 (9) | NOT CLEAN DERIVED
TPL | S042 | not stated | trailing_pe 345.24 (negative Q4 EPS) | not stated (62 blank) | NOT CLEAN DERIVED
FOX | S042 | not stated | shares_outstanding 1 | not stated (55 blank) | NOT CLEAN DERIVED
SYF | S042 | not stated | none (revenue blank defensible) | 38 no-reason (79 blank) | NOT CLEAN DERIVED
PPG | S042 | not stated | stale Q2 (0 facts) | not stated (27 blank) | NOT CLEAN DERIVED
PFG | S042 | not stated | stale Q2 (0 facts) | not stated (76 blank) | NOT CLEAN DERIVED
RF | S042 | not stated | revenue = interest income; OI 53M stray | not stated (65 blank) | NOT CLEAN DERIVED
IOT | S042 | not stated | shares blank; PE 265 | not stated (55 blank) | NOT CLEAN DERIVED
SYM | S042 | not stated | trailing_pe 2,916 | not stated (53 blank) | NOT CLEAN DERIVED
DLTR | S042 | not stated | fiscal_year label +1; revenue basis 0.1% | not stated (41 blank) | NOT CLEAN DERIVED
S043
NVT | S043 | 22.4-23.6B | none | not stated (29 blank) | NOT CLEAN DERIVED
BRO | S043 | band | stale OI 317 at 2024-09-30 | not stated (38 blank) | NOT CLEAN DERIVED
IFF | S043 | band | revenue Q1 2,741 vs recast 1,906 | not stated (26 blank) | NOT CLEAN DERIVED
OMC | S043 | band | stale Q2 (0 facts); trailing_pe -219.38 | not stated (31 blank) | NOT CLEAN DERIVED
RL | S043 | band | shares blank | not stated (24 blank) | NOT CLEAN DERIVED
EQR | S043 | band | revenue frozen 2020; OI 520.0 vs 218.9; identity VIVMARK/AvalonBay/VMRK | not stated (62 blank) | NOT CLEAN DERIVED
MKL | S043 | band | none | not stated (55 blank) | NOT CLEAN DERIVED
UTHR | S043 | band | none (false pre-revenue reason) | not stated (28 blank) | NOT CLEAN DERIVED
ROKU | S043 | band | shares stale (2025FY only) | not stated (30 blank) | NOT CLEAN DERIVED
L | S043 | band | revenue 828 vs 4,734 | not stated (49 blank) | NOT CLEAN DERIVED
S044
STZ | S044 | 21.2-23.2B | EPS and shares blank (class axis) | 23 (39) | NOT CLEAN DERIVED
RBRK | S044 | band | trailing_pe -90.44; total_debt blank | 20 (41) | NOT CLEAN DERIVED
INCY | S044 | band | stale Q2 (0 facts) | 11 (43) | NOT CLEAN DERIVED
DINO | S044 | band | none (ppe_net unmapped) | 6 (23) | NOT CLEAN DERIVED
USFD | S044 | band | none | 13 (28) | NOT CLEAN DERIVED
CRCL | S044 | band | revenue 33,582K vs 701,315K | 28 (73) | NOT CLEAN DERIVED
XPO | S044 | band | none | 6 (28) | NOT CLEAN DERIVED
NRG | S044 | band | revenue 7,319 vs 7,481 (about 2%) | 3 (19) | NOT CLEAN DERIVED
ARXS | S044 | band | equity blank; shares blank | 36 (80) | NOT CLEAN DERIVED
STE | S044 | band | latest diluted EPS 2.04 not stored (stale 7.93) | 3 (18) | NOT CLEAN DERIVED
S045
GPN | S045 | 21.2-22.5B | trailing_pe -28.43 | 6 | NOT CLEAN DERIVED
EXE | S045 | band | Q2 DPS missing | 9 (heading count) | NOT CLEAN DERIVED
DOW | S045 | band | stale Q2 (0 facts); PE -7.6125 | 9 | NOT CLEAN DERIVED
TROW | S045 | band | gross_profit 2012 counted filled | 22 | NOT CLEAN DERIVED
SW | S045 | band | none | 9 | NOT CLEAN DERIVED
THC | S045 | band | none | 18 | NOT CLEAN DERIVED
JBHT | S045 | band | DPS -0.88; yield 0.20% | 8 | NOT CLEAN DERIVED
VTRS | S045 | band | trailing_pe -46.15 | 3 | NOT CLEAN DERIVED
PHM | S045 | band | none | 20 | NOT CLEAN DERIVED
KEY | S045 | band | revenue 449M vs bank net revenue | 20 | NOT CLEAN DERIVED
S046
ENTG | S046 | 20.5-22.2B | none | 8 (18) | NOT CLEAN DERIVED
PKG | S046 | band | none | 7 (17) | NOT CLEAN DERIVED
GH | S046 | band | ROE +203%, P/B -97.5, PE -46.28 | 12 (27) | NOT CLEAN DERIVED
INSM | S046 | band | trailing_pe -23.17 | 13 (32) | NOT CLEAN DERIVED
RS | S046 | band | stale Q2 (0 facts) | 7 (27) | NOT CLEAN DERIVED
PTC | S046 | band | none | 14 (27) | NOT CLEAN DERIVED
AMRZ | S046 | band | Q1 2026 revenue/CFO/capex missing (recast) | 8 (57) | NOT CLEAN DERIVED
SMCI | S046 | band | none (zero buyback not stored) | 11 (29) | NOT CLEAN DERIVED
LYB | S046 | band | NI incl. NCI; trailing_pe -56.28 | 6 (17) | NOT CLEAN DERIVED
PR | S046 | band | none (capex and D&A unmapped, 17+ cells) | 21 (62) | NOT CLEAN DERIVED
S047
BG | S047 | 19.4-20.7B | revenue 4,660M vs 21,861M; stale Q2 | 10 | NOT CLEAN DERIVED
NI | S047 | band | none (pretax unmapped) | 8 | NOT CLEAN DERIVED
RGLD | S047 | band | none (capex, cost of sales, inventory) | 15 | NOT CLEAN DERIVED
AMCR | S047 | band | Q4 EPS 1.287 vs 0.83 | 3 | NOT CLEAN DERIVED
BR | S047 | band | income_before_tax stuck 2020-03-31 | 6 | NOT CLEAN DERIVED
MTSI | S047 | band | none | 8 | NOT CLEAN DERIVED
SBAC | S047 | band | revenue 51,389K vs 715,274K; P/B -4.18 | 16 | NOT CLEAN DERIVED
SSNC | S047 | band | none | 6 | NOT CLEAN DERIVED
SNX | S047 | band | none | 4 | NOT CLEAN DERIVED
BBY | S047 | band | none | 8 | NOT CLEAN DERIVED
S048
WWD | S048 | not stated | none (dividends_paid blank for payer) | 10 (27) | NOT CLEAN DERIVED
LUV | S048 | not stated | none (inventory unmapped) | 13 (25) | NOT CLEAN DERIVED
EVRG | S048 | not stated | stale Q2 (0 facts) | 12 (31) | NOT CLEAN DERIVED
CBRS | S048 | not stated | shares blank | 36 (74) | NOT CLEAN DERIVED
OVV | S048 | not stated | revenue 2,872 vs 3,013 | 13 (32) | NOT CLEAN DERIVED
SNA | S048 | not stated | none (capex unmapped, 13 cells) | 13 (29) | NOT CLEAN DERIVED
EFX | S048 | not stated | none | 11 (28) | NOT CLEAN DERIVED
CDW | S048 | not stated | none (total_debt, AP unmapped) | 6 (16) | NOT CLEAN DERIVED
CRS | S048 | rank 479 | none (false financial-institution reason; cover label) | 4 (7) | NOT CLEAN DERIVED
TOST | S048 | not stated | shares_outstanding zero (2021) | 7 (26) | NOT CLEAN DERIVED
S049
SOFI | S049 | not stated | revenue 153,577K vs 1,218,676K | 15 (39) | NOT CLEAN DERIVED
FSLR | S049 | not stated | none | 10 (33) | NOT CLEAN DERIVED
CW | S049 | not stated | none | 9 (18) | NOT CLEAN DERIVED
FIS | S049 | not stated | none | 8 (29) | NOT CLEAN DERIVED
GPC | S049 | not stated | trailing_pe 484.8 | 5 (38) | NOT CLEAN DERIVED
LEN | S049 | not stated | capex Q3 -8,019K | 24 (55) | NOT CLEAN DERIVED
NTNX | S049 | not stated | ROE 214%; cover label FY2027 | 17 (31) | NOT CLEAN DERIVED
CF | S049 | not stated | NI incl. NCI 869/1,545 | 8 (15) | NOT CLEAN DERIVED
WES | S049 | not stated | stale Q2 (0 facts) | 22 (61) | NOT CLEAN DERIVED
IP | S049 | not stated | shares 627M issued vs 529.6M; PE -5.20 | 9 (52) | NOT CLEAN DERIVED
S050
ZBH | S050 | not stated | none | not stated (21 blank) | NOT CLEAN DERIVED
NDSN | S050 | not stated | none | not stated (14 blank) | NOT CLEAN DERIVED
PAA | S050 | not stated | stale equity 2017/EPS 2016; P/B -23.84; PE 6.49 | not stated (50 blank) | NOT CLEAN DERIVED
PS | S050 | not stated | stub periods (DI); round market cap 18,006,000,000 (unverified) | not stated (88 blank) | NOT CLEAN DERIVED
ITT | S050 | not stated | none (false financial-institution reason) | not stated (14 blank) | NOT CLEAN DERIVED
U | S050 | not stated | trailing_pe -29.43; total_debt blank | not stated (66 blank) | NOT CLEAN DERIVED
GIS | S050 | not stated | trailing_pe -20.12; two coexisting NI values | not stated (19 blank) | NOT CLEAN DERIVED
LNT | S050 | not stated | stale Q2 (0 facts) | not stated (41 blank) | NOT CLEAN DERIVED
FTV | S050 | not stated | stale Q2 (0 facts) | not stated (37 blank) | NOT CLEAN DERIVED
DD | S050 | not stated | mixed-basis revenue; PE 155.7 | not stated (39 blank) | NOT CLEAN DERIVED
S051
DT | S051 | not stated | none (total_debt stale 0 at 2023) | not stated (33 blank) | NOT CLEAN DERIVED
ZBRA | S051 | not stated | none | not stated (17 blank) | NOT CLEAN DERIVED
RGA | S051 | not stated | none | 25 (56) | NOT CLEAN DERIVED
EWBC | S051 | not stated | revenue 1,080,823K vs 791,143K | not stated (56 blank) | NOT CLEAN DERIVED
IEX | S051 | not stated | none | not stated (28 blank) | NOT CLEAN DERIVED
APG | S051 | not stated | trailing_pe -66.44 | not stated (47 blank) | NOT CLEAN DERIVED
ESS | S051 | not stated | revenue 2,318K vs 489,049K; margins 2,887%/4,718% | 29 (70) | NOT CLEAN DERIVED
TSCO | S051 | not stated | none | not stated (21 blank) | NOT CLEAN DERIVED
MEDP | S051 | not stated | none (total_debt stale 0 at 2019) | not stated (56 blank) | NOT CLEAN DERIVED
APA | S051 | not stated | revenue empty; OI 1,280 not on face | not stated (69 blank) | NOT CLEAN DERIVED
S052
HEI | S052 | not stated | Q3 FY26 10-Q never ingested | not stated | NOT CLEAN DERIVED
RVTY | S052 | not stated | none | not stated | NOT CLEAN DERIVED
FTAI | S052 | not stated | NI basis (ProfitLoss); OI stale 2021 | not stated | NOT CLEAN DERIVED
FDXF | S052 | 16.4B | TTM cells blank (annual only); cash/ppe/total_liabilities blank | 32 (87 blank; 76 of 163 filled) | NOT CLEAN DERIVED
RIVN | S052 | not stated | trailing_pe -4.84 | not stated | NOT CLEAN DERIVED
CLH | S052 | not stated | stale Q2 (0 facts) | not stated | NOT CLEAN DERIVED
TLN | S052 | not stated | trailing_pe -87.32 | not stated | NOT CLEAN DERIVED
BALL | S052 | not stated | NI 223 vs 221; stale OI 2024-03 | not stated | NOT CLEAN DERIVED
WCC | S052 | not stated | none | not stated | NOT CLEAN DERIVED
FICO | S052 | not stated | none (negative equity -4,097M; book value blank) | not stated | NOT CLEAN DERIVED
S053
BURL | S053 | 15.9-17.1B (ranks 521-530) | revenue 2,852.3M vs 2,856.5M (minor) | 9 (27) | NOT CLEAN DERIVED
J | S053 | band | none (AR unmapped) | not stated | NOT CLEAN DERIVED
HST | S053 | band | capex stale 2019 | 22 (42) | NOT CLEAN DERIVED
WMG | S053 | band | EPS and shares stale 2020 | not stated | NOT CLEAN DERIVED
TPG | S053 | band | revenue 704,969K vs 1,841,424K; OI -792,369K | 35 (73) | NOT CLEAN DERIVED
CHRW | S053 | band | none | 12 (29) | NOT CLEAN DERIVED
NWSA | S053 | band | OI stale 2019 | 16 (62) | NOT CLEAN DERIVED
H | S053 | band | PE 211.7 (plausible) | 15 (43) | NOT CLEAN DERIVED
ROL | S053 | band | none | 10 (36) | NOT CLEAN DERIVED
INVH | S053 | band | revenue 49,460K vs 747,550K; capex stale 2018 | 25 (55) | NOT CLEAN DERIVED
S054
CDE | S054 | 15.0-16.1B | none | 11 (31) | NOT CLEAN DERIVED
RBC | S054 | band | none (capex(2026) absent) | 3 (22) | NOT CLEAN DERIVED
NVR | S054 | band | none (false reason; inventory/AR unmapped) | 29 (73) | NOT CLEAN DERIVED
BEN | S054 | band | none | 12 (35) | NOT CLEAN DERIVED
LDOS | S054 | band | Q4 fiscal_year label | 8 (27) | NOT CLEAN DERIVED
EXEL | S054 | band | Q4 fiscal_year label | 11 (44) | NOT CLEAN DERIVED
RBA | S054 | band | none | 8 (26) | NOT CLEAN DERIVED
CRBG | S054 | band | none | 30 (82) | NOT CLEAN DERIVED
YUMC | S054 | band | none (short-term borrowings not in total_debt) | 11 (28) | NOT CLEAN DERIVED
PFGC | S054 | band | none | 11 (30) | NOT CLEAN DERIVED
S055
KIM | S055 | 14.5-15.7B | EPS stale 2020; capex stale | not stated (58 blank) | NOT CLEAN DERIVED
TSN | S055 | band | shares blank | not stated (34 blank) | NOT CLEAN DERIVED
MTZ | S055 | band | none | not stated (34 blank) | NOT CLEAN DERIVED
LAMR | S055 | band | shares blank | not stated (37 blank) | NOT CLEAN DERIVED
JHX | S055 | band | none (TTM price metrics blank) | not stated (53 blank) | NOT CLEAN DERIVED
LOGI | S055 | band | none (total_debt blank, zero) | not stated (26 blank) | NOT CLEAN DERIVED
EG | S055 | band | shares 74.5M issued vs about 38.7M | not stated (77 blank) | NOT CLEAN DERIVED
WPC | S055 | band | EPS stale 2018, capex 2018, OI 2015 | not stated (59 blank) | NOT CLEAN DERIVED
ULS | S055 | band | none | not stated (35 blank) | NOT CLEAN DERIVED
LSCC | S055 | band | price metrics regressed to blank since 2026-10-03 | not stated (42 blank) | NOT CLEAN DERIVED
S056
MAS | S056 | not stated | stale Q2 (0 facts); P/B -62.17, ROE -345.9% | 8 (25) | NOT CLEAN DERIVED
TYL | S056 | not stated | shares 48,147,969 issued vs about 40.95M | 12 (29) | NOT CLEAN DERIVED
SOLV | S056 | not stated | none | 14 (38) | NOT CLEAN DERIVED
UNM | S056 | not stated | none (OI anomaly unresolved) | 21 (51) | NOT CLEAN DERIVED
RNR | S056 | not stated | diluted EPS Q2 missing (unmapped tag) | 29 (70) | NOT CLEAN DERIVED
ARMK | S056 | not stated | none | 5 (24) | NOT CLEAN DERIVED
PINS | S056 | not stated | market cap 15.32B vs about 13.05B; total_debt blank | 17 (49) | NOT CLEAN DERIVED
EQH | S056 | not stated | P/B -18.79, ROE -57.8%, PE -16.28 | 31 (80) | NOT CLEAN DERIVED
MKSI | S056 | not stated | none | 4 (13) | NOT CLEAN DERIVED
SUI | S056 | not stated | stale Q2 (0 facts; discontinued ops) | 20 (68) | NOT CLEAN DERIVED
S057
GEN | S057 | not stated | none | not stated (11 blank) | NOT CLEAN DERIVED
CNH | S057 | not stated | revenue 4,143 vs 4,803; OI stale 2017; capex 2016 | not stated (51 blank) | NOT CLEAN DERIVED
CRL | S057 | not stated | trailing_pe -65.53; pretax blank | not stated (36 blank) | NOT CLEAN DERIVED
PNFP | S057 | not stated | FY2025 equity 6,013 vs 7,044 | not stated (76 blank) | NOT CLEAN DERIVED
LECO | S057 | not stated | none | not stated (8 blank) | NOT CLEAN DERIVED
TRU | S057 | not stated | stale Q2 (0 facts) | not stated (30 blank) | NOT CLEAN DERIVED
WY | S057 | not stated | capex stale 2019 | not stated (21 blank) | NOT CLEAN DERIVED
SITM | S057 | not stated | PE 848 (arithmetically right) | not stated (40 blank) | NOT CLEAN DERIVED
JLL | S057 | not stated | capex stale 2019 | not stated (65 blank) | NOT CLEAN DERIVED
CHTR | S057 | not stated | shares stale 2016; market cap basis untraceable (13.94B vs cover 119.28M shares) | not stated (63 blank) | NOT CLEAN DERIVED
S058 (the file's own table, FILE)
AIZ | S058 | not stated | 0 found | 19 | NOT CLEAN FILE
SWK | S058 | not stated | 1 family (fiscal_year label breaks TTM); stale OI | 4 | NOT CLEAN FILE
PAG | S058 | not stated | 0 mismatches; 4 of last 8 quarters of revenue missing | 15 | NOT CLEAN FILE
HAS | S058 | not stated | 0 | 6 | NOT CLEAN FILE (nearest to clean)
DOCU | S058 | not stated | 0 | 15 | NOT CLEAN FILE
TRMB | S058 | not stated | 1 family (same Q4 label) | 8 | NOT CLEAN FILE
GWRE | S058 | not stated | 0 (total_debt blank with 678.1M converts) | 13 | NOT CLEAN FILE
OHI | S058 | not stated | 3 (revenue, OI, margin 2366%); P/S inherits | 24 | NOT CLEAN FILE
NBIX | S058 | not stated | 0 | 15 | NOT CLEAN FILE
HALO | S058 | not stated | 0 | 12 | NOT CLEAN FILE
S059 (the file's own table, FILE)
NLY | S059 | 13.2-13.8B | 1 (W3 stale total_debt) | 34 of 86 | NOT CLEAN FILE
JAZZ | S059 | band | 2 (W11, W12) | 13 of 46 | NOT CLEAN FILE
CACI | S059 | band | 1 minor (rounded NI) | 15 of 32 | NOT CLEAN FILE
MAA | S059 | band | 3 (stale Q2, OI 348,153K, total_debt blank) | 30 of 75 | NOT CLEAN FILE
BF-A | S059 | band | 1 (shares stale 15 months) | 7 of 22 | NOT CLEAN FILE
GME | S059 | band | 1 minor (total_debt stale) | 8 of 38 | NOT CLEAN FILE
SJM | S059 | band | 2 (Q1 FY27 10-Q never collected; PE -99.27) | 6 of 25 | NOT CLEAN FILE
ARCC | S059 | band | 0 shown wrong; revenue-equivalent absent | 52 of 103 | NOT CLEAN FILE
GDDY | S059 | band | 1 (P/B 2,064.7, ROE 13,587%, D/E 563.3) | 14 of 43 | NOT CLEAN FILE
REG | S059 | band | 3 (stale Q2, OI 296,394K, interest expense stale) | 24 of 64 | NOT CLEAN FILE

---

## History-window items

Most workers explicitly did not check FY history ("Not done: FY2025 10-K / history"). Items actually reported:
- S058 (DI, earliest annual revenue held vs earliest 10-K in core.filing): HAS 2010 vs 1993; SWK 2009 vs 1994 with a gap FY2010 to FY2014 (5 years missing, unexpected); PAG 2008 vs 1996 with a gap FY2009 to FY2014 (6 years missing, unexpected); TRMB 2009 vs 1996; OHI 2016 vs 1997 (nothing before 2016); NBIX 2009 vs 1997; AIZ 2007 vs 2003 (duplicate FY revenue rows 2009-2011); DOCU 2017 vs 2019; GWRE 2010 vs 2012; HALO 2009 vs 2006. FY2021 revenue spot-check (from memory, not filings): HAS 6,420.4M, TRMB 3,659.1M, PAG 25,554.7M, AIZ 10,187.6M, NBIX 1,133.5M, HALO 443.3M, GWRE 743.3M (FY Jul 2021), DOCU 1,453.0M (FY Jan 2021), SWK FY2020 14,534.6M, OHI 1,062.8M. Last 8 quarters: PAG only 4; others 8 or 9.
- S059 (DI plus SJM FY2026 FC): earliest FY revenue held / earliest 10-K (count): BF-A 2017-04-30 / 1994-04-30 (32); CACI 2009-06-30 / 1994-06-30 (26); SJM 2017-04-30 / 1994-04-30 (29); REG 2017-12-31 / 1996-12-31 (29); MAA 2008-12-31 / 1996-12-31 (26); GDDY 2016-12-31 / 2015-12-31 (11); JAZZ 2009-12-31 / 2007-12-31 (19); GME 2017-01-28 / 2006-01-28 (21); NLY and ARCC no revenue concept. FY2018 / FY2021 revenue stored: BF-A 3,248.0M / 3,461.0M; CACI 4,467.9M / 6,044.1M; SJM 7,357.1M / 8,002.7M; REG 1,121.0M / 1,166.2M; MAA 1,571.3M / 1,778.1M; GDDY 2,660.1M / 3,815.7M; JAZZ 1,890.9M / 3,094.2M; GME 8,547.1M / 5,089.8M. Worker called the roughly 2017 start for BF-A, SJM, REG, GME a window limit. Missing quarters: JAZZ 2025-Q1 and Q2; SJM stops at Q4 FY2026 (W4); REG, MAA stop at 2026-Q1.
- Missing quarters or history inside the last 8 elsewhere: AMRZ (Q1 2026, 2025 Q1/Q2), IFF (Q2 2025), DD (no standalone Q3 2025), SN (no Q3/Q4 2025), JHX (no Q2-Q4 FY26), PNFP (Q3 2025, Q4 2025, FY2025), RL (capex Q4 FY26), PS (history from 2025 Q1), CBRS/ARXS (no earlier 10-K/10-Q; ARXS only S-1 history).
- Odd lookback labels: NWSA `diluted_shares_growth` uses a 2012/2010/2008 base for a 2026 period (S053, DI); SMCI `prior_period(2016_Q4)/(2023_FY)` fail despite long history (S046, DI); FOX `prior_period(2014_Q3/2016_Q3)` for a 2019 listing (S042, DI); WPC `eps_growth_10y` asks for 2008_Q4 (S055).
- ENTG `fcf_growth_yoy missing:fcf(2024)`, FTV `fcf(2024)`, PAG `fcf(2024)`, GPC/FIS/STE/LYB 2025 balance-sheet values missing at the fiscal-year-end dates (DI, not investigated).
- FY2015: not spot-checked by any worker in this block. No worker opened a FY2015/2018/2021 filing.

---

## Population counts quoted

| Count | Shard | Query or estimate |
|---|---|---|
| 683 `institutional_ownership_pct` cells carrying `implausible:institutional_shares_exceed_shares_outstanding` | S040 ("live count"); S050 ("683 coverage rows", query); S052 ("683 companies"); S053 ("683 blank cells across 1,690 companies", live query); S055 | Query per S040/S053; S052 wording says companies, S053 says cells across 1,690 companies: unit is inconsistent between files |
| 3,433 cells carry `no_dividend_history` (not split true/false) | S040 (quoted from status.md) | Quoted, not run here |
| 168 companies use the `Revenues - OperatingExpenses` derivation | S040 (quoting S023) | Quoted |
| 497 companies with blank `shares_outstanding`; 398 rows with blank `diluted_eps` | S044 (2026-10-20 coverage run); 497 repeated in S055 | Query |
| 2,555 companies take revenue from the 606 tag alone; 1,556 of them have both `Revenues` and the 606 tag filed | S044 | Query |
| 1,556 of 4,562 companies have both tags in `mapped_tags_filed` with the partial tag chosen; 281 have `Revenues` chosen | S047 | Query over `company_concept_lineage` |
| 144 companies with blank equity (stockholders_equity) | S044 | Query |
| 1,698 companies with total_debt blank and no reason | S044 | Query (method not stated) |
| 38 companies with a Q4 ending 2026-01-01..09 labeled fiscal_year 2026; 43 with FY labeled 2025; 244 with any period ending in that window | S054 | Query ("cheap population count") |
| 203 coverage rows for `operating_expenses` carry `financial_institution_interest_income_not_revenue`; 328 companies across all cells (S023) | S050 | 203 query; 328 quoted from S023 |
| 1,470 cells, 328 companies with the same financial-institution reason | S052 (quoting) | Quoted |
| 142 of 328 non-financial | S041 (quoting S023) | Quoted |
| 189 companies, 789 cells carry `reit_net_interest_income_not_revenue` | S055 | Query |
| Shard baselines: 1,630 cells each; blanks / unexplained: S041 381 / 123; S042 522 blank (68% filled); S044 360 / 149; S046 260 / 111; S054 398 / 134 (1,232 filled, 75.6%); S055 455 blank (72.1% filled); S056 447 / 161 (72.6% filled); S059 267 unexplained | each shard | Queries on `company_data_point_coverage` |
| SN: 6,909,956K derived TTM revenue (FY2025 6,399,188K - 6M 2025 2,667,514K + 6M 2026 3,178,282K) | S039 | Arithmetic from stored values |
| Count of confirmed 0-facts companies across shards: "at least 6 in the top 500" (S050), "6 confirmed" (S056); this block alone has 21 | S050, S056 | Worker tallies; superseded by the 21 above |
| Not run (workers state population counts were skipped because of the 50s cap / shared pooler): 0-facts, stale-series, multi-class, net income basis, capex mapping, P/E guard, recast and filing-never-collected populations | S039-S059 | n/a |
