---
id: inventory-is-a-face-composition-materialssuppliesandother-is
title: Inventory is a face composition; MaterialsSuppliesAndOther is defined as not inventory but is not a quick asset
kind: lesson
tags: inventory, quick_ratio, materials-and-supplies, utilities
paths: data-team/strategy/team/RULING-INVENTORY-PERIMETER-2026-10-25.md
evidence: FILING-CHECKED
source: XOM 0000034088-26-000093 R5; CP 0000016875-17-000029 R4; LNT 0000352541-15-000022 R3; WEC 0000107815-17-000210 R4
created: 2026-10-25
verified: 2026-10-25
---
Only InventoryNet is mapped to inventory, but XOM, LNT and WEC present inventory as face sub-lines on EnergyRelatedInventory, InventoryPartsAndComponentsNetOfReserves, InventoryRawMaterialsAndSupplies and EnergyRelatedInventory*, with no InventoryNet fact. CP's 'Materials and supplies' is on MaterialsSuppliesAndOther, which FASB defines as outside inventory. Proposal: inventory = the face total, else the sum of the current face sub-lines; quick_ratio@2 also deducts materials_supplies_not_inventory. XOM quick 0.847 (0.883 without materials), CP 0.771, LNT 0.866, WEC 0.456, against stored current ratios.
