type BrandMarkProps = {
  size?: "small" | "medium" | "large";
  className?: string;
};

export function BrandMark({ size = "medium", className = "" }: BrandMarkProps) {
  const sizeClass = size === "medium" ? "" : `ds-brand-mark--${size}`;
  return (
    <svg
      className={["ds-brand-mark", sizeClass, className].filter(Boolean).join(" ")}
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden="true"
    >
      <path className="ds-brand-mark__frame" d="M13 4H10a6 6 0 0 0-6 6v5m15-11h3a6 6 0 0 1 6 6v5M4 19v3a6 6 0 0 0 6 6h3m15-9v3a6 6 0 0 1-6 6h-3" />
      <path className="ds-brand-mark__scan" d="M9 16h14" />
      <circle className="ds-brand-mark__point" cx="16" cy="16" r="3.25" />
    </svg>
  );
}
