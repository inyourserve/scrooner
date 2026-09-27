"use client";

import { Search } from "lucide-react";
import { useEffect, useState, type KeyboardEvent } from "react";
import { useRouter } from "next/navigation";
import { Dialog } from "@/components/ui/Dialog";
import { addRecentCompany, loadCompanyDirectory, normalizeRecentCompanies, rankCompanyMatches, type SearchCompany } from "@/lib/company/search";

// The ⌘K "signature interaction" from doc/design/shadcn-system.md section 14.
// Sits alongside CompanySearch (the large inline box on the homepage hero)
// rather than replacing it -- this is the compact, global, keyboard-driven
// entry point used everywhere else (currently the site header).
const RECENT_KEY = "scrooner:recent-companies";

function readRecent(): SearchCompany[] {
  if (typeof window === "undefined") return [];
  try { return normalizeRecentCompanies(JSON.parse(localStorage.getItem(RECENT_KEY) ?? "[]")); } catch { return []; }
}

export function SearchCommand() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    function onKeyDown(event: globalThis.KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((value) => !value);
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <>
      <button type="button" className="search-command-trigger" onClick={() => setOpen(true)}>
        <Search size={16} aria-hidden="true" />
        <span>Search companies or tickers</span>
        <kbd className="ds-kbd">⌘K</kbd>
      </button>
      {/* Mounted fresh on every open so query/results/selection reset for
          free -- no effect needed to clear stale state from the last search. */}
      {open && <SearchCommandPanel onClose={() => setOpen(false)} />}
    </>
  );
}

function SearchCommandPanel({ onClose }: { onClose: () => void }) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchCompany[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);
  // Recomputed once per mount (the panel remounts fresh on every open), so
  // this never needs to be state -- it just reflects localStorage at open time.
  const [recent] = useState<SearchCompany[]>(readRecent);
  const [directory, setDirectory] = useState<SearchCompany[] | null>(null);

  // Same directory-based, zero-network-per-keystroke search as CompanySearch
  // (see lib/company/search.ts) -- this is the site's higher-traffic search
  // entry point (every page, not just the homepage), so it benefits even
  // more from not paying a Postgres round trip per character. The module-
  // level directory cache means a visit to the homepage first (or a prior
  // ⌘K open) already has this ready.
  useEffect(() => {
    let cancelled = false;
    loadCompanyDirectory()
      .then((loaded) => { if (!cancelled) setDirectory(loaded); })
      .catch(() => {}); // stays null; falls back to the server endpoint below
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (!query.trim()) return;

    if (directory) return;

    const controller = new AbortController();
    const timeout = window.setTimeout(async () => {
      try {
        const response = await fetch(`/api/company-search?q=${encodeURIComponent(query)}`, { signal: controller.signal });
        setResults(response.ok ? ((await response.json()).companies ?? []) : []);
      } catch (error) {
        if (!(error instanceof DOMException && error.name === "AbortError")) setResults([]);
      }
    }, 180);
    return () => { window.clearTimeout(timeout); controller.abort(); };
  }, [query, directory]);

  const visible = query.trim() ? (directory ? rankCompanyMatches(directory, query, 8) : results) : recent;

  function select(company: SearchCompany) {
    const next = addRecentCompany(recent, company);
    try { localStorage.setItem(RECENT_KEY, JSON.stringify(next)); } catch { /* private-mode storage */ }
    onClose();
    router.push(`/stocks/${company.ticker.toLowerCase()}`);
  }

  function onInputKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "ArrowDown") { event.preventDefault(); setActiveIndex((index) => Math.min(index + 1, visible.length - 1)); }
    else if (event.key === "ArrowUp") { event.preventDefault(); setActiveIndex((index) => Math.max(index - 1, 0)); }
    else if (event.key === "Enter") { event.preventDefault(); const company = visible[activeIndex]; if (company) select(company); }
  }

  return (
    <Dialog title="Search" onClose={onClose} closeLabel="Close search">
      <div className="search-command">
        <div className="search-command__field">
          <Search size={16} aria-hidden="true" />
          <input
            data-dialog-initial-focus
            value={query}
            onChange={(event) => {
              const value = event.target.value;
              setQuery(value);
              setActiveIndex(0);
              if (!value.trim()) setResults([]);
            }}
            onKeyDown={onInputKeyDown}
            placeholder="Search companies, tickers…"
            aria-label="Search companies or tickers"
            autoComplete="off"
          />
        </div>
        <div className="search-command__results" role="listbox" aria-label="Companies">
          {!query.trim() && recent.length > 0 && <p className="search-command__group-label">Recent</p>}
          {query.trim() && visible.length === 0 && <p className="search-command__empty">No matching companies.</p>}
          {visible.map((company, index) => (
            <button
              type="button"
              key={company.ticker}
              role="option"
              aria-selected={index === activeIndex}
              className={`search-command__result${index === activeIndex ? " is-active" : ""}`}
              onMouseEnter={() => setActiveIndex(index)}
              onClick={() => select(company)}
            >
              <strong>{company.ticker}</strong>
              <span>{company.company_name}</span>
              {company.exchange && <small>{company.exchange}</small>}
            </button>
          ))}
        </div>
      </div>
    </Dialog>
  );
}
