"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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
import { collectMetricNames, DEFAULT_COMPARISON_METRICS } from "@/lib/screener/types";
import { NaturalQueryPanel } from "./NaturalQueryPanel";
import { Button } from "@/components/ui/Button";
import { IconButton } from "@/components/ui/IconButton";
import { StatusPanel } from "@/components/ui/StatusPanel";
import { SaveScreenButton } from "@/components/saved-screens/SaveScreenButton";
import { EmptyState } from "@/components/scrooner/EmptyState";
import { TableSkeleton } from "@/components/scrooner/TableSkeleton";
import { cacheRunPageForNavigation, readNavigationRunPage, readPendingRun, savedScreensApi } from "@/lib/saved-screens/client";
import type { ScreenRunPage } from "@/lib/saved-screens/types";

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
  // A `where` (AND/OR/NOT) query has no single "you matched because X"
  // story the way a flat AND list does -- a company excluded by one
  // branch can still match via another, the same reason query.py's own
  // `exclusion_detail` gives up on precise attribution for these. Rather
  // than render nothing (query.metric_predicates/categorical_predicates
  // are empty for a where-tree query, per the backend's own schema),
  // show every metric the query actually referenced and this company's
  // real value for it -- less precise than "matched at X > Y", but still
  // real, traceable data, not silence.
  const combined = Boolean(query.where);
  return (
    <details className="match-reasons">
      <summary>Why matched</summary>
      <ul>
        {combined && <li className="match-reasons-note"><small>Matched a combined AND/OR/NOT filter -- showing this company&apos;s value for every metric the filter referenced.</small></li>}
        {combined
          ? collectMetricNames(query).map((metricName) => {
              const definition = metricByName(metrics, metricName);
              const actual = company.metrics[metricName];
              return (
                <li key={metricName}>
                  <span><strong>{definition?.display_name ?? metricName}</strong></span>
                  {actual && <small>Value: {formatMetricValue(actual.value, definition)} · {metricPeriod(actual)} · formula v{actual.formula_version}</small>}
                </li>
              );
            })
          : query.metric_predicates.map((predicate, index) => {
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
        {!combined && query.categorical_predicates.map((predicate, index) => (
          <li key={`${predicate.field}-${index}`}>
            <span><strong>Company classification</strong> · {predicate.field} = {predicate.value}</span>
            <small>Matched company SIC {company.sic_code ?? "not available"}</small>
          </li>
        ))}
      </ul>
      {company.ticker && <a href={`${siteUrl}/stocks/${company.ticker.toLowerCase()}/`}>Open company filings and source context<span aria-hidden="true"> →</span></a>}
    </details>
  );
}

export function ScreenerClient({
  siteUrl,
  initialMetrics = [],
  autoRunInitialQuery = false,
  routePath = "/app/screens/new",
  resultsFirst = false,
}: {
  siteUrl: string;
  initialMetrics?: MetricDefinition[];
  autoRunInitialQuery?: boolean;
  routePath?: string;
  resultsFirst?: boolean;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextId = useRef(2);
  const builderSectionRef = useRef<HTMLElement>(null);
  const resultsTitleRef = useRef<HTMLHeadingElement>(null);
  const screenRequestVersion = useRef(0);
  // The one thing that identifies "which run is currently on screen" -- a
  // run_id + cursor pair, always kept in sync with the URL's own `run`/
  // `cursor` params (never a second, independently-tracked copy) so a
  // fresh NL-query submission, a page reload, and browser back/forward all
  // go through the exact same load path below instead of three different
  // ones that could disagree with each other.
  const loadedRunKey = useRef<string | null>(null);
  const upgradedLegacyRuns = useRef(new Set<string>());
  const [metrics, setMetrics] = useState<MetricDefinition[]>(initialMetrics);
  const [catalogState, setCatalogState] = useState<RequestState>(initialMetrics.length > 0 ? "success" : "loading");
  const [catalogError, setCatalogError] = useState("");
  const [rows, setRows] = useState<FilterRow[]>([DEFAULT_ROW]);
  const [category, setCategory] = useState<CategoryFilter>(EMPTY_CATEGORY);
  const [sortBy, setSortBy] = useState("roe");
  const [sortDesc, setSortDesc] = useState(true);
  const [limit, setLimit] = useState("50");
  const [includeInactive, setIncludeInactive] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [requestState, setRequestState] = useState<RequestState>(() =>
    resultsFirst && (searchParams.has("query") || searchParams.has("run")) ? "loading" : "idle"
  );
  const [requestError, setRequestError] = useState("");
  const [result, setResult] = useState<ScreenResult | null>(null);
  const [lastQuery, setLastQuery] = useState<ScreenQueryPayload | null>(null);
  const [interpretedFrom, setInterpretedFrom] = useState("");
  const [builderOpen, setBuilderOpen] = useState(false);
  const [runPage, setRunPage] = useState<ScreenRunPage | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [pageSize, setPageSize] = useState(() => {
    const requested = Number(searchParams.get("limit"));
    return requested === 10 || requested === 25 || requested === 50 ? requested : 10;
  });
  const [hiddenMetricNames, setHiddenMetricNames] = useState<string[]>([]);
  const [showClassification, setShowClassification] = useState(true);

  useEffect(() => {
    if (initialMetrics.length > 0) return;
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
  }, [initialMetrics.length]);

  // The one place a ScreenRunPage (however it was obtained) turns into
  // displayed state. Never gated on whether the advanced filter builder
  // can represent the query as editable rows -- that's a display nicety
  // for the builder panel, not a precondition for showing real results
  // that already came straight from the Screener.
  const applyRunPage = useCallback((page: ScreenRunPage, pageNumber: number) => {
    const state = queryToBuilderState(page.normalized_query, metrics, () => `filter-${nextId.current++}`);
    if (state) {
      setRows(state.rows);
      setCategory(state.category);
      setSortBy(state.sortBy);
      setSortDesc(state.sortDesc);
      setLimit(state.limit);
      setIncludeInactive(state.includeInactive);
      setErrors({});
    }
    setInterpretedFrom(page.query_text);
    setLastQuery(page.normalized_query);
    setResult({ matched: page.items, excluded_missing_data: page.excluded_missing_data, excluded_inactive: page.excluded_inactive });
    setRunPage(page);
    setPageNumber(pageNumber);
    setRequestState("success");
    setBuilderOpen(false);
  }, [metrics]);

  // The one place a `run_id` (from the URL) turns into displayed state --
  // a fresh NL-query submission (handleRunCreated), pagination
  // (loadRunPage), a page reload, and browser back/forward all end up
  // here, because all of them change `searchParams.run`/`cursor` and
  // nothing else independently sets result/lastQuery/runPage for a
  // persisted run. `useSearchParams()` (reactive) is used instead of a
  // one-time `window.location.search` read specifically so this re-runs
  // on client-side navigation, not just on first mount.
  useEffect(() => {
    if (catalogState !== "success") return;
    const runId = searchParams.get("run");
    if (!runId) return;
    const cursor = searchParams.get("cursor") || undefined;
    const key = `${runId}:${pageSize}:${cursor ?? ""}`;
    if (loadedRunKey.current === key) return;
    loadedRunKey.current = key;
    const pending = readPendingRun(runId);
    if (pending) {
      void pending.then((page) => {
        if (page && typeof page === "object" && "run_id" in page) {
          applyRunPage(page as ScreenRunPage, 1);
          cacheRunPageForNavigation(page as ScreenRunPage, pageSize);
          return;
        }
        setRequestState("idle");
      }).catch((error: unknown) => {
        setRequestError(error instanceof Error ? error.message : "The screen could not be completed.");
        setRequestState("error");
      });
      return;
    }
    if (!cursor) {
      const prefetched = readNavigationRunPage(runId, pageSize);
      if (prefetched) {
        void Promise.resolve(prefetched).then((page) => {
          applyRunPage(page, Math.max(1, Number(searchParams.get("page")) || 1));
        });
        return;
      }
    }
    void savedScreensApi.getRun(runId, cursor, pageSize).then((page) => {
      applyRunPage(page, Math.max(1, Number(searchParams.get("page")) || 1));
    }).catch((error: unknown) => {
      setRequestError(error instanceof Error ? error.message : "Saved results could not be loaded.");
      setRequestState("error");
    });
  }, [catalogState, searchParams, applyRunPage, pageSize]);

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
    // collectMetricNames walks query.where too -- an OR/NOT query (from
    // the NL parser) has its real predicates there, not in the flat
    // metric_predicates list, which only ever holds a ranked (top/bottom
    // N) predicate alongside a `where` tree.
    const names = collectMetricNames(lastQuery);
    if (lastQuery.sort_by) names.push(lastQuery.sort_by);
    return [...new Set(names)];
  }, [lastQuery]);
  const visibleMetricNames = resultMetricNames.filter((name) => !hiddenMetricNames.includes(name));

  function exportCurrentPage() {
    if (!result) return;
    const headings = ["S.No.", "Ticker", "Company", ...(showClassification ? ["Industry"] : []), ...visibleMetricNames.map((name) => metricByName(metrics, name)?.display_name ?? name)];
    const escapeCsv = (value: string | number) => `"${String(value).replaceAll('"', '""')}"`;
    const rows = result.matched.map((company, index) => [
      (pageNumber - 1) * pageSize + index + 1,
      company.ticker ?? "",
      company.company_name,
      ...(showClassification ? [company.sic_description ?? ""] : []),
      ...visibleMetricNames.map((name) => company.metrics[name]?.value ?? ""),
    ]);
    const blob = new Blob([[headings, ...rows].map((row) => row.map(escapeCsv).join(",")).join("\n")], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `screen-results-page-${pageNumber}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

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

  // NaturalQueryPanel already has the full ScreenRunPage from creating the
  // run -- no second fetch here. Navigating (a real Next.js route change,
  // not a raw history.pushState) puts `run` in the URL, which is what the
  // effect above treats as the single source of truth for "what's on
  // screen"; setting loadedRunKey first stops that effect from re-fetching
  // a run this function just handed it directly.
  function handleRunCreated(run: ScreenRunPage) {
    screenRequestVersion.current += 1;
    loadedRunKey.current = `${run.run_id}:${pageSize}:`;
    cacheRunPageForNavigation(run, pageSize);
    applyRunPage(run, 1);
    router.push(runUrl(run, 1, null, pageSize));
  }

  useEffect(() => {
    if (!resultsFirst || !runPage || !interpretedFrom || requestState !== "success") return;
    if ((runPage.normalized_query.display_metrics?.length ?? 0) > 1) return;
    if (upgradedLegacyRuns.current.has(runPage.run_id)) return;
    upgradedLegacyRuns.current.add(runPage.run_id);
    const upgradedQuery: ScreenQueryPayload = {
      ...runPage.normalized_query,
      display_metrics: [...DEFAULT_COMPARISON_METRICS],
      sort_by: "market_cap",
      sort_desc: true,
    };
    setRequestState("loading");
    void savedScreensApi.createRunFromQuery(interpretedFrom, upgradedQuery, pageSize)
      .then(handleRunCreated)
      .catch((error: unknown) => {
        setRequestError(error instanceof Error ? error.message : "The comparison columns could not be loaded.");
        setRequestState("error");
      });
    // handleRunCreated intentionally stays out: this compatibility upgrade is
    // keyed by the immutable run id and must not restart on every render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resultsFirst, runPage, interpretedFrom, requestState, pageSize]);

  function runUrl(page: ScreenRunPage, number: number, cursor: string | null, size: number) {
    const params = new URLSearchParams({
      query: page.query_text,
      run: page.run_id,
      page: String(number),
      limit: String(size),
    });
    if (page.normalized_query.sort_by) params.set("sort", page.normalized_query.sort_by);
    if (page.normalized_query.sort_by) params.set("order", page.normalized_query.sort_desc ? "desc" : "asc");
    if (cursor) params.set("cursor", cursor);
    return `${routePath}?${params}`;
  }

  async function loadRunPage(cursor: string | null, nextPage: number) {
    if (!runPage) return;
    setRequestState("loading");
    try {
      const page = await savedScreensApi.getRun(runPage.run_id, cursor || undefined, pageSize);
      loadedRunKey.current = `${page.run_id}:${pageSize}:${cursor ?? ""}`;
      applyRunPage(page, nextPage);
      router.replace(runUrl(page, nextPage, cursor, pageSize));
    } catch (error) {
      setRequestError(error instanceof Error ? error.message : "The next page could not be loaded.");
      setRequestState("error");
    }
  }

  async function sortResults(metricName: string) {
    if (!lastQuery || requestState === "loading") return;
    const descending = lastQuery.sort_by === metricName ? !lastQuery.sort_desc : true;
    const sortedQuery = { ...lastQuery, sort_by: metricName, sort_desc: descending };
    setRequestState("loading");
    setRequestError("");
    try {
      const page = await savedScreensApi.createRunFromQuery(interpretedFrom, sortedQuery, pageSize);
      handleRunCreated(page);
    } catch (error) {
      setRequestState("error");
      setRequestError(error instanceof Error ? error.message : "The results could not be sorted.");
    }
  }

  async function changePageSize(size: number) {
    if (!runPage || size === pageSize || requestState === "loading") return;
    setRequestState("loading");
    try {
      const page = await savedScreensApi.getRun(runPage.run_id, undefined, size);
      setPageSize(size);
      loadedRunKey.current = `${page.run_id}:${size}:`;
      applyRunPage(page, 1);
      router.replace(runUrl(page, 1, null, size));
    } catch (error) {
      setRequestState("error");
      setRequestError(error instanceof Error ? error.message : "The page size could not be changed.");
    }
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

  const queryPanel = (
    <NaturalQueryPanel
      metrics={metrics}
      initialText={searchParams.get("query") ?? ""}
      onRunCreated={handleRunCreated}
      autoRun={autoRunInitialQuery && !searchParams.get("run")}
      pageSize={pageSize}
      title={resultsFirst ? "Search query" : "Create a screen"}
      submitPath={resultsFirst ? routePath : undefined}
      hidden={resultsFirst && requestState === "loading"}
      onBlocked={resultsFirst ? () => setRequestState("idle") : undefined}
    />
  );

  return (
    <main className={`workspace-page screener-content${resultsFirst ? " raw-screen-page" : ""}`} id="main-content">
        {catalogState === "loading" && !resultsFirst && (
          <StatusPanel className="state-panel" title="Loading metric definitions" busy>
            <p>Loading metrics.</p>
          </StatusPanel>
        )}

        {catalogState === "error" && (
          <StatusPanel
            className="state-panel"
            tone="negative"
            title="Metric definitions are unavailable"
            action={<Button type="button" variant="ghost" size="small" onClick={retryCatalog}>Try again</Button>}
          >
            <p>{catalogError}</p>
          </StatusPanel>
        )}

        {(catalogState === "success" || resultsFirst) && (
          <>
          {!resultsFirst && queryPanel}

          {(requestState !== "idle" || resultsFirst) && <section className="results-section" aria-labelledby="results-title" aria-busy={requestState === "loading"}>
            <div className="results-heading">
              <div>
                <h2 ref={resultsTitleRef} id="results-title" tabIndex={-1}>Query results</h2>
                {requestState === "success" && result && <p className="results-source-query"><strong>{runPage?.total_count ?? result.matched.length}</strong> results found · Showing page {pageNumber} of {Math.max(1, Math.ceil((runPage?.total_count ?? result.matched.length) / pageSize))}{interpretedFrom && <span className="results-query-context">From “{interpretedFrom}”</span>}</p>}
                {requestState === "success" && runPage?.corrections && runPage.corrections.length > 0 && <p className="query-corrections" role="status"><strong>Corrected:</strong> {runPage.corrections.map((correction) => `“${correction.source_text}” → “${correction.corrected_text}”`).join(" · ")}</p>}
              </div>
              {requestState === "success" && lastQuery && <SaveScreenButton query={lastQuery} runId={runPage?.run_id} />}
            </div>

            {requestState === "success" && result && result.matched.length > 0 && <div className="results-toolbar" aria-label="Result tools">
              <button type="button" className={showClassification ? "is-active" : ""} onClick={() => setShowClassification((shown) => !shown)}>Industry</button>
              <button type="button" onClick={exportCurrentPage}>Export CSV</button>
              <details className="column-picker">
                <summary>Edit columns</summary>
                <div>
                  <strong>Metrics shown</strong>
                  {resultMetricNames.map((name) => <label key={name}>
                    <input type="checkbox" checked={!hiddenMetricNames.includes(name)} onChange={(event) => setHiddenMetricNames((hidden) => event.target.checked ? hidden.filter((item) => item !== name) : [...hidden, name])} />
                    <span>{metricByName(metrics, name)?.display_name ?? name}</span>
                  </label>)}
                </div>
              </details>
            </div>}

            {requestState === "loading" && (
              <TableSkeleton columnLabels={visibleMetricNames.map((name) => metricByName(metrics, name)?.display_name ?? name)} />
            )}

            {requestState === "error" && (
              <StatusPanel
                className="state-panel"
                tone="negative"
                title="The screen did not run"
                action={lastQuery ? <Button type="button" variant="ghost" size="small" onClick={() => void executeScreen(lastQuery)}>Try again</Button> : undefined}
              >
                <p>{requestError}</p>
              </StatusPanel>
            )}

            {requestState === "success" && result && result.matched.length === 0 && (
              <EmptyState
                bordered={false}
                icon="0"
                title="No companies matched every criterion"
                description="Remove or loosen a condition."
                action={<Button type="button" variant="secondary" onClick={() => lastQuery && applyInterpretedQuery(lastQuery, interpretedFrom)}>Edit criteria</Button>}
              />
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
              <>
              <div className="results-table-wrap" tabIndex={0} aria-label="Screen results. Scroll horizontally to view all metrics.">
                <table className="results-table">
                  <caption className="sr-only">Companies matching the current screen, in backend-determined order.</caption>
                  <thead>
                    <tr>
                      <th scope="col">S.No.</th>
                      <th scope="col">Company</th>
                      {showClassification && <th scope="col">Industry</th>}
                      {visibleMetricNames.map((metricName) => {
                        const active = lastQuery?.sort_by === metricName;
                        return <th className="results-metric-heading" scope="col" key={metricName} aria-sort={active ? (lastQuery?.sort_desc ? "descending" : "ascending") : undefined}><button className="metric-sort-button" type="button" onClick={() => void sortResults(metricName)} aria-label={`Sort by ${metricByName(metrics, metricName)?.display_name ?? metricName}`}>{metricByName(metrics, metricName)?.display_name ?? metricName}{active && <span aria-hidden="true"> {lastQuery?.sort_desc ? "↓" : "↑"}</span>}</button></th>;
                      })}
                    </tr>
                  </thead>
                  <tbody>
                    {result.matched.map((company, index) => (
                      <tr key={company.cik}>
                        <td>{(pageNumber - 1) * pageSize + index + 1}</td>
                        <th scope="row">
                          {company.ticker ? <a className="company-link" aria-label={`${company.ticker} ${company.company_name}`} href={`${siteUrl}/stocks/${company.ticker.toLowerCase()}/`}><strong>{company.ticker}</strong><span>{company.company_name}</span></a> : <span className="company-link"><strong>—</strong><span>{company.company_name}</span></span>}
                          {lastQuery && <MatchReasons company={company} query={lastQuery} metrics={metrics} siteUrl={siteUrl} />}
                        </th>
                        {showClassification && <td><span className="classification">{company.sic_description || "Unclassified"}</span>{company.sic_code && <small>SIC {company.sic_code}</small>}</td>}
                        {visibleMetricNames.map((metricName) => {
                          const value = company.metrics[metricName];
                          const definition = metricByName(metrics, metricName);
                          return (
                            <td className="results-metric-cell" key={metricName}>
                              {value ? <><span className="metric-value" title={`Exact value: ${value.value}`}>{formatMetricValue(value.value, definition)}</span><small>{metricPeriod(value)} · v{value.formula_version}</small></> : <><span className="metric-value missing" aria-label="Not available">—</span><small>Not available</small></>}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {runPage && <nav className="screen-pagination" aria-label="Screen result pages">
                <span>{(pageNumber - 1) * pageSize + 1}–{Math.min((pageNumber - 1) * pageSize + runPage.items.length, runPage.total_count)} of {runPage.total_count}</span>
                <div>
                  <Button type="button" variant="secondary" size="small" disabled={pageNumber === 1} onClick={() => {
                    const previousPage = pageNumber - 1;
                    void loadRunPage(runPage.previous_cursor ?? null, previousPage);
                  }}>Previous</Button>
                  <Button type="button" variant="secondary" size="small" disabled={!runPage.next_cursor} onClick={() => {
                    if (!runPage.next_cursor) return;
                    void loadRunPage(runPage.next_cursor, pageNumber + 1);
                  }}>Next</Button>
                  <span className="page-size-label">Results per page</span>
                  {[10, 25, 50].map((size) => <Button key={size} type="button" variant={pageSize === size ? "primary" : "secondary"} size="small" onClick={() => void changePageSize(size)}>{size}</Button>)}
                </div>
              </nav>}
              </>
            )}

            {resultsFirst && queryPanel}

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
              aria-label="Exact filters"
              aria-expanded={builderOpen}
              aria-controls="advanced-builder-content"
              onClick={() => setBuilderOpen((open) => !open)}
            >
              <span className="builder-disclosure-icon" aria-hidden="true">⌁</span>
              <span><strong id="advanced-builder-title">All filters</strong></span>
              <span className="builder-disclosure-action">{builderOpen ? "Hide" : "Show"}</span>
            </button>

            {builderOpen && (
            <div id="advanced-builder-content" className="advanced-builder-content">
              <section className="reference-section" aria-labelledby="reference-title">
                <div className="section-heading compact">
                  <div>
                    <h2 id="reference-title">Templates</h2>
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
                <p className="step-label">Criteria</p>
                <h2>Filter companies</h2>
                <p>Companies must meet every condition. Missing values are excluded.</p>
              </div>
              <Button type="button" variant="ghost" onClick={resetScreen}>Reset</Button>
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
                      <select className="ds-control" id={`${row.id}-metric`} value={row.metricName} onChange={(event) => changeMetric(row, event.target.value)}>
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
                      <select className="ds-control" id={`${row.id}-operator`} value={row.operator} onChange={(event) => updateRow(row.id, { operator: event.target.value as MetricOperator, value: "", highValue: "" })}>
                        {metric?.operators.map((operator) => <option value={operator} key={operator}>{OPERATOR_LABELS[operator]}</option>)}
                      </select>
                    </div>
                    <div className={`filter-control value-control ${between ? "range" : ""}`}>
                      <label className="sr-only" htmlFor={`${row.id}-value`}>{ranked ? "Number of companies" : "Value"} for condition {index + 1}</label>
                      <div className="input-with-unit">
                        <input className="ds-control"
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
                            <input className="ds-control" id={`${row.id}-high-value`} inputMode="decimal" value={row.highValue} onChange={(event) => updateRow(row.id, { highValue: event.target.value })} aria-invalid={Boolean(errors[row.id])} aria-describedby={errors[row.id] ? `${row.id}-error` : undefined} placeholder="1" />
                            {unitLabel(metric) && <span className="unit">{unitLabel(metric)}</span>}
                          </div>
                        </>
                      )}
                    </div>
                    <IconButton tone="destructive" label={`Remove condition ${index + 1}`} icon={<span aria-hidden="true">×</span>} onClick={() => setRows((current) => current.filter((candidate) => candidate.id !== row.id))} />
                    {errors[row.id] && <p className="field-error" id={`${row.id}-error`}>{errors[row.id]}</p>}
                  </div>
                );
              })}
              <Button type="button" variant="secondary" size="small" className="add-condition" onClick={() => setRows((current) => [...current, createRow()])}>
                <span aria-hidden="true">+</span> Add condition
              </Button>
            </fieldset>

            <div className="classification-row">
              <label className="check-label">
                <input className="ds-checkbox" type="checkbox" checked={category.enabled} onChange={(event) => setCategory((current) => ({ ...current, enabled: event.target.checked }))} />
                <span>Filter by company classification</span>
              </label>
              {category.enabled && (
                <div className="inline-field">
                  <label htmlFor="classification">Classification</label>
                  <select className="ds-control" id="classification" value={category.value} onChange={(event) => { setCategory((current) => ({ ...current, value: event.target.value })); setErrors((current) => ({ ...current, category: "" })); }} aria-invalid={Boolean(errors.category)} aria-describedby={errors.category ? "category-error" : undefined}>
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
                <select className="ds-control" id="sort-by" value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
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
                <select className="ds-control" id="sort-direction" value={sortDesc ? "desc" : "asc"} onChange={(event) => setSortDesc(event.target.value === "desc")} disabled={!sortBy}>
                  <option value="desc">Highest first</option>
                  <option value="asc">Lowest first</option>
                </select>
              </div>
              <div className="setting-field limit-field">
                <label htmlFor="result-limit">Result limit</label>
                <input className="ds-control" id="result-limit" inputMode="numeric" value={limit} onChange={(event) => { setLimit(event.target.value); setErrors((current) => ({ ...current, limit: "" })); }} aria-invalid={Boolean(errors.limit)} aria-describedby={errors.limit ? "limit-error" : undefined} />
                {errors.limit && <p className="field-error" id="limit-error">{errors.limit}</p>}
              </div>
              <label className="check-label inactive-check">
                <input className="ds-checkbox" type="checkbox" checked={includeInactive} onChange={(event) => setIncludeInactive(event.target.checked)} />
                <span>Include inactive companies</span>
              </label>
            </div>

            {errors.form && <div className="validation-summary" role="alert" tabIndex={-1}><strong>Review the screen</strong><span>{errors.form}</span></div>}
            {errors.sort && <div className="validation-summary" role="alert" tabIndex={-1}><strong>Review sorting</strong><span>{errors.sort}</span></div>}

            <div className="builder-actions">
              <p><strong>{rows.length + (category.enabled ? 1 : 0)}</strong> active {rows.length + (category.enabled ? 1 : 0) === 1 ? "criterion" : "criteria"}</p>
              <Button type="submit" disabled={requestState === "loading"} aria-busy={requestState === "loading"}>
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
