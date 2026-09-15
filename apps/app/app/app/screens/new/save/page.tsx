import type { Metadata } from "next";
import { SaveScreenPageClient } from "@/components/saved-screens/SaveScreenPageClient";

export const metadata: Metadata = {
  title: "Save query — Scrooner",
  description: "Save this screen to your private research library.",
};

export default function SaveQueryPage() {
  return <SaveScreenPageClient />;
}
