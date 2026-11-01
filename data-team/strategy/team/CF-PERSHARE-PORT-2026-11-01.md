# Cash-flow and per-share port to the FSN store: findings so far (2026-11-01)

For: Dhairya. Status: **investigation done, port not built yet.** Nothing changed in code, data or the database. This note says what exists, what is missing, what blocks the regression gate, and the plan.

Task: port the cash-flow rules (CFO, dividends paid, buybacks) and the per-share rules (EPS basic/diluted, shares, DPS) into `fsn.concept_rule` seeds and per-company readers, with a regression gate that reproduces their last Verifier-passed outputs. Pattern: the income-statement port, `origin/work/income-statement/fsn-store` 6f90173.

## 1. In plain words

- The cash-flow lane's rules are in one script, `cf_family_replay.py` (branch `work/cashflow/v2-emit` 2e061bc, **not on main**). It reads the whole cohort's FSN files at once. To port it, it must read one company directory (`companies/<cik10>/`, FORMATS-v1) and give the same answer.
- Only the simple tag rules fit the seed format. Most of the lane's logic is label regexes (for example "repurchase" vs "tax withholding", "preferred" vs "common" dividends). The seed format has no field for a label regex, so those rules stay in a ported detector, as the income-statement lane did.
- Some seed rows already exist. The income-statement port wrote 9 cash-flow rows (capex and D&A only) and 3 per-share rows (the EPS tags). **CFO, buybacks, dividends paid, shares and DPS have no seed rows yet.**
- **The main blocker is the regression gate's input data.** The run 7 outputs (CFO 37,121 / buybacks 23,989 / dividends 24,610 publishable) and their inputs are on the dev Mac scratchpad and in the `fsn-notes` bucket. This cloud session has no Supabase credentials and no `pipeline/.env`, so it cannot read either. sec.gov is reachable (one FSN quarter zip is about 430 MB).

## 2. What the cash-flow code does today (source: `cf_family_replay.py` @ 2e061bc)

Inputs are three cohort files: `cf_face_rows.py` (cash-flow face lines), `cf_num_rows.py` (USD values, qtrs 1-4, no dimension, no co-registrant), `cf_cal_rows.py` (cash-flow calc arcs). A cell is (company, period end, months). The value comes from the original filing. Gates, all on one accession: face column, cash-flow identity (change in cash = signed children), section total ties, stub column (FSN `durp`), and later restated copies must agree, otherwise `restated_copies_disagree`.

| family | how a line is chosen | main holds and exclusions |
|---|---|---|
| CFO | `NetCashProvidedByUsedInOperatingActivities`; else a custom operating total; else the continuing-operations line only when no discontinued operating line is printed | `cfo_total_not_printed` (never summed), identity and section gaps |
| Buybacks | financing lines that repurchase common shares, summed | founder ruling 2026-11-04: tax withholding, excise, SBC plan, option exercise, subsidiary and share-swap lines are excluded with a reason; combined, net, unresolved, two repurchase lines and sign-unclear are held |
| Dividends paid | financing lines that pay common dividends, summed | preferred, NCI and standalone dividend-equivalent lines excluded; combined, net, partnership units and unresolved held |

**"Dividends and dividend equivalents" is already counted as common** in `dividend_class` (an "equivalent" label is excluded only when it does not read "dividends and (dividend) equivalents" or "dividends, including"). This matches your rule; it is still listed as "not yet ruled" in the scrooner-28 handoff, so the founder ruling should be recorded in doc 02.

Run 7 summaries are committed in `pipeline/scripts/slot_records/results/cf_run7/*_summary.json` on `work/cashflow/v2-emit`. The per-cell files are not.

## 3. Per-share (sources: `eps_fsn_scan.py` on main; `share_basis.py` on `work/cashflow/split-release-2` db1948f)

- **EPS is never derived.** `eps_fsn_scan.py` only takes filed 3-month values (all filed copies agree within 0.005, else hidden). It reads the whole bucket with Supabase credentials, so it needs the same one-company reader. Family C (`work/per-share/eps-never-derive-rebased`) removes derived EPS cells.
- **Q4 DPS = FY − 9M on one share basis only.** This is in `share_basis.py` on `split-release-2` (`load_held_basis_stale`, around line 3429): derived DPS is dropped when the held share basis is stale. That branch is **not on main**; the port must take the rule from there, not from main.
- Shares (weighted average basic/diluted) have no seed rows and no lane reader in either branch I read. I still need to confirm the canonical concept names in `analytics.canonical_concept` before seeding.

## 4. Verifier-passed cells usable as gate fixtures (FILING-CHECKED)

| report | cells |
|---|---|
| VERIFY-CFO-BUYBACKS-RUN2-2026-11-01 | CFO 15 right (DVN, LPLA, MKSI, ALB, CSX, FTV, RJF, LKQ, NBIX, GM, SO, PEP, TXNM, AEE, AXS) + 2 stub holds |
| VERIFY-BUYBACKS-RUN3-2026-11-01 | buybacks 20 (incl. ROST x3 held, LDOS combined, AAON sign_unclear, FIS unresolved) |
| VERIFY-BUYBACKS-R2-2026-11-04 | 6 of 6 under the founder perimeter ruling (EMR, GPN, GRMN, 790051, 1581280, COIN) |
| VERIFY-EPS-FAMILY-C-V3-2026-11-02 | EPS 15 of 15 |
| VERIFY-SPLIT-RELEASE-2 / -HELD-2026-11-04 | DPS and the held-basis rule |

No Verifier report for **dividends paid** exists yet. Its gate can only show "same output as run 7", not "Verifier-passed".

## 5. Plan (same shape as the income-statement port)

1. Make `cf_family_replay.py` importable (functions per company), cohort mode byte-identical. Add `fsn_company_cf.py` that reads one company directory into the three input shapes.
2. Seeds: `cf.jsonl` gets CFO, buybacks and dividends std_tag rows plus demote rows for the excluded tags; `per_share.jsonl` gets DPS and shares rows; every regex rule goes in `cf_pershare_not_extracted.md`.
3. Gate A (CI, no network): fixture company directories built from the real FSN rows of the Verifier-drawn accessions (fetched once from sec.gov at <= 4 req/s, committed small); the ported reader must give the Verifier's verdict and value for each cell, and cohort mode must equal company mode.
4. Gate B (needs the bucket; run on the Mac or in Actions with secrets): the full run 7 replay, company mode vs cohort mode, per-cell identical. I will commit the script and the command; **I cannot run it from this session.**

## 6. What I need from you

1. Run gate B, or give this session read access to `fsn-notes` (SUPABASE_URL and a key in the environment's secrets).
2. Confirm I should take the Q4 DPS rule from `split-release-2` although it is not on main, or say which branch lands first.
3. A Verifier draw on dividends paid run 7, so that family has a Verifier-passed baseline.
