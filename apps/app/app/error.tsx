"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/Button";

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="main-content error-page" id="main-content">
      <p className="eyebrow">Scrooner</p>
      <h1>Something went wrong</h1>
      <p>We could not display this page. Your account and saved data were not changed.</p>
      <Button type="button" onClick={reset}>Try again</Button>
    </main>
  );
}
