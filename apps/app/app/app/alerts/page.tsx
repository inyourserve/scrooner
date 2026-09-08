import type { Metadata } from "next";
import Link from "next/link";
import { Bell } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";

export const metadata: Metadata = { title: "Alerts — Scrooner" };

export default function AlertsPage() {
  return <main className="main-content workspace-content" id="main-content"><PageHeader eyebrow="Your workspace" title="Alerts" description="Monitor meaningful changes without turning research into noise." /><section className="workspace-empty" aria-labelledby="alerts-empty-title"><Bell size={22} aria-hidden="true" /><div><h2 id="alerts-empty-title">No alerts configured</h2><p>Alert creation will appear here when monitoring is enabled.</p></div><Link className="ds-button ds-button--secondary" href="/app/watchlists">Open watchlists</Link></section></main>;
}
