# Top-1000 campaign: merged findings across all shards (S000-S102)

Findings only. No fixes are proposed and nothing was built, queried or fetched for this document. It is a merge of five digests (DA: S000-S019; DB: S020-S038 plus the S010 filing-checked rerun; DC: S039-S059; DD: S060-S079; DE: S080-S102) and `shards.csv`. Figures and accession numbers are copied from the digests. Where two digests disagree, both are shown. Everything in the "mechanism" lines is the workers' wording or, where marked, the author's inference.

Abbreviations: FC = FILING-CHECKED (worker opened a filing R-page or SEC record and cited it). DI = DATA-INFERRED (our tables only). SNR = suspected not reported. D1 = the per-share pairing defect (equity at the balance-sheet date, share count at the cover date, so book value per share and similar cells never form).

---

## 1. What was run, evidence levels, honest limits

**Run.** One read-only worker per shard of ten companies, shards S001-S102 (S000 was a market-cap ranking audit). `shards.csv` has 1,014 company rows, of which 28 carry an "excluded" note (wrong market cap, foreign private issuer, trust, acquired company, or S000 re-rank backfills). Digest coverage: DA 189 companies (S001-S019, TBLA left to S000), DB about 191 (S020-S038 plus a filing-checked rerun of S010), DC 210 (S039-S059), DD 200 (S060-S079), DE 224 (S080-S102; S101 and S102 are 8 and 6 backfills, S102 with blank market cap). The S010 companies appear twice (DA data-inferred, DB filing-checked rerun); the rerun supersedes. Each company has 163 coverage cells (1,630 per shard).

**Evidence levels (what the workers could and could not do).**
- S001, S003, S004, S005, S006, S007, S008, S011 are DATA-INFERRED only (DA also lists S010 in this group; the S010 filing-checked rerun in DB replaces it). sec.gov was blocked by network policy or by the permission classifier, or by instruction. These early files use an older format and call blanks "unknown (suspected not_reported)".
- Every other shard opened SEC R-pages, but mostly **the latest 10-Q only** (plus YTD cash flow). Very few workers opened a 10-K headline. DB, DE and DC each say "FY2025 10-K headline check not done" for most companies.
- **FY2015 / FY2018 / FY2021 spot checks** were done by no worker in S000-S057 (DA, DB), and only in a handful of shards later (S058, S059, DD, DE); where done they were mostly from memory (DI), not an opened filing.
- **Population counts were mostly NOT run.** The Supabase MCP has a 50-60 second cap and `core.fact` joins time out. Almost every "NEW" family says "not counted beyond this shard". Only a few coverage-table counts exist (section 5).
- All FC reads used one regex R-page reader (rows plus `defref_` tag, footnote cells dropped), with no independent cross-check (DA).
- **Verdicts are DERIVED** by the digest authors unless a file had its own verdict table (only S058 and S059 did, per DC). DA's derivation rule counts a company CLEAN if no wrong, stale or wrongly reasoned value was found, regardless of other blanks. DB's rule is stricter on unexplained blanks. DC treats every company as NOT CLEAN because of the four universal cells. DD and DE use the files' own wording.

**Coverage honesty note (applies to every coverage number).** On 2026-10-19/20 (commit fb26fb6) coverage `has_value` was changed to count only a value whose LATEST period has a value. After that change the S023 ten companies read 1,267 of 1,630 filled = 77.7%, against 83.8% in `shards.csv` (unexplained stayed 110) (DB, S023). The `shards.csv` unexplained and filled columns are therefore a baseline that predates the rebuild; DA notes S011 shows 361 blank cells against a baseline of 224 unexplained. Before the change `has_value` was true if ANY period ever had a value while the reason was read from the latest period (DA, S014 NEW-1: "hidden blanks": 79 in S014, 65 in S018, 69 in S019 = 213 cells in 30 companies). One DE worker (S101) says the stale-series cases still conflict with the intent of fb26fb6.

---

## 2. Headline numbers

| Item | Number | Basis |
|---|---|---|
| Companies in `shards.csv` | 1,014 rows; 986 not excluded; 28 excluded-with-reason | `shards.csv` |
| Companies covered by digests | 189 + about 191 + 210 + 200 + 224 (S010 counted twice) | digests |
| Labelled CLEAN by a digest | DA 14 (AAPL, GOOG, MSFT, AMZN, PLTR, COST, CAT, LRCX, AMAT, TXN, LIN, SNDK, BLK, MSI); DB 4 (WAB, KDP, LHX, NTAP); DC 0; DD 3 (FLS, COO, CSL "candidate"); DE 0 (SSD and TKR "closest") | digest verdict tables, all DERIVED except S058/S059 |
| CLEAN under the strict rule (no wrong value found AND only the 4 universal unexplained cells per `shards.csv` baseline) | 8 of the digest-labelled ones: AAPL, LRCX, WAB, KDP, LHX, NTAP, FLS, COO. The other 13 labelled CLEAN have 5-22 unexplained cells (for example GOOG 7, MSFT 6, AMZN 11, PLTR 14, BLK 22, MSI 7, CSL 5) | author's cross-check of digest labels against `shards.csv` |
| Also no wrong value found and baseline unexplained of 4 or fewer, but labelled NOT CLEAN by their digest (wrong reason, stale-label, history gap, or digest rule) | about 22 more: EME, WST, DOV, ATI, SNX, CRS, RVTY, WCC, RBC, MKSI, GEN, LECO, AIT, KVUE, GNRC, AEIS, TKR, SSD, FSS, ESE, POWL, NPO | author's cross-check; see section 7 |
| NOT CLEAN | everything else: about 1,000 of 1,014 rows, including 28 excluded | digests |
| Rows with any listed wrong, stale or not-meaningful value (crude parse of the verdict tables, FC and DI mixed, includes negative P/E and stale series) | DA 176 of 190; DB 139 of 200 (includes 10 rerun rows); DC 124 of 210; DD 105 of 200; DE 132 of 224; total 676 of 1,024 listed rows, approximate because of the S010 overlap | author's count of verdict rows |
| Companies with at least one FILING-CHECKED wrong value shown | DB states "about 55 of about 191". No other digest states a total. Per-theme FC counts are in section 3 and overlap, so they cannot be summed | DB statement; others not stated |
| Universal unexplained cells | `bdc_total_investment_income`, `collaborative_arrangement_revenue`, `net_lease_revenue`, `employee_count`: blank with no reason at essentially every company (DA S001: 40 cells for 10 companies; DD: 40 of 130 (S064), 30 of 190 (S061), 40 of 142 (S068), 40 of 145 (S079)). Exceptions where the cell is real or filled: ARCC (BDC), BXSL (BDC; Total investment income 320,469K Q2 filed, uncaptured), VICI/REG/MAA (lessors), CSGP (`net_lease_revenue` filled), TRV (BDC cell filled at an insurer, 4,012M, FC), BAH (3 not 4), T/ETN/CSX (tag employees) | digests |

Worst blank counts per shard are inflated by 5 foreign private issuers and 2 trusts (BMO 154, BNS 152, CNI 151, AEM 66, KZIA 122 unexplained of 152, IAU 67, SLV 68).

---

## 3. Themes

Format per theme: (a) companies affected, FC vs DI; (b) cell severity (WRONG shown, BLANK, MEASUREMENT); (c) FC exemplars; (d) mechanism guess; (e) shares a mechanism with. Counts are the sum of what each digest reports for its block; tickers carry shard ids. They overlap and are not de-duplicated.

### Summary table

| Id | Theme | Companies (approx, FC / DI) | Cell severity |
|---|---|---|---|
| T1 | Revenue = partial or sub-line tag | about 109 FC / 17 DI | WRONG (plus every revenue-derived ratio) |
| T2 | Operating income derived or from non-face line | about 44 FC wrong / about 15 DI | WRONG (plus stale and blank-without-reason) |
| T3 | Latest 10-Q/10-K has 0 facts, or filing absent | about 93 with 0 facts, 8 filing rows absent | BLANK/MEASUREMENT (whole quarter stale), with stale values shown as current |
| T4 | Shares outstanding blank/stale/wrong; market cap basis; D1 per-share cascade | about 33 + 30 + 40 + 34 + 40 named; D1 at about 80-100% of companies | BLANK mostly, WRONG market cap in about 25 cases |
| T5 | Stale series counted as filled | about 190 named; DA: effectively all 189 | MEASUREMENT + WRONG-as-current |
| T6 | True zero shown blank; total_debt unmapped/wrong/stale | about 250 named (about 90 + 40 + 40 + 45 + 47) | WRONG (about 40 FC) and BLANK (8-14 cells each) |
| T7 | Wrong or missing blank reasons | all companies; about 200 with a false reason | WRONG explanation, value itself often correctly blank |
| T8 | Negative or meaningless ratios shown | about 24 + 17 + 40 + 34 + 41 | WRONG (meaningless) |
| T9 | Fiscal year / period label wrong | about 3 + 6 + 11 + 11 + 12 | WRONG label, then BLANK TTM chain (6-25 cells each) |
| T10 | Recast / restated / predecessor / missing quarters | about 40 + 25 + 13 + 14 + 14 | BLANK and mixed-basis WRONG |
| T11 | Net income basis (ProfitLoss vs attributable), equity incl. NCI | about 20 + 15 + 9 + 8 + 6 | WRONG (small to 22%) |
| T12 | Capex, D&A, interest, receivables tags unmapped/stale/split | about 150 + 60 + 75 + 60 + 90 company-hits | BLANK cascades (7-17 cells each), some stale WRONG |
| E1 | Institutional-ownership overcount guard | 683 companies (one query, unit disputed); about 17 + 40 + 50 + 55 named | BLANK (honest), underlying 13F data wrong |
| E2 | Scale and unit errors | about 40 distinct | WRONG |
| E3 | EPS per class / non-standard EPS tag | about 25 | BLANK or stale WRONG |
| E4 | Dividend/DPS derivation, YTD-only dividend tags | about 100 | BLANK, a few WRONG |
| E5 | LP / MLP tags | 8 named | BLANK |
| E6 | Multi-registrant combined filings | 1 FC (EAI), about 8 suspected | WRONG (10 values at EAI) |
| E7 | Identity defects | 2 FC (EQR, XOM) | WRONG, history cut |
| E8 | 10-KT / transition filings | 1 FC (FERG); zero 10-KT rows in `core.filing` | BLANK/WRONG labels |
| E9 | Predecessor / successor, spin-off, IPO-limited history | about 60 | BLANK |
| E10 | Foreign private issuers, trusts, acquired, missing large companies | 11 named plus 8 missing | population defect |
| E11 | Sector templates (bank, insurer, REIT, MLP, captive finance) | about 150 | WRONG shown + BLANK without reason |
| E12 | Gross profit / cost of revenue from a partial line; `CostsAndExpenses` ambiguity | about 30 | WRONG |
| E13 | Q4/TTM derivation and YTD-only cash flow | about 100 | WRONG (few) and BLANK |
| E14 | Face line present but concept blank | about 60 | BLANK |
| E15 | Reporting-currency basis | 2 FC (CP, IMO) | WRONG |
| E16 | Provenance: proxy/8-K copies win; market cap without lineage | about 25 | WRONG (small) and traceability |

---

### T1 Revenue resolves to a partial or sub-line tag

