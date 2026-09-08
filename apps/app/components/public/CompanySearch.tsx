"use client";

import { FormEvent, useEffect, useId, useState } from "react";
import { useRouter } from "next/navigation";
import { addRecentCompany, normalizeRecentCompanies, type SearchCompany } from "@/lib/company/search";

const RECENT_KEY = "scrooner:recent-companies";

export function CompanySearch({ variant = "header" }: { variant?: "header" | "hero" }) {
  const router = useRouter();
  const id = useId();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchCompany[]>([]);
  const [recent, setRecent] = useState<SearchCompany[]>(() => {
    if (typeof window === "undefined") return [];
    try { return normalizeRecentCompanies(JSON.parse(localStorage.getItem(RECENT_KEY) ?? "[]")); } catch { return []; }
  });
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (query.trim().length < 1) return;
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
  }, [query]);

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

  const visible = query.trim() ? results : recent;

  return (
    <form className={`company-search company-search--${variant}`} role="search" onSubmit={submit}>
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
