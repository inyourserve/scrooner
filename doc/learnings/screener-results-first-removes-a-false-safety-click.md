# Screener: results-first removes a false safety click

**Problem or clarification**

The plain-language screener was simple in vocabulary but still cumbersome in
sequence. A valid request required **Review my screen** and then **Run this
screen**. That made the user approve the same intent twice and placed a large
review surface between the idea and its answer. The earlier
`plain-language-screener-progressive-disclosure.md` entry correctly moved the
technical builder out of the default path, but its mandatory pre-run review was
still one disclosure layer too many.

**How it was found**

`doc/html/new-screen.html`, `doc/html/after-screener.html`, the live React
component, and the `/v1/ask` backend contract were compared as one workflow.
The first reference showed a focused creator. The second showed the more useful
post-run loop: results lead and the query remains editable on the same page.
Code inspection then confirmed that `/v1/ask` already accepts `run: true` and
refuses to call the screener when interpretation returns no valid query.

The click audit made the friction concrete:

- typed request to result: two clicks;
- example to result: three clicks;
- ambiguity resolution: review, choose meaning, then run.

The extra review click was not the mechanism providing safety. Parser and
backend validity checks were.

**Fix / decision**

The primary action is now **Show matches**. It sends one explicit
interpret-and-run request. Valid requests return the interpreted query and the
result together. Ambiguous, unsupported, and partially recognized requests
return no result and show a clarification state. Choosing an offered meaning
continues the already requested run.

After success, the creator collapses to the original wording and readable
criteria chips. Exact interpretation is one disclosure away, results are the
primary surface, and **Edit wording** / **Edit filters** preserve the same-page
loop. Runnable examples are explicitly labelled and reach results in one click.

This changed `NaturalQueryPanel.tsx`, `ScreenerClient.tsx`, the typed ask
response, stylesheet, component tests, backend contract tests, and the canonical
design framework.

**Why it matters going forward**

Do not equate an extra confirmation screen with safety. A confirmation earns
its place only when the user is making a new decision, facing ambiguity, or
triggering a consequential operation. For a deterministic read-only screen,
one explicit action plus strict server-side non-execution rules is both safer
and faster than two consecutive approvals.

The durable pattern is:

> explicit intent → validate → execute only if unambiguous → show the exact
> interpretation with the answer → keep editing in place

Click-count targets should be treated as interaction contracts and protected by
tests, while ambiguity and partial-query non-execution remain server contracts.
