import { backendAuthorization } from "@/lib/auth/backend-authorization";
import { requireApiUser } from "@/lib/auth/require-user";
import { backendUrl, proxyBackend } from "@/lib/backend";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ companyId: string }> };

export async function PATCH(request: Request, { params }: Props) {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  const { companyId } = await params;
  const authorization = await backendAuthorization(request);
  return proxyBackend(fetch(backendUrl(`/v1/watchlist/${encodeURIComponent(companyId)}`), {
    method: "PATCH",
    cache: "no-store",
    headers: { accept: "application/json", "content-type": "application/json", ...(authorization ? { authorization } : {}) },
    body: await request.text(),
  }));
}

export async function DELETE(request: Request, { params }: Props) {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  const { companyId } = await params;
  const authorization = await backendAuthorization(request);
  return proxyBackend(fetch(backendUrl(`/v1/watchlist/${encodeURIComponent(companyId)}`), {
    method: "DELETE",
    cache: "no-store",
    headers: { accept: "application/json", ...(authorization ? { authorization } : {}) },
  }));
}
