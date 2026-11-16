# AUTO-LOOP review, certification side (approver, 2026-11-17): PASS

Reviewer: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Change: main 566a6651 (Engineering). Scope: `.github/workflows/display-certify-auto.yml`, plus the `requests` mode of `scripts/ci/top100_changed.py` it calls. Out of scope: `top100-auto-trigger.yml`, which dispatches the data flow, not the certification. Engineering owns that half, and this note does not approve it.

## Verdict: PASS for display-certify-auto

- It dispatches the unchanged `display-certify.yml` with the existing `requests` input. `certify_display.py` and the judge workflow are untouched (checked against the diff).
- It is off unless `vars.AUTO_LOOP == 'true'`, and runs on main only.
- It has its own queue group and never cancels. It waits up to 25 minutes for an active display-certify run instead of replacing it. If that run is still active, it exits non-zero, and the next trigger covers the range.
- It holds no secret except GITHUB_TOKEN (`contents: read`, `actions: write`) and writes nothing. The dispatched workflow is read-only on the database (fsn.* SELECTs under a statement timeout).
- The request pattern is anchored to `data-team/strategy/approvals/requests/<T>-request-<date>.md`.

## Notes (not blocking)

1. **Diff base.** The base is the head commit of the last successful auto run. For a `workflow_run` event, a run's head commit is the flow run's commit, which can be older than the main it diffed. The effect is a repeated request, never a skipped one. Repeats are harmless: display-certify writes nothing, and its registry rows go to the artifact copy. If this ever matters, dispatch `requests=pending` instead. Since main 7fa89892, `pending` means "no certificate or final-draw file cites this request's coverage sha256", which deduplicates by content.
2. **A burst of requests** arriving while display-certify is busy for more than 25 minutes is picked up by the next trigger. To be safe, a daily `pending` dispatch would cover a range that no trigger follows.

## Decision: the workflow does not commit verdicts

The loop ends at the artifact and job summary, and the approver commits the certificate or final-draw file. I am keeping that separation for now. On 2026-11-16 alone the approver's reading caught tool defects that a self-committing workflow would have published:
- a filter that matched no fact at all;
- debt and hide evidence that was too loose;
- STX FY2022 dividends per share of 2,770,000, which passed a later draw because it was not drawn.

I will revisit once a run of companies goes through with no change to the tool.
