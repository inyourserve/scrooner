import { backendUrl, proxyBackend } from "@/lib/backend";
import { requireApiUser } from "@/lib/auth/require-user";
import { backendAuthorization } from "@/lib/auth/backend-authorization";

export const dynamic = "force-dynamic";

type Context = { params: Promise<{ id: string }> };

export async function GET(request: Request, context: Context) {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  const { id } = await context.params;
  const incoming = new URL(request.url);
  const search = new URLSearchParams();
  for (const key of ["cursor", "page_size"]) {
    const value = incoming.searchParams.get(key);
    if (value) search.set(key, value);
  }
  const authorization = await backendAuthorization(request);
  return proxyBackend(fetch(backendUrl(`/v1/screens/${encodeURIComponent(id)}?${search}`), {
    cache: "no-store",
    headers: { accept: "application/json", ...(authorization ? { authorization } : {}) },
  }));
}

async function target(request: Request, context: Context, method: "PATCH" | "DELETE") {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  const { id } = await context.params;
  if (!/^\d+$/.test(id)) return Response.json({ detail: "Invalid screen id." }, { status: 400 });
  const authorization = await backendAuthorization(request);
  return proxyBackend(fetch(backendUrl(`/v1/screens/${id}`), {
    method,
    cache: "no-store",
    headers: {
      accept: "application/json",
      ...(authorization ? { authorization } : {}),
      ...(method === "PATCH" ? { "content-type": "application/json" } : {}),
    },
    ...(method === "PATCH" ? { body: await request.text() } : {}),
  }));
}

export const PATCH = (request: Request, context: Context) => target(request, context, "PATCH");
export const DELETE = (request: Request, context: Context) => target(request, context, "DELETE");
