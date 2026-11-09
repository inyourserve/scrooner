# Ruling: FSN done-gate criterion 4 (Ritwik (cloud), release approver, 2026-11-09)

For Dhairya (session_01GLmSDyzegqZw4JqC91z7XH). I could not deliver this with send_message (`elevated_session_untrusted_device`), so please relay it.

## Decision
Option 1 is **APPROVED by me as approver, with conditions**. Criterion 4 is checked per (company, data point). Criteria 1, 2 and 5 stay per company. Criterion 6 stays as it is, with restore by company.

**Authority.** This changes a recorded founder decision. Doc 02, "Founder decision of 2026-11-01: company-wise FSN statement store", item 5, says "A company is written only when all seven completion conditions in design §5 hold." Release case §5 #2 also names the founder as the decider. So my approval is necessary but not enough: the founder must confirm per-data-point writing in typed words. The words that authorize the next select_write can do it, if they say so explicitly. Until then, keep per company.

**Why I approve.** Per company is not the more conservative option today. 960 minus 13 companies keep all of their old-mapping rows, so the old values are served everywhere. Per pair only replaces old rows where a data point is proven complete. Certification is unchanged: each company still needs every template cell valued or reasoned. So the "no old-table fallback" rule (2026-11-04) is not loosened: an unwritten pair simply hasn't been switched yet. It is not a fallback.

## Conditions
- **C1. Unit = (company, data point), all or nothing.** A pair is written only if:
  - (a) the company passes criteria 1, 2 and 5;
  - (b) the pair has 0 reasonless gap keys;
  - (c) the pair has at least one expected key with a cell (valued or reasoned). Rule (c) stops a pair from passing because it is empty; `shares_outstanding_resolved` emits nothing (release case §6).

  Never write some keys of a data point and not others. The loader deletes old rows per (company, concept) (`cell_loader.py` ~l.954), so writing part of a data point would turn old values into reasonless blanks.
- **C2. Hold guard.** A pair whose new cells have 0 values while the before-image had valued rows for that pair is held and listed. It is likely a mapping miss, not a real absence. The dry run must also report, for each data point, the valued→blank transitions with their reason classes. I review that table before dispatch.
- **C3. "Current rows"** means the old canonical_fact rows exactly as they are, untouched. Those pairs are not written and not certified, and they count against the company in not_done and on the scoreboard. A data point whose old values are known to be wrong (task board A8: INTC/HD/AAPL/GE D&A, GE capex) is no reason to write a pair that fails the gate. Fix it and reload.
- **C4. cell_proof scope.** It must cover every written pair of every company with at least one written pair, not just the fully done companies. If a company has a served DISAGREE, restore that company's whole written scope from the before-image (`restore_company_ids`, as today). The restore stage needs the founder's words.
- **C5. company_value_owner (0119) must stay empty while writes are per pair.** It is keyed per company. One owner row would freeze the company's unwritten data points against the nightly. Written cells are already protected per cell through `slot_protected_cell` (0113). A future ownership table per (company, concept) needs its own migration number (doc 53) and the founder's words.
- **C6. `dividends_per_share_resolved` stays out** until the Q4 FY−9M route checks the same share basis (split guard). Founder ruling 2026-11-04 item 2 requires that basis, and release case §6 shows the check is missing. Per-share derived cells must also count toward criterion 5.
- **C7. Fresh cohort dry run before any dispatch,** on main + PR #4 + PR #6 with the new gate. It must report:
  - (i) pairs passing, per data point;
  - (ii) companies with all pairs passing;
  - (iii) the C2 table.

  Then I clear the data_points list, and the founder authorizes the write.
- **C8. Total debt and total liabilities stay out** (seed defect, release case §2/§3a).

## Code change needed (builder, then Verifier)
1. `pilot.done_gate` returns `{company_id: {"company": [failed crit 1/2/5], "data_points": {dp: [failed reasons]}}}`. It applies C1 rule (c), which needs the expected-key count per data point.
2. `jobs/fsn.py done-gate`:
   - writes `done_pairs.tsv` (company_id, data_point);
   - keeps `done_companies.txt` (meaning: all listed pairs pass);
   - writes `not_done.json` per pair;
   - echoes "N pairs of M; K companies fully done".
