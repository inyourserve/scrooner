import type { Metadata } from "next";
import Link from "next/link";
import { Plus } from "lucide-react";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import { PageShell } from "@/components/layout/PageShell";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import { SavedScreensClient } from "@/components/saved-screens/SavedScreensClient";
import { Button } from "@/components/ui/Button";
import { backendUrl } from "@/lib/backend";
import { buildLoginHref } from "@/lib/auth/redirect";
import { createClient } from "@/lib/supabase/server";
import type { SavedScreen } from "@/lib/saved-screens/types";
import { redirect } from "next/navigation";

export const metadata: Metadata = { title: "Saved screens — Scrooner" };
export const dynamic = "force-dynamic";

export default async function ScreensPage() {
  const supabase = await createClient();
  const { data } = await supabase.auth.getSession();
  if (!data.session?.access_token) redirect(buildLoginHref("/app/screens"));
  const response = await fetch(backendUrl("/v1/screens"), {
    cache: "no-store",
    headers: { accept: "application/json", authorization: `Bearer ${data.session.access_token}` },
  });
  if (!response.ok) throw new Error("Saved screens could not be loaded.");
  const screens = await response.json() as SavedScreen[];

  return (
    <PageShell>
      <WorkspaceHeader eyebrow="Screen library" title="Saved screens" description="Reopen your investment criteria, review saved results, or refresh them against the latest available data." actions={<Button asChild leadingIcon={<Plus size={16} aria-hidden="true" />}><Link href="/app/screens/new">Create screen</Link></Button>} />
      <AppPageLayout>
        <SavedScreensClient initialScreens={screens} />
      </AppPageLayout>
    </PageShell>
  );
}
