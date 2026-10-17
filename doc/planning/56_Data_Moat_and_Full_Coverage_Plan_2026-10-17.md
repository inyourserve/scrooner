# Data moat and full coverage plan (2026-10-17)

Status: Draft for founder decision. Evidence is from live queries and one downloaded SEC data set on 2026-10-17. Nothing in this plan is built. It slots into the lanes in [doc 53](53_Multi_Session_Collaboration_Plan_2026-10-13.md) and does not replace docs 41/42/50/52. Claim migration numbers in doc 53's ledger before writing any file.

## 1. Goal, stated so it can be tested

Every (company, line, period) cell for an active US 10-K filer is in exactly one of three states, each traceable to a filing:

- **VALUE**: a number with its source filing, line and formula version.
- **PROVEN ABSENT**: the filing's own statements do not present that line (evidence: accession, statement, label).
- **UNKNOWN**: neither of the above. This is the only state that counts as a defect.

**Moat KPI = UNKNOWN cells divided by applicable cells, driven to 0.** "Coverage %" stops being the headline, because 100% of a narrow model proves little.

Why this is a moat: SEC data is free to everyone. What is hard to copy is breadth (hundreds of standardized lines, not 50), industry-correct statement templates, complete quarterly history, and a per-cell audit trail with evidenced absences.

## 2. Measured baseline (live, 2026-10-17)

| Finding | Evidence |
|---|---|
| The pipeline does not drop mapped data | Only 61 cells have a mapped tag filed but no value (of 107k empty concept cells) |
| Vocabulary is tiny | About 90 of 12,372 SEC tags are approved, provisional or preference. 64% of `core.fact` rows (27.5M of about 43M) sit under unmapped tags. 740 unmapped tags are filed by 500+ companies each |
| Model is narrow | 78 concepts (about 50 distinct lines once `_resolved` copies are removed). Sized to 18 locked screener metrics |
| One template for everyone | 1,339 of 4,567 companies with revenue have no cost of revenue or gross profit: Financials 560, Healthcare 247, Real Estate 159. They file G&A (647), labor (506), professional fees (388), occupancy (335), loan-loss provision (256), none of which has a concept |
| History is incomplete | `period_gap` has about 254k cells: `no_mapped_tag` about 75k, `no_line_item_filed` about 55k (over-claims), Q4/quarter not derived about 57.6k, conflicts about 10k, `not_in_sec_feed` about 23k |
| Q4 gaps are mostly input conflicts, not missing arithmetic (corrected 2026-10-17) | A first estimate that about 60% were plain arithmetic was WRONG: it counted display-layer values that had been picked from conflicting duplicates. Remeasured on raw `core.fact` for 1,200 sampled `q4_not_derived` cells: 3% have a single value for both full year and 9-month YTD with authoritative inputs; 67% have more than one distinct value for the same period (restated or as-filed vs later filings, sometimes opposite signs); 30% have a full-year fact but no 9-month YTD fact; 1% have no full-year fact. Example: company 8 FY2023 tax has 3 copies of the 9M and Q1 values that differ by 5-10x, and only FY is authoritative |
| Measurement is stale | Last `coverage_snapshot` is 2026-10-13. `company_data_point_coverage.gap_reason` is empty in the live table. "Nothing relevant filed" means none of OUR tags were filed |
| Universe is slightly dirty | `real_operating_company` (4,815) still holds 13 FPI-only filers and 83 with no 10-K |
| Capacity is real | Database is 46 GB (core 34 GB, analytics 12 GB). A bigger catalog must store compact evidence, not raw copies |

### What SEC's Financial Statement Data Sets add (checked on 2025q4)

Free, 66-79 MB per quarter, one request each, reachable with our declared User-Agent. Files: `sub` (filing), `pre` (every presented statement line: statement, order, tag, label, negating flag), `num` (values, including a `segments` dimension column).

- 5,631 10-K/10-Q filings, 520,030 face-statement lines (BS/IS/CF), avg 92 lines per filing.
- **Only 9.2% of face lines are company-specific tags.** About 90% are standard us-gaap tags.
- 3,720 distinct standard tags appear on faces; **788 appear in 50+ filings; 342 in 200+.** A catalog of about 350 lines covers most of what filers present. That is the realistic target, not 78 and not 12,000.
- About a third of the 70 most common face lines have no concept today: retained earnings, common and preferred stock value, shares issued/authorized, par value, APIC, weighted-average shares (basic, diluted), operating lease asset and liabilities, interest and income taxes paid, other non-current assets and liabilities, cash-flow prepaid change.

## 2b. What already exists, and how this plan reuses it

Source: `doc/data-moat/SYSTEMS.md` plus live counts on 2026-10-17. This plan extends these; it builds no parallel systems.

