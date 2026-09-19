import { getAuthEnvironmentStatus } from "@/lib/auth/config";
import { createClient } from "@/lib/supabase/server";

export async function hasAuthenticatedUser(): Promise<boolean> {
  if (!getAuthEnvironmentStatus().enabled) return false;
  const supabase = await createClient();
  const { data, error } = await supabase.auth.getClaims();
  return !error && Boolean(data?.claims);
}

// Reads the same JWT claims hasAuthenticatedUser() already checks -- used by
// AppShell so the unified nav's account menu can greet a signed-in visitor
// by email without a second round trip.
export async function getAuthenticatedEmail(): Promise<string | null> {
  if (!getAuthEnvironmentStatus().enabled) return null;
  const supabase = await createClient();
  const { data, error } = await supabase.auth.getClaims();
  if (error || !data?.claims) return null;
  const email = (data.claims as { email?: unknown }).email;
  return typeof email === "string" ? email : null;
}

export async function requireApiUser(): Promise<Response | null> {
  if (await hasAuthenticatedUser()) return null;
  return Response.json(
    { detail: "Sign in to use the Scrooner screening tools." },
    { status: 401, headers: { "Cache-Control": "private, no-store" } },
  );
}
