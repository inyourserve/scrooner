# Study: how others standardize, validate and prove XBRL fundamentals, and what Scrooner should copy

Status: v1, 2026-10-18. Research analyst study for the data agents. Read-only research: no database access, no other file edited.
Method: web search and page fetches on 2026-10-18. Every claim carries the URL it came from. Tags used throughout:
- **[P]** peer-reviewed or working paper; **[R]** regulator or standards body (SEC, XBRL US, XBRL International, PCAOB); **[O]** open-source project documentation; **[V]** vendor material (treat numbers as marketing unless independently confirmed); **[A]** anecdote (forum or review post, unverified); **[S]** Scrooner inference (my reasoning, not from a source).
- Where a fetch was blocked (HTTP 403) or a PDF unreadable, that is listed under "Could not confirm" and nothing is claimed from it.

Reads: `data-team/21-US-FILINGS-DOMAIN-KNOWLEDGE.md` (domain), `data-team/22-FILING-LESSONS-LEDGER.md` (cases), `doc/data-moat/team/PLAN.md` (launch order: wrong values out first, then metric-feeding gaps, then derivable quarters, then displayed reasons for every blank, then Verifier sample).

---

## 0. Executive summary (ten sentences)

1. Every serious provider and every academic study agrees that **filer-side XBRL errors are real and non-trivial**, so "it is in the XBRL" is not proof. Early studies found errors in roughly a quarter of the first large-filer submissions (Debreceny et al., 2010) [P]; staff of the SEC were still reporting scale errors in 2025 [R].
2. **The error classes are stable and enumerable** (sign, scale, period type, wrong tag, wrong context, calculation mismatch). The XBRL US Data Quality Committee (DQC) has turned them into 202 machine-checkable rules; Scrooner can mirror the subset that matters for stored values [R].
3. **Standardization itself changes numbers.** Compustat-vs-filing studies find material discrepancies (Chychyla and Kogan; Du, Huddart and Jiang), and re-standardization of history creates look-ahead bias (Lyle, Siano, Yohn) [P]. A standardized value should therefore always carry its as-reported source and its definition version, which Scrooner already stores in principle.
4. **All the open and commercial mappers use the same skeleton:** an ordered tag-to-concept table, company-specific overrides at higher priority, a statement-context disambiguator, and a validator of identities with tolerance (edgartools) [O]. Scrooner's `concept_mapping` plus confidence states is the same design.
5. **Sector templates are standard vendor practice:** FactSet's published description sorts companies into four profiles (Commercial, Bank, Insurance, Other Financial), each with its own statement template [V]. A blank under the wrong template is a template question, not a data question.
6. **Q4 and TTM are never plain subtraction for everything.** SEC filers themselves state quarterly EPS is computed independently and does not sum to the annual figure [R, filings]; only additive flows can be derived by subtraction.
7. **Restated vs as-reported is a first-class dimension** in point-in-time products (S&P Capital IQ, Compustat Point-In-Time, vendors) [V]; the correct stored fact is `(value, filed date, accession, basis)`, not `(value)`.
8. **Restatement visibility has a hole:** "little r" revisions are about three times as frequent as "Big R" restatements and trigger no Item 4.02 8-K [R], so an 8-K or 10-K/A scan undercounts. Detection must come from value comparison across filings.
9. **Public screener post-mortems are scarce.** What exists is anecdotal (wrong dividend, absurd ROE of about 52,000x, nonsensical share counts) [A]. The recurring shape is: a plausible-looking number that no range check was applied to.
10. **The cheapest proof of correctness that peers use is cross-statement identity plus a tolerance** (assets = liabilities + equity; revenue minus expenses ties to net income within a tolerance) [O, R]. Scrooner can run these over all stored values without opening a filing.

---

## 1. Errors in XBRL financial data: frequency, types, effects

### 1.1 What the research and regulators say

