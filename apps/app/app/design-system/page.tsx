import type { Metadata } from "next";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { PublicPage } from "@/components/public/PublicPage";
import { Delta } from "@/components/scrooner/Delta";
import { TickerBadge } from "@/components/scrooner/TickerBadge";

export const metadata: Metadata = { title: "Design system — Scrooner", robots: { index: false } };
export default function DesignSystemPage() {
  return (
    <PublicPage title="One visual language for every Scrooner surface" description="Owned shadcn components, Scrooner tokens, and research-first composition patterns.">
      <section>
        <h2>Brand and color</h2>
        {/* Revised per doc/design/shadcn-system.md section 7: navy is the
            action/link/focus color, teal is reserved for positive financial
            values. They used to be the same hue -- a primary button and a
            stock gain were, by accident, the exact same color. */}
        <p>Navy is reserved for actions, links, and focus states. Teal/red communicate positive/negative values only, so a primary button is never visually indistinguishable from a stock gain.</p>
      </section>
      <section>
        <h2>Components</h2>
        <div className="ds-stack">
          <div><Button>Primary action</Button> <Button variant="secondary">Secondary action</Button> <Button variant="ghost">Quiet action</Button></div>
          <div><Badge>Default</Badge> <Badge tone="positive">Available</Badge> <Badge tone="warning">Review</Badge></div>
          <div><TickerBadge ticker="AAPL" exchange="NASDAQ" /> <TickerBadge ticker="JPM" size="sm" /></div>
          <div><Delta value={1.24} /> <Delta value={-2.87} /> <Delta value={null} /> <Delta value={0.4} invert format={(v) => `${v > 0 ? "+" : ""}${v.toFixed(1)}% debt`} /></div>
        </div>
      </section>
      <section>
        <h2>Research surfaces</h2>
        <p>Tables carry comparable data. Ledgers carry compact metrics. Cards are reserved for meaningful grouping rather than decorating every section.</p>
      </section>
    </PublicPage>
  );
}
