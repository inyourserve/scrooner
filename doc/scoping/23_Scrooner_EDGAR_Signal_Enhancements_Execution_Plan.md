# 23 — Scrooner: EDGAR Signal Enhancements Execution Plan

Scopes the 5 items from doc 22's ranked list that weren't already covered by doc 21 (8-K `items` and Form N-PORT — see that doc): Form 4's `aff10b5One` field, `dei:EntityPublicFloat`, Form 15 (deregistration), SC 14D9/TO (tender offers), and dimensional/segment XBRL. Each was checked live this pass — real filings, real field values, real structure — not assumed from doc 22's earlier pass. **Nothing here is built.** Same rhythm as doc 19 before Stage 4: scope with real evidence, confirm, then build.

> **Status:** Draft (2026-08-17) — a scoping/execution plan, not yet built. **Owner:** Founder / Product · **Review:** before any stage below is built.

---

## Stage A — Form 4's `aff10b5One` (Rule 10b5-1 trading-plan indicator)

**What it is**: SEC's 2023 rule amendment (effective for transactions on/after 2023-04-01) requires Form 4 to disclose whether the reported transaction(s) were made under a pre-arranged Rule 10b5-1(c) trading plan — a materially weaker "this insider is bearish" signal than a discretionary trade.

**Confirmed live, not assumed**: fetched a real AAPL Form 4 (`0001140361-26-025622`) and four real Microsoft Form 4s (including two open-market sales, transaction code `S`). The field appears exactly once per document — `<aff10b5One>false</aff10b5One>` (AAPL, boolean-word lexical form) or `<aff10b5One>0</aff10b5One>` (MSFT, boolean-digit lexical form) — positioned once, before the transaction tables, not per-transaction-row. **Real, worth-stating limitation**: this means the flag applies to the *filing as a whole*, not to a specific transaction within it — a Form 4 reporting both an RSU vesting (never 10b5-1) and a discretionary sale in the same filing can't have the two distinguished by this field alone. Both real lexical forms (`false`/`0`) must be handled by the parser; don't assume one.

**Build shape**: add `is_10b5_1_plan` (nullable boolean) to `core.insider_transaction`, parsed from `aff10b5One` in `ownership/insider.py`'s existing `_parse_form4` — same document already fetched, zero new fetches. `NULL` for any Form 4 filed before 2023-04-01 (field doesn't exist pre-rule-change) — never defaulted to `false`, same "leave null, don't guess" discipline as `percent_of_class`. Company page's Insider Activity table gets a new column/badge distinguishing scheduled vs. discretionary trades.

**Effort/risk**: low. Smallest item in this doc — one field, one column, no new fetch, no new design question.

---

## Stage B — `dei:EntityPublicFloat` as a labeled market-cap proxy

**What it is**: every 10-K cover page discloses the aggregate market value of shares held by non-affiliates, as of the last business day of the filer's second fiscal quarter (a specific, once-a-year, backward-looking snapshot — not a live price).

**Confirmed live**: real AAPL values already sitting in `core.fact`, unmapped — $3.253T (2025-03-28), $2.629T (2024-03-29), back to $2.021T (2021-03-26). Directionally consistent with real AAPL market-cap history. `EntityCommonStockSharesOutstanding` (quarterly, already mapped as `shares_outstanding`) is the companion field.

**Real design question, not just a build task**: this is *not* Market Cap — it excludes affiliate/insider-held shares, updates once a year, and lags by up to 12 months at worst. Doc 02's locked Market Cap metric is explicitly formula-locked pending the real price-vendor decision; mapping `EntityPublicFloat` under the `market_cap` name would blur that line the same way this project's own discipline (doc 05) exists to prevent. **Recommend**: a distinctly named concept/metric (e.g. `public_float`, not `market_cap`), shown with an explicit "as of [date], non-affiliate shares only" label — never silently substituted where a user would expect real-time Market Cap.

**Build shape**: new `analytics.canonical_concept` row (`public_float`), mapped from `dei:EntityPublicFloat`, reusing Mapper's existing `resolve()` unchanged (same pattern as doc 17's statement concepts). Company page shows it in a clearly-labeled, clearly-different spot from the still-blocked Market Cap field, not as a replacement for it.

