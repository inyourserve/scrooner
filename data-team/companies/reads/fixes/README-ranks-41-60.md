# Red-cell fix files, ranks 41-60 (cash-flow lane session)

**Where:** branch `work/reads/redcells-41-60` (not main). Files: `<TICKER>-fixes-2026-11-13.csv` (v1 list, 1,187 cells,
head ba7ef483) and `<TICKER>-fixes-v2-2026-11-13.csv` (v2 list, the 244 reader rows that are not "fix file ready").

**C / AXP corrections (Tag Expert review, main 1a198c1a):** on this branch since 309dadd8:
C deposits 2024 = 1,284,458,000,000 (Deposits), C loans_net 2024 = 675,914,000,000
(FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss), AXP deposits 2024 = 139,413,000,000 (Deposits).

**Why not main (blocked, stated as asked):** this session's operating instructions allow pushes to work branches only;
a push to `main` needs the user's own instruction in this session, and a peer session's relay is not that. Engineering
(or anyone with main rights) can merge this branch or load the files from it: they are new files only, no existing
docmap is touched. Messages from this cloud session to the Mac manager session are refused (untrusted device), so this
file is the channel.
