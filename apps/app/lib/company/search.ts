export interface SearchCompany {
  ticker: string;
  company_name: string;
  exchange: string | null;
  sector: string | null;
}

export function normalizeCompanyQuery(value: string): string {
  return value.trim().replace(/\s+/g, " ").toLowerCase().slice(0, 64);
}

// Client-side directory cache + ranking for the homepage search box (see
// CompanySearch.tsx and /api/company-search/directory). The whole active
// -company universe is small enough (~6k rows, ~250KB) to ship once and
// search entirely in the browser -- zero network/DB round trip per
// keystroke, which is the actual "fastest possible" answer for a universe
// this size, not a faster server query.
const DIRECTORY_CACHE_KEY = "scrooner:company-directory:v1";
const DIRECTORY_URL = "/api/company-search/directory";

type DirectoryTuple = [string, string, string | null, string | null];

interface DirectoryCache {
  generatedAt: string;
  companies: DirectoryTuple[];
}

function toSearchCompany([ticker, company_name, exchange, sector]: DirectoryTuple): SearchCompany {
  return { ticker, company_name, exchange, sector };
}

function readCachedDirectory(): DirectoryCache | null {
  try {
    const raw = localStorage.getItem(DIRECTORY_CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed.generatedAt !== "string" || !Array.isArray(parsed.companies)) return null;
    return parsed as DirectoryCache;
  } catch {
    return null;
  }
}

function writeCachedDirectory(cache: DirectoryCache): void {
  try {
    localStorage.setItem(DIRECTORY_CACHE_KEY, JSON.stringify(cache));
  } catch {
    // Best-effort only -- a full page-load fetch next time is a fine fallback.
  }
}

let directoryPromise: Promise<SearchCompany[]> | null = null;

// Loads the full directory once per browser session (module-level singleton,
// so mounting CompanySearch twice on one page -- header + hero -- never
// double-fetches), reusing a same-day localStorage cache across page loads.
export function loadCompanyDirectory(): Promise<SearchCompany[]> {
  if (directoryPromise) return directoryPromise;

  directoryPromise = (async () => {
    const today = new Date().toISOString().slice(0, 10);
    const cached = readCachedDirectory();
    if (cached && cached.generatedAt === today) {
      return cached.companies.map(toSearchCompany);
    }
    const response = await fetch(DIRECTORY_URL);
    if (!response.ok) throw new Error(`directory fetch failed: ${response.status}`);
    const data = (await response.json()) as { companies: DirectoryTuple[]; generatedAt: string };
    writeCachedDirectory(data);
    return data.companies.map(toSearchCompany);
  })().catch((error) => {
    directoryPromise = null; // allow a retry on the next call
    throw error;
  });

  return directoryPromise;
}

// Mirrors searchCompanyDirectory's SQL ranking exactly (apps/app/lib/company/db.ts):
// exact ticker match, then exact name match, then ticker-prefix, then
// name/display-name-prefix -- tie-broken by ticker length, then ticker.
export function rankCompanyMatches(directory: SearchCompany[], query: string, limit = 8): SearchCompany[] {
  const normalized = normalizeCompanyQuery(query);
  if (!normalized) return [];

  const scored: { company: SearchCompany; rank: number }[] = [];
  for (const company of directory) {
    const ticker = company.ticker.toLowerCase();
    const name = company.company_name.toLowerCase();
    let rank: number;
    if (ticker === normalized) rank = 0;
    else if (name === normalized) rank = 1;
    else if (ticker.startsWith(normalized)) rank = 2;
    else if (name.startsWith(normalized)) rank = 3;
    else continue;
    scored.push({ company, rank });
  }

  scored.sort((a, b) => {
    if (a.rank !== b.rank) return a.rank - b.rank;
    if (a.company.ticker.length !== b.company.ticker.length) return a.company.ticker.length - b.company.ticker.length;
    return a.company.ticker.localeCompare(b.company.ticker);
  });

  return scored.slice(0, limit).map((entry) => entry.company);
}

const MAX_RECENT_COMPANIES = 5;
export function isSearchCompany(value: unknown): value is SearchCompany {
  if (!value || typeof value !== "object") return false;
  const item = value as Record<string, unknown>;
  return typeof item.ticker === "string" && Boolean(item.ticker) && typeof item.company_name === "string" && Boolean(item.company_name) && (item.exchange === null || typeof item.exchange === "string") && (item.sector === null || typeof item.sector === "string");
}
export function normalizeRecentCompanies(value: unknown): SearchCompany[] {
  if (!Array.isArray(value)) return [];
  const seen = new Set<string>();
  return value.filter(isSearchCompany).map((item) => ({ ...item, ticker: item.ticker.trim().toUpperCase(), company_name: item.company_name.trim() })).filter((item) => item.ticker && !seen.has(item.ticker) && Boolean(seen.add(item.ticker))).slice(0, MAX_RECENT_COMPANIES);
}
export function addRecentCompany(recent: SearchCompany[], selected: SearchCompany) {
  return normalizeRecentCompanies([selected, ...recent.filter((item) => item.ticker.toUpperCase() !== selected.ticker.toUpperCase())]);
}
