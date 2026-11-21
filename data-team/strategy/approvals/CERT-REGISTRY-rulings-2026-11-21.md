# Display-cell certificate registry (0132): approver rulings, 2026-11-21

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Asked by the Mac session scrooner-8d via the verifier-audit session, about branch `work/ops/ledger-and-cert-registry-2026-11-21` (b67383be). Rulings 1-5 are certification semantics and are the approver's. Rulings 6 and 7 are engineering or founder decisions; for those this note gives a recommendation only. Applying 0131 or 0132 still needs the founder's typed words.

1. **What is certified: every SHOWN cell of the certified coverage file, not only the 32 drawn.** A certificate certifies the display (the coverage file, by sha256) at a stated error bound. The 32 drawn cells are the evidence for that bound.
   - Load every cell with an `evidence` column, which says how the cell was checked:
     - `drawn`: individually matched to the filing.
     - `census`: every total_debt year, the per-share plausibility census, and every hidden cell's hide-class proof.
     - `sampled`: covered by the per-company and pooled bound, not individually checked.
   - Never present a `sampled` cell as individually verified.
   - Load hidden cells too. Hides are certified by census.
   - Load only PASS certificates. FAIL notes stay in registry.csv.
   - The pooled bound is computed over `drawn` cells only: 0 wrong in 64 gives 4.57%, and 0 in 300 gives 0.99%, matching the plan.
