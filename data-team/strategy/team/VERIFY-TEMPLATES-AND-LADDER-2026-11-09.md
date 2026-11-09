Under test: (1) origin/work/data-engineer/sector-templates-seed 171ca25 (SECTOR-TEMPLATES-SEED-2026-11-01.md, cohort_v1_1_sic, mapper/sector_templates.py, migration 0120); (2) origin/work/certification-lead/blockers f4f6b63 (CERTIFICATION-BLOCKERS-2026-11-09.md, the ladder in §2 step 2).
Seed 20261109 for the company draw. SEC requests: 351 (sec.gov only, <= 3.4/s). Verifier session scrooner-c3. DB: read-only lookups on core.filing only. No writes.

# Verify: sector-template seed and certification ladder (2026-11-09)

## Verdicts

- **(1) Sector-template seed: FIX** (5 rows/assignments wrong, 1 structural gap, 1 CLI default). The banks, mortgage REITs, BDCs, lenders, crypto overrides and 13 of 17 override rows are right. The apply step is idempotent and reversible.
- **(2) Certification ladder: FIX before ruling.** As written, a company **can be certified with a wrong shown value**, by at least 6 routes. Each has a fix below.

## (1) Sector-template seed

### Method

1. **Every company in the seed's own assignment rule.** I applied the seed's SIC ranges and its 12 company assignments to the 1,000-company cohort: general 769, utility 51, reit_equity 51, bank 42, insurer 39, broker_am 37, lender 7, reit_mortgage 2, bdc 2.
2. **A filing check of 58 companies.** That is a seeded draw across all 9 templates (bank 5, lender 3, broker_am 6 incl. GS/MS/SCHW, insurer 5, reit_equity 4, reit_mortgage 2, utility 5 incl. KMI/LNG, bdc 2, general 4 + flagged), **plus every override company (13) and every company-assignment row (12)**.
3. **What each filing was read for:** every Statements R page of the company's latest 10-K, for the lines that define a template:
   - current totals, gross profit, cost of revenue, operating income, capex, inventory, R&D and receivables;
   - interest income, deposits and provision;
   - premiums and benefits;
   - real estate at cost;
   - repurchase agreements;
   - investment-company lines.

### Right (no change)

- **Banks (13 read: ASB, BAC, BNY, BOKF, BPOP, C, CBC, FHN, GBCI, JPM, MTB, PB, STT):** all print interest income and deposits; none prints current totals, gross profit or cost of revenue. OI is OUT by definition, as approved. CBC is correctly a bank by company assignment.
- **Mortgage REITs (NLY, AGNC):** interest income plus repurchase agreements; no OI or COR. reit_mortgage is right.
- **BDCs (ARCC, BXSL):** investment-company statements. bdc is right.
- **Lenders (AXP, SYF, RKT):** interest income (AXP and SYF also deposits); no COR or GP. lender is right.
- **Crypto / AI miners as general (MSTR, COIN, CRCL, IREN, HUT, WULF, BMNR):** all print classified balance sheets and corporate income statements. general is right.
- **Utilities (AEE, EIX, CWEN) and pipelines/LNG under utility (KMI, LNG):** classified balance sheets with OI. The utility template only drops GP / R&D / Piotroski, so placing midstream there is harmless.
- **Override rows right (13 of 17):**
  - JPM receivables: "Accrued interest and accounts receivable", combined, shown under its own label (ruling item 3).
  - BAC: "Customer and other receivables".
  - BOKF: "Receivables".
  - BPOP / C / STT operating expenses: total noninterest expense printed.
  - RYN, LINE, WY inventory, and SUI "Inventory of manufactured homes".
  - WY gross profit.
  - BRK-A inventory and cost of revenue.
  - SNEX inventory.
  - HOOD R&D: "Technology and development" (custom tag); accept only as the company's own label (definitional).

### Wrong (FIX)

| # | row | what the filing shows | fix |
|---|---|---|---|
| 1 | **EQH (Equitable) → general** (SIC 6411) | 0001333986-26-000012: premiums and policyholder benefits on the face; no current totals | **insurer** (company assignment) |
| 2 | **ACT (Enact) → general** (SIC 6411) | 0001823529-26-000060: premiums and benefits; no current totals. A mortgage insurer like ESNT and MTG, which ARE insurer | **insurer** |
| 3 | **INVH (Invitation Homes) → general** (SIC 6510) and **TRNO (Terreno) → general** (SIC 6500) | 0001687229-26-000016 / 0001476150-26-000011: real estate at cost and accumulated depreciation; no current totals. These are equity REITs | **reit_equity** (company assignments) |
| 4 | **Override MTB cost_of_revenue = yes** | 0000036270-26-000010 R5: the only cost-like line is "Other costs of operations" (`OtherNoninterestExpense`), a noninterest-expense component | **remove** (bank default OUT stands) |
| 5 | **Override BNY accounts_receivable = yes** | 0001390777-26-000033 R6: only "Accrued interest receivable" (`InterestReceivable`), which is not trade or fee receivables | **remove**, or re-evidence with the line it means |
| 6 | **Bank-like brokers under broker_am** (GS, MS, SCHW; also LPLA) | GS / MS / SCHW print interest income, deposits and repos, with no OI, no COR and no current totals; LPLA prints no OI. broker_am keeps OI, COR and current totals IN for them | assign GS, MS and SCHW to a bank-like template, or add overrides OUT for OI, COR and current totals (per company, from the face) |
| 7 | **Structural: "IN COND" implemented as IN for every company in the sector** | Approved §2 marks insurer OI, broker COR / OI and REIT COR as COND (in only for companies that print it). The seed writes them `yes` for all. Measured here: insurer OI 0 of 6 print it; REIT COR 1 of 7 (HST); broker COR 1 of 8 (SNEX) | build the company overlay the approved §1/§4 call for ("SIC proposes, the company's own statements decide"), or the template denominator counts cells the filing never prints as gaps |
| 8 | **CLI defaults** | `seed-sector-templates` defaults to `--templates SECTOR-TEMPLATES-2026-11-01.md --cohort shards.csv`, not the seed file and `cohort_v1_1_sic` | point the defaults at the seed inputs, or make both required |

