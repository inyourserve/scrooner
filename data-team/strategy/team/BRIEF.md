# Shared brief for the tag-non-uniformity investigation (Ritwik, 2026-10-21)

Founder's problem: tags are not uniform across companies, so data coverage has big holes and data quality has wrong values. Founder wants a COMPLETE, evidence-based solution that engineering can build and that moves the needle. No half-baked answers.

What is already known (read, do not redo):
- data-team/strategy/38-*.md and 39-*.md (my diagnosis and proof of concept); data-team/33 (fix plan), 34 (certification program), 22 (ledger), 20 (infra map), tags/ (cards, sources), doc/data-moat/team/top1000/status.md and PLAYBOOK.md.
- PoC finding (DATA-INFERRED, SEC FSDS 2025q4, 353 10-Ks): revenue name-matching already ~97% of filers with a revenue line. The bigger non-uniformity is line PERIMETER for composite concepts (D&A: 61 of ~300 filers differ between name-tag and label-position rule; capex 29; interest, operating income, total debt similar). Net income IS vs CF identity passes 324/324.
- Extracted FSDS 2025q4 files (sub.txt, pre.txt, tag.txt, num.txt, tab-separated) are at /private/tmp/claude-501/-Users-vikash-scrooner/99c20ae4-2938-4dd5-8ec6-924194f63d67/scratchpad/fsds/x/ . Read only. PoC scripts: data-team/strategy/tools/. Use python3 -I for scripts that read data files.

Hard rules:
- Read-only on the database and repo code. No migrations, no commits, no pipeline edits. Write only your report file under data-team/strategy/team/ (name given in your task) using Bash heredoc or Write if you have it.
- DB: pooler is near its ceiling (21 connections seen). Run a DB query only if `select count(*) from pg_stat_activity` is <= 14; one connection, set statement_timeout 20s, chunk by company ids. If you cannot query, say so and use repo files / FSDS instead. Never invent a count.
- Disk is 98% full (about 4 GB free). Do not download more than 300 MB in total; delete what you download. sec.gov fetches: User-Agent from pipeline/.env SEC_USER_AGENT (do not print or send any other value), at most 2 requests/second.
- Label every finding FILING-CHECKED (filing opened, accession + locator cited) / DATA-INFERRED / ASSUMED. Say what you could not verify.
- Do not approve accounting definitions; propose them for the Standardization Lead and a named accountant.
- Final message: <= 900 words: findings with numbers and sources, a clear recommendation, risks, what would change your mind, and the exact path of the report file you wrote.
