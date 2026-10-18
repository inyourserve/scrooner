# Wave 1 canonical concept definitions (PROPOSED, nothing approved)

Author: Standardization Lead (AI research role, 2026-10-18). Status: **proposal for independent Verifier review**; no agent may approve its own rule. Code: `pipeline/src/scrooner_pipeline/mapper/expanded_concepts.py` (`WAVE1_*` lists, gated by `WAVE1_SEED_ENABLED = False`). Tests: `pipeline/tests/unit/test_wave1_proposals.py`.

Evidence base: the Tag Mapper's 300-company convenience sample as summarized in `doc/data-moat/learnings/2026-10-17-coverage-rebuild-atomicity-q4-conflicts-and-nonadditive-derivation.md` sections 3-4. **Those percentages are sample counts, not population error rates, and the sample is not representative (low ids / every-17th-id).** I did not re-measure them, and I ran no database query for this document.

## 0. Two engineering facts that constrain how proposals are stored

1. `analytics.concept_mapping.confidence` is CHECK-constrained to `approved | provisional | rejected` (migration 0004). `candidate` cannot be stored. Proposals use `provisional`.
2. `mapper/resolve.py` loads every mapping whose confidence is `!= 'rejected'`, so a `provisional` row **is consumed** (canonical_fact rows get written, tag_library counts it provisional). "Provisional" is therefore NOT a safe parking state. The patch keeps the entries in separate `WAVE1_*` lists and merges them into the seeded `NEW_*` lists only when `WAVE1_SEED_ENABLED` is flipped in a reviewed commit. Default is off; the patch changes no runtime behavior.

Shared conventions for all concepts below: taxonomy `us-gaap`; `core.fact.is_authoritative = true` only; `Decimal` end to end; a missing value is null, never zero; the as-reported tag and fact stay preserved in `core.fact`; dimensional facts are not available in `core.fact` (Company Facts strips them, doc 22), so "no dimensions" is an assumption about the source, not something this pipeline can verify per fact. Effective range: all filings; taxonomy version: not pinned (us-gaap tag names are stable across 2011-2026 as far as inspected; unverified for deprecated-element transitions).

## 1. Concept contracts

