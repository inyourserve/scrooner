# One display path: resolver is truth through to page, metrics and screener (plan, 2026-11-22)

Goal (founder 2026-11-16 "one path: resolver is truth", doc 02; 2026-11-22 standard definitions): what we certify is
exactly what a user sees on the stock page and filters on in the screener. Owning systems (`data-team/SYSTEMS.md`): #10
structural loader, #11 proof, #13 display state, #16 metrics, #17 screener, #19 pages. Extend them; build nothing new.
Written from `origin/main` fa369851. Plan only: no code, no DB write, no migration claimed.

## 1. Current read paths (all bypass proof and display state)

Paths under `pipeline/src/scrooner_pipeline/` unless shown.

| Consumer | Reads | file:line | What is wrong |
|---|---|---|---|
| Stock page: FY/quarter period picker | `analytics.canonical_fact` | `apps/backend/company_page.py:126`, `:135` | years come from any fact row; HIDDEN_YEAR / pre-filing years still appear |
| Stock page: statement rows | `canonical_fact` x `statement_line` | `company_page.py:171` (`statement_rows`) | every row/value shown; ignores HIDDEN_ROW, OUT, OPEN, DISAGREE; no badge, no R page |
| Stock page: EBITDA / FCF rows | `analytics.metric_value` | `company_page.py:186`, `:203` | metric shown even when an input is hidden/DISAGREE |
| Stock page: metric tiles, history, peers | `metric_value` | `company_page.py:103`, `:119`, `:225` | no badge; null reason only on tiles |
| Stock page: book value, public float | `canonical_fact` | `company_page.py:259`, `:367`, `:402` | latest row regardless of proof/display |
| Legacy TS port | `canonical_fact` (6 refs) | `apps/app/lib/company/db.ts:240` ff. | second copy of the page SQL |
| Watchlists | `canonical_fact`, `metric_value` | `apps/backend/routers/watchlists.py:72`, `:115`, `:123` | same bypass |
| Calculators (inputs) | every `canonical_fact` row | `mapper/calculate.py:285`, `mapper/ttm.py:199`, `mapper/expanded_metrics.py:459`, `mapper/price_metrics.py:123`, `:146`, `:244` | DISAGREE/UNCHECKED/hidden cells feed metrics; write `metric_value` at `calculate.py:560` with no badge |
| Rule (c) gate | `cell_proof` | `metrics/provenance.py:10`, `:159` | correct rule, but `build_cell_record` has no caller: not wired into any calculator |
| Screener snapshot | all `metric_value` rows | `screener/snapshot.py:240` via `screener/resolve.py:81` | built from all metrics; no badge/null-reason column (`snapshot.py:80`) |
| Display state | written, never read | `mapper/cell_display_state.py:19` (cols), 0130 | no reader under `apps/`; holds no value and no badge |

## 2. Target single path

```
resolver CSV (#8) -> structural loader (#10) -> canonical_fact -> cell_proof (#11)
   -> cell_display_state (#13): one row per cell = display + hide_class + badge + value + accession + r_page
       -> analytics.shown_cell (view: display='SHOWN_VALUE' and proof verdict PROVEN or NOT_PRESENTED-zero)
           -> company_page.py / watchlists (#19)  -> page cell = shown_cell row, badge and R page rendered
           -> calculators (#16) via one loader -> metric_value (+ badge, is_null_reason)
                 -> screener snapshot (#17): value + badge + null_reason per metric
```
Rules: (a) a page or metric never reads `canonical_fact` directly; only `shown_cell`. (b) A non-shown input gives the
metric a null with reason `input_not_shown:<dp>:<display|verdict>` (or the cell state `included_in:<dp>` /
`not_applicable` / `not_disclosed`), never a fallback. (c) A metric's badge = union of its inputs' non-`as_printed`
badges (registry rule "a badge is carried to every ratio that uses it", `metrics/registry/data_points.csv` filter_note).

## 3. Badges: where they come from and how they travel

- Vocabulary: `metrics/registry.py:85` (`as_printed`, `combined:<items>`, `derived:<formula>`, `perimeter:<diff>`), one
  per fallback step in `data_points.csv` (`fallback_order` <-> `badges`, 425 rows, on main).
- Per cell: the resolver row knows which step fired (`decision`, `flags`: `DERIVED`, `text_stated`, combined label;
  `line_map/RESOLVER-OUTPUT-FORMAT.md`). New pure function `metrics/registry.py::badge_for(dp, sector, resolver_row)`
  maps step -> badge; the coverage export stores it in `cell_display_state.badge` (if the step is ambiguous: raise,
  cell stays OPEN; never default to `as_printed`).
- Page: `company_page.py` returns `{value, badge, r_page, accession}` per statement cell; `FinancialTable` renders a
  badge chip and R-page link (apps/app component change, screenshot-verified per standing rule).
- Screener: snapshot gets `<metric>__badge` and `<metric>__null_reason` columns (same dynamic-column mechanism as
  `__formula_version`); filter default includes badged cells, an "as printed only" toggle excludes them; a cell in
  `included_in:<dp>` is excluded with that reason, never treated as zero (data_points.csv filter_note).

