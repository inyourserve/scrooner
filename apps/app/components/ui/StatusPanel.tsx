import type { ReactNode } from "react";

type StatusPanelProps = {
  tone?: "neutral" | "positive" | "warning" | "negative";
  title: string;
  children?: ReactNode;
  action?: ReactNode;
  busy?: boolean;
  live?: "polite" | "assertive" | "off";
  className?: string;
};

export function StatusPanel({
  tone = "neutral",
  title,
  children,
  action,
  busy = false,
  live,
  className = "",
}: StatusPanelProps) {
  const toneClass = tone === "neutral" ? "" : `ds-alert--${tone}`;
  const icon = tone === "negative" ? "!" : tone === "warning" ? "!" : tone === "positive" ? "✓" : "i";
  const role = tone === "negative" ? "alert" : "status";
  const liveMode = live ?? (tone === "negative" ? "assertive" : "polite");

  return (
    <section className={["ds-alert", toneClass, className].filter(Boolean).join(" ")} role={role} aria-live={liveMode} aria-busy={busy || undefined}>
      {busy ? <span className="ds-spinner" aria-hidden="true" /> : <span className={`ds-alert__mark ds-alert__mark--${tone}`} aria-hidden="true">{icon}</span>}
      <div>
        <strong>{title}</strong>
        {children}
        {action}
      </div>
    </section>
  );
}
