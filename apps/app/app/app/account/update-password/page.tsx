import type { Metadata } from "next";
import { AuthForm } from "@/components/auth/AuthForm";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import { PageShell } from "@/components/layout/PageShell";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import styles from "../account.module.css";

export const metadata: Metadata = { title: "Change password — Scrooner" };

export default function UpdatePasswordPage() {
  return (
    <PageShell>
      <WorkspaceHeader eyebrow="Account security" title="Change password" description="Replace your current password with a strong, unique credential." />
      <AppPageLayout>
        <div className={styles.passwordContent}>
          <Link className={styles.backLink} href="/app/account"><ArrowLeft size={15} aria-hidden="true" /> Account</Link>
          <AuthForm mode="update" />
        </div>
      </AppPageLayout>
    </PageShell>
  );
}
