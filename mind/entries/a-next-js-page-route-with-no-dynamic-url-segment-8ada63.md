---
id: a-next-js-page-route-with-no-dynamic-url-segment-8ada63
title: A Next.js page/route with no dynamic URL segment and no `force-dynamic` export gets statically prerendered at `next build` time — if its data comes from a `fetc
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
`force-dynamic` isn't just "skip Next's own cache" — it's also "never render at build time." A page with a dynamic segment (`[ticker]`, `[slug]`) is safe without it since Next defers those to request time by default; a flat-path page (homepage, `/explore`, `/stocks`, etc.), a route handler, or `sitemap.ts` needs it explicitly whenever its data comes from a backend fetch. Found 2026-10-13 removing it during a caching port (doc 54) that moved several flat pages off direct Postgres onto `apps/backend` — see `doc/learnings/2026-10-13-sitewide-caching-built.md`'s addendum.
