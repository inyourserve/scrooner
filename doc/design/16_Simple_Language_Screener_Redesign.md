# 16 — Results-first, simple-language screener

> **Status:** Implemented and interaction-tested · **Date:** 2026-08-22  
> **Reference inputs:** `doc/html/new-screen.html`, `doc/html/after-screener.html`  
> **Product surface:** `app.scrooner.com/screener` (Next.js)

## Outcome

The plain-language screener is now a one-action path:

1. describe the companies, or select an example;
2. choose **Show matches**; and
3. see results with the understood criteria beside them.

The previous mandatory **Review my screen → Run this screen** sequence added a
click without adding safety. It has been removed. A click on **Show matches** is
explicit execution consent; the server interprets and runs only when every
clause is valid and unambiguous.

After a successful run, the large creator collapses to a compact current-screen
summary. Results become the dominant surface. Users can reopen the wording or
the exact filter editor without losing the result context.

## What each reference contributed

`new-screen.html` demonstrates a focused creator with one large input and one
clear action, but its formula-like query language is too technical for
Scrooner's proposition.

`after-screener.html` demonstrates the more valuable post-run workflow:
results lead, the query stays editable on the same page, and users are not sent
through a separate creation flow to refine it.

Scrooner combines those interaction patterns with its own advantage: plain
words become deterministic filters and every result remains inspectable. The
references are workflow evidence, not visual or product requirements; their
navigation, account markup, assets, and technical syntax are not copied.

## Experience framework

| State | Primary surface | Primary action | Safety behavior |
|---|---|---|---|
| Empty | Plain-language input and three runnable examples | **Show matches** | No automatic execution while typing |
| Running | Input plus named progress state | Wait | One `/ask` request interprets and runs |
| Ambiguous | The unresolved phrase and candidate meanings | **Choose meaning** | Nothing executes until one meaning is selected |
| Partly unsupported | Recognized criteria plus quoted unsupported wording | Edit wording | Partial criteria never execute |
| Complete | Compact wording and readable criteria summary | Inspect results | Exact interpretation remains available under **Verify** |
| Editing wording | Original language restored in the input | **Show matches** | Existing results remain until replaced |
| Editing filters | Structured metric/operator controls | **Run screen** | Advanced path uses the same typed query contract |
| Zero result | Successful empty state | **Edit criteria** | Clearly distinct from failure |
| Failure | Preserved wording and error explanation | **Try again** | No false empty-result state |

## Click-count contract

| Task | Previous | Current target |
|---|---:|---:|
| Typed valid request → results | 2 clicks | **1 click** |
| Example → results | 3 clicks | **1 click** |
| Ambiguous request → clarified results | 3 clicks | **2 clicks**: submit, choose meaning |
| Open exact filters after results | 1 click | **1 click** |
| Change exact filters and rerun | 2 clicks | **2 clicks**: open, run |

The product should not reduce clicks by guessing. It reduces clicks by combining
interpretation and deterministic execution behind one explicit action while
retaining hard stops for ambiguity and unsupported clauses.

## Information hierarchy

### Before a run

1. Page purpose: **Find companies**.
2. Plain-language input.
3. **Show matches**.
4. One-click examples.
5. Optional **Build with filters** disclosure.

There is no empty 300px result panel and no mandatory intermediate review card.

### After a run

1. Compact current-screen wording.
2. Human-readable criteria chips.
3. Result count and result table.
4. Coverage exclusions and “Why matched” evidence.
5. Metric definitions and exact query disclosures.
6. Optional structured editor after the result surface.

This is the `after-screener.html` loop adapted to Scrooner: answer first, edit in
place, and keep advanced controls available without making them the default.

## Trust contract

- The client sends `{ text, run: true }` only after an explicit submit or an
  explicitly labelled runnable example click.
- The backend returns no `result` when the query is ambiguous, unsupported, or
  only partly recognized.
- Choosing an ambiguity candidate replaces only that phrase and reruns the now
  explicit request; the choice is both clarification and execution consent.
- The compact summary exposes readable criteria immediately after success.
- **Verify how Scrooner understood this** exposes metric, operator, value,
  period policy, sort, limit, and universe.
- Result rows retain exact values, period labels, formula versions, missing-data
  exclusions, match reasons, and links to company/source context.
- Plain-language and structured paths resolve to the same `ScreenQuery` model.

## Responsive and visual rules

- The initial creator remains centered at 960px; completed context aligns with
  the 1220px result surface.
- White and neutral canvas remain the 60/30 foundation; green is reserved for
  actions, verified criteria, and trust cues.
- The completed summary uses low-emphasis borders instead of another large card.
- At mobile width, wording, criteria, and edit actions stack without horizontal
  overflow; result tables retain their explicit horizontal-scroll container.
- Advanced controls remain a single disclosure row until requested.

## Implementation map

- `apps/app/components/screener/NaturalQueryPanel.tsx` — one-request execution,
  ambiguity resolution, runnable examples, compact completed summary, verify
  disclosure.
- `apps/app/components/screener/ScreenerClient.tsx` — accepts the result returned
  by `/ask`, keeps the structured editor optional, and prioritizes results.
- `apps/app/lib/screener/types.ts` — typed optional `AskResponse.result`.
- `apps/app/app/globals.css` — results-first ordering and responsive summary.
- `apps/app/components/screener/ScreenerClient.test.tsx` — click-count and safety
  regression coverage.
- `apps/backend/tests/test_screen_api.py` — valid one-request run plus existing
  ambiguity/partial-query non-execution contracts.

## Acceptance criteria

- [x] Valid typed request reaches results with one user click.
- [x] A labelled example reaches results with one user click.
- [x] No separate review/run gate remains.
- [x] Ambiguous and partly unsupported requests do not execute.
- [x] Choosing a meaning continues without another run click.
- [x] Criteria are readable after success and exactly inspectable on demand.
- [x] Wording and structured filters remain editable.
- [x] Zero results, missing coverage, and failures remain distinct.
- [x] Interaction tests and lint pass.

## Verification evidence

- Next.js: 19/19 component and utility tests pass; ESLint passes.
- Backend: 12/12 screen API tests pass, including one-request valid execution,
  ambiguity blocking, and partial-query blocking.
- Next.js production compilation and TypeScript pass.
- Design-system contract passes with 123 tokens, nine implementation contracts,
  and no raw or undefined application tokens.
- Documentation contract checks 262 local targets successfully.
- Live Chrome passes all eight desktop/mobile surface checks at 1440px and exact
  390px with no horizontal document overflow.
- The expanded browser contract clicks the example once on both viewports,
  verifies the completed current-screen summary, checks that results appear
  visually before the exact editor, and captures completed-state screenshots.
- The live example `companies with ROE above 30%` returned four companies through
  the Next.js proxy in a single `/api/ask` request.

## Product metrics for the next validation round

Measure median time to first result, successful first-submit rate, ambiguity
rate, unsupported-clause rate, example-to-result completion, edit-wording use,
edit-filter use, and zero-result recovery. The next interface change should be
driven by those observations rather than adding more controls.
