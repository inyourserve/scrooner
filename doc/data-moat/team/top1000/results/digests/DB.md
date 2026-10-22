# Digest DB (block B): S020 through S038 plus S010-filing-checked

Read-only synthesis of the shard result files. Evidence labels are the workers' own (FILING-CHECKED = worker read the face statement or cover R-page of the named filing; DATA-INFERRED = our tables only). No database, SEC or code was touched while writing this. Accessions are copied as written in the files; where a file only names the 10-Q it read, that is the accession given.

## Block

Read in full: S020, S021, S022, S023, S024, S025, S026, S027, S028, S029, S030, S031, S032, S033, S034, S035, S036, S037, S038, and S010-filing-checked.md (S010.md was not read, as instructed). No file missing. Partial or caveated: S022 (IAU gold trust excluded, only W12 noted), S037 (SLV silver trust excluded; FTI blank list cut off in the worker's query; HAL cash-flow page rendered empty), S035 (RKLB 10-Q never opened), S029 (header says 363 blank cells but per-company blanks sum to 300; flagged, not resolved), S023 (run inline by the main session, not a sub-agent). About 191 operating companies covered. Market-cap bands per file (as stated by the workers): S010fc 123.6-133.4B, S021 61.2-66.1B, S025 49-52B, S026 46.8-51.1B (ranks 251-260), S027 44-49B, S028 42.4-44.7B, S034 31.2-34.3B, S036 28.9-30.7B (ranks 351-360), S037 27.0-29.5B. Other files give no band. No worker found an impossible market cap in this block, but several caps sit on the wrong share basis (see T4).

Coverage-denominator note quoted in S023: the 2026-10-20 coverage run after commit fb26fb6 ("a metric cell is filled only if its LATEST period has a value") gives 1,267 of 1,630 filled (77.7%) for S023's ten, against 83.8% in shards.csv; unexplained stayed 110.

No worker ran an FY2015 / FY2018 / FY2021 spot-check. Nearly every file lists "FY2025 10-K headline check not done" for most companies; only the latest 10-Q (plus YTD cash flow) was compared. See "History-window items".

---

## Themes

### T1 revenue resolves to a partial/sub-line tag instead of the statement total
- Companies affected: 23 FILING-CHECKED, 1 DATA-INFERRED.
  - FILING-CHECKED: MET(S021), OXY(S021), LNG(S022), MPLX(S022), VST(S025), DVN(S023), URI(S020), FITB(S027), AMP(S028), ADM(S029), PAYX(S029), HIG(S031), IBKR(S031), CCI(S032), CNC(S033), SUNB(S035), MTB(S035), NTRS(S035), EXR(S036), WTW(S036), RJF(S036, convention choice: gross revenue stored, net revenues 3,928M filed), CFG(S038), IMO(S020, stored includes 81M other income). 
  - DATA-INFERRED: HBAN(S035: revenue tag inferred, stale 472M; the stale part is FILING-CHECKED).
  - Opposite error (real revenue suppressed): RKT(S035, revenue blank under `financial_institution_interest_income_not_revenue` although the face shows "Total revenue, net" 2,784 Q2 / 5,725 6M; FILING-CHECKED).
- Cells: wrong values shown. Spill-over wrong ratios listed by workers: MET net_margin 101.7%, operating_margin 221.5%, P/S 23.9; EXR operating margin 1,123.6%, net margin 754.8%, P/S 220.8x; MTB net margin 185%; CCI Q2 net margin 229%; SUNB net margin 62.5%; NTRS 58.7%; HIG P/S 28.85 and EV/Sales 31.9; IBKR P/S 13.6; CFG P/S 15.4. Number of dependent cells per company: not stated.
- Exemplars (FILING-CHECKED):
  - MET: stored 724M Q2 / 1,458M 6M vs "Total revenues" 19,154M / 38,228M on R4 of 10-Q 0001099219-26-000050; `Revenues` is in core.fact as authoritative for the same period (worker: "the most severe seen").
  - ADM: stored 6,386M Q2, 24,956M FY2025 vs filed Revenues 22,681M and 80,269M (10-Q 0000007084-26-000042; 10-K 0000007084-26-000011 read for income statement); also derived Q4 2024 revenue stored as -25,710M (DATA-INFERRED mixed-basis subtraction).
  - EXR: stored 34.904M Q2 vs Total revenues 874.152M (10-Q 0001289490-26-000053). HIG: 111M vs 7,263M (10-Q 0000874766-26-000060). CCI: 41M vs Net Revenues 1,008M (10-Q 0001051470-26-000074; FY2025 215M vs 4,264M in 10-K 0001051470-26-000016).
- Mechanism (workers' wording): `RevenueFromContractWithCustomerExcludingAssessedTax` is picked first even though `Revenues` (the statement total) is also filed and larger; for banks the ASC 606 tag is a noninterest-income footnote subset; for CNC the 606-style line excludes premium tax revenue; for DVN/VST/LNG it excludes derivative/hedge results.

### T2 operating income derived or taken from a non-face line where the filer presents none (or a different figure)
- Companies affected: FILING-CHECKED: AJG(S020), APO(S020), MET(S021), DVN(S023), AFL(S022), HONA(S024), OXY(S021, stale derived), HIG(S031, stale 2020 derived). DATA-INFERRED: ARES(S031: operating_income_resolved 248.6M derived from OperatingExpenses and the 606 revenue tag; face has no operating income).
- Cells: wrong values shown (operating_income_resolved, then operating_margin, roic, interest_coverage built on it). Stored margins: AJG 83%, AFL 70.9%.
- Exemplars (FILING-CHECKED):
  - DVN: stored 1,497 Q2 / 2,318 6M / 2,279 FY2025. Devon presents no operating income; earnings before income taxes filed 2,384 / 2,550 / 3,466. Filed `OperatingExpenses` 5,506 = total expenses 5,033 plus income tax 473, so stored = product sales minus costs minus income tax (10-Q 0001193125-26-334340; FY2025 10-K 0001193125-26-056485).
  - AJG: stored 3,324 Q2 / 7,439 6M = revenue 4,003 minus `OperatingExpenses` 679, but 679 is only the caption "Operating", one of six expense lines; total expenses 3,589; earnings before taxes 414 (10-Q 0001628280-26-053489).
  - MET: `OperatingIncomeLoss` 3,235M (6M) is not on the face statement (pretax 2,542M); filed from a segment note (10-Q 0001099219-26-000050). HONA: stored 995M Q2 / 2,090M 6M; face has no operating income, income before taxes 378 (10-Q 0002089271-26-000021).
- Mechanism: "Revenue minus `OperatingExpenses`" derivation is valid only where OperatingExpenses is the statement's own operating-cost subtotal (S023); or `OperatingIncomeLoss` taken from a segment/note total (MET, HONA). APO is arithmetically revenue minus total expenses, acceptable only if labelled.
- Population quoted: 168 companies use exactly that two-input derivation, 103 with a 2026 period (S023, query).

### T3 latest 10-Q/10-K has 0 facts in core.fact, or is absent from core.filing (page a quarter or more stale)
- Companies affected (25 plus one transition filing):
  - 0 facts, FILING-CHECKED for the filed values: SPGI(S010fc), URI(S020), BE(S021), DLR(S021), NXPI(S023), D(S023), GRMN(S024), F(S025), HUM(S025), PYPL(S025), IQV(S028), EXC(S028), ED(S029), CARR(S027), BIIB(S032), VMC(S033), CTSH(S034), GEHC(S034), HBAN(S035), DTE(S038), FE(S038), CNP(S038).
  - 0 facts, DATA-INFERRED for the filing contents (value comparison not shown): CAH(S022, 10-Q 0000721371-26-000018).
  - Filing row absent from core.filing although SEC companyfacts has it: HPQ(S037, FILING-CHECKED), MDB(S038, FILING-CHECKED).
  - FERG(S027): 10-KT 0002011641-26-000006 (Aug-Dec 2025 transition) not in core.filing (see T9).
- Companyfacts also lacked the accession (checked live) for: SPGI, URI, BE, DLR, NXPI (fetched 2026-10-08), D (2026-10-09), IQV, EXC, CARR, BIIB, CTSH, GEHC. For HPQ and MDB companyfacts has it.
- Cells: whole latest quarter missing; every TTM, growth, EBITDA and per-share metric is a quarter stale. Examples of materiality: BE revenue 1,065.4M filed vs 746.4M stored; HBAN assets +26% by merger; DLR assets +11%; BIIB Q2 EPS 0.66 vs 4.33 prior.
- Exemplars (FILING-CHECKED):
  - SPGI: Q2 10-Q 0000064040-26-000045 has full R-pages (revenue 4,146 3M, assets 62,906) but 0 facts; stored latest period is Q1 (revenue 4,171).
  - BE: 0001628280-26-050247 (revenue 1,065.4M, NI attributable 196.3M, EPS 0.62). 
  - HPQ: 10-Q 0000047217-26-000051 filed 2026-08-27 (revenue 15,677, EPS 0.71) not in core.filing (max filing_date 2026-08-07); MDB: 0001628280-26-059830 filed 2026-09-01.
- Mechanism (workers' wording): upstream of our parser for the 0-facts group (SEC companyfacts has no fact for the accession even though the filing has XBRL; fix path in PLAYBOOK: parse the filing's own XBRL instance); for HPQ/MDB the filing row itself was never ingested ("collection/ingestion gap"). S028 suggests testing whether EXC's multi-registrant combined 10-Q is why it is skipped; S038 DTE/FE/CNP and S031 PEG are also combined parent-and-utility filings (PEG stored values did match the parent).
- Populations quoted: see "Population counts quoted" (167, 190, 150, sample 27 of 236).

### T4 shares_outstanding blank/stale/wrong; market cap on the wrong share basis; per-share cascade
- Companies affected.
  - Dual/multi-class cover not summed, shares blank (FILING-CHECKED counts on the cover or balance sheet): TEAM(S024), MSTR(S026), WDAY(S026), XYZ(S027), EL(S030), TKO(S033), OKTA(S034), CRWV(S034), ZM(S037), DTE n/a. DATA-INFERRED: VG(S035), MDLN(S035), RKT(S035), RDDT(S036), TW(S038: stored 0 at 2019-09-30, four classes), CVNA(S028: stored shares fact is a literal 0 from 2017-03-31), HSY(S032: per-class EPS/DPS, shares one class only).
  - Class A only counted: EXPE(S033: 114,473,000 vs cover A 114,495,891 + B 5,523,452 = 120,019,343, FILING-CHECKED), IBKR(S031: market cap 37.1B = price x Class A only; 77% of net income is noncontrolling, FILING-CHECKED).
  - Stale or rounded or inconsistent count: NKE(S024: single value 855,351,589 dated 2015-07-17 vs diluted weighted 1,484.2M; market cap about 40% low; share count FILING-CHECKED), DVN(S023: cover rounded to 0.1B, 1,100,000,000 vs balance sheet 1,150M, market cap 55.39B about 4% low; FILING-CHECKED), SPGI(S010fc: 296,000,000 round vs Q2 cover 294.8M; FILING-CHECKED), PCG(S032: cover 2,680,110,496 vs balance sheet 2,202,366,726 at 6/30, stable 22% gap three quarters, market cap 35.42B, which is right NOT resolved; FILING-CHECKED numbers), HON(S020: shares 633.7M Q1 vs 316.9M Q2, Q1 EPS 1.29 not restated; FILING-CHECKED share counts, EPS mixing DATA-INFERRED), ARES(S031: shares stale 2024-12-31 313M, implied cap share count 326M matches no stored value), CAH/UI(S022/S031: cover count labelled next fiscal year, harmless alone).
  - Market cap on weighted diluted count because no point-in-time count: CVNA (price 60.30 x 740,174,000 = 44,632,492,200 exactly, DATA-INFERRED). Unknown share source behind a computed market cap: XYZ (46.99B), TKO (34.7B), EL (38.26B), OKTA (34.3B), CRWV (32.6B), RKT (31.6B, round P/E 51), ZM, TW (28.1B).
  - Per-share pairing D1 (equity at balance-sheet date, shares at cover date; book_value_per_share `incomplete:numerator|denominator`): quoted hit rates S010fc 10/10, S020 6/10, S021 10/10, S022 8/9, S023 8/10, S025 8/10, S026 8/10, S027 10/10, S028 10/10, S029 9/10, S030 9/10, S031 7/10, S032 9/10, S035 9/10, S036 10/10, S037 9/9, S038 7/10 (+TW own cause). S033, S034 give no count.
- Cells: blank per-share cascade of 8-12 cells per dual-class company (book_value_per_share, net_cash_per_share, diluted_shares_growth x3, share_dilution_trend, total_shareholder_yield, piotroski, institutional_ownership_pct); wrong market cap at NKE, DVN, IBKR, EXPE, CVNA, PCG(unresolved). Totals: not stated.
- Exemplars (FILING-CHECKED): NKE (above); XYZ cover R1 540,816K Class A + 59,979K Class B = 600,795K, nothing stored; EL cover Class A 247,291,223 + Class B 114,507,344 = 361,798,567 (and cover "Entity Public Float $26" under "$ in Billions", a scale trap).
- Mechanism: class-dimensioned `EntityCommonStockSharesOutstanding` facts are dropped instead of summed. For D1, S027 gives the precise cause: the metric IS computed at the balance-sheet date (LHX 2026-07-03 value 106.80; CIEN 2026-08-01 value 21.54) and then hidden by a second NULL row at the cover date (LHX 2026-07-24; CIEN 2026-08-28), and "latest period must have a value" reads the cell blank.

### T5 stale series counted as filled (latest period years old, coverage says has_value)
- Companies affected (FILING-CHECKED stale, i.e. worker opened the later filing and showed the line still exists or no longer exists): BMY(S010fc: operating_income Q1 2012, gross_profit 2020), NEM(S010fc: inventory 2015-03-31, interest_expense 2013-03-31), MPC(S010fc: ppe_net 2021-09-30), VRTX(S010fc: debt 2011), PGR(S010fc: total_debt 2016), FTNT(S010fc: total_debt 2021), VLO(S010fc: capex 9M-2025), OXY(S021: op income 2016), COHR(S027: op income 2024-06-30), COIN(S027: capex 2023-09-30), MNST(S027: EPS 2011-06-30, debt 2025-03-31), AIG(S028: capex FY2023), VTR(S028: operating_income_resolved 2011), HSY(S032: EPS/DPS 2010-04-04), BKR(S024: EPS and op income 2024-12-31), VRSN(S037: EPS 2022-12-31, debt 2013-12-31), ILMN(S030: total_debt 2018, interest_expense 2024-03-31), MTB(S035: capex 2023-12-31), UAL(S034: total_debt 2014-09-30, interest_expense 2019-09-30; `_resolved` debt is right), DXCM(S034: debt 2016, a wrong zero), CFG(S038: capex 2019-12-31), ED(S029: capex FY2022), JBL(S036: AR 2023-08-31), RJF(S036: dividends_paid 2023-06-30), ARES(S031: EPS 2020-03-31), WEC(S031: no 2026 EPS row; FY2025 4.81), O(S024).
- DATA-INFERRED: O(S024: total_debt_resolved 4,675M at 2017-03-31; balance sheet debt line not opened), MDB(S038: total_debt 2019-01-31), EXR(S036: total_debt_resolved 2018), TFC(S023: capex stops FY2022), IR/EXR/RJF/DG/JBL/WSM(S036: interest_expense last 2023-2024), DG(buybacks 2023).
- Cells: wrong or misleading values shown as the "latest" and counted as filled; dependants (margin, ROIC, coverage, debt ratios) blank with a reason about a different input. Total cells: not stated.
- Exemplars (FILING-CHECKED): MNST (EPS line is tagged `IncomeLossFromContinuingOperationsPerDilutedShare`; R4 shows 0.59 Q2 / 1.17 6M; core.fact `EarningsPerShareDiluted` stops 2011; 10-Q 0001104659-26-092193). HSY (EPS 2.26 common / 2.11 Class B filed; stored 0.64 at 2010-04-04). VRSN (Q2 2026 EPS 2.38 / 6M 4.71 filed; stored 6.24 at 2022-12-31; 10-Q 0001014473-26-000028).
- Mechanism: the filer changed tag or stopped presenting the line; coverage counts any value; S028 N3 / S030 STALE suggest comparing the latest period with the company's latest filing.
- Populations quoted: 34,290 of 295,966 filled lineage cells (4,906 companies) with latest period before 2025-07-01 (S027); 240 companies with `diluted_eps` latest before 2025-07-01, 46 before 2020 (S032).

### T6 true zero shown as blank; total_debt unmapped / wrong / stale
- True zero (no debt) shown as a blank or a stale old value:
  - FILING-CHECKED: VRTX(S010fc), MNST(S027), CMG(S030: explicit 0 at 2025-12-31 in 10-K, no debt line in 10-Qs), UI(S031), ZM(S037), OKTA(S034), CRDO(S034, face only), MPWR(S022).
  - DATA-INFERRED: TER(S025), VEEV(S025), ALAB(S026), GRMN(S024), NTRA(S023), RDDT(S036), WSM(S036: stale zeros 2015/2022), TW(S038), MDB(S038), RVMD(S030).
- total_debt unmapped, wrong or stale at a company WITH debt (FILING-CHECKED unless noted): VLO(S010fc: resolved 9,101M vs face 11,349M; raw 927M), BMY(S010fc: resolved 43,888M and raw 44,915M vs face 43,120M, cause unknown), MPC(raw 2,120M vs 32,816M), PGR, FTNT, LMT(raw one quarter stale), SPGI(raw 16,015M vs resolved 13,318M; Q2 face 15,170M), MPLX(S022: 1,502M stale vs 25,640M), F(S025: blank; only Company / Ford Credit dimensioned, 163,336M), PCAR(S022: blank, 14.7B in segment columns), DHI(S030: `NotesPayable` 7,112.6M unmapped), DXCM(S034: convertible 1,242.8M), CRWV(S034: Q2 35,068M vs Q1 stored 24,859M), VRSN(S037: 2,334.4M vs stale 0), WRB(S037: 2,840.3M blank), ILMN(S030: 1,991M), CLS(S032: 810.4M), AFL(S022: notes payable 8,729M, blank). DATA-INFERRED: DLR(S021 blank), AMP/AIG/MSCI(S028), ARES(S031), EXR(S036 component tags), NTRS(S035), ALNY(S035), EME(S034).
- Buyback/dividend zero shown blank is in T7 (reason) rather than here.
- Cells: debt_to_equity, zero_debt, net_cash, roic, piotroski, net_debt_ebitda, debt_to_ebitda, net_cash_per_share, total_debt_split: 8-14 cells per affected company (S025 TER/VEEV). Wrong values shown at companies with debt: VLO, BMY, MPLX, DXCM, VRSN.
- Exemplars (FILING-CHECKED): VRTX balance sheet 2025-12-31 and 2026-06-30 has no borrowings line while stored debt is 105.0M at 2011-09-30 (10-Q 0000875320-26-000259); VRSN; VLO current 927 + non-current 10,422 = 11,349M vs resolved 9,101M (10-Q 0001628280-26-050937).
- Mechanism: silence in later filings leaves an old non-zero value as "latest" or produces `missing:total_debt(2026)`; debt exists only under component/dimensioned tags (SeniorNotes, NotesPayable, recourse/non-recourse, Company / Ford Credit); "resolved" is not automatically the face sum (S010fc NEW-1: audit resolved totals against face rows).

### T7 wrong or missing blank reasons
- Sub-families and companies (reason defects; counts of cells mostly "not stated", NO REASON = unexplained):
  - a) `financial_institution_interest_income_not_revenue` on non-financials: NUE(S023), D(S023), APD(S020), PAYX(S029), COIN(S027, SIC 6199), RBLX(S031), DTE(S038), DOV(S038), MO(S010fc, tobacco), WTW(S036, insurance broker), MPLX(S022, pipeline MLP). On insurers the wording is wrong though the sector fits: PGR(S010fc, 12 cells), ALL/MET(S021), HIG/IBKR(S031), PRU(S029), AFL(S022, accepted). RKT(S035) suppresses a real revenue line.
  - b) `reit_net_interest_income_not_revenue` on equity REITs with ordinary statements: SPG(S020), DLR(S021), O(S024), PSA(S024), VTR(S028, wording), CCI(S032, filed "Total operating expenses" 538), IRM(S033, files "Cost of sales" 958,609K).
  - c) `pre_revenue_biotech_pharma` on revenue-generating companies: VRTX(S010fc), BMY(S010fc), TEVA(S026), ZTS(S033), BIIB(S032), RPRX(S032), ALNY(S035); mining variant `pre_revenue_mining_exploration` on NEM(S010fc, revenue 22,669M).
  - d) Non-dividend payers (and non-repurchasers) shown NO REASON or `missing:...` instead of "pays no dividend"; only `dividend_growth_streak_years` carries `no_dividend_history`: very widespread, e.g. VRTX, FTNT, NTRA, KEYS, AZO, VEEV, EW, ALAB, ADSK, TEVA, MSTR, WDAY, CIEN, XYZ, MNST, COIN, COHR, IDXX, CVNA, WAT, IQV, ILMN, TTWO, CBRE, CMG, RVMD, TWLO, RBLX, MTD, BIIB, CLS, ON, ZM, MDB, CNC, ZS, FLEX, OKTA, DXCM, CRDO, AXON, UAL, CRWV, ALNY, RKLB, MDLN, TDY, RDDT, P, LYV, BSX, BE, TEAM. Wording gone wrong: `no_dividend_history` at actual payers ET(S020), DLR(S021, 435,908K Q2 common), HSY(S032), EBAY(S024); `zero_base_value` at TEVA, CRWV, FDX, CRH, CNP.
  - e) Bank/insurer/REIT/utility template cells (current_assets, current_liabilities, current_ratio, quick_ratio, working_capital, inventory_days, payables_days, cf_*_change, reconciliation gaps, sga_expense, total_debt_split) NO REASON: TFC, MET, ALL, AFL, HUM, PRU, ACGL, WRB, AMP, AIG, VTR, ARES, HIG, O, PSA, DLR, SPG, APO, MTB, HBAN, NTRS, CFG, RKT, RJF, EXR, STT, FITB, TW, PGR, plus utilities and software (inventory cells, sga_expense). EBITDA reasons for banks read `missing:4_consecutive_quarters` (MTB, CFG) instead of not applicable.
  - f) Operating income NR-F (no subtotal on the face) with NO REASON: NUE, MTD(S031), NKE(S024), ADM(S029), PCAR(S022), IMO(S020), AJG(S020), OXY(S021), AMP(S028), AIG(S028), DHI(S030), BIIB(S032), ZTS(S033, wrong reason), BKR(S024).
  - g) `line_not_presented_in_filing` where the line IS presented, or `line_in_filing_not_extracted` where it is not: UAL operating_expenses (R2 "Total operating expense" 16,576), CCL accounts_receivable (R4 "Trade and other receivables, net" 670), ADM interest_income, EW operating_expenses (SNR), BKR accounts_receivable (DATA-INFERRED), WAT operating_expenses (R4 "Total costs and operating expenses" 1,731), OTIS cost_of_revenue (not on face).
  - h) History-limit reasons that read like lost data: `missing:prior_period(2016_Q2)` for IPO/spin-off names (KVUE, RBLX, TWLO, TW, RPRX named 2019/2017/2015 pre-IPO periods), `piotroski missing:total_assets(2025)` when 2025 total assets are stored (HIG), WEC fcf reason naming a stale input.
  - i) The 4 universal unexplained cells (`bdc_total_investment_income`, `collaborative_arrangement_revenue`, `net_lease_revenue`, `employee_count`) NO REASON at essentially every company in the block (about 40 per shard, 8 of 10 for net_lease_revenue at S021). All workers mark them SNR; `employee_count` is a text fact, not XBRL.
