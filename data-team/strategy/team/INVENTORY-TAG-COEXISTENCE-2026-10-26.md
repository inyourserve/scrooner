# Inventory tag coexistence check and recompute impact (RUL-INV-1 precondition C3), 2026-10-26

Role: Tag Mapper. Status: **PROPOSAL, read-only**. Nothing was mapped, written or applied. I do not approve this proposal; the approver agent and the Verifier must review it. Ruling being served: RUL-INV-1 in `data-team/strategy/team/APPROVAL-RULINGS-2026-10-25.md` (conditions C1-C5), proposal in `RULING-INVENTORY-PERIMETER-2026-10-25.md`.

Evidence labels: FILING-CHECKED (SEC R page opened, locator cited), DATA-INFERRED (our tables or FSDS presentation rows, no filing page opened), ASSUMED.

## 0. Scope and method (what was actually run)
- **Hidden cells**: the dry-run list of `quick_ratio` cells with reason `incomplete:inventory_like_tag_unmapped` from branch `work/data-engineer/quick-ratio-fix` f4d33bf (planner output `qr4_all.json`): 6,796 cells at 595 companies. Cohort v1.1 (`data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv`, 1,000 companies): **2,992 cells at 168 companies; 2,217 of them dated 2015-01-01 or later** (the I11 window). Every one of these cells today stores the current ratio, because no `inventory` canonical fact exists at the date. (DATA-INFERRED)
- **Facts**: `core.fact` instant, us-gaap, tags matching `%nventor%` or `%MaterialsSupplies%`, for all 1,000 cohort companies since 2014-01-01 (254,701 rows), plus the footing tags (cash, short-term investments, receivables, prepaid, other) for the 168 companies. One read-only connection (`default_transaction_read_only=on`, `statement_timeout` 60-100 s), chunks of 10-20 companies, no peer job active at start (pg_stat_activity: 19 sessions, none active). `core.fact` is built from the Company Facts API, which strips dimensional facts, so every row is dimension-free by construction (doc 22, CLAUDE.md); custom (extension) tags are absent from it.
- **Face vs note**: FSDS `pre` balance-sheet rows kept locally (`fsds_work/cohort_bs_rows_all.jsonl`, 1,399,274 rows, periods 2014-2026). A tag is a "face line" when it sits in the period's own 10-K/10-Q balance-sheet report **above the `AssetsCurrent` row** (C2: current, above total current assets, by position). FSDS `period` is month-rounded, so 52/53-week filers (KR, AZO, GAP, DLTR, ULTA, SYY...) were matched to the nearest month end within 10 days. The local `num.txt` files are not present; only `pre` rows and a dimensional-fact extract are, so custom-line values could not be read.
- **Footing test** (my own, DATA-INFERRED): for each cell I apply the proposed rule to get an inventory value S, then require S plus every other non-custom current face line (values from `core.fact` at the cell date, from the period's own filing when present) to reproduce the filer's `AssetsCurrent` within rounding (2 units of the total's printed precision). "Strong" = all other face lines sum to CA - S. "Subset" = only some subset of them does (weaker; spurious matches possible). "Uncheckable" = the face carries a custom-tag line, whose value is not in `core.fact`.
- **SEC pages**: 18 R pages opened (budget 20), all FILING-CHECKED, listed in section 6.
- Query/script text: `/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/inv/` (fetch1.py, fetch2.py, fetch3.py, an1.py, an4.py, an5.py; outputs cell_outcomes5.json). Source cutoff: database read 2026-10-26; planner dry-run f4d33bf (2026-10-26 01:50 IST).

## 1. Result in one table: recompute impact on the 2,992 hidden cohort cells
Rule used (section 4): R1 face `InventoryNet`; else R2 a printed "Total inventor..." face line; else R3 sum of the current face inventory sub-lines, minus a face `InventoryLIFOReserve` line. `MaterialsSuppliesAndOther` and custom inventory lines are never part of the sum.

| Outcome | Cells, all years | Cells since 2015 | Companies (since 2015) | What it means |
|---|---|---|---|---|
| **Value recomputable, strong footing** | 1,274 | **1,263** | 110 | Rule value + all other face lines = CA. Cell gets (CA - inventory) / CL. R1 124, R2 44, R3 1,095 (since 2015). DATA-INFERRED; 8 of 8 sampled strong-footed filings agree (AAL, GAP, SYY, VFC, MKC, DHR, LNT, CWST; section 6) |
| Value recomputable, subset footing only | 170 | 167 | 11 | Utilities (NFG 45, AWK 43, ATO 35, WTRG 24, EXC 9, WEC 5). Needs a Verifier sample before use. ATO sample FILING-CHECKED right |
| Face has a custom-tag line, value unreadable | 429 | 424 | 34 | IMO, PEG, NI, PNW, FCX, RGLD, BA, KR, CEG... Keep hidden until the custom line's value is read from FSDS num or the instance. PEG proves tag-only sums are wrong here (custom "Fuel" 329 is inventory, section 6) |
| Rule value does not foot | 28 | 28 | 8 | MPLX 19, PNW 2, DUK 2... Three samples (PNW, DUK, MPLX) show the rule VALUE is right; the failure is my footing pool (negative allowance lines, related-party lines). Keep hidden |
| Face has a current `MaterialsSuppliesAndOther` line | 177 | 177 | 6 | UNP, NSC, CP, CSX and two more. **Stay hidden** by the ruling, reason `materials_supplies_line_present` (the branch calls the cells `inventory_like_tag_unmapped`; the reason text should change) |
| Custom inventory face line | 52 | 52 | 3 | NEM 43 ("Inventories" and "Stockpiles and ore on leach pads" are two custom-tag lines), DAL 8, MTDR 1. Cannot be summed from `core.fact` |
| Face tag has no fact at the date | 43 | 43 | 3 | EXC 33, CNP 9, EVRG 1 (EXC prints "Inventories, net" with 2 sub-lines, FILING-CHECKED; the sub-line facts are missing in `core.fact`) |
| Face shows no inventory line at all | 14 | 13 | 3 | CLH 5, SWX 5, OMC 3: a note fact exists but the face has none; inventory = 0 is right, the stored current ratio is right, **these cells should not be hidden** (DATA-INFERRED) |
| Statement not read (no FSDS rows) | 805 | 50 | 23 | 755 are before 2015. Since 2015: KR 14, AZO 14, XOM 2 (successor CIK), NKE, DAL, DDS, OMC, GAP, GE, MKC, PFE, SYY, UAL, PEG 1 each. Not investigated |
| **Total** | **2,992** | **2,217** | 168 (all years) | |

**Answer to the question: 1,263 of 2,217 in-window hidden cohort cells (57.0%) get a true value on the strong rule alone; up to 1,430 (64.5%) after the 167 subset-footed cells pass a Verifier sample. 787 stay hidden, each with a named cause above.** For all years including pre-2015: 1,274 strong (42.6% of 2,992).

**Defect found that is not a mapping problem.** 147 of the in-window hidden cells (124 are fiscal-year-end dates; 85 companies) already have an `InventoryNet` fact in `core.fact` at that date, but every copy of it is `is_authoritative = false`, so no `inventory` canonical fact exists. Examples: DHR 2015-12-31 (3,442M in three filings, recast to 2,284M later), VFC 2018-06-30 (1,993,825K, FILING-CHECKED right), AAL-type year ends. Mapping a tag will not fix these; the authority resolver does. Route to Period Engineer / Data Engineer. About half of all cohort `InventoryNet` facts (23,866 of 48,514) are non-authoritative, which is normal for repeated copies, but at these 147 cells no copy was promoted.

## 2. Per-tag table: face line vs note-only (hidden cohort cells since 2015; 168 companies)
"Face cells/cos" = cells where the tag has a fact at the date and is a current face line of that period's balance sheet. "Note cells/cos" = the fact exists at the date but the tag is not on that face. (DATA-INFERRED)

| Candidate tag | Face cells | Face cos | Note-only cells | Note cos | Role seen |
|---|---|---|---|---|---|
| InventoryNet | 144 | 85 | 3 | 3 | printed total (R1); facts non-authoritative (see above) |
| InventoryRawMaterialsAndSupplies | 351 | 12 | 49 | 12 | utilities' "Materials and supplies" face line (PEG, AWK, NI, DTE, CNP, WTRG, NFG, EXC, LNT); note component elsewhere |
| InventoryPartsAndComponentsNetOfReserves | 0 | 0 | 4 | 3 | never a face line in the cohort; note only |
| EnergyRelatedInventory | 124 | 4 | 4 | 3 | WEC "Materials, supplies, and inventories", EVRG, DTE |
| EnergyRelatedInventoryOtherFossilFuel | 148 | 4 | 62 | 4 | utility fuel line (PNW, IDA, LNT) |
| EnergyRelatedInventoryNaturalGasInStorage | 154 | 5 | 50 | 3 | utility gas line (CNP, NI, WTRG, EXC) |
| EnergyRelatedInventoryGasStoredUnderground | 135 | 4 | 0 | 0 | ATO, LNT, NFG, DTE face line (name in the brief `InventoryGasStoredUndergroundCurrent` does not exist in our concept table; `InventoryGasInStorageUndergroundNoncurrent` exists and must stay out) |
| PublicUtilitiesInventory | 47 | 2 | 0 | 0 | DUK, CNP single "Inventory" line (also dimensional by legal entity in FSDS; core.fact holds the consolidated one) |
| OtherInventorySupplies | 137 | 7 | 10 | 9 | PNW, IDA, HL, KNX face line |
| InventoryFinishedGoods | 143 | 8 | 123 | 36 | face single line (ULTA, DLTR-type) or component under a total |
| InventoryFinishedGoodsNetOfReserves | 191 | 7 | 123 | 52 | single-line face total at GAP, NKE, AZO, SYY, LULU; component elsewhere |
| MaterialsSuppliesAndOther | 177 | 6 | 18 | 7 | separate face line (UNP, NSC, CP, CSX); excluded by the ruling |
| Tags that carry the face total but were not in the brief | | | | | |
| InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings | 149 | 5 | 0 | 0 | BA, LMT, HII, NOC, KTOS "Inventories" (alternate total tag; equals InventoryNet at 80 of 111 pairs) |
| AirlineRelatedInventoryNet / AirlineRelatedInventory | 125 / 45 | 3 / 1 | 4 / 1 | | AAL, UAL, LUV |
| RetailRelatedInventoryMerchandise | 84 | 2 | 2 | 2 | DLTR, DDS |
| InventoryGross | 176 | 6 | 35 | 17 | single face line (CWST, RGLD, MPLX) or printed "Total inventor.." with sub-lines (MKC, DHR) |
| FIFOInventoryAmount | 32 | 1 | 22 | 7 | KR; needs the face `InventoryLIFOReserve` line subtracted |
| OtherInventoryNetOfReserves, InventoryWorkInProcessAndRawMaterialsNetOfReserves, InventoryRealEstate | 45, 44, 16 | 1 each | | | MTDR, EME, Z |
| InventoryWorkInProcess | 33 | 4 | 89 | 27 | includes OMC's agency "Work in process" (19 cells, strong footing; semantic call, section 5) |

## 3. Coexistence with InventoryNet (double-count risk), all 1,000 cohort companies, dates since 2015
Pairs = (company, date) where both the tag and InventoryNet have a fact (any filing, any authority). `lt` = tag value below InventoryNet (consistent with a component). "Both on face" = in the period's own balance sheet both are current face lines (a sub-line printed under a total). (DATA-INFERRED, FSDS presentation rows)

| Tag | Companies | Pairs | eq | lt | gt | Both on face (pairs / cos) | Reading |
|---|---|---|---|---|---|---|---|
| InventoryFinishedGoodsNetOfReserves | 286 | 9,510 | 33 | 9,460 | 17 | 603 / 24 | component; **double count if mapped by tag** |
| InventoryWorkInProcessNetOfReserves | 241 | 8,028 | 6 | 7,973 | 49 | 531 / 21 | component |
| InventoryRawMaterialsNetOfReserves | 210 | 6,862 | 6 | 6,834 | 22 | 379 / 17 | component |
| InventoryFinishedGoods | 182 | 4,825 | 12 | 4,754 | 59 | 194 / 12 | component |
| InventoryRawMaterialsAndSupplies | 67 | 1,659 | 2 | 1,600 | 57 | 126 / 6 | component under a total at some filers, face line at others |
| InventoryRawMaterialsAndSuppliesNetOfReserves | 57 | 1,670 | 0 | 1,657 | 13 | 166 / 6 | same |
| OtherInventorySupplies | 32 | 781 | 0 | 735 | 46 | 117 / 5 | same |
| InventoryPartsAndComponentsNetOfReserves | 14 | 369 | 0 | 369 | 0 | 0 / 0 | note component, never beside InventoryNet on a face |
| EnergyRelatedInventory | 8 | 40 | 0 | 40 | 0 | 8 / 1 | component at one filer, total at WEC |
| EnergyRelatedInventoryNaturalGasInStorage | 10 | 114 | 0 | 114 | 0 | 0 / 0 | note component where a total exists |
| PublicUtilitiesInventory | 6 | 38 | 37 | 0 | 1 | 1 / 1 | alternate tag for the same total (equal at 37 of 38) |
| AirlineRelatedInventoryNet | 4 | 10 | 9 | 0 | 1 | 0 / 0 | alternate tag for the same total |
| InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings | 8 | 111 | 80 | 30 | 1 | 0 / 0 | alternate tag for the same total |
| InventoryGross | 74 | 1,856 | 261 | 85 | 1,510 | 0 / 0 | note gross figure (above the net total at 1,510 pairs); a face line only when the filer has no reserve line |
| FIFOInventoryAmount | 28 | 583 | 7 | 97 | 479 | 0 / 0 | gross before LIFO reserve, above net at 479 pairs |
| MaterialsSuppliesAndOther | 12 | 77 | 1 | 50 | 26 | 37 / 2 | separate face line beside inventories; 26 pairs exceed InventoryNet, so it is not a component |

Consequence (DATA-INFERRED): **no tag in the list can be added to `inventory` by tag alone.** Every sub-line tag (FinishedGoods*, WorkInProcess*, RawMaterials*, OtherInventorySupplies, InventoryRawMaterialsAndSupplies*) is a component under a printed total at 5-24 cohort companies and a stand-alone face total at others. Only the face tells which. The alternate-total tags (PublicUtilitiesInventory, AirlineRelatedInventoryNet, InventoryNetOfAllowances...) are equal to InventoryNet where both exist, so they are safe synonyms only when no InventoryNet is on the same face.

## 4. Proposed mapping rule (proposal; not approved by me)
**Rule INV@2-face (company-and-filing scope, from the period's own balance-sheet presentation; this is a slot rule, not a global tag-to-concept row).**
1. Members: non-custom us-gaap inventory elements that are current face lines of the period's own balance sheet (above total current assets, by report order), with a dimension-free instant fact at the cell date. Admitted member tags (face only): InventoryNet; InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings; AirlineRelatedInventoryNet and AirlineRelatedInventory; PublicUtilitiesInventory; RetailRelatedInventoryMerchandise; EnergyRelatedInventory and its children (OtherFossilFuel, NaturalGasInStorage, GasStoredUnderground, Coal, Chemicals); InventoryRawMaterialsAndSupplies(NetOfReserves); OtherInventorySupplies; InventorySuppliesNetOfReserves; InventoryFinishedGoods(NetOfReserves); InventoryWorkInProcess(NetOfReserves); InventoryRawMaterials(NetOfReserves); combined WIP/raw/finished variants; OtherInventoryNetOfReserves; InventoryGross and FIFOInventoryAmount only under rules 3-4; InventoryRealEstate only on a classified balance sheet.
2. Precedence: (R1) a face `InventoryNet` line; (R2) else a face line labelled "Total inventor..." (MKC, DHR carry it on InventoryGross); (R3) else the sum of the face sub-lines. A total is never added to its own parts. This matches RUL-INV-1 part 2.
3. Net of reserves: a face `InventoryLIFOReserve` (or valuation-reserve) line is subtracted (KR: FIFO 7,998 - LIFO reserve 1,291 = 6,707, FILING-CHECKED). `InventoryGross`/`FIFOInventoryAmount` are accepted only when no reserve line is on the face (CWST, RGLD, MPLX single lines: none seen).
4. Exclusions: `MaterialsSuppliesAndOther` (stays out, quick ratio hidden with `materials_supplies_line_present`); noncurrent inventory (`InventoryGasInStorageUndergroundNoncurrent`, ore on leach pads noncurrent); any face with a custom-tag inventory-type line (NEM, DAL, MTDR, PEG "Fuel") until its value is read; a combined line mixing quick items (existing COMBINED_LINE_ONLY).
5. Publication gate: auto-publish only when the footing is strong (face lines other than inventory plus the rule value reproduce the current-assets total within rounding). Subset-footed, uncheckable and non-footing cells stay hidden with a specific reason until the Verifier samples them.
6. Era scope: none needed by date in the data (strong cells are spread 92-122 per year, 2015-2026). Scope by company and filing; the face fingerprint changes when a filer changes its presentation, which is the A11 format-change gate's job.
7. Version: `inventory@2`. inventory_days moves for utilities, rails, airlines and retailers whose single line is not tagged InventoryNet (GAP, NKE, AZO, SYY, KR, DLTR, AAL, BA...). IncreaseDecreaseInInventories perimeter (C4) was **not checked** here.

**What would make me withdraw rule 2/3**: one FILING-CHECKED face where the printed total differs from the rule value without a printed reserve line; a face that carries a custom inventory-type line whose tag sum still foots; or a Verifier draw showing a strong-footed cell wrong.

## 5. Open points for the approver (not decided by me)
- OMC prints "Work in process" (agency costs billed to clients, tagged InventoryWorkInProcess; 19 strong-footed cells). Z prints "Inventory" of homes (InventoryRealEstate, 16 cells). RGLD "Stream inventory". The tag says inventory; the economics may not be merchandise. Include by tag, or exclude as non-quick-ratio inventory? (Founder or Standardization call.)
- Utilities' "Materials and supplies" lines tagged `InventoryRawMaterialsAndSupplies` (PEG, AWK, NI, DTE, CNP, WTRG, NFG, EXC, LNT; about 450 cells) are inventory elements by tag and count under RUL-INV-1 part 2. The founder's part 3 hides only `MaterialsSuppliesAndOther` lines. The branch's `materials_supplies_reason` already treats inventory-named supplies as inventory. Confirm this is the intended boundary, since economically they are the same item as CP's materials and supplies.
- The 13 cells with no inventory line on the face (CLH, SWX, OMC) are over-hidden today; the branch rule should not hide them.
- 147 cells need an authority fix, not a mapping (section 1).

## 6. Filing evidence (FILING-CHECKED; each R page opened 2026-10-26)
| Company, date | Accession, locator | Face fact | Rule value | Agrees |
|---|---|---|---|---|
| AAL 2019-09-30 | 0000006201-19-000067 R4 | Aircraft fuel, spare parts and supplies, net 1,800 (AirlineRelatedInventoryNet); CA 9,572 | 1,800 | yes |
| GAP 2016-10-29 | 0000039911-16-000388 R2 | Merchandise inventory 2,398 (InventoryFinishedGoodsNetOfReserves, single line); CA 4,671 | 2,398 | yes |
| SYY 2018-09-29 | 0000096021-18-000178 R2 | Inventories, net 3,354,458K; CA 8,642,256K | 3,354,458 | yes |
| VFC 2018-06-30 | 0000103379-18-000009 R2 | Inventories 1,993,825K (InventoryNet fact non-authoritative in DB) | 1,993,825 | yes |
| MKC 2020-05-31 | 0000063754-20-000119 R4 | Finished 381.9 + raw/WIP 449.4; "Total inventory" 831.3; CA 1,615.7 | 831.3 (R2; summing sub-lines plus total would give 1,662.6 > CA) | yes |
| DHR 2020-10-02 | 0000313616-20-000142 R2 | FG 1,318.6, WIP 392.9, RM 710.2, "Total inventories" 2,421.7 | 2,421.7 (R2) | yes |
| LNT 2017-06-30 | 0000352541-17-000081 R3 | Fuel 84.7 + gas 22.2 + M&S 94.7; CA 814.7 | 201.6 (R3) | yes |
| ATO 2024-12-31 | 0000731802-25-000006 R2 | Gas stored underground 153,034K; CA 1,828,127K | 153,034 | yes |
| CWST 2019-03-31 | 0000911177-19-000026 R2 | Inventory 6,793K (InventoryGross, single line, no reserve line) | 6,793 | yes |
| KR 2019-05-25 | 0001558370-19-005961 R5 | FIFO inventory 7,998; LIFO reserve (1,291); no total line; also custom "Store deposits in-transit" | 6,707 (R3 less reserve) | yes |
| BA 2021-09-30 | 0000012927-21-000094 R4 | Inventories 81,897 (InventoryNetOfAllowances...); CA 116,888 | 81,897 | yes |
| PNW 2016-03-31 | 0000764622-16-000107 R5 | M&S 234,179 + fossil fuel 44,227 | 278,406 | yes (my footing failed: negative allowance line) |
| DUK 2023-03-31 | 0001326160-23-000148 R5 | Inventory 3,865 (PublicUtilitiesInventory) | 3,865 | yes (footing failed on my pool) |
| MPLX 2025-06-30 | 0001552000-25-000026 R4 | Inventories 192 | 192 | yes (footing failed on my pool) |
| AWK 2015-06-30 | 0001564590-15-006249 R2 | Materials and supplies 38,332K; the only inventory-type current line | 38,332 | yes; flagged "uncheckable" only because PP&E custom lines print above the current section |
| PEG 2018-09-30 | 0000788784-18-000026 R5 | Fuel 329 (custom tag) + Materials and Supplies, net 590 | tag sum 590 is **wrong** (true 919) | **no: shows the custom-line exclusion is needed** |
| EXC 2019-03-31 | 0001628280-19-005692 R4 | Inventories, net: fossil fuel and emission allowances 179, M&S 1,380 (no total line) | needs sub-line facts missing in core.fact | blocked |
| NEM 2020-09-30 | 0001164727-20-000228 R7 | Inventories 983 and Stockpiles and ore on leach pads 805, separate custom-tag lines | not recomputable from core.fact | blocked |

## 7. Not done / untested scope
- The 6,796-cell population outside the cohort (595 companies) was not analysed; cohort only.
- IncreaseDecreaseInInventories perimeter (C4): not checked.
- Custom-line values (utilities, NEM, FCX, IMO, BA, KR, RGLD: 424 cells) need FSDS `num.txt` or the instance documents; not available locally.
- 50 in-window cells at KR/AZO/XOM and others had no matching FSDS rows after month-rounding; reason not investigated.
- The strong footing is a DATA-INFERRED test and the 8 strong samples are a convenience sample (chosen by company type), not a random draw; the Verifier's random draw is still required before any value is shown.
- Pre-2015 cells (775) were counted but not examined.

## 8. Next action
Approver: rule 1-5 and the open points in section 5. Then Standardization Lead writes the `inventory@2` record, Data Engineer wires the face-slot rule into the quick_ratio branch (stop labelling these cells `inventory_like_tag_unmapped`; add the footing gate), Verifier draws random strong-footed cells (suggest 40, one per company) and the 167 subset-footed cells.
