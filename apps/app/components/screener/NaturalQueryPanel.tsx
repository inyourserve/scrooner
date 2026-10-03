"use client";

import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { useRouter } from "next/navigation";
import { metricByName } from "@/lib/screener/catalog";
import { NATURAL_QUERY_EXAMPLES, parserPhraseForMetric } from "@/lib/screener/interpretation";
import { applySuggestion, getSuggestions, loadNlVocabulary, type NlVocabulary, type Suggestion } from "@/lib/screener/suggest";
import type { AskResponse, MetricDefinition } from "@/lib/screener/types";
import { Button } from "@/components/ui/Button";
import { StatusPanel } from "@/components/ui/StatusPanel";
import { InterpretationTable } from "./InterpretationTable";
import { cacheRunPageForNavigation, registerPendingRun, savedScreensApi } from "@/lib/saved-screens/client";
import type { ScreenRunPage } from "@/lib/saved-screens/types";

type InterpretState = "idle" | "loading" | "attention" | "error";

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// This panel's only job once a run exists is to hand it off -- the run
// itself (query_text, normalized_query, results) is the single source of
// truth from here on, and ScreenerClient's URL-driven state is the only
// place that turns it into a displayed screen. Rendering a second,
// independent "here's your screen" summary here (as an earlier version of
// this component did) meant two places could show a query and disagree.
export function NaturalQueryPanel({
  metrics,
  initialText = "",
  onRunCreated,
  submitPath,
  autoRun = false,
  pageSize = 50,
  title = "Create a screen",
  hidden = false,
  onBlocked,
}: {
  metrics: MetricDefinition[];
  initialText?: string;
  onRunCreated?: (run: ScreenRunPage) => void;
  submitPath?: string;
  autoRun?: boolean;
  pageSize?: number;
  title?: string;
  hidden?: boolean;
  onBlocked?: () => void;
}) {
  const router = useRouter();
  const [text, setText] = useState(initialText);
  const [state, setState] = useState<InterpretState>("idle");
  const [interpretation, setInterpretation] = useState<AskResponse | null>(null);
  const [error, setError] = useState("");
  const requestVersion = useRef(0);
  const autoRunStarted = useRef(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Typeahead (2026-10-02) -- the same "type 'ab', see 'above'" experience
  // company search already gives for company names, built entirely
  // client-side (see lib/screener/suggest.ts's own module comment for why
  // this can never recommend a phrase the real parser wouldn't also
  // recognize). `vocabulary` loads once per mount and is never on the
  // critical path for typing or submitting -- a failed/slow fetch just
  // means no suggestions, never a blocked textarea.
  const [vocabulary, setVocabulary] = useState<NlVocabulary | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [activeSuggestion, setActiveSuggestion] = useState(0);

  useEffect(() => {
    let active = true;
    void loadNlVocabulary().then((loaded) => {
      if (!active) return;
      setVocabulary(loaded);
      // The fetch can resolve after the user has already started typing
      // (its own fetch + the mount effect both race the user's first
      // keystroke) -- recompute for whatever's in the box right now
      // instead of waiting for the next keystroke to reflect it.
      const el = textareaRef.current;
      if (el) setSuggestions(getSuggestions(loaded, el.value, el.selectionStart ?? el.value.length));
    }).catch(() => {});
    return () => { active = false; };
  }, []);

  function updateSuggestions(nextText: string, cursor: number) {
    if (!vocabulary) { setSuggestions([]); return; }
    setSuggestions(getSuggestions(vocabulary, nextText, cursor));
    setActiveSuggestion(0);
  }

  function changeText(next: string, cursor?: number) {
    requestVersion.current += 1;
    setText(next);
    setInterpretation(null);
    setState("idle");
    setError("");
    updateSuggestions(next, cursor ?? next.length);
  }

  function applySuggestionAt(index: number) {
    const suggestion = suggestions[index];
    if (!suggestion) return;
    const result = applySuggestion(text, suggestion);
    setText(result.text);
    setSuggestions([]);
    window.requestAnimationFrame(() => {
      const el = textareaRef.current;
      if (!el) return;
      el.focus();
      el.selectionStart = result.cursor;
      el.selectionEnd = result.cursor;
    });
  }

  async function runQuery(nextText = text) {
    const normalized = nextText.trim();
    if (!normalized) {
      setState("attention");
      setInterpretation({
        explanation: "Enter a supported screening request.",
        query: null,
        recognized_query: null,
        unrecognized: ["Empty query"],
        ambiguous: [],
      });
      onBlocked?.();
      return;
    }

    const version = ++requestVersion.current;
    setState("loading");
    setError("");
    try {
      const requestedRunId = submitPath ? crypto.randomUUID() : undefined;
      const request = savedScreensApi.createRun(normalized, pageSize, requestedRunId);
      if (submitPath && requestedRunId) {
        registerPendingRun(requestedRunId, request);
        const params = new URLSearchParams({
          query: normalized,
          run: requestedRunId,
          page: "1",
          limit: String(pageSize),
        });
        router.push(`${submitPath}?${params}`, { scroll: true });
      }
      const payload: unknown = await request;
      if (version !== requestVersion.current) return;
      if (payload && typeof payload === "object" && "run_id" in payload) {
        // Hand the run straight to ScreenerClient (the single source of
        // truth for "what's on screen" from here) and reset this panel to
        // its ready state -- no local copy of the query/result is kept
        // here, so there's nothing that could drift out of sync with what
        // the results section below actually shows.
        const run = payload as ScreenRunPage;
        if (submitPath && !requestedRunId) {
          cacheRunPageForNavigation(run, pageSize);
          const params = new URLSearchParams({
            query: run.query_text,
            run: run.run_id,
            page: "1",
            limit: String(pageSize),
          });
          if (run.normalized_query.sort_by) {
            params.set("sort", run.normalized_query.sort_by);
            params.set("order", run.normalized_query.sort_desc ? "desc" : "asc");
          }
          router.push(`${submitPath}?${params}`, { scroll: true });
        } else {
          onRunCreated?.(run);
        }
        setState("idle");
        setInterpretation(null);
        return;
      }
      const next = payload as AskResponse;
      setInterpretation(next);

      if (!next.query || next.unrecognized.length > 0 || next.ambiguous.length > 0) {
        setState("attention");
        onBlocked?.();
        return;
      }
      setState("attention");
      onBlocked?.();
    } catch (requestError) {
      if (version !== requestVersion.current) return;
      setState("error");
      setInterpretation(null);
      setError(requestError instanceof Error ? requestError.message : "The screen could not be completed.");
      onBlocked?.();
    }
  }

  useEffect(() => {
    if (submitPath) router.prefetch(submitPath);
  }, [router, submitPath]);

  useEffect(() => {
    if (!autoRun || autoRunStarted.current || !initialText.trim()) return;
    autoRunStarted.current = true;
    void runQuery(initialText);
    // The initial URL query should run exactly once when this route mounts.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (state !== "loading") void runQuery();
  }

  function keyboardSubmit(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (suggestions.length > 0) {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActiveSuggestion((index) => (index + 1) % suggestions.length);
        return;
      }
      if (event.key === "ArrowUp") {
        event.preventDefault();
        setActiveSuggestion((index) => (index - 1 + suggestions.length) % suggestions.length);
        return;
      }
      if (event.key === "Escape") {
        event.preventDefault();
        setSuggestions([]);
        return;
      }
      if (event.key === "Enter" || event.key === "Tab") {
        event.preventDefault();
        applySuggestionAt(activeSuggestion);
        return;
      }
    }
    if ((event.metaKey || event.ctrlKey) && (event.key === "Enter" || event.key === "NumpadEnter")) {
      event.preventDefault();
      if (state !== "loading") void runQuery();
    }
  }

  function runExample(example: string) {
    setText(example);
    void runQuery(example);
  }

  function chooseMeaning(phrase: string, metricName: string) {
    const replacement = parserPhraseForMetric(metricName);
    const resolved = text.replace(new RegExp(escapeRegExp(phrase), "i"), replacement);
    setText(resolved);
    void runQuery(resolved);
  }

  return (
    <section className="natural-query" aria-labelledby="natural-query-title" hidden={hidden}>
      <div className="natural-query-heading">
        <div>
          <p className="workspace-eyebrow">Company screener</p>
          <h1 className="ds-workspace-title" id="natural-query-title">{title}</h1>
          <p className="natural-query-subtitle">Describe the companies you want to find. Scrooner will translate your words into verifiable financial criteria.</p>
        </div>
      </div>

      <div className="natural-query-workspace">
        <form onSubmit={submit} className="natural-query-form" aria-busy={state === "loading"}>
          <label htmlFor="natural-query-input"><span aria-hidden="true">Query</span><span className="sr-only">Your criteria</span></label>
          <div className="natural-query-input-wrap">
            <textarea
              ref={textareaRef}
              className="ds-control query-composer"
              id="natural-query-input"
              value={text}
              onChange={(event) => changeText(event.target.value, event.target.selectionStart ?? event.target.value.length)}
              onSelect={(event) => updateSuggestions(text, event.currentTarget.selectionStart ?? text.length)}
              onKeyDown={keyboardSubmit}
              onBlur={() => setSuggestions([])}
              placeholder={"ROE above 20% AND\nDebt to equity below 1"}
              rows={7}
              aria-controls="natural-query-suggestions"
              aria-activedescendant={suggestions.length > 0 ? `natural-query-suggestion-${activeSuggestion}` : undefined}
              autoComplete="off"
              aria-invalid={state === "attention" || state === "error"}
              aria-describedby={`natural-query-help${state === "attention" ? " natural-query-attention" : ""}${state === "error" ? " natural-query-error" : ""}`}
            />
            {suggestions.length > 0 && (
              <div className="natural-query-suggestions" id="natural-query-suggestions" role="listbox" aria-label="Matching metrics, operators, and classifications">
                {suggestions.map((suggestion, index) => (
                  <button
                    type="button"
                    key={`${suggestion.kind}:${suggestion.phrase}`}
                    id={`natural-query-suggestion-${index}`}
                    role="option"
                    aria-selected={index === activeSuggestion}
                    className={`natural-query-suggestion${index === activeSuggestion ? " is-active" : ""}`}
                    onMouseEnter={() => setActiveSuggestion(index)}
                    onMouseDown={(event) => event.preventDefault()}
                    onClick={() => applySuggestionAt(index)}
                  >
                    <span>
                      {suggestion.metricNames
                        ? (metricByName(metrics, suggestion.metricNames[0])?.display_name ?? suggestion.phrase)
                        : suggestion.phrase}
                    </span>
                    <span className="natural-query-suggestion-kind">{suggestion.kind}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
          <div className="natural-query-actions">
            <span id="natural-query-help" />
            <Button type="submit" loading={state === "loading"} loadingLabel="Finding matches…">Show matches</Button>
          </div>
        </form>

        <aside className="query-guide" aria-label="Plain-language examples">
          <p className="query-guide-label">Examples</p>
          <div className="query-examples">
            {NATURAL_QUERY_EXAMPLES.slice(0, 3).map((example) => (
              <button className="query-example" key={example} type="button" aria-label={`Run example: ${example}`} disabled={state === "loading"} onClick={() => runExample(example)}>{example}</button>
            ))}
          </div>
        </aside>
      </div>

      {state === "loading" && (
        <StatusPanel className="interpretation-state" title="Finding matching companies" busy>
          <p>Applying your criteria.</p>
        </StatusPanel>
      )}

      {state === "attention" && interpretation && (
        <div id="natural-query-attention" className="interpretation-attention" role="status" aria-live="polite">
          <div className="interpretation-title">
            <span className="status-mark warning" aria-hidden="true">!</span>
            <div><strong>Clarify this screen</strong><p>Choose a meaning to continue.</p></div>
          </div>

          {interpretation.recognized_query && (
            <div className="recognized-partial">
              <h3>What we understood</h3>
              <InterpretationTable query={interpretation.recognized_query} metrics={metrics} partial />
            </div>
          )}

          {interpretation.ambiguous.map((ambiguity) => (
            <div className="unresolved-clause" key={ambiguity.phrase}>
              <span>Choose one meaning</span>
              <strong>“{ambiguity.phrase}”</strong>
              <div className="candidate-list">
                {ambiguity.candidates.map((candidate) => (
                  <button className="choice-button" type="button" key={candidate} onClick={() => chooseMeaning(ambiguity.phrase, candidate)}>
                    {metricByName(metrics, candidate)?.display_name ?? candidate.replaceAll("_", " ")}
                  </button>
                ))}
              </div>
            </div>
          ))}

          {interpretation.unrecognized.map((phrase) => (
            <div className="unresolved-clause" key={phrase}>
              <span>Change this wording</span>
              <strong>“{phrase}”</strong>
              <p>Use a supported financial metric, comparison, range, ranking, or company classification.</p>
            </div>
          ))}
        </div>
      )}

      {state === "error" && (
        <div id="natural-query-error">
          <StatusPanel
            className="interpretation-state"
            tone="negative"
            title="The screen did not run"
            action={<Button type="button" variant="ghost" size="small" onClick={() => void runQuery()}>Try again</Button>}
          >
            <p>{error}</p>
          </StatusPanel>
        </div>
      )}
    </section>
  );
}
