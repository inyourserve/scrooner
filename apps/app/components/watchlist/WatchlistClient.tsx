"use client";

import Link from "next/link";
import { Bookmark, ChevronDown, ExternalLink, Search, Trash2, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { EmptyState } from "@/components/scrooner/EmptyState";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input, Textarea } from "@/components/ui/Input";
import { fmtDate, fmtNum, fmtPct } from "@/lib/company/format";

type Snapshot = { value: string; period_end: string; period_label: string };
type Fundamental = { latest?: Snapshot; previous?: Snapshot };
type WatchlistItem = {
  company_id: number; company_name: string; ticker: string | null; sector: string | null;
  created_at: string; note: string | null; reviewed_at: string | null;
  price: string | null; previous_price: string | null; price_as_of: string | null;
  valuation: { label: string; value: string } | null;
  latest_update: { form: string; filed_at: string; accession_number: string; source_url: string } | null;
  has_unreviewed: boolean; next_earnings: { date: string; estimated: boolean } | null;
  fundamentals: Record<string, Fundamental>;
  updates: Array<{ form: string; filed_at: string; accession_number: string; source_url: string; is_unreviewed: boolean }>;
};
type View = "all" | "unreviewed" | "reporting";
type Sort = "updates" | "earnings" | "movement" | "company";

const metricLabels: Record<string, string> = { revenue_growth_yoy: "Revenue growth", operating_margin: "Operating margin", diluted_eps: "Diluted EPS", fcf: "Free cash flow" };

function movement(item: WatchlistItem) {
  const price = Number(item.price); const previous = Number(item.previous_price);
  return Number.isFinite(price) && Number.isFinite(previous) && previous !== 0 ? ((price - previous) / previous) * 100 : null;
}

function metricValue(metric: string, value?: string) {
  if (!value) return "Unavailable";
  if (metric === "revenue_growth_yoy" || metric === "operating_margin") return fmtPct(value);
  if (metric === "diluted_eps") return `$${Number(value).toFixed(2)}`;
  return `$${fmtNum(value)}`;
}

