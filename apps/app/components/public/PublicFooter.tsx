import Link from "next/link";
import { BrandMark } from "@/components/ui/BrandMark";

// "Explore" everywhere -- this used to say "Company research" and link to
// one specific example ticker page (a different per-caller URL each time),
// while the header nav had already been renamed to "Explore" pointing at
// /explore. Same underlying concept, two different names in two different
// places on the same page -- fixed by using the one real name and the one
// real destination, matching the header exactly.
export function PublicFooter() {
  return <footer className="public-footer">
    <div className="footer-brand"><BrandMark size="small" />scrooner</div>
    <div className="footer-links">
      <Link href="/app/screens/new">Create screen</Link><Link href="/explore">Explore</Link><Link href="/methodology">Methodology</Link><Link href="/data-sources">Data sources</Link><Link href="/about">About</Link><Link href="/pricing">Access</Link><Link href="/privacy">Privacy</Link><Link href="/terms">Terms</Link>
      <a href="https://www.sec.gov/edgar/search/" target="_blank" rel="noreferrer">SEC EDGAR <span aria-hidden="true">↗</span></a>
    </div>
    <p className="footer-note">Financial data sourced from SEC EDGAR filings. For research and educational purposes only—not investment advice.</p>
  </footer>;
}
