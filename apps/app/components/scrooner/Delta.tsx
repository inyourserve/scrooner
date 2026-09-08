import { ArrowDown, ArrowUp } from "lucide-react";
import type { ReactNode } from "react";

// One reusable up/down indicator so a price change, a chart-period return,
// and a QoQ metric move all render the same way (doc/design/shadcn-system.md
// section 17: one component, one visual language) instead of each screen
// picking its own colored span.
export interface DeltaProps {
  /** Signed value the tone/arrow is derived from -- typically a percent, e.g. 1.24 for +1.24%. */
  value: number | null | undefined;
  /** Renders the signed value; receives the raw signed number, sign included by convention. */
  format?: (value: number) => ReactNode;
  size?: "sm" | "md";
  showIcon?: boolean;
  /** Set for metrics where a decrease reads as favorable (e.g. debt, share dilution). */
  invert?: boolean;
  fallback?: ReactNode;
  className?: string;
}

const defaultFormat = (value: number) => `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;

export function Delta({
  value,
  format = defaultFormat,
  size = "md",
  showIcon = true,
  invert = false,
  fallback = "—",
  className = "",
}: DeltaProps) {
  if (value == null || !Number.isFinite(value)) {
    return <span className={`ds-delta ds-delta--neutral ${className}`.trim()} data-size={size}>{fallback}</span>;
  }
  const positive = invert ? value < 0 : value > 0;
  const negative = invert ? value > 0 : value < 0;
  const tone = positive ? "positive" : negative ? "negative" : "neutral";
  const Icon = value > 0 ? ArrowUp : value < 0 ? ArrowDown : null;

  return (
    <span className={`ds-delta ds-delta--${tone} ${className}`.trim()} data-size={size}>
      {/* Deliberately NOT the app's standard 16/18px icon scale (doc/design/shadcn-system.md
          section 11) -- this arrow is a typographic mark glued to a number, not a UI-chrome
          icon, so it scales with Delta's own font-size (12/14px) the way a glyph would. */}
      {showIcon && Icon && <Icon size={size === "sm" ? 11 : 13} aria-hidden="true" />}
      {format(value)}
    </span>
  );
}
