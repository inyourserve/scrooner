# Tag card: PaymentsToAcquirePropertyPlantAndEquipment (capex)

Written 2026-11-02 by the FSN expert. Family: capex. INDEX.md had "no card yet".

## Meaning
- **What it is:** cash outflow to acquire long-lived physical assets used in operations.
- **Period type:** duration.
- **Balance:** credit.
- **Sign:** stored positive; printed in parentheses (negated label).

## Who uses it
- On the CF face for 94 EDGAR names in our top-100 extract, 2009–2026 (4,074 lines; DI).
- Labels: "Capital expenditures" (812), "Purchases of property and equipment" (705), "Additions to property, plant and equipment" (366).
- MSFT: in all 54 in-scope filings, "Additions to property and equipment", the only capex line.
  - FY2026 115,948M, FY2025 64,551M (FSN; production agrees).
  - FILING-CHECKED: Q2 FY2026 10-Q 0001193125-26-027207 R6 prints 29,876 for the quarter.

## Misuse seen
- The FSN pilot (run 41490670432) has no capex rule for MSFT (`no_mapped_line`, 59 cells) while production has the right values.
- INDEX.md warns that it is not *total* capex where other capex lines exist (Air Lease); MSFT has none.
