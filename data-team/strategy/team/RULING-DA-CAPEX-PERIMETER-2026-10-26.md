# Ruling proposal: D&A and capex perimeter, 2026-10-26

Standardization lead. PROPOSAL ONLY: not in force until approved by an agent other than the author (preparer is not approver). Because this sets a metric definition, the approver should also decide whether it is a novel definition call that needs founder sign-off.

Source of all filing evidence: `data-team/strategy/team/VERIFY-DA-CAPEX-V3-2026-10-25.md` (Verifier 2, values checked on each accession's cash-flow R page). Its labels are kept. I did not reopen filings and did not read code for this ruling; anything I add beyond the verify file is marked ASSUMED or DOC-CITED.

## Definitions (proposed)

**Capex** = gross cash paid in the investing section of the cash-flow statement to acquire or build long-lived tangible assets the company owns and depreciates, plus capitalized internal-use and to-be-sold software, as printed on the face. It is the SUM of every printed line of that kind for the column. It does not net proceeds from disposals. It excludes business acquisitions, purchased intangibles (licenses, patents, customer lists), investments, and finance-lease principal payments (those sit in financing).

**D&A** = depreciation (of all owned PP&E, including equipment leased to others) plus amortization of intangible assets and of capitalized software, as printed in the operating adjustments of the cash-flow statement, summed over every printed line of that kind. It excludes amortization of debt costs or discounts, content/film cost amortization (consistent with NFLX 9M 2020 349,567K, FILING-CHECKED), contract-cost amortization, operating-lease ROU amortization, stock compensation, and impairments.

Rule for both: if a printed line's nature cannot be determined from its face label, the filing's notes must settle it before the cell is published. Until then the cell is unavailable with reason `perimeter_line_unresolved`, not published from the slot alone. No size threshold applies.

## 1. Capex questions

### 1a. Equipment leased to others (CAT): INCLUDE
- Reasoning: the leased equipment is CAT's own property, on its balance sheet and depreciated, so it is capital spending. Leaving it out makes FCF inconsistent with D&A, which includes depreciation of that same equipment (ASSUMED that CAT's printed D&A line covers it; confirm on the face). The narrow slot shows only the line the filer calls "excluding equipment leased to others", which by its own wording is a partial total.
- Example: CAT 9M 2016, 0000018230-16-000715 (FILING-CHECKED): "Capital expenditures - excluding equipment leased to others" 807 + "Expenditures for equipment leased to others" 1,393 = capex **2,200**. The slot currently publishes 807, which is wrong under this definition.
- CAT's own "ME&T free cash flow" is a segment measure. We report the consolidated total; a segment view is out of scope.
- Effect: every CAT capex cell that has the leasing line printed changes (2026 Q1 is named by the Verifier too). The count of cells is unknown. Other filers with a separate leased-equipment or rental-fleet line (equipment lessors, captive-finance manufacturers) need the same check; how many there are has not been measured.

### 1b. Capitalized software (MA, GE): INCLUDE
- Reasoning: internal-use software is a capitalized productive asset that is amortized through D&A, so it is capex in substance. Including it keeps FCF symmetric with D&A, which includes software amortization. Purchased intangibles stay excluded: AAPL 6M FY2015 capex is **5,586**, not the broad 5,741 that adds 155 of intangible purchases (FILING-CHECKED).
- Example: MA FY2024 (accession not given in the verify file; take it from the replay report): PP&E 474 + capitalized software 720 = capex **1,194** (FILING-CHECKED value, equals production). GE: the broad slot adds capitalized software in the same way (FILING-CHECKED per verify file; no accession given).
- Effect: MA and GE capex cells should come from the slot that includes software, not the narrow one. Production already holds 1,194 for MA FY2024, so this cell does not change. The count of other affected cells is unknown.

### 1c. Separate "Payments for (Proceeds from) Productive Assets" line beside PP&E (AMD): HIDE pending notes
- Reasoning: the face shows AMD's own capex line, "Purchases of property and equipment" (974), and a separate 38 under the standard element label, whose nature the face does not state (FILING-CHECKED). The element's standard meaning is a net capex TOTAL covering PP&E, software and intangibles, net of proceeds (ASSUMED, from taxonomy knowledge, not re-read). Here it is a sibling line, so its meaning is ambiguous: it could be software (include), intangibles (exclude) or a net figure (include only the gross part). Publishing 974 when the true value may be 1,012, or 1,012 when it may be 974, would show an unverified number either way.
- Ruling: AMD FY2025 capex (0000002488-26-000018) becomes unavailable, `perimeter_line_unresolved`, until someone reads the 10-K notes. If the notes show property or software spending, publish 1,012; otherwise publish 974. Any Q4 derived from FY minus 9M is hidden with it.
- General rule: a capex-class element (net_capex) that appears as a SIBLING of a PP&E purchase line, rather than as the section's capex total, must not be summed or dropped automatically. The replay should flag the cell. The number of such cells is unknown; the replay can count them.

