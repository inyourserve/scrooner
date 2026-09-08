"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/Button";

export default function AppError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { console.error(error); }, [error]);
  return <main className="main-content workspace-content" id="main-content"><section className="workspace-empty" role="alert"><div><p className="workspace-eyebrow">Workspace unavailable</p><h1>We couldn&apos;t load this page.</h1><p>Your saved data has not been changed. Try loading the page again.</p></div><Button onClick={reset}>Try again</Button></section></main>;
}
