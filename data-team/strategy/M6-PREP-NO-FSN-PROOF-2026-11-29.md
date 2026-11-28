# M6 prep: proof for ranks 1,001-5,000 without FSN (read-only probe, 2026-11-29)

Rank = market_cap order in the latest analytics.company_screening_snapshot dataset_version. Ranks 1,001-5,000 hold 4,000
companies; 3,315 have no fsn.filing row (DB-checked); 4,368 have a market cap. fsn.filing covers 1,036 CIKs.

## Inputs
- Resolver (data-team/tags/line_map/tools/standard_run.py, extract.sql, extract_bs.sql, extract_notefacts.sql, extract_facelines.sql):
  reads fsn.filing, fsn.line, fsn.calc_arc, fsn.value, fsn.tag. Without FSN the extract returns 0 filings: it cannot run from
  core.fact alone. Blocked: every statement-line cell (statement line identity, calc tree, presented position, scale),
  hence every IS/BS/CF template cell. core.fact (standard tags) feeds only notefacts / role tags.
- Proof (scrooner_pipeline.jobs.proof, run --fsn-source files|db): needs the shown cell (analytics.canonical_fact row, old pipeline,
  exists for 3,361 companies beyond rank 1,000) plus the shown accession's FSN structure (pre/cal/num). The fsn-notes bucket holds
  only the loaded cohort (2022q2 sub: 932 CIKs; none of the 10), so there is no fallback source.
- Template: analytics.company_data_point_template has 106 companies; none of the 10 (sector_default catalog exists, not seeded).

## Probe: 10 companies, proof dry-run (--fsn-source files, report JSONL only, no write)
Cells = proof rows (canonical_fact cells since 2015). Command: `scrooner-proof run --ciks <10> --fsn-source files --fsn-root <tmp> --report <jsonl> --statement-timeout 5min`.
8,275 cells: PROVEN 0, DISAGREE 23, UNCHECKED 8,252 (HIDDEN with reason: 0; no display-state rows exist for these).

| Company | cells | no FSN structure | no claim to prove against | DISAGREE |
|---|---|---|---|---|
| ABCB bank | 848 | 848 | 0 | 0 |
| GNW insurer | 808 | 755 | 43 | 10 |
| PLMR insurer | 612 | 609 | 3 | 0 |
| SBRA REIT | 851 | 804 | 46 | 1 |
| MWA industrial, FYE Sep | 1267 | 1218 | 45 | 4 |
| ESAB industrial | 589 | 571 | 18 | 0 |
| MGNI tech | 1197 | 1169 | 28 | 0 |
| BILL tech, FYE Jun | 835 | 811 | 21 | 3 |
| ARX IPO 2025 | 168 | 162 | 6 | 0 |
| HP energy, FYE Sep | 1100 | 1049 | 46 | 5 |

Top reasons OPEN: "no FSN structure for the shown accession" 6,078 + derived fact's filing 1,830 + FSN quarter 2026m11 not in bucket 88
(= 7,996, 96.6%); "no company_tag_map claim" 256 (3.1%). All 23 DISAGREE: "shown is not the authoritative copy" (old-mapper rows, 2015-2025).
Evidence label: DATA-INFERRED (tool output); not filing-checked.

## Filing check of PROVEN cells: not done. There are 0 PROVEN cells to sample.

## What a production serve for 1,001-5,000 needs
1. FSN rows for the shown accessions of each company (SEC FSDS/per-filing XBRL load: ~15 SEC requests per filing, 2 req/s total;
   ~44 filings/company since 2015 backfill = ~660k requests per 1,000 companies, ~3.8 days; 5,000 cos steady ~1.6 h/day, PIPELINE.md s5).
   Then resolver (standard_run + resolve_all) -> canonical_fact via the structural loader; proof --write; cell_display_state; a template seed
   (sector_default rows into company_data_point_template for each company).
2. Writes (cell_proof, cell_display_state, canonical_fact, template) are production writes: founder's own typed words required; a
   relayed message from a peer/coordinator agent is not approval, so none were made here.
3. Disk: this probe's FSN quarter download filled /private/tmp to 99%; use a shared cache and clean it.
