# GILD / DHR balance-sheet cash check, 2026-11-12 (FILING-CHECKED)

## Gilead, CIK 0000882095, 10-K FY2025, accession 0000882095-26-000006 (filed 2026-02-24)
- BS = R3 "CONSOLIDATED BALANCE SHEETS": label "Cash and cash equivalents", tag us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents; 12/31/2025 7,564; 12/31/2024 9,991 ($M). No restricted cash line anywhere on the BS.
- CF = R9: "Cash and cash equivalents at end of period" (same tag) 7,564 / 9,991 / 6,085 (FY25/24/23); beginning 9,991 (FY25). BS = CF for FY0 and FY-1. CF net-change line uses the ...RestrictedCash...PeriodIncreaseDecreaseIncludingExchangeRateEffect tag, labelled plain "Net change in cash and cash equivalents".
- Notes: main doc gild-20251231.htm has 24 hits of "restricted", all stock/units or contractual (no restricted cash, no escrow/pledged cash). None disclosed.
- Verdict: cash_and_equivalents (plain cash; tag is the total by filer choice, no restricted component).

## Danaher, CIK 0000313616, 10-K FY2025, accession 0000313616-26-000062 (filed 2026-02-24)
- BS = R3 "Consolidated Balance Sheets": label "Cash and equivalents", same tag; 12/31/2025 4,615; 12/31/2024 2,078 ($M). No restricted cash on BS.
- CF = R8: "Ending balance of cash and equivalents" (same tag) 4,615 / 2,078 / 5,864; beginning 2,078 (FY25), 5,864 (FY24). BS = CF for FY0 and FY-1.
- Notes: dhr-20251231.htm has 13 "restricted" hits, none restricted cash (only an injury metric and a sentence that repatriation of foreign cash "may be restricted by local laws", a risk remark, no amount). None disclosed.
- Verdict: cash_and_equivalents.

Sources: MetaLinks.json fetched for both (R3/R9 and R3/R8 statement mapping); R pages and main 10-K htm under .../scratchpad/sec/ (gR3,gR9,dR3,dR8,g.htm,d.htm). Not checked: XBRL-only footnote facts without text (searched rendered text only).
