"use client";

import { useEffect } from "react";
import { RefreshCw, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { StatusPage } from "@/components/layout/StatusPage";

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
    <StatusPage code="500" eyebrow="Temporary problem" title="This page couldn’t load" description="Scrooner hit an unexpected issue while preparing this page. Your account, screens, and saved research haven’t been changed." icon={<ShieldAlert size={30} strokeWidth={1.7} />} primaryAction={<Button type="button" onClick={reset} leadingIcon={<RefreshCw size={16} aria-hidden="true" />}>Try again</Button>} detail={error.digest} />
  );
}
