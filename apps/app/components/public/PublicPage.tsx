import type { ReactNode } from "react";
import { PageHeader } from "@/components/layout/PageHeader";
import { PageShell } from "@/components/layout/PageShell";
import { PublicFooter } from "./PublicFooter";
import { PublicHeader, type Current } from "./PublicHeader";

export function PublicPage({ title, description, eyebrow, current, children }: { title: string; description: string; eyebrow?: string; current?: Current; children: ReactNode }) {
  return <div className="public-site"><PublicHeader current={current} /><PageShell className="public-content" tabIndex={-1}>
    <PageHeader eyebrow={eyebrow} title={title} description={description} tone="editorial" />
    <div className="public-prose">{children}</div>
  </PageShell><PublicFooter /></div>;
}
