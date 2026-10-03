import { HelpCircle } from "lucide-react";
import { useId, type ReactNode } from "react";

export function Tooltip({ label, children, side = "top", align = "center" }: {
  label: string;
  children: ReactNode;
  side?: "top" | "bottom";
  align?: "start" | "center" | "end";
}) {
  const id = useId();
  return (
    <span className="ds-tooltip" data-slot="tooltip" data-side={side} data-align={align}>
      <button
        className="ds-tooltip__trigger"
        type="button"
        aria-label={`About ${label}`}
        aria-describedby={id}
      >
        <HelpCircle aria-hidden="true" size={15} strokeWidth={1.8} />
      </button>
      <span className="ds-tooltip__content" id={id} role="tooltip">{children}</span>
    </span>
  );
}
