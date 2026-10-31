# Income statement lane handoff (2026-11-01)
- **Role**: is_core cells for the canonical_fact rebuild (manager scrooner-0f; loader and format scrooner-8a, CELL-FORMAT v1.1 at 6559c65): revenue_sanity, operating_income, net_income, gross_profit, cost_of_revenue for the 1,000 cohort, period_end >= 2014. Rules are the Verifier-passed slot rules, unchanged. Flags OFF, no production DB writes.
- **Branch**: `work/income-statement/full-population` (from main). It carries the lane's latest detector/replay. main had only the results; the code of 6637a1c (G1b preferred, G2b bridge, co-registrant face) never landed. Also `is_not_presented.py`, which replaces `is_oi_not_presented.py`, and the new `is_emit.py`.
- **Stopped**: the generic slot writer `work/income-statement/slot-writer` b74289e (founder: rebuild, don't patch). Do not land or run it. The IS release packages are superseded.
- **Emitter state**: full file built locally, not handed over yet: 281,761 rows, 1,000 companies, FSN 2014q1..2026m09, sha256 (uncompressed) 77f5846af90949a5..., 10.9 MB gz. Per data point (calendar keys valued+derived / blank-no-column): revenue 40,594 / 3,352; NI 49,335 / 1,709; OI 36,668 / 1,924; GP 18,166 / 3,048; COR 22,945 / 12,453.
- **Pipeline** (scratch, regenerate if wiped; ~20 min, read-only):
  1. `is_detect.py <is_fsn> <out> coreg_cohort_adsh.txt`: byte-identical to the verified slots (223,575 rows).
  2. `IS_REPLAY_PROD=0 IS_SINCE=2014-01-01 is_replay.py slots @cohort_ciks.txt <replay>`: one DB connection, 60s timeout, 17 min.
  3. `is_not_presented.py family=<operating_income|gross_profit|cost_of_revenue> ...` per family.
  4. `is_emit.py <replay> <np> slots <is_fsn> company_ids.tsv expected_periods_2026-10-31.csv.gz <out> <commit>`
- **Next**:
  - (1) Rerun `is_emit.py` with the commit sha and hand `cells.jsonl.gz` + `manifest.json` to scrooner-8a. I handed over a local path, not the fsn-notes bucket: my instructions say no production writes without the founder's typed words, and 0f's OK to use the bucket is a peer's OK, not the founder's.
  - (2) Ask 0f whether cost of revenue Q2-Q4 should be derived. Not derived now: the 2026-11-04 list was revenue, NI, OI and GP only; this is why COR has 12,453 calendar blanks.
  - (3) Check the 3 calendar keys skipped because their length does not match their fiscal period (listed in the manifest).
- **Derived quarters**: Q2/Q3/Q4 = YTD_n - YTD_(n-1), same fiscal start. Vintage rule unrestated_single_value: a published cell already agrees with every copy. A hidden input gives defect mixed_vintage, a held input gives quarter/q4_input_held. A printed 3-month column always wins.
- **Gotchas**:
  - Spec grains are FY/Q only: 6M/9M rows are dropped as rows, but they feed the quarters.
  - Held filings publish no replay cell. The emitter re-adds each original filing's face column as a defect with that filing's gate, or the column would vanish.
  - CF/BS packages key cells on FSN nominal month-end (KO 2015-03-31 vs core.period 2015-04-03): bind by period id or within 10 days, never by date alone.
  - Local Postgres here is 14. DB tests need 16 (CI), so push and read the CI result.
  - FSN 2026m10 is empty locally.
