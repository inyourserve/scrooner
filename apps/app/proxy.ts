import type { NextRequest } from "next/server";
import { updateSession } from "@/lib/supabase/proxy";

export async function proxy(request: NextRequest) {
  return updateSession(request);
}

export const config = {
  matcher: [
    "/app/:path*",
    "/api/ask/:path*",
    "/api/screen/:path*",
    "/api/screens/:path*",
    "/api/metrics/:path*",
  ],
};
