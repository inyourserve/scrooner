import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { BrandMark } from "@/components/ui/BrandMark";
import { CompanySearch } from "@/components/public/CompanySearch";
import { PublicFooter } from "@/components/public/PublicFooter";
import { PublicHeader } from "@/components/public/PublicHeader";
import { getCompaniesByTickers } from "@/lib/company/db";

export const metadata: Metadata = {
  title: "US Stock Screener & Company Research — Scrooner",
  description: "Search US companies, research SEC-derived financials, and create verifiable stock screens with Scrooner.",
  keywords: ["US stock screener", "stock screener", "company research", "fundamental stock screener"],
};
export const dynamic = "force-dynamic";
const names: Record<string, string> = { AAPL: "Apple", MSFT: "Microsoft", NVDA: "Nvidia", AMZN: "Amazon", GOOGL: "Alphabet", "BRK.B": "Berkshire", COST: "Costco", V: "Visa", JPM: "JPMorgan", LLY: "Eli Lilly", KO: "Coca-Cola" };

async function getQuickPicks() {
  const tickers = Object.keys(names);

  try {
    const companies = await getCompaniesByTickers(tickers);
    return companies
      .sort((a, b) => tickers.indexOf(a.ticker.toUpperCase()) - tickers.indexOf(b.ticker.toUpperCase()))
      .slice(0, 8);
  } catch {
    // Popular links are optional homepage enrichment. A database outage must
    // not prevent the public search shell and primary navigation from loading.
    return [];
  }
}

export default async function Home({ searchParams }: { searchParams: Promise<{ code?: string; next?: string }> }) {
  const params = await searchParams;
  // Supabase falls back to the configured Site URL when a local callback URL
  // is not yet allow-listed. Recover that response instead of showing the
  // homepage with an OAuth code in its address bar.
  if (params.code) {
    const callbackParams = new URLSearchParams({ code: params.code });
    if (params.next) callbackParams.set("next", params.next);
    redirect(`/auth/callback?${callbackParams}`);
  }
  const quickPicks = await getQuickPicks();
  const siteUrl = process.env.NEXT_PUBLIC_SCROONER_URL ?? "https://scrooner.com";
  // Plain Organization + WebSite JSON-LD -- standard practice for a site's
  // homepage. Deliberately NO `potentialAction`/SearchAction: that schema
  // asserts a working `?q={search_term_string}` endpoint, and /stocks only
  // supports letter-based browsing (`?letter=`), not free-text search --
  // asserting a capability the site doesn't have would be worse than no
  // structured data at all.
  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      { "@type": "Organization", name: "Scrooner", url: siteUrl },
      { "@type": "WebSite", name: "Scrooner", url: siteUrl },
    ],
  };
  return <div className="public-site">
    {/* Standard Next.js JSON-LD pattern -- content is the fixed object above, never user input. */}
    <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }} />
    <PublicHeader current="home" skipHref="#company-search" /><main className="home-main" id="main-content">
    <div className="hero-wordmark" aria-label="Scrooner"><span className="name">scrooner</span><BrandMark className="hero-research-mark" /></div>
    <h1 className="tagline">Search and research US public companies.</h1>
    <p className="subtag">Explore SEC-derived financials, ratios, ownership, and filings—or use the US stock screener to find companies that match your criteria.</p>
    <div id="company-search"><CompanySearch /></div>
    {quickPicks.length > 0 && <div className="quick-picks" aria-label="Popular company pages"><span className="label">Or analyse:</span>{quickPicks.map((company) => <Link className="ds-chip company-chip" key={company.ticker} href={`/stocks/${company.ticker.toLowerCase()}`}>{names[company.ticker.toUpperCase()] ?? company.company_name}<span className="ticker">{company.ticker}</span></Link>)}</div>}
    <p className="screener-path">Have an investment thesis? <Link href="/app/screens/new">Create a stock screen →</Link></p>
  </main><PublicFooter /></div>;
}
