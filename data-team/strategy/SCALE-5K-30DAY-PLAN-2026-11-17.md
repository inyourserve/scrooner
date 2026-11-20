# Scale plan: 5,000 companies in 30 days (data chief, 2026-11-17)

Measured on origin/main 09327b30 (2026-11-16 20:03Z) and one read-only DB connection (statement_timeout 30s). Labels: FILING-CHECKED / CODE-CHECKED (read in code or CI logs) / DATA-INFERRED (computed from repo data) / ESTIMATE (arithmetic on stated assumptions). There is no acceptable error rate. Every gate below needs zero observed wrong values; the statistical bounds are published measurements, not allowances.
## 0. Verdict

- **Throughput is not the constraint.** SEC traffic, DB size and Actions minutes all fit inside 30 days (section 2).
- **The per-cell path makes 30 days infeasible today.** Three reasons:
  - Residue is read by agents.
  - The rule-discovery curve has not bent (section 3).
  - The founder rule "full latest-10-K read per company" (2026-11-12) would mean 5,000 reads.
  - Resolver accuracy is unmeasured: the daily drill has never succeeded (runs 43808031421 failure, 43918576122 skipped).
- **30 days becomes feasible only if four things land by about day 7:**
  1. Residue is auto-classified, and an unresolved cell gets a visible, evidenced "not yet verified" state instead of a read. This is a novel definition, so it goes to FOUNDER-QUEUE.
  2. The predictor graduates per class, so reading becomes sampling (founder 2026-11-13).
  3. Pipeline O(N²) and git-size limits are removed (section 4).
  4. A measured accuracy gate replaces trust.
- **Without these, the honest 30-day target is 1,000 companies.**
## 1. Verified state (CODE-CHECKED unless marked)

