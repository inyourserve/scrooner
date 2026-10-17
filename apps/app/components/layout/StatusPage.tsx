import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowLeft, Home } from "lucide-react";
import { PublicFooter } from "@/components/public/PublicFooter";
import { PublicHeader } from "@/components/public/PublicHeader";
import { Button } from "@/components/ui/Button";

type StatusPageProps = {
  code: string;
  eyebrow: string;
  title: string;
  description: string;
  icon: ReactNode;
  primaryAction: ReactNode;
  secondaryHref?: string;
  secondaryLabel?: string;
  detail?: string;
};

export function StatusPage({ code, eyebrow, title, description, icon, primaryAction, secondaryHref = "/", secondaryLabel = "Back to home", detail }: StatusPageProps) {
  return <div className="public-site status-page-shell">
    <PublicHeader />
    <main id="main-content" className="status-page" tabIndex={-1}>
      <section className="status-page__card" aria-labelledby="status-page-title">
        <div className="status-page__visual" aria-hidden="true"><span className="status-page__orb">{icon}</span><span className="status-page__code">{code}</span></div>
        <div className="status-page__content">
          <p className="status-page__eyebrow">{eyebrow}</p>
          <h1 id="status-page-title">{title}</h1>
          <p className="status-page__description">{description}</p>
          <div className="status-page__actions">{primaryAction}<Button asChild variant="outline" leadingIcon={<Home size={16} aria-hidden="true" />}><Link href={secondaryHref}>{secondaryLabel}</Link></Button></div>
          {detail ? <p className="status-page__detail">Reference: <code>{detail}</code></p> : null}
        </div>
      </section>
      <Link className="status-page__back" href="/explore"><ArrowLeft size={15} aria-hidden="true" /> Explore companies and screens</Link>
    </main>
    <PublicFooter />
  </div>;
}
