# SIC catch-all codes were producing meaningless peer comparisons — found and fixed 2026-09-06

## What was reported

User: "my peer comparison table is not good, I think yfinance sector and industry
mapping can help." No specific ticker named.

## What was actually wrong

Two legacy SEC SIC codes are used as generic dumping grounds and carry no real
industry signal on their own, but `company_master/sector_bucket.py`'s SIC-range
table was silently mapping both to a real-sounding sector anyway:

- **SIC 6770 "Blank Checks"** — 848 of ~6,900 active companies (12%!). A random
  sample was dominated by still-unmerged SPAC shells (SPACSphere, Jackson
  Acquisition, FIGX Capital, GigCapital8, Columbus Acquisition). It was falling
  into the `(6700, 6799, "Real Estate")` range (built for holding/investment
  offices/REITs) — every one of these 848 companies was labeled sector
  "Real Estate," which is meaningless for a shell classification.
- **SIC 7389 "Business Services, NEC"** — 112 companies, falling into
  `(7380, 7799, "Industrials")`. A 25-company sample turned up Uber, MercadoLibre,
  FIS, Shift4, TriNet, Maximus, comScore, Xometry — genuinely no shared business
  model, and definitely not "Industrials." This code also happens to hold Visa,
  Mastercard, PayPal, Global Payments, and Western Union — the exact case that
  made the report concrete: two of the most obvious real peers on the market
  (Visa/Mastercard) had zero way to ever appear as each other's peer.

`apps/app/lib/company/db.ts`'s peer-comparison query already had a two-tier
design (exact SIC match, falling back to the 11-bucket sector only when SIC gives
<3 peers) from an earlier fix (2026-08-30, Apple/semiconductor mix-up). That
design is sound; it just had no way to know these two codes are catch-alls, so it
trusted both a wrong exact match and a wrong sector fallback equally.

## How yfinance was actually used (and how it wasn't)

Per `doc/planning/y-finance.md`'s own recommendation (§3.4/§4): fetched sector/
industry live for the full 112-company SIC 7389 population, one-time, dev-only —
never imported into the pipeline's production dependency tree, never stored
verbatim. Confirmed genuine heterogeneity (Software - Infrastructure, Software -
Application, Credit Services, Internet Retail, Shell Companies, Specialty
Business Services, ... — no dominant category), but also surfaced one clean, real
cluster: Visa/Mastercard/PayPal/Western Union/MSCI/Heritage Global/QuoteMedia/
Sezzle/Superstar Platforms all independently classify as Yahoo's own "Credit
Services"/"Financial Data & Stock Exchanges"/"Capital Markets" under "Financial
Services." That finding informed a small, hand-written, hand-reviewed per-CIK
override (`SIC_7389_FINANCIALS_OVERRIDE_CIKS`) that assigns this project's own
"Financials" sector name — Yahoo's classification was a reference used to decide,
never copied or persisted as a fact, matching the doc's explicit "never store a
yfinance-sourced number as a fact" constraint.

## The fix

1. `sector_bucket.py`: carved SIC 6770 and 7389 out of their surrounding ranges
   into `"Other"` (the existing honest-default bucket for genuinely unclassifiable
   codes), same pattern as the pre-existing Nike/3021 footwear carve-out.
2. `sector_bucket.py`: added `SIC_7389_FINANCIALS_OVERRIDE_CIKS`, a 9-company
   allowlist reclassifying the confirmed Credit-Services cluster to "Financials."
3. `apps/app/lib/company/db.ts`: excluded SIC 6770/7389 from the exact-SIC peer
   tier (never a reliable exact-match signal), and excluded sector `'Other'` from
   the sector-fallback tier (a deliberate "no signal" bucket, not a real industry
   group — matching it against itself would repeat the same mistake this fix
   exists to remove).
4. Re-ran `scrooner-company-master update-sector` for the 393 affected CIKs
   against the live database.

## Verified live

- Visa/Mastercard/PayPal/Western Union: now show real Financials-sector peers
  (Mastercard appears in Visa's own table), instead of "Industrials."
- Uber/Etsy/Global Payments (SIC 7389, not in the Financials override, no other
  usable signal): now show the pre-existing honest "No sufficiently comparable
  companies are available yet" empty state, instead of a confidently-wrong
  "Industrials" peer group.
- Apple, JPMorgan (control, unaffected SIC codes): peer tables unchanged —
  confirmed via a live `next dev` render of `/stock/aapl`, `/stock/v`,
  `/stock/uber`, `/stock/jpm`, not just the SQL.
- 389/389 pipeline unit tests pass; 8 new tests added in
  `tests/unit/test_sector_bucket.py`.

## Generalizable lesson

A SIC-range mapping table that has been checked against enough real companies to
earn trust for *most* codes can still contain one or two codes that are
structurally different in kind — a legacy catch-all/NEC classification, not a
genuine industry — and those don't get safer with a wider sample, they get
*more* misleading, because every additional company shares nothing except having
been filed under the same "we don't know" code. The tell isn't a small sample
size; it's the code's own description ("NEC," "Blank Checks," "Miscellaneous").
Worth grep'ing `core.company.sic_description` for those words the next time a
sector/industry-adjacent bug report comes in with no specific company named.
