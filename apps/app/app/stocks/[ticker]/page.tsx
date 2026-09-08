import type { Metadata } from "next";
import Link from "next/link";
import { ExternalLink } from "lucide-react";
import { cache, Fragment } from "react";
import { notFound, permanentRedirect } from "next/navigation";
import { FinancialTable } from "@/components/company/FinancialTable";
import { MetricGrid, type MetricItem } from "@/components/company/MetricGrid";
import { PriceChart } from "@/components/company/PriceChart";
import { ResearchSection } from "@/components/company/ResearchSection";
import { StockSectionNav, type StockSectionLink } from "@/components/company/StockSectionNav";
import { PublicFooter } from "@/components/public/PublicFooter";
import { PublicHeader } from "@/components/public/PublicHeader";
import { Delta } from "@/components/scrooner/Delta";
import { EmptyState } from "@/components/scrooner/EmptyState";
import { StockHeader } from "@/components/scrooner/StockHeader";
import { getCompanyPageData, type FilingRow, type MetricRow, type SegmentRevenueRow, type Statement } from "@/lib/company/db";
import { fmtNum, fmtPct, fmtShares } from "@/lib/company/format";
import { buildChecklist } from "@/lib/company/pros-cons";

export const dynamic = "force-dynamic";
type Props = { params: Promise<{ ticker: string }> };
const getStock = cache(getCompanyPageData);

const metricGroups: { title: string; metrics: [string, string, MetricItem["kind"]][] }[] = [
  { title: "Valuation", metrics: [["trailing_pe", "P/E", "multiple"], ["price_to_sales", "Price / Sales", "multiple"], ["price_to_book", "Price / Book", "multiple"], ["dividend_yield", "Dividend yield", "pct"], ["peg_ratio", "PEG", "multiple"], ["ev_ebitda", "EV / EBITDA", "multiple"]] },
  { title: "Growth", metrics: [["revenue_growth_yoy", "Revenue growth · YoY", "pct"], ["revenue_growth_3y_cagr", "Revenue growth · 3Y", "pct"], ["revenue_growth_5y_cagr", "Revenue growth · 5Y", "pct"], ["eps_growth_yoy", "EPS growth · YoY", "pct"], ["eps_growth_3y_cagr", "EPS growth · 3Y", "pct"]] },
  { title: "Profitability", metrics: [["gross_margin", "Gross margin", "pct"], ["operating_margin", "Operating margin", "pct"], ["net_margin", "Net margin", "pct"], ["roe", "ROE", "pct"], ["roic", "ROIC", "pct"], ["roa", "ROA", "pct"]] },
  { title: "Financial strength", metrics: [["current_ratio", "Current ratio", "multiple"], ["quick_ratio", "Quick ratio", "multiple"], ["debt_to_equity", "Debt / equity", "multiple"], ["interest_coverage_ratio", "Interest coverage", "multiple"], ["net_debt_ebitda", "Net debt / EBITDA", "multiple"], ["piotroski_f_score", "Piotroski F-Score", "score"]] },
  { title: "Cash flow and allocation", metrics: [["fcf", "Free cash flow", "dollar"], ["fcf_margin", "FCF margin", "pct"], ["buyback_yield", "Buyback yield", "pct"], ["total_shareholder_yield", "Shareholder yield", "pct"], ["share_dilution_trend", "Share dilution · YoY", "pct"]] },
];

const sections: StockSectionLink[] = [
  { id: "overview", label: "Overview" }, { id: "analysis", label: "Analysis" },
  { id: "chart", label: "Chart" }, { id: "quarterly-results", label: "Quarters" },
  { id: "profit-loss", label: "Income" }, { id: "balance-sheet", label: "Balance sheet" },
  { id: "cash-flow", label: "Cash flow" }, { id: "ratios", label: "Ratios" },
  { id: "peers", label: "Peers" }, { id: "shareholding", label: "Ownership" },
  { id: "documents", label: "Documents" },
];

function secUrl(cik: string, accession: string) {
  return `https://www.sec.gov/Archives/edgar/data/${cik.replace(/^0+/, "") || "0"}/${accession.replaceAll("-", "")}/${accession}-index.html`;
}

