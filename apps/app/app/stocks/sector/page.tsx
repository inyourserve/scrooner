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
    <PublicPage title="Sectors" description={metadata.description!} wide>
      <ul className="ds-directory">
        {sectors.map((row) => (
          <li key={row.slug} className="ds-directory__item">
            <Link className="ds-directory__link" href={`/stocks/sector/${row.slug}`}><span className="ds-directory__label">{row.sector}</span><small className="ds-directory__meta">{row.company_count} companies</small></Link>
          </li>
        ))}
      </ul>
    </PublicPage>
  );
}
