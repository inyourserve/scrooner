# Mapper Day 3 — Metric Formula Definitions

## ROIC's formula, pinned with real evidence rather than a textbook default

Doc 02 explicitly left ROIC's tax-rate/invested-capital detail open for this stage to resolve "with a version number." Locked: `NOPAT = Operating Income × (1 − Income Tax Expense ÷ Income Before Tax)`, `Invested Capital = Total Debt + Stockholders' Equity − Cash`, `ROIC = NOPAT ÷ Invested Capital` — all six inputs already resolved by Stage 3b, no new canonical concepts needed.

Sanity-checked against real AAPL data before locking it in (Q1 FY2026, the first period found with all six inputs simultaneously authoritative): tax rate 17.46%, invested capital $131.4B, single-quarter NOPAT/invested-capital = 31.95% — a plausible-looking number on its own.

## A real distortion caught by checking a second way, not just accepting the first plausible number

Before treating 31.95% as validated, tried the obvious next step — annualizing the single quarter (×4) to get a comparable-to-FY figure, since ROIC is conventionally an annual metric. That gives **127.8%** — not plausible even for Apple. Investigated why rather than picking whichever number looked more familiar: AAPL's Q1 (Oct-Dec, the holiday iPhone quarter) is its seasonally strongest by a wide margin, so multiplying that one quarter's operating income by 4 substantially overstates the year. Checked whether this is ROIC-specific or structural: it's structural — any ratio dividing a *flow* (an income-statement figure, measured over a period) by a *stock* (a balance-sheet figure, measured at a point in time) will misbehave on a single quarter without proper trailing-twelve-month aggregation of the flow side. ROE has the identical structure (Net Income ÷ Stockholders' Equity) and the identical risk.

Checked the other 12 EDGAR-only metrics against this same structural question before writing them down, not just ROIC/ROE:
- Margin ratios (gross/operating/net/FCF) and Interest Coverage Ratio: flow ÷ flow, both sides measured over the same period — no distortion, valid on any period.
- Debt/Equity, Current Ratio: point-in-time ÷ point-in-time — no period-length question at all.
- Only ROIC and ROE have the flow/stock mismatch.

**Consequence for Stage 3d:** ROIC and ROE compute directly on FY periods (where the income-statement figure already represents a full year — no distortion) but are deliberately *not* computed from a bare quarterly period until Stage 3e's TTM windows exist to aggregate the flow side properly first. Written into `mapper/definitions.py`'s module docstring as an explicit constraint Stage 3d must respect, not left implicit.

## Two more real gaps found while sourcing the sanity-check data itself

Neither is a bug — both are the same "null over guess" pattern already established, showing up in new places:

- **NKE has zero `OperatingIncomeLoss` facts across its entire filing history** — not missing for one period, genuinely never tagged. NKE's income statement apparently doesn't break out a discrete operating-income line the way AAPL/MSFT do. Confirms Operating Margin, ROIC, and Interest Coverage Ratio will correctly be null for NKE specifically, for a real structural reason, not a resolver gap.
- **AAPL's own `total_debt` is null for FY2024** — its `LongTermDebt` tag has six authoritative-conflicting values for that period (two figures $38M apart, appearing across several filings), so Stage 2e correctly flagged all of them non-authoritative. A third real instance of the same silent-small-revision pattern already documented for JPM (Normalizer Day 5, Mapper Day 1/2) — the Normalizer's conflict handling is catching this consistently across companies, not just the cases it was originally tuned against.

## Verification

- 20 `metric_definition` rows seeded (18 product-facing metrics per doc 02's guardrail; Revenue Growth and EPS Growth each split into separate YoY/3Y-CAGR rows for independent storage, not a scope expansion), 39 `metric_definition_input` rows.
- 14 rows `requires_price=false`, 6 `requires_price=true` — matches doc 02's 12-EDGAR-only / 6-price-dependent split exactly once the growth-metric splits are accounted for.
- Reran the seed — identical counts (20/39), confirming idempotency.

## Why it matters going forward

The sanity-check almost stopped at the first plausible-looking number (31.95%) — it was the deliberate second check (comparing against the annualized version) that surfaced the real distortion. "One number that looks reasonable" was insufficient evidence here the same way it's been insufficient at every other stage of this build; the discipline that caught it was checking the *same* quantity two structurally different ways and noticing they disagreed by 4x, not re-deriving a new verification technique from scratch.
