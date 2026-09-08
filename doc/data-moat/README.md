# The Data Moat — entry point

**Created 2026-09-08.** Scrooner's moat, in order (doc 01): **data → trust → distribution → UX.** Everything in this folder is about the first two — not "do we have SEC data" (anyone can pull that, it's free and public) but "is our copy of it *correct*, and can every number *prove* it." That correctness-and-traceability layer is the actual moat. This folder exists because that work outgrew being one more thread inside the giant, product-wide root `CLAUDE.md` and `doc/` tree — it needs its own home so a future session (human or agent) can load *just* this context and move fast, instead of re-deriving it from a hundred-KB chronological journal every time.

**Scope note (this folder is new as of 2026-09-08, go-forward only):** nothing that already existed got moved here — doc 44, `DATA_COVERAGE.md`, and every `doc/learnings/*.md` entry before today stay exactly where they are, still fully valid, still linked from below. **From today forward, new data-correctness systems get added to [`SYSTEMS.md`](SYSTEMS.md) here (not doc 44), and new data-correctness findings get written into [`learnings/`](learnings/) here (not `doc/learnings/`).** If you're looking for something from before 2026-09-08, it's in the old locations linked below; from today on, it's here.

## The rule everything here obeys

**SEC EDGAR is the only source of truth. Every other source (yfinance, SEC's own Frames API) exists to *detect and match* disagreements — never to supply a value that gets stored.** A fix always traces back to a real `core.fact` row from a real filing. This was made explicit and load-bearing 2026-09-08 (see `sanity/tag_investigator.py`'s own module docstring) but it's really just a sharper restatement of doc 02's original "AI is assistive only, data is deterministic" principle, applied to data verification instead of the screener.

## Map — where everything actually lives

| What you need | Where |
|---|---|
| **Which systems exist, what they do, how to run them** | [`SYSTEMS.md`](SYSTEMS.md) (this folder, current) · [doc 44](../reference/44_Scrooner_Systems_Index.md) (everything through 2026-09-08, including non-data-moat systems) |
| **What's been found and fixed, narrated** | [`learnings/`](learnings/) (this folder, from 2026-09-08 forward) · [`doc/learnings/`](../learnings/) (everything before, plus the day-of entries that predate this folder's creation) |
| **Current coverage numbers** (% of companies with a real value per concept/metric) | [`doc/status/DATA_COVERAGE.md`](../status/DATA_COVERAGE.md) — stays in place; root `CLAUDE.md` already has a hard "update in the same pass" discipline wired to it, not worth forking |
| **The quantitative score + budget tracking** | [`doc/status/SCORECARD.md`](../status/SCORECARD.md) — same reasoning, stays in place |
| **Locked decisions specific to data correctness** | [`decisions.md`](decisions.md) (this folder) — a short, curated pull-out; doc 02 (`doc/foundational/02_Scrooner_Decision_Register.md`) remains the authoritative full register for the whole product |
| **The full, unabridged engineering journal** (every bug, every query, every wrong turn, in order) | [`pipeline/CLAUDE.md`](../../pipeline/CLAUDE.md) — this stays the canonical low-level diary; nothing here duplicates it, this folder curates and points into it |

## Why a real product needs this to be fast, not just correct

The point of separating this isn't organizational tidiness for its own sake — it's throughput. Every session so far has spent real time re-establishing context (what tables exist, what's already been tried, which tag mappings are provisional vs. approved) by reading through unrelated frontend/product history to find the data-relevant parts. A dedicated entry point means the next data-correctness task — human or agent — starts working in minutes, not after re-deriving the whole picture. That compounds: the faster this loop runs, the faster the moat actually widens.
