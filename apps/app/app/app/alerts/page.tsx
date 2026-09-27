import type { Metadata } from "next";
import Link from "next/link";
import { Bell } from "lucide-react";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/scrooner/EmptyState";
import { Card } from "@/components/ui/Card";

export const metadata: Metadata = { title: "Alerts — Scrooner" };

export default function AlertsPage() {
  return <main className="main-content" id="main-content">
    <PageHeader eyebrow="Your workspace" title="Alerts" description="Monitor meaningful changes without turning research into noise." />
    <AppPageLayout>
      <Card><EmptyState bordered={false}
        icon={<Bell size={22} aria-hidden="true" />}
        title="No alerts configured"
        description="Alert creation will appear here when monitoring is enabled."
        action={<Link className="ds-button ds-button--secondary ds-button--small" href="/app/watchlists">Open watchlists</Link>}
      /></Card>
    </AppPageLayout>
  </main>;
}
