import type { HTMLAttributes, ReactNode } from "react";

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: "neutral" | "positive" | "warning" | "negative" | "info";
  children: ReactNode;
};

export function Badge({ tone = "neutral", className = "", children, ...props }: BadgeProps) {
  const toneClass = tone === "neutral" ? "" : `ds-badge--${tone}`;
  return <span data-slot="badge" className={["ds-badge", toneClass, className].filter(Boolean).join(" ")} {...props}>{children}</span>;
}