3. `pipeline-fsn-write.yml` filter (~l.179-196): keep a row when (company_id, data_point_name) is in done_pairs. The before-image and the cell_proof input cover every company with any written pair.
4. The C2 hold guard reads `out/before_image`.
5. Tests, run the way CI runs them and mutation-checked (they must fail when the gate is per company and when rule (c) is removed):
   - a pair passes or fails on its own;
   - an empty pair is rejected;
   - a company that fails criterion 2 writes nothing;
   - the filter keeps only done pairs.
6. Update design §5 and doc 02 only after the founder's words.

## Evidence (origin/main, 2026-11-09)
- `pilot.py:510-539`: criterion 4 counts a company's gaps over all listed data points.
- `pipeline-fsn-write.yml:166-199`: the filter keeps rows where data_point is in allowed AND company is in done_companies.
- `cell_loader.py`:
  - ~954: delete scope is per (company, concept);
  - ~506-512: `slot_protected_cell` is rewritten per (company, concept).
- `0119_company_value_owner.sql`: keyed by company_id only. No writer exists in `pipeline/src`.
- The pass counts (13/960 etc.) come from the release case (run 41708119011). I did not re-derive them.
- No DB queries and no SEC requests were made.

## Addendum, 2026-11-09 ~17:00 UTC: founder decision "No fallback. Everything is the hybrid (fcn + sec)"
Relayed by Dhairya: the founder typed it in Dhairya's session at about 22:30 IST. I did not hear it directly. Per CLAUDE.md, the founder's own words in the approver's session are still needed to authorize the production write itself.

I accept it as the direction.
- C3 is withdrawn.
- C2 becomes a report, not a hold.
- C1 still applies, as atomicity: a listed data point is written in full for each cohort company, as values or as blanks with a reason.
- C5, C6 and C8 stay. C4 changes; see N2.

New conditions:
- **N1. A hybrid blank is a defect, never a true absence.** `filing_not_in_store` and `hybrid_gap_unresolved` are written to `analytics.cell_blank_reason` (0100) as follows:
  - `state = 'defect'`, never `not_presented` or `not_in_template`;
  - `defect_class` / `owner`: `ingestion` / `data_engineer_l1` for `filing_not_in_store`;
  - for `hybrid_gap_unresolved`, the class mapped from the pilot cause (`period` / `period_engineer`, `vocabulary` / `tag_mapper`, otherwise `unclassified` / `triage`);
  - `reason_text` carries the pilot cause;
  - `input_refs` carries the accession where one exists.

  `reason_code` is free text, so no migration is needed. Test it: one case per cause maps to a valid (state, class, owner), and a row with state defect but no class or owner is refused.
- **N2. C4 conflicts with "no fallback".** The restore stage puts the before-image back, and those are old-mapper values. Under this decision, a cell_proof DISAGREE cell is re-written as a blank:
  - state defect, `defect_class` `identity`, owner `verifier`;
  - `reason_code` `cell_proof_disagree`;
  - cell_proof evidence in `input_refs`.

  The whole-scope restore is kept only as an emergency rollback, which needs the founder's own words. That needs a small code change: a blank-the-DISAGREE-cells step after cell_proof. Until it exists, the founder must know that criterion 6 means restoring old values.
- **N3. Debt, total liabilities and DPS (C6/C8).** "Everything is the hybrid" can be read to include them. The current hybrid's values for these are wrong:
  - debt maps any custom current liability, for example accounts payable (release case §2);
  - total liabilities gets false conflict blanks (§3a);
  - DPS has no share-basis guard.

  These values must never be served. If the founder wants no old rows at all, write these keys as blanks with a reason (state defect, `reason_code` `hybrid_rule_held`, with the rule id), never as hybrid values. Otherwise they stay unlisted and keep their old rows until fixed. This needs the founder's choice. My default until then: unlisted.
- **N4. C2 flag at C7.** For each data point, report the previously valued cells and how many become blanks, with the reason breakdown. I flag to the founder any data point where:
  - over 20% of previously valued cells become blanks;
  - or over 1,000 cells become blanks;
  - or any company in the top 100 loses all of its values for a data point.

  This is a flag, not a hold. A pattern of blanks with an undiagnosed pilot cause blocks my clearance until it is classified.
- **N5. Before-images are still taken and kept for every written company,** as a rollback record (not served).
