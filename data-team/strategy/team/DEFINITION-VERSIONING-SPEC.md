# Definition versioning spec (WO-5 deliverable 1, Standardization Lead, 2026-10-22)

Status: **PROPOSED design, not built, not applied.** No code, no DB writes, no commits in this run. It is the Gate A precondition for any history backfill (doc 49 section 4, Gate A; section 7.4 row 0.3, Dhairya's ruling). Builder: Data Engineer (lane 1 or 2, Data Chief assigns). Reviewers: Engineering Head (schema, capacity) and Period Engineer (Q4 and history sections). I do not approve my own design.

Evidence labels: **CODE-READ** (what the repository does today; not financial evidence), **MEASURED** (catalog query run in this session, section 12), **DATA-INFERRED**, **ASSUMED**. Nothing here is FILING-CHECKED and nothing needs to be: this is engineering of the definition record, not an accounting claim.

## 0. Summary
Today a definition change silently overwrites history. `definitions.py` always writes `formula_version = 1` with `on conflict do update`, concepts and mappings carry no version, and eight writers delete-then-insert `canonical_fact`. The fix keeps four layers apart and makes only the last one depend on the definition:
- **L1** source facts (immutable).
- **L2** what each filing contains, slot by slot, at the finest grain, independent of any definition.
- **L3** versioned definitions that nobody edits in place.
- **L4** outputs that cite the definition and release that produced them.

A definition change then becomes a replay: read L1, L2 and the new L3, write candidates, publish a diff, have it sampled, then move the active pointer. No filing is reopened. Old outputs are retired to archives, never overwritten. The whole build is:
- three migrations (proposed numbers 0100-0102);
- a writer refactor, so the nightly and the replay run the same code;
- one test family (incremental equals full).

Effort: about 13-15 Data Engineer days (ASSUMED).

## 1. What the code does today (why the one-time test fails)
| # | Fact | Locator | Label |
|---|---|---|---|
| 1.1 | `seed()` inserts every metric at `formula_version = 1`. On conflict it overwrites `formula_description` and `requires_price`, then deletes and re-inserts that definition's inputs. Changing a formula in code changes the stored definition in place, and the old meaning is gone. | `pipeline/src/scrooner_pipeline/mapper/definitions.py` 237-268 | CODE-READ |
| 1.2 | Same pattern for the expanded metrics. | `mapper/expanded_definitions.py` 591-600, 611 | CODE-READ |
| 1.3 | All 82 `metric_definition` rows are version 1: 82 distinct names, none non-active. | catalog query (section 12) | MEASURED |
| 1.4 | `canonical_concept` (78 rows, 29 of them `*_resolved` twins) and `concept_mapping` (90 rows: 73 approved, 15 provisional, 2 rejected) have no version column. Their seeders upsert. | migration 0004 lines 27-53; `mapper/concepts.py` 377-424; `mapper/expanded_concepts.py` 673-720 | CODE-READ, MEASURED |
| 1.5 | Mapping changes ship as migrations that insert straight into `concept_mapping`. They take effect on the next nightly resolve, with no diff step. | e.g. `db/migrations/0095_cash_flow_continuing_operations_fallback.sql` | CODE-READ |
| 1.6 | `canonical_fact` has one row per (company, concept, period), with no version and no writer identity. Eight modules write it, most by delete-then-insert: `mapper/resolve.py` (186), `mapper/concept_fallback.py` (349, 702, 776, 871, 930, 1068), `mapper/conflict_resolution.py`, `mapper/dedup_majority_resolver.py`, `mapper/revenue_resolvers/net_lease_income.py`, `parsers/main_parser.py` (196), `corporate_actions/stock_splits.py`, `sanity/tag_investigator.py` (471, 591). | grep `insert into analytics.canonical_fact` | CODE-READ |
| 1.7 | `metric_value` is keyed by `metric_definition_id`, so two versions could coexist. But ten writers delete their own scope and re-insert: `calculate.py` 517, `ttm.py` 291/597/855, `price_metrics.py` 454, `expanded_metrics.py`, `fcf_growth.py` 126, `quality_flags.py` 305, `quality_score.py` 273, `dividend_streak.py` 125, `reconciliation.py` 185, `tax_reconciliation.py` 135. | grep `delete from analytics.metric_value` | CODE-READ |
| 1.8 | **Hazard if anyone inserts a version-2 row today.** At least seven writers look metrics up by name only (`select metric_name, id from analytics.metric_definition where metric_name = any(...)`) and build a dict. With two rows per name the dict keeps whichever row comes last, so the result is non-deterministic. Only `screener/snapshot.py` 126 filters `status = 'active'`, and nothing enforces one active row per name. | `ttm.py` 162, `expanded_metrics.py` 781, `fcf_growth.py` 155, `quality_flags.py` 349, `reconciliation.py` 224, `dividend_streak.py` 161, `quality_score.py` 311 | CODE-READ |
| 1.9 | Q4 and interim derivation runs at tag level for every duration tag, with no reference to `concept_mapping`. Lineage keeps only the FY fact's filing. The docstring says the Q1-Q3 inputs are "reconstructable by querying", which stops being true once authority or vintage changes later. | `normalizer/derived.py` 1-40, 373, 663 | CODE-READ |
| 1.10 | Doc 53 lists the Period Engineer's archive table `analytics.canonical_fact_retired` (migration 0098) as "file written, NOT committed". I found no 0098 file in the working tree (`find . -name '*0098*'`); it may be in another worktree. This spec reuses that table and does not redefine it. | doc 53 ledger row 0098 | DATA-INFERRED |

Sizes (MEASURED 2026-10-22; 16 connections open at the time):
- `canonical_fact`: about 17.0M rows, 4,680 MB.
- `metric_value`: about 13.3M rows, 4,573 MB.
- Database: 47 GB, against the 60 GB plan in doc 47.

A design that duplicates either table per version does not fit, so versions must be stored as deltas.

## 2. Acceptance criteria (what "versioned" means, testable)
1. **Never overwrite.** No statement changes or deletes an L4 row without first copying it to an archive with the run that retired it.
2. **One definition, one meaning.** A stored definition version never changes after it leaves `proposed`. A change creates a new version.
3. **The active pointer moves only after a published diff.** The diff is stored (company, object, period, old, new, reason) and summarized in the repo before promotion. The Verifier sample and the approval required for the version class are recorded first.
4. **Replay is a pure function of stored records.** The same L1, L2 and release give byte-identical L4. A definition change reads no SEC endpoint and no `raw` object (proved by test 7.4).
5. **Incremental equals full** (section 7).
6. **Reproducible.** "What did release R show for company C" is answered from active plus retired rows, without re-running anything.
7. **Coupled concepts move together.** A MAJOR change that affects several concepts is one release (AC-1 moves debt, interest, D&A and FCF together).

## 3. The four layers

### L1 Source facts (unchanged; owner Normalizer / Data Engineer)
- `core.fact`, `core.filing`, `core.period`, `core.unit`, `core.concept`: immutable, lossless.
- Structure evidence per accession: `analytics.filing_statement_line` and `analytics.filing_calc_edge` (R6 section 1). They are built under WO-1.10 only after K1 and K3 pass, and are not in this migration set.
- **A gap this spec must state:** `core.fact` comes from companyfacts, which strips custom tags and dimensions (data-team/21 rules 8.9 and 3). Some slots are carried only by custom tags (CVX cash, Air Lease flight equipment) or only by segment-member rows (CAT long-term debt), and `core.fact` cannot observe them. For those slots, "no filing reopened" holds only if their face facts are stored once in L1.
  - Proposed table: `analytics.filing_face_fact`, the FSDS `num.txt` face-statement rows (custom and member rows included) for accessions in `filing_statement_line`.
  - Owner: Data Engineer, gated by the WO-1.10 size pilot (ASSUMED about 1 GB for top-1000 over 2023q1-2026q3; not measured).
  - Until it exists, those slots are `unknown`. Any definition that needs them stays `partial` (hidden with a reason), never estimated.
- **Derived-fact lineage** (precondition for the Q4 backfill; owner Period Engineer; Normalizer boundary): `core.derived_fact_input(derived_fact_id, input_fact_id, input_role FY|YTD9|Q1|Q2|Q3, input_filing_id, input_vintage_date)` plus `core.fact.derivation_rule` text (`derive.q4_fy_minus_ytd@1` etc.). This is the R5 B6 lineage. It is not in my migration set; it is listed because section 8 depends on it.

### L2 Slot observations (new; definition-independent)
A slot is the smallest line a definition might include or exclude. L2 records what each filing contains for each slot. That is a fact about the filing, not a choice. It is captured once, at the finest grain, **including slots no current definition uses**, so flipping a definition later is arithmetic over stored rows.

```sql
-- vocabulary of slots (seeded from section 3.1; new slots are additive)
analytics.slot_catalog (
  slot_code      text primary key,          -- 'TD.FINANCE_LEASE_NONCURRENT'
  family         text not null,             -- 'TD','DA','CX','IE','RV','NI','CF','DIV','EPS','SH','CASH','OI','BS'
  statement      text not null check (statement in ('income_statement','balance_sheet','cash_flow','equity','note')),
  period_type    text not null check (period_type in ('instant','duration')),
  unit_kind      text not null check (unit_kind in ('monetary','per_share','shares','pure')),
  description    text not null,
  added_in_scanner_version int not null
);

-- which tags carry a slot, or a combined total spanning several slots. This is a taxonomy fact, not a
-- definition choice, so it moves here from R3's composite_tag_role (which was keyed on a definition)
analytics.slot_tag_role (
  taxonomy text not null, tag text not null,
  role text not null check (role in ('slot','anchor_total','combined')),
  covers_slots text[] not null,                  -- slots the tag's amount contains by its definition
  may_cover_slots text[] not null default '{}',  -- allowed by the taxonomy calc tree; needs filer evidence
  evidence text not null,                        -- taxonomy label / calc linkbase file / tag card path
  scanner_version int not null,
  primary key (taxonomy, tag, scanner_version)
);

-- one row per (filing, period, slot family) the scanner evaluated. With a scan row, a missing slot row
-- means 'unknown' (evaluated, no evidence); with no scan row, the slot is NOT_RUN
analytics.filing_slot_scan (
  filing_id bigint not null references core.filing(id),
  company_id bigint not null references core.company(id),
  period_id bigint not null references core.period(id),
  family text not null,
  scanner_version int not null,
  source_sha text not null,                 -- hash of the L1 rows read (fact ids + values); a changed input forces a rescan
  scanned_at timestamptz not null default now(),
  primary key (filing_id, period_id, family, scanner_version)
);

-- the observation itself: only states other than 'unknown' are stored (sparse)
analytics.filing_slot_observation (
  filing_id bigint not null, company_id bigint not null, period_id bigint not null,
  slot_code text not null references analytics.slot_catalog(slot_code),
  scanner_version int not null,
  state text not null check (state in ('reported_separately','inside_anchor','not_present','combined_inseparable')),
  value numeric,                            -- as stored in L1, sign as filed, unit checked (USD / shares / USD per share)
  share_class text,                         -- per-class EPS, DPS, shares (BRK, GOOGL); null = undimensioned
  class_key text generated always as (coalesce(share_class, '')) stored,
  fact_ids bigint[] not null default '{}',
  anchor_slot_code text,                    -- for inside_anchor: the anchor that contains it
  evidence jsonb not null,                  -- {method: 'tag'|'calc_edge'|'pre_row'|'line_evidence'|'verifier', locator, accession}
  form text not null, filing_date date not null, is_amendment boolean not null,
  is_comparative boolean not null,          -- value shown as a prior-period column of a later filing
  primary key (filing_id, period_id, slot_code, class_key, scanner_version)
);
create index on analytics.filing_slot_observation (company_id, slot_code, period_id);
```

Rules for L2:
- **Inputs.** The scanner reads L1 only (`core.fact`, `filing_statement_line`, `filing_calc_edge`, `filing_face_fact`, `company_filing_line_evidence`) plus `slot_tag_role`. It never reads a definition.
- **Forms.** It writes rows for every periodic filing: 10-K, 10-Q, their amendments and 10-KT. Never 8-K, DEF 14A, 20-F or 40-F (ledger WTRG, AEMD).
- **Evidence.** `inside_anchor` and `not_present` need filer evidence: a calc edge, a face row list, line evidence after its audit, or a Verifier record. A tag-dictionary miss is never `not_present` (ledger 2026-10-13: 18% of rendered samples show a line that the XBRL lookup missed).
- **Versioning.** A scanner change is a new `scanner_version`, and a rescan writes new rows. Old rows stay until the release that used them leaves the reproducibility window (section 10).
- **Idempotency.** Keyed by `(filing_id, period_id, family, scanner_version, source_sha)`, so an unchanged input is not rescanned.
- **Verifier evidence is not duplicated.** An observation whose method is `verifier` stores the `evidence_id` of the durable `analytics.cell_evidence` row (freeze register section 5) in its `evidence` json. L2 never copies or deletes cell evidence.

#### 3.1 Slot catalog v1 (finest grain; the list must be complete before any history backfill)
| Family | Slots | Definitions that may need them |
|---|---|---|
| TD debt | SHORT_TERM, LTD_CURRENT, LTD_NONCURRENT, LTD_COMBINED (`LongTermDebt`), DEBT_CURRENT_ALL, FINANCE_LEASE_CURRENT, FINANCE_LEASE_NONCURRENT, LEASE_COMBINED_DEBT (lease-inclusive tags), OPERATING_LEASE_CURRENT, OPERATING_LEASE_NONCURRENT, FHLB, MRP (mandatorily redeemable preferred), VEHICLE_CAPTIVE, UNAMORTIZED_DISCOUNT_COST, FACE_VALUE (recorded, never an anchor), FILER_TOTAL (`DebtLongtermAndShorttermCombinedAmount`) | AC-1, AC-2, AC-3, AC-4, NA-6, NA-7 |
| IE interest | DEBT, FINANCE_LEASE, FEES, CAPITALIZED, EXTINGUISHMENT, OPERATING (rental, captive finance), INTEREST_INCOME, NET_COMBINED, CASH_PAID | AC-1, AC-15 |
| DA | DEPRECIATION, DEPLETION, AMORT_INTANGIBLES, AMORT_SOFTWARE, AMORT_FINANCE_LEASE_ROU, OPERATING_LEASE_ROU, AMORT_DEBT_COST, AMORT_OTHER_OPERATING (content, regulatory, contract cost), ACCRETION, IMPAIRMENT, COMBINED_TOTAL (cash-flow add-back anchor), IS_SUBLINE (income-statement D&A sub-line, Kura) | AC-1, AC-6, NA-10 |
| CX capex | PPE, SOFTWARE, INTANGIBLES_OTHER, PRODUCTIVE_ASSETS_COMBINED, DISPOSAL_PROCEEDS, ACQUISITIONS, NONCASH_FINANCED, RENTAL_FLEET, RE_DEVELOPMENT, RE_IMPROVEMENT, RE_ACQUISITION, OTHER_FACE_CAPEX_ROW (every other investing purchase row, Air Lease) | AC-5, AC-12, NA-10 |
| RV revenue | TOTAL_AS_PRESENTED, CONTRACT (RCFC), LEASE, OTHER_OPERATING, EXCISE_INCLUDED, EXCISE_DEDUCTION, CONTRA (rebates, incentives), NONOP_INSIDE_TOTAL (equity-method income, gains), BANK_INTEREST_INCOME, BANK_INTEREST_EXPENSE, BANK_NONINTEREST_INCOME, INS_PREMIUMS_EARNED, INS_NET_INVESTMENT_INCOME, INS_REALIZED_GAINS, INS_FEES_OTHER, PREMIUM_TAXES | AC-9, AC-10, AC-11, NA-8, NA-9 |
| NI income | CONSOLIDATED (`ProfitLoss`), NCI, PARENT, PREFERRED_DIVIDENDS, PARTICIPATING_ALLOCATION, AVAILABLE_TO_COMMON, DISCONTINUED, CONTINUING | AC-8, AC-14, NA-11 |
| CF cash flow | CFO_TOTAL, CFO_CONTINUING, CFO_DISCONTINUED, CFI_TOTAL, CFI_CONTINUING, CFF_TOTAL, CFF_CONTINUING, FINANCE_LEASE_PRINCIPAL, BUYBACK_COMMON, NET_SHARE_SETTLEMENT_TAX | AC-20, NA-13 |
| DIV | DPS_DECLARED (per class), DPS_PAID (per class), CASH_COMMON, CASH_PREFERRED, CASH_ORDINARY_COMBINED (`PaymentsOfOrdinaryDividends`), LP_DISTRIBUTIONS, NCI_DISTRIBUTIONS, RATE_ON_ANNUAL_CONTEXT (pattern flag: a per-share value equal on 3-month and YTD contexts, V, LEA) | AC-13, NA-1, NA-3, NA-13, NA-14 |
| EPS / SH | EPS_BASIC, EPS_DILUTED, EPS_CONT_BASIC, EPS_CONT_DILUTED (ANDE), WEIGHTED_BASIC, WEIGHTED_DILUTED, OUTSTANDING_COVER (per class), OUTSTANDING_BS, OUTSTANDING_EQUITY_STMT | AC-14, NA-1, NA-2, split basis (R4) |
| CASH | CASH_ONLY (`Cash`), CASH_AND_EQUIVALENTS, RESTRICTED, COMBINED_WITH_RESTRICTED, INSURER_INVESTMENTS_AND_CASH | AC-21 |
| OI flags | REPORTED_SUBTOTAL, GAIN_LOSS_DISPOSAL, IMPAIRMENT, RESTRUCTURING, EQUITY_METHOD, OTHER_OPERATING_INCOME, DA_INSIDE, PRETAX_LABEL_SHIFT (AFG, ELS), NO_SUBTOTAL (single-step) | AC-7, T2 guard |
| BS other | INVENTORY, GOODWILL, OCI_NONE_STATEMENT (filing states there is no OCI) | AC-17, AC-18 |

Filing vintage is not a slot. It is carried on every observation (form, filing date, amendment, comparative), so AC-19 (restatement basis) is a selection rule over stored rows, not a re-read.

### L3 Definitions (new tables plus changes to existing ones)
```sql
-- a coherent set of active versions; exactly one row is 'active'
analytics.definition_release (
  id bigint generated always as identity primary key,
  status text not null check (status in ('draft','published','active','retired')),
  created_at timestamptz not null default now(),
  published_diff_run_id bigint,             -- the diff published before activation
  activated_at timestamptz, activated_by text,
  code_revision text not null,              -- git sha of the pipeline that computes it
  notes text
);
create unique index definition_release_one_active on analytics.definition_release ((true)) where status = 'active';

analytics.concept_definition_version (
  id bigint generated always as identity primary key,
  canonical_concept_id bigint not null references analytics.canonical_concept(id),
  version int not null,
  version_class text not null check (version_class in ('BASELINE','PATCH','MINOR','MAJOR')),
  status text not null check (status in ('proposed','verified','approved','active','retired','rejected')),
  economic_definition text not null,         -- the data-team/11 concept contract, as prose
  statement text not null, period_type text not null, unit_kind text not null,
  sign_policy text not null, attribution text not null,   -- 'consolidated' | 'parent' | 'common'
  template text not null default 'all',      -- group key from company_group (WO-1.6); 'all' until it exists
  combination_mode text not null check (combination_mode in ('first_match','sum','slots','rule_chain')),
  card_ref text,                             -- 'AC-1', 'NA-7'; null for BASELINE
  approved_by text,
  approved_role text check (approved_role in ('accountant','standardization_lead','founder_policy')),
  approved_at timestamptz,
  body_hash text not null,                   -- sha256 of the canonical JSON of row + slots + mappings + rules + overrides
  supersedes_id bigint references analytics.concept_definition_version(id),
  unique (canonical_concept_id, version, template)
);

analytics.concept_definition_slot (          -- for combination_mode 'slots'
  definition_version_id bigint not null references analytics.concept_definition_version(id),
  slot_code text not null references analytics.slot_catalog(slot_code),
  inclusion text not null check (inclusion in ('include','exclude','separate_concept')),
  arithmetic_sign smallint not null check (arithmetic_sign in (1,-1)),
  subtraction_allowed boolean not null default false,   -- may an excluded slot be removed from an anchor holding it (AC-1 C2)
  primary key (definition_version_id, slot_code)
);

analytics.concept_mapping_version (          -- frozen snapshot of concept_mapping for one version
  definition_version_id bigint not null references analytics.concept_definition_version(id),
  concept_id bigint not null references core.concept(id),
  priority int not null, confidence text not null,
  conditions jsonb not null default '{}',    -- form allowlist, unit, period type, era (valid_from / valid_to filing date)
  primary key (definition_version_id, concept_id)
);

analytics.concept_company_override_version (  -- frozen snapshot of the company_tag_preference rows the version uses
  definition_version_id bigint not null references analytics.concept_definition_version(id),
  company_id bigint not null references core.company(id),
  override jsonb not null,                   -- the preference row as it was, including its evidence accession
  primary key (definition_version_id, company_id)
);

analytics.rule_registry (                     -- one row per rule version; Tier 0 seed in RULE-REGISTRY-DRAFT-2026-10-22.md
  rule_id text not null,                     -- 'debt.floor_r5'
  version int not null,
  family text not null,
  kind text not null check (kind in ('guard','state','reason','derivation','selection','writer')),
  classification text not null check (classification in ('serve_time','recompute_leaf','recompute_cascade')),
  consumers_direct int not null, consumers_transitive int not null,   -- computed from the dependency graph at registration
  params jsonb not null default '{}',        -- thresholds are part of the version (doc 49 2.1)
  state_emitted text,                        -- frozen state enum value
  wording_key text,
  owner_role text not null, implementer_role text not null, verifier_role text not null,
  status text not null check (status in ('proposed','verified','approved','active','retired')),
  primary key (rule_id, version)
);

analytics.concept_definition_rule (           -- ordered rule chain of a version (fallbacks, conflict fill, guards)
  definition_version_id bigint not null references analytics.concept_definition_version(id),
  ordinal int not null, rule_id text not null, rule_version int not null,
  primary key (definition_version_id, ordinal),
  foreign key (rule_id, rule_version) references analytics.rule_registry(rule_id, version)
);

analytics.definition_release_member (
  release_id bigint not null references analytics.definition_release(id),
  object_kind text not null check (object_kind in ('concept','metric','rule','scanner')),
  object_id bigint,                          -- concept_definition_version.id or metric_definition.id
  rule_id text, rule_version int, scanner_version int
);
create unique index on analytics.definition_release_member
  (release_id, object_kind, coalesce(object_id, 0), coalesce(rule_id, ''), coalesce(rule_version, 0), coalesce(scanner_version, 0));
```

Changes to existing L3 tables:
- **`analytics.metric_definition`:**
  - Add `version_class`, `card_ref`, `approved_by`, `approved_role`, `approved_at`, `body_hash` and `supersedes_id`.
  - Widen `status` to `('proposed','verified','approved','active','deprecated','retired','rejected')`.
  - Add `create unique index metric_definition_one_active on analytics.metric_definition (metric_name) where status = 'active'`.
  - The 82 existing rows stay `active` and become release 1 members.
- **`analytics.metric_definition_input`:** a trigger rejects update and delete for the inputs of a definition whose status is not `proposed`. An approved definition's inputs are immutable.
- **`analytics.concept_mapping`** becomes **the working copy** and is no longer the source of resolution.
  - It stays writable, so existing migrations and `concepts.py` keep working.
  - `scrooner-defs freeze` snapshots it into a new `proposed` concept version.
  - Resolution reads `concept_mapping_version` of the active release.
- **`analytics.canonical_concept`:** unchanged. The active version comes from the release, which is the single source of truth, so no pointer column is added.
- **Views:**
  - `analytics.metric_definition_active` (one row per name, status active).
  - `analytics.concept_definition_active` and `analytics.concept_mapping_active` (via the active release).
  - Every reader in 1.8 switches to these views.

### L4 Outputs (existing tables, additive columns, archives, candidates)
```sql
alter table analytics.canonical_fact
  add column definition_version_id bigint,   -- concept version that produced the row (FK added NOT VALID, validated later)
  add column rule_id text,                    -- writer rule: 'resolve.first_match@1', 'debt.compose@3', 'split.rebase@1'
  add column release_id bigint not null default 1,
  add column run_id bigint;
alter table analytics.metric_value
  add column release_id bigint not null default 1,
  add column run_id bigint,
  add column input_bundle_id bigint;          -- the set of input concept versions read

create table analytics.input_bundle (id bigint generated always as identity primary key,
  bundle_hash text unique not null, members jsonb not null);

-- canonical_fact_retired is the Period Engineer's 0098 table; this set only adds the columns it lacks
alter table analytics.canonical_fact_retired
  add column if not exists release_id_from bigint, add column if not exists release_id_to bigint,
  add column if not exists definition_version_id bigint, add column if not exists rule_id text;
  -- retire_reason must accept 'definition_change','source_change','split_rebase','retirement'
create table analytics.metric_value_retired (like analytics.metric_value including defaults,
  retire_reason text not null, release_id_to bigint, retire_run_id bigint not null,
  retired_at timestamptz not null default now());

-- candidates written by a replay; never read by serving
create table analytics.canonical_fact_candidate (like analytics.canonical_fact including defaults,
  state text, reason_rule text);                 -- run_id is already a column after the alter above
create table analytics.metric_value_candidate (like analytics.metric_value including defaults);

create table analytics.definition_run (
  id bigint generated always as identity primary key,
  kind text not null check (kind in ('replay','promote','rollback','shadow_full','baseline')),
  release_from bigint, release_to bigint, company_ids bigint[] not null,
  objects jsonb not null,                    -- changed concepts/metrics/rules and their transitive consumers
  code_revision text not null, status text not null,
  started_at timestamptz, finished_at timestamptz,
  counts jsonb                               -- per change_class
);
create table analytics.definition_change_diff (
  run_id bigint not null, company_id bigint not null,
  object_kind text not null, object_name text not null,
  period_start date not null, period_end date not null, period_label text not null,
  old_value numeric, new_value numeric, old_reason text, new_reason text,
  old_source_fact_ids bigint[], new_source_fact_ids bigint[],
  change_class text not null check (change_class in ('value_changed','now_null','now_valued','reason_changed','lineage_changed')),
  primary key (run_id, company_id, object_kind, object_name, period_start, period_end, period_label)
);
```

Notes:
- **No table rewrite.** Adding nullable or constant-default columns is metadata-only on PostgreSQL 11+ (prod is 17.6), so the 17M-row and 13M-row tables are not rewritten. No new index on these columns at first.
- **What `release_id` means.** It is the release under which the row was last computed. A new release does not rewrite an unchanged row.
- **Reproducing release R.** `analytics.canonical_fact_as_of_release(R)` returns:
  - live rows with `release_id <= R`, except those whose archived successor was retired at or before R;
  - plus retired rows with `release_id_from <= R < release_id_to`.

  Metric values work the same way.
- **Nightly source changes** (a new filing) keep using archive-then-replace, with `retire_reason = 'source_change'` under the active release.
- **Two different reproduction questions.** "What would release R give on today's data" is a replay; this spec guarantees it. "What was shown on date D" comes from the archive by timestamp, and is best-effort only (section 12).
- **Reasons are rule IDs, not free text.** Pass-through null reasons (S4, WO-1.5) and guard reasons are stored as rule IDs plus wording keys (`debt.floor_r5@1`). The free-text constants in the held code (`REASON_UNDECIDABLE_FLOOR`, `NON_ADDITIVE_UNAVAILABLE_REASON`) map to rule IDs in the registry.

## 4. Version classes
| Class | What changes | Can values change? | Who approves | Verifier tier (WO-REVIEW-verifier C2) | Effect on consumers |
|---|---|---|---|---|---|
| BASELINE | release 1: frozen copy of today's behavior | no, by definition | Standardization Lead + Engineering Head (it is a snapshot) | baseline drift report (7.6-prod), no sample | n/a |
| PATCH | a guard, state, reason, wording or evidence detector; hides or relabels only | no displayed number changes; values can become hidden | Standardization Lead proposes, Verifier samples, founder release policy applies | P 30, plus the count of correct values hidden | consumers recompute (an input may now be null with a reason); their versions do not change |
| MINOR | source selection or precedence within an unchanged meaning (mapping set, tag order, company override, N + C reorder NA-7, revenue structural pick NA-9) | yes | Verifier sample. Accountant not needed only if the founder's release policy accepts filing-proven source selection as non-definitional (my condition 6; founder item 11) | V 60 + 15 risk + 15 negative controls | consumers recompute; versions unchanged |
| MAJOR | perimeter or meaning: a slot include/exclude flag, attribution, sign policy, unit, period type, template applicability, the economic text | yes | the named accountant (card answered and signed) | V tier per affected family, plus a per-company diff | **every transitive consumer metric gets a new version in the same release** (same formula, new meaning) |

The class is computed as well as declared. `scrooner-defs classify` compares the new body with the active one:
- **MAJOR:** any change to `concept_definition_slot`, `attribution`, `sign_policy`, `unit_kind`, `period_type`, `template` or `economic_definition`.
- **MINOR:** a change to `concept_mapping_version`, overrides or a selection rule.
- **PATCH:** a change only to guard or state rules, or their params.

CI fails if the declared class is lower than the computed one.

## 5. How a definition change becomes a recompute (no filing reopened)
The same code computes the nightly and the replay. A second, replay-only implementation would drift from production, which is the redo this spec exists to prevent. So every L4 writer takes two parameters:
- **`DefinitionSource`:** `active` (nightly) or `release(R)` (replay). It supplies mapping sets, slot flags, rule chains, overrides and metric versions. Once the switch flag is on, no writer reads `concept_mapping`, `company_tag_preference` or a hard-coded tag list directly.
- **`WriteTarget`:** `live` (nightly, archive-then-replace) or `candidate(run_id)` (replay, insert into `*_candidate` only).

Steps (CLI names proposed; a new `scrooner-defs` entry point):
1. **Freeze.** `scrooner-defs freeze --concept capex --class MINOR --card NA-10` snapshots the working copy and the referenced rules into a `proposed` version, plus a `draft` release that copies every other active member.
2. **Classify.** `scrooner-defs classify --release R` computes the class (section 4) and the change set: the changed objects plus their transitive consumers. Consumers come from `metric_definition_input` and the code-derived graph (`data-team/strategy/data/metric_dependency_graph.csv`, kept current by Triage under WO-7).
3. **Replay.** `scrooner-defs replay --release R --scope auto`:
   - Selects affected companies by query: any company with L1 facts on a tag whose mapping changed, an L2 observation on a slot whose flag changed, an override that changed, or a stored value on a changed rule's guarded node.
   - Runs the normal writers in topological order with `DefinitionSource=release(R)` and `WriteTarget=candidate(run)`.
   - Connects as a role with no privilege on `raw`, and with `SCROONER_OFFLINE=1`, which makes `common/sec_client.py` raise on any request.
4. **Diff.** The replay writes `definition_change_diff` (changed rows only) and `definition_run.counts`.
5. **Publish.** `scrooner-defs publish-diff --run N` writes the summary to `doc/data-moat/team/definition-diffs/<release>.md`: counts by class, the 20 largest changes, and every top-100 company that changed. The Release Manager commits it. This is the "published diff" of doc 49.
6. **Sample and approve.** The Verifier draws the sample on the diff, independently of the proposer. Approval is recorded on the version rows (`approved_by`, `approved_role`). For MAJOR, the reference is the signed accountant card (ACCOUNTANT-PACKET-2026-10-22).
7. **Promote.** `scrooner-defs promote --run N`, in the heavy-db-jobs slot.
   - Per company chunk (about 50 companies), in one transaction: copy every live row in scope whose value, reason or lineage differs into `*_retired` (`retire_reason='definition_change'`, `release_id_to=R`, run id), replace it from the candidate, and set `release_id = R`. Equal rows are untouched.
   - Then release R becomes `active` and the previous one `retired`.
   - First live run on 10 companies, a Verifier check, then the rest (doc 49 section 3).
8. **Recheck.** Re-run certify for the cohort, then the screener snapshot rebuild (existing nightly steps).
9. **Rollback.** `scrooner-defs rollback --run N` deletes the rows the run inserted and re-inserts that run's retired rows, one transaction per chunk, then re-activates the previous release.

Cost: one replay over the affected companies, typically one concept family and its consumers. A definition change never costs a re-mapping of tags or a new SEC fetch. Two redo triggers remain:
- a slot that nobody captured;
- a face fact that is not in L1 (the L1 gap in section 3).

That is why the slot catalog must be complete, and `filing_face_fact` sized, before any history backfill.

## 6. File-by-file changes (for the Data Engineer)
| File / object | Change |
|---|---|
| The seven name-only readers (1.8) and every other reader of `metric_definition` | Switch to `metric_definition_active`. **First change, ahead of everything else**, together with the partial unique index. Until this is done, no version-2 row may exist. |
| `mapper/definitions.py`, `mapper/expanded_definitions.py` | Every entry gets an explicit `formula_version` and `version_class`. `seed()` stops writing `1` and stops `on conflict do update`. It computes `body_hash` (description, inputs, roles, requires_price, version):<br>- same hash as stored: no-op;<br>- different hash, same version: **raise** (a silent edit);<br>- bumped version: insert a new `proposed` row and its inputs, never touching the old row.<br>A committed lock file `mapper/definition_lock.json` (name -> version -> body_hash) is checked in CI, so an edited description or input without a bump fails CI. |
| `mapper/concepts.py`, `mapper/expanded_concepts.py` | Keep writing the working copy. Add a test that a seeding run changes no active resolution until `freeze` and promotion. |
| `mapper/resolve.py` | Load mappings from `DefinitionSource` (the active release's `concept_mapping_version`), not `concept_mapping`. Stamp `definition_version_id`, `rule_id` (`resolve.first_match@1` or `resolve.sum@1`), `release_id` and `run_id`. Replace the bare delete-then-insert with archive-then-replace through one shared helper, `mapper/output_writer.py` (new). The Period Engineer's 0098 path uses the same helper. |
| The seven other `canonical_fact` writers (1.6) | Each becomes a named rule in `rule_registry`, with a version constant in code (`RULE_ID = 'debt.compose'`, `RULE_VERSION = 3`). Each writes through `output_writer` and keeps its own delete scope (the scope rules in pipeline/CLAUDE.md still apply). |
| The ten `metric_value` writers (1.7) | Look up definitions through `metric_definition_active` (or the members of `release(R)`). Write through `output_writer`. Stamp `release_id`, `run_id` and `input_bundle_id`. |
| `normalizer/derived.py` | No definition dependency (CODE-READ 1.9). Gains the B6 lineage write (Period Engineer). Eligibility of derived facts for `canonical_fact` becomes a Mapper rule, `derive.mapper_eligibility@1` (the additive allowlist), per the Period Engineer's boundary correction. |
| `screener/snapshot.py`, `screener/resolve.py`, `apps/backend` readers | No change: `__formula_version` columns already exist, and they read live tables, which hold only active rows. |
| `certification/` | Add I14 `incremental_drift` (7.5-prod) once 0097 accepts `^I[0-9]+$`. |
| New: `mapper/output_writer.py`, `mapper/definition_source.py`, `jobs/defs.py` | The two writer parameters, the archive-then-replace helper, the CLI. |
| New workflow `pipeline-definitions.yml` | `replay`, `promote`, `rollback`, `shadow_full`. Joins `concurrency: heavy-db-jobs`, with an explicit `timeout-minutes`; the job sets its own per-statement `statement_timeout`; tested the way CI invokes it. |

## 7. The test that proves incremental equals full
**Fixture.** A frozen extract of `core.fact`, `core.filing`, `core.period`, `core.unit` and `core.concept` for 12 companies with known hard cases: AAPL, MSFT, WMT, CVX, AMD, APTV, HON, V, FCX, PFE, CDNL, JPM. It is limited to the tags those companies file for the concepts in scope and committed as CSV under `pipeline/tests/fixtures/definition_versioning/` (target under 2 MB; ASSUMED). It runs in the existing real-SQL scratch-schema test pattern on CI's `postgres:16`.

**Normalized row set.**
- For `canonical_fact`: `(company_id, concept name, period start, period end, value::text, sorted source_fact_ids, definition body_hash, rule_id, reason)`.
- For `metric_value`: `(company_id, metric_name, version, period_start, period_end, period_label, value::text, is_null_reason, sorted source_fact_ids)`.
- Excluded: surrogate ids, timestamps, `run_id`, and `release_id` (checked separately).
- Comparison: `md5(string_agg(row_text, E'\n' order by row_text))` per table, plus a row-level `except` in both directions, printed on failure.

| # | Test | Pass condition |
|---|---|---|
| 7.1 | Idempotency: full build of (D0, R1) twice | identical hashes; zero `definition_change_diff` rows on the second run |
| 7.2 | **Incremental equals full.** Three delta types, run separately and together:<br>(a) data delta: a new 10-Q for two companies;<br>(b) MINOR: the capex mapping adds `PaymentsToDevelopSoftware`;<br>(c) MAJOR: the AC-1 flag flip (finance leases included), moving `total_debt`, `interest_expense` and `da_ebitda` together.<br>S_inc = full(D0, R1), then incremental(delta, R2, auto scope). S_full = full(D0 + delta, R2) on an empty schema. | S_inc hash = S_full hash for both tables. In S_inc, every row whose value changed carries `release_id = R2`, and every unchanged row keeps `R1`. |
| 7.3 | Scope isolation | the set of (company, object) pairs in the diff is a subset of (affected companies) x (changed objects plus transitive consumers) |
| 7.4 | No filing reopened | the replay runs under a role without `raw` privileges and with `SCROONER_OFFLINE=1`; it succeeds, and a patched `SECClient` records zero calls |
| 7.5 | Rollback round trip | promote R2, then roll back: hashes equal the pre-promotion state, `release_id` included |
| 7.6 | Reproduction | after R2 is active, `canonical_fact_as_of_release(R1)` equals the row set of S_full(D0 + delta, R1) |
| 7.7 | Silent-edit guard | editing a description or input in `definitions.py` without a version bump fails `seed()` and the lock-file test |
| 7.8 | One active definition | inserting a second `active` row for a metric name fails (partial unique index); the readers in 1.8 return one id per name |

**Mutation checks.** Each must make at least one test fail. They run on a temp copy, never the working tree (R6 section 6):
- (m1) drop one company from the auto scope;
- (m2) skip the transitive consumers;
- (m3) promote without archiving;
- (m4) a writer ignores `DefinitionSource` and reads `concept_mapping`;
- (m5) a replay writes to the live table;
- (m6) the diff omits `now_null` rows.

Production guards:
- **7.5-prod shadow full.** Nightly, after the reprocess, take 50 rotating companies of the 986 (a full rotation in about 20 nights). Run a full recompute into the candidate tables and compare it with live. Any difference becomes a `certification_finding` I14 `incremental_drift` (severity `review`), with the diff rows as evidence. This is doc 47 v2 section D's "nightly incremental certify".
- **7.6-prod baseline drift (a Gate A measurement, run once).** Replay release 1 (today's frozen definitions) over the 986 into candidates and diff against live.
  - Diffs are expected: stale fills, insert-only paths, the 2026-10-17 stale-fill class.
  - Each diff is classified and routed as a finding. None is fixed by promoting the replay outside the normal release path.
  - The count is published as "baseline drift", so the first real version change is not blamed for old drift.

## 8. Preconditions for the Q4 backfill and for history backfill

### 8.1 Q4 backfill (re-deriving or filling Q4 and interim quarters across history)
Derivation is tag-level in L1 and reads no definition (1.9), so it does not need L2 slots. It does need a fixed basis, lineage and a reversible write.

| # | Precondition | Owner | State today |
|---|---|---|---|
| Q-1 | Restatement display basis decided (AC-19; founder item 12). Default if undecided: block mixed-basis derivation (NA-4). | founder + accountant | open |
| Q-2 | Additive allowlist (classes A/B) at the Mapper gate, starting from `certification/model.py ADDITIVE_FLOWS`, approved by me and verified by the Verifier | Standardization Lead, Verifier | draft exists (R5 section 6); not approved |
| Q-3 | B6 lineage: every derived fact stores all input fact ids, their filing and vintage, and the derivation rule id | Period Engineer | not built |
| Q-4 | RU-1 shipped: periodic-form gate on derivation inputs (WTRG) and per-share non-derivation (NA-1, NA-2) | Period Engineer, Data Engineer | held code, uncommitted |
| Q-5 | Archive table (0098) applied; every backfill write is archive-then-replace with a run id | Period Engineer, Data Engineer | file not found in tree (1.10) |
| Q-6 | Definition registry (0100) and output versioning (0102) applied; resolve reads the frozen release; `derive.mapper_eligibility@1` registered | Data Engineer | this spec |
| Q-7 | Tests 7.1-7.8 green in CI and mutation-checked; shadow full clean on its first 50 companies | Data Engineer, Verifier | not built |
| Q-8 | Dry-run over the 986 with per-class counts (unchanged, newly derived, re-derived, now hidden); a Verifier sample per class; a separate first live run (10 companies, then the cohort) | Period Engineer, Verifier | not run |
| Q-9 | Size check of new derived rows against headroom; stop if free space would fall below the Engineering Head's floor | Data Engineer | not run |

### 8.2 History backfill (widening the stored or displayed window, perimeter capture for past periods, FSDS structure for history)
All of 8.1, plus:

| # | Precondition | Owner |
|---|---|---|
| H-1 | Slot catalog v1 complete (3.1) for every family that an open AC card can change, reviewed by the Verifier against the R3 fixtures; scanner v1 passes a 30-company audit with zero false `not_present` | Standardization Lead, Data Engineer, Verifier |
| H-2 | L2 populated for the backfill window. **No history backfill under a definition that an open AC card can change unless the slot components are stored separately in L2.** A concept whose card is open may be backfilled only as slots, never as a single combined number. | Data Engineer |
| H-3 | `filing_face_fact` sized and loaded for the window, or the custom-only and member-only slots explicitly left `unknown` (hidden) for that window | Data Engineer (WO-1.10 pilot) |
| H-4 | Structure pilot K1 and K3 passed (doc 47 section 3) before calc-edge evidence is used for `inside_anchor` | Data Engineer, Verifier |
| H-5 | History gate (doc 38: nothing before 2015-01-01 shown as current) and F-2 (no pre-2015 base year) encoded as rules: `history.display_gate@1`, `growth.base_year_gate@1` | Standardization Lead |
| H-6 | Successor/predecessor CIK links FILING-CHECKED before any series is joined (XOM 8-K12B; WO-2 item 5) | Period Engineer, Company Master |
| H-7 | Split basis live (train R4: `split_event`, `filing_share_basis`, migration 0099), so per-share history is not re-based twice (GOOG, WMT ledger rows) | Period Engineer |
| H-8 | Engineering Head accepts the storage plan for L2 + history: ASSUMED about 0.3 GB of L2 for top-1000 2015+ and about 1.5 GB for the full population, to be measured on the first 50 companies | Engineering Head |

## 9. Migration set (proposed numbers; the builder claims them in doc 53 at start)
Status in doc 53:
- Next free number is 0100.
- 0098 and 0099 are claimed by the Period Engineer.

Doc 49 section 7.3 says later numbers are claimed by their owner at build start. Others also need numbers: the Data Engineer's `cell_state`, `company_group` and `metric_template` work, and the freeze register's `cell_evidence` table (A7: "next for `cell_evidence`"). So I have not written claims on behalf of an agent who has not started. The numbers below are placeholders that the Data Chief arbitrates.

Proposed order and content. Each migration is additive, ends with `;`, and keeps contiguity per `scripts/check_migrations.py`:

| Proposed | Name | Content | Depends on | Rollback |
|---|---|---|---|---|
| 0100 | `definition_registry` | `definition_release`, `concept_definition_version`, `concept_definition_slot`, `concept_mapping_version`, `concept_company_override_version`, `rule_registry`, `concept_definition_rule`, `definition_release_member`; the new `metric_definition` columns, widened status check and partial unique active index; the `metric_definition_input` immutability trigger; the three `*_active` views. Reads nothing, backfills nothing. | 0098 committed (number order only) | drop the new objects; drop the added columns and index; restore the old status check |
| 0101 | `slot_observation` | `slot_catalog`, `slot_tag_role`, `filing_slot_scan`, `filing_slot_observation` and indexes. Empty. | 0100 | drop tables |
| 0102 | `output_versioning` | the added columns on `canonical_fact` and `metric_value` (metadata-only); `input_bundle`; `metric_value_retired`; `canonical_fact_candidate`; `metric_value_candidate`; `definition_run`; `definition_change_diff`; the missing columns on 0098's `canonical_fact_retired`; the SQL functions `canonical_fact_as_of_release(R)` and its metric equivalent | 0098 applied, 0100 | drop the added objects and columns (they hold nothing that cannot be rebuilt from the archive) |

Release 1 (BASELINE) is seeded by `scrooner-defs freeze --baseline`, not by a migration, because it writes rows derived from live tables. The command has a dry-run and writes only the new L3 tables.

Apply order:
- 0100 and 0101 can be applied at any time after commit (empty tables, no reader).
- 0102 only after the writer refactor is merged behind a flag (`DEFINITION_VERSIONING=off` keeps today's behavior), so the new defaults never meet a writer that ignores them.
- `lock_timeout 5s`, per the Engineering Head.

## 10. Storage and effort
**Storage:**
- **L3:** kilobytes.
- **L4 columns:** about 8-24 bytes per new or rewritten row. Existing rows are unchanged (metadata defaults).
- **Archives:** grow only by changed rows. A revenue MAJOR change across all companies would archive about 0.3-0.5 GB (ASSUMED from revenue's share of `canonical_fact`; not measured).
- **Archive retention:** keep every retired row for releases inside a reproducibility window (proposed: the last 4 releases or 12 months, whichever is longer). Older archives move to a dump in Storage. Engineering Head decision.
- **L2:** see 8.2 H-8.

**Effort (Data Engineer days, ASSUMED):**

| Item | Days |
|---|---|
| Readers to `*_active` views, plus the partial unique index | 1 |
| Versioned seeding in `definitions.py` and `expanded_definitions.py`, plus the lock file | 1 |
| Migrations 0100-0102 with scratch-schema tests | 2 |
| `output_writer` and `DefinitionSource` through the 8 + 10 writers | 4-5 |
| CLI and workflow | 2 |
| Tests 7.1-7.8 with fixtures and mutation checks | 2-3 |
| Baseline freeze, baseline drift run and report | 1 |
| **Total** | **13-15** |

The L2 scanner v1 is separate: about 5-7 days after the slot catalog is approved (ASSUMED).

My part:
- slot catalog seed and `slot_tag_role` evidence: 2 days;
- BASELINE body text for the 78 concepts: 1 day;
- review of each PR's definition behavior: ongoing.

## 11. Open decisions (who decides)
1. **Data Chief:**
   - migration numbers for this set versus `cell_state`, `company_group` and `metric_template`;
   - which Data Engineer lane builds it;
   - timing. My recommendation: do the one-day readers + unique-index change before R2, and the rest in parallel with R3, before Gate C.
2. **Period Engineer:**
   - confirm that `canonical_fact_retired` (0098) can carry the columns 0102 adds, and that one shared `output_writer` serves both the split rebase and definition changes;
   - confirm that the B6 lineage table (Q-3) is yours, and its shape.
3. **Engineering Head:**
   - the archive retention window;
   - `filing_face_fact` go/no-go after the pilot;
   - whether `shadow_full` fits in the nightly or needs its own slot.
4. **Founder (via the release policy):** whether MINOR (filing-proven source selection) may ship without the accountant (my condition 6; founder item 11).

## 12. Commands actually run, evidence, untested scope
**Read:**
- data-team/20, 21, 22, 11 and 03;
- strategy/47, 49, team/WO-REVIEW-standardization-lead, team/R3 (sections 4-5), team/R6 (section 1), team/S3 (sections 1-2 and 4), team/WO-REVIEW-period-engineer (grep);
- `mapper/definitions.py`; migrations 0004, 0095 and 0097; the doc 53 migration ledger; `normalizer/derived.py` (head); `certification/model.py` ADDITIVE_FLOWS.

**Code searches:**
- grep and sed over `pipeline/src` for the writers and readers of `canonical_fact`, `metric_value` and `metric_definition`;
- `git diff` on `derived.py` and `concept_fallback.py` (reason constants);
- `git log` on `definitions.py`: last change 8660a17 (a seed-text fix), no versioning work in its history;
- `find` for 0098.

**Database (one read-only psql session, `default_transaction_read_only on`, `statement_timeout 30s`):** `pg_stat_activity` count (16); `pg_class` sizes for 9 analytics tables; database size; `metric_definition` version counts; `canonical_concept` twin count; `concept_mapping` by confidence.

**Shared memory:** `python3 mind/mind.py search` x3 (definition versioning, formula_version, canonical_fact rebuild); no prior entry on versioning.

**NOT RUN / untested:**
- no prototype of any table or test;
- sizes for L2, the archives and `filing_face_fact` are ASSUMED;
- "what was shown on date D" reproduction is best-effort only;
- the claim that derivation is definition-independent rests on a code read of `derived.py`, not a test;
- the 0098 file was not found, so I do not know its columns.

## 13. Acceptance (freeze register A13: "design section with schema sketch and a replay test spec; two acceptance signatures")
This document is the design section (sections 3-5), the schema sketch (sections 3 and 9) and the replay test spec (section 7).

| Role | Accepts (yes / yes with changes / no) | Changes required | Signature and date |
|---|---|---|---|
| Engineering Head (scrooner-4d): schema, capacity, migration order | | | |
| Data Head (Data Chief): layers, version classes, backfill preconditions | | | |
| Period Engineer (advisory): sections 3 L1 lineage, 8.1, 11.2 | | | |

