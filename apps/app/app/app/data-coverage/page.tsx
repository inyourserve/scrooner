import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { ArrowDown, ArrowRight, ArrowUp, Building2, Database, Minus, Search } from "lucide-react";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import { PageShell } from "@/components/layout/PageShell";
import { GroupCoverage, isCoverageBand } from "@/components/data-coverage/GroupCoverage";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardDescription, CardHeader, CardHeading, CardTitle } from "@/components/ui/Card";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableHeader, TableRow, TableRowHeader } from "@/components/ui/Table";
import { backendUrl } from "@/lib/backend";
import { buildLoginHref } from "@/lib/auth/redirect";
import { createClient } from "@/lib/supabase/server";
import styles from "./data-coverage.module.css";

export const metadata: Metadata = { title: "Data coverage — Scrooner" };
export const dynamic = "force-dynamic";

type HistoryRow = { date: string; metric_score: string | null; core_score: string | null; concept_score: string | null; total_active_companies: number };
type MetricRow = { metric_name: string; companies_covered: number; total_active_companies: number; coverage_pct: string; previous_coverage_pct: string | null; delta: string | null };
type CoveragePayload = { as_of: string | null; history: HistoryRow[]; weakest_metrics: MetricRow[] };

type CompanyItem = { data_point_name: string; data_point_type: string; status: "present" | "not_applicable" | "gap"; note: string | null };
type CompanyCoverage = {
  company_id: number;
  cik: string;
  company_name: string;
  sic_description: string | null;
  status: string;
  populations: string[];
  items: CompanyItem[];
  counts: Record<string, number>;
  coverage_pct: number | null;
};

type Props = { searchParams: Promise<{ ticker?: string; band?: string }> };

function score(value: string | null) { return value === null ? "—" : `${Number(value).toFixed(1)}%`; }
function label(value: string) { return value.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase()); }
function delta(value: string | null) {
  if (value === null) return <Badge>Baseline</Badge>;
  const number = Number(value);
  if (number > 0) return <Badge tone="positive"><ArrowUp size={12} aria-hidden="true" /> {number.toFixed(2)} pp</Badge>;
  if (number < 0) return <Badge tone="negative"><ArrowDown size={12} aria-hidden="true" /> {Math.abs(number).toFixed(2)} pp</Badge>;
  return <Badge><Minus size={12} aria-hidden="true" /> No change</Badge>;
}

function statusIcon(status: CompanyItem["status"]) {
  if (status === "present") return <Badge tone="positive">Present</Badge>;
  if (status === "not_applicable") return <Badge>N/A</Badge>;
  return <Badge tone="negative">Gap</Badge>;
}