// A fixed, deterministic priority order -- not alphabetical or first-seen --
// so the same company's documents always group the same way, and the most
// investor-relevant filing types lead. `match` checks the exact form prefix
// SEC itself uses (10-K/A still starts with "10-K", etc.).
const FILING_GROUPS: { label: string; match: (form: string) => boolean }[] = [
  { label: "Annual reports", match: (form) => form.startsWith("10-K") },
  { label: "Quarterly reports", match: (form) => form.startsWith("10-Q") },
  { label: "Current reports", match: (form) => form.startsWith("8-K") },
  { label: "Proxy statements", match: (form) => /^DEF(A|M|R)?\s?14A$/.test(form) },
  { label: "Insider transactions", match: (form) => /^[345](\/A)?$/.test(form) },
  { label: "Ownership disclosures", match: (form) => form.startsWith("SC 13") },
  { label: "Registration & offerings", match: (form) => /^(S-1|S-3|S-8|424B|FWP|144)/.test(form) },
];

function groupFilings(filings: FilingRow[]) {
  const buckets = new Map<string, FilingRow[]>();
  for (const filing of filings) {
    const label = FILING_GROUPS.find((group) => group.match(filing.form))?.label ?? "Other filings";
    (buckets.get(label) ?? buckets.set(label, []).get(label)!).push(filing);
  }
  return [...FILING_GROUPS.map((group) => group.label), "Other filings"]
    .filter((label) => buckets.has(label))
    .map((label) => ({ label, filings: buckets.get(label)! }));
}

const FILING_GROUP_VISIBLE = 5;

function filingItem(filing: FilingRow, cik: string) {
  return (
    <a className="filing-item" key={filing.accession_number} href={secUrl(cik, filing.accession_number)} target="_blank" rel="noreferrer">
      <span className="filing-item__title">{filing.items ? `Items ${filing.items}` : `${filing.form} filing`}<ExternalLink size={12} aria-hidden="true" /></span>
      <span className="filing-item__meta">Filed {filing.filing_date} · {filing.accession_number}</span>
    </a>
  );
}

// SEC's rendered segment report shows the filer's OWN period pairing (e.g. a
// 10-Q's "3 Months Ended" current-quarter-vs-prior-year-quarter columns, and
// separately its "9 Months Ended" YTD columns) -- never a clean single
// fiscal-year series. Pivoting groups same-duration periods together so each
// segment's real year-over-year comparison reads across a row, matching
// FinancialTable's own rows-are-line-items/columns-are-periods shape.
function parseFilingDateLabel(label: string): number {
  const match = label.match(/([A-Za-z]+)\.?\s+(\d{1,2}),\s+(\d{4})/);
  if (!match) return 0;
  const months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];
  const monthIndex = months.indexOf(match[1].slice(0, 3).toLowerCase());
  if (monthIndex < 0) return 0;
  return new Date(Number(match[3]), monthIndex, Number(match[2])).getTime();
}

function pivotSegmentRevenue(rows: SegmentRevenueRow[]) {
  const typeOrder: string[] = [];
  const endsByType = new Map<string, Set<string>>();
  for (const row of rows) {
    if (!endsByType.has(row.period_type)) { endsByType.set(row.period_type, new Set()); typeOrder.push(row.period_type); }
    endsByType.get(row.period_type)!.add(row.period_end);
  }
  const durationGroups = typeOrder.map((periodType) => ({
    periodType,
    periodEnds: [...endsByType.get(periodType)!].sort((a, b) => parseFilingDateLabel(a) - parseFilingDateLabel(b)),
  }));

  const lookup = new Map(rows.map((row) => [`${row.segment_name}|${row.period_type}|${row.period_end}`, row.value]));
  const segments = [...new Set(rows.map((row) => row.segment_name))].map((name) => ({
    name,
    values: durationGroups.map((group) => group.periodEnds.map((end) => lookup.get(`${name}|${group.periodType}|${end}`) ?? null)),
  }));
  return { durationGroups, segments };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { ticker } = await params;
  const data = await getStock(ticker);
  if (!data) return { title: "Company not found — Scrooner", robots: { index: false } };
  return {
    title: `${data.company.company_name} (${data.company.ticker}) — Scrooner`,
    description: `Inspect ${data.company.company_name} financial statements, ratios, ownership, and recent SEC filings.`,
    alternates: { canonical: `/stocks/${ticker.toLowerCase()}` },
  };
}

