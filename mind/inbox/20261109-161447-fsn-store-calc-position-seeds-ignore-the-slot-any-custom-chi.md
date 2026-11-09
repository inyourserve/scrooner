---
id: fsn-store-calc-position-seeds-ignore-the-slot-any-custom-chi
title: FSN store calc_position seeds ignore the slot: any custom child of LiabilitiesCurrent maps as total_debt
kind: gotcha
tags: fsn-store, total-debt, mapping, seeds
paths: pipeline/src/scrooner_pipeline/fsn_store/mapping.py, data-team/47-fsn-store/concept_rules/bs.jsonl
evidence: CODE-CHECKED
created: 2026-11-09
verified: 2026-11-09
---
mapping.map_filing rule 2 (calc_position) runs only for CUSTOM tags and never tests position.slot. So bs.debt_member_parent@1 maps every custom child of LiabilitiesCurrent as total_debt_resolved; standard LongTermDebt*/CommercialPaper/FinanceLeaseLiability stay unmapped; select never sums. Prod fsn.line_map 2026-11-09: 7,335 lines/5,441 filings/236 cos, 4,027 single-line filings (e.g. 'Accounts payable and accrued liabilities'). bs.liab_cal_child@1 likewise maps custom children of Liabilities as the total -> false conflicting_values_in_filing blanks (4,479 filings). Capex/D&A are safe only because detectors.capex_da_detector overrides seeded lines. See FAMILY-RELEASE-CASE-2026-11-09.md (branch work/release/family-release-case-2026-11-09).
