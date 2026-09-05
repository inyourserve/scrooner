# 39 — Employee Headcount Full-Coverage Plan (Unstructured 10-K Text Extraction)

> **Status:** Draft (2026-08-30) — a scoping plan, not built. Prompted directly by a user request for full-population employee headcount coverage (for a future layoff/employee-growth dashboard), after the XBRL-only path was found to cover only 178 of ~5,024 active companies (~3.5%). **Owner:** Founder/Product · **Review:** before Stage A begins, and again after Stage B's real coverage number is measured.

## The gap this closes

`dei:EntityNumberOfEmployees` is an *optional* structured XBRL tag. Checked live 2026-08-30: even Apple, Microsoft, Amazon, Alphabet, and Costco — filers with no plausible excuse to under-report — do not tag it. Every one of them still discloses headcount, just as prose text in their 10-K's Item 1 "Human Capital" section, which XBRL-only ingestion never sees. This is not a fetch-depth problem (widening a date range fixes nothing) — it requires a new capability: **parsing 10-K narrative text**, something this project has never built before ([`doc/foundational/12`](../foundational/12_Scrooner_Edgar_Python_Plugin_Usage.md)'s `edgartools` is verification-only; every other data point in Scrooner comes from structured XBRL).

## Real evidence gathered before writing this plan

Per doc 05's build method ("check live before trusting an assumption"), three real 10-Ks were fetched and inspected directly, not assumed:

| Company | Filing | Actual disclosure text found |
|---|---|---|
| Apple | 10-K filed 2025-10-31 | *"As of September 27, 2025, the Company had approximately 166,000 full-time equivalent employees."* |
| Microsoft | 10-K filed 2026-07-29 | *"HUMAN CAPITAL RESOURCES — As of June 30, 2026, we employed approximately 223,000 people on a full-time basis, 121,000 in the U.S...."* |
| Costco | 10-K filed 2025-10-08 | *"Employee Base — At the end of 2025, we employed 341,000 employees worldwide."* |

**A real extraction hazard found in the same pass, not assumed:** a first naive attempt (crude HTML-tag stripping, no awareness of inline XBRL) matched garbage — `us-gaap:EmployeeStockMember`, `cost:EmployeesMember` — pulled from the document's hidden `<ix:header>` block (the machine-readable inline-XBRL context data every modern 10-K embeds inline with the human-readable text). Only after stripping that block first did the real sentences surface cleanly. **Any extractor must strip `<ix:header>`, `<script>`, `<style>`, and `display:none` elements before searching visible text — a plain regex-over-raw-HTML approach will silently produce wrong matches, not just fail loudly.**

**Confirmed empty for the raw-storage question**: `raw.sec_filing_documents` has 50 rows tagged `form='10-K'`, but every one has an empty `storage_path` — these are index-only rows (filing exists, was never fetched), not stored document bodies. Full 10-K primary-document text is not currently stored anywhere in this project. This is a genuinely new fetch, not a re-read of existing raw storage (unlike every other 2026-08-29 zero-fetch win — this one is NOT zero-fetch).

## Feasibility assessment

**The core pattern is real and consistent** across all three companies checked: a "Human Capital"-titled section (post-2020, per SEC's Item 101(c) human capital disclosure rule) containing a sentence of the shape `[as of DATE,] [subject] employed/had approximately [NUMBER] [full-time] employees`. A curated regex targeting this shape, run against properly-cleaned visible text, should resolve a solid majority of large/mid-cap filers.

**Real risks found or reasoned through, not glossed over:**
1. **Multiple numbers in one sentence/paragraph** — Microsoft's own sentence contains both the total (223,000) and a regional breakdown (121,000 in the U.S.) in the same match. A naive "first number near 'employ'" heuristic happens to work here (total comes first) but this ordering is not guaranteed across companies — needs real validation across a larger sample, not assumed safe from 3 examples.
2. **No disclosure at all** — SEC's Item 101(c) requires human capital disclosure only "to the extent material," not a specific headcount number. Some filers (holding companies, REITs with few direct employees, shell/SPAC-stage companies — the same CIK-2,000,000+ population that broke the beneficial-ownership crosswalk's chunk sizing) may have zero employees or simply never state a number. **100% coverage is not achievable even with parsing** — this needs to be message-tested with the user before "full coverage no matter what" is treated as a literal target rather than "as close as the source data allows."
3. **Pre-2021 filings** — the Item 101(c) human capital rule took effect for fiscal years ending after 2020-11-09. A 10-K filed before then may have no comparable section at all. This caps realistic **historical depth** at ~2021-onward, not a company's full filing history — directly relevant to the layoff/growth dashboard's need for a real multi-year series.
4. **Approximate, not exact, values** — every example found used "approximately." Storage must carry this as a flag, never silently presented as an exact figure the way an XBRL fact would be.

