# Total liabilities and current items on the FSN store: derived or reasoned (2026-11-02)

For Dhairya. Branch `work/bs/derive-tl-current`. Scratch database only: nothing was written to Supabase, no migration, zero new SEC requests (the company directories were built from the cached FSN zips).

## The ask

Cohort dry run 41515845455 (artifact `fsn-cohort`, `gaps.csv`) left these `no_mapped_line` keys:

- total liabilities: 9,407;
- current assets: 7,575;
- current liabilities: 7,575.

You asked for two things:

1. Derive total liabilities only where the filing's own calc tree or the liabilities-and-equity (L&E) identity supports it, from the same accession.
2. Give banks, insurers and REITs that print no current items a reason, with evidence.

## Result

| Data point | Gap keys | Freed or reasoned | Still open |
|---|---|---|---|
| Total liabilities | 9,407 | **8,921** (94.8%) | 486 |
| Current assets | 7,575 | **7,104** (93.8%) | 471 |
| Current liabilities | 7,575 | **7,104** (93.8%) | 471 |

Measured by running the pilot sequence (load, seed, map, checks, `pilot.report_company`) on all 380 gap companies twice, without and then with the new reader, and comparing the gap keys. Per-company numbers are in [`results/bs-derive-tl-current/summary.json`](results/bs-derive-tl-current/summary.json).

## What each change freed or reasoned

All the code is in `pipeline/src/scrooner_pipeline/fsn_store/bs_derive.py`, called from `pilot.report_company` only for keys that have no stored cell.

| Change (commit) | Rule id | Keys |
|---|---|---|
| **1. Calc route** (c9ec649c) | `fsn.derive_total_liabilities_calc@1` | Total liabilities 4,742 |
| **2. Blank child counts as zero only when the tie proves it** (57c3d551) | same calc rule; `inputs.blank_children` lists the blanks | Total liabilities 4,102 more |
| **3. Identity route** (c9ec649c) | `fsn.derive_total_liabilities_identity@1` | Total liabilities 65 |
| **4. Unclassified balance sheet reason** (c9ec649c) | `fsn.unclassified_balance_sheet@1`, state `not_presented`, reason `unclassified_balance_sheet` | Current assets 7,104; current liabilities 7,104 |
| **5. Face column = the closing total is valued at the date** (0b4da28f) | — | +4 total liabilities, +272 each current item |
| **6. A current total in any statement of the filing blocks the reason** (this push) | — | −0 counted keys (it withdrew 2 reasons that were wrong) |

Changes 1 to 3 add up to 8,909 keys when each key is assigned to its nearest derived date. The pilot's own ±10-day match frees 8,921; the 12-key difference is that matching.

### How each change works

**1. Calc route.** It takes the L&E children from the filing's own balance-sheet calc group.

- Capitalization subtotals are expanded into their children (utilities print "total capitalization").
- Each child is classed with the BS lane's `classify_line`, imported from `bs_totals_detect`.
- Total liabilities is the sum of the liability children, weight-signed.
- It is published only if liabilities + equity + temporary equity ties to the printed L&E within the filing's rounding.
- It refuses when:
  - a child cannot be classed;
  - liabilities or equity is missing;
  - the tie fails;
  - the face prints its own `Liabilities` line (a printed total is never derived).

Example: NextEra 10-Q 0000753308-20-000150, 2020-06-30. Current 12,365M + other liabilities 25,064M + long-term debt 42,667M = **80,096M**. With equity incl. NCI of 41,574M and redeemable NCI of 291M, that ties to L&E 121,961M exactly.

**2. Blank child.** A calc child with no value in the column counts as zero only when the valued children still tie to L&E. `CommitmentsAndContingencies` is allowed only when it is blank or 0; a valued one refuses.

- 4,326 of the 4,462 derived rows that use a blank child have `CommitmentsAndContingencies` as one of the blanks.
- The rest are lines such as a lease or related-party note that was empty that quarter.

**3. Identity route.** It runs only when the filing has no calc arcs under L&E. Total liabilities = L&E − total equity incl. NCI − temporary equity, with every term printed and valued in the same accession.

- Example: Oracle, 2024-08-31, = 132,945M.

**4. Unclassified reason.** It is given when the balance sheet has no `AssetsCurrent` or `LiabilitiesCurrent` and no "total current assets/liabilities" label (custom tags included).

- The evidence on each cell is `input_refs.accession` and `face_lines`.
- The display text is added to `select.REASON_TEXT`.

| Sector (template) | Current keys reasoned (each item) |
|---|---|
| REIT | 1,852 |
| Bank | 1,772 |
| Insurer | 1,661 |
| General | 1,819 |

"General" here is 50 companies, and they are not mistakes. Each one really prints an unclassified balance sheet:

