import type { Metadata } from "next";
import Link from "next/link";
import { Telescope } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";

export const metadata: Metadata = { title: "Watchlists — Scrooner" };

export default function WatchlistsPage() {
  return <main className="main-content workspace-content" id="main-content"><PageHeader eyebrow="Your workspace" title="Watchlists" description="Organize companies around the questions you are researching." /><section className="workspace-empty" aria-labelledby="watchlists-empty-title"><Telescope size={22} aria-hidden="true" /><div><h2 id="watchlists-empty-title">No watchlists yet</h2><p>Watchlist creation will appear here when monitoring is enabled.</p></div><Link className="ds-button ds-button--secondary" href="/">Find a company</Link></section></main>;
}