## 4. Migration (proposed, NOT claimed; needs the founder's typed words; claim in doc 53 first, next free is 0135)

`0135_shown_cell_badges.sql` (name proposed): (1) `cell_display_state` add `badge text`, `value numeric`,
`canonical_fact_id bigint` with CHECK `badge is not null = (display='SHOWN_VALUE')` and badge prefix in
BADGE_KINDS; (2) `metric_value` add `badge text` (nullable; null = all inputs as_printed); (3) view
`analytics.shown_cell` joining cell_display_state x canonical_fact x latest cell_proof, filtered as in section 2.
Depends on 0130 (applied) and 0133 (pending: `only_after_tax_disclosed` class must be live first). Snapshot columns need
no migration (runtime `ADD COLUMN IF NOT EXISTS`, `snapshot.py:93`). Rollback: drop view, drop the three columns.

## 5. File changes in order (each with the test that must fail without it; mutation-check each)

1. `metrics/registry.py`: `badge_for()` + test `test_registry_badge_for.py` (every data_points.csv step maps to its badge;
   a combined resolver row gives `combined:<label items>`; fails if badge_for returns as_printed for a DERIVED row).
2. `mapper/cell_display_state.py` + `mapper/top100_coverage.py`: write badge, value, canonical_fact_id; test
   `test_cell_display_state.py::test_shown_cell_has_badge_and_value` (fails without the new columns in `state_rows`).
3. Migration 0135 file in `pipeline/db/pending/` + CI replay test parsing the badge CHECK against `BADGE_KINDS`
   (fails if the lists drift).
4. New loader `mapper/shown_inputs.py::load_shown_cells(conn, company_id)` reading only `analytics.shown_cell`, returning
   the same shape as `calculate.py:_load_canonical_facts` plus badge/state; wire `provenance.py` rule (c) into it.
   Test `test_shown_inputs.py`: a DISAGREE cell, a HIDDEN_ROW cell and an OPEN cell are absent; NOT_PRESENTED-zero kept
   only for `zero_when_absent` (fails if the loader reads canonical_fact).
5. Calculators switch to the loader one file per commit: `calculate.py`, `ttm.py`, `expanded_metrics.py`,
   `price_metrics.py`; write `badge` and `is_null_reason=input_not_shown:...` into `metric_value`. Test per file:
   net_margin with a DISAGREE net_income yields null + reason, a `combined:` payables gives payables_days with badge
   (fails on today's code, which computes a value with no badge).
6. `apps/backend/company_page.py`: statement rows, periods, book value, public float from `shown_cell`; metrics carry
   badge; hidden rows/years dropped. Tests in `apps/backend/tests/test_company_page.py`: HIDDEN_YEAR column absent,
   HIDDEN_ROW row absent, OUT row absent, badge returned (each fails on today's query). Same for `routers/watchlists.py`.
7. `apps/app`: FinancialTable badge chip + R-page link; vitest + headless screenshot. Delete `lib/company/db.ts` SQL copy.
8. Screener (owned by the agent now changing `screener/*`; hand over, do not edit here): `resolve.py` returns badge,
   `snapshot.py` writes `__badge`/`__null_reason`, query schema gets the as-printed toggle; test: a badged metric
   is excluded under the toggle and an `included_in` cell never passes a `< x` filter as zero.
9. Certificate tie (#14): `display_cert.py` certifies `shown_cell` rows; end-to-end test: page cell == certified cell
   for 3 companies (fails if company_page reads canonical_fact).
10. Delete dead reads (`canonical_fact` refs in `apps/`); grep test `no canonical_fact under apps/backend` in CI.

## 6. Rollout

- Steps 1-4 change no shown value. Steps 5-6 behind a per-company flag (`shown_cell_path`, the ONE-PATH step 3 flag).
- Top 100 first, pilot 10 diverse companies (bank, insurer, REIT, utility, 6 general). Before switching a company, a dry-run
  diff report `data-team/strategy/shown-diff/<TICKER>.csv`: every page cell and metric whose value, badge or
  presence changes (old, new, reason, display/verdict), plus a per-company summary line (cells removed, metrics
  nulled, badges added). Switch only when every removed value has a reason in the evidence column; verifier draws 20
  random changed cells per company against the filing.
- Then all 100 in 4 shards max; then the scale ladder (500/1k). Cache: bump page cache key on switch (`cache.py`).
- Prerequisite: 139 DISAGREE + 414 UNCHECKED (SYSTEMS #11) become nulls with reasons on switch; report that count first.

## 7. Effort

| Steps | Size |
|---|---|
| 1-3 badge + display-state columns + migration file | ~1.5 days |
| 4-5 shown-input loader + 4 calculators | ~3 days |
| 6-7 company page, watchlists, frontend badge | ~2 days |
| 8 screener (other agent) | ~1 day |
| 9-10 certificate tie, deletions | ~1 day |
| Pilot 10 + diff reports, then top 100 | ~2 days |

Total about 10 working days; steps 1-4 can start now, 0135 waits for the founder's typed approval.
