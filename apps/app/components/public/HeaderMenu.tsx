"use client";

import Link from "next/link";
import { Activity, Bookmark, LayoutDashboard, Menu, Plus, Search, Star, X } from "lucide-react";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Popover } from "@/components/ui/Popover";

const menuLinks = [
  { href: "/app", label: "Dashboard", icon: LayoutDashboard, group: "workspace", authenticated: true, active: (path: string) => path === "/app" },
  { href: "/app/screens", label: "Saved screens", icon: Star, group: "workspace", authenticated: true, active: (path: string) => path.startsWith("/app/screens") && !path.startsWith("/app/screens/new") },
  { href: "/app/watchlist", label: "Watchlist", icon: Bookmark, group: "workspace", authenticated: true, active: (path: string) => path.startsWith("/app/watchlist") },
  { href: "/app/data-coverage", label: "Data coverage", icon: Activity, group: "workspace", authenticated: true, active: (path: string) => path.startsWith("/app/data-coverage") },
  { href: "/explore", label: "Explore companies", icon: Search, group: "research", authenticated: false, active: (path: string) => path.startsWith("/explore") || path.startsWith("/stocks") },
  { href: "/app/screens/new", label: "Create screen", icon: Plus, group: "research", authenticated: false, active: (path: string) => path.startsWith("/app/screens/new"), action: true },
] as const;

export function HeaderMenu({ authenticated }: { authenticated: boolean }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname() ?? "";
  const close = () => setOpen(false);

  const visibleLinks = menuLinks.filter((link) => authenticated || !link.authenticated);
  const workspaceLinks = visibleLinks.filter((link) => link.group === "workspace");
  const researchLinks = visibleLinks.filter((link) => link.group === "research");

  const renderLink = (link: (typeof menuLinks)[number]) => {
    const Icon = link.icon;
    const active = link.active(pathname);
    return (
      <Link
        aria-current={active ? "page" : undefined}
        className={"action" in link && link.action ?"header-menu__link header-menu__link--action" : "header-menu__link"}
        href={link.href}
        key={link.href}
        onClick={close}
      >
        <span className="header-menu__icon"><Icon size={16} aria-hidden="true" /></span>
        <span>{link.label}</span>
      </Link>
    );
  };

  return <div className="header-menu">
    <button className="header-menu__trigger" type="button" aria-label={open ? "Close navigation" : "Open navigation"} aria-haspopup="dialog" aria-expanded={open} onPointerDown={(event) => event.stopPropagation()} onClick={() => setOpen((value) => !value)}>
      {open ? <X size={18} aria-hidden="true" /> : <Menu size={18} aria-hidden="true" />}
    </button>
    {open && <Popover label="Navigation" onClose={close} className="header-menu__popover" size="small">
      <nav aria-label="Mobile navigation">
        {authenticated && <div className="header-menu__section">
          <p className="header-menu__eyebrow">Your workspace</p>
          {workspaceLinks.map(renderLink)}
        </div>}
        <div className="header-menu__section">
          {authenticated && <p className="header-menu__eyebrow">Research</p>}
          {researchLinks.map(renderLink)}
        </div>
      </nav>
    </Popover>}
  </div>;
}
