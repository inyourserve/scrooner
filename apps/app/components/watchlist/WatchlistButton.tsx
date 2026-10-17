"use client";

import { BookmarkCheck, BookmarkPlus } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { buildLoginHref } from "@/lib/auth/redirect";
import { Button } from "@/components/ui/Button";

export function WatchlistButton({ companyId }: { companyId: number }) {
  const pathname = usePathname();
  const router = useRouter();
  const [inWatchlist, setInWatchlist] = useState(false);
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    let active = true;
    void fetch(`/api/watchlist?company_id=${companyId}`, { cache: "no-store" }).then(async (response) => {
      if (!active) return;
      if (response.status === 401) { setAuthenticated(false); return; }
      if (!response.ok) { setAuthenticated(null); return; }
      const payload = await response.json() as { contains: boolean };
      if (active) { setAuthenticated(true); setInWatchlist(payload.contains); }
    }).catch(() => { if (active) setAuthenticated(null); });
    return () => { active = false; };
  }, [companyId]);

  async function handleClick() {
    if (authenticated === false) {
      router.push(buildLoginHref(pathname));
      return;
    }

    if (authenticated === true && inWatchlist) {
      router.push("/app/watchlist");
      return;
    }

    setBusy(true);
    setMessage("");
    try {
      const response = await fetch("/api/watchlist", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ company_id: companyId }),
      });
      if (response.status === 401) {
        router.push(buildLoginHref(pathname));
        return;
      }
      if (!response.ok) throw new Error("Watchlist could not be updated.");
      setAuthenticated(true);
      setInWatchlist(true);
      setMessage("Added to watchlist");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Watchlist could not be updated.");
    } finally {
      setBusy(false);
    }
  }

  return <div className="watchlist-action"><Button type="button" size="small" variant={inWatchlist ? "secondary" : "primary"} loading={busy} loadingLabel="Adding…" leadingIcon={inWatchlist ? <BookmarkCheck size={16} aria-hidden="true" /> : <BookmarkPlus size={16} aria-hidden="true" />} onClick={() => void handleClick()}>{inWatchlist ? "In watchlist" : "Add to watchlist"}</Button><span className="sr-only" role="status" aria-live="polite">{message}</span></div>;
}
