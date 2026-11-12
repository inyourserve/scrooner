# Card family: entity and predecessor traps (which company a filing's numbers belong to) — Tag Expert, 2026-11-11, from the Engineering relay (FILING-CHECKED by Engineering and the Verifier 2026-11-10)

These are not tag meanings but they decide whether ANY tag's value belongs to the company. Check them before trusting a series' early periods.
1. **Pre-merger shells under the successor's own CIK** report Assets ≈ 0 and revenue 0: MDT 0001613103-15-000008 (assets $46K), BKR, AMCR ($130), VICI, FTI (74,100), SW, PRMB, AMRX, GLXY, TW; FRHC's 2013-2017 BMB Munai shell filings. Rule: a filing whose Assets is under a de-minimis floor before the successor's first real 10-K is a shell; its values are not the company's history.
2. **SPAC statements in filings dated AFTER the merger close** (trust-account balance sheets): VRT FY2019 10-K, AUR Q3-21 10-Q, PR Q3-16, MGY Q2-18, HIMS FY2020 10-K + 10-K/As. The filing date does not prove the entity; the balance-sheet shape does.
3. **Real entity on a legal-entity member, shell on the default context**: PLNT's pre-IPO 10-Q 0001193125-15-310710 tags Pla-Fit Holdings on a LegalEntityAxis member; non-dimensional reads get the shell.
4. **Reverse mergers**: KDP's own CIK 2015-2018 Q2 is Dr Pepper Snapple (the legal acquirer), while later comparatives reprint Keurig/Maple (2017-Q3: 1,140 vs DPS 1,740). The same pattern as Tyco/JCI, and COLB/Umpqua (interest.md §7).
5. **Predecessor CIK carries the history**: Medtronic plc's 10-Q reprints the quarter to 2014-10-24 with Medtronic, Inc.'s own values (4,366 / 828); the predecessor CIK (64670) holds the earlier series.
6. Utility co-registrant blocks: several registrants' statements in one R page (PEG R5); FSN `coreg` marks only a sole LegalEntity axis (FSN-GUIDE).

> See also (FILING-CHECKED, Dhairya 2026-11-11): cards/fsn-cash-flow.md, fsn-balance-sheet-assets.md, fsn-balance-sheet-liabilities-equity.md, fsn-income-statement.md; conflicts settled in decisions/TAG-EXPERT-RECONCILE-FSN-CARDS-2026-11-11.md.

## Ritwik (cloud) notes 16, 21, 29 (2026-11-11)
- Co-registrant statements inside one filing (PLD/Prologis L.P., SPG/Simon L.P., DUK + six utilities, CMCSA/NBCUniversal to 2019, URI/United Rentals (North America)): take coreg = '' only, for every data point. A UN statement is excluded only when its column carries a co-registrant/LegalEntityAxis member (Dhairya accepted 2026-11-11).
- Pre-merger SPAC filings under the same CIK (VRT 2018-19, GS Acquisition Holdings): outside the history window. 10-K/As with 0 IS/BS/CF lines (MO, SCCO, NEM, TMUS, DIS): not expected filings. CB 2014-17 IS lines sit in a stmt=CI report (14 10-Qs).

- Store statement-scope cases (Data Engineer 2026-11-12): WMB 10-Qs print a combined IS+CI report (stmt CI, R2) and a Transco legal-entity IS (stmt IS, R9): the parent face is R2 (0000107263-26-000026); ROST 10-Q 0000745732-24-000062 has a blank stmt on every pre.txt row (FSN data defect; 1 of 992 filings in 2024q4). Engineering-owned.

## FSN data mechanics (FSN nightly session, relayed by Dhairya 2026-11-12; source: module docstring of pipeline/src/scrooner_pipeline/fsn_store/xbrl_fsn.py on work/fsn-nightly-incremental, calibrated against the 2026m10 SEC FSN set)
- `ddate` = the period end rounded to the NEAREST month end (day 1-15 → previous month end); `datp` = ddate − end date in days; `qtrs` = round(days / 91.25). Match periods by ddate ± datp, never by exact end date.
- `coreg`: LegalEntityAxis is taken out into coreg only when it is the sole axis; typed axes sort after explicit ones, with their raw QName. Primary-registrant values: coreg = '' and dim = 0x00000000.
- `version`: '<taxonomy>/<year>' for a standard tag; the ACCESSION for a filer's own (extension) tag — the reliable custom-tag test (value_source fsn_xbrl).
- `pre` mirrors the R page: statements + cover, depth-first presentation order, plabel = the preferred-label text. `stmt`: the first report of each statement type wins; later ones are UN; a parenthetical takes the type of the statement before it; a lone comprehensive-income statement with no income statement is the IS. The cover is CP only when the filing has statements.
- `iprx` 0 = highest decimals, then end date closest to the month end, then the closest duration (take iprx = 0).
- `dcml`: INF = 32767, absent = −32768. Values are rounded to 4 decimals (per-share and tiny values: use the API or the instance, §AA).
- SEC's cal group/arc numbering is NOT reproducible across builders: compare calc trees by (parent, child, weight), never by grp/arc numbers.
