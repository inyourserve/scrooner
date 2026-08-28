"use client";

import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import {
  OPERATOR_LABELS,
  REFERENCE_SCREENS,
  SIC_OPTIONS,
  metricByName,
  type ReferenceScreen,
} from "@/lib/screener/catalog";
import { formatMetricValue, metricPeriod } from "@/lib/screener/format";
import { predicateSummary, queryToBuilderState } from "@/lib/screener/interpretation";
import { buildScreenQuery } from "@/lib/screener/query";
import type {
  CategoryFilter,
  FilterRow,
  MatchedCompany,
  MetricDefinition,
  MetricOperator,
  ScreenQueryPayload,
  ScreenResult,
} from "@/lib/screener/types";
import { NaturalQueryPanel } from "./NaturalQueryPanel";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/layout/PageHeader";
import { StatusPanel } from "@/components/ui/StatusPanel";
import { SaveScreenButton } from "@/components/saved-screens/SaveScreenButton";
import { SAVED_QUERY_KEY } from "@/lib/saved-screens/client";

const DEFAULT_ROW: FilterRow = {
  id: "filter-1",
  metricName: "roe",
  operator: ">",
  value: "30",
  highValue: "",
};

const EMPTY_CATEGORY: CategoryFilter = { enabled: false, field: "sic_code", value: "" };

type RequestState = "idle" | "loading" | "success" | "error";

function unitLabel(metric?: MetricDefinition) {
  if (metric?.value_type === "percentage") return "%";
  if (metric?.value_type === "currency") return "USD";
  if (metric?.value_type === "multiple") return "x";
  return "";
}

function errorDetail(payload: unknown, fallback: string) {
  if (!payload || typeof payload !== "object") return fallback;
  const detail = (payload as { detail?: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => (item && typeof item === "object" && "msg" in item ? String(item.msg) : ""))
      .filter(Boolean)
      .join(" ");
  }
  return fallback;
}

async function requestMetricCatalog(): Promise<MetricDefinition[]> {
  const response = await fetch("/api/metrics", { headers: { accept: "application/json" } });
  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) throw new Error(errorDetail(payload, "Metric definitions could not be loaded."));
  if (!Array.isArray(payload) || payload.length === 0) throw new Error("No screenable metrics are currently available.");
  return payload as MetricDefinition[];
}

function MatchReasons({
  company,
  query,
  metrics,
  siteUrl,
}: {
  company: MatchedCompany;
  query: ScreenQueryPayload;
  metrics: MetricDefinition[];
  siteUrl: string;
}) {
  return (
    <details className="match-reasons">
      <summary>Why matched</summary>
      <ul>
        {query.metric_predicates.map((predicate, index) => {
          const definition = metricByName(metrics, predicate.metric_name);
          const summary = predicateSummary(predicate, metrics);
          const actual = company.metrics[predicate.metric_name];
          return (
            <li key={`${predicate.metric_name}-${index}`}>
              <span><strong>{summary.metric}</strong> · {summary.operator} {summary.value}</span>
              {actual && <small>Matched at {formatMetricValue(actual.value, definition)} · {metricPeriod(actual)} · formula v{actual.formula_version}</small>}
            </li>
          );
        })}
        {query.categorical_predicates.map((predicate, index) => (
          <li key={`${predicate.field}-${index}`}>
            <span><strong>Company classification</strong> · {predicate.field} = {predicate.value}</span>
            <small>Matched company SIC {company.sic_code ?? "not available"}</small>
          </li>
        ))}
      </ul>
      {company.ticker && <a href={`${siteUrl}/stock/${company.ticker.toLowerCase()}/`}>Open company filings and source context<span aria-hidden="true"> →</span></a>}
    </details>
  );
}