function StatementSection({ id, title, description, companyName, statement, periods }: { id: string; title: string; description: string; companyName: string; statement: Statement; periods: number }) {
  return <ResearchSection id={id} title={title} description={description} meta={<span className="data-unit">USD · auto-scaled</span>}><FinancialTable title={title} companyName={companyName} statement={statement} periods={periods} /></ResearchSection>;
}

export default async function StockPage({ params }: Props) {
  const { ticker } = await params;
  if (ticker !== ticker.toLowerCase()) permanentRedirect(`/stocks/${ticker.toLowerCase()}`);
  const data = await getStock(ticker);
  if (!data) notFound();

  const { company, metrics, latestPrice, institutionalSummary, insiderOwnershipSummary, fundSummary } = data;
  const metric = (name: string): MetricRow | undefined => metrics[name];
  const shortName = company.company_name.replace(/\s+(incorporated|inc\.?|corporation|corp\.?|company|co\.?)$/i, "");
  // Day-over-day change: latestPrice is the freshest Alpaca bar, priceHistory
  // is the daily series feeding the chart -- the second-to-last history point
  // is the prior close. Left null (never guessed) if fewer than 2 points exist.
  const previousClose = data.priceHistory.length >= 2 ? Number(data.priceHistory[data.priceHistory.length - 2].price) : null;
  const currentPrice = latestPrice ? Number(latestPrice.price) : null;
  const dayChangeAbs = currentPrice != null && previousClose != null && Number.isFinite(previousClose) ? currentPrice - previousClose : null;
  const dayChangePct = dayChangeAbs != null && previousClose ? (dayChangeAbs / previousClose) * 100 : null;
  const keyMetrics: MetricItem[] = [
    { label: "Market cap", row: metric("market_cap"), kind: "dollar" },
    { label: "P/E · TTM", row: metric("trailing_pe"), kind: "multiple" },
    { label: "Revenue growth · 3Y", row: metric("revenue_growth_3y_cagr"), kind: "pct" },
    { label: "Operating margin", row: metric("operating_margin"), kind: "pct" },
    { label: "ROIC", row: metric("roic"), kind: "pct" },
    { label: "Debt / equity", row: metric("debt_to_equity"), kind: "multiple" },
  ];
  const checklist = buildChecklist(metrics, data.metricHistory);
  const strengths = checklist.filter((item) => item.kind === "pro");
  const risks = checklist.filter((item) => item.kind === "con");
  const institutional = institutionalSummary?.total_institutional_pct == null ? null : Number(institutionalSummary.total_institutional_pct);
  const institutionalPercent = institutional !== null && Number.isFinite(institutional) ? Math.max(0, Math.min(100, institutional * 100)) : null;
  const about = company.about_text?.replace(/^\s*company background\s*[:—-]?\s*/i, "").trim();

  return <div className="public-site stock-page">
    <PublicHeader current="company" companyHref={`/stocks/${ticker}`} skipHref="#company-content" />
    <StockSectionNav sections={sections} />

    <main className="stock-page__main" id="company-content">
      <section className="stock-hero" id="overview" aria-labelledby="company-name">
        <StockHeader
          ticker={company.ticker}
          companyName={company.company_name}
          sector={company.sector}
          status={company.status}
          price={latestPrice ? { value: Number(latestPrice.price), asOfLabel: new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", dateStyle: "medium", timeStyle: "short" }).format(new Date(latestPrice.bar_timestamp)) } : null}
          dayChangePct={dayChangePct}
          dayChangeAbs={dayChangeAbs}
          website={company.website}
        />

        <div className="stock-snapshot"><div className="stock-snapshot__metrics"><p className="overline">Investor snapshot</p><MetricGrid items={keyMetrics} dense /><a href="#ratios" className="quiet-link">View all ratios ↓</a></div><div className="stock-snapshot__about"><p className="overline">Business overview</p><p>{about || `${company.company_name} is an SEC registrant in the ${company.sector ?? "unclassified"} sector.`}</p><dl>{data.employeeHeadcountHistory[0] && <div><dt>Employees</dt><dd>{data.employeeHeadcountHistory[0].is_approximate ? "~" : ""}{data.employeeHeadcountHistory[0].headcount.toLocaleString("en-US")}</dd></div>}{data.segmentRevenue.length > 0 && <div><dt>Revenue segments</dt><dd>{new Set(data.segmentRevenue.map((item) => item.segment_name)).size}</dd></div>}{data.publicFloat && <div><dt>Public float</dt><dd>${fmtNum(data.publicFloat.value)}</dd></div>}<div><dt>Source</dt><dd>SEC EDGAR</dd></div></dl><details className="plain-disclosure"><summary>Company details</summary><p>CIK {company.cik}{company.business_address_city || company.business_address_state ? ` · ${[company.business_address_city, company.business_address_state].filter(Boolean).join(", ")}` : ""}</p></details></div></div>
      </section>

      <ResearchSection id="analysis" title={`${shortName} analysis`} description="Deterministic observations from reported results—not a recommendation." className="analysis-section">
        <div className="signal-ledger"><div><h3><span className="signal-dot signal-dot--positive" />Strengths</h3>{strengths.length ? <ul>{strengths.map((item) => <li key={item.text}>{item.text}</li>)}</ul> : <p className="empty-copy">No positive rule-based observation is available.</p>}</div><div><h3><span className="signal-dot signal-dot--negative" />Watch items</h3>{risks.length ? <ul>{risks.map((item) => <li key={item.text}>{item.text}</li>)}</ul> : <p className="empty-copy">No cautionary rule-based observation is available.</p>}</div></div>
      </ResearchSection>

      <ResearchSection id="chart" title={`${shortName} price chart`} description="Historical daily closes; market data may be delayed." meta={<span className="data-unit">USD</span>}><PriceChart companyName={company.company_name} points={data.priceHistory} /></ResearchSection>

      <StatementSection id="quarterly-results" title={`${shortName} quarterly results`} description="Recent revenue, profitability, and earnings." companyName={company.company_name} statement={data.quarterlyResults} periods={8} />
      <StatementSection id="profit-loss" title={`${shortName} income statement`} description="Annual operating performance." companyName={company.company_name} statement={data.incomeStatement} periods={5} />
      <StatementSection id="balance-sheet" title={`${shortName} balance sheet`} description="Assets, obligations, and shareholder capital." companyName={company.company_name} statement={data.balanceSheet} periods={5} />
      <StatementSection id="cash-flow" title={`${shortName} cash flow`} description="Cash generated, invested, and returned to shareholders." companyName={company.company_name} statement={data.cashFlow} periods={5} />

      <ResearchSection id="ratios" title={`${shortName} financial ratios`} description="Latest available values grouped by investor question.">
        <div className="ratio-groups">{metricGroups.map((group, index) => <details className="ratio-group" key={group.title} open={index < 2}><summary><span>{group.title}</span><small>{group.metrics.length} metrics</small></summary><MetricGrid dense items={group.metrics.map(([name, label, kind]) => ({ label, kind, row: metric(name) }))} /></details>)}</div>
      </ResearchSection>

      <ResearchSection id="peers" title="Peer comparison" description="Companies sharing the closest available SEC industry classification.">
        {data.peerCompanies.length ? <><p className="inline-note">Peer classification is a starting point, not a claim that business models are identical.</p><div className="statement-scroll"><table className="research-table"><thead><tr><th>Company</th><th>ROIC</th><th>Revenue growth · 3Y</th><th>Net margin</th><th>ROE</th></tr></thead><tbody>{data.peerCompanies.map((peer) => <tr key={peer.ticker}><th scope="row"><Link href={`/stocks/${peer.ticker.toLowerCase()}`}>{peer.company_name}<small>{peer.ticker}</small></Link></th><td>{fmtPct(peer.roic)}</td><td>{fmtPct(peer.revenue_growth_3y_cagr)}</td><td>{fmtPct(peer.net_margin)}</td><td>{fmtPct(peer.roe)}</td></tr>)}</tbody></table></div></> : <EmptyState description="No sufficiently comparable companies are available yet." />}
      </ResearchSection>

      <ResearchSection id="shareholding" title={`${company.company_name} ownership`} description="Reported regulatory positions—not live beneficial ownership.">
        <div className="ownership-overview">{institutionalPercent === null ? <EmptyState description="A complete institutional ownership estimate is not available." /> : <div className="ownership-mix"><div className="ownership-mix__heading"><div><span>Institutions</span><strong>{institutionalPercent.toFixed(1)}%</strong></div><div><span>Other shareholders</span><strong>{(100 - institutionalPercent).toFixed(1)}%</strong></div></div><div className="ownership-mix__bar" aria-label={`Institutions ${institutionalPercent.toFixed(1)} percent, other shareholders ${(100 - institutionalPercent).toFixed(1)} percent`}><span style={{ width: `${institutionalPercent}%` }} /></div><p>These two categories total 100%. Insider and mutual-fund figures overlap with them and must not be added.</p></div>}<dl className="ownership-facts"><div><dt>Institutional change</dt><dd>{fmtPct(institutionalSummary?.qoq_change_pct)}</dd><small>vs prior quarter</small></div><div><dt>Insider ownership</dt><dd>{fmtPct(insiderOwnershipSummary?.ownership_pct)}</dd><small>{insiderOwnershipSummary ? `${insiderOwnershipSummary.distinct_insiders_count} reporting insiders` : "Not available"}</small></div><div><dt>Through mutual funds</dt><dd>{fmtPct(fundSummary?.total_fund_ownership_pct)}</dd><small>included within institutions</small></div></dl></div>
        <div className="disclosure-list">
          <details><summary><span>Institutional holders</span><small>{data.institutionalHolders.length} reported</small></summary><div className="statement-scroll"><table className="research-table"><thead><tr><th>Institution</th><th>Shares</th><th>Value</th><th>Filed</th></tr></thead><tbody>{data.institutionalHolders.map((holder, index) => <tr key={`${holder.filer_name}-${index}`}><th scope="row">{holder.filer_name}</th><td>{fmtShares(holder.shares)}</td><td>{holder.value_usd ? `$${fmtNum(holder.value_usd)}` : "—"}</td><td>{holder.filing_date ?? "—"}</td></tr>)}</tbody></table></div></details>
          <details><summary><span>Insider transactions</span><small>{data.insiderTransactions.length} reported</small></summary><div className="statement-scroll"><table className="research-table"><thead><tr><th>Insider</th><th>Type</th><th>Shares</th><th>Price</th><th>Date</th></tr></thead><tbody>{data.insiderTransactions.map((item, index) => <tr key={`${item.accession_number}-${index}`}><th scope="row">{item.reporting_owner_name}<small>{item.officer_title}</small></th><td>{item.transaction_code ?? "—"} · {item.acquired_disposed_code === "A" ? "Acquired" : item.acquired_disposed_code === "D" ? "Disposed" : "Reported"}</td><td>{fmtShares(item.shares)}</td><td>{item.price_per_share ? `$${Number(item.price_per_share).toFixed(2)}` : "—"}</td><td>{item.transaction_date ?? "—"}</td></tr>)}</tbody></table></div></details>
          {fundSummary && <details><summary><span>Mutual-fund holders</span><small>{fundSummary.top_holders.length} reported</small></summary><div className="statement-scroll"><table className="research-table"><thead><tr><th>Fund</th><th>Shares</th><th>Value</th><th>As of</th></tr></thead><tbody>{fundSummary.top_holders.map((holder, index) => <tr key={`${holder.fund_cik}-${holder.report_period}-${index}`}><th scope="row">{holder.fund_name}<small>{holder.fund_family}</small></th><td>{fmtShares(holder.shares)}</td><td>{holder.value_usd ? `$${fmtNum(holder.value_usd)}` : "—"}</td><td>{holder.report_period}</td></tr>)}</tbody></table></div></details>}
          <details><summary><span>Reported holders above 5%</span><small>{data.beneficialOwnership.length} filings</small></summary><div className="statement-scroll"><table className="research-table"><thead><tr><th>Filer</th><th>Schedule</th><th>Filed</th><th>Source</th></tr></thead><tbody>{data.beneficialOwnership.map((holder, index) => <tr key={`${holder.accession_number}-${index}`}><th scope="row">{holder.filer_name}</th><td>{holder.schedule_type}{holder.is_amendment ? "/A" : ""}</td><td>{holder.filing_date ?? "—"}</td><td><a href={secUrl(company.cik, holder.accession_number)} target="_blank" rel="noreferrer">SEC filing ↗</a></td></tr>)}</tbody></table></div></details>
        </div>
      </ResearchSection>

      {data.segmentRevenue.length > 0 && (() => {
        const { durationGroups, segments } = pivotSegmentRevenue(data.segmentRevenue);
        return (
          <ResearchSection id="segments" title="Revenue by segment" description="Latest dimensional revenue disclosures, grouped so each segment's year-over-year change reads across a row; values use the filing's reported unit.">
            <div className="statement-scroll">
              <table className="research-table segment-table">
                <thead>
                  <tr>
                    <th rowSpan={2}>Segment</th>
                    {durationGroups.map((group) => (
                      <th key={group.periodType} colSpan={group.periodEnds.length + (group.periodEnds.length === 2 ? 1 : 0)} className="segment-table__group">{group.periodType}</th>
                    ))}
                  </tr>
                  <tr>
                    {durationGroups.map((group) => (
                      <Fragment key={group.periodType}>
                        {group.periodEnds.map((end) => <th key={`${group.periodType}-${end}`}>{end}</th>)}
                        {group.periodEnds.length === 2 && <th>YoY</th>}
                      </Fragment>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {segments.map((segment) => (
                    <tr key={segment.name}>
                      <th scope="row">{segment.name}</th>
                      {segment.values.map((values, groupIndex) => {
                        const prior = values[0] != null ? Number(values[0]) : null;
                        const latest = values.length === 2 && values[1] != null ? Number(values[1]) : null;
                        const yoyPct = prior && latest != null ? ((latest / prior) - 1) * 100 : null;
                        return (
                          <Fragment key={groupIndex}>
                            {values.map((value, valueIndex) => <td key={valueIndex}>{value != null ? Number(value).toLocaleString("en-US") : "—"}</td>)}
                            {values.length === 2 && <td><Delta value={yoyPct} size="sm" /></td>}
                          </Fragment>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ResearchSection>
        );
      })()}

      <ResearchSection id="documents" title={`${company.company_name} documents`} description="Recent company filings, grouped by type and linked to the original SEC record.">
        {data.filings.length ? (
          <div className="filing-groups">
            {groupFilings(data.filings).map((group) => {
              const visible = group.filings.slice(0, FILING_GROUP_VISIBLE);
              const rest = group.filings.slice(FILING_GROUP_VISIBLE);
              return (
                <div className="filing-group-card" key={group.label}>
                  <div className="filing-group-card__header"><h3>{group.label}</h3><span>{group.filings.length}</span></div>
                  <div className="filing-group-card__list">
                    {visible.map((filing) => filingItem(filing, company.cik))}
                    {rest.length > 0 && (
                      <details className="filing-group-card__more">
                        <summary><span className="filing-group-card__more-label">Show {rest.length} more</span><span className="filing-group-card__less-label">Show less</span></summary>
                        <div className="filing-group-card__more-list">{rest.map((filing) => filingItem(filing, company.cik))}</div>
                      </details>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : <EmptyState description="No recent SEC filings are available." />}
      </ResearchSection>
    </main>
    <PublicFooter companyHref={`/stocks/${ticker}`} />
  </div>;
}
