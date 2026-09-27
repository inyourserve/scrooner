import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { redirect } from "next/navigation";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardDescription, CardHeader, CardHeading, CardTitle } from "@/components/ui/Card";
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
  return new Intl.DateTimeFormat("en", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value));
}

export default async function AppHome() {
  const supabase = await createClient();
  const { data } = await supabase.auth.getSession();
  if (!data.session?.access_token) redirect(buildLoginHref("/app"));

  let screens: SavedScreen[] = [];
  try {
    const response = await fetch(backendUrl("/v1/screens"), {
      cache: "no-store",
      headers: { accept: "application/json", authorization: `Bearer ${data.session.access_token}` },
    });
    if (response.ok) screens = await response.json() as SavedScreen[];
  } catch {
    // Keep the dashboard usable if the saved-screen service is unavailable.
  }

  const recentScreens = [...screens]
    .sort((left, right) => Date.parse(right.updated_at) - Date.parse(left.updated_at))
    .slice(0, 6);

  return <main className="main-content" id="main-content">
    <div className="dashboard-page__header">
      <PageHeader eyebrow="Research workspace" title="Dashboard" description="Return to saved research or start a new company screen." />
      <Button asChild><Link href="/app/screens/new">New screen</Link></Button>
    </div>

    <Card>
      <CardHeader>
        <CardHeading><CardTitle>Saved screens</CardTitle><CardDescription>Your most recently updated research.</CardDescription></CardHeading>
        {screens.length > 0 && <Button asChild variant="ghost" size="small" trailingIcon={<ArrowRight size={14} aria-hidden="true" />}><Link href="/app/screens">View all</Link></Button>}
      </CardHeader>
      {recentScreens.length > 0 ? (
        <div className="dashboard-page__recent-list">
          {recentScreens.map((screen) => {
            const count = criterionCount(screen);
            return <Link href={`/app/screens/${screen.slug}`} className="dashboard-page__recent-item" key={screen.id}>
              <span><strong>{screen.name}</strong><small>Updated {updatedLabel(screen.updated_at)}</small></span>
              <Badge>{typeof count === "number" ? `${count} ${count === 1 ? "filter" : "filters"}` : count}</Badge>
            </Link>;
          })}
        </div>
      ) : (
        <EmptyState
          title="Nothing saved yet"
          description="Screens you save from a search stay here for quick reruns."
          action={<Link className="ds-button ds-button--secondary ds-button--small" href="/app/screens/new">Build a screen</Link>}
        />
      )}
    </Card>
  </main>;
}