- broker-dealers and asset managers (Schwab, Goldman Sachs, Morgan Stanley, LPL, Interactive Brokers, KKR, Blackstone, Ares, T. Rowe);
- card and consumer lenders (American Express, Synchrony, Credit Acceptance, OneMain, Affirm);
- homebuilders (NVR, Lennar, D.R. Horton, Toll Brothers, PulteGroup);
- Deere, CNH Industrial, GATX, U-Haul, Rocket and Equitable.

Their sector template says "general" only because of the SIC code. The full list is in `summary.json` under `per_company`.

**5. Face column.** A column now counts as a balance-sheet face column when the statement's own closing total (L&E, else Assets) is valued at that date and the filing's BS check passed. The latest accepted copy decides.

- The earlier test needed at least 50% of face lines valued. It rejected segment-split faces such as NVR, Lennar, Berkshire and Ares, where most lines are valued per member.

**6. Current total elsewhere in the filing** (found in a spot check). Planet Fitness 10-Q 0001193125-15-310710 has two balance sheets:

- the pre-IPO registrant shell is filed as stmt `BS`, with no current items;
- the operating predecessor's classified balance sheet is filed as stmt `UN`, and it prints `AssetsCurrent`.

Saying "unclassified" there would be wrong. So any non-parenthetical `AssetsCurrent` or `LiabilitiesCurrent` line in any statement of the accession now blocks the reason. Across all 380 companies this withdrew only those 2 reasons, and they were `no_face_print_for_period` keys, not `no_mapped_line` keys. The case is unit-tested and mutation-checked.

## What is still open

| Cause | Total liabilities | Current items (each) | Biggest companies |
|---|---|---|---|
| Face column exists, not derived or reasoned | 315 keys, 66 companies | 286 keys, 64 companies | TL: Marriott 34, Targa 25, Evergy 17, PPL 15, News Corp 14, Energy Transfer 12. Current: Old Republic 15, Chubb 14, Associated Banc-Corp 13, U-Haul 12, UDR 11, AIG 11 |
| No stored filing prints the date | 171 keys | 185 keys | TL: Paramount Skydance 39, Shopify 11, Dow 9, Disney 8. Current: Pinnacle Financial 42, Regency Centers 15, CNH 9 |

Why total liabilities was not derived, counted on the latest-copy columns:

| Reason | Columns |
|---|---|
| Calc children do not tie to L&E | 196 |
| Identity route: temporary equity not valued | 5 |
| Calc children lack a liability or equity part | 5 |
| `DeferredTaxAssetsLiabilitiesNet` child with a debit balance | 4 |
| The face prints `Liabilities` | 4 |
| Capitalization total without arcs | 2 |
| No printed L&E | 2 |

I refused rather than guessed in every one of these.

- The not-tied columns are mostly filings whose calc tree is incomplete or nests a subtotal that is not on the face. Each needs a look at the filing, not a looser rule.
- The current-item columns that are still open (Chubb, Old Republic, AIG, UDR and others) have no current lines on the face. Most likely their BS filing check failed at that date, which excludes the column. I have not split this cause yet.
- "No stored filing prints the date" is store coverage (the date is in the calendar, but no loaded filing prints it), not a mapping problem.

## Spot checks against the filings

| Company | Date | Route | Value | Filing check |
|---|---|---|---|---|
| Coca-Cola | 2020-12-31 | calc | 66,012M | L&E 87,296 − equity 21,284 |
| NextEra | 2020-06-30 | calc (capitalization) | 80,096M | ties to L&E 121,961 |
| DTE | 2016 | calc | 22,542M | NCI correctly kept out of liabilities |
| Oracle | 2024-08-31 | identity | 132,945M | L&E − equity |
| Planet Fitness | 2015-06-30 | — | no reason given | predecessor balance sheet is classified (change 6) |

Every derived cell carries `derivation = {formula, accession, inputs}`, with each input tag and value. A reviewer can check it against that one filing.

## Tests and rerun

- `pipeline/tests/unit/test_fsn_bs_derive.py`: 7 tests. They use NextEra's real numbers and the Planet Fitness shell case. Each was mutation-checked: it fails when the guard it covers is removed.
- Measurement script, scratch database only (it refuses anything else):

```bash
SCRATCH_DATABASE_URL=postgresql://scrooner_test@/scrooner_test_1?host=/tmp&port=5433 \
  pipeline/.venv/bin/python pipeline/scripts/slot_records/bs_derive_measure.py \
  reports.json calendar.csv.gz out_dir companies/*
```

The script is resumable (`progress.jsonl` per company), and it writes `measure.json` and `rows.jsonl`.

## Not done, needs a decision

- Nothing is promoted. The derived and `not_presented` cells appear only in pilot reports.
- Writing them to production cells is a production write, so it needs the founder's typed approval.
- A Verifier pass on a sample of calc-route values (especially the blank-child ones) is the natural next step before any release.
