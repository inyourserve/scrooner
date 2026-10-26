# Verify: retirement Family B, plan 14 (work/data-engineer/derivation-gate aaaf4cc; dryrun_B14_keep), 2026-10-26

Verifier 2. Seed random.Random(20261120). Kit on main (8b651bc) for income statements, plus my own reader for 3 pages; about 110 SEC requests, nothing on disk. Read-only DB on one connection with a 20s timeout. FILING-CHECKED unless marked.

**Ready for apply review: NO.** One cell blocks: CSGP Q4 2023 is shown as 96,475,000, but its FY input is printed 374.7 ($M, one decimal) in every 10-K, so the filing supports 96.5M. Fix that one cell (the scale check missed it) and Family B is ready.

## 1. The two B13 failures: fixed
- **Company 3460 (CIK 0001599617) FY2023:** removed as proxy_filed_copies_disagree (247M original vs 250M restated). Its derived quarters are also removed.
- **ABNB Q4 2022:** 319,000,000. The ABNB FY cells show 1,893M / 4,792M / 2,648M.

## 2. Superseded copies (72) and the 4 demoted 8-K / 2 demoted 10-K/A copies
- **All 72 checked in the DB:** each key ends with exactly one surviving fact. 69 survivors are the precise original of a rounded later copy, or an identical duplicate.
- **20 sampled survivors: right.** E.g. STE 614,641K, SM 770,293K, NXST 971.1M, CHWY 39,580K, CSGP 2023 9M 278,225K, AXTA 267.4M, CIK 0001596532 2,852,054K; MA's duplicate 10-K and CIK 0001022408's identical 8-K copy.
- **Demoted copies carrying a materially different value: 2.** Both are the Pinnacle holdco 8-K (0002082866-26-000020): FY2023 543,705K vs 10-K 562,152K, and FY2024 482,460K vs 475,056K.
  - FILING-CHECKED: that 8-K's income statement is **"Net income attributable to Synovus Financial Corp."** (R5: 791,980 / 482,460 / 543,705), i.e. the merger partner's statements.
  - Demoting them is right.
  - WDAY FY2022 29,000K vs 29,373K is a rounding copy: right.

**URGENT, outside Family B:** the same Synovus 8-K has **410 authoritative facts (187 tags) under Pinnacle's company_id 4938**. Production today shows Pinnacle's FY2025 net income as **791,980K (Synovus)** instead of 641,865K (Pinnacle's 10-K 0002082866-26-000018), and FY2024 `net_income` as 482,460K. Family B only demotes the 8-K facts on its own two keys. Route an 8-K demotion for that accession.

## 3. 15 of 240 promoted facts: right
Each equals its filing face, e.g. Kennametal FY2022/FY2023 144,623K / 118,459K (attributable), CHE 265,238K, GIS -87.6M, BAH 9M 742,295K, Pinnacle 562,152K, CIK 0001679688 70,522K (attributable).
- CIK 0001086745 FY2023 -34,160,455 matches a line labelled "Net loss prior to provision for income taxes"; it equals net loss only if there is no tax (DATA-INFERRED, as in B8).

## 4. 10 random cohort replacements: 9 right, 1 over-precise
- **Right:** SM Q4 2024 188,278K; CMG Q4 2025 330,932K = 1,535,761 - 1,204,829; WTFC 823,844K; DOCU -97,454K; S -288,441K; NFLX 5,407,990K; TGTX 23,037K; DT Q4 FY2026 17,416K; AVAV 59,666K.
- **Over-precise:** CSGP Q4 2023 (above). Scan of all cohort derived quarters for mixed input precision outside the 19 scale-checked cells: CSGP is the only one.

## 5. Restatement scan beyond company 3460
All 443 cohort FY replacements were compared with every later periodic copy of the same key (DB). Only 3 differ by more than 0.5%:
- the 2 Pinnacle cells, where the "copy" is Synovus's 8-K;
- WDAY FY2022, a rounding copy.
20 sampled FY replacements were read in the LATEST 10-K's prior-year column: 20 of 20 equal (e.g. FTNT 1,853.4M, VFC -968,882K, ALGN 421,362K, TJX 4,864M, PH 1,315,605K, PCG 1,800 / 2,593 / -102M attributable, PRAX -214,029K). No other restatement leaks.
