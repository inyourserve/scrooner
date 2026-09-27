import type { Metadata } from "next";
import Link from "next/link";
import { PublicPage } from "@/components/public/PublicPage";
import { getIndustryList } from "@/lib/company/db";

export const metadata: Metadata = {
  title: "Industries — browse US stocks",
  description: "All industries covered by Scrooner, with the number of companies in each.",
};
export const dynamic = "force-dynamic";

export default async function IndustryIndexPage() {
  const industries = await getIndustryList();
  return (
    <PublicPage title="Industries" description={metadata.description!} wide>
      <ul className="ds-directory">
        {industries.map((row) => (
          <li key={row.slug} className="ds-directory__item">
            <Link className="ds-directory__link" href={`/stocks/industry/${row.slug}`}><span className="ds-directory__label">{row.y_industry}</span><small className="ds-directory__meta">{row.company_count} companies</small></Link>
          </li>
        ))}
      </ul>
    </PublicPage>
  );
}
