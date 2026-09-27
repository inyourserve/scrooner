import type { Metadata } from "next";
import { redirect } from "next/navigation";
import Link from "next/link";
import { CalendarDays, CheckCircle2, KeyRound, LogOut, Mail } from "lucide-react";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { logout } from "@/app/auth/actions";
import { getAuthEnvironmentStatus } from "@/lib/auth/config";
import { createClient } from "@/lib/supabase/server";
import styles from "./account.module.css";

export const metadata: Metadata = { title: "Account — Scrooner" };

export default async function AccountPage() {
  const status = getAuthEnvironmentStatus();
  if (!status.enabled) {
    return (
      <main id="main-content" className="main-content">
        <PageHeader eyebrow="Account settings" title="Account unavailable" description="Account settings could not be loaded in this environment." />
      </main>
    );
  }

  const supabase = await createClient();
  const { data, error } = await supabase.auth.getUser();
  if (error || !data.user) redirect("/login?redirect_url=%2Fapp%2Faccount");

  const email = data.user.email || "Not available";
  const initial = email.charAt(0).toUpperCase();
  const joined = new Intl.DateTimeFormat("en", { month: "long", year: "numeric" }).format(new Date(data.user.created_at));

  return (
    <main id="main-content" className="main-content">
      <PageHeader eyebrow="Settings" title="Account" description="Your identity and sign-in security." />

      <AppPageLayout>
        <section aria-labelledby="account-details"><Card className={styles.profile}>
          <div className={styles.avatar} aria-hidden="true">{initial}</div>
          <div className={styles.identity}>
            <div className={styles.identityHeading}>
              <h2 id="account-details">{email}</h2>
              <Badge tone={data.user.email_confirmed_at ? "positive" : "warning"}>
                {data.user.email_confirmed_at ? <CheckCircle2 size={12} aria-hidden="true" /> : null}
                {data.user.email_confirmed_at ? "Verified" : "Pending verification"}
              </Badge>
            </div>
            <p><Mail size={14} aria-hidden="true" /> Email account</p>
            <p><CalendarDays size={14} aria-hidden="true" /> Member since {joined}</p>
          </div>
        </Card></section>

        <section aria-labelledby="security-title"><Card className={styles.settings}>
          <header className={styles.sectionHeader}>
            <h2 id="security-title">Security</h2>
            <p>Manage how you access your account.</p>
          </header>
          <div className={styles.settingRow}>
            <div className={styles.settingIcon} aria-hidden="true"><KeyRound size={17} /></div>
            <div className={styles.settingCopy}><h3>Password</h3><p>Use a unique password you do not use elsewhere.</p></div>
            <Button asChild variant="secondary" size="small"><Link href="/app/account/update-password">Change password</Link></Button>
          </div>
          <div className={styles.settingRow}>
            <div className={styles.settingIcon} aria-hidden="true"><LogOut size={17} /></div>
            <div className={styles.settingCopy}><h3>Current session</h3><p>Sign out of Scrooner on this device.</p></div>
            <form action={logout}><Button variant="ghost" size="small" type="submit">Sign out</Button></form>
          </div>
        </Card></section>
      </AppPageLayout>
    </main>
  );
}
