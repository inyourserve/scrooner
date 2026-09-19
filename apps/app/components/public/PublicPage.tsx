import type { ReactNode } from "react";
import { PublicFooter } from "./PublicFooter";
import { PublicHeader, type Current } from "./PublicHeader";

export function PublicPage({ title, description, eyebrow, current, children }: { title: string; description: string; eyebrow?: string; current?: Current; children: ReactNode }) {
  return <div className="public-site"><PublicHeader current={current} /><main className="public-content" id="main-content" tabIndex={-1}>
    <header className="public-content-hero">{eyebrow && <p className="public-eyebrow">{eyebrow}</p>}<h1>{title}</h1><p className="public-lede">{description}</p></header>
    <div className="public-prose">{children}</div>
  </main><PublicFooter /></div>;
}
