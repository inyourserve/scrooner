import type { ReactNode } from "react";
import { PublicFooter } from "./PublicFooter";
import { PublicHeader, type Current } from "./PublicHeader";

export function PublicPage({ title, description, eyebrow, current, wide = false, children }: { title: string; description: string; eyebrow?: string; current?: Current; wide?: boolean; children: ReactNode }) {
  return <div className="public-site"><PublicHeader current={current} /><main className={`ds-page${wide ? " ds-page--wide" : ""} public-content`} id="main-content" tabIndex={-1}>
    <header className="ds-page__hero">{eyebrow && <p className="public-eyebrow">{eyebrow}</p>}<h1 className="ds-page__title">{title}</h1><p className="ds-page__lede">{description}</p></header>
    <div className="public-prose">{children}</div>
  </main><PublicFooter /></div>;
}
