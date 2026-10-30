# Approval of record inventory@2 (`RECORD-INVENTORY2-2026-10-26.md`) - 2026-10-26

Approver: Data Chief session (not the preparer, not the Tag Mapper). **Decision: APPROVE WITH CHANGES (R1-R3 below).** Nothing applied; no publication authority granted (dry-run, Verifier draw, Release Manager still required). **Novel founder calls: none.**

## Checks against my approval `APPROVAL-INVENTORY2-2026-10-26.md`
- C1 authority + own filing: implemented (P4, R1). C2 registrant block: implemented (P1). C3 receivable triple-count: implemented (footing check). C4 KR reserve: carried (R3).
- Custom-line block (C5/C6): implemented, FSDS `num.txt` read + Verifier classification, no caption matching. Footing as gate not membership (C7): implemented (section 6 "necessary, not sufficient").
- Boundary by tag (item b): implemented as approved, inside and outside lists match, noncurrent/note-only MaterialsSuppliesAndOther does not hide.
- Precedence (item c): `materials_supplies_line_present` first, fixture CP 2017-03-31: implemented. Item (d) `inventory_fact_not_authoritative`: implemented. Withdrawal conditions 1-5: adequate.
- **OMC (FILING-CHECKED by me today):** fetched 0000029989-17-000004 `a201610-k.htm`, sha256 fadb0fb5...a199 (matches the record). Note 2 "Work in Process": "costs incurred on behalf of clients in providing advertising and marketing services, including media and production costs, and fees that have not yet been billed ... normally billed within the next 30 days." The document contains zero occurrences of "inventor". Client billable costs, not inventory: treatment (stored value, un-hidden, 2015-03 onward) approved. Quarter-end dates between annual notes are DATA-INFERRED from bracketing notes with the same face tag; acceptable, label it so in the cell evidence.

## Required changes
- **R1 (the preparer's flagged choice): split the reason code.** `inventory_presented_not_extracted` is untruthful for most of the cells placed under it: a subset-footed, non-footing, unread-custom-line or not-yet-drawn cell HAS a candidate value; we withheld it, we did not fail to extract it. "Not extracted" also collides with the coverage meaning of `line_in_filing_not_extracted` (a pipeline gap). Use:
  - `inventory_value_under_review`: a rule value exists but is withheld (subset-footed, non-footing, unread custom line, Verifier draw not passed). Page text: "Inventory is shown on the filing; the value is withheld until it is verified."
  - `inventory_presented_not_extracted`: kept only where a face inventory line exists at the date and no rule step R1-R3 yields any value.
  - Store the sub-cause (subset_footed / not_footing / custom_line_unread / draw_pending) in the cell's evidence detail, not as more page codes, so the Verifier queue is splittable.
- **R2: InventoryGross contradiction.** Section 2 admits InventoryGross "only under R2/R3 and only net of a face reserve line", which excludes RGLD "Stream inventory" (single face line, no reserve, 12,973K), approved INCLUDE in item a3. Fix: InventoryGross (and FIFOInventoryAmount) is a member as a single current face line when no face reserve line is printed, and is netted against a face reserve line when one is.
- **R3: total precedence order.** State one order for all codes: `materials_supplies_line_present` > `inventory_fact_not_authoritative` > `inventory_statement_unavailable` > `inventory_presented_not_extracted` > `inventory_value_under_review`. Also: the section 4 note-text arm of the contract-asset guard applies only on a FILING-CHECKED note read, never on a caption.

Once R1-R3 are edited in, the record is approved without re-review by me; the Release Manager checks the three edits are present.
