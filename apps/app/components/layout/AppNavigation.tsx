"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { logout } from "@/app/auth/actions";

function active(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function AppNavigation({ signedIn, siteUrl }: { signedIn: boolean; siteUrl: string }) {
  const pathname = usePathname();
  const linkClass = (href: string) => [
    "app-shell__nav-link",
    active(pathname, href) ? "app-shell__nav-link--active" : "",
  ].filter(Boolean).join(" ");

  return (
    <nav className="app-shell__nav" aria-label="Primary navigation">
      {signedIn && <Link className={linkClass("/screener")} href="/screener" aria-current={active(pathname, "/screener") ? "page" : undefined}>Screener</Link>}
      {signedIn && <Link className={linkClass("/saved-screens")} href="/saved-screens" aria-current={active(pathname, "/saved-screens") ? "page" : undefined}>Saved screens</Link>}
      <a className="app-shell__nav-link app-shell__public-link" href={siteUrl}>Company research<span aria-hidden="true"> ↗</span></a>
      {signedIn ? (
        <>
          <Link className={linkClass("/account")} href="/account" aria-current={active(pathname, "/account") ? "page" : undefined}>Account</Link>
          <form action={logout}><button className="app-shell__nav-action" type="submit">Sign out</button></form>
        </>
      ) : <><Link className={linkClass("/login")} href="/login" aria-current={active(pathname, "/login") ? "page" : undefined}>Sign in</Link><Link className="ds-button ds-button--primary ds-button--small" href="/signup">Create account</Link></>}
    </nav>
  );
}
