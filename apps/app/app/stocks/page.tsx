import type { Metadata } from "next";
import Link from "next/link";
import { PublicPage } from "@/components/public/PublicPage";
import { getSectorList, getIndustryList } from "@/lib/company/db";

export const metadata: Metadata = {
  title: "Stocks — browse by company, sector, or industry",
  description: "Browse US-listed companies by sector or industry, or search directly for a ticker.",
};
export const dynamic = "force-dynamic";

export default async function StocksIndexPage() {
  const [sectors, industries] = await Promise.all([getSectorList(), getIndustryList()]);
  return (
    <PublicPage title="Stocks" description={metadata.description!}>
      <section>
        <h2>Browse by sector</h2>
        <p><Link href="/stocks/sector">All sectors →</Link></p>
        <ul>
          {sectors.map((row) => (
            <li key={row.slug}>
              <Link href={`/stocks/sector/${row.slug}`}>{row.sector}<span className="public-meta"> ({row.company_count})</span></Link>
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2>Browse by industry</h2>
        <p><Link href="/stocks/industry">All industries →</Link></p>
        <ul>
          {industries.slice(0, 20).map((row) => (
            <li key={row.slug}>
              <Link href={`/stocks/industry/${row.slug}`}>{row.y_industry}<span className="public-meta"> ({row.company_count})</span></Link>
            </li>
          ))}
        </ul>
      </section>
      <p className="public-meta">Looking for a specific company? Use search in the header, or go directly to <Link href="/stocks/aapl">/stocks/&#123;ticker&#125;</Link>.</p>
    </PublicPage>
  );
}
