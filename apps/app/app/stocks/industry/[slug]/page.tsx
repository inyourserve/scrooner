import type { Metadata } from "next";
import Link from "next/link";
import { cache } from "react";
import { notFound } from "next/navigation";
import { PublicPage } from "@/components/public/PublicPage";
import { getCompaniesByIndustrySlug } from "@/lib/company/referenceData";

// Calls apps/backend instead of querying Postgres directly (doc 54,
// 2026-10-13). cache() dedupes the generateMetadata vs. page-render
// call within one request, same pattern as the company page.
const getIndustryData = cache(getCompaniesByIndustrySlug);

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const data = await getIndustryData(slug);
  if (!data) return { title: "Industry not found — Scrooner", robots: { index: false } };
  return {
    title: `${data.industry} stocks — Scrooner`,
    description: `US-listed companies in the ${data.industry} industry, with links to full financials and filings.`,
  };
}

export default async function IndustryPage({ params }: Props) {
  const { slug } = await params;
  const data = await getIndustryData(slug);
  if (!data) notFound();
  return (
    <PublicPage title={`${data.industry} stocks`} description={`${data.companies.length} companies in the ${data.industry} industry.`}>
      <p className="public-directory-back"><Link href="/stocks/industry">← All industries</Link></p>
      <ul className="ds-directory">
        {data.companies.map((company) => (
          <li key={company.ticker} className="ds-directory__item">
            <Link className="ds-directory__link" href={`/stocks/${company.ticker.toLowerCase()}`}><span className="ds-directory__label">{company.company_name}</span><small className="ds-directory__meta">{company.ticker}</small></Link>
          </li>
        ))}
      </ul>
    </PublicPage>
  );
}