(a) FC about 109 (DA 11, DB 23, DC 19, DD 22, DE 34); DI about 17 (DA 8, DB 1, DD 5, DE 3). Cleared correct (FC): JPM(S002), SCHW(S009), PNC(S015), HOOD(S015), C(S006). Top-20 FC with shard: AMT(S016), WMT(S002), USB(S014), BNY(S013), FCX(S013), CEG(S013), MET(S021), OXY(S021), ADM(S029), HIG(S031), IBKR(S031), CCI(S032), EXR(S036), MTB(S035), NTRS(S035), CFG(S038), CNA(S061), CRCL(S044), AFRM(S041), SBAC(S047). Opposite error (real revenue suppressed): RKT(S035, blank under the financial-institution reason though the face shows "Total revenue, net" 2,784 Q2 / 5,725 6M, FC); ENS(S095) and WMB(S016), where the sub-total or subset was larger than the face total.
(b) WRONG revenue in every period back to the first year at many (REXR, HR, VAL, LNC FY2018, CWEN, ENS, CHE, UHAL, BGC), plus revenue growth, net margin, P/S, EV/S, TTM, operating income. Quoted effects: MET net margin 101.7% and operating margin 221.5%; EXR operating margin 1,123.6%, P/S 220.8x; ESS net margin 28.87 (2,887%); OHI operating margin 2,365.9%; REXR P/S 26,209.95; UDR P/S 945.75; CPT net margin 6.00 (600%), P/S 761.9; WAL net margin 573%; AMT TTM net margin 41.8% vs about 32%. Per-company cell counts: not stated.
(c) Exemplars (FC):
- AMT, 10-Q 0001053507-26-000133 R4: stored Q2 211.1M (tag `RevenueFromContractWithCustomerExcludingAssessedTax`) vs filed "Total operating revenues" `Revenues` 2,749.1M.
- MET, 10-Q 0001099219-26-000050 R4: stored 724M Q2 / 1,458M 6M vs "Total revenues" 19,154M / 38,228M; `Revenues` is in core.fact as authoritative for the same period.
- USB, 10-Q 0000036104-26-000044 R4: stored Q2 7,598 (`InterestAndDividendIncomeOperating`) vs NII 4,361 + noninterest income 3,325 = 7,686; FY2025 (10-K 0000036104-26-000011 R4) stored 30,970 vs filed 28,540.
- Also WMT 10-Q 0000104169-26-000154 R2 (186,100 vs 187,937); EXR 10-Q 0001289490-26-000053 (34.904M vs 874.152M); HIG 10-Q 0000874766-26-000060 (111M vs 7,263M); CCI 10-Q 0001051470-26-000074 (41M vs 1,008M); HR 10-Q 0001360604-26-000064 (8,033K vs 281,849K); UHAL 10-Q 0001193125-26-335008 (237,447K vs 1,682,027K); BGC 10-Q 0001628280-26-055187 (695,557K vs 845,545K); LNC FY2018 10-K 0000059558-19-000010 (1,343M vs 16,424M).
(d) Mechanism (workers): revenue "chosen by tag-name priority, not by the statement's total line"; for banks the priority-4 provisional gross-interest-income tag outranks `RevenuesNetOfInterestExpense`; the Revenue-row fix is pinned per period so new quarters fall back to the ASC 606 tag (S016); WTFC annual and quarterly periods resolve to different tags (S073); the later incremental resolve chose a different tag than the full resolve (WMT, S002). Population evidence: 1,556 of 4,562 companies have both `Revenues` and the 606 tag filed with the partial tag chosen; 281 have `Revenues` chosen (DC S047, query).
(e) Shares a mechanism with T2 (derived from the wrong revenue), T6, T12, E12, E14 (all: line identity decided by tag).

### T2 Operating income derived or taken from a non-face line

(a) FC about 44 wrong (DA 10, DB 8, DC 8, DD 7, DE 11); DI about 15; plus many stale values and blanks without a reason. Top-20 with shard: ELV(S014), ETN(S009), JCI(S014), ADP(S012), SHW(S017), TRV(S017), BX(S017), SLB(S019), DVN(S023), AJG(S020), MET(S021), AFL(S022), HONA(S024), CASY(S040), EQR(S043), TPG(S053), AHR(S065), AFG(S063), CACC(S100), RLI(S100). Also BGC(S101), THG(S081), AOS(S081), GLXY(S092), INSW(S101), REG/MAA(S059), APA(S051), OHI(S058), VOYA(S079), EVR(S069), AMG(S072), MOG-A(S065). Population: 168 companies use exactly the two-input derivation, 103 with a 2026 period (S023, query).
(b) WRONG operating_income_resolved, then operating margin, ROIC, interest coverage. Quoted: AJG margin 83%, AFL 70.9%, CASY 87%, CACC 77%, RLI 94%, WELL -1,650M (double subtraction), TPG -792,369K on a profitable firm.
(c) Exemplars (FC):
- DVN, 10-Q 0001193125-26-334340 (FY2025 10-K 0001193125-26-056485): stored 1,497 Q2 / 2,318 6M; Devon presents no operating income; earnings before income taxes 2,384; filed `OperatingExpenses` 5,506 = total expenses 5,033 plus income tax 473.
- AJG, 10-Q 0001628280-26-053489: stored 3,324 Q2 = revenue 4,003 minus `OperatingExpenses` 679, but 679 is one caption of six; earnings before taxes 414.
- ELV, 10-Q 0001156039-26-000060 R4: stored Q2 1,763M; the face goes from total expenses to income before tax 1,937 with no such line.
- CASY: stored 4,924,225K vs about 369,089K; filed `OperatingExpenses` 754,111 excludes cost of goods sold and D&A (no accession given).
(d) Mechanism: "Revenue minus `OperatingExpenses`" is valid only where that tag is the statement's own operating-cost subtotal; or a segment-note `OperatingIncomeLoss` is taken as consolidated (MET, HONA, MOG-A); a stale old value stays "latest" where the filer presents none (GE family).
(e) Shares a mechanism with T1, T7 (companies that present none show no reason), T12.

### T3 Latest 10-Q/10-K has 0 facts in `core.fact`, or filing absent from `core.filing`

(a) 0 facts, about 93 (DA 15, DB 23, DC 21, DD 18, DE 16), of which the filed values were read FC at most; the 0-fact count itself is a DB query. Filing row absent, 8: DE(S008, DA), HPQ(S037), MDB(S038), HEI(S052), SJM(S059), JKHY(S068), IREN(S074), OLLI(S099). Top-20 with shard: CB(S009), HCA(S013), DUK(S013), GD(S014), JCI(S014), SPGI(S010/S020 rerun), URI(S020), BE(S021), DLR(S021), NXPI(S023), D(S023), F(S025), HUM(S025), PYPL(S025), PPL(S039), HUBB(S041), OMC(S043), EAI(S078), OSK(S083), VFC(S091). Control: BWXT(S063) original 10-Q has no XBRL but the 10-Q/A 0001486957-26-000044 carries 428 facts and is used (false positive).
(b) MEASUREMENT: the whole latest quarter is missing, so every latest value, TTM, growth and per-share cell is one quarter stale (HEI, SJM, IREN about two). Stale values read as current: HUBB assets 8,417.7M stored vs 11,846.2M filed; CLX P/E 14.19 vs about 18; BE revenue 746.4M stored vs 1,065.4M filed; BIIB Q2 EPS 0.66 vs 4.33 prior.
(c) Exemplars (FC, filed values): CB, 10-Q 0000896159-26-000017 (R2/R4/R6 revenue 15,816, NI 2,854, EPS 7.30; 0 rows in `core.fact`); SPGI, 10-Q 0000064040-26-000045 (revenue 4,146, assets 62,906; stored latest is Q1); HCA, 10-Q 0001193125-26-321077; HPQ, 10-Q 0000047217-26-000051 filed 2026-08-27, not in `core.filing` (max filing_date 2026-08-07); JKHY FY2026 10-K 0000779152-26-000067 filed 2026-08-28, absent.
(d) Mechanism (workers): SEC companyfacts lacks the accession, so "filing ingested but XBRL facts not loaded"; for HPQ, MDB, JKHY, IREN, HEI, SJM the filing row itself was never registered (collection/ingestion gap). Counter-evidence: for SPGI companyfacts was refetched 2026-10-06 and NEE 2026-10-15, after the 10-Q dates, and for HPQ and MDB companyfacts has the filing, so a stale payload is not the whole story (DA, DB). Combined multi-registrant filings (EXC, DTE, FE, CNP, PEG, EAI) are suspected but untested.
Populations: 167 10-Qs with 0 facts filed 2026-07-20 to 2026-08-10 (S025), 190 filings/189 companies (S027), 150 10-Qs (S038), 27 of 236 filings in a sample (S029) (section 5).
(e) Shares a mechanism with E6, E8 (ingestion gaps), and with T5/T10 as the cause of "stale".

### T4 Shares outstanding, market-cap share basis, per-share cascade

