import { createClient } from "@/lib/supabase/server";

/**
 * Resolve the bearer token used for calls from Next.js route handlers to the
 * backend. Browser callers may send one explicitly, but the authenticated
 * Supabase cookie is the canonical fallback for same-origin app requests.
 */
export async function backendAuthorization(request: Request): Promise<string | null> {
  const incoming = request.headers.get("authorization");
  if (incoming) return incoming;

  const { data } = await (await createClient()).auth.getSession();
  return data.session?.access_token ? `Bearer ${data.session.access_token}` : null;
}
