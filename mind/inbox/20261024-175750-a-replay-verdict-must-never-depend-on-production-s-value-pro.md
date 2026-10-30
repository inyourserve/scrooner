---
id: a-replay-verdict-must-never-depend-on-production-s-value-pro
title: A replay verdict must NEVER depend on production's value: production is the thing being replaced
kind: rule
tags: verification, replay, circularity, slot-records, blank-cells
paths: pipeline/scripts/slot_records/replay30.py (branch work/scrooner-25/slot-records); data-team/strategy/team/VERIFY-SLOT-RECORDS-30SET-V3-2026-10-24.md
evidence: FILING-CHECKED
created: 2026-10-24
verified: 2026-10-24
---
Verifier V3 defect 1 (2026-10-24): a replay rule accepted a missing member as a face blank whenever the slot sum equaled PRODUCTION's value - i.e. the value under test proved itself; 2 of 5 such cells were wrong in BOTH slot and production (GE 2015-12-31 slot 194,519M missing the custom non-recourse line 3,083M, face 197,602M, 0000040545-17-000010 R5; RPAY 2020-03-31 slot 5.5M vs face 246.5M - the custom long-term debt line was invisible to the API). Standing law: in any pipeline-replacement replay, the only admissible proofs are the filing itself (a genuinely blank/absent face cell, or the filer's own printed total tying) - never the system being replaced, and never a sibling system sharing its vocabulary (see the regex-gate lesson, same day). Corollary: a missing CUSTOM-tag member is never a blank - custom values don't reach the companyfacts API - it is a distinct 'needs_instance_reader' state. This is the third circularity found in this campaign (tag vocabulary 2026-10-17, regex line-gate earlier today, production-as-proof now): the general form is 'two artifacts that share an ancestor cannot verify each other.'
