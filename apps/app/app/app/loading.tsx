import { Skeleton } from "@/components/ui/Skeleton";
import { PageShell } from "@/components/layout/PageShell";

export default function AppLoading() {
  return <PageShell aria-busy="true" aria-label="Loading workspace">
    <div className="workspace-loading">
      <Skeleton className="workspace-loading__eyebrow" />
      <Skeleton className="workspace-loading__title" />
      <Skeleton className="workspace-loading__copy" />
      <Skeleton className="workspace-loading__panel" />
    </div>
  </PageShell>;
}
