# D&A and capex slot families: why the first gate failed and the member-level gate to build (scrooner-25, 2026-10-25)

Status: design, nothing proposed. Agreed with Dhairya: no draw is requested until a gate passes on the 36-company set.

## What was run
`assemble_family.py` + the rewritten `replay_family.py` (verdict from the filing, production informational only). Gate v1 = the filer's whole cash-flow section arithmetic on the same accession: sum of signed section roots = section total (operating for D&A, investing for capex).

| | D&A (128 records) | capex (112 records) |
|---|---|---|
| cells where the section ties (publishable) | 299 | 273 |
| hold: a section root has no value in the API | 1,258 | 1,425 |
| hold: section total absent for that (start, end) | 423 | 629 |
| needs instance reader (custom member) | 619 | 14 |
| hold: no statement-role section cal | 0 | 77 |
| hold: section gap | 68 | 217 |
| production agrees / differs on publishable cells | 190 / 33 | 261 / 5 |

## Why the whole-section gate is wrong for these families
1. The cash-flow section lists 15-30 lines; many are custom or dimension-only in practice, so a root value is missing in the API for most periods. The balance-sheet identity worked because its terms are four or five standard totals; a cash-flow section is not.
2. The API period grid for cash-flow lines is irregular (3-month facts derived or missing, YTD columns, 52/53-week ends), so the section total is often absent at the member's (start, end) even when the member exists.
3. For capex the investing section mixes acquisitions, investments and dispositions; its tie says nothing about whether the capex member's perimeter is right.

## Member-level gate (to build)
A D&A or capex cell is publishable when ONE of these holds on the same accession:
- **G1 printed total.** The face prints a single D&A line (`DepreciationDepletionAndAmortization` or the filer's equivalent root) and the member IS that line: no composition, no gate beyond the face-admission rules (zone = operating section; never an IS sub-line; never `AccumulatedDepreciation`).
- **G2 composition tie.** The face prints components (depreciation, amortization of intangibles, software amortization) and the filer's cal has a parent that sums exactly those components in the statement role: the parent's value (if tagged) or the component sum is published when the parent-children arithmetic ties for the children present. Missing child -> hold.
- **G3 note tie (D&A).** The PP&E note's depreciation expense plus the intangibles note's amortization expense (`Depreciation`, `AmortizationOfIntangibleAssets`) equals the face line within the rounding unit: a FLAG when it differs (definitional, e.g. depreciation inside cost of sales), never a hold.
- **capex perimeter rule.** Members are the investing-section payments lines in `family_config` classes (`ppe_capex`, `net_capex`, `software_capex`, `intangible_capex`); `net_capex` (payments net of proceeds) is a separate variant, never summed with gross lines; capitalized software is a variant (`plus_software`) per the Standardization card, never silently included (DDOG finding).
- **Period rule.** Cells exist only at the periods the filer reports (annual, YTD, or quarterly as tagged); no subtraction-derived quarters in this family (Period Engineer's domain).

## Fixtures to collect before any draw
From the shard findings: GOOG/MSFT/AVGO/ABBV/ORCL/TXN/GEV (no combined D&A tag; components), Kura (IS sub-line 14,046K vs 448K), CSCO (700M both years), ISRG/ACN/SCHW (company-specific D&A tags), VZ `PaymentsToAcquireOtherProductiveAssets`, COP custom capex, EOG `PaymentsToAcquireOilAndGasPropertyAndEquipment`, WELL REIT capital improvements (definition), FCX segment-only capex, DDOG capitalized software.

## Cost
Zero SEC requests for G1/G2 (cal files for the 36-company set exist in `fam_cal`, 192 boundaries); G3 reads note facts from the API. Instance reads only for custom D&A members after the gate passes.
