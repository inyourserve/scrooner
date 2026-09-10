import type { NextConfig } from "next";
import { fileURLToPath } from "node:url";

const repositoryRoot = fileURLToPath(new URL("../..", import.meta.url));

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  outputFileTracingRoot: repositoryRoot,
  reactStrictMode: true,
  turbopack: {
    root: repositoryRoot,
  },
  // /stock/{ticker} -> /stocks/{ticker}, 2026-09-06: the route itself was
  // renamed to match doc 02's already-locked "/stocks/{company_slug}"
  // canonical-routes decision. Permanent (308) so any bookmark, external
  // link, or search-engine-indexed URL from before the rename keeps working
  // rather than 404ing.
  async redirects() {
    return [
      { source: "/stock/:ticker", destination: "/stocks/:ticker", permanent: true },
      { source: "/app/screener", destination: "/app/screens/new", permanent: true },
      { source: "/app/saved-screens", destination: "/app/screens", permanent: true },
      { source: "/saved-screens", destination: "/app/screens", permanent: true },
    ];
  },
};

export default nextConfig;
