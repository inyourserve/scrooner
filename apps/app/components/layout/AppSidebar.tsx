import Link from "next/link";
import { BarChart3, Compass, FileText, Plus, Settings, Sparkles, Star } from "lucide-react";
import { NATURAL_QUERY_EXAMPLES } from "@/lib/screener/interpretation";

// The shortest of the already-verified example phrases (doc 15b) -- a
// narrow sidebar column has no room for the longer ones ("revenue growth
// 3Y CAGR above 15%") without ugly wrapping.
const PROMOTED_SCREENS = [...NATURAL_QUERY_EXAMPLES].sort((a, b) => a.length - b.length).slice(0, 3);

function exampleHref(example: string) {
  return `/app/screens/new?${new URLSearchParams({ q: example, run: "1" })}`;
}

// The one sidebar shown on every standard-width /app page (see
// AppPageLayout) -- promotes the paid plan and a couple of popular screens
// alongside the same quick links every page needs, rather than each page
// inventing its own "where else can I go" answer. Never shown on wide-table
// pages (screen results, saved-screen detail) or public company pages --
// those have their own reasons to want the full width instead.
export function AppSidebar() {
  return (
    <aside className="app-sidebar" aria-label="Quick links">
      <div className="app-sidebar__promo">
        <Sparkles size={16} aria-hidden="true" />
        <div>
          <strong>Scrooner Premium</strong>
          <p>A deeper screening tier is in development.</p>
        </div>
        <Link className="ds-button ds-button--secondary ds-button--small" href="/pricing">See plans</Link>
      </div>

      <div className="app-sidebar__group">
        <p className="app-sidebar__label">Popular screens</p>
        {PROMOTED_SCREENS.map((example) => (
          <Link key={example} className="app-sidebar__link app-sidebar__link--text" href={exampleHref(example)}>{example}</Link>
        ))}
      </div>

      <div className="app-sidebar__group">
        <p className="app-sidebar__label">Research</p>
        <Link className="app-sidebar__link" href="/app/screens/new"><Plus size={16} aria-hidden="true" /><span>New screen</span></Link>
        <Link className="app-sidebar__link" href="/explore"><Compass size={16} aria-hidden="true" /><span>Explore</span></Link>
        <Link className="app-sidebar__link" href="/app/screens"><Star size={16} aria-hidden="true" /><span>Saved screens</span></Link>
      </div>

      <div className="app-sidebar__group">
        <p className="app-sidebar__label">Resources</p>
        <Link className="app-sidebar__link" href="/methodology"><FileText size={16} aria-hidden="true" /><span>Methodology</span></Link>
        <Link className="app-sidebar__link" href="/data-sources"><BarChart3 size={16} aria-hidden="true" /><span>Data sources</span></Link>
      </div>

      <div className="app-sidebar__group">
        <p className="app-sidebar__label">Account</p>
        <Link className="app-sidebar__link" href="/app/account"><Settings size={16} aria-hidden="true" /><span>Account settings</span></Link>
      </div>
    </aside>
  );
}
