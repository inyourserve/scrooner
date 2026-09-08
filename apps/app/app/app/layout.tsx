import type { ReactNode } from "react";
import { redirect } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { hasAuthenticatedUser } from "@/lib/auth/require-user";
import { buildLoginHref } from "@/lib/auth/redirect";
import "./workspace.css";

export const dynamic = "force-dynamic";

export default async function AuthenticatedLayout({ children }: { children: ReactNode }) {
  if (!(await hasAuthenticatedUser())) redirect(buildLoginHref("/app"));
  return <AppShell siteUrl="/stocks">{children}</AppShell>;
}
