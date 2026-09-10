# Screen lifecycle: URLs, pagination, and saving

**Status:** Proposed implementation scope — 2026-09-09  
**Applies to:** authenticated screens under `/app/screens/*`  
**Does not cover:** public curated `/screens/*` SEO pages

## Product rule

A screen is a saved definition of *which companies to find*. A run is the result
of applying that definition to data at a particular time.

These are related, but they are not the same object:

- **Screen:** name, stable slug, normalized criteria, owner, timestamps.
- **Run:** screen criteria used, ordered matches, displayed metric values,
  exclusions, total count, and run timestamp.

Saving a screen must attach the run the user has already completed. Opening a
saved screen must read that run. It must not silently execute the financial
query again.

## Final user flow

```text
/app/screens/new
  Enter query
      ↓ Run
/app/screens/new?query=...&run=...&page=1
  See the already-computed results
      ↓ Save and name
/app/screens/{screen_slug}
  See the same run immediately
      ↓ Refresh results (explicit only)
/app/screens/{screen_slug}?run=...&page=1
  See a newly computed run
```

Browser Back returns to the previous state. Reloading a results URL restores
the same run instead of submitting the query again.

## URL contract

| URL | Meaning |
|---|---|
| `/app/screens/` | User's saved-screen library |
| `/app/screens/new/` | Empty query editor |
| `/app/screens/new/?query={text}&run={run_id}&page=1` | Unsaved result view |
| `/app/screens/{slug}/` | Saved screen using its latest attached run |
| `/app/screens/{slug}/?run={run_id}&page=2` | A specific run and page |

`query` contains the user's readable input, not the large normalized JSON
contract. The server stores the normalized query against `run_id`. URLs remain
shareable within the user's authenticated session without becoming enormous.

Reserved private slugs: `new`, `results`, `create`, `edit`, and `api`.

## Slug rules

- Generate the slug from the screen name on first save.
- Slugs are lowercase ASCII with hyphens.
- Slugs are unique per user, not globally.
- Resolve collisions deterministically: `quality-companies`,
  `quality-companies-2`, `quality-companies-3`.
- Renaming a screen does not silently change its slug or break bookmarks.
- The numeric database ID remains internal and never appears in the user URL.
- Screen lookup always combines `user_id` and `slug`; a user can never read
  another user's screen by guessing its slug.

Required database constraint and lookup index:

```sql
unique (user_id, slug)
```

## Running a query

Submitting `/app/screens/new` performs one mutation:

```http
POST /api/screen-runs
{
  "text": "ROE above 20% and debt to equity below 1",
  "page_size": 50
}
```

The backend interprets, validates, and executes in one request. It persists an
immutable run and returns:

```json
{
  "run_id": "uuid",
  "query_text": "ROE above 20% and debt to equity below 1",
  "normalized_query": {},
  "total_count": 87,
  "items": [],
  "next_cursor": "opaque-or-null",
  "ran_at": "timestamp"
}
```

After success, the frontend uses `router.push()` to place `query`, `run`, and
`page=1` in the URL. It renders the returned response immediately. It must not
fetch the same first page again after navigation.

## Pagination

Pagination happens on the server. The frontend must never download every match
and slice it in the browser.

- Default page size: 50.
- The database preserves a deterministic result position for every company.
- API navigation uses an opaque cursor backed by `(run_id, position)`.
- The URL may show `page=2` for humans, while also carrying the opaque cursor.
- UI copy is simple: `1–50 of 87`, Previous, Next.
- Changing page reads stored run rows. It does not reinterpret or rerun the
  screen.
- Sorting or changing criteria creates a new run because it changes the ordered
  result set.

Cursor pagination is chosen over deep SQL `OFFSET`, keeping lookup cost stable
as result sets grow.

## Saving

Saving from an unsaved result sends:

```http
POST /api/screens
{
  "name": "High quality companies",
  "query": {},
  "run_id": "uuid"
}
```