- Cells: blank cells with a false or absent reason. Counts: see per-company line (unexplained counts where the file gives them); block-level sum not stated.
- Exemplars (FILING-CHECKED): NUE R2 shows net sales then "Earnings before income taxes" 1,625, no operating income, yet carries the financial-institution reason (10-Q 0001193125-26-345891); ZTS revenue 2,468M Q2 labelled `pre_revenue_biotech_pharma` (10-Q 0001555280-26-000040); DLR distributions 435,908K Q2 vs `no_dividend_history` (10-Q 0001104659-26-089296).
- Mechanism guess: S023: the trigger "appears to be that the company also files `InterestAndDividendIncomeOperating`" (inferred, not read from coverage code); pre-revenue reason "looks SIC-driven" (S033), should key on revenue; sector template reason layer not applied to insurers, REITs, MLPs.
- Populations quoted: 328 carry the financial-institution reason, 186 SIC 6000-6799, 142 not (S023); 495 carry `pre_revenue_biotech_pharma`, 366 with stored revenue (S026), 29 above 500M latest revenue, 65 above 100M (S032); 3,433 `no_dividend_history`, 502 of them with a dividends_paid value, 3,242 with DPS blank and no reason (S021).

### T8 negative or meaningless ratios shown as numbers
- Companies affected.
  - Negative trailing_pe shown: APD -1,429.43(S020), BE -5,546.82(S021), NTRA -302.27(S023), TEAM -1050(S024), F -7.81(S025), MSTR -1.5167(S026), LYV -154.71(S029), COIN -44.98(S027), TTWO -119.27(S030), RVMD -22.03(S030), CNC -6.81(S033), ZS -552.44(S033), CRWV -18.99(S034), RKLB -189.67(S035), RBLX -36.72(S031), KHC -8.35(S037), MDB -1006.95(S038). IAU(S022) 805.96 on a gold trust.
  - Negative equity P/B, ROE, D/E shown: TDG(S021: P/B -6.44, ROE -21.7%, D/E -3.34), CAH -20.52(S022), AZO -18.50 and ROE -0.89, D/E -3.25(S025), CCI -10.64(S032), HPQ -197.99(S037), VRSN -12.28(S037), HONA -8.84(S024), MO(S010fc: D/E -9.21, P/B -46.6, ROE -298.8%), OTIS(S038: D/E -1.47, ROIC 92.9%).
  - Meaningless large positives: FTNT ROIC -222.6%, ROE 136.7%, P/B 80.8(S010fc: invested capital -886.9M); MTD P/B 2,760.7(S031: equity 12.8M); RBLX P/B 245; ALL fcf_yield 19.4%(S021, insurer); ZM P/E 9.0 (S037, about 1.7B non-operating gain); TWLO P/E 36.1 on a roughly 990M tax benefit(S031); WAT P/E 111.55 across a business combination(S028); BDX P/E 58.4 with discontinued-ops loss(S024); MLM P/E 12.6 / net margin 36.7% with discontinued-ops gain(S036); ROP margins with about 720M gain(S030).
