export interface SearchCompany {
  ticker: string;
  company_name: string;
  exchange: string | null;
  sector: string | null;
}

export function normalizeCompanyQuery(value: string): string {
  return value.trim().replace(/\s+/g, " ").toLowerCase().slice(0, 64);
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
