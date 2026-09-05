import { backendUrl, proxyBackend } from "@/lib/backend";
import { requireApiUser } from "@/lib/auth/require-user";

export const dynamic = "force-dynamic";

type Context = { params: Promise<{ id: string }> };

async function target(request: Request, context: Context, method: "PATCH" | "DELETE") {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  const { id } = await context.params;
  if (!/^\d+$/.test(id)) return Response.json({ detail: "Invalid screen id." }, { status: 400 });
  const authorization = request.headers.get("authorization");
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
