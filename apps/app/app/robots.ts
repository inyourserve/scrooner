import type { MetadataRoute } from "next";

const BASE_URL = (process.env.NEXT_PUBLIC_SCROONER_URL ?? "https://scrooner.com").replace(/\/$/, "");

// `/app/*` is the authenticated product (screener workspace, saved
// screens, account) -- real content, but never meant to rank, and every
// result behind it is per-user anyway. Auth pages have no indexable
// content and would otherwise show up as thin/duplicate pages in Search
// Console. Everything else (marketing pages, /stocks/*, /explore) is the
// actual distribution surface and stays crawlable.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/app/", "/login", "/signup", "/forgot-password", "/account"],
    },
    sitemap: `${BASE_URL}/sitemap.xml`,
  };
}
