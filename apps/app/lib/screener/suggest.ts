// Client-side typeahead for the create-screen natural-language box
// (2026-10-02) -- the same "type 'ab', see 'above'" experience
// lib/company/search.ts already gives for company names: fetch the whole
// vocabulary once, rank entirely in the browser, zero network/DB round
// trip per keystroke. The vocabulary itself (/api/nl-vocabulary) is the
// exact same phrase table the backend parser resolves against
// (ai_query/aliases.py) -- a suggestion can never name a phrase the
// parser wouldn't also recognize, because there is only one source.
//
// This module only ever suggests WORDS to type, never a resolved
// meaning: clicking a suggestion inserts the literal phrase text. If
// that phrase is still ambiguous (e.g. "revenue growth"), the existing
// "choose a meaning" flow after submission is what resolves it -- same
// division of labor as everywhere else in this project (never guess).

export interface MetricSuggestionEntry {
  phrase: string;
  metric_names: string[];
}
export interface OperatorSuggestionEntry {
  phrase: string;
  operator: string;
}
export interface SectorSuggestionEntry {
  phrase: string;
  field: string;
  value: string;
}
export interface NlVocabulary {
  metrics: MetricSuggestionEntry[];
  operators: OperatorSuggestionEntry[];
  sectors: SectorSuggestionEntry[];
}

export type SuggestionKind = "metric" | "operator" | "sector";
export interface Suggestion {
  phrase: string;
  kind: SuggestionKind;
  metricNames?: string[];
  replaceStart: number;
  replaceEnd: number;
}

const VOCABULARY_CACHE_KEY = "scrooner:nl-vocabulary:v1";
const VOCABULARY_URL = "/api/nl-vocabulary";

function readCachedVocabulary(): { generatedAt: string; vocabulary: NlVocabulary } | null {
  try {
    const raw = localStorage.getItem(VOCABULARY_CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed.generatedAt !== "string" || !parsed.vocabulary) return null;
    return parsed;
  } catch {
    return null;
  }
}

function writeCachedVocabulary(vocabulary: NlVocabulary): void {
  try {
    localStorage.setItem(
      VOCABULARY_CACHE_KEY,
      JSON.stringify({ generatedAt: new Date().toISOString().slice(0, 10), vocabulary }),
    );
  } catch {
    // Best-effort only -- a fresh fetch next time is a fine fallback.
  }
}

function isNlVocabulary(value: unknown): value is NlVocabulary {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  return Array.isArray(v.metrics) && Array.isArray(v.operators) && Array.isArray(v.sectors);
}

let vocabularyPromise: Promise<NlVocabulary> | null = null;

/** Test-only escape hatch: this module intentionally caches the fetch at
 * module scope (same reasoning as lib/company/search.ts's directory
 * cache) so a real page only ever pays for it once -- but that means
 * the cache otherwise persists across every test in a file, making a
 * later test's own fetch stub silently ineffective. Call this in
 * `beforeEach`/`afterEach` in any test that renders a component using
 * `loadNlVocabulary()`. */
export function __resetNlVocabularyCacheForTests(): void {
  vocabularyPromise = null;
  try {
    localStorage.removeItem(VOCABULARY_CACHE_KEY);
  } catch {
    // jsdom/private-mode -- nothing to clear either way.
  }
}

export function loadNlVocabulary(): Promise<NlVocabulary> {
  if (vocabularyPromise) return vocabularyPromise;

  vocabularyPromise = (async () => {
    const today = new Date().toISOString().slice(0, 10);
    const cached = readCachedVocabulary();
    if (cached && isNlVocabulary(cached.vocabulary) && cached.generatedAt === today) {
      return cached.vocabulary;
    }
    const response = await fetch(VOCABULARY_URL);
    if (!response.ok) throw new Error(`nl-vocabulary fetch failed: ${response.status}`);
    const payload: unknown = await response.json();
    if (!isNlVocabulary(payload)) throw new Error("nl-vocabulary response was not the expected shape");
    writeCachedVocabulary(payload);
    return payload;
  })().catch((error) => {
    vocabularyPromise = null; // allow a retry on the next call
    throw error;
  });

  return vocabularyPromise;
}

