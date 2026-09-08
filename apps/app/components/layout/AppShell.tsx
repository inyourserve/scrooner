import type { ReactNode } from "react";
import Link from "next/link";
import { AppNavigation } from "@/components/layout/AppNavigation";
import { SearchCommand } from "@/components/scrooner/SearchCommand";
import { BrandMark } from "@/components/ui/BrandMark";

export async function AppShell({ children, siteUrl }: { children: ReactNode; siteUrl: string }) {
  return (
    <div className="app-shell">
      <a className="app-shell__skip-link" href="#main-content">Skip to main content</a>
      <header className="app-shell__header">
        <div className="app-shell__header-inner">
          <Link className="app-shell__brand" href="/app" aria-label="Scrooner workspace home"><BrandMark /><span>scrooner</span><small>Workspace</small></Link>
          <div className="app-shell__search" aria-label="Company search"><SearchCommand /></div>
        </div>
      </header>
      <div className="app-shell__workspace">
        <aside className="app-shell__sidebar"><AppNavigation siteUrl={siteUrl} /></aside>
        <div className="app-shell__stage">
          <div className="app-shell__content">{children}</div>
        </div>
      </div>
    </div>
  );
}
