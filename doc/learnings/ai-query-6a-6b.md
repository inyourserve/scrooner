# AI Query Engine — Stages 6a-6b

## The first real test query failed, and the fix generalizes past this one bug

"companies with ROE above 30%" — the single most natural way an investor would actually phrase this — failed to parse at all on first attempt. The metric-lookup step compared the literal text before "above" (`"companies with roe"`) against a clean alias table that only had `"roe"`. Every one of doc 15's other test queries happened to phrase the metric name without filler words ("software companies", "debt to equity between...", "top 3 by roic") and passed immediately — meaning the bug was specifically in the one query shaped the way a real user is most likely to actually type, not an edge case.

Fixed with a small, explicit, curated list of filler prefixes to strip before lookup (`"companies with "`, `"where "`, `"having "`, etc.) — deliberately not a generic stopword remover, matching the same "reviewed list, not fuzzy matching" discipline as the alias tables themselves (doc 12's reasoning, restated once more: a wrong auto-accepted mapping would silently corrupt a real result).

## Reusing an already-verified downstream system as the correctness oracle

Every positive test query was checked two ways: does it produce the expected `ScreenQuery`, and does running that query through the real Screener reproduce results doc 14b already independently verified? The second check is strictly stronger — it's not just "the parser looks right," it's "the parser produces the exact same real, previously-checked answer." This pattern (verify a new layer by re-deriving a result an earlier, already-trusted layer already proved correct) is available specifically because the Screener was built and verified first — a benefit of following the dependency chain (doc 06) in order rather than building layers out of sequence.

## Verification summary

- 4/4 positive test queries parsed correctly and, after the filler-prefix fix, executed through the real Screener to produce results identical to doc 14b's already-verified output.
- 2/2 negative test queries (ambiguous metric, unrecognized metric) correctly returned `query=None` with the specific reason, never a guessed or partial result.
- Percentage conversion (`30%` → `Decimal("0.30")`) confirmed correct via the ROE test's exact matched values.

## Why it matters going forward

The filler-word gap is a preview of exactly the kind of limitation a real LLM (6c) would handle for free — worth remembering when deciding how much further to invest in the rule-based grammar (6b) versus prioritizing the vendor decision that unblocks 6c. Every additional rule-based fix narrows a gap an LLM wouldn't have had in the first place; that's a real, ongoing cost/benefit question for whoever picks up the vendor decision, not something to keep silently patching around.