(a) Multi-class cover counts not summed or dimension dropped: FC and DI together about 33 (DA), 30 (DB), 40 (DC), 34 (DD), 40 (DE). Top-20 with shard: SPCX(S002), ACN(S009), CME(S012), UPS(S016), CMCSA(S017), TEAM(S024), MSTR(S026), WDAY(S026), XYZ(S027), EL(S030), TKO(S033), EXPE(S033), IBKR(S031), FOX(S042), CHTR(S057), PINS(S056), MKC(S063), ASTS(S064), AOS(S081), TTAN(S094). Issued reported as outstanding: GL(S061), IP(S049), EG(S055), TYL(S056). Stale or zero stored: NKE(S024, single value 855,351,589 dated 2015-07-17), CVNA(S028, literal 0 from 2017-03-31), TW(S038, 0 at 2019-09-30), CHWY(S078, 100 in 2019), HOOD/DDOG/SHOP (0). Market cap wrong basis: S000 confirmed 10 FC (AKTX, ZLAB, SCNI, KZIA, AMRN, GPCR, DBVT by ADS ratio; TBLA, RPAY by x1000 WASO; SPCX multi-class understated); also DVN (~4% low), IBKR (Class A only), QSR (~30% low), PINS (15.32B vs about 13.05B), SF, WSO, EAI (466.6M parent shares x a different security's price 18.41), PCG (cover 2,680,110,496 vs balance sheet 2,202,366,726, unresolved), CHTR (13.94B vs cover 119.28M shares, untraceable).
D1 cascade: `book_value_per_share` incomplete in nearly every shard (examples: 10 of 10 in S010fc, S021, S027, S028, S036, S040, S046, S047, S050, S051, S060, S062, S064, S068, S071, S072, S074, S077, S080, S086, S096, S097; 6 of 8 in S101). The exact cause (S027): the metric is computed at the balance-sheet date (LHX 2026-07-03 value 106.80; CIEN 2026-08-01 21.54) and then hidden by a second NULL row at the cover date.
(b) BLANK per-share cascade of 6-14 cells per affected company (book_value_per_share, net_cash_per_share, fcf_per_share, diluted_shares_growth x3, share_dilution_trend, total_shareholder_yield, piotroski, institutional_ownership_pct); WRONG market cap and P/E, P/B, P/S at about 25 companies. Population: 497 companies with blank `shares_outstanding` (S026, S044, S055, query); 477 with 270 older than 2025-10-01 (S081, query) (contradiction in section 5).
(c) Exemplars (FC): AKTX, 10-Q 0001493152-26-037730 (stored 155,758,529,533 ordinary shares, $1,274.1B; 80,000 ordinary shares per ADS gives about $0.016B); TBLA, 10-Q 0001840502-26-000012 (stored diluted WASO 290,505,359,000, $999.3B; cover 270,155,398 gives $0.93B); ACN, 10-K 0001467373-26-000049 R1 (stored 637,016,143 at 2010-03-19; cover Class A 668,722,814 + Class X 300,673); TTAN, 10-Q 0001638826-26-000094 (35,397,085 at 2024-10-31 vs 83,857,202 Class A + 12,605,018 Class B); SNDR, 10-Q 0001692063-26-000039 (cover Class A 83,029,500 + Class B 92,271,399; shares blank, market cap 5.43B still filled).
(d) Mechanism (workers): per-class cover shares are dimensioned and stripped by companyfacts, so "class-dimensioned dei fact dropped instead of summed"; "there is no ADS or depositary ratio anywhere" (`price_metrics.py` line 362); "WASO fallback with no plausibility check"; a rounded narrative fact wins the FY shares cell (USB); no cross-check of outstanding vs issued minus treasury.
(e) Shares a mechanism with E1 (wrong share base inflates institutional %), E2 (scale), E6, E9.

### T5 Stale series counted as filled

(a) DA: effectively all 189 (FC: at least 60 named, for example ETN, JCI, ADP, SHW, TRV, SNPS, MRSH, CDNS, HXL-type; the rest DI). DB about 26 FC; DC about 28; DD about 20; DE about 45 (explicit list: RHP, COLB, CBSH, LEVI, HXL, STAG, TAP, AAON, CWEN, MGY, EMN, DY, INSW, WFRD, HRB, HR, BRK-A, BAM). Worst ages: AEM whole page FY2009-2013 (S014); CDNS gross margin 94.47% from 2012; INTU gross margin 82.27% from 2020; VRTX total_debt 105.0M from 2011; LOW interest expense 86M from 2011; MRSH accounts receivable 5M from 2011; TRV operating income 2015; AXP operating margin 91.4% from 2010; HSY EPS/DPS 2010-04-04; MNST EPS 2011-06-30; EPS 2011.
(b) MEASUREMENT plus WRONG-as-current: the old value is displayed as the latest and counted as filled; the cells that depend on it are blank with a reason about a different input. 213 hidden blanks in 30 companies (DA, S014/S018/S019). DA: "real count about 356/398/233" in those three shards. Population: 34,290 of 295,966 filled lineage cells (4,906 companies) have a latest period before 2025-07-01 (S027, query, upper bound); 240 companies have `diluted_eps` latest before 2025-07-01, 46 before 2020 (S032, query).
(c) Exemplars (FC): SNPS, 10-Q 0000883241-26-000025 R4 (stored interest_expense 1.324M at 2024-01-31, coverage 266.3x; filed Q3 133.2M, about 2.7x); MRSH, 10-Q 0000062709-26-000258 R4 (stored AR 5M at 2011-06-30; filed 8,548M); CDNS, 10-Q 0000813672-26-000092 R3 (stored gross margin 94.47% from 2012; filed 84.9%); HXL, 10-Q 0001193125-26-323941 (diluted_eps latest 2020-12-31 vs filed Q2 0.64; filer now uses `IncomeLossFromContinuingOperationsPerDilutedShare`); RHP, 10-Q 0001104659-26-092580 (capex 2015-12-31 vs 241,190K 6M); VRSN, 10-Q 0001014473-26-000028 (EPS 2.38 filed vs 6.24 at 2022-12-31).
(d) Mechanism (workers): coverage `bool_or(value is not null)` across all periods while the reason reads the latest period (`coverage_matrix.py` around L740-750, DA S014); the `_resolved` concepts ignore the latest-period rule (S065); no staleness cut-off on non-TTM cells; the filer changed tag or stopped presenting the line.
(e) Shares a mechanism with T6, T12 (tag vocabulary frozen at an older generation), E3, E4.

### T6 True zero shown as blank; total_debt unmapped, wrong or stale

(a) About 250 named (DA about 90, DB about 40, DC about 40, DD about 45, DE about 47). True zero blank: FC ISRG(S009), VRTX(S010fc), MNST(S027), CMG(S030), UI(S031), ZM(S037), OKTA(S034), IONQ(S064), CART/HUBS(S066), ANF(S091), KNSA(S091), DOCS(S100), TTD(S098), DLB(S098), APPF(S084), JAN(S083); DI many more. total_debt wrong where debt exists, FC: MU, WMT, SCHW, UBER, BA, STX, MAR, ADBE, BNY, EQIX, CME, NET, CDNS, CMI, SLB, LITE, GM, KKR, CL, GD, BX, VLO, BMY, MPC, MPLX, F, PCAR, DHI, DXCM, CRWV, VRSN, WRB, ILMN, CLS, AFL, AVY, BAX, SGI, AKAM, GGG, TXT, TECH, AES, CUBE, ACM, TAP, KMX, EMN, CACC, WH, CWST, CAKE, ESNT, HOMB, ARWR, NE, DBX, VRNS. Hit rates inside shards: S003 7/10, S005 6/10, S007 6/10, S008 7/10, S009 5/10, S010 8/10, S011 6/10, S013 8/10, S015 6/10, S016 8/10 (base row; resolved correct 10/10), S060 6/10. Population: 1,698 companies with `total_debt` blank and no reason (S044, method not stated).
(b) WRONG at companies with debt (base row mostly; in 20+ cases the `_resolved` row too) and BLANK cascades of 7-14 cells (debt_to_equity, zero_debt, net_cash, roic, piotroski, net_debt_ebitda, debt_to_ebitda, net_cash_per_share, interest coverage).
(c) Exemplars (FC): MAR, 10-Q 0001048286-26-000035 R5 (stored 23M vs filed 460 + 16,455 = 16,915M); UBER, 10-Q 0001543151-26-000032 R2 (stored 14,720M vs filed 12,723M, double count); ADBE, 10-Q 0000796343-26-000156 R2 (4,766 vs 6,363); CME, 10-Q 0001156375-26-000047 R2 (0 vs 3,424.2M); ACM, 10-Q 0000868857-26-000021 (base 65,366K vs 2,714,798K; resolved 2,714,788K right); TAP, 10-Q 0000024545-26-000071 (9,718.9M vs 7,709.6M); CACC, 10-Q 0000885550-26-000182 (lineage latest 1,752.5M at 2014-12-31 vs filed 6,286.2M); VRTX, 10-Q 0000875320-26-000259 (stored 105.0M at 2011-09-30, no borrowings line in 2025-26); VLO, 10-Q 0001628280-26-050937 (resolved 9,101M vs face 927 + 10,422 = 11,349M).
(d) Mechanism (workers): `total_debt` sums whichever of `LongTermDebt`, `ShortTermBorrowings`, `DebtCurrent`, `SecuredDebtCurrent` is present; in 10-Qs only `ShortTermBorrowings` = 0 is tagged so the sum is 0; `DebtCurrent` plus `LongTermDebt` double counts; unmapped tags (`UnsecuredLongTermDebt`, `ConvertibleDebtNoncurrent`, `LoansPayable`, `NotesPayable`, custom `slb_`/`homb_`); debt only under dimensional members (GM, F, PCAR); "no filed debt line means no fact, which reads as missing instead of zero".
(e) Shares a mechanism with T5 (stale), T12, E14.

### T7 Wrong or missing blank reasons

(a) All companies carry the four universal cells. Wrong sector reason, about 200 companies: `financial_institution_interest_income_not_revenue` on non-financials (328 companies, 186 SIC 6000-6799 and 142 not, S023), including MO(S010fc), GD(S014), HPE/ORLY(S019), NUE/D(S023), KMX/VFC/AGCO(S085-S091), TXT/BAX(S060); `reit_net_interest_income_not_revenue` on equity REITs (189 companies / 789 cells, S055/S079/S091): WELL, PLD, AMT, SPG, DLR, O, PSA, CCI, IRM, REXR, ARE, VNO; `pre_revenue_biotech_pharma` on revenue-generating companies (495 companies carry it on a blank, 366 with stored revenue, S026; 1,875 cells, 464 gross_profit cells, S097): LLY, JNJ, ABBV, MRK, AMGN, PFE, VRTX, BMY, REGN, ZTS, BIIB, UTHR, NBIX, JAZZ (4.6B in 6M), PTGX, ARWR; `pre_revenue_mining_exploration` on NEM(22,669M), FCX, SCCO. Non-payers show NO REASON or `missing:` instead of "pays no dividend" (only `dividend_growth_streak_years` carries `no_dividend_history`), about 90 of 224 in DE alone, and the reverse: `no_dividend_history` at actual payers (XOM, C, DHR, GD, REGN, VRT, EPD, DLR, ET, HSY, EBAY, LPLA, VRSK, SBAC, CDE, AM, VNOM, INGR, LKQ). Sector-template cells (current ratio family, inventory days, cf changes, sga) with no reason at banks, insurers, REITs, MLPs, brokers (about 17-25 cells each). `line_not_presented_in_filing` or `line_in_filing_not_extracted` contradicted by the face: SCHW, HCA, TRV, EOG, HOOD, UAL, CCL, WAT, HRB, BLCO, CAI. Population: `no_dividend_history` on 3,433 (DB: companies; DC: cells; DE: blank cells) with 502 of them having a dividends_paid value (S021); 3,242 companies with DPS blank and no reason (S021).
(b) WRONG explanation (the blank is often right). Counts: PFE 5 cells, PGR 12, WELL 9, EPD false no-dividend plus 25 unmapped, MAC 11, ARE 8, ACT 8.
(c) Exemplars (FC): SCHW, 10-Q 0000316709-26-000031 R2 (reason `line_not_presented_in_filing` vs "Interest revenue" 4,146 on the face); VRT, 10-Q 0001628280-26-050609 R6 (`no_dividend_history` vs dividends paid 47.8M); HPE, 10-Q 0001645590-26-000080 R2 (financial-institution reason on an IT hardware company); NUE, 10-Q 0001193125-26-345891 (no operating income on the face, yet financial-institution reason); ZTS, 10-Q 0001555280-26-000040 (revenue 2,468M Q2 labelled `pre_revenue_biotech_pharma`); KMX, 10-Q 0001170010-26-000104; ARWR, 10-Q 0000879407-26-000057 (413.0M nine-month revenue); DLR, 10-Q 0001104659-26-089296 (distributions 435,908K vs `no_dividend_history`).
(d) Mechanism (workers): the reason is keyed on a stray tag or SIC, not on the statement: `classify_concept_gaps` has an `exists(... co2.tag = any(_FINANCIAL_INCOME_TAGS))` test with no period, size or SIC limit (S010); the pharma reason "seems to be assigned by SIC 2834 alone" (S001); `bdc_total_investment_income` carries `applicable_population = bdc_company` but is still in the matrix for non-BDCs (S003); the non-payer reason is derived from an absent input, not from absent activity.
(e) Shares a mechanism with T2 and E11 (sector template), T5 (reason read from the latest period while value read from any), and the four universal cells.

### T8 Negative or meaningless ratios shown as numbers

(a) About 24 (DA) + 17 (DB) + 40 (DC) + 34 (DD) + 41 (DE) = about 150 shown; the arithmetic is right in nearly all (DI), the loss or equity itself FC. Population: 1,634 of 4,287 stored `trailing_pe` values negative and 450 negative `price_to_book` (S025, S073); 1,642 negative / 2,174 non-negative / 796 null of the latest rows (S097) (different filter; section 5). Top-20: APD -1,429.43(S020), BE -5,546.82(S021), ZETA -3,353.01(S084), MDB -1,006.95(S038), TEAM -1050(S024), ZS -552.44(S033), FROG -249.12(S070), HPQ P/B -197.99(S037), DVA P/B -14.50(S064), ABBV P/B -85.4(S003), MCD ROE -859%(S008), DELL ROE -797%(S005), GDDY ROE 13,587%(S059), MTD P/B 2,760.7(S031), FTNT ROIC -222.6%(S010), MCK ROIC 1,640%(S011), MAS ROE -345.9%(S056), COF YoY growth on a negative base -155%(S011), PLXS operating margin 46.95 (S095), MOS dividend yield 12,246.07 (S096).
(b) WRONG (meaningless), 1-4 cells per company.
(c) Exemplars (FC equity or loss): LOW, 10-Q 0000060667-26-000117 R2 (D/E -5.05, P/B -14.9, ROE -89%; equity -7,437M); ORLY, 10-Q 0000898173-26-000045 R2 (D/E -3.82; deficit -1,835.7M); CL, 10-Q 0000021665-26-000042 R4 (P/B 319.2, ROE 864%; Colgate equity 236M, total incl. NCI 566M); AAL, 10-Q 0000006201-26-000052 (P/B -2.02; equity -3,972); MO, 10-Q 0000764180-26-000094 (equity attributable -2,668M).
(d) Mechanism (workers): `trailing_pe` has no non-positive guard (`peg_ratio` already carries `non_positive_growth_not_meaningful`); P/B, D/E, ROE, ROIC have no guard for non-positive equity or invested capital; the CAGR metrics null this case but YoY does not.
(e) Shares a mechanism with E1/E2 as "missing presentation guards".

### T9 fiscal_year / fiscal_period label wrong

(a) About 3 (DA, DI) + 6 (DB) + 11 (DC) + 11 (DD) + 12 (DE). FC against SEC companyfacts `fy`: NUE(S023), FERG(S027), KR(S030), ULTA(S040), ROIV(S041), DLTR(S042), EXEL(S054), SWK/TRMB(S058), DKS(S061), DDS(S070), LULU(S071), CHWY(S078), GAP(S081), ANF(S091), ACI(S092), M(S093), CNM(S081). DI: PG(S003), ADP(S012, Jul-Sep labelled Q1, fiscal Q3 never exists), TEL(S022), ONTO(S068), QXO(S066, about 25 cells), DAR(S074), CAVA(S090, 16-week Q1 with NULL `fiscal_period`), SLAB(S086), BJ, LDOS, CGNX. Populations: 38 companies with a Q4 ending 2026-01-01..09 labelled fiscal_year 2026, 43 with FY labelled 2025, 244 with any period in that window (S054, query); 35 with Q4 ending 2026-01-01..07 labelled FY2026 (S086); 224 companies / 322 duplicate-label groups since 2024-01-01 (S022); 11 companies with a 105-125 day revenue period ending 2026 and NULL `fiscal_period` (S030).
(b) WRONG label (values themselves align); BLANK TTM chain of 5-25 cells (revenue_ttm, diluted_eps_ttm, cfo_ttm, trailing_pe, price_to_sales, ev_sales, ebitda_margin, fcf_yield, peg_ratio); ADP 15 price-based TTM cells; KR 8; QXO about 25.
(c) Exemplars (FC): NUE, 0001193125-26-220778 and 0001193125-26-345891 (all 2026 stored as fiscal_year 2027; SEC fy=2026, fp=Q1/Q2); ULTA, 10-K 0001104659-26-035243 (FY ended 2026-01-31 stored 2026 vs SEC fy=2025); ROIV, 0001635088-26-000061; EXEL, 10-K 0000939767-26-000021; DDS, 10-K 0000028917-26-000006; ANF, 0001018840-26-000047 (stored fy 2027 vs SEC fy=2026 Q2); ACI, 10-K 0001646972-26-000032 (stored FY2026 vs SEC FY2025).
(d) Mechanism (workers): "fiscal year taken from the calendar year of the period end date" for January and 52/53-week year-ends; derived Q4 gets the calendar year of its end date; 16-week quarters get NULL `fiscal_period`; ADP: "derive fiscal_period from the company's fiscal year end and start/end dates, not from the filing's fp".
(e) Shares a mechanism with E8 (transition periods), E13 (TTM construction), T10.

### T10 Recast, restated, spun-off, predecessor comparatives; missing quarters inside the last 8

(a) About 40 (DA) + 25 (DB) + 13 (DC) + 14 (DD) + 14 (DE). FC: MMM(S016), ZTS(S033), MLM(S036), IFF(S043), AMRZ(S046), DD(S050), FTV(S050), JAZZ(S059), PAG(S058), PSKY(S070), APTV(S076), ETSY(S083), TFX(S100), FLR(S094), LNC(S084). DI: GE(S004), ANET(S006), MRVL(S006), AEIS(S074), BAH(S077), HL(S071), CSGP(S060), JEF(S071), MLI(S060), HON(S020), KDP and acquirers (real jumps). Rounding-scale duplicates treated as conflicts: 82 tag-periods in 8 of 10 companies of S006 (ANET 30, MRVL 24, CRM 13, SHOP 8).
(b) BLANK (revenue_growth_yoy, TTM, CAGR) and mixed-basis WRONG (MMM revenue 5y -6.2% and 10y -1.6% CAGR; APTV implied TTM 18.73B; MLI trailing_pe 8.56, about half true; KLAC Q4 EPS -22.61; BKNG trailing_pe 1.23 vs about 18).
(c) Exemplars (FC): MMM, 10-K 0000066740-25-000006 R3 (FY2022 net sales re-presented 26,161; stored FY2021 35,355 original, 10-K 0000066740-22-000010); ANET, 10-K 0001596532-25-000028 (Assets 14,043,921,000) vs four later filings (for example 0001596532-26-000013) 14,043,900,000, all five `is_authoritative=false`, no canonical value for 2024-12-31 (DI on the resolver); PSKY, 0002041610-26-000011 (successor 2025-08-08 to 2025-12-31 revenue 12,269M; predecessor revenue 16,622M `is_authoritative=false`; no FY2025, no TTM); IFF (stored Q1 2,741 vs recast 1,906; 3,860 - 1,954 = 1,906); ETSY (Q2 2025 original 672.7 and recast 629.1 both non-authoritative).
(d) Mechanism (workers): a rounding-scale or recast change is treated as a conflict and the period is left with no authoritative fact (S006 W9: "the gap is 0.00015%"); "latest filed wins re-presents only the periods inside the later filings' comparative window" (S016); a stock split missing from `company_stock_split` (S011, S060); restatement basis not tracked per period.
(e) Shares a mechanism with E9, E13, T11, E16.

### T11 Net income basis inconsistent; equity incl. NCI

(a) About 20 (DA), 15 (DB), 9 (DC), 8 (DD), 6 (DE). FC wrong: SCHW(S009), FCX(S013), AMT(S016), CMI(S019), T(S009, equity incl. NCI 15,990), SPG(S020), OXY(S021), O(S024), IRM(S033), QSR(S039), CF(S049), FTAI(S052), IVZ(S063), AR(S064), JEF(S071), BAM(S102), CELH(S088). DI: MDT(S011, FY2022-26 about 10^6 too small), NFLX/HD(S004). Provenance-only (value equals 10-K): CAT, BKNG, PH, APH. Population: 231 of 5,210 companies cite `ProfitLoss` as net_income source tag (S062, method not shown).
(b) WRONG (about 0.04% to 22%; FCX TTM about 4,183M vs about 2,945M attributable; SPG ROE about 19% high; QSR ROE about 22% high; MDT ROE 0.86% vs about 10.4%).
(c) Exemplars (FC): FCX, 10-Q 0000831259-26-000036 R3 and 10-K 0000831259-26-000012 R3 (stored Q1 2026 `ProfitLoss` 1,387M; attributable 881M); SCHW, 10-K 0000316709-26-000009 R3 (stored FY2025 8,417 vs filed 8,852; base row holds DEF 14A 0001193125-26-142826 R2 value 8,852,000, 1000x too small); CMI, 10-Q 0000026172-26-000029 R2 (968M vs 932M attributable).
(d) Mechanism (workers): the resolver falls back to `ProfitLoss` when `NetIncomeLoss` is untagged; proxy (DEF 14A) and 8-K values win over authoritative 10-K copies (S004), "breaks the hard rule is_authoritative=false is a hard filter" (MDT); equity resolved by tag priority (`...IncludingPortionAttributableToNoncontrollingInterest`) not attributable-first.
(e) Shares a mechanism with E16, E2 (proxy $ thousands read as dollars), T1.

### T12 Capex, D&A, interest expense, receivables tags unmapped, stale or split

(a) About 150 company-hits (DA), 60 (DB), 75 (DC), 60 (DD), 90 (DE), not de-duplicated. Interest expense hits alone sum to about 99 in DA. Capex FC examples: GLW(S012), EOG(S016), VLO(S010fc), FANG(S023), DAL(S025), SNA(S048), PR(S046), CSGP(S060), AR(S064), RYAN(S068), AAOI(S092), APPF(S084), RHP(S082). D&A as two lines (Depreciation + Amortization): about 30 (DA), SEIC, RYAN, SJM, VIAV (40.4 + 67.9), AJG. Interest: Q, DD, QSR, ULS, ILMN, OXY, CIEN. Receivables: VLO (stored 9,207M vs face 9,877M), BBY, J, CHRW, ARMK, CDW AP.
(b) BLANK cascades: capex gap costs 7-17 FCF-family cells (EOG 13, PSX 13, NEE 17, PR 17+, SNA 13); D&A gap 5 EBITDA cells + 4 ratios; interest gap blanks coverage; AR gap about 4-5 cells. WRONG where a stale or wrong value is shown (LEN derived capex -8,019K, CSGP capex 26% low, APPF capex 228K vs 2,782K, RYAN 1,556K vs 30,432K).
(c) Exemplars (FC): GLW, 10-Q 0000024741-26-000255 R6 (stored capex 986M at 2020-09-30, filed 754M); EOG, 10-Q 0000821189-26-000149 R7 (capex never stored; additions 3,129 + 297); FANG, 10-Q 0001539838-26-000142 R5 (`PaymentsToExploreAndDevelopOilAndGasProperties` 1,929, 12 FCF cells); DAL, 10-Q 0000027904-26-000038 R5; AAOI, 10-Q 0001437749-26-026278 (`PaymentsToAcquireOtherPropertyPlantAndEquipment` 335,132,000 authoritative in core.fact, not used); APPF, 10-Q 0001433195-26-000058.
(d) Mechanism (workers): the tag vocabulary is frozen at an older generation of tags (period-scoped tag sets, S005); the capex candidate list is too narrow with no fallback to the cash-flow line; D&A maps one combined tag with no sum of components; custom extensions are absent from companyfacts (domain rule 8.9) so some cannot be fixed from it; only 90 of about 12.4k SEC tags are approved/provisional/preference and 64% of `core.fact` rows sit under unmapped tags (root CLAUDE.md audit 2026-10-17).
(e) Shares a mechanism with T1, T5, T6, E14.

---

### E1 Institutional-ownership overcount guard (`implausible:institutional_shares_exceed_shares_outstanding`)
(a) DI everywhere (nobody investigated the cause). Named: about 17 (DB), about 40 (DC), at least 50 (DD), about 55 (DE). Measured overcount (DI): CCK 254.7M held vs 108.8M outstanding (2.3x), FIVE 177.5M vs 55.1M (3.2x), HSIC 126.9M vs 111.4M, SAIA 29.4M vs 26.67M, OC 84.1M vs 79.0M; rows include amendments (MDGL 590 rows for 377 filers, DPZ 1,205 for 786). Population: 683 (unit disputed, section 5).
(b) BLANK, one cell per company; the guard is honest but the stored holdings or share base is wrong.
(c) No FC exemplar.
(d) Mechanism (workers): duplicate filer rows, amendment rows, sub-adviser or option legs summed; or the wrong share base for multi-class names (HON, MSTR, IBKR, TTAN, AOS).
(e) T4 (share base). Same mechanism as the 13F double-counting family in section 4.

### E2 Scale and unit errors
(a) FC: AKTX, TBLA, RPAY (WASO x1000), ZLAB, SCNI, KZIA, DBVT, AMRN (ADS), PLXS (revenue unscaled in companyfacts, negative annual revenue FY2011-14, derived Q4 4,029,991,400), CHE (net income FY2022-25 249,624 dollars vs 265.2M; derived Q4 -211,378,001; source DEF 14A 0000019584-26-000005 and -000052), SCHW (DEF 14A thousands), MDT (about 10^6 too small, DI), MOS (DPS 220,000 vs 0.22; yield 12,246.07; 140 rows over 39 companies, S096 query), `EntityPublicFloat` errors (ONTO $4,817B, TTMI $4,166B, SKY $4,136B, OLED $6,792B, NOVT $3,497B, ENVA $2,670B, CBT $4.4e15, WTTR $837B, CRD-A $240B, RPAY $399.7B; too small ARES, LB, PTCT) and six latent WASO scale errors (WAT 98.2B, NTNX, CYTK, LOAR, IOVA, MCD) (S000). Rounding cases (SAIC 42,000,000 vs 41,897,635; FAF rounded cover) are minor.
(b) WRONG; market cap for 10 rows of 1,300 checked in S000 (7 in the top-1000).
(c) Exemplars: see T4 (AKTX, TBLA).
(d) Mechanism (workers): no ADS ratio; WASO fallback with no plausibility check; per-share items inherit filing scale; "no cross-concept scale check (revenue << operating income)"; proxy values win over the 10-K.
(e) T4, T11, E16.

### E3 EPS per class or under a non-standard tag
(a) FC: V(S002, 11 cells), KKR(S018), ABNB(S012, 10 cells, `IncomeLossFromContinuingOperationsPerDilutedShare` 1.37), GD(S014), HSY(S032), MNST(S027), VRSN(S037), STZ(S044), RNR(S056), STE(S044), HXL/STAG/CHDN/CWEN/MGY(S089, S095, S099), GLXY(S092), FWONA/BAM/PLNT/BRK-A/UHAL(S102). DI: BKR(S024), CVNA, WEC, ARES.
(b) BLANK or stale EPS, which in turn stalls trailing_pe, PEG and growth cells (HSY, MNST name 2000s periods).
(c) Exemplar: V 10-K 0001403161-25-000089 R8; HXL 0001193125-26-323941.
(d) Mechanism: the undimensioned fact exists only until the filer splits by class or changes tag.
(e) T5, E4.

### E4 Dividend and DPS derivation; YTD-only dividend tags
(a) FC: V(S002: FY DPS 0.59 is the quarterly rate; derived Q4 -1.18; TTM DPS 0.75 vs 2.52; yield 0.187% vs about 0.63%; 10-K 0001403161-25-000089 R8), WMT(S002, payout 0.0000), PNW(S062), PBF(S072), AM(S073), ORI(S074), WTS(S064), RYAN(S068), RYN(S098, special dividend, yield 13.1% vs about 4.5-5%). JBHT(S045: DPS -0.88). Payers with blank DPS or yield: about 28 (DC), about 20 (DD), about 24 (DB). Wrong or missing `PaymentsOfOrdinaryDividends` mapping: GE, PFE, DUK, CL, HWM, EOG, GLW, JNJ, ACN. `zero_base_value` reason at actual payers (HEI, FDX, CRH).
(b) BLANK mostly; a few WRONG.
(d) Mechanism: "TTM builder ignores an annual DPS fact"; cumulative per-share figure assigned to the quarter; discrete-quarter derivation subtracts to zero; YTD-only per-share dividend tag.
(e) E13, T7.

### E5 Partnership (LP/MLP) tags
(a) ET(S020), MPLX(S022), CQP(S035), EPD(S017, 25 cells), WES and PAA (S049/S050), plus ARXS equity (LLC members' equity). FC lines, tag-level DI.
(b) BLANK (equity, ROE, ROIC, D/E, BVPS, basic EPS, DPS; MPLX 18 unexplained).
(c) CQP, 10-Q 0001383650-26-000028 (`PartnersCapital` 754,000,000 in core.fact at 2026-06-30, R3 Total partners' equity 754); MPLX, 10-Q 0001552000-26-000038 (14,027); ET, 10-Q 0001276187-26-000038 (`DistributionMadeToLimitedPartnerCashDistributionsPaid` filed three periods, unmapped).
(d) Mechanism: `StockholdersEquity` and dividend tags only; `PartnersCapital*` and `DistributionMadeToLimitedPartner*` not mapped. Reach quoted from `sec_tag_library`: 101, 49, 60, 36, 39 active companies for the five tags (S017, "not coexistence-checked").
(e) T12, E11.

### E6 Multi-registrant combined filings
(a) FC: EAI(S078). Suspected combined filings: EXC(S028), DTE/FE/CNP(S038), PEG(S031, parent values matched), XOM two-registrant 10-Q (S002), CNP.
(b) WRONG at EAI: revenue 3,523,638K Q2 / 6,711,264K 6M is Entergy Corporation (Entergy Arkansas is 693,486K / 1,339,783K), plus operating income 850,089K vs 158,472K, net income, diluted EPS 1.03 (an LLC has no EPS), assets 79,002,618K vs 17,638,405K, equity, shares 466,631,498 and market cap 8,590,685,878 from a different security's price. 0 FY revenue rows; 32 10-Ks, none with facts.
(c) EAI, latest 10-K 0000065984-26-000174 and Q1 10-Q 0000065984-26-000222 show 0 facts under EAI; only Q2 has 467 facts.
(d) Mechanism (worker): "undimensioned fact in a multi-registrant filing attributed to every co-registrant"; "security-type not checked before computing market cap".
(e) T3, E7, T4.

### E7 Identity defects
(a) EQR(S043, FC cover R1): `company_name` "VIVMARK RESIDENTIAL", `display_name` "AvalonBay Communities, Inc.", `primary_ticker` "VMRK"; the filing says EQUITY RESIDENTIAL, CIK 0000906107, symbol EQR (also revenue frozen at 2020 and operating income 520.0 vs 218.9). XOM(S002, FC): 10-Q 0000034088-26-000093 is a combined two-registrant filing (Exxon Mobil Corporation and ExxonMobil Holdings Corporation); CIK 0000034088 absent from `core.company`; 46 period_gap cells; history starts Q2 2026.
(b) WRONG identity; history cut.
(d) Mechanism: not diagnosed by the workers. (Author's inference: company/CIK mapping drift, see section 4.)
(e) E6, E9, E8.

### E8 10-KT / transition filings
(a) FERG(S027, FC): 10-KT 0002011641-26-000006 (Aug-Dec 2025 transition; revenue 12,833M, NI 786M) absent from `core.filing`; Jan-Mar 2026 stored FY2026 Q3 and Apr-Jun FY2026 Q4 vs SEC fy=2026 Q1/Q2. Zero `10-KT`/`10-KT/A` rows in `core.filing` for any company (S027, query).
(b) BLANK/WRONG labels (15+ TTM/CAGR cells at FERG).
(d) Mechanism: transition filings not collected; label from end date.
(e) T9, T3.

### E9 Predecessor / successor, spin-off and IPO-limited history
(a) Predecessor CIK or registrant cuts: XOM, BLK, DIS(S007), AVGO(S001, redomicile 2018), MRVL(new CIK 1835632 in 2021), LIN, SHOP, CI, HWM, PSKY, EGP, LHX, AON, TRGP, WULF, MGY, GEN, PNFP; spin-offs GEV, SNDK, CEG, HONA, QNTY, SOLS, VNOM; 20-F to 10-K switchers SN, JHX, IREN; IPO-limited about 25 (PLTR, UBER, SNOW, ABNB, NET, DASH, HOOD, APP, DDOG, CRWD, MRNA, VRT) and about 25 more in DC/DD/DE.
(b) BLANK (10-year CAGRs missing because the 2016 base is absent; TTM missing). DA notes several are legitimate history limits but the reason should say so (S009 NEW-H, S005 F10).
(d) Mechanism: history is held under the current CIK only; reason text names a pre-IPO period (`missing:prior_period(2016_Q2)`).
(e) T10, E7.

### E10 Population and scope defects
(a) Foreign private issuers kept by a legacy 10-K or filing 20-F/40-F: BMO(S011, 154 blanks, 40-F x25 and 40-F/A x5), BNS(S012, "10-Ks" are covered-bond ABS reports, 0 facts, 0001140361-21-002628, 152 blanks), AEM(S014, never filed a 10-K, 40-F x13, 20-F x12, 6-K x489, 66 blanks; whole page FY2009-2013), CNI(S018, 40-F x25, 6-K x572, 151 blanks), KZIA(S094, 20-F, 122 of 152 blanks unexplained), SCNI(S069, 20-F), ZLAB. Trusts: IAU(S000 rank 211), SLV(S000 rank 367); IAU trailing_pe 805.96. Acquired: WBD(S017): acquired 2026-10-06, Form 25 and 15-12G, still `active`, market cap $77,782M at a 2026-10-05 price; 8-K 0001193125-26-415055, 15-12G 0001193125-26-423513. S000 also listed 8 large companies missing from the ranking because market_cap is null: BRK-A, FWONA, BAM, PLNT, UHAL, SUN, ENB, TSM (the first six were later backfilled in S102 with blank market cap).
(d) Mechanism (workers): population is `status='active'` minus SPAC and trust reasons with no form check; "classify by the latest annual form (40-F/20-F)".
(e) T4, E2 (ADS), T3.

### E11 Sector templates (bank, broker, insurer, asset manager, exchange, REIT, MLP, captive finance)
(a) FC and DI: JPM, BAC, MS, GS, WFC, C, AXP, COF, USB, PNC, BNY, SCHW, HOOD, KKR, BX, BLK, CB, TRV, PGR, CI, ELV, UNH, MRSH, CME, ICE, ADP, EPD, WELL, PLD, AMT, EQIX, GM, DE, plus the S020-S102 banks, insurers, REITs, MLPs. Bank rows `not_applicable` about 42-63 per bank; bank metrics still shown (D/E WFC 0.14, GS 3.57, MS 3.37; net_cash; fcf_yield; ev_sales); banks' net interest income and interest income unmapped while the face has them (WFC, MS, USB, PNC, C, AXP, GS NII -59,217M); "15 banks with a wrong net_interest_income value" quoted from another document (S004). Customer-fund balance sheets make current ratio and ROA meaningless (CME 158.1B of 194.7B assets, ADP 43.96B of 63.2B, ICE 122B).
(b) WRONG shown plus BLANK with no reason.
(c) CME, 10-Q 0001156375-26-000047 R2/R6; EPD, 10-Q 0001061219-26-000021 R2/R6; GM, 10-Q 0001467858-26-000051 R4 (debt only on `gm_BusinessGroupAxis` members).
(d) Mechanism (worker): "industrial template applied to a non-industrial statement"; not-applicable cells need the face-line check before a reason is shown.
(e) T7, T1, T2, E5.

### E12 Gross profit / cost of revenue from a partial cost line; `CostsAndExpenses`
(a) FC: UNH 88.6%, CVX 43.6%, ELV 89.1%, WM 40.9%, EPD 25.6% (about 12.5% correct), CI 20.6%, COP 50.9%, RCL 49.1%, RSG 42.0%, KMI 48.9%, MPC 17.2%, BMY, NEM, CNP 99.96%, KYMR gross margin 0 beside revenue 65M. Cost of sales filed only on Product/Service members: GD, CDNS, INTU, SLB, NOC, HPE, GM, REGN. `CostsAndExpenses` is opex at some filers (ORCL, CME, MRVL, HLT, V, CEG, DUK, EOG, UPS, AMT, WMB, CMCSA) and includes COGS or interest at others (STX, ACN, UBER, HCA, GE, CVX, ABBV, UNH, AMGN, TMO, SBUX, ELV, DASH): 33 cells carry one gap reason for both cases (S013).
(b) WRONG.
(d) Mechanism: no gross-profit line exists but a margin is presented anyway; perimeter of the cost tag not checked. A sanity gate (gross margin above 95%, operating margin above about 70% for a non-royalty company) was suggested by workers.
(e) T2, T1.

### E13 Q4 and TTM derivation; YTD-only cash flow
(a) Derived Q4 impossible or non-additive: DIS(S007, FY interest_expense sign flipped FY2021-25, derived Q4 -3,208M, -3,608M, -3,445M), KYMR(S078, Q4 NI +535,721K vs (86,981)K), CAI(S078, Q4 EPS 8.24 vs about 0.29), TPL(S042, Q4 EPS -8.59, P/E 345.24), AMCR(S047), VIAV, FLR, LEN(S049, capex -8,019K), RPAY, COP, JBHT. YTD-only cash flow blocks TTM and the EBITDA chain (`ebitda` `missing:4_consecutive_quarters` plus 4 ratios): very widespread (NXPI, KEYS, AZO, APD, IQV, HPQ, ROP, COIN, FERG, MSCI, NKE, ALNY, WAT, DTE, ALLE, AVY, DOC, TXT, JKHY, SM, R, OTEX, VFC); TTM cannot form on 12/12/12/16-week calendars (COST 10 cells, PEP 4); LSCC(S055) price metrics regressed to blank since 2026-10-03 (hypothesis: 371-day window rejected by a span guard, untested).
(b) WRONG (few) and BLANK (5-6 EBITDA cells plus FCF cells per company).
(d) Mechanism: standalone quarters cannot be derived when only YTD is filed or the line changes tag between quarters; Q4 by subtraction from a mismatched YTD base or after a share-base change.
(e) T9, T10, T12, E4.

### E14 Face line present but concept blank
(a) FC lines with a blank concept: operating_expenses / total costs and expenses (MPC, VRTX, UAL, MSCI, WAT, HPQ, CMG, ODFL, AON, CNC, DGX, QSR, MKL, ROL, BURL), gross_profit derivable (VRTX, TKO, PINS, EFX, ULS), income_before_tax (PYPL 1,310 Q2, CVNA 579, DOV 387,698K, LH, NI, BR, CRL), other_income_expense_net (about 40 companies), basic_eps (MPLX 1.06), inventory (NEM 1,478M, DHI 26,686.9M, DAL 2,637), accounts_payable (DHI 1,388.4M, CDW 5,117.4M), `total_liabilities` derivable at about 25 (ENTG, PKG, LYB, BG, NI, SBAC, BBY, GPC, IP, CF), dividends and repurchases (RPRX, RJF, RBLX, CSGP 587M, PAYC 1,389.7M), cash tag `us-gaap:Cash` (FDXF 251M).
(b) BLANK.
(d) Mechanism: vocabulary gap (tag not in the mapped set).
(e) T12, T1, T6.

### E15 Reporting-currency basis
(a) FC: CP(S018, 10-Q 0000016875-26-000026): statements in CAD, USD market cap divided by CAD values; P/B 76.7B / 46,626M = 1.645; P/E, P/S, P/B understated about 28%, yields overstated about 39%. IMO(S020): statements in CAD, trailing_pe 15.67, P/B 2.65, market cap 64.9B divide a USD price (price currency DI) by CAD EPS and equity.
(b) WRONG. Reach not counted.
(d) Mechanism: no currency carried on price-based ratios.
(e) E2, E10.

### E16 Provenance and traceability
(a) Derived Q4 fact attributed to DEF 14A and marked authoritative (FTNT fact 183100851); CAT, BKNG, PH, APH, FCX show a proxy filing as the only source; CLX FY2026 NI 601M exists only from 9 facts out of DEF 14A 0001552781-26-000516; market cap with NULL `source_fact_ids` (META(S001), ABNB, NET, CME, DDOG, V); HD, NFLX net income from DEF 14A rounding (S004); TRV/PGR `_resolved` rows lag one filing.
(b) WRONG (small) and traceability.
(e) T11, E2.

---

## 4. Mechanism grouping (AUTHOR'S INFERENCE)

This regroups the symptom themes by what the evidence suggests sits underneath. It is an inference from the digests, not something any worker diagnosed in code, except where a quoted worker wording is noted.

**M1. A line's identity is decided by tag name and priority, not by where it sits in the statement.**
Themes: T1, T2, T6, T11, T12, E3, E5, E12, E14 (and the revenue part of E11).
Why: the same pattern recurs in every digest: the partial tag wins over the total (T1), a derived figure subtracts tags that do not share a perimeter (T2: `OperatingExpenses` that is one caption or excludes COGS), the debt composite sums whatever tag is present (T6), ProfitLoss is a fallback (T11), a combined or alternate tag for capex, D&A and interest is not in the vocabulary (T12, E14), equity and distributions use `PartnersCapital*` (E5). Worker wording: "revenue chosen by tag-name priority, not by the statement's total line". Evidence for the vocabulary aspect: 64% of `core.fact` rows are under unmapped tags (root CLAUDE.md audit).

**M2. Period and fiscal-calendar assumptions.**
Themes: T9, E8, E13, T10 (the restatement-window part), T5 (partly).
Why: calendar year of the period end date used as fiscal year (January, 52/53-week), 16-week quarters stored with NULL `fiscal_period`, transition periods uncollected, Q4 derived by subtraction from a mismatched YTD base, TTM windows rejected for 371 days, recast comparatives covering only a window.

**M3. Cover-page, dimension and share-class handling.**
Themes: T4, E1, E2 (market cap part), E6, E10 (ADS).
Why: class-dimensioned `EntityCommonStockSharesOutstanding` dropped instead of summed; undimensioned facts in multi-registrant filings attributed to every co-registrant; no ADS ratio; cover-date shares never meeting balance-sheet-date equity (D1). The institutional-% guard (E1) fires partly because the share base is wrong.

**M4. Ingestion gaps between the SEC feed, `core.filing` and `core.fact`.**
Themes: T3, E8, E7, E10 (population), parts of E6 and E9.
Why: filings present with R-pages but no facts (companyfacts lacks the accession), filing rows never registered (HPQ, MDB, JKHY, IREN, HEI, SJM, OLLI), no 10-KT rows at all, company/CIK identity drift (EQR, XOM), populations kept by form type without a 20-F/40-F check.

**M5. Coverage and reason-layer logic.**
Themes: T5, T7, parts of T6 (true zero reads as missing), the four universal cells, D1 hidden blanks.
Why: `has_value` read any period while the reason read the latest (changed 2026-10-19), reasons keyed on SIC or a stray tag rather than the statement, absent activity not distinguished from absent input, applicability flags not set for sector-specific concepts.

**M6. Missing presentation and plausibility guards.**
Themes: T8, E1, E2, E15, E12 (suggested gross-margin gate).
Why: no non-positive guard on P/E, P/B, ROE, ROIC; no scale, sign or currency check; the guard that exists (institutional overcount, `peg_ratio` non-positive growth) works, which shows the pattern is available.

**M7. Basis inconsistency and provenance.**
Themes: T11, T10 (mixed bases), E16, E4 (cumulative vs discrete).
Why: consolidated vs attributable, parent vs including-NCI equity, original vs recast quarters side by side, DEF 14A or 8-K copies beating the 10-K, per-share and dollar figures on different bases.

Cross-links: T2 depends on T1 (derived from the wrong revenue); T3 amplifies T5 (a missing quarter leaves old values as "latest"); T4's wrong share counts feed T8 (P/E) and E1; E11 explains many T7 reasons.

---

## 5. Population counts quoted by workers

Contradictions are flagged, not resolved. "Q" = a query or count the worker says it ran; "E" = estimate or inference; "Quoted" = taken from another document.

| Count | What it counts | Shard | Basis | Flag |
|---|---|---|---|---|
| 683 | companies with `institutional_ownership_pct` blank for `implausible:institutional_shares_exceed_shares_outstanding` | S040 "live count"; S050 "683 coverage rows"; S052 "683 companies"; S079 (companies); S088 "683 of 5,206 companies (1,690 blank, 3,516 filled)" | Q | CONTRADICTION in unit: S053 says "683 blank cells across 1,690 companies"; S050 says "rows"; S088 reads as 683 of 1,690 blanks. Not resolved |
| 328 / 1,470 / 203 / 142 | companies carrying the financial-institution reason: 328 companies (S023), 1,470 cells (S052, quoted), 203 coverage rows for `operating_expenses` alone (S050), 142 of 328 non-financial (S023, S041, S101) | S023 Q; others Quoted | Q / Quoted | consistent but different units |
| 168 (103 with a 2026 period) | companies using Revenue minus `OperatingExpenses` for operating_income_resolved | S023 | Q | repeated as Quoted in S040, S069, S080, S100, S101 |
| 189 companies / 789 cells | `reit_net_interest_income_not_revenue` | S055, S079, S091 | Q | |
| 3,433 | `no_dividend_history` on `dividend_growth_streak_years`: "3,433 companies" (S021), "3,433 cells" (S040, DC), "3,433 blank cells" (S094, DE); 502 of them have a dividends_paid value; 3,242 companies with DPS blank and no reason | S021 Q | Q | CONTRADICTION in unit (companies vs cells) |
| 495 / 366 / 1,875 / 464 / 336 / 29 / 65 | `pre_revenue_biotech_pharma`: 495 companies on a blank, 366 with stored revenue (S026); 1,875 blank cells across 495 companies, 464 gross_profit cells, 336 at companies whose revenue cell has a value (S097); 29 above 500M latest revenue, 65 above 100M (S032) | S026, S097, S032 | Q | consistent; different slices |
| 497 vs 477 | companies with blank `shares_outstanding` | S026, S044, S055: 497 (2026-10-20 run); S081: 477 with 270 older than 2025-10-01 and 4,486 current | Q | CONTRADICTION in value (497 vs 477), dates not reconciled |
| 1,634 of 4,287 | stored `trailing_pe` values negative; 450 negative `price_to_book` | S025, S073 | Q | S097 gives 1,642 negative / 2,174 non-negative / 796 null for the latest rows: different filter, not reconciled |
| 167 / 190 / 150 / 27 of 236 | latest 10-Q/10-K filings with 0 facts: 167 10-Qs filed 2026-07-20 to 2026-08-10 (S025); 190 filings, 189 companies, 2026-07-15 to 2026-09-15 (S027, "some will be too recent"); 150 10-Qs 2026-07-20 to 2026-08-05 (S038); 27 of 236 (11%) in a non-random sample (S029) | | Q / E | different windows; not reconciled. S023's own full count timed out at 50 s |
| 6 / 6+ / "at least 10" / "sixth company" | running tallies of 0-facts companies | S050, S056, S014, S077, S079 | E | superseded by the 93 named across digests (author's sum) |
| 213 (79 + 65 + 69) | hidden blanks (value from any period, reason from latest) across 30 companies | S014, S018, S019 | Q | "real" counts about 356 / 398 / 233 quoted; population-wide count not run (55 s cap) |
| 34,290 of 295,966 (4,906 companies) | filled lineage cells with latest period before 2025-07-01 (upper bound) | S027 | Q | |
| 240 / 46 | companies with `diluted_eps` latest before 2025-07-01 / before 2020 | S032 | Q | |
| 224 companies / 322 groups | duplicate fiscal-label groups since 2024-01-01 | S022 | Q | |
| 38 / 43 / 244 vs 35 vs 11 | Q4 ending 2026-01-01..09 labelled FY2026 (38), FY labelled 2025 (43), any period in window (244) (S054); 35 for window 01-01..07 (S086); 11 companies with 105-125 day revenue period and NULL fiscal_period (S030) | | Q | different windows |
| 0 | `10-KT` / `10-KT/A` rows in `core.filing` | S027 | Q | |
| 2,555 / 1,556 / 281 / 4,562 | companies taking revenue from the 606 tag alone (2,555), of which 1,556 have both tags filed (S044); 1,556 of 4,562 with both tags filed and the partial one chosen, 281 with `Revenues` chosen (S047) | | Q | consistent; denominators differ |
| 144 | companies with blank stockholders_equity | S044 | Q | |
| 1,698 | companies with `total_debt` blank and no reason | S044 | Q (method not stated) | |
| 231 of 5,210 | companies whose net_income lineage cites `ProfitLoss` | S062 | stated (method not shown) | |
| 140 rows / 39 companies | `dividends_per_share_resolved` rows with absolute value of 1,000 or more | S096 | Q | |
| 1,300 / 4,351 / 866 / 45 / 10 / 7 | S000: largest active market-cap rows checked (rank 1,300; shard rank 1000 = TFX = overall 1009); non-null and null market_cap rows; rows flagged; wrong market caps confirmed (7 inside the top-1000, 6 overstated, 1 understated, 3 below) | S000 | Q + FC | |
| 13 and 6 | EntityPublicFloat scale errors (10 too large, 3 too small); latent WASO scale errors | S000 | Q | |
| 363 vs 300 | S029: header says 363 blank cells; per-company blanks sum to 300 | S029 | Q | CONTRADICTION inside one file; DB flagged, not resolved. (S027 and S030 also have 363 blanks and match their per-company sums.) |
| 77.7% vs 83.8% | S023 ten companies: 1,267 of 1,630 filled after commit fb26fb6 vs `shards.csv` baseline; unexplained 110 in both | S023 | Q | coverage-rule change, see section 1 |
| about 207 / 402 / 363 / 179 | blanks across ten companies: S010 (BMY 21 not 14), S021, S027 and S030 (S030 with 132 unexplained), S024 | | Q | |
| 62 / 82 | S010 SNR cells; S006 tag-periods with all copies non-authoritative across 8 of 10 companies (ANET 30, MRVL 24, CRM 13, SHOP 8, C 3, KLAC 2, AXP 1, IBM 1) | S010, S006 | Q | |
| 40 universal cells | 10 x 4 per shard; DD quotes 40 of 130, 30 of 190, 40 of 142, 40 of 145 per shard | many | Q | |
| 9-10 of 10 | `employee_count` not tagged per shard; 9 of 10 in S002, S009, S011, S012, S014 (CSX tags it), S018; `EntityNumberOfEmployees` tagged by only 177 companies (S003) | | Q | |
| 15 banks | "15 banks with a wrong net_interest_income value" | S004 | Quoted from another document | |
| `sec_tag_library` reach counts | `InterestExpenseNonoperating` 2,017 active (35,998 facts, candidate); `InterestIncomeExpenseNonoperatingNet` 1,048; `ReceivablesNetCurrent` 739; `AccountsAndOtherReceivablesNetCurrent` 508; `SeniorNotes` 328; `UnsecuredDebt` 299; `Depreciation` unmapped at 3,572; `SalesRevenueGoodsNet` 745; `PartnersCapital` 101; `ConvertibleLongTermNotesPayable` 512; `LoansPayable` 462; `PaymentsForRepurchaseOfEquity` 426; `PaymentsToAcquireOilAndGasPropertyAndEquipment` 60 and `...OilAndGasProperty` 72 | S003, S016, S017, S036 | Q ("not coexistence-checked") | |
| "not run" | reach of every NEW family (ASC 606 precedence, dual-class shares, MLP/LP, ProfitLoss reach beyond 231, currency, HPQ/MDB-style gaps, debt-free wrong-zero audit, business-combination discontinuities, EPS per-class tags, multi-registrant filings, Q4-by-subtraction, HealthCareOrganizationRevenue, Jan/52-53-week labels) | many | not run | no top-1000-wide count exists for any family except S000's market-cap pass |

Worker-tallies inside a shard (E, not population): "6 of 10 in S060 have a total-debt problem", "8 of 10 ebitda `missing:4_consecutive_quarters` (S068)", "4 of 10 institutional overcount (S074)".

---

## 6. History-window findings

No worker ran the planned systematic checks of first period held vs filing history, FY2015/2018/2021, or missing quarters inside the last 8 across the board. FY2015: no worker in any block opened or recalled a FY2015 filing as a labelled check. What exists, per company (FC unless marked; "mem" = from memory, DI):

**Wrong or broken early history (FC unless noted).**
- ELS FY2018 15,191,000 vs 986,653,000 (S065, DD). APTV FY2010 29,000,000 vs 13,817,000,000 (S076). ZION FY2018 412M vs `Revenues` 508M / `InterestAndDividendIncomeOperating` 2,481M (S076). ALLY FY2021 852M vs 8,428M (S066, 10-K FY2023 R3). GLPI FY2021 109.7M vs 1,216.4M (S066). UDR FY2021 6,102K (S067). CNA FY2021 1,430M vs about 11B (S061, mem). FNF FY2018 2,216M and FY2021 2,821M vs 11,752M-14,445M (S069). OSCR FY2021 5.4M (S070). CPT 2018 7.2M, 2021 10.5M (S072). CFR FY2018 85.2M, FY2021 83.3M (S074). VOYA FY2018 1,426M, FY2021 1,984M (S079). COLB FY2021 83.3M (S082). LNC FY2018 and FY2021 (S084). CHE FY2021 1,261.2M vs filed 2,139.3M (S090). LYFT FY2018 and FY2021 (S093). CWEN FY2018/19 and ENS FY2012-FY2020 (S095). GBCI series broken in 2021: 627M FY2020 then 65M FY2021 (S099). CTRE FY2018 3,379K, FY2021 0, FY2025 1,225K (S078). JEF FY2021 6,141,801 vs SEC `Revenues` 8,945,464 (S071). DOC FY2018 144.2M (S060, mem). TFX recast FY2025 1,992.7M below its own 9M YTD 2,394.6M (S100). FLR FY2021 14,156M (recast) vs originally filed 12,435M, FY2020 and FY2018 match neither (S094). LNC FY2021 19,862M matches neither as-filed 19,230M nor restated 17,715M (S084).
- PLXS negative annual revenue FY2011-FY2014 (-229,001,000; -154,844,000; -103,592,000; -108,372,000) (S095, DI).
- ASB mixes bases: FY2023 net 1,102,756K vs 10-K gross 1,958,052K (S101).

**First period held vs earliest filing.** XBRL-era limit is expected (stored history starts about 2008-2011 where 10-Ks go back to 1993-1996). Flagged as unexpected:
- Gaps or late starts: MLI annual revenue absent 2009-2015 (S060); EHC gap 2008-2015, `HealthCareOrganizationRevenue` unmapped (S062); TOL FY2010-FY2016 revenue missing though `HomeBuildingRevenue` is in `core.fact` (S063); DECK FY2008-2016 missing (S065); AOS 2009-2015 missing (S081); MHK 2009-2010 missing (S081); FR FY2009-2015 absent and quarterly rows before 2017 absent (S083); AGCO and ARE start 2016-12-31 vs 1996/1997, 2009-2015 absent (S086); TAP 2009-2015 missing (S085); ACM 2009-2016 missing (S085); DY none before FY2016 (S084); CVI from 2016 vs 2008 (S094); MOS 2018-12-31 earliest, 2005-2017 absent (S096); AMG, CPT, TTMI start 2016/2017 although XBRL exists from about 2009 (S072); HXL and STAG start 2016 (S089); AMH 5 FY, revenue chain ends 2020 (S067); UHS three years later than peers (S067); FHN FY2020 and FY2021 annual revenue missing (S068); NPO FY2020 and FY2021 missing (S096); SWK FY2010-2014 and PAG FY2009-2014 missing (S058); DVA 10 FY though filings go back 24 years (S064); LFUS 20 FY rows over 16 years, FY2021 absent (S074); AXSM, HUT plausible (S080).
- Late starts explained by registrant or IPO: AEM FY2009-2013 only (S014); XOM from Q2 2026; AVGO (2016_Q3 base missing); SPCX one 10-Q; INIO only Q2 2026; JAN first filing Q2 2026; SN, JHX, IREN 20-F to 10-K; HONA no history; PSKY FY2025 absent; EAI no FY revenue (32 10-Ks, none with facts); BAM from 2022-12-31; SFD 2023 vs 1994.
- `Piotroski missing:total_assets(2025)` while 2025 total assets are stored (HIG, PG).

**Missing quarters inside the last 8.**
- Revenue or other series: LLY 2025 Q2/Q3 (H1-2025 duplicates 1,665.6M vs 1,666M and others non-authoritative) and FY2024 balance sheet absent (S001); GOOG H1-2025 buybacks 28,706M (0001652044-25-000062) vs 28,306M (0001652044-26-000071) both non-authoritative (S001); ANET whole 2024-12-31 balance sheet (30 tag-periods) and MRVL FY2022 quarters (S006); AMT Q3/Q4 2025 buybacks; CEG Q1 2026 buybacks; WM, CMI (S014, S019, S016, S013); CSGP Q1 and Q2 2025 revenue (S060); TXT Q3/Q4 2025 EPS (S060); HL Q1 and Q2 2025 revenue (S071); JAZZ 2025 Q1 and Q2 (S059); PAG 4 of 8 quarters (S058); AMRZ Q1 2026 and 2025 Q1/Q2 (S046); IFF Q2 2025 (S043); DD no standalone Q3 2025 (S050); SN no Q3/Q4 2025 (S039); JHX no Q2-Q4 FY26 (S055); PNFP Q3/Q4 2025 and FY2025 (S057); PSKY all 2025 quarters; ETSY Q1/Q2 2025 (S083); COLB Q1/Q2 2025, CBC Q3/Q4 2025 (S082); TFX 5 of 8 quarters (S100); MSCI 2025 Q2 comparatives (S028); ALNY 2025 quarters (S035); BAH 2024-09-30, 2024-12-31, 2025-03-31 (S077); OC 2024-12-31 (S077); AEIS 2023Q1-2024Q4 (S074); CUBE 1, HLI 1 (S077); MLM Q1 and Q2 2025 (S036); RPM holds 9 quarters (S062).
- Latest quarter absent: see T3.
- Mid-history series stopping while the line still exists (DI): KMB AR/AP/inventory FY2023/2024 (S032); STLD AR/AP FY2024; PAYC AR; DVN AP 2020; ROK 2024; SPGI inventory last 2012; NKE shares one 2015 value; CVNA shares 0 at 2017; TW shares 0 at 2019; TFC/CFG/MTB/ED capex dead since 2022/2019/2023/2022; NVDA fcf_growth_5y capex FY2021 missing in 0001045810-21-000010, -22-000036, -23-000017 (S001); KO quarterly revenue 2015-Q1 2016 filed only under unmapped `SalesRevenueGoodsNet` (S003).
- Label breaks that make quarters unfindable: TEL (duplicate Q1/Q2 across FY2024 and FY2025, S022), NUE (2026 labelled 2027), FERG, KR (S030), QXO (Q3 2025 stored as Q2, S066), ONTO (2025Q3, 2026Q4, 2026Q1, 2026Q2), MU 53-week not checked, TGT and LITE 53-week handled correctly (S019, FC).

**FY2018 / FY2021 spot checks (mostly mem).** S058 (mem): HAS 6,420.4M, TRMB 3,659.1M, PAG 25,554.7M, AIZ 10,187.6M, NBIX 1,133.5M, HALO 443.3M, GWRE 743.3M, DOCU 1,453.0M, SWK FY2020 14,534.6M, OHI 1,062.8M. S059 (mem): BF-A 3,248.0M/3,461.0M, CACI 4,467.9M/6,044.1M, SJM 7,357.1M/8,002.7M, REG 1,121.0M/1,166.2M, MAA 1,571.3M/1,778.1M, GDDY 2,660.1M/3,815.7M, JAZZ 1,890.9M/3,094.2M, GME 8,547.1M/5,089.8M. FC via SEC API or companyfacts: GAP FYE Jan-2021 13,800 and Jan-2022 16,670; AOS FY2018 3,187.9 and FY2021 3,538.9; MHK FY2021 11,200.6; AVT FY2025/FY2024; VFC FY2024/FY2025; AIT FY2025 4,563,424 and FY2024 4,479,406; BSY FY2021 965,046; ONB (3,269.9 / 2,601.7 / 2,206.8) and WMS. Not done: S000-S057 as a labelled check; S087, S088, S092, S097, S100, S101, S102.

---

## 7. The 20 largest companies that came out CLEAN or closest to CLEAN

**Plainly: very few.** Under the strict rule (no wrong value found AND no unexplained blank except the 4 universal cells), no digest worker certified any company as clean. Eight were labelled CLEAN by a digest and also have a `shards.csv` baseline of four or fewer unexplained cells (AAPL, LRCX, WAB, KDP, LHX, NTAP, FLS, COO). About 22 more had no wrong value found with the same unexplained count but were labelled NOT CLEAN for a wrong reason, label or history gap. All of these are weakly evidenced: every worker opened the latest 10-Q only, the FY2025 10-K usually not, and the early-shard ones (AAPL, LRCX) are DATA-INFERRED. `shards.csv` unexplained counts are the pre-2026-10-19 baseline (section 1), so a post-rebuild recount could differ. The mcap ranking uses `mcap_bn` from `shards.csv` (a market cap that DA/DB found unreliable for 10 rows, none in this list).

Companies below are ordered by mcap_bn; "unexpl." is the `shards.csv` baseline.

### 7a. Strict CLEAN or the nearest (no wrong value found, baseline unexplained 4 or fewer): 20 largest

| # | Ticker | Shard | mcap_bn | Unexpl. | Digest label | Evidence | Residual (from digest) |
|---|---|---|---|---|---|---|---|
| 1 | AAPL | S001 | 5000.3 | 4 | CLEAN (DA, derived) | DI only | 6 total blanks (4 universal + 2) |
| 2 | LRCX | S004 | 332.2 | 4 | CLEAN (DA, derived) | DI only | 4 total blanks, all universal |
| 3 | WAB | S026 | 48.4 | 4 | CLEAN (DB, derived) | latest 10-Q headline read (digest does not isolate WAB) | none beyond universal |
| 4 | KDP | S026 | 47.1 | 4 | CLEAN (DB, derived) | same | acquisition jump in assets/revenue is real |
| 5 | LHX | S027 | 46.2 | 3 | CLEAN (DB, derived) | same | NI 600M vs 586M noted (low); predecessor-identity history |
| 6 | NTAP | S029 | 39.8 | 4 | CLEAN (DB, derived) | same | institutional-% guard fired (E1) |
| 7 | KVUE | S031 | 36.2 | 4 | NOT CLEAN borderline (DB) | same | history-limit reason wording (E9) |
| 8 | EME | S034 | 31.8 | 4 | NOT CLEAN borderline (DB) | same | inventory unmapped |
| 9 | WST | S038 | 27.0 | 4 | NOT CLEAN borderline (DB) | same | institutional guard (E1) |
| 10 | DOV | S038 | 26.4 | 4 | NOT CLEAN borderline (DB) | same | wrong reason; pretax unmapped (E14) |
| 11 | ATI | S040 | 25.3 | 4 | NOT CLEAN (DC, rule) | latest 10-Q | none listed |
| 12 | SNX | S047 | 19.7 | 4 | NOT CLEAN (DC, rule) | latest 10-Q | none listed |
| 13 | CRS | S048 | 18.7 | 4 | NOT CLEAN (DC, rule) | latest 10-Q | false financial-institution reason; cover label FY2027 |
| 14 | RVTY | S052 | 17.0 | 4 | NOT CLEAN (DC, rule) | latest 10-Q | gross profit blank with "not presented" though derivable (E14) |
| 15 | WCC | S052 | 16.6 | 4 | NOT CLEAN (DC, rule) | latest 10-Q | same gross-profit item (E14) |
| 16 | RBC | S054 | 15.8 | 3 | NOT CLEAN (DC, rule) | latest 10-Q | capex(2026) absent |
| 17 | MKSI | S056 | 14.5 | 4 | NOT CLEAN (DC, rule) | latest 10-Q | none listed |
| 18 | GEN | S057 | 14.5 | 4 | NOT CLEAN (DC, rule) | latest 10-Q | possible quarter-label shift (DI) |
| 19 | LECO | S057 | 14.3 | 4 | NOT CLEAN (DC, rule) | latest 10-Q | none listed |
| 20 | AIT | S063 | 12.1 | 4 | NOT CLEAN (DD: "closest to certifiable") | latest 10-Q; FY2025/FY2024 revenue FC against FY2026 10-K | dividend-yield reason untruthful |

Smaller ones that also fit (below the top 20): COO(S068, 10.9B, DD "CLEAN on values"), FLS(S077, 9.0B, DD "CLEAN: only the 4 universal cells"), TKR(S083, 7.8B, DE "CLEAN on values"), SSD(S086, 7.2B, DE "CLEAN apart from the universal 4"), AEIS(S074, 9.5B, quarterly revenue 2023Q1-2024Q4 missing), GNRC(S066, 11.3B), FSS(S089), ESE(S092), POWL(S096), NPO(S096, FY2020/21 missing). Not included though no wrong value was found: TPR(S042, 24.1B, ROE 221% flagged plausible) because the digest carries it with a flagged ratio.

### 7b. Larger companies where no wrong value was found but unexplained blanks exceed the universal four (so not strictly CLEAN)

| Ticker | Shard | mcap_bn | Unexpl. (baseline) | Digest note |
|---|---|---|---|---|
| GOOG | S001 | 4157.7 | 7 | CLEAN (DI, open conflict): H1-2025 buybacks 28,706M vs 28,306M, both non-authoritative; 20 total blanks |
| MSFT | S001 | 3912.0 | 6 | CLEAN (DI); 13 total blanks |
| AMZN | S001 | 2685.6 | 11 | CLEAN (DI); 18 total blanks |
| PLTR | S003 | 442.2 | 14 | CLEAN (DI); population bug (dividend_family_ever_reported) |
| COST | S003 | 437.5 | 8 | CLEAN (DI); TTM fails on 52/53-week (10 blanks) |
| CAT | S004 | 335.8 | 9 | CLEAN (DI); provenance only (DEF 14A source) |
| AMAT | S004 | 325.0 | 7 | CLEAN (DI) |
| TXN | S005 | 252.5 | 11 | CLEAN (DI) |
| LIN | S006 | 228.6 | 8 | CLEAN (DI) |
| SNDK | S007 | 189.2 | 13 | CLEAN (DI) |
| BLK | S007 | 175.4 | 22 | CLEAN (DI); predecessor history cut |
| MSI | S018 | 76.8 | 7 | CLEAN, the only FILING-CHECKED one (DA): headline and debt FC; interest current |
| FDX, COR, GWW, AON, TRGP | S020-S021 | 69.1, 65.1, 62.7, 62.0, 62.0 | 12, 8, 5, 13, 9 | NOT CLEAN borderline (DB): no wrong value found |
| NVDA | S001 | 5151.4 | 4 | NOT CLEAN: total_debt base vs resolved disagree (possible double count) |
| CSCO | S003 | 422.0 | 3 | NOT CLEAN: total_debt, D&A 700M suspect |

---

## 8. What this document does not tell you

- **No root cause was confirmed in code.** The mechanisms are workers' wording or the author's inference (section 4). Nothing was reproduced.
- **No top-1000-wide count for any theme.** Except S000's market-cap pass (1,300 rows) and a few coverage-table queries (section 5), every defect family has a shard-level sample only. The company counts in section 3 are sums of per-shard tallies, overlap, and cannot be read as a population rate.
- **Weak evidence for the earliest shards.** S001-S011 (and S010 before its rerun) are DI only. A CLEAN verdict there means "no problem seen in our tables".
- **Latest-quarter bias.** Most FC checks compared the latest 10-Q headline (revenue, net income, EPS, assets, equity). FY2025 10-K headlines, FY2015/2018/2021 history, restated comparatives, and older quarters were rarely opened. The history findings in section 6 are therefore skewed toward what workers happened to notice.
- **Rules differ across digests.** DA's CLEAN ignores non-universal blanks; DB's rule is stricter; DC and DE mark every company NOT CLEAN; DD uses file wording. The strict list in section 7 is the author's cross-check of the digest labels against `shards.csv`, not a worker verdict.
- **Baseline vs current coverage.** `shards.csv` unexplained and filled counts predate the 2026-10-19 `has_value` change. No post-change recount was run for most shards (S023 is the exception).
- **Not investigated by anyone:** the cause of the institutional-overcount cases (E1), the stale-versus-missing split for most DI items, whether a 0-fact filing sits in companyfacts, the derived-Q4 root cause beyond the cases named, the reach of the multi-registrant defect (E6), the reach of the currency defect (E15), and which of the 10-Q "stale" blanks are legitimate history limits.
- **Excluded or unreliable rows:** 28 `shards.csv` rows are flagged excluded; their verdicts are NOT CLEAN by construction. Market caps for 10 rows are known wrong (S000) and several more are on a questionable share basis (T4), so any ranking by mcap_bn carries that caveat. The S101 backfills and S102 names have no usable market cap today.
- **Digest-level inconsistencies left unresolved:** the 683 unit (companies vs cells vs rows), 3,433 (companies vs cells), 497 vs 477, S029's 363 vs 300, 1,634 vs 1,642 negative P/E, 38 vs 35 vs 43 vs 244 January-window counts, and whether companyfacts staleness explains the 0-fact cases (SPGI/NEE refetched after the 10-Q date).
- **Findings only.** No ordering of severity across themes by users' impact was done beyond the cell-severity labels; that ranking is for the product and engineering teams.
