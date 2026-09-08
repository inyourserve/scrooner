// A single reusable ticker chip -- see doc/design/shadcn-system.md section 16.
// Kept intentionally plain (mono, bordered, uppercase) rather than a colored
// "brand" pill, matching the doc's "precise rather than playful" direction.
export function TickerBadge({
  ticker,
  exchange,
  size = "md",
}: {
  ticker: string;
  exchange?: string | null;
  size?: "sm" | "md";
}) {
  return (
    <span className="ds-ticker-badge" data-size={size}>
      {ticker}
      {exchange && <span className="ds-ticker-badge__exchange">{exchange}</span>}
    </span>
  );
}
