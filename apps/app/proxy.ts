import type { NextRequest } from "next/server";
import { updateSession } from "@/lib/supabase/proxy";

export async function proxy(request: NextRequest) {
  return updateSession(request);
}

export const config = {
  // Session refresh belongs only on authenticated journeys. Public screener,
  // auth, and catalog requests must not pay for a duplicate claims lookup.
  matcher: ["/account/:path*", "/saved-screens/:path*", "/api/screens/:path*"],
};
