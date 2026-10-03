import type { Metadata } from "next";
import Link from "next/link";
import { AlertTriangle, ArrowRight, Bookmark, History, Search } from "lucide-react";
import { redirect } from "next/navigation";
import { PageHeader } from "@/components/layout/PageHeader";
import { PageShell } from "@/components/layout/PageShell";
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

export default async function AppHome() {
  const supabase = await createClient();
  const { data } = await supabase.auth.getSession();
  if (!data.session?.access_token) redirect(buildLoginHref("/app"));

  let screens: SavedScreen[] = [];
  let recentRuns: RecentRun[] = [];
  let screensUnavailable = false;
  let runsUnavailable = false;
  const requestHeaders = { accept: "application/json", authorization: `Bearer ${data.session.access_token}` };
  const [screensResult, runsResult] = await Promise.allSettled([
    fetch(backendUrl("/v1/screens"), {
      cache: "no-store",
      headers: requestHeaders,
    }),
    fetch(backendUrl("/v1/screen-runs?limit=8"), { cache: "no-store", headers: requestHeaders }),
  ]);
  if (screensResult.status === "fulfilled" && screensResult.value.ok) screens = await screensResult.value.json() as SavedScreen[];
  else screensUnavailable = true;
  if (runsResult.status === "fulfilled" && runsResult.value.ok) recentRuns = await runsResult.value.json() as RecentRun[];
  else runsUnavailable = true;

  const recentScreens = [...screens]
    .sort((left, right) => Date.parse(right.updated_at) - Date.parse(left.updated_at))
    .slice(0, 6);

  return <PageShell>
    <div className="dashboard-page__header">
      <PageHeader eyebrow="Your research" title="Dashboard" description="Pick up where you left off, or turn a new investment idea into a screen." />
      <Button asChild><Link href="/app/screens/new">Create screen</Link></Button>
    </div>

    <section className="dashboard-page__summary" aria-label="Research overview">
      <Card variant="subtle"><CardContent><span className="dashboard-page__summary-icon"><History size={17} aria-hidden="true" /></span><strong>{recentRuns.length}</strong><small>recent queries</small></CardContent></Card>
      <Card variant="subtle"><CardContent><span className="dashboard-page__summary-icon"><Bookmark size={17} aria-hidden="true" /></span><strong>{screens.length}</strong><small>saved screens</small></CardContent></Card>
      <Card variant="subtle"><CardContent><span className="dashboard-page__summary-icon"><Search size={17} aria-hidden="true" /></span><strong>{recentRuns[0]?.total_count ?? "—"}</strong><small>latest matches</small></CardContent></Card>
    </section>

    <div className="dashboard-page__grid">
    <Card>
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

    <Card>
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
    </div>
  </PageShell>;
}