| Fact | Value | Locator |
|---|---|---|
| Top-100 shown values | 41,757 of 43,890 = 95.14%. Open shown 2,133 at 93 companies (median 17.5, p90 45, max 77). 4 companies excluded | top100-coverage-summary.csv @cc516852 (2026-11-16 17:08Z) |
| Coverage trend | 96.58% (1,473 open) at 11-16 00:02, down to 95.14% at 15:00. The hourly export also published half-reloaded states: 0.0% at 06:54 and 41% at 08:34 | git log of the summary CSV |
| Certified | 3 with open=0: JNJ, GILD, STX. Registry: GILD and JNJ PASS; BA, MO and STX FAIL. MSFT certificate 11-14 | approvals/registry.csv |
| Certification draw | n=32 shown cells per company, checked against fsn.* (no SEC). With 0 errors the 95% upper bound is 8.94% per company. Target 0.10% pooled | CERTIFICATION-METHOD-2026-11-16.md l.8, l.18 |
| Rulebook | 256 rule rows. 78 have no test ("—"). Section 7 lists them | data-team/tags/RULEBOOK.md |
| Resolver tests in CI | Not gated. ci.yml runs only pipeline/tests and tests/. line_map tests run only in the manual tag-library-learn.yml | .github/workflows/ci.yml l.97-100 |
| Debt perimeter copies | At least 3 live: line_map/tools/total_debt.py, certification/display_cert.py:80 (DEBT_FACE_TAGS), mapper/concept_fallback.py:310. Older ones in slot_records and strategy/tools | git grep |
| Flow time per company | Chain about 8 min, of which about 5 min is a full top-100 coverage export repeated in every company job (06:57:45 to 07:02:47, company 5761). Median job 26.9 min and p90 37.5 min in a 43-wide run (43819808913), against 10.1 min in a 3-wide run | gh run view |
| Standard extract | 0 successes in its last 30 runs (5 failed, 2 cancelled). Run 43928679894 still running after 1 h 41 m on 8 shards for about 110 CIKs | gh run list |
| Resolver output in git | resolver-all110-2026-11-14.csv is 29.5 MB for 110 companies. That hits GitHub's 100 MB file limit at about 370 companies | git ls-tree -l |
| AUTO_LOOP fan-out cap | 256 companies per trigger | top100-auto-trigger.yml l.13 |
| SEC limiter | Per-process only. instance_evidence.py defaults to 0.34 s (about 2.9 req/s, above the founder's 2 req/s total). There is no shared budget across processes | instance_evidence.py l.22-25 |
| DB | 72 GB. core.fact 33 GB (65M rows, about 4,469 companies by pg_stats). fsn 20 GB (about 1,000 companies, 45,883 filings, 11,388 annual). analytics 15 GB. cell_proof 1.3 GB (848k rows). 34 of 90 connections in use. core.company has 5,286 rows | read-only query 2026-11-16 |
| Docmaps | 110 docmaps (hand reads) and 114 fix files. The flow loads them per company | data-team/companies/reads |
## 2. Throughput math for 5,000 companies
**SEC, 2 req/s total = 7,200 req/h. Bulk-first.**

| Source | Requests | Bytes | Hours |
|---|---|---|---|
| FSN notes sets, 2014q2 to 2020q3 quarterly (26) plus 2020-10 to 2026-10 monthly (73) | 99 | about 430 MB per quarter, about 21 GB total (mind entry, CODE-CHECKED). FSN covers all filers, so 5,000 costs the same downloads as 1,000 | under 0.1 (bandwidth-bound) |
| companyfacts.zip and submissions.zip (collector already bulk) | 2 | about 1-2 GB (ESTIMATE) | about 0 |
| Raw 10-K cache per filing: index.json, FilingSummary.xml, Financial_Report.xlsx (every R page in one file), xbrl.zip | 4 x 56,700 = 226,800 | MSFT FY2020 (FILING-CHECKED, 0001564590-20-034944): 72 KB + 177 KB + 415 KB. About 0.7 MB per filing, about 38 GB upper bound | **31.5** |
| Primary 10-K HTML, fetched lazily, only for text-class residue (57 of 713 fix rows, 8%, had no R page) | about 4,500 (ESTIMATE) | MSFT 6.6 MB | 0.6 |
| Residue as read today, uncached | at least 421 distinct R pages across 55 companies, so at least 38,000 for 5,000 | n/a | at least 5.3 at 2 req/s, about 23 at the agents' 1 per 2.2 s |

- 56,700 = 11,388 annual filings / 1,005 companies x 5,000. This is an upper bound; younger companies have fewer years.
- **Total: about 33 SEC-hours, 4.6% of the 720 hours in 30 days.** The nightly incremental adds about 55 filings a day off-season.
- An R-page-by-R-page cache (118 R pages in MSFT FY2020) would need 6.7M requests, which is 39 days. **Never do that.**
**DB.** ESTIMATE, linear in companies:
- fsn grows from 20 to about 100 GB if every form is loaded, or about +20 GB if companies 1,001-5,000 load annual forms only. The resolver reads only 10-K, 20-F and 40-F.
- cell_proof grows to about 2,000 cells x 5,000 = 10M rows, about 15 GB.
- core.fact is already about 4,469 companies (about +4 GB).
- Total about 120-190 GB. Supabase Pro disk is fine.
- **Compute is the risk.** A 30 s count(distinct) on cell_proof timed out. Raise to the planned Medium tier before rung 2,000.
- Connections: the flow holds one connection at a time per job. Width 20 means at most about 20-40 connections, inside the 70 load budget.
**Actions.** The repo is public, so standard-runner minutes cost nothing. The user-owned Free plan caps concurrency at 20 jobs (ASSUMED from plan type).
- With the export per company: about 3.3 min per company (measured chain without the export). 5,000 companies is 16,500 runner-min, **13.8 h wall at width 20**.
- As built today: 27 min x 5,000 = 135,000 min. The export would also scale O(N²), with each job exporting all N companies. Not runnable.
- Extract: ESTIMATE of at least 7.3 connection-min per company from the in-flight run. 5,000 companies is about 610 connection-hours, **about 51 h at 12 shards**.
## 3. Residue decay (DATA-INFERRED from 713 rows in the 55 open-shown-fixes/*-2026-11-17.csv)
**Outcomes.** VALUE 392, HIDE 200, RULE 121.
- Every row sat on an OPEN cell: REASON 370, UNCHECKED 81, HELD 81, BLANK 70, DISAGREE 62, hidden 49.
- 39 VALUE rows differ from the stored value. Examples: ACN shares are Class X counts (1,000x off), PFE revenue 2021, MPC gross profit 2018, QCOM sign.
- **No fix touched a SHOWN PROVEN cell, so this exercise says nothing about the accuracy of shown values.**
**How the 713 rows were closed:**

| Closed by | Rows | Share |
|---|---|---|
| (A) standard hide class (only_combined, absence, before_first_10k, never_reported, not_in_template) | 174 | 24.4% |
| (B) rule key shared by 2 or more companies (14 keys) | 79 | 11.1% |
| (C) single-company rule proposal (101 keys) | 361 | 50.6% |
| (D) one-off value read, no proposal | 97 | 13.6% |
| Other | 2 | 0.3% |

- **General: 35.5% (A+B). One-off or unproven: 64.2%.**
- 89 rows (12.5%) cite an existing RULEBOOK id: the resolver had the rule and did not fire it.
**Projection.** Rule-key accumulation over 2,000 random company orders fits Heaps' law K = 2.8 n^0.94. Nearly linear, so the curve has not bent.
- New keys per new company: 2.0 at 100, 1.8 at 500, 1.6 at 5,000. This is an upper bound, because free-text names split one rule into several.
- At 3.6 cells per new key plus 1.8 one-off reads per company: **about 8 cells per new company need new knowledge**, against 22 open per company today. That is about 38,000 cells at 5,000 companies.
- At today's agent pace (about 713 rows a day) that is about 54 days. **This is the binding infeasibility.**
- Remedies: canonical rule keys (one RULEBOOK id per proposal), to measure the true curve, and auto-classification of the tail.
## 4. Architecture: humans and agents off the per-cell path (dependency order)

1. **Remove scale breakers (Engineering).**
   - The flow exports only its own company. The hourly export stays global and writes atomically: temp file, then rename, publish only a complete set.
   - Resolver output goes to per-company files or a DB table, not one CSV in git.
   - Lift the AUTO_LOOP cap of 256 by batching.
   - Make the standard extract succeed: fix the failures in its last 30 runs.
2. **One SEC gateway (Engineering).** A single token bucket at 2 req/s, shared across all jobs through a DB advisory-lock row or one fetcher job.
   - Raw cache: a Supabase Storage bucket with zstd-compressed, hash-addressed files under (cik, accession, filename). The collector rules hold: lossless, immutable, no parsing.
   - Every residue reader, text_disclosure.py and instance_evidence.py reads the cache first. A cache miss queues a fetch; readers never call sec.gov directly.
3. **Mined-rule pipeline (Tag Expert, Engineering).** Fix files gain a required rule_id column. A proposal is either an existing RULEBOOK id or a NEW id with a fixture taken from the cited row.
   - `mine_rules.py` groups rows by rule id and emits a test stub per id, where the cited cells are the expected values.
   - A rule ships only with its code, a mutation-checked test and a RULEBOOK row (already the RULEBOOK §1 contract).
   - Add a test that replays every committed fix row against the resolver (extend test_resolver_vs_served_fixes.py). A fix row the resolver contradicts fails CI.
4. **Auto-classification of residue (Engineering).** For each OPEN cell, from the cached xlsx, FilingSummary and the FSN calc tree, emit one class:
   - HIDE: standard class plus evidence. This handles the 24% in (A).
   - RULE-MISS: an existing id should have fired. This handles the 12.5%.
   - SPLIT-FROM-NOTE, TEXT-STATED, or NOVEL.
   - Only NOVEL reaches an agent, and agents get batches by class, not by company.
   - Unresolved cells get the evidenced state "not yet verified (class, locator)". **Founder definition call.**
5. **Measured accuracy gate (Verifier, Tag Expert, Ritwik).**
   - Gate merges on all 139+ resolver tests, so the 78 untested rules get tests or are deleted.
   - The daily blind drill on 20 unseen companies runs green every day.
   - Graduation per class and per template group: at least 200 unseen companies, 0 errors in 200 (one-sided 95% upper bound 1.5%). Demote on any sampled miss.
   - **A semantic Verifier sample.** certify_display checks a value against the filing's own FSN data, so it cannot catch a correct number on the wrong line, such as gross profit served as revenue (resolver .73). The Verifier sample does check that: right line for the concept, plus identity checks (revenue - COR = GP; assets = liabilities + equity; CF section sums).
6. **Certification by census plus sample (Ritwik).**
   - Census on every shown cell: proof verdict, identities, debt perimeter from one shared module (collapse the 3 copies).
   - Per-company draw of 32, pooled across the rung.
   - Semantic sample stratified by class and by template group.
   - A rung passes only with 0 wrong.
## 5. Ladder (zero observed wrong at every gate; bounds are what a clean sample proves)

| Rung | Days (from 11-17) | Go criteria | Clean sample proves |
|---|---|---|---|
| 100 | D0-D7 | open=0 for all 96 template companies. Census clean. 3,072 FSN draws plus a 300-cell semantic sample with 0 wrong. Resolver tests gate CI. Drill green 3 days running | pooled at most 0.10%, semantic at most 1.0% |
| 500 | D7-D12 | Items 1-4 of section 4 live. Novel cells per company at most 3 (measured). Graduated classes at least 50% of cells. 0 wrong in 400 x 32 plus 300 semantic | at most 0.023% / 1.0% |
| 1,000 | D12-D17 | Cache complete for ranks 1-1,000. Extract under 6 h. 0 wrong. Every miss so far closed as a rule with a test | at most 0.012% / 1.0% |
| 2,000 | D17-D23 | FSN plus cache loaded for ranks 1,001-2,000 (about 6 SEC-hours). DB on Medium compute. New groups (small banks, BDCs, REITs) with at least 200 companies graded, or kept on reading | as above, per new group |
| 5,000 | D23-D30 | Micro-cap and 20-F tail. Nightly incremental keeps certified companies green. Any group under 200 companies stays read or hidden with a reason | publish per group |
**No-go at any rung:** one wrong shown value. Stop, root-cause the class, fix by rule plus test, then re-sample the rung.
## 6. Next 72 hours (owner, done-check)

1. **Engineering.** Flow exports one company; the hourly export becomes atomic. Done-check: a 3-wide run has median job time 4 min or less, and no half-state commits for 24 h.
2. **GitHub ops.** Add line_map/tools/test_*.py and tags/library to ci.yml. Done-check: a PR that breaks a rule turns CI red (mutation-checked); main stays green.
3. **Engineering.** Get one standard extract green for the 110. Record the minutes per company. Done-check: a run id with conclusion success, plus a timing row in this file's successor.
4. **Engineering.** SEC gateway plus raw cache (Storage bucket) at 2 req/s total. Done-check: ranks 1-100 cached (about 1,140 10-Ks, about 4,560 requests, about 0.6 h). text_disclosure and instance_evidence read 0 bytes from sec.gov on a rerun.
5. **Engineering.** Resolver output split per company or into a table. Done-check: no file over 10 MB under line_map; AUTO_LOOP consumes the new format.
6. **Tag Expert.** Map the 115 free-text rule keys to RULEBOOK ids. Add the rule_id column. Done-check: every 11-17 fix row carries an id. Recompute the Heaps exponent and report it.
7. **Tag Expert.** Fix the 89 rule-miss rows, the 39 value mismatches and the ACN shares class. Done-check: those cells are PROVEN in coverage, and the replay test passes.
8. **Verifier.** 300-cell semantic sample, stratified over shown PROVEN cells in the top 100. Done-check: a committed answer key, with wrong count and per-class results.
9. **Ritwik.** One debt perimeter module used by the resolver, certify_display and the mapper. Write tests for the 78 untested rules, or retire them. Done-check: grep finds one definition; RULEBOOK §7 is empty or each entry justified.
10. **Engineering and Tag Expert.** Daily drill green 3 days running, with per-class blind accuracy published. Done-check: 3 consecutive successful runs of pipeline-daily-drill.yml, plus a per-class table.
**Decision to queue (FOUNDER-QUEUE).** The display state "not yet verified (class, locator)" for unresolved cells, and whether the full-10-K-read requirement becomes graduation-based sampling past rung 1,000.
## 7. Assumptions and untested scope

- Not measured:
  - FSN load time for new companies.
  - Contention at width 20 after the export fix.
  - Real 10-K count for ranks 1,001-5,000.
  - Supabase compute tier (90 max_connections suggests Small).
- The Mac had 2.2 GiB free on 2026-11-20 and must not hold the cache.
