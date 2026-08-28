import { backendUrl, proxyBackend } from "@/lib/backend";

export const revalidate = 3600;

export async function GET() {
  const response = await proxyBackend(
    fetch(backendUrl("/v1/metrics"), {
      next: { revalidate: 3600 },
      headers: { accept: "application/json" },
    }),
  );
  response.headers.set(
    "Cache-Control",
    "public, s-maxage=3600, stale-while-revalidate=86400",
  );
  return response;
}