- Evidence: the equity or loss itself FILING-CHECKED in every case; the displayed metric is DATA-INFERRED arithmetic.
- Cells: wrong-or-not-meaningful values shown, one to three per company.
- Exemplars: APD 9M net loss -52.2M with trailing_pe -1,429.43; MO equity attributable -2,668M (10-Q 0000764180-26-000094); FTNT 496.9 + 1,551.1 - 2,934.9 = -886.9M invested capital.
- Mechanism: `trailing_pe` has no `non_positive` guard (peg_ratio already has `non_positive_growth_not_meaningful`); P/B, D/E, ROE, ROIC have none for non-positive equity or invested capital.
- Populations quoted: 1,634 of 4,287 stored trailing_pe values negative; 450 negative price_to_book (S025, query).

### T9 fiscal_year / period label wrong
- Companies affected: NUE(S023, FILING-CHECKED vs SEC companyfacts), TEL(S022, DATA-INFERRED by date arithmetic), FERG(S027, FILING-CHECKED), KR(S030, FILING-CHECKED vs companyfacts), CAH(S022 cover label), UI(S031 cover label). Suspected not verified: DG, WSM(S036), VEEV(S025), ROK(S026 Sep year-end pairing), IQV n/a.
- Cells: wrong labels on every affected period; consequence is blanks (`missing:prior_period(...)`, `missing:revenue_ttm`), 15-25+ cells per company (TEL "20+ growth cells" plus trailing_pe, dividend_yield, ev_sales, price_to_sales; NUE 17 derivation cells; FERG 15+ TTM/CAGR cells; KR 8 price/FCF cells).
- Exemplars (FILING-CHECKED):
  - NUE: all 2026 periods stored as fiscal_year 2027; SEC companyfacts says fy=2026, fp=Q1/Q2 for 0001193125-26-220778 and 0001193125-26-345891 (52/53-week period ending 2026-07-04; probable year-end Jan 2, 2027).
  - FERG: Jan-Mar 2026 stored FY2026 Q3 and Apr-Jun FY2026 Q4; companyfacts says fy=2026 fp=Q1 / Q2. Ferguson moved year-end from Jul 31 to Dec 31; 10-KT 0002011641-26-000006 (revenue 12,833M, NI 786M) absent from core.filing; zero `10-KT`/`10-KT/A` rows in core.filing for any company.
  - KR: 16-week Q1 (111 days) and its YTD periods have NULL fiscal_period, so trailing_pe, price_to_sales, ev_sales, fcf_yield, ebitda_margin, buyback_yield, dividend_yield, share_repurchases_pct_fcf (8 cells) are blank while net_margin TTM (0.73%) IS computed; separately KR FY ending 2026-01-31 is labelled 2026 where SEC says fy=2025.
  - TEL (DATA-INFERRED): Mar-Jun 2025 quarter labelled FY2025 Q1 and Jun-Sep 2025 labelled FY2025 Q2 (same for FY2024); the late-September year end makes those Q3 and Q4.
