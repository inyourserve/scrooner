import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Compass, Plus } from "lucide-react";
import { redirect } from "next/navigation";
import { Badge } from "@/components/ui/Badge";
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

// Dashboard's own job is narrow: this is the signed-in visitor's home base
// -- a quick way back to research they already saved, plus two clear doors
// to the two other, genuinely different tools (a fresh screen, or browsing
// for one). It never duplicates the query composer that lives on
// /app/screens/new -- that page owns the one real interpret-and-run flow,
// and Dashboard reusing its look was making the two pages feel like the
// same feature wearing different clothes.
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

  return <main className="dashboard-page" id="main-content">
    <header className="dashboard-page__header">
      <p className="dashboard-page__eyebrow">Research workspace</p>
      <h1>Dashboard</h1>
    </header>

    <div className="dashboard-page__actions">
      <Link className="dashboard-page__action" href="/app/screens/new">
        <Plus size={18} aria-hidden="true" />
        <span><strong>New screen</strong><small>Describe what you&apos;re looking for in plain language.</small></span>
      </Link>
      <Link className="dashboard-page__action" href="/explore">
        <Compass size={18} aria-hidden="true" />
        <span><strong>Explore</strong><small>Browse popular screens, sectors, and industries.</small></span>
      </Link>
    </div>

    <section className="dashboard-page__recent">
      <div className="dashboard-page__recent-heading">
        <h2>Saved screens</h2>
        {screens.length > 0 && <Link href="/app/screens">View all<ArrowRight size={14} aria-hidden="true" /></Link>}
      </div>
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
        <p className="dashboard-page__empty">Nothing saved yet. Screens you save from a search stay here for quick reruns.</p>
      )}
    </section>
  </main>;
}
