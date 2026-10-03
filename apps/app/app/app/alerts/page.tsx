import type { Metadata } from "next";
import Link from "next/link";
import { Bell } from "lucide-react";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import { PageHeader } from "@/components/layout/PageHeader";
import { PageShell } from "@/components/layout/PageShell";
import { EmptyState } from "@/components/scrooner/EmptyState";
import { Card } from "@/components/ui/Card";

export const metadata: Metadata = { title: "Alerts — Scrooner" };

export default function AlertsPage() {
  return <PageShell>
    <PageHeader eyebrow="Research workspace" title="Alerts" description="Stay informed when the companies you follow change in meaningful ways." />
    <AppPageLayout>
      <Card><EmptyState bordered={false}
        icon={<Bell size={22} aria-hidden="true" />}
        title="Alerts are coming soon"
        description="You’ll be able to monitor important changes without adding noise to your research."
        action={<Link className="ds-button ds-button--secondary ds-button--small" href="/app/screens">View saved screens</Link>}
      /></Card>
    </AppPageLayout>
  </PageShell>;
}
