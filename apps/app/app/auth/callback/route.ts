import { NextResponse, type NextRequest } from "next/server";
import { getAppOrigin, getAuthEnvironmentStatus } from "@/lib/auth/config";
import { getSafeRedirectPath } from "@/lib/auth/redirect";
import { createClient } from "@/lib/supabase/server";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const next = getSafeRedirectPath(request.nextUrl.searchParams.get("next"));
  const flowId = request.nextUrl.searchParams.get("sb_flow_id");

  if (code && getAuthEnvironmentStatus().enabled) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(
      code,
      flowId ? { flowId } : undefined,
    );
    if (!error) return NextResponse.redirect(new URL(next, getAppOrigin()));
  }

  return NextResponse.redirect(new URL("/login?error=callback", getAppOrigin()));
}
