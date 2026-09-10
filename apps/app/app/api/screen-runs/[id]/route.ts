import { backendUrl, proxyBackend } from "@/lib/backend";
import { requireApiUser } from "@/lib/auth/require-user";
import { createClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

type Context = { params: Promise<{ id: string }> };

export async function GET(request: Request, context: Context) {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  const { id } = await context.params;
  if (!/^[0-9a-f-]{36}$/i.test(id)) return Response.json({ detail: "Invalid run id." }, { status: 400 });
  const incoming = new URL(request.url);
  const search = new URLSearchParams();
  for (const key of ["cursor", "page_size"]) {
    const value = incoming.searchParams.get(key);
    if (value) search.set(key, value);
  }
  let authorization = request.headers.get("authorization");
  if (!authorization) {
    const { data } = await (await createClient()).auth.getSession();
    if (data.session?.access_token) authorization = `Bearer ${data.session.access_token}`;
  }
  return proxyBackend(fetch(backendUrl(`/v1/screen-runs/${id}?${search}`), {
    cache: "no-store",
    headers: { accept: "application/json", ...(authorization ? { authorization } : {}) },
  }));
}
