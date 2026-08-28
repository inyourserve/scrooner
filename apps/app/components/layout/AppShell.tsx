import type { ReactNode } from "react";
import { BrandMark } from "@/components/ui/BrandMark";
import { logout } from "@/app/auth/actions";
import { getAuthEnvironmentStatus } from "@/lib/auth/config";
import { createClient } from "@/lib/supabase/server";

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
          <a className="app-shell__brand" href="/screener" aria-label="Scrooner app home">
            <BrandMark />
            <span>scrooner</span>
          </a>
          <nav className="app-shell__nav" aria-label="Primary navigation">
            <a className="app-shell__nav-link app-shell__nav-link--active" href="/screener" aria-current="page">Screener</a>
            <a className="app-shell__nav-link" href="/saved-screens">Saved screens</a>
            <a className="app-shell__nav-link app-shell__public-link" href={siteUrl}>Company research<span aria-hidden="true"> ↗</span></a>
            {signedIn ? <><a className="app-shell__nav-link" href="/account">Account</a><form action={logout}><button className="app-shell__nav-action" type="submit">Sign out</button></form></> : <a className="app-shell__nav-link" href="/login">Sign in</a>}
          </nav>
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
