---
id: slot-members-come-only-from-the-balance-sheet-statement-role
title: Slot members come ONLY from the balance-sheet statement role; five member-defect classes from the V2 verdict and their standing exclusions
kind: rule
tags: slot-records, total_debt, statement-role, securities-lending, intercompany, mixed-lease
paths: pipeline/scripts/slot_records/build_debt_slots.py @ 322d092 (branch work/scrooner-25/slot-records); data-team/strategy/team/VERIFY-SLOT-RECORDS-30SET-V2-2026-10-24.md
evidence: FILING-CHECKED
created: 2026-10-24
verified: 2026-10-24
---
Verifier verdict on the 30-set V2 (values 32/32 right, structure 8 records wrong) distilled to standing rules: (1) composition members come ONLY from calc arcs in the balance-sheet STATEMENT role (role name ~ balance sheet/financial position/condition) - note-role arcs injected MSFT/GOOG securities-lending payables (+62% GOOG 2015) and GE/AVGO/TSLA note-only lines that would double count or blank cells; aggregates may still be read role-wide as evidence. (2) DepositsReceivedForSecuritiesLoanedAtCarryingValue is a collateral payable, never a borrowing (Dhairya ruling under delegation, Std Lead to confirm). (3) Custom 'assumed by parent/sub' debt lines (GE Short/LongTermDebtAssumed) are intercompany eliminations: 0 in the consolidated column (0000040545-19-000014 R4) - read only the consolidated context. (4) A GENERIC lease-liability line (amzn LeaseLiabilityNoncurrent, LongTermLeaseLiabilities) mixes operating+finance leases: excluded/hold until the lease note splits it, never classed borrowing. (5) DueToRelatedParties* can be real debt (TSLA solar bonds ~100M): must be in the candidate net. (6) A blank face member must not hard-stop a cell when the filer's own printed debt aggregate confirms the sum (ABBV 2015-06-30 31,123M). All six live as regression fixtures (expected_membership/expected_values.json).
