# Decision card: `pershare.share_count_date@2` (Standardization Lead, 2026-10-22)

Status: **PROPOSED** (decision kind: derivation/definition). Not verified, not approved. The Standardization Lead cannot approve its own rule; the next step is a Verifier re-read. No code, data or migration was changed.
Inputs: `W10-SHARE-DATE-CENSUS-2026-10-22.md` (Period Engineer, the census), PLAN.md section "Period Engineer W10 share-date census", WO-21 (`WO-ADS-RATIO-AND-MULTICLASS-2026-10-22.md` 3.1-3.4, AC-22 to AC-25), the tag card `net-income-and-shares.md`.
Evidence labels: **FC** = FILING-CHECKED (I opened the XBRL instance and/or the main 10-Q document myself for this card; the accession is cited). **FC-census** = filing-checked by the Period Engineer, not re-opened by me. **DI** = DATA-INFERRED (our tables). **AS** = ASSUMED.
Consumers: `book_value_per_share` and `net_cash_per_share` (balance-sheet-dated per-share metrics, RF-10). Market cap keeps WO-21 3.2 (cover-first) and is out of scope here.

## 1. The rule
The denominator is the count of **common shares outstanding at the balance-sheet instant D**. D, the count and the numerator all come from the **same accession**, a periodic form (10-K, 10-Q, their amendments, 10-KT). Facts must be at instant D, consolidated (no LegalEntityAxis or other non-class axis), unit `shares`. Common classes only.

