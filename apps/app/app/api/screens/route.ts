import { backendUrl, proxyBackend } from "@/lib/backend";

export const dynamic = "force-dynamic";

function headers(request: Request, hasBody = false) {
  const authorization = request.headers.get("authorization");
  return {
    accept: "application/json",
    ...(authorization ? { authorization } : {}),
    ...(hasBody ? { "content-type": "application/json" } : {}),
  };
}

export async function GET(request: Request) {
  return proxyBackend(fetch(backendUrl("/v1/screens"), { cache: "no-store", headers: headers(request) }));
}

export async function POST(request: Request) {
  return proxyBackend(fetch(backendUrl("/v1/screens"), {
    method: "POST", cache: "no-store", headers: headers(request, true), body: await request.text(),
  }));
}

