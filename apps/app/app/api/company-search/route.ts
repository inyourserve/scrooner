import { searchCompanyDirectory } from "@/lib/company/db";
import { normalizeCompanyQuery } from "@/lib/company/search";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const query = normalizeCompanyQuery(new URL(request.url).searchParams.get("q") ?? "");
  if (!query) return Response.json({ companies: [] });
  return Response.json({ companies: await searchCompanyDirectory(query, 8) }, { headers: { "Cache-Control": "public, max-age=60, stale-while-revalidate=300" } });
}
