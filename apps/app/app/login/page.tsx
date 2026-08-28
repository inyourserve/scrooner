import { AuthForm } from "@/components/auth/AuthForm";
import { getSafeRedirectPath } from "@/lib/auth/redirect";

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ redirect_url?: string; error?: string }> }) {
  const params = await searchParams;
  const redirectUrl = getSafeRedirectPath(params.redirect_url);
  return (
    <main id="main-content" className="auth-page">
      {params.error && <p className="auth-page__notice" role="alert">The sign-in link is invalid or has expired. Please try again.</p>}
      <AuthForm mode="login" redirectUrl={redirectUrl} />
    </main>
  );
}
