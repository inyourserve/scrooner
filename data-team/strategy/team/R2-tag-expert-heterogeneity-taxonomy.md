# R2. How filers tag the same economic line differently: taxonomy with measured prevalence (Tag Expert, 2026-10-21)

Status: COMPLETE for the 11 concepts asked, on FY2025 10-K face statements. Proposals only: no definition here is approved (Standardization Lead plus a named accountant decide).

## 0. Data, method, evidence classes, limits (read first)
- **Population:** every 10-K in SEC FSDS **2025q4** (already extracted, 353 10-Ks, mostly Sep/Jun FYE) **plus 2026q1** (downloaded this run, 85 MB zip, read straight from the zip, deleted after; 4,262 10-Ks, mostly Dec FYE). One 10-K per CIK (latest period): **N = 4,601 filers**. Families from `sub.sic`: bank (6021-6036, 6712) 320, insurer (6311-6411) 131, REIT (6798) 244, other financial 401, shell/SPAC (6770) 225, utility (49xx) 141, energy (13xx, 29xx) 133, pharma/biotech (2833-2836, 8731) 600, other 2,239, no SIC 167 (mostly commodity/crypto trusts).
- **What was read:** `pre.txt` (statement, report, line, label, negating flag) for the primary IS, BS, CF and BS-parenthetical of each filing; `tag.txt` custom flag; `num.txt` values for the filing's own fiscal year (duration qtrs=4 or instant at the period date), undimensioned and no co-registrant; dimensioned values kept only as a "has a member value" flag. USD/shares units only.
- **FSDS `num.txt` holds only facts that appear on the presented statements, not note facts** (Verifier R7 inbox line, FILING-CHECKED on DLH; I confirmed it on Apple 0000320193-25-000079: 92 distinct tags in `num` = 92 in `pre`). So every count below that says "both filed", "only in notes" or "filed elsewhere" is a **face-statement lower bound**; companyfacts/core.fact coexistence is higher (Tag Mapper file 31 B: RCFC and Revenues differ >1% at 201 of 467 top-1000 companies across periods, vs my 99 of 4,601 on FY2025 faces).
- **How a line was found:** by statement position and label (not by tag name), then the tag on that line was classified. This is the structural lens of file 39 applied per concept. Classifiers are regex rules: the counts are **DATA-INFERRED screening counts, not certified rates**. Their precision was not measured; two false-positive types were found and fixed or noted (sec. 13).
- **Filing checks:** 25 filings were opened on sec.gov (R-files, at most 2 requests per second, declared User-Agent). They prove each pattern EXISTS as described; they do not prove the rate. Every row marked FILING-CHECKED below names the accession and R-file.
- **Not covered:** 10-Q and Q4 derivation; eras before FY2025 (no ASC 606/842 drift measured here); notes (only face statements and the filing's own FY facts); filers reporting in non-USD (they fall into "no FY value"); the calculation linkbase (FSDS has no `cal`, so every "a calc tree resolves it" verdict below is ASSUMED unless it cites the one FILING-CHECKED CVX calc case in ledger 22). No database read (not needed; pooler was reported at 21 connections).
- Scripts (read-only, `python3 -I`): `scratchpad/scripts/extract.py`, `common.py`, `taxo.py`, `ce.py`, `cx2.py`, `extra.py`, `fetchr.py` in this session's scratchpad. They are NOT in the repo (I may write only this file); the Data Engineer should copy them into `data-team/strategy/tools/` if this is adopted.

## 1. The pattern classes (one vocabulary for every concept)
| Code | Pattern | What it means |
|---|---|---|
| P1 | Synonym tag | Different standard tags carry the same economic line (Revenues vs RCFC; CostOfRevenue vs CostOfGoodsAndServicesSold) |
| P2 | Narrower / broader tag | The tag on the line is a subset or superset of the concept (RCFC = fee line only; Revenues includes other income) |
| P3 | Company extension | The line is on a custom tag |
| P4 | Sign convention | Stored sign differs from the "natural" sign (net credit tags for expenses; negating labels; stored negatives on non-negative tags) |
| P5 | Inclusion difference | Same line name, different contents (D&A with or without intangibles/accretion; debt with or without leases; cash with or without restricted cash; revenue gross or net of excise) |
| P6 | Sub-total vs components only | Filer shows parts and no total, or a total whose parts sit in different places |
| P7 | Dimension-only | The face row uses a generic tag plus an axis member; there is no undimensioned total fact |
| P8 | Label shift | The tag says one thing, the row label says another (OperatingIncomeLoss on "Income before income taxes") |
| P9 | Cross-statement perimeter | The "same" line differs between statements of one filing (IS D&A vs CF D&A; IS parent NI vs CF consolidated NI) |
| P10 | Template absence | The line does not exist for the business model (banks: no revenue/COGS/OI line). Not a tagging problem; listed so it is not counted as one |

## 2. Prevalence summary (DATA-INFERRED, N = 4,601 FY2025 10-K filers)
"Line filers" = filers where the face line was found. Shares are of line filers unless marked "of N".

| Concept | Line filers | Dominant tag share | Main heterogeneity found (count) |
|---|---|---|---|
| Total revenue | 3,443 (+317 banks with no revenue line) | RCFC 1,732 (50%); Revenues 1,333 (39%) | RCFCIncl 247; other standard 89 (utility 22, premiums, lease income); custom total 25; RCFC and Revenues both filed and different 99; dimension-only total 24; excise gross+net 7; label "and other income" 12 |
| Cost of revenue | 2,278 (2,297 have none, 49.9% of N) | COGS 1,151 (51%); CostOfRevenue 769 (34%) | excludes D&A 276 (12%); dimension-only 158 (7%); custom 74; components only 66; other standard 36 |
| Operating income | 3,405 (1,170 have none, 25% of N) | OperatingIncomeLoss 3,379 (99%) | label shift 30; Rev minus total-cost line != OI 189 of 2,184 tested (8.7%); CostsAndExpenses has 4 perimeters (sec. 5) |
| Net income | ~4,460 | NetIncomeLoss only 3,053 | both ProfitLoss and NetIncomeLoss 1,114 (NCI non-zero 750); ProfitLoss only 294; CF starts with ProfitLoss while IS bottom line is parent 724 |
| D&A (CF) | 3,871 | DDA 1,543 (40%) | split into 2-3 lines 911 (24%); custom 151 single + 321 in splits; DepreciationAndAmortization 552; Depreciation only 336; accretion in line 162; depletion 156; DDA and DA both filed and different 95 |
| Capex (CF) | 3,226 | PaymentsToAcquirePPE 2,564 (79%) | multiple capex lines 264; PaymentsToAcquireProductiveAssets 305; custom 176; software line 304; PPE tag plus other lines 193 (other lines >= 10% of PPE line at 152) |
| Interest expense (non-bank IS) | 3,133 | InterestExpenseNonoperating 1,419 | net tags 569; gross tag on a "net" label 388; net tag on a plain "interest expense" label 57; custom 210; only in notes 44; 357 show 2+ interest lines |
| Total debt (BS) | 3,857 | no single dominant tag | 1 line 663, 2 lines 1,266, 3-4 lines 1,493, 5+ 435; debt-plus-lease tag on a debt-only label 297; combined debt+lease rows 88; commercial paper 32; custom debt row 512 (13%) |
| Cash | 4,458 | CCE 3,365 (75%) | CashAndDueFromBanks 280 (banks); Cash 440; restricted-inclusive total tag on the BS 272 (207 labelled plain "cash and cash equivalents"); separate restricted-cash row 1,198 |
| Shares outstanding (BS) | 4,575 | undimensioned 3,112 (68%) | dimension-only per class 682 (15%); issued only, no outstanding 430; none on BS 327; custom 18 |
| EPS | 4,339 | EarningsPerShareBasic 4,131 (95%) | per-class only (dimension-only) 227; continuing-ops tag only 71; custom only 40; diluted only 54 |

Cross-cutting (DATA-INFERRED): custom tags are 7.8% of IS face lines (2,836 filers have at least one), 5.2% of BS lines, **16.3% of CF lines** (4,309 of 4,537 CF filers have at least one). **946 filers (20.6% of N) have at least one IS face row whose FY value exists only with a dimension member** (P7).

## 3. Total revenue
| Pattern | n (share of 3,443) | Family concentration | Examples (adsh) | Evidence |
|---|---|---|---|---|
| P1 synonym: RCFC vs Revenues vs RCFCIncl as the face total | RCFC 1,732; Revenues 1,333; RCFCIncl 247 | Revenues dominates insurers (104/131), REITs (161), utilities (80); RCFC dominates "other" (1,305) | RCFC: 0001628280-26-010185 Abbott; Revenues: 0000066740-26-000014 3M; RCFCIncl: 0001193125-26-067467 Boston Beer | DATA-INFERRED |
| P1 sector totals | 22 utilities (RegulatedAndUnregulatedOperatingRevenue 17, RegulatedOperatingRevenue 3), PremiumsEarnedNet 9, OperatingLeaseLeaseIncome 4 | utility, insurer, REIT | file 39: NJR, Spire, TVA | DATA-INFERRED |
| P2 narrower RCFC beside a face total `Revenues` | 99 filers file both, different; RCFC smaller in 96 (face total is Revenues in 93) | REIT 24, other_fin 17, energy 13, insurer 6 | **UDR 0000074208-26-000013 R4**: RCFC = "Joint venture management and other fees" 11,361K vs Revenues "Total revenues" 1,712,317K; CNA 0000021175-26-000011; Helmerich & Payne 0000046765-25-000071 | UDR FILING-CHECKED; others DATA-INFERRED |
| P2 broader: `Revenues` includes other income | 12 label hits; true count larger (XOM's label is just "Revenues") | energy 5 | **XOM 0000034088-26-000045 R3**: `Revenues` 332,238M = total revenues AND other income (sales 323,905M, equity-affiliate income 5,064M and other income 3,269M are dimension members of the same tag); **Dillard's 0000028917-26-000006 R4**: Revenues "Total net sales and service charges and other income" 6,563,336K vs RCFC "Net sales" 6,473,623K; CVX 0000093410-26-000078 (card) | FILING-CHECKED |
| P3 custom total, standard tag is the narrower line | 25 | energy 6, other_fin 5 | **COP 0001163165-26-000009 R3**: total "Total revenues and other income" 61,548M on custom `cop_RevenuesAndOtherIncome`; `Revenues` = "Sales and other operating revenues" 58,944M. APA 0001841666-26-000015; Interactive Brokers 0001381197-26-000062 | COP FILING-CHECKED |
| P5 excise: gross and net both on face | 7 | beverage, cannabis, oil | **Boston Beer 0001193125-26-067467 R2**: RCFCIncl "Revenue" 2,087,251K, custom `sam_LessExciseTaxes` 122,257K, `Revenues` "Net revenue" 1,964,994K; Molson Coors 0000024545-26-000006; Imperial Oil 0000049938-26-000009 | Boston Beer FILING-CHECKED |
| P7 dimension-only total | 24 | pharma 6 | Ares Capital 0001287750-26-000006; Geron 0000886744-26-000008; L3Harris 0000202058-26-000015 | DATA-INFERRED |
| P6 components only, no total | 16 after fixing the classifier | insurers 4, funds 8 | PennyMac Financial 0001104659-26-018142; Primerica 0001193125-26-082233; Prudential 0001137774-26-000048 | DATA-INFERRED (classifier had 32 false positives before the fix, sec. 13) |
| P10 bank template | 317 banks have no revenue line | bank | 1st Source 0000034782-26-000011; Ally 0000040729-26-000005; Ameris 0000351569-26-000050 | DATA-INFERRED; card revenue.md FILING-CHECKED |

Revenue identity: revenue - cost of revenue = gross profit passes 1,371 of 1,383 testable filers (99.1%); fails 12 (Altria 0000764180-26-000017, Criteo 0001576427-26-000014, Glaukos 0001193125-26-061944: excise or a total-tag choice, not opened).

Resolvable by structure? P1 yes (position plus the identity above). P2 and P3: the filer's calc tree shows what sits under the tag (XOM: equity income under Revenues; COP: Revenues under the custom total), so **the tree can identify the perimeter (ASSUMED; FSN `cal` not loaded)**, but **which perimeter the product calls "revenue" (with or without other income, gross or net of excise) is a human rule**. P7 needs the member values, which FSDS has.

## 4. Cost of revenue
| Pattern | n (share of 2,278 line filers) | Families | Examples | Evidence |
|---|---|---|---|---|
| P1 COGS vs CostOfRevenue | 1,151 / 769 | both everywhere | Abbott 0001628280-26-010185 (COGS); 3M 0000066740-26-000014 (CostOfRevenue); A10 0001580808-26-000014 | DATA-INFERRED (card: AAPL/DHI/BBW checked) |
| P5 excludes D&A (label or `...ExcludingDepreciation...` tag) | 276 (12%); tag used by 170 | other 198, utility 18, energy 16 | Abercrombie 0001018840-26-000012; ACV Auctions 0001637873-26-000011; Alcoa 0001193125-26-077167 | DATA-INFERRED |
| P7 dimension-only cost rows | 158 (7%) | other 110, utility 11, energy 11 | **AMH 0001562401-26-000010 R5**: `CostOfGoodsAndServicesSold` used twice with members "Property operating expenses" 663,954K and "Property management expenses" 134,808K, no undimensioned value; **BRK 0001193125-26-083899 R4**: cost lines exist only per segment group (160,062M; custom `brka_CostOfLeasing` 7,685M; custom 16,959M), only "Total costs and expenses" 318,473M is undimensioned; Antero 0001104659-26-013386 | AMH, BRK FILING-CHECKED |
| P3 custom | 74 | pharma 20 | ADT 0001703056-26-000022; Apellis 0001193125-26-065179; Cars.com 0001193125-26-076546 | DATA-INFERRED |
| P6 components only | 66 | pharma 16, other 41 | Alnylam 0001628280-26-007497; AMN 0001628280-26-009918; BrightSpring 0001193125-26-079454 | DATA-INFERRED |
| P4 negating label on the cost row | 176 (display only; stored positive) | other 140 | Amentum 0001628280-25-053993; Autoliv 0001193125-26-058162; Ball 0001104659-26-017410 | DATA-INFERRED |
| P10 no cost-of-revenue line | 2,297 (49.9% of N) | bank 317, pharma 369, REIT 222, other_fin 319, shells 223, other 403 | 1st Source; AbCellera 0001703057-26-000012; ABM 0000771497-25-000031 | DATA-INFERRED |
Resolvable: P1 and P7 by structure (GP identity; member sum to the undimensioned total). P5 (ex-D&A) is visible in tag/label but whether to add D&A back is a **human rule**. P10 needs the sector template, and "no line in XBRL" is not "no line in filing" (ledger 22).

## 5. Operating income
| Pattern | n | Families | Examples | Evidence |
|---|---|---|---|---|
| P1 one tag | OperatingIncomeLoss on 3,379 of 3,405 OI lines (99%) | | Apple, 3M | card FILING-CHECKED |
| P8 label shift: `OperatingIncomeLoss` on a different line | 30 | all families | **AFG 0001042046-26-000010 R5**: "Earnings before income taxes" 1,073M = revenues 8,174M - costs 7,101M; **ELS 0001628280-26-008722 R5**: "Income before taxes and other items" 391,349K; PEBO 0000318300-26-000099 ("Income before income taxes"); BANR 0000946673-26-000009 ("Total non-interest income", known quirk, recurs in FY2025) | AFG, ELS FILING-CHECKED; PEBO/BANR FSDS label, quirk FILING-CHECKED earlier |
| P2 the total-cost line has 4 perimeters (`CostsAndExpenses`, 958 filers on the face) | A: revenue - CE = OI 651 (68%); B: CE = operating expenses only, GP - CE = OI 29; C: revenue - CE = pretax (interest inside) 42; D: no OI line 115 (REITs 65, GE); E: other operating items between CE and OI 64 | C: energy, other_fin; D: REIT | B: **HP 0000047217-25-000071 R3** "Total operating expenses" 8,218M = GP 11,392M - OI 3,174M; Arrow 0001104659-26-012765; Zillow 0001617640-26-000015. C: **XOM 0000034088-26-000045 R3** (interest expense 603M inside "Total costs and other deductions" 290,970M; revenue - CE = pretax 41,268M); BMS 0000014272-26-000004; SWK 0000093556-26-000009. E: S&P Global 0000064040-26-000013; UDR; RTX 0000101829-26-000006 | HP, XOM FILING-CHECKED; CVX/AJG/HTZ already in ledger 22 |
| Identity revenue - "total costs/expenses" line = OI | passes 1,995, fails 189 (8.7%) | fails: REIT 33, other_fin 24 | Acadia Realty 0001193125-26-051677; AdaptHealth 0001628280-26-011213; Agree Realty 0000917251-26-000013 | DATA-INFERRED |
| P3 custom OI | 4 | | BrightSpire 0001717547-26-000008; Bristow 0001525221-26-000013; CNX 0001070412-26-000038 | DATA-INFERRED |
| P10 no OI line | 1,170 (25% of N): bank 313, insurer 101, REIT 152, other_fin 203, no-SIC 160 | | 1st Source; abrdn trusts | DATA-INFERRED |
Resolvable: P8 partly by identity (a tag whose value equals revenue minus all costs and whose next row is income tax is pretax), fully by the calc tree if interest is a child (ASSUMED). The CE perimeter split above was resolved **by identities alone** for 722 of 901 filers with a revenue total (A+B+C); E (64) needs the calc tree or a human read. Deciding whether REIT/insurer "operating income" should exist at all is a **human (sector) rule**.

## 6. Net income (attributable vs including NCI)
| Pattern | n | Families | Examples | Evidence |
|---|---|---|---|---|
| P1/P2 ProfitLoss and NetIncomeLoss both on face | 1,114; NCI non-zero (values differ) 750 | REIT 132, other 614 | **ANF 0001018840-26-000012 R3**: ProfitLoss "Net income" 514,995K, NetIncomeLoss 506,921K; AbbVie 0001551152-26-000008; Acadia Healthcare 0001193125-26-078266 | ANF FILING-CHECKED |
| P1 ProfitLoss is the only "net income" row | 294 (194 with no NCI at all; 100 with NCI) | REIT 48 | **1st Source 0000034782-26-000011 R5**: ProfitLoss "Net income" 158,259K; parent figure tagged `NetIncomeLossAvailableToCommonStockholdersBasic` 158,277K; Adeia 0001193125-26-076549; Alarm.com 0001459200-26-000005 | 1st Source FILING-CHECKED |
| P1 consolidated line on another tag (`IncomeLossFromContinuingOperationsIncludingPortion...`) or custom | 27 filers have an NCI row but no ProfitLoss | | Masco 0000062996-26-000005; Wells Fargo 0000072971-26-000133; 3M 0000066740-26-000014 | DATA-INFERRED |
| P9 CF starts with consolidated ProfitLoss, IS bottom line is parent | 724 | REIT 101, other 390 | ANF R7 starts "Net income" 514,995K (ProfitLoss) vs IS parent 506,921K; Acadia Realty; Acadian Asset Mgmt 0001628280-26-012856 | ANF FILING-CHECKED |
| P2 "available to common" differs from NI (preferred dividends, participating securities) | 369 | bank 61, REIT 61 | AES 0000874761-26-000063; AGNC 0001423689-26-000043; Agree Realty | DATA-INFERRED |
| CF starts at continuing operations | 43 | | Alight 0001628280-26-011108; Aramark 0001584509-25-000219; Baxter 0001628280-26-007733 | DATA-INFERRED |
Identities: ProfitLoss - NCI = NetIncomeLoss passes 891 of 907 (98.2%); 16 fail (Aptiv 0001521332-26-000009, Acadia Realty, BlackLine 0001628280-26-011915: redeemable NCI or preferred units, not opened). File 39's IS-vs-CF NI identity (324/324) is consistent. **Fully resolvable by structure** once the policy names the basis (parent vs consolidated) - that choice is human, but it is a one-time global rule, not per company.

## 7. D&A (cash-flow add-back)
| Pattern | n (share of 3,871 line filers) | Families | Examples | Evidence |
|---|---|---|---|---|
| P1 one combined line, different standard tags | DDA 1,543; DepreciationAndAmortization 552; DepreciationAmortizationAndAccretionNet 200 (bank 65); Depreciation only 336 (pharma 142) | | 3M (DDA); Abercrombie (D&A); Allstate 0000899051-26-000031 (accretion) | DATA-INFERRED |
| P6 split into 2-3 lines | 911 (24%) | bank 148, other 468 | Abbott 0001628280-26-010185; AbbVie 0001551152-26-000008; Alamo 0000897077-26-000016 | DATA-INFERRED |
| P6+P2 a combined tag PLUS other D&A lines (the tag alone understates) | 300; other lines >= 10% of the combined line at 162 (median 14%) | REIT 36, utility 24 | Ameren 0001002910-26-000009; ADMA 0001140361-26-006815; Alpha Metallurgical 0001704715-26-000010 | DATA-INFERRED (one false positive seen: Hercules "unrealized appreciation/depreciation") |
| P3 custom single line | 151 (+321 custom inside splits) | REIT 19, energy 11 | **AAL 0000006201-26-000014 R7**: "Depreciation and amortization" 2,219M on `aal_MainlineAndExpressDepreciationAndAmortization`; American Tower 0001053507-26-000035; Americold 0001628280-26-012274 | AAL FILING-CHECKED |
| P5 broader single line ("and other") | DepreciationAmortizationAndOther / OtherDepreciationAndAmortization 45+ | | **Accenture 0001467373-25-000217 R8** "Depreciation, amortization and other" 2,441,594K | FILING-CHECKED |
| P5 accretion / depletion inside | 162 / 156 | accretion: bank 65; depletion: energy 83 | Adobe 0000796343-26-000003; AES; Antero | DATA-INFERRED |
| P5 ROU amortization as a separate line (in or out of D&A is a choice) | 493 | | 10x Genomics 0001628280-26-007822; AAON 0000824142-26-000005 | DATA-INFERRED |
| P9 IS D&A differs from CF D&A | 95 file both DDA and DA with different values | REIT 14 | **AEO 0001193125-26-132097**: IS R4 "Depreciation and amortization expense" 211,961K vs CF R8 222,180K; American States Water 0001628280-26-009114; Bristow 0001525221-26-000013 | AEO FILING-CHECKED |
Resolvable: the split lines are resolvable by position (all D&A-type add-backs in the CFO section) **but which add-backs belong in D&A (intangibles yes? ROU? accretion? inventory step-up? debt-cost amortization?) is a human rule**, and a single custom or "and other" line cannot be decomposed from structure at all (content is in the notes).

## 8. Capex
| Pattern | n (share of 3,226) | Families | Examples | Evidence |
|---|---|---|---|---|
| P1 standard tag | PaymentsToAcquirePPE 2,564 (79%); PaymentsToAcquireProductiveAssets 305 (broader: includes intangibles); OtherPPE 55; CapitalImprovements 41 (REIT) | | 3M; Abbott; Akamai | DATA-INFERRED |
| P6 multiple capex lines | 264; PPE tag plus other lines 193, other lines >= 10% of the PPE line at 152, median other/PPE = 1.35 | other 184 | **Air Lease 0001628280-26-007707 R8**: PPE tag only on "aircraft furnishings, equipment and other assets" 237,683K; the main line "Acquisition of flight equipment" 2,348,253K is `PaymentsForFlightEquipment`, deposits 1,045,667K custom; DoorDash 0001792789-26-000013 (capitalized software line bigger than PPE); REPAY 0001193125-26-098518 | Air Lease FILING-CHECKED |
| P5 software capex separate | 304 | other 215 | ACI Worldwide 0000935036-26-000011; Alarm.com; Alkami 0001529274-26-000009 | DATA-INFERRED |
| P3 custom | 176 | REIT 30, energy 18 | Air Lease; American Healthcare REIT 0001193125-26-082692; AMH 0001562401-26-000010 | DATA-INFERRED |
| P5/P8 "net" in label | 134 (banks 56) | | **ADI 0000006281-25-000153 R10**: "Additions to property, plant and equipment, net" 533,552K beside a separate proceeds line; Allstate; Americold | ADI FILING-CHECKED (label only) |
| P4 stored negative | 18 | | BorgWarner 0000908255-26-000011; Sonic Automotive 0001628280-26-010570; Flagstar 0000910073-26-000025 | DATA-INFERRED, quarantine candidates |
Resolvable: lines are found by structure (investing section, "payments for" family); **whether flight equipment, software, real-estate development or intangibles count as capex is a human rule**; the name path (PPE tag) understates capex at about 152 filers by at least 10%.

## 9. Interest expense (non-banks; banks: 298 of 317 use InterestExpenseOperating, 14 InterestExpense)
| Pattern | n | Examples | Evidence |
|---|---|---|---|
| P1 gross tags | Nonoperating 1,419; InterestExpense 538; Operating 199 (non-bank lenders, REITs); Debt 132; InterestAndDebtExpense 91 | Abbott; Accenture; Amgen 0000318154-26-000010 (Debt) | DATA-INFERRED |
| P2 net tags (interest income netted in) | 569 (InterestIncomeExpenseNonoperatingNet 363, InterestIncomeExpenseNet 197, InterestRevenueExpenseNet 9) | AbbVie (Nonop net); AAON; TJX 0000109198-26-000008 | DATA-INFERRED |
| P8 gross tag on a "net" line | 388 (284 with no separate interest-income row) | **Agree Realty 0000917251-26-000013 R5**: `InterestExpenseNonoperating` labelled "Interest expense, net" (134,612K); Accendra 0001104659-26-018169; Alliance Resource 0001104659-26-020468 | Agree FILING-CHECKED |
| P4+P8 net tag on a plain "Interest expense" label, stored negative | 57 | **AAON 0000824142-26-000005 R4**: `InterestIncomeExpenseNet` "Interest expense" (17,726) stored -17,726K; Advance Auto 0001193125-26-051305; Akebia 0001517022-26-000020 | AAON FILING-CHECKED |
| P4 stored negative on a gross expense tag | 19 | Ecolab 0001104659-26-018357; LKQ 0001065696-26-000012; Okta 0001660134-26-000020 | DATA-INFERRED, quarantine candidates |
| P3 custom | 210 | A10; Align 0001097149-26-000014; Amex 0000004962-26-000080 | DATA-INFERRED |
| Not on the income statement, but an interest-expense fact is on another presented statement (lower bound: FSDS has no note facts) | 44 | Alexandria 0001035443-26-000013; AMC 0001411579-26-000016; AJG 0001628280-26-008662 | DATA-INFERRED (AJG card FILING-CHECKED) |
Resolvable: tag direction and sign by structure (balance type, negating flag, calc weight); **gross vs net is NOT resolvable when the filer shows one netted line** (the gross figure is only in a note, if at all): human rule plus note reading.

## 10. Total debt (short + long + leases + commercial paper)
| Pattern | n (share of 3,857 BS debt filers) | Examples | Evidence |
|---|---|---|---|
| P6 total built from several rows | 1 row 663; 2 rows 1,266; 3-4 rows 1,493; 5+ rows 435 | AdaptHealth 0001628280-26-011213 (5+); AbbVie (3-4) | DATA-INFERRED |
| P2/P8 debt-plus-lease tag on a "debt" row | 297 (283 with no separate finance-lease row) | **CAT 0000018230-26-000008 R5** and **APD 0000002969-25-000055 R6** (`LongTermDebtAndCapitalLeaseObligations*` on "Long-term debt"); Accenture | CAT, APD FILING-CHECKED |
| P7 dimension-only debt rows | CAT: long-term debt shown only per segment (two member blocks: 35M + 10,678M and 7,085M + 20,018M; CAT's columns are Machinery-Energy-Transportation and Financial Products, member names not read from the instance) with no consolidated undimensioned fact; APD: two "Long-term debt" rows (16,769.9M and 177.5M in a second block, member not identified), no undimensioned FY fact in FSDS | Caterpillar; Air Products | FILING-CHECKED (rendering) + DATA-INFERRED (no undimensioned fact) |
| P5 leases as separate rows | operating lease 1,947; finance lease 316; lease unspecified 539; combined debt+lease row 88 | 10x Genomics; AMC 0001411579-26-000016; AbbVie | DATA-INFERRED |
| P5 commercial paper | separate 25; combined with notes 7 | Apple 0000320193-25-000079; Duke 0001326160-26-000014 ("Notes payable and commercial paper", card); Analog Devices | Duke FILING-CHECKED (card) |
| P3 custom debt row | 512 (13%) | 1st Source; ADTRAN 0001193125-26-073878; AES | DATA-INFERRED |
| Bank borrowings (FHLB advances) | 99 rows (60 banks) | Amerant 0001734342-26-000017; Banner; Beacon 0001628280-26-013247 | DATA-INFERRED |
| Total not on the BS face / no BS debt row | LongTermDebt filed on another presented report but not as a BS row 34; no BS debt row but LongTermDebt filed 31 (BDCs). Lower bounds (no note facts in FSDS) | Air Lease; Blue Owl Capital Corp 0001655888-26-000010; Blackstone Secured Lending 0001736035-26-000004 | DATA-INFERRED |
Resolvable: summing rows is structural (BS calc tree: the rows roll into Liabilities). **Which rows count as debt (operating leases, finance leases, related-party notes, FHLB advances, deposits) is a human rule**; LongTermDebt at face value (AMZN, GOOG, ledger 22) is not detectable from structure, only from a carrying-amount comparison.

## 11. Cash and equivalents (incl. restricted)
| Pattern | n (share of 4,458) | Examples | Evidence |
|---|---|---|---|
| P1 CCE tag | 3,365 (75%) | 3M; Abbott | card FILING-CHECKED |
| P1 bank tag `CashAndDueFromBanks` (+ separate interest-bearing deposits row) | 280; banks show 2+ cash rows (215) | 1st Source; Amerant; American Express 0000004962-26-000080 | DATA-INFERRED |
| P8 plain `Cash` tag labelled "cash and cash equivalents" | 23 | **Badger Meter 0001193125-26-054739 R2** (226,016K); PGR 0000080661-26-000086 (card); Green Brick 0001628280-26-011798 | Badger FILING-CHECKED |
| P2/P8 restricted-inclusive total tag on the BS cash row | 272; 207 labelled plain "cash and cash equivalents" | **Cummins 0000026172-26-000009 R5** "Cash and cash equivalents" 2,845M on `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents`; Dover 0000029905-26-000009; Omnicom 0000029989-26-000006 | Cummins FILING-CHECKED (presentation); restricted content NOT verified |
| P5 restricted cash as a separate BS row | 1,198 | AAON; AbCellera; Acadia Pharmaceuticals 0001193125-26-072519 | DATA-INFERRED |
| P3 custom | 26 | AECOM 0000868857-25-000013; BorgWarner; CVX (card) | DATA-INFERRED |
| Combined with short-term investments | 9 | Kroger 0001104659-26-037723; Masco; International Paper 0000051434-26-000055 | DATA-INFERRED |
Identity CF ending cash (restricted-inclusive) vs BS: equals BS cash 2,128; equals BS cash + restricted rows 719; needs reconciliation 660 (banks 191, i.e., the bank cash rows). **Mostly resolvable by the identity**; the 207 "plain label on a restricted-inclusive tag" cases are not (does the figure contain restricted cash or not? a note read, human).

## 12. Shares outstanding and EPS
| Pattern | n | Examples | Evidence |
|---|---|---|---|
| P7 BS shares outstanding only per class | 682 (15% of N; shells 181) | **Accenture 0001467373-25-000217 R4** (parenthetical shows class-level counts only, e.g. 302,358 outstanding for one class); ACV 0001637873-26-000011; ADT 0001703056-26-000022 | Accenture FILING-CHECKED |
| BS shows shares issued only, not outstanding | 430 | Abbott; AbbVie; 1st Source | DATA-INFERRED |
| No share count on BS | 327 | AAON; AES; Alcoa | DATA-INFERRED |
| P7 EPS only per class | 227 (shells 115) | **Baker Hughes 0001701605-26-000007 R3**: "Basic income per Class A common share" 2.62, no undimensioned EPS fact; ADT; AST SpaceMobile 0001780312-26-000006 | Baker Hughes FILING-CHECKED |
| P1 continuing-ops EPS tag used as the only EPS | 71 | **Airbnb 0001559720-26-000004 R5**: "Basic (in USD per share)" 4.10 on `IncomeLossFromContinuingOperationsPerBasicShare`; ANDE (ledger 22); Agilon 0001628280-26-011655 | Airbnb FILING-CHECKED |
| P3 custom EPS only | 40 (energy 13: LP unit EPS) | BXP 0001037540-26-000006; Advantage Solutions 0001193125-26-088543; Horizon Technology Finance 0001437749-26-006636 | DATA-INFERRED |
| Weighted shares only per class | 201 | ADT; Bel Fuse 0001437749-26-005354; BRK (card) | DATA-INFERRED |
Resolvable: class members are structural (sum the classes for shares; never sum EPS). **Per-class EPS cannot be turned into one issuer EPS by structure**; it needs a rule (show per class, or use the class with the conversion ratio, BRK). Continuing-ops-only EPS equals total EPS only when there are no discontinued operations: an identity (NI = continuing NI) can confirm it.

## 13. Classifier errors found (calibration)
- Revenue "components only" first counted 48; Boston Beer (gross, excise, net) and Exponent (a total without the word "total") were false positives. After adding a standard-total check: 16. Lesson: a label rule must accept a standard total tag as the total even without "total" in the label.
- D&A "other lines" list included Hercules Capital's "unrealized appreciation/depreciation" (an investment fair-value line). The ratio counts in sec. 7 carry that noise.
- Revenue "no USD FY value" (82) is mostly Canadian/foreign filers reporting in CAD etc. (CP 0000016875-26-000008, Enbridge 0001193125-26-049810): a unit pattern, not a tagging one.
- No classifier precision was measured; counts are screening signals (as in file 39).

## 14. What a calculation tree or identity can resolve, and what it cannot
Resolvable from structure (FSDS pre/num + FSN cal/dim), proposed for build:
1. **P1 synonyms** for every concept (position + GP / OI / NI identities): revenue, COGS, NI, EPS, cash. Identities pass 98-99% where testable.
2. **P6 sub-total vs components**: sum the rows or the dimension members to the undimensioned total (CAT, BRK, AMH).
3. **P7 dimension-only**: FSDS `num.segments` already carries the members; 20.6% of filers have at least one such IS row.
4. **P9 cross-statement**: ProfitLoss - NCI = NetIncomeLoss (891/907); CF ending cash = BS cash (+ restricted) (2,847 of 3,507).
5. **P4 display sign**: negating flag + balance type. Stored-sign errors are detectable (19 interest, 18 capex), not fixable, by structure: quarantine.
6. **Perimeter detection** for totals whose components are on the face (CostsAndExpenses A/B/C classes resolved by identity for 722 filers; XOM/COP by the calc tree, ASSUMED).

NOT solvable from structure alone (needs a human rule, a note read or an accountant):
1. **Which perimeter is the product's definition**: revenue with or without other income and excise; D&A with or without intangibles, ROU, accretion; capex with or without software, flight equipment, real-estate development; debt with or without operating/finance leases, related-party notes, FHLB advances; NI parent vs consolidated. Structure can show the perimeter; it cannot choose it.
2. **Single composite line with no components on the face** (AAL custom D&A, Accenture "and other", a single netted interest line, Cummins cash on a restricted-inclusive tag): content lives in note text.
3. **Gross vs net interest** when only the net line is shown (569 net-tag filers + 388 gross tags on net labels).
4. **Label shifts with no arithmetic signature** (a mis-tag whose value is plausible both ways; BANR "non-interest income" is caught only by label).
5. **Filer context errors** (GE quarterly revenue = GE Capital, ledger 22): needs Q-sum vs FY checks, not structure.
6. **Custom dimension members** (CAT "ME&T" vs "Financial Products"): which members to include is a definition.
7. **Template absence vs vocabulary miss** (2,297 with no COGS line; 1,170 with no OI): needs the sector template plus the rendered statement.

## 15. Recommendation (proposal; owners per data-team roles)
1. Adopt this 10-class vocabulary (sec. 1) as the `finding_type` sub-classification for tag findings, so Triage and the Verifier speak the same language. Owner: Triage + Tag Expert.
2. Build the structural layer in this order, all read-only first: (a) identity suite (GP, OI from total-cost line, PL-NCI=NI, CF cash = BS cash + restricted, member sum = total) over FSDS for all 10-K filers per quarter; (b) per-company **perimeter record** for the 5 composite concepts (D&A, capex, interest, total debt, cash): which rows/tags/members make up the value, from face rows plus FSN `cal`/`dim`; (c) name-path vs structure disagreement report. Owner: Data Engineer; Verifier samples 10 companies x 3 concepts.
3. Before (b) is useful, the Standardization Lead and a named accountant must write the 6 perimeter definitions in sec. 14 item 1. Without them, structure only describes the disagreement.
4. Quarantine, never flip: stored negatives on non-negative tags (37 cases above) and label shifts on OperatingIncomeLoss (30) become `company_data_finding` rows for the Verifier.
5. Measured payoff targets (to verify): capex understated by name path at ~152 filers, D&A at ~162, total-cost perimeter wrong for ~42+64 OI derivations, 207 cash rows of uncertain perimeter, 682 + 227 class-only share/EPS filers.

## 16. Risks and what would change this
- Regex classifiers: precision unknown; a 50-filer filing-checked sample per main pattern is needed before any count drives a decision. If precision on the composite patterns is below about 80%, the counts above should be read as upper bounds.
- One fiscal year, 10-K only: 10-Q quarters, Q4 derivation and pre-2019 eras (ASC 606/842 tag switches) are untested; the 2025q4 slice is September-FYE heavy, 2026q1 is December-FYE heavy, so the pooled set is broad but still one year.
- The calc-tree claims are ASSUMED except CVX (ledger 22). If FSN `cal` shows filers do not attach custom D&A/capex lines to identifiable parents, structure resolves less than stated in sec. 14.
- What would change my mind: a Verifier sample showing that most "perimeter" differences are immaterial (<1% of the value) would demote P5 from a build item to a disclosure note.
