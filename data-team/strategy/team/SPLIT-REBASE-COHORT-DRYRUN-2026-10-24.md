# Split re-base dry-run on cohort v1.1 (1,000 companies), 2026-10-24

Period Engineer. Rules `split.event_basis@1` (dry_run) + `pershare.never_derive@1` (classification only). Read-only: 6 connections max, `default_transaction_read_only`, statement_timeout 20s, chunks of 50, peak 8 pooler/app backends (team cap 30). 1,000 of 1,000 companies processed, 0 failures. Branch `work/period-engineer/split-rebase`; runner `pipeline/scripts/split_rebase_cohort_dryrun.py`; per-cell table `doc/data-moat/team/backups/split_rebase_dryrun_cohort1000_20261024.csv.gz` (old value, new value, class, status, factor, chosen fact and accession, every candidate). Cohort file `data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv`. Evidence: DATA-INFERRED unless a row says FILING-CHECKED (the Verifier's 194-value sample on the 11 companies passed with 0 wrong, VERIFY-SPLIT-REBASE-2026-10-24.md).

## Cells by class (per-share and share-count resolved concepts)

| Class | All periods | Periods ending 2015-01-01 or later |
|---|---|---|
| unchanged | 277,648 | 201,445 |
| rounding only | 2,670 | 1,539 |
| was unadjusted (stored value on a pre-split basis) | 6,476 | 1,881 |
| was double-divided (stored value divided too often) | 1,452 | 888 |
| shares re-based | 6,301 | 3,410 |
| other changed (filed copy replaces a different stored value) | 195 | 140 |
| new (no stored cell today) | 995 | 807 |
| hidden: restated copies disagree on one basis | 5,373 | 3,686 |
| derived-only, removed with RU-1 | 19,839 | 15,172 |
| hidden: copies disagree after conversion | 1,913 | 970 |
| hidden: unconfirmed split candidate | 2,289 | 977 |
| hidden: company invariant | 3,855 | 2,678 |
| hidden: dividend basis pending (AC-24, off-basis cells only) | 9,653 | 6,297 |
| hidden: units scale suspect | 753 | 391 |
| hidden: zero share count filed | 107 | 64 |
| hidden: quarter equals year (label error) | 33 | 26 |
| still blank (no stored cell, none shown) | 1,167 | 858 |
| **total cells evaluated** | 340,719 | 241,229 |

Classes: 'was unadjusted' / 'was double-divided' are today's wrong values that the pass corrects; 'hidden' rows are cells shown today that would become unavailable with the stated reason. 'derived-only, removed with RU-1' is the RU-1 half of the pair (Q4 per-share by subtraction).

## Events

Events: 237 confirmed, 52 review, 32 pending (no filing on the new basis yet, or every held filing post-dates it), 759 rejected (exchange/conversion ratios, context or units errors, contradicted candidates). Confirmed by evidence kinds: filed_pair+ratio_fact+share_step 172, filed_pair+share_step 55, filed_pair+ratio_fact 8, ratio_fact+share_step 2.
Companies: 174 with at least one confirmed split, 26 with only review candidates, 800 with none.

Confirmed events per company (ratio @ basis date [evidence kinds]):

- AAON: 3/2 @ 2014-08-07 [ratio_fact+filed_pair+share_step]; 3/2 @ 2023-11-06 [ratio_fact+filed_pair+share_step]
- AAPL: 4 @ 2020-10-30 [ratio_fact+filed_pair+share_step]; 7 @ 2014-07-23 [ratio_fact+filed_pair+share_step]
- ACGL: 3 @ 2011-08-05 [filed_pair+share_step]; 3 @ 2018-08-08 [ratio_fact+filed_pair+share_step]
- AFL: 2 @ 2018-05-04 [ratio_fact+filed_pair+share_step]
- AHR: 1/4 @ 2023-03-17 [ratio_fact+filed_pair+share_step]
- AMCR: 1/5 @ 2026-02-04 [filed_pair+share_step]
- AME: 3/2 @ 2011-02-24 [filed_pair+share_step]; 3/2 @ 2012-08-02 [filed_pair+share_step]
- AMZN: 20 @ 2022-07-29 [ratio_fact+filed_pair+share_step]
- ANET: 4 @ 2022-02-15 [ratio_fact+filed_pair+share_step]; 4 @ 2025-02-19 [ratio_fact+filed_pair+share_step]
- ANF: 2 @ 2013-04-02 [ratio_fact+filed_pair]
- AOS: 3/2 @ 2011-02-24 [ratio_fact+filed_pair]; 2 @ 2013-05-06 [ratio_fact+filed_pair+share_step]; 2 @ 2016-11-08 [ratio_fact+filed_pair+share_step]
- APG: 3/2 @ 2025-07-31 [ratio_fact+filed_pair+share_step]
- APH: 2 @ 2014-11-05 [ratio_fact+filed_pair+share_step]; 2 @ 2021-04-30 [ratio_fact+filed_pair+share_step]; 2 @ 2024-07-26 [ratio_fact+filed_pair+share_step]
- ARWR: 1/10 @ 2011-12-20 [ratio_fact+filed_pair]
- AVGO: 10 @ 2024-09-11 [ratio_fact+filed_pair+share_step]
- BALL: 2 @ 2011-02-28 [ratio_fact+filed_pair]; 2 @ 2017-08-09 [ratio_fact+filed_pair+share_step]
- BEN: 3 @ 2013-07-29 [ratio_fact+filed_pair+share_step]
- BF-A: 5/4 @ 2018-03-07 [filed_pair+share_step]; 3/2 @ 2012-09-05 [ratio_fact+filed_pair+share_step]; 2 @ 2016-08-31 [ratio_fact+filed_pair+share_step]
- BKNG: 25 @ 2026-04-28 [filed_pair+share_step]
- BMNR: 1/20 @ 2025-07-02 [filed_pair+share_step]
- BPOP: 1/10 @ 2012-08-09 [filed_pair+share_step]
- BRO: 2 @ 2018-05-10 [ratio_fact+filed_pair+share_step]
- BWA: 2 @ 2014-02-13 [ratio_fact+filed_pair+share_step]
- C: 1/10 @ 2011-08-05 [ratio_fact+filed_pair+share_step]
- CELH: 3 @ 2024-02-29 [ratio_fact+filed_pair+share_step]
- CF: 5 @ 2015-08-06 [ratio_fact+filed_pair+share_step]
- CGNX: 2 @ 2013-10-28 [ratio_fact+filed_pair+share_step]; 2 @ 2018-02-15 [ratio_fact+filed_pair+share_step]
- CHD: 2 @ 2011-08-05 [ratio_fact+filed_pair+share_step]; 2 @ 2016-11-03 [ratio_fact+filed_pair+share_step]
- CHDN: 2 @ 2023-07-26 [ratio_fact+filed_pair+share_step]; 3 @ 2019-02-27 [ratio_fact+filed_pair+share_step]
- CL: 2 @ 2013-07-25 [ratio_fact+filed_pair+share_step]
- CLH: 2 @ 2011-08-09 [ratio_fact+filed_pair+share_step]
- CMCSA: 2 @ 2017-04-27 [ratio_fact+filed_pair+share_step]
- CME: 5 @ 2012-08-08 [filed_pair+share_step]
- CMG: 50 @ 2024-07-25 [ratio_fact+filed_pair+share_step]
- CNC: 2 @ 2015-02-23 [ratio_fact+filed_pair+share_step]; 2 @ 2019-02-19 [ratio_fact+filed_pair+share_step]
- COHR: 2 @ 2011-08-26 [ratio_fact+filed_pair+share_step]
- COO: 4 @ 2024-03-01 [ratio_fact+filed_pair+share_step]
- CP: 5 @ 2021-07-29 [ratio_fact+filed_pair+share_step]
- CPRT: 2 @ 2012-06-11 [filed_pair+share_step]; 2 @ 2017-05-25 [filed_pair+share_step]; 2 @ 2023-09-28 [ratio_fact+filed_pair+share_step]; 4 @ 2023-09-28 [filed_pair+share_step]
- CRM: 4 @ 2013-05-24 [ratio_fact+filed_pair+share_step]
- CRWD: 4 @ 2026-08-27 [ratio_fact+filed_pair+share_step]
- CSGP: 10 @ 2021-07-28 [ratio_fact+filed_pair+share_step]
- CSX: 3 @ 2011-07-21 [filed_pair+share_step]; 3 @ 2021-07-22 [ratio_fact+filed_pair+share_step]
- CTAS: 4 @ 2024-10-04 [ratio_fact+filed_pair+share_step]
- CTSH: 2 @ 2014-05-08 [filed_pair+share_step]
- DCI: 2 @ 2012-06-05 [ratio_fact+filed_pair+share_step]
- DD: 1/3 @ 2019-08-06 [filed_pair+share_step]; 1/3 @ 2026-08-04 [ratio_fact+filed_pair+share_step]
- DECK: 6 @ 2024-10-31 [ratio_fact+filed_pair+share_step]
- DHR: 2 @ 2010-08-11 [ratio_fact+filed_pair+share_step]
- DLTR: 2 @ 2012-08-16 [ratio_fact+filed_pair+share_step]
- DUK: 1/3 @ 2012-08-08 [ratio_fact+filed_pair+share_step]
- DVA: 2 @ 2013-11-06 [ratio_fact+filed_pair+share_step]
- DXCM: 4 @ 2022-07-28 [ratio_fact+filed_pair+share_step]
- EL: 2 @ 2012-02-06 [ratio_fact+filed_pair+share_step]
- ELS: 2 @ 2013-08-02 [ratio_fact+filed_pair+share_step]; 2 @ 2019-10-30 [ratio_fact+filed_pair+share_step]
- EMN: 2 @ 2011-11-01 [filed_pair+share_step]
- ENSG: 2 @ 2016-02-10 [filed_pair+share_step]
- EOG: 2 @ 2014-05-06 [filed_pair+share_step]
- EPD: 2 @ 2014-11-10 [ratio_fact+filed_pair+share_step]
- ET: 2 @ 2015-08-07 [filed_pair+share_step]
- EW: 2 @ 2016-02-19 [filed_pair+share_step]; 3 @ 2020-07-27 [ratio_fact+filed_pair+share_step]
- EXE: 1/200 @ 2020-04-29 [ratio_fact+filed_pair+share_step]
- EXLS: 5 @ 2023-10-26 [ratio_fact+filed_pair+share_step]
- EXPE: 1/2 @ 2012-02-10 [filed_pair+share_step]
- FAST: 2 @ 2011-07-21 [ratio_fact+filed_pair+share_step]; 2 @ 2019-07-16 [ratio_fact+filed_pair+share_step]; 2 @ 2025-07-17 [ratio_fact+filed_pair+share_step]
- FCX: 2 @ 2011-02-25 [ratio_fact+filed_pair+share_step]
- FISV: 2 @ 2014-02-20 [ratio_fact+filed_pair+share_step]; 2 @ 2018-05-02 [ratio_fact+filed_pair+share_step]
- FLS: 3 @ 2013-07-24 [ratio_fact+filed_pair+share_step]
- FTNT: 5 @ 2022-08-05 [ratio_fact+filed_pair+share_step]
- FWONA: 3 @ 2014-08-05 [filed_pair+share_step]
- GE: 1/8 @ 2021-10-26 [ratio_fact+filed_pair+share_step]
- GGG: 3 @ 2018-02-20 [filed_pair+share_step]
- GILD: 2 @ 2013-02-27 [filed_pair+share_step]
- GIS: 2 @ 2010-07-09 [filed_pair+share_step]
- GL: 3/2 @ 2014-08-08 [ratio_fact+filed_pair+share_step]
- GME: 4 @ 2022-09-07 [ratio_fact+filed_pair+share_step]
- GOOG: 20 @ 2022-07-27 [ratio_fact+filed_pair+share_step]
- GPN: 2 @ 2016-01-11 [ratio_fact+filed_pair+share_step]
- GSAT: 1/15 @ 2025-02-28 [filed_pair+share_step]
- HEI: 5/4 @ 2011-09-01 [filed_pair+share_step]; 5/4 @ 2013-12-19 [filed_pair+share_step]; 5/4 @ 2017-05-25 [filed_pair+share_step]; 5/4 @ 2018-08-31 [filed_pair+share_step]
- HLT: 1/3 @ 2017-02-15 [filed_pair+share_step]
- HOMB: 2 @ 2013-08-07 [ratio_fact+filed_pair+share_step]; 2 @ 2016-08-05 [ratio_fact+filed_pair+share_step]; 2 @ 2018-11-05 [ratio_fact+filed_pair]
- HON: 1/2 @ 2026-07-23 [ratio_fact+filed_pair+share_step]
- HR: 1/2 @ 2015-02-23 [ratio_fact+filed_pair+share_step]
- HRL: 2 @ 2011-03-11 [filed_pair+share_step]; 2 @ 2016-03-04 [filed_pair+share_step]
- HSIC: 2 @ 2017-11-06 [filed_pair+share_step]
- HWM: 1/3 @ 2016-11-09 [ratio_fact+filed_pair+share_step]
- IBKR: 4 @ 2025-08-06 [ratio_fact+filed_pair+share_step]
- ICE: 5 @ 2017-02-07 [ratio_fact+filed_pair+share_step]
- IDXX: 2 @ 2015-07-30 [ratio_fact+filed_pair+share_step]
- IOVA: 1/100 @ 2013-10-23 [filed_pair+share_step]
- ISRG: 3 @ 2017-10-20 [ratio_fact+filed_pair+share_step]; 3 @ 2021-10-20 [ratio_fact+filed_pair+share_step]
- ITT: 1/2 @ 2012-02-29 [filed_pair+share_step]
- KDP: 8 @ 2018-08-08 [filed_pair+share_step]
- KLAC: 10 @ 2026-08-06 [ratio_fact+filed_pair+share_step]
- KO: 2 @ 2012-10-25 [ratio_fact+filed_pair+share_step]
- KR: 2 @ 2015-09-22 [ratio_fact+filed_pair+share_step]
- LDOS: 1/4 @ 2013-12-10 [ratio_fact+filed_pair+share_step]
- LECO: 2 @ 2011-08-02 [ratio_fact+filed_pair+share_step]
- LEVI: 10 @ 2019-04-09 [filed_pair+share_step]
- LKQ: 2 @ 2012-10-26 [ratio_fact+filed_pair+share_step]
- LNT: 2 @ 2016-08-02 [ratio_fact+filed_pair+share_step]
- LRCX: 10 @ 2024-10-28 [ratio_fact+filed_pair+share_step]
- LULU: 2 @ 2011-09-09 [ratio_fact+filed_pair+share_step]
- MA: 10 @ 2014-02-14 [filed_pair+share_step]
- MANH: 4 @ 2014-02-06 [ratio_fact+filed_pair+share_step]
- MCHP: 2 @ 2021-11-04 [ratio_fact+filed_pair+share_step]
- MKC: 2 @ 2021-01-28 [filed_pair+share_step]
- MLI: 2 @ 2014-04-25 [ratio_fact+filed_pair+share_step]; 2 @ 2023-10-25 [ratio_fact+filed_pair+share_step]; 2 @ 2026-07-22 [ratio_fact+filed_pair+share_step]
- MNST: 2 @ 2012-02-29 [ratio_fact+filed_pair+share_step]; 2 @ 2023-05-05 [ratio_fact+filed_pair+share_step]; 3 @ 2017-03-01 [ratio_fact+filed_pair+share_step]
- MPC: 2 @ 2015-08-03 [filed_pair+share_step]
- MSI: 1/7 @ 2011-02-18 [filed_pair+share_step]
- MSTR: 10 @ 2024-10-31 [ratio_fact+filed_pair+share_step]
- NDAQ: 3 @ 2022-11-02 [ratio_fact+filed_pair+share_step]
- NDSN: 2 @ 2011-06-03 [filed_pair+share_step]
- NEE: 4 @ 2021-02-12 [ratio_fact+filed_pair+share_step]
- NFLX: 7 @ 2015-07-17 [ratio_fact+filed_pair+share_step]; 10 @ 2026-01-23 [ratio_fact+filed_pair+share_step]
- NKE: 2 @ 2013-01-09 [ratio_fact+filed_pair+share_step]; 2 @ 2016-01-06 [ratio_fact+filed_pair+share_step]
- NLY: 1/4 @ 2022-11-03 [ratio_fact+filed_pair+share_step]
- NOW: 5 @ 2026-01-29 [ratio_fact+filed_pair+share_step]
- NVDA: 4 @ 2021-08-20 [ratio_fact+filed_pair+share_step]; 10 @ 2024-08-28 [ratio_fact+filed_pair+share_step]
- ODFL: 3/2 @ 2010-11-08 [ratio_fact+filed_pair+share_step]; 3/2 @ 2012-11-06 [ratio_fact+filed_pair+share_step]; 3/2 @ 2020-05-05 [ratio_fact+filed_pair+share_step]; 2 @ 2024-05-07 [ratio_fact+filed_pair+share_step]
- OGE: 2 @ 2013-08-08 [filed_pair+share_step]
- OKE: 2 @ 2012-08-01 [filed_pair+share_step]
- ORLY: 15 @ 2025-08-08 [ratio_fact+filed_pair+share_step]
- OTEX: 2 @ 2014-04-24 [ratio_fact+filed_pair+share_step]; 2 @ 2017-02-02 [ratio_fact+filed_pair+share_step]
- PAA: 2 @ 2012-11-07 [ratio_fact+share_step]
- PANW: 2 @ 2025-02-14 [ratio_fact+filed_pair+share_step]; 3 @ 2022-11-18 [ratio_fact+filed_pair+share_step]
- PCAR: 3/2 @ 2023-02-22 [filed_pair+share_step]
- PEGA: 2 @ 2014-05-06 [ratio_fact+filed_pair+share_step]; 2 @ 2025-07-22 [ratio_fact+filed_pair+share_step]
- POWL: 3 @ 2026-05-05 [ratio_fact+filed_pair+share_step]
- PPG: 2 @ 2015-07-27 [ratio_fact+filed_pair+share_step]
- PRAX: 1/15 @ 2024-03-05 [ratio_fact+filed_pair+share_step]
- QXO: 1/8 @ 2024-08-14 [ratio_fact+filed_pair+share_step]
- RJF: 3/2 @ 2021-11-23 [ratio_fact+filed_pair+share_step]
- RLI: 2 @ 2014-02-27 [ratio_fact+filed_pair+share_step]; 2 @ 2025-02-21 [ratio_fact+filed_pair+share_step]
- ROL: 3/2 @ 2011-02-25 [ratio_fact+filed_pair+share_step]; 3/2 @ 2015-04-30 [ratio_fact+filed_pair+share_step]; 3/2 @ 2019-03-01 [ratio_fact+filed_pair+share_step]; 3/2 @ 2021-02-26 [ratio_fact+filed_pair+share_step]
- ROST: 2 @ 2012-03-27 [ratio_fact+filed_pair+share_step]; 2 @ 2015-09-09 [ratio_fact+filed_pair+share_step]
- RYN: 3/2 @ 2011-10-28 [ratio_fact+filed_pair+share_step]
- SAIA: 3/2 @ 2013-08-07 [filed_pair+share_step]
- SBUX: 2 @ 2015-04-28 [ratio_fact+filed_pair+share_step]
- SF: 3/2 @ 2011-05-10 [filed_pair+share_step]; 3/2 @ 2021-02-19 [ratio_fact+filed_pair+share_step]; 3/2 @ 2026-05-04 [filed_pair+share_step]
- SGI: 4 @ 2021-02-19 [ratio_fact+filed_pair+share_step]
- SHW: 3 @ 2021-04-28 [ratio_fact+filed_pair+share_step]
- SIRI: 1/10 @ 2024-10-31 [ratio_fact+filed_pair]
- SMCI: 10 @ 2025-02-25 [ratio_fact+filed_pair+share_step]
- SNEX: 3/2 @ 2024-02-06 [ratio_fact+filed_pair+share_step]; 3/2 @ 2025-05-07 [ratio_fact+filed_pair+share_step]; 3/2 @ 2026-08-05 [ratio_fact+share_step]
- SSNC: 2 @ 2016-08-05 [ratio_fact+filed_pair+share_step]
- SYRE: 1/25 @ 2023-11-09 [filed_pair+share_step]
- TECH: 4 @ 2023-02-07 [ratio_fact+filed_pair+share_step]
- THC: 1/4 @ 2012-11-07 [ratio_fact+filed_pair+share_step]
- TJX: 2 @ 2012-03-27 [ratio_fact+filed_pair+share_step]; 2 @ 2018-12-04 [ratio_fact+filed_pair+share_step]
- TPL: 3 @ 2024-05-08 [ratio_fact+filed_pair+share_step]; 3 @ 2026-02-18 [ratio_fact+filed_pair+share_step]
- TRMB: 2 @ 2013-05-02 [ratio_fact+filed_pair+share_step]
- TSCO: 2 @ 2010-11-02 [ratio_fact+filed_pair+share_step]; 2 @ 2013-11-04 [ratio_fact+filed_pair+share_step]; 5 @ 2025-02-20 [ratio_fact+filed_pair+share_step]
- TSLA: 3 @ 2022-10-24 [ratio_fact+filed_pair+share_step]; 5 @ 2020-10-26 [ratio_fact+filed_pair+share_step]
- TTC: 2 @ 2012-09-05 [ratio_fact+filed_pair+share_step]; 2 @ 2016-12-22 [ratio_fact+filed_pair+share_step]
- TTD: 10 @ 2021-08-09 [ratio_fact+filed_pair+share_step]
- TTEK: 5 @ 2024-11-19 [ratio_fact+filed_pair+share_step]
- UGI: 3/2 @ 2014-11-28 [filed_pair+share_step]
- UNP: 2 @ 2014-07-25 [ratio_fact+filed_pair+share_step]
- VFC: 4 @ 2014-02-26 [ratio_fact+filed_pair+share_step]
- VRNS: 3 @ 2021-05-04 [ratio_fact+filed_pair]
- WAB: 2 @ 2013-07-26 [ratio_fact+filed_pair+share_step]
- WCN: 3/2 @ 2017-07-26 [ratio_fact+filed_pair+share_step]
- WEC: 2 @ 2011-05-05 [filed_pair+share_step]
- WLK: 2 @ 2014-05-06 [ratio_fact+filed_pair+share_step]
- WMT: 3 @ 2024-03-15 [ratio_fact+filed_pair+share_step]
- WRB: 3/2 @ 2019-05-08 [ratio_fact+filed_pair+share_step]; 3/2 @ 2022-05-03 [ratio_fact+filed_pair+share_step]; 3/2 @ 2024-08-02 [filed_pair+share_step]
- WSM: 2 @ 2024-08-23 [ratio_fact+filed_pair+share_step]
- WST: 2 @ 2013-11-04 [filed_pair+share_step]
- WTRG: 5/4 @ 2013-11-08 [ratio_fact+filed_pair+share_step]
- XPO: 1/4 @ 2011-11-10 [filed_pair+share_step]
- Z: 3 @ 2015-11-05 [ratio_fact+filed_pair]

Review candidates (cells of filings before them are hidden 'share basis under review'):

- AAL: 3/2 @ 2014-04-24 [share_step] one evidence kind only; 2 @ 2014-04-24 [filed_pair] one evidence kind only
- ACI: 2 @ 2020-08-04 [filed_pair] one evidence kind only
- AHR: 8 @ 2016-08-10 [share_step] one evidence kind only
- ARWR: 1/7 @ 2011-12-20 [share_step] one evidence kind only
- BMNR: 15 @ 2021-12-09 [share_step] one evidence kind only
- BRO: 1/50 @ 2018-05-10 [filed_pair] one evidence kind only
- CHTR: 5/2 @ 2016-08-09 [share_step] one evidence kind only
- CVNA: 1/5 @ 2026-05-08 [ratio_fact] ratio disclosed, no basis change observed
- CYTK: 1/6 @ 2013-08-07 [filed_pair] one evidence kind only; 1/5 @ 2013-08-07 [share_step] one evidence kind only
- DELL: 2 @ 2016-12-09 [share_step] one evidence kind only
- DRS: 3/2 @ 2023-03-28 [filed_pair] one evidence kind only
- EOG: 1/500 @ 2014-05-06 [filed_pair] one evidence kind only
- ET: 5/4 @ 2012-05-09 [share_step] one evidence kind only; 2 @ 2014-02-27 [share_step] one evidence kind only
- FRHC: 1/10 @ 2017-11-14 [share_step] one evidence kind only; 5 @ 2016-02-16 [share_step] one evidence kind only
- GL: 3/2 @ 2011-08-08 [filed_pair] one evidence kind only
- GLPI: 5/4 @ 2014-03-25 [share_step] one evidence kind only
- GSAT: 2/3 @ 2025-02-10 [ratio_fact] ratio disclosed, no basis change observed
- HEI: 1/4 @ 2017-12-21 [ratio_fact] ratio disclosed, no basis change observed
- IONS: 5/4 @ 2021-05-05 [filed_pair] one evidence kind only
- IOVA: 5/4 @ 2013-11-14 [share_step] one evidence kind only
- KDP: 5 @ 2018-11-08 [filed_pair] one evidence kind only; 15 @ 2018-11-08 [filed_pair] one evidence kind only
- LAMR: 5/4 @ 2014-02-27 [filed_pair] one evidence kind only
- LDOS: 2 @ 2013-12-10 [filed_pair] one evidence kind only
- MDGL: 1/12 @ 2016-11-14 [share_step] one evidence kind only
- MTCH: 3 @ 2020-08-10 [share_step] one evidence kind only
- MTSI: 3/2 @ 2014-05-12 [filed_pair] one evidence kind only
- PNFP: 2 @ 2026-05-06 [share_step] one evidence kind only
- PPC: 5/4 @ 2012-04-27 [share_step] one evidence kind only
- PRAX: 1/10 @ 2024-03-05 [share_step] one evidence kind only
- QXO: 1/30 @ 2015-03-31 [filed_pair] one evidence kind only
- ROIV: 3 @ 2021-11-15 [share_step] one evidence kind only
- SMMT: 3/2 @ 2023-05-11 [filed_pair] one evidence kind only; 7 @ 2023-03-09 [share_step] one evidence kind only
- SNDK: 5/4 @ 2025-03-17 [share_step] one evidence kind only
- SNOW: 2 @ 2021-03-31 [ratio_fact] ratio disclosed, no basis change observed
- SYRE: 5/4 @ 2022-08-04 [share_step] one evidence kind only; 5/4 @ 2025-11-04 [share_step] one evidence kind only
- TGTX: 40 @ 2012-03-14 [share_step] one evidence kind only
- TMUS: 1/6 @ 2013-08-08 [filed_pair] one evidence kind only; 1/4 @ 2013-08-08 [filed_pair] one evidence kind only; 2 @ 2013-08-08 [share_step] one evidence kind only
- TRU: 5/4 @ 2015-07-31 [filed_pair] one evidence kind only
- TSCO: 1/500 @ 2010-11-02 [filed_pair] one evidence kind only
- VICI: 3/2 @ 2018-03-28 [share_step] one evidence kind only
- WES: 2 @ 2019-05-01 [share_step] one evidence kind only
- WULF: 6 @ 2022-03-31 [filed_pair] one evidence kind only; 50 @ 2022-03-31 [share_step] one evidence kind only

## Companies tripping the company invariant (every per-share and share cell hidden)

| Ticker | Violating filed pairs | Cells hidden |
|---|---|---|
| KDP | 10 | 473 |
| HWM | 5 | 484 |
| HEI | 42 | 319 |
| BRO | 52 | 465 |
| CPRT | 40 | 359 |
| CELH | 4 | 209 |
| SNEX | 16 | 337 |
| ANF | 17 | 351 |
| HOMB | 26 | 408 |
| AAON | 31 | 450 |

Read (DATA-INFERRED): KDP is the 2018 Keurig/Dr Pepper reverse merger (cross-entity history); CPRT, SNEX, AAON, HEI, HOMB, ANF, HWM, BRO and CELH show filed comparatives that disagree with the observed boundary (a missed or mis-placed boundary). Hiding is the safe state until a filing check places the boundary.

## 20 largest value changes (one per company)

Per-share (magnitude = old/new or new/old):

| Ticker | Concept | Period end | Stored | New | Factor | Class | Source accession |
|---|---|---|---|---|---|---|---|
| PACS | diluted_eps_resolved | 2023-03-31 | 0.001351870915 | 0.29 | 1 | other_changed | 0002001184-24-000010 |
| EXE | diluted_eps_resolved | 2020-03-31 | -170594 | -852.97 | 1 | was_unadjusted | 0000895126-21-000107 |
| CFG | diluted_eps_resolved | 2013-09-30 | -0.03859115121 | -6.39 | 1 | was_double_divided | 0000759944-14-000012 |
| JXN | diluted_eps_resolved | 2020-06-30 | -0.66672774604 | -69.98 | 1 | was_double_divided | 0001193125-21-277272 |
| NFLX | diluted_eps_resolved | 2014-03-31 | 0.86 | 0.012 | 10 | was_unadjusted | 0001065280-16-000047 |
| CMG | diluted_eps_resolved | 2022-12-31 | 32.04 | 0.64 | 1 | was_unadjusted | 0001058090-25-000014 |
| CBC | diluted_eps_resolved | 2024-12-31 | 0.0278 | 1.39 | 1 | was_double_divided | 0001628280-26-021067 |
| WMG | diluted_eps_resolved | 2011-06-30 | -0.01424851803 | -0.68 | 1 | was_double_divided | 0001193125-11-209307 |
| NVDA | diluted_eps_resolved | 2020-01-26 | 4.52 | 0.113 | 10 | was_unadjusted | 0001045810-22-000036 |
| GOOG | basic_eps_resolved | 2013-12-31 | 0.0239125 | 0.9565 | 20 | was_double_divided | 0001652044-16-000012 |
| AHR | dividends_per_share_resolved | 2021-06-30 | 0.02 | 0.8 | 1/4 | was_double_divided | 0001632970-21-000066 |
| SFD | diluted_eps_resolved | 2011-05-01 | 0.015523487573 | 0.59 | 1 | was_double_divided | 0000091388-12-000027 |
| LDOS | dividends_per_share_resolved | 2013-05-03 | 0.12 | 4.48 | 1 | was_double_divided | 0001336920-14-000014 |
| DD | dividends_per_share_resolved | 2018-12-31 | 0.38 | 13.68 | 1/3 | was_double_divided | 0001666700-21-000005 |
| TTD | diluted_eps_resolved | 2016-03-31 | -13.3513351335 | -0.445 | 10 | was_unadjusted | 0001193125-17-167445 |
| AAPL | diluted_eps_resolved | 2012-12-29 | 13.81 | 0.4925 | 4 | was_unadjusted | 0001193125-14-383437 |
| BKNG | basic_eps_resolved | 2024-12-31 | 174.96 | 6.9984 | 25 | was_unadjusted | 0001075531-26-000009 |
| AMZN | basic_eps_resolved | 2020-12-31 | 42.64 | 2.13 | 1 | was_unadjusted | 0001018724-23-000004 |
| CRWV | diluted_eps_resolved | 2024-12-31 | -0.215 | -4.3 | 1 | was_double_divided | 0001769628-26-000104 |
| BMNR | diluted_eps_resolved | 2024-08-31 | -0.07 | -1.32 | 1 | was_double_divided | 0001493152-25-024679 |

Share counts:

| Ticker | Period end | Stored | New | Factor | Source accession |
|---|---|---|---|---|---|
| PCG | 2016-12-31 | 506891874000000 | 506891874 | 1 | 0001004980-18-000003 |
| ZS | 2019-07-31 | 127253 | 127253000 | 1 | 0001713683-20-000163 |
| MCY | 2010-12-31 | 54803 | 54803000 | 1 | 0001193125-11-125798 |
| AEIS | 2012-12-31 | 37991 | 37991000 | 1 | 0000927003-14-000012 |
| LGND | 2018-12-31 | 20766 | 20766000 | 1 | 0000886163-20-000025 |
| EXE | 2011-11-02 | 659266080 | 3296330 | 1/200 | 0001193125-11-304766 |
| NFLX | 2012-12-31 | 55398615 | 3891101690 | 70 | 0001065280-14-000006 |
| CMG | 2012-04-16 | 31703449 | 1585172450 | 50 | 0001193125-12-170975 |
| NVDA | 2015-01-25 | 544913000 | 21800000000 | 40 | 0001045810-16-000205 |
| AAPL | 2012-10-19 | 940692000 | 26339376000 | 28 | 0001193125-12-444068 |
| BKNG | 2014-08-01 | 52447706 | 1311192650 | 25 | 0001075531-14-000049 |
| GOOG | 2018-09-30 | 695957000 | 13919140000 | 20 | 0001652044-18-000035 |
| AMZN | 2022-03-31 | 509000000 | 10180000000 | 20 | 0001018724-22-000013 |
| ANET | 2021-09-30 | 76886000 | 1230176000 | 16 | 0001596532-21-000354 |
| TSLA | 2018-12-31 | 172603000 | 2595000000 | 15 | 0001564590-20-004475 |
| PRAX | 2022-12-31 | 49382453 | 3292163 | 1 | 0001689548-24-000034 |
| ORLY | 2011-02-21 | 141128889 | 2116933335 | 15 | 0001193125-11-049998 |
| MNST | 2011-02-22 | 89005264 | 1068063168 | 12 | 0001104659-11-011438 |
| AVGO | 2019-11-03 | 397560810 | 3980000000 | 10 | 0001730168-20-000226 |
| SMCI | 2023-06-30 | 52901000 | 529014000 | 1 | 0001375365-25-000004 |

Needs a filing check before trust (DATA-INFERRED): LDOS FY2014 Q1 DPS 4.48 (0001336920-14-000014), AHR Q2 2021 DPS 0.8, DD 2018 DPS 13.68 on the post-2026 basis (two 1-for-3 events, 2019 and 2026), BKNG factor 25 (2026 split), PRAX 1-for-15 review candidate.

## Split table (`analytics.company_stock_split`) vs filing-detected

- In the table and confirmed from filings: 101 companies.
- Confirmed from filings only (missing from the table): 73 companies: EOG (2@2014-05-06), SHW (3@2021-04-28), EPD (2@2014-11-10), HLT (1/3@2017-02-15), MSI (1/7@2011-02-18), CL (2@2013-07-25), ET (2@2015-08-07), OKE (2@2012-08-01), PCAR (3/2@2023-02-22), AME (3/2@2011-02-24; 3/2@2012-08-02), KDP (8@2018-08-08), COHR (2@2011-08-26), IDXX (2@2015-07-30), EL (2@2012-02-06), WEC (2@2011-05-05), CME (5@2012-08-08), FCX (2@2011-02-25), HWM (1/3@2016-11-09), MA (10@2014-02-14), KO (2@2012-10-25), C (1/10@2011-08-05), CRM (4@2013-05-24), GILD (2@2013-02-27), DHR (2@2010-08-11), MPC (2@2015-08-03), BKNG (25@2026-04-28), EXPE (1/2@2012-02-10), CTSH (2@2014-05-08), NDSN (2@2011-06-03), ITT (1/2@2012-02-29), GIS (2@2010-07-09), DD (1/3@2019-08-06; 1/3@2026-08-04), HEI (5/4@2011-09-01; 5/4@2013-12-19; 5/4@2017-05-25; 5/4@2018-08-31), CLH (2@2011-08-09), BEN (3@2013-07-29), LDOS (1/4@2013-12-10), LECO (2@2011-08-02), PPG (2@2015-07-27), DLTR (2@2012-08-16), BRO (2@2018-05-10), XPO (1/4@2011-11-10), AMCR (1/5@2026-02-04), WST (2@2013-11-04), CHD (2@2011-08-05; 2@2016-11-03), TRMB (2@2013-05-02), BF-A (5/4@2018-03-07; 3/2@2012-09-05; 2@2016-08-31), GGG (3@2018-02-20), BMNR (1/20@2025-07-02), MANH (4@2014-02-06), MKC (2@2021-01-28), DVA (2@2013-11-06), BWA (2@2014-02-13), WTRG (5/4@2013-11-08), HRL (2@2011-03-11; 2@2016-03-04), OGE (2@2013-08-08), HSIC (2@2017-11-06), FLS (3@2013-07-24), SAIA (3/2@2013-08-07), ENSG (2@2016-02-10), LULU (2@2011-09-09), DCI (2@2012-06-05), BPOP (1/10@2012-08-09), EMN (2@2011-11-01), SYRE (1/25@2023-11-09), VFC (4@2014-02-26), ANF (2@2013-04-02), WLK (2@2014-05-06), LEVI (10@2019-04-09), ARWR (1/10@2011-12-20), RYN (3/2@2011-10-28), LKQ (2@2012-10-26), FWONA (3@2014-08-05), IOVA (1/100@2013-10-23).
- In the table but not confirmed: 55 companies. These are splits before every held filing (pending), or IPO/merger exchange ratios the table treats as splits (CFG 165.582, JXN 104.96, WMG 47.72, BTSG 15.70, INGM 8.37, VOYA 2.30: the old adjuster divides those companies' earlier periods by them):
  - DASH: table [['2020-11-09', '5']]; detector [['5', 'pending', 'every held filing post-dates it'], ['5', 'rejected', 'filed comparatives span the date at ratio 1']]
  - LITE: table [['2015-08-01', '0.2']]; detector [['5/4', 'rejected', 'share-count step only; filed comparatives span it '], ['1/5', 'pending', 'every held filing post-dates it']]
  - BE: table [['2018-07-07', '0.6667']]; detector [['1/1000', 'rejected', 'per-share power-of-ten move without share counts: '], ['2/3', 'pending', 'every held filing post-dates it']]
  - NTRA: table [['2015-06-19', '0.6135']]; detector [['1227/2000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - CVNA: table [['2026-05-05', '0.2']]; detector [['139/2500', 'rejected', 'not a clean split ratio (exchange/conversion)'], ['1/5', 'review', 'ratio disclosed, no basis change observed']]
  - RVMD: table [['2020-02-07', '0.2055']]; detector [['3/2', 'rejected', 'share-count step only; filed comparatives span it '], ['411/2000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - RBLX: table [['2020-01-31', '2']]; detector [['2', 'pending', 'every held filing post-dates it']]
  - ABNB: table [['2020-10-26', '0.5']]; detector [['1/2', 'pending', 'every held filing post-dates it']]
  - DDOG: table [['2018-01-02', '0.25']]; detector [['1/4', 'pending', 'every held filing post-dates it'], ['1/3', 'pending', 'every held filing post-dates it']]
  - MRNA: table [['2016-08-10', '10'], ['2018-11-27', '0.4587']]; detector [['10', 'pending', 'every held filing post-dates it'], ['4587/10000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - CRWV: table [['2025-03-14', '20']]; detector [['20', 'pending', 'no filing on the new basis yet']]
  - VG: table [['2025-01-27', '4.5203317']]; detector [['45203317/10000000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - TOST: table [['2021-09-09', '5']]; detector [['5', 'pending', 'every held filing post-dates it']]
  - MEDP: table [['2016-07-25', '0.74']]; detector [['37/50', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - WMG: table [['2020-02-28', '47.7242614672']]; detector [['29827663417/625000000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - PFGC: table [['2015-08-28', '0.485']]; detector [['97/200', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - ULS: table [['2023-11-20', '2']]; detector [['2', 'pending', 'every held filing post-dates it']]
  - PINS: table [['2019-03-28', '0.33']]; detector [['33/100', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - EQH: table [['2018-04-24', '0.459475265']]; detector [['5/4', 'rejected', 'pairs from one tag only (judged per cell)'], ['91895053/200000000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - GH: table [['2018-09-19', '0.7378']]; detector [['3689/5000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - CFG: table [['2014-08-22', '165.582']]; detector [['82791/500', 'rejected', 'not a clean split ratio (exchange/conversion)'], ['6', 'rejected', 'filed comparatives span the date at ratio 1']]
  - DRI: table [['2015-11-09', '0.3333']]; detector [['1/3', 'rejected', 'filed comparatives span the date at ratio 1']]
  - BTSG: table [['2024-01-24', '15.7027']]; detector [['157027/10000', 'rejected', 'not a clean split ratio (exchange/conversion)'], ['157027/10000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - SMMT: table [['2020-09-18', '0.2']]; detector [['1/2', 'rejected', 'share-count step only; filed comparatives span it '], ['3/2', 'review', 'one evidence kind only'], ['2', 'rejected', 'share-count step only; filed comparatives span it ']]
  - HUBS: table [['2014-09-25', '0.33']]; detector [['3/2', 'rejected', '2 filed pair(s) contradicted by 21 ratio-1 pairs'], ['33/100', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - GKOS: table [['2015-06-11', '0.4']]; detector [['2/5', 'pending', 'every held filing post-dates it']]
  - DRS: table [['2022-11-23', '1.451345']]; detector [['3/2', 'review', 'one evidence kind only'], ['145', 'rejected', 'not a clean split ratio (exchange/conversion)'], ['290269/200000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - PCVX: table [['2020-06-05', '0.593']]; detector [['593/1000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - KRYS: table [['2017-09-14', '0.222222']]; detector [['111111/500000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - OSCR: table [['2021-03-03', '0.33']]; detector [['33/100', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - AWI: table [['2016-04-02', '0.5']]; detector [['1/2', 'rejected', 'pairs from one tag only (judged per cell)'], ['1/2', 'rejected', 'filed comparatives span the date at ratio 1']]
  - COMP: table [['2021-03-19', '10']]; detector [['10', 'rejected', 'filed comparatives span the date at ratio 1']]
  - PATH: table [['2020-07-09', '3']]; detector [['3', 'pending', 'every held filing post-dates it']]
  - CAVA: table [['2023-06-02', '3']]; detector [['3', 'pending', 'every held filing post-dates it']]
  - KNSA: table [['2018-05-11', '2.73235']]; detector [['54647/20000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - ACI: table [['2020-06-18', '2.072']]; detector [['5/4', 'rejected', 'share-count step only; filed comparatives span it '], ['2', 'review', 'one evidence kind only'], ['259/125', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - JXN: table [['2021-09-09', '104.960383628']]; detector [['26240095907/250000000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - KYMR: table [['2020-08-20', '1.5949']]; detector [['15949/10000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - CAI: table [['2025-06-01', '0.25']]; detector [['1/4', 'pending', 'every held filing post-dates it']]
  - VOYA: table [['2013-04-11', '2.295248835']]; detector [['1/2', 'rejected', 'pairs from one tag only (judged per cell)'], ['459049767/200000000', 'rejected', 'not a clean split ratio (exchange/conversion)'], ['2869061/1250000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - HUT: table [['2022-09-01', '0.25']]; detector [['1/4', 'pending', 'every held filing post-dates it']]
  - AXSM: table [['2015-10-30', '7.3445']]; detector [['5/4', 'rejected', 'share-count step only; filed comparatives span it '], ['14689/2000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - DBX: table [['2018-03-07', '0.6667']]; detector [['2/3', 'pending', 'every held filing post-dates it']]
  - CBC: table [['2025-10-09', '50']]; detector [['50', 'pending', 'every held filing post-dates it']]
  - ETSY: table [['2015-03-25', '0.5']]; detector [['1/2', 'pending', 'every held filing post-dates it'], ['10', 'rejected', 'filed comparatives span the date at ratio 1']]
  - APPF: table [['2015-06-04', '0.25']]; detector [['1/4', 'pending', 'every held filing post-dates it']]
  - PACS: table [['2023-06-30', '33.33'], ['2024-03-31', '6.4361693']]; detector [['1/3', 'rejected', '2 filed pair(s) contradicted by 13 ratio-1 pairs'], ['6', 'rejected', 'share-count step only; filed comparatives span it '], ['3333/100', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - SFD: table [['2025-01-17', '38.0069232']]; detector [['23754327/625000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - S: table [['2021-02-06', '0.3333']]; detector [['1/3', 'pending', 'every held filing post-dates it']]
  - ESNT: table [['2013-11-04', '0.67']]; detector [['67/100', 'rejected', 'not a clean split ratio (exchange/conversion)'], ['2/3', 'rejected', 'filed comparatives span the date at ratio 1']]
  - DOCS: table [['2021-06-08', '2']]; detector [['2', 'pending', 'every held filing post-dates it']]
  - EPAM: table [['2012-01-19', '8']]; detector [['8', 'rejected', 'filed comparatives span the date at ratio 1']]
  - NAVN: table [['2025-09-18', '0.333']]; detector [['1/3', 'pending', 'every held filing post-dates it']]
  - INGM: table [['2024-10-23', '8.36719365']]; detector [['167343873/20000000', 'rejected', 'not a clean split ratio (exchange/conversion)']]
  - RYTM: table [['2017-09-22', '0.109051']]; detector [['5/4', 'rejected', 'share-count step only; filed comparatives span it '], ['5/4', 'rejected', 'share-count step only; filed comparatives span it '], ['109051/1000000', 'rejected', 'not a clean split ratio (exchange/conversion)']]

## Policy questions with cohort counts

- Restatement (Standardization Lead): hide vs leave a period whose filed copies disagree on one share basis. Hide affects 5,373 cells (3,686 in periods ending 2015+). Leave keeps today's value for those cells (code constant `RESTATEMENT_POLICY`).
- Dividend basis per series (AC-24, declared vs paid): the default shows a mixed series on the priority-1 tag (Declared) and hides the off-basis cells: 9,653 cells (6,297 in 2015+). Hiding every mixed series instead: 25,558 (17,859 in 2015+; measured on the previous detector revision) (`DPS_MIXED_POLICY`).

## Rules added from this run (all tested, mutation-checked)

Label-shift drop before 'restated' (Verifier false holds AMZN 2011-12 from 0001193125-13-028520, NVDA 6M FY2018); one dividend basis per series (LLY); disclosure attaches to one nearest event, ratio k or 1/k (WAB, CGNX, TTD 0.1 for 10:1); restated share counts count as share evidence (MA, CSX, CME); single-tag, dividend-only and power-of-ten pair candidates rejected; non-clean ratio facts are exchange ratios (DUK, WTW, ACI); same ratio confirmed twice within 400 days keeps one (KR); invariant only on ratios built from the company's own events (CRM); share copies off by 1000x/10^6 vs their own filing dropped (PCG); scale-off copies need a majority (AAPL 899,213); zero share counts hidden (SIRI); DPS and share counts 50x off the company median hidden (VICI 262,500; SWX; ROST; HL; DLTR 123.5).
