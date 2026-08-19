const DEFAULT_BACKEND_URL = "http://127.0.0.1:8000";

export function backendUrl(path: string): string {
  const origin = (process.env.SCROONER_BACKEND_URL || DEFAULT_BACKEND_URL).replace(/\/$/, "");
  return `${origin}${path}`;
}

export async function proxyBackend(responsePromise: Promise<Response>): Promise<Response> {
  try {
    const response = await responsePromise;
    const body = await response.text();
    return new Response(body, {
      status: response.status,
      headers: { "content-type": response.headers.get("content-type") || "application/json" },
    });
  } catch {
    return Response.json(
      {
        detail: "Scrooner's screening service is temporarily unavailable. Your criteria are still in the browser; try again shortly.",
      },
      { status: 502 },
    );
  }
}
