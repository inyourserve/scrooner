import { AuthForm } from "@/components/auth/AuthForm";
import { AuthShell } from "@/components/auth/AuthShell";
import { getSafeRedirectPath } from "@/lib/auth/redirect";

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ redirect_url?: string; error?: string }> }) {
  const params = await searchParams;
  const redirectUrl = getSafeRedirectPath(params.redirect_url);
  return (
    <AuthShell>
      {params.error && <p className="auth-page__notice" role="alert">We couldn’t complete sign in. Please try again.</p>}
      <AuthForm mode="login" redirectUrl={redirectUrl} />
    </AuthShell>
  );
}
