import type { Metadata } from "next";
import { NaturalQueryPanel } from "@/components/screener/NaturalQueryPanel";

export const metadata: Metadata = {
  title: "Create screen — Scrooner",
  description: "Create a private stock screen using reported fundamentals.",
};
export default async function NewScreenPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; run?: string }>;
}) {
  const params = await searchParams;
  const initialText = params.q ?? "";
  return (
    <main className="workspace-page screener-content" id="main-content">
      <NaturalQueryPanel
        metrics={[]}
        submitPath="/app/screens/new/raw"
        initialText={initialText}
        autoRun={params.run === "1" && initialText.trim().length > 0}
      />
    </main>
  );
}
