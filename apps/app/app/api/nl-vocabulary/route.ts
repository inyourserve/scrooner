import { backendUrl, proxyBackend } from "@/lib/backend";
import { requireApiUser } from "@/lib/auth/require-user";

export const revalidate = 3600;

export async function GET() {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  const response = await proxyBackend(
    fetch(backendUrl("/v1/nl-vocabulary"), {
      next: { revalidate: 3600 },
      headers: { accept: "application/json" },
    }),
  );
  response.headers.set("Cache-Control", "private, max-age=300");
  return response;
}
