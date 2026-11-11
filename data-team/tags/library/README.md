# Standard tag library (cross-company), Tag Expert

`standard-tag-library.csv`: one row per (statement, us-gaap tag), ranked by how often the tag sits on the face of the top-100 companies' statements (all filings in `fsn.*`, read 2026-11-11). It is the cross-company default that `analytics.company_tag_map` starts from (founder method 2026-11-11: FSN to learn which tag is what, SEC company API for values). Company residue (custom tags, a company whose use contradicts a row, combined lines, era changes) is the two Ritwik sessions' layer on top.

Columns (agreed with Ritwik, Mac session): `stmt, tag, decision, concept, parent_concept, reason_class, caveat, evidence, lines_top100, companies_top100, source`.
- `decision`: `map` (a catalog concept, `analytics.canonical_concept`), `component` (part of the named `parent_concept` total; never served as that total), `excluded` (no catalog concept; `reason_class` says why).
- `reason_class`: subtotal_not_in_catalog, component_no_concept, movement_line, equity_component, identity_check_line, per_share_detail, supplemental, caption, nci_component, combined_perimeter.
- `caveat`: the known misuse that must be checked per company before the default applies; `evidence`: the card section or accession that proves it.
- `source`: `explicit` (decided tag by tag from the cards) or `pattern` (family rule: EQ roll-forward lines, OCI components, CF working-capital changes, other components without a concept). Pattern rows are first-cut defaults; tell me where one is wrong.

Coverage of the first cut (2026-11-11): 445 (stmt, tag) rows; 443,032 of the 907,399 top-100 statement lines (49%; the rest are custom extensions, abstracts, axes/members and the long tail). Explicit rows: 217.

Rules that apply to every row: map by face position and the filer's calc tree, not by tag name; a parenthetical (inpth) line is never a balance line; non-dimensional means `dim_id = 0` and `coreg = ''`; take the `iprx = 0` copy (rounded note copies exist); FSN `ddate` is month-end rounded (`datp` = days).
