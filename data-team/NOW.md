# Scrooner now

Compact orientation only. Generated evidence and the task board win if this file becomes stale.

Updated: 2026-10-26 IST.

## Product objective

For the top 1,000 US companies, every displayed financial cell is either a filing-traceable correct value or a visible, evidenced reason. Never claim universal correctness; publish measured error rates.

## Scoreboard

- Certified companies: 0 / 1,000.
- Production cells changed by the certification programme: 0.
- Cohort cells: 161,533; valued: 124,029 (76.8%); reasonless blanks: 13,354.
- Migrations 0098-0100 are applied. Migration 0110 (`company_slot_record`) is not applied.
- Balance-sheet slot records have been produced for 999 companies and passed multiple filing-check samples; they are not serving users.
- Total debt passed its 33-company verifier gate. D&A/capex is under V3 verification.

## Current critical path

1. Finish migration sequence 0101-0109, merge/apply 0110.
2. Approve and load balance-sheet slot records.
3. Wire them behind a flag; dry-run and rehearse rollback.
4. Switch on one company and generate its certificate.
5. Continue families: debt, D&A/capex, then revenue/net income/operating income/shares/EPS/CFO/dividends/buybacks/interest/tax.

## Canonical files

- Direction: `data-team/strategy/THE-PLAN.md`
- Execution state: `data-team/strategy/TASK-BOARD-TOP1000.md`
- Compact live view: `python3 scripts/agent_context.py`
- Detailed evidence: files linked by the task-board row being worked.

Do not expand this file into a work log. Keep it under roughly 80 lines.
