# Digest DE (block E: S080 through S102)

Abbreviations: FC = FILING-CHECKED (worker read the SEC R-page / statement). DI = DATA-INFERRED (our tables only). SNR = suspected not reported. Wording of evidence labels is the workers'. Accession numbers copied as written in the files; "no accession given" means the file did not give one for that finding.

## Block

Read in full: S080, S081, S082, S083, S084, S085, S086, S087, S088, S089, S090, S091, S092, S093, S094, S095, S096, S097, S098, S099, S100, S101, S102 (23 files, none missing or partial). Companies covered: 224 (S080-S100 = 21 shards x 10 = 210; S101 = 8 backfill; S102 = 6 backfill, all with blank market cap). Every worker was read-only, `statement_timeout='50s'`, and read the latest 10-Q (or 10-K) R-pages; **no worker checked a FY2025 10-K headline across the board** (only a few: VFC, HRB, CMC, PATH, ELF, OTEX, CPB, CAG, AVT, RAL, FLR, ASB/BGC comparatives), and most FY2018/FY2021 "spot checks" were against memory, not an opened filing (DI).

Block-wide headline finding: at the latest quarter, revenue / net income / EPS / total assets / equity matched the filing for nearly every company where the stored quarter exists; the defects are in (a) which revenue tag is chosen, (b) share counts, (c) tags not mapped (capex, D&A, interest, debt), (d) stale series counted as filled, (e) reasons that are false or missing, (f) a latest quarter that is simply absent. No company is strictly CLEAN: all 224 carry at least the 4 universal unexplained cells (`bdc_total_investment_income`, `collaborative_arrangement_revenue`, `net_lease_revenue`, `employee_count`).

## Theme T1: revenue resolves to a partial/sub-line tag instead of the statement total

**Companies affected: about 37 (34 FC, 3 DI).**
- FC, ASC 606 / sub-line / wrong-tag (non-bank): UGI(S080), REXR(S080), NFG(S084), LNC(S084), PACS(S085), KMX(S085, rounded 0.1M), TAP(S085, gross "Sales" instead of "Net sales"), M(S093), LYFT(S093 history), WEX(S094), HR(S096), VAL(S096), CWEN(S095 FY2018-19), ENS(S095 FY2012-2020, reverse direction: `Revenues` sub-total beat the real total), CHE(S090 FY2017-2024), SNEX(S090 quarters), GLXY(S092, misses two face revenue lines), RYN(S098 Q1), BGC(S101), INSW(S101, 0.5%), BRK-A(S102), BAM(S102), UHAL(S102), SWX(S092, new tag `RegulatedOperatingRevenue` not accepted so Q2 revenue absent).
- FC, banks where revenue is gross interest income or a tiny 606 slice: PB(S081), WAL(S081), COLB(S082 FY2023-25), CBSH(S082, a zero-valued `Revenues` tag wins), BOKF(S085), UBSI(S092), HWC(S097), GBCI(S099, series flips between the interest tag and the 606 tag), HOMB(S098), ASB(S101, basis switch inside the series).
- DI: VLY(S088, filing total not read), FNB(S095), CBC(S082).

**Cells:** wrong values shown for revenue itself plus every revenue-based metric (margins, P/S, ev_sales, growth, operating income derived from revenue). Numbers quoted: REXR price_to_sales 26,209.95; HR price_to_sales 199.7; VAL price_to_sales 285.3 and gross margin -133.03; WAL net_margin 573%; GBCI price_to_sales 53.1; UHAL revenue about 7x low; TAP margins about 16% too high. Counts of affected cells per company: not stated; whole revenue series wrong for REXR, HR, VAL, LNC (FY2018), CWEN, ENS, CHE, UHAL, BGC (every year).

**FC exemplars:**
- REXR(S080): stored revenue 0 for every 2026 period and 611K/589K for FY2024/FY2025 vs filed "TOTAL REVENUES" 245,506K (Q2), 490,584K (6M); comparative Q2 2025 249,507K vs stored 132K. Tag `RevenueFromContractWithCustomerExcludingAssessedTax` picked the "Management and leasing services" line. No accession given.
- LNC(S084): FY2018 stored 1,343M vs Total revenues 16,424M (10-K 0000059558-19-000010); a 606 sub-line won over `Revenues`.
- UHAL(S102): Q2 FY27 stored 237,447K vs Total revenues 1,682,027K (10-Q 0001193125-26-335008); FY2026 stored 761,453K.
- Also HR(S096): 8,033K vs 281,849K (10-Q 0001360604-26-000064); BGC(S101) 695,557K vs 845,545K (10-Q 0001628280-26-055187), understated 17-21% every year.

