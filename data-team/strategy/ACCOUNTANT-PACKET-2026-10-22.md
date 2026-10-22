# Accountant packet: 21 decisions for Scrooner's financial data (2026-10-22)

Prepared by: Standardization Lead (AI research role, data-team/11). **Every recommendation here is a proposal. None is approved until the named accountant signs the card.** Source of the cards: `data-team/strategy/team/WO-REVIEW-standardization-lead.md` section 2C. Evidence for each number is cited on the card with its label: FILING-CHECKED (someone opened the filing; accession given), DATA-INFERRED (from our tables or SEC data sets, no filing opened), NOT MEASURED. Cell counts are from the cited evidence files and are not re-measured for this packet.

Printing: each card starts on a new page when this file is rendered to HTML or PDF. Sitting order follows the founder-approved plan (doc 49 section 9, item 14).

<div style="page-break-after: always"></div>

## Cover note for the founder: who, how long, how to get it done cheaply and fast

**What this is.** Scrooner shows numbers from SEC filings, for example total debt, free cash flow, EBITDA, dividend yield and P/E. For 21 of them, companies present the underlying lines differently, so we need one consistent definition for every company. That is an accounting judgement, not an engineering one. Until each card is answered, the affected cells stay hidden with a reason (they are not guessed). Answering a card unblocks those cells for every company at once.

