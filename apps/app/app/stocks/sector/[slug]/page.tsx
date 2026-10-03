import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { PublicPage } from "@/components/public/PublicPage";
import { getCompaniesBySectorSlug } from "@/lib/company/db";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const data = await getCompaniesBySectorSlug(slug);
  if (!data) return { title: "Sector not found — Scrooner", robots: { index: false } };
  return {
    title: `${data.sector} stocks — Scrooner`,
    description: `US-listed companies in the ${data.sector} sector, with links to full financials and filings.`,
  };
}

export default async function SectorPage({ params }: Props) {
  const { slug } = await params;
  const data = await getCompaniesBySectorSlug(slug);
  if (!data) notFound();
  return (
    <PublicPage title={`${data.sector} stocks`} description={`${data.companies.length} companies in the ${data.sector} sector.`}>
      <p className="public-directory-back"><Link href="/stocks/sector">← All sectors</Link></p>
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
