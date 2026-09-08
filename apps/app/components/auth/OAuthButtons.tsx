"use client";

import { useState, type ReactNode } from "react";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/Button";

type Provider = "google" | "apple";

const LABEL: Record<Provider, string> = { google: "Google", apple: "Apple" };

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.9 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.5 6.1 29.5 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.7-.4-3.5z" />
      <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.5 6.1 29.5 4 24 4c-7.7 0-14.3 4.3-17.7 10.7z" />
      <path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.4 26.7 36 24 36c-5.2 0-9.6-3.1-11.3-7.6l-6.5 5C9.5 39.6 16.2 44 24 44z" />
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.3-2.3 4.3-4.1 5.8l6.2 5.2C40.8 36.1 44 30.5 44 24c0-1.3-.1-2.7-.4-3.5z" />
    </svg>
  );
}

function AppleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 384 512" fill="currentColor" aria-hidden="true">
      <path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z" />
    </svg>
  );
}

const ICON: Record<Provider, () => ReactNode> = { google: GoogleIcon, apple: AppleIcon };

// SSO is the code half of the feature -- Google and Apple both still need
// to be turned on in the Supabase project (Authentication > Providers)
// with real OAuth client credentials from Google Cloud Console / Apple
// Developer before this actually completes a sign-in. Until then, clicking
// a button here fails gracefully with a visible error instead of a silent
// redirect loop.
export function OAuthButtons({ redirectUrl = "/app" }: { redirectUrl?: string }) {
  const [pending, setPending] = useState<Provider | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function signInWith(provider: Provider) {
    setError(null);
    setPending(provider);
    try {
      const supabase = createClient();
      const { error: oauthError } = await supabase.auth.signInWithOAuth({
        provider,
        options: { redirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(redirectUrl)}` },
      });
      if (oauthError) {
        setError(`${LABEL[provider]} sign-in isn't available right now.`);
        setPending(null);
      }
      // On success the browser is already navigating to the provider --
      // there's nothing further to render here.
    } catch {
      setError("Something went wrong starting sign-in. Try again.");
      setPending(null);
    }
  }

  return (
    <div className="auth-oauth">
      {(["google", "apple"] as const).map((provider) => {
        const Icon = ICON[provider];
        return (
          <Button
            key={provider}
            type="button"
            variant="secondary"
            fullWidth
            leadingIcon={<Icon />}
            loading={pending === provider}
            loadingLabel="Redirecting…"
            disabled={pending !== null && pending !== provider}
            onClick={() => signInWith(provider)}
          >
            Continue with {LABEL[provider]}
          </Button>
        );
      })}
      {error && <p className="auth-message auth-message--error" role="alert">{error}</p>}
      <div className="auth-divider"><span>or continue with email</span></div>
    </div>
  );
}
