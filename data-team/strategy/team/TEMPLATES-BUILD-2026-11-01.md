# Sector-template layer build: report to Dhairya (2026-11-01)

Status: **IN PROGRESS.** These are the findings so far; this file is updated as the build lands on this branch.
Branch: `work/data-engineer/sector-templates`. Nothing has been applied to any database, and no production data has been written.

## 1. Blocker: the templates file does not exist

The brief says to seed from `data-team/strategy/SECTOR-TEMPLATES-2026-11-01.md`. **That file does not exist** on `origin/main` or on any of the 177 remote branches (checked by listing every branch tree). Here is what does exist:

| Source | What it is | Usable as the seed? |
|---|---|---|
| Doc 02, "Founder ruling of 2026-11-01: sector templates and 100% coverage" | The rule: a field is shown only if the sector template includes it; coverage = valued ÷ template cells | Rule only, no template contents |
| `data-team/30-SECTOR-TEMPLATES-FOR-FULL-ROWS-2026-10-19.md` | An older narrative template proposal | No (not machine-readable, pre-ruling) |
| `data-team/strategy/50-SECTOR-ROWS-AND-VISIBLE-METRIC-SETS-DRAFT-2026-10-22.md` | DRAFT sector rows (bank, insurer, REIT and others), **not approved** | No (draft) |
| `data-team/strategy/data/template_v1_draft.csv` (only on `archive/branches/bs-tl-release1-guard-2026-11-01`) | Draft group × data-point REQ/COND/NIT table, based on presence rates | No (draft, archived) |

**What I am doing about it:** I am building the seeder against a strict, documented file format (section 3), with test fixtures. The Sector Analyst, or whoever owns the template contents, writes the real `SECTOR-TEMPLATES-2026-11-01.md` in that format. The seeder then runs on it unchanged. I am not inventing template contents: which fields a bank shows is a Sector Analyst and Standardization Lead decision, not an engineering one.

**Decision needed from you:** who writes the templates file, and should `template_v1_draft.csv` or doc 50 be its starting point?

## 2. Migration number

- **0120 is claimed** in doc 53 on this branch. 0118 and 0119 are the latest files on main, and no branch has a 0120 file.
- The claim line lives on this work branch. **It must reach main first** (release manager), otherwise another session could take 0120.
- The migration is not applied, and applying it needs the founder's typed words.

## 3. Design (being implemented)

**Table `analytics.company_data_point_template` (migration 0120)**
- Columns: company_id, data_point, in_template, reason, effective_from. For traceability it also has template (the sector template applied), source (`sector_default` / `company_override`) and template_version.
- Primary key: (company_id, data_point, effective_from).
- `reason` is required when `in_template = false`, and for every company override.
- **A company's current template** is all of its rows at the latest `effective_from` on or before the as-of date. Every seed writes the full set for each company, so dropping a field in a new version removes it and never leaves a stale row behind.

**Templates file format** (markdown tables under fixed headings, so it stays human-editable and diffable):
- Metadata: `template_version` and `effective_from`.
- `## Sector assignment`: template | sic_from | sic_to. SIC ranges must not overlap.
- `## Company assignment`: cik | template | reason. Use it when SIC is wrong for a company (for example a BDC filed under a generic SIC).
- `## Sector defaults`: template | data_point | in_template | reason.
- `## Company overrides`: cik | data_point | in_template | reason. This covers ruling item 3, where a company's own combined line goes into its template.
- **Hard failures, never silent defaults:**
  - a cohort company that matches no template,
  - duplicate rows,
  - a missing reason,
  - a data point unknown to `canonical_concept` / `metric_definition`.

**Seeder**
- The cohort is `doc/data-moat/team/top1000/shards.csv`, which already carries company_id, cik and sic. **The plan is therefore built offline from files only.**
- Dry run is the default and writes a plan CSV plus a summary.
- `--apply` writes each company in one batched transaction: it deletes that company's rows at this effective_from, then inserts. Running it again gives the same result.

**Coverage snapshot (`mapper/coverage_snapshot.py`)**
- When template rows exist, each concept or metric row reports **valued ÷ template cells**: companies whose current template includes the data point, and how many of them have a value.
- Data points that are in no template get no row: they are not shown, so they are not cells.
- A new score row, `template_cell_coverage_score`, gives Σ valued ÷ Σ template cells.
- A template data point with no producer counts as a template cell with 0 valued, so it stays visible as a defect.
- Until 0120 is applied and seeded, the snapshot keeps today's population denominators and logs that the template table is absent. This keeps the nightly `snapshot-coverage` step from crashing before the apply. It is a reporting-only state, not a value fallback.
- The cell grain here is company × data point, matching the existing snapshot. Period-level cells (ruling item 4, periods before the first filing) belong to the cohort coverage table and are out of scope for this change.

## 4. Next (on this branch)
Migration 0120 plus a clean-replay check, the seeder plus tests, the snapshot change plus tests (each mutation-checked), and CI green. This file will be updated with the test and CI evidence.
