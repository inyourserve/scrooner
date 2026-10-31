# Verify: co-registrant demotion, rule entity.shared_accession_demote_coregistrant_facts@1 (origin/main ec6277c), 2026-10-31
Seed 20261031. Files: demote_plan_cells.jsonl (600 cells), code under test normalizer/shared_accession_cleanup.py at main ec6277c (read only, not used as evidence). Claimed counts: facts_to_demote=1771, cells=600, filings=4. Evidence class: FILING-CHECKED.

## Result
**YES. GATE: zero wrong-to-demote cells. 20 of 20 sampled cells right to demote; 0 wrong; 0 unreadable.**
One condition for the approver (outside the sample, see Findings 1): 4 SCE cells (inventory x2, cf_inventory_change x2) carry the parent's figure, but Edison International's printed value is the same number as SCE's own. Demoting them shows no wrong value; it blanks 4 values that would have been numerically right for SCE.

## Method
- Filing identity: `<accession>-index-headers.html` under the subsidiary's CIK folder. For all four, the first FILER block and the accession prefix are the parent, and the subsidiary appears as a further FILER (co-registrant):
  - 0000065984-26-000283, 10-Q, period 2026-06-30, filed 2026-07-31: ENTERGY CORP /DE/ (65984) first; ENTERGY ARKANSAS, LLC (7323) is one of 6 co-registrants.
  - 0000827052-26-000059, 10-Q, 2026-06-30, filed 2026-07-30: EDISON INTERNATIONAL (827052) first; SOUTHERN CALIFORNIA EDISON Co (92103) second.
  - 0001032208-26-000045, 10-Q, 2026-06-30, filed 2026-08-06: SEMPRA (1032208) first; SDG&E (86521) and SOUTHERN CALIFORNIA GAS CO (92108) follow.
  - 0000811156-26-000032, 10-Q, 2026-09-30, filed 2026-10-27: CMS ENERGY CORP (811156) first; CONSUMERS ENERGY CO (201533) second.
- Values: FilingSummary.xml, then the R pages, through the slot-records `SecClient` (sec.gov only, SEC_USER_AGENT, 4/s or slower) and `filing_kit.parse_rpage`. Columns matched by end date plus "N Months Ended" (`months=`). Scale read from the page header. Tolerance is half the printed unit. Every sampled match was exact.
- Registrant blocks: Entergy puts every registrant on one page as `dei:LegalEntityAxis` sections ("Entergy Arkansas [Member]"). Edison, Sempra and CMS give each subsidiary its own "- SCE" / "- SoCalGas" / "Consumers Energy Company" page. **The first block on those subsidiary pages is the PARENT (the undimensioned default context) printed under the subsidiary's labels.** The subsidiary's own values start below a header row with the entity name ("SCE", "SoCalGas", "Consumers Energy Company"). I read the subsidiary's values only from below that header.
- Equity statements (Entergy R6, Sempra R7, SoCalGas R20, Edison R50/R51) are transposed: components are columns and balances are rows. I read them raw. Entergy's balance rows have no date in their label, so I placed them in order and tied them to the balance sheet: R6 row 36 = BS 2025-06-30 16,308,940; row 38 = BS 2025-12-31 17,014,167; row 73 = BS 2026-06-30 18,320,686. That makes row 58 the 2026-03-31 balance.
- Supplementary screen (DATA-INFERRED, not part of the gate): all 600 cells checked against every number in the parent block and the subsidiary block of the 38 fetched statement pages, matched on period. Result: 432 match the parent only, 0 match the subsidiary only after hand review, 14 flagged and re-read by hand, 154 not found on the fetched pages (mostly transposed equity pages and note-only values).

## Sample
Draw: `random.Random(20261031)`. For each subsidiary, in the order 142, 1079, 1080, 1165, over base (non-`_resolved`) cells sorted by id: one mandatory instant (stockholders_equity / total_assets / cash_and_equivalents), one mandatory duration (revenue / net_income / operating_income / D&A / share_buybacks / basic or diluted EPS), then 3 seeded picks with distinct concept names. That gives 5 per subsidiary, 20 total.
Picked ids: 364985492, 364985477, 364985514, 364985531, 364985471 (Entergy Arkansas); 364989426, 364989412, 364989480, 364989432, 364989512 (SCE); 364989554, 364989541, 364989607, 364989609, 364989568 (SoCalGas); 364991449, 364991432, 364991459, 364991502, 364991490 (Consumers).
Resolved twins (same key, same value in the plan; each verdict carries to its twin): 102503987, 100461730, 101937736, 102452363, 99564078, 101888471, 120268707, 120574877, 102452651, 323126416, 120674339, 102076167, 358568014, 357926982, 358131957.

