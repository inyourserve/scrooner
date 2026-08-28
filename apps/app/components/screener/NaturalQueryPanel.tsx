"use client";

import { useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { metricByName } from "@/lib/screener/catalog";
import {
  NATURAL_QUERY_EXAMPLES,
  categorySummary,
  parserPhraseForMetric,
  predicateSummary,
} from "@/lib/screener/interpretation";
import type { AskResponse, MetricDefinition, ScreenQueryPayload, ScreenResult } from "@/lib/screener/types";
import { Button } from "@/components/ui/Button";
import { StatusPanel } from "@/components/ui/StatusPanel";

type InterpretState = "idle" | "loading" | "complete" | "attention" | "error";

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function InterpretationTable({ query, metrics, partial = false }: {
  query: ScreenQueryPayload;
  metrics: MetricDefinition[];
  partial?: boolean;
}) {
  const categories = categorySummary(query);
  return (
    <div className={`interpretation-table ${partial ? "partial" : ""}`} role="table" aria-label={partial ? "Recognized partial criteria" : "Interpreted criteria"}>
      <div className="interpretation-table-head" role="row">
        <span role="columnheader">Metric or classification</span><span role="columnheader">Operator</span><span role="columnheader">Value</span><span role="columnheader">Period</span>
      </div>
      {query.metric_predicates.map((predicate, index) => {
        const summary = predicateSummary(predicate, metrics);
        return (
          <div className="interpretation-row" role="row" key={`${predicate.metric_name}-${index}`}>
            <strong role="cell">{summary.metric}</strong>
            <span role="cell">{summary.operator}</span>
            <span role="cell">{summary.value}</span>
            <span role="cell">Latest available</span>
          </div>
        );
      })}
      {categories.map((label) => (
        <div className="interpretation-row" role="row" key={label}>
          <strong role="cell">{label}</strong><span role="cell">Equal to</span><span role="cell">Selected class</span><span role="cell">Current company status</span>
        </div>
      ))}
      <div className="interpretation-settings" role="row">
        <span role="cell"><strong>Sort</strong> {query.sort_by ? metricByName(metrics, query.sort_by)?.display_name ?? query.sort_by : "Deterministic default"}</span>
        <span role="cell"><strong>Direction</strong> {query.sort_desc ? "Highest first" : "Lowest first"}</span>
        <span role="cell"><strong>Limit</strong> {query.limit ?? "No explicit limit"}</span>
        <span role="cell"><strong>Universe</strong> {query.include_inactive ? "Active and inactive" : "Active companies"}</span>
      </div>
    </div>
  );
}

function responseError(payload: unknown): string {
  if (payload && typeof payload === "object" && "detail" in payload && typeof payload.detail === "string") {
    return payload.detail;
  }
  return "The screen could not be completed. Try again or use the filter editor.";
}

export function NaturalQueryPanel({
  metrics,
  onResult,
  onEdit,
}: {
  metrics: MetricDefinition[];
  onResult: (query: ScreenQueryPayload, result: ScreenResult, sourceText: string) => boolean;
  onEdit: (query: ScreenQueryPayload, sourceText: string) => boolean;
}) {
  const [text, setText] = useState("");
  const [state, setState] = useState<InterpretState>("idle");
  const [interpretation, setInterpretation] = useState<AskResponse | null>(null);
  const [error, setError] = useState("");
  const [filtersOpened, setFiltersOpened] = useState(false);
  const requestVersion = useRef(0);

  function changeText(next: string) {
    requestVersion.current += 1;
    setText(next);
    setInterpretation(null);
    setState("idle");
    setError("");
    setFiltersOpened(false);
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
      return;
    }

    const version = ++requestVersion.current;
    setState("loading");
    setError("");
    setFiltersOpened(false);
    try {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: { "content-type": "application/json", accept: "application/json" },
        body: JSON.stringify({ text: normalized, run: true }),
      });
      const payload: unknown = await response.json().catch(() => null);
      if (version !== requestVersion.current) return;
      if (!response.ok) throw new Error(responseError(payload));
      const next = payload as AskResponse;
      setInterpretation(next);

      if (!next.query || next.unrecognized.length > 0 || next.ambiguous.length > 0) {
        setState("attention");
        return;
      }
      if (!next.result) throw new Error("The screen service returned no results. Please try again.");
      if (!onResult(next.query, next.result, normalized)) {
        throw new Error("This screen contains more classification filters than the editor can represent.");
      }
      setState("complete");
    } catch (requestError) {
      if (version !== requestVersion.current) return;
      setState("error");
      setInterpretation(null);
      setError(requestError instanceof Error ? requestError.message : "The screen could not be completed.");
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (state !== "loading") void runQuery();
  }

  function keyboardSubmit(event: KeyboardEvent<HTMLTextAreaElement>) {
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

  function editFilters() {
    if (!interpretation?.query) return;
    if (onEdit(interpretation.query, text.trim())) {
      setFiltersOpened(true);
      return;
    }
    setState("error");
    setError("This screen contains more classification filters than the editor can represent. Edit the wording and try again.");
  }

  const completedQuery = state === "complete" ? interpretation?.query : null;

  return (
    <section className={`natural-query ${completedQuery ? "complete" : ""}`} aria-labelledby="natural-query-title">
      {completedQuery ? (
        <div className="screen-summary" aria-live="polite">
          <div className="screen-summary-main">
            <p className="step-label">Current screen</p>
            <h2 id="natural-query-title">{text}</h2>
            <div className="criteria-chips" aria-label="Criteria used">
              {completedQuery.metric_predicates.map((predicate, index) => {
                const summary = predicateSummary(predicate, metrics);
                return <span key={`${predicate.metric_name}-${index}`}><strong>{summary.metric}</strong> {summary.operator.toLowerCase()} {summary.value}</span>;
              })}
              {categorySummary(completedQuery).map((label) => <span key={label}><strong>{label}</strong></span>)}
            </div>
          </div>
          <div className="screen-summary-actions">
            <Button type="button" variant="ghost" className="tertiary-button" onClick={() => setState("idle")}>Edit wording</Button>
            <Button type="button" variant="secondary" className="secondary-button" onClick={editFilters}>
              {filtersOpened ? "Filters opened ✓" : "Edit filters"}
            </Button>
          </div>
          <details className="verify-screen">
            <summary>Verify how Scrooner understood this</summary>
            <InterpretationTable query={completedQuery} metrics={metrics} />
          </details>
        </div>
      ) : (
        <>
          <div className="natural-query-heading">
            <div>
              <p className="step-label">Start in your own words</p>
              <h2 id="natural-query-title">What companies are you looking for?</h2>
              <p>Describe the companies you want. One click turns your words into exact filters and shows the matches.</p>
            </div>
          </div>

          <div className="natural-query-workspace">
            <form onSubmit={submit} className="natural-query-form" aria-busy={state === "loading"}>
              <label htmlFor="natural-query-input">Describe your screen</label>
              <textarea
                id="natural-query-input"
                value={text}
                onChange={(event) => changeText(event.target.value)}
                onKeyDown={keyboardSubmit}
                placeholder="Companies with ROE above 20% and debt to equity below 1"
                rows={5}
                aria-invalid={state === "attention" || state === "error"}
                aria-describedby={`natural-query-help${state === "attention" ? " natural-query-attention" : ""}${state === "error" ? " natural-query-error" : ""}`}
              />
              <div className="natural-query-actions">
                <p id="natural-query-help">If a phrase has more than one meaning, we will ask before running it.</p>
                <Button type="submit" className="primary-button" disabled={state === "loading"}>
                  {state === "loading" ? <><span className="spinner light" aria-hidden="true" /> Finding matches…</> : "Show matches"}
                </Button>
              </div>
            </form>

            <aside className="query-guide" aria-label="Plain-language examples">
              <p className="query-guide-label">Run an example</p>
              <div className="query-examples">
                {NATURAL_QUERY_EXAMPLES.slice(0, 3).map((example) => (
                  <button key={example} type="button" aria-label={`Run example: ${example}`} disabled={state === "loading"} onClick={() => runExample(example)}>{example}</button>
                ))}
              </div>
              <p className="query-guide-note"><span aria-hidden="true">✓</span> Click an example to see its matches immediately.</p>
            </aside>
          </div>
        </>
      )}

      {state === "loading" && (
        <StatusPanel className="interpretation-state" title="Finding matching companies" busy>
          <p>Interpreting your words and applying the verified filters.</p>
        </StatusPanel>
      )}

      {state === "attention" && interpretation && (
        <div id="natural-query-attention" className="interpretation-attention" role="status" aria-live="polite">
          <div className="interpretation-title">
            <span className="status-mark warning" aria-hidden="true">!</span>
            <div><strong>Clarify this screen</strong><p>Nothing ran because part of the request needs your input.</p></div>
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
              <p>Which metric did you mean?</p>
              <div className="candidate-list">
                {ambiguity.candidates.map((candidate) => (
                  <button type="button" key={candidate} onClick={() => chooseMeaning(ambiguity.phrase, candidate)}>
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
            action={<button type="button" className="text-button" onClick={() => void runQuery()}>Try again</button>}
          >
            <p>{error}</p>
          </StatusPanel>
        </div>
      )}
    </section>
  );
}
