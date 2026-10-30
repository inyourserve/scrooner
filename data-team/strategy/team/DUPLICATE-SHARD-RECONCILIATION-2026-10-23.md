# Duplicate-shard reconciliation (38 shards in two versions), 2026-10-23

Author: scrooner-7b. Read-only, no deletions. 'upstream' = the version already on origin/main (committed by another session); 'session-7b' = results/session-7b-versions/. Both are worker output from independent runs of the same shard.
Winner rule (mechanical heuristic): the version citing more distinct accession numbers plus FILING-CHECKED labels; tie goes to upstream because it is already committed. This measures how much was opened, not whether findings are right; a Verifier should sample disagreements before either version is quoted as evidence.

| shard | upstream: lines / accessions / FC labels / verdict word | 7b: lines / accessions / FC labels / verdict word | winner (heuristic) | upstream last commit |
|---|---|---|---|---|
| S020 | 368 / 15 / 39 / False | 114 / 11 / 16 / False | upstream | 1057d51 Top-1000: S020 results; DEF 14A displaces 10-K net income (FDX |
| S021 | 309 / 14 / 27 / False | 77 / 10 / 16 / False | upstream | 5395bc8 Top-1000: S021 results; MET 606 revenue and adjusted-earnings  |
| S022 | 428 / 19 / 46 / False | 60 / 10 / 19 / False | upstream | fd3c41d Top-1000: S022 results; DEF 14A authoritative demotes 10-K NI  |
| S023 | 357 / 31 / 46 / False | 83 / 13 / 13 / False | upstream | 2be54bc Top-1000: S023 results; ProfitLoss-over-NetIncomeLoss now 8 co |
| S024 | 459 / 22 / 56 / False | 63 / 10 / 16 / False | upstream | 7e5318a Top-1000: S024 results; BKR zero history, TEAM IFRS history |
| S025 | 309 / 19 / 34 / False | 73 / 11 / 15 / False | upstream | f7ab923 Top-1000: S025 results; FIX non-authoritative 10-Q beats 10-K  |
| S026 | 448 / 25 / 60 / False | 59 / 10 / 5 / False | upstream | 1eebc69 Top-1000: S026 results; stale resolved rows never rebuilt |
| S027 | 365 / 37 / 48 / False | 90 / 12 / 22 / False | upstream | 7fcb72d Top-1000: S027 results; 10-KT transition reports never collect |
| S028 | 474 / 28 / 54 / False | 68 / 10 / 16 / False | upstream | 631fd78 Top-1000: S028 results; CVNA split applied backwards, EXC sub- |
| S029 | 402 / 24 / 48 / False | 97 / 13 / 11 / False | upstream | e4b38dc Top-1000: S029 results; SG&A as G&A only, SalesRevenueGoodsNet |
| S030 | 291 / 35 / 39 / False | 60 / 10 / 12 / False | upstream | d495f87 Top-1000: S030 results |
| S031 | 263 / 34 / 61 / False | 71 / 10 / 15 / False | upstream | a515c37 Top-1000: S031 results; Up-C template, mixed-tag revenue serie |
| S032 | 558 / 44 / 63 / False | 62 / 11 / 18 / False | upstream | 0c1a3eb Top-1000: S032 results; PCG proxy NI zero, subsidiary-held sha |
| S033 | 471 / 23 / 47 / False | 68 / 10 / 20 / False | upstream | 03530ef Top-1000: S033 results; TKO Up-C and stub period |
| S034 | 313 / 32 / 41 / False | 64 / 10 / 15 / False | upstream | 47c4797 Top-1000: S034 results |
| S035 | 330 / 33 / 89 / False | 112 / 10 / 12 / False | upstream | 8fa41b1 Top-1000: S035 results; DEF 14A scale both ways (MDLN trillion |
| S036 | 354 / 42 / 65 / False | 70 / 11 / 10 / False | upstream | bdf2766 Top-1000: partial shard results before rate-limit resume |
| S037 | 446 / 32 / 54 / False | 64 / 10 / 12 / False | upstream | bdf2766 Top-1000: partial shard results before rate-limit resume |
| S038 | 333 / 26 / 38 / False | 121 / 11 / 12 / False | upstream | bdf2766 Top-1000: partial shard results before rate-limit resume |
| S039 | 293 / 39 / 59 / False | 67 / 10 / 17 / False | upstream | 00f9459 Top-1000: S039 results |
| S040 | 380 / 33 / 48 / False | 69 / 11 / 14 / False | upstream | 0d3aad1 Top-1000: S040 results |
| S041 | 290 / 36 / 43 / False | 75 / 11 / 10 / False | upstream | 89e9b28 Top-1000: S041 results; DRI spin-off stored as reverse split |
| S042 | 313 / 34 / 40 / False | 74 / 12 / 18 / False | upstream | 6a47351 Top-1000: S042 results |
| S043 | 412 / 35 / 79 / False | 122 / 10 / 14 / False | upstream | 6a47351 Top-1000: S042 results |
| S044 | 287 / 36 / 34 / False | 74 / 11 / 16 / False | upstream | 37bf56b Top-1000: S047 results; acquiree 8-K stored as acquirer (AMCR/ |
| S045 | 274 / 37 / 34 / False | 67 / 4 / 7 / False | upstream | 37bf56b Top-1000: S047 results; acquiree 8-K stored as acquirer (AMCR/ |
| S046 | 313 / 32 / 31 / False | 83 / 11 / 9 / False | upstream | 56dd473 Top-1000: S046 results |
| S047 | 357 / 33 / 81 / False | 96 / 11 / 28 / False | upstream | e92f6b0 Top-1000: partial shard results before rate-limit resume |
| S048 | 396 / 34 / 111 / False | 87 / 10 / 19 / False | upstream | 448979a Top-1000: S048 results; TTM from non-consecutive quarters |
| S049 | 411 / 38 / 115 / False | 76 / 11 / 14 / False | upstream | 97d33d6 Top-1000: in-progress shard result files |
| S050 | 333 / 35 / 78 / False | 75 / 10 / 16 / False | upstream | e7a6979 Top-1000: S050 results; S052 running |
| S051 | 257 / 24 / 33 / False | 71 / 5 / 14 / False | upstream | 52ed71a Top-1000: S051 results |
| S052 | 458 / 38 / 78 / False | 61 / 11 / 12 / False | upstream | 2d491eb Top-1000: S052 results |
| S053 | 307 / 31 / 78 / False | 114 / 10 / 22 / False | upstream | 1b93bc9 Top-1000: S053 results |
| S054 | 356 / 32 / 110 / False | 62 / 11 / 12 / False | upstream | 8176471 Top-1000: S054 results |
| S055 | 416 / 32 / 116 / False | 70 / 10 / 16 / False | upstream | 0ede9bd Top-1000: S055 results |
| S056 | 344 / 34 / 81 / False | 73 / 10 / 16 / False | upstream | 34a9158 Top-1000: S056 results; EQH proxy NI in dollars, recap stored  |
| S057 | 343 / 36 / 52 / False | 54 / 11 / 9 / False | upstream | a484250 Top-1000: S057 results; PNFP stores Synovus 8-K as its own |

Winner counts: upstream 38, session-7b 0 (of 38).

## Caveats
- ALL-SHARDS-ROOT-CAUSES.md and its digests were built from the session-7b versions for these shards; where the upstream version disagrees on a finding the merged document may overstate or miss it.
- No field-level comparison of specific wrong values between the two versions was done; that needs a per-shard diff and a Verifier sample.
- No file was deleted or edited.