import type { Metadata } from "next";
import Link from "next/link";
import { Bell, Bookmark, ChevronRight, Search, Telescope } from "lucide-react";

export const metadata: Metadata = { title: "Research workspace — Scrooner" };

const actions = [
  { href: "/app/screens/new", icon: Search, title: "Run a screen", copy: "Find companies using reported fundamentals." },
  { href: "/app/screens", icon: Bookmark, title: "Saved screens", copy: "Return to criteria you use repeatedly." },
  { href: "/app/watchlists", icon: Telescope, title: "Watchlists", copy: "Organize companies you want to follow." },
  { href: "/app/alerts", icon: Bell, title: "Alerts", copy: "Review the monitoring workspace." },
];

export default function AppHome() {
  return <main className="workspace-page" id="main-content">
    <header className="workspace-hero">
      <p className="workspace-eyebrow">Research workspace</p>
      <h1>Overview</h1>
      <p>Screen the market, keep useful criteria, and organize companies for deeper review.</p>
      <Link className="ds-button ds-button--primary" href="/app/screens/new">Start a screen <ChevronRight size={15} aria-hidden="true" /></Link>
    </header>
    <section className="workspace-section" aria-labelledby="workspace-actions-title">
      <div className="workspace-section__heading"><div><p className="workspace-eyebrow">Workspace</p><h2 id="workspace-actions-title">Continue your research</h2></div></div>
      <div className="workspace-action-grid">{actions.map(({ href, icon: Icon, title, copy }) => <Link href={href} className="workspace-action" key={href}><span className="workspace-action__icon"><Icon size={18} strokeWidth={1.8} aria-hidden="true" /></span><span><strong>{title}</strong><small>{copy}</small></span><ChevronRight className="workspace-action__arrow" size={16} aria-hidden="true" /></Link>)}</div>
    </section>
    <section className="workspace-note" aria-labelledby="workspace-note-title"><div><p className="workspace-eyebrow">Principle</p><h2 id="workspace-note-title">Evidence before opinion</h2></div><p>Scrooner screens narrow the research universe. Verify important conclusions against company filings and source context.</p></section>
  </main>;
}
