# Accounting reviewer: team design, contractor brief and card order (Ritwik, 2026-10-24)

Written for: the founder (who books it) and Dhairya (who prepares the packets). Founder instruction (2026-10-24, relayed in my session): "create one account reviewer or team of account reviewer; book the accounting reviewer now." I cannot hire a person. What I can do, and did, is make the booking ready to send: who, what for, in what order, what they sign, what it costs, and what we prepare first. Evidence labels: DATA-INFERRED (our files), ASSUMED (my estimate or market knowledge, not verified).

## 1. The rule that decides the design
The plan's standing rule (doc 49, constitution, release policy): accounting definitions and perimeter changes are approved by a **named human accountant**; agents propose, they never approve. Today every accountant-gated cell is hidden with a reason, and a company certificate with pending cells cannot say 100%. The Standardization Lead has 38 decision cards: **21 need the accountant (AC-1..AC-21)**, plus growth cards AC-22..AC-26 and the ADS cards renumbered AC-27..AC-29+ (PLAN.md). 14 NA cards and 3 founder calls do not need him or her.
**Two ways to "create a reviewer", and what each does**
- **A. A human reviewer (or small team): the only option under the current rule.** Recommended.
- **B. An AI accounting preparer (an agent that drafts packets, checks fixtures, challenges options).** Useful, and I can create it on your word, but it can NOT sign. Making an AI the approver would loosen a locked rule (your decision, not mine; I recommend against, because the certificate's value is that a named accountable person stood behind each definition).
Do both: B reduces A's time and cost.

## 2. The team (smallest that works)
| Role | Needed for | Days (ASSUMED) | When |
|---|---|---|---|
| **R1 Lead reviewer: US CPA, SEC reporting / technical accounting** | all non-financial cards, i.e. company #1 and the pilot 10 | 2-3 for company #1; 2 more for the rest of the 21 | now |
| **R2 Financial-institutions specialist (banks, insurers, brokers)** | AC-10 bank revenue, AC-11 insurer revenue, AC-3 (FHLB advances etc.), financial parts of AC-1/AC-2/AC-15 | about 2 | before the first bank company |
| **R3 Real-estate/REIT specialist (optional; R1 can cover if qualified)** | AC-12 REIT capex, REIT parts of AC-1/AC-5/AC-6 | 0.5-1 | before the first REIT |
One reviewer is enough to START. R2 and R3 are booked only when a bank or REIT is next. All sign the same register.

## 3. Profile and conditions (the brief)
- **Must have:** US CPA in good standing (license state and number recorded); 8+ years in SEC financial reporting or technical accounting (Big-4 technical group, a public-company controller/technical accounting role, or a standards/analysis background); working knowledge of ASC 842 (leases), 606 (revenue), 230 (cash flows), 260 (EPS), 280 (segments), 470 (debt), 205-20 (discontinued ops), 250 (restatements/recasts), 810 (NCI). XBRL familiarity is a plus, not required.
- **Independence:** no employment with, and no position in, the companies covered in the engagement (the 1,000-company cohort list is public: `data/cohort_v1_1_proposal_2026-10-24.csv`); a conflict statement signed; no investment advice given or implied.
- **What they do:** for each decision card, choose an option (or write a better one), give the rationale with the authoritative citation (ASC paragraph, SEC rule or the filing itself), say what version and effective date it applies to, and sign. They approve DEFINITIONS and PERIMETERS, not individual values.
- **What they do not do:** touch the database, run code, or review thousands of values. They read one-page packets and filings.
- **Terms:** NDA; a named signature (name, credential, date) in the decision register; response to clarification questions within 2 business days; a written note of any card they decline or want escalated.
- **Cost (ASSUMED, not quoted):** US contract CPA / technical-accounting consultants commonly bill about $150-300 per hour; 2-3 days (16-24 h) = about $2.4-7.2k for R1 and the same order for R2. Set a cap and let them bill hours.

## 4. The card order
**Update 2026-10-24 (Dhairya, from the merged one-company plan): company #1 is MU or MSFT first, AAPL second.** My product half recommended AAPL first; the merged plan supersedes it. MU touches the lease perimeter, growth and restatement basis (as relayed by the founder); the Standardization Lead confirms the card subset for MU (and for MSFT) when next awake. The AAPL-oriented list below is the working assumption until then.
Use the Standardization Lead's order (his review): AC-1, 5, 6, 13, 14, 8, 10, 2, 9, 7, 15, 19, then the rest. For company #1 (a non-financial large-cap such as AAPL or MU) the sitting is this subset in that relative order (ASSUMED which cards touch it; the Standardization Lead confirms):
1. **AC-1** finance leases in debt, with the coupled interest, D&A and FCF choices (one answer must serve four metrics)
2. **AC-5** capex composition (capitalized software, finance-lease additions)
3. **AC-6** D&A for EBITDA
4. **AC-13** dividends: per-share basis, yield, payout
5. **AC-14** TTM EPS, trailing P/E and PEG basis
6. **AC-8** net income attribution (NCI, preferred)
7. **AC-2** debt composition beyond the carrying lines (short-term block, instrument sums)
8. **AC-15** interest expense composition and coverage
9. **AC-19** restatement basis for series, growth and TTM (also decides what Q4 backfill may show)
10. **AC-17** a line that is not presented: zero or not applicable in a ratio
11. **AC-16** ROIC and ROE details
12. **AC-20** continuing-operations basis for CFO and FCF
13. **AC-21** cash perimeter
14. **AC-22..AC-26** growth cards: multi-year endpoint restatement policy; 53-week treatment; DPS declared vs paid; shares-growth definition; growth across two losses
Not for company #1: AC-3 (special liabilities), AC-4 (zero borrowings), AC-7 (no operating-income line), AC-9 (revenue beyond the clean subset), AC-10/11/12 (bank, insurer, REIT), AC-18, AC-27+ (ADS). Estimated about 17 cards, about 30 minutes each plus fixtures: 2 to 3 days with buffer.

## 5. What we prepare BEFORE the first hour (our work, not theirs)
- One page per card: question, options with the consequence for users and cells (counts with their evidence labels), recommendation, what is blocked until answered. These exist in the Standardization Lead's review (`team/WO-REVIEW-standardization-lead.md` section 2) and the `DC-*` cards; they must be re-cut to one page each and checked for stale counts.
- **Fixtures:** 3-5 FILING-CHECKED filings per card so the reviewer judges real statements, not abstractions. The Standardization Lead says new fixtures are still needed for AC-11, 12, 13, 14, 17, 18, 19, 20, 21 (about 5 agent-days, ASSUMED). For company #1 fix the fixture set on its own filings.
- A decision register file (proposed `data-team/strategy/accountant/DECISION-REGISTER.md`): card id, question, option chosen, rationale and citation, scope and version, reviewer name, credential, date, supersedes. Under definition versioning every answer becomes a MAJOR/MINOR definition version; a changed answer later is a new version with a published diff, never an edit.
- A one-page glossary of our states and of which cells each answer unlocks, so every answer maps to cells that move from "Definition pending" to a value.
- The AI preparer (option B) can assemble and quality-check the packets in about 2-3 days; its draft definition is `ACCOUNTING-PREPARER-AGENT-DRAFT.md` (draft only; it can never sign; every packet keeps an empty 'HUMAN approver' line). No agent is created or woken by either file.

## 6. How to find and book (routes; no names invented)
- (i) A fractional or contract CPA through a vetted professional-services marketplace (examples: Toptal's finance network, Upwork's vetted CPA talent, Catalant; availability and rates are VENDOR CLAIMS, unverified).
- (ii) The technical-accounting or SEC-reporting group of a mid-size CPA firm on an hourly consulting contract.
- (iii) A former Big-4 technical accounting partner/manager now independent.
- (iv) A university accounting professor (financial reporting) as a paid independent consultant.
- (v) A referral from the founder's own network: fastest, and trust is already established.
**Screen:** a paid 30-minute test on real cards: AC-1 (finance leases / lease perimeter), AC-19 (restatement basis) and the NCI/preferred numerator cards AC-31 (SPAC redeemable common, the share card), AC-32 (preferred measurement: carrying vs liquidation, arrears), AC-33 (participating or convertible preferred) per Dhairya; card texts for AC-31..33 are in `team/DC-COMMON-EQUITY-BVPS-2026-10-22.md` (I read them there; they are PROPOSALS). The answer shows whether the candidate cites the standard and weighs the consequence for users.
**Booking path:** founder chooses the route and signs the engagement (budget cap, NDA, conflict statement); Dhairya sends the packets; first sitting 3-5 working days after the packets are ready (ASSUMED).

## 7. What the founder decides now, and the default
| Decision | Recommendation | Default if undecided |
|---|---|---|
| Book R1 (one human CPA, 2-3 days, cap about $7k) | yes, now | company #1 certificate lists about 17 cards as pending and cannot claim 100% |
| Which route (section 6) | (v) own network, else (i) with the screen | none; nothing is booked |
| Create the AI preparer (option B) | yes; it never signs | packets prepared by the Standardization Lead alone (slower) |
| Let an AI be the approver | no | stays human |
| Book R2 and R3 | only when a bank or REIT company is next | later |

## 8. Honest limits
I could not verify any market rate, platform availability or the exact number of cards that touch company #1 (the Standardization Lead's list rules). The card texts contain counts of different evidence quality (several DATA-INFERRED); the reviewer decides definitions, the counts only size the effect. The reviewer does not remove the need for the Verifier: a signed definition says what the cell MEANS, the Verifier says whether the value is right.
