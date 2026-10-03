import type { Metadata } from "next";
import Link from "next/link";
import { Check, ShieldCheck, Sparkles } from "lucide-react";
import { PublicPage } from "@/components/public/PublicPage";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

export const metadata: Metadata = {
  title: "Pricing — Scrooner",
  description: "Scrooner is free during beta. See what is included today and how we are approaching a future premium plan.",
};

const included = [
  "Plain-English screening across 18 core fundamental metrics",
  "Company financials, ratios, ownership, and insider activity",
  "Source, period, and formula context for key metrics",
  "Save and rerun your own screens",
  "SEC EDGAR coverage across thousands of US-listed companies",
];

const principles = [
  {
    title: "A useful free core",
    body: "Company research and fundamental screening should be useful before you pay. Premium will add depth and higher-value workflows—not hide the basics.",
  },
  {
    title: "Clear terms before checkout",
    body: "No card is required during beta. If paid plans launch, the price, limits, and renewal terms will be clear before you subscribe.",
  },
  {
    title: "AI translates; code evaluates",
    body: "AI may help interpret a request. The screen itself is evaluated against reported data and versioned formulas—not generated as an answer.",
  },
];

export default function Page() {
  return (
    <PublicPage current="pricing" eyebrow="Pricing" title="Free during beta. Clear when that changes." description="Create screens, research companies, and save your work without a credit card. Here is what beta access includes today.">
      <section>
        <h2>Included in beta</h2>
        <ul className="pricing-included">{included.map((item) => <li key={item}><Check size={18} aria-hidden="true" />{item}</li>)}</ul>
        <div className="pricing-cta">
          <Button asChild size="large"><Link href="/signup">Create free account</Link></Button>
          <Button asChild size="large" variant="ghost"><Link href="/app/screens/new">Start screening</Link></Button>
        </div>
      </section>

      <section>
        <h2>One plan when premium launches</h2>
        <div className="pricing-plans">
          <div className="pricing-plan pricing-plan--highlight">
            <div className="pricing-plan__name">Free<Badge tone="positive">Live now</Badge></div>
            <div className="pricing-plan__price"><strong>$0</strong></div>
            <p className="pricing-plan__desc">Beta access to the current research and screening workflow. No card required.</p>
            <ul className="pricing-plan__list">
              <li><Check size={16} aria-hidden="true" />Full screener &amp; company pages</li>
              <li><Check size={16} aria-hidden="true" />Ownership &amp; insider data</li>
              <li><Check size={16} aria-hidden="true" />Saved screens</li>
            </ul>
            <Button asChild variant="secondary"><Link href="/signup">Get beta access</Link></Button>
          </div>
          <div className="pricing-plan">
            <div className="pricing-plan__name">Premium<Badge>In development</Badge></div>
            <div className="pricing-plan__price"><strong>~$100</strong><span>/ year, target</span></div>
            <p className="pricing-plan__desc">We are validating one annual plan for investors who need deeper history and broader screening. Scope and price remain a working hypothesis.</p>
            <ul className="pricing-plan__list">
              <li><Sparkles size={16} aria-hidden="true" />Expanded ownership &amp; insider history</li>
              <li><Sparkles size={16} aria-hidden="true" />Additional screening metrics</li>
              <li><Sparkles size={16} aria-hidden="true" />Early access to new research data</li>
            </ul>
            <p className="pricing-plan__note">Not available yet. The final feature set and price may change.</p>
          </div>
        </div>
      </section>

      <section>
        <h2>Pricing principles</h2>
        <div className="pricing-principles">{principles.map((item) => <div key={item.title}><ShieldCheck size={18} aria-hidden="true" /><div><strong>{item.title}</strong><p>{item.body}</p></div></div>)}</div>
      </section>
    </PublicPage>
  );
}
