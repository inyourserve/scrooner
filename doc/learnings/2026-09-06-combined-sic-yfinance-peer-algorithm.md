# Peer comparison: a 4-tier cascade combining SIC and yfinance classification

## What changed

`apps/app/lib/company/db.ts`'s peer-comparison query went from a 2-tier cascade
(exact SIC code → coarse 11-bucket SIC-derived sector) to a 4-tier cascade,
each tier used only when every higher-priority tier combined still gives fewer
than 3 peers:

1. `industry` — exact SIC-code match (unchanged, the SEC's own 4-digit
   classification, excluding SIC 6770/7389 per the 2026-09-06 catch-all fix).
2. `industry_yf` (new) — exact match on `core.company.y_industry` (yfinance's
   own industry classification, backfilled the same day — see doc 02's
   decision register for why this is now a stored, production field).
3. `sector_yf` (new) — exact match on `core.company.y_sector` (yfinance's
   broader ~13-bucket sector).
4. `sector` — this project's own SIC-derived 11-bucket sector (unchanged,
   excludes `sector = 'Other'`).

Implemented as three chained CTEs (`peer_tier_1_2`, `peer_tier_1_2_3`,
`peer_companies`), each a `union all` gated by `(select count(*) from
<prior-tier-CTE>) < 3` and `id not in (select id from <prior-tier-CTE>)` —
the same binary "use the whole next tier, or none of it" gating the original
2-tier version already used, just extended to 4 levels instead of writing a
scored/weighted blend.

## Why this design, not something fancier

Considered and rejected: a scored/weighted blend of SIC and yfinance signals
(e.g. "peer score = agreement between both classifications"). Rejected because
(a) it isn't deterministic/explainable in the way this project's whole
screening philosophy requires (doc 05's "determinism before AI magic," "every
number traces to source"), and (b) the existing 2-tier cascade already
established the right shape — cascading tiers with a `match_basis` label are
easy to reason about and extend, a weighted score is not. Extending the proven
pattern to 4 tiers was strictly additive: zero changes to tiers 1 and 4's own
logic, both new tiers copy the same `distinct on (c.id)` / `security_type =
'Common Stock'` ordering already proven for the other two.

## Verified live against real companies, not just SQL

- **Visa / Mastercard**: previously stuck together with hundreds of unrelated
  companies under SIC 7389's catch-all (or, after the earlier fix, an honest
  empty peer table). Now land in `industry_yf` with 35 real Credit-Services
  peers each — Mastercard appears in Visa's own top-8 (ranked by ROIC),
  alongside PayPal, Western Union, American Express, Affirm, Ally Financial.
- **Etsy**: 22 `industry_yf` peers (Amazon, Chewy, Coupang, BBBY) — real
  e-commerce/online-retail peers, a business model SIC 7389 gave zero signal
  for.
- **Netflix**: previously 1 SIC-exact peer, falling back to the coarse
  "Communication Services" sector (146 companies, phone/telecom included).
  Now lands in `industry_yf` with 33 real media/entertainment peers — Madison
  Square Garden Entertainment, Warner Music Group, TKO Group Holdings
  (UFC/WWE), Walt Disney all appear in the top-8.
- **Uber**: lands in `industry_yf` (193 candidates, "Software - Application" —
  a broad Yahoo bucket that doesn't distinguish gig-economy/mobility apps from
  general enterprise software). Real names shown (Elastic, Workiva, Fair
  Isaac) aren't ideal business-model peers — an honest limitation of Yahoo's
  own taxonomy granularity for this specific company, not a bug in the
  cascade logic. Still strictly better than the prior empty state.
- **SPAC shells still carrying legacy SIC 6770 ("Blank Checks")**: correctly
  share `y_industry = 'Shell Companies'` — an honest, real classification
  (confirmed by direct query, not assumed), meaning these companies now get a
  coherent peer group instead of either a wrong "Real Estate" grouping or an
  empty table.
- **Apple, JPMorgan Chase** (regression controls, both already have 3+
  SIC-exact peers): peer tables byte-identical to before the change — the new
  tiers never activate when tier 1 already satisfies the >=3 threshold, as
  designed.
- Confirmed via a live `next dev` render (`/stock/v`, `/stock/uber`,
  `/stock/nflx`, `/stock/aapl`), not just the standalone SQL — `npx tsc
  --noEmit` clean.

## Known, accepted limitation

Yahoo's own `industry` field is not uniformly granular — some buckets
("Software - Application," "Specialty Business Services") are broad enough to
surface a weak-fit top-ROIC company (e.g. a small, high-ROIC name unrelated in
practice to the anchor company's actual business, the same
degenerate-ratio-at-small-scale risk the existing +/-200% ROIC/margin bound
already guards against, just not eliminated by it). This is a property of the
underlying data source, not a fixable bug in the cascade — the existing
"Peer classification is a starting point, not a claim that business models
are identical" disclaimer already sets the right expectation, and no further
change was made to chase this on a per-industry basis.
