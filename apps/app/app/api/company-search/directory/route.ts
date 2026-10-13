import { loadFullCompanyDirectory } from "@/lib/company/referenceData";

// Calls apps/backend instead of querying Postgres directly, which also
// replaces this route's own unstable_cache(revalidate: 3600) wrapper
// (doc 54, 2026-10-13): unstable_cache's default handler is per server
// PROCESS, not shared -- the exact gap already found and fixed for the
// company page on 2026-09-15, just never retrofitted here until now.
// apps/backend's Redis cache (shared across instances) now does this
// job instead, at the same 1hr freshness this endpoint already had.
//
// Ships the whole ~6k-row active-company directory once so the homepage
// search box can match client-side with zero network/DB round trip per
// keystroke -- see CompanySearch.tsx. Tuples, not objects: with ~6k rows
// the repeated key names in an object shape cost real bytes even after
// gzip. Order: [ticker, company_name, exchange, sector].
export async function GET() {
  const rows = await loadFullCompanyDirectory();
  const companies = rows.map((row) => [row.ticker, row.company_name, row.exchange, row.sector]);
  return Response.json(
    { companies, generatedAt: new Date().toISOString().slice(0, 10) },
    { headers: { "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400" } },
  );
}
