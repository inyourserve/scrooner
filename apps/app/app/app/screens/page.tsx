import type { Metadata } from "next";
import Link from "next/link";
import { Plus } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { SavedScreensClient } from "@/components/saved-screens/SavedScreensClient";
import { Button } from "@/components/ui/Button";
import { backendUrl } from "@/lib/backend";
import { buildLoginHref } from "@/lib/auth/redirect";
import { createClient } from "@/lib/supabase/server";
import type { SavedScreen } from "@/lib/saved-screens/types";
import { redirect } from "next/navigation";
import styles from "../saved-screens/saved-screens.module.css";

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
    <main className={`main-content ${styles.page}`} id="main-content">
      <div className={styles.heading}>
        <PageHeader eyebrow="Research library" title="Saved screens" description="Reusable investment criteria, ready to run against the latest company data." />
        <Button asChild leadingIcon={<Plus size={16} aria-hidden="true" />}><Link href="/app/screens/new">New screen</Link></Button>
      </div>
      <div className={styles.note}>
        <span aria-hidden="true" className={styles.noteMark}>i</span>
        <p><strong>Results open instantly.</strong> Refresh a screen only when you want to run it against newer data.</p>
      </div>
      <SavedScreensClient initialScreens={screens} />
    </main>
  );
}
