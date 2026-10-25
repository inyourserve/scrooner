# Problem playbook: tags, problems, fixes (top-1000 campaign)

Built from shards S000-S018 and verifier passes VERIFY-W1/W2 (2026-10-18/19). One entry per problem type. Each entry says what the problem looks like, which XBRL tags are involved, how to spot it, the fix rule, and real examples. Evidence labels: **FC** = FILING-CHECKED (the filing was opened); **DI** = DATA-INFERRED (from our tables only). Detail and accessions are in `results/S###.md`. Status and owners are in `status.md` and `fix-register.md`.

Updated as shards finish. If a rule here and a filing disagree, the filing wins.

## How to read a company's numbers (the habits behind every entry)
1. **Open the face statement** (SEC Financial Report R2/R4) before trusting a tag. A tag name is a claim, not proof.
2. **Check the period by start/end dates**, never by companyfacts `fy`/`fp`.
3. **Check the form.** 10-K/10-Q/10-K/A/10-Q/A/10-KT are primary sources. DEF 14A, 8-K, S-1 and 20-F rows must never win.
4. **Check scale and unit.** Thousands vs dollars, USD vs CAD, ADS vs ordinary shares, per-class shares.
5. **Check age.** A "latest" value older than the latest filing is stale, not current.

---

## A. Wrong values shown today (fix first)

### A1. Total debt composition (most common; 25+ of the first ~180 companies)
- **Looks like:** total debt equals only current debt, or only short-term borrowings, or counts the current portion twice, or is 0.
- **Tags:** `LongTermDebt`, `LongTermDebtNoncurrent`, `LongTermDebtCurrent`, `DebtCurrent`, `ShortTermBorrowings`, `CommercialPaper`, `LongTermDebtAndCapitalLeaseObligations` (unmapped family), `ConvertibleDebtNoncurrent`, `ConvertibleLongTermNotesPayable`, `UnsecuredLongTermDebt`, `NotesPayable`, `SeniorNotes`.
- **Traps:**
  - `LongTermDebt` *includes* its current portion. Adding `DebtCurrent` on top double counts it.
  - A tiny bare `LongTermDebt` fact can outrank the face lines (MAR: 23M vs 16,915M).
  - Some companies file debt only per segment (GM, KKR).
  - A "0" can be one component's reported zero (ABBV).
- **Spot it:** total_debt below the sum of the face debt lines, or above the face total. Base and resolved debt rows disagree. A debt-free company shows an old non-zero value.
- **Fix rule:** build total debt from the face statement:
  - short-term borrowings + commercial paper + current portion of long-term debt + long-term debt noncurrent (+ finance leases, per the Standardization ruling);
  - never add `DebtCurrent` to a `LongTermDebt` that already includes it;
  - an explicit reported zero or a "no borrowings" statement means 0, while silence means blank;
  - run a full-population dry-run before any write.
- **Examples:**
  - Too low:
    - LLY 7,050M vs 54,908M (FC, 0000059478-26-000081 R4)
    - RTX 229M vs 37,383M (FC)
    - SCHW 22,669M vs 37,114M (FC)
    - MU 2,792M vs 5,179M (FC)
    - WMT 39,932M vs 50,411M (FC)
    - ADBE 4,766M vs 6,363M (FC)
    - LITE FY2025 10.6M vs 2,573.2M (FC)
    - CMI 7,236M vs 7,695M, loans payable omitted (FC)
  - Double counted:
    - CSCO 33,033M vs 29,533M (FC)
    - TMO (FC)
    - DELL (DI)
    - UBER 14,720M vs 12,723M (FC)
  - Zero or outdated:
    - ABBV 0 vs 70,822M (FC)
    - CME 0 vs 3,424M (FC)
    - NET 0 vs 3,270M convertible notes (FC)
    - VRTX 105M from 2011 (DI)

