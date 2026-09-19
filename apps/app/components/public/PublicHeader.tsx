import Link from "next/link";
import { SearchCommand } from "@/components/scrooner/SearchCommand";
import { BrandMark } from "@/components/ui/BrandMark";
import { AccountMenu } from "@/components/public/AccountMenu";
import { DashboardNavLink } from "@/components/public/DashboardNavLink";
import { HeaderAuthAction } from "@/components/public/HeaderAuthAction";

export type Current = "home" | "company" | "explore" | "methodology" | "data-sources" | "about" | "pricing" | "privacy" | "terms" | "dashboard";

// The one navigation shared by every page, signed in or not -- the public
// site and the authenticated /app section used to each carry their own
// separate header/nav implementation with different links and inconsistent
// login/logout handling. AppShell now renders this directly (passing
// `userEmail`, which it already knows server-side) instead of its own
// bespoke nav, so there is exactly one place that decides what the primary
// links are.
export function PublicHeader({
  current,
  skipHref = "#main-content",
  userEmail,
}: {
  current?: Current;
  skipHref?: string;
  /** Pass this only when the caller already knows the visitor is signed
      in, as whom (AppShell) -- skips the client-side session check
      entirely so the app's own header never flashes a "Sign in" button
      first. Omit on public pages, where sign-in state is unknown until
      checked client-side. */
  userEmail?: string | null;
}) {
  const authenticated = userEmail !== undefined;
  const item = (href: string, label: string, active: boolean) => active ? <span aria-current="page">{label}</span> : <Link href={href}>{label}</Link>;
  return <>
    <a className="public-skip-link" href={skipHref}>Skip to main content</a>
    <header className="public-header"><nav className="public-nav" aria-label="Primary navigation">
      <Link href="/" className="public-brand" aria-label="Scrooner home"><BrandMark /><span className="brand-name">scrooner</span></Link>
      <div className="public-links">
        {item("/explore", "Explore", current === "explore")}
        {item("/app/screens/new", "Create screen", false)}
        {authenticated ? item("/app", "Dashboard", current === "dashboard") : <DashboardNavLink active={current === "dashboard"} />}
      </div>
      <SearchCommand />
      {authenticated ? <AccountMenu email={userEmail} /> : <HeaderAuthAction />}
    </nav></header><div className="public-header-spacer" aria-hidden="true" />
  </>;
}
