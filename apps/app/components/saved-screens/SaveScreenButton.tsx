"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/Button";
import type { ScreenQueryPayload } from "@/lib/screener/types";

export const SAVE_QUERY_SESSION_KEY = "scrooner.save-query";

export function SaveScreenButton({ query, runId }: { query: ScreenQueryPayload; runId?: string }) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();

  function openSavePage() {
    const key = runId || "draft";
    window.sessionStorage.setItem(`${SAVE_QUERY_SESSION_KEY}:${key}`, JSON.stringify(query));
    const params = new URLSearchParams(searchParams);
    if (runId) params.set("run", runId);
    params.set("from", `${pathname}?${searchParams}`);
    router.push(`/app/screens/new/save?${params}`);
  }

  return <div className="save-screen-control"><Button type="button" variant="secondary" onClick={openSavePage}>Save screen</Button></div>;
}
