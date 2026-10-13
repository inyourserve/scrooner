import type { MetadataRoute } from "next";
import { loadFullCompanyDirectory, getSectorList, getIndustryList } from "@/lib/company/referenceData";

// Calls apps/backend instead of querying Postgres directly, which also
// replaces this file's own unstable_cache(revalidate: 3600) wrapper
// (doc 54, 2026-10-13): unstable_cache's default handler is per server
// PROCESS, not shared -- the same gap already found and fixed for the
// company page on 2026-09-15. apps/backend's Redis cache (shared across
// instances) now does this job instead, at the same 1hr freshness this
// file already had.
//
// force-dynamic is still required, same reasoning this file already had
// before this change (sitemaps are prerendered by default) -- rendering
// at request time, not build time, is what's needed when the data
// source is a fetch() to a backend that isn't running during `next
// build` (CI has none). This was never actually about Postgres vs.
// apps/backend; removing this export broke CI's build (found live
// 2026-10-13) because it changed WHEN the fetch happens, not just WHERE
// it goes.
export const dynamic = "force-dynamic";

// Base URL comes from the same env var already used elsewhere in this app
// (see .env.example) -- never hardcoded, so a staging/preview deploy never
// accidentally submits production URLs to a crawler.
const BASE_URL = (process.env.NEXT_PUBLIC_SCROONER_URL ?? "https://scrooner.com").replace(/\/$/, "");

// Static marketing/reference pages worth crawling. Deliberately excludes:
// auth pages (/login, /signup, /forgot-password, /account*) -- no SEO
// value, and disallowed in robots.ts; legacy redirect-only routes
// (/screener, /saved-screens) -- next.config.ts already 308s these
// elsewhere, listing them here would just submit a redirect to Google;
// everything under /app/* -- the authenticated product, not indexable.
const STATIC_PAGES: { path: string; changeFrequency: MetadataRoute.Sitemap[number]["changeFrequency"]; priority: number }[] = [
  { path: "/", changeFrequency: "daily", priority: 1 },
  { path: "/stocks", changeFrequency: "daily", priority: 0.9 },
  { path: "/stocks/sector", changeFrequency: "weekly", priority: 0.6 },
  { path: "/stocks/industry", changeFrequency: "weekly", priority: 0.6 },
  { path: "/explore", changeFrequency: "weekly", priority: 0.7 },
  { path: "/about", changeFrequency: "monthly", priority: 0.5 },
  { path: "/pricing", changeFrequency: "monthly", priority: 0.5 },
  { path: "/methodology", changeFrequency: "monthly", priority: 0.5 },
  { path: "/data-sources", changeFrequency: "monthly", priority: 0.4 },
  { path: "/privacy", changeFrequency: "yearly", priority: 0.2 },
  { path: "/terms", changeFrequency: "yearly", priority: 0.2 },
];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [directory, sectors, industries] = await Promise.all([
    loadFullCompanyDirectory(),
    getSectorList(),
    getIndustryList(),
  ]);

  const now = new Date();
  const staticEntries: MetadataRoute.Sitemap = STATIC_PAGES.map((page) => ({
    url: `${BASE_URL}${page.path}`,
    lastModified: now,
    changeFrequency: page.changeFrequency,
    priority: page.priority,
  }));

  // Real per-company pages -- the actual distribution surface (doc 01's
  // "distribution moat"): ~5,282 active companies today, well under
  // Google's 50,000-URL-per-sitemap limit, so a single file is enough for
  // now (see generateSitemaps() if that ever needs splitting).
  const companyEntries: MetadataRoute.Sitemap = directory.map((company) => ({
    url: `${BASE_URL}/stocks/${company.ticker.toLowerCase()}`,
    lastModified: now,
    changeFrequency: "daily",
    priority: 0.8,
  }));

  const sectorEntries: MetadataRoute.Sitemap = sectors.map((sector) => ({
    url: `${BASE_URL}/stocks/sector/${sector.slug}`,
    lastModified: now,
    changeFrequency: "weekly",
    priority: 0.5,
  }));

  const industryEntries: MetadataRoute.Sitemap = industries.map((industry) => ({
    url: `${BASE_URL}/stocks/industry/${industry.slug}`,
    lastModified: now,
    changeFrequency: "weekly",
    priority: 0.5,
  }));

  return [...staticEntries, ...companyEntries, ...sectorEntries, ...industryEntries];
}
