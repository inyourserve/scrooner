---
id: before-pushing-resolver-extract-roles-library-changes-full-p
title: Before pushing resolver/extract/roles/library changes: full pipeline suite plus structural_loader.read_claims must show 0 rejects
kind: rule
evidence: CODE-CHECKED
created: 2026-11-16
verified: 2026-11-16
---
Dhairya 2026-11-16: .57 not_in_template broke test_tag_library_rebuild:285 and .54's mem CTE broke test_fsn_dim_note:111; .58 text rows and .57 BEFORE: rows gave 21 loader rejects (fixed in .59, 3d870ed6). line_map tests alone are not enough. Run uv run --project pipeline pytest pipeline/tests against Postgres 16 (scripts/ci/bootstrap_supabase.sql, then every migration; ci.yml is the reference) and diff the failures against the parent commit (this container has about 18 pre-existing fixture and subprocess failures). Then run structural_loader.read_claims(Path(resolver csv)) with dummy DATABASE_URL, SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY: rejects must be 0. A mapped row needs a tag unless it is flagged stated_zero; a row without an accession is allowed only for not_presented with before_first_10k.
