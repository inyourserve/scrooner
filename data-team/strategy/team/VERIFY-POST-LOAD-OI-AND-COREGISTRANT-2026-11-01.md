# VERIFY (post-load): operating income not presented and shared-accession demotion (2026-11-01)
Loaded runs in analytics.rule_run: slot.is_operating_income_not_presented@1 (run 4d7b48ee, 3,313 hides of 13,942 reasons) and entity.shared_accession_demote_coregistrant_facts@1 (run 93daea3a, 4 companies, 600 cells archived). Seed 20261104, 15 cells each from analytics.canonical_fact_retired. analytics.cell_proof is EMPTY, so no proof verdicts could be drawn. Verifier 2 (scrooner-bc). 140 SEC requests.

## Result: error rate 0 of 30
- **Operating income not presented: 15 of 15 hides right.** Each income statement (selected with select_income_statement, scanned by XBRL element and label) prints no operating income line: FTAI, EVR x2, AOS, CDE, LEA, OHI, AMG x2, AFL, BRO, FCFS, CAG, ROK, MET. Positive control: the scan finds "Operating income" on MSFT 0001193125-25-256321 and HD 0000354950-23-000185. All 15 rows are gone from canonical_fact.
- **Co-registrant demotion: 15 of 15 removals right.** Every removed value comes from the PARENT's combined filing and equals the parent block, not the subsidiary's own:
  - SoCalGas capex 4,687 is Sempra's; SoCalGas prints 967. SoCalGas basic EPS 0.71 is Sempra's, and SoCalGas has no EPS.
  - Consumers equity 9,726 and income tax (22) are CMS's; Consumers prints 13,656 and 92.
  - Entergy Arkansas net income, operating income and diluted EPS are Entergy Corp's. Its D&A 1,206,649 is printed on no statement, and Arkansas's own CF line differs.
  - SCE capex, dividends, revenue and other income are EIX's block.
  - The parent figures I flagged earlier (SoCalGas 115,281M, Consumers 41,683M, SCE 96,171M, Entergy Arkansas 79,002,618K) no longer show.
- **Consequence:** the 4 subsidiaries now show blanks for those cells, not their own values. The fill should come from each subsidiary's own block in the combined filing, which every R page prints AFTER the parent block.
