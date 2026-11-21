# Structural resolver output format (for `scrooner-map structural-load`, rule company_tag_map.structural@1)

The output is ONE FILE PER COMPANY, `data-team/tags/line_map/resolver/<TICKER>.csv` (since 2026-11-21: run `tools/split_resolver.py <single csv>` after `resolve_all.py`; the single file `resolver-all110-<YYYY-MM-DD>.csv` is no longer committed, and every reader goes through `scrooner_pipeline.mapper.resolver_files`). Each is a UTF-8 CSV with a header and one row per company × data point × period, rows sorted by key. The period is one 10-K's own column. Family modules (`resolver-<family>-<date>.csv`) use the same columns, and the merge keeps one row per key.

**Key:** (cik, data_point, period_end, grain).

## Columns
| column | meaning |
|---|---|
| `cik` | 10-digit CIK of the filer (the company master links predecessor CIKs) |
| `ticker` | ticker from `data-team/tags/exam/ranks.csv` |
| `data_point` | template data point (canonical concept base name, e.g. `revenue`, `total_debt`, `weighted_basic_shares`) |
| `period_end` | the filing's own period end (FSN `period`, YYYY-MM-DD) |
| `grain` | `FY` for durations (qtrs 4), `I` for balance-sheet instants |
| `decision` | one of the decisions below |
| `nodes` | the structural evidence: each node is `Tag[=value] [R<report>.htm:<line> \| NOTE]`, joined by `; `, then ` \| why: <the role and tree path>` |
| `value` | decimal, filer units (USD; shares; USD per share). Empty for `combined`, `not_presented` and `no_role` |
| `accession` | the own-period 10-K the value is read from |
| `column` | `own` (this file); `comparative` is reserved for the latest-filed-copy pass |
| `calc_check` | the filer's own calc arithmetic on its own numbers in this filing (`calc <root>: ok\|FAIL;...`). A FAIL quarantines the filing |
| `flags` | rule source (`core`, `core_fallback`, `roles`, `total_debt`) plus rule flags (`hint_ranked`, `hint_only`, `DERIVED`, `READER CHECK ...`, `location by absence: CHECK`, `printed_zero`: a line printed on the own face with a dash or zero, served as 0 with its R:line; `comparative_fill`: the value comes from the next 10-K's comparative column (`column` = comparative, `accession` = that filing); `member_face_fact`: the face line's only own-period fact carries one member (equity-statement column or NonrelatedParty); `polarity_flip`: the value was normalised to the concept's sign from rules/polarity.csv; the node keeps the filer's raw value; `filing_read`: a reviewed full-10-K read (rules/filing_read_cells.csv, X109) confirms the cell, with `text_stated` when the read itself is served (quote + locator, nodes empty; a read that only rounds the resolver's figure coarser is an agreement, ruling c); `filing_read_hide;<class>`: the read's hide class with its quote) |
| `resolver_version` | version tag of the run (`resolver-YYYY-MM-DD.n`); the code is `tools/resolve.py` + `tools/resolve_all.py` + `tools/total_debt.py` + `rules/roles.csv` at the commit that adds the file |
| `quote` | `stated_zero` and `text_stated` rows only (empty otherwise): the EXACT sentence or table line of the filing that states the zero, copied verbatim (e.g. `We did not pay any dividends during fiscal 2022.`, `Long-term debt $ —`) |
| `locator` | `stated_zero` and `text_stated` rows only: the section or page of `accession` that holds the quote (e.g. `Item 5, Dividends`, `Note 9 Debt, p. 71`) |
| `quote_period` | `stated_zero` and `text_stated` rows only: the period end (YYYY-MM-DD) the quoted statement speaks for. Must equal `period_end`, or the row is rejected |

## Decisions
| decision | value | meaning |
|---|---|---|
| `mapped` | yes | one node holds the role |
| `component_sum` | yes | the role is the sum of the listed nodes (e.g. opex band, G&A + S&M, debt lines + located leases) |
| `derived_not_printed` | yes | not printed; computed only from nodes of the same filing and column (rulings C2, R5) |
| `combined` | no | the filing prints the item only inside a line that also holds other items |
| `not_presented` | no | the filing has no node of this role (on the face, or as an undimensioned note fact where note facts are allowed) |
| `not_in_template` | no | the data point is outside the company's template (e.g. a bank data point at a non-bank). Not served and not a gap (resolver .57) |
| `no_role` | no | the resolver found no node and has no reason yet. This is a rule gap, never a served reason |

## Sources and rules
- **`core`**: statement roles from the tree (`tools/resolve.py`). These are total assets, total liabilities, stockholders' equity, current assets and liabilities, revenue, cost of revenue, gross profit, operating expenses, operating income, pretax income, tax, net income, and the three cash-flow totals. Rulings S12/§AE, R1 (BKNG), R2, R3, R5, A, B and C2 are in the code.
- **`core_fallback`**: a role row from `rules/roles.csv` with `fallback=Y`. It is used only when the tree gives no node, i.e. filings without calc arcs.
- **`roles`**: every other data point, from `rules/roles.csv` with these columns:
  - `stmt` and `parent`: the position, a calc descendant of the parent node when the filer's tree has one;
  - `alternatives`: element families in rank order (`A+B` means a component sum);
  - `combined_if`: elements that mean the item sits inside a combined line;
  - `note_ok`: an undimensioned consolidated note fact is allowed (§AG);
  - `custom_label`: a custom line is accepted only when its own label names the role;
  - `ruling`: the decision behind the row.
- **`total_debt`**: `tools/total_debt.py`. Debt-role face nodes under liabilities, plus leases located outside debt. Pre-842 leases located by the instance's BalanceSheetLocationAxis come from `_lease-locations-pre842-*.csv`.


## Stated zero (ruling 2026-11-16, Dhairya; contract for the Tag Expert)
When the filing EXPLICITLY states a zero for the cell's period ("Long-term debt $ -", "did not have any outstanding debt", "did not pay any dividends"), emit one row:
- `decision` = `mapped`, `value` = `0`, `flags` includes `stated_zero`, `accession` = the own-period 10-K holding the statement;
- `nodes` empty (a stated zero has no tag to cite; if there is a printed line with a stored fact, it is a normal `mapped` row, and a dash line with no stored value is `printed_zero`);
- `quote`, `locator`, `quote_period` as defined above. All three are required.
Only an explicit statement counts, never an inference from silence or from the absence of a line. A row missing the quote, locator or accession, with a value other than 0, or with `quote_period` != `period_end` is REJECTED by `structural_loader` / `structural_direct` (nothing is served). Served as 0 with no fact id, `value_source` `stated_zero` (canonical_fact family `company_tag_map:stated_zero`), the quote and locator in the serve note. Coverage shows the cell (SHOWN_VALUE), r_page = the locator, evidence = the quote, column `stated_zero` = Y. Ritwik samples these cells in every certification.

## Text stated (Dhairya 2026-11-16: the same contract for a NONZERO value the filing states in its text)
When the filing STATES a number in running text that no XBRL fact or statement line carries (first cells: MCK R&D, "R&D expenses were $74 million, $96 million, and $71 million" in Item 1, p.13), emit one row:
- `decision` = `mapped`, `flags` includes `text_stated`, `value` = the stated number in filer units (USD, at the filing's scale: "$74 million" is `74000000`), `accession` = the own-period 10-K, `nodes` empty;
- `quote`, `locator`, `quote_period` exactly as for stated_zero. All required; `quote_period` must equal `period_end`.
- `value` must be NONZERO. A zero belongs under `stated_zero`; a `stated_zero` row must be 0.
A row failing any rule is rejected (nothing is served). Served with `value_source` `text_stated` (family `company_tag_map:text_stated`), no fact id, the quote and locator in the serve note. Coverage: SHOWN_VALUE, r_page = locator, evidence = quote, column `text_stated` = Y (a stated zero has `stated_zero` = Y), so Ritwik can sample both.


## Derived pairs served directly (Dhairya, revised ruling 2026-11-16; RULEBOOK X60, X67; serving: `structural_direct.derived_value`)
Two `derived_not_printed` rows are SERVED (every other derived row is counted, not served; gross profit and total liabilities go through `derived_cells`). Contract for the Tag Expert:
- `decision` = `derived_not_printed`, `value` = the derived number, `accession` = the own-period 10-K, `column` as for any row, `grain` `I` for shares and `FY` for comprehensive income.
- The flag is REQUIRED and selects the pair: `derived_issued_less_treasury` for `shares_outstanding` (shares issued minus treasury shares; emitted only when `DERIVE_SHARES=1`), `ci_parent_derived` for `comprehensive_income` (total comprehensive income including NCI minus the NCI portion).
- `nodes` carries EXACTLY two parts of the SAME filing and column, plus part first, minus part second with a leading `-`, each with its value and its printed page: `CommonStockSharesIssued=<v> [R3.htm:5]; -TreasuryStockShares=<v> [R3.htm:6] | why: ...` (tags: `CommonStockSharesIssued` minus `TreasuryStockShares` or `TreasuryStockCommonShares`; `ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest` minus `ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest`).
- The loader keeps the map's `not_presented` statement for the row (the value is never loaded). Direct serving reads each part from the stored facts of that accession and column only (never another filing or period), requires each to equal its node value and the difference to equal `value` (shares: issued > treasury >= 0), and REJECTS anything else (nothing is served).
- Served with `value_source` `derived_not_printed` (family `company_tag_map:derived_not_printed`), no fact id; the serve note carries the signed parts in the coverage export's parts format, `tag=value@accession#R<page>` joined by `;`, minus part prefixed `-`.
- A printed figure beats an own derivation (X67): where the filing or a later 10-K prints the figure, emit `mapped` instead.
- Open conflict (RULEBOOK X67): doc 02, founder decision 2026-11-01 item 4 ("EPS and instants are never derived"). The serving path ships dormant (no share rows exist while `DERIVE_SHARES` is off); switching the resolver on needs that line amended by the founder.
