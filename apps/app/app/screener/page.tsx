import type { Metadata } from "next";
import { ScreenerClient } from "@/components/screener/ScreenerClient";
import { redirect } from "next/navigation";
import { hasAuthenticatedUser } from "@/lib/auth/require-user";
import { buildLoginHref } from "@/lib/auth/redirect";

export const metadata: Metadata = {
  title: "Stock Screener — Scrooner",
  description: "Find US companies in plain language, verify the exact criteria, and inspect every matched metric.",
};

export default async function ScreenerPage() {
  if (!(await hasAuthenticatedUser())) redirect(buildLoginHref("/screener"));
  const siteUrl = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:4321").replace(/\/$/, "");
  return <ScreenerClient siteUrl={siteUrl} />;
}
