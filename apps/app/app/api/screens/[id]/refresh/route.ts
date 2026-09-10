import { backendUrl, proxyBackend } from "@/lib/backend";
import { requireApiUser } from "@/lib/auth/require-user";

export const dynamic = "force-dynamic";
type Context = { params: Promise<{ id: string }> };

export async function POST(request: Request, context: Context) {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  const { id } = await context.params;
  const authorization = request.headers.get("authorization");
  return proxyBackend(fetch(backendUrl(`/v1/screens/${encodeURIComponent(id)}/refresh`), {
    method: "POST",
    cache: "no-store",
    headers: { accept: "application/json", ...(authorization ? { authorization } : {}) },
  }));
}
