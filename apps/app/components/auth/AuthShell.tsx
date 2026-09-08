import Link from "next/link";
import { Check } from "lucide-react";
import { BrandMark } from "@/components/ui/BrandMark";
import type { ReactNode } from "react";

const TRUST_POINTS = [
  "Every number traces to its source SEC filing, formula, and date.",
  "Screens are deterministic — AI interprets intent, code decides results.",
  "SEC EDGAR data across 5,000+ US-listed companies.",
];

// The onboarding shell for login/signup/forgot-password -- a quiet
// brand/trust panel next to the actual form, the same two-panel shape as
// Linear/Stripe/Vercel's own auth pages, minus any illustration or
// gradient (doc/design/shadcn-system.md: premium via precision, not
// decoration). Collapses to a single column on mobile, with the brand
// mark moved into the form panel so it's never lost.
export function AuthShell({ children }: { children: ReactNode }) {
  return (
    <div className="auth-shell">
      {/* aria-hidden: purely decorative/marketing (hidden entirely below the
          desktop breakpoint) -- the form panel's own brand link below is the
          one real, always-visible way back home, so this panel's copy of
          that link isn't duplicated for assistive tech as a second,
          identically-named link. */}
      <aside className="auth-shell__brand" aria-hidden="true">
        <svg className="auth-shell__watermark" viewBox="0 0 24 24" fill="none">
          <path d="M4 17.5 9.2 12l3.2 3.1L20 7" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M16 7h4v4" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <Link href="/" className="auth-shell__brand-mark">
          <BrandMark className="auth-shell__mark" />
          <span>scrooner</span>
        </Link>
        <p className="auth-shell__tagline">The easiest way to screen US companies using complex fundamental logic — in plain English.</p>
        <ul className="auth-shell__trust">
          {TRUST_POINTS.map((point) => <li key={point}><Check size={16} aria-hidden="true" />{point}</li>)}
        </ul>
      </aside>
      <main id="main-content" className="auth-shell__form">
        <Link href="/" className="auth-shell__form-brand">
          <BrandMark size="small" />
          <span>scrooner</span>
        </Link>
        {children}
      </main>
    </div>
  );
}
