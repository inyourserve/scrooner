import type { ReactNode } from "react";
import { BrandMark } from "@/components/ui/BrandMark";
import { getAuthEnvironmentStatus } from "@/lib/auth/config";
import { createClient } from "@/lib/supabase/server";
import { AppNavigation } from "@/components/layout/AppNavigation";

export async function AppShell({ children, siteUrl }: { children: ReactNode; siteUrl: string }) {
  let signedIn = false;
  if (getAuthEnvironmentStatus().enabled) {
    const supabase = await createClient();
    const { data } = await supabase.auth.getClaims();
    signedIn = Boolean(data?.claims);
  }
  return (
    <div className="app-shell">
      <a className="app-shell__skip-link" href="#main-content">Skip to main content</a>
      <header className="app-shell__header">
        <div className="app-shell__header-inner">
          <a className="app-shell__brand" href={signedIn ? "/screener" : "/login"} aria-label="Scrooner app home">
            <BrandMark />
            <span>scrooner</span>
          </a>
          <AppNavigation signedIn={signedIn} siteUrl={siteUrl} />
        </div>
      </header>
      <div className="app-shell__content">{children}</div>
      <footer>
        <div className="app-shell__footer-inner">
          <p>Research tool, not investment advice. Values may be delayed or unavailable.</p>
        </div>
      </footer>
    </div>
  );
}
