# Handover: FSN-expert session → SEC/FSN Tag Expert (knowledge owner)

**Date:** 2026-11-10.

**From:** the FSN-expert session (session_01GLmSDzg8V2n4juSyJdbko5), branch `docs/fsn-expert`.

**To:** the Tag Expert session (session_01GLmSDzfptGrTXZu6qg8aL3), which owns `data-team/tags/` (family cards, playbooks).

**Why:** the manager sync of 2026-11-10 says one tag-knowledge owner, not two. This session stops writing tag cards. Whether it keeps writing company dossiers is its user's call.

## What is on `docs/fsn-expert` (not merged to main)
| File | What it is | Suggested home |
|---|---|---|
| `data-team/fsn/FSN-GUIDE.md` | Every FSN file and column checked against SEC's spec and real rows. Five spec errors. Verdicts on the seven team beliefs | keep as is; reference doc |
| `data-team/fsn/companies/MSFT.md` | MSFT dossier: 52 filings, every face line per era, 9 recasts with reasons, store comparison | keep; the pattern for other companies |
| `data-team/fsn/PROPOSALS.md` | P-1…P-9 with evidence. P-1 is partly done in PR #4 (CSCO gap, eefbefc) | engineering backlog |
| `data-team/fsn/STATUS.md`, `journal/2026-11-02.md` | status and journal | — |
| `data-team/tags/cards/<Tag>.md` ×8 (per-tag) | CommercialPaper; EffectOfExchangeRate…IncludingDisposalGroupAndDiscontinuedOperations; SalesRevenueGoodsNet; the pretax pair; NetCashProvidedByUsedInOperatingActivitiesContinuingOperations; PaymentsToAcquirePropertyPlantAndEquipment; InterestExpenseNonoperating; FinanceLeaseLiability | **Tag Expert:** fold into your family cards (debt, cash-flow totals, revenue, operating-income, capex-and-da, interest), then drop the per-tag files. They are not on main |
| INDEX rows (8), company-quirks (3 MSFT rows), CHANGELOG entry | additions to your files | fold in or reject |
| `mind/inbox/20261102-2053*` (5) | captures | curator |

## Findings the Tag Expert should own (all with evidence in the files above)
1. **Face lines vs SEC spec.** FSN cal `negative` = ±1; DIM key `dimhash` with `0x00000000`; iprx is 0-based; `datp` is days (ddate − actual); dcml −32768 = nil; coreg is set only for a sole LegalEntity axis; pre.stmt can be `SI` or a mislabelled `UN`. Source: FSN-GUIDE §2–10.
2. **FX on the cash flow:** four or more sibling tags. CSCO's only FX line is the `…DisposalGroupIncludingDiscontinuedOperations` twin, while RTX uses it as a discontinued-operations component. Sum every FX line that is a calc child of the net change (PROPOSALS P-1).
3. **`CommercialPaper` printed as "Short-term debt"** (MSFT FY2024, FILING-CHECKED). Production MSFT total_debt FY2024 and FY2016 are wrong.
4. **`SalesRevenueGoodsNet` is a component** ("Product") under `SalesRevenueNet`. The pilot treats it as a second total.
5. **MSFT custom "Depreciation, amortization, and other"** is combined and was recast in FY2026 (FILING-CHECKED). Never map it as D&A.
6. **10-Ks before 2021 print Q4 three-month values**, EPS included. Printed beats derived.
7. **The pretax pair switch** (MSFT Q2 FY2022) and **CFO `…ContinuingOperations` as the sole CFO line** (60 top-100 names).
8. **Equity statement restated opening balance vs the BS print** (MSFT 2016-06-30: 83,090 vs 71,997): a vintage policy question (P-6).

## Not done
- HD, AAPL, JPM, TRV, PLD, NEE, XOM, JNJ, WMT dossiers.
- The bucket `fsn-notes` (59 periods, cohort extracts) is the right source, but this session has no Storage key.
