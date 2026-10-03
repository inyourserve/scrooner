"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/scrooner/EmptyState";
import { PageShell } from "@/components/layout/PageShell";

export default function AppError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { console.error(error); }, [error]);
  return <PageShell><section role="alert" aria-label="Workspace unavailable"><EmptyState icon={<AlertTriangle size={22} />} title="This page didn’t load" description="Your saved research is safe. Try loading the page again." action={<Button onClick={reset}>Reload page</Button>} /></section></PageShell>;
}
