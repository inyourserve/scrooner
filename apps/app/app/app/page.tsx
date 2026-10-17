import type { Metadata } from "next";
import Link from "next/link";
import { AlertTriangle, ArrowRight, Bookmark, Eye, History, Sparkles } from "lucide-react";
import { redirect } from "next/navigation";
import { PageShell } from "@/components/layout/PageShell";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardHeading, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/scrooner/EmptyState";
import { backendUrl } from "@/lib/backend";
import { buildLoginHref } from "@/lib/auth/redirect";
import type { SavedScreen } from "@/lib/saved-screens/types";
import { createClient } from "@/lib/supabase/server";

export const metadata: Metadata = { title: "Dashboard — Scrooner" };
export const dynamic = "force-dynamic";

function criterionCount(screen: SavedScreen) {
  if (screen.query.where) return "Advanced logic";
  return screen.query.metric_predicates.length + screen.query.categorical_predicates.length;
}

function updatedLabel(value: string) {
  return new Intl.DateTimeFormat("en", { day: "numeric", month: "short", hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

type RecentRun = { run_id: string; query_text: string; ran_at: string; total_count: number };
type WatchlistItem = { company_id: number; company_name: string; ticker: string | null; sector: string | null; created_at: string; has_unreviewed?: boolean };

export default async function AppHome() {
  const supabase = await createClient();
  const { data } = await supabase.auth.getSession();
  if (!data.session?.access_token) redirect(buildLoginHref("/app"));

  let screens: SavedScreen[] = [];
  let recentRuns: RecentRun[] = [];
  let watchlist: WatchlistItem[] = [];
  let screensUnavailable = false;
  let runsUnavailable = false;
  let watchlistUnavailable = false;
  const requestHeaders = { accept: "application/json", authorization: `Bearer ${data.session.access_token}` };
  const [screensResult, runsResult, watchlistResult] = await Promise.allSettled([
    fetch(backendUrl("/v1/screens"), {
      cache: "no-store",
      headers: requestHeaders,
    }),
    fetch(backendUrl("/v1/screen-runs?limit=8"), { cache: "no-store", headers: requestHeaders }),
    fetch(backendUrl("/v1/watchlist"), { cache: "no-store", headers: requestHeaders }),
  ]);
  if (screensResult.status === "fulfilled" && screensResult.value.ok) screens = await screensResult.value.json() as SavedScreen[];
  else screensUnavailable = true;
  if (runsResult.status === "fulfilled" && runsResult.value.ok) recentRuns = await runsResult.value.json() as RecentRun[];
  else runsUnavailable = true;
  if (watchlistResult.status === "fulfilled" && watchlistResult.value.ok) {
    const payload = await watchlistResult.value.json() as { items: WatchlistItem[] };
    watchlist = payload.items;
  } else watchlistUnavailable = true;

  const recentScreens = [...screens]
    .sort((left, right) => Date.parse(right.updated_at) - Date.parse(left.updated_at))
    .slice(0, 6);
  const watchlistUpdates = watchlist.filter((company) => company.has_unreviewed).length;

  return <PageShell>
    <WorkspaceHeader eyebrow="Your research" title="Dashboard" description="Pick up where you left off, review company changes, or turn a new investment idea into a screen." actions={<Button asChild><Link href="/app/screens/new">Create screen</Link></Button>} />

    <section className="dashboard-page__summary" aria-label="Research overview">
      <Link aria-label="Open recent queries" className="dashboard-page__summary-link" href="/app/screens/new"><Card variant="subtle"><CardContent><span className="dashboard-page__summary-icon"><History size={17} aria-hidden="true" /></span><strong>{recentRuns.length}</strong><small>recent queries</small></CardContent></Card></Link>
      <Link aria-label="Open saved screens" className="dashboard-page__summary-link" href="/app/screens"><Card variant="subtle"><CardContent><span className="dashboard-page__summary-icon"><Bookmark size={17} aria-hidden="true" /></span><strong>{screensUnavailable ? "—" : screens.length}</strong><small>saved screens</small></CardContent></Card></Link>
      <Link aria-label="Open watchlist" className="dashboard-page__summary-link" href="/app/watchlist"><Card variant="subtle"><CardContent><span className="dashboard-page__summary-icon"><Eye size={17} aria-hidden="true" /></span><strong>{watchlistUnavailable ? "—" : watchlist.length}</strong><small>companies followed</small></CardContent></Card></Link>
      <Link aria-label="Review watchlist updates" className="dashboard-page__summary-link" href="/app/watchlist"><Card variant="subtle"><CardContent><span className="dashboard-page__summary-icon"><Sparkles size={17} aria-hidden="true" /></span><strong>{watchlistUnavailable ? "—" : watchlistUpdates}</strong><small>updates to review</small></CardContent></Card></Link>
    </section>

    <div className="dashboard-page__grid">
    <Card className="dashboard-page__card dashboard-page__card--primary">
      <CardHeader>
        <CardHeading><CardTitle>Recent queries</CardTitle><CardDescription>Open a previous result set without rebuilding the screen.</CardDescription></CardHeading>
        <Button asChild variant="ghost" size="small" trailingIcon={<ArrowRight size={14} aria-hidden="true" />}><Link href="/app/screens/new">New query</Link></Button>
      </CardHeader>
      {runsUnavailable ? <EmptyState icon={<AlertTriangle size={22} aria-hidden="true" />} title="Query history is unavailable" description="Your saved research is unaffected." /> : recentRuns.length > 0 ? (
        <div className="dashboard-page__recent-list">
          {recentRuns.map((run) => <Link href={`/app/screens/new/raw?run=${run.run_id}&query=${encodeURIComponent(run.query_text)}&limit=50&page=1`} className="dashboard-page__recent-item" key={run.run_id}>
            <span><strong>{run.query_text}</strong><small>Ran {updatedLabel(run.ran_at)}</small></span>
            <Badge>{run.total_count} {run.total_count === 1 ? "match" : "matches"}</Badge>
          </Link>)}
        </div>
      ) : <EmptyState title="No query history yet" description="Describe an investment idea in plain English to begin." action={<Link className="ds-button ds-button--secondary ds-button--small" href="/app/screens/new">Create a query</Link>} />}
    </Card>

    <Card className="dashboard-page__card">
      <CardHeader>
        <CardHeading><CardTitle>Recent screens</CardTitle><CardDescription>Continue from your most recently updated screens.</CardDescription></CardHeading>
        {screens.length > 0 && <Button asChild variant="ghost" size="small" trailingIcon={<ArrowRight size={14} aria-hidden="true" />}><Link href="/app/screens">View all</Link></Button>}
      </CardHeader>
      {screensUnavailable ? (
        <EmptyState
          icon={<AlertTriangle size={22} aria-hidden="true" />}
          title="We couldn’t load your saved screens"
          description="Your research is safe. Try opening your screen library again."
          action={<Link className="ds-button ds-button--secondary ds-button--small" href="/app/screens">Try again</Link>}
        />
      ) : recentScreens.length > 0 ? (
        <div className="dashboard-page__recent-list">
          {recentScreens.map((screen) => {
            const count = criterionCount(screen);
            return <Link href={`/app/screens/${screen.slug}`} className="dashboard-page__recent-item" key={screen.id}>
              <span><strong>{screen.name}</strong><small>Updated {updatedLabel(screen.updated_at)}</small></span>
              <Badge>{typeof count === "number" ? `${count} ${count === 1 ? "criterion" : "criteria"}` : count}</Badge>
            </Link>;
          })}
        </div>
      ) : (
        <EmptyState
          title="Your saved screens will appear here"
          description="Create a screen, review the results, and save it to run again later."
          action={<Link className="ds-button ds-button--secondary ds-button--small" href="/app/screens/new">Create your first screen</Link>}
        />
      )}
    </Card>

    <Card className="dashboard-page__card dashboard-page__card--wide">
      <CardHeader>
        <CardHeading><CardTitle>Watchlist</CardTitle><CardDescription>Companies you are actively following.</CardDescription></CardHeading>
        <Button asChild variant="ghost" size="small" trailingIcon={<ArrowRight size={14} aria-hidden="true" />}><Link href="/app/watchlist">Open watchlist</Link></Button>
      </CardHeader>
      {watchlistUnavailable ? <EmptyState icon={<AlertTriangle size={22} aria-hidden="true" />} title="Watchlist is unavailable" description="Your saved companies are unaffected." /> : watchlist.length > 0 ? (
        <div className="dashboard-page__recent-list">
          {watchlist.slice(0, 5).map((company) => <Link className="dashboard-page__recent-item" href={company.ticker ? `/stocks/${company.ticker.toLowerCase()}` : "/app/watchlist"} key={company.company_id}>
            <span><strong>{company.company_name}</strong><small>{company.sector ?? "Sector unclassified"}</small></span>
            <span className="dashboard-page__item-meta"><Badge>{company.ticker ?? "—"}</Badge>{company.has_unreviewed && <Badge tone="warning">New filing</Badge>}</span>
          </Link>)}
        </div>
      ) : <EmptyState title="Your watchlist is empty" description="Follow companies from their research pages to see them here." action={<Link className="ds-button ds-button--secondary ds-button--small" href="/explore">Explore companies</Link>} />}
    </Card>
    </div>
  </PageShell>;
}
