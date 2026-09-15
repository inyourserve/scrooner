import type { Metadata } from "next";
import { NaturalQueryPanel } from "@/components/screener/NaturalQueryPanel";

export const metadata: Metadata = {
  title: "Create screen — Scrooner",
  description: "Create a private stock screen using reported fundamentals.",
};
export default function NewScreenPage() {
  return (
    <main className="workspace-page screener-content" id="main-content">
      <NaturalQueryPanel metrics={[]} submitPath="/app/screens/new/raw" />
    </main>
  );
}
