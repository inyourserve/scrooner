# Open sources for coverage: what each closes in our residue (Tag Expert, 2026-10-24)

Test set: the 5,625 residue cells (PLAN.md "Root fix #3 built"), counted per company without `_resolved` twins. Face test: FSDS 2025q4 (986 cohort filings). Notes test: FSN 2025_11. 15 R-files opened, all agreed with FSDS. Labels: FILING-CHECKED (R-file opened), DOC-CHECKED (official file read), DATA-INFERRED (our tables).

## Ranked by coverage gained / effort

| # | Source (licence) | Download | What it gives | Residue it closes |
|---|---|---|---|---|
| 1 | FASB us-gaap schemas + calc + dep arcs, 2015-2026 (FAF authorized use; internal reference OK) | 7.4 MB zip per year; about 5 MB per year actually needed | Elements per year, definitions, calc tree, deprecation replacements | **Era gap, new:** `InterestExpenseNonoperating` exists only from the 2024 schema and `interest_expense` does not map it. CL and AVY stop at FY2023 / Q1 2024 (FILING-CHECKED); 1,542 companies have recent IEN and no recent mapped interest tag (DATA-INFERRED). Calc tree classifies 527 residue cells as combined or broader lines (below) |
| 2 | SEC FSDS quarterly (public; bulk download intended) | 60-85 MB zip per quarter; cohort is about 16% of rows (642k num rows, 92 MB text per quarter); 2015-2026 about 3 GB, streamed | Face lines with label and position (`pre`); face values incl. custom tags and **dimensional facts**, which companyfacts strips | Gives face evidence (present / combined / not shown) for every residue family; finds member-only lines (AES debt by recourse, TXT by group, ERIE DPS by class) |
| 3 | SEC FSN monthly, `cal.tsv` (same) | 41-314 MB zip per month (2025_11: 292 MB, 2.0 GB unpacked); read cal + sub only | The filer's own calculation tree | Perimeter per company: ODFL puts interest inside NonoperatingIncomeExpense; OXY and CVX put it inside cost totals. Note facts added almost nothing: interest 4, debt 1, D&A 0, DPS 0 companies |
| 4 | SEC companyfacts / Frames (public) | companyfacts.zip 1.41 GB per day (one file instead of about 1,000 calls); Frames is small JSON | Values for cross-checks | 0 residue; no dimensions or custom tags |
| 5 | edgartools `gaap_mappings.json` (MIT) | 1.2 MB | Tag usage counts | Candidates only: 3 of 12 tested mappings agree (IEN yes; AP-plus-accrued, accretion D&A, collaboration revenue no) |
| 6 | DQC rules (copy allowed with notice; rule text may not be modified) | under 1 MB in the taxonomy | Sign checks (DQC_0015) | 0 coverage; a guard |
| 7 | EDGAR full-text search + 8-K Ex. 99.1 | 100-500 KB per release; about 11k releases for top-1000 since 2015 | Q4 and DPS as furnished | Q4 cross-check only; furnished, not filed, so display is a founder decision. Apple 0000320193-25-000077 found |
| x | XBRL US API (members only), python-xbrl (regex matching), OpenBB (licence unclear) | | | Excluded |

Essence-alias and general-special: the 2026 taxonomy has 22 essence-alias arcs, all on deprecated items, and 0 general-special arcs (DOC-CHECKED). They are not a tag-equivalence source. Use the calc tree, meta-model arcs (class-subclass 1,573; dimensional-equivalent 301) and deprecation arcs (e.g. EarningsPerShareBasicAndDiluted -> EarningsPerShareBasic + EarningsPerShareDiluted, removed by 2026).

## Residue families: can an open resource explain or fill them?

| Family (residue companies) | FSDS face result | Verdict |
|---|---|---|
| collaborative_arrangement_revenue (708) | 647 have no face line; 30 have collaboration member facts only | **Explains:** applicability. Only 26 companies ever file the tag |
| cf_ap_change (358) | 244 file `IncreaseDecreaseInAccountsPayableAndAccruedLiabilities`, which the FASB calc makes the parent of AP | **Explains** as combined; never fill. LNG R6 |
| cf_ar_change (329) | 174 file a broader receivables line; 16 insurers file premiums receivable | **Explains**; fills only with an approved wider perimeter. XEL R4 |
| other_income_expense_net (275) | 185 file `OtherNonoperatingIncomeExpense`, a calc child of NonoperatingIncomeExpense | **Fills if** the concept is defined as the presented "other" line. SWKS R3, ROL R4 |
| amortization_of_intangibles (149) | 109 show only a D&A total | **Explains** as combined |
| dividends_paid (149) / DPS (163) | 11 `PaymentsOfOrdinaryDividends` (fill, PFE R8); 30 NCI/preferred only; about 96-99 no line in face or notes | Fill 11; the rest supports evidenced-zero (AMD, RDDT, ISRG). TSN, ERIE, SBAC, RKT, VNOM: DPS by class only, needs a class rule |
| interest_expense (128) | 21 IEN, 14 InterestAndDebtExpense, 34 net-only lines | Fill 21 (+14 with a perimeter flag); 34 explained. The bigger win is the IEN era gap above |
| D&A (126) | 66 show separate depreciation and amortization lines; 29 `DepreciationAmortizationAndAccretionNet` (banks/insurers) | Fill 66 by calc composition (NUE R6: 910 + 191); 29 with an accretion flag (JPM R8) |
| total_debt (79) | 54 no face debt line; member-only at AES, TXT | Explains most; sum one axis's members only after a face check |

## How it plugs into the hybrid design
- Values stay from companyfacts. FSDS `pre` + FSN `cal` feed the per-company mapper (which tag sits on which face row; what the filer put inside each total). FASB calc and deprecation arcs supply the candidate family and era.
- **Format-change gate:** re-map a company when its face tag set changes between consecutive filings, or when its taxonomy version moves. The IEN switch is exactly this case: it is keyed by filing vintage, and comparatives carry the new tag back to 2020-21.
- **Lower storage:** a face-only cohort store is about 16% of each FSDS quarter and holds the dimensional and custom face facts we lack. Notes add about 1.6 GB unpacked per month for almost no residue gain.

## Next actions
1. Tag Mapper: coexistence check for IEN under `interest_expense`, with a flag for ", net" labels (inbox 2026-10-24).
2. Data Engineer: yearly schema diff plus a quarterly FSDS face-presence pass.
3. Standardization Lead: rule on the AR and other-income perimeters, and the collaboration-revenue template.
