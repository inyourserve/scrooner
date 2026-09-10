export const REQUIRED_AUTH_ENV_KEYS = [
  "NEXT_PUBLIC_SUPABASE_URL",
  "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
] as const;

export type AuthEnvironment = Record<string, string | undefined>;

export type AuthEnvironmentStatus = {
  enabled: boolean;
  missing: readonly (typeof REQUIRED_AUTH_ENV_KEYS)[number][];
  cookieDomain: string | null;
};

export function getAppOrigin(
  environment: AuthEnvironment = process.env,
): string {
  const configured = environment.NEXT_PUBLIC_SCROONER_URL?.trim();
  try {
    return new URL(configured || "http://localhost:3000").origin;
  } catch {
    return "http://localhost:3000";
  }
}

/**
 * Reports whether the public, user-scoped Supabase Auth configuration exists.
 *
 * This deliberately does not accept SUPABASE_SERVICE_ROLE_KEY as a fallback.
 * Service-role access bypasses RLS and must never enter the Next.js client
 * bundle or stand in for a user session.
 */
export function getAuthEnvironmentStatus(
  environment: AuthEnvironment = process.env,
): AuthEnvironmentStatus {
  const missing = REQUIRED_AUTH_ENV_KEYS.filter(
    (key) => !environment[key]?.trim(),
  );
  const cookieDomain = environment.SUPABASE_AUTH_COOKIE_DOMAIN?.trim() || null;

  return {
    enabled: missing.length === 0,
    missing,
    cookieDomain,
  };
}
