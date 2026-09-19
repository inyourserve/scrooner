"use client";

import Link from "next/link";
import { useAuthState } from "@/lib/auth/useAuthState";

// Renders nothing until a public-page visitor is confirmed signed in, then
// adds the one extra nav item AppShell's own header always shows (since it
// only renders for signed-in visitors already). Kept out of PublicHeader's
// server-rendered markup so an anonymous visitor never sees a flash of a
// link to a page they'd just get redirected away from.
export function DashboardNavLink({ active }: { active?: boolean }) {
  const { status } = useAuthState();
  if (status !== "authenticated") return null;
  return active ? <span aria-current="page">Dashboard</span> : <Link href="/app">Dashboard</Link>;
}
