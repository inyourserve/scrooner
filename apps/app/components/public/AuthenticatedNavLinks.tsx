"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/app", label: "Dashboard", active: (path: string) => path === "/app" },
  { href: "/explore", label: "Explore", active: (path: string) => path.startsWith("/explore") || path.startsWith("/stocks") },
  { href: "/app/screens", label: "Saved screens", active: (path: string) => path.startsWith("/app/screens") && !path.startsWith("/app/screens/new") },
  { href: "/app/watchlist", label: "Watchlist", active: (path: string) => path.startsWith("/app/watchlist") },
  { href: "/app/data-coverage", label: "Data coverage", active: (path: string) => path.startsWith("/app/data-coverage") },
  { href: "/app/screens/new", label: "Create screen", active: (path: string) => path.startsWith("/app/screens/new"), action: true },
];

export function AuthenticatedNavLinks() {
  const pathname = usePathname() ?? "";
  return <>{links.map((link) => (
    <Link
      aria-current={link.active(pathname) ? "page" : undefined}
      className={link.action ? "public-links__action" : undefined}
      href={link.href}
      key={link.href}
    >
      {link.label}
    </Link>
  ))}</>;
}
