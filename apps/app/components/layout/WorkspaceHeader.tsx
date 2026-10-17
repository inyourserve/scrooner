import type { ReactNode } from "react";
import { PageHeader } from "@/components/layout/PageHeader";

type WorkspaceHeaderProps = {
  eyebrow?: string;
  title: string;
  description: string;
  actions?: ReactNode;
  trustItems?: string[];
};

export function WorkspaceHeader({ eyebrow, title, description, actions, trustItems }: WorkspaceHeaderProps) {
  return <div className="workspace-page-header">
    <PageHeader eyebrow={eyebrow} title={title} description={description} trustItems={trustItems} />
    {actions && <div className="workspace-page-header__actions">{actions}</div>}
  </div>;
}