The backend creates the screen, verifies that the run belongs to the same user,
attaches it as the latest run, and returns:

```json
{
  "id": 123,
  "name": "High quality companies",
  "slug": "high-quality-companies"
}
```

The frontend immediately navigates to
`/app/screens/high-quality-companies/`. There is no success toast followed by
remaining on `/new`, and there is no second screen execution.

## Opening a saved screen

One screen-read endpoint returns the screen definition, latest-run metadata,
and requested result page together:

```http
GET /api/screens/{slug}?page_size=50&cursor=...
```

Opening the page performs one read. Client effects must not issue duplicate
list calls and then search for the screen. The detail page fetches its screen
directly by owner and slug on the server.

Development-only React Strict Mode may invoke client effects twice. This flow
does not depend on a client mount effect for its initial data, so Strict Mode
cannot duplicate the query.

## Refresh semantics

The saved page displays:

```text
87 matches                         Updated 9 Sep 2026, 01:20
[Refresh results]
```

Only **Refresh results** creates a new run. After it succeeds, that run becomes
the screen's latest run. Old run URLs may remain readable for a short retention
period so browser history works.

Do not call this action “Run” on an already-saved screen; “Refresh results”
communicates that the saved definition remains unchanged while data is updated.

## Persistence model

Extend `app.saved_screen` with:

- `slug text not null`
- `last_run_id uuid null`
- unique `(user_id, slug)`

Add immutable run storage:

```text
app.screen_run
  id, user_id, query_text, normalized_query, total_count,
  exclusions, created_at, expires_at

app.screen_run_result
  run_id, position, company_id, displayed_metrics
```

`screen_run_result` uses primary key `(run_id, position)` and an additional
unique constraint on `(run_id, company_id)`. Pages read by run and position.
Runs attached to a saved screen are retained. Unattached runs can expire.

Do not store only a giant result array in `app.saved_screen.query`. It makes
pagination expensive, mixes definition with execution, and turns every update
into a large JSON rewrite.

## What saving means

Saving provides four concrete benefits:

1. A memorable, stable URL.
2. The criteria remain available across sessions.
3. The last result opens immediately without recomputation.
4. The user can explicitly refresh the same definition against newer data.

It does **not** mean that the original result is treated as permanently current.
The page always shows when the attached run was produced.

## Remove from the current implementation

- Session-storage handoff as the primary saved-screen mechanism.
- Loading the entire saved-screen list to open one screen.
- Automatic rerun when a saved screen opens.
- Duplicate `/api/screens` fetches from mount effects.
- Numeric IDs in user-facing screen URLs.
- Saving followed only by a toast while the user remains on `/new`.
- Client-side pagination over a full result payload.

## Delivery sequence

1. Add run persistence, slug, ownership constraints, and indexes.
2. Add create/read/refresh run endpoints and direct screen-by-slug endpoint.
3. Make `/app/screens/new` URL-driven after submit.
4. Add cursor-backed results pagination.
5. Make Save attach the current run and redirect to the slug URL.
6. Build `/app/screens/[slug]` as a server-loaded detail page.
7. Remove session-storage and automatic rerun paths.
8. Add retention cleanup for unattached runs.

## Acceptance criteria

- Running a query changes the URL and creates exactly one backend run.
- Reloading that URL shows the same results without another run.
- Next and Previous change pages without rerunning criteria.
- Saving creates one screen and redirects to `/app/screens/{slug}`.
- The saved page initially shows the exact run that was saved.
- Reloading a saved page performs reads only.
- Refresh results creates exactly one new run and updates `ran_at`.
- Two users can use the same slug without collision or cross-user access.
- Renaming does not break the existing URL.
- Every `/app/screens/*` response remains authenticated and `noindex`.

## Explicit non-goals

- Public user-generated screens.
- Sharing private screens between accounts.
- Scheduled email alerts.
- Full run history UI.
- Arbitrary column customization.
- Live-updating results while the page is open.

Those can be scoped after the core lifecycle is reliable.