2. **No single proof_version string.** Read the versions from the request file, not a command-line argument, which can be mistyped. Store:
   - `sample_hash` (the coverage file's sha256: this is the identity);
   - `detector_version` (the request's proof DETECTOR_VERSION, e.g. `cell_proof_v21_2026-11-16`);
   - the resolver path;
   - the code sha.
   Do not mark a cell stale on a resolver version bump. A version-only bump changes no value; doc 02 and top100_changed already treat it as "reruns nothing". A cell is stale when its served value, accession or display class differs from the certified row.
3. **A later filing voids a cell only when it prints a different value for that cell's period.** That means the same tag, period and dimensions in a later periodic filing (10-K/Q, 20-F, 40-F; fsn.*), with a different value: a restatement. A later filing that merely re-presents the period as a comparative column does not void the cell.
   - The 3-year-window rule in b67383be would mark 29 of GILD's 32 drawn cells and 27 of JNJ's stale on the day they load, because nearly every period has a later 10-K comparative column.
   - A new fiscal year adds uncertified cells; it voids nothing.
4. **A company is display_certified only while every cell of its latest PASS certificate is valid**, all of them, not just the 32. Any stale cell makes the company `stale` until re-drawn. Agreed in spirit, with ruling 1's scope.
5. **r2 supersedes r1.** The premise is outdated: registry.csv on main already holds the r2 rows (GILD e4ed0b0f, JNJ 674389ae) after the r1 rows. The pooled bound uses the latest row per ticker, and each r2 certificate states that it supersedes r1. Load r2. Any r1 row loaded is invalidated with reason `superseded`.
6. **Recommendation:** keep company_certification deprecated until the retired I1-I11 writer is removed, then drop it in its own migration.
7. **Recommendation:** not as written. A backfill timestamp must never read as an apply time. Make applied_at nullable, and add a source column (`recorded` or `backfilled`) plus backfilled_at, or take the real time from evidence (a CI run or a session log) where one exists.

Also recommended: have `certify_display.py` write a machine-readable certificate (JSON: drawn cells, census results, hide proofs, versions) for the loader to read, instead of parsing markdown. The approver can add this.

## Addendum, 2026-11-21 (after the 0131/0132 load)

8. **A change between two hide classes makes a cell stale for review, not void.** No shown value is wrong either way. But the certificate proved a specific claim ("hidden because X"), so the company is not display_certified until re-certified on an export with the new class. Re-certification is one certify_display run on a new coverage file and request. A change from hidden to shown, or a changed shown value, accession or display class, is stale_display as before.
9. **JNJ 674389ae: the certificate's class claim was wrong for 22 cells, and the approver missed it.** operating_income and shares_outstanding (11 years each) were hidden as whole rows with hide_class `verified_absent`. Doc 02 rule 1 defines verified absence only for a year inside the filing window. A row hidden in every year is `structural_not_presented`, which is what live analytics.cell_display_state now says.
   - The proof the tool ran on these rows (no presented, undimensioned, annual fact of the family at any display-year end) is the structural proof, so the evidence holds under the corrected class.
   - certify_display now rejects `verified_absent` on a HIDDEN_ROW (main, this commit).
   - JNJ stays stale until a new export and request are certified.
10. **GILD e4ed0b0f has no hide_class** because its coverage file predates the column (532fc006). null means "not recorded", not empty. GILD is stale for the same reason as JNJ until it is re-exported with hide_class and re-certified.
11. **Loader NULLs:** the `""` hide_class values on 462 JNJ shown cells came from the certificate JSON, not the loader. certify_display now writes null for an empty hide_class or reason_code. The committed JNJ certificate still holds `""`, so the loader should read `""` as null until JNJ is re-certified.

## Addendum 2, 2026-11-21: changes held by the certified-guard (top100-flow run 44942016622)

12. **JNJ shares_outstanding FY2015-FY2025 (REASON hidden to DERIVED shown): ACCEPTED.** Founder approvals 2026-11-17 (doc 02, 93c8d6ba) allow shares issued minus treasury shares from the same filing. I checked all 11 years in fsn.*: each 10-K's balance sheet (R3 for FY2015-20, R4 for FY2021-25) prints both inputs, undimensioned. Expected values, issued 3,119,843,000 less treasury:

    | FY | Expected |
    |---|---|
    | 2015 | 2,755,162,000 |
    | 2016 | 2,706,511,000 |
    | 2017 | 2,682,525,000 |
    | 2018 | 2,662,324,000 |
    | 2019 | 2,632,507,000 |
    | 2020 | 2,632,512,000 |
    | 2021 | 2,628,965,000 |
    | 2022 | 2,613,597,000 |
    | 2023 | 2,407,078,000 |
    | 2024 | 2,406,922,000 |
    | 2025 | 2,407,939,000 |

    certify_display now checks every derived shown cell against its identity, drawn or not (main, this commit), so the re-certification proves all 11 mechanically.
13. **GILD interest_income FY2024 (REASON to UNCHECKED, 281,000,000, no proof row): REJECTED.** A value without a proof row is never shown. If the resolver proves it (accession, R page and tag, presented in the filing), it is a real change: the row is reported, so the certified HIDDEN_ROW for interest_income is wrong, and every year needs a value or a valid hide class before re-certification.
14. **GILD total_liabilities FY2015 (DERIVED 32,601,000,000 to REASON structural_not_presented): REJECTED.** structural_not_presented means a row never reported, and total_liabilities is shown in every other GILD year. Keep the certified value, 32,601,000,000, from the FY2016 10-K (0000882095-17-000006, R2): 9,890 current + 21,073 long-term debt + 1,243 income taxes payable + 395 other = 32,601. The FY2015 10-K gives 32,724 before the FY2016 restatement. The own-period rule allows a later periodic filing that presents the year, and the restated figure matches the comparatives a reader sees.
    - This also exposed a defect in certify_display: its identity (assets less total equity) counted GILD's 2M of temporary equity ("equity component of currently redeemable convertible notes") as liabilities. It now subtracts temporary equity.
    - The certified cell was sampled, not drawn, so the GILD verdict stands; derived cells are now checked in full.
15. **Re-certification while the certified-guard holds: an approver re-cert token.**
    - Token: `data-team/strategy/approvals/recert/<TICKER>-<date>.md` on main, written by the approver, naming the company and the accepted changes.
    - top100-flow lets a company with a token newer than its latest certificate through the guard once. The gate runs, the export and request are written, and the request cites the token.
    - Rejected changes must be reverted in the resolver before a token is written.
    - JNJ's token is written now. GILD gets one once items 13 and 14 are reverted in the resolver and it can be re-exported with hide_class (addendum 10).
