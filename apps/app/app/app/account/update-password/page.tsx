import type { Metadata } from "next";
import { AuthForm } from "@/components/auth/AuthForm";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import styles from "../account.module.css";

export const metadata: Metadata = { title: "Change password — Scrooner" };

export default function UpdatePasswordPage() {
  return (
    <main id="main-content" className="main-content">
      <AppPageLayout>
        <div className={styles.passwordContent}>
          <Link className={styles.backLink} href="/app/account"><ArrowLeft size={15} aria-hidden="true" /> Account</Link>
          <AuthForm mode="update" />
        </div>
      </AppPageLayout>
    </main>
  );
}
