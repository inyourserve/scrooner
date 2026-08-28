# Plain-language screener: progressive disclosure beats parallel builders

**Problem or clarification**

The screener had two complete creation experiences stacked vertically: a large
plain-language interpreter and a permanently visible structured builder. Both
were individually capable, but together they made the page feel technical and
forced the main action below too much interface. The supplied
`doc/html/new-screen.html` was visually focused, yet its query language was more
technical than Scrooner's proposition.

**How it was found**

The reference HTML was read as a source artifact and compared with the rendered
Scrooner page at 1440×1100 and 390×844. The comparison showed that the valuable
reference pattern was its single-card focus, example placement, and action
hierarchy—not its `Metric > value AND ...` syntax. At mobile width, Scrooner's
old hierarchy spent the first viewport explaining tools rather than helping the
user complete a screen.

**Fix / decision**

Plain language became an end-to-end path: describe, review human-readable
filters, and deliberately run. The exact builder moved behind **Build with
filters** and opens when **Edit filters** is chosen. Examples sit beside the
input on desktop and follow the action on mobile. The idle result panel was
compressed. Both paths still use the same deterministic query and screen APIs.

The change is implemented in `NaturalQueryPanel.tsx`, `ScreenerClient.tsx`, and
the app stylesheet, with interaction tests and the live render contract updated
to protect the new hierarchy.

**Why it matters going forward**

Progressive disclosure should separate user sophistication without splitting
the underlying product contract. A simple interface is not less rigorous: it
can keep ambiguity resolution, explicit review, exact execution, periods,
formulas, and coverage evidence while hiding controls that are unnecessary for
the current decision. Competitive references should be decomposed into useful
patterns and unsuitable assumptions instead of copied wholesale.
