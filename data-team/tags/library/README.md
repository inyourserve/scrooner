# Scrooner tag library

The single place that says what every element is, which data point it serves, under which rule, how often it is proven, and what has gone wrong with it. One row per element: the us-gaap taxonomy, plus every custom element the resolver has served.

**Generated, never edited by hand.** Rebuild it on every resolver version (part of the release procedure in `line_map/README.md` and `line_map/CHANGELOG.md`) and every daily drill:

    python3 data-team/tags/library/build_library.py                  # repo root; read-only, no DB, no network, ~5 s
    python3 data-team/tags/library/build_library.py --check-version  # the CI gate (below)

## One library (2026-11-22)

This is the only tag library. `build_library.py` is the only builder; everything else reads its output:

| Reader | What it takes from `library.csv` |
|---|---|
| `pipeline/src/scrooner_pipeline/mapper/library_csv.py` | the shared reader the two DB loaders use (`load`, `knowledge`, `sec_tag_library_rows`) |
| `mapper/tag_library_rebuild.py` → analytics.tag_library_entry (0128) | polarity class per data point, deprecated_by / replaces, caveats, known problems (no longer re-read from polarity.csv, deprecations.csv, standard-tag-library.csv) |
| `mapper/tag_library.py`, `library` stage → analytics.sec_tag_library (0077) | mapping status, data points (`mapped_concepts` / `candidate_for_concepts`), metrics (no longer re-derived from the retired concept_mapping / concept_tag_candidate); usage counts still come from analytics.company_sec_tag |
| `data-team/tags/cards/*.md` | the generated block at the end of each card (below) |

**Version gate.** `coverage.json` records the resolver version the library was built from. CI (`ci.yml`, step "Tag library built for the newest resolver version", plus `test_committed_library_is_built_for_the_newest_resolver_version`) fails while it is older than the newest `resolver_version` in `line_map/resolver/*.csv`.

**Card blocks.** Each hand-written card in `data-team/tags/cards/` (not `generated/`, which the rules tooling owns) ends with a block between `<!-- BEGIN GENERATED: tag library rows ... -->` and `<!-- END GENERATED: tag library rows -->`. For every element the card's prose names that the library knows (most served first, 30 at most), it lists the meaning, data point, rules, evidence counts, known problems, pattern hits (any `pattern*` column) and deprecations. The build rewrites only that block; the prose above it is marked `HAND-WRITTEN` and never rewritten, and element names inside the block never count as card mentions.

## Learning loop (from the filings, FSN and SEC)

1. `learn_from_filings.py EXTRACT_DIR` reads the standard extract (the same filings the resolver reads) and writes `learned_elements.csv`: every element filers use, with its labels, statements, own calc parents, filings and companies, note use and member axes, and custom or standard. It also writes `learned_labels.csv`: the face labels of every line the resolver served, per data point.
2. `build_library.py` folds both into `library.csv`, next to the taxonomy (FASB meaning and deprecations), the rules, proof and certification.
3. The resolver reads `learned_labels.csv` back. A label that served a data point at two or more companies, and no other data point, blocks a false absence hide. The learned tables are also the place to find problems: the first run exposed net interest income served from industrials' interest-expense lines (fixed in .56).
4. Run 1 then 2 after every extract. On the full 1,000-company extract this is the FSN-wide pass, with no extra DB query.

## Files

| File | What it is |
|---|---|
| `library.csv` | One row per element. This is the input the resolver, proof, the daily drill and both DB loaders (analytics.tag_library_entry, analytics.sec_tag_library) read. `polarity` holds `data_point:positive|signed|raw` (rules/polarity.csv sign and normalise, common/polarity.py semantics). |
| `library.json` | The same rows, limited to elements with any knowledge (usage, a rule or a proof). |
| `library.schema.json` | Column schema. Lists inside a cell are `;`-separated. |
| `INDEX.md` | Elements by data point, statement, family and problem type. |
| `browser.html` | Static search page. Open it in a browser, search an element, ruling ID, ticker or problem, and click through the links. |
| `CHANGELOG.md` | Per build, what changed per element (data points, rulings, served, proven, certified, problems, successors). |
| `coverage.json` | Row counts and coverage (below). |
| `learn_from_filings.py`, `learned_elements.csv`, `learned_labels.csv` | The learning step above. |
| `proof_by_tag.csv` / `proof_by_tag.sql` | analytics.cell_proof aggregated by shown tag. The SQL refreshes it (read-only). |