**Mechanism (workers' wording):** "revenue resolved by tag-name priority, not by which tag equals the statement's total revenue line" (S080); for banks "revenue resolved to `InterestAndDividendIncomeOperating`" (gross interest income, noninterest income dropped), needing a "Standardization ruling" on bank revenue (S082, S088, S095, S098). Not a new bug for MUR(S096), where stored "Total revenue from sales to customers" 926.3M vs face 928.3M is called a definition choice.

## Theme T2: operating income derived or taken from a non-face line / segment note

**Companies affected: 12 distinct for wrong/derived displayed values (11 FC, 1 DI); stale versions are under T5.**
- FC: THG(S081), AOS(S081), GLXY(S092), CACC(S100), RLI(S100), BGC(S101), INSW(S101), REXR(S080, derived with the wrong revenue, stored latest 2020), LEA(S096, stored 267.9M equals pretax+interest+other, "arithmetically consistent", no defect called), VNO(S095, revenue minus Total expenses reproduces, noted not wrong), PEGA(S099, Q3 operating income not yet derived though `OperatingIncomeLoss` is in core.fact).
- DI origin of the fact: THG, AOS (origin of the fact "likely a segment-note total"), CACC, RLI.

**Cells:** wrong values shown for operating_income_resolved and operating margin / ROIC / interest coverage. THG Q2 251.9 vs EBT 244.6 (margin 14.6% on the derived base); AOS Q2 166.1 vs EBT 158.0; GLXY Q2 -282,120 (YTD -689,162) vs result before other items -128,923 (off by 153,197); CACC 453.3M / 892.1M vs pretax 168.6M / 343.6M (77% "margin"); RLI 542,952K / 938,542K vs EBT 210,688K / 278,029K (94% margin); BGC -78,086K Q2 (operating margin -14.1%) for a profitable company (pretax 98,943K); INSW 6M 589,913K vs face "Operating income" 593,832K.

**FC exemplars:**
- BGC(S101, 10-Q 0001628280-26-055187): stored 695,557K minus filed OperatingExpenses 773,643K = -78,086K; company presents no operating income, pretax income 98,943K.
- THG(S081): stored 251.9 = pretax 244.6 + interest 10.1 - realized gains 2.8; Hanover presents no operating income (no accession given).
- INSW(S101): stored picks "Income from vessel operations", dropping the 3,919K holding gain the face adds before "Operating income"; needs a ruling on which subtotal.

**Mechanism:** "two-input revenue-minus-opex derivation (W3-family of S023, 168 companies)" applied to lenders, insurers, brokers; `OperatingIncomeLoss` taken from a segment note; "ask: gate the derivation off for SIC 6xxx or require the subtotal on the statement" (S100) is the worker's observation, recorded here only as their wording.

## Theme T3: latest 10-Q/10-K has 0 facts in core.fact, or filing absent from core.filing

**Companies affected: 17 (all FC for the filed values; the 0-facts count itself is a DB query).** OSK(S083), ZWS(S083), IDA(S084, two quarters), AXS(S085), TAP(S085, Q1 only, breaks trailing_pe), AXTA(S087), NNN(S082, Q1 2026, DI), NOV(S090), VFC(S091), OMF(S091), KNSA(S091), POOL(S093), STAG(S089), EXLS(S095), LSTR(S098), RYN(S098), OLLI(S099, filing row itself missing from core.filing though SEC companyfacts has it; distinct from 0 facts).
SEC companyfacts also lacks the filing at OSK, ZWS, NOV (live fetch), VFC, OMF, KNSA, POOL, LSTR, RYN (workers say so); AAL's same-week 10-Q has 288 facts (control, S083).
Shards with none: S086, S088, S092, S094, S096, S097, S100, S101 (workers stated no 0-facts filing).

**Cells:** the whole quarter is absent: every TTM metric, P/E, P/S, margins, EBITDA chain, FCF chain one quarter (IDA two quarters) stale; coverage cell filled from the older period. Exact cell counts: not stated.

**FC exemplars:**
- OSK(S083, 10-Q 0001193125-26-320490): filed net sales 2,915.1, op income 243.2, NI 183.2, EPS 2.92, assets 10,051.5; stored latest 2026-03-31 revenue 2,317.8, op income 82.0, NI 43.1.
- AXS(S085, 0001214816-26-000203): total revenues 1,752,914K, NI 258,095K, EPS 3.38; stored latest 2026-03-31; P/E 7.5 uses a quarter-stale base.
- IDA(S084, Q1 0001057877-26-000098 and Q2 0001057877-26-000129): NI 102,869, EPS 1.79, assets 10,866,164 filed, not stored; the merger/stock offering effect on market cap is T4.
- Also NOV(S090, 0001193125-26-322979): revenue 2,134, NI attributable 112; stored Q1 revenue 2,052M, EPS 0.05.

**Mechanism (workers):** "our only source is companyfacts, which lacks the accession" (S083); "filing ingested without facts"; the filing has R-pages. PLAYBOOK family B1.

## Theme T4: shares_outstanding blank/stale/wrong, market cap on wrong share basis, per-share cascade

**Companies affected: about 40.**
- Multi-class/multi-series/unit cover counts not captured or not summed. FC (cover or equity statement read): AOS(S081), CNM(S081), DBX(S082), JAN(S083), MSGS(S084), APPF(S084), ZETA(S084), FPS(S084), S(S086), TTAN(S094), BGC(S101), SNDR(S101), GLXY(S092), HIMS(S092), RNG(S092), BRK-A(S102), FWONA(S102), BAM(S102), PLNT(S102), UHAL(S102), SUN(S102). DI: LEVI(S082, stale 2019), TAP(S085, five zero-valued rows from 2010 count as filled), NTSK(S085), Z(S088), PATH(S090), DUOL(S090, 2021 fallback 16.6M vs about 46-48M), BROS(S091), KNSA(S091), NAVN(S093), LB(S093), TTD(S098), DLB(S098), CWST(S100), MGY(S095, only 2 recent points).
- Other share-basis errors: IDA(S084, market cap uses 54,899,034 shares vs diluted 57.2M after an offering; about 4% low), FAF(S090, rounded cover 102.1M gives round market cap 6,761,062,000.00), SAIC(S100, 42,000,000 scaled vs cover 41,897,635; minor), ORA(S101, FY2025 cover count stored under FY2026 Q1), TTAN(S094, market cap 6,615M implies 80.2M shares vs 96.46M A+B, about 7.95B; DI), KZIA(S094, market cap 6,463M vs about 12M: ordinary shares x ADS price; also a 20-F filer, see T13).
- Market cap blank for all six in S102. Market cap present while shares_outstanding blank (source of cap not traced): JAN, LEVI, Z, PATH, NAVN, LB, S, BGC, SNDR, HIMS, DUOL, TTAN-class.
- D1 per-share pairing (cover-date shares vs balance-sheet-date equity): book_value_per_share, net_cash_per_share, piotroski blank. Quoted counts in the Population section.

**Cells:** shares_outstanding(+resolved), diluted_shares_growth_yoy/3y/5y, share_dilution_trend, total_shareholder_yield, book_value_per_share, net_cash_per_share, fcf_per_share, piotroski_f_score, institutional_ownership_pct (see T13), and for S102 market_cap and about 14 dependents. Roughly 8 to 14 dependent cells per company. Blank rather than wrong, except stale (AOS 2015 value shown, MSGS 2015, DUOL 2021) and wrong market cap (KZIA, FAF round, IDA).

**FC exemplars:**
- AOS(S081): stored latest 75,732,188 dated 2015-08-05 vs cover 25,861,359 Class A + 110,047,214 Common = 135.9M (28 Jul 2026). No accession given.
- TTAN(S094, 10-Q 0001638826-26-000094): stored 35,397,085 at 2024-10-31 vs equity statement 83,857,202 Class A + 12,605,018 Class B at 2026-07-31.
- SNDR(S101, 0001692063-26-000039): cover Class A 83,029,500 + Class B 92,271,399 (175.3M); stored blank; market cap 5.43B still filled.

**Mechanism:** "cover-page share count is dimensioned by class; no unclassified total is stored" (S084); "cover count read only when undimensioned"; for D1 "shares are stored on cover-page dates, equity on balance-sheet dates; they never meet" (S096).

## Theme T5: stale series counted as filled (latest period years old but coverage says has_value)

**Companies affected: about 45 (explicit "coverage counts it as filled": RHP, COLB, CBSH, LEVI, HXL, STAG, TAP, AAON, CWEN, MGY, EMN, DY, INSW, WFRD, HRB, HR, BRK-A, BAM; others listed as stale-latest in lineage).**

| Stale cell | Companies (latest stored period) | Level |
|---|---|---|
| capex | RHP(2015, S082), COLB(2023-06-30), VSAT(2023-09-30, S081), MUR(2019-12-31), HR(2023-09-30), CHDN(2019-09-30), EPRT(2019-03-31), AAON(2023-09-30), RYN(2025-09-30), INSW(2025-01-28), plus Q1-only capex at MTDR, MATX, AAOI, LNTH, TEX | RHP FC line, AAON FC line and tag, INSW FC line; others FC line / DI tag |
| total_debt (base or resolved) | COLB(2023-09-30), CBSH(2013-12-31), URBN(2020), KTOS(2021), BOKF(2025-12-31), GAP(2020 base 500M, S081), VSAT(2022 base 2,486M), AXTA/EMN/IONS/PRMB (stale or mismatched base, S087), Z(2022-06-30), HIMS(2020-12-31), DLB(2010), LKQ(2011), CHDN(2022), OLLI(2016), CACC(2014), HOMB(2016-12-31), LAD(resolved 2025-12-31), ANF(resolved 2025-02-01), HUT (FY2025 missing) | CACC, HOMB, GAP FC (filing debt read), most DI |
| diluted_eps | HXL(2020-12-31), STAG(2016-09-30), CHDN(2023-12-31), CWEN(2024-12-31), MGY(2019-09-30), FWONA(2016), BAM(2023) | HXL, STAG, CHDN, CWEN, MGY FC filed value; tag DI |
| operating_income | DY(2016-01-23, -418,016,000), EMN(2017-12-31), SNEX(2025-06-30), FAF(2011-12-31), HRB(2014-07-31), HR(2018-09-30), BRK-A(2013-03-31), BAM(2024-12-31), ESNT(2022-03-31), REXR(2020) | line absence FC, stale cell DI |
| shares_outstanding | MSGS(2015-09-30), AOS(2015-08-05), LEVI(2019-02-24), DUOL(2021-12-31), HIMS(2019-06-30), RNG(2013-12-31), PLNT(100 shares, 2015), UHAL(2022), BRK-A(2011) | covers FC |
| other | WFRD goodwill / gross_profit (no row after 2024-12-31) | DI |

**Cells:** the stale value counts as `has_value=true`; downstream cells (FCF chain 8-13 cells, EBITDA chain 5, debt chain 6-11, EPS-growth cells) are blank or computed on old data. EPS CAGR reasons "negative_ratio_undefined_cagr" at HXL are "wrong in cause" because the EPS series ends in 2020 (S089); MGY EPS lookbacks land in 2018/2016/2014/2009 (S095).

**FC exemplars:**
- HXL(S089, 10-Q 0001193125-26-323941): diluted_eps latest 2020-12-31 (69 rows, none after) vs filed Q2 2026 diluted EPS 0.64, six months 1.13; filer now uses `IncomeLossFromContinuingOperationsPerDilutedShare`.
- RHP(S082, 10-Q 0001104659-26-092580): capex latest 2015-12-31 vs R6 "Purchases of property and equipment" 241,190K (6M).
- AAON(S095): capex 22,271,000 at 2023-09-30 vs filed 97,282K 6M, tag `PaymentsToAcquireMachineryAndEquipment` (no accession given).

**Mechanism:** "no staleness guard on latest-period selection" (S096); "coverage compares to the concept's own latest period, not the company's latest quarter" (S084); worker S101 says this conflicts with the intent of commit fb26fb6 ("latest period must have a value").

## Theme T6: true zero shown as blank; total_debt unmapped / wrong / stale

**(a) Real zero debt shown as blank: 7 FC, about 12 DI/probable.** FC (statement opened, no borrowings): ANF(S091), KNSA(S091), DOCS(S100), TTD(S098), DLB(S098), APPF(S084), JAN(S083, debt 0 at 2026-06-30 vs 102,688 at Dec-2025). DI / probable: SLAB, S(S086), QLYS(S093), PRAX, PATH, DUOL, CAVA(S090), SYRE(S088), NTSK(S085), PEGA(S099), PTGX, TWST(S080), IOVA(S094 unclear), KTOS, URBN (S085, stale). Cells per company: 6 to 11 (total_debt, total_debt_split, zero_debt, debt_to_equity, net_cash, net_cash_per_share, debt_to_ebitda, net_debt_ebitda, roic, interest_coverage_ratio, piotroski). The same blank also shows on buybacks and dividends for non-payers (see T7).
**(b) Real debt not mapped (total_debt blank or wrong): about 35.** FC (balance-sheet line read): ARWR(S083, credit facility 40,000 + 141,366 and convertible notes 682,707), NE(S088), DBX(S082, convertibles), VRNS(S100, convertible notes 453,278K), CACC(S100, 6,286.2M), WH(S100, 23M + 2,652M), CWST(S100, 25,580K + 1,325,132K), CAKE(S099, 562,895K), ESNT(S098, 495,972K), HOMB(S098, 450,250K + 279,602K), LAD(S091, dimensional members), PLXS(S095, borrowings 605,500K), AXSM(S080, current 70,000K + noncurrent 117,958K, from XBRL facts not statement), HUT(S080, 7.74B carrying amount in 2026). DI: PB, WAL(S081), AXS(S085), SARO(S088), HIMS, GLXY(S092), CVLT(S094), LGND(S097), AAON, SFM(S095), GBCI(S099), CBC(S082), MKTX(S098, total_debt_resolved blank), WULF(S098, Q2 empty), TTAN, TWST, PTGX.
**(c) Base vs resolved disagree or double count:** ACM(S085, FC), TAP(S085, FC, double count), KMX(S085, FC, two totals; non-recourse notes need a ruling), AXTA, EMN(S087, EMN FC), IONS, PRMB(S087), WH(S100), ACA(S087), FAF(S090), CNM(S081), LINE(S085).

**FC exemplars:**
- ACM(S085, 10-Q 0000868857-26-000021): `total_debt` base 65,366K vs R2 2,566 + 60,244 + 2,651,988 = 2,714,798K; `total_debt_resolved` 2,714,788K is right (41x apart).
- TAP(S085, 10-Q 0000024545-26-000071): base 9,718.9M vs R4 2,037.1 + 5,672.5 = 7,709.6M (`DebtCurrent` added to `LongTermDebt` that already includes it).
- CACC(S100, 10-Q 0000885550-26-000182): lineage latest 1,752.5M at 2014-12-31 vs filed revolver 177.8M + secured financing 5,019.0M + senior notes 1,089.4M = 6,286.2M.
- True zero: ANF(S091, 10-Q 0001018840-26-000047): R3 has no debt line, total_debt_resolved stops at 2025-02-01, 7+ downstream cells blank.

**Mechanism:** "no debt tag filed means absent, never converted to 0" (S098); "debt built per-tag with no period-age guard" (S085); debt held in custom (`homb_`), dimensional or non-LongTermDebt tags.

## Theme T7: wrong or missing blank reasons

**(a) `financial_institution_interest_income_not_revenue` on non-financials.** FC: KMX(S085), VFC, SSRM(S091), AGCO(S086), MSA(S089), WEX(S094), HRB(S096), LSTR, MKTX(S098), WFRD(S101), AAON(S095), UHAL, BAM(S102). Right sector but wrong sentence for insurers/brokers: KNSL(S080), LNC(S084), MTG, MCY(S099), RLI(S100), ESNT(S098), ACT(S092), BGC(S101); FAF(S090) says the label is TRUE for a title insurer. DI-only on the trigger (SIC or a stray interest tag).
**(b) `reit_net_interest_income_not_revenue` on equity REITs (mortgage wording).** FC: REXR(S080), NNN, RHP(S082), FR, JAN(S083), ARE(S086), MAC(S091), STAG(S089), VNO(S095), HR(S096), RYN(S098), EPRT(S099), LINE(S085, statement has no such issue).
**(c) `pre_revenue_biotech_pharma` / `pre_revenue_mining_exploration` on companies with revenue.** FC: PTGX(213M), TGTX(240M), AXSM(218M), TWST(118M)(S080); ARWR(413M 9M, S083); IONS(267.9M), MP(108M/quarter, 199M 6M)(S087); ALKS(496M)(S089); KNSA(243.6M)(S091); IOVA(99.3M)(S094); LGND(115.4M 6M), RYTM(131.4M 6M)(S097). SYRE(S088) is correctly pre-revenue.
**(d) Non-dividend / non-buyback payers with NO REASON or `missing:`** (about 90 companies, essentially every non-payer; examples S080: PTGX, SPXC, HUT, TGTX, AXSM, TWST; S081: CNM, VIAV, MHK, FORM, VSAT; S088: VSXY, CELH, SARO, Z, SYRE). Typical 6 to 12 cells (dividends_paid(+resolved), dividends_per_share(+resolved), dps_growth_yoy/3y, dividend_yield, dividends_pct_fcf, payout_ratio, cash_returned_to_shareholders, share_buybacks, buyback_yield, share_repurchases_pct_fcf). Only `dividend_growth_streak_years` carries `no_dividend_history`. Other reason variants on non-payers: `zero_base_value` (FLR, WULF, OLLI, ETSY). Inverse: **payers labelled `no_dividend_history` or with blank DPS/yield**: THG, PB(S081, DPS ends 2016), WAL(dividends_paid ends 2025-03), INGR(S094; "3,433 blanks carry no_dividend_history"), LKQ(S099), LB(S093), SUN(S102), plus yield blank from YTD-only/no DPS tag at MSM, SFD, ESE, UBSI, NPO, POWL, ST, HR, CVI, CWEN, INSW, SNDR, CHDN, PEGA, RNG, FSS, MKTX (dividends_paid blank for a payer).
**(e) Sector-template cells with no reason (banks, insurers, REITs, lenders, brokers, BDC).** About 12-25 NO REASON cells each (current_assets/liabilities(+resolved), current_ratio, quick_ratio, working_capital, sga_expense, inventory_days, payables_days, total_debt_split, cf_ap/ar/inventory_change and 3 reconciliation gaps, ppe_net, income_before_tax). Companies include KNSL, REXR, PB, WAL, THG, COLB, CBSH, VLY, TRNO, BOKF, AXS, LNC, FNB, HWC, UBSI, HOMB, ASB, MTG, MCY, ACT, RLI, CACC, ESNT, MKTX, FAF, VCTR, SNEX, STAG, ARE, FR, JAN, MAC, GATX, EPRT, BXSL, BRK-A, UHAL. Missing-line cells where the statement was opened and the line is truly absent but no reason is shown (NR-F): total_liabilities (OSK, ARWR, ATR, SFD, AAL, CMC, CWST, VRNS, CVI, BKH, LSTR, MOS, BKH), operating income at CMC, GATX, EMN, KEX.
**(f) The 4 universal cells blank at all 224 companies.** BXSL(S100) is an actual BDC and `Total investment income` 320,469K Q2 / 645,940K 6M and net investment income 173,785K are filed but uncaptured (51 unexplained blanks, worst in block). `net_lease_revenue` deserves a real answer at VNO(S095), EPRT(S099), FR, JAN(S083).
**(g) Reasons that contradict the data:** BLCO(S097) `line_in_filing_not_extracted` on cost_of_revenue though the face has no cost line; HRB gross_profit/operating_expenses with R3 showing "Costs of revenues" 2,196,407K and "Total operating expenses" 3,037,706K; REXR debtor_days `immaterial_revenue_base` and growth `immaterial_prior_base` are artifacts of the wrong revenue; MBGL(S101) gross_margin 71.4% filled while gross_profit says `line_not_presented_in_filing`; SYRE/BAM growth reasons better as "no revenue".

**FC exemplars:**
- ARWR(S083, 10-Q 0000879407-26-000057): `pre_revenue_biotech_pharma` on cost_of_revenue/gross_profit vs 9-month revenue 413.0M (75.3M latest quarter).
- KMX(S085, 10-Q 0001170010-26-000104): operating_income/operating_expenses/operating_margin/roic carry the financial-institution reason; CarMax is a used-car retailer (SIC 5500); R2 has no operating income line.
- ARE(S086, 10-Q 0001035443-26-000066): `reit_net_interest_income_not_revenue` on 8 cells; R3 shows an equity REIT with no operating income/cost/gross-profit subtotal.

**Mechanism:** reason keyed on SIC or a stray tag ("reason chosen by SIC (2834) not by whether revenue exists", S097; "triggered by tags or SIC range, not by the statement actually presented", S085); non-payer reason "derived from absent input, not from absent activity" (S094).

## Theme T8: negative or meaningless ratios shown as numbers

**Companies affected: 41 negative trailing_pe displayed as a number, plus about 10 other meaningless ratios.** (All DI as displayed values; the underlying losses are FC at most companies.)
- Negative trailing_pe: HUT -13.21, TGTX -66.52, AXSM -42.66, REXR -20.57 (S080); VSAT -301.85, VIAV -268 (S081); WLK -6.51 (S082); AAL -24.79, ARWR -26.87 (S083); ZETA -3,353.01 (S084); LINE -47.77, NTSK -9.26 (S085); RAL -6.14, ARE -7.05, S -21.72 (S086); IONS -12.94, MP -122.44 (S087); SYRE -45.35 (S088); CAG -3.63, CLF -8.63 (S089); PRAX -20.61 (S090); MAC -35.29 (S091); MXL -62.87, HIMS -46.72, AAOI -99.42, GLXY -22.10 (S092); RIG -3.27, NAVN -12.53 (S093); FLR -3.83, TTAN -58.45, AVAV -29.10, IOVA -23.16 (S094); HR -68.5, MOS -8.94 (S096); BLCO -35.22, CZR -12.79, RYTM -29.06 (S097); WULF -2.75 (S098); VRNS -39.9, TFX -5.6 (S100); NIQ -16.28 (S101).
- Extreme or near-zero base: CWST 1,024 (S100), VNO 1100 (S095), MSGS 1,298.3 (S084), ALGM 483.6 (S096), KTOS 230.4 (S085), ACA 14.76 on TTM EPS dominated by discontinued ops gain (S087, FC EPS split).
- Negative-equity ratios: price_to_book / ROE AAL -2.02 / +8.2%, WYNN -46.7 / -265%, ETSY -5.74 / -15.0% (S083, equity FC); RNG price_to_book -11.24 (S092, FC equity deficit 610,359); AMRX price_to_book 190.7 (S093); HRB price_to_book 50.8, ROE 624% and CVLT price_to_book 123.6, ROE 131% (correct arithmetic, equity depressed by buybacks).
- Plausibility-only: HUT operating_margin -295% (arithmetic matches filing, includes mark-to-market digital asset loss); TFX net_margin -45.8% on mixed-basis revenue (S100).

**Cells:** wrong in the sense of meaningless (one displayed metric each); no case where the arithmetic disagrees with price / stored EPS.
**FC exemplars:** FLR(S094): trailing_pe -3.83, TTM EPS -11.81 tied to filed FY2025 EPS; AAL(S083, 10-Q 0000006201-26-000052): P/B -2.02, equity -3,972; RAL(S086): loss FC (FY2025 NI -1,222.5M).
**Mechanism:** "no sign guard on trailing_pe"; other loss makers carry `non_positive_growth_not_meaningful` only on peg_ratio.

## Theme T9: fiscal_year / period label wrong

**Companies affected: about 12.**
- FC (vs SEC companyfacts or dei): CNM(S081), GAP(S081), ANF(S091), M(S093), ACI(S092; plus 16-week Q1 has no Q1 row). DI: VSXY(S088, FY2027 vs company fiscal 2026), SLAB(S086, 53-week year ending 2026-01-03), AAL(S083, cover date 2026-07-17 labelled 2027 Q4), CAVA(S090, 16-week Q1 stored with `fiscal_period` NULL), OLLI(S099, Q1 labelled FY2027 vs SEC 2026, possible cause of the missed Q2), ORA(S101 share count under wrong FY), GTES(S091, period-end drift 2025-12-31 vs 2025-12-27, not a missing quarter), RNG(S092 FY2008/FY2010 lookbacks suspicious).
- Counterexamples (labels OK): NAVN (SEC itself says fy=2027), FLR/TTAN/CVLT/AVAV/OTEX (S094), DOCS, SAIC (S100), CPB (S097), ENS (S095).
- Cumulative YTD periods are stored with `fiscal_period` null (S081 general statement).

**Cells:** every period label for the affected company (CNM, GAP, ANF, M, ACI). Knock-on: SLAB blank TTM chain (revenue_ttm, diluted_eps_ttm, cfo_ttm, ebitda_ttm, ev_sales, price_to_sales, trailing_pe, peg_ratio, fcf_yield, ev_ebitda, net_debt_ebitda, debt_to_ebitda, ebitda_margin); CAVA about 7 cells (trailing_pe, price_to_sales, ev_sales, ebitda_margin, fcf_yield, peg_ratio, fcf_growth_5y_cagr); ACI trailing_pe, ev_sales, price_to_sales, fcf_yield. Values themselves are right (GAP FY Jan-2021 13,800, Jan-2022 16,670 match companyfacts).

**FC exemplars:**
- GAP(S081): FY ending 2021-01-30 stored 2021 vs SEC fy=2020; Q2 ending 2026-08-01 stored 2027 vs SEC 2026 (no accession given).
- ANF(S091): 0001018840-26-000047 is fy=2026 Q2 in companyfacts; stored fy=2027. 10-K 0001018840-26-000012 (Jan 31 2026) is fy=2025 in SEC, stored 2026.
- ACI(S092): 10-K 0001646972-26-000032 `fy=2025 FY` in SEC vs stored FY2026; no Q1 row.

**Mechanism:** "fiscal year taken from the calendar year of the period end date" (January year-ends; distinct from the NUE 52/53-week cause); 16-week first quarter stored as YTD so a four-quarter TTM builder sees only 3.

## Theme T10: recast / restated / spun-off / predecessor comparatives; missing quarters inside the last 8

**Companies affected: about 14.**
- ETSY(S083): Depop discontinued; Q2 2025 original 672.7 and recast 629.1 both stored `is_authoritative=false`, so Q1/Q2 2025 revenue absent; operating income Q2 2025 on recast basis, Q1 2025 not. FC for the 629,131 figure.
- TFX(S100): FY2025 recast 1,992.7M below its own 9M YTD 2,394.6M; Q1-Q3 2025 only as YTD; 5 of 8 quarters missing (only 2412, 2512, 2603, 2606 held). FC for Q2 2025 comparative 442,525K.
- FLR(S094): FY2021 14,156M (recast) vs originally filed 12,435M; FY2020 15,788M and FY2018 18,851M match neither opened filing (FC for 2021 and 2020).
- LNC(S084): FY2021 19,862M matches neither as-filed 19,230M nor restated 17,715M (FC vs companyfacts).
- NPO(S096): FY2020 and FY2021 revenue and NI missing (all 2019-2021 facts non-authoritative, DI).
- COLB(S082): Q1/Q2 2025 revenue absent (merger year; cause not investigated). CBC(S082): Q3/Q4 2025 absent (pre-IPO).
- MHK(S081): revenue_growth_3y `missing:prior_period(2023_Q2)` despite 80 stored periods; piotroski missing total_assets(2024) (DI). TKR(S083): 2016 quarterly rows absent. FR(S083): quarterly rows before 2017 absent.
- Predecessor/legacy history: JAN(S083, none before Q2 2026 10-Q), VAL(S096, 2021 missing, 2022-2025 wrong via T1), MGY(S095, FY2018 absent), WULF(S098, pre-2021 history is IKONICS), HUT(S080), FWONA(S102 tracking-stock restructure), DLB(S098, FY2018 1,054.6M vs about 1.17B recalled, unresolved).
- Derived quarter by subtraction (non-additive items): VIAV(S081, Q4 EPS 0.15 vs about 0.13), FLR(S094, Q4 diluted EPS -9.40 vs FY-less-9M -9.44); CHE derived Q4 net income (T13 scale).
- Missing quarters inside last 8 otherwise only as T3 (OSK, ZWS, IDA, AXS, AXTA, NOV, VFC, OMF, KNSA, POOL, STAG, EXLS, LSTR, RYN, OLLI, NNN) and SWX(S092, Q2 revenue), AAOI/MTDR/MATX/TEX/LNTH (Q2 capex only).
- Non-defects stated: RYN merger (assets 3.4B to 7.7B), TEX acquisition, ALKS/COMP/GATX/ASB acquisitions: comparisons not like-for-like but data correct.

**Cells:** whole quarters or years blank (ETSY, TFX, NPO) or on mixed bases (FLR, LNC, TFX). Counts: not stated beyond the above.
**Mechanism:** "re-presented comparatives conflict with originals and neither wins" (S083); "restatement basis not tracked per period; standalone quarters not formed from recast comparatives" (S100).

## Theme T11: net income basis inconsistent (consolidated vs attributable), equity incl. NCI

**Companies affected: 6 clear, several definitional.**
- FC: BAM(S102): stored net income 1,172 / 1,758 (consolidated incl. NCI) vs attributable to common 904 / 1,521; BRK, FWONA, PLNT store attributable. CELH(S088): NI 55.293 total while EPS 0.14 is on attributable 36.421; trailing_pe 123.5 from preferred-adjusted EPS, net_margin from total NI.
- Equity basis: RIG(S093, stored 8,370 = total equity incl. NCI), CZR(S097, stored 3,375 parent vs face total 3,552), ALGM(S096, stored 964,276K parent vs 965,962K total), CMC(S087, 4,696,932 vs 4,697,206, probably NCI), WFRD(S101, 1,788M vs 1,789M).
- Cash-flow basis: TFX(S100) and SSRM(S091): CFO total vs continuing-operations flips (blocks consistent TTM CFO).
- GLXY(S092) P/E must use NI incl. NCI (-278M TTM). DLB(S098), LB(S093), HUT(S080): attributable, treated as correct.

**Cells:** a handful per company (net_margin, trailing_pe, ROE, EPS pairs). Counts: not stated.
**FC exemplar:** BAM(S102): 1,172 stored vs 904 attributable; BAM EPS/PE overstated relative to per-share earnings.

## Theme T12: capex (and D&A, interest expense, receivables) tags unmapped, stale or split, causing FCF/EBITDA cascades

**Companies affected: about 90.**
- **Capex unmapped / wrong-tag / split (FCF chain 8 to 13 cells each: capex_resolved, capex_pct_revenue, fcf, fcf_margin, fcf_yield, fcf_per_share, fcf_gt_net_income, fcf_growth_yoy/3y/5y, dividends_pct_fcf, share_repurchases_pct_fcf).** FC (filed line read): REXR(PaymentsForCapitalImprovements), WAL, VSAT, RHP(PaymentsForCapitalImprovements filed 3x), NNN(PaymentsToAcquireRealEstateHeldForInvestment), FR, ARE(PaymentsToDevelopRealEstateAssets), VFC(PaymentsForCapitalImprovements), MUR and HR(PaymentsToAcquireOtherProductiveAssets 866,159K / 130,948K), AAOI(PaymentsToAcquireOtherPropertyPlantAndEquipment 335,132K), PACS(PaymentsToAcquireOtherPropertyPlantAndEquipment 48,355K), NE(PaymentsForCapitalImprovements), MATX(two lines), LYFT(combined purchase line), CHDN(maintenance 38 + project 79), VNO, MGY(PaymentsToAcquireOilAndGasPropertyAndEquipment), LOAR(PaymentsForProceedsFromProductiveAssets 6,973K), AAON, SNDR (three PP&E lines, only one mapped), INSW(custom insw_ tag), TEX and RYN(only SegmentExpenditureAdditionToLongLivedAssets), MTDR(Q2 tags), LNTH(Q2 YTD), APPF and MKTX (capitalised software omitted: understated about 12x / 30x), JAN(REIT additions), EPRT(single investment line), STAG, TRNO, MAC, GATX (combined line, correct to leave unmapped but no reason). NR-F (no capex line exists): RYTM, ASB, LNC.
- **D&A tags unmapped or split across two lines (EBITDA chain: ebitda, ebitda_margin, ev_ebitda, debt_to_ebitda, net_debt_ebitda, 5 to 9 cells):** VIAV, SLAB, AGCO (Depreciation + Amortization of intangibles), VSAT, AXSM, DBX, PRAX, IONS, AMRX, POOL, G(`us-gaap:Depreciation`), LOAR, ECG, CBSH, ACT, GLXY (D&A 9,161 on the face). Separately `missing:4_consecutive_quarters` EBITDA blanks from YTD-only cash-flow D&A at non-December year ends and 10-Q Q3 filers (OTEX, VFC, ESE, MSM, many).
- **Interest expense / net interest:** OSK, PACS(InterestExpenseNonoperating), ZWS, DY(Interest expense, net 37,965), EMN, PRMB, TTAN(188 on R4), VNO(89,582K Q2), OMF(InterestExpenseBorrowings), NAVN(31,971K), INGR, OTEX, LINE, MUR, LEA, MBGL(net), RAL(net), BROS, ELF.
- **Receivables / payables / inventory lines on the face but unmapped:** PTGX, AOS(669.8 and 525.7), MHK, ATR(897,660), ALKS, ANF(190,347), GAP inventory(2,297), AGCO(177.7), FLR(1,027), TEX, WLK, OSK(1,646.1), POOL, CAG, PPC, CWEN, GTES, ECG, LKQ.
- **Other face lines unmapped:** pretax income at LINE, VSXY, BROS, CZR, HXL, SUN; other_income_expense_net at ~40 companies; amortization_of_intangibles; ppe_net at JAN, MGY, SWX, PRMB.

**FC exemplars:**
- AAOI(S092): capex latest = Q1 58,225; cash flow "Purchase of property, plant and equipment" 335,132 (6M), tag `PaymentsToAcquireOtherPropertyPlantAndEquipment` 335,132,000 authoritative in core.fact (10-Q 0001437749-26-026278).
- VIAV(S081, FY2026 10-K): D&A as two lines, "Depreciation expense" 40.4 and "Amortization of acquired technologies and other intangibles" 67.9; EBITDA chain blank (9 cells).
- APPF(S084, 10-Q 0001433195-26-000058): capex H1 228K stored vs PP&E 228 + capitalised software 2,554 = 2,782K; FCF overstated.

**Mechanism:** capex candidate list too narrow (no fallback to the cash-flow line); D&A concept maps one combined tag with no sum of components; combined lines need a Standardization ruling (acquisitions vs capex, capitalised software, non-recourse debt).

## Theme T13: institutional_ownership_pct `implausible:institutional_shares_exceed_shares_outstanding` suppressed (new)

**Companies affected: about 55 in this block (DI; reason is truthful, cause not investigated).** Examples: PTGX, IDCC, REXR, TWST(S080); CNM, AOS(S081); HQY(S084); KEX, AXTA(S087); AWI, VSXY, SARO, Z, TRNO(S088); ALKS, HXL(S089); EPAM, LYFT, POOL, LB, NAVN, QLYS, G(S093); WEX, TTAN, CVLT, CVI(S094); PLXS, EXLS(S095); LEA, ST, HR(S096); CROX, LGND, BLDR, CZR, RYTM, GATX(S097); LSTR, MKTX(S098); MTG, CAKE, LKQ, OLLI, EPRT(S099); CWST, WH, TFX(S100); AVT, SSD(S086); BRK-A, PLNT, UHAL(S102). At TTAN, AOS, DUOL, RNG the cause is the stale share count (T4); at single-class companies (AVT, SSD) the 13F aggregation or denominator is suspect (double counting across filers). Cells: one per company (blank, not a wrong number).

## Theme T14: scale / unit / sign errors in source or derived values (new)

**Companies affected: 5 FC.**
- PLXS(S095): 10-Q revenue is unscaled in SEC's own companyfacts (Q3 FY26 1,304,778 vs 1,304,778 thousand = 1.305B; 9M 3,538,387) while NI/OI are scaled; Q4 FY25 derived 4,029,991,400 (should be about 1.06B); operating_margin 46.95 (4,695%); also negative annual revenue FY2011-FY2014 (-229,001,000; -154,844,000; -103,592,000; -108,372,000) (DI).
- CHE(S090): net_income FY2022-FY2025 stored 249,624 / 272,509 / 301,999 / 265,238 dollars vs 10-K thousands (265.2M); source rows came from DEF 14A/DEFR14A (0000019584-26-000005, -26-000052) non-authoritative, won over the 10-K fact 265,238,000; derived Q4 net income -211,378,001 / -188,221,762 (should be about +72M to +75M); net_margin TTM 0.39% (should be about 10%). FC for the 10-K, DI for source rows.
- MOS(S096): dividends_per_share_resolved 220,000 in three quarters (and -219,999.34 derived Q4) vs 0.22; dividend_yield 12,246.07 (1,224,607%) (DI; filing header "$ in Millions" read on R2).
- SAIC(S100): shares 42,000,000 (millions-scaled) vs 41,897,635; minor.
- CBSH(S082): zero-valued `Revenues` accepted as authoritative (see T1).
**Mechanism:** per-share items inherit filing scale; proxy-statement values win over the 10-K; "no cross-concept scale check (revenue << operating income)".

## Theme T15: EPS under a non-standard tag, EPS per class, FY-only TTM, YTD-only dividend tags (new)

- EPS filed only as `IncomeLossFromContinuingOperationsPerDilutedShare` (stale EPS, see T5): HXL, STAG, CHDN, CWEN, MGY. Per-class or tracking-stock EPS leaves diluted_eps blank: FWONA, BAM, PLNT, BRK-A, UHAL, GLXY(Class A EPS (0.09) and 192,869,271 diluted shares never stored). FPS(S084): no EPS on the FY face (FC); TTM builder refuses an FY row as TTM, so P/E 83.8 appears with EPS blank.
- Dividend yield blank for payers because only YTD or no per-share dividend tag exists: see T7(d). Special dividend summed into TTM yield: RYN 13.1% vs about 4.5-5% regular (Q4 2025 DPS 1.6725; DI).
- TTM cannot form with cash flow YTD-only or FY-only: TFX, SSRM(CFO 6M only), FPS, MBGL/NIQ/CBC (history limits, correct to be blank).
- PEGA(S099): derived operating_income lags core.fact for a 2-day-old filing (possibly transient).

## Theme T16: foreign private issuer in scope list

KZIA(S094): files 20-F (latest 2025-11-07, 263 facts, no 10-K/10-Q); 122 of 152 blanks unexplained, only 11 of 163 cells have values; worker recommends excluding from the Top-1000 (outside V1 scope per doc 02). Market cap also wrong (T4).

## Per-company verdicts

Format: TICKER | shard | market cap or rank (file does not give rank; "band" = the range the worker stated for the shard, not a per-company value) | wrong values shown | unexplained blanks | verdict. "Wrong values" counts are the files' own tables. Where a file states a verdict, it is used; otherwise DERIVED. **No company is strictly CLEAN**: every one has the 4 universal unexplained cells. SSD(S086) and TKR(S083) are the files' own "closest": SSD "CLEAN apart from the universal 4", TKR "CLEAN on values; strictly NOT CLEAN".

S080 (market caps 8.19B SPXC to 9.22B TWST, band)
PTGX | S080 | band | 0 (plus wrong reason pre_revenue) | 22 | NOT CLEAN
KNSL | S080 | band | 0 | 22 | NOT CLEAN
SPXC | S080 | 8.19B | 0 | 10 | NOT CLEAN
HUT | S080 | band | 1 (negative P/E) | 21 | NOT CLEAN
TGTX | S080 | band | 1 (negative P/E) | 13 | NOT CLEAN
UGI | S080 | band | 1 (revenue 1,299 vs 1,331) | 9 | NOT CLEAN
IDCC | S080 | band | 0 | 10 | NOT CLEAN
AXSM | S080 | band | 1 (negative P/E) + wrong blank total_debt | 18 | NOT CLEAN
REXR | S080 | band | 4 (revenue 0, P/S 26,210, stale op income, negative P/E) | 29 | NOT CLEAN
TWST | S080 | 9.22B | 0 | 11 | NOT CLEAN

S081 (no market caps stated)
CNM | S081 | n/s | 2 (fiscal_year labels; institutional implausible) | 19 | NOT CLEAN
AOS | S081 | n/s | 2 (shares stale 2015; operating income not on face) | 6 | NOT CLEAN
VIAV | S081 | n/s | 1 (negative P/E) | 13 | NOT CLEAN
MHK | S081 | n/s | 0 | 14 | NOT CLEAN (blanks only)
PB | S081 | n/s | 1 (revenue = total interest income) | 22 | NOT CLEAN
WAL | S081 | n/s | 1 (revenue 45.7M, net margin 572%, P/S 40.5) | 25 | NOT CLEAN
FORM | S081 | n/s | 0 | 10 | NOT CLEAN (blanks only)
VSAT | S081 | n/s | 1 (negative P/E) | 12 | NOT CLEAN
THG | S081 | n/s | 2 (operating income not on face; wrong no_dividend_history) | 25 | NOT CLEAN
GAP | S081 | n/s | 2 (fiscal_year labels; stale base total_debt) | 11 | NOT CLEAN

S082 (market caps 7.9-8.3B, band)
WLK | S082 | band | 1 (P/E -6.51) | 6 | NOT CLEAN
DBX | S082 | 8,253,252,000 | 0 shown (shares, total_debt, D&A missing) | 27 | NOT CLEAN
NEU | S082 | band | 0 | 9 | NOT CLEAN (blanks only)
COLB | S082 | band | 3 FC (FY2023/24/25 revenue) plus FY2021 DI; stale capex/total_debt | 21 | NOT CLEAN
NNN | S082 | band | 0 wrong; Q1 2026 missing; capex unmapped | 31 | NOT CLEAN
CBSH | S082 | band | 1 (revenue 0 in 5 periods); stale total_debt | 22 | NOT CLEAN
LEVI | S082 | 8.09B | 0 wrong; shares stale since 2019 | 4 | NOT CLEAN
CBC | S082 | band | 0 FC; revenue basis interest-only | 30 | NOT CLEAN
MOD | S082 | band | 0 | 11 | NOT CLEAN (blanks only)
RHP | S082 | band | 0 wrong; capex stale 2015 | 9 | NOT CLEAN

S083 (no band stated except JAN 7.93B, ETSY/others none)
OSK | S083 | n/s | 1 (latest quarter absent) | 9 | NOT CLEAN
ARWR | S083 | n/s | 2 (negative P/E; false reason) | 20 | NOT CLEAN
ATR | S083 | n/s | 0 | 12 | NOT CLEAN
JAN | S083 | 7.93B | 1 (market cap present while shares blank) | 55 | NOT CLEAN
AAL | S083 | n/s | 4 (label, P/E, P/B, ROE) | 7 | NOT CLEAN
ZWS | S083 | n/s | 1 (latest quarter absent) | 7 | NOT CLEAN
WYNN | S083 | n/s | 2 (P/B, ROE on negative equity) | 11 | NOT CLEAN
ETSY | S083 | n/s | 4 (missing/mixed revenue basis x2, P/B, ROE) | 13 | NOT CLEAN
FR | S083 | n/s | 1 (wrong reason on 5 cells) | 31 | NOT CLEAN
TKR | S083 | n/s | 0 | 4 | file: CLEAN on values, strictly NOT CLEAN

S084 (no market caps stated except IDA 7.61B)
MORN | S084 | n/s | 0 | 8 | NOT CLEAN (blanks only)
MSGS | S084 | n/s | 1 (shares frozen 2015, DI) | 8 | NOT CLEAN
FPS | S084 | n/s | 0 FC, 2 suspect (P/E 83.8 with EPS blank; P/S, FCF yield blank) | 30 | NOT CLEAN
ZETA | S084 | n/s | 1 (P/E -3,353) | 18 | NOT CLEAN
LNC | S084 | n/s | 2 (FY2018, FY2021 revenue) | 29 | NOT CLEAN
APPF | S084 | n/s | 1 (capex omits capitalised software) | 18 | NOT CLEAN
DY | S084 | n/s | 1 (operating_income_resolved -418M stale 2016) | 17 | NOT CLEAN
HQY | S084 | n/s | 0 | 8 | NOT CLEAN (blanks only)
NFG | S084 | n/s | 1 (revenue Q3/9M too low) | 9 | NOT CLEAN
IDA | S084 | 7.61B | 2 (two quarters missing; market cap on stale count) | 13 | NOT CLEAN

S085 (no market caps stated)
PACS | S085 | n/s | 1 (revenue 0.04% low) | 20 | NOT CLEAN
BOKF | S085 | n/s | 2 (revenue gross interest income; stale total_debt) | 23 | NOT CLEAN
ACM | S085 | n/s | 1 (total_debt base 41x low) | 8 | NOT CLEAN
LINE | S085 | n/s | 1 (negative P/E) | 9 | NOT CLEAN
KTOS | S085 | n/s | 0 found | 10 | NOT CLEAN
KMX | S085 | n/s | 2 (rounded revenue; two debt totals) | 12 | NOT CLEAN
NTSK | S085 | n/s | 1 (negative P/E) + shares missing | 22 | NOT CLEAN
TAP | S085 | n/s | 3 (revenue gross Sales; total_debt double count; shares 0 value) | 6 | NOT CLEAN
AXS | S085 | n/s | 1 (whole Q2 missing) | 34 | NOT CLEAN
URBN | S085 | n/s | 1 (debt stale 2020, DI) | 15 | NOT CLEAN

S086 (market caps: AVT 7.49B, SFD 7.30B, AGCO 7.32B, SSD 7.39B, MSM 7.30B, ARE 7.45B, SLAB 7.38B, S 7.54B, RAL 7.43B, LW 7.40B)
AVT | S086 | 7.49B | 0 | 5 | NOT CLEAN
SLAB | S086 | 7.38B | 2 (fiscal labels; TTM blanks) | 13 | NOT CLEAN
RAL | S086 | 7.43B | 1 (negative P/E) | 8 | NOT CLEAN
ARE | S086 | 7.45B | 2 (wrong reasons; negative P/E) | 32 | NOT CLEAN
SFD | S086 | 7.30B | 0 | 6 | NOT CLEAN
S | S086 | 7.54B | 1 (negative P/E) | 18 | NOT CLEAN
LW | S086 | 7.40B | 0 | 7 | NOT CLEAN
MSM | S086 | 7.30B | 0 | 7 | NOT CLEAN
AGCO | S086 | 7.32B | 1 (wrong reason) | 8 | NOT CLEAN
SSD | S086 | 7.39B | 0 | 4 | file: CLEAN apart from universal 4 (institutional % blank with dubious reason); strictly NOT CLEAN

S087 (market caps 6.98-7.44B, rank 861-870, band)
ACA | S087 | band | 1 (P/E on disc-ops gain) | 6 | NOT CLEAN
MGM | S087 | band | 0 | 8 | NOT CLEAN
KEX | S087 | band | 0 | 13 | NOT CLEAN
AXTA | S087 | band | 2 (Q2 absent; base total_debt 23M) | 12 | NOT CLEAN
CMC | S087 | band | 0 | 8 | NOT CLEAN
PRMB | S087 | band | 0 (base debt stale) | 10 | NOT CLEAN
MTDR | S087 | band | 1 (capex stuck at Q1) | 11 | NOT CLEAN
MP | S087 | band | 1 (P/E -122.4) | 14 | NOT CLEAN
IONS | S087 | band | 2 (P/E; base total_debt stale) | 15 | NOT CLEAN
EMN | S087 | band | 2 (base total_debt 765M vs 5,217M; stale operating income) | 7 | NOT CLEAN

S088 (market caps 6.8B-8.1B, band; Z 7.28B)
AWI | S088 | band | 0 | 9 | NOT CLEAN
VSXY | S088 | band | 0 FC / 1 DI (fiscal_year label) | 11 | NOT CLEAN
CELH | S088 | band | 0 (mixed NI/EPS basis flagged) | 10 | NOT CLEAN
SARO | S088 | band | 0 | 15 | NOT CLEAN
NE | S088 | band | 0 | 17 | NOT CLEAN
MATX | S088 | band | 0 | 7 | NOT CLEAN (closest)
Z | S088 | 7.28B | table 0/0; W4 lists shares_outstanding blank with market cap present (DI) | 16 | NOT CLEAN
VLY | S088 | band | 0 FC / 1 DI (revenue interest only) | 21 | NOT CLEAN
TRNO | S088 | band | 0 | 34 | NOT CLEAN
SYRE | S088 | band | 0 FC / 1 DI (negative P/E) | 24 | NOT CLEAN

S089 (market caps 6.7-7.8B, band)
ALKS | S089 | band | 0 | 14 | NOT CLEAN
COMP | S089 | band | 0 | 18 | NOT CLEAN
MSA | S089 | band | 0 (1 wrong reason) | 8 | NOT CLEAN
PPC | S089 | band | 0 | 7 | NOT CLEAN
NCLH | S089 | band | 0 | 10 | NOT CLEAN
CLF | S089 | band | 1 (negative P/E) | 6 | NOT CLEAN
STAG | S089 | band | 2 (Q2 missing; diluted EPS stale 2016) | 32 | NOT CLEAN
CAG | S089 | band | 1 (negative P/E) | 3 | NOT CLEAN (closest)
FSS | S089 | band | 0 | 4 | NOT CLEAN (closest)
HXL | S089 | band | 1 (diluted EPS stale 2020) | 6 | NOT CLEAN

S090 (DUOL 6.58B, FAF 6.761B, PATH 7.04B)
SNEX | S090 | n/s | 2 (revenue basis; stale operating income) | 20 | NOT CLEAN
PRAX | S090 | n/s | 1 (negative P/E) | 27 | NOT CLEAN
PATH | S090 | 7.04B | 0 found (shares blank) | 23 | NOT CLEAN
NOV | S090 | n/s | 1 (Q2 absent) | 5 | NOT CLEAN
CHE | S090 | n/s | 3 (FY NI scale, revenue history, derived Q4 NI) | 5 | NOT CLEAN
VCTR | S090 | n/s | 0 found | 18 | NOT CLEAN
ELF | S090 | n/s | 0 found | 10 | NOT CLEAN
CAVA | S090 | n/s | 0 wrong; about 7 cells blank with wrong cause | 18 | NOT CLEAN
FAF | S090 | 6.761B | 1 (round market cap) + 1 stale derived | 22 | NOT CLEAN
DUOL | S090 | 6.58B | 1 (shares stale 2021) | 18 | NOT CLEAN

S091 (market caps 6.4-7.1B band; LAD 6.55B, ANF 6.85B)
BROS | S091 | band | 0 | 17 | NOT CLEAN
GTES | S091 | band | 0 | 11 | NOT CLEAN
MAC | S091 | band | 1 (negative P/E) + 11 wrong reasons | 25 | NOT CLEAN
LNTH | S091 | band | 0 | 9 | NOT CLEAN
VFC | S091 | band | 1 (Q1 FY27 missing) + 2 wrong reasons | 9 | NOT CLEAN
ANF | S091 | 6.85B | 1 (fiscal labels) | 9 | NOT CLEAN
LAD | S091 | 6.55B | 1 (total debt stale) | 7 | NOT CLEAN (file: closest)
SSRM | S091 | band | 0 + 2 wrong reasons | 14 | NOT CLEAN
KNSA | S091 | band | 1 (Q2 missing) | 21 | NOT CLEAN
OMF | S091 | band | 1 (Q2 missing) | 30 | NOT CLEAN

S092 (market caps 6.1-6.9B, band)
ESE | S092 | band | 0 | 4 | NOT CLEAN (closest)
MXL | S092 | band | 1 (negative P/E) | 11 | NOT CLEAN
HIMS | S092 | band | 1 (negative P/E) + shares missing since 2019 | 13 | NOT CLEAN
ACT | S092 | band | 0 values; wrong reason on 8 cells | 30 | NOT CLEAN
AAOI | S092 | band | 2 (capex stale; negative P/E) | 13 | NOT CLEAN
ACI | S092 | band | 1 (fiscal_year off by one) | 8 | NOT CLEAN
UBSI | S092 | band | 1 (revenue = gross interest income) | 23 | NOT CLEAN
RNG | S092 | band | 1 (negative P/B) | 4 | NOT CLEAN
GLXY | S092 | band | 3 (operating income; no EPS/shares; negative P/E) | 35 | NOT CLEAN
SWX | S092 | band | 1 (Q2 revenue missing) | 12 | NOT CLEAN

S093 (NAVN 6.60B, LB 6.10B)
AMRX | S093 | n/s | 0 | 17 | NOT CLEAN
EPAM | S093 | n/s | 0 | 16 | NOT CLEAN
LYFT | S093 | n/s | 1 (history revenue) | 19 | NOT CLEAN
POOL | S093 | n/s | 1 (Q2 missing) | 8 | NOT CLEAN
LB | S093 | 6.10B | 0 | 19 | NOT CLEAN
RIG | S093 | n/s | 1 (negative P/E) | 14 | NOT CLEAN
M | S093 | n/s | 2 (revenue definition; fiscal_year label) | 10 | NOT CLEAN
NAVN | S093 | 6.60B | 1 (negative P/E) | 19 | NOT CLEAN
QLYS | S093 | n/s | 0 | 15 | NOT CLEAN
G | S093 | n/s | 0 | 9 | NOT CLEAN

S094 (KZIA 6,463M, TTAN 6,615M)
WEX | S094 | n/s | 1 (revenue) | 12 | NOT CLEAN
FLR | S094 | n/s | 1 (negative P/E) | 9 | NOT CLEAN
KZIA | S094 | 6,463M (wrong; about 12M) | 1 (market cap); 20-F filer | 122 | NOT CLEAN (exclude)
TTAN | S094 | 6,615M (suspect) | 2 (shares stale; negative P/E) | 21 | NOT CLEAN
CVI | S094 | n/s | 0 | 6 | NOT CLEAN (blanks only)
CVLT | S094 | n/s | 0 | 16 | NOT CLEAN (blanks only)
INGR | S094 | n/s | 1 (false no_dividend_history) | 11 | NOT CLEAN
AVAV | S094 | n/s | 1 (negative P/E) | 11 | NOT CLEAN
OTEX | S094 | n/s | 0 | 12 | NOT CLEAN (blanks only)
IOVA | S094 | n/s | 2 (negative P/E; false pre_revenue reason) | 15 | NOT CLEAN

S095 (no market caps stated)
INGM | S095 | n/s | 0 | 7 | NOT CLEAN (blanks only)
CWEN | S095 | n/s | 3 (FY2018/19 revenue, EPS stale, P/E) | 11 | NOT CLEAN
VNO | S095 | n/s | 1 (P/E 1100) | 28 | NOT CLEAN
PLXS | S095 | n/s | 3 (scaled revenue, negative revenue, margin 4,695%) | 10 | NOT CLEAN
ENS | S095 | n/s | 1 (revenue FY2012-2020) | 5 | NOT CLEAN
AAON | S095 | n/s | 1 (capex stale 2023) | 6 | NOT CLEAN
FNB | S095 | n/s | 1 (revenue interest-only) | 24 | NOT CLEAN
SFM | S095 | n/s | 0 | 10 | NOT CLEAN (closest)
EXLS | S095 | n/s | 1 (Q2 missing) | 12 | NOT CLEAN
MGY | S095 | n/s | 1 (diluted EPS stale 2019) | 15 | NOT CLEAN

S096 (no market caps stated)
HRB | S096 | n/s | 0 (1 stale value DI) | 8 | NOT CLEAN
HR | S096 | n/s | 5 | 28 | NOT CLEAN
MOS | S096 | n/s | 3 | 8 | NOT CLEAN
MUR | S096 | n/s | 0 (capex dead since 2019) | 7 | NOT CLEAN
NPO | S096 | n/s | 0 (FY2020/21 missing) | 4 | NOT CLEAN (universal 4 only)
VAL | S096 | n/s | 6 | 7 | NOT CLEAN
ST | S096 | n/s | 0 | 8 | NOT CLEAN
LEA | S096 | n/s | 0 | 6 | NOT CLEAN
ALGM | S096 | n/s | 0 | 8 | NOT CLEAN
POWL | S096 | n/s | 0 | 4 | NOT CLEAN (universal 4 only)

S097 (market caps about 5.8-6.2B, band)
CPB | S097 | band | 0 | 9 | NOT CLEAN
CROX | S097 | band | 0 | 11 | NOT CLEAN
LGND | S097 | band | 0 (2 wrong reasons) | 9 | NOT CLEAN
BLDR | S097 | band | 0 | 12 | NOT CLEAN
BLCO | S097 | band | 1 (negative P/E) + 1 wrong reason | 20 | NOT CLEAN
HWC | S097 | band | 1 (revenue = gross interest income) | 21 | NOT CLEAN
CZR | S097 | band | 1 (negative P/E) | 11 | NOT CLEAN
RYTM | S097 | band | 1 (negative P/E) + 1 wrong reason | 14 | NOT CLEAN
GATX | S097 | band | 0 | 21 | NOT CLEAN
BKH | S097 | band | 0 | 12 | NOT CLEAN

S098 (market caps 5.7-6.0B, band)
HOMB | S098 | band | 3 (2 FC) | 21 | NOT CLEAN
LOAR | S098 | band | 1 (capex missing) | 21 | NOT CLEAN
TEX | S098 | band | 1 (capex stale, Q2 missing) | 7 | NOT CLEAN
TTD | S098 | band | 1 (total_debt blank true zero) | 21 | NOT CLEAN
LSTR | S098 | band | 1 (Q2 absent) | 14 | NOT CLEAN
WULF | S098 | band | 1 (negative P/E) | 5 | NOT CLEAN
ESNT | S098 | band | 1 (total_debt blank) | 22 | NOT CLEAN
MKTX | S098 | band | 1 (capex excludes software) | 21 | NOT CLEAN
RYN | S098 | band (5.68B) | 4 (Q2 missing, Q1 revenue, capex stale, dividend yield 13.1%) | 5 | NOT CLEAN
DLB | S098 | band | 1 (total_debt true zero blank) | 13 | NOT CLEAN

S099 (market caps 5.5-5.9B, band)
MTG | S099 | band | 0 (wrong reasons) | 23 | NOT CLEAN
GBCI | S099 | band | 2 (revenue, P/S) | 27 | NOT CLEAN
CHDN | S099 | band | 2 (EPS stale 2023; capex stale 2019) | 8 | NOT CLEAN
MCY | S099 | band | 0 (wrong reasons) | 24 | NOT CLEAN
SXT | S099 | band | 0 | 8 | NOT CLEAN
PEGA | S099 | band | 1 (Q3 op income absent) | 11 | NOT CLEAN
EPRT | S099 | band | 1 (capex stale 2019) | 26 | NOT CLEAN
CAKE | S099 | band | 0 (total_debt blank with filed debt) | 5 | NOT CLEAN
OLLI | S099 | band | 1 (Q2 absent) | 5 | NOT CLEAN
LKQ | S099 | band | 0 shown; dividend reason false | 12 | NOT CLEAN

S100 (market caps 5.4-6.1B, band)
CACC | S100 | band | 1 (operating income) + stale debt | 31 | NOT CLEAN
WH | S100 | band | 0 | 13 | NOT CLEAN
RLI | S100 | band | 1 (operating income) | 24 | NOT CLEAN
CWST | S100 | band | 0 (P/E 1,024 flagged) | 23 | NOT CLEAN
ECG | S100 | band | 0 | 18 | NOT CLEAN
SAIC | S100 | band | 0 (shares rounded, minor) | 8 | NOT CLEAN
VRNS | S100 | band | 0 (negative P/E W5) | 15 | NOT CLEAN
DOCS | S100 | band | 0 | 17 | NOT CLEAN
BXSL | S100 | band | 0 | 51 | NOT CLEAN
TFX | S100 | band | 2 (mixed-basis revenue; negative P/E) | 6 | NOT CLEAN

S101 backfill, 8 companies (BGC 5.43B, SNDR 5.43B, MBGL 5.48B)
ASB | S101 | n/s | 1 (revenue basis) | 26 | NOT CLEAN
BGC | S101 | 5.43B | 2 (revenue; operating income) | 25 | NOT CLEAN
INSW | S101 | n/s | 3 (revenue; operating income; capex) | 12 | NOT CLEAN
MBGL | S101 | 5.48B | 1 (gross margin) | 31 | NOT CLEAN
NIQ | S101 | n/s | 1 (negative P/E) | 26 | NOT CLEAN
ORA | S101 | n/s | 0 | 9 | NOT CLEAN (blanks only)
SNDR | S101 | 5.43B | 1 (capex) | 14 | NOT CLEAN
WFRD | S101 | n/s | 0 (1 wrong reason) | 3 | NOT CLEAN (nearest to certifiable; 3 = universal cells)

S102 backfill, 6 companies, market cap blank for all
BRK-A | S102 | blank | 3 (revenue; operating income stale 2013; shares stale 2011) | 20 | NOT CLEAN
FWONA | S102 | blank | 2 (diluted EPS stale 2016; shares blank) | 18 | NOT CLEAN
BAM | S102 | blank | 4 (revenue; net income basis; stale operating income; EPS stale 2023) | 15 | NOT CLEAN
PLNT | S102 | blank | 1 (diluted EPS blank/stale) | 17 | NOT CLEAN
UHAL | S102 | blank | 2 (revenue about 7x low; shares stale 2022) | 20 | NOT CLEAN
SUN | S102 | blank | 0 shown wrong; equity and shares blank | 13 | NOT CLEAN

## History-window items

**S080 (DI):** earliest FY revenue held vs earliest 10-K in core.filing: SPXC 2007 vs 1993; UGI 2008 vs 1997; TGTX 2016 vs 2007; REXR 2014 vs 2013; AXSM 2022 vs 2015 (plausible, pre-2022 revenue zero); TWST 2017 vs 2018 and HUT 2022 vs 2024 (facts from later comparatives; HUT is a 2023 re-domiciled registrant); KNSL 2014 vs 2016; PTGX 2017 vs 2016; IDCC 2008 vs 2007. FY2021 revenue stored SPXC 1,219.5M, UGI 7,348M, KNSL 653.5M, IDCC 425.4M, not confirmed against a later 10-K. Missing quarters in last 8: none for any of the 10 (REXR revenue wrong, T1).
**S081:** earliest annual revenue vs earliest 10-K: GAP 2008 vs 1994; **AOS 2016-12-31 vs 1993 (2009-2015 missing)**; VSAT 2009 vs 1997; **MHK 2011 vs 1996 (2009-2010 missing)**; VIAV 2009 vs 1996; THG 2008 vs 1996; FORM 2009 vs 2003; PB 2008 vs 1998; CNM 2020 vs 2022 (IPO fine); WAL 2009 vs 2001. FC spot checks vs SEC companyfacts: GAP FYE Jan-2021 13,800 and Jan-2022 16,670; AOS FY2018 3,187.9 and FY2021 3,538.9; MHK FY2021 11,200.6 all match. Last 8 quarters: all present (MHK has a Q2 2023 label gap in a growth cell, DI).
**S082:** CBSH 2008 vs 1997; MOD 2010 vs 1996; LEVI 2009 vs 2001; NNN 2008 vs 1996; COLB 2009 vs 1997 (**FY2021 83.3M wrong**); RHP 2009 vs 1998; WLK 2009 vs 2004; NEU 2008 vs 2005; CBC 2024 vs 2026 (IPO); DBX 2016 vs 2019. Spot checks marked "memory" (not opened): MOD FY2021 1,808.4M, LEVI 5,763.9M, NNN FY2018 622.7M, WLK 8,635/11,778, NEU 2,356.1M, DBX 1,391.7/2,157.9M. Missing quarters: NNN Q1 2026 (0 facts); COLB Q1/Q2 2025 revenue absent; CBC Q3/Q4 2025 absent.
**S083 (DI):** AAL 2013 vs 1993; TKR 2011 vs 1993 (2016 quarterly rows absent); OSK 2008 vs 1994; ARWR 2011 vs 2006; ATR 2008 vs 1996; **FR 2016-12-31 (FY2009-2015 annual revenue not held; quarterly rows before 2017 absent)**; WYNN 2008 vs 2002; ETSY 2013 vs 2015; ZWS 2010 vs 2012; JAN none (first filing Q2 2026 10-Q). FY2018/FY2021 spot checks agree "from memory" (DI). Missing quarters: OSK and ZWS 2026-06; ETSY 2025-03 and 2025-06; JAN has only 2025-03/06 and 2026-03/06.
**S084:** MORN 2008 vs 2006; LNC 2007 vs 1994 (**FY2018 and FY2021 fail, FC**); NFG 2010; IDA 2008; **DY 2016-07-30 vs 1997 (no annual revenue before FY2016, probable older tag unmapped)**; HQY FY2013; APPF 2013; ZETA 2019; MSGS 2014; FPS 2025 (2 annuals). Spot checks otherwise "plausible" (DI). Missing quarters: IDA 2026 Q1, Q2.
**S085:** TAP 2016 vs 1994 (2009-2015 missing); ACM 2017 vs 2007 (2009-2016 missing); BOKF 2008 vs 1996; URBN 2009 vs 1997; KTOS 2009 vs 2001; KMX 2009 vs 2003; AXS 2008 vs 2004; LINE 2022 vs 2025, PACS 2022 vs 2025 (IPO 2024); NTSK 2024 vs 2026. ACM FY2021 13,340,852,000 matches recalled; KMX FY2021/FY2022 match except rounding; TAP FY2021 12,449.9M is gross Sales (T1); BOKF FY2021 1,179.9M is gross interest income. Gaps: AXS Q2.
**S086:** AVT 2008 vs 1994 (revenue_growth_10y `missing:prior_period(2016_Q4)` unexpected); SLAB 2009 vs 2000; SSD 2008 vs 1996; MSM 2009 vs 1996; **AGCO 2016-12-31 vs 1996 and ARE 2016-12-31 vs 1997 (2009-2015 absent, why 10y CAGRs blank)**; SFD 2023 vs 1994 (entity change 2024); S 2020 vs 2022; RAL 2023 vs 2026; LW 2017. AVT FY2025/FY2024 match 10-K comparatives (FC). Missing-quarter scan only for SLAB and RAL (not done for the rest).
**S087:** all DI: ACA 2016 vs 2019; MGM 2008 vs 1994; KEX 2008; AXTA 2014 vs 2015; CMC 2009; PRMB 2022 vs 2025; MTDR 2010 vs 2012; MP 2019 vs 2021; IONS 2008 vs 2003; EMN 2010 vs 2003. Missing quarters: AXTA Q2 2026; MTDR Q2 2026 capex only.
**S088:** AWI 2009 vs 1993; MATX 2012 vs 1994; VLY 2008 vs 1993; TRNO 2016 vs 2009; CELH 2017 vs 2008; Z 2013 vs 2015; VSXY 2020; NE 2020; SYRE 2016; SARO 2022. FY2018/FY2021 spot check and missing-quarter scan not done.
**S089:** FY revenue starts 2016 (HXL, STAG), 2019 (COMP), 2008-2012 (others) vs 10-Ks to 1994; HXL and STAG start later than XBRL history (about 2009-2011). No FY2018/FY2021 spot check. Missing quarter: STAG Q2 2026.
**S090:** SNEX 2009 vs 2007; PRAX 2022 (value 0); PATH 2020 vs 2022; NOV 2007 vs 1996; **CHE 2008 vs 1993 (FY2021 1,261.2M vs filed 2,139.3M, FC)**; VCTR 2015; ELF 2015; CAVA 2021 vs 2023; FAF 2008; DUOL 2020. Missing quarters: NOV Q2 2026; CAVA Q1 FY25 and Q1 FY26 exist but with NULL fiscal_period.
**S091:** BROS 2019 vs 2021; GTES 2018 vs 2017; MAC 2008; LNTH 2013; VFC 2007 (FY2024/FY2025 match FY2026 10-K comparatives, FC); ANF 2009; LAD 2009; SSRM 2019 vs 2021; KNSA 2021 vs 2018 (3 years of 10-K unused); OMF 2011 vs 2013. FC spot checks OK for BROS, GTES, MAC, LNTH, LAD. Missing quarters: VFC 2026-06-27, OMF 2026-06-30, KNSA 2026-06-30.
**S092:** ESE 2008 vs 1997; MXL 2009; HIMS 2019; ACT 2019 vs 2021; AAOI 2011; ACI 2016 (labels off by one); UBSI 2008 vs 1994; RNG 2011 vs 2013; GLXY 2023 vs 2025; SWX 2015. No FY2018/FY2021 check. Missing: ACI no Q1 rows; SWX Q2 revenue; AAOI Q2 capex.
**S093:** AMRX 2016 vs 2017; EPAM 2010; **LYFT 2017: FY2018 and FY2021 wrong (FC)**; POOL 2008; LB 2023; RIG 2007; M 2008 (FY2017 24,939 = net sales); NAVN 2024; QLYS 2010; G 2008. Only LYFT checked against SEC data. Missing quarter: POOL Q2 2026.
**S094:** WEX 2008; **FLR 2007 (recast basis, FC)**; KZIA none; TTAN 2023 (4 FYs from S-1 style comparatives); **CVI FY revenue only from 2016 vs 10-Ks from 2008 (about 8 years not held, cause not investigated)**; CVLT 2009; INGR 2008; AVAV 2010; OTEX 2007; IOVA 2013. No missing quarters in last 8 for 9 non-KZIA companies.
**S095:** PLXS negative FY2011-14 (T14); CWEN FY2018/19 wrong (FC), CWEN FY2013 434M after 175M unchecked; ENS FY2012-FY2020 wrong (FC FY2018-20), FY2021 2,977,932K correct; MGY FY2018 absent (predecessor/successor); INGM FY2022+ only; FNB no FY2016/FY2017 rows. Detector "FY revenue jumps >2x or <0.5x": 9 hits across these ten, 4 confirmed real errors.
**S096:** HRB 2008 (19 annual points); POWL 2010; **VAL 2016 (2021 missing; 2022-2025 wrong)**; MUR 2007; LEA 2016; ALGM 2020; ST 2009; **NPO missing FY2020 and FY2021**; **MOS earliest annual revenue 2018-12-31 (8 points) vs 10-K from 2005; 2005-2017 annual series absent**; HR 2009 (wrong, T1). No missing quarters in last 8 for any.
**S097:** CPB 2017-07-30 (10 FY); BLCO earliest FY 2020 (carve-out); FY2021 revenue matches public figures for all ten but not opened (DI). Last 8 quarters of revenue present for all ten.
**S098:** HOMB 2009 vs 2006; LOAR FY2023 (3 FY); TEX 2009; TTD 2016; LSTR 2009; WULF 2017 legacy registrant (IKONICS); ESNT 2012; MKTX 2009; RYN 2008; DLB 2008 (FY2018 1,054.6M vs recalled 1.17B, unresolved). Missing quarters: RYN and LSTR 2026-06.
**S099:** CHDN 2011; MCY 2008; SXT 2011; GBCI 2008 (**series broken in 2021, 627M FY2020 then 65M FY2021**); MTG; CAKE; PEGA; LKQ; OLLI 2017-01-28 (FY ending 2016-01-30 missing); EPRT 2017. Missing quarter: OLLI Q2 2026.
**S100:** CACC 2009; WH 2016 vs 2018; RLI 2008; CWST 2010; ECG 2022; SAIC 2012; VRNS 2012; DOCS 2020; BXSL revenue not held; **TFX 2012: 5 of 8 quarters missing (only 2412, 2512, 2603, 2606 held; Q1-Q3 2025 and Q3 2024 as YTD only)**. FY2018/FY2021 spot check not done.
**S101:** ASB 2008 (mixes bases: FY2023 net basis 1,102,756K vs 10-K gross 1,958,052K; FY2024/FY2025 tie to gross); BGC 2009 (FY2023-25 all fail, FC); INSW 2014; MBGL none (new registrant); NIQ 2023; ORA 2008; SNDR 2015; WFRD 2012. Missing-quarter scan skipped.
**S102:** not done (no FY2018/FY2021 comparison, no last-8 scan); BAM history starts 2022-12-31 (40-F/20-F era), FWONA period_gap.

## Population counts quoted

| Count | Quoted in | Query or estimate |
|---|---|---|
| 683 of 5,206 companies carry `implausible:institutional_shares_exceed_shares_outstanding` (1,690 blank, 3,516 filled) | S088 (also quoted as 683 in S091, S093, S094, S097) | Query (coverage table); the later quoters repeat it |
| 328 companies / 1,470 blank cells carry `financial_institution_interest_income_not_revenue` | S091 | Quoted as a count; query not shown in file |
| 189 companies carry `reit_net_interest_income_not_revenue` | S091 | Query/count, not shown |
| 142 non-financial companies carry the financial-institution reason | S101 (from S023) | Quoted from S023 |
| 168 companies use the revenue-minus-OperatingExpenses operating income derivation | S080 (S023 family), S100, S101 | Quoted from S023 |
| 477 companies with no `shares_outstanding` value, 270 with latest period older than 2025-10-01, 4,486 current | S081 | Query (lineage) |
| 35 companies have a Q4 ending 2026-01-01..07 labelled FY2026 | S086 | Single cheap query; worker says not all verified mislabelled |
| 1,875 blank cells across 495 companies carry `pre_revenue_biotech_pharma`; 464 are `gross_profit` cells, 336 of those at companies whose revenue cell has a value | S097 (464 also in S094) | Query on coverage table |
| 3,433 blank cells carry `no_dividend_history` | S094 | Count, not shown |
| 1,642 negative / 2,174 non-negative / 796 null of latest trailing_pe rows (period_end 2026-10-19 or later) | S097 | Query |
| 140 `dividends_per_share_resolved` rows with absolute value >= 1,000 across 39 companies | S096 | Live query |
| 6 other loss makers in the population show negative P/E (S023 figure) | S080 | Quoted from S023 |
| 198 of 1,630 cells unexplained across the shard's 10 companies | S083 | Query (coverage totals) |
| 9 hits from the "FY revenue jumps >2x or <0.5x between adjacent years" detector across the shard's ten, 4 confirmed real errors | S095 | Query within shard |
| KZIA: 11 of 163 cells have values; 122 of 152 blanks unexplained | S094 | Query |
| Population counts for 0-facts filings, REV-TAG, dual-class shares, capex-tag families | S080, S086, S087, S088, S091, S092, S093, S098 | Stated as "not run" or "times out unchunked"; no number given |
| D1 book_value_per_share blank: 10 of 10 (S080, S086, S096, S097), 8 of 10 (S081, S082, S087, S095), 9 of 10 (S083, S088, S089, S093, S094, S100), 6 of 8 (S101), 9 of 10 stated in S091 as blank at several | S080-S101 | In-shard counts from coverage cells |