| Finding | Source | Tag |
|---|---|---|
| In the first round of XBRL submissions by about 400 large US corporations, one quarter of filings had errors where a reported monetary fact differed from the sum of the facts bound to it in a calculation relationship; authors attributed this mainly to debit/credit sign assumptions in the instance vs the taxonomy. Paper: "Does it add up? Early evidence on the data quality of XBRL filings to the SEC", Journal of Accounting and Public Policy, 2010. | https://ideas.repec.org/a/eee/jappol/v29y2010i3p296-306.html | P |
| Earlier NC State work on the first 22 voluntary XBRL 10-Ks (2006 and 2008) found errors in amounts, signs, presentation and labels in almost all companies examined; they point to the manual bolt-on conversion step as a source and warn users will not see errors visually. | https://news.ncsu.edu/2009/06/accuracy-essential-to-xbrl-financial-filing-program | P (press summary of study) |
| As of August 2014, XBRL US tallies compiled by DataTracks show 3,256,365 problems in 107,294 submissions from 10,112 public companies; most common categories include Missing Calculation, Calculation Error, Incorrect Calculation Weight. The source also says errors decreased as software matured. | https://datatracks.com/?p=847 (same figures in search listing of https://governancebeat.cooley.com/the-ten-most-common-xbrl-errors-for-form-10-ks/) | V (vendor compilation of XBRL US counts) |
| SEC staff (Division of Economic and Risk Analysis) found **continued scaling errors in tagged public float in fiscal-2024 10-Ks**: one filer showed $78 million in HTML and $78 in XBRL. Staff also saw the public float date tagged with the fiscal year end while the HTML used the Q2 measurement date. Staff had published a scaling reminder in 2019. | https://xbrl.us/news/sec-scaling-issues (published 2025-07-21) | R |
| SEC staff flagged inconsistent scale between `EntityCommonStockSharesOutstanding` and `CommonStockSharesOutstanding`; the related DQC rule had fired 121 times by Nov 2020. | https://xbrl.us/sec-acknowledges-dqc-rules/ and search summary at the xbrl.us scaling page above | R (via XBRL US) |
| A ten-item list of the most common 10-K XBRL errors, compiled by a law-firm publication from SEC DERA and Corp Fin comment-letter observations: wrong tag selection, unnecessary extensions, **sign errors (deferred taxes, impairments, OCI)**, **wrong period type**, text-block errors, missing required tags, **wrong units or scale**, **wrong context**, inconsistent dimensions, **failed calculation checks**. The article does not attribute each item to a specific source. | https://governancebeat.cooley.com/the-ten-most-common-xbrl-errors-for-form-10-ks/ | secondary summary of R |
| The SEC does not require third-party assurance on XBRL documents; risks are the usual statement risks plus taxonomy-choice and mapping risks. | stated in a paper summarized at the Boritz/No search listing, https://www.ensani.ir/fa/article/download/584212 (not opened in full) | P (low confidence on exact text) |
| A 2025 University of Tennessee dissertation uses DQC rule errors as its measure of low-quality machine-readable data and finds no evidence of an increase in information asymmetry for filings with an error. This is about market effect, not data correctness. | https://trace.tennessee.edu/utk_graddiss/12354 | P |

Relevance to Scrooner: the domain doc already lists sign, scale, unit, period and context risks (21 sections 3). The sources confirm the list is the standard one and, importantly, that **errors are still occurring in 2025**, so "old filings are clean" is not safe and the `EntityPublicFloat` case in the ledger is not an outlier.

### 1.2 Custom (extension) tags: our "about 9%" figure needs a footnote

Domain doc 21 section 3 says "about 9% of face lines use [custom tags]". The SEC's own page reports an average custom line-item tag rate of **16%-21% depending on filer category for 2018-2020** (e.g. 20% for large accelerated filers in 2020; 21% for non-accelerated filers), excluding abstract, member and domain tags; the formula for the average is not given [R]: https://www.sec.gov/structureddata/gaap-xbrl-custom-tags . An older SEC review of 2014-2016 10-Ks put the average near 20% and a trade-press report cites filers ranging from 1% to 55% [R/secondary]: https://www.complianceweek.com/custom-tag-use-in-xbrl-persists-sec-analysis-shows/9189.article . The two numbers may differ because of denominator (all line-item tags vs face-statement lines); **do not repeat "9%" as a general fact until our own face-line measurement is cited next to it.** Action: add a ledger row stating Scrooner's own measured face-line custom-tag rate and its denominator.

### 1.3 Effect on screeners and backtests

- Du, Huddart and Jiang, "Lost in standardization: Effects of financial statement database discrepancies on inference", Journal of Accounting and Economics 76(1), 2023. Abstract: discrepancies between as-filed and Compustat data affect four research settings (accrual properties, real earnings management, accounting-based anomalies, disclosure quality), **6 of 21 accounting-based anomalies** have affected existence or magnitude (including the accruals anomaly), discrepancies are more pronounced for firms with complex financial reporting, and **FactSet data show discrepancies from as-filed data, often larger than Compustat's** [P]: https://pure.psu.edu/en/publications/lost-in-standardization-effects-of-financial-statement-database-d/
- Chychyla and Kogan compared 30 line items for about 5,000 companies (Oct 2011 - Sep 2012) between Compustat and SEC XBRL 10-K data and found significant differences varying by item type, industry and company size [P]: https://scholarship.miami.edu/esploro/outputs/journalArticle/Using-XBRL-to-Conduct-a-Large-Scale/991031575973402976
- A 2026 study of 5,000 annual reports (2014-2023) found AI extraction error 9.19% when given XBRL context vs 15.75% from HTML and 18.24% from plain text [P/secondary]: https://tax.thomsonreuters.com/news/xbrl-cuts-ai-errors-in-reading-company-filings-study-finds/ . This measures extractors, not filers, but supports using the instance-level XBRL context (period, dimension, unit) rather than rendered text as the primary extraction route, and rendered statements as the cross-check. [S: this matches our hierarchy in doc 21 section 6.]

Not found: a current population-wide error rate for all SEC XBRL filers. Do not quote a single "XBRL is X% wrong" number.

---

## 2. Standardization methodology of established providers and open projects

### 2.1 What is public, by source

