# Structural resolver output format (for `scrooner-map structural-load`, rule company_tag_map.structural@1)

The file is `data-team/tags/line_map/resolver-all110-<YYYY-MM-DD>.csv`: UTF-8 CSV with a header and one row per company × data point × period. The period is one 10-K's own column. Family modules (`resolver-<family>-<date>.csv`) use the same columns, and the merge keeps one row per key.

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
| `flags` | rule source (`core`, `core_fallback`, `roles`, `total_debt`) plus rule flags (`hint_ranked`, `hint_only`, `DERIVED`, `READER CHECK ...`, `location by absence: CHECK`, `printed_zero`: a line printed on the own face with a dash or zero, served as 0 with its R:line; `comparative_fill`: the value comes from the next 10-K's comparative column (`column` = comparative, `accession` = that filing); `member_face_fact`: the face line's only own-period fact carries one member (equity-statement column or NonrelatedParty); `polarity_flip`: the value was normalised to the concept's sign from rules/polarity.csv; the node keeps the filer's raw value) |
| `resolver_version` | version tag of the run (`resolver-YYYY-MM-DD.n`); the code is `tools/resolve.py` + `tools/resolve_all.py` + `tools/total_debt.py` + `rules/roles.csv` at the commit that adds the file |
| `quote` | `stated_zero` rows only (empty otherwise): the EXACT sentence or table line of the filing that states the zero, copied verbatim (e.g. `We did not pay any dividends during fiscal 2022.`, `Long-term debt $ —`) |
| `locator` | `stated_zero` rows only: the section or page of `accession` that holds the quote (e.g. `Item 5, Dividends`, `Note 9 Debt, p. 71`) |
| `quote_period` | `stated_zero` rows only: the period end (YYYY-MM-DD) the quoted statement speaks for. Must equal `period_end`, or the row is rejected |

## Decisions
| decision | value | meaning |
|---|---|---|
| `mapped` | yes | one node holds the role |
| `component_sum` | yes | the role is the sum of the listed nodes (e.g. opex band, G&A + S&M, debt lines + located leases) |
| `derived_not_printed` | yes | not printed; computed only from nodes of the same filing and column (rulings C2, R5) |
| `combined` | no | the filing prints the item only inside a line that also holds other items |
| `not_presented` | no | the filing has no node of this role (on the face, or as an undimensioned note fact where note facts are allowed) |
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
