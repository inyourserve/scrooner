import type { Metadata } from "next";
import { ScreenerClient } from "@/components/screener/ScreenerClient";

export const metadata: Metadata = {
  title: "Create screen — Scrooner",
  description: "Create a private stock screen using reported fundamentals.",
};
export const dynamic = "force-dynamic";

export default function NewScreenPage() {
  return <ScreenerClient siteUrl="/" />;
}
