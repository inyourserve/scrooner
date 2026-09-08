const DEFAULT_REDIRECT = "/app";
const ENCODED_CONTROL_CHARACTER = /%(?:0[0-9a-f]|1[0-9a-f]|7f)/i;
const RAW_CONTROL_CHARACTER = /[\u0000-\u001f\u007f]/;

type RedirectOptions = {
  allowedOrigins?: readonly string[];
  fallback?: string;
};

function cleanPath(url: URL): string {
  return `${url.pathname}${url.search}${url.hash}`;
}

/**
 * Converts a login redirect request into an app-local path.
 *
 * Returning a path instead of the original absolute URL removes host-header
 * ambiguity and makes it impossible for a successful login to redirect to an
 * attacker-controlled origin.
 */
export function getSafeRedirectPath(
  requested: string | null | undefined,
  options: RedirectOptions = {},
): string {
  const fallback = options.fallback || DEFAULT_REDIRECT;
  const value = requested?.trim();

  if (
    !value ||
    RAW_CONTROL_CHARACTER.test(value) ||
    ENCODED_CONTROL_CHARACTER.test(value) ||
    value.includes("\\")
  ) {
    return fallback;
  }

  const allowedOrigins = new Set(
    (options.allowedOrigins || []).map((origin) => {
      try {
        return new URL(origin).origin;
      } catch {
        return "";
      }
    }),
  );

  if (value.startsWith("/") && !value.startsWith("//")) {
    try {
      return cleanPath(new URL(value, "https://app.scrooner.invalid"));
    } catch {
      return fallback;
    }
  }

  try {
    const destination = new URL(value);
    if (
      destination.username ||
      destination.password ||
      !allowedOrigins.has(destination.origin)
    ) {
      return fallback;
    }
    return cleanPath(destination);
  } catch {
    return fallback;
  }
}

export function buildLoginHref(
  requested: string,
  options: RedirectOptions = {},
): string {
  const redirectPath = getSafeRedirectPath(requested, options);
  return `/login?${new URLSearchParams({ redirect_url: redirectPath })}`;
}
