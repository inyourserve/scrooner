import type { ReactNode } from "react";

// The one canonical empty state (doc/design/shadcn-system.md section 16) --
// replaces three independently-invented patterns that had drifted apart
// (a bordered box with no icon, a screener-only variant with an icon mark,
// and a third, defined-but-never-used primitive). `bordered` covers a
// standalone context (a table, a chart, a page section) that needs its own
// visual boundary; set it false when the empty state already sits inside a
// bordered container (e.g. the screener's results section).
export function EmptyState({
  icon,
  title,
  description,
  action,
  bordered = true,
}: {
  icon?: ReactNode;
  title?: string;
  description: ReactNode;
  action?: ReactNode;
  bordered?: boolean;
}) {
  return (
    <div className={`ds-empty-state${bordered ? " ds-empty-state--bordered" : ""}`}>
      <div>
        {icon && <span className="ds-empty-state__mark" aria-hidden="true">{icon}</span>}
        {title && <h3>{title}</h3>}
        <p>{description}</p>
        {action}
      </div>
    </div>
  );
}
