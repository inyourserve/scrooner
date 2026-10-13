import { ArrowDown, ArrowUp, Minus } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardHeading, CardTitle, CardDescription } from "@/components/ui/Card";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableHeader, TableRow, TableRowHeader } from "@/components/ui/Table";
import { backendUrl } from "@/lib/backend";
import styles from "./GroupCoverage.module.css";

type BandRow = { key: string; companies: number; score: string; delta: string | null; pct_ge90: string; pct_lt60: string };
type SectorRow = BandRow & { score_top2000: string | null; companies_top2000: number; score_all: string | null; companies_all: number };
type BandMetric = { metric_name: string; companies: number; covered: number; missing: number; coverage_pct: string; delta: string | null };
type Readiness = { key: string; ready: boolean; checks: { average: boolean; tail: boolean; sectors: boolean | null }; weakest_sector: string | null; weakest_sector_score: string | null };
type GroupPayload = { launch_readiness: Readiness[]; as_of: string | null; previous_as_of: string | null; rank_bands: BandRow[]; sectors: SectorRow[]; band: string; band_metrics: BandMetric[]; history: { date: string; bands: Record<string, string> }[] };

const BANDS = ["top_100", "top_500", "top_1000", "top_1500", "top_2000", "top_3000", "all"];
function bandLabel(key: string) { return key === "all" ? "All companies" : `Top ${Number(key.slice(4)).toLocaleString("en-US")}`; }


function score(value: string | null) { return value === null ? "—" : `${Number(value).toFixed(1)}%`; }
function label(value: string) { return value.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase()); }
function delta(value: string | null) {
  if (value === null) return <Badge>Baseline</Badge>;
  const number = Number(value);
  if (number > 0) return <Badge tone="positive"><ArrowUp size={12} aria-hidden="true" /> {number.toFixed(2)} pp</Badge>;
  if (number < 0) return <Badge tone="negative"><ArrowDown size={12} aria-hidden="true" /> {Math.abs(number).toFixed(2)} pp</Badge>;
  return <Badge><Minus size={12} aria-hidden="true" /> No change</Badge>;
}

export function isCoverageBand(value: string | undefined): value is string { return BANDS.includes(value ?? ""); }

