import { ScreenerClient } from "@/components/screener/ScreenerClient";

export default function ScreenerPage() {
  const siteUrl = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:4321").replace(/\/$/, "");
  return <ScreenerClient siteUrl={siteUrl} />;
}
