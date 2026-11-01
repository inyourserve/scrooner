---
id: cash-flow-member-direction-trust-printed-signs-only-where-th
title: Cash-flow member direction: trust printed signs only where the filer's own section adds up with them
kind: rule
tags: capex, cash-flow, sign, fsn, slot-records
paths: 
evidence: DATA-INFERRED
status: active
created: 2026-10-31
verified: 2026-10-31

unmerged_paths: pipeline/scripts/slot_records/cf_da_capex_variants.py
---
Label rules for capex kept missing new inflow lines (customer advances, deposits utilized, reimbursements, '(purchase) sale ... net'). Structural rule that replaced them (v13, 2026-11-01): presented value = FSN num value x (-1 if pre.negating). If the investing lines' presented values sum to the filer's NetCashProvidedByUsedInInvestingActivities within its rounding unit (37,950 of 40,418 cohort cells), the printed signs are trusted and only outflows count. If exactly one member's flipped sign makes the section add up, that member was mis-printed (104 cells; INTC FY2021 NAND, where the R page dropped the parentheses the 10-K prints). Otherwise a positive value of a standard Payments* element is an outflow by definition, and any other member's direction holds the cell (13 cells). Companion for D&A: when the income statement prints a D&A line and the cash-flow composition is held or partial, the IS line is the value; a complete CF composition stays even if the IS differs (COGS D&A). Gotcha: a rounding-unit helper returns its cap for 0, so never compute a tie tolerance from a zero base.
