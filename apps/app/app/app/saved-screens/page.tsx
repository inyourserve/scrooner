import type { Metadata } from "next";
import Link from "next/link";
import { Plus } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { SavedScreensClient } from "@/components/saved-screens/SavedScreensClient";
import { Button } from "@/components/ui/Button";
import styles from "./saved-screens.module.css";

export const metadata: Metadata = { title: "Saved screens — Scrooner" };

export default function SavedScreensPage() {
  return (
    <main className={`main-content ${styles.page}`} id="main-content">
      <div className={styles.heading}>
        <PageHeader eyebrow="Research library" title="Saved screens" description="Reusable investment criteria, ready to run against the latest company data." />
        <Button asChild leadingIcon={<Plus size={16} aria-hidden="true" />}><Link href="/app/screener">New screen</Link></Button>
      </div>
      <div className={styles.note}>
        <span aria-hidden="true" className={styles.noteMark}>i</span>
        <p><strong>Results stay current.</strong> Screens save criteria, not a frozen company list.</p>
      </div>
      <SavedScreensClient />
    </main>
  );
}