## Columns (matching the DB schema: element, taxonomy, data_point, rule_id, polarity, family, deprecated_by, replaces, statements and positions, companies, proven_cells, certified_cells, known_problems, links, last_verified)

- **Meaning** (FASB taxonomy, `data-team/tags/taxonomy/`): `taxonomy, standard_label, definition, balance, period_type, data_type, abstract, taxonomy_years`.
- **Deprecation**: `deprecated_year, replaces, deprecated_by, deprecation_chain`.
- **Mapping**: `data_point` (resolver data points), `roles_rows` (rules/roles.csv rows), `role_kind` (primary, combined or part, with the alternative's rank), `rule_id` (RULEBOOK IDs), `resolver_functions`, `tests`, `polarity`, `family` (code lists such as resolve_cf.CAPEX).
- **Where it sits**: `statements`, `positions` (face, note, BS parenthetical, equity statement, with counts from the resolver's served nodes), `calc_parents` (taxonomy calc).
- **Use downstream**: `metrics` (the metric registry formulas whose inputs include its data point), `concept_catalog`.
- **Usage**: `companies, filings_seen, years_seen, served_cells, example_cells` (ticker, year, data point, accession, R page).
- **Evidence**: `proof_cells, proven_cells, proof_companies, last_verified` (analytics.cell_proof), `certified_cells` (certification coverage files), `composite_uses` (proven as a part of a multi-element cell).
- **Folded-in legacy library**: `fsn_lines_top100, fsn_companies_top100, legacy_decision, legacy_concept, legacy_caveat` (standard-tag-library.csv, needs-detail-answers-r1r2.csv) and `company_overrides` (company-overrides.csv).
- **Problems**: `known_problems` (filer XBRL errors, FSN dropped facts, each with its evidence), `problem_commits` (ruling ID and resolver version that fixed it).
- **Links**: `links` (one list of every cross-reference) and the detailed `cards`, `mind_ids`, `ledger_lines`.
- **Quality bar**: `quality` (companies, proven, certified, open problems, last verified) and `full_row` (yes when the row has a data point, a ruling, served cells, proof or certification, and the taxonomy meaning once the taxonomy tables are present).

## How a tag gets mapped, end to end

1. **Filings.** The extract selects the company's annual reports through `company_filings` (own CIK minus exclude windows, plus predecessor CIKs; RULEBOOK section 2).
2. **Position.** The resolver reads each data point by position on the face and the filer's calc tree (RULEBOOK X01). The element only ranks the nodes that already hold the role. Custom lines count when their own label names the role.
3. **Alternatives.** For each data point, the element alternatives, combined lines and note fallbacks are the `roles_rows` / `family` of this library (rules/roles.csv, resolve_cf lists, total_debt patterns).
4. **Guards** then decide value or reason: combined, net, per class, absence proof, fills from later 10-Ks, printed dashes. Each is one `rule_id`, with its test.
5. **Proof and certification** check the served cell against the R page. Their counts come back here as `proven_cells` / `certified_cells`.

## Diagnosing a new company's open cell with the library

1. Find the element on the open cell's face line (FSN line) or note fact, and search it in `browser.html`.
2. **No row, or no `data_point`:** the element is unknown to the resolver.
   - Check `definition` and `deprecation_chain`. A successor of a known element gets the same role.
   - Otherwise it is a new mapping: add the alternative to roles.csv with a test, and a RULEBOOK row.
3. **Row exists:**
   - Read `rule_id` and `known_problems` for the case: combined label, net line, per-class EPS, component element.
   - Check `example_cells` for a company that resolved the same way, and follow its R page.
4. **Proven count is low and `open_problems` > 0:** treat the element as risky. Read the linked card and mind entries before serving it.
5. After the fix, rebuild. `CHANGELOG.md` shows what moved for the element.

## Coverage

`coverage.json` has `coverage_pct`: the share of resolver-served cells whose every element has a full row.

## Legacy inputs folded into library.csv

These files stay as generator inputs, because pipeline code reads them (pipeline/scripts/tag_map_seed_r1r2.py, its tests, the exam tools). Do not add rows to them; new knowledge goes into rules/roles.csv, RULEBOOK.md or the code, and shows up here on rebuild. Their original notes follow.

### Legacy: standard tag library (cross-company), 2026-11-11

`standard-tag-library.csv`: one row per (statement, us-gaap tag), ranked by how often the tag sits on the face of the top-100 companies' statements (all filings in `fsn.*`, read 2026-11-11). It is the cross-company default that `analytics.company_tag_map` starts from (founder method 2026-11-11: FSN to learn which tag is what, SEC company API for values). Company residue (custom tags, a company whose use contradicts a row, combined lines, era changes) is the two Ritwik sessions' layer on top.

Columns (agreed with Ritwik, Mac session): `stmt, tag, decision, concept, parent_concept, reason_class, caveat, evidence, lines_top100, companies_top100, source`.
- `decision`: `map` (a catalog concept, `analytics.canonical_concept`), `component` (part of the named `parent_concept` total; never served as that total), `excluded` (no catalog concept; `reason_class` says why).
- `reason_class`: subtotal_not_in_catalog, component_no_concept, movement_line, equity_component, identity_check_line, per_share_detail, supplemental, caption, nci_component, combined_perimeter.
- `caveat`: the known misuse that must be checked per company before the default applies; `evidence`: the card section or accession that proves it.
- `source`: `explicit` (decided tag by tag from the cards) or `pattern` (family rule: EQ roll-forward lines, OCI components, CF working-capital changes, other components without a concept). Pattern rows are first-cut defaults; tell me where one is wrong.

Coverage of the first cut (2026-11-11): 445 (stmt, tag) rows; 443,032 of the 907,399 top-100 statement lines (49%; the rest are custom extensions, abstracts, axes/members and the long tail). Explicit rows: 217.

Rules that apply to every row: map by face position and the filer's calc tree, not by tag name; a parenthetical (inpth) line is never a balance line; non-dimensional means `dim_id = 0` and `coreg = ''`; take the `iprx = 0` copy (rounded note copies exist); FSN `ddate` is month-end rounded (`datp` = days).

### Legacy: company-overrides.csv (2026-11-12)
Company-scoped mappings that the library default does not allow (doc 02: a label may demote a line but never promote it). Only FILING-CHECKED rows are usable; PENDING-FILING-CHECK rows wait for an R-page read. Columns: company, cik, tag, stmt, concept, scope, status, evidence, note.

### Legacy: needs-detail-answers-r1r2.csv (2026-11-12)
Answers to Engineering's data-team/47-fsn-store/company_tag_map/needs_detail_r1r2.csv (168 rows, all closed). Added columns: final_decision, members (concept:sign, only from the filing's own calc children or same-filing facts; instants never by subtraction), sign (component contribution to its parent concept, on stored values), label_condition, rule, status. Concept keys use concepts_catalog.csv (_resolved keys where they exist).

- company-overrides.csv column `value_source` (2026-11-12, doc 02 "Founder decision of 2026-11-12: value source for custom-tag lines" (doc/foundational/02_Scrooner_Decision_Register.md, main fcf1425d)): `fsn_xbrl` = value from the filing's own XBRL via SEC FSN data, checked against the printed R page (custom tags); `sec_api` = SEC API (standard tags).

## CI: rebuilt after every extract

`.github/workflows/tag-library-learn.yml` runs after each successful standard extract on main (or by dispatch with an
extract run id): resolver, `learn_from_filings.py`, `build_library.py`, the library and resolver tests, then pushes the
result to branch `data/library-<date>` (never main). Review the branch diff and bring it to main by hand; learned labels
are candidates and never reach the resolver unreviewed.
