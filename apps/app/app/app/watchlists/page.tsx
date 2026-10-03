import type { Metadata } from "next";
import Link from "next/link";
import { Telescope } from "lucide-react";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import { PageHeader } from "@/components/layout/PageHeader";
import { PageShell } from "@/components/layout/PageShell";
import { EmptyState } from "@/components/scrooner/EmptyState";
import { Card } from "@/components/ui/Card";

export const metadata: Metadata = { title: "Watchlists — Scrooner" };

export default function WatchlistsPage() {
  return <PageShell>
    <PageHeader eyebrow="Research workspace" title="Watchlists" description="Keep the companies you’re following organized in one place." />
    <AppPageLayout>
      <Card><EmptyState bordered={false}
        icon={<Telescope size={22} aria-hidden="true" />}
        title="Watchlists are coming soon"
        description="You’ll be able to group companies and return to them as your research develops."
        action={<Link className="ds-button ds-button--secondary ds-button--small" href="/explore">Explore companies</Link>}
      /></Card>
    </AppPageLayout>
  </PageShell>;
}