| Already built | State | Used by |
|---|---|---|
| Detection and verification: Data Sanity (yfinance), SEC Frames self-consistency (99.69% exact on 28,187 pairs), time-series checker, period completeness, freshness, unified incident view, verifier | Running; nightly runs unstable | W0, W1 (as acceptance checks) |
| Tag library (12.4K tags, `company_concept_lineage`), candidate library, `gap-tags <concept>` lead ranking | Built | W3 (lead source) |
| Data Truth Layer: `tag_concept_verdict`, `company_data_finding`, `company_tag_preference` | 102 verdicts recorded (73 approved); 429 company preferences; about 51k open findings (pipeline_bug 27.9k, data_limit 19.4k, filer_error 4.1k) | W3 (decision record), W0 (reason buckets) |
| Filing-line evidence layer (`company_filing_line_evidence`, 46.8k rows) | Built; HTML-based | W2 extends it with exact FSDS lines |
| Concept fallback (`*_resolved`), tag investigator, component total debt | Built | W3, W4 |
| Read-only SEC XBRL Tag Expert agent spec (`.github/agents`, `doc/tag-agent`) | Recommend-only by design; a human approves | W3 workflow |
| Cockpit admin app (`apps/admin`, uncommitted) | In progress | Review queue UI for W3 |

**Consequence:** detection is largely automated. The binding constraint is **decision throughput**: 102 recorded tag verdicts against 740 unmapped tags used by 500+ companies, and about 51k open findings. W0 therefore repairs and extends `company_data_point_coverage` and the existing evidence table (adds the three-state field) instead of adding a new ledger, and W3 runs through the verdict workflow with the tag-expert agent doing volume and a named human approving.

## 3. Workstreams

Order matters: W0 first (so progress is measurable), then W1 and W2 in parallel (different tables, different lanes), then W3.

### W0. Truth ledger and measurement (first, about 2-3 days)
- Nightly snapshot must write every day. Fail the run loudly if it does not. Persist `gap_reason` in the served table, and rerun the matrix then snapshot in the same job.
- Add filer-type populations: 10-K filer, FPI, pool/trust, non-operating. Exclude FPI and pools from operating denominators. Fix the 96.
- Add the VALUE / PROVEN_ABSENT / UNKNOWN state and evidence pointer to `company_data_point_coverage`, fed by `company_filing_line_evidence` and `period_gap` (no new parallel table unless those cannot carry it). Start at concept and fiscal-year grain; extend to quarters in W1.
- Report the KPI (UNKNOWN / applicable) on `/app/data-coverage`, overall and per top-100/1,000/2,000 band.
- Acceptance: three consecutive nightly snapshots; KPI number published; every UNKNOWN cell has a queryable reason bucket.
- Lane: A (scrooner-98) with B for evidence. Do not change how `has_value` is set (doc 53 rule 2).

### W1. Period completeness (parallel, about 1 week)

Evidence and sample limits: [learning 2026-10-17](../data-moat/learnings/2026-10-17-coverage-rebuild-atomicity-q4-conflicts-and-nonadditive-derivation.md). Updated census (3,587 cells): about 2% clean, 65% conflicting with no authoritative copy, 31.5% no 9-month source. The latest-filed resolver covers only 6 full-year tags; extending it (after a Frames check) plus same-vintage pairing is the main lever.
- The existing deriver (`normalizer/derived.py`) already handles both the Q1+Q2+Q3 chain and the 9-month YTD path, and correctly refuses non-authoritative inputs. The problem is upstream: duplicate conflicting values for the same period. W1 is therefore conflict resolution first (restated vs as-filed basis, sign conflicts, which filing governs), then derivation on the cleaned inputs.
- Cases with no 9-month fact (about 30% of the sample) need a source: Q3 10-Q YTD columns from the filing, which Company Facts may not carry.
- Keep one rule from the data-team pack: never mix a restated annual input with an unreconciled original 9-month input. Mark basis explicitly.
- Mark derived cells `is_derived`, keep `source_fact_ids`.
- Reconcile derived Q4 against reported values where a company files them, and against the FSDS `num` table.
- Fix conflict resolution (`conflict_material`, `conflict_split`) with recorded rules.
- Acceptance: every `q4_not_derived` cell carries a precise cause (basis conflict, sign conflict, no YTD source, derivable); the derivable and resolved-conflict subsets are filled; a 100-company hand check of derived Q4 values against filings.
- Lane: F (scrooner-2b already owns Q4/YTD analysis). Hand it the sample above.

