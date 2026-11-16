# US-GAAP taxonomy and DQC rule tables (for the line-map resolver)

Built 2026-11-15/16 from official sources only. Every value was parsed out of the XML/HTML with
Python `xml.etree` / regex; nothing was hand-entered. Builders (not in the repo):
`scratchpad/tx_scripts/build_taxonomy.py` and `scratchpad/tx_scripts/build_dqc.py`
(run with `python3 -I <script> <taxonomy_dl> <taxonomy>`).

## Sources (downloaded 2026-11-15 UTC)

| Year | URL | bytes |
|---|---|---|
| 2014 | https://xbrl.fasb.org/us-gaap/2014/us-gaap-2014-01-31.zip | 5,582,583 |
| 2015 | https://xbrl.fasb.org/us-gaap/2015/us-gaap-2015-01-31.zip | 5,803,950 |
| 2016 | https://xbrl.fasb.org/us-gaap/2016/us-gaap-2016-01-31.zip | 5,400,556 |
| 2017 | https://xbrl.fasb.org/us-gaap/2017/us-gaap-2017-01-31.zip | 5,509,516 |
| 2018 | https://xbrl.fasb.org/us-gaap/2018/us-gaap-2018-01-31.zip | 5,554,418 |
| 2019 | https://xbrl.fasb.org/us-gaap/2019/us-gaap-2019-01-31.zip | 5,728,252 |
| 2020 | https://xbrl.fasb.org/us-gaap/2020/us-gaap-2020-01-31.zip | 6,345,468 |
| 2021 | https://xbrl.fasb.org/us-gaap/2021/us-gaap-2021-01-31.zip | 6,526,936 |
| 2022 | https://xbrl.fasb.org/us-gaap/2022/us-gaap-2022.zip | 6,485,888 |
| 2023 | https://xbrl.fasb.org/us-gaap/2023/us-gaap-2023.zip | 6,607,657 |
| 2024 | https://xbrl.fasb.org/us-gaap/2024/us-gaap-2024.zip | 7,115,653 |
| 2025 | https://xbrl.fasb.org/us-gaap/2025/us-gaap-2025.zip | 7,101,405 |
| 2026 | https://xbrl.fasb.org/us-gaap/2026/us-gaap-2026.zip | 7,387,980 |

All 13 years 2014-2026 were obtained.

DQC:
- FASB taxonomy `dqcrules/` folder (2020-2026 releases): the official DQC element lists, shipped
  inside the US-GAAP taxonomy ((c) XBRL US). 2020 uses separate `-def`/`-ref` XML files and the
  arcrole `concept-rule`; 2021+ embed the linkbases in `dqcrules-NNNN-<ver>.xsd` with `rule-concept`.
  The two are normalised to `rule-concept`.
- https://xbrl.us/data-rule/ index page (https://xbrl.us/data-quality/rules-guidance/ redirects to
  https://xbrl.us/home/priorities/data-quality/rules-guidance/): 202 approved rules with title,
  description, approved/effective dates, applies-to and "last updated as part of vX" version.
  The page states current approved plugin version 31.0.3 (October 2026).
- https://xbrl.us/data-rule/dqc_NNNN/ rule pages (fetched at 1 request/second): message templates and status.

## What failed and why

- **github.com / api.github.com / codeload.github.com: blocked** (HTTP 403 from the session proxy:
  "GitHub access to this repository is not enabled for this session"). Attaching the repo
  `DataQualityCommittee/dqc_us_rules` was refused by the session permission policy. So the DQC repo
  (rule source `.xule`, `resources/DQC_US_*/` JSON/CSV) was **not** used. The element lists come instead from the
  FASB-shipped `dqcrules` taxonomy (same publisher, official), and rule metadata from xbrl.us.
- **xbrl.us rule pages: 129 of 202 obtained.** The rest (DQC_0138 to DQC_0252 mostly) returned HTTP
  500/504 or connection reset on two passes, so their `message_template` and `status` are blank. Their
  title, description, version and dates still come from the index page.
- **SEC EDGAR Filer Manual: skipped.** Two requests (1/s, declared User-Agent) to guessed Filer Manual
  URLs on www.sec.gov returned 404; it is not needed for these tables.
- `ebp/` (employee benefit plan sub-taxonomy, namespace `us-gaap-ebp`, 2024+) is out of scope and not parsed.

## Tables

| File | Rows | Notes |
|---|---|---|
| elements.csv | 22,756 | every element in `elts/us-gaap-<ver>.xsd` of any release 2014-2026 |
| elements_years.csv | 22,756 | name, years_present (shows gaps, e.g. `2014-2016,2018`) |
| deprecations.csv | 6,131 | element, deprecated_in_year, deprecated_date, replacement_element, source, chain |
| deprecations_detail.csv | 6,131 | the same rows plus final_successor, deprecation_kind, replacement_text_cn_ref, reason |
| calc.csv | 9,726 | parent, child, weight, role, first_year, last_year (union across years) |
| calc_years.csv | 9,726 | the same keys plus exact years present and calc spec (2003 / 2023 summation-item) |
| dqc_rules.csv | 202 | one row per approved DQC rule |
| dqc_rule_elements.csv | 9,189 | one row per (rule, element, group, parent, arcrole), 90 rules have element lists |