## 2. D&A questions

### 2a. AMD FY2025: printed "Amortization" line
- Face (FILING-CHECKED): "Depreciation and amortization" 750 and "Amortization" 2,254. The narrow slot gives 750 because AdjustmentForAmortization is classed other_amort. The 9M 2025 narrow (2,253) does include intangible amortization, so the FY value and the 9M value come from different perimeters.
- Under the definition above, FY2025 D&A = 750 + 2,254 = **3,004**, if the 2,254 is intangible amortization. That is DATA-INFERRED only (its size matches the quarterly AmortizationOfIntangibleAssets facts). The face label is just "Amortization".
- Ruling: hide AMD FY2025 D&A (and any derived Q4) as `perimeter_line_unresolved` until the notes confirm the 2,254 is intangible amortization; then publish 3,004. Do not publish 750 under any reading, because it is known to be an understatement.
- General rule: AdjustmentForAmortization and other other_amort elements are generic. They count in D&A only when the face label or notes identify intangible or software amortization. Otherwise the cell is hidden with the reason above. A cell must never mix perimeters across periods (FY narrow without intangibles, 9M with them). The replay should check that the FY and 9M slot compositions match for the same company and fiscal year.

### 2b. Custom "Depreciation, amortization, and other" lines (CSCO, MSFT)
- Face (FILING-CHECKED): CSCO 6M FY2024 and MSFT 9M FY2025 print one custom combined line. The line includes unnamed "other" items, so it is not D&A and must never be published as D&A, even approximately.
- Ruling: the blank is correct. The reason changes from `not_a_face_column` (wrong) to `da_combined_with_other_items`, which is a structural reason only for cells where the face has been checked (these two). Other custom-member D&A cells not checked on the face get `needs_instance_reader`, as the Verifier proposed, and are not called structural.
- Allowed later route, not built: if the filing's notes give depreciation and intangible amortization for exactly the same period, D&A = their sum, with the note locator as lineage. That route needs its own verification before any value is published.

## 3. Metric consequences

The V1 list has 18 metrics (DOC-CITED: root CLAUDE.md / doc 02). From that list, as I understand it:
- **FCF** (= CFO minus capex) and **FCF Yield** (FCF / market cap) consume capex. They change for CAT (lower FCF: leased equipment now included), for MA/GE wherever a cell used the narrow slot without software (lower FCF), and are hidden for AMD FY2025 (and derived Q4) until the 38 is resolved.
- **D&A** is not an input to any of the 18 V1 metrics (DOC-CITED: EBITDA, Net Debt/EBITDA and EV/EBITDA are doc 18 Tier A / doc 26 Tier 3 and not on the locked list). So the D&A ruling changes only the displayed D&A line on the cash-flow statement, plus any EBITDA metric if one has been built since those docs. I did not check that in code.
- Hidden pending review (cell, its FCF and FCF Yield):
  1. AMD FY2025 capex and D&A (0000002488-26-000018) and their derived Q4 cells.
  2. Every cell with a net_capex sibling of a PP&E line, or an other_amort line whose label does not name intangibles or software.
  3. CAT capex cells (and FCF/FCF Yield) until the slot sums both printed lines. Until then the cell publishes 807-type partial values, which this ruling calls wrong.
  4. CSCO/MSFT combined-line D&A stays blank with the corrected reason.
- Counts: not measured. The Verifier's scale figures (277 D&A / 374 capex long-period `not_a_face_column` cells) concern the separate face-column bug, not this perimeter ruling.

## Untested scope / open items
- Not re-opened: CAT's D&A coverage of leased equipment; the AMD notes (38 and 2,254); GE accession; the MA FY2024 accession.
- Not checked in code: which mapper modules consume capex/D&A, and whether an EBITDA metric exists now.
- Population counts for every rule above: run the replay with the new perimeter flags (dry-run) and report the number of cells changed or hidden per company.
