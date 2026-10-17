import Link from "next/link";
import { Search } from "lucide-react";
import type { Metadata } from "next";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import { PageShell } from "@/components/layout/PageShell";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import { WatchlistClient } from "@/components/watchlist/WatchlistClient";
import { Button } from "@/components/ui/Button";

export const metadata: Metadata = { title: "Watchlist — Scrooner" };

export default function WatchlistPage() {
  return <PageShell>
    <WorkspaceHeader eyebrow="Research workspace" title="Watchlist" description="Catch up on company results, fundamental changes, and the reasons you started following each business." actions={<Button asChild variant="secondary" leadingIcon={<Search size={15} aria-hidden="true" />}><Link href="/explore">Find companies</Link></Button>} />
    <AppPageLayout>
      <WatchlistClient />
    </AppPageLayout>
  </PageShell>;
}
