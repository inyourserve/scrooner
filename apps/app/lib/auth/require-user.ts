import { getAuthEnvironmentStatus } from "@/lib/auth/config";
import { createClient } from "@/lib/supabase/server";

export async function hasAuthenticatedUser(): Promise<boolean> {
  if (!getAuthEnvironmentStatus().enabled) return false;
  const supabase = await createClient();
  const { data, error } = await supabase.auth.getClaims();
  return !error && Boolean(data?.claims);
}

export async function requireApiUser(): Promise<Response | null> {
  if (await hasAuthenticatedUser()) return null;
  return Response.json(
    { detail: "Sign in to use the Scrooner screening tools." },
    { status: 401, headers: { "Cache-Control": "private, no-store" } },
  );
}
