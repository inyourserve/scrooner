import Link from "next/link";
import { ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Delta } from "./Delta";
import { TickerBadge } from "./TickerBadge";

// doc/design/shadcn-system.md section 8: "the stock header should become a
// signature component ... every company gets exactly the same hierarchy."
// Extracted from app/stocks/[ticker]/page.tsx so that guarantee holds by
// construction (one component, one call site's worth of markup) rather than
// by convention across a page every company re-renders independently.
export interface StockHeaderPrice {
  value: number;
  /** Pre-formatted "as of" timestamp, already in the exchange's local time. */
  asOfLabel: string;
}

export interface StockHeaderProps {
  ticker: string | null;
  companyName: string;
  sector: string | null;
  status: string;
  price: StockHeaderPrice | null;
  /** Signed percent change vs. the prior verified close, e.g. 1.24 for +1.24%. Null when there's no prior close to compare against. */
  dayChangePct: number | null;
  dayChangeAbs: number | null;
  website?: string | null;
}

export function StockHeader({ ticker, companyName, sector, status, price, dayChangePct, dayChangeAbs, website }: StockHeaderProps) {
  return (
    <div className="stock-hero__identity">
      <div className="stock-hero__title-row">
        <div>
          <p className="stock-hero__ticker">{ticker ?? "—"} · {sector ?? "Sector unclassified"}</p>
          <h1 id="company-name"><TickerBadge ticker={ticker ?? "—"} size="sm" /> {companyName}</h1>
        </div>
        <Badge tone={status === "active" ? "positive" : "neutral"}>{status}</Badge>
      </div>
      <div className="stock-hero__price">
        {price ? (
          <>
            <strong>${price.value.toFixed(2)}</strong>
            <Delta
              value={dayChangePct}
              format={(v) => `${dayChangeAbs! >= 0 ? "+" : ""}$${Math.abs(dayChangeAbs!).toFixed(2)} (${v >= 0 ? "+" : ""}${v.toFixed(2)}%) today`}
            />
            <span className="stock-hero__price-caption">Delayed market data · {price.asOfLabel} ET</span>
          </>
        ) : (
          <>
            <strong>—</strong>
            <span className="stock-hero__price-caption">No verified market price on record</span>
          </>
        )}
      </div>
      <div className="stock-hero__actions">
        <Button asChild size="small"><Link href="/app/screens/new">Compare in screener</Link></Button>
        {website && (
          <Button asChild size="small" variant="secondary" trailingIcon={<ExternalLink size={16} aria-hidden="true" />}>
            <a href={`https://${website}`} target="_blank" rel="nofollow noopener">Official website</a>
          </Button>
        )}
      </div>
    </div>
  );
}
