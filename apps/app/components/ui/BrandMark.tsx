type BrandMarkProps = {
  size?: "small" | "medium" | "large";
  className?: string;
};

// The one canonical Scrooner mark (an upward trend line with an arrowhead
// corner) -- every surface (public site, app shell, auth pages) renders
// this exact component so the brand can never silently diverge again.
export function BrandMark({ size = "medium", className = "" }: BrandMarkProps) {
  const sizeClass = size === "medium" ? "" : `ds-brand-mark--${size}`;
  return (
    <svg
      className={["ds-brand-mark", sizeClass, className].filter(Boolean).join(" ")}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path className="ds-brand-mark__line" d="M4 17.5 9.2 12l3.2 3.1L20 7" />
      <path className="ds-brand-mark__arrow" d="M16 7h4v4" />
    </svg>
  );
}
