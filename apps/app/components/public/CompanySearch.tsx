"use client";

import { FormEvent, useEffect, useId, useState } from "react";
import { useRouter } from "next/navigation";
import { addRecentCompany, loadCompanyDirectory, normalizeRecentCompanies, rankCompanyMatches, type SearchCompany } from "@/lib/company/search";

const RECENT_KEY = "scrooner:recent-companies";

// "hero" is the only variant ever rendered (the homepage hero box) -- the
// site's other search entry point, the sitewide command palette, is the
// separate SearchCommand component. A previously-supported "header" variant
// was dead code (never actually mounted anywhere) and was removed 2026-09-13.
export function CompanySearch() {
  const router = useRouter();
  const id = useId();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchCompany[]>([]);
  const [recent, setRecent] = useState<SearchCompany[]>(() => {
    if (typeof window === "undefined") return [];
    try { return normalizeRecentCompanies(JSON.parse(localStorage.getItem(RECENT_KEY) ?? "[]")); } catch { return []; }
  });
  const [open, setOpen] = useState(false);
  const [directory, setDirectory] = useState<SearchCompany[] | null>(null);

  // Loads the full ~6k-company directory once (module-level singleton, see
  // lib/company/search.ts) so every keystroke after that matches entirely
  // in the browser -- no network/DB round trip, no debounce needed.
  useEffect(() => {
    let cancelled = false;
    loadCompanyDirectory()
      .then((loaded) => { if (!cancelled) setDirectory(loaded); })
      .catch(() => {}); // stays null; the effect below falls back to the server endpoint
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (query.trim().length < 1) return;

    if (directory) return;

    // Directory not loaded yet (first paint, or the fetch failed) -- fall
    // back to the original debounced server-side search so the box still
    // works while/if the client-side path isn't available.
    const controller = new AbortController();
    const timeout = window.setTimeout(async () => {
      try {
        const response = await fetch(`/api/company-search?q=${encodeURIComponent(query)}`, { signal: controller.signal });
        if (response.ok) setResults((await response.json()).companies ?? []);
        else setResults([]);
      } catch (error) {
        if (!(error instanceof DOMException && error.name === "AbortError")) setResults([]);
      }
    }, 180);
    return () => { window.clearTimeout(timeout); controller.abort(); };
  }, [query, directory]);

  function submit(event: FormEvent) {
    event.preventDefault();
    const company = results[0];
    if (company) select(company);
  }

  function select(company: SearchCompany) {
    const next = addRecentCompany(recent, company);
    setRecent(next);
    localStorage.setItem(RECENT_KEY, JSON.stringify(next));
    router.push(`/stocks/${company.ticker.toLowerCase()}`);
  }

  const visible = query.trim() ? (directory ? rankCompanyMatches(directory, query, 8) : results) : recent;

  return (
    <form className="company-search company-search--hero" role="search" onSubmit={submit}>
      <label className="ds-sr-only" htmlFor={id}>Search companies</label>
      <input id={id} value={query} onChange={(event) => { const value = event.target.value; setQuery(value); if (!value.trim()) setResults([]); setOpen(true); }} onFocus={() => setOpen(true)} placeholder="Search company or ticker" autoComplete="off" />
      {open && visible.length > 0 && (
        <div className="company-search-results" role="listbox">
          {!query.trim() && <p className="company-search-results__label">Recent companies</p>}
          {visible.map((company) => (
            <button key={company.ticker} type="button" onClick={() => select(company)}>
              <strong>{company.ticker}</strong><span>{company.company_name}</span>
            </button>
          ))}
        </div>
      )}
    </form>
  );
}