**Who this person should be**
- **A licensed US CPA** (active license), with **at least 8 years of US GAAP financial reporting for SEC registrants**: preparing 10-K/10-Q filings (controller, SEC reporting manager), or auditing them (audit senior manager or above at a firm with SEC clients).
- Working knowledge of: leases (ASC 842), revenue (ASC 606), cash flows (ASC 230), EPS (ASC 260), noncontrolling interests (ASC 810), discontinued operations (ASC 205-20), banks (ASC 942) and insurers (ASC 944). An analyst background (CFA charterholder, equity research) helps on AC-13, AC-14 and AC-16, but does not replace the CPA for the meaning cards.
- **Financial-institution depth for AC-3, AC-10 and AC-11.** If the main reviewer is not comfortable with banks and insurers, add a second short engagement (2-3 days) with a bank or insurance reporting specialist for those three cards only.
- **Independent of the proposer.** It must not be anyone who wrote these rules, and no AI agent can answer for them (the plan's own rule: nobody approves their own rule).
- XBRL knowledge is helpful but not required. The cards are written in accounting terms, with the filing page for each example.

**What we are asking for, and what we are not**
- Asked: pick an option on each card (or write a better one), state any condition, and sign. A short reason is enough.
- Not asked: an audit opinion, an attestation, or a check of our numbers. The engagement letter should say "methodology advice for a financial data product; no assurance is given". This keeps the price and the liability low.
- All examples are public SEC filings, so no confidential client data is involved.

**Time needed**
- About half a day per card, including the pre-read: **about 10-11 working days in total**. If the accountant agrees with a recommendation, the card is usually much faster. Disagreements and the bank/insurer cards take longer.
- It can be done in sittings. Proposed: 6 remote sittings of about 1.5-2 days of effort each, about one per week, in the order below. Cards 1-12 unblock the most cells. Cards 13-21 can follow later.

| Sitting | Cards | Theme | Unblocks (summary) |
|---|---|---|---|
| 1 | AC-1, AC-5, AC-6 | Coupled perimeters: finance leases, capex, D&A | EV and every EV multiple, debt ratios, FCF family, EBITDA family |
| 2 | AC-13, AC-14, AC-8 | Dividends, P/E basis, net income attribution | dividend yield, payout, P/E, PEG, net margin, ROE |
| 3 | AC-10, AC-2 | Bank revenue; debt composition | bank revenue and P/S; about 1,086 total-debt capture defects |
| 4 | AC-9, AC-7 | Revenue beyond the clean subset; operating income without a subtotal | revenue for hidden companies; 314 EBITDA cells |
| 5 | AC-15, AC-19, AC-20 | Interest, restatement basis, continuing operations | interest coverage; growth and TTM certification; FCF with discontinued operations |
| 6 | AC-3, AC-4, AC-11, AC-12, AC-16, AC-17, AC-18, AC-21 | Remaining special cases | insurer and REIT templates, zero debt, ROIC/ROE, quick ratio, CCC, goodwill %, OCI, cash perimeter |

**The cheapest fast route (recommendation)**
1. **One freelance CPA on a fixed fee per card**, found through a finance-professional marketplace or by referral from a small CPA firm with SEC clients. Ask two or three candidates for a quote against this packet. A fixed fee per card avoids open-ended hourly billing.
2. **Send the packet in advance.** Each sitting is a 2-3 hour video call for the open questions; the rest is the reviewer's own reading. Answers are written on the card's answer block. A scanned or e-signed page is enough.
3. **Batch by sitting**, not card by card. Cards in one sitting share evidence, and AC-1, AC-5 and AC-6 must be decided together anyway.
4. **Start with sitting 1 even if only one candidate is ready.** It unblocks the most cells.
5. Budget (ASSUMED; not a quote): at a market rate of roughly $100-250 per hour, about 80-90 hours is roughly $8,000-22,000. A semi-retired SEC reporting professional, or an accounting faculty member with SEC reporting background, is often at the low end. Get two quotes; do not rely on this range.

**What happens with each signed card.** The answer becomes a versioned definition (a MAJOR version under the versioning spec, `data-team/strategy/team/DEFINITION-VERSIONING-SPEC.md`). We recompute from stored filing data (no filing is re-read), publish a before/after list per company, and an independent Verifier checks a sample against the filings. Only then do the cells go live. A later change of mind is a new version with a published diff, never a silent edit.

**Before sitting 2 and sitting 6:** the Standardization Lead adds the missing filing examples for AC-11, AC-12, AC-13, AC-14, AC-17, AC-18, AC-19, AC-20 and AC-21 (3-5 filings each; about 5 agent-days). Those cards say "examples pending" below.

<div style="page-break-after: always"></div>

## Card 1 of 21. AC-1: Are finance leases part of "total debt"? (and the coupled interest, D&A and FCF choices)
**Sitting 1.** Evidence: R3 C1/C2, data-team/27 D3, ledger row 53.

**The question in plain words.** Many companies owe money in two forms: borrowings (loans, bonds, commercial paper) and finance-lease obligations. Some put both in one balance-sheet line; others show them separately. Should Scrooner's screen "total debt" include finance leases? The answer must then carry through consistently:
- finance-lease interest in interest expense;
- finance-lease right-of-use amortization in D&A (EBITDA);
- lease principal payments in free cash flow.

Sub-question C2: where a company shows only a combined line, may we subtract its separately disclosed finance-lease amount to get borrowings only?

**Example (FILING-CHECKED).** Walmart at 2025-10-31 (0000104169-25-000191 R2, R4):
- Borrowings 46,369M; with finance leases (842 + 5,916) 53,127M (+14.6%).
- Debt interest 563M; finance-lease interest 121M.
- Operating leases are excluded under every option (wave1 1.3-1.4; CATO, ATEX ledger rows).

| Option | What users see | Cells / companies affected |
|---|---|---|
| (a) Exclude finance leases everywhere | "Borrowings" everywhere; combined-line filers need the C2 subtraction or show "partial" | SEC data sets 2025q4: lease-combined debt tag on the face 516 filings; separate finance-lease line 443; both 18 (DATA-INFERRED). Cohort cells NOT MEASURED |
| (b) Include everywhere | debt includes finance leases; add `FinanceLeaseLiability*` where not already inside a combined line (risk of double counting) | same filings |
| (c) Today's behavior | in when the company combines them, out when it shows them separately: inconsistent between companies | current state |

**Recommendation.**
- Use debt including finance leases for EV, net debt, debt/EBITDA and interest coverage, with finance-lease ROU amortization added to D&A and lease interest added to interest expense.
- Also show "borrowings" (excluding leases) as its own labelled line.
- Allow C2 subtraction only where the company's own note or calculation shows combined = debt + that lease amount.
- Until answered, show the composition path ("includes finance leases").

**Blocked until answered:** borrowings and debt-incl-leases values, EV and every EV multiple, D/E, net debt/EBITDA, interest coverage, FCF after lease principal; the debt and interest composers.

**Answer.**
- Option chosen: ______
- Conditions or changes: ______________________________________________
- C2 subtraction allowed? yes / no / only if: ______________________
- Name, credential, license state/number: ______________________
- Signature and date: ______________________

<div style="page-break-after: always"></div>

## Card 2 of 21. AC-5: What counts as capital expenditure?
**Sitting 1.** Evidence: R3 C4-C6, C8; ledger rows 54, 59; doc 46 (cohort capex defects).

**The question in plain words.** Capex is the cash spent on long-lived operating assets, and companies split it across lines. Which of these are capex for free cash flow?
1. Capitalized internal-use software.
2. Purchases of intangibles (licences, spectrum, patents).
3. A single line labelled "Capital expenditures" tagged as productive assets, which may include intangibles.
4. "PP&E net of financings".
5. Rental-fleet purchases.
6. Every purchase row in the investing section, when there is more than one.

**Examples (FILING-CHECKED).**
- Aptiv "Capital expenditures" 489M is on `PaymentsToAcquireProductiveAssets`, and our capex is blank (0001521332-25-000051 R6).
- ArcBest software 9,958K is a separate line, and PP&E is "net of financings" (0001104659-25-106816 R8).
- Air Lease: the standard capex tag holds only 237,683K of furnishings; flight equipment 2,348,253K and deposits 1,045,667K are on other lines (0001628280-26-007707 R8).

| Option | What users see | Cells affected |
|---|---|---|
| (a) Software IN; intangibles a separate line; a "productive assets" capex line accepted with a flag; net-of-financings flagged; rental fleet in a separate template; all face capex rows summed | consistent FCF; flags where the company's line is broader | SEC data sets: PP&E only 2,514 filings; PP&E + intangibles 321; PP&E + software 146; two or three PP&E lines 137; custom only 53; about 152 FY2025 10-K filers with other capex lines >= 10% of the PP&E line (DATA-INFERRED). Cohort capex defects 1,567 cells (doc 46) |
| (b) PP&E tag only (today) | understates Aptiv (blank), ArcBest, Air Lease; FCF overstated where software is large | as today |
| (c) PP&E + software + intangibles | FCF lower for acquirers of licences | same filings |

**Recommendation:** (a). It is coupled with AC-6: if software is in capex, software amortization is in D&A.

**Blocked until answered:** FCF, FCF margin, FCF yield, FCF per share, capex % revenue, FCF growth, "FCF greater than net income"; the temporary hides from NA-10 convert to values.

**Answer.**
- Option chosen: ______
- (1) software ___ (2) intangibles ___ (3) productive-assets line ___ (4) net of financings ___ (5) rental fleet ___ (6) sum all rows ___
- Conditions: ______________________________________________
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 3 of 21. AC-6: What is inside D&A for EBITDA?
**Sitting 1.** Evidence: R3 C3, C4, C7, C11, C12, 5.1; S3 item 12; ledger rows 50, 52.

**The question in plain words.** EBITDA adds back depreciation and amortization, but the cash-flow add-backs come in many pieces. Which pieces count?
1. Depletion (oil and gas, mining).
2. Capitalized software amortization.
3. When a company labels a line "Depreciation and amortization" but tags it `Depreciation`, may we treat the label as evidence that amortization is inside?
4. Content, regulatory-asset and contract-cost amortization.
5. Asset-retirement accretion.
6. Amortization of debt issuance costs (we propose OUT: it is interest).
7. When there are no finite-lived intangibles, is intangible amortization zero?

**Examples (FILING-CHECKED).**
- AMD 9M 2025: 556 + 1,697 = 2,253 (0000002488-25-000166 R6).
- Aptiv 9M: 585 + 156 = 741, with debt-cost amortization of 7 left out (0001521332-25-000051 R6).
- Kura Sushi: an income-statement D&A sub-line (448K) vs the cash-flow total (14,046K) (0001193125-25-269773 R4/R6).
- Gilead: composition unknown (partial).

| Option | What users see | Cells affected |
|---|---|---|
| (a) Depletion IN, software IN, label accepted when only intangibles are shown separately, content/regulatory/contract-cost OUT, accretion OUT, debt cost OUT, zero only with a "no intangibles" note | consistent EBITDA from the cash-flow face | SEC data sets: one combined line 2,286 filings; depreciation only 427; depreciation + separate intangibles 286; debt-cost amortization lines 1,439; ROU amortization 823 (DATA-INFERRED). Cohort: 710 cells where D&A is filed only as two lines (MSFT, GOOG, ABT, AMD); EBITDA 427 and EBITDA margin 452 blank |
| (b) Today: the larger of two tags | perimeter chosen by size, fitted to a vendor | as today |

**Recommendation:** (a), with finance-lease ROU amortization following the AC-1 answer.

**Blocked until answered:** EBITDA, EBITDA margin, EV/EBITDA, debt/EBITDA, net debt/EBITDA.

**Answer.**
- Option chosen: ______
- (1) depletion ___ (2) software ___ (3) label as evidence ___ (4) content/regulatory/contract ___ (5) accretion ___ (6) debt cost ___ (7) zero rule ___
- Conditions: ______________________________________________
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 4 of 21. AC-13: Dividend yield, payout ratio and MLP distributions
**Sitting 2.** Evidence: S3 items 2 and 10; 42-EVIDENCE section 2e; ledger rows 66, 71, 72. **Examples partly ready; two more pending (CAT lumpy declarations, an MLP).**

**The question in plain words.** We will no longer derive a fourth-quarter dividend per share by subtraction, because it gives nonsense (NA-1). The questions:
1. What should dividend yield be, and should it use dividends declared or paid?
2. Are distributions by master limited partnerships "dividends to common"?
3. Does `PaymentsOfOrdinaryDividends`, which some filers use and which can include preferred dividends, count as common dividends?

**Examples (FILING-CHECKED).**
- Visa and Lear tag the quarterly rate (0.59, 0.77) on the full-year context, so FY minus 9M gives -1.18 and -1.54 (V 0001403161-25-000089 R8; LEA 0000842162-26-000011, the LEA conclusion DATA-INFERRED).
- Pfizer files dividends under `PaymentsOfOrdinaryDividends`, so our total shareholder yield shows -0.25% against a 5.7% dividend yield (0000078003-26-000095 R8).

| Option for dividend yield | What users see | Cells affected |
|---|---|---|
| (a) Latest filed FY dividends declared per share / current price, guarded by NA-3, labelled "FY<year> dividends declared per share" | up to 12 months stale but filed | dividend_yield rows using a derived DPS: 420 (top 1000), 938 (all); `missing:dividends_per_share_ttm` 453 in the cohort (DATA-INFERRED, 42-EVIDENCE, S3) |
| (b) TTM common dividends paid (cash flow, additive) / market cap | current, but cash paid, not declared | dividends_paid blank 280 in the cohort |
| (c) Sum of four quarterly DPS | blocked by NA-1 | n/a |
| (d) Latest quarterly rate x 4 | not reliably in XBRL | n/a |

**Recommendation.**
- Dividend yield: (a), with (b) as a cross-check that holds the cell when the two disagree beyond a stated band.
- Payout ratio: FY DPS / FY diluted EPS for the same FY, "Not meaningful" when EPS <= 0. Affects 7,289 payout rows (DATA-INFERRED).
- MLP distributions count for MLPs, labelled "distributions" (CQP, EPD, ET, MPLX, PAA).
- `PaymentsOfOrdinaryDividends` counts as common dividends only after the Tag Mapper's check shows preferred is not inside; otherwise company by company.

**Blocked until answered:** dividend yield, payout ratio, dividends % FCF, the dividend term in total shareholder yield, DPS growth (3,739 / 3,399 rows), dividend streak.

**Answer.**
- Yield option: ______ Declared or paid: ______ Cross-check band: ______
- Payout definition: ______
- MLP distributions: count / do not count: ______
- `PaymentsOfOrdinaryDividends`: ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 5 of 21. AC-14: P/E, TTM EPS and PEG basis
**Sitting 2.** Evidence: 42-EVIDENCE section 6; S3 item 2; ledger row 49. **Examples partly ready (MSFT, AAPL); one preferred-stock issuer pending.**

**The question in plain words.** There is no Q4 10-Q, and Q4 EPS cannot be derived by subtraction: the derived value differs from the company's own figure (MSFT Q4 FY26 4.80 vs 4.81 in the earnings release, 0001193125-26-323632 Ex. 99.1; AAPL Q4 FY25 1.84 vs 1.85, 0000320193-25-000077 Ex. 99.1; FILING-CHECKED). So a trailing-12-month EPS is unavailable for most companies. What should P/E and PEG use?

| Option for P/E | What users see | Cells affected |
|---|---|---|
| (a) Market cap / TTM net income attributable to common (parent net income minus preferred dividends where filed), basis labelled | current; basis stated | trailing_pe rows using a derived EPS: 874 (top 1000), 3,334 (all); displayed diluted EPS from derived facts: 5,263 Q4 cells (top 1000) (DATA-INFERRED) |
| (b) Market cap / TTM net income to parent (today's fallback, `price_metrics.py` 367-383) | ignores preferred dividends | same |
| (c) Price / latest filed FY diluted EPS | up to 12 months stale | same |
| (d) Price / sum of four filed quarters | rare (no Q4 10-Q) | same |

**Recommendation.**
- P/E: (a), falling back to (b) only where the filing shows no preferred stock and no participating securities.
- Do not display TTM EPS as a number. Show "FY<year> diluted EPS (filed)" plus the filed quarters.
- PEG = P/E (TTM basis) / FY-over-FY EPS growth, "Not meaningful" when either is not meaningful or growth <= 0. Today: negative P/E 117 cells; PEG non-positive 328; PEG can read a quarter row (S3).

**Blocked until answered:** trailing P/E, PEG, earnings yield. The per-share non-derivation (NA-1) may not ship with an unlabelled basis change.

**Interim (already in the plan, no accounting choice):** until this card is signed, P/E is shown with its basis labelled, and dividend yield is hidden where it used a derived DPS.

**Answer.**
- P/E option: ______ Fallback allowed when: ______
- TTM EPS displayed? yes / no
- PEG definition: ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 6 of 21. AC-8: Net income: consolidated, attributable to parent, available to common
**Sitting 2.** Evidence: R3 5.7, C14; data-team/33 I.

**The question in plain words.** "Net income" has three meanings:
- including noncontrolling interests (`ProfitLoss`);
- attributable to the parent (`NetIncomeLoss`);
- available to common shareholders (after preferred dividends and participating securities).

Today one chain mixes them under one name. Questions:
1. Adopt three separate concepts, with parent feeding net margin, ROE and P/E checks, and common feeding EPS checks?
2. When a company files only `ProfitLoss` and no NCI line, is NCI zero?

**Examples.**
- FCX Q1 2026: shown 1,387M vs 881M attributable (FILING-CHECKED in data-team/33 I).
- Walmart Q3: consolidated 6,088M, NCI 55M, parent 6,143M (0000104169-25-000191; R3).

| Option | What users see | Cells affected |
|---|---|---|
| (a) Three concepts; parent = consolidated - NCI when NCI is reported; no NCI line means "partial" (not zero) | correct attribution; some cells hidden | SEC data sets: NetIncomeLoss only 2,679 filings; NetIncomeLoss + ProfitLoss + NCI 744; ProfitLoss without NetIncomeLoss 259; available-to-common lines 523 (DATA-INFERRED). Rows at risk today: 1,189 (DATA-INFERRED, 33 I) |
| (b) (a), but a missing NCI line counts as zero | more cells filled; wrong where NCI exists but is not on the face | the 259-type filings |
| (c) Today's single chain | three attributions under one name | as today |

**Recommendation:** (a). The split itself is attribution, not perimeter. Your ruling is needed on (2) and to confirm the metric wiring.

**Blocked until answered:** the temporary hides from NA-11 convert to values; net margin, ROE, the P/E basis (AC-14).

**Answer.**
- Option chosen: ______
- Missing NCI line = zero? yes / no / only if: ______
- Metric wiring (net margin, ROE -> parent; EPS -> common) confirmed? ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 7 of 21. AC-10: Bank revenue
**Sitting 3.** Evidence: data-team/32 (5 of 5 printing banks agree); ledger rows 39, 40; S2.

**The question in plain words.** For banks, should "revenue" be net interest income plus noninterest income, computed and labelled? The filed `Revenues` tag means different things at different banks: gross of interest expense at some, net at others.

**Examples (FILING-CHECKED).**
- Citigroup `Revenues` = "Total revenues, net of interest expense", 65,354M = 44,127M NII + 21,227M noninterest income (0000831001-25-000154 R2).
- BAC: stored 138,566M vs 113,097M.
- FLG tags only the securities interest line with `InvestmentIncomeInterest` (19,785K of 116,469K) (0001104659-25-106961 R4).

| Option | What users see | Cells affected |
|---|---|---|
| (a) Revenue = NII + noninterest income, computed, labelled "net revenue (NII + noninterest income)" | comparable bank revenue and P/S | 44 banks in the cohort; NII and interest income blank for 40 of 44 though on the face (USB R4); part of the 961 "sector definition pending" cells (doc 46) |
| (b) Not shown for banks | blank with reason | same |
| (c) The filer's `Revenues` | unsafe: gross at some banks, net at others | same |

**Recommendation:** (a).

**Blocked until answered:** bank template revenue, P/S, revenue growth; the 961-cell class; certification of the financial companies in the top 100 (Gate D(F)): 13 by the freeze register's count (14 with BRK-A), DATA-INFERRED, superseding doc 49's "15-20".

**Answer.**
- Option chosen: ______ Conditions: ______________________________________
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 8 of 21. AC-2: Building total debt from parts: short-term block and instrument sums
**Sitting 3.** Evidence: data-team/31 section B (R2, R3, F1, F2); doc 46; ledger row 48.

**The question in plain words.**
1. May we add `DebtCurrent` once, after removing the current portion already inside `LongTermDebt`, and refuse when two different short-term tags remain whose nesting we cannot decide (BAC)?
2. When a company has no total-debt tag at all, may we build total debt by summing its instrument tags (notes, term loans, revolver)? Cases: CDNL pair, FRD, EG three-tag, NET, CME, CDNS, DLR.

**Examples.**
- CDNL shows gross `NotesPayable` 121,178,878 vs the net face pair (FILING-CHECKED in data-team/31), so the face pair outranks a schedule total.
- `LongTermDebt` is face value at AMZN and GOOG, not carrying amount (AMZN 0001018724-26-000004 R69; GOOG 0001652044-26-000018 R67; FILING-CHECKED).

| Option | What users see | Cells affected (DATA-INFERRED, data-team/31 B; doc 46) |
|---|---|---|
| (a) Adopt R2 and R3 as written, refusing where undecidable | more totals; refusals shown as "composition undecidable" | R2: double count 51 instants, DebtCurrent omitted 83, short-term tag outside our list 463. R3: 3,301 blank instants with instrument tags only (1,459 single tag; 1,308 non-financial). Cohort total-debt capture defects 1,086 cells |
| (b) Only the single-instrument case (a sole tag that covers current and noncurrent, non-financial SIC) | fewer totals, low risk | subset of the 1,459 |
| (c) None | those cells stay blank | as today |

**Recommendation:** (a). Every sum must tie to a filed total or a face check within rounding; refuse otherwise.

**Blocked until answered:** Tier 2 total-debt fills (company-specific cases like CDE and AMP come on top).

**Answer.**
- Option chosen: ______ Short-term block (1) allowed? ______ Instrument sums (2) allowed? ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 9 of 21. AC-9: Revenue when the printed total includes other items
**Sitting 4.** Evidence: data-team/37 section 6; R3 C9, C10; ledger rows 55, 57, 61, 69.

**Context.** For the clean case (a standard-tag total that ties exactly), we propose to use the filer's printed total without a ruling (NA-9). This card covers the rest. Proposed default: "revenue = the filer's total revenue as presented, net of contra-revenue, excluding non-operating income shown inside the total". Please accept or change each line:

| # | Case | Example (FILING-CHECKED unless noted) | Proposed default | Your answer |
|---|---|---|---|---|
| i | Insurer total revenues incl. realized gains | HIG | template-specific, see AC-11 | |
| ii | "Total revenues and other income" | XOM 332,238M incl. other income (0000034088-26-000045 R3); COP 61,548M on a custom tag (0001163165-26-000009 R3); CVX equity-affiliate income | subtract equity-method and non-operating income only where shown on the face; else flag | |
| iii | Contra-revenue | MA 29,845 gross - 10,961 rebates = 18,884 net (0001141391-22-000023 R61) | net as presented | |
| iv | Pre-606 bad-debt netting | THC | net as presented, basis labelled | |
| v | Premium taxes inside the total | CNC | as presented | |
| vi | Excise taxes (C9) | | net where presented as a deduction | |
| vii | Custom-tag totals | COP | company-scoped mapping with accession and calculation path | |
| viii | 10-K and Q3 10-Q select different tags | | Q4 blank "basis change" | |

**Effect.** These are the hides the revenue-total guard (NA-8) cannot convert. Their share of the 4,479 affected company-periods is NOT MEASURED; in doc 37's sample, 4 of 19 decidable companies fall in these cases. Also: undimensioned `Revenues` facts that are not the total (EMR acquiree revenue 0000032604-23-000030; NTAP segment 0001193125-26-259683 R4).

**Blocked until answered:** revenue, P/S, EV/sales, margins and growth for those companies.

**Answer.**
- Overall default accepted? yes / no
- Per-line changes: ______________________________________________
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 10 of 21. AC-7: Operating income and EBITDA when the statement has no operating-income line
**Sitting 4.** Evidence: data-team/27 D1, D2; doc 46 (314 cells); ledger rows 20, 38, 41, 56, 58.

**The question in plain words.** Single-step income statements (CVX, AJG, HTZ, GE) and statements without an operating subtotal list revenues and costs and go straight to pretax income. What should operating income and EBITDA show for them?

**Examples (FILING-CHECKED).**
- At CVX, AJG and HTZ, revenues minus `CostsAndExpenses` equals pretax income (interest is inside the costs): CVX 0000093410-26-000078 R3; AJG 0001628280-26-008662 R3; HTZ 0001657853-26-000008 R7.
- `OperatingIncomeLoss` is really pretax at AFG (0001042046-26-000010 R5) and ELS (0001628280-26-008722 R5).
- PLD operating income includes about 943.6M of disposal gains (0001193125-26-051453 R4).

| Option | What users see | Cells affected |
|---|---|---|
| (a) Operating income blank "not reported as a subtotal by this company" (face evidence required); EBITDA blank | honest blanks | 314 EBITDA cells (doc 46); SEC data sets: no OI line 398 filings; `CostsAndExpenses` without OI 89 (DATA-INFERRED) |
| (b) A separately named "EBIT (pretax + interest expense)", never written into operating income, excluded for financials and operating-interest filers | a new labelled metric | same companies |
| (c) OI = revenue - cost of revenue - SG&A only when SG&A is the only operating line, after an exactness test on a control group | values for simple shapes | subset |
| (d) Today's arithmetic fallback (85.5-90.3% within 2% of filed OI on its own control group, measured 2026-09-13) | **some wrong values today**; inexact shapes must be suppressed whatever is chosen | 168 companies use it (doc 47 v2 T2) |

**Recommendation.** (a) now; (c) after its exactness test; (b) only if the product wants a named EBIT metric. Separately, and without a ruling, we already guard pretax-labelled OI (AFG, ELS) and flag OI that includes disposal gains (PLD).

**Blocked until answered:** operating margin, interest coverage, the ROIC numerator and EBITDA for these company-periods.

**Answer.**
- Option(s) chosen: ______ Conditions: ______________________________________
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 11 of 21. AC-15: Interest expense composition and interest coverage
**Sitting 5.** Evidence: R3 5.4; data-team/27 D4; S3 item 3; doc 46.

**Questions.**
1. Gross interest expense = debt interest + debt-related fees (+ finance-lease interest per AC-1); capitalized interest out; net interest tags never used.
2. Operating interest for rental and captive-finance companies: HTZ tags 608M of 1,077M as `InterestExpenseOperating` (vehicle debt) (0001657853-26-000008 R7).
3. Companies that report only net interest (VVX, UNIT): blank, with a company-specific exception only where each period's composition is evidenced.
4. Coverage with an operating loss: "Not meaningful", or show the negative ratio?
5. Zero interest: show "No interest expense".

**Example (FILING-CHECKED).** Walmart Q3: debt interest 563M, finance-lease interest 121M, "Interest, net" 591M, which is a different concept (0000104169-25-000191 R4).

| Option for (4) | What users see | Cells affected |
|---|---|---|
| (a) "Not meaningful: operating loss" | no negative coverage numbers | interest_coverage blank 788 (588 `incomplete:denominator`) in the cohort (S3); cohort interest-expense capture defects 798 (doc 46); SEC data sets: gross only 1,349 filings, gross + income 867, net only 763 (DATA-INFERRED) |
| (b) Show the negative ratio | negative values | same |

**Recommendation.** (1) as stated; (2) operating interest kept in a separate template and excluded from the commercial coverage ratio; (3) as data-team/27 D4; (4) (a); (5) as stated.

**Blocked until answered:** interest coverage; the interest expense line for these shapes.

**Answer.**
- (1) ___ (2) ___ (3) ___ (4) ___ (5) ___
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 12 of 21. AC-19: Restatement basis for series, growth and TTM
**Sitting 5.** Evidence: S3 item 13; R3 4.4; doc 37 mechanism 4; ledger rows 64, 70, 78. **Examples partly ready; population NOT MEASURED. This card also gates the Q4 backfill (founder item 12; doc 49 Gate C).**

**The question in plain words.** When a company restates or recasts prior years (new accounting standard, discontinued operation, spin-off), which version do we show? May a growth rate or a 12-month sum mix an original figure with a restated one?

**Examples (FILING-CHECKED).**
- MSFT FY2016 growth is 68% when a restated FY2016 is compared with an unrestated FY2015, and about 38% on one basis (0001564590-18-019062 R2/R8; 0001193125-16-662209 R2).
- HON Q4 2025 capex 58M = recast FY 986M minus the original 9M of 928M (0000773840-26-000013 R7).
- LLY: recast revenue combined with original cost of goods (0000059478-19-000274 R2/R99).

| Option | What users see | Cells affected |
|---|---|---|
| (a) Latest-filed (restated) basis for every period shown; growth and TTM only from endpoints of the same filing vintage; original figures kept as provenance | consistent series; some cross-basis cells hidden until a same-basis pair exists | population NOT MEASURED; part of 786 history blanks (S3 F5) |
| (b) As originally reported for every period (point-in-time view) | reproduces what investors saw then; growth can be cross-basis | same |
| (c) Mixed (today) | inconsistent | as today |

**Recommendation:** (a) for display; (b) can be a later backtest product. Until answered, cross-basis pairs stay hidden (NA-4).

**Blocked until answered:** growth and TTM certification; the Q4 backfill; AC-9 (viii).

**Answer.**
- Option chosen: ______ Conditions: ______________________________________
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 13 of 21. AC-3: Special liabilities: FHLB advances (non-banks), mandatorily redeemable preferred, vehicle and captive-finance debt
**Sitting 6.** Evidence: R3 C15; data-team/31.

**The question.**
- Are Federal Home Loan Bank advances debt for insurers (EG)? For banks and thrifts they are funding and fall under the bank template.
- Is mandatorily redeemable preferred stock (a liability by classification) in total debt?
- Is rental-vehicle or captive-finance debt (HTZ) in total debt?

| Option | What users see | Cells affected |
|---|---|---|
| (a) FHLB advances are debt for insurers, never for banks and thrifts; mandatorily redeemable preferred out; vehicle debt in (it is borrowing; its interest follows AC-15) | EG D/E shown; HTZ leverage includes the fleet | EG D/E blank today; EWBC stored 35.6M vs 3,035.6M (bank, moot under the bank template). Counts NOT MEASURED |
| (b) All out | lower leverage for these models | same |
| (c) Case by case | per-company rulings | same |

**Recommendation:** (a).

**Blocked until answered:** EG-type insurer D/E; HTZ-type leverage.

**Answer.**
- Option chosen: ______ Notes: ______________________________________
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 14 of 21. AC-4: When may total debt show zero?
**Sitting 6.** Evidence: data-team/27 D3 (E1-E3); S3 item 8; ledger row 21.

**Examples (FILING-CHECKED).**
- CATO states it has no borrowings, and no borrowing line is on the face (0001562762-26-000041 R3/R58).
- ATEX has no debt line and no debt note (0001304492-26-000027 R3).
- Vendors' "total debt" includes leases for both, so it cannot prove borrowings exist.

| Option | What users see | Cells affected |
|---|---|---|
| (a) Zero when a total tag = 0 or every family tag is 0 (E1), or when the filing says "no borrowings outstanding" and there is no face borrowing line (E2); no line and no note (E3) stays blank "No borrowings reported" | zeros only with filing evidence | `zero_debt` 184 blank cells and the `missing:total_debt` cells (S3, cohort); E2/E3 population NOT MEASURED |
| (b) Also zero for E3 if a strict face test passes (every face liability line identified, none a catch-all, no debt note) | more zeros | larger |
| (c) Only E1 | fewest zeros | smaller |

**Recommendation:** (a), with (b) as a later rule only after a Verifier audit of the face test.

**Blocked until answered:** the evidenced-zero state for borrowings; zero_debt; D/E = 0; ROIC invested capital for debt-free filers.

**Answer.**
- Option chosen: ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 15 of 21. AC-11: Insurer revenue composition
**Sitting 6.** Evidence: S2 (cohort counts); ledger row 45. **Examples pending (HIG, PGR, one life insurer, CNC) before this sitting.**

**The question.** For property-casualty and life insurers, is revenue premiums earned + net investment income + fees + other, with or without realized investment gains? How are managed care companies (premium taxes inside revenue, CNC) and insurance brokers treated?

**Example (FILING-CHECKED).** PGR tags investment income with the bank total-interest tag (0000080661-26-000086 R3), so tag names do not identify the line.

| Option | What users see | Cells affected |
|---|---|---|
| (a) "Total revenues as presented, excluding realized and unrealized investment gains" for P&C and life, with gains as a separate line; managed care and brokers use the corporate template | stable revenue, gains visible separately | 40 insurers, 7 managed care, 7 brokers in the cohort (S2); affected cells NOT MEASURED |
| (b) Total revenues as presented (gains included) | volatile revenue | same |
| (c) Premiums only | understates investment-led insurers | same |

**Recommendation:** (a).

**Blocked until answered:** insurer template revenue cells; financial T1 certification (Gate D(F)).

**Answer.**
- Option chosen: ______ Managed care / brokers: ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 16 of 21. AC-12: REIT capital expenditure
**Sitting 6.** Evidence: R3 section 8; S3 section 6; S2. **Examples pending (two equity REITs, one with large development) before this sitting.**

**The question.** For equity REITs, is capex development plus recurring improvements, with acquisitions separate? (We do not propose to compute FFO: it is non-GAAP and not in the XBRL face statements; data-team/21 section 5.)

| Option | What users see | Cells affected |
|---|---|---|
| (a) Capex = development + capital improvements; acquisitions separate; the FCF family not in the REIT template | a capex line, but no REIT FCF | 54 equity REITs and 2 mortgage REITs in the cohort (S2); cells NOT MEASURED |
| (b) Capex not in the REIT template | no capex or FCF for REITs on the screen | same |
| (c) All real-estate payments | mixes acquisitions with capex | same |

**Recommendation:** (b) for the screen (consistent with S3's REIT removals), plus (a) as a statement-only line.

**Blocked until answered:** finalizing the REIT template.

**Answer.**
- Option chosen: ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 17 of 21. AC-16: ROIC tax term and average vs ending capital (ROIC, ROE)
**Sitting 6.** Evidence: S3 item 4; `mapper/definitions.py` (ROIC v1 formula). **Examples pending (one loss-making company, one with a large capital change).**

**The questions.**
1. ROIC uses NOPAT = operating income x (1 - tax / pretax income). What is the tax rate when pretax income is zero or negative?
2. Should ROE and ROIC use average or ending capital?

| Option | What users see | Cells affected |
|---|---|---|
| (a) Statutory 21% when pretax <= 0, labelled; average capital where both ends are certified, ending otherwise, labelled | values for loss years | ROIC blank 422 in the cohort, mostly input gaps; ROE negative 145 (S3) |
| (b) "Not meaningful" when pretax <= 0; average capital where available | no assumed rate on a loss | same |
| (c) Ending capital always | simpler; biased for fast-growing companies | same |

**Recommendation:** (b) for the tax term (no assumed rate on a loss); average capital where available.

**Blocked until answered:** ROIC and ROE wording and values for these cases.

**Answer.**
- (1) ______ (2) ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 18 of 21. AC-17: A line that is not presented: zero, or not applicable, in a ratio?
**Sitting 6.** Evidence: S3 items 5-7. **Examples pending (a classified balance sheet with no inventory line, a company with no goodwill).**

**The questions.**
1. Quick ratio when there is no inventory line: inventory = 0 (so quick = current), or not applicable?
2. Cash conversion cycle without inventory: a separately named "DSO - DPO" variant, or not applicable?
3. Goodwill as % of assets with no goodwill line: 0% or not applicable?

| Option | What users see | Cells affected (cohort, S3) |
|---|---|---|
| (a) No inventory on a classified balance sheet = 0 for quick ratio; CCC not applicable (no variant under that name); goodwill % = 0% "No goodwill" when the face shows no goodwill and there is no goodwill note | values where the absence is proven | quick_ratio 169 blank; CCC 598 blank, of which 359 companies have inventory not presented; goodwill_pct_assets 190 blank, goodwill not presented 94 |
| (b) All not applicable | blanks with reasons | same |
| (c) All zero | zeros without proof | same |

**Recommendation:** (a). Every zero here needs the not-presented evidence (FILING-CHECKED, or an audited detector).

**Blocked until answered:** those three metrics.

**Answer.**
- (1) ______ (2) ______ (3) ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 19 of 21. AC-18: Comprehensive income when there is no OCI statement
**Sitting 6.** Evidence: S3 item 11. **Examples pending (two companies stating no OCI items).**

**The question.** If a company presents no statement of other comprehensive income, does comprehensive income equal net income?

| Option | What users see | Cells affected |
|---|---|---|
| (a) Comprehensive income = net income only when the filing states it has no OCI items; otherwise not presented | values with evidence | 28 cohort blanks (S3) |
| (b) Not presented | blanks | same |

**Recommendation:** (a), only with the filing's statement.

**Blocked until answered:** 28 cells.

**Answer.**
- Option chosen: ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 20 of 21. AC-20: Continuing operations vs total for cash from operations and free cash flow
**Sitting 5 (with AC-19).** Evidence: R3 C13; WO-REVIEW finding 0.4; migration 0095; ledger row 34. **Examples partly ready; population NOT MEASURED.**

**The question.** When a company reports discontinued-operations cash flows, should FCF use continuing-operations CFO and capex, or the totals? Today our series can switch between the two from one period to the next: the continuing-ops tag is a fallback when the plain total is missing for that period (migration 0095, CODE-READ).

**Examples.**
- AMD 9M CFO 5,109M includes 920M of discontinued operations (0000002488-25-000166 R6; FILING-CHECKED in R3).
- MGNC and LRDC put the total tag on a continuing-ops subtotal (MGNC 0001683168-26-007689 R6; LRDC 0001199835-26-000359 R6).

| Option | What users see | Cells affected |
|---|---|---|
| (a) Continuing CFO and continuing capex when the filer reports discontinued cash flows separately; totals otherwise; never mixed within one series | consistent FCF | NOT MEASURED |
| (b) Totals always | includes businesses being sold | NOT MEASURED |
| (c) Today | series can switch basis | as today |

**Recommendation:** (a).

**Blocked until answered:** FCF certification for companies with discontinued operations.

**Answer.**
- Option chosen: ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Card 21 of 21. AC-21: Cash perimeter
**Sitting 6.** Evidence: data-team/27 Q-C (not run); ledger rows 45, 36. **Examples pending (CDNL, EG, one restricted-cash case).**

**The questions.**
1. May the `Cash` tag (which by definition excludes cash equivalents) fill "cash and cash equivalents"? Examples: CDNL; PGR uses plain `Cash` (0000080661-26-000086 R3).
2. Is restricted cash in or out?
3. How is insurer cash held inside "total investments and cash" treated (EG)?

| Option | What users see | Cells affected |
|---|---|---|
| (a) `Cash` fills only when the filing states it has no cash equivalents; restricted cash OUT of balance-sheet cash and equivalents but IN for the cash-flow reconciliation (ASU 2016-18); insurer cash through the insurer template | correct net cash and EV | counts NOT MEASURED |
| (b) `Cash` is a component only and never fills | more blanks | same |

**Recommendation:** (a).

**Blocked until answered:** net cash and EV for those filers.

**Answer.**
- (1) ______ (2) ______ (3) ______
- Name, credential, license: ______________________ Signature and date: ______________

<div style="page-break-after: always"></div>

## Record of answers (filled by the Standardization Lead after each sitting)
| Card | Sitting date | Answer | Matches recommendation? | Definition version created | Verifier sample result | Live in release |
|---|---|---|---|---|---|---|
| AC-1 | | | | | | |
| AC-5 | | | | | | |
| AC-6 | | | | | | |
| AC-13 | | | | | | |
| AC-14 | | | | | | |
| AC-8 | | | | | | |
| AC-10 | | | | | | |
| AC-2 | | | | | | |
| AC-9 | | | | | | |
| AC-7 | | | | | | |
| AC-15 | | | | | | |
| AC-19 | | | | | | |
| AC-3 | | | | | | |
| AC-4 | | | | | | |
| AC-11 | | | | | | |
| AC-12 | | | | | | |
| AC-16 | | | | | | |
| AC-17 | | | | | | |
| AC-18 | | | | | | |
| AC-20 | | | | | | |
| AC-21 | | | | | | |
