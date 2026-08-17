# Normalizer Day 6 — Restatement Handling

## Finding: the linking rule holds for 39/42 amendments; the 3 gaps are all pre-2002 filings

Before writing `restatements.py`, pulled every `10-K/A`/`10-Q/A`/`40-F/A` across the golden-10 (43 total, once ENB/TSM included) and tested the candidate linking rule — "most recent prior filing, same company, same base form family, same `period_of_report`" — against all of them before trusting it. Held cleanly for 39; the 3 unmatched companies' 7 gaps are all filings from 1994–2002, several carrying SEC's `9999999997` dummy-CIK prefix used for old paper filings — the original genuinely isn't in our captured submissions history, not a linking bug. Left `amends_filing_id` null and counted for these, rather than guessing.

Generalized the rule to match against either the bare base form or an earlier amendment of it (not just the exact base form), so a hypothetical amendment-of-an-amendment chain links to its immediate predecessor rather than always jumping back to the original — untested in this golden set (no such chain exists here) but a correct, low-cost generalization to have in place before it's needed.

## Finding: three different "zero superseded pairs despite linked" cases, all explainable, none a bug

Ran the fact-supersession step and found `superseded_pairs=0` for MSFT (6 linked amendments), NKE (3), and GOOGL (2) — worth checking before trusting the output, since a real bug (e.g. a broken join) would look identical to "genuinely nothing to supersede."

- **MSFT's 2012 10-Q/A**: amended its original just **8 days** after filing. The original accession number has **zero** facts anywhere in `core.fact` — SEC's XBRL data never retained a datapoint citing that short-lived accession at all, presumably because it was superseded before any later filing's comparative ever cited it back. The linking itself is correct (verified `period_of_report` and form match exactly); there's simply nothing on the original side to supersede.
- **NKE/GOOGL's older amendments**: mostly 1990s–2002-era filings, predating XBRL entirely (mandatory XBRL tagging phased in ~2009–2011) — `companyfacts` has no data for that era at all, so an amendment from before XBRL existed correctly has 0 facts on both sides.
- **ARCC (doc 09's named test case)**: 4 of 5 linked amendments produced exactly 1 superseded pair each (4 total, not 8, despite each amendment having 2 of its own facts). Checked why: each amendment reports both `EntityCommonStockSharesOutstanding` (dated as of the *amendment's own filing date* — a period that never existed in the original, correctly not matched) and `EntityPublicFloat` (dated as of the original 10-K's own reference period — correctly matched and superseded). Turns out ARCC's amendments are routine SEC Part-III/cover-page updates, not P&L or balance-sheet restatements — doc 09's "original and corrected figures" framing suggested something meatier, but the mechanism is proven correct regardless of which real-world amendments happened to be available to test it against.

## Verification: found genuine, material financial restatements elsewhere in the golden set

Since ARCC's own amendments turned out to be cover-page-only, checked whether the mechanism also handles a real P&L/balance-sheet restatement correctly, using JPM and AAPL's (much larger) superseded-pair sets:

- **JPM's 2012 10-Q/A**: `EarningsPerShareDiluted` restated from **$1.31 → $1.19/$1.20** (~9% change) for the quarter ended 2012-03-31, alongside dozens of other `us-gaap` balance-sheet lines (`Assets`, `DerivativeAssets`, `Capital`, etc.). Both values now correctly queryable — original marked non-authoritative, amendment authoritative.
- **AAPL's amendment**: FY2008 total assets restated from **$39.572B → $36.171B** — very likely tied to Apple's real historical stock-option-backdating-related restatement. Same pattern: both values preserved, correctly ordered.

Both real, both material, both handled identically to ARCC's routine case — the mechanism doesn't care whether a restatement is a typo-level cover-page fix or a material EPS correction, which is the correct, general behavior doc 09 asked for.

## Verification summary

- 43 amendments found across the golden-10; 36 linked, 7 correctly left unmatched (all pre-2002, explained above).
- 681 fact pairs superseded; spot-checked across three companies (ARCC, MSFT, JPM/AAPL) with three different explanations for the counts observed, all verified against real accession-level data, not assumed.
- Originals confirmed still fully queryable after supersession (ARCC's `EntityPublicFloat` history: every original row present, `is_authoritative=false`, value intact; every amendment row `is_authoritative=true`, `supersedes_fact_id` populated).
- Reran the whole job — identical stats (36/7/681), confirming idempotency.
- DB size unchanged after vacuum (52 MB) — this stage's update volume (681 pairs × 2 rows) was too small to cause the bloat seen on Days 4–5's full-table passes.

## Why it matters going forward

Zero-result outputs need the same scrutiny as non-zero ones — three different companies produced "0 superseded pairs" for three completely different, legitimate reasons (an 8-day-lived original with no citable XBRL history, pre-XBRL-era filings, and cover-page-only amendments), and none of them would have been distinguishable from an actual bug without checking the underlying accession-level data directly. Same standing lesson as every prior Normalizer day, applied here to a new shape: "it ran and produced a plausible-looking number" is not verification; checking *why* a specific number is what it is remains the actual bar.
