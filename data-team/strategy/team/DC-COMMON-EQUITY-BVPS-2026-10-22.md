# Decision card: common-equity numerator for book value per share (`bvps.common_equity_numerator@1`), Standardization Lead, 2026-10-22

Status: **PROPOSED** (decision kind: definition/derivation). Not verified, not approved. The Standardization Lead cannot approve its own rule; the next step is a Verifier re-read. No code, data or migration was changed.
Companion: `DC-SHARE-COUNT-DATE-2026-10-22.md` (the denominator). Both must come from the same accession and the same instant D.
Evidence labels: **FC** = FILING-CHECKED (I opened the filing's XBRL instance and/or main document; the accession is cited). **DI** = DATA-INFERRED (our tables). **AS** = ASSUMED.

## 1. Problem
`book_value_per_share` is "Stockholders' Equity / Shares Outstanding" (`pipeline/src/scrooner_pipeline/mapper/expanded_definitions.py`). Its numerator is canonical `stockholders_equity`, mapped first_match as:
1. `StockholdersEquity`;
2. `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` (`mapper/concepts.py`; DI, `concept_mapping`).

Two errors follow:
- **Preferred stock is inside the numerator.** JPM's stored BVPS at 2026-06-30 is 140.92 (DI). The filer prints **$133.01** (FC, below): our value is 5.9% too high.
- **Noncontrolling interest enters through fallback 2** whenever a filer has no `StockholdersEquity` fact. UNH's stored BVPS at 2026-06-30 is 115.48 (DI) = 104,513M total equity (incl. NCI) / 905M shares. Parent equity is 98,447M (FC).

## 2. Concept contract `common_equity_resolved` (proposed)
- **Economic definition:** equity attributable to the parent's common shareholders at instant D. That is parent stockholders' equity (excluding noncontrolling interests) less preferred stock carried in permanent equity. Treasury stock and AOCI stay in, as filed.
- **Statement:** balance sheet, instant, consolidated (no LegalEntityAxis or other non-class axis), unit **USD only**.
- **Source:** the same periodic-form accession and instant D as the share count.
- **Sign:** as filed. A deficit is negative and is a real value (STKS -92,074K, FC).
- **Idiom:** a `_resolved` concept with zero `concept_mapping` rows, written by a resolver. This is the `total_debt_resolved` idiom, so `resolve-facts` never wipes it.
- **Change to the formula:** `book_value_per_share` = `common_equity_resolved` / the share count from `pershare.share_count_date@2`.
- **Not changed:** canonical `stockholders_equity` itself. Its fallback-2 NCI problem also feeds ROE and leverage ratios; that is routed in section 8.

## 3. Parent equity P (first computable)
- **P1.** Undimensioned `us-gaap:StockholdersEquity`.
- **P2.** Undimensioned `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` minus undimensioned `MinorityInterest` (NCI in permanent equity), both at D.
  - If `MinorityInterest` is absent, P2 may use the inclusive total only with filing evidence that NCI is zero:
    - a filed zero `MinorityInterest`, or a filed zero `[NoncontrollingInterestMember]`; or
    - equity-statement components that sum to the total with no NCI member.
  - Otherwise hide with `numerator:nci_unseparated`.
- **Corroboration.** Where the filing has `StockholdersEquityIncludingPortion...[StatementEquityComponentsAxis=ParentMember]`, P must equal it (PSA 9,190,280K, CRL 2,839,636K, STKS -92,074K, all FC). A mismatch beyond rounding holds the cell (`review:parent_equity_conflict`).
- **Never** the inclusive total on its own as parent equity. **Never** a figure with redeemable NCI added in.

## 4. Preferred in permanent equity, Pref
**Sources:** undimensioned
- `PreferredStockValue`,
- `PreferredStockValueOutstanding`,
- `PreferredStockIncludingAdditionalPaidInCapital`,
- `PreferredStockIncludingAdditionalPaidInCapitalNetOfDiscount`,

or the equity-statement preferred column `StockholdersEquity[StatementEquityComponentsAxis=PreferredStockMember | PreferredStockIncludingAdditionalPaidInCapitalMember]`.
- When both the line tag and the column are filed, they must agree (JPM 21,040M both, HOVR 6,277K both; FC).
- When preferred is filed per series, the series members must sum to the undimensioned total (JPM: 12 series sum to 21,040M, FC).

**Pref = 0 only with filing evidence:**
- a filed zero `PreferredStockValue`, `PreferredStockSharesIssued` or `PreferredStockSharesOutstanding` (DHI, UNH, CRL, HAS, LMNR, GUAC, SEV; FC); or
- equity-statement components that sum to P with no preferred member.

The absence of our preferred tags is not evidence of zero (ledger row 72). If preferred shares are outstanding at D and there is no amount, hide with `numerator:preferred_amount_unknown`.

**Measurement: carrying amount as presented**, not liquidation preference.
- FC: JPM. (374,598M - 21,040M carrying) / (4,104,933,895 issued - 1,446,747,700 treasury) = **133.007**. This matches the filer's "Book value per share $133.01" (10-Q 0001628280-26-054343, MD&A selected data). On a liquidation basis (21,200M) the result is 132.947, which does not match.
- Where liquidation preference or cumulative dividends in arrears exceed carrying, the definition is **AC-32** (accountant).
  - Default: carrying amount.
  - Hide with `numerator:preferred_dividends_in_arrears` when `PreferredStockAmountOfPreferredDividendsInArrears` > 0 at D. AS: no arrears case was opened.

## 5. Redeemable preferred, redeemable NCI and other mezzanine items
- **Redeemable or convertible preferred in temporary equity** is already outside P. Nothing is subtracted or added back.
  - FC STKS 0001104659-26-092751: Series A preferred 210,554K (160,000 shares) in temporary equity; P = -92,074K = common equity; BVPS = -92,074K / 31,684,868 = **-2.906**. That equals the stored value (DI).
  - FC LMNR 0001342423-26-000031: Series B and B-2 preferred 1,331K + 9,331K in temporary equity, outside equity.
  - The amount the preferred would be redeemed at, versus its carrying value, is AC-32.
- **Redeemable NCI** (`RedeemableNoncontrollingInterestEquityCarryingAmount`) is outside P and outside common, so it is ignored:
  - CRL 42,537K (FC);
  - UNH 1,436M (FC);
  - HIW "Noncontrolling interests in the Operating Partnership" 60,840K (FC).
- **NCI in permanent equity** is excluded: DHI 587M, UNH 6,066M, PSA 95,532K, CRL 6,354K, HIW 198,050K "in consolidated affiliates" (all FC).
- **Up-C or UpREIT units that are NCI** are excluded, so the perimeter matches the registrant's own shares (as in WO-21 3.4 step 5; **AC-22**).
- **Redeemable common** (SPACs) goes to the share card, section 5 (**AC-31**).

## 6. Other exits
- `unit:non_usd_numerator` (HOVR: CAD).
- Liquidation basis (AIV).
- The combined-registrant default context must be the registrant's (Gate A, ledger row 83).
- **AC-33: participating or convertible preferred** that shares in residual equity like common (two-class EPS allocates earnings to it).
  - Default: hide with `numerator:participating_preferred`.
  - Detection tags still need a Tag Mapper census (AS).

## 7. Acceptance tests (FC inputs; stored values DI)
| Case | Accession, D | Expected |
|---|---|---|
| JPM | 0001628280-26-054343, 2026-06-30 | P1 374,598M; Pref 21,040M (12 series sum to the total; line equals column); CE **353,558M**; shares A3 2,658,186,195; BVPS **133.007**, which matches the filer's $133.01. Never 140.92 (stored) or 132.95 (liquidation basis) |
| PSA | 0001628280-26-050612, 2026-06-30 | P1 9,190,280K = [ParentMember]; Pref 4,350,000K (= liquidation 4,350,000K); CE **4,840,280K**. Preferred is 47% of stockholders' equity, so today's formula would nearly double BVPS. NCI 95,532K is already outside P1 |
| HIW | 0000921082-26-000045, 2026-06-30 | P1 2,391,440K ("Total Stockholders' Equity"); Pref 26,631K (Series A); CE **2,364,809K**; shares 110,306,211 "issued and outstanding"; BVPS **21.439**. OP units 60,840K and affiliates' NCI 198,050K are not included |
| UNH | 0000731766-26-000197, 2026-06-30 | No `StockholdersEquity` fact; the face shows no parent subtotal (common 9 + APIC 0 + RE 100,957 - AOCI 2,519). P2 = 104,513M - 6,066M = **98,447M**, and the components agree; Pref 0 (filed). Never 104,513M (stored path, BVPS 115.48) |
| DHI | 0000882184-26-000096, 2026-06-30 | P1 23,819.5M (not the inclusive 24,406.5M); Pref 0 (filed); CE 23,819.5M |
| CRL | 0001100682-26-000118, 2026-06-27 | P1 2,839,636K = [ParentMember]; Pref 0; redeemable NCI 42,537K and NCI 6,354K are not included |
| STKS | 0001104659-26-092751, 2026-06-28 | CE = -92,074K (preferred is in temporary equity); BVPS -2.906 |
| HOVR | 0001213900-26-108211, 2026-08-31 | P1 67,657K CAD minus Pref 6,277K gives 61,380K CAD; the result is **hidden `unit:non_usd_numerator`** |
| Negatives (synthetic) | - | Inclusive total with no `MinorityInterest` and an NCI column present: `numerator:nci_unseparated`. Preferred shares > 0 with no amount: `numerator:preferred_amount_unknown`. Series members that do not sum to the total: hold. A P1 vs [ParentMember] mismatch: hold |

## 8. Impact plan, open items and routing (counts not measured)
- **Impact query (read-only, chunked by company):** for each company's latest D, count three groups:
  1. Pref > 0 in permanent equity (preferred-inclusive today);
  2. canonical `stockholders_equity` sourced from the inclusive tag where NCI is not zero;
  3. Pref unknown.

  A first attempt at this over all FY2025 instants timed out at 20 s per statement and was stopped (my own session, confirmed ended). The next attempt should go through the FSDS `pre`/`num` files or a heavy-job slot.
- **Routed to the Standardization Lead and Tag Mapper:** canonical `stockholders_equity` fallback 2 (the inclusive tag) also feeds ROE, debt/equity and other leverage metrics. UNH shows it publishes NCI-inclusive equity as parent equity. That needs its own card: replace the fallback with P2.
- **Accountant:** AC-32 (preferred measurement: carrying vs liquidation, arrears); AC-33 (participating preferred); AC-22 (units); AC-31 (SPAC; the share card).
- **Data Engineer:** a USD-only gate on monetary canonical concepts (HOVR).
- **Not tested:**
  - 10-K filers (all cases above are 10-Qs);
  - a filing with preferred dividends in arrears;
  - a participating-preferred filer;
  - preferred carried below liquidation preference in permanent equity, other than JPM's 0.8% gap;
  - JPM's earlier periods;
  - the rendered R-file view.
