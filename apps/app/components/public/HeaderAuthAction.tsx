"use client";

import Link from "next/link";
import { useAuthState } from "@/lib/auth/useAuthState";
import { AccountMenu } from "./AccountMenu";

// Public pages don't know server-side whether a visitor is signed in, so
// this checks client-side and swaps in place -- AppShell (which already
// knows, since its layout redirects anonymous visitors) skips this
// entirely and renders AccountMenu directly. See PublicHeader.
export function HeaderAuthAction() {
  const { status, email } = useAuthState();

  if (status === "authenticated") return <AccountMenu email={email} />;

  return (
    <Link
      className="ds-button ds-button--primary ds-button--small public-auth-action"
      href="/login"
      aria-busy={status === "checking"}
    >
      Sign in
    </Link>
  );
}