## Cell table
Units: $ millions unless noted (Entergy pages print $ thousands). Parent and subsidiary values come from the same accession's R page.

| Cell id | Company | Concept | Period | Cell value | Parent face | Subsidiary face | R page | Verdict |
|---|---|---|---|---|---|---|---|---|
| 364985492 | Entergy Arkansas (142) | stockholders_equity | 2026-03-31 | 17,438,143,000 | 17,438,143,000 (Total, incl. NCI) | 4,792,809,000 | 65984-26-000283 R6 row 58 | RIGHT-TO-DEMOTE |
| 364985477 | Entergy Arkansas | revenue | Q2 2026 (3M to 2026-06-30) | 3,523,638,000 | 3,523,638 thousand | 693,486 thousand | R2 | RIGHT-TO-DEMOTE |
| 364985514 | Entergy Arkansas | income_tax_expense | Q2 2025 | 138,399,000 | 138,399 thousand | 25,677 thousand | R2 | RIGHT-TO-DEMOTE |
| 364985531 | Entergy Arkansas | total_assets | 2025-12-31 | 71,890,730,000 | 71,890,730 thousand | 16,470,902 thousand | R4 | RIGHT-TO-DEMOTE |
| 364985471 | Entergy Arkansas | accounts_payable | 2025-12-31 | 2,565,546,000 | 2,565,546 thousand | 103,411 associated + 346,541 other (two lines) | R4 | RIGHT-TO-DEMOTE |
| 364989426 | SCE (1079) | stockholders_equity | 2024-12-31 | 17,740,000,000 | 17,740 (opening balance, 3M to Mar 31 2025) | 21,751 | 827052-26-000059 R50 / R51 | RIGHT-TO-DEMOTE |
| 364989412 | SCE | operating_income | Q2 2025 | 775,000,000 | 775 | 794 | R2; SCE block of R8 | RIGHT-TO-DEMOTE |
| 364989480 | SCE | total_assets | 2026-06-30 | 96,171,000,000 | 96,171 | 96,018 | R4; SCE block of R10 | RIGHT-TO-DEMOTE |
| 364989432 | SCE | basic_eps | Q2 2026 | 1.39 | 1.39 | not presented (SCE income statement has no EPS) | R2; R8 | RIGHT-TO-DEMOTE |
| 364989512 | SCE | dividends_per_share | Q2 2026 | 0.8775 | 0.8775 | 0.9888 | R50 / R51 | RIGHT-TO-DEMOTE |
| 364989554 | SoCalGas (1080) | stockholders_equity | 2025-06-30 | 38,296,000,000 | 38,296 (total equity) | 8,691 | 1032208-26-000045 R7 / R20 | RIGHT-TO-DEMOTE |
| 364989541 | SoCalGas | depreciation_and_amortization | 6M 2026 | 1,233,000,000 | 1,233 | 549 | R6; SoCalGas block of R19 | RIGHT-TO-DEMOTE |
| 364989607 | SoCalGas | dividends_per_share | Q2 2025 | 0.64 | 0.64 (common) | no common DPS presented (only preferred $0.37) | R8 / R21 | RIGHT-TO-DEMOTE |
| 364989609 | SoCalGas | effective_tax_rate_reported | Q2 2026 | 0.17 | 17.00% | 0.00% | R67 (Income taxes, Details) | RIGHT-TO-DEMOTE |
| 364989568 | SoCalGas | current_liabilities | 2026-06-30 | 22,105,000,000 | 22,105 | 2,617 | R4; SoCalGas block of R17 | RIGHT-TO-DEMOTE |
| 364991449 | Consumers (1165) | stockholders_equity | 2025-12-31 | 9,144,000,000 | 9,144 (total stockholders' equity) | 12,578 | 811156-26-000032 R7; Consumers block of R14 | RIGHT-TO-DEMOTE |
| 364991432 | Consumers | depreciation_and_amortization | Q3 2025 | 288,000,000 | 288 | 274 | R2; Consumers block of R10 | RIGHT-TO-DEMOTE |
| 364991459 | Consumers | cash_and_equivalents | 2026-09-30 | 451,000,000 | 451 | 257 | R7; R14 | RIGHT-TO-DEMOTE |
| 364991502 | Consumers | total_debt_split | 2025-12-31 | 18,757,000,000 | 18,757 (LTD carrying amount incl. current) | 12,097 + 1,005 related party = 13,102 | R56 (Financial Instruments, Details) | RIGHT-TO-DEMOTE |
| 364991490 | Consumers | ppe_net | 2026-09-30 | 31,940,000,000 | 31,940 (total plant, property and equipment) | 30,860 | R7; R14 | RIGHT-TO-DEMOTE |

## Withheld cells (avoidable holds)
None in the sample. Outside the sample, the 4 coincident SCE cells (Findings 1) become avoidable blanks if demoted.

## False holds
None.

## Findings for the builder
1. **Coincident values (approver must know; outside the sample).** In 0000827052-26-000059, Edison International's printed Inventory (R4: 567 at 2026-06-30, 535 at 2025-12-31) and cash-flow Inventory change (R6: -39 for 6M 2026, 12 for 6M 2025) equal SCE's own lines (R10 SCE block: 567 / 535; R11 SCE block: -39 / 12), because SCE holds all of EIX's inventory. The cells are 364989395, 364989396 (inventory) and 364989436, 364989437 (cf_inventory_change). The brief's wording ("WRONG-TO-DEMOTE if the cell equals the subsidiary's own value") does not cover a value that equals both. Demoting them shows no wrong value; it replaces a numerically right value with a blank whose reason (`parent_values_filed_under_coregistrant_cik`) is true of the source fact but not of the number. Recommended action: keep the demotion (the source fact is the parent's context). In a follow-up, re-source subsidiary cells from the filing's own LegalEntityAxis=subsidiary facts so all of these blanks fill. After the fix, re-verify those 4 cells against the R10/R11 SCE blocks.
2. **Sign check, not a collision.** SCE income_tax_expense Q2 2025 cells 364989459 and 100392314 = -14,000,000. EIX's printed figure is (14) benefit (R2). SCE's own is +14 expense (R8 SCE block). Right to demote. Any automated cross-check here must compare signed values.
3. **Count mismatch, not checkable from filings.** The brief claims 1,771 facts. The module docstring at ec6277c says 1,772 (467 + 388 + 543 + 374 = 1,772). Reconcile from the dry-run log before applying. The cell count (600) and the one accession per subsidiary (4) match the plan file: 164 / 172 / 154 / 110 cells.
4. Some sampled parent values come from Details pages, not the face: ETR (Sempra R67), total_debt_split (CMS R56), SCE stockholders_equity and DPS (EIX R50/R51 Details). Each is still the parent's printed figure in the same accession.

## Requests and disk
SEC requests: 42 (8 index-headers/FilingSummary, 34 R pages). All went to sec.gov through `SecClient`, one process, 0.26 s minimum spacing. Downloads were in scratchpad/verify-demotion-dl and are deleted. Free disk on /private/tmp: about 12 GB throughout, above the 4 GB floor.

## Untested scope
- 580 of the 600 cells were not sampled. The supplementary screen covers 446 of them at DATA-INFERRED strength. 154 were not on the fetched pages (equity-statement balances, note-only items such as shares_outstanding cover dates, interest_income, net_lease_revenue, sbc, comprehensive income pages not fetched) and were not screened.
- The 1,771 / 1,772 core.fact demotions themselves (fact ids, is_authoritative flips) were not checked; that needs the DB.
- Not tested: rollback/restore_run, writing the blank reasons, the archive path, and whether other co-registrant companies (SDG&E 86521, the other 5 Entergy subsidiaries) have the same defect. Those companies are not in this plan.
- The flag-ON apply path was not run.
