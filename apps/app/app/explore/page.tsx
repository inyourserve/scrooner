import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { PublicPage } from "@/components/public/PublicPage";
import { getSectorList, getIndustryList } from "@/lib/company/db";
import { NATURAL_QUERY_EXAMPLES } from "@/lib/screener/interpretation";

export const metadata: Metadata = {
  title: "Explore — sectors, industries, and stock screens",
  description: "Start from a popular screen, or browse US-listed companies by sector and industry.",
};
export const dynamic = "force-dynamic";

// Reuses the exact phrases doc 15b already verified parse correctly and
// reproduce the Screener's own results -- an "explore" surface is not the
// place to hand-write new example queries that have never been run through
// the real interpreter.
function exampleHref(example: string) {
  return `/app/screens/new?${new URLSearchParams({ q: example, run: "1" })}`;
}

export default async function ExplorePage() {
  const [sectors, industries] = await Promise.all([getSectorList(), getIndustryList()]);
  return (
    <PublicPage current="explore" title="Explore" description={metadata.description!} wide>
      <section aria-labelledby="explore-screens-title">
        <h2 id="explore-screens-title">Popular screens</h2>
        <p>Run a tested, plain-English screen with one click.</p>
        <div className="ds-directory">
          {NATURAL_QUERY_EXAMPLES.map((example) => (
            <Link key={example} href={exampleHref(example)} className="ds-directory__item">
              <span className="ds-directory__label">{example}</span>
              <ArrowRight size={14} aria-hidden="true" />
            </Link>
          ))}
        </div>
      </section>

      <section aria-labelledby="explore-sectors-title">
        <h2 id="explore-sectors-title">Browse by sector</h2>
        <div className="ds-directory ds-directory--compact">
          {sectors.map((row) => (
            <Link key={row.slug} href={`/stocks/sector/${row.slug}`} className="ds-directory__item">
              <span className="ds-directory__label">{row.sector}</span>
              <small className="ds-directory__meta">{row.company_count}</small>
            </Link>
          ))}
        </div>
      </section>

      <section aria-labelledby="explore-industries-title">
        <div className="ds-section-heading">
          <h2 id="explore-industries-title">Browse by industry</h2>
          <Link href="/stocks/industry">All industries →</Link>
        </div>
        <div className="ds-directory ds-directory--compact">
          {industries.slice(0, 24).map((row) => (
            <Link key={row.slug} href={`/stocks/industry/${row.slug}`} className="ds-directory__item">
              <span className="ds-directory__label">{row.y_industry}</span>
              <small className="ds-directory__meta">{row.company_count}</small>
            </Link>
          ))}
        </div>
      </section>

      <p className="public-meta">Looking for a specific company? Use search in the header (⌘K), go directly to <Link href="/stocks/aapl">/stocks/&#123;ticker&#125;</Link>, or see the full <Link href="/stocks">list of covered stocks</Link>.</p>
    </PublicPage>
  );
}