- Mechanism: Scrooner assigns the label from end date / old fiscal calendar instead of the filer's own `fy`/`fp`; 16-week quarters get NULL fiscal_period; transition filings not collected.
- Populations quoted: 224 companies / 322 duplicate-label groups since 2024-01-01 (S022, query); 11 companies with a 105-125 day revenue period ending 2026 and NULL fiscal_period (S030, one count).

### T10 recast / restated / spun-off / predecessor comparatives: no authoritative fact or mixed bases; missing quarters in last 8
- Companies affected.
  - FILING-CHECKED value conflict, none authoritative: ZTS(S033: FY2025 assets 15,467 / 15,490 / 15,490 and equity 3,331 / 3,415 all `is_authoritative=false`; fiscal-year alignment recast, Note 2), MLM(S036: Q2-2025 revenue 1,811M original vs 1,609M recast, all three rows non-authoritative; Q1-2025 also no canonical row).
  - Corporate-action discontinuities: HONA(S024: spin-off carve-out, no 10-K, no history, no per-share line), HON(S020: share halving, prior-period comparatives restated, `missing:prior_period(2025_Q2)`), WAT(S028: assets 5,077M to 24,751M, shares 59.7M to 98.2M), DVN(S023: merger, assets 31,599 to 70,893, shares 622M to 1,150M), FITB(S027: assets 214,376M to 300,180M, shares 674M to 916M), HBAN(S035: assets 225,106 to 283,984), KDP(S026: assets 55,459 to 87,619, revenue 4,163 to 7,309, real), CVNA(S028: diluted shares 224M to 740M), BDX(S024: Biosciences spin-off, 9M EPS 1.59 vs 2.58 continuing), KMB(S032: discontinued-ops reclass; AR, AP, inventory series stop FY2023/2024), CCI(S032: fiber sale moved to discontinued, revenue basis broke), MLM(S036: ~1.5B discontinued gain in TTM).
  - Predecessor/history under another identity (SNR, not opened): LHX(Harris CIK), AON, TRGP(MLP era), APO, CRH(US filer 2023), CARR(spun 2020), IMO(earlier tags), KVUE, GEHC (history limits).
- Cells: not stated as a count; consequence is blank growth/TTM cells or mixed-basis TTM values (HON Q1 EPS on the old share base; WAT, BDX, MLM P/E).
- Mechanism: conflict resolver finds several non-authoritative values for the same period end and picks none (S033 Q-recast); S036 ties it to the "restatement basis" rule.

