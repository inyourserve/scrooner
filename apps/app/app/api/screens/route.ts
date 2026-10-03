import { backendUrl, proxyBackend } from "@/lib/backend";
import { requireApiUser } from "@/lib/auth/require-user";
import { backendAuthorization } from "@/lib/auth/backend-authorization";

export const dynamic = "force-dynamic";

async function headers(request: Request, hasBody = false) {
  const authorization = await backendAuthorization(request);
  return {
    accept: "application/json",
    ...(authorization ? { authorization } : {}),
    ...(hasBody ? { "content-type": "application/json" } : {}),
  };
}

export async function GET(request: Request) {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  return proxyBackend(fetch(backendUrl("/v1/screens"), { cache: "no-store", headers: await headers(request) }));
}

export async function POST(request: Request) {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  return proxyBackend(fetch(backendUrl("/v1/screens"), {
    method: "POST", cache: "no-store", headers: await headers(request, true), body: await request.text(),
  }));
}
