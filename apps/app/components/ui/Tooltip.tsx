import { HelpCircle } from "lucide-react";
import { useId, type ReactNode } from "react";

export function Tooltip({ label, children }: { label: string; children: ReactNode }) {
  const id = useId();
  return <span className="ui-tooltip"><button className="ui-tooltip__trigger" type="button" aria-label={`About ${label}`} aria-describedby={id}><HelpCircle aria-hidden="true" size={16} /></button><span className="ui-tooltip__content" id={id} role="tooltip">{children}</span></span>;
}
