import type { Metadata } from "next";
import type { ReactNode } from "react";
import { redirect } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { hasAuthenticatedUser } from "@/lib/auth/require-user";
import { buildLoginHref } from "@/lib/auth/redirect";
import "./workspace.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { robots: { index: false, follow: false } };

export default async function AuthenticatedLayout({ children }: { children: ReactNode }) {
  if (!(await hasAuthenticatedUser())) redirect(buildLoginHref("/app"));
  return <AppShell siteUrl="/stocks">{children}</AppShell>;
}
