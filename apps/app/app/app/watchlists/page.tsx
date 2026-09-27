import type { Metadata } from "next";
import Link from "next/link";
import { Telescope } from "lucide-react";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/scrooner/EmptyState";
import { Card } from "@/components/ui/Card";

export const metadata: Metadata = { title: "Watchlists — Scrooner" };

export default function WatchlistsPage() {
  return <main className="main-content" id="main-content">
    <PageHeader eyebrow="Your workspace" title="Watchlists" description="Organize companies around the questions you are researching." />
    <AppPageLayout>
      <Card><EmptyState bordered={false}
        icon={<Telescope size={22} aria-hidden="true" />}
        title="No watchlists yet"
        description="Watchlist creation will appear here when monitoring is enabled."
        action={<Link className="ds-button ds-button--secondary ds-button--small" href="/">Find a company</Link>}
      /></Card>
    </AppPageLayout>
  </main>;
}