const CLAUSE_BOUNDARY_RE = /\b(?:and|or)\b/gi;
const MIN_SUGGEST_LENGTH = 2;
const MAX_SUGGESTIONS = 8;

/** Where the "current clause" (since the last and/or) begins, and where
 * the last whitespace-delimited word within it begins. */
function currentTypingContext(text: string, cursor: number) {
  const before = text.slice(0, cursor);
  let tailStart = 0;
  for (const match of before.matchAll(CLAUSE_BOUNDARY_RE)) {
    const end = (match.index ?? 0) + match[0].length;
    if (end <= cursor) tailStart = end;
  }
  while (tailStart < cursor && /\s/.test(text[tailStart])) tailStart += 1;
  const tail = text.slice(tailStart, cursor);
  const lastWhitespace = tail.search(/\s\S*$/);
  const lastWordStart = lastWhitespace === -1 ? tailStart : tailStart + lastWhitespace + 1;
  const lastWord = text.slice(lastWordStart, cursor);
  return { tail, tailStart, lastWord, lastWordStart };
}

/** `phrase` qualifies against `needle` (case-insensitive prefix) when
 * `needle` is long enough to be a meaningful filter, not on every
 * keystroke from character one -- same threshold reasoning as the
 * backend's own typo-suggestion cutoff, just for a plain prefix here. */
function qualifies(phrase: string, needle: string): boolean {
  return needle.trim().length >= MIN_SUGGEST_LENGTH && phrase.startsWith(needle.toLowerCase());
}

export function getSuggestions(
  vocabulary: NlVocabulary,
  text: string,
  cursor: number,
): Suggestion[] {
  const { tail, tailStart, lastWord, lastWordStart } = currentTypingContext(text, cursor);
  const ranked: { suggestion: Suggestion; rank: number }[] = [];

  function consider(phrase: string, kind: SuggestionKind, metricNames?: string[]) {
    if (qualifies(phrase, tail)) {
      ranked.push({ suggestion: { phrase, kind, metricNames, replaceStart: tailStart, replaceEnd: cursor }, rank: 0 });
    } else if (qualifies(phrase, lastWord)) {
      ranked.push({ suggestion: { phrase, kind, metricNames, replaceStart: lastWordStart, replaceEnd: cursor }, rank: 1 });
    }
  }

  for (const entry of vocabulary.metrics) consider(entry.phrase, "metric", entry.metric_names);
  for (const entry of vocabulary.operators) consider(entry.phrase, "operator");
  for (const entry of vocabulary.sectors) consider(entry.phrase, "sector");

  ranked.sort((a, b) => {
    if (a.rank !== b.rank) return a.rank - b.rank;
    if (a.suggestion.phrase.length !== b.suggestion.phrase.length) {
      return a.suggestion.phrase.length - b.suggestion.phrase.length;
    }
    return a.suggestion.phrase.localeCompare(b.suggestion.phrase);
  });

  // Same phrase can qualify at most once (a duplicate would only arise if
  // tail and lastWord were identical, which the if/else above already
  // prevents), but different entries can legitimately share a phrase
  // (none do today) -- de-dupe defensively on (phrase, kind).
  const seen = new Set<string>();
  const result: Suggestion[] = [];
  for (const { suggestion } of ranked) {
    const key = `${suggestion.kind}:${suggestion.phrase}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(suggestion);
    if (result.length >= MAX_SUGGESTIONS) break;
  }
  return result;
}

/** Applies a suggestion to `text`, returning the new text and the cursor
 * position right after the inserted phrase (plus a trailing space, so
 * the user can keep typing the next word immediately). */
export function applySuggestion(
  text: string,
  suggestion: Suggestion,
): { text: string; cursor: number } {
  const insertion = `${suggestion.phrase} `;
  const next = text.slice(0, suggestion.replaceStart) + insertion + text.slice(suggestion.replaceEnd);
  return { text: next, cursor: suggestion.replaceStart + insertion.length };
}
