import Link from "next/link";
import { SearchCommand } from "@/components/scrooner/SearchCommand";
import { BrandMark } from "@/components/ui/BrandMark";

type Current = "home" | "company" | "methodology" | "data-sources" | "about" | "pricing" | "privacy" | "terms";

export function PublicHeader({ current, companyHref = "/#company-search", skipHref = "#main-content" }: { current?: Current; companyHref?: string; skipHref?: string }) {
  const item = (href: string, label: string, active: boolean) => active ? <span aria-current="page">{label}</span> : <Link href={href}>{label}</Link>;
  return <>
    <a className="public-skip-link" href={skipHref}>Skip to main content</a>
    <header className="public-header"><nav className="public-nav" aria-label="Primary navigation">
      <Link href="/" className="public-brand" aria-label="Scrooner home"><BrandMark /><span className="brand-name">scrooner</span></Link>
      <div className="public-links">
        {item(companyHref, "Company research", current === "home" || current === "company")}
        {item("/app/screener", "Create screen", false)}
        {item("/methodology", "Methodology", current === "methodology")}
        {item("/data-sources", "Data sources", current === "data-sources")}
      </div>
      <SearchCommand />
      <Link className="ds-button ds-button--primary ds-button--small open-screener" href="/login">Sign in to screen</Link>
    </nav></header><div className="public-header-spacer" aria-hidden="true" />
  </>;
}
