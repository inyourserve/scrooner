import { backendUrl, proxyBackend } from "@/lib/backend";
import { requireApiUser } from "@/lib/auth/require-user";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  const body = await request.text();
  return proxyBackend(
    fetch(backendUrl("/v1/screen"), {
      method: "POST",
      cache: "no-store",
      headers: { "content-type": "application/json", accept: "application/json" },
      body,
    }),
  );
}
