# Verify: duplicate-column merge (origin/work/engineering/duplicate-column-merge f843251, data-team/40-duplicate-columns/verifier-draw.jsonl), 2026-11-02

The package's draw: 10 merges, 10 hides, plus ATI FY2022 NI (requested; not in the draw). Evidence: both copies' facts and accessions from core.fact (DATA-INFERRED for all 20), and face reads (FILING-CHECKED) for ITT Q2 2020 and ATI Q2 2022, FY2022. Verifier 2 (scrooner-bc).

## Result
- **Merges: YES.** 10 of 10. The two periods carry identical values from their filings, and the end dates differ only by fiscal-calendar labelling (e.g. ITT Q2 2020: the 2021 10-Q's comparative column "Jun. 27, 2020" prints 514.7M, the same value the 2020 10-Q tags at Jun 30).
- **Hides: YES.** 10 of 10 show genuinely different printed values: recasts and restatements (YUM, MTSI, ATI x2), predecessor or merged-entity changes (ONTO Nanometrics/Rudolph x2, VTRS Mylan/Upjohn), a pre-IPO stub period (EPRT Jun 24 vs Jun 30), and fresh-start emergence balance sheets (CHRD Nov 18 vs Nov 19, 2020).
- **ATI FY2022 NI:** both printed and genuinely different. The FY2022 10-K (0001628280-23-005017) shows 130.9M for the year ended Dec 31, 2022. The FY2024 10-K (0001628280-24-006606) shows 323.5M for the fiscal year ended Jan 1, 2023 (recast). Hide right (or show the latest recast under the restatement policy).
- ATI Q2 2022 face (0001628280-22-021008): net loss attributable to ATI (38.0)M as filed; 6.7M appears only in the later recast.

## Cell list
| Action | Ticker | Tag | Canonical (period, value, filings) | Duplicate (period, value, filings) | Verdict |
|---|---|---|---|---|---|
| merge | THG | EPS diluted Q1 2019 | Jan 1-Mar 31, 2.97 (10-Qs) | Jan 2-Mar 31, 2.97 (10-Ks) | right |
| merge | CIEN | Gross profit Q4 FY2018 | to Oct 31, 398,075K | to Nov 3, 398,075K | right |
| merge | WAT | NI to common Q1 2023 | to Apr 1, 140,923K | to Mar 31, 140,923K | right |
| merge | ITT | Revenues Q2 2020 | Apr 1-Jun 30, 514.7M | Mar 29-Jun 27, 514.7M (face read) | right |
| merge | RBC | EPS diluted Q3 FY2025 | 1.82 | 1.82 | right |
| merge | TER | EPS basic Q1 2018 | 0.45 | 0.45 | right |
| merge | OHI | Operating income Q2 2015 | 74,254K | 74,254K | right |
| merge | CIEN | SBC FY2019 | 59,736K | 59,736K | right |
| merge | GRMN | Revenue Q3 2019 | 934,383K | 934,383K | right |
| merge | URBN | SBC Q1 FY2017 | 5,760K | 5,760K | right |
| hide | YUM | Net interest FY2016 | -305M / -307M (2018/2019 10-Ks) | -307M (2017 10-K) | right (restated) |
| hide | ONTO | Opex FY2018 | 97,195K (post-merger 10-Ks) | 117,607K (2019 10-K, Nanometrics calendar) | right |
| hide | ONTO | Capex FY2017 | 5,204K | 10,210K | right |
| hide | VTRS | Continuing ops Q1 2020 | 30.7M | 0 | right (predecessor change) |
| hide | MTSI | COGS Q1 FY2014 | 46,803K | 48,432K (recast) | right |
| hide | ATI | NI Q2 2022 | (38.0)M as filed (face) | 6.7M (2024 10-K recast) | right |
| hide | EPRT | ProfitLoss Q2 2018 | Apr 1-Jun 30, 3,499K | Apr 1-Jun 24 stub, 3,176K | right (different periods) |
| hide | CHRD | Current assets Nov 2020 | Nov 19, 339,085K | Nov 18, 394,825K | right (fresh start) |
| hide | CHRD | Current LTD Nov 2020 | Nov 19, 0 | Nov 18, 360,640K | right (fresh start) |
| hide | ATI | NI Q1 2023 | 70.1M | 84.5M (recast) | right |

SEC requests: 8. DB: one connection for the facts behind each pair.
