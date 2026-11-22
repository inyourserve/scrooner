---
id: fsn-num-puts-legalentityaxis-members-in-coreg-not-dimh-a-cor
title: FSN num puts LegalEntityAxis members in coreg, not dimh: a coreg='' filter hides subsidiary copies from a member-duplicate guard
kind: gotcha
evidence: DATA-INFERRED
status: active
created: 2026-11-01
verified: 2026-11-01
---
GE FY2016 10-K 0000040545-17-000010: each undimensioned qtrs=1 Revenues row (e.g. 2016-12-31 = 2,649M) has a twin with coreg='SubsidiariesGecc' (dimh shows LegalEntity=SubsidiariesGecc too) and the same value. Any guard that compares an undimensioned value against member values must read rows with coreg<>'' as members; selecting only coreg='' (the usual face filter) silently drops them. Also: 10-K FY values repeat across iprx 0/1/2; filter iprx=0. Fix and test: work/engineering/fsn-store 0efe166 (fsn_store/select.py build(), test_ge_member_duplicate_alone_rejects_a_note_quarter).
