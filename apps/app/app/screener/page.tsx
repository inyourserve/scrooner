import type { Metadata } from "next";
import { ScreenerClient } from "@/components/screener/ScreenerClient";

export const metadata: Metadata = {
  title: "Stock Screener — Scrooner",
  description: "Find US companies in plain language, verify the exact criteria, and inspect every matched metric.",
};

export default function ScreenerPage() {
  const siteUrl = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:4321").replace(/\/$/, "");
  return <ScreenerClient siteUrl={siteUrl} />;
}
