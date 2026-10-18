# Tag feedback inbox (append-only)

Anyone on the data team (agents and humans) appends one line when they learn something about a tag: its meaning, how a company uses it, a misuse, a surprise, or evidence that a card is wrong. The Tag Expert processes this file at the start of every run, updates the cards, records the outcome in `CHANGELOG.md`, and marks the line processed (do not delete lines).

Format: `| date | from (role/agent) | tag | what was learned | evidence (accession+locator or query) | evidence class | status |` with status `new` or `processed <date>`.

| date | from | tag | what was learned | evidence | class | status |
|---|---|---|---|---|---|---|
| 2026-10-19 | Dhairya | all seeded rows in company-quirks.md | seeded from Verifier reports 26, 27, 28, 29, 32 | see those files | FILING-CHECKED | processed 2026-10-19 |
