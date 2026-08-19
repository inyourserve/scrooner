import { backendUrl, proxyBackend } from "@/lib/backend";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = await request.text();
  return proxyBackend(
    fetch(backendUrl("/v1/ask"), {
      method: "POST",
      cache: "no-store",
      headers: { "content-type": "application/json", accept: "application/json" },
      body,
    }),
  );
}
