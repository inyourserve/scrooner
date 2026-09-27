import { ResearchSection } from "@/components/company/ResearchSection";
import { stockPageSections } from "@/components/company/stockPageSections";
import { StockSectionNav } from "@/components/company/StockSectionNav";
import { PublicFooter } from "@/components/public/PublicFooter";
import { PublicHeader } from "@/components/public/PublicHeader";

// A cache MISS on this route (a ticker nobody has viewed in the last 15
// minutes -- lib/company/cache.ts) can genuinely take anywhere from ~150ms
// to several seconds (doc/learnings/2026-09-15-company-page-caching.md),
// and this page has no per-section Suspense boundaries -- one consolidated
// query means one consolidated wait. Without a loading.tsx, Next.js shows
// nothing at all for that whole span; with one, the shell below renders
// INSTANTLY (before the server component's data fetch even starts) and
// Next swaps in the real page the moment it resolves. Same principle as
// TableSkeleton (doc/design/shadcn-system.md section 12): shaped like the
// real content, not a spinner or "Loading..." text, and reusing the real
// page's own class names so there's minimal layout shift on swap.
//
// PublicHeader/StockSectionNav need no fetched data at all, so they render
// for real here -- only the data-dependent content area is a skeleton.
// Deliberately doesn't attempt to mirror all 11 sections of the real page
// (11 near-identical skeleton blocks would be pure repetition for a state
// users see for well under a second in the common case) -- the hero +
// snapshot metrics (what's above the fold) plus a couple of representative
// section shapes communicate "this is a stock page, it's loading" without
// that cost.
export default function StockPageLoading() {
  return (
    <div className="public-site stock-page" aria-busy="true" aria-label="Loading company page">
      <PublicHeader current="company" skipHref="#company-content" />
      <StockSectionNav sections={stockPageSections} />

      <main className="stock-page__main" id="company-content">
        <section className="stock-hero" aria-hidden="true">
          <div className="stock-hero__identity">
            <div className="stock-hero__title-row">
              <div>
                <p className="stock-hero__ticker"><span className="ds-skeleton ds-skeleton--text" style={{ width: "6ch", display: "inline-block" }} /></p>
                <h1><span className="ds-skeleton ds-skeleton--text" style={{ width: "18ch", height: "1.4em" }} /></h1>
              </div>
            </div>
            <div className="stock-hero__price">
              <span className="ds-skeleton ds-skeleton--text" style={{ width: "10ch", height: "1.6em" }} />
            </div>
          </div>

          <div className="stock-snapshot">
            <div className="stock-snapshot__metrics">
              <p className="section-label">Investor snapshot</p>
              <div className="metric-grid metric-grid-dense">
                {Array.from({ length: 6 }).map((_, index) => (
                  <div className="metric-cell" key={index}>
                    <span className="metric-label"><span className="ds-skeleton ds-skeleton--text" style={{ width: "70%" }} /></span>
                    <span className="metric-value"><span className="ds-skeleton ds-skeleton--value" style={{ width: "60%" }} /></span>
                  </div>
                ))}
              </div>
            </div>
            <div className="stock-snapshot__about">
              <p className="section-label">Business overview</p>
              <span className="ds-skeleton ds-skeleton--text" style={{ width: "100%" }} />
              <span className="ds-skeleton ds-skeleton--text" style={{ width: "92%" }} />
              <span className="ds-skeleton ds-skeleton--text" style={{ width: "75%" }} />
            </div>
          </div>
        </section>

        <ResearchSection id="chart" title="Price chart" description="Historical daily closes; market data may be delayed.">
          <div className="ds-skeleton" style={{ width: "100%", height: "260px" }} aria-hidden="true" />
        </ResearchSection>

        <ResearchSection id="quarterly-results" title="Quarterly results" description="Recent revenue, profitability, and earnings.">
          <div aria-hidden="true">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} style={{ display: "flex", gap: "1rem", padding: "0.5rem 0" }}>
                <span className="ds-skeleton ds-skeleton--text" style={{ width: "22%" }} />
                <span className="ds-skeleton ds-skeleton--text" style={{ width: "12%" }} />
                <span className="ds-skeleton ds-skeleton--text" style={{ width: "12%" }} />
                <span className="ds-skeleton ds-skeleton--text" style={{ width: "12%" }} />
                <span className="ds-skeleton ds-skeleton--text" style={{ width: "12%" }} />
              </div>
            ))}
          </div>
        </ResearchSection>
      </main>
      <PublicFooter />
    </div>
  );
}