### T11 net income basis inconsistent (ProfitLoss / consolidated vs attributable to parent); equity incl. NCI
- Companies affected, FILING-CHECKED: SPG(S020: `ProfitLoss` 574.1M Q2 / 1,142.7M 6M vs attributable 483.1M / 962.7M; EPS 1.49 on attributable; net margin and ROE about 19% high), OXY(S021: 2,996M / 6,355M vs attributable to common 2,807M / 5,982M, preferred dividends 170/340 and NCI 19/33 between), BSX(S021: 905 vs 907), MPLX(S022: 1,087 vs 1,077), F(S025: 2,551 vs 2,548), IRM(S033: 106,102K vs 101,430K; 6M 255,101K vs 245,095K), O(S024: 370,513K incl NCI vs 343,955K common; EPS and ROE on common), MDLN(S035: 6M stored 197M matches neither consolidated 378 nor attributable 189), MCHP(S029: 229.8M before preferred vs 202.0M to common; EPS on common), LHX(S027: 600M vs 586M, small).
- Equity basis: ET(S020: `...IncludingPortionAttributableToNoncontrollingInterest` 49,737M at Q1; Q2 facts under partners' capital tags unmapped), TKO(S033: parent equity 3,395,932K stored vs 8,330,896K incl NCI, NCI 60%), LNG(S022: parent 6,191 vs 11,490 incl NCI, defensible), IBKR(S031: NCI holds 77% of earnings).
- Cells: wrong or mixed-basis net_margin, ROE, P/E inputs, payout_ratio, usually a few percent (OXY ~6%, SPG ~19%). Number of cells: not stated.
- Mechanism: concept picks `ProfitLoss` where it exists; no single "attributable to common" rule; S025 and S027 call for one policy line in the Standardization decision.

### T12 capex (and D&A, interest expense, receivables) tags unmapped, stale or split, causing FCF/EBITDA cascades
- Capex missing, stale or split: VLO(S010fc, FILING-CHECKED: FY2025 719 + 71 + 6 plus turnaround 990 + 99; turnaround ruling needed), FANG(S023: `PaymentsToExploreAndDevelopOilAndGasProperties` 1,929 6M, 12 FCF cells), DAL(S025: flight equipment + ground property = 4,071M 9M), AJG(S020: line exists 87/68), URI(S020), TFC(S023, DATA-INFERRED), D(S023), ED(S029: "Utility capital expenditures" (4,764) FY2025), DLR(S021: "Improvements to investments in real estate" 1,784M), O/PSA(S024), VTR(S028), TWLO(S031: `PaymentsToDevelopSoftware` + `PaymentsToAcquireOtherProductiveAssets`), IBKR(S031), HIG(S031: net disposals +84, stored -84/-115/+31, sign flips), MTB(S035), SUNB(S035), TKO(S033), DTE(S038), CFG(S038), CBOE(S034: Q1 `PaymentsToAcquirePropertyPlantAndEquipment` vs 6M `PaymentsToAcquireProductiveAssets`, Q2 never derived), VEEV(S025, DATA-INFERRED), WEC(S031 annual cell), ARES(S031). No capex line on the face (legitimately NR-F, reason wrong or absent): COIN, AIG, MET, RPRX, APO, PRU.
- D&A unmapped or two-line: NUE(S023), FAST(S022), AJG(S020: Depreciation 57 + Amortization 301), CIEN(S027), CCI(S032: "Depreciation, amortization and accretion 171"), MPLX(S022: 365), OTIS(S038: 83), NTRS(S035), MTD(S031), CFG(S038: `DepreciationAmortizationAndAccretionNet` 212M), WAT(S028), GRMN(S024), BE(S021), PCG(S032), RPRX(S032).
- Interest expense unmapped or stale: ILMN(S030: now `InterestExpenseNonoperating` 24/47), OXY(S021: "Interest and debt expense, net" 108/540), TDG(S021), CIEN(S027: `InterestExpenseNonoperating` 5,803K filed, 24 facts), D(S023: 555 Q2), HON, COR, URI, BKR, NKE (net line), AXON, GEHC, FERG, ODFL(76/375), MO, VRTX(stale 2020; 13.3M FY2025), NEM(stale 2013; 229 FY2025), IR/EXR/RJF/DG/JBL/WSM/TDY(S036), CLS, UI(combined line), LHX/JBL/DG/WSM(net-only presentations).
- Receivables unmapped or wrong: VLO(S010fc: stored 9,207M vs face "Receivables, net" 9,877M and 13,928M at 2026-06-30; wrong AND stale), LMT, MO, ROK, AME, NDAQ, IQV, BSX, WSM, JBL (stale 3,647M vs face 5,473M), DAL(R2 4,325), HAL(5,325), UAL(2,473), GEHC(3,881), FTI, YUM, SYY, CCL, DHI, FDX, CRH, KMB(1,858), TW.
- Cells: blank; cascades per company: capex gap removes 8-15 FCF-family cells (FANG 12, DLR about 11, O/PSA 13-14, TKO 11, DAL 8, URI 9, ED 9, TWLO about 8); EBITDA gap removes ebitda plus 4-5 ratios; AR gap removes debtor_days, cash_conversion_cycle and 2 reconciliation cells. Wrong values shown: VLO AR 9,207M, HIG capex sign, VLO/NEM/VRTX stale interest.
- Exemplars (FILING-CHECKED): FANG cash flow R5 (10-Q 0001539838-26-000142); DAL R5 (10-Q 0000027904-26-000038); VLO (10-Q 0001628280-26-050937).
- Mechanism: tag moved after a filing year or is a custom/dimensioned label; capex is a combined-line / perimeter question (acquisitions vs maintenance, rental equipment, turnaround) needing a Tag/Standardization ruling.
- Populations quoted: `InterestExpenseNonoperating` candidate in 2,017 active companies / 35,998 facts; `ReceivablesNetCurrent` 739; `AccountsAndOtherReceivablesNetCurrent` 508; `InterestIncomeExpenseNonoperatingNet` 1,048 (S036, sec_tag_library).

### T13 partnership / MLP / LP tags unmapped (equity, distributions, per-unit EPS)
- Companies: ET(S020), MPLX(S022), CQP(S035); all FILING-CHECKED lines, tag-level DATA-INFERRED.
- Cells: ET about 10 dividend cells plus ROE/ROIC/D/E/book value; MPLX equity, ROE, ROIC, D/E, BVPS, basic EPS, DPS blank (18 unexplained); CQP equity, ROE, D/E, P/B, distributions blank. Wrong reason: ET `no_dividend_history`.
- Exemplars: CQP `PartnersCapital` = 754,000,000 sits in core.fact at 2026-06-30 (R3 Total partners' equity 754; 10-Q 0001383650-26-000028); MPLX "Total MPLX LP partners' capital" 14,027 (10-Q 0001552000-26-000038); ET `DistributionMadeToLimitedPartnerCashDistributionsPaid` filed 3 periods, unmapped (10-Q 0001276187-26-000038).
- Mechanism: `StockholdersEquity` / dividend tags only; `PartnersCapital*` and `DistributionMadeToLimitedPartner*` not mapped. Reach to other MLPs (EPD, WES, PAA) suggested, not counted.

### T14 per-share series (EPS, DPS) tagged per class or under a different tag, so the annual series dies; dividend payers' TTM DPS cannot form
- Companies: EPS/DPS dimensioned or changed tag: HSY(S032), BKR(S024), CVNA(S028), WEC(S031), ARES(S031), MNST(S027), VRSN(S037). Dividend payers with blank dividend_yield / DPS TTM (`missing:dividends_per_share_ttm`): AME(S023), CARR(S027), ZTS(S033), AMP(S028), EBAY(S024), GRMN(S024), BDX(S024), BKR(S024), ATO/HAL/HPQ(S037), WST(S038), DAL(S025), IR(S036), PCG/CCL(S032, partly legitimate resumption), FERG(S027), NKE n/a, CRH(S023), IBKR(S031, 0.0875/share), NTAP(payout_ratio only).
- Cells: stale or blank EPS drives trailing_pe, PEG, growth cells (HSY and MNST growth cells name 2000s periods). Counts: not stated.
- Mechanism: undimensioned fact exists only until the filer splits by class; YTD-only DPS/dividend tags (AME: "filed only as a year-to-date figure").

### T15 YTD-only cash-flow items break TTM (CFO, capex, D&A, dividends, buybacks)
- Companies: very widespread; named instances: NXPI, KEYS (S023), AZO(S025, 36-week CFO), APD(S020), IQV(S028), HPQ(S037), ROP(S030), COIN(S027: buybacks 1,243,488K 6M), FERG(S027), MSCI(S028), NKE(S024), ALNY(S035), WAT(S028), XEL/KDP/WDAY(S026), DTE(S038). `missing:4_consecutive_quarters` EBITDA chain (ebitda + debt_to_ebitda, ebitda_margin, ev_ebitda, net_debt_ebitda, net_debt_ebitda) appears in most shards.
- Cells: 5-6 EBITDA cells plus fcf_yield, fcf_per_share, dividends_pct_fcf, share_repurchases_pct_fcf per company. Evidence DATA-INFERRED except where the YTD figure was read (AZO 2,119,587K; ROP capex 25.3M exists).
- Mechanism: standalone quarters cannot be derived when only YTD is filed or when the same line changes tag between quarters (CBOE, S034 N2).

### T16 institutional_ownership_pct hidden by `implausible:institutional_shares_exceed_shares_outstanding`
- Companies: HON, SPG(S020), NKE(S024), MSTR(S026), NTAP(S029), ILMN, ROP(S030), CNC, EXPE, ZTS(S033), CTSH(S034), CCI(S032), IR(S036), ON(S037), WST, CNP(S038), IBKR(S031: stale 2015 shares). All DATA-INFERRED; none investigated. Guard works; root cause is a wrong share base (HON, MSTR, IBKR) or 13F double counting (NTAP, ZTS). TW and CVNA instead get `zero_denominator`.
- Cells: one per company (17+).

### T17 reporting currency not carried
- IMO(S020, FILING-CHECKED statements in CAD): trailing_pe 15.67, price_to_book 2.65, market cap 64.9B divide a USD price by CAD EPS and equity; whether the price is USD is DATA-INFERRED. Population: not counted (S018 excluded CNI for a related reason).

### T18 gross margin / cost of revenue built on a partial or minor line
- FILING-CHECKED: MPC(S010fc: "Cost of revenues (excludes items below)" 43,064, gross margin 17.2%), BMY (cost of products sold excludes amortization 3,317), NEM ("Costs applicable to sales" excludes D&A), CNP(S038: `CostOfGoodsAndServicesSold` 1M is only "Non-utility cost of revenues", gross profit 2,974M on revenue 2,975M = 99.96% while the same cell's reason says gross profit not presented).
- Mechanism: no gross-profit line exists; margin presented anyway. Sanity gate suggested: gross_margin above 95% (S038) and operating margin above about 70% on a non-royalty company (S020).

### T19 face line exists but concept blank (mapping gap), ranked above SNR cells by S010fc (NEW-3)
- FILING-CHECKED lines with blank concept: operating_expenses / total costs and expenses (MPC, VRTX, UAL, MSCI, WAT, HPQ, CMG, ODFL, AON, CNC), gross_profit derivable (VRTX, TKO direct operating costs 556,123K), other_income_expense_net (LMT 183/45, BMY 674, APD, APO, COIN, TEL, CT), income_before_tax (PYPL 1,310 Q2, CVNA 579, DOV 387,698K, FLEX 377, ON, ALL 4,142), basic_eps (MPLX 1.06), inventory (NEM 1,478M, DHI 26,686.9M, DAL 2,637, MPLX 200, EME 153,679, NEM leach pads), accounts_payable (DHI 1,388.4M tag `AccountsPayableCurrentAndNoncurrent`), interest income (ODFL, CTSH 18M, STT 5,494M), dividends and repurchases (RPRX "Dividends to shareholders" (209,406) and repurchases (94,743); RJF 326M YTD; RBLX repurchases 323.0M; CRH, ZTS 447M, AMP 300).
- Cells: blank mapping gaps; counts per company in each file.

---

## Per-company verdicts

Format: TICKER | shard | rank-or-mcap (shard band) | wrong values | unexplained blanks | CLEAN or NOT CLEAN. No file has a verdict table, so all are DERIVED. Rule used: CLEAN only if the file reports no wrong value and no more than the 4 universal unexplained cells; "(borderline)" = no wrong value found but more unexplained or mapping-gap blanks. "unexpl" = unexplained (NO REASON); "blank" = total blank cells when unexplained is not stated. Band shown in header only where the file gives one.

### S010 rerun (band 123.6-133.4B)
- MPC | S010fc | band | total_debt raw 2,120M vs 32,816M; ppe_net 2021; partial gross margin | blank 11 | NOT CLEAN
- VLO | S010fc | band | capex stale, debt 9,101M vs 11,349M, AR 9,207M vs 9,877M | blank 16 | NOT CLEAN
- LMT | S010fc | band | raw total_debt one quarter stale | blank 14 | NOT CLEAN
- VRTX | S010fc | band | debt 2011 at debt-free company; 3 wrong reasons | blank 22 | NOT CLEAN
- PGR | S010fc | band | raw debt 2016; dividend yield 6.27% inflated; 12 wrong reasons | blank 51 | NOT CLEAN
- SPGI | S010fc | band | whole Q2 missing; shares 296M rounded; debt | blank 17 | NOT CLEAN
- MO | S010fc | band | negative-equity ratios; 1 wrong reason | blank 15 | NOT CLEAN
- NEM | S010fc | band | stale inventory/interest; mining reason on 22.7B revenue; 5 wrong reasons | blank 24 | NOT CLEAN
- FTNT | S010fc | band | ROIC -222.6%; stale debt 2021; proxy-sourced NI provenance | blank 16 | NOT CLEAN
- BMY | S010fc | band | debt 43,888M/44,915M vs 43,120M; op income 2012 stale | blank 20 | NOT CLEAN

### S020
- ET | S020 | n/a | equity stale Q1 and incl. NCI; P/B on wrong basis; distributions unmapped | unexpl 14 of 45 | NOT CLEAN
- FDX | S020 | n/a | none (full FY2026 matches) | unexpl 12 of 25 | NOT CLEAN (borderline)
- HON | S020 | n/a | shares halved, Q1 EPS not restated | unexpl 9 of 18 | NOT CLEAN
- APD | S020 | n/a | trailing_pe -1,429.43; wrong financial reason | unexpl 7 of 15 | NOT CLEAN
- SPG | S020 | n/a | net_income ProfitLoss; wrong REIT reason | unexpl 30 of 60 | NOT CLEAN
- APO | S020 | n/a | operating income = revenue minus total expenses | unexpl 31 of 62 | NOT CLEAN
- AJG | S020 | n/a | operating income 83% margin | unexpl 12 of 37 | NOT CLEAN
- COR | S020 | n/a | none found | unexpl 8 of 12 | NOT CLEAN (borderline)
- IMO | S020 | n/a | CAD vs USD; revenue incl other income | unexpl 12 of 35 | NOT CLEAN
- URI | S020 | n/a | Q2 missing; Q1 revenue 929M vs 3,985M | unexpl 7 of 23 | NOT CLEAN

### S021 (band 61.2-66.1B)
- BSX | S021 | band | net_income ProfitLoss (905 vs 907) | blank 28 | NOT CLEAN
- MET | S021 | band | revenue 724M vs 19,154M; op income non-face | blank 60 | NOT CLEAN
- TDG | S021 | band | negative-equity ratios; equity -9,809 vs -9,800 | blank 18 | NOT CLEAN
- GWW | S021 | band | none found | blank 16 (total_liabilities NO REASON) | NOT CLEAN (borderline)
- ALL | S021 | band | fcf_yield 19.4% insurer; wrong reason | blank 59 | NOT CLEAN
- BE | S021 | band 63.1B | Q2 missing; trailing_pe -5,546.82 | blank 45 | NOT CLEAN
- OXY | S021 | band | revenue, NI basis, stale op income | blank 42 | NOT CLEAN
- AON | S021 | band | none found | blank 41 | NOT CLEAN (borderline)
- TRGP | S021 | band 62.6B | none found | blank 21 | NOT CLEAN (borderline)
- DLR | S021 | band 61.2B | Q2 missing; wrong REIT reason; false no_dividend_history | blank 72 | NOT CLEAN

### S022
- TEL | S022 | n/a | fiscal labels duplicated | blank 38, unexpl 5 | NOT CLEAN
- AFL | S022 | n/a | op income 70.9% margin; debt blank | unexpl 28 | NOT CLEAN
- LNG | S022 | n/a | revenue 5,677 vs 5,732; 6M 663 high | unexpl 9 | NOT CLEAN
- MPWR | S022 | n/a | none (true-zero debt shown blank) | unexpl 11 | NOT CLEAN (borderline)
- CAH | S022 | n/a | Q3 FY26 missing; P/B -20.52 | blank 41 | NOT CLEAN
- OKE | S022 | n/a | none found | blank 32 | NOT CLEAN (borderline)
- MPLX | S022 | n/a | revenue 2,615 vs 3,312; debt; NI basis; equity | unexpl 18 of 49 | NOT CLEAN
- FAST | S022 | n/a | op income lagged one day | blank 22 | NOT CLEAN (borderline)
- PCAR | S022 | n/a | none (debt in segment columns blank) | blank 49 | NOT CLEAN (borderline)
- IAU | S022 | excluded gold trust | trailing_pe 805.96 | unexpl 67 of 163 | excluded (NOT CLEAN)

### S023
- NXPI | S023 | n/a | Q2 missing | blank 24, unexpl 8 | NOT CLEAN
- NUE | S023 | n/a | fiscal_year 2027 label; wrong reason | blank 38, unexpl 6 | NOT CLEAN
- TFC | S023 | n/a | none found | blank 63, unexpl 23 | NOT CLEAN (borderline)
- FANG | S023 | n/a | none found (capex unmapped) | blank 46, unexpl 14 | NOT CLEAN (borderline)
- AME | S023 | n/a | none found | blank 24, unexpl 11 | NOT CLEAN (borderline)
- NTRA | S023 | n/a | trailing_pe -302.27 | blank 36, unexpl 14 | NOT CLEAN
- KEYS | S023 | n/a | none found | blank 28, unexpl 10 | NOT CLEAN (borderline)
- D | S023 | n/a | Q2 missing; wrong reason | blank 47, unexpl 9 | NOT CLEAN
- DVN | S023 | 55.39B | revenue, op income, shares | blank 27, unexpl 9 | NOT CLEAN
- CRH | S023 | n/a | none found | blank 30, unexpl 6 | NOT CLEAN (borderline)

### S024
- BKR | S024 | n/a | EPS and op income stale 2024 | blank 32 | NOT CLEAN
- NKE | S024 | 56.36B | shares 2015, market cap about 40% low | blank 31 | NOT CLEAN
- GRMN | S024 | n/a | Q2 missing | blank 31 | NOT CLEAN
- EBAY | S024 | n/a | none (no_dividend_history wrong at a payer) | blank 24 | NOT CLEAN (borderline)
- HONA | S024 | n/a | op income 995M vs none; P/B -8.84 | blank 85 | NOT CLEAN
- O | S024 | n/a | debt 2017; NI incl NCI | blank 63 | NOT CLEAN
- TEAM | S024 | n/a | trailing_pe -1050; shares blank | blank 43 | NOT CLEAN
- NDAQ | S024 | n/a | none found | blank 24 | NOT CLEAN (borderline)
- PSA | S024 | n/a | none (capex unmapped, wrong REIT reason) | blank 53 | NOT CLEAN (borderline)
- BDX | S024 | n/a | trailing_pe 58.4 incl disc-ops loss | blank 24 | NOT CLEAN

### S025 (band 49-52B)
- AZO | S025 | band | P/B -18.50, ROE -0.89, D/E -3.25 | blank 28 | NOT CLEAN
- VST | S025 | band | revenue 4,401 vs 4,017 | blank 33 | NOT CLEAN
- F | S025 | band | Q2 missing; debt blank; PE -7.81; NI total basis | blank 29 | NOT CLEAN
- TER | S025 | band | none (true-zero debt blank) | blank 20 | NOT CLEAN (borderline)
- FIX | S025 | band | none found | blank 20 | NOT CLEAN (borderline)
- VEEV | S025 | band | none (true-zero debt, capex stops) | blank 47 | NOT CLEAN (borderline)
- EW | S025 | band | none | blank 29 | NOT CLEAN (borderline)
- HUM | S025 | band | Q2 missing | blank 40 | NOT CLEAN
- PYPL | S025 | band | Q2 missing | blank 37 | NOT CLEAN
- DAL | S025 | band | capex split, FCF cascade | blank 40 | NOT CLEAN

### S026 (band 46.8-51.1B)
- ALAB | S026 | band | none | unexpl 17 | NOT CLEAN (borderline)
- ADSK | S026 | band | none | unexpl 14 | NOT CLEAN (borderline)
- A | S026 | band | none | unexpl 5 | NOT CLEAN (borderline)
- WAB | S026 | band | none found | unexpl 4 (universal only) | CLEAN (DERIVED)
- TEVA | S026 | band | wrong `pre_revenue_biotech_pharma` reason | unexpl 8 | NOT CLEAN
- MSTR | S026 | band | trailing_pe -1.5167; shares blank | unexpl 18 | NOT CLEAN
- XEL | S026 | band | none | unexpl 9 | NOT CLEAN (borderline)
- ROK | S026 | band | none | unexpl 7 | NOT CLEAN (borderline)
- KDP | S026 | band | none (acquisition jump is real) | unexpl 4 | CLEAN (DERIVED)
- WDAY | S026 | band | shares missing since 2025-06 | unexpl 12 | NOT CLEAN

### S027 (band 44-49B)
- CIEN | S027 | band | interest expense unmapped (no wrong value) | unexpl 15 of 30 | NOT CLEAN (borderline)
- STT | S027 | band | none | unexpl 22 of 52 | NOT CLEAN (borderline)
- XYZ | S027 | 46.99B | shares blank | unexpl 19 of 35 | NOT CLEAN
- LHX | S027 | band | none (NI 600M vs 586M noted) | unexpl 3 of 13 | CLEAN (DERIVED)
- FITB | S027 | band | revenue 3,372M vs 3,274M | unexpl 22 of 55 | NOT CLEAN
- CARR | S027 | band | Q2 missing | unexpl 8 of 36 | NOT CLEAN
- COIN | S027 | band | trailing_pe -44.98; capex stale | unexpl 15 of 52 | NOT CLEAN
- COHR | S027 | band | op income stale 2024 | unexpl 11 of 39 | NOT CLEAN
- FERG | S027 | band | fiscal labels, 10-KT absent | unexpl 11 of 55 | NOT CLEAN
- MNST | S027 | band | EPS 2011, debt 2025 stale | unexpl 15 of 36 | NOT CLEAN

### S028 (band 42.4-44.7B)
- IQV | S028 | band | Q2 missing | unexpl 12 of 37 | NOT CLEAN
- EXC | S028 | band | Q2 missing | unexpl 11 of 40 | NOT CLEAN
- AMP | S028 | band | revenue gross 5,013 vs 4,940; dividends | unexpl 26 of 58 | NOT CLEAN
- IDXX | S028 | band | none | unexpl 10 of 20 | NOT CLEAN (borderline)
- VTR | S028 | band | op income 2011 stale; capex FY2025 only | unexpl 25 of 65 | NOT CLEAN
- CVNA | S028 | 44.63B | EPS quarters missing; shares 0 from 2017 | unexpl 17 of 55 | NOT CLEAN
- WAT | S028 | band | P/E 111.55 across combination | unexpl 14 of 47 | NOT CLEAN
- WCN | S028 | band | none | unexpl 7 of 21 | NOT CLEAN (borderline)
- AIG | S028 | band | capex FY2023 stale | unexpl 24 of 65 | NOT CLEAN
- MSCI | S028 | band | none found | unexpl 6 of 27 | NOT CLEAN (borderline)

### S029 (no band stated)
- ED | S029 | n/a | Q2 missing; capex 2022 | unexpl 8 of 45 | NOT CLEAN
- P | S029 | n/a | none | unexpl 11 of 30 | NOT CLEAN (borderline)
- YUM | S029 | n/a | none | unexpl 8 of 22 | NOT CLEAN (borderline)
- LYV | S029 | n/a | trailing_pe -154.71 | unexpl 19 of 42 | NOT CLEAN
- MCHP | S029 | n/a | NI basis vs EPS (low severity) | unexpl 8 of 18 | NOT CLEAN
- PRU | S029 | n/a | wrong insurer reason | unexpl 26 of 63 | NOT CLEAN
- ADM | S029 | n/a | revenue 24,956M vs 80,269M; Q4 2024 -25,710M | unexpl 7 of 25 | NOT CLEAN
- NTAP | S029 | n/a | none (institutional guard fired) | unexpl 4 of 10 | CLEAN (DERIVED)
- PAYX | S029 | n/a | revenue 1,580.7 vs 1,630.5; false reason | unexpl 8 of 21 | NOT CLEAN
- SYY | S029 | n/a | none | unexpl 8 of 24 | NOT CLEAN (borderline)

### S030 (no band stated)
- ILMN | S030 | n/a | debt 2018/2022, interest 2024 stale | unexpl 11 of 35 | NOT CLEAN
- ODFL | S030 | n/a | none | unexpl 15 of 38 | NOT CLEAN (borderline)
- DHI | S030 | n/a | none (debt, AP, inventory unmapped) | unexpl 24 of 53 | NOT CLEAN (borderline)
- CBRE | S030 | n/a | none | unexpl 14 of 34 | NOT CLEAN (borderline)
- TTWO | S030 | n/a | trailing_pe -119.27 | unexpl 12 of 30 | NOT CLEAN
- EL | S030 | 38.26B | shares blank | unexpl 9 of 26 | NOT CLEAN
- CMG | S030 | n/a | debt-free shown blank | unexpl 18 of 45 | NOT CLEAN
- ROP | S030 | n/a | none (margins distorted by gain) | unexpl 6 of 32 | NOT CLEAN (borderline)
- RVMD | S030 | n/a | trailing_pe -22.03 | unexpl 14 of 57 | NOT CLEAN
- KR | S030 | n/a | NULL fiscal_period blanks 8 price cells; label convention | unexpl 9 of 39 | NOT CLEAN

### S031 (no band stated)
- TWLO | S031 | n/a | capex blank; P/E on tax benefit | blank 22 | NOT CLEAN
- IBKR | S031 | 37.1B | revenue 760 vs 1,896; market cap Class A only | blank 52 | NOT CLEAN
- HIG | S031 | n/a | revenue 111M vs 7,263M; capex sign | blank 35 | NOT CLEAN
- ARES | S031 | n/a | EPS 2020 stale; derived op income | blank 74 | NOT CLEAN
- UI | S031 | n/a | zero debt shown blank | blank 19 | NOT CLEAN
- KVUE | S031 | n/a | none (history-limit wording) | blank 21 | NOT CLEAN (borderline)
- PEG | S031 | n/a | none (blanks SNR) | blank 53 | NOT CLEAN (borderline)
- WEC | S031 | n/a | no 2026 EPS row | blank 31 | NOT CLEAN
- RBLX | S031 | n/a | trailing_pe -36.72, P/B 245; wrong reason | blank 31 | NOT CLEAN
- MTD | S031 | n/a | P/B 2,760.7; operating income blank no reason | blank 27 | NOT CLEAN

### S032 (no band stated)
- KMB | S032 | n/a | none (AR/AP/inventory series stop) | unexpl 6, blank 14 | NOT CLEAN (borderline)
- RPRX | S032 | n/a | wrong biotech reason; dividends unmapped | unexpl 25, blank 50 | NOT CLEAN
- PCG | S032 | 35.42B | cover vs balance-sheet shares 22% apart | unexpl 14, blank 38 | NOT CLEAN
- CCI | S032 | n/a | revenue 41M vs 1,008M; P/B -10.64 | unexpl 11, blank 28 | NOT CLEAN
- CCL | S032 | n/a | none (wrong AR reason) | unexpl 9, blank 34 | NOT CLEAN (borderline)
- CLS | S032 | n/a | none (many mapping gaps) | unexpl 19, blank 52 | NOT CLEAN (borderline)
- HSY | S032 | n/a | EPS/DPS 2010 stale | unexpl 3, blank 13 | NOT CLEAN
- STLD | S032 | n/a | none | unexpl 5, blank 14 | NOT CLEAN (borderline)
- RMD | S032 | n/a | none found | unexpl 5, blank 9 | NOT CLEAN (borderline)
- BIIB | S032 | n/a | Q2 missing; wrong biotech reason | unexpl 13, blank 35 | NOT CLEAN

### S033 (no band stated)
- CNC | S033 | n/a | revenue 44,375 vs 53,579; trailing_pe -6.81 | unexpl 17 | NOT CLEAN
- ACGL | S033 | n/a | none (insurer template) | unexpl 31 | NOT CLEAN (borderline)
- TKO | S033 | 34.7B | shares blank; capex line unmapped | unexpl 21 | NOT CLEAN
- EQT | S033 | n/a | none | unexpl 7 | NOT CLEAN (borderline)
- IRM | S033 | n/a | NI incl NCI; wrong REIT reason | unexpl 8 | NOT CLEAN
- ZS | S033 | n/a | trailing_pe -552.44 | unexpl 13 | NOT CLEAN
- VMC | S033 | n/a | Q2 missing | unexpl 8 | NOT CLEAN
- FLEX | S033 | n/a | none | unexpl 10 | NOT CLEAN (borderline)
- EXPE | S033 | 34.46B | shares Class A only | unexpl 9 | NOT CLEAN
- ZTS | S033 | n/a | FY2025 balance sheet none authoritative; wrong reason | unexpl 5 | NOT CLEAN

### S034 (band 31.2-34.3B; no per-company counts)
- OKTA | S034 | 34.3B | zero debt blank; shares blank | n/a | NOT CLEAN
- CBOE | S034 | band | capex Q2 missing (tag change) | n/a | NOT CLEAN
- DXCM | S034 | band | debt 2016 zero vs 1,242.8M | n/a | NOT CLEAN
- CRWV | S034 | 32.6B | debt Q2 stale; P/E -18.99; shares blank | n/a | NOT CLEAN
- EME | S034 | band | none (inventory unmapped) | n/a | NOT CLEAN (borderline)
- CRDO | S034 | band | zero debt blank | n/a | NOT CLEAN
- AXON | S034 | band | none (interest expense unmapped) | n/a | NOT CLEAN (borderline)
- GEHC | S034 | band | Q2 missing | n/a | NOT CLEAN
- UAL | S034 | band | debt/interest base stale; wrong opex reason | n/a | NOT CLEAN
- CTSH | S034 | band | Q2 missing | n/a | NOT CLEAN

### S035 (filled of 163 given; no band)
- MTB | S035 | n/a | revenue 442M vs 2,532M; capex 2023 | filled 110, blank 53 | NOT CLEAN
- VG | S035 | n/a | none (shares blank) | filled 107, blank 56 | NOT CLEAN
- ALNY | S035 | n/a | wrong biotech reason; Q2 CFO/capex quarter not derived | filled 133, blank 30 | NOT CLEAN
- HBAN | S035 | 31.5B | Q2 missing | filled 110, blank 53 | NOT CLEAN
- SUNB | S035 | n/a | revenue 701M vs 3,115M | filled 115, blank 48 | NOT CLEAN
- MDLN | S035 | n/a | NI 6M matches neither basis | filled 113, blank 50 | NOT CLEAN
- CQP | S035 | n/a | equity unmapped | filled 121, blank 42 | NOT CLEAN
- RKLB | S035 | n/a | trailing_pe -189.67 (filing not opened) | filled 138, blank 25 | NOT CLEAN
- NTRS | S035 | n/a | revenue 1,349.5M vs about 2,698M | filled 109, blank 54 | NOT CLEAN
- RKT | S035 | 31.6B | revenue blank, shares blank | filled 80, blank 83 | NOT CLEAN

### S036 (band 28.9-30.7B; ranks 351-360)
- IR | S036 | band | stale interest expense | blank 24 | NOT CLEAN
- RJF | S036 | band | gross revenue convention; dividends 2023 stale | blank about 55 | NOT CLEAN
- MLM | S036 | band | recast quarter none authoritative; P/E with disc gain | blank 12 | NOT CLEAN
- DG | S036 | band | stale interest, buybacks 2023 | blank 36 | NOT CLEAN
- RDDT | S036 | band | zero debt blank; shares blank | blank 62 | NOT CLEAN
- EXR | S036 | band | revenue 34.904M vs 874.152M; margins 1,123.6% | blank 36 | NOT CLEAN
- WSM | S036 | band | stale zero debt; AR unmapped | blank 26 | NOT CLEAN
- WTW | S036 | band | revenue 2,428 vs 2,466; wrong reason | blank about 36 | NOT CLEAN
- JBL | S036 | band | AR stale 3,647M vs 5,473M | blank 14 | NOT CLEAN
- TDY | S036 | band | none (interest expense stale 2025-12-28) | blank 30 | NOT CLEAN (borderline)

### S037 (band 27.0-29.5B)
- ATO | S037 | band | none (DPS TTM, total_liabilities) | unexpl 9 | NOT CLEAN (borderline)
- KHC | S037 | band | trailing_pe -8.35 | unexpl 5 | NOT CLEAN
- WRB | S037 | band | debt blank vs 2,840.3M | unexpl 27 | NOT CLEAN
- HAL | S037 | band | none (AR unmapped; DPS TTM) | unexpl 5 | NOT CLEAN (borderline)
- ON | S037 | band | none (dividend reasons) | unexpl 10 | NOT CLEAN (borderline)
- ZM | S037 | band | zero debt blank; shares blank; P/E 9.0 | unexpl 23 | NOT CLEAN
- SLV | S037 | excluded silver trust | not checked | unexpl 68 | excluded
- HPQ | S037 | band | fiscal Q3 filing absent from core.filing; P/B -197.99 | unexpl 5 | NOT CLEAN
- FTI | S037 | band | none found (blank list truncated) | unexpl 6 | NOT CLEAN (borderline)
- VRSN | S037 | band | debt 0 (2013), EPS 2022, P/B -12.28 | unexpl 9 | NOT CLEAN

### S038 (no band stated)
- OTIS | S038 | n/a | D/E -1.47, ROIC 92.9% | blank 25 | NOT CLEAN
- WST | S038 | n/a | none (institutional guard) | blank 17 | NOT CLEAN (borderline)
- MDB | S038 | n/a | Q2 FY27 absent; trailing_pe -1006.95 | blank 38 | NOT CLEAN
- DTE | S038 | n/a | Q2 missing; wrong reason | blank 40 | NOT CLEAN
- AWK | S038 | n/a | none | blank 29 | NOT CLEAN (borderline)
- TW | S038 | 28.1B | shares stored 0 (2019); debt blank | blank 62 | NOT CLEAN
- FE | S038 | n/a | Q2 missing | blank 37 | NOT CLEAN
- CFG | S038 | n/a | revenue 451M vs 2,283M; capex 2019 | blank 83 | NOT CLEAN
- CNP | S038 | n/a | Q2 missing; gross margin 99.96% | blank 32 | NOT CLEAN
- DOV | S038 | n/a | none (wrong reason, pretax unmapped) | blank 17 | NOT CLEAN (borderline)

Tally: 4 CLEAN (DERIVED) out of about 191 operating companies (WAB, KDP, LHX, NTAP). About 55 have at least one FILING-CHECKED wrong value shown (counted from the T1, T2, T4, T5, T6, T8, T11 lists).

---

## History-window items

No worker did a first-period-held vs filing-history comparison, an FY2015/2018/2021 spot-check, or a missing-quarters-in-last-8 sweep as a stated method. What the files do record:

- Label/sequence breaks that make quarters unfindable: TEL(S022, duplicate Q1/Q2 labels across FY2024 and FY2025), NUE(S023, 2026 labelled 2027), FERG(S027, Q3/Q4 labels vs SEC Q1/Q2 and 10-KT Aug-Dec 2025 absent), KR(S030, 16-week Q1 and YTD periods NULL fiscal_period; FY label start vs end year).
- Quarter present in filings but no authoritative fact: MLM(S036, Q1-2025 and Q2-2025 revenue), ZTS(S033, 2025-12-31 balance sheet), HON(S020, `missing:prior_period(2025_Q2)`, prior comparatives restated post-separation), MSCI(S028, 2025 Q2 comparatives missing while 2026 Q2 exists), COIN(S027, Q2-2025 diluted shares exist in R4 but prior period not found), ALNY(S035, 2025 quarters absent so revenue_ttm and eps_growth_yoy blank), VEEV(S025, `missing:prior_period(2024_Q2)/(2022_Q2)` label mismatch candidate), IQV/EXC/etc. only the latest quarter.
- Suspiciously missing for long-listed companies (not investigated, DATA-INFERRED): XEL 2021_Q2 and dps 3y 2023_Q2(S026), WDAY 2024_Q2 / 3y revenue (S026), AIG 2021_Q2 EPS (S028), MCHP eps_growth_5y 2022_Q1 and revenue 10y 2017_Q1 (S029), SYY fcf(2023) and 2016_Q4 (S029), WAT fcf(2022)/(2020) (S028), ED fcf(2017) (S029), TWLO diluted shares 2023_Q2 (S031), FDX dps_growth_yoy `zero_base_value` and CRH dps_growth_3y `zero_base_value` (S020/S023), MNST/HSY growth cells naming 2000s periods because EPS ends 2011/2010.
- Series that stop mid-history while the line still exists: KMB AR/AP/inventory stop FY2023/2024(S032), STLD AR/AP stop FY2024(S032), PAYX AR stops before FY2026(S029), DVN AP stops 2020(S023), ROK 2024 ap/inventory/total assets (S026), HON 2024 reconciliation (S020), SPGI inventory last 2012 (S010fc), NKE shares single 2015 value(S024), CVNA shares 0 at 2017(S028), TW shares 0 at 2019(S038), TFC/CFG/MTB/ED capex dead since 2022/2019/2023/2022.
- Legitimate history limits reported (so not defects, but wording is poor): KVUE(2023), RBLX(2021), TWLO(2016 IPO), TW(2019 IPO but reasons name 2014/2016/2018 periods), RPRX (reasons name 2015-2019 pre-IPO periods), MDLN(IPO Dec 2025, only FY2025 + 2 quarters), SUNB(new filer FY2026), CRWV(IPO 2025), CARR(spun April 2020), GEHC(2023), HONA(no history), CRH(US filer 2023), APO(registrant 2022), LHX/AON/TRGP (predecessor-identity history SNR), F(diluted_shares_growth needs 2008_Q1 and 2006_Q1, history before 2009 not held).
- Nothing in the block tested first-period-held against filing history for any company.

---

## Population counts quoted

Each: number, shard, query or estimate.

- 83.8% filled and 110 unexplained (shards.csv baseline) vs 1,267 of 1,630 filled = 77.7%, 363 blank, 110 unexplained for S023's ten companies after commit fb26fb6 (S023; coverage query).
- About 207 blank cells across S010's ten (S010fc; coverage run, "BMY 21 not 14").
- 402 blank cells across S021's ten (S021; query). 363 across S027's ten (S027; query); 363 across S030's ten with 132 unexplained (S030; query, per-company sums match); 179 blank across S024's ten (S024; query); S029 header says 363 but per-company figures sum to 300 (S029; internal inconsistency, query results quoted).
- 328 companies carry `financial_institution_interest_income_not_revenue`: 186 with SIC 6000-6799, 142 without (S023; query on 2026-10-20 coverage).
- 168 companies use the Revenue-minus-`OperatingExpenses` two-input derivation for operating_income_resolved; 103 with a 2026 period (S023; query).
- 3,433 companies carry `no_dividend_history` on dividend_growth_streak_years, 502 of them with a dividends_paid value (upper bound for false reason); 3,242 companies with dividends_per_share blank and no reason (S021; query on coverage).
- 224 companies / 322 duplicate fiscal-label groups (same company, fiscal_year and fiscal_period, more than one distinct end date, quarterly-length periods from 2024-01-01) (S022; cheap query).
- 167 10-Qs (167 distinct companies) filed 2026-07-20 to 2026-08-10 with 0 facts (S025; single 50 s query). 190 10-Q/10-K filings (189 companies) filed 2026-07-15 to 2026-09-15 with zero rows in core.fact (S027; query, "some will be too recent"). 150 10-Qs (150 companies) filed 2026-07-20 to 2026-08-05 with no facts (S038; query). 27 of 236 filings (11%) in a non-random sample of the first 400 coverage companies, 10-Qs filed 2026-07-25 to 2026-08-10 (S029; estimate, sample). 12+ companies in PLAYBOOK B1 and "at least NXPI, D, SPGI, CB, KO, C, NEE, WELL" (S010fc, S021; quoted from earlier work). S023's own full count timed out at 50 s.
- 1,634 of 4,287 stored trailing_pe values negative; 450 negative price_to_book (S025; query on 2026-10-20 rows).
- 495 companies carry `pre_revenue_biotech_pharma` on a blank, 366 of them with a stored revenue value (S026; query). 29 with latest revenue above 500M and 65 above 100M (S032; lineage `revenue.latest_value`).
- 497 companies with an unexplained blank `shares_outstanding` (S026; query; "not all dual class").
- 34,290 of 295,966 filled lineage cells (4,906 companies) have a latest period before 2025-07-01 (S027; query, upper bound). 240 companies have `diluted_eps` has_value with latest period before 2025-07-01, 46 before 2020 (S032; lineage query).
- 11 companies with a revenue period of 105-125 days ending 2026 and NULL fiscal_period (S030; one cheap count).
- Zero `10-KT` / `10-KT/A` rows in core.filing across all companies (S027; query).
- sec_tag_library active-company counts: `InterestExpenseNonoperating` 2,017 (35,998 facts, candidate), `ReceivablesNetCurrent` 739, `AccountsAndOtherReceivablesNetCurrent` 508, `SeniorNotes` 328, `UnsecuredDebt` 299, `InterestIncomeExpenseNonoperatingNet` 1,048 (S036; tag-library query).
- Hit rates inside shards: book_value_per_share blank D1 at 10/10 (S010fc, S021, S027, S028, S036), 9/10 (S029, S030, S032, S035), 9/9 (S037) etc. (per-shard queries, see T4); 0-facts latest 10-Q at 2 of 10 in S021, S028 and S034, 3 of 10 in S025, 3 of 10 in S038 (DTE, FE, CNP) plus 1 absent filing (MDB).
- Not counted, flagged as needing chunked queries: ASC 606 revenue-tag precedence reach (S021, S022, S025, S031, S035, S036), dual-class shares reach (S024, S027, S033, S034), MLP/LP reach (S020, S022, S035), net income basis reach (S020, S025, S033), currency reach (S020), HPQ/MDB-style ingestion gaps (S037, S038), debt-free wrong-zero audit (S027, S037), business-combination discontinuities (S028), EPS per-class tag reach (S027, S031). Cloud/pooler 50 s cap prevented `core.fact` joins in S021, S022, S023, S024, S031, S032.