### A2. Bank, broker and exchange revenue
- **Looks like:** revenue is gross interest income, or a component, not the company's net revenue line.
- **Tags:**
  - correct: `RevenuesNetOfInterestExpense` (face total for banks, brokers, AXP)
  - currently used: `InterestAndDividendIncomeOperating` (gross)
- **Fix rule:**
  - banks and brokers: map `RevenuesNetOfInterestExpense` ahead of gross interest income;
  - exchanges (ICE, CME): use net revenue, after transaction-based expenses.
- **Examples:**
  - Banks and brokers:
    - BAC 138,566M vs 113,097M (FC, 0000070858-26-000157 R3)
    - MS 15,902M vs 21,348M (FC)
    - WFC, GS (DI)
    - USB FY 30,970M vs 28,540M (FC)
    - AXP 11,212M vs 19,637M (FC: 11.2B is a segment-note figure)
  - Exchanges:
    - ICE 3,611M vs 2,666M (FC)
  - Not affected: SCHW, PNC, HOOD revenue is correct.

### A3. ASC 606 "contract revenue" used as total revenue
- **Looks like:** revenue a few percent (or far) below the reported total, because lease, derivative or other non-contract revenue is left out. Sometimes it is *above* the total (WMB).
- **Tags:** `RevenueFromContractWithCustomerExcludingAssessedTax` (subset) vs `Revenues` (total).
- **Spot it:** the 606 value differs from `Revenues` in the same filing and period.
- **Fix rule:**
  - prefer `Revenues` (the face total) whenever both are filed;
  - never use 606 alone when the face shows a larger or smaller total;
  - a fix must cover *future* periods too (AMT regressed on new quarters).
- **Examples:**
  - AMT Q2-2026 211.1M vs 2,749.1M (FC, 0001053507-26-000133 R4)
  - CEG Q2 5,843M vs 7,504M (FC)
  - FCX FY2025 25,186M vs 25,915M (FC)
  - DUK Q1 8,995M vs 9,178M (FC)
  - KMI Q2 4,098M vs 4,477M (FC)
  - CP (FC)
  - WMB +11% to +56% above total (FC)
  - COF (DI)

