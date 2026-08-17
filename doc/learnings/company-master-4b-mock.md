# Company Master 4b — Mock Price Data

## Unblocking on a real, explicitly user-approved decision, not a silent one

Doc 02's market-price vendor decision stayed open through 4a on purpose — it's a real recurring-cost, ToS-bound choice, not something to assume. When directed to close it with mock data instead of a real vendor, the risk wasn't building the wrong thing technically, it was building something that could later get *mistaken* for real data in a project whose entire trust model (doc 04) is "every number traces to source, formula version, and data date." A mock EOD price that later got treated as if it were real would be a much worse failure than any of 4a's two bugs, because it wouldn't look wrong — it would look like a normal, plausible price.

The fix was structural, not just documentary: `is_mock` is a hard boolean column, not just a string on `source` that a future query could misspell or forget to filter on. Two independent signals (`is_mock=true` and `source='mock'`, never a real-sounding vendor name) mean there's no single point of failure for "how would a future reader know this isn't real."

## A seeded generator, for the same reason every other stage in this project gets rerun and diffed

Mock data doesn't need to be *correct* the way a computed metric does, but it still needs to be *reproducible* — otherwise this stage's own idempotency can't be verified the same way every other stage's has been (rerun, diff, confirm identical). Seeding the random walk by a hash of `(cik, end_date)` gets that for free: the same company, reloaded on the same day, produces byte-identical prices, which is exactly what got checked (AAPL's full 30-row series, reran, compared field by field).

## Verification summary

- 300 mock rows loaded (10 companies × 30 trading days), all `is_mock=true`/`source='mock'`.
- Reran the full golden-set load and a single-CIK targeted reload; confirmed byte-identical output and full isolation from other companies' rows.
- No bugs found — the first clean stage in Company Master, after 4a's two.

## Why it matters going forward

This table is a live landmine until a real vendor is chosen: every row in it right now is fabricated, in a project that otherwise never fabricates a financial number. The two structural safeguards (`is_mock` boolean, `source='mock'` never resembling a real vendor) exist specifically so that fact stays impossible to miss, not just documented. Any code that reads `core.market_price` — starting with the eventual Mapper follow-on that computes the 6 price-dependent metrics — must treat `is_mock=true` rows as unfit for anything shown to a real user, and this project's own discipline (never fall back to a lower-confidence value to avoid a gap) applies exactly the same way here as it does to `core.fact.is_authoritative`.