No file is over 20 MB (largest is elements.csv at 8.2 MB), so none are gzipped.

### elements.csv
Columns: name, first_year, last_year, type, balance, period_type, abstract, substitution_group,
standard_label, documentation, deprecated_year, replacement. Attributes, label and documentation come
from the **latest** release that contains the element. Deprecated elements stay in the schema for
a few years with "(Deprecated YYYY)" in the label, so `last_year` is the last release that still
**ships** the element, not the last year it was active. `documentation` is cut to 500 characters.

### deprecations.csv
The deprecation evidence is unioned from every release:
1. `elts/us-gaap-dep-def` (2014-2018) and `us-gaap-depcon-def` (2018-2026) definition arcs. Arcroles:
   `essence-alias`, `dep-concept-deprecatedConcept`, `dep-aggregateConcept-deprecatedPartConcept`,
   `dep-partConcept-deprecatedAggregateConcept`, `dep-dimensionallyQualifiedConcept-deprecatedConcept`,
   `dep-mutuallyExclusiveConcept-deprecatedConcept`. In every arc, `from` is the successor and `to` is the deprecated element.
   For dimensionally qualified arcs, the line item is the replacement and the axis or member goes in brackets,
   e.g. `CostOfGoodsAndServicesSold [ProductMember, srt:ProductOrServiceAxis]`.
2. `deprecatedDateLabel` / `deprecatedLabel` label roles in `us-gaap-doc` (2014-2017).
3. `us-gaap-cn-ref` change notes (2017+): `DeprecatedDate`, `DeprecatedLabel`, `DeprecationReplacement`,
   `TaxonomyVersion`, `ElementDeprecated`. The replacement is taken from this text only when no arc exists, and the source says so.
4. The "(Deprecated YYYY[-MM-DD])" suffix of the standard label, and the `dep-pre`/`depcon-pre` DeprecatedItems lists.

deprecated_in_year takes the first of these that exists: an explicit date, the change-note TaxonomyVersion, the label
year, then the first release that lists the element. The label year never disagreed with the chosen year (0 mismatches).
Elements deprecated in 2012-2013 appear because the 2014 release still ships them.
`chain` follows successors that were themselves later deprecated (A -> B -> C). Branching
successors are listed as separate paths joined by " ; ". 3,015 rows have a successor. The other
3,116 have none, because FASB gave no replacement (low usage, guidance superseded, or abstracts).

### calc.csv
Summation-item arcs from every `stm/*-cal-*.xml` and `dis/*-cal-*.xml`. The 2024+ releases use the
Calculations 1.1 arcrole `https://xbrl.org/2023/arcrole/summation-item`. It is merged with the 2003
arcrole, and calc_years.csv records which spec was used. `role` is the last path segment of the
extended-link role URI. Non-us-gaap concepts carry their prefix (`srt:`, `dei:`).

### dqc_rules.csv / dqc_rule_elements.csv
dqc_rules: rule_id, title, description, message_template, version, last_updated, approved, effective,
applies_to, status, url, taxonomy_rule_name, taxonomy_rule_documentation, in_fasb_taxonomy_years, source.
dqc_rule_elements: rule_id, element, role_in_rule (the group label from the dqcrules taxonomy, e.g.
"Non-negative Items", "Exclude Non-negative Members", "Element A must be less than or equal to
Element B"), element_prefix, parent_element (for example the axis an excluded member hangs from, or the
summation/greaterThan partner), arcrole, weight, rule_element_ids (e.g. `DQC.US.0015.7131`, the
id printed in DQC messages), first_year, last_year. DQC_0079 / DQC_0001 regex exclusion strings are
rows with arcrole `allowableSubString`/`disallowableSubString`, and the regex is in `element`.

## Resolver use
- **Element families from the taxonomy instead of hand lists.** Filter elements.csv by
  type/balance/period_type, and walk calc.csv (parent -> children with weights, by year) to get the
  members of a family (for example everything that rolls into `Revenues` or `CostsAndExpenses`) for the filing's taxonomy year.
- **Deprecation chains for tag switches.** When a company changes tag across years, look up
  deprecations.csv. If the old tag's `chain` ends in the new tag, the switch is FASB-sanctioned.
  A bracketed replacement means the old value is now reported as the new line item on the named
  axis/member, not on the bare line item. Empty `replacement_element` means FASB named no successor
  (e.g. `SalesRevenueNet`, `CapitalLeaseObligations`), so the resolver must not auto-map it.
- **DQC checks as automatic validations.** dqc_rule_elements gives the machine-readable lists:
  DQC_0015 non-negative items, with member/axis exclusions; DQC_0004 / DQC_0009 equalities and
  less-than-or-equal pairs; DQC_0091 percentage items; DQC_0044/0046/0048 calculation-descendant checks. Run
  them on resolved values, and cite the rule_element_id when a cell fails.
