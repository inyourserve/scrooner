import type { Metadata } from "next";
import Link from "next/link";
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

export default async function Home() {
  const quickPicks = await getQuickPicks();
  return <div className="public-site"><PublicHeader current="home" skipHref="#company-search" /><main className="home-main" id="main-content">
    <div className="hero-wordmark" aria-label="Scrooner"><span className="name">scrooner</span><BrandMark className="hero-research-mark" /></div>
    <h1 className="tagline">Search and research US public companies.</h1>
    <p className="subtag">Explore SEC-derived financials, ratios, ownership, and filings—or use the US stock screener to find companies that match your criteria.</p>
    <div id="company-search"><CompanySearch variant="hero" /></div>
    {quickPicks.length > 0 && <div className="quick-picks" aria-label="Popular company pages"><span className="label">Or analyse:</span>{quickPicks.map((company) => <Link className="ds-chip company-chip" key={company.ticker} href={`/stocks/${company.ticker.toLowerCase()}`}>{names[company.ticker.toUpperCase()] ?? company.company_name}<span className="ticker">{company.ticker}</span></Link>)}</div>}
    <p className="screener-path">Have an investment thesis? <Link href="/app/screener">Create a stock screen →</Link></p>
  </main><PublicFooter companyHref={quickPicks[0] ? `/stocks/${quickPicks[0].ticker.toLowerCase()}` : "/"} /></div>;
}
