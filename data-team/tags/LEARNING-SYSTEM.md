# Tag Expert learning system

Owner: the Tag Expert. Direction: Dhairya, 2026-11-13, at the founder's request ("create scalable learning system for tag expert … where his mind can be scalable"). Bar and graduation: `data-team/NOW.md`.

## Why the current setup doesn't scale

The predictor's knowledge sits in Python dicts in `exam/tools/predict.py`: DEMOTE regexes, NOTE_RULES, BANK. The reasons sit in prose cards. Three things follow:
- Only one session can safely change it.
- Its context window has to hold the whole of it.
- Nothing records which piece of knowledge produced which right or wrong answer.

A mind that scales needs knowledge that is **data, executable, evidenced and measured per rule**.

## 1. Knowledge is rules, not prose

`data-team/tags/rules/<namespace>.csv`, one row per rule. Namespaces: `bs`, `is`, `cf`, `notes`, `per_share`, `bank`, `insurer`, `reit`, `utility`, `energy`, `company`. Columns:

| column | meaning |
|---|---|
| rule_id | stable id, e.g. `is.interest_expense.net_label_demote` |
| version | integer; bumped on every change |
| data_point | template data point |
| scope | `all`, a template group, a sector, or a ticker (company override) |
| era | from/to period, or blank |
| when | machine-readable condition: tag in set, label regex, statement, calc parent, sibling present, custom tag, DQC check |
| then | status / tags / sign / value_source |
| precedence | company > template > data point > default |
| evidence | accession+R page, DQC id, FASB/taxonomy reference, or doc 02 decision |
| author / date | who added it, from which finding |

Cards (`cards/*.md`) become **generated views** of these rows plus their stats. A card is never edited by hand.

## 2. The predictor is an engine over the rules

`predict.py` loads `rules/*.csv`, fires rules by precedence, and writes `rule_ids` on every predicted row. It holds no domain knowledge in code. It stays deterministic and versioned (`VERSION` = hash of the rule files).

## 3. The evidence ledger gives every rule its own score

`exam/results/ledger.csv` is append-only, one row per graded data point: ticker, data_point, template group, predictor version, rule_ids fired, predicted, key, key evidence (hand or machine), result.

From it, every rule has: fires, correct, wrong, its blind accuracy, and its last wrong case. Weak rules (accuracy below 95% over 20 or more fires) are listed for repair. Dead rules (0 fires in 300 companies) are retired.

## 4. The learning loop runs on every new docmap chunk

1. **Grade** the new docmaps against the predictions committed before them, and append to the ledger.
2. **Cluster** the misses by the rule that fired, or by the rule that was missing.
3. **Propose** a rule add or edit, with evidence (R page, DQC id).
4. **Backtest** the candidate rule set on ALL read companies, hand-verified keys only (`exam/tools/backtest.py`).
5. **Accept** only if net accuracy rises and no data-point × template class that is graduated, or at 99% or better, loses a single row.
6. **Commit** with a version bump, then re-predict the unread tickers.

## 5. Many contributors, one curator

- Readers, the Verifier, the nightly path and Engineering submit proposals as rows in `rules/inbox/*.csv`. These rows use the same columns plus `proposed_by` and `finding`.
- The Tag Expert curates: it accepts only through the backtest.
- Sub-agents can each own one namespace (bs, is, cf, notes, banks, …) and run the loop in parallel. Namespaces don't conflict, because precedence is explicit.
- This is how the mind grows beyond one session's context. Each agent loads only the rules for the tags in front of it (an index by tag), never every card.

## 6. External knowledge is ingested as rules

- XBRL US DQC rules, the US GAAP taxonomy implementation guides and SEC staff XBRL observations each become rules, with the source id in `evidence`.
- A DQC check that applies becomes a `when` validation the loader can run too.
- A DQC rule wins over a card unless a filing proves the company does something else. That exception is a company-scope rule.

## 7. Metrics on the scoreboard

- Rules: count by namespace.
- Tag-union coverage: tags printed by the 1,000 that have at least one rule.
- Accuracy per rule.
- Blind accuracy trend per 100 companies.
- Graduated classes.
- Proposals: open, accepted, rejected by the backtest.

## 8. Later: the database

Once the format settles, `rules` and `ledger` move into database tables (a migration claimed in doc 53; applying it needs the founder's typed words). Then the loader, the nightly auto-mapper and the predictor all read the same rules.