export function WatchlistClient() {
  const [items, setItems] = useState<WatchlistItem[] | null>(null);
  const [error, setError] = useState("");
  const [view, setView] = useState<View>("all");
  const [sort, setSort] = useState<Sort>("updates");
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState<number | null>(null);
  const [busy, setBusy] = useState<number | null>(null);
  const [drafts, setDrafts] = useState<Record<number, string>>({});
  const [loadedAt] = useState(() => Date.now());

  async function load() {
    setError("");
    try {
      const response = await fetch("/api/watchlist", { cache: "no-store" });
      if (!response.ok) throw new Error("Your watchlist could not be loaded.");
      const payload = await response.json() as { items: WatchlistItem[] };
      setItems(payload.items);
      setDrafts(Object.fromEntries(payload.items.map((item) => [item.company_id, item.note ?? ""])));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Your watchlist could not be loaded."); }
  }

  useEffect(() => {
    let active = true;
    void fetch("/api/watchlist", { cache: "no-store" }).then(async (response) => {
      if (!response.ok) throw new Error("Your watchlist could not be loaded.");
      const payload = await response.json() as { items: WatchlistItem[] };
      if (!active) return;
      setItems(payload.items);
      setDrafts(Object.fromEntries(payload.items.map((item) => [item.company_id, item.note ?? ""])));
    }).catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : "Your watchlist could not be loaded."); });
    return () => { active = false; };
  }, []);

  const visible = useMemo(() => {
    const sevenDays = loadedAt + 7 * 86_400_000;
    return [...(items ?? [])].filter((item) => {
      if (!`${item.company_name} ${item.ticker ?? ""}`.toLowerCase().includes(query.trim().toLowerCase())) return false;
      if (view === "unreviewed") return item.has_unreviewed;
      if (view === "reporting") return item.next_earnings && Date.parse(item.next_earnings.date) <= sevenDays;
      return true;
    }).sort((a, b) => {
      if (sort === "company") return a.company_name.localeCompare(b.company_name);
      if (sort === "movement") return Math.abs(movement(b) ?? -1) - Math.abs(movement(a) ?? -1);
      if (sort === "earnings") return (a.next_earnings?.date ?? "9999").localeCompare(b.next_earnings?.date ?? "9999");
      return Number(b.has_unreviewed) - Number(a.has_unreviewed);
    });
  }, [items, loadedAt, query, sort, view]);

  async function update(companyId: number, body: { note?: string; mark_reviewed?: boolean }) {
    setBusy(companyId); setError("");
    try {
      const response = await fetch(`/api/watchlist/${companyId}`, { method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
      if (!response.ok) throw new Error("The watchlist item could not be updated.");
      await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "The watchlist item could not be updated."); }
    finally { setBusy(null); }
  }

  async function remove(companyId: number) {
    setBusy(companyId); setError("");
    try {
      const response = await fetch(`/api/watchlist/${companyId}`, { method: "DELETE" });
      if (!response.ok) throw new Error("The company could not be removed.");
      setItems((current) => current?.filter((item) => item.company_id !== companyId) ?? []);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "The company could not be removed."); }
    finally { setBusy(null); }
  }

  if (error && items === null) return <Card><EmptyState bordered={false} title="Watchlist unavailable" description={error} action={<Button size="small" variant="secondary" onClick={() => void load()}>Try again</Button>} /></Card>;
  if (items === null) return <Card><EmptyState bordered={false} title="Loading your watchlist" description="Retrieving your saved companies…" /></Card>;

  const unread = items.filter((item) => item.has_unreviewed).length;
  const reporting = items.filter((item) => item.next_earnings && Date.parse(item.next_earnings.date) <= loadedAt + 7 * 86_400_000).length;
  const viewOptions = [
    ["all", "All", items.length],
    ["unreviewed", "Unreviewed", unread],
    ["reporting", "Reporting soon", reporting],
  ] as const;

  return <div className="watchlist-workspace">
    <section className="watchlist-catchup" aria-label="Watchlist catch-up">
      <span className="watchlist-catchup__signal" aria-hidden="true"><Bookmark size={17} /></span>
      <span><strong>{unread > 0 ? `${unread} ${unread === 1 ? "company has" : "companies have"} new updates` : "You’re caught up"}</strong><small>{reporting > 0 ? `${reporting} ${reporting === 1 ? "company reports" : "companies report"} in the next 7 days.` : "No tracked earnings are due in the next 7 days."}</small></span>
    </section>
    <div className="watchlist-toolbar">
      <div className="watchlist-views" aria-label="Watchlist filters">{viewOptions.map(([key, label, count]) => <button aria-pressed={view === key} key={key} onClick={() => setView(key)} type="button"><span>{label}</span><b>{count}</b></button>)}</div>
      <label className="watchlist-search"><Search size={15} aria-hidden="true" /><Input aria-label="Search watchlist" placeholder="Search by company or ticker" value={query} onChange={(event) => setQuery(event.target.value)} />{query && <button aria-label="Clear search" onClick={() => setQuery("")} type="button"><X size={14} aria-hidden="true" /></button>}</label>
      <label className="watchlist-sort"><span>Sort</span><select value={sort} onChange={(event) => setSort(event.target.value as Sort)}><option value="updates">Unreviewed updates</option><option value="earnings">Earnings date</option><option value="movement">Daily movement</option><option value="company">Company name</option></select></label>
    </div>
    <div className="watchlist-results-meta" aria-live="polite"><strong>{visible.length}</strong> {visible.length === 1 ? "company" : "companies"}<span>Updated from verified filings and market data</span></div>
    {error && <p className="watchlist-list__error" role="alert">{error}</p>}
    {items.length === 0 ? <Card><EmptyState bordered={false} icon={<Bookmark size={22} aria-hidden="true" />} title="Your watchlist is empty" description="Follow companies from any company research page." action={<Link className="ds-button ds-button--secondary ds-button--small" href="/explore">Explore companies</Link>} /></Card> : visible.length === 0 ? <Card><EmptyState bordered={false} title="No companies in this view" description="Try another view or clear your search." /></Card> : <Card className="watchlist-list"><div className="watchlist-list__header" aria-hidden="true"><span>Company</span><span>Price</span><span>Valuation</span><span>Latest update</span><span>Next earnings</span><span>Status</span></div>{visible.map((item) => {
      const change = movement(item); const isOpen = expanded === item.company_id;
      return <article className="watchlist-company" key={item.company_id}>
        <button className="watchlist-company__summary" aria-expanded={isOpen} onClick={() => setExpanded(isOpen ? null : item.company_id)} type="button">
          <span className="watchlist-company__identity">{item.has_unreviewed && <i aria-label="Unreviewed update" />}<span><strong>{item.company_name}</strong><small>{item.ticker ?? "Ticker unavailable"} · {item.sector ?? "Sector unclassified"}</small></span></span>
          <span><small>Price</small><strong>{item.price ? `$${Number(item.price).toFixed(2)}` : "Unavailable"}</strong>{change !== null && <em data-tone={change >= 0 ? "positive" : "negative"}>{change >= 0 ? "+" : ""}{change.toFixed(2)}%</em>}</span>
          <span><small>{item.valuation?.label ?? "Valuation"}</small><strong>{item.valuation ? `${Number(item.valuation.value).toFixed(1)}x` : "Unavailable"}</strong></span>
          <span><small>Latest update</small><strong>{item.latest_update ? `${item.latest_update.form} filed` : "No result update"}</strong><em>{fmtDate(item.latest_update?.filed_at)}</em></span>
          <span><small>Next earnings</small><strong>{item.next_earnings ? fmtDate(item.next_earnings.date) : "Unavailable"}</strong><em>{item.next_earnings?.estimated ? "Estimated" : "No verified date"}</em></span>
          <span className="watchlist-company__status"><Badge tone={item.has_unreviewed ? "warning" : "neutral"}>{item.has_unreviewed ? "Unreviewed" : "Reviewed"}</Badge><ChevronDown size={17} aria-hidden="true" /></span>
        </button>
        {isOpen && <div className="watchlist-company__detail">
          <section><div className="watchlist-detail-heading"><h3>What changed</h3>{item.latest_update && <a href={item.latest_update.source_url} rel="noreferrer" target="_blank">SEC source <ExternalLink size={13} aria-hidden="true" /></a>}</div>
            <div className="watchlist-fundamentals">{Object.entries(metricLabels).map(([metric, label]) => { const fact = item.fundamentals?.[metric]; return <div key={metric}><strong>{label}</strong><span><small>{fact?.previous ? `${fact.previous.period_label} · ${fmtDate(fact.previous.period_end)}` : "Prior-year quarter"}</small>{metricValue(metric, fact?.previous?.value)}</span><b aria-hidden="true">→</b><span><small>{fact?.latest ? `${fact.latest.period_label} · ${fmtDate(fact.latest.period_end)}` : "Latest quarter"}</small>{metricValue(metric, fact?.latest?.value)}</span></div>; })}</div>
            <p className="watchlist-source-note">Figures compare the latest available quarter with the same quarter a year earlier. Data as of {item.latest_update ? fmtDate(item.latest_update.filed_at) : "the latest verified filing"}.</p>
            {(item.updates?.length ?? 0) > 0 && <div className="watchlist-update-history"><h3>Recent results</h3>{item.updates.map((update) => <a href={update.source_url} key={update.accession_number} rel="noreferrer" target="_blank"><span><strong>{update.form}</strong><small>{fmtDate(update.filed_at)}</small></span>{update.is_unreviewed && <Badge tone="warning">New</Badge>}<ExternalLink size={13} aria-hidden="true" /></a>)}</div>}
          </section>
          <section className="watchlist-note"><h3>Why I’m watching</h3><Textarea maxLength={2000} placeholder="Add your investment thesis or the question you want to revisit…" value={drafts[item.company_id] ?? ""} onChange={(event) => setDrafts((current) => ({ ...current, [item.company_id]: event.target.value }))} /><div><Button size="small" variant="secondary" loading={busy === item.company_id} onClick={() => void update(item.company_id, { note: drafts[item.company_id] ?? "" })}>Save note</Button>{item.has_unreviewed && <Button size="small" loading={busy === item.company_id} onClick={() => void update(item.company_id, { mark_reviewed: true })}>Mark as reviewed</Button>}<Button aria-label={`Remove ${item.company_name} from watchlist`} size="small" variant="ghost" leadingIcon={<Trash2 size={14} aria-hidden="true" />} onClick={() => void remove(item.company_id)}>Remove</Button></div><Link href={item.ticker ? `/stocks/${item.ticker.toLowerCase()}` : "/stocks"}>Open company research</Link></section>
        </div>}
      </article>;
    })}</Card>}
  </div>;
}
