import type { Metadata } from "next";
import { NaturalQueryPanel } from "@/components/screener/NaturalQueryPanel";
import { PageShell } from "@/components/layout/PageShell";

export const metadata: Metadata = {
  title: "Create screen — Scrooner",
  description: "Describe company criteria in plain English and create a repeatable screen over reported fundamentals.",
};
export default async function NewScreenPage({
  searchParams,
}: {
  searchParams: Promise<{ query?: string; q?: string; run?: string }>;
}) {
  const params = await searchParams;
  // `query` is the canonical screener URL contract used by results, save,
  // and edit flows. Keep `q` as a legacy alias so older shared links still
  // restore the editor instead of silently opening an empty form.
  const initialText = params.query ?? params.q ?? "";
  return (
    <PageShell className="screener-content">
      <NaturalQueryPanel
        metrics={[]}
        submitPath="/app/screens/new/raw"
        initialText={initialText}
        autoRun={params.run === "1" && initialText.trim().length > 0}
      />
    </PageShell>
  );
}
