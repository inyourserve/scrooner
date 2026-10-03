import { backendUrl, proxyBackend } from "@/lib/backend";
import { requireApiUser } from "@/lib/auth/require-user";
import { createClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  const incoming = new URL(request.url);
  const limit = incoming.searchParams.get("limit") || "8";
  let authorization = request.headers.get("authorization");
  if (!authorization) {
    const { data } = await (await createClient()).auth.getSession();
    if (data.session?.access_token) authorization = `Bearer ${data.session.access_token}`;
  }
  return proxyBackend(fetch(backendUrl(`/v1/screen-runs?limit=${encodeURIComponent(limit)}`), {
    cache: "no-store",
    headers: { accept: "application/json", ...(authorization ? { authorization } : {}) },
  }));
}

export async function POST(request: Request) {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  let authorization = request.headers.get("authorization");
  if (!authorization) {
    const { data } = await (await createClient()).auth.getSession();
    if (data.session?.access_token) authorization = `Bearer ${data.session.access_token}`;
  }
  return proxyBackend(fetch(backendUrl("/v1/screen-runs"), {
    method: "POST",
    cache: "no-store",
    headers: {
      accept: "application/json",
      "content-type": "application/json",
      ...(authorization ? { authorization } : {}),
    },
    body: await request.text(),
  }));
}
