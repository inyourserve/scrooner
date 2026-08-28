import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { getAuthEnvironmentStatus } from "@/lib/auth/config";

export async function createClient() {
  const status = getAuthEnvironmentStatus();

  if (!status.enabled) {
    throw new Error("Supabase Auth is not configured.");
  }

  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) => {
              cookieStore.set(name, value, {
                ...options,
                ...(status.cookieDomain
                  ? { domain: status.cookieDomain }
                  : {}),
              });
            });
          } catch {
            // Server Components cannot write cookies. proxy.ts refreshes them.
          }
        },
      },
    },
  );
}
