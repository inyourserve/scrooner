import type { Metadata } from "next";
import { ScreenerClient } from "@/components/screener/ScreenerClient";

export const metadata: Metadata = {
  title: "Screen results — Scrooner",
  description: "Companies matching your fundamental screen.",
};
export default function RawScreenPage() {
  return (
    <ScreenerClient
      siteUrl="/"
      autoRunInitialQuery
      routePath="/app/screens/new/raw"
      resultsFirst
    />
  );
}
