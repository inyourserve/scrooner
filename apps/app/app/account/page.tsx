import { redirect } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { logout } from "@/app/auth/actions";
import { getAuthEnvironmentStatus } from "@/lib/auth/config";
import { createClient } from "@/lib/supabase/server";

export default async function AccountPage() {
  const status = getAuthEnvironmentStatus();
  if (!status.enabled) {
    return (
      <main id="main-content" className="main-content account-page">
        <p className="eyebrow">Account settings</p><h1>Account access is not configured</h1>
        <p className="intro-copy">Add the public Supabase URL and publishable key to enable account access in this environment.</p>
      </main>
    );
  }

  const supabase = await createClient();
  const { data, error } = await supabase.auth.getUser();
  if (error || !data.user) redirect("/login?redirect_url=%2Faccount");

  return (
    <main id="main-content" className="main-content account-page">
      <p className="eyebrow">Account settings</p>
      <h1>Your account</h1>
      <section className="account-panel" aria-labelledby="account-details">
        <h2 id="account-details">Sign-in details</h2>
        <dl><div><dt>Email</dt><dd>{data.user.email || "Not available"}</dd></div><div><dt>Email status</dt><dd>{data.user.email_confirmed_at ? "Verified" : "Confirmation pending"}</dd></div></dl>
        <div className="account-panel__actions"><Link className="ds-button ds-button--secondary account-link-button" href="/account/update-password">Change password</Link><form action={logout}><Button variant="ghost" type="submit">Sign out</Button></form></div>
      </section>
    </main>
  );
}