**edgartools (open source)** [O]
- Maps company XBRL tags to **95 standard concepts**, keeps the original filed label, adds a `standard_concept` column. Chain: tag -> `gaap_mappings.json` -> standard concept -> `display_names.json`. Mapping count differs by doc version (2,900+ in "latest", 2,067 in "stable"); mappings credited to a production taxonomy "tested on 390+ companies". https://edgartools.readthedocs.io/en/latest/xbrl/concepts/standardization/ and /stable/
- Customizing guide: **priority levels** (P1 core mappings, P2 company-specific, P4 prefix-match boost); more than **200 ambiguous tags** (asset/liability overlap, current vs noncurrent) to be resolved with context: statement type, calculation-tree parents, sign conventions, position. Company overrides are keyed by ticker (the guide itself calls this a limitation: tickers change and share classes exist; CIK-keying is planned). Validation described: **assets = liabilities + equity within a small tolerance; revenue minus expenses reconciled to net income with a 10% tolerance for unlisted items; list unmapped tags sorted by occurrence count**. Several features are marked planned, not current. https://edgartools.readthedocs.io/en/latest/advanced/customizing-standardization/
- Lesson for us: (a) key overrides by CIK (we do); (b) a **statement-context disambiguator** for ambiguous tags is the same problem as our "combined lines never mapped as a component" rule; (c) the 10% net-income tie is a loose tolerance, which tells us a tight tie needs the explicit list of "other" items, otherwise false alarms.

**Intrinio** [V]: ML-powered standardizer maps line items to standardized templates, "dozens of rigorous quality checks", automatic discrepancy flagging plus manual review; standardized vs as-reported tags distinguished. The page names no sector-template detail and no specific check, so nothing more can be copied. https://intrinio.com/xbrl-financial-standards and https://help.intrinio.com/standardized-vs.-as-reported-data-tags (the second only appeared as a search result, not opened).

**FactSet Fundamentals** [V]: four industry profiles (Commercial, Bank, Insurance, Other Financial) each with its own statement template; "Balance Model" tables map each company to its template; standardized basis plus as-reported basis offered in the broader product; no description of specific validation. Industry Metrics product has bank-specific metrics with bank history since 2009. https://insight.factset.com/resources/at-a-glance-factset-fundamental-datafeed and https://insight.factset.com/resources/at-a-glance-factset-fundamentals-industry-metrics (second from search snippet only).