export async function GroupCoverage({ accessToken, band }: { accessToken: string; band: string }) {
  const response = await fetch(backendUrl(`/v1/data-coverage/groups?band=${band}&days=30`), { cache: "no-store", headers: { accept: "application/json", authorization: `Bearer ${accessToken}` } });
  if (!response.ok) return null;
  const groups = await response.json() as GroupPayload;
  if (!groups.as_of) return null;
  return <div className={styles.stack}>
    <Card className={styles.card}>
      <CardHeader><CardHeading><CardTitle>Coverage by company size</CardTitle><CardDescription>Core screening metrics, companies ranked by market cap (revenue where market cap is missing). Every company counts — no exclusions. A group is launch-ready when average coverage is at least 85%, under 10% of companies are below 60%, and no sector in it averages below 60%. Change is versus {groups.previous_as_of ?? "no earlier snapshot"}.</CardDescription></CardHeading></CardHeader>
      <TableContainer aria-label="Coverage by company rank band"><Table><TableHeader><TableRow><TableHead>Group</TableHead><TableHead data-align="right">Companies</TableHead><TableHead data-align="right">Avg coverage</TableHead><TableHead data-align="right">≥ 90% covered</TableHead><TableHead data-align="right">&lt; 60% covered</TableHead><TableHead>Change</TableHead><TableHead>Launch check</TableHead></TableRow></TableHeader><TableBody>{groups.rank_bands.map((row) => { const ready = groups.launch_readiness.find((r) => r.key === row.key); return <TableRow key={row.key}><TableRowHeader>{bandLabel(row.key)}</TableRowHeader><TableCell data-align="right">{row.companies.toLocaleString("en-US")}</TableCell><TableCell data-align="right"><strong>{score(row.score)}</strong></TableCell><TableCell data-align="right">{score(row.pct_ge90)}</TableCell><TableCell data-align="right">{score(row.pct_lt60)}</TableCell><TableCell>{delta(row.delta)}</TableCell><TableCell>{ready ? (ready.ready ? <Badge tone="positive">Ready</Badge> : <Badge tone="negative">Not ready</Badge>) : "—"}{ready && !ready.checks.average && <small> avg &lt; 85%</small>}{ready && !ready.checks.tail && <small> tail ≥ 10%</small>}{ready && ready.checks.sectors === false && <small> {ready.weakest_sector} {score(ready.weakest_sector_score)}</small>}</TableCell></TableRow>; })}</TableBody></Table></TableContainer>
    </Card>

    <Card className={styles.card}>
      <CardHeader><CardHeading><CardTitle>Coverage by sector</CardTitle><CardDescription>Weakest sectors first, measured within the top 1,000; top 2,000 and all-company scores alongside.</CardDescription></CardHeading></CardHeader>
      <TableContainer aria-label="Coverage by sector"><Table><TableHeader><TableRow><TableHead>Sector</TableHead><TableHead data-align="right">Top 1,000</TableHead><TableHead data-align="right">Top 2,000</TableHead><TableHead data-align="right">All</TableHead><TableHead>Change (top 1,000)</TableHead></TableRow></TableHeader><TableBody>{groups.sectors.map((row) => <TableRow key={row.key}><TableRowHeader>{row.key}</TableRowHeader><TableCell data-align="right"><strong>{score(row.score)}</strong> <small>({row.companies.toLocaleString("en-US")})</small></TableCell><TableCell data-align="right">{score(row.score_top2000)} <small>({row.companies_top2000.toLocaleString("en-US")})</small></TableCell><TableCell data-align="right">{score(row.score_all)} <small>({row.companies_all.toLocaleString("en-US")})</small></TableCell><TableCell>{delta(row.delta)}</TableCell></TableRow>)}</TableBody></Table></TableContainer>
    </Card>

    <Card className={styles.card}>
      <CardHeader><CardHeading><CardTitle>Fix first: {bandLabel(groups.band)}</CardTitle><CardDescription>Core metrics ranked by number of companies missing a value in this group — the biggest gaps to close first.</CardDescription></CardHeading></CardHeader>
      <nav className={styles.bandNav} aria-label="Choose company group">{BANDS.map((key) => <a key={key} href={`?band=${key}`} aria-current={key === groups.band ? "true" : undefined}>{bandLabel(key)}</a>)}</nav>
      <TableContainer aria-label="Missing values by metric"><Table><TableHeader><TableRow><TableHead>Metric</TableHead><TableHead data-align="right">Missing</TableHead><TableHead data-align="right">Coverage</TableHead><TableHead>Change</TableHead></TableRow></TableHeader><TableBody>{groups.band_metrics.map((metric) => <TableRow key={metric.metric_name}><TableRowHeader>{label(metric.metric_name)}</TableRowHeader><TableCell data-align="right"><strong>{metric.missing.toLocaleString("en-US")}</strong> of {metric.companies.toLocaleString("en-US")}</TableCell><TableCell data-align="right">{score(metric.coverage_pct)}</TableCell><TableCell>{delta(metric.delta)}</TableCell></TableRow>)}</TableBody></Table></TableContainer>
    </Card>

    <Card className={styles.card}>
      <CardHeader><CardHeading><CardTitle>Group history</CardTitle><CardDescription>Average core coverage per company-size group, one row per daily snapshot.</CardDescription></CardHeading></CardHeader>
      <TableContainer aria-label="Date-wise coverage by company size"><Table><TableHeader><TableRow><TableHead>Date</TableHead>{BANDS.map((key) => <TableHead key={key} data-align="right">{bandLabel(key)}</TableHead>)}</TableRow></TableHeader><TableBody>{groups.history.map((row) => <TableRow key={row.date}><TableRowHeader>{row.date}</TableRowHeader>{BANDS.map((key) => <TableCell key={key} data-align="right">{score(row.bands[key] ?? null)}</TableCell>)}</TableRow>)}</TableBody></Table></TableContainer>
    </Card>
  </div>;
}
