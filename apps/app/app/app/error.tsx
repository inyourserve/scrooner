"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/scrooner/EmptyState";

export default function AppError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { console.error(error); }, [error]);
  return <main className="main-content workspace-content" id="main-content"><section role="alert" aria-label="Workspace unavailable"><EmptyState icon={<AlertTriangle size={22} />} title="We couldn’t load this page" description="Your saved data has not been changed. Try loading the page again." action={<Button onClick={reset}>Try again</Button>} /></section></main>;
}