### W2. Standard line catalog from SEC face statements (parallel, about 1-2 weeks)
- Ingest FSDS `sub` + `pre` (and `num` selectively) for 10-K and 10-Q filings of our active companies. Download once per quarter (about 65 requests back to 2009; far lighter than per-company calls). Keep zips outside the database.
- Store compact evidence only: per filing, per face line: statement, order, tag, label, negating, custom flag. Limit to the latest 3 fiscal years of 10-Ks plus the latest 10-Q per company first (about 1.5M rows). Size-check before loading; the database is 46 GB.
- Use it to (a) replace the HTML-based applicability probe with exact line evidence for every company, (b) rank candidate catalog lines by number of filers, (c) reconcile `core.fact` against SEC's own published normalization of the same filings (independent integrity check).
- Acceptance: for each sampled 10-K, every face line is either mapped to a catalog line or listed as unclassified with a reason; reconciliation mismatch rate published.
- Lane: B (applicability/evidence). Reuse `company_filing_line_evidence` columns where possible instead of a parallel table.

### W3. Canonical model v2 with industry templates (after W0/W2, ongoing)
- Define statement templates: Industrial, Bank/Insurance, REIT, Pre-revenue biotech, Utility, plus a Core set every filer has. Each line declares which template(s) it belongs to; applicability comes from the template, not from a per-metric guess.
- **Wave 1 (low risk, one-to-one standard tags):** the roughly 24 unmapped common face lines listed above, balance-sheet equity detail, share counts, leases, taxes and interest paid, other assets/liabilities.
- **Wave 2:** nature-of-expense and bank lines: G&A, labor, professional fees, occupancy, loan-loss provision, interest income and expense by type, deposits, loans. Align with [doc 33](../execution-plans/33_Scrooner_Sector_Specific_Metrics_Plan.md) and the FDIC source in doc 32b.
- **Wave 3:** company-specific (extension) tags, resolved from face position, label and calculation relationships. Only about 9% of face lines, so do it last.
- Standing gate for every mapping: full-population coexistence check (a 5-row sample is not evidence; see the 2026-09-12 learning). Combined lines (for example "payable and accrued") are never mapped as the plain line.
- Acceptance per wave: lines added with coexistence results recorded; no regression in sanity checks; coverage ledger shows UNKNOWN falling.
- Lane: A/C/F by area; coordinate migrations through doc 53.

### W4. Metrics that degrade honestly
- Replace all-inputs-or-null with ordered input chains and a `partial` state that names the missing input (for example EBITDA with D&A from cash flow when absent on the income statement).
- Bind metrics to templates so gross margin is not demanded from a bank; give Financials and REITs their own metric set (doc 33).
- Acceptance: Piotroski, cash conversion cycle and EBITDA metrics report value / partial / not-applicable with reasons; top-1,000 launch-readiness rules in doc 53 pass for Financials.

### W5. Segment and geography data (later)
- FSDS `num.segments` carries the dimensional data the Company Facts API strips. Feeds [doc 37](../scoping/37_Scrooner_Segment_Revenue_Scoping.md). Not required for coverage; it is a differentiator. Start only after W0-W3 Wave 1.

## 4. Targets (proposed; founder to confirm)

| Band | Target on applicable cells (VALUE + PROVEN ABSENT) | Target UNKNOWN |
|---|---|---|
| Top 100 | 99% | under 1% |
| Top 1,000 | 97% | under 3% |
| All active operating companies | 93% | under 7%, falling each month |

## 5. Risks and constraints

- **Database size (46 GB).** Store evidence compactly; measure before each load; drop superseded rows. Do not mirror FSDS wholesale.
- **Multi-session collisions.** Shared files `coverage_matrix.py`, `coverage_snapshot.py` and the migration ledger follow doc 53. `ListAgents` before heavy jobs; one SEC fetch process at a time.
- **FSDS lag.** Published about 2-3 weeks after quarter end. It supplies catalog, evidence and reconciliation; the live path for new filings stays companyfacts and submissions.
- **Evidence is not proof.** A line absent from face statements may still be disclosed in the notes (the earlier probe saw 14-34% of present values with no face line). Label such cells PROVEN ABSENT FROM FACE STATEMENTS and keep a notes-lookup path.
- **Unverified here:** the full-population Q4 breakdown (sample of 1,200 only); FSDS coverage for older years and for our exact company set; the per-quarter size of compact evidence. W1 and W2 each begin with a measurement step for these.

## 6. Decisions needed from the founder

1. Confirm the three-state KPI (UNKNOWN to 0) as the headline instead of coverage %.
2. Confirm the targets in section 4.
3. Approve W2 ingesting FSDS for the latest 3 fiscal years first, with a size check.
4. Decide template scope for W3 (suggested first cut: Industrial, Bank/Insurance, REIT, Pre-revenue biotech).
