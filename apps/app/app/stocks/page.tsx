import type { Metadata } from "next";
import Link from "next/link";
import { PublicPage } from "@/components/public/PublicPage";
import { loadFullCompanyDirectory } from "@/lib/company/db";

export const metadata: Metadata = {
  title: "All stocks — every US-listed company Scrooner covers",
  description: "Browse the full directory of US-listed companies covered by Scrooner, one letter at a time.",
};
export const dynamic = "force-dynamic";

const LETTERS = ["#", ..."ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")];

function firstLetter(name: string) {
  const char = name.trim().charAt(0).toUpperCase();
  return /[A-Z]/.test(char) ? char : "#";
}

type Props = { searchParams: Promise<{ letter?: string }> };

// A single page listing all ~6,000 covered companies is a bad idea on its
// own terms, not just a style nit -- it ships a huge HTML payload on every
// load, and scrolling past thousands of rows to find one company is worse
// than just using search. Paginated by first letter instead: each request
// renders one letter's worth (tens to a few hundred rows), and the letter
// lives in a query param (not a path segment) specifically so it can never
// collide with a real single-letter ticker under /stocks/{ticker} (e.g.
// ticker "A" is a real company -- Agilent).
export default async function AllStocksPage({ searchParams }: Props) {
  const { letter: requested } = await searchParams;
  const rows = await loadFullCompanyDirectory();

  const counts = new Map<string, number>();
  for (const row of rows) {
    const key = firstLetter(row.company_name);
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  const activeLetters = LETTERS.filter((entry) => counts.has(entry));

  const normalized = requested?.toUpperCase();
  const letter = normalized && activeLetters.includes(normalized) ? normalized : activeLetters[0];
  const companies = rows
    .filter((row) => firstLetter(row.company_name) === letter)
    .sort((a, b) => a.company_name.localeCompare(b.company_name));

  return (
    <PublicPage current="company" title="All stocks" description={`${rows.length.toLocaleString()} US-listed companies covered by Scrooner, browsable A to Z.`}>
      <nav className="stocks-directory-jump" aria-label="Jump to letter">
        {activeLetters.map((entry) => (
          <Link key={entry} href={`/stocks?letter=${entry}`} aria-current={entry === letter ? "page" : undefined}>{entry}</Link>
        ))}
      </nav>
      <section aria-labelledby="stocks-letter-title">
        <div className="explore-section-heading">
          <h2 id="stocks-letter-title">{letter}</h2>
          <span className="public-meta">{companies.length.toLocaleString()} companies</span>
        </div>
        <div className="explore-grid">
          {companies.map((row) => (
            <Link key={row.ticker} href={`/stocks/${row.ticker.toLowerCase()}`} className="explore-item">
              <span>{row.company_name}</span>
              <small>{row.ticker}</small>
            </Link>
          ))}
        </div>
      </section>
      <p className="public-meta">Looking for something more specific? <Link href="/explore">Explore</Link> popular screens, sectors, and industries.</p>
    </PublicPage>
  );
}
