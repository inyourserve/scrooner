# 36 — Scrooner: SEC Filing Types Reference

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

**Status:** Reference · Owner: Founder/Product · Review: when a new filing type is added to scope

A single consolidated reference, one section per SEC EDGAR filing type Scrooner recognizes or could recognize: what the filing legally covers, exactly what Scrooner's real code currently extracts from it (module + table, or "existence only," or "not used"), and why it matters for the product. [`doc/foundational/07_SEC_EDGAR_Rules_and_Data_Guide.md`](../foundational/07_SEC_EDGAR_Rules_and_Data_Guide.md) §8 remains canonical for EDGAR access mechanics and the original form-type inventory; this doc goes deeper on one column that doc 07 mostly leaves blank — what Scrooner actually *does* with each form, grounded in the current codebase, not intent.

Every extraction claim below was checked directly against the real module listed (not recalled from a plan doc) as of 2026-08-29. Where a doc (07/22/24/etc.) described something as scoped-but-not-built, this doc checks whether it has since shipped — one real gap between doc claims and code state was found and is called out in §Form N-PORT below.

---

## Summary table

| Filing | One-line purpose | Scrooner extraction depth |
|---|---|---|
| [10-K](#10-k--10-kA) | Annual report | **Full** — primary XBRL financial-data source |
| [10-Q](#10-q--10-qA) | Quarterly report | **Full** — same pipeline as 10-K |
| [8-K](#8-k--8-kA) | Current report (material events) | **Partial** — form + `items` classification captured; no document body parsed |
| [DEF 14A family](#def-14a-family-def-14a-defa14a-defm14a-defr14a) | Definitive proxy statement | **Existence-only** — filing presence in `core.filing`, no document parsing |
| [Form 3](#form-3) | Initial insider ownership statement | **Not used** — deliberately excluded from the ownership build |
| [Form 4](#form-4) | Insider transaction report | **Full** — real transaction-level detail, trailing 12 months |
| [Form 5](#form-5) | Annual insider transaction summary | **Not used** — deliberately excluded |
| [Schedule 13D](#schedule-13d--13g) | Active beneficial ownership (>5%) | **Partial** — filer/issuer/CUSIP captured; `percent_of_class`/`shares_owned` deliberately left null |
| [Schedule 13G](#schedule-13d--13g) | Passive beneficial ownership (>5%) | **Partial** — same as 13D |
| [Form 13F](#form-13f-13f-hr--13f-nt) | Institutional manager holdings | **Full** (single-window snapshot) — bulk-data CUSIP match |
| [Form N-PORT](#form-n-port) | Fund/ETF monthly portfolio holdings | **Full** (single-window snapshot) — built, not yet reflected in some planning docs |
| [Form 15 family](#form-15-family-15-12g-15-15d-15f-12b-15f-12g) | Deregistration notice | **Partial** — confirmed common-stock deregistrations drive `core.company.status = 'delisted'` |
| [SC 14D9 / SC TO](#sc-14d9--sc-to) | Tender offer response / commencement | **Existence-only** (SC 14D9); **not used** (SC TO) |
| [20-F / 40-F](#20-f--40-f-foreign-private-issuers) | Annual report, foreign private issuers | **Identity-only** — filing/company record exists, XBRL facts excluded from V1 scope |
| [S-1](#s-1--s-1a) | IPO registration statement | **Not used** |

---

## 10-K / 10-K/A

**What it legally covers.** The annual report a US domestic operating company must file under the Exchange Act: full-year audited financial statements, MD&A, risk factors, business description, executive comp summary tables, and (since the early 2010s XBRL mandate) machine-readable Inline XBRL tagging of the financial statements. The `/A` variant is a formal amendment/restatement.

**What Scrooner extracts.** This is the backbone of the whole product, not a side feature:
- `pipeline/src/scrooner_pipeline/normalizer/identity.py` records the filing itself (`core.filing`: accession number, filing date, period of report, `is_amendment`) — 10-K/10-K/A have been in `FORM_ALLOWLIST` since the Normalizer's original build.
- `pipeline/src/scrooner_pipeline/normalizer/` (Stage 2d and onward) parses the underlying XBRL facts already fetched by the Collector into `core.fact`, `core.period`, `core.unit`, `core.concept` — every tagged number, every taxonomy, every restatement history, with `is_authoritative` conflict-flagging.
- `pipeline/src/scrooner_pipeline/mapper/concepts.py` + `expanded_concepts.py` map ~30 curated XBRL tags to canonical concepts (`revenue`, `net_income`, `total_debt`, `cfo`, `capex`, `inventory`, `sbc`, `goodwill`, `accounts_receivable`, etc.), each with a documented priority/confidence and cross-checked for double-counting traps (e.g. `LongTermDebt` vs. its component tags).
- `pipeline/src/scrooner_pipeline/mapper/calculate.py`, `ttm.py`, `expanded_metrics.py`, `quality_score.py`, `quality_flags.py`, `price_metrics.py` compute the full locked 18-metric set plus doc 18/26's expanded set (ROE/ROIC, margins, growth CAGRs, Piotroski F-Score, dilution trend, quick ratio, EV/EBITDA, cash conversion cycle, etc.) from these facts.
- `pipeline/src/scrooner_pipeline/statements/classify.py` additionally classifies facts into displayable Income Statement / Balance Sheet / Cash Flow line items for the company page's statement tables.
- `10-K/A` restatements are explicitly handled: `normalizer/restatements.py` supersedes (never silently overwrites) an amended filing's facts against the original.

**Why it matters.** This is the entire "data moat" from doc 01 — a small set of financial facts, tagged and normalized once, is what makes deterministic screening and traceable company pages possible at all. Every locked metric and every statement table on the company page traces back to a 10-K (or 10-Q) fact.

---

## 10-Q / 10-Q/A

**What it legally covers.** The quarterly report for the three fiscal quarters not covered by the 10-K — unaudited financial statements plus an updated MD&A. `/A` is the amendment variant.

**What Scrooner extracts.** Identical pipeline to 10-K — same `FORM_ALLOWLIST` entry, same `core.fact` extraction, same Mapper concept mapping. The one 10-Q-specific piece: `normalizer/derived.py`'s `derive_interim_quarters` decomposes cumulative YTD-tagged cash-flow facts (a normal, valid GAAP presentation choice some filers use) into discrete Q2/Q3 values by successive subtraction — needed because TTM/quarterly metrics require a genuine discrete-quarter number, not a running total. `mapper/ttm.py` uses trailing-four-quarter windows built from 10-Q + 10-K data for TTM metrics (ROE, ROIC, the 6 price-dependent metrics) and for quarter-over-quarter growth.

**Why it matters.** Without 10-Q data, Scrooner could only refresh once a year and could never compute TTM figures — the freshness a serious investor expects (doc 01's "trusted enough to come back to every time") depends on this.

---

## 8-K / 8-K/A

**What it legally covers.** A "current report" companies must file within four business days of a defined list of material events — earnings releases (often via an Item 2.02 exhibit, ahead of the 10-Q), M&A completion, executive/director changes, bylaw amendments, delisting notices, shareholder votes, and more. SEC assigns each 8-K a structured `items` classification (e.g. `2.02`, `5.02`) describing which triggering event(s) it covers.

**What Scrooner extracts.** Added to `FORM_ALLOWLIST` 2026-08-17 (doc 19 Stage 1) as a deliberate, verified-zero-regression widening of `normalizer/identity.py`. Scrooner captures the filing's existence *and* its raw `items` string (`core.filing.items`, e.g. `"2.02,9.01"`) — sourced directly from the submissions payload's own `items` array, no document body ever fetched or parsed. `apps/site/src/pages/stock/[ticker].astro` renders this on the company page's Filings section: a hardcoded `ITEM_LABELS` map (16 curated codes — Material Agreement, Earnings Results, Officer/Director Change, Shareholder Vote, etc.) turns the raw item codes into a human-readable summary (`filingSummary()`); an unrecognized code falls back to the raw code itself, never a fabricated label.

**Why it matters.** This is SEC's own structured event classification, sitting free in already-fetched data — doc 22 ranked capturing it the single highest-leverage unbuilt item at the time, and it's now built: a real, zero-guesswork corporate-actions feed (earnings dates, M&A, governance changes) without any text-mining or AI summarization, matching doc 02's "AI is assistive only" boundary. The 8-K's actual document body (the press release, the material-agreement text) is **not** parsed — that would be a genuinely new, separate text-extraction project.

---

## DEF 14A family (DEF 14A, DEFA14A, DEFM14A, DEFR14A)

**What it legally covers.** The definitive proxy statement — executive compensation tables, board composition and nominee bios, shareholder proposals, and the matters put to a shareholder vote at the annual meeting. `DEFA14A` (additional soliciting material), `DEFM14A` (merger-related), `DEFR14A` (revised) are the company's own amendment/companion variants; Scrooner deliberately excludes `PRE 14A`/`PREM14A` (preliminary, superseded by the DEF that follows) and third-party/activist exempt-solicitation forms (`DFAN14A`, `PX14A6G`, `PX14A6N`) — not the company's own disclosure.

**What Scrooner extracts.** Added to `FORM_ALLOWLIST` 2026-08-18 (doc 26). **Existence-only** — `normalizer/identity.py` records the filing's presence in `core.filing` (accession number, filing date, form). No document body is parsed: executive comp figures, board composition, and insider-holdings tables that live inside the proxy's own text are not captured anywhere in `core`. This was verified live against the golden-10 (472 real filings landed, zero regression to other form types) but the parsing itself — doc 19's "Stage 5" — remains explicitly deferred, unstructured/P2 work.

**Why it matters.** Governance and executive-comp data is a real, named future differentiator (doc 18), but it isn't in the locked 18-metric list and needs genuinely new text-extraction work, not a quick win. Recording the filing's existence now means the company page's Filings list is at least complete and the future parsing work has a ready-made list of documents to work from.

---

## Form 3

**What it legally covers.** The initial ownership statement a company officer, director, or new 10%+ owner must file (Section 16 of the Exchange Act) — a snapshot of holdings at the moment they became an insider, not a transaction.

**What Scrooner extracts.** **Not used.** `normalizer/identity.py`'s `FORM_ALLOWLIST` does not include Form 3, and `pipeline/src/scrooner_pipeline/ownership/insider.py`'s own module docstring explicitly scopes it out: "Form 3/5 deliberately out of this pass — Form 4 is doc 10's own named 'core insider-activity feed'; 3/5 are lower-priority supporting context... and Form 3's holding-only structure needs its own verification pass before being trusted, not assumed from Form 4's shape." No `core.filing` row, no parsed data.

**Why it matters.** Form 3 confirms *who* is an insider but carries no transaction (buy/sell) signal — lower decision-value than Form 4 for the "is this insider bullish or bearish" question the product cares about. A real, deliberately deferred gap, not an oversight.

---

## Form 4

**What it legally covers.** The report an insider (officer, director, or 10%+ owner) files within two business days of any transaction in the company's securities — the core, timely insider-trading disclosure under Section 16(a).

**What Scrooner extracts.** **Full, real transaction-level detail.** `pipeline/src/scrooner_pipeline/ownership/insider.py` reads the filing list from the already-fetched `raw.sec_submissions` payload (zero new discovery fetch), downloads each individual filing's XML body, and parses it with `ElementTree` (not regex) into `core.insider_transaction`: reporting owner name/CIK, director/officer/10%-owner role flags, officer title, security title, transaction date/code, shares, price per share, acquired/disposed code, and post-transaction share balance. Also captures `is_10b5_1_plan` from the `aff10b5One` field (SEC's 2023 Rule 10b5-1 trading-plan disclosure) — document-level (one flag per filing, not per transaction), `NULL` (never a guessed `False`) for filings before the 2023-04-01 effective date. Every row is cross-checked against `issuer_cik` before being trusted — a real, verified issue: 285 mismatches were found across the golden-10 where a tracked company appears in someone *else's* Form 4 as the reporting owner (e.g. JPMorgan itself crossing a 10% stake in an unrelated company), not as the issuer. **As of 2026-08-28, deliberately bounded to the trailing 12 months** (`MIN_FILING_DATE`), not full history — a scoping decision, not a data gap, since `apps/site`'s Insider Activity table only ever shows the 15 most recent transactions per company.

**Why it matters.** Doc 10 names insider/institutional ownership as the product's own actual differentiator for a paid tier — this is the single most fully-built piece of that thesis. `is_10b5_1_plan` in particular lets the product distinguish a pre-scheduled, low-signal sale from a genuinely discretionary one, a real signal-quality improvement doc 22 flagged and doc 23 shipped.

---

## Form 5

**What it legally covers.** The annual insider-transaction summary that catches anything an insider should have reported on Form 4 but didn't, filed within 45 days of fiscal year end.

**What Scrooner extracts.** **Not used** — same deliberate exclusion as Form 3, for the same reason (`ownership/insider.py`'s module docstring). Not in `FORM_ALLOWLIST`, no `core.filing` row.

**Why it matters.** A real, small, deliberately deferred gap: Form 5 activity is rare (most insiders file correctly on time via Form 4) and lower-priority than getting Form 4 itself right first.

---

## Schedule 13D / 13G

**What it legally covers.** Beneficial-ownership disclosure once a holder crosses 5% of a class of a company's stock — Schedule 13D for an "active" investor (may seek control/influence), 13G for a "passive" one (no such intent), both under Exchange Act §13(d)/(g). `/A` variants are amendments (a stake increasing, decreasing, or crossing another threshold).

**What Scrooner extracts.** **Partial.** `pipeline/src/scrooner_pipeline/ownership/beneficial_ownership.py` reads the filing list from `raw.sec_submissions` (zero new discovery fetch), downloads each filing's full-submission `.txt`, and parses the machine-readable SGML `<SEC-HEADER>` block (not the free-text document body — Schedule 13D/13G has never had a structured XML primary document, checked live back to 1995) into `core.beneficial_ownership`: schedule type, `is_amendment`, filer name/CIK, filing date, and CUSIP (extracted via a regex window search around the literal "CUSIP" token, handling three real observed label/number orderings). Every row requires a confirmed `issuer_cik` match before being stored. **`percent_of_class` and `shares_owned` are explicitly left `NULL`** — those figures live only in the filing's free-text body (Item 4/5), whose layout varies across decades of filers and would need its own dedicated, separately-verified text-extraction pass; this is a named, honest gap, not a silent omission.

**Why it matters.** This is the beneficial-ownership half of doc 10's named differentiator, and its captured CUSIP field turned out to unblock two much larger data sets for free (see Form 13F and Form N-PORT below) without needing an external CUSIP↔CIK vendor.

---

## Form 13F (13F-HR / 13F-NT)

**What it legally covers.** The quarterly holdings disclosure large institutional investment managers (>$100M AUM) must file, listing every reportable equity security they hold. Filed *by* the manager, *about* the issuer — never by the issuer itself.

**What Scrooner extracts.** **Full, but scoped to a single most-recent bulk-data window (~3 months), not a multi-quarter history.** `pipeline/src/scrooner_pipeline/ownership/institutional.py` downloads SEC's bulk Form 13F data set (`SUBMISSION`/`COVERPAGE`/`INFOTABLE` flat files, ~100MB/window) and matches `INFOTABLE` rows to a golden company by CUSIP equality against `core.beneficial_ownership.cusip` (Schedule 13D/13G's own captured field — no external CUSIP↔CIK vendor needed). Writes `core.institutional_ownership`: filer name/CIK, shares, `value_usd`, report period, filing date, `is_amendment`. Filters out derivative (`PUTCALL`) and non-share (`SSHPRNAMTTYPE != 'SH'`) rows. A real vendor-provided-spec bug was caught and fixed here: SEC's own field-layout PDF describes `VALUE` as "(x$1000)," but that changed to actual dollars in 2023 — trusting the stale PDF would have shown a real ~$242B position as $242 trillion.

**Why it matters.** The other half of doc 10's named differentiator — institutional ownership % and top-holder identification. As of 2026-08-28, per this doc's own module docstring, this is a *snapshot*, not a trend: 50,786 of stored rows belong to a single filing window (doc 28's own finding) — a real, honestly-scoped limitation, not a display gap.

---

## Form N-PORT

**What it legally covers.** The monthly portfolio-holdings report registered investment companies (mutual funds, ETFs) must file, disseminated quarterly in bulk by SEC.

**What Scrooner extracts.** **Full, single most-recent window (2026 Q2 as of this writing) — and this is now actually built**, not merely scoped. `pipeline/src/scrooner_pipeline/ownership/mutual_fund.py` (built 2026-08-28) downloads SEC's bulk N-PORT data set and matches `FUND_REPORTED_HOLDING.ISSUER_CUSIP` against the same `core.beneficial_ownership.cusip` crosswalk Form 13F uses, filtered to `ASSET_CAT == "EC"` (equity-common) and `PAYOFF_PROFILE == "Long"` (excludes derivatives/shorts/debt). Writes `core.fund_ownership`: fund name (preferring the specific `SERIES_NAME` over the umbrella `REGISTRANT_NAME`, a real distinction the original scoping doc undersold), fund CIK, shares, currency code/value, USD value (only when the filing's native currency is already USD — no currency conversion is attempted, left `NULL` otherwise), percent of fund net assets, report period.

**Real gap found while writing this doc:** [`doc/scoping/21_Scrooner_MF_Holdings_and_Corporate_Actions_Scope.md`](../scoping/21_Scrooner_MF_Holdings_and_Corporate_Actions_Scope.md) and [`doc/scoping/22_Scrooner_EDGAR_Full_Surface_Evaluation.md`](../scoping/22_Scrooner_EDGAR_Full_Surface_Evaluation.md) both still describe N-PORT as "scoped, not built," and root `CLAUDE.md`'s own module list doesn't mention `ownership/mutual_fund.py` at all — but the module exists, is dated 2026-08-28, and its own docstring documents real live verification (a 420MB bulk zip, 14,080 raw golden-10 CUSIP matches, several real field-layout corrections to doc 21's original description). These planning docs are stale on this one point and should be updated to reflect that Stage 5/Phase 2 of doc 21/24 has, in fact, shipped.

**Why it matters.** A clean, fund-only slice of ownership (distinct from Form 13F's broader "any institutional manager" mix) — useful for an investor asking specifically "which funds hold this."

---

## Form 15 family (15-12G, 15-15D, 15F-12B, 15F-12G)

**What it legally covers.** The notice a company (or foreign private issuer, for the `15F-` variants) files to deregister a class of securities — terminating or suspending its Exchange Act reporting obligations. Often, but not always, a signal the company is going private or has been acquired.

**What Scrooner extracts.** **Partial, deliberately conservative.** Added to `normalizer/identity.py`'s `FORM_ALLOWLIST` 2026-08-17 (doc 23 Stage C) for existence capture. `pipeline/src/scrooner_pipeline/company_master/status.py` goes further: it treats a Form 15/15F filing as only a *candidate* delisting signal, then fetches that filing's own cover page and checks the "Title of each class of securities covered by this Form" field for the literal phrase "common stock" before ever setting `core.company.status = 'delisted'`. This extra check is not optional plumbing — it was added after a real false positive: JPMorgan Chase has 4 real Form 15/15D filings on record, all deregistering specific debt/trust-preferred instruments issued by wholly separate financing-subsidiary trusts sharing JPM's parent CIK ("Chase Capital I," etc.), none related to JPM's common stock still being actively listed. A confirmed non-common-stock Form 15 correctly leaves status untouched.

**Why it matters.** This is the only data source that can ever populate a real, evidenced `delisted` status — root `CLAUDE.md` had explicitly flagged "no data source to confirm delisted" as a known gap before this was built. Getting it wrong (a false "delisted" flag) would be a real, visible trust failure, hence the extra confirmation fetch.

---

## SC 14D9 / SC TO

**What it legally covers.** Tender-offer documents: **SC 14D9** is the target company's own required response/recommendation once a tender offer is made for its shares; **SC TO-T**/**SC TO-I** are the tender offer's own commencement documents (third-party or issuer self-tender, respectively).

**What Scrooner extracts.**
- **SC 14D9: existence-only.** Added to `FORM_ALLOWLIST` 2026-08-17 (doc 23 Stage D) — filed by the target under its own CIK, so there's no issuer-vs-filer ambiguity to resolve, unlike Schedule 13D/13G or Form 4. `core.filing` records the filing; no document body is parsed, and — checked directly while writing this doc — nothing downstream currently reads this form type to set a "tender-offer target" flag or similar signal on the company. It's captured but not yet surfaced.
- **SC TO-T / SC TO-I: not used at all.** Not in `FORM_ALLOWLIST`. [`doc/scoping/22_Scrooner_EDGAR_Full_Surface_Evaluation.md`](../scoping/22_Scrooner_EDGAR_Full_Surface_Evaluation.md) §3 names these as real and decision-relevant but explicitly not yet live-verified for structure, unlike everything else in that doc's list.

**Why it matters.** "Someone is trying to buy this company" is a genuinely high-value, real-time signal for an investor — doc 22 ranks it, but building the surfaced product feature (not just recording the filing) is still open work.

---

## 20-F / 40-F (foreign private issuers)

**What it legally covers.** **20-F** is the annual-report equivalent of a 10-K for a non-US-domiciled foreign private issuer listed on a US exchange (e.g. Shell, Alibaba, Novartis); **40-F** is the equivalent for certain Canadian issuers under the US-Canada MJDS regime.

**What Scrooner extracts.** **Identity/filing-record only — explicitly excluded from V1 scope, resolved 2026-08-27 (doc 02).** `20-F`/`20-F/A`/`40-F`/`40-F/A` are in `normalizer/identity.py`'s `FORM_ALLOWLIST`, so `core.company`/`core.filing` rows exist for these filers (originally included because two golden companies, TSM and ENB, use them). **But their XBRL facts are not extracted or mapped** — the full-population run (2026-08-26) confirmed 2,520 foreign private issuers exist in the SEC universe and are deliberately kept out of the `core.fact`/Mapper population. The reasoning, per doc 02's now-closed decision: most FPIs report under IFRS, not US-GAAP, and Scrooner's 30-tag concept-mapping table was built and verified only against US-GAAP filings — including FPIs silently would risk a real trust-moat failure (an IFRS tag resolving to a wrong or absent canonical concept) with no demonstrated user demand to justify the risk yet.

**Why it matters.** This is a deliberate scope boundary, not a technical gap — worth naming clearly so nobody mistakes TSM/ENB's continued identity presence in `core.company` (a byproduct of the golden-10 test set) as evidence that FPI financials are supported.

---

## S-1 / S-1/A

**What it legally covers.** The registration statement a company files with the SEC to register securities for a public offering — most commonly, an IPO prospectus.

**What Scrooner extracts.** **Not used at all.** Not in `FORM_ALLOWLIST`, no `core.filing` row, no parsing anywhere in the pipeline. Doc 07 itself only ever describes it as "relevant later for newly-public companies, not core to MVP."

**Why it matters.** Named here for completeness, not because anything is built: an S-1 is a real dilution/early-warning signal for a company about to go public, but Scrooner's universe is already-listed companies with existing 10-K/10-Q history, so this has no near-term product use.

---

## Cross-cutting notes

- **Existence vs. extraction is a real, load-bearing distinction throughout this pipeline.** A form type being in `normalizer/identity.py`'s `FORM_ALLOWLIST` means only that `core.filing` has a row for it — accession number, form, filing date, period of report, and (for 8-K) the raw `items` string. It does **not** mean any document body has been fetched or parsed. Every ownership form (4, 13D/13G, 13F, N-PORT) that goes further does so in its own dedicated `ownership/` module with its own separately-fetched document.
- **The Collector itself does not filter by form type** (per doc 06/doc 07) — everything a tracked company files lands in `raw.sec_submissions`/`raw.sec_filing_documents` regardless of whether the Normalizer's `FORM_ALLOWLIST` recognizes it. A form type absent from every table above could still be recovered from `raw` later without a new SEC fetch — this is exactly the mechanism that let Form 4/13D-13G/8-K/Form 15/DEF 14A all get built with zero new discovery fetches.
- **"Not used" here means genuinely absent from the codebase as of 2026-08-29**, not a permanent decision — Form 3/5, SC TO, and S-1 are named gaps with a stated reason (lower signal value, unverified structure, out of current universe), not oversights.
