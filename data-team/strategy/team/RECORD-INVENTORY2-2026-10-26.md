# Record: canonical concept `inventory@2` (face-slot rule) - 2026-10-26

Status: **APPROVED with edits R1-R3 (`APPROVAL-RECORD-INVENTORY2-2026-10-26.md`), edits applied 2026-10-26; nothing applied to data.** Preparer: Standardization Lead. I may not approve it; an approver other than me (and other than the Tag Mapper, who prepared the evidence) must. Sources: approval `APPROVAL-INVENTORY2-2026-10-26.md` (C1-C7, items a-d), evidence `INVENTORY-TAG-COEXISTENCE-2026-10-26.md` sections 2-5, parent `APPROVAL-RULINGS-2026-10-25.md` RUL-INV-1 (C1-C5), founder part-3 answer as relayed in the approval. Supersedes inventory@1 (= `us-gaap:InventoryNet` only, metric_definition 42 input). Rule type: **face-slot rule, never a global `concept_mapping` row** (no tag is added to `inventory` by tag alone).

## 1. Definition
`inventory` = the registrant's consolidated, current-asset inventory carried on the face of the period's own balance sheet: goods, materials, supplies, fuel and real estate held for sale or consumption in operations (ASC 330 scope plus filer-elected inventory elements), net of any LIFO or valuation reserve printed on the face. Instant, USD (reporting currency), dimension-free, sign positive. One value per (company, balance-sheet date).