**Effort/risk**: low build effort, but the labeling/design question above needs an explicit answer before shipping — a "looks like Market Cap but isn't" mistake would be a real trust-moat violation (doc 02's traceability principle), not just a cosmetic issue.

---

## Stage C — Form 15 (deregistration) → real `delisted`/`deregistered` status

**What it is**: the form a company (or its transfer agent) files to formally terminate or suspend its SEC reporting obligations — filed at exactly the "going private" or "delisted" moment root `CLAUDE.md` already flags Company Master has no data source for.

**Confirmed live**: form-type variants are `15-12G`, `15-12G/A`, `15-15D`, `15F-12B`, `15F-12G` (no bare "15"). Found and read a real, very recent example: **American Woodmark Corporation** (NASDAQ: AMWD) filed `15-12G` on 2026-06-08 — plain HTML, not XBRL, but a fixed SEC template, and its own text states "**Approximate number of holders of record as of the certification or notice date: One**" — a clean, unambiguous real-world go-private/acquisition-completion signal.

**Real finding — this is even cheaper than doc 22 estimated**: the document body doesn't need to be parsed at all. The *form type itself* is the signal, and form type is already captured in `raw.sec_submissions`'s existing filing list for every golden company — the same "already-fetched, just never looked" pattern as 8-K `items` (doc 21) and Stage 4's CUSIP crosswalk before it. Detecting "this company deregistered" is a query, not a fetch.

**Build shape**: extend `company_master/status.py`'s status derivation to check for `15-12G`/`15-15D`/`15F-12B`/`15F-12G` in the company's own filing history — if present, `core.company.status` becomes a real, evidenced `delisted`/`deregistered` value instead of the current `active`/`stale`/`unknown` set (which the schema comment already says can't represent this). Zero new fetches.

**Effort/risk**: very low. No golden-10 company has actually filed one (all 10 remain active), so this stage can't be *verified* against the golden set the way every other stage in this project has been — it would need either a temporarily-added real example (like American Woodmark) or an honest note that the logic is verified against real EDGAR data but not against the golden-10 specifically, a real gap in this project's own "reconcile against the golden set" methodology worth naming explicitly, not glossing over.

---

## Stage D — SC 14D9 / SC TO (tender offers)

**What it is**: tender-offer disclosure documents. SC 14D9 is the *target* company's own recommendation statement, filed under the target's own CIK. SC TO-T/SC TO-C relate to the offer itself (filed by or about the bidder).

**Confirmed live** (2026 Q2 full-index sample): real, current, recognizable examples — Apellis Pharmaceuticals, Assertio Holdings, Destination XL Group, FS KKR Capital Corp, Genco Shipping, KalVista Pharmaceuticals, Nuvalent, and others all filed `SC 14D9` in Q2 2026 alone. **SC 14D9 is filed by the target under its own CIK — zero issuer-vs-filer ambiguity**, unlike Schedule 13D/13G/Form 4 (doc 19's own repeated finding). `SC TO-C` (pre-commencement communications) also appeared cross-indexed under the same target CIKs in this sample — real corroborating evidence, not yet independently verified for what `SC TO-T` itself (the bidder's own filing, likely under a *different* CIK) looks like structurally.

**Build shape**: same "form-type presence is the signal" pattern as Form 15 (Stage C) for the cheap first cut — `SC 14D9` appearing in a company's filing history means "this company is currently/was recently the subject of a tender offer," zero parsing needed. A richer version (deal terms, offer price, acquirer identity) would need real document parsing — `SC TO-T`'s own structure and its issuer-vs-filer shape weren't verified this pass and would need the same kind of check doc 19 already did for 13D/13G before trusting it.

**Effort/risk**: low for the cheap presence-only signal (Stage C's pattern, reused). Higher, and not yet scoped, for deal-detail extraction — flagged as a real next investigation, not assumed solvable at the same cost.

---

## Stage E — Dimensional/segment XBRL (revenue by product, revenue by geography)

**What it is**: the breakdown investors actually want on a company page (screener.in-style "segment results") — e.g. AAPL's iPhone/Mac/Services split, or Americas/Europe/Greater China split.

**Confirmed live, and confirmed genuinely harder than everything else in this doc**: fetched AAPL's real XBRL instance document directly (`aapl-20240928_htm.xml`, not the Company Facts API, which — confirmed in doc 22 — strips this entirely). Found 231 dimensionally-qualified contexts using real axes including `srt:ProductOrServiceAxis` and `srt:StatementGeographicalAxis` (exactly the ones needed for segment/geography revenue), alongside a dozen other axes (debt instruments, hedging, fair-value hierarchy, etc.) this project has no use for.

**The real, unsolved design problem, confirmed concretely this pass**: the *members* on those axes are frequently **company-specific custom extension elements** (e.g. `aapl:...Member`-style names), not universal us-gaap values — meaning "which member means iPhone" isn't a single mapping that works across companies the way `Revenues`/`NetIncomeLoss` do. This needs either (a) per-company curation, the same labor-intensive pattern Mapper already uses for revenue-tag drift, just repeated for every company's own segment taxonomy, or (b) a more general approach that captures dimensional facts generically and renders them using each filer's own disclosed label text rather than forcing a fixed canonical name — a real architectural choice, not a small addition.

**Build shape**: not proposed here — this stage needs its own dedicated design pass (parsing the raw XBRL instance document is itself new infrastructure, since nothing in this pipeline currently touches instance XML directly, only the Company Facts/Concept APIs) before a build plan the way Stages A-D already have one.

**Effort/risk**: high, and the highest-uncertainty item in this entire doc. Correctly still the lowest-priority item in doc 22's ranking.

---

## Summary — effort-ranked

| Stage | New fetch? | Effort | Verifiable against golden-10? |
|---|---|---|---|
| A — `aff10b5One` | No | Low | Yes |
| B — `EntityPublicFloat` | No | Low (+ a labeling decision) | Yes |
| C — Form 15 status | No | Very low | **No golden-10 company has filed one** — real methodology gap, noted not hidden |
| D — SC 14D9 presence signal | No | Low | **No golden-10 company has filed one either** — same gap as C |
| E — Dimensional/segment XBRL | New (raw instance XML) | High, undesigned | Yes, but needs its own design pass first |

## What this doc does not do

Same discipline as doc 18/19/20/21/22: nothing here is built, no metric/field is added to doc 02's locked list, and Stage E is deliberately left undesigned rather than forced into a plan that would just be guessing. Stages C and D's golden-10 verification gap is named explicitly rather than quietly built around — if either is picked up, it needs either a temporarily-widened test set or an honest acknowledgment that "verified against real EDGAR data, not against the golden-10 specifically" is the actual evidence bar being met.