## Recommended two-tier approach

**Tier 1 — regex/lexical extraction (buildable now, zero new vendor decision):**
A curated pattern set targeting the "Human Capital"/"Employees"/"Human Capital Resources" section header plus the common phrasings found above, run against XBRL-hidden-content-stripped visible text. Store a value **only** when a single, unambiguous total is found with high confidence — otherwise leave null, per this project's standing "honest null over guess" discipline ([`CLAUDE.md`](../../CLAUDE.md)'s ownership-module rule generalizes directly here). This should be built and measured first — its real coverage % becomes the evidence for whether Tier 2 is worth doing at all.

**Tier 2 — LLM-assisted extraction (blocked on doc 02's open LLM vendor decision):**
For filings Tier 1 can't confidently resolve, an LLM prompt (strict output contract: single integer + as-of date + source sentence, or explicit "not found" — never a bare guess) would likely be far more robust against phrasing variance than any regex set could ever be. This directly mirrors the AI Query Engine's already-established 6a/6b-now, 6c-deferred precedent ([`doc/execution-plans/15`](../execution-plans/15_Scrooner_AI_Query_Engine_Execution_Plan.md)) — build the deterministic path now, defer the LLM path behind a swappable interface until a vendor is actually chosen. **Not proposing this be decided now** — flagging it because it directly affects how close to "full coverage" this can realistically get, the same way it affects the AI Query Engine.

## Storage design

**A new table, not `core.fact`.** XBRL facts in `core.fact` carry `is_authoritative` and are trusted as ground truth throughout the Mapper (`core.fact.is_authoritative = false` is a hard filter per this project's own standing rule). Text-parsed values are a fundamentally different confidence class — mixing them into `core.fact` as if they were tagged XBRL data would violate that discipline and silently degrade trust in every other concept sharing that table. Proposed: `core.employee_headcount_disclosure` (company_id, as_of_date, headcount, is_approximate, extraction_method [`regex`|`llm`], source_filing_accession, source_snippet, confidence). The Mapper's `analytics.canonical_fact` layer can still union this with the existing `dei:EntityNumberOfEmployees` XBRL rows when serving a dashboard — that blending happens at the analytics layer, where provenance is still visible per-row, not at the raw-storage layer.

## Phased build plan

| Stage | Scope | Gate before starting |
|---|---|---|
| **A** | New fetch: store each company's latest 10-K primary document body (currently not stored — confirmed above). Most-recent filing only, per [doc 38](../foundational/38_Scrooner_History_Depth_Gate.md)'s case-1 reasoning (start narrow, expand only once the pattern is proven). | None — ready to build |
| **B** | Build the hidden-content-stripping + regex extractor. Run against a **larger sample than golden-10** (proposed: 30-50 companies spanning sector/size, not just mega-caps that are easiest to parse) to get a real, honest coverage % — not assumed from 3 examples. | Stage A done |
| **C** | Decide on Tier 2 (LLM) **using Stage B's real number**, not assumed necessary up front — if regex alone clears, say, 70-80% of the population, that may already be the right stopping point pending a product call. | Stage B's real coverage measured |
| **D** | Expand from latest-only to full available history (2021-onward floor per the Item 101(c) rule) — only once Stages A-C are proven, since this multiplies fetch/parse cost by however many years of 10-Ks each company has filed. This stage is what actually enables the layoff/growth dashboard's time-series need — A-C alone only get a single latest-period snapshot per company. | Stages A-C complete and reviewed |

## Honest ceiling on "full coverage no matter what"

Even at full build-out, this cannot reach literal 100% — a nontrivial slice of the ~5,024-company population (very small filers, holding companies, pre-2021 fiscal years, filers with genuinely no human capital disclosure) will remain uncoverable without fabricating a number, which this project will not do. The realistic target is "as close as the source data structurally allows, every gap explained rather than silently guessed" — the same honest-null standard applied everywhere else in Scrooner, not a literal 100% guarantee.