### 1.1 `retained_earnings`
- Stable id: `retained_earnings`. Mapping: `RetainedEarningsAccumulatedDeficit` p1 (exact).
- Economic definition: cumulative undistributed consolidated earnings (positive) or accumulated deficit (negative) at the balance-sheet date.
- Statement/period: balance sheet, instant. Unit: currency (as reported). Consolidated, parent-company-shareholder equity section; no noncontrolling split.
- Sign: signed as reported; a deficit is negative. Never taken absolute.
- Perimeter: excludes APIC, AOCI, treasury stock, noncontrolling interests. Includes nothing from other equity lines.
- Relationships: **not_equivalent** to `stockholders_equity` (equal in 27 of 10,560 sample company-periods) and not a component to be netted for any approved identity. It is one component of equity.
- Precedence: single tag; no alternates.
- Allowed derivations: none. No back-solve from equity minus other lines.
- Applicability: all template types; REIT/bank/insurer filers report it but meaning varies (REIT distributions often drive it negative); mark comparability limited for REITs, not exclude.
- Downstream metrics: none today (candidate inputs: payout/retention analyses, accounting-identity equity decomposition). None wired.
- Unit policy (OPEN, human decision): sample shows CAD and EUR values. Proposal: keep value in reported currency, never convert, never compare or screen across currencies; screener use restricted to USD-reported rows until an approved currency policy exists.
- Adverse checks before promotion: parent vs consolidated (confirm no dimensional member leaks - not verifiable in core.fact, check ~10 filings' R-pages); cash vs expense N/A; as-filed vs restated (latest-filed resolver behavior for equity restatements); custom namespace collision (confirm only us-gaap namespace is mapped; company-extension tags with the same local name must not map); non-USD unit census (Q-A below).

### 1.2 `weighted_avg_shares_basic` / `weighted_avg_shares_diluted`
- Mappings: `WeightedAverageNumberOfSharesOutstandingBasic` p1; `WeightedAverageNumberOfDilutedSharesOutstanding` p1 (exact each).
- Economic definition: time-weighted average common shares outstanding over the reporting duration (diluted adds treasury-method dilution).
- Statement/period: income statement (EPS note), duration. Unit: shares.
- Sign: positive always; a non-positive stored value is an error.
- Perimeter: common shares of the registrant used in the EPS denominator; multi-class filers may report per-class values dimensionally (not visible here); the consolidated tag is used.
- Relationships: **not_equivalent** to point-in-time shares outstanding (`dei:EntityCommonStockSharesOutstanding`, balance-sheet shares); basic and diluted are separate concepts, never fallbacks for each other (diluted <= basic can fail under loss years - antidilution - so no ordering check is valid).
- Precedence: single tag each.
- Allowed derivations: Q4 and interim quarters only via `4*FY - (Q1+Q2+Q3)` and `Q_n = n*YTD_n - (n-1)*YTD_(n-1)`; commit `7825b47`, verified against earnings releases for five issuers only. Derived rows are an **approximation** (equal-length-quarter assumption; 52/53-week and large mid-year buybacks add error; median 0.024%, max 0.78% vs Yahoo in 44 cases) and must stay `is_derived = true` with lineage. The old `FY - sum(quarters)` formula must never be reapplied (guard `46399a6`).
- Open: whether derived rows may feed `weighted_avg_shares_*` at the concept layer or must be excluded (Tag Mapper note says "must exclude derived"). Proposal: reported rows only feed the concept by default; derived rows are exposed separately with a visible "derived, approximate" flag. Human/Verifier decision.
- Applicability: all templates with EPS. Not applicable for filers reporting no EPS (BDC/funds - null, not zero).
- Downstream: Market Cap fallback in `price_metrics.py::_load_latest_diluted_weighted_shares` (reads the raw tag today; any switch to the canonical concept is a separate reviewed change and must keep the `> 0` filter); future per-share metrics, dilution trend.
- Adverse checks: basic vs diluted tag swap in a single filing; point vs weighted (confirm no `EntityCommonStockSharesOutstanding` leakage - different tag, so test by value divergence); post-split restatement (as-filed shares before a split differ from restated; keep latest-filed rule); unit must be `shares` (not `USD`, `pure`); non-positive derived rows = 0 after recompute.

### 1.3 `operating_lease_rou_asset`
- Mapping: `OperatingLeaseRightOfUseAsset` p1 (exact).
- Economic definition: lessee's operating-lease right-of-use asset (ASC 842) at the balance-sheet date. Statement: balance sheet, instant. Unit: currency. Sign: positive.
- Perimeter: excludes finance-lease ROU assets (`FinanceLeaseRightOfUseAsset`, not mapped) and lessor assets. OPEN: finance-lease separation unreviewed; some filers report a combined "right-of-use assets" line that carries a different tag (combined, would need its own concept, not this one).
- Relationships: independent concept; not a component of `total_assets` mapped here.
- Precedence: single tag. Derivations: none. Applicability: filers after ASC 842 adoption (2019+); null before is expected and not a gap. Treat null in 2019+ as unresolved, not zero.
- Downstream: none yet (lease-adjusted leverage if later approved). Lease liabilities are NOT debt under any current metric; including them in `total_debt` needs an explicit separate approved policy.
- Adverse checks: current vs noncurrent N/A; combined ROU line (operating + finance) filed under this tag by some issuers - compare to liability scale; counterexample companies 1550, 1312, 683, 1108 reviewed against filings.

### 1.4 `operating_lease_liability_total`, `_current`, `_noncurrent`, and `operating_lease_liability_total_resolved`
- Mappings: `OperatingLeaseLiability` -> total p1; `OperatingLeaseLiabilityCurrent` -> current p1; `OperatingLeaseLiabilityNoncurrent` -> noncurrent p1. All exact, first_match, single tag each.
- Economic definition: present value of remaining operating-lease payments (ASC 842); total = current + noncurrent. Balance sheet, instant, currency, positive.
- Relationships: total = current + noncurrent (within 0.5% in 97.7% of 2,708 sample periods; counterexamples 1550, 1312, 683 - causes unknown, possibly lines mixing finance leases or the total tag in a footnote only).
- `operating_lease_liability_total_resolved`: derived layer; precedence (a) reported total if authoritative, else (b) current + noncurrent **only when both exist for the same company/period/filing basis**; never use one component alone as the total. It is a canonical_concept row with **zero** `concept_mapping` rows (same idiom as `total_debt_resolved`; resolve.py's delete scope must exclude it). The builder is to go in `mapper/concept_fallback.py` and is **not written**; a `sum`-mode mapping row is explicitly rejected because it would double-count whenever the total tag is also filed (the `total_debt` LongTermDebt lesson).
- Perimeter: operating leases only; finance-lease liabilities (`FinanceLeaseLiability*`) excluded and unmapped. Not debt by default.
- Applicability: ASC 842 filers (2019+); null earlier is expected.
- Downstream: none today; candidate lease-adjusted leverage, only after a debt-vs-lease policy is approved.
- Adverse checks: total vs component (above), current vs noncurrent mislabel, finance-lease contamination, sum-fallback equals total where both exist, no fallback ever fires when the total exists.

### 1.5 `interest_paid_cash`
- Mappings: `InterestPaidNet` p1, `InterestPaid` p2 (exact; alternates used only if p1 absent for that period).
- Economic definition: cash actually paid for interest during the duration (supplemental cash-flow disclosure). Cash-flow statement/notes, duration, currency, positive for payments.
- Perimeter: Net variant is net of capitalized interest per its definition and of amounts received depending on filer; the gross `InterestPaid` variant may differ in perimeter (capitalized interest). OPEN: whether first_match across the two is acceptable; coexistence agreement not measured.
- Relationships: **not_equivalent** to `interest_expense` (within 10% in only 2,064 of 4,854 sample pairs). **Hard rule: never a fallback or proxy for interest_expense, never used in interest coverage.**
- Derivations: none; no annualization from YTD (cash-flow statements are cumulative YTD - see Q4/interim caveat: YTD cumulative tagging breaks naive TTM, the known TTM CFO problem; deriving quarters needs the same `Q_n = YTD_n - YTD_(n-1)` care and is not authorized here).
- Applicability: all templates; zero is a valid reported value and must be preserved; missing is not zero.
- Downstream: none today (cash-interest coverage, if ever approved).
- Adverse checks: cash paid vs expense (above, must show NOT equal), Net vs gross divergence, cumulative-YTD vs discrete-quarter facts, financial-company presentation (banks report interest paid as operating-core; comparability limited).

### 1.6 `income_taxes_paid_cash`
- Mappings: `IncomeTaxesPaidNet` p1, `IncomeTaxesPaid` p2.
- Economic definition: cash paid for income taxes, net of refunds in the Net variant. Cash-flow statement/notes, duration, currency.
- Sign: signed as reported; net refunds exceeding payments are negative; do not take absolute.
- Relationships: **not_equivalent** to `income_tax_expense` (off by more than 2x in 2,288 of 6,173 sample pairs). Never a fallback for tax expense, never used for effective tax rate.
- Derivations: none (same YTD caveat as 1.5). Applicability: all; preserve zero. Perimeter question Net vs gross (refund inclusion) as for interest.
- Downstream: none today (cash tax rate if later approved).
- Adverse checks: cash vs expense, Net vs gross divergence, sign of net refunds, foreign vs federal-only tags (the other `IncomeTaxesPaid*` variants, e.g. foreign/federal, must stay unmapped).

## 2. Open decisions needing a human or the Verifier
1. Currency policy for non-USD retained earnings (and any other concept): USD-only screening vs conversion. Founder/accountant.
2. Whether derived (approximate) weighted-share rows may enter `weighted_avg_shares_*` or stay separate.
3. Finance-lease separation: confirm op-lease tags exclude finance leases; decide whether finance-lease concepts are needed; debt-vs-lease policy for `total_debt`.
4. Counterexample filings for companies 1550, 1312, 683, 1108 (leases): Verifier must read the original filings.
5. Net vs gross precedence for interest/taxes paid (first_match across perimeter variants).
6. Whether `provisional` rows (consumed by resolve) are acceptable at all pre-approval, or `WAVE1_SEED_ENABLED` stays off until approval (recommended: off).

## 3. FULL-POPULATION read-only coexistence queries for the Verifier

Run before any promotion, each as its own statement with `set statement_timeout = 0`, in a quiet window, in company-id chunks if it times out (parameters `:lo`, `:hi`; the full population is the union of chunks). All are SELECT only. `:tag` etc. are text parameters. "Same context" = same company, same period_id, same unit_id, authoritative.

**Q1 - Population and issuer coverage per tag (no sample):**
```sql
select c.tag, u.unit_name, count(distinct f.company_id) as issuers, count(*) as facts
from core.fact f join core.concept c on c.id = f.concept_id
join core.unit u on u.id = f.unit_id
where c.taxonomy = 'us-gaap' and c.tag = any(:tags) and f.is_authoritative
  and f.company_id between :lo and :hi
group by 1, 2 order by 1, 3 desc;
```
`:tags` = the 11 mapped tags. Pass: every tag reported with its unit census; share counts have only `shares`, money tags only currency units. Any unit outside that set is listed and a rule (exclude/convert) decided before promotion. This also answers the non-USD retained-earnings question (units other than `USD`).

**Q2 - Coexistence of primary vs alternate (interest/taxes paid):**
```sql
select count(*) as pairs,
       count(*) filter (where abs(a.value - b.value) <= 0.01 * greatest(abs(a.value), abs(b.value))) as agree_1pct,
       count(*) filter (where a.value is distinct from b.value) as differ
from core.fact a join core.concept ca on ca.id = a.concept_id
join core.fact b on b.company_id = a.company_id and b.period_id = a.period_id and b.unit_id = a.unit_id
join core.concept cb on cb.id = b.concept_id
where ca.tag = :primary and cb.tag = :alternate and a.is_authoritative and b.is_authoritative
  and a.company_id between :lo and :hi;
```
Run for (InterestPaidNet, InterestPaid) and (IncomeTaxesPaidNet, IncomeTaxesPaid). Pass: >= 95% of pairs agree within 1% AND the disagreeing pairs are listed (issuer counts) and reviewed on at least 10 original filings; otherwise the alternate is dropped or split into its own concept. Coexistence is not equivalence; this is a necessary, not sufficient, condition.

**Q3 - Not-equivalent proofs (cash vs expense, equity):** must show the hard rules are visible in the data, so no code may alias them.
```sql
select count(*) as pairs,
       count(*) filter (where abs(p.value - e.value) <= 0.10 * nullif(abs(e.value),0)) as within_10pct
from core.fact p join core.concept cp on cp.id = p.concept_id
join core.fact e on e.company_id = p.company_id and e.period_id = p.period_id and e.unit_id = p.unit_id
join core.concept ce on ce.id = e.concept_id
where cp.tag = :paid_tag and ce.tag = :expense_tag and p.is_authoritative and e.is_authoritative
  and p.company_id between :lo and :hi;
```
Pairs: (InterestPaidNet, InterestExpense), (IncomeTaxesPaidNet, IncomeTaxExpenseBenefit), (RetainedEarningsAccumulatedDeficit, StockholdersEquity). Pass (for rejecting equivalence): within-10% share clearly below 100% (expected ~43% interest, far lower taxes, ~0.3% equity) so the not_equivalent classification stands; report the population number replacing the sample figures.

**Q4 - Lease total vs components and counterexamples:**
```sql
select t.company_id, p.fiscal_year, p.fiscal_period,
       t.value as total, (cu.value + nc.value) as parts,
       (cu.value + nc.value) - t.value as diff
from core.fact t join core.concept ct on ct.id = t.concept_id and ct.tag = 'OperatingLeaseLiability'
join core.fact cu on cu.company_id = t.company_id and cu.period_id = t.period_id and cu.unit_id = t.unit_id
join core.concept ccu on ccu.id = cu.concept_id and ccu.tag = 'OperatingLeaseLiabilityCurrent'
join core.fact nc on nc.company_id = t.company_id and nc.period_id = t.period_id and nc.unit_id = t.unit_id
join core.concept cnc on cnc.id = nc.concept_id and cnc.tag = 'OperatingLeaseLiabilityNoncurrent'
join core.period p on p.id = t.period_id
where t.is_authoritative and cu.is_authoritative and nc.is_authoritative
  and t.company_id between :lo and :hi
  and abs((cu.value + nc.value) - t.value) > 0.005 * nullif(abs(t.value),0);
```
Pass: the full set of violators is enumerated (not a sample), grouped by company, every violating company with >= 3 periods reviewed against filings (incl. 1550, 1312, 683, 1108); a documented cause for each class (finance leases, rounding, tag misuse) and a rule excluding that class from `_resolved`, or the sum fallback is not enabled. Companion: count of (company, period) with components but no total (the population the fallback would fill) and with total but no components.

**Q5 - Non-positive share counts (reported and derived):**
```sql
select c.tag, f.is_derived, count(*) as rows_total,
       count(*) filter (where f.value <= 0) as non_positive
from core.fact f join core.concept c on c.id = f.concept_id
where c.tag in ('WeightedAverageNumberOfSharesOutstandingBasic','WeightedAverageNumberOfDilutedSharesOutstanding')
  and f.is_authoritative and f.company_id between :lo and :hi
group by 1, 2;
```
Pass: non_positive = 0 for both derived and reported after the pending population re-derive; any nonzero value blocks promotion and is listed per company.

**Q6 - Basic vs diluted plausibility and swap detection:**
```sql
select count(*) as pairs,
       count(*) filter (where d.value > 1.5 * b.value) as diluted_gt_1_5x_basic,
       count(*) filter (where d.value < 0.5 * b.value) as diluted_lt_half_basic
from core.fact b join core.concept cb on cb.id = b.concept_id and cb.tag = 'WeightedAverageNumberOfSharesOutstandingBasic'
join core.fact d on d.company_id = b.company_id and d.period_id = b.period_id and d.unit_id = b.unit_id
join core.concept cd on cd.id = d.concept_id and cd.tag = 'WeightedAverageNumberOfDilutedSharesOutstanding'
where b.is_authoritative and d.is_authoritative and not b.is_derived and not d.is_derived
  and b.company_id between :lo and :hi;
```
Pass: both outlier counts near zero; every outlier company reviewed (class-share and tag-swap issuers expected); explained or excluded.

**Q7 - Custom-namespace / mapped-namespace collision:**
```sql
select c.taxonomy, c.tag, count(distinct f.company_id) as issuers
from core.concept c left join core.fact f on f.concept_id = c.id and f.is_authoritative
where c.tag = any(:tags) and c.taxonomy <> 'us-gaap'
group by 1, 2 order by 3 desc;
```
Pass: no non-us-gaap row shares a mapped local name (mappings are namespace-qualified; this proves no accidental conflation and lists extension tags that look alike for review).

**Q8 - Sign and magnitude sanity (retained earnings, taxes paid):**
```sql
select c.tag, count(*) as n,
       count(*) filter (where f.value < 0) as negative,
       percentile_cont(0.5) within group (order by abs(f.value)) as median_abs
from core.fact f join core.concept c on c.id = f.concept_id join core.unit u on u.id = f.unit_id
where c.tag in ('RetainedEarningsAccumulatedDeficit','IncomeTaxesPaidNet','IncomeTaxesPaid','InterestPaidNet','InterestPaid')
  and u.unit_name = 'USD' and f.is_authoritative and f.company_id between :lo and :hi
group by 1;
```
Pass: negatives for retained earnings are plausible (deficit filers) and negatives for interest paid are near zero and explained; no scale outliers (value > 1e13) left unreviewed - apply the EntityPublicFloat scaling-bug lesson.

**Q9 - Already-mapped / double-mapping check in the live database (not just code):**
```sql
select c.tag, cc.name, m.confidence, m.priority
from analytics.concept_mapping m join core.concept c on c.id = m.concept_id
join analytics.canonical_concept cc on cc.id = m.canonical_concept_id
where c.taxonomy = 'us-gaap' and c.tag = any(:tags) order by 1;
```
Pass: returns no row before seeding (and exactly the proposed rows after), so no tag maps to two canonical concepts.

## 4. What this document does not establish
- No population-level claim; all quoted percentages are Tag Mapper sample numbers I did not re-measure.
- Dimensional/segment eligibility (`core.fact` carries none), per-filing statement-line placement, finance-lease separation, and issuer-specific exceptions were not inspected against original filings.
- Approval: none requested or implied. Verification by the Verifier plus human policy approval are required; promotion path is new -> evidence_ready -> proposed -> independently_verified -> policy_eligible.