## 2. Perimeter
**By face position (all required):** (P1) a line in the registrant's **own** statement block of the balance-sheet role, above that block's `AssetsCurrent` row (C2: co-registrant reports such as PEG R5 hold several blocks; read only the registrant's); (P2) current, not noncurrent; (P3) a nonzero instant fact at the cell's own date; (P4) the fact is `is_authoritative = true` and comes from the period's own filing (C1).
**By tag (members, face only):** InventoryNet; InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings; AirlineRelatedInventoryNet, AirlineRelatedInventory; PublicUtilitiesInventory; RetailRelatedInventoryMerchandise; EnergyRelatedInventory and children (OtherFossilFuel, NaturalGasInStorage, GasStoredUnderground, Coal, Chemicals); InventoryRawMaterialsAndSupplies(NetOfReserves); InventorySuppliesNetOfReserves; OtherInventorySupplies; InventoryPartsAndComponentsNetOfReserves; InventoryFinishedGoods(NetOfReserves); InventoryWorkInProcess(NetOfReserves) subject to the contract-asset guard (section 4); InventoryRawMaterials(NetOfReserves); combined WIP/raw/finished variants; OtherInventoryNetOfReserves; InventoryRealEstate (classified balance sheet only); InventoryGross and FIFOInventoryAmount: allowed as a single face line when no LIFO or valuation reserve line is printed on the face (RGLD "Stream inventory" 12,973K, CWST); when a reserve line is printed, used only net of it under R3 (KR FIFO 7,998 - LIFO reserve 1,291).

## 3. Rule steps (first match wins)
- **R1** a face `InventoryNet` line (P1-P4). Non-authoritative copies are never read (C1).
- **R2** else a face line printed "Total inventor..." (MKC, DHR carry it on InventoryGross).
- **R3** else the sum of the current face member sub-lines, minus a face `InventoryLIFOReserve` or valuation-reserve line (KR 2019-05-25: 7,998 - 1,291 = 6,707, foots CA 10,162, FILING-CHECKED by approver). A total is never added to its own parts.
- **Footing check (gate, not membership):** rule value + every other current face line of the block = printed `AssetsCurrent` within 2 units of printed precision. The pool must not add gross receivables, allowance and net receivables when all three are printed; use the net line only (C3, NI 0001111711-24-000011 R6).

## 4. Exclusions
- `us-gaap:MaterialsSuppliesAndOther` as a current face line (element text "not included in inventory"): not inventory; quick_ratio hidden (section 6). Noncurrent or note-only MaterialsSuppliesAndOther does not hide (UPS 2023-12-31).
- Noncurrent inventory (InventoryGasInStorageUndergroundNoncurrent, noncurrent ore/leach pads, line fill).
- **Contract-asset guard:** an inventory element whose same-filing value is also tagged as a contract-asset element, or whose own policy note describes it as costs/fees billable to clients, is not inventory (OMC, section 5). The note-text part applies only after someone has actually read that filer's note for the era and cited the accession and paragraph; a caption alone (e.g. "Work in process") never triggers it.
- Any nonzero custom (extension) current face line blocks auto-publication until its value is read from FSDS `num.txt` and the Verifier classifies it; caption matching is never used (C5, C6; PEG "Fuel" 329).
- Combined lines that mix quick items (existing COMBINED_LINE_ONLY).
- **Materials boundary by tag.** Inside: InventoryRawMaterialsAndSupplies(NetOfReserves), InventorySuppliesNetOfReserves, OtherInventorySupplies, InventoryPartsAndComponentsNetOfReserves, PublicUtilitiesInventory, EnergyRelatedInventory and children, whatever the caption (NI "Materials and supplies, at average cost" 172.1). Outside (hide): MaterialsSuppliesAndOther, and any custom or generic non-inventory element (e.g. OtherAssetsCurrent) whose current face caption reads materials and supplies. The boundary follows the filer's element choice.

## 5. OMC "Work in process"
Not inventory in any era. 2017-2019: same-filing ContractWithCustomerAssetGrossCurrent tag (approver, FILING-CHECKED/SEC-API). **2015-2016: policy note read (FILING-CHECKED, this record):** "Work in process includes costs incurred on behalf of clients in providing advertising and marketing services, including media and production costs, and fees that have not yet been billed. Media and production costs are billed during the production process and fees are normally billed within the next 30 days." Note 2 "Significant Accounting Policies", 10-K FY2016 0000029989-17-000004 (a201610-k.htm, sha256 fadb0fb5ae757ab4abc65c89a03e00564714858d7f6402debfc79a30bdb4a199) and identical text in 10-K FY2015 0000029989-16-000015 (a201510-k.htm, sha256 2ec4f3fe906a7b1f18d60bae4c92b09e1c14a7f7c3c87df856aaa82e2ca87b32). Neither 10-K uses the word "inventory". Face (R2, FY2016 10-K): Work in process 1,125.4 / 1,122.7 on `us-gaap:InventoryWorkInProcess`; 3,002.2 + 20.6 + 7,510.8 + 1,125.4 + 1,063.0 = 12,722.0 = Total Current Assets. Treatment: OMC cells keep the stored value (quick ratio = current ratio), un-hidden, all dates 2015-03 onward. The 2015-2016 quarter-end dates rely on the annual note bracketing them; the 10-Q notes were not read.

## 6. Publication conditions and reason codes
Publish a cell only if all hold: (a) strong footing; (b) every member tag is on the section 2 list and passes section 4; (c) the cell is in a passed Verifier random draw (40 cells, one per company, plus the 167 subset-footed utility cells sampled separately) (C7). Footing is necessary, not sufficient. Otherwise hide with:
Precedence when several apply (one reason per cell, first wins): `materials_supplies_line_present` > `inventory_fact_not_authoritative` > `inventory_statement_unavailable` > `inventory_presented_not_extracted` > `inventory_value_under_review`.
- `materials_supplies_line_present`: a current MaterialsSuppliesAndOther (or materials-captioned non-inventory) face line exists (approval item c; fixture CP 2017-03-31).
- `inventory_fact_not_authoritative`: the face inventory fact exists only as non-authoritative copies (147 cells / 85 companies; owner Data Engineer authority resolver).
- `inventory_statement_unavailable`: the period's own balance sheet for that date cannot be read (filing shows newer columns only, no readable pages).
- `inventory_presented_not_extracted`: the face shows an inventory line at the date and no rule step (R1-R3) yields any value.
- `inventory_value_under_review`: a rule step yields a value but it is not yet publishable. Page text: "the value is withheld until it is verified". The sub-cause (subset_footing, no_footing, unread_custom_line, draw_not_passed) goes in the evidence detail, not the reason code.
`inventory_like_tag_unmapped` is retired for these cells. A face with no inventory line keeps the stored value (13 cells CLH, SWX, OMC; Verifier spot-check CLH, SWX).

## 7. Downstream effect
- **quick_ratio:** formula unchanged, (CA - inventory) / CL (founder part-3 answer). Only the inventory input changes.
- **inventory_days and the inventory reconciliation:** move under inventory@2 for utilities, rails, airlines and retailers whose line is not InventoryNet. **Both stay gated by RUL-INV-1 C4** (IncreaseDecreaseInInventories perimeter, Tag Mapper, NOT_RUN) and must not consume inventory@2 until C4 passes. quick_ratio is not gated by C4.

## 8. Withdrawal conditions (any one suspends R2/R3 auto-publication)
1. A FILING-CHECKED face where the printed total differs from the rule value with no printed reserve line.
2. A face carrying a custom inventory-type line whose us-gaap tag sum still foots (would show the footing gate admits wrong values).
3. A Verifier draw finding any strong-footed published cell wrong.
4. A member tag found to be a contract asset or receivable at another filer (as OMC), until the guard is extended and the tag rechecked.
5. A published value drawn from a non-authoritative fact or a non-registrant block.

## Not tested by this record
OMC 2015-2016 10-Q notes; the 50 unread KR/AZO/XOM cells; DAL/MTDR custom lines; C4; companies outside the top-1000 cohort.
