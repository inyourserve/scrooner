# Exception Rule Register — design proposal v2 (2026-10-24)

Status: PROPOSAL v2, nothing built, no migration number claimed (doc 53 ledger: next free is 0110; 0098–0103 belong to the trains). Written by session scrooner-25 at the founder's direction; revised per Dhairya's feedback after reading the as-filed pilot (`team/AS-FILED-PILOT-2026-10-24.md`), the V2 design (`team/SCROONER-V2-DESIGN-PROPOSAL-2026-10-24.md`) and the open-sources study (`team/OPEN-SOURCES-FOR-COVERAGE-2026-10-24.md`). For Dhairya's merged plan; Data Engineer owns implementation; Standardization Lead and the human accountant own approval.

## v2 change summary (what Dhairya corrected)

v1 proposed a rule register *beside* the mapper. v2 makes it **THE company-wise mapper table** — the same object as the V2 design's `analytics.company_slot_record`, extended with the register's governance (evidence level, human approval, supersedes chain). One table, not two: a "rule" and a "slot record" were always the same thing seen from different ends. Eras are keyed to the **filing's taxonomy version**, not period dates — the Tag Expert's `InterestExpenseNonoperating` finding (exists only from the 2024 taxonomy; 1,542 companies affected; comparatives carry the new tag back to 2020-21) makes date-keyed eras structurally wrong. Re-verification runs in the **certification suite (I12)**, never in `resolve.py` — resolution stays a pure, fast read of approved rows.

## The table (one, in `analytics` — the V2 design's mapper table with governance columns)

```sql
create table analytics.company_slot_record (
    id                   bigint generated always as identity primary key,
    -- scope: company row (cohort), sector row (template), or global fallback row
    company_id           bigint references core.company(id),
    sector_code          text,
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    slot                 text not null,            -- e.g. 'total_debt.current_borrowings', 'revenue.total_line', 'interest_expense.face'
    rule_type            text not null check (rule_type in (
                           'tag_mapping',          -- v1: this tag feeds this slot
                           'slot_composition',     -- v1: member tags + weights under a calc parent (the hybrid's core: total debt, revenue total, D&A, capex, interest)
                           'not_applicable'        -- v1: evidenced N/A, feeds the single 'Not disclosed' state
                           -- later kinds (NOT v1): sign, scale, period_basis, tag_exclusion
                         )),
    member_tags          jsonb,                    -- slot_composition: [{concept_id, weight, calc_parent}] from the filer's own _cal.xml / FSN cal
    taxonomy_era_from    text,                     -- us-gaap taxonomy version of the first filing this applies to (e.g. '2024'); null = all eras
    taxonomy_era_to      text,                     -- null = current
    fingerprint_hash     text,                     -- the format-change gate's fingerprint this record was verified against
    evidence_accession   text not null,            -- REQUIRED: the filing(s) this was read from
    evidence_level       text not null check (evidence_level in ('FILING-CHECKED','DATA-INFERRED')),
    source               text not null,            -- shard id / tag card / verifier report / pilot cell #
    status               text not null default 'proposed'
                         check (status in ('proposed','verified','retired')),
    approved_by          text,                     -- FOUNDER DECISION 2026-10-24: no human accountant; approver is the founder or a designated independent approver agent, and must differ from created_by (preparer never approves own work).
    approved_at          timestamptz,
    review_note          text,                     -- one line in the approver's own words
    supersedes_id        bigint references analytics.company_slot_record(id),
    created_by           text not null,
    created_at           timestamptz not null default now(),
    check (approved_by is not null or status <> 'verified'),
    check (num_nonnulls(company_id, sector_code) <= 1)
);
```

v1 scope (per Dhairya): `tag_mapping`, `slot_composition`, `not_applicable` only. Slot records first for the five families the pilot proved: **total debt, revenue total, D&A, capex, interest** (V2 build-order step 2, replaying the 16 known-wrong cells as the regression set).

## Enforcement

1. **Resolution** (`mapper/resolve.py`): company record → sector record → global `concept_mapping`. Only `status='verified'` rows fire; `proposed` rows are triage-visible and change nothing. Era match is by the filing's taxonomy version. This is the one value-changing path → doc 49's 10-step procedure.
2. **Re-verification lives in certification (new I12), not resolve:** for each company being certified, every verified record is re-checked against the latest filing's fingerprint (presentation + calc tree). Fingerprint moved → the affected slots go to a visible hold ("format changed, under review" — the V2 design's gate), never silently stale. Same FILING-CHECKED bar as I1–I11; never Frames (2026-10-18 lesson).
3. **Coverage:** `not_applicable` records are the evidence rows behind reasoned blanks; the reasonless-blank counter burns down through this table. The open-sources study's residue verdicts (collaborative revenue = applicability for 647 companies, cf_ap_change = combined-line for 244, …) become seed `not_applicable`/`slot_composition` rows with their FSDS/FSN evidence.
4. **Backfill, don't re-derive:** seed `proposed` rows from `canonical_fact_sanity_override` (collapse per-period rows into per-era records), company-quirks.md, fix-register, tag-card exception lines, shard digests, and the pilot's 16-cell table. Original evidence strings kept.
5. **Provenance:** values resolved via a company record carry the record id in lineage → "this number uses a company-specific rule, approved by <reviewer>, from <accession>" (strategy doc 37 D1).

## What this is NOT

- Not a second table beside `company_slot_record` — it IS that table; this doc contributes the governance columns (evidence_level, approved_by/review_note, supersedes chain, the human-signature check constraint) and the backfill plan.
- Not a v1 home for sign/scale/period-basis/split rules — those stay where they are (split_event, sanity layer) until the slot core is proven on the 30-company set.
- Not self-approving — `approved_by` is structural and must differ from `created_by`. Founder direction 2026-10-24: approval is all-agent (independent approver agent distinct from the preparer, FILING-CHECKED evidence mandatory), with the founder as final approver only for genuinely novel accounting-definition calls. The earlier human-accountant plan (ACCOUNTING-REVIEWER-BRIEF-2026-10-24.md) is superseded by this direction.

## Open items for the merged plan

1. Migration number: claim 0110 (or next free) in the doc 53 ledger at build time, not before.
2. Whether `concept_mapping`'s global rows eventually migrate in as global-scope records, or stay separate as the non-cohort fallback (V2 design says: stay, as fallback outside the cohort).
3. Fingerprint definition ownership (Data Engineer) and where the gate's RSS trigger lands (V2 step 3).
4. Whether `review_note` is required (recommended) or optional on approval.