**Compustat** [P/V]: standardizes company-reported figures through a proprietary process, so values can diverge from the filing or XBRL (Chychyla and Kogan; Du, Huddart, Jiang above). North America files replace restated quarterly income-statement figures while "Snapshot" keeps originals; Global products keep both series (WRDS guide, https://wrds-www.wharton.upenn.edu/documents/2179/Selected_Questions_Final_-_Answered.pdf, via search summary). Lyle, Siano and Yohn (July 2024 working paper, "Re-Standardized Financial Statement Data") show that periodic re-standardization overwrites history, which is a look-ahead bias, and that results change by data-pull date: https://som.yale.edu/sites/default/files/2024-07/Re-Standardized%20Financial%20Statement%20Data.pdf (confirmed by search abstract; full text not read).

**Fitch Fundamentals** [V, banks]: standardized statements for over 33,000 banks, up to 550 data points per bank and 50 pre-calculated ratios, with access to the source filing. https://economia.uniroma2.it/public/ba/files/Fitch_Fundamentals_Brochure.pdf (search snippet only). Takeaway: banks have their own data-point set, not a stretched commercial template.

**Calcbench** [V, 2013 article]: repository of scrubbed and normalized XBRL; calculates summary fields when the company did not report that line (e.g. cash plus short-term investments). https://www.journalofaccountancy.com/issues/2013/apr/20126677/ (search snippet only; 13 years old; no current methodology found).

**FMP-style providers** [V]: an FMP article states that a standardized value may come from one consolidated filing tag, several component tags, or a dimensioned fact, so mismatches vs as-reported do not always mean a mapping error. https://site.financialmodelingprep.com/insights/data/how-to-reconcile-standardized-and-asreported-financial-statements-to (search snippet; the page returned HTTP 403 when fetched). Takeaway: each standardized value should record its **composition type** (single tag / sum of components / derived / dimensioned). [S: Scrooner's lineage table should expose this if it does not.]

**SEC Financial Statement Data Sets (FSDS)** [R]: `num` has one row per distinct amount on the primary financial statements with keys adsh (accession), tag, version, ddate (period end), qtrs (duration in quarters), uom, a dimensional qualifier, and iprx (sequence integer distinguishing otherwise identical facts). A restated number appears under a different adsh rather than overwriting. Some 2010-2013 sets were reissued for processing corrections. The SEC says the sets are not a substitute for filings. https://www.sec.gov/files/aqfsn_1.pdf , https://www.sec.gov/data-research/financial-statement-notes-data-sets . SEC gives no rule for which duplicate to choose (searched, not found).

**SEC companyfacts and frames APIs** [R]: frames "aggregates one fact for each reporting entity that is last filed that most closely fits the calendrical period requested"; annual = 365 days +/-30, quarterly = 91 days +/-30; instants have an "I" suffix; units join numerator/denominator with "-per-". XBRL APIs aggregate only facts using a non-custom taxonomy that apply to the entire filing entity (so no dimensional segment data, consistent with doc 21 section 3 last bullet). https://www.sec.gov/search-filings/edgar-application-programming-interfaces . Note the +/-30 day tolerance: a 371-day 53-week year passes, a transition-period 10-KT does not; this is the SEC's own tolerance, a usable default for our duration classifier. [S for the 10-KT remark.]

**Arelle plus DQC plugin** [O/R]: the DQC rules run as an Arelle plugin written in XULE, after Arelle processes an instance; rule set map file must be current; command line example `--plugins "validate/DQC|EDGAR/transforms" --validate`. https://github.com/DataQualityCommittee/dqc_us_rules and https://arelle.readthedocs.io/en/2.41.3/plugins/popular/xule.html . XBRL US says 99 data rules are free for use in tools (https://www.xbrl.org/?p=12554, older) and the data-rule page now lists 202 approved rules, with new SEC-filer rules taking effect 60-90 days after approval (https://xbrl.us/data-rule/).

**OpenBB, Morningstar, Refinitiv/LSEG, S&P Compustat templates, Bloomberg:** no usable public methodology found (see "Could not confirm").

### 2.2 How these sources handle the exact sub-problems

| Sub-problem | Practice found | Source | Scrooner status |
|---|---|---|---|
| Tag -> standard line | Ordered table + company override + context disambiguator | edgartools [O] | same design; add explicit priority rank and context rule documentation |
| Tag switching over time | Ordered synonym list per concept, deterministic resolution rule; a single tag leaves gaps | https://dev.to/tradevodata/how-to-build-a-point-in-time-fundamentals-database-from-sec-edgar-and-when-not-to-2gn6 [V] | have (AAPL case) |
| Extension tags | Company-specific mapping file (Tesla `tsla:AutomotiveRevenue`); SEC advises preferring standard elements | edgartools [O]; SEC page above [R] | gap: extension tags only enter via sec_tag_library counts, no per-company extension map |
| Sector templates | 4 profiles (Commercial, Bank, Insurance, Other Financial) with template tables per company | FactSet [V] | partial (sector analyst role); no company-to-template table with evidence |
| Q4 derivation | EPS cannot be subtracted: filings state quarterly EPS is computed on that quarter's weighted shares and the sum of quarters need not equal the annual EPS | e.g. https://www.sec.gov/Archives/edgar/data/320193/000119312515023732/R20.htm and other R-file footnotes returned by search [R, filings]; I did not read a general derivation guide | rule already in doc 21 section 2 |
| TTM | no public methodology found beyond Compustat/vendor claims | - | n/a |
| Restatement basis | keep first-reported value and latest value plus a restated flag with 0.5% tolerance; filter on first_filed <= as-of date | Tradevo Data article [V] | policy is latest-filed only (PLAN decision 4); no first-reported vintage stored (verify) |

---

## 3. Failure case studies

Public post-mortems of wrong fundamentals are rare; what follows is what could be sourced. Where only an anecdote exists it is labelled.

1. **Public float scaling, 2019 and 2025 (regulator-documented).** HTML $78 million tagged as $78; date tagged with the fiscal year end instead of the Q2 measurement date; SEC reminders in 2019 and 2025 [R]: https://xbrl.us/news/sec-scaling-issues . Parallels our ledger row 2026-09 (eBay public float at $31 quintillion). Implication: a magnitude plausibility check on every dei and monetary value is warranted, not a one-off fix.
2. **Share count scale mismatch (2020).** `EntityCommonStockSharesOutstanding` vs `CommonStockSharesOutstanding` at different scales; the DQC rule had fired 121 times [R]: https://xbrl.us/sec-acknowledges-dqc-rules/ . Implication: cross-check dei shares against balance-sheet shares and against weighted-average shares for order of magnitude. [S]
3. **Calculation and sign errors at the start of XBRL (2009-2010).** 25% of first-wave large-filer submissions had calculation inconsistencies tied to debit/credit sign assumptions [P] (Debreceny et al. above).
4. **Restatement perimeter changes.** PCAOB: Big R restatements occurred at around 3% per year over 2005-2024 [R]: https://pcaobus.org/economicandriskanalysis/data-points/dp04-2025-financial-restatements-auditor-turnover.pdf (via search summary). Audit Analytics: revision ("little r") restatements correct immaterial errors, are made inside a periodic filing, and require no Item 4.02 8-K [V]: https://auditanalytics.help.ideagen.com/hc/en-gb/articles/35432233953554/ . An SEC comment letter estimated little r may be about three times Big R in 2021 excluding SPACs [R]: https://sec.gov/comments/s7-12-15/s71215-20130560-298718.pdf (search snippet). Audit Analytics 2019 count (484 restatements, 32 with Item 4.02) comes from a vendor blog and the analyst who searched flagged that its own figures do not obviously reconcile with the "80% revisions" statement: https://blog.auditanalytics.com/2019-financial-restatements-review/ . Implication: **an 8-K 4.02 or 10-K/A scan finds only a minority of value changes**; detect restatement by comparing values for the same (concept, period, dimension) across filings.
5. **Compustat re-standardization changing history.** Lyle, Siano and Yohn [P] above: hedge-return conclusions change with data-pull date. The same hazard applies to Scrooner if a mapping change silently rewrites historical `analytics` values without a version stamp. [S]
6. **Split and corporate-action adjustment errors.** yfinance's "price repair" changes (release 0.2.21) were aimed at Yahoo's mishandled dividend and split adjustments [A/O]: https://newreleases.io/project/pypi/yfinance/release/0.2.21 ; a Wharton note on I/B/E/S says that when a split falls between an estimate date and the report date, estimates and actuals sit on different share bases: https://wrds-www.wharton.upenn.edu/documents/5/A_Note_on_IBES_Unadjusted_Data_pdf.pdf [R-like/academic data guide, search summary only]. Implication: per-share facts need a share-basis stamp (as-filed vs adjusted to date X); our ledger already has the basic-vs-diluted EPS adjusted-only-in-part case (doc 21 section 4).
7. **Screener anecdotes (all [A], unverified):** Morningstar-fed Stock Selection Guide showed Gentex 2018 dividend $0.33 vs claimed $0.44 (https://feedback.betterinvesting.org/forums/220694-stock-selection-guide-tools/suggestions/38283763-use-correct-data); eSignal nonsensical shares outstanding for one symbol persisting after a vendor switch (https://forum.esignal.com/forum/product-data-category/esignal/esignal-archive/13133-shares-outstanding-wrong); Optuma ROE of about 52,000x vs about 11x real (https://forum.optuma.com/t/data-issues-for-fundamental-data/4108); a Stockrover post saying errors occur mainly for small Pink Sheet stocks (https://www.stockrover.com/?p=1062). Common shape: no range check on a ratio or on a share count. These establish that implausible ROE and share counts do reach users; they do not establish root causes.

Not found: a documented incident of a tier-one vendor (S&P, Refinitiv, FactSet, Bloomberg, Morningstar) publicly post-morteming a wrong fundamentals feed.

---

## 4. Concrete techniques and how peers prove a number correct

### 4.1 Validation rule families (XBRL US DQC, 202 approved rules)

Source for all: https://xbrl.us/data-rule/ (page read to rule DQC_0187 of 202; the rest not read) [R].

| Family | Rule examples (as titled on the page) | What it implies for Scrooner |
|---|---|---|
| Balance identity | DQC_0004 "Element Values Are Equal": assets must equal liabilities plus shareholders' equity. A 2015 committee minute says tolerance of 2 (rounding) was added, facts compared only within the same context and dimension, and the rule does not run if a required element is absent. https://xbrl.us/wp-content/uploads/2015/05/DQCminutes20150929.pdf | Check `total_assets = total_liabilities_and_equity` per filing period; tolerance = rounding at the filed decimals; skip when an input is absent |
| Calculation consistency | DQC_0126 child values sum to parent (non-dimensional); DQC_0008 reversed calculation; DQC_0099 FS element with no calculation; DQC_0167 inconsistent calculation roots | Subtotal check on stored values (see 4.2) |
| Negative-value | DQC_0015 US GAAP elements that should not be negative (2,420 elements per https://datatracks.com/?p=900 [V]); updated rule effective 2023-03-31 (https://xbrl.us/wp-content/uploads/2022/12/DQCMeetingNotes230125.pdf); DQC_0013/0014/0174 conditional negatives | Non-negative allowlist for stored concepts (revenue, total_assets, shares) |
| Sign direction | DQC_0147 elimination members; DQC_0184 OCI signs; DQC_0178 dividends in equity statement | Sign rule per concept with documented exception list |
| DEI and dates | DQC_0006 DEI vs block-tag date contexts; DQC_0033/0036 document period end date vs fact context | Reconcile `period_end` with the filing's own document period; catches mislabeled fiscal period (ledger LGND case) |
| Dimensional | DQC_0128 dimensional values larger than the default | Never read a dimensional value as total; check dimensional member does not exceed the undimensioned total |
| Cash flow | DQC_0043, 0049, 0057 (titles not read) | Reconcile cash-flow subtotals and cash roll-forward |

Calculation Linkbase caveats worth knowing [R/O]:
- The SEC accepts calculation weights of only 1 or -1; the accounting identity A = L + E cannot be expressed as a calculation (debit/credit balance mismatch); period types cannot be mixed (instant vs duration), so net income -> retained earnings cannot be modelled; dimensions must match. https://www.openriskmanual.org/wiki/XBRL_Calculation_Linkbase (secondary summary of the XBRL specs; spec itself: https://www.xbrl.org/Specification/calculation-1.1/REC-2023-02-22/calculation-1.1-REC-2023-02-22.html).
- XBRL 2.1 calculation checking can create false failures on rounded values and miss failures where duplicate facts exist; Calculation 1.1 addresses both and states inconsistencies do not make a report invalid. Same spec page. **Consequence: a calculation mismatch is a signal for review, not proof of error, and a pass is not proof of correctness.**
- Calculation checks cannot catch an error that is consistently wrong (wrong tag with right sums), a missing total, or a wrong scale applied uniformly to all facts. [S]

### 4.2 Cross-statement identities that need only stored values (candidate Scrooner checks)

These are standard accounting identities; the published sources that name checks are edgartools (assets = liabilities + equity; revenue minus expenses ties to net income) and DQC (DQC_0004, DQC_0126). The remaining ones are [S] inferences from accounting, listed for the Standardization Lead to approve, not sourced:
- Assets = Liabilities + Equity (+ mezzanine / noncontrolling interest where reported) [sourced].
- Sum of current assets components = total current assets; same for liabilities, only where the filer presents a classified balance sheet [S].
- Net income on the income statement = net income in the cash flow starting line (same period) [S].
- Ending cash on cash flow = cash on balance sheet (restricted-cash variants differ) [S].
- EPS x weighted shares is approximately net income available to common (loose tolerance because of rounding and participating securities) [S].
- Diluted EPS <= basic EPS in magnitude for profit-making periods, with an exception for anti-dilution presentation [S].
- Quarters: sum of discrete Q1..Q4 flows = annual for additive items only [S; consistent with SEC filers' own EPS footnotes].

### 4.3 Confidence scoring

Public sources describing a numeric confidence score for fundamentals: none found. What peers do publish:
- Intrinio: automated flagging plus manual review, no score [V].
- Tradevo article: a `qa_status` column on each row so consumers can filter, plus a restated flag [V].
- edgartools: unmapped tag list sorted by occurrence count, logged for review [O].
- DQC: binary rule results with an effective-date discipline (errors flagged before the effective date do not necessarily indicate a defect; https://xbrl.us/data-rule/) [R].
Conclusion: the industry practice is **categorical status plus reason**, not a probability. [S: this matches Scrooner's existing confidence states and the PLAN's three-state ledger; do not invent a numeric score.]

### 4.4 As-reported vs restated vintages (point-in-time)

- S&P Capital IQ's paper (as summarized by search; page returned 403 when fetched): point-in-time data is stamped by filing or press-release date while non-PIT is dated by fiscal period end; non-PIT databases overwrite history on correction; time-lags are an imperfect substitute because filing rules differ by region and change over time [V]: https://spglobal.com/content/dam/spglobal/mi/en/documents/general/sp-capitaliq-quantamental-point-in-time-vs-lagged-fundamentals.pdf
- Compustat Point-In-Time combines originally reported and restated values for annual, quarterly and YTD, from December 1986 (press release, per search summary) [V]: https://www.globalcustodian.com/?p=26067
- Tradevo Data: store `first_filed`, `original_value`, `latest_value`; query `first_filed <= X`; restatement flag at 0.5%; vendor claims about 6% of point-in-time rows flagged restated (18,723 of 312,751; **vendor-owned dataset, 7 concepts only, not a benchmark**) and mean reporting lag 66 days, median 60, p90 90 days for its full universe [V]: https://dev.to/tradevodata/as-reported-vs-restated-financial-data-why-the-difference-matters-for-backtesting-1big
- Practical meaning for Scrooner: the stock-page user wants the current best value, so "latest filed" (PLAN decision 4) is a reasonable display policy. The vintage matters for (a) screening history if we ever back-test, (b) proving a number against the filing that first showed it, (c) detecting restatements. Storing `first_filed_accession` and `first_value` next to the current fill costs little. [S]

### 4.5 How peers "prove" a number

No peer publishes a proof standard stronger than: identity checks inside the filing, comparison against another independent extraction, manual review of flagged items, and keeping a link to the source filing (Fitch "access to the original source filing" [V]; Intrinio manual review [V]). The academic benchmark approach is filing-vs-database comparison (Chychyla and Kogan, Du et al.) [P]. Scrooner's golden-10 plus Verifier sample is the same approach; the improvement is to run it with a stratified sample (see ranked list item 9).

---

## 5. Techniques to adopt now (ranked)

Ranking criterion: reduces wrong values reaching users in the next days-to-weeks (PLAN launch re-rank), uses data we already store, needs no vendor data and no migration where possible. Each item names the Scrooner rule or check it becomes.

1. **Population-wide identity checks as a gate before display (DQC_0004 style).** Rule `check_balance_identity`: for each (company, filing, period) where `total_assets`, `total_liabilities` (or liabilities-and-equity) and equity are all authoritative, flag if `abs(assets - (liabilities + equity [+ NCI + mezzanine]))` exceeds the rounding implied by the least precise input's `decimals` (DQC uses a tolerance of 2 units after scaling; use filed decimals, not a fixed number). Skip when any input is absent (as DQC does). Flagged rows are routed to a review queue and the affected display values go "unavailable" until cleared. Sources: https://xbrl.us/wp-content/uploads/2015/05/DQCminutes20150929.pdf , https://edgartools.readthedocs.io/en/latest/advanced/customizing-standardization/ .
2. **Scale and magnitude plausibility check on every monetary, share and dei value.** Rule `check_magnitude`: per concept, compare each value to the same company's neighbouring periods and to the median log-magnitude of its peers (same SIC division); flag > 3 orders of magnitude off. First applications: `EntityPublicFloat` (dei), `shares_outstanding` vs `diluted_eps`-implied shares (net_income / diluted_eps within an order of magnitude), `revenue`. Evidence it is needed: SEC scaling alerts 2019 and 2025; share-count scale rule fired 121 times; eBay $31 quintillion in our ledger; the ROE 52,000x anecdote. Sources: https://xbrl.us/news/sec-scaling-issues , https://xbrl.us/sec-acknowledges-dqc-rules/ .
3. **Non-negative and sign rule table per canonical concept (DQC_0015 / 0014 / 0147 family).** Rule `concept_sign_policy`: a table of concepts that must be >= 0 (revenue, total_assets, shares_outstanding, weighted-average shares, total_debt) and concepts with known legitimate negatives (net_income, cfo, capex-as-outflow convention), with an exception list needing a filing proof. Directly covers the PLAN's "stale negative weighted-average share rows" class. Sources: https://xbrl.us/data-rule/ , https://xbrl.us/wp-content/uploads/2022/12/DQCMeetingNotes230125.pdf .
4. **Treat a calculation mismatch as a signal, never as proof; store the reason code.** Rule `calc_mismatch_reason`: when a derived or stored total disagrees with the sum of its stored components, record `rounding | missing_component | combined_line | extension_component | unexplained`; only `unexplained` blocks display. Prevents false alarms (XBRL 2.1 false failures on rounding) and prevents blind trust (consistent-wrong errors pass). Source: https://www.xbrl.org/Specification/calculation-1.1/REC-2023-02-22/calculation-1.1-REC-2023-02-22.html , https://www.openriskmanual.org/wiki/XBRL_Calculation_Linkbase .
5. **Duration and period-type validation from dates, not labels (SEC frames tolerance as default).** Rule `period_classify`: classify duration facts as quarter (91 days +/-30 per SEC frames, but prefer 13/14 weeks for 52/53-week filers), annual (365 +/-30, accepts 371), YTD (6M/9M), or `other` (10-KT, short year); never use `fy`/`fp` labels as authority; reconcile `period_end` with the filing's own document period end (DQC_0033/0036/0006 family). This is the code detector the PLAN asks for to catch full-year-under-quarter-label (LGND). Sources: https://www.sec.gov/search-filings/edgar-application-programming-interfaces , https://xbrl.us/data-rule/ .
6. **Q4 only for the additive allowlist, and never EPS.** Rule `q4_derivation_allowlist`: Q4 = FY - 9M YTD (same vintage, same filing family) for cash-flow items, taxes, pretax income, revenue and other additive flows; `diluted_eps`, `basic_eps`, weighted-average shares and ratios are taken from the filing's quarterly-data note or left unavailable with the reason "quarterly EPS is not additive". Source: SEC filers' own footnotes (e.g. https://www.sec.gov/Archives/edgar/data/320193/000119312515023732/R20.htm) [R]; matches PLAN step 4.
7. **Restatement detection by value comparison, with a tolerance, stored as a flag.** Rule `restated_flag`: for the same (company, concept, period, unit, dimension), if a later filing's value differs from an earlier one by more than rounding (the vendor article uses 0.5%; calibrate on our data), mark `restated=true`, keep `first_value`, `first_accession`, `current_accession`. Do not depend on Item 4.02 or 10-K/A alone because little r revisions are about 3x Big R and carry no 4.02. Sources: https://auditanalytics.help.ideagen.com/hc/en-gb/articles/35432233953554/ , https://sec.gov/comments/s7-12-15/s71215-20130560-298718.pdf , https://dev.to/tradevodata/how-to-build-a-point-in-time-fundamentals-database-from-sec-edgar-and-when-not-to-2gn6 (vendor).
8. **Record composition type on each standardized value.** Rule `composition_type`: every mapped value is tagged `single_tag | sum_of_components | derived | dimensioned_member`; a `dimensioned_member` can never fill a consolidated concept (doc 21 section 3). Prevents the "mismatch is not always a mapping error" confusion and supports Verifier. Source: https://site.financialmodelingprep.com/insights/data/how-to-reconcile-standardized-and-asreported-financial-statements-to (search snippet, vendor) plus doc 21.
9. **Verifier sample stratified by the risk factors the research identifies.** Rule `verifier_strata`: sample across (a) complex reporters / financials (Du et al.: discrepancies larger for complex reporting), (b) custom-tag-heavy filers, (c) tag-switchers and small caps (vendor advice to test beyond mega-caps), (d) filers with amendments or restatement flags, (e) 52/53-week and non-December fiscal years. Report failures by stratum, not a single pass rate, since 12 clean cases bound the failure rate only to about 25% (PLAN). Sources: https://pure.psu.edu/en/publications/lost-in-standardization-effects-of-financial-statement-database-d/ , https://dev.to/tradevodata/how-to-build-a-point-in-time-fundamentals-database-from-sec-edgar-and-when-not-to-2gn6 .
10. **Per-concept mapping priority table with explicit context disambiguator and CIK-keyed overrides.** Rule `mapping_priority`: document, for each canonical concept, ordered tag candidates, the statement/section context required, and company overrides keyed by CIK (edgartools notes ticker-keying is a known weakness). The 200-plus ambiguous tag categories edgartools names (asset/liability overlap, current vs noncurrent) are the same family as our combined-line and `total_debt` composition problems. Source: https://edgartools.readthedocs.io/en/latest/advanced/customizing-standardization/ .
11. **Unmapped-tag backlog sorted by occurrence, filtered by the metric-feeding set.** Already how we work (sec_tag_library); keep ranking by `active_company_count` but weight by whether a metric consumes the concept (PLAN finding: 45 of 78 concepts feed no metric). Source: edgartools unmapped-list practice (above).
12. **Footnote the custom-tag rate in doc 21** (SEC reports 16-21% average of line-item tags; our "9%" needs its denominator). Source: https://www.sec.gov/structureddata/gaap-xbrl-custom-tags . Documentation fix only; no code.

Concept-specific examples of how items become rules:
- `diluted_eps`: items 3 (sign: EPS may be negative, so only rule is `diluted_eps` magnitude <= `basic_eps` magnitude for profits), 2 (net_income / diluted_eps implies a share count, compare to `weighted_average_diluted_shares` within an order of magnitude), 6 (never derive Q4 by subtraction), split-basis stamp (see "defer").
- `revenue`: item 2 (annual revenue vs sum of four quarters within rounding), item 5 (annual vs YTD labelling), item 7 (restated flag), item 3 (>= 0).
- `total_debt`: item 8 (composition type `sum_of_components`; record which components present), item 4 (reason code when a component such as current portion of long-term debt is missing), item 3 (>= 0).

---

## 6. Techniques to defer

1. **Loading the SEC Financial Statement Data Sets in bulk.** They are derived from the same filings and fill nothing companyfacts lacks (PLAN re-rank); useful later for ranking face lines and proving absence. The SEC gives no rule for choosing among duplicates across filings, so a rule must be designed. Pilot only, as already decided.
2. **Running Arelle plus the full DQC ruleset on original instances.** High value (all 202 rules are written and maintained) but requires fetching and processing each filing's instance and an Arelle/XULE deployment; PLAN defers calculation linkbases. Reasonable later as an independent check for sampled filings: https://github.com/DataQualityCommittee/dqc_us_rules . Note new rules apply 60-90 days after approval.
3. **Calculation Linkbase mining** to learn subtotal structure automatically; limited by weights of 1/-1 only and no cross-period-type relationships; defer past launch (PLAN).
4. **Full point-in-time (bitemporal) store** with `knowledge_time` and `event_time`. Needed for backtesting, not for a correct current page. Adopt only the cheap subset in item 7.
5. **Numeric confidence scores.** No peer publishes one; categorical status plus reason is the practice. Keep the three-state ledger.
6. **ML-assisted mapping** (Intrinio-style). Vendor-claimed, unverifiable; our deterministic tag library with human-approved release tiers is better aligned with "never self-approve".
7. **Split-adjustment basis stamping for every per-share fact.** Right idea (I/B/E/S and yfinance cases), but it needs design across basic/diluted EPS and dividends per share; do after the launch-critical fixes. [S]
8. **Sector-specific bank data (FDIC) and bank templates** (FactSet and Fitch practice supports dedicated bank data points); already planned as a labelled secondary source.
9. **Company-to-template table** (Commercial / Bank / Insurance / Other Financial) built from SIC plus filing evidence; useful once the sector analyst's proposals are approved by the named accounting reviewer.

---

## 7. Could not confirm

- A population-wide current error rate for SEC XBRL filings (only 2010-era and 2014-era counts and 2025 scaling alerts found).
- Methodology documents for **Morningstar, Refinitiv/LSEG, S&P Compustat item definitions, Bloomberg, OpenBB** standardization; the searches returned only product pages. The Compustat item-definition manual was not located.
- Calcbench's current tag-to-line-item rules (only a 2013 article).
- Whether FactSet offers restated vs originally-reported series (the page read does not say).
- The full text of Lyle, Siano and Yohn (PDF unreadable via fetch; abstract confirmed via search), the S&P Capital IQ point-in-time paper (HTTP 403), the FMP reconciliation and restated-financials articles (HTTP 403), and the PCAOB data point (search summary only). The 'around 3% per year' Big R figure is therefore second-hand.
- The Boritz and No paper on XBRL assurance (not located; the assurance statement above rests on a secondary paper that was not opened).
- Hoffman's Fundamental Accounting Concepts rule set (searched; nothing found), so no sourced list of cross-statement "fundamental accounting relations" exists here; the identities in 4.2 other than assets = liabilities + equity and the net-income tie are my own reasoning.
- The SEC's own rule for choosing among duplicate facts across filings in FSDS, and an SEC-published Q4 derivation method (none found).
- Any public post-mortem of a tier-one vendor's wrong fundamentals feed; only forum-level anecdotes exist.
- The DQC rule text and tolerance values for the current rules (read only titles; the 2015 tolerance of 2 is from old minutes and may have changed). Verify against https://github.com/DataQualityCommittee/dqc_us_rules before encoding a tolerance.
- The latest custom-tag percentage beyond 2020 on the SEC page (later years' figures are in images).
- Whether Tradevo's, Intrinio's or FMP's numbers hold up: all vendor claims, none independently checked.

---

## 8. Suggested ledger rows (for the Ledger owner, after verification; not appended by this study)

| Case | Rule it implies | Proof needed before appending |
|---|---|---|
| SEC 2025: public float scaled $78 vs $78 million | Magnitude check on dei values | An accession from our data showing a flagged row |
| Quarterly EPS does not sum to annual EPS (filer footnotes) | Never derive Q4 EPS by subtraction | One accession per case from golden-10 |
| Little r revisions carry no 4.02 | Restatement detection by value comparison | An accession where a prior-period value changed inside a periodic filing |
| Custom-tag rate 16-21% (SEC) vs our 9% | State the denominator | Our own measured face-line rate |
