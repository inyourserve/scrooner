import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { PublicPage } from "@/components/public/PublicPage";
import { getCompaniesByIndustrySlug } from "@/lib/company/db";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const data = await getCompaniesByIndustrySlug(slug);
  if (!data) return { title: "Industry not found — Scrooner", robots: { index: false } };
  return {
    title: `${data.industry} stocks — Scrooner`,
    description: `US-listed companies in the ${data.industry} industry, with links to full financials and filings.`,
  };
}

export default async function IndustryPage({ params }: Props) {
  const { slug } = await params;
  const data = await getCompaniesByIndustrySlug(slug);
  if (!data) notFound();
  return (
    <PublicPage title={`${data.industry} stocks`} description={`${data.companies.length} companies in the ${data.industry} industry.`}>
      <p><Link href="/stocks/industry">All industries →</Link></p>
      <ul>
        {data.companies.map((company) => (
          <li key={company.ticker}>
            <Link href={`/stocks/${company.ticker.toLowerCase()}`}>{company.company_name}<span className="public-meta"> {company.ticker}</span></Link>
          </li>
        ))}
      </ul>
    </PublicPage>
  );
}
