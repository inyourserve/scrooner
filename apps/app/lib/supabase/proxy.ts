import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { getAuthEnvironmentStatus } from "@/lib/auth/config";
import { buildLoginHref } from "@/lib/auth/redirect";

export async function updateSession(request: NextRequest) {
  const status = getAuthEnvironmentStatus();
  let response = NextResponse.next({ request });

  if (!status.enabled) {
    return response;
  }

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value),
          );
          response = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) => {
            response.cookies.set(name, value, {
              ...options,
              ...(status.cookieDomain
                ? { domain: status.cookieDomain }
                : {}),
            });
          });
        },
      },
    },
  );

  const { data } = await supabase.auth.getClaims();
  const isProtected = request.nextUrl.pathname.startsWith("/account");

  if (isProtected && !data?.claims) {
    const destination = `${request.nextUrl.pathname}${request.nextUrl.search}`;
    return NextResponse.redirect(
      new URL(buildLoginHref(destination), request.url),
    );
  }

  return response;
}