### Noted, not a FIX (accountant decision)

- **Capex OUT for bank / insurer / equity REIT is "OUT by definition"** in the approved §2, but many of these companies print a capex line:
  - banks: 9 of 13 sampled print "purchases of premises and equipment" (FHN, STT, BPOP, C, GBCI, BOKF, PB, BNY, CBC);
  - insurers: 3 of 6 (MCY, MTG, BRK-A);
  - equity REITs: SPG, HST, BRX, INVH print capital-improvement or development lines.

  OUT hides printed values. Keep it as a ruling, and label it on the page.
- **Current assets / liabilities stay IN for bank / insurer / REIT / broker** as approved ("not yet evidenced"). Evidence now exists: 13 of 13 banks and 6 of 6 insurers print none. VERIFY-BS-DERIVE-2026-11-08 also found 9 of 9 `unclassified_balance_sheet` reasons right. Promote them to OUT, or keep IN with the BS lane's reason, but do not count them as gaps.

### Apply step

- **Dry run by default.** `--apply` also needs `--confirm-version tv1-2026.11.01-approved`, and `--validate-db` checks names and ids (read-only).
- **What `--apply` writes:** `analytics.company_data_point_template`. Within one transaction it deletes the planned companies' rows at `effective_from = 2026-11-01`, then batch-inserts 163 rows per company (1,000 companies × 163 = 163,000 rows).
- **Idempotent: yes.** A rerun gives the same rows.
- **Reversible: yes, by hand.** Run `delete … where effective_from = '2026-11-01' and template_version = 'tv1-2026.11.01-approved'`; the table is empty today. There is no rule_run row or before-image, so add one if later versions overwrite data.

## (2) Certification ladder: can a company be certified with a wrong shown value?

**Yes.** The holes, each seen in this week's draws, and the fix:

| # | hole | example from the record | fix |
|---|---|---|---|
| 1 | **Scope:** `reconciled` and `verified` look only at the 11 headline cells (latest FY + latest Q). Every other shown cell (older periods, the other ~150 data points, derived quarters) can be wrong in a certified company | 0 / 62 headline-type shown values were wrong at MSFT/HD, but the first CF-gaps draw found wrong reasons and withdrawn right values outside any headline | `verified` also needs a seeded random draw over **all shown cells** of the company (or the cohort, with a stated error bound). `certified` must state its scope on the page |
| 2 | **"None DISAGREE" is headline-only:** a DISAGREE on any other shown cell does not block | — | **any served DISAGREE blocks** `reconciled`; resolve it to a value or a reasoned blank first |
| 3 | **PROVEN is not proof of the right concept:** position plus identity ties hold when the wrong line is read consistently | ELV and SLB: segment totals tagged OperatingIncomeLoss; DAL: net interest as interest expense; WPC: a misused tag (VERIFY-TEMPLATE-OUTS). KMB: mezzanine counted inside total liabilities while the identity still ties (VERIFY-BS-DERIVE) | PROVEN must include an independent **face read**: R page / printed HTML label and position at that column, not FSN `num` alone. A label or line check must also reject segment-note totals and "net" lines for gross concepts |
| 4 | **PROVEN is not proof of the latest print:** a cell proven against the accession it cites can still be the superseded original | MSFT FY2016 NI 16,798 vs restated 20,539; Brixmor FY2015/16 buybacks (VERIFY-POSTLOAD-MSFT-HD; CF-GAPS re-draw) | PROVEN also checks that the cited accession is the latest accepted filing printing that column |
| 5 | **Derived and note-sourced cells have no face to DISAGREE with** | Q4 = FY − 9M; note-sourced interest expense / DPS | a derived cell is PROVEN only if both inputs are PROVEN, from latest copies, with the same-basis witness. Note-sourced cells need a note-page read with label |
| 6 | **Certification is not invalidated when a value changes after `verified_at`** (nightly refresh, new filings, metric recompute) | blocker 8: metrics not recomputed after the write, so market cap / P/E are stale | store a hash of the verified cells; any change to a shown cell or its metric inputs drops the company back to `checks_clean` until re-proven and re-verified |

Two more weaknesses. They do not produce wrong *values*, but they certify wrong *blanks*:

- **"Valued or reasoned" accepts a false reason.** The MSFT/HD draw had 11 of 18 blanks with a reason that the filing contradicted. `certified` should require the Verifier's blank draw to pass, not just a non-null reason.
- **A wrong template makes wrong blanks "out of template".** Examples: EQH as general, and MTB COR forced IN. The seed FIXes above must land before template-aware I11 (step 3a) is trusted.

**The `verified` record must be written by the Verifier, not the builder.** Each row should carry the accession, page and label per cell, plus the draw seed. The certification lead's step 3b table should enforce that (a writer role, or a signed source field).
