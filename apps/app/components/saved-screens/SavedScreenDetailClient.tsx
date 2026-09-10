"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { StatusPanel } from "@/components/ui/StatusPanel";
import { savedScreensApi } from "@/lib/saved-screens/client";
import type { SavedScreen } from "@/lib/saved-screens/types";

function metricLabel(name: string) {
  return name.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function displayValue(value: string) {
  const number = Number(value);
  return Number.isFinite(number) ? new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(number) : value;
}

export function SavedScreenDetailClient({ initialScreen, initialPage }: { initialScreen: SavedScreen; initialPage: number }) {
  const router = useRouter();
  const [screen, setScreen] = useState(initialScreen);
  const [run, setRun] = useState(initialScreen.run ?? null);
  const [page, setPage] = useState(initialPage);
  const [state, setState] = useState<"ready" | "loading" | "error">("ready");
  const [message, setMessage] = useState("");
  const metricNames = [...new Set([
    ...screen.query.metric_predicates.map((item) => item.metric_name),
    ...(screen.query.sort_by ? [screen.query.sort_by] : []),
  ])];

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

  return <main className="workspace-page saved-screen-detail" id="main-content">
    <header className="saved-screen-detail__header">
      <div><Link href="/app/screens" className="saved-screen-detail__back">Saved screens</Link><h1>{screen.name}</h1>{run && <p>{run.total_count} matches · Updated {new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(run.ran_at))}</p>}</div>
      <div><Button variant="secondary" onClick={edit}>Edit query</Button><Button loading={state === "loading"} loadingLabel="Refreshing…" onClick={() => void refresh()}>Refresh results</Button></div>
    </header>
    {state === "error" && <StatusPanel tone="negative" title="Results are unavailable"><p>{message}</p></StatusPanel>}
    {!run ? <StatusPanel title="This screen has not been run"><p>Edit the query and run it to create results.</p></StatusPanel> : <>
      <div className="results-table-wrap"><table className="results-table"><thead><tr><th>Company</th><th>Classification</th>{metricNames.map((name) => <th key={name}>{metricLabel(name)}</th>)}</tr></thead><tbody>{run.items.map((company) => <tr key={company.company_id}><th>{company.ticker ? <Link href={`/stocks/${company.ticker.toLowerCase()}`}>{company.ticker}<span>{company.company_name}</span></Link> : <span>{company.company_name}</span>}</th><td>{company.sic_description || "—"}</td>{metricNames.map((name) => <td key={name}>{company.metrics[name] ? displayValue(company.metrics[name].value) : "—"}</td>)}</tr>)}</tbody></table></div>
      <nav className="screen-pagination" aria-label="Screen result pages"><span>{(page - 1) * 50 + 1}–{Math.min((page - 1) * 50 + run.items.length, run.total_count)} of {run.total_count}</span><div><Button variant="secondary" size="small" disabled={!run.previous_cursor || state === "loading"} onClick={() => void changePage(run.previous_cursor ?? null, page - 1)}>Previous</Button><Button variant="secondary" size="small" disabled={!run.next_cursor || state === "loading"} onClick={() => { if (run.next_cursor) void changePage(run.next_cursor, page + 1); }}>Next</Button></div></nav>
    </>}
  </main>;
}
