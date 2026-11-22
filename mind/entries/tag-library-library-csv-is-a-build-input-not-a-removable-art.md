---
id: tag-library-library-csv-is-a-build-input-not-a-removable-art
title: Tag library library.csv is a build input, not a removable artifact
kind: gotcha
tags: tag-library, storage, repo-size
paths: data-team/tags/library/build_library.py, .github/workflows/tag-library-learn.yml
evidence: CODE-CHECKED
status: active
created: 2026-11-21
verified: 2026-11-21
---
build_library.py:284 diffs the new build against the previous library.csv to write CHANGELOG.md. tag-library-learn.yml then runs git add data-team/tags/library. If you git rm library.csv (14.9 MB) to shrink the repo, the next rebuild logs every element as new and adds the file back. Before moving it to Storage, make the workflow download the previous copy before the build and upload the new one after, and gitignore it. Supabase Storage buckets as of 2026-11-21: raw (collector, immutable) and fsn-notes.
