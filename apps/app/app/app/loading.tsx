import { Skeleton } from "@/components/ui/Skeleton";

export default function AppLoading() {
  return <main className="main-content workspace-content" id="main-content" aria-busy="true" aria-label="Loading workspace">
    <div className="workspace-loading">
      <Skeleton className="workspace-loading__eyebrow" />
      <Skeleton className="workspace-loading__title" />
      <Skeleton className="workspace-loading__copy" />
      <Skeleton className="workspace-loading__panel" />
    </div>
  </main>;
}
