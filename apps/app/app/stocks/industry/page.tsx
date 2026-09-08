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
    <PublicPage title="Industries" description={metadata.description!}>
      <ul>
        {industries.map((row) => (
          <li key={row.slug}>
            <Link href={`/stocks/industry/${row.slug}`}>{row.y_industry}<span className="public-meta"> · {row.company_count} companies</span></Link>
          </li>
        ))}
      </ul>
    </PublicPage>
  );
}
