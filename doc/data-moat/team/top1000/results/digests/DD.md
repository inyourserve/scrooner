# Digest DD (block D): shards S060 to S079

Read-only synthesis of the shard result files. Findings only, no fixes. Labels FILING-CHECKED (FC) and DATA-INFERRED (DI) are the workers' own. Accession numbers are copied from the files.

## Block
Read in full: S060.md, S061.md, S062.md, S063.md, S064.md, S065.md, S066.md, S067.md, S068.md, S069.md, S070.md, S071.md, S072.md, S073.md, S074.md, S075.md, S076.md, S077.md, S078.md, S079.md (20 files, 200 companies, 10 per shard). No file missing. No file partial in the sense of truncation; each file lists its own "not done" items (the common ones: no FY 10-K headline check for most companies, only the latest 10-Q; most blank reasons accepted as SNR, statement not opened; FY2018/FY2021 history spot checks mostly from the worker's memory, not an opened filing; very few population counts run). Market-cap bands per shard as the files state them: S060 12.4B to 13.5B, S065 11.3B to 12.7B, S066 10.9B to 12.5B, S070 10.4B to 11.4B, S072 9.8B to 10.2B, S077 8.8B to 9.3B. No file gives a rank number.

Cross-cutting observations that recur in nearly every shard (counted once here, referenced by theme below):
- The four "universal" cells `bdc_total_investment_income`, `collaborative_arrangement_revenue`, `net_lease_revenue`, `employee_count` are blank with no reason at (almost) every one of the 200 companies (workers say 4 per company, BAH 3, CSGP shows net_lease_revenue filled, MDGL variant noted). They alone make every company NOT CLEAN under the strict rule. Quoted as 40 of 130 (S064), 30 of 190 (S061), 40 of 142 (S068), 40 of 145 (S079) unexplained cells per shard.
- `book_value_per_share` is blank (`incomplete:numerator` or `incomplete:denominator`) at 10 of 10 in S060, S062, S064, S068, S071, S072, S074, S077; 9 of 10 S076; 8 of 10 S073, S075, S078, S079; 7 of 10 S061, S069, S066. Equity is present and FC-matched in every case the worker opened. Workers call this the "D1" family (balance-sheet-date equity paired with cover-date share count).
- `institutional_ownership_pct` blank with `implausible:institutional_shares_exceed_shares_outstanding` appears in most shards (see T14).

## T1. Revenue resolves to a partial/sub-line tag instead of the statement total

Companies affected: 27 (22 FC, 5 DI) plus 1 definitional case.
- FILING-CHECKED (22): DOC(S060), CNA(S061), AHR(S065), ALLY(S066), GLPI(S066), UDR(S067), SF(S068), RYAN(S068), FNF(S069), OSCR(S070), ENSG(S071), JEF(S071), RRC(S072), CPT(S072), CFR(S074), FCFS(S075), ZION(S076), CTRE(S078), PCTY(S078), VOYA(S079), VNOM(S079), WTFC(S073, annual value only; quarters use a different tag).
- DATA-INFERRED (5): BPOP(S072), UMBF(S072), SSB(S072) (source tag `InterestAndDividendIncomeOperating` = gross interest income, filing line not opened); ELS(S065, FY2018 duplicate same-tag fact 15,191K beat the 986,653K total); APTV(S076, FY2010 stored 29,000,000 vs `SalesRevenueGoodsNet` 13,817,000,000 in core.fact accession 0001521332-13-000010).
- Definitional (not a mismatch with the face): SM(S075, stored = "Total operating revenues and other income" 2,500 includes a 262 gain on divestiture; production revenue is 2,156); EVR(S069, stores Total Revenues 998,497, statement leads with Net Revenues 990,199).

Cells: wrong values shown, in every period back to the first year, plus all revenue-driven ratios. Worker-quoted consequences: UDR price_to_sales 945.75 (about 6 expected); OSCR price_to_sales 378.96 (about 1); CPT net_margin 6.00 (600%) and price_to_sales 761.9; ZION net_margin 321% and price_to_sales 17.4; ALLY price_to_sales 9.41 (about 1.3); CFR price_to_sales 74.59 (about 4 to 5); CTRE price_to_sales 31.1; CPT/UDR/CTRE FY history wrong. Count of cells not stated beyond that.

FC exemplars:
- CNA: stored Q2 2026 revenue 367M vs filed Total revenues 3,829M (6M 741M vs 7,506M); FY2025 stored 1,577M vs about 14B; chosen tag `RevenueFromContractWithCustomerExcludingAssessedTax` while `Revenues` is also filed (S061).
- OSCR: stored 6,095,000 Q2 / 11,813,000 H1 vs filed 4,880,220K / 9,527,414K; core.fact holds `Revenues` = 4,880,220,000 authoritative (S070).
- FCFS: stored FY2025 1,668,410 equals only "Retail merchandise sales" in the FY2025 10-K R5; 10-Q total revenue 1,074,688 vs stored Q2 471,263 (S075).
- Also DOC stored Q2 216,456K = "Resident fees and services" vs Total revenues 771,579K (0001628280-26-053373); AHR 634,519K vs 674,250K; JEF 1,751,808 vs Revenues 3,230,798 / Net revenues 2,221,934 (FY2021 stored 6,141,801 vs SEC `Revenues` 8,945,464).

Mechanism (workers' wording): "revenue chosen by tag-name priority, not by the statement's total line" (S061, S063, S065, S068, S070, S072, S075, S078, S079). Variants: bank revenue = gross interest income or a fee sub-line (CFR "Service charges on deposit accounts"; ZION fee income); WTFC annual period resolved per period by tag availability while quarters use another tag (annual 14x below filed total interest income); GLPI in the year the filer split a component line the chosen tag became the component (FY2021 109.7M vs 1,216.4M); RRC derivative fair-value income inside "Total revenues and other income" is dropped. No worker ran a population count for this family.

## T2. Operating income derived or taken from a non-face line

Companies affected: 7 FC.
- FILING-CHECKED: AHR(S065), MOG-A(S065), EVR(S069), AMG(S072), FCFS(S075), VOYA(S079), AFG(S063).
- DATA-INFERRED: none stated separately. S069 quotes "168 companies derive this way" (taken from S023, not rerun).

Cells: operating_income_resolved shown as a wrong value, with operating_margin, roic, ebitda ratios inheriting. Per-period counts not stated.

FC exemplars:
- AHR: stored 137,239K Q2 = total revenues 674,250 minus Property operating 524,838 minus Rental expenses 12,173, dropping G&A, D&A (72,125K) and restructuring; AHR presents no operating income; revenue less Total expenses = 42,437K (S065).
- EVR: stored 154,874K Q2 = `Revenues` minus `OperatingExpenses`; `Revenues` is gross of the 8,298K Q2 interest expense the statement deducts to reach Net Revenues; 998,497-843,623=154,874 vs 990,199-843,623=146,576 (S069).
- AFG: stored 316 / 555 equals "Earnings before income taxes" (R4); AFG presents no operating income, so operating margin 15.6% is a pretax margin (S063). MOG-A: stored 176,270K Q3 is "Total operating profit" from the Segments note (R24); statement has no operating income line (S065). FCFS: 1,074,688-285,619-406,667=382,402 vs pretax 127,002 (S075). AMG: 640.7-486.7=154.0 where expenses include 40.5M interest and equity income 124.9M sits below the line (S072). VOYA: stored -367M Q2 (subset revenue minus OperatingExpenses) while net income is +18M consolidated (S079).

Mechanism: "operating income resolved from the nearest subtotal when no operating-income line exists" (S063); "`Revenues - CostOfGoodsAndServicesSold - OperatingExpenses` assumes the three tags share a perimeter" (S075); derived from a partial expense set or segment note (S065). Workers flag several of these as needing a Standardization ruling.

Related, listed under other themes: stale operating-income values kept as "latest" (T5); filers that correctly present no operating income but show no reason (T7).

## T3. Latest 10-Q/10-K has 0 facts in core.fact, or filing absent from core.filing

Companies affected: 18 with 0 facts, 2 with filing absent, 1 false positive.
- FILING-CHECKED 0 facts (17): SMTC(S062, 0000088941-26-000034), LII(S063, 0001069202-26-000087), ELS(S065, 0001628280-26-050244), UDR(S067, 0000074208-26-000073), AVTR(S067, 0001628280-26-050415), KNX(S070, 0001492691-26-000059), AMKR(S070, 0001047127-26-000046), CLX(S070, 10-K 0000021076-26-000034), OGE(S073, 0001021635-26-000025), ONB(S073, 0000707179-26-000046), LFUS(S074, 0001628280-26-050481), RMBS(S075, 0001193125-26-321000), FRT(S076, 0000034903-26-000042), VICR(S076, 0001193125-26-322462), CUBE(S077, 0001298675-26-000038), ESI(S079, 0001590714-26-000065), PNR(S079, 0000077360-26-000045).
- EAI(S078): latest 10-K 0000065984-26-000174 and Q1 10-Q -000222 show 0 facts under EAI (combined Entergy filing); only Q2 has 467 facts; FC that R-pages exist.
- Filing absent from core.filing (FC): JKHY(S068, FY2026 10-K 0000779152-26-000067 filed 2026-08-28, in SEC submissions fetched 2026-10-04, not in core.filing; last JKHY row is an 8-K of 2026-08-18); IREN(S074, FY2026 10-K 0001878848-26-000052 filed 2026-08-27, absent; company moved from 20-F to 10-K).
- False positive: BWXT(S063): original 10-Q 0001486957-26-000042 has no XBRL and 0 facts, but the 10-Q/A 0001486957-26-000044 carries 428 facts and is what the pipeline uses. Worker says do not count it; refine the population count to exclude filings superseded by an amendment with facts.
- Clean for this theme: all ten latest filings had facts in S061, S064, S066, S071, S072 (workers state so).

Cells: whole latest quarter or FY missing; every TTM metric one quarter (JKHY, IREN about two quarters) stale; trailing_pe built on stale TTM EPS: KNX 303.8, AMKR 24.03, LFUS -227.15, IREN 40.52 and ROE +5.93% (FY2026 net loss 702,621K), VICR 68.1 and price_to_sales 22.6, CLX 14.19 (filed FY EPS 4.81, expected about 18), RMBS 44.2, ESI 57.5. AMKR total assets stored 8,298,634K vs filed 9,716,114K.

FC exemplars: LII Q2 filed net sales 1,545.3, op income 355.0, NI 269.0, EPS 7.72 vs stored latest Q1 revenue 1,135.1 (S063). JKHY FY2026 revenue 2,544,339K, NI 502,776K, EPS 6.98 vs stored latest Q3 FY26 (S068). CLX FY2026 net sales 6,720M, NI 601M vs stored 9M revenue 4,772M; FY2026 NI 601M and Q4 177M exist only because 9 facts come from DEF 14A 0001552781-26-000516 (S070).

Mechanism: "filing ingested but fact load produced nothing, no retry" (S063); for FRT and VICR SEC companyfacts also carries 0 facts for the accession (S076); JKHY/IREN: "never registered in core.filing" / "collector/refresh gap" (S068, S074). No population counts run (S079: "now 6+ large names"; S077: "sixth company seen across the campaign").

## T4. shares_outstanding blank/stale/wrong, market cap on wrong share basis, per-share cascade

Companies affected: about 34 for shares (multi-class or dimension issues), plus market-cap-basis cases, plus D1 across nearly all.
- FILING-CHECKED (cover or balance sheet read): MKC(S063, Common 14,522,864 + Non-Voting 254,541,615 = 269,064,479, blank in every period), ASTS(S064, three classes 389.2M; shares blank, market cap 12,255,992,507 = 294,898,761 x 41.56 vs 16.2B on cover total, 12.46B on Class A), WTS(S064, Class A 27,466,760 + Class B 5,916,290), WSO(S066, 35,588,756 + 5,663,438 = 41,252,194; market cap 11,506,312,319 implies 38.19M, matches neither), HRL(S067, cover per-class, one class 0), SF(S068, shares 69,584,449 dated 2019-08-01 vs cover 151,001,734; market cap 10,850,613,000 implies 162.6M shares, 7.7% above cover x 66.75), NYT(S068, Class A 160,502,862 + Class B 780,724; market cap sums them correctly), GSAT(S069, 126,442,583 dated 2025-02-11 vs cover 129,563,390 + 149,425; market cap 2.5% low), EVR(S069, Class A 38,457,778, no value ever), BSY(S071, 11,515,127 + 290,577,762), PBF(S072, Class A 118,536,838; no `EntityCommonStockSharesOutstanding` row in core.fact at all), BIO(S074, 21,677,137 + 5,061,038), DKNG(S075, 496,454,048 + 393,013,951), VNOM(S079, two cover values 194,405,049 and 164,789,844; market cap 8.58B printed with shares blank), GL(S061, balance-sheet shares 92,218,183 = issued; cover 78.6M / 76.8M; 15.16M treasury).
- DATA-INFERRED: AMH, ERIE, FIG, UHS(S067), RYAN(S068, 109,903,867 dated 2021-09-01 kept as latest), OSCR(S070), DDS(S070, Class A/B), HLI, GTLB, TXG(S077, TXG shares stop at 2025-12-31), CHWY(S078, latest value 100 dated 2019-06-17), W and MOG-A(S065, two-class cover inferred, cover R1 not opened), WMS(S073: balance sheet 71.32M vs cover 75.4M incl 4.42M mezzanine ADS; market cap uses the larger; "defensible but not documented").
- Other wrong-basis cases: SCNI(S069, market cap 9.78B and price_to_book 1,207 from 13,872,899,584 ordinary shares x ADS price; 20-F filer; true cap about 0.003B per the lead's note); EAI(S078, market cap 8,590,685,878 = parent's 466.6M shares x about 18.41 price of a different security); INIO(S063, stored 750,000,000 equals diluted weighted average, cover not checked); WTS market cap 358.19 x 33.5M weighted vs 33.38M cover (0.3%, immaterial).
- Date-label cases: DCI(S071) and PCTY(S078) cover-date shares labelled with the next fiscal year.

Cells: shares_outstanding(+_resolved) blank or stale, plus roughly 6 to 12 dependent cells each: book_value_per_share, net_cash_per_share, fcf_per_share, diluted_shares_growth_yoy/3y/5y, share_dilution_trend, total_shareholder_yield, piotroski_f_score, institutional_ownership_pct. Examples: MKC about 11 cells; WTS about 12; EVR about 10; ASTS 9 named.

D1 per-share pairing: book_value_per_share / net_cash_per_share / piotroski blank because shares sit at the cover date and equity at the balance-sheet date. Counts above in the cross-cutting section. Workers note negative-equity companies (MTCH, IBRX, DVA, CYTK) show `incomplete:numerator` instead of "not meaningful".

FC exemplars: SF cover Common Stock [Member] dimension keeps only the 2019 undimensioned value (S068); GL filer tags outstanding equal to issued (S061); HRL cover R1 lists "Common Stock $0.01465 par" 550,350,800 and Nonvoting 0 (S067).

Mechanism: "class-dimensioned dei fact dropped instead of summed" (S063); "collector keeps only the undimensioned value" (S068); "no cross-check of outstanding vs issued minus treasury" (S061); market cap "falls back to H1 weighted-average diluted shares" (S064, inferred from the exact product). No population counts run.

## T5. Stale series counted as filled

Companies affected: about 20 where the worker states the cell counts as filled / `has_value=true` on an old latest period.
- FC or lineage-read: ASTS(S064, EPS latest 2022-09-30, filing shows (0.77) Q2 2026), SF(S068, operating_income only FY2024 928,444K; shares 2019), RYAN(S068, shares 2021), ELAN(S065, operating_income_resolved last 2020-12-31 56,700,000, with false reason `pre_revenue_biotech_pharma`), SMMT(S065, last FY2024 -225,998K), BXP(S075, op income 2018-09-30: 677,140 vs 238,364), WTFC(S073, 2014-09-30 113.3M), CTRE(S078, operating_income_resolved 2019-09-30), TXT(S060, 2011-07-02), CHWY(S078, shares 100 in 2019), JEF(S071, current_ratio FY2012 1.97, gross_margin 52.6% for a broker-dealer).
- Stale inputs behind blanks (not always called has_value): total_debt stale at MLI (2022-12-31, 2.7M vs 5,243K filed), CG (2022-09-30, 2,235M), SGI (4,606.7M at 2025-12-31 vs face 4,685.7), SCNI (2022-12-31), ERIE (40M from 2022); capex stale at DOC (FY2025), BAX (2025-12-31), CTRE/UDR/RRC/ENSG (2019), AR (2023-03-31), FNF (2015-03-31), GSAT (2019-12-31), VOYA (2017), AMH (2013), FCFS (2025), GLPI (Q1 2026 only); BWA cash (2025-12-31 vs 2,448 filed).

Cells: single cells shown as values or counted filled while the latest period is 1 to 12+ years old; downstream blanks cascade. Counts per company not stated.

Mechanism (workers): "coverage looks at any period, not the latest, in lineage" (S064); "the coverage rule 'latest period must have a value' is not enforced for this concept" (S068); "no staleness cut-off on non-TTM cells" (S075); `_resolved` concept ignores the latest-period rule (S065). Coverage-rule problem plus the old tag no longer being filed.

## T6. True zero shown as blank; total_debt unmapped, wrong or stale

Wrong values shown (FC):
- AVY(S060): total_debt 500.5M (current portion only) vs 500.5 + 3,177.7 = 3,678.2M.
- BAX(S060): total_debt 0 (bare `ShortTermBorrowings`=0) vs 844 + 8,615 = 9,459M.
- SGI(S060): 4,606.7M at 2025-12-31 and nothing for 2026-06-30; face 4,685.7 and 4,408.5.
- AKAM(S062): debt_to_equity 1.2335 (5,857.3 non-current only) vs about 1.59 (current convertibles 1,705.6 omitted); total_debt blank.
Blank where debt exists (FC unless noted): GGG(S060, notes payable 28,128K + current portion 1,104K), TXT(S060, group-level lines only; Manufacturing current portion 355, long-term 3,111), TECH(S066, `LongTermDebtAndCapitalLeaseObligations` 200,000K; 346,000K a year earlier), AES(S069, Short-Term 300, LT 5,800 recourse + 3,162 non-recourse), CUBE(S077, about 3.5B of notes, revolver, mortgages, finance leases), AKAM, PEN(S062, only finance leases about 22.0M), CFR/ORI/PRI/IREN/DKNG/IBRX/AHR/ELS/AMG/PSKY/DKS (DI: debt expected, tag not found), MLI/CG/SCNI stale.
True zero blanked, FC that no debt line exists: IONQ(S064), CART and HUBS(S066), PEN. Suspected true zero (DI): MANH, BMNR, FN, NXT, SMMT, NYT, ERIE, ALGN, FROG, GMED, LULU, PCOR, KYMR, GTLB, TXG, HLI, RMBS, PCVX, CGNX, VICR, ONTO, AUR, FIVE, GKOS, CORT, SAIL, FIG, DECK, AMKR, SSB (zero_debt missing), AMG.
Related zero cases: missing dividend or buyback not treated as zero so `cash_returned_to_shareholders` is `incomplete:add` (DVA, BTSG, IONQ, CORT, CR, WTS, ASTS, IT, EVR); SEIC Q1 2026 DPS absent should be zero so TTM fails; AM no property-additions line in H1 2026 (FC) but nine FCF cells blank with `missing:capex` instead of zero/not presented; SGI buyback series ends 2022-09-30 with no 2026 repurchases (treasury shares unchanged 73.9M) so buyback cells blank instead of zero.

Cells: total_debt, total_debt_resolved, total_debt_split, zero_debt, debt_to_equity, net_cash, net_cash_per_share, roic, debt_to_ebitda, net_debt_ebitda, piotroski, interest_coverage_ratio: typically 7 to 12 per company.

Mechanism: "total debt built from the one bare short-term line that happens to be zero" (S060 BAX); "debt composite picks only the non-current notes tag; current convertibles not in the tag list" (S062); "no filed debt line means no fact, which reads as missing instead of zero" (S064); "a missing debt tag is treated as unknown, not as zero with evidence, and a stale period is still used as the latest" (S061); "debt lines only in group sections/dimensional" (TXT, AES). Worker count: "six of ten companies in S060 have a total-debt problem".

## T7. Wrong or missing blank reasons

Companies affected: all 200 carry at least the universal four. Sub-families and who is hit:
- Non-dividend payers with `NO REASON` / `missing:` / `incomplete:` / `zero_base_value` instead of "pays no dividend" (only `dividend_growth_streak_years` has `no_dividend_history`): by far the most common. Named at STRL, AKAM, FLUT, PEN, SMTC(S062); FIVE(S063); BTSG, IONQ, ASTS, DVA, CORT, AR(S064); NXT, DECK, SMMT, W, ELAN, FRHC(S065); CART, DOCN, HUBS, QXO, GNRC(S066); AVTR, FIG(S067); ARW, ONTO, MOH, COO(S068); SAIL, BMRN, GSAT(S069); ALGN, SNAP, FROG, OSCR(S070); MDGL, GMED, LULU(S071); RGEN, TTMI(S072); AUR, PODD, GKOS, IBRX(S073); IREN, ESTC, DAR, HSIC, BIO(S074); SANM, PCVX, KRYS, RMBS, DKNG, PCVX(S075); APTV, LTH, VICR(S076); SAIA, GTLB, TXG(S077); PCTY, KYMR, PCOR, CAI, CYTK, CHWY(S078); EAT(S079); BJ, FN, IT, MANH, BMNR, BBIO(S061); CSGP(S060). Reverse case (payer shown as no history): AM `no_dividend_history` on a dividend payer (S073); VNOM same (S079).
- Bank/insurer/REIT/broker template cells with no reason (current_assets, current_liabilities, current_ratio, quick_ratio, working_capital, sga_expense, inventory_days, payables_days, cf_*_change, reconciliation gaps, total_debt_split): ALLY, BPOP, UMBF, SSB, FHN, ZION, WTFC, ONB, CFR, SF (banks/brokers: about 17 to 22 cells each); GL, CNA, CG, ORI, JXN, VOYA, AFG, FNF, PRI (insurers/managers); AMH, UDR, ELS, EGP, GLPI, BXP, CUBE, CPT, FRT, AHR, ADC, BRX (REITs, about 6 to 7 cells each for the current-ratio family); TXT, DOC, TOL (unclassified balance sheets); IVZ, JEF, AGNC, HLI.
- `financial_institution_interest_income_not_revenue` on non-banks (R1): TXT, BAX(S060); AVTR, ERIE(S067); WTRG(S065); MOH(S068); PNR(S079); APTV(S076); SM, FCFS(S075); PRI (insurer, blank true, text false); and wording misleading for insurers/asset managers GL, CNA, CG, FNF, AFG, OSCR, SF, VOYA.
- `reit_net_interest_income_not_revenue` on equity REITs: ELS, AHR, CPT, UDR, AMH, FRT, GLPI, CUBE, EGP, BRX, ADC, CTRE, BXP (S079 count: 789 cells across 189 companies, a query result).
- `pre_revenue_biotech_pharma` on revenue-generating companies: BBIO(S061), ELAN(S065), BMRN(S069), IBRX(S073), MDGL(S071), KRYS(S075), KYMR and CYTK(S078). KYMR also shows gross_margin 0 beside revenue 65M.
- No reason where the filer presents no subtotal/line (FC NR-F): operating_income at AVY, RPM, EHC, AES, RRC, R, SOLS, CLX, DDS, FNF-type insurers; total_liabilities at AVY, GGG, RPM, SMTC, PNW, EAT, MANH, DKS, ARW, TTC, WSO, NYT, MTCH, TECH, DRS, WTS, CCK, RRX, ALV; operating_expenses at FLUT; income_before_tax at MDGL, BXP, EGP, ADC, AMH, CUBE; inventory-change cells at companies with no inventory.
- Wrong or contradictory reasons elsewhere: GLPI/AMH/CPT gross_profit text; CAI cost_of_revenue `line_in_filing_not_extracted` vs gross_profit `line_not_presented_in_filing` for the same statement; PCVX dps_growth `zero_base_value`; ASTS goodwill `incomplete` though no goodwill; OGE/MDGL goodwill_pct_assets `incomplete` though not reported; `line_presented_combined_with_others` for ALLY interest_income although "Total financing revenue and other interest income" is on the face; AGNC interest_income `line_in_filing_not_extracted` on the core mREIT line.
- Reasons that name the symptom not the cause: QXO (about 25 cells `missing:` caused by period labels); PSKY (`missing:prior_period` caused by split year); CHWY, DAR.

Cells: unexplained counts per company from the files range from 4 (GNRC, AMKR, AIT, COO, AEIS, BRKR, ESI, LFUS, VMI-adjacent) to 89 blanks / 37 unexplained (INIO); highest unexplained: AGNC 40, EGP 38, INIO 37, ORI 34, BXP 34, ERIE 33, VNOM 33, JXN 31, EAI 31, AFG 29, CPT 29. Per-company figures are in the verdict table.

Mechanism (workers): "reason keyed on presence of finance-group interest tags, not sector" (S060); "applicability not set for sector-specific concepts" (S061); "reason assigned per missing input, not from 'no dividend history'" (S062); "reason set once from an old state or a coarse flag, not refreshed" (S073); "reason keyed to the REIT sic code (6798), not the income model" (S072).

## T8. Negative or meaningless ratios shown as numbers

Companies affected: 34 for negative trailing_pe plus negative-equity ratio cases.
- Negative trailing_pe displayed (DI unless noted; loss itself FC): BAX -11.63, SMTC -337.27, FLUT -18.35 (S060/S062); BMNR -2.68, BBIO -18.92 (S061); IVZ -42.32 (S063); IONQ -7.89, ASTS -19.81 (S064); ELAN -56.94, W -46.25, SMMT -14.31 (S065); FIG -5.42, AVTR -20.71 (S067); SAIL -60.39, GSAT -163.35 (S069); SNAP -36, FROG -249.12 (S070); MDGL -33.01 (S071); AUR -11.04, GKOS -53.53, IBRX -9.06 (S073); LFUS -227.15 (stale TTM, S074); PCVX -8.70, DKNG -57.6 (S075); GTLB -178.15, TXG -123.39, OC -14.15 (S077); KYMR -34.8, PCOR -232.5, CYTK -8.8 (S078); VNOM -381.4, BRKR -80.45 (S079).
- Negative EV/EBITDA: IONQ -12.63 (flagged `partial:missing_debt_or_cash` yet carries a value), ASTS -23.81.
- Negative equity ratios: DVA debt_to_equity -14.09, price_to_book -14.50, ROE -154% (deficit -765,096 FC); DPZ debt_to_equity -1.24, P/B -2.63, ROE -15.4% (deficit 3,955,098 FC); CYTK ROE +515% (equity -173,487K).
- Near-zero positive earnings: MOH 1,208.89 (TTM EPS 0.18), CORT 275 and EV/EBITDA 501, RGEN 243.4, ALB 369.6 (arithmetically right), JXN 158.78. ESTC P/E 27.4 rests on a 370.1M tax benefit.
- Meaningless margin from other defects: BMNR operating_margin -145.05 (real but extreme).
- CAI trailing_pe 3.76 and KYMR roe +21.4% are wrong (see T17).

Cells: one to three per company. Population: 1,634 of 4,287 trailing_pe values on 2026-10-20 are negative (S073, query). Other metrics (peg_ratio) already carry `non_positive_growth_not_meaningful`.

Exemplar (FC arithmetic): ELAN TTM diluted EPS -0.07 -0.55 +0.11 +0.11 = -0.40, price/EPS = -56.9 (S065).

Mechanism: "no non-positive guard on trailing_pe" (many workers); "guards exist for growth and PEG only" (S064); "no materiality floor when TTM EPS is near-zero positive" (S068).

## T9. fiscal_year / fiscal_period label wrong

Companies affected: 11 plus lookup-key suspects.
- FC against SEC companyfacts: DKS(S061, FYE 2026-01-31 labelled FY2026 vs SEC fy=2025; Q2 to 2026-08-01 labelled FY2027 vs fy=2026), DDS(S070, same; 10-K 0000028917-26-000006 is fy=2025 FY), LULU(S071, accn 0001397187-26-000127 is fy=2026 Q2), CHWY(S078, Q2 ended 2026-08-02 stored fy 2027).
- FC (10-K period) plus DI labels: ONTO(S068, Q4 ended 2026-01-03 labelled fiscal_year 2026; quarter sequence reads 2025Q3, 2026Q4, 2026Q1, 2026Q2).
- DI (own tables): BJ(S061, same pattern as DKS), QXO(S066, Q1 2026 = fy2026 Q1, Q2 2026 and 6M = fy2027 Q1, Q3 2025 stored as "Q2"), DAR(S074, Q4 of year ending 2026-01-03 labelled 2026Q4 while FY row is 2025FY), CGNX(S076, quarter 2024-09-30 to 2024-12-31 labelled fp=Q1), DCI and PCTY (cover-date shares labelled next fiscal year).
- Lookup-key suspects (DI): HLI diluted_shares_growth citing prior_period(2014_FY/2012_FY/2010_FY); BIO diluted_shares_growth citing 2007 to 2009; TTC 3y/10y CAGRs; TECH dps_growth_3y/eps_growth_5y (June FYE); BWA 10y CAGR asking `2016_Q2`; CLX eps CAGR `negative_ratio_undefined_cagr` suspicious; SAIL label FY2027 is the company's own convention (not verified).
- 16-week Q1 / 12-week quarters: DPZ(S071) cash-flow YTD (24 and 36 weeks) not split into quarters; revenue quarters are derived (83 and 111 day lengths) but cash-flow quarters are not (DI).
- NULL fiscal_period: none stated.

Cells: whole period history shifted by one year (DKS, BJ, DDS, LULU, CHWY); TTM chain (revenue_ttm, diluted_eps_ttm, cfo_ttm) fails so trailing_pe, price_to_sales, ev_sales, peg_ratio, ebitda_margin, roa, roe, roic, fcf_yield blank: QXO about 25 cells, ONTO about 10, DAR 6.

Mechanism (workers): "fiscal year taken from period end year for a January year-end (company names it by the year it starts)" (S061); "52/53-week year ending near Jan 1" (S068, S074); labels equal calendar year of period end (S071).

## T10. Recast / restated / spun-off / predecessor comparatives, mixed bases, missing quarters inside the last 8

Companies affected:
- FC: PSKY(S070, split year at merger: Successor 2025-08-08 to 2025-12-31 revenue 12,269M NI -586M; Predecessor 2025-01-01 to 2025-08-06 revenue 16,622M NI -35M, `is_authoritative=false`; no FY2025, no 2025 quarters, no TTM; filing 0002041610-26-000011), APTV(S076, Q2 2025 on new basis 3,199M beside Q1 2025 4,825M, Q3 5,212M, Q4 5,153M, FY2025 20,398M, Q1 2026 5,086M pre-spin; Q1+Q2 2026 = 8,360M vs 6M 6,306M; implied TTM 18.73B).
- DI: AEIS(S074, 2023Q1 to 2024Q4 quarterly revenue absent; all 2024 interim facts non-authoritative after discontinued-ops recast, no authoritative recast quarter written), HLI(S077, FY26 Q1 revenue in core.fact with `is_authoritative=false`), BAH(S077, 2024-09-30, 2024-12-31, 2025-03-31 revenue non-authoritative; Sep-2024 quarter 3,146,386K), HL(S071, Q1 2025 and Q2 2025 revenue missing, 10-Qs have 284 and 406 facts but none under revenue tags; later 10-Qs restate Q2 2025 to 218,992 for discontinued operations), CSGP(S060, Q1 2025 and Q2 2025 revenue missing though EPS exists), TXT(S060, Q3 2025 and Q4 2025 diluted EPS missing), OC(S077, Q4 2024 missing), JEF(S071, Q4 2024 stored 2,851,242 vs about 1.1 to 1.7B neighbours: derived Q4 mixing bases), MLI(S060, Q1 2.16 pre-split beside Q2 1.13 and YTD 2.21 post-split; trailing_pe 8.56, about half true; shares 110.6M then 221.2M), BMNR (shell history, business change), INIO(S063, first registrant: no 10-K, only Q2 2026 and 6M), TOL(S063), SOLS, VNOM, CR, DTM, AIT (spin-offs; history limits).

Cells: missing quarters break `revenue_growth_yoy`, `eps_growth_*`, TTM sums. Examples: CSGP revenue_growth_yoy/3y `missing:prior_period(2025_Q2)/(2023_Q2)`; HL revenue_growth_yoy; MLI eps_growth_yoy, dps_growth_yoy, 3y CAGR; HLI revenue_growth_yoy and dps_growth_yoy; PSKY about 20 cells.

FC exemplar: APTV Q2 2026 10-Q: 6M 6,306M, Q2 3,274M, Q2 2025 comparative 3,199M, implying Q1 2026 on the new basis = 3,032M vs stored 5,086M (S076).

Mechanism: "restated comparatives overwrite only the quarter the new filing carries; neighbouring quarters stay on the old basis" (S076); "authoritative selection leaves the quarter with no winner" (S077); "the rule 'non-authoritative when a later filing restates it' needs the restated comparative to take its place" (S074); "stock split not applied retroactively to older per-share periods" (S060).

## T11. Net income / equity basis inconsistent (consolidated vs attributable)

Companies affected: 8 net income (all FC) plus equity cases.
- Net income stored includes NCI / consolidated while EPS is attributable: FLUT(S062, -296 / -87 vs attributable -274 / -56), PNW(S062, 180,767 / 215,881 vs 178,574 / 211,494), IVZ(S063, 338.9 / 558.0 / 197.4 vs attributable 345.3 / 575.7 / (12.5); sign flips for Q2 2025; Q4 2025 -995.9 vs EPS -2.61 not opened), AR(S064, 548,213 / 286,417 / 834,630 vs Antero 278,657 Q2, 813,873 H1), TXRH(S067, 124,514 vs 121,933 Q2), TTEK(S077, 109,801K / 308,821K vs 109,584K / 308,235K), JEF(S071, 288,253 / 697,577 vs 283,883 / 661,718).
- Equity basis: BWXT(S063, stored 1,334,450 = 1,334,149 attributable + 301 NCI), ASTS(S064, 2,397,578 total incl 503,561 NCI; no parent-only line), BBIO(S064, stored -2,515,215K parent-only vs filed total deficit (2,504,875K); not counted as wrong), GNRC(S066, stored 2,877,623 parent vs total 2,877,628).
- Population: 231 of 5,210 companies with a net_income lineage cite `ProfitLoss` as source tag (S062).

Cells: net_income, ROE, net_margin, EPS-vs-NI disagreement, trailing and TTM ratios.

Mechanism: "net_income falls back to ProfitLoss when NetIncomeLoss absent; peers store attributable" (S062); JEF: two-class EPS note hides `NetIncomeLoss`; "equity resolved by tag priority (StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest) not attributable first" (S063).

## T12. Capex, D&A, interest expense, receivables (and similar line) tags unmapped, stale or split

Companies affected (capex): about 35.
- FC (filing line shown): CSGP(S060, stored 83 YTD vs "new campuses" 83 + other purchases 29 = 112), DOC(S060, development/redevelopment 299.2M + recurring capex 66.1M), BAX(S060, 253 YTD), IT(S061, "Additions to property, equipment and leasehold improvements" 40,346K under `us-gaap:PaymentsForCapitalImprovements`, unmapped for capex), CR(S064, 25,300K six months; only `PaymentsForCapitalImprovements` filed), AR(S064, three E&P lines 492,372 + 45,551 + 8,894; mapped tag last filed 2023), GSAT(S069, four network-upgrade/intangible lines about 205M, extension tags), GLPI(S066, 296,230K + 9,078K), ENSG(S071, `ensg:PaymentsToAcquirePropertyAndEquipment`, mapped tag last 2019), RRC(S072, `PaymentsToAcquireOilAndGasPropertyAndEquipment` authoritative, capex stops 2019), AFG(S063, "Real estate, property and equipment" 58), SM(S075, 1,309 for 6M), CHRD(S079, 755,502K 6M), AHR(S065, "Developments and capital expenditures" 86,006K), FRT(S076, 78,779K + 56,241K), RYAN(S068, stored 1,556K = "Asset acquisitions" vs "Capital expenditures" 30,432K: wrong tag mapped, so fcf_yield 0.049 wrong).
- DI: FNF, EGP, VNOM, BXP, ADC, CUBE, ELS, WTRG, UDR, VOYA, WTFC (banks), DAR (6M 2026 capex 223,626K filed, no 2025-26 interim capex stored: YTD-to-quarter derivation produced none), KNX (FY2025 gap), ORI/JXN/ALLY (no capex line). PRI combined line correctly left blank.
D&A: SEIC(S062, Depreciation 14,327 + Amortization 37,491 two lines), RYAN(S068, 4,133 + 64,387), ALSN(S076, two tags), SWKS(S064, only `OtherDepreciationAndAmortization`), TTMI, PNR, MTCH, CCK, AFG, FCFS (income statement D&A 32,440), SM ("Depletion, depreciation, and amortization" 1,024), GSAT ("Depreciation, amortization and accretion" 35,199K). Cascade: ebitda and four ratios.
Interest expense: AM("Interest expense, net" (55,680)), WMS(27,040,000), DCI(36.0), SOLS("Interest and other financial charges" 23), ALSN/LTH (only net filed), ARW, ALB, VNOM(24 net), HLI.
Receivables / AP: ReceivablesNetCurrent unmapped at SWKS, BWA, ALLE(559.7), GGG, LII, PBF(1,839.2M), OC, BSY, LULU, TOL, PNR, WMS, MOH, MKC (AP), DECK (AP series ends about 2020), CCK/CFR other lines.

Cells: capex gap costs 7 to 14 FCF-family cells each (fcf, fcf_margin, fcf_yield, fcf_per_share, fcf_gt_net_income, fcf_growth_yoy/3y/5y, capex_pct_revenue, dividends_pct_fcf, share_repurchases_pct_fcf); CSGP understates capex by 26%. D&A gap costs 5 ebitda cells; AR gap about 4 to 5; interest expense gap blanks interest_coverage_ratio.

Mechanism (worker wording): "capex mapped to PaymentsToAcquireProductiveAssets only; the E&P/REIT/utility tags are not in the list" (S064, S065, S072); "Mapper captures one of two cash-flow capex lines, the second is left out" (S060); "same wrong-tag class as the 'acquisitions are not capex' rule" (S068); "tags absent from the mapped vocabulary (vocabulary circularity)" (S072).

## T13. Dividend payers with blank DPS/yield (cumulative or YTD-only per-share, empty quarter not zero)

Companies affected: about 20.
- FC: PNW(S062, DPS 1.82 under 3-month labels, six-month figure; Q3 2025 derived 0.00; dividends on common 220,565K over 121.2M shares), PBF(S072, dividends 32.5M Q2 / 64.7M 6M, per-share filed YTD only), AM(S073, dividends to common 220.7M H1 vs `no_dividend_history`), ORI(S074, 770.4M common dividends 6M, yield blank), HLI(S077, quarterly dividends, DPS stored for only two quarters), FRT(S076, yield 4.2% filled but dividends_paid unmapped), WTS(S064, "Dividends" (38.8) six months, declared 0.63/qtr, dividends_paid blank), RYAN(S068, Class A dividends paid 33,741K), ERIE(S067, Class A dividends declared 1.4625/qtr; EPS and DPS blank).
- DI: SEIC (Q1 2026 absent), RPM (no DPS fact since mid-2025), AIT, BWXT, LII (declared DPS missing quarters), CHRD, BRKR, VNOM, PNR, EGP, EVR, BXP, SCI (dps_growth_3y), ALSN (dps_growth_3y `prior_period(2023_Q2)`).
Cells: dividend_yield, dps_growth_yoy/3y, payout_ratio, dividends_pct_fcf, cash_returned_to_shareholders (3 to 6 each).
Mechanism: "TTM builder ignores an annual DPS fact" (S063); "cumulative per-share figure assigned to the quarter period; discrete-quarter derivation subtracts to zero" (S062); "per-share dividend filed year-to-date only" (S072).

## T14. institutional_ownership_pct blank as implausible (13F sums exceed shares outstanding)

Companies affected: at least 50 named across the block; count query result 683 companies carry the reason population-wide (S079, query).
Named: SGI, BAX, CSL(S060); BJ, FN, MANH, IT(S061); SMTC, PNW, AKAM(S062); CCK, FIVE(S063); SWKS, BTSG, BWA(S064); ELS, W, ELAN(S065); TECH, WSO, PAYC(S066); UDR, TXRH, AVTR(S067); SF, NYT, COO, ARW, JKHY, MOH, FHN, RYAN(S068); FDS(S069); KNX, OSCR(S070); MDGL, RRX, DPZ(S071); CPT, RGEN(S072); MTCH, PODD(S073); LFUS, DAR, AEIS, HSIC(S074); BXP, PCVX, SANM(S075); ALSN, VICR(S076); HLI, SAIA, OC, GTLB(S077); KYMR, CYTK, CHWY(S078); ESI, EAT, VOYA, ALV, BRX, CHRD, ADC(S079).
Evidence of the real overcount (DI): CCK 254.7M held vs 108.8M outstanding (2.3x), FIVE 177.5M vs 55.1M (3.2x), HSIC 126.9M vs 111.4M (114%), SAIA 29.4M (27.4M excluding amendments) vs 26.67M, OC 84.1M (78.7M ex-amendments) vs 79.0M, MDGL 116%, RRX 108%, DPZ 115% (rows: MDGL 590 for 377 filers, RRX 848/545, DPZ 1,205/786, incl. amendment rows), CFR 1,709 filers (value shown, not examined).
Cells: ownership % blank (honest), but the underlying holdings are wrong. Mechanism: duplicate filer rows, amendment rows, sub-adviser or option legs summed; wrong share base for multi-class names.

## T15. Multi-registrant combined filing attributes parent facts to subsidiary (new)

Companies: EAI(S078) only. FC: stored revenue 3,523,638K Q2 / 6,711,264K 6M = Entergy Corporation; Entergy Arkansas is 693,486K / 1,339,783K. Same for operating_income_resolved (850,089K vs 158,472K Q2), net_income 487,820K and diluted EPS 1.03 (an LLC has no EPS), total assets 79,002,618K vs 17,638,405K, equity 18,229,120K vs members' equity 5,067,015K, shares 466,631,498 (parent cover), cash flow parent page (R3). 10 wrong values plus market cap 8,590,685,878 from a different security's price. 0 FY revenue rows; 32 10-Ks, none with facts. Mechanism: "undimensioned fact in a multi-registrant filing attributed to every co-registrant"; also "security-type not checked before computing market cap". Reach unknown.

## T16. Q4 / per-share values derived by subtraction are impossible (new)

Companies: KYMR, CAI (FC for FY, DI for the arithmetic).
- KYMR(S078): Q4 2025 net income +535,721K vs FY (311,351) minus 9M (224,370) = (86,981)K; FY and 9M match the filing. Flows to ROE +21.4% (TTM +323M), a loss-maker showing positive ROE.
- CAI(S078): Q4 2025 diluted EPS 8.24 vs filed FY2025 EPS (3.22) on 167.2M weighted shares (Q4 about 0.29); trailing_pe 3.76 (TTM EPS 8.32), expected about 85.
Mechanism: "Q4 derivation subtracts from a wrong/mismatched YTD base"; "per-share Q4 not additive after a share-base change (June 2025 IPO at CAI)".

## T17. YTD-only cash flow blocks TTM (ebitda, fcf, buyback) and real buybacks not mapped

- `ebitda` `missing:4_consecutive_quarters` plus 4 ratios because cash-flow D&A is cumulative YTD: ALLE, AVY, DOC, TXT(S060); JKHY, ONTO-adjacent, MOG-A, SWKS, LFUS, SCI, RRX, AIT, DPZ, OGE, ESI, TTEK, TTMI, CTRE, BXP, SM, R, DAR (named across shards; ARW, FHN, etc.).
- Buybacks real but not captured (FC line): CSGP repurchases 587M YTD (S060), PAYC 1,389.7M for 6M (S066), RYAN "Repurchases of Class A common stock" 300,182K (S068), RRC "Treasury stock purchases" 105,476K (S072), SWKS PaymentsForRepurchaseOfCommonStock mapped but TTM fails (9M YTD, S064). DI: DPZ (shares fell 33.26M to 32.90M), ALV (74.86M to 73.24M), CUBE (227.3M to 225.5M), GTLB, EVR, HRL, DKS.
- FCF-from-capex-blank cascades are under T12.

## T18. Operating margin / ratio blank while a resolved input exists (new, small)

BRX(S079): operating_income_resolved 121.603M exists but operating_margin `incomplete:numerator` (margin reads `operating_income`); ASTS(S064): operating_income_resolved Q2 -297,577 stored and FC-correct but operating_margin and roic blank. Mechanism: margin reads the unresolved concept (D2) / blocked chain not isolated.

## T19. Foreign private issuer in the list (new)

SCNI(S069): files 20-F, no 10-Q; market cap 9.78B and price_to_book 1,207 wrong (ordinary shares x ADS price); latest FY2025 only. Scope question (doc 02) stays open.

## Per-company verdicts

Format: TICKER | shard | rank/mcap | wrong values | unexplained blanks | verdict. "-" = not in file. Counts are the files' own verdict-table figures; notes in brackets. Unexplained counts include the four universal cells unless stated. Rows marked DERIVED were not in a file verdict table.

SGI | S060 | band 12.4-13.5B | 1 (total_debt stale/off) | 4 | NOT CLEAN
ALLE | S060 | - | 0 | 7 | NOT CLEAN (blanks)
AVY | S060 | - | 1 (total_debt) | 8 | NOT CLEAN
MLI | S060 | - | 2 (split-basis EPS, trailing_pe; total_debt stale) | 7 | NOT CLEAN
GGG | S060 | - | 0 (1 blank that should have a value, total_debt) | 9 | NOT CLEAN
CSL | S060 | - | 0 | 5 (4 universal + total_liabilities) | CLEAN candidate (file wording)
CSGP | S060 | - | 1 (capex 83 vs 112) | 13 | NOT CLEAN
DOC | S060 | - | 1 (revenue all years) plus capex stale | 18 | NOT CLEAN
BAX | S060 | - | 2 (total_debt=0, negative P/E) | 4 | NOT CLEAN
TXT | S060 | - | 0 values, 2 wrong reasons | 15 | NOT CLEAN
DKS | S061 | - | 1 (fiscal_year labels) | 9 | NOT CLEAN
BJ | S061 | - | 1 (fiscal_year labels) | 9 | NOT CLEAN
BMNR | S061 | 13.75B | 1 (negative P/E) | 24 | NOT CLEAN
FN | S061 | - | 0 | 9 | NOT CLEAN
BBIO | S061 | - | 1 (negative P/E) | 8 | NOT CLEAN
GL | S061 | 13.0B | 1 (shares at FY2025 = issued) | 21 | NOT CLEAN
MANH | S061 | - | 0 | 21 | NOT CLEAN
IT | S061 | - | 0 (capex blank = mapping gap) | 19 | NOT CLEAN
CG | S061 | - | 0 | 18 | NOT CLEAN
CNA | S061 | - | 1 (revenue all periods) | 21 | NOT CLEAN
FLUT | S062 | - | 2 (net income incl NCI, negative P/E) | 14 | NOT CLEAN
STRL | S062 | - | 0 | 9 | NOT CLEAN
RPM | S062 | - | 0 | 7 | NOT CLEAN
PEN | S062 | - | 0 (total_debt wrong blank) | 13 | NOT CLEAN
DTM | S062 | - | 0 | 9 | NOT CLEAN
EHC | S062 | - | 0 | 9 | NOT CLEAN
SMTC | S062 | - | 2 (Q2 missing, negative P/E) | 14 | NOT CLEAN
AKAM | S062 | - | 1 (debt_to_equity) | 17 | NOT CLEAN
PNW | S062 | - | 2 (net income incl NCI, DPS 1.82/0.00) | 8 | NOT CLEAN
SEIC | S062 | - | 0 | 13 | NOT CLEAN
BWXT | S063 | - | 1 (equity incl NCI) | 8 | NOT CLEAN
MKC | S063 | 12.77B | 0 shown, 1 wrong blank (shares) | 10 | NOT CLEAN
LII | S063 | - | 1 (Q2 missing) | 7 | NOT CLEAN
IVZ | S063 | - | 2 (net income incl NCI, negative P/E) | 11 | NOT CLEAN
CCK | S063 | - | 1 (13F overcount 2.3x) | 13 | NOT CLEAN
AFG | S063 | - | 1 (operating income = pretax) | 29 | NOT CLEAN
TOL | S063 | - | 0 | 22 | NOT CLEAN
FIVE | S063 | - | 1 (13F overcount 3.2x) | 10 | NOT CLEAN
INIO | S063 | - | 0 found (cover shares not checked) | 37 | NOT CLEAN
AIT | S063 | - | 0 values, 1 untruthful reason (dividend yield) | 4 | NOT CLEAN (closest to certifiable, file wording)
BTSG | S064 | 12.33B | 0 | 13 | NOT CLEAN (blanks only)
SWKS | S064 | - | 0 | 10 | NOT CLEAN (blanks only)
IONQ | S064 | - | 2 (negative P/E, EV/EBITDA) + 1 wrong blank (zero debt) | 22 | NOT CLEAN
ASTS | S064 | 12.26B | 4 (stale EPS, market cap basis, negative P/E, negative EV/EBITDA) | 20 | NOT CLEAN
DVA | S064 | - | 3 (D/E, P/B, ROE on negative equity) | 11 | NOT CLEAN
WTS | S064 | 12.0B | 0 (market cap 0.3% off) | 14 | NOT CLEAN (blanks only)
CR | S064 | 11.62B | 0 | 9 | NOT CLEAN (blanks only)
CORT | S064 | - | 0 (P/E 275 outlier) | 6 | NOT CLEAN (blanks only)
BWA | S064 | - | 1 (cash stale, ROIC blank) | 8 | NOT CLEAN
AR | S064 | - | 2 (net income incl NCI, capex stale 2023) | 17 | NOT CLEAN
NXT | S065 | band 11.3-12.7B | 0 | 15 | NOT CLEAN (blanks only)
ELS | S065 | - | 2 (Q2 missing, FY2018 revenue) | 22 | NOT CLEAN
MOG-A | S065 | - | 1 (operating income) | 12 | NOT CLEAN
DECK | S065 | - | 0 | 15 | NOT CLEAN (blanks only)
SMMT | S065 | - | 1 (op income stale 2024) + negative P/E | 19 | NOT CLEAN
AHR | S065 | - | 2 (revenue, operating income) | 24 | NOT CLEAN
WTRG | S065 | - | 0 (wrong reason on 4 cells) | 14 | NOT CLEAN
FRHC | S065 | - | 0 | 10 | NOT CLEAN (blanks only)
W | S065 | - | 0 (negative P/E displayed) | 15 | NOT CLEAN
ELAN | S065 | - | 1 (op income stale 2020 + wrong reason) + negative P/E | 17 | NOT CLEAN
ALLY | S066 | band 10.9-12.5B (11.5B) | 3+ (revenue every period, P/S 9.41) | 25 (21 excl universal) | NOT CLEAN
CART | S066 | - | 0 | 19 (15) | NOT CLEAN
DOCN | S066 | - | 0 | 14 (10) | NOT CLEAN
HUBS | S066 | - | 0 | 14 (10) | NOT CLEAN
GLPI | S066 | - | 2 (FY2021 revenue; capex stale) | 17 (13) | NOT CLEAN
TECH | S066 | - | 0 (total_debt blank with debt on balance sheet) | 10 (6) | NOT CLEAN
GNRC | S066 | - | 0 | 4 (0) | NOT CLEAN (nearly)
PAYC | S066 | - | 0 (buyback cells blank) | 5 (1) | NOT CLEAN (nearly)
QXO | S066 | - | 1 (fiscal labels) | 4 (0), plus 12+ misleading derived blanks | NOT CLEAN
WSO | S066 | 11.5B | 1 (market cap share basis) | 10 (6) | NOT CLEAN
AMH | S067 | band 11.1-11.5B | 3 (revenue, op income, capex stale) | 30 | NOT CLEAN
ALB | S067 | - | 0 | 9 | NOT CLEAN
ERIE | S067 | - | 0 (EPS and dividends blank wrongly) | 33 | NOT CLEAN
HRL | S067 | - | 0 | 12 | NOT CLEAN
AVTR | S067 | - | 2 (Q2 missing, negative P/E) | 9 | NOT CLEAN
FIG | S067 | - | 1 (negative P/E) | 25 | NOT CLEAN
UDR | S067 | 11.14B | 3 (revenue, P/S 945.75, Q2 missing) | 25 | NOT CLEAN
SCI | S067 | - | 0 | 9 | NOT CLEAN
TXRH | S067 | - | 1 (net income incl NCI) | 6 | NOT CLEAN
UHS | S067 | - | 0 | 18 | NOT CLEAN
SF | S068 | 10.85B | 3 (revenue, shares stale 2019, market cap) | 21 | NOT CLEAN
NYT | S068 | - | 0 | 14 | NOT CLEAN (blanks only)
COO | S068 | - | 0 | 4 (universal) | CLEAN on values; 4 universal unexplained (file wording)
ARW | S068 | - | 0 | 13 | NOT CLEAN (blanks only)
AA | S068 | - | 0 | 10 | NOT CLEAN (blanks only)
JKHY | S068 | - | 1 (FY2026 10-K not ingested) | 12 | NOT CLEAN
ONTO | S068 | - | 1 (Q4 label breaks TTM) | 10 | NOT CLEAN
MOH | S068 | - | 1 (trailing P/E 1,208.9) | 16 | NOT CLEAN
FHN | S068 | - | 0 (annual history hole FY2020-21) | 21 | NOT CLEAN (blanks only)
RYAN | S068 | 264.2M implied shares | 4 (revenue, capex, EPS missing, shares stale 2021) | 23 | NOT CLEAN
HII | S069 | - | 0 | 7 | NOT CLEAN
FDS | S069 | - | 0 | 7 | NOT CLEAN
FNF | S069 | - | 1 (revenue every period) | 19 | NOT CLEAN
SAIL | S069 | - | 1 (negative P/E) | 21 | NOT CLEAN
AES | S069 | - | 0 | 12 | NOT CLEAN
BMRN | S069 | - | 0 | 13 | NOT CLEAN
GSAT | S069 | 10.73B | 2 (stale shares/market cap, negative P/E) | 16 | NOT CLEAN
SCNI | S069 | 9.78B (wrong) | 2 (market cap, P/B) | 23 | NOT CLEAN
EGP | S069 | - | 0 | 38 | NOT CLEAN
EVR | S069 | 10.45B | 1 (operating_income_resolved) | 23 | NOT CLEAN
OSCR | S070 | band 10.4-11.4B | 2 (revenue 6.1M vs 4,880M; P/S 379) | 23 | NOT CLEAN
KNX | S070 | - | 1 (latest quarter stale; P/E 303.8) | 8 | NOT CLEAN
CLX | S070 | - | 2 (latest 10-K missing; P/E 14.2 vs about 18.2) | 11 | NOT CLEAN
PSKY | S070 | - | 0 (FY2025 and TTM absent) | 21 | NOT CLEAN
ALGN | S070 | - | 0 | 12 | NOT CLEAN
SNAP | S070 | - | 1 (negative P/E) | 13 | NOT CLEAN
AGNC | S070 | - | 0 | 40 | NOT CLEAN
AMKR | S070 | - | 1 (latest quarter stale; P/E 24.0) | 4 | NOT CLEAN
FROG | S070 | - | 1 (negative P/E) | 15 | NOT CLEAN
DDS | S070 | - | 0 numeric; fiscal_year labels one year ahead | 16 | NOT CLEAN
MDGL | S071 | - | 1 (negative P/E) + 1 wrong reason | 13 | NOT CLEAN
BSY | S071 | - | 0 | 13 | NOT CLEAN
GMED | S071 | - | 0 | 16 | NOT CLEAN
ENSG | S071 | - | 1 (revenue) | 5 | NOT CLEAN
LULU | S071 | - | 1 (fiscal_year labels +1) | 16 | NOT CLEAN
RRX | S071 | - | 0 | 7 | NOT CLEAN
HL | S071 | - | 0 (Q1/Q2 2025 revenue missing) | 6 | NOT CLEAN
JEF | S071 | - | 5 (revenue, net income, EPS stale, gross_margin, current_ratio stale 2012) | 7 | NOT CLEAN
DCI | S071 | - | 0 | 6 | NOT CLEAN
DPZ | S071 | - | 3 (D/E, P/B, ROE on negative equity) | 11 | NOT CLEAN
BPOP | S072 | band 9.8-10.2B | 1 (revenue = gross interest income) | 22 | NOT CLEAN
RRC | S072 | - | 2 (revenue excludes derivative income; capex stale) | 8 | NOT CLEAN
MUSA | S072 | - | 0 | 7 | NOT CLEAN (blanks only)
UMBF | S072 | - | 1 (bank revenue) | 21 | NOT CLEAN
AMG | S072 | - | 1 (operating income) | 11 | NOT CLEAN
CPT | S072 | - | 3 (revenue 3.1M vs about 393M, net margin 600%, P/S 762) | 29 | NOT CLEAN
RGEN | S072 | - | 0 (P/E 243.4 noted) | 12 | NOT CLEAN (blanks only)
SSB | S072 | - | 1 (bank revenue) | 22 | NOT CLEAN
TTMI | S072 | - | 0 | 13 | NOT CLEAN (blanks only)
PBF | S072 | - | 0 (shares missing) | 11 | NOT CLEAN
MTCH | S073 | - | 0 | 11 | NOT CLEAN
OGE | S073 | - | 1 (Q2 missing) | 4 | NOT CLEAN
AUR | S073 | - | 1 (negative P/E) | 18 | NOT CLEAN
PODD | S073 | - | 0 | 10 | NOT CLEAN
WTFC | S073 | - | 1 (annual revenue 14x low) + wrong-reason class | 22 | NOT CLEAN
GKOS | S073 | - | 1 (negative P/E) | 12 | NOT CLEAN
IBRX | S073 | - | 1 (negative P/E) | 10 | NOT CLEAN
AM | S073 | - | 0 values, 1 wrong reason | 12 | NOT CLEAN
WMS | S073 | 9.74B | 0 | 11 | NOT CLEAN
ONB | S073 | - | 1 (Q2 missing) | 21 | NOT CLEAN
LFUS | S074 | - | 2 (Q2 missing, negative P/E -227) | 4 | NOT CLEAN
IREN | S074 | - | 2 (FY2026 10-K missing; P/E 40.5, ROE +5.9%) | 19 | NOT CLEAN
ESTC | S074 | - | 0 | 14 | NOT CLEAN
DAR | S074 | - | 0 shown wrong, 5 headline cells blank by label defect | 14 | NOT CLEAN
ORI | S074 | - | 0 | 34 | NOT CLEAN
CFR | S074 | 9.71B | 2 (revenue 34.2M vs 576.0M; P/S 74.6) | 23 | NOT CLEAN
HSIC | S074 | - | 0 | 13 | NOT CLEAN
BIO | S074 | - | 0 (shares absent) | 12 | NOT CLEAN
AEIS | S074 | - | 0 | 4 | NOT CLEAN by strict rule, closest to certifiable
TTC | S074 | - | 0 | 8 | NOT CLEAN
DRS | S075 | - | 0 | 9 | NOT CLEAN
BXP | S075 | - | 1 (stale 2018 operating income) | 34 | NOT CLEAN
PCVX | S075 | - | 1 (negative P/E -8.70) | 27 | NOT CLEAN
SANM | S075 | - | 0 | 11 | NOT CLEAN
SM | S075 | - | 0 FC (1 definitional) | 18 | NOT CLEAN
KRYS | S075 | - | 0 | 17 | NOT CLEAN
RMBS | S075 | - | 1 (Q2 missing) | 12 | NOT CLEAN
SOLS | S075 | - | 0 | 14 | NOT CLEAN
FCFS | S075 | - | 3 (revenue, FY revenue 3 years, operating income) | 12 | NOT CLEAN
DKNG | S075 | - | 1 (negative P/E -57.6) + shares blank | 21 | NOT CLEAN
ZION | S076 | - | 3 (revenue, net_margin 321%, P/S 17.4) | 22 (19) | NOT CLEAN
ALSN | S076 | - | 0 | 7 (4) | NOT CLEAN
FRT | S076 | - | 1 (Q2 stale) | 39 (36) | NOT CLEAN
APTV | S076 | - | 4 (mixed-basis revenue, TTM revenue, P/S, FY2010 revenue) + 1 wrong reason | 5 (2) | NOT CLEAN
R | S076 | - | 0 | 10 (7) | NOT CLEAN
CGNX | S076 | - | 1 (one quarter wrong fiscal period) | 10 (8) | NOT CLEAN
AYI | S076 | - | 0 | 6 (4) | NOT CLEAN
LTH | S076 | - | 0 | 13 (11) | NOT CLEAN
SIRI | S076 | - | 0 | 6 (3) | NOT CLEAN
VICR | S076 | - | 1 (Q2 stale) | 10 (7) | NOT CLEAN
FLS | S077 | band 8.8-9.3B | 0 | 0 excl universal (4 universal) | CLEAN (file wording: only the 4 universal cells unexplained)
HLI | S077 | - | 0 | 18 excl universal (22 all) | NOT CLEAN
SAIA | S077 | - | 0 | 16 excl universal (20) | NOT CLEAN
BAH | S077 | - | 0 | 4 excl universal (7; BAH has 3 universal) | NOT CLEAN (history only)
OC | S077 | - | 1 (negative P/E) | 5 excl universal (9) | NOT CLEAN
GTLB | S077 | - | 1 (negative P/E) | 19 excl universal (23) | NOT CLEAN
TTEK | S077 | - | 1 (net income incl NCI) | 3 excl universal (7) | NOT CLEAN
TXG | S077 | - | 1 (negative P/E) | 7 excl universal (11) | NOT CLEAN
JXN | S077 | - | 0 (P/E 158.8 flagged, not proven wrong) | 27 excl universal (31) | NOT CLEAN
CUBE | S077 | - | 1 (everything one quarter stale) | 22 excl universal (26) | NOT CLEAN
PCTY | S078 | - | 2 | 15 | NOT CLEAN
KYMR | S078 | - | 4 (Q4 NI, ROE sign, negative P/E, gross margin 0) | 25 | NOT CLEAN
PRI | S078 | - | 0 | 19 | NOT CLEAN
PCOR | S078 | - | 1 (negative P/E) | 14 | NOT CLEAN
CTRE | S078 | - | 3 (revenue 4.6M vs 161M, P/S, net margin) | 21 | NOT CLEAN
CAI | S078 | - | 2 (Q4 EPS 8.24, P/E 3.76) | 16 | NOT CLEAN
CYTK | S078 | - | 2 (ROE 515%, negative P/E) | 14 | NOT CLEAN
CHWY | S078 | - | 2 (fiscal_year +1, shares 100 stale) | 10 | NOT CLEAN
VMI | S078 | - | 0 | 6 (4 universal + 2 AR-change) | NOT CLEAN (strictly); closest to certifiable
EAI | S078 | 8.59B (wrong) | 10 (every stored value is Entergy Corporation's) | 31 | NOT CLEAN
ESI | S079 | - | 1 (Q2 missing) | 4 | NOT CLEAN
EAT | S079 | - | 0 FC; 1 display issue (no-dividend reason) | 7 | NOT CLEAN
VOYA | S079 | - | 2 (revenue, operating income) | 22 | NOT CLEAN
ALV | S079 | - | 0 | 8 | NOT CLEAN
BRX | S079 | - | 0 values wrong; operating_margin blank while operating income exists | 30 | NOT CLEAN
PNR | S079 | - | 1 (Q2 missing) | 6 | NOT CLEAN
VNOM | S079 | 8.58B | 1 (revenue 658 vs 677) + negative P/E | 33 | NOT CLEAN
CHRD | S079 | - | 0 values wrong; capex blank | 13 | NOT CLEAN
BRKR | S079 | - | 1 (negative P/E -80.45) | 4 | NOT CLEAN
ADC | S079 | - | 0 | 18 | NOT CLEAN

Totals as the files give them: 2 companies called CLEAN in their own words (FLS, plus CSL "CLEAN candidate", and COO "CLEAN on values with 4 universal unexplained"); all others NOT CLEAN. No file counts a company as certifiable.

## History-window items

First-FY revenue held vs earliest 10-K in core.filing, FY2018/FY2021 spot checks, missing quarters. FC = opened filing or SEC API; otherwise from the worker's memory (DI).

S060 (all DI except where stated): earliest FY revenue stored / earliest 10-K: SGI 2008 / 2004; ALLE 2012 / 2014 (spin-off); AVY 2008 / 1994 (14 FY, gaps in the early series); MLI 2016 / 1994 (annual revenue absent 2009-2015, likely older revenue tag not in vocabulary); GGG 2008 / 1995; CSL 2008 / 1994; CSGP 2009 / 1999; DOC 2007 / 1994 (FY2016 2,129M is the only total, then 524M/144M/144M/436M for 2017-2020; FY2018 144.2M wrong); BAX 2007 / 1994; TXT 2009 / 1994. Missing quarters: CSGP Q1 2025 and Q2 2025 revenue; TXT Q3 2025 and Q4 2025 EPS. FY2018 AVY 7,159.0M, CSGP 1,191.8M, TXT 13,972M, MLI 2,507.9M agree with known figures (DI).
S061: DKS 2009 / 2003; BJ 2017 / 2019; BMNR 2021 / 2021; FN 2010 / 2010; BBIO 2019 / 2020; GL 2007 / 1994; MANH 2009 / 2001; IT 2008 / 1996; CG 2010 / 2013; CNA 2009 / 1994 with FY2021 stored 1,430M wrong (about 11B). FY2021 matches for the others (DI). GL 19, DKS 18, CNA 17 FY vs filings back to 1994 (design limit about 15 years). Missing quarters: not checked.
S062: SMTC 2009 / 1996; RPM 2009 / 1994; SEIC 2008 / 1995; PNW 2008 / 1993; EHC 2016 / 1995 (GAP 2008-2015: `HealthCareOrganizationRevenue` unmapped, companyfacts shows 10-K values 2008 to 2017); STRL 2009 / 1996; DTM 2019 / 2021; AKAM 2007 / 2000; FLUT 2022 / 2023; PEN 2013 / 2015. Missing: SMTC quarter ending 2026-07-26; RPM holds 9 quarters.
S063: MKC 2008 / 1993; LII 2008 / 2001; IVZ 2007 / 2007; CCK 2008 / 2002; AFG 2008 / 2002; TOL 2017 / 1994 (FY2010-FY2016 revenue missing although core.fact holds `HomeBuildingRevenue` 1,494,771K FY2010 to 5,169,508K FY2016, each with an authoritative copy; DI); FIVE 2011 / 2013; INIO none; AIT 2009 / 1994; BWXT 2009 / 2011. AIT FY2025 4,563,424 and FY2024 4,479,406 FC against the FY2026 10-K. Missing: LII Q2 2026; INIO only Q2 2026 held.
S064: SWKS 2008 / 1996; WTS 2008 / 1994; BWA 2011 / 1995; DVA 2016 / 2002 (only 10 FY though filings go back 24 years; depth gap, cause not investigated); CORT 2009 / 2004; AR 2011 / 2013; IONQ 2020 / 2020; BTSG 2022 / 2023; CR 2021 / 2022; ASTS 2020 / 2019. FY2021/2022 WTS 1,809.2/1,979.5, BWA 11,803/12,635, DVA 11,618.8/11,609.9 not FC. Last three 10-Qs present for all; full 8-quarter scan not done.
S065: NXT 2021 / 2023; ELS 2008 / 1996 (FY2018 15,191,000 wrong vs 986,653,000); MOG 2008 / 1994; DECK 2017 / 1997 (FY2008-2016 missing); SMMT 2018 / 2020; AHR 2016 / 2015 (FY2018 36.9M looks too small, DI); WTRG 2007 / 1993; FRHC 2011 / 2007; W 2012 / 2014; ELAN 2016 / 2018. Missing: ELS Q2 2026; others not scanned.
S066: ALLY 2009 / 1994 (FY2021 stored 852M vs filed 8,428M, FC via FY2023 10-K R3); WSO 2008 / 2002; TECH 2009 / 1995; GLPI 2011 / 2013 (FY2021 109.7M vs 1,216.4M); CART 2021 / 2023; DOCN 2019 / 2021; PAYC 2012 / 2014; QXO 2010 / 2008; HUBS 2012 / 2014; GNRC 2012 / 2009. FY2021 matches for WSO, HUBS, PAYC, DOCN, CART, GNRC, TECH. QXO FY2024/FY2025 balance sheet history missing (only Q2 2026 equity and Q1/Q2 2026 total assets held; FY2025 10-K has 505 facts; DI). GLPI capex only Q1 2026.
S067: HRL 2008 / 1995; UDR 2008 / 1993 (FY2021 6,102K wrong); SCI 2008 / 1993; UHS 2012 / 1993 (three years later than peers); ALB 2008 / 1996; ERIE 2008 / 1996; AMH 2016 / 2013 (5 FY, revenue chain ends 2020); FIG 2023 / 2025; TXRH 2009 / 2004; AVTR 2017 / 2019. Missing: UDR and AVTR Q2 2026; AMH no revenue after 2020.
S068: SF 2008 / 1994; NYT 2008 / 1993; COO 2008 / 1993; ARW 2008 / 1993; AA 2015 / 2016; JKHY 2009 / 1995; ONTO 2010 / 1996; MOH 2009 / 2003; FHN 2008 / 1993 (FY2020 and FY2021 annual revenue missing, probable merger-year transition); RYAN 2019 / 2021. Missing: JKHY Q4 FY2026 and FY2026; ONTO Q4 2025 mislabelled.
S069: HII 2009 / 2012; FDS 2009 / 1996; FNF 2008 / 2006 (FY2018 2,216M and FY2021 2,821M wrong vs filed totals 11,752M to 14,445M for FY2023-25); SAIL FY2024-01-31 / 2025; AES 2009 / 1997; BMRN 2008 / 2000; GSAT 2009 / 2007; SCNI 2024 / 2023 (20-F; 2 FY); EGP 2008 / 1995; EVR 2009 / 2007. Quarters complete for all.
S070: OSCR 2019 / 2022 (FY2021 5.4M wrong); KNX 2009 / 2011; CLX 2010 / 1994; PSKY 2023 / 2026 (FY2025 absent; predecessor Paramount Global is a separate CIK); ALGN 2008 / 2002; SNAP 2015 / 2018; AGNC none / 2009 (no revenue concept); AMKR 2008 / 2003; FROG 2018 / 2021; DDS 2009 / 1994 (labels one year ahead). Missing newest period: KNX, AMKR, CLX; PSKY 2025 Q1-Q4.
S071: MDGL 2012 / 2006; BSY 2018 / 2020 (FY2021 965,046 FC via SEC API); GMED 2010 / 2012; ENSG 2016 / 2007; LULU 2009 / 2008 (labels +1); RRX 2012 / 1994; HL 2010 / 1993; JEF 2007 / 1993 (FY2021 6,141,801 vs SEC `Revenues` 8,945,464, FC via SEC API); DCI 2016 / 1994; DPZ 2010 / 2005. Missing: HL Q1 2025 and Q2 2025 revenue.
S072: BPOP 2008 / 1993; RRC 2007 / 2000; MUSA 2011 / 2013; UMBF 2008 / 1993; AMG 2016 / 1998; CPT 2016 / 1996 (2018 7.2M, 2021 10.5M wrong); RGEN 2010 / 1995; SSB 2009 / 1995; TTMI 2017 / 2000; PBF 2012 / 2012. AMG, CPT, TTMI start 2016/2017 although XBRL exists from about 2009 (7 to 8 FY unmapped; cause not examined). All 8 of 8 quarters present.
S073: ONB, MTCH, WTFC, OGE FY2008; AUR FY2019; WMS FY2017; AM FY2015; PODD FY2009; GKOS FY2013; IBRX FY2013 (earliest 10-K not queried). FY2023-2025 FC for ONB (3,269.9 / 2,601.7 / 2,206.8) and WMS (FY2024-2026); WTFC FY wrong. Missing: OGE and ONB Q2 2026.
S074: LFUS FY from 2010-01-02 (20 FY rows over about 16 years: duplicate or mislabelled rows suspected; FY2021 row absent); IREN 2023 / 2025; ESTC 2017 / 2019; DAR 2009 / 1996; ORI 2008 / 1993; CFR 2008 / 1993 (FY2018 85.2M and FY2021 83.3M wrong); HSIC 2011 / 1996; BIO 2008 / 1996; AEIS 2009 / 1999 (2023Q1 to 2024Q4 missing); TTC 2008 / 1994. Missing: LFUS 2026Q2; DAR mislabelled; AEIS 8 quarters.
S075: FCFS 2009 / 1996 (FY2023-25 equal "Retail merchandise sales" exactly; total about double); SM 2008 / 1996; SANM 2009 / 1998; RMBS 2008 / 1997; BXP 2007 / 2001; DRS 2019 / 2021; DKNG 2020 / 2022; SOLS 2023 / 2025; PCVX 2021 / 2017; KRYS 2021 / 2017. Missing: RMBS Q2 2026; others checked only last two quarters.
S076: ZION 2008 (2,974M, different basis) / 1993 with FY2018 stored 412M vs SEC `Revenues` 508M / `InterestAndDividendIncomeOperating` 2,481M (FC via companyfacts); ALSN 2014 / 2012; FRT 2008 / 1993; APTV 2010 = 29M wrong / 2011; R 2008 / 1993; CGNX 2008 / 1995; AYI 2016 / 2002; LTH 2019 / 2021; SIRI 2008 / 1998; VICR 2009 / 2001. Missing: FRT and VICR Q2 2026.
S077: FLS 2007 / 1994; HLI 2017 / 2016; SAIA 2016 / 2002; BAH 2017 / 2011; OC 2012 / 2006; GTLB 2020 / 2022; TTEK 2016 / 1996; TXG 2017 / 2019; JXN 2019 / 2021; CUBE 2017 / 2004. Missing quarters: CUBE 1, HLI 1 (FY26 Q1), BAH 3 (2024-09-30, 2024-12-31, 2025-03-31), OC 1 (2024-12-31). Spot checks DI.
S078: PCTY 2012 / 2014 (FY2025 1,471,801K vs filed 1,595,221K); KYMR 2019 / 2020; PRI 2009 / 2010; PCOR 2019 / 2021; CTRE 2012 / 2014 (FY2018 3,379K, FY2021 0, FY2025 1,225K all wrong); CAI 2023 / 2025; CYTK 2009 / 2004; CHWY 2018 / 2020 (labels +1); VMI 2008 / 1994; EAI none / 1993 (32 10-Ks, no FY revenue). Quarter gaps not checked except EAI.
S079: ESI 2014 / 2014; EAT 2009 / 1994; VOYA 2011 / 2014 (FY2018 1,426M and FY2021 1,984M wrong); ALV 2016 / 2001; BRX 2017 / 2014; PNR 2008 / 1994; VNOM 2023 / 2026; CHRD 2016 / 2011; BRKR 2009 / 2001; ADC 2009 / 1997. Missing: ESI and PNR Q2 2026.

General point several workers make: stored history starts about 2008-2011 even where 10-Ks go back to 1993-1996 (XBRL-era limit, expected).

## Population counts quoted

Query or stated population figures:
- S079: 683 companies carry `implausible:institutional_shares_exceed_shares_outstanding` (stated as a count from the coverage table; worker marks it R4; method a query on coverage).
- S079: 789 cells across 189 companies carry `reit_net_interest_income_not_revenue` in the 2026-10-20 coverage (a query result).
- S073: 1,634 of 4,287 trailing_pe values on 2026-10-20 are negative (query on metric values).
- S062: 231 of 5,210 companies with a net_income lineage cite `ProfitLoss` as source tag (stated as a population count; method not shown).
- S069: 168 companies derive operating income as Revenues minus OperatingExpenses (taken from S023, not rerun in this shard).
- S071 per-company ownership rows (queries): MDGL 590 rows for 377 filers, RRX 848/545, DPZ 1,205/786; S074 HSIC 126.9M 13F shares vs 111.4M outstanding (114%), CFR 1,709 filers; S077 SAIA 29.4M (27.37M excluding amendments, 102.6%) vs 26.67M, OC 84.1M (78.7M excluding amendments) vs 79.0M, HLI 57.7M; S063 CCK 254.7M vs 108.8M, FIVE 177.5M vs 55.1M.
- Shard-level coverage counts (from shards.csv or the 2026-10-20 coverage run, 163 cells per company): S077 1,289 filled of 1,630 (79.1%), 160 unexplained; S079 145 unexplained (4+7+22+8+30+6+33+13+4+18); S068 142 unexplained; S064 130 unexplained; S061 190 unexplained; S075 169 unexplained; S065 filled 110-141 of 163; S063 blanks/unexplained per company (BWXT 19/8, MKC 27/10, LII 29/7, IVZ 26/11, CCK 30/13, AFG 66/29, TOL 51/22, FIVE 34/10, INIO 89/37, AIT 17/4); S069 blank/unexplained/filled per company (HII 19/7/144, FDS 19/7/144, EGP 75/38/88, AES 38/12/125, BMRN 31/13/132, SCNI 71/23/92, SAIL 51/21/112, FNF 58/19/105, EVR 55/23/108, GSAT 53/16/110); S078 blanks/unexplained (PCTY 25/15, KYMR 54/25, PRI 53/19, PCOR 36/14, CTRE 46/21, CAI 49/16, CYTK 32/14, CHWY 32/10, VMI 11/6, EAI 87/31); S076 filled counts (ZION 112, ALSN 145, FRT 97, APTV 152, R 133, CGNX 138, AYI 154, LTH 133, SIRI 151, VICR 131).
- Universal four cells: 40 of 130 (S064), 30 of 190 (S061), 40 of 142 (S068), 40 of 145 (S079) unexplained cells per shard.
- Estimates or shard-internal tallies (not population queries): S060 "six of ten companies in one shard have a total-debt problem"; S068 "ebitda `missing:4_consecutive_quarters` at 8 of 10", "institutional implausible at 8 of 10"; S065 "no impossible market caps"; S074 "4 of 10 with institutional overcount"; S066 "book_value_per_share blank at 7 of 10".
- Population counts the workers say they did NOT run (all need chunked core.fact queries): revenue component-beats-total (S061, S063, S065, S068, S070, S075, S078, S079), 0-facts filings (S074, S079), multi-class shares (S064, S067, S072, S077), ProfitLoss vs attributable beyond the 231 figure (S063, S077), stale-as-filled (S064, S068), filings in SEC submissions missing from core.filing (S068, S074), REIT/utility capex tags (S065, S072), multi-registrant combined filings (S078), Q4-by-subtraction errors (S078), HealthCareOrganizationRevenue unmapped (S062), January/52-53-week label shift (S066, S070, S071).
