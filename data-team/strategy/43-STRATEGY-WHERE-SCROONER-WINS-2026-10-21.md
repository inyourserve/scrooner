# 43. Strategy: where Scrooner wins, and what the data program is for (Ritwik, 2026-10-21)

This sits above docs 40-42. Those are the how; this is the why and the bet. Evidence labels: DATA-INFERRED / ASSUMED / VENDOR-CLAIM. Strategy, not a measurement.

## 1. The reframe
Doc 40-42 treat coverage as gaps to close. That is a maintenance mindset. The strategic question is: what is the asset that makes a serious US investor open Scrooner first and trust it, and that a competitor cannot copy by buying the same data?
- The raw data is public (SEC EDGAR, free, redistributable). It is not the moat. Competitors have it or can buy equivalents.
- Breadth of metrics is not the moat. Finviz (~70 filters), Koyfin and others already sell breadth; we cannot out-breadth them and doc 02 caps us at ~18 metrics on purpose (VENDOR-CLAIM sources in doc 37).
- What nobody I found offers is **a company page that is complete for its business model and provably checked**: every number linked to the filing it came from, certified, with the reason shown wherever a line does not apply. The moat is the **accumulated, verified standardization knowledge**: group templates, tag knowledge, composition definitions, invariants, a ledger of every filer quirk we have checked against an opened filing. That compounds with each filing season, and it is expensive for a vendor-fed competitor to replicate because it is judgment plus evidence, not a feed.

## 2. The bet
**Scrooner is the certified screener.** The unit of value is a certified company, not a metric cell. The promise users can test: pick any company in the cohort, every number on its page traces to the filing, and nothing is wrong or missing without a stated reason.
Why this bet, not another:
- It matches the north star (doc 01: the site a US investor opens first and trusts enough to return to).
- It is the one thing the free-forever data cost lets us afford at scale and a paid vendor cannot promise.
- It turns the correctness work (which is slow) into the brand rather than hiding it as cost.
- The customer's pain is real and documented: stale latest quarter, gaps in history, occasional wrong values on competing screeners (third-party reports; no independent accuracy study found, doc 37).

## 3. Design the system so gaps cannot accumulate (the structural idea)
Do not collect data and then count holes. Invert it:
1. **Product decides what a complete page is for each kind of business** (the group template): a bank, an insurer, a REIT, an industrial each have a defined set of cells. That is a product decision, owned here, and it bounds the engineering scope. Coverage becomes finite and checkable.
2. **Every new filing is checked against the template and the invariants the moment it arrives.** A company is certified or it is not; nothing is a quiet blank.
3. **Every fix is converted into a permanent rule** (tag card, template cell, invariant, ledger entry) so the same class of error is caught for all companies and future years. This is what makes the cost per company fall over time, and why moat work and coverage work are the same work.
4. **Trust is shown, not claimed**: certification state, "why this number", a public data-quality scorecard that includes our own error rate. Publishing it is the proof and the distribution hook.

## 4. What we will not do (the discipline that makes the bet credible)
- No more metrics, sources or vendors (estimates, technicals, sentiment) until the certified cohort exists. Breadth is the competitors' game.
- No number shown that the pipeline cannot certify. A reasoned absence beats a guess every time.
- No public "100%" claim for a cohort that is not fully certified.
- No parallel trackers or per-company hunting as the main loop once the invariant suite exists.

## 5. Sequence by strategic value, not by defect count
1. **Certify the companies users actually search first**: top 100, then top 1,000. They carry most traffic and most reputational risk, and they are where a wrong number hurts most.
2. **Make trust visible early**: certified badge and "why this number" ship as soon as the first cohort is real, even before the long tail. Visible trust is what turns correctness work into acquisition and retention (doc 24 SEO, doc 35 shareable content).
3. **Build the learning loop before the scale-up**: templates, tag knowledge, invariants and ledger must be cheap to extend, because the long tail of ~4,200 companies is won by reusing rules, not by hand work.
4. **Then widen**: the rest of the population, history to 2015, additional groups, only after the cohort metrics hold.

## 6. How we know the strategy is working (leading indicators, ASSUMED targets)
- Share of screener results and page views on certified companies (target high and rising).
- Wrong values found per 1,000 cells in independent sampling (target zero in released families).
- Cost to certify the next company (time and Verifier minutes) falling cohort over cohort. If it does not fall, the learning loop is not working and the strategy is just labor.
- User trust signals once real users exist: return rate, saved screens, support complaints about wrong numbers (none measured today; no analytics were reviewed).

## 7. Risks to the strategy itself
- A competitor with a large budget copies the badge. The defense is the accumulated verified rules and the evidence trail, not the badge.
- Certification becomes a cost center that never finishes. Defense: bounded cohorts, falling cost per company as a tracked metric, explicit stop rules (doc 42 section 6).
- The market does not pay for trust. Defense: test it early with real users on the certified top 100 before investing past it. This is a hypothesis, not a fact.
- Accounting judgment calls (what is revenue for a bank, are leases debt) are the real human bottleneck; the reviewer must be named.

## 8. Decisions this strategy asks of the founder
1. Confirm the bet: "the certified screener" as the primary positioning, with breadth deliberately second.
2. Name the accounting reviewer.
3. Agree that the first public proof is the certified top 100 with the visible scorecard, before any wider claim.
