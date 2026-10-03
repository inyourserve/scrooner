"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { PageShell } from "@/components/layout/PageShell";
import { StatusPanel } from "@/components/ui/StatusPanel";
import { savedScreensApi } from "@/lib/saved-screens/client";
import type { SavedScreen } from "@/lib/saved-screens/types";
import { metricByName } from "@/lib/screener/catalog";
import { formatMetricValue, metricPeriod, resultColumnLabel, resultColumnUnit } from "@/lib/screener/format";
import { collectMetricNames, collectPredicateMetricNames, type MetricDefinition } from "@/lib/screener/types";

export function SavedScreenDetailClient({ initialScreen, initialPage, metrics }: { initialScreen: SavedScreen; initialPage: number; metrics: MetricDefinition[] }) {
  const router = useRouter();
  const [screen, setScreen] = useState(initialScreen);
  const [run, setRun] = useState(initialScreen.run ?? null);
  const [page, setPage] = useState(initialPage);
  const [state, setState] = useState<"ready" | "loading" | "error">("ready");
  const [message, setMessage] = useState("");
  const metricNames = [...new Set([
    ...collectMetricNames(screen.query),
    ...(screen.query.sort_by ? [screen.query.sort_by] : []),
  ])];
  const filteredMetricNames = new Set(collectPredicateMetricNames(screen.query));
  const resultStart = run && run.total_count > 0 ? (page - 1) * 50 + 1 : 0;
  const resultEnd = run ? Math.min((page - 1) * 50 + run.items.length, run.total_count) : 0;

  async function changePage(cursor: string | null, targetPage: number) {
    setState("loading");
    try {
      const next = await savedScreensApi.get(screen.slug, cursor || undefined);
      setRun(next.run ?? null);
      setPage(targetPage);
      setState("ready");
      const params = new URLSearchParams({ page: String(targetPage) });
      if (cursor) params.set("cursor", cursor);
      router.push(`/app/screens/${screen.slug}?${params}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Results could not be loaded.");
      setState("error");
    }
  }

  async function refresh() {
    setState("loading");
    try {
      const nextRun = await savedScreensApi.refresh(screen.slug);
      setRun(nextRun);
      setScreen((current) => ({ ...current, run: nextRun, updated_at: nextRun.ran_at }));
      setPage(1);
      setState("ready");
      router.replace(`/app/screens/${screen.slug}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Results could not be refreshed.");
      setState("error");
    }
  }

  function edit() {
    const queryText = run?.query_text.trim();
    router.push(queryText ? `/app/screens/new?query=${encodeURIComponent(queryText)}` : "/app/screens/new");
  }

  return <PageShell className="saved-screen-detail">
    <header className="saved-screen-detail__header">
      <div><Breadcrumb items={[{ label: "Saved screens", href: "/app/screens" }, { label: screen.name }]} /><p className="workspace-eyebrow">Saved screen</p><h1 className="ds-workspace-title">{screen.name}</h1>{run && <p><strong>{run.total_count}</strong> matches · Updated {new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(run.ran_at))}</p>}</div>
      <div><Button variant="secondary" onClick={edit}>Edit query</Button><Button loading={state === "loading"} loadingLabel="Refreshing…" onClick={() => void refresh()}>Refresh results</Button></div>
    </header>
    {state === "error" && <StatusPanel tone="negative" title="Results are unavailable"><p>{message}</p></StatusPanel>}
    {!run ? <StatusPanel title="This screen has not been run"><p>Edit the query and run it to create results.</p></StatusPanel> : <>
      <section className="saved-results-surface" aria-label="Saved screen results">
        <div className="saved-results-surface__toolbar"><span>Showing page {page}</span><span>Reported fundamentals · Formula-versioned</span></div>
        <div className="results-table-wrap ds-data-table-shell" tabIndex={0} role="region" aria-label="Saved screen results. Scroll horizontally to view all metrics.">
          <table className="results-table ds-data-table ds-screen-results-table" data-presentation="financial">
            <caption className="sr-only">Companies matching the saved screen.</caption>
            <thead><tr><th scope="col">S.No.</th><th scope="col">Company</th><th scope="col" data-text="true">Industry</th>{metricNames.map((name) => { const definition = metricByName(metrics, name); const filtered = filteredMetricNames.has(name); return <th className="results-metric-heading" data-filtered={filtered || undefined} data-numeric="true" scope="col" key={name} title={definition?.short_definition}><span className="results-column-label">{resultColumnLabel(name, definition)}</span><span className="results-column-unit">{filtered ? "Criterion · " : ""}{resultColumnUnit(definition)}</span></th>; })}</tr></thead>
            <tbody>{run.items.map((company, index) => <tr key={company.company_id}>
              <td>{(page - 1) * 50 + index + 1}</td>
              <th scope="row">{company.ticker ? <Link className="company-link" aria-label={`${company.ticker} ${company.company_name}`} href={`/stocks/${company.ticker.toLowerCase()}`}><strong>{company.ticker}</strong><span title={company.company_name}>{company.company_name}</span></Link> : <span className="company-link"><strong>—</strong><span>{company.company_name}</span></span>}</th>
              <td data-text="true"><span className="classification" title={company.sic_description || "Unclassified"}>{company.sic_description || "Unclassified"}</span>{company.sic_code && <small>SIC {company.sic_code}</small>}</td>
              {metricNames.map((name) => { const value = company.metrics[name]; const definition = metricByName(metrics, name); return <td className="results-metric-cell" data-filtered={filteredMetricNames.has(name) || undefined} data-numeric="true" key={name}>{value ? <><span className="metric-value" title={`Exact value: ${value.value}`}>{formatMetricValue(value.value, definition)}</span><small>{metricPeriod(value)} · v{value.formula_version}</small></> : <><span className="metric-value missing" aria-label="Not available">—</span><small>Not available</small></>}</td>; })}
            </tr>)}</tbody>
          </table>
        </div>
        <nav className="screen-pagination ds-pagination" aria-label="Screen result pages"><span className="ds-pagination__summary">{resultStart}–{resultEnd} of {run.total_count}</span><div className="ds-pagination__controls"><Button variant="secondary" size="small" disabled={!run.previous_cursor || state === "loading"} onClick={() => void changePage(run.previous_cursor ?? null, page - 1)}>Previous</Button><Button variant="secondary" size="small" disabled={!run.next_cursor || state === "loading"} onClick={() => { if (run.next_cursor) void changePage(run.next_cursor, page + 1); }}>Next</Button></div></nav>
      </section>
    </>}
  </PageShell>;
}
