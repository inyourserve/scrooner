import type { ReactNode } from "react";

export function ResearchSection({ id, title, description, meta, children, className = "" }: { id: string; title: string; description?: string; meta?: ReactNode; children: ReactNode; className?: string }) {
  return <section className={`ds-section research-section ${className}`} id={id} aria-labelledby={`${id}-title`}><header className="ds-section__header research-section__header"><div><h2 id={`${id}-title`}>{title}</h2>{description && <p>{description}</p>}</div>{meta && <div className="ds-section__meta research-section__meta">{meta}</div>}</header>{children}</section>;
}
