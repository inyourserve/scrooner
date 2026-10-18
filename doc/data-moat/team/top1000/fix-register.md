# Fix register for the top-1000 campaign (owner: Dhairya, started 2026-10-19)

Division of labour: shard workers FIND (read-only, `results/S###.md`); Dhairya's data-team agents FIX through rule families: proposal -> Verifier filing sample -> full-population coexistence check -> committed migration or code -> reprocess -> re-measure (see `../PLAN.md`). Fix priority = number of top-1000 companies touched, then the rank of the largest. Companies are matched against `shards.csv` (rank by market cap, provisional until S000 finishes). Every defect below was FILING-CHECKED by the Verifier unless marked DATA-INFERRED.

## Known defects, ordered by top-1000 reach
| # | Defect | Top-1000 companies hit (rank) | Status / owner |
|---|---|---|---|
| 1 | Banks and other financials show metrics that do not apply (fcf_yield for 209 of 326 banks, debt_to_equity 210, net_cash) and 15 banks show a wrong net_interest_income (InvestmentIncomeInterest minus interest expense); bank revenue perimeter undefined. DATA-INFERRED, being filing-checked now | 148 financials in the top 1000: JPM 14, BAC 32, MS 42, GS 45, WFC 47, C 57, BLK 70, SCHW 82, CB 90, COF 101, USB 136, PNC 149, AJG 197, MET 202, TFC 223 | Verifier running (`data-team/32`); then the bank template (`data-team/30`) |
| 2 | GE quarterly revenue is GE Capital only (wrong value shown) | GE 36 | Tag Mapper / Standardization; needs a filing-checked fix. First in the queue |
| 3 | Operating income blank where the statement has no subtotal. Ruling: blank with reason "not reported as a subtotal by this company", shown only after a rendered-statement check | CVX 23, AJG 197 | Ruling done (`data-team/27`); needs the reason layer (X2) |
| 4 | Total-debt inputs missing (about 1,800 of 2,200 blank ROIC cells); sole-tag candidates NotesPayable / SeniorNotes / SubordinatedDebt; wrong-zero audit | DHI 293, EG 547 named; population-wide count pending | Tag Mapper coexistence checks running (`data-team/31`) |
| 5 | Period-label errors in later filings (the stale-fill guards cover the refresh path, but stored values stay wrong until a detector exists) | CB 90, SPGI 96 (re-presentation), TT 122, MET 202, F 243, PPG 415 (re-presentation), STE 440, SWK 572, LGND 963 (shifted 10-K/A) | Stale-fill v3 dry-run in progress; filer label-error detector: Data Engineer, not started |
| 6 | Derived Q4 EPS / dividends per share by subtraction, and derived impossible signs | DOC 598, MUR 954, LEA 958 | Period Engineer; not started |
| 7 | Segment-note operating income mapped as consolidated | DD 500 (AAME, Kilroy outside top 1000) | Tag Mapper; not started |
| 8 | Reverse-split EPS history (splits missing from our split table) | none of GURE / NCRA / SVMB / BURU are top 1000, but the class exists | Split owner; park until after launch |
| 9 | Impossible market caps from wrong share counts (AKTX, TBLA, RPAY) | found by the campaign; the ranking is provisional | Campaign S000, then a share-count rule family |
| 10 | Nightly reprocess cancelled at the 180-minute cap every night since 10-13; matrix and tag-library steps still hit QueryCanceled | all | Data Engineer, next |

## Not in the top 1000 (park, do not spend launch time)
ANDE, HTZ, CDNL, FRD, CATO, ATEX, VVX, UNIT, BBW, UP, RTB, MGNC, EXP, IVDA, GRBK, AROC, AAME, KRC, PAGP, MSGE. They remain true examples for the rule families (ledger rows exist), but each matters only through the family fix.

## Rules
- Shard workers do not edit pipeline code or write to the database; findings go to `results/` and the families table in `status.md`.
- Heavy jobs only after a `ListAgents` and connection check (pooler ceiling about 15). Dhairya's agents run at most 3 DB-touching agents at once while shard waves run.
- A fix reaches the nightly only after: reviewed dry-run, Verifier filing sample with zero wrong rows, committed migration or code, and a re-measure on the top-1000 cohort.
