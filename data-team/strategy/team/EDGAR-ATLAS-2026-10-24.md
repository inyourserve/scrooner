# EDGAR atlas (Head of Data Product, 2026-10-24)

Builds on docs 07, 36, 22, 23, 31, 32b, data-team/23, `tags/sources.md` and the as-filed pilot; repeats them only to correct them.
Labels: **FC** FILING-CHECKED (opened on sec.gov today, about 40 requests, 4 req/s, shared limiter, files deleted); **DC** DOC-CHECKED (SEC document or repo doc read); **DI** DATA-INFERRED (read-only DB query today, one connection, 20 s, 9-10 backends); **AS** ASSUMED.

## Corrections to what we wrote before
| # | Earlier claim | What is true | Label |
|---|---|---|---|
| 1 | Doc 36: 13D/13G "has never had a structured XML primary document"; module reads `SC 13D/G` | Since 2024-12-18 these are filed as form types `SCHEDULE 13G`/`13D` with `primary_doc.xml`, including `classPercent` and share counts (MU 0002100119-26-000795: Vanguard 7.47%, 84,297,629 sh). `beneficial_ownership.py` FORMS = SC only, so rows fell from 1,452-12,818 per quarter (2024) to 2-19 per quarter (2025-26). This also starves the CUSIP crosswalk that 13F and N-PORT use | FC + DI |
| 2 | Docs 22/31: FSDS is "genuinely redundant"; FSN is "out of scope" | The pilot showed FSDS adds custom tags and presentation. FSN adds notes, dimensions, text facts and each filer's calc tree | FC (pilot) + DC |
| 3 | Pilot: "no start date, ddate month-rounded, no calc linkbase" | True for FSDS only. FSN NUM carries `datp`/`durp` (offset from the rounded date and duration) and `dcml`; FSN CAL has the calc arcs | DC (aqfsn_1.pdf) |
| 4 | Doc 07: companyfacts = "all structured data" | Only standard, undimensioned, numeric facts. MU FY2026 10-K: instance 1,421 facts (682 dimensional, 137 undimensioned text, 77 custom); we hold 519 fact rows. Only 5 dei tags are in `core.concept`, so AuditorName, ErrorCorrectionFlag, cyd and ecd text never reach us | FC + DI |
| 5 | Doc 36: Forms 3/5 not used, Form 4 per filing | SEC publishes all Forms 3/4/5 as one quarterly bulk set: 2026q3 is 8.7 MB with 38,153 submissions, 59,886 transactions and an `AFF10B5ONE` column | FC |
| 6 | Financial_Report.xlsx (in tools and lore) | 404 for MU FY2025, MU FY2026 and AAPL FY2025; present for AAPL FY2019. No longer generated | FC |

## A. Filing package anatomy: MU FY2026 10-K, 0000723125-26-000023 (filed 2026-10-09, 124 files)
| Part | Real example | Good for |
|---|---|---|
| Main iXBRL doc | `mu-20260903.htm` 2.06 MB | Item text (1, 1A, 1C, 7, 7A, 9A), the cover page, tagged facts in place |
| Exhibits | Ex-10.x awards; **Ex-19.1 insider-trading policy** (new, S-K 408(b)); Ex-21.1 subsidiaries; Ex-23.1 consent; Ex-31/32 certifications. No Ex-13 here (filers that incorporate the annual report use it, AS) | Governance flags, subsidiary list, auditor |
| Ex-101 set | `.xsd` 65 KB (32 custom keys); `_cal` 108 KB; `_def` 372 KB (axes/domains); `_lab` 930 KB; `_pre` 637 KB | Which tags sum to which total (cal), statement order (pre), segment structure (def) |
| Instance | `mu-20260903_htm.xml` 1.72 MB: us-gaap 1,278, custom 77, dei 38, cyd 15, ecd 11, srt 2 facts; 35 axes, 295 contexts | Everything tagged, including segments, geography, 10b5-1 arrangements |
| FilingSummary.xml | 50 KB, 86 reports with MenuCategory and role URI | Cheap statement-set fingerprint |
| R1-R86.htm | R3 IS, R4 BS, R7 CF, R26 segments, R58 debt maturities, R73 ASU 2023-09 tax reconciliation | Verifier locators |
| MetaLinks.json | 1.35 MB: per tag, the roles where it appears, its labels and definition; per report, first anchor with decimals | The cheapest single-file face/notes fingerprint |
| index.json, -index-headers | file list and sizes; SGML header | Discovery |
| Full .txt / -xbrl.zip | 25.5 MB (base64 images) / 4.55 MB | Single-request archive; zip only if needed |
| 8-K Ex-99.1 (0000723125-26-000018, 9 days before the 10-K) | Q4 revenue 54,229M, **Q4 diluted EPS 32.87** (the 10-K tags only the FY figure, 74.33), FQ1-27 guidance $61.5B ± $1.5B; the 8-K's own XBRL is cover-only (2.9 KB) | The only filed source of discrete Q4 per-share; company guidance |

