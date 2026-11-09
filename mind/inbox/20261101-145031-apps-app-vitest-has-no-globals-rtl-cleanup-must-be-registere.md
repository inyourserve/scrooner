---
id: apps-app-vitest-has-no-globals-rtl-cleanup-must-be-registere
title: apps/app vitest has no globals: RTL cleanup must be registered in vitest.setup.ts
kind: gotcha
tags: ci, frontend, flaky
paths: apps/app/vitest.setup.ts
evidence: CODE-CHECKED
created: 2026-11-01
verified: 2026-11-01
---
Without vitest globals, @testing-library/react auto-cleanup never runs; trees outlive jsdom and React's scheduler throws 'window is not defined' at teardown (CI run 41313158728). Fixed by afterEach(cleanup) in vitest.setup.ts. Also: focus set in a useEffect must be asserted with waitFor, not right after findBy.
