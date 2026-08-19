import { backendUrl, proxyBackend } from "@/lib/backend";

export const dynamic = "force-dynamic";

export async function GET() {
  return proxyBackend(
    fetch(backendUrl("/v1/metrics"), {
      cache: "no-store",
      headers: { accept: "application/json" },
    }),
  );
}
