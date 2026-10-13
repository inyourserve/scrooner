# Phase 3 step 1: the SPAC-merger pattern does not generalize (2026-10-13)

Doc 50 Phase 3 proposed a period-conditional "genuinely doesn't apply" classifier for
cash-flow gaps, because three post-SPAC companies (MultiSensor AI Holdings, VSee Health,
Alpha Star Acquisition) were missing `cash_flow_investing` only for their pre-merger
shell years. Doc 53 agreed on a gated plan: verify the pattern on the whole gap
population first, build nothing unless it holds. This is that verification.

## Test 1 -- are the gaps in the shell years?

`pipeline/scripts/phase3_spac_gap_probe.py` (read-only). A SPAC holds a trust account,
tagged `AssetsHeldInTrust*` in XBRL, which is independent of SIC and of our own
extraction. For every `cash_flow_investing_resolved` gap whose cause is a "genuine
absence" (`no_line_item_filed`, `no_mapped_tag`; 12,682 gaps, 1,680 companies) it asks
whether the gap is before the company's first present period ("leading") and whether it
falls while the company was still reporting a trust account ("in_spac").

| cause | gaps | leading | in_spac | leading AND in_spac (the Phase 3 pattern) |
|---|---|---|---|---|
| no_line_item_filed | 8,647 | 19.8% | 11.0% | **4.1%** |
| no_mapped_tag | 4,035 | 4.2% | 15.9% | **0.3%** |

Where the gaps actually sit relative to the company's own reported history:

| cause | before first present | **inside it** | after last present |
|---|---|---|---|
| no_line_item_filed | 19.8% | **51.6%** | 28.6% |
| no_mapped_tag | 4.2% | **80.2%** | 15.6% |

71% / 66% of them are quarterly (Q), the rest FY / Q4. No gap belongs to a company that
never reports the concept (0%), matching doc 50's earlier finding.

**Verdict: do not build a SPAC-timing classifier.** It would explain about 4% of one
cause and 0.3% of the other. The pattern is real for those three companies and does not
describe the population. The dominant shape is a hole *inside* a company's own history.

## Test 2 -- is `no_line_item_filed` right that the line is absent?

`pipeline/scripts/verify_no_line_item_filed.py` (read-only). `no_line_item_filed`
(finding type `legitimate_absence`, `sanity/period_completeness.py`) is decided from the
filing's XBRL facts: no fact whose tag matches the concept's pattern anywhere in the
filing. It cannot see a line that is on the rendered statement but tagged in a way the
pattern misses. A random sample of 40 interior-or-any quarterly `no_line_item_filed`
gaps was checked against the filing's own rendered cash-flow statement:

- **33 of 40 (82%)**: the statement has no investing-activities total. Confirmed.
  (Typically a tiny company with no investing activity that quarter, so it omits the line.)
- **7 of 40 (18%)**: the statement DOES show "Net cash (used in) investing activities".
  The gap is not a legitimate absence: it is an unmapped or custom tag, or a fact we
  failed to read. Examples: American Picture House (2026-06-30), Bioxytran (2020-06-30),
  Defense Technologies International (2022-01-31), PetroGas (2016-06-30), BioVie (2025-09-30).

The sample is small (about +/-12 points at 95% confidence), so read 18% as "a meaningful
minority, worth its own sweep", not as a measured rate. Both scripts are re-runnable with
`--sample` / `--seed` for a bigger one.

## What follows

1. **No Phase 3 classifier.** Doc 50 Phase 3 is closed as "premise did not generalize".
2. **`no_line_item_filed` over-claims for roughly one gap in five** on this sample. The
   owner of that classification (lane F, `sanity/period_completeness.py`) can either add the
   rendered-statement check used here as a second evidence source, or relabel the cause as
   "no matching XBRL fact" rather than "the filing reports no such line item".
3. The 33 confirmed cases suggest something worth a decision, not a code change: where a
   company has no investing activity, the honest value may be **$0** rather than "missing".
4. The interior-hole shape (51-80%) points back at derivation and mapping of quarterly
   cash flow (cash-flow statements are cumulative year-to-date in 10-Qs), not at
   applicability. That work belongs with the `quarter_not_derived` hand-off (lane C).