## B. EDGAR surfaces
| Surface | What only it gives | Coverage / lag / size | Today |
|---|---|---|---|
| Submissions API / zip | items, acceptance time, isXBRL, size, primary doc, category, ein, lei, former names | MU: 1,004 recent + overflow file to 1994; zip 1.57 GB nightly (FC) | Used |
| companyfacts API / zip | Values for standard tags across all filings, incl. 8-K, 10-K/A, DEF 14A ecd | Under a minute (API); zip 1.41 GB nightly (FC) | Core feed |
| companyconcept / Frames | One tag / one period across all entities | Frames = latest-filed; entity counts are lower bounds (ledger row 98) | Checks only |
| FSDS | Face-statement pre/num/tag, custom tags | Quarterly, 2026q3 65 MB published 2026-10-07 (FC) | Pilot |
| **FSN** | + notes, DIM, TXT (all non-numeric facts), REN, CAL, exact-date offsets | Monthly: 2026_08 313 MB, 2026_09 56 MB (published 2026-10-07); quarterly after one year (2024q3 439 MB) (FC) | Not used |
| Daily / full index | What was filed | Daily | Used |
| XBRL RSS (`usgaap.rss.xml`, monthly `xbrlrss-YYYY-MM.xml`) | Each XBRL filing with its EX-101 file list, SIC, FYE | 200 latest items, rolling (FC) | Not used: gate trigger |
| EFTS full-text search | Phrase search, 2001+ | 10-Ks 2026 with "substantial doubt"+"going concern": 1,655; 8-Ks with "non-reliance": 1,423 (FC); undocumented API (AS) | Not used |
| Insider Transactions Data Sets | All Forms 3/4/5 incl. footnotes | Quarterly, 8.7 MB (FC) | Not used |
| 13F / N-PORT sets | Holdings | 13F about 100 MB per 3-month window (FC) | Used (one window) |
| Fails-to-deliver | Settlement fails (not short interest) | Twice monthly, about 1.5 MB (FC) | Not used |
| EDGAR-CORPUS ([HF](https://huggingface.co/datasets/eloukas/edgar-corpus), DC) | 10-K items split | 1993-2020 only | No |

## C. By form: what a screener can use
| Form | Reports that matter | Today |
|---|---|---|
| 10-K | Items 1 (segments, employees), 1A, **1C cyber (cyd-tagged)**, 5 (buybacks), 7, 7A, 8, **9A (ICFR, material weakness: text)**, 9B/**408 10b5-1 arrangements (ecd-tagged)**; cover dei: AuditorName, PCAOB ID, IcfrAuditorAttestationFlag, **DocumentFinStmtErrorCorrectionFlag**, public float | Item 8 numeric only |
| 10-Q | Interim statements, YTD cash flow, Part II 1A and 2 (buybacks) | Numeric |
| 8-K | 2.02 earnings (Ex-99.1: Q4, guidance), 1.01/1.02 agreements, 1.03 bankruptcy, 1.05 cyber incident, 2.01 deals, 2.03 new debt, 2.05/2.06 restructuring and impairment, 3.01 delisting notice, 3.02 unregistered sales (dilution), 4.01 auditor change, **4.02 non-reliance**, 5.01 control change, 5.02 departures, 5.03 bylaws/FYE, 5.07 votes. Since 2025: 4.02 = 196 filings at 164 companies, 4.01 = 1,043 at 843, 3.01 = 842 companies, 1.03 = 20 (DI) | Items shown as labels only, no flags |
| 10-K/A, 10-Q/A | Restated statements, or Part III only | Supersede logic |
| NT 10-K/10-Q, 25, 15 | Lateness, delisting, deregistration | 15 only; NT and 25 not in `core.filing` (DI) |
| DEF 14A | Pay vs performance (ecd numeric, in companyfacts: PeoTotalCompAmt 1,226 companies, TSR 1,773, DI), ownership table, board (text) | Existence only |
| S-1/424B/FWP | Offering size, dilution | 424B5/FWP rows only |
| SCHEDULE 13D/13G | Holder, % of class, shares (XML since 2024-12) | **Broken since 2025** (row 1) |
| 3/4/5, 144 | Insider trades, planned sales | Form 4, 12 months; 144: 49,062 rows, not parsed (DI) |
| 13F, N-PORT | Holdings | One window |

## D. Derivations we do not store or compute
| Item | Source | Method | Difficulty | Investor value | Label |
|---|---|---|---|---|---|
| Restatement flag | 8-K 4.02 items; 10-K ErrorCorrectionFlag; 10-K/A | Item code (zero fetch) + FSN TXT flag | Low | High (trust) | DI/DC |
| Auditor and auditor change | 8-K 4.01; dei AuditorName and PCAOB ID | Item code + FSN TXT | Low | Medium-high | DI/FC |
| Going concern | 10-K text, auditor's report | EFTS phrase or FSN TXT, plus Verifier sample | Medium | High for small caps | FC (hits) |
| Material weakness | Item 9A text | Phrase flag, Verifier sample | Medium | High | AS |
| Segment and geography revenue | Instance dims / FSN DIM (MU: 4 segments sum to 133,188M; country:US 91,323M) | Axis+member sum-to-total check | Medium | High | FC |
| Q4 discrete EPS and revenue | 8-K Ex-99.1 tables | Parse the furnished table, tie to FY minus 9M | Medium | High (I11 Q4 gaps) | FC |
| Company guidance | Ex-99.1 outlook table | Parse; label "company guidance, not GAAP" | Medium | High, but a policy question | FC |
| Note schedules already in `core.fact`, unmapped or candidate | Debt maturities (2,461 companies), operating-lease payments (3,938), cash taxes paid (3,748), RPO/backlog (1,032), remaining buyback authorization (1,135) | Map tags, sum-check against totals | Low | High (debt wall) to medium | DI |
| CEO pay vs TSR | ecd PvP facts already in `core.fact` | Map, ratio | Low | Medium (alignment) | DI |
| Exec 10b5-1 plan adoptions | 10-K/10-Q ecd TrdArr* (MU: DeBoer, 85,632 sh) | FSN TXT/instance | Low | Medium | FC |
| % held by 5% holders | SCHEDULE 13D/G XML | Parse classPercent | Low | High | FC |
| Full insider history incl. Forms 3/5 | Insider data sets | Bulk load | Low | High | FC |
| Cover share count by class | dei by class axis | Instance or FSN | Low | High (market cap) | DC |
| Subsequent events | SubsequentEvent axis (MU: 4 facts) + text | Dims + text | Medium | Medium | FC |
| Late filer / delisting | NT 10-K, Form 25, 8-K 3.01 | Form type (allowlist) | Very low | High (risk) | DI |

## Could not verify
FSN zip contents (field guide only, no zip pulled) and whether TXT holds every dei flag; when Financial_Report.xlsx stopped; EFTS lag; our nightly route (API vs zip); Ex-13 counts; why a few 13D/G rows still arrive in 2025-26 (legacy-form amendments, AS).
