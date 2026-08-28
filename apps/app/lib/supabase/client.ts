import { createBrowserClient } from "@supabase/ssr";
import { getAuthEnvironmentStatus } from "@/lib/auth/config";

export function createClient() {
  const status = getAuthEnvironmentStatus();

  if (!status.enabled) {
    throw new Error("Supabase Auth is not configured.");
  }

  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
  );
}
