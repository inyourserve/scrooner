"use client";

import { useState, type FormEvent, type KeyboardEvent } from "react";
import { metricByName } from "@/lib/screener/catalog";
import {
  NATURAL_QUERY_EXAMPLES,
  categorySummary,
  parserPhraseForMetric,
  predicateSummary,
} from "@/lib/screener/interpretation";
import type { AskResponse, MetricDefinition, ScreenQueryPayload } from "@/lib/screener/types";

type InterpretState = "idle" | "loading" | "ready" | "attention" | "error";

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
  return "The query could not be interpreted. Try again or use the structured editor.";
}

export function NaturalQueryPanel({
  metrics,
  onApply,
}: {
  metrics: MetricDefinition[];
  onApply: (query: ScreenQueryPayload, sourceText: string) => boolean;
}) {
  const [text, setText] = useState("");
  const [state, setState] = useState<InterpretState>("idle");
  const [interpretation, setInterpretation] = useState<AskResponse | null>(null);
  const [error, setError] = useState("");
  const [applied, setApplied] = useState(false);

  function changeText(next: string) {
    setText(next);
    setInterpretation(null);
    setState("idle");
    setError("");
    setApplied(false);
  }

  async function interpretQuery(nextText = text) {
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

    setState("loading");
    setError("");
    setApplied(false);
    try {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: { "content-type": "application/json", accept: "application/json" },
        body: JSON.stringify({ text: normalized, run: false }),
      });
      const payload: unknown = await response.json();
      if (!response.ok) throw new Error(responseError(payload));
      const result = payload as AskResponse;
      setInterpretation(result);
      setState(result.query && result.unrecognized.length === 0 && result.ambiguous.length === 0 ? "ready" : "attention");
    } catch (requestError) {
      setState("error");
      setInterpretation(null);
      setError(requestError instanceof Error ? requestError.message : "The query could not be interpreted.");
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void interpretQuery();
  }

  function keyboardSubmit(event: KeyboardEvent<HTMLTextAreaElement>) {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      void interpretQuery();
    }
  }

  function chooseMeaning(phrase: string, metricName: string) {
    const replacement = parserPhraseForMetric(metricName);
    const resolved = text.replace(new RegExp(escapeRegExp(phrase), "i"), replacement);
    setText(resolved);
    void interpretQuery(resolved);
  }

  function applyInterpretation() {
    if (!interpretation?.query) return;
    const accepted = onApply(interpretation.query, text.trim());
    if (accepted) {
      setApplied(true);
    } else {
      setState("error");
      setError("This interpretation contains more classification filters than the structured editor can represent. Edit the language and interpret again.");
    }
  }

  return (
    <section className="natural-query" aria-labelledby="natural-query-title">
      <div className="natural-query-heading">
        <div>
          <p className="step-label">Start with plain English</p>
          <h2 id="natural-query-title">Describe the companies you want</h2>
          <p>The interpreter translates supported language into exact criteria. It does not calculate or invent financial data.</p>
        </div>
        <span className="bounded-badge">Bounded parser</span>
      </div>

      <form onSubmit={submit} className="natural-query-form">
        <label htmlFor="natural-query-input">Screening request</label>
        <textarea
          id="natural-query-input"
          value={text}
          onChange={(event) => changeText(event.target.value)}
          onKeyDown={keyboardSubmit}
          placeholder="e.g. companies with ROE above 30%"
          rows={3}
          aria-describedby="natural-query-help"
        />
        <div className="natural-query-actions">
          <p id="natural-query-help">Use a supported example or write a precise request. Press Ctrl/⌘ + Enter to interpret.</p>
          <button type="submit" className="primary-button" disabled={state === "loading"}>
            {state === "loading" ? <><span className="spinner light" aria-hidden="true" /> Checking criteria…</> : "Interpret query"}
          </button>
        </div>
      </form>

      {state === "idle" && (
        <div className="query-examples" aria-label="Supported query examples">
          <span>Try a supported example:</span>
          <div>
            {NATURAL_QUERY_EXAMPLES.map((example) => (
              <button key={example} type="button" onClick={() => changeText(example)}>{example}</button>
            ))}
          </div>
        </div>
      )}

      {state === "loading" && (
        <div className="interpretation-state" aria-live="polite" aria-busy="true">
          <span className="spinner" aria-hidden="true" />
          <div><strong>Checking your criteria</strong><p>No screen will run during interpretation.</p></div>
        </div>
      )}

      {state === "ready" && interpretation?.query && (
        <div className="interpretation-ready" aria-live="polite">
          <div className="interpretation-title">
            <span className="status-mark success" aria-hidden="true">✓</span>
            <div><strong>Ready for your review</strong><p>Every phrase was recognized. Nothing has been executed.</p></div>
          </div>
          <InterpretationTable query={interpretation.query} metrics={metrics} />
          <div className="interpretation-actions">
            <details>
              <summary>View exact interpreted query</summary>
              <pre>{JSON.stringify(interpretation.query, null, 2)}</pre>
            </details>
            <button type="button" className="secondary-button" onClick={applyInterpretation}>
              {applied ? "Criteria added below ✓" : "Review and edit criteria"}
            </button>
          </div>
        </div>
      )}

      {state === "attention" && interpretation && (
        <div className="interpretation-attention" aria-live="polite">
          <div className="interpretation-title">
            <span className="status-mark warning" aria-hidden="true">!</span>
            <div><strong>Resolve the language before running</strong><p>No executable query was created.</p></div>
          </div>

          {interpretation.recognized_query && (
            <div className="recognized-partial">
              <h3>Recognized criteria</h3>
              <InterpretationTable query={interpretation.recognized_query} metrics={metrics} partial />
            </div>
          )}

          {interpretation.ambiguous.map((ambiguity) => (
            <div className="unresolved-clause" key={ambiguity.phrase}>
              <span>Ambiguous phrase</span>
              <strong>“{ambiguity.phrase}”</strong>
              <p>Choose the metric you intended:</p>
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
              <span>Unsupported phrase</span>
              <strong>“{phrase}”</strong>
              <p>Edit the request using a supported metric, comparison, range, ranking, or listed classification.</p>
            </div>
          ))}
        </div>
      )}

      {state === "error" && (
        <div className="interpretation-state error" role="alert">
          <span className="state-icon" aria-hidden="true">!</span>
          <div><strong>Interpretation service unavailable</strong><p>{error}</p><button type="button" className="text-button" onClick={() => void interpretQuery()}>Try again</button></div>
        </div>
      )}
    </section>
  );
}
