# SEC EDGAR Python Plugin — Usage Plan (EdgarTools & similar)

**Status: Finalized v1.0** (registered into the project as doc 12, adopted 2026-08-16)
**Companion to:** `us-investor-data-points.md` (Section 14 — SEC EDGAR Data Collection Plan)

> **Verified live 2026-08-16, before adopting this plan, not just theoretically:** installed `edgartools` and ran it against real Mapper output. It independently reproduced AAPL's FY2025 revenue ($416,161,000,000) and Q1 FY2024 revenue ($119,575,000,000) exactly, matching our own `analytics.canonical_fact` values. It also surfaced a genuinely useful, real discrepancy: querying JPM's `Revenues` by its raw `fiscal_year`/`fiscal_period` fields returns misleading results — the exact `fy`/`fp`-describes-the-filing-not-the-period issue doc 09 already found and designed around (`doc/learnings/normalizer-day-02-periods.md`). Cross-checking against our own date-keyed data found that JPM's FY2014 revenue *does* exist in our pipeline ($94.205B originally, revised to $95.112B in two later 10-Ks) but is correctly marked `is_authoritative=false` by Stage 2e (a genuine unresolved conflict) — a more precise explanation than doc 11's Day 1 learnings entry originally gave ("no reliable tag exists"), now corrected there. See `doc/learnings/mapper-day-01-concepts.md`'s 2026-08-16 correction.



