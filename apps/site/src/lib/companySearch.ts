export interface SearchCompany {
  ticker: string;
  company_name: string;
  exchange: string | null;
  sector: string | null;
}

const MAX_RECENT_COMPANIES = 5;

export function normalizeCompanyQuery(value: string): string {
  return value.trim().replace(/\s+/g, " ").toLowerCase().slice(0, 64);
}

export function isSearchCompany(value: unknown): value is SearchCompany {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.ticker === "string" &&
    candidate.ticker.length > 0 &&
    typeof candidate.company_name === "string" &&
    candidate.company_name.length > 0 &&
    (candidate.exchange === null || typeof candidate.exchange === "string") &&
    (candidate.sector === null || typeof candidate.sector === "string")
  );
}

export function normalizeRecentCompanies(value: unknown): SearchCompany[] {
  if (!Array.isArray(value)) return [];

  const seen = new Set<string>();
  const companies: SearchCompany[] = [];
  for (const item of value) {
    if (!isSearchCompany(item)) continue;
    const ticker = item.ticker.trim().toUpperCase();
    if (!ticker || seen.has(ticker)) continue;
    seen.add(ticker);
    companies.push({
      ticker,
      company_name: item.company_name.trim(),
      exchange: item.exchange?.trim() || null,
      sector: item.sector?.trim() || null,
    });
    if (companies.length === MAX_RECENT_COMPANIES) break;
  }
  return companies;
}

export function addRecentCompany(
  recent: SearchCompany[],
  selected: SearchCompany,
): SearchCompany[] {
  return normalizeRecentCompanies([
    selected,
    ...recent.filter(
      (company) => company.ticker.toUpperCase() !== selected.ticker.toUpperCase(),
    ),
  ]);
}
