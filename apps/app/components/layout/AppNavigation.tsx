"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ArrowUpRight, Bell, LayoutDashboard, ListFilter, LogOut, SearchCode, Settings, Star } from "lucide-react";
import { logout } from "@/app/auth/actions";

const workspaceLinks = [
  { href: "/app", label: "Dashboard", icon: LayoutDashboard },
  { href: "/app/screens/new", label: "Create screen", icon: SearchCode },
  { href: "/app/watchlists", label: "Watchlists", icon: ListFilter },
  { href: "/app/screens", label: "Saved screens", icon: Star },
  { href: "/app/alerts", label: "Alerts", icon: Bell },
] as const;

function isActive(pathname: string, href: string) {
  if (href === "/app/screens/new") return pathname === href;
  if (href === "/app/screens") {
    return pathname === href || (pathname.startsWith(`${href}/`) && pathname !== "/app/screens/new");
  }
  return href === "/app" ? pathname === href : pathname === href || pathname.startsWith(`${href}/`);
}

export function AppNavigation({ siteUrl }: { siteUrl: string }) {
  const pathname = usePathname();

  return (
    <nav className="app-shell__nav" aria-label="Workspace navigation">
      <div className="app-shell__nav-group">
        <p className="app-shell__nav-label">Workspace</p>
        <div className="app-shell__nav-list">
          {workspaceLinks.map(({ href, label, icon: Icon }) => {
            const current = isActive(pathname, href);
            return <Link key={href} className={`app-shell__nav-link${current ? " app-shell__nav-link--active" : ""}`} href={href} aria-current={current ? "page" : undefined}><Icon aria-hidden="true" size={17} strokeWidth={1.8} /><span>{label}</span></Link>;
          })}
        </div>
      </div>
      <div className="app-shell__nav-group app-shell__nav-group--account">
        <p className="app-shell__nav-label">Account</p>
        <div className="app-shell__nav-list">
          <a className="app-shell__nav-link" href={siteUrl}><ArrowUpRight aria-hidden="true" size={17} strokeWidth={1.8} /><span>Company research</span></a>
          <Link className={`app-shell__nav-link${isActive(pathname, "/app/account") ? " app-shell__nav-link--active" : ""}`} href="/app/account" aria-current={isActive(pathname, "/app/account") ? "page" : undefined}><Settings aria-hidden="true" size={17} strokeWidth={1.8} /><span>Account settings</span></Link>
          <form action={logout}><button className="app-shell__nav-link app-shell__nav-action" type="submit"><LogOut aria-hidden="true" size={17} strokeWidth={1.8} /><span>Sign out</span></button></form>
        </div>
      </div>
    </nav>
  );
}
