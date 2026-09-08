import type { Metadata } from "next";
import { ScreenerClient } from "@/components/screener/ScreenerClient";

export const metadata: Metadata = {
  title: "Stock Screener — Scrooner",
  description: "Find US companies in plain language, verify the exact criteria, and inspect every matched metric.",
};
export const dynamic = "force-dynamic";

export default function ScreenerPage() {
  return <ScreenerClient siteUrl="/" />;
}
