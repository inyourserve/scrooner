import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { ArrowDown, ArrowRight, ArrowUp, Minus } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { PageShell } from "@/components/layout/PageShell";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardDescription, CardHeader, CardHeading, CardTitle } from "@/components/ui/Card";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableHeader, TableRow, TableRowHeader } from "@/components/ui/Table";
import { backendUrl } from "@/lib/backend";
import { buildLoginHref } from "@/lib/auth/redirect";
import { createClient } from "@/lib/supabase/server";

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

type Props = { searchParams: Promise<{ ticker?: string }> };

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
  const { ticker: requestedTicker } = await searchParams;
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

  return <PageShell className="coverage-dashboard">
    <PageHeader eyebrow="Pipeline health" title="Data coverage" description="Track whether company and metric coverage is improving, stable, or regressing over time." trustItems={["UTC daily snapshots", "Real active-company denominator"]} />
    <section className="coverage-dashboard__summary" aria-label="Latest coverage scores">
      {[
        ["Core screening metrics", latest?.core_score, previous?.core_score],
        ["All active metrics", latest?.metric_score, previous?.metric_score],
        ["Canonical concepts", latest?.concept_score, previous?.concept_score],
      ].map(([title, current, prior]) => <Card variant="subtle" key={title}><CardContent><small>{title}</small><strong>{score(current ?? null)}</strong>{delta(current && prior ? String(Number(current) - Number(prior)) : null)}</CardContent></Card>)}
    </section>

    <div className="coverage-dashboard__grid">
      <Card>
        <CardHeader><CardHeading><CardTitle>Coverage trend</CardTitle><CardDescription>One persisted log per UTC date. Latest snapshot: {coverage.as_of ?? "not available"}.</CardDescription></CardHeading><ArrowRight size={18} aria-hidden="true" /></CardHeader>
        <TableContainer aria-label="Date-wise coverage history"><Table><TableHeader><TableRow><TableHead>Date</TableHead><TableHead data-align="right">Core metrics</TableHead><TableHead data-align="right">All metrics</TableHead><TableHead data-align="right">Concepts</TableHead><TableHead data-align="right">Companies</TableHead></TableRow></TableHeader><TableBody>{coverage.history.map((row) => <TableRow key={row.date}><TableRowHeader>{row.date}</TableRowHeader><TableCell data-align="right">{score(row.core_score)}</TableCell><TableCell data-align="right">{score(row.metric_score)}</TableCell><TableCell data-align="right">{score(row.concept_score)}</TableCell><TableCell data-align="right">{row.total_active_companies.toLocaleString("en-US")}</TableCell></TableRow>)}</TableBody></Table></TableContainer>
      </Card>

      <Card>
        <CardHeader><CardHeading><CardTitle>Weakest metrics</CardTitle><CardDescription>Lowest current company coverage, with movement since the previous snapshot.</CardDescription></CardHeading></CardHeader>
        <TableContainer aria-label="Lowest coverage metrics"><Table><TableHeader><TableRow><TableHead>Metric</TableHead><TableHead data-align="right">Coverage</TableHead><TableHead data-align="right">Covered</TableHead><TableHead>Change</TableHead></TableRow></TableHeader><TableBody>{coverage.weakest_metrics.map((metric) => <TableRow key={metric.metric_name}><TableRowHeader>{label(metric.metric_name)}</TableRowHeader><TableCell data-align="right"><strong>{score(metric.coverage_pct)}</strong></TableCell><TableCell data-align="right">{metric.companies_covered.toLocaleString("en-US")} / {metric.total_active_companies.toLocaleString("en-US")}</TableCell><TableCell>{delta(metric.delta)}</TableCell></TableRow>)}</TableBody></Table></TableContainer>
      </Card>
    </div>

    <Card>
      <CardHeader>
        <CardHeading>
          <CardTitle>Company-wise coverage</CardTitle>
          <CardDescription>Look up one company: what it has, what genuinely doesn&rsquo;t apply to it, and what&rsquo;s a real gap — with a plain-English reason for every absence.</CardDescription>
        </CardHeading>
      </CardHeader>
      <form method="get" className="coverage-dashboard__company-search" aria-label="Look up a company by ticker">
        <input type="text" name="ticker" defaultValue={requestedTicker ?? ""} placeholder="Ticker, e.g. V" aria-label="Ticker" />
        <button type="submit">Look up</button>
      </form>
      {companyError && <p role="alert">{companyError}</p>}
      {companyCoverage && (
        <>
          <p>
            <strong>{companyCoverage.company_name}</strong> (CIK {companyCoverage.cik}) — {companyCoverage.sic_description ?? "sector unknown"}
            {" · "}
            Populations: {companyCoverage.populations.length > 0 ? companyCoverage.populations.join(", ") : "none"}
          </p>
          <p>
            <strong>{companyCoverage.coverage_pct !== null ? `${companyCoverage.coverage_pct}%` : "—"}</strong> coverage
            {" "}({companyCoverage.counts.present ?? 0} present / {companyCoverage.counts.gap ?? 0} genuine gaps / {companyCoverage.counts.not_applicable ?? 0} not applicable)
          </p>
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
        </>
      )}
    </Card>
  </PageShell>;
}
