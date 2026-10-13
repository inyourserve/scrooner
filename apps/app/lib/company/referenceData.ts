// Calls apps/backend's reference-data endpoints instead of querying
// Postgres directly (doc 54, 2026-10-13, by the same founder direction
// as the company page's 2026-10-03 move: Next.js must never hold a
// direct DB connection, consistency with the Screener's own
// architecture). This backs the site's least-personalized, most-
// repeat-traffic pages -- homepage, /stocks, /stocks/sector,
// /stocks/industry, /explore -- which previously queried Postgres
// directly on every request with `force-dynamic` and NO caching at
// all (doc 54's finding). The real queries and their Redis cache both
// moved to apps/backend (reference_data.py/routers/reference_data.py/
// cache.py's reference-data functions), same 1hr TTL already
// established for this exact data by the directory API route's own
// prior unstable_cache(revalidate: 3600).

import { backendUrl } from "@/lib/backend";

export interface CompanyDirectoryRow {
  ticker: string;
  company_name: string;
  exchange: string | null;
  sector: string | null;
}

export interface SectorSummaryRow {
  sector: string;
  slug: string;
  company_count: string;
}

export interface IndustrySummaryRow {
  y_industry: string;
  slug: string;
  company_count: string;
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(backendUrl(path), { headers: { accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Reference data service returned ${response.status} for ${path}`);
  }
  return (await response.json()) as T;
}

export function loadFullCompanyDirectory(): Promise<CompanyDirectoryRow[]> {
  return fetchJson<CompanyDirectoryRow[]>("/v1/directory");
}

export function getSectorList(): Promise<SectorSummaryRow[]> {
  return fetchJson<SectorSummaryRow[]>("/v1/sectors");
}

export function getIndustryList(): Promise<IndustrySummaryRow[]> {
  return fetchJson<IndustrySummaryRow[]>("/v1/industries");
}

export async function getCompaniesBySectorSlug(
  slug: string,
): Promise<{ sector: string; companies: CompanyDirectoryRow[] } | null> {
  const response = await fetch(backendUrl(`/v1/sectors/${encodeURIComponent(slug)}`), {
    headers: { accept: "application/json" },
  });
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error(`Reference data service returned ${response.status} for sector ${slug}`);
  }
  return (await response.json()) as { sector: string; companies: CompanyDirectoryRow[] };
}

export async function getCompaniesByIndustrySlug(
  slug: string,
): Promise<{ industry: string; companies: CompanyDirectoryRow[] } | null> {
  const response = await fetch(backendUrl(`/v1/industries/${encodeURIComponent(slug)}`), {
    headers: { accept: "application/json" },
  });
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error(`Reference data service returned ${response.status} for industry ${slug}`);
  }
  return (await response.json()) as { industry: string; companies: CompanyDirectoryRow[] };
}

// tickers is a fixed, small, caller-supplied list (homepage quick picks) --
// the cache key on the backend side is the normalized ticker set itself,
// so this is correct for any caller, not just the one list apps/app uses
// today.
export async function getCompaniesByTickers(tickers: string[]): Promise<CompanyDirectoryRow[]> {
  if (tickers.length === 0) return [];
  return fetchJson<CompanyDirectoryRow[]>(`/v1/companies?tickers=${tickers.map(encodeURIComponent).join(",")}`);
}
