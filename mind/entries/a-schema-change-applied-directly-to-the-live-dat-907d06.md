---
id: a-schema-change-applied-directly-to-the-live-dat-907d06
title: A schema change applied directly to the live database without a matching committed migration silently diverges from `main`
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
until a clean-DB CI replay catches it, possibly days later. Always add schema changes via a committed migration.