This doc answers: given we're building the core ingestion pipeline directly on raw SEC
EDGAR APIs (no third-party dependency in the production path), where and how does a
Python plugin like [EdgarTools](https://github.com/dgunning/edgartools) still add value?

Architecture decision recap: **core = in-house, plugin = verification/tooling only.**
Never on the customer-facing request path.

---

## 1. The plugins in question

| Package | Role here | License |
|---|---|---|
| `edgartools` | Primary verification tool — typed wrapper over Company Facts, Submissions, Form 4, 13F | MIT |
| `sec-edgar-downloader` | Raw filing archival for spot-checks / manual review | MIT |
| `sec-edgar-toolkit` | Secondary cross-check option (independent codebase from edgartools, useful for a second opinion) | Open source |

`edgartools` is the one we'll actually build workflows around below; the other two are
situational fallbacks.

---

## 2. Where it plugs into the Screener pipeline

Mapped against the ingestion pipeline implied by Section 14 of the data-points doc:

```
[SEC EDGAR raw APIs] --> [Our ingestion service] --> [Our normalized DB] --> [App/API layer] --> [User]
                                                            ^
                                                            |
                                          [EdgarTools verification jobs] (offline, batch)
                                                  |
                                          [Discrepancy log / alert]
                                                  |
                                          [Engineer review queue]
```

The plugin never sits between EDGAR and the production database. It runs in parallel,
independently, and only ever produces a **report**, not a write to production data.

---

## 3. Concrete use cases

### 3.1 Nightly/weekly reconciliation job (primary use case)

**What:** For a rotating sample of tracked companies (e.g., 5–10% of the universe per
night, full universe over ~2 weeks), recompute a fixed set of core metrics using
EdgarTools and diff them against what our own pipeline stored.

**Metrics to check** (highest bug-risk, highest downstream impact if wrong):
- Revenue (TTM and last fiscal year)
- Net Income / EPS (basic & diluted)
- Total Assets, Total Liabilities, Stockholders' Equity
- Shares Outstanding
- Cash from Operations, CapEx (→ our computed FCF)
- Dividends paid, buybacks (`PaymentsForRepurchaseOfCommonStock`)

**Pseudocode:**

```python
from edgar import Company, set_identity
set_identity("screener-verify verify@yourdomain.com")

def verify_company(ticker, our_stored_facts):
    ref = Company(ticker).get_financials()
    checks = {
        "revenue_ttm": ref.income_statement().get("Revenues"),
        "eps_diluted": ref.income_statement().get("EarningsPerShareDiluted"),
        "shares_outstanding": ref.balance_sheet().get("CommonStockSharesOutstanding"),
        "cfo": ref.cash_flow_statement().get("NetCashProvidedByUsedInOperatingActivities"),
    }
    discrepancies = []
    for field, ref_value in checks.items():
        our_value = our_stored_facts.get(field)
        if not within_tolerance(our_value, ref_value, pct=0.5):  # 0.5% tolerance
            discrepancies.append((field, our_value, ref_value))
    return discrepancies
```

**Output:** A discrepancy log written to a review queue (not auto-corrected — a human
or a second automated check confirms which source is right, since restatements and
period-alignment differences can cause legitimate mismatches).

### 3.2 New-ticker onboarding sanity check

**What:** When we add a new company to the tracked universe, before its data goes live,
run one EdgarTools pull as a "does this look sane" check against our freshly-ingested
data — catches onboarding-time bugs (wrong CIK resolved, wrong fiscal year end assumed,
non-standard XBRL taxonomy usage) before they reach users.

**Where:** Part of the onboarding/QA step in the ingestion pipeline, run once per new
ticker, not recurring.

### 3.3 Edge-case / non-standard filer fallback investigation

**What:** Some companies use custom XBRL extension tags instead of standard `us-gaap`
tags, or restate prior periods in ways that trip up simple tag-based parsers. When our
pipeline flags a company with missing/null core fields, use EdgarTools interactively
(in a notebook, not production code) to inspect what tags that specific company actually
used, and use that to fix our tag-mapping table.

**Where:** Ad hoc, used by engineers debugging specific tickers — not a scheduled job.

### 3.4 CI regression tests for our own XBRL parser

**What:** Maintain a small fixed set of "golden" companies (e.g., AAPL, a mid-cap
industrial, a REIT, a bank — different filing styles) with known-correct expected
values. On every change to our in-house EDGAR parsing/tag-mapping code, run both our
parser and EdgarTools against these golden companies and assert both agree with the
expected values (and with each other, as a secondary signal).

**Where:** CI pipeline, on pull requests that touch the ingestion/parsing code.

### 3.5 Insider activity (Form 4) & institutional ownership (13F) cross-check

**What:** These are higher-complexity feeds (structured relationship data, not just
flat financial facts) where our in-house parser is more likely to have subtle bugs
early on. Use EdgarTools's Form 4 and 13F object models as the reference implementation
during initial build, and periodically thereafter, to validate our own insider-activity
and institutional-ownership tables.

**Where:** Weekly batch job, same pattern as 3.1, scoped to the Section 8 (Ownership &
Insider Activity) data points specifically.

### 3.6 Manual research / prototyping tool (not shipped)

**What:** During feature design (e.g., prototyping the "guidance track record" scoring
logic from Section 9), use EdgarTools in a notebook to quickly pull and explore data
without waiting on our own pipeline — speeds up R&D before something becomes a real
in-house feature.

**Where:** Local dev/notebook environment only. Never packaged into a deployed service.

---

## 4. What we explicitly do NOT use the plugin for

- Serving any data directly to the production app or API (always our own DB).
- Being a required dependency at request time — if it's down, unavailable, or removed
  from PyPI, nothing user-facing breaks.
- Computing our differentiated metrics (FCF yield, dilution trend, pros/cons flags) —
  those are our IP and logic, built on our own data, even if EdgarTools happens to
  offer similar helper functions.
- Bulk primary ingestion — that stays on the raw EDGAR bulk ZIP / Submissions API path
  described in Section 14.5 of the data-points doc.

---

## 5. Risk mitigation for using it even as a verification tool

- **Pin the version.** Don't auto-upgrade; review changelogs before bumping, since a
  changed parsing behavior in the plugin could produce false-positive discrepancies.
- **Isolate it.** Run verification jobs in their own container/environment, separate
  from the production ingestion service's dependency tree, so a plugin issue (broken
  install, dependency conflict) can't affect production.
- **Treat mismatches as signals, not truth.** When our data and EdgarTools disagree,
  the default assumption should be "investigate," not "EdgarTools is right" — both
  ultimately derive from the same EDGAR source data, so disagreements are usually a
  parsing/period-alignment bug on one side or the other, not a data-source problem.
- **Have a fallback.** If EdgarTools becomes unmaintained or breaks against a new EDGAR
  schema change, the verification layer can be paused without any production impact,
  and swapped for `sec-edgar-toolkit` or a hand-rolled comparison script.

---

## 6. Summary table

| Use case | Frequency | Environment | Blocking for prod? |
|---|---|---|---|
| Nightly/weekly reconciliation (3.1) | Rotating sample, nightly | Batch job | No |
| New-ticker onboarding check (3.2) | Once per new ticker | Onboarding pipeline step | Advisory only |
| Edge-case investigation (3.3) | Ad hoc | Engineer notebook | No |
| CI regression tests (3.4) | Every PR touching parser | CI | Yes — for the parser change, not for prod data |
| Insider/13F cross-check (3.5) | Weekly | Batch job | No |
| Research/prototyping (3.6) | As needed | Local dev | No |
