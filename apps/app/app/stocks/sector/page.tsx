import type { Metadata } from "next";
import Link from "next/link";
import { PublicPage } from "@/components/public/PublicPage";
import { getSectorList } from "@/lib/company/db";

export const metadata: Metadata = {
  title: "Sectors — browse US stocks",
  description: "All sectors covered by Scrooner, with the number of companies in each.",
};
export const dynamic = "force-dynamic";

export default async function SectorIndexPage() {
  const sectors = await getSectorList();
  return (
    <PublicPage title="Sectors" description={metadata.description!}>
      <ul>
        {sectors.map((row) => (
          <li key={row.slug}>
            <Link href={`/stocks/sector/${row.slug}`}>{row.sector}<span className="public-meta"> · {row.company_count} companies</span></Link>
          </li>
        ))}
      </ul>
    </PublicPage>
  );
}