export function ScreenerClient({ siteUrl }: { siteUrl: string }) {
  const nextId = useRef(2);
  const builderSectionRef = useRef<HTMLElement>(null);
  const resultsTitleRef = useRef<HTMLHeadingElement>(null);
  const screenRequestVersion = useRef(0);
  const [metrics, setMetrics] = useState<MetricDefinition[]>([]);
  const [catalogState, setCatalogState] = useState<RequestState>("loading");
  const [catalogError, setCatalogError] = useState("");
  const [rows, setRows] = useState<FilterRow[]>([DEFAULT_ROW]);
  const [category, setCategory] = useState<CategoryFilter>(EMPTY_CATEGORY);
  const [sortBy, setSortBy] = useState("roe");
  const [sortDesc, setSortDesc] = useState(true);
  const [limit, setLimit] = useState("50");
  const [includeInactive, setIncludeInactive] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [requestError, setRequestError] = useState("");
  const [result, setResult] = useState<ScreenResult | null>(null);
  const [lastQuery, setLastQuery] = useState<ScreenQueryPayload | null>(null);
  const [interpretedFrom, setInterpretedFrom] = useState("");
  const [builderOpen, setBuilderOpen] = useState(false);

  useEffect(() => {
    let active = true;
    void requestMetricCatalog()
      .then((catalog) => {
        if (!active) return;
        setMetrics(catalog);
        setCatalogState("success");
      })
      .catch((error: unknown) => {
        if (!active) return;
        setCatalogState("error");
        setCatalogError(error instanceof Error ? error.message : "Metric definitions could not be loaded.");
      });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (catalogState !== "success") return;
    const stored = window.sessionStorage.getItem(SAVED_QUERY_KEY);
    if (!stored) return;
    window.sessionStorage.removeItem(SAVED_QUERY_KEY);
    try {
      const query = JSON.parse(stored) as ScreenQueryPayload;
      if (applyInterpretedQuery(query, "Saved screen")) void executeScreen(query);
    } catch { /* Ignore malformed browser state. */ }
  // apply once after the catalog makes query-to-builder mapping possible
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [catalogState]);

  useEffect(() => {
    if (requestState === "success" || requestState === "error") {
      resultsTitleRef.current?.focus({ preventScroll: true });
    }
  }, [requestState]);

  function retryCatalog() {
    setCatalogState("loading");
    setCatalogError("");
    void requestMetricCatalog()
      .then((catalog) => {
        setMetrics(catalog);
        setCatalogState("success");
      })
      .catch((error: unknown) => {
        setCatalogState("error");
        setCatalogError(error instanceof Error ? error.message : "Metric definitions could not be loaded.");
      });
  }

  const categories = useMemo(() => {
    const grouped = new Map<string, MetricDefinition[]>();
    for (const metric of metrics) {
      const existing = grouped.get(metric.category) ?? [];
      existing.push(metric);
      grouped.set(metric.category, existing);
    }
    return [...grouped.entries()];
  }, [metrics]);

  const resultMetricNames = useMemo(() => {
    if (!lastQuery) return [];
    const names = lastQuery.metric_predicates.map((predicate) => predicate.metric_name);
    if (lastQuery.sort_by) names.push(lastQuery.sort_by);
    return [...new Set(names)];
  }, [lastQuery]);

  function createRow(seed?: Partial<FilterRow>): FilterRow {
    const firstMetric = metrics[0]?.metric_name ?? "roe";
    return {
      id: `filter-${nextId.current++}`,
      metricName: seed?.metricName ?? firstMetric,
      operator: seed?.operator ?? ">",
      value: seed?.value ?? "",
      highValue: seed?.highValue ?? "",
    };
  }

  function updateRow(id: string, patch: Partial<FilterRow>) {
    setRows((current) => current.map((row) => (row.id === id ? { ...row, ...patch } : row)));
    setErrors((current) => {
      if (!current[id] && !current.form) return current;
      const next = { ...current };
      delete next[id];
      delete next.form;
      return next;
    });
  }

  function changeMetric(row: FilterRow, metricName: string) {
    const definition = metricByName(metrics, metricName);
    const operator = definition?.operators.includes(row.operator) ? row.operator : (definition?.operators[0] ?? ">" as MetricOperator);
    updateRow(row.id, { metricName, operator, value: "", highValue: "" });
  }

  function applyReference(screen: ReferenceScreen) {
    screenRequestVersion.current += 1;
    setRows(screen.rows.map((row) => createRow(row)));
    setCategory({ ...screen.category });
    setSortBy(screen.sortBy);
    setSortDesc(screen.sortDesc);
    setLimit(screen.limit);
    setIncludeInactive(false);
    setErrors({});
    setRequestError("");
    setRequestState("idle");
    setResult(null);
    setLastQuery(null);
    setInterpretedFrom("");
    setBuilderOpen(true);
  }

  function applyInterpretedQuery(query: ScreenQueryPayload, sourceText: string): boolean {
    const state = queryToBuilderState(query, metrics, () => `filter-${nextId.current++}`);
    if (!state) return false;
    setRows(state.rows);
    setCategory(state.category);
    setSortBy(state.sortBy);
    setSortDesc(state.sortDesc);
    setLimit(state.limit);
    setIncludeInactive(state.includeInactive);
    setErrors({});
    setRequestError("");
    setInterpretedFrom(sourceText);
    setBuilderOpen(true);
    window.setTimeout(() => builderSectionRef.current?.scrollIntoView?.({ behavior: "smooth", block: "start" }), 0);
    return true;
  }

  function acceptInterpretedResult(query: ScreenQueryPayload, nextResult: ScreenResult, sourceText: string): boolean {
    const state = queryToBuilderState(query, metrics, () => `filter-${nextId.current++}`);
    if (!state) return false;
    screenRequestVersion.current += 1;
    setRows(state.rows);
    setCategory(state.category);
    setSortBy(state.sortBy);
    setSortDesc(state.sortDesc);
    setLimit(state.limit);
    setIncludeInactive(state.includeInactive);
    setErrors({});
    setRequestError("");
    setInterpretedFrom(sourceText);
    setLastQuery(query);
    setResult(nextResult);
    setRequestState("success");
    setBuilderOpen(false);
    return true;
  }

  function resetScreen() {
    screenRequestVersion.current += 1;
    setRows([{ ...DEFAULT_ROW, id: createRow().id }]);
    setCategory({ ...EMPTY_CATEGORY });
    setSortBy("roe");
    setSortDesc(true);
    setLimit("50");
    setIncludeInactive(false);
    setErrors({});
    setRequestError("");
    setRequestState("idle");
    setResult(null);
    setLastQuery(null);
    setInterpretedFrom("");
  }

  async function executeScreen(query: ScreenQueryPayload) {
    const version = ++screenRequestVersion.current;
    setRequestError("");
    setRequestState("loading");
    setLastQuery(query);
    try {
      const response = await fetch("/api/screen", {
        method: "POST",
        headers: { "content-type": "application/json", accept: "application/json" },
        body: JSON.stringify(query),
      });
      const payload: unknown = await response.json().catch(() => null);
      if (version !== screenRequestVersion.current) return;
      if (!response.ok) throw new Error(errorDetail(payload, "The screen could not be completed."));
      if (!payload || typeof payload !== "object") throw new Error("The screening service returned an invalid response. Please try again.");
      setResult(payload as ScreenResult);
      setRequestState("success");
    } catch (error) {
      if (version !== screenRequestVersion.current) return;
      setResult(null);
      setRequestState("error");
      setRequestError(error instanceof Error ? error.message : "The screen could not be completed.");
    }
  }

  async function runScreen(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (requestState === "loading") return;
    const built = buildScreenQuery({ rows, category, sortBy, sortDesc, limit, includeInactive, metrics });
    setErrors(built.errors);
    setRequestError("");
    if (!built.query) {
      setRequestState("idle");
      window.setTimeout(() => {
        const target = builderSectionRef.current?.querySelector<HTMLElement>('[aria-invalid="true"], .validation-summary');
        target?.focus();
      }, 0);
      return;
    }
    await executeScreen(built.query);
  }

  return (
    <main className="main-content screener-content" id="main-content">
        <PageHeader
          eyebrow="Stock screener"
          title="Find companies"
          description="Describe the companies you want in plain language and see matching results in one step."
        />

        {catalogState === "loading" && (
          <StatusPanel className="state-panel" title="Loading metric definitions" busy>
            <p>Checking the Screener&apos;s current validated catalog.</p>
          </StatusPanel>
        )}

        {catalogState === "error" && (
          <StatusPanel
            className="state-panel"
            tone="negative"
            title="Metric definitions are unavailable"
            action={<button type="button" className="text-button" onClick={retryCatalog}>Try again</button>}
          >
            <p>{catalogError}</p>
          </StatusPanel>
        )}

        {catalogState === "success" && (
          <>
          <NaturalQueryPanel metrics={metrics} onResult={acceptInterpretedResult} onEdit={applyInterpretedQuery} />

          {requestState !== "idle" && <section className="results-section" aria-labelledby="results-title" aria-busy={requestState === "loading"}>
            <div className="results-heading">
              <div>
                <p className="step-label">Screen results</p>
                <h2 ref={resultsTitleRef} id="results-title" tabIndex={-1}>Matching companies</h2>
              </div>
              {requestState === "success" && result && <p className="match-count"><strong>{result.matched.length}</strong> {result.matched.length === 1 ? "company" : "companies"} matched</p>}
              {requestState === "success" && lastQuery && <SaveScreenButton query={lastQuery} />}
            </div>

            {requestState === "loading" && (
              <StatusPanel className="state-panel" title="Running your screen" busy>
                <p>Evaluating every condition against available company metrics.</p>
              </StatusPanel>
            )}

            {requestState === "error" && (
              <StatusPanel
                className="state-panel"
                tone="negative"
                title="The screen did not run"
                action={lastQuery ? <button type="button" className="text-button" onClick={() => void executeScreen(lastQuery)}>Try again</button> : undefined}
              >
                <p>{requestError}</p><p>Your criteria are preserved below.</p>
              </StatusPanel>
            )}

            {requestState === "success" && result && result.matched.length === 0 && (
              <div className="empty-results zero-results">
                <span className="empty-mark" aria-hidden="true">0</span>
                <h3>No companies matched every criterion</h3>
                <p>The screen ran successfully. Edit or remove a condition to widen the result.</p>
                <Button type="button" variant="secondary" className="secondary-button" onClick={() => lastQuery && applyInterpretedQuery(lastQuery, interpretedFrom)}>Edit criteria</Button>
              </div>
            )}

            {requestState === "success" && result && result.excluded_missing_data.length > 0 && (
              <details className="coverage-panel">
                <summary>
                  <span className="coverage-icon" aria-hidden="true">i</span>
                  <span><strong>{result.excluded_missing_data.length} {result.excluded_missing_data.length === 1 ? "company was" : "companies were"} excluded for missing data</strong><small>Missing data is not treated as a failed financial criterion.</small></span>
                </summary>
                <div className="coverage-detail">
                  {result.excluded_missing_data.map((company) => (
                    <p key={company.cik}><strong>{company.company_name}</strong><span>{company.missing_metrics.map((name) => metricByName(metrics, name)?.display_name ?? name).join(", ")}</span></p>
                  ))}
                </div>
              </details>
            )}

            {requestState === "success" && result && result.matched.length > 0 && (
              <div className="results-table-wrap" tabIndex={0} aria-label="Screen results. Scroll horizontally to view all metrics.">
                <table className="results-table">
                  <caption className="sr-only">Companies matching the current screen, in backend-determined order.</caption>
                  <thead>
                    <tr>
                      <th scope="col">Company</th>
                      <th scope="col">Classification</th>
                      {resultMetricNames.map((metricName) => <th scope="col" key={metricName}><a className="metric-heading-link" href={`#definition-${metricName}`}>{metricByName(metrics, metricName)?.display_name ?? metricName}</a></th>)}
                      <th scope="col"><span className="sr-only">Actions</span></th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.matched.map((company) => (
                      <tr key={company.cik}>
                        <th scope="row">
                          {company.ticker ? <a className="company-link" aria-label={`${company.ticker} ${company.company_name}`} href={`${siteUrl}/stock/${company.ticker.toLowerCase()}/`}><strong>{company.ticker}</strong><span>{company.company_name}</span></a> : <span className="company-link"><strong>—</strong><span>{company.company_name}</span></span>}
                          {lastQuery && <MatchReasons company={company} query={lastQuery} metrics={metrics} siteUrl={siteUrl} />}
                        </th>
                        <td><span className="classification">{company.sic_description || "Unclassified"}</span>{company.sic_code && <small>SIC {company.sic_code}</small>}</td>
                        {resultMetricNames.map((metricName) => {
                          const value = company.metrics[metricName];
                          const definition = metricByName(metrics, metricName);
                          return (
                            <td key={metricName}>
                              {value ? <><span className="metric-value" title={`Exact value: ${value.value}`}>{formatMetricValue(value.value, definition)}</span><small>{metricPeriod(value)} · v{value.formula_version}</small></> : <><span className="metric-value missing" aria-label="Not available">—</span><small>Not available</small></>}
                            </td>
                          );
                        })}
                        <td>{company.ticker && <a className="row-action" href={`${siteUrl}/stock/${company.ticker.toLowerCase()}/`}>View company<span aria-hidden="true"> →</span></a>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {requestState === "success" && result && resultMetricNames.length > 0 && (
              <section className="result-definitions" aria-labelledby="result-definitions-title">
                <h3 id="result-definitions-title">Metric definitions used</h3>
                <p>These definitions describe the current calculation contract. Each result cell shows the formula version actually used.</p>
                <div>
                  {resultMetricNames.map((metricName) => {
                    const definition = metricByName(metrics, metricName);
                    return (
                      <details id={`definition-${metricName}`} key={metricName}>
                        <summary>{definition?.display_name ?? metricName}</summary>
                        <p>{definition?.short_definition ?? "Defined Scrooner metric."}</p>
                        <dl>
                          <div><dt>Formula</dt><dd>{definition?.formula_description ?? "See current metric catalog."}</dd></div>
                          <div><dt>Current version</dt><dd>v{definition?.formula_version ?? "—"}</dd></div>
                        </dl>
                      </details>
                    );
                  })}
                </div>
              </section>
            )}

            {lastQuery && (
              <details className="query-contract">
                <summary>View exact query sent to the Screener</summary>
                <pre>{JSON.stringify(lastQuery, null, 2)}</pre>
              </details>
            )}
          </section>}

          <section ref={builderSectionRef} className="advanced-builder" aria-labelledby="advanced-builder-title">
            <button
              type="button"
              className="builder-disclosure"
              aria-expanded={builderOpen}
              aria-controls="advanced-builder-content"
              onClick={() => setBuilderOpen((open) => !open)}
            >
              <span className="builder-disclosure-icon" aria-hidden="true">⌁</span>
              <span><strong id="advanced-builder-title">Build with filters</strong><small>Choose financial metrics, comparisons, and sorting yourself.</small></span>
              <span className="builder-disclosure-action">{builderOpen ? "Hide" : "Open"}<span aria-hidden="true"> {builderOpen ? "↑" : "↓"}</span></span>
            </button>

            {builderOpen && (
            <div id="advanced-builder-content" className="advanced-builder-content">
              <section className="reference-section" aria-labelledby="reference-title">
                <div className="section-heading compact">
                  <div>
                    <h2 id="reference-title">Start from an example</h2>
                    <p>Load a ready-made screen, then change any filter.</p>
                  </div>
                </div>
                <div className="reference-list">
                  {REFERENCE_SCREENS.map((screen) => (
                    <button key={screen.id} type="button" className="reference-button" onClick={() => applyReference(screen)}>
                      <strong>{screen.label}</strong>
                      <span>{screen.description}</span>
                    </button>
                  ))}
                </div>
              </section>

              {interpretedFrom && (
                <div className="interpretation-applied" role="status">
                  <span aria-hidden="true">✓</span>
                  <p><strong>Your words are now editable filters</strong><small>From: “{interpretedFrom}” · Change anything below, then run the screen.</small></p>
                </div>
              )}

              <form id="structured-builder" className="builder" onSubmit={runScreen} noValidate>
            <div className="builder-header">
              <div>
                <p className="step-label">Step 1</p>
                <h2>Define your criteria</h2>
                <p>All conditions are combined with AND. Missing values never pass a condition.</p>
              </div>
              <Button type="button" variant="ghost" className="tertiary-button" onClick={resetScreen}>Reset</Button>
            </div>

            <fieldset className="criteria-fieldset">
              <legend className="sr-only">Metric conditions</legend>
              <div className="criteria-labels" aria-hidden="true">
                <span>Metric</span><span>Operator</span><span>Value</span><span />
              </div>
              {rows.map((row, index) => {
                const metric = metricByName(metrics, row.metricName);
                const ranked = row.operator === "top_n" || row.operator === "bottom_n";
                const between = row.operator === "between";
                return (
                  <div className="filter-group" key={row.id}>
                    <div className="filter-index" aria-hidden="true">{index + 1}</div>
                    <div className="filter-control metric-control">
                      <label className="sr-only" htmlFor={`${row.id}-metric`}>Metric for condition {index + 1}</label>
                      <select id={`${row.id}-metric`} value={row.metricName} onChange={(event) => changeMetric(row, event.target.value)}>
                        {categories.map(([categoryName, definitions]) => (
                          <optgroup label={categoryName} key={categoryName}>
                            {definitions.map((definition) => <option key={definition.metric_name} value={definition.metric_name}>{definition.display_name}</option>)}
                          </optgroup>
                        ))}
                      </select>
                      {metric && <span className="field-help">{metric.short_definition}</span>}
                    </div>
                    <div className="filter-control">
                      <label className="sr-only" htmlFor={`${row.id}-operator`}>Operator for condition {index + 1}</label>
                      <select id={`${row.id}-operator`} value={row.operator} onChange={(event) => updateRow(row.id, { operator: event.target.value as MetricOperator, value: "", highValue: "" })}>
                        {metric?.operators.map((operator) => <option value={operator} key={operator}>{OPERATOR_LABELS[operator]}</option>)}
                      </select>
                    </div>
                    <div className={`filter-control value-control ${between ? "range" : ""}`}>
                      <label className="sr-only" htmlFor={`${row.id}-value`}>{ranked ? "Number of companies" : "Value"} for condition {index + 1}</label>
                      <div className="input-with-unit">
                        <input
                          id={`${row.id}-value`}
                          inputMode={ranked ? "numeric" : "decimal"}
                          value={row.value}
                          onChange={(event) => updateRow(row.id, { value: event.target.value })}
                          aria-invalid={Boolean(errors[row.id])}
                          aria-describedby={errors[row.id] ? `${row.id}-error` : undefined}
                          placeholder={ranked ? "10" : "0"}
                        />
                        {!ranked && unitLabel(metric) && <span className="unit">{unitLabel(metric)}</span>}
                      </div>
                      {between && (
                        <>
                          <span className="range-separator">to</span>
                          <label className="sr-only" htmlFor={`${row.id}-high-value`}>Upper value for condition {index + 1}</label>
                          <div className="input-with-unit">
                            <input id={`${row.id}-high-value`} inputMode="decimal" value={row.highValue} onChange={(event) => updateRow(row.id, { highValue: event.target.value })} aria-invalid={Boolean(errors[row.id])} aria-describedby={errors[row.id] ? `${row.id}-error` : undefined} placeholder="1" />
                            {unitLabel(metric) && <span className="unit">{unitLabel(metric)}</span>}
                          </div>
                        </>
                      )}
                    </div>
                    <button type="button" className="icon-button" aria-label={`Remove condition ${index + 1}`} onClick={() => setRows((current) => current.filter((candidate) => candidate.id !== row.id))}>
                      <span aria-hidden="true">×</span>
                    </button>
                    {errors[row.id] && <p className="field-error" id={`${row.id}-error`}>{errors[row.id]}</p>}
                  </div>
                );
              })}
              <button type="button" className="add-condition" onClick={() => setRows((current) => [...current, createRow()])}>
                <span aria-hidden="true">+</span> Add condition
              </button>
            </fieldset>

            <div className="classification-row">
              <label className="check-label">
                <input type="checkbox" checked={category.enabled} onChange={(event) => setCategory((current) => ({ ...current, enabled: event.target.checked }))} />
                <span>Filter by company classification</span>
              </label>
              {category.enabled && (
                <div className="inline-field">
                  <label htmlFor="classification">Classification</label>
                  <select id="classification" value={category.value} onChange={(event) => { setCategory((current) => ({ ...current, value: event.target.value })); setErrors((current) => ({ ...current, category: "" })); }} aria-invalid={Boolean(errors.category)} aria-describedby={errors.category ? "category-error" : undefined}>
                    <option value="">Choose classification</option>
                    {SIC_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label} · SIC {option.value}</option>)}
                  </select>
                  {errors.category && <p className="field-error" id="category-error">{errors.category}</p>}
                </div>
              )}
            </div>

            <div className="run-settings">
              <div className="setting-field sort-field">
                <label htmlFor="sort-by">Sort results by</label>
                <select id="sort-by" value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
                  <option value="">Default deterministic order</option>
                  {categories.map(([categoryName, definitions]) => (
                    <optgroup label={categoryName} key={categoryName}>
                      {definitions.map((definition) => <option key={definition.metric_name} value={definition.metric_name}>{definition.display_name}</option>)}
                    </optgroup>
                  ))}
                </select>
              </div>
              <div className="setting-field direction-field">
                <label htmlFor="sort-direction">Direction</label>
                <select id="sort-direction" value={sortDesc ? "desc" : "asc"} onChange={(event) => setSortDesc(event.target.value === "desc")} disabled={!sortBy}>
                  <option value="desc">Highest first</option>
                  <option value="asc">Lowest first</option>
                </select>
              </div>
              <div className="setting-field limit-field">
                <label htmlFor="result-limit">Result limit</label>
                <input id="result-limit" inputMode="numeric" value={limit} onChange={(event) => { setLimit(event.target.value); setErrors((current) => ({ ...current, limit: "" })); }} aria-invalid={Boolean(errors.limit)} aria-describedby={errors.limit ? "limit-error" : undefined} />
                {errors.limit && <p className="field-error" id="limit-error">{errors.limit}</p>}
              </div>
              <label className="check-label inactive-check">
                <input type="checkbox" checked={includeInactive} onChange={(event) => setIncludeInactive(event.target.checked)} />
                <span>Include inactive companies</span>
              </label>
            </div>

            {errors.form && <div className="validation-summary" role="alert" tabIndex={-1}><strong>Review the screen</strong><span>{errors.form}</span></div>}
            {errors.sort && <div className="validation-summary" role="alert" tabIndex={-1}><strong>Review sorting</strong><span>{errors.sort}</span></div>}

            <div className="builder-actions">
              <p><strong>{rows.length + (category.enabled ? 1 : 0)}</strong> active {rows.length + (category.enabled ? 1 : 0) === 1 ? "criterion" : "criteria"}</p>
              <Button className="primary-button" type="submit" disabled={requestState === "loading"}>
                {requestState === "loading" ? <><span className="spinner light" aria-hidden="true" /> Running screen…</> : "Run screen"}
              </Button>
            </div>
              </form>
            </div>
            )}
          </section>
          </>
        )}

    </main>
  );
}
