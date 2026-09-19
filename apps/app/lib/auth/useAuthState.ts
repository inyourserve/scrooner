"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";

export type AuthStatus = "checking" | "authenticated" | "anonymous";

export interface SessionInfo {
  status: AuthStatus;
  email: string | null;
}

const CHECKING: SessionInfo = { status: "checking", email: null };
const ANONYMOUS: SessionInfo = { status: "anonymous", email: null };

// Shared by every client-side nav element that needs to know "is someone
// signed in, and as whom" (HeaderAuthAction, DashboardNavLink) so there is
// exactly one place that talks to Supabase for this, not one copy per
// component that could drift out of sync with the others.
export function useAuthState(): SessionInfo {
  const [state, setState] = useState<SessionInfo>(CHECKING);

  useEffect(() => {
    let active = true;
    const resolve = (email: string | null | undefined) => {
      if (active) setState(email ? { status: "authenticated", email } : ANONYMOUS);
    };
    try {
      const client = createClient();
      void client.auth.getSession().then(({ data }) => resolve(data.session?.user.email)).catch(() => resolve(null));
      const { data } = client.auth.onAuthStateChange((_event, session) => resolve(session?.user.email));
      return () => {
        active = false;
        data.subscription.unsubscribe();
      };
    } catch {
      queueMicrotask(() => resolve(null));
    }
  }, []);

  return state;
}
