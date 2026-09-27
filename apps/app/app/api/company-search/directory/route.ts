import { unstable_cache } from "next/cache";
import { loadFullCompanyDirectory } from "@/lib/company/db";

// Not force-static: prerendering ran the directory query at `next build`
// time, so the build failed anywhere without a reachable Postgres (CI has
// none). Rendered at request time instead, with the query result held in
// Next's data cache for an hour -- the same freshness the static version had.
export const dynamic = "force-dynamic";

const loadDirectory = unstable_cache(loadFullCompanyDirectory, ["company-search-directory"], {
  revalidate: 3600,
});

// Ships the whole ~6k-row active-company directory once so the homepage
// search box can match client-side with zero network/DB round trip per
// keystroke -- see CompanySearch.tsx. Tuples, not objects: with ~6k rows
// the repeated key names in an object shape cost real bytes even after
// gzip. Order: [ticker, company_name, exchange, sector].
export async function GET() {
  const rows = await loadDirectory();
  const companies = rows.map((row) => [row.ticker, row.company_name, row.exchange, row.sector]);
  return Response.json(
    { companies, generatedAt: new Date().toISOString().slice(0, 10) },
    { headers: { "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400" } },
  );
}