export default async function DataCoveragePage({ searchParams }: Props) {
  const { ticker: requestedTicker, band: requestedBand } = await searchParams;
  const band = isCoverageBand(requestedBand) ? requestedBand : "top_1000";
  const supabase = await createClient();
  const { data } = await supabase.auth.getSession();
  if (!data.session?.access_token) redirect(buildLoginHref("/app/data-coverage"));
  const accessToken = data.session.access_token;
  const response = await fetch(backendUrl("/v1/data-coverage?days=90"), { cache: "no-store", headers: { accept: "application/json", authorization: `Bearer ${accessToken}` } });
  if (!response.ok) throw new Error("Data coverage could not be loaded.");
  const coverage = await response.json() as CoveragePayload;
  const latest = coverage.history[0];
  const previous = coverage.history[1];

  let companyCoverage: CompanyCoverage | null = null;
  let companyError: string | null = null;
  if (requestedTicker) {
    const companyResponse = await fetch(backendUrl(`/v1/data-coverage/company/${encodeURIComponent(requestedTicker)}`), {
      cache: "no-store",
      headers: { accept: "application/json", authorization: `Bearer ${accessToken}` },
    });
    if (companyResponse.status === 404) {
      companyError = `No company found for ticker "${requestedTicker}".`;
    } else if (!companyResponse.ok) {
      companyError = "Company coverage could not be loaded.";
    } else {
      companyCoverage = await companyResponse.json() as CompanyCoverage;
    }
  }

  return <PageShell>
    <WorkspaceHeader eyebrow="Pipeline health" title="Data coverage" description="Track whether company and metric coverage is improving, stable, or regressing over time." trustItems={["UTC daily snapshots", "Real active-company denominator"]} />
    <AppPageLayout>
    <section className={styles.summary} aria-label="Latest coverage scores">
      {[
        ["Core screening metrics", latest?.core_score, previous?.core_score],
        ["All active metrics", latest?.metric_score, previous?.metric_score],
        ["Canonical concepts", latest?.concept_score, previous?.concept_score],
      ].map(([title, current, prior]) => <Card variant="subtle" key={title}><CardContent className={styles.summaryContent}><small>{title}</small><strong>{score(current ?? null)}</strong>{delta(current && prior ? String(Number(current) - Number(prior)) : null)}</CardContent></Card>)}
    </section>

    <div className={styles.grid}>
      <Card className={styles.tableCard}>
        <CardHeader><CardHeading><CardTitle>Coverage trend</CardTitle><CardDescription>One persisted log per UTC date. Latest snapshot: {coverage.as_of ?? "not available"}.</CardDescription></CardHeading><ArrowRight size={18} aria-hidden="true" /></CardHeader>
        <TableContainer aria-label="Date-wise coverage history"><Table><TableHeader><TableRow><TableHead>Date</TableHead><TableHead data-align="right">Core metrics</TableHead><TableHead data-align="right">All metrics</TableHead><TableHead data-align="right">Concepts</TableHead><TableHead data-align="right">Companies</TableHead></TableRow></TableHeader><TableBody>{coverage.history.map((row) => <TableRow key={row.date}><TableRowHeader>{row.date}</TableRowHeader><TableCell data-align="right">{score(row.core_score)}</TableCell><TableCell data-align="right">{score(row.metric_score)}</TableCell><TableCell data-align="right">{score(row.concept_score)}</TableCell><TableCell data-align="right">{row.total_active_companies.toLocaleString("en-US")}</TableCell></TableRow>)}</TableBody></Table></TableContainer>
      </Card>

      <Card className={styles.tableCard}>
        <CardHeader><CardHeading><CardTitle>Weakest metrics</CardTitle><CardDescription>Lowest current company coverage, with movement since the previous snapshot.</CardDescription></CardHeading></CardHeader>
        <TableContainer aria-label="Lowest coverage metrics"><Table><TableHeader><TableRow><TableHead>Metric</TableHead><TableHead data-align="right">Coverage</TableHead><TableHead data-align="right">Covered</TableHead><TableHead>Change</TableHead></TableRow></TableHeader><TableBody>{coverage.weakest_metrics.map((metric) => <TableRow key={metric.metric_name}><TableRowHeader>{label(metric.metric_name)}</TableRowHeader><TableCell data-align="right"><strong>{score(metric.coverage_pct)}</strong></TableCell><TableCell data-align="right">{metric.companies_covered.toLocaleString("en-US")} / {metric.total_active_companies.toLocaleString("en-US")}</TableCell><TableCell>{delta(metric.delta)}</TableCell></TableRow>)}</TableBody></Table></TableContainer>
      </Card>
    </div>

    <GroupCoverage accessToken={accessToken} band={band} />


    <Card className={styles.companyCard}>
      <CardHeader>
        <CardHeading>
          <CardTitle>Company-wise coverage</CardTitle>
          <CardDescription>Look up one company: what it has, what genuinely doesn&rsquo;t apply to it, and what&rsquo;s a real gap — with a plain-English reason for every absence.</CardDescription>
        </CardHeading>
      </CardHeader>
      <form method="get" className={styles.companySearch} aria-label="Look up a company by ticker">
        <label htmlFor="coverage-ticker">US ticker symbol</label>
        <div className={styles.searchControl}>
          <Search size={16} aria-hidden="true" />
          <input id="coverage-ticker" type="text" name="ticker" defaultValue={requestedTicker ?? ""} placeholder="e.g. AAPL" autoCapitalize="characters" spellCheck={false} />
          <button type="submit">Look up coverage</button>
        </div>
      </form>
      {companyError && <p className={styles.companyError} role="alert">{companyError}</p>}
      {!requestedTicker && <div className={styles.companyPrompt}><Database size={20} aria-hidden="true" /><div><strong>Inspect the source of truth</strong><p>Search a ticker to see every expected data point and distinguish a genuine gap from a metric that does not apply.</p></div></div>}
      {companyCoverage && (
        <div className={styles.companyResult}>
          <div className={styles.companyOverview}>
            <span className={styles.companyIcon}><Building2 size={18} aria-hidden="true" /></span>
            <div><h3>{companyCoverage.company_name}</h3><p>{companyCoverage.sic_description ?? "Sector unavailable"} · CIK {companyCoverage.cik}</p></div>
            <div className={styles.coverageScore}><strong>{companyCoverage.coverage_pct !== null ? `${companyCoverage.coverage_pct}%` : "—"}</strong><span>coverage</span></div>
          </div>
          <dl className={styles.companyStats}>
            <div><dt>Present</dt><dd>{companyCoverage.counts.present ?? 0}</dd></div>
            <div><dt>Genuine gaps</dt><dd>{companyCoverage.counts.gap ?? 0}</dd></div>
            <div><dt>Not applicable</dt><dd>{companyCoverage.counts.not_applicable ?? 0}</dd></div>
            <div><dt>Populations</dt><dd>{companyCoverage.populations.length > 0 ? companyCoverage.populations.join(", ") : "None"}</dd></div>
          </dl>
          <TableContainer aria-label="Per-data-point coverage for this company">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Data point</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Note</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {companyCoverage.items.map((item) => (
                  <TableRow key={item.data_point_name}>
                    <TableRowHeader>{label(item.data_point_name)}</TableRowHeader>
                    <TableCell>{item.data_point_type}</TableCell>
                    <TableCell>{statusIcon(item.status)}</TableCell>
                    <TableCell>{item.note ?? ""}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </div>
      )}
    </Card>
    </AppPageLayout>
  </PageShell>;
}
