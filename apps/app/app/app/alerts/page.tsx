import type { Metadata } from "next";
import Link from "next/link";
import { Bell, FileText, LineChart, Radar } from "lucide-react";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import { PageShell } from "@/components/layout/PageShell";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import { EmptyState } from "@/components/scrooner/EmptyState";
import { Card } from "@/components/ui/Card";
import styles from "./alerts.module.css";

export const metadata: Metadata = { title: "Alerts — Scrooner" };

export default function AlertsPage() {
  return <PageShell>
    <WorkspaceHeader eyebrow="Research workspace" title="Alerts" description="Monitor material changes across the companies and screens you follow—without the market noise." />
    <AppPageLayout>
      <div className={styles.layout}>
        <Card className={styles.emptyCard}><EmptyState bordered={false}
          icon={<Bell size={22} aria-hidden="true" />}
          title="Your alert inbox is ready for signals"
          description="Alert delivery is coming next. In the meantime, build the saved screens and watchlist that will power your monitoring."
          action={<Link className="ds-button ds-button--primary ds-button--small" href="/app/watchlist">Open watchlist</Link>}
        /></Card>
        <Card className={styles.preview}>
          <div className={styles.previewHeader}><h2>What you’ll monitor</h2><span>Coming next</span></div>
          <ul className={styles.signalList}>
            <li className={styles.signal}><span className={styles.signalIcon}><FileText size={15} aria-hidden="true" /></span><div><strong>New company filings</strong><p>Know when a followed company files a 10-K, 10-Q, or material 8-K.</p></div></li>
            <li className={styles.signal}><span className={styles.signalIcon}><LineChart size={15} aria-hidden="true" /></span><div><strong>Metric changes</strong><p>Track meaningful moves in the fundamentals behind your thesis.</p></div></li>
            <li className={styles.signal}><span className={styles.signalIcon}><Radar size={15} aria-hidden="true" /></span><div><strong>Screen matches</strong><p>See when a company enters or exits one of your saved screens.</p></div></li>
          </ul>
          <p className={styles.note}>Only material events will be surfaced. Delivery controls will be available before alerts go live.</p>
        </Card>
      </div>
    </AppPageLayout>
  </PageShell>;
}
