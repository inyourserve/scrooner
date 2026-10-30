---
id: founder-decisions-2026-10-25-migrations-0098-0100-go-storage
title: Founder decisions 2026-10-25: migrations 0098-0100 go; storage dedupe + delete pre-2015 data; agent-only approver confirmed; no quiet windows, shard and parallelize
kind: decision
evidence: DOC-CITED
created: 2026-10-25
verified: 2026-10-25
---
Given to scrooner-25, relayed to scrooner-a5 and scrooner-4d; both require the founder's words in their own sessions for production writes/deletes. (1) 'Go ahead' on applying 0098-0100. (2) 'authorized: delete duplicate companyfacts objects after hash check, keep the latest payload per CIK' and 'keep data from January 2015 only, any data before 2015 - delete' (Dhairya flags: pre-2015 rows feed split bases, comparatives and 2015 TTM/Q4; cut needs a ruling; backup first). (3) Approver policy: agents only, approver never the preparer, founder signs only novel definitions. (4) 'move faster, thread, shard, multiple connections, complete the job': no quiet windows or clock G; Dhairya's agents get 8 pooler connections total, heavy jobs via 4d's shard plan. Board: data-team/strategy/TASK-BOARD-TOP1000.md (main 9192e8d).