### A4. Proxy statement or 8-K value wins over the 10-K
- **Looks like:** net income slightly or wildly off, sometimes 1,000x or 1,000,000x too small.
- **Why:** DEF 14A pay-versus-performance tables tag `NetIncomeLoss`, sometimes in thousands, sometimes for continuing operations only.
- **Fix rule:**
  - only 10-K/10-Q/10-K/A/10-Q/A/10-KT facts may become a canonical value;
  - **a non-authoritative DEF 14A fact must never be selected** (that breaks the project's hard rule; MDT shows it is being broken).
- **Examples:**
  - MRK FY2021 12,345M vs 13,049M (FC)
  - MDT net income 4,801 *dollars* vs 4,801M, FY2022-26 (DI, fact 64871764). TTM ROE shows 0.86% vs about 10.4%.
  - SCHW base 1000x small; shown 8,417M vs 8,852M (FC)
  - NFLX, HD (precision only)
  - FTNT derived Q4 traced to DEF 14A

### A5. Net income includes noncontrolling interest
- **Tags:** `ProfitLoss` (includes NCI) used when `NetIncomeLoss` is not tagged.
- **Fix rule:**
  - net income means attributable to the parent;
  - use `NetIncomeLoss`, or `ProfitLoss` minus `NetIncomeLossAttributableToNoncontrollingInterest`;
  - never use bare `ProfitLoss`.
- **Examples:**
  - FCX Q1-2026 1,387M vs 881M (FC; TTM ~42% high)
  - AMT 887.5 vs 867.5 (FC)
  - CMI Q2 968M vs 932M (FC)
  - APH, CEG, EQIX, BNY (DI)
  - Equity version: T equity includes 15,990M of NCI, so ROE and P/B are skewed (FC).

### A6. Gross margin from a partial cost line
- **Looks like:** an implausible gross margin (88-89%) at insurers, energy companies and waste haulers.
- **Fix rule:**
  - if the company presents no gross profit, leave gross margin blank with the reason "not presented";
  - never compute revenue minus one cost line.
- **Examples:**
  - UNH 88.6% (FC)
  - ELV 89.1%: only cost of products 5,492M is subtracted, while benefit expense of 37,024M is left out (FC)
  - CVX 43.6% (FC)
  - WM 40.9% (cost line excludes D&A) (FC)
  - RCL 49.1%, RSG 42.0% (FC)

### A7. Market cap: share count wrong
- **Causes:**
  - ADS ratio ignored (AKTX 1 ADS = 80,000 ordinary shares; ZLAB, SCNI, KZIA, AMRN, GPCR, DBVT);
  - the filer's own XBRL has diluted shares 1000x too large (TBLA, RPAY);
  - multi-class cover pages dropped, so only one class is counted (SPCX understated: about $1.92T, not $710B);
  - per-class only, falling back to 0 (SHOP);
  - CAD statements divided into a USD price (CP, about 28% off on P/E, P/S and P/B).
- **Tags:** `dei:EntityCommonStockSharesOutstanding` (sum every class), `dei:Security12bTitle` (ADS ratio), `WeightedAverageNumberOfDilutedSharesOutstanding` (fallback only, with a scale check).
- **Fix rule (MCAP-SHARES, S000):**
  - sum the cover classes;
  - divide by the ADS ratio;
  - reject diluted shares more than 10x off the company's own history or more than 100x off the cover count;
  - hold for review if market cap is over 8x public float, over 200x revenue, or follows a 3x share jump with no split;
  - require USD statements or convert them.
- Code: `mapper/price_metrics.py` lines 179-247, 362.

### A8. Stale "latest" values shown as current (very common)
- **Looks like:** the latest value of a metric comes from years ago because the company switched tags and we only map the old one.
- **Examples:**
  - Operating income: SHW 2024, TRV 2015, BX 2018 (no subtotal presented), GE 2012 (segment profit, FC), ADP 2014, ETN 2019, JCI 2016, JNJ 2015.
  - Gross margin: TMO 2019, RTX 2020, SBUX 2020, CDNS 2012, INTU 2020, GD 2019, KMI 2022, GM 2021.
  - Shares: CMCSA 2009 (fcf_per_share 9.91 vs ~5.77), ACN 2010, MA 2010, CME 2010 (66.6M vs 359.6M), REGN 2012, UPS 2010, RPAY 2018.
  - Debt: PANW FY2023, CDNS 2018.
  - Interest expense: stale at 8 of 10 in several shards (LOW 2011, KMI coverage from 2014).
  - Cash flow and dividends: VZ capex 2019, COP capex 2022, GLW capex 2020, EOG dividends 2009.
- **Fix rule:**
  - add a staleness guard: a "latest" value older than the company's latest 10-K/10-Q period shows blank with the reason "not reported in the latest filing";
  - then map the new tag.

### A9. Derived values that cannot be derived
- **Per-share values derived by subtraction:**
  - KLAC Q4 diluted EPS -22.61 vs filed $1.04, because pre- and post-split figures were mixed (FC, 8-K Ex. 99.1)
  - Visa Q4 dividend -1.18: the quarterly DPS was tagged on the full-year context (FC)
  - Rule: never derive EPS or DPS by subtraction.
- **Sign flips between 10-K and 10-Q:** Disney interest expense is negative in 10-Ks and positive in 10-Qs, so the derived Q4 is -3.4B vs about +416M (DI).
- **Double subtraction:** WELL operating income -1,650M; the opex total already includes property costs and interest (FC).
- **Missing splits:** BKNG 25-for-1, so P/E shows 1.23 vs about 18 (DI).

### A10. Ratios that mean nothing
- **Negative or near-zero equity:**
  - ABBV, PM, DELL (ROE -797%), MO, HLT, MSI, ORLY, MCK (ROIC 1,640%)
  - CL P/B 319
- **Negative invested capital:** FTNT ROIC -222.6%.
- **Growth on a negative base:** COF EPS went from -8.58 to +4.73 but shows -155%.
- **Variable dividends:** PGR trailing yield shows 6.36%.
- **Customer funds on the balance sheet:** CME, ADP and ICE current ratio and ROA.
- **Captive finance arm:** GM FCF yield 19.3%, net cash -110.6B.
- **Fix rule:**
  - show blank with a reason when the denominator is negative or near zero;
  - YoY growth on a negative base is blank, as multi-year growth already is.

---

## B. Data that exists at SEC but never reaches us

### B1. Latest 10-Q not in SEC companyfacts (12+ companies)
- **Looks like:** the company page stops one quarter short. The filing is in `core.filing` with 0 facts.
- **Cause (FC, VERIFY-W2):** the filings carry full XBRL, but SEC's companyfacts feed, our only source, does not include those accessions yet. Frames sometimes does.
- **Fix rule:** when companyfacts lacks a filed accession, fall back to the filing's own XBRL instance or the quarterly Financial Statement Data Sets.
- **Examples:** KO, C (2 quarters), NEE, WELL, ABT, CB, SPGI, PLD, HCA, DUK, MDLZ, GD, JCI, CDNS.

### B2. History lost at a new registrant (predecessor CIK)
- **Re-registration, so the old history is not linked:** BLK (new CIK 2024), DIS (2019), XOM (old CIK 34088 missing), MRVL, LIN, SHOP.
- **Opposite case:** HWM still carries Alcoa-era costs, dividends and SIC.
- **Fix rule:** keep a predecessor/successor CIK link table and join history across it, with a re-presentation note.

### B3. Stale companyfacts fetch
- DE last fetched 2026-08-22, so its Q3 FY26 10-Q is missing.

---

## C. Tags we don't map yet (cause blanks)

| Line | Tag(s) seen | Companies |
|---|---|---|
| E&P capex | `PaymentsToAcquireOilAndGasPropertyAndEquipment` (60-72 filers) | EOG |
| Other capex | `PaymentsToAcquireOtherProductiveAssets`, `PaymentsForCapitalImprovements` | VZ, GLW |
| Receivables change | `IncreaseDecreaseInReceivables` | 3 of 10 in S004 |
| Receivables | `ReceivablesNetCurrent` | LMT, MO |
| Other non-operating | `OtherNonoperatingIncomeExpense` | 3-4 per shard |
| Interest expense | `InterestExpenseNonoperating`, interest-and-debt expense (BA) | 6 in S007 |
| Interest income | `InvestmentIncomeNonoperating` | ABNB, NET, SNOW, CME |
| Dividends paid | `PaymentsOfOrdinaryDividends` | GE, PFE, CL |
| D&A | separate Depreciation + Amortization; company-specific tags | GOOG, MSFT, AVGO, ABBV, ORCL, TXN, GEV, ISRG, ACN, SCHW |
| Cost of revenue | only on product/service members (no total) | CDNS, INTU, GD |
| EPS | continuing-ops EPS only; per-class EPS only | ABNB, GD; V |
| Pretax | Domestic + Foreign only; `IncomeLossAttributableToParent` (an after-tax element used for pretax) | MCD; INTU, LITE (stuck at 2020; 0001628280-26-057358 R3) |
| PP&E | PP&E including finance-lease right-of-use assets | C, + 4 in S019 |
| Cash | `us-gaap:Cash` (not CashAndCashEquivalents...) | SLB (3,172M from 2015 vs 2,743M) |
| Buybacks | `PaymentsForRepurchaseOfEquity` (426 filers) | SLB, SHW |
| MLP equity and distributions | `PartnersCapital`, `DistributionMadeToLimitedPartner*` | EPD (25 cells; false no_dividend_history) |
| Current debt | custom tag only | SLB (total debt 11,140M vs 12,798M) |
| Receivables | `ContractWithCustomerAssetNet` used for trade AR (LITE 520.3M) - company-scoped only: NOC uses it for unbilled | LITE |

**Guards (do NOT map):**
- An O&M-only tag is not total opex (WMB 597 vs 1,871).
- A combined "accounts and notes receivable" line is not plain receivables (PEP).
- `CostsAndExpenses` includes interest at CVX, AJG and HTZ.

Every new mapping needs a full-population coexistence check first.

---

## D. Wrong or missing blank reasons

- **False "pre-revenue" reasons:** MRK, ABBV, AMGN, LLY, ABT, GILD, VRTX, BMY (pharma); SCCO, NEM (mining, 13.4B revenue).
- **False "no dividend history":** DHR (paid 878M), C (5,372M), TMUS before its first dividend.
- **False financial-institution reason:** it fires if a company *ever* filed one of 5 tags, with no date or sector check (`coverage_matrix.py`). This hits MO (tobacco), HPE and ORLY, and shows the wrong text for PGR (insurer).
- **Wrong REIT reason:** WELL, an equity REIT, gets the mortgage-REIT reason.
- **No reason at all:** dividend and shareholder-return cells at non-payers (NOW, UBER, VRTX, FTNT, +18 in S012). These should use buybacks only, or show "does not pay dividends".
- **Debt-free companies:** blank instead of 0 (ISRG, 16 cells).

---

## E. Who is in the population

- **Foreign private issuers wrongly included:**
  - BMO and BNS were kept in by a legacy 10-K; BNS's 10-Ks are covered-bond ABS reports.
  - AEM and CNI never filed a 10-K.
  - All are excluded from the cohort (doc 02: V1 excludes 20-F/40-F filers).
- **Not companies:** IAU and SLV are commodity trusts.
- **Acquired or delisted but still active:** WBD (bought by Skydance 10-06; 8-K 0001193125-26-415055, Form 25, Form 15) still shows a $77.8B market cap on a stale price. Rule: Form 25 or Form 15 marks the company inactive.
- **Missing large companies:** BRK-A, FWONA, BAM, PLNT, UHAL and SUN have a blank market cap (shard S102).

---

## F. Measurement: how coverage is counted

- `company_data_point_coverage.has_value` is true if **any past period** had a value (`coverage_matrix.py:746`, `bool_or`). A metric blank today still counts as filled.
  - S014 found 79 such cells; S018 found 65.
  - So 80.86% overstates coverage. A "latest period" coverage measure is needed before any 100% claim.
- "Nothing relevant filed" in lineage means none of *our* tags were filed. It is not proof the line is absent.

---

## Sector notes (templates)

- **Banks and brokers:** use the bank revenue line; fcf_yield, debt_to_equity and net_cash do not apply; net interest income must come from the face (PNC 4,107M, HOOD 389M).
- **Insurers:** no gross margin; use benefit and claims expense. Variable dividends (PGR) distort yield.
- **Asset managers** (BLK, BX, KKR, APO): need their own template; debt and EPS go stale.
- **REITs** (AMT, PLD, WELL, EQIX, SPG, DLR): lease revenue is outside ASC 606; FFO is not in XBRL; whether capital improvements count as capex is undecided.
- **Utilities and power** (NEE, DUK, CEG): custom capex and interest tags; 606 subset revenue.
- **Energy** (EOG, OXY, COP, SLB): E&P capex tag; interest incurred vs expensed (SCCO).
- **Captive finance** (GM, DE): split consolidated from industrial-only figures.
- **Exchanges and payroll** (ICE, CME, ADP): customer funds on the balance sheet.
- **Spin-offs and re-presentations** (MMM Solventum, SPGI, PPG): blank growth across the break, with a reason.
