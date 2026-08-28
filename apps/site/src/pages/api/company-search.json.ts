import type { APIRoute } from "astro";

import { searchCompanyDirectory } from "../../lib/db";
import { normalizeCompanyQuery } from "../../lib/companySearch";

export const prerender = false;

export const GET: APIRoute = async ({ request }) => {
  const query = normalizeCompanyQuery(new URL(request.url).searchParams.get("q") ?? "");
  if (!query) {
    return Response.json(
      { companies: [] },
      {
        headers: {
          "Cache-Control": "public, max-age=300, s-maxage=3600, stale-while-revalidate=86400",
          "X-Content-Type-Options": "nosniff",
          "X-Scrooner-DB-Queries": "0",
        },
      },
    );
  }

  const startedAt = performance.now();
  try {
    const companies = await searchCompanyDirectory(query);
    const durationMs = performance.now() - startedAt;
    return Response.json(
      { companies },
      {
        headers: {
          "Cache-Control": "public, max-age=300, s-maxage=3600, stale-while-revalidate=86400",
          "Server-Timing": `db;dur=${durationMs.toFixed(1)};desc=\"company-search\"`,
          "X-Content-Type-Options": "nosniff",
          "X-Scrooner-DB-Queries": "1",
        },
      },
    );
  } catch {
    return Response.json(
      { companies: [], error: "Company search is temporarily unavailable." },
      {
        status: 503,
        headers: {
          "Cache-Control": "no-store",
          "X-Content-Type-Options": "nosniff",
        },
      },
    );
  }
};
