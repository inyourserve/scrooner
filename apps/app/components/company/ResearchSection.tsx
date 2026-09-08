import type { ReactNode } from "react";

export function ResearchSection({ id, title, description, meta, children, className = "" }: { id: string; title: string; description?: string; meta?: ReactNode; children: ReactNode; className?: string }) {
  return <section className={`research-section ${className}`} id={id} aria-labelledby={`${id}-title`}><header className="research-section__header"><div><h2 id={`${id}-title`}>{title}</h2>{description && <p>{description}</p>}</div>{meta && <div className="research-section__meta">{meta}</div>}</header>{children}</section>;
}