Precedence, first computable path wins:
- **A1** undimensioned `us-gaap:CommonStockSharesOutstanding` (today's rule).
- **A2** sum of `CommonStockSharesOutstanding` over `StatementClassOfStockAxis` common members (conditions in section 2).
- **A3** undimensioned `CommonStockSharesIssued` minus undimensioned `TreasuryStockCommonShares` (section 3).
- **A4** undimensioned `CommonStockSharesIssued` alone, only when the filing has no treasury line of any kind (section 4).
- **C** otherwise: blank with reason `incomplete:denominator:no_balance_sheet_date_share_count`.

Rules that apply to every path:
- **R1. Paths must agree with each other.** Any two paths that can both be computed must give the same count to within the coarser `decimals` of their inputs. Otherwise the cell is held with reason `review:share_path_conflict`. CDLX (A1 5,451,000 vs issued 5,808,000, no treasury fact, FC-census) is the kind of case this catches.
- **R2. The equity-statement column is never a source.** That column is the fact dimensioned `StatementEquityComponentsAxis=CommonStockMember`, tagged `CommonStockSharesOutstanding` or `SharesOutstanding`. It may serve only as a corroborating check, and only when it equals A3 to within rounding. At PKOH, CSW, DK, ALOT and USPH it is the **issued** count (FC-census; PKOH re-checked FC below).
- **R3. Cover is a cross-check only.** If |chosen count - cover `dei:EntityCommonStockSharesOutstanding` (sum of the cover's class facts)| / chosen count > 5%, the cell is held with reason `review:share_count_cover_divergence` until a Verifier record exists for that accession. The value it holds is still the D-dated count, never the cover count. The 5% is a trigger that hides a cell for review, not an accepted error rate.
- **R4. Never use these tags:** `WeightedAverageNumberOf*`, diluted counts, `SharesIssued` (a movement tag: SEV files an undimensioned `SharesIssued` 4,301,846 at instant D that is not a balance, FC), authorized counts, `TemporaryEquitySharesOutstanding`, members for pre-funded warrants or shares "to be issued" (section 6), and ADR-member facts.
- **R5. Precision.** A derived count carries the coarser `decimals` of its inputs. KO, KR and KD file in rounded millions or 0.1M.
- **Structural exits, which run before the paths:**
  - liquidation-basis statements give `not_applicable:liquidation_basis` (AIV, ledger row 93);
  - no publicly held common gives `not_applicable:no_public_common` (Athene, FC-census);
  - redeemable common in temporary equity is handled in section 5;
  - an ADS-priced listing is handled in section 7;
  - a non-USD equity numerator gives `unit:non_usd_numerator` (section 6, HOVR).

## 2. A2: sum of common classes
**Accounting meaning.** Shares outstanding is a per-class legal count. For per-share book value, the issuer total is the sum over the common classes that share pro rata in residual equity. It is not any single class (doc 21 section 8.7).

**Conditions (all must hold):**
1. **Class enumeration.** The set of common classes is the union of `StatementClassOfStockAxis` common members on `CommonStockSharesAuthorized`, `CommonStockSharesIssued`, `CommonStockSharesOutstanding` and `CommonStockValue` at D. Every enumerated class needs an outstanding count; a filed zero counts. Members whose label or name says "to be issued", "issuable", "subscribed" or "pre-funded" are not classes (section 6). If any class is missing, hide with `class_count_incomplete`.
2. **Economic class test.** If the filing files class-dimensioned basic EPS or basic WASO:
   - sum only the classes that carry those facts;
   - the per-class EPS figures must be equal. If they are unequal (BRK Class A and Class B, a 1,500 ratio), hide with `class_rights_unequal` unless the filing states a conversion ratio (WO-21 3.4 step 3).
   - If EPS is undimensioned only, every common class with an outstanding count is summed (PRLD).
3. **No redeemable class.** No summed class may appear in `TemporaryEquitySharesOutstanding`.

**Failure modes:**
- Up-C non-economic class. RPAY Class V has 100 shares, no EPS fact and no economic rights; condition 2 excludes it. In larger Up-Cs, Class B voting shares are issued 1:1 with LLC units and would double the count.
- Unlisted convertible class (AC-24).
- SEV-type cover. The cover counts only the listed class, so the cover cross-check fires (R3).
- SPAC redeemable class (section 5).
- To-be-issued member (HOVR, section 6).

**Accountant?** Not for equal-rights classes: summing is arithmetic. Unequal rights, unlisted convertible classes and Up-C units stay with the accountant (AC-22, AC-24). The default is to hide.

## 3. A3: issued minus treasury
**Accounting meaning.** Outstanding = issued - treasury. This is a same-instant balance identity in legal share accounting (WO-21 3.1), not a period subtraction. Treasury shares are issued but not outstanding and carry no dividend or vote.

**Conditions:**
- Both facts undimensioned, at the same instant D, in the same accession.
- Treasury >= 0. A negative treasury fact is quarantined (sign rule, doc 21 section 3), never flipped.
- `TreasuryStockShares` is an accepted synonym for `TreasuryStockCommonShares` only when the filing has no preferred treasury.
- If issued or treasury is filed only per class, use A2 or C. Never mix a class-dimensioned fact with an undimensioned one.

**Failure modes:**
- PKOH/CSW/DK/ALOT/USPH trap: the equity column carries the issued count under an "outstanding" tag. R2 rejects it, and A3 recovers the correct count: CSW 17,946,000 - 1,645,000 = 16,301,000; DK 78,774,745 - 17,575,527 = 61,199,218 (FC-census).
- Issued filed under `SharesIssued` (NSP: `SharesIssued` 55M with treasury in dollars only). R4 rejects it, so the result is C.
- Shares held by subsidiaries, rabbi trusts or ESOPs that are not called treasury (AC-25, open).
- Rounded inputs (R5).

**Accountant?** Not for the identity. AC-25 (treasury-like holdings) remains open and is unaffected.

## 4. A4: issued only
**Accounting meaning.** If an issuer holds no treasury stock (it retires repurchased shares, as in Maryland and many other states), then issued = outstanding.

**Condition: no treasury line of any kind in the accession at D or at the prior balance-sheet date.** That means no fact whose name contains `TreasuryStock`, and no context with a `TreasuryStock*Member`. A text mention of the "treasury stock method" for EPS does not count.

**Evidence:**
- MDU 0000067716-26-000072: issued 210,349,456 (undimensioned and in the equity column); `CommonStockValueOutstanding`; no treasury fact, context or text (FC).
- TROW 0001628280-26-051335: issued 213,312,000; no treasury fact; the main document mentions only the "treasury stock method" (FC).
- SRTA 0001628280-26-052256: issued 88,466,806; the equity statement shows "Retirement of common stock (675,334)"; no treasury fact (FC).
- Refusals:
  - HOG 0000793952-26-000061: `TreasuryStockCommonValue` 2,275,356K with no share count (FC).
  - NSP 0001000753-26-000087: `TreasuryStockValue` 824M (FC).
  - PKOH: treasury column `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` [TreasuryStockCommonMember] -95.3M (FC).

**Failure modes:**
- Treasury held in dollars only. The condition catches it.
- Holdings that are not called treasury: AS that none of MDU, TROW or SRTA have any; only the instance and a text search were read.

**Accountant?** No.

## 5. SPAC book value per share (definition ruling)
**FC, GUAC 0001829126-26-008903 at 2026-06-30:**
- undimensioned `CommonStockSharesOutstanding` 7,877,500 (founder shares);
- `StockholdersEquity` -10,484,793;
- `TemporaryEquitySharesOutstanding` 31,510,000 at a redemption price of 10.04;
- `TemporaryEquityCarryingAmountAttributableToParent` 316,413,752 (PublicSharesMember).

Founder shares only gives -10,484,793 / 7,877,500 = **-1.33**.

**Ruling: founder shares only is WRONG to display**, even though each input is GAAP-correct:
- The numerator (permanent equity) and the denominator (non-redeemable shares) are internally consistent.
- But the priced security is the redeemable public share, which is 80% of common here. Its claim on the trust is excluded from both sides.
- A per-share figure labelled as the stock's book value would be -1.33 against a share redeemable at 10.04.
- This hits the **current A1 path**, not only the fallback (5 SPACs in the control set, FC-census).

The alternative, (permanent + temporary equity) / all common = 305,928,959 / 39,387,500 = 7.77, is a non-GAAP perimeter choice that needs the accountant (**AC-31**).

**Default until ruled:** give `not_applicable:redeemable_common_in_temporary_equity` (and route P/B the same way) when `TemporaryEquitySharesOutstanding` > 0 at D and that count is NOT fully explained by preferred members. A count is explained when its undimensioned value equals the sum of its preferred-member facts (`StatementClassOfStockAxis` preferred/series member, or `StatementEquityComponentsAxis=PreferredStockMember`).
- Redeemable preferred in temporary equity does not trigger this: it is outside both the numerator and the common count.
- Revision 2026-10-22, FC: STKS 0001104659-26-092751 files `TemporaryEquitySharesOutstanding` 160,000 twice, once undimensioned and once with [SeriesAPreferredStockMember, PreferredStockMember]. A rule that read only "undimensioned and untagged" would have hidden STKS by mistake.
- If the redeemable class cannot be identified, the default is hide.

## 6. HOVR "to be issued" line, and the HOVR blockers
**FC, HOVR 0001213900-26-108211 at 2026-08-31.** The balance sheet shows:
- "Class A ordinary shares ... 67,123,941 issued and outstanding" (175,754);
- "Class A ordinary shares to be issued" (21), tagged `CommonStockValue` / `SharesOutstanding` [ClassAOrdinarySharesToBeIssuedMember] = 8,204 shares.

Note 8 says these are shares "to be issued at a future date for services rendered". At 2026-05-31 the same line held 2,433,018 shares from exercised pre-funded warrants that were not yet issued.

**Ruling:** to-be-issued shares are **not outstanding**. They are excluded from the count, so A2 = 67,123,941. This matches the market cap contract (WO-21 3.1: outstanding only, pre-funded warrants excluded, AC-23), so P/B = price / BVPS stays consistent. The PRLD pre-funded warrants are treated the same way (FC: PRLD's basic EPS "including pre-funded warrants" uses a WASO of 98,388,593 against 79,757,131 outstanding). The equity amount for these shares stays in the numerator. That perimeter difference belongs to AC-23 (accountant, already open).

**HOVR is still blank for two other reasons:**
1. Its equity is **CAD** (statements "expressed in Canadian dollar 000's"; instance unit `iso4217:CAD`, FC). Our canonical `stockholders_equity` holds the CAD facts 73183954 (71,110,000) and 216945757 (67,657,000) as if they were USD (DI, core.fact unit `cad`). This is a monetary-unit defect (the IVDA pattern, ledger row 36), so the reason is `unit:non_usd_numerator`.
2. It has preferred equity of 6,277K. Our formula is "Stockholders' Equity / Shares Outstanding" (`expanded_definitions.py`), and the numerator includes preferred. **Numerator defect, routed:** the numerator should be common equity (SE minus preferred). That needs its own concept card.

## 7. ADS issuers
Balance-sheet counts are per ordinary share, while the priced unit is the ADS (ledger row 87). BVPS per ordinary share is arithmetically right but would mislead next to an ADS price. The share-count rule is unchanged. Display waits on NA-15 `mcap.ads_conversion@1` (BVPS per ADS = per-ordinary BVPS x ratio); until then the reason is `ads_basis_unconverted`. DBVT also has the "including treasury" problem (AC-25). NNDM's listing form is AS (FC-census).

## 8. Acceptance tests (expected denominator at D; inputs FC unless marked)
| Case | Accession, D | Expected |
|---|---|---|
| KO | 0001628280-26-028802, 2026-04-03 | A1 none (the 4,303M fact is the equity column). **A3** = 7,040,000,000 - 2,737,000,000 = **4,303,000,000**, decimals -6. R2 corroborates (equity column 4,303M = A3). Cover 4,302,482,418 is 0.012% off, so the cell is published |
| SEV | 0001493152-26-037373, 2026-06-30 | **A2** = 11,983,010 (A) + 25,439,653 (B) = **37,422,663**. Classes {A, B} on authorized, issued and outstanding; EPS per class equal (-0.30 Q2, -0.61 6M), two-class method. The cover is Class B only (28,560,115), 23.7% off, so the cell is **held `review:share_count_cover_divergence`**. It never takes 28,560,115 |
| PRLD | 0001193125-26-343475, 2026-06-30 | **A2** = 65,028,996 (voting) + 14,728,135 (non-voting) = **79,757,131**. EPS undimensioned only, so all classes are summed. Cover 79,803,485 is 0.06% off, so the cell is published. Never WASO 98,388,593 (pre-funded warrants) |
| PKOH | 0000076282-26-000028, 2026-06-30 | The only share fact at D is the equity column 18,575,430, which R2 rejects. No issued or treasury share facts; a treasury dollar column exists, so A4 is refused. Result: **C `incomplete:denominator:no_balance_sheet_date_share_count`**. Never 18,575,430; never the cover 14,490,010 |
| HUBB | 0001628280-26-029110, 2026-03-31 | No share-unit fact at D (instance FC; the census's text search found only the cover and WASO). Result: **C**, same reason |
| HOVR | 0001213900-26-108211, 2026-08-31 | Denominator **67,123,941** (the to-be-issued 8,204 is excluded). BVPS hidden `unit:non_usd_numerator` |
| GUAC | 0001829126-26-008903, 2026-06-30 | A1 7,877,500 exists, but `TemporaryEquitySharesOutstanding` 31,510,000 > 0, so the result is `not_applicable:redeemable_common_in_temporary_equity`. Never -1.33 |
| RPAY (negative) | 0001193125-26-342440, 2026-06-30 | A2 with Class A only = 82,892,959 (Class V 100 excluded: no class EPS). Equals issued 96,268,848 - treasury 13,375,889 under R1 |
| CSW, DK (trap) | FC-census | A3 = 16,301,000 and 61,199,218; the equity column (17,946,378; 78,774,745) is rejected |
| MDU, TROW, SRTA | see section 4 | A4 = 210,349,456; 213,312,000 (decimals -3); 88,466,806 |
| HOG, NSP | see section 4 | C (a treasury value line with no share count) |
| BRK (negative) | 0001193125-26-083899 (tag card, FC by the Tag Expert) | Per-class EPS unequal, so `class_rights_unequal` unless the 1/1,500 conversion is applied. Never A + B |
| Mutation checks | synthetic | Drop one class member, so `class_count_incomplete`. Negative treasury, so quarantine. `SharesIssued` swapped in for `CommonStockSharesIssued`, so C. Cover equal to the A-path but the A-path missing, so C (the cover is never a value) |

## 9. Open items and routing
- **Accountant:** AC-31 (new: SPAC perimeter); AC-22 (Up-C); AC-23 (pre-funded warrants and to-be-issued shares in the numerator vs the count); AC-24 (unequal or unlisted classes); AC-25 (treasury-like holdings). Defaults are stated above, and all of them hide.
- **Standardization Lead (next card):** a common-equity numerator for BVPS (SE minus preferred; HOVR 6,277K preferred).
- **Data Engineer:** enforce USD on monetary canonical concepts (HOVR CAD equity); the class-member reader (shared with WO-21 3.6).
- **Lane 2:** state the 194/167/27 probe query (from the census).
- **Not tested:** 10-K filers; populations beyond the seed-1 300 sample; the rendered R-file view; whether redeemable preferred tagged without a member could falsely trigger section 5; holdings that are not called treasury at the A4 companies (AS none); the BRK conversion arithmetic.
