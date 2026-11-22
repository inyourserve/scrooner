---
id: non-december-filers-open-shown-rows-keyed-to-wrong-or-phanto
title: Non-December filers: open-shown rows keyed to wrong or phantom periods (PG 2024-09-30, MU 2023-12-31, DE calendar-2017 FY row) are a period-key defect, not a filing gap
kind: gotcha
tags: period, fiscal-year, open-shown, top100, flow
paths: data-team/strategy/open-shown-fixes/PG-2026-11-21.csv, data-team/strategy/open-shown-fixes/MU-2026-11-21.csv, data-team/strategy/open-shown-fixes/DE-2026-11-21.csv
evidence: FILING-CHECKED
status: active
created: 2026-11-21
verified: 2026-11-21
---
Filing agents 2026-11-21 found that at three non-December filers most open shown cells sit on a period the company never reported: PG FY2024 duration rows keyed period_end 2024-09-30 (true FYE 2024-06-30; 36 of 63 open rows); MU FY2023 rows keyed 2023-12-31 (true 2023-08-31) and FY2026 BS rows keyed 2026-09-12 (true 2026-09-03), 42 of 58; DE has a phantom core.period row id 171434 (2017-01-01..2017-12-31, FY) beside the real FY2017 row id 171454, 31 of 83 open rows. The shifted key also joins the row to another filing's figure (MU interest_income FY2023 row quoted the FY2026 value 1,084 instead of 468). Treat such rows as a flow/period-table bug to fix once (key derivation for non-December and 52/53-week fiscal years; phantom FY rows need a migration-backed delete with the founder's typed words), never as filing gaps, and never create an annual cell on the bogus date.
